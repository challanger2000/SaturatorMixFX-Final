# SMX-3 V2 Coupled IRON Probe — Jiles-Atherton Example Shape

Date: 2026-09-30
Status: REJECTED AS JENSEN FIT; useful solver architecture retained

## Model

Electrical side:
- source resistance 600 Ohm
- Jensen documented primary DCR 1.45 kOhm
- 1:1 ideal turns coupling
- Jensen documented secondary DCR 1.55 kOhm
- load 10 kOhm
- derived low-level effective magnetizing inductance ≈106.554 H

Magnetic side:
- Jiles-Atherton state equation
- DAFx-2016 example SHAPE parameters:
  - a=14.1
  - alpha=5e-5
  - c=0.55
  - k=17.8
  - Ms=2.75e5

Unknown core geometry is reduced to two combined scaling factors:
- H = KI * i_m
- lambda = KPHI * (H+M)

KPHI is not free once KI is selected because small-signal Lm is constrained:

Lm = KPHI * KI * (1 + dM/dH at the origin)

This avoids inventing turns N, core area A and magnetic path length separately when the available manufacturer data do not identify them independently.

## High-level calibration experiment

KI was adjusted to approximately 41431 A/m per A so that the coupled model lands close to Jensen's documented typical:

20 Hz / +20 dBu -> 1 % THD

At high-resolution simulation the model gives approximately:
- +20 dBu / 20 Hz: 0.997 % THD

So a single high-level anchor can be reproduced by geometry/field scaling.

## Critical cross-check

Without changing any other parameter:

- Jensen +4 dBu / 20 Hz target: approximately 0.025 % THD
- scaled example Jiles-Atherton model: approximately 0.153 % THD

The model therefore produces about six times too much low-level distortion while matching the high-level 1 % point.

Approximate +20 dBu frequency results:
- 20 Hz: 0.997 %
- 30 Hz: 0.393 %
- 50 Hz: 0.145 %
- 100 Hz: 0.041 %
- 1 kHz: 0.0017 %

The qualitative frequency trend is physically correct, but the nonlinear curve shape is not yet Jensen-like.

## Decision

REJECT the unmodified DAFx example Jiles-Atherton parameter SHAPE as the SMX-3 IRON hardware fit.

Retain:
- coupled electrical/magnetic architecture;
- H/M state formulation;
- composite geometry parameterization;
- low-level Lm constraint;
- manufacturer multi-point fitting strategy.

Next fit must vary magnetic shape parameters (a, alpha, c, k, Ms or an identifiable reduced set), not merely KI/KPHI.

Acceptance requires simultaneous agreement with:
- +4 dBu / 20 Hz ~0.025 % THD;
- +20 dBu / 20 Hz ~1 % THD;
- Jensen THD-vs-level curves at 20/30/50 Hz;
- Jensen THD-vs-frequency curves at +4/+14/+20 dBu;
- already established low-level gain/impedance/frequency anchors.

This is a useful failed model: it proves that 'Jiles-Atherton' by itself is not enough; the actual magnetic loop shape must be identified from the hardware evidence.
