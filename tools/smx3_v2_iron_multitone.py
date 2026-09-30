#!/usr/bin/env python3
"""Direct multitone/IMD residual for the SMX-3 V2 IRON 1x candidate.

Excitation:
- 100 Hz
- 1 kHz
- 5 kHz
- 11 kHz
- each component at +14 dBu RMS

For orthogonal coherent tones this is approximately +20 dBu combined RMS.

Compare:
- host-rate midpoint/RK2 at 44.1 and 48 kHz;
- coherent 8x-rate RK4 authority;
- authority ideally band-limited to host Nyquist by Fourier-series projection.

This tests nonlinear intermodulation/foldback, not just harmonic sine behavior.
"""

import math
import smx3_v2_iron_candidate as ref

BASE=100.0
TONES=(100.0,1000.0,5000.0,11000.0)
COMPONENT_DBU=14.0
WARM_SECONDS=0.5
ANALYSIS_CYCLES=5


def source(t):
    vrms=0.775*10.0**(COMPONENT_DBU/20.0)
    peak=vrms*math.sqrt(2.0)
    return sum(peak*math.sin(2.0*math.pi*f*t) for f in TONES)


def deriv_vs(H,M,vs):
    rseries=ref.RSOURCE+ref.RP
    divider=1.0+rseries/ref.RLOAD
    numerator=vs-rseries*H/ref.KI
    direction=1.0 if numerator>=0.0 else -1.0
    slope=ref.dmdh(H,M,direction)
    vnode=numerator/divider
    dH=vnode/(ref.KPHI*(1.0+slope))
    dM=slope*dH
    vout=vnode*ref.RL/ref.RLOAD
    return dH,dM,vout


def rk4_step(t,H,M,dt):
    v1=source(t)
    k1h,k1m,o=deriv_vs(H,M,v1)

    v2=source(t+0.5*dt)
    k2h,k2m,_=deriv_vs(H+0.5*dt*k1h,M+0.5*dt*k1m,v2)
    k3h,k3m,_=deriv_vs(H+0.5*dt*k2h,M+0.5*dt*k2m,v2)

    v4=source(t+dt)
    k4h,k4m,_=deriv_vs(H+dt*k3h,M+dt*k3m,v4)

    H += dt*(k1h+2*k2h+2*k3h+k4h)/6.0
    M += dt*(k1m+2*k2m+2*k3m+k4m)/6.0
    return H,M,o


def midpoint_step(t,H,M,dt):
    v1=source(t)
    k1h,k1m,o=deriv_vs(H,M,v1)
    vm=source(t+0.5*dt)
    k2h,k2m,_=deriv_vs(H+0.5*dt*k1h,M+0.5*dt*k1m,vm)
    return H+dt*k2h,M+dt*k2m,o


def render_authority(host):
    fs=host*8.0
    # Both supported hosts and all tones are coherent with BASE.
    warm=int(round(WARM_SECONDS*fs))
    analysis=int(round(ANALYSIS_CYCLES*fs/BASE))
    dt=1.0/fs
    H=M=0.0

    for n in range(warm):
        H,M,_=rk4_step(n*dt,H,M,dt)

    t0=warm*dt
    y=[]
    for n in range(analysis):
        H,M,o=rk4_step(t0+n*dt,H,M,dt)
        y.append(o)

    return y,fs,t0


def bandlimit(y,fs,t0,host):
    N=len(y)
    mean=sum(y)/N
    max_h=int((0.499*host)//BASE)
    coeff=[]

    for h in range(1,max_h+1):
        re=im=0.0
        f=h*BASE
        for i,v in enumerate(y):
            t=t0+i/fs
            a=2.0*math.pi*f*t
            vv=v-mean
            re+=vv*math.cos(a)
            im-=vv*math.sin(a)
        coeff.append((h,complex(2.0*re/N,2.0*im/N)))
    return mean,coeff


def reconstruct(mean,coeff,host):
    spc=int(round(host/BASE))
    N=ANALYSIS_CYCLES*spc
    y=[]
    for n in range(N):
        t=n/host
        v=mean
        for h,c in coeff:
            a=2.0*math.pi*h*BASE*t
            v+=(c*complex(math.cos(a),math.sin(a))).real
        y.append(v)
    return y


def render_host(host):
    warm=int(round(WARM_SECONDS*host))
    analysis=int(round(ANALYSIS_CYCLES*host/BASE))
    dt=1.0/host
    H=M=0.0

    for n in range(warm):
        H,M,_=midpoint_step(n*dt,H,M,dt)

    t0=warm*dt
    y=[]
    for n in range(analysis):
        H,M,o=midpoint_step(t0+n*dt,H,M,dt)
        y.append(o)
    return y


def residual_db(a,b):
    ma=sum(a)/len(a); mb=sum(b)/len(b)
    aa=[v-ma for v in a]; bb=[v-mb for v in b]
    err=sum((x-y)**2 for x,y in zip(aa,bb))
    den=sum(y*y for y in bb)
    return 20.0*math.log10(max(math.sqrt(err/max(den,1e-30)),1e-30))


def main():
    print("SMX-3 V2 IRON multitone/IMD direct residual")
    print("tones=100,1000,5000,11000 Hz; each +14 dBu RMS (~+20 dBu combined)")
    print("host_Hz,residual_dB")

    worst=-300.0
    for host in (44100.0,48000.0):
        ya,fs,t0=render_authority(host)
        mean,c=bandlimit(ya,fs,t0,host)
        target=reconstruct(mean,c,host)
        cand=render_host(host)
        db=residual_db(cand,target)
        worst=max(worst,db)
        print(f"{host:.0f},{db:.9f}")

    print(f"worst multitone residual = {worst:.9f} dB")
    print("classification: "+("STRONG" if worst<=-80 else "PLAUSIBLE" if worst<=-60 else "WEAK"))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
