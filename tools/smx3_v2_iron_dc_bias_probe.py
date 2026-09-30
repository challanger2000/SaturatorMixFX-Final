#!/usr/bin/env python3
"""DC-bias / remanence probe for the provisional SMX-3 V2 IRON candidate.

Tests the stateful magnetic consequence documented by Jensen/Whitlock:
- demagnetized/unbiased operation should be strongly H3-dominant;
- DC magnetic bias should introduce even-order distortion, especially H2;
- after bias removal, symmetric AC cycling should return toward the
  deterministic unbiased periodic orbit.

Research tool only. Standard library only.
"""

import math
import smx3_v2_iron_candidate as m

FS=96000.0
FREQ=20.0
LEVEL_DBU=4.0


def step(t,H,M,vs):
    # Same coupled circuit as the reference, but permit arbitrary source
    # waveform including DC pre-bias.
    rseries=m.RSOURCE+m.RP
    divider=1.0+rseries/m.RLOAD
    numerator=vs-rseries*H/m.KI
    direction=1.0 if numerator>=0.0 else -1.0
    slope=m.dmdh(H,M,direction)
    vnode=numerator/divider
    dH=vnode/(m.KPHI*(1.0+slope))
    dM=slope*dH
    vout=vnode*m.RL/m.RLOAD
    return dH,dM,vout


def rk4_step(t,H,M,dt,source):
    v1=source(t)
    k1h,k1m,_=step(t,H,M,v1)

    tm=t+0.5*dt
    v2=source(tm)
    k2h,k2m,_=step(tm,H+0.5*dt*k1h,M+0.5*dt*k1m,v2)
    k3h,k3m,_=step(tm,H+0.5*dt*k2h,M+0.5*dt*k2m,v2)

    te=t+dt
    v4=source(te)
    k4h,k4m,_=step(te,H+dt*k3h,M+dt*k3m,v4)

    H2=H+dt*(k1h+2*k2h+2*k3h+k4h)/6.0
    M2=M+dt*(k1m+2*k2m+2*k3m+k4m)/6.0
    _,_,vo=step(te,H2,M2,v4)
    return H2,M2,vo


def run_dc(H,M,vdc,seconds):
    dt=1.0/FS
    n=int(round(seconds*FS))
    source=lambda t:vdc
    t=0.0
    for _ in range(n):
        H,M,_=rk4_step(t,H,M,dt,source)
        t+=dt
    return H,M


def run_sine(H,M,cycles,analyze_last=4):
    dt=1.0/FS
    vrms=0.775*10.0**(LEVEL_DBU/20.0)
    amp=vrms*math.sqrt(2.0)
    n=int(round(cycles*FS/FREQ))
    keep=int(round(analyze_last*FS/FREQ))
    y=[]
    t=0.0

    def source(tt):
        return amp*math.sin(2.0*math.pi*FREQ*tt)

    for i in range(n):
        H,M,vo=rk4_step(t,H,M,dt,source)
        t+=dt
        if i>=n-keep:
            y.append(vo)

    N=len(y)

    def component(h):
        re=im=0.0
        for i,v in enumerate(y):
            a=2.0*math.pi*h*FREQ*i/FS
            re+=v*math.cos(a)
            im-=v*math.sin(a)
        return math.hypot(re,im)

    fundamental=component(1)
    hs=[component(h)/fundamental for h in range(2,8)]
    thd=math.sqrt(sum(v*v for v in hs))
    return H,M,thd,hs


def summary(label,H,M,thd,hs):
    h2=hs[0];h3=hs[1];h5=hs[3]
    ratio=20.0*math.log10(max(h2,1e-30)/max(h3,1e-30))
    print(
        f"{label}: H={H:.6f} A/m M={M:.6f} A/m "
        f"THD={100*thd:.9f}% H2={100*h2:.9f}% "
        f"H3={100*h3:.9f}% H5={100*h5:.9f}% H2/H3={ratio:.3f}dB"
    )
    return ratio


def main():
    print("SMX-3 V2 IRON DC-bias/remanence probe")
    print("20 Hz / +4 dBu analysis")
    print()

    # Baseline periodic orbit.
    H=M=0.0
    H,M,thd,hs=run_sine(H,M,40,4)
    baseline_ratio=summary("baseline after 40 AC cycles",H,M,thd,hs)

    failures=[]

    for vdc in (0.010,0.050,0.100):
        H=M=0.0
        H,M=run_dc(H,M,vdc,1.0)
        print()
        print(f"DC pre-bias {vdc*1000:.1f} mV for 1.0 s -> H={H:.6f} M={M:.6f}")

        # Immediately observe first four cycles after removing DC.
        H,M,thd1,hs1=run_sine(H,M,4,4)
        biased_ratio=summary("first 4 AC cycles",H,M,thd1,hs1)

        # Continue to periodic state.
        H,M,thd2,hs2=run_sine(H,M,40,4)
        recovered_ratio=summary("after 40 more AC cycles",H,M,thd2,hs2)

        # Bias should materially increase even-harmonic content at least for
        # the larger bias fixtures. Recovery should reduce it again.
        if vdc>=0.050:
            if hs1[0] <= 10.0*hs2[0]:
                failures.append(f"{vdc} V: H2 did not materially decay after bias removal")
            if abs(recovered_ratio-baseline_ratio)>20.0:
                failures.append(f"{vdc} V: recovered H2/H3 remains far from baseline")

    print()
    if failures:
        print("FAIL:")
        for x in failures:
            print(" - "+x)
        return 1

    print("PASS: DC pre-bias creates transient even-order asymmetry and symmetric AC cycling returns toward the deterministic H3-dominant orbit.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
