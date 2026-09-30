#!/usr/bin/env python3
"""Realtime-rate matrix for the frozen unified SMX-3 V2 IRON candidate.

Compares explicit midpoint/RK2 host-rate integration of the full H/M/i_relax
state against a coherent high-rate RK4 authority. This isolates state/update
rate error before any final production antialias/filter implementation.

Standard library only.
"""

import math
import cmath
import smx3_v2_iron_unified_candidate as ref

RATES=(44100.0,48000.0,96000.0,192000.0)
AUTH_FACTOR=8

CASES=(
    (4.0,20.0),
    (20.0,20.0),
    (4.0,50.0),
    (20.0,50.0),
    (4.0,100.0),
    (20.0,100.0),
    (20.0,1000.0),
    (20.0,5000.0),
    (20.0,10000.0),
)


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


def render_mid(level_dbu,freq,fs,warmup_cycles=40,analysis_cycles=6):
    vrms=0.775*10.0**(level_dbu/20.0)
    amp=vrms*math.sqrt(2.0)
    dt=1.0/fs
    total=warmup_cycles+analysis_cycles
    n=int(round(total*fs/freq))
    warm=int(round(warmup_cycles*fs/freq))
    source=lambda t: amp*math.sin(2.0*math.pi*freq*t)

    H=M=I=0.0
    y=[]
    for i in range(n):
        H,M,I,v=step_mid(i*dt,H,M,I,dt,source)
        if i>=warm:
            y.append(v)
    return y


def render_rk4(level_dbu,freq,fs,warmup_cycles=40,analysis_cycles=6):
    vrms=0.775*10.0**(level_dbu/20.0)
    amp=vrms*math.sqrt(2.0)
    dt=1.0/fs
    total=warmup_cycles+analysis_cycles
    n=int(round(total*fs/freq))
    warm=int(round(warmup_cycles*fs/freq))
    source=lambda t: amp*math.sin(2.0*math.pi*freq*t)

    H=M=I=0.0
    y=[]
    for i in range(n):
        H,M,I,v=ref.rk4_step(i*dt,H,M,I,dt,source)
        if i>=warm:
            y.append(v)
    return y


def harmonic_metrics(y,freq,fs,max_h=10):
    N=len(y)
    coeff=[]
    for h in range(1,max_h+1):
        z=0j
        for i,v in enumerate(y):
            a=2.0*math.pi*h*freq*i/fs
            z += v*cmath.exp(-1j*a)
        coeff.append(2.0*z/N)

    fund=max(abs(coeff[0]),1e-30)
    hs=[abs(z)/fund for z in coeff[1:]]
    thd=math.sqrt(sum(x*x for x in hs))
    return coeff[0],thd,hs


def main():
    print("SMX-3 V2 unified IRON realtime-rate matrix")
    print("candidate=midpoint/RK2 at host rate; authority=RK4 at 8x candidate rate")
    print("rate,level,freq,mag_res_dB,phase_res_deg,THD_res_pp,H3_res_pp")

    worst={fs:{"mag":0.0,"phase":0.0,"thd":0.0,"h3":0.0} for fs in RATES}

    for fs in RATES:
        auth_fs=fs*AUTH_FACTOR
        for level,freq in CASES:
            y_ref=render_rk4(level,freq,auth_fs)
            y_mid=render_mid(level,freq,fs)
            c_ref,t_ref,h_ref=harmonic_metrics(y_ref,freq,auth_fs)
            c_mid,t_mid,h_mid=harmonic_metrics(y_mid,freq,fs)

            mag_res=abs(20.0*math.log10(max(abs(c_mid),1e-30)/max(abs(c_ref),1e-30)))
            phase_res=abs(math.degrees(cmath.phase(c_mid/c_ref)))
            thd_res=100.0*abs(t_mid-t_ref)
            h3_res=100.0*abs(h_mid[1]-h_ref[1])

            w=worst[fs]
            w["mag"]=max(w["mag"],mag_res)
            w["phase"]=max(w["phase"],phase_res)
            w["thd"]=max(w["thd"],thd_res)
            w["h3"]=max(w["h3"],h3_res)

            print(f"{fs:.0f},{level:.1f},{freq:.1f},{mag_res:.9f},{phase_res:.9f},{thd_res:.9f},{h3_res:.9f}")

    print()
    failures=[]
    for fs in RATES:
        w=worst[fs]
        print(
            f"WORST {fs:.0f}: mag={w['mag']:.9f} dB phase={w['phase']:.9f} deg "
            f"THD={w['thd']:.9f} pp H3={w['h3']:.9f} pp"
        )
        if w["mag"]>0.02:
            failures.append(f"{fs:.0f} magnitude")
        if w["phase"]>0.20:
            failures.append(f"{fs:.0f} phase")
        if w["thd"]>0.002:
            failures.append(f"{fs:.0f} THD")
        if w["h3"]>0.002:
            failures.append(f"{fs:.0f} H3")

    if failures:
        print("FAIL:")
        for item in failures:
            print(" - "+item)
        return 1

    print("PASS: unified 3-state IRON midpoint/RK2 is numerically host-rate viable across 44.1/48/96/192 kHz test matrix.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
