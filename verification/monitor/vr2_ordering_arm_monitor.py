#!/usr/bin/env python3
"""VR2 -- the ARMING MONITOR for the LATENT ordering-key sites.

Frozen gate: verification/campaign/VR2_PREREGISTRATION.md, commit ffe5ded7.
LATENT is not a resting state, it is an UNMONITORED one.  This fires the moment
a site's function-object directory set becomes MULTI-MEMBER *and* DIVERGENT
(lexicographic last != numeric last), which is the arming condition.
"""
import os, sys, tempfile

ROOTS = ["verification/runs/F3_runs", "verification/runs/F4_runs",
         "verification/runs/DPW8_V2_runs", "verification/runs/F23_HP_WEDGE_runs"]

def divergent(names):
    ns = [n for n in names if n and n[0].isdigit()]
    if len(ns) < 2:
        return None
    lex = sorted(ns)[-1]
    try:
        num = sorted(ns, key=float)[-1]
    except ValueError:
        return None
    return (lex, num) if lex != num else None

def scan(roots):
    armed, seen = [], 0
    for r in roots:
        for dp, dn, fn in os.walk(r):
            if os.path.basename(os.path.dirname(dp)) != "postProcessing":
                continue
            kids = [d for d in dn]
            seen += 1
            d = divergent(kids)
            if d:
                armed.append((dp, len(kids), d[0], d[1]))
    return armed, seen

def control():
    """G3 -- both limbs, before any zero is believed (charter 2j)."""
    ok = True
    t = tempfile.mkdtemp(prefix="vr2_")
    pp = os.path.join(t, "case", "postProcessing", "fo")
    os.makedirs(pp)
    for n in ("0", "950", "2000"):
        os.makedirs(os.path.join(pp, n))
    a, _ = scan([t])
    if not a:
        print("  CONTROL FAIL: planted {0,950,2000} did NOT fire"); ok = False
    else:
        print("  control +: planted {0,950,2000} fired -> lex=%s num=%s" % (a[0][2], a[0][3]))
    t2 = tempfile.mkdtemp(prefix="vr2_")
    pp2 = os.path.join(t2, "case", "postProcessing", "fo")
    os.makedirs(pp2)
    for n in ("0", "100", "200"):
        os.makedirs(os.path.join(pp2, n))
    b, _ = scan([t2])
    if b:
        print("  CONTROL FAIL: planted {0,100,200} fired (lex == numeric here)"); ok = False
    else:
        print("  control -: planted {0,100,200} correctly silent")
    return ok

def main():
    print("VR2 -- ordering-key ARMING monitor (frozen: VR2_PREREGISTRATION.md @ ffe5ded7)")
    if not control():
        print("VERDICT: NOT A RESULT -- controls did not both behave")
        return 2
    armed, seen = scan([r for r in ROOTS if os.path.isdir(r)])
    print("  scanned %d function-object directories under %d roots" % (seen, len(ROOTS)))
    if armed:
        print("VERDICT: GATE FAIL -- %d site(s) ARMED:" % len(armed))
        for dp, n, lex, num in armed:
            print("    %s  (%d dirs) lexicographic[-1]=%s  numeric[-1]=%s" % (dp, n, lex, num))
        return 1
    print("VERDICT: PASS -- no LATENT site has armed; every set is single-member "
          "or lexicographically == numerically ordered")
    return 0

if __name__ == "__main__":
    sys.exit(main())
