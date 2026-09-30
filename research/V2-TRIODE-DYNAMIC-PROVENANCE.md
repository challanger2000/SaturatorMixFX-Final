# SMX-3 V2 TRI0DE Dynamic Reference Provenance

Date: 2026-09-30

## What is authoritative

The current dynamic TRI0DE reference intentionally combines two independent evidence sources:

### Tube device law
Dempwolf & Zoelzer, DAFx-2011:
- measured/fitted practical 12AX7 specimen parameters;
- RSD-2 selected as the current primary measured-specimen reference after manufacturer-loaded and dynamic cross-check;
- explicit grid-current law;
- published parasitic capacitances Cak=0.9 pF, Cgk=2.3 pF, Cag=2.4 pF.

Evidence:
PUBLISHED-PARAMETER DERIVED / MEASURED-SPECIMEN MODEL.

### Surrounding amplifier network
Philips/Mullard ECC83 manufacturer operating-characteristics sheet:
- Vb=250 V selected row;
- Ra=100 kOhm;
- Rk=1.5 kOhm;
- following-stage load=330 kOhm;
- input grid leak=1 MOhm;
- input coupling capacitor=0.01 uF;
- cathode bypass capacitor=50 uF;
- output coupling capacitor=0.01 uF.

Evidence:
DOCUMENTED manufacturer circuit/network.

## Important non-equivalence

Dempwolf DAFx-2011 Figure 8 publishes the common-cathode topology and Figure 9 publishes the excitation cases, but the paper does not publish the numerical component values for that particular laboratory Figure-8 amplifier.

The paper states that Figure 9 used:
- 500 Hz sine at 2 V, 4 V and 8 V;
- 4 V sine bursts at 500 Hz, 1 kHz and 2 kHz;
- measurement/simulation sample rate 96 kHz.

Those excitation cases are DOCUMENTED.

However, because the Figure-8 component values are not given in the paper, the current SMX-3 Mullard-network solver must NOT claim numerical waveform agreement with Dempwolf Figure 9.

## Correct use of the Dempwolf Figure-9 cases

Until the exact laboratory component values are recovered from a primary or author-provided source, the Figure-9 signals may be used as:

- severe dynamic/grid-current stress stimuli;
- solver-convergence stimuli;
- blocking/recovery diagnostics;
- qualitative waveform-shape sanity checks.

They are NOT:
- an absolute voltage-output fixture;
- an RMS/THD acceptance target for the Mullard-network circuit;
- a direct residual comparison against the published Figure-9 traces.

## Current authority statement

The correct name for the current solver is:

"RSD-2 measured 12AX7 device model embedded in a documented Mullard/Philips ECC83 R-C amplifier network."

It is not:

"an exact reproduction of the Dempwolf Figure-8 amplifier."

## Promotion requirements

The current dynamic reference may be promoted as SMX-3's TRI0DE offline authority when:

1. its numerical integration is demonstrably converged;
2. a second numerical formulation cross-checks the same circuit;
3. grid voltage/current and low-anode-voltage excursions are reported;
4. frequency/level fixtures are frozen;
5. the chosen Drive operating domain avoids relying materially on known invalid Dempwolf regions (positive grid combined with Va below about 20 V);
6. the distinction between measured RSD-2 specimen behavior and Mullard average production data remains explicit.

Exact Dempwolf Figure-9 residual comparison is optional and becomes valid only if the original laboratory component values are recovered.


## Specimen-selection correction — 2026-09-30

A direct same-network comparison was run for EHX-1 and RSD-2.

RSD-2 remains numerically stable in the full dynamic circuit and is closer to the Mullard loaded reference on the combined static criteria:
- idle cathode current;
- loaded small-signal gain;
- distortion at the 26 Vrms manufacturer output point.

Representative settled dynamic results:
- 1 kHz / 10 mVrms: RSD-2 gain ~56.40, THD ~0.0747%; EHX-1 gain ~49.44, THD ~0.0431%;
- 1 kHz / 0.5 Vrms: RSD-2 THD ~4.19%; EHX-1 ~2.42%;
- 1 kHz / 0.7 Vrms: RSD-2 THD ~6.60%; EHX-1 ~3.90%.

These differences are specimen behavior, not a reason to choose 'more distortion'.

Selection is based on the independent manufacturer-loaded circuit comparison, with the dynamic comparison used to confirm stability and plausible progression.

Dempwolf/Zoelzer state that the same tubes used during fitting were operated in their test circuit, but the paper text does not establish EHX-1 as the unique Figure-9 specimen. Therefore there is no primary-source requirement to retain EHX-1 as SMX-3's primary specimen.

EHX-1 remains a mandatory independent measured-specimen cross-check.
