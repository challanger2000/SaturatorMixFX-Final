#!/usr/bin/env python3
"""EF86 large-signal/kink sensitivity matrix for SMX-3 V2.

Purpose:
identify which extended-family kink parameters actually move the Philips
large-signal envelope, and how much collateral damage they cause to static
manufacturer surfaces.

This is an INFORMATIONAL screening tool, not a fitter.
"""

import csv, math, pathlib

ROOT=pathlib.Path(__file__).resolve().parents[1]
GA=ROOT/"research"/"ef86_philips_graphA_provisional.csv"
GB=ROOT/"research"/"ef86_philips1956_platecurve_provisional.csv"
GBK=ROOT/"research"/"ef86_philips1956_platecurve_knee_provisional.csv"

RA=100000.0; RG2=390000.0; RK=1000.0; RGLOAD=330000.0

BASE={
 "MU":44.70894,"KG1":1208.50779,"KP":238.26123,"KVB":63.64558,
 "VCT":-0.03071,"EX":0.96428,"KG2":77294.8,
 "KNEE":11.97187,"KVC":20.63642,"KLAM":0.0,"KLAMG":1.21e-5,
 "KNEE2":32.21346,
 # neutral/default large-signal block:
 "KNEX":0.0,"KNK":0.0,"KNG":0.0,
 "KNPL":0.10,"KNSL":25.0,"KNPR":9.0,"KNSR":1600.0,
}

PHILIPS={250.0:50.0,400.0:87.0}


def l1p(x):
    if x>50.0:return x
    if x<-50.0:return math.exp(x)
    return math.log1p(math.exp(x))


def clamp(v,lo,hi):
    return lo if v<lo else hi if v>hi else v


def currents(p,vp,vg2,vg):
    z=(1.0/p["MU"]+(p["VCT"]+vg)/math.sqrt(p["KVB"]+vg2*vg2))*p["KP"]
    e1=vg2/p["KP"]*l1p(z)
    e2=2.0*max(e1,0.0)**p["EX"]

    knee=math.atan((vp+p["KNEX"])/p["KNEE"])*math.tanh(vp/p["KNEE2"])
    base=e2/p["KG1"]*knee

    kink_shape=(
        -math.atan((vp-p["KNPL"])/p["KNSL"])
        +math.atan((vp-p["KNPR"])/p["KNSR"])
    )
    kink=base*clamp(p["KNK"]-vg*p["KNG"],0.0,0.3)*kink_shape

    ia=base*(1.0+p["KLAMG"]*vp)+p["KLAM"]*vp+kink
    ig2=e2/p["KG2"]*(p["KVC"]-knee)/(1.0+p["KLAMG"]*vp)-kink
    return max(ia,0.0),max(ig2,0.0)


def solve_dc(p,vb):
    vp=.3*vb;vs=.45*vb;vk=2.0
    for _ in range(30000):
        ia,ig2=currents(p,vp-vk,vs-vk,-vk)
        a=vb-ia*RA;s=vb-ig2*RG2;k=(ia+ig2)*RK
        if max(abs(a-vp),abs(s-vs),abs(k-vk))<1e-10:
            return vp,vs,vk,ia,ig2
        d=.05
        vp=(1-d)*vp+d*a;vs=(1-d)*vs+d*s;vk=(1-d)*vk+d*k
    raise RuntimeError("DC solve failed")


def graph_score(p,path,graph_a=False):
    rows=list(csv.DictReader(path.open(encoding="utf-8")))
    sig=[]
    for r in rows:
        if graph_a:
            vp=250.0;vg2=float(r["vg2_v"]);vg=float(r["vg1_v"])
        else:
            vp=float(r["va_v"]);vg2=140.0;vg=float(r["curve_vg1_v"])
        ref=float(r["ia_ma"]);u=float(r["uncertainty_ma"])
        m=1e3*currents(p,vp,vg2,vg)[0]
        sig.append((m-ref)/u)
    return math.sqrt(sum(x*x for x in sig)/len(sig))


def waveform(p,vb,vin_rms,n=192):
    dc=solve_dc(p,vb)
    vp,vs,vk,ia0,_=dc
    r=1.0/(1.0/RA+1.0/RGLOAD)
    vth=vp+ia0*r
    ys=[]

    for i in range(n):
        vin=vin_rms*math.sqrt(2.0)*math.sin(2.0*math.pi*i/n)
        x=vp
        for _ in range(4000):
            ia,_=currents(p,x-vk,vs-vk,vin-vk)
            t=vth-ia*r
            if abs(t-x)<1e-9:break
            x=.75*x+.25*t
        ys.append(x)

    mean=sum(ys)/n
    ys=[y-mean for y in ys]
    rms=math.sqrt(sum(y*y for y in ys)/n)
    amps=[]
    for h in range(1,8):
        re=sum(y*math.cos(2.0*math.pi*h*i/n) for i,y in enumerate(ys))
        im=-sum(y*math.sin(2.0*math.pi*h*i/n) for i,y in enumerate(ys))
        amps.append(2.0*math.hypot(re,im)/n)
    thd=100.0*math.sqrt(sum(a*a for a in amps[1:]))/amps[0]
    return rms,thd


def vo5(p,vb):
    lo=0.0;hi=2.5
    _,dhi=waveform(p,vb,hi,128)
    if dhi<5.0:return None
    for _ in range(28):
        mid=.5*(lo+hi)
        _,d=waveform(p,vb,mid,128)
        if d<5.0:lo=mid
        else:hi=mid
    vo,_=waveform(p,vb,.5*(lo+hi),384)
    return vo


def summarize(label,p):
    ga=graph_score(p,GA,True)
    gb=graph_score(p,GB,False)
    gbk=graph_score(p,GBK,False)
    v250=vo5(p,250.0)
    v400=vo5(p,400.0)
    e250=None if v250 is None else 100.0*(v250-50.0)/50.0
    e400=None if v400 is None else 100.0*(v400-87.0)/87.0
    print(
        f"{label},"
        f"{ga:.4f},{gb:.4f},{gbk:.4f},"
        f"{v250 if v250 is not None else float('nan'):.4f},"
        f"{e250 if e250 is not None else float('nan'):+.3f},"
        f"{v400 if v400 is not None else float('nan'):.4f},"
        f"{e400 if e400 is not None else float('nan'):+.3f}"
    )


def main():
    print("SMX-3 V2 EF86 kink-parameter sensitivity matrix")
    print("label,GraphA_NRMS,GraphB_plateau_NRMS,GraphB_knee_NRMS,Vo5_250,err250_pct,Vo5_400,err400_pct")

    summarize("baseline",BASE)

    cases=[
        ("KNEX+20",{"KNEX":20.0}),
        ("KNEX+40",{"KNEX":40.0}),
        ("KNK=.01",{"KNK":0.01}),
        ("KNK=.03",{"KNK":0.03}),
        ("KNK=.05",{"KNK":0.05}),
        ("KNG=.002",{"KNK":0.03,"KNG":0.002}),
        ("KNG=.005",{"KNK":0.03,"KNG":0.005}),
        ("KNSL=10",{"KNK":0.03,"KNSL":10.0}),
        ("KNSL=60",{"KNK":0.03,"KNSL":60.0}),
        ("KNPR=30",{"KNK":0.03,"KNPR":30.0}),
        ("KNSR=400",{"KNK":0.03,"KNSR":400.0}),
        ("KNSR=3000",{"KNK":0.03,"KNSR":3000.0}),
    ]

    for label,delta in cases:
        p=BASE.copy();p.update(delta)
        summarize(label,p)

    print()
    print("INFO: select only parameters that materially improve the exact envelope without large Graph-A/B collateral damage.")


if __name__=="__main__":
    raise SystemExit(main())
