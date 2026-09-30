# SMX-3 V2 IRON Phase Constraint

Date: 2026-09-30
Source: Jensen JT-11P-1 manufacturer datasheet.

## Exact manufacturer constraint

For test circuit 1, Rs=600 Ohm, +4 dBu, 20 Hz to 20 kHz:

Deviation from linear phase (DLP):
- typical: +0.6 degrees
- maximum: +/-2.0 degrees

The page-1 manufacturer graph shows the deviation falling smoothly from roughly +0.6 degrees at 20 Hz toward approximately zero through the upper audio band.

Evidence class:
DOCUMENTED.

## Consequence for reduced HF-network identification

Magnitude constraints alone admitted multiple leakage-L / effective-C pairs.

Therefore the V2 linear transformer skeleton must not select a specific leakage/capacitance pair from magnitude response alone.

Additional discrimination must include:
- DLP across 20 Hz..20 kHz;
- the documented +/-2 degree maximum;
- preferably multiple graph points from the phase plot;
- any further physically documented parasitic information.

## Acceptance rule

A reduced parasitic network is acceptable only if it simultaneously reproduces, within stated tolerance:
- 20 Hz relative magnitude;
- 20 kHz relative magnitude;
- ~95 kHz upper -3 dB point;
- DLP behavior through the audio band.

Until then, leakage inductance and effective capacitance remain ESTIMATED/APPROXIMATED and non-identifiable as individual physical component values.
