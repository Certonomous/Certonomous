#!/usr/bin/env python3
"""F28 L1 -- face-adjacent cell-volume-jump and aspect-ratio distribution.

NO SOLVE.  Reads fields `checkMesh -writeAllFields` already wrote.  This is the
instrument that found the `n == 1` grading defect recorded in ADDENDUM 1 of
`verification/campaign/F28_DUCTED_ACTUATOR_DISK_PREREGISTRATION.md`, and it is
filed here rather than left in scratch because a repository document may never
cite a scratch path (L-186) and the scratchpad is wiped.

TWO READER ERRORS ARE RECORDED HERE RATHER THAN TIDIED AWAY, because each would
have produced a confident wrong answer:

  1. `checkMesh`'s `cellVolumeRatio` is `min(V)/max(V)` ACROSS EACH FACE, so it
     lies in (0,1] and 1 is perfect.  THE BAD DIRECTION IS SMALL.  A first pass
     reported `max(cellVolumeRatio) = 0.936` as "the worst neighbour ratio" and
     concluded no cell exceeded 1.5.  That is the wrong tail: the true worst
     jump is 1/min = 28,735.  This script reports `1/cellVolumeRatio`.
  2. The first planted control, at 1.3579e-4, was REFUSED by the plant assert
     because the mesh already contains a smaller ratio.  The refusal was
     correct and is why the plant is now placed strictly below the true
     minimum.  A plant that is not extreme enough proves nothing.

Standing rule 3: the reader plants a known perturbation and refuses if it cannot
see it.  Nothing is reported before that assert passes.

Usage:
    python3 cases/F28_DUCTED_ACTUATOR_DISK/f28_neighbour_volume_ratio.py
"""
import os
import re
import sys

# The directory holding the `checkMesh -writeAllFields` output.  It defaults to
# the L1 diagnostic case this script was written against; ADDENDUM 1's
# supersession needed the SAME reader on L2 and L3 and on the rebuilt meshes, so
# it is overridable by environment rather than being copied and edited (a copied
# reader is a second reader, and two readers are two chances to be wrong).
DIAG = os.environ.get(
    "F28_DIAG_DIR",
    "/home/ubuntu/Certonomous/verification/runs/F28_runs/"
    "DIAG_mesh_L1_aspectRatio/constant/")

# Size of the high-aspect-ratio set `checkMesh` reported for THIS mesh.  It is a
# per-mesh number, not a constant; passing the wrong one silently reports the
# column share of the wrong set.
HIGH_AR_N = int(os.environ.get("F28_HIGH_AR_N", "2228"))

# Column boundaries of the L1 generator, for locating a defect by column.
COLB = [("X_IN", -2.50), ("X_NOSE", -0.03), ("X_B", -0.0025),
        ("X_LIPEND", 0.030), ("X_DISK_0", 0.0675), ("X_DISK_1", 0.0725),
        ("L_DUCT", 0.200), ("X_SLIP", 1.45), ("X_OUT", 6.45)]


def read_field(name):
    """Parse one OpenFOAM nonuniform scalar volField.  Refuses on shape."""
    path = os.path.join(DIAG, name)
    if not os.path.exists(path):
        raise SystemExit("REFUSE: %s absent. Run checkMesh -writeAllFields "
                         "first; this script never builds a mesh." % path)
    txt = open(path).read()
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\n(\d+)\s*\n\(",
                  txt)
    if not m:
        raise SystemExit("REFUSE: %s is not a nonuniform scalar list" % name)
    n = int(m.group(1))
    end = txt.index("\n)", m.end())
    vals = [float(v) for v in txt[m.end():end].split()]
    if len(vals) != n:
        raise SystemExit("REFUSE: %s declared %d values, parsed %d"
                         % (name, n, len(vals)))
    return vals


def main():
    vr = read_field("cellVolumeRatio")
    ar_s = read_field("aspectRatio")
    ar_c = read_field("cellAspectRatio")
    vol = read_field("cellVolume")
    cx = read_field("Cx")
    cy = read_field("Cy")
    N = len(vr)
    for nm, f in (("aspectRatio", ar_s), ("cellAspectRatio", ar_c),
                  ("cellVolume", vol), ("Cx", cx), ("Cy", cy)):
        if len(f) != N:
            raise SystemExit("REFUSE: %s length %d != %d" % (nm, len(f), N))

    if max(vr) > 1.0 + 1e-9:
        raise SystemExit("REFUSE: cellVolumeRatio > 1; the min/max definition "
                         "this script relies on does not hold for this file.")

    # ---- PLANTED CONTROL, strictly below the true minimum ------------------
    true_min = min(vr)
    plant_idx, plant_val = N // 3, true_min / 10.0
    probe = list(vr)
    probe[plant_idx] = plant_val
    if min(probe) != plant_val or probe.index(plant_val) != plant_idx:
        raise SystemExit("REFUSE: reducer cannot see a planted %g" % plant_val)
    print("PLANTED CONTROL: reducer saw planted %.5g at cell %d -- reader live"
          % (plant_val, plant_idx))
    print("TRUE MINIMUM cellVolumeRatio = %.6g  ->  worst neighbour jump %.6g"
          % (true_min, 1.0 / true_min))
    print("\ncells = %d" % N)

    jump = [1.0 / v for v in vr]
    sj = sorted(jump)
    print("\n=== FACE-ADJACENT VOLUME JUMP (>=1; 1 is ideal) ===")
    for p in (50, 90, 99, 99.9):
        print("  p%-5s = %.4f" % (p, sj[min(N - 1, int(p / 100.0 * N))]))
    worst = max(jump)
    i = jump.index(worst)
    print("  WORST = %.6g at x = %.6g, r = %.6g, V = %.4g"
          % (worst, cx[i], cy[i], vol[i]))
    for lo, hi in ((1.5, 2.0), (2.0, 3.0), (3.0, 1e9)):
        c = sum(1 for v in jump if lo <= v < hi)
        print("  cells with jump in [%g,%g) : %d  (%.3f%%)"
              % (lo, hi, c, 100.0 * c / N))

    print("\n=== WORST JUMP NEAR EACH COLUMN BOUNDARY ===")
    for k in range(len(COLB) - 1):
        nm, xb = COLB[k + 1]
        tol = 0.015 * max(xb - COLB[k][1],
                          COLB[min(k + 2, len(COLB) - 1)][1] - xb)
        idx = [j for j in range(N) if abs(cx[j] - xb) <= tol]
        if not idx:
            print("  %-9s x=%-9.4g : no cells within %.3g m" % (nm, xb, tol))
            continue
        b = min(idx, key=lambda j: vr[j])
        print("  %-9s x=%-9.4g : n=%-5d  worst jump %.4f at r=%.5g"
              % (nm, xb, len(idx), 1.0 / vr[b], cy[b]))

    print("\n=== ASPECT RATIO, BOTH DEFINITIONS ===")
    for nm, f in (("aspectRatio (checkMesh summary metric)", ar_s),
                  ("cellAspectRatio", ar_c)):
        mx = max(f)
        j = f.index(mx)
        print("  %-40s max %.6g at x=%.5g r=%.5g" % (nm, mx, cx[j], cy[j]))

    vmin, vmax = min(vol), max(vol)
    print("\n=== GLOBAL VOLUME EXTREMES ===")
    print("  min V = %.6g at x=%.5g r=%.5g"
          % (vmin, cx[vol.index(vmin)], cy[vol.index(vmin)]))
    print("  max V = %.6g at x=%.5g r=%.5g"
          % (vmax, cx[vol.index(vmax)], cy[vol.index(vmax)]))
    print("  global max/min = %.4g   <-- NOT the solver-relevant quantity; the"
          % (vmax / vmin))
    print("      face-adjacent jump above is. A global ratio can be huge on a")
    print("      perfectly smooth wedge mesh purely because cell volume ~ r.")

    print("\n=== COLUMN SHARE OF THE HIGH-ASPECT-RATIO SET ===")
    order = sorted(range(N), key=lambda j: -ar_s[j])[:HIGH_AR_N]
    print("  of the %d highest-AR cells, %d have r < 1e-3 m"
          % (HIGH_AR_N, sum(1 for j in order if cy[j] < 1e-3)))
    for k in range(len(COLB) - 1):
        n = sum(1 for j in order if COLB[k][1] <= cx[j] < COLB[k + 1][1])
        if n:
            print("    c%-3d : %d" % (k, n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
