# SMX-3 V2 EF86 EX=1.40 Graph-D Out-of-Fit Result

Date: 2026-09-30
Workflow run: 36683173572
Conclusion: SUCCESS as test; PLAUSIBLE out-of-fit large-signal shape

## Candidate under test

Current strongest static/large-signal PENTODE candidate:

- EX = 1.40
- VCT = 0.609404027245
- KG1 = 1733.51695398
- S0 = 0.000115372393411
- Stage-2C normalized plate knee retained
- Philips typical Ia/gm/Ig2 device anchors retained

This candidate was selected without using Philips Graph D.

## Philips Graph-D comparison

Provisional manufacturer-graph points:

| Vo | Vi model | Vi graph | THD model | THD graph |
|---:|---:|---:|---:|---:|
| 10 V | 88.06 mV | ~91 mV | 0.604% | ~0.30% |
| 20 V | 177.41 mV | ~184 mV | 1.147% | ~0.75% |
| 30 V | 270.04 mV | ~280 mV | 1.597% | ~1.45% |
| 40 V | 370.16 mV | ~378 mV | 2.259% | ~2.55% |
| 50 V | 487.41 mV | ~490 mV | 4.393% | ~5.00% |

## Compression / transfer result

Vi -> Vo normalized residual:

- NRMS ~0.688 sigma
- worst ~0.996 sigma

Interpretation:
STRONG out-of-fit agreement.

The candidate reproduces the manufacturer input/output compression trajectory very well under the present digitization uncertainty.

## Distortion-growth result

THD normalized residual:

- NRMS ~2.466 sigma
- worst ~3.802 sigma

The systematic pattern is informative:

- model is too nonlinear at low output (10-20 V);
- close around 30 V;
- slightly low at 40-50 V.

Therefore the remaining error is not a simple constant gain or THD scale.

## Diagnosis

The static/quasi-static transfer law has the right overall compression geometry, but its harmonic growth is too front-loaded.

Plausible missing mechanisms to test before modifying the static curve:

1. real cathode-bypass dynamics;
2. screen-grid bypass / dynamic screen voltage;
3. output/load network;
4. device capacitances;
5. grid-current onset near the highest level.

Do NOT add:
- an arbitrary low-level distortion suppressor;
- a supply-dependent output trim;
- a post-waveshaper.

The next test must determine how much of the Graph-D residual changes when the exact documented dynamic Philips network is simulated.

## Decision

Status remains:

**STRONG PROVISIONAL EF86 OFFLINE CANDIDATE**

Graph D does NOT reject EX=1.40.

But Graph-D distortion shape prevents final promotion until:
- the dynamic network is evaluated;
- graph digitization is calibrated more tightly;
- remaining distortion residual is explained physically.
