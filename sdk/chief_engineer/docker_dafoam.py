"""The compressible transonic backend: DAFoam's DARhoSimpleCFoam via Docker.

Acts 8 and 9 (the ONERA M6 wing and the CRM wing) are transonic, compressible
bodies -- outside what :class:`chief_engineer.head_engineer.HeadEngineer`
solves (native incompressible ``simpleFoam``, meshed by ``snappyHexMesh`` off
an STL). Their validated evidence came from the DAFoam tutorial's own case
recipe (a pre-built CGNS surface mesh, ``pyHyp`` volume extrusion,
``DARhoSimpleCFoam``) run inside the ``dafoam/opt-packages`` container. This
module runs that exact recipe again, unmodified, so the acts reproduce the
same validated physics rather than a different, unvalidated pipeline built to
fit the incompressible engine.

Mirrors :class:`HeadEngineer`'s mesh-cache / solve-cache discipline: a mesh is
cached by case name (the topology only), a finished solve is cached by case
name plus cell count plus iteration budget (the force history and final
fields). ``CERTONOMOUS_MESH_CACHE=0`` / ``CERTONOMOUS_SOLVER_CACHE=0`` force a
fresh build exactly as they do for the native engine.
"""
from __future__ import annotations

import os
import re
import secrets
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

DOCKER_IMAGE = "dafoam/opt-packages:latest"
RUN_ROOT = Path.home() / "certonomous-runs"
MESH_CACHE_ROOT = RUN_ROOT / ".mesh-cache"
SOLVE_CACHE_ROOT = RUN_ROOT / ".solve-cache"
MOUNT_POINT = "/home/dafoamuser/mount/case"
LOAD_ENV = "source /home/dafoamuser/dafoam/loadDAFoam.sh"
DEFAULT_MEM_GB = 12
DEFAULT_RANKS = 4
MIN_MEMAVAILABLE_GB = 6.0


def docker_available() -> bool:
    if not shutil.which("docker"):
        return False
    try:
        result = subprocess.run(["sudo", "-n", "docker", "info"],
                                capture_output=True, timeout=15)
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def mem_available_gb() -> float:
    try:
        text = Path("/proc/meminfo").read_text()
        match = re.search(r"MemAvailable:\s+(\d+)\s+kB", text)
        return (int(match.group(1)) / 1048576.0) if match else 99.0
    except OSError:
        return 99.0


def wait_for_headroom(*, floor_gb: float = MIN_MEMAVAILABLE_GB,
                      poll_seconds: float = 15.0, max_wait_seconds: float = 1800.0,
                      narrate: Callable[[str], None] | None = None) -> float:
    """Block until MemAvailable clears the floor before a heavy stage.

    Checked, never assumed: every heavy Docker stage (mesh generation, the
    primal solve) calls this first. Returns the headroom actually measured.
    """
    waited = 0.0
    available = mem_available_gb()
    while available < floor_gb and waited < max_wait_seconds:
        if narrate:
            narrate(f"• MemAvailable {available:.1f} GB, below the "
                    f"{floor_gb:.0f} GB floor; waiting before the heavy stage.")
        time.sleep(poll_seconds)
        waited += poll_seconds
        available = mem_available_gb()
    return available


@dataclass
class DockerStepResult:
    name: str
    status: int
    seconds: float
    log_path: str


class DockerDAFoamEngineer:
    """Stage, mesh, and solve one DAFoam tutorial case, monitored, cached."""

    def __init__(self, case_name: str, out_root: str | os.PathLike[str],
                tutorial_source: str | os.PathLike[str], *,
                mem_gb: int = DEFAULT_MEM_GB, ranks: int = DEFAULT_RANKS,
                on_event: Callable[[str, dict], None] | None = None):
        self.case_name = case_name
        self.tutorial_source = Path(tutorial_source)
        self.remote_case = RUN_ROOT / f"{case_name}-{secrets.token_hex(3)}"
        self.out_root = Path(out_root) / case_name
        self.out_root.mkdir(parents=True, exist_ok=True)
        self.mem_gb = mem_gb
        self.ranks = min(DEFAULT_RANKS, max(1, ranks))
        self.on_event = on_event
        self.steps: list[DockerStepResult] = []
        self._cached_cell_count: str | None = None

    def _emit(self, event: str, payload: dict) -> None:
        if self.on_event:
            self.on_event(event, payload)

    # -- infrastructure -----------------------------------------------------

    def stage_case(self) -> None:
        RUN_ROOT.mkdir(parents=True, exist_ok=True)
        if self.remote_case.exists():
            shutil.rmtree(self.remote_case)
        shutil.copytree(self.tutorial_source, self.remote_case)
        self._assert_case_code_vetted()

    def _assert_case_code_vetted(self) -> None:
        """The same trust boundary HeadEngineer.stage_case enforces.

        The container is not a sandbox for this purpose. It runs as root on a
        bind mount of the case directory with ``--network=host``, and its
        OpenFOAM also reports ``allowSystemOperations : Allowing`` (visible at
        the head of every archived DAFoam log, e.g.
        ``demo-output/website/dafoam/probe_baseline_run1.log`` line 33). So a
        case carrying its own C++ compiles and runs it there too, with the host
        network and write access to the mounted directory.
        """
        from .head_engineer import CASE_CODE_PATTERN, vetted_case_reason
        pattern = CASE_CODE_PATTERN
        carriers: list[str] = []
        for path in sorted(self.remote_case.rglob("*")):
            if not path.is_file():
                continue
            try:
                text = path.read_text(errors="ignore")
            except OSError:
                continue
            if pattern.search(text):
                carriers.append(path.name)
        if not carriers:
            return
        if vetted_case_reason(str(self.tutorial_source)):
            return
        raise RuntimeError(
            f"refusing to run {str(self.tutorial_source)!r} in the DAFoam "
            f"container: it carries case-supplied executable code "
            f"({', '.join(carriers[:8])}"
            f"{', ...' if len(carriers) > 8 else ''}) and the container runs "
            "OpenFOAM with allowSystemOperations enabled, as root, on a bind "
            "mount of this directory with --network=host. A case from an "
            "external source must not run with system operations enabled "
            "(Verification Charter section 13). Review it and add it to "
            "chief_engineer.head_engineer.VETTED_SYSTEM_OPERATION_CASES with "
            "the reason.")

    def run(self, command: str, *, name: str, timeout: float = 3600.0,
           mem_gb: int | None = None) -> DockerStepResult:
        """Run one command inside the container, case dir bind-mounted, the
        OpenFOAM/DAFoam/pyHyp/cgns_utils environment sourced first."""
        mem_gb = mem_gb or self.mem_gb
        log_path = self.out_root / f"log.{name}"
        # Root, not dafoamuser: the bind-mounted case directory is owned by
        # the host user (uid 1000), dafoamuser inside the container is a
        # different uid (1002) with no write access to it, and root is how
        # this exact case family was run before (matches the ownership left
        # on disk by the prior validated runs). loadDAFoam.sh is sourced
        # explicitly by path rather than relied on from a login shell.
        docker_cmd = [
            "sudo", "docker", "run", "--rm", "--network=host",
            f"--memory={mem_gb}g",
            "-v", f"{self.remote_case}:{MOUNT_POINT}",
            "-w", MOUNT_POINT, DOCKER_IMAGE,
            "bash", "-c", f"{LOAD_ENV} && {command}",
        ]
        self._emit("step.started", {"step": name})
        start = time.monotonic()
        result = subprocess.run(docker_cmd, capture_output=True, text=True,
                                errors="replace", timeout=timeout)
        seconds = round(time.monotonic() - start, 1)
        log_path.write_text((result.stdout or "") + (result.stderr or ""),
                            errors="replace")
        step = DockerStepResult(name, result.returncode, seconds, str(log_path))
        self.steps.append(step)
        # The container runs as root inside the bind mount, so anything it
        # wrote is root-owned on the host; hand it back to this process's own
        # user so the mesh/solve cache copy and later cleanup (plain Python,
        # not root) can read and remove it.
        try:
            subprocess.run(["sudo", "chown", "-R", f"{os.getuid()}:{os.getgid()}",
                            str(self.remote_case)], capture_output=True, timeout=60)
        except (OSError, subprocess.TimeoutExpired):
            pass
        self._emit("step.completed", {"step": name, "status": result.returncode,
                                      "seconds": seconds})
        if result.returncode != 0:
            tail = "\n".join(log_path.read_text(errors="replace").splitlines()[-25:])
            raise RuntimeError(f"docker step {name!r} failed ({result.returncode}): {tail}")
        return step

    # -- mesh cache -----------------------------------------------------------

    def _mesh_cache_dir(self, cache_key: str) -> Path:
        safe = re.sub(r"[^A-Za-z0-9._-]", "_", cache_key)
        return MESH_CACHE_ROOT / safe

    def restore_cached_mesh(self, cache_key: str) -> bool:
        if os.environ.get("CERTONOMOUS_MESH_CACHE") == "0":
            return False
        cache = self._mesh_cache_dir(cache_key)
        poly = cache / "polyMesh"
        if not (poly / "points").exists() and not (poly / "points.gz").exists():
            return False
        dest = self.remote_case / "constant" / "polyMesh"
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(poly, dest)
        # The cell count lives in a log this restore never generates (that
        # log is only written by a fresh preProcessing.sh run); the sidecar
        # written at save time is the mesh's own reported count, carried
        # across the cache instead of read as 0 on every warm hit.
        sidecar = cache / "cells.txt"
        if sidecar.exists():
            self._cached_cell_count = sidecar.read_text().strip()
        return True

    def save_mesh_to_cache(self, cache_key: str) -> None:
        if os.environ.get("CERTONOMOUS_MESH_CACHE") == "0":
            return
        src = self.remote_case / "constant" / "polyMesh"
        if not src.exists():
            return
        cache = self._mesh_cache_dir(cache_key)
        if cache.exists():
            shutil.rmtree(cache)
        cache.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, cache / "polyMesh")
        cells = self.mesh_cell_count()
        if cells:
            (cache / "cells.txt").write_text(str(cells))

    # -- solve cache ----------------------------------------------------------

    def _solve_cache_dir(self, cache_key: str) -> Path:
        safe = re.sub(r"[^A-Za-z0-9._-]", "_", cache_key)
        return SOLVE_CACHE_ROOT / safe

    def _solved_time_dirs(self) -> list[str]:
        out = []
        for child in self.remote_case.iterdir():
            if child.is_dir() and re.fullmatch(r"[0-9]+", child.name) and child.name != "0":
                out.append(child.name)
        return sorted(out, key=int)

    def restore_cached_solve(self, cache_key: str, *, log_name: str = "run_model"
                             ) -> tuple[bool, str]:
        """Restore a finished solve's final time directory and its solver log
        (the log carries the CD/CL history postprocessing reads). Returns
        (hit, log_text)."""
        if os.environ.get("CERTONOMOUS_SOLVER_CACHE") == "0":
            return False, ""
        cache = self._solve_cache_dir(cache_key)
        done = cache / "DONE"
        if not done.exists():
            return False, ""
        latest = done.read_text().strip()
        if not re.fullmatch(r"[0-9]+", latest or ""):
            return False, ""
        dest = self.remote_case / latest
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(cache / latest, dest)
        log_text = (cache / f"{log_name}.log").read_text(errors="replace") \
            if (cache / f"{log_name}.log").exists() else ""
        return True, log_text

    def save_solve_to_cache(self, cache_key: str, *, log_text: str,
                            log_name: str = "run_model") -> None:
        if os.environ.get("CERTONOMOUS_SOLVER_CACHE") == "0":
            return
        solved = self._solved_time_dirs()
        if not solved:
            return
        latest = solved[-1]
        cache = self._solve_cache_dir(cache_key)
        if cache.exists():
            shutil.rmtree(cache)
        cache.mkdir(parents=True, exist_ok=True)
        shutil.copytree(self.remote_case / latest, cache / latest)
        (cache / f"{log_name}.log").write_text(log_text, errors="replace")
        (cache / "DONE").write_text(latest)

    def mesh_cell_count(self) -> int:
        """Cell count from renumberMesh's own log line, the same evidence the
        original ladder cited (``Mesh region0 size: N``).

        ``preProcessing.sh`` redirects its mesh-generation tool chain into
        ``logMeshGeneration.txt`` INSIDE the case directory (``&>``, ``>>``),
        not to the stdout this engine's own ``run()`` captures, so that file
        is read directly; the owner-file cell-count note is the fallback for
        a case whose recipe does not write that log.
        """
        if self._cached_cell_count:
            try:
                return int(self._cached_cell_count)
            except ValueError:
                pass
        gen_log = self.remote_case / "logMeshGeneration.txt"
        if gen_log.exists():
            match = re.search(r"Mesh region0 size:\s*(\d+)", gen_log.read_text(errors="replace"))
            if match:
                return int(match.group(1))
        for name in ("log.mesh", "log.preProcessing"):
            log_path = self.out_root / name
            if log_path.exists():
                match = re.search(r"Mesh region0 size:\s*(\d+)", log_path.read_text(errors="replace"))
                if match:
                    return int(match.group(1))
        owner_dir = self.remote_case / "constant" / "polyMesh"
        owner_plain, owner_gz = owner_dir / "owner", owner_dir / "owner.gz"
        text = None
        if owner_plain.exists():
            text = owner_plain.read_text(errors="replace")
        elif owner_gz.exists():
            import gzip
            with gzip.open(owner_gz, "rt", errors="replace") as fh:
                text = fh.read()
        if text:
            match = re.search(r"note\s+\"nPoints:\s*\d+\s+nCells:\s*(\d+)", text)
            if match:
                return int(match.group(1))
        return 0
