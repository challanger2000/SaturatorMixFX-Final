#!/usr/bin/env python3
"""Exact-table large-signal envelope check for the generalized EF86 surrogate.

The Philips 1956 circuit-1 table gives the output voltage at 5% total
harmonic distortion for Vb=200..400 V. This is a strong out-of-fit test of
whether one model generalizes across supply conditions.

Standard library only.
"""

import math
import smx3_v2_ef86_generalized_surrogate as m

TARGETS={
    200.0:40.0,
    250.0:50.0,
    300.0:64.0,
    350.0:75.0,
    400.0:87.0,
}


def waveform(vb,vin_rms,n=1024):
    dc=m.solve_dc(vb)
    vp0,vs,vk,ia0,_=dc
    rload=1.0/(1.0/m.RA+1.0/m.RGLOAD)
    vth=vp0+ia0*rload
    ys=[]

    for i in range(n):
        vin=vin_rms*math.sqrt(2.0)*math.sin(2.0*math.pi*i/n)
        x=vp0
        for _ in range(10000):
            ia,_=m.currents(x-vk,vs-vk,vin-vk)
            target=vth-ia*rload
            if abs(target-x)<1e-11:
                break
            x=0.75*x+0.25*target
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


def find_5pct(vb):
    lo=0.0
    hi=1.5
    for _ in range(46):
        mid=0.5*(lo+hi)
        _,d=waveform(vb,mid,512)
        if d<5.0:
            lo=mid
        else:
            hi=mid
    vin=0.5*(lo+hi)
    out,d=waveform(vb,vin,2048)
    return vin,out,d


def main():
    print("SMX-3 V2 generalized EF86 exact 5%-THD envelope")
    print("Vb_V,Vin_5pct_Vrms,Vo_model_Vrms,Vo_Philips_Vrms,error_pct")

    worst=0.0
    for vb in sorted(TARGETS):
        vin,out,d=find_5pct(vb)
        target=TARGETS[vb]
        err=100.0*(out-target)/target
        worst=max(worst,abs(err))
        print(f"{vb:.1f},{vin:.9f},{out:.9f},{target:.9f},{err:+.6f}")

    print()
    print(f"worst absolute output error = {worst:.6f}%")

    # This is an informational/rejection probe. Keep exit 0 so the reference
    # suite can record the model limitation while later model families are
    # evaluated.
    if worst<=5.0:
        print("SHAPE-CHECK: candidate unexpectedly clears the full exact envelope.")
    else:
        print("REJECT AS FINAL EF86 MODEL: exact Philips 5%-THD envelope is not reproduced.")

    return 0


if __name__=="__main__":
    raise SystemExit(main())
