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

def classify(pl, coords):
    """Class of one boundary face from its vertex COORDINATES."""
    pts = [coords[i] for i in pl]
    if all(abs(p[1]) < Y_SYMM_TOL for p in pts):
        return "symmetry", 0.0
    n = len(pts)
    cx = sum(p[0] for p in pts) / n
    cy = sum(p[1] for p in pts) / n
    cz = sum(p[2] for p in pts) / n
    r = (cx * cx + cy * cy + cz * cz) ** 0.5
    return ("farfield" if r > 40.0 else "wing"), r


def planted_control(faces, coords, apply_plant=True):
    """Rule 3. Move ONE face's vertices so it genuinely belongs to another class,
    RE-RUN classify() on it, and require the new class to be reported.

    apply_plant=False is the NEGATIVE ARM: the plant is deliberately NOT applied, so a
    sound control must report NO detection. A control that 'passes' with the plant
    withheld is a control that cannot fail, which is the defect this replaces."""
    out = []
    idx = None
    for i, pl in enumerate(faces):
        c, r = classify(pl, coords)
        if c == "farfield" and any(abs(coords[j][1]) > 1.0 for j in pl):
            idx = i
            break
    if idx is None:
        return False, ["no suitable farfield face found to plant into"]
    pl = faces[idx]
    before, r_before = classify(pl, coords)
    saved = {j: coords[j] for j in pl}
    if apply_plant:
        for j in pl:
            x, y, z = coords[j]
            coords[j] = (x * 0.02, y * 0.02, z * 0.02)   # |r| ~85 -> ~1.7: wing band
    after, r_after = classify(pl, coords)
    for j, c in saved.items():
        coords[j] = c
    restored, r_restored = classify(pl, coords)
    detected = (after != before)
    out.append("face %d: class before = %s (|r| %.3f)" % (idx, before, r_before))
    out.append("plant applied = %s -> class after = %s (|r| %.3f)" % (apply_plant, after, r_after))
    out.append("restored -> class = %s (|r| %.3f)%s"
               % (restored, r_restored, "" if restored == before else "  *** RESIDUE ***"))
    out.append("classifier responded to the input change: %s" % detected)
    return (detected and restored == before) if apply_plant else (not detected), out



def _write_synth(d):
    """Build a tiny synthetic polyMesh whose boundary has exactly the registered
    counts, so main() runs end to end and the SYMMETRY branch is proven live."""
    import os
    os.makedirs(d, exist_ok=True)
    nsym, nwing, nff = EXPECT["symmetry"], EXPECT["wing"], EXPECT["farfield"]
    start = 10
    pts, faces = [], []
    def quad(base, y, scale):
        o = len(pts)
        for dx, dz in ((0, 0), (1, 0), (1, 1), (0, 1)):
            pts.append((base + dx * 0.01, y, scale + dz * 0.01))
        return [o, o + 1, o + 2, o + 3]
    for _ in range(start):                       # dummy internal faces
        faces.append(quad(0.0, 0.5, 0.5))
    for _ in range(nsym):                        # y == 0 exactly -> symmetry
        faces.append(quad(1.0, 0.0, 1.0))
    for _ in range(nwing):                       # |r| ~1.7 -> wing (<= 4.3)
        faces.append(quad(1.0, 1.0, 1.0))
    for _ in range(nff):                         # |r| ~86 -> farfield (>= 80)
        faces.append(quad(50.0, 50.0, 50.0))
    hdr = "\n".join(["// synthetic"] * 12) + "\n%d\n(\n"
    with open(os.path.join(d, "points"), "w") as f:
        f.write(hdr % len(pts))
        for x, y, z in pts: f.write("(%.10f %.10f %.10f)\n" % (x, y, z))
        f.write(")\n")
    with open(os.path.join(d, "faces"), "w") as f:
        f.write(hdr % len(faces))
        for q in faces: f.write("4(%d %d %d %d)\n" % tuple(q))
        f.write(")\n")
    with open(os.path.join(d, "boundary"), "w") as f:
        f.write("FoamFile{}\n1\n(\n    defaultFaces\n    {\n        type wall;\n"
                "        nFaces %d;\n        startFace %d;\n    }\n)\n"
                % (nsym + nwing + nff, start))
    return d


def selftest_main():
    """Arm 4 — RUN main() END TO END on a synthetic mesh. Arms 1-3 exercise
    planted_control() only and CANNOT see a broken main(); this arm can."""
    import tempfile
    d = _write_synth(os.path.join(tempfile.gettempdir(), "p1_synth_polyMesh"))
    print("SELFTEST 4 — main() END TO END on a SYNTHETIC mesh (not the real one)")
    print("   built at %s with a KNOWN symmetry face set, so the symmetry branch is proven live" % d)
    rc = main(d)
    print("   -> main() rc=%d  (expected 0)" % rc)
    return rc


def selftest():
    """Exercise the control on synthetic geometry, INCLUDING its failure mode.
    Runs no mesh and is not P1."""
    coords = {0: (85.0, 40.0, 10.0), 1: (85.0, 41.0, 10.0),
              2: (86.0, 41.0, 10.0), 3: (86.0, 40.0, 10.0)}
    faces = [[0, 1, 2, 3]]
    print("SELFTEST 1 — plant APPLIED, sound classifier: control must PASS")
    ok, msg = planted_control(faces, dict(coords), apply_plant=True)
    for m in msg: print("   " + m)
    print("   -> %s  (expected PASS)" % ("PASS" if ok else "FAIL"))
    a = ok
    print("SELFTEST 2 — plant WITHHELD: a control that cannot fail would still say PASS")
    ok2, msg2 = planted_control(faces, dict(coords), apply_plant=False)
    for m in msg2: print("   " + m)
    print("   -> control reports no-detection = %s  (expected: no detection)" % ok2)
    print("SELFTEST 3 — THE CONTROL MUST BE ABLE TO FAIL: break the classifier's band")
    global FARFIELD_BAND_BROKEN
    import __main__ as M
    saved = M.classify
    M.classify = lambda pl, c: ("farfield", 99.0)          # a classifier that never changes its mind
    ok3, msg3 = planted_control(faces, dict(coords), apply_plant=True)
    M.classify = saved
    for m in msg3: print("   " + m)
    print("   -> %s  (expected FAIL — this is the control refusing)" % ("PASS" if ok3 else "FAIL"))
    good = a and ok2 and (not ok3)
    rc4 = selftest_main()
    good = good and rc4 == 0
    print("\nSELFTEST %s" % ("PASS — control detects a real plant, refuses a dead classifier, "
                              "AND main() runs end to end with all three branches live"
                              if good else "FAIL"))
    return 0 if good else 1


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

    got = {"wing": 0, "farfield": 0, "symmetry": 0}
    wing_rmax, ff_rmin = 0.0, 1e18
    labels = []
    for pl in faces:
        name, r = classify(pl, coords)      # classify takes coords; it ALWAYS returns a tuple
        got[name] += 1; labels.append(name)
        if name == "wing":       wing_rmax = max(wing_rmax, r)
        elif name == "farfield": ff_rmin = min(ff_rmin, r)

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

    # ---- PLANTED CONTROL (rule 3) — PLANTED IN THE INPUT, classify() RE-RUN
    # The previous version relabelled a copy of the OUTPUT list and counted it. That
    # tested arithmetic, never the classifier, and could not fail for any input.
    print("\nPLANTED CONTROL — perturb one face's COORDINATES and re-run classify()")
    ok_ctrl, msg = planted_control(faces, coords)
    for line in msg:
        print("  " + line)
    if not ok_ctrl:
        print("  REFUSE: the classifier did not respond to a known-bad input. Its clean "
              "result is NOT evidence.")
        return 2
    ok &= ok_ctrl

    print("\nP1 %s" % ("PASS" if ok else "GATE FAIL — reported, NOT adjusted"))
    return 0 if ok else 1

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        sys.exit(selftest())
    sys.exit(main(sys.argv[1]))
