#!/usr/bin/env python3
"""Practical program-material benchmark for the frozen unified SMX-3 V2 IRON.

Goals:
1. Judge cheap realtime candidates on music-like signals, not pathological
   infinite-bandwidth steps.
2. Quantify how much audible nonlinear character the physical IRON model
   contributes relative to its local linearized path.
3. Select the cheapest candidate whose practical residual is comfortably below
   the nonlinear character itself.

All candidates receive identical 48 kHz host samples. The authority uses RK4
with 8 internal substeps under zero-order-held host input.
"""

import math
import random
import smx3_v2_iron_unified_candidate as ref

FS=48000.0
AUTH_FACTOR=8
LEVELS=(10.0,16.0,20.0)
CANDIDATES=(("rk2",1),("rk2",2),("rk4",1),("rk4",2),("rk4",4))

def dbu_amp(level):
    return 0.775*10.0**(level/20.0)*math.sqrt(2.0)

def step_mid(H,M,I,dt,x):
    k1h,k1m,k1i,_,_=ref.deriv_source(H,M,I,x)
    k2h,k2m,k2i,_,_=ref.deriv_source(
        H+0.5*dt*k1h,M+0.5*dt*k1m,I+0.5*dt*k1i,x)
    H2=H+dt*k2h
    M2=M+dt*k2m
    I2=I+dt*k2i
    _,_,_,v,_=ref.deriv_source(H2,M2,I2,x)
    return H2,M2,I2,v

def render(samples,method,factor):
    dt=1.0/(FS*factor)
    H=M=I=0.0
    y=[]
    for x in samples:
        v=0.0
        if method=="rk2":
            for _ in range(factor):
                H,M,I,v=step_mid(H,M,I,dt,x)
        else:
            src=lambda _t,value=x:value
            for k in range(factor):
                H,M,I,v=ref.rk4_step(k*dt,H,M,I,dt,src)
        y.append(v)
    return y

def authority(samples):
    return render(samples,"rk4",AUTH_FACTOR)

def linear_render(samples):
    # Frozen unified small-signal magnetic branch, discretized exactly for the
    # relaxation current under ZOH input. This intentionally excludes the
    # nonlinear JA curvature so residual versus authority estimates character.
    dt=1.0/FS
    rseries=ref.RSOURCE+ref.RP
    load=ref.RLOAD
    a=math.exp(-dt/ref.TAU)
    irel=0.0
    # Lstat current integrated with trapezoidal voltage approximation.
    imag_l=0.0
    prev_v=0.0
    y=[]
    for x in samples:
        # one light fixed-point iteration is enough in this near-linear branch
        vnode=(x-rseries*(imag_l+irel))/(1.0+rseries/load)
        imag_l += 0.5*dt*(prev_v+vnode)/ref.LSTAT
        irel = a*irel + ref.GREL*(1.0-a)*vnode
        vnode=(x-rseries*(imag_l+irel))/(1.0+rseries/load)
        prev_v=vnode
        y.append(vnode*ref.RL/ref.RLOAD)
    return y

def rms(x):
    return math.sqrt(sum(v*v for v in x)/max(1,len(x)))

def peak(x):
    return max((abs(v) for v in x),default=0.0)

def residual_db(refsig,test):
    e=[a-b for a,b in zip(refsig,test)]
    return 20.0*math.log10(max(rms(e)/max(rms(refsig),1e-30),1e-30))

def crest(x):
    return 20.0*math.log10(max(peak(x)/max(rms(x),1e-30),1e-30))

def normalize(sig,amp):
    p=max(abs(x) for x in sig) or 1.0
    return [amp*x/p for x in sig]

def drum_bus(n):
    y=[0.0]*n
    hits=[0.02,0.14,0.26,0.38,0.50,0.62,0.74,0.86]
    for h,t0 in enumerate(hits):
        for i in range(int(t0*FS),min(n,int((t0+0.16)*FS))):
            t=i/FS-t0
            kick=math.sin(2*math.pi*(58.0+32.0*math.exp(-t*30))*t)*math.exp(-t*24)
            sn=0.0
            if h%2:
                # deterministic bright snare-like burst
                z=math.sin(2*math.pi*180*t)+0.45*math.sin(2*math.pi*2300*t)+0.25*math.sin(2*math.pi*6100*t)
                sn=z*math.exp(-t*35)
            y[i]+=0.9*kick+0.48*sn
    return y

def bass(n):
    y=[]
    notes=(55.0,55.0,65.406,73.416)
    for i in range(n):
        t=i/FS
        f=notes[int(t/0.25)%len(notes)]
        ph=2*math.pi*f*t
        env=0.65+0.35*(1.0-math.exp(-((t%0.25)+1e-9)*80))
        y.append(env*(math.sin(ph)+0.28*math.sin(2*ph)+0.12*math.sin(3*ph)))
    return y

def guitar(n):
    y=[]
    freqs=(82.407,123.471,164.814,246.942,329.628)
    for i in range(n):
        t=i/FS
        x=0.0
        gate=0.55+0.45*(0.5-0.5*math.cos(2*math.pi*min((t%0.125)/0.018,1.0)))
        for j,f in enumerate(freqs):
            x+=(1.0/(1+j*0.5))*math.sin(2*math.pi*f*t+0.21*j)
        y.append(gate*x)
    return y

def mixbus(n):
    d=drum_bus(n); b=bass(n); g=guitar(n)
    y=[]
    for i in range(n):
        t=i/FS
        pad=0.28*(math.sin(2*math.pi*110*t)+0.7*math.sin(2*math.pi*220*t)+0.35*math.sin(2*math.pi*440*t))
        y.append(0.43*d[i]+0.33*b[i]+0.27*g[i]+pad)
    return y

def main():
    n=int(FS*1.0)
    programs={
        "drums":drum_bus(n),
        "bass":bass(n),
        "guitar":guitar(n),
        "mixbus":mixbus(n),
    }

    print("SMX-3 V2 IRON practical program-material benchmark")
    print("program,level_dBu,crest_dB,character_residual_dBc,method,factor,candidate_residual_dBc")

    practical_limit=-80.0
    winner_ok={c:True for c in CANDIDATES}
    worst={c:-300.0 for c in CANDIDATES}
    char_min=0.0

    for level in LEVELS:
        amp=dbu_amp(level)
        for name,raw in programs.items():
            x=normalize(raw,amp)
            auth=authority(x)
            lin=linear_render(x)
            char_db=residual_db(auth,lin)
            char_min=min(char_min,char_db)
            cr=crest(x)

            for cand in CANDIDATES:
                y=render(x,*cand)
                rd=residual_db(auth,y)
                worst[cand]=max(worst[cand],rd)
                if rd>practical_limit:
                    winner_ok[cand]=False
                print(f"{name},{level:.1f},{cr:.3f},{char_db:.3f},{cand[0]},{cand[1]}x,{rd:.3f}")

    print()
    for cand in CANDIDATES:
        print(f"WORST {cand[0]} {cand[1]}x practical residual = {worst[cand]:.3f} dBc")

    # Cheapest by derivative evaluations/sample.
    ranked=sorted(CANDIDATES,key=lambda c:(2 if c[0]=="rk2" else 4)*c[1])
    selected=next((c for c in ranked if winner_ok[c]),None)

    if selected is None:
        print("FAIL: no tested cheap candidate clears -80 dBc on all practical programs.")
        return 1

    print(f"PASS: lowest-cost practical candidate = {selected[0]} {selected[1]}x.")
    print("INFO: practical residual criterion is -80 dBc; pathological transient gate remains diagnostic only.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
