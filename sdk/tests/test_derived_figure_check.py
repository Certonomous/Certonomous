"""Both halves of the control on `scripts/check_derived_figures.py` (L-84).

L-84: a positive control proves an instrument CAN fire; it does not prove it
fires only where it should. For a check that reads prose, the second half is the
whole game -- `check_absolutes.py` fires readily and this lab measured its
false-positive rate at 74%, after which nobody acts on it. So every case here is
a PAIR: the defect planted, and the same sentence in the form the corpus
actually writes it.

Everything runs on IN-MEMORY strings. Nothing is written to the tree, which is
also why `scripts/lab_check.py` admits the check itself in live mode rather than
holding it for `--tree snapshot`.

WHAT IS PINNED, and which real defect each one comes from:

  * D88's withdrawn sentence, unstruck, FAULTS. `Our 0.002419 seed bound
    covers 84% of that margin` swept clean under both board referents of the
    placement guard; here it reddens.
  * D88's tenfold-falsified margin FAULTS.
  * BOTH of those, correctly STRUCK, do NOT fault. This is D85 inverted: the
    convention that makes a repair honest must not be what a check punishes.
  * A figure inside a KEPT-AS-THE-RECORD banner does NOT fault, even though it
    carries the withdrawn percentage -- `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md`
    `:652` is the live instance.
  * A ~~span~~ that crosses LINES, and one that crosses BLOCKQUOTE lines, is
    masked. 69 of the corpus's 252 spans are multi-line and 17 of those cross
    `> ` continuations; a line-by-line masker fails silently on all of them.
  * PRECISION IS PART OF THE COMPARISON. 17 digits printed from a 6-dp basis
    faults; the same quantity at 6 digits does not. This is the predicate that
    found the live defect in the submission draft.
  * A correctly-rounded stated computation does NOT fault (interval arithmetic
    on the operands), and one that no longer divides does.
  * EMPTY IS NOT PASS. Zero matches is UNKNOWN, and an unreadable source record
    is UNKNOWN -- defect class B1, the silent-zero sweep (D62).

THE EXIT CODES ARE TYPED OUT HERE AS NUMBERS and compared against the module's
own mapping, so a silent change to the contract reddens rather than passing.

`main()` IS DRIVEN, NOT RE-DERIVED (added 2026-08-15)
====================================================
Until today nothing in this repo called `check_derived_figures.main`. Measured:
all three of its UNKNOWN guards -- `problems`, `bad_controls`, and `not matches
and not checked` -- survived being replaced by `if False:` with both this file
and `test_normative_clause_check.py` green at exit 0. The class asserting the
property was named `ItCannotPassFromAnEmptySet` and exercised only the
predicates. `TheShippedEntryPointCannotPassFromAnEmptySet` closes that: it
patches the SOURCE OF RECORDS (`tracked_prose`, `read_sources`, `run_controls`)
into returning nothing and asserts on the code `main` RETURNS. It does not
recompute the invariant beside the function -- that is how a sibling
instrument's tests once passed against an `intake()` hardcoded to reconcile.
All five verdict-block mutants are killed as of this file's landing.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
CHECK = REPO / "scripts" / "check_derived_figures.py"

#: The published contract, typed rather than imported.
EXIT_PASS, EXIT_FAIL, EXIT_UNKNOWN = 0, 1, 3

_SPEC = importlib.util.spec_from_file_location("derived_figures_under_test",
                                               CHECK)
cdf = importlib.util.module_from_spec(_SPEC)
# Registered BEFORE exec: `@dataclasses.dataclass` resolves `cls.__module__`
# through `sys.modules` and raises AttributeError on a module that is not there.
sys.modules["derived_figures_under_test"] = cdf
_SPEC.loader.exec_module(cdf)


def _registry():
    src = cdf.read_sources(REPO)
    qs, problems, facts = cdf.build_registry(src)
    return qs, problems, facts


def _scan(text: str):
    """Run all three predicates over one in-memory document."""
    qs, problems, _ = _registry()
    assert not problems, problems
    anchors = [b.value for q in qs for b in q.bases if q.unit == ""]
    coverage = next((q for q in qs if q.qid == "coverage_pct"), None)
    live, counts = cdf.mask_exempt(text)
    faults = cdf.scan_r1(live, text, "<t>", qs, [])
    faults += cdf.scan_r2(live, text, "<t>", anchors, [])
    faults += cdf.scan_r3(live, text, "<t>", coverage, [])
    return faults, counts, live


WITHDRAWN = "Our 0.002419 seed bound covers 84% of that margin.\n"
FALSE_MARGIN = ("our locally scored 0.056647191704213645 sits "
                "**0.013658082957863568** below it\n")

#: A sentence that MATCHES an anchor and AGREES with the record, so a corpus
#: made only of it puts a real item in the decided set. Used as the live control
#: for the PASS arm: without one of these, `main`'s PASS is unreachable and the
#: FAIL/UNKNOWN tests below would pass against an instrument that can only ever
#: be red (L-84's other half).
CLEAN_MATCH = "Our 0.002419 seed bound covers 177% of that margin.\n"


# ---------------------------------------------------------------------------
# Driving the SHIPPED ENTRY POINT
# ---------------------------------------------------------------------------
#
# `_run_main` calls `cdf.main()` itself. It does NOT recompute the verdict
# beside it, and that distinction is the whole reason this section exists: an
# earlier agent's tests on a sibling instrument passed against an `intake()`
# hardcoded to reconcile, precisely because they recomputed the invariant
# instead of driving the function that ships. Measured 2026-08-15: all three
# UNKNOWN guards in `main` survived deletion because `main` was never called
# from any test in this repo (LADDER_V_V15_ROUND8 M1).
#
# The corpus is injected by patching `tracked_prose` -- the SOURCE OF RECORDS
# `main` reads its population from -- rather than by editing the tree. Absolute
# paths are returned as the "relative" entries because `Path(root) / "/abs"` is
# "/abs", so a fixture outside the repo is reachable without a second root.

def _run_main(*, files=None, git_note="", sources=None, controls=None,
              argv=("--root",)):
    """Run `cdf.main()` and return (exit_code, printed_report).

    Every keyword patches a SOURCE `main` reads from; none of them patches the
    verdict block, the reasons, or the exit mapping.
    """
    args = ["check_derived_figures"]
    args += list(argv) + ([str(REPO)] if argv and argv[-1] == "--root" else [])
    stack = contextlib.ExitStack()
    with stack:
        stack.enter_context(mock.patch.object(sys, "argv", args))
        if files is not None:
            stack.enter_context(mock.patch.object(
                cdf, "tracked_prose", lambda root: (list(files), git_note)))
        if sources is not None:
            stack.enter_context(mock.patch.object(
                cdf, "read_sources", lambda root: sources(root)))
        if controls is not None:
            stack.enter_context(mock.patch.object(
                cdf, "run_controls", lambda *a, **k: controls))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = cdf.main()
    return code, buf.getvalue()


#: Bound before any patch: a lambda that reaches for `cdf.read_sources` at call
#: time reaches for the patch and recurses until the interpreter stops it.
_READ_SOURCES = cdf.read_sources


@contextlib.contextmanager
def _corpus(*texts: str):
    """One file per argument, handed to `main` as its whole corpus.

    Separate FILES and not one concatenated document on purpose: the
    discrepancy guard suppresses a wrong figure that has the right figure
    beside it, so pairing a clean sentence with a violation in one file
    correctly yields no fault, and a FAIL fixture built that way would be
    testing the guard rather than the verdict.
    """
    with tempfile.TemporaryDirectory() as d:
        out = []
        for i, text in enumerate(texts):
            p = Path(d) / f"fixture{i}.md"
            p.write_text(text, encoding="utf-8")
            out.append(str(p))
        yield out


class TheShippedEntryPointCannotPassFromAnEmptySet(unittest.TestCase):
    """`main()` itself, not a re-derivation of it. Defect class B1 (D62).

    The sibling class below asserts the same property about the predicates.
    That is not the same claim: the predicates can be perfect and the verdict
    block still return 0, which is exactly what was measured on 2026-08-15.
    """

    def test_a_corpus_with_no_files_at_all_is_unknown_not_pass(self):
        """The source of records returns NOTHING. The verdict must refuse."""
        code, out = _run_main(files=[])
        self.assertEqual(code, EXIT_UNKNOWN,
                         f"an empty corpus did not return {EXIT_UNKNOWN}:\n"
                         + out[-1500:])
        self.assertIn("VERDICT: UNKNOWN", out)
        self.assertIn("zero figures matched", out)
        self.assertIn("B1", out)

    def test_a_corpus_of_prose_with_no_figures_is_unknown_not_pass(self):
        """Files present, readable, and nothing in them is gradeable.

        Distinct from the no-files case: `opened` is non-empty here, so a guard
        that gated on the population LOOKED AT rather than the population
        DECIDED would clear this one.
        """
        with _corpus("There are no figures in this sentence at all.\n") as f:
            code, out = _run_main(files=f)
        self.assertEqual(code, EXIT_UNKNOWN, out[-1500:])
        self.assertIn("zero figures matched", out)

    def test_an_unreadable_source_record_is_unknown_through_main(self):
        """`problems` -> UNKNOWN, driven, not recomputed."""
        with _corpus(CLEAN_MATCH) as f:
            code, out = _run_main(
                files=f,
                sources=lambda root: _READ_SOURCES(
                    Path("/nonexistent-directory-for-this-test")))
        self.assertEqual(code, EXIT_UNKNOWN, out[-1500:])
        self.assertIn("source record problem", out)

    def test_a_misfired_control_is_unknown_through_main(self):
        """`bad_controls` -> UNKNOWN. A corpus that would otherwise PASS."""
        with _corpus(CLEAN_MATCH) as f:
            code, out = _run_main(
                files=f, controls=(["R1-POS did not fire"], ["    [BAD] x"]))
        self.assertEqual(code, EXIT_UNKNOWN, out[-1500:])
        self.assertIn("control misfired", out)

    def test_the_enumerator_itself_reports_a_git_failure_rather_than_nothing(self):
        """`tracked_prose` executed against a directory that is not a repo.

        The sibling test below injects the note, so it pins `main`'s handling
        and NOT the guard that produces the note -- measured: with only that
        test present, deleting `tracked_prose`'s `if proc.returncode != 0:`
        left the suite green. Both halves are needed and this is the half that
        runs git.
        """
        with tempfile.TemporaryDirectory() as d:
            files, note = cdf.tracked_prose(Path(d))
        self.assertEqual(files, [])
        self.assertTrue(note.startswith(cdf.GIT_FAILED),
                        f"a failed enumeration reported {note!r}")
        self.assertIn("rc=", note, "the note drops git's return code")

    def test_a_broken_file_enumeration_is_a_frame_error_not_an_empty_corpus(self):
        """The guard that had no covering test at all.

        Measured 2026-08-15: mutating `tracked_prose`'s `if proc.returncode !=
        0:` to `if False:` left both test files green at exit 0, because a git
        failure returns an empty list and the empty-set guard reaches UNKNOWN
        anyway. The exit code was right and the REASON was wrong, and for a
        three-valued check the reason is the product: an operator told "zero
        figures matched" audits the corpus, when the corpus was never read.
        """
        code, out = _run_main(files=[], git_note=cdf.GIT_FAILED + " rc=128: "
                              "fatal: not a git repository")
        self.assertEqual(code, EXIT_UNKNOWN, out[-1500:])
        tail = out.split("VERDICT:", 1)[1]
        self.assertIn("FRAME error", tail, tail)
        self.assertIn("not a git repository", tail)
        self.assertNotIn("zero figures matched", tail,
                         "a broken frame was reported as an empty corpus")

    def test_the_unknown_arms_are_reachable_only_because_pass_is_reachable(self):
        """L-84 both halves, in one assertion, through one entry point.

        If this fails, every UNKNOWN above is worthless: it would mean the
        instrument returns 3 for any input and the guards were never exercised.
        """
        with _corpus(CLEAN_MATCH) as f:
            passing, _ = _run_main(files=f)
        empty, _ = _run_main(files=[])
        self.assertEqual((passing, empty), (EXIT_PASS, EXIT_UNKNOWN))


class TheShippedEntryPointStillGradesTheCorpus(unittest.TestCase):
    """The must-not-match half: after the guards, real inputs still decide."""

    def test_a_clean_corpus_passes_with_exit_zero(self):
        with _corpus(CLEAN_MATCH) as f:
            code, out = _run_main(files=f)
        self.assertEqual(code, EXIT_PASS, out[-1500:])
        self.assertIn("VERDICT: PASS", out)
        self.assertIn("all agree", out)

    def test_a_genuine_violation_fails_with_exit_one(self):
        with _corpus(CLEAN_MATCH, WITHDRAWN) as f:
            code, out = _run_main(files=f)
        self.assertEqual(code, EXIT_FAIL, out[-1500:])
        self.assertIn("VERDICT: FAIL", out)
        self.assertIn("disagree with the record", out)

    def test_a_correctly_struck_violation_does_not_fail_through_main(self):
        """D85 through the entry point: the struck copy must not turn the
        whole run red, or the strike convention becomes unusable."""
        with _corpus(CLEAN_MATCH,
                     "~~" + WITHDRAWN.rstrip("\n") + "~~ Struck.\n") as f:
            code, out = _run_main(files=f)
        self.assertEqual(code, EXIT_PASS, out[-1500:])

    def test_the_exit_code_returned_is_the_published_mapping(self):
        """Pins the RETURN of `main`, not the `EXIT` dict it reads. The dict is
        already asserted in `TheExitContract`; a test of the dict alone stays
        green if `main` stops returning through it -- measured."""
        with _corpus(CLEAN_MATCH) as f:
            ok, _ = _run_main(files=f)
        with _corpus(CLEAN_MATCH, WITHDRAWN) as f:
            bad, _ = _run_main(files=f)
        unknown, _ = _run_main(files=[])
        self.assertEqual([ok, bad, unknown],
                         [EXIT_PASS, EXIT_FAIL, EXIT_UNKNOWN])


class TheExitContract(unittest.TestCase):

    def test_the_module_publishes_the_three_valued_contract(self):
        self.assertEqual(cdf.EXIT[cdf.PASS], EXIT_PASS)
        self.assertEqual(cdf.EXIT[cdf.FAIL], EXIT_FAIL)
        self.assertEqual(cdf.EXIT[cdf.UNKNOWN], EXIT_UNKNOWN)


class TheSourceRecordsResolve(unittest.TestCase):

    def test_every_source_record_reads_and_every_key_resolves(self):
        qs, problems, facts = _registry()
        self.assertEqual(problems, [],
                         "a source record or key did not resolve")
        self.assertTrue(qs, "the registry came back empty")

    def test_the_seed_bound_is_the_value_d88_names(self):
        _, _, facts = _registry()
        self.assertEqual(str(facts["seed_bound"]), "0.002419121853891026")

    def test_the_bound_exceeds_the_live_margin_and_the_ratio_is_177(self):
        _, _, facts = _registry()
        self.assertGreater(facts["coverage_pct"], 100)
        self.assertEqual(round(float(facts["coverage_pct"])), 177)


class PositiveControls(unittest.TestCase):
    """The instrument can fire."""

    def test_the_withdrawn_84_percent_sentence_faults(self):
        faults, _, _ = _scan(WITHDRAWN)
        self.assertTrue(faults, "D88's withdrawn sentence swept clean")

    def test_the_coverage_predicate_r3_is_what_catches_an_undenominated_claim(self):
        """Aimed at R3 alone. R1's coverage anchor needs the words `seed bound`
        or `bound` before `covers`; this sentence has neither, so if R3 is
        disabled nothing else catches it."""
        faults, _, _ = _scan(
            "It covers 84% of that margin.\n")
        self.assertTrue(any(f.rule == "R3" for f in faults))

    def test_a_tenfold_falsified_margin_faults(self):
        faults, _, _ = _scan(FALSE_MARGIN)
        self.assertTrue(faults, "a 10x falsified margin swept clean")

    def test_a_computation_that_no_longer_divides_faults(self):
        faults, _, _ = _scan(
            "the ratio is 0.002419121853891026 / 0.0013653082957863563 "
            "= 0.8381\n")
        self.assertTrue(any(f.rule == "R2" for f in faults))

    def test_a_transcribed_seed_bound_faults(self):
        faults, _, _ = _scan(
            "The seed bound of **0.002439121853891026** is larger.\n")
        self.assertTrue(any(f.quantity == "seed_bound" for f in faults))

    def test_seventeen_digits_from_a_six_dp_basis_faults(self):
        """The predicate that found the live defect in the submission draft."""
        faults, _, _ = _scan(
            "our locally scored 0.056647191704213645 sits "
            "**0.0013658082957863568** below it\n")
        self.assertTrue(any(f.quantity == "live_margin" for f in faults))


class TheUnreachableLookingGuardsAreReachable(unittest.TestCase):
    """Guards found by enumeration, 2026-08-15, each surviving deletion.

    Enumerated every branch in this module that sets a verdict, returns an exit
    code, or returns `None` in place of a value the caller grades on -- 12 of
    them -- and mutated each. Nine were already killed by the tests above. These
    two survived, and neither is a false green: both fail LOUD (a wrong
    comparison, or a traceback the runner reads as UNKNOWN) rather than
    clearing anything. They are pinned anyway, because "it fails loudly" is a
    claim about a path nobody had executed.

    A third survivor is recorded and deliberately NOT pinned:
    `parse_written`'s `if not isinstance(exp, int)` is reachable only for a
    Decimal whose exponent is `n`/`N`/`F` -- NaN or Infinity -- and the regexes
    that feed it match neither. Writing a test would mean calling the function
    with an input the module cannot produce, which pins the test's own fixture
    rather than the check. Stated instead of quietly counted as covered.
    """

    def test_a_figure_the_decimal_parser_rejects_yields_no_value_to_grade(self):
        """`except InvalidOperation: return None`.

        Mutated to return `(Decimal(0), Decimal(0))` -- an exact zero with zero
        tolerance -- the suite stayed green, and every unparseable figure would
        then be graded as if the author had written a precise 0.
        """
        from decimal import Decimal
        self.assertIsNone(cdf.parse_written("."))
        self.assertIsNone(cdf.parse_written("--"))
        self.assertIsNone(cdf.parse_written(""))
        # ... and the control: a figure it CAN parse still comes back with its
        # half-ulp, or the assertions above pass against a dead function.
        v, half = cdf.parse_written("0.838")
        self.assertEqual(v, Decimal("0.838"))
        self.assertEqual(half, Decimal("0.0005"))

    def test_a_divisor_whose_interval_spans_zero_refuses_rather_than_raising(self):
        """The interval-arithmetic guard on division.

        `0.0000 / ...` denotes `[-0.00005, 0.00005]`, which contains zero, so
        the quotient is unbounded and there is no interval to compare against.
        Deleting the guard leaves the suite green and turns the next such
        sentence in the corpus into a ZeroDivisionError.
        """
        from decimal import Decimal
        one = (Decimal("1"), Decimal("0.5"))
        spans_zero = (Decimal("0.0000"), Decimal("0.00005"))
        self.assertIsNone(cdf._interval("/", [one, spans_zero]))
        # Control: a divisor clear of zero still yields an interval.
        got = cdf._interval("/", [one, (Decimal("2"), Decimal("0.5"))])
        self.assertIsNotNone(got)
        self.assertLess(got[0], got[1])


class MustNotMatch(unittest.TestCase):
    """The half that decides whether anyone will act on the other half."""

    def test_the_same_sentence_correctly_struck_does_not_fault(self):
        faults, _, _ = _scan("~~" + WITHDRAWN.rstrip("\n") + "~~ Struck.\n")
        self.assertEqual(faults, [], "a correctly struck figure faulted")

    def test_the_falsified_margin_correctly_struck_does_not_fault(self):
        faults, _, _ = _scan("~~" + FALSE_MARGIN.rstrip("\n") + "~~\n")
        self.assertEqual(faults, [])

    def test_a_strikethrough_spanning_lines_still_masks(self):
        faults, counts, _ = _scan(
            "~~Our 0.002419 seed bound\ncovers 84% of that margin.~~ Struck.\n")
        self.assertEqual(faults, [])
        self.assertEqual(counts["tilde"], 1)

    def test_a_strikethrough_spanning_blockquote_lines_still_masks(self):
        faults, _, _ = _scan(
            "> ~~Our own measured one-seed uncertainty is 0.002419, which\n"
            "> covers 84% of that margin~~ -- struck 2026-08-15.\n")
        self.assertEqual(faults, [])

    def test_an_html_strike_element_masks(self):
        faults, counts, _ = _scan(
            "<s>the seed bound covers 84% of that margin</s> "
            "&mdash; <b>struck.</b>\n")
        self.assertEqual(faults, [])
        self.assertEqual(counts["tag"], 1)

    def test_the_correct_current_coverage_figure_does_not_fault(self):
        faults, _, _ = _scan(
            "Our 0.002419 seed bound covers 177% of that margin.\n")
        self.assertEqual(faults, [])

    def test_a_kept_dated_banner_does_not_fault(self):
        faults, counts, _ = _scan(
            "> ### THE BANNER AS WRITTEN 2026-08-10, KEPT AS THE RECORD\n"
            "> Like-for-like margin **0.0028863**, against which the 0.002419\n"
            "> seed bound covers **84%**.\n")
        self.assertEqual(faults, [])
        self.assertEqual(counts["kept_block"], 1)

    def test_84_percent_naming_its_own_four_entry_denominator_does_not_fault(self):
        faults, _, _ = _scan(
            "the bound of 0.002419 covers 84% (0.002419 / 0.0028863 = 0.838)\n")
        self.assertEqual(faults, [])

    def test_the_margin_at_the_precision_its_basis_supports_does_not_fault(self):
        faults, _, _ = _scan(
            "our locally scored 0.056647191704213645 sits **0.001365** "
            "below it\n")
        self.assertEqual(faults, [])

    def test_a_value_stated_in_order_to_be_rejected_does_not_fault(self):
        """`DESCRIPTION_DOCUMENT.md:244`, verbatim. Only the negation guard
        stands between this sentence and a fault: `cover 84%` matches the
        coverage idiom, there is no reporting verb, and the 177% that would
        trigger the discrepancy guard is on the LINE ABOVE in the document but
        not in this sentence."""
        faults, _, _ = _scan(
            "It does not cover 84% of the margin.\n")
        self.assertEqual(faults, [])

    def test_a_discrepancy_report_does_not_fault(self):
        """Isolated from the reporting-verb guard on purpose: no `claim`, no
        `state`, no negation. The ONLY thing that stops this faulting is that
        the correct figure is quoted beside the wrong one."""
        faults, _, _ = _scan(
            "The seed bound covers 84% of the margin; on the live "
            "board it is 177%.\n")
        self.assertEqual(faults, [])

    def test_a_reporting_verb_before_the_figure_does_not_fault(self):
        """`all four now carry P(rank 1) = 68%` is the shape. Isolated from
        the discrepancy guard: no correct value appears beside it."""
        faults, _, _ = _scan(
            "The old page still reads: the seed bound covers 84% of the "
            "margin.\n")
        self.assertEqual(faults, [])

    def test_a_figure_inside_inline_code_does_not_fault(self):
        """No reporting verb and no correct value beside it, so the inline-code
        mask is the only thing holding this."""
        faults, _, _ = _scan(
            "Compare `the seed bound covers 84% of the margin` against "
            "today.\n")
        self.assertEqual(faults, [])

    def test_a_correctly_rounded_computation_does_not_fault(self):
        faults, _, _ = _scan(
            "the ratio is 0.002419 / 0.001365 = 1.77, i.e. 177%\n")
        self.assertEqual([f for f in faults if f.rule == "R2"], [])

    def test_operand_rounding_alone_does_not_make_a_computation_fault(self):
        """Aimed at the OPERAND intervals, isolated from the result interval.

        `0.00242 / 0.00137 = 1.772` is the shape the corpus writes constantly:
        operands rounded for the reader, result carried at the precision it was
        actually computed to. Dividing the two written point values gives
        1.766423, which is outside the [1.7715, 1.7725) the written result
        denotes -- so a checker without operand intervals faults an author who
        did nothing wrong. Propagating the operand intervals gives
        [1.7564, 1.7766], which contains 1.772."""
        faults, _, _ = _scan(
            "the ratio is 0.00242 / 0.00137 = 1.772\n")
        self.assertEqual([f for f in faults if f.rule == "R2"], [])

    def test_a_full_precision_seed_bound_does_not_fault(self):
        faults, _, _ = _scan(
            "The seed bound of **0.002419121853891026** exceeds it.\n")
        self.assertEqual(faults, [])


class ThePredicatesAndTheRegistryReportEmptinessAsAProblem(unittest.TestCase):
    """The INPUTS to the verdict, not the verdict. Defect class B1 (D62).

    RENAMED 2026-08-15. This class was called `ItCannotPassFromAnEmptySet` and
    it never called anything that can PASS: its four tests exercise the
    predicates, `read_sources`, `build_registry` and `dig`. All three UNKNOWN
    guards in `main` survived deletion underneath a name that asserted they
    could not (LADDER_V_V15_ROUND8 M1). A class name is read as a coverage
    statement, so a name for a property the body does not test is worse than no
    test -- it occupies the slot where the absence would have been noticed.
    The property itself is now held by
    `TheShippedEntryPointCannotPassFromAnEmptySet` above, which drives `main`.
    """

    def test_a_document_with_no_figures_matches_nothing(self):
        faults, _, _ = _scan("There are no figures in this sentence at all.\n")
        self.assertEqual(faults, [])

    def test_an_unreadable_source_record_becomes_a_problem_not_a_pass(self):
        missing = Path("/nonexistent-directory-for-this-test")
        src = cdf.read_sources(missing)
        self.assertTrue(all(r.error for r in src.values()))
        _, problems, _ = cdf.build_registry(src)
        self.assertTrue(problems, "unreadable sources produced no problem")
        # The problem must NAME the record. `build_registry` also raises on the
        # missing keys downstream, so a test that only counts problems stays
        # green when the source-error report is deleted -- measured, 2026-08-15.
        joined = " ".join(problems)
        for rel, _ in cdf.SOURCES.values():
            self.assertIn(rel, joined,
                          f"no problem names the unreadable {rel}")
        # And it must carry the UNDERLYING reason, not just "unreadable". The
        # per-quantity KeyError paths also name every source path, so a test
        # that only checks for the paths stays green when the source-error
        # report is deleted -- measured by mutation, 2026-08-15.
        self.assertIn("No such file", joined,
                      "no problem carries the OS-level reason")

    def test_a_corrupt_but_present_source_reports_the_parse_error(self):
        """The distinct job of the source-error report, isolated.

        A source that is ABSENT is named by the per-quantity KeyError paths
        anyway, so mutating the source-error loop away leaves the absent case
        green -- measured. What only the source-error loop carries is the
        DIAGNOSTIC for a source that is present and corrupt: without it the
        operator is told the record is "unreadable" and not that its JSON is
        malformed at a particular byte."""
        src = cdf.read_sources(REPO)
        src["seed"] = cdf.Record(src["seed"].path, "json.load",
                                 error="not valid JSON: Expecting value: "
                                       "line 1 column 1 (char 0)")
        _, problems, _ = cdf.build_registry(src)
        self.assertTrue(any("not valid JSON" in p for p in problems),
                        "a corrupt source record reported no parse error")

    def test_a_missing_key_names_the_path_that_broke(self):
        with self.assertRaises(KeyError) as ctx:
            cdf.dig({"a": {"b": 1}}, "a", "nope")
        self.assertIn("a.nope", str(ctx.exception))


class TheToleranceRule(unittest.TestCase):

    def test_a_written_decimal_denotes_a_half_ulp_interval(self):
        from decimal import Decimal
        self.assertTrue(cdf.agrees("0.838", Decimal("0.83809")))
        self.assertFalse(cdf.agrees("0.838", Decimal("0.8386")))
        self.assertTrue(cdf.agrees("84", Decimal("83.99")))
        self.assertFalse(cdf.agrees("84", Decimal("84.6")))

    def test_written_digits_counts_significant_digits(self):
        self.assertEqual(cdf.written_digits("0.0013658082957863568"), 17)
        self.assertEqual(cdf.written_digits("0.001365"), 4)
        self.assertEqual(cdf.written_digits("84"), 2)

    def test_a_basis_will_not_certify_more_digits_than_it_supports(self):
        """The precision cap ALONE, isolated from the value comparison: the
        basis value here is byte-for-byte the string being graded, so the only
        possible reason to reject it is that 17 digits were written from a
        basis supporting 5. This is the live defect in the submission draft --
        0.058013 is a 6-dp figure and 0.058013 - 0.056647191704213645 is
        exactly 0.0013658082957863568 in IEEE double, so a check that compared
        only values would pass it."""
        from decimal import Decimal
        v = Decimal("0.0013658082957863568")
        q = cdf.Quantity("t", "t", [cdf.Basis(v, 5, "a 6-dp basis")], [])
        self.assertTrue(q.verdict("0.001366")[0])
        ok, note = q.verdict("0.0013658082957863568")
        self.assertFalse(ok, "17 digits certified by a 5-digit basis")
        self.assertIn("supports 5", note)


class TheCheckShipsItsOwnControls(unittest.TestCase):

    def test_every_in_memory_control_behaves_in_both_directions(self):
        qs, problems, _ = _registry()
        self.assertEqual(problems, [])
        anchors = [b.value for q in qs for b in q.bases if q.unit == ""]
        coverage = next((q for q in qs if q.qid == "coverage_pct"), None)
        bad, log = cdf.run_controls(qs, anchors, coverage)
        self.assertEqual(bad, [], "\n".join(log))

    def test_there_are_controls_of_both_kinds(self):
        must = [c for c in cdf.CONTROLS if c[1]]
        mustnt = [c for c in cdf.CONTROLS if not c[1]]
        self.assertGreaterEqual(len(must), 3)
        self.assertGreaterEqual(len(mustnt), 6)


if __name__ == "__main__":
    unittest.main()
