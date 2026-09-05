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


def harvest(name: str, out_dir: Path, ranks: int = 1) -> dict:
    out_dir = Path(out_dir)
    staged = json.loads((out_dir / "stage_params.json").read_text())
    params = staged["params"]
    remote_dir = Path(staged["remote_dir"])
    timings = dict(staged["timings"])

    log_path = remote_dir / "log.pimpleFoam"
    if not log_path.exists():
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
            f"{remote_dir}")
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
        "wall_seconds": sum(v for v in timings.values() if v is not None), "timings": timings,
        "stationary": drift["relative_drift"] <= 0.10,
        "final_time_reached": times[-1] if times else None,
    }
    (out_dir / "record.json").write_text(json.dumps(record, indent=2, default=str))
    lr_txt = f"Lr/D {lr['lr_over_d']:.3f}" if lr and lr["lr_over_d"] else "Lr/D not found"
    cpb_txt = f"-Cpb {cpb['cpb_magnitude']:.3f}" if cpb else "Cpb n/a"
    st_txt = f"St {strouhal:.4f}" if strouhal else "no period detected"
    print(f"[{name}] Cd {cd_stats['mean']:.4f} (drift {100*drift['relative_drift']:.1f}%), "
          f"{st_txt}, {cpb_txt}, {lr_txt}, wall {record['wall_seconds']:.0f}s, "
          f"final_t={record['final_time_reached']}")
    return record


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
    y_token = 'rglob("yPlus.dat")'
    y_sel_src = inspect.getsource(CL._yplus_series_path)
    y_gone = y_token not in h_src
    # THE PLANT for this detector: the OLD exact-name glob must still appear inside the
    # selector's own control-facing comment/source region.  The selector deliberately globs
    # `yPlus*.dat`, so we plant against the wider token instead and prove the detector reads
    # this source at all rather than returning a reflexive True.
    y_detector_works = 'rglob("yPlus*.dat")' in y_sel_src
    if y_gone and y_detector_works:
        fired.append("YPLUS LOCAL COPY: the exact-name rglob is GONE from harvest(), and "
                     "the detector DOES read CL._yplus_series_path's own glob -- the "
                     "absence was read by a detector shown able to see a presence")
    else:
        ok = False
        fired.append(f"YPLUS LOCAL COPY: absent from harvest={y_gone}, detector reads the "
                     f"selector source={y_detector_works} (must both be True)")

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


if __name__ == "__main__":
    # INTERCEPTED BEFORE argparse, AND HERE THE WALL IS HIGHER THAN IN cylinder_ladder.py:
    # `mode` is a POSITIONAL with choices, and --name and --out are required=True, so
    # argparse exits 2 on all three before any flag of ours could be read.  A selftest
    # checked after parse_args would be UNREACHABLE -- L-491, third campaign.
    if "--selftest-harvest-delegation" in sys.argv[1:]:
        sys.exit(selftest_harvest_delegation())

    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["stage", "harvest"])
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
        harvest(a.name, Path(a.out), ranks=a.ranks)
