# SMX-3 V2 EF86 Dynamic Reference — Stage 1

Date: 2026-09-30
Status: first dynamic offline reference candidate

## Primary Philips evidence

From the original EF86 manufacturer sheets:

Selected circuit (1):
- Ra = 100 kOhm
- Rg2 = 390 kOhm
- Rk = 1 kOhm
- screen bypass capacitor = 0.5 uF
- cathode bypass capacitor = 50 uF
- output coupling capacitor = 0.01 uF
- following-stage grid resistor Rg1' = 330 kOhm
- input coupling capacitor shown = 0.01 uF

Internal capacitance data:
- Cg1 = 3.8 pF
- Ca = 5.3 pF
- Cag1 < 0.05 pF

Typical device point:
- Va = 250 V
- Vg2 = 140 V
- Vg1 = -2 V
- Ia = 3.0 mA
- Ig2 = 0.6 mA
- gm = 2 mA/V
- ri = 2.5 MOhm

## Important input-network limitation

The selected Philips circuit drawing labels Rg1 at the input but the operating table does not numerically specify its value.

Therefore the first dynamic solver does NOT invent an input-grid-leak value.

It is driven directly at the g1 node.

Consequences:
- cathode, screen and output dynamics are modeled;
- tube parasitic capacitances are modeled;
- the 0.01 uF input coupling high-pass is not yet part of the authority circuit;
- reported gain is g1-node voltage -> loaded output voltage.

This is preferable to silently inserting a conventional 1 MOhm value and later treating it as manufacturer fact.

## Capacitance interpretation

Philips lists terminal capacitances rather than a complete multi-terminal capacitance matrix.

For the first reduced dynamic authority model:
- Cg1 is represented as g1-to-cathode lumped input capacitance;
- Ca is represented as anode-to-cathode lumped output capacitance;
- Cag1 uses the published upper bound 0.05 pF as anode-to-g1 reverse capacitance.

Evidence classification:
PUBLISHED-PARAMETER DERIVED / REDUCED EQUIVALENT.

This interpretation must be challenged later against measured/manufacturer HF response if available.

## Nonlinear current model

Current strongest candidate:
- EX = 1.40
- exact Ia/gm/Ig2 local anchors retained;
- Stage-2C normalized plate knee retained;
- Philips Graph A/B and exact 5%-THD envelope already used as independent/static constraints.

The dynamic solver does not introduce any new saturation waveshaper.

## Numerical method

First implementation:
- implicit trapezoidal integration;
- Newton solve per step;
- physical-time warmup of 0.4 s before spectral analysis;
- analysis integration density >=96 steps/fundamental period and >=192 kHz.

A second implicit method must cross-check the result before final authority promotion.

## First promotion gate

The dynamic model must:
- remain finite/stable;
- reproduce the Philips small-input 250 V circuit gain of approximately 112 V/V at 1 kHz within provisional tolerance;
- preserve DC operating-point consistency;
- show numerically converged frequency/THD results after physical-time settling.

Not yet production-ready:
- input coupling/grid leak;
- calibrated HF reference;
- dynamic grid current at overload;
- independent integration-method check;
- realtime reduction;
- aliasing/CPU.
