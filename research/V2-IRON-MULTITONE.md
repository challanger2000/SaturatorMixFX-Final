# SMX-3 V2 IRON Multitone / IMD Direct Residual

Date: 2026-09-30
Workflow run: 36687003819
Conclusion: SUCCESS

## Excitation

Four coherent tones:
- 100 Hz
- 1 kHz
- 5 kHz
- 11 kHz

Each component:
- +14 dBu RMS

Combined RMS:
- approximately +20 dBu.

This deliberately stresses simultaneously:
- low-frequency magnetic flux;
- hysteretic memory;
- mid/high-frequency components;
- intermodulation/foldback.

## Comparison

Candidate:
- host-rate midpoint/RK2;
- no oversampling.

Authority:
- 8x-rate RK4 physical model;
- ideally band-limited to host Nyquist before comparison.

## Result

| host rate | direct multitone residual |
|---:|---:|
| 44.1 kHz | -96.46 dB |
| 48 kHz | -97.86 dB |

Worst:
- ~-96.46 dB

Classification:
**STRONG**

## Decision

The host-rate 1x IRON hypothesis now passes:

- state-integration residual;
- coherent harmonic-fold alias analysis;
- direct periodic sine residual at 44.1 and 48 kHz;
- direct multitone/IMD residual at 44.1 and 48 kHz.

This is sufficient to reject blanket 2x/4x oversampling as the default IRON architecture.

One important non-periodic gate remains:
- transient/burst excitation.

After that, the remaining work is C++ implementation/realtime QA rather than offline model credibility.
