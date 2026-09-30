# SMX-3 V2 TRI0DE Practical-Rate Numerical Result

Date: 2026-09-30
Workflow run: 36686485899
Conclusion: SUCCESS

## Purpose

Measure only discretization/integration error of the full dynamic ECC83 MNA
reference at practical internal rates.

Aliasing is intentionally excluded from this conclusion.

The physical model includes:
- nonlinear EHX-1 12AX7 current law;
- documented Philips/Mullard common-cathode network;
- Cak/Cgk/Cag interelectrode capacitances;
- cathode/output dynamics.

## Corrected method

High-frequency total THD is not used as a pure numerical-rate metric because
different internal sample rates expose different harmonic counts and alias
paths.

Coherent fundamentals are used for gain/phase.
THD residual is only scored in low-frequency cases where comparable harmonics
fit comfortably below Nyquist.

## Representative results

### 1 kHz / 0.70 Vrms

| internal rate | gain residual | phase residual | THD residual |
|---:|---:|---:|---:|
| 48 kHz | 1262 ppm | 0.00532 deg | 0.01435 pp |
| 96 kHz | 312 ppm | 0.00132 deg | 0.00353 pp |
| 192 kHz | 75 ppm | 0.000315 deg | 0.000819 pp |
| 384 kHz | 15 ppm | 0.000063 deg | 0.000163 pp |

Midband nonlinearity converges reasonably quickly.

### 8 kHz / low level

| internal rate | gain residual |
|---:|---:|
| 48 kHz | ~93078 ppm = 9.31% |
| 96 kHz | ~22928 ppm = 2.29% |
| 192 kHz | ~5695 ppm = 0.57% |
| 384 kHz | ~1406 ppm = 0.141% |
| 768 kHz | ~335 ppm = 0.0335% |

### 12 kHz / low level

| internal rate | gain residual | phase residual |
|---:|---:|---:|
| 48 kHz | ~214595 ppm = 21.46% | 0.191 deg |
| 96 kHz | ~51921 ppm = 5.19% | 0.0409 deg |
| 192 kHz | ~12862 ppm = 1.286% | 0.00988 deg |
| 384 kHz | ~3192 ppm = 0.319% | 0.00244 deg |
| 768 kHz | ~781 ppm = 0.0781% | 0.000589 deg |

Current classification:
- 48 kHz: WEAK
- 96 kHz: WEAK
- 192 kHz: WEAK under strict full-band authority tolerance
- 384 kHz: PLAUSIBLE
- 768 kHz: STRONG

## Interpretation

This is NOT evidence that TRI0DE needs 16x oversampling for aliasing.

It is evidence that directly discretizing the full physical capacitive MNA
network with the current second-order implicit step is expensive to converge
at high audio frequencies.

The key mechanism is consistent with triode physics:
- Cag is material;
- Miller multiplication couples the plate swing back to the input;
- tiny pF capacitors coexist with much slower cathode/coupling states;
- the continuous circuit spans a wide stiffness/time-scale range.

Blindly solving the full MNA at 16x would be a poor realtime architecture.

## Production architecture decision

REJECT:
- brute-force full dynamic MNA at fixed 16x as the primary production plan.

PREFER:
- preserve the validated nonlinear tube current law;
- derive a reduced/exact discrete representation for the linear capacitive
  subnetwork;
- or use a suitable WDF/state-space decomposition;
- then compare that reduced realtime model directly against the full MNA
  authority.

Only after that numerical reduction is proven should oversampling be selected
for alias control.

## Required next TRI0DE work

1. separate nonlinear current equations from the linear C/R network;
2. derive an exact/bilinear/state-space discrete linear network at host/2x/4x;
3. solve the nonlinear coupling with minimal iteration;
4. compare waveform/gain/phase against the high-rate MNA authority;
5. then measure physical harmonic-fold aliasing;
6. choose oversampling from alias + CPU evidence, not from current MNA stiffness.

The high-rate offline MNA remains the reference, not the realtime design.
