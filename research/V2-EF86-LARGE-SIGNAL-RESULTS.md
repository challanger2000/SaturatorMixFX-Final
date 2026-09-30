# SMX-3 V2 EF86 Large-Signal Validation

Date: 2026-09-30
Model: provisional multi-anchor EF86 candidate
Reference: Philips EF86 4-Apr-1956, selected 250 V R-C amplifier

## Exact manufacturer anchor

Selected circuit:
- Vb=250 V
- Ra=100 kOhm
- Rg2=390 kOhm
- Rk=1 kOhm
- following-grid resistor=330 kOhm

Philips table:
- small-signal gain ~112
- output voltage ~50 Vrms
- total distortion ~5 % at that documented maximum-output condition

## Quasi-static large-signal test

Assumptions:
- cathode AC bypassed;
- screen AC bypassed;
- 330 kOhm following-stage grid load included;
- static tube current equations solved sample-by-sample;
- harmonics H2-H10 measured from a sinusoidal cycle.

Result for current provisional fit:
- input required for 5 % THD: ~0.35739 Vrms
- output at 5 % THD: ~36.7567 Vrms
- manufacturer target: ~50 Vrms
- output error: about -26.49 %

## Decision

FAIL as a final PENTODE model.

This is a useful failure:
the candidate matches device anchors, amplifier current/gain sweep and coarse plate curves well, but its large-signal curvature generates distortion too early.

Therefore:
- static/mid-level fit quality is insufficient;
- the large-signal Philips Vi/Vo/distortion graph must be part of the optimization objective;
- knee/transfer curvature must be adjusted without sacrificing the successful DC and small-signal constraints.

Current status:
- retain parameter set as a strong intermediate baseline;
- do not promote to production;
- next pentode fit must jointly optimize static curves + small-signal tables + large-signal distortion.
