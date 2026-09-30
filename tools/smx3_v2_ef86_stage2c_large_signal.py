#!/usr/bin/env python3
"""Out-of-fit large-signal probe for the EF86 Stage-2C candidate.

Tests:
- exact Philips Vo @ 5% THD envelope, Vb=200..400 V;
- provisional Philips Graph-D compression/distortion trajectory at 250 V.

Stage-2C was NOT fit to these data.

Standard library only.
"""

import csv
import math
import pathlib

ROOT=pathlib.Path(__file__).resolve().parents[1]
GRAPHD=ROOT/"research"/"ef86_philips1956_graphD_provisional.csv"

BASE={
    "MU":42.1294068459,
    "EX":1.48016674106,
    "KG1":2059.06189749,
    "KP":215.816749098,
    "VCT":0.761562843483,
    "KVB_SCREEN":430.818432714,
    "LAMBDA":0.000160501489918,
}
KNEE=3.35311366202
S0=9.02342723159e-5

RA=100000.0
RG2=390000.0
RK=1000.0
RGLOAD=330000.0

VO5={
    200.0:40.0,
    250.0:50.0,
    300.0:64.0,
    350.0:75.0,
    400.0:87.0,
}


def l1p(x):
    if x>50.0:return x
    if x<-50.0:return math.exp(x)
    return math.log1p(math.exp(x))


def activation(vg2,vg1):
    if vg2<=0.0:return 0.0
    b=BASE
    denom=math.sqrt(b["KVB_SCREEN"]+vg2*vg2)
    z=(1.0/b["MU"]+(b["VCT"]+vg1)/denom)*b["KP"]
    e1=vg2/b["KP"]*l1p(z)
    return 2.0*max(e1,0.0)**b["EX"]


def knorm(va):
    if va<=0.0:return 0.0
    return math.atan(va/KNEE)/math.atan(250.0/KNEE)


def ia(va,vg2,vg1):
    b=BASE
    slope=max(0.1,1.0+b["LAMBDA"]*(va-250.0))
    return max(0.0,activation(vg2,vg1)/b["KG1"]*slope*knorm(va))


def ig2(va,vg2,vg1):
    return activation(vg2,vg1)*S0


def solve_dc(vb):
    vp=.35*vb; vs=.50*vb; vk=2.0
    for _ in range(50000):
        a=ia(vp-vk,vs-vk,-vk)
        s=ig2(vp-vk,vs-vk,-vk)
        tvp=vb-a*RA
        tvs=vb-s*RG2
        tvk=(a+s)*RK
        if max(abs(tvp-vp),abs(tvs-vs),abs(tvk-vk))<1e-11:
            return vp,vs,vk,a,s
        d=.08
        vp=(1-d)*vp+d*tvp
        vs=(1-d)*vs+d*tvs
        vk=(1-d)*vk+d*tvk
    raise RuntimeError("DC solve failed")


def waveform(vb,vin_rms,n=1024):
    dc=solve_dc(vb)
    vp0,vs,vk,ia0,_=dc
    rload=1.0/(1.0/RA+1.0/RGLOAD)
    vth=vp0+ia0*rload

    ys=[]
    for i in range(n):
        vin=vin_rms*math.sqrt(2.0)*math.sin(2.0*math.pi*i/n)
        x=vp0
        for _ in range(20000):
            cur=ia(x-vk,vs-vk,vin-vk)
            target=vth-cur*rload
            if abs(target-x)<1e-11:
                break
            x=.80*x+.20*target
        ys.append(x)

    mean=sum(ys)/n
    ys=[y-mean for y in ys]
    out=math.sqrt(sum(y*y for y in ys)/n)

    amps=[]
    for h in range(1,11):
        re=sum(y*math.cos(2.0*math.pi*h*i/n) for i,y in enumerate(ys))
        im=-sum(y*math.sin(2.0*math.pi*h*i/n) for i,y in enumerate(ys))
        amps.append(2.0*math.hypot(re,im)/n)

    thd=100.0*math.sqrt(sum(a*a for a in amps[1:]))/amps[0]
    return out,thd


def find_for_thd(vb,target=5.0):
    lo=0.0; hi=2.0
    for _ in range(45):
        mid=.5*(lo+hi)
        _,d=waveform(vb,mid,512)
        if d<target:lo=mid
        else:hi=mid
    vin=.5*(lo+hi)
    out,d=waveform(vb,vin,2048)
    return vin,out,d


def solve_input_for_output(target):
    lo=0.0; hi=1.0
    while waveform(250.0,hi,512)[0]<target and hi<3.0:
        hi*=1.5

    for _ in range(42):
        mid=.5*(lo+hi)
        out,_=waveform(250.0,mid,512)
        if out<target:lo=mid
        else:hi=mid

    vin=.5*(lo+hi)
    out,d=waveform(250.0,vin,2048)
    return vin,out,d


def main():
    print("SMX-3 V2 EF86 Stage-2C out-of-fit large-signal probe")
    print()

    print("EXACT PHILIPS 5%-THD ENVELOPE")
    print("Vb,Vin_5pct,Vo_model,Vo_target,error_pct")
    errors=[]
    for vb in sorted(VO5):
        vin,out,d=find_for_thd(vb)
        target=VO5[vb]
        err=100.0*(out-target)/target
        errors.append(err)
        print(f"{vb:.0f},{vin:.9f},{out:.9f},{target:.9f},{err:+.6f}")

    print(f"worst |Vo5 error|={max(abs(e) for e in errors):.6f}%")
    print()

    rows=list(csv.DictReader(GRAPHD.open(encoding="utf-8")))
    vi_sig=[]
    d_sig=[]

    print("PROVISIONAL PHILIPS GRAPH-D SHAPE")
    print("Vo,Vi_model_mV,Vi_ref_mV,Vi_sigma,THD_model,THD_ref,THD_sigma")
    for r in rows:
        vo=float(r["output_vrms"])
        vi_ref=float(r["input_mvrms"])
        d_ref=float(r["distortion_percent"])
        uvi=float(r["input_uncertainty_mV"])
        ud=float(r["distortion_uncertainty_pct"])

        vin,out,d=solve_input_for_output(vo)
        vi_mv=vin*1000.0
        sv=(vi_mv-vi_ref)/uvi
        sd=(d-d_ref)/ud
        vi_sig.append(sv)
        d_sig.append(sd)

        print(f"{vo:.1f},{vi_mv:.6f},{vi_ref:.6f},{sv:+.3f},{d:.6f},{d_ref:.6f},{sd:+.3f}")

    vi_nrms=math.sqrt(sum(x*x for x in vi_sig)/len(vi_sig))
    d_nrms=math.sqrt(sum(x*x for x in d_sig)/len(d_sig))

    print()
    print(f"Graph-D Vi NRMS={vi_nrms:.6f} sigma")
    print(f"Graph-D distortion NRMS={d_nrms:.6f} sigma")
    print("INFO: these data were NOT part of Stage-2C fitting.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
