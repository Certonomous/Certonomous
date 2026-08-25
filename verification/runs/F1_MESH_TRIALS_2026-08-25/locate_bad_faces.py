#!/usr/bin/env python3
"""Locate the severely non-orthogonal faces checkMesh wrote to nonOrthoFaces.

Reads constant/polyMesh/{points,faces} and the faceSet checkMesh emitted,
computes each flagged face's centroid, and reports WHERE the bad faces are:
inboard span (z < z_tip) vs the outboard TIP-FILL region (z >= z_tip), with the
x, y, z extent of each group.  It measures; it grades nothing.

PLANTED CONTROL (CLAUDE.md rule 3).  A count is not evidence from a reader not
shown able to see the other answer.  --selftest displaces one flagged face's
points by a known offset and asserts the reported centroid moves by exactly that
offset, and asserts an empty faceSet reports NO FLAGGED FACES rather than 0%.
"""
import re
import sys

import numpy as np

TRIPLE = re.compile(r"\(\s*(-?[\d.eE+-]+)\s+(-?[\d.eE+-]+)\s+(-?[\d.eE+-]+)\s*\)")


def _after_header(path):
    t = open(path, errors="replace").read()
    return t[t.index("}", t.index("FoamFile")) + 1:]


def read_points(p):
    b = _after_header(p)
    n = int(re.search(r"^\s*(\d+)\s*$", b, re.M).group(1))
    P = np.array(TRIPLE.findall(b), dtype=float)
    assert len(P) == n, f"points: header says {n}, parsed {len(P)}"
    return P


def read_faces(p):
    b = _after_header(p)
    n = int(re.search(r"^\s*(\d+)\s*$", b, re.M).group(1))
    F = [np.fromstring(m.group(1), sep=" ", dtype=np.int64)
         for m in re.finditer(r"\d+\s*\(([\d\s]+)\)", b)]
    assert len(F) == n, f"faces: header says {n}, parsed {len(F)}"
    return F


def read_set(p):
    b = _after_header(p)
    m = re.search(r"^\s*(\d+)\s*$", b, re.M)
    n = int(m.group(1))
    if n == 0:
        return np.array([], dtype=np.int64)
    tail = b[b.index("(", m.end()) + 1:]
    return np.fromstring(tail[:tail.index(")")], sep=" ", dtype=np.int64)


def centroids(P, F, ids):
    return np.array([P[F[i]].mean(axis=0) for i in ids]) if len(ids) else np.zeros((0, 3))


def report(case, z_tip, P=None, F=None, ids=None):
    if P is None:
        P = read_points(f"{case}/constant/polyMesh/points")
        F = read_faces(f"{case}/constant/polyMesh/faces")
        ids = read_set(f"{case}/constant/polyMesh/sets/nonOrthoFaces")
    print(f"{case}: points {len(P)}  faces {len(F)}  flagged {len(ids)}")
    if len(ids) == 0:
        print("  NO FLAGGED FACES")
        return None
    C = centroids(P, F, ids)
    tip = C[:, 2] >= z_tip - 1e-9
    print(f"  z_tip = {z_tip:.7f}")
    print(f"  OUTBOARD of z_tip (TIP-FILL region): {int(tip.sum()):6d}  ({100*tip.mean():5.1f}%)")
    print(f"  INBOARD  of z_tip (wing/wake span) : {int((~tip).sum()):6d}  ({100*(~tip).mean():5.1f}%)")
    # A face inside the TIP FILL lies within the aerofoil section, so |y| is at
    # most the local half-thickness (~0.05 c).  A face out in the wrap/farfield
    # reaches |y| ~ R = 16.1.  0.2 separates them with two orders of margin.
    near = np.abs(C[:, 1]) <= 0.2
    print(f"  of which, INSIDE the aerofoil envelope (|y| <= 0.2, i.e. the TIP FILL "
          f"proper): {int((tip & near).sum())}")
    print(f"            OUT in the wrap / farfield (|y| >  0.2)               "
          f"     : {int((tip & ~near).sum())}")
    for nm, sel in (("ALL", np.ones(len(C), bool)), ("outboard", tip), ("inboard", ~tip),
                    ("tipfill", tip & near), ("outb-wrap", tip & ~near)):
        if sel.sum() == 0:
            continue
        c = C[sel]
        print(f"    {nm:9s} n={int(sel.sum()):6d}  x[{c[:,0].min():9.4f},{c[:,0].max():9.4f}]"
              f"  y[{c[:,1].min():9.5f},{c[:,1].max():9.5f}]"
              f"  z[{c[:,2].min():9.5f},{c[:,2].max():9.5f}]")
    return C


def selftest(case, z_tip):
    P = read_points(f"{case}/constant/polyMesh/points")
    F = read_faces(f"{case}/constant/polyMesh/faces")
    ids = read_set(f"{case}/constant/polyMesh/sets/nonOrthoFaces")
    assert len(ids) > 0, "SELFTEST NEEDS A NON-EMPTY SET"
    c0 = centroids(P, F, ids[:1])[0]
    off = np.array([1.234e-03, -5.678e-03, 9.012e-03])
    P2 = P.copy(); P2[F[ids[0]]] += off
    c1 = centroids(P2, F, ids[:1])[0]
    d = c1 - c0
    assert np.allclose(d, off, atol=1e-12), f"PLANT NOT SEEN: moved {d}, planted {off}"
    print(f"  PLANT SEEN: centroid moved by {d} == planted {off}")
    empty = report(case, z_tip, P, F, np.array([], dtype=np.int64))
    assert empty is None, "empty set must report NO FLAGGED FACES"
    print("  SELFTEST PASS: reader can see a non-zero displacement and reports an empty set as empty")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest(sys.argv[1], float(sys.argv[2]))
    else:
        report(sys.argv[1], float(sys.argv[2]))
