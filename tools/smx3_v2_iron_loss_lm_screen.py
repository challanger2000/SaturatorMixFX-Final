#!/usr/bin/env python3
"""Joint low-field-L / dynamic-loss architecture screen for SMX-3 V2 IRON.

Why this exists:
The corrected 144 H value is only a lossless-equivalent baseline. Once
frequency-dependent magnetic loss is admitted, the quasi-static inductive
scale must be allowed to move.

This screen keeps the current quasi-static hysteresis shape (c, k, etc.) and
KI fixed, but varies:
- quasi-static low-field inductive scale L_qs;
- classical dynamic-loss coefficient A_v;
- excess-loss coefficient B_v.

Primary metric:
complex magnetic-branch admittance at +4 dBu versus the accepted Jensen
loss-aware target:
    Y_target = 1 / (Rmag + j*w*Lmag)

HF leakage/capacitance are intentionally excluded here.

Only the best magnetic-admittance regions are then checked for the two 20 Hz
THD anchors. No parameter is promoted by this tool.
"""

import math
import cmath

import smx3_v2_iron_candidate as base
import smx3_v2_jensen_lossaware_target as target


FREQS=(20.0,50.0,100.0,200.0,1000.0)
LM_VALUES=(144.0,400.0,900.0,1600.0)
A_VALUES=(0.0,0.10,0.30)
B_VALUES=(0.0,0.03,0.10,0.30)


def kphi_for_lm(lm):
    return lm/(base.KI*(1.0+base.SLOPE0))


def solve_vnode(vs,H,lm,av,bv):
    rseries=base.RSOURCE+base.RP
    n=vs-rseries*H/base.KI
    if abs(n)<1e-30:
        return 0.0

    D=1.0+rseries/base.RLOAD+rseries*av/base.KI
    C=rseries*bv/base.KI

    disc=C*C+4.0*D*abs(n)
    u=(-C+math.sqrt(disc))/(2.0*D)
    return math.copysign(u*u,n)


def run(level_dbu,freq,lm,av,bv,fs=None,warmup_cycles=20,analysis_cycles=3):
    if fs is None:
        fs=max(24000.0,48.0*freq)

    kp=kphi_for_lm(lm)
    vrms=0.775*10.0**(level_dbu/20.0)
    amp=vrms*math.sqrt(2.0)
    dt=1.0/fs

    total=warmup_cycles+analysis_cycles
    n=int(round(total*fs/freq))
    start=int(round(warmup_cycles*fs/freq))

    H=0.0
    M=0.0

    y=[]
    re_v=im_v=0.0
    re_i=im_i=0.0

    def deriv(t,H,M):
        vs=amp*math.sin(2.0*math.pi*freq*t)
        vnode=solve_vnode(vs,H,lm,av,bv)
        direction=1.0 if vnode>=0.0 else -1.0
        slope=base.dmdh(H,M,direction)
        dH=vnode/(kp*(1.0+slope))
        dM=slope*dH
        vout=vnode*base.RL/base.RLOAD
        h_dyn=av*vnode
        if vnode!=0.0:
            h_dyn += bv*math.copysign(math.sqrt(abs(vnode)),vnode)
        imag=(H+h_dyn)/base.KI
        return dH,dM,vout,vnode,imag

    for idx in range(n):
        t=idx*dt

        k1h,k1m,v1,_,_=deriv(t,H,M)
        k2h,k2m,_,_,_=deriv(t+0.5*dt,H+0.5*dt*k1h,M+0.5*dt*k1m)
        k3h,k3m,_,_,_=deriv(t+0.5*dt,H+0.5*dt*k2h,M+0.5*dt*k2m)
        k4h,k4m,_,_,_=deriv(t+dt,H+dt*k3h,M+dt*k3m)

        H += dt*(k1h+2*k2h+2*k3h+k4h)/6.0
        M += dt*(k1m+2*k2m+2*k3m+k4m)/6.0

        if idx>=start:
            _,_,vout,vnode,imag=deriv(t+dt,H,M)
            local=idx-start
            a=2.0*math.pi*freq*local/fs
            c=math.cos(a); s=math.sin(a)

            re_v+=vnode*c
            im_v-=vnode*s
            re_i+=imag*c
            im_i-=imag*s
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
        return math.hypot(re,im)

    f1=comp(1)
    hs=[comp(h)/f1 for h in range(2,11)]
    thd=math.sqrt(sum(h*h for h in hs))

    return ymag,thd,hs


def target_y(freq):
    return 1.0/complex(target.RMAG,2.0*math.pi*freq*target.LMAG)


def admittance_cost(lm,av,bv):
    total=0.0
    detail=[]

    for f in FREQS:
        y,_,_=run(4.0,f,lm,av,bv)
        yt=target_y(f)

        # Normalize real and imaginary components separately to avoid the
        # larger susceptance hiding conductance mismatch.
        sr=max(abs(yt.real),0.05e-6)
        si=max(abs(yt.imag),0.05e-6)

        er=(y.real-yt.real)/sr
        ei=(y.imag-yt.imag)/si
        total+=er*er+ei*ei
        detail.append((f,y,yt,er,ei))

    return total/len(FREQS),detail


def main():
    ranked=[]

    print("SMX-3 V2 IRON joint low-field-L / dynamic-loss architecture screen")
    print("Scanning magnetic admittance only; no HF parasitics.")

    for lm in LM_VALUES:
        for av in A_VALUES:
            for bv in B_VALUES:
                cost,detail=admittance_cost(lm,av,bv)
                ranked.append((cost,lm,av,bv,detail))

    ranked.sort(key=lambda x:x[0])

    print()
    print("TOP MAGNETIC-ADMITTANCE REGIONS")
    print("rank,cost,L_qs_H,A_v,B_v")

    for i,(cost,lm,av,bv,_) in enumerate(ranked[:12],1):
        print(f"{i},{cost:.9f},{lm:.3f},{av:.6f},{bv:.6f}")

    print()
    print("DETAILED TOP 3")
    for rank,(cost,lm,av,bv,detail) in enumerate(ranked[:3],1):
        print(f"[{rank}] L_qs={lm:.3f} H A_v={av:.6f} B_v={bv:.6f} cost={cost:.9f}")
        print("freq,Y_model_re_uS,Y_model_im_uS,Y_target_re_uS,Y_target_im_uS")
        for f,y,yt,er,ei in detail:
            print(
                f"{f:.1f},{1e6*y.real:.9f},{1e6*y.imag:.9f},"
                f"{1e6*yt.real:.9f},{1e6*yt.imag:.9f}"
            )

    print()
    print("THD CHECK FOR TOP 5")
    print("rank,L_qs_H,A_v,B_v,H4_THD_pct,H20_THD_pct,H2_pct,H3_pct")

    for rank,(cost,lm,av,bv,_) in enumerate(ranked[:5],1):
        _,low,low_hs=run(4.0,20.0,lm,av,bv,fs=48000.0,warmup_cycles=30,analysis_cycles=4)
        _,high,_=run(20.0,20.0,lm,av,bv,fs=48000.0,warmup_cycles=30,analysis_cycles=4)

        print(
            f"{rank},{lm:.3f},{av:.6f},{bv:.6f},"
            f"{100*low:.9f},{100*high:.9f},"
            f"{100*low_hs[0]:.9f},{100*low_hs[1]:.9f}"
        )

    best=ranked[0]
    print()
    print("SCREEN DECISION:")
    if best[1] > 144.0:
        print("Best coarse magnetic-admittance region requires L_qs above the 144 H lossless-equivalent baseline.")
    else:
        print("Best coarse region remains near the 144 H baseline.")
    print("Next step: jointly refit c/KI only around the best L_qs/A_v/B_v region, then evaluate full Jensen DLP/magnitude.")
    print("No parameter from this coarse grid is promoted.")


if __name__=="__main__":
    raise SystemExit(main())
