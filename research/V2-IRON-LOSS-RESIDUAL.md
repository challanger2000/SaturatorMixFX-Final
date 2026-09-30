# SMX-3 V2 IRON Dynamic-Loss Residual Decomposition

Date: 2026-09-30
Status: architecture-identification experiment

## Question

What dynamic small-signal behavior is missing from the accepted quasi-static
Jiles-Atherton core relative to the Jensen loss-aware target?

Rather than immediately inventing an eddy-current coefficient, this experiment
computes the residual complex admittance between:

1. the settled low-level Jiles-Atherton transformer candidate;
2. the Jensen loss-aware small-signal target.

Residual:
Yaux = 1/Ztarget - 1/Zja

## Why admittance

A causal auxiliary loss/relaxation mechanism that sits in parallel with the
magnetizing response naturally adds admittance.

If the residual:
- has non-negative real part;
- and can be approximated by a passive RL/relaxation network;

then a separate dynamic-loss branch can be introduced without modifying the
quasi-static hysteresis law.

## First candidate

Fit the residual to one passive series-RL branch:

Yaux ~= 1 / (Raux + s*Laux)

This branch:
- contributes no arbitrary static waveshaping;
- is causal;
- is passive for Raux>0, Laux>0;
- vanishes at DC voltage steady state;
- can represent one magnetic relaxation/loss timescale.

## Rejection rule

Do not use a single RL branch if:
- residual conductance becomes materially negative;
- complex fit error is poor;
- DLP/magnitude cannot be recovered after insertion.

Then move to:
- two relaxation branches;
- or a derivative-dependent dynamic-JA loss formulation derived from the
  Jiles dynamic-loss literature.

This staged approach minimizes unnecessary model complexity.
