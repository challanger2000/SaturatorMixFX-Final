#!/usr/bin/env python3
"""DC-bias/remanence regression for the frozen unified IRON candidate.

Verifies:
- baseline unbiased H3 dominance after full settling;
- DC pre-bias produces transient H2/asymmetry;
- symmetric AC returns H/M toward the deterministic orbit;
- the added relaxation current decays back toward its periodic baseline and
  does not become a hidden remanent state.
"""

import math
import smx3_v2_iron_unified_candidate as m

FS=48000.0
FREQ=20.0
LEVEL_DBU=4.0


def run_source(H,M,I,source,seconds):
    dt=1.0/FS
    n=int(round(seconds*FS))
    t=0.0
    for _ in range(n):
        H,M,I,_=m.rk4_step(t,H,M,I,dt,source)
        t+=dt
    return H,M,I


def run_sine(H,M,I,cycles,analyze_last=6):
    dt=1.0/FS
    vrms=0.775*10.0**(LEVEL_DBU/20.0)
    amp=vrms*math.sqrt(2.0)
    n=int(round(cycles*FS/FREQ))
    keep=int(round(analyze_last*FS/FREQ))
    source=lambda t:amp*math.sin(2.0*math.pi*FREQ*t)
    y=[]
    t=0.0

    for idx in range(n):
        H,M,I,vo=m.rk4_step(t,H,M,I,dt,source)
        t+=dt
        if idx>=n-keep:
            y.append(vo)

    def comp(h):
        re=im=0.0
        for i,v in enumerate(y):
            a=2.0*math.pi*h*FREQ*i/FS
            re+=v*math.cos(a)
            im-=v*math.sin(a)
        return math.hypot(re,im)

    f1=comp(1)
    hs=[comp(h)/f1 for h in range(2,8)]
    thd=math.sqrt(sum(x*x for x in hs))
    return H,M,I,thd,hs


def summary(label,H,M,I,thd,hs):
    h2=hs[0];h3=hs[1];h5=hs[3]
    ratio=20.0*math.log10(max(h2,1e-30)/max(h3,1e-30))
    print(
        f"{label}: H={H:.9f} M={M:.9f} Irel={I:.12g} "
        f"THD={100*thd:.9f}% H2={100*h2:.9f}% "
        f"H3={100*h3:.9f}% H5={100*h5:.9f}% H2/H3={ratio:.3f}dB"
    )
    return ratio


def main():
    print("SMX-3 V2 unified IRON DC-bias/remanence regression")
    print("20 Hz / +4 dBu")
    print()

    H=M=I=0.0
    H,M,I,bthd,bhs=run_sine(H,M,I,120,6)
    bratio=summary("baseline after 120 cycles",H,M,I,bthd,bhs)
    baseline=(H,M,I,bthd,bhs,bratio)

    failures=[]

    if bhs[0]>=0.1*bhs[1]:
        failures.append("baseline lost H3 dominance")

    for vdc in (0.010,0.050,0.100):
        H=M=I=0.0
        H,M,I=run_source(H,M,I,lambda t,v=vdc:v,1.0)

        print()
        print(f"DC pre-bias {1000*vdc:.1f} mV -> H={H:.9f} M={M:.9f} Irel={I:.12g}")

        # Remove DC and inspect immediate four-cycle response.
        H,M,I,t1,h1=run_sine(H,M,I,4,4)
        r1=summary("first 4 AC cycles",H,M,I,t1,h1)

        # Continue to the fully settled periodic orbit.
        H,M,I,t2,h2=run_sine(H,M,I,120,6)
        r2=summary("after 120 more AC cycles",H,M,I,t2,h2)

        if vdc>=0.050:
            if h1[0] <= 10.0*h2[0]:
                failures.append(f"{vdc:g} V: transient H2 did not materially decay")
            if abs(r2-bratio)>15.0:
                failures.append(f"{vdc:g} V: recovered H2/H3 far from baseline")

        # Relaxation state is dynamic only. At the same phase of the settled
        # periodic orbit it must converge back close to the baseline state.
        base_I=baseline[2]
        if abs(I-base_I)>2.0e-8:
            failures.append(
                f"{vdc:g} V: relaxation periodic-state recall differs by {I-base_I:+.3e} A"
            )

        # H/M should also return near deterministic periodic state.
        if abs(H-baseline[0])>0.05:
            failures.append(f"{vdc:g} V: H did not return near baseline")
        if abs(M-baseline[1])>500.0:
            failures.append(f"{vdc:g} V: M did not return near baseline")

    print()
    if failures:
        print("FAIL:")
        for x in failures:
            print(" - "+x)
        return 1

    print("PASS: unified candidate preserves JA remanence/asymmetry behavior and the relaxation state does not create hidden remanence.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
