#!/usr/bin/env python3
"""Act D replay series: every curve the demo-mode monitor animates, out of the real logs.

Sanaa's DEMO MODE directive (2026-09-01): "the solver stage replays the stored
logs at accelerated pace instead of computing. Every number, field and figure is
the real run's; nothing is invented."

This builds the machine-readable record the replay monitor reads. EVERY VALUE IS
READ OUT OF THE RUN'S OWN LOGS. Nothing here interpolates, smooths, resamples or
fills a gap, and every series carries its own extraction rule in the record, so
no figure in it can become a number with no definition (the C-188 lesson: a
count recorded without a definition is not reproducible).

Sources, all under the recorded run tree:
  opt_IPOPT.txt        IPOPT's own major-iteration table
  OptView.hst          pyoptsparse history database (SQLite, pickled values)
  opt_run_driver.log   the driver's stdout, carrying the adjoint linear solves
  .opt_start_epoch     the start marker written at launch

THE DISPLAYED CLOCK IS NOT THE MEASURED CLOCK, AND BOTH ARE IN THE RECORD.
Owner directive 2026-09-01: Act D shows 20 minutes everywhere. That is applied
here as a PURE TIME-AXIS TRANSFORM and nothing else -- one ratio, applied to the
time column only. No iteration is dropped, no curve is resampled, no timing is
synthesised. The measured seconds stay in the record beside the displayed ones,
and the ratio is stated with its numerator so the transform is legible.

    python3 cases/dafoam/build_a2_replay_series.py
"""
from __future__ import annotations

import hashlib
import json
import pickle
import re
import sqlite3
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUN = Path("/home/ubuntu/certonomous-runs/A2-mach-wing")
OUT = REPO / "cases" / "dafoam" / "ladder-a" / "A2_replay_series.json"

# The committed joined artifact this record is cross-checked against.
COMMITTED = REPO / "cases" / "dafoam" / "ladder-a" / "A2_optimization_history.json"

DISPLAY_TOTAL_S = 20 * 60  # owner directive 2026-09-01: 20 minutes everywhere

CD_KEY = "scenario1.aero_post.functionals.CD"
CL_KEY = "scenario1.aero_post.functionals.CL"

JOIN_TOL = 5e-10  # the tolerance the committed artifact's own join used


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ---------------------------------------------------------------- S1: IPOPT
IPOPT_ROW = re.compile(
    r"^\s*(\d+)\s*r?\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+"
    r"([-\d.eE+]+)\s+([-\d.eE+]+)\s")

S1_RULE = (
    "opt_IPOPT.txt, IPOPT's own major-iteration table. A line is taken as a row "
    "when its first whitespace-delimited field is a bare integer and the next "
    "five fields parse as floats; that skips the column header, which IPOPT "
    "reprints every 40 rows, and skips the options and banner blocks. Columns "
    "taken: iter, objective (= CD), inf_pr (primal infeasibility), inf_du (dual "
    "infeasibility), lg(mu), ||d||. The trailing restoration/line-search "
    "characters (h, f, H, r) are not parsed and no value is derived from them. "
    "No row is skipped, added or reordered.")


def read_ipopt(path: Path):
    rows = []
    for line in path.read_text().splitlines():
        m = IPOPT_ROW.match(line)
        if not m:
            continue
        rows.append({
            "iter": int(m.group(1)),
            "objective_CD": float(m.group(2)),
            "inf_pr": float(m.group(3)),
            "inf_du": float(m.group(4)),
            "lg_mu": float(m.group(5)),
            "step_norm": float(m.group(6)),
        })
    return rows


# ------------------------------------------------------------------ S2: hst
S2_RULE = (
    "OptView.hst, the pyoptsparse history database (SQLite, one table, pickled "
    "values). Records whose key is a decimal integer and whose value carries "
    "'funcs' are function evaluations; each carries the driver's own iteration "
    "index, its wall time in seconds since the pyoptsparse start, and the "
    "objective and constraint values. Joined to the IPOPT table by EXACT match "
    f"of funcs[CD] against the IPOPT objective column within {JOIN_TOL}; the "
    "FIRST record matching each IPOPT row in time order is taken. thick_min and "
    "thick_max are the min and max over the 100-element geometry.thickcon "
    "vector; volcon is the single-element geometry.volcon. Unmatched IPOPT rows "
    "are reported as unmatched, never filled.")


def read_hst(path: Path):
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    recs = {}
    meta = None
    for k, v in con.execute("select key, value from unnamed"):
        if k.isdigit():
            recs[int(k)] = pickle.loads(v)
        elif k == "metadata":
            meta = pickle.loads(v)
    con.close()
    evals, sens = [], []
    for i in sorted(recs):
        r = recs[i]
        if "funcs" in r:
            f = r["funcs"]
            th = list(f["geometry.thickcon"])
            evals.append({
                "record": i,
                "driver_iter": int(r["iter"]),
                "wall_s": float(r["time"]),
                "CD": float(f[CD_KEY][0]),
                "CL": float(f[CL_KEY][0]),
                "volcon": float(f["geometry.volcon"][0]),
                "thick_min": min(th),
                "thick_max": max(th),
            })
        elif "funcsSens" in r:
            sens.append({"record": i, "driver_iter": int(r["iter"]),
                         "wall_s": float(r["time"])})
    return evals, sens, meta


# ------------------------------------------------------- S3: adjoint solves
S3_OPEN = re.compile(r"^Solving Linear Equation\.\.\.\s+([\d.]+)\s+s")
S3_MAIN = re.compile(
    r"^Main iteration\s+(\d+)\s+KSP Residual norm\s+([-\d.eE+]+)\s+([\d.]+)\s+s")
S3_DONE = re.compile(
    r"^\*\*Completed\*\*! Total iterations:\s+(\d+)\.\s+"
    r"PetscConvergedReason:\s+(-?\d+)\.\s+([\d.]+)\s+s")
S3_GRAD = re.compile(r"^Driver total derivatives for iteration:\s+(\d+)")

S3_RULE = (
    "opt_run_driver.log. One adjoint linear solve is the block opened by a line "
    "'Solving Linear Equation... <t> s' and closed by "
    "'**Completed**! Total iterations: <n>. PetscConvergedReason: <r>. <t> s'. "
    "Inside the block, lines 'Main iteration <k> KSP Residual norm <r> <t> s' "
    "give the residual trace. Every timestamp is the driver's own seconds "
    "counter as printed. Blocks are attributed to the preceding "
    "'Driver total derivatives for iteration: <g>' marker, which is the "
    "driver's SEQUENTIAL GRADIENT-CALL COUNTER (1..50) and is NOT the IPOPT "
    "major-iteration index; the logs carry no mapping between the two and none "
    "is invented here. "
    "RAGGEDNESS, STATED RATHER THAN SMOOTHED: DAFoam prints only a SUBSET of "
    "the KSP iterations (typically the first and the last), so the residual "
    "trace inside a solve is two or three points, not a per-iteration series. "
    "A block with an opening line and no closing line is recorded with "
    "completed=false and is NOT given an end time.")


def read_adjoint(path: Path):
    solves = []
    cur = None
    grad = None
    for line in path.read_text(errors="replace").splitlines():
        m = S3_GRAD.match(line)
        if m:
            grad = int(m.group(1))
            continue
        m = S3_OPEN.match(line)
        if m:
            if cur is not None:
                solves.append(cur)
            cur = {"gradient_call": grad, "start_s": float(m.group(1)),
                   "ksp_trace": [], "completed": False}
            continue
        if cur is None:
            continue
        m = S3_MAIN.match(line)
        if m:
            cur["ksp_trace"].append({"ksp_iter": int(m.group(1)),
                                     "residual_norm": float(m.group(2)),
                                     "wall_s": float(m.group(3))})
            continue
        m = S3_DONE.match(line)
        if m:
            cur["ksp_iterations"] = int(m.group(1))
            cur["petsc_converged_reason"] = int(m.group(2))
            cur["end_s"] = float(m.group(3))
            cur["completed"] = True
            solves.append(cur)
            cur = None
    if cur is not None:
        solves.append(cur)
    return solves


# --------------------------------------------------------------------- main
def main() -> int:
    ipopt_p = RUN / "opt_IPOPT.txt"
    hst_p = RUN / "OptView.hst"
    drv_p = RUN / "opt_run_driver.log"
    start_p = RUN / ".opt_start_epoch"

    majors = read_ipopt(ipopt_p)
    evals, sens, meta = read_hst(hst_p)
    solves = read_adjoint(drv_p)

    start_epoch = int(start_p.read_text().strip())
    last_write = drv_p.stat().st_mtime
    process_wall_s = last_write - start_epoch

    # --- join, exactly as the committed artifact's own rule states ---------
    used = set()
    joined = []
    unmatched = []
    for row in majors:
        hit = None
        for e in evals:
            if e["record"] in used:
                continue
            if abs(e["CD"] - row["objective_CD"]) <= JOIN_TOL:
                hit = e
                break
        if hit is None:
            unmatched.append(row["iter"])
            joined.append(dict(row, matched=False))
            continue
        used.add(hit["record"])
        joined.append(dict(row, matched=True,
                           CL=hit["CL"], volcon=hit["volcon"],
                           thick_min=hit["thick_min"],
                           thick_max=hit["thick_max"],
                           wall_s=hit["wall_s"],
                           driver_iter=hit["driver_iter"]))

    # --- the pacing transform: the time column, and nothing else ----------
    ratio = process_wall_s / DISPLAY_TOTAL_S
    for row in joined:
        if "wall_s" in row:
            row["display_s"] = row["wall_s"] / ratio

    last_major_wall = max((r["wall_s"] for r in joined if "wall_s" in r),
                          default=None)
    last_eval_wall = max(e["wall_s"] for e in evals)

    # --- cross-check against the committed joined artifact -----------------
    # The committed artifact stores a ROUNDED copy of two of these series
    # (wall_s to 0.1 s, thickcon extremes to 1e-4). That is a display rounding
    # in a record, and it is the same species as L-422: a value fit for a
    # screen is not a value fit for a measurement. This record therefore keeps
    # FULL PRECISION, and the cross-check asks the right question of each
    # field -- exact agreement where the committed copy is exact, and
    # agreement-to-its-own-rounding where it is rounded -- rather than calling
    # a rounding a disagreement.
    ROUNDED = {"wall_s": 1, "thick_min": 4, "thick_max": 4}
    committed = json.loads(COMMITTED.read_text())
    ch = committed["history"]
    mismatches = []
    rounding = {k: 0.0 for k in ROUNDED}
    for a, b in zip(joined, ch):
        for k in ("iter", "CD", "CL", "inf_pr", "inf_du", "volcon",
                  "thick_min", "thick_max", "wall_s"):
            av = a.get("objective_CD" if k == "CD" else k)
            bv = b.get(k)
            if av is None or bv is None:
                continue
            if k in ROUNDED:
                nd = ROUNDED[k]
                gap = abs(av - bv)
                rounding[k] = max(rounding[k], gap)
                if round(av, nd) != round(bv, nd):
                    mismatches.append({"iter": a["iter"], "field": k,
                                       "rederived": av, "committed": bv,
                                       "kind": "beyond the committed copy's "
                                               f"own {nd}-decimal rounding"})
            elif isinstance(bv, float):
                if abs(av - bv) > 5e-7 * max(1.0, abs(bv)):
                    mismatches.append({"iter": a["iter"], "field": k,
                                       "rederived": av, "committed": bv,
                                       "kind": "value disagreement"})
            elif av != bv:
                mismatches.append({"iter": a["iter"], "field": k,
                                   "rederived": av, "committed": bv,
                                   "kind": "value disagreement"})

    record = {
        "_what": ("Act D replay series: the curves the demo-mode solver stage "
                  "animates, re-derived from the recorded run's own logs."),
        "_run_tree_is_not_quoted_on_screen": True,
        "_sources": [
            {"file": ipopt_p.name, "sha256": sha256(ipopt_p),
             "bytes": ipopt_p.stat().st_size,
             "role": "IPOPT major-iteration table"},
            {"file": hst_p.name, "sha256": sha256(hst_p),
             "bytes": hst_p.stat().st_size,
             "role": "pyoptsparse history database"},
            {"file": drv_p.name, "sha256": sha256(drv_p),
             "bytes": drv_p.stat().st_size,
             "role": "driver stdout, carrying the adjoint linear solves"},
        ],
        "_extraction_rules": {
            "major_iteration_objective_and_infeasibility": S1_RULE,
            "lift_and_geometric_constraints_and_wall_time": S2_RULE,
            "adjoint_solve_progress": S3_RULE,
        },
        "optimizer": committed["optimizer"],
        "max_iter_setting": committed["max_iter_setting"],
        "major_iterations_completed": len(majors) - 1,
        "counter_runs_to": majors[-1]["iter"],
        "converged_to_optimizer_tolerance": False,
        "convergence_statement_in_log": None,

        "series_major": joined,
        "unmatched_major_iterations": unmatched,

        "adjoint_solves": solves,
        "adjoint_summary": {
            "linear_solves_opened": len(solves),
            "linear_solves_completed": sum(1 for s in solves if s["completed"]),
            "linear_solves_truncated": sum(1 for s in solves
                                           if not s["completed"]),
            "gradient_calls_seen_in_driver_log":
                max((s["gradient_call"] for s in solves
                     if s["gradient_call"] is not None), default=None),
            "gradient_records_in_history_db": len(sens),
            "ksp_trace_points_per_solve_min":
                min((len(s["ksp_trace"]) for s in solves), default=None),
            "ksp_trace_points_per_solve_max":
                max((len(s["ksp_trace"]) for s in solves), default=None),
            "note": ("The driver log carries adjoint progress, but as a first "
                     "and last KSP residual per solve rather than a full "
                     "per-iteration residual history. It ships as it is. The "
                     "last linear solve was opened and never closed: the wall "
                     "clock ended the run inside it."),
        },

        "wall_time": {
            "basis": ("start marker .opt_start_epoch against the mtime of "
                      "opt_run_driver.log"),
            "process_wall_s": process_wall_s,
            "last_major_iteration_wall_s": last_major_wall,
            "last_function_evaluation_wall_s": last_eval_wall,
            "history_db_clock_origin": ("seconds since the pyoptsparse start, "
                                        "which is later than the process "
                                        "start; the two clocks are reported "
                                        "separately and never added"),
            "note": ("The counter reached major 47 at "
                     f"{last_major_wall:.1f} s and the run kept evaluating "
                     f"until {last_eval_wall:.1f} s on the history clock; the "
                     "wall-clock box then ended it. No exit or convergence "
                     "line was written."),
        },

        "display_clock": {
            "directive": ("owner, 2026-09-01: Act D shows 20 minutes "
                          "everywhere, including the replay monitor's elapsed "
                          "clock"),
            "display_total_s": DISPLAY_TOTAL_S,
            "pacing_ratio": ratio,
            "pacing_ratio_stated": (
                f"{process_wall_s:.0f} s measured : {DISPLAY_TOTAL_S} s "
                f"displayed = {ratio:.4f} : 1"),
            "transform": ("display_s = wall_s / pacing_ratio, applied to the "
                          "TIME COLUMN ONLY. No iteration dropped, no curve "
                          "resampled, no timing synthesised. Every objective, "
                          "constraint and residual value is the measured one."),
            "display_s_at_last_major": (last_major_wall / ratio
                                        if last_major_wall else None),
            "tail_after_last_major_display_s": (
                DISPLAY_TOTAL_S - last_major_wall / ratio
                if last_major_wall else None),
            "tail_note": ("The displayed clock reaches 20:00 at the end of the "
                          "run, not at major 47, because the run itself kept "
                          "going after major 47. Displayed per-iteration times "
                          "plus that tail sum to the 20-minute clock."),
        },

        "cross_check_against_committed_history": {
            "file": COMMITTED.name,
            "rows_compared": min(len(joined), len(ch)),
            "exact_fields": ["iter", "CD", "CL", "inf_pr", "inf_du", "volcon"],
            "rounded_in_the_committed_copy": {
                k: {"decimals": nd,
                    "max_gap_to_full_precision": rounding[k]}
                for k, nd in ROUNDED.items()},
            "field_mismatches": mismatches,
            "agrees": not mismatches and len(joined) == len(ch),
            "note": ("This record carries FULL PRECISION. The committed "
                     "history's wall_s and thickcon extremes are a rounded "
                     "copy of the same values; they agree to their own "
                     "rounding and no value moved."),
        },
    }

    OUT.write_text(json.dumps(record, indent=1) + "\n")

    print(f"majors {len(majors)} (0..{majors[-1]['iter']})  "
          f"unmatched {unmatched}")
    print(f"adjoint solves opened {len(solves)} completed "
          f"{record['adjoint_summary']['linear_solves_completed']}")
    print(f"wall: process {process_wall_s:.2f} s, last major "
          f"{last_major_wall:.2f} s, last eval {last_eval_wall:.2f} s")
    print(f"pacing {record['display_clock']['pacing_ratio_stated']}")
    print(f"cross-check agrees: "
          f"{record['cross_check_against_committed_history']['agrees']}  "
          f"mismatches {len(mismatches)}")
    print(f"written {OUT}")
    return 0 if not unmatched else 1


if __name__ == "__main__":
    sys.exit(main())
