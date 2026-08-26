#!/usr/bin/env python3
"""Curriculum D4 grader -- MACH wing constrained CD minimisation at fixed CL.

REFUSES (exit 2) rather than degrades.  CLAUDE.md rule 4.

The defect this grader is built against, verbatim from the supervisor's brief:
`A4/curriculum_D3/d3_grade.py`'s gate G3+G4 returned PASS at 0.0000 % with zero
sign flips OVER AN EMPTY COMPONENT SET -- a present-but-unparseable FD block
yielded an empty list WITH THE KEY PRESENT, the refusal tested key presence and
never non-emptiness, the plateau loop iterated zero times so a step was
"selected" without one comparison, and the discrimination control fired
correctly and certified a result it had not measured.

Therefore, here:
  * G5 refuses on an EMPTY **or SHORT** component set EXPLICITLY, BY COUNT,
    WITH THE COUNT PRINTED, against the count registered before compute.
  * Every loop that could iterate zero times asserts its own trip count and
    prints it.
  * G7 is a live negative control that DELIBERATELY empties and DELIBERATELY
    shortens the row list and requires a NAMED refusal from each.  A control
    that cannot make the gate refuse is not a control (L-302).
  * G6 plants a known perturbation into the artifact ON DISK, reads it back
    THROUGH THE SAME READER, and refuses if the reader cannot see it; and a
    blind reader -- one that ignores the path it is handed -- must be REFUSED.

Every graded number is read from a FILE.  MPI log splicing on this exact case
is MEASURED (A2 per_component_table §2.2, commit 79679a84): four ranks
interleave on one stdout and sever arrays mid-number.  Nothing here parses
stdout for a graded quantity; stdout is read only for provenance markers
(container uid, IDWarp .so md5) which are single short lines whose corruption
would make them fail to match rather than silently mis-read.
"""
import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime

# ================= REGISTERED CONSTANTS (PREREGISTRATION.md) ===============
N_COMPONENTS_REGISTERED = 5           # §6 -- named in advance, by name
COMPONENTS_REGISTERED = [["shape", 46], ["shape", 18], ["shape", 0],
                         ["twist", 0], ["patchV", 1]]
CL_TARGET = 0.5
CL_TOL_PER_MAJOR = 5.0e-4             # §4 band A
CL_TOL_FINAL = 1.0e-5                 # §4 band B (IPOPT constr_viol_tol)
DRAG_BAND_PCT = (25.0, 45.0)          # §4 band C
FD_BAND_PCT_PER_COMPONENT = 5.0       # §4 band D
FD_BAND_PCT_AGGREGATE = 5.0           # §4 band D
PLATEAU_TOL_PCT = 10.0                # §7
CD_BASELINE_A2 = 2.9619634e-02        # A2's own opt_IPOPT.txt iteration 0
NCELLS = 38304
RANKS = 4
DECOMP_METHOD = "scotch"
CPUSET_REGISTERED = [5, 6, 7, 9]      # §5b -- pinned before compute
DELIVERED_CORES_FLOOR = 3.0           # §5b -- of a 4-core quota
CAPS = {"P1": 5.0, "P2": 55.0, "O": 620.0, "ACC": 80.0, "F3": 120.0}
ITEM_CEILING_CORE_MIN = 880.0         # sum of the five registered arm caps

# ---- D4-DEF-7 REPAIR: the two clauses g_completion() NAMED AND NEVER RAN.
# TERMINAL_STATEMENT is checked POSITIONALLY -- as the LAST non-empty line of
# the producer's own log FILE -- and NOT as a substring anywhere in it.
# MEASURED, ON D4'S OWN FOUR ARM LOGS, BEFORE THIS WAS WRITTEN:
#   substring present : O yes, F3 yes, F yes, F2 yes   -> 4 of 4, DISCRIMINATES NOTHING
#   LAST non-empty    : O yes, F3 yes, F  no, F2 no    -> 2 of 4, exactly the rc=0 arms
# The crashed arms carry FOUR copies of the line mid-file (one per rank) and
# then eleven further lines of mpirun abort text.  The obvious implementation
# of this clause would have PASSED arm F -- the very arm that motivated
# D4-DEF-7 -- so it would have been a second dead lever inside the repair.
TERMINAL_STATEMENT = "Finalising parallel run"

# ---- ADDENDUM 2 (L-342, d4d0c29d): FIELD CLASSES.  "a bookkeeping failure
# invalidates the bookkeeping, never the physics artifacts".  Gates read
# PHYSICS fields only; an INFRASTRUCTURE field that is absent reads
# NOT_MEASURED, is disclosed in the verdict line, and the grade PROCEEDS.  An
# absent PHYSICS field still REFUSES.  Absent != present-but-garbage: a
# present value that does not parse REFUSES exactly as before.
FIELDS_PHYSICS = ("rc", "inspect_exit", "oomkilled", "terminal_statement",
                  "age_guard", "wall_s", "core_min", "cap_core_min",
                  "enforced_core_min", "DIGEST", "cpuset")
FIELDS_INFRASTRUCTURE = ("memavail_pre_GiB", "memavail_post_GiB",
                         "delivered", "siblings_pre", "siblings_post",
                         "cpu_series", "log")
NOT_MEASURED = "NOT_MEASURED"
# When an arm has NO ledger row, G1 takes its PHYSICS fields from the KERNEL
# RECORD of the arm's container, found by the launcher's own naming pattern
# d4_<ARM>_<stamp>; the record survives because the launcher registered no
# --rm.  Exactly one candidate container may stand in; zero or several refuse.
KERNEL_RECORD_NAME_PREFIX = "d4_%s_"
MD5_RUNSCRIPT = "2906d52a5dbed2bacbaeaf85a37d3fe8"
PLANT = 1.234e-03                     # rule 3

VOCAB = {"PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED",
         "PENDING"}


class Refuse(Exception):
    pass


def refuse(where, detail):
    raise Refuse("%s: %s" % (where, json.dumps(detail, sort_keys=True,
                                               default=str)[:1200]))


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


# ------------------------------------------------------------------ readers
def read_json(path, where):
    if not os.path.isfile(path):
        refuse(where, {"absent": path})
    if os.path.getsize(path) == 0:
        refuse(where, {"empty_file": path})
    with open(path) as fh:
        try:
            return json.load(fh)
        except Exception as exc:                       # noqa: BLE001
            refuse(where, {"unparseable": path, "error": repr(exc)[:300]})


IPOPT_ROW = re.compile(
    r"^\s*(\d+)r?\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s")


def read_ipopt(path, where="read_ipopt"):
    """Parse IPOPT's OWN output file.  This is written by IPOPT to
    `opt_IPOPT.txt`, not to stdout, so the MPI interleave cannot reach it."""
    if not os.path.isfile(path):
        refuse(where, {"absent": path})
    txt = open(path, errors="replace").read()
    rows = []
    for line in txt.splitlines():
        m = IPOPT_ROW.match(line)
        if m:
            try:
                rows.append({"iter": int(m.group(1)),
                             "objective": float(m.group(2)),
                             "inf_pr": float(m.group(3)),
                             "inf_du": float(m.group(4))})
            except ValueError:
                continue
    exits = [l.strip() for l in txt.splitlines() if l.strip().startswith("EXIT")]
    if not rows:
        refuse(where, {"no_iteration_rows_parsed": path,
                       "bytes": len(txt),
                       "note": "an IPOPT file with zero parsed rows is a "
                               "parser failure, not a converged run"})
    return {"rows": rows, "n_rows": len(rows), "exit_lines": exits,
            "path": os.path.abspath(path), "md5": md5_of(path)}


# ------------------------------------------------------------------- gates
def terminal_statement_ok(log_path):
    """D4-DEF-7 clause 2, POSITIONAL.  The producer's own log FILE must END on
    the terminal statement -- not merely contain it somewhere.

    Returns (ok, detail).  Never raises on a readable file: an absent or
    unreadable log is reported as a FAILED clause, not as a passing one.
    """
    if not os.path.isfile(log_path):
        return False, {"log_absent": log_path}
    try:
        raw = open(log_path, "rb").read().replace(b"\x00", b"")
        text = raw.decode("utf-8", errors="replace")
    except OSError as exc:
        return False, {"log_unreadable": log_path, "error": str(exc)}
    return terminal_statement_ok_text(text, log_path)


def terminal_statement_ok_text(text, log_path):
    """ADDENDUM 2: the positional clause on a TEXT, so a kernel-held `docker
    logs` stream is checked by the SAME rule as a log file.  Body moved
    verbatim from terminal_statement_ok()."""
    lines = [ln.rstrip() for ln in text.splitlines()]
    nonempty = [ln for ln in lines if ln.strip()]
    if not nonempty:
        return False, {"log_empty": log_path}
    last = nonempty[-1]
    ok = TERMINAL_STATEMENT in last
    # The non-discriminating reading is computed and REPORTED BESIDE the
    # verdict, never used as the verdict, so a reader can see for himself that
    # the substring form would not have caught this.
    anywhere = any(TERMINAL_STATEMENT in ln for ln in nonempty)
    return ok, {"log": os.path.basename(log_path),
                "last_nonempty_line": last[:160],
                "terminal_ok_POSITIONAL": bool(ok),
                "substring_anywhere_NOT_THE_TEST": bool(anywhere),
                "n_lines_after_last_occurrence": (
                    len(nonempty) - 1 - max(
                        (k for k, ln in enumerate(nonempty)
                         if TERMINAL_STATEMENT in ln), default=-1)
                    if anywhere else None)}


def g_completion(work, base, ledger_rows, arms_required):
    """G1.  Strict completion, DAFoam analogue of CLAUDE.md rule 4.

    Rule 4's field list (`T U p_rgh alphat nut k omega`) is the THERMAL
    family's and does not apply to a compressible DAFoam optimisation.  The
    clauses that DO apply are carried through unchanged: rc == 0, a terminal
    statement from the producer's own log FILE, and the AGE GUARD -- every
    graded artifact strictly NEWER than the case's own `0/` reference, which
    the launcher touches LAST at stage time and records in `.d4_age_datum`.

    D4-DEF-7 REPAIR.  In `curriculum_D4/d4_grade.py` this docstring named three
    clauses and the code implemented ONE.  `rc` was written into the output and
    NEVER COMPARED TO ZERO; there was no terminal-statement check at all; and
    `main()` consumed the age half alone, so `G1_completion_and_age` emitted
    PASS on a run whose required arm F reads `rc: 1`
    (`curriculum_D4/ARMF3_d4_grade_verdict.json` at HEAD carries both
    simultaneously).  All three clauses now run, ALL THREE reach the verdict,
    and `out["pass"]` is the conjunction.

    THE EXIT CODE IS READ FROM THE KERNEL'S RECORD.  `curriculum_D4/
    PREREGISTRATION.md`:256-257 registered that the exit comes from
    `docker inspect .State.ExitCode` "the kernel's own record, not from the
    harness's `$?`", with `OOMKilled` from the same place -- and no D4-family
    launcher except `A3/curriculum_D7R/d7r_run_arm.sh` ever implemented it.
    This grader cannot fix a frozen launcher (rule 6), so it does the next
    honest thing: it reads BOTH, requires the KERNEL's to be zero, and REFUSES
    on a disagreement between them rather than silently preferring either.  On
    every D4 arm graded to date the two agreed, so this clause is expected to
    be quiet -- and a clause that is quiet because the condition is absent is
    only known to work because the demonstration below MAKES it occur.
    """
    out = {"arms_required": arms_required, "arms": {}}
    datum_path = os.path.join(work, ".d4_age_datum")
    if not os.path.isfile(datum_path):
        refuse("G1", {"age_datum_absent": datum_path})
    datum = int(open(datum_path).read().strip())
    ref = os.path.join(work, "0", "U")
    if not os.path.isfile(ref):
        refuse("G1", {"age_reference_absent": ref})
    if int(os.path.getmtime(ref)) != datum:
        refuse("G1", {"age_reference_moved": ref,
                      "recorded": datum, "on_disk": int(os.path.getmtime(ref))})
    out["age_datum_epoch"] = datum
    n_checked = 0
    rc_failures, terminal_failures = [], []
    for arm in arms_required:
        hits = [r for r in ledger_rows if r.get("ARM") == arm]
        if not hits:
            refuse("G1", {"arm_absent_from_ledger": arm})
        r = hits[-1]

        # ---- CLAUSE 1: rc == 0, FROM THE KERNEL'S OWN RECORD ------------
        kernel_exit = r.get("inspect_exit")
        if kernel_exit is None:
            refuse("G1", {"kernel_exit_absent": arm,
                          "note": "no inspect(exit,oomkilled) field in the "
                                  "ledger row; the kernel's record was not "
                                  "captured and rc cannot be established. A "
                                  "launcher using --rm destroys it by "
                                  "construction."})
        try:
            kernel_rc = int(kernel_exit)
        except (TypeError, ValueError):
            refuse("G1", {"kernel_exit_unparseable": arm, "value": kernel_exit})
        harness_rc = r["rc"]
        if kernel_rc != harness_rc:
            refuse("G1", {"rc_disagreement": arm, "kernel": kernel_rc,
                          "harness": harness_rc,
                          "note": "the kernel's .State.ExitCode and the "
                                  "harness's $? disagree. This grader refuses "
                                  "rather than choose one silently."})
        oom = str(r.get("oomkilled")).lower()
        if oom not in ("false", "true", "none", "null"):
            refuse("G1", {"oomkilled_unparseable": arm, "value": r.get("oomkilled")})
        rc_ok = bool(kernel_rc == 0 and oom != "true")
        if not rc_ok:
            rc_failures.append({"arm": arm, "kernel_rc": kernel_rc,
                                "oomkilled": oom})

        # ---- CLAUSE 2: a terminal statement from the producer's log FILE --
        logname = r.get("log")
        if r.get("log_text") is not None:
            # ADDENDUM 2: the producer's log is the container's own stream,
            # read from the kernel record; the source is recorded beside it.
            t_ok, t_detail = terminal_statement_ok_text(
                r["log_text"], "docker logs " + str(r.get("container")))
            t_detail["source"] = "kernel_record"
        elif not logname:
            t_ok, t_detail = False, {
                "log_not_named_in_ledger": arm,
                "note": "the ledger row carries no log= field, so the "
                        "producer's own log FILE cannot be identified. "
                        "Reported as a FAILED clause, never as a passing one."}
        else:
            t_ok, t_detail = terminal_statement_ok(os.path.join(base, logname))
        if not t_ok:
            terminal_failures.append({"arm": arm, "detail": t_detail})

        out["arms"][arm] = {"rc": harness_rc, "kernel_rc": kernel_rc,
                            "source": r.get("source", "ledger_row"),
                            "field_sources": r.get("field_sources"),
                            "infrastructure_not_measured":
                                r.get("infra_not_measured", []),
                            "core_min": r["core_min"],
                            "oomkilled": r["oomkilled"],
                            "inspect_exit": r["inspect_exit"],
                            "rc_clause_pass": rc_ok,
                            "terminal_clause_pass": bool(t_ok),
                            "terminal_detail": t_detail}
        n_checked += 1
    if n_checked != len(arms_required):
        refuse("G1", {"arms_checked": n_checked,
                      "arms_required": len(arms_required)})
    out["n_arms_checked"] = n_checked
    out["rc_failures"] = rc_failures
    out["terminal_failures"] = terminal_failures
    out["rc_clause_pass"] = bool(not rc_failures)
    out["terminal_clause_pass"] = bool(not terminal_failures)
    # `pass` here is the TWO clauses this function owns.  The age limb is
    # computed by g_age() and conjoined at the verdict, so neither half can
    # carry the gate alone -- which is exactly how D4-DEF-7 happened.
    out["pass"] = bool(not rc_failures and not terminal_failures)
    return out


def g_age(work, artifacts, datum):
    """The age guard, applied by name to every graded artifact."""
    rows, n = [], 0
    for a in artifacts:
        p = os.path.join(work, a)
        if not os.path.isfile(p):
            refuse("G1-age", {"graded_artifact_absent": p})
        m = int(os.path.getmtime(p))
        rows.append({"artifact": a, "mtime": m, "newer_than_datum": m > datum})
        n += 1
    if n == 0:
        refuse("G1-age", {"artifacts_checked": 0,
                          "note": "an age guard that checked nothing is not a "
                                  "guard"})
    stale = [r for r in rows if not r["newer_than_datum"]]
    return {"n_checked": n, "rows": rows, "n_stale": len(stale),
            "pass": bool(not stale)}


def g_decomposition(work):
    """G8.  Determinism DEMONSTRATED, not asserted: the same decomposition,
    re-run, must produce the same processorN cell counts.

    Registered method: `scotch`, numberOfSubdomains 4, from the case's own
    `system/decomposeParDict`.  OpenFOAM's `scotchDecomp` exposes NO seed
    parameter, so determinism here is an EMPIRICAL claim about this build and
    this mesh -- it is not determinism by construction, and this gate is the
    only evidence for it.  That limitation is registered, not discovered.
    """
    a = read_json(os.path.join(work, "d4_decomp_A.json"), "G8")
    b = read_json(os.path.join(work, "d4_decomp_B.json"), "G8")
    if not a or not b:
        refuse("G8", {"empty_decomposition_map": {"A": len(a), "B": len(b)}})
    if len(a) != RANKS or len(b) != RANKS:
        refuse("G8", {"n_processor_dirs": {"A": len(a), "B": len(b)},
                      "expected": RANKS})
    tot_a, tot_b = sum(a.values()), sum(b.values())
    if tot_a != NCELLS:
        refuse("G8", {"cell_total_A": tot_a, "expected": NCELLS})
    dp = os.path.join(work, "system", "decomposeParDict")
    dict_txt = open(dp).read() if os.path.isfile(dp) else ""
    method_ok = bool(re.search(r"^\s*method\s+%s\s*;" % DECOMP_METHOD,
                               dict_txt, re.M))
    nsub_ok = bool(re.search(r"^\s*numberOfSubdomains\s+%d\s*;" % RANKS,
                             dict_txt, re.M))
    return {"A": a, "B": b, "identical": bool(a == b),
            "cells_A": tot_a, "cells_B": tot_b, "cells_expected": NCELLS,
            "method_registered": DECOMP_METHOD, "method_in_dict": method_ok,
            "numberOfSubdomains_in_dict": nsub_ok,
            "pass": bool(a == b and tot_a == NCELLS and tot_b == NCELLS
                         and method_ok and nsub_ok)}


def g_termination(ip):
    """G3.  DAFOAM_CHARTER §9.  A cap-stop is GATE REACHED or NOT A RESULT,
    NEVER PASS -- and never described by the size of the improvement."""
    conv = [l for l in ip["exit_lines"] if "Optimal Solution Found" in l]
    other = [l for l in ip["exit_lines"] if l not in conv]
    last = ip["rows"][-1]
    return {"exit_lines": ip["exit_lines"], "converged": bool(conv),
            "other_exit_lines": other, "n_majors": last["iter"],
            "n_rows_parsed": ip["n_rows"], "final_inf_pr": last["inf_pr"],
            "final_inf_du": last["inf_du"], "final_objective": last["objective"]}


def g_cl(hist):
    """G2.  CL feasibility per major, from the pyOptSparse history FILE."""
    cl = hist.get("CL")
    if cl is None:
        refuse("G2", {"CL_key_absent": sorted(hist.keys())})
    if not isinstance(cl, list) or len(cl) == 0:
        refuse("G2", {"CL_empty_or_not_a_list": type(cl).__name__,
                      "len": (len(cl) if isinstance(cl, list) else None),
                      "note": "a present-but-empty key is exactly the D3 "
                              "defect; this gate refuses on it BY COUNT"})
    n = len(cl)
    devs = [abs(v - CL_TARGET) for v in cl]
    n_compared = len(devs)
    if n_compared != n:
        refuse("G2", {"comparisons": n_compared, "majors": n})
    worst = max(devs)
    bad = [i for i, d in enumerate(devs) if d > CL_TOL_PER_MAJOR]
    return {"n_majors": n, "n_comparisons": n_compared,
            "worst_abs_dev": worst, "final_abs_dev": devs[-1],
            "band_per_major": CL_TOL_PER_MAJOR, "band_final": CL_TOL_FINAL,
            "n_outside_per_major_band": len(bad), "outside_indices": bad[:20],
            "pass_per_major": bool(not bad),
            "pass_final": bool(devs[-1] <= CL_TOL_FINAL)}


def g_drag(hist, ip):
    """G4.  Drag reduction against the band frozen before compute."""
    cd = hist.get("CD")
    if not cd:
        refuse("G4", {"CD_empty_or_absent": True, "len": len(cd or [])})
    cd0, cdf = cd[0], cd[-1]
    red = 100.0 * (cd0 - cdf) / cd0
    ip0 = ip["rows"][0]["objective"]
    return {"CD_first_major": cd0, "CD_final": cdf,
            "reduction_pct": red, "band_pct": list(DRAG_BAND_PCT),
            "in_band": bool(DRAG_BAND_PCT[0] <= red <= DRAG_BAND_PCT[1]),
            "CD_baseline_A2_record": CD_BASELINE_A2,
            "ipopt_iter0_objective": ip0,
            "baseline_matches_A2": bool(abs(ip0 - CD_BASELINE_A2)
                                        <= 1e-6 * abs(CD_BASELINE_A2))}


# ------------------------------- G5: the FD table, and the COUNT refusal ---
def g_fd(fd, where="G5"):
    """G5.  The endpoint FD table.

    THE COUNT REFUSAL, first, before anything else is read.  A present-but-
    empty or present-but-short `rows` list is the D3 defect verbatim and it is
    REFUSED HERE BY COUNT, with the count PRINTED.
    """
    rows = fd.get("rows")
    n_registered = N_COMPONENTS_REGISTERED
    if rows is None:
        refuse(where, {"rows_key_absent": True, "n_rows": 0,
                       "n_registered": n_registered})
    if not isinstance(rows, list):
        refuse(where, {"rows_not_a_list": type(rows).__name__,
                       "n_registered": n_registered})
    n_rows = len(rows)
    if n_rows == 0:
        refuse(where, {"COUNT_REFUSAL": "empty component set",
                       "n_rows": 0, "n_registered": n_registered})
    if n_rows != n_registered:
        refuse(where, {"COUNT_REFUSAL": "short or long component set",
                       "n_rows": n_rows, "n_registered": n_registered})
    got = [[r.get("dv"), r.get("idx")] for r in rows]
    if got != COMPONENTS_REGISTERED:
        refuse(where, {"COUNT_REFUSAL": "component set is not the registered "
                                        "set, in the registered order",
                       "n_rows": n_rows, "got": got,
                       "registered": COMPONENTS_REGISTERED})

    eta = float(fd["eta_used"].strip("'\"") if isinstance(fd["eta_used"], str)
                else fd["eta_used"])
    graded, near_zero, ungradeable = [], [], []
    n_plateau_comparisons = 0
    for r in rows:
        tag = "%s[%d]" % (r["dv"], r["idx"])
        if r.get("status") != "PLANNED":
            (near_zero if r.get("status") == "NEAR_ZERO"
             else ungradeable).append({"component": tag,
                                       "status": r.get("status"),
                                       "J_adj": r.get("J_adj"),
                                       "max_clearance": r.get("max_clearance")})
            continue
        fdb = r.get("fd") or {}
        lo, hi = fdb.get("s_lo"), fdb.get("s_hi")
        if not (lo and hi and lo.get("ok") and hi.get("ok")):
            ungradeable.append({"component": tag, "status": "FD_STEP_FAILED",
                                "s_lo": lo, "s_hi": hi})
            continue
        d_lo = float(str(lo["d"]).strip("'\""))
        d_hi = float(str(hi["d"]).strip("'\""))
        j = float(str(r["J_adj"]).strip("'\""))
        if d_hi == 0.0:
            ungradeable.append({"component": tag, "status": "FD_ZERO_AT_S_HI"})
            continue
        plateau = 100.0 * abs(d_hi - d_lo) / abs(d_hi)
        n_plateau_comparisons += 1
        rel = 100.0 * abs(j - d_hi) / abs(d_hi)
        graded.append({"component": tag, "s_lo": lo["step"], "s_hi": hi["step"],
                       "d_lo": d_lo, "d_hi": d_hi, "J_adj": j,
                       "plateau_pct": plateau,
                       "plateau_ok": bool(plateau <= PLATEAU_TOL_PCT),
                       "rel_err_pct": rel,
                       "in_band": bool(rel <= FD_BAND_PCT_PER_COMPONENT),
                       "sign_flip": bool(j * d_hi < 0.0),
                       "C_lo": r.get("C_lo"), "C_hi": r.get("C_hi")})

    # a plateau loop that iterated zero times "selected" nothing -- D3's defect
    if n_plateau_comparisons != len(graded):
        refuse(where, {"plateau_comparisons": n_plateau_comparisons,
                       "graded_rows": len(graded)})
    if graded:
        num = math.sqrt(sum((g["J_adj"] - g["d_hi"]) ** 2 for g in graded))
        den = math.sqrt(sum(g["d_hi"] ** 2 for g in graded))
        agg = 100.0 * num / den if den else float("inf")
    else:
        agg = None
    n_flips = sum(1 for g in graded if g["sign_flip"])
    n_no_plateau = sum(1 for g in graded if not g["plateau_ok"])
    return {"n_rows": n_rows, "n_registered": n_registered,
            "eta_used": eta, "eta_floored": fd.get("eta_floored"),
            "n_graded": len(graded), "n_near_zero": len(near_zero),
            "n_ungradeable": len(ungradeable),
            "n_plateau_comparisons": n_plateau_comparisons,
            "graded": graded, "near_zero": near_zero,
            "ungradeable": ungradeable,
            "aggregate_rel_err_pct": agg,
            "aggregate_band_pct": FD_BAND_PCT_AGGREGATE,
            "n_sign_flips": n_flips, "n_without_plateau": n_no_plateau,
            "coverage": "%d of %d" % (len(graded), n_registered)}


# ------------------------------------------------- G6/G7: the live controls
def planted_zero_control(fd_path, workdir, reader=read_json):
    """G6.  Rule 3.  Plant a KNOWN perturbation into the artifact ON DISK,
    read it back THROUGH THE SAME READER, and refuse if the reader cannot see
    it.  A zero from a reader not shown able to see a non-zero is not evidence.
    """
    before = md5_of(fd_path)
    base = reader(fd_path, "G6-base")
    baseg = g_fd(base, "G6-base")
    if baseg["n_graded"] == 0:
        # the plant needs a graded row to move; if there is none, SAY SO
        return {"pass": False, "reason": "NO_GRADED_ROW_TO_PLANT_INTO",
                "n_graded": 0,
                "note": "the control could not be run; this is reported as "
                        "an unmeasured channel, never as a passing control"}
    if not os.path.isdir(workdir):
        os.makedirs(workdir)
    planted_path = os.path.join(workdir, "d4_fd_endpoint.PLANTED.json")
    doc = reader(fd_path, "G6-copy")
    moved = None
    for r in doc["rows"]:
        if r.get("status") == "PLANNED" and (r.get("fd") or {}).get("s_hi", {}).get("ok"):
            old = float(str(r["fd"]["s_hi"]["d"]).strip("'\""))
            r["fd"]["s_hi"]["d"] = repr(old * (1.0 + PLANT))
            moved = {"component": "%s[%d]" % (r["dv"], r["idx"]),
                     "from": old, "to": old * (1.0 + PLANT)}
            break
    if moved is None:
        return {"pass": False, "reason": "NO_PLANTABLE_ROW"}
    with open(planted_path, "w") as fh:
        json.dump(doc, fh)
    plantedg = g_fd(reader(planted_path, "G6-planted"), "G6-planted")
    seen_channels = {
        "rel_err_pct": abs(plantedg["graded"][0]["rel_err_pct"]
                           - baseg["graded"][0]["rel_err_pct"]) > 1e-9,
        "plateau_pct": abs(plantedg["graded"][0]["plateau_pct"]
                           - baseg["graded"][0]["plateau_pct"]) > 1e-9,
        "aggregate": abs((plantedg["aggregate_rel_err_pct"] or 0.0)
                         - (baseg["aggregate_rel_err_pct"] or 0.0)) > 1e-12,
    }
    after = md5_of(fd_path)
    out = {"plant": PLANT, "moved": moved, "channel_seen": seen_channels,
           "src_md5_before": before, "src_md5_after": after,
           "src_unchanged": bool(before == after),
           "pass": bool(all(seen_channels.values()) and before == after)}
    os.remove(planted_path)
    if not out["pass"]:
        refuse("G6", out)
    return out


def negative_control(fd_path, workdir):
    """G6b.  The control must be able to FAIL.  A deliberately BLIND reader --
    one that returns the unperturbed document whatever path it is handed --
    must be REFUSED.  A planted-zero control that cannot refuse is not a
    control."""
    def blind(_p, where=None, _real=fd_path):
        return read_json(_real, where or "blind")
    try:
        planted_zero_control(fd_path, workdir, reader=blind)
    except Refuse as exc:
        return {"pass": True, "refused_with": str(exc)[:300]}
    return {"pass": False, "refused_with": None,
            "note": "the blind reader was ACCEPTED -- G6 is not a control"}


def count_controls(fd_path, workdir):
    """G7.  THE control this grader exists for.  Hand the FD gate (a) an EMPTY
    row list and (b) a SHORT row list, and require a NAMED refusal from each,
    with the count printed.  L-302: an instrument that cannot say "I measured
    nothing" will report a number it did not measure."""
    if not os.path.isdir(workdir):
        os.makedirs(workdir)
    results = {}
    for label, mutate in (
        ("empty", lambda d: d.update({"rows": []})),
        ("short", lambda d: d.update({"rows": d["rows"][:2]})),
        ("reordered", lambda d: d.update({"rows": list(reversed(d["rows"]))})),
        ("key_absent", lambda d: d.pop("rows", None)),
    ):
        doc = read_json(fd_path, "G7-src")
        mutate(doc)
        p = os.path.join(workdir, "d4_fd_endpoint.G7_%s.json" % label)
        with open(p, "w") as fh:
            json.dump(doc, fh)
        try:
            g_fd(read_json(p, "G7-%s" % label), "G7-%s" % label)
            results[label] = {"pass": False, "refused_with": None,
                              "note": "mutation was ACCEPTED"}
        except Refuse as exc:
            results[label] = {"pass": True, "refused_with": str(exc)[:400]}
        os.remove(p)
    results["pass"] = all(v["pass"] for k, v in results.items() if k != "pass")
    return results


def g_placement(p1dir, ledger_rows):
    """G12.  CPU PLACEMENT -- MEASURED, never inferred from the quota flag.

    `mpirun` inside a `--cpus=N` container binds rank 0 to the FIRST CORE OF
    THE HOST TOPOLOGY; concurrent containers collide there and throughput
    collapses as 1/N while the box reports itself idle (MEASURED, D13 lane,
    2026-08-25: 0.250 cores delivered against a 1.0-core quota, host 61 % idle).
    `--cpus=4` does NOT hand out four distinct cores.

    This gate refuses BY COUNT on a short set of per-rank placement files, for
    the same reason G5 does: a placement gate that reads zero ranks and reports
    no collision has measured nothing.

    It also exists to stop a specific FALSE FINDING.  A slow adjoint at np=4
    reads exactly like GMRES stagnation, which is a REAL failure mode measured
    on this ladder at N=52.  No adjoint-conditioning finding may be recorded by
    this item until this gate has ruled out core contention.
    """
    import glob
    files = sorted(glob.glob(os.path.join(p1dir, "d4_placement_rank*.json")))
    n_files = len(files)
    if n_files == 0:
        refuse("G12", {"COUNT_REFUSAL": "no per-rank placement files",
                       "n_files": 0, "n_expected": RANKS, "dir": p1dir})
    if n_files != RANKS:
        refuse("G12", {"COUNT_REFUSAL": "short or long placement set",
                       "n_files": n_files, "n_expected": RANKS})
    ranks, n_read = {}, 0
    for f in files:
        d = read_json(f, "G12")
        if "rank" not in d or "affinity" not in d:
            refuse("G12", {"placement_file_malformed": f,
                           "keys": sorted(d.keys())})
        if not d["affinity"]:
            refuse("G12", {"empty_affinity_mask": f})
        ranks[int(d["rank"])] = sorted(int(c) for c in d["affinity"])
        n_read += 1
    if n_read != RANKS or sorted(ranks.keys()) != list(range(RANKS)):
        refuse("G12", {"ranks_read": sorted(ranks.keys()), "expected": RANKS})
    union = sorted(set(c for v in ranks.values() for c in v))
    inside = bool(set(union) <= set(CPUSET_REGISTERED))
    # the defect's signature: every rank pinned to ONE shared core
    singles = [v[0] for v in ranks.values() if len(v) == 1]
    collided = bool(len(singles) == RANKS and len(set(singles)) < RANKS)
    distinct = bool(len(singles) == RANKS and len(set(singles)) == RANKS)
    delivered_rows, n_delivered = [], 0
    for r in ledger_rows:
        dv = (r.get("delivered") or "").split()
        val = None
        if dv and dv[0] not in ("NOT_MEASURED", ""):
            try:
                val = float(dv[0])
            except ValueError:
                val = None
        delivered_rows.append({"arm": r["ARM"], "cpuset": r.get("cpuset"),
                               "delivered_cores_mean": val,
                               "raw": r.get("delivered"),
                               "siblings_pre": r.get("siblings_pre"),
                               "siblings_post": r.get("siblings_post"),
                               "cpuset_as_registered": bool(
                                   r.get("cpuset") ==
                                   ",".join(str(c) for c in CPUSET_REGISTERED))})
        if val is not None:
            n_delivered += 1
    mpi_arms = [d for d in delivered_rows
                if d["arm"] in ("P2", "O", "F")
                and d["delivered_cores_mean"] is not None]
    starved = [d for d in mpi_arms
               if d["delivered_cores_mean"] < DELIVERED_CORES_FLOOR]
    return {"n_placement_files": n_files, "n_ranks_read": n_read,
            "rank_affinity": ranks, "affinity_union": union,
            "cpuset_registered": CPUSET_REGISTERED,
            "affinity_inside_cpuset": inside,
            "all_ranks_on_distinct_single_cores": distinct,
            "COLLISION_all_ranks_share_a_core": collided,
            "delivered": delivered_rows,
            "n_arms_with_delivered_measurement": n_delivered,
            "delivered_floor": DELIVERED_CORES_FLOOR,
            "arms_below_floor": [d["arm"] for d in starved],
            "pass": bool(inside and not collided and distinct
                         and not starved and mpi_arms)}


# ------------------------------------------------------------------ ledger
LEDGER_RE = re.compile(
    r"ARM=(?P<ARM>\S+)\s+ROW=(?P<ROW>\S+)\s+IMG=(?P<IMG>\S+)\s+"
    r"DIGEST=(?P<DIGEST>\S+)\s+rc=(?P<rc>-?\d+)\s+wall_s=(?P<wall_s>\d+)\s+"
    r"ranks=(?P<ranks>\d+)\s+core_min=(?P<core_min>[\d.]+)\s+"
    r"cap_core_min=(?P<cap>[\d.]+)\s+enforced_wall_s=(?P<ewall>\d+)\s+"
    r"enforced_core_min=(?P<ecore>[\d.]+)\s+memory=(?P<mem>\S+)\s+"
    r"inspect\(exit,oomkilled\)=\[(?P<inspect>[^\]]*)\]\s+"
    r"memavail_pre_GiB=(?P<mempre>[\d.]+|NOT_MEASURED)\s+memavail_post_GiB=(?P<mempost>[\d.]+|NOT_MEASURED)\s+"
    r"cpuset=(?P<cpuset>\S+)\s+delivered_cores_mean=\[(?P<delivered>[^\]]*)\]\s+"
    r"siblings_pre=\[(?P<sibpre>[^\]]*)\]\s+siblings_post=\[(?P<sibpost>[^\]]*)\]"
    r"(?:\s+log=(?P<log>\S+))?")


def read_ledger(path):
    if not os.path.isfile(path):
        refuse("ledger", {"absent": path})
    rows = []
    for line in open(path, errors="replace"):
        m = LEDGER_RE.search(line)
        if not m:
            continue
        g = m.groupdict()
        parts = g["inspect"].split()
        rows.append({"ARM": g["ARM"], "ROW": g["ROW"], "IMG": g["IMG"],
                     "DIGEST": g["DIGEST"], "rc": int(g["rc"]),
                     "wall_s": int(g["wall_s"]), "ranks": int(g["ranks"]),
                     "core_min": float(g["core_min"]),
                     "cap_core_min": float(g["cap"]),
                     "enforced_core_min": float(g["ecore"]),
                     "memory": g["mem"],
                     "inspect_exit": (parts[0] if parts else None),
                     "oomkilled": (parts[1] if len(parts) > 1 else None),
                     "memavail_pre_GiB": (None if g["mempre"] == NOT_MEASURED
                                          else float(g["mempre"])),
                     "memavail_post_GiB": (None if g["mempost"] == NOT_MEASURED
                                           else float(g["mempost"])),
                     "cpuset": g["cpuset"], "delivered": g["delivered"],
                     "siblings_pre": g["sibpre"], "siblings_post": g["sibpost"],
                     "log": g.get("log"), "source": "ledger_row",
                     "infra_not_measured": [k for k, v in (
                         ("memavail_pre_GiB", g["mempre"]),
                         ("memavail_post_GiB", g["mempost"]),
                         ("delivered", g["delivered"]),
                         ("siblings_pre", g["sibpre"]),
                         ("siblings_post", g["sibpost"]))
                         if NOT_MEASURED in str(v)]})
    if not rows:
        refuse("ledger", {"no_rows_parsed": path,
                          "note": "a ledger with zero parsed rows is a parser "
                                  "failure, not a costless run"})
    return rows


# ================= ADDENDUM 2: THE KERNEL-RECORD FALLBACK FOR G1 ===========
def docker_ps_a_names(prefix):
    out = subprocess.run(["sudo", "-n", "docker", "ps", "-a", "--format",
                          "{{.Names}}", "--filter", "name=^%s" % prefix],
                         capture_output=True, text=True)
    if out.returncode != 0:
        return None
    return [n for n in out.stdout.split() if n.startswith(prefix)]


def docker_inspect(name):
    out = subprocess.run(["sudo", "-n", "docker", "inspect", name],
                         capture_output=True, text=True)
    if out.returncode != 0:
        refuse("G1", {"kernel_record_inspect_failed": name,
                      "stderr": out.stderr[:300]})
    try:
        return json.loads(out.stdout)[0]
    except (ValueError, IndexError) as exc:
        refuse("G1", {"kernel_record_unparseable": name, "error": str(exc)})


def docker_logs(name):
    out = subprocess.run(["sudo", "-n", "docker", "logs", name],
                         capture_output=True)
    if out.returncode != 0:
        refuse("G1", {"kernel_record_logs_failed": name})
    return (out.stdout + out.stderr).replace(b"\x00", b"").decode(
        "utf-8", errors="replace")


def parse_docker_ts(s):
    s = s.strip()
    if s.endswith("Z"):
        s = s[:-1]
    if "." in s:
        head, frac = s.split(".", 1)
        s = head + "." + (frac + "000000")[:6]
    return datetime.fromisoformat(s)


def kernel_record_row(arm, name, insp, log_text, registered_cap):
    """A ledger-shaped row whose PHYSICS fields come from `docker inspect` and
    the container's own log stream, with the SOURCE recorded per field, and
    whose INFRASTRUCTURE fields -- the ones only a live poller could have
    measured -- are NOT_MEASURED.  Nothing is invented.  Pure function of the
    inspect dict so the selftest can drive it."""
    st, hc = insp["State"], insp["HostConfig"]
    if st.get("Running"):
        refuse("G1", {"kernel_record_still_running": name})
    for k in ("ExitCode", "StartedAt", "FinishedAt"):
        if k not in st:
            refuse("G1", {"kernel_record_physics_field_absent": k,
                          "container": name})
    t0, t1 = parse_docker_ts(st["StartedAt"]), parse_docker_ts(st["FinishedAt"])
    wall = int(round((t1 - t0).total_seconds()))
    if wall <= 0:
        refuse("G1", {"kernel_record_wall_nonpositive": wall, "container": name})
    src = "docker inspect %s" % name
    return {"ARM": arm, "ROW": "SHIPPED",
            "IMG": insp.get("Config", {}).get("Image", ""),
            "DIGEST": insp.get("Image", ""), "rc": int(st["ExitCode"]),
            "wall_s": wall, "ranks": RANKS,
            "core_min": round(wall * RANKS / 60.0, 3),
            "cap_core_min": registered_cap, "enforced_core_min": registered_cap,
            "memory": "%dg" % (int(hc.get("Memory", 0)) // 2**30),
            "inspect_exit": str(st["ExitCode"]),
            "oomkilled": str(bool(st.get("OOMKilled"))).lower(),
            "memavail_pre_GiB": None, "memavail_post_GiB": None,
            "cpuset": hc.get("CpusetCpus", ""), "delivered": NOT_MEASURED,
            "siblings_pre": NOT_MEASURED, "siblings_post": NOT_MEASURED,
            "log": None, "log_text": log_text, "source": "kernel_record",
            "container": name, "started": st["StartedAt"],
            "finished": st["FinishedAt"],
            "field_sources": {
                "rc": src + " .State.ExitCode",
                "inspect_exit": src + " .State.ExitCode",
                "oomkilled": src + " .State.OOMKilled",
                "wall_s": src + " .State.StartedAt/.State.FinishedAt",
                "core_min": "wall_s x %d / 60" % RANKS,
                "DIGEST": src + " .Image",
                "cpuset": src + " .HostConfig.CpusetCpus",
                "memory": src + " .HostConfig.Memory",
                "terminal_statement": "docker logs %s (positional)" % name,
                "cap_core_min": "registered CAPS table"},
            "infra_not_measured": ["memavail_pre_GiB", "memavail_post_GiB",
                                   "delivered", "siblings_pre",
                                   "siblings_post", "cpu_series", "log"]}


def kernel_record_fallback(arm, ledger_rows):
    """If `arm` has no ledger row, find its container by the launcher's naming
    pattern.  Exactly one must exist; zero or several refuse."""
    if any(r.get("ARM") == arm for r in ledger_rows):
        return None
    names = docker_ps_a_names(KERNEL_RECORD_NAME_PREFIX % arm)
    if names is None:
        refuse("G1", {"arm_absent_from_ledger": arm,
                      "kernel_record_lookup_failed": "docker ps -a"})
    if len(names) != 1:
        refuse("G1", {"arm_absent_from_ledger": arm,
                      "kernel_record_candidates": names,
                      "note": "exactly one container may stand in for a "
                              "missing row; zero or several is a refusal"})
    name = names[0]
    return kernel_record_row(arm, name, docker_inspect(name),
                             docker_logs(name), CAPS.get(arm))


def g_caps(ledger_rows):
    """G10.  The enforced cap must EQUAL the registered cap, per arm, read back
    from the ledger the launcher wrote -- not from the launcher's own claim."""
    rows, n = [], 0
    for r in ledger_rows:
        reg = CAPS.get(r["ARM"])
        if reg is None:
            refuse("G10", {"unregistered_arm_in_ledger": r["ARM"]})
        rows.append({"arm": r["ARM"], "registered": reg,
                     "ledger_cap": r["cap_core_min"],
                     "enforced": r["enforced_core_min"],
                     "actual": r["core_min"],
                     "cap_equals_registered": bool(
                         abs(r["cap_core_min"] - reg) < 1e-9
                         and abs(r["enforced_core_min"] - reg) <= 0.02),
                     "within_cap": bool(r["core_min"] <= reg + 1e-9)})
        n += 1
    if n == 0:
        refuse("G10", {"arms_checked": 0})
    total = sum(r["actual"] for r in rows)
    return {"n_arms": n, "rows": rows, "total_core_min": total,
            "item_ceiling": ITEM_CEILING_CORE_MIN,
            "within_item_ceiling": bool(total <= ITEM_CEILING_CORE_MIN),
            "pass": bool(all(r["cap_equals_registered"] and r["within_cap"]
                             for r in rows)
                         and total <= ITEM_CEILING_CORE_MIN)}


def g_toolchain(ledger_rows, work, logs, extra_texts=None):
    """G9.  DAFOAM_CHARTER §11: the identity is the image hash, never a version
    string.  Also records the IDWarp .so md5 the run actually imported."""
    so = {}
    n_logs = 0
    for lp in logs:
        if not os.path.isfile(lp):
            continue
        n_logs += 1
        for line in open(lp, errors="replace"):
            if "D4S_IDWARP_SO_MD5:" in line:   # D4S-GRADER-DEF-1: the string the container prints
                so.setdefault(os.path.basename(lp),
                              line.split("D4S_IDWARP_SO_MD5:")[1].strip())
    for label, text in (extra_texts or {}).items():
        n_logs += 1
        for line in text.splitlines():
            if "D4S_IDWARP_SO_MD5:" in line:
                so.setdefault(label, line.split("D4S_IDWARP_SO_MD5:")[1].strip())
    if n_logs == 0:
        refuse("G9", {"no_arm_logs_found": logs})
    digests = sorted({r["DIGEST"] for r in ledger_rows})
    rowlabels = sorted({r["ROW"] for r in ledger_rows})
    uniq_so = sorted(set(so.values()))
    return {"n_logs_read": n_logs, "digests": digests, "rows": rowlabels,
            "idwarp_so_md5_by_log": so, "idwarp_so_md5_distinct": uniq_so,
            "single_toolchain": bool(len(digests) == 1 and len(uniq_so) <= 1),
            "pass": bool(len(digests) >= 1 and len(uniq_so) == 1)}


# ------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--arms", default="P1,P2,O,F3")   # ADDENDUM 2: the arm list is REGISTERED
    ap.add_argument("--out", required=True)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    verdicts, report = {}, {}
    try:
        ledger_rows = read_ledger(os.path.join(a.base, "ledger.txt"))
        arms = [x for x in a.arms.split(",") if x]
        # ---- ADDENDUM 2: kernel-record fallback for arms with no ledger row
        report["G1_kernel_record_fallback"] = {}
        for arm in arms:
            fb = kernel_record_fallback(arm, ledger_rows)
            if fb is not None:
                ledger_rows.append(fb)
                report["G1_kernel_record_fallback"][arm] = {
                    k: v for k, v in fb.items() if k != "log_text"}
        report["field_classes"] = {"physics": list(FIELDS_PHYSICS),
                                   "infrastructure": list(FIELDS_INFRASTRUCTURE)}
        report["NOT_MEASURED"] = {r["ARM"]: r.get("infra_not_measured", [])
                                  for r in ledger_rows
                                  if r.get("infra_not_measured")}
        report["G1_completion"] = g_completion(a.work, a.base, ledger_rows, arms)
        datum = report["G1_completion"]["age_datum_epoch"]

        report["G10_caps"] = g_caps(ledger_rows)
        verdicts["G10_cap_discipline"] = ("PASS" if report["G10_caps"]["pass"]
                                          else "GATE FAIL")

        logs = [os.path.join(a.base, f) for f in sorted(os.listdir(a.base))
                if f.endswith(".log")]
        report["G9_toolchain"] = g_toolchain(
            ledger_rows, a.work, logs,
            extra_texts={"docker_logs:" + r["container"]: r["log_text"]
                         for r in ledger_rows if r.get("log_text") is not None})
        verdicts["G9_toolchain_identity"] = (
            "PASS" if report["G9_toolchain"]["pass"] else "GATE FAIL")

        # ---- G12 CPU placement, measured
        report["G12_placement"] = g_placement(
            os.path.join(a.base, "P1"), ledger_rows)
        verdicts["G12_cpu_placement"] = (
            "PASS" if report["G12_placement"]["pass"] else "GATE FAIL")

        # ---- G8 decomposition determinism
        report["G8_decomposition"] = g_decomposition(
            os.path.join(a.base, "P1"))
        verdicts["G8_decomposition_determinism"] = (
            "PASS" if report["G8_decomposition"]["pass"] else "GATE FAIL")

        # ---- G11 memory envelope (DAFOAM_CHARTER §7)
        oom = [r["ARM"] for r in ledger_rows if str(r["oomkilled"]).lower() == "true"]
        report["G11_memory"] = {"arms_oomkilled": oom,
                                "n_arms": len(ledger_rows),
                                "pass": bool(not oom)}
        verdicts["G11_memory_envelope"] = (
            "PASS" if not oom else "NOT A RESULT")

        # ---- the optimisation arm
        ip = read_ipopt(os.path.join(a.work, "opt_IPOPT.txt"))
        report["G3_termination"] = g_termination(ip)
        hist = read_json(os.path.join(a.work, "d4_major_history.json"), "G2")
        report["G2_cl_feasibility"] = g_cl(hist)
        report["G4_drag"] = g_drag(hist, ip)
        report["G1_age"] = g_age(a.work,
                                 ["opt_IPOPT.txt", "OptView.hst",
                                  "d4_major_history.json",
                                  "d4_fd_endpoint.json"], datum)
        # D4-DEF-7 REPAIR AT THE VERDICT.  The frozen grader read the age limb
        # ALONE here -- `report["G1_completion"]` was computed and consumed by
        # NO verdict in either file -- so a gate named for completion could
        # emit PASS on a required arm that exited non-zero.  All three clauses
        # now reach the label, and each is reported separately so a future
        # reader can see WHICH one failed rather than only THAT the gate did.
        report["G1_limbs"] = {
            "rc_clause_pass": report["G1_completion"]["rc_clause_pass"],
            "terminal_clause_pass":
                report["G1_completion"]["terminal_clause_pass"],
            "age_clause_pass": report["G1_age"]["pass"]}
        verdicts["G1_completion_and_age"] = (
            "PASS" if (report["G1_completion"]["rc_clause_pass"]
                       and report["G1_completion"]["terminal_clause_pass"]
                       and report["G1_age"]["pass"])
            else "NOT A RESULT")

        cap_stopped = not report["G3_termination"]["converged"]
        if report["G3_termination"]["converged"]:
            verdicts["G3_termination"] = "PASS"
        elif report["G4_drag"]["in_band"] and report["G2_cl_feasibility"]["pass_per_major"]:
            verdicts["G3_termination"] = "GATE REACHED"
        else:
            verdicts["G3_termination"] = "NOT A RESULT"
        verdicts["G2_cl_feasibility"] = (
            "PASS" if (report["G2_cl_feasibility"]["pass_per_major"]
                       and report["G2_cl_feasibility"]["pass_final"])
            else "GATE FAIL")
        if cap_stopped:
            verdicts["G4_drag_reduction"] = (
                "GATE REACHED" if report["G4_drag"]["in_band"]
                else "NOT A RESULT")
        else:
            verdicts["G4_drag_reduction"] = (
                "PASS" if report["G4_drag"]["in_band"] else "GATE FAIL")

        # ---- G5/G6/G7 the endpoint FD table and its controls
        fd_path = os.path.join(a.work, "d4_fd_endpoint.json")
        ctrl_dir = os.path.join(a.base, "grader_controls")
        report["G7_count_controls"] = count_controls(fd_path, ctrl_dir)
        verdicts["G7_count_refusal_control"] = (
            "PASS" if report["G7_count_controls"]["pass"] else "GATE FAIL")
        report["G6b_negative_control"] = negative_control(fd_path, ctrl_dir)
        verdicts["G6b_negative_control"] = (
            "PASS" if report["G6b_negative_control"]["pass"] else "GATE FAIL")
        report["G6_planted_zero"] = planted_zero_control(fd_path, ctrl_dir)
        verdicts["G6_planted_zero"] = (
            "PASS" if report["G6_planted_zero"]["pass"] else "GATE FAIL")
        fd = read_json(fd_path, "G5")
        report["G5_fd_table"] = g_fd(fd)
        f = report["G5_fd_table"]
        if f["n_graded"] == 0:
            verdicts["G5_endpoint_fd"] = "NOT A RESULT"
        elif (f["aggregate_rel_err_pct"] is not None
              and f["aggregate_rel_err_pct"] <= FD_BAND_PCT_AGGREGATE
              and f["n_sign_flips"] == 0 and f["n_without_plateau"] == 0
              and all(g["in_band"] for g in f["graded"])):
            verdicts["G5_endpoint_fd"] = "PASS"
        else:
            verdicts["G5_endpoint_fd"] = "GATE FAIL"

    except Refuse as exc:
        out = {"REFUSED": str(exc), "verdicts": verdicts, "report": report}
        with open(a.out, "w") as fh:
            json.dump(out, fh, indent=1, sort_keys=True, default=str)
        sys.stdout.write("D4_GRADER REFUSED %s\n" % str(exc)[:600])
        sys.exit(2)

    bad = [v for v in verdicts.values() if v not in VOCAB]
    if bad:
        sys.stderr.write("D4_GRADER vocabulary violation %r\n" % bad)
        sys.exit(2)
    out = {"verdicts": verdicts, "report": report,
           "n_gates": len(verdicts),
           "registered": {"components": COMPONENTS_REGISTERED,
                          "n_components": N_COMPONENTS_REGISTERED,
                          "cl_target": CL_TARGET,
                          "cl_tol_per_major": CL_TOL_PER_MAJOR,
                          "cl_tol_final": CL_TOL_FINAL,
                          "drag_band_pct": list(DRAG_BAND_PCT),
                          "fd_band_pct": FD_BAND_PCT_PER_COMPONENT,
                          "plateau_tol_pct": PLATEAU_TOL_PCT,
                          "caps": CAPS,
                          "item_ceiling_core_min": ITEM_CEILING_CORE_MIN,
                          "decomposition": {"method": DECOMP_METHOD,
                                            "numberOfSubdomains": RANKS},
                          "cpuset": CPUSET_REGISTERED,
                          "delivered_cores_floor": DELIVERED_CORES_FLOOR}}
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)
    # ADDENDUM 2: NOT_MEASURED infrastructure fields are NAMED in the verdict
    # line, beside the verdicts, never composed into any of them.
    sys.stdout.write("D4_GRADER OK gates=%d %s NOT_MEASURED=%s\n"
                     % (len(verdicts), json.dumps(verdicts, sort_keys=True),
                        json.dumps(report.get("NOT_MEASURED", {}),
                                   sort_keys=True)))


if __name__ == "__main__":
    main()
