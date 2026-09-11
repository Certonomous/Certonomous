#!/usr/bin/env python3
"""Read ONE level's registered gate numbers out of its own checkMesh report.

Registered items (L2_L3_OUTCOME_PARTITION.md, committed 9651f6cc4 BEFORE the build):
  ROW 0   completion: CGNS written and plot3dToFoam/checkMesh could read it
  AXIS A  max skewness S vs gate 4
  AXIS B  trend S3-S1 vs H=0.10          (needs L3; reported as PENDING at L2)
  AXIS C  max non-orthogonality vs gate 70
  DIAG    skew-face count and centroid location  (reported, never gated)
  plus    DELIVERED cell count and r21 RE-DERIVED from what checkMesh reports

TRAPS THIS READER IS BUILT AGAINST, all measured in this campaign today:
  * checkMesh's rc is meaningless in BOTH directions -> the report TEXT is read.
  * checkMesh prints 'solution (non-empty) directions' FOUR LINES from the
    geometric one, and the solution line reads 3 for a wedge -> match the word
    'geometric' specifically, never just 'directions'.
  * a zero face-count is only evidence if the set-writer was shown able to write
    a NON-empty set in the SAME run -> the sibling sets are listed as the control.
"""
import re, sys, os

GATE_SKEW, GATE_NONORTHO = 4.0, 70.0
S1 = 4.90021          # L1 max skewness, measured, committed at 9572e4f42
H  = 0.10             # hold band, fixed in advance

def grab(txt, pat, cast=float):
    m = re.search(pat, txt)
    return cast(m.group(1)) if m else None

def main(lvl):
    R = os.path.dirname(os.path.abspath(__file__))
    L = os.path.join(R, lvl)
    cm = os.path.join(L, "log.checkMesh")
    print("=== %s : ROW 0 -- COMPLETION ===" % lvl)
    for name, p in (("CGNS", os.path.join(L, "m6c2_mp_%s_vol.cgns" % lvl)),
                    ("PLOT3D", os.path.join(L, "m6c2_mp_%s_vol.xyz" % lvl)),
                    ("log.checkMesh", cm)):
        ok = os.path.exists(p) and os.path.getsize(p) > 0
        print("   %-14s %s %s" % (name, "present" if ok else "ABSENT/EMPTY",
                                  ("%d bytes" % os.path.getsize(p)) if ok else ""))
    ex = os.path.join(L, "log.extrude")
    comp = "EXTRUSION COMPLETE" in open(ex).read() if os.path.exists(ex) else False
    rcf = os.path.join(L, "rc.extrude")
    rc = open(rcf).read().strip() if os.path.exists(rcf) else "(no rc file)"
    print("   EXTRUSION COMPLETE line: %s     wrapper rc (captured INSIDE): %s" % (comp, rc))
    if not (comp and os.path.exists(cm)):
        print("   *** ROW 0 APPLIES: %s is NOT A RESULT and the partition is NOT READ. ***" % lvl)
        return 1
    t = open(cm).read()

    print("\n=== DELIVERED MESH, AS checkMesh REPORTS IT (not as planned) ===")
    cells = grab(t, r"cells:\s+(\d+)", int)
    pts   = grab(t, r"points:\s+(\d+)", int)
    faces = grab(t, r"faces:\s+(\d+)", int)
    hexes = grab(t, r"hexahedra:\s+(\d+)", int)
    print("   cells %s   points %s   internal+boundary faces %s   hexahedra %s (%.2f %%)"
          % (cells, pts, faces, hexes, 100.0 * hexes / cells if cells and hexes else float('nan')))
    # the geometric directions line -- NOT the 'solution (non-empty)' one 4 lines away
    # The geometric line reads "(non-empty/wedge)"; the SOLUTION line reads
    # "(non-empty)". Matching "(non-empty)" grabs the WRONG line -- match the
    # word 'geometric' and let the parenthetical be anything.
    gd = re.search(r"Mesh has (\d+) geometric \([^)]*\) directions", t)
    sd = re.search(r"Mesh has (\d+) solution \([^)]*\) directions", t)
    print("   geometric (non-empty) directions = %s   [solution line, NOT the gate: %s]"
          % (gd.group(1) if gd else "NOT FOUND", sd.group(1) if sd else "n/a"))

    L1cells = 452608     # measured, committed at 9572e4f42
    if cells:
        ratio = cells / L1cells
        print("   cells/L1 = %d/%d = %.4f   =>  r21 RE-DERIVED = %.6f  (plan says 1.5)"
              % (cells, L1cells, ratio, ratio ** (1.0 / 3.0)))
        print("   *** a ratio exact in the plan is still ASSUMED until the mesh reports it. ***")

    print("\n=== AXIS A -- SKEWNESS, GATE %.0f ===" % GATE_SKEW)
    S = grab(t, r"Max skewness = ([\d.eE+-]+)")
    nsk = grab(t, r"Max skewness = [\d.eE+-]+.*?(\d+) highly skew faces", int)
    if nsk is None:
        m = re.search(r"(\d+) highly skew faces", t); nsk = int(m.group(1)) if m else 0
    print("   max skewness = %s   highly skew faces = %d   %s"
          % (S, nsk, "CLEARS" if (S is not None and S <= GATE_SKEW) else "FAILS"))

    print("\n=== AXIS C -- NON-ORTHOGONALITY, GATE %.0f ===" % GATE_NONORTHO)
    N = grab(t, r"Mesh non-orthogonality Max: ([\d.eE+-]+)")
    A = grab(t, r"Mesh non-orthogonality Max: [\d.eE+-]+ average: ([\d.eE+-]+)")
    m = re.search(r"\*Number of severely non-orthogonal \(> \d+ degrees\) faces: (\d+)", t)
    nno = int(m.group(1)) if m else 0
    print("   max non-orthogonality = %s  (avg %s)   severely non-ortho faces = %d   %s"
          % (N, A, nno, "CLEARS" if (N is not None and N <= GATE_NONORTHO) else "FAILS"))

    print("\n=== THE ZERO CONTROL -- which sets did checkMesh actually WRITE? ===")
    sets = re.findall(r"<<Writing (\d+) .*? to set (\w+)", t)
    written = sorted(set(sets), key=lambda x: x[1])
    print("   sets written in THIS run: %s"
          % (", ".join("%s(%s)" % (n, c) for c, n in written) if written else "NONE"))
    nonempty = [n for c, n in written if int(c) > 0]
    print("   NON-EMPTY sets written: %s" % (", ".join(nonempty) if nonempty else "NONE"))
    if not nonempty:
        print("   *** THE SET-WRITER WAS NOT SHOWN ABLE TO PRODUCE A NON-EMPTY SET.")
        print("       Any zero face-count above is NOT EVIDENCE. ***")
    print("   => a zero count above is evidence only if a SIBLING set here is non-empty.")

    print("\n=== AXIS B -- TREND, H = %.2f ===" % H)
    print("   S1 = %.5f (L1, committed).  S2 = %s." % (S1, S))
    print("   Axis B is defined on S3 - S1 and L3 is NOT BUILT: Axis B is PENDING.")
    print("   The partition has NINE cells and none may be named from two levels.")

    print("\n=== OTHER REPORTED QUANTITIES ===")
    for lab, pat in (("boundary openness", r"Boundary openness \(([^)]+)\)"),
                     ("max cell openness", r"Max cell openness = ([\d.eE+-]+)"),
                     ("max aspect ratio", r"Max aspect ratio = ([\d.eE+-]+)"),
                     ("min face area", r"Minimum face area = ([\d.eE+-]+)"),
                     ("min volume", r"Min volume = ([\d.eE+-]+)")):
        m = re.search(pat, t)
        print("   %-20s %s" % (lab, m.group(1) if m else "not found"))
    for lab, pat in (("face pyramids", r"Face pyramids\s+(.*)"),
                     ("concave cells", r"(?:concave cells|Concave cell).*")):
        m = re.search(pat, t)
        print("   %-20s %s" % (lab, m.group(0).strip()[:70] if m else "not found"))
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "L2"))
