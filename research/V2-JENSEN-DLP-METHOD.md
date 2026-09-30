# SMX-3 V2 Jensen DLP Measurement Method

Date: 2026-09-30
Status: frozen research measurement convention

## Primary definition

Deane Jensen defines Deviation From Linear Phase (DLP) by separating absolute
phase into:

1. a Frequency Independent Delay component;
2. a Frequency Dependent Delay / phase-error component.

The frequency-independent delay, or its equivalent linear-phase term, is
subtracted from absolute phase.

The remaining phase error is DLP.

Primary references:
- Jensen JT-11P-1 manufacturer data sheet;
- Deane Jensen, "High-Frequency Phase Response Specifications — Useful or
  Misleading?", AES Convention Paper 2398, 1986, revised 1988.

## JT-11P-1 visual behavior

The manufacturer DLP plot:
- is around +0.6 degrees at 20 Hz;
- falls rapidly toward approximately 0 degrees through the low/mid band;
- remains close to 0 degrees through most of the audio band.

This means the constant-delay term must be estimated from the near-linear
mid/high-band phase, not from a whole-band regression that includes the LF
phase curvature we are trying to measure.

## Frozen SMX-3 numerical convention

For offline reference comparisons:

1. unwrap absolute/relative phase;
2. select samples at and above 500 Hz;
3. fit phase radians versus LINEAR frequency Hz:
       phi(f) = a + b*f
4. interpret:
       delay = -b / (2*pi)
5. subtract both:
       a + b*f
   from the full-band unwrapped phase;
6. report the residual in degrees as DLP.

The intercept handles the polarity/reference-phase constant.
The slope handles Frequency Independent Delay.

## Why whole-band log-spaced fitting is rejected

A whole-band log-spaced least-squares fit gives excessive statistical weight to
the low-frequency samples.

But low-frequency curvature is precisely the DLP behavior being measured.

Such a fit partially absorbs the LF error into the "constant delay" estimate
and can create artificial negative residuals elsewhere.

That approach is superseded.

## Manufacturer gates

JT-11P-1:
- condition: 20 Hz..20 kHz, +4 dBu, test circuit 1, Rs=600 Ohm;
- typical DLP: approximately +0.6 degrees;
- maximum: +/-2.0 degrees.

The plotted typical curve is used as shape evidence.
The +/-2 degree value is the hard manufacturer limit.

## Implementation

Shared utility:
tools/smx3_v2_dlp_utils.py

All current IRON phase tools must use that implementation.

Any future change to DLP extraction requires:
- explicit source justification;
- re-running every IRON phase result;
- marking superseded numbers in research documentation.
