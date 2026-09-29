# SMX-3 V2 Jiles-Atherton Solver Baseline

Date: 2026-09-30
Tool: tools/smx3_v2_jiles_atherton_reference.py

## Purpose

Establish a deterministic, numerically stable magnetic-state reference before fitting the IRON model to the Jensen JT-11P-1.

This baseline is NOT a Jensen model.

## Source equations

The implementation follows the Jiles-Atherton formulation used by Holters & Zoelzer, DAFx-2016:
- M decomposed into reversible and irreversible contributions;
- anhysteretic magnetization through the Langevin function;
- direction-dependent irreversible magnetization;
- paper's near-zero Taylor handling for the Langevin function and derivative.

For a prescribed H trajectory, equation (14) can be rearranged algebraically into an explicit dM/dH expression. This allows a standalone RK4 reference integration without yet coupling the core to an electrical transformer circuit.

## Example parameters

The test uses the example set printed in the paper's implementation figure:
- a = 14.1 A/m
- alpha = 5e-5
- c = 0.55
- k = 17.8 A/m
- Ms = 2.75e5 A/m

These values originate from the paper's cited example source and are not JT-11P-1 parameters.

## Deterministic major-loop test

Test:
- demagnetized start H=0, M=0;
- sweep H to +250 A/m;
- then to -250 A/m;
- then back to +250 A/m;
- 5000 RK4 steps per segment.

Result:
- maximum |M| ≈ 259728.44 A/m
- descending-branch remanence M at H=0 ≈ 56965.41 A/m
- descending-branch coercive field H at M=0 ≈ -6.9700 A/m
- no NaN/Inf or non-finite state

## Interpretation

The standalone model already demonstrates:
- saturation approaching Ms;
- remanence;
- non-zero coercivity;
- path dependence / hysteresis.

These are necessary properties for IRON and are impossible to obtain from a purely memoryless static waveshaper.

## Next gate

The next IRON reference stage must couple this magnetic state to the electrical circuit through:
- Ampere relation between winding currents and H;
- flux Phi = mu0*A*(H+M);
- Faraday winding voltage v = n*dPhi/dt;
- primary/secondary winding resistances;
- turns ratio;
- source and load impedances.

Only then can we fit the unknown magnetic/core geometry parameters to the Jensen THD-vs-frequency and THD-vs-level measurements.
