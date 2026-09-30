# SMX-3 V2 TRI0DE Operating-Domain Probe

Date: 2026-09-30
Reference:
Dempwolf/Zoelzer EHX-1 12AX7 current model inside the documented Philips/Mullard ECC83 dynamic network.

Status:
settled-state result; supersedes the earlier short-run interpretation.

## Why this gate exists

The Dempwolf/Zoelzer source model identifies reduced accuracy especially for:
- positive grid voltage;
- very low anode voltage, approximately Va < 20 V.

SMX-3 must therefore measure where the actual cathode-biased/coupled reference circuit enters those regions.

## Measurement-method correction

The first operating-domain estimate used only a fixed number of cycles and therefore inherited the same insufficient-settling problem documented in:

research/V2-TRIODE-SETTLING-CORRECTION.md

The corrected probe now preconditions the complete nonlinear/capacitive circuit for 0.4 s before evaluating the final cycles.

This materially changes the strong-drive HF operating point because:
- cathode bias has time to shift;
- input-coupling/grid-current interaction reaches periodic steady state;
- the circuit self-biases rather than remaining near its cold-start trajectory.

## Settled-state regression points

GitHub Actions run 36657000349 measured:

| frequency | Vin RMS | min Va | max Vg | max Ig | interpretation |
|---:|---:|---:|---:|---:|---|
| 20 Hz | 0.70 V | ~125.65 V | ~-0.515 V | ~0.054 uA | valid-domain |
| 1 kHz | 0.70 V | ~117.91 V | ~-0.312 V | ~0.281 uA | valid-domain |
| 10 kHz | 0.70 V | ~117.86 V | ~-0.311 V | ~0.284 uA | valid-domain |
| 20 kHz | 0.70 V | ~117.87 V | ~-0.311 V | ~0.284 uA | valid-domain |
| 20 kHz | 1.00 V | ~107.22 V | ~-0.101 V | ~3.96 uA | still negative-grid |
| 20 kHz | 8.00 V | ~78.32 V | ~+0.563 V | ~167.88 uA | positive-grid extrapolation |

## Important correction

The earlier short-run estimate suggested:
- positive-grid crossing already near ~0.93 Vrms at 20 kHz;
- Va < 20 V around 8 Vrms / 20 kHz.

Those conclusions are superseded.

After proper settling:
- 1.0 Vrms / 20 kHz remains negative-grid;
- 8.0 Vrms / 20 kHz enters positive-grid operation strongly;
- but Va remains around 78 V rather than dropping below 20 V.

The cathode-bias/grid-conduction network moves the operating point substantially under sustained extreme excitation.

## Current conservative normal-domain fixture

The automated gate now establishes:

- 0.70 Vrms remains safely negative-grid from 20 Hz through 20 kHz;
- 1.00 Vrms at 20 kHz also remains negative-grid;
- 8.00 Vrms at 20 kHz intentionally exercises the positive-grid extrapolation region.

This gives the future product calibration more headroom than the initial short-run result suggested.

## Low-Va limitation

Very-low-anode-voltage behavior remains a known limitation of the Dempwolf model family.

However, the present documented Mullard/Philips circuit may not reach Va < 20 V under ordinary or even very strong steady sine excitation before:
- grid conduction;
- cathode-bias shift;
- coupling-network behavior

substantially changes the trajectory.

Therefore Va<20 V is now treated as:
- a monitored warning;
- not a required stress fixture.

Do not invent an artificial low-Va test merely to force the circuit into a region it does not naturally visit.

## Product implication

### 0-75% Drive target
Can likely remain fully inside the validated negative-grid region if calibration is chosen carefully.

### 75-100% Drive target
May intentionally enter positive-grid operation for stronger physical saturation.

Before production:
- positive-grid behavior needs a more authoritative extension or bounded model;
- Drive mapping must record the fraction of samples/time spent beyond Vg=0;
- extreme operation must not depend on undocumented low-Va extrapolation.

## Decision

The first practical validity boundary in the current TRI0DE circuit remains positive-grid operation.

But correct periodic steady-state measurement moves that boundary materially higher than the initial short-run estimate.

This is favorable:
SMX-3 can obtain substantial authentic triode nonlinearity before relying on the least reliable region of the Dempwolf current model.
