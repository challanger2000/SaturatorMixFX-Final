# SMX-3 V2 EF86 Provisional Multi-Anchor Fit

Date: 2026-09-30
Status: provisional reference candidate — NOT final PENTODE model

## Objective used

A six-parameter Koren-form pentode equation was refitted against multiple independent Philips-1956 constraints simultaneously:

Device point:
- Va=250 V
- Vg2=140 V
- Vg1=-2 V
- Ia=3.0 mA
- Ig2=0.6 mA
- gm=2.0 mA/V

Amplifier circuit 1:
- Ra=100 kOhm
- Rg2=390 kOhm
- Rk=1 kOhm
- next-stage grid resistor=330 kOhm

Manufacturer sweep:
- Vb = 200, 250, 300, 350, 400 V
- Ik at every supply point
- small-signal voltage gain at every supply point

## Fitted parameters

- MU = 40.4643134
- EX = 1.10072133
- KG1 = 805.463266
- KG2 = 2542.71827
- KP = 220.481328
- KVB = 8.11723096

Evidence classification:
EMPIRICALLY TUNED TO DOCUMENTED MEASUREMENTS.

These are NOT hardware component values.

## Reproduced device point

Approximate result:
- Ia = 3.0293 mA, error +0.98 %
- Ig2 = 0.5964 mA, error -0.60 %
- gm = 1.9929 mA/V, error -0.36 %

## Amplifier sweep

| Vb | Philips Ik | fit Ik | error | Philips gain | fit gain | error |
|---:|---:|---:|---:|---:|---:|---:|
| 400 V | 3.300 mA | 3.3922 mA | +2.79 % | 124 | 122.10 | -1.53 % |
| 350 V | 2.900 mA | 2.9469 mA | +1.62 % | 120 | 119.45 | -0.46 % |
| 300 V | 2.500 mA | 2.5038 mA | +0.15 % | 116 | 116.31 | +0.27 % |
| 250 V | 2.100 mA | 2.0633 mA | -1.75 % | 112 | 112.49 | +0.43 % |
| 200 V | 1.700 mA | 1.6261 mA | -4.35 % | 106 | 107.64 | +1.55 % |

## Interpretation

This is a substantial improvement over the previously tested third-party CC0 parameter set.

Most importantly, one parameter set now explains:
- a real EF86 device operating point;
- screen current;
- transconductance;
- self-biased amplifier current over a 2:1 supply-voltage range;
- amplifier gain over the same range.

No separate output gain compensation was fitted per supply point.

## Why it is still provisional

The fit objective does NOT yet contain the Philips plate-current curve family Ia(Va,Vg1) at Vg2=140 V.

Therefore a model could still:
- interpolate the chosen operating region well;
- yet have the wrong pentode knee;
- wrong output resistance away from the operating point;
- wrong large-signal trajectory;
- wrong distortion progression.

Promotion gate:
digitize multiple Philips plate curves and include them as out-of-fit validation first; only then decide whether to refit or accept this parameter family.
