#!/usr/bin/env python3
"""Independent numerical-method cross-check for the provisional IRON candidate.

Compares:
- production-research reference: RK4;
- independent explicit midpoint (RK2) at elevated integration rate.

The purpose is numerical credibility of the OFFLINE candidate, not realtime
architecture selection.

Standard library only.
"""

import math
import smx3_v2_iron_candidate as ref


def step_midpoint(t,H,M,dt,amp,freq):
    k1h,k1m,_=ref.deriv(t,H,M,amp,freq)
    hm=H+0.5*dt*k1h
    mm=M+0.5*dt*k1m
    k2h,k2m,_=ref.deriv(t+0.5*dt,hm,mm,amp,freq)
    H2=H+dt*k2h
    M2=M+dt*k2m
    _,_,vout=ref.deriv(t+dt,H2,M2,amp,freq)
    return H2,M2,vout


def simulate_midpoint(level_dbu,freq=20.0,fs=192000.0,warmup_cycles=30,analysis_cycles=4):
    vrms=0.775*10.0**(level_dbu/20.0)
    amp=vrms*math.sqrt(2.0)
    total_cycles=warmup_cycles+analysis_cycles
    n=int(round(total_cycles*fs/freq))
    warm_samples=int(round(warmup_cycles*fs/freq))
    dt=1.0/fs

    H=0.0
    M=0.0
    y=[]

    for i in range(n):
        t=i*dt
        H,M,vout=step_midpoint(t,H,M,dt,amp,freq)
        if i>=warm_samples:
            y.append(vout)

    N=len(y)

    def component(h):
        re=0.0
        im=0.0
        for i,v in enumerate(y):
            a=2.0*math.pi*h*freq*i/fs
            re+=v*math.cos(a)
            im-=v*math.sin(a)
        return math.hypot(re,im)

    fundamental=component(1)
    hs=[component(h)/fundamental for h in range(2,11)]
    thd=math.sqrt(sum(v*v for v in hs))
    return thd,hs


def main():
    print("SMX-3 V2 IRON numerical-method cross-check")
    print("RK4 candidate @48 kHz vs explicit midpoint/RK2 @192 kHz")
    print()
    print("case,RK4_THD_pct,midpoint_THD_pct,residual_pp,H3_residual_pp")

    failures=[]

    cases=[
        ("20Hz +4dBu",4.0,20.0),
        ("20Hz +20dBu",20.0,20.0),
        ("40Hz +4dBu",4.0,40.0),
    ]

    for label,level,freq in cases:
        rk4_thd,rk4_hs=ref.simulate(level,freq,fs=48000.0,warmup_cycles=30,analysis_cycles=4)
        mid_thd,mid_hs=simulate_midpoint(level,freq=freq,fs=192000.0,warmup_cycles=30,analysis_cycles=4)

        thd_pp=100.0*abs(mid_thd-rk4_thd)
        h3_pp=100.0*abs(mid_hs[1]-rk4_hs[1])

        print(
            f"{label},{100*rk4_thd:.9f},{100*mid_thd:.9f},"
            f"{thd_pp:.9f},{h3_pp:.9f}"
        )

        if thd_pp>0.003:
            failures.append(label+" THD residual")
        if h3_pp>0.003:
            failures.append(label+" H3 residual")

    print()
    if failures:
        print("FAIL: IRON numerical-method disagreement")
        for f in failures:
            print(" - "+f)
        return 1

    print("PASS: 48 kHz RK4 candidate and 192 kHz independent midpoint reference agree within frozen offline tolerances.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
