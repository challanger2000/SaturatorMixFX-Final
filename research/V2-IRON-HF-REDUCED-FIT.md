# SMX-3 V2 IRON Reduced HF Network Experiment

Date: 2026-09-30
Status: research fit architecture

## Problem

A single effective shunt capacitance cannot simultaneously reproduce:
- JT-11P-1 ~-0.05 dB at 20 kHz;
- approximately -3 dB upper point near 95 kHz.

## New reduced topology

Keep documented/derived values:
- source resistance for the cited test: 600 Ohm;
- primary DCR: 1.45 kOhm;
- secondary DCR: 1.55 kOhm;
- load: 10 kOhm;
- effective low-level magnetizing inductance: ~106.554 H;
- primary-to-shield capacitance: 98 pF;
- secondary-to-shield capacitance: 110 pF.

Add only two fit degrees of freedom:
1. series leakage inductance Llk;
2. an effective extra secondary-side/interwinding shunt capacitance Cx.

Important:
Cx is an EFFECTIVE reduced-network parameter.
It is not claimed to equal the transformer's physical interwinding capacitance.

## Identification targets

Magnitude only:
- 20 kHz / 1 kHz = -0.05 dB typical;
- 95 kHz / 1 kHz = approximately -3 dB.

## Promotion rule

Even if both magnitude anchors are matched, the topology is not promoted until it also passes:
- Jensen DLP / phase-deviation behavior;
- parameter sensitivity / identifiability;
- no implausible resonance in the extended frequency response;
- consistency when the nonlinear magnetic branch is reinserted.

Magnitude matching is necessary but not sufficient.


## Corrected 144 H fit result

After correcting the LF magnetizing-inductance derivation for Jensen test
circuit 1 with Rs=600 Ohm, the reduced HF fit was rerun.

Targeted GitHub run:
- run 36697771830
- conclusion: success

Current reduced-network result:
- Lm = ~143.999 H
- Llk = ~2.75665 mH
- documented Cp = 98 pF
- documented Cs = 110 pF
- effective fitted Cx = ~1.15504 nF

Magnitude response relative to 1 kHz:
- 20 Hz: ~-0.03989 dB
- 20 kHz: ~-0.04925 dB
- 50 kHz: ~-0.49387 dB
- 95 kHz: ~-3.00081 dB
- 150 kHz: ~-8.13 dB

This is substantially more internally consistent than the old 106.55 H
derivation because the same source condition now reproduces the LF anchor.

## Promotion status

Magnitude topology:
STRONG PROVISIONAL.

Parameter interpretation:
- Llk remains an effective referred leakage inductance unless direct Jensen
  leakage data become available;
- Cx remains an effective reduced-network capacitance and must not be described
  as the physical interwinding capacitance.

Still blocking promotion:
- DLP / phase-deviation reproduction;
- identifiability / sensitivity of Llk vs Cx;
- reinsertion into the full nonlinear magnetic state model;
- no unintended resonant peak under all intended source/load conditions.

Do not compare source-to-load absolute gain with Jensen's separate
transformer-port -2.3 dB voltage-gain figure. The response test includes
Rs=600 Ohm; the 1 kHz transformer-port figure is a different measurement
quantity.
