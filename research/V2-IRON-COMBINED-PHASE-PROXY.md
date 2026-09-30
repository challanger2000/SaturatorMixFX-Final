# SMX-3 V2 IRON Combined JA + HF-Parasitic Phase Proxy

Date: 2026-09-30
Status: diagnostic bridge before full nonlinear/parasitic MNA integration

## Purpose

After standardizing all DLP measurements on the shared >=500 Hz delay-fit
convention, the corrected 144 H JA candidate is much closer to the Jensen
phase limit than older mixed-method reports suggested.

Before adding more magnetic states, test whether the already-identified
winding HF parasitics are sufficient to move the full low-level fundamental
inside the Jensen DLP limit.

## Proxy construction

At +4 dBu the JA candidate is only ~0.025% THD.

Use:
H_proxy = H_JA_fundamental * (H_HF_full / H_linear_144H_base)

The ratio isolates the incremental effect of:
- leakage inductance;
- documented shield capacitances;
- fitted effective HF capacitance.

The base 144 H magnetizing branch is divided out so it is not counted twice.

## Interpretation

A proxy pass does not promote production DSP.

It means the next implementation should prioritize a unified nonlinear
magnetic + HF-parasitic circuit before adding extra dynamic-loss mechanisms.

A proxy failure means the magnetic low-field model still needs additional
frequency-dependent structure after parasitics are included.
