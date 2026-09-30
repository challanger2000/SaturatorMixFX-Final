#!/usr/bin/env python3
"""Practical-rate numerical benchmark for SMX-3 V2 PENTODE.

Compare the same dynamic EF86 physical model at 48/96/192 kHz against a
high-density offline authority. This isolates numerical integration error;
aliasing is intentionally assessed separately.

Standard library only.
"""

import smx3_v2_ef86_dynamic_reference as ref


CASES=[
    ("1k low",1000.0,0.010,768000.0,True),
    ("1k medium",1000.0,0.180,768000.0,True),
    ("4k low",4000.0,0.010,1536000.0,False),
    ("8k low",8000.0,0.010,3072000.0,False),
    ("8k medium",8000.0,0.120,3072000.0,False),
    ("12k low",12000.0,0.010,4608000.0,False),
]

RATES=(48000.0,96000.0,192000.0)


def phase_delta(a,b):
    d=a-b
    while d>180.0:d-=360.0
    while d<-180.0:d+=360.0
    return d


def main():
    print("SMX-3 V2 PENTODE practical-rate numerical benchmark")
    print("Aliasing is not assessed by this tool.")
    print()
    print("case,rate,gain_ppm,phase_residual_deg,THD_residual_pp")

    worst={r:{"gain":0.0,"phase":0.0,"thd":0.0} for r in RATES}

    for label,freq,vin,fsref,compare_thd in CASES:
        auth=ref.simulate(freq,vin,fs=fsref,warmup_seconds=0.4,cycles=8)

        for rate in RATES:
            if rate/freq < 4.0:
                print(f"{label},{rate:.0f},SKIP,SKIP,SKIP")
                continue

            cand=ref.simulate(freq,vin,fs=rate,warmup_seconds=0.4,cycles=8)
            gppm=1e6*abs(cand["gain"]-auth["gain"])/max(abs(auth["gain"]),1e-30)
            pdeg=abs(phase_delta(cand["phase_deg"],auth["phase_deg"]))
            if compare_thd:
                thdpp=100.0*abs(cand["thd"]-auth["thd"])
                worst[rate]["thd"]=max(worst[rate]["thd"],thdpp)
                thd_text=f"{thdpp:.9f}"
            else:
                thd_text="NA"

            worst[rate]["gain"]=max(worst[rate]["gain"],gppm)
            worst[rate]["phase"]=max(worst[rate]["phase"],pdeg)

            print(f"{label},{rate:.0f},{gppm:.6f},{pdeg:.9f},{thd_text}")

    print()
    for rate in RATES:
        w=worst[rate]
        if w["gain"]<=1000.0 and w["phase"]<=0.1 and w["thd"]<=0.02:
            cls="STRONG"
        elif w["gain"]<=5000.0 and w["phase"]<=0.5 and w["thd"]<=0.10:
            cls="PLAUSIBLE"
        else:
            cls="WEAK"

        print(
            f"{rate:.0f} Hz: gain={w['gain']:.3f} ppm "
            f"phase={w['phase']:.6f} deg THD={w['thd']:.6f} pp -> {cls}"
        )

    print()
    print("INFO: high-frequency THD is excluded from numerical-rate classification; production oversampling depends on a separate alias-energy matrix.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
