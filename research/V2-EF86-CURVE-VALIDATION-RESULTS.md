# SMX-3 V2 EF86 Plate-Curve Validation Result

Date: 2026-09-30
Model: provisional multi-anchor EF86 fit
Source: Philips EF86 sheet B, Vg2=140 V, Vg3=0 V

## Dataset status

Current dataset:
- 21 manufacturer-graph points;
- Vg1 = -1.0 to -4.0 V;
- Va = 100, 200, 300 V;
- every point has explicit manual-reading uncertainty;
- evidence class MANUAL_GRAPH_DIGITIZATION.

This is intentionally a coarse validation set, not final precision digitization.

## Result

Normalized RMS residual:
- approximately 0.535 sigma

Worst residual:
- approximately 1.002 sigma
- near Vg1=-3 V, Va=100 V
- graph estimate approximately 1.15 mA
- model approximately 1.270 mA
- assigned graph-reading uncertainty 0.12 mA

## Interpretation

The provisional model is consistent with the currently digitized Philips plate-curve shape throughout the sampled normal operating region.

This materially strengthens the model because its parameters were originally optimized against:
- device Ia/Ig2/gm;
- amplifier cathode-current sweep;
- amplifier gain sweep;

and NOT against these 21 plate-curve points.

Therefore the plate-curve test currently functions as an out-of-fit validation.

## Remaining risk

The current validation is deliberately sparse in the low-Va knee.

A pentode model can match the flat high-Va region and still have:
- wrong knee position;
- wrong curvature below about 100 V;
- wrong large-signal behavior when the plate is driven toward the knee.

Promotion remains blocked until:
1. calibrated image-coordinate digitization replaces/co-validates the manual points;
2. knee-region points below 100 V are sampled more densely;
3. the 1956 Vi/Vo/distortion graph is checked;
4. large-signal harmonic progression is measured.

Current status:
PROVISIONAL PASS for normal-region plate-curve consistency.
NOT FINAL PENTODE MODEL.
