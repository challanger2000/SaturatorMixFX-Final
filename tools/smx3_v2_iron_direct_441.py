#!/usr/bin/env python3
"""Direct 44.1 kHz IRON waveform residual vs ideal band-limited authority."""

import math
import smx3_v2_iron_candidate as ref

HOST=44100.0
AUTH_TARGET=705600.0


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
        if n>=cut:y.append(v)
    return y,fs


def bandlimit(y,fs,freq):
    N=len(y); mean=sum(y)/N
    max_h=int((0.499*HOST)//freq)
    coeff=[]
    for h in range(1,max_h+1):
        re=im=0.0
        for i,v in enumerate(y):
            a=2*math.pi*h*freq*i/fs
            re+=v*math.cos(a); im-=v*math.sin(a)
        coeff.append((h,complex(2*re/N,2*im/N)))
    return mean,coeff


def reconstruct(mean,coeff,freq,cycles=4):
    spc=int(round(HOST/freq)); N=cycles*spc; y=[]
    for n in range(N):
        t=n/HOST; v=mean
        for h,c in coeff:
            e=complex(math.cos(2*math.pi*h*freq*t),math.sin(2*math.pi*h*freq*t))
            v+=(c*e).real
        y.append(v)
    return y


def render_host(level_dbu,freq,warm=30,cycles=4):
    if abs(HOST/freq-round(HOST/freq))>1e-12:raise RuntimeError("noncoherent")
    vrms=0.775*10.0**(level_dbu/20.0)
    amp=vrms*math.sqrt(2.0); spc=int(round(HOST/freq)); dt=1/HOST
    H=M=0.0; y=[]; total=(warm+cycles)*spc; cut=warm*spc
    for n in range(total):
        t=n*dt; H,M,v=midpoint_step(t,H,M,dt,amp,freq)
        if n>=cut:y.append(v)
    return y


def residual_db(a,b):
    ma=sum(a)/len(a); mb=sum(b)/len(b)
    aa=[x-ma for x in a]; bb=[x-mb for x in b]
    err=sum((x-y)**2 for x,y in zip(aa,bb)); den=sum(y*y for y in bb)
    return 20*math.log10(max(math.sqrt(err/max(den,1e-30)),1e-30))


def main():
    cases=[(4.0,900.0),(20.0,900.0),(20.0,3675.0),(20.0,7350.0),(20.0,11025.0)]
    print("SMX-3 V2 IRON direct 44.1k waveform residual")
    print("level_dBu,freq_Hz,residual_dB")
    worst=-300.0
    for level,freq in cases:
        ya,fs=render_authority(level,freq)
        mean,c=bandlimit(ya,fs,freq)
        target=reconstruct(mean,c,freq)
        cand=render_host(level,freq)
        db=residual_db(cand,target); worst=max(worst,db)
        print(f"{level:.1f},{freq:.1f},{db:.9f}")
    print(f"worst direct 44.1k residual = {worst:.9f} dB")
    print("classification: "+("STRONG" if worst<=-80 else "PLAUSIBLE" if worst<=-60 else "WEAK"))
    return 0


if __name__=="__main__": raise SystemExit(main())
