#!/usr/bin/env python3
"""Provisional JT-11P-1 magnetic candidate for SMX-3 V2 IRON.

This candidate keeps the Jiles-Atherton model family and the previously
derived Jensen electrical skeleton. Relative to the DAFx example magnetic
shape, only the reversible fraction c is changed substantially.

Purpose:
- reproduce the exact Jensen 20 Hz / +4 dBu THD anchor;
- reproduce the exact Jensen 20 Hz / +20 dBu / 1% THD anchor;
- retain settled-state odd/H3-dominant behavior.

This is NOT claimed to be the unique physical Jensen core parameter set.
Parameters fitted only from audio data remain EMPIRICALLY TUNED TO
DOCUMENTED MEASUREMENTS.
"""

import math

RSOURCE=600.0
RP=1450.0
RSEC=1550.0
RL=10000.0
RLOAD=RSEC+RL
LM_TARGET=106.554

P={
    "a":14.1,
    "alpha":5.0e-5,
    "c":0.84,
    "k":17.8,
    "Ms":2.75e5,
}

# Field/current scale selected so the settled coupled model reaches
# approximately 1% THD at Jensen's exact +20 dBu / 20 Hz anchor.
KI=26174.31640625


def langevin(x):
    ax=abs(x)
    if ax<1e-4:
        return x/3.0
    return 1.0/math.tanh(x)-1.0/x


def langevin_d(x):
    ax=abs(x)
    if ax<1e-4:
        return 1.0/3.0
    s=math.sinh(x)
    return 1.0/(x*x)-1.0/(s*s)


def dmdh(H,M,direction):
    a=P["a"]; alpha=P["alpha"]; c=P["c"]; k=P["k"]; Ms=P["Ms"]
    q=(H+alpha*M)/a
    Man=Ms*langevin(q)
    Ld=langevin_d(q)
    delta=1.0 if direction>=0.0 else -1.0
    dm=Man-M
    delta_m=1.0 if delta*dm>=0.0 else 0.0

    den=(1.0-c)*delta*k-alpha*dm
    if abs(den)<1e-12:
        den=math.copysign(1e-12,den if den else delta)

    irreversible=(1.0-c)*delta_m*dm/den
    reversible=c*Ms/a*Ld
    yden=1.0-alpha*reversible
    if abs(yden)<1e-12:
        yden=math.copysign(1e-12,yden if yden else 1.0)

    return (irreversible+reversible)/yden


SLOPE0=dmdh(0.0,0.0,1.0)
KPHI=LM_TARGET/(KI*(1.0+SLOPE0))


def deriv(t,H,M,amp,freq):
    vs=amp*math.sin(2.0*math.pi*freq*t)
    rseries=RSOURCE+RP
    divider=1.0+rseries/RLOAD

    numerator=vs-rseries*H/KI
    direction=1.0 if numerator>=0.0 else -1.0
    slope=dmdh(H,M,direction)

    vnode=numerator/divider
    dH=vnode/(KPHI*(1.0+slope))
    dM=slope*dH
    vout=vnode*RL/RLOAD
    return dH,dM,vout


def simulate(level_dbu,freq=20.0,fs=48000.0,warmup_cycles=30,analysis_cycles=4):
    vrms=0.775*10.0**(level_dbu/20.0)
    amp=vrms*math.sqrt(2.0)
    total_cycles=warmup_cycles+analysis_cycles
    n=int(round(total_cycles*fs/freq))
    warm_samples=int(round(warmup_cycles*fs/freq))
    dt=1.0/fs

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

        if i>=warm_samples:
            y.append(v1)

    N=len(y)

    def component(h):
        re=0.0
        im=0.0
        for i,v in enumerate(y):
            a=2.0*math.pi*h*freq*i/fs
            re+=v*math.cos(a)
            im-=v*math.sin(a)
        return math.hypot(re,im)

    fundamental=component(1)
    hs=[component(h)/fundamental for h in range(2,11)]
    thd=math.sqrt(sum(v*v for v in hs))

    return thd,hs


def main():
    print("SMX-3 V2 provisional JT-11P-1 magnetic candidate")
    print(f"JA c={P['c']:.6f}; KI={KI:.9f}; derived KPHI={KPHI:.12g}")
    print()

    results={}
    print("level_dBu,THD_pct,H2_pct,H3_pct,H5_pct,H2_over_H3_dB")
    for level in (4.0,14.0,20.0):
        thd,hs=simulate(level)
        h2=hs[0]; h3=hs[1]; h5=hs[3]
        ratio=20.0*math.log10(max(h2,1e-30)/max(h3,1e-30))
        results[level]=(thd,hs)
        print(f"{level:.1f},{100*thd:.9f},{100*h2:.9f},{100*h3:.9f},{100*h5:.9f},{ratio:.6f}")

    low=100.0*results[4.0][0]
    high=100.0*results[20.0][0]

    low_err=low-0.025
    high_err=high-1.0

    print()
    print(f"+4 dBu / 20 Hz error vs Jensen 0.025%: {low_err:+.6f} percentage-points")
    print(f"+20 dBu / 20 Hz error vs Jensen 1.0%: {high_err:+.6f} percentage-points")

    # Hard gates use only exact manufacturer anchors plus the documented
    # demagnetized H3-dominance requirement.
    if abs(low_err)>0.005:
        raise SystemExit("FAIL: low-level exact Jensen THD anchor")
    if abs(high_err)>0.05:
        raise SystemExit("FAIL: high-level exact Jensen THD anchor")

    h2=results[4.0][1][0]
    h3=results[4.0][1][1]
    if h2 >= 0.1*h3:
        raise SystemExit("FAIL: default settled Iron state is not sufficiently H3-dominant")

    print("PASS: provisional Iron candidate matches exact 20 Hz anchors and H3-dominant settled symmetry.")
    print("WARNING: multi-frequency Jensen graph fit remains provisional and is not a hard gate yet.")


if __name__=="__main__":
    raise SystemExit(main())
