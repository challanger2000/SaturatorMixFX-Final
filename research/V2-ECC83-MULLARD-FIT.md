# SMX-3 V2 ECC83 Mullard Multi-Point Fit

Date: 2026-09-30
Status: provisional reference candidate — supersedes the earlier EHX-1-only selection

## Why the earlier decision was revised

The first EHX-1 comparison used an unloaded small-signal plate gain.

Mullard's R.C.-coupled amplifier table explicitly documents a 330 kOhm grid resistor for the following stage. In the midband this resistor is an AC load on the plate through the coupling capacitor.

When that load is included, the published Dempwolf/Zoelzer specimens give approximately at Vb=250 V / Ra=100 kOhm / Rk=1.5 kOhm:

- RSD-1: Ik ~0.8225 mA, gain ~59.08
- RSD-2: Ik ~0.8354 mA, gain ~57.50
- EHX-1: Ik ~0.8248 mA, gain ~50.22
- Mullard: Ik ~0.86 mA, gain 54.5

Therefore no measured specimen should be declared the final Mullard reference from the earlier unloaded comparison.

This is an intentional correction of the research record.

## Provisional manufacturer-table fit

The Dempwolf/Zoelzer equation family was refitted to all five rows of Mullard's 100 kOhm amplifier table simultaneously.

Targets:

| Vb | Rk | Mullard Ik | Mullard gain |
|---:|---:|---:|---:|
| 200 V | 1.8 kOhm | 0.65 mA | 50.0 |
| 250 V | 1.5 kOhm | 0.86 mA | 54.5 |
| 300 V | 1.2 kOhm | 1.11 mA | 57.0 |
| 350 V | 1.0 kOhm | 1.40 mA | 61.0 |
| 400 V | 0.82 kOhm | 1.72 mA | 63.0 |

Ra=100 kOhm and the documented 330 kOhm following-stage load are included.

Fitted plate/cathode-current parameters:

- G = 2.18714303e-3
- mu = 105.447663
- gamma = 1.07136184
- C = 2.60122984

Grid-current parameters are provisionally retained from EHX-1 because the small-signal Mullard table does not identify them.

Evidence class:
EMPIRICALLY TUNED TO DOCUMENTED MANUFACTURER MEASUREMENTS within a published physically motivated equation family.

## Reproduction

| Vb | fitted Ik | Ik error | fitted gain | gain error |
|---:|---:|---:|---:|---:|
| 200 V | 0.64854 mA | -0.224 % | 49.694 | -0.612 % |
| 250 V | 0.85762 mA | -0.277 % | 54.289 | -0.386 % |
| 300 V | 1.12018 mA | +0.917 % | 58.077 | +1.889 % |
| 350 V | 1.39804 mA | -0.140 % | 60.706 | -0.482 % |
| 400 V | 1.71593 mA | -0.237 % | 62.707 | -0.465 % |

Worst observed errors:
- cathode current: ~0.92 %
- gain: ~1.89 %

## Important limitation

This parameter set is NOT yet final.

Compared with the measured Dempwolf/Zoelzer specimen fits, gamma and C move materially. That could mean:
- Mullard's table represents a different average tube population;
- the reduced fitting objective is compensating for missing curve-shape information;
- or both.

Therefore the fit must be challenged against:
- ECC83 plate-current curve families;
- grid-current onset;
- large-signal Mullard output/distortion points;
- frequency response after the documented coupling/bypass network is included.

No promotion to production DSP before those checks.
