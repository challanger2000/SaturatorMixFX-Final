# SMX-3 V2 Structural QA Checkpoint

Date: 2026-09-30
Branch: v2.0.0-development

## Scope

This checkpoint covers only:
- shared V1-reference core integration;
- V2 plugin identity/build targets;
- legacy/V2 state infrastructure;
- current V1-equivalent DSP wiring.

It does NOT approve the future physical TRI0DE/PENTODE/IRON engines.

## Channel

Workflow:
V2 Channel Refactor QA

Corrected run:
36652932568

Result:
SUCCESS

Steinberg validator:
- class category: Audio Module Class
- controller category: Component Controller Class
- Result: 47 tests passed, 0 tests failed

## Mix FX

Workflow:
V2 MixFX Refactor QA

Corrected run:
36652935538

Result:
SUCCESS

Steinberg validator:
- processor factory category: Audio Mix Processor
- controller category: Component Controller Class
- Result: 0 tests passed, 0 tests failed

Interpretation:
The standard Steinberg validator creates no ordinary plugin test suite for the host-specific Audio Mix Processor category. The workflow explicitly verifies the category and treats this expected 0/0 class scan separately from a non-Mix-FX zero-test failure.

Host-specific Mix FX QA remains required later.

## Prior failure root cause

Runs:
- 36650082702 Channel
- 36650082832 Mix FX

Both failed during CMake configure because workflows referenced source directories:
- SMX-3-V2-Channel
- SMX-3-V2-MixFX

The actual source directories remain:
- SMX-3-Channel
- SMX-3-MixFX

while their CMake targets/bundle names are intentionally:
- SMX-3-V2-Channel
- SMX-3-V2-MixFX

Only the workflow source paths/path filters were corrected. No audio-DSP change was made in the fix.

## Other established gates

Previously successful:
- V2 Reference Core Smoke with frozen Windows/MSVC V1 golden hashes
- V2 State Codec QA
- Channel shared-core refactor QA before identity change
- MixFX shared-core refactor QA before identity change

## Status

STRUCTURAL CHECKPOINT PASS for current V1-equivalent V2 skeleton.

This does not mean:
- sonic V2 is complete;
- physical hardware engines are accepted;
- host-specific Mix FX torture QA is complete;
- release QA is complete.

The next sonic work remains blocked by the hardware-reference gates in docs/V2-REFERENCE-GATES.md.
