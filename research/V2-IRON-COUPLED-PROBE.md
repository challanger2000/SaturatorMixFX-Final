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


## Harmonic-parity follow-up

The same rejected example-shape model was decomposed into individual harmonics at 20 Hz.

### +4 dBu
- THD ≈ 0.15344 %
- H2 ≈ 0.01341 %
- H3 ≈ 0.15154 %
- H5 ≈ 0.01620 %
- H2/H3 ≈ -21.06 dB

### +14 dBu
- THD ≈ 0.41736 %
- H2 ≈ 0.02557 %
- H3 ≈ 0.41524 %
- H5 ≈ 0.01518 %
- H2/H3 ≈ -24.21 dB

### +20 dBu
- THD ≈ 0.99703 %
- H2 ≈ 0.02294 %
- H3 ≈ 0.98279 %
- H5 ≈ 0.16254 %
- H2/H3 ≈ -32.64 dB

## Revised interpretation

This refines the rejection.

The example Jiles-Atherton shape is NOT wrong in every respect.

It gets one important transformer property qualitatively right:
- zero-bias distortion is strongly H3-dominant;
- even-order distortion remains substantially below H3.

That is consistent with Jensen/Whitlock's engineering description of an un-magnetized transformer core.

The principal mismatch is instead:
- excessive low-level nonlinear/hysteretic contribution;
- incorrect THD-growth law between +4 and +20 dBu.

Therefore the next magnetic fit should preferentially alter:
- low-field irreversible-loop opening;
- reversible/anhysteretic balance;
- field scaling / saturation-transition shape;

while preserving:
- approximate odd symmetry;
- H3 dominance;
- stateful magnetic memory.

Do NOT discard Jiles-Atherton merely because the published example parameter set fails the JT-11P-1 amplitude law.


## Settled magnetic-cycle correction — 2026-09-30

The earlier harmonic-parity follow-up analyzed the Jiles-Atherton response before the magnetic state had fully reached a periodic orbit.

That especially contaminated H2.

The coupled probe now performs 40 complete magnetic warm-up cycles before analyzing the final four cycles.

With the original rejected DAFx example parameter shape and the same high-level scaling, the settled-state results are approximately:

### +4 dBu / 20 Hz
- THD ≈ 0.1584 %
- H3 ≈ 0.1573 %
- H5 ≈ 0.0150 %
- H2 becomes effectively negligible
- H2/H3 falls to roughly -99 dB

### +14 dBu / 20 Hz
- THD ≈ 0.4218 %
- H3 ≈ 0.4205 %
- H2 effectively negligible

### +20 dBu / 20 Hz
- THD ≈ 0.9971 %
- H3 ≈ 0.9830 %
- H5 ≈ 0.1645 %
- H2 effectively negligible

## Revised conclusion

The earlier reported finite H2 in the 12-cycle run was primarily magnetic startup/remanence settling, not the stationary symmetric distortion of the model.

This strengthens, rather than weakens, the Jensen/Whitlock consistency:

- the un-biased settled model is overwhelmingly odd-symmetric;
- H3 dominates;
- even harmonics collapse after the periodic orbit is reached.

The model is still rejected as a JT-11P-1 amplitude-law fit because:
- +4 dBu / 20 Hz remains about 0.158 % THD instead of ~0.025 %;
- +20 dBu / 20 Hz remains close to the fitted ~1 % point.

Therefore the remaining problem is specifically the low-field nonlinear/hysteretic strength, not harmonic parity.

Future IRON fitting must measure only after magnetic periodic-state convergence or after an explicitly defined demagnetization/state protocol.
