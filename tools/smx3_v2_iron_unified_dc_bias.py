#!/usr/bin/env python3
"""Frozen DC-bias/remanence gate for unified SMX-3 V2 IRON candidate.

Evidence-derived recovery policy:
- immediate post-bias response must show strong H2/asymmetry;
- by 240 symmetric 20 Hz cycles, H2 must be materially suppressed;
- by 480 cycles, H/M and relaxation current must converge back to the
  deterministic unbiased periodic orbit within strict offline tolerances.

This preserves physical magnetic history while proving the extra relaxation
state does not create hidden remanence.
"""

import math
import smx3_v2_iron_unified_candidate as m

FS=24000.0
FREQ=20.0
LEVEL_DBU=4.0


def run_sine(H,M,I,cycles,analyze_last=6):
    dt=1.0/FS
    vrms=0.775*10.0**(LEVEL_DBU/20.0)
    amp=vrms*math.sqrt(2.0)
    source=lambda t:amp*math.sin(2.0*math.pi*FREQ*t)
    n=int(round(cycles*FS/FREQ))
    keep=int(round(min(analyze_last,cycles)*FS/FREQ))
    y=[]
    t=0.0

    for idx in range(n):
        H,M,I,vo=m.rk4_step(t,H,M,I,dt,source)
        t+=dt
        if idx>=n-keep:
            y.append(vo)

    def comp(h):
        re=im=0.0
        for k,v in enumerate(y):
            a=2.0*math.pi*h*FREQ*k/FS
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


def describe(label,H,M,I,thd,hs):
    h2=hs[0]; h3=hs[1]; h5=hs[3]
    ratio=20.0*math.log10(max(h2,1e-30)/max(h3,1e-30))
    print(
        f"{label}: H={H:.9f} M={M:.9f} Irel={I:.12g} "
        f"THD={100*thd:.9f}% H2={100*h2:.9f}% "
        f"H3={100*h3:.9f}% H5={100*h5:.9f}% "
        f"H2/H3={ratio:.3f}dB"
    )


def main():
    print("SMX-3 V2 unified IRON frozen DC-bias/remanence gate")
    print()

    # Authoritative unbiased periodic orbit.
    H=M=I=0.0
    H,M,I,bthd,bhs=run_sine(H,M,I,480)
    base=(H,M,I,bthd,bhs)
    describe("baseline_480",H,M,I,bthd,bhs)

    failures=[]

    if bhs[0]>=0.01*bhs[1]:
        failures.append("baseline even-order content is too high")

    for vdc in (0.050,0.100):
        print()
        H=M=I=0.0
        H,M,I=run_dc(H,M,I,vdc)

        # First four cycles: explicit magnetic-history evidence.
        H,M,I,t4,h4=run_sine(H,M,I,4,4)
        describe(f"{int(vdc*1000)}mV_after_4",H,M,I,t4,h4)

        if h4[0]<=h4[1]:
            failures.append(f"{vdc:g} V: immediate post-bias H2 is not dominant")

        # Continue to a total of 240 cycles.
        H,M,I,t240,h240=run_sine(H,M,I,236,6)
        describe(f"{int(vdc*1000)}mV_after_240",H,M,I,t240,h240)

        if 100.0*h240[0]>0.00025:
            failures.append(f"{vdc:g} V: H2 remains too high after 240 cycles")

        # Continue to 480 total cycles and demand near-identical periodic state.
        H,M,I,t480,h480=run_sine(H,M,I,240,6)
        describe(f"{int(vdc*1000)}mV_after_480",H,M,I,t480,h480)

        dH=abs(H-base[0])
        dM=abs(M-base[1])
        dI=abs(I-base[2])

        if dH>0.001:
            failures.append(f"{vdc:g} V: H periodic-state residual {dH:.6g}")
        if dM>1.0:
            failures.append(f"{vdc:g} V: M periodic-state residual {dM:.6g}")
        if dI>1e-11:
            failures.append(f"{vdc:g} V: relaxation-state residual {dI:.6g}")
        if abs(100.0*t480-100.0*bthd)>0.00005:
            failures.append(f"{vdc:g} V: recovered THD differs from baseline")

    print()
    if failures:
        print("FAIL:")
        for x in failures:
            print(" - "+x)
        return 1

    print("PASS: DC pre-bias creates physical JA history, symmetric AC erases it toward a deterministic orbit, and the relaxation state adds no remanence.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
