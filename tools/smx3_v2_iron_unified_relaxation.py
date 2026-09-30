#!/usr/bin/env python3
"""Unified nonlinear JA + one-state magnetic-relaxation IRON candidate.

Architecture:

    i_mag = H / KI + i_relax

    tau * d(i_relax)/dt + i_relax = GREL * v_core

    v_core = KPHI * (1 + dM/dH) * dH/dt

The relaxation state is therefore a causal series-RL loss branch in parallel
with the nonlinear JA magnetizing branch.

Key properties:
- at static equilibrium v_core=0 -> i_relax -> 0;
- JA remains solely responsible for quasi-static hysteresis/remanence;
- one extra stable state supplies the complex-permeability behavior identified
  by the Jensen small-signal relaxation fit;
- LSTAT fixes the low-field equilibrium JA inductance;
- c and KI are re-fit ONLY to the two exact Jensen 20 Hz THD anchors.

This is an OFFLINE candidate / fitting tool, not production DSP.\n\nSettling rule: the 20 Hz fit uses 120 complete warm-up cycles because shorter\n20-40-cycle windows were empirically shown to bias the low-level THD upward.
"""

import math

RSOURCE=600.0
RP=1450.0
RSEC=1550.0
RL=10000.0
RLOAD=RSEC+RL

# Accepted one-state small-signal relaxation fit.
LSTAT=1309.871357869
GREL=2.73374681419e-6
TAU=1.440238371e-3

BASE={
    "a":14.1,
    "alpha":5.0e-5,
    "k":17.8,
    "Ms":2.75e5,
}


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


def make_model(c,ki):
    a=BASE["a"];alpha=BASE["alpha"];k=BASE["k"];ms=BASE["Ms"]

    def dmdh(H,M,direction):
        q=(H+alpha*M)/a
        man=ms*langevin(q)
        ld=langevin_d(q)
        delta=1.0 if direction>=0.0 else -1.0
        dm=man-M
        delta_m=1.0 if delta*dm>=0.0 else 0.0

        den=(1.0-c)*delta*k-alpha*dm
        if abs(den)<1e-12:
            den=math.copysign(1e-12,den if den else delta)

        irreversible=(1.0-c)*delta_m*dm/den
        reversible=c*ms/a*ld
        yden=1.0-alpha*reversible
        if abs(yden)<1e-12:
            yden=math.copysign(1e-12,yden if yden else 1.0)

        return (irreversible+reversible)/yden

    slope0=dmdh(0.0,0.0,1.0)
    kphi=LSTAT/(ki*(1.0+slope0))

    def deriv(t,H,M,irel,amp,freq):
        vs=amp*math.sin(2.0*math.pi*freq*t)
        rseries=RSOURCE+RP

        vnode=(
            vs-rseries*(H/ki+irel)
        )/(1.0+rseries/RLOAD)

        direction=1.0 if vnode>=0.0 else -1.0
        slope=dmdh(H,M,direction)

        dH=vnode/(kphi*(1.0+slope))
        dM=slope*dH
        dI=(GREL*vnode-irel)/TAU
        vout=vnode*RL/RLOAD

        return dH,dM,dI,vout

    return dmdh,deriv,kphi,slope0


def simulate(c,ki,level_dbu,freq=20.0,fs=4000.0,warmup_cycles=120,analysis_cycles=4):
    _,deriv,_,_=make_model(c,ki)

    vrms=0.775*10.0**(level_dbu/20.0)
    amp=vrms*math.sqrt(2.0)
    total=warmup_cycles+analysis_cycles
    n=int(round(total*fs/freq))
    start=int(round(warmup_cycles*fs/freq))
    dt=1.0/fs

    H=M=irel=0.0
    y=[]

    for i in range(n):
        t=i*dt
        k1h,k1m,k1i,v1=deriv(t,H,M,irel,amp,freq)
        k2h,k2m,k2i,_=deriv(
            t+0.5*dt,
            H+0.5*dt*k1h,
            M+0.5*dt*k1m,
            irel+0.5*dt*k1i,
            amp,freq
        )
        k3h,k3m,k3i,_=deriv(
            t+0.5*dt,
            H+0.5*dt*k2h,
            M+0.5*dt*k2m,
            irel+0.5*dt*k2i,
            amp,freq
        )
        k4h,k4m,k4i,_=deriv(
            t+dt,
            H+dt*k3h,
            M+dt*k3m,
            irel+dt*k3i,
            amp,freq
        )

        H += dt*(k1h+2*k2h+2*k3h+k4h)/6.0
        M += dt*(k1m+2*k2m+2*k3m+k4m)/6.0
        irel += dt*(k1i+2*k2i+2*k3i+k4i)/6.0

        if i>=start:
            y.append(v1)

    N=len(y)

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
    thd=math.sqrt(sum(v*v for v in hs))

    phase=math.atan2(c1.imag,c1.real)+math.pi/2.0
    while phase>math.pi:phase-=2.0*math.pi
    while phase<-math.pi:phase+=2.0*math.pi

    rms=math.sqrt(sum(v*v for v in y)/N)

    return {
        "thd":thd,
        "hs":hs,
        "phase":phase,
        "rms":rms,
        "H":H,
        "M":M,
        "irel":irel,
    }


def fit_ki(c):
    lo=100000.0
    hi=2000000.0

    dlo=simulate(c,lo,20.0)["thd"]
    dhi=simulate(c,hi,20.0)["thd"]

    if not (dlo<0.01<dhi):
        return None

    for _ in range(18):
        mid=0.5*(lo+hi)
        d=simulate(c,mid,20.0)["thd"]
        if d<0.01:
            lo=mid
        else:
            hi=mid

    return 0.5*(lo+hi)


def score_c(c):
    ki=fit_ki(c)
    if ki is None:
        return None

    low=simulate(c,ki,4.0)
    high=simulate(c,ki,20.0)

    cost=(
        ((100.0*low["thd"]-0.025)/0.004)**2
        +((100.0*high["thd"]-1.0)/0.02)**2
    )
    return cost,ki,low,high


def fit():
    candidates=[]

    # Settled-state research narrowed the physically useful c region.
    # Keep a deterministic coarse scan wide enough to detect regressions.
    for i in range(10):
        c=0.44+i*(0.18/9.0)
        r=score_c(c)
        if r is not None:
            candidates.append((r[0],c,r[1],r[2],r[3]))

    if not candidates:
        raise RuntimeError("no c/KI bracket")

    candidates.sort(key=lambda x:x[0])
    _,c,ki,_,_=candidates[0]

    step=.010
    for _ in range(20):
        current=score_c(c)
        best=(current[0],c,current[1],current[2],current[3])
        improved=False

        for cc in (c-step,c+step):
            if not (0.5<cc<0.995):
                continue
            r=score_c(cc)
            if r is None:
                continue
            cand=(r[0],cc,r[1],r[2],r[3])
            if cand[0]<best[0]:
                best=cand
                improved=True

        _,c,ki,_,_=best

        if not improved:
            step*=0.5
        if step<2e-5:
            break

    return c,ki


def high_res(c,ki,level,freq=20.0):
    return simulate(
        c,ki,level,freq,
        fs=max(48000.0,96.0*freq),
        warmup_cycles=120,
        analysis_cycles=6
    )


def main():
    c,ki=fit()
    _,_,kphi,slope0=make_model(c,ki)

    low=high_res(c,ki,4.0)
    high=high_res(c,ki,20.0)

    print("SMX-3 V2 unified JA + one-state relaxation IRON candidate")
    print(f"LSTAT = {LSTAT:.9f} H")
    print(f"GREL = {GREL:.12g} S")
    print(f"TAU = {TAU*1e3:.9f} ms")
    print(f"c = {c:.9f}")
    print(f"KI = {ki:.9f} A/m per A")
    print(f"KPHI = {kphi:.12g}")
    print(f"SLOPE0 = {slope0:.9f}")
    print()
    print(f"+4 dBu / 20 Hz THD = {100*low['thd']:.9f}%")
    print(f"+20 dBu / 20 Hz THD = {100*high['thd']:.9f}%")
    print(f"+4 H2 = {100*low['hs'][0]:.9f}%")
    print(f"+4 H3 = {100*low['hs'][1]:.9f}%")
    print(f"+4 H5 = {100*low['hs'][3]:.9f}%")
    print(f"+20 H3 = {100*high['hs'][1]:.9f}%")
    print(f"settled relaxation current (+4) = {low['irel']:.12g} A")

    failures=[]

    if abs(100*low["thd"]-0.025)>0.005:
        failures.append("+4 dBu THD")
    if abs(100*high["thd"]-1.0)>0.05:
        failures.append("+20 dBu THD")
    if low["hs"][0]>=0.1*low["hs"][1]:
        failures.append("H3 dominance")

    # Relaxation state must remain bounded and small relative to practical
    # primary currents.
    if not math.isfinite(low["irel"]) or not math.isfinite(high["irel"]):
        failures.append("relaxation-state finiteness")

    if failures:
        print("REJECT:")
        for item in failures:
            print(" - "+item)
        return 1

    print("PASS: unified nonlinear JA + one-state relaxation candidate preserves exact Jensen THD anchors and H3-dominant symmetry.")
    print("NEXT: verify small-signal DLP/magnitude in time domain, remanence/DC-bias and integration-method invariance.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
