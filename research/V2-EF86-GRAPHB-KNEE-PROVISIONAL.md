# SMX-3 V2 EF86 Graph-B Knee-Region Provisional Digitization

Date: 2026-09-30

Primary source:
Philips EF86 Graph B:
- Vg2 = 140 V
- Vg3 = 0 V
- Ia versus Va
- Vg1 families.

Source PDF:
https://www.r-type.org/pdfs/ef86-1.pdf

## Why this dataset exists

The existing plate-curve CSV sampled mainly:
- 100 V
- 200 V
- 300 V

Those points are useful for plateau current / finite plate slope, but they do not strongly identify the pentode knee.

The extended EF86 family contains knee-related degrees of freedom such as:
- KVB
- KNEE
- KNEE2

Those parameters must not be fitted from high-Va data alone.

This supplemental dataset therefore samples:
- 20 V
- 40 V
- 60 V
- 80 V

for Vg1=-1.0 through -4.0 V.

## Evidence quality

All new points are:
MANUAL_GRAPH_DIGITIZATION

They are deliberately assigned broader uncertainty than exact manufacturer table anchors.

Reasons:
- scanned raster;
- thick plotted curves;
- curve crowding near the origin;
- manual coordinate read.

Machine-readable file:
research/ef86_philips1956_platecurve_knee_provisional.csv

## Usage rule

Use this dataset for:
- model-family discrimination;
- knee-parameter identifiability;
- out-of-fit diagnostics.

Do not:
- claim these values are exact Philips tabular data;
- reduce uncertainty simply to increase fit pressure;
- override exact DC/gain/5%-THD table anchors when conflict is within graph-read uncertainty.

Final promotion still requires calibrated coordinate extraction or an equivalently strong independent primary source.
