#!/usr/bin/env python3
"""Find the WORST non-orthogonal face in a polyMesh and say exactly where it is.

WHY.  checkMesh reports a maximum but not which face produced it, and two
plausible mechanisms for F1's 81.94 deg (the butterfly's 180 deg degenerate strip
corners, and the sharp trailing-edge wedge) were BOTH falsified by dial sweeps
that failed to move the maximum.  This stops modelling it and measures it: it
recomputes every internal face's non-orthogonality with OpenFOAM's own cell-centre
algorithm, takes the argmax, and prints that face's centroid, its owner and
neighbour cell centres and the offending angle.

PLANTED CONTROL (CLAUDE.md rule 3), two independent legs:
  (a) AGREEMENT -- the recomputed maximum must match the value checkMesh wrote in
      log.checkMesh to < 0.05 deg.  A reader that cannot reproduce an independent
      implementation's number is refused.
  (b) DISPLACEMENT -- one point of the winning face is moved by a known offset and
      the recomputed angle for that face MUST change by more than 1e-6 deg.  A
      reader that cannot see a perturbation is refused.
Both must pass or the script exits 2 WITHOUT printing a result.
"""
import re
import sys

import numpy as np


def _body(path):
    t = open(path, errors="replace").read()
    return t[t.index("}", t.index("FoamFile")) + 1:]


def read_points(p):
    b = _body(p)
    n = int(re.search(r"^\s*(\d+)\s*$", b, re.M).group(1))
    P = np.array(re.findall(r"\(\s*(-?[\d.eE+-]+)\s+(-?[\d.eE+-]+)\s+(-?[\d.eE+-]+)\s*\)", b), dtype=float)
    assert len(P) == n, f"points: header {n}, parsed {len(P)}"
    return P


def read_faces(p):
    b = _body(p)
    n = int(re.search(r"^\s*(\d+)\s*$", b, re.M).group(1))
    F = [np.fromstring(m.group(1), sep=" ", dtype=np.int64)
         for m in re.finditer(r"(\d+)\s*\(([\d\s]+)\)", b)]
    F = [np.fromstring(m.group(2), sep=" ", dtype=np.int64)
         for m in re.finditer(r"(\d+)\s*\(([\d\s]+)\)", b)]
    assert len(F) == n, f"faces: header {n}, parsed {len(F)}"
    return F


def read_labels(p):
    b = _body(p)
    m = re.search(r"^\s*(\d+)\s*$", b, re.M)
    n = int(m.group(1))
    tail = b[b.index("(", m.end()) + 1:]
    L = np.fromstring(tail[:tail.index(")")], sep=" ", dtype=np.int64)
    assert len(L) == n, f"labels: header {n}, parsed {len(L)}"
    return L


def face_centres_areas(P, F):
    """OpenFOAM primitiveMeshFaceCentresAndAreas: triangle fan about the average point."""
    Cf = np.zeros((len(F), 3)); Sf = np.zeros((len(F), 3))
    for i, f in enumerate(F):
        pts = P[f]
        if len(f) == 3:
            Cf[i] = pts.mean(axis=0)
            Sf[i] = 0.5 * np.cross(pts[1] - pts[0], pts[2] - pts[0])
            continue
        pAvg = pts.mean(axis=0)
        a = pts; b = np.roll(pts, -1, axis=0)
        c = (a + b + pAvg) / 3.0
        n = 0.5 * np.cross(b - a, pAvg - a)
        mag = np.linalg.norm(n, axis=1)
        s = mag.sum()
        if s < 1e-300:
            Cf[i] = pAvg; Sf[i] = n.sum(axis=0)
        else:
            Cf[i] = (c * mag[:, None]).sum(axis=0) / s
            Sf[i] = n.sum(axis=0)
    return Cf, Sf


def cell_centres(P, F, own, nei, ncell):
    """OpenFOAM primitiveMeshCellCentresAndVols: pyramid-weighted."""
    Cf, Sf = face_centres_areas(P, F)
    cEst = np.zeros((ncell, 3)); nf = np.zeros(ncell)
    np.add.at(cEst, own, Cf); np.add.at(nf, own, 1)
    np.add.at(cEst, nei, Cf[:len(nei)]); np.add.at(nf, nei, 1)
    cEst /= nf[:, None]
    Cc = np.zeros((ncell, 3)); V = np.zeros(ncell)
    # owner side
    pyr3Vo = np.einsum('ij,ij->i', Cf - cEst[own], Sf)
    pcO = (3.0 / 4.0) * Cf + (1.0 / 4.0) * cEst[own]
    np.add.at(Cc, own, pyr3Vo[:, None] * pcO); np.add.at(V, own, pyr3Vo)
    # neighbour side (normal reversed)
    ni = len(nei)
    pyr3Vn = -np.einsum('ij,ij->i', Cf[:ni] - cEst[nei], Sf[:ni])
    pcN = (3.0 / 4.0) * Cf[:ni] + (1.0 / 4.0) * cEst[nei]
    np.add.at(Cc, nei, pyr3Vn[:, None] * pcN); np.add.at(V, nei, pyr3Vn)
    good = np.abs(V) > 1e-300
    Cc[good] /= V[good][:, None]
    Cc[~good] = cEst[~good]
    return Cc, Cf, Sf, V / 3.0


def nonortho(P, F, own, nei, ncell):
    Cc, Cf, Sf, _ = cell_centres(P, F, own, nei, ncell)
    ni = len(nei)
    d = Cc[nei] - Cc[own[:ni]]
    S = Sf[:ni]
    dn = np.linalg.norm(d, axis=1); Sn = np.linalg.norm(S, axis=1)
    ok = (dn > 1e-300) & (Sn > 1e-300)
    cosa = np.ones(ni)
    cosa[ok] = np.einsum('ij,ij->i', d[ok], S[ok]) / (dn[ok] * Sn[ok])
    return np.degrees(np.arccos(np.clip(cosa, -1.0, 1.0))), Cc, Cf


def load(case):
    pm = f"{case}/constant/polyMesh"
    P = read_points(f"{pm}/points"); F = read_faces(f"{pm}/faces")
    own = read_labels(f"{pm}/owner"); nei = read_labels(f"{pm}/neighbour")
    return P, F, own, nei, int(max(own.max(), nei.max())) + 1


if __name__ == "__main__":
    case = sys.argv[1]
    P, F, own, nei, ncell = load(case)
    ang, Cc, Cf = nonortho(P, F, own, nei, ncell)
    mine = float(np.nanmax(ang))
    ref = float(re.search(r"Mesh non-orthogonality Max:\s*(\S+)",
                          open(f"{case}/log.checkMesh").read()).group(1))
    print(f"{case}: {ncell} cells, {len(F)} faces, {len(nei)} internal")
    print(f"  CONTROL (a) AGREEMENT: recomputed max {mine:.4f} deg vs checkMesh {ref:.4f} deg"
          f"  |diff| = {abs(mine-ref):.5f}")
    if abs(mine - ref) >= 0.05:
        print("  REFUSED: reader does not reproduce checkMesh. No result printed."); sys.exit(2)
    k = int(np.nanargmax(ang))
    P2 = P.copy(); P2[F[k][0]] += np.array([0.0, 1.234e-04, 0.0])
    ang2, _, _ = nonortho(P2, F, own, nei, ncell)
    if not abs(ang2[k] - ang[k]) > 1e-6:
        print("  REFUSED: displacing a point of the winning face did not move its angle."); sys.exit(2)
    print(f"  CONTROL (b) DISPLACEMENT: moving one point of the winning face by 1.234e-04 in y")
    print(f"     moved its angle {ang[k]:.4f} -> {ang2[k]:.4f} deg.  PLANT SEEN.")
    print(f"\n  WORST INTERNAL FACE  id={k}  angle={ang[k]:.4f} deg")
    print(f"     face centroid   ({Cf[k][0]:.6f}, {Cf[k][1]:.6f}, {Cf[k][2]:.6f})")
    print(f"     owner cell   {own[k]:8d}  centre ({Cc[own[k]][0]:.6f}, {Cc[own[k]][1]:.6f}, {Cc[own[k]][2]:.6f})")
    print(f"     neighbour    {nei[k]:8d}  centre ({Cc[nei[k]][0]:.6f}, {Cc[nei[k]][1]:.6f}, {Cc[nei[k]][2]:.6f})")
    d = Cc[nei[k]] - Cc[own[k]]
    print(f"     owner->neighbour vector ({d[0]:.6e}, {d[1]:.6e}, {d[2]:.6e})")
    for t in (70.0, 80.0, 85.0, 89.0):
        print(f"     faces above {t:5.1f} deg: {int((ang > t).sum())}")
    sel = ang > 70.0
    if sel.any():
        C = Cf[:len(nei)][sel]
        print(f"     >70 deg face centroids: x[{C[:,0].min():.5f},{C[:,0].max():.5f}]"
              f" y[{C[:,1].min():.6f},{C[:,1].max():.6f}] z[{C[:,2].min():.5f},{C[:,2].max():.5f}]")
