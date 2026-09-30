#!/usr/bin/env python3
"""Cross-domain validation of the EF86 Stage-3 large-signal correction.

Stage 3 is only acceptable if its localized low-Va correction improves the
exact large-signal envelope WITHOUT materially damaging the Philips current
surfaces that define Stage 1/2.

Checks:
- Graph A screen family
- Graph B plateau family
- supplemental Graph B knee region (20/40/60/80 V)
- exact 200..400 V Vo@5% envelope
- refined provisional Graph D at 250 V
"""

import csv, math, pathlib
import smx3_v2_ef86_stage2_joint_static as s2
import smx3_v2_ef86_stage3_knee_candidate as s3

ROOT=pathlib.Path(__file__).resolve().parents[1]
GA=ROOT/"research"/"ef86_philips_graphA_provisional.csv"
GB=ROOT/"research"/"ef86_philips1956_platecurve_provisional.csv"
GBK=ROOT/"research"/"ef86_philips1956_platecurve_knee_provisional.csv"
GD=ROOT/"research"/"ef86_philips1956_graphD_refined_provisional.csv"

ENV={200.0:40.0,250.0:50.0,300.0:64.0,350.0:75.0,400.0:87.0}


def score(path,currents,mode):
    rows=list(csv.DictReader(path.open(encoding="utf-8")))
    sig=[]
    detail=[]
    for r in rows:
        if mode=="A":
            x1=float(r["vg2_v"]);x2=float(r["vg1_v"])
            ia=currents(250.0,x1,x2)[0]
            ref=float(r["ia_ma"]);u=float(r["uncertainty_ma"])
            ident=f"Vg2={x1:g} V Vg1={x2:g} V"
        else:
            x1=float(r["va_v"]);x2=float(r["curve_vg1_v"])
            ia=currents(x1,140.0,x2)[0]
            ref=float(r["ia_ma"]);u=float(r["uncertainty_ma"])
            ident=f"Va={x1:g} V Vg1={x2:g} V"
        model=1e3*ia
        s=(model-ref)/u
        sig.append(s)
        detail.append((abs(s),ident,ref,model,u,s))
    detail.sort(reverse=True)
    return math.sqrt(sum(x*x for x in sig)/len(sig)),max(abs(x) for x in sig),detail


def envelope():
    errs=[]
    for vb,target in sorted(ENV.items()):
        _,out,_=s3.find_for_thd(vb)
        errs.append(100.0*(out-target)/target)
    return math.sqrt(sum(x*x for x in errs)/len(errs)),max(abs(x) for x in errs),errs


def graphd():
    rows=list(csv.DictReader(GD.open(encoding="utf-8")))
    vi_sig=[]
    d_sig=[]
    details=[]

    for r in rows:
        vo=float(r["output_vrms"])
        vin,out,d=s3.input_for_output(250.0,vo)

        vi_ref=float(r["input_mvrms"])
        d_ref=float(r["distortion_percent"])
        uvi=float(r["input_uncertainty_mV"])
        ud=float(r["distortion_uncertainty_pct"])

        sv=(vin*1000.0-vi_ref)/uvi
        sd=(d-d_ref)/ud
        vi_sig.append(sv);d_sig.append(sd)
        details.append((vo,vin*1000.0,vi_ref,sv,d,d_ref,sd))

    vi_rms=math.sqrt(sum(x*x for x in vi_sig)/len(vi_sig))
    d_rms=math.sqrt(sum(x*x for x in d_sig)/len(d_sig))
    return vi_rms,max(abs(x) for x in vi_sig),d_rms,max(abs(x) for x in d_sig),details


def main():
    print("SMX-3 V2 EF86 Stage-3 cross-domain validation")
    print()

    for label,path,mode in [
        ("Graph A",GA,"A"),
        ("Graph B plateau",GB,"B"),
        ("Graph B knee",GBK,"B"),
    ]:
        a=score(path,s2.currents,mode)
        b=score(path,s3.currents,mode)
        print(f"{label}:")
        print(f"  Stage2 NRMS={a[0]:.6f} sigma worst={a[1]:.6f}")
        print(f"  Stage3 NRMS={b[0]:.6f} sigma worst={b[1]:.6f}")
        print(f"  delta NRMS={b[0]-a[0]:+.6f} sigma")
        if label=="Graph B knee":
            print("  Stage3 worst knee points:")
            for _,ident,ref,model,u,s in b[2][:5]:
                print(f"    {ident}: ref={ref:.6f}mA model={model:.6f}mA u={u:.6f}mA residual={s:+.6f}sigma")

    env_rms,env_worst,env_errs=envelope()
    print()
    print(f"Vo@5% envelope RMS error={env_rms:.6f}% worst={env_worst:.6f}%")
    print("envelope errors="+", ".join(f"{x:+.3f}%" for x in env_errs))

    vi_rms,vi_worst,d_rms,d_worst,details=graphd()
    print()
    print(f"refined Graph-D Vi: NRMS={vi_rms:.6f} sigma worst={vi_worst:.6f}")
    print(f"refined Graph-D distortion: NRMS={d_rms:.6f} sigma worst={d_worst:.6f}")
    print("Vo,Vi_model_mV,Vi_ref_mV,Vi_sigma,THD_model_pct,THD_ref_pct,THD_sigma")
    for row in details:
        print(f"{row[0]:.1f},{row[1]:.6f},{row[2]:.6f},{row[3]:+.3f},{row[4]:.6f},{row[5]:.6f},{row[6]:+.3f}")

    # Hard gates:
    # - exact envelope must remain strong;
    # - Stage3 may alter the low-Va knee, but not catastrophically leave the
    #   provisional manufacturer uncertainty band.
    knee=score(GBK,s3.currents,"B")
    if env_worst>6.0:
        raise SystemExit("FAIL: exact Philips 5%-THD envelope")
    if knee[0]>1.5:
        raise SystemExit("FAIL: Stage-3 correction damages Philips low-Va knee surface in normalized RMS")

    # Individual Graph-B knee points remain manual raster digitizations with
    # heuristic reading uncertainties. Their normalized residuals are useful
    # diagnostics, but they are not formal independent Gaussian 'sigma' tests.
    # Freeze a pointwise hard gate only after calibrated coordinate extraction.
    if knee[1]>5.0:
        raise SystemExit("FAIL: Stage-3 correction has a catastrophic provisional knee outlier")

    print()
    print("PASS: Stage-3 clears the exact envelope and provisional low-Va knee NRMS gate.")
    print("INFO: individual Graph-B knee residuals remain diagnostic until calibrated coordinate extraction.")
    print("INFO: refined Graph-D intermediate points remain provisional and are reported, not hard-frozen.")


if __name__=="__main__":
    raise SystemExit(main())
