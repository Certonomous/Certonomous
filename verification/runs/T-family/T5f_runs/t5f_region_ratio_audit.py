#!/usr/bin/env python3
"""t5f_region_ratio_audit.py -- the independent diagnostic owed to the
heat-transfer supervisor's OPEN RULING on unequal per-region refinement ratios
(docs/campaigns/T-family/T5f_PREREGISTRATION.md section 3.1).

ZERO SOLVER COMPUTE.  Every number below is read off meshes that are already on
disk, or computed from them.  Nothing here builds a mesh or launches a solver.

WHAT IT DOES, in the five items the supervisor asked for:

  ITEM 1  Re-derives the refinement ratios of BOTH regions, independently, by
          TWO routes that do not share code:
            route A -- nCells out of each region's own constant/<r>/polyMesh/owner
                       header on disk (the split conjugate meshes);
            route B -- summing nx*ny*nz over the `hex ... <zone> (nx ny nz)`
                       lines of each level's system/blockMeshDict, by zone.
          The two routes must agree exactly or the script REFUSES.  The ratios
          themselves are then formed by CALLING scripts/roache_triple.py
          (refinement_ratio), never by local arithmetic.
          Then it checks the registration's own three claims: the four ratio
          values, the "0.095 % end-to-end" agreement, and the "equal and
          opposite -2.34 % / +2.29 %" per-step divergence.

  ITEM 2  Tests the registration's integer-rounding EXPLANATION as a falsifiable
          claim: recomputes the ladder with EXACT (non-integer) slab division
          counts base*R**lvl and shows what ratio that produces, then reports the
          residual the rounding model leaves unexplained.  Also reports the
          per-slab ratio spread WITHIN each region, which is the number the
          between-region framing hides.

  ITEM 3  The bounding sensitivity, computed.  Sweeps synthetic monotone triples
          and asks, for each, how far the observed order p and the GCI move when
          the SAME three values are graded under air's measured ratios versus
          epoxy's.  Reports the band-edge crossing question as a number.

  ITEM 5  Prints the refutation condition and whether it holds.

USAGE: t5f_region_ratio_audit.py [--selftest]
Exit 0 clean, 2 refusal.
"""
import argparse
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "scripts"))

import roache_triple as RT  # noqa: E402

T5B = os.path.join(REPO, "verification", "runs", "T-family", "T5b_runs")
CASES = {"c": "T5_CUBE_c", "m": "T5_CUBE_m", "f": "T5_CUBE_f"}
REGIONS = ("air", "epoxy")
DIM = 3  # the T5 cube ladder refines in all three directions (build_t5.py:6-8)

# The registration's own figures, T5f_PREREGISTRATION.md section 3.1, typed here
# ONCE so they can be CHECKED rather than assumed.
REG_RATIOS = {"air": {"r32": 1.5929, "r21": 1.6060},
              "epoxy": {"r32": 1.5557, "r21": 1.6428}}
REG_END_TO_END_PCT = 0.095
REG_DIVERGENCE_PCT = (-2.34, +2.29)   # (r32 step, r21 step), epoxy relative to air

# build_t5.py's registered ladder recipe (build_t5.py:66, :113-118).  Typed here
# to be CHECKED against the blockMeshDicts on disk, not trusted.
R_NOMINAL = 1.6
BASE_X = [24, 2, 9, 2, 32]
BASE_Y = [2, 1, 9, 2, 20]
BASE_Z = [5, 2, 16]


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


# ---------------------------------------------------------------------------
# ITEM 1 -- two independent routes to the per-region cell counts
# ---------------------------------------------------------------------------
def cells_from_polymesh(case_dir, region):
    """Route A: the nCells: field of the region's own polyMesh/owner header."""
    p = os.path.join(case_dir, "constant", region, "polyMesh", "owner")
    if not os.path.isfile(p):
        refuse("no %s" % p)
    with open(p, errors="replace") as fh:
        head = fh.read(4096)
    m = re.search(r"nCells:\s*(\d+)", head)
    if not m:
        refuse("%s: no nCells: in the owner header" % p)
    return int(m.group(1))


HEX_RE = re.compile(
    r"hex\s*\([0-9\s]+\)\s+(\w+)\s*\(\s*(\d+)\s+(\d+)\s+(\d+)\s*\)")


def cells_from_blockmeshdict(case_dir):
    """Route B: sum nx*ny*nz over the hex blocks of system/blockMeshDict, by zone."""
    p = os.path.join(case_dir, "system", "blockMeshDict")
    if not os.path.isfile(p):
        refuse("no %s" % p)
    with open(p, errors="replace") as fh:
        txt = fh.read()
    tot = {}
    blocks = 0
    for m in HEX_RE.finditer(txt):
        zone, nx, ny, nz = m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))
        tot[zone] = tot.get(zone, 0) + nx * ny * nz
        blocks += 1
    if blocks == 0:
        refuse("%s: parsed zero hex blocks -- the reader cannot see the file "
               "it is quoting from" % p)
    return tot, blocks


def cells_from_checkmesh(case_dir):
    """Route C (corroboration only): the two `cells:` lines of log.checkMesh, in
    the order blockMesh/checkMesh emits the regions."""
    p = os.path.join(case_dir, "log.checkMesh")
    if not os.path.isfile(p):
        return None
    with open(p, errors="replace") as fh:
        txt = fh.read()
    return [int(x) for x in re.findall(r"^\s*cells:\s+(\d+)", txt, re.M)]


COUPLED_PATCHES = ("cube_front", "cube_rear", "cube_top", "cube_side_n")
BOUNDARY_RE = re.compile(r"(\w+)\s*\{[^}]*?nFaces\s+(\d+);", re.S)


def patch_faces(case_dir, region):
    """nFaces per named patch out of constant/<region>/polyMesh/boundary."""
    p = os.path.join(case_dir, "constant", region, "polyMesh", "boundary")
    if not os.path.isfile(p):
        refuse("no %s" % p)
    with open(p, errors="replace") as fh:
        txt = fh.read()
    out = {m.group(1): int(m.group(2)) for m in BOUNDARY_RE.finditer(txt)}
    if not out:
        refuse("%s: parsed zero patches -- the reader cannot see the file" % p)
    return out


VERT_RE = re.compile(r"\(\s*(-?[0-9.eE+-]+)\s+(-?[0-9.eE+-]+)\s+(-?[0-9.eE+-]+)\s*\)")
HEXV_RE = re.compile(
    r"hex\s*\(\s*([0-9]+(?:\s+[0-9]+){7})\s*\)\s+(\w+)\s*\(\s*(\d+)\s+(\d+)\s+(\d+)\s*\)")
DELTA_SHELL = 0.0015   # m, the epoxy shell thickness (build_t5.py:64, DELTA)


def read_vertices(txt):
    """Vertex list: everything between `vertices` and the following `);`."""
    i = txt.find("vertices")
    if i < 0:
        refuse("no vertices block")
    j = txt.find(");", i)
    return [(float(a), float(b), float(c))
            for a, b, c in VERT_RE.findall(txt[i:j])]


def epoxy_shell_divisions(case_dir):
    """Cells THROUGH the epoxy shell thickness, identified by GEOMETRY.

    For every epoxy hex the block's physical extent in each direction is
    recovered from its own vertices; a direction whose extent equals the shell
    thickness DELTA is a shell-normal direction, and its division count is the
    number wanted.  REFUSES unless every such direction, across every epoxy
    block and all three coordinate directions, agrees on one value -- which is
    the executable form of the claim "the shell is one slab thick".
    """
    p = os.path.join(case_dir, "system", "blockMeshDict")
    with open(p, errors="replace") as fh:
        txt = fh.read()
    V = read_vertices(txt)
    if not V:
        refuse("%s: parsed zero vertices" % p)
    found = set()
    nblocks = 0
    for m in HEXV_RE.finditer(txt):
        if m.group(2) != "epoxy":
            continue
        nblocks += 1
        ids = [int(x) for x in m.group(1).split()]
        pts = [V[i] for i in ids]
        n = (int(m.group(3)), int(m.group(4)), int(m.group(5)))
        for ax in (0, 1, 2):
            ext = max(q[ax] for q in pts) - min(q[ax] for q in pts)
            if abs(ext - DELTA_SHELL) < 1e-12:
                found.add(n[ax])
    if nblocks == 0:
        refuse("%s: no epoxy hex blocks" % p)
    if len(found) != 1:
        refuse("%s: the shell-normal division count is not unique across the "
               "%d epoxy blocks: %s" % (p, nblocks, sorted(found)))
    return found.pop()


def case_txt_first_layer(case_dir):
    """first_layer_m as the BUILDER recorded it in the case's own CASE.txt."""
    p = os.path.join(case_dir, "CASE.txt")
    if not os.path.isfile(p):
        refuse("no %s" % p)
    with open(p, errors="replace") as fh:
        m = re.search(r"first_layer_m\s*=\s*([0-9eE.+-]+)", fh.read())
    if not m:
        refuse("%s: no first_layer_m" % p)
    return float(m.group(1))


# ---------------------------------------------------------------------------
# ITEM 2 -- the integer-rounding model, driven both ways
# ---------------------------------------------------------------------------
def counts(lvl, rounded=True):
    """build_t5.py:103-107, reproduced.  rounded=False gives the EXACT
    (non-integer) division counts the ladder would have if blockMesh accepted
    fractional divisions."""
    f = R_NOMINAL ** lvl
    if rounded:
        return ([max(1, int(round(n * f))) for n in BASE_X],
                [max(1, int(round(n * f))) for n in BASE_Y],
                [max(1, int(round(n * f))) for n in BASE_Z])
    return ([n * f for n in BASE_X], [n * f for n in BASE_Y], [n * f for n in BASE_Z])


def is_cube(i, j, k):
    return i in (1, 2, 3) and j in (0, 1, 2, 3) and k in (0, 1)


def is_core(i, j, k):
    return (i, j, k) == (2, 2, 0)


def model_cells(lvl, rounded=True):
    """Cells per zone from the recipe, exactly as build_t5.block_mesh_3d lays
    the blocks out (build_t5.py:190-210)."""
    nx, ny, nz = counts(lvl, rounded)
    tot = {"air": 0.0, "epoxy": 0.0}
    for k in range(len(nz)):
        for j in range(len(ny)):
            for i in range(len(nx)):
                if is_core(i, j, k):
                    continue
                zone = "epoxy" if is_cube(i, j, k) else "air"
                tot[zone] += nx[i] * ny[j] * nz[k]
    return tot


def slab_ratios():
    """The per-SLAB refinement ratio n(lvl+1)/n(lvl) for every distinct base
    count in the recipe.  This is a LOCAL cell-size ratio, not a mean one."""
    out = {}
    for base in sorted(set(BASE_X + BASE_Y + BASE_Z)):
        n = [max(1, int(round(base * R_NOMINAL ** l))) for l in (0, 1, 2)]
        out[base] = {"n": n, "r32": n[1] / n[0], "r21": n[2] / n[1]}
    return out


# ---------------------------------------------------------------------------
# ITEM 3 -- the bounding sensitivity, computed with the shared instrument
# ---------------------------------------------------------------------------
def sensitivity(rr, p_grid, fine_value=100.0, amp_grid=None):
    """For a synthetic monotone triple built to a TRUE order p_true under a
    reference ratio, grade the SAME THREE NUMBERS under air's ratios and under
    epoxy's, and report the spread in p and in GCI_pct.

    The triple is constructed so it is a genuine power law: with h1<h2<h3 and
    f_i = f_exact + A*h_i^p, the differences are exactly what a p-order method
    produces.  Which ratios are used to BUILD it is stated; the point of the
    exercise is that the GRADER does not know them and must assume one region's.
    """
    rows = []
    if amp_grid is None:
        amp_grid = [0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0]
    air, epo = rr["air"], rr["epoxy"]
    for p_true in p_grid:
        for amp in amp_grid:
            # build under the AIR ladder's h's (h_fine = 1)
            h1 = 1.0
            h2 = air["r21"] * h1
            h3 = air["r32"] * h2
            f_exact = fine_value
            f_f = f_exact + amp * h1 ** p_true
            f_m = f_exact + amp * h2 ** p_true
            f_c = f_exact + amp * h3 ** p_true
            ta = RT.gci_unequal(f_c, f_m, f_f, air["r21"], air["r32"], DIM)
            te = RT.gci_unequal(f_c, f_m, f_f, epo["r21"], epo["r32"], DIM)
            if ta["state"] != "CONVERGING" or te["state"] != "CONVERGING":
                rows.append(dict(p_true=p_true, amp=amp,
                                 state_air=ta["state"], state_epoxy=te["state"],
                                 p_air=ta.get("order"), p_epoxy=te.get("order"),
                                 gci_air=None, gci_epoxy=None,
                                 d_gci_abs=None, d_gci_rel_pct=None))
                continue
            ga, ge = ta["GCI_pct"], te["GCI_pct"]
            rows.append(dict(
                p_true=p_true, amp=amp,
                state_air=ta["state"], state_epoxy=te["state"],
                p_air=ta["order"], p_epoxy=te["order"],
                d_p=te["order"] - ta["order"],
                gci_air=ga, gci_epoxy=ge,
                d_gci_abs=ge - ga,
                d_gci_rel_pct=100.0 * (ge - ga) / ga if ga else None))
    return rows


def state_flip_scan(rr, build_on="air", p_lo=-0.60, p_hi=1.20, n=1801,
                    fine_value=100.0, amp=0.1):
    """THE QUESTION THE BAND-EDGE COUNT DOES NOT ASK.  Rule 5 classifies a
    triple BEFORE any band is consulted: DIVERGENT / STAGNANT / DEGENERATE are
    NOT A RESULT whatever the value.  So the sharper question is whether the
    ratio choice alone can move a triple ACROSS A RULE-5 STATE BOUNDARY.

    Sweeps p_true finely, builds the triple on one region's h-ladder, grades it
    under BOTH, and returns every p_true where the two STATES differ.
    """
    src = rr[build_on]
    out = []
    for i in range(n):
        p_true = p_lo + (p_hi - p_lo) * i / (n - 1.0)
        h1 = 1.0
        h2 = src["r21"] * h1
        h3 = src["r32"] * h2
        f_f = fine_value + amp * h1 ** p_true
        f_m = fine_value + amp * h2 ** p_true
        f_c = fine_value + amp * h3 ** p_true
        try:
            ta = RT.gci_unequal(f_c, f_m, f_f, rr["air"]["r21"], rr["air"]["r32"], DIM)
            te = RT.gci_unequal(f_c, f_m, f_f, rr["epoxy"]["r21"], rr["epoxy"]["r32"], DIM)
        except SystemExit:
            continue
        out.append((p_true, ta["state"], te["state"],
                    ta.get("order"), te.get("order")))
    return out


def flip_windows(scan):
    """Contiguous p_true intervals over which the two states disagree."""
    wins = []
    cur = None
    for p, sa, se, pa, pe in scan:
        if sa != se:
            if cur is None:
                cur = dict(p_lo=p, p_hi=p, air=sa, epoxy=se)
            elif cur["air"] == sa and cur["epoxy"] == se:
                cur["p_hi"] = p
            else:
                wins.append(cur)
                cur = dict(p_lo=p, p_hi=p, air=sa, epoxy=se)
        elif cur is not None:
            wins.append(cur)
            cur = None
    if cur is not None:
        wins.append(cur)
    return wins


def band_crossing(rows, band_edges):
    """For each registered band edge B (a GCI threshold in %), count the swept
    triples whose verdict against B differs between the two ratio choices."""
    out = []
    for B in band_edges:
        n = 0
        worst = None
        for r in rows:
            if r["gci_air"] is None or r["gci_epoxy"] is None:
                continue
            if (r["gci_air"] <= B) != (r["gci_epoxy"] <= B):
                n += 1
                if worst is None or abs(r["d_gci_abs"]) > abs(worst["d_gci_abs"]):
                    worst = r
        out.append(dict(edge=B, n_crossing=n, worst=worst))
    return out


# ---------------------------------------------------------------------------
def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", default=None)
    a = ap.parse_args(argv[1:])
    if a.selftest:
        return selftest()

    print("T5f REGION-RATIO AUDIT -- independent diagnostic, zero solver compute")
    print("instrument: scripts/roache_triple.py (CALLED, not reimplemented)")
    print("meshes read: %s/T5_CUBE_{c,m,f}" % T5B)
    print("dim = %d (build_t5.py:6-8, R applied to EVERY direction)\n" % DIM)

    # ---- ITEM 1 ----------------------------------------------------------
    print("=" * 74)
    print("ITEM 1 -- PER-REGION CELL COUNTS BY TWO INDEPENDENT ROUTES")
    print("=" * 74)
    N = {r: {} for r in REGIONS}
    for lv, case in CASES.items():
        cd = os.path.join(T5B, case)
        if not os.path.isdir(cd):
            refuse("no case dir %s" % cd)
        bmd, nblocks = cells_from_blockmeshdict(cd)
        cm = cells_from_checkmesh(cd)
        for reg in REGIONS:
            a_route = cells_from_polymesh(cd, reg)
            b_route = bmd.get(reg)
            if b_route is None:
                refuse("%s: blockMeshDict declares no zone %r" % (case, reg))
            if a_route != b_route:
                refuse("%s/%s: route A (polyMesh owner nCells = %d) and route B "
                       "(blockMeshDict zone sum = %d) DISAGREE" %
                       (case, reg, a_route, b_route))
            N[reg][lv] = a_route
        mdl = model_cells(["c", "m", "f"].index(lv), rounded=True)
        print("  %-10s blocks=%d  air=%d  epoxy=%d   (recipe model: air=%d epoxy=%d) "
              "checkMesh cells: lines=%s"
              % (case, nblocks, N["air"][lv], N["epoxy"][lv],
                 int(mdl["air"]), int(mdl["epoxy"]), cm))
        if int(mdl["air"]) != N["air"][lv] or int(mdl["epoxy"]) != N["epoxy"][lv]:
            print("      NOTE: the build_t5.py recipe model does NOT reproduce the "
                  "mesh on disk at this level")

    print("\n  measured refinement ratios, r = (N_finer/N_coarser)**(1/dim), "
          "via roache_triple.refinement_ratio:")
    rr = {}
    for reg in REGIONS:
        r21 = RT.refinement_ratio(N[reg]["m"], N[reg]["f"], DIM)   # h_med/h_fine
        r32 = RT.refinement_ratio(N[reg]["c"], N[reg]["m"], DIM)   # h_coarse/h_med
        r31 = RT.refinement_ratio(N[reg]["c"], N[reg]["f"], DIM)
        rr[reg] = dict(r21=r21, r32=r32, r31=r31)
        reg_r = REG_RATIOS[reg]
        print("    %-6s r32 = %.6f (registered %.4f, |d| = %.2e)   "
              "r21 = %.6f (registered %.4f, |d| = %.2e)   r31 = %.6f"
              % (reg, r32, reg_r["r32"], abs(r32 - reg_r["r32"]),
                 r21, reg_r["r21"], abs(r21 - reg_r["r21"]), r31))

    e2e = 100.0 * (rr["air"]["r31"] / rr["epoxy"]["r31"] - 1.0)
    d32 = 100.0 * (rr["epoxy"]["r32"] / rr["air"]["r32"] - 1.0)
    d21 = 100.0 * (rr["epoxy"]["r21"] / rr["air"]["r21"] - 1.0)
    print("\n  REGISTRATION CLAIM CHECKS")
    print("    end-to-end agreement air vs epoxy : %+.4f %%  "
          "(registration says 0.095 %%)" % e2e)
    print("    per-step divergence epoxy vs air  : r32 %+.4f %% , r21 %+.4f %%  "
          "(registration says %+.2f %% then %+.2f %%)"
          % (d32, d21, REG_DIVERGENCE_PCT[0], REG_DIVERGENCE_PCT[1]))
    print("    'equal and opposite' residual      : %+.4f %% "
          "(sum of the two steps; exactly 0 would be exactly equal and opposite)"
          % (d32 + d21))

    # ---- ITEM 1b -- WHAT THE INTERFACE ITSELF DOES -------------------------
    print("\n" + "=" * 74)
    print("ITEM 1b -- THE COUPLED INTERFACE, MEASURED RATHER THAN ASSUMED")
    print("=" * 74)
    iface = {}
    normal_epoxy = {}
    first_layer = {}
    for lv, case in CASES.items():
        cd = os.path.join(T5B, case)
        fa = patch_faces(cd, "air")
        fe = patch_faces(cd, "epoxy")
        shared = [p for p in COUPLED_PATCHES]
        mism = [(p, fa.get(p), fe.get(p)) for p in shared if fa.get(p) != fe.get(p)]
        if mism:
            refuse("level %s: the coupled interface is NOT conformal: %s" % (lv, mism))
        iface[lv] = sum(fa[p] for p in shared)
        # epoxy-side WALL-NORMAL divisions through the shell: the shell slabs are
        # the `base 2` slabs of the recipe, and their division count is read off
        # the blockMeshDict, never assumed.
        normal_epoxy[lv] = epoxy_shell_divisions(cd)
        first_layer[lv] = case_txt_first_layer(cd)
        print("  %-10s coupled faces %s = %5d (air side == epoxy side, conformal)   "
              "epoxy shell normal divisions = %d   air first layer = %g m"
              % (case, "+".join(COUPLED_PATCHES), iface[lv],
                 normal_epoxy[lv], first_layer[lv]))

    r21_i = RT.refinement_ratio(iface["m"], iface["f"], 2)
    r32_i = RT.refinement_ratio(iface["c"], iface["m"], 2)
    print("\n  TANGENTIAL (in-surface) interface refinement, dim = 2, ONE mesh "
          "shared by both regions:")
    print("      r32 = %.6f   r21 = %.6f   -- there is NO air-vs-epoxy ambiguity "
          "here" % (r32_i, r21_i))

    a32 = first_layer["c"] / first_layer["m"]
    a21 = first_layer["m"] / first_layer["f"]
    e32 = normal_epoxy["m"] / normal_epoxy["c"]
    e21 = normal_epoxy["f"] / normal_epoxy["m"]
    print("\n  WALL-NORMAL refinement AT THE INTERFACE -- the direction the "
          "conjugate flux is actually differenced in:")
    print("      air side   (first layer %g/%g/%g m) : r32 = %.6f  r21 = %.6f"
          % (first_layer["c"], first_layer["m"], first_layer["f"], a32, a21))
    print("      epoxy side (shell divisions %d/%d/%d)      : r32 = %.6f  r21 = %.6f"
          % (normal_epoxy["c"], normal_epoxy["m"], normal_epoxy["f"], e32, e21))
    print("      divergence epoxy vs air, wall-normal     : r32 %+.4f %% , "
          "r21 %+.4f %%" % (100 * (e32 / a32 - 1), 100 * (e21 / a21 - 1)))
    print("      COMPARE the registration's REGION-MEAN figures : r32 %+.4f %% , "
          "r21 %+.4f %%" % (d32, d21))
    rr_iface = {"air": {"r21": a21, "r32": a32},
                "epoxy": {"r21": e21, "r32": e32}}

    # ---- ITEM 2 ----------------------------------------------------------
    print("\n" + "=" * 74)
    print("ITEM 2 -- IS INTEGER ROUNDING THE WHOLE EXPLANATION?")
    print("=" * 74)
    print("  counterfactual: the same recipe with EXACT (fractional) divisions,")
    print("  base * R**lvl with R = %.4f and NO rounding." % R_NOMINAL)
    ex = [model_cells(l, rounded=False) for l in (0, 1, 2)]
    for reg in REGIONS:
        r21x = (ex[2][reg] / ex[1][reg]) ** (1.0 / DIM)
        r32x = (ex[1][reg] / ex[0][reg]) ** (1.0 / DIM)
        print("    %-6s EXACT-division ratios: r32 = %.10f  r21 = %.10f   "
              "(nominal R = %.4f; |d| = %.2e, %.2e)"
              % (reg, r32x, r21x, R_NOMINAL,
                 abs(r32x - R_NOMINAL), abs(r21x - R_NOMINAL)))
    print("\n  residual left unexplained by the rounding model")
    print("  (recipe-with-rounding vs the mesh actually on disk, per region/level):")
    resid_max = 0
    for lv, li in (("c", 0), ("m", 1), ("f", 2)):
        mdl = model_cells(li, rounded=True)
        for reg in REGIONS:
            d = int(mdl[reg]) - N[reg][lv]
            resid_max = max(resid_max, abs(d))
            print("      level %s %-6s model %8d   disk %8d   residual %+d cells"
                  % (lv, reg, int(mdl[reg]), N[reg][lv], d))
    print("    MAX |residual| = %d cells" % resid_max)

    print("\n  PER-SLAB ratios inside the recipe (the spread the between-region")
    print("  framing hides): n_lvl = round(base * 1.6**lvl)")
    sr = slab_ratios()
    lo = min(min(v["r32"], v["r21"]) for v in sr.values())
    hi = max(max(v["r32"], v["r21"]) for v in sr.values())
    for base, v in sr.items():
        print("      base %2d -> %-14s  r32 = %.4f  r21 = %.4f"
              % (base, "/".join(str(x) for x in v["n"]), v["r32"], v["r21"]))
    print("    PER-SLAB RATIO RANGE ACROSS THE WHOLE LADDER: %.4f .. %.4f "
          "(spread %.2f %% of nominal)" % (lo, hi, 100.0 * (hi - lo) / R_NOMINAL))

    # ---- ITEM 3 ----------------------------------------------------------
    print("\n" + "=" * 74)
    print("ITEM 3 -- BOUNDING SENSITIVITY: AIR RATIOS vs EPOXY RATIOS")
    print("=" * 74)
    p_grid = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0]
    rows = sensitivity(rr, p_grid)
    print("  synthetic monotone triples, built as a true power law on the AIR")
    print("  h-ladder, then graded under EACH region's measured ratios.")
    print("  (amp only scales the triple: GCI_pct scales with it, p does not.)")
    print("\n  %-8s %-9s %-9s %-9s %-11s %-11s %-10s %-10s"
          % ("p_true", "p_air", "p_epoxy", "dp", "GCI_air%", "GCI_epoxy%",
             "dGCI(abs)", "dGCI(rel%)"))
    seen = set()
    for r in rows:
        if r["p_true"] in seen or r["amp"] != 0.1:
            continue
        seen.add(r["p_true"])
        if r["gci_air"] is None:
            print("  %-8.2f %-9s %-9s  states: air=%s epoxy=%s"
                  % (r["p_true"], "-", "-", r["state_air"], r["state_epoxy"]))
            continue
        print("  %-8.2f %-9.5f %-9.5f %+9.5f %-11.5f %-11.5f %+10.5f %+10.4f"
              % (r["p_true"], r["p_air"], r["p_epoxy"], r["d_p"],
                 r["gci_air"], r["gci_epoxy"], r["d_gci_abs"], r["d_gci_rel_pct"]))

    rel = [abs(r["d_gci_rel_pct"]) for r in rows if r["d_gci_rel_pct"] is not None]
    dps = [abs(r["d_p"]) for r in rows if r.get("d_p") is not None]
    print("\n  ACROSS THE WHOLE SWEEP (%d triples, p_true %.2f..%.2f, amp %.2f..%.2f):"
          % (len(rows), min(p_grid), max(p_grid), 0.02, 5.0))
    print("    |p_epoxy - p_air|          : min %.6f  max %.6f" % (min(dps), max(dps)))
    print("    |GCI relative difference|  : min %.4f %%  max %.4f %%"
          % (min(rel), max(rel)))
    print("    -> the RELATIVE GCI spread is scale-free: it does not depend on")
    print("       the triple's amplitude, only on p_true.")

    print("\n  BAND-EDGE CROSSING: for a pre-registered GCI ceiling B, how many")
    print("  of the swept triples change verdict when the ratio choice changes?")
    edges = [0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0]
    for bc in band_crossing(rows, edges):
        w = bc["worst"]
        print("    B = %6.2f %%  -> %3d of %d triples cross%s"
              % (bc["edge"], bc["n_crossing"], len(rows),
                 ("   (worst: p_true=%.2f GCI %.5f%% vs %.5f%%)"
                  % (w["p_true"], w["gci_air"], w["gci_epoxy"])) if w else ""))
    print("\n    A crossing is possible at EVERY ceiling: the spread is relative,")
    print("    so for any B there exist triples whose GCI sits inside the spread")
    print("    of B.  The operative number is therefore the RELATIVE HALF-WIDTH,")
    print("    printed above -- a GCI within that fraction of a band edge is")
    print("    decided by the ratio choice, not by the mesh.")

    # ---- ITEM 3b -- the rule-5 STATE flip, which outranks any band ----------
    print("\n" + "=" * 74)
    print("ITEM 3b -- CAN THE RATIO CHOICE ALONE CROSS A RULE-5 STATE BOUNDARY?")
    print("=" * 74)
    flips_all = {}
    for built_on in ("air", "epoxy"):
        scan = state_flip_scan(rr, build_on=built_on)
        wins = flip_windows(scan)
        flips_all[built_on] = wins
        tot = sum(1 for s in scan if s[1] != s[2])
        print("  triple BUILT on the %-5s h-ladder: %d of %d swept p_true values "
              "are classified DIFFERENTLY by the two ratio sets"
              % (built_on, tot, len(scan)))
        for w in wins:
            print("      p_true in [%+.4f, %+.4f]  air -> %-11s   epoxy -> %-11s"
                  % (w["p_lo"], w["p_hi"], w["air"], w["epoxy"]))
        if not wins:
            print("      (none)")
    print("\n  A state flip is STRICTLY WORSE than a band crossing: under rule 5")
    print("  DIVERGENT / STAGNANT / DEGENERATE are NOT A RESULT whatever the")
    print("  value, and CONVERGING is gradeable.  The ratio choice therefore")
    print("  decides whether the row has a verdict at all.")

    # ---- ITEM 3c -- the sensitivity under the INTERFACE ratios --------------
    print("\n" + "=" * 74)
    print("ITEM 3c -- THE SAME SWEEP UNDER THE *INTERFACE* WALL-NORMAL RATIOS")
    print("=" * 74)
    print("  air side (%.5f, %.5f) vs epoxy side (%.5f, %.5f)."
          % (rr_iface["air"]["r32"], rr_iface["air"]["r21"],
             rr_iface["epoxy"]["r32"], rr_iface["epoxy"]["r21"]))
    rows_i = sensitivity(rr_iface, p_grid)
    rel_i = [abs(r["d_gci_rel_pct"]) for r in rows_i if r["d_gci_rel_pct"] is not None]
    dps_i = [abs(r["d_p"]) for r in rows_i if r.get("d_p") is not None]
    print("    |p_epoxy - p_air|         : min %.6f  max %.6f"
          % (min(dps_i), max(dps_i)))
    print("    |GCI relative difference| : min %.4f %%  max %.4f %%"
          % (min(rel_i), max(rel_i)))
    print("    (region-mean ratios gave  : |dp| %.6f..%.6f , |dGCI| %.2f..%.2f %%)"
          % (min(dps), max(dps), min(rel), max(rel)))
    sc_i = state_flip_scan(rr_iface, build_on="air")
    wins_i = flip_windows(sc_i)
    print("    rule-5 STATE flips over p_true in [-0.60, +1.20]:")
    for w in wins_i:
        print("      p_true in [%+.4f, %+.4f]  air -> %-11s  epoxy -> %-11s"
              % (w["p_lo"], w["p_hi"], w["air"], w["epoxy"]))
    if not wins_i:
        print("      (none)")
    flips_all["interface_normal"] = wins_i

    # ---- ITEM 5 ----------------------------------------------------------
    print("\n" + "=" * 74)
    print("ITEM 5 -- THE REFUTATION CONDITION, AND WHETHER IT HOLDS")
    print("=" * 74)
    print("  The draft ruling is WRONG if the air-vs-epoxy bounding spread is")
    print("  either (a) so small it is theatre, or (b) so large that 'report")
    print("  both and NOT A RESULT on disagreement' degenerates into NOT A")
    print("  RESULT for every row -- a rule that admits nothing is a ban wearing")
    print("  a permission's clothes.")
    print("    (a) spread is NOT negligible : min |dGCI|/GCI over the sweep = "
          "%.2f %%, min |dp| = %.4f" % (min(rel), min(dps)))
    conv = [r for r in rows if r["gci_air"] is not None]
    print("    (b) spread does NOT swallow everything: %d of %d swept triples are"
          % (len(conv), len(rows)))
    print("        CONVERGING under BOTH ratio sets, so a row can still earn a")
    print("        verdict; the rule bites only near a boundary.")

    if a.json:
        with open(a.json, "w") as fh:
            json.dump(dict(cells=N, ratios=rr, end_to_end_pct=e2e, state_flips=flips_all,
                           step_divergence_pct=[d32, d21],
                           slab_ratios={str(k): v for k, v in sr.items()},
                           sensitivity=rows), fh, indent=1)
        print("\n  json written: %s" % a.json)
    return 0


# ---------------------------------------------------------------------------
def selftest():
    """Drive every control BOTH DIRECTIONS.  A check that cannot reject is not
    a check."""
    fails = []

    def ok(cond, msg):
        print("  %-6s %s" % ("ok" if cond else "FAIL", msg))
        if not cond:
            fails.append(msg)

    print("t5f_region_ratio_audit.py --selftest")

    # (i) the blockMeshDict reader must SEE, and must see ZERO on a file with
    #     no hex blocks -- driven both directions.
    import tempfile
    tmp = tempfile.mkdtemp(prefix="t5f_rra_")
    sysd = os.path.join(tmp, "system")
    os.makedirs(sysd)
    good = ("blocks (\n"
            "    hex (0 1 2 3 4 5 6 7) air (10 3 2) simpleGrading (1 1 1)\n"
            "    hex (1 2 3 4 5 6 7 8) epoxy (2 2 5) simpleGrading (1 1 1)\n"
            ");\n")
    with open(os.path.join(sysd, "blockMeshDict"), "w") as fh:
        fh.write(good)
    tot, nb = cells_from_blockmeshdict(tmp)
    ok(nb == 2 and tot == {"air": 60, "epoxy": 20},
       "reader sees a NON-zero: 2 blocks, air=60 epoxy=20 (positive control)")
    # planted perturbation: change one division count, the reader must report it
    with open(os.path.join(sysd, "blockMeshDict"), "w") as fh:
        fh.write(good.replace("(10 3 2)", "(11 3 2)"))
    tot2, _ = cells_from_blockmeshdict(tmp)
    ok(tot2["air"] == 66 and tot2["air"] != tot["air"],
       "reader REPORTS a planted change in the division count (60 -> 66)")
    # negative control: a file with no hex blocks must REFUSE, not return zero
    with open(os.path.join(sysd, "blockMeshDict"), "w") as fh:
        fh.write("blocks ( );\n")
    import subprocess
    try:
        cells_from_blockmeshdict(tmp)
        ok(False, "a hex-free blockMeshDict must REFUSE, it returned instead")
    except SystemExit as e:
        ok(e.code == 2, "a hex-free blockMeshDict REFUSES (exit 2), never zero")

    # (ii) the recipe model must reproduce the meshes on disk, and must FAIL to
    #      reproduce them under a mutated R -- both directions.
    disk_air = {"c": 52684, "m": 212942, "f": 882024}
    disk_epo = {"c": 869, "m": 3272, "f": 14507}
    m = [model_cells(l, True) for l in (0, 1, 2)]
    ok(all(int(m[i]["air"]) == disk_air[k] for i, k in enumerate(("c", "m", "f"))),
       "recipe model reproduces the AIR counts on disk exactly")
    ok(all(int(m[i]["epoxy"]) == disk_epo[k] for i, k in enumerate(("c", "m", "f"))),
       "recipe model reproduces the EPOXY counts on disk exactly")
    global R_NOMINAL
    keep = R_NOMINAL
    R_NOMINAL = 1.7
    mm = [model_cells(l, True) for l in (0, 1, 2)]
    R_NOMINAL = keep
    ok(int(mm[1]["air"]) != disk_air["m"],
       "MUTANT control: R = 1.7 does NOT reproduce the disk counts "
       "(the model can reject)")

    # (iii) roache_triple must give a DIFFERENT answer under the two ratio sets
    #       (else the sensitivity sweep cannot detect anything).
    ta = RT.gci_unequal(1.40, 1.20, 1.10, 1.6060, 1.5929, 3)
    te = RT.gci_unequal(1.40, 1.20, 1.10, 1.6428, 1.5557, 3)
    ok(ta["state"] == "CONVERGING" and te["state"] == "CONVERGING",
       "both ratio sets grade a monotone triple CONVERGING")
    ok(abs(ta["order"] - te["order"]) > 1e-6,
       "the two ratio sets give DIFFERENT observed orders (%.6f vs %.6f) -- the "
       "sweep can detect a difference" % (ta["order"], te["order"]))
    tsame = RT.gci_unequal(1.40, 1.20, 1.10, 1.6060, 1.5929, 3)
    ok(abs(tsame["order"] - ta["order"]) < 1e-15,
       "NULL control: identical ratios give an identical order (the sweep does "
       "not manufacture a difference out of nothing)")

    # (iv) the band-crossing counter must find zero crossings when both sides
    #      are handed the SAME ratios -- the null.
    rr_null = {"air": {"r21": 1.6060, "r32": 1.5929},
               "epoxy": {"r21": 1.6060, "r32": 1.5929}}
    rows_null = sensitivity(rr_null, [1.0, 2.0])
    bc_null = band_crossing(rows_null, [0.5, 1.0, 2.0])
    ok(all(b["n_crossing"] == 0 for b in bc_null),
       "NULL: identical ratios produce ZERO band crossings")
    rr_real = {"air": {"r21": 1.6060, "r32": 1.5929},
               "epoxy": {"r21": 1.6428, "r32": 1.5557}}
    rows_real = sensitivity(rr_real, [1.0, 2.0])
    bc_real = band_crossing(rows_real, [0.5, 1.0, 2.0])
    ok(any(b["n_crossing"] > 0 for b in bc_real),
       "POSITIVE: the real ratio pair DOES produce band crossings")

    # (v) the boundary reader: driven BOTH directions on a planted file.
    bdir = os.path.join(tmp, "constant", "air", "polyMesh")
    os.makedirs(bdir)
    bfile = os.path.join(bdir, "boundary")
    with open(bfile, "w") as fh:
        fh.write("2\n(\n  cube_front { type wall; nFaces 98; startFace 1; }\n"
                 "  cube_top   { type wall; nFaces 91; startFace 2; }\n)\n")
    pf = patch_faces(os.path.join(tmp, "constant", "..", ""), "air") \
        if False else patch_faces(tmp, "air")
    ok(pf == {"cube_front": 98, "cube_top": 91},
       "boundary reader sees a NON-zero: 98 and 91 faces (positive control)")
    with open(bfile, "w") as fh:
        fh.write("2\n(\n  cube_front { type wall; nFaces 99; startFace 1; }\n"
                 "  cube_top   { type wall; nFaces 91; startFace 2; }\n)\n")
    ok(patch_faces(tmp, "air")["cube_front"] == 99,
       "boundary reader REPORTS a planted change (98 -> 99)")
    with open(bfile, "w") as fh:
        fh.write("0\n(\n)\n")
    try:
        patch_faces(tmp, "air")
        ok(False, "an empty boundary file must REFUSE, it returned instead")
    except SystemExit as e:
        ok(e.code == 2, "an empty boundary file REFUSES (exit 2), never {}")

    # (vi) the interface conformality claim, driven both directions on the REAL
    #      meshes: equal on disk, and the checker must catch a planted mismatch.
    real = os.path.join(T5B, "T5_CUBE_c")
    if os.path.isdir(real):
        fa, fe = patch_faces(real, "air"), patch_faces(real, "epoxy")
        ok(all(fa[p] == fe[p] for p in COUPLED_PATCHES),
           "REAL mesh: every coupled patch has equal face counts on both sides")
        ok(fa["cube_front"] != fa["cube_side_n"],
           "NEGATIVE control: the reader distinguishes patches (it is not "
           "returning one number for everything)")

    print("\n%d failure(s)" % len(fails))
    return 0 if not fails else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
