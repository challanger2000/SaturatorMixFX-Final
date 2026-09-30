# SMX-3 V2 IRON Joint Low-Field-L / Dynamic-Loss Screen

Date: 2026-09-30
Status: architecture screen

## Why L_qs is now free

The corrected ~144 H value is the inductance required when the magnetic
branch is assumed lossless.

The Jensen loss-aware small-signal target shows that once magnetic loss is
modeled, the corresponding inductive scale can be much larger.

Therefore a unified dynamic model must not force L_qs=144 H while also adding
dynamic loss.

## Screen

Keep current quasi-static JA shape and KI fixed.

Vary:
- L_qs;
- classical loss A_v;
- excess loss B_v.

Compare the +4 dBu magnetic-branch complex admittance directly against the
accepted Jensen loss-aware magnetic target:

Y_target = 1 / (Rmag + j*w*Lmag)

at:
- 20 Hz
- 50 Hz
- 100 Hz
- 200 Hz
- 1 kHz

HF winding parasitics are excluded.

The best magnetic-admittance regions are then checked against:
- +4 dBu / 20 Hz THD;
- +20 dBu / 20 Hz THD;
- H2/H3.

## Interpretation

This tool does not fit production parameters.

It answers only:
"Does freeing the quasi-static inductive scale give the dynamic-loss model the
correct direction of leverage?"

If yes:
- refine only around the best L_qs/A_v/B_v region;
- re-identify c and KI against the exact THD anchors;
- then run the full DLP/magnitude/state suite.

If no:
- do not waste CPU on a full optimizer;
- reformulate the dynamic magnetic model.
