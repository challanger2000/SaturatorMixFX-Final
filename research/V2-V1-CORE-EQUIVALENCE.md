# SMX-3 V2 V1 Core Equivalence Proof

Date: 2026-09-30
Baseline branch: v2.0.0-development derived from V1 main @ 98e3d7d0fa7eca2b2104b78c7ffc99cf06cf117d

Compared files:
- SMX-3-Channel/source/processor.cpp
- SMX-3-MixFX/source/processor.cpp

## Machine comparison results

### Oversampling design/filter section
Range:
- designOversamplingFilters
- runOversamplingFilter

Result:
TEXT IDENTICAL

Compared section length:
1299 bytes/characters in both extracted source ranges.

### Core nonlinear DSP section
Range:
- shapeTriode
- shapePentode
- shapeIron
- processNonlinear
- dcBlock
- processCoreSample

Result:
TEXT IDENTICAL

Compared section length:
approximately 5.8 k source characters in both targets.

### Reset/smoothing
Functions:
- resetDsp
- updateSmoothers

Result:
TEXT IDENTICAL

### setupProcessing / lifecycle
Result:
NOT text-identical as a whole, for an expected host-integration reason.

Common DSP coefficient setup is the same.

Mix FX additionally calls resetMixFxStates() when:
- setActive(true) while Mix FX host mode is engaged;
- processing transitions from stopped to active while Mix FX host mode is engaged.

This is host-state lifecycle handling, not a DSP-algorithm difference.

## Conclusion

The current V1 Channel and Mix FX products already share the same DSP algorithm by duplication.

Therefore V2 may extract the core to one common implementation without reconciling conflicting sound algorithms.

The refactor acceptance criterion remains:
- old Channel vs shared-core Channel;
- old MixFX core vs shared-core MixFX;
- deterministic fixture residuals.

The source-text identity result is evidence that a common-core refactor is appropriate, but it does NOT replace compiled numerical regression after the refactor.

## Refactor boundary

Move/shared:
- DSP state types;
- oversampling coefficients/state;
- filter design;
- V1 nonlinear functions during equivalence phase;
- DC block;
- processCoreSample;
- later physical TRI0DE/PENTODE/IRON engines.

Keep target-specific:
- VST3 AudioEffect lifecycle;
- parameter queues and ParamIDs;
- bus negotiation;
- state stream plumbing;
- Mix FX proprietary interfaces;
- Mix FX 128-channel host state ownership;
- factory/controller/editor integration.

## Required next gate

Before deleting duplicated DSP from either target:
1. add shared core as a new source without changing callers;
2. compile both targets;
3. add deterministic comparison harness;
4. switch one target at a time;
5. compare output;
6. only then remove duplicated implementation.

No V2 physical-model change is permitted in the same refactor step.
