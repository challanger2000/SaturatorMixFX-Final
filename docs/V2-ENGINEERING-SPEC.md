# SMX-3 V2 Engineering Specification

Status: development baseline
Baseline: SMX-3 v0.1.1, main @ 98e3d7d0fa7eca2b2104b78c7ffc99cf06cf117d

## Product goal

SMX-3 V2 remains a compact saturation processor with two deliverables:

- SMX-3 Channel
- SMX-3 Mix FX

V2 must not become a reduced MixEngine. Its defining feature is three deliberately different hardware-inspired saturation paths:

- TRI0DE: small-signal audio triode stage, primary reference ECC83 / 12AX7
- PENTODE: small-signal audio pentode stage, primary reference EF86
- IRON: line-level audio transformer / magnetic-core saturation stage

The active processor is allowed to impart baseline hardware character at Drive = 0 when that behaviour follows the documented reference model. Bypass remains the neutral reference. Mix = 0 must be a true dry path unless a documented architecture and measurement demonstrate a better reason.

## Evidence policy

Every important model parameter must be classified as one of:

- MEASURED
- DOCUMENTED
- CIRCUIT DERIVED
- PHYSICS DERIVED
- PUBLISHED-PARAMETER DERIVED
- EMPIRICALLY TUNED
- ESTIMATED / APPROXIMATED

No empirically tuned value may be described as a hardware fact.

## V1 preservation

- main remains the immutable V1 stable reference during V2 development.
- V2 development occurs on v2.0.0-development or a descendant branch.
- Existing V1 parameter IDs 99-103 are preserved unless an intentional compatibility break is documented.
- Old five-double V1 processor state must remain readable by V2.
- New V2 state must be explicitly versioned.
- Channel and Mix FX must be regression-compared against each other for shared DSP behaviour.

## Reference architecture targets

### Triode

Reference family:
- ECC83 / 12AX7 common-cathode voltage-amplifier stage.

Required physical/electrical behaviours to investigate:
- plate-current dependence on plate and grid voltage;
- bias-dependent asymmetry;
- grid-current onset where applicable;
- cathode-bias / charge memory where justified;
- load-line interaction;
- level-dependent H2/H3 structure;
- frequency dependence arising from the actual surrounding circuit.

Primary technical basis:
- manufacturer ECC83/12AX7 characteristic data;
- Dempwolf / Zolzer physically motivated triode modelling;
- published WDF / virtual-analog triode work as comparison, not automatic implementation authority.

### Pentode

Reference family:
- EF86 low-noise audio pentode voltage-amplifier stage.

Required behaviours:
- plate and screen-grid interaction;
- pentode knee;
- screen-current behaviour where relevant;
- bias and screen-supply dependence;
- different harmonic progression from the triode;
- dynamic operating-point movement where justified by the chosen circuit.

Primary technical basis:
- Mullard / Philips EF86 data and documented audio circuits;
- established pentode equations cross-checked against characteristic curves.

### Iron

Reference family:
- high-quality line-level audio transformer driven into progressively nonlinear operation.

Required behaviours:
- flux proportionality to voltage/frequency;
- frequency-dependent saturation threshold;
- B-H hysteresis / memory;
- remanence and minor-loop behaviour where material;
- DC-bias sensitivity where applicable;
- leakage / magnetizing / winding effects where needed for the target bandwidth;
- harmonic progression versus level and frequency.

Primary technical basis:
- documented audio-transformer measurement data;
- Jiles-Atherton based magnetic modelling literature;
- real-time transformer-emulation literature.

## Mandatory measurement matrix

For each of TRI0DE, PENTODE and IRON, measure at minimum:

Input levels:
- -36, -30, -24, -18, -12, -9, -6, -3 dBFS

Frequencies:
- 40, 80, 100, 250, 1000, 5000, 10000, 15000 Hz where sample rate permits

Drive:
- 0, 10, 25, 50, 75, 100 %

Sample rates:
- 44.1, 48, 88.2, 96, 192 kHz

Metrics:
- fundamental gain;
- H2-H10;
- THD and THD+N where meaningful;
- SMPTE and/or CCIF IMD;
- DC offset;
- alias products / out-of-band foldback metric;
- frequency response;
- phase / group delay;
- crest-factor change;
- transient response;
- recovery / memory behaviour;
- output peak and RMS;
- deterministic repeatability.

For nonlinear comparisons, input and output level must be stated explicitly. Loudness-matched listening is supplemental, never the sole acceptance test.

## Oversampling / anti-aliasing decision

Do not assume V1's fixed 4x architecture is optimal.

Compare at minimum:
- 1x
- 2x
- 4x
- higher factors only when measurements justify them
- ADAA or other antialiasing approaches where mathematically compatible with the selected stateful model

Record:
- alias reduction;
- passband deviation;
- phase/group delay;
- latency;
- warm-up/state effects;
- CPU mean/p95/p99/max.

Prefer oversampling only around the nonlinear region unless end-to-end measurements prove otherwise.

## Host / realtime requirements

V2 must cover:
- 32-bit and 64-bit processing;
- mono->mono and stereo->stereo for SMX-3 Channel;
- Mix FX multichannel behaviour under the verified PreSonus/Fender host contract;
- variable block sizes;
- offline and realtime;
- automation at exact valid offsets;
- repeated activate/deactivate and editor lifecycle;
- state save/restore;
- silence;
- NaN/Inf;
- denormal/subnormal stress;
- no callback allocation, file/network I/O, logging or blocking locks;
- controlled bypass transitions;
- Ctrl + left-click reset to actual default on every custom continuous control.

## Shared DSP rule

The V2 Channel and Mix FX products should use one authoritative DSP implementation. Host integration remains separate. DSP duplication between targets should be removed only after a regression proves the refactor itself did not alter V1-equivalent behaviour unintentionally.

## Acceptance principle

No model is accepted because it is more complex.

A candidate must demonstrate:
1. closer agreement with documented hardware/circuit behaviour;
2. materially controlled aliasing;
3. stable state and automation;
4. acceptable realtime cost;
5. no unexplained level advantage;
6. successful VST3 / 125A regression QA.

The final judgement remains:

understand -> derive -> measure -> implement -> measure again -> regress -> verify host compliance -> judge quality
