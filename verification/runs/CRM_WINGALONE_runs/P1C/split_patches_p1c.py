#!/usr/bin/env python3
"""ARM P1C -- the wing assertion measures the quantity §2 REGISTERS.

Registered in ADDENDUM 2, committed 122398334 at 2026-09-12T03:23:42Z, BEFORE this ran.

WHAT CHANGED AND WHAT DID NOT.  §2 clause 3: "every `wing` face centre must lie within
|r| <= 4.3 mesh-units OF THE BODY AXIS and every `farfield` face centre beyond |r| >= 80".
P1/P1B computed distance from the ORIGIN for BOTH clauses.  Right for farfield, WRONG for
wing: on a 30-deg-swept planform the two diverge at the tip trailing edge.

  * WING assertion  -> sqrt(y^2 + z^2), distance from the BODY AXIS.  Threshold 4.3 UNMOVED.
  * FARFIELD assertion -> |r| from the origin, >= 80.  UNCHANGED, quantity and threshold.
  * classify() -> IMPORTED FROM P1B AND NOT REDEFINED.  Its r > 40.0 origin-distance split
    is correct (max wing 4.9810 vs min farfield 80.4423, 16.1x, nothing between).  Body-axis
    distance must NEVER classify: min farfield body-axis distance is 0.9015, so it does not
    separate the patches at all.

NO THRESHOLD IS MOVED BY THIS FILE.  WING_R_MAX and FARFIELD_R_MIN are imported, not restated.
"""
import sys, os, re, math
P1B = "/home/ubuntu/Certonomous/verification/runs/CRM_WINGALONE_runs/P1B"
sys.path.insert(0, P1B)
import split_patches_p1b as M          # classify(), body(), planted_control(), thresholds

def body_axis_r(c):
    """Distance from the BODY AXIS (the x-axis) -- the quantity §2 registers for wing."""
    return math.sqrt(c[1] * c[1] + c[2] * c[2])

def load(pm):
    txt = open(os.path.join(pm, "boundary")).read()
    m = re.search(r"defaultFaces\s*\{[^}]*?nFaces\s+(\d+);[^}]*?startFace\s+(\d+);", txt, re.S)
    nb, start = int(m.group(1)), int(m.group(2))
    flines, fs = M.body(os.path.join(pm, "faces"))
    plines, ps = M.body(os.path.join(pm, "points"))
    faces, need = [], set()
    for k in range(nb):
        pl = [int(x) for x in re.findall(r"\d+", flines[fs + 1 + start + k])][1:]
        faces.append(pl); need.update(pl)
    coords = {}
    for idx in need:
        v = re.findall(r"[-+0-9.eE]+", plines[ps + 1 + idx])
        coords[idx] = (float(v[0]), float(v[1]), float(v[2]))
    return faces, coords, nb, start

def main():
    pm = sys.argv[1]
    faces, coords, nb, start = load(pm)
    print("BOUNDARY defaultFaces nFaces=%d startFace=%d" % (nb, start))
    cls, wing_axis_r, ff_orig_r = {}, [], []
    order = []
    for pl in faces:
        name, r = M.classify(pl, coords)
        cls[name] = cls.get(name, 0) + 1
        order.append(name)
        pts = [coords[i] for i in pl]; n = len(pts)
        c = (sum(p[0] for p in pts)/n, sum(p[1] for p in pts)/n, sum(p[2] for p in pts)/n)
        if name == "wing":     wing_axis_r.append(body_axis_r(c))
        elif name == "farfield": ff_orig_r.append(r)

    print("\nPREDICTED (ADDENDUM 2 A2.4, registered before this ran) vs ACHIEVED")
    pred = {"wing": 11136, "farfield": 11136, "symmetry": 14144}
    counts_ok = True
    for k in ("wing", "farfield", "symmetry"):
        got = cls.get(k, 0); ok = (got == pred[k]); counts_ok &= ok
        print("  %-9s predicted %6d   achieved %6d   %s" % (k, pred[k], got, "MATCH" if ok else "MISMATCH"))

    wmax = max(wing_axis_r); fmin = min(ff_orig_r)
    g1 = wmax <= M.WING_R_MAX
    g2 = fmin >= M.FARFIELD_R_MIN
    print("\nGEOMETRIC ASSERTION -- IN THE QUANTITIES §2 REGISTERS")
    print("  max wing face-centre distance from the BODY AXIS = %9.4f   gate <= %.1f  -> %s"
          % (wmax, M.WING_R_MAX, "PASS" if g1 else "FAIL"))
    print("  min farfield face-centre |r| from the ORIGIN      = %9.4f   gate >= %.1f  -> %s"
          % (fmin, M.FARFIELD_R_MIN, "PASS" if g2 else "FAIL"))

    print("\nPLANTED CONTROL (rule 3) -- BOTH ARMS, because a control that cannot fail is not one")
    okp, lines = M.planted_control(faces, coords, apply_plant=True)
    for l in lines: print("   " + l)
    print("   POSITIVE ARM (plant applied, must detect): %s" % ("PASS" if okp else "FAIL"))
    okn, lines = M.planted_control(faces, coords, apply_plant=False)
    for l in lines: print("   " + l)
    print("   NEGATIVE ARM (plant withheld, must NOT detect): %s" % ("PASS" if okn else "FAIL"))

    verdict = counts_ok and g1 and g2 and okp and okn
    print("\nP1C %s" % ("PASS" if verdict else "GATE FAIL"))
    if not verdict:
        print("  REPORTED, NOT ADJUSTED.")
    return 0 if verdict else 1

if __name__ == "__main__":
    sys.exit(main())
