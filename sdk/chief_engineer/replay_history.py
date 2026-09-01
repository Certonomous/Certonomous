#!/usr/bin/env python3
"""Per-iteration solve history, read off a landed OpenFOAM run tree.

WHAT THIS IS FOR. The solver stage of a demo act replays a completed run's
own monitors at accelerated pace instead of computing. Everything it puts on
screen -- the iteration counter, the residuals, the lift and drag curves, the
elapsed clock -- is a value this module read off disk. Nothing is modelled,
interpolated, smoothed or invented.

WHICH MAKES THIS A MEASUREMENT SCRIPT, NOT A DISPLAY HELPER. A reader that
silently returns nothing, or reads a neighbouring column, produces a beautiful
moving plot of garbage, and a moving plot of garbage is more convincing than a
static one. So every channel below is paired with a PLANT (CLAUDE.md rule 3):
a known value written into a copy of the real file, read back through the same
public function, and asserted. A reader that cannot see its plant REFUSES. It
does not fall back, does not warn, and does not return a zero.


=============================================================================
THE PRESSURE DOUBLE-SOLVE.  READ THIS BEFORE CHANGING ANY PARSING BELOW.
=============================================================================

These cases run ``nNonOrthogonalCorrectors 1``. Pressure is therefore solved
TWICE per SIMPLE iteration and every other field ONCE. Measured on
``verification/runs/JF1_jet_flap/JF1_L1_BLOWN_CMU020_A0/log.simpleFoam``:

    8000 ``Time =`` lines
    8000 ``Solving for Ux``      8000 ``Solving for Uy``
    8000 ``Solving for k``       8000 ``Solving for omega``
   16000 ``Solving for p``

A naive "last match per field" reader -- the obvious way to write this, and
the way it was written once tonight -- takes the SECOND corrector pass for p.
That is not the iteration's residual. It is the residual of a correction
applied after the iteration's pressure equation was already solved, it is
roughly an order of magnitude smaller, and quoting it makes a calculation look
converged when it is not. That error is on the lab record as L-419.

Measured at the final iteration of that same case:

    GAMG:  Solving for p, Initial residual = 2.323244216e-05   <- pass 1
    GAMG:  Solving for p, Initial residual = 1.176285151e-06   <- pass 2

WHAT THIS MODULE DOES ABOUT IT, EXPLICITLY:

  * It parses the log into TIME STEPS first, and only then reads solve lines
    WITHIN a step. It never scans the whole file for a field name.
  * For every step it asserts the number of ``Solving for p`` lines equals
    ``1 + nNonOrthogonalCorrectors``, read from the case's OWN
    ``system/fvSolution``. A case whose log disagrees with its own settings is
    refused rather than guessed at.
  * IT TAKES PASS 1 -- index 0 within the step. Pass 1 is the residual of the
    pressure equation as the iteration posed it. Pass 2 measures the
    non-orthogonal correction, which is a different question, and is the
    number that must NOT go on a convergence plot.
  * The plant for this channel writes TWO DIFFERENT sentinels into the two p
    lines of one iteration and asserts the reader returns the FIRST. A
    last-match reader returns the second sentinel and is caught on the spot.

SECOND, INDEPENDENT CHANNEL. OpenFOAM's own ``solverInfo`` function object
writes ``postProcessing/contErr/<t>/solverInfo.dat``: exactly one row per time
step, with a ``p_initial`` column. Measured across all 8000 iterations of
JF1_L1_BLOWN_CMU020_A0, its ``p_initial`` equals the log's FIRST p pass in
8000 rows and the second in 0. This module reads the log as the canonical
source and uses solverInfo purely as an ASSERT-EQUAL cross-check that refuses
on disagreement. It is a control, not a second implementation: there is one
number, and a second channel whose only job is to disagree if the first is
wrong.

  Honest limit of that cross-check: in that case the first pass happened to be
  the LARGER of the two passes in every one of the 8000 iterations, so this
  data cannot distinguish "solverInfo keeps the first solve" from "solverInfo
  keeps the largest solve". That is exactly why the log, where pass order is
  unambiguous, is canonical and solverInfo is only the control.


DOWN-SAMPLING. Twenty thousand points do not fit on a plot and do not need to.
Frames are selected by STRIDE over the real rows -- every k-th row, verbatim,
plus always the exact first and last row. Values are never averaged, smoothed,
interpolated or clipped. Each frame carries the source row index it came from
and each history carries its stride, so any frame on screen can be traced back
to a line of the log. Because a stride can step over a spike, each frame also
carries the true min and max of the rows it stepped over; that is additional
measured data, not a smoothing of the sampled value.
"""

from __future__ import annotations

import math
import re
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Sequence

__all__ = [
    "ReaderRefused", "RunHistory", "SweepPoint", "Frame",
    "read_run_history", "read_solve_history", "read_coefficient_history",
    "read_run_status", "read_non_orthogonal_correctors",
    "downsample", "self_check",
]


class ReaderRefused(RuntimeError):
    """A reader could not prove it was reading what it claimed to read."""


#: The plant. Chosen so it cannot be mistaken for a residual, a coefficient or
#: an elapsed time, and so the two pressure passes get DIFFERENT sentinels.
PLANT = 1.234e-03
PLANT_SECOND_PASS = 5.678e-03

#: Fields whose residual the solver stage shows. ``p`` is listed like any
#: other and is emphatically not read like any other; see the module preamble.
RESIDUAL_FIELDS = ("Ux", "Uy", "p", "k", "omega")

#: Owner-stated instance rate. The box cannot read its own billing
#: (COMPUTE_BUDGET_CHARTER §5), so any currency figure derived from this is
#: DERIVED, NOT MEASURED, and every carrier of it below says so.
USD_PER_CORE_HOUR = 0.0513


# ===========================================================================
# 0. Case settings: how many times is pressure solved per iteration?
# ===========================================================================

_CORRECTOR_RE = re.compile(r"\bnNonOrthogonalCorrectors\s+(\d+)\s*;")


def read_non_orthogonal_correctors(case_dir: Path | str) -> int:
    """``nNonOrthogonalCorrectors`` from the case's own ``system/fvSolution``.

    Read rather than assumed because it is the whole basis on which this
    module decides how many ``Solving for p`` lines an iteration is allowed to
    have. Hard-coding 2 here would make the p-pass assertion vacuous on any
    case that does not run 1 corrector.
    """
    path = Path(case_dir) / "system" / "fvSolution"
    if not path.is_file():
        raise ReaderRefused(f"no fvSolution at {path}; cannot know how many "
                            f"times pressure is solved per iteration")
    text = path.read_text(encoding="utf-8", errors="replace")
    found = _CORRECTOR_RE.search(text)
    if found is None:
        raise ReaderRefused(
            f"{path} does not state nNonOrthogonalCorrectors. Refusing rather "
            f"than assuming a value: the assumption decides which pressure "
            f"pass every residual on screen comes from (L-419).")
    return int(found.group(1))


# ===========================================================================
# 1. The solver log, parsed as time steps
# ===========================================================================

_TIME_RE = re.compile(r"^Time\s*=\s*(\S+)\s*$")
_SOLVE_RE = re.compile(
    r"Solving for (\w+),\s*Initial residual = ([-\d.eE+]+),"
    r"\s*Final residual = ([-\d.eE+]+)")
_EXEC_RE = re.compile(
    r"^ExecutionTime\s*=\s*([-\d.eE+]+)\s*s\s+ClockTime\s*=\s*([-\d.eE+]+)\s*s")


@dataclass
class _Step:
    """One SIMPLE iteration as the log records it."""
    time: str
    #: field name -> initial residuals, IN THE ORDER THE LOG PRINTS THEM.
    #: A list, not a scalar, precisely so the p double-solve is visible to the
    #: caller rather than collapsed here.
    solves: dict = field(default_factory=dict)
    execution_s: float | None = None
    clock_s: float | None = None


def _parse_steps(log_path: Path) -> list[_Step]:
    if not log_path.is_file():
        raise ReaderRefused(f"no solver log at {log_path}")
    steps: list[_Step] = []
    current: _Step | None = None
    for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
        stamp = _TIME_RE.match(line)
        if stamp:
            current = _Step(time=stamp.group(1))
            steps.append(current)
            continue
        if current is None:
            # Header noise before the first Time line. Never a solve line in
            # a healthy log; if one appears here it is dropped, and the
            # per-step count assertion below is what would catch it.
            continue
        solve = _SOLVE_RE.search(line)
        if solve:
            current.solves.setdefault(solve.group(1), []).append(
                float(solve.group(2)))
            continue
        timing = _EXEC_RE.match(line)
        if timing:
            current.execution_s = float(timing.group(1))
            current.clock_s = float(timing.group(2))
    if not steps:
        raise ReaderRefused(f"{log_path} carries no 'Time =' lines")
    return steps


def read_solve_history(case_dir: Path | str,
                       fields: Sequence[str] = RESIDUAL_FIELDS,
                       *, cross_check: bool = True) -> dict:
    """Initial residual of each field at each iteration, plus elapsed time.

    Returns ``{"iterations": [...], "elapsed_s": [...], "residuals":
    {field: [...]}, "p_pass_taken": 1, "p_passes_per_iteration": n, ...}``.

    THE PRESSURE RULE, STATED AT THE PLACE IT IS APPLIED: for every field this
    function takes the FIRST ``Solving for <field>`` line inside the time step,
    never the last match in the file. For fields solved once the two are the
    same. For ``p``, solved ``1 + nNonOrthogonalCorrectors`` times, they are
    not, and the last match is the non-orthogonal corrector pass, which is not
    the iteration's residual (L-419). Taking index 0 is therefore not an
    arbitrary tie-break; it is the choice of which physical quantity is shown.
    """
    case = Path(case_dir)
    log_path = case / "log.simpleFoam"
    steps = _parse_steps(log_path)
    correctors = read_non_orthogonal_correctors(case)
    expect_p = 1 + correctors

    iterations: list[float] = []
    elapsed: list[float] = []
    residuals: dict[str, list[float]] = {name: [] for name in fields}

    for step in steps:
        for name in fields:
            passes = step.solves.get(name)
            if not passes:
                raise ReaderRefused(
                    f"{log_path}: time step {step.time} has no 'Solving for "
                    f"{name}' line. Refusing rather than carrying a gap that "
                    f"would draw as a straight segment on a residual plot.")
            if name == "p" and len(passes) != expect_p:
                raise ReaderRefused(
                    f"{log_path}: time step {step.time} has {len(passes)} "
                    f"'Solving for p' lines but system/fvSolution sets "
                    f"nNonOrthogonalCorrectors {correctors}, so exactly "
                    f"{expect_p} were expected. The log and the case settings "
                    f"disagree about how pressure was solved, and this reader "
                    f"will not guess which pass is the iteration's residual.")
            # INDEX 0 -- the first pass. See the docstring above and the
            # module preamble. Do not change this to passes[-1].
            residuals[name].append(passes[0])
        if step.execution_s is None:
            raise ReaderRefused(
                f"{log_path}: time step {step.time} has no ExecutionTime "
                f"line, so the elapsed clock for that frame is unknown. The "
                f"clock on screen is the run's real wall time and will not be "
                f"filled in by interpolation.")
        iterations.append(float(step.time))
        elapsed.append(step.execution_s)

    history = {
        "case": str(case),
        "log": str(log_path),
        "iterations": iterations,
        "elapsed_s": elapsed,
        "residuals": residuals,
        "n": len(iterations),
        "p_passes_per_iteration": expect_p,
        "p_pass_taken": 1,
        "p_pass_rule": (
            "first pass of the iteration; passes 2..n are the "
            "non-orthogonal corrector and are not the iteration's residual"),
        "solver_info_cross_check": "not run",
        "solver_info_path": None,
    }
    if cross_check and "p" in fields:
        sentence, path = _cross_check_solver_info(
            case, iterations, residuals["p"])
        history["solver_info_cross_check"] = sentence
        history["solver_info_path"] = path
    return history


def _solver_info_path(case_dir: Path) -> Path | None:
    root = Path(case_dir) / "postProcessing" / "contErr"
    if not root.is_dir():
        return None
    candidates = sorted(p for p in root.glob("*/solverInfo.dat") if p.is_file())
    if not candidates:
        return None
    if len(candidates) > 1:
        raise ReaderRefused(
            f"{root} holds {len(candidates)} solverInfo.dat files, one per "
            f"restart. Refusing: silently taking one of them would cross-check "
            f"part of the run against all of it. Files: "
            f"{[str(p) for p in candidates]}")
    return candidates[0]


def _cross_check_solver_info(case_dir: Path, iterations: list[float],
                            p_first_pass: list[float]) -> tuple:
    """Assert OpenFOAM's own per-iteration record agrees with the log.

    This is a CONTROL, not a second reader. There is one canonical pressure
    residual -- the log's first pass -- and this function's only job is to
    refuse if an independently written file disagrees with it. Two channels
    that agree on every row of the run are much stronger evidence that the
    right column was read than either channel alone; two that disagree mean
    one of them is wrong and neither should reach a screen.

    Returns ``(sentence, path)``. THE SENTENCE CARRIES NO PATH and the path is
    returned beside it, because the two facts have two different audiences: a
    viewer needs to know the control ran and what it proved, and a filesystem
    path tells them nothing they can use. The path belongs in the run record,
    where whoever audits the control will look for it. Refusal messages below
    keep their paths deliberately: an exception is a diagnostic, never a screen.
    """
    path = _solver_info_path(case_dir)
    if path is None:
        return ("the solver wrote no second residual record for this run, so "
                "the pressure residual rests on the solver log alone", None)
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    header = None
    rows: dict[str, float] = {}
    for line in lines:
        if line.startswith("#"):
            names = [c.strip() for c in line.lstrip("#").split("\t") if c.strip()]
            if "p_initial" in names and "Time" in names:
                header = names
            continue
        if header is None:
            raise ReaderRefused(
                f"{path} has data before any header naming p_initial")
        cells = [c.strip() for c in line.split("\t")]
        if len(cells) <= header.index("p_initial"):
            continue
        rows[cells[header.index("Time")]] = float(cells[header.index("p_initial")])
    if not rows:
        raise ReaderRefused(f"{path} carries no rows")

    checked = mismatched = 0
    first_bad = None
    for step_time, value in zip(iterations, p_first_pass):
        key = _time_key(step_time)
        if key not in rows:
            continue
        checked += 1
        reference = rows[key]
        if abs(reference - value) > 1e-9 * max(abs(reference), abs(value), 1e-30):
            mismatched += 1
            if first_bad is None:
                first_bad = (key, value, reference)
    if checked == 0:
        raise ReaderRefused(
            f"{path} shares no time value with {case_dir}/log.simpleFoam, so "
            f"the pressure cross-check compared nothing. A cross-check that "
            f"silently compares zero rows is the control failing open.")
    if mismatched:
        key, mine, theirs = first_bad
        raise ReaderRefused(
            f"pressure residual disagreement on {mismatched} of {checked} "
            f"iterations between {case_dir}/log.simpleFoam first pass and "
            f"{path}. First at time {key}: log first pass {mine!r}, "
            f"solverInfo p_initial {theirs!r}. If the log's SECOND p pass "
            f"matches instead, this reader has regressed to the L-419 bug.")
    return (f"The solver's own residual record agrees with the first pressure "
            f"pass read from the solver log on all {checked} of {checked} "
            f"iterations", str(path))


def _time_key(value: float) -> str:
    """Format a time the way the log and solverInfo both print it."""
    if float(value).is_integer():
        return str(int(value))
    return repr(value)


# ===========================================================================
# 2. Force coefficients
# ===========================================================================

def _coefficient_path(case_dir: Path) -> Path:
    root = Path(case_dir) / "postProcessing" / "forceCoeffs"
    candidates = sorted(p for p in root.glob("*/coefficient.dat") if p.is_file())
    if not candidates:
        raise ReaderRefused(f"no force history under {root}")
    if len(candidates) > 1:
        raise ReaderRefused(
            f"{root} holds {len(candidates)} coefficient.dat files, one per "
            f"restart; refusing to pick one silently. Files: "
            f"{[str(p) for p in candidates]}")
    return candidates[0]


def read_coefficient_history(case_dir: Path | str, column: str) -> list[float]:
    """One named column of ``coefficient.dat``, every row, in order.

    ``column`` is matched against the header names exactly. ``Cl`` and
    ``Cl(f)`` are different columns and a substring match between them is
    precisely the failure this refuses to allow.
    """
    path = _coefficient_path(Path(case_dir))
    index = None
    values: list[float] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("#"):
            names = line.lstrip("#").split()
            if column in names:
                index = names.index(column)
            continue
        if index is None:
            raise ReaderRefused(
                f"{path} has data before any header naming {column!r}")
        cells = line.split()
        if len(cells) > index:
            values.append(float(cells[index]))
    if index is None:
        raise ReaderRefused(f"{path} has no column named {column!r}")
    if not values:
        raise ReaderRefused(f"{path} carries no rows")
    return values


def _assert_matches_jf1_reader(case_dir: Path, mine: list[float]) -> str:
    """Tripwire against the lift number forking into two implementations.

    ``verification/runs/JF1_jet_flap/jf1_display_numbers.read_lift_history``
    already reads Cl for the jet-flap family and is the number the result
    sheet quotes. If this module ever returns a different Cl history for the
    same case, the screen's moving curve and the screen's table would be two
    different measurements wearing one label. So they are compared, and a
    difference REFUSES rather than being reconciled at display time.
    """
    import importlib.util

    reader = Path("/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap"
                  "/jf1_display_numbers.py")
    if not reader.is_file():
        return ("The lift figures on the result table were not available to "
                "compare against, so this check did not run")
    spec = importlib.util.spec_from_file_location("_jf1_display_numbers", reader)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    theirs = module.read_lift_history(case_dir)
    if len(theirs) != len(mine):
        raise ReaderRefused(
            f"lift history length disagreement on {case_dir}: this module "
            f"read {len(mine)} rows, jf1_display_numbers read {len(theirs)}")
    for position, (a, b) in enumerate(zip(mine, theirs)):
        if a != b:
            raise ReaderRefused(
                f"lift history disagreement on {case_dir} at row {position}: "
                f"this module read {a!r}, jf1_display_numbers read {b!r}. Two "
                f"implementations of one number have diverged.")
    return (f"The moving lift curve and the lift table are the same "
            f"measurement, matching on all {len(mine)} of {len(mine)} rows")


# ===========================================================================
# 3. The run's REAL wall time and REAL cost
# ===========================================================================

_STATUS_KEYS = ("rc", "wall_s", "ranks", "core_min_MEASURED", "utc_start",
                "utc_end", "stage_at_exit", "case_id")


def read_run_status(case_dir: Path | str) -> dict:
    """The launcher's own record of what this run cost.

    This is where the elapsed clock and the cost line come from, because it is
    the file that MEASURED them: wall seconds between the wrapper's own start
    and end stamps, and core-minutes at the rank count actually used. The
    solver log's ClockTime is read separately and asserted consistent, but it
    excludes setup and is not the costed figure.
    """
    case = Path(case_dir)
    candidates = sorted(case.glob("RUN_STATUS.*.txt"))
    if not candidates:
        raise ReaderRefused(
            f"no RUN_STATUS.*.txt under {case}; the run's real wall time and "
            f"real cost are unknown and this stage will not display an "
            f"elapsed clock it had to invent")
    if len(candidates) > 1:
        raise ReaderRefused(
            f"{case} holds {len(candidates)} RUN_STATUS files; refusing to "
            f"pick one: {[p.name for p in candidates]}")
    path = candidates[0]
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split(None, 1)
        if len(parts) == 2 and parts[0] in _STATUS_KEYS:
            values.setdefault(parts[0], parts[1].strip())
    missing = [k for k in ("rc", "wall_s", "ranks", "core_min_MEASURED")
               if k not in values]
    if missing:
        raise ReaderRefused(f"{path} states no {', '.join(missing)}")
    if values["rc"] != "0":
        raise ReaderRefused(
            f"{path} records rc {values['rc']!r}; this run did not complete "
            f"and its monitors will not be replayed as a completed solve")
    return {
        "path": str(path),
        "case_id": values.get("case_id", case.name),
        "wall_s": float(values["wall_s"]),
        "ranks": int(values["ranks"]),
        "core_min_measured": float(values["core_min_MEASURED"]),
        "utc_start": values.get("utc_start"),
        "utc_end": values.get("utc_end"),
        "cost_basis": (
            "Core minutes measured while the run executed. Any figure in "
            f"currency is derived from them at ${USD_PER_CORE_HOUR} per core "
            "hour and is not itself a measurement, because this machine "
            "cannot read its own billing."),
    }


# ===========================================================================
# 4. Down-sampling for display -- stride only, never smoothing
# ===========================================================================

@dataclass(frozen=True)
class Frame:
    """One displayed sample. Every number here is a row of the run."""
    position: int          # 0-based position in the emitted sequence
    source_row: int        # 0-based row of the source history it IS
    iteration: float
    elapsed_s: float       # the run's real ExecutionTime at that iteration
    residuals: dict        # field -> initial residual, verbatim
    coefficients: dict     # name -> coefficient, verbatim
    envelope: dict         # field -> (min, max) over the rows stridden past

    def as_dict(self) -> dict:
        return {"position": self.position, "source_row": self.source_row,
                "iteration": self.iteration, "elapsed_s": self.elapsed_s,
                "residuals": dict(self.residuals),
                "coefficients": dict(self.coefficients),
                "envelope": {k: list(v) for k, v in self.envelope.items()}}


def downsample(history: dict, coefficients: dict, max_frames: int = 120
               ) -> tuple[list[Frame], dict]:
    """Select at most ``max_frames`` REAL rows: every k-th, plus first and last.

    No averaging, no interpolation, no smoothing, no clipping. The returned
    provenance record states the stride and the source row of every frame, so
    anything on screen can be traced to a line of the log.

    Because a stride steps over rows, each frame also carries the true min and
    max of each channel across the rows from the previous frame up to and
    including its own. That is measured data added beside the sample, not a
    modification of it: a spike that the stride missed is still visible as an
    envelope rather than being quietly erased.
    """
    total = history["n"]
    if total == 0:
        raise ReaderRefused("cannot down-sample an empty history")
    if max_frames < 2:
        raise ReaderRefused("a replay needs at least a first and a last frame")
    stride = max(1, math.ceil(total / max_frames))

    picks = list(range(0, total, stride))
    if picks[-1] != total - 1:
        picks.append(total - 1)

    channels = history["residuals"]
    frames: list[Frame] = []
    previous = -1
    for position, row in enumerate(picks):
        window = slice(previous + 1, row + 1)
        envelope = {}
        for name, series in channels.items():
            chunk = series[window]
            if chunk:
                envelope[name] = (min(chunk), max(chunk))
        frames.append(Frame(
            position=position,
            source_row=row,
            iteration=history["iterations"][row],
            elapsed_s=history["elapsed_s"][row],
            residuals={name: series[row] for name, series in channels.items()},
            coefficients={name: series[row] for name, series in
                          coefficients.items() if row < len(series)},
            envelope=envelope,
        ))
        previous = row

    provenance = {
        "rule": ("every k-th source row, values verbatim, plus the exact "
                 "first and last row; no averaging, interpolation or "
                 "smoothing of any kind"),
        "stride": stride,
        "source_rows": total,
        "frames": len(frames),
        "source_row_of_each_frame": [f.source_row for f in frames],
        "envelope": ("min and max of each channel over the source rows "
                     "between this frame and the previous one, measured, so a "
                     "spike the stride stepped over is still visible"),
    }
    return frames, provenance


# ===========================================================================
# 5. Assembling one run, and one sweep
# ===========================================================================

@dataclass
class SweepPoint:
    """One replayable solve: its frames, its real clock, its real cost."""
    label: str
    case_dir: str
    frames: list
    provenance: dict
    status: dict
    history_n: int
    final: dict
    #: What the controls PROVED, in sentences a viewer can read. No paths.
    controls: list
    #: Where each control looked. The audit trail, for the record only.
    control_paths: list

    def as_dict(self) -> dict:
        return {"label": self.label, "case_dir": self.case_dir,
                "iterations": self.history_n,
                "wall_s": self.status["wall_s"],
                "core_min_measured": self.status["core_min_measured"],
                "ranks": self.status["ranks"],
                "final": dict(self.final),
                "downsample": dict(self.provenance),
                "controls": list(self.controls),
                "control_paths": list(self.control_paths)}


@dataclass
class RunHistory:
    """A whole sweep, ready to be paced onto a screen."""
    points: list
    core_min_total: float
    wall_clock_span_s: float | None
    concurrent: bool
    cost_basis: str
    controls: list

    @property
    def usd_derived(self) -> float:
        return self.core_min_total / 60.0 * USD_PER_CORE_HOUR


def read_run_history(cases: Sequence[tuple[str, Path | str]],
                     *, coefficient_columns: Sequence[str] = ("Cl", "Cd"),
                     max_frames: int = 120,
                     cross_check_jf1: bool = False) -> RunHistory:
    """Read every sweep point, run every control, refuse on any blindness.

    ``cases`` is an ordered sequence of ``(label, case_dir)``. Order is the
    order the points are presented in, which is a presentation choice; the
    numbers are not.
    """
    import datetime as _dt

    controls = self_check(Path(cases[0][1]))
    points: list[SweepPoint] = []
    starts: list[_dt.datetime] = []
    ends: list[_dt.datetime] = []

    for label, case_dir in cases:
        case = Path(case_dir)
        status = read_run_status(case)
        history = read_solve_history(case)
        coefficients = {name: read_coefficient_history(case, name)
                        for name in coefficient_columns}

        # Two lists, deliberately. The first is what a viewer reads and
        # carries no path; the second is where each control looked and stays
        # in the record. Keeping them apart here, at the point the sentences
        # are minted, is what stops a path reaching a screen downstream.
        per_case_controls = []
        per_case_paths = [str(status["path"])]
        if cross_check_jf1 and "Cl" in coefficients:
            per_case_controls.append(
                _assert_matches_jf1_reader(case, coefficients["Cl"]))
        per_case_controls.append(history["solver_info_cross_check"])
        if history["solver_info_path"]:
            per_case_paths.append(history["solver_info_path"])

        # The log's own ClockTime against the wrapper's measured wall seconds.
        # They are not the same quantity -- the wrapper's includes setup -- so
        # this asserts consistency, not equality, and names the gap.
        log_clock = history["elapsed_s"][-1]
        if not (0 < log_clock <= status["wall_s"] + 5):
            raise ReaderRefused(
                f"{case}: the log's final ExecutionTime {log_clock} s and the "
                f"wrapper's measured wall {status['wall_s']} s are not "
                f"consistent; the elapsed clock on screen has two sources "
                f"that disagree and neither will be shown")
        per_case_controls.append(
            f"The elapsed time the solver reported, {log_clock:.0f} s, sits "
            f"inside the {status['wall_s']:.0f} s measured for the whole run, "
            f"the {status['wall_s'] - log_clock:.0f} s difference being setup")

        frames, provenance = downsample(history, coefficients, max_frames)
        final = {name: series[-1] for name, series in coefficients.items()}
        final.update({f"{name}_residual": series[-1]
                      for name, series in history["residuals"].items()})

        points.append(SweepPoint(
            label=label, case_dir=str(case), frames=frames,
            provenance=provenance, status=status, history_n=history["n"],
            final=final, controls=per_case_controls,
            control_paths=per_case_paths))

        if status["utc_start"] and status["utc_end"]:
            fmt = "%Y-%m-%dT%H:%M:%SZ"
            starts.append(_dt.datetime.strptime(status["utc_start"], fmt))
            ends.append(_dt.datetime.strptime(status["utc_end"], fmt))

    core_min_total = sum(p.status["core_min_measured"] for p in points)
    span = None
    concurrent = False
    if len(starts) == len(points) and starts:
        span = (max(ends) - min(starts)).total_seconds()
        wall_sum = sum(p.status["wall_s"] for p in points)
        concurrent = span < wall_sum - 1.0

    return RunHistory(
        points=points,
        core_min_total=core_min_total,
        wall_clock_span_s=span,
        concurrent=concurrent,
        cost_basis=points[0].status["cost_basis"],
        controls=controls,
    )


# ===========================================================================
# 6. The plants
# ===========================================================================

def _copy_case_shell(case: Path, work: Path) -> Path:
    """A copy of just the files the readers touch, so a plant is cheap."""
    target = work / case.name
    (target / "system").mkdir(parents=True, exist_ok=True)
    shutil.copy2(case / "system" / "fvSolution", target / "system" / "fvSolution")
    shutil.copy2(case / "log.simpleFoam", target / "log.simpleFoam")
    info = _solver_info_path(case)
    if info is not None:
        destination = target / "postProcessing" / "contErr" / info.parent.name
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copy2(info, destination / "solverInfo.dat")
    coefficients = _coefficient_path(case)
    destination = target / "postProcessing" / "forceCoeffs" / coefficients.parent.name
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copy2(coefficients, destination / "coefficient.dat")
    for status in case.glob("RUN_STATUS.*.txt"):
        shutil.copy2(status, target / status.name)
    return target


def _plant_pressure_passes(case: Path) -> str:
    """THE control this module exists for.

    Two DIFFERENT sentinels are written into the two ``Solving for p`` lines
    of one interior iteration of a copy of the real log. The reader is then
    run over the copy and must return the FIRST sentinel.

    A reader that took the last match -- the L-419 bug -- returns
    ``PLANT_SECOND_PASS`` here and is caught. A reader that read the wrong
    field entirely returns neither. There is no way to pass this control by
    accident.
    """
    with tempfile.TemporaryDirectory(prefix="replay_plant_p_") as tmp:
        copy = _copy_case_shell(case, Path(tmp))
        lines = (copy / "log.simpleFoam").read_text(
            encoding="utf-8", errors="replace").splitlines()

        # Find an interior time step and its two p lines.
        step_starts = [i for i, ln in enumerate(lines) if _TIME_RE.match(ln)]
        if len(step_starts) < 3:
            raise ReaderRefused(
                f"{case}: fewer than three time steps; no interior iteration "
                f"to plant into")
        target_index = len(step_starts) // 2
        begin = step_starts[target_index]
        end = step_starts[target_index + 1]
        p_lines = [i for i in range(begin, end)
                   if (m := _SOLVE_RE.search(lines[i])) and m.group(1) == "p"]
        if len(p_lines) < 2:
            raise ReaderRefused(
                f"{case}: the iteration chosen for the pressure plant has "
                f"{len(p_lines)} p solves; this control requires the double "
                f"solve it exists to police")

        expected_time = float(_TIME_RE.match(lines[begin]).group(1))
        for line_index, sentinel in ((p_lines[0], PLANT),
                                     (p_lines[1], PLANT_SECOND_PASS)):
            lines[line_index] = _SOLVE_RE.sub(
                lambda m, s=sentinel: (
                    f"Solving for {m.group(1)}, Initial residual = {s!r}, "
                    f"Final residual = {m.group(3)}"),
                lines[line_index], count=1)
        (copy / "log.simpleFoam").write_text("\n".join(lines) + "\n",
                                             encoding="utf-8")

        # The planted log no longer matches solverInfo, which is the point:
        # the cross-check is exercised separately, so it is off here.
        seen = read_solve_history(copy, cross_check=False)
        row = seen["iterations"].index(expected_time)
        value = seen["residuals"]["p"][row]
        if abs(value - PLANT_SECOND_PASS) <= 1e-15:
            raise ReaderRefused(
                f"PRESSURE PASS CONTROL FAILED on {case}: planted {PLANT!r} "
                f"into the first 'Solving for p' of iteration "
                f"{expected_time:g} and {PLANT_SECOND_PASS!r} into the "
                f"second, and the reader returned the SECOND. It is taking "
                f"the non-orthogonal corrector pass, which is the L-419 bug.")
        if abs(value - PLANT) > 1e-15:
            raise ReaderRefused(
                f"PRESSURE PASS CONTROL FAILED on {case}: planted {PLANT!r} "
                f"into the first 'Solving for p' of iteration "
                f"{expected_time:g} and the reader returned {value!r}. It is "
                f"not reading that line at all.")
        return (f"pressure pass control PASSED: two different sentinels in the "
                f"two p solves of iteration {expected_time:g}; the reader "
                f"returned the first-pass sentinel")


def _plant_cross_check(case: Path) -> str:
    """Prove the solverInfo cross-check can actually fail.

    A control that never fires is not a control. One row of a copied
    solverInfo.dat is corrupted and the cross-check must refuse.
    """
    if _solver_info_path(case) is None:
        return "no solverInfo.dat; cross-check control not applicable"
    with tempfile.TemporaryDirectory(prefix="replay_plant_x_") as tmp:
        copy = _copy_case_shell(case, Path(tmp))
        info = _solver_info_path(copy)
        lines = info.read_text(encoding="utf-8", errors="replace").splitlines()
        header = None
        data_rows = []
        for index, line in enumerate(lines):
            if line.startswith("#"):
                names = [c.strip() for c in line.lstrip("#").split("\t") if c.strip()]
                if "p_initial" in names:
                    header = names
                continue
            data_rows.append(index)
        if header is None or not data_rows:
            raise ReaderRefused(f"{info} has no p_initial column to corrupt")
        victim = data_rows[len(data_rows) // 2]
        cells = lines[victim].split("\t")
        cells[header.index("p_initial")] = repr(PLANT)
        lines[victim] = "\t".join(cells)
        info.write_text("\n".join(lines) + "\n", encoding="utf-8")
        try:
            read_solve_history(copy)
        except ReaderRefused:
            return ("cross-check control PASSED: a single corrupted "
                    "solverInfo p_initial row made the reader refuse")
        raise ReaderRefused(
            f"CROSS-CHECK CONTROL FAILED on {case}: one row of solverInfo "
            f"p_initial was set to {PLANT!r} and the reader accepted it. The "
            f"pressure cross-check is not comparing what it claims to.")


def _plant_elapsed(case: Path) -> str:
    """Prove the elapsed clock is read from ExecutionTime and not counted."""
    with tempfile.TemporaryDirectory(prefix="replay_plant_t_") as tmp:
        copy = _copy_case_shell(case, Path(tmp))
        lines = (copy / "log.simpleFoam").read_text(
            encoding="utf-8", errors="replace").splitlines()
        exec_lines = [i for i, ln in enumerate(lines) if _EXEC_RE.match(ln)]
        if not exec_lines:
            raise ReaderRefused(f"{case}: no ExecutionTime lines to plant into")
        victim = exec_lines[len(exec_lines) // 2]
        clock = _EXEC_RE.match(lines[victim]).group(2)
        lines[victim] = f"ExecutionTime = {PLANT!r} s  ClockTime = {clock} s"
        (copy / "log.simpleFoam").write_text("\n".join(lines) + "\n",
                                             encoding="utf-8")
        seen = read_solve_history(copy, cross_check=False)
        if abs(seen["elapsed_s"][exec_lines.index(victim)] - PLANT) > 1e-15:
            raise ReaderRefused(
                f"ELAPSED CONTROL FAILED on {case}: planted {PLANT!r} into an "
                f"ExecutionTime line and the reader did not read it back. The "
                f"clock on screen is not coming from the log.")
        return ("elapsed control PASSED: a planted ExecutionTime was read "
                "back at its own iteration")


def _plant_coefficient(case: Path) -> str:
    """Prove the coefficient reader reads Cl and not a neighbouring column."""
    with tempfile.TemporaryDirectory(prefix="replay_plant_c_") as tmp:
        copy = _copy_case_shell(case, Path(tmp))
        path = _coefficient_path(copy)
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        index = None
        last = None
        for position, line in enumerate(lines):
            if line.startswith("#"):
                names = line.lstrip("#").split()
                if "Cl" in names:
                    index = names.index("Cl")
                continue
            last = position
        if index is None or last is None:
            raise ReaderRefused(f"{path} has no Cl column to plant into")
        cells = lines[last].split()
        cells[index] = repr(PLANT)
        lines[last] = " ".join(cells)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        seen = read_coefficient_history(copy, "Cl")
        if abs(seen[-1] - PLANT) > 1e-15:
            raise ReaderRefused(
                f"COEFFICIENT CONTROL FAILED on {case}: planted {PLANT!r} into "
                f"the last Cl value and the reader read {seen[-1]!r}; it is "
                f"reading a different column.")
        return ("coefficient control PASSED: a planted Cl was read back from "
                "the Cl column")


def self_check(case: Path | str) -> list[str]:
    """Run every control. Any failure raises; nothing is displayed on a warning.

    Called before a single frame is emitted. A reader that cannot see its own
    plants does not get to move a plot.
    """
    case = Path(case)
    return [
        _plant_pressure_passes(case),
        _plant_cross_check(case),
        _plant_elapsed(case),
        _plant_coefficient(case),
    ]
