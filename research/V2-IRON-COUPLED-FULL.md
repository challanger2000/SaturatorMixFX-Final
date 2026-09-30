# SMX-3 V2 Coupled IRON Magnetic + Parasitic Reference

Date: 2026-09-30
Status: first full offline topology candidate

## Why this model exists

The magnetic candidate and the HF parasitic fit were previously validated as
separate subsystems.

That is insufficient for final reference work because:
- HF parasitics alter winding voltage;
- winding voltage drives magnetic flux;
- magnetic current loads the primary node;
- therefore magnitude, phase and nonlinear behavior are coupled.

## State topology

States:
- H
- M
- primary node voltage Vp
- leakage current Ilk
- secondary node voltage Vsec

Documented / derived values:
- Rs=600 Ohm for Jensen response/THD test conditions
- Rp=1.45 kOhm
- Rsec=1.55 kOhm
- RL=10 kOhm
- corrected Lm target ~143.999 H
- Cp=98 pF
- Cs=110 pF

Current provisional fitted HF values:
- Llk ~2.75665 mH
- effective Cx ~1.15504 nF

Current provisional magnetic values:
- Jiles-Atherton family
- c ~0.820
- KI ~40528.8 A/m per A
- KPHI derived from corrected Lm

## Equations

Magnetic branch:
- Im = H / KI
- Vp = KPHI * (dH/dt + dM/dt)
- dM/dt = (dM/dH) * dH/dt

Primary KCL:
(Vin - Vp)/(Rs+Rp) = Im + Ilk + Cp*dVp/dt

Leakage:
Llk*dIlk/dt = Vp - Vsec

Secondary:
Ilk = Vsec/(Rsec+RL) + (Cs+Cx)*dVsec/dt

Output:
Vout = Vsec * RL/(Rsec+RL)

## First acceptance gates

The coupled model must preserve simultaneously:
- ~-0.04 dB at 20 Hz / 1 kHz;
- ~-0.05 dB at 20 kHz / 1 kHz;
- ~-3 dB near 95 kHz;
- ~0.025% THD at +4 dBu / 20 Hz;
- ~1% THD at +20 dBu / 20 Hz.

This is deliberately stronger than validating magnetic and electrical
subsystems independently.

## Still blocked

Before promotion:
- numerical method convergence of the coupled five-state solver;
- DLP/phase comparison;
- source/load variation;
- state reset/recall;
- realtime reduction;
- aliasing/CPU.

No production DSP is derived yet.
