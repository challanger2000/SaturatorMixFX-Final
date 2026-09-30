#!/usr/bin/env python3
"""One-state magnetic-relaxation small-signal architecture for SMX-3 V2 IRON.

Static JA low-field behavior is represented by a pure inductive equilibrium
branch Lstat.

A dynamic loss field obeys:

    tau * dHloss/dt + Hloss = K * dB/dt

Linearized at the transformer terminals this contributes the admittance:

    Yloss = Gloss / (1 + s*tau)

so the magnetic branch becomes:

    Ymag = 1/(s*Lstat) + Gloss/(1+s*tau)

The relaxation term vanishes in the quasi-static/DC limit in FIELD form
(Hloss -> 0 when dB/dt -> 0), so static JA hysteresis/remanence need not be
redefined.

Fit parameters:
- Lstat
- Gloss
- tau
- Llk
- effective Cx

Fixed documented values:
- source response Rs=600 ohm
- winding DCRs
- 10k load
- 98 pF / 110 pF shield capacitances

Targets:
- 1 kHz gain and input impedance
- 20 Hz and 20 kHz response
- ~95 kHz upper bandwidth
- Jensen DLP.
"""

import math, cmath
from smx3_v2_dlp_utils import dlp_degrees

RSOURCE=600.0
RP=1450.0
RSEC=1550.0
RL=10000.0
CP=98e-12
CS=110e-12


def solve2(a11,a12,a21,a22,b1,b2):
    det=a11*a22-a12*a21
    return ((b1*a22-a12*b2)/det,(a11*b2-b1*a21)/det)


def ymag(freq,Lstat,G,tau):
    s=1j*2*math.pi*freq
    return 1/(s*Lstat)+G/(1+s*tau)


def transfer(freq,Lstat,G,tau,Llk,Cx,source_loaded=True):
    s=1j*2*math.pi*freq
    rs=RSOURCE if source_loaded else 0.0
    zs=complex(rs+RP,0)
    yp=ymag(freq,Lstat,G,tau)+s*CP
    yl=1/(s*Llk)
    yload=1/complex(RSEC+RL,0)+s*(CS+Cx)

    a11=1/zs+yp+yl
    a12=-yl
    a21=-yl
    a22=yl+yload
    vp,vb=solve2(a11,a12,a21,a22,1/zs,0)
    return vb*RL/(RSEC+RL)


def zin(freq,Lstat,G,tau,Llk,Cx):
    s=1j*2*math.pi*freq
    yp=ymag(freq,Lstat,G,tau)+s*CP
    zlink=s*Llk
    yload=1/complex(RSEC+RL,0)+s*(CS+Cx)
    zdown=zlink+1/yload
    return RP+1/(yp+1/zdown)


def db(z): return 20*math.log10(abs(z))


def metrics(p):
    L,G,tau,Llk,Cx=p
    gain=db(transfer(1000,*p,source_loaded=False))
    z1=abs(zin(1000,*p))

    ref=db(transfer(1000,*p,source_loaded=True))
    r20=db(transfer(20,*p,source_loaded=True))-ref
    r20k=db(transfer(20000,*p,source_loaded=True))-ref
    r95k=db(transfer(95000,*p,source_loaded=True))-ref

    n=401
    freqs=[20*(20000/20)**(i/(n-1)) for i in range(n)]
    phases=[cmath.phase(transfer(f,*p,source_loaded=True)) for f in freqs]
    d=dlp_degrees(freqs,phases)
    d20=d["residual_deg"][0]

    return gain,z1,r20,r20k,r95k,d20,d["worst_abs_deg"]


def cost(p):
    try:m=metrics(p)
    except Exception:return 1e99
    gain,z1,r20,r20k,r95,d20,w=m
    return (
        ((gain+2.3)/.03)**2
        +((z1-13000)/250)**2
        +((r20+.04)/.0075)**2
        +((r20k+.05)/.0075)**2
        +((r95+3)/.12)**2
        +((d20-.6)/.20)**2
        +(max(0,w-2)/.20)**2
    )


def fit():
    # log10 bounds:
    # Lstat 50..10000 H
    # G 1e-9..1e-3 S
    # tau 1 us..100 ms
    # Llk 10 uH..50 mH
    # Cx 10 pF..10 nF
    lo=[math.log10(50),-9,-6,-5,-11]
    hi=[4,-3,-1,math.log10(.05),-8]

    seeds=[]
    for L in (300,600,1000,2000,5000):
      for R in (2e4,4e4,1e5,3e5):
        G=1/R
        for tau in (1e-4,5e-4,1e-3,5e-3,2e-2):
          seeds.append([math.log10(L),math.log10(G),math.log10(tau),math.log10(.00275),math.log10(1.15e-9)])

    best=None
    for p in seeds:
        p=p[:]
        step=[.22,.25,.22,.16,.16]
        for _ in range(85):
            cur=cost([10**x for x in p])
            moved=False
            for d in range(5):
                for sign in (-1,1):
                    q=p[:]
                    q[d]=max(lo[d],min(hi[d],q[d]+sign*step[d]))
                    v=cost([10**x for x in q])
                    if v<cur:
                        p=q;cur=v;moved=True
            if not moved: step=[x*.62 for x in step]
            if max(step)<3e-5: break
        vals=[10**x for x in p]
        v=cost(vals)
        if best is None or v<best[0]:best=(v,vals)
    return best


def main():
    score,p=fit()
    L,G,tau,Llk,Cx=p
    gain,z1,r20,r20k,r95,d20,w=metrics(p)

    print("SMX-3 V2 one-state magnetic-relaxation small-signal fit")
    print(f"Lstat = {L:.9f} H")
    print(f"Gloss = {G:.12g} S  (Rscale={1/G:.9f} ohm)")
    print(f"tau = {tau*1e3:.9f} ms")
    print(f"Llk = {Llk*1e3:.9f} mH")
    print(f"Cx = {Cx*1e12:.9f} pF")
    print(f"cost = {score:.9f}")
    print()
    print(f"gain1k = {gain:.9f} dB")
    print(f"Zin1k = {z1:.9f} ohm")
    print(f"rel20 = {r20:.9f} dB")
    print(f"rel20k = {r20k:.9f} dB")
    print(f"rel95k = {r95:.9f} dB")
    print(f"DLP20 = {d20:+.9f} deg")
    print(f"DLP worst = {w:.9f} deg")

    ok=(abs(gain+2.3)<=.05 and 12300<=z1<=13700 and
        abs(r20+.04)<=.01 and abs(r20k+.05)<=.01 and
        abs(r95+3)<=.15 and abs(d20-.6)<=.5 and w<=2)

    if ok:
        print("PASS: one magnetic-relaxation state can reproduce selected Jensen small-signal magnitude/impedance/DLP constraints.")
    else:
        print("REJECT: one magnetic-relaxation state is insufficient for selected Jensen small-signal constraints.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
