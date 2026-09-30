# SMX-3 V2 EF86 Knee-Aware Static Refit

Date: 2026-09-30
Status: REJECTED INTERMEDIATE MODEL — useful identifiability result

## Objective

Fit the extended EF86 core equation family WITHOUT kink terms against:

- Philips Graph A screen families;
- Philips Graph B plateau points;
- new Philips Graph B knee-region points at 20/40/60/80 V;
- exact device Ia / Ig2 / gm anchors;
- circuit-1 DC current and small-signal gain sweep.

Weak regularization was used only to prevent poorly identified parameters from diverging arbitrarily.

No large-signal 5%-THD envelope data were used during this stage.

## Representative fitted parameter set

- MU ≈ 44.70894
- KG1 ≈ 1208.50779
- KP ≈ 238.26123
- KVB ≈ 63.64558
- EX ≈ 0.96428
- KG2 ≈ 77294.8
- KNEE ≈ 11.97187
- KVC ≈ 20.63642
- KNEE2 ≈ 32.21346
- VCT ≈ -0.03071 V
- KLAMG ≈ 1.21e-5

Evidence class:
EMPIRICALLY TUNED TO PROVISIONAL + DOCUMENTED MANUFACTURER DATA.

These values are NOT accepted hardware parameters.

## Static fit quality

Approximate normalized residuals:

- Graph A screen family: NRMS ~0.78 sigma, worst ~2.16 sigma
- Graph B plateau: NRMS ~0.71 sigma, worst ~1.63 sigma
- Graph B knee: NRMS ~0.88 sigma, worst ~1.68 sigma

Device point:
- Ia ~2.984 mA
- Ig2 ~0.582 mA
- gm ~2.098 mA/V

Amplifier sweep remains directionally plausible but current is still low at the lower supply points.

## Critical out-of-fit large-signal test

Without adding kink terms, the same model reaches 5% THD at approximately:

| Vb | modeled Vo@5% | Philips Vo@5% |
|---:|---:|---:|
| 200 V | ~13.99 V | 40 V |
| 250 V | ~21.69 V | 50 V |
| 300 V | ~31.22 V | 64 V |
| 350 V | ~41.52 V | 75 V |
| 400 V | ~52.06 V | 87 V |

## Decision

REJECT as a complete PENTODE model.

This failure is useful because it demonstrates that:

- Graph A/B knee and screen behavior can be fit reasonably well with the extended static core;
- but the manufacturer large-signal envelope requires additional nonlinear/kink structure;
- therefore those extra terms should be identified specifically from the large-signal data rather than allowed to compensate static current surfaces.

## Revised parameter-identification architecture

### Block 1 — static/small-signal
Use:
- MU
- KG1
- KP
- KVB
- EX
- screen-current scale terms
- KNEE/KNEE2
- limited plate-slope terms

Fit against:
- Graph A
- Graph B knee + plateau
- device Ia/Ig2/gm
- DC/gain sweep

### Block 2 — large-signal/kink
Only after Block 1 is constrained, fit:
- kink magnitude/shape terms;
- any remaining large-signal knee asymmetry terms

against:
- exact Vo@5% envelope 200..400 V;
- Philips Graph-D Vi->Vo;
- Philips Graph-D distortion->Vo.

Then re-run all Block-1 residuals.

## Important identifiability note

The very large fitted KG2/KVC values show that screen-current parameterization is still weakly identified by the available data.

Do not freeze those numbers.

Graph A constrains anode-current response to screen voltage, but direct screen-current evidence remains sparse.

If a simpler screen-current law can satisfy the exact Ig2 anchor and amplifier behavior without introducing weakly identified parameters, prefer the simpler formulation.
