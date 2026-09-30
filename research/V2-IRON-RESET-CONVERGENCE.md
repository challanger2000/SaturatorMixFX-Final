# SMX-3 V2 IRON Reset / Periodic-State Convergence Result

Date: 2026-09-30
Workflow run: 36684414139
Conclusion: SUCCESS

## Purpose

Quantify how quickly a canonical demagnetized reset:

H = 0
M = 0

converges to the steady periodic orbit under real AC excitation.

This directly informs host lifecycle and state policy.

## Representative results

Waveform residual is measured against the final settled cycle.

### +4 dBu / 20 Hz
- first cycle residual: ~-18.1 dB
- <= -60 dB: ~10 cycles
- <= -80 dB: ~18 cycles
- ~0.90 s to -80 dB

### +20 dBu / 20 Hz
- first cycle residual: ~-15.2 dB
- <= -60 dB: ~7 cycles
- <= -80 dB: ~9 cycles
- ~0.45 s to -80 dB

### +4 dBu / 100 Hz
- first cycle: ~-29.5 dB
- <= -60 dB: ~23 cycles
- <= -80 dB: ~41 cycles
- ~0.41 s to -80 dB

### +20 dBu / 100 Hz
- first cycle: ~-29.8 dB
- <= -60 dB: ~27 cycles
- <= -80 dB: ~42 cycles
- ~0.42 s to -80 dB

### +20 dBu / 1 kHz
- first cycle: ~-53.2 dB
- <= -60 dB: ~18 cycles
- <= -80 dB: ~44 cycles
- ~44 ms to -80 dB

## Interpretation

A demagnetized reset is deterministic but is NOT equivalent to the settled
periodic state.

At low frequencies the natural magnetic startup trajectory can remain
measurably different for several hundred milliseconds.

This is physically plausible behavior, not numerical instability.

## Host-lifecycle consequence

Do NOT demagnetize IRON on:

- transport stop/start;
- bypass toggle;
- every process enable/disable;
- ordinary block discontinuity;
- editor lifecycle.

Preserve H/M sample-stream state through those events whenever the processor
instance remains valid.

## Fresh-start policy

A canonical H=M=0 state remains appropriate for:

- new processor construction;
- deterministic fresh offline render;
- hard structural reset where preserving old magnetic history is invalid;
- sample-rate reinitialization if state transformation is not proven.

A short output ramp may suppress a discontinuity/click, but it must not be
misrepresented as eliminating the physical magnetic settling trajectory.

## Project-state implication

The result does not automatically force H/M serialization.

Current preferred semantics remain:
- project/preset state stores user parameters;
- realtime magnetic history is session-stream state;
- fresh project load begins from the defined demagnetized state.

However, host tests must explicitly verify:
- state load while stopped;
- state load during playback;
- suspend/resume;
- activate/deactivate;
- offline render repeatability.

If a host routinely destroys/recreates processor state during benign session
operations, a lifecycle-specific preservation strategy may be needed.

## Acceptance rule

IRON production code must include a regression proving:

- transport changes do not reset H/M;
- bypass does not reset H/M;
- ordinary setProcessing toggles preserve H/M unless a documented host contract
  makes that impossible;
- fresh initialization remains deterministic;
- no hidden thread/channel-order dependence exists.
