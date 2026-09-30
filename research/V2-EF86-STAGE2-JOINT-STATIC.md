# SMX-3 V2 EF86 Stage-2 Joint Static Candidate

Date: 2026-09-30
Status: STRONG PROVISIONAL STATIC PENTODE CANDIDATE

## Scope

This candidate is the first EF86 surface fitted jointly across:

- Philips Graph A screen-grid families;
- Philips Graph B plate-current families;
- Ia device anchor;
- Ig2 device anchor;
- gm device anchor;
- Ri device anchor;
- circuit-1 cathode-current sweep;
- circuit-1 small-signal gain sweep.

It is still a static/midband candidate. Large-signal Stage 3 is separate.

## Representative exact-anchor reproduction

Approximate:

- Ia = 2.9785 mA vs 3.000 mA
- Ig2 = 0.5586 mA vs 0.600 mA
- gm = 1.9875 mA/V vs 2.000 mA/V
- Ri = 2.4788 MOhm vs 2.500 MOhm

Ig2 is the weakest exact anchor but remains within about 7%.

## Amplifier sweep

Approximate:

| Vb | Ik model | Ik Philips | gain model | gain Philips |
|---:|---:|---:|---:|---:|
| 200 V | 1.638 mA | 1.700 mA | 105.45 | 106 |
| 250 V | 2.049 mA | 2.100 mA | 111.85 | 112 |
| 300 V | 2.464 mA | 2.500 mA | 116.70 | 116 |
| 350 V | 2.882 mA | 2.900 mA | 120.59 | 120 |
| 400 V | 3.302 mA | 3.300 mA | 123.83 | 124 |

This is substantially better than the minimal Stage-2 screen law.

## Interpretation

The correct static solution requires coupled plate/screen partition behavior.

Trying to keep the Stage-1 plate surface absolutely frozen while adding only a simple screen-current law produced systematic low-supply errors.

A joint but constrained fit resolves:
- screen-voltage dependence;
- plate slope;
- screen-current partition;
- self-bias amplifier behavior

without per-supply correction.

## Remaining limitation

The same candidate reaches 5% THD too early in the large-signal envelope.

That is a Stage-3 low-Va-knee problem, not evidence that the static fit is invalid.

The Stage-3 candidate therefore adds only a strongly localized low-Va correction that vanishes throughout the Graph-A/B region.

## Evidence classification

All fitted equation parameters:
EMPIRICALLY TUNED TO DOCUMENTED / PROVISIONALLY DIGITIZED MANUFACTURER DATA.

No fitted coefficient is claimed to be a physical EF86 construction parameter.


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
