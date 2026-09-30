# SMX-3 V2 IRON Numerical Cross-Method Gate

Date: 2026-09-30

Purpose:
verify that the provisional Jensen-matched IRON candidate is not an artifact of one integration formula.

Methods:
- RK4 candidate solver at 48 kHz;
- independent explicit midpoint/RK2 solver at 192 kHz.

Cases:
- +4 dBu / 20 Hz;
- +20 dBu / 20 Hz;
- +4 dBu / 40 Hz.

Metrics:
- total H2-H10 THD;
- H3 ratio.

Frozen tolerances:
- THD absolute residual <= 0.003 percentage-points;
- H3 absolute residual <= 0.003 percentage-points.

These are numerical-method tolerances, not hardware-specification tolerances.

The 4x higher midpoint integration rate is intentional. A lower-order, independently formulated method at higher density provides a meaningful cross-check of the lower-rate RK4 candidate used for current reference calculations.
