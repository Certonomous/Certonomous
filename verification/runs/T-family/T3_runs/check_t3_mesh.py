#!/usr/bin/env python3
"""
Verify every T3 mesh against the design it claims, BEFORE any solver runs,
by READING constant/polyMesh/points.  Nothing the builder printed is trusted
(L-142: a build chain cannot check itself; T1b attempt 1 spent 57 core-hours
on a mesh whose every link quoted the same wrong number back to the others).

Per case, straight from the points file (z = 0 plane):
  A. the y-cell touching y = 0 on the heated wall equals CASE.txt
     first_cell_wall to 0.2 %
  B. it is the SMALLEST y-cell in [0, H], and the cell touching y = H from
     below equals it
  C. the cell touching y = 5H equals first_cell_wall and is the smallest in
     [H, 5H]
  D. the y-cells sum to H (lower block) and to 4H (upper blocks)
  E. the x-cell touching x = 0 on BOTH sides equals first_cell_x_step to 0.2 %
     and is the smallest x-cell on its side
  F. within each graded half (or single-sided block) the cell-to-cell ratio
     is geometric to 1e-6 relative
  G. (conformity, beyond the contract's list) B1 and B3 share the identical
     y distribution, B2 and B3 the identical x distribution, and the counts
     match CASE.txt.

Usage:  python3 check_t3_mesh.py [--root DIR] [case ...]
Runs blockMesh (log.blockMesh) and checkMesh (log.checkMesh) for any case
lacking constant/polyMesh/points, then checks.  Prints a table; returns 1 if
any assertion fails or any blockMesh fails.  checkMesh's own verdict (aspect
ratio, non-orthogonality, "Failed N mesh checks" / "Mesh OK") is REPORTED,
not asserted: aspect-ratio complaints are expected on wall-resolved meshes.
"""
import argparse
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = "/usr/lib/openfoam/openfoam2606/etc/bashrc"
TOL = 2.0e-3          # A, C, D, E
GEOM_TOL = 1.0e-6     # F
EQ_TOL = 1.0e-6       # "equals" between the two wall cells of a half pair
CASES = ["R_c", "R_m", "R_f", "P_m", "C_lam_m", "W_m", "D_m", "O_m"]


def case_field(d, key):
    for line in open(os.path.join(d, "CASE.txt")):
        t = line.split()
        if t and t[0] == key:
            return t[1]
    return None


def read_points(d):
    """All z = 0 points as (x, y) floats, from constant/polyMesh/points."""
    pts = []
    rx = re.compile(r"\(([-\d.eE+]+) ([-\d.eE+]+) ([-\d.eE+]+)\)")
    for line in open(os.path.join(d, "constant", "polyMesh", "points")):
        m = rx.fullmatch(line.strip())
        if m:
            x, y, z = (float(v) for v in m.groups())
            if abs(z) < 1e-12:
                pts.append((x, y))
    return pts


def line_coords(pts, fixed_idx, fixed_val, lo, hi, tol=1e-9):
    """Sorted unique coordinates of the OTHER axis along the line
    coord[fixed_idx] == fixed_val, restricted to [lo, hi]."""
    other = 1 - fixed_idx
    vals = sorted({round(p[other], 12) for p in pts
                   if abs(p[fixed_idx] - fixed_val) < tol
                   and lo - tol <= p[other] <= hi + tol})
    return vals


def cells(coords):
    return [coords[i + 1] - coords[i] for i in range(len(coords) - 1)]


def geometric_dev(h):
    """Max relative deviation of consecutive cell ratios from their mean."""
    if len(h) < 3:
        return 0.0, 1.0
    r = [h[i + 1] / h[i] for i in range(len(h) - 1)]
    mean = sum(r) / len(r)
    return max(abs(x - mean) for x in r) / mean, mean


def ncells_from_owner(d):
    for line in open(os.path.join(d, "constant", "polyMesh", "owner")):
        m = re.search(r"nCells:\s*(\d+)", line)
        if m:
            return int(m.group(1))
        if line.strip().startswith("(") or line.strip().isdigit():
            break
    return None


def parse_checkmesh(d):
    p = os.path.join(d, "log.checkMesh")
    out = dict(verdict="no log.checkMesh", aspect=None, nonorth=None)
    if not os.path.isfile(p):
        return out
    txt = open(p, errors="replace").read()
    m = re.search(r"^\s*(Failed \d+ mesh checks?\.|Mesh OK\.)", txt, re.M)
    if m:
        out["verdict"] = m.group(1)
    m = re.search(r"Max aspect ratio = ([0-9.eE+-]+)", txt)
    if m:
        out["aspect"] = float(m.group(1))
    m = re.search(r"non-orthogonality Max: ([0-9.eE+-]+)", txt)
    if m:
        out["nonorth"] = float(m.group(1))
    return out


def check(d):
    H = float(case_field(d, "H"))
    fcw = float(case_field(d, "first_cell_wall"))
    fcx = float(case_field(d, "first_cell_x_step"))
    L_up = float(case_field(d, "L_up_H")) * H
    L_dn = float(case_field(d, "L_down_H")) * H
    n = {k: int(case_field(d, k)) for k in ("nx_up", "nx_down", "ny_low", "ny_up")}
    pts = read_points(d)
    bad = []

    # y distributions along x = 0 (lower: B2 face on the step wall; upper:
    # the shared B1/B3 interface), plus the inlet (B1) and outlet (B3) lines
    y_low = cells(line_coords(pts, 0, 0.0, 0.0, H))
    y_up_x0 = cells(line_coords(pts, 0, 0.0, H, 5.0 * H))
    y_up_in = cells(line_coords(pts, 0, -L_up, H, 5.0 * H))
    y_up_out = cells(line_coords(pts, 0, L_dn, H, 5.0 * H))
    # x distributions: B1 along the top wall (x < 0), B2 along the heated wall,
    # B3 along the top wall (x > 0)
    x_up = cells(line_coords(pts, 1, 5.0 * H, -L_up, 0.0))
    x_dn_heated = cells(line_coords(pts, 1, 0.0, 0.0, L_dn))
    x_dn_top = cells(line_coords(pts, 1, 5.0 * H, 0.0, L_dn))

    # G: counts and conformity
    if len(y_low) != n["ny_low"]:
        bad.append(f"G: {len(y_low)} y-cells in [0,H], CASE.txt ny_low {n['ny_low']}")
    if len(y_up_x0) != n["ny_up"]:
        bad.append(f"G: {len(y_up_x0)} y-cells in [H,5H], CASE.txt ny_up {n['ny_up']}")
    if len(x_up) != n["nx_up"]:
        bad.append(f"G: {len(x_up)} x-cells upstream, CASE.txt nx_up {n['nx_up']}")
    if len(x_dn_heated) != n["nx_down"]:
        bad.append(f"G: {len(x_dn_heated)} x-cells downstream, CASE.txt nx_down {n['nx_down']}")
    for lab, a, b in (("B1 inlet vs x=0", y_up_in, y_up_x0),
                      ("B3 outlet vs x=0", y_up_out, y_up_x0)):
        if len(a) != len(b) or any(abs(p - q) > EQ_TOL * q for p, q in zip(a, b)):
            bad.append(f"G: y distribution differs ({lab}); B1 and B3 not identical")
    if (len(x_dn_heated) != len(x_dn_top)
            or any(abs(p - q) > EQ_TOL * q for p, q in zip(x_dn_heated, x_dn_top))):
        bad.append("G: x distribution differs between B2 (heated wall) and B3 (top wall)")

    if not (y_low and y_up_x0 and x_up and x_dn_heated):
        return bad + ["could not extract distributions from points"], {}

    # A
    hw = y_low[0]
    eA = abs(hw - fcw) / fcw
    if eA > TOL:
        bad.append(f"A: heated-wall cell {hw:.6e} vs design {fcw:.6e} ({100*eA:.3f} % off)")
    # B
    # "smallest" and "equals" are judged to EQ_TOL relative: the two wall cells
    # of a symmetric half pair differ by an ulp, and a real inversion is a
    # factor, not a rounding
    if hw > min(y_low) * (1.0 + EQ_TOL):
        bad.append(f"B: heated-wall cell {hw:.4e} is NOT the smallest in [0,H] "
                   f"(min {min(y_low):.4e} at cell {y_low.index(min(y_low))})")
    if y_low[-1] > hw * (1.0 + EQ_TOL):
        bad.append(f"B: INVERTED lower block: cell at y=H- {y_low[-1]:.4e} > wall cell {hw:.4e}")
    if abs(y_low[-1] - hw) > EQ_TOL * hw:
        bad.append(f"B: cell touching y=H from below {y_low[-1]:.6e} != wall cell {hw:.6e}")
    # C
    ht = y_up_x0[-1]
    eC = abs(ht - fcw) / fcw
    if eC > TOL:
        bad.append(f"C: top-wall cell {ht:.6e} vs design {fcw:.6e} ({100*eC:.3f} % off)")
    if ht > min(y_up_x0) * (1.0 + EQ_TOL):
        bad.append(f"C: top-wall cell {ht:.4e} is NOT the smallest in [H,5H] (min {min(y_up_x0):.4e})")
    if abs(y_up_x0[0] - ht) > EQ_TOL * ht:
        bad.append(f"C: cell touching y=H from above {y_up_x0[0]:.6e} != top-wall cell {ht:.6e}")
    # D
    sl, su = sum(y_low), sum(y_up_x0)
    if abs(sl - H) / H > TOL:
        bad.append(f"D: lower y-cells sum to {sl:.8f}, H = {H}")
    if abs(su - 4.0 * H) / (4.0 * H) > TOL:
        bad.append(f"D: upper y-cells sum to {su:.8f}, 4H = {4*H}")
    # E
    xs_up, xs_dn = x_up[-1], x_dn_heated[0]
    for lab, v, arr, idx in (("upstream", xs_up, x_up, len(x_up) - 1),
                             ("downstream", xs_dn, x_dn_heated, 0)):
        e = abs(v - fcx) / fcx
        if e > TOL:
            bad.append(f"E: {lab} step x-cell {v:.6e} vs design {fcx:.6e} ({100*e:.3f} % off)")
        if v > min(arr) * (1.0 + EQ_TOL):
            bad.append(f"E: {lab} step x-cell {v:.4e} is NOT the smallest on its side "
                       f"(min {min(arr):.4e}); INVERTED x grading")
    # F: geometric within each graded half / single-sided block
    halves = {
        "y_low first half": y_low[:len(y_low) // 2],
        "y_low second half": y_low[len(y_low) // 2:],
        "y_up first half": y_up_x0[:len(y_up_x0) // 2],
        "y_up second half": y_up_x0[len(y_up_x0) // 2:],
        "x_up": x_up,
        "x_down": x_dn_heated,
    }
    ratios = {}
    for lab, h in halves.items():
        dev, mean = geometric_dev(h)
        ratios[lab] = mean
        if dev > GEOM_TOL:
            bad.append(f"F: {lab} not geometric (max deviation {dev:.2e} relative)")

    # location of the smallest y-cell (0..5H) for the table
    ys_all = line_coords(pts, 0, 0.0, 0.0, 5.0 * H)
    ya = cells(ys_all)
    imin = ya.index(min(ya))
    y_min_loc = 0.5 * (ys_all[imin] + ys_all[imin + 1])

    info = dict(hw=hw, fcw=fcw, ht=ht, xs_up=xs_up, xs_dn=xs_dn, fcx=fcx,
                ymin=min(ya), ymin_loc=y_min_loc,
                r_ylow=ratios["y_low first half"], r_yup=ratios["y_up first half"],
                r_xup=1.0 / ratios["x_up"], r_xdn=ratios["x_down"],
                max_y_low=max(y_low), max_y_up=max(y_up_x0),
                max_x_up=max(x_up), max_x_dn=max(x_dn_heated))
    return bad, info


def mesh_if_needed(d):
    """blockMesh then checkMesh when points are absent. Returns
    (blockMesh_rc or None, checkMesh_rc or None)."""
    if os.path.isfile(os.path.join(d, "constant", "polyMesh", "points")):
        return None, None
    r = subprocess.run(["bash", "-c",
                        f"source {ENV} >/dev/null 2>&1 && cd '{d}' && "
                        f"blockMesh > log.blockMesh 2>&1"])
    if r.returncode != 0:
        return r.returncode, None
    c = subprocess.run(["bash", "-c",
                        f"source {ENV} >/dev/null 2>&1 && cd '{d}' && "
                        f"checkMesh > log.checkMesh 2>&1"])
    return r.returncode, c.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=HERE)
    ap.add_argument("cases", nargs="*", default=CASES)
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    fails = {}
    print(f"{'case':8s} {'heatedWall cell':>14s} {'design':>11s} {'topWall cell':>12s} "
          f"{'step x up':>11s} {'step x dn':>11s} {'design':>11s} "
          f"{'min y-cell @y':>13s} {'nCells':>7s} {'cm_rc':>5s} {'aspect':>8s} "
          f"{'nonOrth':>7s}  checkMesh verdict")
    for c in a.cases:
        d = os.path.join(root, c)
        if not os.path.isdir(d):
            print(f"{c:8s}  NO CASE DIRECTORY (not built)")
            fails[c] = ["no case directory"]
            continue
        bm_rc, cm_rc = mesh_if_needed(d)
        if bm_rc not in (None, 0):
            print(f"{c:8s}  blockMesh FAILED rc={bm_rc} (see log.blockMesh)")
            fails[c] = ["blockMesh failed"]
            continue
        bad, m = check(d)
        cm = parse_checkmesh(d)
        nc = ncells_from_owner(d)
        rc_s = "-" if cm_rc is None else str(cm_rc)
        asp = "-" if cm["aspect"] is None else f"{cm['aspect']:.1f}"
        non = "-" if cm["nonorth"] is None else f"{cm['nonorth']:.2f}"
        if m:
            print(f"{c:8s} {m['hw']:14.6e} {m['fcw']:11.4e} {m['ht']:12.6e} "
                  f"{m['xs_up']:11.4e} {m['xs_dn']:11.4e} {m['fcx']:11.4e} "
                  f"{m['ymin_loc']:13.6e} {nc if nc is not None else -1:7d} {rc_s:>5s} "
                  f"{asp:>8s} {non:>7s}  {cm['verdict']}")
            print(f"{'':8s}   cell-to-cell: y_low {m['r_ylow']:.6f}  y_up {m['r_yup']:.6f}  "
                  f"x_up {m['r_xup']:.6f}  x_down {m['r_xdn']:.6f}   largest cells: "
                  f"y_low {m['max_y_low']:.3e}  y_up {m['max_y_up']:.3e}  "
                  f"x_up {m['max_x_up']:.3e}  x_down {m['max_x_dn']:.3e}")
        else:
            print(f"{c:8s}  distributions not extracted")
        for b in bad:
            print(f"{'':8s}   <-- {b}")
        if bad:
            fails[c] = bad
    print()
    if fails:
        print(f"MESH CHECK FAILED for {len(fails)} of {len(a.cases)} cases: "
              f"{', '.join(sorted(fails))}")
        return 1
    print(f"MESH CHECK PASSED for all {len(a.cases)} cases: wall cells and step "
          f"x-cells are the design values and the smallest in their direction; "
          f"halves geometric; blocks conformal")
    return 0


if __name__ == "__main__":
    sys.exit(main())
