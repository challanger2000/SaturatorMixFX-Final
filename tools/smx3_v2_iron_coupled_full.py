#!/usr/bin/env python3
"""Coupled magnetic + HF-parasitic offline reference for SMX-3 V2 IRON.

States:
- H, M: Jiles-Atherton magnetic state
- Vp: primary winding node voltage
- Ilk: leakage-branch current
- Vs: secondary winding node voltage

Topology:
source -> (Rs=600 + Rp=1.45k) -> primary node
primary node -> magnetic branch (H/KI)
primary node -> Cp=98 pF to shield
primary node -> Llk -> secondary node
secondary node -> (Rsec=1.55k + RL=10k) to ground
secondary node -> (Cs=110 pF + effective Cx) to shield

The output is the voltage across RL within the secondary resistive branch.

This is an OFFLINE research authority, not production DSP.
"""

import math
import cmath
import smx3_v2_iron_candidate as mag

RSER=mag.RSOURCE+mag.RP
RLOAD=mag.RSEC+mag.RL
CP=98e-12
CS=110e-12
LLK=2.756645114219e-3
CX=1.155036777196e-9
CSEC=CS+CX

# Newton normalization scales. The five states differ by many orders of
# magnitude; solving the raw residual with one absolute tolerance is poorly
# conditioned and can report false non-convergence.
STATE_SCALE=(100.0,3.0e5,10.0,1.0e-3,10.0)


def deriv(t,state,amp,freq):
    H,M,Vp,Ilk,Vsec=state

    vin=amp*math.sin(2.0*math.pi*freq*t)

    # Magnetic constitutive state. Direction follows the applied magnetic
    # voltage because dH/dt has the same sign while the differential
    # permeability remains positive in the accepted operating region.
    direction=1.0 if Vp>=0.0 else -1.0
    slope=mag.dmdh(H,M,direction)
    dH=Vp/(mag.KPHI*(1.0+slope))
    dM=slope*dH

    # Primary KCL:
    # (vin - Vp)/Rser = H/KI + Ilk + Cp*dVp/dt
    im=H/mag.KI
    dVp=((vin-Vp)/RSER-im-Ilk)/CP

    # Leakage branch and secondary shunt dynamics.
    dIlk=(Vp-Vsec)/LLK
    dVsec=(Ilk-Vsec/RLOAD)/CSEC

    return (dH,dM,dVp,dIlk,dVsec)


def solve_linear(A,b):
    n=len(A)
    m=[A[i][:]+[b[i]] for i in range(n)]
    for col in range(n):
        pivot_row=max(range(col,n),key=lambda r:abs(m[r][col]))
        m[col],m[pivot_row]=m[pivot_row],m[col]
        pivot=m[col][col]
        if abs(pivot)<1e-30:
            raise RuntimeError("singular coupled IRON Newton matrix")
        for j in range(col,n+1):
            m[col][j]/=pivot
        for r in range(n):
            if r==col:
                continue
            q=m[r][col]
            for j in range(col,n+1):
                m[r][j]-=q*m[col][j]
    return [m[i][n] for i in range(n)]


def trapezoid_step(t,x,dt,amp,freq):
    f0=deriv(t,x,amp,freq)

    # Work in dimensionless Newton coordinates y=z/scale.
    y=[x[i]/STATE_SCALE[i] for i in range(5)]

    def physical(yy):
        return [yy[i]*STATE_SCALE[i] for i in range(5)]

    def residual(yy):
        z=physical(yy)
        f1=deriv(t+dt,z,amp,freq)
        return [
            (z[i]-x[i]-0.5*dt*(f0[i]+f1[i]))/STATE_SCALE[i]
            for i in range(5)
        ]

    for iteration in range(18):
        F=residual(y)

        if max(abs(v) for v in F)<1e-9:
            return tuple(physical(y)),iteration

        J=[[0.0]*5 for _ in range(5)]
        for j in range(5):
            eps=1e-7*max(1.0,abs(y[j]))
            yy=y[:]
            yy[j]+=eps
            FF=residual(yy)
            for i in range(5):
                J[i][j]=(FF[i]-F[i])/eps

        delta=solve_linear(J,[-v for v in F])

        # Conservative Newton damping if a full step increases the residual.
        base=max(abs(v) for v in F)
        step=1.0
        accepted=False
        for _ in range(8):
            trial=[y[i]+step*delta[i] for i in range(5)]
            Ft=residual(trial)
            if max(abs(v) for v in Ft)<base:
                y=trial
                accepted=True
                break
            step*=0.5

        if not accepted:
            # The solution may already be close enough that finite-difference
            # noise prevents a strict decrease. Accept only under a looser but
            # still tiny normalized residual; otherwise report the real failure.
            if base<1e-7:
                return tuple(physical(y)),iteration+1
            raise RuntimeError(
                f"coupled IRON Newton line search failed at t={t:.9g}s "
                f"residual={base:.9g}"
            )

        if max(abs(step*d) for d in delta)<1e-9:
            return tuple(physical(y)),iteration+1

    final=max(abs(v) for v in residual(y))
    raise RuntimeError(
        f"coupled IRON Newton solver did not converge at t={t:.9g}s "
        f"residual={final:.9g}"
    )


def analyze(y,freq,fs):
    N=len(y)
    def component(h):
        re=0.0; im=0.0
        for i,v in enumerate(y):
            a=2.0*math.pi*h*freq*i/fs
            re+=v*math.cos(a)
            im-=v*math.sin(a)
        return 2.0*complex(re,-im)/N

    comps=[component(h) for h in range(1,11)]
    fund=abs(comps[0])
    hs=[abs(c)/fund for c in comps[1:]]
    thd=math.sqrt(sum(h*h for h in hs))
    rms=math.sqrt(sum(v*v for v in y)/N)
    phase=math.degrees(cmath.phase(comps[0]))
    return rms,fund,phase,thd,hs


def simulate(level_dbu,freq,fs=None,warmup_cycles=40,analysis_cycles=4):
    # Implicit trapezoid handles the stiff pF network without requiring an
    # explicit-step rate above its fastest RC pole. Keep at least 32 samples
    # per fundamental at HF and 96 kHz at LF; convergence is checked separately.
    if fs is None:
        fs=max(96000.0,32.0*freq)

    vrms=0.775*10.0**(level_dbu/20.0)
    amp=vrms*math.sqrt(2.0)
    dt=1.0/fs

    total_cycles=warmup_cycles+analysis_cycles
    n=int(round(total_cycles*fs/freq))
    start=int(round(warmup_cycles*fs/freq))

    x=(0.0,0.0,0.0,0.0,0.0)
    out=[]

    max_newton=0
    for i in range(n):
        x,it=trapezoid_step(i*dt,x,dt,amp,freq)
        max_newton=max(max_newton,it)
        if not all(math.isfinite(v) for v in x):
            raise RuntimeError("non-finite coupled IRON state")
        if i>=start:
            out.append(x[4]*mag.RL/RLOAD)

    return (*analyze(out,freq,fs),max_newton)


def main():
    print("SMX-3 V2 coupled IRON magnetic + HF-parasitic reference")
    print(f"Lm target={mag.LM_TARGET:.6f} H c={mag.P['c']:.6f} KI={mag.KI:.6f}")
    print(f"Cp={CP*1e12:.3f}pF Llk={LLK*1e3:.6f}mH Csec_total={CSEC*1e12:.3f}pF")
    print()

    # Low-level magnitude reference. +4 dBu is the documented response-test
    # level; nonlinear contribution is tiny enough to compare directly.
    print("+4 dBu frequency response")
    base=None
    rows=[]
    for f in (20.0,1000.0,20000.0,95000.0):
        rms,fund,phase,thd,hs,max_newton=simulate(4.0,f)
        if f==1000.0:
            base=fund
        rows.append((f,rms,fund,phase,thd,max_newton))

    # base is known now; print relative fundamental magnitude.
    for f,rms,fund,phase,thd,max_newton in rows:
        rel=20.0*math.log10(fund/base)
        print(f"{f:.1f}Hz rel={rel:.9f}dB phase={phase:.6f}deg THD={100*thd:.9f}% NewtonMax={max_newton}")

    print()
    print("20 Hz nonlinear anchors")
    anchors={}
    for level in (4.0,20.0):
        rms,fund,phase,thd,hs,max_newton=simulate(level,20.0)
        anchors[level]=100.0*thd
        print(
            f"{level:+.1f}dBu THD={100*thd:.9f}% "
            f"H2={100*hs[0]:.9f}% H3={100*hs[1]:.9f}%"
        )

    # Frozen first coupled-model gates.
    rels={f:20.0*math.log10(fund/base) for f,_,fund,_,_,_ in rows}
    if abs(rels[20.0]-(-0.04))>0.015:
        raise SystemExit("FAIL: coupled model misses 20 Hz magnitude anchor")
    if abs(rels[20000.0]-(-0.05))>0.015:
        raise SystemExit("FAIL: coupled model misses 20 kHz magnitude anchor")
    if abs(rels[95000.0]-(-3.0))>0.15:
        raise SystemExit("FAIL: coupled model misses 95 kHz bandwidth")
    if abs(anchors[4.0]-0.025)>0.006:
        raise SystemExit("FAIL: coupled model misses +4 dBu / 20 Hz THD")
    if abs(anchors[20.0]-1.0)>0.06:
        raise SystemExit("FAIL: coupled model misses +20 dBu / 20 Hz THD")

    print()
    print("PASS: first coupled magnetic/parasitic IRON reference preserves magnitude and nonlinear anchors.")
    print("WARNING: DLP/phase, source/load variants and numerical cross-method still gate promotion.")


if __name__=="__main__":
    raise SystemExit(main())
