# SMX-3 V2 EF86 Stage-2 Simple Screen-Law Result

Date: 2026-09-30
Workflow run: 36662416364
Conclusion: SUCCESS as experiment; REJECTED as final Stage-2 model

## Manufacturer circuit recheck

Philips circuit (1) explicitly includes:
- input coupling capacitor: 0.01 uF
- cathode bypass capacitor: 50 uF
- screen bypass capacitor: 0.5 uF
- output coupling capacitor: 0.01 uF
- Ra=100 kOhm
- Rg2=390 kOhm
- Rk=1 kOhm
- following grid resistor=330 kOhm

Therefore the previous Stage-2 small-signal assumption of substantially bypassed cathode and screen is appropriate in the midband.

The ~5-6% gain residual is not plausibly explained by forgetting those bypass capacitors.

## Simple screen-law experiment

Stage-1 plate-current surface was frozen.

Only:
- MU_G2
- EX_G2
- KG2

were fitted for a simple positive-power screen-current law.

Result:
- objective NRMS ~2.484 sigma
- device Ig2 ~0.5888 mA vs 0.6000 mA
- max cathode-current error ~3.60%
- max gain error ~5.94%
- EX_G2 ran exactly to its lower bound 1.0

Supply sweep:

| Vb | Ik error | gain error | plate node | screen node |
|---:|---:|---:|---:|---:|
| 200 V | +0.41% | +5.77% | ~56.0 V | ~95.9 V |
| 250 V | -2.03% | +5.20% | ~78.2 V | ~117.5 V |
| 300 V | -3.17% | +5.82% | ~99.1 V | ~139.5 V |
| 350 V | -3.60% | +5.94% | ~118.7 V | ~161.9 V |
| 400 V | -3.58% | +5.72% | ~137.0 V | ~184.6 V |

## Interpretation

The Stage-1 high-Va transfer surface is being evaluated at plate voltages as low as ~56 V inside the actual amplifier.

That is precisely where a pentode knee model must begin to matter.

A simple screen-current power law cannot repair a missing plate-voltage knee without distorting other constraints.

## Decision

REJECT the simple separate screen-current law as the completed Stage-2 model.

Stage 2B must introduce a coupled plate/screen knee:

- Stage-1 control/screen transfer remains fixed;
- a low-Va plate-current factor is introduced and normalized to preserve the 250 V Stage-1 anchor;
- screen current receives complementary plate-voltage dependence so current can redistribute toward g2 as plate voltage falls;
- Graph B and ri remain regularization constraints;
- no supply-specific gain correction is allowed.

This is more physically meaningful and better identified than adding arbitrary gain coefficients.
