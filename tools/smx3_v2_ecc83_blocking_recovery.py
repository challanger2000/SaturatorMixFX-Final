#!/usr/bin/env python3
"""TRIODE grid-current-law blocking/recovery sensitivity for SMX-3 V2.

The RSD-2 plate/cathode-current law and the documented Mullard/Philips
surrounding circuit are held fixed.

Only the grid-current law Ig(Vg) is varied:
- RSD-2 (current primary reference)
- RSD-1 grid law
- EHX-1 grid law
- Danyuk AES-137 polynomial overload fit

This deliberately isolates the influence of grid-current magnitude on:
- coupling-capacitor/bias shift;
- immediate post-overdrive attenuation;
- recovery trajectory.

Hybrid runs are sensitivity experiments, NOT claims about complete physical
tube specimens.

Standard library only.
"""

import math

import smx3_v2_ecc83_dynamic_reference as ref


GRID_LAWS={
    "RSD-2":{"kind":"dempwolf","Gg":5.911e-4,"xi":1.358,"Cg":11.76,"Ig0":4.527e-8},
    "RSD-1":{"kind":"dempwolf","Gg":6.177e-4,"xi":1.314,"Cg":9.901,"Ig0":8.025e-8},
    "EHX-1":{"kind":"dempwolf","Gg":3.263e-4,"xi":1.156,"Cg":11.99,"Ig0":3.917e-8},
    "Danyuk-poly":{"kind":"danyuk"},
}


def softplus(v,c):
    z=c*v
    if z>50.0:
        return v
    if z<-50.0:
        return math.exp(z)/c
    return math.log1p(math.exp(z))/c


def grid_current(name,vg):
    p=GRID_LAWS[name]
    if p["kind"]=="dempwolf":
        return p["Gg"]*softplus(vg,p["Cg"])**p["xi"]+p["Ig0"]

    # Danyuk AES-137 polynomial fit around the transition/positive-grid region.
    # Kept non-negative to avoid inventing reverse grid current.
    return 3.1e-4*max(vg+0.53,0.0)**3


def cathode_current(va,vg):
    p=ref.P
    return p["G"]*ref.softplus_scaled(va/p["mu"]+vg,p["C"])**p["gamma"]


def currents(name,va,vg):
    ik=cathode_current(va,vg)
    ig=grid_current(name,vg)
    return ik,ik-ig,ig


def solve_dc(name):
    vk=1.2
    vp=165.0

    for _ in range(30000):
        ik,ia,_=currents(name,vp-vk,-vk)
        tvk=ik*ref.RK
        tvp=ref.VB-ia*ref.RA

        if max(abs(tvk-vk),abs(tvp-vp))<1e-12:
            return [0.0,vp,vk,0.0]

        vk=.7*vk+.3*tvk
        vp=.7*vp+.3*tvp

    raise RuntimeError("DC solver did not converge")


def rms_for_time(t,low_rms,stress_rms,pre,stress):
    if t<pre:
        return low_rms
    if t<pre+stress:
        return stress_rms
    return low_rms


def rhs(name,t,x,freq,low_rms,stress_rms,pre,stress):
    vg,vp,vk,vo=x
    vrms=rms_for_time(t,low_rms,stress_rms,pre,stress)
    peak=vrms*math.sqrt(2.0)

    # Switching happens at integer 1 kHz cycle boundaries in the fixture,
    # where the sine itself is zero. The source voltage remains continuous.
    dvin=peak*2.0*math.pi*freq*math.cos(2.0*math.pi*freq*t)

    ik,ia,ig=currents(name,vp-vk,vg-vk)

    return [
        ref.CIN*dvin-vg/ref.RG-ig,
        ref.VB/ref.RA-vp/ref.RA-ia,
        -vk/ref.RK+ik,
        -vo/ref.RLOAD,
    ]


def step(name,t,x,dt,freq,low_rms,stress_rms,pre,stress):
    r0=rhs(name,t,x,freq,low_rms,stress_rms,pre,stress)
    z=x[:]

    for iteration in range(18):
        r1=rhs(name,t+dt,z,freq,low_rms,stress_rms,pre,stress)
        dz=[z[i]-x[i] for i in range(ref.NODES)]
        cd=ref.matvec(ref.CMAT,dz)
        F=[cd[i]/dt-.5*(r0[i]+r1[i]) for i in range(ref.NODES)]

        if max(abs(v) for v in F)<1e-10:
            return z,iteration

        J=[[0.0]*ref.NODES for _ in range(ref.NODES)]
        for j in range(ref.NODES):
            eps=1e-7*max(1.0,abs(z[j]))
            zz=z[:]
            zz[j]+=eps
            rr=rhs(name,t+dt,zz,freq,low_rms,stress_rms,pre,stress)
            dd=[zz[i]-x[i] for i in range(ref.NODES)]
            cdd=ref.matvec(ref.CMAT,dd)
            FF=[cdd[i]/dt-.5*(r0[i]+rr[i]) for i in range(ref.NODES)]
            for i in range(ref.NODES):
                J[i][j]=(FF[i]-F[i])/eps

        delta=ref.solve_linear(J,[-v for v in F])
        z=[z[i]+delta[i] for i in range(ref.NODES)]

        if not all(math.isfinite(v) for v in z):
            raise RuntimeError("non-finite blocking/recovery state")
        if max(abs(v) for v in delta)<1e-10:
            return z,iteration+1

    raise RuntimeError("blocking/recovery Newton solver did not converge")


def window_stats(samples,fs,start_s,end_s,low_rms):
    a=max(0,int(round(start_s*fs)))
    b=min(len(samples),int(round(end_s*fs)))
    rows=samples[a:b]

    if not rows:
        raise RuntimeError("empty analysis window")

    y=[r[0] for r in rows]
    vgr=[r[1] for r in rows]
    vk=[r[2] for r in rows]

    mean=sum(y)/len(y)
    ac=[v-mean for v in y]
    out_rms=math.sqrt(sum(v*v for v in ac)/len(ac))

    gain=out_rms/low_rms
    return {
        "gain":gain,
        "vg_mean":sum(vgr)/len(vgr),
        "vk_mean":sum(vk)/len(vk),
    }


def simulate(name,fs=96000.0,freq=1000.0,low_rms=0.10,stress_rms=1.50,
             pre=0.20,stress=0.10,recovery=0.40):
    total=pre+stress+recovery
    n=int(round(total*fs))
    dt=1.0/fs

    x=solve_dc(name)
    rows=[]
    peak_ig=0.0
    max_vg=-1e9

    for i in range(n):
        t=i*dt
        x,_=step(name,t,x,dt,freq,low_rms,stress_rms,pre,stress)

        va=x[ref.P_NODE]-x[ref.K]
        vg=x[ref.G]-x[ref.K]
        _,_,ig=currents(name,va,vg)

        peak_ig=max(peak_ig,ig)
        max_vg=max(max_vg,vg)

        rows.append((x[ref.O],vg,x[ref.K]))

    baseline=window_stats(rows,fs,pre-.04,pre-.01,low_rms)

    # Recovery windows are relative to the end of the stress burst.
    t0=pre+stress
    windows=[
        ("0-20ms",t0,t0+.020),
        ("50-70ms",t0+.050,t0+.070),
        ("100-120ms",t0+.100,t0+.120),
        ("200-220ms",t0+.200,t0+.220),
        ("350-370ms",t0+.350,t0+.370),
    ]

    out=[]
    for label,a,b in windows:
        s=window_stats(rows,fs,a,b,low_rms)
        s["label"]=label
        s["gain_ratio"]=s["gain"]/baseline["gain"]
        out.append(s)

    return baseline,out,peak_ig,max_vg


def main():
    print("SMX-3 V2 TRI0DE grid-current blocking/recovery sensitivity")
    print("Fixed plate law: RSD-2; only Ig(Vg) varies.")
    print("Fixture: 1 kHz, 0.10 Vrms baseline -> 1.50 Vrms for 100 ms -> 0.10 Vrms recovery.")
    print()

    for name in GRID_LAWS:
        base,recovery,peak_ig,max_vg=simulate(name)

        print(f"[{name}]")
        print(
            f"baseline_gain={base['gain']:.6f} "
            f"baseline_VgMean={base['vg_mean']:.6f}V "
            f"baseline_VkMean={base['vk_mean']:.6f}V "
            f"stress_peak_Ig={peak_ig*1e6:.3f}uA "
            f"max_Vg={max_vg:.6f}V"
        )
        print("window,gain,gain_vs_baseline,Vg_mean_V,Vk_mean_V")
        for r in recovery:
            print(
                f"{r['label']},{r['gain']:.6f},{r['gain_ratio']:.6f},"
                f"{r['vg_mean']:.6f},{r['vk_mean']:.6f}"
            )
        print()

    print("INFO: differences quantify grid-current-law sensitivity, not complete tube-specimen differences.")
    print("INFO: Danyuk polynomial is a measured overload cross-check and must not be extrapolated as a universal 12AX7 law.")


if __name__=="__main__":
    main()
