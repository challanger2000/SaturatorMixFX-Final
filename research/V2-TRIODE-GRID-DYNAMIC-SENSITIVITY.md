# SMX-3 V2 TRI0DE Dynamic Grid-Current Sensitivity

Date: 2026-09-30
Status: INFORMATIONAL sensitivity experiment

## Purpose

The current dynamic TRI0DE reference uses the RSD-2 Dempwolf/Zoelzer specimen.

Measured 12AX7 grid-current laws differ materially between:
- RSD-1;
- RSD-2;
- EHX-1;
- independent Danyuk overload measurements.

This experiment isolates grid-current uncertainty while holding the plate/cathode current law fixed at RSD-2.

## Stress protocol

- documented Mullard/Philips dynamic surrounding network;
- RSD-2 plate/cathode law;
- 1 kHz;
- 2.0 Vrms sustained sine overload;
- 0.4 s physical-time settling;
- then input removed to zero;
- recovery measured against zero-input DC operating point.

Metrics:
- minimum Va;
- maximum Vg;
- maximum grid current;
- average driven Vg and cathode voltage;
- recovery toward the zero-input bias state;
- fixed recovery checkpoints.

## Interpretation rule

This test does NOT select a production grid-current law.

It quantifies how much the extreme-drive behavior changes when only a measured uncertain sub-model is changed.

The Danyuk case is explicitly hybrid:
- RSD-2 plate law;
- Danyuk grid-current law.

It exists to bound sensitivity, not to claim one physically measured tube.

## Product use

If blocking/recovery changes little across the measured laws:
- RSD-2 may remain a sufficiently robust archetype.

If it changes materially:
- Drive 75-100% must either expose/specify the chosen specimen archetype;
- or use a separately justified consensus/bounded grid-current law.

Do not hide specimen uncertainty inside arbitrary Drive tuning.
