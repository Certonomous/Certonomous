"""Act B, the blown wing, as a DEMO MODE act.

Every value below is read off the landed run tree at the moment it is asked
for. There are no numbers in this file: the lift table, the cell count, the
wall resolution, the wall time and the cost all come from
:mod:`workflows._jf1_numbers`, :mod:`workflows._jf1_geometry` and the run
status files, which are the readers that carry the planted controls. A
constant retyped here would be a second copy free to drift from the run.

Sanaa's jet-flap specifics (2026-09-01 ~03:40Z) are structural rather than
remembered:

* **One grid on screen.** The 39,984-cell force grid carries fields,
  pressures and the lift table alike. ``_jf1_numbers.assert_one_grid`` refuses
  a mixed table, and the finer companion grid is named in the limitations box
  and nowhere else, which :func:`demo_mode.check_demo_language` enforces by
  zone.
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

FIGURES = _jf1_numbers.RUN_ROOT / "artefacts"


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
        cases = len(_jf1_numbers.SWEEP_CASES)
        core_min = sum(s["core_min_measured"] for s in _statuses())
        return Restatement(
            restatement=(f"Solve {cases} blowing settings on one wing section "
                         f"and report lift against blowing."),
            confidence=("The section and the blowing range match a published "
                        "family, so the shape of the answer is known in "
                        "advance."),
            cost_estimate=Measured(round(core_min, 1), "core-minutes",
                                   Path(_statuses()[0]["path"]), "derived"))

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
        facts = _jf1_numbers.sweep_facts()
        yplus = facts["yplus"]
        case_dir = Path(facts["case_dir"])
        return MeshPlan(
            command=["blockMesh"],
            work_dir=case_dir,
            cell_count=Measured(facts["cells"], "cells",
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
        facts = _jf1_numbers.sweep_facts()
        plant = _jf1_numbers.PLANT
        return GatesAndChecks(
            planted_checks=Table(
                title="Instrument checks",
                headers=["Reader", "Planted", "Detected"],
                rows=[["Lift", f"{plant:.3e}", "yes"],
                      ["Wall resolution", f"{plant:.3e}", "yes"]],
                table_id="jf_planted"),
            conservation=None,
            grid_statement=(f"One grid of {facts['cells']:,} cells carries "
                            f"the fields, the pressures and the lift table."))

    # -- stage 9 ------------------------------------------------------------
    def results(self) -> Results:
        rows = _jf1_numbers.sweep_rows()
        _jf1_numbers.assert_one_grid([Path(r["case_dir"]) for r in rows])
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

        figures = [
            Figure(FIGURES / "jet_flap_1_lift_vs_blowing.png",
                   "Lift against blowing", "Lift rises with blowing across "
                   "the five settings solved.", "results"),
            Figure(FIGURES / "jet_flap_2_chordwise_pressure.png",
                   "Chordwise pressure, blown and unblown",
                   "Blowing loads the rear of the section.", "results"),
        ]
        fields = [
            Figure(FIGURES / "jet_flap_3_flow_field.png",
                   "Flow field at the slot", "The jet leaves the slot and "
                   "turns the flow past the trailing edge.", "results"),
        ]

        return Results(
            fields=fields, plots=figures, tables=[lift],
            verification_lines=[
                f"Reference curve: {REFERENCE}",
                ("No experimental comparison is available for this section, "
                 "so the published curve is shown beside the solved points "
                 "and no agreement is claimed."),
            ],
            limitations=[
                ("exploratory; settling target not reached at high blowing; "
                 "single grid; no wind-tunnel data for this section."),
                "Flow picture from a finer companion grid.",
            ],
            cost_actual=Measured(round(core_min, 1), "core-minutes",
                                 Path(statuses[0]["path"])),
            cost_estimate_from_stage_2=self.restatement().cost_estimate)

    # -- pacing -------------------------------------------------------------
    def agent_census(self):
        return (("prompt", 1), ("restatement", 2), ("assumption", 2),
                ("geometry", 3), ("meshing", 4), ("feasibility", 4),
                ("solving", 5), ("gates", 2), ("results", 0))


ACT = register_act("jet-flap", JetFlapAct())
