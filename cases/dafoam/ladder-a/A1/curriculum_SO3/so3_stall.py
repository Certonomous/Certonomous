#!/usr/bin/env python3
"""SO-3 STALL DETECTOR -- the registered numerical stop for a backtracking optimiser.

WHY THIS FILE EXISTS, AND IT IS NOT A CONVENIENCE
-------------------------------------------------
`docs/COST_CALIBRATION.md` C-188 is the measurement this instrument is built on.
D6's `O_mp` arm -- 3 scenarios, np = 4, a 3-D wing -- ran 8 h 20 m, was stopped
by its own registered deadline with `rc = 124`, `OOMKilled = false`, and cost
**31.258 core-min/major MEASURED against 19.167 registered**, a factor 1.6308.
The row's own conclusion is that the optimiser **STALLED** rather than ran slow:

    545 line-search cutbacks, 7 restoration majors, dual infeasibility WORSENING

and that *"a rate calibrated on a converging optimiser does not price one that is
backtracking, and the successor's estimate must carry a stall branch."*

A wall-clock deadline already bounds the spend.  What it does NOT do is tell the
record WHY the run ended, and `DAFOAM_CHARTER.md` section 9 makes that difference
a verdict difference: an optimisation stopped by a wall clock is `GATE REACHED`
where a registered intermediate threshold was met and `NOT A RESULT` otherwise,
**never `PASS`**.  A run that spent four hours backtracking and a run that was
still descending when the clock ran out are both `rc = 124`, and only a stall
reading separates them.

WHAT IS REGISTERED HERE, BEFORE ANY COMPUTE
--------------------------------------------
Two conditions, either of which STOPS the run.  Both are stated as numbers, not
as adjectives, and both are frozen with the pre-registration:

  A. `N_STALL` CONSECUTIVE majors with `alpha_pr < ALPHA_PR_MIN`.
     `alpha_pr` is IPOPT's primal step length: the fraction of the computed step
     the line search actually accepted.  A run taking 1e-4 of its step for eight
     majors running is not descending, it is cutting back.
  B. Dual infeasibility NON-DECREASING over `N_STALL` consecutive majors.
     `inf_du` is IPOPT's own measure of distance from the KKT stationarity
     condition.  Non-decreasing over a window means the optimiser is not getting
     closer to a stationary point.  NON-DECREASING, not INCREASING: a perfectly
     flat `inf_du` is the same failure and would slip a strict test.

`ls` (the line-search count per major) is PARSED AND REPORTED but is NOT a stop
condition.  C-188's 545 cutbacks are the headline number and it is tempting to
gate on them; that would be gating on a CUMULATIVE quantity, so a long healthy
run would eventually trip it.  `alpha_pr` is the per-major form of the same
signal and is scale-free.  The cumulative count is reported beside the verdict
so a reader can see C-188's own statistic.

CALIBRATED AGAINST 36 REAL IPOPT LOGS ON THIS BOX, NOT AGAINST ITS OWN FIXTURES
-------------------------------------------------------------------------------
Every number in this paragraph is MEASURED by driving this module over
`/home/ubuntu/certonomous-runs/**/opt_IPOPT.txt` (36 files; 3 carry fewer majors
than the window and are REFUSED rather than graded, leaving 33):

  * **Condition A fires on exactly 2 of 33, and both are the known stalls** --
    `CURRICULUM-D6-a2-wing-multipoint/O_mp` (C-188's own arm, 65 majors) and
    `CURRICULUM-D6R-a2-wing-multipoint/O_mp` (74 majors).  Both fire at major
    **34**.  Zero of the other 31 fire, INCLUDING the seven that ended
    `Maximum Number of Iterations Exceeded` -- a cap is not a stall and the
    detector must not confuse them.  31/31 specificity, 2/2 sensitivity, on the
    lab's whole optimisation history.
  * **Condition B fires on 0 of 33.  IT HAS NEVER BEEN EXERCISED ON REAL
    EVIDENCE**, and it is reported that way -- `NOT EXERCISED`, never as a
    passing control (`DAFOAM_CHARTER.md` section 18.5's shape).  It fires only on
    this module's synthetic legs (s3/s4).  This CONTRADICTS the plain reading of
    C-188's phrase *"dual infeasibility worsening"*: on D6's own artefact `inf_du`
    goes 5.71e-03 -> 1.14e-03, i.e. it IMPROVES fivefold over the run, and no
    8-major window is non-decreasing.  C-188's phrase is a characterisation of a
    violently non-monotone series (it swings 2.6e-04 .. 9.99e+02 across
    restoration majors), not a monotone claim.  **Condition A is the condition
    carrying the load; B is registered for a failure mode this lab has not yet
    observed.**
  * **The cumulative cutback count does not reproduce C-188's 545.**  This module
    defines it as `sum(max(0, ls-1))` over every parsed row and MEASURES **547**
    on D6's artefact; `sum(ls)` is 611 and the non-restoration variants are 507
    and 450.  None is 545.  C-188's figure is not reproduced by any natural
    definition and the discrepancy is REPORTED rather than reconciled by picking
    a definition that lands on it.  Restoration-major count DOES reproduce
    exactly: **7**, as C-188 records.
  * **The abort's value is 48 %, not 7.7 %**, and only because the stop is taken
    at the FIRST reach of the window.  See the comment at condition A.

WHAT THIS FILE DOES NOT DECIDE
-------------------------------
It emits `STALL` or `NO_STALL` and the evidence.  It NEVER emits a verdict from
`CLAUDE.md` rule 1's vocabulary.  The mapping from a stall to `GATE REACHED` or
`NOT A RESULT` lives in `so3_grade.py` and is section 9's, not this module's --
because that mapping depends on a registered intermediate threshold this module
cannot see.  A detector that also graded would be able to launder a stop into a
pass by relabelling it here.

REFUSAL TOKENS -- exit 2 AND a named token on stdout, so an unrelated crash
(which also exits non-zero) can never be read as an expected refusal:
    REFUSE_NO_ITERATION_TABLE   the log carries no parseable IPOPT iteration row
    REFUSE_NONMONOTONE_ITER     the parsed major numbers are not strictly ordered
    REFUSE_WINDOW_LONGER        N_STALL exceeds the number of majors parsed
"""
import json
import os
import re
import sys

# ---- THE REGISTERED CONSTANTS.  Frozen with PREREGISTRATION.md. --------------
N_STALL = 8            # consecutive majors in the window, BOTH conditions
ALPHA_PR_MIN = 1.0e-3  # condition A: a primal step below this is a cutback
# Condition B compares `inf_du` across the window.  A tolerance is registered so
# that floating-point noise at the 1e-16 level in a genuinely decreasing series
# cannot read as "non-decreasing".  It is RELATIVE to the window's first value.
INF_DU_REL_TOL = 1.0e-12

# IPOPT's iteration table.  The `r` suffix marks a RESTORATION major; `iter` may
# also carry no suffix.  Columns, in the order IPOPT prints them:
#   iter  objective  inf_pr  inf_du  lg(mu)  ||d||  lg(rg)  alpha_du  alpha_pr  ls
# `lg(rg)` prints as `-` when the regularisation is zero, so it is matched as a
# non-space run rather than as a number.
_NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eEdD][-+]?\d+)?"
ITER_RE = re.compile(
    r"^\s*(?P<iter>\d+)(?P<restore>r?)\s+"
    r"(?P<obj>" + _NUM + r")\s+"
    r"(?P<inf_pr>" + _NUM + r")\s+"
    r"(?P<inf_du>" + _NUM + r")\s+"
    r"(?P<lgmu>" + _NUM + r")\s+"
    r"(?P<dnorm>" + _NUM + r")\s+"
    r"(?P<lgrg>\S+)\s+"
    r"(?P<alpha_du>" + _NUM + r")\s+"
    r"(?P<alpha_pr>" + _NUM + r")(?P<alpha_pr_tag>[a-zA-Z]*)\s+"
    r"(?P<ls>\d+)\s*$")

# IPOPT's own terminal statement.  PARSED AND REPORTED; the grader decides what
# it means.  `DAFOAM_CHARTER.md` section 9: A2's 47-major run printed NO `EXIT`
# line at all, and that absence is the finding.
EXIT_RE = re.compile(r"^\s*EXIT:\s*(?P<what>.+?)\s*$", re.M)


def _f(s):
    return float(str(s).replace("D", "E").replace("d", "e"))


def refuse(token, detail):
    print("%s %s" % (token, detail))
    sys.exit(2)


def parse_majors(text):
    """Every IPOPT iteration row in `text`, in file order, as dicts.

    Reads ONLY rows the registered regex matches in full.  There is no fallback
    that splits on whitespace and hopes: a looser reader on a log whose column
    set moved would return numbers from the wrong columns, and every number
    below would still be a float."""
    out = []
    for line in text.splitlines():
        m = ITER_RE.match(line)
        if not m:
            continue
        out.append({
            "iter": int(m.group("iter")),
            "restoration": m.group("restore") == "r",
            "objective": _f(m.group("obj")),
            "inf_pr": _f(m.group("inf_pr")),
            "inf_du": _f(m.group("inf_du")),
            "alpha_du": _f(m.group("alpha_du")),
            "alpha_pr": _f(m.group("alpha_pr")),
            "ls": int(m.group("ls")),
        })
    return out


def detect_stall(majors, n_stall=N_STALL, alpha_pr_min=ALPHA_PR_MIN):
    """The registered stop conditions, applied to a parsed major list.

    Returns a dict.  NEVER returns a rule-1 verdict token: the caller maps."""
    if not majors:
        refuse("REFUSE_NO_ITERATION_TABLE", "zero parseable IPOPT iteration rows")
    nums = [m["iter"] for m in majors]
    if any(b < a for a, b in zip(nums, nums[1:])):
        refuse("REFUSE_NONMONOTONE_ITER",
               "major numbers go backwards: %r" % (nums[:20],))
    if n_stall > len(majors):
        refuse("REFUSE_WINDOW_LONGER",
               "window %d > majors parsed %d" % (n_stall, len(majors)))

    # ---- condition A: N_STALL consecutive majors with alpha_pr below the floor.
    # ---- Major 0 is EXCLUDED: IPOPT prints alpha_pr = 0 on its first row by
    # ---- construction (no step has been taken), and including it would let a
    # ---- two-major run with one cutback look like the start of a stall.
    # ---- AND THE STOP IS WHERE THE RUN **FIRST REACHES** THE WINDOW, NEVER
    # ---- WHERE THE LONGEST RUN ENDS.  This lane's first draft reported the
    # ---- longest run's end and it was WRONG BY 26 MAJORS on the real artefact:
    # ---- driven against C-188's own `CURRICULUM-D6-a2-wing-multipoint/O_mp/
    # ---- opt_IPOPT.txt`, the longest run (17) ends at major 60 of 65, but the
    # ---- FIRST run to reach 8 ends at major 34.  Reporting 60 would have priced
    # ---- the abort at a 7.7 % saving when it is really 48 %, and -- far worse --
    # ---- a watchdog built on that reading would not have stopped until major 60.
    # ---- The error was invisible in the synthetic legs, where the first run and
    # ---- the longest run are the same run.
    body = [m for m in majors if m["iter"] > 0]
    a_run, a_best, a_best_at, a_at = 0, 0, None, None
    for m in body:
        if m["alpha_pr"] < alpha_pr_min:
            a_run += 1
            if a_run > a_best:
                a_best, a_best_at = a_run, m["iter"]
            if a_run == n_stall and a_at is None:
                a_at = m["iter"]
        else:
            a_run = 0
    cond_a = a_at is not None

    # ---- condition B: inf_du NON-DECREASING across a window of n_stall majors.
    # ---- Compared PAIRWISE inside the window, so a series that dips once and
    # ---- then climbs does not read as a stall.
    b_at, cond_b, b_window = None, False, None
    for i in range(0, max(0, len(body) - n_stall + 1)):
        w = body[i:i + n_stall]
        base = abs(w[0]["inf_du"]) or 1.0
        tol = INF_DU_REL_TOL * base
        if all(b["inf_du"] >= a["inf_du"] - tol for a, b in zip(w, w[1:])):
            cond_b, b_at = True, w[-1]["iter"]
            b_window = [x["inf_du"] for x in w]
            break

    return {
        "n_majors_parsed": len(majors),
        "n_restoration_majors": sum(1 for m in majors if m["restoration"]),
        "cumulative_line_search_cutbacks": sum(max(0, m["ls"] - 1) for m in majors),
        "n_stall_window": n_stall,
        "alpha_pr_min": alpha_pr_min,
        "condition_A_alpha_pr_run": {"longest_run": a_best,
                                     "longest_run_ends_at_major": a_best_at,
                                     "first_reaches_window_at_major": a_at,
                                     "ends_at_major": a_at,
                                     "fired": cond_a},
        "condition_B_inf_du_nondecreasing": {"ends_at_major": b_at, "fired": cond_b,
                                             "window": b_window},
        "stall": "STALL" if (cond_a or cond_b) else "NO_STALL",
        "stop_at_major": (min([x for x in (a_at, b_at) if x is not None])
                          if (cond_a or cond_b) else None),
        "first_inf_du": body[0]["inf_du"] if body else None,
        "last_inf_du": body[-1]["inf_du"] if body else None,
        "last_objective": majors[-1]["objective"],
        "first_objective": majors[0]["objective"],
    }


def read_exit_statement(text):
    """IPOPT's own terminal line, or None.  `None` IS THE FINDING when it happens
    -- section 9's A2 incident is a 47-major run with no EXIT line anywhere."""
    m = EXIT_RE.search(text)
    return m.group("what") if m else None


def scan_file(path, n_stall=N_STALL, alpha_pr_min=ALPHA_PR_MIN):
    if not os.path.isfile(path):
        refuse("REFUSE_NO_ITERATION_TABLE", "no such file: %s" % path)
    text = open(path, "r", errors="replace").read()
    rec = detect_stall(parse_majors(text), n_stall, alpha_pr_min)
    rec["exit_statement"] = read_exit_statement(text)
    rec["source"] = os.path.abspath(path)
    return rec


# ---------------------------------------------------------------------------
# SELFTEST -- every leg DRIVEN, never asserted in prose.  An instrument that has
# never fired is not evidence, so the RED legs come first and each demands its
# refusal or its firing BY NAME.
# ---------------------------------------------------------------------------

_HDR = ("iter    objective    inf_pr   inf_du lg(mu)  ||d||  lg(rg) "
        "alpha_du alpha_pr  ls\n")


def _row(i, obj, inf_pr, inf_du, alpha_pr, ls=1, restore=False, alpha_du=9.99e-01):
    return ("%4d%s %14.7e %8.2e %8.2e  -1.0 1.00e-02    -  %8.2e %8.2e %3d\n"
            % (i, "r" if restore else "", obj, inf_pr, inf_du, alpha_du, alpha_pr, ls))


def _leg(name, fn, expect):
    """`expect` is a REFUSAL TOKEN, or a (key, value) pair the returned record
    must carry, or None for "returns cleanly"."""
    import contextlib
    import io
    buf = io.StringIO()
    got, code = None, 0
    try:
        with contextlib.redirect_stdout(buf):
            got = fn()
    except SystemExit as e:
        code = e.code
    out = buf.getvalue()
    if isinstance(expect, str):
        ok = (code == 2) and (expect in out)
        why = "expected exit 2 AND token %s" % expect
    elif expect is None:
        ok = (code == 0)
        why = "expected a clean return"
    else:
        k, v = expect
        ok = (code == 0) and got is not None and got.get(k) == v
        why = "expected %s == %r, got %r" % (k, v, (got or {}).get(k))
    print("  %-46s %-34s %s" % (name, expect if isinstance(expect, str)
                                else (expect or "(clean)"), "PASS" if ok else "FAIL"))
    if not ok:
        print("     %s; code=%r out=%r" % (why, code, out.strip()[:200]))
    return ok, got


def selftest():
    ok = True
    print("SO-3 STALL DETECTOR SELFTEST")

    # ---- (s1) THE C-188 GEOMETRY, REPRODUCED FROM ITS OWN RECORDED STATISTICS.
    # A backtracking run: alpha_pr collapses, inf_du worsens, restoration majors
    # appear, and the cumulative cutback count climbs toward C-188's 545.
    print("\n[s1] C-188's own shape -- the detector MUST fire")
    t = _HDR + _row(0, 2.9619634e-02, 0.0, 1.00e+00, 0.0, ls=0)
    for i in range(1, 6):                      # a healthy start
        t += _row(i, 2.9e-02 - i * 1e-4, 1e-6, 1.0e+00 / (i + 1), 1.0, ls=1)
    for i in range(6, 30):                     # the stall: cutbacks, inf_du climbing
        t += _row(i, 2.86e-02, 1e-6, 1.6e-01 * (1.0 + 0.01 * (i - 6)),
                  1.0e-5, ls=23, restore=(i % 4 == 0))
    r1 = None
    good, r1 = _leg("C-188 backtracking series", lambda: detect_stall(parse_majors(t)),
                    ("stall", "STALL"))
    ok &= good
    if r1:
        for k, want in (("cond_a", True), ("cond_b", True)):
            pass
        a = r1["condition_A_alpha_pr_run"]["fired"]
        b = r1["condition_B_inf_du_nondecreasing"]["fired"]
        print("     condition A (alpha_pr run=%d) fired=%s ; condition B fired=%s "
              "; restoration majors=%d ; cumulative cutbacks=%d"
              % (r1["condition_A_alpha_pr_run"]["longest_run"], a, b,
                 r1["n_restoration_majors"], r1["cumulative_line_search_cutbacks"]))
        ok &= (a and b)
        ok &= (r1["n_restoration_majors"] == 6)
        ok &= (r1["stop_at_major"] == 13)

    # ---- (s2) THE NEGATIVE LEG.  A CONVERGING run must NOT fire.  Without this
    # ---- the detector could be a function that returns STALL unconditionally.
    print("\n[s2] a converging series -- the detector MUST NOT fire")
    t2 = _HDR + _row(0, 2.9619634e-02, 0.0, 1.00e+00, 0.0, ls=0)
    for i in range(1, 25):
        t2 += _row(i, 2.96e-02 - i * 3e-4, 1e-8, 1.0e+00 * (0.6 ** i), 1.0, ls=1)
    good, r2 = _leg("converging series", lambda: detect_stall(parse_majors(t2)),
                    ("stall", "NO_STALL"))
    ok &= good

    # ---- (s3) EACH CONDITION ALONE.  A detector whose two conditions can only
    # ---- fire together has one condition, not two.
    print("\n[s3] each registered condition fires ALONE")
    t3 = _HDR + _row(0, 1.0, 0.0, 1.0, 0.0, ls=0)          # A only: inf_du still falls
    for i in range(1, 21):
        t3 += _row(i, 1.0 - i * 1e-6, 1e-8, 1.0 * (0.5 ** i), 1.0e-5, ls=30)
    good, r3 = _leg("A alone (cutbacks, inf_du still falling)",
                    lambda: detect_stall(parse_majors(t3)), ("stall", "STALL"))
    ok &= good
    if r3:
        good = (r3["condition_A_alpha_pr_run"]["fired"] and
                not r3["condition_B_inf_du_nondecreasing"]["fired"])
        print("     A fired alone: %s" % ("PASS" if good else "FAIL"))
        ok &= good

    t4 = _HDR + _row(0, 1.0, 0.0, 1.0, 0.0, ls=0)          # B only: full steps taken
    for i in range(1, 21):
        t4 += _row(i, 1.0, 1e-8, 1.0e-2 * (1.0 + 0.05 * i), 1.0, ls=1)
    good, r4 = _leg("B alone (full steps, inf_du non-decreasing)",
                    lambda: detect_stall(parse_majors(t4)), ("stall", "STALL"))
    ok &= good
    if r4:
        good = (not r4["condition_A_alpha_pr_run"]["fired"] and
                r4["condition_B_inf_du_nondecreasing"]["fired"])
        print("     B fired alone: %s" % ("PASS" if good else "FAIL"))
        ok &= good

    # ---- (s4) THE FLAT SERIES.  `NON-DECREASING`, not `INCREASING`: a perfectly
    # ---- flat inf_du is the same failure and a strict `>` would miss it.  This
    # ---- leg is the reason the word in the docstring is the word in the code.
    print("\n[s4] a FLAT inf_du is a stall -- a strict `>` test would miss it")
    t5 = _HDR + _row(0, 1.0, 0.0, 1.0, 0.0, ls=0)
    for i in range(1, 21):
        t5 += _row(i, 1.0, 1e-8, 3.3e-02, 1.0, ls=1)
    good, r5 = _leg("flat inf_du", lambda: detect_stall(parse_majors(t5)),
                    ("stall", "STALL"))
    ok &= good

    # ---- (s5) THE REFUSALS, EACH DEMANDED BY NAME.
    print("\n[s5] refusals, each demanded BY NAME")
    good, _ = _leg("no iteration table at all",
                   lambda: detect_stall(parse_majors("nothing here\n")),
                   "REFUSE_NO_ITERATION_TABLE")
    ok &= good
    back = _HDR + _row(3, 1.0, 0.0, 1.0, 1.0) + _row(1, 1.0, 0.0, 1.0, 1.0)
    good, _ = _leg("major numbers go backwards",
                   lambda: detect_stall(parse_majors(back)), "REFUSE_NONMONOTONE_ITER")
    ok &= good
    short = _HDR + _row(0, 1.0, 0.0, 1.0, 0.0) + _row(1, 1.0, 0.0, 1.0, 1.0)
    good, _ = _leg("window longer than the run",
                   lambda: detect_stall(parse_majors(short)), "REFUSE_WINDOW_LONGER")
    ok &= good

    # ---- (s6) THE PARSER IS NOT A WHITESPACE SPLITTER.  A row whose column set
    # ---- moved must be SKIPPED, not read from the wrong columns.  This is the
    # ---- leg that proves the strict regex is doing work.
    print("\n[s6] a row with a moved column set is SKIPPED, never mis-read")
    bad = _HDR + "   1  2.9e-02 0.00e+00 1.00e+00  -1.0 1.00e-02\n"   # truncated row
    n = len(parse_majors(bad))
    print("  %-46s %-34s %s" % ("truncated row not parsed", "0 rows",
                                "PASS" if n == 0 else "FAIL"))
    ok &= (n == 0)

    # ---- (s7) THE MISSING `EXIT` LINE, which is section 9's A2 incident.
    print("\n[s7] IPOPT's EXIT statement -- present and ABSENT")
    good = (read_exit_statement("EXIT: Optimal Solution Found.\n")
            == "Optimal Solution Found.")
    print("  %-46s %-34s %s" % ("EXIT present", "parsed", "PASS" if good else "FAIL"))
    ok &= good
    good = read_exit_statement(t) is None
    print("  %-46s %-34s %s" % ("EXIT absent (A2's 47-major run)", "None",
                                "PASS" if good else "FAIL"))
    ok &= good

    # ---- (s8) THE REAL-ARTEFACT LEGS.  A parser validated only against rows this
    # ---- same file printed is validated against itself.  These drive the module
    # ---- over artefacts it did not write.  A file that is NOT ON DISK is
    # ---- reported `NOT_ON_DISK` and the leg is NOT EXERCISED -- never PASS,
    # ---- because a skipped leg counted as a pass is a fail-open.
    print("\n[s8] REAL artefacts this module did not write")
    REAL = [
        # (path, expected stall, expected first-reach major, expected EXIT, why)
        ("/home/ubuntu/certonomous-runs/CURRICULUM-D6-a2-wing-multipoint/O_mp/opt_IPOPT.txt",
         "STALL", 34, None,
         "C-188's OWN arm.  MUST fire, and MUST report no EXIT line."),
        ("/home/ubuntu/certonomous-runs/CURRICULUM-D1-a1-constrained-opt/armO/opt_IPOPT.txt",
         "NO_STALL", None, "Optimal Solution Found.",
         "C-24's anchor on THIS A1 case.  A converging run MUST NOT fire."),
        ("/home/ubuntu/certonomous-runs/A2-mach-wing/opt_IPOPT.txt",
         "NO_STALL", None, None,
         "section 9's own A2 incident: 47 majors, NO EXIT line, and NOT a stall "
         "-- it was still descending when the clock ran out."),
        ("/home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-a2-wing-cdmin/O/opt_IPOPT.txt",
         "NO_STALL", None, "Maximum Number of Iterations Exceeded.",
         "A CAP IS NOT A STALL.  This run hit max_iter and must NOT fire."),
    ]
    n_exercised = 0
    for path, want_stall, want_at, want_exit, why in REAL:
        short = path.replace("/home/ubuntu/certonomous-runs/", "")
        if not os.path.isfile(path):
            print("  %-64s NOT_ON_DISK -- LEG NOT EXERCISED" % short)
            continue
        n_exercised += 1
        text = open(path, errors="replace").read()
        rec = detect_stall(parse_majors(text))
        got_exit = read_exit_statement(text)
        good = (rec["stall"] == want_stall
                and rec["condition_A_alpha_pr_run"]["ends_at_major"] == want_at
                and got_exit == want_exit)
        print("  %-64s majors=%3d %-8s A@%-5s exit=%-38r %s"
              % (short, rec["n_majors_parsed"], rec["stall"],
                 rec["condition_A_alpha_pr_run"]["ends_at_major"], got_exit,
                 "PASS" if good else "FAIL"))
        if not good:
            print("     wanted stall=%s first_reach=%s exit=%r -- %s"
                  % (want_stall, want_at, want_exit, why))
        ok &= good
    print("  real-artefact legs exercised: %d of %d" % (n_exercised, len(REAL)))
    if n_exercised == 0:
        print("  NO REAL ARTEFACT WAS READ.  The parser is validated against its "
              "own fixtures only, and that is reported, not hidden.")

    # ---- (s9) CONDITION B'S HONEST STATUS.  Swept over every real IPOPT log on
    # ---- the box.  If it ever fires on one, this leg SAYS SO and the docstring
    # ---- above is out of date -- which is the point of measuring rather than
    # ---- asserting.
    print("\n[s9] condition B across every real IPOPT log -- NOT EXERCISED is a "
          "finding, not a pass")
    import glob
    logs = sorted(glob.glob("/home/ubuntu/certonomous-runs/**/opt_IPOPT.txt",
                            recursive=True))
    n_grad, n_a, n_b, refused = 0, 0, 0, 0
    for p in logs:
        rows = parse_majors(open(p, errors="replace").read())
        if len(rows) < N_STALL + 1:
            refused += 1
            continue
        r = detect_stall(rows)
        n_grad += 1
        n_a += 1 if r["condition_A_alpha_pr_run"]["fired"] else 0
        n_b += 1 if r["condition_B_inf_du_nondecreasing"]["fired"] else 0
    print("  logs=%d gradable=%d refused_short=%d | condition A fired on %d | "
          "condition B fired on %d" % (len(logs), n_grad, refused, n_a, n_b))
    if logs:
        print("  condition A: %s" % ("2 of 33 and both are the known D6 stalls"
                                     if (n_grad, n_a) == (33, 2)
                                     else "MEASURED %d of %d -- the docstring's "
                                          "figure has moved" % (n_a, n_grad)))
        print("  condition B: %s" % ("NOT EXERCISED on real evidence"
                                     if n_b == 0 else
                                     "FIRED on %d real logs -- the docstring is "
                                     "OUT OF DATE" % n_b))
    else:
        print("  no real logs on this box -- condition B's status is UNKNOWN, "
              "not clear")

    print("\nSELFTEST %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv):
    if len(argv) == 2 and argv[1] == "selftest":
        return selftest()
    if len(argv) >= 3 and argv[1] == "scan":
        print(json.dumps(scan_file(argv[2]), indent=2, sort_keys=True))
        return 0
    print(__doc__)
    print("usage: so3_stall.py scan <ipopt_output_file>\n"
          "       so3_stall.py selftest")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
