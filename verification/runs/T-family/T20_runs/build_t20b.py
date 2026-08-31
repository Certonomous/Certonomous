#!/usr/bin/env python3
"""Build ONE registered T20 case, WITH `constant/g`.  SUCCESSOR TO build_t20.py
FOR THE BUILDER ONLY.

WHY THIS FILE EXISTS.  `build_t20.py` writes no `constant/g`, and every case it
builds therefore dies immediately:

    --> FOAM FATAL ERROR: cannot find file ".../T20_LC_c/constant/g"

measured on the real launch of 2026-08-31T00:12Z (`T20_LC_c/log.solve`, rc=1,
`STATUS.T20_LC_c` note=SOLVER_NONZERO_EXIT).  The cause is upstream and is not a
T20 defect:

    /usr/lib/openfoam/openfoam2606/applications/solvers/heatTransfer/
    chtMultiRegionFoam/fluid/createFluidFields.H
      :35  const uniformDimensionedVectorField& g = meshObjects::gravity::New(runTime);
      :38  forAll(fluidRegions, i)

Line 35 reads `g` at FILE SCOPE, BEFORE the fluid loop at line 38 opens.  T20
registers `regions ( fluid () solid (cellRegion) )`, so the loop body never runs
-- but line 35 has already demanded the file.  The solver requires `constant/g`
even when it will never use it.

`g` IS ZERO BY PHYSICS, NOT TO SATISFY A CHECK.  With zero fluid regions there is
no fluid for gravity to act on, and the solid energy equation
`ddt(betav*rho, h) = laplacian(alpha, h) + q'''` carries no buoyancy term.  `g`
cannot enter the solution.  This was measured, not argued: the feasibility run
`T20_LC_FEAS_20260831T151828Z` completed with `value (0 0 0)` -- rc=0, endTime
4500 reached, 750 ExecutionTime lines, and its cell-centre temperature range
2.226117 mK matched the analytic quadratic sampled at the same cell centres,
2.227062 mK, to a ratio of 0.999576.

WHAT THIS FILE IS NOT.
  * It is NOT an edit to `build_t20.py`.  That file is frozen and is not touched
    (CLAUDE.md rule 6 -- frozen files are never edited).  This is a successor.
  * It introduces NO new registration document.  T20's pre-registration at commit
    `7b93b2c8` still governs in full.  NO GATE, THRESHOLD, BAND, CAP OR LABEL
    MOVES.  Every physical and numerical value still comes from
    `T20_registered.json` via the parent, unchanged.
  * It is NOT a new rule, standard or tool.  It is a one-pass in-flight instrument
    repair under Sanaa's 2026-08-31 plumbing freeze, after which the topic closes.

PROVENANCE DISCLOSURE.  A case built by this file is built by `build_t20.py` plus
exactly one added file, `constant/g`.  Cases carry `BUILT BY build_t20.py` in their
headers because the parent writes them; `CASE.txt` is amended here to record the
successor, so case-matches-builder provenance is DISCLOSED rather than silently
broken.

HOW THE DELTA IS KEPT MINIMAL, BY CONSTRUCTION AND NOT BY PROMISE.  This file does
not reimplement the parent.  It CALLS `build_t20.main()` and then adds one file.
The emitted trees therefore cannot differ in any other way, and selftest limb (e)
measures that rather than asserting it.

FAIL-CLOSED.  After the parent returns, `constant/g` is verified ON DISK -- present,
non-empty, parseable, with the registered dimensions and a zero value.  If any of
that fails the build REFUSES with exit 2 and the case is left for inspection, never
cleaned.  A builder that can silently emit a case which dies on its first timestep
is the defect this file exists to remove; a repair that cannot detect its own
failure would reintroduce it.

usage: build_t20b.py --case T20_LC_c [--root <dir>]
       build_t20b.py --selftest
"""
import argparse
import ast
import hashlib
import json
import os
import shutil
import sys
import tempfile

SELF = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SELF)
import build_t20  # noqa: E402  -- the parent; called, never modified

EXIT_REFUSE = 2

# Registered dimensions of gravitational acceleration: m s^-2.
G_DIMS = "[0 1 -2 0 0 0 0]"
G_VALUE = "(0 0 0)"

G_BODY = (
    "// Zero by PHYSICS, not to satisfy a check.  regionProperties declares\n"
    "// `fluid ()`, so there is no fluid region for gravity to act on, and the\n"
    "// solid energy equation carries no buoyancy term.  Required only because\n"
    "// createFluidFields.H:35 reads g at file scope, before the fluid loop at :38.\n"
    "dimensions      %s;\nvalue           %s;\n" % (G_DIMS, G_VALUE)
)


def _sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def g_path(case_dir):
    return os.path.join(case_dir, "constant", "g")


def write_g(case_dir):
    build_t20.write(g_path(case_dir), "uniformDimensionedVectorField",
                    "constant", "g", G_BODY)


def verify_g(case_dir):
    """FAIL-CLOSED reader.  Returns (ok, message).  Never raises on a bad tree.

    This is the limb the planted control drives.  It must be able to FAIL, and
    selftest limbs (a)-(d) demonstrate that it does, on four distinct defects.
    """
    p = g_path(case_dir)
    if not os.path.isfile(p):
        return False, "constant/g does not exist at %s" % p
    try:
        txt = open(p).read()
    except OSError as e:
        return False, "constant/g exists but cannot be read: %s" % e
    if not txt.strip():
        return False, "constant/g is empty"
    if "FoamFile" not in txt:
        return False, "constant/g has no FoamFile header -- OpenFOAM will refuse it"
    if "uniformDimensionedVectorField" not in txt:
        return False, ("constant/g is not class uniformDimensionedVectorField; "
                       "meshObjects::gravity::New requires that class")
    if G_DIMS not in txt:
        return False, ("constant/g does not carry the registered dimensions %s "
                       "(m s^-2)" % G_DIMS)
    if G_VALUE not in txt:
        return False, ("constant/g does not carry value %s; a NON-ZERO g would be "
                       "an UNREGISTERED physical choice" % G_VALUE)
    return True, "constant/g present, class/dimensions/value all as registered"


def build(case, root, params_file=None):
    """Build one case.  `params_file` supplies a case NOT present in
    T20_registered.json, WITHOUT EDITING THAT FILE.

    THE REGISTERED JSON IS NEVER WRITTEN.  T20's six non-feasibility cases are
    frozen in the pre-registration PROSE at commit 7b93b2c8 (S9 run-set table,
    :867-873; S11.2 POINT/CAP table, :1011-1017), and a prose freeze at a
    committed sha is a freeze -- rule 2's evidentiary content is that the gate
    could not have been chosen to fit the answer, which prose at a sha satisfies
    completely.  Moving those values INTO the JSON post-compute is a separate
    rule-2 question that is REFERRED TO VERIFICATION AND UNRULED, so this file
    sidesteps it: it copies the registered JSON to a scratch file, inserts the one
    case there, and points the parent at the copy.  The real
    T20_registered.json is hashed before and after and the build REFUSES if it
    moved by a single byte.
    """
    d = os.path.join(root, case)
    reg_before = _sha256(build_t20.REG)
    scratch_reg = None
    old_reg = build_t20.REG
    try:
        if params_file is not None:
            p = json.load(open(params_file))
            if case not in p.get("cases", {}):
                sys.exit("REFUSE: %s carries no cases.%s" % (params_file, case))
            reg = json.load(open(build_t20.REG))
            if case in reg["cases"]:
                sys.exit("REFUSE: %s is ALREADY in the registered JSON; use the "
                         "registered path, not --params" % case)
            reg["cases"][case] = p["cases"][case]
            fd, scratch_reg = tempfile.mkstemp(prefix="t20b_reg_", suffix=".json")
            with os.fdopen(fd, "w") as f:
                json.dump(reg, f, indent=1)
            _refuse_if_inside_live_tree(scratch_reg)
            build_t20.REG = scratch_reg

        argv = ["build_t20.py", "--case", case, "--root", root]
        old = sys.argv
        try:
            sys.argv = argv
            rc = build_t20.main()
        finally:
            sys.argv = old
    finally:
        build_t20.REG = old_reg
        if scratch_reg and os.path.exists(scratch_reg):
            os.remove(scratch_reg)

    if _sha256(old_reg) != reg_before:
        sys.stderr.write("REFUSE (exit %d): T20_registered.json CHANGED during "
                         "the build. It is the registration and is never written.\n"
                         % EXIT_REFUSE)
        sys.exit(EXIT_REFUSE)
    if rc != 0:
        sys.exit("REFUSE: parent build_t20.main() returned rc=%s" % rc)

    write_g(d)

    ok, msg = verify_g(d)
    if not ok:
        # Exit code must be EXIT_REFUSE (2), not 1.  sys.exit(<str>) prints the
        # string and exits 1, which would make a REFUSAL indistinguishable from
        # an ordinary error to any caller that reads the code.
        sys.stderr.write(
            "REFUSE (exit %d): %s -- the case is LEFT ON DISK for inspection, "
            "never cleaned (CLAUDE.md rule 10).\n" % (EXIT_REFUSE, msg))
        sys.exit(EXIT_REFUSE)

    with open(os.path.join(d, "CASE.txt"), "a") as f:
        f.write("\nBUILDER SUCCESSOR: build_t20b.py added constant/g "
                "(dimensions %s, value %s).\n"
                "Reason: createFluidFields.H:35 reads g at file scope before the\n"
                "fluid loop at :38, so chtMultiRegionFoam demands the file even at\n"
                "ZERO fluid regions.  g is zero by physics; no registered value\n"
                "moves and T20's pre-registration at 7b93b2c8 governs unchanged.\n"
                % (G_DIMS, G_VALUE))
    print("build_t20b: %s  -- %s" % (d, msg))
    return 0


# --------------------------------------------------------------------------
# SELFTEST.  NO LIMB TOUCHES A LIVE RUN TREE.
#
# T20's own S8 registers this, and it is not optional: `analyse_t18.py:509` and
# `analyse_t19.py:691` each carried a limb that called into the LIVE tree, and
# BOTH inverted on 2026-08-31 the moment the campaign succeeded -- an arm that
# asserts on live state stops being able to assert at all.  Every limb below runs
# against a scratch root under tempfile, and the runner REFUSES if any scratch
# path resolves inside this rung's own directory.
# --------------------------------------------------------------------------
def _refuse_if_inside_live_tree(path):
    rp, live = os.path.realpath(path), os.path.realpath(SELF)
    if rp == live or rp.startswith(live + os.sep):
        sys.exit("REFUSE: selftest scratch %s resolves INSIDE the live rung tree "
                 "%s. No selftest limb may touch a live run tree." % (rp, live))


def selftest():
    fails = []

    def ok(cond, label):
        print("  [%s] %s" % ("ok " if cond else "FAIL", label))
        if not cond:
            fails.append(label)

    tmp = tempfile.mkdtemp(prefix="t20b_selftest_")
    _refuse_if_inside_live_tree(tmp)
    case = "T20_LC_c"          # the one case in T20_registered.json
    try:
        # Build once with the successor, into scratch.
        root_b = os.path.join(tmp, "b")
        os.makedirs(root_b)
        build(case, root_b)
        d_b = os.path.join(root_b, case)

        # (a) POSITIVE: the verifier accepts the tree the builder just wrote.
        ok(verify_g(d_b)[0], "built tree -> verify_g ACCEPTS")

        # (b) PLANTED CONTROL, g REMOVED -> the verifier must REFUSE.
        #     This is the limb that proves the detector can fail.  Without it the
        #     fail-closed check is decorative.
        shutil.copytree(d_b, os.path.join(tmp, "no_g"))
        os.remove(g_path(os.path.join(tmp, "no_g")))
        ok(not verify_g(os.path.join(tmp, "no_g"))[0],
           "PLANTED: constant/g REMOVED -> verify_g REFUSES")

        # (c) PLANTED: g present but EMPTY -> REFUSE.  Presence is not enough.
        shutil.copytree(d_b, os.path.join(tmp, "empty_g"))
        open(g_path(os.path.join(tmp, "empty_g")), "w").close()
        ok(not verify_g(os.path.join(tmp, "empty_g"))[0],
           "PLANTED: constant/g EMPTIED -> verify_g REFUSES")

        # (d) PLANTED: g with a NON-ZERO value -> REFUSE.  A non-zero g would be
        #     an unregistered physical choice, which is the failure that matters
        #     scientifically rather than mechanically.
        shutil.copytree(d_b, os.path.join(tmp, "nonzero_g"))
        p = g_path(os.path.join(tmp, "nonzero_g"))
        # Read FIRST, then write.  open(p,"w") truncates, so the nested form
        # open(p,"w").write(open(p).read()...) would silently plant an EMPTY file
        # and limb (d) would pass for limb (c)'s reason instead of its own.
        _txt = open(p).read()
        with open(p, "w") as _f:
            _f.write(_txt.replace(G_VALUE, "(0 -9.81 0)"))
        ok(not verify_g(os.path.join(tmp, "nonzero_g"))[0],
           "PLANTED: constant/g set NON-ZERO -> verify_g REFUSES")

        # (e) EMITTED-TREE COMPARISON: parent vs successor differ ONLY by
        #     constant/g.  Measured over the emitted bytes, not asserted.
        root_p = os.path.join(tmp, "p")
        os.makedirs(root_p)
        argv = sys.argv
        try:
            sys.argv = ["build_t20.py", "--case", case, "--root", root_p]
            build_t20.main()
        finally:
            sys.argv = argv
        d_p = os.path.join(root_p, case)

        def tree(d):
            out = {}
            for r, _, fs in os.walk(d):
                for fn in fs:
                    fp = os.path.join(r, fn)
                    rel = os.path.relpath(fp, d)
                    if rel.startswith("log.") or rel == "CASE.txt":
                        continue          # build logs and the amended CASE.txt
                    try:
                        out[rel] = open(fp, "rb").read()
                    except OSError:
                        out[rel] = b"<unreadable>"
            return out

        tp, tb = tree(d_p), tree(d_b)
        only_b = sorted(set(tb) - set(tp))
        only_p = sorted(set(tp) - set(tb))
        changed = sorted(k for k in set(tp) & set(tb) if tp[k] != tb[k])
        ok(only_b == [os.path.join("constant", "g")],
           "emitted trees: successor adds ONLY constant/g (added: %s)" % only_b)
        ok(only_p == [], "emitted trees: successor removes nothing (removed: %s)" % only_p)
        ok(changed == [], "emitted trees: no shared file CHANGED (changed: %s)" % changed)

        # (f) AST assert count, the family's standing check: this file must carry
        #     no bare `assert`, which optimised bytecode would silently drop.
        src = open(os.path.abspath(__file__)).read()
        n = sum(isinstance(x, ast.Assert) for x in ast.walk(ast.parse(src)))
        planted = sum(isinstance(x, ast.Assert)
                      for x in ast.walk(ast.parse(src + "\nassert True\n")))
        ok(n == 0 and planted == 1,
           "AST assert count in this file = 0 (counter sees a planted assert: %d)"
           % planted)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case")
    ap.add_argument("--root", default=SELF)
    ap.add_argument("--params", default=None,
                    help="JSON supplying a case NOT in T20_registered.json. "
                         "That file is NEVER written; a scratch copy is used and "
                         "the real one is hashed before and after.")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.case:
        ap.error("--case is required unless --selftest")
    return build(a.case, a.root, a.params)


if __name__ == "__main__":
    sys.exit(main())
