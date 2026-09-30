#!/usr/bin/env python3
"""Shared Deviation-from-Linear-Phase utilities for SMX-3 V2.

Jensen defines DLP by removing the Frequency Independent Delay / corresponding
linear-phase component from absolute phase.

For the SMX-3 transformer reference we estimate that delay from the mid/high
audio band where the JT-11P-1 manufacturer DLP graph is already approximately
flat around 0 degrees.

Frozen research convention:
- delay-fit frequencies: >= 500 Hz;
- linear regression is phase radians vs LINEAR frequency Hz;
- both intercept (polarity/reference phase) and slope (constant delay) are removed;
- DLP is then evaluated over the full requested band.

Do not use a whole-band log-spaced fit: that overweights the LF curvature which
is precisely the quantity DLP is supposed to measure.
"""

import math


FIT_MIN_HZ=500.0


def unwrap(phases):
    if not phases:
        return []
    out=[phases[0]]
    for p in phases[1:]:
        q=p
        while q-out[-1] > math.pi:
            q-=2.0*math.pi
        while q-out[-1] < -math.pi:
            q+=2.0*math.pi
        out.append(q)
    return out


def linear_phase_fit(freqs,phases,fit_min_hz=FIT_MIN_HZ):
    pairs=[(f,p) for f,p in zip(freqs,phases) if f>=fit_min_hz]
    if len(pairs)<2:
        raise ValueError("need at least two frequencies in DLP delay-fit band")

    xs=[x for x,_ in pairs]
    ys=[y for _,y in pairs]

    n=len(xs)
    sx=sum(xs); sy=sum(ys)
    sxx=sum(x*x for x in xs)
    sxy=sum(x*y for x,y in pairs)

    den=n*sxx-sx*sx
    if abs(den)<1e-30:
        raise ValueError("degenerate DLP delay-fit frequencies")

    b=(n*sxy-sx*sy)/den
    a=(sy-b*sx)/n
    return a,b


def dlp_degrees(freqs,phases,fit_min_hz=FIT_MIN_HZ):
    phases=unwrap(phases)
    a,b=linear_phase_fit(freqs,phases,fit_min_hz)

    residual=[
        math.degrees(p-(a+b*f))
        for f,p in zip(freqs,phases)
    ]
    tau=-b/(2.0*math.pi)

    return {
        "residual_deg":residual,
        "delay_s":tau,
        "intercept_rad":a,
        "min_deg":min(residual),
        "max_deg":max(residual),
        "worst_abs_deg":max(abs(min(residual)),abs(max(residual))),
    }
