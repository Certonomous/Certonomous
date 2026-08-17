"""The authority ruling made mechanical, with both controls. (D219, D222.)

WHAT IS BEING ENFORCED, AND WHY A RULE WITH A SWEEP WAS NOT ENOUGH
==================================================================
D219 ruled: `docket.json` is authoritative for `status` on any id it holds, and
a proposal file's `status` is intake-only -- load-bearing before its first merge,
non-authoritative after it. It also reconciled all 34 live disagreements by hand
and shipped a sweep that measures them. What it could not claim, and said so, is
that anything ENFORCED the ruling: `refresh_docket` still skipped a merged id
forever, so an agent hand-editing an inbox status the next day re-opened the
divergence at exactly the same rate. A rate-unchanged defect detected sooner is
still a rate-unchanged defect.

Three changes carry the ruling into `chief_engineer.agenda`, and this file is
their specification. Every expectation below is derived from the RULING and from
the clauses of `agenda` the ruling was read out of -- never from reading the
current text of `agenda.py`.

    E1  AN OUT-OF-VOCABULARY STATUS IS REFUSED, NOT COERCED. `read_inbox` used
        to write `status if status in STATUSES else "proposed"`. Two live files
        carried `queued`, so they read `proposed` through the module and
        `queued` to any agent who opened the raw file -- which is what an agent
        does before starting a run. `queued` is SETTLED as REFUSED rather than
        admitted: `approved-queued` is already in the vocabulary and means the
        thing, `set_status` raises on anything outside it so no such value can
        ever become a decision, and a sixth near-synonym would need its own
        answer in `OPEN_STATUSES` and in `docket_view`'s open count.

    E2  THE MERGE IS TWO-WAY FOR EVIDENCE AND ONE-WAY FOR AUTHORITY. Where a
        file carries an `outcome` or a `measured_core_min` the docket lacks,
        the file holds a record the docket LOST, and `refresh_docket` moves it
        IN. Additive only: a field the docket already carries is never touched,
        and `status` is not in the carried set at all, so the ruling is enforced
        by construction rather than by a conditional somebody can edit.

    E3  `measured_core_min` SURVIVES INTAKE. It was dropped by `read_inbox`
        while 37 docket records carried it, so a file recording what work
        actually cost lost that number on ingest and E2 would have had nothing
        to carry.

BOTH CONTROLS (L-84)
====================
    FIRES      a `queued` file is refused and named; a docket record missing an
               outcome its file holds gains it, ON DISK
    DOES NOT   every legal status still rides through untouched; a docket
    FIRE       record that already has an outcome keeps its own; a file's
               `status` NEVER moves onto the docket, not even when the file is
               `done` and the docket is `proposed` -- which is the single
               assertion that separates this enforcement from the auto-promotion
               it was explicitly rejected in favour of

MUTATION DISCIPLINE
===================
`sdk/chief_engineer/` is COPIED into a temporary tree and the copy is mutated.
The tracked module is never edited: on 2026-08-15 a harness held a tracked file
mutated in place for ten minutes and a concurrent commit captured the mutant
into HEAD, with `git status` clean throughout. Judged by failure-count delta
against a control asserted green, never by a returncode.
"""

from __future__ import annotations

import importlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "sdk"))
from chief_engineer import agenda  # noqa: E402

# The one module that names this repository's tree (MOVE_MAP batch 3).
# Every name it exports is bound to a legacy/successor PAIR resolved
# against the filesystem at import, so the constants below are correct
# before the move, between batches and after it, with no edit here.
import sys as _sys  # noqa: E402
import pathlib as _pathlib  # noqa: E402
_LAB_PATHS_DIR = str(_pathlib.Path(__file__).resolve().parents[2]
                     / "scripts")
if _LAB_PATHS_DIR not in _sys.path:
    _sys.path.insert(0, _LAB_PATHS_DIR)
import lab_paths  # noqa: E402

_PACKAGE = REPO / "sdk" / "chief_engineer"
_SOURCE = _PACKAGE / "agenda.py"


def _mutant(name: str, old: str, new: str):
    """`chief_engineer.agenda` with one substitution, from a COPY of the whole
    package in a temp tree. Never the tracked file."""
    text = _SOURCE.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise AssertionError(
            f"mutation {name!r} does not identify one site: "
            f"{text.count(old)} occurrence(s). The code moved; fix the "
            f"mutation rather than deleting this test.")
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name) / "sdk"
    shutil.copytree(_PACKAGE, root / "chief_engineer",
                    ignore=shutil.ignore_patterns("__pycache__"))
    (root / "chief_engineer" / "agenda.py").write_text(
        text.replace(old, new), encoding="utf-8")
    saved_path, saved_modules = list(sys.path), dict(sys.modules)
    for key in list(sys.modules):
        if key == "chief_engineer" or key.startswith("chief_engineer."):
            del sys.modules[key]
    sys.path.insert(0, str(root))
    try:
        module = importlib.import_module("chief_engineer.agenda")
    finally:
        sys.path[:] = saved_path
        for key in list(sys.modules):
            if key == "chief_engineer" or key.startswith("chief_engineer."):
                del sys.modules[key]
        sys.modules.update(saved_modules)
    module.__keepalive = tmp          # noqa: SLF001 - hold the tempdir open
    return module


# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------

_FILED_BEFORE_THE_SCHEMA_BOUND = "2026-08-01T00:00:00+00:00"


def _file(item_id, status, **extra):
    """An inbox file old enough that the grandfathered schema rails do not
    bind, so each cell tests the one rail it names and nothing else."""
    out = {"id": item_id, "objective": f"objective for {item_id}",
           "rationale": "because the record says so", "citations": [],
           "est_core_min": 10, "cost_basis": "estimate",
           "expected_knowledge_gain": "a number where there is none",
           "source_kind": "inbox", "status": status,
           "created_at": _FILED_BEFORE_THE_SCHEMA_BOUND}
    out.update(extra)
    return out


class _Tree(unittest.TestCase):
    """A private agenda directory per test. Nothing here can reach the live
    tree: `CERTONOMOUS_AGENDA_DIR` is redirected and restored."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.agenda_dir = Path(self.tmp.name) / "agenda"
        (self.agenda_dir / "proposals").mkdir(parents=True)
        self._saved = os.environ.get("CERTONOMOUS_AGENDA_DIR")
        os.environ["CERTONOMOUS_AGENDA_DIR"] = str(self.agenda_dir)
        # The drafters read four other roots; point them all at empty
        # directories so a cell measures the inbox and nothing else.
        self._saved_roots = {
            key: os.environ.get(key) for key in
            ("CERTONOMOUS_REPORT_ROOTS", "CERTONOMOUS_TMR_CARD",
             "CERTONOMOUS_UQ_STUDIES", "CERTONOMOUS_CREDENTIALS",
             "CERTONOMOUS_LEDGER_STUDY")}
        for key in self._saved_roots:
            os.environ[key] = str(Path(self.tmp.name) / f"empty-{key}")
        self.addCleanup(self._restore)

    def _restore(self):
        if self._saved is None:
            os.environ.pop("CERTONOMOUS_AGENDA_DIR", None)
        else:
            os.environ["CERTONOMOUS_AGENDA_DIR"] = self._saved
        for key, value in self._saved_roots.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.tmp.cleanup()

    def put_file(self, item_id, status, **extra):
        path = self.agenda_dir / "proposals" / f"{item_id}.json"
        path.write_text(json.dumps(_file(item_id, status, **extra)),
                        encoding="utf-8")
        return path

    def put_docket(self, *records):
        (self.agenda_dir / "docket.json").write_text(
            json.dumps({"generated_at": _FILED_BEFORE_THE_SCHEMA_BOUND,
                        "proposals": list(records)}), encoding="utf-8")

    def docket_on_disk(self):
        """Read the file, NOT the return value. `refresh_docket` mutates the
        same dict objects `load_docket` handed it, so a carry that never
        reached disk would still be visible in what it returns."""
        data = json.loads(
            (self.agenda_dir / "docket.json").read_text(encoding="utf-8"))
        return {r["id"]: r for r in data["proposals"]}


# --------------------------------------------------------------------------
# E1 -- the vocabulary, and the settlement of `queued`
# --------------------------------------------------------------------------

class TestAnIllegalStatusIsRefusedNotCoerced(_Tree):

    def test_queued_is_refused_and_named(self):
        """The settlement. Silent coercion is the defect; refusal is loud, and
        `refused_inbox()` is where the control room can read it."""
        self.put_file("has-queued", "queued")
        accepted = agenda.read_inbox()
        self.assertEqual([i["id"] for i in accepted], [])
        refused = agenda.refused_inbox()
        self.assertEqual([r["id"] for r in refused], ["has-queued"])
        violations = " ".join(refused[0]["violations"])
        self.assertIn("status", violations)
        self.assertIn("queued", violations)

    def test_the_refusal_points_at_the_status_the_author_meant(self):
        """A near-miss named is a repair; a near-miss unnamed is a guess.
        `queued` is one hyphenated word from `approved-queued`."""
        self.assertIn("approved-queued",
                      " ".join(agenda.status_violations(
                          {"status": "queued"})))

    def test_queued_is_settled_as_refused_rather_than_admitted(self):
        """The other half of the settlement, asserted so a later widening of
        the vocabulary has to come past this cell. `approved-queued` already
        carries the meaning and is already graded by `OPEN_STATUSES`."""
        self.assertNotIn("queued", agenda.STATUSES)
        self.assertIn("approved-queued", agenda.STATUSES)
        self.assertIn("approved-queued", agenda.OPEN_STATUSES)

    def test_no_illegal_status_can_ever_become_a_decision_anyway(self):
        """Why refusal is the narrow, correct choice rather than a harsh one:
        the value was already unactionable. Coercion added only the pretence
        that it was actionable as something else."""
        self.put_docket({"id": "x", "objective": "o", "rationale": "r",
                         "est_core_min": 1, "cost_basis": "estimate",
                         "expected_knowledge_gain": "g",
                         "status": "proposed"})
        with self.assertRaises(ValueError):
            agenda.set_status("x", "queued")

    def test_every_legal_status_still_rides_through(self):
        """THE NEGATIVE CONTROL. A rail that refused a legal value would empty
        the inbox, and an empty inbox reads as a clean one."""
        for status in agenda.STATUSES:
            with self.subTest(status=status):
                self.assertEqual(
                    agenda.status_violations({"status": status}), [])

    def test_the_whole_live_inbox_still_passes_this_rail(self):
        """Reach on the real tree (L-84): zero of the live files are refused
        by the NEW rail, so nothing standing was broken by adding it. Measured
        against the live directory, not a fixture."""
        os.environ["CERTONOMOUS_AGENDA_DIR"] = str(lab_paths.AGENDA)
        try:
            accepted = agenda.read_inbox()
            refused = agenda.refused_inbox()
        finally:
            os.environ["CERTONOMOUS_AGENDA_DIR"] = str(self.agenda_dir)
        self.assertGreater(len(accepted), 0, "the live inbox read as empty")
        by_status = [r for r in refused
                     if any(v.startswith("status:") for v in r["violations"])]
        self.assertEqual(by_status, [],
                         "the new rail refuses a file that stands today")

    def test_an_absent_status_is_the_documented_default_not_a_violation(self):
        """`read_inbox` defaults an absent status to `proposed`; the rail must
        agree with that default or every file without the field is refused."""
        self.assertEqual(agenda.status_violations({}), [])
        self.assertEqual(agenda.status_violations({"status": ""}), [])


# --------------------------------------------------------------------------
# E2/E3 -- evidence carried in, authority never carried out
# --------------------------------------------------------------------------

class TestTheMergeIsTwoWayForEvidenceOnly(_Tree):

    def test_an_outcome_the_docket_lacks_is_carried_in_and_persisted(self):
        """Asserted against the FILE ON DISK, deliberately. `_carry_evidence`
        mutates the very dicts `load_docket` returned, so `result != existing`
        compares them against themselves and reads EQUAL; without the extra
        save clause the carry would happen in memory, be reported, and never
        reach the file."""
        self.put_file("item", "done", outcome="measured 0.056647, MATERIAL")
        self.put_docket({"id": "item", "objective": "objective for item",
                         "rationale": "r", "est_core_min": 10,
                         "cost_basis": "estimate",
                         "expected_knowledge_gain": "g", "status": "proposed",
                         "source_kind": "inbox"})
        agenda.refresh_docket()
        on_disk = self.docket_on_disk()
        self.assertEqual(on_disk["item"]["outcome"], "measured 0.056647, "
                                                     "MATERIAL")

    def test_the_files_status_never_moves_onto_the_docket(self):
        """THE SINGLE ASSERTION THAT SEPARATES THIS FROM AUTO-PROMOTION. The
        file says `done`; the docket said `proposed` and must still say it.
        D219's three file-ahead closures each had to be checked against a named
        pre-registration commit before they could be believed, and a merge that
        closed an item on the filer's say-so would defeat `set_status`'s own
        precondition. Carrying the outcome forward is what MAKES a later close
        possible; it is not the close."""
        self.put_file("item", "done", outcome="it found a number")
        self.put_docket({"id": "item", "objective": "objective for item",
                         "rationale": "r", "est_core_min": 10,
                         "cost_basis": "estimate",
                         "expected_knowledge_gain": "g", "status": "proposed",
                         "source_kind": "inbox"})
        agenda.refresh_docket()
        self.assertEqual(self.docket_on_disk()["item"]["status"], "proposed")
        self.assertNotIn("status", agenda._EVIDENCE_FIELDS)

    def test_measured_core_min_survives_intake_and_is_carried(self):
        """E3. It was dropped by `read_inbox`, so E2 would have had nothing to
        carry however right the merge was."""
        self.put_file("item", "proposed", measured_core_min=335.98)
        self.assertEqual(
            agenda.read_inbox()[0]["measured_core_min"], 335.98)
        self.put_docket({"id": "item", "objective": "objective for item",
                         "rationale": "r", "est_core_min": 600,
                         "cost_basis": "estimate",
                         "expected_knowledge_gain": "g", "status": "done",
                         "outcome": "already recorded", "source_kind": "inbox"})
        agenda.refresh_docket()
        self.assertEqual(
            self.docket_on_disk()["item"]["measured_core_min"], 335.98)

    def test_a_field_the_docket_already_holds_is_never_overwritten(self):
        """THE NEGATIVE CONTROL, and the whole safety argument: additive only.
        This merge can give the docket something it does not have; it can never
        take something away, so it cannot destroy a decision or a record."""
        self.put_file("item", "done", outcome="THE FILE'S VERSION")
        self.put_docket({"id": "item", "objective": "objective for item",
                         "rationale": "r", "est_core_min": 10,
                         "cost_basis": "estimate",
                         "expected_knowledge_gain": "g", "status": "done",
                         "outcome": "THE DOCKET'S VERSION",
                         "source_kind": "inbox"})
        agenda.refresh_docket()
        self.assertEqual(self.docket_on_disk()["item"]["outcome"],
                         "THE DOCKET'S VERSION")

    def test_nothing_is_carried_when_there_is_nothing_to_carry(self):
        """The second negative control: the quiet state this rail exists to
        keep the tree in. A carry ledger that is never empty is a ledger
        nobody reads."""
        self.put_file("item", "proposed")
        self.put_docket({"id": "item", "objective": "objective for item",
                         "rationale": "r", "est_core_min": 10,
                         "cost_basis": "estimate",
                         "expected_knowledge_gain": "g", "status": "approved",
                         "source_kind": "inbox"})
        agenda.refresh_docket()
        self.assertEqual(agenda.carried_evidence(), [])
        self.assertEqual(self.docket_on_disk()["item"]["status"], "approved")

    def test_the_carry_is_published_rather_than_silent(self):
        """A merge nobody can see is a merge nobody can question -- the same
        reason `refused_inbox` and `unscored_kinds` exist."""
        self.put_file("item", "done", outcome="a sentence with 0.42 in it")
        self.put_docket({"id": "item", "objective": "objective for item",
                         "rationale": "r", "est_core_min": 10,
                         "cost_basis": "estimate",
                         "expected_knowledge_gain": "g", "status": "proposed",
                         "source_kind": "inbox"})
        agenda.refresh_docket()
        carried = agenda.carried_evidence()
        self.assertEqual([(c["id"], c["field"]) for c in carried],
                         [("item", "outcome")])

    def test_a_docket_record_with_no_file_is_untouched(self):
        """The third negative control. 189 live records are in this class and
        a merge that reached them would be rewriting the drafters' output."""
        self.put_docket({"id": "drafted", "objective": "no file exists",
                         "rationale": "r", "est_core_min": 10,
                         "cost_basis": "estimate",
                         "expected_knowledge_gain": "g", "status": "done",
                         "source_kind": "report"})
        before = self.docket_on_disk()["drafted"]
        agenda.refresh_docket()
        self.assertEqual(self.docket_on_disk()["drafted"], before)


class TestTheRulingIsEnforcedByConstruction(unittest.TestCase):
    """The ruling's four legs, asserted where they can redden. If any of these
    stops being true, the ruling stops being derivable from code and becomes a
    preference, which is what D38 item (5) was stuck on for weeks."""

    def test_set_status_is_the_only_decision_recorder_and_writes_the_docket(self):
        import inspect
        source = inspect.getsource(agenda.set_status)
        self.assertIn("save_docket", source)
        self.assertNotIn("inbox", source)

    def test_no_code_path_writes_a_proposal_files_status(self):
        """Leg 2 of the ruling, made falsifiable: every status ever changed in
        the inbox was changed by hand, and if that stops being true this cell
        is where it shows."""
        text = _SOURCE.read_text(encoding="utf-8")
        self.assertNotIn("write_text", text.split("def read_inbox")[1]
                         .split("def draft_all")[0])

    def test_status_is_not_in_the_carried_set(self):
        """Leg 3, and the enforcement itself. The authority ruling holds
        because `status` is absent from a tuple, not because a conditional
        somewhere remembers to skip it."""
        self.assertEqual(tuple(agenda._EVIDENCE_FIELDS),
                         ("outcome", "measured_core_min"))

    def test_docket_view_serves_the_docket(self):
        """Leg 4: what the control room reads is the docket. The inbox is
        served nowhere, so an inbox-only decision reaches no consumer."""
        import inspect
        self.assertIn("refresh_docket", inspect.getsource(agenda.docket_view))


class TestMutations(_Tree):
    """Each enforcement proved by removing it and watching a named cell die.
    The package is COPIED and the copy mutated; the tracked module is never
    edited."""

    def _with(self, module, body):
        """Run `body(module)` against this test's private agenda directory."""
        return body(module)

    def test_M1_restoring_the_coercion_makes_queued_invisible_again(self):
        """The exact defect D219 measured: the file says `queued`, the module
        says `proposed`, and only an agent opening the raw file can tell."""
        mutant = _mutant("coercion_restored",
                         '            "status": status,\n',
                         '            "status": status if status in STATUSES '
                         'else "proposed",\n')
        self.put_file("has-queued", "queued")
        items = mutant.read_inbox()
        self.assertEqual([i["status"] for i in items], ["proposed"],
                         "the mutation did not reintroduce the defect")
        self.assertEqual(mutant.refused_inbox(), [])
        # the control holds the line on the same file
        self.assertEqual(agenda.read_inbox(), [])
        self.assertEqual([r["id"] for r in agenda.refused_inbox()],
                         ["has-queued"])

    def test_M2_restoring_the_unconditional_skip_loses_the_evidence(self):
        """The drift mechanism itself, put back. A file is never re-read after
        first merge, so the outcome it holds never reaches the docket."""
        mutant = _mutant(
            "skip_restored",
            "                carried.extend(_carry_evidence(by_id[proposal[\"id\"]],\n"
            "                                               proposal))\n",
            "")
        self.put_file("item", "done", outcome="a sentence with 0.42 in it")
        record = {"id": "item", "objective": "objective for item",
                  "rationale": "r", "est_core_min": 10,
                  "cost_basis": "estimate", "expected_knowledge_gain": "g",
                  "status": "proposed", "source_kind": "inbox"}
        self.put_docket(record)
        mutant.refresh_docket()
        self.assertNotIn("outcome", self.docket_on_disk()["item"],
                         "the mutation did not reintroduce the defect")
        self.put_docket(record)
        agenda.refresh_docket()
        self.assertIn("outcome", self.docket_on_disk()["item"],
                      "the control did not hold the line")

    def test_M3_dropping_the_extra_save_clause_loses_the_carry_on_disk(self):
        """THE ALIASING MUTATION, and the reason every evidence cell asserts
        against the file rather than the return value. Without `or carried`
        the carry happens in memory, `carried_evidence()` reports it, and the
        docket on disk never learns it: a repair that says it ran."""
        mutant = _mutant("alias_bug",
                         "        if result != existing or carried:",
                         "        if result != existing:")
        self.put_file("item", "done", outcome="a sentence with 0.42 in it")
        record = {"id": "item", "objective": "objective for item",
                  "rationale": "r", "est_core_min": 10,
                  "cost_basis": "estimate", "expected_knowledge_gain": "g",
                  "status": "proposed", "source_kind": "inbox"}
        self.put_docket(record)
        returned = {p["id"]: p for p in mutant.refresh_docket()}
        self.assertIn("outcome", returned["item"],
                      "the mutation did not model the defect")
        self.assertEqual([(c["id"], c["field"])
                          for c in mutant.carried_evidence()],
                         [("item", "outcome")])
        self.assertNotIn("outcome", self.docket_on_disk()["item"],
                         "the mutation did not model the defect: it reached "
                         "disk anyway")
        self.put_docket(record)
        agenda.refresh_docket()
        self.assertIn("outcome", self.docket_on_disk()["item"],
                      "the control did not hold the line")

    def test_M4_widening_the_carried_set_to_status_breaks_the_ruling(self):
        """The mutation that turns this enforcement into the auto-promotion it
        was rejected in favour of: one word added to a tuple closes items on
        the filer's say-so."""
        mutant = _mutant(
            "status_carried",
            '_EVIDENCE_FIELDS = ("outcome", "measured_core_min")',
            '_EVIDENCE_FIELDS = ("outcome", "measured_core_min", "status")')
        self.put_file("item", "done", outcome="it found a number")
        record = {"id": "item", "objective": "objective for item",
                  "rationale": "r", "est_core_min": 10,
                  "cost_basis": "estimate", "expected_knowledge_gain": "g",
                  "status": "", "source_kind": "inbox"}
        self.put_docket(record)
        mutant.refresh_docket()
        self.assertEqual(self.docket_on_disk()["item"]["status"], "done",
                         "the mutation did not model the defect")
        self.put_docket(record)
        agenda.refresh_docket()
        self.assertEqual(self.docket_on_disk()["item"]["status"], "",
                         "the control did not hold the line: the file's "
                         "status reached the docket")

    def test_M5_making_the_carry_overwrite_destroys_a_docket_record(self):
        """Additive-only is the safety argument; this is what it is safe
        against. An overwriting carry lets a stale file erase the docket's
        own record of what the work found."""
        mutant = _mutant(
            "carry_overwrites",
            '        if value in (None, "") or record.get(field) not in (None, ""):',
            '        if value in (None, ""):')
        self.put_file("item", "done", outcome="THE FILE'S VERSION")
        record = {"id": "item", "objective": "objective for item",
                  "rationale": "r", "est_core_min": 10,
                  "cost_basis": "estimate", "expected_knowledge_gain": "g",
                  "status": "done", "outcome": "THE DOCKET'S VERSION",
                  "source_kind": "inbox"}
        self.put_docket(record)
        mutant.refresh_docket()
        self.assertEqual(self.docket_on_disk()["item"]["outcome"],
                         "THE FILE'S VERSION",
                         "the mutation did not model the defect")
        self.put_docket(record)
        agenda.refresh_docket()
        self.assertEqual(self.docket_on_disk()["item"]["outcome"],
                         "THE DOCKET'S VERSION",
                         "the control did not hold the line")


if __name__ == "__main__":
    unittest.main()
