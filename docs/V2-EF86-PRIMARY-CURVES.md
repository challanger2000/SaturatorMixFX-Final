# SMX-3 V2 EF86 Primary-Curve Reference

Status: primary manufacturer reference pinned
Device: Philips EF86
Source: Philips EF86 data, 4 April 1956, r-type scan of original Philips sheets.

Primary PDF:
https://www.r-type.org/pdfs/ef86-1.pdf

## Why this source is important

This source contains the original characteristic plots needed to fit and validate PENTODE without treating a third-party SPICE model as ground truth.

The plots below are the authoritative first-fit targets.

## Sheet A — control-grid transfer families

Conditions printed on the sheet:
- Va = 250 V
- Vg3 = 0 V

The plot gives anode current Ia against control-grid voltage Vg1 for multiple screen-grid voltages, including:
- Vg2 = 180 V
- Vg2 = 140 V
- Vg2 = 100 V
- Vg2 = 60 V

Use:
- screen-grid sensitivity;
- control-grid transfer curvature;
- gm variation versus bias;
- cross-check of the 140 V typical-characteristic anchor.

## Sheet B — pentode plate-current family

Conditions printed on the sheet:
- Vg2 = 140 V
- Vg3 = 0 V

The plot gives Ia versus Va for control-grid curves including approximately:
- Vg1 = 0 V
- -0.5 V
- -1.0 V
- -1.5 V
- -2.0 V
- -2.5 V
- -3.0 V
- -3.5 V
- -4.0 V
- -4.5 V

The 1 W anode-dissipation boundary is also shown.

Use:
- pentode knee;
- finite plate slope / output resistance;
- plate-voltage dependence;
- model fitting over multiple Vg1 curves;
- safety/reference range.

This sheet is the primary static curve target for the EF86 current model.

## Sheet C — documented R-C amplifier supply behaviour

The manufacturer explicitly labels two R-C amplifier configurations.

Circuit (1):
- Ra = 0.1 MOhm
- Rg2 = 0.39 MOhm
- Rk = 1 kOhm

Circuit (2):
- Ra = 0.22 MOhm
- Rg2 = 1 MOhm
- Rk = 2.2 kOhm

The plot gives, versus supply voltage Vb:
- cathode current Ik;
- voltage gain g.

SMX-3 V2 selected PENTODE reference is Circuit (1).

Use:
- verify solved DC current against the complete 200-400 V supply curve rather than one single table point;
- verify small-signal gain against the manufacturer curve;
- test whether fitted tube equations generalize when Vb moves away from 250 V.

## Sheet D — level and distortion transfer at Vb = 250 V

The sheet repeats the two circuit definitions and states Vb = 250 V.

Horizontal axis:
- output voltage Vo, 0 to 50 V

Left axis:
- input voltage Vi in mV

Right axis:
- distortion d in percent

Curves are given for both circuit (1) and circuit (2).

Use:
- derive voltage gain as a function of output level;
- validate compression/nonlinear transfer before clipping;
- validate distortion growth versus output amplitude;
- determine whether harmonic growth of the fitted model follows the manufacturer's amplifier behaviour.

Important:
do not manually invent numerical samples from visual inspection. Digitize the curves using a reproducible coordinate calibration step and record:
- source sheet;
- pixel/graph coordinate calibration;
- sampled points;
- estimated reading uncertainty.

## Manufacturer typical device anchor

The Philips sheet gives the typical device point:

- Va = 250 V
- Vg3 = 0 V
- Vg2 = 140 V
- Vg1 = -2 V
- Ia = 3.0 mA
- Ig2 = 0.6 mA
- transconductance S = 2.0 mA/V
- mu(g2/g1) = 38
- internal resistance Ri = 2.5 MOhm

This is a device-characteristic anchor and must not be confused with the self-biased R-C amplifier's final operating point.

## PENTODE fitting order

1. Fit/control Ia(Va, Vg1, Vg2) to Sheets A+B.
2. Fit or derive Ig2 over available manufacturer evidence.
3. Verify the typical 250/140/-2 V device anchor.
4. Insert the model into Circuit (1): Ra=100k, Rg2=390k, Rk=1k.
5. Solve DC self-bias.
6. Compare Ik and gain against Sheet C at multiple Vb values.
7. Simulate static/low-frequency large-signal transfer.
8. Compare Vi/Vo and distortion-growth curves against Sheet D.
9. Only then add parasitic capacitances and realtime discretization.

## Model selection rule

A Koren-style equation family may be used as a candidate parameterization, but no third-party EF86 fit is accepted as ground truth.

The selected model is the one that best satisfies the Philips manufacturer curves under the defined error metrics while remaining numerically stable enough for a realtime implementation or a justified reduced surrogate.


## Exact 1956 circuit-1 table

The original Philips sheet dated 4 April 1956 gives for:
- Ra = 100 kOhm
- next-stage grid resistor = 330 kOhm
- total distortion at maximum output = 5 %

| Vb | Ik | Rg2 | Rk | small-signal Vo/Vi | Vo at 5% |
|---:|---:|---:|---:|---:|---:|
| 400 V | 3.3 mA | 390 kOhm | 1.0 kOhm | 124 | 87 Vrms |
| 350 V | 2.9 mA | 390 kOhm | 1.0 kOhm | 120 | 75 Vrms |
| 300 V | 2.5 mA | 390 kOhm | 1.0 kOhm | 116 | 64 Vrms |
| 250 V | 2.1 mA | 390 kOhm | 1.0 kOhm | 112 | 50 Vrms |
| 200 V | 1.7 mA | 390 kOhm | 1.0 kOhm | 106 | 40 Vrms |

The 100 V row changes Rg2 to 470 kOhm and Rk to 1.5 kOhm and is therefore not part of the same fixed-component sweep.

These 1956 rows are the primary PENTODE amplifier-fit targets because they belong to the same edition as the selected characteristic curves.
