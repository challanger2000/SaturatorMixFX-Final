# SMX-3 V2 IRON Classical-Loss Fair Small-Signal Test

Date: 2026-09-30

The 144 H value is only the lossless-equivalent magnetizing inductance.
Therefore a fair test of the classical dynamic-loss term must allow the
underlying low-field inductance to change when loss is introduced.

For the implemented classical field term, the small-signal magnetic branch is:

Ymag = Gmag + 1/(s Lmag)

This experiment jointly fits:
- Lmag;
- Gmag;
- leakage inductance;
- effective extra HF capacitance

against Jensen:
- 1 kHz gain;
- 1 kHz input impedance;
- 20 Hz response;
- 20 kHz response;
- ~95 kHz bandwidth;
- Jensen-conformant DLP.

This isolates the architecture itself from the previous artificial constraint
of fixing L=144 H.

If the freely fitted G||L architecture still cannot satisfy all domains, the
classical instantaneous loss term is structurally insufficient and a
relaxation/viscosity state becomes justified.
