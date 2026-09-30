# SMX-3 V2 TRI0DE Grid-Current Cross-Check

Date: 2026-09-30
Status: INFORMATIONAL source/specimen comparison

## Sources

Dempwolf & Zoelzer, DAFx-2011:
three individually fitted practical 12AX7 specimens:
- RSD-1
- RSD-2
- EHX-1

Dimitri Danyuk, AES Convention 137, Paper 9124:
measured 12AX7 grid current under overload and two convenient fit forms for the practical transition/positive-grid region.

## Why this matters

The TRI0DE plate-current reference and the grid-current/blocking behavior are related but not identical identification problems.

Dempwolf's own specimen fits already show substantial spread.

An independent Danyuk measurement adds further evidence that:
- positive-grid current is real and important;
- specimen/circuit variation is material;
- one grid-current parameter set should not be marketed as a universal ECC83/12AX7 truth.

## Representative +0.3 V grid-current values

Approximate:

- Dempwolf RSD-1: ~130 uA
- Dempwolf RSD-2: ~117 uA
- Dempwolf EHX-1: ~82 uA
- Danyuk polynomial fit: ~177 uA
- Danyuk exponential fit: ~221 uA

Danyuk also reports approximately 200 uA around +0.3 V for the measured stage/specimen.

## Interpretation

EHX-1 is the weakest positive-grid-current specimen of the currently compared Dempwolf sets.

That does NOT invalidate EHX-1 as a plate-current/dynamic reference.

It means:
- extreme-grid-current behavior should be evaluated independently;
- blocking/recovery must not be tuned solely from the EHX-1 current magnitude;
- RSD/Danyuk provide a realistic higher-grid-current comparison range.

## Product implication

Before freezing Drive 75-100%:

1. run the documented Mullard network with multiple measured grid-current laws;
2. compare:
   - peak Vg;
   - grid-current charge per cycle;
   - cathode-bias shift;
   - coupling-capacitor shift;
   - recovery time;
   - THD/harmonic weighting;
3. determine whether the user-facing TRI0DE mode should represent:
   - the EHX-1 specimen specifically;
   - a manufacturer-average/archetype;
   - or a bounded consensus fit.

Do not silently splice a stronger grid-current law into the EHX-1 model without documenting the hybrid evidence basis.
