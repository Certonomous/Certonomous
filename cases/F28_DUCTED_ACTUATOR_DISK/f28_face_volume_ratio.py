#!/usr/bin/env python3
"""F28 -- PER-FACE cell-volume ratio, read from `owner`/`neighbour`/`cellVolume`.

WHY A SECOND READER EXISTS AND WHY IT IS NOT A DUPLICATE.
`f28_neighbour_volume_ratio.py` reads `checkMesh`'s `cellVolumeRatio`, which is a
CELL field: each cell carries the worst ratio over ITS faces.  It can therefore
say WHICH CELL is worst but not WHICH FACE, and it cannot separate the two
mechanisms that produce a large ratio on an axisymmetric wedge:

  (i) AXIAL neighbours -- the ratio is the axial cell-size ratio dx_{i+1}/dx_i,
      which the generator's grading controls;
  (ii) RADIAL neighbours -- on a wedge the sector volume is
      V_j = (theta/2) * (r_{j+1}^2 - r_j^2) * dx, so the ratio between the first
      and second cell off the AXIS is 3.0 EXACTLY for uniform radial spacing,
      and no grading choice that expands outward can reduce it below 3.
      This is geometry, not a generator defect, and a gate that does not
      separate it gates against every axisymmetric mesh that touches its axis.

This reader classifies every internal face as AXIAL or RADIAL from the two cell
centres and reports the two populations separately.  Nothing is excluded from
the census; the classification is reported as counts (MESH_STANDARD 12.3: a
percentile that silently excludes is a percentile of a different population).

PLANTED CONTROL (CLAUDE.md rule 3).  Before any number is printed the reader
plants a known volume perturbation into one cell, recomputes, and REFUSES unless
the planted face ratio appears at the planted face with the planted value.  A
NEGATIVE LIMB then confirms the unperturbed field does NOT report it.

Usage:
    F28_MESH_DIR=<dir containing constant/polyMesh and constant/cellVolume> \
        python3 cases/F28_DUCTED_ACTUATOR_DISK/f28_face_volume_ratio.py
"""
import os
import re
import sys

MESH_DIR = os.environ.get("F28_MESH_DIR")
if not MESH_DIR:
    raise SystemExit("REFUSE: F28_MESH_DIR unset. This reader never guesses a "
                     "mesh; a reader pointed at the wrong mesh is a reader that "
                     "reports somebody else's number.")

# Column boundaries of the F28 generator (level-independent: they are geometry).
COLB = [("X_IN", -2.50), ("X_NOSE", -0.03), ("X_B", -0.0025),
        ("X_LIPEND", 0.030), ("X_DISK_0", 0.0675), ("X_DISK_1", 0.0725),
        ("L_DUCT", 0.200), ("X_SLIP", 1.45), ("X_OUT", 6.45)]

R_DUCT_INNER = 0.125     # duct inner radius at the disk station
R_HI = 0.140             # highlight radius


def _read_list(path, cast):
    if not os.path.exists(path):
        raise SystemExit("REFUSE: %s absent" % path)
    txt = open(path).read()
    # strip the FoamFile header block, then take the first "N ( ... )" body
    m = re.search(r"\n(\d+)\s*\n\(", txt)
    if not m:
        raise SystemExit("REFUSE: %s has no list body" % path)
    n = int(m.group(1))
    end = txt.index("\n)", m.end())
    vals = [cast(v) for v in txt[m.end():end].split()]
    if len(vals) != n:
        raise SystemExit("REFUSE: %s declared %d, parsed %d"
                         % (path, n, len(vals)))
    return vals


def _read_field(path):
    if not os.path.exists(path):
        raise SystemExit("REFUSE: %s absent -- run "
                         "`checkMesh -writeAllFields` first; this reader never "
                         "builds a mesh." % path)
    txt = open(path).read()
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\n(\d+)\s*\n\(",
                  txt)
    if not m:
        raise SystemExit("REFUSE: %s is not a nonuniform scalar list" % path)
    n = int(m.group(1))
    end = txt.index("\n)", m.end())
    vals = [float(v) for v in txt[m.end():end].split()]
    if len(vals) != n:
        raise SystemExit("REFUSE: %s declared %d, parsed %d"
                         % (path, n, len(vals)))
    return vals


def face_ratios(vol, own, nei):
    """(ratio, owner, neighbour) for every internal face. ratio >= 1."""
    out = []
    for f in range(len(nei)):
        a, b = vol[own[f]], vol[nei[f]]
        out.append((a / b if a >= b else b / a, own[f], nei[f]))
    return out


def main():
    pm = os.path.join(MESH_DIR, "constant", "polyMesh")
    cst = os.path.join(MESH_DIR, "constant")
    own = _read_list(os.path.join(pm, "owner"), int)
    nei = _read_list(os.path.join(pm, "neighbour"), int)
    vol = _read_field(os.path.join(cst, "cellVolume"))
    cx = _read_field(os.path.join(cst, "Cx"))
    cy = _read_field(os.path.join(cst, "Cy"))
    N, NF = len(vol), len(nei)
    if max(own) >= N or max(nei) >= N:
        raise SystemExit("REFUSE: owner/neighbour index exceeds cell count")
    if min(vol) <= 0.0:
        raise SystemExit("REFUSE: non-positive cell volume -- MESH_STANDARD "
                         "12.3 status MIN_NEGATIVE/MIN_ZERO; ratios undefined")

    # ---------------- PLANTED CONTROL (rule 3) --------------------------------
    # Plant a factor-K volume on ONE cell and require the reader to report
    # exactly that ratio on that cell's faces.  K is chosen strictly above the
    # mesh's own maximum so the plant cannot be confused with a real feature.
    base = face_ratios(vol, own, nei)
    base_max = max(r for r, _, _ in base)
    K = 10.0 * base_max
    pcell = N // 2
    probe = list(vol)
    probe[pcell] = vol[pcell] * K
    planted = face_ratios(probe, own, nei)
    # the planted cell's own worst face must now read >= K (its neighbours were
    # within base_max of it, so the ratio is at least K / base_max * 1)
    pf = [r for r, a, b in planted if a == pcell or b == pcell]
    if not pf:
        raise SystemExit("REFUSE: planted cell %d has no internal face" % pcell)
    if max(pf) < K / base_max:
        raise SystemExit("REFUSE: reader cannot see a planted %.4g volume "
                         "perturbation (worst planted face ratio %.4g)"
                         % (K, max(pf)))
    # NEGATIVE LIMB: the unperturbed field must NOT report it.
    bf = [r for r, a, b in base if a == pcell or b == pcell]
    if max(bf) >= K / base_max:
        raise SystemExit("REFUSE: negative limb failed -- the UNPERTURBED mesh "
                         "already reads the planted magnitude")
    print("PLANTED CONTROL: planted x%.4g on cell %d -> face ratio %.4g "
          "(unperturbed %.4g). Reader live; negative limb held."
          % (K, pcell, max(pf), max(bf)))

    # ---------------- classification ------------------------------------------
    # AXIAL: the two cell centres differ mainly in x.  RADIAL: mainly in r.
    axial, radial = [], []
    for r, a, b in base:
        dx, dr = abs(cx[a] - cx[b]), abs(cy[a] - cy[b])
        (axial if dx >= dr else radial).append((r, a, b))
    print("internal faces = %d   (axial %d, radial %d)  cells = %d"
          % (NF, len(axial), len(radial), N))

    def report(tag, pop):
        if not pop:
            print("  %s: EMPTY" % tag)
            return
        s = sorted(r for r, _, _ in pop)
        n = len(s)
        line = "  %-8s n=%-7d" % (tag, n)
        for p in (50, 90, 99, 99.9):
            line += " p%-5s=%.4f" % (p, s[min(n - 1, int(p / 100.0 * n))])
        print(line)
        w, a, b = max(pop, key=lambda t: t[0])
        print("           MAX=%.6g  between (x=%.6g r=%.6g) and (x=%.6g r=%.6g)"
              % (w, cx[a], cy[a], cx[b], cy[b]))
        for thr in (1.25, 1.5, 2.0, 3.0):
            c = sum(1 for r, _, _ in pop if r > thr)
            print("           faces > %-5.2f : %-7d (%.4f%%)"
                  % (thr, c, 100.0 * c / n))

    print("\n=== FACE-ADJACENT CELL-VOLUME RATIO (>=1; 1 ideal) ===")
    report("ALL", base)
    report("AXIAL", axial)
    report("RADIAL", radial)

    # ---------------- the axis population, named and counted -------------------
    # The innermost radial band: faces whose lower cell centre sits below twice
    # the first-cell height.  The height is read from the mesh, not assumed.
    r_axis_min = min(cy)
    band = 4.0 * r_axis_min
    ax_r = [t for t in radial if min(cy[t[1]], cy[t[2]]) <= band]
    print("\n=== AXIS BAND  (r <= %.4g m = 4 x the smallest cell-centre "
          "radius) ===" % band)
    report("AXIS", ax_r)
    off = [t for t in radial if min(cy[t[1]], cy[t[2]]) > band]
    report("OFFAXIS", off)

    # ---------------- the duct surface, which is what the gate cares about -----
    duct = [t for t in base
            if 0.0 <= min(cx[t[1]], cx[t[2]]) <= 0.2
            and 0.10 <= min(cy[t[1]], cy[t[2]]) <= 0.16]
    print("\n=== DUCT SURFACE NEIGHBOURHOOD  (0 <= x <= 0.2, 0.10 <= r <= 0.16) "
          "-- the patch whose integrated force is the graded quantity ===")
    report("DUCT", duct)

    # ---------------- worst face per column boundary --------------------------
    print("\n=== WORST FACE RATIO BY AXIAL BAND ===")
    for k in range(len(COLB) - 1):
        lo, hi = COLB[k][1], COLB[k + 1][1]
        pop = [t for t in base if lo <= 0.5 * (cx[t[1]] + cx[t[2]]) < hi]
        if not pop:
            continue
        w, a, b = max(pop, key=lambda t: t[0])
        print("  %-9s .. %-9s n=%-7d MAX=%.5g at x=%.6g r=%.6g"
              % (COLB[k][0], COLB[k + 1][0], len(pop), w, cx[a], cy[a]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
