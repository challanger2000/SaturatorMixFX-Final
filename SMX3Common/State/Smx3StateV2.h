#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <limits>

namespace SaturatorMixFX {
namespace StateV2 {

constexpr std::uint32_t kMagic = 0x32584D53u;
constexpr std::uint32_t kFormatVersion = 1u;
constexpr std::size_t kLegacyBytes = 5u * sizeof(double);
constexpr std::size_t kHeaderBytes = 4u * sizeof(std::uint32_t);
constexpr std::size_t kV1PayloadBytes = 5u * sizeof(double);
constexpr std::size_t kV2Bytes = kHeaderBytes + kV1PayloadBytes;

struct Parameters
{
    double bypass = 0.0;
    double drive = 0.30;
    double character = 0.0;
    double mix = 1.0;
    double output = 0.75;
};

enum class Source
{
    Invalid,
    LegacyV1,
    VersionedV2
};

struct DecodeResult
{
    Source source = Source::Invalid;
    Parameters params{};
};

inline bool finite(double v)
{
    return v == v &&
           v != std::numeric_limits<double>::infinity() &&
           v != -std::numeric_limits<double>::infinity();
}

inline double clamp01(double v)
{
    return v < 0.0 ? 0.0 : (v > 1.0 ? 1.0 : v);
}

inline void putU32LE(std::uint8_t* dst, std::uint32_t v)
{
    dst[0] = static_cast<std::uint8_t>(v & 0xffu);
    dst[1] = static_cast<std::uint8_t>((v >> 8) & 0xffu);
    dst[2] = static_cast<std::uint8_t>((v >> 16) & 0xffu);
    dst[3] = static_cast<std::uint8_t>((v >> 24) & 0xffu);
}

inline std::uint32_t getU32LE(const std::uint8_t* src)
{
    return static_cast<std::uint32_t>(src[0]) |
           (static_cast<std::uint32_t>(src[1]) << 8) |
           (static_cast<std::uint32_t>(src[2]) << 16) |
           (static_cast<std::uint32_t>(src[3]) << 24);
}

inline void putDoubleLE(std::uint8_t* dst, double v)
{
    static_assert(sizeof(double) == 8, "SMX-3 state requires IEEE-754 64-bit double storage");
    std::uint64_t bits = 0;
    std::memcpy(&bits, &v, sizeof(bits));
    for (int i = 0; i < 8; ++i)
        dst[i] = static_cast<std::uint8_t>((bits >> (8 * i)) & 0xffu);
}

inline double getDoubleLE(const std::uint8_t* src)
{
    std::uint64_t bits = 0;
    for (int i = 0; i < 8; ++i)
        bits |= static_cast<std::uint64_t>(src[i]) << (8 * i);
    double v = 0.0;
    std::memcpy(&v, &bits, sizeof(v));
    return v;
}

inline bool sanitize(const Parameters& in, Parameters& out)
{
    if (!finite(in.bypass) || !finite(in.drive) || !finite(in.character) ||
        !finite(in.mix) || !finite(in.output))
        return false;

    out.bypass = clamp01(in.bypass);
    out.drive = clamp01(in.drive);
    out.character = clamp01(in.character);
    out.mix = clamp01(in.mix);
    out.output = clamp01(in.output);
    return true;
}

inline std::array<std::uint8_t, kV2Bytes> encode(const Parameters& p)
{
    std::array<std::uint8_t, kV2Bytes> out{};
    putU32LE(out.data() + 0, kMagic);
    putU32LE(out.data() + 4, kFormatVersion);
    putU32LE(out.data() + 8, static_cast<std::uint32_t>(kV1PayloadBytes));
    putU32LE(out.data() + 12, 0u);

    putDoubleLE(out.data() + 16, p.bypass);
    putDoubleLE(out.data() + 24, p.drive);
    putDoubleLE(out.data() + 32, p.character);
    putDoubleLE(out.data() + 40, p.mix);
    putDoubleLE(out.data() + 48, p.output);
    return out;
}

inline DecodeResult decode(const std::uint8_t* data, std::size_t size)
{
    DecodeResult r{};
    if (!data)
        return r;

    Parameters raw{};

    if (size == kLegacyBytes)
    {
        raw.bypass = getDoubleLE(data + 0);
        raw.drive = getDoubleLE(data + 8);
        raw.character = getDoubleLE(data + 16);
        raw.mix = getDoubleLE(data + 24);
        raw.output = getDoubleLE(data + 32);

        if (!sanitize(raw, r.params))
            return {};

        r.source = Source::LegacyV1;
        return r;
    }

    if (size < kHeaderBytes)
        return r;

    const std::uint32_t magic = getU32LE(data + 0);
    const std::uint32_t version = getU32LE(data + 4);
    const std::uint32_t payloadBytes = getU32LE(data + 8);

    if (magic != kMagic || version != kFormatVersion)
        return r;
    if (payloadBytes < kV1PayloadBytes)
        return r;
    if (size < kHeaderBytes + static_cast<std::size_t>(payloadBytes))
        return r;

    raw.bypass = getDoubleLE(data + 16);
    raw.drive = getDoubleLE(data + 24);
    raw.character = getDoubleLE(data + 32);
    raw.mix = getDoubleLE(data + 40);
    raw.output = getDoubleLE(data + 48);

    if (!sanitize(raw, r.params))
        return {};

    r.source = Source::VersionedV2;
    return r;
}

} // namespace StateV2
} // namespace SaturatorMixFX
