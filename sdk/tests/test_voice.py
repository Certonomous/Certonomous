"""The Claude narration voice: strictly optional, strictly honest."""

import os
import tempfile
import unittest
from unittest import mock

from chief_engineer import voice
from chief_engineer.transcript import Transcript


class VoiceDisabled(unittest.TestCase):
    def test_off_by_default(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("CERTONOMOUS_VOICE", None)
            self.assertEqual(voice.polish("CHIEF ENGINEER", "L/D 19.7 solved"),
                             "L/D 19.7 solved")

    def test_transcript_unchanged_when_disabled(self):
        os.environ.pop("CERTONOMOUS_VOICE", None)
        script = Transcript("t", echo=None)
        entry = script.engineer("Winner: 80 deg at 1345 Pa.")
        self.assertEqual(entry.message, "Winner: 80 deg at 1345 Pa.")


class VoiceEnabled(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = mock.patch.dict(os.environ, {
            "CERTONOMOUS_VOICE": "1",
            "CERTONOMOUS_VOICE_CACHE": self.tmp.name,
        })
        self.env.start()
        self.addCleanup(self.env.stop)
        self.addCleanup(self.tmp.cleanup)

    def test_rewrite_used_when_numbers_survive(self):
        with mock.patch.object(voice, "_complete",
                               return_value="We solved it: L/D 19.7 at span 64 m."):
            out = voice.polish("CHIEF ENGINEER", "Best L/D 19.7 at span 64 m")
        self.assertEqual(out, "We solved it: L/D 19.7 at span 64 m.")

    def test_number_guard_falls_back(self):
        with mock.patch.object(voice, "_complete",
                               return_value="We found a great lift-to-drag ratio."):
            out = voice.polish("CHIEF ENGINEER", "Best L/D 19.7 at span 64 m")
        self.assertEqual(out, "Best L/D 19.7 at span 64 m")

    def test_api_failure_falls_back(self):
        with mock.patch.object(voice, "_complete", side_effect=RuntimeError("down")):
            out = voice.polish("MONITOR", "Worker 3 lost. Reprovisioning.")
        self.assertEqual(out, "Worker 3 lost. Reprovisioning.")

    def test_cache_serves_second_call_without_api(self):
        with mock.patch.object(voice, "_complete",
                               return_value="Cycle loss lands at 1345 Pa.") as call:
            first = voice.polish("CHIEF ENGINEER", "Loss 1345 Pa")
            second = voice.polish("CHIEF ENGINEER", "Loss 1345 Pa")
        self.assertEqual(first, second)
        self.assertEqual(call.call_count, 1)

    def test_em_dash_scrubbed(self):
        with mock.patch.object(voice, "_complete",
                               return_value="Loss 1345 Pa — the winner holds."):
            out = voice.polish("CHIEF ENGINEER", "Loss 1345 Pa")
        self.assertNotIn("—", out)


if __name__ == "__main__":
    unittest.main()
