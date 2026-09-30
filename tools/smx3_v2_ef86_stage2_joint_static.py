#!/usr/bin/env python3
"""EF86 Stage-2 joint static candidate for SMX-3 V2.

This candidate is fitted jointly against:
- Philips Graph A;
- Philips Graph B;
- exact Ia / Ig2 / gm / Ri device anchors;
- Philips circuit-1 Ik(Vb);
- Philips circuit-1 small-signal gain(Vb).

It intentionally does NOT include the Stage-3 large-signal knee correction.

Standard library only.
"""

import csv
import math
import pathlib

ROOT=pathlib.Path(__file__).resolve().parents[1]
GRAPHA=ROOT/"research"/"ef86_philips_graphA_provisional.csv"
GRAPHB=ROOT/"research"/"ef86_philips1956_platecurve_provisional.csv"
GRAPHB_KNEE=ROOT/"research"/"ef86_philips1956_platecurve_knee_provisional.csv"

P={
    "MU":43.5037280,
    "KG1":2037.16212,
    "KP":197.039407,
    "KVB":277.241979,
    "VCT":0.389775431,
    "EX":1.25081541,
    "KNEE":6.01238680,
    "KNEE2":0.513422804,
    "KNEX":0.0190330750,
    "KLAMG":7.46640006e-5,
    "KG2":10172.0319,
    "KVC":8.49508970,
    "SCREEN_BETA":0.200667665,
    "SCREEN_LAMBDA":7.50398016e-8,
}

RA=100000.0
RG2=390000.0
RK=1000.0
RGLOAD=330000.0

SWEEP={
    200.0:(0.00170,106.0),
    250.0:(0.00210,112.0),
    300.0:(0.00250,116.0),
    350.0:(0.00290,120.0),
    400.0:(0.00330,124.0),
}


def l1p(x):
    if x>50.0:return x
    if x<-50.0:return math.exp(x)
    return math.log1p(math.exp(x))


def currents(vp,vg2,vg1):
    if vp<=0.0 or vg2<=1e-12:
        return 0.0,0.0

    z=(1.0/P["MU"]+(P["VCT"]+vg1)/math.sqrt(P["KVB"]+vg2*vg2))*P["KP"]
    e1=vg2/P["KP"]*l1p(z)
    e2=2.0*max(e1,0.0)**P["EX"]

    knee=math.atan((vp+P["KNEX"])/P["KNEE"])*math.tanh(vp/P["KNEE2"])

    ia=max(
        e2/P["KG1"]*knee*(1.0+P["KLAMG"]*vp),
        0.0,
    )

    ig2=max(
        e2/P["KG2"]
        * max(P["KVC"]-knee,0.0)**P["SCREEN_BETA"]
        / (1.0+P["SCREEN_LAMBDA"]*vp),
        0.0,
    )

    return ia,ig2


def solve_dc(vb):
    vp=0.3*vb
    vs=0.45*vb
    vk=2.0

    for _ in range(30000):
        ia,ig2=currents(vp-vk,vs-vk,-vk)

        a=vb-ia*RA
        s=vb-ig2*RG2
        k=(ia+ig2)*RK

        if max(abs(a-vp),abs(s-vs),abs(k-vk))<1e-10:
            return vp,vs,vk,ia,ig2

        d=0.05
        vp=(1.0-d)*vp+d*a
        vs=(1.0-d)*vs+d*s
        vk=(1.0-d)*vk+d*k

    raise RuntimeError("DC solve failed")


def small_gain(dc):
    vp,vs,vk,ia0,_=dc
    rload=1.0/(1.0/RA+1.0/RGLOAD)
    vth=vp+ia0*rload

    def solve(vin):
        x=vp
        for _ in range(10000):
            ia,_=currents(x-vk,vs-vk,vin-vk)
            target=vth-ia*rload
            if abs(target-x)<1e-10:
                return x
            x=0.8*x+0.2*target
        raise RuntimeError("AC solve failed")

    dv=1e-5
    return (solve(dv)-solve(-dv))/(2.0*dv)


def graph_score(path,mode):
    rows=list(csv.DictReader(path.open(encoding="utf-8")))
    sigmas=[]

    for r in rows:
        if mode=="A":
            m=currents(250.0,float(r["vg2_v"]),float(r["vg1_v"]))[0]*1e3
            y=float(r["ia_ma"])
            u=float(r["uncertainty_ma"])
        else:
            m=currents(float(r["va_v"]),140.0,float(r["curve_vg1_v"]))[0]*1e3
            y=float(r["ia_ma"])
            u=float(r["uncertainty_ma"])
        sigmas.append((m-y)/u)

    return (
        math.sqrt(sum(s*s for s in sigmas)/len(sigmas)),
        max(abs(s) for s in sigmas),
    )


def main():
    ia0,ig20=currents(250.0,140.0,-2.0)

    dv=1e-4
    gm=(currents(250.0,140.0,-2.0+dv)[0]
        -currents(250.0,140.0,-2.0-dv)[0])/(2.0*dv)

    dva=0.1
    gop=(currents(250.0+dva,140.0,-2.0)[0]
         -currents(250.0-dva,140.0,-2.0)[0])/(2.0*dva)
    ri=1.0/gop

    ar,aw=graph_score(GRAPHA,"A")
    br,bw=graph_score(GRAPHB,"B")
    kr,kw=graph_score(GRAPHB_KNEE,"B")

    print("SMX-3 V2 EF86 Stage-2 joint static candidate")
    print(f"Ia={ia0*1e3:.9f} mA target 3.000")
    print(f"Ig2={ig20*1e3:.9f} mA target 0.600")
    print(f"gm={gm*1e3:.9f} mA/V target 2.000")
    print(f"Ri={ri/1e6:.9f} MOhm target 2.500")
    print(f"Graph A NRMS={ar:.6f} sigma worst={aw:.6f}")
    print(f"Graph B plateau NRMS={br:.6f} sigma worst={bw:.6f}")
    print(f"Graph B knee NRMS={kr:.6f} uncertainty-units worst={kw:.6f}")
    print()
    print("Vb,Ik_mA,target_Ik_mA,gain,target_gain")

    worst_i=0.0
    worst_g=0.0
    for vb in sorted(SWEEP):
        dc=solve_dc(vb)
        ik=dc[3]+dc[4]
        g=abs(small_gain(dc))
        ti,tg=SWEEP[vb]
        worst_i=max(worst_i,abs(100.0*(ik-ti)/ti))
        worst_g=max(worst_g,abs(100.0*(g-tg)/tg))
        print(f"{vb:.0f},{ik*1e3:.9f},{ti*1e3:.9f},{g:.9f},{tg:.9f}")

    print()
    print(f"worst Ik error={worst_i:.6f}%")
    print(f"worst gain error={worst_g:.6f}%")

    if ar>1.25 or br>1.25:
        raise SystemExit("FAIL: Philips Graph A/B plateau surface")
    if kr>1.25:
        raise SystemExit("FAIL: Philips Graph-B low-Va knee surface")
    if abs((ia0-0.003)/0.003)>0.03:
        raise SystemExit("FAIL: Ia anchor")
    if abs((ig20-0.0006)/0.0006)>0.10:
        raise SystemExit("FAIL: Ig2 anchor")
    if abs((gm-0.002)/0.002)>0.05:
        raise SystemExit("FAIL: gm anchor")
    if abs((ri-2.5e6)/2.5e6)>0.10:
        raise SystemExit("FAIL: Ri anchor")
    if worst_i>5.0:
        raise SystemExit("FAIL: Ik sweep")
    if worst_g>5.0:
        raise SystemExit("FAIL: gain sweep")

    print("PASS: Stage-2 joint static EF86 candidate clears current multi-domain static gates.")


if __name__=="__main__":
    raise SystemExit(main())
