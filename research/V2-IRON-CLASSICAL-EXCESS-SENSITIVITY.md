# SMX-3 V2 IRON Classical + Excess Dynamic-Loss Screen

Date: 2026-09-30
Status: architecture screen

## Literature basis

Dynamic loss separation augments the quasi-static hysteresis field with two
rate-dependent terms:

- classical eddy-current field proportional to dB/dt;
- excess/anomalous field proportional to sign(dB/dt)*sqrt(abs(dB/dt)).

The associated instantaneous power terms scale with:
- (dB/dt)^2;
- abs(dB/dt)^(3/2).

These terms vanish at DC and therefore do not replace the quasi-static
remanence/hysteresis law.

Primary:
D. C. Jiles, IEEE Transactions on Magnetics 30(6), 1994,
DOI 10.1109/20.334076.

## Reduced SMX-3 implementation

Core voltage is proportional to dB/dt in the reduced transformer state.

The screening field is therefore:

H_total = H_qs
        + A_v * v_core
        + B_v * sign(v_core)*sqrt(abs(v_core))

The scalar circuit equation remains monotonic for non-negative A_v/B_v and
can be solved analytically each derivative evaluation.

## Gates observed during the sweep

- +4 dBu / 20 Hz THD;
- +20 dBu / 20 Hz THD;
- H2/H3 parity;
- 20 Hz relative response;
- 20 kHz relative response;
- DLP through 20 Hz..20 kHz.

## Promotion rule

No A_v/B_v pair is accepted simply because phase improves.

A candidate must eventually be re-fitted jointly with the quasi-static
effective scaling and then pass:
- exact Jensen THD anchors;
- low-level frequency-law diagnostic;
- DLP;
- magnitude;
- DC-bias/remanence;
- numerical cross-method convergence;
- realtime reduction.

This screen only determines whether the classical+excess architecture has
sufficient independent leverage to solve the missing dynamic behavior.
