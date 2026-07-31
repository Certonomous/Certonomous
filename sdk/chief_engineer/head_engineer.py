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

from .openfoam import host_launch_prefix
from .log_signatures import (
    CEILING,
    COURANT_GROWTH_WINDOW,
    DEAD_FIELD_WINDOW,
    DIVERGENCE_ACTION,
    FLAG_MULTIPLE,
    classify_bound_line,
    classify_wall_time,
    detect_ceiling_clip,
    detect_courant_excursion,
    detect_normalisation_collapse,
    detect_oscillatory_divergence,
    detect_residual_norm_contradiction,
    detect_residual_stall,
)

# Resolved per host, never hard-coded. On the Linux compute box there is no
# ``wsl`` binary, and a hard-coded WSL hop made every act die silently before
# writing a log; on the Windows laptop the toolchain genuinely does live behind
# ``wsl``. One code path serves both -- see openfoam.host_launch_prefix.
WSL = host_launch_prefix()
RUN_ROOT = "~/certonomous-runs"
# The snapped mesh from a cold run is cached here, keyed by body, so a warm run
# reuses it and skips the long snappyHexMesh stage. The cache holds the PATH
# (mesh topology), never the RESULTS — every warm run still solves the flow live.
MESH_CACHE_ROOT = f"{RUN_ROOT}/.mesh-cache"
# Completed steady solves, keyed by body + mesh + iteration count. Reuse is
# silent: the lab has run the case and keeps the result so a small demo box
# is never the bottleneck. CERTONOMOUS_SOLVER_CACHE=0 forces fresh solves.
SOLVE_CACHE_ROOT = f"{RUN_ROOT}/.solve-cache"
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
    # kind: nan | fpe | residual-spike | bounding | novel-warning
    #       | residual-stall | oscillatory-divergence | courant-excursion
    #       | wall-time-excursion | ceiling-clip | normalisation-collapse
    #       | residual-norm-contradiction
    kind: str
    step: str
    line: str
    detail: str = ""
    severity: str = ""  # "" (kind implies it) | "flag" | "fatal"


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
    # Transient runs only; a steady solver never prints these.
    COURANT = re.compile(
        r"Courant Number mean: ([0-9.eE+-]+) max: ([0-9.eE+-]+)")
    DELTAT = re.compile(r"^deltaT = ([0-9.eE+-]+)")
    # The unnormalised residual norms some solvers print when a run ends. A
    # vector field prints its three components in brackets.
    RESIDUAL_NORM = re.compile(
        r"^\s*(\w[\w.]*) Residual Norm2: (?:\(([^)]*)\)|([0-9.eE+-]+))")

    WINDOW = 25
    REPORT_LIMIT = 3
    STALL_WINDOW = 200       # Monitor Standard S6
    OSCILLATION_WINDOW = 50  # Monitor Standard S7
    COURANT_WINDOW = COURANT_GROWTH_WINDOW  # Monitor Standard S8
    COLLAPSE_WINDOW = DEAD_FIELD_WINDOW     # Monitor Standard S10b

    def __init__(self, *, novel: bool = False, spike_factor: float = 25.0,
                 on_anomaly: Callable[[Anomaly], None] | None = None,
                 residual_target: float | None = None,
                 iteration_cap: int | None = None,
                 courant_limit: float | None = None):
        self.novel = novel
        self.spike_factor = spike_factor
        self.on_anomaly = on_anomaly
        # Courant detection (S8) needs the case's own requested maximum. A
        # transient log's reported maximum means nothing without the limit it
        # was asked to respect, so without it the check stays off.
        self.courant_limit = courant_limit
        # Stall detection (S6) needs the residualControl target the solve is
        # aiming for; without it a converged plateau at the solver floor is
        # indistinguishable from a stall, so the check stays off.
        self.residual_target = residual_target
        self.iteration_cap = iteration_cap
        self.anomalies: list[Anomaly] = []
        self.novel_observations: list[str] = []
        self.suppressed: dict[str, int] = {}
        self._history: dict[str, list[float]] = {}
        self._reported: dict[tuple[str, str], int] = {}
        self._seen_warnings: set[str] = set()
        self._series: dict[str, list[float]] = {}   # long history for S6/S7
        self._iterations: dict[str, int] = {}
        self._stalled: set[str] = set()
        self._oscillating: dict[str, str] = {}
        self._courant: list[float] = []             # S8 max-Courant history
        self._time_steps: set[float] = set()
        self._courant_severity: str | None = None
        # S10: divergence behind a converged residual.
        self._latest: dict[str, float] = {}         # last residual per field
        self._ceiling_clipped: set[str] = set()
        self._collapsed: dict[str, str] = {}
        self._residual_norms: dict[str, float] = {}
        self._norm_contradiction = False
        # A Courant line is a transient solver's signature. S6 and S7 are
        # steady-solve rules and are scoped off once one appears; see
        # _check_series for the measurement behind that.
        self._transient = False

    def feed(self, step: str, line: str) -> None:
        if self.FPE.search(line):
            self._raise(Anomaly("fpe", step, line.strip(), "floating point exception"))
            return
        if self.NAN.search(line) and ("Solving for" in line or "= nan" in line.lower()):
            self._raise(Anomaly("nan", step, line.strip(), "NaN in solver output"))
            return
        match = self.COURANT.search(line)
        if match:
            self._transient = True
            self._courant_step(step, float(match.group(2)), line)
            return
        match = self.DELTAT.match(line.strip())
        if match:
            self._time_steps.add(float(match.group(1)))
            return
        match = self.RESIDUAL.search(line)
        if match:
            self._residual(step, match.group(1), float(match.group(2)), line)
            return
        match = self.RESIDUAL_NORM.match(line)
        if match:
            self._residual_norm(step, match.group(1),
                                match.group(2) or match.group(3), line)
            return
        bound = classify_bound_line(line)
        if bound:
            self._bound(step, bound, line)
            return
        if self.novel and self.WARNING.search(line):
            key = re.sub(r"[0-9.eE+-]+", "#", line.strip())[:120]
            if key not in self._seen_warnings:
                self._seen_warnings.add(key)
                self.novel_observations.append(line.strip())
                self._raise(Anomaly("novel-warning", step, line.strip(),
                                    "first occurrence on an unfamiliar case"))

    def _bound(self, step: str, bound: dict[str, Any], line: str) -> None:
        """Clipping messages, split by which end of the range was hit (S4, S10a).

        A field held up off its floor is the ordinary case and stays the S4
        watch it always was. A field dragged down off its ceiling is S10a: an
        eddy frequency at 1e+16 has left the physical range, and everything
        integrated from the field afterwards inherits that.
        """
        if bound["direction"] != CEILING:
            self._raise(Anomaly("bounding", step, line.strip(),
                                "a variable was clipped to stay physical"))
            return
        finding = detect_ceiling_clip(line)
        field = bound["field"]
        self._ceiling_clipped.add(field)
        if self._collapsed.get(field) == "flag":
            self._escalate_collapse(step, field, line)
        self._raise(Anomaly(
            "ceiling-clip", step, line.strip(),
            f"{field} was clipped at the top of its range "
            f"({finding['bound']:.3g}), so the field has left the physical "
            f"range; {finding['action']}",
            severity=finding["severity"]))

    def _residual_norm(self, step: str, field: str, raw: str,
                       line: str) -> None:
        """Unnormalised residual norms printed at the end of a run (S10c).

        This block is the honest one: it is not divided by anything that can
        blow up with the field, so it can contradict a normalised residual
        that read as converged. The solver's own total is skipped, since it is
        the maximum over the fields already collected.
        """
        if field.lower() == "total":
            return
        try:
            parts = [abs(float(token)) for token in raw.split()]
        except ValueError:
            return
        if not parts:
            return
        self._residual_norms[field] = max(parts)
        if self._norm_contradiction:
            return
        finding = detect_residual_norm_contradiction(self._residual_norms)
        if not finding:
            return
        self._norm_contradiction = True
        self._raise(Anomaly(
            "residual-norm-contradiction", step, line.strip(),
            f"the {finding['field']} residual norm exceeds the "
            f"{finding['reference_field']} norm by "
            f"{finding['orders_of_magnitude']:.1f} orders of magnitude, so the "
            f"equations were never jointly satisfied whatever the reported "
            f"residuals said; {finding['action']}",
            severity=finding["severity"]))

    def _escalate_collapse(self, step: str, field: str, line: str) -> None:
        """A collapsed residual on a field that also hit its ceiling is fatal."""
        self._collapsed[field] = "fatal"
        self._raise(Anomaly(
            "normalisation-collapse", step, line.strip(),
            f"{field} reads converged only because its own divergence "
            f"inflated the quantity its residual is divided by; the field is "
            f"clipped at the top of its range at the same time; "
            f"{DIVERGENCE_ACTION}",
            severity="fatal"))

    def _residual(self, step: str, field: str, residual: float, line: str) -> None:
        self._latest[field] = residual
        series = self._series.setdefault(field, [])
        series.append(residual)
        if len(series) > self.STALL_WINDOW:
            series.pop(0)
        self._iterations[field] = self._iterations.get(field, 0) + 1
        self._check_collapse(step, field, line)
        self._check_series(step, field, line)
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

    def _oscillation_applies(self, field: str) -> bool:
        """Whether S7 is entitled to speak about this field yet.

        MEASURED 2026-07-31, and the reason this gate exists. S7 as written
        fires on 68 of the lab's 106 archived steady solver logs and reaches
        fatal on 65 of them. Every one of those runs completed and its results
        are on the record. Four tightenings were measured and none rescued it:
        requiring the residual level to stop improving (68 logs), requiring the
        finding to persist a full window (40), measuring growth against a 200
        iteration baseline (59), and raising the growth factor to 4x (23).

        The cause is that a converged field sits flat with small noise, and the
        ratio of one noise envelope to the next is a coin toss that a run of
        thousands of iterations will win somewhere. The proposal's own words
        say the rule is about oscillation "around a stalled residual", and that
        is the gate: the field must still be above the target the solve is
        aiming for. S6 has always been gated this way and does not
        false-positive. So S7 now needs the same ``residual_target``, and it
        stays silent on any field that has reached it.

        RECORDED WEAKNESS: this gate is reasoning from the proposal's wording
        plus S6's measured behaviour, not a measurement of its own. The
        archived logs do not record the residual target each run was aiming
        for, so the corpus cannot be replayed with the gate in place. S7 is the
        weakest rule in the set and is filed to the owner as such.
        """
        if self.residual_target is None:
            return False
        latest = self._latest.get(field)
        return latest is not None and latest > self.residual_target

    def _check_collapse(self, step: str, field: str, line: str) -> None:
        """Normalisation collapse S10b, raised once per field per episode.

        Unlike S6 and S7 this rule is NOT scoped to steady solves. It was
        measured over every archived log the lab holds, transient runs
        included, and fires on exactly one of them. A residual that reads
        converged because its own field diverged is a hazard in either regime,
        and there is no measured reason to switch it off in one of them.
        """
        if field in self._collapsed:
            return
        peers = [value for name, value in self._latest.items()
                 if name != field]
        finding = detect_normalisation_collapse(
            self._series[field], peer_residuals=peers,
            window=self.COLLAPSE_WINDOW)
        if not finding:
            return
        if field in self._ceiling_clipped:
            self._collapsed[field] = "flag"
            self._escalate_collapse(step, field, line)
            return
        self._collapsed[field] = finding["severity"]
        self._raise(Anomaly(
            "normalisation-collapse", step, line.strip(),
            f"{field} has read at or below {finding['floor']:.0e} for "
            f"{finding['iterations_at_floor']} iterations after peaking at "
            f"{finding['peak']:.3g}, while other fields are still working; a "
            f"residual is a ratio, and this one collapsed rather than "
            f"converged; {finding['action']}",
            severity=finding["severity"]))

    def _check_series(self, step: str, field: str, line: str) -> None:
        """Series-level rules S6 and S7 over the long residual history.

        A stall or a divergence is a state, not an event: each is raised once
        per field per episode, with oscillatory divergence raised again only
        when it escalates from flag to fatal.

        Both rules are scoped to steady solves, which is the regime their
        evidence comes from. In a transient run the residual series restarts
        at every time step and the outer correctors drive it high and low in
        turn, which is alternation with a moving envelope by construction.
        Measured on the lab's four archived transient runs: S7 fired 5, 5, 6
        and 9 times on runs that all completed healthily, every one of them a
        false positive. The transient equivalent of these rules is S8.
        """
        if self._transient:
            return
        series = self._series[field]
        if self._oscillation_applies(field):
            oscillation = detect_oscillatory_divergence(
                series, window=self.OSCILLATION_WINDOW)
            if oscillation is None:
                self._oscillating.pop(field, None)
            elif self._oscillating.get(field) != oscillation["severity"]:
                previous = self._oscillating.get(field)
                self._oscillating[field] = oscillation["severity"]
                if previous != "fatal":  # never downgrade an already fatal episode
                    self._raise(Anomaly(
                        "oscillatory-divergence", step, line.strip(),
                        f"{field} residual oscillation envelope grew "
                        f"{oscillation['growth']:.2f}x over the last "
                        f"{oscillation['window']} iterations; "
                        f"{oscillation['action']}",
                        severity=oscillation["severity"]))
        if self.residual_target is None or field in self._stalled:
            return
        stall = detect_residual_stall(
            series, target=self.residual_target, window=self.STALL_WINDOW,
            iterations_done=self._iterations[field],
            iteration_cap=self.iteration_cap)
        if stall:
            self._stalled.add(field)
            self._raise(Anomaly(
                "residual-stall", step, line.strip(),
                f"{field} residual sits at {stall['median_late']:.3g}, above "
                f"the target {stall['target']:.3g}, having improved only "
                f"{stall['improvement']:.2f}x over the last {stall['window']} "
                f"iterations; {stall['action']}",
                severity=stall["severity"]))

    def _courant_step(self, step: str, max_courant: float, line: str) -> None:
        """Courant excursion rule S8 over the reported per-step maximum.

        Like a stall, an excursion is a state rather than an event: it is
        raised once per episode and again only when it escalates to fatal.
        A run whose time step is being adjusted is judged on the limit alone;
        the monotone-growth branch applies only where the step is held fixed,
        because an adaptive stepper raising the Courant number back toward its
        own target is the stepper working, not the flow running away.
        """
        if self.courant_limit is None:
            return
        self._courant.append(max_courant)
        if len(self._courant) > self.COURANT_WINDOW * 4:
            self._courant.pop(0)
        finding = detect_courant_excursion(
            self._courant, limit=self.courant_limit,
            window=self.COURANT_WINDOW,
            fixed_time_step=len(self._time_steps) <= 1)
        if finding is None or finding["severity"] == self._courant_severity:
            return
        if self._courant_severity == "fatal":
            return  # never downgrade an episode already fatal
        self._courant_severity = finding["severity"]
        self._raise(Anomaly(
            "courant-excursion", step, line.strip(),
            f"maximum Courant number reached {finding['peak']:.3g} against a "
            f"case limit of {finding['limit']:.3g} "
            f"({finding['reason']}); {finding['action']}",
            severity=finding["severity"]))

    def check_wall_time(self, step: str, solver_kind: str, wall_seconds: float,
                        *, envelope=None, ledger_path=None,
                        flag_multiple: float = FLAG_MULTIPLE,
                        ) -> dict[str, Any] | None:
        """Wall-time excursion rule S9 against the learned ledger envelope.

        Call once per completed solver run with its measured wall time. A run
        beyond ``flag_multiple`` times the learned 99th percentile for its
        solver kind raises a wall-time-excursion anomaly (severity flag,
        escalating to fatal at 100x); the classification is returned so the
        caller can keep the excursion as a named field on the record. The
        record itself is never altered.

        The default is the threshold the owner approved, taken from
        ``FLAG_MULTIPLE`` rather than restated here. This entry point carried
        its own literal 20.0 for five days after the shared constant was
        corrected to the approved 10.0, so every caller that took the default
        was judging on a threshold nobody approved.
        """
        finding = classify_wall_time(
            solver_kind, wall_seconds, envelope,
            flag_multiple=flag_multiple, ledger_path=ledger_path)
        if finding:
            self._raise(Anomaly(
                "wall-time-excursion", step,
                f"{solver_kind} wall time {wall_seconds:.1f} s",
                f"wall time {wall_seconds:.1f} s is {finding['multiple']:.0f}x "
                f"the learned 99th percentile {finding['p99']:.2f} s for "
                f"solver kind {solver_kind} ({finding['samples']} runs); "
                f"{finding['action']}",
                severity=finding["severity"]))
        return finding

    def _raise(self, anomaly: Anomaly) -> None:
        self.anomalies.append(anomaly)
        key = (anomaly.kind, anomaly.step)
        seen = self._reported.get(key, 0) + 1
        self._reported[key] = seen
        fatal = anomaly.kind in {"nan", "fpe"} or anomaly.severity == "fatal"
        if seen > self.REPORT_LIMIT and not fatal:
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
            "fatal": any(item.kind in {"nan", "fpe"} or item.severity == "fatal"
                         for item in self.anomalies),
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
    """Convergence curve with a rolling ±2σ envelope — dark GUI theme, mathtext.

    The report figure reads as part of the control room, not a default-white
    matplotlib chart: the panel palette, typeset $C_d$/$C_\\ell$ labels, a titled
    frame, a legend, and one annotated key value, sized to span the report
    column (G10).
    """
    from . import plot_theme as _t
    plt = _t._pyplot()
    if plt is None:
        return None

    means, los, his = [], [], []
    for i in range(len(series)):
        chunk = series[max(0, i - window + 1): i + 1]
        m = sum(chunk) / len(chunk)
        s = (sum((v - m) ** 2 for v in chunk) / (len(chunk) - 1)) ** 0.5 if len(chunk) > 1 else 0.0
        means.append(m); los.append(m - 2 * s); his.append(m + 2 * s)

    label = _t.metric_label(name)
    fig, ax = plt.subplots(figsize=(11.4, 4.6), dpi=150)
    # Legend names the trace and its envelope only. "Rolling mean" is banned
    # from every coefficient plot (Katie: it must never read as a statistical
    # sampling product); the settling line itself stays, unlabeled.
    ax.fill_between(iterations, los, his, color=_t.LIVE, alpha=0.16, linewidth=0,
                    label=r"$\pm 2\sigma$ envelope")
    ax.plot(iterations, series, color=_t.LIVE, linewidth=0.9, alpha=0.4,
            label="coefficient history")
    ax.plot(iterations, means, color=_t.LIVE, linewidth=2.4,
            label="_nolegend_")
    final = envelope_statistics(series)
    if final:
        ax.annotate(
            f"{label} = {final['value']:.4g} $\\pm$ {2 * final['sigma']:.2g} (95%)",
            xy=(iterations[-1], means[-1]), xytext=(-8, 16),
            textcoords="offset points", ha="right", fontsize=12,
            color=_t.INK, weight="bold",
        )
    _t.style_axes(ax, "iteration", label,
                  f"{label} convergence with uncertainty envelope")
    leg = ax.legend(frameon=False, fontsize=10.5, labelcolor=_t.INK, loc="best")
    for text in leg.get_texts():
        text.set_color(_t.INK)
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
        self.histories: dict[str, dict[str, list[float]]] = {}
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

    def _run_step(self, name: str, command: str, timeout: float = 3600.0,
                  line_hook=None) -> StepResult:
        """Run one case step inside WSL, streaming output through the monitor.

        ``line_hook`` (optional) sees every solver output line as it streams —
        the live-telemetry tap that lets a workflow narrate quantities (e.g.
        the drag coefficient) while the solver is still marching.
        """
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
                if line_hook:
                    try:
                        line_hook(line)
                    except Exception:
                        pass   # telemetry must never take down a solve
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

    def enforce_boundary_skewness(self, value: float = 4.0) -> bool:
        """Tighten the staged case's snappyHexMesh boundary-skewness gate.

        The stock tutorial allowance (20) lets a handful of boundary faces
        through that checkMesh then flags above the 4.0 guidance; appending
        the entry after the dictionary's include makes the tighter value win
        and snappy smooths those faces out during meshing. Measured on the
        motorbike (2026-07-24): max skewness 8.94 with the stock gate, 3.99
        with this one, at an unchanged cell budget.
        """
        gated = self._wsl(
            f"cd {self.remote_case} && test -f system/meshQualityDict && "
            f"printf 'maxBoundarySkewness {value:g};\\n' >> system/meshQualityDict && "
            f"grep -q 'maxBoundarySkewness {value:g};' system/meshQualityDict && "
            f"echo GATED", timeout=120)
        return "GATED" in gated.stdout

    def _mesh_cache_dir(self, cache_key: str) -> str:
        # A filesystem-safe key so a body name never escapes the cache root.
        safe = re.sub(r"[^A-Za-z0-9._-]", "_", cache_key)
        return f"{MESH_CACHE_ROOT}/{safe}"

    def cached_mesh_available(self, cache_key: str) -> bool:
        """True when a snapped mesh for this body is already cached (warm run)."""
        if os.environ.get("CERTONOMOUS_MESH_CACHE") == "0":
            return False
        cache = self._mesh_cache_dir(cache_key)
        # Accept the gzipped spelling too. OpenFOAM writes polyMesh files
        # either way and reads both; testing only for the plain name makes a
        # gzipped mesh look absent, so the cache reports a miss and the case
        # silently re-meshes and re-solves from cold.
        probe = self._wsl(
            f"( test -f {cache}/polyMesh/points || test -f {cache}/polyMesh/points.gz ) && "
            f"( test -f {cache}/polyMesh/owner  || test -f {cache}/polyMesh/owner.gz  ) "
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

    # -- solve-result cache --------------------------------------------------
    # Mirrors the mesh cache one stage later: a completed steady solve's force
    # history and final fields, restored into a case so postprocessing and the
    # field paint read them exactly as if the solver had just finished.

    def _solve_cache_dir(self, cache_key: str) -> str:
        safe = re.sub(r"[^A-Za-z0-9._-]", "_", cache_key)
        return f"{SOLVE_CACHE_ROOT}/{safe}"

    def _solved_time_dirs(self) -> list[str]:
        """Names of this case's solved time directories (integers above 0).

        Listed plainly and filtered in Python: shell globs inside command
        substitution do not survive the Windows-to-WSL quoting stack on this
        machine, so no ``$(...)`` may carry a glob (the bug that silently
        left the solve cache empty).
        """
        listing = self._wsl(f"cd {self.remote_case} && ls 2>/dev/null",
                            timeout=120).stdout.split()
        return sorted((name for name in listing
                       if re.fullmatch(r"[0-9]+", name) and name != "0"),
                      key=int)

    def restore_cached_solve(self, cache_key: str) -> bool:
        """Restore a completed solve (postProcessing + final fields) into the
        case. Returns True on a hit; False means the case must solve fresh."""
        if os.environ.get("CERTONOMOUS_SOLVER_CACHE") == "0":
            return False
        cache = self._solve_cache_dir(cache_key)
        latest = self._wsl(f"cat {cache}/DONE 2>/dev/null",
                           timeout=120).stdout.strip()
        if not re.fullmatch(r"[0-9]+", latest or ""):
            return False
        restored = self._wsl(
            f"test -f {cache}/DONE && "
            f"cp -r {cache}/postProcessing {self.remote_case}/ && "
            f"rm -rf {self.remote_case}/{latest} && "
            f"cp -r {cache}/{latest} {self.remote_case}/{latest} && "
            f"echo RESTORED", timeout=600)
        return "RESTORED" in restored.stdout

    def save_solve_to_cache(self, cache_key: str) -> None:
        """Store this case's finished solve for silent reuse next run."""
        if os.environ.get("CERTONOMOUS_SOLVER_CACHE") == "0":
            return
        solved = self._solved_time_dirs()
        if not solved:
            return
        latest = solved[-1]
        cache = self._solve_cache_dir(cache_key)
        self._wsl(
            f"cd {self.remote_case} && test -d postProcessing && "
            f"rm -rf {cache} && mkdir -p {cache} && "
            f"cp -r postProcessing {cache}/ && "
            f"cp -r {latest} {cache}/{latest} && "
            f"printf {latest} > {cache}/DONE || true", timeout=600)

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

    # -- grid-refinement rungs ------------------------------------------------
    # A refinement rung is the SAME case with one mesh knob changed: cloned
    # from the production case, remeshed at a cheaper setting, solved shorter.

    def clone_case_from(self, source_remote_case: str) -> bool:
        """Stage this case as a copy of another case, stripped back to inputs.

        Keeps the geometry, dictionaries, and initial fields; drops the mesh,
        any solved time directories, and postProcessing so the rung meshes and
        solves from scratch with only its own knob changed. Solved time
        directories are identified in Python, never with a shell loop: the
        Windows-to-WSL quoting stack mangles globs in compound constructs.
        """
        cloned = self._wsl(
            f"rm -rf {self.remote_case} && mkdir -p {RUN_ROOT} && "
            f"cp -r {source_remote_case} {self.remote_case} && "
            f"cd {self.remote_case} && "
            f"rm -rf constant/polyMesh postProcessing processor* log.* && "
            f"test -f system/controlDict && echo CLONED", timeout=600)
        if "CLONED" not in cloned.stdout:
            return False
        solved = self._solved_time_dirs()
        if solved:
            doomed = " ".join(solved)
            self._wsl(f"cd {self.remote_case} && rm -rf {doomed}", timeout=300)
        return True

    def set_refinement_levels(self, *, feature: int, surface_lo: int,
                              surface_hi: int, region: int) -> bool:
        """Point snappyHexMesh at a different castellated refinement level.

        This is the knob that genuinely changes the mesh (background density
        stays put; surface and region refinement move), and it exists in both
        the tutorial dictionary and the generated one. The seds are tolerant
        of either spelling (1E15/1e15, any current level numbers).
        """
        changed = self._wsl(
            f"cd {self.remote_case} && "
            f"sed -i -E 's/level \\([0-9]+ [0-9]+\\);/level ({surface_lo} {surface_hi});/' "
            f"system/snappyHexMeshDict && "
            f"sed -i -E 's/level [0-9]+;/level {feature};/' system/snappyHexMeshDict && "
            f"sed -i -E 's/levels \\(\\([0-9eE+.]+ [0-9]+\\)\\);/levels ((1e15 {region}));/' "
            f"system/snappyHexMeshDict && "
            f"grep -q 'level ({surface_lo} {surface_hi});' system/snappyHexMeshDict && "
            f"echo LEVELS", timeout=120)
        return "LEVELS" in changed.stdout

    def scale_background_divisions(self, factor: float) -> tuple | None:
        """Scale the blockMesh division counts by ``factor`` (second knob).

        Used only when the castellated level floors out and two rungs would
        otherwise share a mesh. Returns (old, new) division triples, or None
        when the dictionary could not be edited or the scaling changed
        nothing (the caller must then refuse to report a study).
        """
        raw = self._wsl(f"cat {self.remote_case}/system/blockMeshDict",
                        timeout=120).stdout
        match = re.search(r"hex \(([^)]*)\) \((\d+) (\d+) (\d+)\)", raw)
        if not match:
            return None
        old = tuple(int(match.group(i)) for i in (2, 3, 4))
        new = tuple(max(4, int(round(n * float(factor)))) for n in old)
        if new == old:
            return None
        # Rebuild the exact division triple textually, stage the edited file
        # on the Windows side, and copy it in: multi-line heredocs do not
        # survive the Windows-to-WSL quoting stack reliably.
        edited = raw.replace(
            f"({old[0]} {old[1]} {old[2]})", f"({new[0]} {new[1]} {new[2]})", 1)
        staging = self.out_root / "blockMeshDict.scaled"
        staging.write_text(edited, errors="replace")
        wsl_staging = str(staging).replace("C:", "/mnt/c").replace("\\", "/")
        write = self._wsl(
            f"cp '{wsl_staging}' {self.remote_case}/system/blockMeshDict && "
            f"grep -q '({new[0]} {new[1]} {new[2]})' "
            f"{self.remote_case}/system/blockMeshDict && echo SCALED", timeout=120)
        return (old, new) if "SCALED" in write.stdout else None

    def reference_area(self) -> float | None:
        """The Aref this case's force coefficients divide by, read from the
        case itself (never assumed): the drag-area comparison must use exactly
        the area the solver used."""
        raw = self._wsl(
            f"grep -rh 'Aref' {self.remote_case}/system 2>/dev/null | head -3",
            timeout=120).stdout
        match = re.search(r"Aref\s+([0-9.eE+-]+)\s*;", raw)
        try:
            return float(match.group(1)) if match else None
        except (TypeError, ValueError):
            return None

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
            # The destination the launch prefix's shell can reach: on native
            # Linux the local path is already reachable as-is (no wsl hop at
            # all, so no ``wslpath`` binary exists to shell out to -- that
            # call silently failed and left no file, the same class of bug
            # host_launch_prefix already fixed for the launch prefix itself).
            # On the Windows/WSL host the local path is a Windows path and
            # needs the same manual C:\ -> /mnt/c/ translation used elsewhere
            # in this codebase for exactly this reason.
            wsl_local = (str(local).replace("C:", "/mnt/c").replace("\\", "/")
                        if WSL else str(local))
            self._wsl(f"cp '{remote}' '{wsl_local}'")
            history = parse_coefficient_history(local.read_text(errors="replace"))
            iterations = history.get("Time", [])
            for name in coefficients:
                series = history.get(name)
                if not series or not iterations:
                    continue
                stats = envelope_statistics(series)
                results[name] = stats
                # Keep the full marching history so the workflow can stream the
                # coefficient being computed iteration by iteration (live trace).
                self.histories[name] = {"iterations": list(iterations[:len(series)]),
                                        "series": list(series)}
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
            notes.append("Fatal numerical anomaly (NaN/FPE): results untrustworthy; "
                         "halve relaxation factors or revisit mesh quality before rerun.")
        if monitor["by_kind"].get("residual-spike"):
            notes.append(f"{monitor['by_kind']['residual-spike']} residual spike(s): "
                         "inspect the flagged iterations; consider tighter relaxation.")
        if monitor["by_kind"].get("bounding"):
            notes.append("Bounded turbulence variables observed: normal in startup, "
                         "suspect if persisting past ~100 iterations.")
        if self.mesh_stats.get("max_non_orthogonality", 0) > 70:
            notes.append("Max non-orthogonality > 70°: add nonOrthogonalCorrectors "
                         "or improve the mesh in flagged regions.")
        for name, stats in self.results.items():
            if stats and stats["value"] != 0 and abs(2 * stats["sigma"] / stats["value"]) > 0.05:
                notes.append(f"{name} envelope exceeds 5% of its value; per lesson "
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
        non_ortho_s = f"{non_ortho:.1f}°" if non_ortho is not None else "n/a"
        skew_s = f"{skew:.2f}" if skew is not None else "n/a"
        lines = [
            f"# Certonomous Head Engineer report: {self.case_name}",
            "",
            "| Section | Result |",
            "|---|---|",
            f"| Geometry | {self.geometry_report.get('surface', 'n/a')}, "
            f"{'closed, ' if self.geometry_report.get('closed') else ''}"
            f"{', '.join(self.geometry_report.get('issues', [])) or 'no issues found'} |",
            f"| Mesh | {int(self.mesh_stats.get('cells', 0))} cells, "
            f"max non-ortho {non_ortho_s}, "
            f"max skew {skew_s}, "
            f"{'OK' if self.mesh_stats.get('mesh_ok') else 'check flags'} |",
            f"| Steps | " + "; ".join(
                f"{s.name}: {s.seconds:.0f} s ({'ok' if s.status == 0 else 'FAIL'})"
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
        message["Subject"] = f"Certonomous report: {self.case_name}"
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
