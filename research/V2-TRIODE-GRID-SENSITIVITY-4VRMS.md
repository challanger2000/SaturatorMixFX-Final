# SMX-3 V2 TRI0DE 4 Vrms Grid-Current Sensitivity Result

Date: 2026-09-30
Status: INFORMATIVE ROBUSTNESS RESULT

## Protocol

Fixed:
- RSD-2 plate/cathode law;
- documented Mullard/Philips dynamic RC network;
- 1 kHz;
- 4.0 Vrms sustained overload;
- 0.4 s driven settling;
- 2 s recovery observation.

Varied only the grid-current law:
- Dempwolf RSD-1;
- Dempwolf RSD-2;
- Dempwolf EHX-1;
- Danyuk polynomial overload fit.

The Danyuk case is explicitly hybrid and is used only as an independent sensitivity bound.

## Measured strong-drive results

| grid-current law | min Va | max Vg | max Ig | recovery to 10 mV |
|---|---:|---:|---:|---:|
| RSD-1 | ~75.65 V | +0.176 V | ~71.0 uA | ~183.74 ms |
| RSD-2 | ~73.69 V | +0.206 V | ~72.4 uA | ~183.79 ms |
| EHX-1 | ~71.10 V | +0.244 V | ~65.3 uA | ~183.38 ms |
| Danyuk hybrid | ~82.44 V | +0.075 V | ~68.7 uA | ~186.88 ms |

## Recovery shape

At 200 ms after signal removal:
- cathode-bias error is already only about 6.5-7.1 mV;
- output error is roughly 0.039-0.042 V.

By 500 ms:
- cathode/output residuals are effectively negligible for all tested laws.

## Interpretation

Static positive-grid current differs substantially between measured sources, but the complete AC-coupled cathode-biased stage compresses those differences.

The surrounding circuit self-limits the sustained positive-grid excursion through:
- grid-current conduction;
- coupling-capacitor charge shift;
- cathode-bias movement.

Consequently, the strong-drive recovery time is remarkably insensitive to the chosen measured grid-current law.

The largest model-to-model differences are instead:
- peak positive Vg;
- minimum Va;
- instantaneous grid-current waveform;
- short-term bias trajectory.

## Decision

Retain RSD-2 as the coherent TRI0DE reference specimen.

Do NOT create a synthetic consensus grid-current law merely to average the sources.

Reason:
- RSD-2 is a complete internally consistent measured specimen fit;
- dynamic stage-level behavior remains close to the independent RSD-1/EHX/Danyuk bounds;
- a hybrid law would reduce provenance clarity without materially improving the observed recovery behavior.

Use the other grid-current laws as uncertainty bounds during:
- Drive 75-100% validation;
- blocking/recovery QA;
- aliasing/solver-reduction tests.

## Product implication

The current evidence supports a strong-drive TRI0DE implementation based on the complete RSD-2 dynamic model, provided:
- Vg remains inside the measured approximately -5..+3 V range;
- the documented invalid combination Vg>0 with Va<20 V is avoided;
- production reduction preserves the ~180 ms overload-recovery behavior within a justified tolerance.
