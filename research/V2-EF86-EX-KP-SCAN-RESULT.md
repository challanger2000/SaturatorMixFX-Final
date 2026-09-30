# SMX-3 V2 EF86 EX x KP Curvature Scan Result

Date: 2026-09-30
Workflow run: 36684266121
Conclusion: SUCCESS; KP REOPENING DOES NOT SOLVE THE REMAINING GRAPH-D RESIDUAL

## Purpose

After dynamic cathode/screen/output modeling failed to explain the provisional
Graph-D low-level THD residual, the existing equation-family sharpness
parameter KP was reopened.

Scanned:
- EX = 1.36 .. 1.44
- KP = 140 / 180 / 220 / 260 / 320

For every candidate:
- VCT was re-solved so gm/Ia remained exact;
- KG1 was derived so Ia=3.0 mA remained exact;
- S0 was derived so Ig2=0.6 mA remained exact.

No candidate could win by moving the local device anchor.

## Strong-gate eligibility

Required:
- Graph A NRMS <= 1 sigma;
- Graph B NRMS <= 1 sigma;
- max Ik error <= 7%;
- max gain error <= 5%;
- max exact Vo@5% error <= 5%.

Only KP=220 candidates survived across the tested EX band.

Representative eligible candidates:

| EX | KP | Graph A | Graph B | max Ik err | max gain err | max Vo5 err | Graph-D THD NRMS |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.36 | 220 | 0.502 | 0.489 | 5.20% | 3.97% | 3.62% | 2.35 sigma |
| 1.38 | 220 | 0.507 | 0.490 | 5.12% | 3.98% | 3.59% | 2.38 sigma |
| 1.40 | 220 | 0.514 | 0.491 | 5.04% | 3.98% | 3.56% | 2.42 sigma |
| 1.42 | 220 | 0.523 | 0.492 | 4.97% | 4.08% | 3.53% | 2.46 sigma |
| 1.44 | 220 | 0.534 | 0.493 | 4.90% | 4.21% | 3.50% | 2.50 sigma |

The numerical ranking differences are tiny compared with the uncertainty of
the manually digitized Graph-D distortion curve.

## Decision

DO NOT change the current EF86 model based on this scan.

Evidence:
- the independently fitted Stage-1 KP (~215.8) is already essentially at the
  only viable region found by this scan;
- changing KP does not materially improve the remaining Graph-D discrepancy;
- EX=1.40 remains centered in the successful range and already has stronger
  exact-envelope evidence.

Current preferred static candidate therefore remains approximately:

- EX = 1.40
- KP = original Stage-1 value ~215.8 (220 in coarse scans)
- exact Ia/gm/Ig2 calibration
- Stage-2C plate knee

## Graph-D caution

The current low-output Graph-D distortion points are manual raster reads.

Visual reinspection of the original Philips graph shows that the low-level
curves are difficult to separate reliably and the existing 10/20 V estimates
may be biased low.

Therefore:
- do not add another model degree of freedom to chase those points;
- do not promote a different EX/KP candidate merely for lower Graph-D score;
- retain Graph D as provisional shape evidence until calibrated extraction is available.

This prevents overfitting the hardware model to digitization error.
