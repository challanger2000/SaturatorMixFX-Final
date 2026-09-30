# SMX-3 V2 TRI0DE Operating-Domain Probe

Date: 2026-09-30
Reference:
Dempwolf/Zoelzer EHX-1 12AX7 current model inside the documented Philips/Mullard ECC83 dynamic network.

## Why this gate exists

The source model is not equally trustworthy everywhere.

The Dempwolf/Zoelzer paper identifies inaccuracies in particular for:
- positive grid voltage;
- very low plate/anode voltage (approximately Va below 20 V).

SMX-3 must therefore know where its product Drive mapping enters those regions instead of silently extrapolating.

## Measured matrix highlights

### 20 Hz

At 0.70 Vrms:
- min Va ~125.65 V
- max Vg ~-0.515 V

At 1.00 Vrms:
- min Va ~112.40 V
- max Vg ~-0.282 V

Even 2.0 Vrms remains negative-grid in the current low-frequency network.

### 1 kHz

At 0.70 Vrms:
- min Va ~117.03 V
- max Vg ~-0.299 V

At 1.00 Vrms:
- min Va ~107.43 V
- max Vg ~-0.113 V

At 2.00 Vrms:
- min Va ~99.74 V
- max Vg ~+0.0556 V

Therefore the measured model begins entering positive-grid extrapolation somewhere above the 1 Vrms region at 1 kHz.

### 10 kHz

At 0.70 Vrms:
- min Va ~115.32 V
- max Vg ~-0.266 V

At 1.00 Vrms:
- min Va ~99.57 V
- max Vg ~+0.0307 V

### 20 kHz

At 0.70 Vrms:
- min Va ~115.19 V
- max Vg ~-0.263 V

At 1.00 Vrms:
- min Va ~97.28 V
- max Vg ~+0.0764 V

Therefore the worst current positive-grid boundary within the tested audio band is near the top of the band.

A linear interpolation of the already measured 0.70/1.00 Vrms points places first crossing around:
- ~0.97 Vrms at 10 kHz;
- ~0.93 Vrms at 20 kHz.

The checked-in tool performs an actual numerical bisection and is the authority for the exact research threshold.

## Very-low-anode-voltage stress

The Va<20 V warning region is much farther away than the first positive-grid boundary under ordinary audio-band excitation.

Representative extreme stress:
- 20 kHz / 4 Vrms -> min Va ~50.27 V
- 20 kHz / 6 Vrms -> min Va ~26.36 V
- 20 kHz / 8 Vrms -> min Va ~3.70 V

Thus extremely strong HF excitation can enter BOTH suspect regions.

At 1 kHz / 8 Vrms:
- min Va remains roughly 79.5 V;
- positive grid is already substantial.

## Current conservative valid-domain fixture

Freeze for reference work:

- Vin <= 0.70 Vrms
- frequencies 20 Hz..20 kHz

Within the measured matrix this remains:
- grid voltage < 0 V;
- Va > 20 V.

This is deliberately conservative and is NOT yet the final Drive=75% boundary.

## Product implication

TRI0DE Drive mapping should be split conceptually:

### Normal/musical region
Target approximately 0-75% Drive:
- should remain mostly within the validated tube-model domain;
- no reliance on positive-grid/low-Va extrapolation for its basic character.

### Strong/extreme region
Target approximately 75-100% Drive:
- may intentionally approach grid-current operation;
- but a production model cannot simply trust the present Dempwolf extrapolation outside its documented-valid region.

Before that region is frozen, choose and validate one of:
- a bounded extension of the current law;
- a richer low-Va/positive-grid model;
- a deliberate saturation boundary whose residual versus a higher-authority reference is measured.

Do not simply clamp internal voltages: that would create an arbitrary transfer characteristic rather than hardware behavior.

## Decision

The first limiting mechanism for the current TRI0DE reference is positive-grid excursion, especially at high audio frequencies.

Low-anode-voltage invalidity is an extreme-stress issue rather than the first normal operating boundary.

This gives the later Drive-calibration stage a measurable physical ceiling instead of an arbitrary normalized number.
