#!/usr/bin/env python3
"""F4 CONVERSION LAUNCHER -- limb A only (Gates 1 and 2, the 2-D cylinder).

Registered by verification/campaign/F4_CONVERSION_PREREGISTRATION.md, frozen at
3e82e989.  THIS FILE IS A LAUNCHER, NOT A GRADER.  It computes NOTHING that any
gate reads: it builds cases, runs the solver, runs the two sampling passes, and
records the return code.  Every gate value is re-derived by grade_f4.py from the
raw sample files.  The one artifact it writes that the grader consumes is
RC.txt, which is a COMPLETION artifact -- and it is written from the solver's
own exit status, synced, and read back rather than inferred (`set -e` does not
gate at tool top level nor inside `( set -e; ... )`).

GUARDS, all refusing:
  * check_no_preexisting() from the FROZEN grader is called before any case is
    built -- rule 4's launch-side clause.  A case directory that already exists
    at all is refused outright (rc 3), so a graded artifact can never be
    overwritten.
  * per-case runaway guard: the solver is killed at 1200 wall s (prereg 7.8).
  * batch HARD CAP 24.0 core-minutes (prereg 10.3).  A crossing STOPS the batch
    and is REPORTED; this file never extends a cap.

Exit codes: 0 = every case completed; 2 = a guard refused; 3 = usage/pre-existing.
"""
import os
import sys
import json
import time
import shutil
import argparse
import subprocess
import concurrent.futures as cf

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
F4 = os.path.join(REPO, "verification", "runs", "F4_runs")
sys.path.insert(0, HERE)
sys.path.insert(0, F4)

import grade_f4 as GR                                          # noqa: E402

FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"
MACHS = (6.0, 7.0, 8.0)
LEVELS = ("coarse", "medium", "fine")
ENDTIME = 6.0
NWRITES = 8
N_SNAPSHOTS = 3
STALL_WALL_S = 1200.0
CAP_CORE_MIN = 24.0
MAX_WORKERS = 6            # <= 6 cores; two other cfd lanes are live


def sh(cmd, cwd, logfile, timeout=None):
    """Run one OpenFOAM command.  Returns (rc, wall_s).  NEVER raises on a
    non-zero rc -- the caller decides, because a crash is a FINDING."""
    full = f"source {FOAM_BASHRC} >/dev/null 2>&1; {cmd}"
    t0 = time.time()
    try:
        p = subprocess.run(["bash", "-c", full], cwd=cwd,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           timeout=timeout)
        rc, out = p.returncode, p.stdout
    except subprocess.TimeoutExpired as exc:
        rc = 124
        out = (exc.stdout or b"") + \
            f"\n*** KILLED BY THE {timeout:.0f} s PER-CASE RUNAWAY GUARD ***\n".encode()
    dt = time.time() - t0
    with open(logfile, "wb") as fh:
        fh.write(out)
        fh.flush()
        os.fsync(fh.fileno())
    return rc, dt


def write_rc(case_dir, rc):
    """Write the return code, flush, fsync, then READ IT BACK from disk."""
    p = os.path.join(case_dir, "RC.txt")
    with open(p, "w") as fh:
        fh.write(f"{rc}\n")
        fh.flush()
        os.fsync(fh.fileno())
    back = open(p).read().strip()
    if back != str(rc):
        raise RuntimeError(f"{p}: wrote {rc!r}, read back {back!r}")
    return back


def run_case(args):
    M, level, root = args
    from make_cylinder_case import make_case
    from run_cylinder_case import write_sampledicts

    case_dir = os.path.join(root, "cyl", f"M{M}", level)
    rec = dict(M=M, level=level, case_dir=case_dir)

    # ---- rule 4's launch-side guard, from the FROZEN grader ----
    if os.path.exists(case_dir):
        rec.update(status="REFUSED",
                   why=f"{case_dir} already exists -- refusing to overwrite")
        return rec
    os.makedirs(case_dir, exist_ok=False)
    try:
        GR.check_no_preexisting(case_dir)
    except GR.Refusal as exc:
        rec.update(status="REFUSED", why=str(exc))
        return rec

    t_all0 = time.time()
    meta = make_case(case_dir, M, level, end_time_abs=ENDTIME, nWrites=NWRITES)

    rc, t_mesh = sh("blockMesh", case_dir, f"{case_dir}/log.blockMesh", 600)
    if rc != 0:
        write_rc(case_dir, rc)
        rec.update(status="FAILED", stage="blockMesh", rc=rc)
        return rec
    rc, t_chk = sh("checkMesh -noTopology", case_dir,
                   f"{case_dir}/log.checkMesh", 600)
    if rc != 0:
        write_rc(case_dir, rc)
        rec.update(status="FAILED", stage="checkMesh", rc=rc)
        return rec

    rc_solver, t_run = sh("rhoCentralFoam", case_dir,
                          f"{case_dir}/log.rhoCentralFoam", STALL_WALL_S)
    write_rc(case_dir, rc_solver)          # the SOLVER's rc, synced and read back
    rec.update(rc=rc_solver, t_run_s=t_run, core_min=t_run / 60.0,
               ncells=meta["ntheta"] * meta["nr"])
    if rc_solver != 0:
        rec.update(status="CRASH" if rc_solver != 124 else "RUNAWAY-STOP",
                   stage="rhoCentralFoam")
        return rec

    # ---- sampling: the grader reads these files, this file does not ----
    write_sampledicts(case_dir, meta["R_top"], 7)
    tdirs = sorted([d for d in os.listdir(case_dir)
                    if os.path.isdir(os.path.join(case_dir, d))
                    and d.replace(".", "", 1).isdigit()], key=float)
    if len(tdirs) < N_SNAPSHOTS + 1:
        rec.update(status="FAILED", stage="writes",
                   why=f"only {len(tdirs)} time dirs")
        return rec
    snaps = tdirs[-N_SNAPSHOTS:]
    for func, log in (("sampleDict", "log.sample"),
                      ("surfaceSampleDict", "log.surfsample")):
        rc, _ = sh(f"postProcess -func {func} -time '{snaps[0]}:{snaps[-1]}'",
                   case_dir, f"{case_dir}/{log}", 900)
        if rc != 0:
            rec.update(status="FAILED", stage=func, rc=rc)
            return rec

    rec.update(status="COMPLETE", t_total_s=time.time() - t_all0,
               snapshots=snaps)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--ledger", default=None)
    a = ap.parse_args()

    if os.path.exists(a.root):
        print(f"REFUSED: run root {a.root} already exists (rc 3)", file=sys.stderr)
        return 3
    os.makedirs(a.root, exist_ok=False)

    jobs = [(M, lv, a.root) for M in MACHS for lv in LEVELS]
    done, total_cm, capped = [], 0.0, False
    t0 = time.time()
    with cf.ProcessPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = {ex.submit(run_case, j): j for j in jobs}
        for fut in cf.as_completed(futs):
            rec = fut.result()
            total_cm += rec.get("core_min", 0.0)
            done.append(rec)
            print(f"  {rec['status']:14s} M{rec['M']}/{rec['level']:6s} "
                  f"rc={rec.get('rc')} {rec.get('core_min', 0.0):.4f} core-min "
                  f"(cum {total_cm:.4f} / cap {CAP_CORE_MIN})", flush=True)
            if total_cm > CAP_CORE_MIN and not capped:
                capped = True
                print(f"*** HARD CAP {CAP_CORE_MIN} core-min CROSSED at "
                      f"{total_cm:.4f}. STOPPING. This is REPORTED to the "
                      f"supervisor, who decides. The cap is NOT extended here.",
                      file=sys.stderr, flush=True)
                for f2 in futs:
                    f2.cancel()
                break

    ledger = dict(root=a.root, wall_s=time.time() - t0,
                  solver_core_min=total_cm, cap_core_min=CAP_CORE_MIN,
                  cap_crossed=capped, cases=done,
                  prereg_commit="3e82e989604e540ea2e9cfbef62e0530a086a98d",
                  grader_blob="f51961435729558dc768d89e429c1818e8ae1da6")
    path = a.ledger or os.path.join(a.root, "..", "F4_CONVERSION_RUN_LEDGER.json")
    with open(path, "w") as fh:
        json.dump(ledger, fh, indent=2)
        fh.flush()
        os.fsync(fh.fileno())
    print(json.dumps({k: v for k, v in ledger.items() if k != "cases"}, indent=2))

    bad = [r for r in done if r["status"] != "COMPLETE"]
    if capped or bad:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
