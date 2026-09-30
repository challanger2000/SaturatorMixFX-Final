# SMX-3 V2 IRON Classical Dynamic-Loss Sensitivity

Date: 2026-09-30
Status: architecture screen

## Model change under test

Keep the accepted quasi-static Jiles-Atherton state.

Add only a dynamic loss field proportional to core voltage / dB/dt:

H_applied = H_qs + A_v * v_core

This is the simplest causal derivative-dependent dynamic-loss augmentation.

At DC:
v_core = 0
therefore the added field vanishes and static hysteresis/remanence are not
replaced.

## Why test this first

Dynamic Jiles-Atherton literature separates:
- quasi-static hysteresis;
- classical eddy-current loss;
- excess/anomalous loss.

The classical term is the lowest-complexity missing mechanism.

Only if it cannot satisfy Jensen phase/magnitude while preserving THD should
an excess-loss term proportional to sqrt(|dB/dt|) be introduced.

## Screening metrics

For each A_v:
- +4 dBu / 20 Hz THD;
- +20 dBu / 20 Hz THD;
- H2/H3;
- 20 Hz / 1 kHz magnitude;
- 20 kHz / 1 kHz magnitude;
- DLP after linear-phase removal.

No A_v value is promoted solely from this sweep.

## Decision rule

If a finite A_v moves DLP into Jensen bounds while preserving the exact THD
anchors and H3-dominant symmetry, classical dynamic loss is sufficient for
the first unified candidate.

If not, add the excess-loss term as a second independent dynamic mechanism.
