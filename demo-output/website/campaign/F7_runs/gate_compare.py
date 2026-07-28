#!/usr/bin/env python3
"""Compute gate deviations: simulated surge-front position and column-height
decay vs digitised Martin & Moyce (1952) data points (digitised from Fig. 7
of Xie, arXiv:2108.08769, a=2 1/4 in square-column case), via pixel-position
detection on the published figure (see F7 report for method/uncertainty)."""
import bisect

def load(path):
    rows = []
    with open(path) as f:
        next(f)
        for line in f:
            t, T, Z = map(float, line.split())
            rows.append((T, Z))
    return rows

def interp(rows, Tq):
    Ts = [r[0] for r in rows]
    i = bisect.bisect_left(Ts, Tq)
    if i == 0 or i >= len(rows):
        return None
    T0, Z0 = rows[i - 1]
    T1, Z1 = rows[i]
    frac = (Tq - T0) / (T1 - T0)
    return Z0 + frac * (Z1 - Z0)

front_digitised = [
    (3.90, 6.00), (4.49, 7.00), (5.17, 8.00), (5.91, 9.00),
    (6.74, 10.00), (7.72, 11.00), (8.58, 12.00), (9.53, 13.00),
]

height_digitised = [
    (0.00, 1.00), (0.80, 0.89), (1.29, 0.78), (1.74, 0.67),
    (2.15, 0.56), (2.57, 0.44), (3.08, 0.33), (4.27, 0.22), (6.30, 0.11),
]

print("=== Surge front position gate (closed-box medium mesh) ===")
front_sim = load("closedbox_front.txt")
devs = []
for T, Zref in front_digitised:
    Zsim = interp(front_sim, T)
    if Zsim is None:
        print(f"T={T:5.2f}  Zref={Zref:5.2f}  Zsim=  N/A (out of sim range)")
        continue
    dev = (Zsim - Zref) / Zref * 100
    devs.append(dev)
    print(f"T={T:5.2f}  Zref={Zref:5.2f}  Zsim={Zsim:6.2f}  dev={dev:+6.1f}%")
if devs:
    print(f"mean dev = {sum(devs)/len(devs):+.1f}%   max |dev| = {max(abs(d) for d in devs):.1f}%")

print()
print("=== Column height decay gate (closed-box medium mesh) ===")
height_sim = load("damBreak_MM_a2p25in_medium_closedbox/postProcessing/columnHeight/height_extracted.txt") \
    if False else load("medium_closedbox_height.txt")
devs = []
for T, href in height_digitised:
    if T == 0:
        continue
    hsim = interp(height_sim, T)
    if hsim is None:
        print(f"T={T:5.2f}  href={href:5.2f}  hsim=  N/A (out of sim range)")
        continue
    dev = (hsim - href) / href * 100
    devs.append(dev)
    print(f"T={T:5.2f}  href={href:5.2f}  hsim={hsim:6.3f}  dev={dev:+6.1f}%")
if devs:
    print(f"mean dev = {sum(devs)/len(devs):+.1f}%   max |dev| = {max(abs(d) for d in devs):.1f}%")
