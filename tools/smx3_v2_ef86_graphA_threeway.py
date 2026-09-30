#!/usr/bin/env python3
"""Three-way EF86 Graph-A screen-family comparison.

Compares:
1. compact provisional fit;
2. generalized beta surrogate;
3. extended knee/kink family with community comparison parameters.

The community parameter set remains research-only. This tool compares MODEL
FAMILY behavior; it does not promote third-party fitted values.
"""

import csv
import math
import pathlib

import smx3_v2_ef86_generalized_surrogate as generalized
import smx3_v2_ef86_extended_family_benchmark as extended

ROOT=pathlib.Path(__file__).resolve().parents[1]
CSV=ROOT/"research"/"ef86_philips_graphA_provisional.csv"

PROV={
    "MU":40.4643134,
    "EX":1.10072133,
    "KG1":805.463266,
    "KP":220.481328,
    "KVB":8.11723096,
}


def l1p(x):
    if x>50.0:return x
    if x<-50.0:return math.exp(x)
    return math.log1p(math.exp(x))


def provisional_currents(vp,vg2,vg1):
    if vg2<=1e-12 or vp<=0.0:
        return 0.0,0.0
    z=PROV["KP"]*(1.0/PROV["MU"]+vg1/vg2)
    e=(vg2/PROV["KP"])*l1p(z)
    ia=max(e,0.0)**PROV["EX"]/PROV["KG1"]*math.atan(vp/PROV["KVB"])
    return ia,0.0


def score(name,fn,rows):
    ss=0.0
    worst=(0.0,None)
    trends={}

    for r in rows:
        vg2=float(r["vg2_v"])
        vg1=float(r["vg1_v"])
        ref=float(r["ia_ma"])
        u=float(r["uncertainty_ma"])
        model=fn(250.0,vg2,vg1)[0]*1e3
        sig=(model-ref)/u

        ss+=sig*sig
        trends.setdefault(vg2,[]).append(sig)
        if abs(sig)>worst[0]:
            worst=(abs(sig),(vg2,vg1,ref,model,sig))

    nrms=math.sqrt(ss/len(rows))
    means={k:sum(v)/len(v) for k,v in trends.items()}

    print(f"{name}: NRMS={nrms:.6f} sigma; worst={worst[0]:.6f} sigma")
    for vg2 in sorted(means):
        print(f"  Vg2={vg2:.0f} V mean signed residual={means[vg2]:+.6f} sigma")

    return nrms,worst


def main():
    rows=list(csv.DictReader(CSV.open(encoding="utf-8")))

    print("SMX-3 V2 EF86 Graph-A three-way structural comparison")
    print("DATA STATUS: provisional manufacturer-graph digitization")
    print()

    results=[
        ("compact provisional",score("compact provisional",provisional_currents,rows)),
        ("generalized beta",score("generalized beta",generalized.currents,rows)),
        ("extended knee/kink family",score("extended knee/kink family",extended.currents,rows)),
    ]

    print()
    results.sort(key=lambda x:x[1][0])
    print("NRMS order:")
    for name,(nrms,_) in results:
        print(f"  {name}: {nrms:.6f} sigma")

    print()
    print("INFO: ranking is model-family evidence only; no third-party parameter set is promoted.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
