#!/usr/bin/env python3
"""Derive/check SMX-3 V2 physical level calibration anchors."""

import math

NOMINAL_DBU=4.0
VREF_DBU=0.775
TRIODE_DRIVE0_GRID_VRMS=0.10
TRIODE_MAX_GRID_VRMS=2.00


def dbu_to_vrms(dbu):
    return VREF_DBU*10.0**(dbu/20.0)


def db_ratio(a,b):
    return 20.0*math.log10(a/b)


def main():
    external=dbu_to_vrms(NOMINAL_DBU)
    pad_db=db_ratio(TRIODE_DRIVE0_GRID_VRMS,external)
    drive_span=db_ratio(TRIODE_MAX_GRID_VRMS,TRIODE_DRIVE0_GRID_VRMS)

    print("SMX-3 V2 level calibration")
    print(f"+4 dBu = {external:.9f} Vrms")
    print(f"TRIODE Drive=0 grid = {TRIODE_DRIVE0_GRID_VRMS:.6f} Vrms")
    print(f"required modeled input pad = {pad_db:.6f} dB")
    print(f"0.10 -> 2.00 Vrms physical Drive span = {drive_span:.6f} dB")

    if not (-22.0 < pad_db < -21.5):
        raise SystemExit("FAIL: triode nominal pad derivation moved")
    if not (25.9 < drive_span < 26.2):
        raise SystemExit("FAIL: triode drive-span derivation moved")

    print("PASS: physical level anchors are stable.")


if __name__=="__main__":
    main()
