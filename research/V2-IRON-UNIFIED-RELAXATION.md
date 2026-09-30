# SMX-3 V2 IRON Unified JA + One-State Relaxation Candidate

Date: 2026-09-30
Status: offline unification candidate

## Architecture

Keep nonlinear Jiles-Atherton state:
- H
- M

Add exactly one dynamic relaxation-current state:
- i_relax

Equations:

i_mag = H/KI + i_relax

tau * d(i_relax)/dt + i_relax = Grel * v_core

The surrounding circuit solves v_core from:
- source resistance;
- winding DCR;
- reflected load;
- nonlinear JA magnetizing current;
- relaxation current.

## Static/DC behavior

At static equilibrium:
v_core = 0

therefore:
i_relax -> 0.

The added state does not define remanence or coercivity.
Those remain entirely in JA H/M.

## Small-signal authority

Use the already-passed Jensen one-state relaxation fit:
- Lstat ~1309.871 H
- Grel ~2.73375 uS
- tau ~1.44024 ms

HF leakage/capacitance remains a separate electrical network.

## Nonlinear fit policy

Freeze:
- a
- alpha
- k
- Ms
- Grel
- tau
- Lstat

Re-fit only:
- c
- KI

to the exact Jensen:
- +4 dBu / 20 Hz ~0.025% THD
- +20 dBu / 20 Hz ~1% THD

KPHI is derived from Lstat, KI and zero-field JA slope.

## Promotion gates after THD fit

1. H3-dominant unbiased state
2. Jensen small-signal magnitude/DLP
3. DC-bias/remanence regression
4. independent numerical method
5. host-rate reduction
6. aliasing
7. HF parasitic integration

No production C++ until these pass.
