# SMX-3 V2 Hardware Reference Checkpoint — 2026-09-30

This checkpoint records the current authoritative research status for the three SMX-3 V2 hardware modes.

It is not a release declaration.

## TRI0DE

Current reference architecture:
- Dempwolf/Zoelzer measured 12AX7 current-law family;
- EHX-1 specimen retained as measured-device reference/cross-check;
- Philips/Mullard documented ECC83 surrounding network;
- full dynamic MNA/capacitance model;
- corrected physical-time settling;
- corrected relative-phase measurement.

Established:
- DC operating-point reference;
- loaded small-signal comparisons;
- dynamic parasitics Cag/Cgk/Cak;
- aggregate integration convergence;
- trapezoid vs implicit-midpoint numerical agreement;
- settled-state operating-domain probe;
- positive-grid validity monitoring;
- explicit provenance split between measured tube specimen and manufacturer amplifier network.

Rejected/superseded:
- original unloaded EHX gain comparison as final selection;
- small-signal-only Mullard refit as complete large-signal model;
- short fixed-cycle HF THD measurements.

Current blocker:
- authoritative positive-grid / extreme large-signal extension;
- final multi-level/frequency fixture matrix;
- realtime reduction / aliasing / CPU comparison;
- final Drive calibration.

Current status:
STRONG OFFLINE REFERENCE, NOT YET PRODUCTION DSP.

## PENTODE

Primary authority:
Philips EF86 original manufacturer data.

Evidence now includes:
- exact device Ia/Ig2/gm anchor;
- exact circuit-1 component values;
- exact DC-current and gain supply sweep;
- exact Vo@5% THD envelope across Vb=200..400 V;
- Graph A screen-voltage transfer families;
- Graph B high-Va plate family;
- supplemental Graph B 20/40/60/80 V knee-region samples;
- refined Graph D Vi->Vo / distortion->Vo trajectory.

Rejected/superseded:
- third-party CC0 compact parameter set as final reference;
- generalized beta surrogate as final reference;
- unrestricted extended-family static fit;
- knee-aware static fit without large-signal terms.

Important structural result:
- Graph A/B static current physics can be matched reasonably well;
- a static-only model fails the large-signal 5%-THD envelope severely;
- therefore static/small-signal and large-signal/kink degrees of freedom must be identified in separate stages;
- large-signal improvement must not degrade Graph A/B.

Current status:
MODEL FAMILY / DATA ARCHITECTURE DEFINED, FINAL PENTODE PARAMETER SET NOT YET ACCEPTED.

Next blocker:
- staged extended knee/kink refit against all primary domains;
- screen-current identifiability;
- refined large-signal residual;
- dynamic capacitance/network model after static acceptance.

## IRON

Primary hardware archetype:
Jensen JT-11P-1 line-input transformer.

Established linear skeleton:
- 1:1 turns ratio;
- Rp=1.45 kOhm;
- Rs=1.55 kOhm;
- 10 kOhm load;
- circuit-derived ~13 kOhm input impedance;
- circuit-derived ~-2.28 dB insertion gain;
- effective low-level Lm ~144.0 H from the 20 Hz droop measured with Rs=600 Ohm.

Magnetic model family:
Jiles-Atherton stateful hysteresis.

Rejected:
- unmodified DAFx example magnetic shape scaled only by geometry.

Strong provisional candidate:
- reversible fraction c ~0.820 after correcting the Rs=600 LF reference;
- field scale KI ~40528.8 A/m per A re-derived against the exact +20 dBu / 20 Hz anchor;
- low-level magnetizing-inductance constraint retained.

Hard evidence currently matched:
- +4 dBu / 20 Hz ~0.025% THD;
- +20 dBu / 20 Hz ~1% THD;
- settled H3-dominant / negligible-H2 symmetry;
- low-level distortion approximately quarters per octave from 20->40->80 Hz;
- stateful DC-bias/remanence behavior;
- DC bias naturally creates strong H2 rather than using an artificial even-harmonic shaper.

Numerical QA:
- RK4 reference;
- independent higher-rate midpoint cross-check added to the positive suite.

Current status:
STRONG PROVISIONAL OFFLINE IRON CANDIDATE.

Remaining blockers:
- final calibrated Jensen multi-frequency/multi-level curve extraction;
- HF parasitic / phase network;
- deterministic state recall policy;
- realtime reduction;
- aliasing / CPU QA.

## Cross-product rules now frozen

1. No hardware mode is accepted from one headline number.
2. Exact manufacturer tables outrank manual graph reads.
3. Manual graph reads retain explicit uncertainty.
4. No data point is moved to make a model fit better.
5. Numerical convergence and physical agreement are separate gates.
6. A more complex model wins only if it improves independent evidence.
7. Empirically fitted parameters are never described as undocumented hardware facts.
8. Drive calibration remains unfrozen until the corresponding physical reference is accepted.
9. Bypass remains the neutral reference; Drive=0 may retain authentic active-circuit character.
10. Mix=0 remains targeted as true dry.

## Repository scope

All work in this checkpoint is confined to:
- challanger2000/SaturatorMixFX-Final
- branch: v2.0.0-development

V1/main remains intentionally untouched.


### IRON LF-reference correction

The former ~106.55 H magnetizing-inductance value was derived by applying the -0.04 dB / 20 Hz manufacturer response directly to the transformer port.

The Jensen datasheet explicitly specifies that magnitude-response measurement as:
test circuit 1, Rs=600 Ohm.

Re-deriving the magnetizing branch with the source resistance included gives approximately:
- Lm = 144.0 H

The separate 1 kHz transformer-port quantities remain consistent:
- Zi ~13 kOhm
- voltage gain ~-2.28 dB vs manufacturer typical -2.3 dB

The magnetic candidate was therefore re-identified rather than keeping stale fitted numbers:
- c ~0.820
- KI ~40528.8 A/m per A
- KPHI re-derived from the corrected Lm.

All earlier IRON candidate numbers based on Lm ~106.55 H are superseded.
