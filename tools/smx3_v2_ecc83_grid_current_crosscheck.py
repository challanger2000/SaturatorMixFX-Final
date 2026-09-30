#!/usr/bin/env python3
"""12AX7 grid-current cross-check for SMX-3 V2 TRI0DE.

Compares:
- Dempwolf/Zoelzer fitted practical specimens RSD-1, RSD-2, EHX-1;
- Danyuk AES-137 measured-grid-current fit in the overload region.

This is an INFORMATIONAL specimen/circuit-variation check. It does not select
a production grid-current law by itself.
"""

import math

SETS={
    "RSD-1":{"Gg":6.177e-4,"xi":1.314,"Cg":9.901,"Ig0":8.025e-8},
    "RSD-2":{"Gg":5.911e-4,"xi":1.358,"Cg":11.76,"Ig0":4.527e-8},
    "EHX-1":{"Gg":3.263e-4,"xi":1.156,"Cg":11.99,"Ig0":3.917e-8},
}


def softplus(v,c):
    z=c*v
    if z>50.0:return v
    if z<-50.0:return math.exp(z)/c
    return math.log1p(math.exp(z))/c


def dempwolf(p,vg):
    return p["Gg"]*softplus(vg,p["Cg"])**p["xi"]+p["Ig0"]


def danyuk_poly(vg):
    # AES-137 fit quoted for the practical region around -0.3..+0.3 V.
    return 3.1e-4*max(vg+0.53,0.0)**3


def danyuk_exp(vg):
    # Alternate exponential fit reported for the same measured data region.
    return 4.0e-5*math.exp(5.7*vg)


def main():
    points=(-0.3,-0.2,-0.1,0.0,0.1,0.2,0.3)

    print("SMX-3 V2 12AX7 grid-current cross-check")
    print("Vg_V,RSD1_uA,RSD2_uA,EHX1_uA,Danyuk_poly_uA,Danyuk_exp_uA")

    for vg in points:
        vals=[1e6*dempwolf(SETS[name],vg) for name in ("RSD-1","RSD-2","EHX-1")]
        print(
            f"{vg:+.3f},{vals[0]:.6f},{vals[1]:.6f},{vals[2]:.6f},"
            f"{1e6*danyuk_poly(vg):.6f},{1e6*danyuk_exp(vg):.6f}"
        )

    print()
    print("At +0.3 V:")
    for name,p in SETS.items():
        print(f"  {name}: {1e6*dempwolf(p,0.3):.3f} uA")
    print(f"  Danyuk polynomial fit: {1e6*danyuk_poly(0.3):.3f} uA")
    print(f"  Danyuk exponential fit: {1e6*danyuk_exp(0.3):.3f} uA")

    print()
    print("INFO: positive-grid current varies materially between measured specimens/sources.")
    print("INFO: product grid-current law must be chosen/fitted as an archetype, not treated as an exact universal 12AX7 constant.")


if __name__=="__main__":
    main()
