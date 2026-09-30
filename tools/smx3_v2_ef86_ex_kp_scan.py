#!/usr/bin/env python3
"""EF86 EX x KP transfer-curvature scan for SMX-3 V2.

Reopen only two existing equation-family shape parameters:
- EX: global grid-current transfer exponent
- KP: softplus sharpness parameter

For every candidate:
- solve VCT so gm/Ia at the Philips device point is exact;
- derive KG1 so Ia=3.0 mA exactly;
- derive S0 so Ig2=0.6 mA exactly.

Thus candidates cannot win by moving the local device operating point.

Evaluate independently:
- Philips Graph A;
- Philips Graph B;
- exact circuit Ik/gain table;
- exact multi-supply Vo@5% envelope;
- provisional Graph-D large-signal trajectory.

Standard library only.
"""

import csv
import math
import pathlib

ROOT=pathlib.Path(__file__).resolve().parents[1]
GRAPHA=ROOT/"research"/"ef86_philips_graphA_provisional.csv"
GRAPHB=ROOT/"research"/"ef86_philips1956_platecurve_provisional.csv"
GRAPHD=ROOT/"research"/"ef86_philips1956_graphD_provisional.csv"

MU=42.1294068459
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

EX_VALUES=(1.36,1.38,1.40,1.42,1.44)
KP_VALUES=(140.0,180.0,220.0,260.0,320.0)

A_POINTS=list(csv.DictReader(GRAPHA.open(encoding="utf-8")))
B_POINTS=list(csv.DictReader(GRAPHB.open(encoding="utf-8")))
D_POINTS=list(csv.DictReader(GRAPHD.open(encoding="utf-8")))


def l1p(x):
    if x>50.0:return x
    if x<-50.0:return math.exp(x)
    return math.log1p(math.exp(x))


def e1(vg2,vg1,vct,kp):
    den=math.sqrt(KVB_SCREEN+vg2*vg2)
    z=(1.0/MU+(vct+vg1)/den)*kp
    return vg2/kp*l1p(z)


def activation(vg2,vg1,ex,vct,kp):
    return 2.0*max(e1(vg2,vg1,vct,kp),0.0)**ex


def ratio_gm_ia(ex,vct,kp):
    h=1e-5
    a0=activation(140.0,-2.0,ex,vct,kp)
    ap=activation(140.0,-2.0+h,ex,vct,kp)
    am=activation(140.0,-2.0-h,ex,vct,kp)
    if a0<=0.0:return 1e9
    return ((ap-am)/(2*h))/a0


def derive_local(ex,kp):
    target=TARGET_GM/TARGET_IA
    xs=[-5.0+i*0.05 for i in range(201)]
    vals=[ratio_gm_ia(ex,x,kp)-target for x in xs]

    bracket=None
    for a,b,fa,fb in zip(xs,xs[1:],vals,vals[1:]):
        if fa==0.0:
            bracket=(a,a);break
        if fa*fb<=0.0:
            bracket=(a,b);break

    if bracket is None:
        raise RuntimeError("no VCT root")

    lo,hi=bracket
    if lo!=hi:
        flo=ratio_gm_ia(ex,lo,kp)-target
        for _ in range(80):
            mid=.5*(lo+hi)
            fm=ratio_gm_ia(ex,mid,kp)-target
            if flo*fm<=0.0:
                hi=mid
            else:
                lo=mid;flo=fm
        vct=.5*(lo+hi)
    else:
        vct=lo

    act=activation(140.0,-2.0,ex,vct,kp)
    kg1=act/TARGET_IA
    s0=TARGET_IG2/act
    return vct,kg1,s0


def knorm(va):
    if va<=0.0:return 0.0
    return math.atan(va/KNEE)/math.atan(250.0/KNEE)


def ia(va,vg2,vg1,p):
    ex,kp,vct,kg1,s0=p
    slope=max(0.1,1.0+LAMBDA*(va-250.0))
    return max(0.0,activation(vg2,vg1,ex,vct,kp)/kg1*slope*knorm(va))


def ig2(va,vg2,vg1,p):
    ex,kp,vct,kg1,s0=p
    return activation(vg2,vg1,ex,vct,kp)*s0


def solve_dc(vb,p):
    vp=.35*vb;vs=.50*vb;vk=2.0
    for _ in range(30000):
        a=ia(vp-vk,vs-vk,-vk,p)
        s=ig2(vp-vk,vs-vk,-vk,p)
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
    vp0,vs,vk,a0,_=dc
    rload=1.0/(1.0/RA+1.0/RGLOAD)
    vth=vp0+a0*rload
    vg1=vin-vk

    def residual(x):
        cur=ia(x-vk,vs-vk,vg1,p)
        return x-(vth-cur*rload)

    lo=vk-20.0
    hi=max(vth+50.0,vp0+50.0)
    flo=residual(lo);fhi=residual(hi)

    for _ in range(10):
        if flo<=0.0<=fhi:break
        if flo>0.0:
            lo-=50.0;flo=residual(lo)
        if fhi<0.0:
            hi+=50.0;fhi=residual(hi)
    else:
        raise RuntimeError("plate root")

    for _ in range(70):
        mid=.5*(lo+hi)
        fm=residual(mid)
        if abs(fm)<1e-9 or hi-lo<1e-9:return mid
        if fm>0.0:hi=mid
        else:lo=mid
    return .5*(lo+hi)


def small_gain(dc,p):
    dv=1e-5
    return (solve_plate(dv,dc,p)-solve_plate(-dv,dc,p))/(2*dv)


def waveform(vb,vin_rms,p,n=128):
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
    for _ in range(19):
        mid=.5*(lo+hi)
        _,d=waveform(vb,mid,p,96)
        if d<5.0:lo=mid
        else:hi=mid
    vin=.5*(lo+hi)
    out,d=waveform(vb,vin,p,192)
    return out


def graph_score(rows,p,which):
    vals=[]
    for r in rows:
        if which=="A":
            va=250.0;vg2=float(r["vg2_v"]);vg1=float(r["vg1_v"])
            ref=float(r["ia_ma"])*1e-3;u=float(r["uncertainty_ma"])*1e-3
        else:
            va=float(r["va_v"]);vg2=140.0;vg1=float(r["curve_vg1_v"])
            ref=float(r["ia_ma"])*1e-3;u=float(r["uncertainty_ma"])*1e-3
        vals.append((ia(va,vg2,vg1,p)-ref)/u)
    return math.sqrt(sum(x*x for x in vals)/len(vals)),max(abs(x) for x in vals)


def graphD_score(p):
    # Drive with graph-read Vi. Score Vo in percent and THD in stated uncertainty.
    out_rel=[]
    d_sig=[]

    for r in D_POINTS:
        vin=float(r["input_mvrms"])/1000.0
        vo_ref=float(r["output_vrms"])
        d_ref=float(r["distortion_percent"])
        ud=float(r["distortion_uncertainty_pct"])

        out,d=waveform(250.0,vin,p,192)
        out_rel.append(100.0*(out-vo_ref)/vo_ref)
        d_sig.append((d-d_ref)/ud)

    out_rms=math.sqrt(sum(x*x for x in out_rel)/len(out_rel))
    d_nrms=math.sqrt(sum(x*x for x in d_sig)/len(d_sig))
    d_worst=max(abs(x) for x in d_sig)
    return out_rms,d_nrms,d_worst


def evaluate(ex,kp):
    vct,kg1,s0=derive_local(ex,kp)
    p=(ex,kp,vct,kg1,s0)

    ga,_=graph_score(A_POINTS,p,"A")
    gb,_=graph_score(B_POINTS,p,"B")

    ikerrs=[];gerrs=[];voerrs=[]
    for vb,t in AMP.items():
        dc=solve_dc(vb,p)
        ik=dc[3]+dc[4]
        g=abs(small_gain(dc,p))
        vo=output_at_5(vb,p)
        ikerrs.append(abs(100*(ik-t["ik"])/t["ik"]))
        gerrs.append(abs(100*(g-t["gain"])/t["gain"]))
        voerrs.append(abs(100*(vo-t["vo5"])/t["vo5"]))

    d_out,d_nrms,d_worst=graphD_score(p)

    return {
        "p":p,
        "ga":ga,
        "gb":gb,
        "ik":max(ikerrs),
        "gain":max(gerrs),
        "vo5":max(voerrs),
        "dout":d_out,
        "dthd":d_nrms,
        "dthdworst":d_worst,
    }


def main():
    print("SMX-3 V2 EF86 EX x KP curvature scan")
    print("Ia/gm/Ig2 exact at 250V/140V/-2V for every candidate.")
    print()
    print("EX,KP,GraphA,GraphB,IkMaxPct,GainMaxPct,Vo5MaxPct,GraphD_Vo_RMSPct,GraphD_THD_NRMS,GraphD_THD_Worst,eligible")

    rows=[]

    for ex in EX_VALUES:
        for kp in KP_VALUES:
            try:
                r=evaluate(ex,kp)
                eligible=(
                    r["ga"]<=1.0 and r["gb"]<=1.0 and
                    r["ik"]<=7.0 and r["gain"]<=5.0 and r["vo5"]<=5.0
                )
                # Graph D does not determine eligibility because it is provisional.
                # Among candidates that clear stronger gates, rank its residual.
                score=r["dthd"] + 0.15*r["dout"] + 0.25*r["ga"] + 0.25*r["gb"]
                rows.append((0 if eligible else 1,score,ex,kp,r))
                print(
                    f"{ex:.3f},{kp:.1f},{r['ga']:.4f},{r['gb']:.4f},"
                    f"{r['ik']:.3f},{r['gain']:.3f},{r['vo5']:.3f},"
                    f"{r['dout']:.3f},{r['dthd']:.3f},{r['dthdworst']:.3f},"
                    f"{int(eligible)}"
                )
            except Exception as e:
                print(f"{ex:.3f},{kp:.1f},ERROR,{type(e).__name__}:{e}")

    rows.sort()

    print()
    print("BEST ELIGIBLE CANDIDATES")
    shown=0
    for flag,score,ex,kp,r in rows:
        if flag:continue
        p=r["p"]
        print(
            f"EX={ex:.3f} KP={kp:.1f} score={score:.4f} "
            f"GraphA={r['ga']:.3f} GraphB={r['gb']:.3f} "
            f"Ik={r['ik']:.2f}% Gain={r['gain']:.2f}% Vo5={r['vo5']:.2f}% "
            f"GraphDTHD={r['dthd']:.3f}sigma VCT={p[2]:.6f} KG1={p[3]:.3f}"
        )
        shown+=1
        if shown>=8:break

    if shown==0:
        print("No candidate cleared the stronger static/exact manufacturer gates.")

    return 0


if __name__=="__main__":
    raise SystemExit(main())
