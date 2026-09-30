# SMX-3 V2 EF86 Stage-2 Minimal Screen-Current Probe

Date: 2026-09-30
Status: REJECTED AS FINAL SCREEN MODEL

## Frozen foundation

Plate-current surface:
- Philips Graph A + B constrained;
- Ia anchor constrained;
- gm constrained;
- Ri=2.5 MOhm constrained.

This Stage-2 experiment does NOT refit the plate surface.

## Minimal screen law tested

Ig2 = max(Vg2/MUs + Vg1 + Voff, 0)^EXs / KG2

Best current fit:
- MUs ≈ 42.6791
- EXs ≈ 0.99264
- KG2 ≈ 2857.13
- Voff ≈ 0.44283 V

The exact device screen-current anchor is reproduced:
- Ig2 ≈ 0.6007 mA vs Philips 0.600 mA.

## Amplifier-sweep result

Using the documented Philips circuit (1):

| Vb | modeled Ik | Philips Ik | modeled gain | Philips gain |
|---:|---:|---:|---:|---:|
| 200 V | ~1.491 mA | 1.700 mA | ~96.82 | 106 |
| 250 V | ~1.905 mA | 2.100 mA | ~105.40 | 112 |
| 300 V | ~2.337 mA | 2.500 mA | ~111.52 | 116 |
| 350 V | ~2.785 mA | 2.900 mA | ~116.22 | 120 |
| 400 V | ~3.247 mA | 3.300 mA | ~119.98 | 124 |

The error is systematic rather than random:
- low-supply current is too low;
- low-supply gain is too low;
- agreement improves progressively with supply voltage.

## Interpretation

A one-dimensional screen law driven only by a simple Vg2/MU + Vg1 term is not sufficient.

The systematic supply dependence indicates that the screen branch needs additional dependence on:
- plate voltage / knee state;
- screen-to-plate current partition;
- or both.

This is consistent with the extended pentode-family architecture, where screen current depends on the same knee state that shapes plate current.

## Decision

Do NOT distort the already-good Stage-1 plate surface to compensate for this screen-model failure.

Next Stage-2 candidate should add only physically motivated screen/plate partition structure, for example:
- dependence on the plate-knee state;
- bounded screen-current fraction;
- explicit plate-voltage dependence.

Any richer screen model must still satisfy:
- exact Ig2 anchor;
- Philips Ik(Vb);
- Philips gain(Vb);
- and must not degrade Graph A+B plate-current residuals.

No per-supply correction is allowed.
