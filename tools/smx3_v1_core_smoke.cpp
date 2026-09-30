#include "../SMX3Common/DSP/Smx3V1Reference.h"

#include <cmath>
#include <cstdint>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <limits>
#include <string>

using SaturatorMixFX::V1Reference::Core;

static std::uint64_t fnv1a(std::uint64_t h, double v)
{
    std::uint64_t bits=0;
    static_assert(sizeof(bits)==sizeof(v),"unexpected double size");
    std::memcpy(&bits,&v,sizeof(bits));
    for(int i=0;i<8;++i)
    {
        h ^= static_cast<unsigned char>((bits>>(8*i))&0xffu);
        h *= 1099511628211ull;
    }
    return h;
}

static double inputSample(int n,double sr)
{
    const double t=static_cast<double>(n)/sr;
    const double s =
        0.31*std::sin(2.0*3.14159265358979323846*97.0*t)
        +0.17*std::sin(2.0*3.14159265358979323846*997.0*t+0.37)
        +0.09*std::sin(2.0*3.14159265358979323846*8111.0*t+1.13);

    // Deterministic transient content without random-number-library dependence.
    const double impulse=(n%509==0)?0.47:0.0;
    const double polarity=((n/113)&1)?-1.0:1.0;
    return 0.72*s+polarity*impulse;
}

static int runCase(double sr,double drive,double character,double mix,double output,std::uint64_t expectedHash)
{
    Core core;
    core.prepare(sr);
    Core::ChannelState st{};
    Core::Params p{drive,character,mix,output};

    constexpr int N=8192;
    std::uint64_t hash=1469598103934665603ull;
    long double sum2=0.0L;
    double peak=0.0;

    for(int n=0;n<N;++n)
    {
        const double x=inputSample(n,sr);
        const double y=core.processSample(x,st,p);
        if(!std::isfinite(y))
        {
            std::cerr<<"non-finite output at n="<<n<<"\n";
            return 2;
        }
        hash=fnv1a(hash,y);
        sum2+=static_cast<long double>(y)*static_cast<long double>(y);
        peak=std::max(peak,std::abs(y));
    }

    const double rms=std::sqrt(static_cast<double>(sum2/N));
    std::cout<<std::fixed<<std::setprecision(12)
             <<"sr="<<sr
             <<" drive="<<drive
             <<" character="<<character
             <<" mix="<<mix
             <<" output="<<output
             <<" rms="<<rms
             <<" peak="<<peak
             <<" hash=0x"<<std::hex<<hash<<std::dec<<"\n";
    return 0;
}

int main()
{
    const double rates[]={44100.0,48000.0,96000.0,192000.0};
    const Core::Params cases[]={
        {0.00,0.00,1.00,0.75},
        {0.30,0.00,1.00,0.75},
        {0.50,0.50,1.00,0.75},
        {0.75,1.00,1.00,0.75},
        {1.00,0.00,0.50,0.75},
        {0.50,1.00,0.00,0.75},
        {0.50,0.50,1.00,1.00},
    };

    const std::uint64_t golden[4][7]={
        {
            0xa12a8e5c8732ac7aull,0x2771226c2f0463cbull,0xc0a28e7d89c6924bull,
            0x3f398a757de0711bull,0x359cbe8874026460ull,0xa12a8e5c8732ac7aull,
            0x69ed3949db3c3ce3ull
        },
        {
            0xc7dcade7b2f3cb7dull,0x026073cbc2f78904ull,0xc4a3b996c40044a3ull,
            0x0f33469406dceab3ull,0x6600fa26739e001eull,0xc7dcade7b2f3cb7dull,
            0xad0db1b0c1f69672ull
        },
        {
            0xf5a7f278f2c79e5aull,0xb0e2e61bde2878eull,0x21be72e2eb3c3bb0ull,
            0x03d25de4c580efdaull,0x6c0edd6aee7447e1ull,0xf5a7f278f2c79e5aull,
            0x08562f979493a8b8ull
        },
        {
            0xe18cd2e0d38ef23dull,0xdd5cfda2b31386dcull,0xd9673f82b960c75aull,
            0x3f385c7a7fead2fbull,0xd4e04933a7f80d6aull,0xe18cd2e0d38ef23dull,
            0x94e25ba118b47e2cull
        }
    };

    for(int ri=0;ri<4;++ri)
        for(int ci=0;ci<7;++ci)
        {
            const auto& p=cases[ci];
            if(const int rc=runCase(rates[ri],p.drive,p.character,p.mix,p.output,golden[ri][ci]))
                return rc;
        }

    // Reset determinism test.
    Core c;
    c.prepare(48000.0);
    Core::ChannelState a{},b{};
    Core::Params p{0.63,0.5,0.81,0.75};
    for(int n=0;n<4096;++n)
    {
        const double x=inputSample(n,48000.0);
        const double ya=c.processSample(x,a,p);
        const double yb=c.processSample(x,b,p);
        if(ya!=yb)
        {
            std::cerr<<"reset/determinism mismatch at n="<<n<<"\n";
            return 3;
        }
    }

    std::cout<<"PASS: shared V1 reference core finite/deterministic smoke test\n";
    return 0;
}
