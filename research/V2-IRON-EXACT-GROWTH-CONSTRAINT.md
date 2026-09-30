# SMX-3 V2 IRON Exact Nonlinearity-Growth Constraint

Date: 2026-09-30
Source: Jensen JT-11P-1 manufacturer specification table.

## Exact anchors

At 20 Hz, Rs=600 Ohm, test circuit 1:

- +4 dBu -> typical THD = 0.025 %
- +20 dBu -> typical input level for 1 % THD = +20 dBu

These two anchors are tabulated manufacturer values, not graph digitization.

## Derived level ratio

The RMS voltage ratio between +4 and +20 dBu is:

A2/A1 = 10^((20-4)/20)
      = 6.3095734448

THD ratio:

THD2/THD1 = 1.0 / 0.025
          = 40

If local distortion growth is represented over this interval by

THD proportional to A^p,

then

p = ln(40) / ln(6.3095734448)
  = 2.002574989

Therefore the Jensen reference exhibits approximately quadratic THD growth with input voltage over the +4 to +20 dBu / 20 Hz interval.

Evidence class:
PUBLISHED-PARAMETER DERIVED.

## Why this matters

This is a strong shape constraint and is more reliable than manually reading intermediate graph points.

A magnetic model that is scaled to hit only the +20 dBu / 1 % point but has roughly linear THD growth versus amplitude will necessarily over-predict low-level distortion.

## Comparison with rejected DAFx example-shape probe

The previous coupled probe produced approximately:
- +4 dBu / 20 Hz: 0.153 % THD
- +20 dBu / 20 Hz: 0.997 % THD

Its implied growth exponent is approximately:

p_example = ln(0.997/0.153) / ln(6.3095734448)
          ~ 1.02

That is fundamentally different from the Jensen-derived ~2.00 exponent.

This mathematically explains the earlier rejection:
the issue is not merely gain/geometry scaling; the nonlinear growth law of the example magnetic loop is wrong for the target transformer over the relevant level range.

## Fit requirement

Any promoted IRON reference candidate must satisfy all of:

1. +4 dBu / 20 Hz THD near 0.025 %;
2. +20 dBu / 20 Hz THD near 1 %;
3. implied 20 Hz level-growth exponent consistent with approximately 2 over that interval;
4. frequency-dependent saturation behavior from the multi-frequency Jensen evidence;
5. low-level linear gain/impedance anchors already established.

Do not optimize the model to the exponent alone. It is a compact diagnostic derived from two exact anchors, not a substitute for the full curve family.
