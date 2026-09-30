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
