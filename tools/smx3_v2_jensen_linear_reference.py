#!/usr/bin/env python3
"""Linear JT-11P-1 reference derivation for SMX-3 V2 IRON.

Derives the low-level line-transformer skeleton from documented Jensen values
before any nonlinear magnetic model is fitted.

Model:
- 1:1 ideal transformer
- primary DCR Rp
- secondary DCR Rs
- secondary load RL
- shunt magnetizing inductance Lm on the primary side

The script solves Lm so the 20 Hz response is -0.04 dB relative to 1 kHz.
Standard library only.
"""

import cmath
import math

RP = 1450.0
RS = 1550.0
RL = 10000.0
TARGET_20HZ_REL_DB = -0.04


def parallel(a, b):
    return 1.0 / (1.0/a + 1.0/b)


def transfer(f_hz, lm_h):
    zload = complex(RS + RL, 0.0)
    zm = 1j * 2.0 * math.pi * f_hz * lm_h
    zbranch = parallel(zload, zm)

    # Voltage at ideal-transformer primary branch, then secondary DCR/load divider.
    return zbranch/(RP + zbranch) * RL/(RS + RL)


def input_impedance(f_hz, lm_h):
    zload = complex(RS + RL, 0.0)
    zm = 1j * 2.0 * math.pi * f_hz * lm_h
    return RP + parallel(zload, zm)


def db(x):
    return 20.0 * math.log10(abs(x))


def relative_db(f_hz, lm_h, ref_hz=1000.0):
    return db(transfer(f_hz,lm_h)) - db(transfer(ref_hz,lm_h))


def solve_lm():
    lo = 0.01
    hi = 10000.0
    for _ in range(160):
        mid = 0.5*(lo+hi)
        r = relative_db(20.0, mid)
        if r < TARGET_20HZ_REL_DB:
            lo = mid
        else:
            hi = mid
    return 0.5*(lo+hi)


def main():
    lm = solve_lm()

    print("SMX-3 V2 JT-11P-1 linear reference")
    print(f"Rp = {RP:.3f} ohm")
    print(f"Rs = {RS:.3f} ohm")
    print(f"RL = {RL:.3f} ohm")
    print(f"derived Lm = {lm:.9f} H")
    print()

    print("freq_hz,gain_db,relative_to_1k_db,input_Z_mag_ohm,phase_deg")
    for f in (20.0, 1000.0, 20000.0):
        h = transfer(f,lm)
        zin = input_impedance(f,lm)
        phase = math.degrees(cmath.phase(h))
        print(f"{f:.1f},{db(h):.9f},{relative_db(f,lm):.9f},{abs(zin):.9f},{phase:.9f}")

    # Jensen low-level anchors.
    gain_1k = db(transfer(1000.0,lm))
    zin_1k = abs(input_impedance(1000.0,lm))
    rel_20 = relative_db(20.0,lm)

    print()
    print(f"1 kHz gain error vs -2.3 dB: {gain_1k - (-2.3):+.6f} dB")
    print(f"1 kHz Zin error vs 13.0 kOhm: {(zin_1k-13000.0):+.3f} ohm")
    print(f"20 Hz relative response error vs -0.04 dB: {rel_20 - (-0.04):+.9f} dB")

    if abs(gain_1k - (-2.3)) > 0.05:
        raise SystemExit("FAIL: linear skeleton misses Jensen 1 kHz gain")
    if abs(zin_1k - 13000.0) > 50.0:
        raise SystemExit("FAIL: linear skeleton misses Jensen 1 kHz input impedance")
    if abs(rel_20 - (-0.04)) > 1e-6:
        raise SystemExit("FAIL: Lm solve misses Jensen 20 Hz relative response")

    print("PASS: documented DCR/load plus derived Lm reproduce the selected low-level Jensen anchors.")


if __name__ == "__main__":
    main()
