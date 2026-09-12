# 125A SMX-3

**SMX-3** is a free saturation processor for Studio One / Fender Studio. The package contains two Windows x64 VST3 plug-ins:

- **SMX-3 Mix FX** — dedicated Mix FX build for Studio One / Fender Studio.
- **SMX-3 Channel** — conventional VST3 channel insert using the same saturation concept.

SMX-3 is both a usable saturation tool and a public proof that third-party Mix FX integration can be implemented.

## Controls

- **Bypass / On-Off** — enables or bypasses processing.
- **Drive** — sets the amount of saturation.
- **Character** — selects **Triode**, **Pentode** or **Iron**.
- **Mix** — blends dry and processed signal.
- **Output** — sets the output level.

All main parameters are automatable.

## Installation

Copy both `.vst3` bundles to your VST3 plug-in folder, normally:

`C:\Program Files\Common Files\VST3`

Then rescan plug-ins in Studio One / Fender Studio if required.

Use **SMX-3 Channel** as a normal insert effect. Use **SMX-3 Mix FX** in the host's Mix FX slot.

## Manual

See [BEDIENUNGSANLEITUNG.md](BEDIENUNGSANLEITUNG.md) for the German user manual.

## Platform

- Windows x64
- VST3
- Studio One / Fender Studio for Mix FX operation

## Validation

Both plug-in variants are built with the Steinberg VST3 SDK and are checked with the Steinberg VST3 validator in the release workflow.

## Build

The repository builds both final plug-ins from one source tree:

- `SMX-3-Channel.vst3`
- `SMX-3-MixFX.vst3`

The Mix FX target uses the host-specific factory category required for Mix FX registration, while the Channel target is a standard VST3 audio effect.

## Freeware

SMX-3 is provided free of charge by **125A**. See [LICENSE.txt](LICENSE.txt) for the distribution terms.
