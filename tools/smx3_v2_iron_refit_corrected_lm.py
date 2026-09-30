#!/usr/bin/env python3
"""Refit the SMX-3 V2 IRON candidate after correcting Jensen Lm to ~144 H.

Only two effective parameters are searched:
- Jiles-Atherton reversible fraction c;
- field/current scale KI.

Everything else remains fixed to the previously tested model family.

Fit anchors:
- +4 dBu / 20 Hz -> 0.025% THD typical
- +20 dBu / 20 Hz -> 1.0% THD typical

Search uses a lower-cost solver. Final candidate is rechecked with the
high-resolution 48 kHz / 30-cycle reference.
"""

import math

RSOURCE=600.0
RP=1450.0
RSEC=1550.0
RL=10000.0
RLOAD=RSEC+RL
LM_TARGET=143.999433995

BASE={
    "a":14.1,
    "alpha":5.0e-5,
    "k":17.8,
    "Ms":2.75e5,
}


def langevin(x):
    if abs(x)<1e-4:
        return x/3.0
    return 1.0/math.tanh(x)-1.0/x


def langevin_d(x):
    if abs(x)<1e-4:
        return 1.0/3.0
    s=math.sinh(x)
    return 1.0/(x*x)-1.0/(s*s)


def make_model(c,ki):
    a=BASE["a"];alpha=BASE["alpha"];k=BASE["k"];ms=BASE["Ms"]

    def dmdh(H,M,direction):
        q=(H+alpha*M)/a
        man=ms*langevin(q)
        ld=langevin_d(q)
        delta=1.0 if direction>=0 else -1.0
        dm=man-M
        delta_m=1.0 if delta*dm>=0 else 0.0

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
    kphi=LM_TARGET/(ki*(1.0+slope0))

    def deriv(t,H,M,amp,freq):
        vs=amp*math.sin(2.0*math.pi*freq*t)
        rseries=RSOURCE+RP
        divider=1.0+rseries/RLOAD
        numerator=vs-rseries*H/ki
        direction=1.0 if numerator>=0.0 else -1.0
        slope=dmdh(H,M,direction)
        vnode=numerator/divider
        dH=vnode/(kphi*(1.0+slope))
        dM=slope*dH
        vout=vnode*RL/RLOAD
        return dH,dM,vout

    return deriv,kphi


def simulate(c,ki,level_dbu,fs=12000.0,warmup_cycles=12,analysis_cycles=4):
    deriv,_=make_model(c,ki)
    freq=20.0
    vrms=0.775*10.0**(level_dbu/20.0)
    amp=vrms*math.sqrt(2.0)
    total=warmup_cycles+analysis_cycles
    n=int(round(total*fs/freq))
    start=int(round(warmup_cycles*fs/freq))
    dt=1.0/fs

    H=0.0;M=0.0;y=[]

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
        re=0.0;im=0.0
        for i,v in enumerate(y):
            ang=2.0*math.pi*h*freq*i/fs
            re+=v*math.cos(ang)
            im-=v*math.sin(ang)
        return math.hypot(re,im)

    fund=comp(1)
    hs=[comp(h)/fund for h in range(2,11)]
    thd=math.sqrt(sum(v*v for v in hs))
    return thd,hs


def fit_ki_for_high(c):
    lo=3000.0
    hi=90000.0

    # Require a monotonic bracket around 1% THD.
    dlo=simulate(c,lo,20.0)[0]
    dhi=simulate(c,hi,20.0)[0]

    if not (dlo<0.01<dhi):
        return None

    for _ in range(24):
        mid=0.5*(lo+hi)
        d=simulate(c,mid,20.0)[0]
        if d<0.01:
            lo=mid
        else:
            hi=mid

    return 0.5*(lo+hi)


def score(c):
    ki=fit_ki_for_high(c)
    if ki is None:
        return None

    low,_=simulate(c,ki,4.0)
    high,_=simulate(c,ki,20.0)
    # low-level anchor dominates c selection; high is already constrained by KI.
    cost=((low-0.00025)/0.00005)**2 + ((high-0.01)/0.0002)**2
    return cost,ki,low,high


def high_res(c,ki,level):
    return simulate(c,ki,level,fs=48000.0,warmup_cycles=30,analysis_cycles=4)


def main():
    candidates=[]

    # Coarse c scan.
    for i in range(29):
        c=0.70+i*(0.28/28.0)
        r=score(c)
        if r is not None:
            candidates.append((r[0],c,r[1],r[2],r[3]))

    if not candidates:
        raise SystemExit("FAIL: no valid c/KI bracket")

    candidates.sort()
    _,best_c,best_ki,_,_=candidates[0]

    # Local deterministic refinement around best c.
    step=0.01
    for _ in range(18):
        improved=False
        current=score(best_c)
        if current is None:
            raise SystemExit("FAIL: lost current candidate")

        best_local=(current[0],best_c,current[1],current[2],current[3])

        for cand_c in (best_c-step,best_c+step):
            if not (0.65<cand_c<0.995):
                continue
            r=score(cand_c)
            if r is None:
                continue
            cand=(r[0],cand_c,r[1],r[2],r[3])
            if cand[0]<best_local[0]:
                best_local=cand
                improved=True

        _,best_c,best_ki,_,_=best_local
        if not improved:
            step*=0.5
        if step<2.5e-5:
            break

    deriv,kphi=make_model(best_c,best_ki)

    low,low_hs=high_res(best_c,best_ki,4.0)
    high,high_hs=high_res(best_c,best_ki,20.0)

    print("SMX-3 V2 corrected-Lm IRON refit")
    print(f"Lm fixed = {LM_TARGET:.9f} H")
    print(f"best c = {best_c:.9f}")
    print(f"best KI = {best_ki:.9f} A/m per A")
    print(f"derived KPHI = {kphi:.12g}")
    print()
    print(f"high-res +4 dBu / 20 Hz THD = {100.0*low:.9f}%")
    print(f"high-res +20 dBu / 20 Hz THD = {100.0*high:.9f}%")
    print(f"+4 dBu H2 = {100.0*low_hs[0]:.9f}%")
    print(f"+4 dBu H3 = {100.0*low_hs[1]:.9f}%")
    print(f"+20 dBu H3 = {100.0*high_hs[1]:.9f}%")

    if abs(100.0*low-0.025)>0.005:
        raise SystemExit("FAIL: corrected-Lm candidate misses +4 dBu anchor")
    if abs(100.0*high-1.0)>0.05:
        raise SystemExit("FAIL: corrected-Lm candidate misses +20 dBu anchor")
    if low_hs[0]>=0.1*low_hs[1]:
        raise SystemExit("FAIL: corrected-Lm candidate loses H3-dominant symmetry")

    print("PASS: corrected-Lm candidate re-fits both exact Jensen anchors and H3 symmetry.")


if __name__=="__main__":
    raise SystemExit(main())
