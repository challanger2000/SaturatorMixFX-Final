> SUPERSEDED NUMERICAL VALUES — 2026-09-30
>
> The numerical tables below were generated with the historical EHX-1 dynamic specimen.
> The solver infrastructure and convergence methodology remain valid, but the current
> dynamic authority has been switched to RSD-2. Re-run results under RSD-2 supersede
> these numerical values once the central reference suite completes.

# SMX-3 V2 TRI0DE Dynamic Integration Convergence

Date: 2026-09-30
Tools:
- tools/smx3_v2_ecc83_dynamic_reference.py
- tools/smx3_v2_ecc83_dynamic_convergence.py

Circuit:
EHX-1 measured 12AX7 model embedded in the documented Mullard/Philips ECC83 R-C amplifier network.

## Phase-measurement correction

The first convergence probe exposed a measurement bug in the reference tool.

The implicit trapezoid step advances the state from t=n*dt to t=(n+1)*dt and then stores out[n].
The former harmonic analysis projected out[n] against time n*dt.

That created an artificial one-sample phase advance whose angle changed with sample rate.

The phase measurement is now:
- projected on the actual stored-state times (n+1)/fs;
- reported relative to the known input projected on the same absolute time grid.

This correction changes phase reporting only. It does not alter the circuit state integration, gain or nonlinear current equations.

## Convergence matrix

### 1 kHz, 10 mVrms

| integration rate | gain | relative phase | THD |
|---:|---:|---:|---:|
| 192 kHz | 49.32338 | -176.47243 deg | 0.193274 % |
| 384 kHz | 49.32660 | -176.47341 deg | 0.193244 % |
| 768 kHz | 49.32739 | -176.47396 deg | 0.193256 % |

384 -> 768 kHz residual:
- gain: ~16.0 ppm
- phase: ~0.000551 deg
- THD: ~0.0000126 percentage-points

### 1 kHz, 0.70 Vrms

| integration rate | gain | relative phase | THD |
|---:|---:|---:|---:|
| 192 kHz | 48.23360 | -176.47991 deg | 3.873441 % |
| 384 kHz | 48.23654 | -176.47990 deg | 3.874311 % |
| 768 kHz | 48.23727 | -176.47996 deg | 3.874634 % |

384 -> 768 kHz residual:
- gain: ~15.2 ppm
- phase: ~0.000062 deg
- THD: ~0.000323 percentage-points

### 10 kHz, 10 mVrms

| integration rate | gain | relative phase | THD |
|---:|---:|---:|---:|
| 0.96 MHz | 49.91295 | +179.95550 deg | 0.514589 % |
| 1.92 MHz | 49.92631 | +179.96214 deg | 0.512441 % |
| 3.84 MHz | 49.92965 | +179.96540 deg | 0.511684 % |

1.92 -> 3.84 MHz residual:
- gain: ~66.9 ppm
- phase: ~0.003267 deg
- THD: ~0.000757 percentage-points

### 20 kHz, 10 mVrms

| integration rate | gain | relative phase | THD |
|---:|---:|---:|---:|
| 1.92 MHz | 49.76789 | +179.39972 deg | 0.295096 % |
| 3.84 MHz | 49.78119 | +179.40362 deg | 0.293473 % |
| 7.68 MHz | 49.78450 | +179.40551 deg | 0.292841 % |

3.84 -> 7.68 MHz residual:
- gain: ~66.6 ppm
- phase: ~0.001889 deg
- THD: ~0.000633 percentage-points

## Frozen numerical convergence limits

For the top two integration densities in each current matrix case:

- relative gain residual <= 250 ppm
- relative-phase residual <= 0.02 deg
- THD residual <= 0.0025 percentage-points

These are numerical-authority tolerances, not hardware-accuracy tolerances.

## Decision

PASS for aggregate numerical convergence of the current implicit-trapezoid dynamic reference.

This establishes that the current frequency-adaptive integration densities are sufficient for the tested aggregate metrics.

It does NOT yet establish:
- correctness versus a second integration formulation;
- waveform-sample residual convergence;
- Dempwolf Figure-9 laboratory waveform reproduction;
- production realtime architecture.

Next numerical gate:
cross-check the same network with an independent implicit method and measure waveform/fundamental residuals.
