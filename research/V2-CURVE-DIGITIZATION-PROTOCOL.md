# SMX-3 V2 Primary-Curve Digitization Protocol

Status: required before full PENTODE / IRON parameter fit

## Principle

No point read from a printed/scanned graph is treated as exact manufacturer tabular data.

Digitized graph samples are:
- DOCUMENTED-GRAPH-DERIVED;
- stored with source page/graph identity;
- stored with axis calibration;
- stored with an uncertainty estimate;
- never silently mixed with exact tabulated specifications.

## EF86 primary plate curves

Source:
Philips EF86 original data sheet, sheet B / plate-current family.

Conditions:
- Vg2 = 140 V
- Vg3 = 0 V
- x = Va in volts
- y = Ia in mA

Visible control-grid curves include:
- Vg1 = 0
- -0.5
- -1.0
- -1.5
- -2.0
- -2.5
- -3.0
- -3.5
- -4.0
- -4.5 V

### Required calibration

For the source raster:
1. record source image width/height;
2. locate graph rectangle using printed major-axis intersections, not page edges;
3. establish x mapping from at least three known Va grid lines;
4. establish y mapping from at least three known Ia grid lines;
5. calculate residual calibration error;
6. reject any calibration whose residual exceeds half a minor-grid division.

### Sampling

For Vg1 = 0, -1, -2, -3, -4 V:
- sample knee densely;
- sample high-Va region at regular plate-voltage intervals;
- target at least 12 samples per curve when the line is visually separable;
- never infer an obscured crossing through another curve/dissipation line without marking it estimated.

Store:
- Va_V
- Ia_mA
- Vg1_V
- Vg2_V
- source_sheet
- pixel_x
- pixel_y
- x_uncertainty_V
- y_uncertainty_mA
- quality flag

## EF86 transfer curves

Source:
Philips sheet A.

Conditions:
- Va = 250 V
- Vg3 = 0 V

Screen-grid families:
- Vg2 = 60
- 100
- 140
- 180 V

Digitize Ia(Vg1) for each visible family.

This is a separate objective from the plate curves and directly constrains screen-voltage dependence.

## Jensen JT-11P-1 graph curves

Source:
Jensen manufacturer JT-11P-1 data sheet.

### Graph 1
THD+N (%) versus frequency (Hz).

Axes:
- frequency logarithmic, 20 Hz to 20 kHz;
- THD+N logarithmic, 0.001% to 1%.

Curves:
- +4 dBu
- +14 dBu
- +20 dBu

### Graph 2
THD+N (%) versus input level (dBu).

Axes:
- input level linear in dBu, approximately -25 to +30 dBu;
- THD+N logarithmic, 0.001% to 1%.

Curves:
- 20 Hz
- 30 Hz
- 50 Hz

### Anchor enforcement

The digitized Jensen data must remain consistent with exact table entries:
- 20 Hz / +4 dBu: typical 0.025% THD;
- 20 Hz / +20 dBu: typical 1% THD threshold;
- 1 kHz / +4 dBu: <0.001% THD.

If a graph trace appears inconsistent with a tabulated exact value:
- table wins as exact specification;
- graph point is retained with its reading uncertainty and discrepancy documented.

## Fitting weights

Exact table values:
highest authority/weight.

Digitized primary manufacturer curves:
weighted by digitization uncertainty.

Secondary/community curve fits:
out-of-fit comparison only unless independently verified.

## Reproducibility artifact

Final curve datasets must include a calibration sidecar containing:
- source URL/document;
- sheet/page;
- raster dimensions;
- graph rectangle;
- axis type (linear/log);
- known calibration intersections;
- residual error;
- extraction date;
- operator/tool.

No dataset without this sidecar may be used to tune final production model parameters.
