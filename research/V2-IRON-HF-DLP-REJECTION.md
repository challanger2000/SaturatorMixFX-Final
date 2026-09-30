# SMX-3 V2 IRON Reduced HF Network — Phase Rejection

Date: 2026-09-30
Status: REJECTED AS FINAL HF NETWORK

## Candidate under test

Reduced topology:
- documented Rp/Rs/load;
- derived Lm;
- documented 98 pF primary-to-shield capacitance;
- documented 110 pF secondary-to-shield capacitance;
- fitted leakage inductance ~2.756 mH;
- fitted effective extra shunt/interwinding capacitance ~1.155 nF.

Magnitude fit:
- 20 kHz / 1 kHz: ~-0.04935 dB
- 95 kHz / 1 kHz: ~-3.0008 dB

Therefore magnitude anchors alone look essentially perfect.

## Independent phase test

Jensen JT-11P-1 specifies deviation from linear phase over 20 Hz..20 kHz:
- typical: +0.6 degrees
- maximum: +/-2.0 degrees.

The reduced network phase was unwrapped and the best least-squares linear
phase phi(f)=a+b*f was removed.

Residual:
- minimum roughly -1.2 degrees;
- maximum roughly +5.9 degrees;
- worst absolute residual roughly 5.9 degrees.

## Decision

REJECT the two-parameter Llk + effective-C network as the final JT-11P-1 HF equivalent.

This is a valuable rejection:
- it proves two magnitude anchors are insufficient;
- the network can fake the amplitude curve while producing the wrong phase law;
- Jensen DLP successfully discriminates otherwise plausible reduced models.

## Next HF topology requirement

The next reduced physical network needs more realistic distributed behavior,
likely involving at least:
- leakage inductance distribution rather than one lump;
- primary/secondary winding capacitance placement;
- interwinding coupling capacitance;
- source/load interaction.

Documented 98 pF / 110 pF shield capacitances remain fixed physical anchors.

Any additional capacitance remains an effective reduced-network quantity
unless directly documented.

Promotion still requires simultaneous:
- 20 Hz magnitude;
- 20 kHz magnitude;
- ~95 kHz -3 dB point;
- Jensen DLP inside +/-2 degrees;
- no artificial resonance.
