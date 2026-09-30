#!/usr/bin/env python3
"""Unified EF86 multi-domain scorecard for SMX-3 V2.

Compares current model families against the same Philips evidence:
- exact device anchor;
- provisional Graph A screen-family;
- provisional Graph B plate-family;
- exact circuit-1 DC current / small-signal gain sweep;
- exact Vo at 5% THD envelope over Vb=200..400 V.

This is INFORMATIONAL because Graph A/B are still provisional manual
manufacturer-graph digitizations. Exact tabular anchors remain authoritative.
"""

import csv, math, pathlib
import smx3_v2_ef86_provisional_fit as provisional
import smx3_v2_ef86_generalized_surrogate as generalized
import smx3_v2_ef86_extended_family_benchmark as extended

ROOT=pathlib.Path(__file__).resolve().parents[1]

GRAPH_A=ROOT/"research"/"ef86_philips_graphA_provisional.csv"
GRAPH_B=ROOT/"research"/"ef86_philips1956_platecurve_provisional.csv"
GRAPH_B_KNEE=ROOT/"research"/"ef86_philips1956_platecurve_knee_provisional.csv"

PHILIPS={
    200.0:{"ik":0.00170,"gain":106.0,"vo5":40.0},
    250.0:{"ik":0.00210,"gain":112.0,"vo5":50.0},
    300.0:{"ik":0.00250,"gain":116.0,"vo5":64.0},
    350.0:{"ik":0.00290,"gain":120.0,"vo5":75.0},
    400.0:{"ik":0.00330,"gain":124.0,"vo5":87.0},
}

DEVICE={"ia":0.0030,"ig2":0.0006,"gm":0.0020}

MODELS={
    "provisional":{
        "currents":provisional.currents,
        "solve_dc":provisional.solve_dc,
        "gain":lambda dc: abs(provisional.gain(dc)),
    },
    "generalized":{
        "currents":generalized.currents,
        "solve_dc":generalized.solve_dc,
        "gain":lambda dc: abs(generalized.small_gain(dc)),
    },
    "extended-community":{
        "currents":extended.currents,
        "solve_dc":extended.solve_dc,
        "gain":lambda dc: abs(extended.small_gain(dc)),
    },
}


def pct(v,r):
    return 100.0*(v-r)/r


def graph_a_score(currents):
    rows=list(csv.DictReader(GRAPH_A.open(encoding="utf-8")))
    sig=[]
    for r in rows:
        vg2=float(r["vg2_v"]); vg1=float(r["vg1_v"])
        ref=float(r["ia_ma"]); u=float(r["uncertainty_ma"])
        m=1e3*currents(250.0,vg2,vg1)[0]
        sig.append((m-ref)/u)
    return math.sqrt(sum(x*x for x in sig)/len(sig)),max(abs(x) for x in sig)


def graph_file_score(currents,path):
    rows=list(csv.DictReader(path.open(encoding="utf-8")))
    sig=[]
    for r in rows:
        vg1=float(r["curve_vg1_v"]); va=float(r["va_v"])
        ref=float(r["ia_ma"]); u=float(r["uncertainty_ma"])
        m=1e3*currents(va,140.0,vg1)[0]
        sig.append((m-ref)/u)
    return math.sqrt(sum(x*x for x in sig)/len(sig)),max(abs(x) for x in sig)


def graph_b_score(currents):
    return graph_file_score(currents,GRAPH_B)


def graph_b_knee_score(currents):
    return graph_file_score(currents,GRAPH_B_KNEE)


def device_score(currents):
    ia,ig2=currents(250.0,140.0,-2.0)
    dv=1e-4
    gm=(currents(250.0,140.0,-2.0+dv)[0]
        -currents(250.0,140.0,-2.0-dv)[0])/(2.0*dv)
    return {
        "ia_err":pct(ia,DEVICE["ia"]),
        "ig2_err":pct(ig2,DEVICE["ig2"]),
        "gm_err":pct(gm,DEVICE["gm"]),
    }


def dc_gain_score(model):
    ikerrs=[]; gerrs=[]
    for vb,t in PHILIPS.items():
        dc=model["solve_dc"](vb)
        ik=dc[3]+dc[4]
        g=model["gain"](dc)
        ikerrs.append(pct(ik,t["ik"]))
        gerrs.append(pct(g,t["gain"]))
    return {
        "ik_rms":math.sqrt(sum(x*x for x in ikerrs)/len(ikerrs)),
        "ik_worst":max(abs(x) for x in ikerrs),
        "gain_rms":math.sqrt(sum(x*x for x in gerrs)/len(gerrs)),
        "gain_worst":max(abs(x) for x in gerrs),
    }


def waveform_for(model,vb,vin_rms,n=512):
    currents=model["currents"]
    dc=model["solve_dc"](vb)
    vp,vs,vk,ia0,_=dc
    ra=100000.0
    rg=330000.0
    rload=1.0/(1.0/ra+1.0/rg)
    vth=vp+ia0*rload
    ys=[]

    for i in range(n):
        vin=vin_rms*math.sqrt(2.0)*math.sin(2.0*math.pi*i/n)
        x=vp
        for _ in range(12000):
            ia,_=currents(x-vk,vs-vk,vin-vk)
            target=vth-ia*rload
            if abs(target-x)<1e-10:
                break
            x=0.75*x+0.25*target
        ys.append(x)

    mean=sum(ys)/n
    ys=[y-mean for y in ys]
    out=math.sqrt(sum(y*y for y in ys)/n)

    amps=[]
    for h in range(1,11):
        re=sum(y*math.cos(2.0*math.pi*h*i/n) for i,y in enumerate(ys))
        im=-sum(y*math.sin(2.0*math.pi*h*i/n) for i,y in enumerate(ys))
        amps.append(2.0*math.hypot(re,im)/n)
    thd=100.0*math.sqrt(sum(a*a for a in amps[1:]))/amps[0]
    return out,thd


def vo5_score(model):
    errs=[]
    details=[]
    for vb,t in sorted(PHILIPS.items()):
        lo=0.0; hi=2.5
        # Require a real bracket. If 5% cannot be reached, score as invalid.
        _,dhi=waveform_for(model,vb,hi,256)
        if dhi<5.0:
            details.append((vb,None,None))
            errs.append(100.0)
            continue

        for _ in range(34):
            mid=0.5*(lo+hi)
            _,d=waveform_for(model,vb,mid,256)
            if d<5.0: lo=mid
            else: hi=mid

        vin=0.5*(lo+hi)
        vo,d=waveform_for(model,vb,vin,1024)
        e=pct(vo,t["vo5"])
        errs.append(e)
        details.append((vb,vo,e))

    return {
        "rms":math.sqrt(sum(x*x for x in errs)/len(errs)),
        "worst":max(abs(x) for x in errs),
        "details":details,
    }


def main():
    print("SMX-3 V2 EF86 unified multi-domain scorecard")
    print("Graph A/B are provisional manual digitizations; exact tables are authoritative.")
    print()

    rows=[]
    for name,model in MODELS.items():
        dev=device_score(model["currents"])
        ga=graph_a_score(model["currents"])
        gb=graph_b_score(model["currents"])
        gbk=graph_b_knee_score(model["currents"])
        dg=dc_gain_score(model)
        ve=vo5_score(model)

        rows.append((name,dev,ga,gb,gbk,dg,ve))

        print(f"[{name}]")
        print(f"  device errors: Ia={dev['ia_err']:+.3f}% Ig2={dev['ig2_err']:+.3f}% gm={dev['gm_err']:+.3f}%")
        print(f"  Graph A: NRMS={ga[0]:.3f} sigma worst={ga[1]:.3f}")
        print(f"  Graph B plateau (100/200/300 V): NRMS={gb[0]:.3f} sigma worst={gb[1]:.3f}")
        print(f"  Graph B knee (20/40/60/80 V): NRMS={gbk[0]:.3f} sigma worst={gbk[1]:.3f}")
        print(f"  DC Ik: RMS={dg['ik_rms']:.3f}% worst={dg['ik_worst']:.3f}%")
        print(f"  gain: RMS={dg['gain_rms']:.3f}% worst={dg['gain_worst']:.3f}%")
        print(f"  Vo@5%: RMS={ve['rms']:.3f}% worst={ve['worst']:.3f}%")
        for vb,vo,e in ve["details"]:
            if vo is None:
                print(f"    {vb:.0f} V: 5% THD not reached in search range")
            else:
                print(f"    {vb:.0f} V: Vo={vo:.3f} V error={e:+.3f}%")
        print()

    print("INTERPRETATION:")
    print("- no overall winner is declared from provisional graph data;")
    print("- exact table domains (device/DC/gain/Vo@5%) and graph domains are shown separately;")
    print("- a future refit must improve the large-signal envelope without materially degrading Graph A, Graph-B plateau or Graph-B knee.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
