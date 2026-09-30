#!/usr/bin/env python3
"""Operating-domain probe for the SMX-3 V2 dynamic ECC83 reference.

Measures where the Dempwolf/Zoelzer EHX-1 model enters regions the source
paper explicitly identifies as inaccurate:
- positive grid voltage;
- very low anode voltage (approximately Va < 20 V).

This tool does not declare those regions "forbidden sound". It identifies
where an extension/alternate model is required before production Drive mapping
may rely on them.

Standard library only.
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

    return {
        "min_va":min_va,
        "max_vg":max_vg,
        "max_ig":max_ig,
        "max_newton":max_newton,
    }


def bisect_grid_zero(freq,lo=0.05,hi=2.0):
    a=probe(freq,lo)["max_vg"]
    b=probe(freq,hi)["max_vg"]
    if a>=0.0:
        return lo
    if b<0.0:
        return None

    # Coarse research threshold: ~0.5 mVrms resolution is more than sufficient
    # for setting product Drive headroom. Avoid pretending the physical model
    # itself is known to microvolt precision.
    while hi-lo > 0.0005:
        mid=0.5*(lo+hi)
        if probe(freq,mid)["max_vg"]>=0.0:
            hi=mid
        else:
            lo=mid
    return 0.5*(lo+hi)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument(
        "--full",
        action="store_true",
        help="Run the full level/frequency matrix, threshold bisections and stress cases."
    )
    args=ap.parse_args()

    gate_freqs=(20.0,1000.0,10000.0,20000.0)

    print("SMX-3 V2 ECC83 model-domain gate")
    print("freq_Hz,Vin_rms,min_Va_V,max_Vg_V,max_Ig_uA,max_Newton,grid_positive,Va_below_20")

    failures=[]

    # Fast regression gate: the intended normal/musical reference level must
    # remain inside the documented model-validity warnings throughout the
    # tested audio band.
    for f in gate_freqs:
        r=probe(f,0.70)
        print(
            f"{f:.1f},0.700,{r['min_va']:.9f},{r['max_vg']:.9f},"
            f"{r['max_ig']*1e6:.9f},{r['max_newton']},"
            f"{int(r['max_vg']>0.0)},{int(r['min_va']<20.0)}"
        )
        if r["max_vg"]>=0.0:
            failures.append(f"{f:g} Hz: positive grid at 0.70 Vrms")
        if r["min_va"]<20.0:
            failures.append(f"{f:g} Hz: Va<20 V at 0.70 Vrms")

    # Diagnostic sensitivity checks at the top of the audio band.
    top=probe(20000.0,1.00)
    extreme=probe(20000.0,8.00)

    print(
        f"20000.0,1.000,{top['min_va']:.9f},{top['max_vg']:.9f},"
        f"{top['max_ig']*1e6:.9f},{top['max_newton']},"
        f"{int(top['max_vg']>0.0)},{int(top['min_va']<20.0)}"
    )
    print(
        f"20000.0,8.000,{extreme['min_va']:.9f},{extreme['max_vg']:.9f},"
        f"{extreme['max_ig']*1e6:.9f},{extreme['max_newton']},"
        f"{int(extreme['max_vg']>0.0)},{int(extreme['min_va']<20.0)}"
    )

    if top["max_vg"]<=0.0:
        failures.append("20 kHz / 1.0 Vrms no longer exercises positive-grid boundary")
    if extreme["min_va"]>=20.0:
        failures.append("20 kHz / 8.0 Vrms no longer exercises low-Va stress boundary")

    if args.full:
        print()
        print("FULL MATRIX")
        freqs=(20.0,100.0,1000.0,10000.0,20000.0)
        levels=(0.10,0.30,0.50,0.70,1.00,1.50,2.00)

        for f in freqs:
            for vin in levels:
                # Skip cases already printed by the fast gate only for display
                # compactness; recomputation is still acceptable research cost.
                r=probe(f,vin)
                print(
                    f"{f:.1f},{vin:.3f},{r['min_va']:.9f},{r['max_vg']:.9f},"
                    f"{r['max_ig']*1e6:.9f},{r['max_newton']},"
                    f"{int(r['max_vg']>0.0)},{int(r['min_va']<20.0)}"
                )

        print()
        print("Approximate Vin RMS at first positive-grid crossing")
        for f in freqs:
            threshold=bisect_grid_zero(f)
            if threshold is None:
                print(f"{f:.1f} Hz: >2.0 Vrms")
            else:
                print(f"{f:.1f} Hz: ~{threshold:.4f} Vrms")

    print()
    if failures:
        print("FAIL: TRI0DE model-domain regression moved")
        for x in failures:
            print(" - "+x)
        return 1

    print("PASS: conservative normal domain remains valid and stress fixtures still exercise the documented suspect regions.")
    if not args.full:
        print("Use --full for the complete research matrix and positive-grid threshold bisections.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
