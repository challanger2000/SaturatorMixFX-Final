# SMX-3 V2 EF86 Dynamic Integration-Method Cross-Check

Date: 2026-09-30
Workflow run: 36685298567
Conclusion: SUCCESS

## Methods

Compared on the same EX=1.40 EF86 + Philips dynamic network:

- implicit trapezoidal integration;
- independent implicit midpoint integration.

Both use:
- the same physical-time warmup;
- the same nonlinear current equations;
- the same documented cathode/screen/output network;
- the same reduced Philips terminal capacitance model.

## Results

| case | integration rate | gain residual | phase residual | THD residual |
|---|---:|---:|---:|---:|
| 1 kHz / 10 mVrms | 768 kHz | ~8.48 ppm | ~0.00000005 deg | ~0.00000290 pp |
| 1 kHz / 180 mVrms | 768 kHz | ~8.53 ppm | ~0.00000008 deg | ~0.00002995 pp |
| 10 kHz / 10 mVrms | 3.84 MHz | ~33.83 ppm | ~0.00000078 deg | ~0.00000926 pp |
| 20 kHz / 10 mVrms | 7.68 MHz | ~33.51 ppm | ~0.00000094 deg | ~0.00000765 pp |

pp = percentage-points.

## Decision

PASS.

The dynamic EF86 offline reference is no longer supported only by one
integration formula.

Two independent implicit second-order formulations converge to effectively
the same solution over:
- small-signal midband;
- materially nonlinear midband;
- 10 kHz;
- 20 kHz.

Therefore the remaining PENTODE uncertainties are physical/modeling questions,
not basic numerical-integrator credibility.

## Current dynamic authority status

PROMOTE to:
**EF86 OFFLINE DYNAMIC AUTHORITY CANDIDATE**

Still not production DSP because:
- exact input Rg1 value is not sourced;
- Graph-D distortion points remain provisional;
- realtime-rate reduction is not yet measured;
- aliasing/CPU are not yet measured.

The current direct-g1 reference is nevertheless numerically strong enough to
judge future realtime surrogates and integration reductions.
