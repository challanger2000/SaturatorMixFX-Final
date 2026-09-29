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


## New research decisions

### Provisional refitted EF86 Koren-form candidate
Status: ACCEPTED AS PROVISIONAL MULTI-ANCHOR CANDIDATE; NOT FINAL

Reason:
- one parameter set reproduces the Philips-1956 device point closely;
- reproduces Ia, Ig2 and gm near the selected device anchor;
- reproduces circuit-1 cathode current across Vb=200..400 V within about 4.4% worst-case;
- reproduces circuit-1 small-signal gain across the same sweep within about 1.6% worst-case;
- no per-supply gain trim is used.

Not promoted because:
- full Ia(Va,Vg1) plate-curve family has not yet been included or validated;
- knee/output-resistance and large-signal distortion behavior are therefore not proven.

### DAFx example Jiles-Atherton shape scaled to Jensen
Status: REJECTED AS JT-11P-1 FIT

Reason:
- geometry/field scaling can make +20 dBu/20 Hz land near Jensen's 1% THD anchor;
- the same scaled model predicts about 0.153% at +4 dBu/20 Hz versus Jensen's ~0.025%;
- therefore the hysteresis SHAPE itself is wrong for the target, despite a correct qualitative frequency trend.

Retain:
- the coupled electrical/magnetic solver architecture;
- the low-level Lm constraint;
- the composite geometry parameterization;
- Jiles-Atherton as a model family.

Next requirement:
fit magnetic shape parameters to the full Jensen multi-level/multi-frequency curve set.


### Six-parameter EF86 candidate after large-signal gate
Status: REJECTED AS FINAL PENTODE MODEL

Reason:
- a parameter set can match Philips device current, screen current, gm, amplifier DC current and small-signal gain closely;
- when constrained by Philips 5% total-distortion output, the same simple model family cannot reproduce the whole 200-400 V large-signal envelope closely enough;
- representative compromise still misses 400 V maximum output by about 11.5%, 350 V by about 8.6%, and 300 V by about 6.5%, while the 250/200 V region is close.

Conclusion:
- do not keep forcing six Koren parameters;
- move to a curve-family model with independent knee/slope flexibility;
- full Philips plate curves and large-signal envelope remain simultaneous acceptance gates.

### EF86 screen/cathode dynamics
Status: MUST BE MODELED DELIBERATELY

Reason:
- manufacturer circuit uses a screen dropping resistor and bypass conditions that affect gain and overload;
- screen current contributes to cathode current;
- large-signal behaviour near the knee cannot be represented reliably by plate current alone.

Production implication:
- first offline reference keeps plate and screen currents separate;
- realtime reduction may simplify only after comparison against the reference circuit.
