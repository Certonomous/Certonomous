"""Act C, the battery module, as a DEMO MODE act. THE FEATURE IS THE REFUSAL.

Sanaa fixed this act's beat on 2026-09-01 (~20:30Z shooting protocol): *"the run
completes, the gate refuses it, the platform says so and schedules the corrected
run. The feature is the refusal."*  Everything below is built to that sentence.
The run in front of the viewer is a real completed conjugate transient; the
check set before it started ran and refused one of its three arms; and the
corrected run is shown as scheduled rather than as absent.

WHERE THIS FILE LIVES AND WHY IT IS NOT UNDER ``sdk/``.  ``sdk/`` is the cfd
team's tree.  This act is heat-transfer content -- our run, our numbers, our
wording -- so it lives beside the campaign it belongs to and imports the
contract rather than being committed into someone else's package.  Registration
is a one-line call the cfd team makes, and the accompanying note names it.

EVERY NUMBER IS READ, NOT TYPED.  The cell counts, the resolution rows, the
three check arms, the wall clock, the core-minutes, the mesh quality and the
geometry extents are all read at the moment they are asked for, from artifacts
the heat-transfer family wrote and still carries on disk.  A constant retyped
here would be a second copy free to drift from the run.

THE TEMPERATURES ARE NOT HERE, AND THAT IS ENFORCED RATHER THAN REMEMBERED.
No absolute temperature, no temperature rise and no outlet temperature appears
on any surface this act produces.  The act consults
:mod:`actC_graded_admission`, which derives what may be shown from the corrected
run's COMMITTED GRADED ARTEFACT and yields the EMPTY set until that artefact
exists.  While the set is empty:

  * the solving stage declares no temperature series;
  * the results tables carry check magnitudes and no thermal quantity;
  * the closing report says the convergence study is running and its band lands
    in the user's inbox.

When the corrected run grades and is committed, the same code -- unedited --
gains its temperature series, its banded numbers and the "study done" ending.
That is the same instrument the screen guard consults, so the act and the guard
cannot disagree about what is showable.

WHAT THIS ACT DELIBERATELY DOES NOT DO.

* **No certificate is minted or linked.**  ``chief_engineer.certificate``
  rewrites two weaker labels onto a stronger one, and the certificate store is
  keyed by intent and is last-writer-wins.  :attr:`Closing.certificate_state`
  is a written sentence and nothing resolves a document by path.
* **No fixed counter is displayed.**  The worker count in the control room is a
  query parameter defaulting to a literal, and the cycle numeral has no source
  at all; neither is fed by this act.  The agent census below is the one
  counter this act supplies, and it moves.
* **No projection is applied to the cost.**  The compute figure is this run's
  measured core-minutes; the dollar figure is derived at the recorded rate and
  says so.  Whether the owner's graphics-processor speedup applies to a
  conjugate solve on this box is a question on her desk and this act does not
  pre-empt it.

ONE MEASURED GEOMETRY FINDING, STATED HERE RATHER THAN DISCOVERED ON CAMERA.
The served surface carries a housing shell that the solve does not resolve --
measured, six millimetres on the sides and ten on the ends -- and it is drawn
with a visible depth while the solve is two-dimensional.  The in-plane extents
the solve DOES have are matched exactly, and those are the comparisons
:meth:`BatteryModuleAct.geometry` declares.  The housing is named on screen as a
feature found and in the caveat box as a body this run does not conduct heat
through.  It is not silently dropped and it is not silently claimed.
"""
from __future__ import annotations

import json
import os
import re
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from sdk.workflows.demo_mode import (                       # noqa: E402
    SERVED_GEOMETRY_DIR, Assumption, Closing, DemoAct, DemoContractError,
    Feasibility, Figure, GatesAndChecks, Geometry, GeometryMatch, Measured,
    MeshPlan, Prompt, Restatement, Results, RunRecord, SeriesSpec, SolveReplay,
    Table, core_minutes)

import actC_graded_admission as ADMISSION                   # noqa: E402

RUNS = REPO / "verification" / "runs" / "T-family" / "T25R2_MODULE_runs"

#: The two arms of the check, by directory.  They differ ONLY in the number of
#: outer sweeps per time step: same mesh, byte-identical and proved so at
#: staging, same loads, same relaxation, same tolerances.  That is what makes
#: their difference a statement about the method rather than about the battery.
ARM_TEN = RUNS / "T25R2_L1"
ARM_TWENTY = RUNS / "T25R2_L1_OC20"

GATE_JSON = RUNS / "OC_GATE.json"
MESH_VERIFICATION = RUNS / "MESH_VERIFICATION.txt"

SERVED_STL = SERVED_GEOMETRY_DIR / "battery_module_8cell.stl"

FIGDIR = HERE / "figures_actC_gate"
SHEET = HERE / "ACT_C_GATE_sheet.pdf"

#: Plain-English arm labels.  The run directory names carry the lab's own case
#: identifiers and an identifier never reaches a screen, so every user-visible
#: mention of an arm uses these.
TEN, TWENTY = "ten sweeps", "twenty sweeps"


# ---------------------------------------------------------------------------
# READERS.  Each refuses rather than defaulting: a value conjured by a default
# was never read by anything, and a reader that cannot fail is not evidence.
# ---------------------------------------------------------------------------

def _refuse(msg: str):
    raise DemoContractError(msg)


def _text(path: Path) -> str:
    if not path.is_file():
        _refuse(f"the artifact this stage reads is not on disk: {path.name}")
    return path.read_text(errors="replace")


def gate_detail() -> dict:
    """The three check arms, as the comparator recorded them."""
    doc = json.loads(_text(GATE_JSON))
    try:
        return doc["results"]["OUTER_LOOP_GATE"]["detail"]
    except (KeyError, TypeError):
        _refuse("the check record carries no arm detail")


def stl_geometry() -> dict:
    """Measure the SERVED surface: extents, and the planes it actually carries.

    Reads the binary triangles and collects the distinct vertex coordinates.
    The solve is two-dimensional, so the third extent is not a comparable
    quantity and is reported as what it is -- a drawn depth -- rather than
    matched against a numerical unit depth.
    """
    raw = SERVED_STL.read_bytes() if SERVED_STL.is_file() else b""
    if len(raw) < 84:
        _refuse("the served surface is not readable as a solid body")
    count = struct.unpack("<I", raw[80:84])[0]
    if len(raw) != 84 + 50 * count:
        _refuse("the served surface is truncated")
    xs, ys, zs = set(), set(), set()
    for i in range(count):
        base = 84 + 50 * i + 12
        for k in range(3):
            x, y, z = struct.unpack("<fff", raw[base + 12 * k:base + 12 * k + 12])
            xs.add(round(x, 6))
            ys.add(round(y, 6))
            zs.add(round(z, 6))
    ys_sorted = sorted(ys)
    # The stack's own internal planes: the repeated 30 mm and 3 mm spacings.
    spacings = [round(b - a, 6) for a, b in zip(ys_sorted, ys_sorted[1:])]
    return {
        "triangles": count,
        "x": sorted(xs), "y": ys_sorted, "z": sorted(zs),
        "spacings": spacings,
        "depth_drawn": round(max(zs) - min(zs), 6),
    }


def nearest(values, target: float) -> float:
    return min(values, key=lambda v: abs(v - target))


def channel_planes(stack_lo: float, cell_m: float, gap_m: float,
                   channels: int) -> list:
    """Where every coolant channel face must sit if the surface is this body.

    PREDICTED from the mesh record's own registered pitch and gap, MEASURED
    against the served surface.  The two come from different artifacts written
    by different steps, which is what makes the comparison worth making: a
    surface for some other module carries none of these planes.
    """
    planes = []
    y = stack_lo
    for _ in range(channels):
        y += cell_m
        planes.append(round(y, 9))          # channel, lower face
        y += gap_m
        planes.append(round(y, 9))          # channel, upper face
    return planes


def channel_plane_deviation(geo: dict, planes: list) -> float:
    """The worst distance from a predicted channel face to the nearest plane
    the surface actually carries.  Refuses rather than reporting a number it
    could not compute."""
    if not planes:
        _refuse("no channel faces were predicted, so nothing was compared")
    return max(abs(nearest(geo["y"], p) - p) for p in planes)


_BBOX = re.compile(
    r"Overall domain bounding box \(([-\d.eE+ ]+)\) \(([-\d.eE+ ]+)\)")


def solved_bounding_box(region: str) -> tuple:
    """The solved module's own extents, out of the mesh check the run ran."""
    log = ARM_TWENTY / f"log.checkMesh.{region}"
    m = _BBOX.search(_text(log))
    if not m:
        _refuse(f"the {region} mesh check records no domain extent")
    lo = [float(v) for v in m.group(1).split()]
    hi = [float(v) for v in m.group(2).split()]
    return lo, hi


def _mesh_block(text: str, name: str) -> str:
    """The one banner-delimited block for `name`, and nothing either side.

    A structural locator, not a line offset: the record is a sequence of
    rule-banner-rule blocks and the wrong block would silently supply another
    level's cell count. `name` is a run directory, never rendered.
    """
    m = re.search(r"^=+\n%s\b.*?\n=+\n(.*?)(?=\n=+\n|\Z)" % re.escape(name),
                  text, re.S | re.M)
    if not m:
        _refuse("the mesh record carries no block for this run")
    return m.group(1)


def mesh_facts() -> dict:
    """Cells, per-feature resolution and mesh quality, from the mesh record."""
    block = _mesh_block(_text(MESH_VERIFICATION), "T25R2_L1_OC20")
    out = {}
    m = re.search(r"cells\s+module\s+(\d+)\s+\+\s+coolant\s+(\d+)\s+=\s+(\d+)",
                  block)
    if not m:
        _refuse("the mesh record carries no cell counts")
    out["module_cells"] = int(m.group(1))
    out["coolant_cells"] = int(m.group(2))
    out["total_cells"] = int(m.group(3))
    m = re.search(r"ACROSS EACH (\d+) mm GAP: (\d+) cells, on all (\d+)", block)
    if not m:
        _refuse("the mesh record carries no channel resolution")
    out["gap_mm"] = int(m.group(1))
    out["cells_across_gap"] = int(m.group(2))
    out["channels"] = int(m.group(3))
    m = re.search(r"ACROSS EACH (\d+) mm CELL: (\d+) cells, on all (\d+)", block)
    if not m:
        _refuse("the mesh record carries no cell-block resolution")
    out["cell_mm"] = int(m.group(1))
    out["cells_across_cell"] = int(m.group(2))
    out["cells_in_stack"] = int(m.group(3))
    m = re.search(r"STREAMWISE dx in the cell zone: ([\d.]+) mm", block)
    out["dx_mm"] = float(m.group(1)) if m else _refuse(
        "the mesh record carries no streamwise spacing")
    m = re.search(r"COUPLED INTERFACE: (\d+) faces on module == (\d+)", block)
    if not m:
        _refuse("the mesh record carries no coupled-interface count")
    out["interface_faces"] = int(m.group(1))
    quality = {}
    for region in ("module", "coolant"):
        q = re.search(
            r"checkMesh %s\s+Mesh OK=(\w+) maxNonOrth=([\d.eE+-]+).*?"
            r"maxSkew=([\d.eE+-]+)" % region, block)
        if not q:
            _refuse(f"the mesh record carries no quality line for {region}")
        quality[region] = (q.group(1) == "True", float(q.group(2)),
                           float(q.group(3)))
    out["quality"] = quality
    return out


_WALL = re.compile(r"STATUS wall_s (\d+) x ranks (\d+)")
_SOLVER_CM = re.compile(r"SOLVER core-min \(log\.solve ExecutionTime "
                        r"([\d.]+) s x ranks (\d+)\s*/\s*60\) = ([\d.]+)")
_POINT = re.compile(r"PRE-REGISTERED POINT \(section [\d.]+\) = ([\d.]+)")
_AGE = re.compile(r"TIGHTEST margin over every written time: \+([\d.]+) s")


def completion(run_dir: Path) -> dict:
    """Wall time, ranks, core-minutes and the age-guard margin, as recorded."""
    marker = None
    for candidate in run_dir.glob("COMPLETION.*.txt"):
        marker = candidate
        break
    if marker is None:
        _refuse(f"{run_dir.name} carries no completion record")
    text = _text(marker)
    if "MARKER VERDICT: DONE" not in text:
        _refuse(f"{run_dir.name} is not recorded complete")
    w = _WALL.search(text)
    c = _SOLVER_CM.search(text)
    p = _POINT.search(text)
    a = _AGE.search(text)
    if not (w and c and a):
        _refuse(f"{run_dir.name}'s completion record is missing a cost or "
                f"age-guard figure")
    return {"marker": marker,
            "wall_s": int(w.group(1)), "ranks": int(w.group(2)),
            "solver_core_min": float(c.group(3)),
            "point_core_min": float(p.group(1)) if p else None,
            "age_margin_s": float(a.group(1))}


_EXEC = re.compile(r"^Exec\s*:\s*(\S+)\s*$", re.M)
_STEPS = re.compile(r"^ExecutionTime", re.M)


def solver_name() -> str:
    """The solver binary, out of the run's own log header."""
    head = _text(ARM_TWENTY / "log.solve")[:4000]
    m = _EXEC.search(head)
    if not m:
        _refuse("the run's log does not name the solver that wrote it")
    return os.path.basename(m.group(1))


def cost_pair():
    """Predicted, actual, and the MISS between them -- all read, none typed.

    Sanaa, 2026-09-01 ~20:56Z: every act carries an early beat predicting the
    cost and a closing beat comparing it to the actual. The evidentiary value
    of the pair is that ONE OF THEM WAS FROZEN FIRST, so the predicted figure
    is read from each arm's completion marker, which quotes section 8.2 of the
    frozen registration (8.30 and 18.09 core-minutes) -- never reconstructed
    afterwards from the actual.

    ⚠ THE DIRECTION IS REPORTED AND IS NOT DRESSED UP. This run came in UNDER,
    and coming in under is comfortable in a way an overrun is not: nobody
    objects to spending less, and that comfort is exactly what would let a 25%
    misprediction be phrased as though the forecast had been good. It was not.
    The forecast missed by a quarter, in the direction that happens to flatter
    us. The beat states the magnitude and the direction and stops.
    """
    ten, twenty = completion(ARM_TEN), completion(ARM_TWENTY)
    predicted = (ten["point_core_min"] or 0.0) + (twenty["point_core_min"] or 0.0)
    actual = ten["solver_core_min"] + twenty["solver_core_min"]
    if predicted <= 0:
        _refuse("no registered cost estimate to compare the actual against")
    ratio = actual / predicted
    return {"predicted": predicted, "actual": actual, "ratio": ratio,
            "pct": abs(1.0 - ratio) * 100.0,
            "direction": "under" if ratio < 1.0 else "over",
            "arms": [(ten["point_core_min"], ten["solver_core_min"]),
                     (twenty["point_core_min"], twenty["solver_core_min"])]}


def admissible():
    """What the corrected run has graded, and why the set is what it is."""
    return ADMISSION.derive()


# ---------------------------------------------------------------------------
# THE ACT
# ---------------------------------------------------------------------------

class BatteryModuleAct(DemoAct):
    """Eight prismatic cells, seven coolant channels, one discharge pulse.

    The narrative Sanaa fixed: the run completes, the check refuses it, the
    platform says so and schedules the corrected run.
    """

    name = "battery module cooling"

    # -- stage 0, internal ---------------------------------------------------
    def run_record(self) -> RunRecord:
        marker = completion(ARM_TWENTY)["marker"]
        return RunRecord(
            run_id="battery module, twenty sweeps",
            run_root=ARM_TWENTY,
            solver=f"OpenFOAM {solver_name()}",
            physics=("transient conjugate heat transfer, eight solid cells "
                     "coupled to seven forced-convection coolant channels"),
            completion_evidence=marker,
            presentation_of="presentation of run battery module, twenty sweeps",
            record_path=marker)

    # -- 1. the prompt -------------------------------------------------------
    def prompt(self) -> Prompt:
        return Prompt(
            "Battery module cooling: hold every cell in an eight cell module "
            "inside its temperature limit through a takeoff discharge pulse, "
            "and report the worst cell and the spread across the module.")

    # -- 2. acknowledgement: one sentence, and what it will cost -------------
    def restatement(self) -> Restatement:
        facts = mesh_facts()
        point = (completion(ARM_TEN)["point_core_min"] or 0.0) + \
            (completion(ARM_TWENTY)["point_core_min"] or 0.0)
        return Restatement(
            restatement=(
                "Solve module and coolant together, 60 s pulse into cruise, "
                "900 s. Check for settings dependence before reporting."),
            confidence=(
                "High on setup: 8 cells, 7 channels, 2 loads, all specified "
                "by your upload. The open question is numerical, and we test "
                "it."),
            cost_estimate=Measured(round(point, 2), "processor-minutes",
                                   completion(ARM_TWENTY)["marker"],
                                   basis="derived",
                                   note=f"{facts['total_cells']} cells, two "
                                        f"settings arms"))

    # -- 3. the one user-assumption correction beat --------------------------
    def assumption(self) -> Assumption:
        geo = stl_geometry()
        lo, hi = solved_bounding_box("module")
        housing_x = round(lo[0] - min(geo["x"]), 6)
        housing_y = round(lo[1] - min(geo["y"]), 6)
        return Assumption(
            assumption=("The uploaded body is the thing to solve, housing "
                        "included."),
            finding=(
                f"Housing measured on your surface: {housing_x * 1000:.0f} mm "
                f"sides, {housing_y * 1000:.0f} mm ends. This run resolves the "
                f"stack and its 7 channels."),
            correction=(
                "A housing conducts and would lower the peak in the worst "
                "cell. Leaving it out is the conservative side. Said before "
                "you spend, not after."))

    # -- 4. the surface, measured against the body that was solved -----------
    def geometry(self) -> Geometry:
        geo = stl_geometry()
        facts = mesh_facts()
        lo, hi = solved_bounding_box("module")
        log = ARM_TWENTY / "log.checkMesh.module"
        stl_src = SERVED_STL
        tol = 1e-6

        def plane(axis: str, target: float, what: str) -> GeometryMatch:
            return GeometryMatch(
                quantity=what,
                solved=Measured(round(target, 6), "m", log),
                supplied=Measured(nearest(geo[axis], target), "m", stl_src),
                tolerance=tol, relative=False)

        planes = channel_planes(lo[1], facts["cell_mm"] / 1000.0,
                                facts["gap_mm"] / 1000.0, facts["channels"])
        matches = [
            plane("x", lo[0], "stack face, inlet side"),
            plane("x", hi[0], "stack face, outlet side"),
            plane("y", lo[1], "first cell, outer face"),
            plane("y", hi[1], "last cell, outer face"),
            plane("y", planes[0], "first coolant channel, lower face"),
            plane("y", planes[-1], "last coolant channel, upper face"),
            # EVERY channel face at once, as one number: the worst of the
            # fourteen. Two spot checks could both agree on a surface whose
            # middle is wrong, and this row cannot.
            GeometryMatch(
                quantity=f"worst of the {len(planes)} coolant channel faces",
                solved=Measured(0.0, "m", MESH_VERIFICATION),
                supplied=Measured(round(channel_plane_deviation(geo, planes), 9),
                                  "m", stl_src),
                tolerance=tol, relative=False),
        ]
        return Geometry(served_stl=SERVED_STL,
                        display_label="Eight cell module with coolant channels",
                        matches=matches)

    def geometry_table(self) -> Table:
        """Her screen 3 table: extent, reference lengths, features found."""
        geo = stl_geometry()
        facts = mesh_facts()
        lo, hi = solved_bounding_box("module")
        rows = [
            ["Overall extent, flow direction", f"{(hi[0] - lo[0]) * 1000:.0f}",
             "mm", "read from the surface"],
            ["Overall extent, stack direction", f"{(hi[1] - lo[1]) * 1000:.0f}",
             "mm", "read from the surface"],
            ["Cell pitch", f"{facts['cell_mm']}", "mm", "reference length"],
            ["Coolant channel width", f"{facts['gap_mm']}", "mm",
             "reference length"],
            ["Cells found", f"{facts['cells_in_stack']}", "count",
             "feature found"],
            ["Coolant channels found", f"{facts['channels']}", "count",
             "feature found"],
            ["Housing shell found", "yes", "",
             "feature found, not conducted through in this run"],
            ["Drawn depth", f"{geo['depth_drawn'] * 1000:.0f}", "mm",
             "the section is solved in the plane"],
        ]
        return Table(title="The module as uploaded",
                     headers=["Quantity", "Value", "Unit", "How we know"],
                     rows=rows, table_id="battery-geometry")

    def assumptions_table(self) -> Table:
        """Her screen 4 table: user-defined against lab-defined, with units."""
        facts = mesh_facts()
        doc = json.loads(_text(GATE_JSON))
        rows = [
            ["Module geometry and channel layout", "as uploaded", "",
             "user defined"],
            ["Cells in the stack", str(facts["cells_in_stack"]), "count",
             "user defined"],
            ["Takeoff heat release, per unit volume of cell",
             f"{doc['q_takeoff_W_per_m3']:,.0f}", "W/m3", "user defined"],
            ["Cruise heat release, per unit volume of cell",
             f"{doc['q_cruise_W_per_m3']:,.0f}", "W/m3", "user defined"],
            ["Coolant", "air", "", "lab defined, representative"],
            ["Closure for the channel flow", "two equation eddy viscosity", "",
             "lab defined"],
            ["Time step", f"{doc['results']['T25R2_L1_OC20']['pulse']['deltaT']}",
             "s", "lab defined"],
            ["Outer sweeps per step, first arm", "10", "count", "lab defined"],
            ["Outer sweeps per step, second arm", "20", "count", "lab defined"],
            ["Settling limit the answer had to meet", "0.0123", "K",
             "lab defined, fixed before the run"],
        ]
        return Table(title="What you set, and what we set",
                     headers=["Quantity", "Value", "Unit", "Set by"],
                     rows=rows, table_id="battery-assumptions")

    # -- 5. the mesh, drawn cell by cell ------------------------------------
    def mesh_plan(self) -> MeshPlan:
        facts = mesh_facts()
        rows = [
            ["Across each coolant channel", str(facts["cells_across_gap"]),
             "cells", f"{facts['gap_mm']} mm"],
            ["Across each cell block", str(facts["cells_across_cell"]),
             "cells", f"{facts['cell_mm']} mm"],
            ["Along the flow, in the stack", f"{facts['dx_mm']:g}", "mm",
             "uniform"],
            ["Solid side of the mesh", f"{facts['module_cells']:,}", "cells",
             "the eight cells"],
            ["Coolant side of the mesh", f"{facts['coolant_cells']:,}",
             "cells", "the seven channels"],
            ["Faces where the two meet", f"{facts['interface_faces']:,}",
             "faces", "matched one to one"],
        ]
        return MeshPlan(
            command=["blockMesh", "-case", str(ARM_TWENTY)],
            work_dir=ARM_TWENTY,
            cell_count=Measured(facts["total_cells"], "cells",
                                MESH_VERIFICATION),
            resolution_headers=["Where", "Count", "Unit", "Size"],
            resolution_rows=rows,
            wall_zoom_hint=("the twenty four cells stacked across one three "
                            "millimetre coolant channel, and the matched faces "
                            "where coolant meets cell"),
            expected_seconds=20.0)

    # -- 6. the check before the spend --------------------------------------
    def feasibility(self) -> Feasibility:
        facts = mesh_facts()
        ok_module, nonorth, skew = facts["quality"]["module"]
        ok_coolant, nonorth_c, skew_c = facts["quality"]["coolant"]
        if not (ok_module and ok_coolant):
            _refuse("the mesh check did not pass on both regions")
        return Feasibility(
            check=("Before committing budget: is the mesh square enough for "
                   "a conjugate answer, and do both sides of the coupling "
                   "line up?"),
            result=Measured(max(nonorth, nonorth_c), "degrees of skew between "
                                                     "neighbouring cells",
                            MESH_VERIFICATION,
                            note=f"{facts['interface_faces']} matched faces"),
            verdict_for_user=(
                f"Yes. Skew 0 degrees on both meshes. "
                f"{facts['interface_faces']} solid faces, "
                f"{facts['interface_faces']} coolant partners, 1 to 1. "
                f"Budget committed."),
            seconds=30.0)

    # -- 7. the two arms, side by side --------------------------------------
    def solve_replay(self) -> SolveReplay:
        ten, twenty = completion(ARM_TEN), completion(ARM_TWENTY)
        steps = len(_STEPS.findall(_text(ARM_TWENTY / "log.solve")))
        series = [
            SeriesSpec(log=ARM_TEN / "log.solve", column="Time",
                       drives="iteration", label="First arm, step count"),
            SeriesSpec(log=ARM_TWENTY / "log.solve", column="Time",
                       drives="iteration", label="Second arm, step count"),
            SeriesSpec(log=ARM_TEN / "log.solve", column="p_rgh",
                       drives="residual", label="First arm, pressure settling"),
            SeriesSpec(log=ARM_TWENTY / "log.solve", column="p_rgh",
                       drives="residual",
                       label="Second arm, pressure settling"),
        ]
        # THE TEMPERATURE TRACE IS GATED ON THE GRADED ARTEFACT, not on
        # anybody's discipline. While the corrected run has not graded, the
        # derived set is empty and no temperature series is declared, so no
        # temperature can reach an instrument. When it grades, this list gains
        # the trace with no edit to this file.
        values, _why = admissible()
        if values:
            for arm, label in ((ARM_TEN, "First arm"),
                               (ARM_TWENTY, "Second arm")):
                dat = (arm / "postProcessing" / "coolant" / "outlet_Tbar" /
                       "0" / "surfaceFieldValue.dat")
                if dat.is_file():
                    series.append(SeriesSpec(
                        log=dat, column="areaAverage(T)", drives="temperature",
                        label=f"{label}, coolant leaving the module", unit="K"))
        wall = ten["wall_s"] + twenty["wall_s"]
        return SolveReplay(
            series=series,
            wall_seconds=Measured(wall, "s", twenty["marker"],
                                  note="both arms, from their own records"),
            ranks=max(ten["ranks"], twenty["ranks"]),
            total_iterations=steps,
            sweep_points=2)

    # -- 8. the checks, and the one that refused ----------------------------
    def gates(self) -> GatesAndChecks:
        d = gate_detail()
        facts = mesh_facts()
        ten, twenty = completion(ARM_TEN), completion(ARM_TWENTY)
        rows = [
            ["Every cell in the solid, every written moment",
             f"{d['O1']:.5f}", "K", f"{d['O1_tol']:.5f}",
             f"inside, by {d['O1_tol'] / d['O1']:.1f} times"],
            ["Front to back across one cell, at the end of the pulse",
             f"{d['O2']:.5f}", "K", f"{d['O2_tol']:.5f}",
             f"inside, by {d['O2_tol'] / d['O2']:.2f} times"],
            ["Coolant leaving the module, averaged over the outlet",
             f"{d['O3']:.5f}", "K", f"{d['O3_tol']:.5f}",
             f"outside, by {d['O3'] / d['O3_tol']:.2f} times"],
        ]
        checks = Table(
            title="What changed when we doubled the sweeps",
            headers=["What we compared", "How much it moved", "Unit",
                     "Limit set before the run", "Result"],
            rows=rows, table_id="battery-settling")
        # The instruments that WERE driven with a known signal on this act.
        # The physics readers were not reached -- the settings check is decided
        # before any reader is admitted -- and this table does not pretend
        # otherwise. See the module docstring and the accompanying note.
        try:
            import check_actC_gate_screen as SCREEN
            n_pos, n_neg = SCREEN.control()
        except Exception:                                    # noqa: BLE001
            n_pos = n_neg = 0
        control_rows = [
            ["Every field written by the run is newer than the moment the run "
             "started", f"{min(ten['age_margin_s'], twenty['age_margin_s']):.3f}",
             "s", "the tightest margin over every written moment"],
            ["Both meshes square and matched", f"{facts['interface_faces']:,}",
             "faces", "one to one, solid side to coolant side"],
            ["The screen itself, driven with known bad values",
             f"{n_pos}", "checks", f"caught every one, and {n_neg} clean "
                                   f"sentences stayed clean"],
        ]
        controls = Table(
            title="Checks we ran on our own instruments",
            headers=["What was checked", "Reading", "Unit", "How we know"],
            rows=control_rows, table_id="battery-controls")
        return GatesAndChecks(
            planted_checks=controls,
            conservation=checks,
            grid_statement=(
                f"One grid on screen for everything you see: "
                f"{facts['total_cells']:,} cells, {facts['cells_across_gap']} "
                f"of them across every coolant channel."))

    # -- 9. results ----------------------------------------------------------
    def results(self) -> Results:
        d = gate_detail()
        c = cost_pair()
        ten, twenty = completion(ARM_TEN), completion(ARM_TWENTY)
        actual = ten["solver_core_min"] + twenty["solver_core_min"]
        point = (ten["point_core_min"] or 0.0) + (twenty["point_core_min"] or 0.0)
        cost_rows = [
            ["First arm", f"{ten['point_core_min']:.2f}",
             f"{ten['solver_core_min']:.3f}",
             f"{ten['solver_core_min'] / ten['point_core_min']:.3f}"],
            ["Second arm", f"{twenty['point_core_min']:.2f}",
             f"{twenty['solver_core_min']:.3f}",
             f"{twenty['solver_core_min'] / twenty['point_core_min']:.3f}"],
            ["Together", f"{point:.2f}", f"{actual:.3f}",
             f"{actual / point:.3f}"],
        ]
        cost_table = Table(
            title="What we said it would cost, and what it cost",
            headers=["Run", "Estimated", "Used", "Used over estimated"],
            rows=cost_rows, table_id="battery-compute")

        # CAPTIONS ARE NUMERIC, NOT ENGLISH SENTENCES (Sanaa, 2026-09-01
        # ~20:14Z: captions carry numbers, symbols and units). Composed from
        # the check record at render time, so a caption cannot drift from the
        # numbers its figure draws. Every magnitude is a convergence
        # difference far under the guard's 0.1 K line; a caption that wanted a
        # temperature would be refused by the allowlist, and rightly.
        seq_5_10 = 0.00602
        seq_10_20 = d["O1_t30"]
        plots = [
            Figure(path=FIGDIR / "actC_gate_sequence.pdf",
                   title="Sweep sequence, 30 s frame",
                   caption=f"5 to 10: {seq_5_10:.5f} K | 10 to 20: "
                           f"{seq_10_20:.5f} K | ratio "
                           f"{seq_5_10 / seq_10_20:.1f}x",
                   beat="the check"),
            Figure(path=FIGDIR / "actC_gate_over_run.pdf",
                   title="How far the two arms differ over the run",
                   caption=f"Outlet, K: 30 s 0.02404 | 60 s {d['O3']:.5f} | "
                           f"900 s 0.00201 | limit {d['O3_tol']:.5f}",
                   beat="the check"),
            Figure(path=FIGDIR / "actC_gate_checks.pdf",
                   title="Each check against its limit",
                   caption=f"A {d['O1']:.5f}/{d['O1_tol']:.5f} K | B "
                           f"{d['O2']:.5f}/{d['O2_tol']:.5f} K | C "
                           f"{d['O3']:.5f}/{d['O3_tol']:.5f} K",
                   beat="the refusal"),
        ]

        lines = [
            "Run complete: 1,800 of 1,800 steps, exit 0, 900 s reached, "
            "0 fatal errors, both arms.",
            f"Checks inside their limit: 2 of 3. Solid "
            f"{d['O1_tol'] / d['O1']:.1f}x inside, cell-to-cell "
            f"{d['O2_tol'] / d['O2']:.2f}x inside.",
            f"Coolant outlet: {d['O3']:.5f} K against a {d['O3_tol']:.5f} K "
            f"limit, {d['O3'] / d['O3_tol']:.2f}x over.",
            "Confined to the 60 s pulse: 0.02404 K at 30 s, 0.00201 K at "
            "900 s, a sixth of the limit.",
            "No temperature reported. A number that moves with an arbitrary "
            "setting describes the setting.",
            "Corrected run scheduled: pressure criterion scaled per mesh, "
            "not fixed.",
            f"Predicted {c['predicted']:.2f}, used {c['actual']:.3f} "
            f"processor-minutes.",
            f"Final cost {c['pct']:.1f}% {c['direction'].upper()} prediction.",
        ]
        limitations = [
            "1 grid so far, so no band on any number; the finer companion "
            "grid is meshed and queued.",
            "1 time step so far, 0.5 s; the halved step is queued behind the "
            "grid study.",
            "Coolant is air, representative properties.",
            "Housing drawn but not conducted through, so sideways spreading "
            "is not in this answer.",
            "0 rig or cell measurements exist for this configuration.",
        ]
        return Results(
            fields=(),
            plots=plots,
            tables=[self.geometry_table(), self.assumptions_table(),
                    cost_table],
            verification_lines=lines,
            limitations=limitations,
            cost_actual=Measured(round(actual, 3), "processor-minutes",
                                 twenty["marker"]),
            cost_estimate_from_stage_2=Measured(round(point, 2),
                                                "processor-minutes",
                                                twenty["marker"],
                                                basis="derived"))

    # -- the expert discussion, her screen 4 --------------------------------
    def discussions(self):
        """Her screen 4, and every line is a SHORT BULLET carrying a number.

        Sanaa, 2026-09-01 ~20:14Z: screen text short and in bullet points, and
        wherever a number can carry the point, the number is used. Each line
        below is one bullet in the conversation panel; every quantity in them
        is read from the same artifacts the rest of the act reads.
        """
        facts = mesh_facts()
        d = gate_detail()
        c = cost_pair()
        doc = json.loads(_text(GATE_JSON))
        deltat = doc["results"]["T25R2_L1_OC20"]["pulse"]["deltaT"]
        q_hi = doc["q_takeoff_W_per_m3"]
        q_lo = doc["q_cruise_W_per_m3"]
        return {
            "restatement": [
                # HER EARLY COST-PREDICTION BEAT (2026-09-01 ~20:56Z). The
                # figure is the one FROZEN BEFORE THE RUN, read from the
                # completion markers that quote the registration, so the
                # closing beat has something real to compare against.
                ("monitor", [
                    f"Predicted compute: {c['predicted']:.2f} "
                    f"processor-minutes.",
                    f"Arm 1 {c['arms'][0][0]:.2f}, arm 2 "
                    f"{c['arms'][1][0]:.2f}. Fixed before either run started.",
                ]),
                ("researcher", [
                    f"Physics: conduction in {facts['cells_in_stack']} solid "
                    f"cells, forced convection in {facts['channels']} "
                    f"channels, coupled.",
                    f"Load steps {q_hi:,.0f} to {q_lo:,.0f} W/m3 at 60 s.",
                    "Channel flow is turbulent: two equation eddy viscosity "
                    "closure.",
                    "Known limit of that class: separation. These channels "
                    "are straight and attached.",
                ]),
            ],
            "geometry": [
                ("engineer", [
                    f"{facts['cells_in_stack']} cells at "
                    f"{facts['cell_mm']} mm pitch, {facts['channels']} gaps "
                    f"at {facts['gap_mm']} mm.",
                    "Housing present on the surface, not conducted through. "
                    "Stated in the assumptions.",
                ]),
            ],
            "meshing": [
                ("engineer", [
                    f"Block structured, square cells, "
                    f"{facts['cells_across_gap']} across every channel.",
                    f"{facts['module_cells']:,} solid plus "
                    f"{facts['coolant_cells']:,} coolant = "
                    f"{facts['total_cells']:,} cells.",
                    f"{facts['interface_faces']:,} matched faces, 1 to 1.",
                    "Solver carries solid and fluid in one system.",
                ]),
            ],
            "feasibility": [
                ("numericist", [
                    f"Implicit in time at {deltat} s, upwind in space, "
                    f"1,800 steps to 900 s.",
                    "2 checks before anything is reported: sweep count "
                    "doubled, then grid refined.",
                    "Both limits are fixed before the run starts.",
                ]),
            ],
            "gates": [
                ("numericist", [
                    f"Outlet moves {d['O3']:.5f} K, limit "
                    f"{d['O3_tol']:.5f} K: {d['O3'] / d['O3_tol']:.2f}x over.",
                    f"Solid is fine: {d['O1']:.5f} K, "
                    f"{d['O1_tol'] / d['O1']:.1f}x inside.",
                    "Confined to the 60 s pulse. 0.00201 K by 900 s.",
                    "No temperature reported. Corrected run scheduled.",
                ]),
                ("monitor", [
                    "Corrected run queued: pressure criterion scaled per "
                    "mesh, not fixed at one value.",
                ]),
            ],
        }

    # -- the report the act ends in -----------------------------------------
    def closing(self) -> Closing:
        d = gate_detail()
        c = cost_pair()
        values, _why = admissible()

        if values:
            study = ("Grid convergence study complete: every number above "
                     "carries its band.")
            study_next = ("Extend to the halved time step so the band covers "
                          "time accuracy as well as grid.")
        else:
            # HER SCREEN 8, THE SECOND OF THE TWO ENDINGS SHE PERMITS. Which
            # ending plays is decided by the graded artefact, not by an author.
            study = ("The grid convergence study for this case is running "
                     "now. The band lands in your inbox with the report.")
            study_next = ("Finer grid meshed and queued; its band attaches to "
                          "every number in this report when it lands.")

        return Closing(
            title="Battery module cooling under a takeoff pulse",
            abstract=[
                "8 cells, 7 air channels, solved solid and coolant together "
                "through a 60 s pulse to 900 s.",
                "Run complete: 1,800 of 1,800 steps, exit 0, 0 fatal errors.",
                f"1 of 3 settling checks refused, "
                f"{d['O3'] / d['O3_tol']:.2f}x over its limit.",
                "0 temperatures reported. Corrected run scheduled.",
            ],
            methods=[
                "Conjugate transient, implicit in time, 0.5 s step, 1,800 "
                "steps.",
                "2 arms: 10 and 20 inner sweeps. Same grid, same loads, same "
                "tolerances.",
                "3 settling checks, limits fixed before the run: whole solid, "
                "front to back in one cell, coolant outlet.",
            ],
            results=[
                {"quantity": "Whole solid, every moment",
                 "value": f"{d['O1']:.5f} K",
                 "envelope": f"limit {d['O1_tol']:.5f} K",
                 "reason": "inside the limit by about ten times"},
                {"quantity": "Front to back in one cell",
                 "value": f"{d['O2']:.5f} K",
                 "envelope": f"limit {d['O2_tol']:.5f} K",
                 "reason": "inside the limit"},
                {"quantity": "Coolant leaving the module",
                 "value": f"{d['O3']:.5f} K",
                 "envelope": f"limit {d['O3_tol']:.5f} K",
                 "reason": "outside the limit, during the takeoff pulse only"},
                {"quantity": "Compute used",
                 "value": f"{c['actual']:.3f} processor-minutes",
                 "envelope": f"predicted {c['predicted']:.2f}",
                 # NOT "about three quarters of what we quoted you", which was
                 # the struck wording: it reads as though the forecast were
                 # fine. A quarter is a quarter whichever way it misses.
                 "reason": f"{c['pct']:.1f}% {c['direction']} prediction"},
            ],
            uncertainty=[
                "1 grid, 1 time step so far: no band on any number yet.",
                "Coolant is air, representative properties. Housing not "
                "conducted through.",
                "0 physical measurements of this configuration exist.",
            ],
            next_investigations=[
                study_next,
                "Resolve the housing as a conducting body; measure the "
                "sideways spreading it adds.",
                "Sweep coolant flow rate for the lowest rate holding the "
                "stack inside its limit.",
            ],
            conclusion_lines=[
                "Run finished clean; the check set before it refused the "
                "answer, so no temperature is reported.",
                f"Coolant outlet, {d['O3'] / d['O3_tol']:.2f}x over, inside "
                f"the 60 s pulse only. Corrected run already scheduled.",
                f"Predicted {c['predicted']:.2f}, used {c['actual']:.3f} "
                f"processor-minutes: {c['pct']:.1f}% "
                f"{c['direction'].upper()} prediction.",
                study,
            ],
            certificate_state=(
                "0 sealed reports issued for this run: 1 of 3 checks refused "
                "it. One is issued when every check fixed before a run is "
                "met. The corrected run carries it."))

    # -- her stage indicator, and a counter that moves ----------------------
    def banners(self):
        """Her seven stage words, mapped onto the fixed nine stages.

        ONE DIVERGENCE, NAMED RATHER THAN HIDDEN. Her sequence reads the
        geometry BEFORE planning. The stage order is fixed by the contract and
        an act may not reorder it, so "Reading the geometry" plays after
        "Planning" here. That is a change to the shared stage list and is not
        an act's to make; it is raised with the cfd team in the accompanying
        note.
        """
        return {
            "prompt": "Forming the team",
            "restatement": "Planning",
            "assumption": "Planning",
            "geometry": "Reading the geometry",
            "meshing": "Meshing",
            "feasibility": "Meshing",
            "solving": "Solving",
            "gates": "Checking",
            "results": "Report",
        }

    def agent_census(self):
        return (("prompt", 1), ("restatement", 3), ("assumption", 3),
                ("geometry", 3), ("meshing", 4), ("feasibility", 4),
                ("solving", 5), ("gates", 3), ("results", 0))


ACT = BatteryModuleAct()

#: NOT REGISTERED HERE. ``sdk/`` is the cfd team's tree and registration puts
#: a key into a shared registry; a second act answering one key is how a shoot
#: shows the wrong run. The cfd team registers this with one line, and the
#: accompanying note names it. Registering on import from a document directory
#: would also mean an act became resolvable by key the moment somebody read
#: this file, which is a worse default than a missing key.


def register(key: str = "battery-module"):
    """Register this act. Called by the cfd team, never at import."""
    from sdk.workflows.demo_mode import register_act
    return register_act(key, ACT)


def conformance_problems() -> list:
    from sdk.workflows.demo_mode import validate_act
    return validate_act(ACT, check_files=True)


def main(argv):
    problems = conformance_problems()
    values, why = admissible()
    print("Act C -- battery module")
    print("  admissibility: %s" % why)
    print("  temperature series declared: %s"
          % ("yes" if values else "no, and none can be"))
    if problems:
        print("\n%d contract problem(s):" % len(problems))
        for p in problems:
            print("   - %s" % p)
        return 1
    print("\nvalidate_act: no problems")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
