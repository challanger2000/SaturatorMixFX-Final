# SMX-3 V2 EF86 Stage-3 Grid-Dependent-Knee Sweep

Date: 2026-09-30
Workflow run: 36664314146
Conclusion: SUCCESS as experiment; HYPOTHESIS REJECTED

## Hypothesis

Philips Graph B visibly shows grid-dependent knee behavior.

Tested minimal extension:

KNEE_eff(Vg1) = K0 * exp(BK * (Vg1 + 2))

normalized at Va=250 V so the Stage-1 Graph-A reference plane remains unchanged.

Coarse grid:
- K0 = 2 / 5 / 10 / 20 / 40 / 80 V
- BK = -0.50 .. +1.00

Score combined:
- exact amplifier current/gain table;
- exact Vo@5% envelope;
- provisional Graph-B surface.

## Result

Best coarse candidate:
- K0 = 5 V
- BK = +0.5
- score NRMS ~2.110

But its exact 5%-THD output envelope is substantially WORSE than Stage-2C:

| Vb | model Vo@5% | Philips | error |
|---:|---:|---:|---:|
| 200 V | 27.14 V | 40 V | -32.15% |
| 250 V | 40.03 V | 50 V | -19.95% |
| 300 V | 52.43 V | 64 V | -18.08% |
| 350 V | 64.34 V | 75 V | -14.21% |
| 400 V | 75.84 V | 87 V | -12.83% |

This is far worse than the Stage-2C fixed-knee candidate.

## Decision

REJECT the simple exponential grid-dependent-knee extension.

Do not interpret this as evidence that real EF86 knee position is grid-independent.

It means:
- this particular one-parameter grid dependence moves the modeled large-signal curvature in the wrong direction;
- the remaining error is not solved by adding more low-Va plate-knee suppression.

## Revised diagnosis

Stage-2C already matches:
- Graph-D Vi->Vo shape reasonably well;
- Stage-1/2 static current surfaces well;

but reaches the manufacturer's 5%-distortion envelope too early.

Therefore the more likely missing degree of freedom is in the CONTROL-GRID TRANSFER CURVATURE / harmonic generation, not additional plate-knee collapse.

Next experiment:
scan the plate-current power exponent EX while re-solving local transfer calibration so that each candidate preserves:
- exact Ia anchor;
- exact gm anchor;
- exact Ig2 anchor.

Then compare:
- Graph A/B residual;
- amplifier current/gain;
- exact 5%-THD envelope;
- Graph-D trajectory.

Only if one EX region improves large-signal behavior without destroying the manufacturer current surfaces will the Stage-1 exponent be reopened.
