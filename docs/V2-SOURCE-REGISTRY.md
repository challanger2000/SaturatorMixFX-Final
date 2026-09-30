# SMX-3 V2 Source Registry

This registry is the implementation provenance record for SMX-3 V2. A source listed here is research evidence, not automatic permission to copy code. Equations, constants and circuit values used in production code must be traced to an evidence class in the engineering specification.

## Triode / ECC83 / 12AX7

### Philips ECC83 data handbook
URL: https://frank.pocnet.net/sheets/010/e/ECC83.pdf
Type: manufacturer data sheet / handbook scan
Evidence use: DOCUMENTED

Use for:
- characteristic curves;
- nominal electrical parameters;
- recommended operating conditions;
- load-line / bias reference;
- cross-checking any fitted 12AX7 model.

### Dempwolf & Zoelzer — A Physically-motivated Triode Model for Circuit Simulations
DAFx-2011
URL: https://dafx.de/paper-archive/2011/Papers/76_e.pdf
Archive page: https://dafx.de/paper-archive/details/MGMeIyM6_9oAzOgKCuzEqw
Evidence use: PUBLISHED-PARAMETER DERIVED / PHYSICS DERIVED after reproduction

Key reason for inclusion:
- explicitly models a 12AX7;
- continuously differentiable equations;
- includes grid current;
- parameters fitted against measured practical triodes;
- demonstrates the model embedded in amplifier simulation.

Implementation rule:
- reproduce its published response/curve examples independently before accepting any equation or fitted constant into the SMX-3 reference model.

## Pentode / EF86

### Mullard receiving-valve data / EF86
URL: https://frank.pocnet.net/other/Mullard/PD/rxvalves.pdf
Type: manufacturer documentation scan
Evidence use: DOCUMENTED

Use for:
- EF86 identity as a voltage-amplifying pentode;
- characteristic and operating data.

### Mullard audio valve data / EF86 RC-coupled amplifier conditions
URL: https://frank.pocnet.net/other/Mullard/mullard.pdf
Type: manufacturer application data
Evidence use: DOCUMENTED

Important documented content:
- EF86 operating conditions as an RC-coupled AF amplifier;
- supply, cathode, anode and grid resistor examples;
- gain/output/distortion operating points.

Implementation rule:
- select one explicit V2 reference circuit before coding the pentode engine;
- record all selected supply and component values;
- validate the DC operating point and published gain/distortion behaviour before realtime optimization.

## Iron / magnetic transformer behaviour

### Holters & Zoelzer — Circuit Simulation with Inductors and Transformers Based on the Jiles-Atherton Model of Magnetization
DAFx-2016
Archive page: https://www.dafx.de/paper-archive/details/S76rs5EkqeCL6m2FH0TDaQ
Evidence use: PHYSICS DERIVED after reproduction

Key reason for inclusion:
- rewrites Jiles-Atherton magnetization into a time-domain differential equation suitable for circuit simulation;
- explicitly exercises nonlinear inductor / transformer circuits;
- supplies a path toward real stateful magnetic hysteresis rather than a static waveshaper.

### de Paiva, Pakarinen, Valimaki, Tikander — Real-Time Audio Transformer Emulation for Virtual Tube Amplifiers
EURASIP Journal on Advances in Signal Processing, 2011
URL: https://link.springer.com/article/10.1155/2011/347645
DOI: 10.1155/2011/347645
License noted by publisher: CC BY 2.0
Evidence use: PUBLISHED-PARAMETER DERIVED / PHYSICS DERIVED after reproduction

Use for:
- realtime transformer-emulation architecture;
- comparison against Jiles-Atherton/circuit-derived alternatives;
- validation strategy for transformer-induced nonlinear behaviour.

Important limitation:
- the paper targets an output transformer in a tube amplifier. SMX-3 IRON targets a studio/line transformer archetype, so topology/parameters must not be transplanted blindly.



### Jensen JT-11P-1 line-input transformer
Manufacturer selector:
https://www.jensen-transformers.com/transformers/line-input/

Manufacturer data sheet:
https://www.jensen-transformers.com/wp-content/uploads/2014/08/jt-11p-1.pdf

Type: manufacturer specification and measured curves
Evidence use: DOCUMENTED / target curve source

Documented reference points useful for IRON validation:
- 10 kOhm : 10 kOhm nominal impedance ratio;
- 1:1 turns ratio;
- maximum 20 Hz input level approximately +20 dBu at 1% THD in the stated test circuit;
- typical THD about 0.025% at 20 Hz / +4 dBu;
- typical THD below 0.001% at 1 kHz / +4 dBu;
- typical magnitude response approximately -0.04 dB at 20 Hz and -0.05 dB at 20 kHz relative to 1 kHz in the stated test circuit;
- manufacturer plots provide THD vs frequency at fixed input levels and THD vs input level at fixed low frequencies.

Why this is important:
- it gives SMX-3 IRON a line-level studio-transformer reference instead of relying only on guitar-amplifier output-transformer literature;
- the level/frequency distortion curves provide quantitative targets for frequency-dependent magnetic saturation.

Rule:
- the JT-11P-1 is a reference archetype, not a claim that SMX-3 is a component-accurate Jensen clone;
- if its measured curves are digitized for fitting, record the digitization method and error bounds.

## Antialiasing

### Martin Holters — Antiderivative Antialiasing for Stateful Systems
DAFx-2019
URL: https://www.dafx.de/paper-archive/2019/DAFx2019_paper_4.pdf
Archive page: https://dafx.de/paper-archive/details/lp5GcJOo79OBkfcMfN3N_g
Evidence use: PUBLISHED-PARAMETER DERIVED / mathematical method

Use for:
- evaluating ADAA where the chosen nonlinear/stateful architecture satisfies the mathematical requirements;
- comparison against 1x/2x/4x oversampling.

Rule:
- ADAA is a candidate, not a predetermined choice. It must beat or complement oversampling under measured alias, passband, latency, transient and CPU criteria.

## Source quality / outstanding acquisitions

Still required before model freeze:
- exact chosen ECC83 common-cathode reference circuit with component values and documented operating point;
- exact chosen EF86 pentode reference circuit and characteristic curves for the selected screen/anode conditions;
- at least one line-level audio-transformer manufacturer data set with low-frequency level-vs-THD/saturation evidence;
- primary Jiles-Atherton parameter reference and parameter-identification method suitable for the selected transformer;
- exact current Steinberg VST3 host/API references for state, process data, bypass, bus negotiation and realtime lifecycle;
- if physical hardware measurements become available later, add them as MEASURED evidence rather than silently replacing published data.

## Reproduction gate

A source is not considered an implementation authority until:
1. exact version/date is pinned;
2. equations/curves needed by SMX-3 are extracted;
3. a standalone reference calculation reproduces at least one published/table/curve result within a documented tolerance;
4. units/sign conventions are verified;
5. the realtime implementation is compared back to that reference calculation.


### Philips Electron Tubes Part 4 — EF86 operating characteristics (May 1973)
URL: https://frank.pocnet.net/other/Philips/elcoma/Philips_ElectronTubes_4_1975-03.pdf
Type: manufacturer receiving-tube handbook
Evidence use: DOCUMENTED

For the selected EF86 R-C amplifier at Vb=250 V, Ra=100 kOhm, Rg2=390 kOhm, Rk=1 kOhm, next-stage grid resistor=330 kOhm, the table gives:
- Ik = 2.0 mA
- small-signal voltage gain = 123 V/V
- output voltage = 50 Vrms
- total distortion = 5 % at the stated maximum-output condition

This source also supplies the same circuit over Vb=150..400 V, which is a stronger multi-point validation target than a single operating point.

### Circuit Codex EF86 CC0 Koren-fit candidate
URL: https://github.com/TheAnalogMaker/circuit-codex/blob/main/models/ef86.inc
Methodology: https://github.com/TheAnalogMaker/circuit-codex/blob/main/models/METHODOLOGY.md
License stated in model: CC0 1.0 Universal
Evidence use: comparison candidate only

Published candidate parameters:
- MU=38
- EX=1.5
- KG1=1051.45
- KG2=3013.64
- KP=143.216
- KVB=30

The model is fitted to the Philips/Mullard 250 V / 140 V / -2.2 V device anchor, not to the full plate-curve family. It must therefore be treated as a useful independent baseline, not hardware ground truth.


### Cohen & Helie — Real-Time Simulation of a Guitar Power Amplifier
DAFx-2010
URL: https://www.dafx.de/paper-archive/2010/DAFx10/CohenHelie_DAFx10_P45.pdf
Evidence use: implementation-method comparison

Relevant points:
- treats pentode/beam-tetrode current models as phenomenological curve fits rather than fundamental hardware laws;
- notes that correct knee behaviour materially affects realism;
- models control-grid current with a smooth diode-like transition;
- uses extended nonlinear state-space equations and implicit numerical treatment for realtime circuit simulation;
- reports that pentode/tetrode parasitic capacitances have much less audible-band influence than triode Miller capacitance in the studied power-stage context.

Use in SMX-3:
- support for explicit knee validation;
- support for treating grid current as a separate large-signal mechanism;
- numerical-method reference only, not an EF86 parameter source.

### Valve Wizard — Small Signal Pentode design notes
URL: https://www.valvewizard.co.uk/pentode.html
Evidence use: secondary engineering interpretation / sanity check

Relevant points:
- screen voltage materially changes the plate-curve family;
- screen current is part of cathode current and changes operating point;
- the EF86 example uses the data-sheet ratio around Ia=3.0 mA / Ig2=0.6 mA away from the knee;
- screen bypassing materially affects stage gain;
- plate-curve knee/load-line placement changes headroom and asymmetry.

Use in SMX-3:
- topology sanity checks and interpretation only;
- not a replacement for Philips manufacturer curves.

### Image-fitted EF86 SPICE model family (diyAudio / paint_kip)
Example source:
https://www.diyaudio.com/community/threads/vacuum-tube-spice-models.243950/page-93

Evidence use: comparison candidate / model-family research only

Why useful:
- explicitly fitted to published EF86 plate-curve images;
- adds independent knee, plate-slope and kink terms beyond classic six-parameter Koren;
- demonstrates that higher-fidelity curve matching generally needs more degrees of freedom than the simple Koren form.

Restriction:
- community-derived parameters are not treated as primary hardware evidence;
- no production parameter is copied merely because it exists in a SPICE model.


### Philips/Mullard ECC83 operating-characteristics circuit, January 1970
URL: https://frank.pocnet.net/sheets/010/e/ECC83.pdf
Type: manufacturer data sheet
Evidence use: DOCUMENTED

Selected A.F.-amplifier row:
- Vb=250 V
- Ra=100 kOhm
- Rg' next-stage load=330 kOhm
- Rk=1.5 kOhm
- Ia=0.86 mA
- gain=54.5
- Vo=26 Vrms at the stated Ig=0.3 uA criterion
- total distortion=3.9%

Published circuit diagram:
- input coupling C=0.01 uF
- input grid leak=1 MOhm
- cathode bypass Ck=50 uF
- output coupling C=0.01 uF

This is now the authoritative surrounding network for the dynamic TRI0DE reference unless later primary evidence justifies a deliberate alternative.
