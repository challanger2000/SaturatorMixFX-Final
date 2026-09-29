#!/usr/bin/env python3
"""Large-signal Philips-1956 EF86 gate for SMX-3 V2.

Evaluates the current provisional six-parameter Koren-form model against the
manufacturer's documented output voltage at 5% total distortion for circuit 1.

Purpose: prove whether a model that fits DC/current/gain also reproduces the
large-signal saturation envelope across supply voltage.

Standard library only.
"""

import math
import cmath

P = {
    "MU": 35.7111177,
    "EX": 1.36333942,
    "KG1": 1327.64959,
    "KG2": 3963.35429,
    "KP": 180.899907,
    "KVB": 3.31578637,
}

RA=100000.0
RG2=390000.0
RK=1000.0
RLOAD_NEXT=330000.0

TARGETS = {
    400.0: 87.0,
    350.0: 75.0,
    300.0: 64.0,
    250.0: 50.0,
    200.0: 40.0,
}


def log1pexp(z):
    if z > 50.0:
        return z
    if z < -50.0:
        return math.exp(z)
    return math.log1p(math.exp(z))


def currents(vp, vg2, vg1):
    if vg2 <= 1e-12 or vp <= 0.0:
        return 0.0, 0.0
    z=P["KP"]*(1.0/P["MU"] + vg1/vg2)
    e1=vg2/P["KP"]*log1pexp(z)
    ia=max(e1,0.0)**P["EX"]/P["KG1"]*math.atan(vp/P["KVB"])
    ig2=max(vg2/P["MU"]+vg1,0.0)**P["EX"]/P["KG2"]
    return ia,ig2


def solve_dc(vb):
    vp=0.35*vb
    vs=0.45*vb
    vk=2.0
    for _ in range(30000):
        ia,ig2=currents(vp-vk,vs-vk,-vk)
        tvp=vb-ia*RA
        tvs=vb-ig2*RG2
        tvk=(ia+ig2)*RK
        if max(abs(tvp-vp),abs(tvs-vs),abs(tvk-vk)) < 1e-11:
            return vp,vs,vk,ia,ig2
        d=0.08
        vp=(1-d)*vp+d*tvp
        vs=(1-d)*vs+d*tvs
        vk=(1-d)*vk+d*tvk
    raise RuntimeError("DC solver did not converge")


def solve_plate(vin, dc, seed):
    vp0,vs,vk,ia0,_=dc
    rac=1.0/(1.0/RA+1.0/RLOAD_NEXT)
    vth=vp0+ia0*rac
    x=seed
    for _ in range(500):
        ia,_=currents(x-vk,vs-vk,vin-vk)
        target=vth-ia*rac
        xn=0.65*x+0.35*target
        if abs(xn-x) < 1e-10:
            return xn
        x=xn
    return x


def distortion(vb, vin_rms, n=1024):
    dc=solve_dc(vb)
    vp0=dc[0]
    x=vp0
    amp=vin_rms*math.sqrt(2.0)
    y=[]
    for i in range(n):
        vin=amp*math.sin(2.0*math.pi*i/n)
        x=solve_plate(vin,dc,x)
        y.append(x-vp0)

    mean=sum(y)/n
    y=[v-mean for v in y]
    rms=math.sqrt(sum(v*v for v in y)/n)

    harmonics=[]
    for h in range(1,11):
        re=0.0
        im=0.0
        for i,v in enumerate(y):
            a=2.0*math.pi*h*i/n
            re += v*math.cos(a)
            im -= v*math.sin(a)
        harmonics.append(math.hypot(re,im))

    fund=harmonics[0]
    thd=math.sqrt(sum(v*v for v in harmonics[1:]))/fund
    return rms,thd


def find_output_at_5pct(vb):
    lo=0.01
    hi=1.50
    for _ in range(32):
        mid=0.5*(lo+hi)
        _,thd=distortion(vb,mid,512)
        if thd < 0.05:
            lo=mid
        else:
            hi=mid
    vin=0.5*(lo+hi)
    out,thd=distortion(vb,vin,1024)
    return vin,out,thd


def main():
    print("Vb_V,input_rms_V,output_rms_at_5pct_V,target_output_V,error_pct,THD_pct")
    worst=0.0
    for vb,target in TARGETS.items():
        vin,out,thd=find_output_at_5pct(vb)
        err=100.0*(out-target)/target
        worst=max(worst,abs(err))
        print(f"{vb:.1f},{vin:.9f},{out:.9f},{target:.9f},{err:.6f},{100*thd:.9f}")

    print()
    print(f"worst absolute output error at 5% THD: {worst:.6f}%")
    if worst <= 5.0:
        print("PASS: provisional model reproduces manufacturer large-signal envelope.")
    else:
        print("REJECT AS FINAL EF86 MODEL: six-parameter fit misses manufacturer large-signal envelope.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
