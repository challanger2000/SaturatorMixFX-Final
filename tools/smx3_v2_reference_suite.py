#!/usr/bin/env python3
"""SMX-3 V2 offline reference-suite runner.

Runs the research/reference tools that define the current hardware-model
baseline. This is intentionally independent of VST3/DAW execution.

Positive gates must exit 0.
Known-rejection tools are run for visibility but are not promoted to PASS.

Standard library only.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]
PY=sys.executable


POSITIVE=[
    ("IRON numerical-method cross-check", ["tools/smx3_v2_iron_method_crosscheck.py"]),
    ("provisional Iron exact-anchor candidate", ["tools/smx3_v2_iron_candidate.py"]),
    ("ECC83 operating point", ["tools/smx3_v2_ecc83_reference.py","--check"]),
    ("ECC83 large signal", ["tools/smx3_v2_ecc83_large_signal.py"]),
    ("ECC83 dynamic convergence", ["tools/smx3_v2_ecc83_dynamic_convergence.py"]),
    ("ECC83 integration-method cross-check", ["tools/smx3_v2_ecc83_method_crosscheck.py"]),
    ("ECC83 operating-domain gate", ["tools/smx3_v2_ecc83_domain_probe.py"]),
    ("EF86 EX=1.40 hardware candidate", ["tools/smx3_v2_ef86_candidate_gate.py"]),
    ("EF86 dynamic offline reference", ["tools/smx3_v2_ef86_dynamic_reference.py"]),
    ("IRON realtime integration reduction", ["tools/smx3_v2_iron_realtime_reduction.py"]),
    ("Jensen linear skeleton", ["tools/smx3_v2_jensen_linear_reference.py"]),
    ("Jiles-Atherton standalone loop", ["tools/smx3_v2_jiles_atherton_reference.py"]),
]

INFORMATIONAL=[
    ("IRON reset convergence", ["tools/smx3_v2_iron_reset_convergence.py"]),
    ("EF86 dynamic Graph-D probe", ["tools/smx3_v2_ef86_dynamic_graphD.py"]),
    ("EF86 EX=1.40 Graph-D out-of-fit", ["tools/smx3_v2_ef86_ex140_graphD.py"]),
    ("EF86 Stage-2C out-of-fit large-signal", ["tools/smx3_v2_ef86_stage2c_large_signal.py"]),
    ("EF86 Graph-B model-family comparison", ["tools/smx3_v2_ef86_graphB_compare.py"]),
    ("EF86 Graph-A model-family comparison", ["tools/smx3_v2_ef86_graphA_compare.py"]),
    ("EF86 exact multi-supply envelope", ["tools/smx3_v2_ef86_full_envelope.py"]),
    ("EF86 Graph-D shape check", ["tools/smx3_v2_ef86_graphD_validate.py"]),
    ("physical level calibration candidate", ["tools/smx3_v2_level_calibration.py"]),
    ("V1 oversampling baseline", ["tools/smx3_v1_oversampling_baseline.py","--sample-rate","44100"]),
    ("EF86 independent comparison baseline", ["tools/smx3_v2_ef86_candidate_baseline.py"]),
    ("IRON coupled rejection probe", ["tools/smx3_v2_iron_coupled_probe.py"]),
]

EXPECTED_FAILURE=[
    ("EF86 six-parameter large-signal rejection", ["tools/smx3_v2_ef86_large_signal_gate.py"]),
]


def run_case(label,args,verbose):
    cmd=[PY,str(ROOT/args[0]),*args[1:]]
    p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
    if verbose or p.returncode != 0:
        print(f"\n===== {label} =====")
        if p.stdout:
            print(p.stdout.rstrip())
        if p.stderr:
            print(p.stderr.rstrip(),file=sys.stderr)
    return p.returncode


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--verbose",action="store_true")
    args=ap.parse_args()

    failures=[]
    print("SMX-3 V2 offline reference suite")
    print()

    for label,cmd in POSITIVE:
        rc=run_case(label,cmd,args.verbose)
        status="PASS" if rc==0 else "FAIL"
        print(f"[{status}] {label}")
        if rc!=0:
            failures.append(label)

    for label,cmd in EXPECTED_FAILURE:
        rc=run_case(label,cmd,args.verbose)
        status="EXPECTED-REJECTION" if rc!=0 else "UNEXPECTED-PASS"
        print(f"[{status}] {label}")
        if rc==0:
            failures.append(label+" unexpectedly passed")

    for label,cmd in INFORMATIONAL:
        rc=run_case(label,cmd,args.verbose)
        status="INFO-OK" if rc==0 else "INFO-ERROR"
        print(f"[{status}] {label}")
        if rc!=0:
            failures.append(label+" execution error")

    print()
    if failures:
        print("REFERENCE SUITE FAIL")
        for f in failures:
            print(" - "+f)
        return 1

    print("REFERENCE SUITE PASS")
    print("Note: this validates frozen offline research gates, not VST3 release QA.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
