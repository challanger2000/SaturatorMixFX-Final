# SMX-3 V2 TRI0DE Reference Baseline — corrected loaded-circuit comparison

Date: 2026-09-30
Tool: tools/smx3_v2_ecc83_reference.py

## Why this document supersedes the earlier EHX-1 selection

The first cross-source comparison used the selected 250 V / 100 kOhm / 1.5 kOhm operating point but compared small-signal gain without the manufacturer-documented 330 kOhm following-stage load.

The Philips/Mullard circuit diagram and table explicitly include Rg'=330 kOhm for the selected row.

That load materially changes the gain comparison and therefore the preferred measured 12AX7 specimen.

The corrected comparison includes:
- Vb=250 V
- Ra=100 kOhm
- Rk=1.5 kOhm
- Rg'=330 kOhm
- cathode bypassed for the low-frequency/static comparison

Manufacturer anchors:
- Ia/Ik approximately 0.86 mA
- voltage gain 54.5
- output 26 Vrms at the stated Ig=0.3 uA criterion
- total distortion 3.9% at that operating condition

## Corrected results

| specimen | solved Ik | current error | loaded gain | gain error | model THD at 26 Vrms |
|---|---:|---:|---:|---:|---:|
| RSD-1 | 0.8225 mA | -4.36% | 59.09 | +8.43% | 3.71% |
| RSD-2 | 0.8354 mA | -2.86% | 57.51 | +5.52% | 3.70% |
| EHX-1 | 0.8248 mA | -4.09% | 50.22 | -7.84% | 2.53% |

## Decision

RSD-2 supersedes EHX-1 as the first SMX-3 V2 TRI0DE reference specimen.

Reason:
- closest loaded gain of the three published measured specimens;
- very close cathode current;
- model distortion near the manufacturer 3.9% value at 26 Vrms.

This correction is an example of the project measurement policy working as intended: a prior provisional decision is changed when a more complete circuit model provides better evidence.

## Remaining mismatch: manufacturer grid-current criterion

The manufacturer table labels the 26 Vrms output point with Ig=0.3 uA.

The Dempwolf specimen models do not reproduce that criterion at 26 Vrms in this static loaded-circuit calculation. RSD-2 grid current remains materially below 0.3 uA at that exact output level.

Therefore:
- RSD-2 is a strong cross-source reference, not an exact average-Mullard clone;
- grid-current onset remains an independent validation dimension;
- do not retune grid-current parameters solely to force one manufacturer table label until the dynamic manufacturer circuit is simulated and the precise measurement convention is resolved.

## Regression gate

RSD-2 provisional cross-source limits:
- cathode-current error <=5%
- loaded gain error <=6%
- distortion error at 26 Vrms <=0.5 percentage points

These are research-regression tolerances, not production claims.
