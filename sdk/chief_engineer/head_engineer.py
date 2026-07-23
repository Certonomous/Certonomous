"""Head Engineer: geometry-to-report pipeline with a live monitoring sub-agent.

The Head Engineer executes an OpenFOAM case end to end:

1. **Geometry intake** — receives an STL/OBJ surface, runs ``surfaceCheck``,
   and reports manifoldness/open-edge issues before any meshing happens.
2. **Meshing and solving** — stages the case on the WSL-native filesystem
   (as the non-root ``foam`` user; dynamic-code security forbids root), runs
   the step sequence (surface features → blockMesh → snappyHexMesh → solver),
   and streams every solver line through a :class:`LogMonitor` sub-agent that
   watches for NaNs, floating-point exceptions, suspicious residual growth,
   bounded-variable warnings — and, for never-before-seen cases, collects
   novel solver behaviors as candidate knowledge.
3. **Postprocессing** — parses the force-coefficient history, computes
   converged statistics, renders the quantity **with its uncertainty envelope
   on the plot itself**, writes a Markdown report (geometry, mesh, solve,
   results table, anomalies, diagnostics, next steps), and emails it when
   SMTP is configured (``CERTONOMOUS_SMTP_HOST/PORT/USER/PASSWORD/TO``);
   otherwise the report is saved and the email step reports why it was
   skipped.

Everything here is orchestration and analysis — solvers do the physics.
"""

from __future__ import annotations

import os
import re
import smtplib
import subprocess
import threading
import time
from dataclasses import dataclass, field
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Callable, Sequence

WSL = ["wsl", "-d", "Ubuntu", "-u", "foam", "--"]
RUN_ROOT = "~/certonomous-runs"
# The snapped mesh from a cold run is cached here, keyed by body, so a warm run
# reuses it and skips the long snappyHexMesh stage. The cache holds the PATH
# (mesh topology), never the RESULTS — every warm run still solves the flow live.
MESH_CACHE_ROOT = f"{RUN_ROOT}/.mesh-cache"
# Literal install path: environment-variable expansion of FOAM_TUTORIALS
# through the Windows->WSL->bash quoting stack proved unreliable, and the
# packaged install location is version-stable.  Override via env if needed.
FOAM_TUTORIALS = os.environ.get(
    "CERTONOMOUS_FOAM_TUTORIALS", "/usr/lib/openfoam/openfoam2606/tutorials")


# --------------------------------------------------------------------------
# Monitoring sub-agent
# --------------------------------------------------------------------------

@dataclass
class Anomaly:
    kind: str          # nan | fpe | residual-spike | bounding | novel-warning
    step: str
    line: str
    detail: str = ""


class LogMonitor:
    """Streams solver output line by line and raises structured anomalies.

    Two lessons are built into the thresholds. First, comparing a residual to
    its all-time minimum is useless in a converging solve: the deeper it
    converges, the larger every ordinary wobble looks as a multiple, so a
    healthy run drowns the log in alerts. The comparison here is against a
    rolling median of recent history instead, and a spike must also be part of
    a rising trend. Second, a repeated condition is one finding, not hundreds —
    each kind is reported a few times per step and then counted silently.

    In ``novel`` mode, first-seen warning patterns are additionally captured as
    candidate knowledge for a body the lab has not solved before.
    """

    RESIDUAL = re.compile(r"Solving for (\w+),.*Initial residual = ([0-9.eE+-]+)")
    NAN = re.compile(r"\bnan\b|\bNaN\b|-nan", re.IGNORECASE)
    # Every OpenFOAM log banner advertises FPE *trapping*; only an actual
    # signal handler firing (or a raw FPE message) is an anomaly.
    FPE = re.compile(r"Foam::sigFpe::sigHandler|^Floating point exception", re.MULTILINE)
    BOUNDING = re.compile(r"^bounding (\w+),", re.MULTILINE)
    WARNING = re.compile(r"--> FOAM Warning|FOAM Warning :")

    WINDOW = 25
    REPORT_LIMIT = 3

    def __init__(self, *, novel: bool = False, spike_factor: float = 25.0,
                 on_anomaly: Callable[[Anomaly], None] | None = None):
        self.novel = novel
        self.spike_factor = spike_factor
        self.on_anomaly = on_anomaly
        self.anomalies: list[Anomaly] = []
        self.novel_observations: list[str] = []
        self.suppressed: dict[str, int] = {}
        self._history: dict[str, list[float]] = {}
        self._reported: dict[tuple[str, str], int] = {}
        self._seen_warnings: set[str] = set()

    def feed(self, step: str, line: str) -> None:
        if self.FPE.search(line):
            self._raise(Anomaly("fpe", step, line.strip(), "floating point exception"))
            return
        if self.NAN.search(line) and ("Solving for" in line or "= nan" in line.lower()):
            self._raise(Anomaly("nan", step, line.strip(), "NaN in solver output"))
            return
        match = self.RESIDUAL.search(line)
        if match:
            self._residual(step, match.group(1), float(match.group(2)), line)
            return
        if self.BOUNDING.search(line):
            self._raise(Anomaly("bounding", step, line.strip(),
                                "a variable was clipped to stay physical"))
            return
        if self.novel and self.WARNING.search(line):
            key = re.sub(r"[0-9.eE+-]+", "#", line.strip())[:120]
            if key not in self._seen_warnings:
                self._seen_warnings.add(key)
                self.novel_observations.append(line.strip())
                self._raise(Anomaly("novel-warning", step, line.strip(),
                                    "first occurrence on an unfamiliar case"))

    def _residual(self, step: str, field: str, residual: float, line: str) -> None:
        history = self._history.setdefault(field, [])
        history.append(residual)
        if len(history) > self.WINDOW:
            history.pop(0)
        # Need enough history for a median to mean anything, and a spike only
        # counts if the last few values are climbing rather than oscillating.
        if len(history) < self.WINDOW:
            return
        ordered = sorted(history[:-1])
        median = ordered[len(ordered) // 2]
        rising = history[-1] > history[-2] > history[-3]
        if median > 0 and residual > self.spike_factor * median and rising:
            self._raise(Anomaly(
                "residual-spike", step, line.strip(),
                f"{field} residual {residual:.3g} is {residual / median:.0f}x its "
                f"recent median {median:.3g} and still climbing"))
            history.clear()

    def _raise(self, anomaly: Anomaly) -> None:
        self.anomalies.append(anomaly)
        key = (anomaly.kind, anomaly.step)
        seen = self._reported.get(key, 0) + 1
        self._reported[key] = seen
        if seen > self.REPORT_LIMIT and anomaly.kind not in {"nan", "fpe"}:
            self.suppressed[anomaly.kind] = self.suppressed.get(anomaly.kind, 0) + 1
            return
        if self.on_anomaly:
            self.on_anomaly(anomaly)

    def summary(self) -> dict[str, Any]:
        by_kind: dict[str, int] = {}
        for item in self.anomalies:
            by_kind[item.kind] = by_kind.get(item.kind, 0) + 1
        return {
            "anomalies": len(self.anomalies),
            "by_kind": by_kind,
            "reported": sum(min(v, self.REPORT_LIMIT) for v in self._reported.values()),
            "suppressed": dict(self.suppressed),
            "fatal": any(item.kind in {"nan", "fpe"} for item in self.anomalies),
            "novel_observations": list(self.novel_observations),
        }


# --------------------------------------------------------------------------
# Result parsing / statistics
# --------------------------------------------------------------------------

def parse_coefficient_history(text: str) -> dict[str, list[float]]:
    """Full iteration history from a forceCoeffs table (any OpenFOAM layout)."""
    header: list[str] = []
    columns: dict[str, list[float]] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            tokens = stripped.lstrip("#").split()
            if len(tokens) > 1:
                header = tokens
            continue
        try:
            values = [float(token) for token in stripped.split()]
        except ValueError:
            continue
        if len(values) < len(header):
            continue
        for name, value in zip(header, values):
            columns.setdefault(name, []).append(value)
    return columns


def envelope_statistics(series: Sequence[float], window_fraction: float = 0.2):
    """Converged value ± 2-sigma envelope over the final window."""
    n = len(series)
    if n == 0:
        return None
    window = list(series[-max(2, int(n * window_fraction)):]) if n > 1 else list(series)
    mean = sum(window) / len(window)
    if len(window) > 1:
        sigma = (sum((v - mean) ** 2 for v in window) / (len(window) - 1)) ** 0.5
    else:
        sigma = 0.0
    return {"value": mean, "sigma": sigma, "lo": mean - 2 * sigma, "hi": mean + 2 * sigma,
            "window": len(window)}


def plot_with_envelope(iterations, series, name, out_png, *, window: int = 25):
    """Convergence curve with a rolling ±2-sigma envelope, single hue, one axis."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    means, los, his = [], [], []
    for i in range(len(series)):
        chunk = series[max(0, i - window + 1): i + 1]
        m = sum(chunk) / len(chunk)
        s = (sum((v - m) ** 2 for v in chunk) / (len(chunk) - 1)) ** 0.5 if len(chunk) > 1 else 0.0
        means.append(m); los.append(m - 2 * s); his.append(m + 2 * s)

    line = "#2563b8"
    ink, muted = "#1c2430", "#6b7684"
    fig, ax = plt.subplots(figsize=(8.2, 4.4), dpi=140)
    ax.fill_between(iterations, los, his, color=line, alpha=0.16, linewidth=0)
    ax.plot(iterations, series, color=line, linewidth=0.9, alpha=0.45)
    ax.plot(iterations, means, color=line, linewidth=2.0)
    final = envelope_statistics(series)
    if final:
        ax.annotate(
            f"{name} = {final['value']:.4g} ± {2 * final['sigma']:.2g} (95%)",
            xy=(iterations[-1], means[-1]), xytext=(-8, 14),
            textcoords="offset points", ha="right", fontsize=10, color=ink,
        )
        ax.annotate("±2σ envelope", xy=(iterations[len(iterations) // 3],
                    his[len(his) // 3]), xytext=(0, 6), textcoords="offset points",
                    fontsize=8.5, color=muted)
    ax.set_xlabel("iteration", color=ink, fontsize=9)
    ax.set_ylabel(name, color=ink, fontsize=9)
    ax.set_title(f"{name} convergence with uncertainty envelope",
                 color=ink, fontsize=11, loc="left")
    ax.grid(True, color="#dfe4ea", linewidth=0.6)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(muted)
    ax.tick_params(colors=muted, labelsize=8)
    fig.tight_layout()
    fig.savefig(out_png)
    plt.close(fig)
    return str(out_png)


# --------------------------------------------------------------------------
# Head Engineer
# --------------------------------------------------------------------------

@dataclass
class StepResult:
    name: str
    status: int
    seconds: float
    log_path: str


class HeadEngineer:
    """Run one geometry through clean → mesh → solve → report, monitored."""

    def __init__(self, case_name: str, out_root: str | os.PathLike[str], *,
                 novel: bool = False,
                 on_event: Callable[[str, dict], None] | None = None):
        self.case_name = case_name
        # Unique per instance: two studies of the same body must not share a
        # working directory, or the second will delete the first mid-solve.
        import secrets
        self.remote_case = f"{RUN_ROOT}/{case_name}-{secrets.token_hex(3)}"
        self.out_root = Path(out_root) / case_name
        self.out_root.mkdir(parents=True, exist_ok=True)
        self.monitor = LogMonitor(novel=novel, on_anomaly=self._on_anomaly)
        self.on_event = on_event
        self.steps: list[StepResult] = []
        self.geometry_report: dict[str, Any] = {}
        self.mesh_stats: dict[str, Any] = {}
        self.results: dict[str, Any] = {}
        self.plots: list[str] = []

    # -- infrastructure ----------------------------------------------------

    def _emit(self, event: str, payload: dict) -> None:
        if self.on_event:
            self.on_event(event, payload)

    def _on_anomaly(self, anomaly: Anomaly) -> None:
        self._emit("monitor.anomaly", {
            "kind": anomaly.kind, "step": anomaly.step, "detail": anomaly.detail,
        })

    def _wsl(self, command: str, timeout: float = 600.0) -> subprocess.CompletedProcess:
        # The openfoam2606 launcher provides PATH but does not export project
        # variables (FOAM_TUTORIALS, WM_PROJECT_DIR) to non-interactive
        # children — source the bashrc explicitly so both are available.
        preamble = ("for rc in /usr/lib/openfoam/openfoam*/etc/bashrc; do "
                    "source \"$rc\" >/dev/null 2>&1; break; done; ")
        return subprocess.run(
            [*WSL, "bash", "-c", preamble + command],
            capture_output=True, text=True, timeout=timeout,
        )

    def _run_step(self, name: str, command: str, timeout: float = 3600.0) -> StepResult:
        """Run one case step inside WSL, streaming output through the monitor."""
        self._emit("step.started", {"step": name})
        log_path = self.out_root / f"log.{name}"
        start = time.monotonic()
        process = subprocess.Popen(
            [*WSL, "bash", "-lc",
             f"cd {self.remote_case} && openfoam2606 {command} 2>&1"],
            stdout=subprocess.PIPE, text=True, errors="replace", bufsize=1,
        )
        with log_path.open("w", errors="replace") as log:
            for line in process.stdout:
                log.write(line)
                self.monitor.feed(name, line)
        status = process.wait(timeout=timeout)
        result = StepResult(name, status, round(time.monotonic() - start, 1), str(log_path))
        self.steps.append(result)
        self._emit("step.completed", {"step": name, "status": status,
                                      "seconds": result.seconds})
        if status != 0:
            tail = "".join(log_path.read_text(errors="replace").splitlines(True)[-8:])
            raise RuntimeError(f"step {name!r} failed ({status}): {tail}")
        return result

    # -- pipeline ----------------------------------------------------------

    def stage_case(self, template_wsl_path: str) -> None:
        """Copy a case template to the run area (WSL-native for meshing speed)."""
        staged = self._wsl(
            f"rm -rf {self.remote_case} && mkdir -p {RUN_ROOT} && "
            f"cp -r {template_wsl_path} {self.remote_case} && "
            f"chmod -R u+w {self.remote_case} && "
            f"test -f {self.remote_case}/system/controlDict && echo STAGED")
        if "STAGED" not in staged.stdout:
            raise RuntimeError(
                f"case staging from {template_wsl_path!r} failed: "
                f"{(staged.stderr or staged.stdout).strip()[:300]}")

    def _mesh_cache_dir(self, cache_key: str) -> str:
        # A filesystem-safe key so a body name never escapes the cache root.
        safe = re.sub(r"[^A-Za-z0-9._-]", "_", cache_key)
        return f"{MESH_CACHE_ROOT}/{safe}"

    def cached_mesh_available(self, cache_key: str) -> bool:
        """True when a snapped mesh for this body is already cached (warm run)."""
        if os.environ.get("CERTONOMOUS_MESH_CACHE") == "0":
            return False
        cache = self._mesh_cache_dir(cache_key)
        probe = self._wsl(
            f"test -f {cache}/polyMesh/points && test -f {cache}/polyMesh/owner "
            f"&& echo CACHED", timeout=120)
        return "CACHED" in probe.stdout

    def restore_cached_mesh(self, cache_key: str) -> bool:
        """Copy the cached snapped mesh into this case, skipping the mesh build.

        Returns True when a warm mesh was restored; False when none is cached and
        the case must mesh cold. Only the mesh topology is reused — the fields and
        the solve are untouched, so every warm run still produces live numbers.
        """
        if not self.cached_mesh_available(cache_key):
            return False
        cache = self._mesh_cache_dir(cache_key)
        restored = self._wsl(
            f"mkdir -p {self.remote_case}/constant && "
            f"rm -rf {self.remote_case}/constant/polyMesh && "
            f"cp -r {cache}/polyMesh {self.remote_case}/constant/polyMesh && "
            f"test -f {self.remote_case}/constant/polyMesh/points && echo RESTORED",
            timeout=300)
        return "RESTORED" in restored.stdout

    def save_mesh_to_cache(self, cache_key: str) -> None:
        """Cache this case's snapped mesh so the next run of this body is warm."""
        if os.environ.get("CERTONOMOUS_MESH_CACHE") == "0":
            return
        cache = self._mesh_cache_dir(cache_key)
        self._wsl(
            f"test -f {self.remote_case}/constant/polyMesh/points && "
            f"mkdir -p {cache} && rm -rf {cache}/polyMesh && "
            f"cp -r {self.remote_case}/constant/polyMesh {cache}/polyMesh || true",
            timeout=300)

    def clear_mesh_cache(self, cache_key: str) -> None:
        """Drop a cached mesh. A refinement ladder must never reuse another
        rung's mesh, so each rung clears the body's entry before meshing."""
        cache = self._mesh_cache_dir(cache_key)
        self._wsl(f"rm -rf {cache}", timeout=120)

    def solve_ranks(self) -> int:
        """How many MPI ranks the steady solve should use.

        Default 1 (serial — the fully-tested path). Set CERTONOMOUS_SOLVE_RANKS
        to the tutorial's native decomposition (the motorBike case ships a 6-way
        split) to run the on-camera warm solve in parallel and fit its slot on a
        quiet machine. Reused meshes and live numbers are unaffected either way.
        """
        raw = os.environ.get("CERTONOMOUS_SOLVE_RANKS", "1")
        try:
            return max(1, int(raw))
        except (TypeError, ValueError):
            return 1

    def decompose_for_parallel(self, ranks: int) -> bool:
        """Split the case into ``ranks`` subdomains for a parallel solve.

        Uses the case's own decomposeParDict.<ranks> when present (the tutorial
        ships one), else a scotch decomposition it writes. Best-effort: returns
        False so the caller solves serially if decomposition is unavailable or
        fails — the mission never stalls on the parallel path.
        """
        if ranks <= 1:
            return False
        dict_setup = (
            f"cd {self.remote_case} && "
            f"(test -f system/decomposeParDict.{ranks} && "
            f"cp system/decomposeParDict.{ranks} system/decomposeParDict || "
            f"printf 'FoamFile{{version 2.0;format ascii;class dictionary;"
            f"object decomposeParDict;}}\\nnumberOfSubdomains {ranks};\\n"
            f"method scotch;\\n' > system/decomposeParDict) && echo DICT")
        setup = self._wsl(dict_setup, timeout=120)
        if "DICT" not in setup.stdout:
            return False
        result = self._run_step("decomposePar", "decomposePar -force", 600)
        return result.status == 0

    def reconstruct_latest(self) -> None:
        """Merge the decomposed solution back so postprocessing reads it serially."""
        self._run_step("reconstructPar", "reconstructPar -latestTime", 1200)

    def set_iteration_count(self, iterations: int) -> None:
        """Set the steady solver's endTime so the run matches its stated length.

        A staged tutorial ships its own endTime; when the workflow promises N
        iterations the controlDict must say so too, or the report describes a run
        that never happened. Best-effort: a failure here leaves the template's
        own endTime in place rather than stopping the study.
        """
        try:
            n = int(iterations)
        except (TypeError, ValueError):
            return
        if n <= 0:
            return
        self._wsl(
            f"cd {self.remote_case} && openfoam2606 foamDictionary "
            f"-entry endTime -set {n} system/controlDict >/dev/null 2>&1 || true",
            timeout=120)

    def intake_geometry(self, geometry_wsl_path: str, target_name: str) -> dict[str, Any]:
        """Place the surface in constant/triSurface and surface-check it."""
        self._wsl(
            f"mkdir -p {self.remote_case}/constant/triSurface && "
            f"cp {geometry_wsl_path} {self.remote_case}/constant/triSurface/ && "
            f"cd {self.remote_case}/constant/triSurface && "
            f"for f in *.gz; do [ -f \"$f\" ] && gunzip -f \"$f\"; done; true"
        )
        check = self._wsl(
            f"cd {self.remote_case} && openfoam2606 surfaceCheck "
            f"constant/triSurface/{target_name} 2>&1 | tail -40", timeout=300)
        text = check.stdout
        (self.out_root / "log.surfaceCheck").write_text(text, errors="replace")
        report = {
            "surface": target_name,
            "closed": "surface is closed" in text.lower(),
            "issues": [],
        }
        for pattern, label in (
            (r"Surface has (\d+) illegal triangles", "illegal triangles"),
            (r"(\d+)\s+open edges", "open edges"),
            (r"Number of unconnected parts\s*:\s*(\d+)", "unconnected parts"),
        ):
            match = re.search(pattern, text)
            if match and int(match.group(1)) > (1 if "parts" in label else 0):
                report["issues"].append(f"{match.group(1)} {label}")
        self.geometry_report = report
        self._emit("geometry.checked", report)
        return report

    def collect_mesh_stats(self) -> dict[str, Any]:
        check = self._wsl(f"cd {self.remote_case} && openfoam2606 checkMesh 2>&1", timeout=1200)
        text = check.stdout
        (self.out_root / "log.checkMesh").write_text(text, errors="replace")
        stats: dict[str, Any] = {"mesh_ok": "Mesh OK" in text}
        for pattern, key in (
            (r"cells:\s+(\d+)", "cells"),
            (r"non-orthogonality Max:\s*([0-9.]+)", "max_non_orthogonality"),
            (r"Max non-orthogonality =\s*([0-9.]+)", "max_non_orthogonality"),
            (r"Max skewness =\s*([0-9.]+)", "max_skewness"),
        ):
            match = re.search(pattern, text)
            if match:
                stats[key] = float(match.group(1))
        self.mesh_stats = stats
        self._emit("mesh.checked", stats)
        return stats

    def postprocess(self, coefficients: Sequence[str] = ("Cd", "Cl")) -> dict[str, Any]:
        """Pull force-coefficient history back, compute envelopes, render plots."""
        listing = self._wsl(
            f"find {self.remote_case}/postProcessing -name '*.dat' "
            f"-path '*orce*' 2>/dev/null | head -3")
        results: dict[str, Any] = {}
        for remote in [p for p in listing.stdout.split() if p]:
            local = self.out_root / Path(remote).name
            self._wsl(f"cp '{remote}' \"$(wslpath '{local}')\"")
            history = parse_coefficient_history(local.read_text(errors="replace"))
            iterations = history.get("Time", [])
            for name in coefficients:
                series = history.get(name)
                if not series or not iterations:
                    continue
                stats = envelope_statistics(series)
                results[name] = stats
                png = plot_with_envelope(iterations[:len(series)], series, name,
                                         self.out_root / f"{name}_envelope.png")
                if png:
                    self.plots.append(png)
            break
        self.results = results
        self._emit("postprocess.completed", {"metrics": list(results)})
        return results

    # -- reporting ---------------------------------------------------------

    def diagnostics(self) -> list[str]:
        notes = []
        monitor = self.monitor.summary()
        if monitor["fatal"]:
            notes.append("Fatal numerical anomaly (NaN/FPE) — results untrustworthy; "
                         "halve relaxation factors or revisit mesh quality before rerun.")
        if monitor["by_kind"].get("residual-spike"):
            notes.append(f"{monitor['by_kind']['residual-spike']} residual spike(s) — "
                         "inspect the flagged iterations; consider tighter relaxation.")
        if monitor["by_kind"].get("bounding"):
            notes.append("Bounded turbulence variables observed — normal in startup, "
                         "suspect if persisting past ~100 iterations.")
        if self.mesh_stats.get("max_non_orthogonality", 0) > 70:
            notes.append("Max non-orthogonality > 70° — add nonOrthogonalCorrectors "
                         "or improve the mesh in flagged regions.")
        for name, stats in self.results.items():
            if stats and stats["value"] != 0 and abs(2 * stats["sigma"] / stats["value"]) > 0.05:
                notes.append(f"{name} envelope exceeds 5% of its value — per lesson "
                             "L-001, extend the run or refine the mesh until the "
                             "remaining uncertainty is irreducible.")
        if not notes:
            notes.append("No anomalies; envelopes tight. Next lever per doctrine: "
                         "grid-convergence check to quantify discretization error.")
        return notes

    def report_markdown(self) -> str:
        monitor = self.monitor.summary()
        non_ortho = self.mesh_stats.get("max_non_orthogonality")
        skew = self.mesh_stats.get("max_skewness")
        non_ortho_s = f"{non_ortho:.1f}°" if non_ortho is not None else "—"
        skew_s = f"{skew:.2f}" if skew is not None else "—"
        lines = [
            f"# Certonomous Head Engineer report — {self.case_name}",
            "",
            "| Section | Result |",
            "|---|---|",
            f"| Geometry | {self.geometry_report.get('surface', 'n/a')} — "
            f"{'closed, ' if self.geometry_report.get('closed') else ''}"
            f"{', '.join(self.geometry_report.get('issues', [])) or 'no issues found'} |",
            f"| Mesh | {int(self.mesh_stats.get('cells', 0))} cells, "
            f"max non-ortho {non_ortho_s}, "
            f"max skew {skew_s}, "
            f"{'OK' if self.mesh_stats.get('mesh_ok') else 'check flags'} |",
            f"| Steps | " + "; ".join(
                f"{s.name} — {s.seconds:.0f} s ({'ok' if s.status == 0 else 'FAIL'})"
                for s in self.steps) + " |",
            f"| Monitor | {monitor['anomalies']} anomalies {monitor['by_kind']} |",
        ]
        for name, stats in self.results.items():
            if stats:
                lines.append(
                    f"| {name} | **{stats['value']:.4g} ± {2 * stats['sigma']:.2g}** "
                    f"(95% envelope [{stats['lo']:.4g}, {stats['hi']:.4g}], "
                    f"window {stats['window']}) |")
        lines += ["", "## Diagnostics and next steps", ""]
        lines += [f"- {note}" for note in self.diagnostics()]
        if monitor["novel_observations"]:
            lines += ["", "## Novel observations (candidate knowledge)", ""]
            lines += [f"- `{obs}`" for obs in monitor["novel_observations"][:10]]
        if self.plots:
            lines += ["", "## Plots", ""]
            lines += [f"- {Path(p).name}" for p in self.plots]
        text = "\n".join(lines) + "\n"
        (self.out_root / "report.md").write_text(text, errors="replace")
        return text

    def email_report(self, report_text: str) -> str:
        host = os.environ.get("CERTONOMOUS_SMTP_HOST")
        recipient = os.environ.get("CERTONOMOUS_SMTP_TO")
        if not host or not recipient:
            return ("email skipped: set CERTONOMOUS_SMTP_HOST/PORT/USER/PASSWORD/TO "
                    "to enable delivery; report saved to "
                    f"{self.out_root / 'report.md'}")
        message = EmailMessage()
        message["Subject"] = f"Certonomous report — {self.case_name}"
        message["From"] = os.environ.get("CERTONOMOUS_SMTP_USER", "certonomous@localhost")
        message["To"] = recipient
        message.set_content(report_text)
        for png in self.plots:
            message.add_attachment(Path(png).read_bytes(), maintype="image",
                                   subtype="png", filename=Path(png).name)
        with smtplib.SMTP(host, int(os.environ.get("CERTONOMOUS_SMTP_PORT", "587"))) as smtp:
            smtp.starttls()
            user = os.environ.get("CERTONOMOUS_SMTP_USER")
            if user:
                smtp.login(user, os.environ.get("CERTONOMOUS_SMTP_PASSWORD", ""))
            smtp.send_message(message)
        return f"report emailed to {recipient}"


# --------------------------------------------------------------------------
# Reference mission: the motorBike STL, end to end
# --------------------------------------------------------------------------

def run_motorbike_demo(out_root: str | os.PathLike[str],
                       *, iterations: int = 300,
                       on_event: Callable[[str, dict], None] | None = None) -> HeadEngineer:
    """STL intake → snappyHexMesh → simpleFoam on the canonical motorBike case."""
    engineer = HeadEngineer("motorbike", out_root, novel=True, on_event=on_event)
    engineer.stage_case(f"{FOAM_TUTORIALS}/incompressible/simpleFoam/motorBike")
    engineer.intake_geometry(f"{FOAM_TUTORIALS}/resources/geometry/motorBike.obj.gz",
                             "motorBike.obj")
    engineer._wsl(
        f"cd {engineer.remote_case} && cp -r 0.orig 0 && "
        f"openfoam2606 foamDictionary -entry endTime -set {iterations} "
        f"system/controlDict && "
        f"openfoam2606 foamDictionary -entry writeInterval -set {iterations} "
        f"system/controlDict")
    engineer._run_step("surfaceFeatureExtract", "surfaceFeatureExtract", 900)
    engineer._run_step("blockMesh", "blockMesh", 900)
    engineer._run_step("snappyHexMesh", "snappyHexMesh -overwrite", 5400)
    engineer._wsl(f"cd {engineer.remote_case} && rm -rf 0 && cp -r 0.orig 0")
    engineer.collect_mesh_stats()
    engineer._run_step("potentialFoam", "potentialFoam -writephi", 1800)
    engineer._run_step("simpleFoam", "simpleFoam", 7200)
    engineer.postprocess(("Cd", "Cl"))
    report = engineer.report_markdown()
    engineer._emit("report.ready", {"email": engineer.email_report(report)})
    return engineer
