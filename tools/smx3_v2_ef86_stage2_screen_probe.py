#!/usr/bin/env python3
"""EF86 Stage-2 minimal screen-current probe.

Uses the accepted Stage-1 plate-current surface and the simplest useful
screen-current law:

    Ig2 = max(Vg2/MUs + Vg1 + Voff, 0)^EXs / KG2

The parameters below are the best current multi-anchor fit to:
- exact Philips Ig2=0.6 mA device anchor;
- circuit-1 Ik(Vb);
- circuit-1 small-signal gain(Vb).

This probe demonstrates whether that simple screen law is structurally
sufficient. It is informational/rejection evidence, not production DSP.
"""

import math

from smx3_v2_ef86_stage1_plate_surface import ia

RA=100000.0
RG2=390000.0
RK=1000.0
RGLOAD=330000.0

Q={
    "MU":42.6790971704,
    "EX":0.9926403824,
    "KG2":2857.12863059,
    "VOFF":0.4428314792,
}

TARGET={
    200.0:(0.00170,106.0),
    250.0:(0.00210,112.0),
    300.0:(0.00250,116.0),
    350.0:(0.00290,120.0),
    400.0:(0.00330,124.0),
}


def ig2(vg2,vg1):
    x=max(vg2/Q["MU"]+vg1+Q["VOFF"],0.0)
    return x**Q["EX"]/Q["KG2"]


def solve_dc(vb):
    vp=0.3*vb
    vs=0.45*vb
    vk=2.0

    for _ in range(50000):
        ia0=ia(vp-vk,vs-vk,-vk)
        ig20=ig2(vs-vk,-vk)

        a=vb-ia0*RA
        s=vb-ig20*RG2
        k=(ia0+ig20)*RK

        if max(abs(a-vp),abs(s-vs),abs(k-vk))<1e-10:
            return vp,vs,vk,ia0,ig20

        d=0.05
        vp=(1-d)*vp+d*a
        vs=(1-d)*vs+d*s
        vk=(1-d)*vk+d*k

    raise RuntimeError("DC solve failed")


def gain(dc):
    vp,vs,vk,ia0,_=dc
    rload=1.0/(1.0/RA+1.0/RGLOAD)
    vth=vp+ia0*rload

    def solve(vin):
        x=vp
        for _ in range(10000):
            a=ia(x-vk,vs-vk,vin-vk)
            target=vth-a*rload
            if abs(target-x)<1e-10:
                return x
            x=0.8*x+0.2*target
        raise RuntimeError("AC solve failed")

    dv=1e-5
    return (solve(dv)-solve(-dv))/(2.0*dv)


def main():
    anchor=ig2(140.0,-2.0)
    print("SMX-3 V2 EF86 Stage-2 minimal screen-current probe")
    print(f"Ig2 @140/-2 = {anchor*1e3:.9f} mA (Philips 0.600 mA)")
    print()
    print("Vb,Ik_model_mA,Ik_target_mA,Gain_model,Gain_target")

    worst_i=0.0
    worst_g=0.0

    for vb in sorted(TARGET):
        dc=solve_dc(vb)
        ik=dc[3]+dc[4]
        g=abs(gain(dc))
        ti,tg=TARGET[vb]

        ei=100.0*(ik-ti)/ti
        eg=100.0*(g-tg)/tg
        worst_i=max(worst_i,abs(ei))
        worst_g=max(worst_g,abs(eg))

        print(f"{vb:.0f},{ik*1e3:.9f},{ti*1e3:.9f},{g:.9f},{tg:.9f}")

    print()
    print(f"worst |Ik error| = {worst_i:.6f}%")
    print(f"worst |gain error| = {worst_g:.6f}%")

    if worst_i<=5.0 and worst_g<=5.0:
        print("UNEXPECTED: minimal screen law now clears provisional structural target.")
    else:
        print("REJECT AS FINAL SCREEN MODEL: minimal screen-current law is structurally insufficient.")

    return 0


if __name__=="__main__":
    raise SystemExit(main())
