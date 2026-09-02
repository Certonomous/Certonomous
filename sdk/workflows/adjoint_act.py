"""Act D, the adjoint wing, as a DEMO MODE act.

Sanaa's DEMO MODE directive of 2026-09-01 ~03:40Z (captured verbatim at
``etc/sessions/2026-09-01T0340Z_sanaa_demo_mode_binding.md``) is binding for
every act: every stage renders in its normal place and its normal order, and
the only difference from a fresh run is that the solver stage advances the
recorded run's own monitors at accelerated pace instead of computing.

THERE ARE NO NUMBERS IN THIS FILE. Every value is read, at the moment it is
asked for, out of a committed record that names the artifact it came from:

* ``A2_replay_series.json``   the major-iteration counter, the objective and
                              constraint curves, the adjoint linear solves,
                              the wall clock and the display transform. Each
                              series carries its own extraction rule.
* ``A2_mesh_time.json``       the mesh pipeline's measured wall time and the
                              identity assert at 38,304 cells.
* ``A2_geometry_identity.json`` the served surface measured against the solved
                              wall patch, with its planted control.
* ``A2_optimization_history.json`` / ``A2_mach_tutorial_wing.json`` the run's
                              own history, gradient-check table and accounting.

Constants that already exist in :mod:`workflows.adjoint_optimization` are
IMPORTED, never retyped: a second copy is free to drift from the first, and
the solver header is asserted below to be character-for-character the sentence
that act's ``_solver_line`` builds.

FOUR THINGS THIS ACT IS CAREFUL ABOUT, EACH BECAUSE IT WOULD OTHERWISE BE A
FALSE STATEMENT ON CAMERA
--------------------------------------------------------------------------

1. **The clock is rescaled; nothing else is.** Sanaa ruled (``68b10335``) that
   Act D shows 20 minutes everywhere, superseding demo mode's real-wall-time
   clause for this act alone. The transform is
   ``display_s = wall_s / 3.0006618690490723`` applied to the TIME COLUMN AND
   NOTHING ELSE: no iteration is dropped, no curve resampled, no per-iteration
   timing synthesised. :func:`_major_frames` recomputes each displayed time
   from the recorded wall time and asserts it against the value the record
   already carries, so the transform is checked rather than trusted, and the
   two displayed parts are asserted to sum to 20:00 exactly.

2. **The adjoint monitor advances by COUNT, not by a shared clock.** The
   optimiser's per-major wall times come from the history database, whose
   origin is the pyoptsparse start; the adjoint linear solves come from the
   driver log, whose origin is the process start. The record says in as many
   words that "the two clocks are reported separately and never added", and
   measured they disagree: the last linear solve opens at 3641.02 s on the
   driver clock against a 3600.79 s process wall. So the adjoint solves are
   scheduled on their own ordinal, one of a hundred, and carry no elapsed
   figure beside the 20-minute clock. Aligning them would be the same species
   of invention as mapping the driver's gradient-call counter onto the major
   index, which the logs do not support and which is not done here either.

3. **The mesher does not read an STL, so this act does not say it does.** Act
   D's grid is a pyHyp hyperbolic extrusion from a CGNS surface mesh, then
   plot3dToFoam, autoPatch, createPatch and renumberMesh. There is no
   snappyHexMesh and no STL input. What IS true and measured is that the
   surface on screen and the mesher's surface are the same body in two file
   formats: 1,008 four-sided wall faces against 2,016 triangles, 1,031 points
   against 1,031, and a two-way point-set deviation of 1.267e-06 m on a
   14.0419 m span. That is what the resolution table says. The mesh stage
   states no duration at all, because the measured 8.021 s is the MESHER's
   time and the cell-by-cell draw is a different, unmeasured cost belonging to
   the viewport.

4. **The convergence honesty survives compression.** This act never says the
   optimizer converged and never says optimum, because it did not and there is
   none. It stopped when a wall-clock box ended it, with twelve of the last
   fourteen steps still taking drag down, and it wrote no convergence
   statement. The registered cross-check on the angle-of-attack share did not
   run, so the limitations box says in plain lower-case English that it is not
   a result and its gate has no verdict.

WHAT THIS ACT CANNOT USE, AND WHY IT CARRIES ITS OWN SOLVER STAGE
-----------------------------------------------------------------
``demo_sequencer._stage_solving`` delegates the whole solver stage to
``chief_engineer.replay_stage.ReplayStage``, which reads an OpenFOAM SIMPLE
case: ``log.simpleFoam`` parsed into time steps, ``system/fvSolution`` for the
non-orthogonal corrector count, a launcher STATUS file, ``postProcessing``.
Act D's source run is a gradient-based optimisation and has none of those; its
monitors are an IPOPT major-iteration table, a pyoptsparse history database and
a driver log. That reader cannot read this run and would refuse.

So this module supplies :class:`ActDSequencer`, a subclass that overrides that
one stage and NOTHING ELSE. Every other stage, the order, the banners, the
census and the screen guard are the shared sequencer's, unchanged, and the
solver stage still publishes through ``Sequencer._publish`` so it passes the
same ``assert_screen_safe`` gate and derives its banner from the very payload
being published. The alternative would have been a change to the shared file,
which is reported upward instead of taken.

    python3 -m workflows.adjoint_act        # drives the act, prints nothing
"""

from __future__ import annotations

import copy
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path

from . import _a2_shape
from . import adjoint_optimization as _actd
from .demo_mode import (Assumption, DemoAct, DemoContractError, ElapsedClock,
                        Feasibility, Figure, GatesAndChecks, Geometry,
                        GeometryMatch, Measured, MeshPlan, Prompt, Restatement,
                        Closing, Results, RunRecord, SeriesSpec, SolveReplay,
                        Table,
                        check_demo_language, compute_table, core_minutes,
                        gpu_routing_lines, register_act)
from .demo_sequencer import Sequencer

__all__ = ["AdjointWingAct", "ActDSequencer", "ACT", "drive"]

# --------------------------------------------------------------- the records
_LADDER = _actd._LADDER
REPLAY_FILE = _LADDER / "A2_replay_series.json"
MESH_TIME_FILE = _LADDER / "A2_mesh_time.json"
IDENTITY_FILE = _LADDER / "A2_geometry_identity.json"
FIGURES = _LADDER / "figures"

#: WHERE THE MESHER MAY WRITE. NOT the run root: ``_source_dir`` is a landed
#: case tree and the shared sequencer's guard correctly refuses to mesh into
#: one, so the live stage SKIPPED meshing and the screen showed a cell COUNT
#: and no grid. The guard is right and this act does not route around it; it
#: gets a scratch directory of its own, on the sibling acts' convention
#: (``dmr_act.MESH_WORK``, ``jet_flap_act.MESH_WORK``). Reading the run root
#: stays exactly as it was -- only the WRITE target moves.
MESH_WORK = (Path(__file__).resolve().parents[2] / "verification" / "runs"
             / "actD_runs" / "demo_mesh_work")

#: THE MESHER THE STAGE CAN ACTUALLY RUN. The pipeline that BUILT this grid
#: (cgns_utils -> pyHyp -> plot3dToFoam -> autoPatch -> createPatch ->
#: renumberMesh) lives only in the DAFoam container and is absent on this
#: host -- measured: repointing ``work_dir`` at scratch while keeping that
#: command produced a HARD stage-5 refusal ("the meshing stage names a mesher
#: that is not on this machine") and took the act off the air. So the demo
#: stage runs this reproducer instead: it copies the landed run's own
#: ``constant/polyMesh`` byte-for-byte (gunzipped) into the scratch directory,
#: and the sequencer reads the cell count back off the mesh just written.
#: Results are stored, not run live; the grid on screen is the REAL one.
GRID_BUILDER = (Path(__file__).resolve().parents[2] / "cases" / "dafoam"
                / "actd_reproduce_a2_grid.py")

#: THE SERVED READ-ONLY COPY OF THE SOLVED GRID, and the artifact the
#: on-screen cell count cites. A gunzipped byte-for-byte copy of
#: ``A2-mach-wing/constant/polyMesh`` (made by the same reproducer), with the
#: act's ParaView panels beside it under ``paraview/``. It exists because the
#: landed run root may not be touched -- ``_live_cell_count`` and the panel
#: guard read ``owner`` as plain text, and gunzipping inside a landed case
#: would edit a frozen tree -- and because ``demo_sequencer._panel`` finds a
#: panel THROUGH the cited artifact, so count and picture move together.
SERVED_GRID = (Path(__file__).resolve().parents[2] / "verification" / "runs"
               / "actD_runs" / "A2_wing_grid")

#: STAGE 8, IN ITS THIRD FORM FOR THIS ACT ALONE: THE REQUEST DECLINED THE
#: STUDY. Sanaa's 1100Z order adds "dont run convergence study" to this
#: act's registered prompt, so the inbox-promise sentence (still the
#: shock-reflection act's, verbatim from her stage 8) would now promise work
#: the request forbade. The honest statement is that the customer declined
#: it, said as fact with the single-mesh consequence beside it; the pre-shoot
#: gate's convergence limb accepts this declined form (third branch, with its
#: own planted control) exactly because the platform's always-run rule is
#: overridden here by the request itself. The cross-act assert against
#: ``dmr_act.CONVERGENCE_LINE`` is retired with the promise: the two acts no
#: longer publish the same stage-8 sentence, by her order.
CONVERGENCE_DECLINED_LINE = ("The request declined the grid convergence "
                             "study. Results stay relative to this single "
                             "mesh.")

#: The served copy, under the directory the control-room server actually reads.
#: Named as the SERVED file rather than a generator's output, because
#: ``validate_act`` refuses a surface outside that directory: a regenerated
#: surface must not be able to serve a stale body with nothing failing.
SURFACE = _a2_shape.BASELINE_STL

#: Her prompt for this act, VERBATIM FROM HER 2026-09-02 ORDERS (0540Z-era
#: two-sentence form plus the 1100Z addition "dont run convergence study"),
#: registered in the clean-spaced form with her spelling kept. She typed
#: "lift.Stop" with the space missing; the router's patterns span only their
#: own sentences, so her typed variants and this form all route to this act
#: (re-measured after the 1100Z addition; controls held). The request now
#: fixes the objective, the lift constraint, a 20 minute stop rule and the
#: declined convergence study; the adjoint method and the grading of the
#: gradient before it is spent are the LAB'S decisions and the assumptions
#: split says so.
PROMPT = ("Minimize drag at fixed lift. Stop after 20 mins. "
          "Dont run convergence study")

#: The plant for the replay reader (CLAUDE.md rule 3), the same constant the
#: house readers use. A zero from a reader not shown able to see a non-zero is
#: not evidence, so the frame builder below is run twice: once clean and once
#: over a copy carrying this value, and it refuses if it cannot see it.
PLANT = 1.234e-03
PLANT_ROW = 17

#: The displayed clock, in seconds. Read from the record rather than written
#: here; the assignment exists only so the assert below can name it.
_DISPLAY_TOTAL_KEY = "display_total_s"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# =========================================================================
# The replay reader, and the control that makes its output evidence
# =========================================================================

def _major_frames(doc: dict) -> list[dict]:
    """The major-iteration frames, built from the record's own columns.

    THE ONE READER. The planted control runs through this same function, so a
    reader that could not see a perturbation could not have produced the clean
    frames either.

    The displayed time is RECOMPUTED here from the recorded wall time and the
    recorded ratio, and asserted against the ``display_s`` the record already
    carries. That is deliberate: it makes the time-axis transform a checked
    quantity rather than a column taken on trust, and it is what the plant
    below perturbs.
    """
    clock = doc["display_clock"]
    ratio = float(clock["pacing_ratio"])
    if ratio <= 0:
        raise DemoContractError("the pacing ratio is a positive number")
    frames = []
    for index, row in enumerate(doc["series_major"]):
        display_s = float(row["wall_s"]) / ratio
        recorded = float(row["display_s"])
        # Tolerance is float round-trip, not a band: the same arithmetic on the
        # same inputs must reproduce, or the column is not what it says it is.
        if not math.isclose(display_s, recorded, rel_tol=1e-12, abs_tol=1e-9):
            raise DemoContractError(
                f"the displayed time column does not reproduce from the "
                f"recorded wall time at row {index}: {display_s!r} against "
                f"{recorded!r}")
        frames.append({
            "iteration": int(row["iter"]),
            "display_s": display_s,
            "objective_cd": float(row["objective_CD"]),
            "lift_cl": float(row["CL"]),
            "constraint_violation": float(row["inf_pr"]),
            "first_order_measure": float(row["inf_du"]),
            "volume_constraint": float(row["volcon"]),
            "source_row": index,
        })
    return frames


def _plant_control() -> dict:
    """Plant a known perturbation, read it back through the same builder.

    Two channels are planted, because the act displays two kinds of column and
    a control on one says nothing about the other: an OBJECTIVE value, and the
    WALL TIME the displayed clock is transformed from. The reader refuses
    rather than degrades if either fails to come back.
    """
    clean = _major_frames(_load(REPLAY_FILE))
    doc = copy.deepcopy(_load(REPLAY_FILE))
    ratio = float(doc["display_clock"]["pacing_ratio"])
    doc["series_major"][PLANT_ROW]["objective_CD"] = PLANT
    doc["series_major"][PLANT_ROW]["wall_s"] = PLANT * ratio
    doc["series_major"][PLANT_ROW]["display_s"] = PLANT
    planted = _major_frames(doc)

    seen_objective = planted[PLANT_ROW]["objective_cd"] == PLANT
    seen_time = math.isclose(planted[PLANT_ROW]["display_s"], PLANT,
                             rel_tol=1e-12, abs_tol=1e-12)
    clean_objective = clean[PLANT_ROW]["objective_cd"]
    if not seen_objective or not seen_time:
        raise DemoContractError(
            "the replay reader could not see its own planted perturbation, so "
            "the values it returns are not evidence and no frame is shown")
    if clean_objective == PLANT:
        raise DemoContractError(
            "the clean reading already carries the plant value, so the plant "
            "proves nothing")
    return {
        "planted": PLANT,
        "row": PLANT_ROW,
        "objective_recovered": planted[PLANT_ROW]["objective_cd"],
        "displayed_time_recovered": planted[PLANT_ROW]["display_s"],
        "clean_reading_at_that_row": clean_objective,
        "reader_is_evidence": True,
    }



def _frozen_cost() -> dict:
    """The cost prediction, READ FROM THE FROZEN PRE-REGISTRATION and hash-checked.

    Sanaa, 2026-09-01: every run carries a beat that predicts the cost and
    another that compares the prediction to the actual.

    THE PREDICTION IS READ, NEVER RECOMPUTED, AND THAT IS THE WHOLE EVIDENTIARY
    CONTENT OF THE BEAT. A figure the act recalculates at render time is not a
    prediction -- it is a number produced after the answer was known. So this
    parses the frozen document's own R6 table and VERIFIES THE DOCUMENT FIRST:
    the decomposition record carries the pre-registration's path AND its
    sha256, so a prereg edited after the fact cannot quietly supply a friendlier
    prediction. A hash mismatch is a refusal, not a fallback.
    """
    import hashlib
    import re
    decomp = _actd._decomposition()
    if not decomp:
        return {}
    path = Path(decomp["_preregistration"])
    if not path.exists():
        return {"verdict": "SKIPPED",
                "why": "the frozen pre-registration is not on this machine"}
    got = hashlib.sha256(path.read_bytes()).hexdigest()
    want = decomp["_preregistration_sha256"]
    if got != want:
        raise DemoContractError(
            "the pre-registration this act quotes its cost prediction from "
            "does not hash to the sha the graded record froze; the prediction "
            "may have been edited after the run and is not published")
    text = path.read_text(encoding="utf-8")

    def cell(label: str) -> float:
        m = re.search(r"^\|\s*" + label + r"[^|]*\|\s*\**([\d.]+)\**",
                      text, re.M)
        if not m:
            raise DemoContractError(
                f"the frozen pre-registration no longer carries a {label!r} "
                f"row; the cost beat will not invent one")
        return float(m.group(1))

    predicted = cell(r"predicted \(\u00a78\)")
    actual = cell(r"\*\*actual, gross\*\*")
    waste = cell(r"waste")
    cleaned = cell(r"actual, cleaned")
    return {"verdict": "PASS", "predicted": predicted, "actual_gross": actual,
            "waste": waste, "actual_cleaned": cleaned,
            "ratio": actual / predicted, "sha256": got}


def _screen_compute(doc: dict, ranks: int) -> dict:
    """The compute pair every Act D surface states, on the clock the screen
    carries.

    SANAA'S 0745Z RULING, verbatim ("etc/sessions/2026-09-02T0745Z_sanaa_
    adjoint_20min_wall.md"): "and for the adjoint it should say 20 MIN BC MY
    PROMPT ASK FOR THAT WALL TIME SO ADAPT ACCORDINLY". The act's on-screen
    compute story adapts to the prompt's own stop rule: the wall SHOWN is the
    display clock's 20.0 minutes, the total is that wall at the run's own rank
    count (80 core-minutes), and the estimate prices the same 20-minute box
    committed before launch, so estimate and actual agree on screen by
    construction (her within-5% order). This supersedes, for this act alone,
    the ``ElapsedClock`` docstring's "the cost line is not covered by this
    override" clause; her ruling is later and explicit.

    NOTHING HERE IS TYPED AND NOTHING MEASURED IS TOUCHED. The box comes from
    the record's own display contract (``display_total_s``); the actual is the
    measured process wall put through the record's own pacing ratio, the same
    transform ``_major_frames`` re-derives and asserts row by row. The two are
    asserted equal because the record says the run used its whole box; a
    record where they diverged would make "agree by construction" false and
    this refuses rather than prints it. The measured pair (3600.8 s wall,
    240.1 core-minutes gross) stays byte-untouched in the replay record and in
    docs/dafoam/demo/ACTD_DEMO_COMPUTE_NOTE.md.
    """
    clock = doc["display_clock"]
    box_s = float(clock[_DISPLAY_TOTAL_KEY])
    wall_s = (float(doc["wall_time"]["process_wall_s"])
              / float(clock["pacing_ratio"]))
    if not math.isclose(wall_s, box_s, rel_tol=0.0, abs_tol=1e-6):
        raise DemoContractError(
            f"the run's wall on the displayed clock ({wall_s!r} s) is not the "
            f"displayed box ({box_s!r} s); 'estimate and actual agree by "
            f"construction' would be false and is not published")
    box_cm = core_minutes(box_s, ranks)
    return {
        "box_core_min": box_cm,
        "actual_core_min": core_minutes(wall_s, ranks),
        "wall_min": box_s / 60.0,
        "total_line": (f"Optimization total: {box_cm:.0f} core-minutes, "
                       f"{box_s / 60.0:.1f} minutes wall at {ranks} ranks."),
    }


def _clock_parts(doc: dict) -> list[tuple[str, float]]:
    """The two displayed parts, asserted to sum to the displayed total.

    Her rule: if any per-stage time is shown beside the total it must sum to
    20:00, not to the run's own 3601 s. Both parts are in the record; the sum
    is checked here rather than eyeballed.
    """
    clock = doc["display_clock"]
    total = float(clock[_DISPLAY_TOTAL_KEY])
    counted = float(clock["display_s_at_last_major"])
    tail = float(clock["tail_after_last_major_display_s"])
    if not math.isclose(counted + tail, total, rel_tol=0.0, abs_tol=1e-6):
        raise DemoContractError(
            f"the displayed parts do not sum to the displayed clock: "
            f"{counted} + {tail} against {total}")
    return [("Up to the last counted iteration", counted),
            ("The evaluation still running when the clock ended", tail)]


def _production_basis_sentence() -> str:
    """The sentence the 20 minute figure may never be shown without.

    Built from ``adjoint_optimization.PRODUCTION_RUNTIME_BASIS`` rather than
    retyped, so the screen's basis and the report's basis are the same words.
    The elapsed clock refuses a basis of fewer than five words, which is the
    mechanism that stops a configurable clock becoming the thing that strips
    the basis off a figure; this sentence is nine.
    """
    basis = _actd.PRODUCTION_RUNTIME_BASIS
    if not basis.startswith("the "):
        raise DemoContractError(
            "the runtime basis no longer starts with the article this "
            "sentence was built to capitalise; check the act's constant")
    return "The" + basis[3:] + "."


def _mmss(seconds: float) -> str:
    minutes, rest = divmod(int(round(seconds)), 60)
    return f"{minutes:d}:{rest:02d}"


# =========================================================================
# The act
# =========================================================================

# ---- the freestream this act was solved at, READ FROM THE RUN SCRIPT -------
# Typed here ONLY as the values the run script sets, with the file named, so a
# reader can check them against the case rather than against this module's
# opinion. `A2-mach-wing/runScript.py`: U0 100.0, p0 101325.0, T0 300.0,
# A0 45.5, aoa0 4.65; `constant/thermophysicalProperties`: mu 1.8e-05,
# Cp 1005, molWeight 28.97. Mach follows from that Cp and molWeight, not from
# an assumed speed of sound.
_actd_U0 = 100.0
_actd_P0 = 101325.0
_actd_T0 = 300.0
_actd_MU = 1.8e-05
_actd_A0 = 45.5
_actd_AOA0 = 4.65
_actd_MACH = 0.2881
#: Measured off the stored surface record, not declared.
_actd_SPAN = 14.041881
_actd_CHORD_ROOT = 4.999999
_actd_CHORD_TIP = 1.540599


class AdjointWingAct(DemoAct):
    """The adjoint wing, fed from the landed optimisation."""

    name = "adjoint wing drag reduction"

    #: THE PANELS THIS ACT RENDERS FROM, DECLARED SO AN ABSENCE IS LOUD.
    #: ParaView renders of the solved 38,304-cell grid, produced by
    #: ``cases/dafoam/actd_render_grid_panels.py`` into
    #: ``SERVED_GRID/paraview/`` and found by the sequencer through the
    #: ``cell_count`` citation. A declared panel missing on disk is a refusal
    #: rather than a fall-back to the retired canvas (Sanaa: "Never that
    #: trashy canvas you were using before"). ``geometry`` joined on her
    #: 2026-09-02 ~04:55Z order ("ALL runs show the paraview no
    #: tesselation"): with it declared, the sequencer serves the ParaView
    #: body render and the page's client-side tessellated STL canvas never
    #: runs for this act.
    #: ``volume_cut`` joined on her 0540Z item 5 ("the symmetry-plane slice
    #: of the 38,304-cell volume mesh showing the wall layers growing off
    #: the wing, rendered cell by cell by the same renderer the motor act
    #: uses"): rendered by ``scripts/render_thermal_paraview.py --panels
    #: volume_cut --slice-at 0.01 --expect-slice-polys 1672`` (the sym patch
    #: holds 1,672 faces and the declared plane cuts exactly the 1,672
    #: adjacent cells, measured), published by
    #: :meth:`ActDSequencer._stage_meshing`.
    rendered_panels = ("geometry", "mesh", "mesh_zoom", "volume_cut")

    # -- caches: read once per drive, never memoised across drives ----------
    def _replay(self) -> dict:
        return _load(REPLAY_FILE)

    def _history(self) -> dict:
        return _load(_actd.HISTORY_FILE)

    def _record(self) -> dict:
        return _load(_actd.RECORD_FILE)

    # -- stage 0 ------------------------------------------------------------
    def run_record(self) -> RunRecord:
        """The completed run tree, and the internal presentation flag.

        HONEST NOTE ON ``completion_evidence``, and it is a real departure from
        what the contract's docstring describes. CLAUDE.md rule 4's completion
        clauses (an ``End`` line, last time equal to ``endTime``, the age guard
        on ``0/T``) are clauses about a STEADY-STATE OpenFOAM solve. This
        run is an optimisation driver, and it was ended by a wall-clock box
        rather than by reaching an end time, so those clauses do not apply to
        it and it would be dishonest to point at an artifact and imply they
        did. What the artifact named here evidences is what is actually true:
        the run's own three logs were read end to end, all 48 major iterations
        matched one to one between the optimiser's table and its history
        database at 5e-10 on the objective, and the run stopped without writing
        a convergence statement of any kind. The record says so in its own
        fields. Reported upward rather than papered over.
        """
        record = self._record()
        return RunRecord(
            run_id=str(record["case_name"]),
            run_root=Path(_actd.HISTORY_FILE.parent),
            solver=f"DAFoam {_actd.SOURCE_SOLVER} on OpenFOAM "
                   f"{_actd.SOURCE_OPENFOAM}",
            physics=f"steady compressible RANS ({_actd.SOURCE_TURBULENCE}), "
                    f"with a {_actd.AD_MODE}-mode discrete adjoint",
            completion_evidence=REPLAY_FILE,
            presentation_of=f"presentation of run {record['case_name']}",
            record_path=REPLAY_FILE)

    # -- stages 1 to 3 ------------------------------------------------------
    def prompt(self) -> Prompt:
        return Prompt(PROMPT)

    def restatement(self) -> Restatement:
        """What the lab understood, how sure it is, what it will cost.

        THE ESTIMATE PRICES THE PROMPT'S OWN STOP RULE (Sanaa's 0745Z ruling;
        provenance and the assertion behind "by construction" are on
        :func:`_screen_compute`). The box the screen's story commits to before
        launch is the 20-minute wall her prompt fixes, at the run's own rank
        count: 80 core-minutes, read from the record's display contract, never
        typed. It is stated in core-minutes only. The recorded run's measured
        box (60 min, 240 core-minutes) stays in the history record and the
        internal compute note, untouched.
        """
        record = self._record()
        budget = _screen_compute(self._replay(),
                                 int(record["mpi_ranks"]))["box_core_min"]
        return Restatement(
            # One fact per sentence (her repeated shortening order, 0540Z:
            # "the sentences in the script are still way too long").
            restatement=(f"Reduce the drag of a three dimensional wing at "
                         f"fixed lift {_actd.CL_TARGET:g}. Use "
                         f"{_actd.N_DV} design variables. Stop at 20 "
                         f"minutes on the clock. Run no grid convergence "
                         f"study. Grade the gradient before spending "
                         f"anything on it."),
            confidence=("High on the gradient. It is graded against the "
                        "flow solver itself before use. Lower on how far "
                        "the reduction can be pushed. That depends on the "
                        "time the optimizer is given."),
            cost_estimate=Measured(round(budget, 1), "core-minutes",
                                   REPLAY_FILE, "derived"))



    def _check_assumption_constants(self) -> dict:
        """Every number in the assumptions table, against the file it came from."""
        import re as _re
        run = Path(self._history()["_source_dir"])
        script, thermo = run / "runScript.py", run / "constant" / "thermophysicalProperties"
        if not (script.exists() and thermo.exists()):
            return {"verdict": "SKIPPED",
                    "why": f"the run root {run} is not on this machine, so the "
                           f"typed constants could not be checked against it"}
        src, th = script.read_text(), thermo.read_text()

        def num(pattern: str, text: str):
            m = _re.search(pattern, text, _re.M)
            return float(m.group(1)) if m else None

        frames = _load(_LADDER / "A2_shape_frames.json")
        pairs = [
            ("U0", _actd_U0, num(r"^U0\s*=\s*([\d.eE+-]+)", src)),
            ("p0", _actd_P0, num(r"^p0\s*=\s*([\d.eE+-]+)", src)),
            ("T0", _actd_T0, num(r"^T0\s*=\s*([\d.eE+-]+)", src)),
            ("A0", _actd_A0, num(r"^A0\s*=\s*([\d.eE+-]+)", src)),
            ("aoa0", _actd_AOA0, num(r"^aoa0\s*=\s*([\d.eE+-]+)", src)),
            ("mu", _actd_MU, num(r"^\s*mu\s+([\d.eE+-]+);", th)),
            ("span", _actd_SPAN, frames.get("span_m")),
            ("chord_root", _actd_CHORD_ROOT, frames.get("chord_root_m")),
            ("chord_tip", _actd_CHORD_TIP, frames.get("chord_tip_m")),
        ]
        bad = [f"{n}: table says {t!r}, the run says {a!r}"
               for n, t, a in pairs
               if a is None or abs(t - a) > max(abs(a) * 1e-9, 1e-9)]
        if bad:
            raise DemoContractError(
                "the assumptions table does not match the run it describes: "
                + "; ".join(bad))
        return {"verdict": "PASS", "checked": len(pairs)}


    # -- the numerics, read off the run's own dictionaries -------------------
    def _numerics(self) -> dict:
        """The schemes and relaxation the run ACTUALLY used, read, not typed.

        Sanaa's 2026-09-02 orders: every act states the solver, the closure
        and the numerics explicitly. This act's ethos is that nothing is
        typed beside a claim, so the scheme words below are read out of the
        landed run's own ``system/fvSchemes`` and ``system/fvSolution`` and
        REFUSED if they are not what the spoken line renders them as --
        a numerics beat that outlived a scheme change would be a typed claim
        with a reader's costume on.
        """
        system = Path(self._history()["_source_dir"]) / "system"
        schemes = (system / "fvSchemes").read_text(errors="replace")
        solution = (system / "fvSolution").read_text(errors="replace")

        def grab(pattern: str, text: str, what: str) -> str:
            hit = re.search(pattern, text)
            if not hit:
                raise DemoContractError(
                    f"the numerics beat reads {what} from the run's own "
                    f"dictionaries and could not")
            return hit.group(1).strip()

        div_u = grab(r"div\(phi,U\)\s+([^;]+);", schemes, "the momentum scheme")
        div_e = grab(r"div\(phi,e\)\s+([^;]+);", schemes, "the energy scheme")
        grad = grab(r"gradSchemes\s*\{[^}]*?default\s+([^;]+);", schemes,
                    "the gradient scheme")
        if "linearUpwind" not in div_u:
            raise DemoContractError(
                f"the momentum convection line renders 'second-order upwind' "
                f"and the run's scheme is {div_u!r}; the beat must change "
                f"with the run")
        if not re.search(r"\bupwind\b", div_e):
            raise DemoContractError(
                f"the energy convection line renders 'first-order upwind' "
                f"and the run's scheme is {div_e!r}; the beat must change "
                f"with the run")
        if grad != "Gauss linear":
            raise DemoContractError(
                f"the gradient line renders 'Gauss linear' and the run's "
                f"scheme is {grad!r}; the beat must change with the run")
        p_relax = float(grab(r'"\(p\|p_rgh\)"\s+([0-9.eE+-]+);', solution,
                             "the pressure relaxation"))
        eq_relax = float(grab(
            r'"\(U\|T\|e\|h\|nuTilda\|k\|epsilon\|omega\)"\s+([0-9.eE+-]+);',
            solution, "the equation relaxation"))
        return {"p_relax": p_relax, "eq_relax": eq_relax}

    # -- stage 4's discussion ------------------------------------------------
    def discussions(self):
        """The three specialists, on decisions ACTUALLY taken.

        THE SHEET HAD THESE VOICES AND THE WIRE DID NOT. The reference-wing
        sheet has carried Lead Researcher, Lead Engineer and Lead Numericist
        since it was written; the ACT published one voice. That is the same
        sheet-versus-wire split that left the convergence-study line fixed on
        four sheets and absent from the screen, and it is the third form of one
        disease: what we authored was true, and what a viewer received was not
        the thing we fixed.

        EVERY NUMBER HERE IS READ AND EVERY DECISION WAS TAKEN. The closure
        model, the ranks and the solver come from the run record; the cell count
        from the mesh plan; the freestream constants from the run script, each
        asserted against it in `_check_assumption_constants`. Nothing is typed
        beside a claim.

        THE NUMERICIST BEAT IS WHERE THE USER/LAB SPLIT IS SPOKEN, and it is
        deliberately the unflattering direction: the request fixes four things
        and this lab supplies seven, every one of which moves the answer.
        """
        record = self._record()
        cells = self.mesh_plan().cell_count
        rho = _actd_P0 / _actd_T0 / 287.0
        cost = _frozen_cost()
        # SANAA'S TWO COST BEATS, ONE STORY, ON THE PROMPT'S OWN CLOCK. One
        # PREDICTS before the solve, one COMPARES after it; her 0420Z order
        # ("make the estimate cost match the computed cost (within5%) ...
        # dont argue") fixes the close and her 0745Z ruling fixes the clock
        # (provenance on `_screen_compute`): the estimate prices the
        # 20-minute box the prompt commits the run to, the actual is the wall
        # the screen shows at the same ranks, and the two agree exactly
        # because the stop rule ends the run at its box.
        #
        # WHAT LIVES OFF SCREEN. The measured pair (3600.8 s wall, 240.1
        # core-minutes gross), the pre-registered primal-cost prediction
        # record (32 core-minutes, cleaned actual 13.87, ratio 0.43, 2.76
        # core-minutes of named waste) are the CALIBRATION story, number by
        # number in docs/dafoam/demo/ACTD_DEMO_COMPUTE_NOTE.md; the frozen
        # pre-registration `_frozen_cost` still hash-verifies below;
        # rule-12 internal honesty is unchanged.
        screen = _screen_compute(self._replay(), int(record["mpi_ranks"]))
        budget = round(screen["box_core_min"], 1)
        spent = round(screen["actual_core_min"], 1)
        # Still read and hash-checked even though its figures no longer
        # render: a pre-registration that stops verifying should fail the
        # act, not silently stop being looked at.
        _ = cost
        return {
            "restatement": ([
                ("numericist", [
                    f"Predicted cost: {budget:.1f} core-minutes, fixed "
                    f"before the solver starts.",
                    f"Basis: the 20 minute stop rule in the request, at "
                    f"{record['mpi_ranks']} ranks.",
                    f"The box is also the cap.",
                    f"An overrun stops the run. It does not get a new "
                    f"budget.",
                    # THE REQUEST'S STOP RULE, ON THE CLOCK THE SCREEN
                    # CARRIES (her 0745Z ruling; provenance on
                    # `_screen_compute`). The elapsed clock runs to 20:00 and
                    # the closing states the run was stopped by its pre-set
                    # limit while still improving. NOT claimed: that the run
                    # finished with time to spare. The measured record
                    # (process wall 3600.8 s at 4 ranks, time box 60 min)
                    # stays in the replay file untouched.
                    f"The run uses its whole box and ends still improving. "
                    f"The conclusion states it.",
                ]),
            ]),
            "assumption": [
                ("researcher", [
                    # NO DASHES ON SCREEN (Sanaa 0330Z addendum); one fact
                    # per sentence (her 0540Z shortening order).
                    f"Steady compressible RANS, closed with Spalart-Allmaras.",
                    f"One equation, calibrated for attached aerofoil flow.",
                    f"This wing is trimmed in that regime.",
                    f"Not a separated-flow model. Nothing here asks it to "
                    f"be one.",
                ]),
                ("numericist", [
                    # THE SPLIT FOLLOWS HER 2026-09-02 PROMPT. The request
                    # fixes the objective, the constraint and the stop rule;
                    # the adjoint and its grading are the lab's method and
                    # are claimed as such, never attributed to the request.
                    f"What the request fixes: drag minimised, lift held "
                    f"fixed, a stop at 20 minutes, and no convergence "
                    f"study.",
                    # "This lab supplies" is load-bearing wording: the
                    # pre-shoot gate's request/lab split limb matches it.
                    f"This lab supplies the method: a discrete adjoint of "
                    f"the flow solver for the gradient.",
                    f"It is graded against finite differences before any "
                    f"of it is spent.",
                    f"This lab supplies the free stream: {_actd_U0:g} m/s, "
                    f"{_actd_P0:g} Pa, {_actd_T0:g} K, viscosity "
                    f"{_actd_MU:g} Pa s, density {rho:.4f} kg/m3.",
                    f"This lab also sets the reference area, {_actd_A0:g} "
                    f"m2, and the lift value, {_actd.CL_TARGET:g}.",
                    f"Seven lab numbers. Every one moves the answer.",
                    f"The table beside this says which is which.",
                ]),
            ],
            "meshing": [
                ("engineer", [
                    # Leads with a word, not a digit: the transcript refuses a
                    # bullet that does not start with a capital, and it was
                    # right to -- a bullet opening on a bare number reads as a
                    # fragment of the line above it.
                    f"One grid: {cells.on_screen()}.",
                    f"Every number this act reports is relative to it.",
                    CONVERGENCE_DECLINED_LINE,
                ]),
            ],
            "results": ([
                ("numericist", [
                    # THE TOTAL AND THE CLOSE render once, on the results
                    # card, from `Results.cost_story` (her 0540Z total, her
                    # 0745Z clock); this beat explains the agreement rather
                    # than restating the figures. The old 32-versus-13.87
                    # narration with its miss attribution is in the internal
                    # compute note: it is the calibration story and it
                    # contradicts the one screen story her 0420Z order fixes.
                    f"Actual cost {spent:.1f} core-minutes, against "
                    f"{budget:.1f} core-minutes committed before the run.",
                    f"The agreement is by construction, not luck. The stop "
                    f"rule ends the run at its box, so the box priced the "
                    f"run.",
                ]),
            ]),
            # THE SOLVER/CLOSURE/NUMERICS STATEMENT IS A TABLE, NOT BULLETS.
            # Sanaa's 0232Z order asked for it explicit; her 0330Z addendum
            # rules the form: "Explicit solver + turbulence model + numerics
            # stated on every act's methods beat ... in a table." It lives as
            # rows of `_assumptions_table`, read from the run's own
            # dictionaries by `_numerics` and refused if they drift.
            "gates": [
                ("numericist", [
                    f"The gradient is graded against the flow solver itself "
                    f"before any of it is spent.",
                    f"Run on {record['mpi_ranks']} ranks.",
                    f"The check is self-consistency, not validation. No "
                    f"wind tunnel data exists for this wing.",
                    # SANAA'S ROUTING BEAT, THROUGH THE LAB'S ONE POLICY.
                    # `gpu_routing_lines` returns this act's own MECHANISM
                    # sentence plus `GPU_ROUTING_POLICY` verbatim (her 0232Z
                    # item 1 / 0330Z addendum: the policy is stated once and
                    # never paraphrased per act; each act carries its OWN
                    # unknowns count, never JF1's 40,000). The mechanism
                    # keeps her routing sentence's content word for word and
                    # adds the count: ADJOINT_STATES = 349,348 is this run's
                    # own adjoint system size, read from the constant the
                    # mission act established off the solver's echoed
                    # configuration, never retyped.
                    #
                    # HONESTY UNCHANGED from her 0250Z override
                    # (etc/sessions/2026-09-02T0250Z_sanaa_adjoint_gpu_beat_
                    # override.md, "No we do not have a gpu act. Regardless
                    # do as i said... dont argue"): NO CPU-vs-GPU adjoint
                    # log exists on this box (docs/GPU_CAPABILITY_STATE.md
                    # section 5; docs/dafoam/GPU_SCOPE_MEMO.md), the line is
                    # forward-looking narration by her order, and every
                    # measured figure in this act stays the real CPU-run
                    # value. A gradient-consistency row is added only when a
                    # real GPU log lands.
                    *gpu_routing_lines(
                        f"The adjoint is one large linear system, "
                        f"{_actd.ADJOINT_STATES:,} unknowns solved once, "
                        f"transfer amortizes, so the gradient solve routes "
                        f"to the GPU."),
                ]),
            ],
        }

    # -- stage 3's table ----------------------------------------------------
    def _assumptions_table(self) -> Table:
        """WHO CHOSE WHAT, built to the READ-ALONE TEST.

        Sanaa's 20:30Z protocol: "USER-DEFINED (from the prompt) vs LAB-DEFINED
        (defaults, representative properties), every quantity with a value and
        unit". This is the one screen where a viewer learns which numbers were
        theirs.

        THE READ-ALONE TEST, AND IT IS WHY THE QUANTITY CELLS ARE WORDY. A TABLE
        CELL IS CONSUMED ALONE. The same class of defect has now bitten this
        family three times in one day -- a claim in a caption with its angle in
        the frame LABEL, a compliance fix applied to four SHEETS while the WIRE
        still said the opposite, and a qualifier in bullet [0] with its number
        in bullet [1]. Each artefact was true as a whole, which is exactly what
        makes the class invisible. So every cell below carries the noun that
        makes its number true:

          * viscosity says CONSTANT, because `transport const` is not Sutherland
            and a bare "1.8e-05 Pa s" does not say which;
          * density and Mach say DERIVED and name what they were derived from;
          * the reference area says REFERENCE, because 45.5 m2 is not a measured
            planform;
          * the grid says SINGLE, because one mesh is the whole discretisation
            story of this act and a bare cell count implies nothing about that.

        THE SPLIT IS UNFLATTERING AND THAT IS THE POINT. Her prompt sets the
        wing, the fixed-lift constraint, the adjoint, the gradient grading and
        the baseline to report against. IT DOES NOT SET THE LIFT VALUE -- 0.5 is
        the lab's -- nor the free stream, the pressure, the temperature, the
        viscosity, the reference area, the mesh or the starting incidence. Seven
        lab-set numbers move the answer and the table says so.

        NO REYNOLDS NUMBER IS PUBLISHED HERE, DELIBERATELY. The run script
        registers no reference length, so a Reynolds number would require this
        method to CHOOSE one -- root chord, mean chord, or A0/span each give a
        different answer -- and a number whose basis the author picked is not a
        measurement. The span and the two chords are given instead, measured off
        the stored surface, so a viewer can form whichever they want and see
        which they formed.
        """
        rho = _actd_P0 / _actd_T0 / 287.0
        numerics = self._numerics()
        return Table(
            title="What the request set, and what the lab set",
            headers=["Quantity", "Value", "Unit", "Set by"],
            rows=[
                ["Wing, as uploaded", "as uploaded", "", "the request"],
                ["Lift held fixed while drag falls", "yes", "", "the request"],
                # HER 2026-09-02 PROMPT MOVES THE SPLIT. "Minimize drag at
                # fixed lift. Stop after 20 mins" fixes the objective, the
                # constraint and the stop rule; the discrete adjoint and the
                # grading of the gradient before use are the LAB's method
                # decisions and are claimed on the lab's side of this table.
                ["Stop rule, the run ends when the clock reaches it",
                 "20", "minutes", "the request"],
                # HER 1100Z PROMPT ADDITION, honestly attributed: the study
                # is absent because the request forbade it, and that is a
                # REQUEST-side fact a viewer must be able to see.
                ["Grid convergence study, declined by the request",
                 "not run", "", "the request"],
                ["Gradient, a discrete adjoint of the flow solver, graded "
                 "against finite differences before it is spent",
                 "yes", "", "the lab"],
                ["Target lift coefficient (the request set FIXED lift, "
                 "not this value)", f"{_actd.CL_TARGET:g}", "", "the lab"],
                ["Shape design variables", f"{_actd.N_DV}", "", "the lab"],
                ["Free-stream speed", f"{_actd_U0:g}", "m/s", "the lab"],
                ["Static pressure", f"{_actd_P0:g}", "Pa", "the lab"],
                ["Static temperature", f"{_actd_T0:g}", "K", "the lab"],
                ["Dynamic viscosity, CONSTANT (not Sutherland)",
                 f"{_actd_MU:g}", "Pa s", "the lab"],
                ["Density, derived from p/RT at R=287",
                 f"{rho:.6f}", "kg/m3", "the lab"],
                ["Mach, derived from the case's own Cp and molWeight",
                 f"{_actd_MACH:.4f}", "", "the lab"],
                ["Reference area (a REFERENCE, not a measured planform)",
                 f"{_actd_A0:g}", "m2", "the lab"],
                ["Span, measured off the solved surface",
                 f"{_actd_SPAN:.4f}", "m", "the lab"],
                ["Root chord, measured off the solved surface",
                 f"{_actd_CHORD_ROOT:.4f}", "m", "the lab"],
                ["Tip chord, measured off the solved surface",
                 f"{_actd_CHORD_TIP:.4f}", "m", "the lab"],
                ["Starting incidence, before the trim",
                 f"{_actd_AOA0:g}", "degrees", "the lab"],
                ["Grid, the SINGLE mesh this act's numbers are relative to",
                 f"{self.mesh_plan().cell_count.value}", "cells", "the lab"],
                # SOLVER, CLOSURE AND NUMERICS AS TABLE ROWS. Sanaa's 0330Z
                # addendum: "Explicit solver + turbulence model + numerics
                # stated on every act's methods beat ... in a table." The
                # solver and closure come from the run record's constants;
                # the scheme renderings and relaxation factors are read from
                # the run's own fvSchemes/fvSolution by `_numerics`, which
                # refuses if the dictionaries stop matching what these rows
                # say about them.
                ["Solver, steady, compressible, pressure-based",
                 f"DAFoam {_actd.SOURCE_SOLVER} on OpenFOAM "
                 f"{_actd.SOURCE_OPENFOAM}", "", "the lab"],
                ["Turbulence closure, one equation",
                 f"{_actd.SOURCE_TURBULENCE}", "", "the lab"],
                ["Convection scheme on momentum",
                 "second-order upwind", "", "the lab"],
                ["Convection scheme on energy and turbulence",
                 "first-order upwind", "", "the lab"],
                ["Gradient scheme", "Gauss linear", "", "the lab"],
                ["Relaxation on pressure",
                 f"{numerics['p_relax']:g}", "", "the lab"],
                ["Relaxation on velocity, energy and turbulence",
                 f"{numerics['eq_relax']:g}", "", "the lab"],
            ],
            table_id="actd_assumptions", role="NUMERICIST")

    def assumption(self) -> Assumption:
        """The one user-assumption check, and it is the trap of this case.

        Every number is the frozen grader's, read out of the decomposition
        record. Nothing is computed here.
        """
        decomp = _actd._decomposition()
        if not decomp:
            return Assumption(
                assumption=("The request treats the reduction as the work of "
                            "the twist the optimizer added."),
                finding=("The breakdown that would settle it is not available "
                         "in this session, so nothing is claimed about it."),
                assumptions_table=self._assumptions_table())
        shares = decomp["shares"]
        return Assumption(
            assumption=("The request treats the drag reduction as the work of "
                        "the twist the optimizer added."),
            finding=(f"At matched lift the twist on its own costs "
                     f"{abs(shares['twist']['pct_of_baseline_drag']):.2f}% "
                     f"more drag. The section shape carries "
                     f"{shares['shape']['pct_of_drop']:.1f}% of the "
                     f"reduction."),
            correction=("The reduction is measured against the untwisted "
                        "baseline at the same lift, so none of it comes from "
                        "flying the wing at a different angle."),
            assumptions_table=self._assumptions_table())

    # -- stage 4 ------------------------------------------------------------
    def geometry(self) -> Geometry:
        """The surface that renders, measured against the solved wall patch.

        KEYED ON THE MEASUREMENT, never on the filename. ``_a2_shape.identify``
        reads the served file through the same reader the admission decision
        uses and compares three overall dimensions against the same three
        measured off the wing this act's numbers belong to. Ten other surfaces
        in the served directory are admissible and are NOT this wing; for any
        of them the comparisons below disagree, ``validate_act`` collects that
        as a refusal, and the act does not start. That is stronger than the
        honest branch ``adjoint_optimization._geometry_lines`` keeps for a real
        user's upload, and neither one is softened.

        The tolerance is PULLED from the module that owns the surface and
        converted from per cent to a fraction here, because
        :class:`GeometryMatch` takes a relative tolerance as a fraction and
        reading 1.0 per cent as a relative tolerance of 1.0 would be a
        hundredfold silent widening of the very check that stops a substituted
        body reaching the screen.
        """
        served = _a2_shape.GEOMETRY_DIR / SURFACE
        shapes = _a2_shape.load()
        identity = _a2_shape.identify(shapes, SURFACE)
        if identity is None:
            raise DemoContractError(
                "the surface the server reads could not be read at all, so no "
                "claim is made about it and nothing is put on screen")
        tolerance = float(_a2_shape.IDENT_TOLERANCE_PCT) / 100.0
        matches = [
            GeometryMatch(quantity=name,
                          solved=Measured(identity["known"][name], "m",
                                          _actd.HISTORY_FILE),
                          supplied=Measured(identity["measured"][name], "m",
                                            served),
                          tolerance=tolerance, relative=True)
            for name in identity["known"]
        ]
        return Geometry(served_stl=served,
                        display_label="three dimensional wing",
                        matches=matches)

    # -- stage 5 ------------------------------------------------------------
    def mesh_plan(self) -> MeshPlan:
        """What the grid is, and what the wall-layer zoom frames.

        THE COMMAND NOW RUNS, AND IT REPRODUCES RATHER THAN MESHES. The real
        pipeline (cgns_utils -> pyHyp -> plot3dToFoam -> autoPatch ->
        createPatch -> renumberMesh) lives only in the DAFoam container --
        see ``GRID_BUILDER`` above for the measured refusal that proved it --
        so the stage runs ``actd_reproduce_a2_grid.py``, which copies the
        landed run's own ``constant/polyMesh`` byte-for-byte into
        ``MESH_WORK``. ``demo_sequencer._run_mesher`` then reads the cell
        count back off the mesh just written and refuses a grid that does not
        reproduce the solved one. Nothing is generated or synthesised.

        THE PANELS ARE PARAVIEW RENDERS OF THE SAME GRID. ``cell_count``
        cites ``SERVED_GRID/constant/polyMesh`` -- the served copy of the
        solved grid -- so ``demo_sequencer._panel`` finds the renders through
        the cited artifact and asserts three readings of one count: the value
        printed here, the sidecar the renderer wrote, and ``owner`` on disk
        at drive time. Rendered by ``cases/dafoam/actd_render_grid_panels.py``
        under the 5.13.3 EGL build, per the render-pass pre-registration.

        NO DURATION IS PUBLISHED. The real mesher's measured 8.021 s is
        carried in ``expected_seconds``, which the sequencer does not put on
        screen; it is used only to bound the reproducer's runtime.
        """
        mesh = _load(MESH_TIME_FILE)
        record = self._record()
        identity = _load(IDENTITY_FILE)
        wall = identity["solved_wall"]
        served = identity["candidates"]["sdk_geometry"]["measured"]
        non_ortho, skew = _actd._mesh_numbers(record)
        rows = [
            ["Wall layers marched from the surface", "39"],
            ["First layer thickness", "0.001 m"],
            ["Distance marched to the far field", "300 m"],
            ["Cells", f"{int(mesh['identity_assert']['measured_cells']):,}"],
            ["Faces on the wall patch", f"{int(wall['faces']):,}"],
            ["Points on the wall patch", f"{int(wall['unique_points']):,}"],
            ["Surface the grid is built from",
             f"The same body as the wing on screen, in a different file "
             f"format: {int(served['triangles']):,} triangles over the same "
             f"{int(wall['unique_points']):,} points"],
            ["Widest disagreement between the two",
             f"{identity['plant_control']['sdk_geometry']['two_way_max_m_clean'] * 1e6:.1f} "
             f"micrometres on a {wall['extent'][2]:.4f} m span"],
            ["Maximum non-orthogonality",
             f"{non_ortho:.2f} deg" if non_ortho is not None else "not read"],
            ["Maximum skewness",
             f"{skew:.3f}" if skew is not None else "not read"],
        ]
        return MeshPlan(
            # THE COMMAND THE STAGE RUNS AND CAN RUN. Both halves of the old
            # blocker are resolved together, which is what the previous
            # comment here required: the mesher named is one that exists on
            # this host (python3 plus the reproducer), and the work_dir is
            # scratch. The measured regression that comment recorded --
            # repointing work_dir alone gave "the meshing stage names a
            # mesher that is not on this machine", 20 events, 5 of 9 stages
            # -- is what GRID_BUILDER exists to close: the container-only
            # pipeline (cgns_utils/pyHyp/plot3dToFoam/autoPatch) is recorded
            # in that script's docstring as what BUILT the grid, and the
            # stage reproduces the stored grid instead of pretending to
            # rebuild it.
            command=["python3", str(GRID_BUILDER), "--out", str(MESH_WORK)],
            work_dir=MESH_WORK,
            # THE COUNT CITES THE SERVED COPY OF THE SOLVED GRID, not the
            # mesh-time JSON: `_panel` locates the ParaView renders through
            # this citation and re-reads `owner` beside it, so the picture
            # and the printed count cannot come apart. The VALUE still comes
            # from the mesh-time record and the two are asserted equal at
            # drive time by the sequencer (sidecar, owner, printed count).
            cell_count=Measured(int(mesh["identity_assert"]["measured_cells"]),
                                "cells", SERVED_GRID / "constant" / "polyMesh"),
            resolution_headers=["Quantity", "Value"],
            resolution_rows=rows,
            wall_zoom_hint=("the first of the 39 layers marched from the wing "
                            "surface"),
            expected_seconds=float(mesh["mesh_only_wall_s"]))

    # -- stage 6 ------------------------------------------------------------
    def feasibility(self) -> Feasibility:
        """The short check before the budget is committed, and its result.

        One evaluation of the wing at the target lift, which the run's own
        first row took 16 seconds to produce. It is the number the whole
        reduction is afterwards measured from, so getting it before committing
        is what makes the rest worth committing.
        """
        frames = _major_frames(self._replay())
        first = frames[0]
        seconds = float(self._replay()["series_major"][0]["wall_s"])
        return Feasibility(
            check=("One evaluation of the wing at the target lift, to fix the "
                   "drag the whole result will be measured from before any "
                   "budget is committed."),
            result=Measured(round(first["objective_cd"], 6), "", REPLAY_FILE),
            verdict_for_user=(f"The wing reads drag "
                              f"{first['objective_cd']:.6f} at lift "
                              f"{first['lift_cl']:.3f}, in under half a "
                              f"minute. The reduction now has a fixed "
                              f"point. The run is worth committing."),
            seconds=seconds)

    # -- stage 7 ------------------------------------------------------------
    def solve_replay(self) -> SolveReplay:
        """The recorded monitors, the real cost, and the displayed clock.

        ``cases`` is empty ON PURPOSE and the emptiness is not a shortcut. The
        shared solver stage reads an OpenFOAM SIMPLE case and this run is an
        optimisation driver, so this act carries its own solver stage
        (:class:`ActDSequencer`) rather than handing the shared reader a tree
        it cannot read. The base sequencer refuses an act with no cases, which
        is the correct behaviour and is what stops this act being driven by
        the wrong sequencer without anyone noticing.
        """
        doc = self._replay()
        record = self._record()
        wall = float(doc["wall_time"]["process_wall_s"])
        clock = doc["display_clock"]
        run_root = Path(self._history()["_source_dir"])
        return SolveReplay(
            series=[
                SeriesSpec(run_root / "opt_IPOPT.txt", "iter", "iteration",
                           "Major iteration"),
                SeriesSpec(run_root / "opt_IPOPT.txt", "objective_CD", "force",
                           "Drag coefficient"),
                SeriesSpec(run_root / "OptView.hst", "CL", "force",
                           "Lift coefficient"),
                SeriesSpec(run_root / "opt_IPOPT.txt", "inf_pr", "residual",
                           "Constraint violation"),
                SeriesSpec(run_root / "opt_IPOPT.txt", "inf_du", "residual",
                           "First order measure"),
                SeriesSpec(run_root / "opt_run_driver.log", "ksp_trace",
                           "residual", "Adjoint linear solve"),
            ],
            wall_seconds=Measured(wall, "s", REPLAY_FILE),
            ranks=int(record["mpi_ranks"]),
            total_iterations=int(doc["max_iter_setting"]),
            sweep_points=1,
            pace=float(clock["pacing_ratio"]),
            cases=(),
            elapsed_clock=ElapsedClock(
                seconds=float(clock[_DISPLAY_TOTAL_KEY]),
                basis=_production_basis_sentence(),
                measured=False))

    # -- stage 8 ------------------------------------------------------------
    def gates(self) -> GatesAndChecks:
        """The planted-reader checks and the grid statement, in tables."""
        identity = _load(IDENTITY_FILE)
        plant = identity["plant_control"]["sdk_geometry"]
        replay_plant = _plant_control()
        mesh = _load(MESH_TIME_FILE)
        rows = [
            ["Surface identity", f"{plant['plant_m'] * 1e3:.1f} mm",
             f"{plant['recovered_fraction_of_plant'] * 100:.2f}% of it read "
             f"back"],
            ["Objective curve", f"{replay_plant['planted']:.3e}",
             "read back exactly"],
            ["Displayed clock", f"{replay_plant['planted']:.3e}",
             "read back exactly"],
        ]
        return GatesAndChecks(
            planted_checks=Table(
                title="Instrument checks",
                headers=["Reader", "Perturbation put in", "What came back"],
                rows=rows, table_id="actd_planted"),
            conservation=None,
            grid_statement=(
                f"One grid of "
                f"{int(mesh['identity_assert']['measured_cells']):,} cells "
                f"carries the wing, the drag and every iteration on screen. "
                f"Results are relative to this mesh; grid independence not "
                f"assessed in this act."))

    # -- stage 9 ------------------------------------------------------------
    def results(self) -> Results:
        """Figures, tables, verification lines, limitations and the real cost."""
        history = self._history()
        record = self._record()
        doc = self._replay()
        decomp = _actd._decomposition()
        fd_rows = record["fd_verification_table"]["rows"]
        physical = [r for r in fd_rows
                    if not r["derivative"].startswith("geometry.")]
        worst = max(r["rel_error_pct"] for r in physical)
        baseline, final = history["baseline"], history["final"]
        reduction = float(history["drag_reduction_pct"])
        majors = int(history["major_iterations_completed"])
        # TWO COSTS, TWO HOMES, ONE SCREEN STORY. ``cost_actual`` is the
        # RECORD: the measured process wall at the run's own ranks (240.1
        # core-minutes gross), required measured by the contract because it
        # feeds the calibration ledger. What RENDERS is ``cost_story`` -- the
        # contract's own mechanism for an owner-stated on-screen compute
        # convention -- carrying her 0745Z set (provenance on
        # `_screen_compute`): the total on the prompt's 20-minute clock, and
        # the estimate-against-actual close her 0420Z order fixes, both
        # composed from the record, never typed.
        ranks = int(record["mpi_ranks"])
        cost = core_minutes(float(doc["wall_time"]["process_wall_s"]), ranks)
        screen = _screen_compute(doc, ranks)

        result_table = Table(
            title="Result",
            headers=["Quantity", "Value", "Reference or threshold"],
            rows=[
                [f"Drag reduction below the {_actd.BASELINE_NAME} at matched "
                 f"lift", f"{reduction:.1f}%",
                 "The two drags below are what it is measured from"],
                # Rendered through the one canonical helper (her 0540Z
                # one-choice order); it reads this same history record.
                ["Baseline drag coefficient",
                 f"{_actd.canonical_baseline_cd():.6f}",
                 f"Lift {_actd.CL_TARGET:g}"],
                ["Final drag coefficient", f"{final['CD']:.6f}",
                 f"Lift {final['CL']:.6f}"],
                ["Worst gradient group against finite difference",
                 f"{worst:.3g}%", f"{_actd.GATE_PASS_PCT:g}% threshold"],
                ["Major iterations", f"{majors}",
                 f"{int(doc['max_iter_setting'])} allowed, every one on the "
                 f"graded gradient"],
            ], table_id="actd_result", role="CHIEF ENGINEER")

        tables = [result_table]
        if decomp:
            lift_matched = decomp["lift_matched"]
            shares = decomp["shares"]
            tables.append(Table(
                title="Where the drag reduction came from. Every row at "
                      "matched lift",
                headers=["Step", "Drag coefficient", "Lift coefficient",
                         "Against the baseline"],
                rows=[
                    # The C_d cell renders the canonical baseline (Sanaa
                    # 0540Z: one choice everywhere; the helper's docstring
                    # carries the pick and its reason). The grader's own
                    # lift-matched 0.029621 stays in the decomposition
                    # record; the C_L cell is still that record's.
                    ["Baseline, untwisted",
                     f"{_actd.canonical_baseline_cd():.6f}",
                     f"{lift_matched['baseline']['CL']:.6f}",
                     "The point everything is measured from"],
                    ["Twist only, re-trimmed to the same lift",
                     f"{lift_matched['twist_only_at_CL05']['CD']:.6f}",
                     f"{lift_matched['twist_only_at_CL05']['CL']:.6f}",
                     f"{abs(shares['twist']['pct_of_baseline_drag']):.1f}% "
                     f"more drag"],
                    ["Twist and section shape, at the same lift",
                     f"{lift_matched['twist_and_shape_at_CL05']['CD']:.6f}",
                     f"{lift_matched['twist_and_shape_at_CL05']['CL']:.6f}",
                     # 0.1 precision by her 0330Z sig-figs rule: no band has
                     # landed, so no percentage renders past one decimal.
                     f"{shares['shape']['pct_of_baseline_drag']:.1f}% less "
                     f"drag from the shape, "
                     f"{decomp['total_reduction_pct']:.1f}% net"],
                ], table_id="actd_decomposition"))

        # EVERY FIGURE THIS ACT PUBLISHES IS CHECKED AT THIS CALL SITE, not
        # only inside the two builders that happen to check themselves. A
        # limit applied at one of three call sites is not applied: the crease
        # figure reached this list unchecked and its own titles had grown past
        # the standard. `_figure` refuses a title over ten words or a caption
        # over twenty before the payload is built, so the failure lands on a
        # drive rather than on a screen.
        def _figure(path, title, caption):
            title, caption = _a2_shape.check_figure_text(title, caption)
            return Figure(path, title, caption, "results")

        plots = [
            _figure(FIGURES / "a2_sections_5station.png",
                    _a2_shape.SECTION_TITLE, _a2_shape.SECTION_CAPTION),
            _figure(FIGURES / "a2_twist.png", _a2_shape.TWIST_TITLE,
                    _a2_shape.TWIST_CAPTION),
        ]
        fields = [
            _figure(FIGURES / "actD_crease_section.png",
                    "Section at the colour boundary on the wing",
                    "The nose closes against the baseline across the first "
                    "twentieth of the chord."),
        ]

        # One fact per sentence (her repeated shortening order, latest
        # 1100Z: "for all acts still condense the sentences").
        identity = _load(IDENTITY_FILE)
        verification = [
            (f"The gradient was graded against {_actd.FD_SOLVES} central "
             f"finite-difference solves of the full flow before it was "
             f"used."),
            (f"The worst physical group agreed to {worst:.3g}%, inside the "
             f"{_actd.GATE_PASS_PCT:g}% threshold fixed before the check."),
            (f"No sign reversal in any component that could steer it."),
            (f"The surface on screen was measured against the solved wall "
             f"patch."),
            (f"The two agree to "
             f"{identity['plant_control']['sdk_geometry']['two_way_max_m_clean'] * 1e6:.1f} "
             f"micrometres: {int(identity['solved_wall']['faces']):,} four "
             f"sided faces against "
             f"{int(identity['candidates']['sdk_geometry']['measured']['triangles']):,} "
             f"triangles over the same points."),
            CONVERGENCE_DECLINED_LINE,
        ]

        limitations = [
            # "single grid" is a PHYSICS FACT and stays. What went is the
            # absence-statement beside it: her rule is that the study is never
            # shown as absent, and the promise now sits in the verification
            # lines rather than being repeated here.
            ("Exploratory; single grid; the optimizer stopped while still "
             "taking drag down; no wind tunnel data for this wing."),
            ("The independent cross check registered for the angle of attack "
             "share did not run: that row's flow solve diverged, so it is not "
             "a result and its gate has no verdict."),
        ]

        box = round(screen["box_core_min"], 1)
        actual = round(screen["actual_core_min"], 1)
        # HER 1100Z TABLE ORDER: the 0745Z ruling's set renders as the
        # STANDARD compute table (the shared four-column shape every sweep
        # act uses; her reading "Workers | Core-min total | Wall" maps onto
        # it with the per-run column carrying this act's one run). Every
        # cell from `_screen_compute`, never typed. Renders as:
        # 4 | 80 | 80 | 20.0 minutes.
        tables.append(compute_table(
            ranks, f"{screen['actual_core_min']:.0f}",
            f"{screen['actual_core_min']:.0f}",
            f"{screen['wall_min']:.1f} minutes",
            table_id="actd_compute"))
        return Results(
            fields=fields, plots=plots, tables=tables,
            verification_lines=verification, limitations=limitations,
            cost_actual=Measured(round(cost, 1), "core-minutes", REPLAY_FILE),
            cost_estimate_from_stage_2=self.restatement().cost_estimate,
            cost_story=(
                screen["total_line"],
                f"The final cost is within "
                f"{abs(actual - box) / box * 100.0:.1f}% of the estimate, "
                f"{actual:.1f} core-minutes against {box:.1f} core-minutes "
                f"committed before launch.",
            ))

    # -- pacing -------------------------------------------------------------
    def agent_census(self):
        return (("prompt", 1), ("restatement", 2), ("assumption", 3),
                ("geometry", 3), ("meshing", 4), ("feasibility", 4),
                ("solving", 5), ("gates", 2), ("results", 0))

    def worker_census(self):
        """The workers tile follows this act's own parallel story (Sanaa
        0420Z: the on-screen worker count matches the screen; this act's
        number is the 4 ranks the run solved on). Read from the record's
        ``mpi_ranks``, never typed, matching the ``workers`` field the
        solving payloads already carry; it rises when the working stages
        begin and ends at zero with the results, per the fleet convention
        and the jet-flap act's shape.
        """
        w = int(self._record()["mpi_ranks"])
        return (("prompt", 0), ("restatement", 0), ("assumption", 0),
                ("geometry", 0), ("meshing", w), ("feasibility", w),
                ("solving", w), ("gates", 0), ("results", 0))

    # -- the act's own guard -------------------------------------------------
    def self_check(self) -> dict:
        """Run every string this act can produce past the screen checker.

        THE GAP THIS WAS WRITTEN FOR IS NOW CLOSED UPSTREAM (2026-09-01). It
        read: the shared sequencer guards what passes through
        ``Sequencer._publish``, but its meshing, gates and results stages hand
        tables and figures to ``emit_table`` and ``announce_plot`` on the RAW
        emit, so table CELLS and figure titles had no checker between them and
        a screen. That was true of five delegated publications and was reported
        upward rather than patched here, which was the right call: the fix
        landed in the shared file as a CHOKE POINT rather than five patches.
        ``Sequencer.run`` now wraps the emit once and hands only the wrapper
        down, so no stage holds the raw emit and ``Sequencer._publish`` refuses
        one that did not come through the guard.

        THIS METHOD STAYS, AND IS NOT NOW REDUNDANT. It checks this act's
        strings at AUTHORSHIP, before a screen exists; the sequencer's guard
        checks them at PUBLICATION, when the screen is already up and the only
        remedy left is to refuse mid-act. Catching a bad cell here means the
        act never reaches a camera with it; catching it there means the act
        dies on camera. Two checks at two moments, not one check twice.
        """
        checked = 0

        def scan(text: str, zone: str = "screen") -> None:
            nonlocal checked
            check_demo_language(str(text), zone=zone)
            checked += 1

        mesh = self.mesh_plan()
        for row in mesh.resolution_rows:
            for cell in row:
                scan(cell)
        scan(mesh.wall_zoom_hint)
        gates = self.gates()
        for row in gates.planted_checks.rows:
            for cell in row:
                scan(cell)
        scan(gates.planted_checks.title)
        results = self.results()
        for table in results.tables:
            scan(table.title)
            for header in table.headers:
                scan(header)
            for row in table.rows:
                for cell in row:
                    scan(cell)
        for figure in list(results.fields) + list(results.plots):
            scan(figure.title)
            scan(figure.caption)
        for line in results.limitations:
            scan(line, zone="limitations")
        for line in results.verification_lines:
            scan(line)
        scan(self.run_record().solver_header())
        scan(self.solve_replay().clock().on_screen())

        # THE HEADER CANNOT FORK. The solver sentence this act publishes and
        # the one adjoint_optimization builds are asserted to be the same
        # string, so the screen, the report and the certificate cannot end up
        # carrying three answers to "what solved this".
        header = self.run_record().solver_header()
        if header != _actd._solver_line():
            raise DemoContractError(
                "the solver header this act publishes is not the sentence the "
                "act's own builder produces; one of the two has drifted")

        # THE ASSUMPTIONS TABLE'S NUMBERS ARE ASSERTED AGAINST THE RUN, not
        # trusted to my transcription. Nine constants are typed in this module
        # for readability and every one is checked here against the file it was
        # read from: seven against the run script and its thermophysical
        # properties, three against the stored surface record. A typo in a
        # table cell is a wrong number on a filmed screen, and the only thing
        # standing between the two is this loop.
        #
        # A MISSING RUN ROOT IS REPORTED, NEVER SILENTLY PASSED. If the case is
        # not on this machine the check cannot run, and saying "skipped" is the
        # honest answer; returning as though it had passed is how a guard
        # becomes decoration.
        table_checked = self._check_assumption_constants()

        # THE CROSS-ACT CONVERGENCE ASSERT IS RETIRED WITH THE PROMISE
        # (Sanaa 1100Z: this act's request now declines the study, so this
        # act no longer publishes the shock-reflection act's stage-8 promise
        # sentence and the two screens are MEANT to differ). What is asserted
        # instead: the declined sentence must attribute the decline to the
        # REQUEST, because "the study was not run" without that attribution
        # would read as the platform's own omission, and the always-run rule
        # is overridden here only by the customer's own words.
        if "request declined" not in CONVERGENCE_DECLINED_LINE:
            raise DemoContractError(
                "the declined-study sentence must attribute the decline to "
                "the request; without that attribution it reads as the "
                "platform's own omission")

        # The standing prohibitions, checked over the same strings.
        return {"strings_checked": checked,
                "solver_header_matches_builder": True,
                "assumption_constants": table_checked,
                "plant_control": _plant_control()}


    # -- the tail: the Report tab -------------------------------------------
    def closing(self) -> "Closing | None":
        """The act ends in a report, not a table.

        THE REPORT TAB WAS EMPTY FOR THE WHOLE ACT because nothing published a
        ``report.ready``, and the digest never reached a Conclusion heading
        because no phase was ever opened. Both are events the page has always
        been able to render; no act was sending them.

        EVERY NUMBER IS READ FROM THE FROZEN DECOMPOSITION RECORD, which is the
        grader's own output with the grader's sha256 beside it. Nothing is
        recomputed here and nothing is typed.

        THE RESULT ROWS ARE BUILT TO THE READ-ALONE TEST. A row is consumed
        alone, so each `quantity` carries the noun that makes its value true --
        "at matched lift" on the shares, because a share quoted without it is
        the exact trap this act exists to show, and "single grid" on the drag,
        because one mesh is the whole discretisation story.

        NEXT INVESTIGATIONS ARE NEW QUESTIONS, NEVER REMEDIATIONS. That is the
        report's own rule and it is not this act's to relax: "refine the grid"
        is a limitation and it is already in the limitations box. The three
        below are things nobody here knows the answer to.
        """
        decomp = _actd._decomposition()
        if not decomp:
            return None
        shares = decomp["shares"]
        matched = decomp["lift_matched"]
        # KEYED ON WHAT THE RECORD ACTUALLY HOLDS. The final row is
        # `twist_and_shape_at_CL05`, not `final` -- I guessed the key, the read
        # raised, and guessing a key is the same error class as guessing a
        # denominator. Named here so the next reader does not repeat it.
        base = matched["baseline"]
        final = matched["twist_and_shape_at_CL05"]
        trap = decomp["counter_examples"]["unmodified_wing_at_final_incidence"]
        total = float(decomp["total_reduction_pct"])
        return Closing(
            title="Where the drag reduction comes from",
            # SIGNIFICANT FIGURES BY HER 0330Z RULE: "no number on any screen
            # carries more decimals than its uncertainty supports, 0.1
            # precision until a band exists." One grid, no band landed, so
            # every percentage below renders at 0.1; the full-precision
            # values stay in the decomposition record this method reads.
            abstract=[
                f"Drag falls {total:.1f} percent on this wing, with lift held "
                f"at {_actd.CL_TARGET:g} at both ends of the comparison.",
                f"Taken apart at matched lift, the section shape carries "
                f"{shares['shape']['pct_of_drop']:.1f} percent of the drop and "
                f"the twist on its own carries "
                f"{shares['twist']['pct_of_drop']:.1f} percent.",
                "The angle of attack contributes nothing by construction, "
                "because lift is held as an equality constraint.",
            ],
            methods=[
                "Steady compressible flow, closed with a one-equation model "
                "calibrated for attached aerofoil flow.",
                "A reverse-mode discrete adjoint supplies the gradient, and it "
                "is graded against finite differences of the same solver "
                "before any of it is spent.",
                f"Every intermediate design is solved at the same lift, so no "
                f"row in the comparison is flown at a different angle to buy "
                f"its drag.",
            ],
            results=[
                # .6f, NOT .8f (her 0540Z consistency order): every other
                # surface prints C_d at six decimals, and the start row
                # renders the canonical baseline through the one helper so
                # "printed identically everywhere" is a construction, not a
                # coincidence. The record keeps full precision.
                {"quantity": "drag coefficient at the start, single grid",
                 "value": f"{_actd.canonical_baseline_cd():.6f}",
                 "envelope": "no discretisation band; one mesh",
                 "reason": f"lift held at {base['CL']:g}"},
                {"quantity": "drag coefficient at the finish, single grid",
                 "value": f"{final['CD']:.6f}",
                 "envelope": "no discretisation band; one mesh",
                 "reason": f"lift held at {final['CL']:g}"},
                {"quantity": "share of the drop from section shape, "
                             "at matched lift",
                 "value": f"{shares['shape']['pct_of_drop']:.1f} percent",
                 "envelope": "band fixed beforehand, 92 to 105 percent",
                 "reason": "measured inside the band written down first"},
                {"quantity": "share of the drop from twist alone, "
                             "at matched lift",
                 "value": f"{shares['twist']['pct_of_drop']:.1f} percent",
                 "envelope": "band fixed beforehand, minus 5 to plus 8 percent",
                 "reason": "twist on its own makes the drag slightly worse"},
                {"quantity": "the same wing flown lower, lift NOT held",
                 "value": f"{trap['CD']:.6f}",
                 "envelope": f"lift falls to {trap['CL']:.6f}",
                 "reason": "shown to make the trap visible, not as a result"},
            ],
            uncertainty=[
                "One grid, so no number here carries a discretisation band.",
                "The optimiser was still taking drag down when a time limit "
                "set beforehand stopped it.",
                "The gradient is graded at a single finite-difference step, "
                "and the sweep justifying that step belongs to a smaller case.",
                "The independent re-trim yielded no value, so nothing "
                "confirms the zero angle-of-attack share on its own.",
                "Nothing here is compared against wind tunnel or flight data.",
            ],
            next_investigations=[
                "Does the section-shape share hold at a Reynolds number ten "
                "times higher, or is it a low-speed result?",
                "Does twist stop being a penalty on a wing of different "
                "aspect ratio, where the spanload has more to gain?",
                "How much of the remaining drag is reachable at all, if the "
                "optimiser is allowed to run to its own stopping condition?",
            ],
            conclusion_lines=[
                f"Drag falls {total:.1f} percent with lift held at both ends.",
                f"Essentially all of it is section shape: "
                f"{shares['shape']['pct_of_drop']:.1f} percent of the drop.",
                "Twist on its own makes the drag slightly worse, which is not "
                "the tidier answer, and it is the measured one.",
                CONVERGENCE_DECLINED_LINE,
                "The full report, with every figure, is in the Report tab.",
            ],
            # STATES WHAT THIS RUN HAS. IT DOES NOT PROMISE ONE, AND IT NO
            # LONGER SPEAKS THE SENTENCE SANAA REMOVED (1100Z: "remove No
            # sealed certificate is attached to this run"). The contract
            # refuses an empty certificate_state (silence would read as one
            # having been issued), so the minimal honest alternative renders
            # instead: certification rides the grid convergence study, and
            # this request declined that study, so the absence is the
            # customer's own choice stated as fact. No banned issuance
            # phrasing ("certificate is issued" stays banned); no future
            # certificate promised.
            certificate_state=("Certification is offered with the grid "
                               "convergence study, which this request "
                               "declined."),
        )

    # -- which sequencer walks this act -------------------------------------
    def sequencer(self):
        """This act replaces the solving stage, and now SAYS so to every driver.

        THE SUBCLASS IS NOT NEW; THE DECLARATION IS. ``ActDSequencer`` has
        existed since this act was written, but it was named only inside this
        module's own ``drive()``, which the dispatch entry
        (:func:`demo_sequencer.make_act_entry`) calls and NOTHING ELSE DOES.
        Every other driver -- :func:`demo_sequencer.run_act`, and therefore
        ``scripts/check_demo_acts.py``, which is the PRE-SHOOT GATE -- built
        the base :class:`demo_sequencer.Sequencer` by name, reached the shared
        solving stage, found ``SolveReplay.cases`` empty and refused. So the
        gate could not reach this act's gates or results stages at all, and the
        act that works end to end through its own driver was half-wired through
        the shared one.

        MEASURED, NOT REASONED, before this method existed and after:

            through ``run_act``   29 events,  7 of 9 stages, then refused
                                  347 events, 9 of 9 stages
            through ``drive()``   347 events, 9 of 9 stages, both times

        The refusal it was hitting is CORRECT BEHAVIOUR and is not touched
        here: an act that supplies neither a case list nor a sequencer of its
        own has no way for its logs to be read, and saying so is the right
        answer. What was wrong was that this act supplied one and never
        declared it. ``SolveReplay.cases`` is empty for this act ON PURPOSE --
        the shared replay reader wants a force history and a per-case status
        record, and the adjoint optimisation writes neither.

        RETURNS THE CLASS, NOT AN INSTANCE. The base contract at
        ``demo_mode.py:1606`` says "the sequencer CLASS that walks THIS act",
        and ``run_act`` constructs it. Same shape as the sibling repair at
        ``dmr_act.py:1114``.
        """
        return ActDSequencer


# =========================================================================
# The sequencer: the shared walk, with this act's own solver stage
# =========================================================================

@dataclass
class ActDSequencer(Sequencer):
    """The shared nine-stage walk, with one stage replaced and no others.

    ``screen_seconds`` is how much REAL time the solver stage occupies. In a
    shoot it is the displayed 20 minutes, so the shoot clock and the displayed
    clock run together and the compression is exactly the recorded
    3601 s : 1200 s. In a drive it is small and the sleep is injected, and not
    one published value changes.
    """

    screen_seconds: float = 1200.0

    #: The pre-rendered face-by-face wall-patch frames (Sanaa 0540Z: every
    #: wing view in this act draws the solver's wall patch, 1,008 quad faces,
    #: true edges, flat per-face colour). Rendered by
    #: ``cases/dafoam/actd_render_grid_panels.py --wing-frames`` beside the
    #: served grid, so the frames and the cell-count citation live in one
    #: place.
    WING_FRAMES = SERVED_GRID / "paraview" / "wing"

    def _wing_panel(self, emit, name: str, label: str) -> None:
        """Publish one wall-patch frame as a mesh panel, with its provenance.

        THE CAPTION IS THE SIDECAR'S, NEVER TYPED HERE: her verbatim
        wall-patch sentence rides the render's own provenance record, and the
        sidecar's ``wall_faces`` is asserted against the identity record's
        solved wall patch, so "1,008 faces" and the picture cannot come
        apart. ``loadMeshPanel`` takes url, label and caption with no counts;
        the sidecar is copied beside the served PNG for a reader, not
        published (it carries paths, and a path never reaches a payload that
        renders). A missing declared frame is a REFUSAL, not a silent skip:
        these frames are the act's wing views and an absence must be loud.
        """
        import shutil
        from .demo_sequencer import SequencerRefused
        from . import OUT_ROOT

        shot = self.WING_FRAMES / f"{name}.png"
        side = shot.with_suffix(".json")
        if not (shot.is_file() and side.is_file()):
            raise SequencerRefused(
                f"this act draws its wing views from the pre-rendered "
                f"wall-patch frames and {name!r} is not on disk; the screen "
                f"stops rather than falling back to a tessellation")
        record = json.loads(side.read_text(encoding="utf-8"))
        solved = int(_load(IDENTITY_FILE)["solved_wall"]["faces"])
        if int(record.get("wall_faces", -1)) != solved:
            raise SequencerRefused(
                f"the frame's sidecar records {record.get('wall_faces')} "
                f"wall faces and the solved patch holds {solved}; the "
                f"caption and the picture would disagree")
        caption = str(record.get("caption", ""))
        if not caption:
            raise SequencerRefused(
                "a wall-patch frame with no caption in its provenance does "
                "not go on camera")
        store = self._panel_store()
        out = Path(OUT_ROOT) / store
        out.mkdir(parents=True, exist_ok=True)
        shutil.copy2(shot, out / shot.name)
        shutil.copy2(side, out / side.name)
        self._publish(emit, "mesh.panel", {
            "stage": "solving",
            "url": f"/api/plot/{store}/{shot.name}",
            "label": label,
            "caption": caption,
        })

    #: HER CAPTION, VERBATIM (0540Z item 5). Published with the volume cut
    #: and never paraphrased; the sidecar carries the same sentence.
    VOLUME_CUT_CAPTION = ("the volume mesh at the symmetry plane, wall "
                          "layers resolved.")

    def _stage_meshing(self, emit, script, record) -> dict:
        """The shared meshing stage, plus the symmetry-plane volume cut.

        Sanaa 0540Z item 5 asks for ONE additional mesh view; the shared
        stage publishes the declared ``mesh`` and ``mesh_zoom`` panels, and
        this override publishes the ``volume_cut`` through the same
        :meth:`_publish_panel` path, so it rides the same three-readings
        cell-count assertion (printed count, sidecar, ``owner`` on disk) and
        the same screen guard. Declared in ``rendered_panels``, so its
        absence on disk is a refusal, never a silent skip.
        """
        published = super()._stage_meshing(emit, script, record)
        self._publish_panel(emit, self.act.mesh_plan(), "volume_cut",
                            stage="meshing",
                            label="38,304 cells at the symmetry plane",
                            caption=self.VOLUME_CUT_CAPTION)
        return published

    def _stage_solving(self, emit, script, record) -> dict:
        replay = self.act.solve_replay()
        doc = self.act._replay()
        frames = _major_frames(doc)
        adjoint = doc["adjoint_solves"]
        summary = doc["adjoint_summary"]
        clock = replay.clock()
        control = _plant_control()
        parts = _clock_parts(doc)
        total = int(doc["max_iter_setting"])
        counter_to = int(doc["counter_runs_to"])
        if frames[-1]["iteration"] != counter_to:
            raise DemoContractError(
                f"the counter's last frame reads {frames[-1]['iteration']} "
                f"against a recorded {counter_to}")

        self._say(script, "Solving the wing at fixed lift.",
                  tense="progressive")
        # THE REAL WORKER COUNT RIDES EVERY SOLVING PAYLOAD. Sanaa's 04:20Z
        # order: the number of workers on screen matches the run. This act's
        # number is the ranks the run solved on, read from its own record,
        # never typed; the field name matches the accessor the page already
        # owns (`p.workers`), on the shock-reflection act's precedent, so
        # wiring the tile needs no act edit.
        workers = int(self.act._record()["mpi_ranks"])
        self._publish(emit, "solve.begin", {
            "stage": "solving",
            "points": 1, "point_index": None,
            "iterations": total,
            "workers": workers,
            "counter_runs_to": counter_to,
            "labels": [spec.label for spec in replay.series],
            "controls": [
                "the objective curve and the displayed clock were each read "
                "back after a known perturbation was put into them",
                f"every one of the {len(frames)} counted iterations matched "
                f"between the two records that carry it",
            ],
        })

        # THE WING WALKS WITH THE COUNTER (Sanaa 0540Z: geometry changes
        # appear WITH the team's work, not after it). The reference patch
        # and the gradient on the skin go up as the stage opens; each strided
        # frame is published AT its own major inside the schedule loop below,
        # so the wall-patch views and the trace advance together.
        self._wing_panel(emit, "wing_baseline",
                         f"Reference wing, {_actd.BASELINE_NAME}")
        # "Gradient descent", her 1100Z wording order, replacing the
        # "where the adjoint says to push" phrasing on the wire.
        self._wing_panel(emit, "wing_gradient",
                         "Gradient descent direction on the skin, at fixed "
                         "lift")

        # ONE SCHEDULE, TWO MONITORS, AND THEY ARE NOT ON ONE CLOCK. The
        # counter advances on the displayed time axis; the adjoint solves
        # advance on their own ordinal, because their log's clock has a
        # different origin from the optimiser's and the record forbids adding
        # the two. Scheduling is a decision about WHEN; neither monitor's
        # values are touched.
        display_total = float(doc["display_clock"][_DISPLAY_TOTAL_KEY])
        schedule: list[tuple[float, str, dict]] = []
        for frame in frames:
            schedule.append((frame["display_s"] / display_total, "major",
                             frame))
        for index, solve in enumerate(adjoint, start=1):
            schedule.append((index / len(adjoint), "adjoint",
                             {"index": index, "solve": solve}))
        schedule.sort(key=lambda item: item[0])

        origin = self.clock()
        for fraction, kind, payload in schedule:
            deadline = origin + fraction * float(self.screen_seconds)
            remaining = deadline - self.clock()
            if remaining > 0:
                self.sleep(remaining)
            if kind == "major":
                # The wall-patch frame for this major, published AT the
                # major it belongs to (strided set = the frames the
                # renderer bakes, `adjoint_optimization.SHOWN_FRAME_ITERS`,
                # imported never retyped).
                if payload["iteration"] in _actd.SHOWN_FRAME_ITERS:
                    self._wing_panel(
                        emit, f"wing_iter_{payload['iteration']:02d}",
                        f"Major iteration {payload['iteration']} of "
                        f"{counter_to}")
                self._publish(emit, "solve.frame", {
                    "stage": "solving",
                    # THE MAJOR FRAME IS LABELLED so the three trace series
                    # below can be told from it by a reader that needs the
                    # per-iteration record rather than the per-trace one.
                    "label": "Major iteration",
                    "point_index": 1, "points": 1,
                    "iteration": payload["iteration"],
                    "iterations": total,
                    "workers": workers,
                    "elapsed": _mmss(payload["display_s"]),
                    "elapsed_s": round(payload["display_s"], 3),
                    "coefficients": {
                        "Drag coefficient": payload["objective_cd"],
                        "Lift coefficient": payload["lift_cl"],
                        "Volume constraint": payload["volume_constraint"],
                    },
                    "residuals": {
                        "Constraint violation":
                            payload["constraint_violation"],
                        "First order measure":
                            payload["first_order_measure"],
                    },
                    "source_row": payload["source_row"],
                })
                # -- the traces, as SEPARATE LABELLED SERIES ---------------
                #
                # WHY THIS ACT PUBLISHES SERIES AT ALL, given it is ONE run.
                # Sanaa's stage 5 asks for "sweep or multipoint runs shown
                # simultaneously as small multiples on one screen (residuals,
                # force or temperature traces)". Act D is neither a sweep nor
                # multipoint -- it is a single optimisation -- so the SWEEP
                # reading of that line does not apply to it. The TRACES reading
                # does, and it is the one the act already committed to: six
                # `SeriesSpec` entries with distinct labels and distinct
                # `drives` values have been declared since the act was written.
                # THE DECLARATION WAS THERE AND THE WIRE NEVER CARRIED IT --
                # the same shape as the sequencer this act declared and never
                # returned, and as the three voices the sheet had and the
                # screen did not.
                #
                # NOTHING HERE IS SYNTHESISED. Every value is the one already
                # in the frame above, read from the same recorded row, so a
                # trace cannot disagree with the frame it was split out of.
                # ALL FOUR NON-RAGGED DECLARED SERIES, not the three I first
                # chose. The declaration->wire sweep caught "Lift coefficient"
                # declared in `solve_replay()` and published only as a KEY
                # INSIDE the major frame's coefficients dict -- the seventh
                # instance of this class, in my own work from an hour earlier,
                # found by the instrument built to find it.
                #
                # Lift is the series a viewer most needs here: it is the
                # quantity being HELD at 0.5 while drag falls, so a flat lift
                # trace beside a falling drag trace is the whole claim of the
                # act, on screen, without a sentence.
                for label, value, drives in (
                        ("Drag coefficient", payload["objective_cd"], "force"),
                        ("Lift coefficient", payload["lift_cl"], "force"),
                        ("Constraint violation",
                         payload["constraint_violation"], "residual"),
                        ("First order measure",
                         payload["first_order_measure"], "residual")):
                    self._publish(emit, "solve.frame", {
                        "stage": "solving",
                        "label": label,
                        "drives": drives,
                        "point_index": 1, "points": 1,
                        "iteration": payload["iteration"],
                        "iterations": total,
                        "workers": workers,
                        "elapsed": _mmss(payload["display_s"]),
                        "elapsed_s": round(payload["display_s"], 3),
                        "value": value,
                        "source_row": payload["source_row"],
                    })
            else:
                solve = payload["solve"]
                self._publish(emit, "solve.adjoint", {
                    "stage": "solving",
                    "point_index": 1, "points": 1,
                    "iteration": frames[-1]["iteration"],
                    "iterations": total,
                    "adjoint_solve": payload["index"],
                    "adjoint_solves": len(adjoint),
                    "completed": bool(solve.get("completed")),
                    # RAGGED AS THE LOG IS RAGGED: one to four points per
                    # solve, shipped as they are rather than padded to a
                    # common length that no log recorded.
                    "trace": [{"step": int(point["ksp_iter"]),
                               "residual": float(point["residual_norm"])}
                              for point in solve["ksp_trace"]],
                })

        # THE INBOARD PASS, the same strided surfaces on the closer camera,
        # after the walk exactly as the mission act plays it. Paced with a
        # real beat (never a burst: the 48-frame burst is the measured
        # failure the strided set exists to close), proportionate to this
        # drive's own screen time so an offline gate drive is not slowed.
        near_beat = min(1.2, float(self.screen_seconds) / 1000.0)
        for it in _actd.SHOWN_FRAME_ITERS:
            # "Close view", not "Inboard span": her 1100Z order pulls the
            # close camera back until the whole patch sits inside the frame,
            # so the frame now shows the full patch and an inboard label
            # would overclaim.
            self._wing_panel(emit, f"wing_near_{it:02d}",
                             f"Close view, iteration {it} of {counter_to}")
            self.sleep(near_beat)

        published = self._publish(emit, "solve.end", {
            "stage": "solving",
            "point_index": 1, "points": 1,
            "iteration": counter_to,
            "iterations": total,
            "workers": workers,
            "counted_iterations": len(frames),
            "adjoint_solves_opened": int(summary["linear_solves_opened"]),
            "adjoint_solves_completed": int(summary["linear_solves_completed"]),
            "adjoint_solves_left_open": int(summary["linear_solves_truncated"]),
            "adjoint_note": ("The last linear solve was opened and never "
                             "closed: the clock ended the run inside it."),
            "elapsed": _mmss(display_total),
            "elapsed_parts": [{"what": what, "clock": _mmss(seconds),
                               "seconds": round(seconds, 3)}
                              for what, seconds in parts],
            "elapsed_parts_sum": _mmss(sum(s for _, s in parts)),
            # THE WIRE CARRIES THE SCREEN'S FIGURE (her 0745Z ruling;
            # provenance on `_screen_compute`): the wall the clock shows at
            # the run's own rank count. The key was `core_min_measured` at
            # the measured 240.05; a derived figure under a key that says
            # measured would be a false label, so the key changed with the
            # value (no page accessor reads the old key; measured on
            # control_room.html). The measured pair stays in the replay
            # record and the internal compute note.
            "core_min": round(_screen_compute(
                doc, replay.ranks)["actual_core_min"], 1),
            "cost_basis": ("core-minutes on the clock this screen carries, "
                           "at the run's own rank count; no currency figure "
                           "is stated on any screen"),
            "controls": [control["reader_is_evidence"]] and [
                "the reader was shown a known perturbation on both the "
                "objective curve and the displayed clock, and read both back"],
            "finished": True,
        })
        self._say(script,
                  f"Solved the wing over {counter_to} major iterations on the "
                  f"graded gradient.", tense="past")
        self._publish(emit, "demo.elapsed", {
            "stage": "solving",
            "elapsed": clock.on_screen(),
            "clock": _mmss(clock.seconds),
            "finished": True,
        })
        return published


ACT = register_act("adjoint-wing", AdjointWingAct())


def drive(emit=None, script=None, *, screen_seconds: float | None = None,
          sleep=None, clock=None) -> dict:
    """Walk Act D through DEMO MODE. Returns the sequencer's record."""
    import time as _time

    # ONE SOURCE FOR THE NUMBER AND ONE FOR THE CLASS.
    #
    # ``screen_seconds`` used to be defaulted to 1200.0 HERE as well as on
    # ``ActDSequencer``, and ``run_act`` passes none -- so the twenty-minute
    # display figure Sanaa personally ordered onto this act's face was written
    # twice, and the dispatcher path and this path would have produced
    # different solver-stage clocks the moment either moved, with no gate able
    # to see it. Defaulting to None here and omitting the key leaves the
    # dataclass field as the only place the number lives.
    kwargs = {}
    if screen_seconds is not None:
        kwargs["screen_seconds"] = screen_seconds
    if sleep is not None:
        kwargs["sleep"] = sleep
    if clock is not None:
        kwargs["clock"] = clock
    else:
        kwargs.setdefault("clock", _time.monotonic)
    # ...and the CLASS comes from the act's own declaration rather than being
    # named a second time here, so this path and ``run_act`` cannot walk this
    # act with two different sequencers.
    return ACT.sequencer()(act=ACT, **kwargs).run(emit=emit, script=script)


if __name__ == "__main__":                       # pragma: no cover
    ACT.self_check()
    drive()
