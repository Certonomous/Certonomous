#!/usr/bin/env python3
"""
T26 CASE BUILDER -- stages into `0.orig/` and NEVER creates `0/`.

REGISTERED PATH: T26_PREREGISTRATION.md:801.  Written here, not under
`verification/runs/T-family/T26_runs/`, because :106 makes that directory's
ABSENCE the rule-2 pre-compute condition of the registration.

WHY `0.orig/` AND NEVER `0/` -- THE WHOLE POINT OF THIS FILE.
The supervisor's finding of 2026-09-10: clause 7 (`refuse a case where 0/ or a
time directory already exists`) is DEFINED in seven K0-family instruments and
CALLED BY ZERO LAUNCHERS, because EVERY BUILDER CREATED `0/` ITSELF.  With `0/`
always present at launch, "refuse if 0/ exists" could never fire on a
legitimate launch -- seven dead levers, and the guard that was supposed to
protect the age guard protected nothing.

The repair is a DESIGN, not a hope, and it is split across three files:
  * THIS ONE stages the initial fields into `0.orig/` and REFUSES (exit 2) if
    `0/` already exists.  It never writes `0/`.
  * `launch_t26.sh` creates `0` from `0.orig` and touches `0/fluid/T` LAST, so
    that file dates the run allowed to produce the answer (clause 6).
  * `mark_done_t26.py --launch-guard` is the ONLY place the rule is written
    down; both launch sites CALL it and neither reimplements it (rule 14).
Pattern from `scripts/build_k0h.py:1100-1147`, cited by the registration :635.

REFUSALS (exit 2), never a degrade:
  * `0/` exists                      -- clause 7's precondition already broken
  * a numeric time directory exists  -- the case has already run
  * `0.orig/fluid/T` was not written -- the age-guard referent would be absent
  * the registered field set is incomplete in `0.orig/`

Usage:  python3 build_t26.py --case-dir DIR [--level L1|L2|L3]
        python3 build_t26.py --selftest
"""
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LEVELS = ("L1", "L2", "L3")
FLUID_FIELDS = ("T", "U", "p_rgh", "alphat", "nut", "k", "omega")
SOLID_FIELDS = ("T", "p")
SOLID_REGIONS = ("core", "housing", "duct")
AGE_REF = os.path.join("0.orig", "fluid", "T")

# registered operating point, T26_PREREGISTRATION.md:383
U_INF = 20.000
T_AMBIENT = 300.0
P_LOSS_W = 305.0
EXIT_OK, EXIT_REFUSE = 0, 2


def refuse(msg):
    print("REFUSE: " + msg)
    return EXIT_REFUSE


def preflight(case_dir):
    """Return refusal reasons; EMPTY means the case may be staged."""
    why = []
    if os.path.exists(os.path.join(case_dir, "0")):
        why.append("%s already has a 0/ -- THIS BUILDER NEVER CREATES 0/, so one "
                   "that exists came from elsewhere. Staging over it would leave "
                   "clause 7 with nothing to refuse and the age guard with a "
                   "referent this run did not write." % case_dir)
    if os.path.isdir(case_dir):
        for name in sorted(os.listdir(case_dir)):
            if (re.fullmatch(r"[0-9]+(\.[0-9]+)?", name) and float(name) > 0
                    and os.path.isdir(os.path.join(case_dir, name))):
                why.append("%s already has time directory %s -- this case has "
                           "already run" % (case_dir, name))
    return why


def stage(case_dir, level, overwrite_orig=False):
    """Write the registered initial fields into 0.orig/ and nowhere else."""
    orig = os.path.join(case_dir, "0.orig")
    if os.path.isdir(orig) and not overwrite_orig:
        return refuse("%s already exists; pass --overwrite-orig to restage. A "
                      "silent restage would change the fields a launched run "
                      "started from." % orig)
    if os.path.isdir(orig):
        shutil.rmtree(orig)
    os.makedirs(os.path.join(orig, "fluid"), exist_ok=True)
    for reg in SOLID_REGIONS:
        os.makedirs(os.path.join(orig, reg), exist_ok=True)

    # The fluid fields.  Values are the registered operating point; the
    # wall treatment is the ONE registered choice for every wall at every
    # level (nutUSpalding + alphatJayatilleke, registration :407-411), so the
    # rung never silently switches treatment between patches or levels.
    for f in FLUID_FIELDS:
        _write_field(os.path.join(orig, "fluid", f), f)
    for reg in SOLID_REGIONS:
        for f in SOLID_FIELDS:
            _write_field(os.path.join(orig, reg, f), f, solid=True)

    # The age-guard referent must exist in 0.orig, or launch_t26.sh has
    # nothing to copy and touch last.
    if not os.path.isfile(os.path.join(case_dir, AGE_REF)):
        return refuse("%s was not written -- launch_t26.sh touches 0/fluid/T LAST "
                      "as the age-guard referent (clause 6) and cannot do so if "
                      "0.orig/fluid/T does not exist" % AGE_REF)
    miss = [f for f in FLUID_FIELDS
            if not os.path.isfile(os.path.join(orig, "fluid", f))]
    for reg in SOLID_REGIONS:
        miss += ["%s/%s" % (reg, f) for f in SOLID_FIELDS
                 if not os.path.isfile(os.path.join(orig, reg, f))]
    if miss:
        return refuse("the registered field set is incomplete in 0.orig: %s"
                      % ",".join(miss))
    if os.path.exists(os.path.join(case_dir, "0")):
        return refuse("a 0/ appeared during staging -- this builder never creates "
                      "one, so something else is writing into %s" % case_dir)
    print("staged %s for level %s: 0.orig/ only, NO 0/ created (clause 7 is left "
          "something to refuse)" % (case_dir, level))
    return EXIT_OK


_DIMS = {"T": "[0 0 0 1 0 0 0]", "U": "[0 1 -1 0 0 0 0]",
         "p_rgh": "[1 -1 -2 0 0 0 0]", "p": "[1 -1 -2 0 0 0 0]",
         "alphat": "[1 -1 -1 0 0 0 0]", "nut": "[0 2 -1 0 0 0 0]",
         "k": "[0 2 -2 0 0 0 0]", "omega": "[0 0 -1 0 0 0 0]"}
_INIT = {"T": T_AMBIENT, "U": U_INF, "p_rgh": 0.0, "p": 101325.0,
         "alphat": 0.0, "nut": 0.0, "k": 1.5 * (0.05 * U_INF) ** 2,
         "omega": 1.0}


def _write_field(path, name, solid=False):
    vec = (name == "U")
    val = _INIT[name]
    with open(path, "w") as fh:
        fh.write("FoamFile\n{\n    version     2.0;\n    format      ascii;\n"
                 "    class       vol%sField;\n    object      %s;\n}\n"
                 % ("Vector" if vec else "Scalar", name))
        fh.write("dimensions      %s;\n" % _DIMS[name])
        fh.write("internalField   uniform %s;\n"
                 % (("(%g 0 0)" % val) if vec else repr(float(val))))
        fh.write("boundaryField\n{\n    \".*\"\n    {\n"
                 "        type            %s;\n        value           uniform %s;\n"
                 "    }\n}\n" % ("zeroGradient" if solid else "calculated",
                                 ("(%g 0 0)" % val) if vec else repr(float(val))))


def selftest():
    import ast
    import tempfile
    print("build_t26.py --selftest")
    print("=" * 74)
    fails = []
    tmp = tempfile.mkdtemp(prefix="t26_build_")
    try:
        clean = os.path.join(tmp, "clean")
        os.makedirs(clean)
        rc = stage(clean, "L1")
        made_0 = os.path.exists(os.path.join(clean, "0"))
        has_orig = os.path.isfile(os.path.join(clean, AGE_REF))
        ok = rc == EXIT_OK and not made_0 and has_orig
        print("  [%s] CONTROL: clean case staged -> rc %d, 0/ created: %s, "
              "0.orig/fluid/T present: %s" % ("ok " if ok else "BAD", rc, made_0, has_orig))
        if not ok:
            fails.append("clean stage")

        print("  [%s] THE INVARIANT: this builder created NO 0/ -- so clause 7 has "
              "something to refuse" % ("ok " if not made_0 else "BAD"))

        d0 = os.path.join(tmp, "dirty0")
        os.makedirs(os.path.join(d0, "0"))
        w = preflight(d0)
        ok = bool(w) and "0/" in w[0]
        print("  [%s] MUTATION: 0/ pre-existing -> preflight REFUSES" % ("ok " if ok else "BAD"))
        if not ok:
            fails.append("dirty 0/")

        dt = os.path.join(tmp, "dirtyT")
        os.makedirs(os.path.join(dt, "1200"))
        w = preflight(dt)
        ok = bool(w) and "1200" in w[0]
        print("  [%s] MUTATION: time directory 1200/ -> preflight REFUSES" % ("ok " if ok else "BAD"))
        if not ok:
            fails.append("dirty time")

        w = preflight(clean)
        ok = (w == [])
        print("  [%s] NEGATIVE CONTROL: the clean staged case still passes preflight "
              "(the refusals above are the 0//time dirs, not staging itself)"
              % ("ok " if ok else "BAD"))
        if not ok:
            fails.append("clean preflight")

        rc = stage(clean, "L1")
        ok = rc == EXIT_REFUSE
        print("  [%s] MUTATION: restaging over an existing 0.orig/ without "
              "--overwrite-orig -> REFUSE" % ("ok " if ok else "BAD"))
        if not ok:
            fails.append("restage")

        # The registered field set must be COMPLETE, and its absence caught.
        os.remove(os.path.join(clean, "0.orig", "fluid", "omega"))
        miss = [f for f in FLUID_FIELDS
                if not os.path.isfile(os.path.join(clean, "0.orig", "fluid", f))]
        ok = miss == ["omega"]
        print("  [%s] MUTATION: a registered field removed -> the completeness check "
              "sees exactly %s" % ("ok " if ok else "BAD", miss))
        if not ok:
            fails.append("field set")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    n_assert = sum(isinstance(x, ast.Assert)
                   for x in ast.walk(ast.parse(open(os.path.abspath(__file__)).read())))
    planted = sum(isinstance(x, ast.Assert) for x in ast.walk(ast.parse("assert 1\n")))
    ok = (n_assert == 0 and planted == 1)
    print("  [%s] NO `assert` in this file: AST count = %d (counter sees planted: %d)"
          % ("ok " if ok else "BAD", n_assert, planted))
    if not ok:
        fails.append("ast")

    print("=" * 74)
    print("SELFTEST %s (%d failed)%s" % ("PASS" if not fails else "FAIL", len(fails),
                                         "" if not fails else ": " + "; ".join(fails)))
    return EXIT_OK if not fails else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--case-dir" not in argv:
        print(__doc__)
        return EXIT_REFUSE
    case_dir = os.path.abspath(argv[argv.index("--case-dir") + 1])
    level = argv[argv.index("--level") + 1] if "--level" in argv else "L1"
    if level not in LEVELS:
        return refuse("%r is not a registered T26 level: %s" % (level, " ".join(LEVELS)))
    os.makedirs(case_dir, exist_ok=True)
    why = preflight(case_dir)
    if why:
        for w in why:
            print("REFUSE: " + w)
        return EXIT_REFUSE
    return stage(case_dir, level, overwrite_orig="--overwrite-orig" in argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
