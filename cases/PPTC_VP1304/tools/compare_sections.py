#!/usr/bin/env python3
"""Blade-section comparison between two tessellated PPTC CAD variants.

The decisive test for the CAD equivalence measurement: if SVA's gap-closed variant
differs from the detailed variant ONLY in the root-gap region, then the blade sections
at radii above the root must agree, and the disagreement must collapse as r grows.

Chord and max thickness are measured in the unrolled cylindrical surface at each radius,
averaged over the five blades. Units: millimetres (the CAD's own).
"""
import sys
import numpy as np
from stl_metrics import read_stl

R_PROP = 125.0
R_HUB = 37.5


def sections(tris, r_target, halfwidth):
    pts = tris.reshape(-1, 3)
    r = np.hypot(pts[:, 1], pts[:, 2])
    p = pts[np.abs(r - r_target) < halfwidth]
    if len(p) < 60:
        return None
    th = np.arctan2(p[:, 2], p[:, 1])
    o = np.argsort(th)
    th_s, p_s = th[o], p[o]
    brk = np.where(np.diff(th_s) > np.deg2rad(8))[0]
    groups = np.split(np.arange(len(th_s)), brk + 1)
    if len(groups) > 1 and (th_s[0] + 2 * np.pi - th_s[-1]) < np.deg2rad(8):
        groups[0] = np.concatenate([groups[0], groups[-1]])
        groups = groups[:-1]
    groups = [g for g in groups if len(g) >= 25]
    res = []
    for g in groups:
        q = p_s[g]
        tq = np.arctan2(q[:, 2], q[:, 1])
        t0 = np.median(tq)
        dt = (tq - t0 + np.pi) % (2 * np.pi) - np.pi
        P = np.column_stack([r_target * dt, q[:, 0]])
        d2 = ((P[:, None, :] - P[None, :, :]) ** 2).sum(-1)
        i, j = np.unravel_index(np.argmax(d2), d2.shape)
        chord = float(np.sqrt(d2[i, j]))
        e = (P[j] - P[i]) / chord
        n = np.array([-e[1], e[0]])
        off = (P - P[i]) @ n
        res.append((chord, float(off.max() - off.min())))
    if not res:
        return None
    c = np.array([x[0] for x in res])
    t = np.array([x[1] for x in res])
    return len(res), c.mean(), t.mean()


if __name__ == '__main__':
    a_path, b_path = sys.argv[1], sys.argv[2]
    A, B = read_stl(a_path), read_stl(b_path)
    print(f'A = {a_path}   ({len(A)} triangles)')
    print(f'B = {b_path}   ({len(B)} triangles)')
    print(f'hub radius = {R_HUB} mm  ->  r/R = {R_HUB/R_PROP:.3f} is the blade root\n')
    hw = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
    print(f'shell half-width {hw} mm')
    print(f"{'r/R':>6} {'r mm':>7} | {'nA':>3} {'chordA':>9} {'thickA':>8} | "
          f"{'nB':>3} {'chordB':>9} {'thickB':>8} | {'dchord%':>8} {'dthick%':>8}")
    for rr in (0.30, 0.32, 0.35, 0.40, 0.45, 0.50, 0.60, 0.70, 0.80, 0.90, 0.95, 0.98):
        r = rr * R_PROP
        sa, sb = sections(A, r, hw), sections(B, r, hw)
        if sa is None or sb is None:
            print(f'{rr:6.2f} {r:7.2f} |  (insufficient points)')
            continue
        na, ca, ta = sa
        nb, cb, tb = sb
        dc = 100 * (cb - ca) / ca
        dt = 100 * (tb - ta) / ta
        flag = '   <-- root region' if rr <= 0.34 else ''
        print(f'{rr:6.2f} {r:7.2f} | {na:3d} {ca:9.4f} {ta:8.4f} | '
              f'{nb:3d} {cb:9.4f} {tb:8.4f} | {dc:+8.3f} {dt:+8.3f}{flag}')
