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
