# SMX-3 V2 IRON High-Frequency Skeleton Constraint

Date: 2026-09-30

## Manufacturer anchors

Jensen JT-11P-1:
- typical relative response at 20 kHz: -0.05 dB
- advertised wide-band -3 dB upper point: approximately 95 kHz

The existing low-frequency skeleton already contains:
- primary DCR
- secondary DCR
- 10 kOhm load
- effective low-level magnetizing inductance

It is essentially flat at high frequency because leakage/capacitive parasitics are not yet modeled.

## Single-shunt-capacitance experiment

A reduced model was tested by adding one effective shunt capacitance to the primary-side load branch.

Fit A:
choose Ceff so 20 kHz / 1 kHz = -0.05 dB.

Result:
- Ceff approximately 665.65 pF
- predicted 95 kHz / 1 kHz approximately -1.01 dB

This misses the documented approximately -3 dB upper bandwidth substantially.

Fit B:
choose Ceff so 95 kHz / 1 kHz = -3 dB.

Result:
- Ceff approximately 1.297 nF
- predicted 20 kHz / 1 kHz approximately -0.187 dB

This misses the documented typical -0.05 dB at 20 kHz.

## Decision

REJECT a single effective shunt capacitance as the final JT-11P-1 high-frequency equivalent.

The transformer requires at least a higher-order parasitic network capable of reproducing both:
- very small in-band 20 kHz loss;
- substantially steeper roll-off by ~95 kHz.

Likely physical contributors:
- leakage inductance;
- distributed winding capacitance;
- primary/secondary-to-shield capacitance;
- interwinding capacitance;
- source/load interaction.

The datasheet directly documents:
- primary-to-shield/case capacitance: 98 pF typical
- secondary-to-shield/case capacitance: 110 pF typical

These values should be used as physical anchors, not replaced by a single arbitrary coloration capacitor.

## V2 requirement

The final linear IRON network must satisfy simultaneously:
- 1 kHz input impedance;
- 1 kHz insertion gain;
- 20 Hz relative response;
- 20 kHz relative response;
- approximately 95 kHz upper -3 dB point;
- acceptable phase-deviation behavior.

Only after this linear network is stable should the nonlinear magnetic core be reinserted for final fitting.
