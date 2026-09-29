# SMX-3 V2 JT-11P-1 Linear Skeleton

Date: 2026-09-30
Tool: tools/smx3_v2_jensen_linear_reference.py

## Manufacturer anchors used

Jensen JT-11P-1:
- turns ratio: approximately 1:1
- primary DCR: 1.45 kOhm
- secondary DCR: 1.55 kOhm
- test-circuit load: 10 kOhm
- typical input impedance at 1 kHz/+4 dBu: 13.0 kOhm
- typical voltage gain at 1 kHz/+4 dBu: -2.3 dB
- typical 20 Hz relative response at +4 dBu / Rs=600 Ohm: -0.04 dB

## Circuit-derived 1 kHz behaviour

Ignoring the magnetizing branch at 1 kHz:

total reflected series resistance for the 1:1 transformer is approximately

1.45 kOhm + 1.55 kOhm + 10 kOhm = 13.0 kOhm

which directly reproduces the manufacturer's typical 1 kHz input impedance.

The corresponding resistive voltage ratio to the 10 kOhm load is

10k / (1.45k + 1.55k + 10k) = 0.76923

or approximately -2.28 dB, essentially the documented -2.3 dB typical voltage gain.

This is classified CIRCUIT DERIVED from DOCUMENTED component/test values.

## Effective magnetizing inductance

A first-order low-level model was then formed with a primary shunt magnetizing inductance Lm.

Lm was solved numerically such that:

|H(20 Hz)| / |H(1 kHz)| = -0.04 dB.

Result:

- effective Lm ≈ 106.554 H

Selected calculated values:

| frequency | gain | relative to 1 kHz | |Zin| |
|---:|---:|---:|---:|
| 20 Hz | -2.31888 dB | -0.04000 dB | ~9.889 kOhm |
| 1 kHz | -2.27888 dB | 0 dB | ~12.998 kOhm |
| 20 kHz* | -2.27887 dB | ~+0.00002 dB | ~13.000 kOhm |

*The manufacturer documents about -0.05 dB at 20 kHz. The present skeleton intentionally has no parasitic-capacitance/leakage network yet, so it is NOT expected to reproduce the HF roll-off.

## Interpretation

This is useful because the main low-level 1 kHz behavior does not require empirical coloration:
- DCR and load explain the insertion loss;
- DCR plus reflected load explain the input impedance;
- a physically interpretable effective magnetizing inductance explains the small 20 Hz droop.

The nonlinear Jiles-Atherton model should therefore be fitted around this skeleton instead of being used to fake linear insertion loss.

## Next IRON electrical steps

1. Add leakage inductance / parasitic capacitance only as needed to fit the 20 kHz and 95 kHz manufacturer response.
2. Replace the linear magnetizing branch with the stateful magnetic model while preserving the low-level effective inductance.
3. Fit magnetic parameters against 20/30/50 Hz THD-vs-level and +4/+14/+20 dBu THD-vs-frequency curves.
4. Verify that nonlinear fitting does not destroy the already-correct low-level input impedance and insertion loss.


## Flux-linkage anchors for nonlinear fitting

For a sinusoidal winding voltage,

v(t) = d(lambda)/dt, with lambda = N*Phi,

so the peak flux linkage is

lambda_peak = Vwinding_rms * sqrt(2) / (2*pi*f).

Using the derived low-level 20 Hz skeleton to estimate the primary magnetic-branch voltage:

| input level | input Vrms | magnetic-branch Vrms @20 Hz | lambda_peak = N*Phi_peak |
|---:|---:|---:|---:|
| +4 dBu | 1.22829 V | 1.08627 V | 0.0122249 Wb-turn |
| +14 dBu | 3.88420 V | 3.43510 V | 0.0386585 Wb-turn |
| +20 dBu | 7.75000 V | 6.85393 V | 0.0771338 Wb-turn |

These values are CIRCUIT DERIVED from:
- the documented Jensen test level;
- documented winding DCR/load;
- the derived effective low-level Lm.

Why this matters:
the first nonlinear magnetic fit can operate in terms of flux linkage lambda=N*Phi without inventing N and core area A separately.

Only if a later solver requires absolute B and H must geometry/turns be resolved or fitted with an explicit identifiability note.

The +20 dBu / 20 Hz point corresponds to the manufacturer typical 1 % THD threshold and therefore gives a particularly useful high-flux nonlinear anchor.
