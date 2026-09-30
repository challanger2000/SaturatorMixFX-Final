# SMX-3 V2 IRON Primary Reference

Status: primary physics + manufacturer target pinned

## Quantitative hardware target

Primary hardware archetype:
Jensen JT-11P-1 line-input transformer.

Manufacturer PDF:
https://www.jensen-transformers.com/wp-content/uploads/2014/08/jt-11p-1.pdf

### Manufacturer test circuit 1

The datasheet's principal line-level measurements use a 10 kOhm secondary load and, where specified, Rs = 600 Ohm.

Important target anchors:
- 1:1 nominal turns ratio;
- typical input impedance 13.0 kOhm at 1 kHz / +4 dBu;
- typical voltage gain -2.3 dB at 1 kHz / +4 dBu;
- typical relative response -0.04 dB at 20 Hz / +4 dBu / Rs=600 Ohm;
- typical relative response -0.05 dB at 20 kHz / +4 dBu / Rs=600 Ohm;
- typical THD <0.001 % at 1 kHz / +4 dBu / Rs=600 Ohm;
- typical THD 0.025 % at 20 Hz / +4 dBu / Rs=600 Ohm;
- typical +20 dBu at 20 Hz for 1 % THD;
- primary DCR 1.45 kOhm;
- secondary DCR 1.55 kOhm;
- typical turns ratio 1.000:1.

The published curves additionally supply:
- THD+N versus frequency for +4, +14 and +20 dBu;
- THD+N versus input level for 20, 30 and 50 Hz.

These curves, rather than a single waveshaper transfer curve, are the main V2 IRON fitting targets.

## Physical model candidate

Primary physics reference:
Martin Holters and Udo Zoelzer,
"Circuit Simulation with Inductors and Transformers Based on the Jiles-Atherton Model of Magnetization",
DAFx-2016.

Paper:
https://www.dafx.de/paper-archive/2016/dafxpapers/08-DAFx-16_paper_10-PN.pdf

### State definition

The paper uses magnetic field H and magnetization M as state variables.

Total magnetization is decomposed into reversible and irreversible parts, with the anhysteretic magnetization controlling both.

A key implementation feature is that the Jiles-Atherton differential relationship is rewritten with respect to time, making it directly usable inside a time-domain circuit solver.

### Electrical / magnetic linkage

For K windings with turns n_k and currents i_k, the paper gives the magnetic field in the idealized shared-core geometry as proportional to the sum of ampere-turns.

Flux is based on:
Phi = mu0 * A * (H + M)

and winding voltage follows Faraday:
v_k = n_k * dPhi/dt
    = mu0 * A * n_k * (dH/dt + dM/dt)

This relationship is central to SMX-3 IRON because it naturally makes magnetic state depend on volt-seconds. Therefore saturation behaviour must change with signal frequency.

### Jiles-Atherton model parameters

The DAFx paper's example uses the standard Jiles-Atherton parameter family:
- Ms: saturation magnetization
- a: anhysteretic-shape parameter
- alpha: mean-field parameter
- k: hysteresis-loop width parameter
- c: reversible/anhysteretic susceptibility ratio

Do not reuse the paper's example core parameters as JT-11P-1 parameters. The paper itself notes that its demonstration transformer is an illustrative circuit and is not a fitted model of the Jensen device.

## Required SMX-3 offline model

The first IRON implementation is an offline reference model, not a realtime approximation.

Required elements:
1. source resistance according to the selected Jensen test condition;
2. primary winding resistance;
3. magnetic core state using Jiles-Atherton;
4. ideal turns coupling;
5. secondary winding resistance;
6. 10 kOhm load;
7. parasitic capacitances added only after the low-frequency magnetic fit is established.

Unknown physical core geometry / material parameters must be fitted and labelled EMPIRICALLY TUNED TO DOCUMENTED MEASUREMENTS unless direct manufacturer core data become available.

## Fit sequence

### Stage 1 — linear anchors
Fit/check:
- 1 kHz gain;
- 20 Hz relative response;
- 20 kHz relative response;
- input impedance.

Do not use magnetic nonlinearity to compensate for errors that belong to winding resistance, magnetizing inductance or parasitic network.

### Stage 2 — low-frequency nonlinearity
Fit:
- 20 Hz / +4 dBu -> approximately 0.025 % THD;
- 20 Hz / +20 dBu -> approximately 1 % THD;
- full 20 Hz THD-vs-level curve after reproducible digitization.

### Stage 3 — frequency dependence
Fit/check:
- +4 dBu THD-vs-frequency;
- +14 dBu THD-vs-frequency;
- +20 dBu THD-vs-frequency;
- 20/30/50 Hz THD-vs-level relationship.

The model is rejected if it can hit 20 Hz / +20 dBu merely by changing a static threshold while failing the frequency dependence.

### Stage 4 — hysteresis/state tests
Measure:
- major B-H loop;
- minor loops;
- remanence after symmetric and asymmetric excitation;
- decay to stable state;
- DC-bias sensitivity;
- determinism after reset/state restore.

Any intentional remanence/state carried across transport or project state must be explicitly specified. Default project recall must remain deterministic.

## Realtime reduction rule

Only after the offline model fits the manufacturer evidence may a reduced realtime form be considered.

Candidates:
- direct bounded numerical integration;
- reduced state equation;
- fitted surrogate preserving level/frequency/memory behaviour;
- targeted oversampling around the nonlinear magnetic model.

Acceptance requires measured equivalence to the offline reference over the defined fixture set. CPU savings alone are not sufficient.

## Anti-aliasing note

Jiles-Atherton is stateful. Static ADAA assumptions cannot simply be applied as if IRON were a memoryless waveshaper.

Any ADAA/stateful-antialiasing approach must be derived for the actual state equations and compared against targeted oversampling by:
- alias energy;
- state accuracy;
- transient error;
- CPU p95/p99/max;
- stability.

## Immediate next measurement asset

Digitize the two Jensen THD plots with reproducible graph calibration.

The digitized CSV must include:
- curve name;
- x quantity/unit;
- y THD+N percent;
- source page;
- calibration coordinates;
- reading uncertainty estimate.

No hand-entered 'looks about right' points are accepted as final fitting data.


## Harmonic-structure / magnetization acceptance gate

Jensen/Whitlock's audio-transformer engineering chapter gives an important qualitative hardware diagnostic:

- an unmagnetized core exhibits nearly pure third-harmonic distortion with very little even-order distortion;
- residual DC magnetization can produce significant even-order distortion, in some cases H2 exceeding H3;
- a low-frequency test 30-40 dB below rated maximum operating level is described as particularly revealing for hysteresis distortion.

Evidence class:
DOCUMENTED qualitative manufacturer/engineering behavior.

SMX-3 consequence:

The IRON fit must not be accepted solely on total THD.

Required additional fixtures:
1. demagnetized symmetric low-frequency excitation:
   - record H2, H3, H4, H5 separately;
   - H3 should dominate the low-level magnetic distortion reference unless contrary JT-11P-1-specific evidence is found.
2. controlled DC-bias / remanence fixture:
   - intentionally offset magnetic state;
   - verify even-order growth, especially H2.
3. de-magnetization/reset fixture:
   - perform symmetric decaying excitation or explicit state reset;
   - verify return to the deterministic low-even-harmonic baseline.
4. project state policy:
   - do not accidentally preserve an arbitrary remanent core state across unrelated sessions;
   - if magnetic state is serialized, it must be deliberate and deterministic.

This gives a second dimension of hardware fidelity:
- THD magnitude vs level/frequency;
- harmonic composition vs magnetic history.


## Parameter-identifiability limitation

The JT-11P-1 data sheet exposes audio-domain input/output measurements, but not a complete measured B-H loop, core geometry, turns count, magnetic path length or material certificate.

Consequently:
- a Jiles-Atherton parameter set can be fitted to reproduce the audio evidence;
- it cannot automatically be interpreted as the unique physical material parameter set of the proprietary transformer.

The V2 IRON goal is therefore:
an electrically and magnetically plausible stateful model that simultaneously reproduces the documented transformer behaviour.

It is NOT:
reverse-engineering undocumented Jensen core construction and presenting fitted numbers as manufacturer facts.

This distinction is mandatory in code comments, research documentation and marketing claims.
