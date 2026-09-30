#include "../SMX3Common/State/Smx3StateV2.h"

#include <cmath>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <limits>
#include <vector>

using namespace SaturatorMixFX::StateV2;

static bool eq(double a,double b) { return std::abs(a-b) < 1e-15; }

static std::vector<std::uint8_t> legacy(const Parameters& p)
{
    std::vector<std::uint8_t> b(kLegacyBytes);
    putDoubleLE(b.data()+0,p.bypass);
    putDoubleLE(b.data()+8,p.drive);
    putDoubleLE(b.data()+16,p.character);
    putDoubleLE(b.data()+24,p.mix);
    putDoubleLE(b.data()+32,p.output);
    return b;
}

static bool same(const Parameters& a,const Parameters& b)
{
    return eq(a.bypass,b.bypass)&&eq(a.drive,b.drive)&&eq(a.character,b.character)&&
           eq(a.mix,b.mix)&&eq(a.output,b.output);
}

int main()
{
    const Parameters p{1.0,0.17,0.5,0.23,0.81};

    const auto old=legacy(p);
    const auto d1=decode(old.data(),old.size());
    if(d1.source!=Source::LegacyV1 || !same(d1.params,p))
    {
        std::cerr<<"legacy decode failed\n";
        return 1;
    }

    const auto enc=encode(p);
    if(getU32LE(enc.data())!=kMagic || getU32LE(enc.data()+4)!=kFormatVersion ||
       getU32LE(enc.data()+8)!=kV1PayloadBytes)
    {
        std::cerr<<"header mismatch\n";
        return 2;
    }

    const auto d2=decode(enc.data(),enc.size());
    if(d2.source!=Source::VersionedV2 || !same(d2.params,p))
    {
        std::cerr<<"V2 round trip failed\n";
        return 3;
    }

    // Truncation must fail without partial application.
    for(std::size_t n=0;n<enc.size();++n)
    {
        if(n==kLegacyBytes)
            continue; // 40 bytes intentionally has legacy semantics.
        if(decode(enc.data(),n).source!=Source::Invalid)
        {
            std::cerr<<"unexpected truncated acceptance n="<<n<<"\n";
            return 4;
        }
    }

    // Legacy out-of-range values are finite and deliberately clamped.
    Parameters out{-1.0,2.0,-0.25,4.0,1.5};
    const auto oldOut=legacy(out);
    const auto dc=decode(oldOut.data(),oldOut.size());
    if(dc.source!=Source::LegacyV1 || !eq(dc.params.bypass,0.0) || !eq(dc.params.drive,1.0) ||
       !eq(dc.params.character,0.0) || !eq(dc.params.mix,1.0) || !eq(dc.params.output,1.0))
    {
        std::cerr<<"legacy clamp failed\n";
        return 5;
    }

    // Non-finite mandatory parameter must reject the entire state.
    Parameters nanp=p;
    nanp.drive=std::numeric_limits<double>::quiet_NaN();
    const auto oldNan=legacy(nanp);
    if(decode(oldNan.data(),oldNan.size()).source!=Source::Invalid)
    {
        std::cerr<<"NaN legacy state accepted\n";
        return 6;
    }

    auto v2Nan=encode(p);
    putDoubleLE(v2Nan.data()+32,std::numeric_limits<double>::infinity());
    if(decode(v2Nan.data(),v2Nan.size()).source!=Source::Invalid)
    {
        std::cerr<<"Inf V2 state accepted\n";
        return 7;
    }

    // Unsupported version.
    auto badVersion=enc;
    putU32LE(badVersion.data()+4,99u);
    if(decode(badVersion.data(),badVersion.size()).source!=Source::Invalid)
    {
        std::cerr<<"unsupported version accepted\n";
        return 8;
    }

    // Future tail in same format version is allowed only when payload length
    // declares it and all mandatory V1 fields remain intact.
    std::vector<std::uint8_t> future(enc.begin(),enc.end());
    future.resize(enc.size()+8,0x5a);
    putU32LE(future.data()+8,static_cast<std::uint32_t>(kV1PayloadBytes+8));
    const auto df=decode(future.data(),future.size());
    if(df.source!=Source::VersionedV2 || !same(df.params,p))
    {
        std::cerr<<"future tail decode failed\n";
        return 9;
    }

    std::cout<<"PASS: SMX-3 V2 state codec legacy migration, round-trip, malformed and non-finite gates\n";
    return 0;
}
