#!/usr/bin/env python3
"""Realtime-reduction benchmark for SMX-3 V2 IRON.

Compare lower-cost explicit midpoint/RK2 at practical rates against the
settled RK4 offline authority candidate.

This does NOT decide antialiasing yet. It isolates numerical integration error
of the magnetic state.

Standard library only.
"""

import math
import smx3_v2_iron_candidate as ref


def step_mid(t,H,M,dt,amp,freq):
    k1h,k1m,_=ref.deriv(t,H,M,amp,freq)
    hm=H+0.5*dt*k1h
    mm=M+0.5*dt*k1m
    k2h,k2m,_=ref.deriv(t+0.5*dt,hm,mm,amp,freq)
    H2=H+dt*k2h
    M2=M+dt*k2m
    _,_,v=ref.deriv(t+dt,H2,M2,amp,freq)
    return H2,M2,v


def simulate_mid(level_dbu,freq,fs,warmup_cycles=30,analysis_cycles=4):
    vrms=0.775*10.0**(level_dbu/20.0)
    amp=vrms*math.sqrt(2.0)
    total=warmup_cycles+analysis_cycles
    n=int(round(total*fs/freq))
    warm=int(round(warmup_cycles*fs/freq))
    dt=1.0/fs
    H=M=0.0
    y=[]

    for i in range(n):
        t=i*dt
        H,M,v=step_mid(t,H,M,dt,amp,freq)
        if i>=warm:
            y.append(v)

    N=len(y)

    def comp(h):
        re=im=0.0
        for i,v in enumerate(y):
            a=2.0*math.pi*h*freq*i/fs
            re+=v*math.cos(a)
            im-=v*math.sin(a)
        return math.hypot(re,im)

    f1=comp(1)
    hs=[comp(h)/f1 for h in range(2,11)]
    thd=math.sqrt(sum(h*h for h in hs))
    return thd,hs


def main():
    cases=[
        (4.0,20.0),
        (20.0,20.0),
        (4.0,50.0),
        (20.0,50.0),
        (4.0,100.0),
        (20.0,100.0),
        (20.0,1000.0),
    ]

    rates=(48000.0,96000.0,192000.0)

    print("SMX-3 V2 IRON realtime-integration reduction benchmark")
    print("Reference: RK4 @ 192 kHz; candidates: midpoint/RK2.")
    print()
    print("level_dBu,freq_Hz,fs_Hz,THD_ref_pct,THD_candidate_pct,THD_residual_pp,H3_residual_pp")

    worst={fs:{"thd":0.0,"h3":0.0} for fs in rates}

    for level,freq in cases:
        rthd,rhs=ref.simulate(level,freq,fs=192000.0,warmup_cycles=30,analysis_cycles=4)
        for fs in rates:
            cthd,chs=simulate_mid(level,freq,fs)
            dthd=100.0*abs(cthd-rthd)
            dh3=100.0*abs(chs[1]-rhs[1])
            worst[fs]["thd"]=max(worst[fs]["thd"],dthd)
            worst[fs]["h3"]=max(worst[fs]["h3"],dh3)
            print(
                f"{level:.1f},{freq:.1f},{fs:.0f},"
                f"{100*rthd:.9f},{100*cthd:.9f},{dthd:.9f},{dh3:.9f}"
            )

    print()
    print("WORST RESIDUALS")
    for fs in rates:
        print(
            f"{fs:.0f} Hz: THD={worst[fs]['thd']:.9f} pp "
            f"H3={worst[fs]['h3']:.9f} pp"
        )

    # Research classification, not production release gate.
    for fs in rates:
        if worst[fs]["thd"]<=0.002 and worst[fs]["h3"]<=0.002:
            cls="STRONG"
        elif worst[fs]["thd"]<=0.01 and worst[fs]["h3"]<=0.01:
            cls="PLAUSIBLE"
        else:
            cls="WEAK"
        print(f"{fs:.0f} Hz midpoint candidate: {cls}")

    return 0


if __name__=="__main__":
    raise SystemExit(main())
