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


## Measured 4 Vrms / 1 kHz result after full DC-equilibrium correction

Targeted GitHub run:
- run 36698300058
- conclusion: success

The dynamic reference DC solver now includes the grid-leak equilibrium:
Vg/Rg + Ig = 0.

This removed the former artificial long-time recovery offset.

### Sustained overload

| grid-current law | min Va | max Vg | peak Ig | avg Vg | avg Vk | recovery to <10 mV |
|---|---:|---:|---:|---:|---:|---:|
| RSD-1 | 75.65 V | +0.176 V | 71.02 uA | -5.384 V | 0.697 V | 183.74 ms |
| RSD-2 | 73.69 V | +0.206 V | 72.42 uA | -5.352 V | 0.709 V | 183.79 ms |
| EHX-1 | 71.10 V | +0.244 V | 65.35 uA | -5.324 V | 0.720 V | 183.38 ms |
| Danyuk-poly hybrid | 82.44 V | +0.075 V | 68.67 uA | -5.491 V | 0.658 V | 186.88 ms |

## Interpretation

The static grid-current curves differ materially, but the complete AC-coupled,
cathode-biased amplifier self-regulates strongly under sustained overload.

Consequences:

- peak grid current converges into a relatively narrow ~65-72 uA range;
- the strongest observable specimen dependence is in clamp level / max Vg,
  minimum Va and shifted average bias;
- recovery time to the 10 mV criterion is remarkably insensitive to the
  tested grid-current law (~183-187 ms);
- the Danyuk hybrid clamps the grid more strongly and keeps Va higher, but does
  not create a radically different recovery time.

## Current decision

RSD-2 remains a defensible measured-specimen archetype for the dynamic TRI0DE
reference.

There is currently no measurement-based reason to invent an arbitrary
"consensus grid-current" law merely to equalize recovery.

Retain RSD-1 / EHX-1 / Danyuk as uncertainty bounds for:
- clamp behavior;
- grid-current charge;
- bias shift;
- extreme-drive harmonic shape.

If production Drive 75-100% is later tuned materially around clamp level,
repeat this comparison on the exact production realtime solver.
