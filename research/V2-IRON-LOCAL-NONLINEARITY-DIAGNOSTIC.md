# SMX-3 V2 IRON Local Nonlinearity Diagnostic

Date: 2026-09-30

## Exact Jensen anchors

At 20 Hz:
- +4 dBu -> approximately 0.025% THD
- +20 dBu -> approximately 1.0% THD

Input-level difference:
- 16 dB
- amplitude ratio = 10^(16/20) = 6.309573

THD ratio:
- 1.0 / 0.025 = 40

If normalized THD follows a local power law:

THD proportional to A^n

then:

n = log(40) / log(6.309573) ≈ 2.0026

So the exact Jensen anchors imply almost exactly:

THD proportional to amplitude^2

over this interval.

## Connection to H3-dominant transformer physics

For a locally odd-symmetric cubic characteristic:

y = g1*x + g3*x^3 + ...

a sine input produces:
- fundamental approximately proportional to A;
- H3 approximately proportional to A^3;
- therefore H3/fundamental approximately proportional to A^2.

Bill Whitlock's Jensen transformer chapter independently states that an un-magnetized transformer core produces nearly pure third-harmonic distortion with virtually no even-order component.

The two evidence paths are therefore mutually consistent:
- JT-11P-1 exact level anchors -> exponent ~2.003;
- Jensen/Whitlock transformer physics -> H3-dominant local nonlinearity.

## V2 diagnostic gate

For the default demagnetized IRON state, the accepted magnetic model should exhibit around the nominal-to-strong 20 Hz region:

- H3-dominant distortion;
- very low H2 without DC bias/remanence;
- local normalized distortion growth close to A^2 before stronger saturation bends the law.

This is a diagnostic, not the full model.

A memoryless cubic waveshaper could satisfy this local law but would still fail required transformer behavior such as:
- hysteresis;
- remanence/minor loops;
- frequency/volt-second dependence;
- DC-bias asymmetry;
- stateful recovery.

Therefore the A^2 law is used to constrain the LOW-FIELD SHAPE of the physical magnetic model, not to replace it.
