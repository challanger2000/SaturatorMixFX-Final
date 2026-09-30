#!/usr/bin/env python3
"""Provisional ECC83 Mullard multi-point fit for SMX-3 V2.

Fits the Dempwolf/Zoelzer triode equation family to Mullard's full
100 kOhm R.C.-coupled amplifier table (Vb=200..400 V), using the documented
330 kOhm following-stage grid resistor as the AC load.

IMPORTANT:
This is a provisional manufacturer-table fit. It is not promoted to the final
TRIODE hardware reference until plate-current/grid-current curve families and
large-signal distortion are validated.

Standard library only; this file freezes the fitted result and checks it.
"""

import math

# Fitted plate/cathode-current model parameters.
P = {
    "G": 2.18714303e-3,
    "mu": 105.447663,
    "gamma": 1.07136184,
    "C": 2.60122984,

    # Grid-current law retained provisionally from Dempwolf/Zoelzer EHX-1
    # because the Mullard small-signal table does not identify these terms.
    "Gg": 3.263e-4,
    "xi": 1.156,
    "Cg": 11.99,
    "Ig0": 3.917e-8,
}

RA = 100000.0
RLOAD = 330000.0
RPAR = 1.0 / (1.0/RA + 1.0/RLOAD)

MULLARD = {
    200.0: {"rk":1800.0, "ik":0.00065, "gain":50.0},
    250.0: {"rk":1500.0, "ik":0.00086, "gain":54.5},
    300.0: {"rk":1200.0, "ik":0.00111, "gain":57.0},
    350.0: {"rk":1000.0, "ik":0.00140, "gain":61.0},
    400.0: {"rk": 820.0, "ik":0.00172, "gain":63.0},
}


def softplus_scaled(x, c):
    z = c*x
    if z > 50.0:
        return x
    if z < -50.0:
        return math.exp(z)/c
    return math.log1p(math.exp(z))/c


def currents(va, vg):
    ik = P["G"] * softplus_scaled(va/P["mu"] + vg, P["C"]) ** P["gamma"]
    ig = P["Gg"] * softplus_scaled(vg, P["Cg"]) ** P["xi"] + P["Ig0"]
    ia = ik - ig
    return ia, ik, ig


def solve_bias(vb, rk):
    vk = 1.2
    vp = 165.0

    for _ in range(30000):
        ia, ik, ig = currents(vp-vk, -vk)
        new_vk = ik*rk
        new_vp = vb - ia*RA

        if max(abs(new_vk-vk), abs(new_vp-vp)) < 1e-12:
            return vp, vk, ia, ik, ig

        d = 0.35
        vk = (1.0-d)*vk + d*new_vk
        vp = (1.0-d)*vp + d*new_vp

    raise RuntimeError("DC solver did not converge")


def midband_gain(bias):
    vp, vk, _, _, _ = bias
    va = vp-vk
    vg = -vk
    dv = 1e-4

    gp = (currents(va+dv,vg)[0] - currents(va-dv,vg)[0])/(2.0*dv)
    gm = (currents(va,vg+dv)[0] - currents(va,vg-dv)[0])/(2.0*dv)

    # Cathode bypassed for AC. The documented following-stage grid resistor
    # loads the anode through the coupling capacitor in the midband.
    return gm*RPAR/(1.0 + gp*RPAR)


def pct(v, ref):
    return 100.0*(v-ref)/ref


def main():
    print("SMX-3 V2 ECC83 provisional Mullard multi-point fit")
    print("Ra=100k, following-stage load=330k")
    print("Vb_V,Ik_mA,target_Ik_mA,Ik_error_pct,Av,target_Av,Av_error_pct")

    max_i = 0.0
    max_g = 0.0

    for vb in sorted(MULLARD):
        target = MULLARD[vb]
        b = solve_bias(vb,target["rk"])
        av = midband_gain(b)
        ei = pct(b[3],target["ik"])
        eg = pct(av,target["gain"])
        max_i = max(max_i,abs(ei))
        max_g = max(max_g,abs(eg))

        print(
            f"{vb:.1f},{b[3]*1e3:.9f},{target['ik']*1e3:.9f},"
            f"{ei:.6f},{av:.9f},{target['gain']:.9f},{eg:.6f}"
        )

    print()
    print(f"max |Ik error| = {max_i:.6f}%")
    print(f"max |gain error| = {max_g:.6f}%")

    if max_i > 2.0:
        raise SystemExit("FAIL: cathode-current table fit outside provisional tolerance")
    if max_g > 2.5:
        raise SystemExit("FAIL: gain table fit outside provisional tolerance")

    print("PASS: provisional ECC83 table fit stays within frozen tolerances.")
    print("WARNING: plate/grid-current curves and large-signal distortion still gate promotion.")


if __name__ == "__main__":
    main()
