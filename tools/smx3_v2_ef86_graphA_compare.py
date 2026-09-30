#!/usr/bin/env python3
"""Compare EF86 candidate model families against provisional Philips Graph A.

Graph A:
- Va = 250 V
- Vg3 = 0 V
- Ia(Vg1) for Vg2 = 60/100/140/180 V

This is an INFORMATIONAL structural model-family check until calibrated
manufacturer-graph extraction replaces the provisional manual points.
"""

import csv
import math
import pathlib

import smx3_v2_ef86_provisional_fit as provisional
import smx3_v2_ef86_generalized_surrogate as generalized
import smx3_v2_ef86_extended_family_benchmark as extended

ROOT=pathlib.Path(__file__).resolve().parents[1]
CSV=ROOT/"research"/"ef86_philips_graphA_provisional.csv"


def score(fn):
    rows=list(csv.DictReader(CSV.open(encoding="utf-8")))
    ss=0.0
    worst=0.0
    signed_by_vg2={}
    details=[]

    for r in rows:
        vg2=float(r["vg2_v"])
        vg1=float(r["vg1_v"])
        ref=float(r["ia_ma"])
        u=float(r["uncertainty_ma"])
        model=fn(250.0,vg2,vg1)[0]*1e3
        sigma=(model-ref)/u

        ss+=sigma*sigma
        worst=max(worst,abs(sigma))
        signed_by_vg2.setdefault(vg2,[]).append(sigma)
        details.append((vg2,vg1,ref,model,sigma))

    nrms=math.sqrt(ss/len(details))
    trends={vg2:sum(v)/len(v) for vg2,v in signed_by_vg2.items()}
    return nrms,worst,trends,details


def print_model(name,fn):
    nrms,worst,trends,details=score(fn)
    print(f"[{name}]")
    print(f"normalized RMS = {nrms:.3f} sigma")
    print(f"worst residual = {worst:.3f} sigma")
    print("mean signed residual by Vg2:")
    for vg2 in sorted(trends):
        print(f"  {vg2:.0f} V: {trends[vg2]:+.3f} sigma")
    print("points:")
    print("  Vg2,Vg1,Ia_ref_mA,Ia_model_mA,residual_sigma")
    for vg2,vg1,ref,model,sigma in details:
        print(f"  {vg2:.0f},{vg1:.1f},{ref:.6f},{model:.6f},{sigma:+.3f}")
    print()
    return nrms,worst,trends


def main():
    print("SMX-3 V2 EF86 Graph-A structural family comparison")
    print("DATA STATUS: provisional manual manufacturer-graph digitization")
    print()

    p=print_model("provisional compact multi-anchor fit",provisional.currents)
    g=print_model("generalized beta compact surrogate",generalized.currents)
    e=print_model("extended knee/kink family, community comparison parameters",extended.currents)

    print("INTERPRETATION:")
    ranked=sorted([("provisional",p[0]),("generalized",g[0]),("extended-community",e[0])], key=lambda x:x[1])
    print("- provisional Graph-A NRMS ranking: "+", ".join(f"{name}={score:.3f}σ" for name,score in ranked))
    print("- beta improved local large-signal behavior but does not automatically improve screen-grid dependence.")
    print("- community extended parameters remain non-authoritative regardless of score.")
    print("- final decision waits for calibrated Graph-A extraction and independent refit.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
