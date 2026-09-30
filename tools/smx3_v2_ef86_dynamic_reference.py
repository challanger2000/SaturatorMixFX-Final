#!/usr/bin/env python3
"""Dynamic EF86 offline reference for SMX-3 V2 PENTODE research.

Reference device model:
- current strongest EX=1.40 static/large-signal candidate;
- Stage-2C normalized plate knee.

Documented Philips circuit elements represented:
- Ra = 100 kOhm
- Rg2 = 390 kOhm
- Rk = 1 kOhm
- screen bypass = 0.5 uF
- cathode bypass = 50 uF
- output coupling = 0.01 uF
- following-stage load Rg1' = 330 kOhm

Documented Philips tube capacitances represented conservatively as:
- Cg1 = 3.8 pF, lumped g1-to-cathode input capacitance
- Ca = 5.3 pF, lumped anode-to-cathode output capacitance
- Cag1 = 0.05 pF upper-bound reverse capacitance, anode-to-g1

The Philips application drawing shows an input coupling capacitor and Rg1 but
does not numerically state Rg1 in the selected operating table. To avoid
inventing a value, this first dynamic reference is driven directly at g1.
The reported transfer is therefore g1-node voltage -> loaded output voltage.

This is an OFFLINE authority candidate, not realtime DSP.

Standard library only.
"""

import math

import smx3_v2_ef86_ex_scan as base

# Current strongest candidate.
EX=1.40
VCT,KG1,S0=base.derive_local(EX)
P=(EX,VCT,KG1,S0)

VB=250.0
RA=100000.0
RG2=390000.0
RK=1000.0
RLOAD=330000.0

CS=0.5e-6
CK=50.0e-6
COUT=0.01e-6

CG1=3.8e-12
CA=5.3e-12
CAG1=0.05e-12

# State indices.
P_NODE=0
S_NODE=1
K_NODE=2
O_NODE=3
N=4


def ia(vp,vs,vk,vg):
    return base.ia(vp-vk,vs-vk,vg-vk,*P[:3])


def ig2(vp,vs,vk,vg):
    return base.ig2(vp-vk,vs-vk,vg-vk,EX,VCT,S0)


def solve_dc():
    vp=.35*VB
    vs=.50*VB
    vk=2.0

    for _ in range(40000):
        a=ia(vp,vs,vk,0.0)
        s=ig2(vp,vs,vk,0.0)

        tvp=VB-a*RA
        tvs=VB-s*RG2
        tvk=(a+s)*RK

        if max(abs(tvp-vp),abs(tvs-vs),abs(tvk-vk))<1e-12:
            return [vp,vs,vk,0.0]

        d=.08
        vp=(1-d)*vp+d*tvp
        vs=(1-d)*vs+d*tvs
        vk=(1-d)*vk+d*tvk

    raise RuntimeError("EF86 DC solver did not converge")


# Capacitance matrix for x=[plate, screen, cathode, output].
C=[
    [CA+CAG1+COUT, 0.0,          -CA,             -COUT],
    [0.0,          CS,            0.0,              0.0],
    [-CA,           0.0,          CK+CA+CG1,         0.0],
    [-COUT,         0.0,          0.0,              COUT],
]


def matvec(A,x):
    return [sum(A[i][j]*x[j] for j in range(len(x))) for i in range(len(A))]


def solve_linear(A,b):
    n=len(b)
    M=[A[i][:]+[b[i]] for i in range(n)]

    for col in range(n):
        pivot=max(range(col,n),key=lambda r:abs(M[r][col]))
        if abs(M[pivot][col])<1e-30:
            raise RuntimeError("singular Newton matrix")
        if pivot!=col:
            M[col],M[pivot]=M[pivot],M[col]

        q=M[col][col]
        for j in range(col,n+1):
            M[col][j]/=q

        for r in range(n):
            if r==col:
                continue
            q=M[r][col]
            if q==0.0:
                continue
            for j in range(col,n+1):
                M[r][j]-=q*M[col][j]

    return [M[i][n] for i in range(n)]


def grid(t,vin_peak,freq):
    return vin_peak*math.sin(2.0*math.pi*freq*t)


def grid_dot(t,vin_peak,freq):
    return vin_peak*2.0*math.pi*freq*math.cos(2.0*math.pi*freq*t)


def rhs(t,x,vin_peak,freq):
    vp,vs,vk,vo=x
    vg=grid(t,vin_peak,freq)
    dvg=grid_dot(t,vin_peak,freq)

    a=ia(vp,vs,vk,vg)
    s=ig2(vp,vs,vk,vg)

    # C dx/dt = rhs. Grid-capacitor source-derivative terms are explicit.
    return [
        -((vp-VB)/RA + a) + CAG1*dvg,
        -((vs-VB)/RG2 + s),
        -(vk/RK - a - s) + CG1*dvg,
        -(vo/RLOAD),
    ]


def trapezoid_step(t,x,dt,vin_peak,freq):
    f0=rhs(t,x,vin_peak,freq)
    Cx0=matvec(C,x)
    z=x[:]

    for iteration in range(20):
        f1=rhs(t+dt,z,vin_peak,freq)
        Cz=matvec(C,z)

        F=[
            (Cz[i]-Cx0[i])/dt - 0.5*(f0[i]+f1[i])
            for i in range(N)
        ]

        if max(abs(v) for v in F)<1e-10:
            return z,iteration

        J=[[0.0]*N for _ in range(N)]
        for j in range(N):
            eps=1e-7*max(1.0,abs(z[j]))
            zz=z[:]
            zz[j]+=eps
            ff=rhs(t+dt,zz,vin_peak,freq)
            CC=matvec(C,zz)
            FF=[
                (CC[i]-Cx0[i])/dt - 0.5*(f0[i]+ff[i])
                for i in range(N)
            ]
            for i in range(N):
                J[i][j]=(FF[i]-F[i])/eps

        delta=solve_linear(J,[-v for v in F])
        z=[z[i]+delta[i] for i in range(N)]

        if not all(math.isfinite(v) for v in z):
            raise RuntimeError("non-finite EF86 dynamic state")

        if max(abs(v) for v in delta)<1e-10:
            return z,iteration+1

    raise RuntimeError("EF86 dynamic Newton solver did not converge")


def simulate(freq,vin_rms,fs=None,warmup_seconds=0.4,cycles=8):
    if fs is None:
        fs=max(192000.0,96.0*freq)

    vin_peak=vin_rms*math.sqrt(2.0)
    x=solve_dc()
    max_newton=0

    # Physical-time warmup; cathode bypass RC is ~50 ms.
    warm_fs=min(fs,max(192000.0,24.0*freq))
    n_warm=int(round(warmup_seconds*warm_fs))
    dtw=1.0/warm_fs

    for n in range(n_warm):
        x,it=trapezoid_step(n*dtw,x,dtw,vin_peak,freq)
        max_newton=max(max_newton,it)

    t0=n_warm/warm_fs

    n=max(1,int(round(cycles*fs/freq)))
    dt=1.0/fs
    out=[]

    for i in range(n):
        x,it=trapezoid_step(t0+i*dt,x,dt,vin_peak,freq)
        max_newton=max(max_newton,it)
        out.append(x[O_NODE])

    spc=max(1,int(round(fs/freq)))
    keep=min(len(out),4*spc)
    start=len(out)-keep
    y=out[start:]
    mean=sum(y)/len(y)
    y=[v-mean for v in y]
    times=[t0+(start+i+1)/fs for i in range(len(y))]

    mags=[]
    phases=[]
    max_h=min(10,int((0.49*fs)//freq))

    for h in range(1,max_h+1):
        re=im=0.0
        for t,v in zip(times,y):
            a=2.0*math.pi*h*freq*t
            re+=v*math.cos(a)
            im-=v*math.sin(a)
        mags.append(2.0*math.hypot(re,im)/len(y))
        phases.append(math.atan2(im,re))

    in_re=in_im=0.0
    for t in times:
        v=vin_peak*math.sin(2.0*math.pi*freq*t)
        a=2.0*math.pi*freq*t
        in_re+=v*math.cos(a)
        in_im-=v*math.sin(a)
    in_phase=math.atan2(in_im,in_re)

    rel=phases[0]-in_phase
    while rel>math.pi: rel-=2.0*math.pi
    while rel<-math.pi: rel+=2.0*math.pi

    fund=mags[0]
    thd=math.sqrt(sum(a*a for a in mags[1:]))/fund if len(mags)>1 else 0.0

    return {
        "gain":fund/vin_peak,
        "phase_deg":math.degrees(rel),
        "thd":thd,
        "max_newton":max_newton,
    }


def main():
    dc=solve_dc()
    print("SMX-3 V2 EF86 dynamic offline reference")
    print("g1-node drive; Philips circuit-1 cathode/screen/output networks")
    print(f"EX={EX:.6f} VCT={VCT:.9f} KG1={KG1:.9f} S0={S0:.12g}")
    print(f"DC: plate={dc[0]:.6f}V screen={dc[1]:.6f}V cathode={dc[2]:.6f}V")
    print()
    print("freq_Hz,Vin_rms,gain,phase_deg,THD_pct,max_Newton")

    rows=[]
    for freq in (20.0,100.0,1000.0,10000.0,20000.0):
        r=simulate(freq,0.010)
        rows.append((freq,r))
        print(
            f"{freq:.1f},0.010,{r['gain']:.9f},{r['phase_deg']:.9f},"
            f"{100*r['thd']:.9f},{r['max_newton']}"
        )

    # The exact manufacturer table's ~112 V/V is a small-input midband anchor.
    r1k=dict(rows)[1000.0]
    err=100.0*(r1k["gain"]-112.0)/112.0
    print()
    print(f"1 kHz gain error vs Philips 112 V/V = {err:+.6f}%")

    # Provisional dynamic gate: preserve already-established small-signal
    # accuracy; do not yet make HF magnitude a hard manufacturer gate.
    if abs(err)>5.0:
        raise SystemExit("FAIL: dynamic EF86 midband gain moved outside provisional tolerance")

    if not all(math.isfinite(r["gain"]) and math.isfinite(r["thd"]) for _,r in rows):
        raise SystemExit("FAIL: non-finite EF86 dynamic measurement")

    print("PASS: first dynamic EF86 offline reference is finite and preserves Philips midband gain.")
    print("WARNING: g1 input coupling/grid-leak network intentionally omitted until Rg1 is sourced.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
