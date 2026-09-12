#!/usr/bin/env python3
"""A3GC-L2R READER CONTROL -- drives the amended first-match reader in THREE
DIRECTIONS before it is allowed to grade anything.

Not a grader.  It exercises ONE thing: `read_log`'s choice of which `initRes`
line to keep, in `a3gc_grade_l2r.py`, against `a3gc_grade.py`'s frozen last-match
reader, on REAL DAFoam blocks taken from A3GC's own runs.

Exit 0 only if all three directions hold.  Exit 2 refuses.

DIRECTION 1  single-corrector block  -> must read the HONEST outer value.
DIRECTION 2  multi-corrector block with a PLANTED tiny value in a LATER
             corrector position -> must NOT return the plant.  THIS IS THE
             EXACT FORGERY THE FROZEN READER WOULD HAVE SHIPPED.
DIRECTION 3  multi-corrector block -> must return its FIRST line.

A reader that cannot be shown returning BOTH the honest value AND (under the old
rule) the plant is not a reader whose zero means anything (CLAUDE.md rule 3).
"""
import os, re, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
PLANT = 1.234e-09          # distinctive; no A3GC residual lands here by accident


def load(modname, path):
    spec = importlib.util.spec_from_file_location(modname, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[modname] = m
    spec.loader.exec_module(m)
    return m


def blocks(txt):
    tm = [m.start() for m in re.finditer(r"^Time = ", txt, re.M)]
    return [txt[tm[i]: (tm[i + 1] if i + 1 < len(tm) else len(txt))]
            for i in range(len(tm))]


def initres_lines(block, eq="p"):
    return [L for L in block.splitlines()
            if re.match(r"^%s initRes:" % eq, L)]


def read_with(mod, text, tmpname):
    p = os.path.join("/tmp", tmpname)
    with open(p, "w") as fh:
        fh.write(text)
    try:
        return mod.read_log(p)["last_initRes"]
    finally:
        os.unlink(p)


def fail(msg):
    print("  REFUSE: %s" % msg)
    sys.exit(2)


def main():
    if len(sys.argv) != 3:
        print("usage: a3gc_l2r_reader_control.py <single_corrector_log> <multi_corrector_log>")
        sys.exit(2)
    single_log, multi_log = sys.argv[1], sys.argv[2]
    for p in (single_log, multi_log):
        if not os.path.isfile(p):
            fail("fixture log does not exist: %s" % p)

    new = load("g_l2r", os.path.join(HERE, "a3gc_grade_l2r.py"))
    old = load("g_frozen", os.path.join(HERE, "a3gc_grade.py"))

    print("=" * 72)
    print("A3GC-L2R READER CONTROL -- three directions on REAL DAFoam blocks")
    print("=" * 72)

    # ---------------- DIRECTION 1 ----------------
    print("\n--- DIRECTION 1: single-corrector block must read the HONEST outer value ---")
    stxt = open(single_log, errors="replace").read()
    sblk = blocks(stxt)[-1]
    slines = initres_lines(sblk)
    print("  fixture        : %s (last Time block)" % single_log)
    print("  p initRes lines: %d" % len(slines))
    if len(slines) != 1:
        fail("DIRECTION 1 fixture is not single-corrector (%d p lines)" % len(slines))
    honest = float(re.search(r"initRes:\s+([-+0-9.eE]+)", slines[0]).group(1))
    got_new = read_with(new, sblk, "a3gc_d1_new.log")["p"]
    got_old = read_with(old, sblk, "a3gc_d1_old.log")["p"]
    print("  honest value   : %.10e" % honest)
    print("  amended reader : %.10e  %s" % (got_new, "OK" if got_new == honest else "WRONG"))
    print("  frozen reader  : %.10e  (agrees here -- one line, so both rules coincide)" % got_old)
    if got_new != honest:
        fail("DIRECTION 1: amended reader did not return the honest outer value")
    if got_old != honest:
        fail("DIRECTION 1: frozen reader did not return the honest value on a "
             "single-corrector block -- the fixture or the control is wrong")

    # ---------------- DIRECTION 3 (needs the multi fixture; run before 2) ------
    print("\n--- DIRECTION 3: multi-corrector block must return its FIRST line ---")
    mtxt = open(multi_log, errors="replace").read()
    mblk = None
    for b in blocks(mtxt):
        if len(initres_lines(b)) > 1:
            mblk = b
            break
    if mblk is None:
        fail("DIRECTION 3: no multi-corrector block found in %s -- the whole "
             "premise of this amendment is unverified, so it must not be frozen"
             % multi_log)
    mlines = initres_lines(mblk)
    first = float(re.search(r"initRes:\s+([-+0-9.eE]+)", mlines[0]).group(1))
    lastv = float(re.search(r"initRes:\s+([-+0-9.eE]+)", mlines[-1]).group(1))
    print("  fixture        : %s" % multi_log)
    print("  p initRes lines: %d  (REAL DAFoam output, correctors ON)" % len(mlines))
    for L in mlines:
        print("     %s" % L)
    got_new = read_with(new, mblk, "a3gc_d3_new.log")["p"]
    got_old = read_with(old, mblk, "a3gc_d3_old.log")["p"]
    print("  first line     : %.10e" % first)
    print("  last  line     : %.10e" % lastv)
    print("  amended reader : %.10e  %s" % (got_new, "OK" if got_new == first else "WRONG"))
    print("  frozen reader  : %.10e  %s" % (got_old, "(returns the LAST -- the defect)"))
    if got_new != first:
        fail("DIRECTION 3: amended reader did not return the first line")
    if len(mlines) > 1 and first == lastv:
        print("  NOTE: first == last on this block, so DIRECTION 3 cannot by itself")
        print("        separate the two rules.  DIRECTION 2 plants a value to force it.")

    # ---------------- DIRECTION 2 ----------------
    print("\n--- DIRECTION 2: planted value in a LATER corrector must NOT be returned ---")
    print("  (this is the exact forgery the frozen reader would have shipped)")
    planted_line = re.sub(r"initRes:\s+[-+0-9.eE]+",
                          "initRes: %.9e" % PLANT, mlines[-1], count=1)
    pblk = mblk.replace(mlines[-1], planted_line, 1)
    if planted_line not in pblk:
        fail("DIRECTION 2: the plant was not written into the block")
    got_new = read_with(new, pblk, "a3gc_d2_new.log")["p"]
    got_old = read_with(old, pblk, "a3gc_d2_old.log")["p"]
    print("  plant          : %.9e  (written into the LAST corrector position)" % PLANT)
    print("  amended reader : %.10e  %s" % (got_new, "OK -- plant NOT returned"
                                            if got_new != PLANT else "*** RETURNED THE PLANT ***"))
    print("  frozen reader  : %.10e  %s" % (got_old, "<-- PLANT READ BACK: the defect is LIVE"
                                            if got_old == PLANT else "(did not return the plant)"))
    if got_new == PLANT:
        fail("DIRECTION 2: the amended reader returned the plant")
    if got_new != first:
        fail("DIRECTION 2: amended reader returned %r, expected the first line %r"
             % (got_new, first))
    if got_old != PLANT:
        fail("DIRECTION 2: the FROZEN reader did NOT return the plant, so this "
             "control has not demonstrated the defect it exists to demonstrate. "
             "A control that cannot show the failure proves nothing about the fix.")

    # ---------------- direction of the change ----------------
    print("\n--- DIRECTION OF THE CHANGE: can only LOWER a verdict, never raise one ---")
    print("  amended reads %.10e ; frozen reads %.10e" % (first, lastv))
    if first < lastv:
        fail("the amended reader returned a SMALLER residual than the frozen one on a "
             "real block -- that would make the gate EASIER, which this amendment "
             "is registered never to do")
    print("  amended >= frozen on this real block: the amended reader reads the")
    print("  HARDER number. The gate is unmoved; only the number fed to it got worse.")

    print("\n" + "=" * 72)
    print("ALL THREE DIRECTIONS HOLD -- reader may be frozen.")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
