"""Act 3 — the idealized valve: geometry, waveform, and the multi-point screen."""

import sys
import unittest
from pathlib import Path

_VALVE = Path(__file__).resolve().parents[2] / "models" / "curriculum" / "aortic_valve"
for _p in (str(_VALVE.parent), str(_VALVE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import generate_valve  # noqa: E402
import waveform  # noqa: E402


class GeometryTests(unittest.TestCase):
    def test_orifice_area_grows_with_opening_angle(self):
        areas = [generate_valve.effective_orifice_area(a) for a in (35, 50, 65, 80)]
        self.assertEqual(areas, sorted(areas))
        self.assertTrue(all(x > 0 for x in areas))

    def test_valve_builds_a_valid_triangle_mesh(self):
        V, F = generate_valve.build_valve(65.0)
        self.assertGreater(len(F), 0)
        self.assertTrue((F >= 0).all() and (F < len(V)).all())
        self.assertGreaterEqual(len(F), 3)

    def test_orifice_is_a_few_hundred_mm2_at_scale(self):
        area_mm2 = generate_valve.effective_orifice_area(80.0) * 1e6
        self.assertGreater(area_mm2, 100)
        self.assertLess(area_mm2, 500)

    def test_viewport_valve_surface_opens_with_angle(self):
        # The control-room valve_surface must render a real body and its orifice
        # must widen with the opening angle, matching the physics.
        from chief_engineer.geometry import valve_surface
        radii = []
        for a in (35, 50, 65, 80):
            s = valve_surface(a)
            self.assertGreater(len(s["vertices"]), 0)
            self.assertGreater(len(s["faces"]), 0)
            for f in s["faces"]:
                self.assertTrue(all(0 <= i < len(s["vertices"]) for i in f))
            # free-edge radius = root_radius * sin(theta); recover it from bounds.
            radii.append(max(abs(v[1]) for v in s["vertices"]))
        self.assertTrue("bounds" in valve_surface(65))


class WaveformTests(unittest.TestCase):
    def test_three_phase_points_weights_sum_to_one(self):
        phases = waveform.phase_points()
        self.assertEqual(len(phases), 3)
        self.assertAlmostEqual(sum(p.weight for p in phases), 1.0, places=9)

    def test_phases_are_ordered_accel_peak_decel(self):
        taus = [p.tau for p in waveform.phase_points()]
        self.assertEqual(taus, sorted(taus))
        weights = [p.weight for p in waveform.phase_points()]
        self.assertEqual(max(range(3), key=lambda i: weights[i]), 1)

    def test_womersley_is_the_high_aortic_value(self):
        alpha = waveform.womersley(0.0115)
        self.assertGreater(alpha, 10)   # aortic root is inertially unsteady
        self.assertLess(alpha, 25)


def _run_valve():
    """Run the valve act once with pacing off and return every emitted event."""
    import os
    from workflows.valve_study import main

    os.environ["CERTONOMOUS_SWEEP_PACE_MS"] = "0"
    stream = []
    rc = main(request="minimise valve pressure loss over the cardiac cycle",
              emit=lambda e, p: stream.append((e, p)))
    return rc, stream


def _of(stream, event):
    return [p for e, p in stream if e == event]


class WorkflowTests(unittest.TestCase):
    def test_multipoint_screen_grades_conceptual_model(self):
        from workflows.valve_study import main, CANDIDATE_ANGLES
        events = {}
        verdict = {}
        agenda = {}
        certificate = {}

        def emit(e, p):
            events[e] = events.get(e, 0) + 1
            if e == "result.verdict":
                verdict.update(p)
            if e == "agenda.updated":
                agenda.update(p)
            if e == "certificate.ready":
                certificate.update(p)

        import os
        os.environ["CERTONOMOUS_SWEEP_PACE_MS"] = "0"
        rc = main(request="minimise valve pressure loss over the cardiac cycle", emit=emit)
        self.assertEqual(rc, 0)
        n = len(CANDIDATE_ANGLES)
        # A denser sweep so the valve visibly cycles many more times: one
        # cycle-weighted landscape point per real candidate.
        self.assertGreaterEqual(n, 10)
        self.assertEqual(events.get("landscape.point"), n)
        self.assertEqual(events.get("report.ready"), 1)
        self.assertEqual(events.get("uncertainty.channels"), 1)
        # valve renders every candidate valve plus the winner in the viewport
        self.assertEqual(events.get("geometry.ready"), n + 1)
        # the systolic waveform figure leads the report
        self.assertEqual(events.get("plot.ready"), 1)
        # the dispatch panel and the live objective trace are fed
        self.assertGreaterEqual(events.get("dispatch.update", 0), 2 * n)
        self.assertEqual(events.get("trace.point"), n)
        # hard cap
        self.assertEqual(verdict.get("tier"), "RESEARCH MODEL")
        # Physics stays consistent: the widest admissible orifice still wins, so
        # the denser sweep peaks in the same 80 deg region as the old screen.
        self.assertIn("80 deg", verdict.get("envelope", ""))
        # Act 3 carries a Certonomous certificate with its evidence seal.
        self.assertEqual(events.get("certificate.ready"), 1)
        self.assertEqual(certificate.get("fidelity"), "RESEARCH MODEL")
        self.assertEqual(certificate.get("dir"), "valve-study")
        self.assertTrue(Path(certificate.get("path", "")).exists())
        # agenda carries the three deferred capabilities
        self.assertEqual(len(agenda.get("entries", [])), 3)
        for entry in agenda["entries"]:
            self.assertIn("title", entry)
            self.assertIn("scope", entry)
            self.assertIn("cost", entry)

    def test_certificate_failure_never_takes_down_a_good_mission(self):
        # A certificate is wrapped: if issuing it raises, the mission must still
        # complete and report normally.
        import os
        from unittest import mock
        from workflows.valve_study import main

        os.environ["CERTONOMOUS_SWEEP_PACE_MS"] = "0"
        events = {}

        def emit(e, p):
            events[e] = events.get(e, 0) + 1

        with mock.patch("chief_engineer.certificate.build_certificate_v2",
                        side_effect=RuntimeError("boom")):
            rc = main(request="minimise valve pressure loss over the cardiac "
                              "cycle", emit=emit)
        self.assertEqual(rc, 0)
        self.assertEqual(events.get("report.ready"), 1)
        self.assertIsNone(events.get("certificate.ready"))

    def test_candidates_land_in_one_live_growing_table(self):
        # Every candidate is a row of ONE table that grows as evaluations
        # complete, not a repeated per-candidate transcript entry.
        from workflows.valve_study import CANDIDATE_ANGLES
        rc, stream = _run_valve()
        self.assertEqual(rc, 0)
        tables = _of(stream, "transcript.table")
        self.assertEqual(len(tables), len(CANDIDATE_ANGLES) + 1)
        header, *rows = tables
        self.assertFalse(header["append"])
        self.assertEqual(header["rows"], [])
        self.assertEqual(header["headers"],
                         ["Angle", "Orifice Area", "Cycle Loss", "Admissible"])
        ids = {t["table_id"] for t in tables}
        self.assertEqual(ids, {"valve-candidates"})
        for t in rows:
            self.assertTrue(t["append"])
            self.assertEqual(t["headers"], header["headers"])
            self.assertEqual(len(t["rows"]), 1)
        # one row per candidate angle, in sweep order, values carrying units
        angles = [t["rows"][0][0] for t in rows]
        self.assertEqual(angles, [f"{a:g}°" for a in CANDIDATE_ANGLES])
        for t in rows:
            angle, area, loss, admissible = t["rows"][0]
            self.assertTrue(area.endswith("mm²"))
            self.assertTrue(loss.endswith("Pa"))
            self.assertIn("±", loss)
            self.assertTrue(admissible.startswith(("Yes", "No")))
        # the tight openings stay marked infeasible, the winner admissible
        self.assertTrue(rows[0]["rows"][0][3].startswith("No"))
        self.assertEqual(rows[-1]["rows"][0][3], "Yes")
        self.assertEqual(rows[-1]["rows"][0][2], "1327 ± 421 Pa")
        # the per-candidate narration entries are gone: one lead-in bullet only
        lines = [p["message"] for p in _of(stream, "transcript.entry")]
        self.assertEqual([m for m in lines if "Opening 65" in m], [])
        self.assertEqual(
            len([m for m in lines if m.startswith("• Screening 11 opening angles")]), 1)

    def test_waveform_plot_rides_in_the_lab_report(self):
        rc, stream = _run_valve()
        self.assertEqual(rc, 0)
        report = _of(stream, "report.ready")[0]
        plots = report.get("plots") or []
        self.assertEqual(len(plots), 1)
        self.assertEqual(plots[0]["file"], "systolic_waveform.png")
        self.assertEqual(plots[0]["url"],
                         "/api/plot/valve-study/systolic_waveform.png")
        self.assertIn("waveform", plots[0]["title"].lower())
        # the same figure the plot strip announces, so one artifact serves both
        announced = _of(stream, "plot.ready")
        self.assertEqual(announced[0]["file"], plots[0]["file"])

    def test_womersley_ruling_carries_the_requirement_to_solve_it(self):
        rc, stream = _run_valve()
        self.assertEqual(rc, 0)
        lines = [p["message"] for p in _of(stream, "transcript.entry")]
        requirement = [m for m in lines if "To solve this for real" in m]
        self.assertEqual(len(requirement), 1)
        text = requirement[0]
        self.assertIn("transient pulsatile solve", text)
        self.assertIn("moving-boundary incompressible solver", text)
        self.assertIn("time-varying inlet waveform", text)
        self.assertIn("meshed valve geometry", text)
        self.assertIn("becomes the initial guess, not the answer", text)
        # the ruling is ONE agent entry: the three admissibility bullets plus
        # the requirement statement ride the same entry as its bullet rows
        for phrase in ("above the strict limit 1, inertially unsteady",
                       "Under the screening ceiling 25, admissible as a screen",
                       "Dropped phase-interaction rides as model-form"):
            self.assertIn(phrase, text)
            self.assertEqual(len([m for m in lines if phrase in m]), 1, phrase)
        bullets = [b.strip() for b in text.split("•") if b.strip()]
        self.assertEqual(len(bullets), 4)
        self.assertTrue(bullets[-1].startswith("To solve this for real."))

    def test_input_channel_states_the_compute_budget(self):
        rc, stream = _run_valve()
        self.assertEqual(rc, 0)
        channels = _of(stream, "uncertainty.channels")[0]["channels"]
        by_name = {c["name"]: c for c in channels}
        self.assertIn("The compute budget allows the full 2-sigma Monte-Carlo "
                      "envelope.", by_name["input"]["note"])
        self.assertIn("2-sigma Monte-Carlo envelope propagated from the spread",
                      by_name["input"]["note"])
        # numbers untouched by the wording
        self.assertAlmostEqual(by_name["input"]["value"], 421.1424, places=4)
        self.assertAlmostEqual(by_name["numerical"]["value"], 81.0, places=4)
        self.assertAlmostEqual(by_name["model"]["value"], 104.8, places=4)

    def test_headline_numbers_are_unchanged(self):
        rc, stream = _run_valve()
        self.assertEqual(rc, 0)
        verdict = _of(stream, "result.verdict")[0]
        self.assertEqual(verdict["value"], "1327")
        self.assertEqual(verdict["envelope"], "at opening 80 deg")
        report = _of(stream, "report.ready")[0]
        self.assertTrue(any("1327" in line for line in report["abstract"]))
        self.assertTrue(any("80 deg" in line for line in report["abstract"]))
        self.assertTrue(report["results"][0]["value"].startswith("1327"))

    def test_emitted_text_is_house_style(self):
        # No banned punctuation, no raw links; bullets stack as rows inside
        # ONE agent entry (never one entry per bullet), each row opening on a
        # capital letter.
        rc, stream = _run_valve()
        self.assertEqual(rc, 0)
        spoken = [p["message"] for p in _of(stream, "transcript.entry")]
        spoken += [p["title"] for p in _of(stream, "knowledge.added")
                   if p.get("title")]
        for table in _of(stream, "transcript.table"):
            spoken.append(table["title"])
            spoken += [cell for row in table["rows"] for cell in row]
        for channel in _of(stream, "uncertainty.channels")[0]["channels"]:
            spoken.append(channel["note"])
        for line in spoken:
            self.assertNotIn("—", line)      # em dash
            self.assertNotIn("--", line)
            self.assertNotIn("→", line)      # arrow
            self.assertNotIn("http", line)
            self.assertNotIn("conceptual model", line)   # retired term
            for banned in ("real solves", "pre-computed"):
                self.assertNotIn(banned, line.lower())
        # Every bullet row inside an entry opens with the "• " marker the GUI
        # splits on, and starts with a capital letter (or a number).
        for line in [p["message"] for p in _of(stream, "transcript.entry")]:
            if "•" not in line:
                continue
            self.assertTrue(line.startswith("• "), f"entry not bulleted: {line}")
            for bullet in [b.strip() for b in line.split("•") if b.strip()]:
                self.assertTrue(bullet[0].isupper() or bullet[0].isdigit(),
                                f"bullet does not open on a capital: {bullet}")

    def test_router_sends_valve_prompts_to_the_valve_study(self):
        from chief_engineer.router import classify, VALVE_STUDY
        route = classify("optimize the valve opening angle to minimise pressure "
                         "loss over the cardiac cycle")
        self.assertEqual(route.intent, VALVE_STUDY)


if __name__ == "__main__":
    unittest.main()
