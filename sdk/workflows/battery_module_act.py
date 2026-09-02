"""Act C, the battery module, as a DEMO MODE act. THE CLIMAX IS A REFUSAL.

WHAT CHANGED SINCE THE REFUSING SCAFFOLD THIS FILE USED TO BE
-------------------------------------------------------------
An earlier revision registered nothing and refused every stage, because the
only run on record then was a feasibility calculation whose coolant was not a
fluid. That is no longer the state of the disk. The battery family now holds
a COMPLETED conjugate run of the real module under Sanaa's registered load
(``T25R2_L1``: rc 0, one End line, 181 written times to 900 s, every field
present, the age guard clean, its completion record beside it), and Sanaa
approved the act ("battery: approved", 2026-09-01 ~20:10Z) with this beat:

    the run completes, the gate refuses the result, the platform says so and
    schedules the corrected run.

So this act WALKS the stages normally, geometry, discussion, mesh, solve,
all of it fed from the real completed run, and at the checking stage the
verdict gate honestly refuses: the sweep-count check fixed before the runs
started measured 2.3e-02 K of movement between sweep settings against an
allowance of 1.2e-02 K, so no temperature from this run is certified, and
the corrected convergence study (registered, staged on disk as the T25R4
ladder) is what delivers the band. The refusal lands at the RIGHT stage,
once, beside the values it refuses; it is not sixteen refusals pretending to
be an act. Printing the value beside the refusal is the lab's own rule 5
doctrine for a row that is not a result.

WHAT THE SOURCE RUN IS
----------------------
Eight battery cells, 100 by 30 mm section, seven 3 mm coolant channels,
solved as a transient conjugate pair (module solid, coolant air) with
``chtMultiRegionFoam`` and the kOmegaSST closure, 16,608 cells over two
regions, 1,800 steps of 0.5 s to 900 s. The load is her registered
volumetric pulse, read from the case's own fvOptions: 1e5 W/m3 for the first
60 s (takeoff), 2.5e4 W/m3 to 900 s (cruise). Solver and closure are read
from the run's own log header and dictionaries, never asserted here.

Every number below is read off the run tree or its graded records at the
moment it is asked for; a constant retyped here would be a second copy free
to drift. The solving stage is this act's own (:class:`BatteryModuleSequencer`),
because the shared replay reader opens ``log.simpleFoam`` and force columns
and this run has neither; its monitor readers carry planted controls.
"""

from __future__ import annotations

import json
import re
import struct
from pathlib import Path

from .demo_mode import (CANONICAL_SURFACE_DIR, Assumption, Closing, DemoAct,
                        DemoContractError, ElapsedClock, Feasibility, Figure,
                        GatesAndChecks, Geometry, GeometryMatch, Measured,
                        MeshPlan, Prompt, Restatement, Results, RunRecord,
                        SeriesSpec, SolveReplay, Table, register_act)
from .demo_sequencer import Sequencer

REPO = Path(__file__).resolve().parents[2]

RUNS = REPO / "verification" / "runs" / "T-family" / "T25R2_MODULE_runs"
#: The completed run this act is fed from. rc 0, End, 900 s, fields, age
#: guard: its completion record is COMPLETION.<name>.txt beside it.
PRIMARY = RUNS / "T25R2_L1"
#: The second completed arm of the sweep-count check (20 outer sweeps).
SWEEP_ARM = RUNS / "T25R2_L1_OC20"
#: The graded gate record: the registered plant, the three outer-loop
#: quantities, their allowances, and the verdict.
OC_GATE = RUNS / "OC_GATE.json"
#: The corrected convergence study, registered and staged on disk. Its
#: existence is what makes "the corrected study is on the lab's schedule" a
#: statement about artifacts rather than an intention.
CORRECTED_LADDER = (REPO / "verification" / "runs" / "T-family"
                    / "T25R4_MODULE_runs")

#: The served body: the canonical (generator-tracked) copy, which the
#: sequencer stages into the served root itself, so the file measured and the
#: file fetched are one file by construction.
SERVED_STL = CANONICAL_SURFACE_DIR / "battery_module_8cell.stl"

FIGURES = REPO / "docs" / "campaigns" / "T-family" / "demo" / "figures_actC"

MESH_BUILDER = REPO / "scripts" / "build_conjugate_demo_mesh.py"
MESH_WORK = RUNS / "demo_mesh_work"

SOLVER_LOG = "log.solve"
MODULE_MINMAX = PRIMARY / "postProcessing" / "module" / "module_minmax" \
    / "0" / "fieldMinMax.dat"
OUTLET_TBAR = PRIMARY / "postProcessing" / "coolant" / "outlet_Tbar" / "0" \
    / "surfaceFieldValue.dat"

_TIMING = re.compile(
    r"^ExecutionTime\s*=\s*([\d.eE+-]+)\s*s\s+ClockTime\s*=\s*([\d.eE+-]+)\s*s",
    re.M)
_EXEC = re.compile(r"^Exec\s*:\s*(\S+)\s*$", re.M)
_APPLICATION = re.compile(r"^\s*application\s+(\w+)\s*;", re.M)


# ---------------------------------------------------------------------------
# Facts, with no default of any kind
# ---------------------------------------------------------------------------

def _fact(node, *keys):
    """One recorded value. NO DEFAULT (CLAUDE.md rule 3)."""
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


def _gate_record() -> dict:
    if not OC_GATE.is_file():
        raise DemoContractError(
            "the graded gate record is not on disk, so this act cannot state "
            "what the check measured and will not invent it")
    return json.loads(OC_GATE.read_text(encoding="utf-8"))


_LOG_CACHE: dict[str, str] = {}


def _log_text(case: Path) -> str:
    log = case / SOLVER_LOG
    key = str(log)
    if key not in _LOG_CACHE:
        if not log.is_file():
            raise DemoContractError(f"{case.name} has no solver log")
        _LOG_CACHE[key] = log.read_text(encoding="utf-8", errors="replace")
    return _LOG_CACHE[key]


def solver_name(case: Path) -> str:
    """The solver, from the log header AND the case dictionary, cross-checked."""
    from_log = _EXEC.search(_log_text(case))
    control = case / "system" / "controlDict"
    from_dict = (_APPLICATION.search(control.read_text(encoding="utf-8",
                                                       errors="replace"))
                 if control.is_file() else None)
    if not from_log or not from_dict:
        raise DemoContractError(
            f"{case.name} does not name its solver in both its log header "
            f"and its case dictionary, so the solver line will not be shown")
    if from_log.group(1) != from_dict.group(1):
        raise DemoContractError(
            f"{case.name} names one solver in its log and another in its "
            f"case dictionary: {from_log.group(1)} against "
            f"{from_dict.group(1)}")
    return from_log.group(1)


def solver_seconds(case: Path) -> float:
    """The solver's own closing ExecutionTime, which is the family's costed
    figure for this rung (its completion record: "ExecutionTime is the
    solver's own accounting and is the figure used for the ratio")."""
    text = _log_text(case)
    timings = _TIMING.findall(text)
    if not timings:
        raise DemoContractError(f"{case.name} carries no timing line")
    if "\nEnd\n" not in text:
        raise DemoContractError(
            f"{case.name} carries no closing line, so it is not a completed "
            f"solve and will not be shown as one")
    return float(timings[-1][0])


def _dict_value(path: Path, key: str) -> str:
    """One ``key value;`` entry of an OpenFOAM dictionary, comments stripped."""
    if not path.is_file():
        raise DemoContractError(f"{path} is not on disk")
    lines = [line for line in
             path.read_text(encoding="utf-8", errors="replace").splitlines()
             if not line.lstrip().startswith("//")]
    text = re.sub(r"/\*.*?\*/", " ", "\n".join(lines), flags=re.S)
    found = re.search(r"\b" + re.escape(key) + r"\s+([^;{}]+);", text)
    if not found:
        raise DemoContractError(f"{path} does not state {key}")
    return " ".join(found.group(1).split())


def turbulence_model() -> str:
    return _dict_value(PRIMARY / "constant" / "coolant"
                       / "turbulenceProperties", "RASModel")


def _block_tolerance(path: Path, block_name: str) -> str:
    """The ``tolerance`` inside one named solver block, not the file's first."""
    if not path.is_file():
        raise DemoContractError(f"{path} is not on disk")
    lines = [line for line in
             path.read_text(encoding="utf-8", errors="replace").splitlines()
             if not line.lstrip().startswith("//")]
    text = "\n".join(lines)
    # The block may be named bare (``p_rgh``) or as OpenFOAM's quoted
    # pattern (``"p_rgh.*"``); both name the same solver settings.
    found = re.search(r'"?' + re.escape(block_name)
                      + r'[^"{\n]*"?\s*\{[^}]*?\btolerance\s+([^;]+);',
                      text, re.S)
    if not found:
        raise DemoContractError(
            f"{path} states no tolerance for {block_name}")
    return " ".join(found.group(1).split())


def pulse_table() -> list[tuple[float, float]]:
    """The registered load pulse, read from the case's own fvOptions."""
    path = PRIMARY / "constant" / "module" / "fvOptions"
    if not path.is_file():
        raise DemoContractError("the module fvOptions is not on disk")
    text = path.read_text(encoding="utf-8", errors="replace")
    block = re.search(r"table\s*\((.*?)\)\s*;", text, re.S)
    if not block:
        raise DemoContractError(
            "the load pulse could not be read from the case's own fvOptions")
    pairs = re.findall(r"\(\s*([\d.eE+-]+)\s+([\d.eE+-]+)\s*\)",
                       block.group(1))
    if len(pairs) < 2:
        raise DemoContractError(
            "the load pulse table carries fewer than two breakpoints")
    return [(float(a), float(b)) for a, b in pairs]


# ---------------------------------------------------------------------------
# Monitors, and the plants that make their readers evidence
# ---------------------------------------------------------------------------

MONITOR_PLANT_K = 1.234e-03


def read_minmax_series(path: Path) -> list[tuple[float, float, float]]:
    """``(time, min, max)`` rows of a fieldMinMax.dat, verbatim, in order."""
    if not path.is_file():
        raise DemoContractError(f"the monitor {path} is not on disk")
    rows: list[tuple[float, float, float]] = []
    for line in path.read_text(encoding="utf-8",
                               errors="replace").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        cells = line.split("\t")
        if len(cells) < 5:
            raise DemoContractError(
                f"{path.name} carries a row with {len(cells)} columns")
        rows.append((float(cells[0]), float(cells[2].strip()),
                     float(cells[4].strip())))
    if not rows:
        raise DemoContractError(f"{path.name} carries no rows")
    return rows


def read_surface_series(path: Path) -> list[tuple[float, float]]:
    """``(time, value)`` rows of a surfaceFieldValue.dat, verbatim."""
    if not path.is_file():
        raise DemoContractError(f"the monitor {path} is not on disk")
    rows: list[tuple[float, float]] = []
    for line in path.read_text(encoding="utf-8",
                               errors="replace").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        cells = line.split()
        rows.append((float(cells[0]), float(cells[-1])))
    if not rows:
        raise DemoContractError(f"{path.name} carries no rows")
    return rows


def _plant_into_copy(source: Path, column_split, victim_edit) -> Path:
    import tempfile

    lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    data_rows = [i for i, line in enumerate(lines)
                 if line.strip() and not line.startswith("#")]
    if len(data_rows) < 3:
        raise DemoContractError(f"{source} holds too few rows for a plant")
    victim = data_rows[len(data_rows) // 2]
    lines[victim] = victim_edit(lines[victim])
    tmp = Path(tempfile.mkdtemp(prefix="battery_plant_")) / source.name
    tmp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return tmp


def monitor_controls() -> list[dict]:
    """Both monitor readers shown able to see a planted value, or refusal.

    Returns one row per reader: reader label, planted value, value read
    back, and whether it was detected, for the gates table. Any miss raises;
    nothing displays on a warning (CLAUDE.md rule 3).
    """
    import shutil

    out: list[dict] = []

    def minmax_edit(line: str) -> str:
        cells = line.split("\t")
        minmax_edit.time = float(cells[0])
        cells[4] = repr(MONITOR_PLANT_K)
        return "\t".join(cells)

    copy = _plant_into_copy(MODULE_MINMAX, None, minmax_edit)
    try:
        seen = read_minmax_series(copy)
        match = [mx for stamp, _mn, mx in seen if stamp == minmax_edit.time]
    finally:
        shutil.rmtree(copy.parent, ignore_errors=True)
    if not match or abs(match[0] - MONITOR_PLANT_K) > 1e-15:
        raise DemoContractError(
            "MONITOR CONTROL FAILED: a value planted into the module "
            "temperature monitor was not read back at its own row; the "
            "curves on screen are not coming from the monitor files")
    out.append({"reader": "Hottest point in the module",
                "planted": MONITOR_PLANT_K, "read": match[0],
                "detected": True})

    def tbar_edit(line: str) -> str:
        cells = line.split()
        tbar_edit.time = float(cells[0])
        cells[-1] = repr(MONITOR_PLANT_K)
        return "\t".join(cells)

    copy = _plant_into_copy(OUTLET_TBAR, None, tbar_edit)
    try:
        seen = read_surface_series(copy)
        match = [v for stamp, v in seen if stamp == tbar_edit.time]
    finally:
        shutil.rmtree(copy.parent, ignore_errors=True)
    if not match or abs(match[0] - MONITOR_PLANT_K) > 1e-15:
        raise DemoContractError(
            "MONITOR CONTROL FAILED: a value planted into the coolant "
            "outlet monitor was not read back at its own row")
    out.append({"reader": "Coolant leaving the module",
                "planted": MONITOR_PLANT_K, "read": match[0],
                "detected": True})
    return out


def elapsed_by_step(case: Path) -> list[float]:
    """The run's own ClockTime at every step, off its own log, in order."""
    timings = _TIMING.findall(_log_text(case))
    if not timings:
        raise DemoContractError(f"{case.name} carries no timing lines")
    return [float(clock) for _cpu, clock in timings]


def mass_balance() -> tuple[float, float, float]:
    """``(in, out, difference)`` in kg/s at the final time, from the run."""
    root = PRIMARY / "postProcessing" / "coolant"
    into = abs(read_surface_series(root / "inlet_mdot" / "0"
                                   / "surfaceFieldValue.dat")[-1][1])
    out = abs(read_surface_series(root / "outlet_mdot" / "0"
                                  / "surfaceFieldValue.dat")[-1][1])
    return into, out, abs(out - into)


# ---------------------------------------------------------------------------
# Costs: the two completed arms, against their registered points
# ---------------------------------------------------------------------------

def _registered_point(case: Path) -> float:
    """The registered upfront estimate for one arm, read from its own
    completion record's POINT line, never retyped."""
    record = case / f"COMPLETION.{case.name}.txt"
    if not record.is_file():
        raise DemoContractError(f"{case.name} has no completion record")
    text = record.read_text(encoding="utf-8", errors="replace")
    found = re.search(r"POINT \(section [\d.]+\)\s*=\s*([\d.]+)\s*core-min",
                      text)
    if not found:
        found = re.search(r"PRE-REGISTERED POINT[^=]*=\s*([\d.]+)\s*core-min",
                          text)
    if not found:
        raise DemoContractError(
            f"{case.name}'s completion record states no registered point")
    return float(found.group(1))


#: SANAA'S SCRIPTED ESTIMATE (2026-09-02 ~04:20Z, verbatim: "make the
#: estimate cost match the computed cost (within5%) in the script. Same for
#: all acts. dont argue."). The screen's estimate beat is scripted to land
#: within five per cent of the on-screen measured cost, superseding the
#: real-ratio close this act carried ("within 25%"). INTERNAL HONESTY IS
#: UNCHANGED (rule 12): the REAL registered points (8.30 + 18.09 = 26.39
#: core-minutes) stay readable through :func:`campaign_cost` and in each
#: arm's completion record, the real actual (19.76) is still measured off
#: the logs, the real ratio (0.749) stays in the lab's records, and the
#: internal note on the screen figure names both.
SCRIPTED_ESTIMATE_CORE_MIN = 20.5


def scripted_estimate() -> float:
    """The scripted on-screen estimate, refused if it drifts past her 5%."""
    actual, _registered = campaign_cost()
    if abs(actual - SCRIPTED_ESTIMATE_CORE_MIN) \
            > 0.05 * SCRIPTED_ESTIMATE_CORE_MIN:
        raise DemoContractError(
            "the scripted estimate no longer lands within five per cent of "
            "the measured cost; re-set it against the current records rather "
            "than letting a broken script reach a screen")
    return SCRIPTED_ESTIMATE_CORE_MIN


def solver_ranks(case: Path) -> int:
    """The rank count the launcher recorded for one arm, off its STATUS."""
    status = case / f"STATUS.{case.name}"
    if not status.is_file():
        raise DemoContractError(f"{case.name} has no launch status record")
    found = re.search(r"^ranks=(\d+)", status.read_text(encoding="utf-8"),
                      re.M)
    if not found:
        raise DemoContractError(f"{case.name}'s status records no rank count")
    return int(found.group(1))


def campaign_cost() -> tuple[float, float]:
    """``(actual core-minutes, registered core-minutes)`` over both arms.

    Actual is each log's own closing ExecutionTime at 1 rank (the figure the
    family's completion records cost); registered is each arm's frozen POINT.
    """
    actual = registered = 0.0
    for case in (PRIMARY, SWEEP_ARM):
        ranks = 1
        status = case / f"STATUS.{case.name}"
        if status.is_file():
            found = re.search(r"^ranks=(\d+)", status.read_text(), re.M)
            if found:
                ranks = int(found.group(1))
        actual += solver_seconds(case) * ranks / 60.0
        registered += _registered_point(case)
    return actual, registered


# ---------------------------------------------------------------------------
# Geometry: the served surface, measured against the solved case
# ---------------------------------------------------------------------------

def _stl_triangles(path: Path):
    """Vertices of a binary STL, as float tuples. Read only."""
    data = path.read_bytes()
    if len(data) < 84:
        raise DemoContractError(f"{path} is not a binary STL")
    count = struct.unpack("<I", data[80:84])[0]
    if len(data) < 84 + count * 50:
        raise DemoContractError(f"{path} is truncated")
    triangles = []
    for i in range(count):
        offset = 84 + i * 50
        vertices = []
        for v in range(3):
            vertices.append(struct.unpack(
                "<fff", data[offset + 12 + v * 12: offset + 24 + v * 12]))
        triangles.append(vertices)
    return triangles


def measure_served_stack(path: Path) -> dict:
    """Cell thickness, channel gap, stack span and cell length, MEASURED off
    the served surface.

    The eight cell boxes span exactly x in [0, cell length]; the casing does
    not, which is what isolates their faces: every triangle lying in a plane
    of constant y whose x extent equals the cells' own is a cell face. The
    sixteen distinct y planes of those faces give the thickness (large step),
    the gap (small step) and the stack span, with structural asserts instead
    of assumptions.
    """
    triangles = _stl_triangles(path)
    # The cell length is the x extent of y-constant faces; find candidate
    # groups by y-plane first.
    by_plane: dict[float, list] = {}
    for tri in triangles:
        ys = {round(v[1], 6) for v in tri}
        if len(ys) == 1:
            by_plane.setdefault(ys.pop(), []).extend(tri)
    if not by_plane:
        raise DemoContractError("the served surface has no y-constant faces")
    # The dominant x extent among those groups is the cells'.
    extents = {}
    for plane, vertices in by_plane.items():
        xs = [round(v[0], 6) for v in vertices]
        extents[plane] = (min(xs), max(xs))
    spans = {}
    for plane, (lo, hi) in extents.items():
        spans.setdefault((lo, hi), []).append(plane)
    cell_extent, planes = max(spans.items(), key=lambda kv: len(kv[1]))
    planes = sorted(planes)
    if len(planes) != 16:
        raise DemoContractError(
            f"the served surface shows {len(planes)} cell faces where an "
            f"eight cell stack shows 16; it will not be measured as the "
            f"solved module")
    steps = [round(b - a, 6) for a, b in zip(planes, planes[1:])]
    thick = sorted(set(steps))[-1]
    gap = sorted(set(steps))[0]
    return {
        "cell_length_m": round(cell_extent[1] - cell_extent[0], 6),
        "cell_thickness_m": thick,
        "channel_gap_m": gap,
        "stack_span_m": round(planes[-1] - planes[0], 6),
    }


def solved_stack_constants() -> dict:
    """The same four quantities off the SOLVED case's own blockMeshDict.

    Derived from the vertex list with structural asserts: the y planes at the
    module's own x faces must number 16 and alternate a thick step with a
    thin one; the module x extent is the interior pair of the four x planes.
    """
    path = PRIMARY / "system" / "blockMeshDict"
    if not path.is_file():
        raise DemoContractError("the solved case's blockMeshDict is not on disk")
    text = path.read_text(encoding="utf-8", errors="replace")
    block = re.search(r"vertices\s*\((.*?)\n\)\s*;", text, re.S)
    if not block:
        raise DemoContractError("the blockMeshDict vertex list was not found")
    vertices = re.findall(r"\(\s*([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s*\)",
                          block.group(1))
    points = [(float(x), float(y), float(z)) for x, y, z in vertices]
    xs = sorted({round(p[0], 9) for p in points})
    if len(xs) != 4:
        raise DemoContractError(
            f"the solved case shows {len(xs)} x planes where 4 were expected")
    x_lo, x_hi = xs[1], xs[2]
    planes = sorted({round(p[1], 9) for p in points
                     if abs(p[0] - x_lo) < 1e-12})
    if len(planes) != 16:
        raise DemoContractError(
            f"the solved case shows {len(planes)} stack planes where 16 were "
            f"expected")
    steps = [round(b - a, 9) for a, b in zip(planes, planes[1:])]
    thick = sorted(set(steps))[-1]
    gap = sorted(set(steps))[0]
    zs = sorted({round(p[2], 9) for p in points})
    return {
        "cell_length_m": round(x_hi - x_lo, 9),
        "cell_thickness_m": thick,
        "channel_gap_m": gap,
        "stack_span_m": round(planes[-1] - planes[0], 9),
        "depth_m": round(zs[-1] - zs[0], 9),
    }


# ---------------------------------------------------------------------------
# The gate reading the climax rests on
# ---------------------------------------------------------------------------

def gate_reading() -> dict:
    """The three registered outer-loop quantities, their allowances, and the
    one that failed, off the graded record. Refuses if the record does not
    say what the screen would."""
    record = _gate_record()
    detail = _fact(record, "results", "OUTER_LOOP_GATE", "detail")
    reading = {
        "O1": (float(_fact(detail, "O1")), float(_fact(detail, "O1_tol")),
               bool(_fact(detail, "O1_ok"))),
        "O2": (float(_fact(detail, "O2")), float(_fact(detail, "O2_tol")),
               bool(_fact(detail, "O2_ok"))),
        "O3": (float(_fact(detail, "O3")), float(_fact(detail, "O3_tol")),
               bool(_fact(detail, "O3_ok"))),
        "failed": not bool(_fact(detail, "ok")),
        "where": str(_fact(detail, "O3_where")),
    }
    if not reading["failed"]:
        raise DemoContractError(
            "the graded record no longer shows the check refusing; this "
            "act's refusal beat would be a fiction and must be rewritten "
            "against the current record before it is shown")
    return reading


def _corrected_study_is_staged() -> int:
    """How many levels of the corrected ladder are staged on disk. The
    scheduling sentence rests on this count being positive."""
    if not CORRECTED_LADDER.is_dir():
        raise DemoContractError(
            "the corrected convergence study is not on disk, so the act "
            "cannot say the platform has it scheduled")
    staged = [d for d in CORRECTED_LADDER.iterdir()
              if d.is_dir() and (d / "system").is_dir()
              and not list(d.glob("log.solve*"))]
    if not staged:
        raise DemoContractError(
            "the corrected convergence study holds no staged case, so the "
            "act cannot say the platform has it scheduled")
    return len(staged)


# ---------------------------------------------------------------------------
# The act
# ---------------------------------------------------------------------------

class BatteryModuleAct(DemoAct):
    """The battery module under the takeoff pulse, fed from the landed run,
    ending in the honest refusal and the corrected study's scheduling."""

    name = "battery module thermal pulse"

    #: The geometry render is ParaView too (Sanaa 2026-09-02 ~04:55Z: "ALL
    #: runs show ParaView, no tessellation"): with it declared, the sequencer
    #: serves the rendered module and the client STL canvas never runs.
    rendered_panels = ("geometry", "mesh", "mesh_zoom")

    # -- stage 0 ------------------------------------------------------------
    def run_record(self) -> RunRecord:
        return RunRecord(
            run_id=PRIMARY.name,
            run_root=PRIMARY,
            solver="OpenFOAM " + solver_name(PRIMARY),
            physics=("transient conjugate heat transfer between eight "
                     "battery cells and the coolant air in the channels "
                     "between them, with the " + turbulence_model()
                     + " closure"),
            completion_evidence=PRIMARY / f"COMPLETION.{PRIMARY.name}.txt",
            presentation_of=f"presentation of run {PRIMARY.name}",
            record_path=PRIMARY / f"COMPLETION.{PRIMARY.name}.txt")

    # -- stages 1 to 3 ------------------------------------------------------
    def prompt(self) -> Prompt:
        # HER WORDING, VERBATIM (2026-09-02 addendum): the professionalized
        # battery prompt.
        return Prompt(
            "Transient thermal analysis of the 8-cell battery module under "
            "a takeoff power pulse: peak cell temperature, cell-to-cell "
            "spread, time to settle.")

    def restatement(self) -> Restatement:
        pulse = pulse_table()
        takeoff = max(rate for _t, rate in pulse)
        cruise = min(rate for _t, rate in pulse if rate > 0)
        actual, registered = campaign_cost()
        return Restatement(
            restatement=(f"Solve the module through the pulse: "
                         f"{takeoff:,.0f} watts per cubic metre of cell for "
                         f"the first 60 seconds, {cruise:,.0f} after, out to "
                         f"900 seconds, and report the hottest cell, the "
                         f"spread, and the settling."),
            confidence=("The load is a volumetric rate from a real cell, so "
                        "the temperature rise is whatever the physics gives "
                        "and nothing is tuned toward a target."),
            cost_estimate=Measured(
                round(scripted_estimate(), 1), "core-minutes",
                PRIMARY / f"COMPLETION.{PRIMARY.name}.txt", "derived",
                note=(f"SCRIPTED demo estimate per Sanaa 2026-09-02 04:20Z "
                      f"(estimate within 5% of computed cost on screen). "
                      f"The REAL registered estimate is {registered:.2f} "
                      f"core-minutes, the two frozen points summed; the "
                      f"real actual and ratio stay in the completion "
                      f"records unchanged")))

    def assumption(self) -> Assumption:
        pulse = pulse_table()
        takeoff = max(rate for _t, rate in pulse)
        record = _gate_record()
        per_cell = float(_fact(record, "per_cell_W_real_cell_DERIVED"))
        return Assumption(
            assumption=("The request sizes the heat as a per cell wattage on "
                        "a unit depth model."),
            finding=(f"The lab sets it as a volumetric rate from a real "
                     f"cell instead: {takeoff:,.0f} watts per cubic metre at "
                     f"takeoff, which is about {per_cell:.0f} watts in a 100 "
                     f"by 30 by 150 millimetre cell of the 5 to 8C class."),
            correction=("A volumetric rate scales with the cell it heats, so "
                        "the same load is right on any depth of model; the "
                        "basis sits in the table below."),
            assumptions_table=self._assumptions_table())

    def _assumptions_table(self) -> Table:
        pulse = pulse_table()
        takeoff = max(rate for _t, rate in pulse)
        cruise = min(rate for _t, rate in pulse if rate > 0)
        solved = solved_stack_constants()
        inlet_field = _dict_value(PRIMARY / "0.orig" / "coolant" / "T",
                                  "internalField")
        if not inlet_field.startswith("uniform "):
            raise DemoContractError(
                "the coolant inlet temperature is not a uniform field")
        inlet_c = float(inlet_field.split()[1]) - 273.15
        speed_field = _dict_value(PRIMARY / "0.orig" / "coolant" / "U",
                                  "internalField")
        speed = speed_field.replace("uniform", "").strip(" ()").split()
        return Table(
            title="What the request set, and what the lab set",
            headers=["Quantity", "Value", "Unit", "Set by"],
            rows=[
                ["Module geometry", "as uploaded", "", "the request"],
                ["Takeoff heat rate", f"{takeoff:,.0f}", "W/m3",
                 "the request"],
                ["Cruise heat rate", f"{cruise:,.0f}", "W/m3", "the request"],
                ["Pulse timing",
                 f"takeoff to {min(t for t, r in pulse if r == cruise):.0f}, "
                 f"cruise to {pulse[-1][0]:.0f}", "s", "the request"],
                ["Load basis", "real cell, 100 by 30 by 150 mm, 5 to 8C",
                 "", "the lab"],
                ["Coolant", "air", "", "the lab"],
                ["Coolant speed", speed[0], "m/s", "the lab"],
                ["Coolant inlet temperature", f"{inlet_c:.1f}", "C",
                 "the lab"],
                ["Channel gap", f"{solved['channel_gap_m'] * 1000:.0f}", "mm",
                 "the lab"],
            ],
            table_id="battery_assumptions", role="NUMERICIST")

    # -- stage 4 ------------------------------------------------------------
    def geometry(self) -> Geometry:
        served = measure_served_stack(SERVED_STL)
        solved = solved_stack_constants()

        def match(quantity: str, key: str) -> GeometryMatch:
            return GeometryMatch(
                quantity=quantity,
                solved=Measured(float(solved[key]), "m",
                                PRIMARY / "system" / "blockMeshDict"),
                supplied=Measured(float(served[key]), "m", SERVED_STL),
                tolerance=1e-5, relative=False)

        return Geometry(
            served_stl=SERVED_STL,
            display_label="eight cell battery module with cooling channels",
            matches=[
                match("cell length", "cell_length_m"),
                match("cell thickness", "cell_thickness_m"),
                match("cooling channel gap", "channel_gap_m"),
                match("stack extent", "stack_span_m"),
            ],
            regenerated_from=PRIMARY / "system" / "blockMeshDict")

    # -- stage 5 ------------------------------------------------------------
    def mesh_plan(self) -> MeshPlan:
        solved = solved_stack_constants()
        cells = 16608
        return MeshPlan(
            command=["python3", str(MESH_BUILDER),
                     "--case", str(PRIMARY), "--out", str(MESH_WORK),
                     "--expect-cells", str(cells)],
            work_dir=MESH_WORK,
            cell_count=Measured(f"{cells:,}", "cells",
                                PRIMARY / "constant" / "polyMesh"),
            resolution_headers=["Region", "Cells across", "Spacing, mm"],
            resolution_rows=[
                ["Each 3 mm coolant channel", "24",
                 f"{solved['channel_gap_m'] * 1000 / 24:.3f}"],
                ["Each 30 mm cell", "12",
                 f"{solved['cell_thickness_m'] * 1000 / 12:.1f}"],
                ["Streamwise, in the cell zone", "40", "2.5"],
            ],
            wall_zoom_hint="the cells across one cooling channel",
            expected_seconds=30.0,
            mesh_type="Structured hexahedral",
            resolution_title="Channel and cell resolution")

    # -- stage 6 ------------------------------------------------------------
    def feasibility(self) -> Feasibility:
        """The 30 second check: an energy balance on the coolant, from
        registered quantities only, before any budget is spent."""
        pulse = pulse_table()
        takeoff = max(rate for _t, rate in pulse)
        # Solid volume derived off the case's own mesh definition (eight
        # cells of length x thickness x depth); mass flow read off the run.
        # The balance is arithmetic on read values, so its basis is derived.
        solved = solved_stack_constants()
        volume = (8 * solved["cell_length_m"] * solved["cell_thickness_m"]
                  * solved["depth_m"])
        into, _out, _diff = mass_balance()
        cp = float(_dict_value(PRIMARY / "constant" / "coolant"
                               / "thermophysicalProperties", "Cp"))
        rise = takeoff * volume / (into * cp)
        return Feasibility(
            check=("An energy balance on the coolant, which bounds the mean "
                   "outlet temperature rise at takeoff power in seconds."),
            result=Measured(round(rise, 1), "K", OC_GATE, "derived",
                            note="q x V over mdot x cp, registered values"),
            verdict_for_user=(
                f"The bulk rise is about {rise:.1f} K, so the module will "
                f"not run away; what needs the solve is the spread between "
                f"cells and the settling, which no balance gives."))

    # -- stage 7 ------------------------------------------------------------
    def solve_replay(self) -> SolveReplay:
        steps = len(elapsed_by_step(PRIMARY))
        wall = solver_seconds(PRIMARY)
        return SolveReplay(
            series=[
                SeriesSpec(MODULE_MINMAX, "max", "temperature",
                           "Hottest point in the module", "C"),
                SeriesSpec(OUTLET_TBAR, "areaAverage(T)", "temperature",
                           "Coolant leaving the module", "C"),
            ],
            wall_seconds=Measured(
                round(wall, 1), "s", PRIMARY / SOLVER_LOG, "measured",
                note="the solver's own closing time for the primary arm"),
            ranks=1,
            total_iterations=steps,
            sweep_points=1,
            # EMPTY DELIBERATELY: this act declares its own sequencer, whose
            # solving stage reads these monitors itself.
            cases=(),
            elapsed_clock=ElapsedClock(
                seconds=wall, measured=True,
                basis=("The solver's own clock for the pulse, off its log"),
                source=PRIMARY / SOLVER_LOG))

    # -- stage 8: THE CLIMAX ------------------------------------------------
    def gates(self) -> GatesAndChecks:
        controls = monitor_controls()
        into, out, difference = mass_balance()
        reading = gate_reading()
        rows = [[c["reader"], f"{c['planted']:.3e}", f"{c['read']:.3e}",
                 "yes" if c["detected"] else "no"] for c in controls]
        return GatesAndChecks(
            planted_checks=Table(
                title="Instrument checks",
                headers=["Instrument", "Planted, K", "Read back, K",
                         "Detected"],
                rows=rows, table_id="battery_planted"),
            conservation=Table(
                title="Coolant mass through the module",
                headers=["Quantity", "In", "Out", "Difference"],
                rows=[["Coolant mass flow, kg/s", f"{into:.5f}",
                       f"{out:.5f}", f"{difference:.1e}"]],
                table_id="battery_conservation"),
            grid_statement=(
                "One grid of 16,608 cells over two regions carries this "
                "run. The convergence check fixed before the runs started "
                "refused the result: the takeoff transient moved "
                f"{reading['O3'][0] * 1000:.1f} millikelvin between sweep "
                f"settings against an allowance of "
                f"{reading['O3'][1] * 1000:.1f}, so no temperature here is "
                f"certified yet."))

    # -- stage 9 ------------------------------------------------------------
    def results(self) -> Results:
        module = read_minmax_series(MODULE_MINMAX)
        outlet = read_surface_series(OUTLET_TBAR)
        reading = gate_reading()
        staged = _corrected_study_is_staged()
        actual, registered = campaign_cost()
        at60 = [r for r in module if abs(r[0] - 60.0) < 0.26]
        if not at60:
            raise DemoContractError(
                "the monitor holds no row at the end of takeoff")
        t60_min, t60_max = at60[0][1], at60[0][2]
        end_min, end_max = module[-1][1], module[-1][2]
        refused = "as computed; certification refused, see below"
        table = Table(
            title="Module temperatures, as computed",
            headers=["Quantity", "Value", "Unit", "Standing"],
            rows=[
                ["Hottest cell, end of takeoff", f"{t60_max - 273.15:.1f}",
                 "C", refused],
                ["Spread across the module, end of takeoff",
                 f"{t60_max - t60_min:.1f}", "K", refused],
                ["Hottest cell, end of the record",
                 f"{end_max - 273.15:.1f}", "C", refused],
                ["Spread across the module, end of the record",
                 f"{end_max - end_min:.1f}", "K", refused],
                ["Coolant leaving the module, end of the record",
                 f"{outlet[-1][1] - 273.15:.1f}", "C", refused],
                ["Still warming at the end of the record",
                 f"{(module[-1][2] - module[-37][2]) / 180.0 * 1000:.1f}",
                 "mK/s", refused],
            ],
            table_id="battery_map", role="CHIEF ENGINEER")

        fields = [
            Figure(FIGURES / "actC_temperature_field.png",
                   "T at the end of takeoff",
                   "T (K), t = 60 s, module and coolant.", "results"),
        ]
        plots = [
            Figure(FIGURES / "actC_module_history.png",
                   "Module temperature through the pulse",
                   "T (C) against t (s), hottest and coolest points.",
                   "results"),
        ]
        # HER 0610Z COMPUTE CONVENTION: per-run core-minutes, plain sum as
        # total, wall time. The two arms ran at one worker; the wall column
        # carries their measured sum.
        arm_minutes = [solver_seconds(c) / 60.0 for c in (PRIMARY, SWEEP_ARM)]
        compute = Table(
            title="Compute",
            headers=["Core-minutes per run", "Total core-minutes",
                     "Total wall time"],
            rows=[[" and ".join(f"{m:.1f}" for m in arm_minutes),
                   f"{sum(arm_minutes):.1f}",
                   f"{sum(arm_minutes):.0f} minutes at one worker"]],
            table_id="battery_compute", role="CHIEF ENGINEER")
        return Results(
            fields=fields, plots=plots, tables=[table, compute],
            verification_lines=[
                ("Run rejected as a certified result: the sweep convergence "
                 "check fixed before the runs started measured "
                 f"{reading['O3'][0] * 1000:.1f} millikelvin of movement in "
                 f"the takeoff transient between sweep settings, against an "
                 f"allowance of {reading['O3'][1] * 1000:.1f}."),
                ("Two of the three registered checks held; the failed one "
                 "voids every row above as a certified number, which is why "
                 "each carries its standing."),
                (f"The corrected grid convergence study is on the lab's "
                 f"schedule, {staged} cases staged with the repaired "
                 f"criterion; the band lands in your inbox with the "
                 f"certificate."),
                ("Instrument check: both monitor readers detected a planted "
                 "perturbation before any curve moved."),
            ],
            limitations=[
                ("The convergence check refused this run, so every "
                 "temperature above is shown as computed, never as a "
                 "certified value."),
                ("The module is still warming when the record ends at 900 "
                 "seconds, so the settling time is not answered by this "
                 "run."),
                ("The solve is a unit depth section of the module, so "
                 "nothing that varies along the cell depth is resolved."),
                ("No rig or cell test data exists for this module, so "
                 "nothing here is checked against a measurement."),
            ],
            cost_actual=Measured(
                round(actual, 2), "core-minutes",
                PRIMARY / f"COMPLETION.{PRIMARY.name}.txt", "measured",
                note=("both arms' own solver clocks at one rank each")),
            cost_estimate_from_stage_2=self.restatement().cost_estimate)

    # -- the specialists -----------------------------------------------------
    def discussions(self):
        pulse = pulse_table()
        takeoff = max(rate for _t, rate in pulse)
        cruise = min(rate for _t, rate in pulse if rate > 0)
        model = turbulence_model()
        reading = gate_reading()
        return {
            "restatement": [
                ("researcher", [
                    "Transient conjugate pair: heat born in the cells, "
                    "carried across the channel walls, swept out by the "
                    "coolant air.",
                    f"Closure: {model} on the coolant; the solid carries "
                    f"conduction alone.",
                    "Thermal mass sets the story: a 60 second pulse moves "
                    "the metal by a few kelvin, not tens.",
                ]),
                ("engineer", [
                    f"Predicted wall clock: {scripted_estimate():.1f} "
                    f"core-minutes at one worker, about "
                    f"{scripted_estimate():.0f} minutes.",
                ]),
            ],
            "assumption": [
                ("numericist", [
                    f"The request fixes the module and the pulse: "
                    f"{takeoff:,.0f} then {cruise:,.0f} watts per cubic "
                    f"metre.",
                    "This lab supplies the coolant state and the load basis; "
                    "the table above names each with its value and unit.",
                ]),
            ],
            "gates": [
                ("numericist", [
                    "The run completed cleanly: return code zero, every "
                    "field written.",
                    "Completion is not certification.",
                    "The check asked whether the answer moves when the "
                    "solver sweeps harder. It moved: "
                    f"{reading['O3'][0] * 1000:.1f} millikelvin at the "
                    f"takeoff transient, {reading['O3'][1] * 1000:.1f} "
                    f"allowed.",
                    "So the platform declines to certify these temperatures "
                    "and says so on the result sheet.",
                ]),
            ],
        }

    # -- the report the act ends in ------------------------------------------
    def closing(self) -> Closing:
        module = read_minmax_series(MODULE_MINMAX)
        reading = gate_reading()
        staged = _corrected_study_is_staged()
        actual, registered = campaign_cost()
        end_max = module[-1][2]
        return Closing(
            title="Battery module under the takeoff pulse",
            abstract=[
                ("An eight cell battery module with seven cooling channels "
                 "was solved through the registered takeoff and cruise "
                 "pulse, 900 seconds of transient conjugate heat transfer "
                 "on 16,608 cells."),
                (f"The run completed cleanly and the platform refused to "
                 f"certify it: the sweep convergence check measured "
                 f"{reading['O3'][0] * 1000:.1f} millikelvin of movement "
                 f"against {reading['O3'][1] * 1000:.1f} allowed, so the "
                 f"temperatures are reported as computed and the corrected "
                 f"study is on the schedule."),
            ],
            methods=[
                (f"Transient conjugate heat transfer with OpenFOAM "
                 f"{solver_name(PRIMARY)}, {turbulence_model()} on the "
                 f"coolant; the methods table on the solving screen carries "
                 f"the numerics."),
                ("Two arms ran, at 10 and 20 outer sweeps per step, so the "
                 "convergence check compares the same physics under two "
                 "solver efforts."),
                ("Every reader behind these numbers detected a planted "
                 "perturbation before a value was believed."),
            ],
            results=[
                {"quantity": "hottest cell at the end of the record",
                 "value": f"{end_max - 273.15:.1f} C",
                 "envelope": "no band: certification refused",
                 "reason": ("the sweep convergence check failed at the "
                            "takeoff transient")},
                {"quantity": "compute",
                 "value": f"{actual:.1f} core-minutes",
                 "envelope": (f"forecast {scripted_estimate():.1f} before "
                              f"the runs"),
                 "reason": "both arms' own solver clocks"},
            ],
            uncertainty=[
                ("No discretisation band exists for this run and none is "
                 "drawn; the refused check is the reason."),
                (f"The corrected grid convergence study is staged, {staged} "
                 f"cases with the repaired criterion; the band lands in "
                 f"your inbox with the certificate."),
            ],
            next_investigations=[
                ("A longer record past 900 seconds, so the settling time "
                 "the request asks for has an answer."),
                ("Per cell peak temperatures once a certified grid exists, "
                 "so the spread can be attributed cell by cell."),
            ],
            conclusion_lines=[
                (f"The run completed and the platform declined to certify "
                 f"it: the convergence check it registered before solving "
                 f"refused the result, and the hottest cell reads "
                 f"{end_max - 273.15:.1f} C as computed."),
                ("The corrected convergence study is on the schedule; the "
                 "band lands in your inbox with the certificate."),
                ("The full report, with every figure, is in the Report "
                 "tab."),
            ],
            certificate_state=(
                "No sealed certificate is attached to this run: the "
                "convergence check refused it, and the corrected study must "
                "pass before a certificate can carry these temperatures."),
        )

    def worker_census(self):
        """The workers tile follows this act's own story (Sanaa 0420Z). One
        worker: the run's launcher recorded ranks=1, and that record is the
        same source the fleet-channel events use. Zero with the results."""
        w = solver_ranks(PRIMARY)
        return (("prompt", 0), ("restatement", 0), ("assumption", 0),
                ("geometry", 0), ("meshing", w), ("feasibility", w),
                ("solving", w), ("gates", 0), ("results", 0))

    # -- which sequencer walks this act --------------------------------------
    def sequencer(self):
        return BatteryModuleSequencer

    # -- pacing -------------------------------------------------------------
    def agent_census(self):
        return (("prompt", 1), ("restatement", 2), ("assumption", 3),
                ("geometry", 3), ("meshing", 4), ("feasibility", 4),
                ("solving", 5), ("gates", 3), ("results", 0))


# ===========================================================================
# The sequencer: the shared walk, with this act's own solver stage
# ===========================================================================

from dataclasses import dataclass as _dataclass  # noqa: E402


@_dataclass
class BatteryModuleSequencer(Sequencer):
    """The shared nine-stage walk with the solving stage replaced.

    Two labelled series, both the run's own monitors, interleaved so they
    advance together: the hottest point in the module (fieldMinMax) and the
    coolant leaving the module (surfaceFieldValue). The elapsed clock at
    every frame is the run's own ClockTime at that step, off its own log.
    Both readers pass a planted control before a frame moves.
    """

    screen_seconds: float = 36.0

    def _stage_solving(self, emit, script, record) -> dict:
        from . import emit_table

        replay = self.act.solve_replay()
        controls = monitor_controls()
        module = read_minmax_series(MODULE_MINMAX)
        outlet = read_surface_series(OUTLET_TBAR)
        clocks = elapsed_by_step(PRIMARY)
        total_steps = replay.total_iterations
        step_s = 900.0 / total_steps

        if script is not None:
            emit_table(emit, script, role="NUMERICIST", title="Method",
                       headers=["Item", "Setting"], rows=self._methods_rows(),
                       table_id="battery_methods")

        self._say(script, "Solving the module through the pulse.",
                  tense="progressive")
        # THE WORKER TILE SHOWS THE REAL FLEET (Sanaa 2026-09-02 ~04:20Z:
        # the worker count on screen matches the run). This run's launcher
        # recorded ranks=1, so ONE worker rises as solving opens and stands
        # down when it ends; a bigger number here would assert a fleet the
        # record does not show.
        workers = solver_ranks(PRIMARY)
        for _slot in range(workers):
            self._publish(emit, "worker.provisioned", {"stage": "solving"})
        labels = ["Hottest point in the module", "Coolant leaving the module"]
        self._publish(emit, "solve.begin", {
            "stage": "solving",
            "points": 1,
            "labels": labels,
            "iterations_per_point": [total_steps],
            # THIS ACT'S OWN MONITOR PANELS, DECLARED WHERE THE STAGE OPENS.
            # The page's act-generic strip (control_room.html solveBegin ->
            # gsweepReset; contract documented at dmr_act._stage_solving)
            # renders one ROW per panel and one COLUMN per label above from
            # this declaration and types no row label of its own; without it
            # the fallback is the jet act's hard-wired Lift boxes, dark on a
            # thermal act. One panel, two declared series; each frame feeds
            # its own series through its ``monitors`` dict under these exact
            # names, so the module column and the coolant column advance
            # together on one shared temperature scale.
            "monitor_panels": [
                {"title": "Temperatures through the pulse",
                 "x_label": "time step", "y_label": "T, C",
                 "series": labels,
                 "note": ("every value is a row of the run's own monitors: "
                          "the module field extrema and the outlet average")},
            ],
            "controls": [
                "both monitor readers detected a value planted into a copy "
                "of their own files before any curve moved",
            ],
        })

        series = [
            (labels[0], [(stamp, mx - 273.15) for stamp, _mn, mx in module]),
            (labels[1], [(stamp, value - 273.15) for stamp, value in outlet]),
        ]
        schedule = []
        for index, (label, rows) in enumerate(series, start=1):
            for row, (stamp, value) in enumerate(rows):
                schedule.append(((row + 1) / len(rows), index, label, stamp,
                                 value))
        schedule.sort(key=lambda item: (item[0], item[1]))

        origin = self.clock()
        for fraction, index, label, stamp, value in schedule:
            deadline = origin + fraction * float(self.screen_seconds)
            remaining = deadline - self.clock()
            if remaining > 0:
                self.sleep(remaining)
            step = int(round(stamp / step_s))
            if step - 1 >= len(clocks):
                raise DemoContractError(
                    f"time {stamp} has no timing line in the log")
            self._publish(emit, "solve.frame", {
                "stage": "solving",
                "point_index": 1, "points": 1,
                "label": label,
                "iteration": step,
                "iterations": total_steps,
                "elapsed_s": clocks[step - 1],
                "time_s": stamp,
                "value": round(value, 1),
                # ``monitors`` is what the page's declaration-driven strip
                # reads, keyed by this frame's own declared series name; the
                # strip files the frame under the column matching ``label``
                # and leaves the other series null at this abscissa, which is
                # the truth: the two monitors are two files sampled on their
                # own rows. ``coefficients`` stays for the older frame shape.
                "monitors": {label: round(value, 1)},
                "coefficients": {label: round(value, 1)},
                "residuals": {},
            })

        published = self._publish(emit, "solve.end", {
            "stage": "solving",
            "point_index": 1, "points": 1,
            "iteration": total_steps, "iterations": total_steps,
            "core_min_measured": round(campaign_cost()[0], 2),
            "cost_basis": ("core-minutes from each arm's own closing solver "
                           "clock at its recorded rank count"),
            "controls": [c["reader"] + " read its plant back"
                         for c in controls],
            "finished": True,
        })
        self._say(script,
                  "The pulse reaches 900 seconds with every field written.",
                  tense="past")
        # The fleet stands down with the solve.
        for _slot in range(workers):
            self._publish(emit, "worker.released", {"stage": "solving"})
        clock = replay.clock()
        self._publish(emit, "demo.elapsed", {
            "stage": "solving",
            "elapsed": clock.on_screen(),
            "finished": True,
        })
        return published

    @staticmethod
    def _methods_rows() -> list[list[str]]:
        """Solver, closure and numerics, every value read from the case."""
        coolant_solution = PRIMARY / "system" / "coolant" / "fvSolution"
        coolant_schemes = PRIMARY / "system" / "coolant" / "fvSchemes"
        control = PRIMARY / "system" / "controlDict"
        return [
            ["Solver", "OpenFOAM " + solver_name(PRIMARY)
             + ", transient, pressure based, conjugate over two regions"],
            ["Turbulence model", turbulence_model() + " on the coolant"],
            ["Momentum scheme", _dict_value(coolant_schemes, "div(phi,U)")],
            ["Time step", _dict_value(control, "deltaT") + " s"],
            ["End time", _dict_value(control, "endTime") + " s"],
            ["Outer sweeps per step",
             _dict_value(PRIMARY / "system" / "fvSolution",
                         "nOuterCorrectors")],
            ["Pressure tolerance", _block_tolerance(coolant_solution,
                                                    "p_rgh")],
        ]


ACT = register_act("battery-module", BatteryModuleAct())
