# EF86 Philips-1956 Plate-Curve Digitization — Provisional

Source: Philips EF86 sheet B, Vg2=140 V, Vg3=0 V.

The first machine-readable plate-curve dataset is intentionally conservative:
- points are read from the manufacturer graph;
- every point carries an explicit uncertainty;
- evidence class is MANUAL_GRAPH_DIGITIZATION;
- these points are validation-only until calibrated image-coordinate extraction replaces them.

This prevents false precision while allowing the current pentode equation to be tested against the shape of the actual manufacturer curves rather than only against operating-point tables.

The current dataset samples Vg1=-1 to -4 V at Va=100/200/300 V. It deliberately avoids the 1 W dissipation boundary and the most ambiguous near-origin pixels.

Final promotion still requires calibrated extraction with recorded graph bounds/pixel coordinates and denser knee-region sampling.
