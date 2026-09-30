#!/usr/bin/env python3
"""Harmonic-folding alias-risk estimate for the dynamic EF86 PENTODE model.

Authority:
- coherent high-rate implicit-trapezoid dynamic EF86 circuit;
- 0.4 s physical warmup;
- direct g1 drive.

Predict foldback into a 48 kHz host band for nonlinear-core evaluation at:
- 1x = 48 kHz
- 2x = 96 kHz
- 4x = 192 kHz

An ideal low-pass back to the host band is assumed for 2x/4x. This isolates
nonlinear harmonic-fold risk from practical filter leakage.

Standard library only.
"""

import math
import smx3_v2_ef86_dynamic_reference as ref

HOST=48000.0
AUTH_TARGET=768000.0
FACTORS=(1,2,4)


def render(freq,vin_rms,warmup_seconds=0.4,analysis_cycles=4):
    # Exact coherent analysis rate near the target.
    spc=max(64,int(round(AUTH_TARGET/freq)))
    fs=spc*freq
    dt=1.0/fs
    x=ref.solve_dc()
    vin_peak=vin_rms*math.sqrt(2.0)

    # Warm for an integer number of samples; phase at analysis start need not
    # be zero because complex harmonic projection uses absolute time below.
    nw=int(round(warmup_seconds*fs))
    for n in range(nw):
        x,_=ref.trapezoid_step(n*dt,x,dt,vin_peak,freq)

    t0=nw*dt
    N=analysis_cycles*spc
    y=[]

    for n in range(N):
        t=t0+n*dt
        x,_=ref.trapezoid_step(t,x,dt,vin_peak,freq)
        y.append(x[ref.O_NODE])

    return y,fs,t0


def harmonic_coeffs(y,fs,t0,freq,max_h):
    N=len(y)
    mean=sum(y)/N
    coeff={}

    for h in range(1,max_h+1):
        re=im=0.0
        for i,v in enumerate(y):
            t=t0+(i+1)/fs
            a=2.0*math.pi*h*freq*t
            vv=v-mean
            re+=vv*math.cos(a)
            im-=vv*math.sin(a)
        coeff[h]=complex(2.0*re/N,2.0*im/N)

    return coeff


def folded_frequency(f,fs):
    return abs(((f+0.5*fs)%fs)-0.5*fs)


def alias_db(coeff,freq,factor):
    internal=HOST*factor
    int_nyq=0.5*internal
    host_nyq=0.5*HOST
    bins={}

    for h,c in coeff.items():
        physical=h*freq
        if physical<=int_nyq:
            continue
        af=folded_frequency(physical,internal)
        if af>host_nyq+1e-9:
            continue
        key=round(af,6)
        bins[key]=bins.get(key,0j)+c

    fundamental=abs(coeff[1])
    power=sum(abs(v)**2 for v in bins.values())
    ratio=math.sqrt(power)/max(fundamental,1e-30)
    return 20.0*math.log10(max(ratio,1e-30))


def main():
    # Use coherent frequencies and two drive regions: moderate and near the
    # provisional Graph-D high-output input level.
    cases=[
        ("1k moderate",1000.0,0.180),
        ("1k strong",1000.0,0.490),
        ("4k strong",4000.0,0.300),
        ("8k strong",8000.0,0.300),
        ("12k strong",12000.0,0.300),
    ]

    print("SMX-3 V2 PENTODE harmonic-fold alias-risk estimate")
    print("48 kHz host; coherent high-rate physical authority.")
    print()
    print("case,factor,alias_dBc")

    worst={f:-300.0 for f in FACTORS}

    for label,freq,vin in cases:
        y,fs,t0=render(freq,vin)
        max_h=max(16,int((0.45*fs)//freq))
        coeff=harmonic_coeffs(y,fs,t0,freq,max_h)

        for factor in FACTORS:
            db=alias_db(coeff,freq,factor)
            worst[factor]=max(worst[factor],db)
            print(f"{label},{factor}x,{db:.9f}")

    print()
    for factor in FACTORS:
        print(f"worst {factor}x = {worst[factor]:.9f} dBc")

    print("INFO: practical oversampling-filter residual and multitone/transient tests remain separate.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
