#!/usr/bin/env python3
"""EF86 Stage-3 large-signal knee candidate for SMX-3 V2.

Builds on the accepted Stage-2 joint static candidate and adds only a strongly
localized low-plate-voltage correction:

    Ia_stage3 = Ia_stage2 *
                (1 + A0 * (Vg2/140)^P_SCREEN * exp(-Va/VK))

The correction is effectively absent throughout the normal Graph-A/B region
and acts only in the large-signal knee trajectory.

Standard library only.
"""

import csv
import math
import pathlib

import smx3_v2_ef86_stage2_joint_static as base

ROOT=pathlib.Path(__file__).resolve().parents[1]
GRAPHD=ROOT/"research"/"ef86_philips1956_graphD_provisional.csv"

A0=0.558549505811
P_SCREEN=0.533215365718
VK=11.5490503835

TARGET_ENV={
    200.0:40.0,
    250.0:50.0,
    300.0:64.0,
    350.0:75.0,
    400.0:87.0,
}


def currents(vp,vg2,vg1):
    ia,ig2=base.currents(vp,vg2,vg1)

    if vp>0.0 and vg2>0.0:
        scale=A0*(vg2/140.0)**P_SCREEN
        ia*=1.0+scale*math.exp(-vp/VK)

    return ia,ig2


def solve_dc(vb):
    vp=0.3*vb
    vs=0.45*vb
    vk=2.0

    for _ in range(30000):
        ia,ig2=currents(vp-vk,vs-vk,-vk)

        a=vb-ia*base.RA
        s=vb-ig2*base.RG2
        k=(ia+ig2)*base.RK

        if max(abs(a-vp),abs(s-vs),abs(k-vk))<1e-10:
            return vp,vs,vk,ia,ig2

        d=0.05
        vp=(1.0-d)*vp+d*a
        vs=(1.0-d)*vs+d*s
        vk=(1.0-d)*vk+d*k

    raise RuntimeError("DC solve failed")


def waveform(vb,vin_rms,n=384):
    dc=solve_dc(vb)
    vp0,vs,vk,ia0,_=dc
    rload=1.0/(1.0/base.RA+1.0/base.RGLOAD)
    vth=vp0+ia0*rload

    ys=[]

    for i in range(n):
        vin=vin_rms*math.sqrt(2.0)*math.sin(2.0*math.pi*i/n)
        x=vp0

        for _ in range(3000):
            ia,_=currents(x-vk,vs-vk,vin-vk)
            target=vth-ia*rload
            if abs(target-x)<1e-10:
                break
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


def find_for_thd(vb,target=5.0):
    lo=0.0
    hi=1.5

    for _ in range(28):
        mid=0.5*(lo+hi)
        _,d=waveform(vb,mid,192)
        if d<target:
            lo=mid
        else:
            hi=mid

    vin=0.5*(lo+hi)
    out,d=waveform(vb,vin,768)
    return vin,out,d


def input_for_output(vb,target_out):
    lo=0.0
    hi=1.0

    for _ in range(28):
        mid=0.5*(lo+hi)
        out,_=waveform(vb,mid,192)
        if out<target_out:
            lo=mid
        else:
            hi=mid

    vin=0.5*(lo+hi)
    out,d=waveform(vb,vin,768)
    return vin,out,d


def main():
    print("SMX-3 V2 EF86 Stage-3 large-signal knee candidate")
    print(f"A0={A0:.12f} P_SCREEN={P_SCREEN:.12f} VK={VK:.12f} V")
    print()
    print("Vb,Vin_5pct_Vrms,Vo_model_Vrms,Vo_Philips_Vrms,error_pct")

    worst=0.0

    for vb in sorted(TARGET_ENV):
        vin,out,d=find_for_thd(vb)
        target=TARGET_ENV[vb]
        err=100.0*(out-target)/target
        worst=max(worst,abs(err))
        print(f"{vb:.0f},{vin:.9f},{out:.9f},{target:.9f},{err:+.6f}")

    print()
    print(f"worst envelope error={worst:.6f}%")

    if worst>6.0:
        raise SystemExit("FAIL: exact Philips 5%-THD supply envelope")

    # Graph-D remains informational because its intermediate points are manual
    # graph digitizations rather than exact manufacturer tabular values.
    rows=list(csv.DictReader(GRAPHD.open(encoding="utf-8")))

    print()
    print("Graph-D provisional shape:")
    print("Vo_target,Vi_model_mV,Vi_graph_mV,THD_model_pct,THD_graph_pct")

    for r in rows:
        vo=float(r["output_vrms"])
        vin,out,d=input_for_output(250.0,vo)
        print(
            f"{vo:.1f},{vin*1000.0:.6f},{float(r['input_mvrms']):.6f},"
            f"{d:.6f},{float(r['distortion_percent']):.6f}"
        )

    print()
    print("PASS: Stage-3 candidate clears the current exact 5%-THD supply-envelope gate.")
    print("INFO: Graph-D intermediate distortion remains provisional until calibrated extraction.")


if __name__=="__main__":
    raise SystemExit(main())
