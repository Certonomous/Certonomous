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


def _run_main(*checks, argv=("self_audit.py", "--json")):
    """`main()` over a substituted CHECKS tuple. Returns (exit code, stdout).

    THE SHIPPED ENTRY POINT, not a recomputation of its condition beside it.
    `sys.exit(main())` is what `scripts/lab_check.py` runs and what a pre-push
    hook would read, so the code under test is the integer `main` returns and
    nothing else. A cell that rebuilt `any(r.status == FAIL ...)` in the test
    would pass with the arm deleted from the script.

    `_RESULTS_THIS_RUN` is restored as well as `CHECKS`: `main` writes every
    outcome into it by check name, and a probe left behind there is a fixture
    leaking into `check_every_value_claim_names_its_source` in a later test.
    """
    saved = sa.CHECKS, sys.argv, dict(sa._RESULTS_THIS_RUN)
    try:
        sa.CHECKS = tuple(checks)
        sys.argv = list(argv)
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = sa.main()
    finally:
        sa.CHECKS, sys.argv = saved[0], saved[1]
        sa._RESULTS_THIS_RUN.clear()
        sa._RESULTS_THIS_RUN.update(saved[2])
    return code, out.getvalue()


def _probe(status, summary="probe"):
    def check():
        return sa.Result("probe", status, summary)
    check.__name__ = f"probe_{status.lower()}"
    return check


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


class TestTheThreeValuedExitMap(unittest.TestCase):
    """All three arms of `main`'s exit map, driven through `main` (D211/D212).

    WHY THIS EXISTS. The sibling above pinned the UNKNOWN arm only. The FAIL
    arm -- `if any(r.status == FAIL for r in results): return 1` -- had NO
    covering test at all, and the FAIL arm is the one that matters most: exit 1
    is what `scripts/lab_check.py`'s `EXIT_CONTRACT` reads as FAIL, so it is
    the code that reddens the runner and would block a push. A pre-push hook
    whose blocking condition rests on an untested exit path is worth very
    little.

    HOW THE HOLE STAYED OPEN FOR SO LONG, which is the transferable part: the
    guard was mutated and the harness reported it KILLED. The harness judged by
    `returncode != 0` while its control was ALREADY RED, so mutant and control
    were both red and every mutation in that cell reported KILLED, survivors
    included. Re-run against a green control and judged by the CHANGE IN
    FAILURE COUNT it is 0 -> 0 failures: a SURVIVOR. An uncovered guard had
    been converted into a clean bill of health -- a verdict from a population
    that was never measured, which is the empty-set shape this file is named
    for, arriving through the instrument instead of through the check.

    Three mutations, re-measured 2026-08-15 with a green control in an isolated
    worktree, each named beside the case that now kills it:
      SAM1  `if any(FAIL): return 1` -> never taken   was SURVIVED, now killed
      SAM2  `return 3 if any(UNKNOWN) else 0` -> `return 0`   was already
            killed, by the sibling above; kept measured here as the control
            that this class did not simply make everything red
      SAM3  a check that RAISES recorded PASS instead of FAIL   was SURVIVED,
            now killed -- and it is the worse of the two, because a check that
            crashes then reports as a passing check rather than a finding

    Both halves, per L-84: the arms that must return non-zero AND the arm that
    must still return 0, so this class cannot be satisfied by an exit map that
    reddens unconditionally.
    """

    def test_a_FAIL_exits_1(self):
        code, _ = _run_main(_probe(sa.FAIL, "a definite finding"))
        self.assertEqual(code, 1,
                         "exit 1 is what lab_check's EXIT_CONTRACT reads as "
                         "FAIL; without it a FAIL exits 0 beside the passes")

    def test_a_FAIL_beside_PASSes_still_exits_1(self):
        code, _ = _run_main(_probe(sa.PASS), _probe(sa.FAIL), _probe(sa.INFO))
        self.assertEqual(code, 1)

    def test_a_FAIL_OUTRANKS_an_UNKNOWN(self):
        """A definite finding outranks an indefinite one. Order-independent."""
        for order in ((sa.FAIL, sa.UNKNOWN), (sa.UNKNOWN, sa.FAIL)):
            with self.subTest(order=order):
                code, _ = _run_main(*(_probe(s) for s in order))
                self.assertEqual(code, 1)

    def test_an_UNKNOWN_with_no_FAIL_exits_3_through_the_same_entry_point(self):
        code, _ = _run_main(_probe(sa.PASS), _probe(sa.UNKNOWN))
        self.assertEqual(code, 3)

    def test_the_MUST_NOT_FIRE_half_a_clean_run_still_exits_0(self):
        """L-84. Without this, an exit map that returned 1 always would pass."""
        code, _ = _run_main(_probe(sa.PASS), _probe(sa.WARN), _probe(sa.INFO))
        self.assertEqual(code, 0)

    def test_a_WARN_alone_does_not_block_the_push(self):
        code, _ = _run_main(_probe(sa.WARN, "priced, not blocking"))
        self.assertEqual(code, 0)

    def test_a_check_that_RAISES_is_recorded_FAIL_and_exits_1(self):
        """SAM3. A crashed check is a finding, not a pass.

        The exception arm and the exit map are one mechanism: recording the
        crash as PASS makes `self_audit` exit 0 on a check that never ran, so
        the arm is asserted here on BOTH surfaces -- the status carried on the
        JSON and the code `main` returns.
        """
        def exploding_check():
            raise RuntimeError("the check itself is broken")

        code, out = _run_main(exploding_check)
        self.assertEqual(code, 1,
                         "a check that raised did not redden the runner")
        row = json.loads(out)[0]
        self.assertEqual(row["status"], sa.FAIL)
        self.assertIn("check raised RuntimeError", row["summary"])
        self.assertIn("the check itself is broken", row["summary"])

    def test_a_check_that_raises_does_not_stop_the_run(self):
        """Both halves again: the crash is recorded AND its siblings still run."""
        def exploding_check():
            raise ValueError("boom")

        code, out = _run_main(exploding_check, _probe(sa.PASS))
        rows = json.loads(out)
        self.assertEqual(len(rows), 2, "a raising check swallowed the rest")
        self.assertEqual(code, 1)


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
        """THE ANCHOR WAS NARROWED, and which change moved it.

        `return Result(\\n        name, UNKNOWN, summary,` matched exactly one
        site until D175 added `_no_selection` beside `_no_evidence` -- a second
        shared guard, for the case where the source is present and the
        SELECTOR matches nothing, which is a different failure with a different
        remedy. Two identical sites tripped this helper's own uniqueness check,
        which is the check working: the code moved and the mutation was fixed
        rather than the test deleted. The anchor now carries the line that
        distinguishes the two guards, and the second guard is mutated below in
        its own cell so BOTH remain proved.
        """
        mutant = _mutant(
            "no_evidence_passes",
            "    return Result(\n        name, UNKNOWN, summary,\n"
            "        (detail or [])\n"
            '        + [f"not read: {s}" for s in named]',
            "    return Result(\n        name, PASS, summary,\n"
            "        (detail or [])\n"
            '        + [f"not read: {s}" for s in named]')
        self.absent(mutant)
        self.assertEqual(mutant.check_ledger_stalls().status, mutant.PASS)
        self.assertEqual(mutant.check_ledger_integrity().status, mutant.PASS)
        mutant._py_sources = lambda: []
        self.assertEqual(
            mutant.check_nonconclusive_band_readers().status, mutant.PASS)

    def test_defanging_the_SECOND_shared_guard_turns_its_arms_red_too(self):
        """`_no_selection` is load-bearing in its own right (D175).

        It is the guard for a source that is PRESENT, readable and non-empty
        whose selector matches nothing -- eighteen checks returned PASS that
        way. Mutate it to PASS and the arm goes green over a real corpus that
        simply did not select, which is the defect it was written for.
        """
        mutant = _mutant(
            "no_selection_passes",
            "    return Result(\n        name, UNKNOWN, summary,\n"
            "        (detail or [])\n"
            '        + [f"read, and not empty: {s}" for s in named]',
            "    return Result(\n        name, PASS, summary,\n"
            "        (detail or [])\n"
            '        + [f"read, and not empty: {s}" for s in named]')
        # A REAL, NON-EMPTY corpus that selects nothing: not an empty one.
        plain = Path(mutant.REPO) / "plain.py"
        plain.parent.mkdir(parents=True, exist_ok=True)
        plain.write_text("def hello():\n    return 'selects under no rule'\n")
        mutant._py_corpus = lambda name: ([plain], None)
        self.assertEqual(
            mutant.check_nonconclusive_band_readers().status, mutant.PASS)

    def test_removing_the_corpus_guard_now_MISDIAGNOSES_instead_of_passing(
            self):
        """RENAMED AND RE-AIMED, and here is exactly what moved it.

        This asserted that removing `_py_corpus`'s guard lets an empty sweep
        return PASS, and it did, because that guard was the only thing between
        an absent corpus and a green. D175 added a SECOND, independent guard
        downstream -- `if not checked: _no_selection(...)` -- so the mutant can
        no longer produce a green at all. Defence in depth is the substance of
        the repair, and it is asserted first below.

        THE ASSERTION IS NOT RELAXED TO ACCEPT EITHER STATUS, which would test
        nothing. It is re-aimed at what the corpus guard still uniquely
        prevents: a MISDIAGNOSIS. With the guard removed, an ABSENT corpus is
        reported as "my selector matched nothing" -- which sends the reader to
        re-read a regex when the actual problem is that every root is gone.
        The two failures have different remedies, which is the whole reason
        `_no_selection` exists as a separate helper, and this mutation proves
        the first guard is what keeps them apart.
        """
        mutant = _mutant(
            "py_corpus_unguarded",
            "    sources = _py_sources()\n"
            "    if sources:\n"
            "        return sources, None\n",
            "    sources = _py_sources()\n"
            "    if True:\n"
            "        return sources, None\n")
        mutant._py_sources = lambda: []
        mutated = mutant.check_nonconclusive_band_readers()
        # Still not a green: the downstream guard holds the line.
        self.assertEqual(mutant.UNKNOWN, mutated.status, mutated.summary)
        # But the reason is now the WRONG one, and that is the finding.
        joined = " ".join(mutated.detail)
        self.assertIn("selector that matched nothing", joined)
        self.assertNotIn("no Python source was found to scan", mutated.summary)

        # The unmutated module, on the same absent corpus, says the true thing.
        clean = _mutant("py_corpus_intact", "def _py_corpus", "def _py_corpus")
        clean._py_sources = lambda: []
        honest = clean.check_nonconclusive_band_readers()
        self.assertEqual(clean.UNKNOWN, honest.status)
        self.assertIn("no Python source was found to scan", honest.summary)
        self.assertNotIn("selector that matched nothing",
                         " ".join(honest.detail))


if __name__ == "__main__":
    unittest.main()
