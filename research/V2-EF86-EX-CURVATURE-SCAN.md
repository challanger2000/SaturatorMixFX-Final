# SMX-3 V2 EF86 EX Curvature Scan

Date: 2026-09-30
Workflow run: 36664935825
Conclusion: SUCCESS — strong Stage-3 direction identified

## Method

Only the plate-current transfer exponent EX was scanned.

For every EX candidate:
- VCT was solved so gm/Ia at the Philips device point remained exactly 2/3 per volt;
- KG1 was derived so Ia remained exactly 3.0 mA;
- S0 was derived so Ig2 remained exactly 0.6 mA.

Therefore candidates could not win by changing the local operating-point gain/current.

Stage-2C plate knee remained fixed.

## Result

Best coarse candidate:
- EX = 1.40
- VCT ≈ 0.609404
- KG1 ≈ 1733.517
- S0 ≈ 1.15372e-4

Manufacturer-surface quality:
- Graph A NRMS ≈ 0.516 sigma
- Graph B NRMS ≈ 0.483 sigma

Amplifier:
- max Ik error ≈ 5.10%
- max small-signal gain error ≈ 3.74%

Exact Philips Vo@5% envelope:
- worst error only ≈ 3.51%

| Vb | model Vo@5% | Philips | error |
|---:|---:|---:|---:|
| 200 V | 40.075 V | 40 V | +0.19% |
| 250 V | 51.756 V | 50 V | +3.51% |
| 300 V | 62.988 V | 64 V | -1.58% |
| 350 V | 73.915 V | 75 V | -1.45% |
| 400 V | 84.619 V | 87 V | -2.74% |

## Interpretation

This strongly supports the revised diagnosis:

The remaining Stage-2C large-signal error was primarily CONTROL-GRID TRANSFER CURVATURE, not an insufficient plate-voltage knee.

Changing EX while preserving the exact local Ia/gm/Ig2 device anchor:
- dramatically improves the full 200-400 V 5%-THD envelope;
- preserves Graph A/B within current digitization uncertainty;
- preserves small-signal gain reasonably well.

This is substantially stronger evidence than adding a free output/compression trim.

## Remaining issue

The exact-Ig2 calibration causes the circuit cathode-current sweep to miss by up to ~5.1%.

Stage-2C, which allowed effective Ig2 around 0.55 mA, matched amplifier current more closely.

This suggests the next refinement should NOT add another waveshaper degree of freedom.

Instead perform a small joint scan over:
- EX around the successful 1.40 region;
- effective device Ig2 / S0 within the manufacturer/specimen uncertainty around roughly 0.55-0.60 mA.

Ia and gm remain fixed exactly.

Promotion objective:
retain:
- Graph A/B quality;
- <~4% exact 5%-THD envelope;
while restoring amplifier-current agreement.

Any chosen effective Ig2 value must remain explicitly classified as specimen/fit calibration rather than rewriting Philips' tabulated typical 0.6 mA fact.
