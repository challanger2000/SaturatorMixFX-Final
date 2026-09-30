#!/usr/bin/env python3
"""Compare EF86 candidate model families against provisional Philips Graph B.

Graph B:
- Vg2 = 140 V
- Vg3 = 0 V
- Ia(Va) for multiple Vg1 curves

This is an INFORMATIONAL structural model-family comparison until calibrated
manufacturer-graph extraction replaces the provisional points.
"""

import csv
import math
import pathlib

import smx3_v2_ef86_generalized_surrogate as compact
import smx3_v2_ef86_extended_family_benchmark as extended

ROOT=pathlib.Path(__file__).resolve().parents[1]
CSV=ROOT/"research"/"ef86_philips1956_platecurve_provisional.csv"


def score(fn):
    rows=list(csv.DictReader(CSV.open(encoding="utf-8")))
    ss=0.0
    worst=0.0
    by_grid={}
    details=[]

    for r in rows:
        vg=float(r["curve_vg1_v"])
        va=float(r["va_v"])
        ref=float(r["ia_ma"])
        u=float(r["uncertainty_ma"])
        model=fn(va,140.0,vg)[0]*1e3
        sigma=(model-ref)/u

        ss+=sigma*sigma
        worst=max(worst,abs(sigma))
        by_grid.setdefault(vg,[]).append(sigma)
        details.append((vg,va,ref,model,sigma))

    nrms=math.sqrt(ss/len(details))
    trends={vg:sum(v)/len(v) for vg,v in by_grid.items()}
    return nrms,worst,trends,details


def print_model(name,fn):
    nrms,worst,trends,details=score(fn)
    print(f"[{name}]")
    print(f"normalized RMS = {nrms:.3f} sigma")
    print(f"worst residual = {worst:.3f} sigma")
    print("mean signed residual by Vg1:")
    for vg in sorted(trends):
        print(f"  {vg:.1f} V: {trends[vg]:+.3f} sigma")
    print("points:")
    print("  Vg1,Va,Ia_ref_mA,Ia_model_mA,residual_sigma")
    for vg,va,ref,model,sigma in details:
        print(f"  {vg:.1f},{va:.1f},{ref:.6f},{model:.6f},{sigma:+.3f}")
    print()
    return nrms,worst,trends


def main():
    print("SMX-3 V2 EF86 Graph-B structural family comparison")
    print("DATA STATUS: provisional manual manufacturer-graph digitization")
    print()

    a=print_model("generalized compact surrogate",compact.currents)
    b=print_model("extended knee/kink family, community comparison parameters",extended.currents)

    print("INTERPRETATION:")
    if b[0] < a[0]:
        print("- extended family currently follows the plate-curve family better in normalized RMS.")
    else:
        print("- compact family currently follows the plate-curve family at least as well in normalized RMS.")

    print("- this comparison evaluates model FAMILY behavior, not parameter authority.")
    print("- final selection requires independent refit and calibrated graph extraction.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
