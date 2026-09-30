# SMX-3 V2 TRI0DE Settling-Time Correction

Date: 2026-09-30
Status: measurement-method correction

## Problem

The dynamic reference originally measured the final four cycles after simulating only eight cycles total.

That is not a valid settling criterion for the documented ECC83 network.

Relevant slow state:
- cathode bypass: 50 uF
- cathode resistor: 1.5 kOhm
- nominal RC product: ~75 ms

At:
- 1 kHz, 8 cycles = 8 ms
- 10 kHz, 8 cycles = 0.8 ms
- 20 kHz, 8 cycles = 0.4 ms

Therefore the original analysis window could contain substantial startup/bias-settling energy, especially when interpreted as harmonic distortion.

## Corrected method

Before the high-density analysis interval:

1. initialize the physical DC operating point;
2. drive the actual sine for 0.4 seconds;
3. use a resolved warm-up integration density;
4. carry the complete nonlinear/capacitive state into the high-density analysis interval;
5. analyze only the final steady-state cycles.

This is a physical-time settling criterion, not a fixed-cycle criterion.

## Representative correction

### 1 kHz, 10 mVrms

Former 8-cycle result:
- gain ~49.3234 V/V
- THD ~0.1933 %

After 0.4 s preconditioning:
- gain ~49.4353 V/V
- THD ~0.04314 %

### 10 kHz, 10 mVrms

Former 8-cycle result:
- gain ~49.9129 V/V
- THD ~0.5146 %

After physical-time preconditioning:
- THD falls to approximately 0.0432 %.

### 20 kHz, 10 mVrms

Former 8-cycle result:
- gain ~49.7679 V/V
- THD ~0.2951 %

After 0.4 s preconditioning:
- gain ~49.4715 V/V
- THD ~0.04322 %

## Interpretation

The former apparent rise in low-level HF THD was not credible tube behavior.

It was primarily a measurement artifact caused by analyzing a circuit whose slow cathode/coupling state had not reached periodic steady state.

After proper settling:
- low-level THD becomes highly consistent across the tested mid/HF range;
- gain values shift modestly because the bias/coupling state is now periodic;
- the numerical reference becomes suitable for later realtime residual testing.

## Nonlinear example

At 1 kHz / 0.70 Vrms:

Former short-run result:
- gain ~48.2336
- THD ~3.8734 %

After 0.4 s preconditioning:
- gain ~48.2228
- THD ~3.9020 %

The correction remains smaller than at 10 mVrms, but is still measurable.

## Consequences

The following old values are superseded wherever they were produced by the fixed-eight-cycle measurement sequence:
- low-level dynamic THD;
- dynamic gain where startup state materially contributed;
- any frequency comparison based on those unconditioned spectra.

DC results and the underlying nonlinear circuit equations are unaffected.

The dynamic reference tool, operating-domain probe and integration-method cross-check now use physical-time preconditioning.

## QA rule added

No future SMX-3 nonlinear reference measurement may use a fixed number of cycles as its only settling criterion when the modeled circuit contains slower state variables.

Settling time must be derived from:
- circuit time constants;
- measured convergence of the state/output;
- or both.
