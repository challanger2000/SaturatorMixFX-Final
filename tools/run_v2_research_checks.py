#!/usr/bin/env python3
"""Run SMX-3 V2 research regression checks locally.

This runner intentionally avoids network access and third-party Python
packages. It executes the research tools already checked into the repository.

Some tools encode expected rejections of provisional models. Those tools must
exit successfully after printing their documented rejection conclusion.
"""

import os
import subprocess
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHECKS = [
    ["tools/smx3_v1_oversampling_baseline.py", "--sample-rate", "44100"],
    ["tools/smx3_v2_ecc83_reference.py", "--check"],
    ["tools/smx3_v2_ecc83_mullard_fit.py"],
    ["tools/smx3_v2_ecc83_large_signal_probe.py"],
    ["tools/smx3_v2_ef86_candidate_baseline.py"],
    ["tools/smx3_v2_ef86_provisional_fit.py"],
    ["tools/smx3_v2_jiles_atherton_reference.py"],
    ["tools/smx3_v2_jensen_linear_reference.py"],
    ["tools/smx3_v2_iron_coupled_probe.py"],
]


def run_one(args):
    cmd=[sys.executable]+[os.path.join(ROOT,args[0])]+args[1:]
    print("="*78)
    print("RUN", " ".join(args))
    proc=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
    if proc.stdout:
        print(proc.stdout.rstrip())
    if proc.stderr:
        print(proc.stderr.rstrip(),file=sys.stderr)
    print("EXIT",proc.returncode)
    return proc.returncode


def main():
    failed=[]
    for args in CHECKS:
        rc=run_one(args)
        if rc!=0:
            failed.append((args,rc))

    print("="*78)
    if failed:
        print("RESEARCH CHECK FAILURES:")
        for args,rc in failed:
            print(f"- {' '.join(args)} -> {rc}")
        return 1

    print(f"PASS: {len(CHECKS)} SMX-3 V2 research checks completed.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
