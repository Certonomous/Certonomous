"""A check that examined nothing must not report agreement. (D123, 2026-08-15.)

DOCKET ROW, corrected: this file was first headed D124, which is the R-ISOLATE
authorship row and has nothing to do with empty sweeps. The row that names this
defect, measures it both ways and asks for exactly this repair is **D123**
("A verification whose reference is gitignored expires the moment it is made").
The precedent row for the UNKNOWN status itself is D118.

WHAT WAS WRONG
--------------
`scripts/self_audit.py:check_ledger_stalls` iterated `_iter_ledger()`, which
returns immediately when the gitignored ledger (`.gitignore:25`) is absent. It
then fell through to its `if not stalls` branch and printed

    [PASS] ledger stall contamination  no row exceeds the stall threshold

having read ZERO ROWS. Measured both ways in one process on 2026-08-15:
ledger present -> WARN, six stall rows carrying 11.3% of published core-hours;
ledger absent -> PASS. The verdict that read cleanest was the one produced by
reading nothing. That is defect class B1.

Its sibling `check_ledger_integrity` returned FAIL on the same absence. Two
checks, one file, opposite readings of the same nothing.

THE SETTLED VERDICT, and it is UNKNOWN in both
----------------------------------------------
The ledger is gitignored and is written by the mega-batch runner, so it is
absent BY DESIGN on a fresh clone, in the laptop bundle, and on any box that
has not run the batch. Its absence is a fact about the box, not about the
record: neither a defect (FAIL) nor a clean reading (PASS) follows from it.

The FAIL was standing in for one case worth catching -- a published counter
with no ledger under it -- and that case belongs to
`check_wall_counters_vs_ledger`, which was measured FAILing on exactly it
(`missions_run: published 208102, ledger says 0`). So nothing is lost by
saying the true thing in the check that owns the ledger's health. That sibling
now returns UNKNOWN for the same absence rather than blaming the wall for a
file that is not there, and this file holds both halves of that settlement.

SUBJECT VERSUS EVIDENCE, the one distinction the rule turns on: a missing
PUBLISHED SURFACE that a check exists to police is a finding (FAIL); missing
EVIDENCE that a check reads in order to police something else is an instrument
problem (UNKNOWN). `check_gate_table_vs_transcripts` and
`check_register_group_counts` are the two deliberate FAIL-on-absence checks and
are named as such in `self_audit.py`.

CONTROLS BOTH WAYS (L-84)
-------------------------
A positive control proves an instrument can fire, not that it fires only where
it should. So each cell below has its opposite: an absent ledger must be
UNKNOWN, a present ledger holding a genuine stall must still WARN and NAME the
stall, and a present clean ledger must still PASS -- and the PASS must state
its denominator, because a PASS that does not say how many rows it read is the
sentence this whole defect hid behind.

MUTATION-PROVED, one mutation per guard site, because an assertion nobody has
seen fail is not evidence. FOURTEEN mutants, all killed, control and mutant in
one invocation with every `__pycache__` purged before each cell (measured
2026-08-15 on a mirror of the tree, `git ls-tree` frame in the docket row):
  * `if not rows:` -> `if False:` in `check_ledger_stalls` reintroduces the
    exact empty-set PASS and must turn the absent-ledger arm red.
  * the same guard removed in `check_ledger_integrity` and in
    `check_wall_counters_vs_ledger`.
  * `_no_evidence` returning PASS defangs every one of the guards added under
    D123 at once, and must turn all of them red together (22 failures).
  * `_py_corpus`'s guard removed (5 checks) and `_stored_studies`' (6 checks).
  * the clean PASS's denominator deleted -- the second, independent barrier.
  * the guard removed one at a time in `check_withdrawn_numbers`,
    `check_evidence_paths_exist`, `check_ungated_completed_runs`,
    `check_fd_grades_current_standard`, `check_statistical_labels`,
    `check_campaign_json_citations` and
    `check_rung_estimates_state_their_iterations`.

WHAT THAT MEASUREMENT FOUND, recorded because the gap is the point of the
exercise. As first written this file proved SIX of the fourteen. Eight guard
sites -- the six checks sharing `_stored_studies` and the seven single-source
checks above -- survived deletion with the suite still green, and the study
guard's own test was NAMED for the empty arm while asserting only the
populated one. The repair to `self_audit.py` was correct on all thirteen when
executed directly; it was the EVIDENCE for eight of them that did not exist.
That is this file's own defect wearing this file's own subject: a test that
examined nothing reported agreement.
"""

from __future__ import annotations

import importlib.util
import json
import io
import contextlib
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
_SOURCE = REPO / "scripts" / "self_audit.py"
_SPEC = importlib.util.spec_from_file_location(
    "self_audit_under_test", _SOURCE)
sa = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = sa
_SPEC.loader.exec_module(sa)


def _mutant(name: str, old: str, new: str):
    """`self_audit` with one substitution, loaded as its own module.

    The copy sits at `<tmp>/scripts/self_audit.py` so that its own
    `parents[1]` REPO lands in the temporary tree and no mutant can read the
    live one by accident.
    """
    text = _SOURCE.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise AssertionError(
            f"mutation {name!r} does not identify one site: "
            f"{text.count(old)} occurrence(s). The code moved; fix the "
            f"mutation rather than deleting this test.")
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    (root / "scripts").mkdir()
    target = root / "scripts" / "self_audit.py"
    target.write_text(text.replace(old, new), encoding="utf-8")
    spec = importlib.util.spec_from_file_location(f"self_audit_{name}", target)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.__keepalive = tmp          # noqa: SLF001 - hold the tempdir open
    return module


# The three ledger fixtures. Rows are the shape `_iter_ledger` yields and the
# stall row is above STALL_SECONDS by a wide margin so the cell does not sit on
# the threshold it is testing.
_CLEAN = [
    {"solver": "simpleFoam", "ok": True, "wall_seconds": 120.0,
     "timestamp": "2026-08-15T00:00:01Z"},
    {"solver": "pimpleFoam", "ok": True, "wall_seconds": 340.5,
     "timestamp": "2026-08-15T00:00:02Z"},
    {"solver": "simpleFoam", "ok": False, "wall_seconds": 12.0,
     "timestamp": "2026-08-15T00:00:03Z"},
]
_STALL = {"solver": "potentialFoam", "ok": True, "wall_seconds": 7200.0,
          "timestamp": "2026-08-15T00:00:04Z"}


class _LedgerCells(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, module, rows, name="ledger.jsonl"):
        path = self.root / name
        path.write_text("".join(json.dumps(r) + "\n" for r in rows),
                        encoding="utf-8")
        module.LEDGER = path
        return path

    def absent(self, module):
        module.LEDGER = self.root / "no-such-ledger.jsonl"
        self.assertFalse(module.LEDGER.exists())


class TestTheAbsentLedgerIsUnknown(_LedgerCells):
    """The defect arm: an absent ledger, in both siblings, in one process."""

    def test_absent_ledger_is_UNKNOWN_and_above_all_is_not_a_PASS(self):
        self.absent(sa)
        result = sa.check_ledger_stalls()
        self.assertEqual(result.status, sa.UNKNOWN)
        self.assertNotEqual(result.status, sa.PASS)

    def test_the_absent_arm_says_why_and_names_the_file(self):
        self.absent(sa)
        detail = " ".join(sa.check_ledger_stalls().detail)
        self.assertIn("ledger.jsonl", detail)
        self.assertIn("empty sweep is not agreement", detail)

    def test_the_absent_arm_does_not_print_the_clean_sentence(self):
        """The exact string the defect published over zero rows."""
        self.absent(sa)
        self.assertNotIn("no row exceeds the stall threshold",
                         sa.check_ledger_stalls().summary)

    def test_both_siblings_read_the_same_nothing_the_same_way(self):
        """The inconsistency this settles: PASS on one side, FAIL on the other."""
        self.absent(sa)
        stalls = sa.check_ledger_stalls()
        integrity = sa.check_ledger_integrity()
        self.assertEqual(stalls.status, sa.UNKNOWN)
        self.assertEqual(integrity.status, sa.UNKNOWN)
        self.assertEqual(stalls.status, integrity.status)

    def test_the_counters_check_does_not_blame_the_wall_for_a_missing_ledger(self):
        self.absent(sa)
        result = sa.check_wall_counters_vs_ledger()
        self.assertEqual(result.status, sa.UNKNOWN)
        self.assertNotIn("disagree", result.summary)


class TestThePresentLedgerStillFires(_LedgerCells):
    """The other half of the control. An instrument that cannot fire is not
    fixed by making it quiet."""

    def test_a_present_ledger_with_a_stall_is_still_reported(self):
        self.write(sa, _CLEAN + [_STALL])
        result = sa.check_ledger_stalls()
        self.assertIn(result.status, (sa.WARN, sa.FAIL))
        self.assertNotEqual(result.status, sa.PASS)
        self.assertNotEqual(result.status, sa.UNKNOWN)

    def test_the_stall_is_NAMED_not_merely_counted(self):
        self.write(sa, _CLEAN + [_STALL])
        detail = " ".join(sa.check_ledger_stalls().detail)
        self.assertIn("potentialFoam", detail)
        self.assertIn("2026-08-15T00:00:04Z", detail)
        self.assertIn("7200", detail)

    def test_a_present_clean_ledger_still_PASSes(self):
        self.write(sa, _CLEAN)
        result = sa.check_ledger_stalls()
        self.assertEqual(result.status, sa.PASS)

    def test_the_clean_PASS_states_its_denominator(self):
        """A PASS that does not say how many rows it read is the sentence the
        defect hid behind for as long as it existed."""
        self.write(sa, _CLEAN)
        self.assertIn("3", sa.check_ledger_stalls().summary)

    def test_integrity_still_finds_a_torn_row_in_a_present_ledger(self):
        path = self.write(sa, _CLEAN)
        with path.open("a", encoding="utf-8") as handle:
            handle.write('{"solver": "simpleFoam", "ok": tr\n')
        result = sa.check_ledger_integrity()
        self.assertEqual(result.status, sa.WARN)
        self.assertIn("do not parse", result.summary)

    def test_integrity_still_PASSes_a_present_intact_ledger(self):
        self.write(sa, _CLEAN)
        self.assertEqual(sa.check_ledger_integrity().status, sa.PASS)


class TestTheSweptCorpora(unittest.TestCase):
    """The same shape in the checks that read a corpus rather than a file.

    Five checks share `_py_sources` and six share the stored-study directory.
    An empty corpus used to read as `all 0 ... ` and PASS in all eleven.
    """

    def setUp(self):
        self._py = sa._py_sources

    def tearDown(self):
        sa._py_sources = self._py

    def test_an_empty_source_corpus_is_UNKNOWN_in_every_check_that_reads_it(self):
        sa._py_sources = lambda: []
        for check in (sa.check_nonconclusive_band_readers,
                      sa.check_channel_totals_use_one_rule,
                      sa.check_declared_fleet_vs_work,
                      sa.check_restated_thresholds,
                      sa.check_record_writers_name_their_drops):
            with self.subTest(check=check.__name__):
                self.assertEqual(check().status, sa.UNKNOWN)

    def test_the_populated_corpus_still_reaches_a_verdict(self):
        """The negative control for the arm above: with the real corpus these
        checks must NOT be UNKNOWN, or the guard would have turned them all
        off rather than made them honest."""
        for check in (sa.check_nonconclusive_band_readers,
                      sa.check_channel_totals_use_one_rule,
                      sa.check_restated_thresholds):
            with self.subTest(check=check.__name__):
                self.assertNotEqual(check().status, sa.UNKNOWN)

    def test_the_live_tree_still_has_stored_studies_to_read(self):
        """The positive arm only. The EMPTY arm this used to be named after is
        in `TestEveryGuardedCheckOnAnAbsentSource` below: as first written this
        method asserted `blind is None` on the populated tree and nothing
        else, so `_stored_studies`' guard -- the one six checks share --
        survived its own mutation (measured 2026-08-15, mutant M6)."""
        studies, blind = sa._stored_studies("probe")
        self.assertTrue(studies, "the live tree has stored studies; the "
                                 "positive arm of this control is gone")
        self.assertIsNone(blind)


# Every remaining check the D123 sweep repaired, with the module attribute
# that has to be moved to make its evidence absent, and nothing else. The
# attribute is moved rather than the file deleted: these surfaces are tracked
# and a test that unlinks them would be a test that damages the tree it audits.
#
# WHY THIS TABLE EXISTS. Measured 2026-08-15 against the file as recovered:
# the three ledger checks and the five `_py_sources` checks were killed by
# their mutations, and the other THIRTEEN repaired checks were not covered at
# all -- eight guard sites survived deletion with the suite still green. A
# guard nobody has watched fail is not evidence, so each row below is one
# mutation this file now kills.
_ABSENT_SOURCE_CASES = (
    ("check_withdrawn_numbers", ("WALL", "WEB")),
    ("check_evidence_paths_exist", ("WEB",)),
    ("check_ungated_completed_runs", ("WEB",)),
    ("check_fd_grades_current_standard", ("ACTIVE", "WEB")),
    ("check_statistical_labels", ("MISSION",)),
    ("check_campaign_json_citations", ("CAMPAIGN",)),
    ("check_rung_estimates_state_their_iterations", ("REPO",)),
    # The six that share `_stored_studies`. Moving REPO empties
    # models/curriculum/uq-studies without touching the real one.
    ("check_studies_carry_what_the_fit_records", ("REPO",)),
    ("check_stored_fits_reproduce_their_values", ("REPO",)),
    ("check_declined_ladders_name_their_guard", ("REPO",)),
    ("check_stored_rungs_carry_solved_precision", ("REPO",)),
    ("check_ladder_rungs_share_one_recipe", ("REPO",)),
    ("check_order_window_declines_state_their_dimensionality", ("REPO",)),
)


class TestEveryGuardedCheckOnAnAbsentSource(unittest.TestCase):
    """Both arms, for all thirteen, in one process.

    L-84: the absent arm alone would prove only that the instrument can say
    UNKNOWN. The live arm is what proves it has not been turned into an
    instrument that says UNKNOWN everywhere, which would trade a false green
    for no reading at all.
    """

    @classmethod
    def setUpClass(cls):
        # `_uq_module()` does `sys.path.insert(0, REPO / "sdk")` on every call,
        # so the import must be warmed BEFORE any case moves REPO -- otherwise
        # the six study checks would return WARN "cannot import the fit" and
        # the absent arm would go green for the wrong reason.
        sa._uq_module()

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.empty = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_an_absent_source_is_UNKNOWN_in_every_repaired_check(self):
        for name, attrs in _ABSENT_SOURCE_CASES:
            with self.subTest(check=name):
                saved = {a: getattr(sa, a) for a in attrs}
                for a in attrs:
                    setattr(sa, a, self.empty / f"no-such-{a.lower()}")
                try:
                    result = getattr(sa, name)()
                finally:
                    for a, value in saved.items():
                        setattr(sa, a, value)
                self.assertEqual(result.status, sa.UNKNOWN)
                self.assertNotEqual(result.status, sa.PASS)
                self.assertIn("empty sweep is not agreement",
                              " ".join(result.detail))

    def test_the_live_tree_still_reaches_a_verdict_in_every_one_of_them(self):
        for name, _ in _ABSENT_SOURCE_CASES:
            with self.subTest(check=name):
                self.assertNotEqual(getattr(sa, name)().status, sa.UNKNOWN)


class TestUnknownRedddensTheRunner(unittest.TestCase):
    def test_an_UNKNOWN_with_no_FAIL_exits_3(self):
        def one_unknown():
            return sa.Result("probe", sa.UNKNOWN, "read nothing")

        checks, argv = sa.CHECKS, sys.argv
        try:
            sa.CHECKS = (one_unknown,)
            sys.argv = ["self_audit.py", "--json"]
            with contextlib.redirect_stdout(io.StringIO()):
                code = sa.main()
        finally:
            sa.CHECKS, sys.argv = checks, argv
        self.assertEqual(code, 3)


class TestMutations(_LedgerCells):
    """Each guard is proved by removing it and watching the arm go red."""

    def test_reintroducing_the_empty_set_PASS_turns_the_absent_arm_red(self):
        mutant = _mutant("empty_set_pass",
                         "    if not rows:\n"
                         "        return _no_evidence(\n"
                         '            "ledger stall contamination",',
                         "    if False:\n"
                         "        return _no_evidence(\n"
                         '            "ledger stall contamination",')
        self.absent(mutant)
        result = mutant.check_ledger_stalls()
        self.assertEqual(result.status, mutant.PASS)
        # The mutant reaches the clean branch over zero rows, exactly as the
        # defect did. It now says "no row of 0 ...", because the denominator
        # went into the PASS sentence as a SECOND and independent barrier: a
        # reader meeting this line sees the zero even where the status lies.
        self.assertIn("no row of 0", result.summary)
        # ...and the control arm's assertion is the one that would have caught
        # it, stated here so the mutation is tied to the assertion it proves.
        with self.assertRaises(AssertionError):
            self.assertEqual(result.status, mutant.UNKNOWN)

    def test_the_mutant_still_WARNs_on_a_real_stall(self):
        """The mutation is narrow: it defangs the empty set and nothing else.
        A mutation that broke the check outright would turn the arm red for
        the wrong reason."""
        mutant = _mutant("empty_set_pass",
                         "    if not rows:\n"
                         "        return _no_evidence(\n"
                         '            "ledger stall contamination",',
                         "    if False:\n"
                         "        return _no_evidence(\n"
                         '            "ledger stall contamination",')
        self.write(mutant, _CLEAN + [_STALL])
        self.assertEqual(mutant.check_ledger_stalls().status, mutant.WARN)

    def test_defanging_the_shared_guard_turns_every_arm_red_together(self):
        mutant = _mutant(
            "no_evidence_passes",
            "    return Result(\n        name, UNKNOWN, summary,",
            "    return Result(\n        name, PASS, summary,")
        self.absent(mutant)
        self.assertEqual(mutant.check_ledger_stalls().status, mutant.PASS)
        self.assertEqual(mutant.check_ledger_integrity().status, mutant.PASS)
        mutant._py_sources = lambda: []
        self.assertEqual(
            mutant.check_nonconclusive_band_readers().status, mutant.PASS)

    def test_removing_the_corpus_guard_lets_an_empty_sweep_PASS(self):
        mutant = _mutant(
            "py_corpus_unguarded",
            "    sources = _py_sources()\n"
            "    if sources:\n"
            "        return sources, None\n",
            "    sources = _py_sources()\n"
            "    if True:\n"
            "        return sources, None\n")
        mutant._py_sources = lambda: []
        self.assertEqual(
            mutant.check_nonconclusive_band_readers().status, mutant.PASS)
        self.assertIn("0", mutant.check_nonconclusive_band_readers().summary)


if __name__ == "__main__":
    unittest.main()
