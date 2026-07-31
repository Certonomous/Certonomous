"""Race-study workflow — the streaming twin, tested without the real solver.

The lanes' event choreography (race.init, per-lane trace points and progress,
the speedup card, the agreement) must hold regardless of the solver, so a
deterministic stub solver stands in for VSPAERO here. Every measured number in
the events still comes from the stub's timings — the test asserts the SHAPE of
the evidence, never fabricates a magnitude.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import workflows.race_study as rs


class _StubSolver:
    """Deterministic stand-in: an L/D curve peaking near alpha 2, cheap timings.

    Records the wing it was handed so tests can pin which parametric anchor
    the lanes raced (None means the curriculum wing)."""

    created: list["_StubSolver"] = []

    def __init__(self, work_root, wing=None):
        self.work_root = Path(work_root)
        self.wing = dict(wing) if wing else None
        self.solve_seconds: list[float] = []
        _StubSolver.created.append(self)

    def solve(self, alpha, re_cref, tag):
        # A concave curve so the quadratic surface has an interior vertex; the
        # Reynolds sample nudges it so MC peaks scatter a little.
        l_d = 18.0 - 0.10 * (alpha - 2.0) ** 2 + (re_cref - 1.0e6) / 1.0e6 * 0.4
        # A representative per-solve cost so the measured core-minutes on both
        # lanes survive rounding — the speedup then reflects the solve counts.
        self.solve_seconds.append(0.5)
        return {"alpha": alpha, "re_cref": re_cref, "cl": 0.5, "cd": 0.03,
                "l_d": l_d, "seconds": 0.5}


def _run(params=None, request="race test", **kw):
    _StubSolver.created = []
    events: list[tuple[str, dict]] = []
    with tempfile.TemporaryDirectory() as tmp:
        with mock.patch.object(rs, "_TimedSolver", _StubSolver), \
             mock.patch.object(rs, "OUT_ROOT", Path(tmp)):
            rc = rs.main(request=request,
                         params={"mc_samples": 3, **(params or {})},
                         emit=lambda e, p=None: events.append((e, p or {})),
                         **kw)
    return rc, events


def _said(events):
    return " ".join(p.get("message", "") for e, p in events
                    if e == "transcript.entry")


class RaceStudyEvents(unittest.TestCase):
    def setUp(self):
        self.rc, self.events = _run(seed=7)
        self.by = {}
        for name, payload in self.events:
            self.by.setdefault(name, []).append(payload)

    def test_completes(self):
        self.assertEqual(self.rc, 0)

    def test_race_init_declares_both_lanes(self):
        init = self.by["race.init"][0]
        keys = {l["key"] for l in init["lanes"]}
        self.assertEqual(keys, {"mc", "rom"})
        # MC total is samples x alphas; ROM is anchors + one confirm.
        totals = {l["key"]: l["total"] for l in init["lanes"]}
        self.assertEqual(totals["mc"], 3 * len(rs.ALPHAS))
        self.assertEqual(totals["rom"], len(rs.ANCHOR_ALPHAS) + 1)

    def test_both_lanes_report_done(self):
        done = {p["lane"] for p in self.by["race.lane"] if p.get("state") == "done"}
        self.assertEqual(done, {"mc", "rom"})

    def test_per_lane_trace_points_stream(self):
        series = {p["series"] for p in self.by["trace.point"]}
        self.assertEqual(series, {"mc", "rom"})
        # The nominal-Reynolds sample is flagged for the running-answer line.
        self.assertTrue(any(p.get("nominal") for p in self.by["trace.point"]
                            if p["series"] == "mc"))
        # ROM emits an anchor set and exactly one confirmation.
        rom_kinds = [p.get("kind") for p in self.by["trace.point"]
                     if p["series"] == "rom"]
        self.assertEqual(rom_kinds.count("confirm"), 1)
        self.assertEqual(rom_kinds.count("anchor"), len(rs.ANCHOR_ALPHAS))

    def test_rom_emits_a_fitted_surface(self):
        curve = self.by["race.curve"][0]
        self.assertEqual(curve["lane"], "rom")
        self.assertEqual(len(curve["coefficients"]), 3)

    def test_result_card_carries_measured_speedup_and_agreement(self):
        result = self.by["race.result"][0]
        self.assertIn("speedup_core_min", result)
        self.assertIn("speedup_wall", result)
        self.assertIn("agreement_pct", result)
        # The MC lane does more solves than the reduced-order lane, so the
        # measured speedup is a real number greater than 1.
        self.assertGreater(result["mc"]["n_solves"], result["rom"]["n_solves"])
        self.assertGreater(result["speedup_core_min"], 1.0)

    def test_verdict_is_solver_backed(self):
        verdict = self.by["result.verdict"][0]
        self.assertEqual(verdict["tier"], "SOLVER-BACKED")

    def test_certificate_is_issued_for_the_race_act(self):
        # Every act must carry a Certonomous certificate; the race's headline
        # results are the measured speedup and the agreement, on the NACA wing.
        self.assertIn("certificate.ready", self.by)
        cert = self.by["certificate.ready"][0]
        # The PDF is written under the (temp) OUT_ROOT the harness cleans up, so
        # assert the target rather than a surviving file.
        self.assertTrue(cert["path"].endswith("certificate.pdf"))
        self.assertEqual(cert["dir"], "race-study")
        self.assertEqual(cert["tier"], "SOLVER-BACKED")
        self.assertTrue(cert.get("certificate_no", "").startswith("C-"))
        # The seal is a 64-hex SHA-256.
        self.assertEqual(len(cert["hash"]), 64)


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


class WordingPins(unittest.TestCase):
    """The owner-reviewed transcript wording, pinned string by string."""

    @classmethod
    def setUpClass(cls):
        cls.rc, cls.events = _run(seed=7)
        cls.said = _said(cls.events)

    def test_mission_finishes_clean(self):
        self.assertEqual(self.rc, 0)

    def test_solver_named_plainly_and_fidelity_framing_gone(self):
        self.assertIn("Both lanes solve with VSPAERO.", self.said)
        self.assertNotIn("Model fidelity", self.said)
        self.assertNotIn("bounds the claim", self.said)

    def test_no_solver_fidelity_reassurance_in_prose(self):
        # The tier chip carries solver status; the transcript never
        # reassures about it in prose.
        lowered = self.said.lower()
        self.assertNotIn("solver-backed", lowered)
        self.assertNotIn("real polar", lowered)
        self.assertNotIn("real solves", lowered)
        self.assertNotIn("the selected solver here", lowered)

    def test_two_ways_sentence_replaces_the_opaque_one(self):
        self.assertIn(
            "Two ways to find one smooth peak: sweep the whole ensemble "
            "with Monte Carlo, or solve in a reduced order space.",
            self.said)
        self.assertNotIn("fit a surface from a few anchor solves", self.said)
        self.assertNotIn("Two admissible methods", self.said)
        self.assertNotIn("brute the ensemble", self.said)
        self.assertNotIn("anchor a surface", self.said)

    def test_staged_delay_disclaimer_removed(self):
        self.assertNotIn("No delays are staged", self.said)

    def test_contrast_line_is_the_numericists_emitted_once(self):
        # Owner cut (2026-07-25): the contrast line moves to the
        # numericist voice, emitted exactly once.
        entries = [(p["role"], p["message"]) for e, p in self.events
                   if e == "transcript.entry"]
        contrast = [(r, m) for r, m in entries
                    if "The Monte-Carlo lane needs all" in m]
        self.assertEqual(len(contrast), 1)
        self.assertEqual(contrast[0][0], "NUMERICIST")

    def test_owner_cut_lines_are_gone(self):
        # Owner cuts (2026-07-25), removed entirely from the transcript.
        self.assertNotIn("envelopes mean different things", self.said)
        self.assertNotIn("Both lanes are live now", self.said)
        self.assertNotIn("Watch the reduced-order lane", self.said)
        self.assertNotIn("Ensemble bracketing the range", self.said)

    def test_speedup_is_stated_in_core_minutes_only(self):
        # Owner cut (2026-07-25): no wall multiplier beside the speedup.
        self.assertIn("in core-minutes.", self.said)
        self.assertNotIn("(wall", self.said)
        report = [p for e, p in self.events if e == "report.ready"][0]
        prose = " ".join(report["abstract"]
                         + [r["value"] for r in report["results"]])
        self.assertIn("core-minutes", prose)
        self.assertNotIn("(wall", prose)

    def test_envelope_contrast_derives_from_configured_counts(self):
        total_mc = 3 * len(rs.ALPHAS)
        total_rom = len(rs.ANCHOR_ALPHAS) + 1
        self.assertIn(
            f"The Monte-Carlo lane needs all {total_mc} solves to reach a "
            f"confidence band this tight; the reduced-order lane gets "
            f"there with {total_rom}.", self.said)

    def test_agreement_sentence_stands_on_confidence_bounds(self):
        result = [p for e, p in self.events if e == "race.result"][0]
        self.assertTrue(
            result["agreement"].startswith("The two paths agree to"))
        self.assertIn("Both within confidence bounds.", result["agreement"])
        self.assertNotIn("fraction of the cost", result["agreement"])

    def test_result_headline_is_just_peak_l_d(self):
        verdict = [p for e, p in self.events if e == "result.verdict"][0]
        self.assertEqual(verdict["quantity"], "Peak L/D")

    def test_lane_chart_titles_stay_neutral(self):
        titles = {p.get("title") for e, p in self.events
                  if e == "trace.point"}
        self.assertIn("Reduced-order: confirmation solve", titles)
        self.assertNotIn("Reduced-order: one real confirmation", titles)
        self.assertNotIn("Full Monte-Carlo: solved polar", titles)

    def test_measured_numbers_flow_through_verbatim(self):
        # The stub curve peaks at exactly L/D 18 at alpha 2; the result card
        # must carry the measured value untouched.
        result = [p for e, p in self.events if e == "race.result"][0]
        self.assertIn("L/D 18.00 at 2°", result["rom"]["peak"])
        self.assertEqual(result["mc"]["n_solves"], 3 * len(rs.ALPHAS))
        self.assertEqual(result["rom"]["n_solves"],
                         len(rs.ANCHOR_ALPHAS) + 1)

    def test_default_race_runs_the_curriculum_wing(self):
        self.assertEqual([s.wing for s in _StubSolver.created], [None, None])


class RacedWingUpload(unittest.TestCase):
    """A surface uploaded with the race prompt is the raced wing."""

    def test_uploaded_surface_is_announced_and_raced(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "naca4412_wing.stl").write_text(_TINY_STL,
                                                         encoding="utf-8")
            with mock.patch.object(rs, "_GEOMETRY_DIR", Path(tmp)):
                rc, events = _run(params={"surface": "naca4412_wing.stl"},
                                  request=None, seed=7)
        said = _said(events)
        self.assertEqual(rc, 0)
        self.assertIn("Wing received: NACA 4412 finite wing", said)
        self.assertIn("Span 40 m measured off the surface", said)
        # The surface lends its span, never its name to the polar.
        self.assertIn("Both lanes race a NACA 4412 section on that span",
                      said)
        # No raw filename on camera.
        self.assertNotIn("naca4412_wing.stl", said)
        # The wing shows through the same geometry path other acts use.
        geo = [p for e, p in events if e == "geometry.ready"]
        self.assertTrue(any("name=naca4412_wing.stl" in (p.get("url") or "")
                            for p in geo))
        self.assertTrue(any("NACA 4412 finite wing" in (p.get("label") or "")
                            for p in geo))
        # Both lanes solved the measured parametric anchor.
        wings = [s.wing for s in _StubSolver.created]
        self.assertEqual(len(wings), 2)
        for wing in wings:
            self.assertEqual(wing["span"], 40.0)
            self.assertEqual(wing["area"], 40.0)
        # The race subject names the wing and states the measurement.
        init = [p for e, p in events if e == "race.init"][0]
        self.assertIn("NACA 4412 finite wing", init["subject"])
        self.assertIn("span 40 m measured", init["subject"])

    def test_unparseable_surface_stays_on_file_reference_raced(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "blob.stl").write_bytes(b"\x00\x01not a surface")
            with mock.patch.object(rs, "_GEOMETRY_DIR", Path(tmp)):
                rc, events = _run(params={"surface": "blob.stl"}, seed=7)
        said = _said(events)
        self.assertEqual(rc, 0)
        self.assertIn("Wing received: Blob", said)
        self.assertIn("The surface is on file and sets nothing here", said)
        # No invented measurement: the lanes race the curriculum wing.
        self.assertEqual([s.wing for s in _StubSolver.created], [None, None])

    def test_race_study_races_with_the_timed_solver(self):
        # Outside the stub, the act must race the benchmark's timed solver,
        # whose contract (reuse_prior=False, wing pass-through) is pinned in
        # test_race_benchmark.TimedSolverContract.
        from workflows import race_benchmark
        self.assertIs(rs._TimedSolver, race_benchmark._TimedSolver)


def _wing_stl(camber: float, *, chord: float = 1.0, span: float = 2.0,
              half_thickness: float = 0.06) -> str:
    """A three-station wing surface with a stated camber, as ASCII STL.

    Deliberately crude: the point is that the camber line and the thickness
    are what they were asked for, so a measurement of the file has a known
    answer to be checked against.
    """
    stations = [(0.0, 0.0, 0.0), (0.5 * chord, camber + half_thickness,
                                  camber - half_thickness),
                (chord, 0.0, 0.0)]
    facets = []

    def facet(a, b, c):
        facets.append("facet normal 0 0 1\n outer loop\n"
                      + "".join(f"  vertex {p[0]:g} {p[1]:g} {p[2]:g}\n"
                                for p in (a, b, c))
                      + " endloop\nendfacet\n")

    for y0, y1 in ((-span / 2, 0.0), (0.0, span / 2)):
        for i in range(len(stations) - 1):
            xa, ua, la = stations[i]
            xb, ub, lb = stations[i + 1]
            for za, zb in ((ua, ub), (la, lb)):
                facet((xa, y0, za), (xb, y0, zb), (xb, y1, zb))
                facet((xa, y0, za), (xb, y1, zb), (xa, y1, za))
    return "solid wing\n" + "".join(facets) + "endsolid wing\n"


class SymmetricSectionPrior(unittest.TestCase):
    """A named symmetric section may not carry lift at α = 0.

    The act used to take a received surface's NAME for the polar while both
    lanes solved the cambered parametric anchor, so a genuine NACA 0012
    arrived and a curve peaking at α = 0 went out under its name. These pin
    the measurement that settles it and the guard that flags it.
    """

    def test_section_measurement_reads_camber_thickness_and_incidence(self):
        from chief_engineer.geometry import measure_section

        with tempfile.TemporaryDirectory() as tmp:
            flat = Path(tmp) / "flat.stl"
            flat.write_text(_wing_stl(0.0), encoding="utf-8")
            bent = Path(tmp) / "bent.stl"
            bent.write_text(_wing_stl(0.04), encoding="utf-8")
            symmetric = measure_section(flat)
            cambered = measure_section(bent)
        self.assertTrue(symmetric["symmetric"])
        self.assertAlmostEqual(symmetric["max_camber_frac_chord"], 0.0,
                               places=6)
        self.assertAlmostEqual(symmetric["max_thickness_frac_chord"], 0.12,
                               places=3)
        self.assertAlmostEqual(symmetric["incidence_deg"], 0.0, places=6)
        self.assertFalse(cambered["symmetric"])
        self.assertAlmostEqual(cambered["max_camber_frac_chord"], 0.04,
                               places=3)
        self.assertAlmostEqual(cambered["max_camber_at_x_over_c"], 0.5,
                               places=1)

    def test_guard_flags_a_symmetric_name_carrying_lift_at_zero(self):
        from chief_engineer.geometry import zero_lift_report

        flagged = zero_lift_report(name="NACA 0012 finite wing", alpha_deg=0.0,
                                   cl=0.2483, camber_frac_chord=0.0398)
        self.assertFalse(flagged["consistent"])
        self.assertIn("cambered", flagged["caveat"])
        # An offset angle reference is the other admissible explanation, and
        # the guard names whichever one the measurement supports.
        offset = zero_lift_report(name="NACA 0012 finite wing", alpha_deg=0.0,
                                  cl=0.2483, camber_frac_chord=0.0,
                                  incidence_deg=2.0)
        self.assertIn("built-in incidence", offset["caveat"])
        # A section that declares camber has nothing to answer for, and an
        # angle away from the zero reference is not the prior's business.
        self.assertIsNone(zero_lift_report(name="NACA 4412 finite wing",
                                           alpha_deg=0.0, cl=0.2483,
                                           camber_frac_chord=0.04))
        self.assertIsNone(zero_lift_report(name="NACA 0012 finite wing",
                                           alpha_deg=3.3, cl=0.5))

    def test_polar_is_never_labelled_with_the_received_surfaces_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "naca0012_wing.stl").write_text(_wing_stl(0.0),
                                                         encoding="utf-8")
            with mock.patch.object(rs, "_GEOMETRY_DIR", Path(tmp)):
                rc, events = _run(params={"surface": "naca0012_wing.stl"},
                                  request=None, seed=7)
        self.assertEqual(rc, 0)
        init = [p for e, p in events if e == "race.init"][0]
        self.assertTrue(init["subject"].startswith("NACA 4412 finite wing"))
        self.assertIn("received NACA 0012 finite wing", init["subject"])
        report = [p for e, p in events if e == "report.ready"][0]
        self.assertIn("NACA 4412", report["title"])
        self.assertNotIn("NACA 0012", report["title"])
        # The setup table states the section and the angle's reference.
        setup = [p for e, p in events if e == "transcript.table"
                 and p.get("table_id") == rs._SETUP_TABLE][0]
        rows = {row[0]: row[1] for row in setup["rows"]}
        self.assertEqual(rows["Raced body"], "NACA 4412 finite wing")
        self.assertIn("camber 4% chord at 0.4 chord", rows["Raced section"])
        self.assertEqual(rows["Angle α reference"],
                         "the raced section's chord line")

    def test_received_section_is_measured_on_camera(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "naca0012_wing.stl").write_text(_wing_stl(0.0),
                                                         encoding="utf-8")
            with mock.patch.object(rs, "_GEOMETRY_DIR", Path(tmp)):
                _, events = _run(params={"surface": "naca0012_wing.stl"},
                                 request=None, seed=7)
        table = [p for e, p in events if e == "transcript.table"
                 and p.get("table_id") == rs._SECTION_TABLE][0]
        rows = {row[0]: (row[1], row[2]) for row in table["rows"]}
        self.assertEqual(rows["Maximum camber"], ("0.00% chord", "4.00% chord"))
        self.assertEqual(rows["Built-in incidence"], ("0.00°", "0.00°"))
        self.assertIn("The received section measures 0.00% camber",
                      _said(events))

    def test_guard_fires_when_the_received_name_claims_symmetry(self):
        # The stub lifts at every angle, so a symmetric received surface and a
        # lifting α = 0 solve are exactly the contradiction that shipped.
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "naca0012_wing.stl").write_text(_wing_stl(0.0),
                                                         encoding="utf-8")
            with mock.patch.object(rs, "_GEOMETRY_DIR", Path(tmp)):
                _, events = _run(params={"surface": "naca0012_wing.stl"},
                                 request=None, seed=7)
        guards = [p for e, p in events if e == "physics.guard"]
        self.assertTrue(guards)
        flagged = [g for g in guards if not g["consistent"]]
        self.assertEqual([g["name"] for g in flagged],
                         ["NACA 0012 finite wing"])
        self.assertTrue(flagged[0]["measured_symmetric"])
        self.assertIn("cannot belong to this surface", _said(events))

    def test_guard_stays_silent_when_no_name_claims_symmetry(self):
        # The raced section declares its camber, so the prior has no opinion
        # and the act says nothing rather than reassuring about a clean check.
        _, events = _run(seed=7)
        self.assertEqual([p for e, p in events if e == "physics.guard"], [])
        self.assertNotIn("symmetric section", _said(events))


class ReportTabIsPopulated(unittest.TestCase):
    """The exported report renders abstract, methods, uncertainty and next.

    The act used to emit title, subject, summary and an empty figure list.
    The report view reads none of those last three, so every heading in the
    export came out empty while the digest beside it was full, and the
    certificate links from that page.
    """

    @classmethod
    def setUpClass(cls):
        cls.rc, cls.events = _run(seed=7)
        cls.report = [p for e, p in cls.events if e == "report.ready"][0]

    def test_every_section_the_view_renders_carries_content(self):
        for section in ("abstract", "methods", "uncertainty",
                        "next_investigations", "results"):
            self.assertTrue(self.report.get(section),
                            f"{section} ships empty into the report tab")
        self.assertTrue(self.report.get("title"))

    def test_results_carry_a_value_an_envelope_and_a_chip(self):
        headline = self.report["results"][0]
        self.assertIn("Peak lift-to-drag", headline["quantity"])
        self.assertIn("18", headline["value"])
        self.assertIn("95%", headline["envelope"])
        self.assertEqual(headline["tier"], "SOLVER-BACKED")

    def test_methods_state_the_section_and_the_angle_reference(self):
        methods = " ".join(self.report["methods"])
        self.assertIn("NACA 4412 finite wing", methods)
        self.assertIn("camber 4% of chord at 0.4 chord", methods)
        self.assertIn("measured from that section's own chord line", methods)

    def test_uncertainty_carries_the_channel_notes_and_the_composition(self):
        lines = " ".join(self.report["uncertainty"])
        self.assertIn("Ensemble run over the stated spread", lines)
        self.assertIn("root sum of squares", lines)

    def test_boundary_claim_follows_the_located_peak(self):
        # The stub peaks at alpha 2, inside the swept range, so the act must
        # not repeat the boundary sentence it was filmed saying.
        rom_peak = [p for e, p in self.events if e == "race.curve"][0]
        self.assertNotIn(rom_peak["alpha_star"], (rs.ALPHAS[0], rs.ALPHAS[-1]))
        lines = " ".join(self.report["uncertainty"]
                         + self.report["next_investigations"])
        self.assertIn("sits inside the swept range", lines)
        self.assertNotIn("edge of the range", lines)
        self.assertNotIn("Sweep from", lines)
        self.assertNotIn("edge of the range", _said(self.events))

    def test_next_investigations_are_the_emitted_agenda(self):
        agenda = [p for e, p in self.events if e == "agenda.updated"][0]
        self.assertEqual(
            self.report["next_investigations"],
            [f"{e['title']}: {e['scope']}" for e in agenda["entries"]])


class RaceCertificateConvention(unittest.TestCase):
    """The uniform certificate convention on the race act: three computed
    channels, the structured result table, the verbatim objective, no mesh
    block, and generic channel notes on the sealed page."""

    REQUEST = "race the two paths on the NACA 4412 wing tonight"

    @classmethod
    def setUpClass(cls):
        _StubSolver.created = []
        cls.events = []
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(rs, "_TimedSolver", _StubSolver), \
                 mock.patch.object(rs, "OUT_ROOT", Path(tmp)):
                cls.rc = rs.main(
                    request=cls.REQUEST, params={"mc_samples": 3},
                    emit=lambda e, p=None: cls.events.append((e, p or {})),
                    seed=7)
                cert = [p for e, p in cls.events
                        if e == "certificate.ready"][0]
                cls.text = Path(cert["path"]).read_bytes().decode("latin-1")

    def _channels(self):
        payloads = [p for e, p in self.events if e == "uncertainty.channels"]
        self.assertEqual(len(payloads), 1)
        return {c["name"]: c for c in payloads[0]["channels"]}

    def test_all_three_channels_are_computed_numbers(self):
        by = self._channels()
        for name in ("input", "numerical", "model"):
            self.assertTrue(by[name]["quantified"], name)
            self.assertIsNotNone(by[name]["value"], name)

    def test_numerical_is_the_half_step_bracket_from_the_lane_data(self):
        # The stub curve is exactly quadratic (peak at alpha 2), so the
        # anchor fit reproduces it and the half-step bracket is
        # |f(2 ± 0.5) - f(2)| = 0.1 * 0.25 = 0.025. Measured, not invented.
        by = self._channels()
        self.assertAlmostEqual(by["numerical"]["value"], 0.025, places=6)
        self.assertIn("discrete angle grid", by["numerical"]["note"])
        self.assertIn("half a grid step", by["numerical"]["note"])

    def test_model_channel_is_the_measured_cross_path_agreement(self):
        by = self._channels()
        result = [p for e, p in self.events if e == "race.result"][0]
        mc_peak = float(result["mc"]["peak"].split()[1])
        self.assertAlmostEqual(by["model"]["value"],
                               round(abs(mc_peak - 18.00), 3), places=3)
        self.assertIn("Measured agreement between the two independent "
                      "solve paths", by["model"]["note"])
        self.assertIn("confirmation solve", by["model"]["note"])

    def test_headline_band_composes_every_quantified_channel(self):
        # The banner used to publish the input channel alone, which on the
        # filmed inputs was the SMALLEST of three numbers in the same panel.
        # It is now the root sum of squares over the quantified channels,
        # through the same call the rest of the lab closes its acts with.
        import math

        from chief_engineer import uq

        by = self._channels()
        expected = math.sqrt(sum(c["value"] ** 2 for c in by.values()))
        self.assertAlmostEqual(
            expected,
            uq.combine_expanded(input_2sigma=by["input"]["value"],
                                numerical_abs=by["numerical"]["value"],
                                model_abs=by["model"]["value"])["combined_95"],
            places=9)
        verdict = [p for e, p in self.events if e == "result.verdict"][0]
        self.assertAlmostEqual(float(verdict["ci"]), expected, places=2)
        self.assertEqual(verdict["confidence"], "95%")
        # Strictly larger than any one channel: a composition, not a pick.
        for channel in by.values():
            self.assertGreater(float(verdict["ci"]), channel["value"])
        # The certificate publishes the same composed band, and states the
        # ensemble spread beside it rather than in place of it.
        self.assertIn(f"+-{expected:.2f}".replace("+-", ""), self.text)
        self.assertIn("Ensemble Spread", self.text)

    def test_agreement_table_separates_lane_spread_from_published_band(self):
        table = [p for e, p in self.events if e == "transcript.table"
                 and p.get("table_id") == rs._AGREE_TABLE][0]
        rows = {row[0]: row for row in table["rows"]}
        verdict = [p for e, p in self.events if e == "result.verdict"][0]
        self.assertEqual(rows["Published band (95%)"][3],
                         f"±{float(verdict['ci']):.2f}")
        # The Monte Carlo column still carries that lane's own spread.
        self.assertIn("±", rows["Peak L/D"][1])

    def test_notes_stay_on_the_generic_register(self):
        blob = " ".join(str(c["note"]) for c in self._channels().values())
        for banned in ("Monte-Carlo", "quadrature", "Eca", "Hoekstra", "GCI",
                       "least-squares", "uq-"):
            self.assertNotIn(banned, blob)
        self.assertIn("Ensemble run", blob)

    def test_certificate_carries_result_table_and_verbatim_objective(self):
        for token in ("Parameter", "Peak L/D", "18.00 at 2 deg",
                      "Band \\(95%\\)", "Agreement", "Speedup",
                      "Solver Runs", "Cost", self.REQUEST):
            self.assertIn(token, self.text)
        # No mesh block on a meshless act; no method names on the sealed page.
        self.assertNotIn("Mesh Validity", self.text)
        # Owner cut (2026-07-25): the speedup is core-minutes only.
        self.assertNotIn("x wall", self.text)
        self.assertNotIn("wall ", self.text)
        for banned in ("Monte-Carlo", "quadrature", "Eca", "Hoekstra",
                       "GCI", "least-squares"):
            self.assertNotIn(banned, self.text)


class RaceStudyConfig(unittest.TestCase):
    def test_worker_cap_is_four(self):
        self.assertEqual(rs.MAX_WORKERS, 4)

    def test_mc_reynolds_leads_with_the_nominal(self):
        res = rs._mc_reynolds(4, seed=1)
        self.assertEqual(res[0], rs.RE_NOMINAL)
        self.assertEqual(len(res), 4)


if __name__ == "__main__":
    unittest.main()
