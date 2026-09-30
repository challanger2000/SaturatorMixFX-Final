# SMX-3 V2 IRON Additive Linear Correction Target

Date: 2026-09-30
Status: realtime-reduction preparation

Preferred offline architecture:

    y = L_Jensen{x} + [y_JA - L_JA{x}]

Equivalent runtime form:

    y = y_JA + C{x}

with:

    C = L_Jensen - L_JA

This avoids implementing two full linear paths.

The correction target is complex and frequency-dependent. It must therefore be
fit as a stable causal linear filter.

## Procedure

- measure L_JA at very low level with the actual stateful JA solver;
- evaluate L_Jensen analytically from the validated loss-aware target;
- sample C densely over 20 Hz..20 kHz.

## Realtime acceptance

A fitted C filter must be judged on the FINAL corrected transfer, not on C
magnitude alone.

Required final residuals:
- magnitude versus Jensen target <= 0.01 dB through 20 Hz..20 kHz;
- DLP versus Jensen target <= 0.1 degree preferred, <=0.25 degree maximum;
- no unstable poles;
- no discontinuity when sample rate changes outside process;
- coefficients recalculated for 44.1/48/88.2/96/176.4/192 kHz;
- no allocations or coefficient fitting inside process().
