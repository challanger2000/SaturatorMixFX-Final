# SMX-3 V2 TRI0DE Large-Signal Baseline

Date: 2026-09-30
Tool: tools/smx3_v2_ecc83_large_signal.py

## Reference

Tube:
- 12AX7 EHX-1 parameter set measured/fitted by Dempwolf & Zoelzer.

Circuit:
- Mullard ECC83 common-cathode reference;
- Vb=250 V;
- Ra=100 kOhm;
- Rk=1.5 kOhm;
- 330 kOhm following-stage grid load included as AC plate load;
- cathode assumed AC-bypassed for this low-frequency/static large-signal baseline.

This baseline intentionally precedes parasitic capacitance and coupling-network simulation.

## DC point

Approximately:
- Ik = 0.8248 mA
- Vk = 1.2372 V
- plate node = 167.52 V

This remains consistent with the previously frozen Mullard operating-point comparison.

## Harmonic progression

Representative results:

| Vin RMS | Vout RMS | THD | H2 | H3 | peak grid current |
|---:|---:|---:|---:|---:|---:|
| 0.10 V | ~5.02 V | ~0.434 % | ~0.434 % | ~0.011 % | ~0.000039 mA |
| 0.30 V | ~15.02 V | ~1.344 % | ~1.339 % | ~0.106 % | ~0.000039 mA |
| 0.50 V | ~24.89 V | ~2.395 % | ~2.373 % | ~0.321 % | ~0.000051 mA |
| 0.70 V | ~34.50 V | ~3.729 % | ~3.656 % | ~0.719 % | ~0.000622 mA |
| 1.00 V | ~47.76 V | ~6.545 % | ~6.142 % | ~2.217 % | ~0.04685 mA |
| 1.50 V | ~64.80 V | ~13.99 % | ~12.34 % | ~6.54 % | ~0.283 mA |
| 2.00 V | ~78.99 V | ~20.30 % | ~18.34 % | ~8.48 % | ~0.558 mA |

## Interpretation

The selected reference naturally produces:
- strong low-level second harmonic;
- progressive odd-harmonic growth with drive;
- increasing asymmetry rather than a fixed static clipping threshold;
- rapid grid-current growth once instantaneous grid voltage approaches/crosses the cathode potential.

No explicit "even harmonic amount" parameter is required.

This is exactly the behaviour V2 should preserve qualitatively when the physical reference is reduced to realtime DSP.

## Important Dempwolf model limitation

The source paper explicitly notes that the model becomes inaccurate for:
- positive grid voltage;
- very low anode voltage, roughly Va < 20 V.

Therefore the V2 reference solver must flag samples entering this region.

Production mapping should avoid depending on that invalid region for the normal 0-75% Drive range. If 75-100% intentionally enters extreme operation, a bounded extension or different low-Va model must be justified and tested.

## Next TRI0DE steps

1. Add Cak=0.9 pF, Cgk=2.3 pF, Cag=2.4 pF.
2. Add actual coupling/bypass network.
3. Test Dempwolf paper excitation cases:
   - 500 Hz sinusoidal input at 2/4/8 V;
   - 4 V sine bursts at 500 Hz / 1 kHz / 2 kHz.
4. Build a high-accuracy offline dynamic reference.
5. Only then derive the realtime/oversampled production kernel and compare harmonic/step/burst residuals.
