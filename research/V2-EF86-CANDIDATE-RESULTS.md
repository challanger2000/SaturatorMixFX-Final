# SMX-3 V2 EF86 Candidate Baseline Results

Date: 2026-09-30

Candidate:
Circuit Codex CC0 EF86 Koren-form model.

Purpose:
independent comparison baseline only. The Philips manufacturer data remains the hardware authority.

## Device anchor

The candidate was fitted to a later Philips/Mullard device anchor:
- Va=250 V
- Vg2=140 V
- Vg1=-2.2 V
- Ia=3.0 mA
- Ig2=0.6 mA

Reproduction:
- Ia ≈ 3.000010 mA
- Ig2 ≈ 0.600001 mA

As expected, it reproduces that single fitted anchor essentially exactly.

## Primary amplifier validation: Philips 4-Apr-1956 sheet

Primary V2 circuit:
- Ra=100 kOhm
- Rg2=390 kOhm
- Rk=1 kOhm
- following-grid resistor=330 kOhm

For AC gain comparison, cathode and screen are treated as bypassed and the documented following-stage 330 kOhm resistor is included in the plate AC load.

| Vb | Philips-1956 Ik | candidate Ik | Ik error | Philips-1956 gain | candidate gain | gain error |
|---:|---:|---:|---:|---:|---:|---:|
| 400 V | 3.300 mA | 3.4421 mA | +4.31 % | 124 | 99.60 | -19.68 % |
| 350 V | 2.900 mA | 2.9260 mA | +0.90 % | 120 | 97.27 | -18.94 % |
| 300 V | 2.500 mA | 2.4244 mA | -3.02 % | 116 | 93.71 | -19.22 % |
| 250 V | 2.100 mA | 1.9393 mA | -7.65 % | 112 | 88.69 | -20.81 % |
| 200 V | 1.700 mA | 1.4732 mA | -13.34 % | 106 | 81.86 | -22.77 % |

## Later manufacturer edition cross-check

Later Philips handbook data differ from the 1956 sheet. For example, at 250 V the later table is approximately:
- Ik=2.0 mA
- gain=123
- Vo=50 Vrms
- total distortion=5 %

This is kept as a secondary manufacturer-family/spread reference, not merged numerically with the 1956 primary fit.

## Decision

The candidate is useful because:
- it is independently fitted;
- it is cleanly licensed CC0;
- it reproduces its published single device anchor;
- its DC-current trend through the real Philips amplifier remains informative.

It is NOT accepted as the SMX-3 PENTODE reference because:
- it misses the 1956 manufacturer small-signal amplifier gain by roughly 19-23 % over the fixed-component 200-400 V sweep;
- its DC current increasingly diverges at lower supply voltage;
- it was not fitted to the published EF86 plate-curve family;
- its KVB value is a generic project default rather than a parameter derived from EF86 plate-voltage data.

## Consequence for SMX-3

The production/reference pentode model must be fitted against multiple Philips curves and amplifier operating points simultaneously.

Required fit objective must include at least:
- Ia(Va,Vg1) family at Vg2=140 V;
- transfer families versus Vg2;
- device anchor current and transconductance;
- screen current;
- 1956 circuit-1 Ik versus Vb;
- 1956 circuit-1 gain versus Vb;
- later Philips handbook values as an out-of-fit cross-check.

A model that matches one point but fails these cross-checks is rejected even if it sounds subjectively convincing.
