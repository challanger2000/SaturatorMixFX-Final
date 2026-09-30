# SMX-3 V2 Level Calibration

Status: policy frozen; numerical per-mode calibration NOT frozen

## Important terminology

There is no existing 125A Engineering rule that fixes one universal dBFS <-> dBu mapping.

EBU R 68 documents a digital alignment signal 18 dB below full scale:
- digital alignment level: -18 dBFS

Source:
https://tech.ebu.ch/publications/r068

This does NOT by itself define +4 dBu = -18 dBFS for every interface or studio.

Therefore any mapping between SMX-3 digital level and a modeled hardware voltage/current is a PRODUCT CALIBRATION and must be documented as such.

## General signal mapping

Each physical model must expose an explicit engineering chain:

digital sample
-> calibration gain / input network
-> physical model input in volts/amperes
-> physical nonlinear circuit
-> physical output
-> explicit output calibration
-> plugin output sample

No hidden waveshaper coefficient may substitute for this mapping.

## Candidate external alignment convention

A useful candidate convention for later evaluation is:

- -18 dBFS sine RMS alignment -> conceptual +4 dBu external line level.

If adopted, +20 dBu would be 16 dB above nominal, corresponding to -2 dBFS relative sine level.

Evidence classification:
PRODUCT-DERIVED.

Reason it is useful:
- the Jensen JT-11P-1 data use +4 dBu and +20 dBu directly;
- it leaves a physically interpretable 16 dB interval between nominal and the documented 20 Hz / 1% THD region;
- it aligns naturally with an -18 dBFS digital engineering reference.

This mapping is NOT frozen until TRI0DE and PENTODE physical operating ranges are validated too.

## TRI0DE calibration status

NOT FROZEN.

Earlier EHX-1 / Mullard-derived Drive ladders are superseded.

Reason:
- the first EHX comparison used an unloaded plate-node gain;
- the later loaded Mullard multi-point fit reproduced DC and small-signal gain very well;
- that same fit failed the documented large-signal point badly (~36.6 Vrms / ~6.44% modeled versus Mullard 26 Vrms / 3.9%).

Therefore no current TRI0DE model is authoritative enough to define a production dBFS-to-grid-voltage Drive ladder.

Required before calibration:
1. accepted ECC83 large-signal reference;
2. verified grid-current onset;
3. verified manufacturer distortion/output point;
4. accepted input/coupling/bypass network;
5. frequency-dependent measurement.

## PENTODE calibration status

NOT FROZEN.

The provisional EF86 multi-anchor fit is promising in DC/small signal but has not yet passed:
- full Philips plate-curve family;
- knee validation;
- large-signal 5% distortion/output envelope.

No digital-to-EF86 input mapping is accepted until those gates pass.

## IRON calibration status

IRON has the strongest current physical level anchors because Jensen specifies real line input levels.

Documented targets include:
- +4 dBu / 20 Hz -> typical ~0.025% THD;
- +20 dBu / 20 Hz -> typical ~1% THD;
- +4 dBu / 1 kHz -> typical <0.001% THD.

However the current Jiles-Atherton example parameter shape has been rejected as a Jensen fit:
- after scaling to ~1% at +20 dBu / 20 Hz;
- it predicts roughly 0.153% at +4 dBu / 20 Hz.

Therefore even IRON's final production Drive mapping waits for an accepted magnetic parameter fit.

## Drive macro policy

The UI may keep one normalized Drive control, but the physical units underneath are model-specific.

Do NOT force TRI0DE, PENTODE and IRON to share one arbitrary internal voltage scale.

Instead:
- TRI0DE Drive maps to its accepted tube input network/grid excitation;
- PENTODE Drive maps to its accepted EF86 input network/grid excitation;
- IRON Drive maps to line input level / flux excitation.

Desired user-facing progression remains:
- 0%: active baseline hardware operation;
- 20-50%: musical;
- 50-75%: clearly nonlinear;
- 75-100%: strong/creative.

The numeric mapping is derived only after each model's measured THD/gain/crest/memory progression exists.

## Drive=0 semantics

Drive=0 is NOT required to be mathematically neutral.

For this hardware-modeling product:
- Bypass is the neutral reference.
- Active Drive=0 may impart the real baseline character of the selected hardware circuit.
- That character must arise naturally from the accepted physical/circuit model.

No artificial 'always-on analog color' stage is added merely to make Drive=0 audible.

## Mix=0 semantics

Mix=0 remains a separate dry-path decision.

Current target:
- Mix=0 returns the true dry input path.

Any departure from this must be explicitly justified by a measured architecture; it is not inherited from the hardware model's baseline color.

## Output calibration

Never alter physical-model coefficients merely to equalize loudness between modes.

Keep separate:
1. physical stage gain/loss;
2. model-to-plugin calibration;
3. optional listening/auto-level compensation;
4. explicit user Output control.

Reference measurements are performed without hidden auto-level.

Level-matched listening comparisons may use a separately measured compensation stage, reported explicitly.
