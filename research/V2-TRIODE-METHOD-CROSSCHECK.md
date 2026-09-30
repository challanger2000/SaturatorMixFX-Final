# SMX-3 V2 TRI0DE Integration-Method Cross-Check

Date: 2026-09-30

Methods:
- implicit trapezoidal integration;
- independent implicit midpoint integration.

Both solve the same:
- Dempwolf/Zoelzer EHX-1 current equations;
- Philips/Mullard ECC83 surrounding network;
- Cag/Cgk/Cak parasitic capacitances.

## Results at high reference density

| case | rate | gain residual | phase residual | THD residual |
|---|---:|---:|---:|---:|
| 1 kHz / 10 mVrms | 768 kHz | ~8.38 ppm | ~0.00000042 deg | ~0.00000090 pp |
| 1 kHz / 0.70 Vrms | 768 kHz | ~8.36 ppm | ~0.00000020 deg | ~0.000104 pp |
| 10 kHz / 10 mVrms | 3.84 MHz | ~33.24 ppm | ~0.000000014 deg | ~0.0000168 pp |
| 20 kHz / 10 mVrms | 7.68 MHz | ~33.34 ppm | ~0.000000040 deg | ~0.0000093 pp |

pp = percentage-points.

## Frozen cross-method tolerances

- gain residual <= 100 ppm
- phase residual <= 0.001 degree
- THD residual <= 0.0005 percentage-points

## Decision

PASS.

The two independent second-order implicit formulations converge to effectively the same aggregate solution over:
- low-level operation;
- materially nonlinear operation;
- 10 kHz;
- 20 kHz.

This materially strengthens the dynamic TRI0DE offline authority.

The remaining TRI0DE blockers are no longer basic numerical-integrator credibility. They are now primarily:
- operating-domain diagnostics (grid current / Va<20 V);
- frozen multi-frequency/multi-level fixture matrix;
- realtime reduction;
- aliasing/CPU comparison;
- final product Drive calibration.

Dempwolf Figure-9 direct waveform residual remains intentionally excluded because the paper does not publish the numerical component values of its specific laboratory Figure-8 amplifier.
