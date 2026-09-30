# SMX-3 V2 EF86 Stage-2B Coupled-Knee Result

Date: 2026-09-30
Workflow run: 36662675073
Conclusion: SUCCESS as experiment; NOT accepted as final Stage-2 parameterization

## Result

Stage-1 current surface frozen.

Added:
- KNEE
- KNEE2
- KG2
- KVC

with a coupled plate/screen knee.

Best objective:
- NRMS ~1.025 sigma

Graph B:
- NRMS ~0.423 sigma
- worst ~1.068 sigma

Amplifier:
- max Ik error ~3.74%
- max gain error ~6.71%

Device:
- Ig2 ~0.542 mA vs 0.600 mA
- inferred ri ~1.59 MOhm vs Philips typical ~2.5 MOhm

## Identifiability failure

Best parameters hit arbitrary bounds:

- KNEE = 5 -> exact lower bound
- KG2 = 20000 -> exact upper bound
- KNEE2 close to its lower region

This means the numerical improvement does not uniquely identify the physical/effective parameters.

## Structural information gained

The fit materially improves Graph-B low/intermediate plate-voltage behavior.

Therefore:
- adding a plate-knee factor is justified;
- the separate KG2/KVC screen parameterization is unnecessarily degenerate for the present data.

## Reparameterization

The extended screen expression contains the combination:

Ig2 ~ E2/KG2 * (KVC - Kplate)

This can be rewritten as:

Ig2 ~ E2 * (S0 - S1*Kplate)

where:
- S0 = KVC/KG2
- S1 = 1/KG2

S0 and S1 are directly identifiable combinations.

Likewise, KNEE2 running toward very small values indicates tanh(Va/KNEE2) is effectively unity throughout the measured operating region.

Stage 2C therefore tests the minimal identifiable form:

- one arctangent plate knee K(Va)=atan(Va/KNEE), normalized at 250 V;
- Ig2 = E2 * max(S0 - S1*K(Va), 0).

If S1 collapses to zero, the evidence says the current manufacturer dataset does not require explicit plate-voltage redistribution in screen current; the plate knee itself is the missing mechanism.
