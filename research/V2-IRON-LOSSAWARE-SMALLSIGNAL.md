# SMX-3 V2 IRON Loss-Aware Small-Signal Target

Date: 2026-09-30
Status: STRONG SMALL-SIGNAL TARGET — not yet the nonlinear production model

## Why this model exists

The corrected pure-inductor baseline (~144 H) reproduces Jensen's 20 Hz
magnitude only if core loss is ignored.

That same lossless assumption produces too much deviation from linear phase.

Jensen independently constrains:
- 20 Hz magnitude;
- 20 kHz magnitude;
- approximately 95 kHz upper bandwidth;
- 1 kHz input impedance / gain;
- DLP through the audio band.

Therefore a useful linear target must include a dissipative magnetic term.

## Reduced passive topology

Documented:
- response-test source resistance: 600 Ohm;
- primary DCR: 1.45 kOhm;
- secondary DCR: 1.55 kOhm;
- load: 10 kOhm;
- primary-to-shield capacitance: 98 pF;
- secondary-to-shield capacitance: 110 pF.

Effective fitted quantities:
- magnetizing inductive term Lmag ~922.41 H;
- magnetic-loss term Rmag ~38.99 kOhm in series with Lmag;
- leakage inductance ~2.7504 mH;
- extra effective shunt/interwinding capacitance ~1.15485 nF.

These values are EMPIRICALLY TUNED TO DOCUMENTED MEASUREMENTS.
They are NOT claimed as Jensen construction/component values.

## Representative agreement

Approximate:
- 1 kHz transformer gain: -2.278 dB;
- 1 kHz input impedance: ~12.94 kOhm;
- 20 Hz relative response: -0.03999 dB;
- 20 kHz relative response: -0.04990 dB;
- 95 kHz relative response: -2.999 dB.

DLP after best linear-phase removal:
- low-frequency maximum ~+0.60 degrees;
- minimum roughly -0.14 degrees;
- remains well inside Jensen +/-2 degree maximum.

This matches the shape visible in the Jensen DLP graph:
largest positive deviation at the bottom of the audio band, approaching zero
through the mid/high band.

## Interpretation

The key result is architectural, not the exact fitted numbers:

A **loss-aware magnetic impedance** is required to explain Jensen's magnitude
and phase simultaneously.

A lossless Lm cannot.

The current Jiles-Atherton implementation models quasi-static hysteresis but
does not explicitly model all frequency-dependent core/eddy-current loss
mechanisms.

Therefore the production IRON path should be:

1. retain the stateful nonlinear Jiles-Atherton core for:
   - saturation;
   - hysteresis;
   - remanence;
   - H3/H2 behavior;
   - level-dependent THD;

2. add a physically defensible dynamic-loss mechanism whose low-level
   small-signal impedance approaches this loss-aware target;

3. add HF leakage/capacitive parasitics;

4. re-fit only the effective parameters needed to satisfy the complete Jensen
   multi-domain evidence.

## Important consequence for the 144 H baseline

~144 H remains useful as the corrected **lossless-equivalent** inductance.

It is not the final physical magnetizing inductance once a dissipative
frequency-dependent magnetic branch is admitted.

## Promotion blockers

Before using this topology in production DSP:
- derive a causal time-domain core-loss realization;
- determine whether a simple relaxation branch is sufficient or whether an
  eddy-current term is required;
- combine with Jiles-Atherton without double-counting hysteresis loss;
- re-run exact THD anchors;
- re-run DLP;
- re-run remanence/DC-bias behavior;
- measure realtime CPU/aliasing/stability.
