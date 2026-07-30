"""The worker fleet: provision isolated workers, run tasks, survive a kill.

A fleet turns a list of :class:`WorkerTask` into evaluations by handing each
concurrent slot its own provisioned worker and a share of the work. The provider
seam (``VmProvider``) lets the same fleet run against local in-process workers in
development and against real remote workers in production without the caller
changing.

It also carries the on-camera resilience beat: ``scripts/kill_worker.sh`` drops
a marker for a slot, the running worker notices it on its next task and dies,
and the fleet reports the loss, provisions a fresh worker, and reruns that slot's
work so the mission still finishes with the correct numbers.
"""

from __future__ import annotations

import os
import tempfile
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock
from typing import Any, Callable, Protocol, Sequence

from .api import SimulationApi
from .models import Candidate, Evaluation


# --------------------------------------------------------------------------
# Sabotage markers — the "kill a worker on camera" beat
# --------------------------------------------------------------------------

def _sabotage_dir() -> Path:
    # Repo-relative by default so the kill script and the running server agree on
    # the marker location with no environment setup on camera.
    default = Path(__file__).resolve().parents[2] / "mission-output" / ".sabotage"
    return Path(os.environ.get("CERTONOMOUS_SABOTAGE_DIR", str(default)))


def _sabotage_marker(index: int) -> Path:
    return _sabotage_dir() / f"kill-worker-{index}"


def worker_sabotaged(index: int) -> bool:
    """True if a kill marker has been dropped for the given worker slot."""
    try:
        return _sabotage_marker(index).exists()
    except OSError:
        return False


def clear_sabotage(index: int) -> None:
    """Remove a slot's kill marker (called by the recovery wave)."""
    try:
        _sabotage_marker(index).unlink(missing_ok=True)
    except OSError:
        pass


class WorkerKilled(RuntimeError):
    """Raised inside a slot when its kill marker is seen; the fleet recovers."""

    def __init__(self, index: int):
        super().__init__(f"worker {index} was killed mid-mission")
        self.index = index


# --------------------------------------------------------------------------
# Provisioning seam
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class VmSpec:
    worker_id: str
    specialist: str
    analyses: tuple[str, ...]
    image: str = "certonomous-worker:local"


@dataclass
class VmHandle:
    id: str
    spec: VmSpec
    workspace: Path
    state: str = "provisioned"
    metadata: dict[str, str] = field(default_factory=dict)


class VmProvider(Protocol):
    def provision(self, spec: VmSpec) -> VmHandle:
        ...

    def release(self, handle: VmHandle) -> None:
        ...


class LocalVmProvider:
    """Provision in-process workers, each with its own workspace and identity.

    This is the development provider; a production one implements the same two
    methods against containers or VMs without the fleet changing.
    """

    def __init__(self, root: str | None = None):
        self.root = Path(root) if root else Path(
            tempfile.mkdtemp(prefix="certonomous-fleet-"))
        self.root.mkdir(parents=True, exist_ok=True)
        self.provisioned: list[VmHandle] = []
        self.released: list[VmHandle] = []
        self._lock = Lock()

    def provision(self, spec: VmSpec) -> VmHandle:
        handle = VmHandle(
            id=f"vm-{spec.worker_id}-{uuid.uuid4().hex[:8]}",
            spec=spec,
            workspace=self.root / spec.worker_id,
        )
        handle.workspace.mkdir(parents=True, exist_ok=True)
        with self._lock:
            self.provisioned.append(handle)
        return handle

    def release(self, handle: VmHandle) -> None:
        handle.state = "released"
        with self._lock:
            self.released.append(handle)


# --------------------------------------------------------------------------
# The fleet
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class WorkerTask:
    candidate: Candidate
    specialist: str
    analyses: tuple[str, ...]


ApiFactory = Callable[[VmHandle], SimulationApi]
FleetEventSink = Callable[[str, dict], None]


class ApiFleet:
    """Run a batch of tasks across provisioned workers, recovering from a kill."""

    def __init__(self, provider: VmProvider, api_factory: ApiFactory,
                 max_workers: int = 64, event_sink: FleetEventSink | None = None):
        self.provider = provider
        self.api_factory = api_factory
        self.max_workers = max(1, max_workers)
        self.event_sink = event_sink

    def evaluate(self, tasks: Sequence[WorkerTask], plan: Any) -> list[Evaluation]:
        """Evaluate every task; ``plan.worker_count`` caps the concurrency."""
        if not tasks:
            return []
        slots = min(len(tasks), int(getattr(plan, "worker_count", len(tasks))),
                    self.max_workers)
        handles = [self._open_slot(index, tasks[index]) for index in range(slots)]
        # Round-robin the tasks across slots so each worker owns a contiguous share.
        buckets = [list(tasks[index::slots]) for index in range(slots)]

        results: list[Evaluation] = []
        killed: list[int] = []
        try:
            with ThreadPoolExecutor(max_workers=slots,
                                    thread_name_prefix="fleet-worker") as pool:
                pending = {pool.submit(self._run_slot, handles[i], buckets[i], i): i
                           for i in range(slots)}
                for future in as_completed(pending):
                    slot = pending[future]
                    try:
                        results.extend(future.result())
                    except WorkerKilled:
                        self._emit("worker.killed", {
                            "worker_id": handles[slot].id,
                            "worker_index": slot,
                            "pending": len(buckets[slot]),
                            "detail": f"worker-{slot:02d} stopped responding, its "
                                      f"{len(buckets[slot])} task(s) will be reprovisioned"})
                        killed.append(slot)
        finally:
            for handle in handles:
                self.provider.release(handle)
                self._emit("worker.released", {"worker_id": handle.id})

        results.extend(self._recover(killed, buckets))
        return sorted(results, key=lambda item: item.candidate_id)

    def _open_slot(self, index: int, first_task: WorkerTask) -> VmHandle:
        handle = self.provider.provision(
            VmSpec(f"worker-{index:02d}", first_task.specialist, first_task.analyses))
        self._emit("worker.provisioned", {
            "worker_id": handle.id,
            "specialist": first_task.specialist,
            "workspace": str(handle.workspace),
            "runtime": handle.metadata.get("runtime", "local-process"),
            "container": handle.metadata.get("container"),
            "image": handle.metadata.get("image"),
        })
        return handle

    def _recover(self, killed: list[int],
                 buckets: list[list[WorkerTask]]) -> list[Evaluation]:
        """Reprovision each killed slot and rerun its work — correct numbers, late."""
        recovered: list[Evaluation] = []
        for slot in killed:
            clear_sabotage(slot)
            bucket = buckets[slot]
            if not bucket:
                continue
            handle = self.provider.provision(
                VmSpec(f"worker-{slot:02d}r", bucket[0].specialist, bucket[0].analyses))
            self._emit("worker.reprovisioned", {
                "worker_id": handle.id,
                "worker_index": slot,
                "detail": f"a fresh worker took over slot {slot:02d}; rerunning its work"})
            try:
                recovered.extend(self._run_slot(handle, bucket, slot, allow_kill=False))
            finally:
                self.provider.release(handle)
                self._emit("worker.released", {"worker_id": handle.id})
        return recovered

    def _run_slot(self, handle: VmHandle, tasks: Sequence[WorkerTask],
                  index: int = -1, *, allow_kill: bool = True) -> list[Evaluation]:
        done: list[Evaluation] = []
        for task in tasks:
            # A mid-mission kill is caught before the next unit of work begins.
            if allow_kill and index >= 0 and worker_sabotaged(index):
                raise WorkerKilled(index)
            done.append(self._run_one(task, handle))
        return done

    def _run_one(self, task: WorkerTask, handle: VmHandle) -> Evaluation:
        started = time.monotonic()
        api: SimulationApi | None = None
        try:
            handle.metadata["candidate_id"] = task.candidate.id
            self._emit("agent.started", {
                "agent_id": task.candidate.id,
                "worker_id": handle.id,
                "specialist": task.specialist,
                "analyses": list(task.analyses),
                "rationale": task.candidate.rationale,
            })
            api = self.api_factory(handle)
            self._wire_progress(api, task, handle)
            metrics = {k: float(v) for k, v in dict(
                api.evaluate(task.candidate.design, task.analyses)).items()}
            reader = getattr(api, "artifacts", None)
            artifacts = list(reader()) if callable(reader) else []
            result = Evaluation(
                candidate_id=task.candidate.id,
                worker_id=handle.id,
                metrics=metrics,
                elapsed_s=round(time.monotonic() - started, 4),
                artifacts=artifacts,
            )
            self._emit("agent.completed", {
                "agent_id": task.candidate.id,
                "worker_id": handle.id,
                "design": {k: float(v) for k, v in dict(task.candidate.design).items()},
                "metrics": result.metrics,
                "elapsed_s": result.elapsed_s,
                "artifacts": result.artifacts,
            })
            return result
        except Exception as exc:
            result = Evaluation(
                candidate_id=task.candidate.id,
                worker_id=handle.id,
                elapsed_s=round(time.monotonic() - started, 4),
                error=f"{type(exc).__name__}: {exc}",
            )
            self._emit("agent.failed", {
                "agent_id": task.candidate.id,
                "worker_id": handle.id,
                "error": result.error,
            })
            return result
        finally:
            if api is not None:
                api.close()

    def _wire_progress(self, api: SimulationApi, task: WorkerTask,
                       handle: VmHandle) -> None:
        setter = getattr(api, "set_progress_sink", None)
        if callable(setter):
            setter(lambda payload: self._emit("agent.progress", {
                **dict(payload),
                "agent_id": task.candidate.id,
                "worker_id": handle.id,
            }))

    def _emit(self, event: str, payload: dict) -> None:
        if self.event_sink:
            self.event_sink(event, payload)
