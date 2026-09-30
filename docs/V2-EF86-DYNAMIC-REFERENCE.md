# SMX-3 V2 EF86 Dynamic Reference Specification

Date: 2026-09-30
Status: dynamic-reference architecture pinned; implementation pending

## Static foundation

Use:
- Stage-2 joint static plate/screen current model;
- Stage-3 localized low-Va knee correction.

Do not refit those stages during the first dynamic implementation.

## Manufacturer dynamic/capacitive evidence

Philips EF86 typical capacitances:

- grid No.1 to all except anode: Cg1(a) = 3.8 pF
- anode to all except grid No.1: Ca(g1) approximately 5.1-5.3 pF depending edition
- anode to grid No.1: Cag1 <= 0.05 pF
- grid No.1 to heater: Cg1f <= 0.0025 pF

Primary dynamic amplifier network shown by Philips:

- input coupling capacitor = 0.01 uF
- cathode bypass capacitor = 50 uF
- screen-grid bypass capacitor = 0.5 uF
- output coupling capacitor = 0.01 uF
- Ra / Rg2 / Rk / following-stage load according to the selected circuit-1 table.

## Control-grid-current evidence

Independent EF86/6267-family manufacturer data give approximately:

- Vg1 = -1.3 V
- at Ig1 = +0.3 uA

This is a documented onset/reference condition, not a complete current curve.

The first dynamic grid-current law must therefore:
- pass through this anchor;
- remain negligible in the normal -2 V region;
- expose its slope/shape as an explicitly uncertain research parameter;
- be sensitivity-tested before any production choice is frozen.

## Important unknown: input grid-leak/source network

The Philips application drawing labels the input grid-return path, but the currently inspected scan does not provide a sufficiently unambiguous numerical input grid-leak/source resistance for this reference experiment.

Do NOT infer a value from OCR.

Initial dynamic studies must therefore separate:

1. intrinsic tube/network behavior;
2. source impedance;
3. grid-return resistance.

Run sensitivity over a reasonable documented engineering range rather than baking in a guessed resistor.

## Dynamic state variables

Minimum offline MNA/state model:

- control-grid node;
- cathode node;
- screen-grid node;
- plate/anode node;
- output coupling node;
- input coupling capacitor state;
- cathode bypass state;
- screen bypass state;
- output coupling state;
- interelectrode capacitance state;
- control-grid-current contribution.

## First dynamic gates

### DC consistency
Dynamic solver at zero input must converge to the Stage-2 DC operating point.

### Small signal
At 1 kHz and low input:
- gain agrees with Philips circuit-1 table within static/reference tolerance;
- phase/frequency response follows the documented RC/capacitance network;
- no artificial DC drift.

### Large signal
At Vb=250 V:
- Vi->Vo trajectory remains consistent with Graph D;
- 50 Vrms / approximately 5% endpoint remains intact;
- grid-current onset occurs near the documented -1.3 V / 0.3 uA condition;
- cathode/screen bias shift is measured, not guessed.

### Frequency
Measure:
- 20 Hz
- 100 Hz
- 1 kHz
- 10 kHz
- 20 kHz

for low-level and nonlinear input amplitudes.

### Numerical
Require:
- integration-density convergence;
- independent second-method cross-check;
- no NaN/Inf;
- bounded Newton iterations;
- deterministic reset.

## Production rule

Do not derive realtime PENTODE DSP directly from the quasi-static Stage-3 equation.

The production candidate must be reduced from or measured against this dynamic authority once the dynamic gates above pass.
