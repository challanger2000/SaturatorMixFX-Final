#include "../SMX3Common/DSP/Smx3V1Reference.h"
#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

using SaturatorMixFX::V1Reference::Core;
static constexpr double pi=3.14159265358979323846;
static constexpr double fs=48000.0;

static double rms(const std::vector<double>& x,int start=0)
{
    long double s=0.0;
    for(std::size_t i=static_cast<std::size_t>(start);i<x.size();++i) s+=x[i]*x[i];
    const auto n=x.size()-static_cast<std::size_t>(start);
    return std::sqrt(static_cast<double>(s/std::max<std::size_t>(1,n)));
}

static std::vector<double> programme(const std::string& kind,int n)
{
    std::vector<double> y(static_cast<std::size_t>(n),0.0);
    if(kind=="bass")
    {
        const double notes[]={55.0,65.406,73.416,82.407};
        for(int i=0;i<n;++i)
        {
            const double t=i/fs;
            const double f=notes[(i/6000)%4];
            const double ph=2*pi*f*t;
            y[i]=.55*std::sin(ph)+.17*std::sin(2*ph)+.08*std::sin(3*ph);
        }
    }
    else if(kind=="drums")
    {
        for(int hit=0;hit<8;++hit)
        {
            const int start=1200+hit*5400;
            for(int i=start;i<std::min(n,start+6000);++i)
            {
                const double t=(i-start)/fs;
                const double kick=.72*std::sin(2*pi*(55.0+38.0*std::exp(-32*t))*t)*std::exp(-24*t);
                const double bright=(hit&1)?.26*(std::sin(2*pi*190*t)+.5*std::sin(2*pi*2600*t)+.25*std::sin(2*pi*7200*t))*std::exp(-38*t):0.0;
                y[i]+=kick+bright;
            }
        }
    }
    else
    {
        const double f[]={82.407,123.471,164.814,246.942,329.628};
        for(int i=0;i<n;++i)
        {
            const double t=i/fs;
            double v=0.0;
            for(int k=0;k<5;++k) v+=(.19/(1.0+.42*k))*std::sin(2*pi*f[k]*t+.17*k);
            const double p=std::fmod(t,.125);
            const double env=.58+.42*std::min(1.0,p/.012);
            y[i]=env*v;
        }
    }
    return y;
}

static void measure(const std::string& material,double character,double drive)
{
    constexpr int N=48000;
    constexpr int warm=4096;
    Core wetCore, dryCore;
    wetCore.prepare(fs);
    dryCore.prepare(fs);
    Core::ChannelState wetState{}, dryState{};
    Core::Params wetParams{drive,character,1.0,0.75};
    Core::Params dryParams{drive,character,0.0,0.75};

    auto x=programme(material,N);
    std::vector<double> yWet(N), yDry(N);
    for(int i=0;i<N;++i)
    {
        yWet[i]=wetCore.processSampleV2Iron(x[i],wetState,wetParams);
        yDry[i]=dryCore.processSampleV2Iron(x[i],dryState,dryParams);
    }

    // Wet and dry use the same oversampling/reconstruction topology, so this
    // comparison isolates inserted hardware character instead of measuring
    // the common filter delay against the raw source.
    long double dd=0.0,ww=0.0;
    for(int i=warm;i<N;++i)
    {
        dd+=yDry[i]*yDry[i];
        ww+=yWet[i]*yWet[i];
    }
    const double match=std::sqrt(static_cast<double>(dd/std::max<long double>(ww,1e-30L)));

    long double er=0.0,ref=0.0;
    double pk=0.0;
    for(int i=warm;i<N;++i)
    {
        const double e=match*yWet[i]-yDry[i];
        er+=e*e;
        ref+=yDry[i]*yDry[i];
        pk=std::max(pk,std::abs(e));
    }
    const double residual=20*std::log10(std::max(std::sqrt(static_cast<double>(er/ref)),1e-30));
    const double levelDelta=20*std::log10(std::max(rms(yWet,warm)/rms(yDry,warm),1e-30));
    const int bestLag=0;
    const char* mode=character<.25?"TRIODE":(character<.75?"PENTODE":"IRON");
    std::cout<<std::fixed<<std::setprecision(3)
             <<material<<","<<mode
             <<",drive_pct="<<static_cast<int>(std::lround(drive*100.0))
             <<",lag="<<bestLag
             <<",level_delta_dB="<<levelDelta
             <<",matched_residual_dBc="<<residual
             <<",matched_peak_delta="<<pk<<"\n";
}

int main()
{
    std::cout<<"material,mode,drive,metrics\n";
    for(const char* m:{"drums","bass","guitar"})
        for(double c:{0.0,.5,1.0})
            for(double d:{0.0,.25,.50,.75,1.0})
                measure(m,c,d);
    std::cout<<"PASS: hardware-character drive sweep completed\n";
    return 0;
}
