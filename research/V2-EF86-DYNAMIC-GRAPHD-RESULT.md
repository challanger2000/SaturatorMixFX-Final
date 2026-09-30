# SMX-3 V2 EF86 Dynamic Graph-D Result

Date: 2026-09-30
Workflow run: 36683858678
Conclusion: SUCCESS as probe; dynamic network does NOT explain the remaining Graph-D THD residual

## Test

Current EX=1.40 EF86 candidate embedded in the documented Philips dynamic network:

- Ra=100 kOhm
- Rg2=390 kOhm
- Rk=1 kOhm
- screen bypass=0.5 uF
- cathode bypass=50 uF
- output coupling=0.01 uF
- following load=330 kOhm
- reduced Philips terminal-capacitance model

Five provisional Philips Graph-D input levels were applied directly at g1 at 1 kHz.

## Result

| Graph-D Vi | dynamic Vo | graph Vo | dynamic THD | graph THD |
|---:|---:|---:|---:|---:|
| 91 mV | 10.322 V | ~10 V | 0.628% | ~0.30% |
| 184 mV | 20.703 V | ~20 V | 1.220% | ~0.75% |
| 280 mV | 31.018 V | ~30 V | 1.758% | ~1.45% |
| 378 mV | 40.803 V | ~40 V | 2.423% | ~2.55% |
| 490 mV | 50.618 V | ~50 V | 3.974% | ~5.00% |

Worst output-amplitude error:
- ~3.52%

THD residual:
- about +0.47 percentage-points at the low/mid region;
- about -1.03 percentage-points at the highest point.

## Comparison with quasi-static Graph-D probe

Quasi-static EX=1.40 already showed:
- strong Vi->Vo agreement;
- too much low-level distortion;
- too little distortion near the top.

Adding the real cathode/screen/output dynamics does NOT remove that pattern.

Therefore the remaining distortion-shape problem is NOT primarily:
- cathode bypass dynamics;
- screen bypass dynamics;
- output coupling/load memory.

## Diagnosis

The next model refinement must target CONTROL-GRID TRANSFER CURVATURE while preserving:

- exact Ia anchor;
- exact gm anchor;
- exact Ig2 anchor;
- Graph A/B surfaces;
- exact Vo@5% multi-supply envelope;
- the now-validated dynamic network.

The most conservative next degree of freedom is the existing equation-family
softness/sharpness parameter KP.

Do NOT add:
- post distortion suppression;
- level-dependent output trims;
- arbitrary dynamic compression;
- extra waveshapers.

## Important uncertainty

The Graph-D points are still provisional manual digitization and the plotted sheet does not explicitly state the test frequency.

Therefore Graph D remains a strong SHAPE constraint, not yet an exact hard numeric gate.

The model should only be changed if one candidate improves Graph D while preserving the stronger exact manufacturer anchors.
