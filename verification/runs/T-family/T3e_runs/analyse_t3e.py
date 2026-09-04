#!/usr/bin/env python3
"""analyse_t3e.py -- THE GRADING PATH FOR T3e.

REGISTERED BY docs/campaigns/T-family/T3e_PREREGISTRATION.md.

WHAT T3e MEASURES.  T3d finished with |U| at relative = 3.68937e-06 against
tol = 1e-06 -- 3.69x over, NOT CONVERGED -- and purgeWrite 2 left ONE pair on
disk, so whether that non-convergence is DECAYING or STALLED was undeterminable.
T3e runs 8,000 more iterations at purgeWrite 0, giving four checkpoints and
THREE consecutive pairs: the minimum that can tell a trend from a stall.

THE READERS ARE IMPORTED, NEVER REIMPLEMENTED.
    T1C.iterative_convergence(case, "T")        <- analyse_t1c.py
    A3.iterative_convergence_vector(case, "U")  <- analyse_t3.py
These are the same functions the T3 ladder grades on.  They read a case's LAST
TWO checkpoints, so to read three specific pairs this file builds a two-checkpoint
VIEW per pair (symlinks, no copies, nothing written into the case) and calls the
frozen reader on each view.  No convergence logic is reimplemented here.

D-1: THIS GRADER'S INPUT CONTRACT IS CHECKED AND NAMED.  T3d died because its
pinned builder wrote prose where its pinned grader read seven numeric keys.  This
file READS THE KEYS IT NEEDS UP FRONT, NAMES EVERY ONE IT READ, and REFUSES at
exit 2 naming the missing key.  Charter section 2ap requires that contract be
rehearsed -- one success leg and one corruption leg -- before the registration
freezes; --selftest drives both.

D-J1: EVERY convergence_state IS EMITTED WITH ITS field_range BESIDE IT.  T3d's
gate JSON would have carried the word without the denominator.  A zero
denominator returns NOT A RESULT -- never 0.0, never a substituted value.

RULE 5.  NO ROACHE TRIPLE IS FORMED: one mesh, one refinement.  No observed
order, no GCI, no Richardson extrapolate is computed, quoted or derivable, and
EVERY NUMBER THIS FILE PRODUCES CARRIES NO DISCRETISATION BOUND AT ALL.  Clause
(1) IS reached and is applied.

EXIT CODES
  0  PASS -- and only PASS
  1  GATE REACHED, GATE FAIL or NOT A RESULT
  2  REFUSAL -- a missing key, an unreadable field, a control that did not fire
"""
import json
import os
import sys
import tempfile

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
T3 = os.path.normpath(os.path.join(HERE, "..", "T3_runs"))
T1 = os.path.normpath(os.path.join(HERE, "..", "T1_runs"))
sys.path[:0] = [T3, T1]
import analyse_t1c as T1C                                        # noqa: E402
import analyse_t3 as A3                                          # noqa: E402

EXIT_PASS, EXIT_FAIL, EXIT_REFUSE = 0, 1, 2

REQUIRED_KEYS = ("H", "nu", "Pr", "Prt", "dTdn_wall", "T_in", "U_in", "endTime")
PAIRS = (("2000", "4000"), ("4000", "6000"), ("6000", "8000"))
TOL = 1.0e-06                     # inherited from T3d, UNCHANGED
PLANT = 1.234e-03

PASS, GATE_REACHED, GATE_FAIL = "PASS", "GATE REACHED", "GATE FAIL"
NOT_A_RESULT, REPORTED = "NOT A RESULT", "REPORTED"


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def read_keys(case_dir):
    """Read REQUIRED_KEYS from CASE.txt.  Names every key read.  Refuses at
    exit 2 naming the FIRST missing key -- D-1's repair, and the thing the
    corruption leg of the section 2ap rehearsal drives."""
    p = os.path.join(case_dir, "CASE.txt")
    if not os.path.isfile(p):
        refuse("no CASE.txt at %s -- the grader's inputs live there" % p)
    kv = {}
    for line in open(p):
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("="):
            continue
        parts = s.split()
        if len(parts) >= 2:
            kv.setdefault(parts[0], parts[1])
    got = {}
    for k in REQUIRED_KEYS:
        if k not in kv:
            refuse("%s absent from %s -- this grader reads %d keys (%s) and the "
                   "builder must write them as a STRUCTURED key-value block. "
                   "This is defect D-1, the one that cost T3d 4,723.200 core-min."
                   % (k, p, len(REQUIRED_KEYS), " ".join(REQUIRED_KEYS)))
        try:
            got[k] = float(kv[k])
        except ValueError:
            refuse("%s in %s is %r, which is not numeric" % (k, p, kv[k]))
    return got


def pair_view(case_dir, a, b, scratch):
    """A two-checkpoint VIEW of the case, so the frozen reader -- which reads a
    case's last two checkpoints -- reads the pair we want.  Symlinks only:
    nothing is copied and NOTHING IS WRITTEN INTO THE CASE."""
    for t in (a, b):
        d = os.path.join(case_dir, t)
        if not os.path.isdir(d):
            refuse("checkpoint %s absent from %s -- purgeWrite 0 is registered "
                   "so every checkpoint should survive; a missing one is a "
                   "finding, not a gap to route around" % (t, case_dir))
    v = os.path.join(scratch, "view_%s_%s" % (a, b))
    for t in (a, b):
        os.makedirs(os.path.join(v, t), exist_ok=True)
        for f in os.listdir(os.path.join(case_dir, t)):
            src = os.path.join(case_dir, t, f)
            dst = os.path.join(v, t, f)
            if not os.path.exists(dst):
                os.symlink(src, dst)
    return v


def measure(view):
    """Both limbs through the FROZEN readers, with the denominator kept."""
    cT = T1C.iterative_convergence(view, "T")
    cU = A3.iterative_convergence_vector(view, "U")
    return cT, cU


def emit(tag, c):
    """D-J1: a state NEVER leaves this function without its denominator."""
    rng = c.get("field_range")
    dmax = c.get("max_change")
    rel = c.get("relative")
    if rng is None:
        return dict(field=tag, state=NOT_A_RESULT, field_range=None,
                    max_change=dmax, relative=None,
                    why="field_range is not measurable, so no ratio exists")
    if rng == 0.0:
        return dict(field=tag, state=NOT_A_RESULT, field_range=0.0,
                    max_change=dmax, relative=None,
                    why="denominator is exactly zero: the ratio is UNDEFINED "
                        "rather than small. NOT A RESULT, never 0.0 (D-J1).")
    return dict(field=tag, state=c.get("state"), field_range=rng,
                max_change=dmax, relative=rel, why=None)


def control(case_dir, scratch, out):
    """Rule 3.  A zero from a reader not shown able to see a non-zero is not
    evidence.  Plant into a COPY, read back FROM DISK through the same frozen
    reader, refuse if unseen."""
    a, b = PAIRS[-1]
    v = pair_view(case_dir, a, b, os.path.join(scratch, "ctl"))
    base = T1C.iterative_convergence(v, "T")
    tp = os.path.join(v, b, "T")
    real = os.path.realpath(tp)
    os.unlink(tp)
    txt = open(real).read().split("\n")
    start = None
    for i in range(len(txt) - 2):
        if txt[i].strip().isdigit() and txt[i + 1].strip() == "(":
            start = i + 2
            break
    if start is None:
        refuse("rule-3 control: cannot locate the internal field to plant into")
    before = float(txt[start].strip())
    txt[start] = repr(before + PLANT)
    open(tp, "w").write("\n".join(txt))
    got = T1C.iterative_convergence(v, "T")
    moved = abs((got.get("max_change") or 0.0) - (base.get("max_change") or 0.0))
    out("  rule-3 control: planted %.6e K into the later checkpoint, read back "
        "from disk" % PLANT)
    out("    reader max_change moved by %.6e   %s"
        % (moved, "PLANT SEEN" if moved > PLANT / 2 else "*** PLANT INVISIBLE ***"))
    if moved <= PLANT / 2:
        refuse("rule-3 control: the reader did not see a %.6e K plant, so any "
               "zero it reports is not evidence" % PLANT)


def grade(case_dir, out=print):
    keys = read_keys(case_dir)
    out("keys read from CASE.txt (every one named, D-1): %s"
        % "  ".join("%s=%g" % (k, keys[k]) for k in REQUIRED_KEYS))
    scratch = tempfile.mkdtemp(prefix="t3e_")
    rows = []
    try:
        control(case_dir, scratch, out)
        out("")
        for a, b in PAIRS:
            v = pair_view(case_dir, a, b, scratch)
            cT, cU = measure(v)
            rT, rU = emit("T", cT), emit("|U|", cU)
            for r in (rT, rU):
                out("  pair (%s,%s)  %-4s state=%-14s field_range=%s  "
                    "max_change=%s  relative=%s"
                    % (a, b, r["field"], r["state"],
                       "%.6g" % r["field_range"] if r["field_range"] is not None else "None",
                       "%.6g" % r["max_change"] if r["max_change"] is not None else "None",
                       "%.6g" % r["relative"] if r["relative"] is not None else "None"))
                if r["why"]:
                    out("        %s" % r["why"])
            rows.append(dict(pair=[a, b], T=rT, U=rU))
    finally:
        pass
    return keys, rows, scratch


def verdict(rows, out=print):
    out("")
    urel = [r["U"]["relative"] for r in rows]
    if any(u is None for u in urel):
        out("P-1  %s -- a |U| ratio was undefined, so no trend exists" % NOT_A_RESULT)
        return NOT_A_RESULT
    mono = all(urel[i] > urel[i + 1] for i in range(len(urel) - 1))
    out("P-1  |U| relative across the three pairs: %s"
        % "  >  ".join("%.6g" % u for u in urel))
    out("     strictly decaying: %s" % ("YES" if mono else "NO"))
    tconv = all(r["T"]["state"] == "CONVERGED" for r in rows)
    out("P-2  T CONVERGED on every pair: %s" % ("YES" if tconv else "NO"))
    last = urel[-1]
    out("")
    out("RULE 5: NO TRIPLE IS FORMED (one mesh, one refinement). No observed "
        "order, no GCI,")
    out("        no Richardson extrapolate. EVERY NUMBER ABOVE CARRIES NO "
        "DISCRETISATION BOUND.")
    out("        Clause (1) IS reached and is applied below.")
    out("")
    if last <= TOL:
        out("RUNG T3e %s -- |U| reached %.6g <= tol %.6g at the last pair; the "
            "level is iteratively converged." % (PASS, last, TOL))
        return PASS
    if mono:
        out("RUNG T3e %s -- |U| did NOT reach tol (%.6g > %.6g), but P-1 HOLDS: "
            "the non-convergence is DECAYING, not stalled." % (GATE_REACHED, last, TOL))
        out("           Under rule 5 clause (1) the level is not iteratively "
            "converged, so NO ladder row is graded from it.")
        return GATE_REACHED
    out("RUNG T3e %s -- P-1 FALSIFIED: |U| is not decaying across the three "
        "pairs, so the" % NOT_A_RESULT)
    out("           non-convergence is STALLED. Under rule 5 clause (1) the "
        "level is NOT A RESULT,")
    out("           and the item routes under charter section 2an to numerical "
        "rule-out.")
    return NOT_A_RESULT


def selftest():
    """THE SECTION 2ap PAIRED-PIN REHEARSAL: one SUCCESS leg, one CORRUPTION leg."""
    import shutil
    ok = [True]

    def chk(cond, msg):
        ok[0] = ok[0] and bool(cond)
        print("  [%s] %s" % ("PASS" if cond else "FAIL", msg))

    tmp = tempfile.mkdtemp(prefix="t3e_selftest_")
    case = os.path.join(tmp, "R_fy")
    os.makedirs(case)
    # a synthetic CASE.txt in the BUILDER'S OWN format
    open(os.path.join(case, "CASE.txt"), "w").write(
        "case              R_fy\n"
        "H                 0.038\nnu                1.5e-05\n"
        "Pr                0.71\nPrt               0.85\n"
        "dTdn_wall         10000.0\nT_in              300.0\n"
        "U_in              10.35\nendTime           8000\n"
        "# prose appended below the block\n")
    # synthetic fields: T decaying under tol, |U| decaying but above it
    n = 24
    for i, t in enumerate(("2000", "4000", "6000", "8000")):
        d = os.path.join(case, t)
        os.makedirs(d)
        base = 300.0 + 50.0 * (i * 0.0)          # range 50 K, constant
        Tv = [base + 50.0 * (j / (n - 1.0)) + 1e-4 * (0.5 ** i) for j in range(n)]
        open(os.path.join(d, "T"), "w").write(_scalar(Tv, t, "T"))
        Uv = [(1.0 + 10.0 * (j / (n - 1.0)) + 1e-3 * (0.5 ** i), 0.0, 0.0)
              for j in range(n)]
        open(os.path.join(d, "U"), "w").write(_vector(Uv, t))

    print("SECTION 2ap PAIRED-PIN REHEARSAL")
    print(" LEG 1 -- SUCCESS: the builder's real key block drives the grader")
    keys = read_keys(case)
    chk(len(keys) == len(REQUIRED_KEYS),
        "grader read all %d keys and named them: %s"
        % (len(REQUIRED_KEYS), " ".join(REQUIRED_KEYS)))
    _k, rows, scratch = grade(case, out=lambda s: None)
    chk(len(rows) == 3, "grader ran to three graded pairs on synthetic fields")
    chk(all(r["T"]["field_range"] not in (None, 0.0) for r in rows),
        "every T state carries a NON-ZERO field_range beside it (D-J1)")
    chk(all(r["U"]["field_range"] not in (None, 0.0) for r in rows),
        "every |U| state carries a NON-ZERO field_range beside it (D-J1)")
    v = verdict(rows, out=lambda s: None)
    chk(v in (PASS, GATE_REACHED, NOT_A_RESULT), "grader reached a verdict: %s" % v)
    shutil.rmtree(scratch, ignore_errors=True)

    print(" LEG 2 -- CORRUPTION: one key removed, the grader MUST refuse at exit 2")
    bad = os.path.join(tmp, "R_fy_corrupt")
    shutil.copytree(case, bad)
    txt = [l for l in open(os.path.join(bad, "CASE.txt"))
           if not l.startswith("H ")]
    open(os.path.join(bad, "CASE.txt"), "w").writelines(txt)
    pid = os.fork()
    if pid == 0:
        sys.stdout = open(os.devnull, "w")
        try:
            read_keys(bad)
        except SystemExit as e:
            os._exit(e.code if isinstance(e.code, int) else 1)
        os._exit(0)
    _w, st = os.waitpid(pid, 0)
    rc = (st >> 8) & 0xFF
    chk(rc == EXIT_REFUSE,
        "H removed -> grader REFUSED at exit %d (expected %d). A rehearsal that "
        "only shows success does not show the check is live." % (rc, EXIT_REFUSE))

    shutil.rmtree(tmp, ignore_errors=True)
    print("\nREHEARSAL %s" % ("PASSED -- both legs" if ok[0] else "FAILED"))
    return 0 if ok[0] else 1


def _scalar(vals, loc, obj):
    return ("FoamFile\n{\n    version 2.0;\n    format ascii;\n"
            "    class volScalarField;\n    location \"%s\";\n    object %s;\n}\n"
            "\ndimensions [0 0 0 1 0 0 0];\n\ninternalField nonuniform List<scalar>\n"
            "%d\n(\n%s\n)\n;\n\nboundaryField\n{\n}\n"
            % (loc, obj, len(vals), "\n".join(repr(float(v)) for v in vals)))


def _vector(vals, loc):
    return ("FoamFile\n{\n    version 2.0;\n    format ascii;\n"
            "    class volVectorField;\n    location \"%s\";\n    object U;\n}\n"
            "\ndimensions [0 1 -1 0 0 0 0];\n\ninternalField nonuniform List<vector>\n"
            "%d\n(\n%s\n)\n;\n\nboundaryField\n{\n}\n"
            % (loc, len(vals), "\n".join("(%r %r %r)" % v for v in vals)))


def main(argv):
    if "--selftest" in argv:
        return selftest()
    root = argv[argv.index("--root") + 1] if "--root" in argv else os.path.join(T3, "R_fy")
    case_dir = os.path.abspath(root)
    print("=" * 74)
    print("T3e -- |U| trend on three consecutive pairs; tol = %g (T3d's, unchanged)" % TOL)
    print("case: %s" % case_dir)
    print("=" * 74)
    keys, rows, scratch = grade(case_dir)
    v = verdict(rows)
    out = os.path.join(HERE, "gate_t3e.json")
    json.dump(dict(rung="T3e", case=case_dir, tol=TOL, keys=keys,
                   rows=rows, verdict=v,
                   triple="NONE -- one mesh; rule 5 clause (1) only",
                   gci="NOT COMPUTED, NOT QUOTED, NOT DERIVABLE"),
              open(out, "w"), indent=2)
    print("\nwrote %s" % out)
    return EXIT_PASS if v == PASS else EXIT_FAIL


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
