#!/usr/bin/env python3
"""Local two-parameter fit for SMX-3 V2 IRON dynamic loss.

Fits ONLY:
- A_v classical-loss coefficient
- B_v excess-loss coefficient

All quasi-static Jiles-Atherton parameters remain frozen at the corrected
candidate values. This is intentionally minimal.

Targets:
- +4 dBu / 20 Hz THD = 0.025%
- +20 dBu / 20 Hz THD = 1.0%
- 20 Hz / 1 kHz = -0.04 dB
- Jensen DLP low-frequency maximum ~ +0.6 deg
- Jensen DLP worst <= 2 deg

No HF parasitic fit is done here; 20 kHz/95 kHz are handled separately.
"""

import math

import smx3_v2_iron_excess_loss_sensitivity as sens


def objective(av,bv):
    r=sens.evaluate(av,bv)
    cost=(
        ((r["low_thd"]-0.025)/0.003)**2
        +((r["high_thd"]-1.0)/0.03)**2
        +((r["rel20"]-(-0.04))/0.006)**2
        +((r["dlp_max"]-0.6)/0.20)**2
        +(max(0.0,r["dlp_worst"]-2.0)/0.20)**2
        +(max(0.0,abs(r["dlp_min"])-2.0)/0.20)**2
    )
    return cost,r


def fit():
    # Broad deterministic seed grid.
    seeds=[]
    for av in (0.0,0.01,0.03,0.10,0.30,1.0):
        for bv in (0.0,0.01,0.03,0.10,0.30,1.0,3.0,10.0):
            seeds.append((av,bv))

    best=None
    for av,bv in seeds:
        c,r=objective(av,bv)
        cand=(c,av,bv,r)
        if best is None or cand[0]<best[0]:
            best=cand

    _,av,bv,_=best

    # Coordinate refinement in log-like additive scales, retaining >=0.
    step_a=max(0.02,0.35*max(av,0.1))
    step_b=max(0.02,0.35*max(bv,0.1))

    for _ in range(26):
        current=objective(av,bv)
        local=(current[0],av,bv,current[1])
        improved=False

        trials=[
            (max(0.0,av-step_a),bv),
            (av+step_a,bv),
            (av,max(0.0,bv-step_b)),
            (av,bv+step_b),
            (max(0.0,av-step_a),max(0.0,bv-step_b)),
            (max(0.0,av-step_a),bv+step_b),
            (av+step_a,max(0.0,bv-step_b)),
            (av+step_a,bv+step_b),
        ]

        for ta,tb in trials:
            c,r=objective(ta,tb)
            cand=(c,ta,tb,r)
            if cand[0]<local[0]:
                local=cand
                improved=True

        _,av,bv,_=local

        if not improved:
            step_a*=0.5
            step_b*=0.5

        if max(step_a,step_b)<5e-4:
            break

    c,r=objective(av,bv)
    return c,av,bv,r


def main():
    cost,av,bv,r=fit()

    print("SMX-3 V2 IRON local dynamic-loss fit")
    print(f"A_v = {av:.9f}")
    print(f"B_v = {bv:.9f}")
    print(f"cost = {cost:.9f}")
    print()
    print(f"+4 dBu / 20 Hz THD = {r['low_thd']:.9f}%")
    print(f"+20 dBu / 20 Hz THD = {r['high_thd']:.9f}%")
    print(f"H2 = {r['h2']:.9f}%")
    print(f"H3 = {r['h3']:.9f}%")
    print(f"20 Hz relative = {r['rel20']:.9f} dB")
    print(f"20 kHz relative = {r['rel20k']:.9f} dB")
    print(f"DLP min = {r['dlp_min']:+.9f} deg")
    print(f"DLP max = {r['dlp_max']:+.9f} deg")
    print(f"DLP worst = {r['dlp_worst']:.9f} deg")

    failures=[]
    if abs(r["low_thd"]-0.025)>0.005:
        failures.append("+4 dBu THD")
    if abs(r["high_thd"]-1.0)>0.05:
        failures.append("+20 dBu THD")
    if abs(r["rel20"]-(-0.04))>0.01:
        failures.append("20 Hz magnitude")
    if r["dlp_worst"]>2.0:
        failures.append("DLP max")
    if not (0.2<=r["dlp_max"]<=1.2):
        failures.append("DLP low-frequency typical shape")
    if r["h2"]>=0.1*r["h3"]:
        failures.append("H3 dominance")

    if failures:
        print("REJECT:")
        for f in failures:
            print(" - "+f)
        print("Dynamic loss with frozen JA parameters is not sufficient.")
        return 0

    print("PASS: two-parameter dynamic-loss augmentation satisfies first-order Iron constraints with frozen JA parameters.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
