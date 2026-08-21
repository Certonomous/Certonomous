#!/usr/bin/env python3
"""
Mesh verification for the four T1b fourth-level cases R_*_x, BEFORE any solver
runs, reusing check_t1b_mesh.check() unchanged.

check_t1b_mesh.py is frozen and lists the 19 attempt-2 cases; this file does
not edit it.  It imports check(), which reads each case's written
constant/polyMesh/points and asserts (A) the wall cell matches CASE.txt,
(B) the wall cell is the SMALLEST radial cell (the inversion attempt 1 failed,
L-142), (C) the radial cells sum to the wall radius and (D) the grading is
geometric at the builder's ratio.

On top of check() it reads each case's log.checkMesh (written by blockMesh +
checkMesh run from this file if absent) for the cell count, the max aspect
ratio, the non-orthogonality and skewness, and whether checkMesh said
"Mesh OK" or "Failed N mesh checks".  The aspect-ratio failure is EXPECTED on
every resolved T1b mesh (T1b_DESIGN.md 4a) and is recorded, not hidden: the
x level has a wall cell 1.6x thinner and an axial spacing 1.6x smaller than
the fine level, so its aspect ratio should be about the fine level's, not
1.6x it.  That near-constancy is what check (E) below asserts.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from check_t1b_mesh import check, case_field           # noqa: E402

CASES = [f"R_{t}_x" for t in ("10k", "30k", "100k", "300k")]
FINE = {f"R_{t}_x": f"R_{t}_f" for t in ("10k", "30k", "100k", "300k")}
ENV = "/usr/lib/openfoam/openfoam2606/etc/bashrc"


def foam(case_dir, cmd):
    return subprocess.run(["bash", "-lc",
                           f"source {ENV} >/dev/null 2>&1 && cd {case_dir} && {cmd}"])


def mesh_counts(case):
    """(radial, axial) from the CASE.txt line 'mesh  NR radial x NX axial'."""
    for line in open(os.path.join(HERE, case, "CASE.txt")):
        t = line.split()
        if t and t[0] == "mesh":
            return int(t[1]), int(t[4])
    return None, None


def read_checkmesh(case):
    p = os.path.join(HERE, case, "log.checkMesh")
    if not os.path.isfile(p):
        return None
    txt = open(p, errors="replace").read()
    out = dict(verdict=None, cells=None, aspect=None, nonortho=None,
               skew=None, failed=None)
    m = re.search(r"^\s*cells:\s+(\d+)", txt, re.M)
    out["cells"] = int(m.group(1)) if m else None
    m = re.search(r"Max aspect ratio\s*[:=]\s*([0-9.eE+-]+)", txt)
    out["aspect"] = float(m.group(1)) if m else None
    m = re.search(r"Mesh non-orthogonality Max:\s*([0-9.eE+-]+)", txt)
    out["nonortho"] = float(m.group(1)) if m else None
    m = re.search(r"Max skewness = ([0-9.eE+-]+)", txt)
    out["skew"] = float(m.group(1)) if m else None
    if re.search(r"^Mesh OK\.", txt, re.M):
        out["verdict"] = "Mesh OK"
    m = re.search(r"^Failed (\d+) mesh checks?\.", txt, re.M)
    if m:
        out["verdict"] = f"Failed {m.group(1)} mesh check(s)"
        out["failed"] = int(m.group(1))
    return out


def main():
    fails = {}
    rows = []
    for c in CASES:
        d = os.path.join(HERE, c)
        if not os.path.isdir(d):
            fails[c] = ["case directory does not exist (not built)"]
            continue
        if not os.path.isfile(os.path.join(d, "constant", "polyMesh", "points")):
            r = foam(d, "blockMesh > log.blockMesh 2>&1")
            if r.returncode != 0:
                fails[c] = ["blockMesh failed"]
                continue
        if not os.path.isfile(os.path.join(d, "log.checkMesh")):
            foam(d, "checkMesh > log.checkMesh 2>&1")
        bad, m = check(c)
        cm = read_checkmesh(c) or {}
        nr, nx = mesh_counts(c)
        if cm.get("cells") is not None and cm["cells"] != nr * nx:
            bad.append(f"checkMesh counts {cm['cells']} cells, CASE.txt says "
                       f"{nr} x {nx} = {nr * nx}")
        # E: aspect ratio approximately CONSTANT against the fine level
        fcm = read_checkmesh(FINE[c]) or {}
        ar_ratio = None
        if cm.get("aspect") and fcm.get("aspect"):
            ar_ratio = cm["aspect"] / fcm["aspect"]
            if not (0.8 <= ar_ratio <= 1.25):
                bad.append(f"aspect ratio {cm['aspect']:.0f} is {ar_ratio:.2f}x "
                           f"the fine level's {fcm['aspect']:.0f}; the ladder "
                           "is not uniform")
        if cm.get("nonortho") is not None and cm["nonortho"] > 1.0:
            bad.append(f"non-orthogonality {cm['nonortho']}")
        if cm.get("failed") and cm["failed"] > 1:
            bad.append(f"checkMesh failed {cm['failed']} checks, only the "
                       "aspect-ratio failure is admissible")
        rows.append((c, m, cm, ar_ratio, bad))
        if bad:
            fails[c] = bad

    print(f"{'case':10s} {'nr':>4s} {'cells':>7s} {'wall cell':>12s} "
          f"{'designed':>12s} {'off %':>7s} {'axis/wall':>10s} {'maxAR':>8s} "
          f"{'AR/fine':>8s} {'nonorth':>7s} {'skew':>6s}  checkMesh")
    for c, m, cm, arr, bad in rows:
        off = 100.0 * abs(m["wall"] - m["design"]) / m["design"]
        print(f"{c:10s} {m['nr']:4d} {cm.get('cells') or 0:7d} {m['wall']:12.6e} "
              f"{m['design']:12.6e} {off:7.3f} {m['span']:10.1f} "
              f"{cm.get('aspect') or float('nan'):8.0f} "
              f"{arr if arr else float('nan'):8.3f} "
              f"{cm.get('nonortho') if cm.get('nonortho') is not None else float('nan'):7.1f} "
              f"{cm.get('skew') or float('nan'):6.3f}  {cm.get('verdict')}"
              + ("   <-- " + "; ".join(bad) if bad else ""))
    print()
    if fails:
        print(f"MESH CHECK FAILED for {len(fails)} of {len(CASES)} x-level cases")
        for c in sorted(fails):
            for r in fails[c]:
                print(f"  {c}: {r}")
        return 1
    print(f"MESH CHECK PASSED for all {len(CASES)} x-level cases: every wall cell "
          "is the design value and the smallest in its mesh, and the aspect "
          "ratio is within 25 % of the fine level's")
    return 0


if __name__ == "__main__":
    sys.exit(main())
