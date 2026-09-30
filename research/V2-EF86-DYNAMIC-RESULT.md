# SMX-3 V2 EF86 Dynamic Reference Result

Date: 2026-09-30
Workflow run: 36683511775
Conclusion: SUCCESS

## Circuit / model

Current EX=1.40 EF86 current candidate embedded in:
- Philips Ra=100 kOhm;
- Philips Rg2=390 kOhm;
- Philips Rk=1 kOhm;
- 0.5 uF screen bypass;
- 50 uF cathode bypass;
- 0.01 uF output coupling capacitor;
- 330 kOhm following-stage load;
- reduced Philips terminal capacitance model.

Input is driven directly at g1 because the selected Philips operating table does not numerically specify the input Rg1 value.

## DC result

Approximate:
- plate node: 84.03 V
- screen node: 114.57 V
- cathode: 2.007 V

These are consistent with the selected self-biased circuit and the existing static candidate.

## Low-level dynamic matrix

At 10 mVrms g1 drive:

| frequency | gain | phase | THD |
|---:|---:|---:|---:|
| 20 Hz | ~47.15 | -96.37 deg | ~0.0642% |
| 100 Hz | ~105.86 | -154.51 deg | ~0.0702% |
| 1 kHz | ~113.71 | -177.49 deg | ~0.0699% |
| 10 kHz | ~113.77 | +178.87 deg | ~0.0700% |
| 20 kHz | ~113.67 | +177.35 deg | ~0.0702% |

## Manufacturer midband check

Philips circuit-1 table:
- small-input gain ~112 V/V at Vb=250 V.

Dynamic model at 1 kHz:
- ~113.71 V/V
- error ~+1.53%

PASS under the current provisional +/-5% dynamic-reference tolerance.

## Interpretation

The first dynamic EF86 reference is numerically stable and preserves the static/manufacturer midband behavior.

The 20 Hz loss is expected from the real coupling/bypass network and is not a model defect.

The HF result is also plausible:
- Cag1 is extremely small (<0.05 pF);
- pentode Miller feedback is therefore far smaller than in a triode;
- gain remains nearly flat through 20 kHz.

## Next question

The important unresolved PENTODE issue is Graph-D distortion shape.

Quasi-static EX=1.40:
- reproduces Vi->Vo strongly;
- is too nonlinear at ~10-20 V output;
- approaches the manufacturer distortion trajectory at higher output.

The next probe drives the dynamic reference with the same provisional Graph-D input levels to determine whether:
- cathode bias movement;
- screen dynamics;
- coupling/load state

naturally reduce or reshape the low-/mid-level harmonic error.

No static model parameter should be changed before that test is evaluated.
