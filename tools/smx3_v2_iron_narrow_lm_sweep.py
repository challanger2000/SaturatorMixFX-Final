#!/usr/bin/env python3
"""Narrow first-order JT-11P-1 candidate sweep for SMX-3 V2 IRON.

Purpose:
verify whether a small change of the quasi-static low-field inductive scale
around the corrected lossless-equivalent 144 H point can close Jensen's
first-order constraints WITHOUT any additional dynamic-loss term.

For each L_qs candidate:
1. re-identify c/KI against the +4 dBu / +20 dBu 20 Hz THD anchors;
2. fit the reduced HF leakage/C network against:
   - 20 kHz / 1 kHz = -0.05 dB
   - 95 kHz / 1 kHz = -3 dB
3. construct a diagnostic combined low-level transfer:
   H_proxy = H_JA_fundamental * H_HF_full / H_linear_base
4. evaluate with the shared Jensen DLP convention (delay fit >=500 Hz);
5. report magnitude, DLP and harmonic parity.

This remains a proxy. A passing point must later be validated in one unified
nonlinear magnetic + HF-parasitic time-domain circuit.
"""

import cmath
import math

import smx3_v2_iron_lm_constrained_refit as fitmod
from smx3_v2_dlp_utils import dlp_degrees


L_VALUES=(136.0,137.0,138.0,139.0,140.0,144.0)
FREQS=(20.0,30.0,50.0,100.0,200.0,500.0,1000.0,2000.0,5000.0,10000.0,20000.0)

RSOURCE=600.0
RP=1450.0
RSEC=1550.0
RL=10000.0
RLOAD=RSEC+RL
CP=98e-12
CS=110e-12

TARGET20K=-0.05
TARGET95K=-3.0


def parallel(a,b):
    return 1.0/(1.0/a+1.0/b)


def linear_base_transfer(freq,lm):
    zload=complex(RSEC+RL,0.0)
    zm=1j*2.0*math.pi*freq*lm
    zbranch=parallel(zload,zm)
    return zbranch/(RSOURCE+RP+zbranch) * RL/(RSEC+RL)


def solve2(a11,a12,a21,a22,b1,b2):
    det=a11*a22-a12*a21
    return (
        (b1*a22-a12*b2)/det,
        (a11*b2-b1*a21)/det,
    )


def hf_transfer(freq,lm,llk,cx):
    w=2.0*math.pi*freq
    j=1j

    zs=complex(RSOURCE+RP,0.0)
    yp=1.0/(j*w*lm)+j*w*CP

    zlink=j*w*max(llk,1e-12)
    ylink=1.0/zlink

    yload=1.0/complex(RSEC+RL,0.0)+j*w*(CS+cx)

    a11=1.0/zs+yp+ylink
    a12=-ylink
    a21=-ylink
    a22=ylink+yload
    b1=1.0/zs
    b2=0.0

    vp,vb=solve2(a11,a12,a21,a22,b1,b2)
    return vb*RL/(RSEC+RL)


def dbmag(z):
    return 20.0*math.log10(abs(z))


def hf_rel_db(freq,lm,llk,cx,ref=1000.0):
    return dbmag(hf_transfer(freq,lm,llk,cx))-dbmag(hf_transfer(ref,lm,llk,cx))


def hf_objective(lm,logl,logc):
    llk=10.0**logl
    cx=10.0**logc
    e20=hf_rel_db(20000.0,lm,llk,cx)-TARGET20K
    e95=hf_rel_db(95000.0,lm,llk,cx)-TARGET95K
    return e20*e20+e95*e95


def fit_hf(lm):
    best=None

    # Smaller deterministic grid than the research-global fitter because this
    # sweep is deliberately narrow in L_qs.
    for i in range(49):
        logl=-5.5+i*(3.5/48.0)
        for k in range(53):
            logc=-11.7+k*(3.8/52.0)
            e=hf_objective(lm,logl,logc)
            if best is None or e<best[0]:
                best=(e,logl,logc)

    e,logl,logc=best
    step=.10

    for _ in range(50):
        current=hf_objective(lm,logl,logc)
        improved=False

        for dl,dc in (
            (step,0),(-step,0),(0,step),(0,-step),
            (step,step),(step,-step),(-step,step),(-step,-step),
        ):
            nl=logl+dl
            nc=logc+dc
            if not (-6.0<=nl<=-1.0 and -12.0<=nc<=-7.0):
                continue
            ne=hf_objective(lm,nl,nc)
            if ne<current:
                logl,logc=nl,nc
                current=ne
                improved=True

        if not improved:
            step*=.5
        if step<2e-5:
            break

    return 10.0**logl,10.0**logc,hf_objective(lm,logl,logc)


def ja_transfer(lm,c,ki,freq):
    r=fitmod.simulate(
        lm,c,ki,4.0,freq,
        fs=max(48000.0,96.0*freq),
        warmup_cycles=30,
        analysis_cycles=4,
    )

    # simulate() reports output RMS and output phase relative to the sine input.
    # Input RMS at +4 dBu:
    vin_rms=0.775*10.0**(4.0/20.0)
    gain=r["rms"]/vin_rms
    return gain*cmath.exp(1j*r["phase"]),r


def evaluate_l(lm):
    fit=fitmod.fit_c_ki(lm)
    if fit is None:
        return None

    c,ki,_,fit_exact=fit

    # High-resolution anchor verification.
    low=fitmod.simulate(
        lm,c,ki,4.0,20.0,
        fs=48000.0,warmup_cycles=30,analysis_cycles=4,
    )
    high=fitmod.simulate(
        lm,c,ki,20.0,20.0,
        fs=48000.0,warmup_cycles=30,analysis_cycles=4,
    )

    llk,cx,hf_cost=fit_hf(lm)

    proxies=[]
    ja_only=[]

    for f in FREQS:
        hja,_=ja_transfer(lm,c,ki,f)
        hbase=linear_base_transfer(f,lm)
        hfull=hf_transfer(f,lm,llk,cx)
        corr=hfull/hbase

        ja_only.append(hja)
        proxies.append(hja*corr)

    d_ja=dlp_degrees(FREQS,[cmath.phase(h) for h in ja_only])
    d_p=dlp_degrees(FREQS,[cmath.phase(h) for h in proxies])

    i1=FREQS.index(1000.0)

    rel20=20.0*math.log10(abs(proxies[0])/abs(proxies[i1]))
    rel20k=20.0*math.log10(abs(proxies[-1])/abs(proxies[i1]))
    rel95=hf_rel_db(95000.0,lm,llk,cx)

    # Independent low-level frequency law after c/KI re-identification.
    t20=low["thd"]
    t40=fitmod.simulate(
        lm,c,ki,4.0,40.0,
        fs=48000.0,warmup_cycles=30,analysis_cycles=4,
    )["thd"]
    t80=fitmod.simulate(
        lm,c,ki,4.0,80.0,
        fs=48000.0,warmup_cycles=30,analysis_cycles=4,
    )["thd"]

    return {
        "lm":lm,
        "c":c,
        "ki":ki,
        "fit_exact":fit_exact,
        "low":low,
        "high":high,
        "llk":llk,
        "cx":cx,
        "hf_cost":hf_cost,
        "d_ja":d_ja,
        "d_proxy":d_p,
        "rel20":rel20,
        "rel20k":rel20k,
        "rel95":rel95,
        "q1":t40/t20,
        "q2":t80/t40,
        "proxy":proxies,
    }


def first_order_pass(r):
    if abs(100.0*r["low"]["thd"]-0.025)>0.005:
        return False
    if abs(100.0*r["high"]["thd"]-1.0)>0.05:
        return False
    if r["low"]["hs"][0] >= .1*r["low"]["hs"][1]:
        return False
    if not (.18<=r["q1"]<=.35 and .18<=r["q2"]<=.35):
        return False
    if abs(r["rel20"]-(-.04))>.02:
        return False
    if abs(r["rel20k"]-(-.05))>.02:
        return False
    if abs(r["rel95"]-(-3.0))>.10:
        return False
    if r["d_proxy"]["worst_abs_deg"]>2.0:
        return False

    # Jensen graph shape: positive LF curvature, upper band near zero.
    if r["d_proxy"]["residual_deg"][0] <= 0.0:
        return False

    idx10=FREQS.index(10000.0)
    if abs(r["d_proxy"]["residual_deg"][idx10])>.5:
        return False

    return True


def main():
    print("SMX-3 V2 IRON narrow L_qs / c / KI / HF-parasitic sweep")
    print("Shared Jensen DLP convention: delay fit >=500 Hz.")
    print()
    print(
        "L_H,c,KI,fit_exact,H4_THD_pct,H20_THD_pct,H2_pct,H3_pct,"
        "q40_20,q80_40,Llk_mH,Cx_pF,rel20_dB,rel20k_dB,rel95k_dB,"
        "JA_DLP_worst,proxy_DLP_min,proxy_DLP_max,proxy_DLP_worst,pass"
    )

    results=[]

    for lm in L_VALUES:
        r=evaluate_l(lm)
        if r is None:
            print(f"{lm:.3f},nan,nan,0,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,0")
            continue

        passed=first_order_pass(r)
        results.append((passed,r))

        print(
            f"{lm:.3f},{r['c']:.9f},{r['ki']:.9f},{int(r['fit_exact'])},"
            f"{100*r['low']['thd']:.9f},{100*r['high']['thd']:.9f},"
            f"{100*r['low']['hs'][0]:.9f},{100*r['low']['hs'][1]:.9f},"
            f"{r['q1']:.9f},{r['q2']:.9f},"
            f"{r['llk']*1e3:.9f},{r['cx']*1e12:.9f},"
            f"{r['rel20']:.9f},{r['rel20k']:.9f},{r['rel95']:.9f},"
            f"{r['d_ja']['worst_abs_deg']:.9f},"
            f"{r['d_proxy']['min_deg']:+.9f},{r['d_proxy']['max_deg']:+.9f},"
            f"{r['d_proxy']['worst_abs_deg']:.9f},{int(passed)}"
        )

    passing=[r for ok,r in results if ok]

    print()
    if passing:
        # prefer the lowest DLP worst residual, then closest low-level magnitude.
        best=min(
            passing,
            key=lambda r:(
                r["d_proxy"]["worst_abs_deg"],
                abs(r["rel20"]-(-.04)),
            )
        )

        print("FIRST-ORDER PASSING REGION FOUND")
        print(f"best L_qs={best['lm']:.6f} H")
        print(f"c={best['c']:.9f}")
        print(f"KI={best['ki']:.9f}")
        print(f"proxy DLP worst={best['d_proxy']['worst_abs_deg']:.9f} deg")
        print(f"rel20={best['rel20']:.9f} dB")
        print(f"rel20k={best['rel20k']:.9f} dB")
        print("NEXT: build one unified nonlinear magnetic + HF-parasitic time-domain circuit at this region and rerun the full IRON gate set.")
    else:
        print("NO FIRST-ORDER PASS IN NARROW REGION")
        print("Dynamic-loss / richer low-field magnetic structure remains required.")

    print()
    print("Diagnostic proxy only: no L/c/KI/HF tuple is promoted to production from this sweep alone.")


if __name__=="__main__":
    raise SystemExit(main())
