#!/usr/bin/env python3
"""D6RF12 comparator -- the gates frozen in PREREGISTRATION.md section 5.

COMMITTED IN THE SAME COMMIT AS THE PRE-REGISTRATION, BEFORE ANY CONTAINER STARTS.

It REFUSES (exit 2) rather than degrades.  Every reader that can return a zero,
an emptiness or a pass has a planted control and is shown able to see a non-zero
BEFORE any verdict it produces is believed (CLAUDE.md rule 3).

WHAT THIS FILE FIXES RELATIVE TO d6rf11_grade.py, AND WHY:

  G3.  d6rf11_grade.py:111-113 counted `len(rows)` of ANY kind against a minimum
       of 1 and PRINTED the total as "FD sample rows".  It PASSED on a single
       `kind: "endpoint_dvs"` DV-inventory row written at log line 8, BEFORE any
       FD work, while the producer's terminal marker never printed and its first
       primal died at line 2748.  G3_FDSTEP here reads the KIND and requires the
       producer's OWN terminal marker -- two limbs, because either alone is
       forgeable by an early exit.

  G1.  Counted on `did not satisfy the prescribed tolerance`, NEVER on a raw grep
       of `Primal solution failed!`, which counts Python traceback frames.
       Measured: D8G pre-fix and D6RF11 each show 1 genuine failure against 17
       raw hits.  d6rf11_grade.py:20's comment carries that miscount; its
       THRESHOLD is 0 and correct either way, and that frozen file is not touched.
"""
import argparse
import json
import os
import re
import sys

# ---- THE FROZEN THRESHOLDS (PREREGISTRATION.md section 5) -----------------
G1_MAX_TOLERANCE_FAILURES = 0
G2_ACCEPT_FLOOR = 1.0e-05        # primalMinResTol 1e-8 x primalMinResTolDiff 1e3 (N-D43: the PRODUCT)
G3_MIN_FD_STEP_ROWS = 1
FD_STEP_KIND = "fd_step"
TERMINAL_MARKER = "D6RF3_FD_ENDPOINT_WRITTEN"
FD_JSONL = "d6rf3_fd_endpoint.jsonl"

# ---- section 4 axis (a): REPORTED WITH ITS PREDICTION, and gated only by G2 --
PRED_NUTILDA = 2.4e-07
PRED_BASIS = ("D6RF11 measured nuTilda 1.139494133e-05; the cleared D8G R1 arm drives the "
              "linear solve 47.0x further per outer step (1119.7 / 23.8); 1.139494133e-05 / 47.0")

RE_P_INITRES = re.compile(r"^p initRes:\s*([0-9eE+.\-]+)", re.M)
RE_TIMEHDR = re.compile(r"^Time = \S+\s*$", re.M)


def outer_initres(text, rx):
    """THE TRUE OUTER RESIDUAL: the FIRST match in the LAST `Time = ` block.

    NEVER THE LAST MATCH.  `primalResidualControl` prints one `initRes` line PER
    CORRECTOR from inside the corrector loop, so with `nNonOrthogonalCorrectors 12`
    there are 13 `p initRes` lines per outer step and the last is the residual of an
    almost-solved field.  MEASURED on D6RF11: the true outer p is 2.556601762e-05
    (2.557x OVER its 1.0e-05 floor) while the last corrector reads 1.719431323e-09
    -- understated 14,869x -- and d6rf11_grade.py:98, taking res[-1], graded that
    block PASS when it should have been FAIL.

    Returns (outer_value, n_lines_in_block, all_values_in_block) or None.
    """
    blocks = RE_TIMEHDR.split(text)
    for chunk in reversed(blocks):
        vals = rx.findall(chunk)
        if vals:
            return float(vals[0]), len(vals), [float(v) for v in vals]
    return None
RE_NUTILDA = re.compile(r"^nuTilda initRes:\s*([0-9eE+.\-]+)\s+finalRes:\s*([0-9eE+.\-]+)\s+nIters:\s*(\d+)", re.M)
RE_TOLFAIL = re.compile(r"did not satisfy the prescribed tolerance")

VOCAB = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")


def refuse(code, detail):
    print("REFUSE %s %s" % (code, json.dumps(detail, sort_keys=True)))
    sys.exit(2)


# =====================================================================
# G3-FDSTEP.  Driven in THREE directions by planted_control_g3() below.
# =====================================================================
def g3_fdstep(jsonl_text, log_text):
    rows, malformed = [], 0
    for line in jsonl_text.splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except ValueError:
            malformed += 1                      # counted, NEVER silently skipped
    kinds = {}
    for r in rows:
        k = r.get("kind", "<no kind field>")
        kinds[k] = kinds.get(k, 0) + 1
    n_fd = kinds.get(FD_STEP_KIND, 0)
    marker = TERMINAL_MARKER in log_text
    out = {"n_rows_total": len(rows), "n_malformed": malformed, "kinds": kinds,
           "n_fd_step_rows": n_fd, "min_required": G3_MIN_FD_STEP_ROWS,
           "terminal_marker": TERMINAL_MARKER, "terminal_marker_present": marker,
           "limb_fd_step_rows": n_fd >= G3_MIN_FD_STEP_ROWS,
           "limb_producer_completed": marker}
    out["verdict"] = "PASS" if (n_fd >= G3_MIN_FD_STEP_ROWS and marker) else "FAIL"
    return out


def planted_control_g3(jsonl_text, log_text):
    """THREE directions.  A gate that has only ever seen its passing case is how
    d6rf11_grade.py's G3 shipped.

      negative            this run's own file, unmodified          -> whatever it is
      positive            + one planted fd_step row + the marker    -> MUST PASS
      forged completion   + the planted row but marker ABSENT       -> MUST FAIL
    """
    planted = json.dumps({"kind": FD_STEP_KIND, "dv": "twist", "idx": 0,
                          "which": "central",
                          "row": {"h": 1.234e-03, "dJdx": 5.678e-04}}, sort_keys=True)
    pos = g3_fdstep(jsonl_text + "\n" + planted + "\n",
                    log_text + "\n%s %s n_rows=planted\n" % (TERMINAL_MARKER, FD_JSONL))
    forged = g3_fdstep(jsonl_text + "\n" + planted + "\n",
                       log_text.replace(TERMINAL_MARKER, "<MARKER-REMOVED-BY-CONTROL>"))
    ctrl = {"positive_planted_fd_step": pos["verdict"],
            "forged_completion_row_without_marker": forged["verdict"],
            "state": "EXERCISED-PASS" if (pos["verdict"] == "PASS"
                                          and forged["verdict"] == "FAIL") else "EXERCISED-FAIL"}
    if ctrl["state"] != "EXERCISED-PASS":
        refuse("PLANT-G3", ctrl)
    return ctrl


def planted_control_outer(text):
    """Rule 3 for the FIRST-MATCH reader, planted in the shape that actually fooled
    d6rf11_grade.py: ONE LARGE TRUE OUTER RESIDUAL FOLLOWED BY TWELVE SMALL CORRECTOR
    LINES.  The reader MUST return the LARGE one.  A reader that returns the small one
    is reading the last corrector and is refused.

    The control is driven in BOTH directions: the planted block must also be shown to
    contain a value the reader must NOT return.
    """
    big, small = 9.876e-03, 1.234e-11
    block = "\nTime = 999999\n" + "p initRes: %.6e finalRes: 1e-14 nIters: 2\n" % big
    for _ in range(12):
        block += "p initRes: %.6e finalRes: 1e-16 nIters: 4\n" % small
    got = outer_initres(text + block, RE_P_INITRES)
    ctrl = {"planted_true_outer": big, "planted_corrector_tail": small,
            "n_lines_in_planted_block": (got[1] if got else None),
            "reader_returned": (got[0] if got else None),
            "reader_returned_the_outer": bool(got and abs(got[0] - big) < 1e-15),
            "reader_returned_the_last_corrector": bool(got and abs(got[0] - small) < 1e-20)}
    ctrl["state"] = ("EXERCISED-PASS"
                     if (ctrl["reader_returned_the_outer"]
                         and not ctrl["reader_returned_the_last_corrector"]
                         and got[1] == 13) else "EXERCISED-FAIL")
    if ctrl["state"] != "EXERCISED-PASS":
        refuse("PLANT-OUTER", ctrl)
    return ctrl


def planted_control_log(text):
    """Rule 3 for the residual and tolerance-failure readers."""
    planted = (text + "\np initRes: 1.234000e-03 finalRes: 1e-12 nIters: 1\n"
                      "nuTilda initRes: 4.321000e-03 finalRes: 1e-12 nIters: 9\n"
                      "did not satisfy the prescribed tolerance 1e-08\n")
    res = RE_P_INITRES.findall(planted)
    nut = RE_NUTILDA.findall(planted)
    base_f = len(RE_TOLFAIL.findall(text))
    saw_res = bool(res) and abs(float(res[-1]) - 1.234e-03) < 1e-15
    saw_nut = bool(nut) and abs(float(nut[-1][0]) - 4.321e-03) < 1e-15
    saw_fail = len(RE_TOLFAIL.findall(planted)) == base_f + 1
    ctrl = {"reader_saw_planted_p_initRes": saw_res,
            "reader_saw_planted_nuTilda": saw_nut,
            "reader_saw_planted_tolerance_failure": saw_fail,
            "baseline_tolerance_failures": base_f,
            "state": "EXERCISED-PASS" if (saw_res and saw_nut and saw_fail) else "EXERCISED-FAIL"}
    if ctrl["state"] != "EXERCISED-PASS":
        refuse("PLANT-LOG", ctrl)
    return ctrl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--work", default="F_probe")
    ap.add_argument("--log", default=None)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    W = os.path.join(a.base, a.work)

    if a.log:
        logp = a.log if os.path.isabs(a.log) else os.path.join(a.base, a.log)
    else:
        c = sorted(f for f in os.listdir(a.base) if f.endswith(".log"))
        if len(c) != 1:
            refuse("READ", {"log_candidates": c,
                            "note": "name one with --log; picking by glob order is a coin flip"})
        logp = os.path.join(a.base, c[0])
    if not os.path.isfile(logp):
        refuse("READ", {"log_absent": logp})
    text = open(logp, errors="replace").read()

    R = {"item": "D6RF12", "log": logp,
         "controls": {"log": planted_control_log(text),
                      "outer_reader": planted_control_outer(text)}}

    # ---- G1: genuine tolerance failures, NOT traceback frames ---------------
    n_tolfail = len(RE_TOLFAIL.findall(text))
    n_rawgrep = len(re.findall(r"Primal solution failed!", text))
    R["G1"] = {"n_tolerance_failures": n_tolfail, "max": G1_MAX_TOLERANCE_FAILURES,
               "n_raw_grep_primal_solution_failed": n_rawgrep,
               "note": "the raw grep counts traceback frames and is REPORTED, NEVER GATED",
               "verdict": "PASS" if n_tolfail <= G1_MAX_TOLERANCE_FAILURES else "FAIL"}

    # ---- G2: last p initRes below the accept floor -------------------------
    got = outer_initres(text, RE_P_INITRES)
    if got is None:
        refuse("G2", {"zero_p_initRes_prints": logp,
                      "note": "refusing rather than reporting convergence from an empty read"})
    outer_p, n_in_block, all_p = got
    R["G2"] = {"outer_p_initRes": outer_p, "floor": G2_ACCEPT_FLOOR,
               "ratio_to_floor": outer_p / G2_ACCEPT_FLOOR,
               "n_p_lines_in_last_block": n_in_block,
               "last_corrector_p_initRes": all_p[-1],
               "understatement_if_last_were_used": (outer_p / all_p[-1]) if all_p[-1] else None,
               "read_as": "FIRST match in the LAST Time block -- the TRUE OUTER residual",
               "verdict": "PASS" if outer_p < G2_ACCEPT_FLOOR else "FAIL"}
    last_p = outer_p

    # ---- section 4 axis (a): nuTilda against its REGISTERED prediction ------
    nut = RE_NUTILDA.findall(text)
    if not nut:
        refuse("PRED-A", {"zero_nuTilda_prints": logp})
    ini, fin, nit = float(nut[-1][0]), float(nut[-1][1]), int(nut[-1][2])
    R["prediction_a"] = {"predicted_nuTilda": PRED_NUTILDA, "basis": PRED_BASIS,
                         "measured_nuTilda_initRes": ini, "finalRes": fin, "nIters": nit,
                         "reduction_within_outer_step": (ini / fin) if fin else None,
                         "ratio_measured_over_predicted": ini / PRED_NUTILDA,
                         "ratio_to_floor": ini / G2_ACCEPT_FLOOR,
                         "note": "REPORTED against its registered prediction; the GATE is G2."}

    # ---- G3-FDSTEP ---------------------------------------------------------
    p = os.path.join(W, FD_JSONL)
    if not os.path.exists(p):
        R["G3"] = {"file": p, "present": False, "verdict": "FAIL",
                   "note": "the FD producer wrote no output at all"}
        R["controls"]["g3"] = planted_control_g3("", text)
    else:
        jt = open(p, errors="replace").read()
        R["controls"]["g3"] = planted_control_g3(jt, text)
        g3 = g3_fdstep(jt, text)
        g3["file"] = p
        g3["present"] = True
        g3["newer_than_datum"] = None
        d = os.path.join(W, ".d6rf12_age_datum")
        if os.path.isfile(d):
            try:
                age = float(open(d).read().strip())
                g3["newer_than_datum"] = os.path.getmtime(p) > age
                if not g3["newer_than_datum"]:
                    g3["verdict"] = "FAIL"
                    g3["age_guard"] = "artefact NOT newer than the arm's own datum (rule 4)"
            except ValueError:
                refuse("G4", {"age_datum_unparseable": d})
        else:
            refuse("G4", {"age_datum_absent": d,
                          "note": "rule 4's age guard is NOT waived for want of a datum"})
        R["G3"] = g3

    # ---- composition -------------------------------------------------------
    gates = ("G1", "G2", "G3")
    R["verdict"] = "PASS" if all(R[g]["verdict"] == "PASS" for g in gates) else "GATE FAIL"
    if R["verdict"] not in VOCAB:
        refuse("VOCAB", {"token": R["verdict"]})

    print("VERDICT %s   G1=%s G2=%s G3=%s" % (R["verdict"], R["G1"]["verdict"],
                                              R["G2"]["verdict"], R["G3"]["verdict"]))
    print("  G1 genuine tolerance failures = %d (max %d); raw grep = %d [REPORTED, NOT GATED]"
          % (n_tolfail, G1_MAX_TOLERANCE_FAILURES, n_rawgrep))
    print("  G2 TRUE OUTER p initRes = %.6e  (floor %.1e, ratio %.4f)  "
          "[FIRST of %d lines in the block; the last reads %.6e, %.0fx smaller]"
          % (outer_p, G2_ACCEPT_FLOOR, outer_p / G2_ACCEPT_FLOOR, n_in_block,
             all_p[-1], (outer_p / all_p[-1]) if all_p[-1] else float("nan")))
    print("  PRED(a) nuTilda = %.6e  predicted %.1e  measured/predicted %.2fx  "
          "ratio to floor %.4f  reduction %.1fx  nIters %d"
          % (ini, PRED_NUTILDA, ini / PRED_NUTILDA, ini / G2_ACCEPT_FLOOR,
             (ini / fin) if fin else float("nan"), nit))
    print("  G3 fd_step rows = %d (min %d); terminal marker %s; kinds seen = %s"
          % (R["G3"].get("n_fd_step_rows", 0), G3_MIN_FD_STEP_ROWS,
             "PRESENT" if R["G3"].get("terminal_marker_present") else "ABSENT",
             json.dumps(R["G3"].get("kinds", {}), sort_keys=True)))
    print("  BOUNDS: PATCHED ROW ONLY -- not a verdict about DAFoam (charter two-row rule).")
    print("  BOUNDS: axis (b) clearing establishes the FD arm COMPLETED.  It does NOT")
    print("          discharge the charter's bright line: no step is shown to lie in the")
    print("          plateau, and one probe is not an FD table.")
    if a.json:
        json.dump(R, open(a.json, "w"), indent=1, sort_keys=True, default=str)
    return 0 if R["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
