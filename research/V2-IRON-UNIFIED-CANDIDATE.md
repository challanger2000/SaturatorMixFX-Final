# SMX-3 V2 IRON Unified Relaxation Candidate — Frozen Offline Reference

Date: 2026-09-30
Workflow run: 36716019117
Status: OFFLINE CANDIDATE ACCEPTED FOR REGRESSION

## Architecture

States:
- H: magnetic field state
- M: Jiles-Atherton magnetization state
- i_relax: one causal magnetic relaxation-current state

Equations:

i_mag = H/KI + i_relax

tau * d(i_relax)/dt + i_relax = Grel * v_core

The new state tends to zero when core voltage tends to zero.
Therefore quasi-static hysteresis/remanence remain in the JA H/M states.

## Frozen candidate values

Quasi-static JA:
- a = 14.1
- alpha = 5e-5
- k = 17.8
- Ms = 2.75e5
- c = 0.535351563
- KI = 1087366.676330566 A/m per A
- KPHI = 2.85816455767e-7

Relaxation:
- Lstat = 1309.871357869 H
- Grel = 2.73374681419e-6 S
- tau = 1.440238371 ms

## Fully settled high-resolution result

120 complete 20 Hz warm-up cycles were used before analysis.

- +4 dBu / 20 Hz THD = 0.025001495%
- +20 dBu / 20 Hz THD = 1.000139520%
- +4 dBu H2 = 0.000994758%
- +4 dBu H3 = 0.024901682%
- +4 dBu H5 = 0.000479575%
- +20 dBu H3 = 0.869483202%

The unbiased low-level state remains strongly H3-dominant.

## Why this is materially stronger than the previous candidate

The previous quasi-static candidate could match Jensen THD and remanence but
failed Jensen DLP.

The one-state relaxation architecture independently passes the selected Jensen
small-signal:
- 20 Hz response
- 20 kHz response
- ~95 kHz bandwidth
- 1 kHz gain/input impedance
- DLP

and the unified nonlinear fit now recovers the exact low/high 20 Hz THD anchors.

## Next mandatory gates

Before production promotion:
1. DC-bias/remanence regression
2. relaxation-state decay to zero
3. independent numerical-method cross-check
4. time-domain low-level phase/magnitude
5. integrate HF leakage/capacitance network
6. host-rate/realtime reduction
7. aliasing/CPU/stability

No production C++ is frozen yet.
