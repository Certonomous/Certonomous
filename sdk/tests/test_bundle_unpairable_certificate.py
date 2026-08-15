"""An act whose certificate cannot be paired loses the certificate, not the act.

Docket D177. `pick_missions` was right to refuse a contradictory pair, but
refusing the PAIR was implemented as refusing the ACT. On 2026-08-15 that cost
fifteen of ninety zip members -- one certificate, nine `.stl`, three `.png` and
the two recording files -- under a remedy printed to the lab owner as
*"re-run `python3 scripts/build_laptop_bundle.py` and commit the rebuilt
`.zip` ... no content edit is needed"*, costed at *"one command"*.

These tests pin the three things that make the smaller loss safe:
  1. the act comes back and its non-certificate artifacts ship;
  2. the CONTRADICTING certificate never ships, so `check_bundle_pairing`
     still passes on truth and not on tolerance;
  3. the omission is written into the bundle and into the exit code, because
     a count printed to a terminal nobody kept is how the first fifteen went.

Every case builds a REAL certificate with the real generator and reads its seal
back out of the rendered PDF, so a layout change that hid the seal fails these
tests rather than passing them quietly.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "sdk"))
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_laptop_bundle as blb  # noqa: E402

# The pairing tests own the fixtures; reusing them keeps one definition of what
# a recording and a real certificate look like.
from test_bundle_certificate_pairing import (  # noqa: E402
    _write_certificate, _write_recording)


def _plant(root: Path, *, with_stl: bool = True) -> tuple[Path, Path, dict]:
    """A lab tree whose airliner certificate describes a run nothing recorded.

    This is the live situation exactly: 97 recordings announce a certificate in
    `aircraft-optimization/`, none of them announces the page now at that path,
    and the page was written at 19:47:41Z by a run with no recording in either
    state directory.
    """
    output_root = root / "mission-output"
    state = root / "mission-state"
    info = _write_certificate(output_root, "aircraft-optimization",
                              "2026-08-15T19:47:41Z")
    if with_stl:
        for name in ("wing-span61-area360-sweep25.stl",
                     "wing-span67-area420-sweep30.stl"):
            (output_root / "aircraft-optimization" / name).write_text(
                "solid wing\nendsolid wing\n", encoding="utf-8")
    events = _write_recording(state, "m-9c67e2638ff1", "aircraft-optimization",
                              "d889461d" + info["hash"][8:], "C-2026-0918",
                              finished_at=200.0)
    # The recording points at its geometry the way a real one does.
    if with_stl:
        lines = events.read_text(encoding="utf-8").splitlines()
        lines.append(json.dumps({
            "event": "artifact.ready",
            "payload": {"url": "/api/surface/aircraft-optimization/"
                               "wing-span61-area360-sweep25.stl"}}))
        lines.append(json.dumps({
            "event": "artifact.ready",
            "payload": {"url": "/api/surface/aircraft-optimization/"
                               "wing-span67-area420-sweep30.stl"}}))
        events.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_root, state, info


class UnpairableFallbackTests(unittest.TestCase):

    def test_pick_missions_still_refuses_it(self):
        """Control. The strict rule is unchanged; the fallback is a second
        question asked only after the strict one has answered no."""
        with tempfile.TemporaryDirectory() as d:
            output_root, state, _ = _plant(Path(d))
            picked, _ = blb.pick_missions(state, output_root)
            self.assertNotIn("aircraft-optimization", picked)

    def test_fallback_recovers_the_act(self):
        with tempfile.TemporaryDirectory() as d:
            output_root, state, _ = _plant(Path(d))
            fallback = blb.pick_unpairable(state, output_root,
                                           ["aircraft-optimization"])
            self.assertIn("aircraft-optimization", fallback)
            mission_id, _, _, faults = fallback["aircraft-optimization"]
            self.assertEqual(mission_id, "m-9c67e2638ff1")
            self.assertTrue(faults, "it must say why the pair was refused")
            self.assertIn("d889461d", faults[0])

    def test_fallback_declines_when_the_geometry_is_gone_too(self):
        """MUST-NOT-MATCH: the fallback ships an act because the rest of it is
        intact. If the artifacts are absent there is no act to rescue, and
        falling back would trade a named omission for a broken replay."""
        with tempfile.TemporaryDirectory() as d:
            output_root, state, _ = _plant(Path(d))
            for stl in (output_root / "aircraft-optimization").glob("*.stl"):
                stl.unlink()
            self.assertEqual(
                blb.pick_unpairable(state, output_root,
                                    ["aircraft-optimization"]), {})

    def test_fallback_is_not_offered_for_an_intent_already_paired(self):
        """MUST-NOT-MATCH: a matching recording must go through the strict
        path, or the fallback would be the path and the gate would be scenery."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            output_root = root / "mission-output"
            state = root / "mission-state"
            info = _write_certificate(output_root, "aircraft-optimization",
                                      "2026-07-20T00:00:00Z")
            _write_recording(state, "m-good", "aircraft-optimization",
                             info["hash"], info["certificate_no"],
                             finished_at=100.0)
            self.assertEqual(
                blb.pick_unpairable(state, output_root,
                                    ["aircraft-optimization"]), {})

    def test_withheld_directories_names_only_the_disagreeing_one(self):
        """Per directory, not per recording: an act that seals two pages and
        disagrees about one must still ship the one it agrees about."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            output_root = root / "mission-output"
            state = root / "mission-state"
            bad = _write_certificate(output_root, "aircraft-optimization",
                                     "2026-08-15T19:47:41Z")
            good = _write_certificate(output_root, "geometry-study",
                                      "2026-08-15T19:47:41Z")
            events = state / "m-two.events.jsonl"
            state.mkdir(parents=True, exist_ok=True)
            events.write_text("\n".join(json.dumps(x) for x in [
                {"event": "mission.routed",
                 "payload": {"intent": "aircraft-optimization"}},
                {"event": "certificate.ready",
                 "payload": {"dir": "aircraft-optimization",
                             "hash": "d889461d" + bad["hash"][8:],
                             "certificate_no": "C-2026-0918"}},
                {"event": "certificate.ready",
                 "payload": {"dir": "geometry-study", "hash": good["hash"],
                             "certificate_no": good["certificate_no"]}},
            ]) + "\n", encoding="utf-8")
            self.assertEqual(blb.withheld_directories(events, output_root),
                             ["aircraft-optimization"])


class BuildOutcomeTests(unittest.TestCase):
    """End to end through `main`, because the defect was in what got SHIPPED."""

    def _build(self, root: Path, out: Path, *, zip_it: bool = False) -> int:
        output_root, state, _ = _plant(root)
        argv = ["build_laptop_bundle.py", "--out", str(out),
                "--state", str(state), "--output-root", str(output_root)]
        if zip_it:
            argv.append("--zip")
        with mock.patch.object(sys, "argv", argv), \
                mock.patch.object(blb, "WANTED_INTENTS",
                                  ("aircraft-optimization",)), \
                mock.patch.object(blb, "_capture_panels", return_value={}):
            return blb.main()

    def test_the_act_ships_without_its_certificate_and_says_so(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            out = root / "bundle"
            rc = self._build(root, out)

            act = out / "mission-output" / "aircraft-optimization"
            self.assertTrue((out / "mission-state"
                             / "m-9c67e2638ff1.events.jsonl").exists())
            self.assertEqual(len(list(act.glob("*.stl"))), 2)

            # The contradicting page is NOT in the bundle...
            self.assertFalse((act / "certificate.pdf").exists())
            # ...and the gate on the shipped bytes passes because of that,
            # not in spite of it.
            self.assertEqual(blb.check_bundle_pairing(out), [])

            # The omission travels inside the archive.
            note = act / "CERTIFICATE_WITHDRAWN.txt"
            self.assertTrue(note.exists())
            self.assertIn("d889461d", note.read_text(encoding="utf-8"))

            # And it is not spelled "success".
            self.assertEqual(rc, 1)

    def test_a_wholly_missing_act_refuses_to_zip(self):
        """The failure that reached the owner: an archive short an entire act,
        written anyway, behind an exit code the printed remedy never mentioned."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            out = root / "bundle"
            output_root, state, _ = _plant(root)
            # The recording still points at its geometry; the geometry is gone,
            # so there is no act left to rescue and the fallback declines.
            for stl in (output_root / "aircraft-optimization").glob("*.stl"):
                stl.unlink()
            argv = ["build_laptop_bundle.py", "--out", str(out),
                    "--state", str(state), "--output-root", str(output_root),
                    "--zip"]
            with mock.patch.object(sys, "argv", argv), \
                    mock.patch.object(blb, "WANTED_INTENTS",
                                      ("aircraft-optimization",)), \
                    mock.patch.object(blb, "_capture_panels", return_value={}):
                rc = blb.main()
            self.assertEqual(rc, 3)
            self.assertFalse((root / "bundle.zip").exists(),
                             "a bundle short an act must not become an archive")


if __name__ == "__main__":
    unittest.main()
