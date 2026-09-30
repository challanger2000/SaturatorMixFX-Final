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
from smx3_v2_dlp_utils import dlp_degrees



def main():
    # log-spaced evaluation density, but linear phase is fitted against
    # frequency itself because pure delay gives phi=-2*pi*f*tau.
    llk,cx,_,_,_=hf.fit()

    print(f"using refit Llk = {llk*1e6:.9f} uH")
    print(f"using refit Cx = {cx*1e12:.9f} pF")

    n=1201
    f0=20.0
    f1=20000.0
    freqs=[
        f0*(f1/f0)**(i/(n-1))
        for i in range(n)
    ]

    phases=[cmath.phase(hf.transfer(f,llk,cx)) for f in freqs]
    d=dlp_degrees(freqs,phases)
    residual=d["residual_deg"]
    lo=d["min_deg"]
    hi=d["max_deg"]
    worst=d["worst_abs_deg"]
    span=hi-lo
    tau=d["delay_s"]

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
