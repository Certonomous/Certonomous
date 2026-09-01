#!/usr/bin/env python3
"""F28 -- does the tail-apex volume-jump MECHANISM reproduce from the mesh?

The claim under test, written before this script existed: the dominant
face-adjacent cell-volume jump is the axisymmetric r-weighting across the
centrebody tail-cone apex, and its size is

    V_upstream / V_downstream  =  1 + 2 r_hub / h                        (S)

for an upstream innermost cell spanning [r_hub, r_hub + h] against a downstream
one spanning [0, h], at equal axial size.

(S) IS AN APPROXIMATION AND THIS SCRIPT EXISTS TO SAY BY HOW MUCH.  The exact
wedge relation, with no assumption that the two cells share dx or h, is

    V = (theta/2) (r_2^2 - r_1^2) dx                                     (E)

Both are evaluated here against the SAME face, from the SAME polyMesh, with the
vertex radii read out of `points` -- NOT from cell centres.  A cell centre is a
VOLUME CENTROID: for a wedge sector spanning [0, h] it sits at 2h/3, not h/2,
so substituting a reported centre into (S) as if it were h/2 overstates h by
4/3 and is exactly the error this script was written to expose.

Standing rule 3: the reader plants a known perturbation into the volume field
and refuses if it cannot see it, before any number is reported.

Usage:
    F28_MESH_DIR=<dir with constant/polyMesh and constant/cellVolume> \
        python3 cases/F28_DUCTED_ACTUATOR_DISK/f28_apex_mechanism_check.py
"""
import math
import os
import re
import sys

MESH_DIR = os.environ.get("F28_MESH_DIR")
if not MESH_DIR:
    raise SystemExit("REFUSE: F28_MESH_DIR unset.")

WEDGE_DEG = 5.0
L_DUCT = 0.200


def _list(path, cast):
    txt = open(path).read()
    m = re.search(r"\n(\d+)\s*\n\(", txt)
    if not m:
        raise SystemExit("REFUSE: %s has no list body" % path)
    n = int(m.group(1))
    end = txt.index("\n)", m.end())
    body = txt[m.end():end]
    vals = [cast(v) for v in body.split()]
    if cast is int and len(vals) != n:
        raise SystemExit("REFUSE: %s declared %d, parsed %d"
                         % (path, n, len(vals)))
    return vals, n, body


def read_points(path):
    _, n, body = _list(path, str)
    pts = [tuple(float(v) for v in t.strip("()").split())
           for t in re.findall(r"\(([^)]*)\)", body)]
    if len(pts) != n:
        raise SystemExit("REFUSE: points declared %d, parsed %d" % (n, len(pts)))
    return pts


def read_faces(path):
    _, n, body = _list(path, str)
    faces = [[int(v) for v in t.split()]
             for t in re.findall(r"\d+\(([^)]*)\)", body)]
    if len(faces) != n:
        raise SystemExit("REFUSE: faces declared %d, parsed %d" % (n, len(faces)))
    return faces


def read_field(path):
    txt = open(path).read()
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\n(\d+)\s*\n\(",
                  txt)
    if not m:
        raise SystemExit("REFUSE: %s is not a nonuniform scalar list" % path)
    n = int(m.group(1))
    end = txt.index("\n)", m.end())
    vals = [float(v) for v in txt[m.end():end].split()]
    if len(vals) != n:
        raise SystemExit("REFUSE: %s declared %d, parsed %d" % (path, n, len(vals)))
    return vals


def main():
    pm = os.path.join(MESH_DIR, "constant", "polyMesh")
    pts = read_points(os.path.join(pm, "points"))
    faces = read_faces(os.path.join(pm, "faces"))
    own, _, _ = _list(os.path.join(pm, "owner"), int)
    nei, _, _ = _list(os.path.join(pm, "neighbour"), int)
    vol = read_field(os.path.join(MESH_DIR, "constant", "cellVolume"))

    # cell -> set of its point ids, from the faces that bound it
    cellpts = {}
    for f, ps in enumerate(faces):
        for c in (own[f], nei[f] if f < len(nei) else -1):
            if c >= 0:
                cellpts.setdefault(c, set()).update(ps)

    def ends(c):
        """((ri_L, ro_L), (ri_R, ro_R), x_L, x_R) for a structured wedge cell.

        NOT min/max over all vertices.  The apex cell is SLANTED: its inner
        edge follows the tail cone from r_hub(x_L) down to 0 at x_R, so a
        min/max over its vertices reports a radial span of [0, 4.57e-04] and
        turns a thin slanted quad into a fat rectangle -- 34x too much volume.
        The cell is resolved into its LEFT and RIGHT faces instead, and each
        face's own radial span is read.
        """
        vs = sorted(((pts[p_][0], math.hypot(pts[p_][1], pts[p_][2]))
                     for p_ in cellpts[c]))
        # The corners do NOT sit at exactly two x values: blockMesh blends a
        # block's interior from its four edges, so the grid lines TILT -- the
        # very mechanism this generator's header documents at 84.62 degrees.
        # The two faces are separated at the LARGEST GAP in x, and the residual
        # tilt inside each group is reported so it is priced, not hidden.
        gaps = [(vs[i + 1][0] - vs[i][0], i) for i in range(len(vs) - 1)]
        _, k = max(gaps)
        L = [r for _, r in vs[:k + 1]]
        R = [r for _, r in vs[k + 1:]]
        xL = sum(x for x, _ in vs[:k + 1]) / float(k + 1)
        xR = sum(x for x, _ in vs[k + 1:]) / float(len(vs) - k - 1)
        tilt = max(max(x for x, _ in vs[:k + 1]) - min(x for x, _ in vs[:k + 1]),
                   max(x for x, _ in vs[k + 1:]) - min(x for x, _ in vs[k + 1:]))
        if not L or not R:
            raise SystemExit("REFUSE: cell %d did not split into two faces" % c)
        return (min(L), max(L)), (min(R), max(R)), xL, xR, tilt

    def wedge_volume(c):
        """EXACT wedge volume of a linearly-varying annular sector.

        V = (theta/2) * dx * INT_0^1 [ r_out(t)^2 - r_in(t)^2 ] dt with r_in and
        r_out linear in t, and INT_0^1 (A+Bt)^2 dt = A^2 + A B + B^2/3.
        """
        (riL, roL), (riR, roR), xL, xR, _t = ends(c)
        def q(A, B):
            return A * A + A * B + B * B / 3.0
        return (0.5 * math.radians(WEDGE_DEG) * (xR - xL)
                * (q(roL, roR - roL) - q(riL, riR - riL)))

    # ---- PLANTED CONTROL -----------------------------------------------------
    ratios = []
    for f in range(len(nei)):
        a, b = vol[own[f]], vol[nei[f]]
        ratios.append((a / b if a >= b else b / a, f))
    base_max, base_f = max(ratios)
    # K is a FIXED factor chosen strictly above the mesh's own maximum, so the
    # planted signal cannot be confused with a real feature of the mesh.
    K = 1000.0
    if base_max >= K:
        raise SystemExit("REFUSE: the mesh's own maximum %.4g is not below the "
                         "plant factor %.4g; the plant would be indistinguish"
                         "able from the mesh" % (base_max, K))
    probe = list(vol)
    pc = own[base_f]
    probe[pc] = vol[pc] * K
    seen = max((probe[own[f]] / probe[nei[f]] if probe[own[f]] >= probe[nei[f]]
                else probe[nei[f]] / probe[own[f]])
               for f in range(len(nei))
               if own[f] == pc or nei[f] == pc)
    before = max(r for r, f in ratios if own[f] == pc or nei[f] == pc)
    if seen < K:
        raise SystemExit("REFUSE: reader cannot see a planted x%.4g "
                         "(worst planted face %.4g)" % (K, seen))
    if before >= K:
        raise SystemExit("REFUSE: negative limb failed -- the UNPERTURBED mesh "
                         "already reads the planted magnitude (%.4g)" % before)
    print("PLANTED CONTROL: planted x%.4g on cell %d -> %.5g (unperturbed "
          "%.5g). Reader live; negative limb held." % (K, pc, seen, before))

    cu, cd = own[base_f], nei[base_f]
    if vol[cu] < vol[cd]:
        cu, cd = cd, cu
    (uiL, uoL), (uiR, uoR), uxL, uxR, utilt = ends(cu)
    (diL, doL), (diR, doR), dxL, dxR, dtilt = ends(cd)

    print("\nWORST INTERNAL FACE = face %d, MEASURED volume ratio %.6f"
          % (base_f, base_max))
    print("  larger  cell %d:  left face r in [%.6e, %.6e] at x=%.6f"
          % (cu, uiL, uoL, uxL))
    print("                    right face r in [%.6e, %.6e] at x=%.6f"
          % (uiR, uoR, uxR))
    print("  smaller cell %d:  left face r in [%.6e, %.6e] at x=%.6f"
          % (cd, diL, doL, dxL))
    print("                    right face r in [%.6e, %.6e] at x=%.6f"
          % (diR, doR, dxR))
    print("  THE UPSTREAM CELL CONTAINS THE APEX: its inner edge runs %.6e -> "
          "%.6e within the cell." % (uiL, uiR))
    print("  residual in-face x tilt: upstream %.3e m, downstream %.3e m "
          "(against dx_up %.3e)" % (utilt, dtilt, uxR - uxL))

    Vu, Vd = wedge_volume(cu), wedge_volume(cd)
    print("\n(E) EXACT LINEARLY-VARYING WEDGE SECTOR, from vertex radii only")
    print("    V_up   = %.6e  vs solver-reported %.6e   (%.3f%% apart)"
          % (Vu, vol[cu], 100.0 * abs(Vu - vol[cu]) / vol[cu]))
    print("    V_down = %.6e  vs solver-reported %.6e   (%.3f%% apart)"
          % (Vd, vol[cd], 100.0 * abs(Vd - vol[cd]) / vol[cd]))
    print("    ratio  = %.6f  vs MEASURED %.6f            (%.3f%% apart)"
          % (Vu / Vd, base_max, 100.0 * abs(Vu / Vd - base_max) / base_max))

    r_mean = 0.5 * (uiL + uiR)
    h_up = 0.5 * ((uoL - uiL) + (uoR - uiR))
    h_dn = 0.5 * ((doL - diL) + (doR - diR))
    S = 1.0 + 2.0 * r_mean / h_dn
    print("\n(S) SIMPLIFIED CLAIM  1 + 2 r_in_mean / h")
    print("    r_in_mean = %.6e  -- the AXIAL MEAN of the cone edge over the"
          % r_mean)
    print("                        apex cell, = TAIL_SLOPE * dx_up / 2, NOT")
    print("                        r_hub evaluated at the cell centre")
    print("    h         = %.6e  -- VERTEX radial extent of the axis cell,"
          % h_dn)
    print("                        NOT twice its reported centre")
    print("    S         = %.6f  vs MEASURED %.6f   (%.3f%% apart)"
          % (S, base_max, 100.0 * abs(S - base_max) / base_max))
    print("    approximations priced: h_up/h_down = %.6f, dx_up/dx_down = %.6f"
          % (h_up / h_dn, (uxR - uxL) / (dxR - dxL)))

    Cy = read_field(os.path.join(MESH_DIR, "constant", "Cy"))
    print("\nTHE SUBSTITUTION THAT WAS REPORTED EARLIER, AND ITS TWO ERRORS")
    Cx = read_field(os.path.join(MESH_DIR, "constant", "Cx"))
    bad_r = 0.375 * (0.200 - Cx[cu])
    bad_h = 2.0 * Cy[cd]
    print("    r_hub at the CELL CENTRE x=%.6f  = %.6e  (+%.1f%% vs the mean)"
          % (Cx[cu], bad_r, 100.0 * (bad_r - r_mean) / r_mean))
    print("    h from 2 x reported centre       = %.6e  (+%.1f%% vs vertex h)"
          % (bad_h, 100.0 * (bad_h - h_dn) / h_dn))
    print("    the wedge centroid of [0,h] is 2h/3: 2/3 x %.6e = %.6e vs "
          "reported centre %.6e" % (h_dn, 2.0 * h_dn / 3.0, Cy[cd]))
    print("    1 + 2 x %.6e / %.6e = %.4f  -- the reported figure, right to"
          % (bad_r, bad_h, 1.0 + 2.0 * bad_r / bad_h))
    print("    2%% BY CANCELLATION OF TWO ~+33%% ERRORS, not by substitution.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
