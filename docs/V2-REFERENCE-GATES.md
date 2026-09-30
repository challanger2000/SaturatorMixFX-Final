# SMX-3 V2 Reference Gates

Date: 2026-09-30

This is the current authority/status map for the three hardware modes.
It supersedes informal interpretations of older intermediate research files.

## TRI0DE

Primary tube evidence:
- Dempwolf/Zoelzer measured EHX-1 12AX7 specimen model.

Circuit archetype:
- Mullard ECC83 cathode-biased R-C amplifier family.

Current status:
REFERENCE SPECIMEN ACCEPTED FOR OFFLINE DEVELOPMENT.
PRODUCTION DSP NOT YET ACCEPTED.

Established:
- measured current-equation parameter set;
- grid-current model;
- idle operating point in selected 250 V / 100 kOhm / 1.5 kOhm circuit;
- published parasitic capacitance values;
- loaded amplifier comparison against Mullard;
- documented specimen-vs-average differences.

Remaining blockers:
- dynamic circuit with Cag/Cgk/Cak;
- cathode/output network values frozen from an explicit documented circuit;
- reproduce Dempwolf dynamic waveform cases;
- harmonic spectrum versus level/frequency;
- oversampling/aliasing/realtime solver comparison.

Important:
do not force EHX-1 to Mullard average values with arbitrary trims.

## PENTODE

Primary hardware authority:
- Philips EF86 4-Apr-1956 characteristic curves and circuit tables.

Secondary cross-check:
- later Philips handbook edition.

Current compact candidate:
- generalized Koren-style surrogate with empirical beta knee exponent.

Current status:
LOCAL PROVISIONAL SURROGATE ONLY.
NOT FINAL HARDWARE REFERENCE.
NOT PRODUCTION DSP.

Full Philips 5%-THD supply-sweep recheck shows the surrogate remains close at 200-250 V but increasingly underestimates the documented output envelope at 300-400 V (worst case about -15.4% at 400 V).

Established:
- device-point Ia/Ig2/gm near Philips anchor;
- self-biased circuit Ik/gain sweep reasonably close;
- exact 50 Vrms / 5% large-signal endpoint closely reproduced;
- coarse out-of-fit plate-curve validation acceptable.

Remaining blockers:
- calibrated plate-curve digitization, especially low-Va knee;
- calibrated graph-D Vi/Vo/distortion trajectory;
- Vg2-dependent transfer-family validation;
- offline manufacturer-data current surface;
- dynamic capacitances/screen behavior;
- aliasing/realtime comparison.

Important:
beta is EMPIRICALLY TUNED TO DOCUMENTED MEASUREMENTS, not a physical EF86 constant.

## IRON

Primary hardware target:
- Jensen JT-11P-1 line input transformer.

Primary magnetic-model family candidate:
- stateful Jiles-Atherton / related magnetic-state formulation.

Current status:
LINEAR SKELETON ACCEPTED.
NONLINEAR HARDWARE MODEL NOT YET ACCEPTED.
NO PRODUCTION DSP CANDIDATE YET.

Established:
- DCR/load explain ~13 kOhm input impedance and ~-2.3 dB insertion gain;
- effective low-level magnetizing inductance ~106.55 H from 20 Hz response;
- exact +4/+20 dBu 20 Hz THD anchors;
- exact approximately quadratic THD growth diagnostic;
- Jiles-Atherton solver produces deterministic hysteresis/remanence;
- unmodified DAFx example magnetic-loop shape rejected as Jensen fit;
- single-capacitor HF model rejected;
- leakage-L/C magnitude fit shown non-identifiable;
- DLP phase constraint added.

Remaining blockers:
- calibrated Jensen THD-curve extraction;
- fit magnetic shape to low- and high-level anchors simultaneously;
- harmonic parity / H3 dominance evaluation at zero DC bias;
- minor-loop/remanence behavior constrained without excessive low-level loss;
- identify an HF parasitic network using magnitude + phase evidence;
- realtime solver/stability/aliasing/CPU comparison.

Important:
do not call any current magnetic parameter set a Jensen clone.

## Production-DSP entry gate

No V2 character engine is permitted to replace V1 production code until its mode has:

1. an accepted offline reference;
2. a frozen multi-domain fixture set;
3. explicit error metrics/tolerances;
4. a realtime candidate compared against that reference;
5. aliasing and CPU evidence.

At present:
- TRI0DE: offline reference specimen available; dynamic reference incomplete.
- PENTODE: strong surrogate exists; manufacturer-data reference incomplete.
- IRON: linear reference available; nonlinear reference incomplete.

Therefore production DSP replacement remains intentionally blocked.
