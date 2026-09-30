#include "../SMX3Common/DSP/Smx3V1Reference.h"
#include <algorithm>
#include <cmath>
#include <iostream>
#include <vector>

using SaturatorMixFX::V1Reference::Core;

static double rms(const std::vector<double>& v)
{
    double s=0.0;
    for(double x:v) s+=x*x;
    return std::sqrt(s/std::max<std::size_t>(1,v.size()));
}
static double db(double g){return 20.0*std::log10(std::max(g,1e-15));}

int main()
{
    constexpr double fs=48000.0;
    constexpr int N=48000;
    const double levelsDb[]={-36.0,-30.0,-24.0,-18.0,-12.0,-6.0};
    const double drives[]={0.0,.25,.50,.75,1.0};
    const double chars[]={0.0,.5,1.0};
    const char* names[]={"TRIODE","PENTODE","IRON"};

    for(int m=0;m<3;++m)
    {
        for(double inDb:levelsDb)
        {
            const double amp=std::pow(10.0,inDb/20.0);
            std::vector<double> input(N);
            for(int n=0;n<N;++n)
            {
                const double t=n/fs;
                input[n]=amp*(.67*std::sin(2.0*3.14159265358979323846*83.0*t)
                            +.23*std::sin(2.0*3.14159265358979323846*997.0*t+.3)
                            +.10*std::sin(2.0*3.14159265358979323846*6113.0*t+.8));
            }
            const double inR=rms(input);
            for(double d:drives)
            {
                Core core;
                Core::ChannelState st{};
                core.prepare(fs);
                Core::Params p{d,chars[m],1.0,.75};
                std::vector<double> out(N);
                for(int n=0;n<N;++n)
                    out[n]=core.processSampleV2Iron(input[n],st,p);
                const double delta=db(rms(out)/inR);
                std::cout<<names[m]<<",input_dBFS="<<inDb<<",drive_pct="<<(int)std::lround(d*100.0)
                         <<",level_delta_dB="<<delta<<"\n";
                if(!std::isfinite(delta)) return 2;
            }
        }
    }
    std::cout<<"PASS: V2 input-level drive matrix\n";
    return 0;
}
