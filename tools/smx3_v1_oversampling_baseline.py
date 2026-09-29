#!/usr/bin/env python3
"""Reproduce and measure the SMX-3 v0.1.1 oversampling filter path.

This tool intentionally contains no production DSP changes. It mirrors the
filter-design equations in SMX-3 v0.1.1 and reports deterministic properties
of the linear up/down path used by the V1 processor.

Standard-library only.
"""

import argparse
import cmath
import csv
import math
import sys

PI = math.pi
OVERSAMPLE = 4
SECTIONS = 8


def design(sample_rate: float):
    internal_rate = sample_rate * OVERSAMPLE
    cutoff = 0.485 * sample_rate
    w0 = 2.0 * PI * cutoff / internal_rate
    cw = math.cos(w0)
    sw = math.sin(w0)
    order = 2 * SECTIONS
    coeffs = []
    for section in range(SECTIONS):
        angle = (2.0 * (section + 1) - 1.0) * PI / (2.0 * order)
        q = 1.0 / (2.0 * math.cos(angle))
        alpha = sw / (2.0 * q)
        a0 = 1.0 + alpha
        b0 = ((1.0 - cw) * 0.5) / a0
        b1 = (1.0 - cw) / a0
        b2 = b0
        a1 = (-2.0 * cw) / a0
        a2 = (1.0 - alpha) / a0
        coeffs.append((b0, b1, b2, a1, a2))
    return coeffs


def section_response(c, freq_hz: float, internal_rate: float):
    b0, b1, b2, a1, a2 = c
    w = 2.0 * PI * freq_hz / internal_rate
    z1 = cmath.exp(-1j * w)
    z2 = z1 * z1
    return (b0 + b1 * z1 + b2 * z2) / (1.0 + a1 * z1 + a2 * z2)


def cascade_response(coeffs, freq_hz: float, sample_rate: float):
    internal_rate = sample_rate * OVERSAMPLE
    h = 1.0 + 0.0j
    for c in coeffs:
        h *= section_response(c, freq_hz, internal_rate)
    return h


def v1_clean_roundtrip_response(coeffs, freq_hz: float, sample_rate: float):
    # V1 applies the same 8-section lowpass once in the interpolation path and
    # once again in the decimation path. The zero-stuffing amplitude scale is
    # not part of the normalized steady-state transfer magnitude here.
    h = cascade_response(coeffs, freq_hz, sample_rate)
    return h * h


def mag_db(h: complex):
    m = abs(h)
    return -math.inf if m == 0.0 else 20.0 * math.log10(m)


def phase_rad(h: complex):
    return cmath.phase(h)


def wrapped_delta(a: float, b: float):
    d = a - b
    while d > PI:
        d -= 2.0 * PI
    while d < -PI:
        d += 2.0 * PI
    return d


def group_delay_input_samples(coeffs, freq_hz: float, sample_rate: float):
    # Numerical derivative of phase with respect to angular frequency at the
    # base sample rate. Choose a deterministic small frequency step that stays
    # away from DC and Nyquist.
    nyq = 0.5 * sample_rate
    df = max(0.01, min(1.0, sample_rate * 1.0e-5))
    f0 = max(df, min(freq_hz, nyq - df))
    f1 = f0 - df
    f2 = f0 + df
    h1 = v1_clean_roundtrip_response(coeffs, f1, sample_rate)
    h2 = v1_clean_roundtrip_response(coeffs, f2, sample_rate)
    dp = wrapped_delta(phase_rad(h2), phase_rad(h1))
    domega = 2.0 * PI * (f2 - f1) / sample_rate
    return -dp / domega


def default_frequencies(sample_rate: float):
    candidates = [
        10, 20, 40, 80, 100, 250, 500, 1000, 2000, 5000,
        10000, 15000, 18000, 20000, 22000, 30000, 40000,
    ]
    limit = 0.499 * sample_rate
    return [float(f) for f in candidates if f < limit]


def measure(sample_rate: float):
    coeffs = design(sample_rate)
    rows = []
    for f in default_frequencies(sample_rate):
        h = v1_clean_roundtrip_response(coeffs, f, sample_rate)
        rows.append({
            "sample_rate_hz": sample_rate,
            "frequency_hz": f,
            "magnitude_db": mag_db(h),
            "phase_deg": math.degrees(phase_rad(h)),
            "group_delay_samples": group_delay_input_samples(coeffs, f, sample_rate),
        })
    return rows


def print_table(rows):
    print("sample_rate_hz,frequency_hz,magnitude_db,phase_deg,group_delay_samples")
    for r in rows:
        print(
            f'{r["sample_rate_hz"]:.1f},'
            f'{r["frequency_hz"]:.1f},'
            f'{r["magnitude_db"]:.9f},'
            f'{r["phase_deg"]:.9f},'
            f'{r["group_delay_samples"]:.9f}'
        )


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "sample_rate_hz",
                "frequency_hz",
                "magnitude_db",
                "phase_deg",
                "group_delay_samples",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sample-rate",
        type=float,
        action="append",
        dest="sample_rates",
        help="Base sample rate. Repeat for multiple rates.",
    )
    parser.add_argument("--csv", help="Optional CSV output path.")
    args = parser.parse_args()

    rates = args.sample_rates or [44100.0, 48000.0, 88200.0, 96000.0, 192000.0]
    all_rows = []
    for sr in rates:
        if not math.isfinite(sr) or sr <= 1000.0:
            parser.error(f"invalid sample rate: {sr}")
        all_rows.extend(measure(sr))

    print_table(all_rows)
    if args.csv:
        write_csv(args.csv, all_rows)


if __name__ == "__main__":
    sys.exit(main())
