#!/usr/bin/env python3
"""ECC83 multi-domain reference validation for SMX-3 V2.

Compares the three Dempwolf/Zoelzer measured 12AX7 specimen fits against the
selected Mullard 250 V / 100 kOhm / 1.5 kOhm cathode-bias amplifier.

Unlike the earlier unloaded small-signal check, this tool includes the
documented 330 kOhm following-stage grid resistor as the AC load.

It also measures the large-signal point at peak grid current Ig ~= 0.3 uA,
matching the Mullard table condition.

Standard library only.
"""

import math

TUBES={
"RSD-1":{"G":2.242e-3,"mu":103.2,"gamma":1.26,"C":3.40,"Gg":6.177e-4,"xi":1.314,"Cg":9.901,"Ig0":8.025e-8},
"RSD-2":{"G":2.173e-3,"mu":100.2,"gamma":1.28,"C":3.19,"Gg":5.911e-4,"xi":1.358,"Cg":11.76,"Ig0":4.527e-8},
"EHX-1":{"G":1.371e-3,"mu":86.9,"gamma":1.349,"C":4.56,"Gg":3.263e-4,"xi":1.156,"Cg":11.99,"Ig0":3.917e-8},
}

VB=250.0
RA=100000.0
RK=1500.0
RLOAD=330000.0

TARGET_IK=0.00086
TARGET_GAIN=54.5
TARGET_OUT=26.0
TARGET_THD=3.9
TARGET_PEAK_IG=0.3e-6


def softplus(x,c):
    z=c*x
    if z>50:return x
    if z<-50:return math.exp(z)/c
    return math.log1p(math.exp(z))/c


def make_currents(p):
    def current(va,vg):
        ik=p["G"]*softplus(va/p["mu"]+vg,p["C"])**p["gamma"]
        ig=p["Gg"]*softplus(vg,p["Cg"])**p["xi"]+p["Ig0"]
        return ik,ik-ig,ig
    return current


def solve_specimen(p):
    current=make_currents(p)
    vk=1.2; vp=165.0
    for _ in range(30000):
        ik,ia,ig=current(vp-vk,-vk)
        nvk=ik*RK
        nvp=VB-ia*RA
        if max(abs(nvk-vk),abs(nvp-vp))<1e-12:break
        vk=0.7*vk+0.3*nvk
        vp=0.7*vp+0.3*nvp
    else: raise RuntimeError("DC solve failed")

    rload=1.0/(1.0/RA+1.0/RLOAD)
    vth=vp+ia*rload

    def plate(vin):
        x=vp
        for _ in range(20000):
            _,iax,igx=current(x-vk,vin-vk)
            target=vth-iax*rload
            if abs(target-x)<1e-12:return x,igx
            x=0.8*x+0.2*target
        raise RuntimeError("plate solve failed")

    dv=1e-4
    gain=(plate(dv)[0]-plate(-dv)[0])/(2.0*dv)

    def measure(vi,n=2048):
        ys=[]; peak_ig=0.0
        for i in range(n):
            vin=vi*math.sqrt(2.0)*math.sin(2.0*math.pi*i/n)
            y,igx=plate(vin)
            ys.append(y)
            peak_ig=max(peak_ig,igx)
        mean=sum(ys)/n
        ys=[y-mean for y in ys]
        rms=math.sqrt(sum(y*y for y in ys)/n)
        amps=[]
        for h in range(1,11):
            re=sum(y*math.cos(2.0*math.pi*h*i/n) for i,y in enumerate(ys))
            im=-sum(y*math.sin(2.0*math.pi*h*i/n) for i,y in enumerate(ys))
            amps.append(2.0*math.hypot(re,im)/n)
        thd=100.0*math.sqrt(sum(a*a for a in amps[1:]))/amps[0]
        return rms,thd,peak_ig

    lo=0.0; hi=1.5
    for _ in range(55):
        mid=0.5*(lo+hi)
        if measure(mid,512)[2] < TARGET_PEAK_IG:lo=mid
        else:hi=mid
    vi=0.5*(lo+hi)
    out,thd,peak_ig=measure(vi,4096)

    return {
        "Ik":ik,"Vp":vp,"Vk":vk,"gain":gain,
        "input":vi,"out":out,"thd":thd,"peakIg":peak_ig
    }


def pct(v,r):return 100.0*(v-r)/r


def main():
    print("specimen,Ik_mA,Ik_err_pct,loaded_gain,gain_err_pct,Vo_at_0p3uA,Vo_err_pct,THD_pct,THD_err_pct")
    for name,p in TUBES.items():
        r=solve_specimen(p)
        print(
            f"{name},{r['Ik']*1e3:.6f},{pct(r['Ik'],TARGET_IK):+.3f},"
            f"{abs(r['gain']):.6f},{pct(abs(r['gain']),TARGET_GAIN):+.3f},"
            f"{r['out']:.6f},{pct(r['out'],TARGET_OUT):+.3f},"
            f"{r['thd']:.6f},{pct(r['thd'],TARGET_THD):+.3f}"
        )

    print()
    print("NOTE: this is a specimen/model comparison, not a release PASS gate.")


if __name__=="__main__":
    main()
