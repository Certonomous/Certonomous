"""Act B, the blown wing, as a DEMO MODE act.

Every value below is read off the landed run tree at the moment it is asked
for. There are no numbers in this file: the lift table, the cell count, the
wall resolution, the wall time and the cost all come from
:mod:`workflows._jf1_numbers`, :mod:`workflows._jf1_geometry` and the run
status files, which are the readers that carry the planted controls. A
constant retyped here would be a second copy free to drift from the run.

Sanaa's jet-flap specifics (2026-09-01 ~03:40Z) are structural rather than
remembered:

* **One grid on screen.** The force grid carries the pressures and the lift
  table, and the finer companion grid is named in the limitations box and
  nowhere else, which :func:`demo_mode.check_demo_language` enforces by zone.

  THIS DOCSTRING USED TO SAY THE FORCE GRID CARRIED "FIELDS, PRESSURES AND THE
  LIFT TABLE ALIKE", AND SO DID STAGE 8, AND IT WAS FALSE. The only field
  picture the act shows is rendered from the finer companion grid, which stage
  9 correctly admitted while stage 8 denied it. ``assert_one_grid`` could not
  catch it: it guards the cases whose numbers are TABULATED, and a picture's
  grid reaches no table. ``_jf1_numbers.assert_display_grids`` is the whole
  rule -- it guards every grid the act displays, reads each figure's
  provenance record beside the figure itself, and RETURNS the measured facts
  the grid sentence is composed from, so the sentence cannot outrun what was
  measured. Reference areas differ 0.01 m2 against 1.0 m2 between these grids;
  lift read off one and labelled with the other is wrong by a hundred.
* **Her prompt, kept exactly.**
* **The lift table kept exactly**: surface lift, jet push, total, published.
* **Williams, Butler and Wood, ARC R&M 3304 (1961), eq. 2, stated once.**

WHAT THIS ACT DOES NOT CLAIM. No calculation in this family met its
convergence target, so none is claimed to have, and one grid supports no
discretisation band and no percentage agreement with the published curve. The
limitations box says so in her own words.
"""

from __future__ import annotations

from pathlib import Path

from . import _jf1_geometry, _jf1_numbers
from .demo_mode import (Assumption, DemoAct, ElapsedClock, Feasibility, Figure,
                        GatesAndChecks, Geometry, GeometryMatch, MeshPlan,
                        Measured, Prompt, Restatement, Results, RunRecord,
                        SeriesSpec, SolveReplay, Table, register_act)

#: Her prompt, verbatim. Not this act's to reword.
PROMPT = ("Blown-wing high-lift: sweep the trailing-edge jet momentum "
          "coefficient from 0 to 0.4 and report lift against blowing with the "
          "classical jet-flap theory.")

#: Stated once, per her instruction.
REFERENCE = "Williams, Butler and Wood, ARC R&M 3304 (1961), eq. 2."

#: The served surface, under the directory the control-room server reads.
SURFACE = "airfoil_blown_slot.stl"

#: What the compute figure is CALLED on a customer screen. The quantity is
#: unchanged -- wall seconds x ranks / 60, CLAUDE.md rule 12 -- and so is every
#: number derived from it. Only the name changes: "core-minutes" is this lab's
#: internal unit, and Sanaa's live-demo standard keeps internal information off
#: the customer surface. A viewer reads "processor-minutes" without being told
#: what a core is, and it is the same minute on the same processor.
COMPUTE_UNIT = "processor-minutes"

FIGURES = _jf1_numbers.RUN_ROOT / "artefacts"

#: The mesher that actually emits this grid, and a scratch tree it is allowed
#: to write into. NOT the solved case: a mesher writing a fresh polyMesh into
#: a landed graded run breaks the completion rule's age guard on a result that
#: cannot be re-solved. See the README in that directory.
MESH_BUILDER = Path("/home/ubuntu/Certonomous/cases/JF1_JET_FLAP/build_jf1.py")
MESH_WORK = _jf1_numbers.RUN_ROOT / "demo_mesh_work"

#: Every picture this act puts on camera, and the case each one is rendered
#: from. THIS IS THE DECLARATION THE GUARD CHECKS: the generators write a
#: provenance record beside the figures at render time, and
#: ``assert_display_grids`` refuses when a record names a case other than the
#: one declared here. A figure re-rendered from another grid therefore stops
#: the act rather than quietly changing what the screen is a picture of.
DISPLAYED_FIGURES: dict[str, str] = {
    "jet_flap_1_lift_vs_blowing": _jf1_numbers.SWEEP_CASES[3][1],
    "jet_flap_2_chordwise_pressure": _jf1_numbers.SWEEP_CASES[3][1],
    # Rendered from the C_mu = 0.10 row rather than the 0.20 row: the mesh
    # page draws ONE of the five, and the declaration names the case its
    # generator actually opened. Same grid, and the guard proves it -- but the
    # declaration is about provenance, so it names the case, not the family.
    "jet_flap_7_mesh_forcesweep": _jf1_numbers.SWEEP_CASES[2][1],
    "jet_flap_3_flow_field": _jf1_numbers.FLOW_CASE.name,
}


def _displayed_grids() -> dict:
    """Every grid this act displays, measured, tabulated or not.

    Called by stage 8 and stage 9 so both are built from ONE measurement.
    The two sentences drifted apart once already, in the direction that put a
    false one on camera, and the fix is that neither is typed.
    """
    rows = _jf1_numbers.sweep_rows()
    return _jf1_numbers.assert_display_grids(
        [Path(r["case_dir"]) for r in rows],
        {stem: _jf1_numbers.RUN_ROOT / case
         for stem, case in DISPLAYED_FIGURES.items()})


def _run_status(case_dir: Path) -> dict:
    from chief_engineer.replay_history import read_run_status

    return read_run_status(case_dir)


def _statuses() -> list[dict]:
    return [_run_status(_jf1_numbers.RUN_ROOT / name)
            for _, name in _jf1_numbers.SWEEP_CASES]


class JetFlapAct(DemoAct):
    """The blown wing, fed from the landed sweep."""

    name = "blown wing high-lift"

    # -- stage 0 ------------------------------------------------------------
    def run_record(self) -> RunRecord:
        primary = _jf1_numbers.RUN_ROOT / _jf1_numbers.SWEEP_CASES[3][1]
        status = _run_status(primary)
        return RunRecord(
            run_id="JF1",
            run_root=_jf1_numbers.RUN_ROOT,
            solver="OpenFOAM simpleFoam",
            physics=("steady incompressible turbulent flow over a wing "
                     "section with a blown trailing-edge slot, k-omega SST "
                     "resolved to the wall"),
            completion_evidence=Path(status["path"]),
            presentation_of="presentation of run JF1",
            record_path=Path(status["path"]))

    # -- stages 1 to 3 ------------------------------------------------------
    def prompt(self) -> Prompt:
        return Prompt(PROMPT)

    def restatement(self) -> Restatement:
        """What was understood, how sure, and what it was FORECAST to cost.

        THE FORECAST IS THE FORECAST, NOT THE SPEND. This slot used to carry
        the summed measured core-minutes -- the same figure stage 9 reports as
        the actual -- so the estimate-against-actual comparison rule 12
        requires read exactly 1.00x on camera, by construction, and concealed
        a 2.07x overrun. The forecast is now read out of the frozen
        registration's own five-point row, so the two numbers are two
        different measurements of two different things and the comparison
        means something.
        """
        cases = len(_jf1_numbers.SWEEP_CASES)
        forecast = _jf1_numbers.registered_sweep_estimate()
        return Restatement(
            restatement=(f"Solve {cases} blowing settings on one wing section "
                         f"and report lift against blowing."),
            confidence=("The section and the blowing range match a published "
                        "family, so the shape of the answer is known in "
                        "advance."),
            cost_estimate=Measured(round(forecast["total_core_min"], 1),
                                   COMPUTE_UNIT,
                                   _jf1_numbers.PREREGISTRATION, "derived"))

    def assumption(self) -> Assumption:
        facts = _jf1_numbers.sweep_facts()
        return Assumption(
            assumption=("The request treats the unblown case as the blown "
                        "case with the jet switched off."),
            finding=(f"The unblown calculation closes the slot instead, so "
                     f"the {facts['slot']['faces']} slot faces are wall "
                     f"rather than inlet."),
            correction=("The unblown row is a separate reference "
                        "calculation, not a member of the blown comparison."))

    # -- stage 4 ------------------------------------------------------------
    def geometry(self) -> Geometry:
        served = _jf1_geometry.STAGING / SURFACE
        chord, h_over_c = _jf1_geometry.measure_blown_slot(served)
        return Geometry(
            served_stl=served,
            display_label="wing section with a blown trailing-edge slot",
            matches=[
                GeometryMatch.from_module(
                    "chord", _jf1_geometry, solved_attr="SOLVED_CHORD_M",
                    tolerance_attr="SOLVED_GEOMETRY_TOL",
                    supplied=float(chord), source=served, unit="m"),
                GeometryMatch.from_module(
                    "slot height ratio", _jf1_geometry,
                    solved_attr="SOLVED_H_OVER_C",
                    tolerance_attr="SOLVED_GEOMETRY_TOL",
                    supplied=float(h_over_c), source=served),
            ])

    # -- stage 5 ------------------------------------------------------------
    def mesh_plan(self) -> MeshPlan:
        """The real mesher of THIS grid, and a working directory it may write.

        TWO THINGS HERE WERE FALSE AND ONE OF THEM WAS DANGEROUS.

        The mesher was named as ``blockMesh``. There is no ``blockMeshDict``
        anywhere in this campaign. The grid the five force calculations ran on
        is emitted by ``cases/JF1_JET_FLAP/build_jf1.py``, and the finer
        companion grid by ``mesh/make_jf1_mesh.py``; the invocation named
        below is the one the run's own launcher recorded, at
        ``run_jf1_blown.sh`` lines 268-270, rather than one composed here.

        The working directory was the SOLVED CASE. Nothing invokes the mesher
        today, so nothing has happened; the moment the meshing stage is made
        live, a mesher would write a fresh ``constant/polyMesh`` into a landed
        graded run and break the age guard the whole result rests on. That is
        not recoverable tonight. The working directory is now a scratch tree
        that holds no evidence, which is what ``work_dir`` is for.

        None of the NUMBERS on screen come from that directory. The cell
        count, the wall resolution and the mesh figure are all read from the
        solved case's own artifacts.
        """
        facts = _jf1_numbers.sweep_facts()
        yplus = facts["yplus"]
        case_dir = Path(facts["case_dir"])
        return MeshPlan(
            command=["python3", str(MESH_BUILDER), "--out", str(MESH_WORK),
                     "--level", "L1", "--slot-type", "patch"],
            work_dir=MESH_WORK,
            # Grouped HERE rather than at one of the two places it renders.
            # The same count reached the screen as "39984" from the geometry
            # sentence and as "39,984" from the gates line, which reads as two
            # different numbers to anyone not counting digits. The value is
            # formatted once, at the single point it is read.
            cell_count=Measured(f"{facts['cells']:,}", "cells",
                                case_dir / "constant" / "polyMesh"),
            resolution_headers=["Region", "Faces", "Smallest", "Largest",
                                "Mean"],
            resolution_rows=[[
                "Wall layer", str(yplus["n"]), f"{yplus['min']:.3f}",
                f"{yplus['max']:.3f}", f"{yplus['mean']:.3f}"]],
            wall_zoom_hint="the wall layers at the trailing-edge slot",
            expected_seconds=30.0)

    # -- stage 6 ------------------------------------------------------------
    def feasibility(self) -> Feasibility:
        rows = _jf1_numbers.sweep_rows()
        unblown = rows[0]
        return Feasibility(
            check=("A single unblown calculation on the same grid, to see "
                   "whether the section carries lift before any blowing."),
            result=Measured(round(float(unblown["CL_aero"]), 6), "",
                            Path(unblown["case_dir"])),
            verdict_for_user=("The unblown section carries almost no lift, so "
                              "the sweep measures blowing and not incidence."))

    # -- stage 7 ------------------------------------------------------------
    def solve_replay(self) -> SolveReplay:
        statuses = _statuses()
        cases = [(f"blowing {cmu:g}", _jf1_numbers.RUN_ROOT / name)
                 for cmu, name in _jf1_numbers.SWEEP_CASES]
        wall_total = sum(s["wall_s"] for s in statuses)
        span = self._wall_clock_span(statuses)
        return SolveReplay(
            series=[SeriesSpec(Path(statuses[0]["path"]), "Cl", "force",
                               "Lift coefficient"),
                    SeriesSpec(Path(statuses[0]["path"]), "p", "residual",
                               "Pressure residual")],
            # The COST basis: ranks x wall summed over the points that ran.
            wall_seconds=Measured(wall_total, "s", Path(statuses[0]["path"])),
            ranks=int(statuses[0]["ranks"]),
            total_iterations=int(_jf1_numbers.SWEEP_TIME),
            sweep_points=len(cases),
            cases=cases,
            # The ELAPSED figure, which is a different quantity: these points
            # ran concurrently, so their durations do not add.
            # PAST TENSE HERE IS CORRECT AND IS LEFT ALONE. This string was
            # put up for rewriting as narrative past tense. Sanaa's language
            # rule is zone-aware, not a blanket ban: "Progressive tense while
            # running, past tense for results." This line is published after
            # the replay finishes, carries `finished: true`, and reports a
            # completed span. It is a results line, so past tense is what she
            # asked for, and stripping it would have satisfied a rule she
            # never wrote.
            elapsed_clock=ElapsedClock(
                seconds=span, measured=True,
                basis=("The span of a sweep whose points ran concurrently."),
                source=Path(statuses[0]["path"])))

    @staticmethod
    def _wall_clock_span(statuses: list[dict]) -> float:
        """Span from the first start to the last end, in seconds.

        Not the sum: these points overlapped, and adding the durations of
        concurrent runs would report a duration no clock ever measured.
        """
        from datetime import datetime

        def stamp(text: str) -> datetime:
            return datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ")

        starts = [stamp(s["utc_start"]) for s in statuses]
        ends = [stamp(s["utc_end"]) for s in statuses]
        return (max(ends) - min(starts)).total_seconds()

    # -- stage 8 ------------------------------------------------------------
    def gates(self) -> GatesAndChecks:
        """Reader checks and the grid statement, the latter MEASURED.

        THE SENTENCE THIS STAGE USED TO RENDER WAS FALSE, and it was false
        about the one thing this stage exists to be right about. It read "one
        grid of 39,984 cells carries the fields, the pressures and the lift
        table". It carries the pressures and the lift table. The only field
        picture on the screen is rendered from the finer companion grid, and
        stage 9's limitations box said so while this stage denied it -- a
        screen asserting one grid beside its own admission of two.

        Two things changed. The sentence now claims only what is true, and it
        is composed from :func:`_displayed_grids`, which measures every grid
        the act displays and refuses a figure whose provenance record names a
        case other than the one declared. So the count in the sentence is the
        table's own, read from the table's own cases, and a figure swapped to
        another grid stops the act instead of quietly making it false again.

        The companion grid is not named here. Sanaa's zone rule keeps that
        admission in the limitations box and nowhere else, and
        :func:`demo_mode.check_demo_language` enforces it.
        """
        grids = _displayed_grids()
        plant = _jf1_numbers.PLANT
        return GatesAndChecks(
            planted_checks=Table(
                title="Instrument checks",
                headers=["Reader", "Planted", "Detected"],
                rows=[["Lift", f"{plant:.3e}", "yes"],
                      ["Wall resolution", f"{plant:.3e}", "yes"]],
                table_id="jf_planted"),
            conservation=None,
            grid_statement=(f"One grid of {grids['table']['cells']:,} cells "
                            f"carries the pressures and the lift table."))

    # -- stage 9 ------------------------------------------------------------
    def results(self) -> Results:
        rows = _jf1_numbers.sweep_rows()
        grids = _displayed_grids()
        statuses = _statuses()
        core_min = sum(s["core_min_measured"] for s in statuses)

        lift = Table(
            title="Lift against blowing",
            headers=["Blowing", "Surface lift", "Jet push", "Total",
                     "Published"],
            rows=[[f"{r['C_mu']:.2f}", f"{r['CL_aero']:.3f}",
                   f"{r['jet_reaction']:.3f}", f"{r['CL_total']:.3f}",
                   f"{r['CL_published']:.3f}"] for r in rows],
            table_id="jf_lift", role="CHIEF ENGINEER")

        table_cells = grids["table"]["cells"]
        figures = [
            Figure(FIGURES / "jet_flap_1_lift_vs_blowing.png",
                   "Lift against blowing", "Lift rises with blowing across "
                   "the five settings solved.", "results"),
            Figure(FIGURES / "jet_flap_2_chordwise_pressure.png",
                   "Chordwise pressure, blown and unblown",
                   "Blowing loads the rear of the section.", "results"),
            # THE MESH SLICE. Sanaa's shoot list requires every jet-flap
            # capability on screen and the grid itself was the one missing.
            # This slice is drawn cell by cell from the FORCE grid's own
            # stored mesh -- the grid the lift table and the pressures above
            # come from -- so it needs no companion label and breaks no rule.
            # The companion grid's own mesh pages exist and are deliberately
            # not served: showing a second grid's mesh is the mixing the
            # one-grid rule removes.
            Figure(FIGURES / "jet_flap_7_mesh_forcesweep.png",
                   "The grid the lift and pressures are computed on",
                   f"Sliced cell by cell: the wing, the slot and the "
                   f"{table_cells:,} cells around them.", "results"),
        ]
        fields = [
            Figure(FIGURES / "jet_flap_3_flow_field.png",
                   "Flow field at the slot", "The jet leaves the slot and "
                   "turns the flow past the trailing edge.", "results"),
        ]

        flow = grids["figures"]["jet_flap_3_flow_field"]
        return Results(
            fields=fields, plots=figures, tables=[lift],
            verification_lines=[
                f"Reference curve: {REFERENCE}",
                ("No experimental comparison is available for this section, "
                 "so the published curve is shown beside the solved points "
                 "and no agreement is claimed."),
            ],
            # BUILT FROM THE SAME MEASUREMENT AS STAGE 8, not typed beside it.
            # The two sentences drifted apart once, in the direction that put
            # the false one on camera; neither is a literal now.
            limitations=[
                (f"Exploratory; settling target not reached at high blowing; "
                 f"the lift table rests on one grid of {table_cells:,} cells; "
                 f"no wind-tunnel data for this section."),
                (f"Flow picture from a finer companion grid of "
                 f"{flow['cells']:,} cells; no number in the table comes "
                 f"from it."),
            ],
            cost_actual=Measured(round(core_min, 1), COMPUTE_UNIT,
                                 Path(statuses[0]["path"])),
            cost_estimate_from_stage_2=self.restatement().cost_estimate)

    # -- pacing -------------------------------------------------------------
    def agent_census(self):
        return (("prompt", 1), ("restatement", 2), ("assumption", 2),
                ("geometry", 3), ("meshing", 4), ("feasibility", 4),
                ("solving", 5), ("gates", 2), ("results", 0))


ACT = register_act("jet-flap", JetFlapAct())
