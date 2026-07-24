"""Ask the lab: deterministic, record-grounded retrieval with honest refusal.

The reasoning layer (Claude over the retrieved excerpts) is exercised with a
stubbed completion, mirroring test_voice.py: patch ``claude_lab.complete`` and
test the prompt plumbing, never the model.
"""

import os
import tempfile
import unittest
from unittest import mock

from chief_engineer import claude_lab
from chief_engineer.ask_the_lab import answer, _credential_sources

# A question the record grounds but only thinly: retrieval finds ahmed_35 yet
# the excerpts cover less than half of the question's meaningful words, which
# is exactly when the model is asked to reason over them.
THIN_QUESTION = "can you tell me whether to trust the ahmed_35 number and why?"


def _isolate_state(case: unittest.TestCase) -> None:
    """Point mission-state and learned-lesson lookups at an empty temp dir so
    whatever a developer ran earlier cannot leak into retrieval."""
    tmp = tempfile.TemporaryDirectory()
    case.addCleanup(tmp.cleanup)
    env = mock.patch.dict(os.environ, {
        "CHIEF_ENGINEER_STATE_DIR": tmp.name,
        "CERTONOMOUS_LESSONS_DIR": os.path.join(tmp.name, "lessons"),
    })
    env.start()
    case.addCleanup(env.stop)


class AskTheLabTests(unittest.TestCase):
    def setUp(self):
        # Hermetic: the deterministic tests must never reach for a real key.
        self.env = mock.patch.dict(os.environ, {}, clear=False)
        self.env.start()
        self.addCleanup(self.env.stop)
        os.environ.pop("ANTHROPIC_API_KEY", None)
        _isolate_state(self)

    def test_credential_sources_load_from_the_curriculum(self):
        # The validation-wall bodies are a record source; at least the cube
        # (committed) is present.
        sources = _credential_sources()
        names = " ".join(s.detail.lower() for s in sources)
        self.assertTrue(sources, "expected curriculum credential sources")
        self.assertIn("cube", names)

    def test_validation_query_is_grounded_and_cited(self):
        result = answer("what have we validated?")
        self.assertTrue(result.grounded)
        self.assertTrue(result.citations)

    def test_specific_body_query_grounds_on_the_wall(self):
        result = answer("what do we know about the cube?")
        self.assertTrue(result.grounded)
        self.assertIn("cube", result.text.lower())

    def test_numbered_body_names_ground_distinctly(self):
        # 'ahmed_35' must not collapse into 'ahmed' and miss the grounding
        # threshold — the digit distinguishes it from ahmed_25.
        a = answer(THIN_QUESTION)
        self.assertTrue(a.grounded)
        self.assertIn("35", a.text)

    def test_out_of_record_question_refuses_honestly(self):
        result = answer("what is the airspeed velocity of an unladen swallow?")
        self.assertFalse(result.grounded)
        self.assertIn("could not ground", result.text.lower())

    def test_answer_serialises_for_the_api(self):
        payload = answer("what have we validated?").to_dict()
        self.assertIn("grounded", payload)
        self.assertIn("text", payload)
        self.assertIsInstance(payload["citations"], list)
        self.assertIn("mode", payload)

    def test_no_key_stays_deterministic(self):
        # Without a key the answer is the deterministic record listing —
        # byte-identical to the lab before the reasoning layer existed.
        a = answer("what do we know about the cube?")
        self.assertEqual(a.mode, "record")
        self.assertTrue(a.grounded)


class SynthesisTests(unittest.TestCase):
    """The model reasons only when the record alone is thin, and only over
    the excerpts the deterministic layer retrieved."""

    def setUp(self):
        self.env = mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"})
        self.env.start()
        self.addCleanup(self.env.stop)
        os.environ.pop("CERTONOMOUS_CLAUDE", None)
        os.environ.pop("CERTONOMOUS_ASK_LLM", None)
        _isolate_state(self)

    def test_solid_record_answer_is_kept_without_calling_the_model(self):
        # The wall answers "the cube" fully — Claude is not consulted and the
        # deterministic listing is returned unchanged.
        with mock.patch.object(claude_lab, "complete",
                               return_value="should never be used") as call:
            a = answer("what do we know about the cube?")
        self.assertEqual(a.mode, "record")
        call.assert_not_called()

    def test_thin_answer_reasons_over_the_record(self):
        captured = {}

        def fake_complete(system, user, **kwargs):
            captured["system"] = system
            captured["user"] = user
            return ("Reasoned: the ahmed 35 figure sits inside its envelope "
                    "against the reference, so it can be trusted at its tier.")

        with mock.patch.object(claude_lab, "complete", side_effect=fake_complete):
            a = answer(THIN_QUESTION)
        self.assertEqual(a.mode, "synthesized")
        self.assertIn("Reasoned:", a.text)
        # Provenance is still the deterministic citations, unchanged.
        self.assertTrue(a.citations)
        # The no-hallucination guard: the prompt carries only the retrieved
        # excerpts, never the full corpus.
        self.assertIn("FACTS FROM THE LAB'S RECORD", captured["user"])
        self.assertIn("35", captured["user"])
        self.assertNotIn("motorbike", captured["user"].lower())
        self.assertNotIn("cube", captured["user"].lower())

    def test_aggregate_question_reasons_with_the_model(self):
        with mock.patch.object(claude_lab, "complete",
                               return_value="Ranked from the record: ahmed 25 first."):
            a = answer("rank all the cases we have run by drag")
        self.assertEqual(a.mode, "synthesized")
        self.assertTrue(a.grounded)

    def test_model_failure_keeps_the_record_answer(self):
        with mock.patch.object(claude_lab, "complete", return_value=None):
            a = answer(THIN_QUESTION)
        self.assertEqual(a.mode, "record")
        self.assertTrue(a.grounded)

    def test_near_miss_excerpts_go_to_the_model(self):
        # No source clears the grounding bar, but retrieval still surfaced
        # drag excerpts — the model may answer from exactly those.
        captured = {}

        def fake_complete(system, user, **kwargs):
            captured["user"] = user
            return ("The record holds drag figures only for solved bodies; "
                    "no swallow or coconut has been run.")

        with mock.patch.object(claude_lab, "complete", side_effect=fake_complete):
            a = answer("does the swallow have more drag than a coconut?")
        self.assertTrue(a.grounded)
        self.assertEqual(a.mode, "synthesized")
        self.assertTrue(a.citations)
        self.assertIn("FACTS FROM THE LAB'S RECORD", captured["user"])

    def test_unanswerable_reply_keeps_the_honest_refusal(self):
        with mock.patch.object(claude_lab, "complete", return_value="UNANSWERABLE"):
            a = answer("does the swallow have more drag than a coconut?")
        self.assertFalse(a.grounded)
        self.assertIn("could not ground", a.text.lower())

    def test_disabled_flag_forces_deterministic_even_with_key(self):
        with mock.patch.dict(os.environ, {"CERTONOMOUS_ASK_LLM": "0"}), \
             mock.patch.object(claude_lab, "complete",
                               return_value="should never be used") as call:
            a = answer(THIN_QUESTION)
        self.assertEqual(a.mode, "record")
        call.assert_not_called()

    def test_claude_kill_switch_forces_deterministic(self):
        with mock.patch.dict(os.environ, {"CERTONOMOUS_CLAUDE": "0"}), \
             mock.patch.object(claude_lab, "complete",
                               return_value="should never be used") as call:
            a = answer(THIN_QUESTION)
        self.assertEqual(a.mode, "record")
        call.assert_not_called()

    def test_ungrounded_never_calls_the_model(self):
        # Zero retrieval overlap: nothing to hand the model, so it stays out.
        with mock.patch.object(claude_lab, "complete",
                               return_value="should never be used") as call:
            a = answer("what is the airspeed velocity of an unladen swallow?")
        self.assertFalse(a.grounded)
        call.assert_not_called()

    def test_em_dash_scrubbed_from_synthesized_answer(self):
        with mock.patch.object(claude_lab, "complete",
                               return_value="Trust it — the envelope holds."):
            a = answer(THIN_QUESTION)
        self.assertNotIn("—", a.text)


if __name__ == "__main__":
    unittest.main()
