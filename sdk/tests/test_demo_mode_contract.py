"""The demo-mode contract's own control: it must SEE a violation, not merely
report a clean sheet.

CLAUDE.md rule 3 is about comparators, and its principle is the reason this
file exists: a checker not shown able to see a non-zero is not evidence. Every
banned phrase Sanaa named is planted here and asserted to raise; every sentence
she herself wrote is asserted to pass. A checker that quietly stopped matching
would fail this file rather than wave an act through on camera.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from workflows.demo_mode import (  # noqa: E402
    DemoContractError, ElapsedClock, GeometryMatch, Measured, SeriesSpec,
    SolveReplay, check_demo_language, check_running_line, assert_screen_safe,
    core_minutes,
)

HERE = Path(__file__).resolve()


# -- her never-list, planted one phrase at a time ---------------------------

BANNED_ON_SCREEN = [
    "The run already finished before this screen opened.",
    "Presenting the solved case now.",
    "Nothing new is solved on this request.",
    "No compute is booked for this request.",
    "The screens come from that run.",
    "Reference body received.",
    "The surface on file is the reference shape.",
    "The uploaded surface is not meshed by this screen.",
    "Two grids were built for this family.",
    "This request re-displayed that run.",
    "This request produced no new solve.",
    "The monitors replay the stored history.",
    "Solver: none on this request.",
    "That value is not recorded in this bundle.",
    "The source case holds the fields.",
    # The instance actually live in this package today, verbatim from
    # workflows.__init__.acknowledge_reference_surface. Her literal never-list
    # string ("not meshed by this screen") would have missed it.
    "The screen itself runs on the parametric family; the uploaded surface is "
    "not meshed or solved by this screen.",
]


@pytest.mark.parametrize("text", BANNED_ON_SCREEN)
def test_banned_phrase_is_seen(text):
    with pytest.raises(DemoContractError):
        check_demo_language(text)


PATHS_ON_SCREEN = [
    "Fields are under /home/ubuntu/Certonomous/verification/runs/JF1_jet_flap.",
    "Read from cases/demo-surfaces/airfoil_blown_slot.stl.",
    "The mesh count came from log.snappyHexMesh.",
    "Written to C:\\runs\\case\\0\\T.",
]


@pytest.mark.parametrize("text", PATHS_ON_SCREEN)
def test_a_path_is_seen(text):
    with pytest.raises(DemoContractError):
        check_demo_language(text)


def test_innocent_slashes_do_not_fire():
    """A checker that fires on prose gets switched off, and a switched-off
    checker is how these strings survived a manual grep."""
    check_demo_language("Lift/drag curves move as the sweep advances.")
    check_demo_language("Meshing a 2D/axisymmetric case takes under a minute.")


def test_her_own_sentences_pass():
    check_demo_language("Solver: OpenFOAM chtMultiRegionSimpleFoam, steady "
                        "conjugate heat transfer.")
    check_demo_language("Instrument checks: three readers each detected a "
                        "planted 0.001 K perturbation.")
    check_demo_language(
        "exploratory; settling target not reached at high blowing; single "
        "grid; no wind-tunnel data for this section.", zone="limitations")


def test_finer_companion_grid_is_limitations_only():
    sentence = "Flow picture from a finer companion grid."
    check_demo_language(sentence, zone="limitations")
    with pytest.raises(DemoContractError):
        check_demo_language(sentence, zone="screen")


# -- tense ------------------------------------------------------------------

def test_progressive_running_lines():
    check_running_line("Meshing", tense="progressive")
    check_running_line("Solving, iteration 4,000 of 20,000", tense="progressive")
    check_running_line("Sweep point 3 of 5", tense="progressive")
    with pytest.raises(DemoContractError):
        check_running_line("The mesh is complete", tense="progressive")


def test_results_lines_are_past_tense():
    check_running_line("Peak core temperature reached 154.2 degrees Celsius.",
                       tense="past")
    with pytest.raises(DemoContractError):
        check_running_line("The solver will report the peak temperature.",
                           tense="past")


# -- internal-only fields ---------------------------------------------------

def test_presentation_flag_cannot_reach_a_payload():
    with pytest.raises(DemoContractError):
        assert_screen_safe({"beat": "results",
                            "presentation_of": "presentation of run JF1"})


def test_a_source_path_cannot_reach_a_payload():
    with pytest.raises(DemoContractError):
        assert_screen_safe({"rows": [{"source": "/home/ubuntu/x/log.simpleFoam"}]})


def test_a_clean_payload_passes():
    assert_screen_safe({"beat": "results", "title": "Temperature field, 305 W",
                        "rows": [["305", "20", "154.2"]]})


# -- the elapsed clock ------------------------------------------------------

def _wall(seconds: float) -> Measured:
    return Measured(seconds, "s", HERE, "measured")


def test_default_clock_is_the_runs_real_wall_time():
    clock = ElapsedClock.real_wall_time(_wall(3601.0))
    assert clock.measured
    assert "60 minutes" in clock.on_screen()


def test_an_override_without_a_basis_is_refused():
    """The hole this closes: a configurable clock that accepts a bare number
    is the mechanism that strips the basis off a figure."""
    with pytest.raises(DemoContractError):
        ElapsedClock(seconds=1200.0, basis="", measured=False)
    with pytest.raises(DemoContractError):
        ElapsedClock(seconds=1200.0, basis="20 minutes", measured=False)


def test_act_d_override_with_its_basis_is_accepted():
    clock = ElapsedClock(
        seconds=1200.0,
        basis=("Runtime of the optimisation itself, on the production "
               "configuration with the linear solvers on GPU."),
        measured=False)
    assert "20 minutes" in clock.on_screen()


def test_cost_is_never_taken_from_an_overridden_clock():
    replay = SolveReplay(
        series=[SeriesSpec(HERE, "residual", "residual", "Momentum residual")],
        wall_seconds=_wall(3601.0), ranks=16, total_iterations=20000,
        elapsed_clock=ElapsedClock(
            seconds=1200.0,
            basis=("Runtime of the optimisation itself, on the production "
                   "configuration with the linear solvers on GPU."),
            measured=False))
    assert replay.core_minutes() == pytest.approx(core_minutes(3601.0, 16))
    assert replay.clock().seconds == 1200.0


# -- geometry ---------------------------------------------------------------

def test_a_rescaled_surface_cannot_render_the_sentence():
    """Measured on Act B: chord 0.991114 served against 1.000000 solved."""
    match = GeometryMatch(
        "chord", Measured(1.000000, "m", HERE), Measured(0.991114, "m", HERE),
        tolerance=1e-4)
    assert not match.agrees()
    assert "0.89% apart" in match.disagreement()


def test_an_agreeing_surface_renders_the_sentence():
    match = GeometryMatch(
        "chord", Measured(1.000000, "m", HERE), Measured(1.000000, "m", HERE),
        tolerance=1e-4)
    assert match.agrees()


# -- the whole contract, end to end -----------------------------------------

def _example_act():
    """The smallest act that satisfies the contract, used as the round-trip
    control. Every artifact it cites is this test file, so the validator's
    file checks have something real to find; a team copies this shape and
    points it at its own run tree."""
    from workflows.demo_mode import (Assumption, DemoAct, Feasibility, Figure,
                                     Geometry, GatesAndChecks, MeshPlan,
                                     Prompt, Restatement, Results, RunRecord,
                                     SERVED_GEOMETRY_DIR, Table)

    stl = SERVED_GEOMETRY_DIR / "example.stl"

    class ExampleAct(DemoAct):
        name = "contract round-trip"

        def run_record(self):
            return RunRecord(
                run_id="X1", run_root=HERE.parent,
                solver="OpenFOAM simpleFoam",
                physics="steady incompressible flow",
                completion_evidence=HERE,
                presentation_of="presentation of run X1",
                record_path=HERE)

        def prompt(self):
            return Prompt("Report lift against blowing for the blown wing.")

        def restatement(self):
            return Restatement(
                "Sweep the jet momentum coefficient and report lift.",
                "Confident: the configuration matches a published family.",
                Measured(480.0, "core-minutes", HERE, "derived"))

        def assumption(self):
            return Assumption("The user assumed the slot stays choked.",
                              "The slot runs subsonic across the sweep.",
                              "Corrected before spending.")

        def geometry(self):
            return Geometry(
                served_stl=stl, display_label="blown wing section",
                matches=[GeometryMatch("chord", Measured(1.0, "m", HERE),
                                       Measured(1.0, "m", HERE), 1e-4)])

        def mesh_plan(self):
            return MeshPlan(command=["blockMesh"], work_dir=HERE.parent,
                            cell_count=Measured(39984, "cells", HERE),
                            resolution_headers=["Region", "First cell height"],
                            resolution_rows=[["Wall", "1.0e-05 m"]],
                            wall_zoom_hint="the wall layers at mid chord",
                            expected_seconds=45.0)

        def feasibility(self):
            return Feasibility("A coarse pass on the unblown section.",
                               Measured(0.31, "", HERE),
                               "The sweep is worth the budget.")

        def solve_replay(self):
            return SolveReplay(
                series=[SeriesSpec(HERE, "residual", "residual",
                                   "Momentum residual")],
                wall_seconds=Measured(3601.0, "s", HERE, "measured"),
                ranks=16, total_iterations=20000, sweep_points=5)

        def gates(self):
            return GatesAndChecks(
                planted_checks=Table("Instrument checks",
                                     ["Reader", "Planted", "Read back"],
                                     [["Lift", "1.234e-03", "1.234e-03"]],
                                     "planted"),
                conservation=None,
                grid_statement="One grid carries the fields and the lift table.")

        def results(self):
            figure = Figure(HERE, "Lift against blowing", "Lift rises with "
                            "blowing across the sweep.", "results")
            return Results(
                fields=[figure], plots=[figure],
                tables=[Table("Lift", ["Blowing", "Lift"], [["0.10", "1.42"]],
                              "lift")],
                verification_lines=["Verified against the published curve "
                                    "within 6 percent."],
                limitations=["exploratory; single grid; no wind-tunnel data "
                             "for this section."],
                cost_actual=Measured(960.3, "core-minutes", HERE, "measured"),
                cost_estimate_from_stage_2=Measured(480.0, "core-minutes",
                                                    HERE, "derived"))

    return ExampleAct(), stl


def test_a_conforming_act_validates(tmp_path, monkeypatch):
    from workflows import demo_mode

    act, stl = _example_act()
    stl.parent.mkdir(parents=True, exist_ok=True)
    created = not stl.exists()
    if created:
        stl.write_text("solid example\nendsolid example\n", encoding="utf-8")
    try:
        assert demo_mode.validate_act(act) == []
    finally:
        if created:
            stl.unlink()


def test_a_generator_side_surface_is_refused():
    """The served copy is not the generated copy: server.py resolves a named
    body under sdk/geometry, while the demo-surface generator writes to
    cases/demo-surfaces. Naming the generator's copy must fail."""
    from workflows import demo_mode

    from workflows.demo_mode import Geometry

    act, _ = _example_act()
    strayed = Geometry(
        served_stl=Path("/home/ubuntu/Certonomous/cases/demo-surfaces/"
                        "airfoil_blown_slot.stl"),
        display_label="blown wing section",
        matches=[GeometryMatch("chord", Measured(1.0, "m", HERE),
                               Measured(1.0, "m", HERE), 1e-4)])
    strayed_act = type("StrayedAct", (type(act),),
                       {"geometry": lambda self: strayed})()
    problems = [p for p in demo_mode.validate_act(strayed_act)
                if "outside the directory the server reads" in p]
    assert problems, "a generator-side surface must be refused"


# -- R5: internal ids are never user-visible --------------------------------

INTERNAL_IDS_ON_SCREEN = [
    "JF1_L1_BLOWN_CMU020_A0",
    "F17c_KV40_FLOOR",
    "M1_kOmegaSST_null__AR_10_Ret_180",
    "T1b_L4",
    "See L-419.",
    "Docket D438 refers.",
    "tier 2 evidence",
    "Tier-3",
    "GATE FAIL on this row",
    "NOT A RESULT",
    "the pre-registration fixed it",
    "Pre-registration frozen.",
]


@pytest.mark.parametrize("text", INTERNAL_IDS_ON_SCREEN)
def test_an_internal_id_is_seen(text):
    """Found by running this checker against the replay stage's REAL payload:
    a case id reaches the screen through the published `labels` list and every
    string-level check passed it. DEMO STANDARD R5 forbids exactly that."""
    with pytest.raises(DemoContractError):
        check_demo_language(text)


ALLOWED_NAMES = [
    "OpenFOAM chtMultiRegionSimpleFoam, steady conjugate heat transfer.",
    "Williams, Butler and Wood, ARC R&M 3304 (1961), eq. 2.",
    "Ansys verification manual VMFL033.",
    "Spence 1956",
    "NACA 0012 section, chord 1.0 m.",
    "305 W and 20 m/s.",
    "39,984 cells.",
    "Verified against the published curve within 6 percent.",
    "Energy conservation checked: closed to 0.4 percent.",
    "Success criteria fixed before running.",
]


@pytest.mark.parametrize("text", ALLOWED_NAMES)
def test_named_sources_are_not_mistaken_for_internal_ids(text):
    """R3 names its reference curves and her header names the solver. A
    checker that ate those would be switched off within the hour."""
    check_demo_language(text)


# -- the geometry check calls its owner, it does not copy its constants -----

def test_geometry_match_pulls_constants_from_the_owning_module():
    from workflows import _jf1_geometry
    from workflows.demo_mode import GeometryMatch as GM

    match = GM.from_module("chord", _jf1_geometry,
                           solved_attr="SOLVED_CHORD_M",
                           tolerance_attr="SOLVED_GEOMETRY_TOL",
                           supplied=_jf1_geometry.SOLVED_CHORD_M,
                           source=HERE, unit="m")
    assert match.agrees()
    assert float(match.solved.value) == _jf1_geometry.SOLVED_CHORD_M
    assert match.tolerance == _jf1_geometry.SOLVED_GEOMETRY_TOL
    assert not match.relative, "the owning module's tolerance is absolute"


def test_the_measured_rescale_still_fails_against_the_owners_tolerance():
    """0.991114 m against a solved 1.0 m at an absolute 1e-06 m."""
    from workflows import _jf1_geometry
    from workflows.demo_mode import GeometryMatch as GM

    match = GM.from_module("chord", _jf1_geometry,
                           solved_attr="SOLVED_CHORD_M",
                           tolerance_attr="SOLVED_GEOMETRY_TOL",
                           supplied=0.991114, source=HERE, unit="m")
    assert not match.agrees()
    assert "tolerance 1e-06" in match.disagreement()


def test_an_absolute_tolerance_is_not_read_as_a_relative_one():
    """1e-06 on a height ratio of 0.005 is 2e-04 relative: two hundred times
    apart. Reading one as the other is its own silent drift."""
    from workflows.demo_mode import GeometryMatch as GM

    args = dict(quantity="slot height ratio",
                solved=Measured(0.005, "", HERE),
                supplied=Measured(0.005045, "", HERE),
                tolerance=1e-06)
    assert not GM(**args, relative=False).agrees()
    assert GM(**args, relative=True).agrees() is False


def test_a_missing_constant_is_refused_not_defaulted():
    from workflows import _jf1_geometry
    from workflows.demo_mode import GeometryMatch as GM

    with pytest.raises(DemoContractError):
        GM.from_module("chord", _jf1_geometry, solved_attr="NO_SUCH_CONSTANT",
                       tolerance_attr="SOLVED_GEOMETRY_TOL", supplied=1.0,
                       source=HERE)
