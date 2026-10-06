#pragma once

#include "Smx3StateV2.h"
#include "base/source/fstreamer.h"
#include "pluginterfaces/base/ibstream.h"

#include <cstddef>
#include <cstdint>

namespace SaturatorMixFX {
namespace StateV2 {

inline DecodeResult readFromStream(Steinberg::IBStream* stream)
{
    DecodeResult invalid{};
    if (!stream)
        return invalid;

    Steinberg::IBStreamer io(stream, Steinberg::kLittleEndian);
    const auto start = io.tell();
    if (start < 0)
        return invalid;

    Steinberg::int32 marker = 0;
    if (!io.readInt32(marker))
        return invalid;

    if (static_cast<std::uint32_t>(marker) != kMagic)
    {
        if (io.seek(start, Steinberg::kSeekSet) != start)
            return invalid;

        Parameters legacy{};
        if (!io.readDouble(legacy.bypass) ||
            !io.readDouble(legacy.drive) ||
            !io.readDouble(legacy.character) ||
            !io.readDouble(legacy.mix) ||
            !io.readDouble(legacy.output))
            return invalid;

        DecodeResult result{};
        if (!sanitize(legacy, result.params))
            return invalid;
        result.source = Source::LegacyV1;
        return result;
    }

    Steinberg::int32 version = 0;
    Steinberg::int32 payloadBytes = 0;
    Steinberg::int32 reserved = 0;
    if (!io.readInt32(version) ||
        !io.readInt32(payloadBytes) ||
        !io.readInt32(reserved))
        return invalid;

    (void)reserved;

    if (static_cast<std::uint32_t>(version) != kFormatVersion ||
        payloadBytes < static_cast<Steinberg::int32>(kV1PayloadBytes))
        return invalid;

    Parameters current{};
    if (!io.readDouble(current.bypass) ||
        !io.readDouble(current.drive) ||
        !io.readDouble(current.character) ||
        !io.readDouble(current.mix) ||
        !io.readDouble(current.output))
        return invalid;

    const auto extraBytes =
        payloadBytes - static_cast<Steinberg::int32>(kV1PayloadBytes);
    if (extraBytes > 0)
    {
        const auto pos = io.tell();
        if (pos < 0 || io.seek(pos + extraBytes, Steinberg::kSeekSet) != pos + extraBytes)
            return invalid;
    }

    DecodeResult result{};
    if (!sanitize(current, result.params))
        return invalid;
    result.source = Source::VersionedV2;
    return result;
}

inline bool writeToStream(Steinberg::IBStream* stream, const Parameters& params)
{
    if (!stream)
        return false;

    Parameters safe{};
    if (!sanitize(params, safe))
        return false;

    Steinberg::IBStreamer io(stream, Steinberg::kLittleEndian);

    return io.writeInt32(static_cast<Steinberg::int32>(kMagic)) &&
           io.writeInt32(static_cast<Steinberg::int32>(kFormatVersion)) &&
           io.writeInt32(static_cast<Steinberg::int32>(kV1PayloadBytes)) &&
           io.writeInt32(0) &&
           io.writeDouble(safe.bypass) &&
           io.writeDouble(safe.drive) &&
           io.writeDouble(safe.character) &&
           io.writeDouble(safe.mix) &&
           io.writeDouble(safe.output);
}

} // namespace StateV2
} // namespace SaturatorMixFX
