#!/usr/bin/env python3
"""Validate the generalized EF86 surrogate against Philips Graph-D shape.

The provisional Graph-D points are MANUAL_GRAPH_DIGITIZATION and therefore
carry explicit uncertainty. This test is an out-of-fit SHAPE check, not a
manufacturer-exact pass/fail gate yet.

Standard library only.
"""

import csv
import math
import pathlib

import smx3_v2_ef86_generalized_surrogate as model


ROOT=pathlib.Path(__file__).resolve().parents[1]
CSV=ROOT/"research"/"ef86_philips1956_graphD_refined_provisional.csv"


def solve_input_for_output(target_vrms):
    # Bracket by monotonic output level.
    lo=0.0
    hi=0.8

    out_hi,_=model.waveform(hi,1024)
    while out_hi<target_vrms and hi<3.0:
        hi*=1.5
        out_hi,_=model.waveform(hi,1024)

    if out_hi<target_vrms:
        raise RuntimeError(f"could not bracket {target_vrms} Vrms output")

    for _ in range(42):
        mid=0.5*(lo+hi)
        out,_=model.waveform(mid,768)
        if out<target_vrms:
            lo=mid
        else:
            hi=mid

    vin=0.5*(lo+hi)
    out,thd=model.waveform(vin,4096)
    return vin,out,thd


def main():
    rows=list(csv.DictReader(CSV.open(encoding="utf-8")))

    print("SMX-3 V2 EF86 generalized-surrogate Graph-D shape check")
    print("Graph samples are refined provisional manufacturer-graph reads; the 50 V / 5% endpoint is exact table authority.")
    print()
    print("Vo_target_V,Vi_model_mV,Vi_graph_mV,Vi_sigma,THD_model_pct,THD_graph_pct,THD_sigma")

    vi_sigmas=[]
    d_sigmas=[]

    for row in rows:
        vo=float(row["output_vrms"])
        vi_ref=float(row["input_mvrms"])
        d_ref=float(row["distortion_percent"])
        u_vi=float(row["input_uncertainty_mV"])
        u_d=float(row["distortion_uncertainty_pct"])

        vin,out,thd=solve_input_for_output(vo)
        vi_mv=vin*1000.0

        s_vi=(vi_mv-vi_ref)/u_vi
        s_d=(thd-d_ref)/u_d

        vi_sigmas.append(s_vi)
        d_sigmas.append(s_d)

        print(
            f"{vo:.1f},{vi_mv:.6f},{vi_ref:.6f},{s_vi:+.3f},"
            f"{thd:.6f},{d_ref:.6f},{s_d:+.3f}"
        )

    vi_nrms=math.sqrt(sum(s*s for s in vi_sigmas)/len(vi_sigmas))
    d_nrms=math.sqrt(sum(s*s for s in d_sigmas)/len(d_sigmas))
    vi_worst=max(abs(s) for s in vi_sigmas)
    d_worst=max(abs(s) for s in d_sigmas)

    print()
    print(f"Vi normalized RMS = {vi_nrms:.3f} sigma; worst = {vi_worst:.3f} sigma")
    print(f"distortion normalized RMS = {d_nrms:.3f} sigma; worst = {d_worst:.3f} sigma")

    # Informational classification:
    # provisional manual graph reads are not strong enough to make this a hard
    # production gate. Return success and print a clear model-quality verdict.
    if vi_nrms<=1.0 and d_nrms<=1.0 and vi_worst<=2.0 and d_worst<=2.0:
        print("SHAPE-CHECK: STRONG provisional agreement with Philips Graph D.")
    elif vi_nrms<=2.0 and d_nrms<=2.0 and vi_worst<=3.0 and d_worst<=3.0:
        print("SHAPE-CHECK: PLAUSIBLE provisional agreement; calibrated digitization still needed.")
    else:
        print("SHAPE-CHECK: WEAK provisional agreement; model family should not be promoted.")

    print("INFO: final promotion waits for calibrated manufacturer-graph extraction.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
