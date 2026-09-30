#!/usr/bin/env python3
"""EF86 Stage-3 control-grid curvature scan.

Reopens ONLY the plate-current exponent EX.

For every EX candidate, derive:
- VCT so gm/Ia at the Philips device point is exactly 2/3 per volt;
- KG1 so Ia is exactly 3.0 mA;
- S0 so Ig2 is exactly 0.6 mA.

Thus every candidate has the SAME local device point. The comparison tests
global curvature, not level/gain cheating.

Stage-2C plate knee stays fixed initially.

Evaluate:
- provisional Graph A/B;
- exact amplifier Ik/gain table;
- exact Vo@5% THD envelope.

Standard library only.
"""

import csv
import math
import pathlib

ROOT=pathlib.Path(__file__).resolve().parents[1]
GRAPHA=ROOT/"research"/"ef86_philips_graphA_provisional.csv"
GRAPHB=ROOT/"research"/"ef86_philips1956_platecurve_provisional.csv"

MU=42.1294068459
KP=215.816749098
KVB_SCREEN=430.818432714
LAMBDA=0.000160501489918
KNEE=3.35311366202

RA=100000.0
RG2=390000.0
RK=1000.0
RGLOAD=330000.0

TARGET_IA=0.0030
TARGET_GM=0.0020
TARGET_IG2=0.0006

AMP={
    200.0:{"ik":0.00170,"gain":106.0,"vo5":40.0},
    250.0:{"ik":0.00210,"gain":112.0,"vo5":50.0},
    300.0:{"ik":0.00250,"gain":116.0,"vo5":64.0},
    350.0:{"ik":0.00290,"gain":120.0,"vo5":75.0},
    400.0:{"ik":0.00330,"gain":124.0,"vo5":87.0},
}

EX_VALUES=(1.20,1.25,1.30,1.35,1.40,1.45,1.48,1.50,1.55,1.60)

A_POINTS=list(csv.DictReader(GRAPHA.open(encoding="utf-8")))
B_POINTS=list(csv.DictReader(GRAPHB.open(encoding="utf-8")))


def l1p(x):
    if x>50.0:return x
    if x<-50.0:return math.exp(x)
    return math.log1p(math.exp(x))


def e1(vg2,vg1,vct):
    den=math.sqrt(KVB_SCREEN+vg2*vg2)
    z=(1.0/MU+(vct+vg1)/den)*KP
    return vg2/KP*l1p(z)


def activation(vg2,vg1,ex,vct):
    return 2.0*max(e1(vg2,vg1,vct),0.0)**ex


def ratio_gm_ia(ex,vct):
    h=1e-5
    a0=activation(140.0,-2.0,ex,vct)
    ap=activation(140.0,-2.0+h,ex,vct)
    am=activation(140.0,-2.0-h,ex,vct)
    if a0<=0.0:return 1e9
    return ((ap-am)/(2*h))/a0


def derive_local(ex):
    target=TARGET_GM/TARGET_IA

    # Find a sign-changing interval rather than assuming monotonic orientation.
    xs=[-5.0+i*0.05 for i in range(201)]
    vals=[ratio_gm_ia(ex,x)-target for x in xs]
    bracket=None
    for a,b,fa,fb in zip(xs,xs[1:],vals,vals[1:]):
        if fa==0.0:
            bracket=(a,a);break
        if fa*fb<=0.0:
            bracket=(a,b);break
    if bracket is None:
        raise RuntimeError(f"no VCT root for EX={ex}")

    lo,hi=bracket
    if lo!=hi:
        flo=ratio_gm_ia(ex,lo)-target
        for _ in range(80):
            mid=.5*(lo+hi)
            fm=ratio_gm_ia(ex,mid)-target
            if flo*fm<=0.0:
                hi=mid
            else:
                lo=mid; flo=fm
        vct=.5*(lo+hi)
    else:
        vct=lo

    act=activation(140.0,-2.0,ex,vct)
    kg1=act/TARGET_IA
    s0=TARGET_IG2/act
    return vct,kg1,s0


def knorm(va):
    if va<=0.0:return 0.0
    return math.atan(va/KNEE)/math.atan(250.0/KNEE)


def ia(va,vg2,vg1,ex,vct,kg1):
    slope=max(0.1,1.0+LAMBDA*(va-250.0))
    return max(0.0,activation(vg2,vg1,ex,vct)/kg1*slope*knorm(va))


def ig2(va,vg2,vg1,ex,vct,s0):
    return activation(vg2,vg1,ex,vct)*s0


def solve_dc(vb,p):
    ex,vct,kg1,s0=p
    vp=.35*vb;vs=.50*vb;vk=2.0
    for _ in range(30000):
        a=ia(vp-vk,vs-vk,-vk,ex,vct,kg1)
        s=ig2(vp-vk,vs-vk,-vk,ex,vct,s0)
        tvp=vb-a*RA
        tvs=vb-s*RG2
        tvk=(a+s)*RK
        if max(abs(tvp-vp),abs(tvs-vs),abs(tvk-vk))<1e-10:
            return vp,vs,vk,a,s
        d=.10
        vp=(1-d)*vp+d*tvp
        vs=(1-d)*vs+d*tvs
        vk=(1-d)*vk+d*tvk
    raise RuntimeError("DC solve")


def solve_plate(vin,dc,p):
    ex,vct,kg1,s0=p
    vp0,vs,vk,a0,_=dc
    rload=1.0/(1.0/RA+1.0/RGLOAD)
    vth=vp0+a0*rload
    vg1=vin-vk

    def residual(x):
        cur=ia(x-vk,vs-vk,vg1,ex,vct,kg1)
        return x-(vth-cur*rload)

    lo=vk-20.0
    hi=max(vth+50.0,vp0+50.0)
    flo=residual(lo)
    fhi=residual(hi)

    for _ in range(10):
        if flo<=0.0<=fhi:
            break
        if flo>0.0:
            lo-=50.0
            flo=residual(lo)
        if fhi<0.0:
            hi+=50.0
            fhi=residual(hi)
    else:
        raise RuntimeError("plate root not bracketed")

    for _ in range(80):
        mid=.5*(lo+hi)
        fm=residual(mid)
        if abs(fm)<1e-10 or hi-lo<1e-10:
            return mid
        if fm>0.0:
            hi=mid
        else:
            lo=mid

    return .5*(lo+hi)


def small_gain(dc,p):
    dv=1e-5
    return (solve_plate(dv,dc,p)-solve_plate(-dv,dc,p))/(2*dv)


def waveform(vb,vin_rms,p,n=160):
    dc=solve_dc(vb,p)
    ys=[]
    for i in range(n):
        vin=vin_rms*math.sqrt(2.0)*math.sin(2.0*math.pi*i/n)
        ys.append(solve_plate(vin,dc,p))
    mean=sum(ys)/n
    ys=[y-mean for y in ys]
    out=math.sqrt(sum(y*y for y in ys)/n)
    amps=[]
    for h in range(1,9):
        re=sum(y*math.cos(2*math.pi*h*i/n) for i,y in enumerate(ys))
        im=-sum(y*math.sin(2*math.pi*h*i/n) for i,y in enumerate(ys))
        amps.append(2*math.hypot(re,im)/n)
    thd=100*math.sqrt(sum(a*a for a in amps[1:]))/amps[0]
    return out,thd


def output_at_5(vb,p):
    lo=0.0;hi=1.5
    for _ in range(22):
        mid=.5*(lo+hi)
        _,d=waveform(vb,mid,p,128)
        if d<5.0:lo=mid
        else:hi=mid
    vin=.5*(lo+hi)
    out,d=waveform(vb,vin,p,256)
    return out


def graph_score(rows,p,which):
    ex,vct,kg1,s0=p
    vals=[]
    for r in rows:
        if which=="A":
            va=250.0; vg2=float(r["vg2_v"]); vg1=float(r["vg1_v"])
            ref=float(r["ia_ma"])*1e-3;u=float(r["uncertainty_ma"])*1e-3
        else:
            va=float(r["va_v"]);vg2=140.0;vg1=float(r["curve_vg1_v"])
            ref=float(r["ia_ma"])*1e-3;u=float(r["uncertainty_ma"])*1e-3
        vals.append((ia(va,vg2,vg1,ex,vct,kg1)-ref)/u)
    return math.sqrt(sum(x*x for x in vals)/len(vals)),max(abs(x) for x in vals)


def main():
    print("SMX-3 V2 EF86 EX curvature scan")
    print("Each EX is locally recalibrated to exact Ia/gm/Ig2 at 250/140/-2.")
    print()
    print("EX,VCT,KG1,S0,GraphA_NRMS,GraphB_NRMS,max_Ik_err_pct,max_gain_err_pct,max_Vo5_err_pct,score")

    results=[]

    for ex in EX_VALUES:
        try:
            vct,kg1,s0=derive_local(ex)
            p=(ex,vct,kg1,s0)
            ga,_=graph_score(A_POINTS,p,"A")
            gb,_=graph_score(B_POINTS,p,"B")
            ikerrs=[];gerrs=[];verrs=[]
            for vb,t in AMP.items():
                dc=solve_dc(vb,p)
                ik=dc[3]+dc[4]
                g=abs(small_gain(dc,p))
                vo=output_at_5(vb,p)
                ikerrs.append(abs(100*(ik-t["ik"])/t["ik"]))
                gerrs.append(abs(100*(g-t["gain"])/t["gain"]))
                verrs.append(abs(100*(vo-t["vo5"])/t["vo5"]))

            mi=max(ikerrs);mg=max(gerrs);mv=max(verrs)
            # Comparison score only; no promotion threshold.
            score=ga+gb+mi/5.0+mg/5.0+mv/10.0
            results.append((score,ex,p,ga,gb,mi,mg,mv))
            print(f"{ex:.4f},{vct:.9f},{kg1:.9f},{s0:.12g},{ga:.6f},{gb:.6f},{mi:.4f},{mg:.4f},{mv:.4f},{score:.6f}")
        except Exception as e:
            print(f"{ex:.4f},ERROR,{type(e).__name__}:{e}")

    results.sort()
    print()
    print("BEST CANDIDATES")
    for score,ex,p,ga,gb,mi,mg,mv in results[:5]:
        print(f"EX={ex:.4f} score={score:.6f} GraphA={ga:.3f} GraphB={gb:.3f} IkMax={mi:.2f}% GainMax={mg:.2f}% Vo5Max={mv:.2f}%")

    if results:
        _,ex,p,_,_,_,_,_=results[0]
        print()
        print(f"DETAIL BEST EX={ex:.4f}")
        print("Vb,Ik_err_pct,gain_err_pct,Vo5_model,Vo5_target,Vo5_err_pct")
        for vb,t in AMP.items():
            dc=solve_dc(vb,p)
            ik=dc[3]+dc[4]
            g=abs(small_gain(dc,p))
            vo=output_at_5(vb,p)
            print(
                f"{vb:.0f},"
                f"{100*(ik-t['ik'])/t['ik']:+.4f},"
                f"{100*(g-t['gain'])/t['gain']:+.4f},"
                f"{vo:.6f},{t['vo5']:.6f},"
                f"{100*(vo-t['vo5'])/t['vo5']:+.4f}"
            )

    return 0


if __name__=="__main__":
    raise SystemExit(main())
