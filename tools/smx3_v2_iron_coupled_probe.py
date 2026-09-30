#!/usr/bin/env python3
"""Coupled electrical/magnetic IRON research model for SMX-3 V2.

Purpose:
- couple a Jiles-Atherton magnetic core to the derived JT-11P-1 electrical skeleton;
- calibrate geometry scaling to preserve the derived small-signal Lm;
- demonstrate whether the DAFx example hysteresis SHAPE can match Jensen's
  nonlinear anchors after scaling.

This is a research rejection/probing tool, NOT production DSP.

Standard library only.
"""

import math
import cmath

# Electrical skeleton
RSOURCE = 600.0
RP = 1450.0
RSEC = 1550.0
RL = 10000.0
RLOAD = RSEC + RL
LM_TARGET = 106.554

# DAFx-2016 example Jiles-Atherton shape parameters.
P = {"a":14.1, "alpha":5.0e-5, "c":0.55, "k":17.8, "Ms":2.75e5}

# Empirically selected field/current scale that makes the coupled model land
# near 1% THD at Jensen's +20 dBu / 20 Hz anchor. It is NOT a hardware value.
KI = 41431.06


def langevin(x):
    ax=abs(x)
    if ax<1e-4:
        return x/3.0
    return 1.0/math.tanh(x)-1.0/x


def langevin_d(x):
    ax=abs(x)
    if ax<1e-4:
        return 1.0/3.0
    s=math.sinh(x)
    return 1.0/(x*x)-1.0/(s*s)


def dmdh(H,M,direction):
    a=P["a"]; alpha=P["alpha"]; c=P["c"]; k=P["k"]; Ms=P["Ms"]
    q=(H+alpha*M)/a
    Man=Ms*langevin(q)
    Ld=langevin_d(q)
    delta=1.0 if direction>=0 else -1.0
    dm=Man-M
    delta_m=1.0 if delta*dm>=0 else 0.0
    den=(1.0-c)*delta*k-alpha*dm
    if abs(den)<1e-12:
        den=math.copysign(1e-12,den if den else delta)
    irreversible=(1.0-c)*delta_m*dm/den
    reversible_coeff=c*Ms/a*Ld
    yden=1.0-alpha*reversible_coeff
    if abs(yden)<1e-12:
        yden=math.copysign(1e-12,yden if yden else 1.0)
    return (irreversible+reversible_coeff)/yden


SLOPE0=dmdh(0.0,0.0,1.0)
# lambda = KPHI*(H+M), H=KI*i_m.
# Therefore Lm = d(lambda)/d(i_m) = KPHI*KI*(1+dM/dH).
KPHI=LM_TARGET/(KI*(1.0+SLOPE0))


def deriv(t,H,M,amp,freq):
    vs=amp*math.sin(2.0*math.pi*freq*t)
    rseries=RSOURCE+RP
    divider=1.0+rseries/RLOAD

    numerator=vs-rseries*H/KI
    direction=1.0 if numerator>=0.0 else -1.0
    slope=dmdh(H,M,direction)

    vnode=numerator/divider
    dH=vnode/(KPHI*(1.0+slope))
    dM=slope*dH
    vout=vnode*RL/RLOAD
    return dH,dM,vout


def simulate(level_dbu,freq=20.0,fs=96000.0,cycles=8,warmup_cycles=40):
    vrms=0.775*10.0**(level_dbu/20.0)
    amp=vrms*math.sqrt(2.0)
    total_cycles=warmup_cycles+cycles
    n=int(round(total_cycles*fs/freq))
    H=0.0; M=0.0
    out=[0.0]*n
    dt=1.0/fs

    for i in range(n):
        t=i*dt
        k1h,k1m,v1=deriv(t,H,M,amp,freq)
        k2h,k2m,_=deriv(t+0.5*dt,H+0.5*dt*k1h,M+0.5*dt*k1m,amp,freq)
        k3h,k3m,_=deriv(t+0.5*dt,H+0.5*dt*k2h,M+0.5*dt*k2m,amp,freq)
        k4h,k4m,_=deriv(t+dt,H+dt*k3h,M+dt*k3m,amp,freq)
        H += dt*(k1h+2*k2h+2*k3h+k4h)/6.0
        M += dt*(k1m+2*k2m+2*k3m+k4m)/6.0
        out[i]=v1

    # Harmonic projection on the final four complete cycles after magnetic
    # periodic-state warmup; avoids treating startup/remanence settling as H2.
    samples_per_cycle=int(round(fs/freq))
    start=n-4*samples_per_cycle
    y=out[start:]
    N=len(y)

    def component(h):
        re=0.0; im=0.0
        for j,val in enumerate(y):
            a=2.0*math.pi*h*freq*j/fs
            re += val*math.cos(a)
            im -= val*math.sin(a)
        return math.hypot(re,im)

    fundamental=component(1)
    harmonics=[component(h)/fundamental for h in range(2,11)]
    powers=sum(h*h for h in harmonics)
    thd=math.sqrt(powers)

    rms=math.sqrt(sum(v*v for v in y)/N)
    return thd,rms,harmonics


def main():
    print("SMX-3 V2 coupled IRON probe")
    print("DAFx Jiles-Atherton example shape; scaled to Jensen high-level anchor.")
    print("Each measurement includes 40 magnetic warm-up cycles before analysis.")
    print(f"KI={KI:.6f} A/m per A")
    print(f"KPHI={KPHI:.12g} Wb-turn per (A/m)")
    print(f"small-signal Lm target={LM_TARGET:.6f} H")
    print()
    print("20 Hz level sweep")
    print("level_dBu,THD_percent,H2_percent,H3_percent,H5_percent,H2_over_H3_dB,output_rms_V")
    results={}
    for level in (4.0,14.0,20.0):
        thd,rms,hs=simulate(level,20.0)
        h2=hs[0] if len(hs)>0 else 0.0
        h3=hs[1] if len(hs)>1 else 0.0
        h5=hs[3] if len(hs)>3 else 0.0
        ratio_db=20.0*math.log10(max(h2,1e-30)/max(h3,1e-30))
        results[level]=(thd,rms,hs)
        print(
            f"{level:.1f},{100.0*thd:.9f},{100.0*h2:.9f},"
            f"{100.0*h3:.9f},{100.0*h5:.9f},{ratio_db:.9f},{rms:.9f}"
        )

    print()
    print("+20 dBu frequency sweep")
    print("frequency_Hz,THD_percent")
    for freq in (20.0,30.0,50.0,100.0,1000.0):
        thd,_,_=simulate(20.0,freq)
        print(f"{freq:.1f},{100.0*thd:.9f}")

    hi=100.0*results[20.0][0]
    lo=100.0*results[4.0][0]
    print()
    print(f"Jensen target +20 dBu/20Hz: ~1.0% THD; model={hi:.6f}%")
    print(f"Jensen target +4 dBu/20Hz: ~0.025% THD; model={lo:.6f}%")

    if not (0.8 <= hi <= 1.2):
        raise SystemExit("FAIL: scaling no longer reproduces the intended high-level probe anchor")

    # This failure criterion is intentional: it protects the research conclusion
    # that simple geometric scaling of the example JA loop is insufficient.
    if lo <= 0.05:
        raise SystemExit("UNEXPECTED: example JA shape now approaches Jensen low-level target; re-evaluate decision log")

    print("REJECT AS JENSEN FIT: high-level match does not reproduce low-level distortion shape.")


if __name__=="__main__":
    main()
