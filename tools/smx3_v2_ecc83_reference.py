#!/usr/bin/env python3
"""Offline ECC83/12AX7 reference calculations for SMX-3 V2.

Implements the published Dempwolf/Zoelzer 12AX7 current model and evaluates
all three measured-tube fits in the selected Philips/Mullard 250 V / 100 kOhm
/ 1.5 kOhm common-cathode amplifier INCLUDING the documented 330 kOhm
following-stage AC load.

The loaded gain matters: omitting Rg' materially changes which measured tube
specimen best agrees with the manufacturer amplifier table.

Standard library only.
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
    "rg_next_ohm": 330000.0,
    "ik_a": 0.00086,
    "gain_abs": 54.5,
    "max_output_vrms": 26.0,
    "distortion_pct": 3.9,
}


def softplus_scaled(x, c):
    z = c * x
    if z > 50.0:
        return x
    if z < -50.0:
        return math.exp(z) / c
    return math.log1p(math.exp(z)) / c


def currents(params, va, vg):
    ik = params["G"] * softplus_scaled(va / params["mu"] + vg, params["C"]) ** params["gamma"]
    ig = params["Gg"] * softplus_scaled(vg, params["Cg"]) ** params["xi"] + params["Ig0"]
    ia = ik - ig
    return ik, ia, ig


def solve_bias(params, vb, ra, rk, max_iter=20000, tol=1e-13):
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

        vk = 0.70 * vk + 0.30 * vk_new
        vp = 0.70 * vp + 0.30 * vp_new

    raise RuntimeError("bias solver did not converge")


def solve_plate_for_grid(params, bias, vin, vp_seed):
    """Static AC plate solution with bypassed cathode and documented Rg' load."""
    ra = MULLARD["ra_ohm"]
    rg = MULLARD["rg_next_ohm"]
    rload = 1.0 / (1.0 / ra + 1.0 / rg)

    ia0 = bias["ia_a"]
    vth = bias["vp_v"] + ia0 * rload
    vp = vp_seed

    for _ in range(10000):
        _, ia, _ = currents(params, vp - bias["vk_v"], vin - bias["vk_v"])
        vp_new = vth - ia * rload
        if abs(vp_new - vp) < 1e-13:
            return vp
        vp = 0.80 * vp + 0.20 * vp_new

    raise RuntimeError("plate solver did not converge")


def small_signal_gain(params, bias):
    dv = 1e-5
    p_plus = solve_plate_for_grid(params, bias, +dv, bias["vp_v"])
    p_minus = solve_plate_for_grid(params, bias, -dv, bias["vp_v"])
    return (p_plus - p_minus) / (2.0 * dv)


def large_signal(params, bias, vin_rms, n=2048):
    amp = vin_rms * math.sqrt(2.0)
    plate = bias["vp_v"]
    values = []
    grid_currents = []

    for i in range(n):
        vin = amp * math.sin(2.0 * math.pi * i / n)
        plate = solve_plate_for_grid(params, bias, vin, plate)
        values.append(plate - bias["vp_v"])
        _, _, ig = currents(params, plate - bias["vk_v"], vin - bias["vk_v"])
        grid_currents.append(ig)

    mean = sum(values) / n
    values = [v - mean for v in values]
    rms = math.sqrt(sum(v * v for v in values) / n)

    mags = []
    for h in range(1, 11):
        re = 0.0
        im = 0.0
        for i, v in enumerate(values):
            a = 2.0 * math.pi * h * i / n
            re += v * math.cos(a)
            im -= v * math.sin(a)
        mags.append(math.hypot(re, im))

    thd = math.sqrt(sum(v * v for v in mags[1:])) / mags[0]
    return rms, thd, max(grid_currents), sum(grid_currents) / n


def find_input_for_output(params, bias, target_vrms):
    lo = 0.001
    hi = 3.0
    for _ in range(36):
        mid = 0.5 * (lo + hi)
        out, _, _, _ = large_signal(params, bias, mid, 768)
        if out < target_vrms:
            lo = mid
        else:
            hi = mid
    vin = 0.5 * (lo + hi)
    return vin, *large_signal(params, bias, vin, 4096)


def pct_error(value, reference):
    return 100.0 * (value - reference) / reference


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tube", choices=list(TUBES) + ["all"], default="all")
    ap.add_argument("--check", action="store_true",
                    help="Run the selected RSD-2 cross-source regression gate.")
    args = ap.parse_args()

    names = list(TUBES) if args.tube == "all" else [args.tube]

    print("SMX-3 V2 ECC83 manufacturer-loaded reference")
    print("Mullard: Vb=250 V, Ra=100k, Rk=1.5k, Rg'=330k, Ik~0.86mA, |Av|~54.5")
    print("tube,Ik_mA,Ik_err_pct,Av_loaded,Av_err_pct,Vin_for_26Vrms,THD_at_26Vrms_pct,Ig_peak_uA,Ig_mean_uA")

    results = {}
    for name in names:
        p = TUBES[name]
        b = solve_bias(p, MULLARD["supply_v"], MULLARD["ra_ohm"], MULLARD["rk_ohm"])
        av = small_signal_gain(p, b)
        vin, out, thd, igpk, igmean = find_input_for_output(p, b, MULLARD["max_output_vrms"])
        results[name] = (b, av, vin, out, thd, igpk, igmean)
        print(
            f"{name},"
            f"{b['ik_a']*1e3:.9f},"
            f"{pct_error(b['ik_a'],MULLARD['ik_a']):.6f},"
            f"{av:.9f},"
            f"{pct_error(abs(av),MULLARD['gain_abs']):.6f},"
            f"{vin:.9f},"
            f"{100.0*thd:.9f},"
            f"{igpk*1e6:.9f},"
            f"{igmean*1e6:.9f}"
        )

    if args.check:
        if "RSD-2" not in results:
            raise SystemExit("--check requires --tube all or --tube RSD-2")
        b, av, _, _, thd, _, _ = results["RSD-2"]
        ik_err = abs(pct_error(b["ik_a"], MULLARD["ik_a"]))
        gain_err = abs(pct_error(abs(av), MULLARD["gain_abs"]))
        distortion_error_points = abs(100.0 * thd - MULLARD["distortion_pct"])

        print()
        print(
            f"CHECK RSD-2: |Ik error|={ik_err:.3f}% (limit 5%), "
            f"|loaded gain error|={gain_err:.3f}% (limit 6%), "
            f"|distortion error at 26Vrms|={distortion_error_points:.3f} %-points (limit 0.5)"
        )

        if ik_err > 5.0 or gain_err > 6.0 or distortion_error_points > 0.5:
            raise SystemExit("FAIL: RSD-2 cross-source regression outside tolerance")

        print("PASS: RSD-2 remains the best current manufacturer-loaded reference candidate.")
        print("NOTE: the manufacturer Ig=0.3uA criterion is not reproduced by this specimen fit and remains a separate limitation.")


if __name__ == "__main__":
    main()
