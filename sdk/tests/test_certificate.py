"""The Certonomous Certificate: seal integrity and PDF well-formedness."""

import tempfile
import unittest
from pathlib import Path

from chief_engineer.certificate import (build_certificate,
                                        build_certificate_v2, display_name_for,
                                        evidence_hash, _seal_payload)


def _report():
    return {
        "title": "Geometry study - widget",
        "results": [
            {"quantity": "Drag coefficient", "value": "0.0471",
             "envelope": "±0.0013", "tier": "TREND ONLY",
             "reason": "one mesh, no experimental comparison"},
            {"quantity": "Mesh", "value": "193,880 cells",
             "envelope": "skewness 8.9", "tier": "TREND ONLY", "reason": "gate"},
        ],
        "uncertainty": ["A floor, not a bound.", "Numerical not quantified.",
                        "No experimental comparison."],
        "compute": {"cells": 193880, "core_minutes": 8.2, "full_fidelity": True},
    }


_CHANNELS = [
    {"name": "Input / aleatory", "value": "±2.7%", "quantified": True,
     "note": "propagated 2-sigma"},
    {"name": "Numerical", "value": None, "quantified": False, "note": "one mesh"},
    {"name": "Model-form", "value": None, "quantified": False, "note": "closure"},
]

_KW = dict(geometry="widget", objective="Measure drag.",
           mission_id="geometry-study-widget", issued_utc="2026-07-20T00:00:00Z")


class SealTests(unittest.TestCase):
    def test_hash_is_deterministic(self):
        payload = _seal_payload(results=_report()["results"], channels=_CHANNELS,
                                compute=_report()["compute"], **_KW)
        self.assertEqual(evidence_hash(payload), evidence_hash(payload))
        self.assertEqual(len(evidence_hash(payload)), 64)

    def test_hash_changes_when_a_recorded_number_changes(self):
        base = _seal_payload(results=_report()["results"], channels=_CHANNELS,
                             compute=_report()["compute"], **_KW)
        tampered_results = [dict(r) for r in _report()["results"]]
        tampered_results[0]["value"] = "0.9999"
        tampered = _seal_payload(results=tampered_results, channels=_CHANNELS,
                                 compute=_report()["compute"], **_KW)
        self.assertNotEqual(evidence_hash(base), evidence_hash(tampered))

    def test_hash_ignores_cosmetic_report_fields(self):
        # abstract/methods/future_work are not part of the seal.
        r1, r2 = _report(), _report()
        r2["abstract"] = ["totally different prose"]
        p1 = _seal_payload(results=r1["results"], channels=_CHANNELS,
                           compute=r1["compute"], **_KW)
        p2 = _seal_payload(results=r2["results"], channels=_CHANNELS,
                           compute=r2["compute"], **_KW)
        self.assertEqual(evidence_hash(p1), evidence_hash(p2))


class PdfTests(unittest.TestCase):
    def _build(self, report=None, channels=_CHANNELS):
        tmp = Path(tempfile.mkdtemp()) / "certificate.pdf"
        return build_certificate(report or _report(), out_path=tmp,
                                 channels=channels, **_KW)

    def test_writes_a_wellformed_pdf(self):
        out = self._build()
        data = Path(out["path"]).read_bytes()
        self.assertTrue(data.startswith(b"%PDF-1."))
        self.assertTrue(data.rstrip().endswith(b"%%EOF"))
        self.assertIn(b"/Type /Page", data)
        self.assertIn(b"xref", data)

    def test_return_record_carries_seal_and_tier(self):
        out = self._build()
        self.assertEqual(len(out["hash"]), 64)
        self.assertEqual(out["tier"], "TREND ONLY")
        self.assertEqual(out["mission_id"], "geometry-study-widget")

    def test_tier_selects_the_right_badge_colour(self):
        from chief_engineer.certificate import _TIER_COLOR
        self.assertIn("VALIDATED", _TIER_COLOR)
        self.assertIn("TREND ONLY", _TIER_COLOR)
        self.assertNotEqual(_TIER_COLOR["VALIDATED"], _TIER_COLOR["TREND ONLY"])

    def test_falls_back_to_plain_uncertainty_without_channels(self):
        out = self._build(channels=None)
        self.assertTrue(Path(out["path"]).exists())
        self.assertGreater(Path(out["path"]).stat().st_size, 1000)

    def test_accepts_uncertainty_channels_dict_shape(self):
        # lab.uncertainty_channels() returns {"channels": [...]}, not a bare list.
        out = self._build(channels={"channels": _CHANNELS})
        self.assertTrue(Path(out["path"]).read_bytes().startswith(b"%PDF"))

    def test_math_glyphs_do_not_crash_layout(self):
        report = _report()
        report["results"][0]["reason"] = "within ±5%, Re ≈ 270, ≥ threshold"
        out = self._build(report)
        self.assertTrue(Path(out["path"]).read_bytes().startswith(b"%PDF"))


class RedesignV2Tests(unittest.TestCase):
    def _build_v2(self, **kw):
        with tempfile.TemporaryDirectory() as d:
            out = build_certificate_v2(
                _report(), out_path=Path(d) / "c.pdf", channels=_CHANNELS,
                display_name="B-52 Stratofortress-class airframe",
                source_filename="b52.stl", solver="simpleFoam k-omega SST", **{**_KW, **kw})
            return out, Path(out["path"]).read_bytes()

    def test_v2_renders_valid_pdf_and_seal_matches_default(self):
        out, data = self._build_v2()
        self.assertTrue(data.startswith(b"%PDF"))
        self.assertTrue(data.rstrip().endswith(b"%%EOF"))
        # The seal covers the same facts, so it must equal the default cert's.
        with tempfile.TemporaryDirectory() as d:
            old = build_certificate(_report(), out_path=Path(d) / "o.pdf",
                                    channels=_CHANNELS, **_KW)
        self.assertEqual(out["hash"], old["hash"])

    def test_v2_has_human_certificate_number_not_slug(self):
        out, _ = self._build_v2()
        self.assertRegex(out["certificate_no"], r"^C-\d{4}-\d{4}$")
        self.assertNotEqual(out["certificate_no"], _KW["mission_id"])

    def test_v2_fidelity_chip(self):
        out, _ = self._build_v2()
        self.assertIn(out["fidelity"],
                      {"VALIDATED", "SOLVER-BACKED", "RESEARCH MODEL"})

    def test_display_name_fallback(self):
        self.assertEqual(display_name_for("b52"),
                         "B-52 Stratofortress-class airframe")
        self.assertEqual(display_name_for("b52", "Explicit name"), "Explicit name")


class GeometryStudyCertificateTests(unittest.TestCase):
    """Owner directives: all three V&V-20 channels on the geometry-study
    certificate, the mission's real checkMesh numbers with their gate verdicts,
    and none of the banned vocabulary in the rendered text."""

    def _render(self, report=None, channels=_CHANNELS, mesh=None, **kw):
        with tempfile.TemporaryDirectory() as d:
            out = build_certificate_v2(
                report or _report(), out_path=Path(d) / "c.pdf",
                channels=channels, mesh=mesh, **{**_KW, **kw})
            text = Path(out["path"]).read_bytes().decode("latin-1")
            return out, text

    def test_three_channels_on_a_geometry_study_certificate(self):
        from workflows.geometry_study import certificate_channels
        lookup = {"numerical": {"band_abs": 0.00303,
                                "method": "3-mesh ladder (r = 1.22), observed "
                                          "order p = 2.10; GCI band, Fs = 1.25"},
                  "model": None, "pending": False,
                  "provenance": ["uq-b52-r1", "uq-b52-r2", "uq-b52-r3"]}
        channels = certificate_channels(
            settle_2sigma=0.0026, window=60, velocity=20.0, lookup=lookup,
            cells=193880, non_ortho_s="65.2°", skew_s="3.20")
        self.assertEqual([c["name"] for c in channels["channels"]],
                         ["input", "numerical", "model"])
        inp, num, mod = channels["channels"]
        # Input: the freestream envelope, honestly unquantified, never a
        # borrowed number. Numerical: the refinement band plus the REAL
        # mesh-check numbers. Model: k-omega SST, stated model-form.
        self.assertFalse(inp["quantified"])
        self.assertIsNone(inp["value"])
        self.assertTrue(num["quantified"])
        self.assertEqual(num["value"], 0.00303)
        self.assertIn("Grid-refinement study", num["note"])
        self.assertFalse(mod["quantified"])
        self.assertIn("k-omega SST", mod["note"])
        _, text = self._render(channels=channels)
        self.assertTrue(text.startswith("%PDF"))
        for token in ("input", "numerical", "model", "not quantified",
                      "0.00303"):
            self.assertIn(token, text)
        # Render rails: internal study slugs and tool names never reach the page.
        self.assertNotIn("uq-b52", text)
        self.assertNotIn("checkMesh", text)

    def test_model_channel_carries_the_published_band_comparison(self):
        from workflows.geometry_study import certificate_channels
        channels = certificate_channels(
            settle_2sigma=0.0011, window=60, velocity=20.0,
            lookup={"numerical": {"band_abs": 0.0019,
                                  "method": "3-mesh study (r = 1.75)"},
                    "model": {"band_abs": 0.0018,
                              "method": "inter-closure spread "
                                        "(screening estimate)"},
                    "pending": False, "provenance": ["m-1"]},
            cells=353578, non_ortho_s="65.2°", skew_s="3.20",
            model_extra="drag area 0.31 m² inside the published "
                        "motorcycle-with-rider band (Cossalter 2006; "
                        "Hoerner 1965)")
        mod = channels["channels"][2]
        self.assertTrue(mod["quantified"])
        self.assertIn("drag area 0.31 m²", mod["note"])
        self.assertIn("Cossalter 2006", mod["note"])

    def test_pending_study_states_status_and_invents_nothing(self):
        from workflows.geometry_study import certificate_channels
        channels = certificate_channels(
            settle_2sigma=0.004, window=60, velocity=100.0,
            lookup={"numerical": None, "model": None, "pending": True,
                    "provenance": []},
            cells=50000, non_ortho_s="61.0°", skew_s="2.10")
        inp, num, mod = channels["channels"]
        self.assertFalse(num["quantified"])
        self.assertIsNone(num["value"])
        self.assertIn("study pending", num["note"])
        self.assertFalse(mod["quantified"])

    def test_mesh_validity_block_carries_real_checkmesh_numbers(self):
        from workflows.geometry_study import mesh_validity
        mesh = mesh_validity(193880, 65.2, 8.9)
        out, text = self._render(mesh=mesh)
        self.assertIn("Mesh Validity", text)
        self.assertIn("193,880", text)
        self.assertIn("65.2\xb0 vs 70\xb0 gate", text)
        self.assertIn("8.90 vs 4.0 guidance", text)
        self.assertIn("pass", text)      # non-orthogonality inside its gate
        self.assertIn("caveat", text)    # skewness above the guidance
        # The mesh facts are sealed with the run: the hash must move.
        base, _ = self._render()
        self.assertNotEqual(out["hash"], base["hash"])

    def test_banned_language_never_renders(self):
        report = {
            "results": [
                {"quantity": "Drag coefficient", "value": "0.0471",
                 "envelope": "±0.0013", "tier": "TREND ONLY",
                 "reason": "cached, stored, saved, recorded, pre-computed "
                           "from a real solve — TREND"},
            ],
            "uncertainty": [],
            "compute": {"cells": 1000, "core_minutes": 1.0},
        }
        _, text = self._render(report=report,
                               objective="measure drag — precisely")
        self.assertTrue(text.startswith("%PDF"))
        for banned in ("\x97",           # em dash in WinAnsi
                       "cached", "stored", "saved", "recorded",
                       "pre-computed", "real solve", "TREND",
                       "reproducible evidence"):
            self.assertNotIn(banned, text)


class RenderRailTests(unittest.TestCase):
    """Owner review rails: Title Case section headers, no internal study
    slugs, no tool names on the uncertainty channels, the plain input-channel
    sentence, and every surviving number rendered verbatim."""

    def _render(self, channels=_CHANNELS, mesh=None, report=None, **kw):
        with tempfile.TemporaryDirectory() as d:
            out = build_certificate_v2(
                report or _report(), out_path=Path(d) / "c.pdf",
                channels=channels, mesh=mesh, **{**_KW, **kw})
            return out, Path(out["path"]).read_bytes().decode("latin-1")

    def test_section_headers_are_title_case_not_shouted(self):
        mesh = {"cells": 193880, "max_non_orthogonality": 65.2,
                "max_skewness": 3.2}
        _, text = self._render(mesh=mesh)
        for header in ("Certificate of Autonomous Solve", "Certificate No.",
                       "Subject", "Result", "Uncertainty", "Channel", "Value",
                       "State", "Mesh Validity", "Evidence Seal"):
            self.assertIn(header, text)
        for shouted in ("UNCERTAINTY", "MESH VALIDITY", "CHECKMESH", "SUBJECT",
                        "RESULT", "CHANNEL", "PROVENANCE", "EVIDENCE-BUNDLE",
                        "CERTIFICATE OF AUTONOMOUS SOLVE", "CERTIFICATE No."):
            self.assertNotIn(shouted, text)

    def test_uq_study_slugs_never_render(self):
        channels = [{"name": "numerical", "value": 0.00303, "quantified": True,
                     "note": "3-mesh ladder (r = 1.22), observed order "
                             "p = 2.10; GCI band, Fs = 1.25; study uq-b52-r1, "
                             "uq-b52-r2, uq-b52-r3"}]
        _, text = self._render(channels=channels)
        self.assertNotIn("uq-b52", text)
        self.assertNotIn("study uq-", text)
        # every number around the deleted reference survives verbatim
        for kept in ("0.00303", "1.22", "2.10", "1.25"):
            self.assertIn(kept, text)

    def test_checkmesh_dropped_from_channels_numbers_kept(self):
        channels = [{"name": "numerical", "value": 0.003, "quantified": True,
                     "note": "mesh discretization; checkMesh: 193,880 cells, "
                             "max non-orthogonality 65.2° vs the 70° "
                             "gate, max skewness 3.20 vs the 4.0 guidance"}]
        _, text = self._render(channels=channels)
        self.assertNotIn("checkMesh", text)
        self.assertNotIn("CHECKMESH", text)
        for kept in ("193,880", "65.2", "70", "3.20", "4.0"):
            self.assertIn(kept, text)

    def test_mesh_block_never_names_the_tool(self):
        # A mesh record with unreported values renders "not reported by the
        # mesh check", never the tool name.
        _, text = self._render(mesh={"cells": 5000})
        self.assertIn("Mesh Validity", text)
        self.assertIn("not reported by the mesh check", text)
        self.assertNotIn("checkMesh", text)

    def test_input_channel_renders_the_plain_sentence(self):
        note = ("freestream conditions envelope: speed 20 m/s and fluid "
                "properties are taken as specified exactly, so no input "
                "spread was propagated; the result's ±0.0026 band over "
                "the final 60 iterations is settled-state scatter, carried "
                "on the result line; stated, not quantified")
        channels = [{"name": "input", "value": None, "quantified": False,
                     "note": note},
                    {"name": "numerical", "value": 0.001, "quantified": True,
                     "note": "refinement band"}]
        _, text = self._render(channels=channels)
        self.assertIn("No input uncertainty was assumed for this problem.", text)
        self.assertNotIn("as specified exactly", text)
        self.assertNotIn("freestream conditions envelope", text)

    def test_input_sentence_passes_through_unchanged(self):
        channels = [{"name": "input", "value": None, "quantified": False,
                     "note": "No input uncertainty was assumed for this "
                             "problem."}]
        _, text = self._render(channels=channels)
        self.assertIn("No input uncertainty was assumed for this problem.", text)

    def test_quantified_input_channel_is_not_replaced(self):
        # A genuinely quantified input channel keeps its note and its number.
        # Notes render one sentence per line, first letter capitalized.
        _, text = self._render(channels=_CHANNELS)
        self.assertIn("Propagated 2-sigma", text)
        self.assertIn("2.7%", text)
        self.assertNotIn("No input uncertainty was assumed", text)

    def test_rails_delete_jargon_but_never_touch_a_number(self):
        from chief_engineer.certificate import _channel_rails
        railed = _channel_rails("GCI band 0.00303, Fs = 1.25; study uq-b52-r1, "
                                "uq-b52-r2, uq-b52-r3")
        self.assertEqual(railed, "grid-refinement band 0.00303, Fs = 1.25")
        self.assertEqual(_channel_rails("mesh discretization; checkMesh: "
                                        "193,880 cells"),
                         "mesh discretization; 193,880 cells")

    def test_rails_fold_named_methods_to_the_generic_register(self):
        # Owner rule (2026-07-24): the sealed page never states a UQ method
        # by name. The rails fold names to the generic register and delete
        # citations; every measured number survives verbatim.
        from chief_engineer.certificate import _channel_rails
        self.assertEqual(
            _channel_rails("Band ±0.003 on the drag coefficient, "
                           "least-squares fit with safety factor 1.25 "
                           "(Eca & Hoekstra 2014)"),
            "Band ±0.003 on the drag coefficient, default numerical "
            "consistency method with safety factor 1.25")
        self.assertEqual(
            _channel_rails("2-sigma Monte-Carlo envelope, ±421.14 Pa"),
            "2-sigma ensemble envelope, ±421.14 Pa")
        self.assertEqual(
            _channel_rails("phase-quadrature ladder k = 3/5/9"),
            "multi-level refinement of the cycle evaluation")

    def test_banned_method_names_never_render_in_a_channel_note(self):
        channels = [
            {"name": "input", "value": 421.14, "quantified": True,
             "note": "2-sigma Monte-Carlo envelope propagated from the "
                     "stated spreads"},
            {"name": "numerical", "value": 81.0, "quantified": True,
             "note": "phase-quadrature ladder k = 3/5/9"},
            {"name": "model", "value": 0.003, "quantified": True,
             "note": "GCI band, least-squares fit (Eca & Hoekstra 2014)"},
        ]
        _, text = self._render(channels=channels)
        for banned in ("Monte-Carlo", "quadrature", "Eca", "Hoekstra",
                       "least-squares", "GCI", "3/5/9"):
            self.assertNotIn(banned, text)
        # Every measured value still renders verbatim.
        for kept in ("421.14", "81.0", "0.003"):
            self.assertIn(kept, text)

    def test_meshless_certificate_renders_no_mesh_block(self):
        # Acts without a mesh (reduced-order valve, panel-code airliner,
        # race) must not render an empty Mesh Validity block.
        _, text = self._render(mesh=None)
        self.assertNotIn("Mesh Validity", text)

    def test_no_em_dash_or_double_hyphen_on_the_page(self):
        _, text = self._render(mesh={"cells": 1000},
                               objective="measure drag — precisely")
        self.assertNotIn("\x97", text)   # WinAnsi em dash
        self.assertNotIn("--", text)
        # headline numbers rendered verbatim
        self.assertIn("0.0471", text)
        self.assertIn("0.0013", text)


class ResultFieldsTests(unittest.TestCase):
    """Structured result support: ordered label/value pairs render as a
    Parameter | Value table, sealed with the run; acts without them keep the
    sentence fallback (covered by the seal-parity test above)."""

    FIELDS = [("Span", "64 m"), ("AR", "13.7"), ("MTOW", "146 t"),
              ("Range", "9838 km"), ("Approach Speed", "66 m/s"),
              ("L/D", "18.5")]

    def _render(self, result_fields=None):
        report = _report()
        if result_fields is not None:
            report["result_fields"] = result_fields
        with tempfile.TemporaryDirectory() as d:
            out = build_certificate_v2(report, out_path=Path(d) / "c.pdf",
                                       channels=_CHANNELS, **_KW)
            return out, Path(out["path"]).read_bytes().decode("latin-1")

    def test_result_fields_render_as_a_two_column_table(self):
        _, text = self._render(self.FIELDS)
        self.assertIn("Parameter", text)
        for label, value in self.FIELDS:
            self.assertIn(label, text)
            self.assertIn(value, text)

    def test_labels_and_values_render_verbatim_never_recased(self):
        _, text = self._render([("AR", "13.7"), ("L/D", "18.5")])
        self.assertIn("AR", text)
        self.assertIn("L/D", text)
        self.assertNotIn("Ar", text.replace("Parameter", ""))

    def test_result_fields_are_sealed_with_the_run(self):
        with_fields, _ = self._render(self.FIELDS)
        without, _ = self._render(None)
        self.assertNotEqual(with_fields["hash"], without["hash"])
        tampered = [list(pair) for pair in self.FIELDS]
        tampered[0][1] = "65 m"
        other, _ = self._render(tampered)
        self.assertNotEqual(with_fields["hash"], other["hash"])

    def test_dict_shaped_fields_are_accepted(self):
        _, text = self._render([{"label": "Span", "value": "64 m"}])
        self.assertIn("Span", text)
        self.assertIn("64 m", text)


class AtomicWriteTests(unittest.TestCase):
    """The served path always holds a complete page: staging file swapped in,
    never left behind, and a rebuild replaces the page in one step."""

    def test_no_staging_file_remains_and_rebuild_replaces(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "certificate.pdf"
            first = build_certificate_v2(_report(), out_path=path,
                                         channels=_CHANNELS, **_KW)
            self.assertTrue(path.exists())
            leftovers = [p.name for p in Path(d).iterdir() if p.name != path.name]
            self.assertEqual(leftovers, [])
            second_kw = {**_KW, "objective": "Measure lift instead."}
            build_certificate_v2(_report(), out_path=path,
                                 channels=_CHANNELS, **second_kw)
            text = path.read_bytes().decode("latin-1")
            self.assertIn("Measure lift instead.", text)
            self.assertNotIn("Measure drag.", text)
            self.assertTrue(Path(first["path"]).samefile(path))


class ChannelNoteLineTests(unittest.TestCase):
    """A channel note that joins several sentences or bullets inline renders
    one per line, each starting with a capital letter, numbers verbatim."""

    def test_note_lines_split_on_sentences_and_bullets(self):
        from chief_engineer.certificate import _note_lines
        self.assertEqual(
            _note_lines("• the band is ±0.44. the read adds ±0.07."),
            ["The band is ±0.44.", "The read adds ±0.07."])
        self.assertEqual(
            _note_lines("Band ±0.003 (Eca & Hoekstra 2014)."),
            ["Band ±0.003 (Eca & Hoekstra 2014)."])

    def test_semicolon_clauses_stay_on_one_line(self):
        from chief_engineer.certificate import _note_lines
        note = "inside the published band (Cossalter 2006; Hoerner 1965)"
        self.assertEqual(_note_lines(note),
                         ["Inside the published band "
                          "(Cossalter 2006; Hoerner 1965)"])


class ScopeConstraintsAndLedgerTests(unittest.TestCase):
    """The three fields a certificate needs to be read on its own: what the
    run actually covered, every limit it applied and where each came from, and
    every number it assumed because nothing else supplied one."""

    CONSTRAINTS = [("Passengers", "300", "user-stated"),
                   ("Landing speed", "at most 70 m/s", "assumed"),
                   ("ICAO gate code", "Code E, span at most 65 m",
                    "advisory, re-run offer open")]
    ASSUMED = [("CLmax, landing", "2.6", "assumed, not solver-derived"),
               ("CLmax, take-off", "2.1", "assumed, not solver-derived")]
    SCOPE = ("Wing-optimized; fuselage, tail, and nacelle drag from Raymer's "
             "component buildup. Result is whole-aircraft L/D.")

    def _render(self, **kw):
        with tempfile.TemporaryDirectory() as d:
            out = build_certificate_v2(_report(), out_path=Path(d) / "c.pdf",
                                       channels=_CHANNELS, **_KW, **kw)
            return out, Path(out["path"]).read_bytes().decode("latin-1")

    def test_scope_is_a_labelled_field_not_fine_print(self):
        _, text = self._render(scope=self.SCOPE)
        self.assertIn("Scope", text)
        self.assertIn("Result is whole-aircraft L/D.", text)

    def test_scope_sits_between_the_objective_and_the_solver(self):
        _, text = self._render(scope=self.SCOPE, solver="simpleFoam")
        self.assertLess(text.index("(Objective)"), text.index("(Scope)"))
        self.assertLess(text.index("(Scope)"), text.index("(Solver & Model)"))

    def test_a_caller_that_names_no_solver_gets_no_solver_line(self):
        # The field used to draw "Not stated", which asserts an absence
        # instead of leaving the line off. An act that deliberately carries
        # no solver-and-model line then carried one anyway.
        _, text = self._render(scope=self.SCOPE)
        self.assertNotIn("Solver & Model", text)
        self.assertNotIn("Not stated", text)
        named, text = self._render(scope=self.SCOPE, solver="simpleFoam")
        self.assertIn("Solver & Model", text)

    def test_every_constraint_carries_the_tag_it_came_with(self):
        _, text = self._render(constraints=self.CONSTRAINTS)
        self.assertIn("Constraints", text)
        for name, value, tag in self.CONSTRAINTS:
            self.assertIn(name, text)
            self.assertIn(value, text)
            self.assertIn(tag, text)

    def test_the_advisory_carries_its_disposition_not_just_its_existence(self):
        _, text = self._render(constraints=self.CONSTRAINTS)
        self.assertIn("advisory, re-run offer open", text)

    def test_the_ledger_marks_a_value_no_solver_produced(self):
        _, text = self._render(assumptions=self.ASSUMED)
        self.assertIn("Assumed Values", text)
        self.assertIn("CLmax, landing", text)
        self.assertIn("assumed, not solver-derived", text)

    def test_constraints_and_ledger_precede_the_result(self):
        _, text = self._render(constraints=self.CONSTRAINTS,
                               assumptions=self.ASSUMED)
        self.assertLess(text.index("(Constraints)"), text.index("(Assumed Values)"))
        self.assertLess(text.index("(Assumed Values)"), text.index("(Result)"))

    def test_issuance_and_the_seal_sit_together_at_the_foot(self):
        _, text = self._render(scope=self.SCOPE)
        self.assertLess(text.index("(Result)"), text.index("(Issued \\(UTC\\))"))
        self.assertLess(text.index("(Issued \\(UTC\\))"),
                        text.index("(Evidence Seal"))

    def test_all_three_are_sealed_with_the_run(self):
        bare, _ = self._render()
        scoped, _ = self._render(scope=self.SCOPE)
        constrained, _ = self._render(constraints=self.CONSTRAINTS)
        assumed, _ = self._render(assumptions=self.ASSUMED)
        seals = {bare["hash"], scoped["hash"], constrained["hash"],
                 assumed["hash"]}
        self.assertEqual(len(seals), 4)
        tampered = [list(row) for row in self.CONSTRAINTS]
        tampered[0][1] = "301"
        other, _ = self._render(constraints=tampered)
        self.assertNotEqual(other["hash"], constrained["hash"])

    def test_a_certificate_passing_none_of_them_is_one_page_as_before(self):
        _, text = self._render()
        self.assertEqual(text.count("/Type /Page "), 1)
        self.assertNotIn("(Scope)", text)
        self.assertNotIn("(Constraints)", text)

    def test_a_long_body_continues_onto_a_second_leaf_rather_than_cutting(self):
        many = [(f"Limit {i}", f"at most {i} m/s", "assumed")
                for i in range(24)]
        out, text = self._render(scope=self.SCOPE, constraints=many,
                                 assumptions=self.ASSUMED)
        self.assertGreater(text.count("/Type /Page "), 1)
        # Nothing is lost to the page break: the last constraint, the ledger
        # and the seal all reach the page.
        self.assertIn("Limit 23", text)
        self.assertIn("Assumed Values", text)
        self.assertIn(out["hash"][:32], text)


class DensityLadderTests(unittest.TestCase):
    """Tightening is tried to the last rung before a second leaf is taken.

    The airliner certificate came to rest 16 points below the provenance box
    at the old densest rhythm, once the result block gained its fidelity line
    and the validation rank gained the sentence that says which way it runs.
    It paginated for those 16 points: the reader lost the model channel off
    the bottom of the page to save half a line of leading.
    """

    CHANNELS = [
        {"name": "input", "value": 0.74, "quantified": True,
         "note": "Ensemble run over the stated payload-mass and non-wing-drag "
                 "spreads. Requirements are held as exact specification, and "
                 "the remaining sizing constants (SFC, fuel fraction, cruise "
                 "altitude) are fixed"},
        {"name": "numerical", "value": 1.124, "quantified": True,
         "note": "The design grid is discrete, so the true optimum lies "
                 "between grid points. Default numerical consistency method: "
                 "the winner brackets the half-step variation on each grid "
                 "axis, ±1.12. The cruise-point read on the solved polar "
                 "adds ±0.06."},
        {"name": "model", "value": 1.451, "quantified": True,
         "note": "Component buildup band on non-wing drag, propagated to "
                 "whole-aircraft L/D: ±1.45. The band is the documented ±15% "
                 "on the buildup terms (Raymer, Aircraft Design: A Conceptual "
                 "Approach, AIAA). The sizing screen's measured gap to the 9 "
                 "solved wings averages 1.79 in whole-aircraft L/D."},
    ]
    FIELDS = [("Span", "61 m"), ("AR", "10.3"),
              ("Sweep", "20 to 35°, not resolved at this fidelity"),
              ("MTOW", "199 t"), ("Range", "10276 km"),
              ("Approach Speed", "70 m/s"), ("Whole-aircraft L/D", "19.3")]
    OBJECTIVE = ("Optimize lift drag coefficient of the attached twin "
                 "airliner. Constraints: 300 passengers, Range: 6000 km, "
                 "take off speed: 80 m/s landing speed: 70 m/s. Don't use "
                 "all of my workers")

    def _airliner(self):
        doc = {"results": [{"quantity": "Best feasible whole-aircraft L/D",
                            "value": "19.3", "envelope": "2.0",
                            "tier": "SOLVER-BACKED",
                            "reason": "wing solved with VSPAERO; fuselage, "
                                      "tail and nacelle drag added from "
                                      "Raymer's component buildup method"}],
               "result_fields": self.FIELDS, "compute": {}}
        with tempfile.TemporaryDirectory() as d:
            out = build_certificate_v2(
                doc, out_path=Path(d) / "c.pdf", geometry="airliner",
                objective=self.OBJECTIVE, mission_id="aircraft-optimization",
                issued_utc="2026-08-01T09:25:57Z", channels=self.CHANNELS,
                display_name="300-passenger twin-aisle airliner")
            return out, Path(out["path"]).read_bytes().decode("latin-1")

    def test_the_airliner_certificate_holds_one_leaf(self):
        _out, text = self._airliner()
        self.assertEqual(text.count("/Type /Page "), 1)

    def test_the_densest_rhythm_loses_no_content_to_the_squeeze(self):
        # Tightening changes leading, never wording, numbers or order.
        out, text = self._airliner()
        for token in ("19.3", "Span", "61 m", "Whole-aircraft L/D",
                      "Uncertainty", "input", "numerical", "model",
                      "1.451", "Raymer", "Issued"):
            self.assertIn(token, text, token)
        self.assertIn(out["hash"][:32], text)
        self.assertLess(text.index("(Result)"), text.index("(Uncertainty)"))


if __name__ == "__main__":
    unittest.main()
