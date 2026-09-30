# SMX-3 V2 EF86 Kink-Parameter Sensitivity Plan

Date: 2026-09-30

Purpose:
screen the extended pentode family's large-signal terms before any expensive
multi-parameter optimization.

Frozen starting point:
the knee-aware static refit documented in
research/V2-EF86-KNEE-STATIC-REFIT.md.

Parameters screened:
- KNEX
- KNK
- KNG
- KNSL
- KNPR
- KNSR

For every perturbation the tool reports:
- Graph A normalized RMS;
- Graph B plateau normalized RMS;
- Graph B knee normalized RMS;
- exact Vo@5% error at 250 V;
- exact Vo@5% error at 400 V.

This directly answers:
"Does this large-signal degree of freedom improve the manufacturer envelope
without silently damaging the static current surfaces?"

Only parameters with useful independent leverage are eligible for the next fit.

A parameter that merely trades Graph-A/B error for one better large-signal
point is rejected from the active fit set.
