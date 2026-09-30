#!/usr/bin/env python3
"""Stage-1 EF86 transfer-surface fit for SMX-3 V2.

Goal:
identify the CONTROL-GRID / SCREEN-GRID / high-plate-voltage current surface
before any large-signal knee/kink fitting.

Primary/provisional data:
- Philips Graph A screen-voltage families;
- Philips Graph B high-plate-voltage families;
- exact typical device Ia and gm anchors;
- typical internal plate resistance (2.5 MOhm -> dIa/dVa ~= 0.4 uA/V).

Large-signal Vo@5% and Graph D are intentionally NOT in this objective.

The optimizer is a deterministic standard-library differential-evolution
implementation. No third-party fit parameters are used as targets.

This is a research fit, not production DSP.
"""

import csv
import math
import pathlib
import random

ROOT=pathlib.Path(__file__).resolve().parents[1]
GRAPHA=ROOT/"research"/"ef86_philips_graphA_provisional.csv"
GRAPHB=ROOT/"research"/"ef86_philips1956_platecurve_provisional.csv"

# Parameter order:
# MU, EX, KG1, KP, VCT, KVB_SCREEN, LAMBDA
BOUNDS=[
    (20.0,80.0),       # MU
    (1.00,1.70),       # EX
    (300.0,6000.0),    # KG1
    (30.0,600.0),      # KP
    (-1.0,1.0),        # VCT
    (1.0,3000.0),      # KVB_SCREEN
    (0.0,8.0e-4),      # linear high-Va plate slope term
]

NAMES=["MU","EX","KG1","KP","VCT","KVB_SCREEN","LAMBDA"]


def l1p(x):
    if x>50.0:return x
    if x<-50.0:return math.exp(x)
    return math.log1p(math.exp(x))


def ia_model(p,va,vg2,vg1):
    MU,EX,KG1,KP,VCT,KVB,LAM=p
    if vg2<=0.0 or va<=0.0:
        return 0.0

    denom=math.sqrt(KVB+vg2*vg2)
    z=(1.0/MU+(VCT+vg1)/denom)*KP
    e1=vg2/KP*l1p(z)

    # Normalize the asymptotic plate factor out of Stage 1. The future knee
    # stage will provide the low-Va saturation transition explicitly.
    base=2.0*max(e1,0.0)**EX/KG1

    slope=max(0.1,1.0+LAM*(va-250.0))
    return base*slope


def derivative(fn,x,h):
    return (fn(x+h)-fn(x-h))/(2.0*h)


def load_points():
    points=[]

    for r in csv.DictReader(GRAPHA.open(encoding="utf-8")):
        points.append((
            250.0,
            float(r["vg2_v"]),
            float(r["vg1_v"]),
            float(r["ia_ma"])*1e-3,
            float(r["uncertainty_ma"])*1e-3,
            "A",
        ))

    for r in csv.DictReader(GRAPHB.open(encoding="utf-8")):
        points.append((
            float(r["va_v"]),
            140.0,
            float(r["curve_vg1_v"]),
            float(r["ia_ma"])*1e-3,
            float(r["uncertainty_ma"])*1e-3,
            "B",
        ))

    return points


POINTS=load_points()


def objective(p):
    try:
        ss=0.0
        n=0

        for va,vg2,vg1,ref,u,_ in POINTS:
            m=ia_model(p,va,vg2,vg1)
            if not math.isfinite(m) or m<0.0:
                return 1e30
            s=(m-ref)/u
            ss+=s*s
            n+=1

        # Exact/typical device anchors at 250/140/-2.
        ia=ia_model(p,250.0,140.0,-2.0)
        ss+=((ia-0.0030)/0.00005)**2
        n+=1

        gm=derivative(lambda vg: ia_model(p,250.0,140.0,vg),-2.0,1e-4)
        ss+=((gm-0.0020)/0.00010)**2
        n+=1

        # ri ~= 2.5 MOhm -> dIa/dVa ~= 0.4 uA/V.
        gp=derivative(lambda va: ia_model(p,va,140.0,-2.0),250.0,1e-2)
        ss+=((gp-4.0e-7)/1.0e-7)**2
        n+=1

        return ss/n
    except (OverflowError,ValueError,ZeroDivisionError):
        return 1e30


def random_vec(rng):
    return [rng.uniform(lo,hi) for lo,hi in BOUNDS]


def clip_vec(v):
    return [max(lo,min(hi,x)) for x,(lo,hi) in zip(v,BOUNDS)]


def differential_evolution(seed=125, popsize=56, generations=140, F=0.72, CR=0.86):
    rng=random.Random(seed)
    pop=[random_vec(rng) for _ in range(popsize)]
    scores=[objective(v) for v in pop]

    for gen in range(generations):
        for i in range(popsize):
            candidates=[j for j in range(popsize) if j!=i]
            a,b,c=rng.sample(candidates,3)

            mutant=[
                pop[a][d]+F*(pop[b][d]-pop[c][d])
                for d in range(len(BOUNDS))
            ]
            mutant=clip_vec(mutant)

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
            best=min(range(popsize),key=lambda j:scores[j])
            print(f"generation {gen:3d}: normalized RMS={math.sqrt(scores[best]):.6f} sigma")

    best=min(range(popsize),key=lambda j:scores[j])
    return pop[best],scores[best]


def summarize(p):
    print()
    print("BEST PARAMETERS")
    for name,value,(lo,hi) in zip(NAMES,p,BOUNDS):
        frac=(value-lo)/(hi-lo)
        print(f"{name}={value:.12g}  bound_fraction={frac:.6f}")

    print()
    print(f"normalized RMS objective={math.sqrt(objective(p)):.6f} sigma")

    ia=ia_model(p,250.0,140.0,-2.0)
    gm=derivative(lambda vg: ia_model(p,250.0,140.0,vg),-2.0,1e-4)
    gp=derivative(lambda va: ia_model(p,va,140.0,-2.0),250.0,1e-2)

    print(f"Ia(250,140,-2)={ia*1e3:.9f} mA")
    print(f"gm={gm*1e3:.9f} mA/V")
    print(f"ri={1.0/gp/1e6:.9f} MOhm" if gp>0 else "ri=infinite")

    for family in ("A","B"):
        residuals=[]
        for va,vg2,vg1,ref,u,src in POINTS:
            if src!=family:continue
            residuals.append((ia_model(p,va,vg2,vg1)-ref)/u)
        rms=math.sqrt(sum(s*s for s in residuals)/len(residuals))
        worst=max(abs(s) for s in residuals)
        print(f"Graph {family}: NRMS={rms:.6f} sigma worst={worst:.6f} sigma")

    # Identifiability warning for parameters hugging arbitrary bounds.
    near=[]
    for name,value,(lo,hi) in zip(NAMES,p,BOUNDS):
        frac=(value-lo)/(hi-lo)
        if frac<0.02 or frac>0.98:
            near.append((name,frac))

    if near:
        print("IDENTIFIABILITY WARNING: parameters near search bounds:")
        for name,frac in near:
            print(f" - {name}: {frac:.4f}")
    else:
        print("No fitted parameter is within 2% of an arbitrary search bound.")


def main():
    print("SMX-3 V2 EF86 Stage-1 transfer-surface fit")
    print(f"points: {len(POINTS)} provisional/manufacturer current samples + 3 device anchors")
    print("Large-signal/knee data intentionally excluded.")
    print()

    p,s=differential_evolution()
    summarize(p)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
