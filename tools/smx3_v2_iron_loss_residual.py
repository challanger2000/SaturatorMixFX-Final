#!/usr/bin/env python3
"""Decompose the missing low-field dynamic loss for SMX-3 V2 IRON.

Goal:
compare the accepted quasi-static Jiles-Atherton candidate with the
loss-aware Jensen small-signal target and determine whether the residual
small-signal admittance can be represented by a passive causal auxiliary
branch.

This is architecture research only.

Method:
1. Measure the settled +4 dBu fundamental input impedance of the current JA
   candidate over frequency.
2. Compute the loss-aware target input impedance at the same frequencies.
3. Form the residual admittance:
       Yaux = 1/Ztarget - 1/Zja
4. Inspect passivity:
       Re(Yaux) >= 0
5. Fit the residual to a simple series-RL branch:
       Yfit = 1 / (Raux + j*w*Laux)

If the residual is not passive or one RL branch is structurally inadequate,
do not force it; move to a higher-order relaxation network.
"""

import cmath
import math

import smx3_v2_iron_candidate as ja
import smx3_v2_jensen_lossaware_target as target


FREQS=(20.0,30.0,50.0,80.0,100.0,200.0,500.0,1000.0,2000.0,5000.0,10000.0,20000.0)


def ja_input_impedance(freq,level_dbu=4.0,warmup_cycles=30,analysis_cycles=4):
    fs=max(48000.0,96.0*freq)
    vrms=0.775*10.0**(level_dbu/20.0)
    amp=vrms*math.sqrt(2.0)
    dt=1.0/fs

    total_cycles=warmup_cycles+analysis_cycles
    n=int(round(total_cycles*fs/freq))
    start=int(round(warmup_cycles*fs/freq))

    H=0.0
    M=0.0

    # Fundamental of source voltage and total primary current.
    re_v=im_v=0.0
    re_i=im_i=0.0

    for idx in range(n):
        t=idx*dt

        k1h,k1m,vnode1=ja.deriv(t,H,M,amp,freq)
        k2h,k2m,_=ja.deriv(t+0.5*dt,H+0.5*dt*k1h,M+0.5*dt*k1m,amp,freq)
        k3h,k3m,_=ja.deriv(t+0.5*dt,H+0.5*dt*k2h,M+0.5*dt*k2m,amp,freq)
        k4h,k4m,_=ja.deriv(t+dt,H+dt*k3h,M+dt*k3m,amp,freq)

        H += dt*(k1h+2*k2h+2*k3h+k4h)/6.0
        M += dt*(k1m+2*k2m+2*k3m+k4m)/6.0

        if idx>=start:
            local=idx-start
            a=2.0*math.pi*freq*local/fs

            vs=amp*math.sin(2.0*math.pi*freq*t)

            # From the coupled circuit:
            # magnetizing current = H/KI
            # reflected loaded-secondary current = vnode/RLOAD
            # vnode follows directly from the same algebra as ja.deriv().
            rseries=ja.RSOURCE+ja.RP
            numerator=vs-rseries*H/ja.KI
            divider=1.0+rseries/ja.RLOAD
            vnode=numerator/divider
            ip=H/ja.KI + vnode/ja.RLOAD

            re_v += vs*math.cos(a)
            im_v -= vs*math.sin(a)
            re_i += ip*math.cos(a)
            im_i -= ip*math.sin(a)

    V=complex(re_v,im_v)
    I=complex(re_i,im_i)
    return V/I


def target_input_impedance(freq):
    # Jensen target input impedance looking into transformer terminals.
    return target.input_impedance(freq)


def fit_series_rl(freqs,yaux):
    # Coarse deterministic log-grid + refinement.
    # broad effective search: R=100..1e7 ohm, L=1 mH..1e5 H
    best=None

    def err(logr,logl):
        R=10.0**logr
        L=10.0**logl
        s=0.0
        for f,y in zip(freqs,yaux):
            yf=1.0/complex(R,2.0*math.pi*f*L)
            scale=max(abs(y),1e-12)
            d=(yf-y)/scale
            s += d.real*d.real+d.imag*d.imag
        return s/len(freqs)

    for ir in range(61):
        lr=2.0+5.0*ir/60.0
        for il in range(61):
            ll=-3.0+8.0*il/60.0
            e=err(lr,ll)
            if best is None or e<best[0]:
                best=(e,lr,ll)

    e,lr,ll=best
    step=.20
    for _ in range(70):
        current=err(lr,ll)
        improved=False
        for dr,dl in ((step,0),(-step,0),(0,step),(0,-step),(step,step),(step,-step),(-step,step),(-step,-step)):
            nr=lr+dr; nl=ll+dl
            if not (2.0<=nr<=7.0 and -3.0<=nl<=5.0):
                continue
            ne=err(nr,nl)
            if ne<current:
                lr,ll=nr,nl
                current=ne
                improved=True
        if not improved:
            step*=0.5
        if step<1e-5:
            break

    return 10.0**lr,10.0**ll,err(lr,ll)


def main():
    rows=[]
    yaux=[]

    print("SMX-3 V2 IRON missing dynamic-admittance decomposition")
    print("freq_Hz,Zja_re,Zja_im,Ztarget_re,Ztarget_im,Yaux_re_uS,Yaux_im_uS")

    for f in FREQS:
        zja=ja_input_impedance(f)
        zt=target_input_impedance(f)
        ya=1.0/zt-1.0/zja
        rows.append((f,zja,zt,ya))
        yaux.append(ya)
        print(
            f"{f:.1f},{zja.real:.9f},{zja.imag:.9f},"
            f"{zt.real:.9f},{zt.imag:.9f},"
            f"{1e6*ya.real:.9f},{1e6*ya.imag:.9f}"
        )

    neg=[(f,y.real) for f,y in zip(FREQS,yaux) if y.real < -1e-9]

    print()
    if neg:
        print("PASSIVITY WARNING: residual admittance has negative conductance at:")
        for f,g in neg:
            print(f" - {f:g} Hz: {1e6*g:.6f} uS")
    else:
        print("Residual conductance is non-negative across sampled frequencies.")

    R,L,e=fit_series_rl(FREQS,yaux)
    print()
    print("Best single series-RL residual fit:")
    print(f"Raux = {R:.9f} ohm")
    print(f"Laux = {L:.9f} H")
    print(f"normalized complex fit error = {e:.9f}")
    print("freq_Hz,Yaux_re_uS,Yaux_im_uS,Yfit_re_uS,Yfit_im_uS")

    for f,y in zip(FREQS,yaux):
        yf=1.0/complex(R,2.0*math.pi*f*L)
        print(f"{f:.1f},{1e6*y.real:.9f},{1e6*y.imag:.9f},{1e6*yf.real:.9f},{1e6*yf.imag:.9f}")

    if neg:
        print()
        print("DECISION: do not add a passive parallel branch directly; the residual definition/topology needs reformulation.")
    elif e<0.05:
        print()
        print("DECISION: one passive series-RL auxiliary branch is a plausible first dynamic-loss architecture.")
    else:
        print()
        print("DECISION: residual is passive but one series-RL branch is insufficient; use a higher-order relaxation network.")

    return 0


if __name__=="__main__":
    raise SystemExit(main())
