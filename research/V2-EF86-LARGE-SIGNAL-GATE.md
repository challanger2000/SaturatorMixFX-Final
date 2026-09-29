# SMX-3 V2 EF86 Large-Signal Gate

Date: 2026-09-30
Status: six-parameter provisional model REJECTED AS FINAL PENTODE REFERENCE

## Manufacturer target

Philips EF86 sheet, 4-Apr-1956, circuit 1:
- Ra=100 kOhm
- Rg2=390 kOhm
- Rk=1 kOhm
- next-stage grid resistor=330 kOhm
- total distortion target=5%

Manufacturer output voltage at 5% total distortion:
- 400 V supply -> 87 Vrms
- 350 V -> 75 Vrms
- 300 V -> 64 Vrms
- 250 V -> 50 Vrms
- 200 V -> 40 Vrms

## Tested candidate

The previously derived six-parameter Koren-form candidate that already reproduces:
- device Ia/Ig2/gm reasonably closely;
- DC cathode current across the supply sweep;
- small-signal gain across the supply sweep.

A second parameter optimization including the 5%-THD constraint was also tested. It improved the 250 V region but could not reproduce the entire 200-400 V large-signal envelope without degrading other anchors.

Representative best compromise:

| Vb | Philips Vo @5% | model Vo @5% | error |
|---:|---:|---:|---:|
| 400 V | 87 V | ~76.97 V | -11.53 % |
| 350 V | 75 V | ~68.53 V | -8.63 % |
| 300 V | 64 V | ~59.82 V | -6.53 % |
| 250 V | 50 V | ~50.82 V | +1.64 % |
| 200 V | 40 V | ~41.50 V | +3.75 % |

## Decision

The simple six-parameter Koren pentode family is NOT accepted as the final SMX-3 EF86 reference.

Why:
- it can reproduce local operating-point and small-signal data very well;
- but the same parameter family cannot reproduce the documented large-signal saturation envelope over the full supply range closely enough.

This is evidence of model-form limitation, not merely a poor parameter fit.

## Next model family

Investigate a more flexible plate-current formulation fitted directly to the Philips Ia(Va,Vg1) curves.

Useful independent evidence:
- later image-fitted EF86 SPICE models use additional knee/curvature terms beyond the classic six Koren parameters;
- Cohen & Helie, DAFx-2010, emphasize that correct pentode/beam-tetrode knee behaviour materially affects realism and use nonlinear implicit/state-space treatment for realtime simulation.

The next candidate must be constrained simultaneously by:
- Philips plate-curve family;
- device Ia/Ig2/gm;
- amplifier Ik/gain sweep;
- 5%-THD maximum-output sweep.

No per-supply correction is permitted.
