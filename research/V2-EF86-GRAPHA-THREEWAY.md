# SMX-3 V2 EF86 Graph-A Three-Way Model-Family Comparison

Date: 2026-09-30
Evidence status: provisional Philips manufacturer-graph digitization

## Models

Compared against the same Graph-A screen-voltage family:

1. compact provisional Koren-form fit;
2. generalized beta surrogate;
3. extended knee/kink equation family using the published community parameter set only as a research benchmark.

No community parameters are accepted as production authority.

## Result

Approximate normalized RMS residual:

- extended knee/kink family: **0.63 sigma**
- compact provisional fit: **0.72 sigma**
- generalized beta surrogate: **0.99 sigma**

Approximate worst individual residual:

- extended family: ~1.32 sigma
- compact provisional: ~1.63 sigma
- generalized beta: ~1.67 sigma

The extended family also shows relatively small signed residual trends across the 60/100/140 V screen families, with its largest present bias around the 180 V family.

## Interpretation

This is strong MODEL-FAMILY evidence.

The generalized beta surrogate improved the 250 V large-signal endpoint but sacrifices some screen-grid fidelity.

The extended knee/kink family:
- already follows Graph A more naturally;
- independently showed a much better large-signal supply-envelope SHAPE;
- contains explicit plate-knee, slope and screen-coupling degrees of freedom.

Its existing community parameter set is still rejected because:
- screen current is materially wrong at the documented device point;
- self-biased amplifier current is systematically wrong.

Therefore the correct direction is:

**independently refit the extended equation family to Philips primary data.**

Not:
- use the community parameters;
- add per-screen trims;
- or continue stretching the generalized beta surrogate.

## Next identification constraint

The refit objective must contain Graph A explicitly before large-signal optimization.

This prevents large-signal parameters from compensating by corrupting:
- Vg2 dependence;
- control-grid transfer curvature;
- gm/screen relationships.

Graph A is still provisional/manual, so exact numerical ranking may move after calibrated extraction. The structural conclusion is nevertheless strong enough to justify the extended-family research path.
