# SMX-3 V2 IRON HF Two-Parameter Identifiability Study

Date: 2026-09-30

## Goal

Extend the linear JT-11P-1 skeleton so it can satisfy both:
- typical -0.05 dB at 20 kHz relative to 1 kHz;
- approximately -3 dB upper point at 95 kHz.

Topology studied:
- primary DCR;
- shunt magnetizing inductance;
- ideal 1:1 transformer;
- secondary DCR;
- one equivalent series leakage inductance;
- one effective shunt/load capacitance;
- 10 kOhm load.

## Result

The two magnitude constraints can be solved exactly, but the component values are not unique.

Two numerical solutions include approximately:

Candidate A:
- Lleak = 3.537 mH
- Ceff = 903.6 pF

Candidate B:
- Lleak = 27.108 mH
- Ceff = 117.9 pF

Both produce essentially the same selected magnitude points:
- ~-0.04 dB at 20 Hz from the previously derived magnetizing branch;
- 0 dB reference at 1 kHz;
- -0.05 dB at 20 kHz;
- -3.0 dB at 95 kHz.

They also generate essentially identical broad magnitude roll-off in this reduced topology.

## Interpretation

Magnitude-only constraints do not uniquely identify leakage inductance and effective capacitance.

Candidate B is superficially more physically plausible because its fitted effective capacitance (~118 pF) is on the same order as Jensen's documented:
- primary-to-shield/case capacitance: 98 pF;
- secondary-to-shield/case capacitance: 110 pF.

However this is NOT sufficient evidence to declare Candidate B physically correct.

Reasons:
- the documented capacitances are to shield/case, not necessarily the exact effective differential shunt capacitance of the reduced model;
- interwinding capacitance is not separately documented in the selected table;
- leakage inductance is not directly documented;
- several parasitic topologies can have nearly identical magnitude response.

## Required discriminator

Use additional evidence before freezing Lleak/Ceff:
- Jensen deviation-from-linear-phase graph;
- any available transformer phase/group-delay data;
- more HF magnitude points;
- physically documented winding/parasitic measurements if available.

Evidence status:
both parameter pairs are ESTIMATED/APPROXIMATED reduced-network candidates.

## Decision

Do not freeze a specific leakage/capacitance pair yet.

Freeze only the observable transfer constraints:
- in-band flatness;
- 20 kHz typical deviation;
- 95 kHz upper -3 dB bandwidth.

This avoids encoding false physical certainty into the V2 IRON model.
