# SMX-3 V2 IRON Linear-Target + Nonlinear-JA Residual Architecture

Date: 2026-09-30
Status: architecture screen

## Motivation

The evidence now separates cleanly:

The quasi-static/stateful Jiles-Atherton core is strong for:
- nonlinear THD growth;
- H3-dominant symmetry;
- saturation;
- hysteresis/remanence;
- DC-bias history.

But its small-signal complex transfer does not match Jensen DLP.

Adding classical and excess dynamic-loss fields did not provide enough
independent phase leverage before degrading THD.

The validated loss-aware Jensen small-signal target DOES match:
- magnitude;
- impedance/gain;
- upper bandwidth;
- DLP.

Therefore test a model decomposition rather than adding arbitrary loss:

    output =
        Jensen_linear(input)
        +
        [ JA_nonlinear(input,state) - JA_linearized(input) ]

## Interpretation

The bracketed term is the nonlinear/stateful residual of the JA model relative
to its own small-signal linearization.

At vanishing signal:
- JA_nonlinear -> JA_linearized;
- residual -> zero;
- total model -> Jensen linear target.

At larger signal:
- JA residual contributes saturation/hysteresis harmonics and state history;
- the incorrect JA small-signal linear component is not counted twice.

This is a nonlinear model-order decomposition, not a claim about literal
parallel hardware windings.

Evidence class:
PHYSICS-DERIVED NONLINEAR STATE + EMPIRICALLY TUNED LINEAR TARGET.

## First gate

Before designing realtime filters, verify on sinusoidal offline fixtures that
substituting the linear component preserves:
- +4 dBu / 20 Hz ~0.025% THD;
- +20 dBu / 20 Hz ~1% THD;
- H3 dominance;
- low-level distortion quartering trend across 20/40/80 Hz.

If these fail, reject the decomposition.

If these pass:
- identify causal low-order realizations for L_JA and L_Jensen;
- verify phase/magnitude;
- then rerun remanence/DC-bias/state regression on the combined output.
