#!/usr/bin/env python3
"""Coherent nonlinear alias-risk estimate for frozen unified SMX-3 V2 IRON.

Uses the full H/M/i_relax model at a coherent high authority rate and measures
physical harmonic energy that would fold into 44.1/48 kHz host bands when the
nonlinear core is evaluated at 1x, 2x or 4x.

This is still an analytical folding gate, not the final production
oversampling-filter residual test.
"""

import math
import cmath
import smx3_v2_iron_unified_candidate as ref

HOSTS=(44100.0,48000.0)
FACTORS=(1,2,4)
AUTH_TARGET=705600.0

CASES=(
    (20.0,1000.0),
    (20.0,5000.0),
    (20.0,10000.0),
    (4.0,1000.0),
    (4.0,5000.0),
    (4.0,10000.0),
)


def render(level_dbu,freq,warmup_cycles=40,analysis_cycles=8):
    vrms=0.775*10.0**(level_dbu/20.0)
    amp=vrms*math.sqrt(2.0)

    spc=max(64,int(round(AUTH_TARGET/freq)))
    fs=spc*freq
    dt=1.0/fs
    n=(warmup_cycles+analysis_cycles)*spc
    warm=warmup_cycles*spc
    source=lambda t: amp*math.sin(2.0*math.pi*freq*t)

    H=M=I=0.0
    y=[]
    for i in range(n):
        H,M,I,v=ref.rk4_step(i*dt,H,M,I,dt,source)
        if i>=warm:
            y.append(v)
    return y,fs


def harmonic_coeffs(y,freq,fs,max_h):
    N=len(y)
    coeff={}
    for h in range(1,max_h+1):
        z=0j
        for i,v in enumerate(y):
            a=2.0*math.pi*h*freq*i/fs
            z += v*cmath.exp(-1j*a)
        coeff[h]=2.0*z/N
    return coeff


def folded_frequency(f,fs):
    x=((f+0.5*fs)%fs)-0.5*fs
    return abs(x)


def alias_ratio(coeff,freq,host,factor):
    internal=host*factor
    host_nyq=0.5*host
    int_nyq=0.5*internal
    bins={}

    for h,c in coeff.items():
        phys=h*freq
        if phys<=int_nyq:
            continue
        af=folded_frequency(phys,internal)
        if af>host_nyq+1e-9:
            continue
        key=round(af,6)
        bins[key]=bins.get(key,0j)+c

    fund=max(abs(coeff[1]),1e-30)
    power=sum(abs(z)**2 for z in bins.values())
    ratio=math.sqrt(power)/fund
    return 20.0*math.log10(max(ratio,1e-30))


def main():
    print("SMX-3 V2 unified IRON coherent nonlinear alias-risk matrix")
    print("host,level,freq,factor,alias_dBc")

    worst={(host,f):-300.0 for host in HOSTS for f in FACTORS}

    for level,freq in CASES:
        y,auth_fs=render(level,freq)
        max_h=max(16,int((0.45*auth_fs)//freq))
        coeff=harmonic_coeffs(y,freq,auth_fs,max_h)

        for host in HOSTS:
            for factor in FACTORS:
                db=alias_ratio(coeff,freq,host,factor)
                worst[(host,factor)]=max(worst[(host,factor)],db)
                print(f"{host:.0f},{level:.1f},{freq:.1f},{factor}x,{db:.6f}")

    print()
    failures=[]
    for host in HOSTS:
        for factor in FACTORS:
            db=worst[(host,factor)]
            print(f"WORST host={host:.0f} factor={factor}x alias={db:.6f} dBc")

    # Research gate: if 1x is already <= -100 dBc at both host rates, fixed
    # oversampling is not justified by periodic-sine harmonic-fold evidence.
    for host in HOSTS:
        if worst[(host,1)]>-100.0:
            failures.append(f"{host:.0f} Hz 1x alias above -100 dBc research limit")

    if failures:
        print("FAIL:")
        for item in failures:
            print(" - "+item)
        return 1

    print("PASS: unified IRON periodic-sine fold risk supports 1x as the default architecture hypothesis.")
    print("INFO: transient/multitone and final production filter residual tests are still mandatory.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
