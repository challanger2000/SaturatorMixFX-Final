# SMX-3 V2 IRON Classical + Excess Dynamic-Loss Screen

Date: 2026-09-30
Status: architecture screen

## Why the second term is now justified

Classical derivative-dependent loss alone was tested first.

Result:
- DLP changed only modestly;
- a coefficient large enough to move DLP materially already pulled the exact
  +20 dBu / 20 Hz THD anchor downward.

Therefore classical loss alone is structurally insufficient.

## Added mechanism

Dynamic effective field:

H_dyn =
A_v * v_core
+
B_v * sign(v_core) * sqrt(abs(v_core))

Because v_core is proportional to dB/dt, these terms correspond structurally to:
- classical eddy-current loss;
- excess/anomalous loss.

The addition vanishes at DC and therefore does not replace quasi-static
hysteresis/remanence.

## Numerical implementation

The nonlinear circuit equation is solved analytically by substituting:

u = sqrt(abs(v_core))

which yields one positive quadratic root per sample.

No iterative root solver is required.

## Screen

Coarse grid over:
- A_v
- B_v

Metrics:
- exact low/high 20 Hz THD anchors;
- H2/H3;
- 20 Hz and 20 kHz relative magnitude;
- Jensen DLP.

No coefficient is promoted directly from this grid.

If the architecture reaches the required domains simultaneously, the next step
is a constrained local fit followed by:
- DC-bias/remanence regression;
- numerical-method cross-check;
- realtime reduction;
- Jensen multi-level/frequency residual.


## Frozen first-order acceptance envelope

A classical+excess dynamic-loss point is NOT considered viable merely because
it has the lowest aggregate score.

For architecture promotion it must simultaneously satisfy:

- +4 dBu / 20 Hz THD: 0.020..0.030%;
- +20 dBu / 20 Hz THD: 0.95..1.05%;
- default H3 remains dominant over H2;
- Jensen-band DLP worst absolute <= 2.0 degrees;
- 20 Hz relative magnitude remains within +/-0.01 dB of -0.04 dB.

The 20 kHz and 95 kHz response are handled by the separate parasitic/HF target
and are not allowed to conceal a failed magnetic low-frequency model.

Only after a point passes this first-order envelope may c/KI be re-calibrated
locally and the full regression suite be rerun.
