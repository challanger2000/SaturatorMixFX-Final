#!/usr/bin/env python3
"""Dense complex correction target C(f)=L_Jensen(f)-L_JA(f) for SMX-3 V2 IRON.

This tool measures the low-level linearized JA transfer with the same stateful
solver and subtracts it from the validated Jensen loss-aware small-signal target.

The resulting additive correction is what a realtime linear filter must realize:

    y = y_JA + C{x}

This is equivalent to:
    y = L_Jensen{x} + (y_JA - L_JA{x})

but requires only one extra linear correction path at runtime.
"""

import math
import cmath

import smx3_v2_iron_candidate as ja
import smx3_v2_jensen_lossaware_target as target


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
            re += v1*math.cos(a)
            im -= v1*math.sin(a)
            count += 1

    cy=complex(re,im)
    cx=complex(0.0,-0.5*amp*count)
    return cy/cx


def main():
    n=97
    f0=20.0
    f1=20000.0
    freqs=[f0*(f1/f0)**(i/(n-1)) for i in range(n)]

    print("SMX-3 V2 IRON additive linear-correction target")
    print("freq_Hz,JA_re,JA_im,Jensen_re,Jensen_im,C_re,C_im,C_mag_dB,C_phase_deg")

    maxmag=(0.0,None)
    for f in freqs:
        hj=simulate_linear(f)
        ht=target.transfer(f,True)
        c=ht-hj
        mag=abs(c)
        if mag>maxmag[0]:
            maxmag=(mag,f)

        mdb=-300.0 if mag<1e-15 else 20.0*math.log10(mag)
        ph=math.degrees(cmath.phase(c)) if mag>=1e-15 else 0.0
        print(
            f"{f:.9f},"
            f"{hj.real:.12g},{hj.imag:.12g},"
            f"{ht.real:.12g},{ht.imag:.12g},"
            f"{c.real:.12g},{c.imag:.12g},"
            f"{mdb:.9f},{ph:.9f}"
        )

    print()
    print(f"maximum |C| = {20*math.log10(maxmag[0]):.6f} dB at {maxmag[1]:.3f} Hz")
    print("INFO: correction is an additive transfer, so its dB magnitude is not a gain-error dB.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
