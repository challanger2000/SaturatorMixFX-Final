#!/usr/bin/env python3
"""Time-domain small-signal transfer gate for the frozen unified IRON candidate.

Verifies that the actual nonlinear JA + relaxation state converges, at +4 dBu,
to the linearized magnetic transfer implied by the same frozen LSTAT/GREL/TAU.

HF leakage/capacitance is intentionally excluded here; this gate validates the
magnetic dynamic architecture before the separate HF network is integrated.
"""

import cmath
import math

import smx3_v2_iron_unified_candidate as iron
from smx3_v2_dlp_utils import dlp_degrees

FREQS=(20.0,30.0,50.0,100.0,200.0,500.0,1000.0,2000.0,5000.0,10000.0,20000.0)


def linear_transfer(freq):
    s=1j*2.0*math.pi*freq
    rseries=iron.RSOURCE+iron.RP
    ymag=1.0/(s*iron.LSTAT)+iron.GREL/(1.0+s*iron.TAU)
    yload=1.0/iron.RLOAD
    vnode=(1.0/rseries)/(1.0/rseries+ymag+yload)
    return vnode*iron.RL/iron.RLOAD


def simulate_transfer(freq):
    fs=max(48000.0,96.0*freq)
    cycles=6
    r=iron.simulate(4.0,freq=freq,fs=fs,warmup_cycles=120,analysis_cycles=cycles)

    vrms=0.775*10.0**(4.0/20.0)
    amp=vrms*math.sqrt(2.0)
    in_phasor=complex(0.0,-0.5*amp)

    n=int(round(cycles*fs/freq))
    out_phasor=(2.0/n)*r["fundamental"]
    return out_phasor/in_phasor


def db(z):
    return 20.0*math.log10(abs(z))


def main():
    td=[]
    lin=[]

    print("SMX-3 V2 unified IRON time-domain magnetic transfer cross-check")
    print("freq_Hz,TD_mag_dB,LIN_mag_dB,mag_residual_dB,TD_phase_deg,LIN_phase_deg,phase_residual_deg")

    for f in FREQS:
        ht=simulate_transfer(f)
        hl=linear_transfer(f)
        td.append(ht)
        lin.append(hl)

        phase_res=math.degrees(cmath.phase(ht/hl))
        print(
            f"{f:.1f},{db(ht):.9f},{db(hl):.9f},{db(ht)-db(hl):+.9f},"
            f"{math.degrees(cmath.phase(ht)):+.9f},"
            f"{math.degrees(cmath.phase(hl)):+.9f},{phase_res:+.9f}"
        )

    td_ref=db(td[FREQS.index(1000.0)])
    lin_ref=db(lin[FREQS.index(1000.0)])
    td_rel20=db(td[0])-td_ref
    lin_rel20=db(lin[0])-lin_ref

    td_dlp=dlp_degrees(FREQS,[cmath.phase(z) for z in td])
    lin_dlp=dlp_degrees(FREQS,[cmath.phase(z) for z in lin])

    max_mag=max(abs(db(a)-db(b)) for a,b in zip(td,lin))
    max_phase=max(abs(math.degrees(cmath.phase(a/b))) for a,b in zip(td,lin))

    print()
    print(f"TD rel20={td_rel20:+.9f} dB")
    print(f"LIN rel20={lin_rel20:+.9f} dB")
    print(f"TD DLP worst={td_dlp['worst_abs_deg']:.9f} deg")
    print(f"LIN DLP worst={lin_dlp['worst_abs_deg']:.9f} deg")
    print(f"max magnitude residual={max_mag:.9f} dB")
    print(f"max phase residual={max_phase:.9f} deg")

    failures=[]
    if max_mag>0.01:
        failures.append("time-domain magnitude does not converge to frozen linearized magnetic model")
    if max_phase>0.10:
        failures.append("time-domain phase does not converge to frozen linearized magnetic model")
    if abs(td_rel20-lin_rel20)>0.01:
        failures.append("20 Hz relative magnitude residual")
    if abs(td_dlp["worst_abs_deg"]-lin_dlp["worst_abs_deg"])>0.10:
        failures.append("DLP residual versus frozen linearized magnetic model")

    if failures:
        print("FAIL:")
        for item in failures:
            print(" - "+item)
        return 1

    print("PASS: full nonlinear unified IRON converges to its frozen small-signal magnetic transfer in time domain.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
