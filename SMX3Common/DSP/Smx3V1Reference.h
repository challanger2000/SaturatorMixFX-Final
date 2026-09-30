#pragma once

// SMX-3 V1 reference DSP extracted for V2 refactor validation.
//
// IMPORTANT:
// - This file intentionally reproduces the V1 DSP algorithm.
// - Do not "improve" constants or signal flow here.
// - It is a structural reference used to prove Channel/MixFX equivalence
//   before physical V2 engines replace the legacy algorithms.
// - No VST3 or host API dependency.

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>

namespace SaturatorMixFX {
namespace V1Reference {

class Core
{
public:
    static constexpr int kOversample = 4;
    static constexpr int kOversampleSections = 8;

    struct BiquadState { double z1=0.0, z2=0.0; };
    struct BiquadCoeffs { double b0=1.0, b1=0.0, b2=0.0, a1=0.0, a2=0.0; };

    struct ChannelState
    {
        double previousInput=0.0, ironMemory=0.0, dcX1=0.0, dcY1=0.0;
        double lowBand=0.0, highSmooth=0.0;
        double envFast=0.0, envSlow=0.0;
        double triodeCharge=0.0, pentodeCharge=0.0, ironFlux=0.0;
        // V2 physical IRON magnetic states. These are deliberately separate
        // from the legacy V1 ironMemory/ironFlux states so processSample()
        // remains a frozen V1 reference.
        double ironV2H=0.0, ironV2M=0.0, ironV2Relax=0.0;
        std::array<BiquadState,kOversampleSections> osUp{};
        std::array<BiquadState,kOversampleSections> osDown{};
        std::array<BiquadState,kOversampleSections> ironV2Up{};
        std::array<BiquadState,kOversampleSections> cleanUp{};
        std::array<BiquadState,kOversampleSections> cleanDown{};
    };

    struct Params
    {
        double drive=0.30;
        double character=0.0;
        double mix=1.0;
        double output=0.75;
    };

    void prepare(double sampleRate)
    {
        sampleRate_ = sampleRate > 1.0 ? sampleRate : 44100.0;
        const double internalRate = sampleRate_ * kOversample;

        ironMemoryCoeff_ = std::exp(-2.0 * kPi * 95.0 / internalRate);
        triodeChargeCoeff_ = std::exp(-1.0 / (0.030 * internalRate));
        pentodeChargeCoeff_ = std::exp(-1.0 / (0.055 * internalRate));
        ironFluxCoeff_ = std::exp(-1.0 / (0.085 * internalRate));
        dcCoeff_ = std::exp(-2.0 * kPi * 18.0 / sampleRate_);
        lowCoeff_ = std::exp(-2.0 * kPi * 145.0 / sampleRate_);
        highCoeff_ = std::exp(-2.0 * kPi * 6200.0 / sampleRate_);
        envFastCoeff_ = std::exp(-1.0 / (0.0015 * sampleRate_));
        envSlowCoeff_ = std::exp(-1.0 / (0.035 * sampleRate_));
        designOversamplingFilters();
    }

    void reset(ChannelState& s) const { s = {}; }

    double processSample(double x, ChannelState& s, const Params& params) const
    {
        const double pos = clamp01(params.character) * 2.0;
        const double wT = std::max(0.0, 1.0 - pos);
        const double wI = std::max(0.0, pos - 1.0);
        const double wP = 1.0 - wT - wI;

        const double effectiveDrive = shapeDrive(params.drive);
        const double driveDb = 24.0 * effectiveDrive;
        const double inputGain = dbToGain(driveDb);
        const double wet = clamp01(params.mix);
        const double dry = 1.0 - wet;
        const double outGain = dbToGain(-18.0 + 24.0 * clamp01(params.output));

        const double trim = (-9.50*wT - 19.00*wP - 14.47*wI) * effectiveDrive;
        const double baseComp = (-.46*wT - .52*wP - .40*wI) * driveDb;
        const double polishTrimDb = (.73*wT + 2.67*wP - .06*wI) * effectiveDrive;
        const double smoothTrimDb = characterTrimDb(effectiveDrive,wT,wP,wI);
        const double driveLevelComp =
            hardwareDriveLevelCompDb(clamp01(params.drive),wT,wP,wI);
        const double comp = dbToGain(
            trim + baseComp + polishTrimDb + smoothTrimDb + driveLevelComp);

        const double protect = .18*wT + .42*wP + .30*wI;
        const double attackAmount = .08*wT + .22*wP + .15*wI;

        s.lowBand = lowCoeff_*s.lowBand + (1.0-lowCoeff_)*x;
        s.highSmooth = highCoeff_*s.highSmooth + (1.0-highCoeff_)*x;
        const double low = s.lowBand;
        const double high = x - s.highSmooth;
        const double mid = x - low - high;

        const double triCol = .94*low + 1.09*mid + .84*high;
        const double penCol = .84*low + 1.10*mid + 1.07*high;
        const double ironCol = 1.13*low + 1.025*mid + .80*high;
        const double coloured = wT*triCol + wP*penCol + wI*ironCol;

        const double a = std::abs(x);
        s.envFast = envFastCoeff_*s.envFast + (1.0-envFastCoeff_)*a;
        s.envSlow = envSlowCoeff_*s.envSlow + (1.0-envSlowCoeff_)*a;
        const double transient = std::max(0.0,s.envFast-s.envSlow);
        const double normTransient = clamp01(transient/(.06+s.envSlow));
        const double dynamicGain = inputGain*(1.0-protect*normTransient);

        double processedOs=0.0;
        double cleanOs=0.0;
        for(int os=0;os<kOversample;++os)
        {
            const double stuffed=(os==0)?(coloured*static_cast<double>(kOversample)):0.0;
            const double cleanStuffed=(os==0)?(x*static_cast<double>(kOversample)):0.0;
            const double up=runOversamplingFilter(stuffed,s.osUp);
            const double cleanUp=runOversamplingFilter(cleanStuffed,s.cleanUp);
            const double nlT=shapeTriode(up*dynamicGain,s);
            const double nlP=shapePentode(up*dynamicGain,s);
            const double nlI=shapeIron(up*dynamicGain,s);
            const double nl=wT*nlT+wP*nlP+wI*nlI;
            const double filtered=runOversamplingFilter(nl,s.osDown);
            const double cleanFiltered=runOversamplingFilter(cleanUp,s.cleanDown);
            if(os==kOversample-1)
            {
                processedOs=filtered;
                cleanOs=cleanFiltered;
            }
        }

        double processed=processedOs*comp;
        const double attackBlend=normTransient*attackAmount;
        processed=processed*(1.0-attackBlend)+cleanOs*attackBlend;
        processed=peakProtect(processed);
        processed=dcBlock(processed,s);

        // Hardware-mode policy: Drive=0 means minimum excitation, not that
        // the selected hardware path disappears. Bypass is the only truly
        // neutral state. The 12% floor is provisional and must be verified
        // against level-matched programme-material measurements.
        constexpr double kHardwareFloor=.12;
        const double hardwareAmount=kHardwareFloor+(1.0-kHardwareFloor)*effectiveDrive;
        const double wetSignal=cleanOs+hardwareAmount*(processed-cleanOs);
        const double mixed=dry*cleanOs+wet*wetSignal;
        return mixed*outGain;
    }


    // V2 production candidate:
    // - preserves the established outer SMX-3 gain/colour/transient/mix flow;
    // - replaces only the IRON nonlinear branch with the frozen unified
    //   Jiles-Atherton + one-state relaxation model;
    // - advances the magnetic model once per host sample with midpoint/RK2.
    //
    // Evidence for 1x RK2 is in tools/smx3_v2_iron_practical_program_benchmark.py.
    double processSampleV2Iron(double x, ChannelState& s, const Params& params) const
    {
        const double pos = clamp01(params.character) * 2.0;
        const double wT = std::max(0.0, 1.0 - pos);
        const double wI = std::max(0.0, pos - 1.0);
        const double wP = 1.0 - wT - wI;

        const double effectiveDrive = shapeDrive(params.drive);
        const double driveDb = 24.0 * effectiveDrive;
        const double inputGain = dbToGain(driveDb);
        const double wet = clamp01(params.mix);
        const double dry = 1.0 - wet;
        const double outGain = dbToGain(-18.0 + 24.0 * clamp01(params.output));

        const double trim = (-9.50*wT - 19.00*wP - 14.47*wI) * effectiveDrive;
        const double baseComp = (-.46*wT - .52*wP - .40*wI) * driveDb;
        const double polishTrimDb = (.73*wT + 2.67*wP - .06*wI) * effectiveDrive;
        const double smoothTrimDb = characterTrimDb(effectiveDrive,wT,wP,wI);
        const double driveLevelComp =
            hardwareDriveLevelCompDb(clamp01(params.drive),wT,wP,wI);
        const double comp = dbToGain(
            trim + baseComp + polishTrimDb + smoothTrimDb + driveLevelComp);

        const double protect = .18*wT + .42*wP + .30*wI;
        const double attackAmount = .08*wT + .22*wP + .15*wI;

        s.lowBand = lowCoeff_*s.lowBand + (1.0-lowCoeff_)*x;
        s.highSmooth = highCoeff_*s.highSmooth + (1.0-highCoeff_)*x;
        const double low = s.lowBand;
        const double high = x - s.highSmooth;
        const double mid = x - low - high;

        const double triCol = .94*low + 1.09*mid + .84*high;
        const double penCol = .84*low + 1.10*mid + 1.07*high;
        const double ironCol = 1.13*low + 1.025*mid + .80*high;
        const double coloured = wT*triCol + wP*penCol + wI*ironCol;

        const double a = std::abs(x);
        s.envFast = envFastCoeff_*s.envFast + (1.0-envFastCoeff_)*a;
        s.envSlow = envSlowCoeff_*s.envSlow + (1.0-envSlowCoeff_)*a;
        const double transient = std::max(0.0,s.envFast-s.envSlow);
        const double normTransient = clamp01(transient/(.06+s.envSlow));
        const double dynamicGain = inputGain*(1.0-protect*normTransient);

        // The physical magnetic solve stays at host rate. Its output is then
        // passed through the same oversampling input filter topology as the
        // TRI/PENT branches, but without re-running the magnetic solver at 4x.
        // This preserves practical 1x RK2 cost while aligning phase/latency
        // before the shared downsampling filter.
        const double ironHost = shapeIronV2(ironCol*dynamicGain,s);

        double processedOs=0.0;
        double cleanOs=0.0;
        for(int os=0;os<kOversample;++os)
        {
            const double stuffed=(os==0)?(coloured*static_cast<double>(kOversample)):0.0;
            const double ironStuffed=(os==0)?(ironHost*static_cast<double>(kOversample)):0.0;
            const double cleanStuffed=(os==0)?(x*static_cast<double>(kOversample)):0.0;
            const double up=runOversamplingFilter(stuffed,s.osUp);
            const double ironUp=runOversamplingFilter(ironStuffed,s.ironV2Up);
            const double cleanUp=runOversamplingFilter(cleanStuffed,s.cleanUp);
            const double nlT=shapeTriode(up*dynamicGain,s);
            const double nlP=shapePentode(up*dynamicGain,s);
            const double nl=wT*nlT+wP*nlP+wI*ironUp;
            const double filtered=runOversamplingFilter(nl,s.osDown);
            const double cleanFiltered=runOversamplingFilter(cleanUp,s.cleanDown);
            if(os==kOversample-1)
            {
                processedOs=filtered;
                cleanOs=cleanFiltered;
            }
        }

        double processed=processedOs*comp;
        const double attackBlend=normTransient*attackAmount;
        processed=processed*(1.0-attackBlend)+cleanOs*attackBlend;
        processed=peakProtect(processed);
        processed=dcBlock(processed,s);

        // Hardware is already present at minimum Drive. Drive increases
        // excitation/intensity; only bypass is truly neutral.
        // Provisional floor: verify against level-matched programme material.
        constexpr double kHardwareFloor=.12;
        const double hardwareAmount=
            kHardwareFloor+(1.0-kHardwareFloor)*effectiveDrive;
        const double wetSignal=
            cleanOs+hardwareAmount*(processed-cleanOs);
        const double mixed=dry*cleanOs+wet*wetSignal;
        return mixed*outGain;
    }

private:
    static constexpr double kPi=3.14159265358979323846;

    static double clamp01(double v)
    {
        return std::max(0.0,std::min(1.0,v));
    }

    static double dbToGain(double d)
    {
        return std::pow(10.0,d/20.0);
    }

    static double peakProtect(double x)
    {
        constexpr double threshold=.94;
        constexpr double headroom=1.0-threshold;
        const double a=std::abs(x);
        if(a<=threshold)
            return x;
        const double y=threshold+headroom*std::tanh((a-threshold)/headroom);
        return std::copysign(y,x);
    }

    static double shapeDrive(double d)
    {
        d=clamp01(d);
        if(d<=0.0) return 0.0;
        if(d>=1.0) return 1.0;
        constexpr double exponent=1.3012419807039308;
        constexpr double balance=0.7747292343480475;
        const double a=std::pow(d,exponent);
        const double b=balance*std::pow(1.0-d,exponent);
        return a/(a+b);
    }

    static double smootherStep(double d)
    {
        d=clamp01(d);
        return d*d*d*(10.0-15.0*d+6.0*d*d);
    }

    static double hardwareDriveLevelCompDb(
        double drive,double wT,double wP,double wI)
    {
        // Programme-material calibration at 48 kHz. The anchors compensate
        // the measured mean level loss while preserving the nonlinear shape.
        // Interpolate smoothly to avoid audible gain kinks while automating.
        static constexpr double x[5]={0.0,.25,.50,.75,1.0};
        static constexpr double tri[5]={0.0,.78,5.30,10.01,12.80};
        static constexpr double pen[5]={0.0,1.47,5.90,8.77,11.93};
        static constexpr double iron[5]={0.0,.33,.69,1.75,3.06};

        drive=clamp01(drive);
        int seg=0;
        while(seg<3 && drive>x[seg+1]) ++seg;
        const double span=x[seg+1]-x[seg];
        const double u=span>0.0?(drive-x[seg])/span:0.0;
        const double s=u*u*(3.0-2.0*u);
        const auto interp=[&](const double* a){
            return a[seg]+(a[seg+1]-a[seg])*s;
        };
        return wT*interp(tri)+wP*interp(pen)+wI*interp(iron);
    }

    static double characterTrimDb(double effectiveDrive,double wT,double wP,double wI)
    {
        (void)wI;
        const double s=smootherStep(effectiveDrive);
        const double s2=s*s;
        const double s3=s2*s;
        const double s4=s3*s;
        const double tri =
            4.522567512112715*s
            -34.02706594845086*s2
            +41.02777776056358*s3
            -14.887942224225434*s4;
        const double pent =
            5.165025880904459*s
            -45.37422422361783*s2
            +91.75665840452228*s3
            -47.421638161808914*s4;
        return wT*tri+wP*pent;
    }

    void designOversamplingFilters()
    {
        const double internalRate=sampleRate_*kOversample;
        const double cutoff=.485*sampleRate_;
        const double w0=2.0*kPi*cutoff/internalRate;
        const double cw=std::cos(w0);
        const double sw=std::sin(w0);
        constexpr int order=2*kOversampleSections;

        for(int section=0;section<kOversampleSections;++section)
        {
            const double angle=(2.0*(section+1)-1.0)*kPi/(2.0*order);
            const double q=1.0/(2.0*std::cos(angle));
            const double alpha=sw/(2.0*q);
            const double a0=1.0+alpha;
            auto& c=osCoeffs_[static_cast<std::size_t>(section)];
            c.b0=((1.0-cw)*.5)/a0;
            c.b1=(1.0-cw)/a0;
            c.b2=c.b0;
            c.a1=(-2.0*cw)/a0;
            c.a2=(1.0-alpha)/a0;
        }
    }

    double runOversamplingFilter(double x,std::array<BiquadState,kOversampleSections>& state) const
    {
        double y=x;
        for(int i=0;i<kOversampleSections;++i)
        {
            const auto& c=osCoeffs_[static_cast<std::size_t>(i)];
            auto& s=state[static_cast<std::size_t>(i)];
            const double out=c.b0*y+s.z1;
            s.z1=c.b1*y-c.a1*out+s.z2;
            s.z2=c.b2*y-c.a2*out;
            y=out;
        }
        return y;
    }

    double shapeTriode(double x,ChannelState& s) const
    {
        const double a=std::abs(x);
        s.triodeCharge=triodeChargeCoeff_*s.triodeCharge+(1.0-triodeChargeCoeff_)*a;
        const double charge=s.triodeCharge/(.35+s.triodeCharge);
        const double sag=1.0-.055*charge;
        const double bias=.225+.034*charge;
        const double xs=x*sag;
        const double p=std::tanh(1.16*xs+bias)-std::tanh(bias);
        const double n=std::tanh(.89*xs-.52*bias)+std::tanh(.52*bias);
        double y=.655*p+.345*n;
        const double even=xs*xs/(1.0+1.65*a);
        y+=.086*even;
        return y;
    }

    double shapePentode(double x,ChannelState& s) const
    {
        const double a=std::abs(x);
        s.pentodeCharge=pentodeChargeCoeff_*s.pentodeCharge+(1.0-pentodeChargeCoeff_)*a;
        const double charge=s.pentodeCharge/(.30+s.pentodeCharge);
        const double screenSag=1.0-.070*charge;
        const double xs=x*screenSag;
        const double oddCore=.44*std::tanh((1.34+.11*charge)*xs);
        const double oddEdge=.205*std::tanh((2.28+.23*charge)*xs);
        const double open=.145*std::atan(1.82*xs)*(2.0/kPi);
        const double quasiLinear=.21*xs/(1.0+.17*std::abs(xs));
        return oddCore+oddEdge+open+quasiLinear;
    }

    double shapeIron(double x,ChannelState& s) const
    {
        s.ironMemory=ironMemoryCoeff_*s.ironMemory+(1.0-ironMemoryCoeff_)*x;
        s.ironFlux=ironFluxCoeff_*s.ironFlux+(1.0-ironFluxCoeff_)*std::abs(x);
        const double fluxAmount=s.ironFlux/(.28+s.ironFlux);
        const double m=s.ironMemory;
        const double f=x+(.255+.045*fluxAmount)*m;
        const double core=(.555-.020*fluxAmount)*std::tanh((1.08+.10*fluxAmount)*f);
        const double soft=.305*f/(1.0+(.285+.055*fluxAmount)*std::abs(f));
        const double linear=(.125+.018*(1.0-fluxAmount))*f;
        const double hysteretic=(.052+.014*fluxAmount)*m*std::abs(m);
        return core+soft+linear+hysteretic;
    }


    struct IronV2Deriv
    {
        double h=0.0, m=0.0, i=0.0, vout=0.0;
    };

    static double ironV2Langevin(double x)
    {
        const double ax=std::abs(x);
        if(ax<1.0e-4)
            return x/3.0;
        return 1.0/std::tanh(x)-1.0/x;
    }

    static double ironV2LangevinD(double x)
    {
        const double ax=std::abs(x);
        if(ax<1.0e-4)
            return 1.0/3.0;
        if(ax>20.0)
            return 1.0/(x*x);
        const double sh=std::sinh(x);
        return 1.0/(x*x)-1.0/(sh*sh);
    }

    static double ironV2Dmdh(double H,double M,double direction)
    {
        constexpr double a=14.1;
        constexpr double alpha=5.0e-5;
        constexpr double k=17.8;
        constexpr double ms=2.75e5;
        constexpr double c=.535351563;

        const double q=(H+alpha*M)/a;
        const double man=ms*ironV2Langevin(q);
        const double ld=ironV2LangevinD(q);
        const double delta=direction>=0.0?1.0:-1.0;
        const double dm=man-M;
        const double deltaM=(delta*dm>=0.0)?1.0:0.0;

        double den=(1.0-c)*delta*k-alpha*dm;
        if(std::abs(den)<1.0e-12)
            den=std::copysign(1.0e-12,den!=0.0?den:delta);

        const double irreversible=(1.0-c)*deltaM*dm/den;
        const double reversible=c*ms/a*ld;
        double yden=1.0-alpha*reversible;
        if(std::abs(yden)<1.0e-12)
            yden=std::copysign(1.0e-12,yden!=0.0?yden:1.0);

        return (irreversible+reversible)/yden;
    }

    static IronV2Deriv ironV2Deriv(double H,double M,double irel,double vs)
    {
        constexpr double rSource=600.0;
        constexpr double rPrimary=1450.0;
        constexpr double rSecondary=1550.0;
        constexpr double rLoad=10000.0;
        constexpr double rTotalLoad=rSecondary+rLoad;
        constexpr double kI=1087366.676330566;
        constexpr double kPhi=2.85816455767e-7;
        constexpr double gRelax=2.73374681419e-6;
        constexpr double tau=1.440238371e-3;

        const double rSeries=rSource+rPrimary;
        const double vnode=(vs-rSeries*(H/kI+irel))/(1.0+rSeries/rTotalLoad);
        const double direction=vnode>=0.0?1.0:-1.0;
        const double slope=ironV2Dmdh(H,M,direction);

        double slopeDen=1.0+slope;
        if(std::abs(slopeDen)<1.0e-12)
            slopeDen=std::copysign(1.0e-12,slopeDen!=0.0?slopeDen:1.0);

        IronV2Deriv d;
        d.h=vnode/(kPhi*slopeDen);
        d.m=slope*d.h;
        d.i=(gRelax*vnode-irel)/tau;
        d.vout=vnode*rLoad/rTotalLoad;
        return d;
    }

    double shapeIronV2(double x,ChannelState& s) const
    {
        // +20 dBu RMS is mapped to digital full-scale peak. This gives the
        // physical core a practical studio operating reference while the
        // existing Drive control determines how hard it is pushed.
        constexpr double voltsPerUnit=10.947178455;
        constexpr double midbandGain=.7692385064990691;

        if(!std::isfinite(x))
        {
            s.ironV2H=s.ironV2M=s.ironV2Relax=0.0;
            return 0.0;
        }

        const double xin=std::max(-64.0,std::min(64.0,x));
        const double vs=xin*voltsPerUnit;
        const double dt=1.0/sampleRate_;

        const IronV2Deriv k1=ironV2Deriv(s.ironV2H,s.ironV2M,s.ironV2Relax,vs);
        const IronV2Deriv k2=ironV2Deriv(
            s.ironV2H+.5*dt*k1.h,
            s.ironV2M+.5*dt*k1.m,
            s.ironV2Relax+.5*dt*k1.i,
            vs);

        const double h2=s.ironV2H+dt*k2.h;
        const double m2=s.ironV2M+dt*k2.m;
        const double i2=s.ironV2Relax+dt*k2.i;

        if(!std::isfinite(h2)||!std::isfinite(m2)||!std::isfinite(i2))
        {
            s.ironV2H=s.ironV2M=s.ironV2Relax=0.0;
            return xin;
        }

        s.ironV2H=h2;
        s.ironV2M=m2;
        s.ironV2Relax=i2;

        const IronV2Deriv out=ironV2Deriv(h2,m2,i2,vs);
        const double y=out.vout/(voltsPerUnit*midbandGain);
        return std::isfinite(y)?y:xin;
    }

    double dcBlock(double x,ChannelState& s) const
    {
        const double y=x-s.dcX1+dcCoeff_*s.dcY1;
        s.dcX1=x;
        s.dcY1=y;
        return y;
    }

    double sampleRate_=44100.0;
    double ironMemoryCoeff_=0.0;
    double dcCoeff_=0.995;
    double lowCoeff_=0.0;
    double highCoeff_=0.0;
    double envFastCoeff_=0.0;
    double envSlowCoeff_=0.0;
    double triodeChargeCoeff_=0.0;
    double pentodeChargeCoeff_=0.0;
    double ironFluxCoeff_=0.0;
    std::array<BiquadCoeffs,kOversampleSections> osCoeffs_{};
};

} // namespace V1Reference
} // namespace SaturatorMixFX
