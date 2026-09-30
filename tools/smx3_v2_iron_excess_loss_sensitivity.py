#!/usr/bin/env python3
"""Classical + excess dynamic-loss sensitivity for SMX-3 V2 IRON.

Dynamic field:
    H_dyn = A_v * v_core + B_v * sign(v_core) * sqrt(abs(v_core))

where v_core is proportional to dB/dt.

This corresponds structurally to:
- classical eddy-current loss ~ dB/dt;
- excess/anomalous loss ~ sign(dB/dt)*sqrt(abs(dB/dt)).

The surrounding circuit equation can be solved analytically.

Let:
    N = Vs - Rseries * H_qs / KI
    D = 1 + Rseries/RLOAD + Rseries*A_v/KI
    C = Rseries*B_v/KI
    x = abs(v_core)

Then:
    D*x + C*sqrt(x) = abs(N)

Set u=sqrt(x):
    D*u^2 + C*u - abs(N) = 0

Positive root:
    u = (-C + sqrt(C^2 + 4*D*abs(N))) / (2*D)

Thus no per-sample iterative root solve is needed.

This is a screening tool, not a production parameter fitter.
"""

import math
import cmath

import smx3_v2_iron_candidate as base


FREQS=(20.0,30.0,50.0,100.0,200.0,500.0,1000.0,2000.0,5000.0,10000.0,20000.0)

A_VALUES=(0.0,0.10,0.30)
B_VALUES=(0.0,0.03,0.10,0.30,1.0,3.0)


def make_deriv(av,bv):
    def deriv(t,H,M,amp,freq):
        vs=amp*math.sin(2.0*math.pi*freq*t)
        rseries=base.RSOURCE+base.RP

        n=vs-rseries*H/base.KI

        D=1.0+rseries/base.RLOAD+rseries*av/base.KI
        C=rseries*bv/base.KI

        an=abs(n)
        if an<=0.0:
            vnode=0.0
        else:
            disc=C*C+4.0*D*an
            u=(-C+math.sqrt(disc))/(2.0*D)
            vnode=math.copysign(u*u,n)

        direction=1.0 if vnode>=0.0 else -1.0
        slope=base.dmdh(H,M,direction)

        dH=vnode/(base.KPHI*(1.0+slope))
        dM=slope*dH
        vout=vnode*base.RL/base.RLOAD
        return dH,dM,vout
    return deriv


def run(level_dbu,freq,av,bv,fs=None,warmup_cycles=16,analysis_cycles=4):
    if fs is None:
        fs=max(48000.0,72.0*freq)

    deriv=make_deriv(av,bv)
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

    phase=cmath.phase(c1)+math.pi/2.0
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


def fit_line(xs,ys):
    n=len(xs)
    sx=sum(xs); sy=sum(ys)
    sxx=sum(x*x for x in xs)
    sxy=sum(x*y for x,y in zip(xs,ys))
    b=(n*sxy-sx*sy)/(n*sxx-sx*sx)
    a=(sy-b*sx)/n
    return a,b


def evaluate(av,bv):
    low=run(4.0,20.0,av,bv)
    high=run(20.0,20.0,av,bv)

    phases=[]
    gains=[]

    for f in FREQS:
        r=run(4.0,f,av,bv)
        phases.append(r["phase"])
        gains.append(r["rms"])

    phases=unwrap(phases)
    a,b=fit_line(FREQS,phases)
    dlp=[math.degrees(p-(a+b*f)) for f,p in zip(FREQS,phases)]

    i1=FREQS.index(1000.0)
    rel20=20.0*math.log10(gains[0]/gains[i1])
    rel20k=20.0*math.log10(gains[-1]/gains[i1])

    return {
        "low_thd":100.0*low["thd"],
        "high_thd":100.0*high["thd"],
        "h2":100.0*low["hs"][0],
        "h3":100.0*low["hs"][1],
        "rel20":rel20,
        "rel20k":rel20k,
        "dlp_min":min(dlp),
        "dlp_max":max(dlp),
        "dlp_worst":max(abs(min(dlp)),abs(max(dlp))),
    }


def score(r):
    return (
        ((r["low_thd"]-0.025)/0.005)**2
        +((r["high_thd"]-1.0)/0.05)**2
        +((r["rel20"]-(-0.04))/0.01)**2
        +((r["dlp_max"]-0.6)/0.5)**2
        +(max(0.0,r["dlp_worst"]-2.0)/0.5)**2
    )


def main():
    print("SMX-3 V2 IRON classical+excess dynamic-loss sensitivity")
    print("A_v,B_v,H4_THD_pct,H20_THD_pct,H2_pct,H3_pct,rel20_dB,rel20k_dB,DLP_min_deg,DLP_max_deg,DLP_worst_deg,score")

    best=None

    for av in A_VALUES:
        for bv in B_VALUES:
            r=evaluate(av,bv)
            s=score(r)

            print(
                f"{av:.6f},{bv:.6f},"
                f"{r['low_thd']:.9f},{r['high_thd']:.9f},"
                f"{r['h2']:.9f},{r['h3']:.9f},"
                f"{r['rel20']:.9f},{r['rel20k']:.9f},"
                f"{r['dlp_min']:+.9f},{r['dlp_max']:+.9f},{r['dlp_worst']:.9f},"
                f"{s:.9f}"
            )

            if best is None or s<best[0]:
                best=(s,av,bv,r)

    print()
    print(f"screening best A_v={best[1]:.6f} B_v={best[2]:.6f} score={best[0]:.9f}")
    print("No parameters are promoted from this coarse sweep.")

    r=best[3]
    if r["dlp_worst"]<=2.0 and abs(r["high_thd"]-1.0)<=0.05 and abs(r["low_thd"]-0.025)<=0.005:
        print("SCREEN RESULT: classical+excess architecture can satisfy first-order THD/DLP constraints.")
    else:
        print("SCREEN RESULT: coarse classical+excess grid does not yet satisfy all first-order constraints.")


if __name__=="__main__":
    raise SystemExit(main())
