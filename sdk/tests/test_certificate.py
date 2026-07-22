"""The Certonomous Certificate: seal integrity and PDF well-formedness."""

import tempfile
import unittest
from pathlib import Path

from chief_engineer.certificate import (build_certificate, evidence_hash,
                                        _seal_payload)


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


if __name__ == "__main__":
    unittest.main()
