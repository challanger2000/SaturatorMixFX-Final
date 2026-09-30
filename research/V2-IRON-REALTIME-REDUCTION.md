# SMX-3 V2 IRON Realtime Integration Reduction Result

Date: 2026-09-30
Workflow run: 36683720882
Conclusion: SUCCESS

## Question

Does the Jiles-Atherton magnetic state itself require heavy oversampling / RK4
to remain faithful to the offline authority?

Compared:
- reference: RK4 at 192 kHz;
- candidate: explicit midpoint / RK2 at 48, 96 and 192 kHz.

Cases:
- +4 and +20 dBu;
- 20, 50, 100 Hz;
- +20 dBu at 1 kHz.

## Result

Worst residuals versus RK4@192 kHz:

### Midpoint @48 kHz
- THD residual: ~0.00000507 percentage-points
- H3 residual: ~0.00001382 percentage-points

### Midpoint @96 kHz
- THD residual: ~0.00000301 percentage-points
- H3 residual: ~0.00000915 percentage-points

### Midpoint @192 kHz
- THD residual: ~0.00000272 percentage-points
- H3 residual: ~0.00000642 percentage-points

All tested rates classify as STRONG under the frozen research limits.

## Interpretation

The magnetic-state ODE is slow enough that, over the tested audio-transformer
operating domain, a second-order midpoint integrator at 48 kHz already tracks
the high-rate RK4 authority extremely closely.

Therefore:

**state-integration accuracy does not justify fixed 4x oversampling.**

This is an important architectural result.

## What this does NOT prove

It does NOT prove that the final IRON audio path can always run at 1x.

Aliasing is a separate problem.

A nonlinear magnetic output may still generate harmonics above Nyquist, and
those may fold into the audio band even if H/M state integration itself is
numerically accurate.

Therefore the next IRON architecture test separates:

1. magnetic state integration rate;
2. nonlinear output evaluation rate;
3. anti-aliasing / oversampling strategy.

## Current preferred architecture hypothesis

Evaluate first:

- H/M midpoint integration at host rate;
- targeted 2x nonlinear evaluation/output path if alias measurements require it;
- 4x only if measured alias improvement justifies CPU cost.

Do NOT retain V1-style blanket 4x oversampling merely by precedent.

## Realtime production gate still required

Before production freeze:
- alias-energy matrix versus 1x/2x/4x;
- sample-rate matrix 44.1/48/96/192 kHz;
- transient/state residual;
- CPU mean/p95/p99/max;
- denormal/subnormal stress;
- deterministic reset/state lifecycle.

Numerical integration itself is no longer a blocker for a low-cost realtime
IRON engine.
