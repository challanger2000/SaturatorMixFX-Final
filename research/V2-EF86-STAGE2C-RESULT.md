# SMX-3 V2 EF86 Stage-2C Minimal Knee Result

Date: 2026-09-30
Workflow run: 36663206009
Conclusion: SUCCESS

## Model reduction

Stage-1 transfer surface frozen.

Stage-2C used only:
- KNEE: normalized arctangent plate-voltage knee;
- S0: screen-current proportionality;
- S1: optional plate-voltage dependence of screen current.

Fit result:

- KNEE = 3.35311366202 V
- S0 = 9.02342723159e-5
- S1 = 0 exactly at optimum

## Main finding

S1 collapsing to zero is a MODEL-SIMPLIFICATION result.

The current Philips Stage-2 evidence does not justify an additional explicit plate-voltage-dependent screen-current correction.

The important missing mechanism was the plate knee itself.

## Fit quality

Objective:
- NRMS ~0.8317 sigma

Graph B:
- NRMS ~0.4418 sigma
- worst ~1.072 sigma

Amplifier table:
- max Ik error ~2.39%
- max gain error ~3.43%

Supply points:

| Vb | Ik error | gain error |
|---:|---:|---:|
| 200 V | -2.39% | -3.43% |
| 250 V | -1.82% | -0.89% |
| 300 V | -1.22% | +1.50% |
| 350 V | -0.61% | +2.74% |
| 400 V | -0.025% | +3.25% |

Device:
- Ig2 ~0.550 mA vs Philips 0.600 mA
- inferred ri ~1.73 MOhm vs Philips typical ~2.5 MOhm

The remaining ri difference is explicitly retained as a cross-check warning; it must not be hidden by output gain correction.

## Decision

PROMOTE to:
**MINIMAL EF86 STAGE-2 STATIC CANDIDATE**

Not final PENTODE model.

Reasons for promotion:
- fewer parameters than Stage 2B;
- better objective;
- no redundant screen-knee term;
- strong Graph-B consistency;
- materially improved amplifier current/gain trend.

Remaining blockers:
1. exact multi-supply large-signal envelope;
2. Graph-D distortion trajectory;
3. tighter reconciliation of ri versus amplifier gain;
4. dynamic network;
5. realtime/aliasing/CPU.

The next stage may adjust large-signal transfer curvature only if it preserves the Stage-1/2 manufacturer surfaces within their frozen tolerances.
