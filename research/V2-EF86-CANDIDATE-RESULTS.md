# SMX-3 V2 EF86 Candidate Baseline Results

Date: 2026-09-30

Candidate:
Circuit Codex CC0 EF86 Koren-form model.

Purpose:
independent comparison baseline only. The Philips manufacturer data remains the hardware authority.

## Device anchor

The candidate was fitted to:
- Va=250 V
- Vg2=140 V
- Vg1=-2.2 V
- Ia=3.0 mA
- Ig2=0.6 mA

Reproduction:
- Ia ≈ 3.000010 mA
- Ig2 ≈ 0.600001 mA

As expected, it reproduces the single anchor essentially exactly.

## Philips circuit-1 supply sweep

Circuit:
- Ra=100 kOhm
- Rg2=390 kOhm
- Rk=1 kOhm
- following-grid resistor=330 kOhm

For AC gain comparison, cathode and screen are treated as bypassed and the following-stage 330 kOhm resistor is included in the plate AC load.

| Vb | Philips Ik | candidate Ik | Ik error | Philips gain | candidate gain | gain error |
|---:|---:|---:|---:|---:|---:|---:|
| 400 V | 3.200 mA | 3.4421 mA | +7.57 % | 140 | 99.60 | -28.86 % |
| 350 V | 2.750 mA | 2.9260 mA | +6.40 % | 134 | 97.27 | -27.41 % |
| 300 V | 2.400 mA | 2.4244 mA | +1.02 % | 129 | 93.71 | -27.36 % |
| 250 V | 2.000 mA | 1.9393 mA | -3.03 % | 123 | 88.69 | -27.89 % |
| 200 V | 1.550 mA | 1.4732 mA | -4.96 % | 117 | 81.86 | -30.03 % |
| 150 V | 1.050 mA | 1.0296 mA | -1.94 % | 110 | 72.58 | -34.02 % |

## Decision

The candidate is useful because:
- it is independently fitted;
- it is cleanly licensed CC0;
- it reproduces the published single device anchor;
- its DC-current trend through the real Philips amplifier is reasonably close.

It is NOT accepted as the SMX-3 PENTODE reference because:
- it misses the manufacturer small-signal amplifier gain by roughly 27-34 % over the full supply sweep;
- it was not fitted to the published EF86 plate-curve family;
- its KVB value is a project default rather than a parameter derived from EF86 plate-voltage measurements.

## Consequence for SMX-3

The production/reference pentode model must be fitted against multiple Philips curves and amplifier operating points simultaneously.

Required fit objective must include at least:
- Ia(Va,Vg1) family at Vg2=140 V;
- transfer families versus Vg2;
- device anchor current and transconductance;
- screen current;
- circuit-1 Ik versus Vb;
- circuit-1 gain versus Vb.

A model that matches one point but fails these cross-checks is rejected even if it sounds subjectively convincing.
