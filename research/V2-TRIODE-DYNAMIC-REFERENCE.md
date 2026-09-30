# SMX-3 V2 Dynamic TRI0DE Reference

Date: 2026-09-30
Tool: tools/smx3_v2_ecc83_dynamic_reference.py
Status: offline dynamic reference candidate

## Circuit

Tube:
- Dempwolf/Zoelzer measured EHX-1 12AX7 specimen.

Manufacturer surrounding network:
- Vb=250 V
- Ra=100 kOhm
- Rk=1.5 kOhm
- grid leak=1 MOhm
- following-stage load=330 kOhm
- input coupling=0.01 uF
- cathode bypass=50 uF
- output coupling=0.01 uF

Published 12AX7 parasitics:
- Cak=0.9 pF
- Cgk=2.3 pF
- Cag=2.4 pF

## Numerical method

The pF parasitics make the nodal ODE stiff enough that naive explicit RK4 at ordinary audio rates is not a trustworthy reference solver.

The offline tool therefore uses:
- constant capacitance MNA matrix;
- implicit trapezoidal integration;
- Newton solve at every step;
- numerical Jacobian;
- 192 kHz default reference step rate.

This is intentionally a correctness/reference implementation, not a realtime architecture.

## DC result

Approximately:
- plate node ~167.523 V
- cathode ~1.23721 V

matching the existing EHX-1 DC reference.

## Small-signal dynamic behavior

At 1 kHz / 10 mVrms:
- gain is approximately 50.5 V/V,
which is consistent with the previously corrected loaded static EHX-1 gain (~50.2 V/V).

The 0.01 uF input/output coupling network causes the expected LF attenuation; therefore the dynamic circuit should not be compared to the static AC-loaded model at very low frequency as if they were the same topology.

The Miller/parasitic network is now explicit rather than approximated by a post-EQ.

## 1 kHz nonlinear progression

Representative dynamic results at 192 kHz reference integration:

| Vin RMS | Vout RMS | THD |
|---:|---:|---:|
| 0.10 V | ~4.94 V | ~0.435 % |
| 0.30 V | ~14.77 V | ~1.343 % |
| 0.50 V | ~24.46 V | ~2.41 % |
| 0.70 V | ~33.79 V | ~3.87 % |
| 1.00 V | ~44.20 V | ~10.24 % |

At low/moderate excitation the dynamic model closely follows the static EHX-1 harmonic baseline.

At stronger excitation the real input coupling/grid-current interaction changes the trajectory materially. This is expected physical behavior and demonstrates why the final TRI0DE cannot be reduced to a fixed memoryless transfer curve without measured error.

## Important next checks

Before promoting this solver to the final offline authority:
1. integration convergence vs 384/768 kHz reference step rate;
2. waveform residual vs step rate;
3. grid-voltage/grid-current trajectories;
4. 500 Hz / 1 kHz / 2 kHz burst behavior;
5. compare implicit trapezoid with a second integration method;
6. establish valid Drive mapping that avoids relying excessively on Dempwolf's known positive-grid/very-low-Va model limitations.

No realtime production kernel is selected yet.


## Integration-rate convergence correction

A follow-up convergence check showed two different numerical regimes:

At 1 kHz:
- 192 kHz, 384 kHz and 768 kHz integration rates produce essentially the same large-signal result.
- Example at Vin=1.0 Vrms: output changes by only a few millivolts and THD by only a few thousandths of a percentage point.

At 20 kHz:
- 192 kHz is too coarse for an offline authority; trapezoidal discretization still shifts the measured magnitude/phase.
- Increasing the integration density materially changes the result toward convergence.

Therefore the reference tool no longer uses a fixed 192 kHz rate for every test.

Current rule:
- fs_reference = max(192 kHz, 96 * fundamental frequency)

Examples:
- 1 kHz -> 192 kHz
- 10 kHz -> 960 kHz
- 20 kHz -> 1.92 MHz

This keeps the numerical reference error below the level at which it could be mistaken for tube/Miller response.

The production plugin is NOT expected to run at these rates. This is purely an offline ground-truth calculation used to judge reduced realtime implementations.
