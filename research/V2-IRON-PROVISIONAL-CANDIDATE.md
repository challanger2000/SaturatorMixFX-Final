# SMX-3 V2 Provisional IRON Magnetic Candidate

Date: 2026-09-30
Status: STRONG PROVISIONAL OFFLINE CANDIDATE — not yet final production DSP

## Starting point

The original DAFx Jiles-Atherton example shape, after geometry/field scaling to Jensen's exact +20 dBu / 20 Hz / 1% THD point, produced too much low-level distortion:

- +4 dBu / 20 Hz: ~0.158%
- Jensen typical: ~0.025%

Its settled harmonic parity was nevertheless physically plausible:
- H3 dominant;
- H2 effectively negligible in the demagnetized periodic state.

Therefore the model family was retained and the low-field loop shape was targeted instead of replacing the architecture.

## Reduced shape experiment

Keep:
- a = 14.1
- alpha = 5e-5
- k = 17.8
- Ms = 2.75e5

Change:
- reversible fraction c: 0.55 -> approximately 0.84

Then re-scale the field/current geometry factor so the coupled electrical/magnetic model again lands on the exact +20 dBu / 20 Hz anchor.

Candidate:
- c = 0.84
- KI ≈ 26174.316 A/m per A
- KPHI derived from the already constrained ~106.554 H low-level magnetizing inductance.

Evidence class:
EMPIRICALLY TUNED TO DOCUMENTED MEASUREMENTS.

These are effective model parameters, not claimed Jensen core-material constants.

## High-resolution settled results

Using:
- 48 kHz integration for the 20 Hz reference;
- 30 complete magnetic warm-up cycles;
- four analysis cycles;

the candidate gives approximately:

- +4 dBu / 20 Hz: **0.0255% THD**
- +20 dBu / 20 Hz: **1.0000% THD**

Manufacturer typical anchors:
- +4 dBu / 20 Hz: ~0.025%
- +20 dBu / 20 Hz: ~1.0%

The two exact anchors are therefore simultaneously reproduced without a separate low-level waveshaper or amplitude-dependent correction.

## Intermediate level

At +14 dBu / 20 Hz the candidate predicts approximately:
- 0.193% THD.

The current graph-derived +14 dBu points in the repository are explicitly provisional and internally inconsistent between the two Jensen plots, so this value is NOT yet scored as pass/fail.

Do not tune away from exact manufacturer anchors to chase uncertain graph reads.

## Frequency trend at +20 dBu

Current candidate approximately:
- 20 Hz: 1.000%
- 30 Hz: 0.251%
- 50 Hz: 0.0483%
- 100 Hz: 0.00650%
- 1 kHz: 0.000492%

The qualitative volt-second trend is physically correct and very steep.

Before promotion:
- calibrated Jensen graph extraction must determine whether this frequency slope is quantitatively correct;
- HF parasitic/network behavior must be added independently from magnetic fitting.

## Why c matters here

Increasing c moves more of the magnetization response into the reversible component.

In this candidate it:
- substantially reduces low-field hysteretic distortion;
- preserves strong nonlinear growth toward the high-level anchor;
- retains stateful magnetic behavior;
- retains settled odd/H3-dominant symmetry.

This is exactly the deficiency identified in the rejected c=0.55 example shape.

## Current decision

PROMOTE from "rejected example shape" to:
**STRONG PROVISIONAL IRON OFFLINE CANDIDATE**

Hard evidence passed:
- documented electrical skeleton;
- low-level effective magnetizing inductance constraint;
- exact +4 dBu / 20 Hz THD anchor;
- exact +20 dBu / 20 Hz / 1% THD anchor;
- Jensen/Whitlock H3-dominant demagnetized parity.

Still blocking final promotion:
1. calibrated Jensen THD graph extraction;
2. multi-frequency / multi-level residual;
3. phase/HF parasitic network;
4. DC-bias/remanence validation;
5. independent numerical integration cross-check;
6. realtime reduction;
7. aliasing and CPU QA.

No production DSP should yet be derived from these numbers without those gates.
