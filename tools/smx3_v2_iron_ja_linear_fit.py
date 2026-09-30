#!/usr/bin/env python3
"""Fit a minimal causal model to the low-level JA linearization.

Hypothesis from the dense correction target:
the JA small-signal transfer is approximately

    H_JA(s) = G * s / (s + wc)

i.e. one very-low-frequency first-order high-pass plus constant gain.

This structure naturally gives:
- nearly flat magnitude through the audio band;
- positive phase that decays approximately as 1/f.

The fit is evaluated against the actual stateful JA low-level solver.
"""

import math
import cmath

import smx3_v2_iron_candidate as ja


FREQS=(20.0,25.0,31.5,40.0,50.0,63.0,80.0,100.0,125.0,160.0,200.0,315.0,500.0,1000.0,2000.0,5000.0,10000.0,20000.0)


def simulate_linear(freq,level_dbu=-40.0,fs=None,warmup_cycles=30,analysis_cycles=4):
    if fs is None:
        fs=max(48000.0,96.0*freq)

    vrms=0.775*10.0**(level_dbu/20.0)
    amp=vrms*math.sqrt(2.0)
    dt=1.0/fs
    n=int(round((warmup_cycles+analysis_cycles)*fs/freq))
    start=int(round(warmup_cycles*fs/freq))

    H=M=0.0
    re=im=0.0
    count=0

    for i in range(n):
        t=i*dt
        k1h,k1m,v1=ja.deriv(t,H,M,amp,freq)
        k2h,k2m,_=ja.deriv(t+0.5*dt,H+0.5*dt*k1h,M+0.5*dt*k1m,amp,freq)
        k3h,k3m,_=ja.deriv(t+0.5*dt,H+0.5*dt*k2h,M+0.5*dt*k2m,amp,freq)
        k4h,k4m,_=ja.deriv(t+dt,H+dt*k3h,M+dt*k3m,amp,freq)

        H += dt*(k1h+2*k2h+2*k3h+k4h)/6.0
        M += dt*(k1m+2*k2m+2*k3m+k4m)/6.0

        if i>=start:
            a=2.0*math.pi*freq*(i-start)/fs
            re+=v1*math.cos(a)
            im-=v1*math.sin(a)
            count+=1

    cy=complex(re,im)
    cx=complex(0.0,-0.5*amp*count)
    return cy/cx


def hp(freq,gain,fc):
    s=1j*2.0*math.pi*freq
    wc=2.0*math.pi*fc
    return gain*s/(s+wc)


def objective(gain,fc,data):
    # Equal emphasis on magnitude dB and phase degrees.
    e=0.0
    for f,h in data:
        p=hp(f,gain,fc)
        md=20.0*math.log10(abs(p)/abs(h))
        pd=math.degrees(cmath.phase(p/h))
        e+=(md/0.01)**2+(pd/0.10)**2
    return e/len(data)


def fit(data):
    # Gain is essentially the HF asymptote; broad deterministic search.
    best=None

    for ig in range(81):
        g=0.730+0.010*ig/80.0
        for ic in range(121):
            fc=0.1*(100.0**(ic/120.0))  # 0.1..10 Hz log
            e=objective(g,fc,data)
            if best is None or e<best[0]:
                best=(e,g,fc)

    e,g,fc=best
    sg=0.0002
    sf=0.08

    for _ in range(80):
        current=objective(g,fc,data)
        improved=False

        for dg,df in ((sg,0),(-sg,0),(0,sf),(0,-sf),(sg,sf),(sg,-sf),(-sg,sf),(-sg,-sf)):
            ng=g+dg
            nf=fc+df
            if not (0.70<ng<0.80 and 0.01<nf<20.0):
                continue
            ne=objective(ng,nf,data)
            if ne<current:
                g,fc=ng,nf
                current=ne
                improved=True

        if not improved:
            sg*=0.5
            sf*=0.5
        if sg<1e-8 and sf<1e-5:
            break

    return g,fc,objective(g,fc,data)


def main():
    data=[(f,simulate_linear(f)) for f in FREQS]
    gain,fc,obj=fit(data)

    print("SMX-3 V2 JA low-level one-pole fit")
    print(f"gain = {gain:.12f}")
    print(f"fc = {fc:.9f} Hz")
    print(f"objective = {obj:.9f}")
    print()
    print("freq_Hz,JA_mag_dB,fit_mag_dB,mag_err_dB,JA_phase_deg,fit_phase_deg,phase_err_deg")

    worst_mag=0.0
    worst_phase=0.0

    for f,h in data:
        p=hp(f,gain,fc)
        mh=20.0*math.log10(abs(h))
        mp=20.0*math.log10(abs(p))
        ph=math.degrees(cmath.phase(h))
        pp=math.degrees(cmath.phase(p))
        me=mp-mh
        pe=pp-ph
        worst_mag=max(worst_mag,abs(me))
        worst_phase=max(worst_phase,abs(pe))
        print(f"{f:.1f},{mh:.9f},{mp:.9f},{me:+.9f},{ph:+.9f},{pp:+.9f},{pe:+.9f}")

    print()
    print(f"worst magnitude residual = {worst_mag:.9f} dB")
    print(f"worst phase residual = {worst_phase:.9f} deg")

    if worst_mag<=0.01 and worst_phase<=0.25:
        print("PASS: one-pole JA linearization is sufficient for realtime residual subtraction.")
    else:
        print("INFO: one pole is not sufficient under frozen realtime residual tolerances.")

    return 0


if __name__=="__main__":
    raise SystemExit(main())
