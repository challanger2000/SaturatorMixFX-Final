# SMX-3 V2 TRI0DE Operating Domain

Date: 2026-09-30
Primary specimen:
Dempwolf/Zoelzer RSD-2 12AX7 in the documented Philips/Mullard ECC83 network.

## Primary-source model domain

Dempwolf/Zoelzer measured practical 12AX7 specimens over approximately:
- Va = 20..300 V
- Vg = -5..+3 V

Positive grid voltage is explicitly measured and modeled.

The documented problematic region is specifically:
- Vg > 0
- combined with Va < approximately 20 V.

Therefore first positive-grid crossing is NOT a model-validity ceiling.

The automated gate tracks:
- minimum Va;
- maximum Vg;
- peak grid current;
- minimum Va specifically while Vg>0;
- whether the combined Vg>0 / Va<20 V condition occurs.

## Measurement method

All domain measurements use physical-time preconditioning before the analysis interval.

This is required because:
- cathode-bias time constants are slow;
- input-coupling/grid-current interaction changes sustained overload bias;
- fixed-cycle startup measurements previously produced misleading boundaries.

## Current RSD-2 settled fixtures

Revision-11 run 36692441356:

| frequency | Vin RMS | min Va | max Vg | peak Ig | invalid Vg>0 & Va<20? |
|---:|---:|---:|---:|---:|---:|
| 20 Hz | 0.70 V | ~118.35 V | ~-0.539 V | ~0.049 uA | no |
| 1 kHz | 0.70 V | ~108.62 V | ~-0.335 V | ~0.143 uA | no |
| 10 kHz | 0.70 V | ~108.59 V | ~-0.334 V | ~0.144 uA | no |
| 20 kHz | 0.70 V | ~108.59 V | ~-0.334 V | ~0.144 uA | no |
| 20 kHz | 1.00 V | ~93.99 V | ~-0.102 V | ~3.44 uA | no |
| 20 kHz | 8.00 V | ~65.34 V | ~+0.451 V | ~200.68 uA | no |

At the extreme 20 kHz / 8 Vrms fixture:
- grid conduction is substantial;
- Vg remains far below the published +3 V measurement ceiling;
- Va while Vg is positive remains about 65 V;
- the known low-Va/positive-grid failure region is not entered.

## Independent overload cross-check

Danyuk AES-137 measurements independently confirm that positive-grid current is real 12AX7 overload behavior.

Around Vgk=+0.3 V, Danyuk reports approximately 200 uA for the tested specimen/circuit.

The current RSD-2 law gives lower current at the same grid voltage, demonstrating meaningful specimen/source variation.

Therefore extreme Drive must be evaluated across multiple grid-current laws before choosing the final archetype.

## Product implication

There is materially more physically defensible TRI0DE Drive headroom than implied by the earlier incorrect rule "Vg>0 is invalid."

Drive 75-100% may use grid conduction as authentic tube behavior, provided:
- the circuit remains inside the measured Vg range;
- the Vg>0 / Va<20 V combination is avoided or separately modeled;
- blocking/recovery remains stable and intentional;
- the chosen grid-current archetype is documented.

## Current status

The RSD-2 reference clears the present measured-domain gate.

The next TRI0DE blocker is not first positive-grid crossing.

It is selecting and validating the extreme grid-current/blocking archetype across measured specimen/source variation.
