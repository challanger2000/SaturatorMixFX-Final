#!/usr/bin/env python3
"""Frozen offline SMX-3 V2 IRON unified candidate.

This module freezes the first unified nonlinear magnetic reference that passes:
- Jensen +4 dBu / 20 Hz THD;
- Jensen +20 dBu / 20 Hz THD;
- H3-dominant unbiased parity;
while retaining the one-state relaxation architecture that independently passes
the selected Jensen small-signal magnitude/impedance/DLP constraints.

Evidence class:
EMPIRICALLY TUNED TO DOCUMENTED MEASUREMENTS.

This is an OFFLINE REFERENCE, not production DSP.
"""

import math

RSOURCE=600.0
RP=1450.0
RSEC=1550.0
RL=10000.0
RLOAD=RSEC+RL

A=14.1
ALPHA=5.0e-5
K=17.8
MS=2.75e5

C=0.535351563
KI=1087366.676330566

LSTAT=1309.871357869
GREL=2.73374681419e-6
TAU=1.440238371e-3

KPHI=2.85816455767e-7


def langevin(x):
    ax=abs(x)
    if ax<1e-4:
        return x/3.0
    return 1.0/math.tanh(x)-1.0/x


def langevin_d(x):
    ax=abs(x)
    if ax<1e-4:
        return 1.0/3.0
    if ax>20.0:
        return 1.0/(x*x)
    s=math.sinh(x)
    return 1.0/(x*x)-1.0/(s*s)


def dmdh(H,M,direction):
    q=(H+ALPHA*M)/A
    man=MS*langevin(q)
    ld=langevin_d(q)
    delta=1.0 if direction>=0.0 else -1.0
    dm=man-M
    delta_m=1.0 if delta*dm>=0.0 else 0.0

    den=(1.0-C)*delta*K-ALPHA*dm
    if abs(den)<1e-12:
        den=math.copysign(1e-12,den if den else delta)

    irreversible=(1.0-C)*delta_m*dm/den
    reversible=C*MS/A*ld
    yden=1.0-ALPHA*reversible
    if abs(yden)<1e-12:
        yden=math.copysign(1e-12,yden if yden else 1.0)

    return (irreversible+reversible)/yden


def deriv_source(H,M,irel,vs):
    """State derivatives for an arbitrary instantaneous source voltage."""
    rseries=RSOURCE+RP

    vnode=(vs-rseries*(H/KI+irel))/(1.0+rseries/RLOAD)

    direction=1.0 if vnode>=0.0 else -1.0
    slope=dmdh(H,M,direction)

    dH=vnode/(KPHI*(1.0+slope))
    dM=slope*dH
    dI=(GREL*vnode-irel)/TAU
    vout=vnode*RL/RLOAD

    return dH,dM,dI,vout,vnode


def deriv(t,H,M,irel,amp,freq):
    vs=amp*math.sin(2.0*math.pi*freq*t)
    dH,dM,dI,vout,_=deriv_source(H,M,irel,vs)
    return dH,dM,dI,vout


def rk4_step(t,H,M,irel,dt,source):
    v1=source(t)
    k1h,k1m,k1i,_,_=deriv_source(H,M,irel,v1)

    tm=t+0.5*dt
    v2=source(tm)
    k2h,k2m,k2i,_,_=deriv_source(
        H+0.5*dt*k1h,M+0.5*dt*k1m,irel+0.5*dt*k1i,v2
    )
    k3h,k3m,k3i,_,_=deriv_source(
        H+0.5*dt*k2h,M+0.5*dt*k2m,irel+0.5*dt*k2i,v2
    )

    te=t+dt
    v4=source(te)
    k4h,k4m,k4i,_,_=deriv_source(
        H+dt*k3h,M+dt*k3m,irel+dt*k3i,v4
    )

    H2=H+dt*(k1h+2*k2h+2*k3h+k4h)/6.0
    M2=M+dt*(k1m+2*k2m+2*k3m+k4m)/6.0
    I2=irel+dt*(k1i+2*k2i+2*k3i+k4i)/6.0
    _,_,_,vout,_=deriv_source(H2,M2,I2,v4)
    return H2,M2,I2,vout


def simulate(level_dbu,freq=20.0,fs=48000.0,warmup_cycles=120,analysis_cycles=6):
    vrms=0.775*10.0**(level_dbu/20.0)
    amp=vrms*math.sqrt(2.0)
    dt=1.0/fs
    total=warmup_cycles+analysis_cycles
    n=int(round(total*fs/freq))
    start=int(round(warmup_cycles*fs/freq))

    source=lambda t:amp*math.sin(2.0*math.pi*freq*t)

    H=M=irel=0.0
    y=[]

    for i in range(n):
        H,M,irel,vout=rk4_step(i*dt,H,M,irel,dt,source)
        if i>=start:
            y.append(vout)

    def component(h):
        re=im=0.0
        for i,v in enumerate(y):
            a=2.0*math.pi*h*freq*i/fs
            re+=v*math.cos(a)
            im-=v*math.sin(a)
        return complex(re,im)

    c1=component(1)
    fund=abs(c1)
    hs=[abs(component(h))/fund for h in range(2,11)]
    thd=math.sqrt(sum(h*h for h in hs))

    return {
        "thd":thd,
        "hs":hs,
        "H":H,
        "M":M,
        "irel":irel,
        "fundamental":c1,
    }


if __name__=="__main__":
    for level in (4.0,20.0):
        r=simulate(level)
        print(level,100*r["thd"],100*r["hs"][0],100*r["hs"][1],r["irel"])
