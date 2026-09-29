#!/usr/bin/env python3
"""EF86 comparison solver for SMX-3 V2 research.

Implements the independently fitted CC0 Circuit Codex Koren-form EF86 model
as a comparison baseline only. It is NOT the SMX-3 hardware authority.

The script checks:
1) the Philips/Mullard device anchor;
2) the selected Philips R-C amplifier DC point;
3) an approximate low-frequency small-signal gain with cathode/screen
   bypassed for AC and the documented 330 kOhm following-grid load.

Standard library only.
"""

import math

P = {
    "MU": 38.0,
    "EX": 1.5,
    "KG1": 1051.45,
    "KG2": 3013.64,
    "KP": 143.216,
    "KVB": 30.0,
}

PHILIPS_DEVICE = {
    "vp_v": 250.0,
    "vg2_v": 140.0,
    "vg1_v": -2.2,
    "ia_a": 0.0030,
    "ig2_a": 0.0006,
}

PHILIPS_AMP = {
    "vb_v": 250.0,
    "ra_ohm": 100000.0,
    "rg2_ohm": 390000.0,
    "rk_ohm": 1000.0,
    "next_grid_ohm": 330000.0,
    "ik_a": 0.0020,
    "gain_abs": 123.0,
}


def uramp(x):
    return x if x > 0.0 else 0.0


def log1pexp(x):
    if x > 50.0:
        return x
    if x < -50.0:
        return math.exp(x)
    return math.log1p(math.exp(x))


def currents(vp, vg2, vg1):
    """Koren-form comparison model currents in ampere, voltages to cathode."""
    if vg2 <= 1.0e-12 or vp <= 0.0:
        return 0.0, 0.0

    z = P["KP"] * (1.0 / P["MU"] + vg1 / vg2)
    e1 = (vg2 / P["KP"]) * log1pexp(z)
    ia = uramp(e1) ** P["EX"] / P["KG1"] * math.atan(vp / P["KVB"])
    ig2 = uramp(vg2 / P["MU"] + vg1) ** P["EX"] / P["KG2"]
    return ia, ig2


def solve_dc():
    vb = PHILIPS_AMP["vb_v"]
    ra = PHILIPS_AMP["ra_ohm"]
    rg2 = PHILIPS_AMP["rg2_ohm"]
    rk = PHILIPS_AMP["rk_ohm"]

    vp_node = 100.0
    vg2_node = 110.0
    vk = 2.0

    for iteration in range(20000):
        ia, ig2 = currents(vp_node - vk, vg2_node - vk, -vk)
        vp_new = vb - ia * ra
        vg2_new = vb - ig2 * rg2
        vk_new = (ia + ig2) * rk

        err = max(abs(vp_new-vp_node), abs(vg2_new-vg2_node), abs(vk_new-vk))
        if err < 1.0e-12:
            return {
                "iterations": iteration,
                "vp_node_v": vp_node,
                "vg2_node_v": vg2_node,
                "vk_v": vk,
                "ia_a": ia,
                "ig2_a": ig2,
                "ik_a": ia + ig2,
            }

        # Conservative damping for deterministic convergence.
        d = 0.10
        vp_node = (1.0-d)*vp_node + d*vp_new
        vg2_node = (1.0-d)*vg2_node + d*vg2_new
        vk = (1.0-d)*vk + d*vk_new

    raise RuntimeError("DC solver did not converge")


def solve_plate_ac(vin, dc):
    """Low-frequency AC plate solution with cathode/screen bypassed.

    The 330 kOhm next-stage grid resistor loads the plate through the coupling
    capacitor for AC, so the effective plate load is Ra || 330 kOhm.
    """
    vb = PHILIPS_AMP["vb_v"]
    ra = PHILIPS_AMP["ra_ohm"]
    rg = PHILIPS_AMP["next_grid_ohm"]
    rload = 1.0 / (1.0/ra + 1.0/rg)

    # Small-signal Thevenin formulation around the DC point:
    # vout = -delta(Ia)*Rload. Solve absolute plate with a virtual supply chosen
    # so vin=0 returns the DC plate voltage.
    ia0, _ = currents(
        dc["vp_node_v"] - dc["vk_v"],
        dc["vg2_node_v"] - dc["vk_v"],
        -dc["vk_v"]
    )
    vth = dc["vp_node_v"] + ia0 * rload

    vp = dc["vp_node_v"]
    for _ in range(20000):
        ia, _ = currents(
            vp - dc["vk_v"],
            dc["vg2_node_v"] - dc["vk_v"],
            vin - dc["vk_v"]
        )
        target = vth - ia * rload
        if abs(target-vp) < 1.0e-13:
            return vp
        vp = 0.8*vp + 0.2*target
    raise RuntimeError("AC plate solver did not converge")


def pct_error(value, reference):
    return 100.0 * (value-reference) / reference


def main():
    # Device anchor.
    ia, ig2 = currents(
        PHILIPS_DEVICE["vp_v"],
        PHILIPS_DEVICE["vg2_v"],
        PHILIPS_DEVICE["vg1_v"],
    )

    dc = solve_dc()

    dv = 1.0e-5
    p_plus = solve_plate_ac(+dv, dc)
    p_minus = solve_plate_ac(-dv, dc)
    av = (p_plus-p_minus)/(2.0*dv)

    print("SMX-3 V2 EF86 comparison baseline")
    print("Candidate: Circuit Codex CC0 Koren-form EF86")
    print()
    print(f"Device anchor Ia: {ia*1e3:.9f} mA  target 3.000000000 mA")
    print(f"Device anchor Ig2: {ig2*1e3:.9f} mA target 0.600000000 mA")
    print()
    print(f"RC amplifier Ik: {dc['ik_a']*1e3:.9f} mA target 2.000000000 mA")
    print(f"RC amplifier Va node: {dc['vp_node_v']:.9f} V")
    print(f"RC amplifier Vg2 node: {dc['vg2_node_v']:.9f} V")
    print(f"RC amplifier Vk: {dc['vk_v']:.9f} V")
    print(f"Approx AC gain: {av:.9f} V/V target -123 V/V")
    print()
    print(f"Ik error: {pct_error(dc['ik_a'],PHILIPS_AMP['ik_a']):.6f}%")
    print(f"Gain magnitude error: {pct_error(abs(av),PHILIPS_AMP['gain_abs']):.6f}%")

    # This candidate is expected to hit its one fitted device anchor but is not
    # expected to pass the full amplifier validation. Treat a surprisingly
    # good amplifier fit as information, not a release gate.
    if abs(pct_error(ia,PHILIPS_DEVICE["ia_a"])) > 0.1:
        raise SystemExit("FAIL: candidate no longer reproduces its published Ia anchor")
    if abs(pct_error(ig2,PHILIPS_DEVICE["ig2_a"])) > 0.1:
        raise SystemExit("FAIL: candidate no longer reproduces its published Ig2 anchor")

    print("PASS: comparison candidate reproduces its device anchor.")
    print("NOTE: amplifier errors determine whether it can be promoted beyond comparison status.")


if __name__ == "__main__":
    main()
