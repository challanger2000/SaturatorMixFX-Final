# SMX-3 V2 IRON Jensen Linear Target — Bilinear Viability

Date: 2026-09-30
Status: realtime discretization experiment

The Jensen loss-aware target is a four-state passive analog network.

Preferred implementation path:
- preserve that network;
- discretize it directly;
- avoid fitting an unrelated arbitrary IIR if possible.

First test:
standard bilinear transform with one optimized global frequency scale per host
sample rate.

Digital response:
H_d(f) = H_a(j*K*tan(pi*f/fs))

K=2*fs is ordinary Tustin.
A fitted K is a global prewarp.

Frozen acceptance over 20 Hz..min(20 kHz,0.45fs):
- worst magnitude residual <= 0.01 dB;
- worst DLP residual <= 0.10 degree.

Sample rates:
44.1 / 48 / 88.2 / 96 / 176.4 / 192 kHz.

If this passes, production coefficient generation can remain analytic and very
small.

If it fails, do not loosen tolerances; move to a higher-fidelity digital
realization.
