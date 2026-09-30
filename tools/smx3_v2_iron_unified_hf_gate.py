#!/usr/bin/env python3
"""Integrated small-signal HF gate for the frozen SMX-3 V2 IRON candidate.

Combines the frozen JA+relaxation small-signal magnetic admittance with the
effective JT-11P-1 leakage/capacitance network. This is an architecture gate:
it verifies that the already-accepted magnetic relaxation model and HF
parasitics remain mutually consistent when combined.

Effective reduced-network parameters are not physical construction claims.
"""

import cmath
import math

import smx3_v2_iron_unified_candidate as iron
from smx3_v2_dlp_utils import dlp_degrees

CP=98e-12
CS=110e-12
LLK=0.0027503962409619375
CX=1.1548469560690703e-9

MIN_Z=12300.0
MAX_Z=13700.0


def solve2(a11,a12,a21,a22,b1,b2):
    det=a11*a22-a12*a21
    return (
        (b1*a22-a12*b2)/det,
        (a11*b2-b1*a21)/det,
    )


def magnetic_admittance(freq):
    s=1j*2.0*math.pi*freq
    return 1.0/(s*iron.LSTAT)+iron.GREL/(1.0+s*iron.TAU)


def transfer(freq,source_loaded=True):
    s=1j*2.0*math.pi*freq
    rsource=iron.RSOURCE if source_loaded else 0.0
    zseries=complex(rsource+iron.RP,0.0)

    ymag=magnetic_admittance(freq)+s*CP
    zlink=s*LLK
    ylink=1.0/zlink
    yload=1.0/complex(iron.RSEC+iron.RL,0.0)+s*(CS+CX)

    a11=1.0/zseries+ymag+ylink
    a12=-ylink
    a21=-ylink
    a22=ylink+yload
    vp,vs=solve2(a11,a12,a21,a22,1.0/zseries,0.0)
    return vs*iron.RL/(iron.RSEC+iron.RL)


def input_impedance(freq):
    s=1j*2.0*math.pi*freq
    ymag=magnetic_admittance(freq)+s*CP
    zlink=s*LLK
    yload=1.0/complex(iron.RSEC+iron.RL,0.0)+s*(CS+CX)
    zdown=zlink+1.0/yload
    znode=1.0/(ymag+1.0/zdown)
    return iron.RP+znode


def db(z):
    return 20.0*math.log10(abs(z))


def relative_db(freq):
    return db(transfer(freq,True))-db(transfer(1000.0,True))


def main():
    gain_1k=db(transfer(1000.0,False))
    zin_1k=abs(input_impedance(1000.0))
    r20=relative_db(20.0)
    r20k=relative_db(20000.0)
    r95=relative_db(95000.0)

    n=1201
    f0=20.0
    f1=20000.0
    freqs=[f0*(f1/f0)**(i/(n-1)) for i in range(n)]
    phases=[cmath.phase(transfer(f,True)) for f in freqs]
    d=dlp_degrees(freqs,phases)
    lo=min(d["residual_deg"])
    hi=max(d["residual_deg"])
    worst=max(abs(lo),abs(hi))

    print("SMX-3 V2 unified IRON + HF parasitics integration gate")
    print(f"Lstat = {iron.LSTAT:.9f} H")
    print(f"Grel = {iron.GREL:.12e} S")
    print(f"tau = {iron.TAU*1e3:.9f} ms")
    print(f"Llk = {LLK*1e3:.9f} mH")
    print(f"Cp = {CP*1e12:.3f} pF")
    print(f"Cs = {CS*1e12:.3f} pF")
    print(f"Cx effective = {CX*1e12:.9f} pF")
    print()
    print(f"1 kHz transformer-port gain = {gain_1k:.9f} dB")
    print(f"1 kHz input impedance = {zin_1k:.9f} ohm")
    print(f"20 Hz relative response = {r20:+.9f} dB")
    print(f"20 kHz relative response = {r20k:+.9f} dB")
    print(f"95 kHz relative response = {r95:+.9f} dB")
    print(f"best-fit delay = {d['delay_s']*1e6:.9f} us")
    print(f"DLP min = {lo:+.9f} deg")
    print(f"DLP max = {hi:+.9f} deg")
    print(f"DLP worst abs = {worst:.9f} deg")

    failures=[]
    if abs(gain_1k-(-2.3))>0.05:
        failures.append("1 kHz transformer-port gain")
    if not (MIN_Z<=zin_1k<=MAX_Z):
        failures.append("1 kHz input impedance")
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
        for item in failures:
            print(" - "+item)
        return 1

    print("PASS: frozen unified magnetic relaxation and HF parasitics satisfy selected Jensen small-signal gates together.")
    print("WARNING: Llk/Cx are effective reduced-network parameters, not physical construction claims.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
