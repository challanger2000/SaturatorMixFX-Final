#!/usr/bin/env python3
"""Dynamic ECC83 reference circuit for SMX-3 V2 TRI0DE research.

Offline reference only. Solves the documented Mullard-style ECC83 network with
the Dempwolf/Zoelzer measured EHX-1 current equations.

Circuit:
- Vb 250 V
- Ra 100 kOhm
- Rk 1.5 kOhm
- grid leak 1 MOhm
- next-stage load 330 kOhm
- input coupling 0.01 uF
- cathode bypass 50 uF
- output coupling 0.01 uF
- Cak 0.9 pF, Cgk 2.3 pF, Cag 2.4 pF

Numerics:
constant capacitance MNA matrix + implicit trapezoidal integration with Newton
iterations. The reference rate is frequency-adaptive: at least 192 kHz and at
least 96 integration steps per fundamental period. This is deliberately slower
than production DSP and serves as the dynamic authority candidate.

Standard library only.
"""

import math

P={"G":1.371e-3,"mu":86.9,"gamma":1.349,"C":4.56,
   "Gg":3.263e-4,"xi":1.156,"Cg":11.99,"Ig0":3.917e-8}

VB=250.0
RA=100000.0
RK=1500.0
RG=1000000.0
RLOAD=330000.0
CIN=10e-9
COUT=10e-9
CK=50e-6
CAK=0.9e-12
CGK=2.3e-12
CAG=2.4e-12

NODES=4
G,P_NODE,K,O=0,1,2,3


def softplus_scaled(x,c):
    z=c*x
    if z>50.0: return x
    if z<-50.0: return math.exp(z)/c
    return math.log1p(math.exp(z))/c


def currents(va,vg):
    ik=P["G"]*softplus_scaled(va/P["mu"]+vg,P["C"])**P["gamma"]
    ig=P["Gg"]*softplus_scaled(vg,P["Cg"])**P["xi"]+P["Ig0"]
    return ik,ik-ig,ig


def solve_dc():
    vk=1.2
    vp=165.0
    for _ in range(20000):
        ik,ia,_=currents(vp-vk,-vk)
        tvk=ik*RK
        tvp=VB-ia*RA
        if max(abs(tvk-vk),abs(tvp-vp))<1e-12:
            return [0.0,vp,vk,0.0]
        vk=0.7*vk+0.3*tvk
        vp=0.7*vp+0.3*tvp
    raise RuntimeError("DC solver did not converge")


def add_cap(C,i,j,value):
    C[i][i]+=value
    if j is not None:
        C[j][j]+=value
        C[i][j]-=value
        C[j][i]-=value


def capacitance_matrix():
    C=[[0.0]*NODES for _ in range(NODES)]
    add_cap(C,G,None,CIN)      # source side is known excitation
    add_cap(C,G,K,CGK)
    add_cap(C,P_NODE,G,CAG)
    add_cap(C,P_NODE,K,CAK)
    add_cap(C,P_NODE,O,COUT)
    add_cap(C,K,None,CK)
    return C


CMAT=capacitance_matrix()


def matvec(A,x):
    return [sum(A[i][j]*x[j] for j in range(NODES)) for i in range(NODES)]


def solve_linear(A,b):
    n=len(A)
    m=[A[i][:]+[b[i]] for i in range(n)]
    for c in range(n):
        q=max(range(c,n),key=lambda r:abs(m[r][c]))
        m[c],m[q]=m[q],m[c]
        pivot=m[c][c]
        if abs(pivot)<1e-30:
            raise RuntimeError("singular Newton matrix")
        for j in range(c,n+1):
            m[c][j]/=pivot
        for r in range(n):
            if r==c: continue
            f=m[r][c]
            for j in range(c,n+1):
                m[r][j]-=f*m[c][j]
    return [m[i][n] for i in range(n)]


def rhs(t,x,vin_peak,freq):
    vg,vp,vk,vo=x
    dvin=vin_peak*2.0*math.pi*freq*math.cos(2.0*math.pi*freq*t)
    ik,ia,ig=currents(vp-vk,vg-vk)
    return [
        CIN*dvin-vg/RG-ig,
        VB/RA-vp/RA-ia,
        -vk/RK+ik,
        -vo/RLOAD,
    ]


def trapezoid_step(t,x,dt,vin_peak,freq):
    r0=rhs(t,x,vin_peak,freq)

    # Conservative initial predictor: previous state. Newton solves the full
    # implicit trapezoidal residual; no explicit stiff step is required.
    z=x[:]

    for iteration in range(16):
        r1=rhs(t+dt,z,vin_peak,freq)
        dz=[z[i]-x[i] for i in range(NODES)]
        cd=matvec(CMAT,dz)
        F=[cd[i]/dt-0.5*(r0[i]+r1[i]) for i in range(NODES)]

        if max(abs(v) for v in F)<1e-10:
            return z,iteration

        J=[[0.0]*NODES for _ in range(NODES)]
        for j in range(NODES):
            eps=1e-7*max(1.0,abs(z[j]))
            zz=z[:]
            zz[j]+=eps
            rr=rhs(t+dt,zz,vin_peak,freq)
            dd=[zz[i]-x[i] for i in range(NODES)]
            cdd=matvec(CMAT,dd)
            FF=[cdd[i]/dt-0.5*(r0[i]+rr[i]) for i in range(NODES)]
            for i in range(NODES):
                J[i][j]=(FF[i]-F[i])/eps

        delta=solve_linear(J,[-v for v in F])
        z=[z[i]+delta[i] for i in range(NODES)]

        if not all(math.isfinite(v) for v in z):
            raise RuntimeError("non-finite Newton state")
        if max(abs(v) for v in delta)<1e-10:
            return z,iteration+1

    raise RuntimeError("Newton solver did not converge")


def simulate(freq,vin_rms,fs=None,cycles=8):
    # The offline reference must not let its own integration rate dominate the
    # measured HF response. Keep at least 96 integration steps per fundamental
    # period and never go below 192 kHz.
    if fs is None:
        fs=max(192000.0,96.0*freq)
    samples=max(1,int(round(cycles*fs/freq)))
    dt=1.0/fs
    x=solve_dc()
    vin_peak=vin_rms*math.sqrt(2.0)
    out=[]
    max_newton=0

    for n in range(samples):
        x,it=trapezoid_step(n*dt,x,dt,vin_peak,freq)
        max_newton=max(max_newton,it)
        out.append(x[O])

    samples_per_cycle=max(1,int(round(fs/freq)))
    keep=min(len(out),4*samples_per_cycle)
    y=out[-keep:]
    mean=sum(y)/len(y)
    y=[v-mean for v in y]
    N=len(y)

    mags=[]
    phases=[]
    max_h=min(10,int((0.49*fs)//freq))
    for h in range(1,max_h+1):
        re=0.0
        im=0.0
        for i,v in enumerate(y):
            a=2.0*math.pi*h*freq*i/fs
            re+=v*math.cos(a)
            im-=v*math.sin(a)
        mags.append(2.0*math.hypot(re,im)/N)
        phases.append(math.atan2(im,re))

    fund=mags[0]
    thd=math.sqrt(sum(m*m for m in mags[1:]))/fund if len(mags)>1 else 0.0
    out_rms=math.sqrt(sum(v*v for v in y)/N)
    gain=fund/vin_peak

    return {
        "out_rms":out_rms,
        "gain":gain,
        "phase_deg":math.degrees(phases[0]),
        "thd":thd,
        "harmonics":[m/fund for m in mags[1:]],
        "max_newton":max_newton,
    }


def main():
    dc=solve_dc()
    print("SMX-3 V2 dynamic ECC83 EHX-1 reference")
    print(f"DC: Vp={dc[P_NODE]:.9f} V Vk={dc[K]:.9f} V")
    print()

    print("Small-signal frequency response, Vin=10 mVrms")
    print("freq_Hz,gain_V_per_V,phase_deg,THD_pct,max_Newton_iterations")
    for f in (20.0,50.0,100.0,1000.0,10000.0,20000.0):
        r=simulate(f,0.010)
        print(f"{f:.1f},{r['gain']:.9f},{r['phase_deg']:.9f},{100*r['thd']:.9f},{r['max_newton']}")

    print()
    print("1 kHz large-signal progression")
    print("Vin_rms,Vout_rms,THD_pct,H2_pct,H3_pct,max_Newton_iterations")
    for vin in (0.10,0.30,0.50,0.70,1.00):
        r=simulate(1000.0,vin)
        hs=r["harmonics"]+[0.0,0.0]
        print(f"{vin:.3f},{r['out_rms']:.9f},{100*r['thd']:.9f},{100*hs[0]:.9f},{100*hs[1]:.9f},{r['max_newton']}")

    # Low-level dynamic gain should remain close to the loaded static reference.
    g1=simulate(1000.0,0.010)["gain"]
    if not (48.0<g1<53.0):
        raise SystemExit("FAIL: 1 kHz dynamic small-signal gain left expected loaded-EHX range")

    # Low-level 1 kHz distortion should remain EHX-like and finite.
    d1=simulate(1000.0,0.10)["thd"]
    if not (0.003<d1<0.006):
        raise SystemExit("FAIL: low-level dynamic harmonic reference moved")

    print()
    print("PASS: dynamic ECC83 circuit is finite and consistent with the low-level loaded reference.")


if __name__=="__main__":
    main()
