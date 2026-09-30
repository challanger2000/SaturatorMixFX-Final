# SMX-3 V2 EF86 Graph-A Screen-Family Comparison

Date: 2026-09-30
Status: INFORMATIONAL structural comparison

Primary evidence:
Philips EF86 Graph A, Va=250 V, Vg3=0 V, Ia(Vg1) for Vg2=60/100/140/180 V.

Current dataset:
research/ef86_philips_graphA_provisional.csv

Most points remain MANUAL_GRAPH_DIGITIZATION with explicit uncertainties. The exact 140 V / -2 V / 3 mA device point is a manufacturer anchor.

## Models compared

1. Provisional compact multi-anchor fit
   - fitted to Philips device anchor plus circuit-1 DC/gain sweep.

2. Generalized beta compact surrogate
   - one additional empirical knee exponent;
   - strongly improves the 250 V large-signal endpoint;
   - already rejected as final model on the full 200-400 V 5%-THD envelope.

3. Extended knee/kink family with community comparison parameters
   - used only as model-family evidence;
   - parameter values remain non-authoritative.

## Structural result

The compact provisional model currently follows the Graph-A screen-voltage family at least as well as, and in the present provisional dataset somewhat better than, the generalized beta surrogate.

This is important because it shows a real tradeoff:

- the beta extension improves one large-signal domain;
- but does not automatically improve screen-grid physics.

The community extended family remains useful because its equation structure contains independent screen/knee/slope degrees of freedom, but its published parameter set is not accepted.

## Decision

Graph A becomes a mandatory recheck after every future PENTODE large-signal refinement.

No model is accepted if it:
- reduces 5%-THD envelope error;
- while creating systematic Vg2-family residuals.

The final PENTODE fit must minimize contradiction across:
- Graph A: screen-grid transfer;
- Graph B: plate-voltage knee/slope;
- circuit-1 DC current and gain;
- exact 5%-THD envelope;
- Graph D compression/distortion trajectory.

Until calibrated Graph-A extraction replaces the provisional points, this comparison remains INFORMATIONAL rather than a hard release gate.
