# SMX-3 V2 PENTODE Reference Architecture Decision

Date: 2026-09-30

## Problem established by measurement

The current compact Koren-form EF86 candidate performs very well on:
- device operating point;
- screen current anchor;
- transconductance anchor;
- amplifier DC current over Vb=200..400 V;
- amplifier small-signal gain over Vb=200..400 V;
- coarse out-of-fit Philips plate-curve points.

However it fails the exact Philips large-signal amplifier anchor:
- manufacturer: about 50 Vrms output at 5% total distortion;
- current candidate: about 36.76 Vrms at 5% THD.

Therefore a compact equation can look excellent under static/small-signal validation and still have the wrong large-signal curvature.

## V2 decision: maintain two reference paths

### Path A — compact analytic candidate

Purpose:
- potential realtime production model;
- low CPU;
- differentiable/solver-friendly behavior.

Requirement:
it must eventually match all required data classes simultaneously.

Do not preserve the current equation family merely for convenience if it cannot satisfy large-signal evidence.

### Path B — manufacturer-data current-surface reference

Build an offline EF86 current reference from Philips data:

Ia = f(Va, Vg1, Vg2)

and, where evidence supports it:

Ig2 = g(Va, Vg1, Vg2)

Inputs:
- Philips plate-current family at Vg2=140 V;
- Philips control-grid transfer families at several Vg2 values;
- device-point Ia/Ig2/gm anchors;
- amplifier operating tables;
- large-signal amplifier graph.

The reference surface is allowed to use interpolation because its purpose is measurement authority, not production efficiency.

## Why the current-surface reference matters

It gives a model-independent answer to:

'What would the documented EF86 characteristic data predict along this circuit load trajectory?'

That lets us distinguish errors caused by:
- an inadequate compact equation;
- circuit assumptions;
- curve digitization;
- realtime discretization.

## Interpolation rules

The offline surface must:
- preserve nonnegative current;
- remain monotonic where manufacturer data are monotonic;
- avoid spline overshoot near cutoff/knee;
- record extrapolation explicitly;
- never silently extrapolate far outside documented voltage ranges;
- carry digitization uncertainty into comparison tolerances.

Candidate interpolation:
- monotone piecewise cubic along densely sampled 1-D slices where appropriate;
- bilinear/bicubic only when it does not create unphysical overshoot;
- triangulated or regular-grid interpolation after calibrated digitization.

## Production rule

The final realtime PENTODE may be:
- a compact equation;
- a reduced surrogate of the current surface;
- a small LUT/interpolator;
- a hybrid circuit-derived model.

Choice is decided by:
1. error against the offline manufacturer-data reference;
2. large-signal harmonic accuracy;
3. stability;
4. CPU p95/p99/max;
5. aliasing behavior.

No architectural preference outranks measured agreement.

## Immediate gates

1. Densify Philips plate-curve digitization in the low-Va knee.
2. Digitize the Vg2-dependent transfer curves.
3. Digitize circuit-1 Vi/Vo/distortion graph.
4. Construct offline current surface.
5. Re-run the selected 250 V circuit through that surface.
6. Compare:
   - manufacturer graph;
   - current-surface result;
   - compact analytic candidate.

Only then decide whether the compact equation is salvageable or structurally inadequate.
