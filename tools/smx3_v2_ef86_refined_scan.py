#!/usr/bin/env python3
"""Refined EF86 Stage-3 scan around the successful EX region.

Scan only:
- EX, controlling global grid-to-current curvature;
- effective device Ig2 anchor / S0, within a narrow plausible specimen range.

For every candidate:
- VCT is solved to keep gm/Ia exact at the Philips device point;
- KG1 is derived to keep Ia exactly 3.0 mA.

No output gain/compression correction exists.

Standard library only.
"""

import math
import smx3_v2_ef86_ex_scan as base

EX_VALUES=(1.34,1.36,1.38,1.40,1.42,1.44,1.46)
IG2_MA_VALUES=(0.54,0.55,0.56,0.57,0.58,0.59,0.60)


def candidate(ex,ig2_ma):
    vct,kg1,s0_exact=base.derive_local(ex)
    s0=s0_exact*(ig2_ma/0.600)
    return (ex,vct,kg1,s0)


def evaluate(ex,ig2_ma):
    p=candidate(ex,ig2_ma)
    ga,_=base.graph_score(base.A_POINTS,p,"A")
    gb,_=base.graph_score(base.B_POINTS,p,"B")

    ikerrs=[]
    gerrs=[]
    verrs=[]

    for vb,t in base.AMP.items():
        dc=base.solve_dc(vb,p)
        ik=dc[3]+dc[4]
        g=abs(base.small_gain(dc,p))
        vo=base.output_at_5(vb,p)

        ikerrs.append(abs(100*(ik-t["ik"])/t["ik"]))
        gerrs.append(abs(100*(g-t["gain"])/t["gain"]))
        verrs.append(abs(100*(vo-t["vo5"])/t["vo5"]))

    mi=max(ikerrs)
    mg=max(gerrs)
    mv=max(verrs)

    # Device Ig2 remains a soft manufacturer anchor, not a free sound control.
    ig2_sigma=abs(ig2_ma-0.600)/0.050

    # Transparent ranking only.
    score=ga+gb+mi/4.0+mg/4.0+mv/4.0+ig2_sigma

    return score,p,ga,gb,mi,mg,mv,ig2_sigma


def main():
    print("SMX-3 V2 EF86 refined EX / effective-Ig2 scan")
    print("Ia and gm are exact at the Philips device point for every candidate.")
    print()
    print("EX,Ig2_mA,GraphA,GraphB,IkMaxPct,GainMaxPct,Vo5MaxPct,Ig2Sigma,Score")

    rows=[]
    for ex in EX_VALUES:
        for ig2 in IG2_MA_VALUES:
            try:
                r=evaluate(ex,ig2)
                rows.append((r[0],ex,ig2)+r[1:])
                print(
                    f"{ex:.4f},{ig2:.3f},{r[2]:.6f},{r[3]:.6f},"
                    f"{r[4]:.4f},{r[5]:.4f},{r[6]:.4f},{r[7]:.4f},{r[0]:.6f}"
                )
            except Exception as e:
                print(f"{ex:.4f},{ig2:.3f},ERROR,{type(e).__name__}:{e}")

    rows.sort()

    print()
    print("BEST CANDIDATES")
    for row in rows[:10]:
        score,ex,ig2,p,ga,gb,mi,mg,mv,sig=row
        print(
            f"score={score:.6f} EX={ex:.4f} Ig2={ig2:.3f}mA "
            f"GraphA={ga:.3f} GraphB={gb:.3f} IkMax={mi:.2f}% "
            f"GainMax={mg:.2f}% Vo5Max={mv:.2f}% Ig2Sigma={sig:.2f}"
        )

    if not rows:
        return 1

    score,ex,ig2,p,ga,gb,mi,mg,mv,sig=rows[0]
    print()
    print(f"DETAIL BEST EX={ex:.4f} Ig2={ig2:.3f}mA")
    print(f"VCT={p[1]:.12g} KG1={p[2]:.12g} S0={p[3]:.12g}")
    print("Vb,Ik_err_pct,gain_err_pct,Vo5_model,Vo5_target,Vo5_err_pct")

    for vb,t in base.AMP.items():
        dc=base.solve_dc(vb,p)
        ik=dc[3]+dc[4]
        g=abs(base.small_gain(dc,p))
        vo=base.output_at_5(vb,p)
        print(
            f"{vb:.0f},"
            f"{100*(ik-t['ik'])/t['ik']:+.4f},"
            f"{100*(g-t['gain'])/t['gain']:+.4f},"
            f"{vo:.6f},{t['vo5']:.6f},"
            f"{100*(vo-t['vo5'])/t['vo5']:+.4f}"
        )

    return 0


if __name__=="__main__":
    raise SystemExit(main())
