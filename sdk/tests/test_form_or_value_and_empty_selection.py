"""D174 and D175: the declared FORM-or-VALUE column, and the empty selection.

TWO DEFECTS, one file, because they are the same defect at two depths.

D174, THE CLASS. A census over `self_audit.CHECKS`, read by import, classified
every check by its PREDICATE -- by what its FAIL establishes. At 82fb3d46 that
was 17 grading VALUE, 15 grading FORM where the claim's failure mode is VALUE,
and 2 where form is genuinely the whole requirement. The 15 pass well-formed
falsehoods, and their greens get quoted as if they were statements about
truth. The fix is one declared column plus the thing a declaration needs to not
BE the defect: `check_every_check_states_its_basis` already proves a non-empty
string is worth nothing, because `check_studies_carry_what_the_fit_records`
declared EVIDENCE -- "re-derives a published number" -- two lines above a
`blind_to` reading "every VALUE. It compares key sets only", and passed.

So a VALUE declaration must PROVE ITSELF, and the rule that cannot be satisfied
by wording is the PROBE: the check is run again with the record it names made
unreadable, and its verdict must MOVE.

D175, THE RESIDUAL. The 2026-08-15 sweep caught SOURCE ABSENCE. It did not
catch EMPTY SELECTION: source present, readable, non-empty, and the check's own
selector picks nothing out of it. Measured by execution, EIGHTEEN checks
returned PASS that way -- not the nine D174 filed. The worst returned "the wall
quotes the current entry of record" with `wall.json` repointed at a path that
does not exist.

EVERY POSITIVE CONTROL BELOW USES REAL TEXT where the defect was real: the
contradiction tests read the live `blind_to` out of `self_audit.BASIS` rather
than inventing a sentence, and every empty-selection probe hands its check a
REAL, NON-EMPTY source that simply does not select.
"""

from __future__ import annotations

import builtins
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "self_audit_under_test", _REPO / "scripts" / "self_audit.py")
sa = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = sa
_spec.loader.exec_module(sa)


class _Swap:
    """Rebind module attributes for one test and put them back."""

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __enter__(self):
        self.saved = {k: getattr(sa, k) for k in self.kwargs}
        for key, value in self.kwargs.items():
            setattr(sa, key, value)
        return self

    def __exit__(self, *exc):
        for key, value in self.saved.items():
            setattr(sa, key, value)
        return False


def _named(name, body):
    """A check function with a chosen __name__, for the declaration table."""
    body.__name__ = name
    return body


def _table(check, grade, evidence, basis=sa.PROPERTY, blind="a stated limit"):
    """The four tables the declaration check reads, holding ONE check."""
    return _Swap(
        CHECKS=(check,),
        GRADES={check.__name__: (grade, evidence)},
        BASIS={check.__name__: (basis, "a stated catch", blind, None)},
        _RESULTS_THIS_RUN={})


# The live contradiction, read out of the table rather than invented. This is
# the entry D174 names: EVIDENCE beside a blind_to disclaiming every value.
LIVE_DISCLAIMER = sa.BASIS["check_studies_carry_what_the_fit_records"][2]


class TheContradictionIsCaughtTests(unittest.TestCase):
    """The positive control, and it is a live instance rather than a fixture."""

    def test_the_live_blind_to_really_does_disclaim_value(self):
        """If this text ever stops disclaiming value the controls below are
        testing nothing, so the premise is asserted rather than assumed."""
        self.assertIn("every VALUE", LIVE_DISCLAIMER)
        self.assertIn("compares key sets only", LIVE_DISCLAIMER)

    def test_declaring_value_beside_that_blind_to_FAILS(self):
        check = _named("check_x", lambda: sa.Result("x", sa.PASS, "clean"))
        with _table(check, sa.VALUE, ("scripts/self_audit.py",),
                    blind=LIVE_DISCLAIMER):
            result = sa.check_every_value_claim_names_its_source()
        self.assertEqual(sa.FAIL, result.status, result.summary)
        self.assertTrue(any("disclaims value" in d for d in result.detail),
                        result.detail)

    def test_declaring_basis_EVIDENCE_while_grading_form_FAILS(self):
        """The same live entry from the other direction. EVIDENCE's own
        BASIS_MEANING is a claim that a published NUMBER is re-derived here;
        a form-grader declaring it is a contradiction inside one entry."""
        check = _named("check_x", lambda: sa.Result("x", sa.PASS, "clean"))
        with _table(check, sa.FORM_OVER_VALUE,
                    "a well-formed falsehood that passes it, described at "
                    "enough length to be a real disclosure",
                    basis=sa.EVIDENCE):
            result = sa.check_every_value_claim_names_its_source()
        self.assertEqual(sa.FAIL, result.status, result.summary)
        self.assertTrue(
            any("declares basis EVIDENCE and grades" in d
                for d in result.detail), result.detail)

    def test_the_live_table_no_longer_carries_that_contradiction(self):
        """And the repair is real: the entry now declares PROPERTY, whose own
        meaning is that no number is confirmed."""
        basis, _, blind, _ = sa.BASIS["check_studies_carry_what_the_fit_records"]
        self.assertEqual(sa.PROPERTY, basis)
        self.assertIn("no number is confirmed", sa.BASIS_MEANING[basis])
        self.assertIn("every VALUE", blind)


class AForgedValueDeclarationFailsTests(unittest.TestCase):
    """Rule 4, the one that cannot be satisfied by wording."""

    def setUp(self):
        # `sa.REPO` and NOT this file's own `_REPO`. Under the mutation
        # harness's mirror the audit is reached through a SYMLINK, so
        # `Path(__file__).resolve()` inside it lands on the real repository
        # while this test file resolves to the mirror -- and a declared source
        # written relative to the wrong one of the two is a record the check
        # cannot find. That mismatch turned the harness's control red once and
        # is the reason every path below is anchored on the module under test.
        self.tmp = Path(tempfile.mkdtemp(prefix="forged-", dir=str(sa.REPO)))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.record = self.tmp / "record.json"
        self.record.write_text(json.dumps({"n": 1}))
        self.rel = str(self.record.relative_to(sa.REPO))

    def test_a_check_that_never_reads_the_record_it_names_FAILS(self):
        def body():
            # The path is written into this function and never opened. A
            # textual test would clear it; the probe does not.
            _ = "the record is at record.json"
            return sa.Result("x", sa.PASS, "every value re-derives")
        with _table(_named("check_x", body), sa.VALUE, (self.rel,)):
            result = sa.check_every_value_claim_names_its_source()
        self.assertEqual(sa.FAIL, result.status, result.summary)
        self.assertTrue(any("does not constrain this verdict" in d
                            for d in result.detail), result.detail)

    def test_a_check_that_really_reads_it_PASSES(self):
        """MUST-NOT-MATCH (L-84). The instrument must not simply fail
        everything: a genuine value declaration has to survive it."""
        record = self.record

        def body():
            try:
                data = json.loads(record.read_text())
            except OSError:
                return sa.Result("x", sa.UNKNOWN, "the record did not open")
            return sa.Result("x", sa.PASS, f"n is {data['n']}")
        with _table(_named("check_x", body), sa.VALUE, (self.rel,)):
            result = sa.check_every_value_claim_names_its_source()
        self.assertEqual(sa.PASS, result.status, result.detail)

    def test_a_value_declaration_naming_no_record_FAILS(self):
        check = _named("check_x", lambda: sa.Result("x", sa.PASS, "clean"))
        with _table(check, sa.VALUE, ()):
            result = sa.check_every_value_claim_names_its_source()
        self.assertEqual(sa.FAIL, result.status, result.summary)
        self.assertTrue(any("names NO source record" in d
                            for d in result.detail), result.detail)

    def test_a_record_absent_from_this_box_is_UNKNOWN_not_PASS(self):
        """PRESENT is three-valued on purpose: an absent artifact is a fact
        about the box, so the declaration is UNPROVEN rather than false -- and
        UNPROVEN must not read as agreement."""
        check = _named("check_x", lambda: sa.Result("x", sa.PASS, "clean"))
        with _table(check, sa.VALUE, ("no/such/record.json",)):
            result = sa.check_every_value_claim_names_its_source()
        self.assertEqual(sa.UNKNOWN, result.status, result.summary)
        self.assertTrue(any("UNPROVEN" in d for d in result.detail),
                        result.detail)

    def test_a_form_over_value_declaration_naming_no_falsehood_FAILS(self):
        """The obligation is symmetric, so the form column is not the cheap
        place to sit."""
        check = _named("check_x", lambda: sa.Result("x", sa.PASS, "clean"))
        with _table(check, sa.FORM_OVER_VALUE, "too short"):
            result = sa.check_every_value_claim_names_its_source()
        self.assertEqual(sa.FAIL, result.status, result.summary)
        self.assertTrue(any("names no well-formed falsehood" in d
                            for d in result.detail), result.detail)

    def test_a_form_declaration_that_names_evidence_FAILS(self):
        check = _named("check_x", lambda: sa.Result("x", sa.PASS, "clean"))
        with _table(check, sa.FORM, ("scripts/self_audit.py",)):
            result = sa.check_every_value_claim_names_its_source()
        self.assertEqual(sa.FAIL, result.status, result.summary)


class TheBlindfoldIsHonestTests(unittest.TestCase):
    """A probe is only worth its blindfold. Each hook is exercised."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="blindfold-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_it_hides_the_target_and_leaves_its_sibling_alone(self):
        target = self.tmp / "hidden.txt"
        sibling = self.tmp / "visible.txt"
        target.write_text("secret")
        sibling.write_text("fine")
        with sa._Blindfold(target):
            self.assertFalse(target.exists())
            with self.assertRaises(FileNotFoundError):
                target.read_text()
            with self.assertRaises(FileNotFoundError):
                builtins.open(target)
            self.assertEqual("fine", sibling.read_text())
            self.assertNotIn(target, list(self.tmp.glob("*.txt")))
        self.assertEqual("secret", target.read_text())

    def test_resolving_the_target_does_not_recurse(self):
        """`Path.resolve()` calls `Path.stat`, which the blindfold replaces.
        The first version of `_hidden` resolved through pathlib and recursed
        until the interpreter gave up."""
        target = self.tmp / "hidden.txt"
        target.write_text("x")
        with sa._Blindfold(target):
            self.assertFalse((self.tmp / "hidden.txt").exists())

    def test_it_blinds_a_zip(self):
        archive = self.tmp / "a.zip"
        with zipfile.ZipFile(archive, "w") as handle:
            handle.writestr("m.txt", "hello")
        with sa._Blindfold(archive):
            with self.assertRaises(FileNotFoundError):
                zipfile.ZipFile(archive)
        with zipfile.ZipFile(archive) as handle:
            self.assertEqual(b"hello", handle.read("m.txt"))

    def test_it_blinds_an_import_and_its_compiled_copy(self):
        """The trap this lab has already been bitten by. `SourceFileLoader`
        stats the source through `os.stat` -- which no hook touches -- and then
        reads `__pycache__/<stem>.pyc`, which does not live under the source
        path. Blinding the .py alone leaves the module loading from bytecode."""
        package = self.tmp / "pkg"
        package.mkdir()
        (package / "__init__.py").write_text("")
        module = package / "leaf.py"
        module.write_text("VALUE = 41\n")
        sys.path.insert(0, str(self.tmp))
        self.addCleanup(sys.path.remove, str(self.tmp))
        self.addCleanup(lambda: [sys.modules.pop(n, None)
                                 for n in ("pkg", "pkg.leaf")])
        import pkg.leaf                                   # noqa: PLC0415
        self.assertEqual(41, pkg.leaf.VALUE)
        # The compiled copy now exists; this is the half that must also be hid.
        self.assertTrue(list((package / "__pycache__").glob("leaf.*.pyc")))
        with sa._Blindfold(module):
            self.assertNotIn("pkg.leaf", sys.modules)
            with self.assertRaises((ImportError, FileNotFoundError)):
                importlib.import_module("pkg.leaf")
        self.assertEqual(41, importlib.import_module("pkg.leaf").VALUE)

    def test_it_detaches_the_submodule_from_its_parent_package(self):
        """Evicting sys.modules is not enough: importing a submodule also BINDS
        it on its package, and `from pkg import leaf` then takes the attribute
        without importing anything. Both uq.py declarations read as
        unconstrained until this was fixed."""
        package = self.tmp / "pkg2"
        package.mkdir()
        (package / "__init__.py").write_text("")
        module = package / "leaf.py"
        module.write_text("VALUE = 7\n")
        sys.path.insert(0, str(self.tmp))
        self.addCleanup(sys.path.remove, str(self.tmp))
        self.addCleanup(lambda: [sys.modules.pop(n, None)
                                 for n in ("pkg2", "pkg2.leaf")])
        from pkg2 import leaf                             # noqa: PLC0415
        self.assertEqual(7, leaf.VALUE)
        with sa._Blindfold(module):
            self.assertFalse(hasattr(sys.modules["pkg2"], "leaf"))
        self.assertTrue(hasattr(sys.modules["pkg2"], "leaf"))

    def test_every_hook_is_restored(self):
        import _io                                        # noqa: PLC0415
        before = (Path.read_text, Path.exists, Path.glob, builtins.open,
                  zipfile.ZipFile, _io.open_code)
        target = self.tmp / "x.txt"
        target.write_text("x")
        with sa._Blindfold(target):
            pass
        after = (Path.read_text, Path.exists, Path.glob, builtins.open,
                 zipfile.ZipFile, _io.open_code)
        self.assertEqual(before, after)

    def test_it_restores_even_when_the_body_raises(self):
        target = self.tmp / "x.txt"
        target.write_text("x")
        opener = builtins.open
        with self.assertRaises(RuntimeError):
            with sa._Blindfold(target):
                raise RuntimeError("boom")
        self.assertIs(opener, builtins.open)


class TheRealTableIsCompleteTests(unittest.TestCase):
    """Cheap assertions over the live tables; no probe is run here."""

    def test_every_live_check_declares_form_or_value(self):
        names = {c.__name__ for c in sa.CHECKS}
        self.assertEqual(set(), names - set(sa.GRADES))
        self.assertEqual(set(), set(sa.GRADES) - names)

    def test_the_new_check_is_registered_in_all_four_tables(self):
        name = "check_every_value_claim_names_its_source"
        self.assertIn(name, {c.__name__ for c in sa.CHECKS})
        for table in (sa.BASIS, sa.REMEDIES, sa.GRADES):
            self.assertIn(name, table)

    def test_it_does_not_exempt_itself_from_the_family_it_measures(self):
        kind, falsehood = sa.GRADES[
            "check_every_value_claim_names_its_source"]
        self.assertEqual(sa.FORM_OVER_VALUE, kind)
        self.assertIn("WRONG PROPERTY", falsehood)

    def test_every_form_over_value_entry_names_a_falsehood(self):
        for name, (kind, evidence) in sorted(sa.GRADES.items()):
            if kind == sa.FORM_OVER_VALUE:
                with self.subTest(check=name):
                    self.assertIsInstance(evidence, str)
                    self.assertGreater(len(evidence.strip()), 40, name)

    def test_every_value_entry_names_at_least_one_record(self):
        for name, (kind, evidence) in sorted(sa.GRADES.items()):
            if kind in (sa.VALUE, sa.VALUE_ON_A_PIN):
                with self.subTest(check=name):
                    self.assertTrue(evidence, name)
                    for source in evidence:
                        self.assertTrue(
                            sa._grade_source_path(source).exists(),
                            f"{name} names {source}")

    def test_the_census_matches_the_measured_classification(self):
        """The re-derived census, stated with its frame: 36 checks here, of
        which 18 grade value (one of them on a frozen referent), 16 grade form
        over a claim whose failure mode is value, and 2 grade form where form
        is the requirement. At 82fb3d46, before check_rank_claim_values and
        before this check, the same classification gave 17/15/2 over 34."""
        counts: dict[str, int] = {}
        for check in sa.CHECKS:
            kind = sa.GRADES[check.__name__][0]
            counts[kind] = counts.get(kind, 0) + 1
        self.assertEqual(36, len(sa.CHECKS))
        self.assertEqual(17, counts[sa.VALUE])
        self.assertEqual(1, counts[sa.VALUE_ON_A_PIN])
        self.assertEqual(16, counts[sa.FORM_OVER_VALUE])
        self.assertEqual(2, counts[sa.FORM])

    def test_the_pinned_referent_class_is_declared_and_not_folded_in(self):
        """D176: check_board_placement_words does not merely miss a defect, it
        MANUFACTURES one -- 14 correct statements faulted, three of them
        naming the wrong entrant. That severity gets its own column."""
        kind, sources = sa.GRADES["check_board_placement_words"]
        self.assertEqual(sa.VALUE_ON_A_PIN, kind)
        self.assertIn("README.md", sources[0])
        self.assertIn("FROZEN", sa.GRADES_MEANING[sa.VALUE_ON_A_PIN])


# --------------------------------------------------------------------------
# D175: the empty selection
# --------------------------------------------------------------------------

class TheEmptySelectionIsNotAgreementTests(unittest.TestCase):
    """Eighteen checks, each handed a REAL, NON-EMPTY source that selects
    nothing. Every one of them returned PASS before this repair."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="emptysel-"))
        # Inside `sa.REPO`, so `Path.relative_to(REPO)` inside the check
        # resolves. See the note in AForgedValueDeclarationFailsTests.setUp.
        cls.inrepo = Path(tempfile.mkdtemp(prefix="emptysel-",
                                           dir=str(sa.REPO / "scripts")))
        cls.plain = cls.tmp / "plain.py"
        cls.plain.write_text(
            "def hello():\n    return 'selects under no rule here'\n")
        cls.study = cls.tmp / "out_of_scope.json"
        cls.study.write_text(json.dumps(
            {"body": "x", "levels": [], "note": "no numerical block"}))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)
        shutil.rmtree(cls.inrepo, ignore_errors=True)

    def _assert_empty_selection(self, result):
        self.assertEqual(sa.UNKNOWN, result.status, result.summary)
        joined = " ".join(result.detail)
        # The source is named as READ, the selector is named, and the reason
        # given is the empty-selection one and not the absence one.
        self.assertIn("selector that matched nothing", joined)
        self.assertIn("read, and not empty:", joined)
        self.assertIn("the source was FINE", joined)
        self.assertIn("read the SELECTOR", joined)

    PY_SHARERS = ("check_nonconclusive_band_readers",
                  "check_channel_totals_use_one_rule",
                  "check_declared_fleet_vs_work",
                  "check_restated_thresholds",
                  "check_record_writers_name_their_drops")

    STUDY_SHARERS = ("check_studies_carry_what_the_fit_records",
                     "check_stored_fits_reproduce_their_values",
                     "check_stored_rungs_carry_solved_precision",
                     "check_ladder_rungs_share_one_recipe",
                     "check_declined_ladders_name_their_guard",
                     "check_order_window_declines_state_their_dimensionality")

    def test_the_py_corpus_sharers(self):
        """`_py_corpus` guards an EMPTY corpus. It cannot guard a corpus that
        is present and selects nothing, and all five sharers said 'all 0 ...'
        and PASSed."""
        for name in self.PY_SHARERS:
            with self.subTest(check=name):
                with _Swap(_py_corpus=lambda n: ([self.plain], None)):
                    self._assert_empty_selection(getattr(sa, name)())

    def test_the_stored_study_sharers(self):
        for name in self.STUDY_SHARERS:
            with self.subTest(check=name):
                with _Swap(_stored_studies=lambda n: ([self.study], None)):
                    self._assert_empty_selection(getattr(sa, name)())

    def test_cited_evidence_paths(self):
        web = self.tmp / "web"
        (web / "sub").mkdir(parents=True, exist_ok=True)
        (web / "sub" / "note.md").write_text("A real record citing nothing.\n")
        with _Swap(WEB=web):
            self._assert_empty_selection(sa.check_evidence_paths_exist())

    def test_campaign_json_citations(self):
        camp = self.inrepo / "campaign"
        camp.mkdir(exist_ok=True)
        (camp / "c.json").write_text(json.dumps({"note": "no citation field"}))
        with _Swap(CAMPAIGN=camp):
            self._assert_empty_selection(sa.check_campaign_json_citations())

    def test_register_group_counts(self):
        register = self.tmp / "REGISTER.md"
        register.write_text("# Register\n\nReal file, no '## GROUP' heading.\n")
        with _Swap(REGISTER=register):
            self._assert_empty_selection(sa.check_register_group_counts())

    def test_rung_estimates(self):
        root = self.tmp / "r1"
        agenda = root / "demo-output" / "website" / "agenda"
        agenda.mkdir(parents=True, exist_ok=True)
        (agenda / "docket.json").write_text(json.dumps({"proposals": [
            {"id": "x1", "objective": "write a document",
             "rationale": "no mesh here", "est_core_min": 5,
             "status": "proposed", "cost_basis": "forecast"}]}))
        with _Swap(REPO=root):
            self._assert_empty_selection(
                sa.check_rung_estimates_state_their_iterations())

    def test_gate_table(self):
        published = self.tmp / "GATE.md"
        published.write_text(
            "| act | x | reference | measured | deviation | verdict | n |\n")
        sys.path.insert(0, str(sa.REPO / "scripts"))
        import gate_table                                  # noqa: PLC0415
        saved = gate_table.rows
        gate_table.rows = lambda: []
        try:
            with _Swap(GATE_TABLE=published):
                self._assert_empty_selection(
                    sa.check_gate_table_vs_transcripts())
        finally:
            gate_table.rows = saved

    def test_ungated_completed_runs(self):
        web = self.tmp / "lweb"
        (web / "campaign").mkdir(parents=True, exist_ok=True)
        (web / "campaign" / "F5a_cylinder_reynolds_ladder.md").write_text(
            "# Ladder\n\nA real record. It names no completed run.\n")
        with _Swap(WEB=web):
            self._assert_empty_selection(sa.check_ungated_completed_runs())

    def test_the_closure_wall_empty_block(self):
        wall = self.tmp / "wall_empty.json"
        wall.write_text(json.dumps(
            {"counters": {"research": {"closure": {}}}}))
        with _Swap(WALL=wall):
            self._assert_empty_selection(sa.check_closure_entry_of_record())


class TheTwoReasonsAreDifferentTests(unittest.TestCase):
    """'I could not read the source' and 'I read it and selected nothing' are
    different failures with different remedies, so they say different things."""

    def test_absence_and_empty_selection_do_not_share_a_sentence(self):
        absent = sa._no_evidence("x", "s", ["a/b"])
        empty = sa._no_selection("x", "s", ["a/b"], "a selector")
        self.assertEqual(sa.UNKNOWN, absent.status)
        self.assertEqual(sa.UNKNOWN, empty.status)
        self.assertTrue(any(d.startswith("not read:") for d in absent.detail))
        self.assertTrue(any(d.startswith("read, and not empty:")
                            for d in empty.detail))
        self.assertIn("an empty sweep is not agreement",
                      " ".join(absent.detail))
        self.assertIn("read the SELECTOR", " ".join(empty.detail))
        self.assertNotIn("read the SELECTOR", " ".join(absent.detail))

    def test_an_absent_wall_is_a_FAIL_because_the_wall_is_the_SUBJECT(self):
        """D174's own ruling, and the file's SUBJECT-versus-EVIDENCE rule. The
        sibling check_wall_counters_vs_ledger FAILs on the same absence, and
        the two must not read one missing file in opposite directions."""
        with _Swap(WALL=Path("/no/such/wall.json")):
            result = sa.check_closure_entry_of_record()
        self.assertEqual(sa.FAIL, result.status, result.summary)
        self.assertIn("SUBJECT", " ".join(result.detail))
        with _Swap(WALL=Path("/no/such/wall.json")):
            sibling = sa.check_wall_counters_vs_ledger()
        self.assertEqual(sa.FAIL, sibling.status, sibling.summary)

    def test_an_unreadable_entry_of_record_is_UNKNOWN_because_it_is_EVIDENCE(
            self):
        tmp = Path(tempfile.mkdtemp(prefix="entry-"))
        self.addCleanup(shutil.rmtree, tmp, True)
        with _Swap(WEB=tmp):
            result = sa.check_closure_entry_of_record()
        self.assertEqual(sa.UNKNOWN, result.status, result.summary)


class TheLiveCorpusStillReachesItsVerdictTests(unittest.TestCase):
    """MUST-NOT-MATCH (L-84). Replacing false greens with universal UNKNOWNs is
    the OTHER failure mode. On the real tree every repaired check must still
    reach a real verdict, and not one of them may go UNKNOWN."""

    REPAIRED = (TheEmptySelectionIsNotAgreementTests.PY_SHARERS
                + TheEmptySelectionIsNotAgreementTests.STUDY_SHARERS
                + ("check_evidence_paths_exist", "check_campaign_json_citations",
                   "check_register_group_counts", "check_gate_table_vs_transcripts",
                   "check_rung_estimates_state_their_iterations",
                   "check_ungated_completed_runs",
                   "check_closure_entry_of_record"))

    def test_not_one_repaired_check_goes_unknown_on_the_real_corpus(self):
        for name in self.REPAIRED:
            with self.subTest(check=name):
                result = getattr(sa, name)()
                self.assertNotEqual(
                    sa.UNKNOWN, result.status,
                    f"{name} examined the real corpus and returned UNKNOWN: "
                    f"{result.summary}")

    def test_a_genuine_violation_still_FAILS(self):
        """The other half of must-not-match: the repair must not have made
        anything unable to fail. check_declared_fleet_vs_work carries a live
        finding on this tree."""
        self.assertEqual(sa.FAIL, sa.check_declared_fleet_vs_work().status)

    def test_a_genuinely_clean_selection_still_PASSES(self):
        """A non-empty selection with no fault in it is still a PASS, not an
        UNKNOWN -- the repair is scoped to the EMPTY selection."""
        self.assertEqual(sa.PASS, sa.check_restated_thresholds().status)
        self.assertEqual(sa.PASS, sa.check_nonconclusive_band_readers().status)


if __name__ == "__main__":
    unittest.main()
