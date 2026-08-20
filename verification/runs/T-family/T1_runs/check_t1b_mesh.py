#!/usr/bin/env python3
"""
Verify every T1b mesh against the design it claims, BEFORE any solver runs.

This exists because T1b attempt 1 spent 57 core-hours on a mesh whose radial
grading ran the wrong way.  The builder printed the intended wall cell in its
own summary table and in every CASE.txt, and blockMesh accepted the dictionary
without complaint, so nothing in the chain disagreed with anything else.  The
mesh was only caught by reading the written points, which is what this does.

It asserts, per case, straight from constant/polyMesh/points:

  A. the cell touching the WALL has the height CASE.txt says it does
  B. that cell is the SMALLEST radial cell on a resolved or wall-function mesh
     (the axis cell is the largest) -- this is the specific inversion that
     attempt 1 failed
  C. the radial cells sum to the wall radius
  D. the cell-to-cell ratio matches the builder's, so the grading is geometric
     in the direction claimed

Tolerance on A and C is 0.2 %, which admits the wedge cos(theta/2) factor of
0.0952 % and nothing larger.
"""
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOL = 2.0e-3
CASES = ([f"R_{t}_{l}" for t in ("10k", "30k", "100k", "300k")
          for l in ("c", "m", "f")]
         + [f"P_{t}" for t in ("10k", "30k", "100k", "300k")]
         + ["W_100k", "W_300k", "C_lam"])


def radial_faces(case):
    p = os.path.join(HERE, case, "constant", "polyMesh", "points")
    ys = set()
    for line in open(p):
        m = re.fullmatch(r"\(([-\d.eE+]+) ([-\d.eE+]+) ([-\d.eE+]+)\)",
                         line.strip())
        if m:
            x, y, z = (float(v) for v in m.groups())
            if abs(x) < 1e-12 and z >= 0.0:
                ys.add(round(y, 12))
    return sorted(ys)


def case_field(case, key):
    for line in open(os.path.join(HERE, case, "CASE.txt")):
        if line.split() and line.split()[0] == key:
            return line.split()[1]
    return None


def check(case):
    ys = radial_faces(case)
    h = [ys[i + 1] - ys[i] for i in range(len(ys) - 1)]
    R = ys[-1]
    design = float(case_field(case, "first_cell"))
    ratio = float(case_field(case, "cell_ratio"))
    nr = int(case_field(case, "mesh").split()[0])
    bad = []

    if len(h) != nr:
        bad.append(f"{len(h)} radial cells, CASE.txt says {nr}")
    e = abs(h[-1] - design) / design
    if e > TOL:
        bad.append(f"wall cell {h[-1]:.6e} m vs designed {design:.6e} m "
                   f"({100*e:.3f} % off)")
    # B: THE INVERSION TEST
    if h[-1] > h[0]:
        bad.append(f"INVERTED: wall cell {h[-1]:.4e} m is LARGER than the axis "
                   f"cell {h[0]:.4e} m, by {h[-1]/h[0]:.1f}x")
    if h[-1] != min(h):
        bad.append(f"wall cell is not the smallest ({h[-1]:.4e} vs min "
                   f"{min(h):.4e})")
    s = abs(sum(h) - R) / R
    if s > TOL:
        bad.append(f"radial cells sum to {sum(h):.8f}, wall at {R:.8f}")
    if len(h) > 2:
        r = [h[i] / h[i + 1] for i in range(len(h) - 1)]
        rr = sum(r) / len(r)
        if abs(rr - ratio) / ratio > 1e-2:
            bad.append(f"mean cell ratio {rr:.6f} vs builder's {ratio:.6f}")
        if max(r) - min(r) > 1e-6 * rr:
            bad.append("grading is not geometric")
    return bad, dict(nr=len(h), wall=h[-1], axis=h[0], design=design,
                     span=h[0] / h[-1])


def main():
    env = "/usr/lib/openfoam/openfoam2606/etc/bashrc"
    fails = {}
    print(f"{'case':12s} {'nr':>4s} {'wall cell':>12s} {'designed':>12s} "
          f"{'axis/wall':>10s}")
    for c in CASES:
        d = os.path.join(HERE, c)
        if not os.path.isfile(os.path.join(d, "constant", "polyMesh",
                                           "points")):
            r = subprocess.run(["bash", "-lc",
                                f"source {env} >/dev/null 2>&1 && cd {d} && "
                                f"blockMesh > log.blockMesh 2>&1"])
            if r.returncode != 0:
                fails[c] = ["blockMesh failed"]
                print(f"{c:12s}  blockMesh FAILED")
                continue
        bad, m = check(c)
        print(f"{c:12s} {m['nr']:4d} {m['wall']:12.4e} {m['design']:12.4e} "
              f"{m['span']:10.1f}" + ("   <-- " + "; ".join(bad) if bad else ""))
        if bad:
            fails[c] = bad
    print()
    if fails:
        print(f"MESH CHECK FAILED for {len(fails)} of {len(CASES)} cases")
        return 1
    print(f"MESH CHECK PASSED for all {len(CASES)} cases: every wall cell is "
          f"the design value and the smallest in its mesh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
