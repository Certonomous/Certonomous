#!/usr/bin/env python3
"""check_fo_table_is_evidence.py -- REFUSE an OpenFOAM function-object table
that cannot be evidence, and say which of the two ways it failed.

WHY THIS EXISTS.  Measured on T5 (heat-transfer, 2026-09-03), preserved at
`verification/runs/T-family/T5_runs/YPLUS_RECOVERABILITY_2026-09-03/`.  Two
independent defects each produce a file on disk that LOOKS configured and
connected, with no error and a clean exit code:

  (1) ZERO DATA ROWS.  A `writeControl`/`writeInterval` pair copied from an
      `execute()`-emitting function object onto a `write()`-emitting one
      silently means NEVER.  T5's `yPlus` and `wallHeatFlux` carried the
      IDENTICAL control; `wallHeatFlux` wrote 30,000 rows and `yPlus` wrote 0.
      The tell is a `.dat` with headers and no data rows beside a sibling `.dat`
      with thousands.

  (2) EVERY VALUE EXACTLY ZERO.  `postProcess -func yPlus` on a case whose
      turbulence model is not in the registry writes a FULL, WELL-FORMED table
      of zeros and EXITS 0.  The warning is on stderr; the file is not marked.
      A lane that ran the obvious command and filed the result would have graded
      a registered gate on fabricated zeros.  `CLAUDE.md` rule 3: A ZERO FROM A
      READER NOT SHOWN ABLE TO SEE A NON-ZERO IS NOT EVIDENCE.

SCOPE, stated so nobody over-reads a refusal.  This instrument GRADES NOTHING.
It answers one question -- "could this table be evidence at all?" -- and it
answers it restrictively.  A quantity that is LEGITIMATELY identically zero is
refused here too, deliberately: that case needs its own registered
justification, not this instrument's silence.

Exit codes:  0 admissible   2 REFUSED   3 usage error.
Never a bare `assert` -- the lab has measured that assert-based guards vanish
under `python3 -O` (L-475).  Every check below raises or exits.
"""

import os
import sys
import tempfile

EXIT_OK = 0
EXIT_REFUSE = 2
EXIT_USAGE = 3


class Refusal(Exception):
    """Raised when a table cannot be evidence.  Never an assert."""


def refuse(msg):
    raise Refusal(msg)


def usage(msg):
    sys.stderr.write("USAGE ERROR: " + msg + "\n")
    sys.stderr.write(__doc__.strip().splitlines()[0] + "\n")
    sys.exit(EXIT_USAGE)


# ---------------------------------------------------------------------------
# Parsing.  Generic over OpenFOAM function-object tables: column 0 is the time,
# non-numeric tokens are labels (patch/zone names), the rest are values.
# ---------------------------------------------------------------------------
def parse_table(path):
    """Return dict(headers, rows, labels, values).

    `values` EXCLUDES column 0.  That exclusion is load-bearing: the time column
    of a table written at Time = 5000 is non-zero on every row, so a non-zero
    test that included it would pass an all-zero table.
    """
    if not os.path.isfile(path):
        refuse("no such file: %s -- an artifact that is not on disk is not "
               "evidence, and its absence is not a zero" % path)
    headers, rows, labels, values = [], [], [], []
    with open(path, errors="replace") as fh:
        for line in fh:
            s = line.strip()
            if not s:
                continue
            if s.startswith("#"):
                headers.append(s)
                continue
            toks = s.split()
            rows.append(toks)
            for i, t in enumerate(toks):
                try:
                    v = float(t)
                except ValueError:
                    labels.append(t)
                    continue
                if i > 0:
                    values.append(v)
    return dict(headers=headers, rows=rows,
                labels=sorted(set(labels)), values=values)


# ---------------------------------------------------------------------------
# The checks.  Each names the defect it refuses.
# ---------------------------------------------------------------------------
def check_table(path, min_rows=1):
    t = parse_table(path)

    if not t["headers"]:
        refuse("%s has no `#` header line: this is not an OpenFOAM "
               "function-object table, and the check was pointed at the wrong "
               "file" % path)

    if len(t["rows"]) < min_rows:
        refuse("%s carries %d data rows (need >= %d) beside %d header lines. "
               "THE FUNCTION OBJECT NEVER EMITTED. A `writeControl`/"
               "`writeInterval` pair is NOT portable between function objects: "
               "copied from an `execute()`-emitting object onto a "
               "`write()`-emitting one it silently means NEVER. Check the "
               "sibling tables in the same postProcessing tree -- an "
               "`execute()`-emitting object under the identical control will "
               "have thousands of rows"
               % (path, len(t["rows"]), min_rows, len(t["headers"])))

    if not t["values"]:
        refuse("%s has %d data rows but no parseable numeric value outside "
               "column 0 -- there is nothing in it to be evidence"
               % (path, len(t["rows"])))

    if all(v == 0.0 for v in t["values"]):
        refuse("%s has %d data rows and EVERY ONE OF ITS %d VALUES IS EXACTLY "
               "ZERO. CLAUDE.md rule 3: a zero from a reader not shown able to "
               "see a non-zero is not evidence. The known producer of this "
               "shape is a reader that could not find what it was asked to "
               "measure and wrote a well-formed table anyway with rc=0 -- e.g. "
               "`postProcess -func yPlus` on a case whose turbulence model is "
               "not in the registry. The cure is the SOLVER's own -postProcess "
               "mode (`<solver> -postProcess -func <name>`), which loads the "
               "registry, run AS A PAIR with the blind invocation as the "
               "control" % (path, len(t["rows"]), len(t["values"])))

    return t


def check_control_pair(subject_path, control_path):
    """Verify a CLAIMED rule-3 control is actually a control.

    A control offered alongside a subject must itself be able to see a non-zero
    on the same object, or it proves nothing about the subject.
    """
    c = parse_table(control_path)
    if not c["rows"]:
        refuse("the control %s carries ZERO data rows. A control that emitted "
               "nothing demonstrates nothing: it cannot show that the reader "
               "was able to see a non-zero" % control_path)
    if not c["values"] or all(v == 0.0 for v in c["values"]):
        refuse("the control %s is itself ALL ZEROS. THE CONTROL IS NOT A "
               "CONTROL -- two blind readers agreeing is not a live control "
               "(CLAUDE.md rule 3)" % control_path)

    s = parse_table(subject_path)
    if s["labels"] and c["labels"] and s["labels"] != c["labels"]:
        refuse("subject and control cover DIFFERENT label sets, so they do not "
               "measure the same object and neither controls the other.\n"
               "  subject %s: %s\n  control %s: %s"
               % (subject_path, ",".join(s["labels"]),
                  control_path, ",".join(c["labels"])))

    if s["values"] and all(v == 0.0 for v in s["values"]):
        refuse("the control %s IS non-zero on the same label set while the "
               "subject %s is entirely zero. THE PAIR PROVES THE SUBJECT'S "
               "ZEROS ARE FABRICATED, not that they are a measurement"
               % (control_path, subject_path))
    return s, c


# ---------------------------------------------------------------------------
# SELFTEST -- the planted-failure proof.  A guard never driven against a failure
# is not known to gate.  Sanaa's standing directive: every guard ships its
# planted-failure proof.  Restrictive repairs additionally carry a POSITIVE
# control (VERIFICATION_CHARTER §2p.3(e)): the same run must show the guard
# STILL PASSES WHAT IT SHOULD PASS.
# ---------------------------------------------------------------------------
HDR = ("# y+ ()           \n"
       "# Time            \tpatch             \tmin               \t"
       "max               \taverage           \n")

WALLS = ("floor", "roof", "cube_front", "cube_rear", "cube_top", "cube_side_n")


def _write(path, text):
    with open(path, "w") as fh:
        fh.write(text)
    return path


def _table(walls, val, time=5000):
    s = HDR
    for w in walls:
        s += "%-18d\t%s\t%.10e\t%.10e\t%.10e\n" % (time, w, val, val, val)
    return s


def _arm(name, fn, expect):
    """Drive one arm.  `expect` is 'REFUSE' or 'PASS'.  Returns True if the arm
    behaved as required.  Nothing is printed unless this function ran."""
    try:
        fn()
        got = "PASS"
        why = ""
    except Refusal as e:
        got = "REFUSE"
        why = str(e).split("\n")[0]
    ok = (got == expect)
    print("  [%s] %-58s expected %-6s got %-6s%s"
          % ("ok " if ok else "BAD", name, expect, got,
             ("  <- " + why[:96]) if got == "REFUSE" else ""))
    return ok


def selftest():
    here = os.path.dirname(os.path.abspath(__file__))
    repo = os.path.dirname(here)
    diag = os.path.join(repo, "verification", "runs", "T-family", "T5_runs",
                        "YPLUS_RECOVERABILITY_2026-09-03")
    results = []
    print("check_fo_table_is_evidence.py SELFTEST -- planted failures first, "
          "then the positive control, then the real T5 specimen.")
    print("interpreter optimisation flag __debug__ = %r (False means python3 -O; "
          "no check here is an assert)" % __debug__)

    with tempfile.TemporaryDirectory() as d:
        p_headers_only = _write(os.path.join(d, "headers_only.dat"), HDR)
        p_all_zero = _write(os.path.join(d, "all_zero.dat"),
                            _table(WALLS, 0.0))
        p_good = _write(os.path.join(d, "good.dat"), _table(WALLS, 1.5))
        p_other = _write(os.path.join(d, "other_walls.dat"),
                         _table(("inlet", "outlet"), 1.5))
        p_notfo = _write(os.path.join(d, "not_a_table.txt"),
                         "5000 floor 1.0 2.0 3.0\n")
        p_missing = os.path.join(d, "does_not_exist.dat")

        print("\n-- PLANTED FAILURES (each MUST refuse) --")
        results.append(_arm("A1 headers, ZERO data rows (the T5 defect)",
                            lambda: check_table(p_headers_only), "REFUSE"))
        results.append(_arm("A2 rows present, EVERY value exactly zero",
                            lambda: check_table(p_all_zero), "REFUSE"))
        results.append(_arm("A3 file does not exist",
                            lambda: check_table(p_missing), "REFUSE"))
        results.append(_arm("A4 not a function-object table (no # header)",
                            lambda: check_table(p_notfo), "REFUSE"))
        results.append(_arm("A5 control offered but control is ALL ZEROS",
                            lambda: check_control_pair(p_good, p_all_zero),
                            "REFUSE"))
        results.append(_arm("A6 control offered but control has ZERO rows",
                            lambda: check_control_pair(p_good, p_headers_only),
                            "REFUSE"))
        results.append(_arm("A7 control covers a DIFFERENT label set",
                            lambda: check_control_pair(p_good, p_other),
                            "REFUSE"))
        results.append(_arm("A8 all-zero subject vs non-zero control -> "
                            "fabricated",
                            lambda: check_control_pair(p_all_zero, p_good),
                            "REFUSE"))

        print("\n-- POSITIVE CONTROLS (§2p.3(e): it must still pass what it "
              "should pass) --")
        results.append(_arm("B1 a genuine non-zero table",
                            lambda: check_table(p_good), "PASS"))
        results.append(_arm("B2 non-zero subject with a valid non-zero control",
                            lambda: check_control_pair(p_good, p_good), "PASS"))

    print("\n-- THE REAL T5 SPECIMEN (preserved artifacts, not fixtures) --")
    real = [
        ("C1 T5 as-run yPlus.dat: FO never emitted",
         "DIAG_asrun_T5_CUBE_m_yplus_table_ZERO_ROWS.dat", "REFUSE", None),
        ("C2 Run A `postProcess`: fabricated zeros, rc=0",
         "DIAG_runA_yplus_table_ZEROS.dat", "REFUSE", None),
        ("C3 Run B `<solver> -postProcess`: genuine y+",
         "DIAG_runB_yplus_table_NONZERO.dat", "PASS", None),
        ("C4 Run A against Run B as its live control",
         "DIAG_runA_yplus_table_ZEROS.dat", "REFUSE",
         "DIAG_runB_yplus_table_NONZERO.dat"),
    ]
    if not os.path.isdir(diag):
        print("  [BAD] the preserved specimen directory is ABSENT: %s" % diag)
        print("        These arms are the only ones driven over real artifacts "
              "rather than fixtures; their absence is a FAILURE, not a skip.")
        results.append(False)
    else:
        for name, fname, expect, ctl in real:
            sp = os.path.join(diag, fname)
            if ctl is None:
                results.append(_arm(name, lambda p=sp: check_table(p), expect))
            else:
                cp = os.path.join(diag, ctl)
                results.append(_arm(name,
                                    lambda p=sp, c=cp: check_control_pair(p, c),
                                    expect))

    bad = results.count(False)
    print("\n%d arms driven, %d MISBEHAVED." % (len(results), bad))
    if bad:
        sys.stderr.write("SELFTEST FAILED: %d of %d arms did not behave as "
                         "required.\n" % (bad, len(results)))
        return EXIT_REFUSE
    print("Every planted failure refused and every positive control passed.")
    return EXIT_OK


# ---------------------------------------------------------------------------
def main(argv):
    if "--selftest" in argv:
        return selftest()

    args = [a for a in argv if not a.startswith("--")]
    control = None
    min_rows = 1
    i = 0
    while i < len(argv):
        if argv[i] == "--control":
            if i + 1 >= len(argv):
                usage("--control needs a path")
            control = argv[i + 1]
            if control in args:
                args.remove(control)
            i += 1
        elif argv[i] == "--min-rows":
            if i + 1 >= len(argv):
                usage("--min-rows needs an integer")
            try:
                min_rows = int(argv[i + 1])
            except ValueError:
                usage("--min-rows needs an integer, got %r" % argv[i + 1])
            if argv[i + 1] in args:
                args.remove(argv[i + 1])
            i += 1
        i += 1

    if len(args) != 1:
        usage("give exactly one table path (got %d), or --selftest"
              % len(args))

    path = args[0]
    try:
        t = check_table(path, min_rows=min_rows)
        if control is not None:
            check_control_pair(path, control)
    except Refusal as e:
        sys.stderr.write("REFUSED: %s\n" % e)
        return EXIT_REFUSE

    nz = sum(1 for v in t["values"] if v != 0.0)
    print("ADMISSIBLE: %s -- %d data rows, %d values, %d non-zero, labels: %s"
          % (path, len(t["rows"]), len(t["values"]), nz,
             ",".join(t["labels"]) if t["labels"] else "(none)"))
    if control is not None:
        print("            rule-3 control %s verified: non-zero on the same "
              "label set" % control)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
