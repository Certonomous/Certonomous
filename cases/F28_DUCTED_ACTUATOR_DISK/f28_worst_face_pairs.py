#!/usr/bin/env python3
"""F28 L1 -- locate the worst face-adjacent volume jumps in the actual mesh.

NO SOLVE.  Pairs `constant/polyMesh/{owner,neighbour}` from the built L1 mesh
with the cell-volume and cell-centre fields `checkMesh -writeAllFields` wrote,
so the offending FACE can be named, not merely the offending cell.

This is the script that turned "the worst jump is at the c0|c1 interface" from a
number into a mechanism: the owner and neighbour centroids proved to be 0.0154 m
apart in x, which is impossible for two hexes in a column whose prescribed axial
spacing is 3.5e-4 m -- and that impossibility is what exposed the `n == 1`
grading defect recorded in ADDENDUM 1 of the frozen pre-registration.

SELF-CHECK, AND IT IS LOAD-BEARING: this recomputes `cellVolumeRatio` from the
connectivity and asserts it reproduces the field `checkMesh` wrote, cell by
cell.  Without it there is no evidence that the polyMesh and the written fields
describe the same mesh in the same cell order, and every pairing below would be
unfounded.  The comparison is RELATIVE at 1e-6 because the written field carries
8 significant digits; an absolute 1e-9 was tried first and refused 29,099 cells
whose values agreed to every digit the file records -- a tolerance artefact, not
a disagreement, recorded here so the loosening is visible rather than silent.

Usage:
    python3 cases/F28_DUCTED_ACTUATOR_DISK/f28_worst_face_pairs.py
"""
import os
import re
import sys

MESH = ("/home/ubuntu/Certonomous/verification/runs/F28_runs/mesh_L1/"
        "constant/polyMesh/")
DIAG = ("/home/ubuntu/Certonomous/verification/runs/F28_runs/"
        "DIAG_mesh_L1_aspectRatio/constant/")


def read_scalar_field(path):
    if not os.path.exists(path):
        raise SystemExit("REFUSE: %s absent." % path)
    txt = open(path).read()
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\n(\d+)\s*\n\(",
                  txt)
    if not m:
        raise SystemExit("REFUSE: %s is not a nonuniform scalar list" % path)
    n = int(m.group(1))
    end = txt.index("\n)", m.end())
    v = [float(x) for x in txt[m.end():end].split()]
    if len(v) != n:
        raise SystemExit("REFUSE: %s declared %d, parsed %d" % (path, n, len(v)))
    return v


def read_label_list(path):
    if not os.path.exists(path):
        raise SystemExit("REFUSE: %s absent." % path)
    txt = open(path).read()
    m = re.search(r"\n(\d+)\s*\n\(", txt)
    n = int(m.group(1))
    end = txt.index("\n)", m.end())
    v = [int(x) for x in txt[m.end():end].split()]
    if len(v) != n:
        raise SystemExit("REFUSE: %s declared %d, parsed %d" % (path, n, len(v)))
    return v


def main():
    vol = read_scalar_field(DIAG + "cellVolume")
    vr_written = read_scalar_field(DIAG + "cellVolumeRatio")
    cx = read_scalar_field(DIAG + "Cx")
    cy = read_scalar_field(DIAG + "Cy")
    own = read_label_list(MESH + "owner")
    nei = read_label_list(MESH + "neighbour")
    N = len(vol)
    print("cells %d   faces %d   internal faces %d" % (N, len(own), len(nei)))

    recomputed = [1.0] * N
    for f in range(len(nei)):
        o, p = own[f], nei[f]
        r = min(vol[o], vol[p]) / max(vol[o], vol[p])
        if r < recomputed[o]:
            recomputed[o] = r
        if r < recomputed[p]:
            recomputed[p] = r

    bad = [i for i in range(N)
           if abs(recomputed[i] - vr_written[i]) > 1e-6 * max(1e-30,
                                                              vr_written[i])]
    if bad:
        raise SystemExit(
            "REFUSE: recomputation disagrees with the written field on %d "
            "cells (first %d: mine %.6g, written %.6g). The polyMesh and the "
            "written fields do not share a cell ordering; nothing here is "
            "reportable." % (len(bad), bad[0], recomputed[bad[0]],
                             vr_written[bad[0]]))
    print("SELF-CHECK PASSED: recomputed cellVolumeRatio == written field on "
          "all %d cells." % N)

    pairs = sorted(((max(vol[own[f]], vol[nei[f]])
                     / min(vol[own[f]], vol[nei[f]]), f, own[f], nei[f])
                    for f in range(len(nei))), reverse=True)

    print("\n=== THE 12 WORST FACE-ADJACENT VOLUME JUMPS ===")
    print("  jump      | owner   (x, r, V)               | neighbour (x, r, V)")
    for j, f, o, p in pairs[:12]:
        print("  %-9.4g | %8.5f %10.3e %9.3e | %8.5f %10.3e %9.3e"
              % (j, cx[o], cy[o], vol[o], cx[p], cy[p], vol[p]))

    j, f, o, p = pairs[0]
    dx, dr = abs(cx[o] - cx[p]), abs(cy[o] - cy[p])
    print("\n=== ORIENTATION OF THE WORST FACE ===")
    print("  centroid separation: dx = %.6g m, dr = %.6g m" % (dx, dr))
    print("  -> %s" % ("AXIAL: a constant-x interface between two columns"
                       if dx > dr else
                       "RADIAL: an interface inside one column"))
    print("  owner V = %.6g, neighbour V = %.6g" % (vol[o], vol[p]))
    if dx > 10.0 * 3.5e-4:
        print("  NOTE: dx exceeds ten times the prescribed axial spacing at "
              "this station.\n        Two hexes in a properly graded column "
              "cannot be this far apart.\n        THIS IS THE SIGNATURE OF A "
              "SEGMENT THAT DID NOT DELIVER ITS PRESCRIBED SPACING.")

    n_ax = sum(1 for j, f, o, p in pairs[:500]
               if abs(cx[o] - cx[p]) > abs(cy[o] - cy[p]))
    print("\n  of the 500 worst faces: %d axial, %d radial" % (n_ax,
                                                               500 - n_ax))
    print("  of the 500 worst faces: %d have both cells at r < 1e-3 m"
          % sum(1 for j, f, o, p in pairs[:500] if max(cy[o], cy[p]) < 1e-3))
    return 0


if __name__ == "__main__":
    sys.exit(main())
