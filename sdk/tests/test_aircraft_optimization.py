"""Aircraft L/D optimization: requirement parsing, sizing, and routing (#1)."""

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from chief_engineer.router import (AIRCRAFT_OPTIMIZATION, GEOMETRY_STUDY,
                                   apply_surface, classify)
from workflows.aircraft_optimization import (buildup_band_ld, evaluate_design,
                                             grid_spacing_bracket, main,
                                             measure_surface_span,
                                             parse_requirements,
                                             polar_readoff_residual,
                                             screen_solve_gap, seeded_spans)

_TINY_STL = """solid test
 facet normal 0 0 1
  outer loop
   vertex 0 -20 0
   vertex 3 -20 0
   vertex 0 20 0.5
  endloop
 endfacet
endsolid test
"""


class RequirementParsingTests(unittest.TestCase):
    def test_extracts_all_stated_requirements(self):
        reqs = parse_requirements(
            "optimize L/D for 300 passengers, 6000 km range, takeoff 85 m/s, landing 72 m/s")
        self.assertEqual(reqs["passengers"], 300)
        self.assertAlmostEqual(reqs["range_km"], 6000.0)
        self.assertAlmostEqual(reqs["takeoff_speed"], 85.0)
        self.assertAlmostEqual(reqs["landing_speed"], 72.0)
        self.assertTrue(reqs["range_stated"] and reqs["takeoff_stated"])

    def test_missing_requirements_get_flagged_defaults(self):
        reqs = parse_requirements("optimize the lift to drag of this airliner")
        self.assertFalse(reqs["range_stated"])
        self.assertFalse(reqs["passengers_stated"])
        self.assertGreater(reqs["range_km"], 0)   # a default is supplied

    def test_knots_are_converted(self):
        reqs = parse_requirements("landing speed 140 knots for 200 pax")
        self.assertAlmostEqual(reqs["landing_speed"], 140 * 0.514444, places=2)


class SizingModelTests(unittest.TestCase):
    REQS = {"passengers": 300, "range_km": 6000.0, "takeoff_speed": 85.0,
            "landing_speed": 72.0, "passengers_stated": True, "range_stated": True,
            "takeoff_stated": True, "landing_stated": True}

    def test_l_over_d_is_in_a_sane_airliner_band(self):
        r = evaluate_design(58.0, 360.0, 27.5, self.REQS)
        self.assertGreater(r["L_D"], 8)
        self.assertLess(r["L_D"], 30)
        self.assertGreater(r["mtow_kg"], 80_000)   # 300 pax is a heavy jet

    def test_a_tiny_wing_fails_the_landing_speed(self):
        # Small area -> high stall speed -> infeasible on landing.
        r = evaluate_design(64.0, 200.0, 27.5, self.REQS)
        self.assertFalse(r["feasible"])
        self.assertTrue(any("landing" in v or "approach" in v for v in r["violations"]))

    def test_higher_aspect_ratio_raises_l_over_d(self):
        low_ar = evaluate_design(40.0, 360.0, 27.5, self.REQS)["L_D"]
        high_ar = evaluate_design(58.0, 360.0, 27.5, self.REQS)["L_D"]
        self.assertGreater(high_ar, low_ar)


def _disable_pace(test: unittest.TestCase) -> None:
    """Keep CI fast: the on-camera pacing (~120 ms/candidate) is off in tests.

    ``_PACE_S`` is bound at import time, so the env var alone is not enough
    once the module is already loaded — patch the module constant directly."""
    os.environ["CERTONOMOUS_SWEEP_PACE_MS"] = "0"
    from workflows import aircraft_optimization as aopt

    patcher = mock.patch.object(aopt, "_PACE_S", 0.0)
    patcher.start()
    test.addCleanup(patcher.stop)


def _redirect_output(test: unittest.TestCase) -> Path:
    """Every workflow-running test writes into its own temporary output root.

    Root-cause guard for the stale-certificate incident of 2026-07-24: a test
    invoking main() with a directive prompt used to write certificate.pdf and
    transcript.txt into the REAL mission-output tree the control room serves,
    overwriting the artifacts of the owner's own missions. Tests must never
    touch the served tree again. The lessons directory is redirected with it.
    """
    from workflows import aircraft_optimization as aopt

    tmp = Path(tempfile.mkdtemp())
    patcher = mock.patch.object(aopt, "OUT_ROOT", tmp)
    patcher.start()
    test.addCleanup(patcher.stop)
    env = mock.patch.dict(os.environ,
                          {"CERTONOMOUS_LESSONS_DIR": str(tmp / "lessons")})
    env.start()
    test.addCleanup(env.stop)
    test.addCleanup(lambda: shutil.rmtree(tmp, ignore_errors=True))
    return tmp


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        _disable_pace(self)
        _redirect_output(self)

    def test_main_runs_and_reports_a_feasible_optimum(self):
        from workflows import aircraft_optimization as aopt

        events = {}
        verdict = {}
        certificate = {}

        def emit(event, payload):
            events[event] = events.get(event, 0) + 1
            if event == "result.verdict":
                verdict.update(payload)
            if event == "certificate.ready":
                certificate.update(payload)

        # This test asserts the solver-less RESEARCH MODEL path, independent
        # of whether a native VSPAERO happens to be reachable on the host
        # running the suite.
        with mock.patch.object(aopt.vspaero, "available", return_value=False):
            rc = main(request="Optimize the L/D of an airliner for 300 passengers, "
                              "6000 km range, takeoff 85 m/s, landing 72 m/s", emit=emit)
        self.assertEqual(rc, 0)
        self.assertGreater(events.get("landscape.point", 0), 10)
        self.assertEqual(events.get("report.ready"), 1)
        self.assertEqual(verdict.get("tier"), "RESEARCH MODEL")
        self.assertNotEqual(verdict.get("value"), "none")
        # The dispatch panel and the live trace are fed as the grid is screened.
        self.assertGreater(events.get("dispatch.update", 0), 20)
        self.assertGreater(events.get("trace.point", 0), 0)
        # Act 1 carries a Certonomous certificate with its evidence seal. On a
        # solver-less run the finalists are not solved, so the fidelity is the
        # conceptual screen; the seal and human number are still issued.
        self.assertEqual(events.get("certificate.ready"), 1)
        self.assertEqual(certificate.get("dir"), "aircraft-optimization")
        self.assertTrue(certificate.get("certificate_no", "").startswith("C-"))
        self.assertTrue(Path(certificate.get("path", "")).exists())

    def test_stale_api_results_never_crash_and_never_upgrade_the_tier(self):
        # Regression for the stale-result-reuse bug: an api that hands back
        # schema-incomplete results (a stale result.json from a killed run or
        # an older worker) must not crash the finalist processing, and the
        # verdict must stay on the conceptual screen — never claim a solve.
        from unittest import mock

        from workflows import aircraft_optimization as aopt

        class StaleApi:
            def __init__(self, *args, **kwargs):
                pass

            def evaluate(self, design, analyses=()):
                # What the reuse path used to return from a killed run.
                return {"built": {"span": design["span"]}, "stl": "wing.stl",
                        "case_dir": "nowhere", "stl_path": "nowhere/wing.stl"}

        verdict = {}

        def emit(event, payload):
            if event == "result.verdict":
                verdict.update(payload)

        with mock.patch.object(aopt.vspaero, "available", return_value=True), \
                mock.patch.object(aopt.vspaero, "VspAeroWingApi", StaleApi):
            rc = main(request="Optimize the L/D of an airliner for 300 "
                              "passengers, 6000 km range, takeoff 85 m/s, "
                              "landing 72 m/s", emit=emit)
        self.assertEqual(rc, 0)
        self.assertEqual(verdict.get("tier"), "RESEARCH MODEL")

    def test_router_sends_aircraft_ld_prompts_here(self):
        route = classify("optimize the lift-to-drag of this airplane for 250 passengers")
        self.assertEqual(route.intent, AIRCRAFT_OPTIMIZATION)

    # The short demo-day directive: hyphenated "lift-drag", a constraints list,
    # a spoken time budget, and a compute-headroom ask. It must route to the
    # aircraft act and carry BOTH live constraints as params.
    SHORT_DIRECTIVE = (
        "Optimize lift-drag ratio of a twin-aisle airliner with following "
        "constraints: - 300 passengers -6000 km range, take off speed: 85 m/s , "
        "landing speed 72 m/s. Also I want this to be super quick because I am "
        "shooting a demo right now so 2 min at most. I am running locally so "
        "don't use all my workers.")

    def test_short_demo_directive_routes_with_live_constraints(self):
        route = classify(self.SHORT_DIRECTIVE)
        self.assertEqual(route.intent, AIRCRAFT_OPTIMIZATION)
        self.assertEqual(route.params.get("deadline_minutes"), 2.0)
        self.assertTrue(route.params.get("hold_workers_back"))

    def test_short_demo_directive_requirements_parse(self):
        from workflows.aircraft_optimization import parse_requirements
        reqs = parse_requirements(self.SHORT_DIRECTIVE)
        self.assertEqual(reqs["passengers"], 300)
        self.assertEqual(reqs["range_km"], 6000.0)
        self.assertEqual(reqs["takeoff_speed"], 85.0)
        self.assertEqual(reqs["landing_speed"], 72.0)
        self.assertTrue(all(reqs[k] for k in (
            "passengers_stated", "range_stated", "takeoff_stated", "landing_stated")))

    def test_worker_cap_and_time_budget_are_on_the_record(self):
        from workflows.aircraft_optimization import main
        lines = []
        rc = main(request=self.SHORT_DIRECTIVE,
                  params={"deadline_minutes": 2.0, "hold_workers_back": True},
                  emit=lambda e, p: lines.append((e, p)))
        self.assertEqual(rc, 0)
        said = " ".join(p.get("message", "") for e, p in lines
                        if e == "transcript.entry")
        self.assertIn("leave headroom", said)
        self.assertIn("Time budget on the record: 2 minutes", said)


class StartingGeometryTests(unittest.TestCase):
    """An uploaded surface with an airliner prompt: kept on the aircraft
    route, measured for span, and used to seed the search grid."""

    def setUp(self):
        _disable_pace(self)
        _redirect_output(self)

    def test_surface_param_keeps_the_aircraft_route(self):
        route = classify("optimize the lift-to-drag of this airplane "
                         "for 250 passengers")
        route = apply_surface(route, "startwing.stl")
        self.assertEqual(route.intent, AIRCRAFT_OPTIMIZATION)
        self.assertEqual(route.params.get("surface"), "startwing.stl")

    def test_race_prompt_keeps_the_race_route_with_the_surface(self):
        from chief_engineer.router import RACE_COMPARISON
        route = classify("Race a full Monte-Carlo sweep against the "
                         "reduced-order path on the NACA 4412 finite wing: "
                         "same objective, same tolerance, both timed.")
        route = apply_surface(route, "naca4412_wing.stl")
        self.assertEqual(route.intent, RACE_COMPARISON)
        self.assertEqual(route.params.get("surface"), "naca4412_wing.stl")

    def test_surface_still_reroutes_non_optimisation_prompts(self):
        route = apply_surface(classify("how confident are we in the drag "
                                       "number"), "startwing.stl")
        self.assertEqual(route.intent, GEOMETRY_STUDY)
        self.assertEqual(route.params.get("surface"), "startwing.stl")

    def test_span_is_measured_from_a_tiny_synthetic_stl(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "startwing.stl"
            path.write_text(_TINY_STL, encoding="utf-8")
            # Largest horizontal extent: y runs -20..20 -> 40 m.
            self.assertAlmostEqual(measure_surface_span(path), 40.0, places=3)

    def test_unreadable_surface_measures_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.stl"
            path.write_bytes(b"\x00\x01not a surface")
            self.assertIsNone(measure_surface_span(path))
        self.assertIsNone(measure_surface_span(Path("does-not-exist.stl")))

    def test_seeded_spans_bracket_the_measurement_within_clamps(self):
        spans = seeded_spans(40.0)
        self.assertTrue(any(s < 40.0 for s in spans))
        self.assertTrue(any(s > 40.0 for s in spans))
        self.assertTrue(all(28.0 <= s <= 68.0 for s in spans))
        # An extreme measurement is clamped to sane airliner bounds.
        wide = seeded_spans(200.0)
        self.assertTrue(all(s <= 68.0 for s in wide))
        narrow = seeded_spans(5.0)
        self.assertTrue(all(s >= 28.0 for s in narrow))

    def test_workflow_acknowledges_and_seeds_from_the_uploaded_surface(self):
        from workflows import aircraft_optimization as aopt

        events = []
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "startwing.stl").write_text(_TINY_STL, encoding="utf-8")
            with mock.patch.object(aopt, "_GEOMETRY_DIR", Path(tmp)):
                rc = aopt.main(
                    request="Optimize the L/D of an airliner for 300 passengers, "
                            "6000 km range, takeoff 85 m/s, landing 72 m/s",
                    params={"surface": "startwing.stl"},
                    emit=lambda e, p: events.append((e, p)))
        self.assertEqual(rc, 0)
        said = " ".join(p.get("message", "") for e, p in events
                        if e == "transcript.entry")
        self.assertIn("Starting geometry received: Startwing", said)
        self.assertIn("Measured span about 40 m; the search brackets it", said)
        # No raw filename on camera.
        self.assertNotIn("startwing.stl", said)
        # The uploaded surface shows in the geometry viewport via the same
        # display path the geometry study uses.
        geo = [p for e, p in events if e == "geometry.ready"]
        self.assertTrue(any("name=startwing.stl" in (p.get("url") or "")
                            for p in geo))
        # The screened grid is re-centred on the measured span.
        spans = sorted({p["design"]["span"] for e, p in events
                        if e == "landscape.point" and "design" in p})
        expected = sorted(seeded_spans(40.0))
        self.assertEqual(spans, expected)

    def test_unparseable_surface_stays_on_file_with_default_bounds(self):
        from workflows import aircraft_optimization as aopt

        events = []
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "blob.stl").write_bytes(b"\x00\x01not a surface")
            with mock.patch.object(aopt, "_GEOMETRY_DIR", Path(tmp)):
                rc = aopt.main(
                    request="Optimize the L/D of an airliner for 300 passengers, "
                            "6000 km range, takeoff 85 m/s, landing 72 m/s",
                    params={"surface": "blob.stl"},
                    emit=lambda e, p: events.append((e, p)))
        self.assertEqual(rc, 0)
        said = " ".join(p.get("message", "") for e, p in events
                        if e == "transcript.entry")
        self.assertIn("on file as the reference shape", said)
        spans = sorted({p["design"]["span"] for e, p in events
                        if e == "landscape.point" and "design" in p})
        self.assertEqual(spans, [34.0, 40.0, 46.0, 52.0, 58.0, 64.0, 68.0])


class ScopeStatementTests(unittest.TestCase):
    """Section 1: a wing arrives, the objective names an aircraft, and the
    act opens by saying what it is doing with the gap."""

    REQUEST = ("Optimize the L/D of an airliner for 300 passengers, "
               "6000 km range, takeoff 85 m/s, landing 72 m/s")

    def setUp(self):
        _disable_pace(self)
        _redirect_output(self)

    def _run(self, request=None, surface=None, geometry_dir=None):
        from workflows import aircraft_optimization as aopt

        events = []
        ctx = [mock.patch.object(aopt.vspaero, "available", return_value=False)]
        if geometry_dir is not None:
            ctx.append(mock.patch.object(aopt, "_GEOMETRY_DIR", geometry_dir))
        with ctx[0]:
            if len(ctx) > 1:
                ctx[1].start()
                self.addCleanup(ctx[1].stop)
            rc = aopt.main(request=request or self.REQUEST,
                           params=({"surface": surface} if surface else {}),
                           emit=lambda e, p: events.append((e, p)))
        self.assertEqual(rc, 0)
        return events

    @staticmethod
    def _digest_lines(events):
        """The entries the control room shows in the digest: bulleted or
        keyword-bearing narration, never the system echo of the request."""
        return [p.get("message", "") for e, p in events
                if e == "transcript.entry"
                and (p.get("role") or "") != "SYSTEM"]

    def test_detector_separates_a_wing_from_a_configuration(self):
        from workflows.aircraft_optimization import (is_lifting_surface_only,
                                                     surface_bodies)

        wing = surface_bodies(
            Path(__file__).resolve().parents[1] / "geometry"
            / "airliner_wing_span52.stl")
        self.assertEqual(wing["bodies"], 1)
        self.assertTrue(is_lifting_surface_only(wing))
        body = surface_bodies(
            Path(__file__).resolve().parents[1] / "geometry"
            / "crm_wingbody.stl")
        # A wing-body carries a fuselage, so it is not a lifting surface only.
        self.assertFalse(is_lifting_surface_only(body))
        self.assertFalse(is_lifting_surface_only(None))

    def test_scope_statement_is_the_first_digest_line_when_triggered(self):
        events = self._run(surface="airliner_wing_span52.stl")
        first = self._digest_lines(events)[0]
        self.assertIn("Geometry received is a wing only", first)
        self.assertIn("Treating this as wing design for the stated aircraft",
                      first)
        self.assertIn("Fuselage, tail, and nacelle drag are added from "
                      "Raymer's component buildup method", first)
        self.assertIn("All L/D figures quoted are whole-aircraft", first)
        # The ambiguity clause rides the same entry as one clause.
        self.assertIn("geometry and objective scope mismatch resolved as "
                      "above", first)
        self.assertRegex(first, r"Interpretation confidence \d+%")

    def test_no_scope_statement_without_an_uploaded_wing(self):
        said = " ".join(self._digest_lines(self._run()))
        self.assertNotIn("Geometry received is a wing only", said)

    def test_no_scope_statement_when_the_objective_names_no_aircraft(self):
        said = " ".join(self._digest_lines(self._run(
            request="Maximise the lift to drag of this wing for 300 "
                    "passengers, 6000 km range",
            surface="airliner_wing_span52.stl")))
        self.assertNotIn("Geometry received is a wing only", said)

    def test_no_scope_statement_when_the_upload_carries_a_body(self):
        said = " ".join(self._digest_lines(
            self._run(surface="crm_wingbody.stl")))
        self.assertNotIn("Geometry received is a wing only", said)


class AssumedValuesLedgerTests(unittest.TestCase):
    """The ledger sections 3 and 5 read: unstated requirements, the low-speed
    lift coefficients, and the non-wing drag share."""

    def test_clmax_rows_are_always_present_and_marked(self):
        from workflows.aircraft_optimization import (assumed_values,
                                                     parse_requirements)

        rows = assumed_values(parse_requirements(
            "Optimize the L/D of an airliner for 300 passengers, 6000 km "
            "range, takeoff 85 m/s, landing 72 m/s"))
        table = {label: (value, basis) for label, value, basis in rows}
        self.assertEqual(table["CLmax, take-off"][1],
                         "assumed, not solver-derived")
        self.assertEqual(table["CLmax, landing"][1],
                         "assumed, not solver-derived")
        self.assertIn("Raymer", table["Non-wing drag share"][1])
        # Every requirement was stated, so none of them is in the ledger.
        self.assertNotIn("Passengers", table)
        self.assertNotIn("Range requirement", table)

    def test_unstated_requirements_join_the_ledger(self):
        from workflows.aircraft_optimization import (assumed_values,
                                                     parse_requirements)

        rows = assumed_values(parse_requirements(
            "Optimize the lift to drag of this airliner"))
        labels = [label for label, _value, _basis in rows]
        for label in ("Passengers", "Range requirement",
                      "Take-off speed limit", "Landing speed limit"):
            self.assertIn(label, labels)


class _SolvedApi:
    """A stand-in for VspAeroWingApi returning complete solved results."""

    ELAPSED: float | None = None
    REUSED = False

    def __init__(self, *args, **kwargs):
        pass

    def evaluate(self, design, analyses=()):
        result = {
            "polar": {"CLtot": [0.1, 0.5, 0.9],
                      "CDi": [0.002, 0.004, 0.008],
                      "CDo": [0.0055, 0.0056, 0.0058]},
            "matched": {"alpha": 3.9, "cl": design.get("cl_target"),
                        "cdi": 0.0023, "cdo_wing": 0.0055,
                        "extrapolated": False},
            "stl": "wing.stl", "stl_path": "nowhere/wing.stl",
            "case_dir": "nowhere", "solver_version": "VSPAERO 3.x",
        }
        if self.ELAPSED is not None:
            result["elapsed_s"] = self.ELAPSED
        if self.REUSED:
            result["reused_prior"] = True
        return result


class TranscriptTableTests(unittest.TestCase):
    REQUEST = ("Optimize the L/D of an airliner for 300 passengers, "
               "6000 km range, takeoff 85 m/s, landing 72 m/s")

    def setUp(self):
        _disable_pace(self)
        _redirect_output(self)

    def _run(self, api=None):
        from workflows import aircraft_optimization as aopt

        events = []
        emit = lambda e, p: events.append((e, p))
        if api is None:
            # The solver-less path: mocked False independent of whatever
            # VSPAERO happens to be reachable on the host running the suite.
            with mock.patch.object(aopt.vspaero, "available",
                                   return_value=False):
                rc = aopt.main(request=self.REQUEST, emit=emit)
        else:
            with mock.patch.object(aopt.vspaero, "available",
                                   return_value=True), \
                    mock.patch.object(aopt.vspaero, "VspAeroWingApi", api):
                rc = aopt.main(request=self.REQUEST, emit=emit)
        self.assertEqual(rc, 0)
        return events

    @staticmethod
    def _said(events):
        return " ".join(p.get("message", "") for e, p in events
                        if e == "transcript.entry")

    def test_screened_optimum_table_lands_in_the_solver_less_path(self):
        events = self._run()
        tables = [p for e, p in events if e == "transcript.table"]
        screened = [p for p in tables if p["table_id"] == "screened-optimum"]
        self.assertEqual(len(screened), 1)
        self.assertEqual(screened[0]["headers"],
                         ["Best Screened", "Span", "AR", "MTOW", "Range",
                          "Approach Speed", "Whole-aircraft L/D"])
        # The screen tier is named in the table's own title, so a screened
        # number can never be read as a solved one.
        self.assertIn("[screen: reduced-order sizing]", screened[0]["title"])
        self.assertEqual(len(screened[0]["rows"]), 1)
        self.assertTrue(screened[0]["rows"][0][0].startswith("Rank 1"))
        # Finalists are not solved on this path, so no finalist table exists.
        self.assertFalse([p for p in tables
                          if p["table_id"] == "finalist-solves"])
        # The old prose line is gone from the transcript.
        self.assertNotIn("Best screened:", self._said(events))

    def test_finalist_rows_land_live_and_vspaero_is_named(self):
        events = self._run(api=_SolvedApi)
        tables = [p for e, p in events if e == "transcript.table"]
        self.assertTrue([p for p in tables
                         if p["table_id"] == "screened-optimum"])
        finalist = [p for p in tables if p["table_id"] == "finalist-solves"]
        headers = [p for p in finalist if not p["append"]]
        rows = [row for p in finalist if p["append"] for row in p["rows"]]
        self.assertEqual(len(headers), 1)
        self.assertEqual(headers[0]["headers"],
                         ["Span", "Alpha", "CDi", "Wing Viscous",
                          "Whole-aircraft L/D"])
        # The finalist table is solve tier only, and says so.
        self.assertIn("[solve: VSPAERO + Raymer buildup]", headers[0]["title"])
        self.assertEqual(len(rows), 9)   # one row per finalist solve
        said = self._said(events)
        self.assertIn("Solver of choice: VSPAERO", said)
        self.assertNotIn("Each is actual geometry", said)
        # The per-finalist prose entries are replaced by the table.
        self.assertNotIn("Solved span", said)
        report = [p for e, p in events if e == "report.ready"][0]
        self.assertTrue(any(
            "solved with VSPAERO, a vortex-lattice method" in m
            for m in report["methods"]))
        verdict = [p for e, p in events if e == "result.verdict"][0]
        self.assertEqual(verdict.get("tier"), "SOLVER-BACKED")
        self.assertIn("wing solved with VSPAERO", verdict.get("reason", ""))

    def test_instant_batches_never_report_a_zero_second_wall(self):
        # Mocked solves return instantly with no elapsed_s: the honest report
        # names the wings and slots and omits the time clause entirely.
        said = self._said(self._run(api=_SolvedApi))
        self.assertIn("Finalist solves:", said)
        self.assertNotIn("0.0 s", said)

    def test_warm_reuse_reports_the_stamped_parallel_wall_estimate(self):
        calls = []

        class WarmApi(_SolvedApi):
            REUSED = True

            def evaluate(self, design, analyses=()):
                # Thread-safe under the GIL: at least one caller reads an
                # empty list and stamps the 84.0 s first-run duration.
                result = _SolvedApi.evaluate(self, design, analyses)
                first = not calls
                calls.append(1)
                result["elapsed_s"] = 84.0 if first else 12.3
                return result

        said = self._said(self._run(api=WarmApi))
        # max(per-wing elapsed_s) is the parallel wall estimate.
        self.assertIn("Finalist solves: 84.0 s wall", said)

    def test_warm_reuse_without_stamps_omits_the_time_clause(self):
        class LegacyWarmApi(_SolvedApi):
            REUSED = True
            ELAPSED = None

        said = self._said(self._run(api=LegacyWarmApi))
        self.assertIn("Finalist solves:", said)
        self.assertNotIn("s wall", said)
        self.assertNotIn("0.0 s", said)


class ComputedUncertaintyHelperTests(unittest.TestCase):
    """The doctrine's computed-channel helpers on synthetic finalist data."""

    STEPS = {"span": 6.0, "area": 60.0, "sweep_deg": 5.0}

    def test_grid_bracket_recovers_a_known_quadratic(self):
        def value(span, area):
            return 20.0 - 0.01 * (span - 58.0) ** 2 - 1e-4 * (area - 300.0) ** 2

        points = [{"span": s, "area": 300.0, "sweep_deg": 25.0,
                   "L_D_solved": value(s, 300.0)} for s in (52.0, 58.0, 64.0)]
        points += [{"span": 58.0, "area": a, "sweep_deg": 25.0,
                    "L_D_solved": value(58.0, a)} for a in (240.0, 360.0)]
        winner = {"span": 58.0, "area": 300.0, "sweep_deg": 25.0}
        out = grid_spacing_bracket(points, winner, self.STEPS)
        # Half-step deltas of the known quadratics: 0.01·3² and 1e-4·30².
        self.assertAlmostEqual(out["axes"]["span"], 0.09, places=6)
        self.assertAlmostEqual(out["axes"]["area"], 0.09, places=6)
        self.assertIsNone(out["axes"]["sweep_deg"])   # no variation in the data
        self.assertAlmostEqual(out["value"], (2 * 0.09 ** 2) ** 0.5, places=6)

    def test_two_point_axis_uses_the_straight_slope(self):
        points = [
            {"span": 58.0, "area": 300.0, "sweep_deg": 25.0, "L_D_solved": 20.0},
            {"span": 58.0, "area": 360.0, "sweep_deg": 25.0, "L_D_solved": 18.8},
        ]
        out = grid_spacing_bracket(points, points[0], self.STEPS)
        # |slope| = 1.2 / 60 per m²; half step 30 m² -> 0.6.
        self.assertAlmostEqual(out["axes"]["area"], 0.6, places=6)

    def test_lone_winner_returns_none_rather_than_a_guess(self):
        points = [{"span": 58.0, "area": 300.0, "sweep_deg": 25.0,
                   "L_D_solved": 20.0}]
        out = grid_spacing_bracket(points, points[0], self.STEPS)
        self.assertIsNone(out["value"])

    def test_buildup_band_matches_direct_computation(self):
        cl, cdo, cdi, cd0 = 0.478, 0.006014, 0.004889, 0.013
        ld0 = cl / (cd0 + cdo + cdi)
        ld_hi = cl / (0.85 * cd0 + cdo + cdi)
        ld_lo = cl / (1.15 * cd0 + cdo + cdi)
        expected = max(abs(ld_hi - ld0), abs(ld0 - ld_lo))
        self.assertAlmostEqual(buildup_band_ld(cl, cdo, cdi), expected, places=9)
        self.assertGreater(buildup_band_ld(cl, cdo, cdi), 0.0)

    def test_screen_gap_is_the_mean_absolute_delta(self):
        finalists = [{"L_D": 18.0, "L_D_solved": 20.0},
                     {"L_D": 19.0, "L_D_solved": 18.5}]
        self.assertAlmostEqual(screen_solve_gap(finalists), 1.25, places=9)
        self.assertIsNone(screen_solve_gap([]))

    def test_polar_readoff_residual_is_computed_not_invented(self):
        polar = {"CLtot": [0.1, 0.5, 0.9],
                 "CDi": [0.002, 0.004, 0.008],
                 "CDo": [0.0055, 0.0056, 0.0058]}
        # The polar curves, so a straight read and a curved read differ.
        self.assertGreater(polar_readoff_residual(polar, 0.3), 0.0)
        # A polar that cannot support the comparison contributes zero.
        self.assertEqual(polar_readoff_residual({}, 0.3), 0.0)
        self.assertEqual(polar_readoff_residual(None, 0.3), 0.0)


class SolvedRunDoctrineTests(unittest.TestCase):
    """A solved run quantifies all three channels, speaks the cleared
    capability wording, and issues a structured, honestly-labelled page."""

    REQUEST = ("Optimize the L/D of an airliner for 300 passengers, "
               "6000 km range, takeoff 85 m/s, landing 72 m/s")
    BANNED = ("demo", "stored", "saved", "cached", "recorded",
              "pre-computed", "trend")

    def setUp(self):
        _disable_pace(self)
        self.out_root = _redirect_output(self)

    def _run_solved(self):
        from workflows import aircraft_optimization as aopt

        events = []
        with mock.patch.object(aopt.vspaero, "available", return_value=True), \
                mock.patch.object(aopt.vspaero, "VspAeroWingApi", _SolvedApi):
            rc = aopt.main(request=self.REQUEST,
                           emit=lambda e, p: events.append((e, p)))
        self.assertEqual(rc, 0)
        return events

    @staticmethod
    def _messages(events):
        return [p.get("message", "") for e, p in events
                if e == "transcript.entry"]

    def test_all_three_channels_quantified_when_solves_ran(self):
        events = self._run_solved()
        channels = [p for e, p in events
                    if e == "uncertainty.channels"][0]["channels"]
        self.assertEqual([c["name"] for c in channels],
                         ["input", "numerical", "model"])
        for channel in channels:
            self.assertTrue(channel["quantified"], channel)
            self.assertIsNotNone(channel["value"], channel)
            self.assertNotIn("not quantified", channel["note"])
        model = channels[2]
        self.assertIn("Component buildup band on non-wing drag", model["note"])
        self.assertIn("Raymer", model["note"])
        self.assertIn("solved wings averages", model["note"])
        numerical = channels[1]
        # Katie's rule: channel notes never name the exact method.
        self.assertIn("Default numerical consistency method", numerical["note"])
        self.assertNotIn("quadratic fit", numerical["note"])
        self.assertNotIn("Monte-Carlo", channels[0]["note"])
        self.assertIn("Ensemble run", channels[0]["note"])

    def test_certificate_names_the_solver_and_carries_no_unquantified_row(self):
        events = self._run_solved()
        cert = [p for e, p in events if e == "certificate.ready"][0]
        text = Path(cert["path"]).read_bytes().decode("latin-1")
        self.assertIn("VSPAERO vortex lattice", text)
        self.assertIn("research sizing screen", text)
        self.assertNotIn("Research drag-polar sizing model", text)
        self.assertNotIn("not quantified", text)
        # Objective is this run's verbatim request.
        self.assertIn("300 passengers,", text)
        # Structured result table with Title Case labels and units.
        for token in ("Parameter", "Span", "AR", "MTOW", "Range",
                      "Approach Speed", "L/D"):
            self.assertIn(token, text)

    def test_certificate_states_its_scope_constraints_and_assumed_values(self):
        events = self._run_solved()
        cert = [p for e, p in events if e == "certificate.ready"][0]
        text = Path(cert["path"]).read_bytes().decode("latin-1")
        # The scope is a labelled field, read with the objective it qualifies.
        self.assertIn("(Scope)", text)
        self.assertIn("Result is whole-aircraft L/D.", text)
        # Every constraint says where it came from.
        self.assertIn("(Constraints)", text)
        self.assertIn("user-stated", text)
        self.assertIn("Structural span limit", text)
        # The assumed-values ledger carries the lift coefficients the low
        # speed verdicts turn on, marked as no solver's work.
        self.assertIn("(Assumed Values)", text)
        self.assertIn("CLmax, landing", text)
        self.assertIn("assumed, not solver-derived", text)
        # Issuance and the seal sit together at the foot.
        self.assertLess(text.index("(Result)"), text.index("(Issued"))

    def test_wording_is_the_cleared_capability_statement(self):
        events = self._run_solved()
        said = " ".join(self._messages(events))
        self.assertIn("Wing solved with VSPAERO: induced and viscous drag "
                      "from the solved polar at cruise", said)
        self.assertIn("Non-wing drag comes from the component buildup method "
                      "(Raymer)", said)
        self.assertIn("the pipeline itself is ready", said)
        self.assertNotIn("The solver moved the pick", said)
        self.assertNotIn("the screen had it wrong", said)
        self.assertNotIn("not yet solved", said)
        self.assertNotIn("would close that gap", said)
        verdict = [p for e, p in events if e == "result.verdict"][0]
        self.assertIn("Raymer's component buildup method",
                      verdict.get("reason", ""))

    def test_no_banned_strings_and_bullets_start_capitalized(self):
        events = self._run_solved()
        surfaces = list(self._messages(events))
        for e, p in events:
            if e == "uncertainty.channels":
                surfaces += [c.get("note", "") for c in p["channels"]]
            if e == "report.ready":
                surfaces += list(p.get("methods", []))
                surfaces += list(p.get("abstract", []))
                surfaces += list(p.get("uncertainty", []))
        blob = " ".join(surfaces)
        import re
        for word in self.BANNED:
            self.assertIsNone(re.search(rf"\b{word}\b", blob, re.I), word)
        for glyph in ("—", "→", "--"):
            self.assertNotIn(glyph, blob)
        for message in self._messages(events):
            for bullet in message.split("•")[1:]:
                bullet = bullet.strip()
                if bullet:
                    self.assertFalse(bullet[0].islower(), message)

    def test_lesson_records_the_computed_uncertainty_patterns(self):
        from chief_engineer.lessons import learned_lessons

        self._run_solved()
        lessons = {item["mission_id"]: item["text"]
                   for item in learned_lessons()}
        self.assertIn("computed-uncertainty-patterns", lessons)
        text = lessons["computed-uncertainty-patterns"]
        self.assertIn("quadratic fit", text)
        self.assertIn("half-step", text)
        self.assertIn("Screen-vs-solve discrepancy", text)


class StaleCertificateRegressionTests(unittest.TestCase):
    """The served page always belongs to the newest completed run."""

    BASE = ("Optimize the L/D of an airliner for 300 passengers, 6000 km "
            "range, takeoff 85 m/s, landing 72 m/s.")

    def setUp(self):
        _disable_pace(self)
        self.out_root = _redirect_output(self)
        self.pdf = self.out_root / "aircraft-optimization" / "certificate.pdf"

    def _run(self, request, events=None):
        from workflows import aircraft_optimization as aopt

        with mock.patch.object(aopt.vspaero, "available", return_value=False):
            rc = aopt.main(request=request,
                           emit=(None if events is None
                                 else lambda e, p: events.append((e, p))))
        self.assertEqual(rc, 0)

    def test_second_run_replaces_the_served_pdf_with_its_own_request(self):
        self._run(self.BASE + " Fleet name Aquila.")
        first = self.pdf.read_bytes().decode("latin-1")
        self.assertIn("Aquila", first)
        self._run(self.BASE + " Fleet name Borealis.")
        second = self.pdf.read_bytes().decode("latin-1")
        self.assertIn("Borealis", second)
        self.assertNotIn("Aquila", second)
        # Atomic swap leaves no staging file behind in the served directory.
        leftovers = [p.name for p in self.pdf.parent.iterdir()
                     if p.suffix not in {".pdf", ".txt", ".stl"}]
        self.assertEqual(leftovers, [])

    def test_failed_generation_withdraws_the_previous_page_and_says_so(self):
        self._run(self.BASE)
        self.assertTrue(self.pdf.exists())
        events = []
        with mock.patch("chief_engineer.certificate.build_certificate_v2",
                        side_effect=RuntimeError("boom")):
            self._run(self.BASE + " Second pass.", events)
        self.assertFalse(self.pdf.exists())
        self.assertFalse([p for e, p in events if e == "certificate.ready"])
        said = " ".join(p.get("message", "") for e, p in events
                        if e == "transcript.entry")
        self.assertIn("No certificate could be issued for this run", said)
        self.assertIn("withdrawn", said)


if __name__ == "__main__":
    unittest.main()
