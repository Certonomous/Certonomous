"""Act A, the motor-in-duct thermal map, as a DEMO MODE act.

Every value below is read off the landed run tree at the moment it is asked
for. There are no physical numbers in this file: the cell counts, the wall
resolution, the peak temperatures, the margins, the planted-control magnitudes,
the wall clocks and the costs all come from artifacts that the heat-transfer
family wrote and still carries on disk. A constant retyped here would be a
second copy free to drift from the run.

WHAT THE SOURCE RUN IS
----------------------
Sixteen steady conjugate operating points, four dissipated powers by four duct
airspeeds, solved with ``chtMultiRegionSimpleFoam`` at one mesh level of 39,680
cells over three regions (35,200 air, 1,120 housing, 3,360 core). The solver
and the turbulence closure are read from the run's own log header and its
``controlDict``, never asserted here.

THREE THINGS THIS ACT DOES DIFFERENTLY, AND WHY
-----------------------------------------------
* **The served surface is the solved body, and that is MEASURED here rather
  than promised.** :meth:`MotorThermalAct.geometry` imports the generator that
  wrote the surface, takes the solved constants out of the case's own build
  script through it, and runs the generator's own geometry guard over the
  served copy. The guard refuses a strut, a nose, a tail or a wrong axial
  extent; the retired surface that used to be served carried all of those. The
  served copy is additionally asserted byte-identical to the generated one, so
  a regenerated surface cannot serve a stale body.

* **Wall time is ``ClockTime``, never ``ExecutionTime``.** OpenFOAM prints both
  on one line and they differ. ``ExecutionTime`` is CPU time; the wall figure
  is ``ClockTime``, and ``ClockTime`` is what is costed. The family's own cost
  record settles this at its section 3.2, and reading the wrong one of the two
  would misstate every cost on the screen.

* **No numeric default reaches a screen.** :func:`_fact` takes no default at
  all and refuses a missing key; :func:`_cell` renders a missing key as words.
  CLAUDE.md rule 3: a zero conjured by ``dict.get(key, 0.0)`` was never read by
  anything, and a reader that cannot fail cannot be evidence.

ONE KNOWN GAP, STATED HERE RATHER THAN DISCOVERED ON CAMERA
-----------------------------------------------------------
:attr:`SolveReplay.cases` is EMPTY, deliberately, and the contract's own words
are followed: "an act with no ``cases`` must say to its supervisor how its logs
are read instead." The shared reader ``chief_engineer.replay_history`` cannot
open this run. It opens ``log.simpleFoam`` by a hard-coded name, it requires a
``RUN_STATUS.*.txt`` carrying ``rc``, ``wall_s``, ``ranks`` and
``core_min_MEASURED``, and it reads lift and drag coefficient columns. This run
writes ``log.solve``, its launcher status file was destroyed by a queue-runner
name collision and re-derived instead, and a conjugate thermal case has no
force coefficients at all. Until that reader takes a configurable log name and
a thermal channel, the sequencer's solving stage will refuse this act, and it
is right to. The monitor series named below are the real files the run wrote
and are ready for it.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

from .demo_mode import (SERVED_GEOMETRY_DIR, Assumption, DemoAct,
                        DemoContractError, ElapsedClock, Feasibility, Figure,
                        GatesAndChecks, Geometry, GeometryMatch, Measured,
                        MeshPlan, Prompt, Restatement, Results, RunRecord,
                        SeriesSpec, SolveReplay, Table, core_minutes,
                        register_act)

REPO = Path(__file__).resolve().parents[2]

T23_RUNS = REPO / "verification" / "runs" / "T-family" / "T23_runs"
T24_RUNS = REPO / "verification" / "runs" / "T-family" / "T24_runs"

#: The point this act's record is written against. Named by the supervisor.
PRIMARY = T23_RUNS / "T23_P305_U20"

MESH_FACTS = T23_RUNS / "T23_T24_MESH_FACTS.json"
GRADE = T23_RUNS / "T23_GRADE.json"
DISPLAY_SURFACE = T23_RUNS / "display_surface"
GENERATOR = DISPLAY_SURFACE / "generate_t23_display_surface.py"
GENERATED_STL = DISPLAY_SURFACE / "t23_solved_geometry.stl"
PARTS_MANIFEST = DISPLAY_SURFACE / "t23_solved_geometry_parts.json"

#: The copy the control-room server actually reads. NOT the generator's copy:
#: naming that one would let a regenerated surface serve a stale body with
#: nothing failing.
SERVED_STL = SERVED_GEOMETRY_DIR / "t23_solved_geometry.stl"

FIGURES = REPO / "docs" / "campaigns" / "T-family" / "demo" / "figures_actA"
SCREEN_DATA = FIGURES / "actA_screen_data.json"

LAUNCHED = REPO / "verification" / "queue" / "heat-transfer" / "launched"

#: The one place the solver binary and the closure may be named, per the
#: 2026-09-01 figure and wording standard. Both are READ from the run.
SOLVER_LOG = "log.solve"

_CASE_NAME = re.compile(r"^T2[34]_P(\d+)_U(\d+)$")
_TIMING = re.compile(
    r"^ExecutionTime\s*=\s*([\d.eE+-]+)\s*s\s+ClockTime\s*=\s*([\d.eE+-]+)\s*s",
    re.M)
_NPROCS = re.compile(r"^nProcs\s*:\s*(\d+)\s*$", re.M)
_APPLICATION = re.compile(r"^\s*application\s+(\w+)\s*;", re.M)
_EXEC = re.compile(r"^Exec\s*:\s*(\S+)\s*$", re.M)


# ---------------------------------------------------------------------------
# Facts, with no default of any kind
# ---------------------------------------------------------------------------

def _fact(node, *keys):
    """One recorded value. NO DEFAULT, numeric or otherwise.

    CLAUDE.md rule 3. A missing key raises where it is asked for, so the act
    fails at validation with the screen still dark, rather than putting a zero
    on camera that no instrument ever read.
    """
    current = node
    trail: list[str] = []
    for key in keys:
        trail.append(str(key))
        if not isinstance(current, dict) or key not in current:
            raise DemoContractError(
                "the run record carries no value for "
                + " then ".join(trail)
                + "; nothing is substituted for a value that was not read")
        current = current[key]
    return current


def _cell(node, *keys, fmt: str = "") -> str:
    """One table cell. A missing value renders as words, never as a number."""
    try:
        value = _fact(node, *keys)
    except DemoContractError:
        return "not recorded"
    if fmt and isinstance(value, (int, float)) and not isinstance(value, bool):
        return format(value, fmt)
    return str(value)


def _screen() -> dict:
    """The Act A screen record, read at the moment it is asked for."""
    if not SCREEN_DATA.is_file():
        raise DemoContractError(
            "the Act A screen record is not on disk, so this act has no "
            "numbers to show and will not invent any")
    return json.loads(SCREEN_DATA.read_text(encoding="utf-8"))


def _mesh_facts() -> dict:
    if not MESH_FACTS.is_file():
        raise DemoContractError("the mesh record is not on disk")
    return json.loads(MESH_FACTS.read_text(encoding="utf-8"))


def _grade() -> dict:
    if not GRADE.is_file():
        raise DemoContractError("the grading record is not on disk")
    return json.loads(GRADE.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# The sixteen points, discovered rather than typed
# ---------------------------------------------------------------------------

def solved_points() -> list[tuple[int, int, Path]]:
    """``(power in watts, airspeed in metres per second, case dir)``, sorted.

    Discovered from the run tree, so a point that is not on disk cannot be
    counted and a point that is cannot be forgotten.
    """
    found: list[tuple[int, int, Path]] = []
    for root in (T23_RUNS, T24_RUNS):
        if not root.is_dir():
            continue
        for case in sorted(root.iterdir()):
            match = _CASE_NAME.match(case.name)
            if match and (case / SOLVER_LOG).is_file():
                found.append((int(match.group(1)), int(match.group(2)), case))
    if not found:
        raise DemoContractError(
            "no solved operating point is on disk; this act has nothing to "
            "show and will not describe a run that is not there")
    return sorted(found)


def _log_text(case: Path) -> str:
    log = case / SOLVER_LOG
    if not log.is_file():
        raise DemoContractError(f"{case.name} has no solver log")
    return log.read_text(encoding="utf-8", errors="replace")


def wall_clock_seconds(case: Path) -> float:
    """The run's WALL seconds: ``ClockTime``, not ``ExecutionTime``.

    OpenFOAM prints both on one line. ``ExecutionTime`` is CPU time and
    ``ClockTime`` is the wall figure; the family's cost record settles this at
    its section 3.2, and the two differ by more than rounding on a loaded box.
    """
    text = _log_text(case)
    timings = _TIMING.findall(text)
    if not timings:
        raise DemoContractError(
            f"{case.name} carries no timing line, so its wall time is unknown "
            f"and no cost will be stated for it")
    if "\nEnd\n" not in text:
        raise DemoContractError(
            f"{case.name} carries no closing line, so it is not a completed "
            f"solve and will not be shown as one")
    return float(timings[-1][1])


def ranks(case: Path) -> int:
    """The rank count the solver itself recorded in its header."""
    match = _NPROCS.search(_log_text(case))
    if not match:
        raise DemoContractError(
            f"{case.name} does not record how many ranks it ran on, so its "
            f"cost cannot be stated")
    return int(match.group(1))


def solver_name(case: Path) -> str:
    """The solver, from the log header AND the case dictionary, cross-checked.

    Two independent artifacts, because the header alone would not catch a log
    copied beside the wrong case.
    """
    from_log = _EXEC.search(_log_text(case))
    control = case / "system" / "controlDict"
    from_dict = (_APPLICATION.search(control.read_text(encoding="utf-8",
                                                       errors="replace"))
                 if control.is_file() else None)
    if not from_log or not from_dict:
        raise DemoContractError(
            f"{case.name} does not name its solver in both its log header and "
            f"its case dictionary, so the solver line will not be shown")
    if from_log.group(1) != from_dict.group(1):
        raise DemoContractError(
            f"{case.name} names one solver in its log and another in its case "
            f"dictionary: {from_log.group(1)} against {from_dict.group(1)}")
    return from_log.group(1)


def campaign_cost() -> tuple[float, float, int, dict]:
    """``(wall seconds summed, core-minutes, ranks, per-point wall seconds)``.

    Summed over every point on disk, each read from its own log. The rank count
    must agree across the points or the sum is not a single cost.
    """
    points = solved_points()
    per_point = {}
    rank_set = set()
    for power, speed, case in points:
        per_point[(power, speed)] = wall_clock_seconds(case)
        rank_set.add(ranks(case))
    if len(rank_set) != 1:
        raise DemoContractError(
            f"the points did not all run on the same rank count {sorted(rank_set)}; "
            f"one cost figure would hide two different machines")
    rank = rank_set.pop()
    total_wall = sum(per_point.values())
    return total_wall, core_minutes(total_wall, rank), rank, per_point


def registered_estimate() -> float:
    """The upfront estimate, summed over the launched points that ran."""
    total = 0.0
    seen = 0
    for power, speed, case in solved_points():
        entry = LAUNCHED / f"{case.name}.json"
        if not entry.is_file():
            continue
        record = json.loads(entry.read_text(encoding="utf-8"))
        total += float(_fact(record, "cost_core_min_estimate"))
        seen += 1
    if seen != len(solved_points()):
        raise DemoContractError(
            "the upfront estimate is not on record for every point that ran, "
            "so no single estimate will be shown beside the actual")
    return total


# ---------------------------------------------------------------------------
# The geometry guard, borrowed from the module that WROTE the surface
# ---------------------------------------------------------------------------

def _generator():
    """Import the surface generator without writing anything beside it."""
    if not GENERATOR.is_file():
        raise DemoContractError(
            "the module that writes the displayed surface is not on disk, so "
            "the surface cannot be shown to be the solved body")
    saved = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location(
            "_t23_display_surface_readonly", GENERATOR)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = saved
    return module


def measured_surface() -> tuple[dict, dict, float]:
    """``(solved constants, measured surface table, tolerance)``.

    The generator's own guard measures the SERVED copy. It refuses by exiting
    rather than raising, which inside a validator would take the process down,
    so the exit is caught here and translated into the contract's refusal.
    """
    generator = _generator()
    try:
        constants = generator.load_case_constants()
        table = generator.check_surface(str(SERVED_STL), constants,
                                        manifest_path=str(PARTS_MANIFEST))
    except SystemExit as exc:
        raise DemoContractError(
            "the served surface did not pass the guard that measures it "
            "against the solved case, so it will not be shown as the solved "
            "body; regenerate it from the solved case") from exc
    return constants, table, float(generator.TOL_M)


def _assert_served_copy_is_current() -> None:
    """The served copy IS the generated one, byte for byte.

    The geometry guard measures shape. This measures identity, which is a
    different question: a surface regenerated at the case and never copied
    across would still pass every shape test while the screen showed the old
    file.
    """
    import hashlib

    for path, what in ((SERVED_STL, "the served surface"),
                       (GENERATED_STL, "the surface the case generates")):
        if not path.is_file():
            raise DemoContractError(f"{what} is not on disk")
    served = hashlib.sha256(SERVED_STL.read_bytes()).hexdigest()
    generated = hashlib.sha256(GENERATED_STL.read_bytes()).hexdigest()
    if served != generated:
        raise DemoContractError(
            "the served surface is not byte-identical to the one the solved "
            "case generates, so it may be a stale body; copy the generated "
            "surface across before this act is shown")


# ---------------------------------------------------------------------------
# Conservation and instrument readings, from the run's own output
# ---------------------------------------------------------------------------

def _last_value(path: Path) -> float:
    if not path.is_file():
        raise DemoContractError(
            f"the monitor {path.name} is not on disk, so the check it backs "
            f"will not be shown")
    rows = [line for line in path.read_text(encoding="utf-8",
                                            errors="replace").splitlines()
            if line.strip() and not line.lstrip().startswith("#")]
    if not rows:
        raise DemoContractError(f"the monitor {path.name} carries no rows")
    return float(rows[-1].split()[-1])


def mass_balance(case: Path) -> tuple[float, float, float]:
    """``(in, out, difference)`` in kilograms per second, from the run."""
    root = case / "postProcessing" / "fluid"
    into = abs(_last_value(root / "inlet_mdot" / "0" / "surfaceFieldValue.dat"))
    out = abs(_last_value(root / "outlet_mdot" / "0" / "surfaceFieldValue.dat"))
    return into, out, abs(out - into)


# ---------------------------------------------------------------------------
# The act
# ---------------------------------------------------------------------------

class MotorThermalAct(DemoAct):
    """The motor-in-duct thermal map, fed from the sixteen landed points."""

    name = "motor in duct thermal map"

    # -- stage 0 ------------------------------------------------------------
    def run_record(self) -> RunRecord:
        screen = _screen()
        return RunRecord(
            run_id=PRIMARY.name,
            run_root=PRIMARY,
            solver="OpenFOAM " + solver_name(PRIMARY),
            physics=("steady conjugate heat transfer between a heated motor "
                     "core, its housing wall and the cooling air in the duct "
                     "around it, with the "
                     + str(_fact(screen, "solver", "turbulence_model"))
                     + " closure resolved to the wall"),
            completion_evidence=T23_RUNS / f"DONE.{PRIMARY.name}",
            presentation_of=f"presentation of run {PRIMARY.name}",
            record_path=T23_RUNS / f"DONE.{PRIMARY.name}")

    # -- stages 1 to 3 ------------------------------------------------------
    def prompt(self) -> Prompt:
        return Prompt(
            "Electric motor in a cooling duct: map the peak temperature in "
            "the motor solids across the dissipated power and the duct "
            "airspeed, and report the margin to the 200 C temperature limit.")

    def restatement(self) -> Restatement:
        points = solved_points()
        powers = sorted({p for p, _, _ in points})
        speeds = sorted({s for _, s, _ in points})
        return Restatement(
            restatement=(f"Solve {len(points)} operating points, "
                         f"{len(powers)} dissipated powers by {len(speeds)} "
                         f"duct airspeeds, and report the hottest solid "
                         f"temperature and its margin to the limit at each."),
            confidence=("The body, the mesh and the operating range are "
                        "settled before the first point runs, so what varies "
                        "across the map is the physics and nothing else."),
            cost_estimate=Measured(
                round(registered_estimate(), 1), "core-minutes",
                LAUNCHED / f"{PRIMARY.name}.json", "derived",
                note=("summed over the sixteen launched records, one per "
                      "point")))

    def assumption(self) -> Assumption:
        """The one user-assumption check: the hand correlation runs hot.

        THE OVERSHOOT FACTOR NAMES BOTH OF ITS SIDES ON SCREEN. A bare "3.4
        times" invites a viewer to pair it with whatever number is largest on
        the screen, and the largest number on this screen belongs to a
        DIFFERENT operating point and a DIFFERENT solid. So the line states the
        operating point, states that the quantity is the housing, and gives the
        numerator and the denominator as temperature rises above the incoming
        air, which is what the ratio is actually taken on.
        """
        grade = _grade()
        power, speed = self._operating_point()
        ratio = float(_fact(grade, PRIMARY.name, "DB_over_solved"))
        predicted_rise, solved_rise = self._correlation_rises()
        return Assumption(
            assumption=("The request treats a hand correlation for a heated "
                        "duct as good enough to size the hot spot."),
            finding=(f"At {power} watts and {speed} metres per second the "
                     f"correlation puts the housing {predicted_rise:.0f} "
                     f"kelvin above the incoming air, where the coupled solve "
                     f"found {solved_rise:.0f} kelvin, so the quick estimate "
                     f"is {ratio:.1f} times too high."),
            correction=("A correlation sizes the problem in seconds and is "
                        "worth running first. The map itself comes from the "
                        "coupled solve, which carries the solid and the air "
                        "together."))

    @staticmethod
    def _operating_point() -> tuple[int, int]:
        """The power and airspeed of the point the ratio is taken at."""
        match = _CASE_NAME.match(PRIMARY.name)
        if not match:
            raise DemoContractError(
                "the point this act reports its correlation check at cannot be "
                "identified, so no operating point will be named beside it")
        return int(match.group(1)), int(match.group(2))

    @staticmethod
    def _correlation_rises() -> tuple[float, float]:
        """``(predicted rise, solved rise)`` in kelvin above the incoming air.

        Both sides of the overshoot ratio, reconstructed from read values and
        then CROSS-CHECKED against the ratio the grading record computed. The
        inlet temperature is not typed here: it falls out of the two recorded
        quantities as peak minus rise, so a change to the inlet condition
        cannot leave a stale constant behind in this file.

        The cross-check is the point. It is what makes the number on screen
        defensible when it is challenged: if the reconstruction and the
        recorded ratio disagree, this refuses rather than showing a factor
        whose two sides nobody can name.
        """
        grade = _grade()
        screen = _screen()
        speed = str(MotorThermalAct._operating_point()[1])
        predicted = float(_fact(grade, PRIMARY.name, "predicted_DB_degC"))
        solved_peak = float(_fact(screen, "assumption_beat", "solved_degC",
                                  speed))
        solved_rise = float(_fact(screen, "assumption_beat",
                                  "solved_rise_at_20ms_K"))
        recorded = float(_fact(grade, PRIMARY.name, "DB_over_solved"))
        inlet = solved_peak - solved_rise
        predicted_rise = predicted - inlet
        if solved_rise <= 0:
            raise DemoContractError(
                "the solved temperature rise is not positive, so no overshoot "
                "factor is meaningful and none will be shown")
        rebuilt = predicted_rise / solved_rise
        if abs(rebuilt - recorded) > 1e-6 * max(1.0, abs(recorded)):
            raise DemoContractError(
                f"the overshoot factor cannot be reconciled: the grading "
                f"record says {recorded:.6f} and the recorded temperatures "
                f"rebuild it as {rebuilt:.6f}. Neither will be shown until "
                f"they agree")
        return predicted_rise, solved_rise

    # -- stage 4 ------------------------------------------------------------
    def geometry(self) -> Geometry:
        _assert_served_copy_is_current()
        constants, surface, tolerance = measured_surface()

        def match(quantity: str, solved: float, supplied) -> GeometryMatch:
            if supplied is None:
                raise DemoContractError(
                    f"the guard could not measure {quantity} on the served "
                    f"surface, so it will not be shown as the solved body")
            return GeometryMatch(
                quantity=quantity,
                solved=Measured(float(solved), "m",
                                PRIMARY.parent / "T23_P305_U10" / "build_t23.py"),
                supplied=Measured(float(supplied), "m", SERVED_STL),
                tolerance=tolerance, relative=False)

        return Geometry(
            served_stl=SERVED_STL,
            display_label="motor housing inside its cooling duct",
            matches=[
                match("duct inner radius", constants["R_DUCT"],
                      surface.get("duct_inner_radius_m")),
                match("motor body outer radius", constants["R_O"],
                      surface.get("centrebody_outer_radius_m")),
                match("axial extent", constants["Z3"] - constants["Z0"],
                      surface.get("axial_length_m")),
            ],
            regenerated_from=PRIMARY.parent / "T23_P305_U10" / "build_t23.py")

    # -- stage 5 ------------------------------------------------------------
    def mesh_plan(self) -> MeshPlan:
        facts = _mesh_facts()
        grade = _grade()
        cells = int(_fact(facts, "cells", "total"))
        wall = _fact(grade, PRIMARY.name, "yplus")
        labels = (("Duct wall", "duct_wall"),
                  ("Motor body, upstream", "centrebody_up"),
                  ("Motor body, downstream", "centrebody_down"),
                  ("Air against the heated housing", "fluid_to_housing"))
        rows = []
        for label, key in labels:
            try:
                low, high, mean = _fact(wall, key)
            except (DemoContractError, TypeError, ValueError):
                rows.append([label, "not recorded", "not recorded",
                             "not recorded"])
                continue
            rows.append([label, f"{low:.2f}", f"{high:.2f}", f"{mean:.2f}"])
        return MeshPlan(
            command=["blockMesh"],
            work_dir=PRIMARY,
            # A pre-formatted string so the screen reads the way the standard
            # writes it. The number itself is read, never typed.
            cell_count=Measured(f"{cells:,}", "cells", MESH_FACTS),
            resolution_headers=["Surface", "Closest wall unit",
                                "Furthest wall unit", "Mean wall unit"],
            resolution_rows=rows,
            wall_zoom_hint="the layers of air lying against the heated housing",
            expected_seconds=30.0)

    # -- stage 6 ------------------------------------------------------------
    def feasibility(self) -> Feasibility:
        grade = _grade()
        screen = _screen()
        estimate = float(_fact(grade, PRIMARY.name, "predicted_DB_degC"))
        limit = float(_fact(screen, "envelope", "limit_degC"))
        return Feasibility(
            check=("A hand correlation for a heated duct, which sizes the hot "
                   "spot in seconds and says whether the full solve is worth "
                   "its cost."),
            result=Measured(round(estimate, 1), "C", GRADE, "derived"),
            verdict_for_user=(
                f"The quick estimate lands within {limit - estimate:.0f} C of "
                f"the {limit:.0f} C limit, close enough that the answer turns "
                f"on the physics, so the full map is worth solving."))

    # -- stage 7 ------------------------------------------------------------
    def solve_replay(self) -> SolveReplay:
        total_wall, core_min, rank, _per_point = campaign_cost()
        points = solved_points()
        monitors = PRIMARY / "postProcessing"
        iterations = len(_TIMING.findall(_log_text(PRIMARY)))
        return SolveReplay(
            series=[
                SeriesSpec(monitors / "core" / "core_T" / "0"
                           / "fieldMinMax.dat", "max", "temperature",
                           "Hottest point in the motor core", "C"),
                SeriesSpec(monitors / "housing" / "housing_T" / "0"
                           / "fieldMinMax.dat", "max", "temperature",
                           "Hottest point in the housing wall", "C"),
                SeriesSpec(PRIMARY / SOLVER_LOG, "p_rgh", "residual",
                           "Pressure residual"),
            ],
            wall_seconds=Measured(
                round(total_wall, 1), "s", PRIMARY / SOLVER_LOG, "measured",
                note=("the closing ClockTime of each of the sixteen solver "
                      "logs, summed; ExecutionTime on the same line is CPU "
                      "time and is not used")),
            ranks=rank,
            total_iterations=iterations,
            sweep_points=len(points),
            # EMPTY DELIBERATELY. The shared reader cannot open this run; the
            # module docstring says exactly why and what would fix it.
            cases=(),
            elapsed_clock=ElapsedClock(
                seconds=total_wall, measured=True,
                basis=("The solver time of the sixteen operating points added "
                       "together, which shared one machine while they ran"),
                source=PRIMARY / SOLVER_LOG))

    # -- stage 8 ------------------------------------------------------------
    def gates(self) -> GatesAndChecks:
        screen = _screen()
        facts = _mesh_facts()
        controls = _fact(screen, "planted_zero_controls")
        readers = (("Hottest point in the motor core",
                    "peak_core_temperature_reader"),
                   ("Hottest point in the housing wall",
                    "peak_housing_temperature_field_reader"),
                   ("Temperature across the radius", "radial_profile_reader"),
                   ("Settling trace", "monitor_trace_reader"))
        rows = []
        for label, key in readers:
            rows.append([
                label,
                _cell(controls, key, "planted_K", fmt=".3e"),
                _cell(controls, key, "read_K", fmt=".3e"),
                "yes" if _cell(controls, key, "passed") == "True" else "no",
            ])
        into, out, difference = mass_balance(PRIMARY)
        cells = int(_fact(facts, "cells", "total"))
        regions = int(_fact(facts, "regions", "n"))
        return GatesAndChecks(
            planted_checks=Table(
                title="Instrument checks",
                headers=["Instrument", "Planted, K", "Read back, K",
                         "Detected"],
                rows=rows, table_id="motor_thermal_planted"),
            conservation=Table(
                title="Air mass through the duct",
                headers=["Quantity", "In", "Out", "Difference"],
                rows=[["Air mass flow, kg/s", f"{into:.6e}", f"{out:.6e}",
                       f"{difference:.1e}"]],
                table_id="motor_thermal_conservation"),
            grid_statement=(
                f"One grid of {cells:,} cells over {regions} regions carries "
                f"every operating point in the map, and every point was "
                f"checked against it cell by cell before a temperature was "
                f"read."))

    # -- stage 9 ------------------------------------------------------------
    def results(self) -> Results:
        screen = _screen()
        total_wall, core_min, rank, _per_point = campaign_cost()

        limit = float(_fact(screen, "envelope", "limit_degC"))
        rows = []
        for row in _fact(screen, "map_rows"):
            rows.append([
                _cell(row, "power_W"),
                _cell(row, "airspeed_ms"),
                _cell(row, "peak_core_T_degC", fmt=".1f"),
                _cell(row, "peak_housing_T_degC", fmt=".1f"),
                _cell(row, "rise_above_inlet_K", fmt=".1f"),
                _cell(row, "margin_to_limit_K", fmt=".1f"),
                "not available",
            ])
        table = Table(
            title="Peak temperature across the map",
            headers=["Power, W", "Airspeed, m/s", "Hottest core, C",
                     "Hottest housing, C", "Rise above inlet, K",
                     f"Margin to the {limit:.0f} C limit, K", "Uncertainty"],
            rows=rows, table_id="motor_thermal_map", role="CHIEF ENGINEER")

        fields = [
            Figure(FIGURES / "actA_temperature_field.png",
                   "Temperature through the air and the solids",
                   "The core runs hottest and the heat leaves through the "
                   "housing wall into the air.", "results"),
            Figure(FIGURES / "actA_velocity_field.png",
                   "Air speed through the cooling duct",
                   "The air accelerates over the housing and carries the heat "
                   "downstream.", "results"),
        ]
        plots = [
            Figure(FIGURES / "actA_envelope.pdf",
                   "Hottest core temperature against duct airspeed",
                   "One curve per dissipated power, each joining the four "
                   "solved airspeeds.", "results"),
            Figure(FIGURES / "actA_radial_profile.pdf",
                   "Temperature from the shaft out to the duct wall",
                   "The step at each material interface is the contact "
                   "between two conductivities.", "results"),
            Figure(FIGURES / "actA_monitor_replay.pdf",
                   "How the temperature settled at each point",
                   "Every trace is the run's own monitor output, sampled "
                   "every hundred iterations.", "results"),
            Figure(FIGURES / "actA_airspeed_thumbnails.png",
                   "The same body at four duct airspeeds",
                   "Faster air cools the housing and shrinks the hot region "
                   "behind it.", "results"),
            Figure(FIGURES / "actA_mesh_boundary_layer.png",
                   "The grid where the air meets the housing",
                   "The layers thin towards the wall so the heat transfer at "
                   "the surface is resolved.", "results"),
            Figure(FIGURES / "actA_assumptions.pdf",
                   "What this run assumes and what it leaves out",
                   "Every limitation on this sheet is about the physics, not "
                   "about the software.", "results"),
        ]

        residual = float(_fact(screen, "statements_of_fact",
                               "anchor_check_largest_residual_K"))
        planted = float(_fact(screen, "planted_zero_controls",
                              "peak_core_temperature_reader", "planted_K"))
        n_readers = len(_fact(screen, "planted_zero_controls"))
        n_anchor = len(_fact(screen, "anchor_checks"))

        return Results(
            fields=fields, plots=plots, tables=[table],
            verification_lines=[
                (f"Reproduced from the fields on disk: {n_anchor} values "
                 f"re-read against the record fixed before the runs started, "
                 f"agreeing to better than {residual:.1e} K."),
                (f"Instrument check: {n_readers} readers each detected a "
                 f"planted {planted:.3e} K perturbation, so a zero from any "
                 f"of them would have been a reading and not a blind spot."),
                ("No rig or wind tunnel data exists for this configuration, "
                 "so the temperatures are shown as solved and no agreement "
                 "with measurement is claimed."),
            ],
            limitations=[
                ("All sixteen operating points ran at one grid level, so no "
                 "discretisation error bar exists and none is drawn."),
                ("The solve is axisymmetric over a five degree wedge, so "
                 "nothing that varies around the axis is resolved."),
                ("Radiation is switched off in all three regions, so heat "
                 "leaves the body by conduction and forced convection alone."),
                ("Each point is a separate steady state, so nothing here says "
                 "how long the body takes to reach these temperatures."),
                ("Turbulent transport is modelled rather than resolved, so "
                 "the heat carried away by the air carries that model's "
                 "error."),
            ],
            cost_actual=Measured(
                round(core_min, 1), "core-minutes", PRIMARY / SOLVER_LOG,
                "measured",
                note=("wall ClockTime summed over the sixteen solver logs at "
                      f"{rank} rank each")),
            cost_estimate_from_stage_2=self.restatement().cost_estimate)

    # -- pacing -------------------------------------------------------------
    def agent_census(self):
        return (("prompt", 1), ("restatement", 2), ("assumption", 3),
                ("geometry", 3), ("meshing", 4), ("feasibility", 4),
                ("solving", 6), ("gates", 3), ("results", 0))


ACT = register_act("motor-thermal", MotorThermalAct())
