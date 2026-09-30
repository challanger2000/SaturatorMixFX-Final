#!/usr/bin/env python3
"""Large-signal probe for the provisional ECC83 Mullard-table fit.

Tests Mullard's documented 250 V / 100 kOhm / 1.5 kOhm operating condition
at the start of positive grid current.

The provisional plate-law fit is intentionally challenged out-of-fit here.
Standard library only.
"""

import cmath
import math

P = {
    "G": 2.18714303e-3,
    "mu": 105.447663,
    "gamma": 1.07136184,
    "C": 2.60122984,
    "Gg": 3.263e-4,
    "xi": 1.156,
    "Cg": 11.99,
    "Ig0": 3.917e-8,
}

VB = 250.0
RA = 100000.0
RK = 1500.0
RLOAD = 330000.0
RAC = 1.0/(1.0/RA + 1.0/RLOAD)
IG_ONSET = 0.3e-6

TARGET_VRMS = 26.0
TARGET_THD = 0.039


def softplus_scaled(x,c):
    z=c*x
    if z>50.0:
        return x
    if z<-50.0:
        return math.exp(z)/c
    return math.log1p(math.exp(z))/c


def currents(va,vg):
    ik=P["G"]*softplus_scaled(va/P["mu"]+vg,P["C"])**P["gamma"]
    ig=P["Gg"]*softplus_scaled(vg,P["Cg"])**P["xi"]+P["Ig0"]
    return ik-ig,ik,ig


def solve_bias():
    vk=1.2
    vp=165.0
    for _ in range(30000):
        ia,ik,ig=currents(vp-vk,-vk)
        tvk=ik*RK
        tvp=VB-ia*RA
        if max(abs(tvk-vk),abs(tvp-vp))<1e-12:
            return vp,vk,ia,ik,ig
        vk=0.65*vk+0.35*tvk
        vp=0.65*vp+0.35*tvp
    raise RuntimeError("bias solver did not converge")


def grid_voltage_for_current(target):
    lo=-5.0
    hi=2.0
    for _ in range(120):
        mid=0.5*(lo+hi)
        ig=currents(100.0,mid)[2]  # grid-current law is independent of Va here
        if ig<target:
            lo=mid
        else:
            hi=mid
    return 0.5*(lo+hi)


def solve_plate(vin,bias):
    vp0,vk,ia0,_,_=bias
    vth=vp0+ia0*RAC
    vp=vp0
    vg=vin-vk

    for _ in range(20000):
        ia,_,ig=currents(vp-vk,vg)
        target=vth-ia*RAC
        if abs(target-vp)<1e-11:
            return vp,ig
        vp=0.8*vp+0.2*target
    raise RuntimeError("plate solver did not converge")


def harmonic_component(y,h):
    n=len(y)
    re=0.0
    im=0.0
    for i,v in enumerate(y):
        a=2.0*math.pi*h*i/n
        re += v*math.cos(a)
        im -= v*math.sin(a)
    return 2.0*math.hypot(re,im)/n


def main():
    bias=solve_bias()
    vg_on=grid_voltage_for_current(IG_ONSET)
    input_peak=bias[1]+vg_on

    n=8192
    plate=[]
    max_ig=0.0
    for i in range(n):
        vin=input_peak*math.sin(2.0*math.pi*i/n)
        vp,ig=solve_plate(vin,bias)
        plate.append(vp)
        max_ig=max(max_ig,ig)

    mean=sum(plate)/n
    ac=[x-mean for x in plate]
    rms=math.sqrt(sum(x*x for x in ac)/n)

    harmonics=[harmonic_component(ac,h) for h in range(1,11)]
    thd=math.sqrt(sum(x*x for x in harmonics[1:]))/harmonics[0]

    print("SMX-3 V2 ECC83 large-signal out-of-fit probe")
    print(f"DC cathode current: {bias[3]*1e3:.9f} mA")
    print(f"DC cathode voltage: {bias[1]:.9f} V")
    print(f"grid relative voltage at Ig=0.3uA: {vg_on:.9f} V")
    print(f"required grid input peak: {input_peak:.9f} V")
    print(f"observed max Ig: {max_ig*1e6:.9f} uA")
    print(f"output RMS: {rms:.9f} V   Mullard target {TARGET_VRMS:.6f} V")
    print(f"THD H2-H10: {100.0*thd:.9f}%   Mullard target {100.0*TARGET_THD:.6f}%")
    for i,a in enumerate(harmonics,start=1):
        print(f"H{i}: {a:.9f} Vpeak")

    # This is an intentional rejection test for the current provisional fit.
    if rms < 32.0 or thd < 0.05:
        raise SystemExit("REVIEW: large-signal conclusion changed; re-evaluate the reference model")

    print("REJECT AS FINAL TRI0DE MODEL: small-signal table fit fails Mullard large-signal target.")


if __name__=="__main__":
    main()
