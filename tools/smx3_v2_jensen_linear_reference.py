#!/usr/bin/env python3
"""Linear JT-11P-1 reference derivation for SMX-3 V2 IRON.

Important test-condition split:
- Jensen input impedance and voltage gain characterize the transformer itself;
- Jensen 20 Hz / 20 kHz magnitude-response rows explicitly specify Rs=600 ohm.

The magnetizing inductance must therefore be derived with the 600-ohm source
resistance present in the magnitude-response test circuit.

Standard library only.
"""

import cmath
import math

RSOURCE_RESPONSE = 600.0
RP = 1450.0
RS = 1550.0
RL = 10000.0
TARGET_20HZ_REL_DB = -0.04


def parallel(a,b):
    return 1.0/(1.0/a+1.0/b)


def transformer_transfer(f_hz,lm_h):
    """Voltage gain from transformer input terminals to load."""
    zload=complex(RS+RL,0.0)
    zm=1j*2.0*math.pi*f_hz*lm_h
    zbranch=parallel(zload,zm)
    return zbranch/(RP+zbranch) * RL/(RS+RL)


def response_test_transfer(f_hz,lm_h):
    """Generator voltage to load for Jensen response test with Rs=600 ohm."""
    zload=complex(RS+RL,0.0)
    zm=1j*2.0*math.pi*f_hz*lm_h
    zbranch=parallel(zload,zm)
    return zbranch/(RSOURCE_RESPONSE+RP+zbranch) * RL/(RS+RL)


def input_impedance(f_hz,lm_h):
    """Input impedance looking into transformer terminals, excluding source R."""
    zload=complex(RS+RL,0.0)
    zm=1j*2.0*math.pi*f_hz*lm_h
    return RP+parallel(zload,zm)


def db(x):
    return 20.0*math.log10(abs(x))


def relative_response_db(f_hz,lm_h,ref_hz=1000.0):
    return db(response_test_transfer(f_hz,lm_h))-db(response_test_transfer(ref_hz,lm_h))


def solve_lm():
    lo=0.01
    hi=10000.0
    for _ in range(180):
        mid=0.5*(lo+hi)
        r=relative_response_db(20.0,mid)
        if r<TARGET_20HZ_REL_DB:
            lo=mid
        else:
            hi=mid
    return 0.5*(lo+hi)


def main():
    lm=solve_lm()

    print("SMX-3 V2 JT-11P-1 corrected linear reference")
    print(f"response-test source resistance = {RSOURCE_RESPONSE:.3f} ohm")
    print(f"Rp = {RP:.3f} ohm")
    print(f"Rs = {RS:.3f} ohm")
    print(f"RL = {RL:.3f} ohm")
    print(f"derived Lm = {lm:.9f} H")
    print()

    print("freq_hz,transformer_gain_db,response_rel_1k_db,input_Z_mag_ohm,transformer_phase_deg")
    for f in (20.0,1000.0,20000.0):
        h=transformer_transfer(f,lm)
        zin=input_impedance(f,lm)
        phase=math.degrees(cmath.phase(h))
        print(f"{f:.1f},{db(h):.9f},{relative_response_db(f,lm):.9f},{abs(zin):.9f},{phase:.9f}")

    gain_1k=db(transformer_transfer(1000.0,lm))
    zin_1k=abs(input_impedance(1000.0,lm))
    rel_20=relative_response_db(20.0,lm)

    print()
    print(f"1 kHz transformer gain error vs -2.3 dB: {gain_1k-(-2.3):+.6f} dB")
    print(f"1 kHz Zin error vs 13.0 kOhm: {(zin_1k-13000.0):+.3f} ohm")
    print(f"20 Hz response-test error vs -0.04 dB: {rel_20-(-0.04):+.9f} dB")

    if abs(gain_1k-(-2.3))>0.05:
        raise SystemExit("FAIL: transformer skeleton misses Jensen 1 kHz gain")
    if abs(zin_1k-13000.0)>50.0:
        raise SystemExit("FAIL: transformer skeleton misses Jensen 1 kHz input impedance")
    if abs(rel_20-(-0.04))>1e-6:
        raise SystemExit("FAIL: corrected Lm solve misses Jensen 20 Hz response test")

    print("PASS: corrected test-condition split reproduces selected Jensen anchors.")


if __name__=="__main__":
    main()
