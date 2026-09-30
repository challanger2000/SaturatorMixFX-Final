# SMX-3 V2 IRON DC-Bias / Remanence Result

Date: 2026-09-30
Workflow run: 36664877378
Conclusion: SUCCESS

## Purpose

Test whether the provisional Jiles-Atherton/Jensen candidate reproduces the qualitative magnetic-history behavior documented by Jensen/Whitlock:

- demagnetized baseline -> predominantly H3;
- DC magnetic bias -> strong even-order/H2 content;
- after bias removal and symmetric AC cycling -> return toward deterministic H3-dominant periodic state.

## Baseline

20 Hz / +4 dBu after 40 AC cycles:

- THD ~0.025537%
- H2 ~0.0000012%
- H3 ~0.025146%
- H5 ~0.004063%
- H2/H3 ~-86.4 dB

This is strongly odd/H3-dominant.

## 10 mV DC pre-bias for 1 second

First four AC cycles after bias removal:
- THD ~0.724%
- H2 ~0.510%
- H3 ~0.323%
- H2/H3 ~+3.96 dB

After 40 additional symmetric AC cycles:
- THD ~0.025537%
- H2 effectively zero
- H3 ~0.025146%
- H2/H3 ~-95.8 dB

## 50 mV DC pre-bias for 1 second

First four AC cycles:
- THD ~0.852%
- H2 ~0.598%
- H3 ~0.384%
- H2/H3 ~+3.85 dB

After 40 additional AC cycles:
- THD ~0.025537%
- H2 effectively zero
- H3 ~0.025146%
- H2/H3 ~-94.4 dB

## 100 mV DC pre-bias for 1 second

First four AC cycles:
- THD ~1.012%
- H2 ~0.708%
- H3 ~0.460%
- H2/H3 ~+3.74 dB

After 40 additional AC cycles:
- THD ~0.025537%
- H2 effectively zero
- H3 ~0.025146%
- H2/H3 ~-92.9 dB

## Interpretation

PASS.

The same magnetic model that matches Jensen's exact low-/high-level THD anchors also exhibits the expected stateful asymmetry:

- without DC history it is nearly even-harmonic free;
- DC magnetic bias creates strong H2;
- immediately after bias removal H2 can exceed H3;
- continued symmetric excitation returns to the deterministic H3-dominant periodic orbit.

No separate even-harmonic waveshaper is used.

## Consequence

The provisional IRON model now has independent evidence for:

1. documented electrical skeleton;
2. derived low-level magnetizing inductance;
3. exact +4 dBu / 20 Hz THD;
4. exact +20 dBu / 20 Hz / 1% THD;
5. H3-dominant demagnetized harmonic parity;
6. Jensen/Whitlock low-level frequency law;
7. numerical RK4 vs midpoint agreement;
8. DC-bias-induced even-order distortion;
9. deterministic recovery under symmetric excitation.

This materially strengthens its status as the current offline magnetic authority candidate.

Still required before production:
- calibrated full Jensen curve extraction;
- HF/leakage/parasitic network;
- explicit project-state policy for magnetic state;
- realtime reduction;
- aliasing and CPU QA.
