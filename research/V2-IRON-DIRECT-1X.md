# SMX-3 V2 IRON Direct 1x Waveform Residual

Date: 2026-09-30
Workflow run: 36686442655
Conclusion: SUCCESS

## Measurement

Candidate:
- midpoint/RK2;
- 48 kHz internal/host rate;
- no oversampling.

Authority:
- coherent high-rate RK4 physical model;
- 30-cycle magnetic settling;
- Fourier projection;
- ideal removal of physical components above the 48 kHz host Nyquist.

Therefore the residual includes:
- host-rate state-integration error;
- nonlinear alias/foldback;
- any in-band waveform error

while not penalizing the 1x implementation for legitimate analog harmonics
that a 48 kHz digital system cannot represent.

## Result

| input | direct waveform residual |
|---|---:|
| +4 dBu / 1 kHz | -87.72 dB |
| +20 dBu / 1 kHz | -89.01 dB |
| +20 dBu / 4 kHz | -101.06 dB |
| +20 dBu / 8 kHz | -96.32 dB |
| +20 dBu / 12 kHz | -92.43 dB |

Worst tested:
- approximately -87.7 dB.

Classification:
**STRONG** under the current <= -80 dB waveform-residual criterion.

## Combined architecture evidence

IRON now has three mutually consistent realtime findings:

1. midpoint/RK2 at 48 kHz matches RK4 state metrics extremely closely;
2. coherent nonlinear harmonic-fold estimate is below ~-108 dBc worst in the tested periodic-sine set;
3. direct host-rate waveform residual versus an ideal band-limited authority is below ~-87.7 dB.

This is strong evidence that fixed oversampling is unnecessary for the present
physical IRON model under the tested periodic conditions.

## Current architecture decision

Primary production hypothesis:

- H/M state integration: host-rate midpoint/RK2;
- nonlinear magnetic evaluation: host rate;
- no oversampling in default IRON path.

Do not add 2x/4x unless one of the remaining tests demonstrates a meaningful
benefit.

## Remaining freeze gates

Before declaring 1x final:
- repeat direct residual at 44.1 kHz;
- multitone/intermodulation residual;
- transient/impulse-style magnetic excitation;
- C++ implementation CPU p95/p99/max;
- denormal/subnormal and reset/lifecycle QA.

If these remain controlled, oversampling should be omitted from IRON entirely.
