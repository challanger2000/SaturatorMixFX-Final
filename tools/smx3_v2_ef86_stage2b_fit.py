#!/usr/bin/env python3
"""Stage-2B EF86 coupled plate/screen-knee fit for SMX-3 V2.

Stage-1 transfer-surface parameters are frozen.

Stage 2B adds only:
- a normalized low-Va plate-current knee;
- a complementary screen-current dependence on that knee.

Rationale:
in a real pentode, as plate voltage enters the knee and plate collection
weakens, screen-grid current may increase. This is more physical than an
independent arbitrary screen-current power law.

Large-signal 5%-THD and Graph-D data are still excluded from the objective.

Standard library only.
"""

import csv
import math
import pathlib
import random

ROOT=pathlib.Path(__file__).resolve().parents[1]
GRAPHB=ROOT/"research"/"ef86_philips1956_platecurve_provisional.csv"

PLATE={
    "MU":42.1294068459,
    "EX":1.48016674106,
    "KG1":2059.06189749,
    "KP":215.816749098,
    "VCT":0.761562843483,
    "KVB_SCREEN":430.818432714,
    "LAMBDA":0.000160501489918,
}

RA=100000.0
RG2=390000.0
RK=1000.0
RGLOAD=330000.0

PHILIPS={
    200.0:{"ik":0.00170,"gain":106.0},
    250.0:{"ik":0.00210,"gain":112.0},
    300.0:{"ik":0.00250,"gain":116.0},
    350.0:{"ik":0.00290,"gain":120.0},
    400.0:{"ik":0.00330,"gain":124.0},
}

# KNEE, KNEE2, KG2, KVC
BOUNDS=[
    (5.0,120.0),
    (1.0,80.0),
    (500.0,20000.0),
    (1.7,5.0),
]
NAMES=["KNEE","KNEE2","KG2","KVC"]


def l1p(x):
    if x>50.0:return x
    if x<-50.0:return math.exp(x)
    return math.log1p(math.exp(x))


def activation(vg2,vg1):
    p=PLATE
    if vg2<=0.0:
        return 0.0
    denom=math.sqrt(p["KVB_SCREEN"]+vg2*vg2)
    z=(1.0/p["MU"]+(p["VCT"]+vg1)/denom)*p["KP"]
    e1=vg2/p["KP"]*l1p(z)
    return 2.0*max(e1,0.0)**p["EX"]


def base_ia(va,vg2,vg1):
    p=PLATE
    e2=activation(vg2,vg1)
    slope=max(0.1,1.0+p["LAMBDA"]*(va-250.0))
    return e2/p["KG1"]*slope


def knee_raw(va,p):
    KNEE,KNEE2,_,_=p
    if va<=0.0:
        return 0.0
    return math.atan(va/KNEE)*math.tanh(va/KNEE2)


def knee_norm(va,p):
    ref=knee_raw(250.0,p)
    return knee_raw(va,p)/ref if ref>1e-15 else 0.0


def ia(va,vg2,vg1,p):
    return max(0.0,base_ia(va,vg2,vg1)*knee_norm(va,p))


def ig2(va,vg2,vg1,p):
    _,_,KG2,KVC=p
    e2=activation(vg2,vg1)
    k=knee_raw(va,p)
    # Complementary collection behavior: screen current grows as the plate
    # factor falls. Require positivity by construction.
    factor=max(KVC-k,0.0)
    return e2/KG2*factor


def solve_dc(vb,p):
    vp=0.35*vb
    vs=0.50*vb
    vk=2.0

    for _ in range(60000):
        ia0=ia(vp-vk,vs-vk,-vk,p)
        ig20=ig2(vp-vk,vs-vk,-vk,p)

        tvp=vb-ia0*RA
        tvs=vb-ig20*RG2
        tvk=(ia0+ig20)*RK

        if max(abs(tvp-vp),abs(tvs-vs),abs(tvk-vk))<1e-11:
            return vp,vs,vk,ia0,ig20

        d=0.06
        vp=(1-d)*vp+d*tvp
        vs=(1-d)*vs+d*tvs
        vk=(1-d)*vk+d*tvk

    raise RuntimeError("DC solver failed")


def small_gain(dc,p):
    vp,vs,vk,ia0,_=dc
    rload=1.0/(1.0/RA+1.0/RGLOAD)
    vth=vp+ia0*rload

    def solve(vin):
        x=vp
        for _ in range(30000):
            i=ia(x-vk,vs-vk,vin-vk,p)
            target=vth-i*rload
            if abs(target-x)<1e-11:
                return x
            x=0.82*x+0.18*target
        raise RuntimeError("AC plate solve failed")

    dv=1e-5
    return (solve(dv)-solve(-dv))/(2.0*dv)


GRAPHB_POINTS=list(csv.DictReader(GRAPHB.open(encoding="utf-8")))


def derivative(fn,x,h):
    return (fn(x+h)-fn(x-h))/(2.0*h)


def objective(p):
    try:
        ss=0.0
        n=0

        # Exact/typical device screen-current anchor.
        g2=ig2(250.0,140.0,-2.0,p)
        ss+=((g2-0.0006)/0.00003)**2
        n+=1

        # Preserve typical plate resistance around the exact device point.
        gp=derivative(lambda va: ia(va,140.0,-2.0,p),250.0,1e-2)
        ss+=((gp-4.0e-7)/1.0e-7)**2
        n+=1

        # Preserve provisional Philips Graph-B plate-current surface.
        for r in GRAPHB_POINTS:
            va=float(r["va_v"])
            vg=float(r["curve_vg1_v"])
            ref=float(r["ia_ma"])*1e-3
            u=float(r["uncertainty_ma"])*1e-3
            m=ia(va,140.0,vg,p)
            ss+=((m-ref)/u)**2
            n+=1

        # Exact manufacturer amplifier current/gain table.
        for vb,t in PHILIPS.items():
            dc=solve_dc(vb,p)
            ik=dc[3]+dc[4]
            g=abs(small_gain(dc,p))

            ss+=((ik-t["ik"])/0.00005)**2
            ss+=((g-t["gain"])/2.0)**2
            n+=2

        return ss/n
    except (RuntimeError,OverflowError,ValueError,ZeroDivisionError):
        return 1e30


def random_vec(rng):
    return [rng.uniform(lo,hi) for lo,hi in BOUNDS]


def clip(v):
    return [max(lo,min(hi,x)) for x,(lo,hi) in zip(v,BOUNDS)]


def de(seed=314, popsize=52, generations=150, F=0.72, CR=0.86):
    rng=random.Random(seed)
    pop=[random_vec(rng) for _ in range(popsize)]
    scores=[objective(v) for v in pop]

    for gen in range(generations):
        for i in range(popsize):
            ids=[j for j in range(popsize) if j!=i]
            a,b,c=rng.sample(ids,3)
            mutant=clip([
                pop[a][d]+F*(pop[b][d]-pop[c][d])
                for d in range(len(BOUNDS))
            ])
            jrand=rng.randrange(len(BOUNDS))
            trial=[
                mutant[d] if (rng.random()<CR or d==jrand) else pop[i][d]
                for d in range(len(BOUNDS))
            ]
            s=objective(trial)
            if s<scores[i]:
                pop[i]=trial
                scores[i]=s

        if gen%20==0 or gen==generations-1:
            j=min(range(popsize),key=lambda k:scores[k])
            print(f"generation {gen:3d}: NRMS={math.sqrt(scores[j]):.6f} sigma")

    j=min(range(popsize),key=lambda k:scores[k])
    return pop[j],scores[j]


def main():
    print("SMX-3 V2 EF86 Stage-2B coupled knee/screen fit")
    print("Stage-1 transfer surface frozen; large-signal envelope excluded.")
    print()

    p,s=de()

    print()
    print("BEST STAGE-2B PARAMETERS")
    for name,v,(lo,hi) in zip(NAMES,p,BOUNDS):
        frac=(v-lo)/(hi-lo)
        print(f"{name}={v:.12g}  bound_fraction={frac:.6f}")

    print(f"objective NRMS={math.sqrt(s):.6f} sigma")

    print()
    print(f"device Ig2={ig2(250.0,140.0,-2.0,p)*1e3:.9f} mA vs 0.600000000")

    gp=derivative(lambda va: ia(va,140.0,-2.0,p),250.0,1e-2)
    print(f"device ri={(1.0/gp)/1e6:.9f} MOhm" if gp>0 else "device ri=infinite")

    print("Vb,Ik_mA,target_Ik_mA,Ik_err_pct,gain,target_gain,gain_err_pct,Va_node,Vg2_node,Vk")
    max_i=max_g=0.0

    for vb in sorted(PHILIPS):
        dc=solve_dc(vb,p)
        ik=dc[3]+dc[4]
        g=abs(small_gain(dc,p))
        ti=PHILIPS[vb]["ik"]
        tg=PHILIPS[vb]["gain"]
        ei=100.0*(ik-ti)/ti
        eg=100.0*(g-tg)/tg
        max_i=max(max_i,abs(ei))
        max_g=max(max_g,abs(eg))
        print(
            f"{vb:.0f},{ik*1e3:.9f},{ti*1e3:.9f},{ei:+.6f},"
            f"{g:.9f},{tg:.9f},{eg:+.6f},"
            f"{dc[0]:.6f},{dc[1]:.6f},{dc[2]:.6f}"
        )

    ss=0.0
    worst=0.0
    for r in GRAPHB_POINTS:
        va=float(r["va_v"]); vg=float(r["curve_vg1_v"])
        ref=float(r["ia_ma"])*1e-3
        u=float(r["uncertainty_ma"])*1e-3
        z=(ia(va,140.0,vg,p)-ref)/u
        ss+=z*z
        worst=max(worst,abs(z))
    graphb_nrms=math.sqrt(ss/len(GRAPHB_POINTS))

    print()
    print(f"Graph B NRMS={graphb_nrms:.6f} sigma worst={worst:.6f} sigma")
    print(f"max |Ik error|={max_i:.6f}%")
    print(f"max |gain error|={max_g:.6f}%")

    near=[]
    for name,v,(lo,hi) in zip(NAMES,p,BOUNDS):
        frac=(v-lo)/(hi-lo)
        if frac<0.02 or frac>0.98:
            near.append((name,frac))

    if near:
        print("IDENTIFIABILITY WARNING:")
        for name,frac in near:
            print(f" - {name} near bound ({frac:.4f})")
    else:
        print("No Stage-2B parameter is within 2% of an arbitrary bound.")

    return 0


if __name__=="__main__":
    raise SystemExit(main())
