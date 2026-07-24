"""The shared Claude client and the mission debrief: stubbed, silent fallback.

Mirrors test_voice.py: the completion layer is patched, never the network. The
tests prove the plumbing — enablement, hardening parameters, the one-lesson
debrief with its no-invented-numbers guard, and the lesson landing where
ask-the-lab retrieval can ground on it.
"""

import os
import tempfile
import types
import unittest
from unittest import mock

from chief_engineer import ask_the_lab, claude_lab, debrief
from chief_engineer.lessons import learned_lessons, record_learned


class EnablementTests(unittest.TestCase):
    def setUp(self):
        self.env = mock.patch.dict(os.environ, {}, clear=False)
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_disabled_without_key(self):
        os.environ.pop("ANTHROPIC_API_KEY", None)
        os.environ.pop("CERTONOMOUS_CLAUDE", None)
        self.assertFalse(claude_lab.enabled())
        self.assertIsNone(claude_lab.complete("system", "user"))

    def test_kill_switch_wins_over_the_key(self):
        os.environ["ANTHROPIC_API_KEY"] = "sk-test"
        os.environ["CERTONOMOUS_CLAUDE"] = "0"
        self.assertFalse(claude_lab.enabled())

    def test_enabled_with_key(self):
        os.environ["ANTHROPIC_API_KEY"] = "sk-test"
        os.environ.pop("CERTONOMOUS_CLAUDE", None)
        self.assertTrue(claude_lab.enabled())


class _FakeBlock:
    def __init__(self, text):
        self.type = "text"
        self.text = text


class _FakeMessages:
    def __init__(self, captured, reply, stop_reason):
        self._captured = captured
        self._reply = reply
        self._stop_reason = stop_reason

    def create(self, **kwargs):
        self._captured.update(kwargs)
        return types.SimpleNamespace(stop_reason=self._stop_reason,
                                     content=[_FakeBlock(self._reply)])


class CompleteTests(unittest.TestCase):
    """The request the shared client actually builds, with a stub transport."""

    def setUp(self):
        self.env = mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"})
        self.env.start()
        self.addCleanup(self.env.stop)
        os.environ.pop("CERTONOMOUS_CLAUDE", None)
        os.environ.pop("CERTONOMOUS_CLAUDE_MODEL", None)
        os.environ.pop("CERTONOMOUS_CLAUDE_TIMEOUT", None)
        # A fresh lazy client per test so the fake module is the one built.
        claude_lab._client = None
        self.addCleanup(setattr, claude_lab, "_client", None)

    def _fake_anthropic(self, reply="a reply", stop_reason="end_turn"):
        captured_init, captured_call = {}, {}
        module = types.ModuleType("anthropic")

        class _FakeAnthropic:
            def __init__(self, **kwargs):
                captured_init.update(kwargs)
                self.messages = _FakeMessages(captured_call, reply, stop_reason)

        module.Anthropic = _FakeAnthropic
        return module, captured_init, captured_call

    def test_hardened_client_and_request_plumbing(self):
        module, init, call = self._fake_anthropic()
        with mock.patch.dict("sys.modules", {"anthropic": module}):
            out = claude_lab.complete("the system prompt", "the user prompt",
                                      max_tokens=321, effort="medium")
        self.assertEqual(out, "a reply")
        self.assertEqual(init.get("max_retries"), 0)
        self.assertEqual(init.get("timeout"), 15.0)
        self.assertEqual(call.get("model"), "claude-opus-4-8")
        self.assertEqual(call.get("max_tokens"), 321)
        self.assertEqual(call.get("output_config"), {"effort": "medium"})
        self.assertEqual(call.get("thinking"), {"type": "adaptive"})
        self.assertEqual(call.get("system"), "the system prompt")
        self.assertEqual(call.get("messages"),
                         [{"role": "user", "content": "the user prompt"}])

    def test_refusal_is_a_silent_none(self):
        module, _init, _call = self._fake_anthropic(stop_reason="refusal")
        with mock.patch.dict("sys.modules", {"anthropic": module}):
            self.assertIsNone(claude_lab.complete("s", "u"))

    def test_transport_failure_is_a_silent_none(self):
        module = types.ModuleType("anthropic")

        class _Boom:
            def __init__(self, **kwargs):
                raise RuntimeError("network down")

        module.Anthropic = _Boom
        with mock.patch.dict("sys.modules", {"anthropic": module}):
            self.assertIsNone(claude_lab.complete("s", "u"))


EVENTS = [
    {"event": "mission.routed", "payload": {"intent": "valve_study"}},
    {"event": "transcript.entry",
     "payload": {"role": "CHIEF ENGINEER",
                 "message": "Winner: 80 deg at 1345 Pa across the sweep."}},
    {"event": "transcript.entry",
     "payload": {"role": "NUMERICIST",
                 "message": "Mesh sensitivity near the optimum stayed unresolved."}},
    {"event": "mission.completed", "payload": {"status": "complete"}},
]

GOOD_LESSON = ("Sweeping the valve angle worked, the 80 deg winner at 1345 Pa "
               "held across the sweep, mesh sensitivity near the optimum "
               "stayed uncertain, and a denser angle sweep around the winner "
               "is the next investigation.")


class DebriefTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.env = mock.patch.dict(os.environ, {
            "ANTHROPIC_API_KEY": "sk-test",
            "CERTONOMOUS_LESSONS_DIR": self.tmp.name,
        })
        self.env.start()
        self.addCleanup(self.env.stop)
        os.environ.pop("CERTONOMOUS_CLAUDE", None)

    def test_transcript_lines_extracts_only_spoken_entries(self):
        lines = debrief.transcript_lines(EVENTS)
        self.assertEqual(len(lines), 2)
        self.assertTrue(lines[0].startswith("CHIEF ENGINEER:"))

    def test_debrief_writes_one_lesson_cited_by_the_mission(self):
        with mock.patch.object(claude_lab, "complete",
                               return_value=GOOD_LESSON) as call:
            record = debrief.run("m-test01", "study the valve", "complete", EVENTS)
        self.assertIsNotNone(record)
        self.assertEqual(record["mission_id"], "m-test01")
        stored = learned_lessons()
        self.assertEqual(len(stored), 1)
        self.assertEqual(stored[0]["mission_id"], "m-test01")
        self.assertIn("1345", stored[0]["text"])
        # The model saw the transcript, not something else.
        user = call.call_args.args[1]
        self.assertIn("TRANSCRIPT:", user)
        self.assertIn("80 deg at 1345 Pa", user)

    def test_invented_number_discards_the_lesson(self):
        with mock.patch.object(claude_lab, "complete",
                               return_value="The 2000 Pa loss dominated the sweep."):
            record = debrief.run("m-test02", "study the valve", "complete", EVENTS)
        self.assertIsNone(record)
        self.assertEqual(learned_lessons(), [])

    def test_em_dash_scrubbed_from_the_lesson(self):
        with mock.patch.object(claude_lab, "complete",
                               return_value="The sweep held — densify next."):
            debrief.run("m-test03", "study the valve", "complete", EVENTS)
        stored = learned_lessons()
        self.assertEqual(len(stored), 1)
        self.assertNotIn("—", stored[0]["text"])

    def test_model_failure_records_nothing(self):
        with mock.patch.object(claude_lab, "complete", return_value=None):
            record = debrief.run("m-test04", "study the valve", "complete", EVENTS)
        self.assertIsNone(record)
        self.assertEqual(learned_lessons(), [])

    def test_async_is_a_no_op_without_a_key(self):
        os.environ.pop("ANTHROPIC_API_KEY", None)
        with mock.patch.object(debrief.threading, "Thread") as thread:
            debrief.debrief_async("m-test05", "study the valve", "complete", EVENTS)
        thread.assert_not_called()

    def test_learned_lesson_grounds_ask_the_lab(self):
        record_learned(
            "m-feed42",
            "When the valve sweep narrows near the optimum, densify the "
            "opening angle grid before certifying the plateau.")
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ANTHROPIC_API_KEY", None)
            a = ask_the_lab.answer("what did we learn about the valve sweep optimum?")
        self.assertTrue(a.grounded)
        self.assertEqual(a.mode, "record")
        self.assertIn("m-feed42", " ".join(a.citations))


if __name__ == "__main__":
    unittest.main()
