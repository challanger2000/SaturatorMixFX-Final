# SMX-3 V2 EF86 Graph-D Refined Provisional Digitization

Date: 2026-09-30

Primary source:
Philips EF86 Graph D, Vb=250 V, circuits (1) and (2).

Circuit (1):
- Ra=0.1 MOhm
- Rg2=0.39 MOhm
- Rk=1 kOhm
- Rg'=0.33 MOhm

The graph was directly inspected at high resolution.

## Why this supersedes the first provisional read

The first manual read was intentionally rough and slightly under-read the distortion trajectory in the 10-40 V output region.

The refined read uses:
- the original graph directly;
- explicit shared-axis calibration;
- larger uncertainty where curve thickness/crossing makes exact reading ambiguous.

The exact manufacturer table endpoint:
- Vo = 50 Vrms
- total distortion = 5%

remains higher authority than the graph raster and is therefore fixed exactly in the refined dataset.

## Refined circuit-(1) shape points

| Vo | Vi | distortion |
|---:|---:|---:|
| 10 V | ~98 mV | ~0.45% |
| 20 V | ~195 mV | ~0.95% |
| 30 V | ~292 mV | ~1.70% |
| 40 V | ~390 mV | ~2.70% |
| 50 V | ~485 mV | 5.00% exact table endpoint |

Machine-readable file:
research/ef86_philips1956_graphD_refined_provisional.csv

## Evidence classification

- Vi values: MANUAL_GRAPH_DIGITIZATION_REFINED
- distortion at 10-40 V: MANUAL_GRAPH_DIGITIZATION_REFINED
- distortion at 50 V: exact DOCUMENTED manufacturer-table endpoint

## Use

Use for:
- compression trajectory;
- large-signal distortion shape;
- staged kink-model fitting.

Do not:
- treat intermediate graph points as exact table values;
- force a model inside sub-pixel residuals;
- sacrifice exact DC/gain/Vo@5% anchors to chase the scan.
