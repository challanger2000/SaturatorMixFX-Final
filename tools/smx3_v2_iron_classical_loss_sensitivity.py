#!/usr/bin/env python3
"""Classical dynamic-loss sensitivity for the V2 IRON Jiles-Atherton core.

Adds ONLY the classical derivative-dependent loss field:

    H_applied = H_qs + A_v * v_core

because v_core is proportional to dB/dt in the reduced transformer state.

This is the time-domain equivalent of a loss field proportional to dB/dt,
consistent with the classical eddy-current term in dynamic hysteresis models.

A_v >= 0.
At DC, v_core=0, so this addition vanishes and leaves the quasi-static
hysteresis/remanence law unchanged.

Purpose:
determine whether one linear dynamic-loss coefficient can materially improve
Jensen DLP without destroying:
- +4 dBu / 20 Hz THD;
- +20 dBu / 20 Hz THD;
- H3-dominant symmetry.

No production parameter is selected by this screening tool.
"""

import math
import cmath

import smx3_v2_iron_candidate as base


FREQS=(20.0,30.0,50.0,100.0,200.0,500.0,1000.0,2000.0,5000.0,10000.0,20000.0)
A_VALUES=(0.0,0.01,0.03,0.10,0.30,1.00)


def make_deriv(av):
    def deriv(t,H,M,amp,freq):
        vs=amp*math.sin(2.0*math.pi*freq*t)
        rseries=base.RSOURCE+base.RP

        direction_seed=1.0 if vs-rseries*H/base.KI >= 0.0 else -1.0
        slope=base.dmdh(H,M,direction_seed)

        # Total magnetizing current:
        #   i_m = (H + av*vnode)/KI
        # plus reflected load current vnode/RLOAD.
        # Solve the resulting scalar linear circuit equation exactly.
        denom=1.0+rseries/base.RLOAD+rseries*av/base.KI
        vnode=(vs-rseries*H/base.KI)/denom

        # Direction follows actual dH/dt / core voltage.
        direction=1.0 if vnode>=0.0 else -1.0
        slope=base.dmdh(H,M,direction)

        dH=vnode/(base.KPHI*(1.0+slope))
        dM=slope*dH
        vout=vnode*base.RL/base.RLOAD
        return dH,dM,vout
    return deriv


def run(level_dbu,freq,av,fs=None,warmup_cycles=30,analysis_cycles=4):
    if fs is None:
        fs=max(48000.0,96.0*freq)

    deriv=make_deriv(av)
    vrms=0.775*10.0**(level_dbu/20.0)
    amp=vrms*math.sqrt(2.0)
    dt=1.0/fs

    total=warmup_cycles+analysis_cycles
    n=int(round(total*fs/freq))
    start=int(round(warmup_cycles*fs/freq))

    H=0.0
    M=0.0
    y=[]

    for i in range(n):
        t=i*dt
        k1h,k1m,v1=deriv(t,H,M,amp,freq)
        k2h,k2m,_=deriv(t+0.5*dt,H+0.5*dt*k1h,M+0.5*dt*k1m,amp,freq)
        k3h,k3m,_=deriv(t+0.5*dt,H+0.5*dt*k2h,M+0.5*dt*k2m,amp,freq)
        k4h,k4m,_=deriv(t+dt,H+dt*k3h,M+dt*k3m,amp,freq)

        H += dt*(k1h+2*k2h+2*k3h+k4h)/6.0
        M += dt*(k1m+2*k2m+2*k3m+k4m)/6.0

        if i>=start:
            y.append(v1)

    N=len(y)

    def comp(h):
        re=0.0
        im=0.0
        for i,v in enumerate(y):
            a=2.0*math.pi*h*freq*i/fs
            re+=v*math.cos(a)
            im-=v*math.sin(a)
        return complex(re,im)

    c1=comp(1)
    fund=abs(c1)
    hs=[abs(comp(h))/fund for h in range(2,11)]
    thd=math.sqrt(sum(v*v for v in hs))

    # input sine local phasor under this projection is approximately -j.
    # Relative output phase:
    phase=cmath.phase(c1)-(-math.pi/2.0)
    while phase>math.pi: phase-=2.0*math.pi
    while phase<-math.pi: phase+=2.0*math.pi

    rms=math.sqrt(sum(v*v for v in y)/N)
    return {"thd":thd,"hs":hs,"phase":phase,"rms":rms}


def unwrap(vals):
    out=[vals[0]]
    for p in vals[1:]:
        q=p
        while q-out[-1]>math.pi:q-=2.0*math.pi
        while q-out[-1]<-math.pi:q+=2.0*math.pi
        out.append(q)
    return out


def linefit(xs,ys):
    n=len(xs)
    sx=sum(xs);sy=sum(ys)
    sxx=sum(x*x for x in xs)
    sxy=sum(x*y for x,y in zip(xs,ys))
    b=(n*sxy-sx*sy)/(n*sxx-sx*sx)
    a=(sy-b*sx)/n
    return a,b


def evaluate(av):
    low20=run(4.0,20.0,av)
    high20=run(20.0,20.0,av)

    phases=[]
    gains=[]
    for f in FREQS:
        r=run(4.0,f,av)
        phases.append(r["phase"])
        gains.append(r["rms"])

    phases=unwrap(phases)
    a,b=linefit(FREQS,phases)
    dlp=[math.degrees(p-(a+b*f)) for f,p in zip(FREQS,phases)]
    worst=max(abs(min(dlp)),abs(max(dlp)))

    rel20=20.0*math.log10(gains[0]/gains[FREQS.index(1000.0)])
    rel20k=20.0*math.log10(gains[-1]/gains[FREQS.index(1000.0)])

    return {
        "low_thd":100.0*low20["thd"],
        "high_thd":100.0*high20["thd"],
        "h2":100.0*low20["hs"][0],
        "h3":100.0*low20["hs"][1],
        "dlp_min":min(dlp),
        "dlp_max":max(dlp),
        "dlp_worst":worst,
        "rel20":rel20,
        "rel20k":rel20k,
    }


def main():
    print("SMX-3 V2 IRON classical dynamic-loss sensitivity")
    print("A_v,H4_THD_pct,H20_THD_pct,H2_pct,H3_pct,rel20_dB,rel20k_dB,DLP_min_deg,DLP_max_deg,DLP_worst_deg")

    best=None

    for av in A_VALUES:
        r=evaluate(av)
        print(
            f"{av:.6f},{r['low_thd']:.9f},{r['high_thd']:.9f},"
            f"{r['h2']:.9f},{r['h3']:.9f},"
            f"{r['rel20']:.9f},{r['rel20k']:.9f},"
            f"{r['dlp_min']:+.9f},{r['dlp_max']:+.9f},{r['dlp_worst']:.9f}"
        )

        # Screening cost only; not a production fit.
        cost=(
            ((r["low_thd"]-0.025)/0.005)**2
            +((r["high_thd"]-1.0)/0.05)**2
            +((r["dlp_max"]-0.6)/0.5)**2
            +(max(0.0,r["dlp_worst"]-2.0)/0.5)**2
        )
        if best is None or cost<best[0]:
            best=(cost,av,r)

    print()
    print(f"screening best A_v = {best[1]:.6f}")
    print("This is a sensitivity result only; no parameter is promoted.")
    print("If DLP cannot enter Jensen bounds without damaging THD, classical loss alone is structurally insufficient.")


if __name__=="__main__":
    raise SystemExit(main())
