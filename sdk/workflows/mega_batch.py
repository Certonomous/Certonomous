"""Mega-batch runner — continuous REAL solver evaluations into a durable ledger.

This is the all-night accumulator for the website. It streams an unbounded,
*deterministic* sequence of designs — interleaved OpenFOAM 2D cylinder solves
and VSPAERO vortex-lattice wing polars — through a bounded pool of workers, and
appends every finished evaluation as one JSON line to a durable ledger.

Two properties make it demo-safe:

- **Real only.** Both backends run the actual solvers (OpenFOAM ``simpleFoam``
  behind ``OPENFOAM_RUN_PREFIX``; VSPAERO behind ``OPENVSP_RUN_PREFIX``). Every
  ledger row is labelled ``real-solve``; nothing here is a model surrogate. If a
  solver is unreachable the batch refuses to fabricate — it records the failure.
- **Crash-durable + resumable.** Each design maps deterministically from its
  integer index (``design_for_index``), and every row carries that index. On
  restart the runner reads the ledger, learns which indices are already done,
  and resumes with the next un-attempted index — so an interrupted run picks up
  exactly where it left off without repeating or losing work.

The ledger row shape (one JSON object per line)::

    {"index", "solver", "label", "design", "metrics",
     "wall_seconds", "timestamp", "ok" [, "error"]}

Concurrency is capped (default 4) to honour the machine's compute treaty; each
solve is its own process in its own directory, so the workers never share state.
Case directories are deleted after their metrics are extracted to bound disk use.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import shutil
import sys
import threading
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Make ``chief_engineer`` importable when run as a plain script (sdk/ on path).
_SDK_ROOT = Path(__file__).resolve().parents[1]
if str(_SDK_ROOT) not in sys.path:
    sys.path.insert(0, str(_SDK_ROOT))

from chief_engineer.openfoam import OpenFoamCylinderApi  # noqa: E402
from chief_engineer.vspaero import VspAeroWingApi  # noqa: E402

CYLINDER = "openfoam-cylinder"
WING = "vspaero-wing"
VALVE = "reduced-order"

# Seed offset keeps this sequence stable and distinct from any other sampler.
_SEED_BASE = 90_210


# --------------------------------------------------------------------------
# Deterministic design stream — index -> design
# --------------------------------------------------------------------------

def design_for_index(index: int) -> dict[str, Any]:
    """Map an integer index to a solver + design, deterministically.

    A 3-way interleave (index % 3) holds a balanced mix over a long run:
    cylinder solves, wing polars, and reduced-order valve-cycle evaluations.
    Ranges stay physically sensible: cylinders in the steady-laminar band
    (Re ~10-45, where simpleFoam converges), wings at transport-like aspect
    ratios and sweep, valve opening angles across the physiological range.

    The valve rows are honest reduced-order evaluations (``solver='reduced-order'``),
    NOT solves — a cycle-decomposition orifice screen, three phase points each.
    """
    rng = random.Random(_SEED_BASE + index)
    kind = index % 3
    if kind == 0:
        diameter = round(rng.uniform(0.5, 2.0), 4)
        velocity = round(rng.uniform(0.5, 2.5), 4)
        re_target = rng.uniform(10.0, 45.0)
        viscosity = round(velocity * diameter / re_target, 6)
        viscosity = min(max(viscosity, 0.01), 0.2)
        refinement = round(rng.uniform(0.6, 1.6), 3)
        return {
            "solver": CYLINDER,
            "design": {
                "cylinder_diameter": diameter,
                "inlet_velocity": velocity,
                "kinematic_viscosity": viscosity,
                "mesh_refinement": refinement,
            },
        }
    if kind == 1:
        span = round(rng.uniform(20.0, 70.0), 3)
        aspect = rng.uniform(6.0, 16.0)
        area = round(span * span / aspect, 3)
        sweep = round(rng.uniform(0.0, 35.0), 2)
        taper = round(rng.uniform(0.2, 0.6), 3)
        cl_target = round(rng.uniform(0.4, 0.6), 3)
        return {
            "solver": WING,
            "design": {
                "span": span,
                "area": area,
                "sweep": sweep,
                "taper": taper,
                "cl_target": cl_target,
            },
        }
    opening_angle = round(rng.uniform(35.0, 85.0), 2)
    return {
        "solver": VALVE,
        "design": {"opening_angle_deg": opening_angle},
    }


# --------------------------------------------------------------------------
# Single-task evaluation
# --------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run_cylinder(index: int, design: dict[str, float], work_root: Path) -> dict[str, Any]:
    case_dir = work_root / "cylinder" / f"case-{index:06d}"
    api = OpenFoamCylinderApi(case_dir)
    try:
        raw = api.evaluate(design, ["geometry", "aerodynamics"])
    finally:
        api.close()
    keys = (
        "Cd", "Cl", "Re", "Cd_oscillation", "convergence_residual",
        "converged", "solver_iterations", "cell_count",
    )
    metrics = {k: raw[k] for k in keys if k in raw}
    shutil.rmtree(case_dir, ignore_errors=True)
    return metrics


def _run_wing(index: int, design: dict[str, float], work_root: Path) -> dict[str, Any]:
    api = VspAeroWingApi(work_root / "wing")
    raw = api.evaluate(design)
    matched = raw.get("matched", {}) or {}
    built = raw.get("built", {}) or {}
    cdi = matched.get("cdi")
    cdo = matched.get("cdo_wing")
    cl = matched.get("cl")
    cd_total = None
    if cdi is not None and cdo is not None:
        cd_total = cdi + cdo
    l_over_d = (cl / cd_total) if (cl is not None and cd_total) else None
    metrics = {
        "cl": cl,
        "cdi": cdi,
        "cdo_wing": cdo,
        "cd_total": cd_total,
        "L_D": l_over_d,
        "alpha": matched.get("alpha"),
        "span_efficiency": matched.get("span_efficiency"),
        "extrapolated": matched.get("extrapolated"),
        "built_span": built.get("span"),
        "built_area": built.get("area"),
    }
    case_dir = raw.get("case_dir")
    if case_dir:
        shutil.rmtree(case_dir, ignore_errors=True)
    return metrics


def _run_valve(index: int, design: dict[str, float]) -> dict[str, Any]:
    """Reduced-order valve-cycle evaluation — NOT a solve; labelled as such.

    One opening angle, decomposed into the k=3 systolic phase points, each
    passed through the transparent orifice pressure-loss model, then
    cycle-weighted with a deterministic Monte-Carlo input envelope. This reuses
    the exact ROM the Act 3 valve workflow ships, so the numbers are consistent.
    """
    from workflows import valve_study as vs  # lazy: it edits sys.path on import

    angle = float(design["opening_angle_deg"])
    phases = vs.phase_points()
    area = vs.effective_orifice_area(angle)
    weighted = vs._cycle_weighted_loss(angle, phases)
    mean, two_sigma = vs._mc_envelope(angle, phases)
    alpha = vs.womersley(vs.ROOT_RADIUS)
    return {
        "cycle_weighted_loss_Pa": round(weighted, 3),
        "loss_mean_Pa": round(mean, 3),
        "loss_envelope_2sigma_Pa": round(two_sigma, 3),
        "orifice_area_mm2": round(area * 1e6, 2),
        "womersley_alpha": round(alpha, 3),
        "feasible": area >= vs.MIN_ORIFICE_AREA,
        "phase_points": len(phases),
    }


def run_task(index: int, work_root: Path) -> dict[str, Any]:
    """Evaluate one design; never raises — failures come back as ok=False rows."""
    spec = design_for_index(index)
    solver = spec["solver"]
    design = spec["design"]
    # Cylinder and wing are real solves; the valve row is an honest
    # reduced-order (ROM) evaluation — labelled distinctly, never as a solve.
    label = "reduced-order-eval" if solver == VALVE else "real-solve"
    start = time.time()
    record: dict[str, Any] = {
        "index": index,
        "solver": solver,
        "label": label,
        "design": design,
        "timestamp": _now_iso(),
    }
    try:
        if solver == CYLINDER:
            metrics = _run_cylinder(index, design, work_root)
        elif solver == WING:
            metrics = _run_wing(index, design, work_root)
        else:
            metrics = _run_valve(index, design)
        record["metrics"] = metrics
        record["ok"] = True
    except Exception as exc:  # a poison design must not sink the batch
        record["metrics"] = {}
        record["ok"] = False
        record["error"] = f"{type(exc).__name__}: {exc}"
    record["wall_seconds"] = round(time.time() - start, 3)
    return record


# --------------------------------------------------------------------------
# Ledger I/O (durable append + resume)
# --------------------------------------------------------------------------

_LEDGER_LOCK = threading.Lock()


def append_ledger(ledger_path: Path, record: dict[str, Any]) -> None:
    """Append one record as a JSON line, flushed and fsync'd for crash safety."""
    line = json.dumps(record, ensure_ascii=False)
    with _LEDGER_LOCK:
        with ledger_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
            handle.flush()
            os.fsync(handle.fileno())


def load_done_indices(ledger_path: Path) -> set[int]:
    """Indices already attempted (ok or not) — the resume set."""
    done: set[int] = set()
    if not ledger_path.exists():
        return done
    for line in ledger_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
            done.add(int(record["index"]))
        except Exception:
            continue
    return done


# --------------------------------------------------------------------------
# Learning pass — every batch is a learning opportunity
# --------------------------------------------------------------------------

# Refresh the distilled learned study after this many completions in-session,
# and always once more when the session ends. Cheap (one ledger read), and a
# failure here must never sink the batch itself.
LEARN_EVERY = 500


def distill_learning(ledger_path: Path, log=print) -> None:
    """Distill the ledger into the learned study; never raises."""
    try:
        from chief_engineer.ledger_learning import distill_to_file
        study = distill_to_file(ledger_path)
        log(
            f"[mega-batch] learning refreshed: "
            f"{study['provenance']['row_count']} ledger rows distilled"
        )
    except Exception as exc:  # learning is best-effort, the batch is not
        log(f"[mega-batch] learning pass skipped: {type(exc).__name__}: {exc}")


# --------------------------------------------------------------------------
# Resource guards
# --------------------------------------------------------------------------
#
# Added after the 2026-07-27 outage. The instance went unreachable at ~05:12:56
# UTC while two DAFoam adjoint containers and this batch shared 30 GB of RAM
# with no swap; the last sysstat sample (05:10:03) recorded 460 MB free and
# committed memory at 112.90% of RAM. There was no OOM kill and no disk
# exhaustion in the logs -- the box livelocked in reclaim before the OOM killer
# could act. These guards stop the batch cleanly while headroom still exists,
# rather than letting it participate in a second such livelock.

RESOURCE_CHECK_SECONDS = 10.0


def free_disk_gb(path: Path) -> float:
    """GiB free on the filesystem holding ``path``."""
    return shutil.disk_usage(path).free / (1024 ** 3)


def available_mem_gb() -> float:
    """GiB of MemAvailable, the kernel's own estimate of allocatable memory.

    Returns ``inf`` if /proc/meminfo is unreadable, so a parsing problem can
    never stop a healthy batch.
    """
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemAvailable:"):
                return float(line.split()[1]) / (1024 ** 2)
    except Exception:
        pass
    return float("inf")


# --------------------------------------------------------------------------
# Continuous run loop
# --------------------------------------------------------------------------

def run_batch(
    ledger_path: Path,
    work_root: Path,
    *,
    workers: int = 4,
    max_tasks: int | None = None,
    max_seconds: float | None = None,
    stop_file: Path | None = None,
    min_free_disk_gb: float = 20.0,
    min_avail_mem_gb: float = 2.0,
    log=print,
) -> dict[str, int]:
    """Stream designs through ``workers`` slots, appending each result.

    Stops when any of the bounds is hit: ``max_tasks`` completed *this session*,
    ``max_seconds`` elapsed, ``stop_file`` appears, free disk falls below
    ``min_free_disk_gb``, or available memory falls below ``min_avail_mem_gb``.
    Resumes from the ledger.
    """
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    (work_root / "cylinder").mkdir(parents=True, exist_ok=True)
    (work_root / "wing").mkdir(parents=True, exist_ok=True)

    done = load_done_indices(ledger_path)
    log(f"[mega-batch] resuming: {len(done)} indices already in ledger")
    log(
        f"[mega-batch] baseline: workers={workers} "
        f"free_disk={free_disk_gb(work_root):.1f} GB "
        f"avail_mem={available_mem_gb():.1f} GB; "
        f"guards stop at disk<{min_free_disk_gb:.1f} GB, mem<{min_avail_mem_gb:.1f} GB"
    )

    start = time.time()
    next_index = 0
    submitted_this_session = 0
    completed_this_session = 0
    stats = {"ok": 0, "failed": 0, CYLINDER: 0, WING: 0}

    # Resource guards are sampled at most once every RESOURCE_CHECK_SECONDS so
    # the tight submit loop does not spam syscalls. ``guard_trip`` latches: once
    # a guard fires the batch stops for good this session and the reason is
    # reported at the end, so a stop is never silent.
    guard_state = {"last_check": 0.0, "trip": None}

    def resource_guard_tripped() -> str | None:
        if guard_state["trip"] is not None:
            return guard_state["trip"]
        now = time.time()
        if now - guard_state["last_check"] < RESOURCE_CHECK_SECONDS:
            return None
        guard_state["last_check"] = now
        disk = free_disk_gb(work_root)
        if disk < min_free_disk_gb:
            guard_state["trip"] = (
                f"free disk {disk:.1f} GB below the {min_free_disk_gb:.1f} GB floor"
            )
            log(f"[mega-batch] RESOURCE GUARD: {guard_state['trip']} -- draining and stopping")
            return guard_state["trip"]
        mem = available_mem_gb()
        if mem < min_avail_mem_gb:
            guard_state["trip"] = (
                f"available memory {mem:.1f} GB below the {min_avail_mem_gb:.1f} GB floor"
            )
            log(f"[mega-batch] RESOURCE GUARD: {guard_state['trip']} -- draining and stopping")
            return guard_state["trip"]
        return None

    def should_stop() -> bool:
        if stop_file is not None and stop_file.exists():
            return True
        if max_seconds is not None and (time.time() - start) >= max_seconds:
            return True
        if max_tasks is not None and submitted_this_session >= max_tasks:
            return True
        tripped = resource_guard_tripped()
        if tripped is not None:
            return True
        return False

    def claim_next() -> int:
        nonlocal next_index
        while next_index in done:
            next_index += 1
        index = next_index
        next_index += 1
        done.add(index)
        return index

    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        inflight: dict[Any, int] = {}
        while True:
            while len(inflight) < workers and not should_stop():
                index = claim_next()
                inflight[pool.submit(run_task, index, work_root)] = index
                submitted_this_session += 1
            if not inflight:
                break
            finished, _ = wait(inflight, timeout=5.0, return_when=FIRST_COMPLETED)
            for future in finished:
                index = inflight.pop(future)
                record = future.result()
                append_ledger(ledger_path, record)
                completed_this_session += 1
                stats[record["solver"]] = stats.get(record["solver"], 0) + 1
                if record.get("ok"):
                    stats["ok"] += 1
                    log(
                        f"[mega-batch] #{index} {record['solver']} ok "
                        f"{record['wall_seconds']}s "
                        f"(session {completed_this_session})"
                    )
                else:
                    stats["failed"] += 1
                    log(f"[mega-batch] #{index} {record['solver']} FAILED: {record.get('error')}")
                if completed_this_session % LEARN_EVERY == 0:
                    distill_learning(ledger_path, log=log)
            if should_stop() and not inflight:
                break

    # Every batch is a learning opportunity: distill the ledger into the
    # learned study at session end (best-effort, never fatal).
    distill_learning(ledger_path, log=log)

    total = len(load_done_indices(ledger_path))
    reason = guard_state["trip"]
    log(
        f"[mega-batch] session done: completed {completed_this_session} "
        f"(ok {stats['ok']}, failed {stats['failed']}); ledger total {total}"
        + (f"; STOPPED BY RESOURCE GUARD: {reason}" if reason else "")
    )
    stats["ledger_total"] = total
    stats["session_completed"] = completed_this_session
    stats["guard_trip"] = reason
    return stats


# --------------------------------------------------------------------------
# Single-instance lock
# --------------------------------------------------------------------------
#
# Added 2026-07-27 after an audit of the ledger found 55 duplicated indices in
# 186,838-186,893, every pair written between 05:11:15 and 05:12:52 on
# 2026-07-27 -- BEFORE the outage, not across the restart. ``claim_next`` runs
# on one thread and adds to ``done`` the moment it hands an index out, so a
# single session physically cannot emit the same index twice. Two sessions can.
# ``runner.pid`` was dated 05:11 and held PID 2303296, so a second runner was
# launched while the 03:21 runner was still alive, and both appended for the
# ~100 s until the box died.
#
# This is the same failure mode as the historical 1,168-duplicate episode in
# 59,899-61,068. The ledger is append-only and the distiller de-duplicates
# prefer-ok, so no measurement is lost -- but the distinct-evaluation count is
# corrupted every time it happens. Refusing the second launch is the fix.

def _pid_is_live_runner(pid: int) -> bool:
    """True if ``pid`` is alive AND looks like another mega-batch runner.

    Checked against the cmdline so a recycled PID belonging to some unrelated
    process can never block a legitimate start.
    """
    try:
        cmdline = Path(f"/proc/{pid}/cmdline").read_bytes().decode("utf-8", "replace")
    except (FileNotFoundError, ProcessLookupError, PermissionError):
        return False
    return "mega_batch" in cmdline


def acquire_runner_lock(pid_file: Path, *, force: bool = False, log=print) -> bool:
    """Claim ``pid_file`` for this process. False means refuse to start."""
    if pid_file.exists():
        try:
            existing = int(pid_file.read_text().strip())
        except (ValueError, OSError):
            existing = None
        if existing is not None and existing != os.getpid() and _pid_is_live_runner(existing):
            if not force:
                log(
                    f"[mega-batch] REFUSING TO START: another runner is live at PID "
                    f"{existing} (per {pid_file}). Two concurrent runners duplicate "
                    f"ledger indices -- this exact mistake corrupted 55 rows on "
                    f"2026-07-27. Stop it first, or pass --force if you are certain."
                )
                return False
            log(f"[mega-batch] --force given; starting alongside live PID {existing}")
    pid_file.parent.mkdir(parents=True, exist_ok=True)
    pid_file.write_text(str(os.getpid()))
    return True


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _default_paths() -> tuple[Path, Path]:
    # demo-output/website/mega-batch/ledger.jsonl relative to repo root.
    repo_root = _SDK_ROOT.parent
    ledger = repo_root / "demo-output" / "website" / "mega-batch" / "ledger.jsonl"
    work_root = repo_root / "demo-output" / "website" / "mega-batch" / "work"
    return ledger, work_root


def main(argv: list[str] | None = None) -> int:
    ledger_default, work_default = _default_paths()
    parser = argparse.ArgumentParser(description="Continuous real-solver mega-batch.")
    parser.add_argument("--ledger", type=Path, default=ledger_default)
    parser.add_argument("--work-root", type=Path, default=work_default)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--max-tasks", type=int, default=None,
                        help="stop after N tasks submitted this session")
    parser.add_argument("--max-seconds", type=float, default=None,
                        help="stop after N seconds of wall time")
    parser.add_argument("--stop-file", type=Path, default=None,
                        help="stop gracefully when this file appears")
    parser.add_argument("--min-free-disk-gb", type=float, default=20.0,
                        help="stop gracefully when free disk falls below this (GiB)")
    parser.add_argument("--min-avail-mem-gb", type=float, default=2.0,
                        help="stop gracefully when available memory falls below this (GiB)")
    parser.add_argument("--pid-file", type=Path, default=None,
                        help="single-instance lock file (default: runner.pid beside the ledger)")
    parser.add_argument("--force", action="store_true",
                        help="start even if another live runner holds the pid file")
    args = parser.parse_args(argv)

    pid_file = args.pid_file
    if pid_file is None:
        pid_file = args.ledger.parent / "runner.pid"
    if not acquire_runner_lock(pid_file.resolve(), force=args.force):
        return 1

    stop_file = args.stop_file
    if stop_file is None:
        stop_file = args.ledger.parent / "STOP"

    run_batch(
        args.ledger.resolve(),
        args.work_root.resolve(),
        workers=args.workers,
        max_tasks=args.max_tasks,
        max_seconds=args.max_seconds,
        stop_file=stop_file,
        min_free_disk_gb=args.min_free_disk_gb,
        min_avail_mem_gb=args.min_avail_mem_gb,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
