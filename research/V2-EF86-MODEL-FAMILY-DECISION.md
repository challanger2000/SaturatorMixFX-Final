# SMX-3 V2 EF86 Model-Family Decision After Graph A / Graph D

Date: 2026-09-30
Reference workflow: 36661894283
Conclusion: SUCCESS

## Graph A structural comparison

Provisional manufacturer-graph screen-voltage families:
- Va=250 V
- Vg2=60/100/140/180 V
- Ia versus Vg1

Results:

### Generalized compact surrogate
- normalized RMS: ~0.985 sigma

### Extended knee/kink family, comparison parameters
- normalized RMS: ~0.633 sigma

Interpretation:
the extended equation family follows the Philips screen-voltage dependence materially better under the same provisional digitization uncertainty.

This result concerns MODEL FORM only.

The community comparison parameter set remains non-authoritative.

## Graph D shape check of compact surrogate

The compact generalized surrogate was also checked against provisional Philips Graph-D:
- Vi -> Vo normalized RMS: ~0.969 sigma
- worst Vi residual: ~1.379 sigma
- distortion -> Vo normalized RMS: ~4.236 sigma
- worst distortion residual: ~6.281 sigma

Therefore:
- its compression/input-output slope is plausible;
- its distortion-growth shape is not.

This independently confirms the full-envelope rejection above 250 V.

## Decision

The compact generalized surrogate is no longer the preferred final PENTODE model family.

Retain it only as:
- a compact realtime comparison;
- a useful local 200-250 V baseline;
- evidence for minimum complexity.

Promote the extended screen/knee family to:
**PRIMARY PENTODE MODEL-FAMILY RESEARCH PATH**

Conditions:
1. parameters must be independently fitted to Philips primary data;
2. Graph A and B surfaces are Stage-1/structural constraints;
3. exact circuit current/gain table is Stage 2;
4. exact 5%-THD envelope and Graph D are Stage 3;
5. no community fitted parameter becomes production authority;
6. final complexity must still justify itself against the compact baseline in realtime CPU/aliasing tests.

## Why this matters

The choice is no longer based on 'more parameters sounds more realistic'.

The extended family earns further work because it:
- better reproduces independent screen-voltage data;
- has the missing plate-knee degrees of freedom;
- is structurally capable of matching the multi-supply large-signal envelope.

The compact family is rejected because independent manufacturer domains expose systematic limitations.
