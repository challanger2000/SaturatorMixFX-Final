# SMX-3 V2 Identity and State Compatibility

Status: design freeze before production wiring

## Parallel-install requirement

SMX-3 V1 and V2 must be installable at the same time.

Therefore V2 receives:
- new processor UID;
- new controller UID;
- distinct public plugin name;
- distinct VST3 bundle/target name.

V1 identifiers remain unchanged.

## Frozen V1 identifiers

### Channel
Processor:
74D9F51A-2E75-4BC8-A943-9C721DB0A1F4

Controller:
1D27F0E2-A984-42CE-B8B0-B6D190E83753

### Mix FX
Processor:
A54E2D71-6C8B-4F29-9E13-4A62C7D5B801

Controller:
3F91C6A4-D2E7-485B-B06A-1F9374CE520D

These values are compatibility evidence and must not be changed in V1.

## Proposed frozen V2 identifiers

Generated deterministically from the repository/project namespace and role names, so provenance is reproducible rather than depending on an undocumented random UUID generator.

### SMX-3 V2 Channel
Processor:
86D3F3F0-E778-5981-8ED1-204F08A35C82

Steinberg FUID words:
- 0x86D3F3F0
- 0xE7785981
- 0x8ED1204F
- 0x08A35C82

Controller:
17D4F54D-0E35-572C-94A7-55F2F0BD2F7A

FUID words:
- 0x17D4F54D
- 0x0E35572C
- 0x94A755F2
- 0xF0BD2F7A

### SMX-3 V2 Mix FX
Processor:
E31C8403-A6C6-5716-A0A9-91FEBBD41869

FUID words:
- 0xE31C8403
- 0xA6C65716
- 0xA0A991FE
- 0xBBD41869

Controller:
32430640-0732-5598-89D7-B1F7CD066E49

FUID words:
- 0x32430640
- 0x07325598
- 0x89D7B1F7
- 0xCD066E49

Generation provenance:
UUIDv5 namespace derived from
https://github.com/challanger2000/SaturatorMixFX-Final/SMX-3-V2

Role strings:
- SMX-3 V2 Channel Processor
- SMX-3 V2 Channel Controller
- SMX-3 V2 Mix FX Processor
- SMX-3 V2 Mix FX Controller

## Public names

Proposed:
- SMX-3 V2 Channel
- SMX-3 V2 Mix FX

Do not silently reuse the V1 public class names with new UIDs unless host tests prove that naming does not create confusing duplicate entries.

## Existing parameter IDs

Preserve:
- 99 Bypass
- 100 Drive
- 101 Character
- 102 Mix
- 103 Output

Reason:
- migration logic;
- automation semantic continuity;
- controller/core consistency;
- lower project-recall risk.

V2 Character semantics remain the same visible choices:
- Triode
- Pentode
- Iron

The internal V2 implementation changes from legacy blended heuristics to physical-model steady states, but the visible ordering remains compatible.

## V1 state format

Legacy V1 processor/component state is exactly five little-endian doubles:

1. bypass
2. drive
3. character
4. mix
5. output

Total payload:
40 bytes

No header/version tag.

This exact 40-byte legacy payload is the V1 migration signature.

## V2 state format

V2 writes a self-identifying versioned format.

Proposed binary layout:

- uint32 magic = 0x32584D53
  - little-endian bytes spell a stable SMX2 marker convention
- uint32 formatVersion = 1
- uint32 payloadBytes
- uint32 flags/reserved = 0
- double bypass
- double drive
- double character
- double mix
- double output
- future fields appended according to format version

All integer/double fields use little-endian serialization through Steinberg IBStreamer-compatible operations.

The exact magic value must be unit-tested as bytes before release; the human-readable mnemonic is documentation only.

## Read algorithm

V2 setState/setComponentState:

1. determine/read enough input to distinguish legacy vs versioned state without destroying the stream position;
2. if payload is exactly/validly recognizable as legacy five-double state:
   - read five doubles in original order;
   - clamp normalized parameters;
   - assign safe V2 defaults for all new fields;
   - mark migration source = V1 in diagnostic test code only.
3. if V2 magic:
   - validate format version;
   - validate payload length;
   - read known fields;
   - skip forward-compatible unknown tail only when format contract allows it;
   - reject malformed/truncated/non-finite mandatory data safely.
4. no partial application on parse failure.

## Migration semantics

V1 Drive/Character/Mix/Output values are preserved numerically.

However:
- V2 physical DSP will not be sample-identical to V1 after migration;
- migration preserves user intent and automation values, not old sound;
- old V1 remains installed for exact historical project sound.

This is why parallel installation is mandatory.

## New physical-state policy

Do NOT serialize arbitrary solver history blindly.

For Triode/Pentode:
- ordinary dynamic capacitor/bias states reset deterministically on activation/project load unless a specific audible recall need is proven.

For Iron:
- remanent/hysteresis state requires explicit policy.
- default preference is deterministic reset to the documented demagnetized reference state.
- do not restore arbitrary history unless project-recall tests show it is musically necessary and safe.

Parameters/settings are project state.
Microscopic integrator history is not automatically project state.

## Migration regression fixtures

Required fixtures:
- all-default V1 40-byte payload;
- each parameter at min/max individually;
- all parameters at representative mid values;
- Character exactly Triode/Pentode/Iron normalized values;
- malformed payload lengths 0..39 bytes;
- V2 magic with unsupported version;
- truncated V2 header;
- NaN/Inf encoded parameter fields;
- future-tail payload.

Checks:
- no crash;
- no partial state;
- legacy values preserved/clamped as specified;
- controller state mirrors processor state;
- save-load-save deterministic.

## Release naming/version

V2 build system must report project version 2.x only after the V2 identity is wired.

Do not modify the V1 main branch's 0.1.1 project files.

The development branch may move to 2.0.0 only in the same coherent commit that establishes V2 plugin identity and packaging.
