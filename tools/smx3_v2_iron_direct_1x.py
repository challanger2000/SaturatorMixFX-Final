#!/usr/bin/env python3
"""Direct 48 kHz IRON waveform residual vs ideal band-limited authority.

Authority:
- coherent ~768 kHz RK4 physical model;
- settled 30 cycles;
- Fourier-series projection;
- retain only physical components below 48 kHz host Nyquist.

Candidate:
- same physical model;
- explicit midpoint/RK2 at 48 kHz;
- no oversampling/filtering.

The residual therefore includes:
- host-rate integration error;
- nonlinear foldback/aliasing;
while excluding legitimate analog harmonics above Nyquist from the target.

Standard library only.
"""

import math
import smx3_v2_iron_candidate as ref

HOST=48000.0
AUTH_TARGET=768000.0


def rk4_step(t,H,M,dt,amp,freq):
    k1h,k1m,v=ref.deriv(t,H,M,amp,freq)
    k2h,k2m,_=ref.deriv(t+0.5*dt,H+0.5*dt*k1h,M+0.5*dt*k1m,amp,freq)
    k3h,k3m,_=ref.deriv(t+0.5*dt,H+0.5*dt*k2h,M+0.5*dt*k2m,amp,freq)
    k4h,k4m,_=ref.deriv(t+dt,H+dt*k3h,M+dt*k3m,amp,freq)
    return (
        H+dt*(k1h+2*k2h+2*k3h+k4h)/6.0,
        M+dt*(k1m+2*k2m+2*k3m+k4m)/6.0,
        v,
    )


def midpoint_step(t,H,M,dt,amp,freq):
    k1h,k1m,v=ref.deriv(t,H,M,amp,freq)
    hm=H+0.5*dt*k1h
    mm=M+0.5*dt*k1m
    k2h,k2m,_=ref.deriv(t+0.5*dt,hm,mm,amp,freq)
    return H+dt*k2h,M+dt*k2m,v


def render_authority(level_dbu,freq,warm=30,cycles=4):
    vrms=0.775*10.0**(level_dbu/20.0)
    amp=vrms*math.sqrt(2.0)
    spc=max(64,int(round(AUTH_TARGET/freq)))
    fs=spc*freq
    dt=1.0/fs
    H=M=0.0
    y=[]

    total=(warm+cycles)*spc
    cut=warm*spc
    for n in range(total):
        t=n*dt
        H,M,v=rk4_step(t,H,M,dt,amp,freq)
        if n>=cut:
            y.append(v)
    return y,fs


def fourier_bandlimit(y,fs,freq,host_fs):
    N=len(y)
    mean=sum(y)/N
    max_h=int((0.499*host_fs)//freq)
    coeff=[]

    for h in range(1,max_h+1):
        re=im=0.0
        for i,v in enumerate(y):
            a=2.0*math.pi*h*freq*i/fs
            re+=v*math.cos(a)
            im-=v*math.sin(a)
        coeff.append((h,complex(2.0*re/N,-2.0*im/N)))

    return mean,coeff


def reconstruct(mean,coeff,freq,fs,cycles=4):
    spc=int(round(fs/freq))
    N=cycles*spc
    y=[]
    for n in range(N):
        t=n/fs
        v=mean
        for h,c in coeff:
            v+=(c*complex(math.cos(2*math.pi*h*freq*t),
                          math.sin(2*math.pi*h*freq*t))).real
        y.append(v)
    return y


def render_host(level_dbu,freq,warm=30,cycles=4):
    if abs(HOST/freq-round(HOST/freq))>1e-12:
        raise RuntimeError("host test frequency must be coherent")

    vrms=0.775*10.0**(level_dbu/20.0)
    amp=vrms*math.sqrt(2.0)
    spc=int(round(HOST/freq))
    dt=1.0/HOST
    H=M=0.0
    y=[]

    total=(warm+cycles)*spc
    cut=warm*spc
    for n in range(total):
        t=n*dt
        H,M,v=midpoint_step(t,H,M,dt,amp,freq)
        if n>=cut:
            y.append(v)
    return y


def residual_db(candidate,target):
    if len(candidate)!=len(target):
        raise RuntimeError("length mismatch")
    # Remove mean independently: DC-state offsets are tracked elsewhere and
    # should not dominate the audio waveform residual.
    mc=sum(candidate)/len(candidate)
    mt=sum(target)/len(target)
    c=[v-mc for v in candidate]
    t=[v-mt for v in target]
    err=sum((a-b)**2 for a,b in zip(c,t))
    den=sum(v*v for v in t)
    ratio=math.sqrt(err/max(den,1e-30))
    return 20.0*math.log10(max(ratio,1e-30))


def main():
    cases=[
        (4.0,1000.0),
        (20.0,1000.0),
        (20.0,4000.0),
        (20.0,8000.0),
        (20.0,12000.0),
    ]

    print("SMX-3 V2 IRON direct host-rate waveform residual")
    print("Candidate: midpoint/RK2 @48k, no oversampling")
    print("Target: coherent RK4 authority, ideally band-limited to host Nyquist")
    print()
    print("level_dBu,freq_Hz,residual_dB")

    worst=-300.0
    for level,freq in cases:
        ya,fs=render_authority(level,freq)
        mean,coeff=fourier_bandlimit(ya,fs,freq,HOST)
        target=reconstruct(mean,coeff,freq,HOST)
        cand=render_host(level,freq)
        db=residual_db(cand,target)
        worst=max(worst,db)
        print(f"{level:.1f},{freq:.1f},{db:.9f}")

    print()
    print(f"worst direct 48k residual = {worst:.9f} dB")

    if worst<=-80.0:
        cls="STRONG"
    elif worst<=-60.0:
        cls="PLAUSIBLE"
    else:
        cls="WEAK"
    print(f"48k 1x direct-waveform classification: {cls}")
    print("INFO: multitone/transient and 44.1k checks remain required before final 1x freeze.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
