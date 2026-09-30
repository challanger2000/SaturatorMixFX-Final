# SMX-3 V2 Shared DSP Architecture

Status: design freeze before implementation

## Goal

SMX-3 Channel and SMX-3 Mix FX must execute one authoritative DSP core.

Host integration remains separate:
- Channel owns VST3 bus negotiation / ordinary process callback.
- Mix FX owns PreSonus/Fender Audio Mix Processor integration and per-channel host state.

The shared core must not know about:
- Steinberg interfaces;
- PreSonus proprietary interfaces;
- controller/editor classes;
- repository packaging.

## Proposed layout

SMX3Common/
  DSP/
    Smx3Core.h
    Smx3Core.cpp
    Smx3State.h
    Smx3Parameters.h
    Smx3Oversampling.h
    Smx3TriodeReference.h/.cpp
    Smx3PentodeReference.h/.cpp
    Smx3IronReference.h/.cpp

tests/
  dsp/
    v1_equivalence/
    triode/
    pentode/
    iron/
    state/
    realtime/

This structure is conceptual until the V1-equivalence test is in place.

## Core interface

The shared production core should have an interface equivalent to:

- prepare(sampleRate, maxBlockSize)
- reset()
- processSample(input, channelState, parameters)
- optional processBlock(...) thin wrapper

The core owns no heap allocations in the realtime path.

Channel state is fully caller-owned so:
- ordinary stereo Channel can hold 1-2 states;
- Mix FX can hold one state set per host channel;
- reset/state lifetime stays explicit.

## Parameter contract

Existing compatibility-sensitive IDs remain host-layer responsibilities:
- 99 Bypass
- 100 Drive
- 101 Character
- 102 Mix
- 103 Output

Shared DSP receives normalized semantic values only.

The core does not read VST3 parameter queues.

Host layers must apply automation at exact offsets and pass the resulting values to the core.

## Character contract

V2 Character is a discrete hardware-model selection:
- TRI0DE
- PENTODE
- IRON

Do not continuously reinterpret the selected mode as a weighted fourth model.

Click-safe switching may use a short output crossfade or dual-engine transition window, but:
- the steady state must be exactly one physical engine;
- inactive engine state policy must be explicit;
- a crossfade is a transition mechanism, not a model.

## Drive contract

Drive maps digital signal level onto physical model excitation.

Drive is NOT a generic post-model waveshaper coefficient.

Required mapping stages:
1. digital input level -> nominal hardware input level;
2. Drive -> additional physical input gain / operating level;
3. physical circuit output -> normalized digital wet signal;
4. optional calibrated output compensation.

Drive=0 may retain hardware baseline coloration.

The mapping table must be documented in volts/dBu and dBFS before production freeze.

## Mix contract

Mix=0:
- raw dry input path.

Mix=1:
- calibrated physical-model wet path.

The dry path is not forced through nonlinear oversampling filters merely to align implementation convenience.

If wet latency/group delay exists:
- either compensate the dry branch explicitly;
- or choose a zero-latency/low-latency architecture where measured phase error is acceptable;
- document host-reported latency if nonzero.

## Bypass contract

Bypass:
- exact host semantic bypass;
- no intentional coloration.

Automated bypass must be click-safe.

State continues evolving during a bypass transition only if explicitly chosen and tested.

## Physical engines

### TRI0DE
Reference:
- RSD-2 Dempwolf/Zoelzer measured 12AX7 current model as primary reference;
- EHX-1 retained as independent measured-specimen cross-check;
- selected Mullard ECC83 common-cathode circuit.

Production candidate may be:
- direct implicit circuit solve;
- precomputed monotonic surrogate/interpolant;
- reduced analytic approximation.

Acceptance:
must match offline reference over the defined voltage/harmonic/grid-current fixtures.

### PENTODE
Reference:
- Philips 4-Apr-1956 EF86 curves and circuit-1 operating data.

Classic six-parameter Koren form is already rejected as the final model because it cannot match the full large-signal envelope.

Production candidate must preserve:
- separate plate and screen-current behaviour;
- knee;
- supply/screen dependence;
- large-signal saturation envelope.

### IRON
Reference:
- Jensen JT-11P-1 electrical skeleton;
- fitted stateful magnetic model.

Production candidate must preserve:
- low-level insertion loss/impedance;
- frequency-dependent saturation;
- hysteresis/memory;
- THD-vs-level/frequency family.

## V1 equivalence gate before refactor

Before moving V1 code into shared files:

1. create deterministic fixtures for current V1 Channel core;
2. create same fixtures for current V1 Mix FX core;
3. prove their core output is equal within numerical tolerance;
4. copy, do not redesign, the V1 algorithm into a common reference core;
5. compare old per-target implementation vs common reference over fixtures;
6. only then switch callers to shared common code.

No physical V2 model changes are mixed into that refactor commit.

## Test fixture matrix for equivalence

Sample rates:
- 44.1/48/96/192 kHz

Block sizes:
- 1/16/64/127/512/1024 and variable sequences

Signals:
- silence;
- impulse;
- DC-safe step/burst;
- -60/-24/-12/-6/-1 dBFS sine;
- 100 Hz / 1 kHz / 10 kHz;
- deterministic multitone;
- deterministic pseudo-random noise.

Parameters:
- Drive 0/.1/.25/.5/.75/1
- Character exact TRI0DE/PENTODE/IRON points plus historical intermediate positions for V1 equivalence only
- Mix 0/.5/1
- Output default/min/max
- bypass active/inactive

Automation:
- exact sample offset changes;
- multiple points in one block;
- character switch stress.

## Numerical tolerance

During pure refactor:
- 64-bit core: target bit-identical where compiler/operation ordering is preserved;
- otherwise maximum absolute residual must be recorded and justified;
- 32-bit output tolerance derived from float quantization.

No "sounds the same" acceptance for a structural refactor.

## Realtime state

Shared channel state contains only fixed-size POD-like members:
- physical model state;
- antialiasing/oversampling state;
- DC/bypass transition state;
- smoothing state only when per-channel physical necessity requires it.

No vectors, strings, mutexes, file handles or logging objects.

## Denormal policy

V2 common core must explicitly prevent denormal/subnormal CPU stalls.

Preferred order:
1. verify host/processor FTZ/DAZ assumptions are not relied upon;
2. use state sanitization / tiny-value zeroing where needed;
3. measure subnormal stress cost;
4. avoid audible noise injection unless necessary and justified.

## Implementation sequence

1. V1 core-equivalence harness.
2. Common V1 reference extraction.
3. Channel/MixFX shared-core conversion with no intended audio change.
4. State-version/migration layer.
5. TRI0DE physical engine integration behind research/feature gate.
6. PENTODE engine after full curve acceptance.
7. IRON engine after full curve acceptance.
8. Drive calibration.
9. antialiasing strategy.
10. bypass/mix latency/phase solution.
11. full realtime/host QA.
