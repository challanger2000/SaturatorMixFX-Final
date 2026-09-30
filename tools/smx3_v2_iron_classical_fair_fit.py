#!/usr/bin/env python3
"""Fair small-signal test of the classical dynamic-loss architecture.

The current classical dynamic field

    H_dyn = A_v * v_core

makes the low-field magnetizing current

    i_m = H/KI + (A_v/KI) * v_core

which is exactly a parallel inductance + conductance in the small-signal limit:

    Ymag = Gmag + 1/(s*Lmag)

Therefore the correct architecture test must fit BOTH:
- Lmag
- Gmag

instead of holding the 144 H lossless-equivalent inductance fixed.

HF parasitics are also allowed to fit:
- leakage inductance Llk
- effective extra shunt/interwinding capacitance Cx

The fit is tested against Jensen magnitude, 1 kHz gain/Z and DLP.
"""

import math, cmath
from smx3_v2_dlp_utils import dlp_degrees

RSOURCE=600.0
RP=1450.0
RSEC=1550.0
RL=10000.0
CP=98e-12
CS=110e-12

TARGETS={
    "gain1k":-2.3,
    "zin1k":13000.0,
    "r20":-0.04,
    "r20k":-0.05,
    "r95k":-3.0,
    "dlp20":0.6,
}


def solve2(a11,a12,a21,a22,b1,b2):
    det=a11*a22-a12*a21
    return ( (b1*a22-a12*b2)/det, (a11*b2-b1*a21)/det )


def transfer(freq,L,G,Llk,Cx,source_loaded=True):
    w=2*math.pi*freq; j=1j
    rs=RSOURCE if source_loaded else 0.0
    zs=complex(rs+RP,0)
    ymag=G + 1/(j*w*L) + j*w*CP
    ylink=1/(j*w*Llk)
    yload=1/complex(RSEC+RL,0)+j*w*(CS+Cx)
    a11=1/zs+ymag+ylink
    a12=-ylink
    a21=-ylink
    a22=ylink+yload
    vp,vb=solve2(a11,a12,a21,a22,1/zs,0)
    return vb*RL/(RSEC+RL)


def zin(freq,L,G,Llk,Cx):
    w=2*math.pi*freq; j=1j
    ymag=G + 1/(j*w*L) + j*w*CP
    zlink=j*w*Llk
    yload=1/complex(RSEC+RL,0)+j*w*(CS+Cx)
    zdown=zlink+1/yload
    return RP+1/(ymag+1/zdown)


def db(z): return 20*math.log10(abs(z))


def metrics(L,G,Llk,Cx):
    h1=transfer(1000,L,G,Llk,Cx,False)
    gain=db(h1)
    z1=abs(zin(1000,L,G,Llk,Cx))
    ref=db(transfer(1000,L,G,Llk,Cx,True))
    r20=db(transfer(20,L,G,Llk,Cx,True))-ref
    r20k=db(transfer(20000,L,G,Llk,Cx,True))-ref
    r95k=db(transfer(95000,L,G,Llk,Cx,True))-ref

    n=401
    freqs=[20*(20000/20)**(i/(n-1)) for i in range(n)]
    phases=[cmath.phase(transfer(f,L,G,Llk,Cx,True)) for f in freqs]
    d=dlp_degrees(freqs,phases)
    i20=0
    d20=d["residual_deg"][i20]

    return gain,z1,r20,r20k,r95k,d20,d["worst_abs_deg"]


def cost(params):
    L,G,Llk,Cx=params
    try:
        gain,z1,r20,r20k,r95k,d20,worst=metrics(L,G,Llk,Cx)
    except Exception:
        return 1e99
    return (
        ((gain+2.3)/0.03)**2
        +((z1-13000)/300)**2
        +((r20+0.04)/0.01)**2
        +((r20k+0.05)/0.01)**2
        +((r95k+3.0)/0.15)**2
        +((d20-0.6)/0.25)**2
        +(max(0,worst-2.0)/0.25)**2
    )


def fit():
    # log parameters: L 10..5000 H, G 1e-9..1e-2 S,
    # Llk 10uH..50mH, Cx 10pF..10nF.
    lo=[1.0,-9.0,-5.0,-11.0]
    hi=[math.log10(5000),-2.0,math.log10(.05),-8.0]

    # deterministic coarse coordinate seed set
    seeds=[]
    for L in (50,144,300,600,1000,2000):
        for R in (1e4,4e4,1e5,1e6,1e9):
            G=1/R
            seeds.append([math.log10(L),math.log10(G),math.log10(.0027),math.log10(1.1e-9)])

    best=None
    for s in seeds:
        p=s[:]
        step=[.25,.35,.20,.20]
        for _ in range(90):
            vals=[10**x for x in p]
            cur=cost(vals)
            moved=False
            for d in range(4):
                for sign in (-1,1):
                    q=p[:]; q[d]=max(lo[d],min(hi[d],q[d]+sign*step[d]))
                    v=cost([10**x for x in q])
                    if v<cur:
                        p=q;cur=v;moved=True
            if not moved:
                step=[x*.65 for x in step]
            if max(step)<2e-5: break
        vals=[10**x for x in p]
        v=cost(vals)
        if best is None or v<best[0]:
            best=(v,vals)
    return best


def main():
    score,(L,G,Llk,Cx)=fit()
    m=metrics(L,G,Llk,Cx)
    gain,z1,r20,r20k,r95k,d20,worst=m

    print("SMX-3 V2 classical-loss fair small-signal architecture test")
    print(f"Lmag = {L:.9f} H")
    print(f"Gmag = {G:.12g} S  (Rparallel = {1/G:.9f} ohm)")
    print(f"Llk = {Llk*1e3:.9f} mH")
    print(f"Cx = {Cx*1e12:.9f} pF")
    print(f"cost = {score:.9f}")
    print()
    print(f"gain1k = {gain:.9f} dB")
    print(f"Zin1k = {z1:.9f} ohm")
    print(f"rel20 = {r20:.9f} dB")
    print(f"rel20k = {r20k:.9f} dB")
    print(f"rel95k = {r95k:.9f} dB")
    print(f"DLP20 = {d20:+.9f} deg")
    print(f"DLP worst = {worst:.9f} deg")

    ok=(abs(gain+2.3)<=.05 and 12300<=z1<=13700 and
        abs(r20+.04)<=.01 and abs(r20k+.05)<=.01 and
        abs(r95k+3)<=.15 and worst<=2 and abs(d20-.6)<=.5)

    if ok:
        print("PASS: freely refitted parallel G||L classical-loss architecture can satisfy selected Jensen small-signal constraints.")
    else:
        print("REJECT: even with L and conductance jointly refitted, parallel G||L classical-loss architecture cannot satisfy selected Jensen constraints.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
