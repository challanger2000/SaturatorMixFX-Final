# SMX-3 V2 Dynamic TRI0DE Reference

Date: 2026-09-30
Tool: tools/smx3_v2_ecc83_dynamic_reference.py
Status: strong offline dynamic reference candidate
Primary measured specimen: Dempwolf/Zoelzer RSD-2 12AX7

## Circuit

Tube device law:
- Dempwolf/Zoelzer measured RSD-2 12AX7 specimen.

Documented Philips/Mullard surrounding network:
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

RSD-2 current parameters:
- G=2.173e-3
- mu=100.2
- gamma=1.28
- C=3.19
- Gg=5.911e-4
- xi=1.358
- Cg=11.76
- Ig0=4.527e-8 A

Evidence:
PUBLISHED-PARAMETER DERIVED / MEASURED-SPECIMEN MODEL embedded in a DOCUMENTED manufacturer circuit network.

## Why RSD-2 is primary

Manufacturer-loaded static comparison at Vb=250 V / Ra=100 kOhm / Rk=1.5 kOhm / Rg'=330 kOhm:

- RSD-2 idle current error: about -2.86%
- RSD-2 loaded gain error: about +5.52%
- RSD-2 distortion error at 26 Vrms: about -0.20 percentage-points relative to Mullard's 3.9%

RSD-2 currently gives the strongest combined agreement across those manufacturer-loaded criteria.

This is not a claim that RSD-2 is a universal ECC83.

EHX-1 and RSD-1 remain independent specimen cross-checks.

## Numerical method

The pF parasitics make the nodal system stiff enough that ordinary-rate explicit integration is not used as the offline authority.

The reference uses:
- constant capacitance MNA matrix;
- implicit trapezoidal integration;
- Newton solve at every step;
- numerical Jacobian;
- physical-time preconditioning;
- frequency-adaptive high-density analysis.

Reference integration rule:
- at least 192 kHz;
- at least 96 integration steps per fundamental period.

## Settled dynamic results

Revision-11 QA run 36692441356 produced:

### 1 kHz / 10 mVrms

At increasing integration density:
- 192 kHz: gain 56.39860, THD 0.0746939%
- 384 kHz: gain 56.40236, THD 0.0746684%
- 768 kHz: gain 56.40330, THD 0.0746621%

Top-two residual:
- gain ~16.66 ppm
- phase ~0.000060 degree
- THD ~0.000006 percentage-points

### 1 kHz / 0.70 Vrms

- 192 kHz: gain 54.02718, THD 6.60311%
- 384 kHz: gain 54.03042, THD 6.60377%
- 768 kHz: gain 54.03123, THD 6.60393%

Top-two residual:
- gain ~15.00 ppm
- phase ~0.000063 degree
- THD ~0.000163 percentage-points

### 10 kHz / 10 mVrms

At 3.84 MHz:
- gain ~56.46204
- THD ~0.0746760%

### 20 kHz / 10 mVrms

At 7.68 MHz:
- gain ~56.45870
- THD ~0.0747087%

The settled low-level THD is therefore essentially frequency-stable through the tested band rather than showing the false HF rise seen before the settling-time correction.

## Independent numerical-method agreement

Implicit trapezoid vs implicit midpoint at the high reference rates:

- 1 kHz / 10 mVrms: gain residual ~8.50 ppm; THD residual ~0.0000010 pp
- 1 kHz / 0.70 Vrms: gain residual ~8.81 ppm; THD residual ~0.000166 pp
- 10 kHz / 10 mVrms: gain residual ~33.96 ppm
- 20 kHz / 10 mVrms: gain residual ~33.61 ppm

This independently validates the aggregate offline numerical solution.

## Current physical-domain result

The Dempwolf measurement/model domain includes approximately:
- Va=20..300 V
- Vg=-5..+3 V

Positive-grid operation is therefore valid model territory by itself.

The known limitation is specifically positive Vg combined with Va below about 20 V.

The current RSD-2 dynamic circuit is monitored for that combined condition.

## Remaining TRI0DE blockers

1. grid-current specimen/archetype decision for extreme Drive;
2. blocking/recovery comparison across RSD-1/RSD-2/EHX-1/Danyuk evidence;
3. final multi-level/frequency fixture set;
4. realtime reduction;
5. aliasing and CPU comparison;
6. final Drive calibration.

No production realtime kernel is selected yet.
