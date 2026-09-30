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

static int runCase(double sr,double drive,double character,double mix,double output)
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

    for(double sr:rates)
        for(const auto& p:cases)
            if(const int rc=runCase(sr,p.drive,p.character,p.mix,p.output))
                return rc;

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
