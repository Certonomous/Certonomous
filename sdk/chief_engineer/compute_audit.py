"""Compute audit: what capacity exists right now, and does the sweep fit?

The Chief Engineer calls :func:`audit` *before* planning any fan-out.  The
audit is a real measurement of the machine that will run the solvers — the
WSL compute node here — not a configuration constant:

* physical cores and 1-minute load average (``nproc``, ``/proc/loadavg``)
* available memory (``/proc/meminfo`` MemAvailable, which accounts for
  reclaimable cache — the honest number for "can I start N more jobs")
* other jobs already running: live OpenFOAM solvers plus any deliberately
  scripted load (``certonomous-load``, see ``scripts/make_busy.sh``)

The verdict answers one question: **can the requested fan-out run in one go?**
A NO is not a failure — it routes the mission to the Chief Researcher, who
selects the most informative subset to run at full fidelity while the rest is
covered by a reduced-order ensemble.
"""

from __future__ import annotations

import math
import re
import subprocess
from dataclasses import dataclass, field
from typing import Any

WSL = ["wsl", "-d", "Ubuntu", "-u", "foam", "--"]
SOLVER_PATTERN = "simpleFoam|snappyHexMesh|potentialFoam|blockMesh|interFoam|pimpleFoam"
LOAD_MARKER = "certonomous-load"

# Cores held back for the orchestrator, the monitor, and the OS itself.
RESERVED_CORES = 2
# Per-worker memory floor for the 2D cases the demo runs; motorBike-scale
# meshes declare their own requirement through ``memory_per_worker_mb``.
DEFAULT_MEMORY_PER_WORKER_MB = 512


@dataclass
class ComputeAudit:
    cores_total: int
    cores_reserved: int
    load_1min: float
    memory_total_mb: int
    memory_available_mb: int
    other_jobs: int
    solver_jobs: int
    scripted_load_jobs: int
    requested_workers: int
    memory_per_worker_mb: int
    cores_free: int
    workers_by_cores: int
    workers_by_memory: int
    capacity: int
    fits: bool
    reason: str
    error: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {key: getattr(self, key) for key in self.__dataclass_fields__}

    def panel(self) -> dict[str, Any]:
        """Compact payload for the control-room compute panel."""
        return {
            "verdict": "FITS" if self.fits else "CONSTRAINED",
            "requested": self.requested_workers,
            "capacity": self.capacity,
            "cores": f"{self.cores_free}/{self.cores_total} free",
            "memory": f"{self.memory_available_mb // 1024:.0f}/"
                      f"{self.memory_total_mb // 1024:.0f} GB free",
            "other_jobs": self.other_jobs,
            "load": round(self.load_1min, 2),
            "reason": self.reason,
        }

    def headline(self) -> str:
        verdict = "YES" if self.fits else "NO"
        return (
            f"Compute audit, {verdict}: requested {self.requested_workers} "
            f"parallel workers, capacity {self.capacity} "
            f"({self.cores_free}/{self.cores_total} cores free, "
            f"{self.memory_available_mb // 1024:.0f} GB available, "
            f"{self.other_jobs} other job(s) running). {self.reason}"
        )


def _probe() -> dict[str, Any]:
    """One round trip to the compute node for every quantity we need."""
    # Every quantity is emitted with an explicit label: positional parsing
    # breaks the moment a value happens to look like another (nproc's "14" is
    # indistinguishable from a job count).  The bracket trick in the pgrep
    # patterns stops pgrep -f from matching the probe's own command line.
    bracketed = f"[{LOAD_MARKER[0]}]{LOAD_MARKER[1:]}"
    command = (
        "echo CORES=$(nproc); "
        "echo MEMTOTAL=$(awk '/^MemTotal:/{print $2}' /proc/meminfo); "
        "echo MEMAVAIL=$(awk '/^MemAvailable:/{print $2}' /proc/meminfo); "
        "echo LOAD=$(cut -d' ' -f1 /proc/loadavg); "
        f"echo SOLVERS=$(pgrep -c -x '{SOLVER_PATTERN}' || true); "
        f"echo SCRIPTED=$(pgrep -c -f '{bracketed}' || true)"
    )
    completed = subprocess.run(
        [*WSL, "bash", "-c", command], capture_output=True, text=True, timeout=60,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"compute probe failed: {completed.stderr.strip()[:200]}")
    text = completed.stdout.replace("\x00", "")

    def _int(label: str, default: int = 0) -> int:
        match = re.search(rf"{label}=(\d+)", text)
        return int(match.group(1)) if match else default

    def _float(label: str, default: float = 0.0) -> float:
        match = re.search(rf"{label}=([\d.]+)", text)
        return float(match.group(1)) if match else default

    cores = max(1, _int("CORES", 1))
    memory_total = _int("MEMTOTAL") // 1024
    memory_available = _int("MEMAVAIL") // 1024
    load = _float("LOAD")
    solver_jobs = _int("SOLVERS")
    scripted = _int("SCRIPTED")
    return {
        "cores": cores,
        "memory_total_mb": memory_total,
        "memory_available_mb": memory_available,
        "load": load,
        "solver_jobs": solver_jobs,
        "scripted_load_jobs": scripted,
    }


def audit(requested_workers: int, *,
          memory_per_worker_mb: int = DEFAULT_MEMORY_PER_WORKER_MB,
          reserved_cores: int = RESERVED_CORES) -> ComputeAudit:
    """Measure current capacity and decide whether the fan-out fits in one go."""
    requested = max(1, int(requested_workers))
    try:
        probe = _probe()
    except Exception as exc:  # the audit must never crash a mission
        return ComputeAudit(
            cores_total=0, cores_reserved=reserved_cores, load_1min=0.0,
            memory_total_mb=0, memory_available_mb=0, other_jobs=0,
            solver_jobs=0, scripted_load_jobs=0, requested_workers=requested,
            memory_per_worker_mb=memory_per_worker_mb, cores_free=0,
            workers_by_cores=0, workers_by_memory=0, capacity=1, fits=False,
            reason="compute node unreachable; assuming minimal capacity",
            error=f"{type(exc).__name__}: {exc}",
        )

    cores = probe["cores"]
    other_jobs = probe["solver_jobs"] + probe["scripted_load_jobs"]
    usable = max(0, cores - reserved_cores)
    # Each running job is assumed to hold a core; the load average is a
    # cross-check so a busy machine cannot look idle through process counting
    # alone (or vice versa for short-lived jobs).
    occupied = max(other_jobs, int(math.floor(probe["load"])) if probe["load"] > 1.5 else 0)
    cores_free = max(0, usable - occupied)
    workers_by_memory = probe["memory_available_mb"] // max(1, memory_per_worker_mb)
    capacity = max(1, min(cores_free, workers_by_memory))
    fits = cores_free >= requested and workers_by_memory >= requested

    if fits:
        reason = "Full fan-out can run in one wave."
    elif cores_free < requested and workers_by_memory < requested:
        reason = (f"Both cores and memory are short: room for {capacity} of "
                  f"{requested}. Route to staged strategy.")
    elif cores_free < requested:
        reason = (f"Core-limited: {cores_free} free vs {requested} requested "
                  f"({other_jobs} other job(s) holding cores). Route to staged strategy.")
    else:
        reason = (f"Memory-limited: room for {workers_by_memory} workers at "
                  f"{memory_per_worker_mb} MB each. Route to staged strategy.")

    return ComputeAudit(
        cores_total=cores, cores_reserved=reserved_cores, load_1min=probe["load"],
        memory_total_mb=probe["memory_total_mb"],
        memory_available_mb=probe["memory_available_mb"],
        other_jobs=other_jobs, solver_jobs=probe["solver_jobs"],
        scripted_load_jobs=probe["scripted_load_jobs"],
        requested_workers=requested, memory_per_worker_mb=memory_per_worker_mb,
        cores_free=cores_free, workers_by_cores=cores_free,
        workers_by_memory=workers_by_memory, capacity=capacity, fits=fits,
        reason=reason,
    )
