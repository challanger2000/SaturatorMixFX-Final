#!/usr/bin/env python3
"""Fundamental-phase / DLP probe for the corrected V2 IRON magnetic candidate.

This evaluates the FULL stateful Jiles-Atherton candidate at +4 dBu in
Jensen test-circuit-1 conditions before adding the separate HF parasitic
network.

Purpose:
- measure the magnetic core's own phase contribution;
- determine whether hysteresis/loss materially reduces the low-frequency
  phase curvature relative to an ideal pure Lm;
- avoid judging Jensen DLP from an ideal-inductor skeleton alone.

Standard library only.
"""

import math
import cmath

import smx3_v2_iron_candidate as iron
from smx3_v2_dlp_utils import dlp_degrees


FREQS=(20.0,30.0,50.0,100.0,200.0,500.0,1000.0,2000.0,5000.0,10000.0,20000.0)


def simulate_phase(freq,level_dbu=4.0,warmup_cycles=30,analysis_cycles=4):
    fs=max(48000.0,96.0*freq)
    vrms=0.775*10.0**(level_dbu/20.0)
    amp=vrms*math.sqrt(2.0)

    total_cycles=warmup_cycles+analysis_cycles
    n=int(round(total_cycles*fs/freq))
    start=int(round(warmup_cycles*fs/freq))
    dt=1.0/fs

    H=0.0
    M=0.0
    y=[]

    for i in range(n):
        t=i*dt
        k1h,k1m,v1=iron.deriv(t,H,M,amp,freq)
        k2h,k2m,_=iron.deriv(t+0.5*dt,H+0.5*dt*k1h,M+0.5*dt*k1m,amp,freq)
        k3h,k3m,_=iron.deriv(t+0.5*dt,H+0.5*dt*k2h,M+0.5*dt*k2m,amp,freq)
        k4h,k4m,_=iron.deriv(t+dt,H+dt*k3h,M+dt*k3m,amp,freq)

        H += dt*(k1h+2*k2h+2*k3h+k4h)/6.0
        M += dt*(k1m+2*k2m+2*k3m+k4m)/6.0

        if i>=start:
            y.append(v1)

    re_y=0.0
    im_y=0.0
    re_x=0.0
    im_x=0.0

    for i,v in enumerate(y):
        # analysis interval starts after an integer number of cycles, so local
        # phase is sufficient and avoids unnecessary absolute-time growth.
        a=2.0*math.pi*freq*i/fs
        re_y+=v*math.cos(a)
        im_y-=v*math.sin(a)

        x=amp*math.sin(a)
        re_x+=x*math.cos(a)
        im_x-=x*math.sin(a)

    py=math.atan2(im_y,re_y)
    px=math.atan2(im_x,re_x)
    p=py-px

    while p>math.pi:
        p-=2.0*math.pi
    while p<-math.pi:
        p+=2.0*math.pi

    return p


def main():
    phases=[simulate_phase(f) for f in FREQS]
    dlp=dlp_degrees(FREQS,phases)
    residual=dlp["residual_deg"]
    tau=dlp["delay_s"]

    print("SMX-3 V2 corrected IRON magnetic-only Jensen-DLP probe")
    print(f"best-fit delay = {1e6*tau:.9f} us")
    print("freq_Hz,raw_relative_phase_deg,DLP_residual_deg")

    for f,p,r in zip(FREQS,phases,residual):
        print(f"{f:.1f},{math.degrees(p):+.9f},{r:+.9f}")

    lo=dlp["min_deg"]
    hi=dlp["max_deg"]
    worst=dlp["worst_abs_deg"]

    print()
    print(f"residual min = {lo:+.9f} deg")
    print(f"residual max = {hi:+.9f} deg")
    print(f"worst absolute = {worst:.9f} deg")
    print("Jensen max DLP = +/-2 deg")

    # Informational: this is magnetic-only. Final DLP requires HF parasitics.
    if worst<=2.0:
        print("MAGNETIC-ONLY RESULT: already inside Jensen maximum DLP.")
    else:
        print("MAGNETIC-ONLY RESULT: exceeds Jensen maximum; HF/distributed network must compensate without harming magnitude.")

    return 0


if __name__=="__main__":
    raise SystemExit(main())
