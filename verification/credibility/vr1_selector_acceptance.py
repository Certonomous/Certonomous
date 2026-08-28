#!/usr/bin/env python3
"""VR1 -- the FROZEN ACCEPTANCE TEST for the non-unique selector class (L-398).

Frozen gate: verification/campaign/VR1_PREREGISTRATION.md, commit ffe5ded7.
Written BEFORE any successor comparator exists, so it cannot be shaped to the
repair that arrives.  A selector is handed in as a callable over a directory.
"""
import os, sys, tempfile

REAL_BASENAMES = ["T_coneSurface.raw", "p_coneSurface.raw", "rho_coneSurface.raw",
                  "T_wedgeSurface.raw", "p_wedgeSurface.raw", "rho_wedgeSurface.raw",
                  "p_cylSurface.raw", "wallShearStress_plate.raw"]

def defective(d):
    """The shape L-398 records, verbatim in effect: grade_f3s.py:239."""
    c = sorted(f for f in os.listdir(d) if f.endswith(".raw") and "p" in f)
    return c[0] if c else None

def repaired(d):
    """The shape the gate demands: a CARDINALITY guard on the deciding set."""
    c = sorted(f for f in os.listdir(d)
               if f.endswith(".raw") and f.startswith("p_") and not f.startswith("p_rgh"))
    c += sorted(f for f in os.listdir(d) if f.endswith(".raw") and f.startswith("p_rgh"))
    if len(c) != 1:
        raise RuntimeError("VR1-G1: expected exactly one pressure .raw, found %d: %s" % (len(c), c))
    return c[0]

def _plant(names):
    d = tempfile.mkdtemp(prefix="vr1_")
    for n in names:
        open(os.path.join(d, n), "w").write("x\n")
    return d

def run(sel):
    fails = []
    # G2 -- ACCEPTS the well-formed directory, returning the pressure file.
    d = _plant(["T_coneSurface.raw", "p_coneSurface.raw", "rho_coneSurface.raw"])
    try:
        got = sel(d)
        if got != "p_coneSurface.raw":
            fails.append("G2: well-formed dir returned %r, wanted p_coneSurface.raw" % got)
    except Exception as e:
        fails.append("G2: refused a well-formed directory (%s)" % e)
    # G1 (Amendment 1) -- MUST NEVER RETURN A NON-PRESSURE FILE. The renamed
    # surface holds exactly ONE pressure file; a correct selector RETURNS it.
    # "Three matches" is a property of the DEFECTIVE FILTER, not of the directory.
    d = _plant(["T_rampSurface.raw", "p_rampSurface.raw", "rho_rampSurface.raw"])
    try:
        got = sel(d)
        if got != "p_rampSurface.raw":
            fails.append("G1: returned %r on a renamed surface; wanted p_rampSurface.raw "
                         "(returning T_ is the L-398 failure)" % got)
    except Exception as e:
        fails.append("G1: refused a directory holding exactly one pressure file (%s)" % e)
    # G1b (Amendment 1) -- MUST REFUSE a genuinely ambiguous set: two real
    # pressure fields, one meant. This is the cardinality limb.
    d = _plant(["p_coneSurface.raw", "p_rgh_coneSurface.raw", "T_coneSurface.raw"])
    try:
        got = sel(d)
        fails.append("G1b: returned %r instead of refusing (p_ and p_rgh_ both present)" % got)
    except Exception:
        pass
    return fails

def main():
    print("VR1 -- selector acceptance test (frozen: VR1_PREREGISTRATION.md @ ffe5ded7)")
    print("G4 control corpus, real basenames read from disk elsewhere in this repo:")
    print("     " + ", ".join(REAL_BASENAMES))
    bad = run(defective)
    good = run(repaired)
    print("  DEFECTIVE selector (L-398's shape) -> %d gate failure(s): %s"
          % (len(bad), bad if bad else "none"))
    print("  REPAIRED  selector (cardinality guard) -> %d gate failure(s): %s"
          % (len(good), good if good else "none"))
    if not bad:
        print("VERDICT: NOT A RESULT -- the test did not fail the KNOWN-BAD selector, "
              "so it cannot certify a good one (standing rule 3; charter 2j)")
        return 2
    if good:
        print("VERDICT: NOT A RESULT -- the test failed the KNOWN-GOOD selector")
        return 2
    print("VERDICT: PASS -- fails the known-bad selector, passes the known-good one")
    return 0

if __name__ == "__main__":
    sys.exit(main())
