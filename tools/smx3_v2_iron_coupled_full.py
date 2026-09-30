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


def rk4_step(t,x,dt,amp,freq):
    k1=deriv(t,x,amp,freq)
    x2=tuple(x[i]+0.5*dt*k1[i] for i in range(5))
    k2=deriv(t+0.5*dt,x2,amp,freq)
    x3=tuple(x[i]+0.5*dt*k2[i] for i in range(5))
    k3=deriv(t+0.5*dt,x3,amp,freq)
    x4=tuple(x[i]+dt*k3[i] for i in range(5))
    k4=deriv(t+dt,x4,amp,freq)
    return tuple(
        x[i]+dt*(k1[i]+2.0*k2[i]+2.0*k3[i]+k4[i])/6.0
        for i in range(5)
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
    # The HF electrical network is much faster than the magnetic state.
    # Keep a generous fixed oversampling density for offline authority.
    if fs is None:
        fs=max(768000.0,256.0*freq)

    vrms=0.775*10.0**(level_dbu/20.0)
    amp=vrms*math.sqrt(2.0)
    dt=1.0/fs

    total_cycles=warmup_cycles+analysis_cycles
    n=int(round(total_cycles*fs/freq))
    start=int(round(warmup_cycles*fs/freq))

    x=(0.0,0.0,0.0,0.0,0.0)
    out=[]

    for i in range(n):
        x=rk4_step(i*dt,x,dt,amp,freq)
        if not all(math.isfinite(v) for v in x):
            raise RuntimeError("non-finite coupled IRON state")
        if i>=start:
            out.append(x[4]*mag.RL/RLOAD)

    return analyze(out,freq,fs)


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
        rms,fund,phase,thd,hs=simulate(4.0,f)
        if f==1000.0:
            base=fund
        rows.append((f,rms,fund,phase,thd))

    # base is known now; print relative fundamental magnitude.
    for f,rms,fund,phase,thd in rows:
        rel=20.0*math.log10(fund/base)
        print(f"{f:.1f}Hz rel={rel:.9f}dB phase={phase:.6f}deg THD={100*thd:.9f}%")

    print()
    print("20 Hz nonlinear anchors")
    anchors={}
    for level in (4.0,20.0):
        rms,fund,phase,thd,hs=simulate(level,20.0)
        anchors[level]=100.0*thd
        print(
            f"{level:+.1f}dBu THD={100*thd:.9f}% "
            f"H2={100*hs[0]:.9f}% H3={100*hs[1]:.9f}%"
        )

    # Frozen first coupled-model gates.
    rels={f:20.0*math.log10(fund/base) for f,_,fund,_,_ in rows}
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
