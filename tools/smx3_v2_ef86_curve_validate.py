#!/usr/bin/env python3
"""Validate the provisional EF86 model against digitized Philips plate curves.

The CSV points are intentionally marked MANUAL_GRAPH_DIGITIZATION and carry
per-point uncertainty. They are validation evidence, not exact manufacturer
tabular data.

Standard library only.
"""
import csv, math, pathlib

P={"MU":40.4643134,"EX":1.10072133,"KG1":805.463266,"KG2":2542.71827,"KP":220.481328,"KVB":8.11723096}

def l1p(x):
    if x>50:return x
    if x<-50:return math.exp(x)
    return math.log1p(math.exp(x))

def ia(vp,vg2,vg1):
    z=P["KP"]*(1/P["MU"]+vg1/vg2)
    e=(vg2/P["KP"])*l1p(z)
    return max(e,0.0)**P["EX"]/P["KG1"]*math.atan(vp/P["KVB"])

def main():
    path=pathlib.Path(__file__).resolve().parents[1]/"research"/"ef86_philips1956_platecurve_provisional.csv"
    rows=list(csv.DictReader(path.open(encoding="utf-8")))
    sq=0.0; wsum=0.0; worst=(0,None)
    print("Vg1,Va,measured_mA,model_mA,error_mA,error_sigma")
    for r in rows:
        vg=float(r["curve_vg1_v"]); va=float(r["va_v"])
        y=float(r["ia_ma"]); u=float(r["uncertainty_ma"])
        m=ia(va,140.0,vg)*1e3
        e=m-y
        sig=e/u
        sq += sig*sig
        wsum += 1.0
        if abs(sig)>worst[0]: worst=(abs(sig),(vg,va,y,m,e,sig))
        print(f"{vg:.2f},{va:.1f},{y:.6f},{m:.6f},{e:+.6f},{sig:+.3f}")
    nrms=math.sqrt(sq/wsum)
    print()
    print(f"normalized RMS error = {nrms:.3f} sigma")
    print(f"worst absolute error = {worst[0]:.3f} sigma at {worst[1]}")
    if nrms>1.5:
        raise SystemExit("FAIL: provisional model does not stay within graph-digitization uncertainty")
    print("PASS: provisional model is consistent with the current coarse plate-curve digitization.")
    print("WARNING: replace provisional visual points with calibrated graph extraction before final promotion.")

if __name__=="__main__":
    main()
