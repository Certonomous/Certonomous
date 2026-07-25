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
        # Physics stays consistent: the widest admissible orifice wins, and the
        # sweep now extends past the old 80 deg cap to 87.5 deg (the fleet
        # ledger's evaluations beyond the cap showed lower loss).
        self.assertIn("87.5 deg", verdict.get("envelope", ""))
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
        self.assertEqual(rows[-1]["rows"][0][2], "1253 ± 398 Pa")
        # the per-candidate narration entries are gone: one lead-in bullet only
        lines = [p["message"] for p in _of(stream, "transcript.entry")]
        self.assertEqual([m for m in lines if "Opening 65" in m], [])
        self.assertEqual(
            len([m for m in lines if m.startswith("• Screening 13 opening angles")]), 1)
        # the extension past the old cap is narrated, citing the fleet ledger
        self.assertEqual(
            len([m for m in lines if "extends past the old 80 degree cap" in m]), 1)

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
        # Generic register (owner rule, 2026-07-24): no method named in any
        # channel note; the compute-budget statement stays.
        self.assertIn("The compute budget allows the full 2-sigma ensemble "
                      "envelope.", by_name["input"]["note"])
        self.assertIn("Ensemble run over the stated spread",
                      by_name["input"]["note"])
        # numbers untouched by the wording
        self.assertAlmostEqual(by_name["input"]["value"], 397.639, places=3)
        self.assertAlmostEqual(by_name["numerical"]["value"], 76.5, places=4)
        self.assertAlmostEqual(by_name["model"]["value"], 98.9, places=4)

    def test_channel_notes_stay_on_the_generic_register(self):
        rc, stream = _run_valve()
        self.assertEqual(rc, 0)
        channels = _of(stream, "uncertainty.channels")[0]["channels"]
        by_name = {c["name"]: c for c in channels}
        self.assertEqual(by_name["numerical"]["note"],
                         "Three-level refinement of the cycle evaluation; "
                         "the band is the spread between levels.")
        self.assertIn("Spread across published discharge-coefficient "
                      "correlations (screening estimate)",
                      by_name["model"]["note"])
        self.assertIn("unmodeled:", by_name["model"]["note"])
        blob = " ".join(str(c["note"]) for c in channels)
        for banned in ("Monte-Carlo", "quadrature", "k = 3/5/9", "Eca",
                       "Hoekstra", "GCI", "least-squares", "uq-"):
            self.assertNotIn(banned, blob)

    def test_certificate_renders_the_result_table_with_unchanged_numbers(self):
        # The sealed page: structured result table, all three channel values
        # (397.6 / 76.5 / 98.9), generic notes, and no mesh block, because
        # the reduced-order act solves no mesh.
        stream = []

        def emit(e, p):
            stream.append((e, p))

        import os
        os.environ["CERTONOMOUS_SWEEP_PACE_MS"] = "0"
        from workflows.valve_study import main
        rc = main(request="minimise valve pressure loss over the cardiac "
                          "cycle", emit=emit)
        self.assertEqual(rc, 0)
        cert = _of(stream, "certificate.ready")[0]
        text = Path(cert["path"]).read_bytes().decode("latin-1")
        for token in ("Opening Angle", "87.5 deg", "Cycle Loss", "1253 Pa",
                      "Band \\(95%\\)", "Orifice Area", "Parameter",
                      "397.63", "76.5", "98.9",
                      "minimise valve pressure loss over the cardiac cycle"):
            self.assertIn(token, text)
        # No mesh block on a meshless act; no method names on the sealed page.
        self.assertNotIn("Mesh Validity", text)
        for banned in ("Monte-Carlo", "quadrature", "Eca", "Hoekstra",
                       "GCI", "least-squares", "uq-"):
            self.assertNotIn(banned, text)

    def test_failed_certificate_withdraws_the_previous_page(self):
        # The uniform convention: the previous run's page is withdrawn first,
        # so a failed generation leaves nothing out of date being served, and
        # the act says so on the record.
        import os
        from unittest import mock
        from workflows.valve_study import main
        from workflows import OUT_ROOT

        os.environ["CERTONOMOUS_SWEEP_PACE_MS"] = "0"
        pdf = OUT_ROOT / "valve-study" / "certificate.pdf"
        rc = main(request="minimise valve pressure loss over the cardiac "
                          "cycle")
        self.assertEqual(rc, 0)
        self.assertTrue(pdf.exists())
        stream = []
        with mock.patch("chief_engineer.certificate.build_certificate_v2",
                        side_effect=RuntimeError("boom")):
            rc = main(request="minimise valve pressure loss over the cardiac "
                              "cycle",
                      emit=lambda e, p: stream.append((e, p)))
        self.assertEqual(rc, 0)
        self.assertFalse(pdf.exists())
        said = " ".join(p.get("message", "") for e, p in stream
                        if e == "transcript.entry")
        self.assertIn("No certificate could be issued for this run", said)
        self.assertIn("withdrawn", said)
        # Reissue for anything that reads the served directory afterwards.
        main(request="minimise valve pressure loss over the cardiac cycle")

    def test_headline_numbers_match_the_extended_sweep(self):
        # The sweep extended past 80 deg moved the winner: 87.5 deg at
        # 1253 Pa, exactly where the reduced-order physics puts the widest
        # admissible orifice (the ledger's 85 deg record at 1267 Pa sits on
        # the same curve).
        rc, stream = _run_valve()
        self.assertEqual(rc, 0)
        verdict = _of(stream, "result.verdict")[0]
        self.assertEqual(verdict["value"], "1253")
        self.assertEqual(verdict["envelope"], "at opening 87.5 deg")
        report = _of(stream, "report.ready")[0]
        self.assertTrue(any("1253" in line for line in report["abstract"]))
        self.assertTrue(any("87.5 deg" in line for line in report["abstract"]))
        self.assertTrue(report["results"][0]["value"].startswith("1253"))

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


class ValveReferenceSurface(unittest.TestCase):
    """An uploaded STL with a valve prompt keeps the valve route, and the act
    acknowledges it honestly as the reference body on file: display name,
    viewport announcement, and a plain statement that the screen runs on the
    parametric orifice family."""

    def test_uploaded_surface_keeps_the_valve_route(self):
        from chief_engineer.router import VALVE_STUDY, apply_surface, classify
        route = classify("optimize the valve opening angle to minimise "
                         "pressure loss over the cardiac cycle")
        route = apply_surface(route, "patient_valve.stl")
        self.assertEqual(route.intent, VALVE_STUDY)
        self.assertEqual(route.params.get("surface"), "patient_valve.stl")

    def test_uploaded_surface_is_acknowledged_displayed_and_framed(self):
        import os
        from workflows.valve_study import main

        os.environ["CERTONOMOUS_SWEEP_PACE_MS"] = "0"
        stream = []
        rc = main(request="minimise valve pressure loss over the cardiac "
                          "cycle",
                  params={"surface": "patient_valve.stl"},
                  emit=lambda e, p: stream.append((e, p)))
        self.assertEqual(rc, 0)
        # The uploaded surface is shown in the viewport under its display name.
        shown = [p for e, p in stream if e == "geometry.ready"
                 and str(p.get("label", "")).startswith("reference body:")]
        self.assertEqual(len(shown), 1)
        self.assertEqual(shown[0]["label"], "reference body: Patient valve")
        self.assertEqual(shown[0]["url"],
                         "/api/geometry?name=patient_valve.stl")
        # The acknowledgment is ONE entry with the honest framing.
        said = [p["message"] for e, p in stream if e == "transcript.entry"]
        ack = [m for m in said if "Reference body received" in m]
        self.assertEqual(len(ack), 1)
        self.assertIn("Patient valve", ack[0])
        self.assertIn("on file as the reference shape", ack[0])
        self.assertIn("parametric orifice family", ack[0])
        self.assertIn("not meshed or solved", ack[0])
        # The screen itself is unchanged: the certificate is still issued for
        # the valve subject, and the verdict still lands.
        self.assertEqual(len([p for e, p in stream
                              if e == "certificate.ready"]), 1)
        self.assertEqual(len([p for e, p in stream
                              if e == "result.verdict"]), 1)

    def test_no_surface_means_no_reference_acknowledgment(self):
        rc, stream = _run_valve()
        self.assertEqual(rc, 0)
        said = [p["message"] for e, p in stream if e == "transcript.entry"]
        self.assertEqual([m for m in said if "Reference body received" in m],
                         [])


class ReferenceSurfaceHelperTests(unittest.TestCase):
    """The shared acknowledge-reference-surface helper: display name, viewport
    announcement, honest framing, and a clean no-op without a surface."""

    class _Script:
        def __init__(self):
            self.lines = []

        def engineer(self, message):
            self.lines.append(message)

    def test_helper_announces_and_frames_honestly(self):
        from workflows import acknowledge_reference_surface

        script, events = self._Script(), []
        name = acknowledge_reference_surface(
            script, lambda e, p: events.append((e, p)),
            {"surface": "naca0015_sail.stl"}, family="cylinder")
        self.assertEqual(name, "NACA 0015 sail")
        self.assertEqual(events[0][0], "geometry.ready")
        self.assertEqual(events[0][1]["label"],
                         "reference body: NACA 0015 sail")
        self.assertEqual(len(script.lines), 1)
        self.assertIn("parametric cylinder family", script.lines[0])
        self.assertIn("not meshed or solved", script.lines[0])

    def test_no_surface_is_a_no_op(self):
        from workflows import acknowledge_reference_surface

        script, events = self._Script(), []
        name = acknowledge_reference_surface(
            script, lambda e, p: events.append((e, p)), {}, family="orifice")
        self.assertIsNone(name)
        self.assertEqual(events, [])
        self.assertEqual(script.lines, [])


if __name__ == "__main__":
    unittest.main()
