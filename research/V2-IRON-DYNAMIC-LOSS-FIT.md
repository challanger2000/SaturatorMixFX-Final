# SMX-3 V2 IRON Local Dynamic-Loss Fit

Date: 2026-09-30
Status: minimal-fit gate

Purpose:
test whether the new dynamic-loss architecture can close the Jensen phase/loss gap
without reopening the accepted quasi-static Jiles-Atherton parameter set.

Frozen:
- a
- alpha
- c
- k
- Ms
- KI
- KPHI

Fit only:
- A_v classical dynamic-loss coefficient
- B_v excess-loss coefficient

Acceptance domains:
- +4 dBu / 20 Hz THD
- +20 dBu / 20 Hz THD
- H3-dominant symmetry
- 20 Hz magnitude
- Jensen DLP

If this passes:
the IRON reference can move toward a unified nonlinear+dynamic-loss candidate
without re-identifying the quasi-static hysteresis core.

If it fails:
do not immediately add more dynamic parameters.
First determine whether c/KI need a constrained refit in the presence of dynamic loss.
