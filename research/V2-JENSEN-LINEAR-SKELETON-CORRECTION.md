# SMX-3 V2 Jensen Linear Skeleton — Source-Resistance Correction

Date: 2026-09-30
Status: AUTHORITATIVE CORRECTION

## Error found

The first low-frequency skeleton derived the effective magnetizing inductance Lm
from Jensen's 20 Hz relative-response anchor:

- 20 Hz relative to 1 kHz: typical -0.04 dB.

However, the original solve omitted the source resistance from the response-test path.

Jensen explicitly states for this response row:

- test circuit 1;
- Rs = 600 Ohm.

Therefore the original ~106.55 H value was derived under the wrong test condition.

## Correct test-condition split

### Transformer input impedance
Manufacturer anchor:
- ~13.0 kOhm at 1 kHz / +4 dBu.

Interpretation:
looking into the transformer input terminals.
The external source resistor is not part of the input impedance itself.

### Transformer voltage gain
Manufacturer anchor:
- ~-2.3 dB at 1 kHz / +4 dBu.

Interpretation:
transformer input terminals to loaded secondary output.

### Magnitude response
Manufacturer anchors:
- 20 Hz: ~-0.04 dB relative to 1 kHz;
- 20 kHz: ~-0.05 dB relative to 1 kHz.

For these rows Jensen explicitly specifies:
- Rs = 600 Ohm.

Therefore the response-test transfer function includes:
600 Ohm source resistance + transformer network.

## Corrected effective magnetizing inductance

Using:
- Rs_source = 600 Ohm;
- Rp = 1.45 kOhm;
- Rs_winding = 1.55 kOhm;
- RL = 10 kOhm;
- 1:1 turns ratio;
- response target -0.04 dB at 20 Hz relative to 1 kHz;

the corrected effective low-level magnetizing inductance is approximately:

**Lm = 144.0 H**

More precisely in the current solver:
~143.999434 H.

Evidence class:
CIRCUIT DERIVED from DOCUMENTED manufacturer test conditions.

## Consequences

Superseded:
- Lm ~106.554 H;
- any magnetic KPHI/KI calibration that depended on that value;
- any HF/DLP result computed with the old Lm.

Unaffected:
- documented winding DCR values;
- documented 13 kOhm input-impedance anchor;
- documented -2.3 dB transformer gain anchor;
- Jensen exact THD anchors themselves;
- Jiles-Atherton model family choice.

Must be re-derived:
- magnetic candidate geometry scaling;
- corrected c/KI fit;
- HF parasitic fit;
- DLP residual;
- final state/level calibration.

## QA rule

Every manufacturer anchor must carry its test-circuit conditions into the
reference equation.

Do not combine:
- transformer-terminal quantities;
- generator-to-load quantities;
- or source-loaded response quantities

unless the source/load network is explicitly represented.
