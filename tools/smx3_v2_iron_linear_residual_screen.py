#!/usr/bin/env python3
"""Linear-target + nonlinear-JA residual architecture screen for SMX-3 V2 IRON.

Architecture under test:

    y = L_Jensen{x} + ( y_JA - L_JA{x} )

where:
- L_Jensen is the validated loss-aware JT-11P-1 small-signal target;
- y_JA is the full stateful nonlinear Jiles-Atherton output;
- L_JA is the measured low-level linearization of the SAME JA model.

This is not a memoryless waveshaper split:
the nonlinear residual still comes from the full stateful JA trajectory.

Purpose:
determine whether replacing only the incorrect JA small-signal linear component
preserves the independently validated nonlinear evidence:
- +4 dBu / 20 Hz THD ~0.025%;
- +20 dBu / 20 Hz THD ~1%;
- H3 dominance;
- low-level THD frequency law.

For this offline sinusoidal screen the linear correction is synthesized at the
fundamental from the exact complex transfer difference. A later production
implementation would require a causal time-domain realization of both linear
operators.
"""

import math
import cmath

import smx3_v2_iron_candidate as ja
import smx3_v2_jensen_lossaware_target as target


def simulate_wave(level_dbu,freq,fs=None,warmup_cycles=30,analysis_cycles=4):
    if fs is None:
        fs=max(48000.0,96.0*freq)

    vrms=0.775*10.0**(level_dbu/20.0)
    amp=vrms*math.sqrt(2.0)
    total=warmup_cycles+analysis_cycles
    n=int(round(total*fs/freq))
    start=int(round(warmup_cycles*fs/freq))
    dt=1.0/fs

    H=0.0
    M=0.0
    y=[]

    for i in range(n):
        t=i*dt
        k1h,k1m,v1=ja.deriv(t,H,M,amp,freq)
        k2h,k2m,_=ja.deriv(t+0.5*dt,H+0.5*dt*k1h,M+0.5*dt*k1m,amp,freq)
        k3h,k3m,_=ja.deriv(t+0.5*dt,H+0.5*dt*k2h,M+0.5*dt*k2m,amp,freq)
        k4h,k4m,_=ja.deriv(t+dt,H+dt*k3h,M+dt*k3m,amp,freq)

        H += dt*(k1h+2*k2h+2*k3h+k4h)/6.0
        M += dt*(k1m+2*k2m+2*k3m+k4m)/6.0

        if i>=start:
            y.append(v1)

    return amp,fs,y


def component(y,h,freq,fs):
    re=0.0
    im=0.0
    for i,v in enumerate(y):
        a=2.0*math.pi*h*freq*i/fs
        re+=v*math.cos(a)
        im-=v*math.sin(a)
    return complex(re,im)


def transfer_from_wave(amp,freq,fs,y):
    cy=component(y,1,freq,fs)
    # Local analysis starts after an integer number of cycles.
    # Input x=A*sin(theta) -> Cx=-j*A*N/2.
    cx=complex(0.0,-0.5*amp*len(y))
    return cy/cx


def ja_linear_transfer(freq):
    # Very low level: nonlinear harmonics become negligible while the same
    # state/circuit topology is retained.
    amp,fs,y=simulate_wave(-40.0,freq,warmup_cycles=30,analysis_cycles=4)
    return transfer_from_wave(amp,freq,fs,y)


def corrected_wave(level_dbu,freq):
    amp,fs,y=simulate_wave(level_dbu,freq,warmup_cycles=30,analysis_cycles=4)

    h_ja_lin=ja_linear_transfer(freq)
    h_target=target.transfer(freq,True)
    dh=h_target-h_ja_lin

    out=[]
    for i,v in enumerate(y):
        a=2.0*math.pi*freq*i/fs
        # For H=hr+j*hi and sine input:
        # H{x}=A*(hr*sin(theta)+hi*cos(theta)).
        corr=amp*(dh.real*math.sin(a)+dh.imag*math.cos(a))
        out.append(v+corr)

    return amp,fs,y,out,h_ja_lin,h_target


def analyze(y,freq,fs):
    c1=component(y,1,freq,fs)
    f1=abs(c1)
    hs=[abs(component(y,h,freq,fs))/f1 for h in range(2,11)]
    thd=math.sqrt(sum(x*x for x in hs))
    rms=math.sqrt(sum(v*v for v in y)/len(y))
    phase=cmath.phase(c1)+math.pi/2.0
    while phase>math.pi: phase-=2.0*math.pi
    while phase<-math.pi: phase+=2.0*math.pi
    return thd,hs,rms,phase


def main():
    cases=[
        (4.0,20.0),
        (20.0,20.0),
        (4.0,40.0),
        (4.0,80.0),
    ]

    print("SMX-3 V2 IRON linear-target + nonlinear-JA residual screen")
    print("level_dBu,freq_Hz,JA_THD_pct,corr_THD_pct,JA_H2_pct,corr_H2_pct,JA_H3_pct,corr_H3_pct,JA_gain_dB,corr_gain_dB")

    results={}

    for level,freq in cases:
        amp,fs,y,yc,hlin,ht=corrected_wave(level,freq)
        a=analyze(y,freq,fs)
        b=analyze(yc,freq,fs)

        in_rms=amp/math.sqrt(2.0)
        ga=20.0*math.log10(a[2]/in_rms)
        gb=20.0*math.log10(b[2]/in_rms)

        results[(level,freq)]=(a,b)

        print(
            f"{level:.1f},{freq:.1f},"
            f"{100*a[0]:.9f},{100*b[0]:.9f},"
            f"{100*a[1][0]:.9f},{100*b[1][0]:.9f},"
            f"{100*a[1][1]:.9f},{100*b[1][1]:.9f},"
            f"{ga:.9f},{gb:.9f}"
        )

        if level==4.0:
            print(
                f"  linear transfers @ {freq:g} Hz: "
                f"JA={20*math.log10(abs(hlin)):+.6f}dB/{math.degrees(cmath.phase(hlin)):+.6f}deg "
                f"Target={20*math.log10(abs(ht)):+.6f}dB/{math.degrees(cmath.phase(ht)):+.6f}deg"
            )

    low=100.0*results[(4.0,20.0)][1][0]
    high=100.0*results[(20.0,20.0)][1][0]
    h2=results[(4.0,20.0)][1][1][0]
    h3=results[(4.0,20.0)][1][1][1]

    thd20=results[(4.0,20.0)][1][0]
    thd40=results[(4.0,40.0)][1][0]
    thd80=results[(4.0,80.0)][1][0]

    q1=thd40/thd20
    q2=thd80/thd40

    print()
    print(f"corrected +4 dBu / 20 Hz THD = {low:.9f}%")
    print(f"corrected +20 dBu / 20 Hz THD = {high:.9f}%")
    print(f"corrected H2/H3 ratio = {20*math.log10(max(h2,1e-30)/max(h3,1e-30)):.6f} dB")
    print(f"corrected low-level THD octave ratios = {q1:.6f}, {q2:.6f}")

    failures=[]
    if not (0.020<=low<=0.030):
        failures.append("+4 dBu / 20 Hz THD")
    if not (0.95<=high<=1.05):
        failures.append("+20 dBu / 20 Hz THD")
    if h2>=0.1*h3:
        failures.append("H3 dominance")
    if not (0.18<=q1<=0.35):
        failures.append("20->40 Hz THD law")
    if not (0.18<=q2<=0.35):
        failures.append("40->80 Hz THD law")

    if failures:
        print("REJECT:")
        for f in failures:
            print(" - "+f)
        return 0

    print("PASS: replacing only the JA linear component preserves first-order nonlinear Jensen evidence.")
    print("NEXT: identify causal realtime L_JA and L_Jensen realizations, then rerun state/remanence and multilevel regression.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
