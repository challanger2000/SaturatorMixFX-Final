# SMX-3 V2 TRI0DE Multi-Domain Recheck

Date: 2026-09-30
Reference: Mullard ECC83 cathode-bias R-C amplifier
Condition: Vb=250 V, Ra=100 kOhm, Rk=1.5 kOhm, following-grid resistor=330 kOhm

## Correction to earlier baseline

The earlier EHX-1 small-signal comparison used the 100 kOhm plate resistor but did not include the documented 330 kOhm following-stage AC load.

That unloaded calculation produced about 55.69 V/V and appeared to match Mullard's 54.5 V/V extremely closely.

For the amplifier comparison, the 330 kOhm following-stage load must be included.

With that load included, the measured-specimen models give approximately:

| specimen | Ik | loaded gain | output at peak Ig~0.3uA | THD there |
|---|---:|---:|---:|---:|
| RSD-1 | 0.8225 mA | 59.09 | 34.89 Vrms | 5.40 % |
| RSD-2 | 0.8354 mA | 57.51 | 38.63 Vrms | 6.17 % |
| EHX-1 | 0.8248 mA | 50.22 | 32.52 Vrms | 3.42 % |

Mullard anchors:
- Ik ~0.86 mA
- gain ~54.5 V/V
- output ~26 Vrms at the documented onset/grid-current condition
- total distortion ~3.9 %

## Interpretation

EHX-1 remains the strongest of the three published Dempwolf/Zoelzer specimens for the selected SMX-3 reference because:
- idle current remains close;
- its loaded gain brackets the manufacturer value from below while RSD-1/RSD-2 bracket from above;
- its large-signal THD (~3.42%) is much closer to Mullard's ~3.9% than the two RSD specimens.

However EHX-1 is NOT a finished Mullard-reference model:
- loaded gain error is about -7.8%;
- large-signal output at the grid-current condition is about +25% high;
- the real measured EHX specimen is not expected to equal Mullard's average production data exactly.

## Decision

Downgrade EHX-1 status from 'strong cross-source match' to:

BEST PUBLISHED MEASURED-SPECIMEN STARTING POINT.

Next TRI0DE work must fit/derive a reference that jointly respects:
- published 12AX7 current-surface behavior;
- Mullard loaded amplifier gain;
- Mullard current/bias point;
- Mullard output/grid-current condition;
- Mullard large-signal distortion.

Do not hide the remaining differences with an arbitrary output trim.
