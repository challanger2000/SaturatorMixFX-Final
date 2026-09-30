#!/usr/bin/env python3
"""Dynamic EHX-1 vs RSD-2 12AX7 specimen comparison for SMX-3 V2 TRI0DE.

Both published Dempwolf/Zoelzer measured-tube parameter sets are embedded in
the exact same documented Philips/Mullard ECC83 dynamic network.

Purpose:
resolve the historical mismatch where static manufacturer cross-checks favor
RSD-2 while the dynamic reference still uses EHX-1.

No production DSP changes.
"""

import math
import smx3_v2_ecc83_dynamic_reference as dyn

SETS={
    "EHX-1":{
        "G":1.371e-3,"mu":86.9,"gamma":1.349,"C":4.56,
        "Gg":3.263e-4,"xi":1.156,"Cg":11.99,"Ig0":3.917e-8,
    },
    "RSD-2":{
        "G":2.173e-3,"mu":100.2,"gamma":1.28,"C":3.19,
        "Gg":5.911e-4,"xi":1.358,"Cg":11.76,"Ig0":4.527e-8,
    },
}

CASES=[
    (20.0,0.010),
    (1000.0,0.010),
    (1000.0,0.500),
    (1000.0,0.700),
    (10000.0,0.010),
    (20000.0,0.010),
]


def set_params(p):
    dyn.P.clear()
    dyn.P.update(p)


def dc_summary():
    x=dyn.solve_dc()
    vg,vp,vk,vo=x
    ik,ia,ig=dyn.currents(vp-vk,-vk)
    return {
        "vp":vp,"vk":vk,"va":vp-vk,
        "ik":ik,"ia":ia,"ig":ig,
    }


def main():
    original=dict(dyn.P)
    results={}

    try:
        for name,p in SETS.items():
            set_params(p)
            dc=dc_summary()
            print(f"[{name}]")
            print(
                f"DC Ik={dc['ik']*1e3:.9f}mA "
                f"Vp={dc['vp']:.9f}V Vk={dc['vk']:.9f}V "
                f"Va={dc['va']:.9f}V Ig={dc['ig']*1e6:.9f}uA"
            )
            print("freq_Hz,Vin_rms,gain,phase_deg,THD_pct,max_Newton")
            rr={}
            for freq,vin in CASES:
                r=dyn.simulate(freq,vin,cycles=8,warmup_seconds=0.4)
                rr[(freq,vin)]=r
                print(
                    f"{freq:.1f},{vin:.6f},{r['gain']:.9f},"
                    f"{r['phase_deg']:.9f},{100*r['thd']:.9f},{r['max_newton']}"
                )
            results[name]=(dc,rr)
            print()

        print("RSD-2 / EHX-1 comparison")
        print("freq_Hz,Vin_rms,gain_ratio_dB,THD_RSD2_pct,THD_EHX1_pct")
        for freq,vin in CASES:
            a=results["EHX-1"][1][(freq,vin)]
            b=results["RSD-2"][1][(freq,vin)]
            gd=20.0*math.log10(b["gain"]/a["gain"])
            print(
                f"{freq:.1f},{vin:.6f},{gd:+.6f},"
                f"{100*b['thd']:.9f},{100*a['thd']:.9f}"
            )

        print()
        print("INTERPRETATION GATE:")
        print("- static manufacturer-loaded comparison is evaluated separately;")
        print("- this tool checks dynamic stability, frequency behavior and nonlinear progression;")
        print("- no specimen is selected solely because it has lower THD or higher gain.")

    finally:
        set_params(original)

    return 0


if __name__=="__main__":
    raise SystemExit(main())
