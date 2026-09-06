#!/usr/bin/env python3
"""F5a rung driver split into STAGE / SOLVE(launch_solve.sh) / HARVEST so the
long pimpleFoam solve goes through the sanctioned launcher (D12/launch_solve.sh)
instead of a plain foreground subprocess.call that dies with the calling
agent's turn.

  stage     builds the case, blockMesh+checkMesh (fast, foreground)
  launch    prints the exact launch_solve.sh command to run the solve
  harvest   after the solve is done, copies postProcessing back and computes
            the same record.json cylinder_ladder.run_case() would have
            produced (identical stats/probe extraction code, reused, not
            reimplemented)

This performs no physics differently from cylinder_ladder.run_case(); it only
relocates the solve step behind launch_solve.sh so the collector survives a
dropped connection.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parent))
# NOT `parents[4]`, and this is a defect class rather than a typo: a
# repository root derived by COUNTING segments up from a path under a
# MOVING tree points somewhere else the moment the tree moves.  MOVE_MAP
# batch 7 made this file ONE SEGMENT SHALLOWER, so `parents[4]` went from
# the repository root to `/home/ubuntu`.  There is no path literal in the
# expression, so no prefix rewrite and no grep for `demo-output` reaches it
# -- the same class cost `sdk/tests/test_a2_shape.py:28` a green comparison
# over ten synthetic bodies at batch 6.  DERIVED BY SEARCHING for the
# marker, so the answer no longer depends on this file's depth.
_REPO_ROOT = next((_p for _p in Path(__file__).resolve().parents
                  if (_p / "scripts" / "lab_paths.py").is_file()), None)
if _REPO_ROOT is None:
    raise RuntimeError(
        "cannot locate scripts/lab_paths.py above %s; refusing to "
        "guess a repository root" % __file__)
sys.path.insert(0, str(_REPO_ROOT / "sdk"))

# THE SOLVE-EVIDENCE GUARD.  Loaded by explicit path rather than by putting
# `scripts/` on sys.path: this module must not be shadowable by anything, and
# a guard that can be silently replaced is not a guard.  If it is missing, this
# file refuses to run at all -- staging without the guard is the defect.
import importlib.util as _ilu  # noqa: E402

_GUARD_PATH = _REPO_ROOT / "scripts" / "solve_evidence_guard.py"
if not _GUARD_PATH.is_file():
    raise RuntimeError(
        f"solve-evidence guard not found at {_GUARD_PATH}; refusing to stage. "
        "stage() deletes its remote directory, and without the guard that "
        "delete is unconditional -- see the guard's docstring for the rung it "
        "would have destroyed.")
if "solve_evidence_guard" in sys.modules:
    # Registered once, reused everywhere.  Loading the same file twice under
    # two module objects would give SolveEvidencePresent two distinct classes,
    # and a caller's `except solve_evidence_guard.SolveEvidencePresent` would
    # then silently miss the refusal raised by the other copy.  Measured: the
    # integration control hit exactly that before this line existed.
    solve_evidence_guard = sys.modules["solve_evidence_guard"]
else:
    _spec = _ilu.spec_from_file_location("solve_evidence_guard", _GUARD_PATH)
    solve_evidence_guard = _ilu.module_from_spec(_spec)
    sys.modules["solve_evidence_guard"] = solve_evidence_guard
    _spec.loader.exec_module(solve_evidence_guard)
safe_rmtree_for_restage = solve_evidence_guard.safe_rmtree_for_restage
safe_replace_mirror = solve_evidence_guard.safe_replace_mirror

import cylinder_ladder as CL  # noqa: E402
from workflows.tmr_verification import (  # noqa: E402
    _foam, _copy_best_effort, time_weighted_stats, measure_period, halves_drift,
)
from chief_engineer.head_engineer import parse_coefficient_history  # noqa: E402

_RUN_ROOT = Path.home() / "certonomous-runs" / "f5a-cylinder-ladder"


def stage(name: str, out_dir: Path, **build_kwargs) -> dict:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    case = out_dir / "case"
    remote_dir = _RUN_ROOT / name
    # WAS: shutil.rmtree(remote_dir, ignore_errors=True) -- unconditional, and
    # silent about its own failures.  It is the first statement of stage(), so
    # "re-stage the rung" was the same keystroke as "destroy the rung".  The
    # guard refuses when the directory holds time directories > 0 with fields
    # (reconstructed or under processor*/) or a postProcessing series with data
    # rows, and names what would have been lost.  There is NO override flag,
    # deliberately: the recovery path it prints is a human `mv` aside, which
    # preserves the physics.  Past the guard the delete no longer swallows its
    # errors.
    safe_rmtree_for_restage(remote_dir)
    remote_dir.parent.mkdir(parents=True, exist_ok=True)

    params = CL.build_case(case, **build_kwargs)
    shutil.copytree(case, remote_dir)

    timings = {}
    for step, args, timeout in (("blockMesh", ["blockMesh"], 900),
                                ("checkMesh", ["checkMesh", "-allTopology", "-allGeometry"], 900)):
        import time
        start = time.monotonic()
        result = _foam(args, remote_dir, f"log.{step}", timeout=timeout)
        timings[step] = round(time.monotonic() - start, 1)
        _copy_best_effort(remote_dir / f"log.{step}", out_dir / f"log.{step}")
        print(f"[{name}] {step} done in {timings[step]:.1f}s (exit {result.returncode})")
        if step == "blockMesh" and result.returncode != 0:
            raise RuntimeError(f"{name}: blockMesh failed")

    (out_dir / "stage_params.json").write_text(json.dumps(
        {"params": params, "timings": timings, "remote_dir": str(remote_dir)}, indent=2))
    print(f"[{name}] staged at {remote_dir}, cells={params['cells']}")
    return {"params": params, "remote_dir": remote_dir, "timings": timings}


def harvest(name: str, out_dir: Path, ranks: int = 1, *,
            without_log: bool = False) -> dict:
    out_dir = Path(out_dir)
    staged = json.loads((out_dir / "stage_params.json").read_text())
    params = staged["params"]
    remote_dir = Path(staged["remote_dir"])
    timings = dict(staged["timings"])

    log_path = remote_dir / "log.pimpleFoam"
    tail: list[str] | None = None      # None means "no solver log was read"

    # GAP 1 -- THE LOG-LESS HARVEST IS AN EXPLICITLY REQUESTED ENTRY, NEVER A FALLBACK.
    # The raise below is LOAD-BEARING: the obvious repair for a missing log -- "just
    # re-stage and re-run" -- WAS THE CALL THAT DELETED THE PHYSICS, and softening it into a
    # fallback would reinstate exactly that. So the flag is keyword-only, the CLI exposes it
    # as its own MODE rather than an option on the normal one, and the raise is unchanged.
    #
    # ⚠ AND IT REFUSES WHEN THE LOG IS PRESENT.  Without that guard a caller who passed the
    # flag habitually would get a partial-verification record for a run that could have been
    # fully verified -- THE EXCEPTION WOULD QUIETLY BECOME THE DEFAULT, which is how every
    # deliberate exception dies.
    if without_log and log_path.exists():
        raise RuntimeError(
            f"{name}: the log-less harvest was requested but {log_path} EXISTS. REFUSED. "
            "This mode produces a record PERMANENTLY missing three clauses of the strict "
            "completion rule; it is for physics whose log is gone, NEVER a shortcut past a "
            "log that is present. Harvest normally.")
    if not log_path.exists() and without_log:
        # ⚠ NO SEPARATE HARVEST FUNCTION.  A second copy of the measurement body is the
        # very defect this file spent the night removing (rule 14): two copies are two
        # answers the moment one is edited.  The log-less path is THIS path with the
        # log-derived quantities marked absent, so every number is produced by the same
        # code that produces it normally.
        print(f"[{name}] LOG-LESS HARVEST: {log_path} is absent and this was requested "
              "explicitly. Three clauses of the strict completion rule are PERMANENTLY "
              "unverifiable for this rung and the record will say so.")
    elif not log_path.exists():
        # READ THIS BEFORE YOU REACH FOR stage() AGAIN.
        #
        # A missing log.pimpleFoam does NOT mean the solve did not run.  It can
        # also mean the solve ran, produced its physics, and lost its log.
        # `re2000` IS THAT CASE and it is STRANDED:
        #   ~/certonomous-runs/f5a-cylinder-ladder/re2000/ holds 90/ with
        #   U p phi uniform yPlus, and postProcessing/forceCoeffs1/0/
        #   coefficient.dat with 10,191 data rows ending at t = 90 -- exactly
        #   its endTime -- bought at a measured 66.09 core-min.  Only
        #   log.blockMesh and log.checkMesh survive.
        # So this raise refuses it FOREVER, and the obvious repair -- "just
        # re-stage and re-run it" -- used to be the very call that DELETED it.
        # stage() now refuses instead (see safe_rmtree_for_restage above).
        #
        # Under Sanaa's rule of 2026-08-26, BOOKKEEPING NEVER VOIDS PHYSICS:
        # re2000's numbers stand and its banded gate in
        # verification/campaign/F5a_cylinder_reynolds_ladder.md stands.  What is
        # missing is bookkeeping, and THE REPAIR FOR MISSING BOOKKEEPING IS
        # NEVER DELETION OF THE PHYSICS.  If a rung must be re-run, a human
        # moves the old directory aside first; nothing here deletes it.
        raise RuntimeError(
            f"{name}: no log.pimpleFoam in {remote_dir} -- the solve did not "
            f"run, OR it ran and lost its log (this is re2000's condition; see "
            f"the comment above this raise). Do NOT re-stage to 'fix' it "
            f"without first checking for fields and a coefficient series: "
            f"python3 {_REPO_ROOT}/scripts/solve_evidence_guard.py --check "
            f"{remote_dir}. If that guard confirms the PHYSICS is present and only the LOG "
            f"is gone, harvest it with the explicit `harvest-without-log` mode, which "
            f"records what it could and could NOT verify instead of inventing it.")
    if log_path.exists():
        _copy_best_effort(log_path, out_dir / "log.pimpleFoam")
        tail = log_path.read_text(errors="replace").splitlines()
        if not any("End" in l or "ExecutionTime" in l for l in tail[-40:]):
            print(f"[{name}] WARNING: log.pimpleFoam does not look terminated cleanly "
                  f"(last lines): " + "\n".join(tail[-5:]))

    # WAS: shutil.rmtree(out_dir/"postProcessing", ignore_errors=True) -- the
    # same defect class one function down.  The local mirror was destroyed
    # unconditionally and then refreshed BEST-EFFORT: if the remote copy is
    # gone, the last copy of the series goes with it and the failure only
    # surfaces later as "no forceCoeffs output".  Now the mirror is removed
    # only when the source can actually replace its rows.
    safe_replace_mirror(out_dir / "postProcessing", remote_dir / "postProcessing")
    _copy_best_effort(remote_dir / "postProcessing", out_dir / "postProcessing")
    # GAP 5, SECOND CALL SITE.  THIS IS THE ONE THAT MATTERS: cylinder_ladder.run_case()
    # is the foreground path that dies with the calling agent's turn, and THIS harvester
    # is the sanctioned one -- so fixing run_case() alone left the code that actually
    # runs still picking its series by ASCII accident.  Rule 14: A LESSON IS NOT APPLIED
    # UNTIL EVERY CALL SITE ASSERTS IT.
    # DELEGATED, NOT REIMPLEMENTED.  Two copies of a selection rule are two rules the
    # moment one is edited; there is exactly ONE selector and both harvesters call it.
    coeff_path = CL._coefficient_series_path(out_dir)
    history = parse_coefficient_history(coeff_path.read_text(errors="replace"))
    times = history["Time"]
    end_time = params["end_time"]
    t_start = 0.5 * end_time
    cd_stats = time_weighted_stats(times, history["Cd"], t_start)
    cl_stats = time_weighted_stats(times, history["Cl"], t_start)
    period = measure_period(times, history["Cl"], t_start)
    if cd_stats is None or cl_stats is None:
        raise RuntimeError(f"{name}: averaging window empty (ran to "
                           f"t={times[-1] if times else 0:g}, requested {t_start:g}); "
                           f"run is INCOMPLETE, not a result")
    drift = halves_drift(times, history["Cd"], cd_stats["window_start"], cd_stats["window_end"])
    if drift is None:
        raise RuntimeError(f"{name}: halves_drift undecidable -- stationarity UNKNOWN")

    # GAP 5(c), SECOND CALL SITE.  Same delegation, and the selector orders time
    # directories NUMERICALLY rather than refusing -- see the comment on
    # CL._yplus_series_path for why yPlus gets a different repair from coefficient*.dat.
    # Absence stays TOLERATED: None keeps the "" branch this line always had.
    yplus_path = CL._yplus_series_path(out_dir)
    yplus_text = yplus_path.read_text(errors="replace") if yplus_path else ""
    cpb = CL.base_cpb(out_dir, t_start)
    lr = CL.recirculation_length(out_dir, t_start, params["centerline_points"])

    from workflows.cylinder_vortex_shedding import DIAMETER, U_INF
    strouhal = (DIAMETER / (period * U_INF)) if period else None

    # wall time: parse ExecutionTime of the LAST line in the log for the
    # true solver wall time regardless of how many restarts contributed.
    import re
    if tail is None:
        # ⚠ None, NOT 0.0, AND THE DISTINCTION IS THE WHOLE POINT.  None says "NOT KNOWN";
        # zero says "KNOWN TO BE NOTHING".  They are adjacent and opposite, and emitting the
        # wrong one silently converts an ABSENCE into a DATUM.  That is rule 3's
        # planted-zero principle stated for a WRITER rather than a reader: a writer that
        # emits zero where it means unknown MANUFACTURES the very false zero the
        # reader-side rule exists to catch.
        solve_wall = None
    else:
        exec_times = re.findall(r"ExecutionTime = ([\d.]+) s", "\n".join(tail))
        solve_wall = float(exec_times[-1]) if exec_times else None
    timings["pimpleFoam"] = solve_wall

    record = {
        "name": name, "reynolds": params["reynolds"], "nu": params["nu"],
        "turbulence": params["turbulence"], "cells": params["cells"],
        "n_radial": params["n_radial"], "n_tangential": params["n_tangential"],
        "first_cell": params["first_cell"], "farfield_diameters": params["farfield_diameters"],
        "ranks": ranks, "end_time": end_time, "dt0": params["dt0"],
        "max_co": params["max_co"], "steps": len(times),
        "cd_mean": cd_stats["mean"], "cd_band": cd_stats["band"],
        "cd_relative_drift": drift["relative_drift"],
        "cd_first_half_mean": drift["first_half_mean"],
        "cd_second_half_mean": drift["second_half_mean"],
        "cl_mean": cl_stats["mean"], "cl_band": cl_stats["band"],
        "averaging_window": [cd_stats["window_start"], cd_stats["window_end"]],
        "period": period, "strouhal": strouhal,
        "cpb": cpb, "recirculation": lr,
        "yplus_raw": yplus_text.strip().splitlines()[-3:] if yplus_text else [],
        # ⚠ wall_seconds is None -- NOT a partial sum -- when the solve time is unknown.
        # Summing the stage timings and calling the result "wall_seconds" would present a
        # number that LOOKS like the run's wall time and is not: the same absence-into-datum
        # conversion as a zero, one level up.
        "wall_seconds": (None if solve_wall is None
                         else sum(v for v in timings.values() if v is not None)),
        "timings": timings,
        "stationary": drift["relative_drift"] <= 0.10,
        "final_time_reached": times[-1] if times else None,
    }
    if tail is None:
        # THE PARTIALITY IS MACHINE-READABLE AND SITS AT THE TOP LEVEL, so a consumer cannot
        # reach the numbers without passing it.
        record["strict_completion"] = _log_independent_completion(
            remote_dir, end_time, times[-1] if times else None)
        record["harvest_mode"] = "WITHOUT-LOG"
    (out_dir / "record.json").write_text(json.dumps(record, indent=2, default=str))
    lr_txt = f"Lr/D {lr['lr_over_d']:.3f}" if lr and lr["lr_over_d"] else "Lr/D not found"
    cpb_txt = f"-Cpb {cpb['cpb_magnitude']:.3f}" if cpb else "Cpb n/a"
    st_txt = f"St {strouhal:.4f}" if strouhal else "no period detected"
    wall_txt = ("wall UNKNOWN (log absent)" if record["wall_seconds"] is None
                else f"wall {record['wall_seconds']:.0f}s")
    print(f"[{name}] Cd {cd_stats['mean']:.4f} (drift {100*drift['relative_drift']:.1f}%), "
          f"{st_txt}, {cpb_txt}, {lr_txt}, {wall_txt}, "
          f"final_t={record['final_time_reached']}")
    return record


# =====================================================================================
# GAP 1 -- WHAT A LOST LOG DOES AND DOES NOT COST, ENUMERATED AGAINST RULE 4'S SIX CLAUSES.
#
# THE LOG SUPPLIES EXACTLY TWO THINGS TO harvest(): the clean-termination check and the
# wall time.  Cd, Cl, St, -Cpb, Lr and yPlus all come from postProcessing and the time
# directories and NEVER TOUCH IT -- traced, not assumed.
#
# SO SANAA'S RULE OF 2026-08-26 LANDS EXACTLY ON RULE 4'S SEAM, on a case nobody designed
# it for: THE PHYSICS-SIDE CLAUSES SURVIVE THE LOST LOG AND THE INFRASTRUCTURE-SIDE CLAUSES
# DO NOT.  BOOKKEEPING NEVER VOIDS PHYSICS -- ⚠ AND THE MISSING BOOKKEEPING IS STILL
# RECORDED AS MISSING.  A harvest that recovered the physics and went quiet about what it
# could not establish would obey the first half and break the second.
#
# ⚠ THE UNVERIFIABLE CLAUSES ARE `PERMANENTLY UNVERIFIABLE`, NOT `PENDING`.  PENDING is a
# queue state meaning "not yet run" (VERIFICATION §9); this log is GONE, NOT LATE, and
# nothing will ever make these three checkable for this rung.  Calling them PENDING would
# promise a resolution that cannot arrive.
#
# ⚠ AND THIS FUNCTION EMITS NO VERDICT.  Whether three-of-six with three permanently
# unverifiable supports any gate is the GRADER'S question under its own registration.
# A HARVEST THAT ANSWERED IT WOULD BE A COMPARATOR WEARING A HARVESTER'S NAME.
# =====================================================================================
LOG_DEPENDENT_CLAUSES = {
    "solver_return_code": "rc == 0 -- known only to the process that ran the solver",
    "end_line_present": "an `End` line -- written by the solver into the log",
    "execution_time_count_equals_end_time":
        "the count of `ExecutionTime` lines -- read from the log",
}


def _log_independent_completion(remote_dir: Path, end_time: float,
                                series_last_time: float | None) -> dict:
    """Evaluate the clauses of the strict completion rule that DO NOT need the log.

    Returns a MACHINE-READABLE structure, deliberately not prose: a grader must be able to
    consume the partiality programmatically rather than by reading a sentence and choosing
    to believe it.
    """
    remote_dir = Path(remote_dir)
    times = []
    for d in remote_dir.iterdir():
        if not d.is_dir():
            continue
        try:
            times.append((float(d.name), d))
        except ValueError:
            continue
    latest_t, latest_dir = max(times, default=(None, None))

    fields_required = ("U", "p", "phi")
    present = ([f for f in fields_required if (latest_dir / f).is_file()]
               if latest_dir else [])

    # THE AGE GUARD, and the honest note about its reference.  CLAUDE.md rule 4 dates a run
    # against the case's own `0/T`, because `T` is touched last at launch.  THIS FAMILY HAS
    # NO `T`; the reference used is the `0/` DIRECTORY's own mtime, and that substitution is
    # stated rather than glossed -- a guard whose reference has silently changed is not the
    # guard the rule specifies.
    zero_dir = remote_dir / "0"
    zero_mtime = zero_dir.stat().st_mtime if zero_dir.is_dir() else None
    newer = None
    if zero_mtime is not None and latest_dir is not None:
        ages = [(latest_dir / f).stat().st_mtime for f in present]
        newer = bool(ages) and all(a > zero_mtime for a in ages)

    verified = {
        "last_time_equals_end_time": {
            "clause": "last time == endTime",
            "measured": latest_t, "required": end_time,
            "holds": latest_t is not None and abs(latest_t - end_time) < 1e-9,
        },
        "fields_present_at_end_time": {
            "clause": "fields present at endTime",
            "measured": present, "required": list(fields_required),
            "holds": set(present) == set(fields_required),
        },
        "fields_newer_than_time_zero": {
            "clause": "every field at endTime NEWER than the case's own time-zero",
            "anchor": "the `0/` directory's own mtime",
            "anchor_is_a_substitution_for": "0/T",
            "why_this_anchor_is_faithful":
                "Rule 4 anchors the age guard on the case's own `0/T` BECAUSE `T` IS "
                "TOUCHED LAST AT LAUNCH -- the anchor's authority comes from its POSITION "
                "IN THE LAUNCH SEQUENCE, not from its name. This family has no `T`. The "
                "`0/` directory is created when the case is written and is not touched "
                "afterwards, so it dates THE SAME EVENT that `0/T` dates in the thermal "
                "family, and the rule's REASON is preserved rather than merely its form. "
                "What would NOT be faithful is anchoring on a file written at some other "
                "moment -- that is how this guard goes vacuous while still appearing to "
                "run. A GUARD WHOSE REFERENCE HAS SILENTLY CHANGED IS NOT THE GUARD THE "
                "RULE SPECIFIES, so the substitution is declared in the record itself "
                "rather than left to a reader to notice.",
            "measured": newer, "required": True, "holds": newer is True,
        },
    }
    supplementary = {
        "series_reaches_end_time": {
            "note": "NOT a clause of rule 4 -- supplementary evidence that the physics ran "
                    "to the registered end, independent of any log",
            "measured": series_last_time, "required": end_time,
            "holds": series_last_time is not None
                     and abs(series_last_time - end_time) < 1e-9,
        },
    }
    return {
        "harvest_mode": "WITHOUT-LOG",
        "verdict_available": False,
        "why_no_verdict":
            "The strict completion rule requires ALL of its clauses. Three are PERMANENTLY "
            "unverifiable here because the solver log is GONE, NOT LATE. This record is "
            "EVIDENCE, NOT A VERDICT: whether it supports any gate is the grader's question "
            "under its own registration.",
        "clauses_verified": verified,
        "clauses_permanently_unverifiable": {
            k: {"clause": v, "state": "PERMANENTLY UNVERIFIABLE",
                "not_pending_because": "the log is gone, not late -- nothing will make this "
                                       "checkable for this rung"}
            for k, v in LOG_DEPENDENT_CLAUSES.items()
        },
        "supplementary_evidence": supplementary,
        "wall_time_note":
            "The wall time is the ONE quantity that genuinely depended on the lost log "
            "(harvest() parses the last `ExecutionTime` line). It is recorded as null, NOT "
            "zero. The campaign's figure of record for re2000 is 66.09 core-min, from the "
            "run's own accounting -- NOT re-derived here, and no re-derivation is possible "
            "(F5a_cylinder_reynolds_ladder.md:1417-1422).",
    }


def selftest_harvest_delegation() -> int:
    """THE COUPLING CONTROL for gap 5's second call site.

    Rule 14 does not say "fix every call site"; it says EVERY CALL SITE ASSERTS IT.  So
    this proves three separate things, and the third is the one a text check cannot give:

      (1) THE LOCAL COPY IS GONE -- harvest()'s own source no longer contains the
          `rglob("coefficient*.dat")` selection.  PLANTED: the same detector is pointed at
          CL._coefficient_series_path, where the token MUST still appear.  A detector not
          shown able to see the token is not evidence that the token is absent (rule 3).
      (2) THE CALL IS ROUTED -- harvest()'s source contains the delegation by name, so a
          future edit that stops routing through the selector breaks this control rather
          than leaving it vacuously green.
      (3) THE TARGET ACTUALLY REFUSES -- the delegate is exercised on the vendored
          two-file collision and on a clean single-file twin.  (1) and (2) are text; only
          (3) is behaviour, and TEXT THAT NAMES A FUNCTION IS NOT PROOF THE FUNCTION
          REFUSES.
    """
    import inspect
    import tempfile
    ok, fired = True, []

    token = 'rglob("coefficient*.dat")'
    h_src = inspect.getsource(harvest)
    sel_src = inspect.getsource(CL._coefficient_series_path)

    # ---- (1) LOCAL COPY GONE, with the detector PLANTED against the selector.
    seen_where_it_must_be = token in sel_src
    gone_from_harvest = token not in h_src
    if seen_where_it_must_be and gone_from_harvest:
        fired.append("LOCAL COPY: the rglob selection is GONE from harvest(), and the same "
                     "detector DOES find it in CL._coefficient_series_path -- so the "
                     "absence was read by a detector shown able to see a presence")
    else:
        ok = False
        fired.append(f"LOCAL COPY: token in selector={seen_where_it_must_be} (must be True: "
                     f"the plant), token absent from harvest={gone_from_harvest}")

    # ---- (2) THE CALL IS ROUTED, BY NAME.
    if "CL._coefficient_series_path(" in h_src:
        fired.append("ROUTING: harvest() calls CL._coefficient_series_path by name -- an "
                     "edit that stops routing through it breaks this line, not nothing")
    else:
        ok = False
        fired.append("ROUTING: harvest() does NOT name CL._coefficient_series_path -- the "
                     "selector has been bypassed")

    # ---- (3) THE DELEGATE ACTUALLY REFUSES, on the vendored real shape.
    names = ("coefficient.dat", "coefficient_0.dat")
    fx = CL.COEFF_FIXTURE
    if not all((fx / n).is_file() for n in names):
        ok = False
        fired.append(f"DELEGATE: the vendored fixture is missing under {fx} -- this control "
                     "REFUSES rather than substituting a synthetic file")
    else:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            one = base / "single" / "postProcessing" / "forceCoeffs1" / "0"
            two = base / "collision" / "postProcessing" / "forceCoeffs1" / "0"
            one.mkdir(parents=True)
            two.mkdir(parents=True)
            (one / names[0]).write_bytes((fx / names[0]).read_bytes())
            for n in names:
                (two / n).write_bytes((fx / n).read_bytes())

            got = CL._coefficient_series_path(base / "single")
            if got.name == names[0]:
                fired.append(f"DELEGATE CLEAN TWIN: one series ACCEPTED, returning {got.name}")
            else:
                ok = False
                fired.append(f"DELEGATE CLEAN TWIN: returned {got.name!r}, expected "
                             f"{names[0]!r}")
            try:
                picked = CL._coefficient_series_path(base / "collision")
                ok = False
                fired.append("DELEGATE PLANT: the two-file collision was NOT refused -- it "
                             f"silently returned {picked.name!r}")
            except RuntimeError as exc:
                both = all(n in str(exc) for n in names)
                fired.append(f"DELEGATE PLANT: REFUSED, and the message names BOTH "
                             f"candidates = {both}")
                if not both:
                    ok = False

    # ---- (4) THE yPlus SITE, AS A SEPARATE LIMB so the two repairs stay independently
    # verifiable and a regression in one cannot hide behind the other's green.
    # ⚠ THIS LIMB WAS REWRITTEN AFTER IT CORRECTLY WENT RED.  It used to plant against
    # `_yplus_series_path`'s OWN glob.  Gap 5(d) made that function DELEGATE, so its body no
    # longer contains a glob and the plant failed -- THE CONTROL CAUGHT A REFACTOR OF ITS
    # OWN DELEGATE, which is what a coupling control is for.  The repair is not to weaken
    # the plant but to follow the chain: assert the DELEGATION and then plant against the
    # function that now OWNS the glob.  That verifies one link more than the old version.
    y_token = 'rglob("yPlus.dat")'
    y_gone = y_token not in h_src
    y_delegates = "_latest_time_series_path(" in inspect.getsource(CL._yplus_series_path)
    y_detector_works = "rglob(" in inspect.getsource(CL._latest_time_series_path)
    if y_gone and y_delegates and y_detector_works:
        fired.append("YPLUS LOCAL COPY: the exact-name rglob is GONE from harvest(); "
                     "_yplus_series_path DELEGATES to _latest_time_series_path; and the "
                     "detector DOES find a glob in that delegate -- the absence was read by "
                     "a detector shown able to see a presence, one link further down")
    else:
        ok = False
        fired.append(f"YPLUS LOCAL COPY: absent from harvest={y_gone}, yPlus selector "
                     f"delegates={y_delegates}, detector sees the delegate's glob="
                     f"{y_detector_works} (all three must be True)")

    if "CL._yplus_series_path(" in h_src:
        fired.append("YPLUS ROUTING: harvest() calls CL._yplus_series_path by name")
    else:
        ok = False
        fired.append("YPLUS ROUTING: harvest() does NOT name CL._yplus_series_path")

    # THE BEHAVIOURAL LIMB: the delegate must order NUMERICALLY, which is the whole repair.
    with tempfile.TemporaryDirectory() as td:
        m = Path(td)
        for t in ("0", "5", "10"):
            d = m / "postProcessing" / "yPlus1" / t
            d.mkdir(parents=True)
            (d / "yPlus.dat").write_text(f"# t={t}\n0.1 0.2 0.3\n")
        old_pick = sorted((m / "postProcessing").rglob("yPlus.dat"))[-1].parent.name
        new_pick = CL._yplus_series_path(m).parent.name
        if old_pick == "5" and new_pick == "10":
            fired.append("YPLUS DELEGATE: with time dirs 0/5/10 the OLD lexicographic pick "
                         "is t=5 and the delegate returns t=10 -- the defect reproduces and "
                         "the repair changes the answer, so this cannot pass vacuously")
        else:
            ok = False
            fired.append(f"YPLUS DELEGATE: old picked t={old_pick}, delegate picked "
                         f"t={new_pick}; expected 5 then 10")

    for line in fired:
        print(f"  DELEGATION {line}")
    print("  DISCRIMINATES: the detector finds each token where it must be AND misses it "
          "where it must not; the coefficient delegate accepts one series AND refuses two; "
          f"the yPlus delegate orders numerically where the old code ordered by text = {ok}")
    print("HARVEST-DELEGATION SELFTEST " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def selftest_without_log_harvest() -> int:
    """GAP 1 -- THE LOG-LESS HARVEST'S PLANTED CONTROLS.

    The two limbs that matter are the GUARDS, not the arithmetic: this mode must not be
    reachable when a log exists, and the ordinary refusal must still refuse. A repair that
    quietly converts a deliberate refusal into a fallback is worse than the gap it closes.
    """
    import json as _json
    import os
    import tempfile
    ok, fired = True, []

    VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")

    def _tree(root: Path, end="90", fields=("U", "p", "phi"), age_ok=True) -> Path:
        (root / "0").mkdir(parents=True, exist_ok=True)
        for f in ("U", "p"):
            (root / "0" / f).write_text("zero\n")
        d = root / end
        d.mkdir(parents=True, exist_ok=True)
        for f in fields:
            (d / f).write_text("field\n")
        past = 10_000
        now = int(__import__("time").time())
        if age_ok:
            os.utime(root / "0", (now - past, now - past))
        else:
            os.utime(root / "0", (now + past, now + past))   # zero NEWER than the fields
        return root

    with tempfile.TemporaryDirectory() as td:
        base = Path(td)

        # ---- (1) THE CLEAN CASE: all three log-independent clauses hold.
        good = _log_independent_completion(_tree(base / "good"), 90.0, 90.0)
        holds = {k: v["holds"] for k, v in good["clauses_verified"].items()}
        if all(holds.values()):
            fired.append(f"CLEAN: all three log-independent clauses hold {holds}")
        else:
            ok = False
            fired.append(f"CLEAN: expected all True, got {holds}")

        # ---- (2) THE PLANTS: each clause must go FALSE when its own precondition breaks,
        # and the OTHERS must stay TRUE -- otherwise one broken clause could mask another.
        short = _log_independent_completion(_tree(base / "short", end="45"), 90.0, 90.0)
        missing = _log_independent_completion(
            _tree(base / "missing", fields=("U", "p")), 90.0, 90.0)
        stale = _log_independent_completion(_tree(base / "stale", age_ok=False), 90.0, 90.0)
        checks = [
            ("last_time_equals_end_time", short),
            ("fields_present_at_end_time", missing),
            ("fields_newer_than_time_zero", stale),
        ]
        for key, res in checks:
            h = {k: v["holds"] for k, v in res["clauses_verified"].items()}
            if h[key] is False and all(v for k, v in h.items() if k != key):
                fired.append(f"PLANT {key}: went FALSE while the other two stayed TRUE -- "
                             "the clauses are independently sensitive")
            else:
                ok = False
                fired.append(f"PLANT {key}: expected only {key} False, got {h}")

        # ---- (3) SUPPLEMENTARY EVIDENCE IS SENSITIVE TOO.
        supp = _log_independent_completion(_tree(base / "supp"), 90.0, 71.5)
        if supp["supplementary_evidence"]["series_reaches_end_time"]["holds"] is False:
            fired.append("PLANT series: a series stopping at 71.5 against endTime 90 does "
                         "NOT hold")
        else:
            ok = False
            fired.append("PLANT series: a short series was reported as reaching endTime")

        # ---- (4) NO VERDICT WORD ANYWHERE IN THE STRUCTURE.
        blob = _json.dumps(good)
        leaked = [v for v in VERDICTS if v in blob]
        if not leaked:
            fired.append("NO VERDICT: the structure contains none of the six verdict words "
                         "-- it is evidence, and the grader keeps its own question")
        else:
            ok = False
            fired.append(f"NO VERDICT: the structure leaks {leaked} -- a harvester emitting "
                         "a verdict is a comparator wearing a harvester's name")
        if good["verdict_available"] is not False:
            ok = False
            fired.append("NO VERDICT: verdict_available is not False")

        # ---- (5) PERMANENT, NOT PENDING -- and all three log-dependent clauses named.
        unver = good["clauses_permanently_unverifiable"]
        if (set(unver) == set(LOG_DEPENDENT_CLAUSES)
                and all(v["state"] == "PERMANENTLY UNVERIFIABLE" for v in unver.values())):
            fired.append(f"PERMANENCE: all {len(unver)} log-dependent clauses are marked "
                         "PERMANENTLY UNVERIFIABLE, not PENDING -- the log is gone, not late")
        else:
            ok = False
            fired.append(f"PERMANENCE: {sorted(unver)} against "
                         f"{sorted(LOG_DEPENDENT_CLAUSES)}")

        # ---- (6) THE GUARD: this mode REFUSES when a log exists.
        # ---- (7) THE TWIN: the ordinary refusal still refuses when it does not.
        for label, make_log, kwargs, want in (
                ("GUARD", True, {"without_log": True}, "REFUSED"),
                ("TWIN", False, {}, "solve_evidence_guard.py")):
            case = base / f"case_{label}"
            remote = base / f"remote_{label}"
            (remote / "0").mkdir(parents=True)
            case.mkdir(parents=True)
            if make_log:
                (remote / "log.pimpleFoam").write_text("End\n")
            (case / "stage_params.json").write_text(_json.dumps({
                "params": {"end_time": 90.0}, "remote_dir": str(remote), "timings": {}}))
            try:
                harvest("probe", case, **kwargs)
                ok = False
                fired.append(f"{label}: harvest did NOT raise")
            except RuntimeError as exc:
                if want in str(exc):
                    fired.append(f"{label}: refused, and the message carries {want!r}")
                else:
                    ok = False
                    fired.append(f"{label}: refused but the message lacks {want!r}: "
                                 f"{str(exc)[:120]}")

    for line in fired:
        print(f"  WITHOUT-LOG {line}")
    print("  DISCRIMINATES: a complete tree passes all clauses AND each clause goes false "
          "alone when broken; the mode refuses when a log EXISTS and the ordinary refusal "
          f"still refuses when it does not = {ok}")
    print("WITHOUT-LOG SELFTEST " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    # INTERCEPTED BEFORE argparse, AND HERE THE WALL IS HIGHER THAN IN cylinder_ladder.py:
    # `mode` is a POSITIONAL with choices, and --name and --out are required=True, so
    # argparse exits 2 on all three before any flag of ours could be read.  A selftest
    # checked after parse_args would be UNREACHABLE -- L-491, third campaign.
    if "--selftest-harvest-delegation" in sys.argv[1:]:
        sys.exit(selftest_harvest_delegation())
    if "--selftest-without-log-harvest" in sys.argv[1:]:
        sys.exit(selftest_without_log_harvest())

    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["stage", "harvest", "harvest-without-log"])
    p.add_argument("--name", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--reynolds", type=float)
    p.add_argument("--turbulence", choices=["laminar", "kOmegaSST"])
    p.add_argument("--n-radial", type=int)
    p.add_argument("--n-tangential", type=int)
    p.add_argument("--first-cell", type=float)
    p.add_argument("--farfield-diameters", type=float, default=20.0)
    p.add_argument("--end-time", type=float, default=90.0)
    p.add_argument("--dt0", type=float)
    p.add_argument("--max-co", type=float, default=1.5)
    p.add_argument("--perturbation", type=float, default=0.1)
    p.add_argument("--ranks", type=int, default=1)
    a = p.parse_args()
    if a.mode == "stage":
        stage(a.name, Path(a.out), reynolds=a.reynolds, turbulence=a.turbulence,
              farfield_diameters=a.farfield_diameters, n_radial=a.n_radial,
              n_tangential=a.n_tangential, first_cell=a.first_cell,
              end_time=a.end_time, dt0=a.dt0, max_co=a.max_co,
              perturbation=a.perturbation)
    else:
        # ITS OWN MODE, NOT A FLAG ON `harvest`. A separate mode cannot be reached by a
        # caller who did not mean it, and it reads in the shell history as what it is.
        harvest(a.name, Path(a.out), ranks=a.ranks,
                without_log=(a.mode == "harvest-without-log"))
