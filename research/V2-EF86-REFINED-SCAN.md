# SMX-3 V2 EF86 Refined EX / Screen-Current Scan

Date: 2026-09-30
Workflow run: 36665101382
Conclusion: SUCCESS

## Question

After the EX=1.40 scan dramatically improved the exact Philips 5%-THD envelope, could a slightly lower effective screen-current anchor improve the remaining cathode-current sweep without materially hurting the large-signal fit?

Scanned:
- EX = 1.34 .. 1.46
- effective Ig2 = 0.54 .. 0.60 mA

For every candidate:
- Ia = 3.0 mA at the Philips device point was held exactly;
- gm = 2.0 mA/V was held exactly;
- VCT and KG1 were re-derived;
- only the effective screen-current scale changed.

## Result

The best combined candidate remains:

- EX = 1.40
- Ig2 = 0.600 mA
- VCT = 0.609404027245
- KG1 = 1733.51695398
- S0 = 0.000115372393411

Quality:
- Graph A NRMS ~0.516 sigma
- Graph B NRMS ~0.483 sigma
- max cathode-current error ~5.10%
- max small-signal gain error ~3.74%
- max exact Vo@5% error ~3.51%

Exact large-signal envelope:
- 200 V: 40.075 V vs 40 V
- 250 V: 51.756 V vs 50 V
- 300 V: 62.988 V vs 64 V
- 350 V: 73.915 V vs 75 V
- 400 V: 84.619 V vs 87 V

## Why lower Ig2 was rejected

Reducing effective Ig2 does improve cathode-current agreement.

Example around EX=1.40:
- Ig2=0.54 mA -> max Ik error ~1.47%
- but exact Vo@5% error worsens to ~14.84%.

As Ig2 returns toward the manufacturer 0.60 mA anchor:
- cathode-current error grows;
- large-signal envelope improves dramatically.

Therefore lowering Ig2 is not a valid way to 'fix' the model.

It would trade a directly documented device parameter and the large-signal manufacturer envelope for a nicer DC-current table fit.

## Decision

Keep the Philips typical screen-current anchor:
- Ig2 = 0.600 mA.

Promote EX≈1.40 as the current strongest PENTODE control-grid curvature candidate.

Do NOT add a specimen-specific screen-current trim merely to reduce the remaining ~5% cathode-current error.

The remaining current-sweep discrepancy should instead be challenged against:
- calibrated Graph A/B extraction;
- Philips edition/specimen variation;
- the exact dynamic screen/cathode network;
- and the remaining plate-resistance discrepancy.

Current candidate status:
**STRONG PROVISIONAL EF86 OFFLINE STATIC/LARGE-SIGNAL CANDIDATE**

Still required before final reference promotion:
1. Graph-D out-of-fit recheck using the EX=1.40 candidate;
2. continuous Graph-C Ik/gain cross-check between tabulated supply points;
3. calibrated manufacturer graph extraction;
4. dynamic screen/cathode network;
5. realtime reduction and aliasing/CPU QA.
