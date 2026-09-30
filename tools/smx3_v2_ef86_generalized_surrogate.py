#!/usr/bin/env python3
"""Generalized EF86 realtime-surrogate candidate for SMX-3 V2 research.

This candidate extends the compact Koren-style pentode plate-current term with
an empirical knee exponent beta:

Ia = E1^EX / KG1 * atan(Va/KVB)^beta

beta is NOT a physical tube parameter. It is an EMPIRICALLY TUNED surrogate
degree of freedom whose only justification is measured agreement with the
Philips EF86 reference data.

The script validates:
- device Ia / Ig2 / gm;
- Philips-1956 circuit-1 Ik and gain over Vb=200..400 V;
- exact 250 V large-signal anchor (~50 Vrms at 5% THD);
- coarse out-of-fit Philips plate-curve CSV.

Standard library only.
"""

import csv, math, pathlib

P={
    "MU":36.8954959669,
    "EX":1.31035546622,
    "KG1":1371.04200483,
    "KG2":3539.16926088,
    "KP":186.980461845,
    "KVB":1.97512311531,
    "BETA":1.32747494602,
}

RA=100000.0
RG2=390000.0
RK=1000.0
RGLOAD=330000.0

DEVICE={"ia":0.0030,"ig2":0.0006,"gm":0.0020}
SWEEP={
    400.0:(0.00330,124.0),
    350.0:(0.00290,120.0),
    300.0:(0.00250,116.0),
    250.0:(0.00210,112.0),
    200.0:(0.00170,106.0),
}


def l1p(x):
    if x>50:return x
    if x<-50:return math.exp(x)
    return math.log1p(math.exp(x))


def currents(vp,vg2,vg1):
    if vg2<=1e-12 or vp<=0.0:return 0.0,0.0
    z=P["KP"]*(1.0/P["MU"]+vg1/vg2)
    e=(vg2/P["KP"])*l1p(z)
    ia=max(e,0.0)**P["EX"]/P["KG1"] * math.atan(vp/P["KVB"])**P["BETA"]
    ig2=max(vg2/P["MU"]+vg1,0.0)**P["EX"]/P["KG2"]
    return ia,ig2


def solve_dc(vb):
    vp=0.3*vb; vs=0.45*vb; vk=2.0
    for _ in range(30000):
        ia,ig2=currents(vp-vk,vs-vk,-vk)
        a=vb-ia*RA; s=vb-ig2*RG2; k=(ia+ig2)*RK
        if max(abs(a-vp),abs(s-vs),abs(k-vk))<1e-12:
            return vp,vs,vk,ia,ig2
        d=0.08
        vp=(1-d)*vp+d*a; vs=(1-d)*vs+d*s; vk=(1-d)*vk+d*k
    raise RuntimeError("DC solve failed")


def small_gain(dc):
    vp,vs,vk,ia0,_=dc
    rload=1.0/(1.0/RA+1.0/RGLOAD)
    vth=vp+ia0*rload

    def solve(vin):
        x=vp
        for _ in range(10000):
            ia,_=currents(x-vk,vs-vk,vin-vk)
            target=vth-ia*rload
            if abs(target-x)<1e-12:return x
            x=0.75*x+0.25*target
        raise RuntimeError("AC solve failed")

    dv=1e-5
    return (solve(dv)-solve(-dv))/(2.0*dv)


def waveform(vin_rms,n=2048):
    dc=solve_dc(250.0)
    vp0,vs,vk,ia0,_=dc
    rload=1.0/(1.0/RA+1.0/RGLOAD)
    vth=vp0+ia0*rload
    ys=[]

    for i in range(n):
        vin=vin_rms*math.sqrt(2.0)*math.sin(2.0*math.pi*i/n)
        x=vp0
        for _ in range(10000):
            ia,_=currents(x-vk,vs-vk,vin-vk)
            target=vth-ia*rload
            if abs(target-x)<1e-11:break
            x=0.75*x+0.25*target
        ys.append(x)

    mean=sum(ys)/n
    ys=[y-mean for y in ys]
    out_rms=math.sqrt(sum(y*y for y in ys)/n)

    amps=[]
    for h in range(1,11):
        re=sum(y*math.cos(2.0*math.pi*h*i/n) for i,y in enumerate(ys))
        im=-sum(y*math.sin(2.0*math.pi*h*i/n) for i,y in enumerate(ys))
        amps.append(2.0*math.hypot(re,im)/n)
    thd=100.0*math.sqrt(sum(a*a for a in amps[1:]))/amps[0]
    return out_rms,thd


def find_5pct():
    lo=0.0; hi=0.7
    for _ in range(55):
        mid=(lo+hi)*0.5
        _,d=waveform(mid,768)
        if d<5.0:lo=mid
        else:hi=mid
    vi=(lo+hi)*0.5
    vo,d=waveform(vi,4096)
    return vi,vo,d


def pct(v,r):return 100.0*(v-r)/r


def main():
    ia,ig2=currents(250.0,140.0,-2.0)
    dv=1e-4
    gm=(currents(250.0,140.0,-2.0+dv)[0]-currents(250.0,140.0,-2.0-dv)[0])/(2.0*dv)

    print("SMX-3 V2 generalized EF86 surrogate")
    print(f"Ia={ia*1e3:.6f} mA error={pct(ia,DEVICE['ia']):+.3f}%")
    print(f"Ig2={ig2*1e3:.6f} mA error={pct(ig2,DEVICE['ig2']):+.3f}%")
    print(f"gm={gm*1e3:.6f} mA/V error={pct(gm,DEVICE['gm']):+.3f}%")

    max_i=max_g=0.0
    print("Vb,Ik_mA,Ik_err_pct,Gain,Gain_err_pct")
    for vb in sorted(SWEEP,reverse=True):
        dc=solve_dc(vb)
        ik=dc[3]+dc[4]
        g=abs(small_gain(dc))
        ei=pct(ik,SWEEP[vb][0]); eg=pct(g,SWEEP[vb][1])
        max_i=max(max_i,abs(ei)); max_g=max(max_g,abs(eg))
        print(f"{vb:.0f},{ik*1e3:.6f},{ei:+.3f},{g:.6f},{eg:+.3f}")

    vi,vo,d=find_5pct()
    print(f"5pct input={vi:.9f} Vrms output={vo:.9f} Vrms THD={d:.9f}%")
    print(f"5pct output error={pct(vo,50.0):+.3f}%")

    path=pathlib.Path(__file__).resolve().parents[1]/"research"/"ef86_philips1956_platecurve_provisional.csv"
    rows=list(csv.DictReader(path.open(encoding="utf-8")))
    ss=0.0; worst=0.0
    for r in rows:
        vg=float(r["curve_vg1_v"]); va=float(r["va_v"])
        y=float(r["ia_ma"]); u=float(r["uncertainty_ma"])
        m=currents(va,140.0,vg)[0]*1e3
        sig=(m-y)/u
        ss+=sig*sig; worst=max(worst,abs(sig))
    nrms=math.sqrt(ss/len(rows))
    print(f"plate-curve normalized RMS={nrms:.3f} sigma, worst={worst:.3f} sigma")

    if abs(pct(ia,DEVICE["ia"]))>3.0:raise SystemExit("FAIL Ia")
    if abs(pct(ig2,DEVICE["ig2"]))>3.0:raise SystemExit("FAIL Ig2")
    if abs(pct(gm,DEVICE["gm"]))>5.0:raise SystemExit("FAIL gm")
    if max_i>6.0:raise SystemExit("FAIL current sweep")
    if max_g>5.0:raise SystemExit("FAIL gain sweep")
    if abs(pct(vo,50.0))>3.0:raise SystemExit("FAIL large-signal output")
    if nrms>1.0:raise SystemExit("FAIL coarse plate curves")

    print("PASS: generalized surrogate clears current provisional multi-domain gates.")
    print("WARNING: beta is an empirical surrogate term; calibrated curve extraction remains required.")


if __name__=="__main__":
    main()
