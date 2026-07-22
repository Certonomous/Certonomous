"""Ask the lab: deterministic, record-grounded retrieval with honest refusal."""

import os
import sys
import types
import unittest
from unittest import mock

from chief_engineer.ask_the_lab import answer, _credential_sources


class AskTheLabTests(unittest.TestCase):
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
        # threshold � the digit distinguishes it from ahmed_25.
        a = answer("can you tell me whether to trust the ahmed_35 number and why?")
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
        # Without a key the answer is the deterministic record listing.
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ANTHROPIC_API_KEY", None)
            a = answer("what do we know about the cube?")
        self.assertEqual(a.mode, "record")
        self.assertTrue(a.grounded)


class _FakeBlock:
    def __init__(self, text):
        self.type = "text"
        self.text = text


class _FakeMessages:
    def __init__(self, captured, reply):
        self._captured = captured
        self._reply = reply

    def create(self, **kwargs):
        self._captured.update(kwargs)
        return types.SimpleNamespace(content=[_FakeBlock(self._reply)])


class _FakeAnthropic:
    """A stand-in for the anthropic client so the synthesis path can be tested
    with no network and no key."""
    captured: dict = {}
    reply = "Synthesized: the cube Cd is validated within 5% of Hoerner."

    def __init__(self, api_key=None):
        self.messages = _FakeMessages(_FakeAnthropic.captured, _FakeAnthropic.reply)


class SynthesisTests(unittest.TestCase):
    def setUp(self):
        _FakeAnthropic.captured = {}
        self._fake_module = types.ModuleType("anthropic")
        self._fake_module.Anthropic = _FakeAnthropic

    def _with_fake_llm(self):
        return mock.patch.dict(sys.modules, {"anthropic": self._fake_module})

    def test_synthesis_reasons_over_grounded_facts(self):
        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}), \
             self._with_fake_llm():
            a = answer("what do we know about the cube?")
        self.assertEqual(a.mode, "synthesized")
        self.assertIn("Synthesized", a.text)
        # Provenance is still the deterministic citations, unchanged by synthesis.
        self.assertTrue(a.citations)

    def test_model_only_sees_the_grounded_facts_not_the_corpus(self):
        # The no-hallucination guard: the prompt handed to the model must contain
        # only the retrieved facts, never the full corpus.
        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}), \
             self._with_fake_llm():
            answer("what do we know about the cube?")
        sent = _FakeAnthropic.captured["messages"][0]["content"]
        self.assertIn("cube", sent.lower())
        self.assertIn("FACTS FROM THE LAB'S RECORD", sent)
        # A body the retrieval did not select must not be smuggled in.
        self.assertNotIn("motorbike", sent.lower())

    def test_synthesis_failure_falls_back_to_record(self):
        class _Boom:
            def __init__(self, api_key=None):
                raise RuntimeError("network down")
        boom_module = types.ModuleType("anthropic")
        boom_module.Anthropic = _Boom
        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}), \
             mock.patch.dict(sys.modules, {"anthropic": boom_module}):
            a = answer("what do we know about the cube?")
        self.assertEqual(a.mode, "record")
        self.assertTrue(a.grounded)

    def test_disabled_flag_forces_deterministic_even_with_key(self):
        with mock.patch.dict(os.environ,
                             {"ANTHROPIC_API_KEY": "sk-test", "CERTONOMOUS_ASK_LLM": "0"}), \
             self._with_fake_llm():
            a = answer("what do we know about the cube?")
        self.assertEqual(a.mode, "record")

    def test_ungrounded_never_calls_the_model(self):
        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}), \
             self._with_fake_llm():
            a = answer("what is the airspeed velocity of an unladen swallow?")
        self.assertFalse(a.grounded)
        self.assertEqual(_FakeAnthropic.captured, {})   # model was never invoked


if __name__ == "__main__":
    unittest.main()
