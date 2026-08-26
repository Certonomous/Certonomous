#!/usr/bin/env python3
"""check_t5_mesh.py -- reads every polyMesh/points file STREAMED and REFUSES before
any solver runs (prereg S5.4, S15).  Nothing here trusts build_t5.py's inputs: every
geometric constant below is READ BACK from the points on disk (T1c's 9 % D/2 error;
L-142's 210x-too-thick wall cell quoted as correct by every link of a build chain).

CONTRACT (T5_PREREGISTRATION.md @ 0fcbb92e):
  geometry     air region spans x/H [-8, 20], y/H [0, 3.4], z/H [0, 5] (S5.2);
               epoxy region lies inside the cube x/H [0, 1], y/H [0, 1], z/H [0, 0.5]
  first layer  the fluid cell touching the cube front face (x -> 0-), top face
               (y -> H+), side face (z -> H/2+), the floor (y -> 0+) and the roof
               (y -> 3.4H-) has thickness = registered first layer for the level
               (0.128 / 0.080 / 0.050 mm, S5.4) within FIRST_TOL
  grading      cell thickness grows MONOTONICALLY away from each of those walls
               over the first 4 cells -- an INVERTED grading REFUSES, and the
               selftest PLANTS one and requires the refusal to FIRE (S5.4)
  interface    every cube_* patch has the same face count in both regions, and the
               epoxy region has patch `core` with nFaces > 0
  shell        the epoxy shell thickness read from the epoxy points = 1.5 mm
No `assert` carries any of this (L-332); refusals are sys.exit(2), driven under
`python3 -O` in --selftest.  Memory: distinct coordinate values only, never a
point array; run under `ulimit -v 4000000`.
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile

H, DELTA = 0.015, 0.0015
FIRST = {"c": 0.128e-3, "m": 0.080e-3, "f": 0.050e-3}
FIRST_TOL = 0.05          # relative
GEOM_TOL = 1e-6           # m
QUANT = 1e-9              # coordinate quantum for the distinct-value sets
CUBE_FACES = ("cube_front", "cube_top", "cube_rear", "cube_side_n")


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def stream_distinct(points_path):
    """Distinct x, y, z values of an ascii OpenFOAM points file, streamed."""
    xs, ys, zs = set(), set(), set()
    n = 0
    pat = re.compile(r"^\(\s*([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s*\)\s*$")
    with open(points_path, errors="replace") as fh:
        for line in fh:
            m = pat.match(line)
            if not m:
                continue
            n += 1
            xs.add(round(float(m.group(1)) / QUANT) * QUANT)
            ys.add(round(float(m.group(2)) / QUANT) * QUANT)
            zs.add(round(float(m.group(3)) / QUANT) * QUANT)
    if n == 0:
        refuse("%s: no points parsed (binary or empty?)" % points_path)
    return sorted(xs), sorted(ys), sorted(zs), n


def spacings_from(vals, wall, direction, count=4):
    """Cell thicknesses walking away from `wall` in `direction` (+1/-1)."""
    idx = min(range(len(vals)), key=lambda i: abs(vals[i] - wall))
    if abs(vals[idx] - wall) > GEOM_TOL:
        refuse("no grid plane at wall coordinate %.6g (nearest %.6g)" % (wall, vals[idx]))
    out = []
    i = idx
    while len(out) < count and 0 <= i + direction < len(vals):
        out.append(abs(vals[i + direction] - vals[i]))
        i += direction
    return out


def check_wall(name, vals, wall, direction, first):
    sp = spacings_from(vals, wall, direction)
    if not sp:
        refuse("%s: no cells beyond the wall plane" % name)
    if abs(sp[0] - first) / first > FIRST_TOL:
        refuse("%s: first layer %.4g m, registered %.4g m (tol %.0f %%)" % (name, sp[0], first, 100 * FIRST_TOL))
    for a, b in zip(sp, sp[1:]):
        if b < a * (1 - 1e-6):
            refuse("%s: INVERTED grading -- spacing %.4g then %.4g walking away from the wall (%s)"
                   % (name, a, b, ", ".join("%.4g" % s for s in sp)))
    return sp


def patch_faces(boundary_path):
    txt = open(boundary_path).read()
    out = {}
    for m in re.finditer(r"^\s*([A-Za-z_][\w]*)\s*\{\s*(.*?)\}", txt, re.S | re.M):
        nm = m.group(1)
        f = re.search(r"nFaces\s+(\d+)\s*;", m.group(2))
        if f:
            out[nm] = int(f.group(1))
    return out


def check_case(case, verbose=True):
    ct = os.path.join(case, "CASE.txt")
    if not os.path.isfile(ct):
        refuse("%s: no CASE.txt (not built by build_t5.py)" % case)
    kv = dict(l.strip().split("=", 1) for l in open(ct) if "=" in l)
    if kv.get("case") == "X_2d":
        xs, ys, zs, n = stream_distinct(os.path.join(case, "constant/polyMesh/points"))
        first = float(kv["first_layer_m"])
        check_wall("floor", ys, 0.0, +1, first)
        check_wall("roof", ys, 3.4 * H, -1, first)
        if abs(ys[-1] - 3.4 * H) > GEOM_TOL or abs(xs[-1] - float(kv["length_m"])) > GEOM_TOL:
            refuse("X_2d extent wrong: y_max %.6g x_max %.6g" % (ys[-1], xs[-1]))
        if verbose:
            print("%s: X_2d OK -- %d points, %d x-planes, %d y-planes, floor first layer %.4g m"
                  % (os.path.basename(case), n, len(xs), len(ys), spacings_from(ys, 0.0, +1)[0]))
        return
    lvl = kv.get("level")
    if lvl not in FIRST:
        refuse("%s: CASE.txt level '%s' not one of c/m/f" % (case, lvl))
    first = FIRST[lvl]
    axs, ays, azs, na = stream_distinct(os.path.join(case, "constant/air/polyMesh/points"))
    ext = dict(x=(axs[0], axs[-1]), y=(ays[0], ays[-1]), z=(azs[0], azs[-1]))
    want = dict(x=(-8 * H, 20 * H), y=(0.0, 3.4 * H), z=(0.0, 5 * H))
    for k in ext:
        for got, exp in zip(ext[k], want[k]):
            if abs(got - exp) > GEOM_TOL:
                refuse("air extent %s: got %.6g expected %.6g" % (k, got, exp))
    res = {}
    res["cube_front"] = check_wall("cube_front(x->0-)", axs, 0.0, -1, first)
    res["cube_rear"] = check_wall("cube_rear(x->H+)", axs, H, +1, first)
    res["cube_top"] = check_wall("cube_top(y->H+)", ays, H, +1, first)
    res["cube_side_n"] = check_wall("cube_side_n(z->H/2+)", azs, 0.5 * H, +1, first)
    res["floor"] = check_wall("floor(y->0+)", ays, 0.0, +1, first)
    res["roof"] = check_wall("roof(y->3.4H-)", ays, 3.4 * H, -1, first)
    exs, eys, ezs, ne = stream_distinct(os.path.join(case, "constant/epoxy/polyMesh/points"))
    for nm, v, lo, hi in (("x", exs, 0.0, H), ("y", eys, 0.0, H), ("z", ezs, 0.0, 0.5 * H)):
        if abs(v[0] - lo) > GEOM_TOL or abs(v[-1] - hi) > GEOM_TOL:
            refuse("epoxy extent %s: [%.6g, %.6g] expected [%.6g, %.6g]" % (nm, v[0], v[-1], lo, hi))
    # shell thickness: the epoxy x-planes include 0 and DELTA
    if not any(abs(v - DELTA) < GEOM_TOL for v in exs):
        refuse("epoxy region has no grid plane at x = %.4g: shell thickness is not 1.5 mm" % DELTA)
    ba = patch_faces(os.path.join(case, "constant/air/polyMesh/boundary"))
    be = patch_faces(os.path.join(case, "constant/epoxy/polyMesh/boundary"))
    for f in CUBE_FACES:
        if f not in ba or f not in be:
            refuse("interface patch %s missing (air:%s epoxy:%s)" % (f, f in ba, f in be))
        if ba[f] != be[f]:
            refuse("interface patch %s: %d faces in air, %d in epoxy" % (f, ba[f], be[f]))
        if ba[f] == 0:
            refuse("interface patch %s has zero faces" % f)
    if be.get("core", 0) <= 0:
        refuse("epoxy region has no `core` patch faces: the Dirichlet inner surface is absent")
    if verbose:
        print("%s (level %s): OK -- air %d points (%d/%d/%d planes), epoxy %d points; first layers [m]: %s; "
              "interface faces %s; core faces %d"
              % (os.path.basename(case), lvl, na, len(axs), len(ays), len(azs), ne,
                 ", ".join("%s=%.4g" % (k, v[0]) for k, v in res.items()),
                 {f: ba[f] for f in CUBE_FACES}, be["core"]))


def _write_points(path, xs, ys, zs):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write("FoamFile { class vectorField; object points; }\n%d\n(\n" % (len(xs) * len(ys) * len(zs)))
        for z in zs:
            for y in ys:
                for x in xs:
                    fh.write("(%.9g %.9g %.9g)\n" % (x, y, z))
        fh.write(")\n")


def selftest():
    fails = []
    tmp = tempfile.mkdtemp(prefix="t5_meshchk_")
    case = os.path.join(tmp, "X_2d")
    os.makedirs(case)
    first = 0.05e-3
    # a compliant floor/roof grading: 0.05, 0.1, 0.2, 0.4 mm ... then uniform
    good = [0.0, first, 3 * first, 7 * first, 15 * first, 3.4 * H - 15 * first, 3.4 * H - 7 * first,
            3.4 * H - 3 * first, 3.4 * H - first, 3.4 * H]
    xs = [i * 0.01 for i in range(0, 121)]
    open(os.path.join(case, "CASE.txt"), "w").write("case=X_2d\nfirst_layer_m=%g\nlength_m=1.2\n" % first)
    _write_points(os.path.join(case, "constant/polyMesh/points"), xs, good, [0.0, 0.001])
    me = os.path.abspath(__file__)
    p = subprocess.run([sys.executable, me, "--case", case], capture_output=True, text=True)
    if p.returncode != 0:
        fails.append("compliant planted mesh refused: %s" % p.stderr.strip())
    # PLANTED POSITIVE: inverted grading at the floor (0.4, 0.2, 0.1, 0.05 mm) -- MUST FIRE
    bad = [0.0, 8 * first, 12 * first, 14 * first, 15 * first, 3.4 * H - 15 * first, 3.4 * H - 7 * first,
           3.4 * H - 3 * first, 3.4 * H - first, 3.4 * H]
    _write_points(os.path.join(case, "constant/polyMesh/points"), xs, bad, [0.0, 0.001])
    rcs = {}
    for tag, argv in (("python3", [sys.executable]), ("python3 -O", [sys.executable, "-O"])):
        q = subprocess.run(argv + [me, "--case", case], capture_output=True, text=True)
        rcs[tag] = (q.returncode, "first layer" in q.stderr or "INVERTED" in q.stderr)
    if not all(v[0] == 2 and v[1] for v in rcs.values()):
        fails.append("planted inverted grading did not FIRE under both interpreters: %r" % rcs)
    else:
        print("PLANTED-POSITIVE FIRED: inverted floor grading refused under python3 and python3 -O (rc 2).")
    # inverted beyond the first cell only (first layer right, second thinner) -- must also fire
    bad2 = [0.0, first, 1.5 * first, 1.7 * first, 15 * first, 3.4 * H - 15 * first, 3.4 * H - 7 * first,
            3.4 * H - 3 * first, 3.4 * H - first, 3.4 * H]
    _write_points(os.path.join(case, "constant/polyMesh/points"), xs, bad2, [0.0, 0.001])
    q = subprocess.run([sys.executable, "-O", me, "--case", case], capture_output=True, text=True)
    if not (q.returncode == 2 and "INVERTED" in q.stderr):
        fails.append("second-cell inversion did not fire: rc=%d %s" % (q.returncode, q.stderr[-200:]))
    # absent CASE.txt refuses
    os.unlink(os.path.join(case, "CASE.txt"))
    q = subprocess.run([sys.executable, "-O", me, "--case", case], capture_output=True, text=True)
    if q.returncode != 2:
        fails.append("missing CASE.txt did not refuse")
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    for f in fails:
        print("FAILED: " + f)
    print("SELFTEST %s: 4 arms, %d FAILED (%s)" % ("PASS" if not fails else "FAIL", len(fails),
                                                    "-O" if not __debug__ else "plain"))
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", action="append", default=[])
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.case:
        ap.print_help()
        return 0
    for c in a.case:
        check_case(os.path.abspath(c))
    return 0


if __name__ == "__main__":
    sys.exit(main())
