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
                                             range_for_ld, screen_solve_gap,
                                             seeded_spans, unresolved_family)

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
        # The compliance decision is a required output, and it is numeric:
        # the slot counts land as a table, not as a sentence to parse.
        headroom = [p for e, p in lines if e == "transcript.table"
                    and p["table_id"] == "worker-headroom"]
        self.assertEqual(len(headroom), 1)
        self.assertEqual(headroom[0]["headers"], ["Slots", "Count"])
        counts = {row[0]: int(row[1]) for row in headroom[0]["rows"]}
        self.assertEqual(sorted(counts), ["Available", "Held back", "Taken"])
        self.assertEqual(counts["Taken"] + counts["Held back"],
                         counts["Available"])
        self.assertGreater(counts["Held back"], 0)


class ComputeLedgerAgreementTests(unittest.TestCase):
    """The compute panel shows one measurement twice; it must read the same.

    Filmed 2026-08-01: the KPI read "Core-min spent 0.03" and the note under
    it read "spent 0.0 core-min - 9 VSPAERO wing solves", on the same screen.
    Nine solver runs happened, so the 0.0 was the wrong one: the note carried
    one decimal where the totals carry two.
    """

    def test_a_spend_reads_the_same_in_the_note_and_the_total(self):
        from chief_engineer.lab import ComputeLedger

        ledger = ComputeLedger()
        ledger.spend(1.8, "9 VSPAERO wing solves")
        total = ledger.as_dict()["spent_core_minutes"]
        self.assertEqual(total, 0.03)
        self.assertIn(f"spent {total} core-min", ledger.notes[-1])
        self.assertNotIn("spent 0.0 core-min", ledger.notes[-1])

    def test_a_larger_spend_still_reads_at_one_decimal(self):
        from chief_engineer.lab import ComputeLedger

        ledger = ComputeLedger()
        ledger.spend(750.0, "a long solve")
        self.assertIn("spent 12.5 core-min", ledger.notes[-1])

    def test_nothing_measured_still_reads_zero(self):
        # Too small to see is not the same as nothing spent.
        from chief_engineer.lab import ComputeLedger

        ledger = ComputeLedger()
        ledger.spend(0.0, "no solves")
        self.assertIn("spent 0.0 core-min", ledger.notes[-1])


class GateCodeAdvisoryTests(unittest.TestCase):
    """ICAO Annex 14 Volume I, aerodrome reference code, code element 2.

    The bands are wingspan only and the bounds read "up to but not including",
    so a span of exactly 65 m is already Code F. Both of those are easy to get
    wrong and an engineer in the audience will know the table."""

    def setUp(self):
        _disable_pace(self)
        _redirect_output(self)

    def test_the_bands_are_the_published_ones(self):
        from workflows.aircraft_optimization import icao_code_letter
        self.assertEqual(icao_code_letter(36.0), "D")
        self.assertEqual(icao_code_letter(51.9), "D")
        self.assertEqual(icao_code_letter(52.0), "E")
        self.assertEqual(icao_code_letter(64.9), "E")
        self.assertEqual(icao_code_letter(65.0), "F")
        self.assertEqual(icao_code_letter(79.9), "F")

    def test_the_upper_bound_of_each_band_is_exclusive(self):
        # "52 m up to but not including 65 m" is Code E, so 65.0 is Code F and
        # a 65 m span already trips the advisory.
        from workflows.aircraft_optimization import spans_over_code_e
        self.assertEqual(spans_over_code_e([64.99]), [])
        self.assertEqual(spans_over_code_e([65.0]), [65.0])
        self.assertEqual(spans_over_code_e([52, 64, 65, 68]), [65.0, 68.0])

    def test_the_advisory_never_rules_a_design_infeasible(self):
        # A span past Code E is still a buildable, feasible wing: the gate code
        # is advisory and never enters the violation list. The area is found
        # rather than typed, because the smallest wing that clears the stated
        # low-speed limits moves with the payload calibration and a literal
        # here would make this read as a gate failure the next time it does.
        from workflows.aircraft_optimization import (_ICAO_CODE_E_MAX_SPAN,
                                                     evaluate_design,
                                                     parse_requirements)
        reqs = parse_requirements("300 passengers, 6000 km range")
        self.assertGreater(68.0, _ICAO_CODE_E_MAX_SPAN)
        wide = next((d for d in (evaluate_design(68.0, float(a), 25.0, reqs)
                                 for a in range(240, 801, 5)) if d["feasible"]),
                    None)
        self.assertIsNotNone(wide, "no feasible wing at a Code F span")
        self.assertFalse([v for v in wide["violations"] if "gate" in v.lower()])

    def test_the_advisory_and_its_offer_reach_the_digest(self):
        events = []
        main(request="Optimize the L/D of an airliner for 300 passengers, "
                     "6000 km range",
             emit=lambda e, p: events.append((e, p)))
        said = " ".join(p.get("message", "") for e, p in events
                        if e == "transcript.entry")
        self.assertIn("ICAO Aerodrome Reference Code E", said)
        self.assertIn("52 to 65 m", said)
        self.assertIn("65 to 80 m", said)
        self.assertIn("Code F", said)
        self.assertIn("Offer: re-run with span at most 65 m", said)

    def test_the_constraint_list_tags_every_row_and_disposes_the_advisory(self):
        from workflows.aircraft_optimization import (constraint_list,
                                                     parse_requirements)
        reqs = parse_requirements("300 passengers, 6000 km range")
        rows = constraint_list(reqs, advisory=True, winner_span=68.0)
        tags = {name: tag for name, _value, tag in rows}
        self.assertEqual(tags["Passengers"], "user-stated")
        self.assertEqual(tags["Range"], "user-stated")
        self.assertEqual(tags["Landing speed"], "assumed")
        self.assertEqual(tags["ICAO gate code"], "advisory, re-run offer open")
        inside = constraint_list(reqs, advisory=True, winner_span=60.0)
        self.assertEqual(dict((n, t) for n, _v, t in inside)["ICAO gate code"],
                         "advisory, winner inside Code E")
        # No advisory raised means no advisory row.
        quiet = constraint_list(reqs, advisory=False)
        self.assertNotIn("ICAO gate code", [n for n, _v, _t in quiet])


class AnalogueCheckTests(unittest.TestCase):
    """The winner held against real aircraft built for the same mission.

    Advisory only: it blocks nothing and changes no number. Every analogue
    figure is a published one, so the guard here is that nothing is invented
    and that a parameter nobody publishes is reported as such rather than
    quietly dropped."""

    def setUp(self):
        _disable_pace(self)
        _redirect_output(self)

    def test_analogues_must_match_on_passengers_and_on_range(self):
        from workflows.aircraft_optimization import (analogues_for,
                                                     parse_requirements)
        picked = analogues_for(parse_requirements(
            "300 passengers, 6000 km range"))
        names = {a["name"] for a in picked}
        self.assertEqual(names, {"Airbus A300-600R", "Boeing 767-300"})
        # The A330-300 seats exactly 300 and is still not an analogue: at
        # 11750 km it is built for a different mission.
        self.assertNotIn("Airbus A330-300", names)
        # The 777-200 is inside the range band and outside the seat band.
        self.assertNotIn("Boeing 777-200", names)

    def test_no_analogue_is_offered_for_a_mission_nobody_builds(self):
        from workflows.aircraft_optimization import (analogues_for,
                                                     parse_requirements)
        self.assertEqual(
            analogues_for(parse_requirements("900 passengers, 2000 km range")),
            [])

    def test_a_parameter_nobody_publishes_is_reported_as_such(self):
        from workflows.aircraft_optimization import (analogue_rows,
                                                     analogues_for,
                                                     parse_requirements)
        reqs = parse_requirements("300 passengers, 6000 km range")
        rows = analogue_rows(
            {"span": 46.0, "area": 283.4, "aspect_ratio": 7.99,
             "mtow_kg": 160000.0},
            analogues_for(reqs))
        table = {row[0]: row for row in rows}
        # Four parameters, always, whatever is published.
        self.assertEqual(list(table), ["Span", "Wing area", "Aspect ratio",
                                       "MTOW"])
        self.assertEqual(table["Span"][3], "within analogue envelope")
        self.assertEqual(table["MTOW"][3], "within analogue envelope")

    def test_an_outlier_names_its_direction_and_points_at_the_advisory(self):
        from workflows.aircraft_optimization import (analogue_rows,
                                                     analogues_for,
                                                     parse_requirements)
        reqs = parse_requirements("300 passengers, 6000 km range")
        rows = analogue_rows(
            {"span": 68.0, "area": 300.0, "aspect_ratio": 15.4,
             "mtow_kg": 147000.0},
            analogues_for(reqs))
        table = {row[0]: row for row in rows}
        self.assertIn("outlier, above", table["Span"][3])
        self.assertIn("gate code advisory", table["Span"][3])
        self.assertIn("outlier, below", table["MTOW"][3])

    def test_a_winner_inside_code_e_points_at_the_finding_not_an_advisory(self):
        # The conclusion raises an ADVISORY only for a Code F span; a winner
        # inside Code E gets the finding that nothing needs to change. The
        # span row used to point at "gate code advisory" either way, so a
        # winner that had come inside the band sent the reader looking for an
        # advisory the run never raised.
        from workflows.aircraft_optimization import (analogue_rows,
                                                     analogues_for,
                                                     parse_requirements)
        reqs = parse_requirements("300 passengers, 6000 km range")
        rows = analogue_rows(
            {"span": 61.0, "area": 360.0, "aspect_ratio": 10.3,
             "mtow_kg": 199000.0},
            analogues_for(reqs))
        span = {row[0]: row for row in rows}["Span"][3]
        self.assertIn("gate code finding", span)
        self.assertNotIn("advisory", span)

    def test_the_payload_fraction_is_measured_on_the_analogues(self):
        # THE CALIBRATION, NOT A HOUSE CONSTANT. Every weight in the sizing
        # model comes off this number, it carried 0.22, and the act's own
        # analogue rows put the widebodies between 0.124 and 0.167. A figure
        # above every widebody in the table the winner is held against is a
        # calibration error with the evidence in the same file.
        from workflows.aircraft_optimization import (_ANALOGUES, _KG_PER_PAX,
                                                     _PAYLOAD_FRACTION)
        measured = [a["pax"] * _KG_PER_PAX / a["mtow_kg"] for a in _ANALOGUES]
        self.assertAlmostEqual(_PAYLOAD_FRACTION,
                               sum(measured) / len(measured), places=12)
        self.assertLessEqual(_PAYLOAD_FRACTION, max(measured))
        self.assertGreaterEqual(_PAYLOAD_FRACTION, min(measured))
        self.assertLess(_PAYLOAD_FRACTION, 0.22)

    def test_the_ledger_says_where_the_payload_fraction_was_measured(self):
        from workflows.aircraft_optimization import (_PAYLOAD_FRACTION,
                                                     assumed_values,
                                                     parse_requirements)
        reqs = parse_requirements("300 passengers, 6000 km range")
        ledger = {label: (value, basis)
                  for label, value, basis in assumed_values(reqs)}
        value, basis = ledger["Payload fraction"]
        self.assertEqual(value, f"{_PAYLOAD_FRACTION:.3f}")
        self.assertIn("measured on the analogue aircraft", basis)

    def test_every_analogue_figure_is_a_number_with_a_seat_and_range_figure(self):
        from workflows.aircraft_optimization import _ANALOGUES
        self.assertTrue(_ANALOGUES)
        for a in _ANALOGUES:
            self.assertTrue(a["name"])
            for key in ("span_m", "mtow_kg", "pax", "range_km"):
                self.assertIsInstance(a[key], (int, float), a["name"])
                self.assertGreater(a[key], 0, a["name"])
            for key in ("area_m2", "aspect_ratio"):
                self.assertTrue(a[key] is None or a[key] > 0, a["name"])

    def test_the_comparison_reaches_the_transcript_as_a_table(self):
        events = []
        main(request="Optimize the L/D of an airliner for 300 passengers, "
                     "6000 km range",
             emit=lambda e, p: events.append((e, p)))
        tables = [p for e, p in events if e == "transcript.table"
                  and p["table_id"] == "analogue-check"]
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0]["headers"],
                         ["Parameter", "Winner", "Analogues", "Verdict"])
        self.assertEqual(len(tables[0]["rows"]), 4)
        said = " ".join(p.get("message", "") for e, p in events
                        if e == "transcript.entry")
        self.assertIn("Airbus A300-600R", said)
        self.assertIn("Boeing 767-300", said)


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
        # The labels carry their subscripts, which is how every camera
        # surface typesets a coefficient.
        self.assertEqual(table["C_L_max (take-off)"][1],
                         "assumed, not solver-derived")
        self.assertEqual(table["C_L_max (landing)"][1],
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
                         ["Span", "Sweep", "α", "C_Di", "C_D0, wing",
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

    def test_warm_reuse_never_reports_another_runs_wall_clock(self):
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
        # Every stamp here was written by the run that first produced the
        # result, so none of these seconds belong to THIS run. The act used to
        # print max(per-wing elapsed_s) and call it a wall clock, which is both
        # another run's measurement and a PARALLEL estimate valid only at as
        # many slots as there are wings. It states the wings and the slots and
        # no time at all.
        self.assertIn("Finalist solves:", said)
        self.assertNotIn("s wall", said)
        self.assertNotIn("84.0", said)
        self.assertNotIn("12.3", said)

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

    # -- the winner is a family when the numbers do not separate it --------
    CRUISE = {"cl_cruise": 0.478, "cdo_wing_solved": 0.006014,
              "cdi_solved": 0.004889}

    def _sibling(self, sweep, ld, **over):
        row = {"span": 67.0, "area": 300.0, "sweep_deg": sweep,
               "L_D_solved": ld, **self.CRUISE}
        row.update(over)
        return row

    def test_siblings_inside_the_fidelity_band_are_one_family(self):
        solved = [self._sibling(s, ld) for s, ld in
                  ((20.0, 20.0), (25.0, 20.0), (30.0, 20.0), (35.0, 20.1))]
        best = solved[-1]
        family = unresolved_family(solved, best)
        # The whole 67 m / 300 m² set: a 0.1 spread against a band of order 1.
        self.assertEqual([f["sweep_deg"] for f in family],
                         [20.0, 25.0, 30.0, 35.0])
        self.assertGreater(buildup_band_ld(**{
            "cl": self.CRUISE["cl_cruise"],
            "cdo_wing": self.CRUISE["cdo_wing_solved"],
            "cdi": self.CRUISE["cdi_solved"]}), 0.2)

    def test_a_different_planform_is_never_family_however_close(self):
        best = self._sibling(35.0, 20.1)
        solved = [best,
                  self._sibling(25.0, 20.1, span=61.0),   # same area, off span
                  self._sibling(25.0, 20.1, area=360.0)]  # same span, off area
        self.assertEqual(unresolved_family(solved, best), [best])

    def test_a_sibling_beyond_the_band_is_separated(self):
        best = self._sibling(35.0, 20.1)
        far = self._sibling(20.0, 12.0)
        self.assertEqual(unresolved_family([best, far], best), [best])

    def test_a_winner_without_solved_terms_stands_alone(self):
        best = {"span": 67.0, "area": 300.0, "sweep_deg": 35.0}
        self.assertEqual(unresolved_family([best], best), [best])

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

    def test_the_bound_is_stated_with_the_result_not_ahead_of_it(self):
        # Whatever the search returns is the best point on a bounded grid, and
        # for a parabolic polar maximum L/D goes as the square root of aspect
        # ratio and never turns over, so the bound picks the winner. That used
        # to be said four beats before the number it qualifies; a viewer who
        # meets the L/D first has already read it as an interior optimum.
        events = self._run_solved()
        said = self._messages(events)
        bound = [i for i, m in enumerate(said)
                 if "best point on a bounded grid" in m]
        self.assertTrue(bound, said)
        blob = said[bound[0]]
        self.assertIn("without turning over", blob)
        self.assertIn("Move the bound and the answer moves with it", blob)
        # Adjacent to the result, not stranded in the middle of the analogue
        # and gate-code beats: the fidelity line that carries the verdict is
        # the one just before it.
        verdict_lines = [i for i, m in enumerate(said)
                         if "Wing solved with VSPAERO" in m]
        self.assertTrue(verdict_lines)
        self.assertLess(bound[0] - verdict_lines[-1], 2)

    def test_a_range_overshoot_says_why_it_is_free_to_the_objective(self):
        # Range is a feasibility floor and Breguet range here is proportional
        # to L/D at a fixed fuel fraction, so maximising the objective drags
        # range up and the floor cannot bind at the optimum. An engineer
        # watching the aircraft report far more range than it was asked for
        # will ask, so the act answers first.
        events = self._run_solved()
        said = " ".join(self._messages(events))
        verdict = [p for e, p in events if e == "result.verdict"][0]
        from workflows.aircraft_optimization import range_for_ld
        quoted = range_for_ld(float(verdict["value"]))
        self.assertGreater(quoted, 6000.0 * 1.05)
        self.assertIn("Range is a floor the search must clear, never a target",
                      said)
        self.assertIn("proportional to whole-aircraft L/D", said)
        self.assertIn("sizing fuel to the requirement is a trade this model "
                      "does not make", said)

    def test_certificate_carries_the_result_and_no_unquantified_row(self):
        events = self._run_solved()
        cert = [p for e, p in events if e == "certificate.ready"][0]
        text = Path(cert["path"]).read_bytes().decode("latin-1")
        self.assertNotIn("not quantified", text)
        # Objective is this run's verbatim request.
        self.assertIn("300 passengers,", text)
        # Structured result table with Title Case labels and units.
        for token in ("Parameter", "Span", "AR", "MTOW", "Range",
                      "Approach Speed", "L/D"):
            self.assertIn(token, text)

    def test_certificate_is_the_result_and_its_uncertainty_alone(self):
        # THE RULE, not the instance. The page states what was concluded and
        # how far it is trusted: subject, this run's objective, the headline
        # with its interval, the parameter table, the three channels, and the
        # issuance and seal that cover them. The conditions the result rests
        # on -- scope, constraints, assumed values, and the solver-and-model
        # line -- are on the record in the digest and the transcript, and are
        # deliberately off the certificate: carrying them made it a two-leaf
        # page whose headline arrived on the second leaf.
        events = self._run_solved()
        cert = [p for e, p in events if e == "certificate.ready"][0]
        text = Path(cert["path"]).read_bytes().decode("latin-1")
        for absent in ("(Scope)", "(Constraints)", "(Assumed Values)",
                       "(Solver & Model)", "(Solver &", "user-stated",
                       "Structural span limit", "assumed, not solver-derived",
                       "VSPAERO vortex lattice", "research sizing screen",
                       "Research drag-polar sizing model"):
            self.assertNotIn(absent, text, absent)
        for present in ("(Result)", "(Parameter)", "(Uncertainty)",
                        "(Objective)", "(Subject)"):
            self.assertIn(present, text, present)
        # Issuance and the seal sit together at the foot.
        self.assertLess(text.index("(Result)"), text.index("(Issued"))

    def test_the_certificate_is_one_page(self):
        # What prompted the strip: the page ran to two leaves and the
        # headline landed on the second.
        events = self._run_solved()
        cert = [p for e, p in events if e == "certificate.ready"][0]
        raw = Path(cert["path"]).read_bytes()
        self.assertIn(b"/Type /Pages /Kids [3 0 R] /Count 1 >>", raw)

    def test_wording_is_the_cleared_capability_statement(self):
        events = self._run_solved()
        said = " ".join(self._messages(events))
        self.assertIn("Wing solved with VSPAERO: induced and viscous drag "
                      "from the solved polar at cruise", said)
        self.assertIn("Non-wing drag comes from the component buildup method "
                      "(Raymer)", said)
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

    def test_the_conclusion_zone_quotes_one_range_and_it_is_solve_tier(self):
        # THE RULE, not the instance. Whatever range the screened optimum row
        # carries, no surface past the evidence phase may repeat it: the
        # report result, the certificate result and the certificate's Range
        # field all quote the Breguet range of the SOLVED L/D, and they all
        # quote the same one.
        events = self._run_solved()
        tables = [p for e, p in events if e == "transcript.table"]
        screened = [p for p in tables
                    if p["table_id"] == "screened-optimum"][0]
        screen_range = screened["rows"][0][4]
        self.assertTrue(screen_range.endswith("km"), screen_range)

        report = [p for e, p in events if e == "report.ready"][0]
        envelope = report["results"][0]["envelope"]
        self.assertIn("range ", envelope)
        quoted = envelope.split("range ")[1]
        self.assertNotEqual(quoted, screen_range)
        # It is the range the solved L/D flies, on the act's own constants.
        verdict = [p for e, p in events if e == "result.verdict"][0]
        expected = range_for_ld(float(verdict["value"]))
        self.assertAlmostEqual(float(quoted.split()[0]), round(expected),
                               delta=60.0)
        # And the certificate quotes that one figure, never the screened one.
        cert = [p for e, p in events if e == "certificate.ready"][0]
        text = Path(cert["path"]).read_bytes().decode("latin-1")
        self.assertIn(quoted.split()[0], text)
        self.assertNotIn(screen_range.split()[0], text)

    def test_the_limitations_section_is_titled_for_what_it_holds(self):
        # The list holds a boundary-set optimum, a discrete-grid caveat and
        # the non-wing provenance. None of those is a band, so the section is
        # Limitations and the three computed bands keep the word uncertainty.
        report = [p for e, p in self._run_solved() if e == "report.ready"][0]
        self.assertEqual(report["uncertainty_title"], "Limitations")
        self.assertTrue(report["uncertainty"])

    def test_the_certificate_names_the_family_and_the_open_sweep_axis(self):
        # Span, AR and MTOW are shared by every member, so the page names the
        # winner either way. Sweep is not, and gets a row saying so.
        events = self._run_solved()
        said = " ".join(self._messages(events))
        self.assertIn("family, whole-aircraft L/D", said)
        self.assertIn("Quarter-chord sweep is not resolved at this fidelity",
                      said)
        report = [p for e, p in events if e == "report.ready"][0]
        self.assertTrue(any("not resolved at this fidelity" in line
                            for line in report["uncertainty"]))
        cert = [p for e, p in events if e == "certificate.ready"][0]
        text = Path(cert["path"]).read_bytes().decode("latin-1")
        self.assertIn("Sweep", text)
        self.assertIn("not resolved at this", text)

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


class ShootRoundTests(unittest.TestCase):
    """The owner's shoot-day round: captions, speaking order, the tags on the
    constraint table, where the worker count is allowed to appear, and the
    announced search bound agreeing with the winner."""

    # The prompt as she types it, with a surface attached.
    DIRECTIVE = ("Optimize lift drag coefficient of the attached twin "
                 "airliner. Constraints: 300 passengers, Range: 6000 km, "
                 "take off speed: 80 m/s landing speed: 70 m/s. "
                 "Don't use all of my workers")
    # The prompt already registered for this act, which must keep working.
    STANDING = ("Optimize the L/D of an airliner for 300 passengers, "
                "6000 km range.")

    def setUp(self):
        _disable_pace(self)
        _redirect_output(self)

    def _run(self, request=None, params=None, api=None):
        from workflows import aircraft_optimization as aopt

        events = []
        emit = lambda e, p: events.append((e, p))
        live = api is not None
        with mock.patch.object(aopt.vspaero, "available", return_value=live), \
                mock.patch.object(aopt.vspaero, "VspAeroWingApi",
                                  api or aopt.vspaero.VspAeroWingApi):
            rc = aopt.main(request=request or self.STANDING,
                           params=params or {}, emit=emit)
        self.assertEqual(rc, 0)
        return events

    @staticmethod
    def _entries(events):
        return [p for e, p in events if e == "transcript.entry"]

    @classmethod
    def _first(cls, events, needle):
        """Index of the first transcript entry carrying ``needle``."""
        for i, p in enumerate(cls._entries(events)):
            if needle in p.get("message", ""):
                return i
        return None

    # -- the new prompt ----------------------------------------------------
    def test_the_typed_directive_routes_here_with_its_worker_ask(self):
        route = classify(self.DIRECTIVE)
        self.assertEqual(route.intent, AIRCRAFT_OPTIMIZATION)
        self.assertTrue(route.params.get("hold_workers_back"))
        # The uploaded surface keeps the route and rides as starting geometry.
        with_surface = apply_surface(classify(self.DIRECTIVE),
                                     "airliner_wing_span52.stl")
        self.assertEqual(with_surface.intent, AIRCRAFT_OPTIMIZATION)
        self.assertEqual(with_surface.params["surface"],
                         "airliner_wing_span52.stl")

    def test_the_standing_prompt_still_routes_here(self):
        self.assertEqual(classify(self.STANDING).intent, AIRCRAFT_OPTIMIZATION)

    def test_the_typed_directive_steals_no_other_act(self):
        # Every other filmed prompt keeps the act it had. The new directive
        # adds vocabulary ("lift drag", "workers"), and this is the guard that
        # it took nothing with it.
        from chief_engineer.router import (ADJOINT_OPTIMIZATION, AHMED_BODY,
                                           CRM_WINGBODY, CYLINDER_VORTEX_SHEDDING,
                                           DIAMOND_AIRFOIL, GEOMETRY_STUDY,
                                           HYPERSONIC_CYLINDER, NASA_HUMP,
                                           RACE_COMPARISON, SUPERSONIC_CONE,
                                           SUPERSONIC_WEDGE, VALVE_STUDY)
        filmed = {
            "Solve the supersonic wedge at Mach 2 with a 15 degree half-angle "
            "and check the oblique shock angle.": SUPERSONIC_WEDGE,
            "Solve the supersonic cone at Mach 2.35 with a 10 degree "
            "half-angle and check the conical shock angle.": SUPERSONIC_CONE,
            "Solve the diamond airfoil at Mach 2 and check the wave drag "
            "against shock-expansion theory.": DIAMOND_AIRFOIL,
            "Solve hypersonic flow over a blunt cylinder at Mach 8 and check "
            "the shock standoff distance.": HYPERSONIC_CYLINDER,
            "Solve vortex shedding behind a circular cylinder at Reynolds 100 "
            "and check the Strouhal number.": CYLINDER_VORTEX_SHEDDING,
            "Solve the Ahmed body with the 25 degree slant and check the drag "
            "against the wind tunnel.": AHMED_BODY,
            "Solve the NASA wall-mounted hump and check separation": NASA_HUMP,
            "Solve the CRM wing-body and check the drag.": CRM_WINGBODY,
            "Cut the drag on the wing with the discrete adjoint and verify the "
            "gradient against finite differences.": ADJOINT_OPTIMIZATION,
            "Find the valve opening angle that minimizes pressure loss over "
            "the cardiac cycle.": VALVE_STUDY,
            "Race a Monte Carlo uncertainty study against a reduced-order "
            "model.": RACE_COMPARISON,
        }
        for prompt, intent in filmed.items():
            self.assertEqual(classify(prompt).intent, intent, prompt)
        self.assertEqual(
            apply_surface(classify("Solve the external aerodynamics of the "
                                   "supplied B-52 geometry."),
                          "b52.stl").intent, GEOMETRY_STUDY)

    # -- item 3: what the stated speeds moved ------------------------------
    def test_stated_speeds_are_user_stated_and_the_area_floor_is_derived(self):
        from workflows.aircraft_optimization import (assumed_values,
                                                     constraint_list)
        reqs = parse_requirements(self.DIRECTIVE)
        self.assertTrue(reqs["takeoff_stated"] and reqs["landing_stated"])
        rows = {name: (value, tag)
                for name, value, tag in constraint_list(reqs, advisory=False)}
        self.assertEqual(rows["Take-off speed"][1], "user-stated")
        self.assertEqual(rows["Landing speed"][1], "user-stated")
        # The wing area those two demand follows from them, so it is derived.
        self.assertTrue(rows["Wing area"][1].startswith("derived"))
        # And it is a floor at ONE weight, so the row names that weight and
        # says the screen holds each wing to the floor its own weight sets.
        # The weight is read off the act's own floor calculation rather than
        # typed here: it moves with the payload fraction, which is measured on
        # the analogue table, and a literal would go stale the next time a
        # published MTOW is corrected.
        from workflows.aircraft_optimization import low_speed_area_floor
        _area, reference_mtow = low_speed_area_floor(reqs)
        self.assertIn(f"at reference MTOW {reference_mtow / 1000:.0f} t",
                      rows["Wing area"][0])
        self.assertIn("applied per-design at each wing's weight",
                      rows["Wing area"][1])

        # The two maximum lift coefficients do not follow from a speed limit,
        # so they stay assumed and stay in the ledger.
        ledger = {label: basis for label, _v, basis in assumed_values(reqs)}
        self.assertEqual(ledger["C_L_max (take-off)"],
                         "assumed, not solver-derived")
        self.assertEqual(ledger["C_L_max (landing)"],
                         "assumed, not solver-derived")
        # Neither speed is in the ledger any more.
        self.assertNotIn("Take-off speed limit", ledger)
        self.assertNotIn("Landing speed limit", ledger)

    def test_the_screen_applies_the_area_floor_at_each_wings_own_weight(self):
        # PROOF, not inference. ONE area clears the approach limit on a short
        # span and misses it on a long one, because the long wing's own MTOW
        # carries the span-structural penalty and asks for more area. One
        # fixed floor could not produce both verdicts.
        #
        # The area is searched for rather than typed. Both wings' floors scale
        # with the payload calibration, so a literal that split them at one
        # calibration lands under both at another and the test then fails for
        # a reason that has nothing to do with the claim it makes.
        reqs = parse_requirements(self.DIRECTIVE)

        def misses_approach(design):
            return any(v.startswith("approach speed")
                       for v in design["violations"])

        split = next((a for a in range(200, 900)
                      if not misses_approach(
                          evaluate_design(37.0, float(a), 25.0, reqs))
                      and misses_approach(
                          evaluate_design(67.0, float(a), 25.0, reqs))), None)
        self.assertIsNotNone(split, "no area separates the two spans")
        light = evaluate_design(37.0, float(split), 25.0, reqs)
        heavy = evaluate_design(67.0, float(split), 25.0, reqs)
        self.assertGreater(heavy["mtow_kg"], light["mtow_kg"])
        self.assertFalse(misses_approach(light), light)
        self.assertTrue(misses_approach(heavy), heavy)
        # The heavy wing clears once it is given the area its own weight asks
        # for, which is above the reference floor quoted on the table.
        cleared = next((d for d in (evaluate_design(67.0, float(a), 25.0, reqs)
                                    for a in range(split, split + 400, 5))
                        if d["feasible"]), None)
        self.assertIsNotNone(cleared)
        self.assertGreater(cleared["area"], light["area"])

    # -- item 1: the viewport caption --------------------------------------
    def test_every_viewport_caption_is_scoped_wing_only(self):
        events = self._run()
        labels = [p["label"] for e, p in events
                  if e == "geometry.ready" and p.get("label")]
        self.assertTrue(labels)
        for label in labels:
            self.assertTrue(label.startswith("Wing-only"), label)
            self.assertNotIn("component buildup", label)

    def test_the_winner_caption_is_the_scope_and_nothing_else(self):
        # The winner's surface has to land on disk for its caption to be
        # emitted at all, so this api writes one.
        stl = Path(tempfile.mkdtemp()) / "wing.stl"
        stl.write_text(_TINY_STL)

        class _WithSurface(_SolvedApi):
            def evaluate(self, design, analyses=()):
                result = _SolvedApi.evaluate(self, design, analyses)
                result["stl_path"] = str(stl)
                return result

        events = self._run(api=_WithSurface)
        labels = [p["label"] for e, p in events
                  if e == "geometry.ready" and p.get("label")]
        self.assertIn("Wing-only", labels)

    # -- item 7: the researcher opens, the engineer answers ----------------
    def test_the_method_memo_opens_and_the_engineer_answers_with_the_limits(self):
        events = self._run()
        entries = self._entries(events)
        spoken = [p for p in entries
                  if p.get("role") not in ("SYSTEM", "PHASE")]
        # The two method-memo blocks are the first thing spoken, under one
        # Chief Researcher header.
        self.assertEqual([p["role"] for p in spoken[:2]],
                         ["CHIEF RESEARCHER", "CHIEF RESEARCHER"])
        self.assertIn("Smooth 3-parameter space", spoken[0]["message"])
        self.assertIn("The landscape is smooth", spoken[1]["message"])
        # The engineer answers, and the requirements ride in on the answer
        # rather than in a second Chief Engineer entry of their own.
        self.assertEqual(spoken[2]["role"], "CHIEF ENGINEER")
        self.assertTrue(spoken[2]["message"].startswith("On it."))
        self.assertIn("Requirements fixed", spoken[2]["message"])
    def test_no_speaker_takes_three_headers_in_a_row(self):
        # A phase marker is a visual break, so it stays in the sequence and
        # resets the run. Both the bare prompt and the shoot-day one with a
        # surface attached, because the surface adds an entry.
        for request, params in ((self.STANDING, None),
                                (self.DIRECTIVE,
                                 {"surface": "airliner_wing_span52.stl",
                                  "hold_workers_back": True})):
            with self.subTest(request=request[:30]):
                entries = self._entries(self._run(request=request,
                                                  params=params))
                roles = [p.get("role") for p in entries
                         if p.get("role") != "SYSTEM"]
                for i in range(len(roles) - 2):
                    self.assertFalse(roles[i] == roles[i + 1] == roles[i + 2],
                                     f"{roles[i]} three times at entry {i}")

    def test_the_fleet_comes_up_once_and_goes_down_once(self):
        # 0, then the fleet as sizing starts, then 0 at completion. No bounce
        # back to zero between the screening sweep and the finalist wave.
        for api in (None, _SolvedApi):
            with self.subTest(api=api):
                events = self._run(api=api)
                counts = [p["workers"] for e, p in events
                          if e == "roster.update"]
                shape = [n for i, n in enumerate(counts)
                         if i == 0 or n != counts[i - 1]]
                self.assertEqual(len(shape), 3, shape)
                self.assertEqual(shape[0], 0)
                self.assertGreater(shape[1], 0)
                self.assertEqual(shape[2], 0)

    def test_the_plan_is_the_researchers(self):
        events = self._run()
        entries = self._entries(events)
        plan = [p for p in entries if "• Plan: screen" in p.get("message", "")]
        self.assertEqual(len(plan), 1)
        self.assertEqual(plan[0]["role"], "CHIEF RESEARCHER")
        self.assertIn("Infeasible designs stay on the plot",
                      plan[0]["message"])

    def test_the_researcher_owns_the_maximum_lift_line(self):
        events = self._run()
        entries = self._entries(events)
        said = [p for p in entries
                if "maximum lift coefficient no vortex-lattice" in
                p.get("message", "")]
        self.assertEqual(len(said), 1)
        self.assertEqual(said[0]["role"], "CHIEF RESEARCHER")
        self.assertIn("But good for preliminary design", said[0]["message"])

    # -- item 4: the worker count arrives with the work --------------------
    def test_no_worker_count_before_the_tier_line(self):
        events = self._run(api=_SolvedApi)
        entries = self._entries(events)
        tier = self._first(events, "Screen is research sizing")
        self.assertIsNotNone(tier)
        for i, p in enumerate(entries[:tier]):
            self.assertNotIn("workers", p.get("message", "").lower(), p)
        # The headroom table is a worker count too, and it lands after.
        order = [(e, p) for e, p in events
                 if e in ("transcript.entry", "transcript.table")]
        seen_tier = False
        for e, p in order:
            if e == "transcript.entry" and "Screen is research sizing" in \
                    p.get("message", ""):
                seen_tier = True
            if e == "transcript.table" and p["table_id"] == "worker-headroom":
                self.assertTrue(seen_tier)

    # -- items 5, 6, 9: the announced bound tells the truth ----------------
    def test_the_announced_span_bound_contains_the_winner(self):
        import re as _re

        events = self._run(request=self.DIRECTIVE,
                           params={"surface": "airliner_wing_span52.stl",
                                   "hold_workers_back": True})
        said = " ".join(p.get("message", "") for p in self._entries(events))
        bound = _re.search(r"Span (\d+) to (\d+) m", said)
        self.assertIsNotNone(bound, said)
        lo, hi = float(bound.group(1)), float(bound.group(2))
        tables = [p for e, p in events if e == "transcript.table"]
        screened = [p for p in tables if p["table_id"] == "screened-optimum"][0]
        winner_span = float(screened["rows"][0][1].split()[0])
        self.assertLessEqual(winner_span, hi)
        self.assertGreaterEqual(winner_span, lo)
        # Nothing announces a span bound before the search has run. The
        # 65 m gate-code offer used to be the only span figure spoken ahead of
        # the sweep, and it is not a search bound.
        before_evidence = said.split("Screening sweep")[0]
        self.assertNotIn("span at most 65 m", before_evidence)
        self.assertNotIn("Aerodrome Reference Code", before_evidence)

    # -- item 8: where the advisory belongs, and who counts the misses -----
    def test_the_gate_advisory_is_the_researchers_and_follows_a_span(self):
        events = self._run()
        entries = self._entries(events)
        gate = [(i, p) for i, p in enumerate(entries)
                if "ICAO Aerodrome Reference Code" in p.get("message", "")]
        self.assertEqual(len(gate), 1)
        index, entry = gate[0]
        self.assertEqual(entry["role"], "CHIEF RESEARCHER")
        # It names the span it is about, and it comes after the screen found
        # one: the winner is announced in the screened-optimum table above it.
        self.assertIn("winner span", entry["message"].lower())
        self.assertGreater(index, self._first(events, "wings clear every "
                                                      "requirement"))

    def test_the_numericist_counts_the_designs_ruled_out(self):
        events = self._run()
        ruled = [p for e, p in events if e == "transcript.table"
                 and p["table_id"] == "ruled-out"]
        self.assertEqual(len(ruled), 1)
        self.assertEqual(ruled[0]["role"], "NUMERICIST")

    # -- the analogue outliers are explained, not left hanging -------------
    def test_the_researcher_explains_the_distance_to_the_analogues(self):
        events = self._run()
        entries = self._entries(events)
        line = [p for p in entries
                if "aspect ratio 9 to 11" in p.get("message", "")]
        self.assertEqual(len(line), 1)
        self.assertEqual(line[0]["role"], "CHIEF RESEARCHER")
        self.assertIn("difference in objective", line[0]["message"])
        analogue = [i for i, (e, p) in enumerate(events)
                    if e == "transcript.table"
                    and p["table_id"] == "analogue-check"]
        self.assertTrue(analogue)
