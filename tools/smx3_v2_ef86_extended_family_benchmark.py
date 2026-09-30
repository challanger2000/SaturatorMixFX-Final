#!/usr/bin/env python3
"""Extended EF86 model-family benchmark for SMX-3 V2 research.

This independently re-expresses a published image-fitted pentode equation
family as a RESEARCH COMPARISON only. It is not production code and its
community-fitted parameters are not hardware authority.

Primary SMX-3 authority remains Philips EF86 manufacturer data.

The benchmark checks whether the more flexible knee/kink equation family can
represent Philips amplifier behavior better than the classic compact Koren
form. Standard library only.
"""

import math

# Community image-fit parameter set, used only as a benchmark of the model family.
P={
 "MU":40.7,"KG1":2418.21,"KP":250.28,"KVB":310.76,"VCT":0.4522,"EX":1.327,
 "KG2":6770.18,"KNEE":15.01,"KVC":2.753,"KLAM":4.883e-13,"KLAMG":1.146e-4,
 "KNEE2":6.715,"KNEX":24.2,"KNK":3.906e-4,"KNG":1.163e-4,
 "KNPL":0.1016,"KNSL":25.3,"KNPR":9.15,"KNSR":1593.19
}

RA=100000.0
RG2=390000.0
RK=1000.0
RGLOAD=330000.0

PHILIPS={
 200.0:{"ik":0.00170,"gain":106.0,"vo5":40.0},
 250.0:{"ik":0.00210,"gain":112.0,"vo5":50.0},
 300.0:{"ik":0.00250,"gain":116.0,"vo5":64.0},
 350.0:{"ik":0.00290,"gain":120.0,"vo5":75.0},
 400.0:{"ik":0.00330,"gain":124.0,"vo5":87.0},
}


def log1pexp(x):
    if x>50.0:return x
    if x<-50.0:return math.exp(x)
    return math.log1p(math.exp(x))


def clamp(v,lo,hi):
    return lo if v<lo else hi if v>hi else v


def currents(vp,vg2,vg):
    # Independently expressed from the published equation family.
    z=(1.0/P["MU"]+(P["VCT"]+vg)/math.sqrt(P["KVB"]+vg2*vg2))*P["KP"]
    e1=vg2/P["KP"]*log1pexp(z)

    # The source SPICE construction doubles the positive branch.
    e2=2.0*max(e1,0.0)**P["EX"]

    knee=math.atan((vp+P["KNEX"])/P["KNEE"])*math.tanh(vp/P["KNEE2"])
    base=e2/P["KG1"]*knee

    kink_shape=(
        -math.atan((vp-P["KNPL"])/P["KNSL"])
        +math.atan((vp-P["KNPR"])/P["KNSR"])
    )
    kink=base*clamp(P["KNK"]-vg*P["KNG"],0.0,0.3)*kink_shape

    ia=base*(1.0+P["KLAMG"]*vp)+P["KLAM"]*vp+kink
    ig2=e2/P["KG2"]*(P["KVC"]-knee)/(1.0+P["KLAMG"]*vp)-kink
    return max(ia,0.0),max(ig2,0.0)


def solve_dc(vb):
    vp=.3*vb; vs=.45*vb; vk=2.0
    for _ in range(50000):
        ia,ig2=currents(vp-vk,vs-vk,-vk)
        a=vb-ia*RA; s=vb-ig2*RG2; k=(ia+ig2)*RK
        if max(abs(a-vp),abs(s-vs),abs(k-vk))<1e-11:
            return vp,vs,vk,ia,ig2
        d=.05
        vp=(1-d)*vp+d*a
        vs=(1-d)*vs+d*s
        vk=(1-d)*vk+d*k
    raise RuntimeError("DC solver failed")


def small_gain(dc):
    vp,vs,vk,ia0,_=dc
    r=1.0/(1.0/RA+1.0/RGLOAD)
    vth=vp+ia0*r
    def solve(vin):
        x=vp
        for _ in range(20000):
            ia,_=currents(x-vk,vs-vk,vin-vk)
            t=vth-ia*r
            if abs(t-x)<1e-10:return x
            x=.8*x+.2*t
        raise RuntimeError("AC solve failed")
    dv=1e-5
    return (solve(dv)-solve(-dv))/(2.0*dv)


def waveform(vb,vin_rms,n=1024):
    dc=solve_dc(vb)
    vp,vs,vk,ia0,_=dc
    r=1.0/(1.0/RA+1.0/RGLOAD)
    vth=vp+ia0*r
    ys=[]
    for i in range(n):
        vin=vin_rms*math.sqrt(2.0)*math.sin(2.0*math.pi*i/n)
        x=vp
        for _ in range(5000):
            ia,_=currents(x-vk,vs-vk,vin-vk)
            t=vth-ia*r
            if abs(t-x)<1e-10:break
            x=.75*x+.25*t
        ys.append(x)
    mean=sum(ys)/n
    ys=[v-mean for v in ys]
    rms=math.sqrt(sum(v*v for v in ys)/n)
    mags=[]
    for h in range(1,11):
        re=sum(v*math.cos(2.0*math.pi*h*i/n) for i,v in enumerate(ys))
        im=-sum(v*math.sin(2.0*math.pi*h*i/n) for i,v in enumerate(ys))
        mags.append(2.0*math.hypot(re,im)/n)
    thd=100.0*math.sqrt(sum(m*m for m in mags[1:]))/mags[0]
    return rms,thd


def output_at_5pct(vb):
    lo=0.0; hi=2.0
    for _ in range(45):
        mid=(lo+hi)*0.5
        _,d=waveform(vb,mid,512)
        if d<5.0:lo=mid
        else:hi=mid
    vi=(lo+hi)*0.5
    out,d=waveform(vb,vi,2048)
    return vi,out,d


def pct(v,r):
    return 100.0*(v-r)/r


def main():
    ia,ig2=currents(250.0,140.0,-2.0)
    print("SMX-3 V2 extended EF86 model-family benchmark")
    print("COMMUNITY-FITTED COMPARISON PARAMETERS — NOT HARDWARE AUTHORITY")
    print(f"device Ia @250/140/-2 = {ia*1e3:.6f} mA vs Philips 3.0 mA")
    print(f"device Ig2 @250/140/-2 = {ig2*1e3:.6f} mA vs Philips 0.6 mA")
    print()
    print("Vb,Ik_mA,Ik_err_pct,gain,gain_err_pct,Vo5,Vo5_err_pct")
    for vb in sorted(PHILIPS):
        dc=solve_dc(vb)
        ik=dc[3]+dc[4]
        g=abs(small_gain(dc))
        _,vo5,_=output_at_5pct(vb)
        t=PHILIPS[vb]
        print(f"{vb:.0f},{ik*1e3:.6f},{pct(ik,t['ik']):+.3f},"
              f"{g:.6f},{pct(g,t['gain']):+.3f},"
              f"{vo5:.6f},{pct(vo5,t['vo5']):+.3f}")

    print()
    print("INTERPRETATION:")
    print("- published parameter set is not accepted because DC/screen-current anchors miss materially;")
    print("- the extended knee/kink equation family is promising because gain and large-signal envelope are much closer;")
    print("- next step is an independent refit of this family to Philips primary data.")


if __name__=="__main__":
    main()
