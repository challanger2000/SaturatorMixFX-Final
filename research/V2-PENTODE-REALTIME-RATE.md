# SMX-3 V2 PENTODE Practical-Rate Numerical Result

Date: 2026-09-30
Workflow run: 36686011024
Conclusion: SUCCESS

## Measurement scope

Same dynamic EX=1.40 EF86 physical model at:
- 48 kHz
- 96 kHz
- 192 kHz

compared against high-density offline authority.

Coherent test frequencies:
- 1 kHz
- 4 kHz
- 8 kHz
- 12 kHz

High-frequency THD is intentionally excluded from the pure numerical-rate
classification because different sample rates expose different harmonic and
alias paths.

## Results

### 48 kHz
Worst tested:
- gain residual ~269 ppm (0.0269%)
- phase residual ~0.503 deg at 12 kHz
- 1 kHz THD residual ~0.000032 percentage-points

Classification:
WEAK only under the deliberately strict phase tolerance.

Important:
amplitude and nonlinear-transfer integration are already extremely accurate at
1x; the limitation is primarily HF phase discretization of the dynamic network.

### 96 kHz
Worst:
- gain residual ~47 ppm
- phase residual ~0.103 deg
- 1 kHz THD residual ~0.000078 pp

Classification:
PLAUSIBLE.

### 192 kHz
Worst:
- gain residual ~10.8 ppm
- phase residual ~0.0246 deg
- 1 kHz THD residual ~0.000018 pp

Classification:
STRONG.

## Interpretation

The EF86 circuit is substantially less numerically stiff than the ECC83
reference, consistent with:
- extremely small Cag1 (<0.05 pF);
- far less Miller feedback than the triode;
- strongly controlled screen/cathode network.

A fixed 4x internal rate at a 48 kHz host is numerically conservative but not
yet proven necessary.

Current candidate hierarchy:
- 1x: amplitude/nonlinearity strong, HF phase not reference-grade under strict tolerance;
- 2x: plausible;
- 4x: strong.

The final choice must combine:
- alias-energy measurement;
- CPU tails;
- whether a reduced/exactly-discretized linear capacitor network can remove
  the remaining phase error without oversampling.
