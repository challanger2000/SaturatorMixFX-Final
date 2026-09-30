# SMX-3 V2 EF86 Extended-Family Identifiability Check

Date: 2026-09-30
Status: extended model family remains promising; unrestricted static refit is UNDER-IDENTIFIED

## Question

Can the more flexible EF86 knee/screen model be independently fitted from the current static Philips constraints alone?

Current static objective included:
- device Ia at Va=250 V, Vg2=140 V, Vg1=-2 V;
- device Ig2;
- gm;
- circuit-1 cathode-current sweep, Vb=200..400 V;
- circuit-1 small-signal-gain sweep, Vb=200..400 V;
- current provisional Philips Ia(Va,Vg1) plate-curve samples.

The community parameter set was NOT used as a target.

Kink terms were disabled during this identifiability experiment so the question concerns the core knee/screen family rather than copying a third-party fit.

## Result

The objective can be reduced to a very small normalized residual:
- normalized RMS roughly 0.49-0.51 sigma;
- worst current-data residual roughly 1.4 sigma.

However, when parameter bounds are widened, several parameters continue moving to very large/boundary values while the residual improves only slightly.

Representative behavior:
- KG2 moves from ~20k toward ~57k and remains weakly bounded;
- KVB moves from ~1200 toward ~1590 and remains weakly bounded;
- KVC moves to the upper fit bound;
- KLAMG collapses effectively to zero;
- other knee parameters compensate.

## Interpretation

This is NOT evidence that those large values are the physical EF86 parameters.

It is evidence that the present static objective does not independently identify all degrees of freedom of the extended model family.

A low residual alone is therefore insufficient.

## Why the ambiguity exists

The current data constrain combinations of:
- plate-current scale;
- screen-current scale;
- knee shape;
- effective plate slope;
- control-grid/screen sensitivity.

Multiple parameter combinations can produce nearly the same:
- idle point;
- local gm;
- loaded small-signal gain;
- coarse high-plate-voltage current surface.

The missing discriminators are precisely the data that the Philips sheets also provide:
- screen-voltage transfer families;
- dense low-Va knee points;
- complete large-signal Vi/Vo/distortion trajectory;
- large-signal envelope across supply voltage.

## Decision

DO NOT freeze an extended-family parameter set from the current static fit.

The model family remains accepted for research because its structure is capable of reproducing the missing large-signal behavior.

But production/reference parameters must be identified in stages with explicit regularization and independent constraints.

## Revised fitting sequence

### Stage 1 — device/current surface
Fit only the minimum subset needed for:
- Ia(Va,Vg1) at Vg2=140 V;
- Ia(Vg1) across multiple Vg2 values;
- Ia/Ig2/gm device anchor.

Freeze or tightly regularize parameters that are strongly identified here.

### Stage 2 — amplifier DC/small signal
Add:
- circuit-1 Ik(Vb);
- gain(Vb).

Reject any Stage-1 solution that cannot generalize here without supply-dependent correction.

### Stage 3 — large signal
Use remaining knee/kink degrees of freedom against:
- exact Vo@5% THD for Vb=200..400 V;
- Philips Graph-D Vi->Vo;
- Philips Graph-D distortion->Vo.

Then re-run Stages 1 and 2.

### Stage 4 — screen/dynamic network
Only after static/large-signal acceptance:
- screen bypass/capacitance;
- interelectrode capacitances;
- realtime discretization;
- aliasing and CPU.

## Optimization rule

Do not accept:
- parameters pinned to arbitrary search bounds;
- highly correlated parameters with no independent evidence;
- a lower numerical cost obtained by physically uninterpretable cancellation.

If two parameter sets are experimentally indistinguishable within source uncertainty, prefer:
- the simpler parameterization;
- stronger physical constraints;
- better numerical conditioning.
