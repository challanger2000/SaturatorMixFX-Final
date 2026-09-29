# SMX-3 V2 Model Decision Log

This file records technical decisions so rejected or provisional approaches are not silently resurrected later.

## TRI0DE

### EHX-1 Dempwolf/Zoelzer 12AX7 parameter set
Status: ACCEPTED AS FIRST OFFLINE REFERENCE CANDIDATE

Reason:
- published fit to a measured practical 12AX7 specimen;
- in the selected Mullard 250 V / 100 kOhm / 1.5 kOhm circuit, solved cathode current is within about 4.1 % of the manufacturer anchor;
- small-signal gain is within about 2.2 % of the Mullard anchor without empirical output trim.

Not yet accepted as production DSP:
- dynamic parasitics;
- large-signal harmonic behaviour;
- positive-grid-current cases;
- realtime cost and antialiasing
still require validation.

## PENTODE

### Circuit Codex CC0 EF86 Koren-form fit
Status: REJECTED AS FINAL HARDWARE REFERENCE; RETAINED AS COMPARISON BASELINE

Reason:
- reproduces its single later-Philips device anchor essentially exactly;
- DC current through the selected 1956 Philips amplifier is directionally useful;
- however, small-signal amplifier gain misses the 1956 manufacturer table by roughly 19-23 % across Vb=200..400 V;
- candidate KVB is a generic project default, not fit from EF86 plate curves;
- full Philips Ia(Va,Vg1,Vg2) curve family was not part of the fit.

Revisit only if:
- a new parameter fit is performed against the full Philips curve set and multi-supply amplifier table.

### Primary PENTODE authority
Status: PHILIPS EF86 4-Apr-1956 CURVES/TABLES

Later Philips handbook values remain independent cross-checks and evidence of edition/specimen-family variation.

## IRON

### V1 static/memory heuristic Iron code
Status: NOT ACCEPTED AS V2 HARDWARE REFERENCE

Reason:
- useful V1 sound baseline;
- not derived from a transformer circuit or measured magnetic core;
- cannot by itself establish physical line-transformer behaviour.

### Jensen JT-11P-1 linear skeleton
Status: ACCEPTED AS FIRST LINEAR HARDWARE REFERENCE

Documented values:
- 1:1 turns ratio;
- primary DCR 1.45 kOhm;
- secondary DCR 1.55 kOhm;
- 10 kOhm test load.

Circuit-derived result:
- these values explain approximately 13.0 kOhm 1 kHz input impedance;
- they explain approximately -2.28 dB insertion gain, matching the documented -2.3 dB typical value;
- fitting the documented -0.04 dB 20 Hz droop yields an effective low-level magnetizing inductance of about 106.55 H.

### Jiles-Atherton
Status: ACCEPTED AS OFFLINE MAGNETIC-MODEL CANDIDATE

Reason:
- stateful hysteresis;
- remanence;
- coercivity;
- physically links magnetic state to winding voltage/current;
- published realtime/circuit formulation exists.

Not yet accepted as production DSP or Jensen fit:
- Jensen-specific magnetic parameters and geometry are not known;
- must be fitted to manufacturer THD-vs-level/frequency curves;
- realtime numerical stability and CPU remain untested.

## General rule

No approach is promoted to production merely because:
- it is common in SPICE;
- it sounds plausible;
- it is more complex;
- it is branded "physical";
- it matches one data point.

Promotion requires multi-point agreement with the selected primary hardware evidence plus realtime/host QA.
