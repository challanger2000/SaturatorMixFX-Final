#!/usr/bin/env python3
"""Combined low-level IRON phase proxy: nonlinear JA fundamental + HF parasitics.

At +4 dBu / 20 Hz the accepted JA candidate is only ~0.025% THD. Therefore
its fundamental response can be treated as the low-level nonlinear authority,
while the incremental winding-parasitic correction is estimated from the
linear HF network.

Proxy:
    H_proxy(f) = H_JA_fundamental(f)
                 * H_HF_full(f) / H_linear_144H_base(f)

This avoids double-counting the 144 H magnetizing branch:
- H_JA already contains the magnetic branch + load/source interaction;
- the ratio contributes only the incremental leakage/capacitive network.

The proxy is a diagnostic only. Promotion requires a unified time-domain
circuit with the nonlinear magnetic state and HF parasitics solved together.
"""

import math
import cmath

import smx3_v2_iron_candidate as iron
import smx3_v2_jensen_hf_fit as hf
import smx3_v2_jensen_linear_reference as linear
from smx3_v2_dlp_utils import dlp_degrees


FREQS=(20.0,30.0,50.0,100.0,200.0,500.0,1000.0,2000.0,5000.0,10000.0,20000.0)


def ja_fundamental(freq,level_dbu=4.0,warmup_cycles=30,analysis_cycles=4):
    fs=max(48000.0,96.0*freq)
    vrms=0.775*10.0**(level_dbu/20.0)
    amp=vrms*math.sqrt(2.0)
    dt=1.0/fs

    n=int(round((warmup_cycles+analysis_cycles)*fs/freq))
    start=int(round(warmup_cycles*fs/freq))

    H=0.0
    M=0.0

    re_y=im_y=0.0
    re_x=im_x=0.0

    for idx in range(n):
        t=idx*dt

        k1h,k1m,_=iron.deriv(t,H,M,amp,freq)
        k2h,k2m,_=iron.deriv(t+0.5*dt,H+0.5*dt*k1h,M+0.5*dt*k1m,amp,freq)
        k3h,k3m,_=iron.deriv(t+0.5*dt,H+0.5*dt*k2h,M+0.5*dt*k2m,amp,freq)
        k4h,k4m,_=iron.deriv(t+dt,H+dt*k3h,M+dt*k3m,amp,freq)

        H += dt*(k1h+2*k2h+2*k3h+k4h)/6.0
        M += dt*(k1m+2*k2m+2*k3m+k4m)/6.0

        if idx>=start:
            # Evaluate output at the updated state/time.
            t2=t+dt
            vs=amp*math.sin(2.0*math.pi*freq*t2)
            rseries=iron.RSOURCE+iron.RP
            divider=1.0+rseries/iron.RLOAD
            vnode=(vs-rseries*H/iron.KI)/divider
            y=vnode*iron.RL/iron.RLOAD

            local=idx-start
            a=2.0*math.pi*freq*local/fs
            co=math.cos(a)
            si=math.sin(a)

            re_y+=y*co
            im_y-=y*si
            re_x+=vs*co
            im_x-=vs*si

    return complex(re_y,im_y)/complex(re_x,im_x)


def main():
    llk,cx,_,_,_=hf.fit()

    print("SMX-3 V2 IRON combined JA + HF-parasitic phase proxy")
    print(f"HF fit Llk={llk*1e6:.9f} uH Cx={cx*1e12:.9f} pF")
    print()
    print("freq_Hz,JA_mag_dB,HF_correction_mag_dB,proxy_mag_dB,JA_phase_deg,HF_corr_phase_deg,proxy_phase_deg")

    ja=[]
    proxy=[]

    for f in FREQS:
        hja=ja_fundamental(f)
        hbase=linear.response_test_transfer(f,iron.LM_TARGET)
        hfull=hf.transfer(f,llk,cx)
        corr=hfull/hbase
        hp=hja*corr

        ja.append(hja)
        proxy.append(hp)

        print(
            f"{f:.1f},"
            f"{20*math.log10(abs(hja)):.9f},"
            f"{20*math.log10(abs(corr)):.9f},"
            f"{20*math.log10(abs(hp)):.9f},"
            f"{math.degrees(cmath.phase(hja)):+.9f},"
            f"{math.degrees(cmath.phase(corr)):+.9f},"
            f"{math.degrees(cmath.phase(hp)):+.9f}"
        )

    d_ja=dlp_degrees(FREQS,[cmath.phase(x) for x in ja])
    d_p=dlp_degrees(FREQS,[cmath.phase(x) for x in proxy])

    i1=FREQS.index(1000.0)
    rel20=20.0*math.log10(abs(proxy[0])/abs(proxy[i1]))
    rel20k=20.0*math.log10(abs(proxy[-1])/abs(proxy[i1]))

    print()
    print("JA magnetic-only DLP:")
    print(f"  min={d_ja['min_deg']:+.9f} deg max={d_ja['max_deg']:+.9f} deg worst={d_ja['worst_abs_deg']:.9f} deg")
    print("Combined proxy DLP:")
    print(f"  min={d_p['min_deg']:+.9f} deg max={d_p['max_deg']:+.9f} deg worst={d_p['worst_abs_deg']:.9f} deg")
    print(f"Combined proxy rel20={rel20:.9f} dB")
    print(f"Combined proxy rel20k={rel20k:.9f} dB")

    print()
    print("freq_Hz,JA_DLP_deg,proxy_DLP_deg")
    for f,a,b in zip(FREQS,d_ja["residual_deg"],d_p["residual_deg"]):
        print(f"{f:.1f},{a:+.9f},{b:+.9f}")

    print()
    if d_p["worst_abs_deg"]<=2.0:
        print("PROXY PASS: JA fundamental + incremental HF parasitics enters Jensen maximum DLP.")
    else:
        print("PROXY FAIL: combined phase still exceeds Jensen maximum DLP.")

    if abs(rel20-(-0.04))<=0.02 and abs(rel20k-(-0.05))<=0.02:
        print("PROXY MAGNITUDE: close to Jensen 20 Hz / 20 kHz typical response.")
    else:
        print("PROXY MAGNITUDE: still requires unified refit.")

    print("WARNING: proxy is not a substitute for the final coupled nonlinear+parasitic time-domain solver.")


if __name__=="__main__":
    raise SystemExit(main())
