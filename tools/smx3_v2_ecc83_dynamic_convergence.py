#!/usr/bin/env python3
"""Numerical-convergence matrix for the SMX-3 V2 dynamic ECC83 reference.

This checks the current EHX-1 + Mullard-network offline solver at increasing
integration densities. It is deliberately a NUMERICAL reference test, not a
claim of agreement with Dempwolf Figure-9 laboratory waveforms.

Standard library only.
"""

from smx3_v2_ecc83_dynamic_reference import simulate


CASES = [
    # label, frequency, Vin RMS, sample rates
    ("1k small", 1000.0, 0.010, [192000.0, 384000.0, 768000.0]),
    ("1k nonlinear", 1000.0, 0.700, [192000.0, 384000.0, 768000.0]),
    ("10k small", 10000.0, 0.010, [960000.0, 1920000.0, 3840000.0]),
    ("20k small", 20000.0, 0.010, [1920000.0, 3840000.0, 7680000.0]),
]


def phase_delta_deg(a,b):
    d=a-b
    while d>180.0:
        d-=360.0
    while d<-180.0:
        d+=360.0
    return d


def main():
    print("SMX-3 V2 ECC83 dynamic integration convergence")
    print()

    failures=[]

    for label,freq,vin,rates in CASES:
        print(f"[{label}] f={freq:.1f} Hz Vin={vin:.6f} Vrms")
        rows=[]
        for fs in rates:
            r=simulate(freq,vin,fs=fs,cycles=8)
            rows.append((fs,r))
            print(
                f"  fs={fs:.0f} "
                f"gain={r['gain']:.9f} "
                f"phase={r['phase_deg']:.9f}deg "
                f"THD={100.0*r['thd']:.9f}% "
                f"NewtonMax={r['max_newton']}"
            )

        (fs1,a),(fs2,b)=rows[-2],rows[-1]
        gain_rel=abs(b["gain"]-a["gain"])/max(abs(b["gain"]),1e-30)
        phase_abs=abs(phase_delta_deg(b["phase_deg"],a["phase_deg"]))
        thd_abs=abs(b["thd"]-a["thd"])

        print(
            f"  top-two residual: gain={1e6*gain_rel:.3f} ppm, "
            f"phase={phase_abs:.6f} deg, "
            f"THD={100.0*thd_abs:.6f} percentage-points"
        )

        # Conservative offline-authority limits. These are numerical-error
        # gates, deliberately much tighter than hardware-specimen variation.
        if gain_rel > 2.5e-4:
            failures.append(f"{label}: gain convergence")
        if phase_abs > 0.02:
            failures.append(f"{label}: phase convergence")
        if thd_abs > 2.5e-5:
            failures.append(f"{label}: THD convergence")

        print()

    if failures:
        print("FAIL: dynamic reference integration is not converged:")
        for f in failures:
            print(" - "+f)
        return 1

    print("PASS: dynamic ECC83 aggregate metrics converge within frozen numerical tolerances.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
