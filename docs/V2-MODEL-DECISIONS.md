# SMX-3 V2 Model Decision Log

This file records technical decisions so rejected or provisional approaches are not silently resurrected later.

## TRI0DE

### EHX-1 Dempwolf/Zoelzer 12AX7 parameter set
Status: SUPERSEDED AS PRIMARY TRI0DE REFERENCE; RETAINED AS MEASURED-SPECIMEN CROSS-CHECK

Reason for supersession:
- published fit to a measured practical 12AX7 specimen remains valuable;
- the earlier gain comparison used the unloaded plate node;
- once the documented 330 kOhm following-stage load is included, EHX-1 predicts about 50.22 V/V versus Mullard 54.5 V/V;
- therefore the earlier ~2.2% gain agreement was not the correct loaded-circuit comparison.

Retain EHX-1 as an independent measured-tube cross-check, especially for grid-current law and specimen variability.

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


### IRON harmonic composition / remanence
Status: REQUIRED ACCEPTANCE DIMENSION

Jensen/Whitlock documents that an unmagnetized transformer core is expected to show predominantly third-harmonic distortion, while residual magnetization creates significant even-order distortion and can make H2 exceed H3.

Therefore:
- total THD alone is insufficient;
- H2/H3 and magnetic-history tests become mandatory;
- the fitted model must react plausibly to DC bias/remanence and return deterministically to a demagnetized baseline.

This requirement strengthens the case for a stateful magnetic model and rules out any final IRON implementation that merely matches a scalar THD curve with a memoryless symmetric waveshaper.


### EHX-1 loaded-amplifier reassessment
Status: BEST PUBLISHED MEASURED-SPECIMEN STARTING POINT; NOT FINAL TRI0DE REFERENCE

Correction:
the earlier apparent ~2.2% gain agreement used an unloaded small-signal calculation. Including Mullard's documented 330 kOhm following-stage AC load gives approximately 50.22 V/V versus 54.5 V/V.

Large-signal check at the documented grid-current condition:
- EHX-1 ~32.52 Vrms / 3.42% THD
- Mullard ~26 Vrms / 3.9% THD

Decision:
retain EHX-1 as the most useful Dempwolf/Zoelzer specimen, but require a joint current-surface + loaded-circuit + large-signal fit before promotion.


### TRI0DE authority split: measured specimen vs manufacturer average
Status: ACCEPTED

Primary tube authority:
- Dempwolf/Zoelzer EHX-1 measured 12AX7 specimen parameter set.

Primary circuit archetype:
- Mullard ECC83 cathode-biased R-C amplifier family.

Cross-check role of Mullard:
- verify that the measured specimen behaves plausibly within the ECC83/12AX7 hardware class;
- provide practical bias/load/topology anchors;
- do NOT force the measured EHX-1 specimen to equal Mullard average-production numbers exactly.

Reason:
Dempwolf/Zoelzer explicitly note that real tubes of the same type/manufacturer may deviate materially from one another (the paper cites variation up to about 20%). A specimen-accurate measured model is therefore more physically honest than empirically bending it to an average datasheet table.

Consequence:
- EHX-1 current-surface/grid-current fit remains the TRI0DE tube reference;
- Mullard loaded gain/output/distortion differences are documented as cross-source variation;
- no arbitrary trim will be added to make the EHX-1 specimen pretend to be an average Mullard specimen;
- the selected surrounding circuit may use documented Mullard-style values, but the resulting signal behavior is allowed to reflect the EHX-1 specimen.


### Mullard-loaded ECC83 multi-point fit
Status: ACCEPTED AS PROVISIONAL TRI0DE MANUFACTURER-TABLE CANDIDATE; NOT FINAL

Reason:
- uses the Dempwolf/Zoelzer physically motivated equation family;
- includes the documented 330 kOhm following-stage AC load;
- one parameter set fits all five Mullard 100 kOhm amplifier rows (Vb=200..400 V);
- worst cathode-current error is about 0.92%;
- worst small-signal gain error is about 1.89%;
- no per-row output trim is used.

Not promoted because:
- plate-current curve family not yet validated;
- grid-current parameters are still borrowed provisionally from EHX-1;
- large-signal distortion/output limits have not yet been reproduced.


### Mullard-loaded ECC83 small-signal fit — large-signal status
Status: RETAINED AS SMALL-SIGNAL FIT ONLY; REJECTED AS FINAL TRI0DE MODEL

Reason:
- excellent DC-current and loaded small-signal-gain agreement over Vb=200..400 V;
- but at the documented positive-grid-current onset the model predicts about 36.6 Vrms and 6.44% H2-H10 THD;
- Mullard documents about 26 Vrms and 3.9% total distortion.

Consequence:
TRI0DE model selection now requires simultaneous small-signal and large-signal agreement. A local operating-point fit is insufficient.


## 2026-09-30 follow-up decisions

### Generalized beta EF86 surrogate
Status: LOCAL PROVISIONAL SURROGATE ONLY; REJECTED AS FINAL PENTODE MODEL

Evidence:
- strong agreement around the 200-250 V operating region;
- ~49.2 Vrms at 5% THD versus Philips 50 Vrms at 250 V;
- acceptable coarse plate-curve residual;
- but exact Philips 5%-THD envelope diverges increasingly above 250 V:
  - ~57.7 V vs 64 V at 300 V;
  - ~65.8 V vs 75 V at 350 V;
  - ~73.6 V vs 87 V at 400 V.

Consequence:
do not freeze PENTODE production DSP from the generalized beta model.
Use it as a compact local/realtime comparison baseline only.

### Extended EF86 knee/kink family
Status: ACCEPTED FOR INDEPENDENT REFIT RESEARCH; community parameters remain rejected

Reason:
the family has explicit degrees of freedom for:
- low-plate-voltage knee;
- finite plate slope;
- kink behavior;
- screen coupling;

and the published comparison set shows substantially better large-signal envelope shape despite incorrect absolute current/screen-current calibration.

Fit strategy:
1. fit static Philips Ia surfaces, device anchors, DC-current sweep and small-signal gain;
2. freeze/regularize those parameters;
3. fit remaining knee/kink degrees of freedom against exact 5%-THD supply envelope and Graph-D trajectory;
4. re-run all static gates after the large-signal stage;
5. reject any solution that improves the envelope by destroying the primary current surfaces.

### IRON magnetic settling
Status: MEASUREMENT METHOD CORRECTED

A finite-cycle startup state can create apparent even-order distortion in the coupled Jiles-Atherton probe.

After sufficient periodic-state warmup:
- H2 collapses to effectively negligible levels;
- H3 strongly dominates;
- the model agrees qualitatively with Jensen/Whitlock parity behavior.

The DAFx example parameter shape remains rejected as a JT-11P-1 fit because its low-level THD remains far too high (~0.158% vs ~0.025% at +4 dBu/20 Hz) while the +20 dBu point remains near 1%.

Future IRON harmonic analysis requires explicit magnetic periodic-state convergence or an explicit demagnetization/state protocol.


### EF86 staged manufacturer-data fit
Status: STAGE-1 ACCEPTED; STAGE-2C ACCEPTED AS MINIMAL STATIC CANDIDATE; LARGE-SIGNAL STAGE STILL OPEN

Stage 1:
- independently fitted to Philips Graph A/B plus Ia/gm/ri anchors;
- NRMS ~0.497 sigma;
- Graph A ~0.460 sigma;
- Graph B ~0.500 sigma;
- no fit parameter within 2% of arbitrary search bounds.

Accepted Stage-1 parameters:
- MU = 42.1294068459
- EX = 1.48016674106
- KG1 = 2059.06189749
- KP = 215.816749098
- VCT = 0.761562843483
- KVB_SCREEN = 430.818432714
- LAMBDA = 0.000160501489918

Stage 2 simple screen law:
REJECTED.
- NRMS ~2.484 sigma;
- EX_G2 pinned to lower bound;
- max gain error ~5.94%.

Stage 2B coupled plate/screen knee:
REJECTED AS PARAMETERIZATION.
- Graph-B fit improved materially;
- but KNEE and KG2 hit arbitrary search bounds;
- therefore scale/shape terms were not independently identified.

Stage 2C minimal reparameterization:
ACCEPTED AS MINIMAL STATIC CANDIDATE.
- KNEE = 3.35311366202 V
- S0 = 9.02342723159e-5
- S1 = 0

Evidence:
- objective NRMS ~0.832 sigma;
- Graph B NRMS ~0.442 sigma;
- max cathode-current error ~2.39%;
- max small-signal gain error ~3.43%.

Interpretation:
the data identify a plate-voltage knee as the important missing mechanism.
They do NOT identify an additional explicit plate-voltage-dependent screen-current correction: S1 collapses to zero.

Remaining caution:
- device Ig2 remains ~0.550 mA vs Philips ~0.600 mA;
- inferred ri remains ~1.73 MOhm vs Philips typical ~2.5 MOhm;
- these discrepancies remain visible and may not be hidden with output gain compensation.

Next promotion gate:
out-of-fit exact Philips 5%-THD envelope plus Graph-D compression/distortion trajectory. Only the minimum additional large-signal curvature justified by those residuals may be introduced.


### TRI0DE measured-specimen authority correction — RSD-2
Status: RSD-2 PROMOTED TO PRIMARY OFFLINE SPECIMEN; EHX-1 RETAINED AS CROSS-CHECK

Reason:
- the earlier EHX-1 authority choice was historical rather than the result of the final loaded manufacturer comparison;
- RSD-2 gives the best current combined match to Mullard idle current, documented 330 kOhm-loaded gain and the 26 Vrms distortion anchor;
- RSD-2 remains numerically stable in the same complete dynamic network;
- Dempwolf/Zoelzer do not establish EHX-1 as the uniquely authoritative circuit-test specimen in the paper text.

Current static manufacturer comparison at 250 V:
- RSD-2 Ik error ~-2.86%;
- loaded gain error ~+5.52%;
- distortion at 26 Vrms ~3.70% versus Mullard ~3.9%.

Representative dynamic comparison:
- RSD-2 low-level midband gain ~1.14 dB above EHX-1;
- RSD-2 harmonic growth is stronger, consistent with its closer manufacturer large-signal result.

This supersedes any earlier Decision Log section that names EHX-1 as the primary TRI0DE tube authority.

Required after promotion:
- rerun dynamic convergence;
- rerun independent integration-method cross-check;
- rerun operating-domain boundary;
- keep EHX-1 as specimen-variation fixture.


### IRON realtime magnetic integration
Status: HOST-RATE MIDPOINT ACCEPTED AS PRIMARY REALTIME CANDIDATE

Evidence:
- explicit midpoint/RK2 at 48 kHz compared against RK4 at 192 kHz;
- tested +4/+20 dBu at 20/50/100 Hz and +20 dBu at 1 kHz;
- worst THD residual ~0.0000051 percentage-points;
- worst H3 residual ~0.0000138 percentage-points.

Decision:
- do not use fixed 4x oversampling merely for H/M numerical accuracy;
- evaluate alias control separately;
- first production candidate should keep magnetic state integration at host rate and add targeted oversampling only if alias measurements justify it.


### EF86 dynamic Graph-D diagnosis
Status: DYNAMIC-NETWORK EXPLANATION REJECTED

Evidence:
- EX=1.40 dynamic Philips network reproduces midband gain within ~1.53%;
- Graph-D Vi->Vo remains close;
- low/mid output THD remains too high and top-end THD remains low;
- real cathode/screen/output dynamics do not remove the residual pattern.

Decision:
reopen only an existing control-grid transfer-shape degree of freedom next (KP), while re-solving VCT/KG1/S0 to preserve exact local Ia/gm/Ig2. Do not add an external waveshaper or gain correction.


### EF86 KP curvature reopening
Status: CLOSED — NO JUSTIFIED MODEL CHANGE

A coarse EX x KP scan with exact Ia/gm/Ig2 recalibration found that only KP around ~220 consistently clears the stronger Graph A/B, gain/current and exact Vo@5% gates.

The original Stage-1 KP (~215.8) already occupies this region.

Graph-D THD residual does not materially improve across eligible KP candidates, and the current low-level Graph-D manual digitization is not reliable enough to justify another degree of freedom.

Decision:
retain EX≈1.40 and the Stage-1 KP region. Do not tune the pentode model against uncertain Graph-D low-level points.


### IRON oversampling — coherent harmonic-fold checkpoint
Status: DEFAULT 1X HYPOTHESIS STRENGTHENED

Corrected coherent high-rate analysis at +20 dBu gives worst estimated
nonlinear foldback near -108.4 dBc at 1x/48 kHz, improving to about -117 dBc
at 2x and -127.8 dBc at 4x.

At 5-10 kHz the 1x estimate is already below about -127 dBc because magnetic
distortion falls strongly with frequency.

Decision:
do not design IRON around fixed oversampling. Proceed with host-rate midpoint
as the primary realtime candidate and require a direct band-limited waveform
residual test before freezing 1x.


### IRON direct 1x waveform checkpoint
Status: HOST-RATE 1X PROMOTED TO PRIMARY PRODUCTION HYPOTHESIS

Direct 48 kHz midpoint/RK2 output versus ideal band-limited high-rate RK4
authority gives worst tested periodic-sine residual ~-87.7 dB.

Together with:
- negligible midpoint-vs-RK4 state error;
- coherent alias-risk estimate <=~-108 dBc;

this removes the technical justification for blanket IRON oversampling in the
current model.

Final 1x freeze still requires 44.1 kHz, multitone/transient and C++ realtime
QA.


### IRON host-rate multitone checkpoint
Status: 1X HOST-RATE ARCHITECTURE NEAR-FROZEN

Direct four-tone IMD waveform residual:
- 44.1 kHz: ~-96.46 dB
- 48 kHz: ~-97.86 dB

Together with the sine/direct/alias/state results, fixed IRON oversampling is now rejected as unnecessary for the current physical model.

Remaining offline freeze gate:
- transient/burst excitation.

### PENTODE oversampling checkpoint
Status: 1X REJECTED; 4X PRIMARY STRAIGHTFORWARD CANDIDATE; 2X ALTERNATIVE

Coherent physical harmonic-fold estimate at strong drive:
- 1x worst ~-39.6 dBc;
- 2x worst ~-80.0 dBc;
- 4x worst ~-156.6 dBc.

Dynamic numerical accuracy also improves from 1x -> 2x -> 4x.

Decision:
benchmark 4x as the reference production architecture and compare against any lower-cost 2x + targeted antialias method. Do not ship the strong EF86 path at 1x.


### TRI0DE realtime numerical architecture
Status: BRUTE-FORCE FULL-MNA OVERSAMPLING REJECTED

The full dynamic ECC83 MNA requires roughly:
- 8x for merely plausible strict HF numerical agreement;
- 16x for strong full-band agreement under the current benchmark.

This is driven by Miller/interelectrode-network discretization, not proven
alias requirements.

Decision:
do not implement TRI0DE by simply running the full offline MNA at 16x.
Develop a reduced/exactly discretized linear-capacitive network around the
validated nonlinear tube current law, then select oversampling separately from
alias measurements.


### EF86 Stage-2 joint static candidate
Status: STRONG PROVISIONAL STATIC CANDIDATE

Reason:
- one coupled plate/screen parameter set clears the current Graph A/B surfaces;
- reproduces Ia, Ig2, gm and Ri closely;
- reproduces Philips circuit-1 Ik(Vb) and small-signal gain(Vb) without per-supply correction.

Limitation:
- large-signal 5%-THD envelope remains too early without Stage-3 knee correction.

### EF86 Stage-3 localized knee candidate
Status: STRONG PROVISIONAL LARGE-SIGNAL CANDIDATE

Reason:
- localized low-Va correction leaves normal Graph-A/B operating region essentially untouched;
- exact 5%-THD supply envelope is now within roughly 0.3-4.2%;
- Graph-D input/output compression trajectory is very close to provisional manufacturer reads.

Remaining limitation:
- Graph-D intermediate distortion points are not yet calibrated strongly enough for another free fit parameter;
- control-grid current and dynamic input network are still missing.

### EF86 control-grid current
Status: REQUIRED FOR FINAL DYNAMIC PENTODE REFERENCE

Cross-source EF86/6267 data place Ig1≈0.3 uA near Vg1≈-1.3 V.

Consequence:
the final dynamic PENTODE model must include control-grid current and input-network state before production Drive calibration is frozen.


### EF86 knee-aware static refit
Status: REJECTED AS COMPLETE PENTODE MODEL; RETAINED AS STAGED IDENTIFIABILITY EVIDENCE

Evidence:
- Graph A screen-family NRMS ~0.78 sigma;
- Graph B plateau NRMS ~0.71 sigma;
- Graph B knee NRMS ~0.88 sigma;
- exact device anchors remain close;
- but out-of-fit Vo@5% envelope collapses badly (e.g. ~21.7 V vs Philips 50 V at 250 V).

Consequence:
- static/small-signal current surfaces and large-signal/kink behavior must be identified as separate parameter blocks;
- do not let large-signal terms compensate Graph A/B current physics;
- do not promote any parameter set with weakly identified screen-current constants merely because aggregate fit cost is low.
