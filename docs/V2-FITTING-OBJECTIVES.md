# SMX-3 V2 Fitting Objective Specification

## General rule

All nonlinear hardware fitting is multi-point and weighted.

A candidate is rejected if it only matches one headline number while materially missing:
- static curve shape;
- small-signal gain/current;
- large-signal distortion growth;
- frequency dependence;
- state/memory behavior.

All fit errors are evaluated in physically meaningful units before optional normalization.

## PENTODE objective

Primary source:
Philips EF86 4-Apr-1956.

### Stage A — device anchors
Targets:
- Va=250 V
- Vg2=140 V
- Vg1=-2 V
- Ia=3.0 mA
- Ig2=0.6 mA
- gm=2.0 mA/V

### Stage B — amplifier sweep
Circuit 1:
- Ra=100 kOhm
- Rg2=390 kOhm
- Rk=1 kOhm
- next-stage grid resistor=330 kOhm

Targets at Vb=200/250/300/350/400 V:
- Ik
- small-signal gain
- maximum output at 5% total distortion

### Stage C — plate-curve family
Primary curve sheet:
Ia versus Va at Vg2=140 V for multiple Vg1 curves.

Digitization requirements:
- at least 8 plate-voltage samples per selected grid curve;
- include knee and high-Va regions;
- at least Vg1 = 0, -1, -2, -3, -4 V;
- each point stores digitization uncertainty.

Metric:
use current-domain residual in mA, weighted so dense high-current areas do not dominate the knee.

### Stage D — screen-voltage transfer family
Fit/cross-check Ia versus Vg1 for several Vg2 values.

### Promotion gate
A parameter set may be promoted beyond provisional only if:
- device anchors stay within justified tolerance;
- amplifier Ik/gain sweep stays within justified tolerance;
- plate-curve normalized RMS error and maximum error are recorded;
- no systematic knee error remains;
- large-signal 5% output behavior is directionally and quantitatively consistent.

## IRON objective

Primary source:
Jensen JT-11P-1 manufacturer data.

### Stage A — linear circuit
Frozen/derived:
- Rp=1.45 kOhm
- Rs=1.55 kOhm
- turns ratio=1:1
- load=10 kOhm
- source=600 Ohm for cited tests
- low-level effective Lm ~144.0 H from the 20 Hz response anchor in test circuit 1 with Rs=600 Ohm

Targets:
- 1 kHz input impedance
- 1 kHz insertion gain
- 20 Hz relative response
- 20 kHz relative response
- phase deviation where modeled

### Stage B — nonlinear low-frequency anchors
Targets:
- 20 Hz/+4 dBu ~0.025% THD
- 20 Hz/+20 dBu ~1% THD

Both anchors must be fit simultaneously.

### Stage C — curve families
Digitize:
- THD+N vs frequency at +4/+14/+20 dBu
- THD+N vs input level at 20/30/50 Hz

Metric:
fit in log-THD space for the nonlinear curves so low-level and high-level regions both matter.

### Stage D — state behavior
Required:
- finite deterministic hysteresis;
- stable reset;
- no unbounded remanence drift;
- repeatable project recall;
- no NaN/Inf under defined stress.

### Promotion gate
A magnetic parameter set is rejected if a geometry rescale can match 1% THD but low-level THD misses materially.

The already tested unmodified DAFx example Jiles-Atherton shape is therefore a documented rejection as a Jensen fit.


## IRON parameter-identifiability rule

Jensen publishes electrical/audio measurements, not the transformer's complete magnetic B-H loops, core geometry, turns count and material-identification data.

Therefore the five Jiles-Atherton parameters cannot be claimed as uniquely identified physical core-material parameters from the JT-11P-1 audio curves alone.

Literature on Jiles-Atherton identification typically minimizes error against measured hysteresis loops and may require global search plus physical constraints. Multiple-loop fitting is preferred over single-loop fitting.

SMX-3 classification:
- geometry/core parameters inferred only from audio transfer/distortion data are EMPIRICALLY TUNED TO DOCUMENTED MEASUREMENTS;
- circuit values directly stated by Jensen remain DOCUMENTED;
- combinations mathematically derived from those values remain CIRCUIT DERIVED;
- no fitted parameter may be labelled as a Jensen material constant without direct manufacturer/core evidence.

Optimization strategy:
1. enforce physical bounds/constraints;
2. use global search for the magnetic shape;
3. refine locally after global convergence;
4. fit all available Jensen level/frequency curves simultaneously;
5. reject solutions with non-physical loops or unstable minor-loop/state behavior;
6. retain multiple near-optimal parameter sets during identifiability analysis;
7. prefer the simplest/stablest parameterization whose audio predictions are indistinguishable within source uncertainty.
