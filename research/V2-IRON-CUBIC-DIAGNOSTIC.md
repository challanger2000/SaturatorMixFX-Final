# SMX-3 V2 IRON Cubic Low-Level Diagnostic

Date: 2026-09-30
Status: PHYSICS-DERIVED diagnostic surrogate, NOT production model

## Exact Jensen anchors

At 20 Hz:
- +4 dBu -> typical THD = 0.025 %
- +20 dBu -> typical 1 % THD threshold

Input RMS:
- +4 dBu = 1.228292224 V RMS
- +20 dBu = 7.750000000 V RMS

Peak amplitudes:
- A4 = 1.737067522 V
- A20 = 10.960155108 V

## Odd-symmetric cubic diagnostic

Consider the local memoryless diagnostic law:

y = x + g*x^3

For x=A*sin(wt):

x^3 = A^3*(3*sin(wt)-sin(3wt))/4

so:

fundamental amplitude = A + 3*g*A^3/4
third-harmonic amplitude = g*A^3/4

Assuming H3 dominates low-level THD, the exact ratio is:

r = (g*A^2/4) / (1 + 3*g*A^2/4)

which gives:

g = 4*r / (A^2*(1-3*r))

Using the two independent Jensen tabular anchors:

From +4 dBu / 0.025 %:
- g ~= 3.3166e-4 V^-2

From +20 dBu / 1 %:
- g ~= 3.4329e-4 V^-2

Difference:
- approximately 3.5 %

## Interpretation

Two widely separated manufacturer anchors are therefore consistent with nearly the same simple odd-symmetric cubic curvature.

This strongly supports the earlier conclusion that:
- low/mid-level JT-11P-1 distortion is compatible with predominantly odd-symmetric magnetic curvature;
- the leading relative distortion term grows approximately with input amplitude squared;
- the rejected DAFx-example Jiles-Atherton loop opened too strongly at low level after simple scaling.

This does NOT prove that the real transformer is memoryless or exactly cubic.

The cubic law is only a diagnostic baseline. A final model must additionally reproduce:
- hysteresis and minor-loop behavior;
- frequency dependence;
- remanence/state;
- saturation transition;
- source/load interaction;
- measured linear bandwidth and phase.

## Practical fitting use

During magnetic-parameter fitting, compare the local 20 Hz H3-vs-level slope to this cubic diagnostic.

A candidate that:
- matches +20 dBu / 1 %,
- but needs a radically different effective low-level cubic curvature,
must explain that difference through measured hysteresis/frequency behavior rather than arbitrary compensation.

Evidence classification:
- Jensen anchors: DOCUMENTED
- cubic derivation: PHYSICS DERIVED
- coefficient values: PUBLISHED-PARAMETER DERIVED from those anchors
