# SMX-3 V2 Generalized EF86 — Exact Multi-Supply Large-Signal Envelope

Date: 2026-09-30
Status: REJECTED as final PENTODE model; retained as useful surrogate benchmark

## Manufacturer authority

Philips EF86 circuit (1), fixed component values:
- Ra=100 kOhm
- Rg2=390 kOhm
- Rk=1 kOhm
- following-stage grid resistor=330 kOhm

Exact 1956 table output at 5% total distortion:

| Vb | Vo at 5% THD |
|---:|---:|
| 200 V | 40 V |
| 250 V | 50 V |
| 300 V | 64 V |
| 350 V | 75 V |
| 400 V | 87 V |

## Generalized surrogate result

The current beta-extended compact surrogate gives approximately:

| Vb | modeled Vo at 5% | Philips | error |
|---:|---:|---:|---:|
| 200 V | 40.30 V | 40 V | +0.74% |
| 250 V | 49.18 V | 50 V | -1.65% |
| 300 V | 57.67 V | 64 V | -9.89% |
| 350 V | 65.82 V | 75 V | -12.25% |
| 400 V | 73.64 V | 87 V | -15.36% |

## Decision

The generalized surrogate remains useful because it simultaneously performs well on:
- device anchor;
- DC current sweep;
- small-signal gain sweep;
- coarse plate-curve family;
- 250 V large-signal point.

But it is NOT a final PENTODE hardware model because its large-signal envelope does not generalize across supply voltage.

This failure is structurally similar to the simpler six-parameter model, although the 200/250 V region is much improved.

## Next model requirement

The next PENTODE family must add enough plate-knee / voltage-dependent structure to reproduce:
- exact DC current;
- small-signal gain;
- plate-current curves;
- 5%-THD output envelope across 200..400 V;
- Philips Graph-D distortion/compression shape at 250 V.

Do not add a supply-dependent output trim. The improvement must come from the nonlinear plate/screen model itself.
