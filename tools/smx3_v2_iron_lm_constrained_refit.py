#!/usr/bin/env python3
"""Refit c/KI versus quasi-static low-field inductive scale for SMX-3 V2 IRON.

Motivation:
The loss-aware Jensen target indicates an inductive scale near 900 H, while
the former 144 H value is only a lossless-equivalent construction.

Before adding dynamic-loss terms, test whether the EXISTING quasi-static JA
family can satisfy BOTH:
- Jensen +4 / +20 dBu 20 Hz THD anchors;
- Jensen low-field complex magnetic admittance / DLP;

when L_qs is allowed to rise and c/KI are re-identified.

If this works, prefer the simpler stateful model over extra loss mechanisms.
"""

import math
import cmath

import smx3_v2_iron_candidate as base
import smx3_v2_jensen_lossaware_target as target
from smx3_v2_dlp_utils import dlp_degrees


L_VALUES=(400.0,600.0,900.0,1200.0,1600.0)
Y_FREQS=(20.0,50.0,100.0,200.0,1000.0)
DLP_FREQS=(20.0,30.0,50.0,100.0,200.0,500.0,1000.0,2000.0,5000.0,10000.0,20000.0)

A=14.1
ALPHA=5.0e-5
K=17.8
MS=2.75e5


def langevin(x):
    if abs(x)<1e-4:
        return x/3.0
    return 1.0/math.tanh(x)-1.0/x


def langevin_d(x):
    if abs(x)<1e-4:
        return 1.0/3.0
    s=math.sinh(x)
    return 1.0/(x*x)-1.0/(s*s)


def make_dmdh(c):
    def dmdh(H,M,direction):
        q=(H+ALPHA*M)/A
        man=MS*langevin(q)
        ld=langevin_d(q)
        delta=1.0 if direction>=0 else -1.0
        dm=man-M
        delta_m=1.0 if delta*dm>=0 else 0.0

        den=(1.0-c)*delta*K-ALPHA*dm
        if abs(den)<1e-12:
            den=math.copysign(1e-12,den if den else delta)

        irreversible=(1.0-c)*delta_m*dm/den
        reversible=c*MS/A*ld
        yden=1.0-ALPHA*reversible
        if abs(yden)<1e-12:
            yden=math.copysign(1e-12,yden if yden else 1.0)

        return (irreversible+reversible)/yden
    return dmdh


def make_model(lm,c,ki):
    dmdh=make_dmdh(c)
    slope0=dmdh(0.0,0.0,1.0)
    kphi=lm/(ki*(1.0+slope0))

    def deriv(t,H,M,amp,freq):
        vs=amp*math.sin(2.0*math.pi*freq*t)
        rseries=base.RSOURCE+base.RP
        divider=1.0+rseries/base.RLOAD

        numerator=vs-rseries*H/ki
        direction=1.0 if numerator>=0 else -1.0
        slope=dmdh(H,M,direction)

        vnode=numerator/divider
        dH=vnode/(kphi*(1.0+slope))
        dM=slope*dH
        vout=vnode*base.RL/base.RLOAD
        imag=H/ki
        return dH,dM,vout,vnode,imag

    return deriv,kphi


def simulate(lm,c,ki,level_dbu,freq=20.0,fs=None,warmup_cycles=20,analysis_cycles=4):
    if fs is None:
        fs=max(24000.0,48.0*freq)

    deriv,_=make_model(lm,c,ki)
    vrms=0.775*10.0**(level_dbu/20.0)
    amp=vrms*math.sqrt(2.0)
    dt=1.0/fs

    n=int(round((warmup_cycles+analysis_cycles)*fs/freq))
    start=int(round(warmup_cycles*fs/freq))

    H=M=0.0
    y=[]

    re_v=im_v=0.0
    re_i=im_i=0.0

    for idx in range(n):
        t=idx*dt
        k1h,k1m,v1,_,_=deriv(t,H,M,amp,freq)
        k2h,k2m,_,_,_=deriv(t+0.5*dt,H+0.5*dt*k1h,M+0.5*dt*k1m,amp,freq)
        k3h,k3m,_,_,_=deriv(t+0.5*dt,H+0.5*dt*k2h,M+0.5*dt*k2m,amp,freq)
        k4h,k4m,_,_,_=deriv(t+dt,H+dt*k3h,M+dt*k3m,amp,freq)

        H += dt*(k1h+2*k2h+2*k3h+k4h)/6.0
        M += dt*(k1m+2*k2m+2*k3m+k4m)/6.0

        if idx>=start:
            _,_,vout,vnode,imag=deriv(t+dt,H,M,amp,freq)
            local=idx-start
            a=2.0*math.pi*freq*local/fs
            co=math.cos(a); si=math.sin(a)

            re_v+=vnode*co
            im_v-=vnode*si
            re_i+=imag*co
            im_i-=imag*si
            y.append(vout)

    V=complex(re_v,im_v)
    I=complex(re_i,im_i)
    ymag=I/V

    N=len(y)

    def comp(h):
        re=im=0.0
        for i,v in enumerate(y):
            a=2.0*math.pi*h*freq*i/fs
            re+=v*math.cos(a)
            im-=v*math.sin(a)
        return complex(re,im)

    c1=comp(1)
    f1=abs(c1)
    hs=[abs(comp(h))/f1 for h in range(2,11)]
    thd=math.sqrt(sum(h*h for h in hs))

    phase=cmath.phase(c1)+math.pi/2.0
    while phase>math.pi: phase-=2.0*math.pi
    while phase<-math.pi: phase+=2.0*math.pi

    rms=math.sqrt(sum(v*v for v in y)/N)

    return {
        "thd":thd,
        "hs":hs,
        "ymag":ymag,
        "phase":phase,
        "rms":rms,
    }


def solve_ki_for_high(lm,c,target_thd=0.01):
    # Find a monotonic bracket by expansion.
    lo=500.0
    hi=50000.0

    dlo=simulate(lm,c,lo,20.0)["thd"]
    dhi=simulate(lm,c,hi,20.0)["thd"]

    for _ in range(12):
        if dlo>target_thd:
            lo*=0.5
            dlo=simulate(lm,c,lo,20.0)["thd"]
        elif dhi<target_thd:
            hi*=2.0
            dhi=simulate(lm,c,hi,20.0)["thd"]
        else:
            break

    if not (dlo<=target_thd<=dhi):
        return None

    for _ in range(22):
        mid=0.5*(lo+hi)
        d=simulate(lm,c,mid,20.0)["thd"]
        if d<target_thd:
            lo=mid
        else:
            hi=mid

    return 0.5*(lo+hi)


def fit_c_ki(lm):
    # First find a c bracket around +4 dBu target after solving KI for +20 dBu.
    samples=[]

    for i in range(19):
        c=0.05+0.90*i/18.0
        ki=solve_ki_for_high(lm,c)
        if ki is None:
            continue
        low=simulate(lm,c,ki,4.0)["thd"]
        samples.append((c,ki,low))

    if not samples:
        return None

    target_low=0.00025

    bracket=None
    for a,b in zip(samples,samples[1:]):
        if (a[2]-target_low)*(b[2]-target_low)<=0.0:
            bracket=(a,b)
            break

    if bracket is None:
        # Return closest point as an explicit non-exact result.
        best=min(samples,key=lambda x:abs(x[2]-target_low))
        return best[0],best[1],best[2],False

    lo=bracket[0][0]
    hi=bracket[1][0]

    for _ in range(16):
        mid=0.5*(lo+hi)
        ki=solve_ki_for_high(lm,mid)
        if ki is None:
            break
        low=simulate(lm,mid,ki,4.0)["thd"]

        ki_lo=solve_ki_for_high(lm,lo)
        low_lo=simulate(lm,lo,ki_lo,4.0)["thd"]

        if (low_lo-target_low)*(low-target_low)<=0.0:
            hi=mid
        else:
            lo=mid

    c=0.5*(lo+hi)
    ki=solve_ki_for_high(lm,c)
    low=simulate(lm,c,ki,4.0)["thd"]
    return c,ki,low,True


def target_y(freq):
    return 1.0/complex(target.RMAG,2.0*math.pi*freq*target.LMAG)


def y_cost(lm,c,ki):
    total=0.0
    rows=[]

    for f in Y_FREQS:
        r=simulate(lm,c,ki,4.0,f)
        y=r["ymag"]
        yt=target_y(f)

        sr=max(abs(yt.real),0.05e-6)
        si=max(abs(yt.imag),0.05e-6)
        er=(y.real-yt.real)/sr
        ei=(y.imag-yt.imag)/si
        total+=er*er+ei*ei
        rows.append((f,y,yt))

    return total/len(Y_FREQS),rows


def dlp_metric(lm,c,ki):
    phases=[]
    gains=[]

    for f in DLP_FREQS:
        r=simulate(lm,c,ki,4.0,f)
        phases.append(r["phase"])
        gains.append(r["rms"])

    d=dlp_degrees(DLP_FREQS,phases)
    i1=DLP_FREQS.index(1000.0)
    rel20=20.0*math.log10(gains[0]/gains[i1])
    rel20k=20.0*math.log10(gains[-1]/gains[i1])

    return d,rel20,rel20k


def main():
    results=[]

    print("SMX-3 V2 IRON L_qs -> c/KI constrained refit")
    print("Each L_qs solves +20 dBu THD via KI and then +4 dBu THD via c.")
    print()
    print("L_qs_H,c,KI,low_anchor_exact,H4_THD_pct,H20_THD_pct,Ycost,DLP_min,DLP_max,DLP_worst,rel20_dB,rel20k_dB")

    for lm in L_VALUES:
        fit=fit_c_ki(lm)
        if fit is None:
            print(f"{lm:.3f},nan,nan,0,nan,nan,nan,nan,nan,nan,nan,nan")
            continue

        c,ki,low,exact=fit

        low_r=simulate(lm,c,ki,4.0,20.0,fs=48000.0,warmup_cycles=30,analysis_cycles=4)
        high_r=simulate(lm,c,ki,20.0,20.0,fs=48000.0,warmup_cycles=30,analysis_cycles=4)

        yc,rows=y_cost(lm,c,ki)
        d,rel20,rel20k=dlp_metric(lm,c,ki)

        results.append((yc,d["worst_abs_deg"],lm,c,ki,low_r,high_r,d,rel20,rel20k,exact,rows))

        print(
            f"{lm:.3f},{c:.9f},{ki:.9f},{int(exact)},"
            f"{100*low_r['thd']:.9f},{100*high_r['thd']:.9f},"
            f"{yc:.9f},{min(d['residual_deg']):+.9f},{max(d['residual_deg']):+.9f},"
            f"{d['worst_abs_deg']:.9f},{rel20:.9f},{rel20k:.9f}"
        )

    if not results:
        raise SystemExit("FAIL: no constrained L_qs candidate")

    # Prefer exact-anchor fits, then magnetic-admittance agreement.
    exacts=[r for r in results if r[10]]
    pool=exacts if exacts else results
    best=min(pool,key=lambda r:(r[0],r[1]))

    yc,worst,lm,c,ki,low_r,high_r,d,rel20,rel20k,exact,rows=best

    print()
    print("BEST CONSTRAINED L_qs CANDIDATE")
    print(f"L_qs={lm:.9f} H")
    print(f"c={c:.9f}")
    print(f"KI={ki:.9f}")
    print(f"exact low-anchor fit={int(exact)}")
    print(f"+4 dBu THD={100*low_r['thd']:.9f}%")
    print(f"+20 dBu THD={100*high_r['thd']:.9f}%")
    print(f"H2={100*low_r['hs'][0]:.9f}% H3={100*low_r['hs'][1]:.9f}%")
    print(f"Ycost={yc:.9f}")
    print(f"DLP worst={worst:.9f} deg")
    print(f"rel20={rel20:.9f} dB rel20k={rel20k:.9f} dB")
    print()
    print("freq,Y_model_re_uS,Y_model_im_uS,Y_target_re_uS,Y_target_im_uS")
    for f,y,yt in rows:
        print(
            f"{f:.1f},{1e6*y.real:.9f},{1e6*y.imag:.9f},"
            f"{1e6*yt.real:.9f},{1e6*yt.imag:.9f}"
        )

    print()
    if best[2] > 144.0 and exact:
        print("RESULT: higher L_qs can be evaluated fairly after c/KI re-identification.")
    if worst<=2.0 and abs(100*low_r["thd"]-0.025)<=0.005 and abs(100*high_r["thd"]-1.0)<=0.05:
        print("RESULT: quasi-static JA family reaches Jensen first-order THD+DLP bounds without added dynamic-loss terms.")
    else:
        print("RESULT: quasi-static c/KI/L_qs refit alone does not close all Jensen constraints; dynamic model extension remains justified.")


if __name__=="__main__":
    raise SystemExit(main())
