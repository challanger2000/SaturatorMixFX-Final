# SMX-3 V2 EF86 Stage-1 Transfer-Surface Fit

Date: 2026-09-30
Workflow run: 36662285030
Conclusion: SUCCESS

## Purpose

Identify the EF86 plate-current control/screen/high-Va surface BEFORE fitting:
- screen-current law;
- low-Va knee;
- kink;
- large-signal envelope.

Objective data:
- provisional Philips Graph A screen-voltage families;
- provisional Philips Graph B plate-current families;
- Philips typical Ia anchor;
- Philips gm anchor;
- Philips typical internal resistance anchor.

No large-signal Vo@5% or Graph-D data were included.

## Fitted parameters

Equation-family Stage-1 parameters:

- MU = 42.1294068459
- EX = 1.48016674106
- KG1 = 2059.06189749
- KP = 215.816749098
- VCT = 0.761562843483
- KVB_SCREEN = 430.818432714
- LAMBDA = 0.000160501489918 /V

Evidence:
EMPIRICALLY TUNED TO DOCUMENTED / PROVISIONALLY DIGITIZED PHILIPS DATA.

These are effective model parameters, not claimed physical EF86 constants.

## Fit quality

Overall normalized RMS:
- ~0.4973 sigma

Graph A:
- NRMS ~0.4602 sigma
- worst ~1.063 sigma

Graph B:
- NRMS ~0.5000 sigma
- worst ~1.078 sigma

Device reconstruction:
- Ia(250 V, 140 V, -2 V) ~2.9603 mA vs 3.0 mA
- gm ~1.9641 mA/V vs 2.0 mA/V
- inferred ri ~2.1047 MOhm vs Philips typical ~2.5 MOhm

## Identifiability result

No fitted parameter lies within 2% of an arbitrary search bound.

This is a major improvement over the unrestricted extended-family experiment, where several parameters ran to fit bounds.

Interpretation:
the staged factorization is materially better conditioned.

## Decision

PROMOTE to:
**EF86 STAGE-1 TRANSFER-SURFACE CANDIDATE**

Do not yet call it the complete pentode model.

Still missing:
1. screen-current law;
2. self-biased circuit DC/gain validation using the Stage-1 surface;
3. low-Va knee;
4. exact 5%-THD supply envelope;
5. Graph-D compression/distortion trajectory;
6. dynamic capacitances;
7. realtime/aliasing/CPU work.

The Stage-1 parameters should remain fixed or tightly regularized during Stage 2 so later objectives cannot silently destroy the already-identified Philips current surface.
