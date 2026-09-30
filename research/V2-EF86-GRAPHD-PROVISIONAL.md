# SMX-3 V2 EF86 Graph-D Provisional Digitization

Date: 2026-09-30
Source: Philips EF86 original sheet, graph D (sheet dated 1957-10-10 in the assembled PDF)
Primary PDF:
https://www.r-type.org/pdfs/ef86-1.pdf

## Circuit selected

Circuit (1):
- Vb = 250 V
- Ra = 0.1 MOhm
- Rg2 = 0.39 MOhm
- Rk = 1 kOhm
- following-stage grid resistor = 0.33 MOhm

This is the same circuit already selected as the primary PENTODE reference.

## Graph interpretation

The graph overlays:
- input voltage Vi in mV on the left vertical axis;
- distortion d in percent on the right vertical axis;
- output voltage Vo in V on the horizontal axis;
- curves for circuits (1) and (2).

For circuit (1):
- the upper approximately linear Vi curve reaches roughly 0.49 V input at 50 V output;
- the corresponding distortion curve reaches approximately 5% at 50 V output.

The 50 V / 5% endpoint is independently confirmed by the manufacturer table.

## Provisional sampled points

| Vo RMS | Vi RMS | distortion |
|---:|---:|---:|
| 10 V | ~91 mV | ~0.30% |
| 20 V | ~184 mV | ~0.75% |
| 30 V | ~280 mV | ~1.45% |
| 40 V | ~378 mV | ~2.55% |
| 50 V | ~490 mV | ~5.00% |

These are MANUAL_GRAPH_DIGITIZATION values, not exact tabular data.

Uncertainties are deliberately non-trivial because:
- scan line thickness is several pixels;
- multiple curves cross or run close together;
- both vertical quantities share the same raster height;
- the scan is not a vector original.

Machine-readable data:
research/ef86_philips1956_graphD_provisional.csv

## Immediate use

Use these points as an OUT-OF-FIT shape check for:
- Vi -> Vo compression;
- distortion growth versus output.

Do not tune a final production model solely to these provisional points.

Promotion requires:
- calibrated raster coordinates / sidecar;
- independent re-read of the curve;
- consistency with the exact 50 V / 5% table endpoint.
