#!/usr/bin/env python3
"""DLP validation for the reduced JT-11P-1 HF network.

Jensen specifies deviation from linear phase (DLP) over 20 Hz..20 kHz:
- typical approximately +0.6 degrees
- maximum +/-2.0 degrees

This tool removes the best-fit linear phase phi(f)=a+b*f from the reduced
HF-network phase and measures the residual.

The least-squares best-fit delay is a conservative research diagnostic:
if even the best linear fit leaves > +/-2 deg residual, the reduced topology
cannot satisfy the manufacturer DLP constraint.
"""

import math
import cmath

import smx3_v2_jensen_hf_fit as hf


LLK=2755.715474630e-6
CX=1155.036777196e-12


def unwrap(phases):
    out=[phases[0]]
    for p in phases[1:]:
        q=p
        while q-out[-1] > math.pi:
            q-=2.0*math.pi
        while q-out[-1] < -math.pi:
            q+=2.0*math.pi
        out.append(q)
    return out


def fit_line(xs,ys):
    n=len(xs)
    sx=sum(xs); sy=sum(ys)
    sxx=sum(x*x for x in xs)
    sxy=sum(x*y for x,y in zip(xs,ys))
    den=n*sxx-sx*sx
    b=(n*sxy-sx*sy)/den
    a=(sy-b*sx)/n
    return a,b


def main():
    # log-spaced evaluation density, but linear phase is fitted against
    # frequency itself because pure delay gives phi=-2*pi*f*tau.
    n=1201
    f0=20.0
    f1=20000.0
    freqs=[
        f0*(f1/f0)**(i/(n-1))
        for i in range(n)
    ]

    phases=unwrap([
        cmath.phase(hf.transfer(f,LLK,CX))
        for f in freqs
    ])

    a,b=fit_line(freqs,phases)
    residual=[
        math.degrees(p-(a+b*f))
        for f,p in zip(freqs,phases)
    ]

    lo=min(residual)
    hi=max(residual)
    worst=max(abs(lo),abs(hi))
    span=hi-lo

    tau=-b/(2.0*math.pi)

    print("SMX-3 V2 reduced IRON HF-network DLP check")
    print(f"best-fit delay = {1e6*tau:.9f} us")
    print(f"residual min = {lo:+.9f} deg")
    print(f"residual max = {hi:+.9f} deg")
    print(f"residual span = {span:.9f} deg")
    print(f"worst absolute DLP = {worst:.9f} deg")
    print("Jensen maximum = +/-2.0 deg")

    for f in (20.0,100.0,1000.0,10000.0,20000.0):
        idx=min(range(n),key=lambda i:abs(freqs[i]-f))
        print(f"{freqs[idx]:.3f} Hz: residual {residual[idx]:+.9f} deg")

    if worst>2.0:
        print("REJECT: magnitude-fit topology violates Jensen maximum DLP.")
        return 0

    print("PASS: reduced topology remains inside Jensen maximum DLP.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
