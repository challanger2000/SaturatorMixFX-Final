# SMX-3 V2 Offline Reference Suite

Runner:
`python tools/smx3_v2_reference_suite.py`

Verbose:
`python tools/smx3_v2_reference_suite.py --verbose`

## Purpose

One command checks that the currently accepted research facts still reproduce.

It deliberately separates:

### Positive gates
Models/results that are expected to remain valid:
- ECC83 operating-point cross-source match;
- ECC83 large-signal harmonic/grid-current baseline;
- provisional EF86 table/device fit;
- Jensen linear transformer skeleton;
- standalone Jiles-Atherton hysteresis solver.

### Expected rejection gates
A rejected model must continue to be rejected unless the corresponding decision is intentionally revisited:
- simple six-parameter EF86 model against Philips large-signal envelope.

If that tool suddenly passes because somebody changed the model or tolerance, the suite reports an unexpected pass so the decision log must be reviewed.

### Informational probes
These must execute successfully but do not represent production acceptance:
- V1 oversampling baseline;
- independent third-party EF86 comparison model;
- coupled Iron probe using an intentionally non-Jensen Jiles-Atherton parameter shape.

## What PASS means

REFERENCE SUITE PASS means:
- scripts execute;
- frozen accepted anchors remain in tolerance;
- known rejected model remains rejected where encoded.

It does NOT mean:
- VST3 Validator PASS;
- realtime-safe;
- host QA PASS;
- sonic acceptance;
- V2 release readiness.

Those remain separate gates.
