# SMX-3 V2 PENTODE Alias-Risk Result

Date: 2026-09-30
Workflow run: 36686601377
Conclusion: SUCCESS

## Method

Coherent high-rate physical EF86 authority.
Estimated nonlinear harmonic foldback into a 48 kHz host band for:
- 1x
- 2x
- 4x

An ideal return low-pass is assumed for oversampled candidates, so the result isolates nonlinear alias risk rather than practical filter leakage.

## Results

### 1 kHz moderate drive
- 1x: -146.66 dBc
- 2x: -154.71 dBc
- 4x: -156.62 dBc

### 1 kHz strong drive
- 1x: -137.59 dBc
- 2x: -146.10 dBc
- 4x: -156.61 dBc

### 4 kHz strong drive
- 1x: -99.79 dBc
- 2x: -160.95 dBc
- 4x: -164.12 dBc

### 8 kHz strong drive
- 1x: -52.78 dBc
- 2x: -113.14 dBc
- 4x: -159.14 dBc

### 12 kHz strong drive
- 1x: -39.59 dBc
- 2x: -79.97 dBc
- 4x: -167.26 dBc

Worst:
- 1x: ~-39.6 dBc
- 2x: ~-80.0 dBc
- 4x: ~-156.6 dBc

## Interpretation

PENTODE differs fundamentally from IRON.

Its nonlinear transfer remains strong at high audio frequencies, so physical harmonics can cross Nyquist and fold back severely.

Therefore:
- 1x is rejected for the strong-drive production path;
- 2x is a serious candidate but reaches only about -80 dBc worst-case in the current stress set;
- 4x is effectively clean in the same periodic-sine analysis.

## Combined with numerical-rate evidence

Dynamic EF86 numerical benchmark:

- 48 kHz: amplitude very accurate, HF phase ~0.50 deg worst;
- 96 kHz: plausible, HF phase ~0.10 deg worst;
- 192 kHz: strong, HF phase ~0.025 deg worst.

Both independent evidence paths therefore point in the same direction:

**4x / 192 kHz is the current strongest straightforward production candidate at a 48 kHz host.**

This is NOT yet a final oversampling decision because:
- real oversampling-filter error/latency must be measured;
- CPU p95/p99/max must be measured;
- a lower-cost 2x + targeted antialias method may be preferable if it reaches comparable residual.

Do not use 1x for the final strong-drive EF86 engine.
