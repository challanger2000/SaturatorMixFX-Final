#!/usr/bin/env python3
"""Transient + multitone host-rate residual gate for frozen unified SMX-3 V2 IRON.

Compares host-rate midpoint/RK2 output against an 8x RK4 authority rendered
from the same excitation. The authority is downsampled at exactly matching
physical sample times; no production anti-alias filter is assumed here.

Purpose:
- catch state/update errors hidden by periodic sine analysis;
- exercise nonstationary flux excursions and intermodulation;
- quantify direct waveform residual at 44.1/48 kHz.

This is a research architecture gate, not the final C++ release gate.
"""

import math
import random
import smx3_v2_iron_unified_candidate as ref

HOSTS=(44100.0,48000.0)
AUTH_FACTOR=8
LEVEL_DBU=20.0


def step_mid(t,H,M,I,dt,source):
    v1=source(t)
    k1h,k1m,k1i,_,_=ref.deriv_source(H,M,I,v1)
    tm=t+0.5*dt
    vm=source(tm)
    k2h,k2m,k2i,_,_=ref.deriv_source(
        H+0.5*dt*k1h,
        M+0.5*dt*k1m,
        I+0.5*dt*k1i,
        vm,
    )
    H2=H+dt*k2h
    M2=M+dt*k2m
    I2=I+dt*k2i
    ve=source(t+dt)
    _,_,_,vout,_=ref.deriv_source(H2,M2,I2,ve)
    return H2,M2,I2,vout


def render_host(source,duration,fs):
    dt=1.0/fs
    n=int(round(duration*fs))
    H=M=I=0.0
    y=[]
    for i in range(n):
        H,M,I,v=step_mid(i*dt,H,M,I,dt,source)
        y.append(v)
    return y


def render_auth_at_host_times(source,duration,host_fs):
    fs=host_fs*AUTH_FACTOR
    dt=1.0/fs
    n_host=int(round(duration*host_fs))
    H=M=I=0.0
    y=[]
    for ih in range(n_host):
        v=None
        base=ih*AUTH_FACTOR
        for k in range(AUTH_FACTOR):
            i=base+k
            H,M,I,v=ref.rk4_step(i*dt,H,M,I,dt,source)
        y.append(v)
    return y


def rms(x):
    return math.sqrt(sum(v*v for v in x)/max(len(x),1))


def peak(x):
    return max((abs(v) for v in x),default=0.0)


def residual_metrics(a,b):
    e=[x-y for x,y in zip(a,b)]
    ar=rms(a)
    er=rms(e)
    db=20.0*math.log10(max(er/max(ar,1e-30),1e-30))
    pk=peak(e)
    pkdb=20.0*math.log10(max(pk/max(peak(a),1e-30),1e-30))
    return db,pkdb


def source_multitone():
    vrms=0.775*10.0**(LEVEL_DBU/20.0)
    peak_total=vrms*math.sqrt(2.0)
    freqs=(41.0,73.0,131.0,257.0,503.0,1009.0,2017.0,4013.0,7993.0,11987.0)
    phases=(0.1,1.3,2.1,0.7,2.8,1.8,0.4,2.5,1.1,2.9)
    scale=peak_total/len(freqs)*2.0
    def src(t):
        return scale*sum(math.sin(2.0*math.pi*f*t+p) for f,p in zip(freqs,phases))
    return src


def source_burst():
    vrms=0.775*10.0**(LEVEL_DBU/20.0)
    amp=vrms*math.sqrt(2.0)
    def env(t):
        if t<0.050:
            return 0.0
        if t<0.055:
            return (t-0.050)/0.005
        if t<0.180:
            return 1.0
        if t<0.220:
            return max(0.0,1.0-(t-0.180)/0.040)
        if t<0.300:
            return 0.0
        if t<0.305:
            return (t-0.300)/0.005
        if t<0.420:
            return 1.0
        if t<0.460:
            return max(0.0,1.0-(t-0.420)/0.040)
        return 0.0
    def src(t):
        carrier=(
            0.70*math.sin(2.0*math.pi*55.0*t)
            +0.22*math.sin(2.0*math.pi*997.0*t+0.7)
            +0.08*math.sin(2.0*math.pi*7013.0*t+1.2)
        )
        return amp*env(t)*carrier
    return src


def source_step_chirp():
    """Fast but band-limited-ish transient followed by a continuous chirp.

    The former version used ideal voltage steps. Those contain infinite
    bandwidth, so host-rate and 8x renderers were not being driven by the same
    realizable audio-band stimulus. Raised-cosine edges keep this a valid
    realtime architecture comparison while remaining deliberately abrupt.
    """
    vrms=0.775*10.0**(LEVEL_DBU/20.0)
    amp=vrms*math.sqrt(2.0)

    def rc(x):
        if x<=0.0:
            return 0.0
        if x>=1.0:
            return 1.0
        return 0.5-0.5*math.cos(math.pi*x)

    def pulse(t,start,hold,edge,sign):
        a=rc((t-start)/edge)
        b=rc((start+edge+hold+edge-t)/edge)
        return sign*a*b

    def src(t):
        # Two opposite, fast 2 ms raised-cosine transients.
        p=0.78*pulse(t,0.040,0.030,0.002,+1.0)
        p+=0.78*pulse(t,0.085,0.030,0.002,-1.0)

        # Continuous raised-cosine-gated chirp, 30 Hz -> 12 kHz.
        start=0.140
        dur=0.360
        tt=t-start
        if 0.0<=tt<=dur:
            gate=rc(tt/0.003)*rc((dur-tt)/0.003)
            f0=30.0
            f1=12000.0
            k=(f1-f0)/dur
            ph=2.0*math.pi*(f0*tt+0.5*k*tt*tt)
            p+=0.65*gate*math.sin(ph)

        return amp*p
    return src


def main():
    cases=(
        ("multitone",source_multitone(),0.50),
        ("burst",source_burst(),0.55),
        ("fast_transient_chirp",source_step_chirp(),0.55),
    )

    print("SMX-3 V2 unified IRON transient/multitone host-rate residual gate")
    print("host,case,rms_residual_dBc,peak_residual_dBc")

    failures=[]
    worst_rms=-300.0
    worst_peak=-300.0

    for fs in HOSTS:
        for name,source,duration in cases:
            auth=render_auth_at_host_times(source,duration,fs)
            host=render_host(source,duration,fs)
            rdb,pdb=residual_metrics(auth,host)
            worst_rms=max(worst_rms,rdb)
            worst_peak=max(worst_peak,pdb)
            print(f"{fs:.0f},{name},{rdb:.6f},{pdb:.6f}")

            if rdb>-90.0:
                failures.append(f"{fs:.0f} {name} RMS residual above -90 dBc")
            if pdb>-70.0:
                failures.append(f"{fs:.0f} {name} peak residual above -70 dBc")

    print()
    print(f"WORST RMS residual = {worst_rms:.6f} dBc")
    print(f"WORST peak residual = {worst_peak:.6f} dBc")

    if failures:
        print("FAIL:")
        for item in failures:
            print(" - "+item)
        return 1

    print("PASS: host-rate midpoint/RK2 tracks 8x RK4 authority on transient and multitone excitation.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
