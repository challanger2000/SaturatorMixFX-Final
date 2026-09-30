#!/usr/bin/env python3
"""ECC83/12AX7 large-signal reference for SMX-3 V2 TRI0DE.

Uses:
- Dempwolf/Zoelzer EHX-1 measured-tube parameter set;
- selected Mullard common-cathode reference:
  Vb=250 V, Ra=100 kOhm, Rk=1.5 kOhm;
- documented 330 kOhm following-stage grid resistor as AC plate load.

The cathode is treated as AC-bypassed for this static/low-frequency
large-signal reference. The purpose is to freeze harmonic progression and
grid-current onset before adding dynamic capacitances.

Standard library only.
"""

import math

P={"G":1.371e-3,"mu":86.9,"gamma":1.349,"C":4.56,
   "Gg":3.263e-4,"xi":1.156,"Cg":11.99,"Ig0":3.917e-8}

VB=250.0
RA=100000.0
RK=1500.0
RNEXT=330000.0


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
    return ik,ik-ig,ig


def solve_dc():
    vk=1.2
    vp=165.0
    for _ in range(20000):
        ik,ia,ig=currents(vp-vk,-vk)
        tvk=ik*RK
        tvp=VB-ia*RA
        if max(abs(tvk-vk),abs(tvp-vp))<1e-12:
            return vk,vp,ik,ia,ig
        vk=0.7*vk+0.3*tvk
        vp=0.7*vp+0.3*tvp
    raise RuntimeError("DC solver did not converge")


def solve_plate(vin,dc,seed):
    vk,vp0,_,ia0,_=dc
    rac=1.0/(1.0/RA+1.0/RNEXT)
    vth=vp0+ia0*rac
    x=seed
    for _ in range(1000):
        _,ia,_=currents(x-vk,vin-vk)
        target=vth-ia*rac
        xn=0.70*x+0.30*target
        if abs(xn-x)<1e-11:
            return xn
        x=xn
    raise RuntimeError("plate solver did not converge")


def harmonic_metrics(vin_rms,n=4096):
    dc=solve_dc()
    vk,vp0,_,_,_=dc
    amp=vin_rms*math.sqrt(2.0)
    x=vp0
    y=[]
    grid=[]

    for i in range(n):
        vin=amp*math.sin(2.0*math.pi*i/n)
        x=solve_plate(vin,dc,x)
        y.append(x-vp0)
        _,_,ig=currents(x-vk,vin-vk)
        grid.append(ig)

    mean=sum(y)/n
    y=[v-mean for v in y]
    rms=math.sqrt(sum(v*v for v in y)/n)

    mags=[]
    for h in range(1,11):
        re=0.0
        im=0.0
        for i,v in enumerate(y):
            a=2.0*math.pi*h*i/n
            re += v*math.cos(a)
            im -= v*math.sin(a)
        mags.append(math.hypot(re,im))

    fund=mags[0]
    rel=[m/fund for m in mags[1:]]
    thd=math.sqrt(sum(v*v for v in rel))
    return rms,thd,rel,max(grid),sum(grid)/n


def main():
    dc=solve_dc()
    print("SMX-3 V2 ECC83 EHX-1 large-signal reference")
    print(f"DC Vk={dc[0]:.9f} V Vp={dc[1]:.9f} V Ik={dc[2]*1e3:.9f} mA")
    print()
    print("Vin_rms_V,Vout_rms_V,THD_pct,H2_pct,H3_pct,H4_pct,H5_pct,H6_pct,Ig_peak_mA,Ig_mean_uA")

    for vin in (0.05,0.10,0.20,0.30,0.50,0.70,1.00,1.50,2.00):
        rms,thd,rel,igpk,igmean=harmonic_metrics(vin)
        print(
            f"{vin:.4f},{rms:.9f},{100*thd:.9f},"
            f"{100*rel[0]:.9f},{100*rel[1]:.9f},{100*rel[2]:.9f},"
            f"{100*rel[3]:.9f},{100*rel[4]:.9f},"
            f"{igpk*1e3:.9f},{igmean*1e6:.9f}"
        )

    # Regression anchors for the current offline reference.
    _,thd_01,rel_01,_,_=harmonic_metrics(0.10,2048)
    _,thd_10,rel_10,igpk_10,_=harmonic_metrics(1.00,2048)

    if not (0.0035 < thd_01 < 0.0052):
        raise SystemExit("FAIL: low-level harmonic reference moved")
    if not (0.055 < thd_10 < 0.075):
        raise SystemExit("FAIL: 1 Vrms large-signal THD reference moved")
    if not (rel_01[0] > 20.0*rel_01[1]):
        raise SystemExit("FAIL: expected low-level H2 dominance changed")
    if not (igpk_10 > 10e-6):
        raise SystemExit("FAIL: positive-grid-current onset no longer present")

    print()
    print("PASS: ECC83 large-signal harmonic/grid-current reference is stable.")


if __name__=="__main__":
    main()
