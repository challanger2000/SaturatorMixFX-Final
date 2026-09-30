# SMX-3 V2 IRON Magnetic-State Policy

Status: proposed engineering policy; validate with host lifecycle before production freeze
Date: 2026-09-30

## State classes must be separated

IRON has two fundamentally different kinds of state.

### User/project state
Examples:
- Character selection;
- Drive;
- Mix;
- Output;
- future user-exposed Iron calibration controls, if any.

These belong in the versioned VST3 project state.

### Realtime physical history
Examples:
- Jiles-Atherton H / M state;
- integration history;
- antialiasing / oversampling filter memory;
- transition/crossfade history.

These are sample-stream state.

They must not automatically be serialized merely because the physical model contains memory.

## Proposed default policy

On normal continuous processing:
- preserve magnetic state sample-to-sample;
- transport stop does not arbitrarily demagnetize the model unless host lifecycle requires a reset.

On processor reset / new activation / fresh offline render:
- initialize to one defined demagnetized state;
- result is deterministic.

On project-state restore:
- restore user parameters;
- initialize realtime magnetic state by the same documented deterministic rule;
- do not embed arbitrary instantaneous H/M in the preset blob by default.

## Why not serialize instantaneous H/M by default

Saving H/M at an arbitrary host callback time would make project-state bytes depend on:
- the exact preceding waveform;
- sample position at save time;
- host save timing;
- possibly channel processing order.

That creates poor preset semantics and can make state comparisons/non-audio project edits non-deterministic.

Most importantly, H/M is not a user parameter.

## Audible reset transient

A real demagnetized transformer can exhibit a history-dependent startup trajectory when AC excitation begins.

Therefore resetting H/M to zero is deterministic but not necessarily immediately equal to the long-run periodic orbit.

This is not automatically a bug.

Required measurements before policy freeze:
- first-cycle H2/H3 after reset;
- time/cycles to periodic-state convergence versus frequency/level;
- discontinuity if host resets while non-silent audio is present;
- realtime vs offline deterministic equality;
- repeated activate/deactivate;
- project state restore at silence and under nonzero input.

## Alternative if reset transient is excessive

Do NOT silently serialize arbitrary H/M as the first workaround.

Evaluate in order:
1. canonical demagnetized reset and natural physical startup;
2. a deterministic zero-input equilibration if mathematically justified;
3. controlled click-safe output transition around host reset;
4. serialization of bounded magnetic state only if host/preset semantics and cross-platform reproducibility are proven.

## Acceptance requirement

Regardless of chosen policy:
- identical initial state + identical audio + identical automation must produce identical output;
- offline render must be repeatable;
- no unbounded remanence drift;
- no hidden dependence on thread/channel order;
- project-state versioning must remain independent of internal solver representation where possible.


## Measured startup-convergence update

Measured canonical H=M=0 startup shows that periodic-state convergence is not instantaneous.

Worst tested:
- first-cycle waveform residual ~-15 dB;
- low-frequency convergence to <-80 dB may require ~0.4-0.9 s;
- at 1 kHz the same criterion is reached in ~44 ms.

Therefore the lifecycle policy is strengthened:

### Preserve magnetic state through
- transport stop/start;
- bypass;
- editor open/close;
- ordinary processing pauses where the same processor instance continues.

### Demagnetize only on
- fresh processor creation;
- deterministic fresh offline start;
- hard structural reset / incompatible sample-rate reinitialization.

Do not reset H/M merely because a host calls setProcessing(false).

If a host destroys the processor object, deterministic reconstruction from H=M=0 is expected.

Any click-safe wet ramp is a transition aid only; it must not repeatedly erase physical history.
