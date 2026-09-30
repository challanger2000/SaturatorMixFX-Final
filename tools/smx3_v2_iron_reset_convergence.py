#!/usr/bin/env python3
"""Reset/startup convergence probe for the SMX-3 V2 IRON candidate.

Measures cycle-by-cycle waveform residual from canonical H=M=0 startup toward
the settled periodic orbit.

This directly informs VST3 reset/activate/state-restore policy.

Standard library only.
"""

import math
import smx3_v2_iron_candidate as ref


def rk4_step(t,H,M,dt,amp,freq):
    k1h,k1m,v1=ref.deriv(t,H,M,amp,freq)
    k2h,k2m,_=ref.deriv(t+0.5*dt,H+0.5*dt*k1h,M+0.5*dt*k1m,amp,freq)
    k3h,k3m,_=ref.deriv(t+0.5*dt,H+0.5*dt*k2h,M+0.5*dt*k2m,amp,freq)
    k4h,k4m,_=ref.deriv(t+dt,H+dt*k3h,M+dt*k3m,amp,freq)
    H += dt*(k1h+2*k2h+2*k3h+k4h)/6.0
    M += dt*(k1m+2*k2m+2*k3m+k4m)/6.0
    return H,M,v1


def cycle_metrics(y,refy):
    if len(y)!=len(refy):
        raise RuntimeError("cycle length mismatch")
    num=sum((a-b)*(a-b) for a,b in zip(y,refy))
    den=sum(b*b for b in refy)
    rel=math.sqrt(num/max(den,1e-30))
    db=20.0*math.log10(max(rel,1e-30))
    return rel,db


def harmonic_ratio(y,h):
    N=len(y)
    re=im=0.0
    for i,v in enumerate(y):
        a=2.0*math.pi*h*i/N
        re+=v*math.cos(a)
        im-=v*math.sin(a)
    return math.hypot(re,im)


def simulate_cycles(level_dbu,freq,fs=48000.0,total_cycles=48):
    vrms=0.775*10.0**(level_dbu/20.0)
    amp=vrms*math.sqrt(2.0)
    spc=max(8,int(round(fs/freq)))
    # Use an exact-cycle integration rate to keep phase alignment deterministic.
    fs_eff=spc*freq
    dt=1.0/fs_eff

    H=M=0.0
    cycles=[]

    for cyc in range(total_cycles):
        y=[]
        base=cyc*spc
        for n in range(spc):
            t=(base+n)*dt
            H,M,v=rk4_step(t,H,M,dt,amp,freq)
            y.append(v)
        cycles.append(y)

    return cycles


def main():
    cases=[
        (4.0,20.0),
        (20.0,20.0),
        (4.0,100.0),
        (20.0,100.0),
        (20.0,1000.0),
    ]

    print("SMX-3 V2 IRON reset/startup periodic-state convergence")
    print("Canonical reset: H=M=0")
    print()
    print("level_dBu,freq_Hz,cycle,residual_dB,H2_over_H3_dB")

    worst_first=-300.0
    max_cycles_60=0
    max_cycles_80=0

    for level,freq in cases:
        cycles=simulate_cycles(level,freq)
        refy=cycles[-1]

        c60=None
        c80=None

        for idx,y in enumerate(cycles[:-1],start=1):
            _,db=cycle_metrics(y,refy)
            h2=harmonic_ratio(y,2)
            h3=harmonic_ratio(y,3)
            ratio=20.0*math.log10(max(h2,1e-30)/max(h3,1e-30))

            if idx in (1,2,4,8,16,24,32,40):
                print(f"{level:.1f},{freq:.1f},{idx},{db:.6f},{ratio:.6f}")

            if c60 is None and db<=-60.0:
                c60=idx
            if c80 is None and db<=-80.0:
                c80=idx

        first_db=cycle_metrics(cycles[0],refy)[1]
        worst_first=max(worst_first,first_db)
        if c60 is None:c60=999
        if c80 is None:c80=999
        max_cycles_60=max(max_cycles_60,c60)
        max_cycles_80=max(max_cycles_80,c80)

        print(f"SUMMARY {level:.1f}dBu {freq:.1f}Hz: first={first_db:.3f}dB c60={c60} c80={c80}")

    print()
    print(f"worst first-cycle residual = {worst_first:.6f} dB")
    print(f"worst cycles to <=-60 dB = {max_cycles_60}")
    print(f"worst cycles to <=-80 dB = {max_cycles_80}")

    print("INFO: use these results to choose reset/crossfade policy; this is not yet a release gate.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
