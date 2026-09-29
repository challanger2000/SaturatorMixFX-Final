#!/usr/bin/env python3
"""Offline Jiles-Atherton magnetic reference for SMX-3 V2 IRON research.

This is deliberately NOT the production transformer DSP and NOT a fitted
JT-11P-1 model. It reproduces the magnetization law used by Holters/Zoelzer
(DAFx-2016) with their example parameter set and generates deterministic
major/minor-loop data for solver validation.

Standard library only.
"""

import argparse
import csv
import math

PARAMS = {
    # Example set printed in Holters/Zoelzer Fig. 2, taken there from [4].
    "a": 14.1,
    "alpha": 5.0e-5,
    "c": 0.55,
    "k": 17.8,
    "Ms": 2.75e5,
}


def langevin(x):
    ax = abs(x)
    if ax < 1.0e-4:
        # Paper eq. (29) first-order local series.
        return x / 3.0
    return 1.0 / math.tanh(x) - 1.0 / x


def langevin_d(x):
    ax = abs(x)
    if ax < 1.0e-4:
        # Paper eq. (30).
        return 1.0 / 3.0
    s = math.sinh(x)
    return 1.0/(x*x) - 1.0/(s*s)


def dmdh(H, M, direction, p=PARAMS):
    """Explicit dM/dH form derived algebraically from paper eq. (14)."""
    a = p["a"]
    alpha = p["alpha"]
    c = p["c"]
    k = p["k"]
    Ms = p["Ms"]

    q = (H + alpha*M) / a
    Man = Ms * langevin(q)
    Ld = langevin_d(q)

    delta = 1.0 if direction >= 0.0 else -1.0
    dm = Man - M
    delta_m = 1.0 if delta * dm >= 0.0 else 0.0

    den = (1.0-c)*delta*k - alpha*dm
    if abs(den) < 1.0e-12:
        den = math.copysign(1.0e-12, den if den != 0.0 else delta)

    irreversible = (1.0-c)*delta_m*dm / den
    reversible_coeff = c * Ms / a * Ld

    # y = irreversible + reversible_coeff*(1 + alpha*y)
    yden = 1.0 - alpha*reversible_coeff
    if abs(yden) < 1.0e-12:
        yden = math.copysign(1.0e-12, yden if yden != 0.0 else 1.0)

    return (irreversible + reversible_coeff) / yden


def rk4_step(H, M, dH, p=PARAMS):
    direction = 1.0 if dH >= 0.0 else -1.0

    def f(h, m):
        return dmdh(h, m, direction, p)

    k1 = f(H, M)
    k2 = f(H + 0.5*dH, M + 0.5*dH*k1)
    k3 = f(H + 0.5*dH, M + 0.5*dH*k2)
    k4 = f(H + dH, M + dH*k3)
    return M + dH*(k1 + 2*k2 + 2*k3 + k4)/6.0


def segment(H0, H1, M0, steps, p=PARAMS):
    rows = []
    H = H0
    M = M0
    dH = (H1-H0)/steps
    for _ in range(steps):
        rows.append((H, M))
        M = rk4_step(H, M, dH, p)
        H += dH
    rows.append((H1, M))
    return rows, M


def build_loop(hmax=250.0, steps=5000, minor=False):
    # Demagnetized start -> positive saturation -> negative -> positive.
    rows = []
    H = 0.0
    M = 0.0

    for target in (hmax, -hmax, hmax):
        seg, M = segment(H, target, M, steps, PARAMS)
        if rows:
            seg = seg[1:]
        rows.extend(seg)
        H = target

    if minor:
        # Add an inner excursion to verify path dependence / minor-loop memory.
        for target in (-0.35*hmax, 0.35*hmax, -0.35*hmax):
            seg, M = segment(H, target, M, steps//2, PARAMS)
            seg = seg[1:]
            rows.extend(seg)
            H = target

    return rows


def interpolate_zero_cross(rows, quantity_index):
    """Find H at M=0 or M at H=0 by linear interpolation in a row sequence."""
    for a, b in zip(rows, rows[1:]):
        q0 = a[quantity_index]
        q1 = b[quantity_index]
        if q0 == 0.0:
            return a[1-quantity_index]
        if q0*q1 < 0.0:
            t = -q0/(q1-q0)
            other = a[1-quantity_index] + t*(b[1-quantity_index]-a[1-quantity_index])
            return other
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hmax", type=float, default=250.0)
    ap.add_argument("--steps", type=int, default=5000)
    ap.add_argument("--csv")
    ap.add_argument("--minor", action="store_true")
    args = ap.parse_args()

    rows = build_loop(args.hmax, args.steps, args.minor)

    # Analyze only the descending branch (+Hmax -> -Hmax), where remanence and
    # coercive field are unambiguous.
    n = args.steps
    descending = rows[n:2*n+1]
    remanence = interpolate_zero_cross(descending, 0)  # M at H=0
    coercive = interpolate_zero_cross(descending, 1)  # H at M=0

    max_abs_m = max(abs(M) for _,M in rows)
    if not all(math.isfinite(H) and math.isfinite(M) for H,M in rows):
        raise SystemExit("FAIL: non-finite Jiles-Atherton state")

    print("SMX-3 V2 IRON Jiles-Atherton reference")
    print("Parameters are DAFx-2016 example values; NOT a Jensen fit.")
    print(f"Hmax: {args.hmax:.6f} A/m")
    print(f"max |M|: {max_abs_m:.6f} A/m")
    print(f"descending-branch remanence M(H=0): {remanence:.6f} A/m")
    print(f"descending-branch coercive H(M=0): {coercive:.6f} A/m")
    print("PASS: finite deterministic hysteresis loop generated.")

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["H_A_per_m","M_A_per_m"])
            w.writerows(rows)


if __name__ == "__main__":
    main()
