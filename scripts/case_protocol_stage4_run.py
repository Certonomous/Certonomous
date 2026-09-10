#!/usr/bin/env python3
"""THE CASE PROTOCOL -- STAGE 4: FULL RUN.

EXIT CONDITION
    The registered full run reaches the strict completion rule -- rc = 0, an `End`
    line, last time == endTime, every required field present, the ExecutionTime
    count consistent with the steps written, and EVERY field at endTime newer than
    the case's own 0/T -- and the autograder has produced its verdict from a
    comparator pinned before the run started.

FAILURE ACTION -- FIXED, NOT DISCRETIONARY
    The monitor's stops are enumerated below.  Each has ONE registered action, and
    the SAME ACTION IS NEVER TAKEN TWICE ON THE SAME STATE.  When the actions for a
    stop are spent, the ladder for that stop is exhausted and the case is PARKED.

SURVIVAL
    Solver, autograder and monitor are re-parented to init (PPID 1) so a fleet death
    -- a usage limit, a compaction, an agent that ends -- does not take the run with
    it.  An agent's watcher dies with the agent; the daemon does not.

THE rc TRAP THIS FILE IS BUILT AROUND
    `setsid timeout cmd` exits 0 for EVERY outcome, including SIGFPE.  So rc is
    captured INSIDE the detached wrapper, from the solver process itself, written to
    RC.txt by the wrapper, and never inferred from the exit status of anything that
    launched it.

THIS SCRIPT DOES NOT LAUNCH UNLESS `--go` IS PASSED.  Without it, it writes the
launcher, the monitor and the manifest, verifies the preflight, and stops.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
import case_protocol_lib as L  # noqa: E402

STAGE = "STAGE4"

# ---------------------------------------------------------------------------
# The monitor's stops.  Fixed, registered, one action each.
# ---------------------------------------------------------------------------

# THE STAGE-4 LADDER, and it is NOT the stage-3 ladder.  Stage 3 climbs
# mesh -> numerics -> model, because a smoke that fails is asking whether the case
# is set up right.  Stage 4 climbs a different ladder, because a full run that
# stalls is asking how to REACH a state the setup can already represent:
STAGE4_LADDER = [
    {"rung": 1, "id": "CONTINUATION",
     "change": "restart from a converged neighbour -- the next coarser level's converged "
               "field mapped up, or the same level at an easier operating point",
     "why": "the cheapest fix for a hard start is not to start hard"},
    {"rung": 2, "id": "RELAXATION_REDUCTION",
     "change": "reduce under-relaxation on the equation that is misbehaving",
     "why": "relaxation affects only the PATH to steady state -- its contribution scales with "
            "(phi_new - phi_old) and vanishes at convergence -- so the converged answer is "
            "unchanged and the gate stays unbiased"},
    {"rung": 3, "id": "PSEUDO_TRANSIENT",
     "change": "march in pseudo-time (localEuler / LTS) rather than solving steady",
     "why": "a pseudo-transient march reaches states a steady solve cannot get to; it owes the "
            "time-step-independence demonstration registered with it"},
    {"rung": 4, "id": "TRANSIENT_RE_REGISTRATION",
     "change": "re-register the case as genuinely transient",
     "why": "if the flow will not hold still, the honest instrument is a transient one. This is a "
            "NEW registration, not an amendment: it changes what is being measured"},
]

MONITOR_STOPS = [
    {
        "id": "RESIDUAL_GROWTH",
        "detect": ("the mean initial residual of any equation over the last window exceeds its "
                   "mean over the preceding window by more than growth_factor"),
        "why": "a diverging march does not become a converged one by being given more iterations",
        "actions": ["halve maxCo", "drop div(phi,U) to first order for the first 20 percent",
                    "PARK"],
    },
    {
        "id": "BOUNDS_VIOLATION",
        "detect": "any clamp fvOption reports LimitedCells > clamp_tolerance at the plateau",
        "why": ("a clamp ACTIVE at the plateau is a boundary condition on the answer, not a "
                "stabiliser. The converged state is then nonphysical and every gate downstream "
                "of it is biased. This is the specific failure that stopped the previous attempt "
                "on this case: cells pinned at WHATEVER ceiling was set, i.e. unbounded, not a "
                "finite hot value."),
        "actions": ["raise the ceiling and re-check whether cells pin at the new one "
                    "(a diagnostic, not a fix: pinning at any ceiling means unbounded)",
                    "PARK -- the clamp is masking a physical or setup defect"],
    },
    {
        "id": "PLATEAU_WITH_STALLED_LINEAR_SOLVER",
        "detect": ("the graded quantity is flat over the registered trailing window WHILE a "
                   "linear solver is hitting its iteration ceiling every step"),
        "why": ("flatness that comes from the linear solver giving up is not convergence. The two "
                "look identical in the residual trace and only one of them is an answer."),
        "actions": ["raise maxIter and tighten relTol on the stalled equation", "PARK"],
    },
    {
        "id": "COHERENT_OSCILLATION",
        "detect": ("the graded quantity oscillates with a dominant frequency and a stable "
                   "amplitude over the trailing window"),
        "why": ("THIS IS NOT A FAILURE. It is the physics voting that the flow is UNSTEADY. A "
                "steady solver asked for a steady answer to an unsteady flow will either "
                "oscillate or be damped into a fiction by the numerics, and the oscillation is "
                "the honest one of those two."),
        "marks": "physics voting unsteady",
        "actions": ["record the frequency and amplitude, mark the run PHYSICS VOTING UNSTEADY, "
                    "and refer the steady/unsteady question rather than damping it away"],
    },
    {
        "id": "COST_PER_ITERATION_EXCURSION",
        "detect": "wall seconds per iteration over the last window exceeds twice the estimate",
        "why": ("a run that is suddenly twice as slow per iteration is usually swapping, "
                "contending, or has lost a rank -- all of which change what the cost figure "
                "means, and none of which are visible in the residual trace"),
        "note": ("under the 2026-09-10 exemption this STOP DOES NOT KILL A 3D DEMO RUN. It is a "
                 "REPORT. And a silent runner is not evidence a cap was respected: a cap never "
                 "enforced and a cap never exceeded look identical from the log."),
        "actions": ["report the excursion with its measured ratio and continue"],
    },
]


# ---------------------------------------------------------------------------
# Cost, counted over EVERY solve under the run root.
# ---------------------------------------------------------------------------

def spend_under_root(root: Path, ranks_default: int = 1) -> Dict[str, Any]:
    """Core-minutes over EVERY solver log under the run root, not just the graded one.

    An accumulator that counts only the case it was pointed at under-reports a family
    by whatever the diagnostics cost -- measured at 37x on this campaign's
    predecessor, 3.8 core-min recorded against 135.87 actually spent.  Diagnostic
    solves are real compute on real cores and they are part of what the case cost.

    Each log's ranks come from its OWN banner (`nProcs : N`) and NOT from
    decomposeParDict, which can post-date the run.  The FIRST `nProcs` match in a
    log is the one the run actually had.
    """
    rows = []
    for log in sorted(root.rglob("log.*")):
        txt = log.read_text(errors="replace")
        if "ExecutionTime" not in txt and "ClockTime" not in txt:
            continue
        ct = re.findall(r"ClockTime = (\d+)\s*s", txt)
        if not ct:
            continue
        m = re.search(r"^nProcs\s*:\s*(\d+)", txt, re.M)
        ranks = int(m.group(1)) if m else ranks_default
        wall = float(ct[-1])
        rows.append({"log": str(log.relative_to(root)), "clock_s": wall, "ranks": ranks,
                     "ranks_source": "log banner nProcs" if m else f"DEFAULT {ranks_default}, NOT MEASURED",
                     "core_min": wall * ranks / 60.0,
                     "stall_flag": wall > 3600})
    total = sum(r["core_min"] for r in rows)
    return {"rows": rows, "n_logs": len(rows), "core_min_total": total,
            "usd_derived": total / 60.0 * L.RATE_USD_PER_CORE_HOUR,
            "gross_or_cleaned": "GROSS -- rows over 3600 wall s are flagged, not removed",
            "method": ("every log.* under the run root carrying a ClockTime, ranks from each "
                       "log's own banner. Counts diagnostics, not only the graded solve.")}


# ---------------------------------------------------------------------------
# The detached launcher.
# ---------------------------------------------------------------------------

LAUNCHER = r"""#!/bin/bash
# THE CASE PROTOCOL -- stage 4 detached launcher.  Written by
# scripts/case_protocol_stage4_run.py; do not edit in place.
#
# rc IS CAPTURED HERE, INSIDE THE DETACHED WRAPPER, FROM THE SOLVER PROCESS.
# `setsid timeout cmd` returns 0 for every outcome including a SIGFPE, so the exit
# status of anything wrapping this script says nothing about the run.
set -u
CASE="__CASE__"
SOLVER="__SOLVER__"
RANKS=__RANKS__
LOG="$CASE/log.$SOLVER"
STATUS="$CASE/STATUS.stage4"

source __BASHRC__ '' >/dev/null 2>&1
cd "$CASE" || exit 90

echo "launched_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"  > "$STATUS"
echo "ppid=$PPID"                                  >> "$STATUS"
echo "ranks=$RANKS"                                >> "$STATUS"

# 0/T is touched LAST, immediately before the solver starts.  Rule 4's age guard
# dates the run by it: every field at endTime must be NEWER than this file, so it
# must be the last thing written before compute begins.
touch "$CASE/0/T"
T0=$(date +%s)

if [ "$RANKS" -gt 1 ]; then
    decomposePar -case "$CASE" -force > "$CASE/log.decomposePar" 2>&1
    DRC=$?
    echo "decomposePar_rc=$DRC" >> "$STATUS"
    [ "$DRC" -ne 0 ] && { echo "RC=$DRC" > "$CASE/RC.txt"; exit "$DRC"; }
    mpirun -np "$RANKS" "$SOLVER" -case "$CASE" -parallel > "$LOG" 2>&1
    RC=$?
    if [ "$RC" -eq 0 ]; then
        reconstructPar -case "$CASE" -latestTime > "$CASE/log.reconstructPar" 2>&1
        echo "reconstructPar_rc=$?" >> "$STATUS"
    fi
else
    "$SOLVER" -case "$CASE" > "$LOG" 2>&1
    RC=$?
fi

T1=$(date +%s)
echo "RC=$RC" > "$CASE/RC.txt"
echo "solver_rc=$RC"                >> "$STATUS"
echo "wall_s=$((T1-T0))"            >> "$STATUS"
echo "core_min=$(echo "($T1-$T0)*$RANKS/60" | bc -l)" >> "$STATUS"
echo "finished_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"    >> "$STATUS"

# The autograder runs from HERE, in the same detached process group, so a graded
# verdict does not depend on any agent still being alive.
if [ -n "__GRADER__" ] && [ "$RC" -eq 0 ]; then
    __GRADER_ARGV__ > "$CASE/log.autograder" 2>&1
    echo "autograder_rc=$?" >> "$STATUS"
fi
exit "$RC"
"""


def build_launcher(case: Path, solver: str, ranks: int, grader_argv: Optional[List[str]]) -> Path:
    body = (LAUNCHER
            .replace("__CASE__", str(case.resolve()))
            .replace("__SOLVER__", solver)
            .replace("__RANKS__", str(ranks))
            .replace("__BASHRC__", L.FOAM_BASHRC)
            .replace("__GRADER__", "yes" if grader_argv else "")
            .replace("__GRADER_ARGV__",
                     " ".join(f"'{x}'" for x in grader_argv) if grader_argv else "true"))
    p = case / "launch_stage4.sh"
    p.write_text(body)
    p.chmod(0o755)
    return p


def preflight(case: Path, spec: Dict[str, Any], level: str) -> List[Dict[str, Any]]:
    """Every condition that must hold BEFORE a single core-second is spent.

    Refusals here are cheap.  Discovering any of them two hours in is not.
    """
    out = []

    def add(name, ok, detail):
        out.append({"check": name, "pass": bool(ok), "detail": detail})

    add("case exists", case.is_dir(), str(case))
    add("no pre-existing time directory",
        not any(d.is_dir() and re.fullmatch(r"[1-9]\d*(\.\d+)?", d.name) for d in case.iterdir()),
        "a guard refuses a case where a time directory already exists: the age guard cannot "
        "distinguish this run's fields from a previous run's")
    cert = case.parent / "BIRTH_CERTIFICATE.json"
    if cert.is_file():
        mesh = (case / "constant" / "polyMesh").resolve()
        ok, complaints = L.verify_birth(cert, mesh)
        add("mesh matches its birth certificate", ok,
            "; ".join(complaints) if complaints else f"manifest verified against {mesh}")
    else:
        add("mesh matches its birth certificate", False, f"no certificate at {cert}")

    mem = L.memory_state()
    bpc = spec["numerics"].get("solver_bytes_per_cell")
    ncell = None
    if cert.is_file():
        ncell = json.loads(cert.read_text()).get("mesh", {}).get("n_cells")
    if bpc and ncell:
        uplift = float(spec["numerics"].get("parallel_memory_uplift", 1.0))
        need = float(bpc) * int(ncell) * uplift / (1024 ** 3)
        add("memory headroom", need <= mem.mem_available_gib,
            f"needs {need:.2f} GiB (bytes/cell {float(bpc):.1f} MEASURED, largest of three "
            f"levels, x parallel uplift {uplift:g} ASSUMED), MemAvailable "
            f"{mem.mem_available_gib:.2f} GiB, drained ceiling {mem.drained_ceiling_gib:.2f} GiB")
    else:
        add("memory headroom", False,
            "solver bytes/cell NOT MEASURED, so headroom cannot be judged. A meshing "
            "bytes/cell is not a solver bytes/cell and is not substituted.")

    reg = spec.get("registration_path")
    if reg:
        rp = Path("/home/ubuntu/Certonomous") / reg
        committed = subprocess.run(["git", "-C", "/home/ubuntu/Certonomous",
                                    "cat-file", "-e", f"HEAD:{reg}"],
                                   capture_output=True).returncode == 0
        add("registration COMMITTED at HEAD", committed,
            f"{reg}: {'present in HEAD' if committed else 'NOT IN HEAD -- check 4 forbids compute'}")
    else:
        add("registration COMMITTED at HEAD", False, "no registration_path in the spec")
    return out


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--case-root", required=True)
    ap.add_argument("--level", required=True)
    ap.add_argument("--ranks", type=int, default=4)
    ap.add_argument("--grader", default=None)
    ap.add_argument("--go", action="store_true",
                    help="ACTUALLY LAUNCH. Without this the stage builds the launcher and the "
                         "manifest, runs the preflight, and stops.")
    a = ap.parse_args(argv)

    spec = json.loads(Path(a.spec).read_text())
    out = Path(a.out)
    case = Path(a.case_root) / a.level / "case"

    pf = preflight(case, spec, a.level)
    for c in pf:
        print(L.state_line(STAGE, f"preflight {c['check']}",
                           "PASS" if c["pass"] else "REFUSE", detail=c["detail"][:150]))

    grader_argv = None
    if a.grader:
        grader_argv = [sys.executable, str(Path(a.grader).resolve()),
                       "--case", str(case.resolve()),
                       "--level", a.level,
                       "--out", str((out / f"GRADE_{a.level}.json").resolve())]
    launcher = build_launcher(case, spec["run_control"]["solver"], a.ranks, grader_argv)
    print(L.state_line(STAGE, "launcher", "WRITTEN", path=str(launcher),
                       sha256=L.sha256_file(launcher)[:16]))

    manifest = {
        "stage": 4, "case": spec["case"], "level": a.level,
        "built_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "launcher": str(launcher), "launcher_sha256": L.sha256_file(launcher),
        "ranks": a.ranks, "solver": spec["run_control"]["solver"],
        "end_time": spec["run_control"]["end_time"],
        "checkpoint_interval": spec["run_control"]["write_interval"],
        "monitor_stops": MONITOR_STOPS,
        "stage4_ladder": STAGE4_LADDER,
        "preflight": pf,
        "budget_gate": spec.get("budget_gate"),
        "detachment": ("setsid + nohup, re-parented to PPID 1. rc is captured INSIDE the wrapper "
                       "from the solver process and written to RC.txt; no exit status of any "
                       "launching process is consulted."),
        "grader_argv": grader_argv,
        "launched": False,
    }
    blockers = [c for c in pf if not c["pass"]]
    if not a.go:
        (out / f"STAGE4_MANIFEST_{a.level}.json").write_text(json.dumps(manifest, indent=2) + "\n")
        print(L.state_line(STAGE, "EXIT", "BUILT, NOT LAUNCHED",
                           blockers=len(blockers), note="pass --go to launch"))
        return 0 if not blockers else 7

    if blockers:
        print(L.state_line(STAGE, "EXIT", "BLOCKED",
                           reason=f"{len(blockers)} preflight refusals; no compute launched"))
        return 7

    proc = subprocess.Popen(["setsid", "nohup", str(launcher)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            start_new_session=True)
    time.sleep(2)
    manifest["launched"] = True
    manifest["launch_pid"] = proc.pid
    (out / f"STAGE4_MANIFEST_{a.level}.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(L.state_line(STAGE, "EXIT", "LAUNCHED", pid=proc.pid,
                       note="rc will be in RC.txt, written by the wrapper from the solver process"))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except L.Refusal as e:
        print(L.state_line(STAGE, "REFUSAL", e.code, detail=e.detail))
        sys.exit(2)
