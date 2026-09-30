# SMX-3 V2 IRON Low-Level Symmetry Constraint

Date: 2026-09-30

## Observation from exact Jensen anchors

At 20 Hz:
- +4 dBu -> 0.025 % typical THD
- +20 dBu -> 1 % THD typical threshold

The implied THD growth exponent over that interval is approximately 2.003 with respect to input voltage amplitude.

## Physical interpretation

For a transformer operated without DC bias and with a reasonably symmetric magnetic path, the low-level constitutive relation around the origin should be approximately odd-symmetric:

M(-H) = -M(H)

An analytic local expansion therefore has no dominant even powers:

M(H) ~= chi1*H + chi3*H^3 + chi5*H^5 + ...

For sinusoidal field

H = A*sin(wt)

the leading cubic term produces

H^3 = A^3 * (3*sin(wt) - sin(3wt)) / 4.

Therefore:
- fundamental contribution scales approximately with A;
- third-harmonic contribution from the cubic term scales with A^3;
- H3/fundamental scales approximately with A^2.

Thus an approximately quadratic THD-vs-amplitude law is physically consistent with a low-level, odd-symmetric transformer nonlinearity dominated by cubic curvature.

Evidence class:
PHYSICS DERIVED, using the exact Jensen level/THD anchors as the observed constraint.

## Consequence for hysteresis modeling

The rejected DAFx-example Jiles-Atherton shape showed approximately linear THD growth over the same level interval.

That implies its low-level irreversible/hysteretic contribution is too strong for the JT-11P-1 target after simple geometry scaling.

A successful IRON model should therefore:
- preserve near odd symmetry at zero DC bias;
- keep low-level irreversible loop opening small enough that cubic/reversible curvature can dominate the measured THD growth;
- allow hysteresis/remanence to become more important as excitation rises;
- introduce even harmonics primarily when an intentional asymmetry/DC-bias state exists, not by default.

## Rayleigh/minor-loop note

Rayleigh-type low-field magnetization remains relevant to minor-loop loss and remanence, but it must not be inserted merely because it is a recognized low-field law.

The Jensen harmonic-growth evidence constrains how much such irreversible low-field behavior may contribute.

Any Rayleigh/modified-JA/Preisach component must be measured against:
- the ~A^2 THD growth constraint;
- odd/even harmonic balance at zero DC;
- the 20/30/50 Hz level curves;
- remanence/reset behavior.

## Realtime architecture implication

A promising structure to test is:

linear transformer skeleton
+ weak symmetric low-level cubic magnetic curvature
+ stateful hysteresis term whose contribution grows with excitation
+ saturation transition
+ physical source/load/parasitic network

This is a research architecture candidate, not a predetermined production implementation.

Every term must be traceable to measured behavior; no arbitrary 'warmth' term is permitted.
