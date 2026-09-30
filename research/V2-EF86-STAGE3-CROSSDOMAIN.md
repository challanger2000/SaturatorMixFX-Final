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
