#!/usr/bin/env python3
"""Dynamic 12AX7 grid-current law sensitivity for SMX-3 V2 TRI0DE.

Plate/cathode current law is held at the current RSD-2 dynamic reference.
Only the grid-current law is varied between:
- Dempwolf RSD-1
- Dempwolf RSD-2
- Dempwolf EHX-1
- Danyuk polynomial overload fit

This isolates how grid conduction changes:
- peak grid current;
- positive-grid excursion;
- cathode/grid bias shift;
- post-overload recovery.

The Danyuk case is intentionally a HYBRID sensitivity probe, not a claimed
single measured tube model.
"""

import math
import smx3_v2_ecc83_dynamic_reference as dyn


PLATE = {
    "G":2.173e-3,
    "mu":95.29,
    "gamma":1.287,
    "C":3.324,
}

GRID = {
    "RSD-1":{"kind":"dempwolf","Gg":6.177e-4,"xi":1.314,"Cg":9.901,"Ig0":8.025e-8},
    "RSD-2":{"kind":"dempwolf","Gg":5.911e-4,"xi":1.358,"Cg":11.76,"Ig0":4.527e-8},
    "EHX-1":{"kind":"dempwolf","Gg":3.263e-4,"xi":1.156,"Cg":11.99,"Ig0":3.917e-8},
    "Danyuk-poly":{"kind":"danyuk"},
}


def softplus_scaled(x,c):
    z=c*x
    if z>50.0:
        return x
    if z<-50.0:
        return math.exp(z)/c
    return math.log1p(math.exp(z))/c


def grid_current(spec,vg):
    if spec["kind"]=="dempwolf":
        return spec["Gg"]*softplus_scaled(vg,spec["Cg"])**spec["xi"]+spec["Ig0"]
    # AES-137 practical overload fit.
    return 3.1e-4*max(vg+0.53,0.0)**3


def make_currents(spec):
    def currents(va,vg):
        ik=PLATE["G"]*softplus_scaled(va/PLATE["mu"]+vg,PLATE["C"])**PLATE["gamma"]
        ig=grid_current(spec,vg)
        ia=ik-ig
        return ia,ik,ig
    return currents


def run_case(name,spec,freq=1000.0,vin_rms=4.0,fs=384000.0,recovery_fs=96000.0):
    original=dyn.currents
    dyn.currents=make_currents(spec)

    try:
        x=dyn.solve_dc()
        dt=1.0/fs
        vin_peak=vin_rms*math.sqrt(2.0)

        # Establish driven periodic state for 0.4 s.
        warm_samples=int(round(0.4*fs))
        min_va=float("inf")
        max_vg=-float("inf")
        max_ig=0.0
        sum_vg=0.0
        sum_vk=0.0
        tail_count=0

        # Analyze only the last 50 ms of sustained drive.
        tail_start=warm_samples-int(round(0.05*fs))

        for n in range(warm_samples):
            x,_=dyn.trapezoid_step(n*dt,x,dt,vin_peak,freq)
            if n>=tail_start:
                va=x[dyn.P_NODE]-x[dyn.K]
                vg=x[dyn.G]-x[dyn.K]
                _,_,ig=dyn.currents(va,vg)
                min_va=min(min_va,va)
                max_vg=max(max_vg,vg)
                max_ig=max(max_ig,ig)
                sum_vg+=vg
                sum_vk+=x[dyn.K]
                tail_count+=1

        driven_avg_vg=sum_vg/tail_count
        driven_avg_vk=sum_vk/tail_count
        state_at_release=x[:]

        # Remove the signal and observe return toward the zero-input operating point.
        dc=dyn.solve_dc()
        recovery=[]
        checkpoints=(0.001,0.005,0.010,0.025,0.050,0.100,0.200,0.500,1.000,2.000)
        next_idx=0
        recovery_dt=1.0/recovery_fs
        total=int(round(checkpoints[-1]*recovery_fs))

        for n in range(total+1):
            if n>0:
                x,_=dyn.trapezoid_step(0.4+(n-1)*recovery_dt,x,recovery_dt,0.0,freq)

            t=n/recovery_fs
            while next_idx<len(checkpoints) and t>=checkpoints[next_idx]-0.5/fs:
                vg=x[dyn.G]-x[dyn.K]
                recovery.append((
                    checkpoints[next_idx],
                    vg,
                    x[dyn.K]-dc[dyn.K],
                    x[dyn.O]-dc[dyn.O],
                ))
                next_idx+=1

        # Scalar recovery time: first sample where cathode and grid are both
        # close to zero-input reference and stay checked only as a practical metric.
        x=state_at_release[:]
        recovery_ms=None
        limit=int(round(2.0*recovery_fs))
        for n in range(limit+1):
            if n>0:
                x,_=dyn.trapezoid_step(0.4+(n-1)*recovery_dt,x,recovery_dt,0.0,freq)
            vg_err=abs((x[dyn.G]-x[dyn.K])-(dc[dyn.G]-dc[dyn.K]))
            vk_err=abs(x[dyn.K]-dc[dyn.K])
            if vg_err<0.010 and vk_err<0.010:
                recovery_ms=1000.0*n/recovery_fs
                break

        return {
            "name":name,
            "min_va":min_va,
            "max_vg":max_vg,
            "max_ig":max_ig,
            "avg_vg":driven_avg_vg,
            "avg_vk":driven_avg_vk,
            "recovery_ms":recovery_ms,
            "recovery":recovery,
        }
    finally:
        dyn.currents=original


def main():
    print("SMX-3 V2 TRI0DE dynamic grid-current-law sensitivity")
    print("RSD-2 plate law fixed; 1 kHz / 4.0 Vrms sustained overload.")
    print()
    print("law,min_Va_V,max_Vg_V,max_Ig_uA,avg_Vg_V,avg_Vk_V,recovery_to_10mV_ms")

    results=[]
    for name,spec in GRID.items():
        r=run_case(name,spec)
        results.append(r)
        rec="nan" if r["recovery_ms"] is None else f"{r['recovery_ms']:.6f}"
        print(
            f"{name},{r['min_va']:.9f},{r['max_vg']:.9f},{r['max_ig']*1e6:.9f},"
            f"{r['avg_vg']:.9f},{r['avg_vk']:.9f},{rec}"
        )

    print()
    print("Recovery checkpoints: time_ms, grid-relative-V, cathode-error-V, output-error-V")
    for r in results:
        print(f"[{r['name']}]")
        for t,vg,vk,vo in r["recovery"]:
            print(f"{1000*t:.3f},{vg:.9f},{vk:.9f},{vo:.9f}")

    print()
    print("INFO: differences quantify grid-law sensitivity only; Danyuk is a hybrid cross-check, not a unified specimen model.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
