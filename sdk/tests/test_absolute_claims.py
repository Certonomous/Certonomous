"""The L-76 checker's own behavioural claims, executed.

WHY THIS FILE EXISTS, and it is not a tidiness exercise. The module
`scripts/check_absolutes.py` was committed at `8a8b5392` enforcing one rule -- no
absolute claim ships without an executed test named beside it -- and it named
thirteen tests of its own. None of the thirteen had ever been committed: not on
disk, and not in history either (`git log --all -S"def <name>"` returns nothing
for all thirteen, so they are fictional rather than deleted). The instrument
failed its own rule on its first surface, which is docket B3c/D32.

It could not report that about itself, and the reason was control flow rather
than judgement. `classify_unit` asked `elif resolved:` BEFORE `elif dangling:`,
so ONE runnable command in the same docstring -- and the module's own USAGE
block is full of them -- laundered every fictional name into `BACKED`. Run on
itself the checker printed BACKED 15, CITES_MISSING_CHECK 0.

WHAT THESE TESTS ARE EVIDENCE FOR. Two things, and they are different:

  * that the ordering defect is fixed and stays fixed -- the `Cites` class
    below, whose must-not-match control is the load-bearing half. A fix that
    made every unit `CITES_MISSING_CHECK` would satisfy a naive check and be
    worthless, so a unit whose every citation resolves is asserted CLEAN in the
    same class (L-84: a positive control proves an instrument can fire, not
    that it fires only where it should).
  * that the module's remaining citations are no longer air. Eleven of the
    thirteen are written here because the claim beside them is load-bearing --
    the frame is derived, the verdict is three-valued, backing is unit-level.
    Two were STRUCK in the module instead of written, and the module says why
    at each site: one named a comparison against a published rate that was
    measured on a different sample, and one named a test of a past sampling act
    that no execution today can re-perform.

MEASURED, not asserted. Replaying this file against a mutant of the module
whose only difference is the branch order -- control and mutant loaded in the
SAME invocation -- exactly two tests fail on the mutant and none on the fix:
`test_a_dangling_name_beside_a_runnable_command_still_fires` and
`test_a_dangling_name_beside_a_resolving_test_still_fires`. The other 21 pass
on both, which is what a must-not-match control is supposed to do: the
ordering was the only defect in the mechanism, and the citations were the
defect in the prose, so a test that pins the prose has no business changing its
answer when the mechanism moves.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location(
    "check_absolutes_under_test", REPO / "scripts" / "check_absolutes.py")
ca = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = ca
_SPEC.loader.exec_module(ca)

#: A name that this suite guarantees resolves, because it is defined here.
#: Tests below cite it to build units that MUST NOT be flagged.
A_REAL_TEST = "test_a_unit_whose_every_citation_resolves_is_not_flagged"

#: Obviously fictional. If either of these ever becomes a real `def`, the
#: must-not-match controls stop controlling anything, so they are worded to
#: make that unlikely and asserted absent from the tracked corpus below.
A_FAKE_TEST = "test_this_name_was_invented_by_the_suite_and_defines_nothing"
ANOTHER_FAKE_TEST = "test_this_second_invented_name_also_defines_nothing"

#: The module's own USAGE line -- the exact shape that did the laundering.
A_RUNNABLE_COMMAND = "python3 scripts/check_absolutes.py --frame tracked"


def _classify(text: str, suffix: str = ".md", **kw):
    """One unit through the single entry point, with an explicit name corpus.

    `known_tests` is passed rather than derived so that no test in this file
    depends on what the tracked corpus happens to contain today.
    """
    kw.setdefault("known_tests", {A_REAL_TEST})
    kw.setdefault("tracked_paths", {"scripts/check_absolutes.py"})
    return ca.classify_unit(text, suffix, **kw)


def _verdicts(claims) -> set[str]:
    return {c.verdict for c in claims}


class CitesMissingCheckOrderingTests(unittest.TestCase):
    """Evidence FOR: a dangling citation is reported even when a sibling
    citation in the same unit resolves, and ONLY then."""

    def test_a_cited_test_that_does_not_exist_is_not_backing(self):
        """The base case: a lone fictional name is a defect, not backing."""
        claims = _classify(
            f"This can never happen again. Evidence: `{A_FAKE_TEST}`.")
        self.assertEqual({ca.CITES_MISSING_CHECK}, _verdicts(claims))
        self.assertTrue(all(c.is_defect for c in claims))
        self.assertIn(A_FAKE_TEST, claims[0].reason)

    def test_a_dangling_name_beside_a_runnable_command_still_fires(self):
        """The exact laundering shape from D32.

        The module's own docstring pairs fictional test names with a USAGE
        block of runnable commands. Before the fix the command won and the
        unit read `BACKED`.
        """
        text = (f"This can never happen again. Evidence: `{A_FAKE_TEST}`, and "
                f"run `{A_RUNNABLE_COMMAND}` to see it.")
        resolved, dangling = ca._named_checks(
            text, {A_REAL_TEST}, {"scripts/check_absolutes.py"})
        self.assertIn("<command>", resolved,
                      "the command must still resolve, or this test proves "
                      "nothing about precedence")
        self.assertEqual([A_FAKE_TEST], dangling)
        claims = _classify(text)
        self.assertEqual({ca.CITES_MISSING_CHECK}, _verdicts(claims))
        self.assertIn("mixed unit", claims[0].reason,
                      "a mixed unit must say it was mixed, so the call is "
                      "reviewable rather than silent")

    def test_a_dangling_name_beside_a_resolving_test_still_fires(self):
        """One real name does not launder four fictional ones.

        This is the design decision the module argues in a comment: the reader
        who spot-checks one citation and finds it good stops checking.
        """
        text = (f"Nothing here can drift. Evidence: `{A_REAL_TEST}`, "
                f"`{A_FAKE_TEST}`, `{ANOTHER_FAKE_TEST}`.")
        resolved, dangling = ca._named_checks(
            text, {A_REAL_TEST}, {"scripts/check_absolutes.py"})
        self.assertEqual([A_REAL_TEST], resolved)
        self.assertEqual(2, len(dangling), dangling)
        claims = _classify(text)
        self.assertEqual({ca.CITES_MISSING_CHECK}, _verdicts(claims))

    def test_a_unit_whose_every_citation_resolves_is_not_flagged(self):
        """THE MUST-NOT-MATCH CONTROL (L-84).

        A fix that returned `CITES_MISSING_CHECK` for everything would pass
        the three tests above. This one fails against such a fix: a unit
        citing only names that resolve is `BACKED`, and `BACKED` is not a
        defect.
        """
        claims = _classify(
            f"This can never happen again. Evidence: `{A_REAL_TEST}`.")
        self.assertEqual({ca.BACKED}, _verdicts(claims))
        self.assertFalse(any(c.is_defect for c in claims))

    def test_a_unit_citing_only_a_runnable_command_is_not_flagged(self):
        """Second must-not-match control: reordering must not demote commands.

        `<command>` is a resolving citation in its own right. The fix moves
        `dangling` ahead of `resolved`; it must not make a command stop
        backing a claim when no dangling name is present.
        """
        claims = _classify(
            f"This can never happen again. Run `{A_RUNNABLE_COMMAND}`.")
        self.assertEqual({ca.BACKED}, _verdicts(claims))

    def test_the_fictional_names_this_suite_relies_on_define_nothing(self):
        """The controls above are only controls while these names are fake."""
        corpus = ca.known_test_names()
        self.assertIn(A_REAL_TEST, corpus,
                      "this suite's own test name must be in the tracked "
                      "corpus, or every positive control here is vacuous")
        for fake in (A_FAKE_TEST, ANOTHER_FAKE_TEST):
            self.assertNotIn(fake, corpus)

    def test_cites_missing_check_is_counted_as_a_defect(self):
        """The docstring's promise that it is `counted as unbacked`."""
        self.assertIn(ca.CITES_MISSING_CHECK, ca.DEFECT_CLASSES)


class TheUnitIsTheWindowTests(unittest.TestCase):
    """Evidence FOR: backing is scoped to one prose unit, no wider, no
    narrower."""

    _SOURCE_SPLIT = '''"""The module docstring. This can never happen again."""


def f():
    """A different docstring entirely. Evidence: `%s`."""
''' % A_REAL_TEST

    _SOURCE_TOGETHER = '''"""The module docstring. This can never happen
again. Evidence: `%s`."""


def f():
    """A different docstring entirely."""
''' % A_REAL_TEST

    def _units(self, source: str):
        return ca.extract_units(source, ".py", "invented.py")

    def test_a_check_named_in_another_paragraph_does_not_back_the_claim(self):
        """A test two docstrings away is invisible to the reader of this one.

        Negative: the absolute is UNBACKED when the citation lives elsewhere.
        Positive control: the SAME citation and the SAME absolute in ONE unit
        is BACKED, so this is a statement about the window and not about the
        checker being unable to see the name at all.
        """
        apart = [c for u in self._units(self._SOURCE_SPLIT)
                 for c in _classify(u.text, ".py", path=u.path,
                                    lineno=u.lineno, kind=u.kind)]
        self.assertEqual({ca.UNBACKED}, _verdicts(apart), apart)

        together = [c for u in self._units(self._SOURCE_TOGETHER)
                    for c in _classify(u.text, ".py", path=u.path,
                                       lineno=u.lineno, kind=u.kind)]
        self.assertEqual({ca.BACKED}, _verdicts(together), together)

    def test_backing_is_unit_level_and_that_is_stated(self):
        """One named test backs EVERY absolute in its unit -- coarse, in the
        lab's favour, and declared rather than discovered.

        Negative control: the same two absolutes with the citation removed are
        both UNBACKED, so `BACKED` below is the citation's doing.
        """
        backed = _classify(
            "This can never happen again, and nothing above is deleted. "
            f"Evidence: `{A_REAL_TEST}`.")
        self.assertGreaterEqual(len(backed), 2, backed)
        self.assertEqual({ca.BACKED}, _verdicts(backed))

        bare = _classify("This can never happen again, and nothing above "
                         "is deleted.")
        self.assertEqual({ca.UNBACKED}, _verdicts(bare))

        doc = ca.__doc__ or ""
        self.assertIn("backing is unit-level", doc,
                      "the coarseness must be STATED in the module, not just "
                      "true of it")

    def test_the_sample_replays_through_the_same_entry_point(self):
        """The measured rate is a rate over the code that swept the corpus.

        If the sample went through a private copy of the classifier, the
        published rate would describe a program nobody runs. Asserted by
        counting calls to `classify_unit` itself.
        """
        records = [
            {"id": "R1", "label": "needs-backing", "family": "never",
             "keyword": "never", "suffix": ".md", "kind": "paragraph",
             "unit_text": "This can never happen again."},
            {"id": "R2", "label": "legitimate", "family": "never",
             "keyword": "never", "suffix": ".md", "kind": "paragraph",
             "unit_text": "Never shorten a published figure without a rerun."},
        ]
        calls: list[str] = []
        real = ca.classify_unit

        def counting(unit_text, suffix=".md", **kw):
            calls.append(unit_text)
            return real(unit_text, suffix, **kw)

        with tempfile.TemporaryDirectory() as d:
            fixture = Path(d) / "sample.json"
            fixture.write_text(json.dumps({"records": records}),
                               encoding="utf-8")
            ca.classify_unit = counting
            try:
                out = ca.measure_against_sample(fixture, known_tests=set())
            finally:
                ca.classify_unit = real
        self.assertEqual([r["unit_text"] for r in records], calls)
        self.assertEqual(2, out["n"])


class TheMeasuredRateIsRecomputedTests(unittest.TestCase):
    """Evidence FOR: the false-positive rate comes off the fixture at call
    time, and no figure is typed anywhere it can go stale."""

    _RECORDS = [
        {"id": "R1", "label": "needs-backing", "family": "never",
         "keyword": "never", "suffix": ".md", "kind": "paragraph",
         "unit_text": "This can never happen again."},
        {"id": "R2", "label": "needs-backing", "family": "none",
         "keyword": "Nothing", "suffix": ".md", "kind": "paragraph",
         "unit_text": "Nothing in the bundle can drift out of date."},
    ]

    def _measure(self, records):
        with tempfile.TemporaryDirectory() as d:
            fixture = Path(d) / "sample.json"
            fixture.write_text(json.dumps({"records": records}),
                               encoding="utf-8")
            return ca.measure_against_sample(fixture, known_tests=set())

    def test_the_sample_measurement_is_recomputed_not_typed(self):
        """Change the labels, and the rate changes with them.

        Positive control on the negative: the two fixtures are identical
        except for the `label` field, so a rate that moved cannot have moved
        for any other reason.
        """
        all_needing = self._measure(self._RECORDS)
        self.assertEqual(2, all_needing["true_positive"])
        self.assertEqual(0.0, all_needing["false_positive_rate_over_flagged"])

        relabelled = [dict(r, label="legitimate") for r in self._RECORDS]
        flipped = self._measure(relabelled)
        self.assertEqual(2, flipped["false_positive"])
        self.assertEqual(1.0, flipped["false_positive_rate_over_flagged"])

    def test_an_empty_sample_yields_no_rate_rather_than_a_zero(self):
        """A rate over nothing is not 0%. The three-valued discipline again,
        one level down."""
        out = self._measure([])
        self.assertIsNone(out["false_positive_rate_over_flagged"])
        self.assertIsNone(out["false_negative_rate_over_needs_backing"])

    def test_the_committed_sample_carries_its_provenance(self):
        """Not a test that the draw happened -- a test that the file states
        the frame and commit it was drawn at, which is what W-5 requires of a
        durable record."""
        data = json.loads(ca.SAMPLE_PATH.read_text(encoding="utf-8"))
        for key in ("drawn_at_commit", "frame", "sampling", "records"):
            self.assertIn(key, data)


class TheVerdictIsThreeValuedTests(unittest.TestCase):
    """Evidence FOR: a file that could not be read is not a file with no
    absolutes."""

    def _tree(self, d: Path):
        good = d / "has_a_claim.md"
        good.write_text("This can never happen again.\n", encoding="utf-8")
        return good

    def test_an_unreadable_file_yields_unknown_not_a_clean_zero(self):
        """A path that raises on read blinds the verdict.

        The unreadable path is a DIRECTORY named `.py`, which raises
        `IsADirectoryError` for any user -- a chmod-based fixture is a no-op
        when the suite runs as root and would silently stop testing anything.

        Positive control: the readable file's claim is still reported. The
        module promises `claims found before that point are still listed`, so
        UNKNOWN must not be an empty result.
        """
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            self._tree(d)
            (d / "raises_on_read.py").mkdir()
            res = ca.audit(root=d, paths=["has_a_claim.md",
                                          "raises_on_read.py"],
                           known_tests=set())
        self.assertEqual("UNKNOWN", res.verdict)
        self.assertEqual(1, res.skips.unreadable, res.skips.words())
        self.assertEqual(1, res.skips.blinding)
        self.assertTrue(res.claims, "claims found before the raise were lost")
        self.assertIn("UNKNOWN because", res.verdict_line())

    def test_an_unparseable_python_file_yields_unknown(self):
        """A `.py` that will not parse is UNKNOWN, not CLEAN.

        Positive control: the identical tree WITHOUT the broken file, whose
        only claim is backed, is CLEAN -- so UNKNOWN here is the parse failure
        and not the checker refusing to reach a verdict in general.
        """
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "clean.md").write_text(
                f"This can never happen again. Evidence: `{A_REAL_TEST}`.\n",
                encoding="utf-8")
            (d / "broken.py").write_text("def (:\n", encoding="utf-8")
            unknown = ca.audit(root=d, paths=["clean.md", "broken.py"],
                               known_tests={A_REAL_TEST})
            clean = ca.audit(root=d, paths=["clean.md"],
                             known_tests={A_REAL_TEST})
        self.assertEqual("UNKNOWN", unknown.verdict)
        self.assertEqual(1, unknown.skips.unparsed, unknown.skips.words())
        self.assertEqual("CLEAN", clean.verdict, clean.report())

    def test_skip_reasons_are_counted_separately_and_said_out_loud(self):
        """`files skipped: N` with no breakdown is a number nobody can
        challenge. Each reason has its own counter and its own word."""
        skips = ca.Skips(binary=1, over_size_cap=2, unreadable=3, unparsed=4)
        self.assertEqual(10, skips.total)
        self.assertEqual(7, skips.blinding,
                         "only the reasons that BLIND the sweep make it "
                         "UNKNOWN; a binary file skipped is narrower, not "
                         "blinder")
        for word in ("binary", "over size cap", "unreadable", "unparseable"):
            self.assertIn(word, skips.words())

    def test_a_caller_named_path_that_does_not_exist_yields_unknown_not_pass(
            self):
        """THE FAIL-OPEN REGRESSION, and it is the one this class exists for.

        `--paths` is the mode every caller outside a derived frame uses, and a
        path handed to it is a CONTRACT: the caller is asserting this file is
        the thing to audit. A path that does not resolve breaks that contract,
        and the only honest answer is UNKNOWN -- the checker cannot say a file
        it never found is clean.

        Before the repair the missing path was dropped before it was ever
        stat-ed, because selection filtered on SUFFIX first: a nonexistent
        `.md` raised `FileNotFoundError` and blinded the verdict correctly,
        while a nonexistent `.json`, `.png` or extensionless path vanished and
        the audit returned CLEAN -- exit 0, PASS. Which of the two happened
        turned on the spelling of the filename, which is not a property any
        verdict may depend on.

        This matters beyond the CLI: it is the shape a repository
        reorganization produces at scale, where every caller naming a moved
        path would have been told PASS by a checker that read nothing.

        Positive control on the negative:
        `test_an_existing_file_outside_the_prose_frame_is_narrower_not_blinder`
        asserts a file that EXISTS and is merely out of frame stays CLEAN, so
        UNKNOWN here is the missing path and not this mode refusing to reach a
        verdict at all.
        """
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            self._tree(d)
            for missing in ("gone.json", "gone.png", "gone"):
                with self.subTest(missing=missing):
                    res = ca.audit(root=d, paths=["has_a_claim.md", missing],
                                   known_tests=set())
                    self.assertEqual(
                        "UNKNOWN", res.verdict,
                        f"a named path that does not exist ({missing}) was "
                        f"reported {res.verdict}; a checker that reads nothing "
                        f"and says PASS is worse than no checker")
                    self.assertEqual(1, res.skips.missing, res.skips.words())
                    self.assertGreaterEqual(res.skips.blinding, 1)
                    self.assertTrue(
                        res.claims,
                        "claims found beside the missing path were lost")
                    self.assertIn("UNKNOWN because", res.verdict_line())

    def test_an_existing_file_outside_the_prose_frame_is_narrower_not_blinder(
            self):
        """THE MUST-NOT-MATCH CONTROL for the test above.

        A repair that blinded on every path outside the prose frame would
        satisfy the regression above and make the checker useless: `--paths`
        would go UNKNOWN whenever a caller named a `.json` beside its `.md`.

        The line the repair draws: EXISTENCE is the caller's contract and a
        breach of it blinds; the prose-SUFFIX filter is the module's own frame
        and narrowing it does not. So a `.json` that exists is skipped,
        counted, said out loud -- and CLEAN.
        """
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "clean.md").write_text(
                f"This can never happen again. Evidence: `{A_REAL_TEST}`.\n",
                encoding="utf-8")
            (d / "data.json").write_text("{}\n", encoding="utf-8")
            res = ca.audit(root=d, paths=["clean.md", "data.json"],
                           known_tests={A_REAL_TEST})
        self.assertEqual("CLEAN", res.verdict, res.report())
        self.assertEqual(0, res.skips.missing, res.skips.words())
        self.assertEqual(0, res.skips.blinding)
        self.assertEqual(1, res.skips.out_of_frame, res.skips.words())


class TheFrameIsDerivedTests(unittest.TestCase):
    """Evidence FOR: the file list is walked, not enumerated."""

    def test_a_surface_nobody_has_ever_named_is_in_frame(self):
        """A file invented inside this test, whose name appears in no list
        anywhere in the repo, is swept the moment it makes a claim.

        A checker that passed this by adding a filename to a list has not
        passed it. Positive control on the filter: a sibling with a suffix
        outside `PROSE_SUFFIXES` is CONSIDERED and then dropped, so `in_frame`
        is a real filter rather than a synonym for `considered`.
        """
        invented = "a-surface-no-list-has-ever-contained.md"
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / invented).write_text("This can never happen again.\n",
                                      encoding="utf-8")
            (d / "not-prose.bin").write_text("never never never\n",
                                             encoding="utf-8")
            res = ca.audit(root=d, frame="worktree", known_tests=set())
        self.assertEqual(2, res.considered, res.frame_block())
        self.assertEqual(1, res.in_frame, res.frame_block())
        self.assertEqual({invented}, {c.path for c in res.claims})
        self.assertEqual("FLAGGED", res.verdict)
        self.assertIn("git ls-files", ca.sweep_mod.FRAMES["tracked"].rule_words)

    def test_the_report_states_the_frame_it_swept(self):
        """A number without its frame is not a measurement (L-75/W-5)."""
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "x.md").write_text("nothing to see\n", encoding="utf-8")
            block = ca.audit(root=d, frame="worktree",
                             known_tests=set()).frame_block()
        for owed in ("frame", "selection rule", "filter applied",
                     "files considered", "files in frame", "files read",
                     "files skipped"):
            self.assertIn(owed, block)


class TheGatesAndTheirCostTests(unittest.TestCase):
    """Evidence FOR: each rejection gate drops what it says it drops, and
    something survives it."""

    #: (gate verdict, a text it must reject, suffix)
    REJECTED = (
        (ca.CODE_TOKEN, "return None when the increments change sign", ".py"),
        (ca.IDIOM, "That did not narrow it at all, and the run stood.", ".md"),
        (ca.BOUNDED, "All three cases pass on the current mesh.", ".md"),
        (ca.NOT_A_PREDICATION,
         "Reverse every face's winding before writing it.", ".md"),
    )

    #: Real specimens of the defect L-76 exists for. None may be gated away.
    SURVIVORS = (
        ("Every rank in this linear-algebra corpus is a word.", ".md"),
        ("It cannot happen again, because the sentences are now in the "
         "repository.", ".md"),
    )

    def test_each_gate_rejects_and_a_positive_control_survives_it(self):
        """Four gates, each with a specimen it must drop; then two real
        specimens from the L-76 case history that must NOT be dropped.

        Without the second half this test is satisfied by a gate that rejects
        everything, which is the failure mode the 74% false-positive rate is
        already measuring the other side of.
        """
        for expected, text, suffix in self.REJECTED:
            with self.subTest(gate=expected):
                self.assertEqual({expected}, _verdicts(_classify(text, suffix)),
                                 text)
        for text, suffix in self.SURVIVORS:
            with self.subTest(specimen=text[:40]):
                verdicts = _verdicts(_classify(text, suffix))
                self.assertIn(ca.UNBACKED, verdicts,
                              f"a real L-76 specimen was gated away: {text}")

    def test_a_reflowed_rule_is_still_a_rule(self):
        """Whitespace is collapsed BEFORE any marker is matched.

        The negative it guards: ` must ` is not present in the raw text of a
        sentence reflowed as `must\\nnever`, so a marker list matched against
        raw text calls a rule sentence an unbacked claim. Positive control:
        the unwrapped twin, identical but for the line break, gets the same
        verdict.
        """
        wrapped = "A published figure must\nnever be shortened without a rerun."
        flat = wrapped.replace("must\nnever", "must never")
        self.assertNotIn(" must ", wrapped.lower(),
                         "the fixture must actually break the marker, or this "
                         "test proves nothing")
        self.assertIn(" must ", ca._flat(wrapped))
        self.assertEqual({ca.RULE}, _verdicts(_classify(wrapped)))
        self.assertEqual({ca.RULE}, _verdicts(_classify(flat)))


class BlastRadiusTests(unittest.TestCase):
    """Evidence FOR: what is built ON a claim is scored, not felt."""

    def test_code_and_rule_surfaces_outrank_narrative(self):
        """Executable source and rule surfaces score above narrative, and a
        surface that is both outranks either.

        Positive control on the negative: a plain narrative path scores zero
        and says `narrative`, so the ordering below is produced by the surface
        and not by every path scoring high.
        """
        code, code_words = ca.blast_radius("scripts/x.py", ".py", "docstring")
        rule, rule_words = ca.blast_radius("docs/charters/X_CHARTER.md", ".md",
                                           "paragraph")
        both, _ = ca.blast_radius("docs/charters/x.py", ".py", "docstring")
        ships, _ = ca.blast_radius("demo-output/website/x.html", ".html",
                                   "page-text")
        narrative, narrative_words = ca.blast_radius("notes/diary.md", ".md",
                                                     "paragraph")
        self.assertEqual(0, narrative)
        self.assertEqual("narrative", narrative_words)
        self.assertGreater(code, narrative)
        self.assertGreater(rule, narrative)
        self.assertGreater(ships, narrative)
        self.assertGreater(both, code)
        self.assertGreater(both, rule)
        self.assertIn("executable source", code_words)
        self.assertIn("rule surface", rule_words)


class TheCheckerClassifiesItselfTests(unittest.TestCase):
    """Evidence FOR: the instrument is inside its own frame, and reports what
    it finds there."""

    def setUp(self):
        self.res = ca.audit(root=REPO, paths=["scripts/check_absolutes.py"])

    def test_no_citation_in_the_checker_dangles(self):
        """The B3c/D32 regression. Every `test_*` name the module cites must
        resolve in the tracked corpus, or this file is short a test."""
        cites = [c for c in self.res.claims
                 if c.verdict == ca.CITES_MISSING_CHECK]
        self.assertEqual([], [c.line() for c in cites])

    def test_the_checker_still_indicts_itself_where_it_should(self):
        """THE MUST-NOT-MATCH CONTROL AT FILE SCALE.

        `test_no_citation_in_the_checker_dangles` would also pass if the
        checker had been quietly switched off. It has not: the module still
        reports unbacked absolutes in its own source, and its verdict on
        itself is FLAGGED rather than a comfortable CLEAN.
        """
        counts = self.res.by_class()
        self.assertGreater(counts.get(ca.BACKED, 0), 0, counts)
        self.assertGreater(counts.get(ca.UNBACKED, 0), 0,
                           "a checker that finds nothing wrong with itself is "
                           "the shape this whole rung is about")
        self.assertEqual("FLAGGED", self.res.verdict)


if __name__ == "__main__":
    unittest.main()
