#!/usr/bin/env python3
"""F4 SUCCESSOR LAUNCHER.  Registered by
verification/campaign/F4S_SHOCK_LOCUS_PREREGISTRATION.md and pinned at that
document's commit.

THIS FILE IS A LAUNCHER, NOT A GRADER.  It computes nothing any gate reads.
Every gate value is re-derived by grade_f4s.py from the raw sample files.

THE CAP IS A GUARD HERE, NOT AN AUDIT.  Its predecessor totalled wall time
AFTER the last case returned, so its cap was evaluable exactly once -- at a
moment when every core-minute had already been spent.  It could not have
stopped a runaway of any size.  This file:

  * totals WALL x RANKS / 60 -- the rule-12 unit, and the ONLY quantity the cap
    governs.  ExecutionTime is the solver's internal accounting, excludes
    startup, meshing and sampling, and is recorded as a SECONDARY diagnostic
    that is never compared to the cap.
  * captures EVERY clock: blockMesh, checkMesh, the solver, and both sampling
    passes.  The predecessor captured only the solver, so its total was a LOWER
    BOUND on gross spend rather than the spend.
  * checks the running total AFTER EACH CASE and HALTS on a crossing, launching
    nothing further and writing CAP_HALT.json.
  * checks a PROJECTION before each case and refuses to start one that cannot
    fit under the cap.
  * DISPATCHES SERIALLY.  Concurrency would put cases in flight that a halt
    cannot stop, and an unstoppable in-flight overrun is exactly the defect
    this rewrite exists to remove.  Elapsed time is spent to buy a real guard.

Exit codes: 0 every case completed under the cap; 2 a guard refused or the cap
halted the batch; 3 usage or a pre-existing artifact.
"""
import sys

if not __debug__:
    sys.stderr.write("REFUSE (exit 2): launch_f4s.py will not run under -O.\n")
    sys.exit(2)

import argparse
import json
import os
import subprocess
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
F4 = os.path.join(REPO, "verification", "runs", "F4_runs")
sys.path.insert(0, HERE)
sys.path.insert(0, F4)

import grade_f4s as GR                                          # noqa: E402

FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"
MACHS = GR.MACHS
LEVELS = GR.LEVELS
ENDTIME = GR.ENDTIME
NWRITES = GR.NWRITES
N_WINDOW = GR.N_WINDOW
RANKS = 1                       # np = 1 for all nine cases
DECOMPOSITION_SEED = "none (identity; decomposePar is NOT invoked; np = 1)"
PER_CASE_WALL_GUARD_S = GR.PER_CASE_WALL_GUARD_S
CAP_CORE_MIN = 36.0             # prereg 9.3.  WALL x RANKS / 60.
ORDER = [(M, lv) for M in MACHS for lv in LEVELS]


def resolve(path, what):
    """Resolve a path against the disk IN THIS INVOCATION.  The a1fbe127 reorg
    left ~140 tracked scripts citing a tree that no longer exists; a path is not
    a path until this process has seen it."""
    if not os.path.exists(path):
        sys.stderr.write(f"REFUSE: {what} not found at {path}\n")
        sys.exit(3)
    return path


def measure_load():
    """THE COST BASIS IS CONDITIONED ON THE LOAD AT LAUNCH, MEASURED HERE.

    Never a figure relayed from a brief and never the load when the estimate was
    written: the predecessor's 1.389 calibration miss came from a supervisor's
    stale 3.70 while the box was actually at 11.14.
    """
    with open("/proc/loadavg") as fh:
        la = fh.read().split()
    return dict(load1=float(la[0]), load5=float(la[1]), load15=float(la[2]),
                ncpu=os.cpu_count(), measured_at=time.time(),
                measured_by="launch_f4s.py in its own invocation")


def sh(cmd, cwd, logfile, timeout=None):
    """Run one OpenFOAM command.  Returns (rc, wall_s).  NEVER raises on a
    non-zero rc -- the caller decides, because a crash is a FINDING until triage
    says otherwise, and triage is the supervisor's."""
    full = f"source {FOAM_BASHRC} >/dev/null 2>&1; {cmd}"
    t0 = time.time()
    try:
        p = subprocess.run(["bash", "-c", full], cwd=cwd,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           timeout=timeout)
        rc, out = p.returncode, p.stdout
    except subprocess.TimeoutExpired as exc:
        rc = 124
        out = (exc.stdout or b"") + (
            f"\n*** KILLED BY THE {timeout:.0f} s PER-CASE RUNAWAY GUARD ***\n"
        ).encode()
    dt = time.time() - t0
    with open(logfile, "wb") as fh:
        fh.write(out)
        fh.flush()
        os.fsync(fh.fileno())
    return rc, dt


def write_rc(case_dir, rc):
    """Write the return code, flush, fsync, then READ IT BACK from disk.
    `set -e` does not gate at tool top level nor inside ( set -e; ... ), so an
    inferred rc is not an rc."""
    p = os.path.join(case_dir, "RC.txt")
    with open(p, "w") as fh:
        fh.write(f"{rc}\n")
        fh.flush()
        os.fsync(fh.fileno())
    back = open(p).read().strip()
    if back != str(rc):
        sys.stderr.write(f"REFUSE: {p}: wrote {rc!r}, read back {back!r}\n")
        sys.exit(2)
    return back


def append_ledger(ledger_path, row):
    rows = []
    if os.path.isfile(ledger_path):
        with open(ledger_path) as fh:
            rows = json.load(fh)["cases"]
    rows.append(row)
    total = sum(r["core_min_wall"] for r in rows)
    with open(ledger_path, "w") as fh:
        json.dump(dict(cap_core_min=CAP_CORE_MIN,
                       cap_quantity="wall seconds x ranks / 60 (CLAUDE.md "
                                    "rule 12); ExecutionTime is NEVER compared "
                                    "to this cap",
                       ranks=RANKS, decomposition_seed=DECOMPOSITION_SEED,
                       running_total_core_min=total, cases=rows), fh, indent=2)
        fh.flush()
        os.fsync(fh.fileno())
    return total


def run_case(M, level, root, solver_timeout_s):
    from make_cylinder_case import make_case
    from run_cylinder_case import write_sampledicts

    case_dir = os.path.join(root, "cyl", f"M{M}", level)
    GR.check_no_preexisting(case_dir)
    if os.path.isdir(case_dir) and os.listdir(case_dir):
        sys.stderr.write(f"REFUSE: {case_dir} exists and is not empty; this "
                         "launcher refuses, and DELETES NOTHING\n")
        sys.exit(3)
    os.makedirs(case_dir, exist_ok=True)

    clocks = {}
    meta = make_case(case_dir, M, level, end_time_abs=ENDTIME, nWrites=NWRITES)
    write_sampledicts(case_dir, meta["R_top"])

    rc, clocks["blockMesh_s"] = sh("blockMesh", case_dir,
                                   f"{case_dir}/log.blockMesh")
    if rc != 0:
        write_rc(case_dir, rc)
        return dict(M=M, level=level, rc=rc, stage="blockMesh", clocks=clocks)
    rc, clocks["checkMesh_s"] = sh("checkMesh", case_dir,
                                   f"{case_dir}/log.checkMesh")
    if rc != 0:
        write_rc(case_dir, rc)
        return dict(M=M, level=level, rc=rc, stage="checkMesh", clocks=clocks)

    # THE AGE-GUARD REFERENCE: 0/T is touched LAST before the solver starts, so
    # it dates the run allowed to produce this answer.
    os.utime(os.path.join(case_dir, "0", "T"), None)

    clocks["solver_timeout_s"] = solver_timeout_s
    rc, clocks["solver_s"] = sh("rhoCentralFoam", case_dir,
                                f"{case_dir}/log.rhoCentralFoam",
                                timeout=solver_timeout_s)
    write_rc(case_dir, rc)
    if rc != 0:
        return dict(M=M, level=level, rc=rc, stage="rhoCentralFoam",
                    clocks=clocks)

    tdirs = sorted((float(n), n) for n in os.listdir(case_dir)
                   if _isnum(n) and float(n) > 0.0)
    if len(tdirs) < N_WINDOW:
        sys.stderr.write(f"REFUSE: {case_dir}: {len(tdirs)} written times, the "
                         f"registered sustained window is {N_WINDOW}\n")
        sys.exit(2)
    win = tdirs[-N_WINDOW:]
    span = f"{win[0][1]}:{win[-1][1]}"
    rc, clocks["sample_s"] = sh(f"postProcess -func sampleDict -time '{span}'",
                                case_dir, f"{case_dir}/log.sample")
    rc2, clocks["surfsample_s"] = sh(
        f"postProcess -func surfaceSampleDict -time '{span}'",
        case_dir, f"{case_dir}/log.surfsample")

    return dict(M=M, level=level, rc=0, sample_rc=rc, surfsample_rc=rc2,
                stage="complete", clocks=clocks, window=[n for _v, n in win])


def _isnum(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    a = ap.parse_args()

    resolve(FOAM_BASHRC, "the OpenFOAM environment")
    resolve(os.path.join(F4, "make_cylinder_case.py"), "make_cylinder_case.py")
    resolve(os.path.join(F4, "run_cylinder_case.py"), "run_cylinder_case.py")
    resolve(os.path.join(HERE, "grade_f4s.py"), "the frozen grading path")

    root = os.path.abspath(a.root)
    if "successor_" not in root:
        sys.stderr.write(f"REFUSE: {root} is not a successor_* run root\n")
        sys.exit(3)
    if os.path.exists(root):
        sys.stderr.write(f"REFUSE: {root} already exists; rule 2's absence "
                         "condition is checked here, in this invocation, and "
                         "this launcher DELETES NOTHING\n")
        sys.exit(3)
    os.makedirs(root)

    load = measure_load()
    with open(os.path.join(root, "LAUNCH_LOAD.json"), "w") as fh:
        json.dump(load, fh, indent=2)
    with open(os.path.join(root, "LAUNCH_HEAD.txt"), "w") as fh:
        fh.write(subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                                capture_output=True, text=True).stdout)

    ledger = os.path.join(root, "RUN_LEDGER.json")
    total = 0.0
    worst_case_core_min = 0.0

    for M, level in ORDER:
        # ---- THE GUARD, AND IT IS EVALUATED BEFORE EVERY CASE -------------
        # The remaining budget is converted into THIS case's solver timeout, so
        # no single case can carry the batch past the cap: the solver is killed
        # at the remaining budget or at the per-case runaway guard, whichever
        # is smaller.  The residual overrun is then bounded by that case's mesh
        # and sampling clocks -- seconds, not core-minutes -- and it is
        # measured and reported rather than absorbed.
        budget_s = (CAP_CORE_MIN - total) * 60.0 / RANKS
        if budget_s < 60.0:
            _halt(root, "PROJECTED", total, M, level)
        solver_timeout_s = min(PER_CASE_WALL_GUARD_S, budget_s)

        t0 = time.time()
        row = run_case(M, level, root, solver_timeout_s)
        wall = time.time() - t0
        row["wall_s_total"] = wall
        row["core_min_wall"] = wall * RANKS / 60.0
        row["ranks"] = RANKS
        row["decomposition_seed"] = DECOMPOSITION_SEED
        row["cap_remaining_core_min_before"] = CAP_CORE_MIN - total
        worst_case_core_min = max(worst_case_core_min, row["core_min_wall"])
        total = append_ledger(ledger, row)
        print(f"{M} {level}: rc={row['rc']} stage={row['stage']} "
              f"{row['core_min_wall']:.4f} core-min  running {total:.4f} / "
              f"{CAP_CORE_MIN}")
        if row["rc"] != 0:
            print("CRASH -- a crash is a FINDING until triage says otherwise, "
                  "and triage is the supervisor's.  Batch halted.")
            sys.exit(2)
        # INCREMENTAL CAP CHECK, AFTER EACH CASE.
        if total > CAP_CORE_MIN:
            _halt(root, "CROSSED", total, M, level)

    print(f"ALL {len(ORDER)} CASES COMPLETE.  Measured spend {total:.4f} "
          f"core-min wall against the {CAP_CORE_MIN} cap.")
    return 0


def _halt(root, kind, total, M, level, projected=None):
    path = os.path.join(root, "CAP_HALT.json")
    with open(path, "w") as fh:
        json.dump(dict(kind=kind, cap_core_min=CAP_CORE_MIN,
                       running_total_core_min=total,
                       halted_before=f"M{M}/{level}", projected=projected,
                       quantity="wall x ranks / 60",
                       note="The cap is a RUNAWAY GUARD.  The batch is halted "
                            "and REPORTED to the cfd supervisor, who decides.  "
                            "This launcher does not extend a cap."), fh,
                  indent=2)
        fh.flush()
        os.fsync(fh.fileno())
    sys.stderr.write(f"CAP HALT ({kind}): {total:.4f} core-min against a cap of "
                     f"{CAP_CORE_MIN}.  Halted before M{M}/{level}.  "
                     f"Written to {path}\n")
    sys.exit(2)


if __name__ == "__main__":
    sys.exit(main())
