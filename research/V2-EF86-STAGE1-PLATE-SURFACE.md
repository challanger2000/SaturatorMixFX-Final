# SMX-3 V2 EF86 Stage-1 Plate-Current Surface

Date: 2026-09-30
Status: ACCEPTED AS PROVISIONAL STAGE-1 PLATE-CURRENT CANDIDATE

## Objective

Fit one plate-current equation surface simultaneously against:

- Philips Graph A:
  Ia(Vg1) at Va=250 V for Vg2=60/100/140/180 V;
- Philips Graph B:
  Ia(Va) at Vg2=140 V across multiple Vg1 curves;
- exact Philips device Ia anchor;
- exact Philips device gm anchor.

Screen current Ig2 is deliberately excluded from Stage 1.

## Equation-family parameters

- MU = 43.3297945
- KG1 = 2122.02731
- KP = 200.296043
- KVB = 987.399992
- VCT = 0.398021237
- EX = 1.29313213
- KNEE = 12.2652275
- KNEE2 = 3.04408319
- KNEX = 0
- KLAMG = 9.22571089e-5

Evidence class:
EMPIRICALLY TUNED TO DOCUMENTED / PROVISIONALLY DIGITIZED PHILIPS DATA.

These are model parameters, not physical EF86 component constants.

## Primary results

Combined manufacturer-surface fit:
- normalized RMS residual approximately **0.413 sigma**
- worst individual residual below approximately **0.96 sigma**

Exact device point:
- Ia ≈ **2.980 mA** vs Philips 3.000 mA
- gm ≈ **1.991 mA/V** vs Philips 2.000 mA/V

This is materially stronger than fitting Graph B or one operating point alone because Graph A independently constrains screen-voltage dependence.

## Why Screen Current Is Not Included Yet

When the screen-current model parameters are freed together with the plate surface, multiple parameter sets achieve similarly low residuals while:
- KG2 moves strongly;
- KVC moves to search bounds;
- compensating parameter combinations remain possible.

That is an identifiability problem, not a reason to publish extreme fitted values.

Therefore Stage 1 freezes only the plate-current surface.

## Stage-2 requirement

Identify the screen-current / amplifier-bias submodel using independent evidence:

- exact Ig2 = 0.6 mA device anchor;
- Philips circuit-1 cathode-current sweep;
- Philips small-signal gain sweep;
- Graph-A screen dependence already frozen as a plate-current constraint.

Any Stage-2 solution must re-run Stage 1 and may not materially degrade Graph A+B.

## Stage-3 requirement

Only after Stage 2:
- exact 5%-THD supply envelope;
- Graph-D Vi->Vo;
- Graph-D distortion->Vo;
- remaining knee/kink terms if required.

## Decision

This is the first EF86 candidate in the project whose plate-current surface is constrained simultaneously in both:
- plate-voltage dimension;
- screen-voltage dimension.

It is therefore the correct foundation for the next PENTODE identification stage.

It is NOT yet a complete pentode model.
