# SMX-3 V2 Extended EF86 Model-Family Benchmark

Date: 2026-09-30
Status: MODEL-FAMILY EVIDENCE ONLY — community parameter set rejected as hardware reference

## Source

A 2022 diyAudio post publishes an EF86 model generated from Philips plate-curve imagery with a more flexible pentode equation family than classic six-parameter Koren.

The posted model adds independent:
- knee shape;
- low-plate-voltage transition;
- plate slope;
- kink correction;
- screen-current coupling;
- positive grid-current terms.

This is useful as evidence about model form, not as primary hardware authority.

Source:
https://www.diyaudio.com/community/threads/vacuum-tube-spice-models.243950/page-163

Primary SMX-3 authority remains Philips manufacturer data.

## Independent benchmark results

Using the published community-fitted parameter set in an independently expressed calculation:

Device point Va=250 V, Vg2=140 V, Vg1=-2 V:
- Ia ~3.068 mA versus Philips ~3.0 mA
- Ig2 ~0.848 mA versus Philips ~0.6 mA

The screen current is therefore materially high.

### Philips circuit-1 supply sweep

| Vb | Ik error | gain error | Vo @5% error |
|---:|---:|---:|---:|
| 200 V | -20.17 % | -2.78 % | +17.26 % |
| 250 V | -18.67 % | -1.20 % | +13.90 % |
| 300 V | -17.42 % | +0.59 % | +4.32 % |
| 350 V | -16.35 % | +1.43 % | +1.89 % |
| 400 V | -15.42 % | +1.65 % | -1.21 % |

## Interpretation

This is a very useful result.

The posted PARAMETERS are not suitable for SMX-3:
- self-biased cathode current is systematically ~15-20% low;
- screen current at the standard device anchor is far too high.

But the MODEL FAMILY shows substantially better structural behavior than the classic compact Koren candidates:
- small-signal gain stays within roughly 3%;
- large-signal output envelope becomes increasingly accurate through the upper supply range;
- the model includes explicit degrees of freedom for knee, slope and kink behavior that our simple candidates lacked.

Therefore the correct conclusion is NOT 'use this community model'.

The correct conclusion is:

REFIT THE EXTENDED EQUATION FAMILY INDEPENDENTLY AGAINST PHILIPS PRIMARY DATA.

## Licensing / provenance rule

No community implementation is promoted into production.

The research benchmark:
- records the public model-family source;
- independently expresses the equations for measurement;
- treats posted fitted values as comparison data only.

Production parameters and production implementation must be derived independently from Philips primary curves/tables and documented 125A fitting objectives.

## Next fitting objective

Refit an extended model simultaneously against:
- Philips Ia(Va,Vg1) family at Vg2=140 V;
- Vg2 transfer family;
- Ia/Ig2/gm device anchor;
- circuit-1 Ik over 200-400 V;
- circuit-1 small-signal gain over 200-400 V;
- circuit-1 Vo at 5% THD over 200-400 V;
- calibrated graph-D intermediate distortion trajectory.

This benchmark strongly suggests that additional physically interpretable knee/slope degrees of freedom are justified.
