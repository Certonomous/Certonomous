"""Drive real VSPAERO wing solves from the lab — the OpenVSP adapter.

The solver lives behind ``OPENVSP_RUN_PREFIX`` (e.g. ``wsl -d Ubuntu --``),
the same launcher-prefix seam the OpenFOAM adapter uses: the lab writes a job
into a case directory, launches the OpenVSP python there, and reads the solved
polar back. Each evaluation is its own process and its own directory, so many
wings solve in parallel without sharing any state.

What comes back is a real vortex-lattice polar — induced drag, the solver's
wing viscous-drag estimate, and the point on that polar matched to the cruise
lift coefficient. What does not come back is a whole aircraft: the fuselage,
tail, and nacelles are not in the model, and the caller is expected to say so.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

_WORKER = Path(__file__).with_name("vspaero_worker.py")

# Where the OpenVSP release keeps its python packages, inside the launcher's
# filesystem. Overridable for a non-standard install.
_DEFAULT_PYTHONPATH = ("/opt/OpenVSP/python/openvsp:/opt/OpenVSP/python/"
                       "degen_geom:/opt/OpenVSP/python/utilities")


def available() -> bool:
    """True when a VSPAERO launcher is configured for this process."""
    if os.environ.get("OPENVSP_RUN_PREFIX"):
        return True
    return Path("/opt/OpenVSP/vspaero").exists()


# What every caller of ``evaluate`` consumes from a solved result. A prior
# result.json missing any of it (older schema, killed run, single-point solve)
# is not reusable evidence — it must be re-solved, never returned.
_POLAR_COLUMNS = ("CLtot", "CDi", "CDo")
_MATCHED_KEYS = ("alpha", "cdi", "cdo_wing", "extrapolated")


def _usable_prior(prior: Any, design: Mapping[str, float]) -> bool:
    """True only when a prior result carries everything the caller consumes:
    a polar with at least two finite points in every interpolated column, a
    matched cruise point with all its keys, and the surface path — and the
    matched point was solved for THIS design's cl_target, not another
    mission's."""
    if not isinstance(prior, dict) or "error" in prior:
        return False
    polar = prior.get("polar")
    if not isinstance(polar, dict):
        return False
    lengths = set()
    for column in _POLAR_COLUMNS:
        values = polar.get(column)
        if not isinstance(values, (list, tuple)) or len(values) < 2:
            return False
        if any(not isinstance(v, (int, float)) or isinstance(v, bool)
               for v in values):
            return False   # NaN scrubbed to None, or junk: not interpolable
        lengths.add(len(values))
    if len(lengths) != 1:
        return False
    matched = prior.get("matched")
    if not isinstance(matched, dict):
        return False
    if any(key not in matched for key in _MATCHED_KEYS):
        return False
    if "cl_target" in design:
        cl = matched.get("cl")
        if (not isinstance(cl, (int, float)) or isinstance(cl, bool)
                or abs(float(cl) - float(design["cl_target"])) > 1e-6):
            return False   # matched at a different cruise CL: wrong answer
    if not isinstance(prior.get("stl"), str):
        return False
    return True


class VspAeroWingApi:
    """Evaluate parametric wings with real VSPAERO solves, one case per design."""

    def __init__(self, workdir: str | Path, *,
                 run_prefix: str | Sequence[str] | None = None,
                 pythonpath: str | None = None,
                 timeout_s: float = 300.0,
                 reuse_prior: bool = True):
        # reuse_prior=False forces every evaluation to solve fresh. The race
        # lanes require it: their wall clocks ARE the measurement, so a reused
        # result would falsify the very number the act exists to show.
        self.reuse_prior = reuse_prior
        self.workdir = Path(workdir).resolve()
        self.workdir.mkdir(parents=True, exist_ok=True)
        prefix = (run_prefix if run_prefix is not None
                  else os.environ.get("OPENVSP_RUN_PREFIX", ""))
        self.run_prefix = (list(prefix.split()) if isinstance(prefix, str)
                           else list(prefix))
        self.pythonpath = (pythonpath
                           or os.environ.get("OPENVSP_PYTHONPATH")
                           or _DEFAULT_PYTHONPATH)
        self.timeout_s = timeout_s
        self._artifacts: list[dict[str, Any]] = []

    def evaluate(self, design: Mapping[str, float],
                 analyses: Sequence[str] = ()) -> Mapping[str, Any]:
        """Solve one wing; returns the polar, the matched cruise point, and
        the exported surface path. Raises RuntimeError when the solve fails."""
        # One case directory per DISTINCT design: every key that changes the
        # solve must be in the tag, or parallel evaluations clobber each other.
        tag = str(design.get("tag_hint", "")) or "wing-" + "-".join(
            f"{k}{float(v):g}" for k, v in sorted(design.items())
            if k in ("span", "area", "sweep", "alpha_start", "alpha_end",
                     "re_cref", "camber"))
        case = self.workdir / tag
        case.mkdir(parents=True, exist_ok=True)

        # A design already solved in this case directory is reused as-is —
        # same polar, same surface, instant. The demo machine is small; the
        # capability is the chain, and the reuse is silent by design
        # (CERTONOMOUS_SOLVER_CACHE=0 forces every solve fresh).
        if self.reuse_prior and os.environ.get("CERTONOMOUS_SOLVER_CACHE", "1") != "0":
            prior_path = case / "result.json"
            if prior_path.exists():
                try:
                    prior = json.loads(prior_path.read_text(encoding="utf-8"))
                    prior_stl = case / (prior.get("stl", "wing.stl")
                                        if isinstance(prior, dict) else "wing.stl")
                    if _usable_prior(prior, design) and prior_stl.exists():
                        self._artifacts.append({"kind": "surface",
                                                "path": str(prior_stl),
                                                "design": dict(design)})
                        self._artifacts.append({"kind": "polar",
                                                "path": str(prior_path),
                                                "design": dict(design)})
                        prior["case_dir"] = str(case)
                        prior["stl_path"] = str(prior_stl)
                        return prior
                except Exception:
                    pass   # unreadable prior result: solve fresh

        shutil.copy(_WORKER, case / "vspaero_worker.py")
        (case / "job.json").write_text(json.dumps(dict(design)),
                                       encoding="utf-8")
        # A stale result.json must never masquerade as this run's output: if
        # the worker dies before writing (killed WSL, timeout), reading the
        # leftover file back would report a solve that never happened.
        (case / "result.json").unlink(missing_ok=True)

        # ``env`` carries PYTHONPATH through launcher prefixes that do not
        # forward the host environment (WSL, containers). The cwd *is* the
        # case, so the launcher's filesystem view translates it for us.
        command = [*self.run_prefix, "env", f"PYTHONPATH={self.pythonpath}",
                   "python3", "vspaero_worker.py"]
        log_path = case / "log.vspaero"
        with log_path.open("w") as log:
            subprocess.run(command, stdout=log, stderr=subprocess.STDOUT,
                           timeout=self.timeout_s, cwd=case)

        result_path = case / "result.json"
        if not result_path.exists():
            raise RuntimeError(
                f"VSPAERO produced no result for {tag} — see {log_path}")
        result = json.loads(result_path.read_text(encoding="utf-8"))
        if "error" in result:
            raise RuntimeError(f"VSPAERO failed for {tag}: {result['error']}")

        stl = case / result.get("stl", "wing.stl")
        self._artifacts.append({"kind": "surface", "path": str(stl),
                                "design": dict(design)})
        self._artifacts.append({"kind": "polar", "path": str(result_path),
                                "design": dict(design)})
        result["case_dir"] = str(case)
        result["stl_path"] = str(stl)
        return result

    def evaluate_many(self, designs: Sequence[Mapping[str, float]], *,
                      max_workers: int = 6,
                      on_result: Callable[[int, Mapping[str, Any] | None,
                                           str | None], None] | None = None,
                      ) -> list[Mapping[str, Any] | None]:
        """Solve a batch of wings in parallel; order of results matches input.

        Failed solves come back as None (with the error passed to
        ``on_result``) so one bad design does not sink the batch.
        """
        results: list[Mapping[str, Any] | None] = [None] * len(designs)

        def _one(index: int) -> None:
            try:
                results[index] = self.evaluate(designs[index])
                if on_result:
                    on_result(index, results[index], None)
            except Exception as exc:
                if on_result:
                    on_result(index, None, str(exc))

        with ThreadPoolExecutor(max_workers=max(1, max_workers)) as pool:
            list(pool.map(_one, range(len(designs))))
        return results

    def close(self) -> None:
        return None

    def artifacts(self) -> list[dict[str, Any]]:
        return list(self._artifacts)
