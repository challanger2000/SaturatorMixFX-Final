#!/usr/bin/env python3
"""SMX-3 V2 physical-level calibration candidate calculations.

IMPORTANT:
No per-mode Drive calibration is frozen yet.

This tool only derives transparent candidate mappings in physical units so they
can be compared against accepted TRI0DE/PENTODE/IRON reference domains later.
It is informational and must not be treated as a production/release gate.
"""

import math

VREF_DBU=0.775


def dbu_to_vrms(dbu):
    return VREF_DBU*10.0**(dbu/20.0)


def db_ratio(a,b):
    return 20.0*math.log10(a/b)


def main():
    plus4=dbu_to_vrms(4.0)
    plus20=dbu_to_vrms(20.0)

    print("SMX-3 V2 level-calibration candidates")
    print("STATUS: INFORMATIONAL — per-mode Drive mapping is NOT frozen.")
    print()
    print(f"+4 dBu = {plus4:.9f} Vrms")
    print(f"+20 dBu = {plus20:.9f} Vrms")
    print(f"+4 -> +20 dBu physical voltage span = {db_ratio(plus20,plus4):.6f} dB")
    print()

    # Historical TRI0DE candidate, preserved only so earlier research remains
    # reproducible. It is NOT an accepted product mapping.
    drive0=0.10
    old_max=2.00
    print("Historical TRI0DE candidate (NOT FROZEN):")
    print(f"  nominal grid candidate = {drive0:.6f} Vrms")
    print(f"  former maximum candidate = {old_max:.6f} Vrms")
    print(f"  +4 dBu -> 0.10 Vrms pad = {db_ratio(drive0,plus4):.6f} dB")
    print(f"  former 0.10 -> 2.00 Vrms span = {db_ratio(old_max,drive0):.6f} dB")
    print()
    print("No PASS gate: calibration waits for accepted per-mode physical references.")


if __name__=="__main__":
    main()
