#!/usr/bin/env python3
"""Fixed verifier for the one-state SMX-3 V2 IRON relaxation candidate.

These are EFFECTIVE small-signal identification values, not manufacturer
construction or material constants.

Candidate:
- Lstat = 1121.98972 H
- Gloss = 3.07834453 uS
- tau = 0.375428689 ms
- Llk = 2.69380545 mH
- Cx = 1156.92464 pF

Architecture:
    Ymag = 1/(s*Lstat) + Gloss/(1+s*tau)

Equivalent dynamic field state:
    tau*dHloss/dt + Hloss = K*dB/dt

with Hloss -> 0 in the quasi-static/DC limit.
"""

import math, cmath
from smx3_v2_dlp_utils import dlp_degrees

RSOURCE=600.0
RP=1450.0
RSEC=1550.0
RL=10000.0
CP=98e-12
CS=110e-12

LSTAT=1121.98972
GLOSS=3.07834453e-6
TAU=0.000375428689
LLK=0.00269380545
CX=1.15692464e-9


def solve2(a11,a12,a21,a22,b1,b2):
    det=a11*a22-a12*a21
    return ((b1*a22-a12*b2)/det,(a11*b2-b1*a21)/det)


def ymag(freq):
    s=1j*2*math.pi*freq
    return 1/(s*LSTAT)+GLOSS/(1+s*TAU)


def transfer(freq,source_loaded=True):
    s=1j*2*math.pi*freq
    rs=RSOURCE if source_loaded else 0.0
    zs=complex(rs+RP,0)
    yp=ymag(freq)+s*CP
    yl=1/(s*LLK)
    yload=1/complex(RSEC+RL,0)+s*(CS+CX)
    a11=1/zs+yp+yl
    a12=-yl
    a21=-yl
    a22=yl+yload
    vp,vb=solve2(a11,a12,a21,a22,1/zs,0)
    return vb*RL/(RSEC+RL)


def zin(freq):
    s=1j*2*math.pi*freq
    yp=ymag(freq)+s*CP
    zlink=s*LLK
    yload=1/complex(RSEC+RL,0)+s*(CS+CX)
    zdown=zlink+1/yload
    return RP+1/(yp+1/zdown)


def db(z): return 20*math.log10(abs(z))


def main():
    gain=db(transfer(1000,False))
    z1=abs(zin(1000))
    ref=db(transfer(1000,True))
    r20=db(transfer(20,True))-ref
    r20k=db(transfer(20000,True))-ref
    r95=db(transfer(95000,True))-ref

    n=1201
    freqs=[20*(20000/20)**(i/(n-1)) for i in range(n)]
    phases=[cmath.phase(transfer(f,True)) for f in freqs]
    d=dlp_degrees(freqs,phases)
    d20=d["residual_deg"][0]

    print("SMX-3 V2 fixed one-state IRON relaxation candidate")
    print(f"Lstat={LSTAT:.9f} H")
    print(f"Gloss={GLOSS:.12g} S")
    print(f"tau={TAU*1e3:.9f} ms")
    print(f"Llk={LLK*1e3:.9f} mH")
    print(f"Cx={CX*1e12:.9f} pF")
    print()
    print(f"gain1k={gain:.9f} dB")
    print(f"Zin1k={z1:.9f} ohm")
    print(f"rel20={r20:.9f} dB")
    print(f"rel20k={r20k:.9f} dB")
    print(f"rel95k={r95:.9f} dB")
    print(f"DLP20={d20:+.9f} deg")
    print(f"DLPmin={d['min_deg']:+.9f} deg")
    print(f"DLPmax={d['max_deg']:+.9f} deg")
    print(f"DLPworst={d['worst_abs_deg']:.9f} deg")

    failures=[]
    if abs(gain+2.3)>.05: failures.append("1 kHz gain")
    if not 12300<=z1<=13700: failures.append("1 kHz Zin")
    if abs(r20+.04)>.01: failures.append("20 Hz response")
    if abs(r20k+.05)>.01: failures.append("20 kHz response")
    if abs(r95+3)>.15: failures.append("95 kHz response")
    if abs(d20-.6)>.5: failures.append("20 Hz DLP")
    if d["worst_abs_deg"]>2: failures.append("DLP maximum")

    if failures:
        print("FAIL:")
        for x in failures: print(" - "+x)
        return 1

    print("PASS: one-state relaxation candidate reproduces selected Jensen small-signal constraints.")
    print("WARNING: parameters are effective model-fit quantities only.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
