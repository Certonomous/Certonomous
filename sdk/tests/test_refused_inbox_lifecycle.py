"""The refusal ledger describes ONE read, and this file is why (docket D111).

`agenda._REFUSED_INBOX` is a module-level dict keyed by FILENAME. Until
2026-08-15 the module lacked any step that emptied it, so successive
`read_inbox()` calls in one process added to the same ledger and removed only
what a repeat read of the same directory happened to admit. A filename is
meaningless without the directory it came from -- `bad.json` in a test's
temporary agenda root and `bad.json` in the live corpus are one key -- so a test
that pointed `CERTONOMOUS_AGENDA_DIR` at a temporary tree and read four
deliberately malformed fixtures left those four in the ledger for the rest of
the process, including for the live reconcile in
`scripts/calibration_scorecard.py`.

What that produced, measured on 2026-08-15:

    pytest sdk/tests/test_agenda.py sdk/tests/test_calibration_scorecard.py
        -> 2 failed, 76 passed, every time
    the same two files in the reverse order   -> 78 passed, every time
    test_calibration_scorecard.py alone       -> 26 passed

`intake()` compared 131 files on disk against 128 admitted + 7 refused, and the
residual list was EMPTY, because the three extra refusals were ghosts of a
directory that had been deleted. `pytest sdk/tests` collects `test_agenda.py`
first alphabetically, so the full suite was red on this from the day the
reconcile was wired up.

It was diagnosed twice as a concurrent-write artifact -- once in `d2d6bd6c`'s
commit message and once in V15 round 7 §1.2, which set out to contradict the
first and reported that it could not. Both diagnoses ran the failing file BY
ITSELF, which is the passing case. Running a failing test alone and watching it
pass is evidence of pollution; it was read as evidence of flakiness twice.

So the tests here are written the way that mistake was not: every one of them
POLLUTES FIRST and then asserts, and none of them depends on the order pytest
happens to collect anything in. The two that matter most are

  * `test_a_read_of_another_root_does_not_survive_into_this_one`, the direct
    mutation target: revert the fix and it reddens; and
  * `test_the_live_reconcile_balances_after_a_temporary_root_was_read`, which
    reproduces the whole D111 failure inside a single test function rather
    than across two files and a collection order.
"""
from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path

from chief_engineer import agenda

REPO = Path(__file__).resolve().parents[2]
SCORECARD = REPO / "scripts" / "calibration_scorecard.py"

#: A file the reader refuses: no objective at all. Kept deliberately crude, so
#: this file tests the LEDGER's lifetime and not the schema rails, which are
#: `test_agenda.py`'s subject.
_REFUSABLE = {"id": "x-lifecycle", "rationale": "r", "citations": []}


def _write(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


class _TempRootMixin:
    """A temporary agenda root, with the env restored afterwards."""

    def _temp_root(self) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return Path(tmp.name)

    def _point_at(self, root: Path) -> None:
        previous = os.environ.get("CERTONOMOUS_AGENDA_DIR")
        os.environ["CERTONOMOUS_AGENDA_DIR"] = str(root)

        def restore() -> None:
            if previous is None:
                os.environ.pop("CERTONOMOUS_AGENDA_DIR", None)
            else:
                os.environ["CERTONOMOUS_AGENDA_DIR"] = previous
        self.addCleanup(restore)

    def _refused_files(self) -> set[str]:
        return {entry["file"] for entry in agenda.refused_inbox()}


class TheLedgerDescribesTheLastRead(_TempRootMixin, unittest.TestCase):

    def test_a_read_of_another_root_does_not_survive_into_this_one(self):
        """D111 in one function. THE MUTATION TARGET: take the clear back out
        of `read_inbox()` and this reddens on the first assertion."""
        first = self._temp_root()
        _write(first / "proposals" / "from-the-first-root.json", _REFUSABLE)
        self._point_at(first)
        agenda.read_inbox()
        self.assertIn("from-the-first-root.json", self._refused_files())

        second = self._temp_root()
        _write(second / "proposals" / "from-the-second-root.json", _REFUSABLE)
        self._point_at(second)
        agenda.read_inbox()
        self.assertNotIn("from-the-first-root.json", self._refused_files(),
                         "a refusal from a directory this read did not touch "
                         "is still in the ledger: D111 is back")
        self.assertIn("from-the-second-root.json", self._refused_files())

    def test_a_fixture_that_stops_being_refused_leaves_the_ledger(self):
        """The fixture-change case. The ledger used to be add-only, so a file
        deleted between two reads stayed refused for the life of the process
        and the reconcile counted a file that was not on the disk."""
        root = self._temp_root()
        inbox = root / "proposals"
        _write(inbox / "goes-away.json", _REFUSABLE)
        self._point_at(root)
        agenda.read_inbox()
        self.assertEqual({"goes-away.json"}, self._refused_files())

        (inbox / "goes-away.json").unlink()
        agenda.read_inbox()
        self.assertEqual(set(), self._refused_files(),
                         "the ledger still names a file that is not on disk")

    def test_a_refused_file_that_is_repaired_leaves_the_ledger(self):
        """The same shape without a deletion: the file stays, its defect does
        not. The old `pop()` covered this one case and only this one."""
        root = self._temp_root()
        inbox = root / "proposals"
        _write(inbox / "repaired.json", _REFUSABLE)
        self._point_at(root)
        agenda.read_inbox()
        self.assertIn("repaired.json", self._refused_files())

        _write(inbox / "repaired.json", {
            "id": "x-lifecycle", "objective": "Sweep the approach angle",
            "rationale": "r", "citations": ["c"], "est_core_min": 4,
            "expected_knowledge_gain": "g", "cost_basis": "estimate",
            "source_kind": "reading", "hard_criterion": "no-case"})
        admitted = {p["objective"] for p in agenda.read_inbox()}
        self.assertIn("Sweep the approach angle", admitted)
        self.assertEqual(set(), self._refused_files())

    def test_a_root_that_does_not_exist_empties_the_ledger(self):
        """The early return had no ledger write at all, so a read of a missing
        directory left the previous directory's refusals standing."""
        root = self._temp_root()
        _write(root / "proposals" / "present.json", _REFUSABLE)
        self._point_at(root)
        agenda.read_inbox()
        self.assertIn("present.json", self._refused_files())

        self._point_at(self._temp_root() / "no-agenda-here")
        self.assertEqual([], agenda.read_inbox())
        self.assertEqual(set(), self._refused_files())

    def test_the_ledger_names_the_directory_it_was_read_from(self):
        """Asking the ledger about a directory it has not read gets an empty
        answer, and `refused_inbox_root()` says which directory it did read --
        so the empty answer is inspectable rather than a filter nobody can
        see. Without the root the ledger is a filename keyed to nothing."""
        first = self._temp_root()
        _write(first / "proposals" / "only-here.json", _REFUSABLE)
        self._point_at(first)
        agenda.read_inbox()
        self.assertEqual(str(first.resolve() / "proposals"),
                         agenda.refused_inbox_root())

        self._point_at(self._temp_root())
        self.assertEqual([], agenda.refused_inbox(),
                         "the ledger answered for a directory it never read")
        self.assertEqual(str(first.resolve() / "proposals"),
                         agenda.refused_inbox_root(),
                         "and it still says which directory it did read")


class TheLiveReconcileIsNotPolluted(_TempRootMixin, unittest.TestCase):
    """The end-to-end guard: the two `test_calibration_scorecard.py` failures,
    reproduced inside one test function instead of across a collection order.

    `test_calibration_scorecard.py` asserts the same invariant, but only ever
    against a clean process. This one dirties the process first, on purpose,
    which is the experiment neither earlier diagnosis ran.
    """

    def _scorecard(self):
        spec = importlib.util.spec_from_file_location(
            "_calscore_lifecycle", SCORECARD)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def _pollute(self) -> None:
        """Do to the ledger what `test_agenda.py` does to it: read a temporary
        agenda root full of files that are refused by design, then put the
        environment back exactly as it was."""
        root = self._temp_root()
        for name in ("bad.json", "closed.json", "dupe.json",
                     "without-replay.json"):
            _write(root / "proposals" / name, _REFUSABLE)
        previous = os.environ.get("CERTONOMOUS_AGENDA_DIR")
        os.environ["CERTONOMOUS_AGENDA_DIR"] = str(root)
        try:
            agenda.read_inbox()
        finally:
            if previous is None:
                os.environ.pop("CERTONOMOUS_AGENDA_DIR", None)
            else:
                os.environ["CERTONOMOUS_AGENDA_DIR"] = previous

    def test_the_pollution_step_really_does_fill_the_ledger(self):
        """The positive control. Without it the two tests below could pass
        because the ledger was empty the whole time (L-84).

        It reads the private dict on purpose: the point is that the polluting
        read really did leave four entries in the module -- the state that used
        to leak -- and that the accessor declines to hand them to a caller
        asking about a directory those four were not read from.
        """
        self._pollute()
        self.assertEqual(4, len(agenda._REFUSED_INBOX),
                         "the polluting read refused nothing, so the tests "
                         "under it are proving nothing")
        self.assertEqual([], agenda.refused_inbox(),
                         "refusals read from a temporary agenda root were "
                         "handed to a caller asking about the live one")

    def test_the_live_reconcile_balances_after_a_temporary_root_was_read(self):
        self._pollute()
        scorecard = self._scorecard()
        intake = scorecard.collect()["intake"]
        self.assertTrue(intake.get("available"), intake.get("error"))
        self.assertTrue(
            intake["reconciles"],
            f"{intake['files_on_disk']} on disk != {intake['admitted']} "
            f"admitted + {intake['refused_count']} refused; residual "
            f"{intake['residual_files']} -- a refusal from a directory that "
            f"is not the one being reconciled is being counted (D111)")

    def test_no_refusal_names_a_file_that_is_not_on_the_disk_read(self):
        """The invariant behind the arithmetic, asserted directly: a refusal
        is a statement about a file in the directory that was read."""
        self._pollute()
        agenda.read_inbox()
        on_disk = {p.name for p in agenda.inbox_dir().glob("*.json")}
        named = {entry["file"] for entry in agenda.refused_inbox()}
        self.assertEqual(set(), named - on_disk,
                         "the refusal ledger names files that are not in the "
                         "directory it last read")


if __name__ == "__main__":
    unittest.main()
