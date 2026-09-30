#!/usr/bin/env python3
"""Current strongest EF86 offline candidate gate for SMX-3 V2.

Candidate:
- EX = 1.40
- Stage-1 MU/KP/KVB_SCREEN/LAMBDA
- Stage-2C plate knee
- exact Philips Ia/gm/Ig2 local anchors

Hard gates use stronger manufacturer evidence:
- Graph A provisional surface within conservative uncertainty;
- Graph B provisional surface within conservative uncertainty;
- exact circuit Ik/gain table;
- exact multi-supply Vo@5% envelope.

Graph D is intentionally excluded from hard PASS because its low-level points
remain provisional manual digitization.
"""

import smx3_v2_ef86_ex_scan as m

EX=1.40


def main():
    vct,kg1,s0=m.derive_local(EX)
    p=(EX,vct,kg1,s0)

    ga,gaw=m.graph_score(m.A_POINTS,p,"A")
    gb,gbw=m.graph_score(m.B_POINTS,p,"B")

    # Exact Philips local plate resistance anchor: Ri ~= 2.5 MOhm at
    # Va=250 V, Vg2=140 V, Vg1=-2 V.
    h=0.1
    gp=(m.ia(250.0+h,140.0,-2.0,*p[:3]) - m.ia(250.0-h,140.0,-2.0,*p[:3]))/(2.0*h)
    ri=1.0/gp
    ri_err=100.0*(ri-2.5e6)/2.5e6

    ikerrs=[]
    gerrs=[]
    voerrs=[]

    print("SMX-3 V2 EF86 EX=1.40 candidate gate")
    print(f"VCT={vct:.12g} KG1={kg1:.12g} S0={s0:.12g}")
    print(f"Graph A NRMS={ga:.6f} sigma worst={gaw:.6f}")
    print(f"Graph B NRMS={gb:.6f} sigma worst={gbw:.6f}")
    print(f"Ri={ri/1e6:.9f} MOhm vs Philips 2.500000000 MOhm error={ri_err:+.6f}%")
    print()
    print("Vb,Ik_err_pct,Gain_err_pct,Vo5_err_pct")

    for vb,t in m.AMP.items():
        dc=m.solve_dc(vb,p)
        ik=dc[3]+dc[4]
        g=abs(m.small_gain(dc,p))
        vo=m.output_at_5(vb,p)

        ei=100.0*(ik-t["ik"])/t["ik"]
        eg=100.0*(g-t["gain"])/t["gain"]
        ev=100.0*(vo-t["vo5"])/t["vo5"]

        ikerrs.append(abs(ei))
        gerrs.append(abs(eg))
        voerrs.append(abs(ev))

        print(f"{vb:.0f},{ei:+.6f},{eg:+.6f},{ev:+.6f}")

    mi=max(ikerrs)
    mg=max(gerrs)
    mv=max(voerrs)

    print()
    print(f"max |Ik error|={mi:.6f}%")
    print(f"max |gain error|={mg:.6f}%")
    print(f"max |Vo@5% error|={mv:.6f}%")

    failures=[]
    if ga>0.8 or gaw>1.8: failures.append("Graph A")
    if gb>0.8 or gbw>1.8: failures.append("Graph B")
    if abs(ri_err)>12.0: failures.append("exact Ri anchor")
    if mi>6.0: failures.append("cathode-current sweep")
    if mg>5.0: failures.append("gain sweep")
    if mv>5.0: failures.append("exact 5%-THD envelope")

    if failures:
        print("FAIL:")
        for f in failures: print(" - "+f)
        return 1

    print("PASS: current EF86 candidate clears frozen manufacturer-domain gates.")
    print("Graph D remains informational until calibrated digitization is available.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
