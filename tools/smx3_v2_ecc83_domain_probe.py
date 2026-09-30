#!/usr/bin/env python3
"""Operating-domain probe for the SMX-3 V2 dynamic ECC83 reference.

Dempwolf/Zoelzer measured the 12AX7 over approximately:
- Va = 20..300 V
- Vg = -5..+3 V

Positive grid voltage is therefore NOT invalid by itself; grid current under
positive Vg is an explicit measured/modelled feature.

The documented limitation is specifically the combination:
- Vg > 0
- very low Va, approximately Va < 20 V

where real anode current falls rapidly toward Va=0 but the presented model
does not reproduce that behavior correctly.
"""

import argparse
import math

from smx3_v2_ecc83_dynamic_reference import (
    G, P_NODE, K, currents, solve_dc, trapezoid_step
)


def probe(freq,vin_rms,cycles=8,fs=None,warmup_seconds=0.4):
    if fs is None:
        fs=max(192000.0,96.0*freq)

    x=solve_dc()
    vin_peak=vin_rms*math.sqrt(2.0)

    warm_fs=min(fs,max(192000.0,24.0*freq))
    warm_samples=max(0,int(round(warmup_seconds*warm_fs)))
    warm_dt=1.0/warm_fs
    max_newton=0

    for n in range(warm_samples):
        x,it=trapezoid_step(n*warm_dt,x,warm_dt,vin_peak,freq)
        max_newton=max(max_newton,it)

    t0=warm_samples/warm_fs if warm_samples else 0.0

    samples=max(1,int(round(cycles*fs/freq)))
    keep=max(1,int(round(4.0*fs/freq)))
    dt=1.0/fs

    min_va=float("inf")
    max_vg=-float("inf")
    max_ig=0.0
    min_va_when_vg_positive=float("inf")
    positive_grid_samples=0

    for n in range(samples):
        x,it=trapezoid_step(t0+n*dt,x,dt,vin_peak,freq)
        max_newton=max(max_newton,it)

        if n >= samples-keep:
            va=x[P_NODE]-x[K]
            vg=x[G]-x[K]
            _,_,ig=currents(va,vg)

            min_va=min(min_va,va)
            max_vg=max(max_vg,vg)
            max_ig=max(max_ig,ig)

            if vg>0.0:
                positive_grid_samples+=1
                min_va_when_vg_positive=min(min_va_when_vg_positive,va)

    return {
        "min_va":min_va,
        "max_vg":max_vg,
        "max_ig":max_ig,
        "min_va_when_vg_positive":min_va_when_vg_positive,
        "positive_grid_samples":positive_grid_samples,
        "max_newton":max_newton,
    }


def bisect_grid_zero(freq,lo=0.05,hi=2.0):
    a=probe(freq,lo)["max_vg"]
    b=probe(freq,hi)["max_vg"]

    if a>=0.0:
        return lo
    if b<0.0:
        return None

    while hi-lo > 0.0005:
        mid=0.5*(lo+hi)
        if probe(freq,mid)["max_vg"]>=0.0:
            hi=mid
        else:
            lo=mid

    return 0.5*(lo+hi)


def invalid_combination(r):
    return (
        r["positive_grid_samples"]>0
        and r["min_va_when_vg_positive"]<20.0
    )


def fmt_pos_va(r):
    if r["positive_grid_samples"]<=0:
        return float("nan")
    return r["min_va_when_vg_positive"]


def print_row(freq,vin,r):
    print(
        f"{freq:.1f},{vin:.3f},{r['min_va']:.9f},{r['max_vg']:.9f},"
        f"{r['max_ig']*1e6:.9f},{fmt_pos_va(r):.9f},"
        f"{r['max_newton']},{int(r['max_vg']>0.0)},{int(invalid_combination(r))}"
    )


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument(
        "--full",
        action="store_true",
        help="Run the full level/frequency matrix and positive-grid threshold bisections."
    )
    args=ap.parse_args()

    gate_freqs=(20.0,1000.0,10000.0,20000.0)

    print("SMX-3 V2 ECC83 measured-domain gate")
    print(
        "freq_Hz,Vin_rms,min_Va_V,max_Vg_V,max_Ig_uA,"
        "min_Va_when_Vg_positive,max_Newton,grid_positive,"
        "invalid_Vgpos_and_Va_lt20"
    )

    failures=[]

    # Conservative normal reference level.
    for freq in gate_freqs:
        r=probe(freq,0.70)
        print_row(freq,0.70,r)

        if r["max_vg"]>3.0:
            failures.append(f"{freq:g} Hz: Vg exceeds measured +3 V range at 0.70 Vrms")
        if invalid_combination(r):
            failures.append(f"{freq:g} Hz: entered documented Vg>0 / Va<20 V failure region at 0.70 Vrms")

    # Higher-level HF fixtures.
    top=probe(20000.0,1.00)
    extreme=probe(20000.0,8.00)
    print_row(20000.0,1.00,top)
    print_row(20000.0,8.00,extreme)

    for label,r in (
        ("20 kHz / 1.0 Vrms",top),
        ("20 kHz / 8.0 Vrms",extreme),
    ):
        if r["max_vg"]>3.0:
            failures.append(label+" exceeds measured +3 V grid range")
        if invalid_combination(r):
            failures.append(label+" entered documented Vg>0 / Va<20 V failure region")

    # Keep one fixture that definitely exercises grid current / positive-grid
    # behavior while remaining inside the measured plate-voltage domain.
    if extreme["max_vg"]<=0.0:
        failures.append("20 kHz / 8.0 Vrms no longer exercises positive-grid/grid-current behavior")

    if args.full:
        print()
        print("FULL MATRIX")

        freqs=(20.0,100.0,1000.0,10000.0,20000.0)
        levels=(0.10,0.30,0.50,0.70,1.00,1.50,2.00)

        for freq in freqs:
            for vin in levels:
                print_row(freq,vin,probe(freq,vin))

        print()
        print("Approximate Vin RMS at first positive-grid crossing")
        for freq in freqs:
            threshold=bisect_grid_zero(freq)
            if threshold is None:
                print(f"{freq:.1f} Hz: >2.0 Vrms")
            else:
                print(f"{freq:.1f} Hz: ~{threshold:.4f} Vrms")

    print()

    if failures:
        print("FAIL: TRI0DE measured-domain regression moved")
        for item in failures:
            print(" - "+item)
        return 1

    print(
        "PASS: tested fixtures remain inside Dempwolf's measured/modelled Vg range "
        "and avoid the documented Vg>0 / Va<20 V failure region."
    )

    if not args.full:
        print("Use --full for the complete research matrix and positive-grid threshold bisections.")

    return 0


if __name__=="__main__":
    raise SystemExit(main())
