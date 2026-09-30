# SMX-3 V2 EF86 Graph-A Provisional Screen-Family Digitization

Date: 2026-09-30

Primary source:
Philips EF86 manufacturer PDF, Graph A.
The plot states:
- Va = 250 V
- Vg3 = 0 V
- Ia versus Vg1
- Vg2 families 60 / 100 / 140 / 180 V.

The original graph was directly inspected from the PDF.

## Purpose

These provisional points are NOT production fit authority.

They are used to test whether an EF86 model family has the correct screen-voltage dependence before allowing additional free parameters.

This directly addresses the identifiability problem found in the unrestricted extended-family fit.

## Evidence policy

The Vg2=140 V, Vg1=-2 V, Ia=3.0 mA point is independently documented in the manufacturer tabular device characteristics and is therefore marked DOCUMENTED_DEVICE_ANCHOR.

All other points are MANUAL_GRAPH_DIGITIZATION with deliberately broad uncertainties.

Machine-readable file:
research/ef86_philips_graphA_provisional.csv

## Model-selection use

A model family is structurally suspect if it requires:
- per-Vg2 gain trims;
- supply-specific correction;
- or large residual trends across the 60/100/140/180 V families.

A model is not promoted merely for passing this provisional dataset. Final fitting still requires calibrated graph coordinates.
