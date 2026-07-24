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
                      {"VALIDATED", "SOLVER-BACKED", "CONCEPTUAL MODEL"})

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
        # checkMesh numbers. Model: k-omega SST, stated model-form.
        self.assertFalse(inp["quantified"])
        self.assertIn("stated, not quantified", inp["note"])
        self.assertIn("freestream conditions envelope", inp["note"])
        self.assertTrue(num["quantified"])
        self.assertEqual(num["value"], 0.00303)
        self.assertIn("checkMesh: 193,880 cells", num["note"])
        self.assertFalse(mod["quantified"])
        self.assertIn("k-omega SST", mod["note"])
        _, text = self._render(channels=channels)
        self.assertTrue(text.startswith("%PDF"))
        for token in ("input", "numerical", "model", "not quantified",
                      "193,880"):
            self.assertIn(token, text)

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
        self.assertIn("MESH VALIDITY", text)
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


if __name__ == "__main__":
    unittest.main()
