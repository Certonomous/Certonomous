"""THE SHOCK-REFLECTION ACT — a Mach 10 shock reflecting from a wall.

The fifth act to plug into DEMO MODE, and a one-line adoption of the shared
entry factory rather than a fifth copy of the plumbing. It presents the double
Mach reflection benchmark (Woodward and Colella) from two grids that landed on
2026-08-07. **No solver runs here.** Every number is read off those runs'
own artifacts at the moment it is shown, and the one thing that does run live
is the mesher, which builds a grid and never touches a graded case.

WHAT THIS ACT MAY AND MAY NOT SAY, and each clause was paid for by a specific
misreading of the record. These are constraints on the SCREEN, and the file
enforces them by construction where it can:

1. **Two grids exist, and nothing here is a refinement study.** A third and
   finer grid was attempted and stopped part of the way through, so the grid
   triple this lab's Roache gating needs does not exist. No convergence order,
   no grid-convergence index and no "the finer grid is more accurate" sentence
   appears anywhere. In absolute units the fine grid's residual is the smaller
   of the two, exactly as predicted before the runs; in units of each grid's
   OWN cell the ordering reverses (0.41 against 0.24 of a cell), so a sentence
   shaped like refinement would be false in one of the two readings and the
   act declines to write one in either.

2. **The headline is half a cell, not a percentage.** The record's 0.15% and
   0.17% of travelled distance are both SMALLER THAN HALF ONE CELL of the grid
   that measured them, so quoting them as a precision claim states a number
   below the increment of the instrument. What the measurement actually
   supports, and what this act says, is that the shock arrives within half a
   mesh cell of its exact position on both grids. That is the stronger
   statement and it survives a hostile reading.

3. **No sentence may imply the structure check succeeded.** The pre-registered
   double-Mach-structure detector did not find what it was written to find,
   and the reason is the detector's own geometry: it looked on the leading
   front, and the canonical second triple point lives on the reflected shock
   behind it. The failure is left standing rather than repaired. The screen
   carries no gate column and no verdict words in any case, so the operative
   requirement is the negative one: the picture is shown as a picture, and
   nothing narrates the structure as confirmed by a check.

4. **The elapsed figure and the cost are the runs' own.** Both wall times are
   parsed from the two solver logs at display time and cross-checked against
   the graded cost record before either is shown; a disagreement refuses.

WHY IT SUBCLASSES THE SEQUENCER FOR EXACTLY ONE STAGE. The shared solving
stage delegates to the replay reader, which reads a force history and a
per-case status record. This benchmark has neither: it is an explicit
compressible solve whose log carries a physical clock and an execution clock
and no coefficients at all. Handing that reader a case it cannot read would
have produced a refusal on camera at the one stage a viewer is watching. So
the solving stage is replaced, exactly as the adjoint act replaces it, and
every other stage is the shared one. The replacement still publishes through
:meth:`demo_sequencer.Sequencer._publish`, so every payload passes the screen
guard and every banner is derived from the payload being published.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .demo_mode import (Assumption, DemoAct, DemoContractError, ElapsedClock,
                        Feasibility, Figure, GatesAndChecks, Geometry,
                        GeometryMatch, Measured, MeshPlan, Prompt, Restatement,
                        Results, SeriesSpec, SolveReplay, Table, register_act)
from .demo_sequencer import Sequencer, make_act_entry

__all__ = ["ShockReflectionAct", "ShockReflectionSequencer", "ACT", "drive",
           "main"]

REPO = Path(__file__).resolve().parents[2]
RUNS = REPO / "verification" / "runs" / "DMR_runs"
CAMPAIGN = REPO / "verification" / "campaign"
FROZEN_GATE = CAMPAIGN / "DMR_PREREGISTRATION.md"
GRADED_RECORD = CAMPAIGN / "DMR_RESULTS.md"
FIGURES = REPO / "docs" / "campaigns" / "DMR" / "demo" / "figures"
SERVED_STL = Path(__file__).resolve().parents[1] / "geometry" / \
    "dmr_reflecting_wall.stl"
MESH_BUILDER = REPO / "cases" / "DMR_shock_reflection" / "build_dmr_mesh.py"
MESH_WORK = RUNS / "demo_mesh_work"

#: What the compute figure is CALLED on a customer screen. The quantity is
#: unchanged and is still core-minutes.
COMPUTE_UNIT = "processor-minutes"

#: The two grids, in the order the screen shows them: cheap first, so the
#: viewer sees the answer arrive twice rather than once.
GRIDS: tuple[tuple[str, str, int], ...] = (
    ("Coarse", "res60", 60),
    ("Fine", "res120", 120),
)

#: MPI ranks both solves ran on, from the graded cost record.
RANKS = 4

#: The known perturbation the log readers are shown before any number from
#: them is displayed. CLAUDE.md rule 3: a zero from a reader not shown able to
#: see a non-zero is not evidence.
PLANT = 1.234e-03


# ---------------------------------------------------------------------------
# Readers. Each one reads an artifact; none of them carries a typed number.
# ---------------------------------------------------------------------------

def _case(key: str) -> Path:
    return RUNS / key


def _gate_v(key: str) -> dict:
    """The graded kinematics record for one grid, as the locator wrote it."""
    path = _case(key) / "locator_result.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    gate = dict(record["gateV"])
    gate["path"] = path
    gate["increment"] = float(record["dx"])
    return gate


def _cells(key: str) -> int:
    """The cell count of one grid, read out of its own mesh.

    Off the mesh the run actually used, not off the resolution the act names,
    so the number on screen and the grid the numbers came from cannot part.
    """
    owner = _case(key) / "constant" / "polyMesh" / "owner"
    head = owner.read_text(encoding="utf-8")[:2000]
    hit = re.search(r"nCells:(\d+)", head)
    if not hit:
        raise DemoContractError(
            "a grid's own mesh does not state how many cells it has, so the "
            "count on screen would have no source")
    return int(hit.group(1))


def _skewness(key: str) -> float:
    """The worst cell distortion the mesh checker measured on one grid."""
    log = _case(key) / "log.checkMesh"
    hit = re.search(r"Max skewness = ([0-9.eE+-]+)",
                    log.read_text(encoding="utf-8"))
    if not hit:
        raise DemoContractError(
            "a grid's mesh check does not report its worst cell distortion")
    return float(hit.group(1))


def _wall_seconds(key: str) -> float:
    """The measured wall clock of one solve, from its own log."""
    log = _case(key) / "log.rhoCentralFoam"
    line = next((text for text in log.read_text(encoding="utf-8").splitlines()
                 if "Elapsed (wall clock)" in text), None)
    if line is None:
        raise DemoContractError(
            "a solve's log does not carry the wall clock the screen shows")
    # THE CLOCK IS THE TAIL OF THE LINE, NOT THE FIRST COLON ON IT. The label
    # the timing wrapper writes is "(h:mm:ss or m:ss)", so a pattern that
    # takes the first colon parses the units description as the time. Anchored
    # at the end instead, which is where the value is.
    hit = re.search(r"(?:(\d+):)?(\d+):([\d.]+)\s*$", line)
    if not hit:
        raise DemoContractError(
            "a solve's log states a wall clock the screen cannot read")
    hours = float(hit.group(1) or 0)
    return hours * 3600.0 + float(hit.group(2)) * 60.0 + float(hit.group(3))


def _steps(key: str) -> int:
    """How many time steps one solve took, counted in its own log."""
    log = _case(key) / "log.rhoCentralFoam"
    return sum(1 for line in log.read_text(encoding="utf-8").splitlines()
               if line.startswith("Time = "))


def _solver_clock(path: Path) -> tuple[list[float], list[float]]:
    """The two clocks one solve wrote: physical time and execution seconds.

    THE ONLY READER THE SOLVING STAGE USES, and it is deliberately one
    function so the planted control below exercises the same code the screen
    does. A control that tests a copy of the reader tests nothing.
    """
    times: list[float] = []
    execs: list[float] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("Time = "):
            times.append(float(line.split("=", 1)[1]))
        elif line.startswith("ExecutionTime = "):
            execs.append(float(line.split("=", 1)[1].split("s", 1)[0]))
    if not times or not execs:
        raise DemoContractError(
            "a solve's log carries no clock, so the monitors on screen would "
            "have nothing measured behind them")
    return times, execs[:len(times)]


def _planted_control() -> list[list[str]]:
    """Drive the log reader to a KNOWN answer before any real one is shown.

    A known offset is added to both clocks in a copy of the log held in
    memory, the same reader is run over the copy, and the offset must come
    back. It REFUSES rather than reporting a miss: a reader that cannot see a
    perturbation cannot testify that there is none.
    """
    import tempfile

    rows: list[list[str]] = []
    for label, key, _ in GRIDS:
        source = _case(key) / "log.rhoCentralFoam"
        text = source.read_text(encoding="utf-8")
        clean_times, clean_execs = _solver_clock(source)

        def bump(match, add=PLANT):
            return "Time = %.10g" % (float(match.group(1)) + add)

        planted = re.sub(r"^Time = ([\d.eE+-]+)$",
                         lambda m: bump(m), text, flags=re.M)
        planted = re.sub(r"^ExecutionTime = ([\d.eE+-]+) s",
                         lambda m: "ExecutionTime = %.10g s"
                         % (float(m.group(1)) + PLANT), planted, flags=re.M)
        with tempfile.NamedTemporaryFile("w", suffix=".log", delete=False,
                                         encoding="utf-8") as handle:
            handle.write(planted)
            copy = Path(handle.name)
        try:
            seen_times, seen_execs = _solver_clock(copy)
        finally:
            copy.unlink(missing_ok=True)

        for what, clean, seen in (("shock clock", clean_times, seen_times),
                                  ("solver clock", clean_execs, seen_execs)):
            moved = seen[-1] - clean[-1]
            if abs(moved - PLANT) > PLANT * 1e-3:
                raise DemoContractError(
                    f"the {what} reader is shown a known change of "
                    f"{PLANT:.3e} on the {label.lower()} grid and reads back "
                    f"{moved:.3e}; a reader that cannot see a change put into "
                    f"it cannot be trusted to report one that is not there")
            rows.append([f"{label} grid {what}", f"{PLANT:.3e}", "seen"])
    return rows


def _stl_extent() -> tuple[float, float]:
    """The served surface's own streamwise extent, measured off the file."""
    import struct

    data = SERVED_STL.read_bytes()
    count = struct.unpack("<I", data[80:84])[0]
    xs: list[float] = []
    for i in range(count):
        base = 84 + i * 50 + 12
        for vertex in range(3):
            xs.append(struct.unpack(
                "<3f", data[base + vertex * 12:base + vertex * 12 + 12])[0])
    return min(xs), max(xs)


def _wall_from_mesh() -> tuple[float, float]:
    """Where the wall starts and how far it runs, from the run's OWN mesh.

    The bottom boundary of the solved case is split in two: a fixed-inflow
    strip ahead of the shock foot and the reflecting wall behind it. The split
    is a face count in the mesh's boundary file, so dividing by the grid's own
    spacing gives both numbers as measurements of the solved case rather than
    as constants retyped beside it.
    """
    boundary = (_case("res120") / "constant" / "polyMesh"
                / "boundary").read_text(encoding="utf-8")
    faces = dict(re.findall(r"(\w+)\s*\{[^}]*?nFaces\s+(\d+);", boundary))
    try:
        inflow = int(faces["bottomInflow"])
        wall = int(faces["rampWall"])
    except KeyError:
        raise DemoContractError(
            "the solved mesh does not carry the split between the inflow "
            "strip and the reflecting wall, so the served surface cannot be "
            "measured against it") from None
    resolution = 120.0
    return inflow / resolution, wall / resolution


# ---------------------------------------------------------------------------
# The act
# ---------------------------------------------------------------------------

class ShockReflectionAct(DemoAct):
    """A Mach 10 shock reflecting from a wall, from two completed grids."""

    name = "shock reflection at Mach 10"

    # -- stage 0, internal --------------------------------------------------
    def run_record(self):
        from .demo_mode import RunRecord

        return RunRecord(
            run_id="shock-reflection",
            run_root=RUNS,
            solver="OpenFOAM rhoCentralFoam",
            physics=("inviscid compressible flow, a Mach 10 shock reflecting "
                     "from a wall"),
            completion_evidence=_case("res120") / "locator_result.json",
            presentation_of="presentation of run shock-reflection",
            record_path=GRADED_RECORD)

    # -- stage 1 ------------------------------------------------------------
    def prompt(self) -> Prompt:
        return Prompt(
            "Drive a Mach 10 shock into a wall at a steep angle and check "
            "how fast the shock travels against the exact answer.")

    # -- stage 2 ------------------------------------------------------------
    def restatement(self) -> Restatement:
        return Restatement(
            restatement=(
                "Checking the speed of the shock against the exact solution, "
                "on two grids, with the success criterion written down before "
                "anything is built."),
            confidence=(
                "High on the shock speed, which has an exact answer to check "
                "against. The structure behind the shock has no exact answer "
                "and is shown as a picture."),
            cost_estimate=Measured(20, COMPUTE_UNIT, FROZEN_GATE,
                                   basis="derived"))

    # -- stage 3 ------------------------------------------------------------
    def assumption(self) -> Assumption:
        """The one user-assumption check, and it is about the grid.

        Stated as a correction because the record supports it: the coarse grid
        already places the shock inside half a cell, so the expensive grid is
        confirmation and not the decider. It stops there. It does NOT go on to
        say the finer grid is the more accurate one, because in units of each
        grid's own cell that ordering reverses, and there is no third grid to
        settle it.
        """
        return Assumption(
            assumption=("You expect the finer grid to be the one that decides "
                        "whether the shock speed is right."),
            finding=("Both grids put the shock inside half a cell of its "
                     "exact position, so the cheap grid already answers the "
                     "question and the expensive one confirms it."),
            correction=("A third and finer grid is attempted and stops part "
                        "of the way through, so this screen compares two "
                        "grids and offers no refinement study."))

    # -- stage 4 ------------------------------------------------------------
    def geometry(self) -> Geometry:
        start, length = _wall_from_mesh()
        low, high = _stl_extent()
        mesh_source = (_case("res120") / "constant" / "polyMesh" / "boundary")
        return Geometry(
            served_stl=SERVED_STL,
            display_label="the wall the shock reflects from",
            matches=[
                GeometryMatch(
                    quantity="wall start",
                    solved=Measured(start, "", mesh_source),
                    supplied=Measured(low, "", SERVED_STL),
                    tolerance=1e-5, relative=False),
                GeometryMatch(
                    quantity="wall length",
                    solved=Measured(length, "", mesh_source),
                    supplied=Measured(high - low, "", SERVED_STL),
                    tolerance=1e-5, relative=False),
            ])

    # -- stage 5 ------------------------------------------------------------
    def mesh_plan(self) -> MeshPlan:
        """The real mesher of the primary grid, and a directory it may write.

        It writes an OpenFOAM mesh and nothing else, into a scratch directory
        that holds no evidence. That is not a convention: the sequencer
        refuses to mesh into anything that looks like a landed case, because a
        mesher writing a fresh mesh into one destroys the provenance the whole
        result rests on. The cell count below is read off the SOLVED grid's
        own mesh, and the sequencer reads the freshly written mesh back off
        disk and refuses to show a grid that is not the one the numbers came
        from.
        """
        cells = _cells("res120")
        return MeshPlan(
            command=["python3", str(MESH_BUILDER), "--out", str(MESH_WORK),
                     "--resolution", "120"],
            work_dir=MESH_WORK,
            cell_count=Measured(f"{cells:,}", "cells",
                                _case("res120") / "constant" / "polyMesh"),
            resolution_headers=["Grid", "Cells", "Spacing",
                                "Worst cell distortion"],
            resolution_rows=[
                [label, f"{_cells(key):,}", f"1 in {resolution}",
                 f"{_skewness(key):.1e}"]
                for label, key, resolution in GRIDS],
            wall_zoom_hint="the cells along the wall where the shock strikes",
            expected_seconds=40.0)

    # -- stage 6 ------------------------------------------------------------
    def feasibility(self) -> Feasibility:
        """The cheap check before the budget is committed.

        The shock's trace on the wall at the final time is known exactly from
        the configuration, so whether it leaves the channel is answerable
        before anything is meshed. If it left, every position on screen would
        be measured against a shock that was no longer there.
        """
        return Feasibility(
            check=("Whether the shock runs off the far end of the channel "
                   "before the final time, which would leave nothing to "
                   "measure."),
            result=Measured("2.48 along a channel of 4.00", "", FROZEN_GATE,
                            basis="derived"),
            verdict_for_user=("The shock is still well inside the channel at "
                              "the final time, so the comparison holds and "
                              "the budget is worth committing."))

    # -- stage 7 ------------------------------------------------------------
    def solve_replay(self) -> SolveReplay:
        """The two solves' own clocks, and the cost they carry.

        ``cases`` is deliberately empty: this act's solving stage is its own
        (:class:`ShockReflectionSequencer`) and reads these logs directly,
        because the shared reader wants a force history and a per-case status
        record that an explicit compressible solve does not write.
        """
        total = sum(_wall_seconds(key) for _, key, _ in GRIDS)
        self._cross_check_cost(total)
        return SolveReplay(
            series=[SeriesSpec(_case(key) / "log.rhoCentralFoam",
                               "Time", "iteration",
                               f"{label} grid shock clock")
                    for label, key, _ in GRIDS],
            wall_seconds=Measured(round(total, 2), "s", GRADED_RECORD),
            ranks=RANKS,
            total_iterations=_steps("res120"),
            sweep_points=len(GRIDS),
            pace=0.02,
            elapsed_clock=ElapsedClock(
                seconds=total,
                basis="The measured wall time of both grids, added.",
                measured=True,
                source=GRADED_RECORD))

    @staticmethod
    def _cross_check_cost(total: float) -> None:
        """Refuse if the logs and the graded cost record disagree.

        The screen's elapsed figure and its cost both come from the logs; the
        record is what grades them. Two sources for one number is how the two
        drift, so they are compared here rather than trusted, and a
        disagreement stops the act instead of putting the friendlier of the
        two on camera.
        """
        text = GRADED_RECORD.read_text(encoding="utf-8")
        stated = [float(v) for v in re.findall(r"\(([\d.]+) s . 4\)", text)]
        if not stated:
            raise DemoContractError(
                "the graded cost record does not state the wall times the "
                "screen is about to show, so they cannot be cross-checked")
        if abs(sum(stated) - total) > 0.02:
            raise DemoContractError(
                f"the solver logs total {total:.2f} s and the graded record "
                f"states {sum(stated):.2f} s; the elapsed figure has two "
                f"sources that disagree and neither will be shown")

    # -- stage 8 ------------------------------------------------------------
    def gates(self) -> GatesAndChecks:
        """The reader checks, run for real, and the grid sentence.

        The rows are produced by driving the readers to a KNOWN answer, not by
        recording that somebody once did. The grid sentence states what the
        two grids are and stops: it does not claim a refinement study, because
        there is no third grid and none of the three gating levels a
        refinement study needs exists here.
        """
        return GatesAndChecks(
            planted_checks=Table(
                title="Instrument checks",
                headers=["Reader", "Change put in", "Change read back"],
                rows=_planted_control(),
                table_id="dmr_planted"),
            conservation=None,
            grid_statement=(
                f"Two grids carry every number on this screen, one at half "
                f"the spacing of the other, {_cells('res60'):,} cells and "
                f"{_cells('res120'):,} cells, and each number names its own "
                f"grid."))

    # -- stage 9 ------------------------------------------------------------
    def results(self) -> Results:
        """What the screen shows, and the four things it refuses to show.

        No convergence order, no grid-convergence index, no "the finer grid is
        more accurate", and no sentence narrating the structure behind the
        shock as confirmed by a check. The first three need a third grid that
        does not exist; the fourth would misstate a detector that did not find
        what it was written to find.
        """
        rows = []
        for label, key, _ in GRIDS:
            gate = _gate_v(key)
            error = float(gate["error"])
            increment = float(gate["increment"])
            rows.append([
                label,
                f"{float(gate['x_measured']):.4f}",
                f"{float(gate['x_exact_at_row']):.4f}",
                f"{error:.4f}",
                f"{error / increment:.2f}",
            ])

        position = Table(
            title="Where the shock is at the final time",
            headers=["Grid", "Solved position", "Exact position",
                     "Difference", "Difference in cells of that grid"],
            rows=rows, table_id="dmr_position", role="CHIEF ENGINEER")

        figure = Figure(
            FIGURES / "dmr_density_contours.png",
            "Density at the final time, both grids",
            ("The shock, the structure it throws off the wall and the jet "
             "beneath it."),
            "shock-reflection")

        in_cells = {label: float(_gate_v(key)["error"])
                    / float(_gate_v(key)["increment"])
                    for label, key, _ in GRIDS}
        core_min = sum(_wall_seconds(key) for _, key, _ in GRIDS) * RANKS / 60.0

        return Results(
            fields=[figure],
            plots=[],
            tables=[position],
            verification_lines=[
                (f"The shock arrives within half a cell of its exact "
                 f"position on both grids: {in_cells['Fine']:.2f} of a cell "
                 f"on the fine grid and {in_cells['Coarse']:.2f} of a cell on "
                 f"the coarse one."),
                ("The success criterion, one percent of the distance the "
                 "shock travels, is written down before the first grid is "
                 "built."),
                ("The structure behind the shock is recorded as a picture and "
                 "is not one of the quantities measured here."),
            ],
            limitations=[
                ("The second shock and the jet running along the wall under "
                 "it appear in the picture and are not among the quantities "
                 "measured. Read them as a picture, not as a number."),
                ("This is an inviscid calculation with no turbulence model in "
                 "it, so nothing here says anything about a turbulence "
                 "closure."),
                ("The comparison is against an exact answer for the speed of "
                 "the shock only. No experimental measurement of this "
                 "configuration exists to compare the rest of it against."),
                ("Two grids are solved. A third and finer one is attempted "
                 "and stops part of the way through, so no refinement study "
                 "and no order of accuracy is offered here."),
                ("Each difference above is smaller than one cell of the grid "
                 "that measures it, so it is a bound rather than a resolved "
                 "number."),
            ],
            cost_actual=Measured(round(core_min, 2), COMPUTE_UNIT,
                                 GRADED_RECORD),
            cost_estimate_from_stage_2=self.restatement().cost_estimate)

    # -- pacing -------------------------------------------------------------
    def agent_census(self):
        return (("prompt", 1), ("restatement", 2), ("assumption", 2),
                ("geometry", 3), ("meshing", 3), ("feasibility", 3),
                ("solving", 4), ("gates", 2), ("results", 0))


# ---------------------------------------------------------------------------
# The one stage this act owns
# ---------------------------------------------------------------------------

@dataclass
class ShockReflectionSequencer(Sequencer):
    """The shared nine-stage walk with the solving stage replaced.

    ``screen_seconds`` is how much real time the solving stage occupies. Every
    published value is independent of it: the schedule decides WHEN a frame is
    shown and never what is in it, so a rehearsal driven in milliseconds and a
    shoot driven in minutes put the identical numbers on screen.
    """

    screen_seconds: float = 45.0

    #: Frames published per grid. The logs carry 2,111 and 1,008 time steps;
    #: publishing every one of them would spend the whole stage on the paced
    #: queue and show a viewer nothing they could read.
    frames_per_grid: int = 40

    def _stage_solving(self, emit, script, record) -> dict:
        replay = self.act.solve_replay()
        controls = _planted_control()
        self._say(script, "Solving the shock on the cheap grid first.",
                  tense="progressive")

        published = self._publish(emit, "solve.begin", {
            "stage": "solving",
            "points": len(GRIDS), "point_index": None,
            "iterations": replay.total_iterations,
            "labels": [f"{label} grid" for label, _, _ in GRIDS],
            # PRESENT TENSE, DELIBERATELY, AND IT IS A DIRECTIVE RATHER THAN
            # a preference. Two of Sanaa's own instructions cross here: the
            # earlier one asks for the past tense with a result, the later one
            # says flatly no past tense. Present satisfies both; past violates
            # one. Every line this act speaks is therefore present until she
            # rules, and the tense argument below names the CHECK being run,
            # not the tense being written.
            "controls": [
                "each clock the monitors read is shown a known change and "
                "reads it back before any of these numbers appears",
                f"{len(controls)} readers are checked this way",
            ],
        })

        origin = self.clock()
        total_frames = len(GRIDS) * self.frames_per_grid
        shown = 0
        for point, (label, key, _) in enumerate(GRIDS, start=1):
            times, execs = _solver_clock(
                _case(key) / "log.rhoCentralFoam")
            steps = len(times)
            picks = sorted({int(round(i * (steps - 1)
                                      / (self.frames_per_grid - 1)))
                            for i in range(self.frames_per_grid)})
            for index in picks:
                shown += 1
                deadline = origin + (shown / total_frames) * float(
                    self.screen_seconds)
                remaining = deadline - self.clock()
                if remaining > 0:
                    self.sleep(remaining)
                published = self._publish(emit, "solve.frame", {
                    "stage": "solving",
                    "point_index": point, "points": len(GRIDS),
                    "iteration": index + 1,
                    "iterations": steps,
                    "label": f"{label} grid",
                    "monitors": {
                        "Time reached": round(times[index], 5),
                        "Final time": round(times[-1], 5),
                        "Solver seconds": round(execs[index], 2),
                    },
                })

        published = self._publish(emit, "solve.end", {
            "stage": "solving",
            "points": len(GRIDS),
            "finished": True,
            "labels": [f"{label} grid" for label, _, _ in GRIDS],
        })
        self._say(script,
                  "The shock reaches the final time on both grids.",
                  tense="past")
        self._publish(emit, "demo.elapsed", {
            "stage": "solving",
            "elapsed": replay.clock().on_screen(),
            "finished": True,
        })
        return published


ACT = register_act("shock-reflection", ShockReflectionAct())


def drive(emit=None, script=None, *, screen_seconds: float = 45.0,
          typed_prompt: str | None = None, sleep=None, clock=None) -> dict:
    """Walk this act through DEMO MODE. Returns the sequencer's record.

    ``typed_prompt`` IS ACCEPTED, and that is the point of naming it here. The
    shared entry factory passes the typed request only to a driver whose
    signature takes one, and records on the entry whether it did; a driver
    that omits it silently shows the act's registered wording whatever the
    viewer typed, which is the exact defect the typed prompt was threaded to
    remove.
    """
    import time as _time

    kwargs = {"screen_seconds": screen_seconds, "typed_prompt": typed_prompt,
              "clock": clock if clock is not None else _time.monotonic}
    if sleep is not None:
        kwargs["sleep"] = sleep
    return ShockReflectionSequencer(act=ACT, **kwargs).run(emit=emit,
                                                           script=script)


#: THE DISPATCHED ENTRY POINT, adopted in one line from the shared mechanism.
#: ``make_act_entry`` holds the whole implementation: the import that registers
#: the act, the emit passthrough, the transcript the table-publishing stages
#: depend on, the typed-prompt echo, the deliberate dropping of uploaded
#: parameters, and the no-catch policy on refusals.
#:
#: ROUTING IS NOT WIRED BY THIS FILE and is not this module's to wire. Reaching
#: it needs an intent in ``chief_engineer.router``, which is shared
#: control-room tooling read as a diff by a supervisor, and a server restart,
#: which is a coordinated decision. Until then this entry is reachable by
#: calling it, exactly as the pre-shoot gate reaches the act.
main = make_act_entry("shock-reflection", act_module="workflows.dmr_act",
                      driver="drive", label="shock-reflection")


if __name__ == "__main__":                       # pragma: no cover
    from .demo_mode import validate_act

    problems = validate_act(ACT)
    print(f"{len(problems)} problem(s)")
    for problem in problems:
        print(f"  - {problem}")
