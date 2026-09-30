# SMX-3 V2 IRON LqS / c / KI Constrained Refit

Date: 2026-09-30
Status: decisive simplification test

## Question

Before adding new dynamic-loss states, can the existing stateful Jiles-Atherton
family satisfy Jensen simply by allowing the quasi-static low-field inductive
scale to rise and re-fitting the already existing c/KI parameters?

This is necessary because:
- ~144 H is only a lossless-equivalent baseline;
- the loss-aware Jensen small-signal target suggests an inductive scale near
  ~900 H;
- the first L_qs screen showed ~900 H already matches target susceptance much
  better than 144 H.

## Procedure

For each L_qs:
1. solve KI so +20 dBu / 20 Hz returns to 1% THD;
2. solve c so +4 dBu / 20 Hz returns to 0.025% THD;
3. evaluate:
   - H2/H3;
   - complex magnetic admittance vs Jensen loss-aware target;
   - DLP;
   - 20 Hz / 1 kHz magnitude;
   - 20 kHz / 1 kHz magnitude.

No dynamic Classical or Excess loss term is active.

## Decision rule

If one L_qs/c/KI solution satisfies the independent THD and DLP evidence:
prefer the simpler quasi-static state model and reject unnecessary added
dynamic-loss complexity.

If not:
the dynamic-loss extension remains justified, now with L_qs treated as an
identified parameter rather than frozen at 144 H.
