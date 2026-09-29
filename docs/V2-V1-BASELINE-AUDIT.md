# SMX-3 V1 Baseline Audit for V2

Baseline inspected:
- repository: challanger2000/SaturatorMixFX-Final
- stable branch: main
- stable commit: 98e3d7d0fa7eca2b2104b78c7ffc99cf06cf117d
- released/documented version: 0.1.1
- V2 branch: v2.0.0-development

This document records observable V1 behaviour and V2 investigation targets. It is not permission to alter V1.

## Confirmed V1 architecture

Both Channel and Mix FX contain substantially duplicated saturation DSP:
- fixed 4x oversampling;
- eight second-order low-pass sections on interpolation;
- eight second-order low-pass sections on decimation;
- Triode, Pentode and Iron nonlinear functions evaluated in the oversampled core;
- Drive, Character, Mix and Output smoothing;
- DC blocker after the nonlinear path;
- hard bypass selection at the output sample;
- five-double state layout: bypass, drive, character, mix, output.

Parameter IDs:
- 99 Bypass
- 100 Drive
- 101 Character
- 102 Mix
- 103 Output

These IDs are compatibility-sensitive.

## Confirmed neutral-path facts

### Drive = 0

V1 computes:

effectiveDrive = shapeDrive(0) = 0

The nonlinear result is then removed by:
wetSignal = cleanOs + effectiveDrive * (processed - cleanOs)

Therefore Drive = 0 does NOT currently produce tube/iron character. It produces the V1 filtered clean path.

Product decision for V2:
- active Drive = 0 may intentionally produce documented baseline hardware character;
- this must arise from the selected circuit/model, not an arbitrary added coloration.

### Mix = 0

V1 returns dry * cleanOs, not the raw input x.

Therefore Mix = 0 is not a mathematically direct dry path. It includes the V1 interpolation/decimation filter transfer function and group delay.

Product decision for V2:
- Mix = 0 should be true dry unless a documented and measured architecture explicitly justifies otherwise.

## Reproduced V1 oversampling-filter baseline

Tool:
tools/smx3_v1_oversampling_baseline.py

The tool mirrors the V1 filter-design equations and computes the normalized interpolation+decimation steady-state response.

Selected 44.1 kHz results:
- 1 kHz: approximately 0.000000 dB; group delay ~6.375 samples
- 10 kHz: approximately 0.000000 dB; group delay ~7.090 samples
- 15 kHz: approximately -0.000044 dB; group delay ~8.416 samples
- 18 kHz: approximately -0.021535 dB; group delay ~10.337 samples
- 20 kHz: approximately -0.787143 dB; group delay ~13.675 samples

Selected 48 kHz results:
- 1 kHz: approximately 0.000000 dB; group delay ~6.374 samples
- 10 kHz: approximately 0.000000 dB; group delay ~6.963 samples
- 15 kHz: approximately -0.000003 dB; group delay ~7.972 samples
- 18 kHz: approximately -0.001198 dB; group delay ~9.186 samples
- 20 kHz: approximately -0.043673 dB; group delay ~10.755 samples

Interpretation:
- the passband is extremely flat through most of the audible range;
- near Nyquist at 44.1 kHz the clean path becomes materially attenuated and increasingly dispersive;
- active Drive = 0 / Mix = 0 and hard bypass are therefore not the same transfer path.

This is a baseline fact, not yet a judgement that V2 must remove all active-path phase behaviour.

## Bypass investigation

V1 uses a hard per-sample selection:
- bypass -> raw input x
- active -> processed path

Because the active path can have different phase/group delay/state, automated bypass can potentially create discontinuities.

V2 gate:
- measure impulse and steady sine bypass transitions;
- measure click peak/residual over multiple frequencies and levels;
- decide whether a short equal-power/crossfade transition or another host-safe method is required;
- preserve host bypass semantics.

## Mono support

Confirmed:
SMX-3 Channel setBusArrangements currently accepts only stereo -> stereo.

V2 target:
- mono -> mono
- stereo -> stereo
- reject unsupported arrangements intentionally and test them.

Mix FX bus/channel behaviour must remain governed by the verified host-specific contract.

## State versioning

Confirmed:
V1 processor state is five raw doubles with no state-version tag.

V2 requirement:
- continue reading the exact V1 five-double state;
- write a versioned V2 state;
- provide safe defaults for new parameters;
- add migration regression fixtures;
- controller state must mirror migrated processor state correctly.

## GUI / control QA

Confirmed:
- custom Drive control exists;
- Character buttons exist;
- UI zoom control exists;
- Mix and Output are host parameters but are not represented as dedicated custom controls in the current UI description;
- custom Drive mouse handling does not implement Ctrl + left-click default reset.

V2 requirements:
- all user-facing V2 controls visible and synchronized;
- Ctrl + left-click returns every custom continuous control to its actual parameter default;
- version visible in the UI;
- static design first, current 125A branding source of truth before VSTGUI implementation.

## DSP duplication

Confirmed:
Channel and Mix FX contain duplicate copies of the core saturation implementation.

V2 target:
- establish one authoritative shared DSP core;
- perform a regression before and after refactor to prove the refactor itself did not unintentionally change audio;
- keep host-specific Mix FX integration separate from the shared DSP core.

## Character switching / hidden state

V1 continuously blends character weights from the normalized Character value and evaluates Triode, Pentode and Iron in the oversampled core.

Consequences to investigate:
- inactive model states may continue evolving;
- Character automation can behave as a morph between models rather than as a physical mode switch;
- all three nonlinear models incur computation in the core.

V2 hardware-model decision:
- each mode becomes a distinct physical/circuit model;
- switching behaviour must be defined deliberately;
- if click-free crossfading is used, it must not silently become a fourth interpolated hardware model;
- CPU should not be spent on inactive physical engines unless needed for a measured switching strategy.

## Realtime / numerical hardening targets

V1 baseline investigation still required:
- denormal/subnormal behaviour;
- NaN/Inf propagation;
- no callback allocation verification;
- block-size invariance;
- sample-rate invariance;
- 32/64-bit parity;
- offline/realtime parity;
- CPU mean/p95/p99/max;
- Mix FX channel concurrency/order behaviour.

## V2 first implementation order

1. Freeze reproducible V1 baseline measurements.
2. Add state migration tests.
3. Refactor duplicate DSP into one shared core without intentional sonic change.
4. Add mono Channel support and realtime/numerical hardening.
5. Implement hardware reference models individually:
   - Triode
   - Pentode
   - Iron
6. Compare antialiasing strategies per model.
7. Rework Mix/Bypass path after measured transition and latency/phase analysis.
8. Build V2 GUI only after DSP/control semantics are frozen enough to avoid churn.
9. Full 125A release QA and real-audio fixture testing.
