# SMX-3 V2 Hardware-Model Promotion Criteria

Date: 2026-09-30

This document freezes selection criteria before the currently running model-form comparisons complete.

## TRI0DE measured-specimen selection

Candidates currently under direct comparison:
- Dempwolf/Zoelzer EHX-1
- Dempwolf/Zoelzer RSD-2

Do not select a specimen because it is:
- louder;
- more distorted;
- subjectively warmer;
- the specimen historically used first.

Primary manufacturer cross-check:
Mullard/Philips ECC83 250 V / 100 kOhm / 1.5 kOhm / 330 kOhm loaded amplifier.

Selection order:
1. idle cathode current agreement;
2. documented loaded small-signal gain agreement;
3. manufacturer 26 Vrms / distortion behavior;
4. dynamic solver convergence/stability;
5. frequency-dependent gain/phase;
6. harmonic progression;
7. grid-current/domain behavior.

Current static evidence favors RSD-2:
- Ik error ~-2.86%;
- loaded gain error ~+5.52%;
- distortion at 26 Vrms ~3.70% versus Mullard ~3.9%.

EHX-1 remains important as an independent measured-specimen cross-check.

A dynamic mismatch may prevent RSD-2 promotion, but lower/higher subjective saturation is not a selection criterion.

## PENTODE Stage-3 model-form selection

Frozen prior stages:
- Stage-1 current/screen transfer surface;
- Stage-2C minimal plate-knee/static candidate.

Current residual:
- Stage-2C exact Vo@5% envelope is still low by roughly 5-10% across the manufacturer supply sweep;
- provisional Graph-D input/output trajectory is substantially closer than the older compact surrogate.

Stage-3 hypothesis:
Philips Graph B visibly indicates that the plate knee changes with control-grid operating condition.

First candidate extension:
KNEE_eff(Vg1) = K0 * exp(BK * (Vg1 + 2 V))

with normalization at Va=250 V so Stage-1 Graph-A behavior is preserved at its reference plate voltage.

Promotion requires:
1. lower exact Vo@5% envelope error than Stage-2C;
2. no material regression in amplifier Ik/gain;
3. no material regression in Graph-B residual;
4. no arbitrary per-supply correction;
5. no parameter that exists only as an output gain trim.

If the coarse sweep does not materially improve all three domains, reject the grid-dependent-knee hypothesis.

## IRON promotion

Current strong provisional candidate already clears:
- exact +4 dBu / 20 Hz THD anchor;
- exact +20 dBu / 20 Hz / 1% THD anchor;
- H3-dominant settled parity;
- Jensen/Whitlock low-level frequency-law diagnostic.

Next promotion requires:
- independent numerical-method agreement;
- calibrated manufacturer curve family;
- HF/phase parasitic model;
- DC-bias/remanence validation.

Do not move the IRON candidate into production DSP merely because the exact two-point fit is excellent.
