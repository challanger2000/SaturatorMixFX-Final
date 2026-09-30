# SMX-3 V2 IRON Harmonic-Physics Constraints

Date: 2026-09-30

Primary engineering source:
Bill Whitlock, "Audio Transformers", Handbook for Sound Engineers, Jensen Transformers publication.

Source:
https://www.jensen-transformers.com/wp-content/uploads/2014/08/Audio-Transformers-Chapter.pdf

## Documented transformer behavior

Whitlock states that transformer distortion is caused by the smooth symmetrical curvature of the magnetic B-H transfer characteristic.

For constant input voltage:
- magnetic flux density is inversely proportional to frequency;
- transformer harmonic distortion is therefore strongly frequency dependent.

For high-quality nickel-core audio transformers, the chapter notes that distortion roughly quarters for every doubling of frequency over the illustrated low-frequency region.

Evidence class:
DOCUMENTED / PHYSICS-DERIVED interpretation.

## Harmonic parity

The same Jensen source states:

Un-magnetized core:
- distortion is nearly pure third harmonic;
- even-order harmonic distortion is virtually absent.

Magnetized core / residual DC magnetization:
- significant even-order harmonics appear;
- H2 can increase dramatically and may approach/exceed H3 in strongly magnetized cases.

This gives SMX-3 an important model constraint that total THD alone cannot provide.

## Consistency with JT-11P-1 exact anchors

JT-11P-1 exact 20 Hz anchors:
- +4 dBu -> ~0.025% THD
- +20 dBu -> ~1% THD

Those imply approximately:

THD proportional to amplitude^2

over the +4 to +20 dBu interval.

For an approximately odd-symmetric constitutive relation:

M(H) ~= chi1*H + chi3*H^3 + ...

a sine excitation produces:
- fundamental proportional to A;
- H3 from the cubic term proportional to A^3;
- H3/fundamental proportional to A^2.

Therefore two independent Jensen evidence paths agree:

1. exact JT-11P-1 level/THD anchors imply ~quadratic normalized distortion growth;
2. Whitlock identifies nearly pure H3 as the normal un-magnetized transformer distortion product.

This strongly constrains the default IRON model around nominal operation.

## Frequency-scaling diagnostic

If low-frequency transformer distortion approximately quarters per octave:

THD(2f) ~= THD(f)/4

then locally:

THD proportional to 1/f^2.

Using the exact JT-11P-1 +4 dBu / 20 Hz anchor as a rough diagnostic:

- 20 Hz: 0.025%
- 40 Hz: ~0.00625%
- 80 Hz: ~0.00156%
- 160 Hz: ~0.00039%

This is NOT substituted for the actual JT-11P-1 graph.

It is a physics-informed diagnostic derived from Jensen's broader transformer engineering text and is useful for rejecting models whose frequency law is structurally wrong.

## Default state requirement

The default SMX-3 IRON state should represent a normally demagnetized line transformer:

- approximately odd-symmetric magnetic response;
- H3-dominant low-level distortion;
- negligible intentional H2;
- no arbitrary asymmetry parameter at default.

This matches the intended studio-line-transformer archetype.

## Remanence / DC-bias behavior

A stateful magnetic model may produce remanence or asymmetric minor loops after asymmetric/DC excitation.

If V2 models this:
- it must arise from the magnetic state equations;
- it must not be simulated by adding an arbitrary even-harmonic waveshaper;
- DC-bias tests must show the expected growth of H2;
- removing the bias and applying a demagnetization procedure must restore the symmetric baseline.

## Determinism and project recall

Physical hysteresis creates history dependence, but a plugin must also recall predictably.

Current engineering target:

On fresh initialization/reset:
- start from a defined demagnetized magnetic state.

During continuous processing:
- preserve physically meaningful magnetic state sample-to-sample.

On project/state restore:
- use a deterministic documented policy.

Candidate policies to test:
A. serialize the magnetic state;
B. reset to the defined demagnetized equilibrium;
C. serialize only when a stable bounded state representation is proven portable.

Do not allow hidden, host-order-dependent magnetic state.

## New IRON acceptance metrics

In addition to total THD, measure:

At zero intentional DC bias:
- H2/H3 ratio;
- H3 absolute level;
- H5/H3 progression;
- symmetry residual f(x)+f(-x) where meaningful;
- THD frequency slope.

With controlled DC/asymmetry:
- H2 growth;
- H2/H3 crossover;
- remanence after bias removal;
- recovery/demagnetization behavior.

A model can match total THD and still be rejected if its harmonic parity is wrong.

## Consequence for current candidates

The previously rejected DAFx example Jiles-Atherton shape already failed the exact +4/+20 dBu THD growth law.

It must also be evaluated against this H3-dominance constraint.

A future fitted Jiles-Atherton / modified-state model should only be promoted if:
- low-level unmagnetized distortion is predominantly odd/H3;
- the exact JT-11P-1 level anchors are met;
- frequency dependence is consistent with Jensen evidence;
- remanence/asymmetry produces plausible even-order growth rather than default coloration.
