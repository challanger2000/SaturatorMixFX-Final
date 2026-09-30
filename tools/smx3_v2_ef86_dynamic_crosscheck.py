#!/usr/bin/env python3
"""Independent integration-method cross-check for the dynamic EF86 reference.

Compares:
- current offline authority: implicit trapezoid;
- independent implicit midpoint.

Both solve the same EX=1.40 EF86 current model and documented Philips
screen/cathode/output network. Agreement tests numerical credibility only.

Standard library only.
"""

import math

import smx3_v2_ef86_dynamic_reference as ref


def midpoint_step(t,x,dt,vin_peak,freq):
    z=x[:]
    tm=t+0.5*dt

    for iteration in range(20):
        mid=[0.5*(x[i]+z[i]) for i in range(ref.N)]
        r=ref.rhs(tm,mid,vin_peak,freq)
        dz=[z[i]-x[i] for i in range(ref.N)]
        cd=ref.matvec(ref.C,dz)
        F=[cd[i]/dt-r[i] for i in range(ref.N)]

        if max(abs(v) for v in F)<1e-10:
            return z,iteration

        J=[[0.0]*ref.N for _ in range(ref.N)]
        for j in range(ref.N):
            eps=1e-7*max(1.0,abs(z[j]))
            zz=z[:]
            zz[j]+=eps
            mm=[0.5*(x[i]+zz[i]) for i in range(ref.N)]
            rr=ref.rhs(tm,mm,vin_peak,freq)
            dd=[zz[i]-x[i] for i in range(ref.N)]
            cdd=ref.matvec(ref.C,dd)
            FF=[cdd[i]/dt-rr[i] for i in range(ref.N)]
            for i in range(ref.N):
                J[i][j]=(FF[i]-F[i])/eps

        delta=ref.solve_linear(J,[-v for v in F])
        z=[z[i]+delta[i] for i in range(ref.N)]

        if not all(math.isfinite(v) for v in z):
            raise RuntimeError("non-finite EF86 midpoint state")

        if max(abs(v) for v in delta)<1e-10:
            return z,iteration+1

    raise RuntimeError("EF86 midpoint Newton solver did not converge")


def analyze(out,start,t0,fs,freq,vin_peak):
    y=out[start:]
    mean=sum(y)/len(y)
    y=[v-mean for v in y]
    N=len(y)
    times=[t0+(start+i+1)/fs for i in range(N)]

    mags=[]
    phases=[]
    max_h=min(10,int((0.49*fs)//freq))

    for h in range(1,max_h+1):
        re=im=0.0
        for t,v in zip(times,y):
            a=2.0*math.pi*h*freq*t
            re+=v*math.cos(a)
            im-=v*math.sin(a)
        mags.append(2.0*math.hypot(re,im)/N)
        phases.append(math.atan2(im,re))

    ire=iim=0.0
    for t in times:
        v=vin_peak*math.sin(2.0*math.pi*freq*t)
        a=2.0*math.pi*freq*t
        ire+=v*math.cos(a)
        iim-=v*math.sin(a)
    iphase=math.atan2(iim,ire)

    rel=phases[0]-iphase
    while rel>math.pi: rel-=2.0*math.pi
    while rel<-math.pi: rel+=2.0*math.pi

    fund=mags[0]
    thd=math.sqrt(sum(a*a for a in mags[1:]))/fund if len(mags)>1 else 0.0
    return {"gain":fund/vin_peak,"phase_deg":math.degrees(rel),"thd":thd}


def simulate_midpoint(freq,vin_rms,fs,warmup_seconds=0.4,cycles=8):
    x=ref.solve_dc()
    vin_peak=vin_rms*math.sqrt(2.0)
    max_newton=0

    warm_fs=min(fs,max(192000.0,24.0*freq))
    nw=int(round(warmup_seconds*warm_fs))
    dtw=1.0/warm_fs

    for n in range(nw):
        x,it=midpoint_step(n*dtw,x,dtw,vin_peak,freq)
        max_newton=max(max_newton,it)

    t0=nw/warm_fs
    n=max(1,int(round(cycles*fs/freq)))
    dt=1.0/fs
    out=[]

    for i in range(n):
        x,it=midpoint_step(t0+i*dt,x,dt,vin_peak,freq)
        max_newton=max(max_newton,it)
        out.append(x[ref.O_NODE])

    spc=max(1,int(round(fs/freq)))
    keep=min(len(out),4*spc)
    r=analyze(out,len(out)-keep,t0,fs,freq,vin_peak)
    r["max_newton"]=max_newton
    return r


def phase_delta(a,b):
    d=a-b
    while d>180.0:d-=360.0
    while d<-180.0:d+=360.0
    return d


CASES=[
    ("1k low",1000.0,0.010,768000.0),
    ("1k medium",1000.0,0.180,768000.0),
    ("10k low",10000.0,0.010,3840000.0),
    ("20k low",20000.0,0.010,7680000.0),
]


def main():
    print("SMX-3 V2 EF86 integration-method cross-check")
    print("implicit trapezoid vs independent implicit midpoint")
    print()
    print("case,fs,gain_ppm,phase_deg,THD_residual_pp")

    failures=[]

    for label,freq,vin,fs in CASES:
        a=ref.simulate(freq,vin,fs=fs,warmup_seconds=0.4,cycles=8)
        b=simulate_midpoint(freq,vin,fs,warmup_seconds=0.4,cycles=8)

        gppm=1e6*abs(b["gain"]-a["gain"])/max(abs(a["gain"]),1e-30)
        pdeg=abs(phase_delta(b["phase_deg"],a["phase_deg"]))
        thdpp=100.0*abs(b["thd"]-a["thd"])

        print(f"{label},{fs:.0f},{gppm:.6f},{pdeg:.9f},{thdpp:.9f}")

        if gppm>150.0: failures.append(label+" gain")
        if pdeg>0.002: failures.append(label+" phase")
        if thdpp>0.001: failures.append(label+" THD")

    print()
    if failures:
        print("FAIL: EF86 integration-method disagreement")
        for f in failures: print(" - "+f)
        return 1

    print("PASS: trapezoid and midpoint agree within frozen offline tolerances.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
