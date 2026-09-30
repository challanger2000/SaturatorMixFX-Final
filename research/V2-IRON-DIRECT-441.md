# SMX-3 V2 IRON Direct 44.1 kHz Waveform Result

Date: 2026-09-30
Workflow run: 36686791432
Conclusion: SUCCESS

## Candidate

- host-rate midpoint/RK2;
- 44.1 kHz;
- no oversampling.

Authority:
- coherent high-rate RK4;
- ideally band-limited to the 44.1 kHz Nyquist band before comparison.

## Result

| excitation | residual |
|---|---:|
| +4 dBu / 900 Hz | -86.47 dB |
| +20 dBu / 900 Hz | -88.04 dB |
| +20 dBu / 3.675 kHz | -100.16 dB |
| +20 dBu / 7.35 kHz | -95.59 dB |
| +20 dBu / 11.025 kHz | -91.70 dB |

Worst:
- ~-86.47 dB

Classification:
**STRONG**

## Combined sample-rate conclusion

Periodic sine direct-waveform residual:

- 44.1 kHz: <=~-86.5 dB worst tested
- 48 kHz: <=~-87.7 dB worst tested

This materially strengthens host-rate 1x IRON.

Remaining before final architecture freeze:
- multitone/IMD direct residual;
- transient/burst residual;
- final C++ realtime and denormal/lifecycle QA.
