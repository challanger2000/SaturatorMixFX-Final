#!/usr/bin/env python3
"""Dynamic Philips Graph-D probe for current EF86 EX=1.40 candidate.

Uses the first dynamic EF86 offline reference:
- real cathode bypass;
- real screen bypass;
- output coupling/load;
- Philips terminal capacitances.

Graph-D input points are provisional manual reads. This test asks whether the
dynamic network changes the quasi-static distortion trajectory in the direction
required by Philips.

Standard library only.
"""

import csv
import pathlib

import smx3_v2_ef86_dynamic_reference as dyn

ROOT=pathlib.Path(__file__).resolve().parents[1]
CSV=ROOT/"research"/"ef86_philips1956_graphD_provisional.csv"


def main():
    rows=list(csv.DictReader(CSV.open(encoding="utf-8")))

    print("SMX-3 V2 EF86 dynamic Graph-D probe")
    print("Frequency: 1 kHz; input is direct g1-node RMS.")
    print("Graph-D Vi values used as stimulus; input coupling network omitted.")
    print()
    print("Vi_graph_mV,Vo_dynamic_V,Vo_graph_V,Vo_error_pct,THD_dynamic_pct,THD_graph_pct")

    out_errors=[]
    thd_errors=[]

    for r in rows:
        vi_mV=float(r["input_mvrms"])
        vo_ref=float(r["output_vrms"])
        d_ref=float(r["distortion_percent"])

        m=dyn.simulate(1000.0,vi_mV/1000.0,fs=192000.0,warmup_seconds=0.4,cycles=8)
        # dyn.gain is fundamental amplitude ratio. For a sine, RMS ratio is the same.
        vo=m["gain"]*(vi_mV/1000.0)
        d=100.0*m["thd"]

        eout=100.0*(vo-vo_ref)/vo_ref
        ed=d-d_ref
        out_errors.append(eout)
        thd_errors.append(ed)

        print(
            f"{vi_mV:.3f},{vo:.6f},{vo_ref:.6f},{eout:+.6f},"
            f"{d:.6f},{d_ref:.6f}"
        )

    print()
    print(f"worst |Vo error| = {max(abs(x) for x in out_errors):.6f}%")
    print(f"THD residual range = {min(thd_errors):+.6f} .. {max(thd_errors):+.6f} percentage-points")
    print("INFO: Graph-D points are provisional and the exact manufacturer test frequency is not stated on the plotted sheet.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
