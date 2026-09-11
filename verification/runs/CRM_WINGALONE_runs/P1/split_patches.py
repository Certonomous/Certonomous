#!/usr/bin/env python3
"""P1 — split L2's single `defaultFaces` patch into wing / farfield / symmetry.

GRADED, NOT ADJUSTED. The expected counts below are quoted from
CRM_WINGALONE_FLOW_PREREGISTRATION.md §2, which was committed BEFORE this ran. If the
achieved counts differ, this script REPORTS the difference and exits non-zero. It does
NOT adjust the prediction, and nothing here may be edited to make the numbers agree.

Includes a PLANTED CONTROL (rule 3): one face is deliberately relabelled and the
verifier must report the mismatch, or the clean result is refused.
"""
import sys, re, os

# --- REGISTERED IN ADVANCE (§2). Do not edit to fit an outcome. -------------
EXPECT = {"wing": 11136, "farfield": 11136, "symmetry": 14144}
EXPECT_TOTAL = 36416
WING_R_MAX = 4.3        # §2: every wing face centre within this radius
FARFIELD_R_MIN = 80.0   # §2: every farfield face centre beyond this radius
Y_SYMM_TOL = 1e-9       # a face lies IN the root plane only if every vertex does
# ---------------------------------------------------------------------------

def body(path):
    """Return (list_of_lines_after_the_opening_paren, count)."""
    with open(path) as f:
        lines = f.read().split("\n")
    for i, ln in enumerate(lines):
        if ln.strip() == "(" and i > 10:
            return lines, i
    raise SystemExit("REFUSE: no opening paren in %s" % path)

def main(pm):
    # ---- boundary: locate the single defaultFaces patch
    btxt = open(os.path.join(pm, "boundary")).read()
    m = re.search(r"defaultFaces\s*\{[^}]*?nFaces\s+(\d+);[^}]*?startFace\s+(\d+);", btxt, re.S)
    if not m:
        print("REFUSE: defaultFaces patch not found — this mesh is not in the state §2 recorded.")
        return 2
    nb, start = int(m.group(1)), int(m.group(2))
    print("BOUNDARY defaultFaces nFaces=%d startFace=%d" % (nb, start))
    if nb != EXPECT_TOTAL:
        print("REFUSE: nFaces %d != registered %d — the mesh changed since §2 was written." % (nb, EXPECT_TOTAL))
        return 2

    flines, fs = body(os.path.join(pm, "faces"))
    plines, ps = body(os.path.join(pm, "points"))

    # ---- points needed by the boundary faces only
    faces = []
    need = set()
    for k in range(nb):
        toks = [int(x) for x in re.findall(r"\d+", flines[fs + 1 + start + k])]
        pl = toks[1:]
        faces.append(pl); need.update(pl)
    coords = {}
    for idx in need:
        vals = re.findall(r"[-+0-9.eE]+", plines[ps + 1 + idx])
        coords[idx] = (float(vals[0]), float(vals[1]), float(vals[2]))

    def classify(pl):
        pts = [coords[i] for i in pl]
        if all(abs(p[1]) < Y_SYMM_TOL for p in pts):
            return "symmetry"
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        cz = sum(p[2] for p in pts) / len(pts)
        r = (cx * cx + cy * cy + cz * cz) ** 0.5
        return ("farfield", r) if r > 40.0 else ("wing", r)

    got = {"wing": 0, "farfield": 0, "symmetry": 0}
    wing_rmax, ff_rmin = 0.0, 1e18
    labels = []
    for pl in faces:
        c = classify(pl)
        if c == "symmetry":
            got["symmetry"] += 1; labels.append("symmetry"); continue
        name, r = c
        got[name] += 1; labels.append(name)
        if name == "wing":  wing_rmax = max(wing_rmax, r)
        else:               ff_rmin = min(ff_rmin, r)

    print("\nPREDICTED (registered before the run) vs ACHIEVED")
    ok = True
    for k in ("wing", "farfield", "symmetry"):
        good = got[k] == EXPECT[k]
        ok &= good
        print("  %-9s predicted %6d   achieved %6d   %s" % (k, EXPECT[k], got[k], "MATCH" if good else "*** MISMATCH ***"))
    print("  total     predicted %6d   achieved %6d" % (EXPECT_TOTAL, sum(got.values())))

    print("\nGEOMETRIC ASSERTION (counts can be right for the wrong reason)")
    g1 = wing_rmax <= WING_R_MAX
    g2 = ff_rmin >= FARFIELD_R_MIN
    print("  max wing face-centre |r|     = %9.4f   gate <= %.1f  -> %s" % (wing_rmax, WING_R_MAX, "PASS" if g1 else "FAIL"))
    print("  min farfield face-centre |r| = %9.4f   gate >= %.1f  -> %s" % (ff_rmin, FARFIELD_R_MIN, "PASS" if g2 else "FAIL"))
    ok &= g1 and g2

    # ---- PLANTED CONTROL (rule 3): relabel one face and require detection
    print("\nPLANTED CONTROL — one face deliberately relabelled")
    tampered = list(labels)
    victim = next(i for i, l in enumerate(tampered) if l == "farfield")
    tampered[victim] = "wing"
    tgot = {k: tampered.count(k) for k in EXPECT}
    detected = any(tgot[k] != EXPECT[k] for k in EXPECT)
    print("  face %d relabelled farfield -> wing; verifier reports %s"
          % (victim, "A MISMATCH" if detected else "NOTHING"))
    if not detected:
        print("  REFUSE: the verifier cannot see a known-bad labelling. Its clean result is NOT evidence.")
        return 2
    print("  CONTROL PASSED -> the comparison above is evidence, not a blind read.")

    print("\nP1 %s" % ("PASS" if ok else "GATE FAIL — reported, NOT adjusted"))
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
