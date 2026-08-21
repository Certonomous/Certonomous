#!/usr/bin/env python3
"""
Verify every T10a mesh FROM THE MESH, never from the builder (L-142: the
build chain quotes itself; the written points do not).

For each case in T10a_registered.json, using the frozen comparator's own
readers (analyse_t10a.mesh_patches -> constant/polyMesh points+faces+boundary):

  spheres  every vertex of the inner/outer patch lies on the registered
           radius to 1e-9 relative (searchableSphere projection is analytic,
           so the honest expectation is round-off); 6 N^2 faces per patch;
           6 N^2 nr cells; the faceted patch area is BELOW 4 pi r^2 (chords
           subtend) with a deficit that must shrink with refinement.
  box      extents exactly the registered Lx Ly Lz (1e-12); patch areas
           exactly the registered areas (1e-10); registered face and cell
           counts; uniform spacing in each direction.
  hottel   registered extents, counts, and the empty pair OUT of the group.

  all      both/all radiating patches carry inGroups viewFactorWall and
           nothing else does; 0.orig/T patch values equal the registered
           temperatures for THIS case (B_C3's uniform 300, S_C1's unchanged
           600/300); boundaryRadiationProperties emissivities equal the
           registered ones for THIS case (S_C1's 1.0/1.0);
           radiationProperties smoothing and viewFactorsDict GaussQuadTol
           equal the case spec; controlDict has writeInterval STRICTLY less
           than endTime (L-140) and no residualControl (L-141).

PLANTED POSITIVES (L-143's rule: a guard is tested against a plant, not only
against a clean tree): a scratch copy of one sphere case and one box case
with every point coordinate scaled by (1 + 1e-7), and a scratch copy with a
wrong emissivity, must each FAIL this checker.  The run tree is never touched.

Zero solver compute.
"""
import json
import math
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REG = json.load(open(os.path.join(HERE, "T10a_registered.json")))
sys.path.insert(0, HERE)
import analyse_t10a as A     # noqa: E402  (frozen readers)

SCRATCH = os.environ.get(
    "T10A_SCRATCH",
    "/tmp/claude-1000/-home-ubuntu/64b13819-ff95-4d4d-a50f-3720bab19084/scratchpad")
RADIUS_TOL = 1e-9
PLANE_TOL = 1e-9      # blockMesh computes each point independently, so the
                      # coordinates of one mesh plane differ by ~1 ulp between
                      # rows for non-dyadic spacings (1/26, 1/42); round(x, 15)
                      # over-counts the planes.  Cluster with an absolute
                      # tolerance instead (domain is O(1) m).


def cluster(values, tol=PLANE_TOL):
    """Sorted cluster centres of a 1D point set: a new cluster starts where
    the gap to the previous value exceeds tol."""
    vs = sorted(values)
    groups = [[vs[0]]]
    for v in vs[1:]:
        if v - groups[-1][-1] > tol:
            groups.append([])
        groups[-1].append(v)
    return [sum(g) / len(g) for g in groups]


def fail_list():
    fails = []

    def note(cond, msg):
        if not cond:
            fails.append(msg)
        return cond
    return fails, note


def patch_T_written(case, patch, nfaces):
    return A.patch_values(os.path.join(case, "0.orig", "T"), patch, nfaces)[0]


def dict_val(case, path, key, typ=float):
    txt = open(os.path.join(case, *path.split("/"))).read()
    m = re.search(r"^\s*%s\s+([\w.+-]+)\s*;" % key, txt, re.M)
    if not m:
        return None
    v = m.group(1)
    if typ is bool:
        return v == "true"
    return typ(v)


def registered_patch_spec(name, c):
    """[(patch, T, eps)] for THIS case."""
    if c["kind"] == "spheres":
        e1, e2 = c["eps"]
        return [("inner", REG["spheres"]["T1"], e1),
                ("outer", REG["spheres"]["T2"], e2)]
    if c["kind"] == "box":
        Tu = c.get("T_uniform")
        return [(p, Tu if Tu is not None else REG["box"]["patches"][p]["T"], REG["box"]["eps"])
                for p in ("floor", "ceiling", "x0", "x1", "y0", "y1")]
    h = REG["hottel_2d_reported_only"]
    return [("floor", h["T_floor"], 1.0), ("ceiling", h["T_ceiling"], 1.0),
            ("x0", h["T_wall"], 1.0), ("x1", h["T_wall"], 1.0)]


def check_case(name, c, case_dir, quiet=False):
    """Returns (fails, facts).  Never raises on a wrong mesh; every defect is
    a listed failure so the planted positives can be asserted to fire."""
    fails, note = fail_list()
    say = (lambda *a: None) if quiet else print
    try:
        geom, order, pts = A.mesh_patches(case_dir)
    except SystemExit:
        return ["mesh unreadable or no viewFactorWall patch"], {}
    bnd = A.read_boundary(case_dir)
    ncells = A.ncells_from_owner(case_dir)
    spec = registered_patch_spec(name, c)
    facts = dict(ncells=ncells)

    note(ncells == c.get("cells", ncells), f"nCells {ncells} != registered {c.get('cells')}")
    want_group = [p for p, _, _ in spec]
    in_group = [p for p in bnd if "viewFactorWall" in bnd[p]["groups"]]
    note(sorted(in_group) == sorted(want_group),
         f"viewFactorWall group is {sorted(in_group)}, registered {sorted(want_group)}")
    nfaces_tot = sum(geom[p]["nFaces"] for p in order)
    note(nfaces_tot == c.get("faces", nfaces_tot),
         f"radiating faces {nfaces_tot} != registered {c.get('faces')}")

    if c["kind"] == "spheres":
        N, nr = c["N"], c["nr"]
        for p, rr in (("inner", REG["spheres"]["r1"]), ("outer", REG["spheres"]["r2"])):
            note(geom[p]["nFaces"] == 6 * N * N,
                 f"{p}: {geom[p]['nFaces']} faces != 6 N^2 = {6 * N * N}")
            rs = [math.sqrt(x * x + y * y + z * z) for x, y, z in geom[p]["vertices"]]
            off = max(abs(r - rr) for r in rs) / rr
            note(off <= RADIUS_TOL,
                 f"{p}: vertex radius off by {off:.2e} rel (> {RADIUS_TOL})")
            Af = sum(geom[p]["areas"])
            Ax = 4 * math.pi * rr * rr
            deficit = Af / Ax - 1.0
            facts[f"area_{p}"] = Af
            facts[f"deficit_{p}"] = deficit
            note(-0.05 < deficit < 0.0,
                 f"{p}: faceting deficit {deficit:+.3e} not in (-5 %, 0)")
            say(f"  {p:6s} {geom[p]['nFaces']:5d} faces, vertex radii on {rr} to "
                f"{off:.1e} rel, area {Af:.8f} (deficit {deficit:+.4%})")
        note(ncells == 6 * N * N * nr, f"cells {ncells} != 6 N^2 nr = {6 * N * N * nr}")
    elif c["kind"] == "box":
        N = c["N"]
        xs = cluster(p[0] for p in pts)
        ys = cluster(p[1] for p in pts)
        zs = cluster(p[2] for p in pts)
        L = (xs[-1] - xs[0], ys[-1] - ys[0], zs[-1] - zs[0])
        Lr = (REG["box"]["Lx"], REG["box"]["Ly"], REG["box"]["Lz"])
        note(max(abs(a - b) for a, b in zip(L, Lr)) <= 1e-12,
             f"extents {L} != registered {Lr}")
        note((len(xs), len(ys), len(zs)) == (N + 1, N + 1, N // 2 + 1),
             f"plane counts {(len(xs) - 1, len(ys) - 1, len(zs) - 1)} cells/dir, "
             f"registered ({N}, {N}, {N // 2})")
        for planes in (xs, ys, zs):
            d = [b - a for a, b in zip(planes, planes[1:])]
            note((max(d) - min(d)) / max(d) < 1e-9, "non-uniform spacing")
        for p, _, _ in spec:
            Ar = REG["box"]["patches"][p]["A"]
            note(abs(sum(geom[p]["areas"]) - Ar) <= 1e-10,
                 f"{p}: area {sum(geom[p]['areas'])} != {Ar}")
        say(f"  extents {L[0]:.10g} x {L[1]:.10g} x {L[2]:.10g}, "
            f"{len(xs) - 1} x {len(ys) - 1} x {len(zs) - 1} cells, "
            f"areas exact to 1e-10 on all 6 patches")
    else:  # hottel
        h = REG["hottel_2d_reported_only"]
        xs = cluster(p[0] for p in pts)
        ys = cluster(p[1] for p in pts)
        note(abs((xs[-1] - xs[0]) - h["w"]) <= 1e-12, "hottel width wrong")
        note(abs((ys[-1] - ys[0]) - h["h"]) <= 1e-12, "hottel height wrong")
        note("frontAndBack" in bnd and bnd["frontAndBack"]["type"] == "empty"
             and "viewFactorWall" not in bnd["frontAndBack"]["groups"],
             "frontAndBack must be empty and OUT of the group")
        say(f"  {xs[-1] - xs[0]:.10g} x {ys[-1] - ys[0]:.10g} 2D section, "
            f"{len(xs) - 1} x {len(ys) - 1} cells, empty pair out of the group")

    # dictionaries and 0.orig, read back
    for p, T, eps in spec:
        tw = patch_T_written(case_dir, p, geom[p]["nFaces"])
        note(tw == T, f"0.orig/T {p} = {tw}, registered {T}")
    try:
        ew = A.read_emissivities(case_dir, [p for p, _, _ in spec])
        for p, _, eps in spec:
            note(ew[p] == eps, f"emissivity {p} = {ew[p]}, registered {eps}")
    except SystemExit:
        fails.append("boundaryRadiationProperties unreadable")
    sm = dict_val(case_dir, "constant/radiationProperties", "smoothing", bool)
    note(sm == c.get("smoothing", False),
         f"radiationProperties smoothing {sm} != registered {c.get('smoothing')}")
    if "GaussQuadTol" in c:
        gq = dict_val(case_dir, "constant/viewFactorsDict", "GaussQuadTol")
        note(gq == c["GaussQuadTol"],
             f"GaussQuadTol {gq} != registered {c['GaussQuadTol']}")
    wi = dict_val(case_dir, "system/controlDict", "writeInterval")
    et = dict_val(case_dir, "system/controlDict", "endTime")
    note(wi is not None and et is not None and wi < et,
         f"writeInterval {wi} NOT strictly less than endTime {et} (L-140)")
    note("residualControl" not in open(os.path.join(case_dir, "system", "fvSolution")).read(),
         "fvSolution carries residualControl (L-141)")
    return fails, facts


def scale_points(case_dir, factor):
    pfile = os.path.join(case_dir, "constant", "polyMesh", "points")
    pts = A.read_points(case_dir)
    body = "\n".join(f"({x * factor:.16g} {y * factor:.16g} {z * factor:.16g})"
                     for x, y, z in pts)
    open(pfile, "w").write(
        "FoamFile\n{\n    version 2.0;\n    format ascii;\n"
        "    class vectorField;\n    object points;\n}\n"
        f"{len(pts)}\n(\n{body}\n)\n")


def planted_positives():
    """Each plant must make check_case FAIL.  Copies live in scratch only."""
    plants = []
    tmp = tempfile.mkdtemp(prefix="t10a_meshplant_", dir=SCRATCH)
    try:
        for name, mutate, what in (
                ("S_c", lambda d: scale_points(d, 1.0 + 1e-7),
                 "sphere points scaled by 1 + 1e-7 (vertex radii off registered)"),
                ("B_c", lambda d: scale_points(d, 1.0 + 1e-7),
                 "box points scaled by 1 + 1e-7 (extents off registered)"),
                ("S_c", lambda d: open(
                    os.path.join(d, "constant", "boundaryRadiationProperties"), "a").write(
                    "\ninner\n{\n    type lookup;\n    emissivity 0.65;\n"
                    "    absorptivity 0.65;\n}\n"),
                 "inner emissivity overridden to 0.65 (dictionary read-back)")):
            d = os.path.join(tmp, f"plant_{len(plants)}_{name}")
            shutil.copytree(os.path.join(HERE, name), d)
            mutate(d)
            fails, _ = check_case(name, REG["cases"][name], d, quiet=True)
            plants.append((what, bool(fails), fails[:2]))
        return plants
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    allok = True
    edge = {}
    for name, c in REG["cases"].items():
        d = os.path.join(HERE, name)
        print(f"\n{name} ({c['kind']}, {c['role']})")
        if not os.path.isdir(os.path.join(d, "constant", "polyMesh")):
            print("  NO MESH")
            allok = False
            continue
        fails, facts = check_case(name, c, d)
        edge[name] = c.get("N")
        if fails:
            allok = False
            for f in fails:
                print(f"  FAIL {f}")
        else:
            print(f"  OK ({facts.get('ncells')} cells)")

    print("\nrefinement ratios in radiating-face edge count (nominal 1.6):")
    for a, b in (("S_c", "S_m"), ("S_m", "S_f"), ("B_c", "B_m"), ("B_m", "B_f")):
        if edge.get(a) and edge.get(b):
            print(f"  {a}->{b}: {edge[b] / edge[a]:.4f}")
    print("\nfaceting deficits must SHRINK with refinement (spheres):")
    for p in ("inner", "outer"):
        ds = []
        for lv in ("S_c", "S_m", "S_f"):
            f2, facts = check_case(lv, REG["cases"][lv], os.path.join(HERE, lv), quiet=True)
            ds.append(facts.get(f"deficit_{p}"))
        mono = all(abs(a) > abs(b) for a, b in zip(ds, ds[1:]) if a and b)
        print(f"  {p}: " + "  ".join(f"{d:+.4%}" for d in ds if d is not None)
              + ("  (monotone)" if mono else "  NOT MONOTONE"))
        allok &= mono

    print("\nplanted positives (each must FAIL the checker):")
    for what, fired, sample in planted_positives():
        print(f"  {'FIRED' if fired else '** DID NOT FIRE **'}: {what}"
              + (f"  e.g. {sample[0]}" if sample else ""))
        allok &= fired

    print("\nALL MESHES VERIFIED, PLANTS FIRED" if allok else "\nMESH VERIFICATION FAILED")
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
