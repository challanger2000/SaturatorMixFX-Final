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
