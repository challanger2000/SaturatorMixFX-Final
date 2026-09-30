# SMX-3 V2 Level Calibration

Status: provisional physical-level calibration
Purpose: define digital-to-hardware excitation before production DSP mapping

## Important terminology

There is no existing 125A Engineering repository rule that fixes a dBFS <-> dBu calibration.

Therefore the values below are an SMX-3 V2 product calibration, not a claim of universal studio standard.

## External nominal reference

Provisional product convention:

- nominal DAW alignment signal: -18 dBFS sine amplitude
- corresponding conceptual external hardware level: +4 dBu
- +4 dBu = 1.2283 Vrms

This is used only to make the modeled hardware levels understandable and reproducible.

## TRI0DE input pad

The selected ECC83 reference becomes strongly nonlinear if the full +4 dBu line signal is applied directly to the control grid.

A realistic saturator therefore requires input attenuation before the modeled common-cathode grid.

Choose Drive=0 grid target:

- approximately 0.10 Vrms at the nominal +4 dBu external level.

Required voltage ratio:

0.10 / 1.2283 = 0.08141

or approximately:

-21.79 dB input attenuation.

This attenuation is part of the modeled device gain staging, not post-hoc harmonic compensation.

## TRI0DE measured operating ladder

From the frozen EHX-1/Mullard large-signal reference:

| grid Vin RMS | relative to 0.10 Vrms | approximate THD | interpretation |
|---:|---:|---:|---|
| 0.10 V | 0 dB | 0.43 % | baseline active hardware character |
| 0.20 V | +6.02 dB | 0.88 % | gentle saturation |
| 0.30 V | +9.54 dB | 1.34 % | musical saturation |
| 0.50 V | +13.98 dB | 2.39 % | clearly saturated |
| 0.70 V | +16.90 dB | 3.73 % | strong |
| 1.00 V | +20.00 dB | 6.55 % | heavy / grid current begins to matter |
| 1.50 V | +23.52 dB | 13.99 % | extreme |
| 2.00 V | +26.02 dB | 20.30 % | very extreme |

This produces a physically meaningful Drive range of approximately:

0 dB to +26 dB additional modeled input gain.

Notably, V1 already used a nominal 0..24 dB Drive range, so V2 can retain a familiar macro span while replacing the arbitrary waveshaper behavior with actual circuit excitation.

## Proposed Drive macro

Drive normalized d in [0,1].

Physical target:
- d=0 -> +0 dB above the Drive-0 grid reference;
- d=1 -> approximately +26 dB.

The mapping need not be linear in d.

Desired control feel:
- 0%: active baseline hardware character, no extra drive;
- 20-50%: useful musical saturation;
- 50-75%: clearly nonlinear;
- 75-100%: strong/extreme, including positive-grid-current operation.

The exact curve is to be derived from measured THD/crest/gain progression rather than copied from V1 shapeDrive().

## Model-specific calibration

Do NOT force TRI0DE, PENTODE and IRON to share identical internal voltage/current excitation merely because one Drive knob selects all modes.

Instead:

1. define one external conceptual line level;
2. give each hardware model its physically justified input network / attenuation;
3. map the same normalized Drive macro to a comparable *musical progression* while preserving each circuit's real operating units.

This means:
- TRI0DE Drive can map to grid excitation voltage;
- PENTODE Drive can map to the selected EF86 input-circuit excitation;
- IRON Drive maps to transformer input dBu / flux linkage.

The UI macro is common; the underlying physical units are model-specific.

## IRON calibration anchor

IRON has unusually clean nominal behavior by design.

Jensen reference:
- +4 dBu / 20 Hz -> ~0.025% THD
- +20 dBu / 20 Hz -> ~1% THD

Thus a 16 dB hardware-level increase changes the low-frequency magnetic core from very clean to clearly nonlinear.

For SMX-3 creative use, Drive above the documented +20 dBu reference may be permitted only after:
- offline magnetic model remains stable;
- extrapolation is explicitly classified;
- extreme mode does not rely on unidentified/unphysical model regions.

## PENTODE calibration

PENTODE calibration is intentionally not frozen yet.

It waits for the accepted EF86 large-signal reference because the simple six-parameter model has already been rejected for failing the full manufacturer 5%-THD output envelope.

## No auto-level hidden in physical reference

Hardware-reference measurements are made without concealed level matching.

For listening comparisons, a separate measured output compensation may be applied.

The production Output parameter remains explicit and distinct from Drive calibration.
