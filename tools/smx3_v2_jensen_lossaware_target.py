#!/usr/bin/env python3
"""Loss-aware small-signal JT-11P-1 target for SMX-3 V2 IRON.

This is NOT the production nonlinear magnetic model.

Purpose:
derive a passive small-signal target impedance that simultaneously reproduces:
- Jensen low-frequency response;
- Jensen high-frequency response;
- approximate 95 kHz upper bandwidth;
- 1 kHz transformer gain/input impedance;
- Jensen deviation-from-linear-phase behavior.

Topology:
- source resistance for response/DLP tests: 600 ohm;
- primary DCR 1.45 kohm;
- magnetizing branch represented by series Rmag + j*w*Lmag;
- documented primary-to-shield capacitance 98 pF;
- series leakage inductance Llk;
- secondary branch with DCR 1.55 kohm + 10 kohm load;
- documented secondary-to-shield capacitance 110 pF;
- effective extra shunt/interwinding capacitance Cx.

All fitted parameters are EFFECTIVE reduced-network quantities, not claimed
manufacturer construction values.
"""

import math
import cmath
from smx3_v2_dlp_utils import dlp_degrees

RSOURCE=600.0
RP=1450.0
RSEC=1550.0
RL=10000.0
CP=98e-12
CS=110e-12

# Empirically tuned to documented JT-11P-1 anchors.
LMAG=922.410687550444
RMAG=38991.056797481375
LLK=0.0027503962409619375
CX=1.1548469560690703e-9

MIN_Z=12300.0
TYP_Z=13000.0
MAX_Z=13700.0


def solve2(a11,a12,a21,a22,b1,b2):
    det=a11*a22-a12*a21
    return (
        (b1*a22-a12*b2)/det,
        (a11*b2-b1*a21)/det,
    )


def transfer(freq,source_loaded=True):
    w=2.0*math.pi*freq
    j=1j

    rsource=RSOURCE if source_loaded else 0.0
    zseries=complex(rsource+RP,0.0)

    # Loss-aware magnetizing branch + documented primary shield capacitance.
    ymag=1.0/complex(RMAG,w*LMAG)+j*w*CP

    zlink=j*w*LLK
    ylink=1.0/zlink

    yload=1.0/complex(RSEC+RL,0.0)+j*w*(CS+CX)

    a11=1.0/zseries+ymag+ylink
    a12=-ylink
    a21=-ylink
    a22=ylink+yload
    b1=1.0/zseries
    b2=0.0

    vp,vs=solve2(a11,a12,a21,a22,b1,b2)
    return vs*RL/(RSEC+RL)


def input_impedance(freq):
    w=2.0*math.pi*freq
    j=1j

    ymag=1.0/complex(RMAG,w*LMAG)+j*w*CP
    zlink=j*w*LLK
    yload=1.0/complex(RSEC+RL,0.0)+j*w*(CS+CX)

    zdown=zlink+1.0/yload
    znode=1.0/(ymag+1.0/zdown)
    return RP+znode


def db(z):
    return 20.0*math.log10(abs(z))


def relative_db(freq):
    return db(transfer(freq,True))-db(transfer(1000.0,True))


def dlp():
    n=1201
    f0=20.0
    f1=20000.0
    freqs=[f0*(f1/f0)**(i/(n-1)) for i in range(n)]
    phases=[cmath.phase(transfer(f,True)) for f in freqs]
    d=dlp_degrees(freqs,phases)
    return freqs,d["residual_deg"],d["delay_s"]
def main():
    gain_1k=db(transfer(1000.0,False))
    zin=abs(input_impedance(1000.0))

    r20=relative_db(20.0)
    r20k=relative_db(20000.0)
    r95=relative_db(95000.0)

    freqs,res,tau=dlp()
    lo=min(res); hi=max(res); worst=max(abs(lo),abs(hi))

    print("SMX-3 V2 JT-11P-1 loss-aware small-signal target")
    print(f"Lmag = {LMAG:.9f} H")
    print(f"Rmag = {RMAG:.9f} ohm")
    print(f"Llk = {LLK*1e3:.9f} mH")
    print(f"Cx effective = {CX*1e12:.9f} pF")
    print(f"Cp documented = {CP*1e12:.3f} pF")
    print(f"Cs documented = {CS*1e12:.3f} pF")
    print()
    print(f"1 kHz transformer gain = {gain_1k:.9f} dB")
    print(f"1 kHz input impedance = {zin:.9f} ohm")
    print(f"20 Hz relative response = {r20:.9f} dB")
    print(f"20 kHz relative response = {r20k:.9f} dB")
    print(f"95 kHz relative response = {r95:.9f} dB")
    print(f"best-fit delay = {tau*1e6:.9f} us")
    print(f"DLP min = {lo:+.9f} deg")
    print(f"DLP max = {hi:+.9f} deg")
    print(f"DLP worst abs = {worst:.9f} deg")

    for f in (20.0,30.0,50.0,100.0,200.0,1000.0,10000.0,20000.0):
        idx=min(range(len(freqs)),key=lambda i:abs(freqs[i]-f))
        print(f"DLP {freqs[idx]:.3f} Hz = {res[idx]:+.9f} deg")

    failures=[]

    if abs(gain_1k-(-2.3))>0.05:
        failures.append("1 kHz transformer gain")
    if not (MIN_Z<=zin<=MAX_Z):
        failures.append("1 kHz input impedance outside Jensen min/max")
    if abs(r20-(-0.04))>0.01:
        failures.append("20 Hz response")
    if abs(r20k-(-0.05))>0.01:
        failures.append("20 kHz response")
    if abs(r95-(-3.0))>0.10:
        failures.append("95 kHz bandwidth")
    if worst>2.0:
        failures.append("DLP maximum")
    if not (0.2<=hi<=1.2):
        failures.append("DLP low-frequency typical shape")

    if failures:
        print("FAIL:")
        for f in failures:
            print(" - "+f)
        return 1

    print("PASS: loss-aware small-signal target reproduces selected Jensen magnitude/impedance/phase constraints.")
    print("WARNING: fitted R/L/C values are effective reduced-network parameters, not physical construction claims.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
