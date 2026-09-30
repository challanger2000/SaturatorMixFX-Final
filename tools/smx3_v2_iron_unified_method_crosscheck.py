#!/usr/bin/env python3
"""Independent numerical-method cross-check for frozen unified IRON candidate.

Compares:
- RK4 @ 48 kHz
- explicit midpoint/RK2 @ 192 kHz

All cases use full 120-cycle settling.
"""

import math
import smx3_v2_iron_unified_candidate as ref


def midpoint_step(t,H,M,I,dt,source):
    v1=source(t)
    k1h,k1m,k1i,_,_=ref.deriv_source(H,M,I,v1)

    tm=t+0.5*dt
    vm=source(tm)
    hm=H+0.5*dt*k1h
    mm=M+0.5*dt*k1m
    im=I+0.5*dt*k1i

    k2h,k2m,k2i,_,_=ref.deriv_source(hm,mm,im,vm)

    H2=H+dt*k2h
    M2=M+dt*k2m
    I2=I+dt*k2i

    ve=source(t+dt)
    _,_,_,vo,_=ref.deriv_source(H2,M2,I2,ve)
    return H2,M2,I2,vo


def simulate_mid(level_dbu,freq,fs=192000.0,warmup=120,analysis=6):
    vrms=0.775*10.0**(level_dbu/20.0)
    amp=vrms*math.sqrt(2.0)
    source=lambda t:amp*math.sin(2.0*math.pi*freq*t)
    dt=1.0/fs
    n=int(round((warmup+analysis)*fs/freq))
    start=int(round(warmup*fs/freq))

    H=M=I=0.0
    y=[]
    for idx in range(n):
        H,M,I,vo=midpoint_step(idx*dt,H,M,I,dt,source)
        if idx>=start:
            y.append(vo)

    def comp(h):
        re=im=0.0
        for i,v in enumerate(y):
            a=2.0*math.pi*h*freq*i/fs
            re+=v*math.cos(a)
            im-=v*math.sin(a)
        return math.hypot(re,im)

    f1=comp(1)
    hs=[comp(h)/f1 for h in range(2,11)]
    thd=math.sqrt(sum(x*x for x in hs))
    return thd,hs,H,M,I


def main():
    print("SMX-3 V2 unified IRON numerical-method cross-check")
    print("case,RK4_THD_pct,midpoint_THD_pct,THD_residual_pp,H3_residual_pp,Irel_residual_A")

    failures=[]
    for label,level,freq in (
        ("20Hz +4dBu",4.0,20.0),
        ("20Hz +20dBu",20.0,20.0),
        ("40Hz +4dBu",4.0,40.0),
    ):
        a=ref.simulate(level,freq,fs=48000.0,warmup_cycles=120,analysis_cycles=6)
        bthd,bhs,bH,bM,bI=simulate_mid(level,freq)

        dthd=100.0*abs(a["thd"]-bthd)
        dh3=100.0*abs(a["hs"][1]-bhs[1])
        di=abs(a["irel"]-bI)

        print(
            f"{label},{100*a['thd']:.9f},{100*bthd:.9f},"
            f"{dthd:.9f},{dh3:.9f},{di:.12g}"
        )

        if dthd>0.003:
            failures.append(label+" THD residual")
        if dh3>0.003:
            failures.append(label+" H3 residual")
        if di>2e-7:
            failures.append(label+" relaxation-state residual")

    print()
    if failures:
        print("FAIL:")
        for x in failures:
            print(" - "+x)
        return 1

    print("PASS: unified three-state IRON reference is numerically invariant across RK4 and independent midpoint integration within frozen tolerances.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
