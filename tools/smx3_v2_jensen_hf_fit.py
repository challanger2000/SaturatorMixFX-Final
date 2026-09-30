#!/usr/bin/env python3
"""Reduced high-frequency JT-11P-1 network identification for SMX-3 V2.

Topology (all quantities referred to a 1:1 primary side):
- source resistance Rs=600 ohm;
- documented primary DCR Rp=1.45 kohm;
- primary shunt magnetizing inductance Lm from the accepted LF skeleton;
- documented primary-to-shield capacitance Cp=98 pF;
- series leakage inductance Llk (fit parameter);
- secondary node with documented secondary-to-shield capacitance Cs=110 pF;
- effective additional secondary-side/interwinding shunt capacitance Cx
  (fit parameter, explicitly NOT claimed as the physical interwinding C);
- documented secondary DCR 1.55 kohm + 10 kohm load.

Fit targets:
- 20 kHz / 1 kHz = -0.05 dB typical;
- 95 kHz / 1 kHz = -3 dB approximate upper bandwidth.

Standard library only.
"""

import cmath
import math

RSOURCE=600.0
RP=1450.0
RSEC=1550.0
RL=10000.0
LM=143.999434
CP=98e-12
CS=110e-12

TARGET20=-0.05
TARGET95=-3.0


def solve2(a11,a12,a21,a22,b1,b2):
    det=a11*a22-a12*a21
    return (
        (b1*a22-a12*b2)/det,
        (a11*b2-b1*a21)/det,
    )


def transfer(freq,llk,cx):
    w=2.0*math.pi*freq
    j=1j

    zs=complex(RSOURCE+RP,0.0)
    yp=1.0/(j*w*LM)+j*w*CP

    # avoid singular ideal zero leakage in the search
    zlink=j*w*max(llk,1e-12)
    ylink=1.0/zlink

    yload=1.0/complex(RSEC+RL,0.0)+j*w*(CS+cx)

    # nodal equations with ideal source Vs=1:
    # (Vp-Vs)/Zs + Vp*Yp + (Vp-Vb)*Ylink = 0
    # (Vb-Vp)*Ylink + Vb*Yload = 0
    a11=1.0/zs+yp+ylink
    a12=-ylink
    a21=-ylink
    a22=ylink+yload
    b1=1.0/zs
    b2=0.0

    vp,vb=solve2(a11,a12,a21,a22,b1,b2)

    # Output across RL in the resistive secondary branch.
    return vb*RL/(RSEC+RL)


def dbmag(z):
    return 20.0*math.log10(abs(z))


def rel_db(freq,llk,cx,ref=1000.0):
    return dbmag(transfer(freq,llk,cx))-dbmag(transfer(ref,llk,cx))


def objective(logl,logc):
    llk=10.0**logl
    cx=10.0**logc
    e20=rel_db(20000.0,llk,cx)-TARGET20
    e95=rel_db(95000.0,llk,cx)-TARGET95
    return e20*e20+e95*e95,e20,e95


def fit():
    # Broad physically plausible research search:
    # leakage 1 uH .. 100 mH
    # effective extra shunt C 1 pF .. 20 nF
    best=None
    for i in range(81):
        logl=-6.0+i*(5.0/80.0)
        for k in range(87):
            logc=-12.0+k*(math.log10(2e-8)+12.0)/86.0
            o,e20,e95=objective(logl,logc)
            if best is None or o<best[0]:
                best=(o,logl,logc,e20,e95)

    # deterministic coordinate refinement in log space
    o,logl,logc,_,_=best
    step_l=0.15
    step_c=0.15
    for _ in range(80):
        improved=False
        current=objective(logl,logc)[0]
        for dl,dc in ((step_l,0),(-step_l,0),(0,step_c),(0,-step_c),
                      (step_l,step_c),(step_l,-step_c),(-step_l,step_c),(-step_l,-step_c)):
            nl=logl+dl
            nc=logc+dc
            if not (-6.0<=nl<=-1.0 and -12.0<=nc<=math.log10(2e-8)):
                continue
            cand=objective(nl,nc)[0]
            if cand<current:
                logl,logc=nl,nc
                current=cand
                improved=True
        if not improved:
            step_l*=0.5
            step_c*=0.5
            if max(step_l,step_c)<1e-6:
                break

    o,e20,e95=objective(logl,logc)
    return 10.0**logl,10.0**logc,o,e20,e95


def phase_deg(z):
    return math.degrees(cmath.phase(z))


def main():
    llk,cx,obj,e20,e95=fit()

    print("SMX-3 V2 JT-11P-1 reduced HF network fit")
    print(f"Llk = {llk*1e6:.9f} uH")
    print(f"Cp documented = {CP*1e12:.3f} pF")
    print(f"Cs documented = {CS*1e12:.3f} pF")
    print(f"Cx effective fitted = {cx*1e12:.9f} pF")
    print(f"objective = {obj:.12g}")
    print()

    print("freq_Hz,relative_dB,absolute_gain_dB,phase_deg")
    for f in (20.0,1000.0,10000.0,20000.0,50000.0,95000.0,150000.0):
        h=transfer(f,llk,cx)
        print(f"{f:.1f},{rel_db(f,llk,cx):.9f},{dbmag(h):.9f},{phase_deg(h):.9f}")

    r20=rel_db(20000.0,llk,cx)
    r95=rel_db(95000.0,llk,cx)

    print()
    print(f"20 kHz error vs -0.05 dB = {r20-TARGET20:+.9f} dB")
    print(f"95 kHz error vs -3.0 dB = {r95-TARGET95:+.9f} dB")

    if abs(r20-TARGET20)>0.01:
        raise SystemExit("FAIL: reduced HF network misses 20 kHz magnitude")
    if abs(r95-TARGET95)>0.10:
        raise SystemExit("FAIL: reduced HF network misses 95 kHz bandwidth")

    print("PASS: reduced two-parameter HF network reproduces the selected magnitude anchors.")
    print("WARNING: phase/DLP and parameter identifiability still gate promotion.")


if __name__=="__main__":
    raise SystemExit(main())
