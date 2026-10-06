#pragma once

#include "Smx3StateV2.h"
#include "pluginterfaces/base/ibstream.h"

#include <array>
#include <cstddef>
#include <cstdint>

namespace SaturatorMixFX {
namespace StateV2 {

constexpr std::size_t kMaxSerializedBytes = 256u;

inline bool readExact(Steinberg::IBStream* stream, void* dst, Steinberg::int32 bytes)
{
    if (!stream || !dst || bytes < 0)
        return false;

    auto* out = static_cast<std::uint8_t*>(dst);
    Steinberg::int32 total = 0;
    while (total < bytes)
    {
        Steinberg::int32 got = 0;
        const auto result = stream->read(out + total, bytes - total, &got);
        if (result != Steinberg::kResultOk || got <= 0)
            return false;
        total += got;
    }
    return true;
}

inline bool writeExact(Steinberg::IBStream* stream, const void* src, Steinberg::int32 bytes)
{
    if (!stream || !src || bytes < 0)
        return false;

    auto* in = static_cast<const std::uint8_t*>(src);
    Steinberg::int32 total = 0;
    while (total < bytes)
    {
        Steinberg::int32 written = 0;
        const auto result = stream->write(const_cast<std::uint8_t*>(in + total), bytes - total, &written);
        if (result != Steinberg::kResultOk || written <= 0)
            return false;
        total += written;
    }
    return true;
}

inline DecodeResult readFromStream(Steinberg::IBStream* stream)
{
    DecodeResult invalid{};
    if (!stream)
        return invalid;

    std::array<std::uint8_t, kMaxSerializedBytes> bytes{};

    // Four bytes are sufficient to distinguish the V2 magic from the legacy
    // five-double payload without seeking backwards in the host stream.
    if (!readExact(stream, bytes.data(), 4))
        return invalid;

    if (getU32LE(bytes.data()) != kMagic)
    {
        if (!readExact(stream, bytes.data() + 4,
                       static_cast<Steinberg::int32>(kLegacyBytes - 4)))
            return invalid;
        return decode(bytes.data(), kLegacyBytes);
    }

    if (!readExact(stream, bytes.data() + 4,
                   static_cast<Steinberg::int32>(kHeaderBytes - 4)))
        return invalid;

    const std::uint32_t payloadBytes = getU32LE(bytes.data() + 8);
    if (payloadBytes < kV1PayloadBytes)
        return invalid;

    const std::size_t total = kHeaderBytes + static_cast<std::size_t>(payloadBytes);
    if (total > bytes.size())
        return invalid;

    if (!readExact(stream, bytes.data() + kHeaderBytes,
                   static_cast<Steinberg::int32>(payloadBytes)))
        return invalid;

    return decode(bytes.data(), total);
}

inline bool writeToStream(Steinberg::IBStream* stream, const Parameters& params)
{
    if (!stream)
        return false;

    Parameters safe{};
    if (!sanitize(params, safe))
        return false;

    const auto bytes = encode(safe);
    return writeExact(stream, bytes.data(), static_cast<Steinberg::int32>(bytes.size()));
}

} // namespace StateV2
} // namespace SaturatorMixFX
