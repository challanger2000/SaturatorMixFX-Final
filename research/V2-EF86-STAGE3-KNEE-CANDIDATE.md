# SMX-3 V2 EF86 Stage-3 Large-Signal Knee Candidate

Date: 2026-09-30
Status: STRONG PROVISIONAL LARGE-SIGNAL PENTODE CANDIDATE

## Foundation

Stage 2 already provides the static/midband manufacturer surface.

Stage 3 does NOT refit:
- Graph-A screen transfer;
- Graph-B plate surface;
- Ia/Ig2/gm/Ri anchors;
- DC-current sweep;
- small-signal gain sweep.

Instead it adds one localized low-Va structure.

## Low-Va correction

Ia_stage3 = Ia_stage2 *
            [1 + A0*(Vg2/140)^p*exp(-Va/Vk)]

Candidate parameters:

- A0 ≈ 0.55855
- p ≈ 0.53322
- Vk ≈ 11.549 V

Evidence class:
EMPIRICALLY TUNED TO DOCUMENTED LARGE-SIGNAL MANUFACTURER DATA.

Interpretation:
- correction is strongest only near the pentode knee;
- it falls exponentially with plate voltage;
- at the 100-300 V Graph-A/B regions it is negligible;
- screen-voltage dependence allows the knee to move naturally with screen drive.

## High-resolution exact-envelope result

Against the Philips-1956 exact circuit-1 output at 5% THD:

| Vb | model | Philips | error |
|---:|---:|---:|---:|
| 200 V | ~38.58 V | 40 V | -3.56% |
| 250 V | ~50.15 V | 50 V | +0.29% |
| 300 V | ~61.36 V | 64 V | -4.13% |
| 350 V | ~72.30 V | 75 V | -3.61% |
| 400 V | ~83.41 V | 87 V | -4.13% |

This is a major improvement over:
- generalized beta surrogate;
- Stage-2 static model without localized knee correction.

No per-supply gain/output correction is used.

## Philips Graph-D compression trajectory

At 250 V, high-resolution reference results are approximately:

| Vo | model Vi | provisional graph Vi |
|---:|---:|---:|
| 10 V | 89.0 mV | ~91 mV |
| 20 V | 179.4 mV | ~184 mV |
| 30 V | 272.3 mV | ~280 mV |
| 40 V | 370.5 mV | ~378 mV |
| 50 V | 490.8 mV | ~490 mV |

The input/output compression trajectory is therefore extremely close to the current manufacturer-graph read.

## Graph-D distortion trajectory

Approximate model:

- 10 V -> 0.347%
- 20 V -> 0.749%
- 30 V -> 1.256%
- 40 V -> 1.903%
- 50 V -> 4.926%

Current provisional graph read:

- 10 V -> ~0.30%
- 20 V -> ~0.75%
- 30 V -> ~1.45%
- 40 V -> ~2.55%
- 50 V -> ~5.0%

Interpretation:
- 10/20/50 V are strong;
- 30 V is somewhat low;
- 40 V is materially low relative to the present manual read.

Do NOT add another model parameter solely to chase those provisional intermediate graph points until calibrated Graph-D extraction confirms them.

## Grid-current context

Independent EF86/6267 data identify approximately:
- Vg1 ≈ -1.3 V at Ig1 ≈ +0.3 uA.

At the 250 V maximum-output condition, the required input amplitude is naturally near that grid-current-onset region.

This confirms the physical plausibility of the manufacturer endpoint.

A future dynamic reference must add:
- control-grid current;
- input coupling capacitor;
- grid-leak/source impedance;
- cathode/screen bypass dynamics.

The current Stage-3 solver is quasi-static/midband and should not be described as the final dynamic EF86 model.

## Decision

Stage 3 is promoted to a strong provisional PENTODE large-signal candidate.

Remaining gates:
1. calibrated Graph-D extraction;
2. control-grid-current law and dynamic input network;
3. interelectrode capacitances;
4. dynamic numerical convergence;
5. realtime reduction;
6. aliasing and CPU QA.
