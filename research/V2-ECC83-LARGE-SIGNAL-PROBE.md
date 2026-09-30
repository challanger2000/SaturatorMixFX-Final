# SMX-3 V2 ECC83 Large-Signal Probe

Date: 2026-09-30
Status: provisional small-signal fit REJECTED as final TRI0DE model

## Test target

Mullard ECC83 R.C.-coupled amplifier:
- Vb=250 V
- Ra=100 kOhm
- Rk=1.5 kOhm
- following-stage grid resistor=330 kOhm
- documented output at start of positive grid current: 26 Vrms
- documented total distortion at that point: 3.9%
- Philips/Mullard tabulation identifies the output condition at approximately Ig=0.3 uA.

## Model under test

The provisional manufacturer-table fit in:
research/V2-ECC83-MULLARD-FIT.md

Its DC-current and small-signal gain errors across the full 200-400 V table are below about 2%.

Grid-current law remains the measured Dempwolf/Zoelzer EHX-1 law.

## Out-of-fit large-signal result

At the input amplitude where the retained grid-current law reaches 0.3 uA:

- required input peak: approximately 0.9801 V
- output RMS: approximately 36.59 V
- THD H2-H10: approximately 6.44%

Manufacturer target:
- 26 Vrms
- 3.9% total distortion

Approximate modeled harmonic peak amplitudes:
- H1: 51.63 Vpk
- H2: 3.282 Vpk
- H3: 0.528 Vpk
- H4: 0.0555 Vpk
- higher harmonics rapidly smaller

## Decision

The small-signal multi-point fit is NOT a final hardware model.

It fits the local operating-point family by reshaping the Dempwolf/Zoelzer plate law, but its global large-signal transfer is too different from the Mullard amplifier data.

This is important evidence against overfitting only:
- idle current;
- local transconductance/gain;
- supply sweep.

## Next TRI0DE requirement

The final offline reference objective must fit simultaneously:
1. DC operating current across multiple Mullard supply points;
2. loaded small-signal gain across those points;
3. grid-current onset from a measured/published grid-current law;
4. output voltage at grid-current onset;
5. total distortion at that output;
6. plate-current characteristic curves.

If the compact four-parameter Dempwolf plate-current form cannot satisfy all of these simultaneously, retain the full measured Dempwolf specimen model or move to a richer circuit/model family rather than forcing the constants.
