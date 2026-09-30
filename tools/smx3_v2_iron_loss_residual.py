#!/usr/bin/env python3
"""Decompose the missing low-field dynamic behavior for SMX-3 V2 IRON.

IMPORTANT:
This tool keeps electrical reference planes consistent.

Two comparisons are reported:

1) Transformer input terminals:
   Zja_terminal vs Jensen loss-aware Ztarget_terminal.
   The external 600-ohm generator resistance is excluded from BOTH.

2) Magnetizing branch only:
   Ymag_ja vs Ymag_target.
   HF leakage/shield/interwinding parasitics are excluded from the decision
   about magnetic/core-loss architecture.

Only comparison (2) may be used to decide the dynamic magnetic-loss branch.
"""

import math
import cmath

import smx3_v2_iron_candidate as ja
import smx3_v2_jensen_lossaware_target as target


FREQS=(20.0,30.0,50.0,80.0,100.0,200.0,500.0,1000.0,2000.0,5000.0,10000.0,20000.0)


def ja_fundamentals(freq,level_dbu=4.0,warmup_cycles=30,analysis_cycles=4):
    fs=max(48000.0,96.0*freq)
    vrms=0.775*10.0**(level_dbu/20.0)
    amp=vrms*math.sqrt(2.0)
    dt=1.0/fs

    total_cycles=warmup_cycles+analysis_cycles
    n=int(round(total_cycles*fs/freq))
    start=int(round(warmup_cycles*fs/freq))

    H=0.0
    M=0.0

    re_vs=im_vs=0.0
    re_vterm=im_vterm=0.0
    re_vnode=im_vnode=0.0
    re_itotal=im_itotal=0.0
    re_imag=im_imag=0.0

    for idx in range(n):
        t=idx*dt

        k1h,k1m,_=ja.deriv(t,H,M,amp,freq)
        k2h,k2m,_=ja.deriv(t+0.5*dt,H+0.5*dt*k1h,M+0.5*dt*k1m,amp,freq)
        k3h,k3m,_=ja.deriv(t+0.5*dt,H+0.5*dt*k2h,M+0.5*dt*k2m,amp,freq)
        k4h,k4m,_=ja.deriv(t+dt,H+dt*k3h,M+dt*k3m,amp,freq)

        H += dt*(k1h+2*k2h+2*k3h+k4h)/6.0
        M += dt*(k1m+2*k2m+2*k3m+k4m)/6.0

        if idx>=start:
            local=idx-start
            a=2.0*math.pi*freq*local/fs
            c=math.cos(a)
            s=math.sin(a)

            vs=amp*math.sin(2.0*math.pi*freq*t)

            # Same algebra as ja.deriv():
            # source -> RSOURCE -> RP -> parallel(magnetic branch, reflected load)
            rseries=ja.RSOURCE+ja.RP
            numerator=vs-rseries*H/ja.KI
            divider=1.0+rseries/ja.RLOAD
            vnode=numerator/divider

            imag=H/ja.KI
            iload=vnode/ja.RLOAD
            itotal=imag+iload

            # Voltage at the transformer's external primary terminals excludes
            # the documented 600-ohm generator/source resistance.
            vterm=vs-ja.RSOURCE*itotal

            re_vs+=vs*c; im_vs-=vs*s
            re_vterm+=vterm*c; im_vterm-=vterm*s
            re_vnode+=vnode*c; im_vnode-=vnode*s
            re_itotal+=itotal*c; im_itotal-=itotal*s
            re_imag+=imag*c; im_imag-=imag*s

    VTERM=complex(re_vterm,im_vterm)
    VNODE=complex(re_vnode,im_vnode)
    ITOTAL=complex(re_itotal,im_itotal)
    IMAG=complex(re_imag,im_imag)

    return {
        "z_terminal":VTERM/ITOTAL,
        "y_magnetic":IMAG/VNODE,
    }


def target_magnetic_admittance(freq):
    # Magnetic target ONLY. Do not include shield/interwinding/HF parasitics.
    w=2.0*math.pi*freq
    return 1.0/complex(target.RMAG,w*target.LMAG)


def main():
    print("SMX-3 V2 IRON corrected dynamic-loss residual decomposition")
    print()
    print("TERMINAL COMPARISON (source resistance excluded from both):")
    print("freq_Hz,Zja_re,Zja_im,Ztarget_re,Ztarget_im")
    terminal=[]

    print_rows=[]
    magnetic=[]

    for freq in FREQS:
        ja_f=ja_fundamentals(freq)
        zj=ja_f["z_terminal"]
        zt=target.input_impedance(freq)
        terminal.append((freq,zj,zt))

        ymj=ja_f["y_magnetic"]
        ymt=target_magnetic_admittance(freq)
        yr=ymt-ymj
        magnetic.append((freq,ymj,ymt,yr))

        print(f"{freq:.1f},{zj.real:.9f},{zj.imag:.9f},{zt.real:.9f},{zt.imag:.9f}")

    print()
    print("MAGNETIC-BRANCH RESIDUAL (HF parasitics excluded):")
    print("freq_Hz,Yja_re_uS,Yja_im_uS,Ytarget_re_uS,Ytarget_im_uS,Yres_re_uS,Yres_im_uS")

    for freq,yj,yt,yr in magnetic:
        print(
            f"{freq:.1f},"
            f"{1e6*yj.real:.9f},{1e6*yj.imag:.9f},"
            f"{1e6*yt.real:.9f},{1e6*yt.imag:.9f},"
            f"{1e6*yr.real:.9f},{1e6*yr.imag:.9f}"
        )

    neg_g=[(f,y.real) for f,_,_,y in magnetic if y.real < -1e-9]

    print()
    if neg_g:
        print("RESULT: magnetic residual requires negative conductance at sampled frequencies.")
        print("A passive parallel loss branch is therefore NOT a valid direct decomposition.")
        for f,g in neg_g:
            print(f" - {f:g} Hz: residual conductance {1e6*g:.6f} uS")
        print("DECISION: reformulate as dynamic JA effective-field/core-loss term rather than forcing a parallel passive branch.")
    else:
        print("RESULT: magnetic residual conductance is non-negative across sampled frequencies.")
        print("A passive auxiliary relaxation/loss branch remains structurally possible.")

    # Also report sign of susceptance. One simple RL or RC branch is only
    # plausible if the residual has compatible sign/shape.
    signs=set()
    for _,_,_,y in magnetic:
        if y.imag>1e-9: signs.add("capacitive")
        elif y.imag<-1e-9: signs.add("inductive")
        else: signs.add("near-zero")

    print("Residual susceptance signs:",", ".join(sorted(signs)))
    print("No auxiliary topology is promoted by this diagnostic alone.")

    return 0


if __name__=="__main__":
    raise SystemExit(main())
