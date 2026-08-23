#!/usr/bin/env python3
"""
Verify every T9a mesh FROM THE MESH, never from the builder.

Reads constant/polyMesh/points (and owner's nCells) for each case and checks
against T9a_registered.json: total extents, that a mesh face lies exactly on
each registered layer interface, per-layer cell counts and uniform spacing,
the fin's nx/ny, and that the mixed valueFraction written in 0/T equals
1/(1 + k/(h d)) for the wall distance d that the MESH actually has.  The
wall's 0/DT is checked cell by cell against cell-centre positions obtained
from postProcess writeCellCentres (the temporary centre fields are removed
from 0/ afterwards).  Zero solver compute.
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REG = json.load(open(os.path.join(HERE, "T9a_registered.json")))
sys.path.insert(0, HERE)
import analyse_t9a as A     # noqa: E402  (frozen helpers: read_points etc.)


def ncells_from_owner(case):
    txt = open(os.path.join(case, "constant", "polyMesh", "owner"),
               errors="replace").read(2000)
    m = re.search(r"nCells:\s*(\d+)", txt)
    return int(m.group(1))


def centres(case):
    r = A.foam(case, "postProcess -func writeCellCentres -time 0 "
                     "> log.writeCellCentres.t0 2>&1")
    if r.returncode != 0:
        sys.exit(f"writeCellCentres failed in {case}")
    Cx = A.read_internal(os.path.join(case, "0", "Cx"))
    Cy = A.read_internal(os.path.join(case, "0", "Cy"))
    for f in ("C", "Cx", "Cy", "Cz"):
        p = os.path.join(case, "0", f)
        if os.path.exists(p):
            os.remove(p)
    return Cx, Cy


def check_wall(name, c):
    case = os.path.join(HERE, name)
    pts = A.read_points(case)
    xs = sorted(set(round(p[0], 15) for p in pts))
    ys = sorted(set(round(p[1], 15) for p in pts))
    zs = sorted(set(round(p[2], 15) for p in pts))
    ok = True
    thick = xs[-1] - xs[0]
    bounds = [xs[0]] + REG["wall"]["interfaces_x"] + [xs[-1]]
    print(f"\n{name}: {len(pts)} points, nCells(owner) = {ncells_from_owner(case)}"
          f", distinct x planes = {len(xs)}")
    print(f"  x extent {xs[0]:.10g} .. {xs[-1]:.10g}  thickness {thick:.10g}"
          f"  (registered {REG['wall']['total_thickness']})")
    ok &= abs(thick - REG["wall"]["total_thickness"]) < 1e-12
    for xi in REG["wall"]["interfaces_x"]:
        hit = min(abs(v - xi) for v in xs)
        print(f"  interface face at x = {xi}: nearest mesh plane off by {hit:.2e}")
        ok &= hit < 1e-12
    per_layer = []
    for j in range(3):
        lo, hi = bounds[j], bounds[j + 1]
        planes = [v for v in xs if lo - 1e-12 <= v <= hi + 1e-12]
        n = len(planes) - 1
        dx = [b - a for a, b in zip(planes, planes[1:])]
        spread = (max(dx) - min(dx)) / max(dx)
        per_layer.append(n)
        print(f"  layer {j+1}: {n} cells, dx = {dx[0]:.6e}, "
              f"uniformity spread {spread:.1e}  (registered {c['cells_per_layer'][j]})")
        ok &= n == c["cells_per_layer"][j] and spread < 1e-9
    print(f"  y,z extents: {ys[-1]-ys[0]:.6g} x {zs[-1]-zs[0]:.6g}, "
          f"{len(ys)-1} x {len(zs)-1} cells (empty directions)")
    ok &= len(ys) == 2 and len(zs) == 2
    ok &= sum(per_layer) == ncells_from_owner(case)

    # DT layer map against cell centres
    Cx, _ = centres(case)
    DT = A.read_internal(os.path.join(case, "0", "DT"), len(Cx))
    ks = [ly["k"] for ly in REG["wall"]["layers"]]
    bad = [i for i in range(len(Cx)) if DT[i] != ks[A.wall_layer_of(Cx[i])]]
    print(f"  0/DT against cell centres: {len(Cx) - len(bad)}/{len(Cx)} cells "
          f"carry the registered k of their layer"
          + ("" if not bad else f"  MISMATCH at cells {bad[:5]}"))
    ok &= not bad
    # boundary temperatures as written
    blocks = A.boundary_blocks(os.path.join(case, "0", "T"))
    th = A.patch_uniform(blocks["hot"], "value", case, "hot")
    tc = A.patch_uniform(blocks["cold"], "value", case, "cold")
    print(f"  0/T: hot {th} K, cold {tc} K")
    if c["kind"] == "wall":
        ok &= th == REG["wall"]["T_hot"] and tc == REG["wall"]["T_cold"]
    else:
        ok &= th == tc == REG["wall"]["T_hot"]
    # refinement spacing
    print(f"  {'OK' if ok else 'FAIL'}")
    return ok, per_layer


def check_fin(name, c):
    case = os.path.join(HERE, name)
    pts = A.read_points(case)
    xs = sorted(set(round(p[0], 15) for p in pts))
    ys = sorted(set(round(p[1], 15) for p in pts))
    zs = sorted(set(round(p[2], 15) for p in pts))
    L, t, W = xs[-1] - xs[0], ys[-1] - ys[0], zs[-1] - zs[0]
    nx, ny = len(xs) - 1, len(ys) - 1
    dx = [b - a for a, b in zip(xs, xs[1:])]
    dy = [b - a for a, b in zip(ys, ys[1:])]
    ok = True
    print(f"\n{name}: {len(pts)} points, nCells(owner) = {ncells_from_owner(case)}")
    print(f"  L = {L:.10g} (reg {REG['fin']['L']}), t = {t:.10g} "
          f"(reg {REG['fin']['t']}), depth W = {W:.6g}, {len(zs)-1} cell in z")
    ok &= abs(L - REG["fin"]["L"]) < 1e-12 and abs(t - REG["fin"]["t"]) < 1e-12
    ok &= len(zs) == 2
    print(f"  nx = {nx} (reg {c['nx']}), ny = {ny} (reg {c['ny']}), "
          f"dx = {dx[0]:.6e} (spread {(max(dx)-min(dx))/max(dx):.1e}), "
          f"dy = {dy[0]:.6e} (spread {(max(dy)-min(dy))/max(dy):.1e})")
    ok &= nx == c["nx"] and ny == c["ny"]
    ok &= (max(dx) - min(dx)) / max(dx) < 1e-9
    ok &= (max(dy) - min(dy)) / max(dy) < 1e-9
    ok &= nx * ny == ncells_from_owner(case)
    # Robin valueFraction against the MESH's wall distance
    Cx, Cy = centres(case)
    ycs = sorted(set(round(v, 15) for v in Cy))
    d_bot = ycs[0] - ys[0]
    d_top = ys[-1] - ycs[-1]
    k, h = REG["fin"]["k"], REG["fin"]["h"]
    blocks = A.boundary_blocks(os.path.join(case, "0", "T"))
    for p, d in (("top", d_top), ("bottom", d_bot)):
        f_w = A.patch_uniform(blocks[p], "valueFraction", case, p)
        f_m = 1.0 / (1.0 + k / (h * d))
        rel = abs(f_w - f_m) / f_m
        print(f"  {p:6s}: mesh d = {d:.10e}, valueFraction written {f_w:.12e}, "
              f"from mesh {f_m:.12e}, rel diff {rel:.1e}")
        ok &= rel < 1e-9
        ok &= A.patch_uniform(blocks[p], "refValue", case, p) == REG["fin"]["T_inf"]
        ok &= A.patch_uniform(blocks[p], "refGradient", case, p) == 0.0
    tb = A.patch_uniform(blocks["base"], "value", case, "base")
    ok &= tb == REG["fin"]["T_base"]
    print(f"  base T = {tb} K, tip zeroGradient: "
          f"{'yes' if 'zeroGradient' in blocks['tip'] else 'NO'}")
    ok &= "zeroGradient" in blocks["tip"]
    print(f"  {'OK' if ok else 'FAIL'}")
    return ok, (nx, ny)


def main():
    allok = True
    wall_counts, fin_counts = {}, {}
    for name, c in REG["cases"].items():
        if c["kind"].startswith("wall"):
            ok, n = check_wall(name, c)
            wall_counts[name] = n
        else:
            ok, n = check_fin(name, c)
            fin_counts[name] = n
        allok &= ok
    print("\nrefinement ratios read from the meshes (nominal 1.6):")
    for a, b in (("W_c", "W_m"), ("W_m", "W_f")):
        print(f"  {a}->{b}: " + ", ".join(
            f"{y/x:.3f}" for x, y in zip(wall_counts[a], wall_counts[b])))
    for a, b in (("F_c", "F_m"), ("F_m", "F_f")):
        print(f"  {a}->{b}: " + ", ".join(
            f"{y/x:.3f}" for x, y in zip(fin_counts[a], fin_counts[b])))
    print("\nALL MESHES VERIFIED" if allok else "\nMESH VERIFICATION FAILED")
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
