#!/usr/bin/env python3
"""
Curriculum item D3 -- SEPARATION-ONSET MONITOR, frozen instrument.

Reads an OpenFOAM `U` internal field and its polyMesh IN PURE PYTHON (no
OpenFOAM, no container, no compute) and reports, for the A4 Ahmed case:

  n_rev_global   number of cells anywhere in the domain with U_x < 0
  m_def_global   min_over_all_cells(U_x) / U0            <-- PRIMARY, 2777-cell basis
  f_sep(B)       reverse-flow cell fraction inside the frozen box B
  n_cells(B)     cells whose approximate centre lies in B

Cell centres are the vertex average of the cell's own face vertices. This is an
APPROXIMATION (it is not the OpenFOAM cell centroid); it is used ONLY for box
membership, never for a graded scalar. The graded scalar `m_def_global` needs no
centres at all and is exact.

INSTRUMENT CONDITIONS (frozen; see PREREGISTRATION.md sec.6 Gs):
  (i)   n_cells(B) >= 20                     -- the box must contain a sample
  (ii)  the reader must be shown able to see a NON-ZERO on a case of this class
  (iii) n_rev_global >= 1 on the graded field -- separation must exist to monitor

If (i) or (iii) fail the monitor prints NOT AN INSTRUMENT and exits 3. Exit 3 is
NOT a failure of the run: it is the registered refusal, and the item still grades
its optimiser, constraint and gradient gates.

`--plant <fine_mesh_U>` runs condition (ii): the same reader on a field where a
non-zero IS present. If the plant is not seen, the reader refuses with exit 2
(CLAUDE.md rule 3 -- a zero from a reader not shown able to see a non-zero is
not evidence).
"""
import argparse
import os
import re
import sys

U0_DEFAULT = 40.0

# Frozen monitor box B and the wider supplementary box B'. Ahmed 25 body occupies
# x[0, 1.044] y[+-0.1945] z[0, 0.288]; the rear slant runs from the break at
# x = 0.8428, z = 0.288 to the rear edge at x = 1.044, z = 0.1942.
BOX_B = (0.84, 1.10, -0.20, 0.20, 0.10, 0.35)      # slant + immediate near wake
BOX_BP = (0.80, 1.30, -0.25, 0.25, 0.05, 0.40)     # wider near wake
MIN_CELLS_IN_BOX = 20


def _strip_header(txt):
    i = txt.find("FoamFile")
    if i >= 0:
        j = txt.find("}", i)
        txt = txt[j + 1:]
    txt = re.sub(r"/\*.*?\*/", " ", txt, flags=re.S)
    txt = re.sub(r"//[^\n]*", " ", txt)
    return txt


def read_points(path):
    txt = _strip_header(open(path).read())
    m = re.search(r"(\d+)\s*\(", txt)
    n = int(m.group(1))
    body = txt[m.end():]
    vals = re.findall(r"\(\s*([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s*\)", body)
    pts = [(float(a), float(b), float(c)) for a, b, c in vals[:n]]
    assert len(pts) == n, "points: read %d of %d" % (len(pts), n)
    return pts


def read_faces(path):
    txt = _strip_header(open(path).read())
    m = re.search(r"(\d+)\s*\(", txt)
    n = int(m.group(1))
    body = txt[m.end():]
    faces = []
    for mm in re.finditer(r"(\d+)\s*\(([^)]*)\)", body):
        faces.append([int(x) for x in mm.group(2).split()])
        if len(faces) == n:
            break
    assert len(faces) == n, "faces: read %d of %d" % (len(faces), n)
    return faces


def read_labels(path):
    txt = _strip_header(open(path).read())
    m = re.search(r"(\d+)\s*\(", txt)
    n = int(m.group(1))
    body = txt[m.end():]
    out = []
    for tok in re.findall(r"-?\d+", body):
        out.append(int(tok))
        if len(out) == n:
            break
    assert len(out) == n, "labels: read %d of %d" % (len(out), n)
    return out


def read_vector_internal(path):
    """Return the internalField as a list of 3-tuples, or raise."""
    txt = _strip_header(open(path).read())
    i = txt.find("internalField")
    if i < 0:
        raise ValueError("no internalField in %s" % path)
    body = txt[i:]
    m = re.search(r"nonuniform\s+List<vector>\s*(\d+)\s*\(", body)
    if not m:
        raise ValueError("internalField in %s is not a nonuniform vector list "
                         "(uniform field: nothing to monitor)" % path)
    n = int(m.group(1))
    vals = re.findall(r"\(\s*([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s*\)",
                      body[m.end() - 1:])
    v = [(float(a), float(b), float(c)) for a, b, c in vals[:n]]
    assert len(v) == n, "U: read %d of %d" % (len(v), n)
    return v


def approx_centres(meshdir, ncells):
    pts = read_points(os.path.join(meshdir, "points"))
    faces = read_faces(os.path.join(meshdir, "faces"))
    owner = read_labels(os.path.join(meshdir, "owner"))
    nb = os.path.join(meshdir, "neighbour")
    neigh = read_labels(nb) if os.path.exists(nb) else []
    acc = [[0.0, 0.0, 0.0, 0] for _ in range(ncells)]
    for fi, c in enumerate(owner):
        for p in faces[fi]:
            x, y, z = pts[p]
            a = acc[c]
            a[0] += x; a[1] += y; a[2] += z; a[3] += 1
    for fi, c in enumerate(neigh):
        for p in faces[fi]:
            x, y, z = pts[p]
            a = acc[c]
            a[0] += x; a[1] += y; a[2] += z; a[3] += 1
    out = []
    for a in acc:
        if a[3] == 0:
            raise ValueError("cell with no faces -- mesh read is wrong")
        out.append((a[0] / a[3], a[1] / a[3], a[2] / a[3]))
    return out


def in_box(c, box):
    x0, x1, y0, y1, z0, z1 = box
    return x0 <= c[0] <= x1 and y0 <= c[1] <= y1 and z0 <= c[2] <= z1


def measure(ufile, meshdir, u0):
    U = read_vector_internal(ufile)
    n = len(U)
    n_rev_global = sum(1 for u in U if u[0] < 0.0)
    minux = min(u[0] for u in U)
    res = {
        "u_file": ufile,
        "ncells": n,
        "n_rev_global": n_rev_global,
        "min_Ux": minux,
        "m_def_global": minux / u0,
    }
    if meshdir:
        C = approx_centres(meshdir, n)
        for tag, box in (("B", BOX_B), ("Bp", BOX_BP)):
            idx = [i for i, c in enumerate(C) if in_box(c, box)]
            rev = sum(1 for i in idx if U[i][0] < 0.0)
            res["n_cells_%s" % tag] = len(idx)
            res["n_rev_%s" % tag] = rev
            res["f_sep_%s" % tag] = (rev / len(idx)) if idx else None
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--u", required=True, help="OpenFOAM U field to read")
    ap.add_argument("--mesh", default=None, help="polyMesh directory for box membership")
    ap.add_argument("--u0", type=float, default=U0_DEFAULT)
    ap.add_argument("--plant", default=None,
                    help="a U field of this case class KNOWN to contain reverse flow; "
                         "condition (ii). Without it a zero reading is not evidence.")
    ap.add_argument("--plant-mesh", default=None)
    a = ap.parse_args()

    plant_ok = None
    if a.plant:
        p = measure(a.plant, a.plant_mesh, a.u0)
        plant_ok = p["n_rev_global"] >= 1
        print("PLANT  file=%s ncells=%d n_rev_global=%d min_Ux=%.4f"
              % (p["u_file"], p["ncells"], p["n_rev_global"], p["min_Ux"]))
        if not plant_ok:
            print("MONITOR REFUSES (exit 2): the planted non-zero was NOT seen. "
                  "A zero from this reader is not evidence (CLAUDE.md rule 3).")
            return 2
        print("PLANT SEEN: the reader resolves reverse flow on this case class.")

    r = measure(a.u, a.mesh, a.u0)
    print("FIELD  file=%s ncells=%d" % (r["u_file"], r["ncells"]))
    print("  n_rev_global = %d" % r["n_rev_global"])
    print("  min_Ux       = %.6f  m_def_global = min_Ux/U0 = %.6f"
          % (r["min_Ux"], r["m_def_global"]))
    for tag in ("B", "Bp"):
        k = "n_cells_%s" % tag
        if k in r:
            print("  box %-2s n_cells=%4d n_rev=%4d f_sep=%s"
                  % (tag, r[k], r["n_rev_%s" % tag],
                     ("%.6f" % r["f_sep_%s" % tag]) if r["f_sep_%s" % tag] is not None else "n/a"))

    if plant_ok is None:
        print("NO PLANT SUPPLIED: this reading is NOT evidence of absence "
              "(CLAUDE.md rule 3). Re-run with --plant.")
        return 2

    fails = []
    if "n_cells_B" in r and r["n_cells_B"] < MIN_CELLS_IN_BOX:
        fails.append("(i) n_cells(B)=%d < %d" % (r["n_cells_B"], MIN_CELLS_IN_BOX))
    if r["n_rev_global"] < 1:
        fails.append("(iii) n_rev_global=0 -- no separated flow exists on this mesh")
    if fails:
        print("VERDICT: NOT AN INSTRUMENT -- " + "; ".join(fails))
        print("  m_def_global = %.6f is still reported and IS graded "
              "(exact, whole-domain, no centre approximation)." % r["m_def_global"])
        return 3
    print("VERDICT: INSTRUMENT -- f_sep(B) = %.6f is graded." % r["f_sep_B"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
