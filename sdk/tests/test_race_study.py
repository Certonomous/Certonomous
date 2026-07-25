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
            "with Monte Carlo, or fit a surface from a few anchor solves.",
            self.said)
        self.assertNotIn("Two admissible methods", self.said)
        self.assertNotIn("brute the ensemble", self.said)
        self.assertNotIn("anchor a surface", self.said)

    def test_staged_delay_disclaimer_removed(self):
        self.assertNotIn("No delays are staged", self.said)

    def test_contrast_bullet_rides_in_the_same_emitted_entry(self):
        # Owner rule: bullets are rows within ONE emitted entry, never a
        # separate entry per bullet.
        entries = [p["message"] for e, p in self.events
                   if e == "transcript.entry"]
        watch = [m for m in entries if "Watch the reduced-order lane" in m]
        self.assertEqual(len(watch), 1)
        self.assertIn("The Monte-Carlo lane needs all", watch[0])

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
        self.assertIn("Raced wing received: NACA 4412 finite wing", said)
        self.assertIn("Span 40 m measured from the surface bounding box",
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
        self.assertIn("Raced wing received: Blob", said)
        self.assertIn("on file as the reference shape", said)
        # No invented measurement: the lanes race the curriculum wing.
        self.assertEqual([s.wing for s in _StubSolver.created], [None, None])

    def test_race_study_races_with_the_timed_solver(self):
        # Outside the stub, the act must race the benchmark's timed solver,
        # whose contract (reuse_prior=False, wing pass-through) is pinned in
        # test_race_benchmark.TimedSolverContract.
        from workflows import race_benchmark
        self.assertIs(rs._TimedSolver, race_benchmark._TimedSolver)


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
