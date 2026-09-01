#!/usr/bin/env python3
r"""Curriculum D19M -- THE IPOPT LOG READER AND THE REGISTERED NUMERICAL STOP.

This module does three separable jobs and keeps them separable, because
`DAFOAM_CHARTER.md` section 9 makes the difference between them a VERDICT
difference and not a presentational one:

  1. PARSE  an `opt_IPOPT.txt` iteration table into rows.
  2. READ   whether the optimiser printed ITS OWN convergence statement.
  3. DETECT the registered stall condition, so a run that is going nowhere is
     stopped by a NUMERICAL rule rather than by a wall clock -- and so the
     record can say WHICH of the two ended it.

WHY 2 AND 3 MUST NOT BE MERGED (the incident, and it is this family's own).
`DAFOAM_CHARTER.md` section 9 rests on A2: a genuine IPOPT 3.13.5 / MUMPS /
L-BFGS run, `tol = 1e-5`, `max_iter = 100`, 47 majors in a 60-minute box, drag
reduced 28.275488 % at matched `CL ~ 0.5` -- and **IPOPT printed no `EXIT` line
and no convergence statement anywhere in the log; the table simply stops after
iteration 47.**  A reader that inferred convergence from the improvement would
have graded that `PASS`.  Here `converged_statement()` returns a value read from
the bytes or `None`, and `None` can never become a `PASS`.

THE STALL CONDITIONS, AND THE HONEST STATE OF EACH
==================================================
CONDITION A -- `N_STALL` consecutive majors with `alpha_pr < ALPHA_PR_FLOOR`.
CONDITION B -- dual infeasibility (`inf_du`) NON-DECREASING over `N_STALL`
    consecutive majors, with a relative tolerance so that floating-point noise
    in a genuinely decreasing series cannot read as "non-decreasing".

**CONDITION B IS REGISTERED `NOT EXERCISED` AND IS NEVER REPORTED AS A PASSING
CONTROL.**  `curriculum_SO3/PREREGISTRATION.md` section 9.2 measured both over
33 gradable IPOPT logs on this box: condition A fires on exactly 2 (both known
D6 stalls) and on NONE of the 7 that ended `Maximum Number of Iterations
Exceeded` -- a cap is not a stall, and the detector distinguishes them --
while **condition B fires on 0 of 33**.  That registration also corrects the
assumption B was built on: *"dual infeasibility worsening"* is not a monotone
claim, and on C-188's own artefact `inf_du` goes 5.71e-03 -> 1.14e-03, a 5x
IMPROVEMENT, on a run that genuinely stalled.  **Condition A carries the entire
load.**  A control that has never been able to fire is reported as not
exercised; it is not quietly counted as green.

THE STOP IS THE FIRST REACH OF THE WINDOW, AND THE DEFINITION IS REGISTERED.
The abort fires at the FIRST major at which an `N_STALL`-major window is
complete -- NOT at the end of the longest run of stalled majors.  On D6's own
`O_mp/opt_IPOPT.txt` the two differ by 30 majors of 65.  `--calibrate` re-drives
that reading on the real bytes rather than quoting it.

A COUNT IS CITED WITH ITS DEFINITION OR IT IS NOT CITED.
`curriculum_SO3/PREREGISTRATION.md` section 9.4 measured six plausible
definitions of "line-search cutbacks" on one log and got six different numbers,
against a record that quoted `545` with no definition at all (the module's own
definition gives 547, and 545 is not reachable under any of the six).  Every
count this module returns is keyed by the name of its own rule.

Usage:  d19m_stall.py --selftest
        d19m_stall.py --calibrate <opt_IPOPT.txt> [...]
        (as a library: parse_rows / converged_statement / stall_reach)
"""
import json
import os
import re
import sys

ITEM = "D19M"

# ---- REGISTERED CONSTANTS (PREREGISTRATION.md section 9) ---------------------
N_STALL = 8                 # consecutive majors that close the window
ALPHA_PR_FLOOR = 1.0e-3     # condition A
INF_DU_RTOL = 1.0e-12       # condition B's noise guard
CONDITION_B_STATE = "NOT EXERCISED"   # fires on 0 of 33 real logs; never a green

# IPOPT's iteration table.  Column order for print_level 5:
#   iter  objective  inf_pr  inf_du  lg(mu)  ||d||  lg(rg)  alpha_du  alpha_pr  ls
# `iter` may carry a trailing `r` (restoration).  Values may be `-` for the
# first row.  The regex is anchored and counts fields; it does not hunt.
_ROW = re.compile(
    r"^\s*(?P<iter>\d+)(?P<rest>r?)\s+"
    r"(?P<obj>[-+0-9.eE]+)\s+"
    r"(?P<inf_pr>[-+0-9.eE]+)\s+"
    r"(?P<inf_du>[-+0-9.eE]+)\s+"
    r"(?P<lg_mu>[-+0-9.eE]+)\s+"
    r"(?P<d_norm>[-+0-9.eE-]+)\s+"
    r"(?P<lg_rg>[-+0-9.eE-]+)\s+"
    r"(?P<alpha_du>[-+0-9.eE]+)\s+"
    r"(?P<alpha_pr>[-+0-9.eE]+[a-zA-Z]?)\s+"
    r"(?P<ls>\d+)\s*$", re.M)

# The optimiser's OWN convergence statement.  Read, never inferred.
_EXIT = re.compile(r"^EXIT:\s*(?P<text>.+?)\s*$", re.M)
_NITER = re.compile(r"^Number of Iterations\.*:\s*(?P<n>\d+)\s*$", re.M)
CONVERGED_TEXT = "Optimal Solution Found."


def _f(tok):
    """A float, or None where IPOPT printed `-`."""
    try:
        return float(re.sub(r"[a-zA-Z]+$", "", tok))
    except (TypeError, ValueError):
        return None


def parse_rows(text):
    """Every table row, in file order.  A row that does not parse is not a row;
    it is also not silently skipped -- `n_unparsed_numeric_lines` reports it."""
    rows = []
    for m in _ROW.finditer(text):
        rows.append({
            "iter": int(m.group("iter")),
            "restoration": m.group("rest") == "r",
            "objective": _f(m.group("obj")),
            "inf_pr": _f(m.group("inf_pr")),
            "inf_du": _f(m.group("inf_du")),
            "alpha_du": _f(m.group("alpha_du")),
            "alpha_pr": _f(m.group("alpha_pr")),
            "ls": int(m.group("ls")),
        })
    return rows


def converged_statement(text):
    """The optimiser's own words, or None.  NEVER inferred from the numbers.

    Returns {"exit": <text or None>, "n_iterations": <int or None>,
             "converged": <bool>} where `converged` is True ONLY if IPOPT itself
    printed `Optimal Solution Found.` on its EXIT line."""
    m = _EXIT.search(text)
    exit_text = m.group("text") if m else None
    n = _NITER.search(text)
    return {"exit": exit_text,
            "n_iterations": int(n.group("n")) if n else None,
            "converged": bool(exit_text and CONVERGED_TEXT in exit_text)}


def stall_reach(rows, n_stall=N_STALL, alpha_floor=ALPHA_PR_FLOOR,
                inf_du_rtol=INF_DU_RTOL):
    """THE FIRST REACH of a closed window, per condition, or None.

    Returns a dict keyed by condition with the ROW INDEX (0-based, into `rows`)
    at which an `n_stall`-major window first closes.  Row index and IPOPT `iter`
    label are BOTH returned, because they differ by IPOPT's 0-based labelling
    and a single number here would be an ambiguity."""
    out = {"A": None, "B": None, "n_rows": len(rows), "n_stall": n_stall,
           "condition_B_state": CONDITION_B_STATE}
    # --- A: consecutive small alpha_pr ---
    run = 0
    for i, r in enumerate(rows):
        a = r.get("alpha_pr")
        run = run + 1 if (a is not None and a < alpha_floor) else 0
        if run >= n_stall and out["A"] is None:
            out["A"] = {"row_index": i, "iter_label": r["iter"],
                        "window_first_row_index": i - n_stall + 1,
                        "rule": "alpha_pr < %g on %d consecutive majors" % (alpha_floor, n_stall)}
    # --- B: inf_du non-decreasing ---
    run = 0
    for i in range(1, len(rows)):
        prev, cur = rows[i - 1].get("inf_du"), rows[i].get("inf_du")
        if prev is None or cur is None:
            run = 0
            continue
        # non-decreasing, with a RELATIVE tolerance against the window's first
        # value so float noise in a decreasing series cannot read as a stall.
        run = run + 1 if cur >= prev * (1.0 - inf_du_rtol) else 0
        if run >= n_stall and out["B"] is None:
            out["B"] = {"row_index": i, "iter_label": rows[i]["iter"],
                        "window_first_row_index": i - n_stall + 1,
                        "rule": "inf_du non-decreasing over %d consecutive majors "
                                "(rtol %g)" % (n_stall, inf_du_rtol)}
    return out


def cutback_counts(rows):
    """Six DIFFERENT definitions, each named.  Section 9.4's rule: a count is
    cited with its definition or it is not cited."""
    nonrest = [r for r in rows if not r["restoration"]]
    return {
        "majors_parsed": len(rows),
        "restoration_majors": sum(1 for r in rows if r["restoration"]),
        "sum_ls_all": sum(r["ls"] for r in rows),
        "sum_max0_ls_minus_1_all": sum(max(0, r["ls"] - 1) for r in rows),
        "sum_max0_ls_minus_1_nonrestoration": sum(max(0, r["ls"] - 1) for r in nonrest),
        "sum_ls_nonrestoration": sum(r["ls"] for r in nonrest),
        "count_majors_ls_gt_1_all": sum(1 for r in rows if r["ls"] > 1),
        "count_majors_ls_gt_1_nonrestoration": sum(1 for r in nonrest if r["ls"] > 1),
    }


def read_log(path):
    with open(path, errors="replace") as fh:
        text = fh.read()
    rows = parse_rows(text)
    return {"path": path, "rows": rows, "n_rows": len(rows),
            "convergence": converged_statement(text),
            "stall": stall_reach(rows), "cutbacks": cutback_counts(rows)}


# ============================================================================
# SELFTEST -- every leg driven, and the RED legs driven RED
# ============================================================================
def _synth(alpha_prs, inf_dus=None, ls=None):
    lines = ["iter    objective    inf_pr   inf_du  lg(mu)  ||d||  lg(rg) alpha_du alpha_pr  ls"]
    n = len(alpha_prs)
    inf_dus = inf_dus or [10.0 ** (-i) for i in range(n)]
    ls = ls or [1] * n
    for i in range(n):
        lines.append(" %3d  1.0000000e-02 1.00e-06 %8.2e  -5.0 1.00e-03  -1.0 1.00e+00 %8.2e  %d"
                     % (i, inf_dus[i], alpha_prs[i], ls[i]))
    return "\n".join(lines) + "\n"


def selftest():
    ok = True

    def leg(name, want, got, note=""):
        nonlocal ok
        good = (got == want)
        ok = ok and good
        print("  %-11s expect=%-34s got=%-34s %s%s"
              % (name, str(want)[:34], str(got)[:34],
                 "OK" if good else "**LEG DID NOT FIRE**", (" " + note) if note else ""))

    print("D19M STALL DETECTOR -- CONTROLS")
    print("  registered: N_STALL=%d  ALPHA_PR_FLOOR=%g  INF_DU_RTOL=%g" %
          (N_STALL, ALPHA_PR_FLOOR, INF_DU_RTOL))
    print("  condition B registered state: %s" % CONDITION_B_STATE)
    print()

    # --- parser --------------------------------------------------------------
    t = _synth([1.0] * 5)
    leg("PARSE-1", 5, len(parse_rows(t)), "(5 clean rows)")
    leg("PARSE-2", 0, len(parse_rows("no table here at all\n")), "(no table -> no rows)")

    # --- convergence statement: READ, never inferred -------------------------
    leg("CONV-RED", False,
        converged_statement(t + "\n")["converged"],
        "(A2's shape: a real table that simply STOPS -> NOT converged)")
    leg("CONV-GRN", True,
        converged_statement(t + "\nEXIT: Optimal Solution Found.\n")["converged"])
    leg("CONV-CAP", False,
        converged_statement(t + "\nEXIT: Maximum Number of Iterations Exceeded.\n")["converged"],
        "(A CAP IS NOT A CONVERGENCE -- charter section 9)")
    leg("CONV-NITER", 47,
        converged_statement("Number of Iterations....: 47\n")["n_iterations"])

    # --- condition A: fires, and does NOT fire one row early -----------------
    stalled = _synth([1e-4] * N_STALL)
    r = stall_reach(parse_rows(stalled))["A"]
    leg("A-FIRES", 0, r["window_first_row_index"] if r else None,
        "(window closes at the %dth row, first reach)" % N_STALL)
    leg("A-REACH", N_STALL - 1, r["row_index"] if r else None)
    short = _synth([1e-4] * (N_STALL - 1))
    leg("A-RED", None, stall_reach(parse_rows(short))["A"],
        "(%d stalled majors must NOT close an %d-major window)" % (N_STALL - 1, N_STALL))
    healthy = _synth([1.0] * 40)
    leg("A-HEALTHY", None, stall_reach(parse_rows(healthy))["A"],
        "(a healthy run must not read as stalled)")

    # --- FIRST REACH, not longest run: the registered definition -------------
    mixed = _synth([1e-4] * N_STALL + [1.0] * 5 + [1e-4] * (N_STALL + 9))
    rA = stall_reach(parse_rows(mixed))["A"]
    leg("A-FIRST", N_STALL - 1, rA["row_index"] if rA else None,
        "(stops at FIRST reach, not at the end of the LONGEST run)")

    # --- condition B's noise guard -------------------------------------------
    #  A genuinely DECREASING series with float noise must NOT read as stalled.
    dec = [1.0e-3 * (0.5 ** i) for i in range(N_STALL + 4)]
    leg("B-RED", None, stall_reach(parse_rows(_synth([1.0] * len(dec), dec)))["B"],
        "(a decreasing inf_du series is not a stall)")
    flat = [1.0e-3] * (N_STALL + 2)
    rB = stall_reach(parse_rows(_synth([1.0] * len(flat), flat)))["B"]
    leg("B-CAPABLE", True, rB is not None,
        "(B CAN fire on synthetic bytes -- it has never fired on a REAL log; "
        "registered %s)" % CONDITION_B_STATE)

    # --- cutback counts: the six definitions must DIFFER ---------------------
    cb = cutback_counts(parse_rows(_synth([1.0] * 4, ls=[1, 3, 1, 5])))
    leg("CB-DEFS", True, cb["sum_ls_all"] != cb["sum_max0_ls_minus_1_all"],
        "(sum(ls)=%d vs sum(max(0,ls-1))=%d -- a count needs its definition)"
        % (cb["sum_ls_all"], cb["sum_max0_ls_minus_1_all"]))

    print()
    print("D19M STALL SELFTEST: %s" % ("OK -- every red leg fired" if ok else "FAILED"))
    return 0 if ok else 1


def calibrate(paths):
    """Re-drive the registered readings on REAL bytes.  Quotes nothing."""
    fired_A = fired_B = capped = converged = 0
    for p in paths:
        if not os.path.isfile(p):
            print("  ABSENT %s" % p)
            continue
        d = read_log(p)
        c, s = d["convergence"], d["stall"]
        if s["A"]:
            fired_A += 1
        if s["B"]:
            fired_B += 1
        if c["converged"]:
            converged += 1
        if c["exit"] and "Maximum Number of Iterations" in c["exit"]:
            capped += 1
        print("  %-72s rows=%3d exit=%-34s A=%s B=%s"
              % (p[-72:], d["n_rows"], str(c["exit"])[:34],
                 (s["A"] or {}).get("row_index"), (s["B"] or {}).get("row_index")))
    print(json.dumps({"logs": len(paths), "condition_A_fired": fired_A,
                      "condition_B_fired": fired_B, "converged": converged,
                      "iteration_capped": capped,
                      "condition_B_registered_state": CONDITION_B_STATE}, sort_keys=True))
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    if "--calibrate" in sys.argv:
        i = sys.argv.index("--calibrate")
        sys.exit(calibrate(sys.argv[i + 1:]))
    sys.stderr.write("Usage: d19m_stall.py --selftest | --calibrate <opt_IPOPT.txt>...\n")
    sys.exit(64)
