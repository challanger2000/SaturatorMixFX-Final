# SMX-3 V2 IRON One-State Magnetic Relaxation

Date: 2026-09-30
Status: small-signal architecture test

## Architecture

Retain static JA as equilibrium hysteresis.

Add one dynamic field state:

tau * dHloss/dt + Hloss = K * dB/dt

At dB/dt -> 0:
Hloss -> 0.

Therefore:
- static JA loop remains the equilibrium loop;
- remanence/coercivity remain rate-independent in the static limit;
- the new state contributes only dynamic complex permeability/loss.

Linearized magnetic admittance:

Ymag =
1/(s Lstat)
+
Gloss/(1+s tau)

This is a pure static inductive equilibrium branch plus one relaxing loss branch.

## Why this differs from failed Classical-only architecture

Classical-only:
Ymag = 1/(sL) + constant G.

That architecture could match DLP OR 20 Hz attenuation, but not both.

Relaxation:
G/(1+s tau)

allows dynamic loss contribution to decay with frequency and introduces one
additional physical timescale.

## Fit domains

Fixed documented:
- source Rs=600 Ohm in response/DLP test;
- winding DCR;
- 10k load;
- 98pF / 110pF shield capacitances.

Fitted effective:
- static low-field inductance scale;
- relaxation strength;
- relaxation time constant;
- leakage inductance;
- effective additional HF capacitance.

Targets:
- 1k gain;
- 1k input impedance;
- 20Hz response;
- 20k response;
- ~95k bandwidth;
- Jensen DLP.

No fitted value is claimed as a Jensen construction/material constant.

## Promotion sequence

If the one-state small-signal architecture passes:
1. embed its Hloss state around the nonlinear JA equilibrium law;
2. re-fit only the minimum low-field scale/dynamic coefficients;
3. verify +4/+20 dBu THD;
4. verify H3 baseline;
5. verify DC-bias/remanence;
6. verify numerical method and realtime reduction;
7. verify DLP/magnitude simultaneously.

Only then can the unified IRON offline model be considered closed.
