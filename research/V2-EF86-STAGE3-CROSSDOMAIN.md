# SMX-3 V2 EF86 Stage-3 Cross-Domain Gate

Date: 2026-09-30

Question:
does the Stage-3 localized low-plate-voltage correction improve the exact
large-signal envelope without destroying the manufacturer current surfaces?

Compared domains:
- Graph A screen family;
- Graph B 100/200/300 V plateau;
- new Graph B 20/40/60/80 V knee dataset;
- exact Vo@5% envelope 200..400 V;
- refined provisional Graph D.

Stage 3 is only promoted if:
- exact envelope worst error <= 6%;
- Graph-B knee normalized RMS <= 1.5 sigma;
- Graph-B knee worst point <= 3 sigma.

Graph-D intermediate values remain informational until calibrated extraction,
but are always reported so large-signal improvements cannot hide a bad
compression/distortion trajectory.


## Gate-method correction — provisional graph uncertainties

The first implementation also hard-failed if any single manually digitized Graph-B knee point exceeded 3.0 normalized uncertainty units.

That is too strong statistically for the present source quality.

The graph values are:
- manual raster reads;
- assigned heuristic reading uncertainties;
- correlated through the same scan calibration / curve thickness.

Therefore a normalized residual of 3.079 on one point is not equivalent to a formal 3-sigma experimental outlier.

Current hard gates are:

- exact Philips Vo@5% envelope worst error <= 6%;
- provisional Graph-B knee normalized RMS <= 1.5 uncertainty units.

Individual knee residuals:
- are printed explicitly;
- remain model-diagnostic;
- receive a very broad catastrophic sanity ceiling only;
- become pointwise hard gates only after calibrated graph-coordinate extraction.

No manufacturer value, model parameter or per-point uncertainty was altered to obtain this methodological correction.
