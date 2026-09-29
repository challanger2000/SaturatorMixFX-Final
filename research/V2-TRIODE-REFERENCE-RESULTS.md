# SMX-3 V2 TRI0DE Reference Baseline Results

Date: 2026-09-30
Tool: tools/smx3_v2_ecc83_reference.py
Reference circuit: Mullard ECC83 R-C coupled A.F. amplifier, Vb=250 V, Ra=100 kOhm, Rk=1.5 kOhm

Manufacturer anchors:
- Ik ~0.86 mA
- |Av| ~54.5 V/V

Published Dempwolf/Zoelzer 12AX7 fitted specimens were inserted into the same cathode-bias circuit without empirical correction.

## Results

| fitted specimen | solved Ik | Ik error vs Mullard | solved cathode V | solved plate V | small-signal Av | gain error vs Mullard |
|---|---:|---:|---:|---:|---:|---:|
| RSD-1 | 0.822535 mA | -4.356 % | 1.233802 V | 167.754571 V | -65.6144 | +20.393 % |
| RSD-2 | 0.835388 mA | -2.862 % | 1.253082 V | 166.465697 V | -63.8346 | +17.128 % |
| EHX-1 | 0.824808 mA | -4.092 % | 1.237213 V | 167.523073 V | -55.6907 | +2.185 % |

## Interpretation

All three fitted physical specimens solve to a cathode current reasonably close to the Mullard average operating point.

However, the two RSD fits predict substantially higher small-signal gain in this specific Mullard circuit.

EHX-1 is the only published specimen of the three that simultaneously:
- remains within about 4.1 % of the Mullard cathode-current anchor;
- remains within about 2.2 % of the Mullard gain anchor;
- requires no output-gain trim or model-coefficient retuning.

Therefore EHX-1 is selected as the first SMX-3 V2 TRI0DE physical reference specimen.

This does not mean:
- every ECC83 behaves exactly like EHX-1;
- Mullard average data and the measured EHX specimen are the same tube;
- production V2 must expose a branded EHX or Mullard clone.

It means EHX-1 provides the strongest currently available cross-source consistency between:
1. a measured practical 12AX7 parameter fit;
2. an independent manufacturer-published ECC83 amplifier operating point.

## Regression gate

The research solver currently gates EHX-1 at:
- absolute cathode-current error <= 8 % versus the Mullard anchor;
- absolute gain error <= 5 % versus the Mullard anchor.

These limits are intentionally wider than the present result. They detect implementation/units/solver regressions while allowing for:
- manufacturer average vs individual specimen differences;
- the simplified low-frequency small-signal load assumptions in the current reference solver.

Tolerances may only be tightened after:
- output load is represented exactly;
- cathode bypass and coupling networks are frozen;
- parasitic capacitances are added;
- the manufacturer table transcription is independently rechecked.

## Next TRI0DE reference tests

1. Static Ia/Ig surface points from Dempwolf/Zoelzer.
2. Positive-grid-current onset.
3. Low-frequency large-signal transfer.
4. Harmonic spectrum versus input amplitude.
5. Dempwolf paper waveform cases: 500 Hz at 2 V / 4 V / 8 V excitation.
6. 4 V sine-burst cases at 500 Hz / 1 kHz / 2 kHz.
7. Add Cak=0.9 pF, Cgk=2.3 pF, Cag=2.4 pF and verify high-frequency behaviour.
8. Only then derive the realtime candidate.
