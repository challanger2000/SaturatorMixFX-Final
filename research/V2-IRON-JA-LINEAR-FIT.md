# SMX-3 V2 IRON JA Small-Signal One-Pole Fit

Date: 2026-09-30
Status: realtime reduction experiment

Hypothesis:
the current JA small-signal transfer can be represented over the audio band as:

    H_JA(s) = G * s / (s + 2*pi*fc)

Reason:
measured JA phase approximately halves when frequency doubles at low audio
frequencies while magnitude remains nearly flat.

If accepted, realtime unified IRON becomes inexpensive:

    output = JA_stateful_output
             + Jensen_linear_target(input)
             - one_pole_JA_linear(input)

The one-pole fit is accepted only if:
- worst magnitude residual <= 0.01 dB;
- worst phase residual <= 0.25 degree

over the frozen 20 Hz..20 kHz fixture set.

If it fails, move to two poles; do not loosen the tolerance to preserve the
one-pole hypothesis.
