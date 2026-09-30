# SMX-3 V2 IRON — Static JA Parameter vs DLP Sensitivity

Date: 2026-09-30
Status: structural model-family diagnostic

## Question

Can Jensen DLP be recovered simply by retuning the quasi-static
Jiles-Atherton pinning/coercivity parameter k while re-fitting the already
required THD anchors?

If yes, an additional dynamic-loss term might be unnecessary.

If no, the missing phase behavior is structurally outside the current
quasi-static JA parameterization.

## Protocol

For multiple fixed k values spanning a wide range, re-fit:
- reversible fraction c;
- field/current scale KI

so that the model continues to reproduce:
- +4 dBu / 20 Hz ~0.025% THD;
- +20 dBu / 20 Hz ~1% THD.

Then evaluate magnetic-only DLP over 20 Hz..20 kHz.

Representative solutions:

| k | fitted c | fitted KI A/m/A | worst DLP |
|---:|---:|---:|---:|
| 3 | ~0.971 | ~32483 | ~3.88 deg |
| 5 | ~0.944 | ~33882 | ~3.87 deg |
| 8 | ~0.907 | ~35820 | ~3.87 deg |
| 12 | ~0.863 | ~38241 | ~3.88 deg |
| 17.8 | ~0.810 | ~41192 | ~3.88 deg |
| 25 | ~0.756 | ~43764 | ~3.88 deg |
| 40 | ~0.671 | ~46839 | ~3.88 deg |
| 60 | ~0.585 | ~49312 | ~3.89 deg |
| 100 | ~0.462 | ~52559 | ~3.89 deg |

The precise c/KI values are not promoted model parameters; this is a
sensitivity experiment.

## Result

The quasi-static model has a strong parameter tradeoff:

- k can move substantially;
- c and KI compensate so the exact THD anchors remain satisfied;
- the resulting low-field phase curvature hardly changes.

Therefore Jensen DLP is not practically identifiable/correctable by k once
the independent THD evidence is preserved.

## Decision

Do NOT retune quasi-static JA hysteresis parameters merely to chase DLP.

Retain the corrected nonlinear JA candidate for:
- THD growth;
- H3 parity;
- hysteresis;
- remanence;
- DC-bias asymmetry.

Add a separately identified dynamic-loss mechanism for the frequency-dependent
loss/complex-permeability behavior missing from the quasi-static model.

This is consistent with dynamic Jiles-Atherton literature, where classical
eddy-current and excess losses are added separately from the quasi-static
hysteresis law.
