"""The laptop bundle may not ship a recording paired with a certificate that
describes a different run (docket D136).

A recording is frozen and a certificate path is mutable, so the two agree only
by luck. On camera the luck is visible: `control_room.html` renders the EVENT's
seal directly above a link to the PDF, so a mismatched pair shows one seal in
the console and another one click away -- the demo's own tamper-evidence claim
failing inside the only artifact that leaves this box.

These tests are the mutation proof for `check_bundle_pairing` and for the
selection rule in `pick_missions`. Every case builds a REAL certificate with
the real generator and reads its seal back out of the rendered PDF, so a change
to the page layout that hid the seal would fail these tests rather than pass
them silently.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "sdk"))
sys.path.insert(0, str(REPO / "scripts"))

import build_laptop_bundle as blb  # noqa: E402
from chief_engineer.certificate import build_certificate_v2  # noqa: E402

_REPORT = {
    "results": [{"quantity": "Drag coefficient", "value": "0.0471",
                 "envelope": "0.0013", "tier": "TREND ONLY",
                 "reason": "solver-backed"}],
    "uncertainty": [],
    "compute": {"cells": 1000, "core_minutes": 1.0},
}


def _write_certificate(root: Path, directory: str, issued: str) -> dict:
    out = root / directory / "certificate.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    return build_certificate_v2(
        _REPORT, out_path=out, geometry="b52", objective="measure drag",
        mission_id=f"{directory}-mission", issued_utc=issued)


def _write_recording(state: Path, mission_id: str, directory: str,
                     seal: str, certificate_no: str,
                     intent: str = "aircraft-optimization",
                     finished_at: float = 1.0) -> Path:
    events = state / f"{mission_id}.events.jsonl"
    state.mkdir(parents=True, exist_ok=True)
    lines = [
        {"event": "mission.routed", "payload": {"intent": intent}},
        {"event": "certificate.ready",
         "payload": {"dir": directory, "hash": seal,
                     "certificate_no": certificate_no,
                     "path": f"/x/{directory}/certificate.pdf"}},
    ]
    events.write_text("\n".join(json.dumps(x) for x in lines) + "\n",
                      encoding="utf-8")
    (state / f"{mission_id}.json").write_text(
        json.dumps({"mission_id": mission_id, "state": "complete",
                    "finished_at": finished_at}), encoding="utf-8")
    return events


class PdfIdentityTests(unittest.TestCase):
    """The reader has to actually reach the seal, or every check below is a
    tautology that passes on unreadable pages."""

    def test_seal_and_serial_are_read_from_a_real_certificate(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            info = _write_certificate(root, "aircraft-optimization",
                                      "2026-07-20T00:00:00Z")
            seal, serial = blb.pdf_identity(
                root / "aircraft-optimization" / "certificate.pdf")
            self.assertEqual(seal, info["hash"])
            self.assertEqual(serial, info["certificate_no"])

    def test_an_unreadable_page_yields_no_seal(self):
        with tempfile.TemporaryDirectory() as d:
            fake = Path(d) / "certificate.pdf"
            fake.write_bytes(b"%PDF-1.4 nothing sealed here")
            self.assertEqual(blb.pdf_identity(fake), (None, None))


class BundlePairingGateTests(unittest.TestCase):
    """MUTATION PROOF: matched pair passes, mismatched pair fails."""

    def _bundle(self, d: str, *, seal: str, certificate_no: str) -> Path:
        bundle = Path(d) / "bundle"
        _write_certificate(bundle / "mission-output", "aircraft-optimization",
                           "2026-07-20T00:00:00Z")
        _write_recording(bundle / "mission-state", "m-aaaa",
                         "aircraft-optimization", seal, certificate_no)
        return bundle

    def test_matched_pair_passes(self):
        with tempfile.TemporaryDirectory() as d:
            bundle = Path(d) / "bundle"
            info = _write_certificate(bundle / "mission-output",
                                      "aircraft-optimization",
                                      "2026-07-20T00:00:00Z")
            _write_recording(bundle / "mission-state", "m-aaaa",
                             "aircraft-optimization",
                             info["hash"], info["certificate_no"])
            self.assertEqual(blb.check_bundle_pairing(bundle), [])

    def test_mismatched_seal_fails(self):
        """The planted D136 shape: the exact airliner disagreement that
        shipped in five consecutive bundles."""
        with tempfile.TemporaryDirectory() as d:
            bundle = Path(d) / "bundle"
            info = _write_certificate(bundle / "mission-output",
                                      "aircraft-optimization",
                                      "2026-07-20T00:00:00Z")
            planted = "d889461d168b47c2" + info["hash"][16:]
            self.assertNotEqual(planted, info["hash"])
            _write_recording(bundle / "mission-state", "m-aaaa",
                             "aircraft-optimization",
                             planted, info["certificate_no"])
            faults = blb.check_bundle_pairing(bundle)
            self.assertTrue(faults, "a mismatched seal must be caught")
            self.assertIn("d889461d168b47c2", faults[0])

    def test_mismatched_serial_fails(self):
        with tempfile.TemporaryDirectory() as d:
            bundle = Path(d) / "bundle"
            info = _write_certificate(bundle / "mission-output",
                                      "aircraft-optimization",
                                      "2026-07-20T00:00:00Z")
            _write_recording(bundle / "mission-state", "m-aaaa",
                             "aircraft-optimization",
                             info["hash"], "C-2026-0918")
            faults = blb.check_bundle_pairing(bundle)
            self.assertTrue(faults, "a mismatched serial must be caught")
            self.assertIn("C-2026-0918", faults[0])

    def test_unreadable_certificate_fails_rather_than_passing(self):
        """An unguaranteed pairing is exactly what shipped for five builds, so
        'cannot verify' must not be spelled 'fine'."""
        with tempfile.TemporaryDirectory() as d:
            bundle = Path(d) / "bundle"
            pdf = bundle / "mission-output" / "aircraft-optimization" / "certificate.pdf"
            pdf.parent.mkdir(parents=True)
            pdf.write_bytes(b"%PDF-1.4 compressed, unreadable")
            _write_recording(bundle / "mission-state", "m-aaaa",
                             "aircraft-optimization", "a" * 64, "C-2026-0001")
            faults = blb.check_bundle_pairing(bundle)
            self.assertTrue(faults)
            self.assertIn("unreadable", faults[0])

    def test_absent_certificate_is_not_a_pairing_fault(self):
        """Must-not-match control: a bundle with no certificate misleads
        nobody, and the copy step already reports it as absent. If this fired
        the gate would be a blanket 'anything unusual fails' rather than a
        pairing check."""
        with tempfile.TemporaryDirectory() as d:
            bundle = Path(d) / "bundle"
            (bundle / "mission-output").mkdir(parents=True)
            _write_recording(bundle / "mission-state", "m-aaaa",
                             "aircraft-optimization", "a" * 64, "C-2026-0001")
            self.assertEqual(blb.check_bundle_pairing(bundle), [])


class SelectionTests(unittest.TestCase):
    """The pairing FIX, not just its alarm: selection must skip a recording the
    artifact on disk does not describe, instead of taking the newest on faith."""

    def test_newest_mismatched_recording_is_skipped_for_a_matching_older_one(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            output_root = root / "mission-output"
            state = root / "mission-state"
            info = _write_certificate(output_root, "aircraft-optimization",
                                      "2026-07-20T00:00:00Z")
            # The newest complete recording describes a run that has since been
            # overwritten at this path -- the D136 situation exactly.
            _write_recording(state, "m-newer", "aircraft-optimization",
                             "d889461d" + info["hash"][8:], "C-2026-0918",
                             finished_at=200.0)
            # An older recording that the file on disk really does describe.
            _write_recording(state, "m-older", "aircraft-optimization",
                             info["hash"], info["certificate_no"],
                             finished_at=100.0)
            picked, rejected = blb.pick_missions(state, output_root)
            self.assertIn("aircraft-optimization", picked)
            self.assertEqual(picked["aircraft-optimization"][0], "m-older")
            self.assertTrue(rejected["aircraft-optimization"])
            self.assertIn("m-newer", rejected["aircraft-optimization"][0])

    def test_recording_with_no_certificate_event_is_not_selected(self):
        """A recording that seals nothing passes a pairing check vacuously.
        Taking it would trade a contradictory certificate for a MISSING one,
        reported as a count -- so it must be rejected with a reason instead."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            output_root = root / "mission-output"
            state = root / "mission-state"
            info = _write_certificate(output_root, "aircraft-optimization",
                                      "2026-07-20T00:00:00Z")
            state.mkdir(parents=True)
            (state / "m-silent.events.jsonl").write_text(
                json.dumps({"event": "mission.routed",
                            "payload": {"intent": "aircraft-optimization"}}) + "\n",
                encoding="utf-8")
            (state / "m-silent.json").write_text(
                json.dumps({"mission_id": "m-silent", "state": "complete",
                            "finished_at": 300.0}), encoding="utf-8")
            _write_recording(state, "m-sealed", "aircraft-optimization",
                             info["hash"], info["certificate_no"],
                             finished_at=100.0)
            picked, rejected = blb.pick_missions(state, output_root)
            self.assertEqual(picked["aircraft-optimization"][0], "m-sealed")
            self.assertTrue(any("no certificate.ready" in r
                                for r in rejected["aircraft-optimization"]))

    def test_recording_announcing_an_absent_page_is_not_selected(self):
        """Selection requires the page to exist; the gate does not. A console
        announcing a seal whose link opens nothing is the same failure wearing
        a different face."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            output_root = root / "mission-output"
            output_root.mkdir(parents=True)
            state = root / "mission-state"
            _write_recording(state, "m-aaaa", "aircraft-optimization",
                             "a" * 64, "C-2026-0001", finished_at=100.0)
            picked, rejected = blb.pick_missions(state, output_root)
            self.assertNotIn("aircraft-optimization", picked)
            self.assertTrue(any("no page exists" in r
                                for r in rejected["aircraft-optimization"]))

    def test_no_matching_recording_leaves_the_intent_unpicked(self):
        """Nothing is shipped rather than something contradictory."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            output_root = root / "mission-output"
            state = root / "mission-state"
            info = _write_certificate(output_root, "aircraft-optimization",
                                      "2026-07-20T00:00:00Z")
            _write_recording(state, "m-newer", "aircraft-optimization",
                             "d889461d" + info["hash"][8:], "C-2026-0918",
                             finished_at=200.0)
            picked, rejected = blb.pick_missions(state, output_root)
            self.assertNotIn("aircraft-optimization", picked)
            self.assertTrue(rejected["aircraft-optimization"])


if __name__ == "__main__":
    unittest.main()
