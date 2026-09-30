#include "../SMX3Common/DSP/Smx3V1Reference.h"
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <limits>
#include <vector>

using SaturatorMixFX::V1Reference::Core;

static double inputAt(std::int64_t n,double fs)
{
    const double t=static_cast<double>(n)/fs;
    const double a=.31*std::sin(2.0*3.14159265358979323846*83.0*t);
    const double b=.17*std::sin(2.0*3.14159265358979323846*997.0*t+.27);
    const double c=.09*std::sin(2.0*3.14159265358979323846*6137.0*t+.61);
    const double hit=((n%4096)<96)?(.35*std::exp(-static_cast<double>(n%4096)/28.0)):0.0;
    return a+b+c+hit;
}

static Core::Params paramsAt(std::int64_t n)
{
    const int phase=static_cast<int>((n/2048)%8);
    static const double drive[8]={0.0,.25,.50,.75,1.0,.65,.35,.10};
    static const double character[8]={0.0,0.0,.5,.5,1.0,1.0,.5,0.0};
    static const double mix[8]={1.0,1.0,1.0,.75,1.0,.5,1.0,1.0};
    return {drive[phase],character[phase],mix[phase],.75};
}

static std::vector<double> render(double fs,int block)
{
    constexpr int N=32768;
    Core core;
    Core::ChannelState state{};
    core.prepare(fs);
    std::vector<double> y(N);
    for(int base=0;base<N;base+=block)
    {
        const int end=std::min(N,base+block);
        for(int n=base;n<end;++n)
        {
            const auto p=paramsAt(n);
            const double v=core.processSampleV2Iron(inputAt(n,fs),state,p);
            if(!std::isfinite(v) || std::abs(v)>8.0)
            {
                std::cerr<<"non-finite/out-of-range fs="<<fs<<" block="<<block<<" n="<<n<<" v="<<v<<"\n";
                std::exit(10);
            }
            y[n]=v;
        }
    }
    return y;
}

int main()
{
    const double rates[]={44100.0,48000.0,96000.0,192000.0};
    const int blocks[]={1,16,64,257,1024};

    for(double fs:rates)
    {
        const auto ref=render(fs,32768);
        for(int b:blocks)
        {
            const auto y=render(fs,b);
            double maxErr=0.0;
            for(std::size_t i=0;i<y.size();++i)
                maxErr=std::max(maxErr,std::abs(y[i]-ref[i]));
            if(maxErr>1e-12)
            {
                std::cerr<<"block determinism failed fs="<<fs<<" block="<<b<<" maxErr="<<maxErr<<"\n";
                return 20;
            }
        }

        // Explicit mode/drive edge sweep.
        for(double c:{0.0,.5,1.0})
        {
            for(double d:{0.0,.25,.5,.75,1.0})
            {
                Core core;
                Core::ChannelState state{};
                core.prepare(fs);
                Core::Params p{d,c,1.0,.75};
                double energy=0.0;
                for(int n=0;n<8192;++n)
                {
                    const double v=core.processSampleV2Iron(inputAt(n,fs),state,p);
                    if(!std::isfinite(v))
                    {
                        std::cerr<<"edge sweep non-finite fs="<<fs<<" character="<<c<<" drive="<<d<<"\n";
                        return 30;
                    }
                    energy+=v*v;
                }
                if(!(energy>0.0) || !std::isfinite(energy))
                {
                    std::cerr<<"edge sweep invalid energy fs="<<fs<<" character="<<c<<" drive="<<d<<"\n";
                    return 31;
                }
            }
        }
    }

    std::cout<<"PASS: V2 release matrix sample-rates, block segmentation, automation and edge sweep\n";
    return 0;
}
