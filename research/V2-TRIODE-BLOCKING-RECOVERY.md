# SMX-3 V2 TRI0DE Grid-Current Blocking / Recovery Sensitivity

Date: 2026-09-30
Status: INFORMATIONAL research fixture

## Purpose

The current primary dynamic TRI0DE reference uses the Dempwolf/Zoelzer RSD-2 specimen.

Independent measurements show meaningful spread in positive-grid current.

To isolate the effect of that uncertainty, this fixture holds fixed:
- RSD-2 plate/cathode-current law;
- documented Philips/Mullard surrounding circuit;
- parasitic capacitances;
- numerical integration.

Only Ig(Vg) is changed.

Compared grid-current laws:
- RSD-2;
- RSD-1;
- EHX-1;
- Danyuk AES-137 polynomial overload fit.

The latter three hybrid runs are sensitivity experiments, not complete physical tube models.

## Fixture

- 1 kHz sine
- baseline: 0.10 Vrms for 200 ms
- overdrive: 1.50 Vrms for 100 ms
- recovery: 0.10 Vrms for 400 ms
- 96 kHz integration for comparative research

Switches occur at integer 1 kHz cycle boundaries so the source voltage is continuous.

## Metrics

For every grid-current law:
- baseline gain;
- stress peak grid current;
- maximum Vg;
- mean grid/cathode bias;
- post-stress gain relative to baseline at:
  - 0-20 ms
  - 50-70 ms
  - 100-120 ms
  - 200-220 ms
  - 350-370 ms.

## Decision use

If recovery behavior changes materially across measured grid-current laws:
- Drive 75-100% cannot be calibrated from RSD-2 alone without an explicit specimen/archetype decision.

If differences are small:
- RSD-2 can remain the simpler coherent measured-specimen reference.

Do not average grid-current equations merely to obtain an intermediate sound. Any archetype fit must be separately justified and measured.
