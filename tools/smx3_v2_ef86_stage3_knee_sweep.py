#!/usr/bin/env python3
"""Coarse Stage-3 EF86 grid-dependent knee sweep.

Hypothesis:
Philips Graph B visibly shows that the pentode knee is not one fixed
plate-voltage scale for every Vg1 curve.

Test a minimal physically interpretable extension:

    KNEE_eff(Vg1) = K0 * exp(BK * (Vg1 + 2))

and normalize the plate factor to unity at Va=250 V for every Vg1, so the
already-fitted Stage-1 Graph-A surface is preserved exactly at its reference
plate voltage.

This is a COARSE MODEL-FORM SWEEP, not final fitting.

Score:
- exact Philips Vo@5% envelope, Vb=200..400 V;
- Stage-2 amplifier Ik/gain;
- provisional Graph-B residual.

Standard library only.
"""

import csv
import math
import pathlib

ROOT=pathlib.Path(__file__).resolve().parents[1]
GRAPHB=ROOT/"research"/"ef86_philips1956_platecurve_provisional.csv"

BASE={
    "MU":42.1294068459,
    "EX":1.48016674106,
    "KG1":2059.06189749,
    "KP":215.816749098,
    "VCT":0.761562843483,
    "KVB_SCREEN":430.818432714,
    "LAMBDA":0.000160501489918,
}
S0=9.02342723159e-5

RA=100000.0
RG2=390000.0
RK=1000.0
RGLOAD=330000.0

AMP={
    200.0:{"ik":0.00170,"gain":106.0,"vo5":40.0},
    250.0:{"ik":0.00210,"gain":112.0,"vo5":50.0},
    300.0:{"ik":0.00250,"gain":116.0,"vo5":64.0},
    350.0:{"ik":0.00290,"gain":120.0,"vo5":75.0},
    400.0:{"ik":0.00330,"gain":124.0,"vo5":87.0},
}

K0_VALUES=(2.0,5.0,10.0,20.0,40.0,80.0)
BK_VALUES=(-0.50,-0.25,0.0,0.25,0.50,0.75,1.00)

GRAPHB_POINTS=list(csv.DictReader(GRAPHB.open(encoding="utf-8")))


def l1p(x):
    if x>50.0:return x
    if x<-50.0:return math.exp(x)
    return math.log1p(math.exp(x))


def activation(vg2,vg1):
    if vg2<=0.0:return 0.0
    b=BASE
    den=math.sqrt(b["KVB_SCREEN"]+vg2*vg2)
    z=(1.0/b["MU"]+(b["VCT"]+vg1)/den)*b["KP"]
    e1=vg2/b["KP"]*l1p(z)
    return 2.0*max(e1,0.0)**b["EX"]


def knee_eff(vg1,k0,bk):
    exponent=max(-8.0,min(8.0,bk*(vg1+2.0)))
    return k0*math.exp(exponent)


def knorm(va,vg1,k0,bk):
    if va<=0.0:return 0.0
    k=knee_eff(vg1,k0,bk)
    den=math.atan(250.0/k)
    return math.atan(va/k)/den


def ia(va,vg2,vg1,k0,bk):
    b=BASE
    slope=max(0.1,1.0+b["LAMBDA"]*(va-250.0))
    return max(0.0,activation(vg2,vg1)/b["KG1"]*slope*knorm(va,vg1,k0,bk))


def ig2(va,vg2,vg1):
    return activation(vg2,vg1)*S0


def solve_dc(vb,k0,bk):
    vp=.35*vb; vs=.50*vb; vk=2.0
    for _ in range(25000):
        a=ia(vp-vk,vs-vk,-vk,k0,bk)
        s=ig2(vp-vk,vs-vk,-vk)
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


def solve_plate(vin,dc,k0,bk):
    vp0,vs,vk,a0,_=dc
    rload=1.0/(1.0/RA+1.0/RGLOAD)
    vth=vp0+a0*rload
    x=vp0
    for _ in range(3000):
        cur=ia(x-vk,vs-vk,vin-vk,k0,bk)
        t=vth-cur*rload
        if abs(t-x)<1e-9:return x
        x=.72*x+.28*t
    raise RuntimeError("plate solve")


def small_gain(dc,k0,bk):
    dv=1e-5
    return (solve_plate(dv,dc,k0,bk)-solve_plate(-dv,dc,k0,bk))/(2*dv)


def waveform(vb,vin_rms,k0,bk,n=192):
    dc=solve_dc(vb,k0,bk)
    ys=[]
    for i in range(n):
        vin=vin_rms*math.sqrt(2.0)*math.sin(2.0*math.pi*i/n)
        ys.append(solve_plate(vin,dc,k0,bk))
    mean=sum(ys)/n
    ys=[y-mean for y in ys]

    out=math.sqrt(sum(y*y for y in ys)/n)
    amps=[]
    for h in range(1,9):
        re=sum(y*math.cos(2.0*math.pi*h*i/n) for i,y in enumerate(ys))
        im=-sum(y*math.sin(2.0*math.pi*h*i/n) for i,y in enumerate(ys))
        amps.append(2.0*math.hypot(re,im)/n)
    thd=100.0*math.sqrt(sum(a*a for a in amps[1:]))/amps[0]
    return out,thd


def output_at_5pct(vb,k0,bk):
    lo=0.0; hi=1.4
    for _ in range(22):
        mid=.5*(lo+hi)
        _,d=waveform(vb,mid,k0,bk,128)
        if d<5.0:lo=mid
        else:hi=mid
    vin=.5*(lo+hi)
    out,d=waveform(vb,vin,k0,bk,256)
    return out


def score(k0,bk):
    try:
        # Weighted normalized terms. Exact table data dominate.
        residuals=[]

        for vb,t in AMP.items():
            dc=solve_dc(vb,k0,bk)
            ik=dc[3]+dc[4]
            gain=abs(small_gain(dc,k0,bk))
            vo5=output_at_5pct(vb,k0,bk)

            residuals.append((ik-t["ik"])/0.00007)
            residuals.append((gain-t["gain"])/3.0)
            residuals.append((vo5-t["vo5"])/(0.04*t["vo5"]))

        # Provisional Graph-B points keep the knee family from moving in the
        # wrong direction; broad source uncertainties already live in the CSV.
        for r in GRAPHB_POINTS:
            va=float(r["va_v"])
            vg=float(r["curve_vg1_v"])
            ref=float(r["ia_ma"])*1e-3
            u=float(r["uncertainty_ma"])*1e-3
            residuals.append((ia(va,140.0,vg,k0,bk)-ref)/u)

        nrms=math.sqrt(sum(x*x for x in residuals)/len(residuals))
        return nrms
    except (RuntimeError,ValueError,OverflowError,ZeroDivisionError):
        return 1e9


def main():
    print("SMX-3 V2 EF86 Stage-3 grid-dependent knee coarse sweep")
    print("Keff = K0 * exp(BK*(Vg1+2)); normalized at Va=250V")
    print()
    print("K0,BK,score_NRMS")

    rows=[]
    for k0 in K0_VALUES:
        for bk in BK_VALUES:
            s=score(k0,bk)
            rows.append((s,k0,bk))
            print(f"{k0:.6f},{bk:+.6f},{s:.6f}")

    rows.sort()
    print()
    print("BEST COARSE CANDIDATES")
    for s,k0,bk in rows[:8]:
        print(f"score={s:.6f} K0={k0:.6f} BK={bk:+.6f}")

    best=rows[0]
    print()
    print(f"BEST: K0={best[1]:.6f} BK={best[2]:+.6f} score={best[0]:.6f}")

    # Detailed exact-table output for best coarse pair.
    _,k0,bk=best
    print("Vb,Ik_err_pct,gain_err_pct,Vo5_model,Vo5_target,Vo5_err_pct")
    for vb,t in AMP.items():
        dc=solve_dc(vb,k0,bk)
        ik=dc[3]+dc[4]
        g=abs(small_gain(dc,k0,bk))
        vo5=output_at_5pct(vb,k0,bk)
        print(
            f"{vb:.0f},"
            f"{100*(ik-t['ik'])/t['ik']:+.4f},"
            f"{100*(g-t['gain'])/t['gain']:+.4f},"
            f"{vo5:.6f},{t['vo5']:.6f},"
            f"{100*(vo5-t['vo5'])/t['vo5']:+.4f}"
        )

    return 0


if __name__=="__main__":
    raise SystemExit(main())
