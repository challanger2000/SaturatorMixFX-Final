# SMX-3 V2 Hardware Reference Checkpoint — 2026-09-30

Status: current authoritative research checkpoint. Not a release declaration.

## TRI0DE

Current authority:
- Dempwolf/Zoelzer RSD-2 measured 12AX7 specimen law;
- documented Philips/Mullard ECC83 surrounding RC network;
- full dynamic capacitance model;
- physical-time settling;
- corrected relative phase;
- positive-grid domain handled according to Dempwolf's measured range.

Validated:
- operating point / loaded gain;
- dynamic numerical convergence;
- trapezoid vs implicit-midpoint agreement;
- measured-domain gate;
- strong-overload grid-current sensitivity.

4 Vrms / 1 kHz dynamic sensitivity:
- RSD-1 / RSD-2 / EHX-1 / Danyuk grid-current laws recover to the 10 mV criterion in approximately 183-187 ms;
- complete AC-coupled stage compresses specimen differences strongly.

Decision:
- retain coherent RSD-2 specimen;
- do not synthesize a hybrid/consensus grid-current law;
- other measured laws remain uncertainty bounds for Drive 75-100%.

Current TRI0DE status:
STRONG OFFLINE REFERENCE.
Production still needs realtime reduction, aliasing, CPU and final Drive mapping.

## PENTODE

Primary authority:
Philips EF86 manufacturer data.

Current staged architecture:
- Stage 1: plate-surface identification;
- Stage 2: joint static/device/amplifier fit;
- Stage 3: localized low-Va / large-signal correction.

Evidence domains:
- exact device Ia / Ig2 / gm;
- exact circuit-1 DC current / gain sweep;
- Graph A screen families;
- Graph B plateau;
- corrected Graph B 20/40/60/80 V knee region;
- exact 5% THD output envelope 200..400 V;
- refined Graph D compression/distortion trajectory.

Stage-3 cross-domain status:
- exact 5% envelope worst error approximately 4.1%;
- corrected Graph-B knee remains inside the provisional cross-domain gate;
- Stage-3 does not materially damage Graph A / plateau behavior.

Rejected:
- third-party CC0 final-reference use;
- generalized compact beta surrogate as final model;
- unrestricted overparameterized static fits;
- static-only knee fit without large-signal terms.

Current PENTODE status:
STRONG PROVISIONAL STATIC/LARGE-SIGNAL REFERENCE FAMILY.
Dynamic capacitance/network, aliasing/realtime and final Drive mapping remain.

## IRON

Primary hardware archetype:
Jensen JT-11P-1.

### Corrected test-condition basis

Important correction:
Jensen's 20 Hz / 20 kHz response and DLP test explicitly use Rs=600 Ohm.

The former ~106.55 H derivation omitted this source resistance and is superseded.

A lossless one-inductor interpretation gives:
- effective lossless-equivalent Lm ≈ 143.999434 H.

This 144 H value is a LOSSLESS-EQUIVALENT BASELINE, not a unique physical magnetizing inductance.

### Corrected nonlinear magnetic candidate

Refit on corrected 144 H baseline:
- Jiles-Atherton c = 0.814375;
- KI = 40891.896218061 A/m per A;
- KPHI ≈ 4.88989141336e-7.

High-resolution anchors:
- +4 dBu / 20 Hz THD ≈ 0.0261%;
- +20 dBu / 20 Hz THD ≈ 1.0000%;
- settled baseline remains overwhelmingly H3-dominant.

Extended QA on corrected candidate:
- RK4 vs midpoint cross-method residuals essentially negligible;
- midpoint at 48 kHz remains STRONG versus 192 kHz RK4;
- DC pre-bias naturally creates strong H2;
- symmetric AC cycling returns to deterministic H3-dominant orbit.

### Phase / core-loss finding

Pure-lossless magnetic skeleton fails Jensen DLP:
- linear HF/magnitude-fit topology worst DLP ≈ 4.39°;
- magnetic-only quasi-static Jiles-Atherton candidate worst DLP ≈ 3.83°;
- Jensen maximum is ±2° and typical low-frequency deviation is about +0.6°.

Therefore the missing behavior is not simply more leakage-L or capacitance.

### Loss-aware Jensen small-signal target

A passive reduced target including magnetic loss was identified using:
- documented Rp/Rs/RL;
- documented 98 pF / 110 pF shield capacitances;
- effective magnetic-loss R-L branch;
- leakage inductance;
- effective additional shunt/interwinding capacitance.

Effective research target:
- Lmag ≈ 922.4107 H;
- Rmag ≈ 38.991 kOhm;
- Llk ≈ 2.7504 mH;
- effective Cx ≈ 1.15485 nF.

These are EFFECTIVE FIT PARAMETERS, not manufacturer construction values.

Manufacturer agreement:
- 1 kHz transformer gain ≈ -2.27845 dB;
- 1 kHz input impedance ≈ 12.939 kOhm;
- 20 Hz relative response ≈ -0.039994 dB;
- 20 kHz ≈ -0.049900 dB;
- 95 kHz ≈ -2.99879 dB;
- DLP min ≈ -0.134°;
- DLP max ≈ +0.598°.

This target passes the selected Jensen magnitude, impedance and phase constraints simultaneously.

Current IRON conclusion:
- nonlinear Jiles-Atherton state model is strong for THD/hysteresis/remanence;
- quasi-static core alone misses low-field complex permeability / dynamic loss;
- next reference stage is a causal dynamic-loss augmentation that approaches the loss-aware target without double-counting hysteresis.

Current IRON status:
STRONG NONLINEAR MAGNETIC REFERENCE + STRONG SMALL-SIGNAL LOSS TARGET,
NOT YET A SINGLE UNIFIED PRODUCTION MODEL.

## Frozen cross-product rules

1. Exact manufacturer tables outrank graph digitization.
2. Graph digitization retains explicit uncertainty.
3. No source point is moved to improve a model.
4. Numerical convergence and hardware agreement are separate gates.
5. More complexity is accepted only when it improves independent evidence.
6. Fitted parameters are never presented as undocumented hardware facts.
7. Every manufacturer value carries its source/load/test-circuit conditions.
8. Drive mapping remains unfrozen until each physical reference is accepted.
9. Bypass is neutral; active Drive=0 may retain genuine physical baseline behavior.
10. Mix=0 target remains true dry.

## Repository scope

Repository:
challanger2000/SaturatorMixFX-Final

Development branch:
v2.0.0-development

V1/main remains intentionally untouched.
