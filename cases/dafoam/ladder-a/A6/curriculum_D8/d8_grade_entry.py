#!/usr/bin/env python3
"""
D8 grader ENTRY SHIM -- 2026-08-25, D8 CLOSE lane.

WHY THIS FILE EXISTS, and what it deliberately does NOT do.

`d8_grade.py` carries AMENDMENT 1 (commit b8039512), which repairs the v1.0 G0 gate.
Rule 6 required that amendment to be APPENDED at the foot with zero lines changed
above it, and it was: `diff` between the frozen 405-line body and the amended file is
a single purely-additive hunk `@@ -403,3 +403,182 @@`, and `head -405` of the amended
file hashes to the frozen md5 `04bba79c2a303bc3cf70af723da81dce` exactly.

But the frozen body's LAST EIGHT LINES are its `if __name__ == "__main__":` entrypoint.
Python executes a module body top to bottom, so when `d8_grade.py` is run as a script
that entrypoint fires at line 397 -- while `main` is still bound to the v1.0 body --
and `sys.exit(main(sys.argv[1]))` raises SystemExit before the amended `def main` at
line 429 is ever evaluated. AMENDMENT 1 is therefore INERT when the file is run as a
script: the v1.0 gate runs, G0 fails on `Mesh region0 size: 41760` (the very string
the amendment exists to replace), and the grader REFUSES (exit 2), grading nothing.

DEMONSTRATED, not asserted:
    $ python3 d8_grade.py <root>
      G0 Mesh region0 size: 41760           FAIL
      REFUSE: G0 failed -- the arm is VOID on identity/activity; nothing below is graded
      rc = 2
The printed label is the v1.0 label. The v1.1 labels are `Global Cells: 41760 (runtime)`
and `Mesh region0 size: 41760 (generation record)`. Which labels appear is the tell for
which `main` ran, and it is checked below.

THE REPAIR IS A DISPATCH FIX AND NOTHING ELSE. This shim does not edit, patch, monkey-
patch or re-implement one byte of `d8_grade.py`. It imports the committed file under a
module name that is not `__main__`, so the v1.0 entrypoint is skipped, the module body
runs to completion, and the name `main` resolves to the amended v1.1 body -- the same
bytes that were frozen at 17:00Z on 2026-08-25, BEFORE either arm had produced a graded
quantity (arm `opt` ran 16:51:53Z-18:19:24Z; arm `fd` 18:20:22Z-19:03:44Z).

NO GATE, THRESHOLD, BAND, CAP OR LABEL IS TOUCHED HERE. Every number this shim can
produce comes out of the committed blob. Three controls enforce that:

  C1  the file's md5 must equal the HEAD blob md5 -- if the instrument on disk is not
      the committed instrument, refuse.
  C2  the bound `main` must be defined BELOW line 405 -- i.e. it must be the amended
      body and not the frozen v1.0 body. If the shim ever silently binds v1.0 again,
      this refuses instead of grading.
  C3  the frozen 405-line prefix must still hash to the original section-9 md5, so the
      append-only property of AMENDMENT 1 is re-proved at grading time, not trusted.

Refuses (exit 2) rather than degrading, exactly as the instrument it drives does.
"""
import hashlib
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GRADER = os.path.join(HERE, "d8_grade.py")

HEAD_BLOB_MD5 = "0b1907a994b626d5d869ce159bd181df"   # git show HEAD:.../d8_grade.py
FROZEN_S9_MD5 = "04bba79c2a303bc3cf70af723da81dce"   # PREREGISTRATION.md s9, v1.0 body
FROZEN_LINES = 405                                    # length of the v1.0 body


def refuse(msg):
    print("REFUSE (entry shim): %s" % msg)
    sys.exit(2)


def main():
    if len(sys.argv) != 2:
        refuse("usage: d8_grade_entry.py <run-root>")
    root = sys.argv[1]

    raw = open(GRADER, "rb").read()

    # C1 -- the instrument on disk is the committed instrument
    got = hashlib.md5(raw).hexdigest()
    print("  C1 d8_grade.py md5            %s (HEAD blob %s) %s"
          % (got, HEAD_BLOB_MD5, "OK" if got == HEAD_BLOB_MD5 else "FAIL"))
    if got != HEAD_BLOB_MD5:
        refuse("d8_grade.py is not the committed blob -- refusing to grade with an "
               "unverified instrument")

    # C3 -- AMENDMENT 1 is still append-only: the frozen prefix is untouched
    prefix = b"".join(raw.splitlines(keepends=True)[:FROZEN_LINES])
    pgot = hashlib.md5(prefix).hexdigest()
    print("  C3 frozen 405-line prefix md5 %s (s9 %s) %s"
          % (pgot, FROZEN_S9_MD5, "OK" if pgot == FROZEN_S9_MD5 else "FAIL"))
    if pgot != FROZEN_S9_MD5:
        refuse("the frozen v1.0 body has been altered -- AMENDMENT 1 is no longer "
               "append-only and rule 6 is broken")

    spec = importlib.util.spec_from_file_location("d8_grade_frozen", GRADER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["d8_grade_frozen"] = mod
    spec.loader.exec_module(mod)          # __name__ != "__main__": v1.0 entrypoint skipped

    # C2 -- the bound main is the AMENDED body, not the frozen one
    ln = mod.main.__code__.co_firstlineno
    print("  C2 bound main defined at line %d (must be > %d, i.e. the AMENDMENT 1 body) %s"
          % (ln, FROZEN_LINES, "OK" if ln > FROZEN_LINES else "FAIL"))
    if ln <= FROZEN_LINES:
        refuse("the shim bound the v1.0 main -- AMENDMENT 1 would be inert; refusing")

    return mod.main(root)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("REFUSE (entry shim): %s: %s" % (type(e).__name__, e))
        sys.exit(2)
