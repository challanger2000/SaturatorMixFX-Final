#!/usr/bin/env python3
"""Provisional EF86 multi-anchor reference candidate for SMX-3 V2.

This file freezes a parameter set fitted against:
- Philips 1956 EF86 device anchor at Va=250 V, Vg2=140 V, Vg1=-2 V;
- Ia=3.0 mA, Ig2=0.6 mA, gm=2.0 mA/V;
- Philips 1956 circuit-1 Ik and small-signal gain at Vb=200..400 V.

IMPORTANT:
This is NOT yet the final pentode reference because the full published
Ia(Va,Vg1) curve family has not yet been included in the objective.

Standard library only.
"""

import math

P = {
    "MU": 40.4643134,
    "EX": 1.10072133,
    "KG1": 805.463266,
    "KG2": 2542.71827,
    "KP": 220.481328,
    "KVB": 8.11723096,
}

DEVICE = {
    "vp_v": 250.0,
    "vg2_v": 140.0,
    "vg1_v": -2.0,
    "ia_a": 0.0030,
    "ig2_a": 0.0006,
    "gm_a_per_v": 0.0020,
}

AMP = {
    "ra_ohm": 100000.0,
    "rg2_ohm": 390000.0,
    "rk_ohm": 1000.0,
    "next_grid_ohm": 330000.0,
}

SWEEP = {
    400.0: {"ik_a":0.00330, "gain_abs":124.0},
    350.0: {"ik_a":0.00290, "gain_abs":120.0},
    300.0: {"ik_a":0.00250, "gain_abs":116.0},
    250.0: {"ik_a":0.00210, "gain_abs":112.0},
    200.0: {"ik_a":0.00170, "gain_abs":106.0},
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
    if vg2 <= 1e-12 or vp <= 0.0:
        return 0.0, 0.0

    z = P["KP"] * (1.0 / P["MU"] + vg1 / vg2)
    e1 = (vg2 / P["KP"]) * log1pexp(z)
    ia = uramp(e1) ** P["EX"] / P["KG1"] * math.atan(vp / P["KVB"])
    ig2 = uramp(vg2 / P["MU"] + vg1) ** P["EX"] / P["KG2"]
    return ia, ig2


def solve_dc(vb):
    ra=AMP["ra_ohm"]; rg2=AMP["rg2_ohm"]; rk=AMP["rk_ohm"]
    vp=100.0; vs=110.0; vk=2.0

    for _ in range(30000):
        ia,ig2=currents(vp-vk,vs-vk,-vk)
        t_vp=vb-ia*ra
        t_vs=vb-ig2*rg2
        t_vk=(ia+ig2)*rk
        if max(abs(t_vp-vp),abs(t_vs-vs),abs(t_vk-vk)) < 1e-12:
            return vp,vs,vk,ia,ig2
        d=0.10
        vp=(1-d)*vp+d*t_vp
        vs=(1-d)*vs+d*t_vs
        vk=(1-d)*vk+d*t_vk

    raise RuntimeError("DC solver did not converge")


def gain(dc):
    ra=AMP["ra_ohm"]; rg=AMP["next_grid_ohm"]
    rload=1.0/(1.0/ra+1.0/rg)
    vp,vs,vk,ia0,_=dc
    vth=vp+ia0*rload

    def solve(vin):
        x=vp
        for _ in range(20000):
            ia,_=currents(x-vk,vs-vk,vin-vk)
            target=vth-ia*rload
            if abs(target-x)<1e-13:
                return x
            x=0.8*x+0.2*target
        raise RuntimeError("AC solve did not converge")

    dv=1e-5
    return (solve(dv)-solve(-dv))/(2*dv)


def pct(value,ref):
    return 100.0*(value-ref)/ref


def main():
    ia,ig2=currents(DEVICE["vp_v"],DEVICE["vg2_v"],DEVICE["vg1_v"])
    dv=1e-4
    gm=(currents(DEVICE["vp_v"],DEVICE["vg2_v"],DEVICE["vg1_v"]+dv)[0]
        -currents(DEVICE["vp_v"],DEVICE["vg2_v"],DEVICE["vg1_v"]-dv)[0])/(2*dv)

    print("SMX-3 V2 EF86 provisional multi-anchor fit")
    print(f"Device Ia={ia*1e3:.9f} mA, target=3.000000000, error={pct(ia,DEVICE['ia_a']):+.6f}%")
    print(f"Device Ig2={ig2*1e3:.9f} mA, target=0.600000000, error={pct(ig2,DEVICE['ig2_a']):+.6f}%")
    print(f"Device gm={gm*1e3:.9f} mA/V, target=2.000000000, error={pct(gm,DEVICE['gm_a_per_v']):+.6f}%")
    print()
    print("Vb_V,Ik_mA,target_Ik_mA,Ik_error_pct,Av_abs,target_Av,Av_error_pct")

    max_ik=0.0
    max_gain=0.0
    for vb in sorted(SWEEP.keys(),reverse=True):
        dc=solve_dc(vb)
        ik=dc[3]+dc[4]
        av=abs(gain(dc))
        eik=pct(ik,SWEEP[vb]["ik_a"])
        eg=pct(av,SWEEP[vb]["gain_abs"])
        max_ik=max(max_ik,abs(eik))
        max_gain=max(max_gain,abs(eg))
        print(f"{vb:.1f},{ik*1e3:.9f},{SWEEP[vb]['ik_a']*1e3:.9f},{eik:.6f},{av:.9f},{SWEEP[vb]['gain_abs']:.9f},{eg:.6f}")

    print()
    print(f"max |Ik error| = {max_ik:.6f}%")
    print(f"max |gain error| = {max_gain:.6f}%")

    # Provisional gate only. Full curve-family fitting will supersede it.
    if abs(pct(ia,DEVICE["ia_a"])) > 2.0:
        raise SystemExit("FAIL: device Ia outside provisional tolerance")
    if abs(pct(ig2,DEVICE["ig2_a"])) > 2.0:
        raise SystemExit("FAIL: device Ig2 outside provisional tolerance")
    if abs(pct(gm,DEVICE["gm_a_per_v"])) > 2.0:
        raise SystemExit("FAIL: device gm outside provisional tolerance")
    if max_ik > 5.0:
        raise SystemExit("FAIL: amplifier current sweep outside provisional tolerance")
    if max_gain > 3.0:
        raise SystemExit("FAIL: amplifier gain sweep outside provisional tolerance")

    print("PASS: provisional multi-anchor EF86 fit remains within frozen table/device tolerances.")
    print("WARNING: full Philips plate-curve validation is still required before promotion.")


if __name__ == "__main__":
    main()
