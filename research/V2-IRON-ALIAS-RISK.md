# SMX-3 V2 IRON Coherent Alias-Risk Result

Date: 2026-09-30
Workflow run: 36685873987
Conclusion: SUCCESS

## Measurement correction

The first alias-risk run used a fixed 768 kHz authority rate.

At:
- 5 kHz -> 153.6 samples/cycle
- 10 kHz -> 76.8 samples/cycle

That made the final analysis window non-coherent and leaked fundamental energy
into harmonic bins.

The corrected run chooses an integer samples-per-cycle authority rate near
768 kHz for every test frequency.

The old high-frequency alias numbers are superseded.

## Corrected coherent result

+20 dBu excitation, 48 kHz host target:

| input | 1x estimated fold alias | 2x | 4x |
|---:|---:|---:|---:|
| 1 kHz | -108.40 dBc | -117.03 dBc | -127.82 dBc |
| 5 kHz | -127.58 dBc | -135.85 dBc | -143.97 dBc |
| 10 kHz | -136.02 dBc | -143.87 dBc | -151.79 dBc |

Worst current result:
- 1x: ~-108.4 dBc
- 2x: ~-117.0 dBc
- 4x: ~-127.8 dBc

## Interpretation

The physically modeled line transformer becomes rapidly more linear as
frequency rises because flux excursion falls with frequency.

Therefore its worst nonlinear alias risk is not at high audio frequencies,
unlike a frequency-independent static waveshaper.

At the currently modeled +20 dBu operating range:
- even 1x nonlinear-fold risk is already below about -108 dBc in the tested set;
- 2x/4x improve a quantity that is already extremely small.

This aligns with the physical transformer model:
- strong low-frequency magnetic nonlinearity;
- very small high-frequency nonlinear distortion.

## Architecture implication

Fixed 4x oversampling is NOT justified for IRON by the current physical
harmonic-fold evidence.

Current primary hypothesis:

- magnetic H/M state: host-rate midpoint/RK2;
- nonlinear magnetic evaluation: host rate;
- no oversampling by default unless direct waveform residual tests reveal an
  alias mechanism missed by harmonic-fold analysis.

This would be materially cheaper than V1's blanket 4x architecture.

## Remaining confirmation

Before freezing 1x:
- compare direct host-rate waveform against an ideally band-limited high-rate
  authority waveform;
- test 44.1 kHz as well as 48 kHz;
- test transients/multitone, not only periodic sine;
- measure final C++ realtime CPU and actual antialias-filter alternatives.

No oversampling factor is final until those checks pass.
