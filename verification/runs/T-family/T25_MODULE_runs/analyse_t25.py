#!/usr/bin/env python3
# =========================================================================
# T25 -- READER FOR THE 8-CELL MODULE FEASIBILITY RUN
#
# *** THIS IS A READER FOR AN UNGATED FEASIBILITY RUN. ***
# It declares NO verdict, computes NO Roache triple and NO GCI, and applies
# NO gate.  The rung carries no pre-registration, no threshold and no band,
# and CASE.txt says on its face that nothing it produces may be graded.
# This script exists to READ what was solved, so that a sheet drawn from it
# is drawn from values somebody actually read off disk.
#
# EVERYTHING IS COMPUTED FROM THE MESH AND THE FIELDS, NOT FROM THE
# BUILDER'S CONSTANTS.  Cell volumes and boundary-face areas come out of
# constant/module/polyMesh; temperatures come out of the time directories.
# The builder's numbers are then used only as ASSERTIONS against what the
# mesh actually says, so a disagreement is a refusal rather than a silent
# preference for the convenient value.
#
# PLANTED-ZERO CONTROL (CLAUDE.md rule 3): --selftest perturbs a known
# temperature by a known amount, re-reads it THROUGH THE SAME PARSER, and
# refuses unless the reader sees the perturbation at the expected size.  A
# reader never shown able to see a non-zero cannot be trusted with a zero.
# =========================================================================
import argparse
import math
import os
import re
import sys

RHO, CP, KAPPA = 2500.0, 1000.0, 3.0
T_REF = 293.0            # coolant / initial temperature, K
H_CONV = 53.9            # W/m2K on the channel faces
N_CELLS = 8
LX, LY, LZ, GAP = 0.100, 0.030, 1.000, 0.003
PITCH = LY + GAP
P_TAKEOFF, P_CRUISE = 15.0, 4.0     # W per cell
T_PULSE, T_END = 60.0, 900.0
Q_IN_TOTAL = N_CELLS * (P_TAKEOFF * T_PULSE + P_CRUISE * (T_END - T_PULSE))


# ----------------------------------------------------------------- parsing
def _strip(text):
    """Remove OpenFOAM comments so keyword scans cannot match inside them."""
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return re.sub(r"//[^\n]*", " ", text)


def read_list(text, start):
    """Read a '(' ... ')' list of whitespace-separated tokens from start."""
    i = text.index("(", start)
    depth, j = 0, i
    while True:
        if text[j] == "(":
            depth += 1
        elif text[j] == ")":
            depth -= 1
            if depth == 0:
                break
        j += 1
    return text[i + 1:j], j


def scalar_field(path, key="internalField"):
    """internalField of a volScalarField: uniform or nonuniform."""
    t = _strip(open(path).read())
    m = re.search(key + r"\s+uniform\s+([-\d.eE+]+)\s*;", t)
    if m:
        return None, float(m.group(1))
    k = t.index(key)
    body, _ = read_list(t, k)
    return [float(v) for v in body.split()], None


def patch_entry_values(path, patch, key):
    """The `key` list inside boundaryField/<patch> of a field file."""
    t = _strip(open(path).read())
    b = t.index("boundaryField")
    p = t.index(patch, b)
    # bound the patch block by brace matching
    i = t.index("{", p)
    depth, j = 0, i
    while True:
        if t[j] == "{":
            depth += 1
        elif t[j] == "}":
            depth -= 1
            if depth == 0:
                break
        j += 1
    blk = t[i:j]
    m = re.search(r"\b" + key + r"\s+uniform\s+([-\d.eE+]+)\s*;", blk)
    if m:
        return None, float(m.group(1))
    m = re.search(r"\b" + key + r"\s+nonuniform", blk)
    if not m:
        raise KeyError(f"{key} not found on patch {patch} in {path}")
    body, _ = read_list(blk, m.start())
    return [float(v) for v in body.split()], None


def _mesh_body(pm, name):
    """Body of a polyMesh list file.

    These carry no `List<...>` prefix: after the FoamFile block comes a bare
    count and then the parenthesised list.  The FoamFile block is skipped by
    brace matching rather than by line number, and the COUNT IS CHECKED
    against the number of entries actually parsed by each caller.
    """
    t = _strip(open(os.path.join(pm, name)).read())
    k = t.index("FoamFile")
    i = t.index("{", k)
    depth, j = 0, i
    while True:
        if t[j] == "{":
            depth += 1
        elif t[j] == "}":
            depth -= 1
            if depth == 0:
                break
        j += 1
    rest = t[j + 1:]
    m = re.search(r"(\d+)\s*\(", rest)
    if not m:
        return 0, ""
    body, _ = read_list(rest, m.start(1))
    return int(m.group(1)), body


def read_points(pm):
    n, body = _mesh_body(pm, "points")
    pts = [(float(a), float(b), float(c)) for a, b, c in
           re.findall(r"\(\s*([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s*\)",
                      body)]
    if len(pts) != n:
        sys.exit(f"REFUSE: points declares {n} entries, parsed {len(pts)}")
    return pts


def read_faces(pm):
    n, body = _mesh_body(pm, "faces")
    faces = [[int(v) for v in g.split()]
             for g in re.findall(r"\d+\s*\(([^)]*)\)", body)]
    if len(faces) != n:
        sys.exit(f"REFUSE: faces declares {n} entries, parsed {len(faces)}")
    return faces


def read_labels(pm, name):
    n, body = _mesh_body(pm, name)
    vals = [int(v) for v in body.split()]
    if len(vals) != n:
        sys.exit(f"REFUSE: {name} declares {n} entries, parsed {len(vals)}")
    return vals


def read_boundary(pm):
    t = _strip(open(os.path.join(pm, "boundary")).read())
    out = {}
    for m in re.finditer(r"(\w+)\s*\{([^}]*)\}", t):
        blk = m.group(2)
        nf = re.search(r"nFaces\s+(\d+)\s*;", blk)
        sf = re.search(r"startFace\s+(\d+)\s*;", blk)
        if nf and sf:
            out[m.group(1)] = (int(nf.group(1)), int(sf.group(1)))
    return out


# ------------------------------------------------------------------ geometry
def face_area(face, pts):
    """Magnitude of the area vector of a planar polygon."""
    n = len(face)
    c = [sum(pts[i][d] for i in face) / n for d in range(3)]
    ax = ay = az = 0.0
    for a in range(n):
        p, q = pts[face[a]], pts[face[(a + 1) % n]]
        u = (p[0] - c[0], p[1] - c[1], p[2] - c[2])
        v = (q[0] - c[0], q[1] - c[1], q[2] - c[2])
        ax += u[1] * v[2] - u[2] * v[1]
        ay += u[2] * v[0] - u[0] * v[2]
        az += u[0] * v[1] - u[1] * v[0]
    return 0.5 * math.sqrt(ax * ax + ay * ay + az * az)


def mesh_geometry(case, region="module"):
    pm = os.path.join(case, "constant", region, "polyMesh")
    pts = read_points(pm)
    faces = read_faces(pm)
    owner = read_labels(pm, "owner")
    neigh = read_labels(pm, "neighbour")
    bnd = read_boundary(pm)

    ncells = max(max(owner), max(neigh) if neigh else -1) + 1
    cpts = [set() for _ in range(ncells)]
    for fi, f in enumerate(faces):
        cpts[owner[fi]].update(f)
        if fi < len(neigh):
            cpts[neigh[fi]].update(f)

    vol, cy = [], []
    for s in cpts:
        xs = [pts[i][0] for i in s]; ys = [pts[i][1] for i in s]
        zs = [pts[i][2] for i in s]
        vol.append((max(xs) - min(xs)) * (max(ys) - min(ys)) * (max(zs) - min(zs)))
        cy.append(0.5 * (max(ys) + min(ys)))

    nf, sf = bnd["channelFaces"]
    areas = [face_area(faces[sf + i], pts) for i in range(nf)]
    return vol, cy, areas, ncells, bnd


def cell_index(y):
    """Which of the 8 module cells a y-coordinate belongs to."""
    i = int(y // PITCH)
    return min(max(i, 0), N_CELLS - 1)


# -------------------------------------------------------------------- main
def times_of(case):
    ts = []
    for d in os.listdir(case):
        if re.fullmatch(r"[0-9]+(\.[0-9]+)?", d) and os.path.isdir(
                os.path.join(case, d)):
            ts.append(float(d))
    return sorted(ts)


def fmt_t(t):
    return str(int(t)) if float(t).is_integer() else repr(t)


def analyse(case, region="module", quiet=False):
    vol, cy, areas, ncells, bnd = mesh_geometry(case, region)

    problems = []
    if ncells != 960:
        problems.append(f"expected 960 cells, mesh has {ncells}")
    tv = sum(vol)
    if abs(tv - N_CELLS * LX * LY * LZ) > 1e-9:
        problems.append(f"total volume {tv} != {N_CELLS*LX*LY*LZ}")
    ta = sum(areas)
    exp_a = (2 * N_CELLS - 2) * LX * LZ
    if abs(ta - exp_a) > 1e-9:
        problems.append(f"channel area {ta} != expected {exp_a}")
    groups = [[] for _ in range(N_CELLS)]
    for c, y in enumerate(cy):
        groups[cell_index(y)].append(c)
    for i, g in enumerate(groups):
        if len(g) != 120:
            problems.append(f"module cell {i+1} has {len(g)} mesh cells, not 120")
    if problems:
        sys.exit("REFUSE: mesh does not match the registered geometry: "
                 + "; ".join(problems))

    ts = times_of(case)
    rows = []
    for t in ts:
        td = os.path.join(case, fmt_t(t), region)
        Tint, uni = scalar_field(os.path.join(td, "T"))
        if Tint is None:
            Tint = [uni] * ncells
        percell = [sum(Tint[c] * vol[c] for c in g) / sum(vol[c] for c in g)
                   for g in groups]
        estored = sum(RHO * CP * vol[c] * (Tint[c] - T_REF)
                      for c in range(ncells))
        Tw, uw = patch_entry_values(os.path.join(td, "T"), "channelFaces", "value")
        if Tw is None:
            Tw = [uw] * len(areas)
        qout = sum(H_CONV * areas[f] * (Tw[f] - T_REF) for f in range(len(areas)))
        rows.append({"t": t, "percell": percell, "E": estored, "Qout": qout,
                     "Tmin": min(Tint), "Tmax": max(Tint)})

    # trapezoidal integral of the channel-face heat removal
    qint = 0.0
    for a, b in zip(rows[:-1], rows[1:]):
        qint += 0.5 * (a["Qout"] + b["Qout"]) * (b["t"] - a["t"])

    last = rows[-1]
    accounted = last["E"] + qint
    closure_pct = 100.0 * accounted / Q_IN_TOTAL
    gap_pct = 100.0 * (Q_IN_TOTAL - accounted) / Q_IN_TOTAL

    if not quiet:
        print(f"case            {case}")
        print(f"mesh            {ncells} cells, total volume {tv:.6f} m3, "
              f"channel area {ta:.4f} m2, {len(areas)} channel faces")
        print(f"times           {len(ts)} directories, {ts[0]} .. {ts[-1]} s")
        print()
        print("PER-CELL VOLUME-AVERAGE TEMPERATURE, K")
        print("  t, s   " + "".join(f"  cell{i+1:>2}" for i in range(N_CELLS)))
        for t_want in (0.0, 30.0, 60.0, 120.0, 300.0, 600.0, 900.0):
            r = min(rows, key=lambda r: abs(r["t"] - t_want))
            print(f"  {r['t']:6.1f} " +
                  "".join(f" {v:8.4f}" for v in r["percell"]))
        print()
        print("RISE ABOVE COOLANT AT 900 s, K")
        for i, v in enumerate(last["percell"]):
            print(f"  cell {i+1}   {v - T_REF:.6f}")
        print(f"  module point min/max at 900 s: "
              f"{last['Tmin']-T_REF:.6f} / {last['Tmax']-T_REF:.6f} K")
        print()
        print("PEAK AND TIME TO PEAK, per cell (volume-average)")
        for i in range(N_CELLS):
            best = max(rows, key=lambda r: r["percell"][i])
            print(f"  cell {i+1}   peak {best['percell'][i]:.6f} K "
                  f"({best['percell'][i]-273.15:.4f} degC) at t = {best['t']:.0f} s")
        print()
        print("SPREAD (hottest minus coldest cell, volume-average), K")
        for t_want in (0.0, 30.0, 60.0, 120.0, 300.0, 600.0, 900.0):
            r = min(rows, key=lambda r: abs(r["t"] - t_want))
            print(f"  t = {r['t']:6.1f}   {max(r['percell'])-min(r['percell']):.6f}")
        sm = max(rows, key=lambda r: max(r["percell"]) - min(r["percell"]))
        print(f"  MAXIMUM SPREAD {max(sm['percell'])-min(sm['percell']):.6f} K "
              f"at t = {sm['t']:.0f} s")
        print()
        print("ENERGY CLOSURE  -- all three terms measured independently")
        print(f"  heat in, from the duty cycle       {Q_IN_TOTAL:12.4f} J")
        print(f"  stored in the cells at 900 s       {last['E']:12.4f} J"
              "   (rho*cp*V*(T-293) summed over 960 mesh cells)")
        print(f"  removed through the channel faces  {qint:12.4f} J"
              "   (h*A*(Tface-293) integrated over 181 samples)")
        print(f"  accounted for                      {accounted:12.4f} J")
        print(f"  CLOSURE                            {closure_pct:12.4f} %")
        print(f"  unaccounted                        {gap_pct:12.4f} %")
        print()
        print(f"  final removal rate {last['Qout']:.4f} W against a cruise "
              f"input of {N_CELLS*P_CRUISE:.1f} W -- "
              f"{100.0*last['Qout']/(N_CELLS*P_CRUISE):.2f} % of it")
    return rows, closure_pct, qint, last


def selftest(case, region="module"):
    """PLANTED CONTROL: the reader must be able to SEE a perturbation."""
    import shutil
    import tempfile
    print("PLANTED-ZERO CONTROL (rule 3): perturb a known value, re-read it "
          "through the same parser, refuse unless the reader sees it.")
    tmp = tempfile.mkdtemp(prefix="t25_plant_")
    dst = os.path.join(tmp, "case")
    shutil.copytree(case, dst, ignore=shutil.ignore_patterns("postProcessing"))
    _, base_close, _, base_last = analyse(dst, region, quiet=True)

    # plant: raise EVERY internal temperature at 900 s by exactly 1.0 K.
    p = os.path.join(dst, "900", region, "T")
    t = open(p).read()
    k = t.index("internalField")
    body, j = read_list(t, k)
    vals = [float(v) + 1.0 for v in body.split()]
    open(p, "w").write(t[:t.index("(", k) + 1] + "\n"
                       + "\n".join(repr(v) for v in vals) + "\n" + t[j:])

    _, _, _, plant_last = analyse(dst, region, quiet=True)
    d_mean = (sum(plant_last["percell"]) - sum(base_last["percell"])) / N_CELLS
    d_E = plant_last["E"] - base_last["E"]
    expect_E = RHO * CP * N_CELLS * LX * LY * LZ * 1.0
    shutil.rmtree(tmp)

    print(f"  planted           +1.000000 K on all 960 cells at t = 900 s")
    print(f"  reader saw        {d_mean:+.6f} K on the per-cell mean")
    print(f"  stored energy     {d_E:+.4f} J  (expected {expect_E:+.4f} J)")
    ok = abs(d_mean - 1.0) < 1e-9 and abs(d_E - expect_E) < 1e-6
    print("  RESULT            " + ("PLANT SEEN -- the reader's zeros are evidence"
                                    if ok else "PLANT NOT SEEN -- REFUSE"))
    if not ok:
        sys.exit("REFUSE: planted control failed; this reader's numbers are "
                 "not admissible")
    return ok


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--case-dir", required=True)
    ap.add_argument("--region", default="module")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest(os.path.abspath(a.case_dir), a.region)
        print()
    analyse(os.path.abspath(a.case_dir), a.region)
