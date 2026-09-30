#!/usr/bin/env python3
"""Harmonic-folding alias-risk estimate for SMX-3 V2 IRON.

Uses a high-rate settled physical reference waveform, extracts complex
harmonics, then predicts which physical harmonics would fold into the 48 kHz
host audio band if the nonlinear core itself were evaluated at 1x/2x/4x.

This isolates nonlinear sampling alias risk. It assumes an ideal low-pass
before returning an oversampled 2x/4x result to the 48 kHz host.

Standard library only.
"""

import math
import cmath
import smx3_v2_iron_candidate as ref

HOST=48000.0
AUTH_FS_TARGET=768000.0
FACTORS=(1,2,4)


def render(level_dbu,freq,warmup_cycles=30,analysis_cycles=4):
    vrms=0.775*10.0**(level_dbu/20.0)
    amp=vrms*math.sqrt(2.0)

    # Make the analysis EXACTLY coherent: integer samples per fundamental
    # cycle. The former fixed 768 kHz rate gave 153.6 samples/cycle at 5 kHz
    # and 76.8 at 10 kHz, which leaked fundamental energy into harmonic bins.
    spc=max(32,int(round(AUTH_FS_TARGET/freq)))
    fs=spc*freq
    n=(warmup_cycles+analysis_cycles)*spc
    warm=warmup_cycles*spc
    dt=1.0/fs
    H=M=0.0
    y=[]

    for i in range(n):
        t=i*dt
        k1h,k1m,v1=ref.deriv(t,H,M,amp,freq)
        k2h,k2m,_=ref.deriv(t+0.5*dt,H+0.5*dt*k1h,M+0.5*dt*k1m,amp,freq)
        k3h,k3m,_=ref.deriv(t+0.5*dt,H+0.5*dt*k2h,M+0.5*dt*k2m,amp,freq)
        k4h,k4m,_=ref.deriv(t+dt,H+dt*k3h,M+dt*k3m,amp,freq)
        H += dt*(k1h+2*k2h+2*k3h+k4h)/6.0
        M += dt*(k1m+2*k2m+2*k3m+k4m)/6.0
        if i>=warm:
            y.append(v1)

    return y,fs


def harmonic_coeffs(y,freq,fs,max_h):
    # The analysis window contains an exact integer number of cycles.
    N=len(y)
    coeff={}
    for h in range(1,max_h+1):
        re=im=0.0
        for i,v in enumerate(y):
            a=2.0*math.pi*h*freq*i/fs
            re+=v*math.cos(a)
            im-=v*math.sin(a)
        coeff[h]=complex(re,-im)*2.0/N
    return coeff


def folded_frequency(f,fs):
    # Return nonnegative alias frequency in [0, fs/2].
    x=((f+0.5*fs)%fs)-0.5*fs
    return abs(x)


def alias_ratio(coeff,freq,factor):
    internal=HOST*factor
    host_nyq=0.5*HOST
    int_nyq=0.5*internal

    bins={}
    contributors=[]

    for h,c in coeff.items():
        phys=h*freq
        if phys<=int_nyq:
            continue
        af=folded_frequency(phys,internal)
        if af>host_nyq+1e-9:
            continue
        # DC aliases are included; bin to exact harmonic-derived frequency.
        key=round(af,6)
        # A frequency reflection can conjugate spectral orientation; for power
        # risk estimation phase sign is secondary, but complex summation still
        # avoids blindly adding amplitudes.
        bins[key]=bins.get(key,0j)+c
        contributors.append((h,phys,af,abs(c)))

    fundamental=abs(coeff[1])
    alias_power=sum(abs(c)**2 for c in bins.values())
    ratio=math.sqrt(alias_power)/max(fundamental,1e-30)
    db=20.0*math.log10(max(ratio,1e-30))
    return db,contributors


def main():
    cases=[
        (20.0,1000.0),
        (20.0,5000.0),
        (20.0,10000.0),
    ]

    print("SMX-3 V2 IRON harmonic-folding alias-risk estimate")
    print("Host=48k; authority uses coherent ~768k integration; ideal return LPF assumed for 2x/4x.")
    print()
    print("level_dBu,freq_Hz,factor,alias_dBc,contributors")

    worst={f:-300.0 for f in FACTORS}

    for level,freq in cases:
        y,auth_fs=render(level,freq)
        max_h=max(16,int((0.45*auth_fs)//freq))
        coeff=harmonic_coeffs(y,freq,auth_fs,max_h)

        for factor in FACTORS:
            db,contrib=alias_ratio(coeff,freq,factor)
            worst[factor]=max(worst[factor],db)
            print(f"{level:.1f},{freq:.1f},{factor}x,{db:.6f},{len(contrib)}")

    print()
    for factor in FACTORS:
        print(f"worst {factor}x estimated nonlinear-fold alias = {worst[factor]:.6f} dBc")

    print()
    print("INFO: this is a physical-harmonic folding estimate, not a substitute for final oversampling-filter residual tests.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
