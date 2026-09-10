#!/usr/bin/env python3
"""RC4 gate P1 -- THE REPAIR IS ATTRIBUTABLE TO `R` AND TO NOTHING ELSE.

Registration: cases/RANS_LES_closure_models/RC4_kaandorp_propagation_repair/
PREREGISTRATION.md -- section 5 P1 (the gate), section 6 (the third planted
control), section 6.1 (no ast.Assert), section 7 (the second and third
falsifiers), section 10 (one change per run) and section 11 (this module's
registered job and its registered refusals).

THE GATE, verbatim from section 5
---------------------------------
  "The T-bR case directory must differ from the T-b case directory in exactly
   one field file: `kDeficit`.  Every other file -- `system/`, `constant/`,
   `fvSchemes`, `fvSolution`, `controlDict`, BCs, `0/` fields, mesh -- must be
   byte-identical."

  "Verified by a registered recursive directory comparison whose only permitted
   difference is `<time>/kDeficit`.  Any other difference: the instrument
   refuses, `sys.exit(2)`, and the row is `NOT A RESULT`."

WHAT "THE CASE DIRECTORY" MEANS HERE, STATED RATHER THAN ASSUMED
-----------------------------------------------------------------
The clause enumerates INPUTS -- `system/`, `constant/`, `fvSchemes`,
`fvSolution`, `controlDict`, BCs, `0/` fields, mesh.  A solved case also
carries OUTPUTS the solver wrote (its log, its recorded rc, the time
directories it produced), and those cannot be byte-identical between two
configurations that by construction converge differently.  The comparison is
therefore over the case's INPUT SURFACE, and the output artifacts it steps over
are a FIXED, PRINTED list (`OUTPUT_PATTERNS` below) -- printed on every run, so
nothing is skipped quietly.

`--at-build` closes the hole entirely and is the mode the builder uses: run
immediately after the build, when NO output exists, it refuses if either tree
carries any output artifact at all, so the comparison is total and the
exclusion list is doing nothing.  A P1 verdict taken at build time is therefore
a comparison of every byte in both trees.

REGISTERED REFUSALS (section 11), every one a sys.exit(2), never an assert:
  * any difference outside `<time>/kDeficit`,
  * the plant not being detected.

And one more the clause requires by its own wording, "must differ ... in
exactly one field file": if `<time>/kDeficit` is BYTE-IDENTICAL between the two
trees then T-bR is not a different configuration from T-b, the arm does not
exist, and the instrument refuses.

NO ast.Assert CARRIES ANY REFUSAL, GUARD, CONTROL OR GATE (section 6.1, L-332 /
D476 section 31.3).
"""
from __future__ import annotations

import ast
import filecmp
import os
import re
import shutil
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CLOSURE = os.path.dirname(HERE)
COMMON = os.path.join(CLOSURE, "_common")
R4 = os.path.join(CLOSURE, "R4_sparta_build")
for _p in (HERE, COMMON, R4):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from of_read import read_field                               # noqa: E402
import build_rc4_cases as B                                  # noqa: E402

PLANT = 1.234e-03
TIME0 = B.TIME0
KDEFICIT = B.KDEFICIT
PERMITTED = TIME0 + "/" + KDEFICIT          # `<time>/kDeficit`, and only it

# The output surface a solved case carries.  FIXED and PRINTED on every run.
OUTPUT_PATTERNS = (
    r"^log\.",                       # the solver log
    r"^rc$",                         # the recorded return code
    r"^postProcessing/",
    r"^dynamicCode/",
    r"^VTK/",
    r"^processor\d+/",
    r"^convergencePlots/",
    r".*\.foam$",
)
# a numeric time directory that is NOT the input time is an output
TIME_DIR_RE = re.compile(r"^([0-9]+(?:\.[0-9]+)?)/")

# A real kDeficit written by kCorrectiveFrozenFoam on this box, for section 6's
# third control.  ONE NAMED ARTIFACT -- never a glob.
REAL_KDEFICIT = ("/home/ubuntu/closure-data/aposteriori/kaandorp/"
                 "AR_1_Ret_360__FROZENEXTRACT/647/kDeficit")


def refuse(msg):
    sys.stderr.write("RC4 REFUSED (sys.exit 2): " + str(msg) + "\n")
    sys.stderr.flush()
    raise SystemExit(2)


def is_output(rel):
    for pat in OUTPUT_PATTERNS:
        if re.search(pat, rel):
            return True
    m = TIME_DIR_RE.match(rel)
    if m and m.group(1) != TIME0:
        return True
    return False


def _walk(root):
    out = []
    for dirpath, _dirs, files in os.walk(root):
        for f in files:
            p = os.path.join(dirpath, f)
            out.append(os.path.relpath(p, root).replace(os.sep, "/"))
    return sorted(out)


def _same_bytes(a, b):
    return filecmp.cmp(a, b, shallow=False)


def compare(tb, tbr, permitted=PERMITTED, at_build=False, _cmp=_same_bytes):
    """The registered recursive directory comparison.

    Returns a record; REFUSES on any violation.  `_cmp` is injectable so
    section 6's third control can drive a BLINDED byte comparator and show that
    the plant check actually FIRES.
    """
    for d, name in ((tb, "T-b"), (tbr, "T-bR")):
        if not os.path.isdir(d):
            refuse("P1: the " + name + " case directory is absent: " + str(d))
    a, b = _walk(tb), _walk(tbr)
    out_a = [p for p in a if is_output(p)]
    out_b = [p for p in b if is_output(p)]
    if at_build and (out_a or out_b):
        refuse("P1 --at-build: an output artifact is already present, so this "
               "is not a build-time comparison: "
               + ", ".join(sorted(set(out_a) | set(out_b))[:10]))
    ina, inb = [p for p in a if not is_output(p)], [p for p in b if not is_output(p)]
    print("[P1] input surface: %d files in T-b, %d in T-bR; output artifacts "
          "stepped over: %s"
          % (len(ina), len(inb),
             (", ".join(sorted(set(out_a) | set(out_b))) or "none")))

    only_a = sorted(set(ina) - set(inb))
    only_b = sorted(set(inb) - set(ina))
    if only_a or only_b:
        refuse("P1: the two case directories do not carry the same input "
               "files.  Only in T-b: " + (", ".join(only_a) or "none")
               + ".  Only in T-bR: " + (", ".join(only_b) or "none")
               + ".  An arm that moves more than one thing answers no "
               "question; the row is NOT A RESULT")

    differing = sorted(p for p in ina
                       if not _cmp(os.path.join(tb, p), os.path.join(tbr, p)))
    extra = [p for p in differing if p != permitted]
    if extra:
        refuse("P1: files other than " + permitted + " differ between "
               + tb + " and " + tbr + ": " + ", ".join(extra)
               + ".  This is NONCONVERGENCE_STANDARD section 2.0's one change "
               "per run made executable; the row is NOT A RESULT and is not "
               "re-scored as it stands (section 7, second falsifier)")
    if permitted not in differing:
        refuse("P1: " + permitted + " is BYTE-IDENTICAL between " + tb
               + " and " + tbr + ".  T-bR is then not a different "
               "configuration from T-b, the repaired arm does not exist, and "
               "there is nothing to attribute")
    print("[P1] PASS: exactly one file differs, and it is " + permitted)
    return {"t_b": tb, "t_bR": tbr, "permitted": permitted,
            "differing": differing, "n_input_files": len(ina),
            "output_artifacts_skipped": sorted(set(out_a) | set(out_b)),
            "at_build": bool(at_build)}


# ------------------------------- section 6, the third planted control
def plant_control_kdeficit(real_kdeficit=REAL_KDEFICIT, scratch=None,
                           _cmp=_same_bytes):
    """Section 6's third control, verbatim in code.

      "Because RC4's whole claim rests on `kDeficit` being non-zero in T-bR and
       zero in T-b, the instrument additionally plants `PLANT = 1.234e-03` into
       a copy of a real `kDeficit` field, reads it back, and requires the P1
       directory comparator to report that file as differing.  If the
       comparator cannot see a planted difference in the one file it exists to
       watch, it is blind: `sys.exit(2)`."

    The read-back tolerance is PLANT-RELATIVE -- machine epsilon at the field's
    own largest magnitude, floored at 1e-12 -- never an absolute bar.  It has
    to be: `kDeficit_rms` on `AR_1_Ret_360` is 3.6961887e+07 (section 1.7), and
    an absolute 1e-15 read-back bar on data of that size false-refuses a
    perfect reader on arithmetic grounds alone (L-508).
    """
    if not os.path.exists(real_kdeficit):
        refuse("section 6 third control: no real kDeficit field to plant into: "
               + str(real_kdeficit) + ".  A control defined in terms of the "
               "thing it controls is not a control, so a synthetic file will "
               "not do")
    tmp = scratch or tempfile.mkdtemp(prefix="rc4_kdeficit_plant_")
    made = scratch is None
    try:
        tb = os.path.join(tmp, "T-b")
        tbr = os.path.join(tmp, "T-bR")
        for d in (tb, tbr):
            os.makedirs(os.path.join(d, TIME0), exist_ok=True)
            os.makedirs(os.path.join(d, "system"), exist_ok=True)
            open(os.path.join(d, "system", "controlDict"), "w").write(
                "endTime 30000;\n")
            open(os.path.join(d, TIME0, "U"), "w").write("0\n")
            shutil.copyfile(real_kdeficit, os.path.join(d, TIME0, KDEFICIT))

        orig = np.asarray(read_field(os.path.join(tb, TIME0, KDEFICIT)),
                          float).reshape(-1)
        planted = orig.copy()
        n = planted.shape[0]
        idx = sorted({0, n // 2})
        planted[idx] = planted[idx] + PLANT
        _swap_scalar_internal(os.path.join(tbr, TIME0, KDEFICIT), planted)

        back = np.asarray(read_field(os.path.join(tbr, TIME0, KDEFICIT)),
                          float).reshape(-1)
        amax = float(np.abs(planted).max())
        tol = max(1e-12, 8.0 * float(np.finfo(float).eps) * amax)
        recov = float(np.abs((back[idx] - orig[idx]) - PLANT).max())
        if recov > tol:
            refuse("section 6 third control: the planted kDeficit did not "
                   "survive the round trip -- max|recovered - PLANT| = %.3g > "
                   "tol %.3g (field max %.3g).  The reader cannot see a "
                   "non-zero in the one field this item changes"
                   % (recov, tol, amax))

        rec = compare(tb, tbr, at_build=True, _cmp=_cmp)
        if PERMITTED not in rec["differing"]:
            refuse("section 6 third control / section 7 third falsifier: the "
                   "P1 comparator did NOT report " + PERMITTED + " as "
                   "differing after PLANT = %g was written into %d of its %d "
                   "cells.  The comparator is BLIND to the only file this item "
                   "changes, and every P1 PASS it has ever emitted is void"
                   % (PLANT, len(idx), n))
        print("[P1 plant control] PLANT=%g into %d of %d cells of a real "
              "kDeficit (field max %.3g); read back to %.3g (tol %.3g); the "
              "comparator reported %s as differing : PASS"
              % (PLANT, len(idx), n, amax, recov, tol, PERMITTED))
        return {"field": real_kdeficit, "n_cells": int(n), "plant": PLANT,
                "planted_cells": idx, "readback_error": recov,
                "readback_tol": tol, "field_max_abs": amax,
                "detected": True, "verdict": "PASS"}
    finally:
        if made:
            shutil.rmtree(tmp, ignore_errors=True)


def _swap_scalar_internal(path, vals):
    s = open(path).read()
    if "internalField" not in s or "boundaryField" not in s:
        refuse("not an OpenFOAM field file: " + path)
    i, j = s.index("internalField"), s.index("boundaryField")
    a = np.asarray(vals, float).reshape(-1)
    body = ("internalField   nonuniform List<scalar>\n" + str(a.shape[0])
            + "\n(\n" + "\n".join("%.17g" % v for v in a) + "\n)\n;\n\n")
    open(path, "w").write(s[:i] + body + s[j:])


# ---------------------------------------------------------------- selftest
def _fires(fn, *a, **kw):
    try:
        fn(*a, **kw)
    except SystemExit as e:
        return int(e.code or 0) == 2
    return False


def _pair(root, extra_a=None, extra_b=None, kd_differs=True, outputs=False):
    tb, tbr = os.path.join(root, "T-b"), os.path.join(root, "T-bR")
    for d in (tb, tbr):
        os.makedirs(os.path.join(d, TIME0), exist_ok=True)
        os.makedirs(os.path.join(d, "system"), exist_ok=True)
        os.makedirs(os.path.join(d, "constant", "polyMesh"), exist_ok=True)
        open(os.path.join(d, "system", "controlDict"), "w").write("endTime 3;\n")
        open(os.path.join(d, "system", "fvSolution"), "w").write("SIMPLE{}\n")
        open(os.path.join(d, "constant", "polyMesh", "points"), "w").write("p\n")
        open(os.path.join(d, TIME0, "U"), "w").write("U\n")
        open(os.path.join(d, TIME0, "bijDelta"), "w").write("b\n")
        open(os.path.join(d, TIME0, KDEFICIT), "w").write("zero\n")
    if kd_differs:
        open(os.path.join(tbr, TIME0, KDEFICIT), "w").write("extracted R\n")
    if extra_a:
        for rel, txt in extra_a.items():
            p = os.path.join(tb, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "w").write(txt)
    if extra_b:
        for rel, txt in extra_b.items():
            p = os.path.join(tbr, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "w").write(txt)
    if outputs:
        for d in (tb, tbr):
            open(os.path.join(d, "log.solve"), "w").write("End\n")
            open(os.path.join(d, "rc"), "w").write("0\n")
            os.makedirs(os.path.join(d, "788"), exist_ok=True)
            open(os.path.join(d, "788", "U"), "w").write(d + "\n")
    return tb, tbr


def selftest():
    ok = []

    def note(name, passed, detail=""):
        ok.append((name, bool(passed), detail))

    tree = ast.parse(open(os.path.abspath(__file__)).read())
    n_assert = sum(isinstance(n, ast.Assert) for n in ast.walk(tree))
    note("ast.Assert count == 0", n_assert == 0, "counted " + str(n_assert))

    tmp = tempfile.mkdtemp(prefix="rc4_p1_cmp_")
    try:
        r = os.path.join(tmp, "clean")
        tb, tbr = _pair(r)
        rec = compare(tb, tbr, at_build=True)
        note("P1 PASSES when exactly 0/kDeficit differs",
             rec["differing"] == [PERMITTED])

        r2 = os.path.join(tmp, "twochanges")
        tb2, tbr2 = _pair(r2, extra_b={TIME0 + "/bijDelta": "different\n"})
        note("P1 FIRES when a second field file also differs",
             _fires(compare, tb2, tbr2, PERMITTED, True))

        r3 = os.path.join(tmp, "fvsolution")
        tb3, tbr3 = _pair(r3, extra_b={"system/fvSolution": "SIMPLE{tweak}\n"})
        note("P1 FIRES when fvSolution differs", _fires(compare, tb3, tbr3,
                                                        PERMITTED, True))
        r4d = os.path.join(tmp, "mesh")
        tb4, tbr4 = _pair(r4d, extra_b={"constant/polyMesh/points": "moved\n"})
        note("P1 FIRES when the mesh differs",
             _fires(compare, tb4, tbr4, PERMITTED, True))

        r5 = os.path.join(tmp, "extrafile")
        tb5, tbr5 = _pair(r5, extra_b={"system/fvOptions": "x\n"})
        note("P1 FIRES when T-bR carries an input file T-b does not",
             _fires(compare, tb5, tbr5, PERMITTED, True))

        r6 = os.path.join(tmp, "identical")
        tb6, tbr6 = _pair(r6, kd_differs=False)
        note("P1 FIRES when kDeficit is byte-identical -- T-bR would not be a "
             "different configuration at all",
             _fires(compare, tb6, tbr6, PERMITTED, True))

        r7 = os.path.join(tmp, "absent")
        note("P1 FIRES on an absent case directory",
             _fires(compare, os.path.join(r7, "nope"), tb, PERMITTED, True))

        r8 = os.path.join(tmp, "withoutputs")
        tb8, tbr8 = _pair(r8, outputs=True)
        note("P1 --at-build FIRES when an output artifact is already present, "
             "so a build-time verdict is always a total comparison",
             _fires(compare, tb8, tbr8, PERMITTED, True))
        rec8 = compare(tb8, tbr8, at_build=False)
        note("P1 after the run compares the input surface and names every "
             "output artifact it stepped over",
             rec8["differing"] == [PERMITTED]
             and set(rec8["output_artifacts_skipped"])
             == {"log.solve", "rc", "788/U"},
             ", ".join(rec8["output_artifacts_skipped"]))
        note("is_output classifies the input time directory as INPUT and a "
             "written time directory as OUTPUT",
             not is_output(TIME0 + "/kDeficit") and is_output("788/U"))

        # ---- section 6's third control, on a REAL kDeficit field.
        if os.path.exists(REAL_KDEFICIT):
            rec9 = plant_control_kdeficit()
            note("section 6 third control PASSES on a real kCorrectiveFrozenFoam "
                 "kDeficit (O(1e7) data, PLANT-relative tolerance -- L-508)",
                 rec9["verdict"] == "PASS",
                 "field max %.3g, read back to %.3g (tol %.3g)"
                 % (rec9["field_max_abs"], rec9["readback_error"],
                    rec9["readback_tol"]))
            note("section 6 third control FIRES against a BLINDED comparator "
                 "-- the section 7 third falsifier, exercised",
                 _fires(plant_control_kdeficit, REAL_KDEFICIT, None,
                        lambda a, b: True))
            note("section 6 third control FIRES when there is no real kDeficit "
                 "to plant into",
                 _fires(plant_control_kdeficit,
                        os.path.join(tmp, "no_such_kDeficit")))
        else:
            note("a real kCorrectiveFrozenFoam kDeficit is on disk for the "
                 "section 6 third control", False, REAL_KDEFICIT)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    width = max(len(n) for n, _, _ in ok)
    for name, passed, detail in ok:
        print(("  %-" + str(width) + "s  %s%s")
              % (name, "PASS" if passed else "FAIL",
                 ("   [" + detail + "]") if detail else ""))
    bad = [n for n, p, _ in ok if not p]
    if bad:
        sys.stderr.write("SELFTEST FAILED: " + "; ".join(bad) + "\n")
        raise SystemExit(1)
    print("rc4_onechange selftest: %d/%d PASS" % (len(ok), len(ok)))
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--compare" in argv:
        B.refuse_if_unfrozen()
        i = argv.index("--compare")
        if len(argv) < i + 3:
            refuse("usage: rc4_onechange.py --compare <T-b dir> <T-bR dir> "
                   "[--at-build]")
        plant_control_kdeficit()
        compare(argv[i + 1], argv[i + 2], at_build=("--at-build" in argv))
        return 0
    sys.stderr.write("usage: rc4_onechange.py --selftest | --compare <T-b> "
                     "<T-bR> [--at-build]\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
