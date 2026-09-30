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


## Revision — Philips internal resistance added

Primary Philips typical characteristics also document:

- Ri = 2.5 MOhm at Va=250 V, Vg2=140 V, Vg1=-2 V.

This exact manufacturer anchor was added because it directly constrains plate slope/output resistance and therefore helps separate knee/slope parameters that were previously correlated.

Updated Stage-1 parameters:

- MU = 43.5199389
- KG1 = 1998.32070
- KP = 200.286916
- KVB = 1083.75004
- VCT = 0.365171210
- EX = 1.27822810
- KNEE = 12.9196481
- KNEE2 = 1.45283944
- KNEX = 0
- KLAMG = 1.00015581e-7

Updated anchor reproduction:

- Ia ≈ 2.975 mA vs 3.000 mA
- gm ≈ 1.995 mA/V vs 2.000 mA/V
- Ri ≈ 2.475 MOhm vs 2.500 MOhm

Graph A+B normalized residual remains approximately 0.41 sigma with worst point below about 0.94 sigma.

Interpretation:

This is a materially better Stage-1 surface because it now constrains:
- control-grid transfer;
- screen-grid dependence;
- plate-voltage knee/slope;
- local transconductance;
- local plate resistance.

The previous Stage-1 parameter set is superseded by this Ri-constrained revision.


## Low-Va knee gate added

The corrected Philips Graph-B supplemental dataset at:
- 20 V
- 40 V
- 60 V
- 80 V

is now part of the automated static-stage QA.

Evidence quality:
MANUAL_GRAPH_DIGITIZATION_REFINED with deliberately broad uncertainties.

The gate uses normalized RMS across the full low-Va set, not a formal per-point statistical sigma claim.

Purpose:
- prevent later screen/large-signal refinements from silently degrading the pentode knee;
- keep the high-Va plateau and low-Va knee as separately visible error domains.

Exact manufacturer table anchors remain higher authority than these raster-derived points.
