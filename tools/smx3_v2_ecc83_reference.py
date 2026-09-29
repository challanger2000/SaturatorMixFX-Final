#!/usr/bin/env python3
"""Offline ECC83/12AX7 reference calculations for SMX-3 V2.

Research tool only. Implements the published Dempwolf/Zoelzer 12AX7 current
model and solves the selected Mullard 250 V / 100 kOhm / 1.5 kOhm
common-cathode operating point.

No third-party dependencies.
"""

import argparse
import math

TUBES = {
    "RSD-1": {
        "G": 2.242e-3, "mu": 103.2, "gamma": 1.26, "C": 3.40,
        "Gg": 6.177e-4, "xi": 1.314, "Cg": 9.901, "Ig0": 8.025e-8,
    },
    "RSD-2": {
        "G": 2.173e-3, "mu": 100.2, "gamma": 1.28, "C": 3.19,
        "Gg": 5.911e-4, "xi": 1.358, "Cg": 11.76, "Ig0": 4.527e-8,
    },
    "EHX-1": {
        "G": 1.371e-3, "mu": 86.9, "gamma": 1.349, "C": 4.56,
        "Gg": 3.263e-4, "xi": 1.156, "Cg": 11.99, "Ig0": 3.917e-8,
    },
}

MULLARD = {
    "supply_v": 250.0,
    "ra_ohm": 100000.0,
    "rk_ohm": 1500.0,
    "ik_a": 0.00086,
    "gain_abs": 54.5,
}


def softplus_scaled(x, c):
    z = c * x
    if z > 50.0:
        return x
    if z < -50.0:
        return math.exp(z) / c
    return math.log1p(math.exp(z)) / c


def currents(params, va, vg):
    """Return Ik, Ia, Ig in ampere. va/vg are relative to cathode."""
    ik = params["G"] * softplus_scaled(va / params["mu"] + vg, params["C"]) ** params["gamma"]
    ig = params["Gg"] * softplus_scaled(vg, params["Cg"]) ** params["xi"] + params["Ig0"]
    ia = ik - ig
    return ik, ia, ig


def solve_bias(params, vb, ra, rk, max_iter=20000, tol=1e-13):
    """Solve cathode-biased common-cathode DC point by damped fixed-point."""
    vk = 1.2
    vp = 165.0
    for i in range(max_iter):
        va = vp - vk
        vg = -vk
        ik, ia, ig = currents(params, va, vg)
        vk_new = ik * rk
        vp_new = vb - ia * ra

        err = max(abs(vk_new - vk), abs(vp_new - vp))
        if err < tol:
            return {
                "iterations": i,
                "vk_v": vk,
                "vp_v": vp,
                "va_v": va,
                "vg_v": vg,
                "ik_a": ik,
                "ia_a": ia,
                "ig_a": ig,
            }

        # Damping keeps all three published fits stable in this circuit.
        vk = 0.70 * vk + 0.30 * vk_new
        vp = 0.70 * vp + 0.30 * vp_new

    raise RuntimeError("bias solver did not converge")


def solve_plate_for_grid(params, vb, ra, vk_dc, vin, vp_seed):
    """Static plate solution with cathode AC-bypassed at its DC voltage."""
    vp = vp_seed
    for _ in range(10000):
        va = vp - vk_dc
        vg = vin - vk_dc
        _, ia, _ = currents(params, va, vg)
        vp_new = vb - ia * ra
        if abs(vp_new - vp) < 1e-13:
            return vp
        vp = 0.80 * vp + 0.20 * vp_new
    raise RuntimeError("plate solver did not converge")


def small_signal_gain(params, bias, vb, ra):
    dv = 1e-4
    p_plus = solve_plate_for_grid(params, vb, ra, bias["vk_v"], +dv, bias["vp_v"])
    p_minus = solve_plate_for_grid(params, vb, ra, bias["vk_v"], -dv, bias["vp_v"])
    return (p_plus - p_minus) / (2.0 * dv)


def pct_error(value, reference):
    return 100.0 * (value - reference) / reference


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tube", choices=list(TUBES) + ["all"], default="all")
    args = ap.parse_args()

    names = list(TUBES) if args.tube == "all" else [args.tube]

    print("SMX-3 V2 ECC83 reference")
    print("Mullard target: Vb=250 V, Ra=100 kOhm, Rk=1.5 kOhm, Ik~0.86 mA, |Av|~54.5")
    print()
    print("tube,Ik_mA,Vk_V,Vp_V,Va_V,Ig_uA,Av,Ik_error_pct,gain_error_pct")

    for name in names:
        p = TUBES[name]
        b = solve_bias(p, MULLARD["supply_v"], MULLARD["ra_ohm"], MULLARD["rk_ohm"])
        av = small_signal_gain(p, b, MULLARD["supply_v"], MULLARD["ra_ohm"])
        print(
            f"{name},"
            f"{b['ik_a']*1e3:.9f},"
            f"{b['vk_v']:.9f},"
            f"{b['vp_v']:.9f},"
            f"{b['va_v']:.9f},"
            f"{b['ig_a']*1e6:.9f},"
            f"{av:.9f},"
            f"{pct_error(b['ik_a'], MULLARD['ik_a']):.6f},"
            f"{pct_error(abs(av), MULLARD['gain_abs']):.6f}"
        )


if __name__ == "__main__":
    main()
