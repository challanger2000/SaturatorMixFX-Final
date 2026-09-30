# SMX-3 V2 TRI0DE Integration-Method Cross-Check

Date: 2026-09-30
Primary specimen: Dempwolf/Zoelzer RSD-2 12AX7

Methods:
- implicit trapezoidal integration;
- independent implicit midpoint integration.

Both solve:
- RSD-2 measured current equations;
- Philips/Mullard ECC83 surrounding network;
- Cag/Cgk/Cak parasitic capacitances;
- the same physical-time settling protocol.

## Current RSD-2 results

Revision-11 run 36692441356:

| case | reference rate | gain residual | phase residual | THD residual |
|---|---:|---:|---:|---:|
| 1 kHz / 10 mVrms | 768 kHz | ~8.503 ppm | ~0.000000121 deg | ~0.000001004 pp |
| 1 kHz / 0.70 Vrms | 768 kHz | ~8.814 ppm | ~0.000000468 deg | ~0.000165752 pp |
| 10 kHz / 10 mVrms | 3.84 MHz | ~33.956 ppm | ~0.000000036 deg | ~0.000003051 pp |
| 20 kHz / 10 mVrms | 7.68 MHz | ~33.614 ppm | ~0.000000064 deg | ~0.000002662 pp |

pp = percentage-points.

## Frozen cross-method tolerances

- gain residual <= 100 ppm
- phase residual <= 0.001 degree
- THD residual <= 0.0005 percentage-points

## Decision

PASS for the RSD-2 offline reference.

Basic numerical-integrator credibility is no longer a TRI0DE blocker.

Remaining work concerns:
- physical grid-current/archetype choice;
- blocking/recovery;
- realtime reduction;
- aliasing;
- CPU;
- final product calibration.
