# SMX-3 V2 IRON One-State Relaxation Candidate

Date: 2026-09-30
Status: STRONG SMALL-SIGNAL ARCHITECTURE CANDIDATE

A private numerical search found a single-relaxation-state solution for the
architecture documented in V2-IRON-RELAXATION-FIT.md.

The result is now frozen in an independent standard-library verifier so it can
be reproduced in GitHub Actions without the optimizer.

Effective candidate values:
- Lstat ≈ 1121.99 H
- Gloss ≈ 3.07834 uS
- tau ≈ 0.37543 ms
- leakage L ≈ 2.69381 mH
- effective Cx ≈ 1.15692 nF

These are EMPIRICALLY TUNED model quantities.
They are not Jensen winding/core construction values.

The important result is the model structure:

Ymag = 1/(s Lstat) + Gloss/(1+s tau)

One relaxation state supplies the frequency-dependent loss/complex
permeability that a constant classical-loss conductance could not.

The corresponding field-state representation can be constructed so the
dynamic field decays to zero in the quasi-static/DC limit, preserving the
static JA equilibrium hysteresis model.

Next gate:
embed the relaxation state around the nonlinear JA core and prove that:
- +4 dBu / 20 Hz THD remains near 0.025%;
- +20 dBu / 20 Hz remains near 1%;
- H3 dominance remains;
- Jensen DLP/magnitude remain;
- DC-bias/remanence remain;
- numerical/realtime gates remain stable.
