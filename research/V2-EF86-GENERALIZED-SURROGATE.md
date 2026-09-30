# SMX-3 V2 Generalized EF86 Surrogate Candidate

Date: 2026-09-30
Status: strong provisional realtime-surrogate candidate; NOT yet final hardware reference

## Motivation

The previous compact Koren-form candidate passed static/small-signal tests but reached 5% THD at only ~36.76 Vrms versus Philips' documented ~50 Vrms.

A generalized knee term was therefore tested:

Ia = E1^EX / KG1 * atan(Va/KVB)^beta

The extra exponent beta is:
- not claimed as a physical EF86 parameter;
- classified EMPIRICALLY TUNED TO DOCUMENTED MEASUREMENTS;
- acceptable only if the full model remains demonstrably close to the manufacturer reference.

## Candidate parameters

- MU = 36.895496
- EX = 1.310355
- KG1 = 1371.042005
- KG2 = 3539.169261
- KP = 186.980462
- KVB = 1.975123
- beta = 1.327475

## Device anchor

Approximate:
- Ia = 2.9748 mA vs 3.0 mA
- Ig2 = 0.6079 mA vs 0.6 mA
- gm = 1.9212 mA/V vs 2.0 mA/V

## Philips-1956 amplifier sweep

Approximate worst errors:
- cathode current: ~5.52 %
- small-signal gain: ~4.22 %

The errors are somewhat larger than the previous table-only fit, but still controlled while greatly improving large-signal behavior.

## Exact large-signal anchor

At 5% THD:
- candidate output ≈49.18 Vrms
- Philips target ≈50 Vrms
- error ≈-1.65 %

This is a major improvement over the previous ~36.76 Vrms result.

## Out-of-fit coarse plate curves

Against the current 21-point provisional Philips graph dataset:
- normalized RMS error ≈0.717 sigma
- worst point ≈1.54 sigma

The generalized model therefore retains broadly correct plate-curve shape under the present conservative digitization uncertainty.

## Harmonic-growth trajectory

Representative quasi-static outputs:
- 10 Vrms output -> ~0.80 % THD
- 20 Vrms -> ~1.50 % THD
- 30 Vrms -> ~2.03 % THD
- 40 Vrms -> ~2.69 % THD
- 49 Vrms -> ~4.93 % THD

These values now need comparison against calibrated points from Philips graph D.

## Decision

PROMOTE from 'table-only experiment' to STRONG PROVISIONAL REALTIME SURROGATE CANDIDATE.

Do NOT call it final because:
- beta is empirical;
- graph-D intermediate distortion points are not yet calibrated;
- low-Va knee digitization is still coarse;
- dynamic capacitance/screen behavior remains to be added;
- realtime discretization and aliasing are not tested.

The offline manufacturer-data surface remains the authority. This compact model survives only as long as it stays within measured error against that authority.


## Full 5%-THD supply-sweep recheck

The exact Philips-1956 large-signal envelope was then tested at all fixed-component circuit-1 supply points, not only 250 V.

| Vb | Philips Vo @5% | generalized surrogate | error |
|---:|---:|---:|---:|
| 200 V | 40 V | ~40.30 V | +0.74 % |
| 250 V | 50 V | ~49.18 V | -1.65 % |
| 300 V | 64 V | ~57.67 V | -9.89 % |
| 350 V | 75 V | ~65.82 V | -12.25 % |
| 400 V | 87 V | ~73.64 V | -15.36 % |

### Status correction

The generalized beta surrogate is therefore NOT a final EF86 model.

It remains useful as:
- a strong local 200-250 V realtime-surrogate baseline;
- evidence that one extra knee degree of freedom materially improves the 250 V large-signal trajectory;
- a comparison candidate against the future manufacturer-data current surface.

But the full supply sweep demonstrates remaining structural model-form limitation at higher plate/supply voltage.

Current status:
LOCAL PROVISIONAL SURROGATE ONLY.

Promotion requires a model/current-surface that reproduces the complete 200-400 V large-signal envelope without per-supply correction.
