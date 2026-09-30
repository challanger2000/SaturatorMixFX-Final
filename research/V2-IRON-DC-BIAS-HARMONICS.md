# SMX-3 V2 IRON DC-Bias / Remanence Harmonic Gate

Date: 2026-09-30

Primary engineering expectation:
Jensen/Whitlock transformer literature describes:

- demagnetized/unbiased transformer operation as strongly H3-dominant with virtually no intentional even-order component;
- DC or residual magnetization as a mechanism that introduces significant H2;
- removal of the bias followed by symmetric AC cycling as a path back toward the normal symmetric periodic orbit.

## Implemented probe

Tool:
tools/smx3_v2_iron_dc_bias_probe.py

Reference analysis:
- +4 dBu
- 20 Hz
- RK4 reference integration
- baseline state initialized at H=0, M=0

Sequence:

1. Establish baseline periodic orbit with 40 AC cycles.
2. Apply controlled DC source pre-bias for 1 s.
3. Remove DC.
4. Analyze the first four AC cycles after bias removal.
5. Continue 40 additional symmetric AC cycles.
6. Compare:
   - H2;
   - H3;
   - H5;
   - H2/H3 ratio;
   - magnetic state H/M.

DC fixtures:
- 10 mV
- 50 mV
- 100 mV source pre-bias.

## What the gate tests

For the larger DC fixtures:

- H2 must materially increase immediately after DC pre-bias;
- H2 must decay substantially after bias removal and continued symmetric AC cycling;
- the recovered H2/H3 relationship must return toward the deterministic baseline orbit.

This is a state-physics test, not a claim that these exact DC voltages represent a documented JT-11P-1 use case.

## Why this matters

A memoryless saturator can be tuned to mimic:
- THD magnitude;
- H3 dominance;
- even a level/frequency curve.

It cannot naturally reproduce:
- magnetic pre-bias history;
- temporary even-order asymmetry after bias removal;
- recovery toward a symmetric periodic orbit.

This gate therefore discriminates a genuinely stateful magnetic model from a static nonlinear approximation.

## State-policy implication

The offline model demonstrates physically meaningful history dependence.

The production plugin must nevertheless define deterministic host behavior.

Still required before production freeze:
- decide whether magnetic state is serialized;
- or reset to a defined demagnetized/reference equilibrium on project load;
- verify deterministic behavior after transport stop/start and process activation;
- verify no host scheduling/order dependence in Mix FX multichannel processing.

Do not expose hidden nondeterministic remanence.
