"""Ladder V rung V5, at the generator: the untrained QCR claim carries its citation.

WHY THIS FILE EXISTS. V5's criterion is that Spalart (2000) is named wherever
QCR is named, and the chief ruling of 2026-08-15 (`3af7bd2b`, recorded on
`campaign/LADDER_V_TRIPLE_VERIFICATION.md`) fixed the frame as *every surface a
future build or edit can change, plus the generators that write them*.

THE NEAR-MISS THIS GUARD IS SHAPED AGAINST. The 2026-08-11 repair `e071075d`
did check for a generator before hand-editing `benchmarks.html`. It asked
whether anything writes that FILE, and correctly found nothing. It did not ask
whether anything writes that SENTENCE -- and `build_benchmarks.py`'s
module-level `_CLOSURE["our_entry"]` did, into `benchmarks.json`,
`wall/wall.json` and the `dist/` snapshot, all three unattributed. A repair to
an output a generator will rewrite is not a repair, which is `e071075d`'s own
stated principle applied one file to its left.

So the subject of these tests is the GENERATOR'S LITERAL, read out of the
source by `ast`, not the JSON it happens to have written. A regeneration cannot
quietly undo an assertion made against the thing that does the generating.

THE RULE IS ABOUT FORM, NOT ABOUT A SENTENCE. Nothing here pins the wording of
the citation or of the claim; a test that pinned a reference sentence would be
a claim generator of the kind this corpus has twice had to unpick. What is
pinned is the pairing: any emitted sentence that names QCR must, in that same
sentence, name the constant's publisher. Rewrite the prose however you like and
this stays green, as long as the attribution travels with the claim.

`sdk/tests/test_rank_claim_surfaces.py`'s
`TheBestOnBoardCountIsFixedAtItsGeneratorTests` already pins that the generator
and the two JSON files it feeds hold ONE string, so the citation reaching the
literal reaches the shipped surfaces too. That test is the transport; this one
is the content.
"""

from __future__ import annotations

import ast
import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GENERATOR = REPO / "sdk" / "scripts" / "build_benchmarks.py"

# The claim: our own model's QCR2000 term. Matched on the model NAME as a
# reader meets it, not on a phrase, so re-wording the sentence cannot slip out
# from under the guard. Case-sensitive on purpose: the lowercase `qcr` in
# `closure_challenge_round5_qcr.json` is a path, not a claim about a model, and
# a guard that fires on paths is a guard that gets switched off.
_QCR = re.compile(r"\bQCR\d*\b")
# The attribution. `Spalart (2000)` is the citation form the sibling public
# surface `benchmarks.html` already uses ("Ahmed, Ramm & Faltin (1984)",
# "Billig (1967)"); the year is required because "Spalart" alone also names the
# 1992 one-equation model, which is a different paper and not the QCR source.
_CITED = re.compile(r"\bSpalart\b[^.]{0,40}?\(?2000\)?", re.I)


def _sentences(text: str) -> list[str]:
    """Split on sentence-final punctuation followed by whitespace.

    A decimal literal (`Ccr1 = 0.3 is`) has no space after its point and so is
    never a boundary, which is what makes this safe on numeric prose.
    """
    return [s for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


class TheGeneratorAttributesItsUntrainedQcrClaim(unittest.TestCase):

    def _closure_literal(self) -> dict:
        self.assertTrue(GENERATOR.exists(),
                        "the generator is gone; this test asserts nothing "
                        "without it")
        tree = ast.parse(GENERATOR.read_text(encoding="utf-8"))
        for node in tree.body:
            if (isinstance(node, ast.Assign) and len(node.targets) == 1
                    and getattr(node.targets[0], "id", None) == "_CLOSURE"):
                return ast.literal_eval(node.value)
        self.fail("_CLOSURE is not a module-level literal in the generator: "
                  "this test's subject has moved and it is asserting nothing")

    @staticmethod
    def _emitted_strings(node) -> list[str]:
        """Every string the generator EMITS, at any depth.

        Comments and docstrings are deliberately out of reach: this grades what
        reaches a reader of the built artifact, and `ast.literal_eval` of the
        assigned dict cannot see a comment even if one is wrong.
        """
        if isinstance(node, str):
            return [node]
        if isinstance(node, dict):
            out = []
            for key, value in node.items():
                out.extend(
                    TheGeneratorAttributesItsUntrainedQcrClaim
                    ._emitted_strings(key))
                out.extend(
                    TheGeneratorAttributesItsUntrainedQcrClaim
                    ._emitted_strings(value))
            return out
        if isinstance(node, (list, tuple)):
            out = []
            for value in node:
                out.extend(
                    TheGeneratorAttributesItsUntrainedQcrClaim
                    ._emitted_strings(value))
            return out
        return []

    def _unattributed(self, text: str) -> list[str]:
        return [s for s in _sentences(text)
                if _QCR.search(s) and not _CITED.search(s)]

    def test_the_control_is_live(self):
        """The guard must be exercising something.

        If no emitted string names QCR at all, every assertion below passes
        vacuously -- the failure mode where a rule survives the deletion of its
        subject and goes on reporting clean.
        """
        emitted = self._emitted_strings(self._closure_literal())
        naming = [s for s in emitted if _QCR.search(s)]
        self.assertTrue(naming,
                        "no string the generator emits names QCR; this "
                        "guard's subject is gone and it is grading nothing")

    def test_every_emitted_sentence_naming_qcr_names_spalart_2000(self):
        faults = []
        for text in self._emitted_strings(self._closure_literal()):
            faults.extend(self._unattributed(text))
        self.assertEqual(
            [], faults,
            "the generator emits a QCR claim about our own model with no "
            "attribution in the same sentence. V5 requires Spalart (2000) "
            "beside the untrained claim, and this literal is written into "
            "benchmarks.json, wall/wall.json and the dist/ snapshot on the "
            "next build:\n  " + "\n  ".join(faults))

    def test_the_mutant_is_caught(self):
        """The negative control, in-process.

        A guard that has never been shown red is a guard that has never been
        shown to grade. The mutation removes only the attribution and leaves
        the claim standing, which is exactly the pre-repair state of
        `build_benchmarks.py:106`.
        """
        clean = ("round-5 untrained QCR2000 forward solve on the ducts, whose "
                 "one coefficient Ccr1 = 0.3 is Spalart (2000)'s published "
                 "constant, adopted untrained and overridden nowhere.")
        self.assertEqual([], self._unattributed(clean))
        mutant = "round-5 untrained QCR2000 forward solve on the ducts."
        self.assertEqual([mutant], self._unattributed(mutant))
        # "Spalart" without the year is the 1992 SA model, not the QCR source.
        near = ("round-5 untrained QCR2000 forward solve on the ducts, "
                "Spalart's constant.")
        self.assertEqual([near], self._unattributed(near))

    def test_the_shipped_json_surfaces_carry_the_attribution(self):
        """The literal is the subject, but a stale output is the same defect
        one step later, so the two in-tree artifacts are read as well.

        `dist/certonomous-demo/snapshot/lab_stats.json` is the fourth face of
        this string and is gitignored with a designated owner; it is reported
        rather than asserted here.
        """
        for rel in ("demo-output/website/benchmarks.json",
                    "demo-output/website/wall/wall.json"):
            path = REPO / rel
            self.assertTrue(path.exists(), f"{rel} is gone")
            faults = []
            for text in self._emitted_strings(
                    json.loads(path.read_text(encoding="utf-8"))):
                faults.extend(self._unattributed(text))
            self.assertEqual([], faults,
                             f"{rel} states a QCR claim with no attribution "
                             f"in the same sentence:\n  " + "\n  ".join(faults))


if __name__ == "__main__":
    unittest.main()
