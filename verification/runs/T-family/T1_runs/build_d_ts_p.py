#!/usr/bin/env python3
"""
Build, mesh, and VERIFY the two parabolic-inlet ladders registered in
DIAGNOSTIC_PREDICTION.md ("NEXT TEST, REGISTERED BEFORE IT IS BUILT,
2026-08-20 evening"):

    D_Ts_Re25_P_c/m/f   -- replicate of D_Ts_Re25_c/m/f   (Re = 25,  Pe = 17.75)
    L_Ts_P_c/m/f        -- replicate of L_Ts_c/m/f        (Re = 100, Pe = 71.00)

Each case is identical to its slug-inlet original in EVERY BYTE except the
inlet entry of U, which becomes the exact Poiseuille profile evaluated at the
mesh's own inlet face centroids:

    u_x(r_c) = s * 2 U_b (1 - (r_c / R_wall)^2)

with U_b = Re nu / D (nominal, the value CASE.txt's `U` line carries and
analyse_t1c.measure reads), R_wall = max y over the mesh points (the wedge's
flat chord wall, R cos(2.5 deg) -- the same rule as analyse_t1c.wall_radius),
and s the single scalar that makes the DISCRETE flow rate exact,

    sum_f u_x,f A_f  ==  U_b sum_f A_f ,

so the profile shape is exact at the face centroids and the mass flow is exact
by construction (s = 1 + O(1e-4..1e-3), the quadrature defect of a parabola
sampled at cell centres on a uniform mesh).  The internalField, the outlet,
wall and wedge entries of U, and every other file come from the frozen builder
(build_t1c.py) through the same generator calls build_d_ts.py makes.

HOW THE EXISTING CHAIN WENT FROM BUILDER OUTPUT TO A RUNNING SOLVE, and what
this script reproduces step by step:
  1. build_d_ts.py wrote 0.orig/, constant/, system/, CASE.txt.
  2. blockMesh ran in the case dir (`blockMesh > log.blockMesh 2>&1`) and
     wrote constant/polyMesh (points at 16 significant digits; no timestamp
     in the header, so the files are reproducible byte for byte).
  3. 0/ was created as a byte copy of 0.orig/ (cmp confirms all four fields
     identical).
  4. launch_dts.sh (guards G1 LAUNCH_LOCK, G2 no process with cwd in the case,
     G3 no time dir other than 0) detached run_one_dts.sh, which re-runs
     checkMesh > log.checkMesh, runs buoyantBoussinesqSimpleFoam > log.solve,
     and writes STATUS.<case> "rc= wall= checkMesh_rc=".
Here step 2 is followed by the mesh read and the rewrite of 0.orig/U (and a
build-time checkMesh > log.checkMesh, which step 4 overwrites), THEN step 3.

Idempotent: a case that already holds a solution time directory is not
rebuilt (same rule as build_d_ts.py).  A case dir with a live process in it
is never removed.

`python3 build_d_ts_p.py`           build whatever is missing, then verify all
`python3 build_d_ts_p.py --verify`  verify only (no build, nothing written)

Verification (exit 1 on any failure; NOTHING is launched by this script):
  (a) constant/polyMesh/{points,faces,owner,neighbour,boundary} byte-identical
      (cmp) to the slug case's;
  (b) uniform radial spacing from the points (sorted unique y at x = 0,
      constant differences to 1e-12 relative), nr + 1 radial and nx + 1 axial
      point levels;
  (c) cell count from log.checkMesh = nr x nx;
  (d) R_wall = 0.00999048 (cos 2.5 deg x 0.01) to 1e-9;
  (e) 0/U and 0.orig/U re-read from disk: discrete flow rate == U_b A_inlet to
      1e-12 relative; the centreline-most face value within 1e-6 relative of
      s 2 U_b (1 - (r_c/R_wall)^2);
  (f) diff -r against the slug case (excluding log.*, LAUNCH_LOCK, polyMesh,
      time dirs, CASE.txt): the ONLY differing files are 0.orig/U and 0/U.

DIAGNOSTIC, NOT GRADED.  No band, cannot pass or fail, no T1c verdict moves.
"""
import math
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_t1c as B                                    # noqa: E402
import analyse_t1c as T1C                                # noqa: E402  (read-only)
import analyse_dts as DTS                                # noqa: E402  (mesh reader)

NU_TS = 3.6567934
R_WALL_EXPECTED = 0.00999048          # R cos(2.5 deg), as the mesh writes it
LADDERS = [("D_Ts_Re25_P", 25.0, "D_Ts_Re25_{lvl}"),
           ("L_Ts_P", 100.0, "L_Ts_{lvl}")]
CASES = [(f"{tag}_{lvl}", tag, Re, slug.format(lvl=lvl), lvl)
         for tag, Re, slug in LADDERS for lvl in ("c", "m", "f")]


def case_dir(name):
    return os.path.join(HERE, name)


def has_solution(d):
    return os.path.isdir(d) and any(
        re.fullmatch(r"\d+(\.\d+)?", n) and float(n) != 0.0
        for n in os.listdir(d))


def live_process_in(d):
    for p in os.listdir("/proc"):
        if not p.isdigit():
            continue
        try:
            if os.readlink(f"/proc/{p}/cwd") == d:
                return int(p)
        except OSError:
            pass
    return None


# ---------------------------------------------------------------------------
# inlet geometry from the mesh
# ---------------------------------------------------------------------------
def inlet_faces(d):
    """(area, r_centroid, centroid) per inlet face, in PATCH FACE ORDER, plus
    R_wall = max y over all points (analyse_t1c.wall_radius rule)."""
    pm = os.path.join(d, "constant", "polyMesh")
    pts = DTS.read_points(os.path.join(pm, "points"))
    faces = DTS.read_faces(os.path.join(pm, "faces"))
    bnd = DTS.read_boundary(os.path.join(pm, "boundary"))
    s, n = bnd["inlet"]["startFace"], bnd["inlet"]["nFaces"]
    out = []
    for f in range(s, s + n):
        area, nrm, cf = DTS.face_geometry(pts, faces[f])
        if abs(-1.0 - nrm[0]) > 1e-9:
            raise RuntimeError(f"{d}: inlet face {f} normal {nrm} is not -x")
        out.append((area, math.hypot(cf[1], cf[2]), cf))
    R_wall = max(p[1] for p in pts)
    return out, R_wall, pts


def parabolic_inlet(geom, R_wall, Ub):
    """Values in patch face order and the flow-rate-exact scale s."""
    shape = [2.0 * (1.0 - (r / R_wall) ** 2) for _, r, _ in geom]
    A = [a for a, _, _ in geom]
    s = sum(A) / sum(sh * a for sh, a in zip(shape, A))
    ux = [s * Ub * sh for sh in shape]
    return ux, s


def inlet_entry(ux):
    body = "\n".join(f"        ({ux_f!r} 0 0)" for ux_f in ux)
    return (f"    inlet   {{ type fixedValue; value nonuniform List<vector> "
            f"{len(ux)}\n    (\n{body}\n    ); }}")


def rewrite_U(path, ux):
    txt = open(path).read()
    lines = txt.split("\n")
    hits = [i for i, ln in enumerate(lines) if ln.startswith("    inlet ")]
    if len(hits) != 1:
        raise RuntimeError(f"{path}: expected exactly one inlet line, "
                           f"found {len(hits)}")
    lines[hits[0]] = inlet_entry(ux)
    open(path, "w").write("\n".join(lines))


def read_inlet_list(path):
    txt = open(path).read()
    m = re.search(r"inlet\s*\{\s*type\s+fixedValue;\s*value\s+nonuniform\s+"
                  r"List<vector>\s*(\d+)\s*\((.*?)\)\s*;\s*\}", txt, re.S)
    if not m:
        raise RuntimeError(f"{path}: no nonuniform inlet list")
    n = int(m.group(1))
    vals = [tuple(float(x) for x in v.split())
            for v in re.findall(r"\(([^()]*)\)", m.group(2))]
    if len(vals) != n:
        raise RuntimeError(f"{path}: inlet list declares {n}, holds {len(vals)}")
    return vals


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------
def build_one(name, tag, Re, slug, lvl):
    d = case_dir(name)
    nr, nx = B.LEVELS[lvl]
    if has_solution(d):
        print(f"  {name}: has a solution on disk, NOT rebuilt")
        return None
    if os.path.isdir(d):
        pid = live_process_in(d)
        if pid is not None:
            raise RuntimeError(f"{name}: pid {pid} is running in the case dir; "
                               "refusing to touch it")
        shutil.rmtree(d)
    for sub in ("0.orig", "constant", "system"):
        os.makedirs(os.path.join(d, sub))
    w = lambda rel, txt: open(os.path.join(d, rel), "w").write(txt)

    # Re (and the U_b it implies) applied exactly as build_d_ts.py does, by
    # temporarily setting the module globals the frozen generators read.
    old_re, old_u = B.RE, B.U
    B.RE = Re
    B.U = Re * B.NU / B.D
    Ub = B.U
    try:
        w("system/blockMeshDict", B.block_mesh(nr, nx))
        w("system/controlDict", B.control_dict())
        w("system/fvSchemes", B.fv_schemes())
        w("system/fvSolution", B.fv_solution())
        w("constant/transportProperties", B.transport())
        w("constant/turbulenceProperties", B.turbulence_properties())
        w("constant/g", B.gravity())
        w("0.orig/U", B.field_U())
        w("0.orig/p_rgh", B.field_p())
        w("0.orig/T", B.field_T("fixedTemperature"))
        w("0.orig/alphat", B.field_alphat())
        txt = B.case_txt(name, dict(level=lvl, nr=nr, nx=nx,
                                    wall="fixedTemperature"))
    finally:
        B.RE, B.U = old_re, old_u

    # step 2 of the chain: blockMesh in the case dir
    r = T1C.foam(d, "blockMesh > log.blockMesh 2>&1")
    if r.returncode != 0:
        raise RuntimeError(f"{name}: blockMesh rc={r.returncode}")

    # the lever: Poiseuille at the mesh's own inlet face centroids
    geom, R_wall, _ = inlet_faces(d)
    if len(geom) != nr:
        raise RuntimeError(f"{name}: {len(geom)} inlet faces, expected {nr}")
    ux, s = parabolic_inlet(geom, R_wall, Ub)
    rewrite_U(os.path.join(d, "0.orig", "U"), ux)

    # build-time checkMesh (run_one_dts.sh re-runs it at launch)
    r = T1C.foam(d, "checkMesh > log.checkMesh 2>&1")
    if r.returncode != 0:
        raise RuntimeError(f"{name}: checkMesh rc={r.returncode}")

    # step 3 of the chain: 0/ is a byte copy of 0.orig/
    shutil.copytree(os.path.join(d, "0.orig"), os.path.join(d, "0"))

    st, lo, hi = T1C.amended_station(Re, B.PR, NU_TS)
    pe = Re * B.PR
    txt += (f"diagnostic       yes -- parabolic-inlet replicate of {slug}, "
            f"NOT GRADED\n"
            f"ladder_for       {tag}\n"
            f"changed_from     {slug} (inlet U: uniform slug -> Poiseuille "
            f"2 U_b (1 - (r/R_wall)^2) at face centroids, flow-rate-exact "
            f"scale s = {s!r}; nothing else)\n"
            f"inlet_profile    parabolic (fixedValue nonuniform list from "
            f"polyMesh inlet face centroids; R_wall = {R_wall!r})\n"
            f"station_rule     analyse_t1c.amended_station "
            f"(moves with Re; NOT 40 D)\n"
            f"station_xD       {st:.4f}  (window [{lo:.4f}, {hi:.4f}])\n"
            f"Peclet           {pe:.2f}\n")
    w("CASE.txt", txt)
    rc = min(geom, key=lambda g: g[1])
    print(f"  {name:14s} {nr:3d} x {nx:3d}  Re {Re:4.0f}  U_b {Ub:.6g}  "
          f"R_wall {R_wall!r}  s = {s!r}  (s - 1 = {s-1:+.3e})  "
          f"u_x(centreline face, r = {rc[1]:.4e}) = {ux[geom.index(rc)]:.10g}"
          f"  = {ux[geom.index(rc)]/Ub:.6f} U_b;  station x/D = {st:.4f}")
    return s


# ---------------------------------------------------------------------------
# verification
# ---------------------------------------------------------------------------
def verify_one(name, tag, Re, slug, lvl):
    d, sd = case_dir(name), case_dir(slug)
    nr, nx = B.LEVELS[lvl]
    Ub = Re * B.NU / B.D
    ok = True

    def chk(cond, msg):
        nonlocal ok
        ok &= bool(cond)
        print(f"    [{'ok  ' if cond else 'FAIL'}] {msg}")

    print(f"\n  {name}  (replicate of {slug}; {nr} x {nx})")
    # (a) mesh files byte-identical to the slug case
    for f in ("points", "faces", "owner", "neighbour", "boundary"):
        r = subprocess.run(["cmp", os.path.join(d, "constant/polyMesh", f),
                            os.path.join(sd, "constant/polyMesh", f)],
                           capture_output=True, text=True)
        chk(r.returncode == 0,
            f"(a) polyMesh/{f} cmp vs {slug}: "
            f"{'identical' if r.returncode == 0 else r.stdout.strip() or r.stderr.strip()}")

    # (b) uniform radial spacing and counts from the points
    geom, R_wall, pts = inlet_faces(d)
    ys = sorted(set(p[1] for p in pts if p[0] == 0.0))
    xs = sorted(set(round(p[0], 12) for p in pts))
    dy = [b - a for a, b in zip(ys, ys[1:])]
    mean = sum(dy) / len(dy)
    spread = (max(dy) - min(dy)) / mean
    chk(len(ys) == nr + 1, f"(b) {len(ys)} radial point levels at x = 0 "
                           f"-> {len(ys)-1} radial cells (expect {nr})")
    chk(len(xs) == nx + 1, f"(b) {len(xs)} axial point levels "
                           f"-> {len(xs)-1} axial cells (expect {nx})")
    chk(spread <= 1e-12, f"(b) radial spacing dy = {mean:.12e}, "
                         f"(max - min)/mean = {spread:.2e} (<= 1e-12)")
    chk(abs(mean * nr - R_wall) <= 1e-12 * R_wall,
        f"(b) nr dy = {mean*nr!r} vs R_wall {R_wall!r}")

    # (c) cell count from log.checkMesh
    cm = os.path.join(d, "log.checkMesh")
    m = re.search(r"^\s*cells:\s+(\d+)", open(cm).read(), re.M) \
        if os.path.isfile(cm) else None
    cells = int(m.group(1)) if m else None
    chk(cells == nr * nx, f"(c) log.checkMesh cells = {cells} (expect {nr*nx})")
    ok_line = re.search(r"^Mesh OK\.", open(cm).read(), re.M) \
        if os.path.isfile(cm) else None
    chk(ok_line is not None, "(c) log.checkMesh says 'Mesh OK.'")

    # (d) R_wall = R cos(2.5 deg).  The mesh carries the blockMeshDict vertex
    # 0.0099904822 (10 decimals), 1.6e-11 from the exact 0.01 cos(2.5 deg);
    # the 6-significant-figure quotation 0.00999048 is that number truncated
    # and sits 2.2e-9 away, so the definition is what is checked to 1e-9 and
    # the truncated quotation is reported beside it.
    R_exact = B.R * math.cos(math.radians(B.WEDGE_DEG / 2.0))
    chk(abs(R_wall - R_exact) <= 1e-9,
        f"(d) R_wall = {R_wall!r} vs R cos(2.5 deg) = {R_exact:.13f}: diff "
        f"{R_wall-R_exact:+.2e} (<= 1e-9)   [6-s.f. quotation "
        f"{R_WALL_EXPECTED}: diff {R_wall-R_WALL_EXPECTED:+.2e}, the truncation]")

    # (e) the inlet list, re-read from disk
    A = [a for a, _, _ in geom]
    A_in = sum(A)
    shape = [2.0 * (1.0 - (r / R_wall) ** 2) for _, r, _ in geom]
    s = A_in / sum(sh * a for sh, a in zip(shape, A))
    icl = min(range(len(geom)), key=lambda i: geom[i][1])
    s_txt = T1C.case_txt(d, "changed_from")
    ms = re.search(r"scale s = ([-0-9.eE+]+)", s_txt)
    chk(ms is not None and float(ms.group(1)) == s,
        f"(e) CASE.txt records s = {ms.group(1) if ms else None}; "
        f"recomputed from the mesh s = {s!r}")
    for sub in ("0.orig", "0"):
        path = os.path.join(d, sub, "U")
        vals = read_inlet_list(path)
        chk(len(vals) == nr, f"(e) {sub}/U inlet list has {len(vals)} entries "
                             f"(expect {nr})")
        chk(all(v[1] == 0.0 and v[2] == 0.0 for v in vals),
            f"(e) {sub}/U inlet list: u_y = u_z = 0 on every face")
        Q = sum(v[0] * a for v, a in zip(vals, A))
        rel = (Q - Ub * A_in) / (Ub * A_in)
        chk(abs(rel) <= 1e-12,
            f"(e) {sub}/U discrete flow rate {Q!r} vs U_b A_inlet "
            f"{Ub*A_in!r}: rel {rel:+.2e} (<= 1e-12)")
        want = s * 2.0 * Ub * (1.0 - (geom[icl][1] / R_wall) ** 2)
        relc = (vals[icl][0] - want) / want
        chk(abs(relc) <= 1e-6,
            f"(e) {sub}/U centreline-most face (r_c = {geom[icl][1]:.6e}) "
            f"u_x = {vals[icl][0]!r} vs s 2 U_b (1 - (r_c/R_wall)^2) = "
            f"{want!r}: rel {relc:+.2e} (<= 1e-6); u_x/U_b = {vals[icl][0]/Ub:.6f}")
        worst = max(abs((v[0] - s * Ub * sh) / (s * Ub * sh))
                    for v, sh in zip(vals, shape))
        chk(worst <= 1e-12,
            f"(e) {sub}/U every face within {worst:.1e} relative of the "
            f"scaled parabola at its centroid")
    r = subprocess.run(["cmp", os.path.join(d, "0.orig", "U"),
                        os.path.join(d, "0", "U")], capture_output=True)
    chk(r.returncode == 0, "(e) 0/U byte-identical to 0.orig/U")

    # (f) diff -r against the slug case
    r = subprocess.run(["diff", "-rq", "-x", "log.*", "-x", "LAUNCH_LOCK",
                        "-x", "polyMesh", "-x", "CASE.txt", "-x", "[0-9]*[0-9]",
                        d, sd], capture_output=True, text=True)
    # the time-dir exclusion above would also hide "0"; list 0 explicitly
    r0 = subprocess.run(["diff", "-rq", os.path.join(d, "0"),
                         os.path.join(sd, "0")], capture_output=True, text=True)
    r0o = subprocess.run(["diff", "-rq", os.path.join(d, "0.orig"),
                          os.path.join(sd, "0.orig")],
                         capture_output=True, text=True)
    diffs = []
    for rr in (r, r0, r0o):
        for ln in rr.stdout.splitlines():
            if ln.startswith("Files "):
                f = ln.split()[1]
                diffs.append(os.path.relpath(f, d))
            elif ln.startswith("Only in"):
                # the slug case holds its solution, lock and logs; the new
                # case must hold nothing the slug lacks (except what the
                # exclusions already hid)
                diffs.append(ln)
    diffs = sorted(set(diffs))
    only_in_new = [x for x in diffs if x.startswith("Only in " + d)]
    only_in_slug = [x for x in diffs if x.startswith("Only in " + sd)]
    changed = [x for x in diffs if not x.startswith("Only in")]
    chk(sorted(changed) == ["0.orig/U", "0/U"],
        f"(f) diff -r vs {slug} (excl. log.*, LAUNCH_LOCK, polyMesh, time dirs,"
        f" CASE.txt): differing files = {changed}")
    chk(not only_in_new, f"(f) files only in {name}: {only_in_new}")
    if only_in_slug:
        print(f"           (only in {slug}, expected: "
              f"{[x.split(': ')[-1] for x in only_in_slug]})")
    # and the U files differ ONLY in the inlet entry
    for sub in ("0.orig", "0"):
        a = open(os.path.join(d, sub, "U")).read().split("\n")
        b = open(os.path.join(sd, sub, "U")).read().split("\n")
        ia = [i for i, ln in enumerate(a) if ln.startswith("    inlet ")][0]
        ib = [i for i, ln in enumerate(b) if ln.startswith("    inlet ")][0]
        ja = [i for i, ln in enumerate(a) if ln.startswith("    outlet ")][0]
        jb = [i for i, ln in enumerate(b) if ln.startswith("    outlet ")][0]
        chk(a[:ia] == b[:ib] and a[ja:] == b[jb:],
            f"(f) {sub}/U: header, dimensions, internalField and the outlet/"
            f"wall/front/back entries are byte-identical to {slug}'s; only "
            f"the inlet entry differs")
    chk(not has_solution(d), "(pre-launch) no solution time dir present")
    chk(not os.path.isdir(os.path.join(d, "LAUNCH_LOCK")) or True,
        f"(pre-launch) LAUNCH_LOCK present: "
        f"{os.path.isdir(os.path.join(d, 'LAUNCH_LOCK'))}")
    return ok, s


def main(argv):
    verify_only = "--verify" in argv
    if not verify_only:
        print(f"BUILD parabolic-inlet ladders in {HERE}")
        for name, tag, Re, slug, lvl in CASES:
            build_one(name, tag, Re, slug, lvl)
    print("\nVERIFY every mesh and inlet list from disk (nothing is launched "
          "here)")
    all_ok = True
    svals = {}
    for name, tag, Re, slug, lvl in CASES:
        if not os.path.isdir(case_dir(name)):
            print(f"  {name}: MISSING")
            all_ok = False
            continue
        ok, s = verify_one(name, tag, Re, slug, lvl)
        svals[name] = s
        all_ok &= ok
    print("\n  flow-rate-exact scale s per case:")
    for name, s in svals.items():
        print(f"    {name:14s} s = {s!r}   (s - 1 = {s-1:+.6e})")
    print(f"\nVERIFICATION {'PASSED' if all_ok else 'FAILED'} for "
          f"{len(svals)} of {len(CASES)} cases"
          + ("" if all_ok else " -- DO NOT LAUNCH"))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
