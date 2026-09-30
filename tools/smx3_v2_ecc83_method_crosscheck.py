#!/usr/bin/env python3
"""Independent integration-method cross-check for SMX-3 V2 dynamic TRI0DE.

Compares:
- existing implicit trapezoidal reference;
- independent implicit midpoint step.

Both solve the same EHX-1 + documented Mullard/Philips network. Agreement at
high integration density reduces the risk that a result is an artifact of one
discretization formula.

Standard library only.
"""

import math

from smx3_v2_ecc83_dynamic_reference import (
    CMAT, NODES, O, rhs, solve_dc, solve_linear, simulate, matvec
)


def midpoint_step(t,x,dt,vin_peak,freq):
    z=x[:]
    tm=t+0.5*dt

    for iteration in range(20):
        mid=[0.5*(x[i]+z[i]) for i in range(NODES)]
        r=rhs(tm,mid,vin_peak,freq)
        dz=[z[i]-x[i] for i in range(NODES)]
        cd=matvec(CMAT,dz)
        F=[cd[i]/dt-r[i] for i in range(NODES)]

        if max(abs(v) for v in F)<1e-10:
            return z,iteration

        J=[[0.0]*NODES for _ in range(NODES)]
        for j in range(NODES):
            eps=1e-7*max(1.0,abs(z[j]))
            zz=z[:]
            zz[j]+=eps
            mm=[0.5*(x[i]+zz[i]) for i in range(NODES)]
            rr=rhs(tm,mm,vin_peak,freq)
            dd=[zz[i]-x[i] for i in range(NODES)]
            cdd=matvec(CMAT,dd)
            FF=[cdd[i]/dt-rr[i] for i in range(NODES)]
            for i in range(NODES):
                J[i][j]=(FF[i]-F[i])/eps

        delta=solve_linear(J,[-v for v in F])
        z=[z[i]+delta[i] for i in range(NODES)]

        if not all(math.isfinite(v) for v in z):
            raise RuntimeError("non-finite midpoint Newton state")
        if max(abs(v) for v in delta)<1e-10:
            return z,iteration+1

    raise RuntimeError("midpoint Newton solver did not converge")


def analyze(out,start,fs,freq,vin_peak):
    y=out[start:]
    mean=sum(y)/len(y)
    y=[v-mean for v in y]
    N=len(y)
    times=[(start+i+1)/fs for i in range(N)]

    mags=[]
    phases=[]
    max_h=min(10,int((0.49*fs)//freq))
    for h in range(1,max_h+1):
        re=0.0
        im=0.0
        for t,v in zip(times,y):
            a=2.0*math.pi*h*freq*t
            re+=v*math.cos(a)
            im-=v*math.sin(a)
        mags.append(2.0*math.hypot(re,im)/N)
        phases.append(math.atan2(im,re))

    in_re=0.0
    in_im=0.0
    for t in times:
        v=vin_peak*math.sin(2.0*math.pi*freq*t)
        a=2.0*math.pi*freq*t
        in_re+=v*math.cos(a)
        in_im-=v*math.sin(a)
    input_phase=math.atan2(in_im,in_re)

    rel_phase=phases[0]-input_phase
    while rel_phase>math.pi: rel_phase-=2.0*math.pi
    while rel_phase<-math.pi: rel_phase+=2.0*math.pi

    fund=mags[0]
    thd=math.sqrt(sum(m*m for m in mags[1:]))/fund if len(mags)>1 else 0.0

    return {
        "gain":fund/vin_peak,
        "phase_deg":math.degrees(rel_phase),
        "thd":thd,
    }


def simulate_midpoint(freq,vin_rms,fs,cycles=8):
    samples=max(1,int(round(cycles*fs/freq)))
    dt=1.0/fs
    x=solve_dc()
    vin_peak=vin_rms*math.sqrt(2.0)
    out=[]
    max_newton=0

    for n in range(samples):
        x,it=midpoint_step(n*dt,x,dt,vin_peak,freq)
        max_newton=max(max_newton,it)
        out.append(x[O])

    samples_per_cycle=max(1,int(round(fs/freq)))
    keep=min(len(out),4*samples_per_cycle)
    r=analyze(out,len(out)-keep,fs,freq,vin_peak)
    r["max_newton"]=max_newton
    return r


def phase_delta(a,b):
    d=a-b
    while d>180.0: d-=360.0
    while d<-180.0: d+=360.0
    return d


CASES=[
    ("1k small",1000.0,0.010,768000.0),
    ("1k nonlinear",1000.0,0.700,768000.0),
    ("10k small",10000.0,0.010,3840000.0),
    ("20k small",20000.0,0.010,7680000.0),
]


def main():
    failures=[]
    print("SMX-3 V2 TRI0DE integration-method cross-check")
    print("method A: implicit trapezoid")
    print("method B: implicit midpoint")
    print()

    for label,freq,vin,fs in CASES:
        a=simulate(freq,vin,fs=fs,cycles=8)
        b=simulate_midpoint(freq,vin,fs=fs,cycles=8)

        gain_ppm=1e6*abs(b["gain"]-a["gain"])/max(abs(a["gain"]),1e-30)
        phase_deg=abs(phase_delta(b["phase_deg"],a["phase_deg"]))
        thd_pp=100.0*abs(b["thd"]-a["thd"])

        print(
            f"{label}: fs={fs:.0f} Hz "
            f"gainResidual={gain_ppm:.6f} ppm "
            f"phaseResidual={phase_deg:.9f} deg "
            f"THDResidual={thd_pp:.9f} pp"
        )

        if gain_ppm>100.0:
            failures.append(label+" gain")
        if phase_deg>0.001:
            failures.append(label+" phase")
        if thd_pp>0.0005:
            failures.append(label+" THD")

    print()
    if failures:
        print("FAIL: integration-method disagreement")
        for f in failures:
            print(" - "+f)
        return 1

    print("PASS: trapezoid and implicit midpoint agree within frozen cross-method tolerances.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
