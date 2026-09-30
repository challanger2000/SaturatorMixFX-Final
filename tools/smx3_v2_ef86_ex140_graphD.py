#!/usr/bin/env python3
"""Out-of-fit Philips Graph-D check for the current EF86 EX=1.40 candidate.

The candidate was selected from:
- Graph A/B current surfaces;
- exact Ia/gm/Ig2 device anchors;
- exact circuit current/gain table;
- exact Vo@5% multi-supply envelope.

Graph D was NOT used to select EX=1.40.

Therefore this is an independent large-signal shape check.

Standard library only.
"""

import csv
import math
import pathlib

import smx3_v2_ef86_ex_scan as base

ROOT=pathlib.Path(__file__).resolve().parents[1]
GRAPHD=ROOT/"research"/"ef86_philips1956_graphD_provisional.csv"

EX=1.40
VCT,KG1,S0=base.derive_local(EX)
P=(EX,VCT,KG1,S0)


def waveform(vin_rms,n=2048):
    return base.waveform(250.0,vin_rms,P,n)


def solve_input_for_output(target_vrms):
    lo=0.0
    hi=1.2

    out,_=waveform(hi,512)
    while out<target_vrms and hi<3.0:
        hi*=1.4
        out,_=waveform(hi,512)

    if out<target_vrms:
        raise RuntimeError(f"cannot bracket {target_vrms} Vrms output")

    for _ in range(44):
        mid=.5*(lo+hi)
        out,_=waveform(mid,768)
        if out<target_vrms:
            lo=mid
        else:
            hi=mid

    vin=.5*(lo+hi)
    out,thd=waveform(vin,4096)
    return vin,out,thd


def main():
    rows=list(csv.DictReader(GRAPHD.open(encoding="utf-8")))

    print("SMX-3 V2 EF86 EX=1.40 Graph-D out-of-fit check")
    print(f"VCT={VCT:.12g} KG1={KG1:.12g} S0={S0:.12g}")
    print()
    print("Vo_target,Vi_model_mV,Vi_graph_mV,Vi_sigma,THD_model_pct,THD_graph_pct,THD_sigma")

    vi_sig=[]
    d_sig=[]

    for r in rows:
        vo=float(r["output_vrms"])
        vi_ref=float(r["input_mvrms"])
        d_ref=float(r["distortion_percent"])
        uvi=float(r["input_uncertainty_mV"])
        ud=float(r["distortion_uncertainty_pct"])

        vin,out,thd=solve_input_for_output(vo)
        vi_mv=vin*1000.0
        svi=(vi_mv-vi_ref)/uvi
        sd=(thd-d_ref)/ud

        vi_sig.append(svi)
        d_sig.append(sd)

        print(
            f"{vo:.1f},{vi_mv:.6f},{vi_ref:.6f},{svi:+.3f},"
            f"{thd:.6f},{d_ref:.6f},{sd:+.3f}"
        )

    vi_nrms=math.sqrt(sum(x*x for x in vi_sig)/len(vi_sig))
    d_nrms=math.sqrt(sum(x*x for x in d_sig)/len(d_sig))
    vi_worst=max(abs(x) for x in vi_sig)
    d_worst=max(abs(x) for x in d_sig)

    print()
    print(f"Vi NRMS={vi_nrms:.6f} sigma; worst={vi_worst:.6f} sigma")
    print(f"THD NRMS={d_nrms:.6f} sigma; worst={d_worst:.6f} sigma")

    # Provisional graph points are not strong enough to define production
    # pass/fail. This script deliberately reports a classification and exits 0.
    if vi_nrms<=1.5 and d_nrms<=1.5 and vi_worst<=2.5 and d_worst<=2.5:
        verdict="STRONG"
    elif vi_nrms<=2.5 and d_nrms<=2.5 and vi_worst<=4.0 and d_worst<=4.0:
        verdict="PLAUSIBLE"
    else:
        verdict="WEAK"

    print(f"OUT-OF-FIT VERDICT: {verdict}")
    print("INFO: Graph-D points remain provisional manual digitization; no hard promotion gate yet.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
