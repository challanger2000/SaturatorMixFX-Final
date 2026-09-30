#!/usr/bin/env python3
"""EF86 Stage-1 plate-current surface candidate for SMX-3 V2.

Fit authority:
- Philips Graph A screen-voltage transfer families;
- Philips Graph B plate-current families;
- exact Philips Ia/gm device anchors.

IMPORTANT:
This stage deliberately does NOT fit screen current Ig2. The available static
data do not identify the screen-current submodel robustly enough yet.

Standard library only.
"""

import csv
import math
import pathlib

ROOT=pathlib.Path(__file__).resolve().parents[1]
GRAPHA=ROOT/"research"/"ef86_philips_graphA_provisional.csv"
GRAPHB=ROOT/"research"/"ef86_philips1956_platecurve_provisional.csv"

P={
    "MU":43.5199389,
    "KG1":1998.32070,
    "KP":200.286916,
    "KVB":1083.75004,
    "VCT":0.365171210,
    "EX":1.27822810,
    "KNEE":12.9196481,
    "KNEE2":1.45283944,
    "KNEX":0.0,
    "KLAMG":1.00015581e-7,
}


def l1p(x):
    if x>50.0:return x
    if x<-50.0:return math.exp(x)
    return math.log1p(math.exp(x))


def ia(vp,vg2,vg1):
    if vp<=0.0 or vg2<=1e-12:
        return 0.0

    z=(1.0/P["MU"]+(P["VCT"]+vg1)/math.sqrt(P["KVB"]+vg2*vg2))*P["KP"]
    e1=vg2/P["KP"]*l1p(z)
    e2=2.0*max(e1,0.0)**P["EX"]

    knee=math.atan((vp+P["KNEX"])/P["KNEE"])*math.tanh(vp/P["KNEE2"])
    out=e2/P["KG1"]*knee*(1.0+P["KLAMG"]*vp)
    return max(out,0.0)


def score_grapha():
    rows=list(csv.DictReader(GRAPHA.open(encoding="utf-8")))
    sigmas=[]
    for r in rows:
        m=1e3*ia(250.0,float(r["vg2_v"]),float(r["vg1_v"]))
        y=float(r["ia_ma"])
        u=float(r["uncertainty_ma"])
        sigmas.append((m-y)/u)
    return math.sqrt(sum(s*s for s in sigmas)/len(sigmas)),max(abs(s) for s in sigmas)


def score_graphb():
    rows=list(csv.DictReader(GRAPHB.open(encoding="utf-8")))
    sigmas=[]
    for r in rows:
        m=1e3*ia(float(r["va_v"]),140.0,float(r["curve_vg1_v"]))
        y=float(r["ia_ma"])
        u=float(r["uncertainty_ma"])
        sigmas.append((m-y)/u)
    return math.sqrt(sum(s*s for s in sigmas)/len(sigmas)),max(abs(s) for s in sigmas)


def main():
    ia0=ia(250.0,140.0,-2.0)
    dv=1e-4
    gm=(ia(250.0,140.0,-2.0+dv)-ia(250.0,140.0,-2.0-dv))/(2.0*dv)

    dva=0.1
    gop=(ia(250.0+dva,140.0,-2.0)-ia(250.0-dva,140.0,-2.0))/(2.0*dva)
    ri=1.0/gop

    a_rms,a_worst=score_grapha()
    b_rms,b_worst=score_graphb()

    print("SMX-3 V2 EF86 Stage-1 plate-current surface")
    print(f"Ia @250/140/-2 = {ia0*1e3:.9f} mA (Philips 3.000 mA)")
    print(f"gm @250/140/-2 = {gm*1e3:.9f} mA/V (Philips 2.000 mA/V)")
    print(f"Ri @250/140/-2 = {ri/1e6:.9f} MOhm (Philips 2.500 MOhm)")
    print(f"Graph A NRMS = {a_rms:.6f} sigma; worst = {a_worst:.6f} sigma")
    print(f"Graph B NRMS = {b_rms:.6f} sigma; worst = {b_worst:.6f} sigma")

    ia_err=100.0*(ia0-0.003)/0.003
    gm_err=100.0*(gm-0.002)/0.002
    ri_err=100.0*(ri-2.5e6)/2.5e6

    if abs(ia_err)>2.0:
        raise SystemExit("FAIL: exact Ia anchor")
    if abs(gm_err)>2.0:
        raise SystemExit("FAIL: exact gm anchor")
    if abs(ri_err)>12.0:
        raise SystemExit("FAIL: exact Ri anchor")
    if a_rms>1.0 or a_worst>2.0:
        raise SystemExit("FAIL: Graph A screen-family surface")
    if b_rms>1.0 or b_worst>2.0:
        raise SystemExit("FAIL: Graph B plate-current surface")

    print("PASS: Stage-1 plate-current surface stays inside current provisional Philips uncertainties.")
    print("WARNING: screen-current submodel and amplifier large-signal behavior are intentionally NOT part of Stage 1.")


if __name__=="__main__":
    raise SystemExit(main())
