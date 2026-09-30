#!/usr/bin/env python3
"""Recovery-convergence probe for frozen unified IRON candidate.

Purpose:
determine how many symmetric 20 Hz AC cycles are required after DC pre-bias
for H/M, harmonic parity and relaxation current to converge toward the
unbiased periodic orbit.

This is informational; it exists to set a justified recovery gate.
"""

import math
import smx3_v2_iron_unified_candidate as m

FS=24000.0
FREQ=20.0
LEVEL_DBU=4.0


def run_sine_state(H,M,I,cycles,keep=6):
    dt=1.0/FS
    vrms=0.775*10.0**(LEVEL_DBU/20.0)
    amp=vrms*math.sqrt(2.0)
    source=lambda t:amp*math.sin(2*math.pi*FREQ*t)
    n=int(round(cycles*FS/FREQ))
    nkeep=int(round(min(keep,cycles)*FS/FREQ))
    y=[]
    t=0.0

    for idx in range(n):
        H,M,I,vo=m.rk4_step(t,H,M,I,dt,source)
        t+=dt
        if idx>=n-nkeep:
            y.append(vo)

    def comp(h):
        re=im=0.0
        for k,v in enumerate(y):
            a=2*math.pi*h*FREQ*k/FS
            re+=v*math.cos(a)
            im-=v*math.sin(a)
        return math.hypot(re,im)

    f1=comp(1)
    hs=[comp(h)/f1 for h in range(2,8)]
    thd=math.sqrt(sum(x*x for x in hs))
    return H,M,I,thd,hs


def run_dc(H,M,I,vdc,seconds=1.0):
    dt=1.0/FS
    source=lambda t:vdc
    n=int(round(seconds*FS))
    t=0.0
    for _ in range(n):
        H,M,I,_=m.rk4_step(t,H,M,I,dt,source)
        t+=dt
    return H,M,I


def row(label,H,M,I,thd,hs,base):
    h2=hs[0];h3=hs[1]
    ratio=20*math.log10(max(h2,1e-30)/max(h3,1e-30))
    print(
        f"{label},{H:.9f},{M:.9f},{I:.12g},{100*thd:.9f},"
        f"{100*h2:.9f},{100*h3:.9f},{ratio:.6f},"
        f"{H-base[0]:+.9f},{M-base[1]:+.9f},{I-base[2]:+.12g}"
    )


def main():
    print("SMX-3 V2 unified IRON recovery convergence")
    print("label,H,M,Irel,THD_pct,H2_pct,H3_pct,H2_over_H3_dB,dH_vs_base,dM_vs_base,dI_vs_base")

    # Establish a very long baseline periodic orbit.
    H=M=I=0.0
    H,M,I,thd,hs=run_sine_state(H,M,I,480)
    base=(H,M,I,thd,hs)
    row("baseline_480",H,M,I,thd,hs,base)

    for vdc in (0.050,0.100):
        H=M=I=0.0
        H,M,I=run_dc(H,M,I,vdc)
        total=0

        for chunk in (4,116,120,240):
            H,M,I,thd,hs=run_sine_state(H,M,I,chunk)
            total+=chunk
            row(f"{int(vdc*1000)}mV_after_{total}cycles",H,M,I,thd,hs,base)

    print("INFO: use convergence trend, not an arbitrary fixed-cycle threshold, to freeze the remanence recovery gate.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
