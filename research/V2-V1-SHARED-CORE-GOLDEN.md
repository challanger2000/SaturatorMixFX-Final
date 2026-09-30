# SMX-3 V2 V1 Shared-Core Golden Baseline

Date: 2026-09-30
Environment:
- GitHub Actions windows-2022
- Microsoft Visual C++ C++17 /O2
- standalone host-independent V1 reference core

Workflow:
.github/workflows/v2-reference-core-smoke.yml

Tool:
tools/smx3_v1_core_smoke.cpp

## First usable run

Run:
36649049175

Result:
SUCCESS

Checks:
- common V1 core compiled with MSVC;
- 28 sample-rate / Drive / Character / Mix / Output combinations produced finite output;
- duplicate reset states produced bit-identical sample sequences;
- result artifact uploaded.

## Frozen golden hashes

The resulting MSVC FNV-1a hashes over 8192 double-precision output samples are now embedded in the smoke test.

Sample rates:
- 44.1 kHz
- 48 kHz
- 96 kHz
- 192 kHz

Seven parameter cases per rate cover:
- Drive=0;
- default Drive/triode;
- mid Drive/Pentode;
- high Drive/Iron;
- maximum Drive with parallel Mix;
- Mix=0 clean-path behavior;
- Output maximum.

A subsequent push run after embedding the hashes must reproduce the exact values.

## Meaning

These golden hashes are a structural-refactor gate only.

They freeze V1 behavior so:
- shared-core extraction cannot silently change the old algorithm;
- Channel and MixFX caller conversion can be tested against one known Windows implementation.

They are NOT desired V2 sonic targets.

Once the physical V2 engines replace V1:
- new reference fixtures supersede these hashes for the physical models;
- this legacy golden set remains available to verify V1 migration/refactor history.

## Portability note

Exact libm floating-point hashes are compiler/build-environment specific.

Therefore:
- exact hashes are required in the pinned Windows/MSVC workflow;
- other compilers should use numerical residual tolerances rather than assuming identical transcendental-function bit patterns.
