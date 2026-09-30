#!/usr/bin/env python3
"""Bilinear/prewarp viability test for the Jensen linear target.

For an analog transfer H_a(s), bilinear transformation with scale K gives:

    s = K * (1-z^-1)/(1+z^-1)

On the unit circle this means:
    Omega_a = K * tan(omega_d/2)

Therefore the digital response can be evaluated without deriving coefficients:

    H_d(f) = H_a(j * K * tan(pi*f/fs))

We optimize one positive scale K per host sample rate and compare H_d(f) to the
physical target H_a(j*2*pi*f).

If a single global prewarp scale meets the frozen audio-band tolerances, the
production filter can use a straightforward bilinear-transformed 4-state
network with no runtime optimizer.
"""

import math
import cmath

import smx3_v2_jensen_lossaware_target as target
from smx3_v2_dlp_utils import dlp_degrees


SAMPLE_RATES=(44100.0,48000.0,88200.0,96000.0,176400.0,192000.0)


def response_at_omega(omega):
    # Re-express target transfer directly in angular-frequency form.
    j=1j
    zseries=complex(target.RSOURCE+target.RP,0.0)
    ymag=1.0/complex(target.RMAG,omega*target.LMAG)+j*omega*target.CP
    zlink=j*omega*target.LLK
    ylink=1.0/zlink
    yload=1.0/complex(target.RSEC+target.RL,0.0)+j*omega*(target.CS+target.CX)

    a11=1.0/zseries+ymag+ylink
    a12=-ylink
    a21=-ylink
    a22=ylink+yload
    b1=1.0/zseries
    b2=0.0

    vp,vs=target.solve2(a11,a12,a21,a22,b1,b2)
    return vs*target.RL/(target.RSEC+target.RL)


def fixture_freqs(fs):
    fmax=min(20000.0,0.45*fs)
    n=161
    return [20.0*(fmax/20.0)**(i/(n-1)) for i in range(n)]


def evaluate(fs,scale):
    freqs=fixture_freqs(fs)
    k=2.0*fs*scale

    mag_errors=[]
    phase_errors=[]
    actual_ph=[]
    digital_ph=[]

    for f in freqs:
        ha=response_at_omega(2.0*math.pi*f)
        wa=k*math.tan(math.pi*f/fs)
        hd=response_at_omega(wa)

        mag_errors.append(20.0*math.log10(abs(hd)/abs(ha)))

        pe=math.degrees(cmath.phase(hd/ha))
        while pe>180.0: pe-=360.0
        while pe<-180.0: pe+=360.0
        phase_errors.append(pe)

        actual_ph.append(cmath.phase(ha))
        digital_ph.append(cmath.phase(hd))

    # Final DLP residual difference is more relevant than raw phase offset.
    da=dlp_degrees(freqs,actual_ph)["residual_deg"]
    dd=dlp_degrees(freqs,digital_ph)["residual_deg"]
    dlp_err=[b-a for a,b in zip(da,dd)]

    return {
        "worst_mag":max(abs(x) for x in mag_errors),
        "worst_phase":max(abs(x) for x in phase_errors),
        "worst_dlp":max(abs(x) for x in dlp_err),
        "rms_mag":math.sqrt(sum(x*x for x in mag_errors)/len(mag_errors)),
        "rms_dlp":math.sqrt(sum(x*x for x in dlp_err)/len(dlp_err)),
    }


def cost(r):
    return (
        (r["worst_mag"]/0.01)**2
        +(r["worst_dlp"]/0.10)**2
    )


def fit(fs):
    best=None

    # Broad scale search around standard Tustin K=2fs.
    for i in range(201):
        scale=0.70+0.60*i/200.0
        r=evaluate(fs,scale)
        c=cost(r)
        if best is None or c<best[0]:
            best=(c,scale,r)

    _,scale,_=best
    step=.01

    for _ in range(60):
        cur=evaluate(fs,scale)
        cc=cost(cur)
        improved=False
        for ds in (step,-step):
            ns=scale+ds
            if not (0.5<ns<1.5):
                continue
            nr=evaluate(fs,ns)
            nc=cost(nr)
            if nc<cc:
                scale=ns
                cc=nc
                improved=True
        if not improved:
            step*=0.5
        if step<1e-7:
            break

    return scale,evaluate(fs,scale)


def main():
    print("SMX-3 V2 Jensen target bilinear/prewarp viability")
    print("fs_Hz,scale,K,mag_worst_dB,raw_phase_worst_deg,DLP_worst_deg,mag_rms_dB,DLP_rms_deg,status")

    all_pass=True

    for fs in SAMPLE_RATES:
        scale,r=fit(fs)
        status="PASS" if r["worst_mag"]<=0.01 and r["worst_dlp"]<=0.10 else "FAIL"
        if status!="PASS":
            all_pass=False

        print(
            f"{fs:.0f},{scale:.9f},{2*fs*scale:.9f},"
            f"{r['worst_mag']:.9f},{r['worst_phase']:.9f},{r['worst_dlp']:.9f},"
            f"{r['rms_mag']:.9f},{r['rms_dlp']:.9f},{status}"
        )

    print()
    if all_pass:
        print("PASS: one globally prewarped bilinear transform per sample rate is sufficient.")
    else:
        print("INFO: single-scale bilinear transform is insufficient at one or more sample rates.")
        print("NEXT: test two-section frequency warping or direct digital rational fit.")

    return 0


if __name__=="__main__":
    raise SystemExit(main())
