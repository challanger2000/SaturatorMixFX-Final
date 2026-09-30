#!/usr/bin/env python3
"""Realtime-rate numerical benchmark for SMX-3 V2 TRI0DE.

Compare the same implicit-trapezoid physical ECC83 model at practical internal
rates against a high-density offline reference.

This isolates integration/discretization error. It does NOT measure aliasing.

Standard library only.
"""

import math
import smx3_v2_ecc83_dynamic_reference as ref


CASES=[
    # Frequencies divide 48 kHz exactly, avoiding non-coherent spectral-window
    # leakage in this numerical-rate benchmark.
    ("1k low",1000.0,0.010,768000.0,True),
    ("1k medium",1000.0,0.700,768000.0,True),
    ("4k low",4000.0,0.010,1536000.0,False),
    ("8k low",8000.0,0.010,3072000.0,False),
    ("8k medium",8000.0,0.300,3072000.0,False),
    ("12k low",12000.0,0.010,4608000.0,False),
]

RATES=(48000.0,96000.0,192000.0,384000.0,768000.0)


def phase_delta(a,b):
    d=a-b
    while d>180.0:d-=360.0
    while d<-180.0:d+=360.0
    return d


def main():
    print("SMX-3 V2 TRI0DE practical-rate numerical benchmark")
    print("Same implicit-trapezoid physical model; aliasing not assessed.")
    print()
    print("case,rate,gain_ppm,phase_residual_deg,THD_residual_pp")

    worst={r:{"gain":0.0,"phase":0.0,"thd":0.0} for r in RATES}

    for label,freq,vin,fsref,compare_thd in CASES:
        authority=ref.simulate(freq,vin,fs=fsref,warmup_seconds=0.4,cycles=8)

        for rate in RATES:
            # Require sufficient points per cycle. If the requested rate cannot
            # represent the test fundamental with at least 4 samples/cycle,
            # skip rather than produce a meaningless numerical comparison.
            if rate/freq < 4.0:
                print(f"{label},{rate:.0f},SKIP,SKIP,SKIP")
                continue

            cand=ref.simulate(freq,vin,fs=rate,warmup_seconds=0.4,cycles=8)
            gppm=1e6*abs(cand["gain"]-authority["gain"])/max(abs(authority["gain"]),1e-30)
            pdeg=abs(phase_delta(cand["phase_deg"],authority["phase_deg"]))
            # THD is only compared for 1 kHz cases, where H2..H10 all lie
            # comfortably below Nyquist even at 48 kHz. At higher test
            # frequencies different rates expose different harmonic counts
            # and alias paths, so treating total THD as a pure integrator-error
            # metric would be invalid.
            if compare_thd:
                thdpp=100.0*abs(cand["thd"]-authority["thd"])
                worst[rate]["thd"]=max(worst[rate]["thd"],thdpp)
                thd_text=f"{thdpp:.9f}"
            else:
                thdpp=None
                thd_text="NA"

            worst[rate]["gain"]=max(worst[rate]["gain"],gppm)
            worst[rate]["phase"]=max(worst[rate]["phase"],pdeg)

            print(f"{label},{rate:.0f},{gppm:.6f},{pdeg:.9f},{thd_text}")

    print()
    print("WORST RESIDUALS")
    for rate in RATES:
        w=worst[rate]
        print(
            f"{rate:.0f}: gain={w['gain']:.3f} ppm "
            f"phase={w['phase']:.6f} deg THD={w['thd']:.6f} pp"
        )

        if w["gain"]<=1000.0 and w["phase"]<=0.1 and w["thd"]<=0.02:
            cls="STRONG"
        elif w["gain"]<=5000.0 and w["phase"]<=0.5 and w["thd"]<=0.10:
            cls="PLAUSIBLE"
        else:
            cls="WEAK"
        print(f"  numerical-rate classification: {cls}")

    print()
    print("INFO: high-frequency THD is intentionally excluded from numerical-rate classification; aliasing requires a separate test.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
