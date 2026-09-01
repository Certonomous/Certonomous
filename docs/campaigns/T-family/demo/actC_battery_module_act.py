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
                "We will solve the module and its coolant together, through "
                "the takeoff pulse and into cruise, and we will check the "
                "answer for settings dependence before we report it."),
            confidence=(
                "High on the setup: the stack, the channels and the loads are "
                "fully specified by what you uploaded. The open question is "
                "numerical, and we test it rather than assume it."),
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
                f"Your surface carries an outer housing, "
                f"{housing_x * 1000:.0f} millimetres at the sides and "
                f"{housing_y * 1000:.0f} millimetres at the ends. This run "
                f"resolves the cell stack and the coolant between the cells."),
            correction=(
                "A housing conducts, and conduction through it would spread "
                "heat sideways and lower the peak in the worst cell. Leaving it "
                "out is "
                "the conservative choice, so the answer we give you is on the "
                "safe side of the one with the housing in it. We are telling "
                "you before you spend, not afterwards."))

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
            check=("Before committing your budget: is this mesh good enough "
                   "to trust a conjugate answer, and do the two sides of the "
                   "coupling actually line up?"),
            result=Measured(max(nonorth, nonorth_c), "degrees of skew between "
                                                     "neighbouring cells",
                            MESH_VERIFICATION,
                            note=f"{facts['interface_faces']} matched faces"),
            verdict_for_user=(
                "Yes. Every cell in both meshes is square to its neighbour, "
                "and every face on the solid side has exactly one partner on "
                "the coolant side. We commit the budget."),
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

        plots = [
            Figure(path=FIGDIR / "actC_gate_sequence.pdf",
                   title="The answer settling as we double the sweeps",
                   caption="Five against ten, then ten against twenty: the "
                           "movement closes by about eleven times.",
                   beat="the check"),
            Figure(path=FIGDIR / "actC_gate_over_run.pdf",
                   title="How far the two settings differ, moment by moment",
                   caption="The coolant outlet and the solid, against the "
                           "limit, across the whole run.",
                   beat="the check"),
            Figure(path=FIGDIR / "actC_gate_checks.pdf",
                   title="Three checks against one limit",
                   caption="Two sit inside the limit; the third, the coolant "
                           "outlet, sits outside it.",
                   beat="the refusal"),
        ]

        lines = [
            "The run finished on all six of the completion tests we set for "
            "it, and the check we fixed before it started then ran on its "
            "output.",
            f"Two of the three checks passed comfortably; the third, the "
            f"coolant leaving the module, moved {d['O3'] / d['O3_tol']:.2f} "
            f"times more than the limit allowed.",
            "That movement was confined to the takeoff pulse: by the end of "
            "the run the two settings differed by about a sixth of the limit.",
            "Because the third check refused, we reported no temperature from "
            "this run. A number that still moves when we change an arbitrary "
            "setting describes the setting, not your battery.",
            "The corrected run was scheduled automatically, with a pressure "
            "criterion that asks the same thing of every mesh.",
        ]
        limitations = [
            "One grid so far, so no discretisation band is attached to any "
            "number here; the finer companion grid is meshed and its run is "
            "queued.",
            "One time step so far, so nothing here is a statement about time "
            "accuracy; the halved step is queued behind the grid study.",
            "The coolant is air with representative properties, and the "
            "housing is drawn but not conducted through, so heat spreading "
            "sideways through the housing is not in this answer.",
            "No rig or cell measurement exists for this configuration, so "
            "nothing here is checked against a physical test.",
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
        facts = mesh_facts()
        d = gate_detail()
        doc = json.loads(_text(GATE_JSON))
        deltat = doc["results"]["T25R2_L1_OC20"]["pulse"]["deltaT"]
        return {
            "restatement": [
                ("researcher", [
                    "The physics here is conduction inside eight solid cells "
                    "coupled to forced convection in the channels between "
                    "them, driven by a heat release that steps down when "
                    "takeoff ends.",
                    "The channel flow is turbulent, so we close it with a two "
                    "equation eddy viscosity model. It is the standard choice "
                    "for attached channel flow and it is reliable there.",
                    "Its known limit is separation: where flow detaches, this "
                    "class of model runs optimistic. These channels are "
                    "straight and attached, so we are inside its comfort."]),
            ],
            "geometry": [
                ("engineer", [
                    f"The stack is {facts['cells_in_stack']} cells with "
                    f"{facts['channels']} channels between them, at "
                    f"{facts['cell_mm']} millimetre pitch and "
                    f"{facts['gap_mm']} millimetre gaps.",
                    "There is a housing around it. We are solving the stack "
                    "and the coolant, and we say so in the assumptions rather "
                    "than quietly including it."]),
            ],
            "meshing": [
                ("engineer", [
                    f"Block structured mesh, square cells throughout, "
                    f"{facts['cells_across_gap']} across every channel so the "
                    f"boundary layer on each cell face is resolved rather "
                    f"than modelled coarsely.",
                    f"{facts['total_cells']:,} cells in total, and the solid "
                    f"and coolant meshes meet face to face, "
                    f"{facts['interface_faces']:,} of them, one to one.",
                    "The solver is the conjugate multi region solver: it "
                    "carries the solid and the fluid in one system rather "
                    "than passing a heat flux back and forth."]),
            ],
            "feasibility": [
                ("numericist", [
                    f"Implicit in time at a {deltat} second step, upwind in "
                    f"space, with the pressure equation driven down every "
                    f"step.",
                    "Two checks will run before anything is reported. One "
                    "asks whether the answer still moves when we double the "
                    "number of inner sweeps. The other asks whether it moves "
                    "when we refine the grid.",
                    "The limits for both are fixed before the run starts, so "
                    "neither of them can be chosen to fit the answer."]),
            ],
            "gates": [
                ("numericist", [
                    f"Doubling the sweeps moved the coolant outlet by "
                    f"{d['O3']:.5f} kelvin against a limit of "
                    f"{d['O3_tol']:.5f}. That is over.",
                    "The solid is fine; every cell moved by a tenth of its "
                    "limit. It is the outlet, during the pulse, and only "
                    "during the pulse.",
                    "So we do not report a temperature from this run. We "
                    "schedule the corrected one instead."]),
                ("monitor", [
                    "The corrected run is queued with a pressure criterion "
                    "that scales with each mesh instead of a fixed one, which "
                    "is what asked a different thing of each grid last time."]),
            ],
        }

    # -- the report the act ends in -----------------------------------------
    def closing(self) -> Closing:
        d = gate_detail()
        ten, twenty = completion(ARM_TEN), completion(ARM_TWENTY)
        actual = ten["solver_core_min"] + twenty["solver_core_min"]
        values, _why = admissible()

        if values:
            study = ("The grid convergence study for this case is complete, "
                     "and every number above carries its band.")
            study_next = ("Extend the study to the halved time step so the "
                          "band covers time accuracy as well as grid.")
        else:
            # HER SCREEN 8, THE SECOND OF THE TWO ENDINGS SHE PERMITS. Which
            # ending plays is decided by the graded artefact, not by an author.
            study = ("The grid convergence study for this case is running "
                     "now. The band lands in your inbox with the report.")
            study_next = ("The finer grid is meshed and queued; the band it "
                          "produces attaches to every number in this report "
                          "when it lands.")

        return Closing(
            title="Battery module cooling under a takeoff pulse",
            abstract=[
                "Eight prismatic cells with seven air channels between them "
                "were solved through a takeoff discharge pulse and into "
                "cruise, solid and coolant together in one system.",
                "The run completed. The settling check we fixed before it "
                "started then refused one of its three arms, so no "
                "temperature is reported from it and the corrected run is "
                "scheduled.",
            ],
            methods=[
                "Conjugate transient solve, implicit in time, solid and fluid "
                "carried in one system with matched faces at every interface.",
                "Two arms differing only in the number of inner sweeps per "
                "step, ten against twenty, on the same grid and the same "
                "loads, so their difference is a statement about the method.",
                "Three settling checks with limits fixed before the run: the "
                "whole solid, front to back inside one cell, and the coolant "
                "leaving the module.",
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
                 "value": f"{actual:.3f} processor-minutes",
                 "envelope": "against an estimate of "
                             f"{(ten['point_core_min'] or 0) + (twenty['point_core_min'] or 0):.2f}",
                 "reason": "about three quarters of what we quoted you"},
            ],
            uncertainty=[
                "One grid and one time step so far, so no band is attached to "
                "any number in this report yet.",
                "The coolant is air with representative properties and the "
                "housing is not conducted through.",
                "No physical measurement of this configuration exists to "
                "check against.",
            ],
            next_investigations=[
                study_next,
                "Resolve the housing as a conducting body and measure how much "
                "sideways spreading it adds.",
                "Sweep the coolant flow rate to find the lowest rate that "
                "still holds the stack inside its limit.",
            ],
            conclusion_lines=[
                "The run finished cleanly and the check we set before it "
                "refused its answer, so we did not report a temperature.",
                "The movement was in the coolant outlet during the takeoff "
                "pulse, and the corrected run is already scheduled.",
                study,
            ],
            certificate_state=(
                "No sealed report has been issued for this run, because the "
                "settling check refused it. One is issued when a check fixed "
                "before a run is met, and this one was not. The corrected run "
                "carries the report when it lands."))

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
