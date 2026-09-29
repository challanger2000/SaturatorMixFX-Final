# SMX-3 V2 Hardware Reference Specification

Status: research reference, not production DSP
Branch: v2.0.0-development

This document pins the first concrete hardware reference circuits for TRI0DE, PENTODE and IRON. Values are kept separate by evidence class. No value in this file should be described as an exact clone of a named commercial product.

---

## 1. TRI0DE — ECC83 / 12AX7 common-cathode reference

### Selected reference operating point

Manufacturer source:
Mullard, "World Series Valves for Audio Equipment", ECC83 typical operating conditions as an R-C coupled A.F. amplifier with cathode bias.

Selected row:
- B+ / supply: 250 V — DOCUMENTED
- anode resistor Ra: 100 kOhm — DOCUMENTED
- cathode resistor Rk: 1.5 kOhm — DOCUMENTED
- grid resistor of following valve / documented load context: 330 kOhm — DOCUMENTED
- cathode current: approximately 0.86 mA — DOCUMENTED
- voltage gain: approximately 54.5 V/V — DOCUMENTED
- maximum output: approximately 26 Vrms at start of positive-grid-current limitation — DOCUMENTED
- distortion at that documented maximum-output condition: approximately 3.9 % — DOCUMENTED

The source table states that output voltage and distortion are quoted at the start of positive grid current and that at lower output voltages distortion is approximately proportional to output voltage.

### Tube model candidate

Primary model:
Dempwolf & Zoelzer, "A Physically-motivated Triode Model for Circuit Simulations", DAFx-2011.

The paper measures practical 12AX7 tubes and fits:
- cathode current Ik;
- grid current Ig;
- plate/anode current Ia = Ik - Ig.

Model equations:

softplus_C(x) = log(1 + exp(C*x)) / C

Ik = G * softplus_C(Va / mu + Vg)^gamma

Ig = Gg * softplus_Cg(Vg)^xi + Ig0

Ia = Ik - Ig

Voltages Va and Vg are referred to cathode potential.

### Selected measured-tube parameter set for the first reference solver

Use Dempwolf/Zoelzer EHX-1 as the initial measured-tube realization:

- G = 1.371e-3
- mu = 86.9
- gamma = 1.349
- C = 4.56
- Gg = 3.263e-4
- xi = 1.156
- Cg = 11.99
- Ig0 = 3.917e-8 A

Evidence class:
MEASURED/PUBLISHED-PARAMETER DERIVED from the paper's fitted EHX-1 specimen.

Reason for selecting EHX-1 rather than silently averaging the three specimens:
with the Mullard 250 V / 100 kOhm / 1.5 kOhm cathode-bias circuit, the EHX-1 fitted model reproduces the Mullard average operating point and gain substantially better than the two RSD parameter sets.

### Reproduced DC reference using EHX-1

Independent numerical solution of the selected circuit gives approximately:

- cathode current Ik: 0.8248 mA
- anode current Ia: 0.82477 mA
- grid current at idle: about 0.039 uA
- cathode voltage: 1.2372 V
- plate node voltage relative to ground: 167.52 V
- plate-to-cathode voltage: 166.29 V
- small-signal inverting voltage gain with AC-bypassed cathode and unloaded output: approximately -55.69 V/V

Manufacturer comparison:
- Mullard cathode current: about 0.86 mA
- Mullard gain: about 54.5 V/V

This agreement is strong enough to promote this circuit/model pair to the first TRI0DE V2 reference candidate, but it is not yet the final realtime implementation.

### Dynamic capacitances

Dempwolf/Zoelzer quote standard 12AX7 parasitic values:
- Cak = 0.9 pF
- Cgk = 2.3 pF
- Cag = 2.4 pF

Evidence class:
DOCUMENTED in the cited paper as standard datasheet values.

V2 requirement:
the reference solver must first reproduce DC and low-frequency transfer without parasitics, then add the parasitic network and demonstrate the expected high-frequency/Miller behaviour.

### TRI0DE acceptance targets

Before realtime optimization, the reference implementation must:
1. reproduce the EHX-1 current equations over the paper's stated measurement domain;
2. reproduce the selected Mullard operating point within documented tolerances;
3. reproduce the small-signal gain near 54.5 V/V without empirical output-gain correction;
4. demonstrate asymmetric harmonic growth with increasing input;
5. demonstrate positive-grid-current onset rather than adding an arbitrary clipping knee;
6. retain safe solver convergence for large valid input excursions.

---

## 2. PENTODE — EF86 R-C coupled audio stage

### Device reference

Mullard describes the EF86 as a high-gain pentode specially suited to preamplifier and input stages where hum, noise and microphony must be minimized.

Typical device point documented on the Mullard sheet:
- Va = 250 V
- Vg3 = 0 V
- Vg2 = 140 V
- Ia = 3.0 mA
- Ig2 = 0.6 mA
- Vg1 approximately -2 V to -2.2 V depending on source edition/table
- gm approximately 1.8 to 2.2 mA/V
- internal resistance approximately 2.5 MOhm
- grid-1 to grid-2 amplification factor about 38

These typical-characteristic values are device anchors, not automatically the selected amplifier circuit.

### Selected Mullard R-C amplifier row

From the Mullard "Typical Operating Conditions" table for EF86 as an R-C coupled A.F. amplifier, select the 250 V / 100 kOhm row:

- B+ / supply: 250 V — DOCUMENTED
- anode resistor Ra: 100 kOhm — DOCUMENTED
- cathode current Ik: approximately 2.05 mA — DOCUMENTED
- screen-grid feed resistor Rg2: 390 kOhm — DOCUMENTED
- cathode resistor Rk: 1.0 kOhm — DOCUMENTED
- following-stage grid resistor: 330 kOhm — DOCUMENTED
- documented maximum output: approximately 50 Vrms — DOCUMENTED
- documented distortion at that maximum-output condition: approximately 5 % — DOCUMENTED

The exact voltage-gain entry and all secondary table columns must be transcribed from the manufacturer scan into the machine-readable fixture before the pentode reference solver is frozen.

### Model strategy

Unlike TRI0DE, do not simply recycle the triode equation with different coefficients.

The pentode reference must include:
- control-grid dependence;
- screen-grid dependence;
- plate-voltage knee;
- finite plate resistance above the knee;
- screen current or an explicitly justified approximation;
- cathode-bias interaction;
- anode load line.

Candidate equation family:
- Koren-style pentode formulation as a starting mathematical family;
- parameters independently fitted/cross-checked against EF86 manufacturer curves;
- do not copy third-party fitted EF86 parameters into production as authority without reproducing their fit.

### PENTODE validation targets

Reference solver must match, at minimum:
- the Mullard typical point around Va=250 V, Vg2=140 V, Vg1 approximately -2.2 V;
- Ia approximately 3.0 mA and Ig2 approximately 0.6 mA at that device point;
- the chosen 250 V / 100 kOhm / 390 kOhm / 1 kOhm R-C amplifier DC operating point;
- plate-current curves at multiple Vg1 values;
- knee location versus screen voltage;
- small-signal gain and harmonic progression versus level.

No realtime pentode DSP is accepted until these static and dynamic reference tests pass.

---

## 3. IRON — line-level transformer reference

### Selected hardware archetype

Primary quantitative reference:
Jensen JT-11P-1 line-input transformer.

This is used as a line-level studio-transformer archetype. SMX-3 V2 must not be marketed or documented as a Jensen clone.

Manufacturer-documented properties in the stated test circuits:

- impedance ratio: 10 kOhm : 10 kOhm
- turns ratio: nominal 1:1
- input impedance at 1 kHz/+4 dBu with 10 kOhm load: typical 13.0 kOhm
- voltage gain at 1 kHz/+4 dBu: typical -2.3 dB
- magnitude response relative to 1 kHz at 20 Hz/+4 dBu/Rs=600 Ohm: typical -0.04 dB
- magnitude response relative to 1 kHz at 20 kHz/+4 dBu/Rs=600 Ohm: typical -0.05 dB
- THD at 1 kHz/+4 dBu/Rs=600 Ohm: typical <0.001 %
- THD at 20 Hz/+4 dBu/Rs=600 Ohm: typical 0.025 %
- maximum 20 Hz input for 1 % THD: typical +20 dBu
- primary DCR: typical 1.45 kOhm
- secondary DCR: typical 1.55 kOhm
- primary-to-shield/case capacitance: typical 98 pF
- secondary-to-shield/case capacitance: typical 110 pF
- turns ratio tolerance: 0.999:1 to 1.001:1

The manufacturer also publishes:
- THD+N versus frequency at fixed +4, +14 and +20 dBu input levels;
- THD+N versus input level at fixed 20, 30 and 50 Hz.

Those curves are mandatory digitization targets before IRON model fitting.

### Magnetic model strategy

Primary physical candidate:
Jiles-Atherton magnetization model in a circuit formulation following Holters & Zoelzer, DAFx-2016.

Required stateful behaviours:
- hysteresis loop;
- minor loops;
- remanence;
- frequency-dependent flux drive;
- saturation onset tied to volt-seconds rather than a frequency-independent waveshaper threshold.

Secondary comparison:
de Paiva / Pakarinen / Valimaki / Tikander realtime transformer model.

Important limitation:
their paper targets a tube-amplifier output transformer. Architecture may inform the solver, but SMX-3 parameters must be fitted against line-level transformer evidence.

### IRON acceptance targets

Before realtime optimization:
1. reproduce the JT-11P-1 low-level magnitude anchors;
2. reproduce <0.001 % region at 1 kHz/+4 dBu to the extent allowed by model/noise-definition differences;
3. reproduce the strong frequency dependence between 1 kHz and 20 Hz distortion;
4. reproduce approximately 1 % THD at 20 Hz near +20 dBu;
5. fit multiple points of the manufacturer's THD-vs-level and THD-vs-frequency curves, not just one threshold;
6. demonstrate hysteretic state behaviour without unstable DC drift;
7. document whether any transformer parasitics are omitted and the measured consequence.

---

## 4. Normalized plugin mapping comes after physical references

The physical reference solvers use volts, amperes and ohms.

Only after each reference behaves correctly will SMX-3 map DAW full-scale values onto the physical circuit.

That mapping must explicitly define:
- nominal digital reference level;
- nominal hardware operating level;
- Drive 0 % physical input drive;
- Drive 100 % physical input drive;
- headroom above nominal;
- output calibration.

Do not hide the mapping inside arbitrary waveshaper coefficients.

Drive 0 % may have nonzero hardware character if the selected physical circuit produces it.

Mix 0 % remains a separate dry-path semantic decision and is not part of hardware-drive calibration.

---

## 5. Next research gates

TRI0DE:
- machine-readable EHX-1 model fixture;
- DC/load-line solver;
- static transfer and harmonic reference generator;
- compare all three published tube specimens to manufacturer operating-point tolerance.

PENTODE:
- exact manufacturer-curve extraction;
- fit an independent EF86 pentode equation set;
- screen-current fit;
- solve selected R-C amplifier bias point.

IRON:
- digitize Jensen THD curves with recorded coordinates/error;
- implement offline Jiles-Atherton reference solver;
- fit low-frequency level dependence before any realtime simplification.

Only after these gates may production V2 DSP replace the V1 character engines.
