# SMX-3 V2 IRON Narrow LqS / c / KI / HF Sweep

Date: 2026-09-30
Status: decisive first-order architecture gate

## Goal

Test the simplest remaining hypothesis:

A small change from the corrected 144 H lossless-equivalent magnetic scale,
combined with re-identification of c/KI and the already required winding
parasitics, may satisfy the Jensen evidence without an extra dynamic-loss
state.

## Sweep

L_qs:
- 136 H
- 137 H
- 138 H
- 139 H
- 140 H
- 144 H baseline

For every point:
1. refit c/KI to the +4 and +20 dBu / 20 Hz THD anchors;
2. re-fit leakage-L/effective-C to 20 kHz and ~95 kHz magnitude anchors;
3. combine the JA fundamental with only the incremental HF-parasitic ratio;
4. evaluate with the shared Jensen DLP convention (delay fit >=500 Hz);
5. retain H2/H3 and low-level frequency-law gates.

## First-order acceptance

Must simultaneously satisfy:
- +4 dBu / 20 Hz THD within 0.005 percentage-points of 0.025%;
- +20 dBu / 20 Hz THD within 0.05 percentage-points of 1%;
- H3-dominant default symmetry;
- low-level octave THD ratios within the frozen Whitlock diagnostic range;
- 20 Hz magnitude within +/-0.02 dB of -0.04 dB;
- 20 kHz magnitude within +/-0.02 dB of -0.05 dB;
- 95 kHz magnitude within +/-0.10 dB of -3 dB;
- Jensen DLP worst <=2 degrees;
- positive low-frequency DLP shape and near-zero upper-audio residual.

## Important limitation

The combined transfer is still a low-level fundamental proxy.

Even a pass does not promote production DSP.

A pass selects the smallest architecture worth implementing next:
one unified nonlinear magnetic + HF-parasitic time-domain circuit.

Only that unified circuit may supersede the current 144 H quasi-static
reference after the full IRON regression set passes.
