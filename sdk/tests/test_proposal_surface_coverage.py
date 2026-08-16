"""The one-sided rule and the third-surface join, with both controls. (D222.)

WHAT THE CHECK UNDER TEST PROMISES, AND WHERE EACH PROMISE COMES FROM
=====================================================================
Every expectation here is derived from the SPECIFICATION -- the rule stated in
docket row D222 and in the check's own docstring, and the clauses of
`chief_engineer.agenda` that rule is read out of -- and never from reading the
current text of `scripts/check_proposal_surface_coverage.py`. That distinction
is why this preamble exists: on 2026-08-15 a guard in this tree was written by
reading an already-mutated file, asserted the mutant, passed, and survived its
own mutation proof. A mutation proof shows a test detects *a* change. Only a
specification-derived expectation shows it detects the *right* one.

    S1  An inbox-only id carrying a DECIDED status (anything past `proposed`)
        is LOST and is a fault. `agenda.set_status` is the only
        decision-recording function in the tree and it writes `docket.json`
        alone, so a decision that exists only in a file exists nowhere any
        consumer can act on.
    S2  An inbox-only id still `proposed` is PENDING and is NOT a fault.
        `refresh_docket` merges any inbox id the docket does not hold, so it
        is one refresh from the docket and nothing is lost meanwhile.
        THE NEGATIVE CONTROL.
    S3  A docket-only id from a code drafter is DRAFTED and is NOT a fault.
        `draft_all()` has five sources and four are drafters that write no
        file, so a docket record without a file is the system's normal output.
        THE SECOND HALF OF THE NEGATIVE CONTROL, and the larger half: 189 of
        the 245 one-sided ids are in it, so a rule that called one-sided ids
        faults would manufacture 189 of them.
    S4  A docket-only id whose `source_kind` IS `inbox` is ORPHANED and is a
        fault: it entered from a file that no longer exists.
    S5  An inbox-only id that `read_inbox` refuses is BLOCKED and is a fault
        even while it is still `proposed`, because no refresh can ever merge
        it -- it is not lost yet, it is unable ever to arrive.
    S6  An inbox-only id whose normalized objective is already held by a
        DIFFERENT docket id is SHADOWED and is a fault: `refresh_docket` skips
        on the objective key, so it can never merge either.
    S7  An artifact naming an item the docket holds OPEN, where the docket
        record carries none of the trace fields, is UNABSORBED. This is the
        only clause that can reach BOTH SURFACES WRONG TOGETHER, because the
        artifact is evidence that work happened rather than a record of what
        somebody believed.
    S8  An artifact naming a CLOSED item, or an open item whose docket record
        already carries a trace, is NOT unabsorbed. THE THIRD NEGATIVE
        CONTROL: a check that fired on every artifact would redden on every
        item that ever produced one, which is every item worth having.
    S9  Zero ids classified is UNKNOWN with a reason, never PASS (class B1).
    S10 A surface that cannot be read is UNKNOWN, never PASS and never FAIL.
    S11 Exit contract 0 PASS / 1 FAIL / 3 UNKNOWN, so `lab_check.py` reads it
        without an adapter.
    S12 A SHARED id is not this check's population at all. Shared ids belong
        to `check_docket_surface_agreement.py`; classifying one here would
        double-count the tree and put this check in the business of a join it
        deliberately is not.

BOTH CONTROLS, WHICH IS L-84
============================
    FIRES      a planted LOST id, a planted ORPHANED id, a planted BLOCKED id,
               a planted SHADOWED id and a planted UNABSORBED id each turn the
               verdict FAIL and each is named in the finding
    DOES NOT   a PENDING id, a DRAFTED id, a closed item with an artifact, an
    FIRE       open item with an artifact AND a trace, and every shared id,
               all leave the verdict PASS and are still counted in the frame

MUTATION DISCIPLINE
===================
Mutants are substituted COPIES written into a temporary tree; the tracked file
is never edited, because a harness that held a tracked file mutated in place for
ten minutes on 2026-08-15 had the mutant captured into HEAD by a concurrent
commit with `git status` clean throughout. And `killed = returncode != 0` is not
used: once a control is red every mutant "dies" and every survivor is scored a
kill. The control is asserted GREEN first and each mutant is judged by the
FAILURE-COUNT DELTA against that zero, with the dead probes named.

Every probe that owns a class NAMES THE ID and NAMES THE CLASS. A probe that
asserted only a fault COUNT would survive any mutation that swaps two classes,
which is precisely what half the mutations below do.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
_SOURCE = REPO / "scripts" / "check_proposal_surface_coverage.py"
_SPEC = importlib.util.spec_from_file_location(
    "check_proposal_surface_coverage_under_test", _SOURCE)
chk = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = chk
_SPEC.loader.exec_module(chk)


def _mutant(name: str, old: str, new: str):
    """The check with one substitution, loaded from a COPY in a temp tree.

    The copy sits at `<tmp>/scripts/<same name>.py` so its own `parents[1]`
    lands in the temporary tree and no mutant can reach the live agenda by
    accident.
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
    target = root / "scripts" / _SOURCE.name
    target.write_text(text.replace(old, new), encoding="utf-8")
    spec = importlib.util.spec_from_file_location(f"cpsc_{name}", target)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.__keepalive = tmp          # noqa: SLF001 - hold the tempdir open
    return module


# --------------------------------------------------------------------------
# Fixtures. Deliberately tiny, so a count in an assertion is readable by eye.
# --------------------------------------------------------------------------

def _rec(item_id, status, *, objective=None, kind="inbox", core_min=10,
         **extra):
    out = {"id": item_id, "status": status, "est_core_min": core_min,
           "objective": objective if objective is not None else item_id,
           "source_kind": kind}
    out.update(extra)
    return out


#: One fixture pair covering every class at once, so the positive and negative
#: controls are read off the SAME population and cannot differ in anything but
#: the clause under test.
def _population():
    inbox = {
        "lost-done": _rec("lost-done", "done"),
        "lost-approved": _rec("lost-approved", "approved"),
        "pending": _rec("pending", "proposed"),
        "blocked": _rec("blocked", "proposed"),
        "shadowed": _rec("shadowed", "proposed", objective="Same Objective"),
        "shared": _rec("shared", "done"),
    }
    docket = {
        "orphaned": _rec("orphaned", "proposed", kind="inbox"),
        "drafted": _rec("drafted", "proposed", kind="report"),
        "holder": _rec("holder", "proposed", objective="same objective",
                       kind="report"),
        "shared": _rec("shared", "done", kind="inbox"),
    }
    return inbox, docket


REFUSED = {"blocked"}


def _classify(**kwargs):
    inbox, docket = _population()
    return chk.classify(inbox, docket, REFUSED, kwargs.pop("named", {}))


def _classes(result):
    return {row["id"]: row["class"] for row in result["rows"]}


# --------------------------------------------------------------------------
# The probe set. One probe per specification clause, expressed against a
# MODULE, so a mutant goes through exactly the battery the control does.
# --------------------------------------------------------------------------

def _run(mod, named=None):
    inbox, docket = _population()
    return mod.classify(inbox, docket, REFUSED, named or {})


def _mapping(mod, named=None):
    return {row["id"]: row["class"] for row in _run(mod, named)["rows"]}


def probe_a_decided_inbox_only_id_is_LOST(mod):
    """S1. NAMES THE ID AND THE CLASS: a probe asserting only that some fault
    exists survives every mutation that swaps two classes."""
    seen = _mapping(mod)
    assert seen.get("lost-done") == "LOST", seen
    assert seen.get("lost-approved") == "LOST", seen
    assert _run(mod)["verdict"] == mod.FAIL


def probe_an_undecided_inbox_only_id_is_PENDING(mod):
    """S2, the NEGATIVE control. `proposed` alone is never a fault."""
    seen = _mapping(mod)
    assert seen.get("pending") == "PENDING", seen
    assert "PENDING" not in mod.FAULTS, sorted(mod.FAULTS)


def probe_a_drafted_docket_only_id_is_not_a_fault(mod):
    """S3, the larger half of the negative control. 189 of the live 245 are
    here, so a rule that judged one-sided ids faults would invent 189."""
    seen = _mapping(mod)
    assert seen.get("drafted") == "DRAFTED", seen
    assert "DRAFTED" not in mod.FAULTS, sorted(mod.FAULTS)


def probe_an_inbox_sourced_docket_only_id_is_ORPHANED(mod):
    """S4."""
    seen = _mapping(mod)
    assert seen.get("orphaned") == "ORPHANED", seen
    assert "ORPHANED" in mod.FAULTS


def probe_a_refused_file_is_BLOCKED_even_while_proposed(mod):
    """S5. BLOCKED outranks PENDING: an undecided file that can never arrive
    is a fault, and if the two were the other way round the class would be
    silently absorbed into the benign one."""
    seen = _mapping(mod)
    assert seen.get("blocked") == "BLOCKED", seen


def probe_an_objective_collision_is_SHADOWED(mod):
    """S6. The collision key is `refresh_docket`'s, not this check's."""
    seen = _mapping(mod)
    assert seen.get("shadowed") == "SHADOWED", seen


def probe_a_shared_id_is_never_classified(mod):
    """S12. Shared ids belong to the join check; classifying one here would
    double-count the tree."""
    seen = _mapping(mod)
    assert "shared" not in seen, seen
    assert _run(mod)["shared"] == 1, _run(mod)["shared"]


def probe_an_artifact_on_an_open_untraced_item_is_UNABSORBED(mod):
    """S7. The both-surfaces-wrong-together reach."""
    result = _run(mod, {"orphaned": ["some/report.json"]})
    ids = [row["id"] for row in result["unabsorbed"]]
    assert ids == ["orphaned"], result["unabsorbed"]
    assert result["verdict"] == mod.FAIL


def probe_an_artifact_on_a_closed_item_does_not_fire(mod):
    """S8, the third NEGATIVE control. Every item worth having produces an
    artifact; a check that fired on all of them is a check nobody can pass."""
    inbox, docket = _population()
    docket["drafted"]["status"] = "done"
    result = mod.classify(inbox, docket, REFUSED,
                          {"drafted": ["some/report.json"]})
    assert [r["id"] for r in result["unabsorbed"]] == [], result["unabsorbed"]


def probe_an_artifact_on_an_item_with_a_trace_does_not_fire(mod):
    """S8 again, the other half: the docket ABSORBED the artifact's finding,
    which is the repair the rule names, so the fault is gone."""
    inbox, docket = _population()
    docket["drafted"]["outcome"] = "measured 0.056647 against the board"
    result = mod.classify(inbox, docket, REFUSED,
                          {"drafted": ["some/report.json"]})
    assert [r["id"] for r in result["unabsorbed"]] == [], result["unabsorbed"]


def probe_a_clean_population_PASSES(mod):
    """The instrument must be capable of silence, or its FAIL means nothing."""
    inbox = {"pending": _rec("pending", "proposed")}
    docket = {"drafted": _rec("drafted", "proposed", kind="report")}
    result = mod.classify(inbox, docket, set(), {})
    assert result["verdict"] == mod.PASS, result["reason"]
    assert result["one_sided"] == 2, result["one_sided"]


def probe_empty_population_is_UNKNOWN(mod):
    """S9, defect class B1: an empty selection has examined nothing."""
    result = mod.classify({}, {}, set(), {})
    assert result["verdict"] == mod.UNKNOWN, result["verdict"]
    assert result["verdict"] != mod.PASS
    assert "empty selection is never a pass" in result["reason"], \
        result["reason"]


def probe_a_fully_shared_population_is_UNKNOWN(mod):
    """S9 and S12 together, and this is the case that actually happens: two
    surfaces that agree perfectly leave this check with nothing one-sided to
    classify, and "no one-sided fault was found" over an empty population is
    the silent zero, not a pass."""
    both = {"a": _rec("a", "done")}
    result = mod.classify(dict(both), dict(both), set(), {})
    assert result["verdict"] == mod.UNKNOWN, result["verdict"]


def probe_exit_contract(mod):
    """S11."""
    assert mod.EXIT[mod.PASS] == 0, mod.EXIT
    assert mod.EXIT[mod.FAIL] == 1, mod.EXIT
    assert mod.EXIT[mod.UNKNOWN] == 3, mod.EXIT


PROBES = (probe_a_decided_inbox_only_id_is_LOST,
          probe_an_undecided_inbox_only_id_is_PENDING,
          probe_a_drafted_docket_only_id_is_not_a_fault,
          probe_an_inbox_sourced_docket_only_id_is_ORPHANED,
          probe_a_refused_file_is_BLOCKED_even_while_proposed,
          probe_an_objective_collision_is_SHADOWED,
          probe_a_shared_id_is_never_classified,
          probe_an_artifact_on_an_open_untraced_item_is_UNABSORBED,
          probe_an_artifact_on_a_closed_item_does_not_fire,
          probe_an_artifact_on_an_item_with_a_trace_does_not_fire,
          probe_a_clean_population_PASSES,
          probe_empty_population_is_UNKNOWN,
          probe_a_fully_shared_population_is_UNKNOWN,
          probe_exit_contract)


def failures(mod) -> list[str]:
    """Names of the probes that fail against `mod`. Never a returncode."""
    dead = []
    for probe in PROBES:
        try:
            probe(mod)
        except AssertionError as exc:
            dead.append(f"{probe.__name__}: {exc}")
        except Exception as exc:                       # noqa: BLE001
            dead.append(f"{probe.__name__}: raised {type(exc).__name__}: {exc}")
    return dead


# --------------------------------------------------------------------------
# The cells
# --------------------------------------------------------------------------

class TestTheProbesAreTheSpecification(unittest.TestCase):

    def test_control_is_green(self):
        """THE PRECONDITION FOR EVERY MUTATION BELOW. Without it,
        `killed = returncode != 0` scores every survivor a kill."""
        self.assertEqual(failures(chk), [])


class TestBothControls(unittest.TestCase):
    """L-84: an instrument that only ever fires proves nothing about reach."""

    def test_the_positive_control_fires_and_names_every_fault(self):
        result = _classify()
        self.assertEqual(result["verdict"], chk.FAIL)
        self.assertEqual(
            sorted(result["faults"]),
            ["blocked", "lost-approved", "lost-done", "orphaned", "shadowed"])

    def test_the_negative_control_is_silent_over_the_same_population(self):
        """Same fixture, faults removed, nothing else changed."""
        inbox = {"pending": _rec("pending", "proposed")}
        docket = {"drafted": _rec("drafted", "proposed", kind="report")}
        result = chk.classify(inbox, docket, set(), {})
        self.assertEqual(result["verdict"], chk.PASS)
        self.assertEqual(result["faults"], [])
        self.assertEqual(result["counts"], {"PENDING": 1, "DRAFTED": 1})

    def test_the_two_controls_differ_only_in_which_ids_are_present(self):
        """A matched pair. If they differed in more than the presence of the
        fault ids, the negative control would prove nothing about the
        positive one."""
        fires = _classify()
        silent = chk.classify({"pending": _rec("pending", "proposed")},
                              {"drafted": _rec("drafted", "proposed",
                                               kind="report")}, set(), {})
        self.assertEqual(_classes(silent),
                         {k: v for k, v in _classes(fires).items()
                          if k in ("pending", "drafted")})

    def test_no_class_is_both_a_fault_and_legitimate(self):
        """The two tables partition the vocabulary. A class in neither would
        be counted, printed, and silently ungraded -- which is the shape of
        the defect this whole check exists for."""
        self.assertEqual(set(chk.FAULTS) & set(chk.LEGITIMATE), set())
        seen = {row["class"] for row in _classify()["rows"]}
        self.assertTrue(seen <= set(chk.FAULTS) | set(chk.LEGITIMATE), seen)

    def test_every_fault_class_states_its_repair(self):
        """A class with no stated repair is a complaint, not a check."""
        for klass, repair in chk.FAULTS.items():
            self.assertTrue(len(repair) > 20, klass)


class TestTheRuleIsReadOutOfTheModuleItGoverns(unittest.TestCase):
    """The rule is derived, not invented. These assertions are what make that
    claim falsifiable: if `agenda` changes underneath, they redden here rather
    than leaving the check quietly measuring its own opinion."""

    def setUp(self):
        sys.path.insert(0, str(REPO / "sdk"))
        try:
            from chief_engineer import agenda
        finally:
            sys.path.pop(0)
        self.agenda = agenda

    def test_UNDECIDED_is_the_status_agenda_starts_a_proposal_in(self):
        self.assertIn(chk.UNDECIDED, self.agenda.STATUSES)
        self.assertEqual(chk.UNDECIDED, "proposed")

    def test_every_status_past_UNDECIDED_is_a_decision(self):
        """S1's whole basis: every other member of the vocabulary records a
        decision somebody took, so a file alone may not hold one."""
        decided = set(self.agenda.STATUSES) - {chk.UNDECIDED}
        self.assertEqual(decided, {"approved", "approved-queued", "dismissed",
                                   "done"})
        self.assertTrue(set(chk.CLOSED) <= decided)

    def test_the_objective_key_is_the_one_refresh_docket_collides_on(self):
        """SHADOWED is defined by `refresh_docket`'s own key. A second,
        drifting copy of the normalizer would make this class fiction."""
        for text in ("Same  Objective", " SAME objective ", "same objective"):
            self.assertEqual(chk.normalize_objective(text),
                             self.agenda.normalize_objective(text))

    def test_set_status_writes_the_docket_alone(self):
        """The clause LOST rests on. If a decision could be recorded anywhere
        else, an inbox-only decision would not be lost."""
        import inspect
        source = inspect.getsource(self.agenda.set_status)
        self.assertIn("save_docket", source)
        self.assertNotIn("inbox", source)


class TestEmptySelectionIsNeverAPass(unittest.TestCase):
    """Defect class B1."""

    def test_both_surfaces_empty_is_unknown(self):
        self.assertEqual(chk.classify({}, {}, set(), {})["verdict"],
                         chk.UNKNOWN)

    def test_perfectly_overlapping_surfaces_are_unknown_not_pass(self):
        both = {"a": _rec("a", "done")}
        result = chk.classify(dict(both), dict(both), set(), {})
        self.assertEqual(result["verdict"], chk.UNKNOWN)
        self.assertIn("empty selection is never a pass", result["reason"])

    def test_a_missing_docket_is_unknown_not_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            agenda = Path(tmp) / "agenda"
            (agenda / "proposals").mkdir(parents=True)
            self.assertEqual(
                chk.main(["--agenda", str(agenda), "--artifacts", tmp]), 3)

    def test_a_missing_inbox_directory_is_unknown_not_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            agenda = Path(tmp) / "agenda"
            agenda.mkdir(parents=True)
            (agenda / "docket.json").write_text(
                json.dumps({"proposals": [_rec("a", "done")]}),
                encoding="utf-8")
            self.assertEqual(
                chk.main(["--agenda", str(agenda), "--artifacts", tmp]), 3)

    def test_an_unparseable_proposal_file_is_unknown_for_the_whole_run(self):
        """Not a skipped row: a coverage check that quietly drops the file it
        could not read reports coverage over a smaller set than it claims."""
        with tempfile.TemporaryDirectory() as tmp:
            agenda = Path(tmp) / "agenda"
            (agenda / "proposals").mkdir(parents=True)
            (agenda / "proposals" / "a.json").write_text(
                json.dumps(_rec("a", "proposed")), encoding="utf-8")
            (agenda / "proposals" / "broken.json").write_text(
                "{not json", encoding="utf-8")
            (agenda / "docket.json").write_text(
                json.dumps({"proposals": [_rec("a", "proposed")]}),
                encoding="utf-8")
            self.assertEqual(
                chk.main(["--agenda", str(agenda), "--artifacts", tmp]), 3)


class TestTheArtifactSectionNeverReadsAsAgreement(unittest.TestCase):
    """An empty artifact scan examined nothing. It may not print as a clean
    section, which is class B1 applied sectionally rather than to the run."""

    def test_zero_back_references_prints_no_statement_available(self):
        rendered = chk.render(_classify(), scanned=500, unreadable=0,
                              backrefs=0)
        self.assertIn("NO STATEMENT AVAILABLE", rendered)

    def test_the_reach_is_printed_as_a_share_of_the_docket(self):
        rendered = chk.render(_classify(), scanned=500, unreadable=0,
                              backrefs=4)
        self.assertIn("of the docket", rendered)
        self.assertIn("never about", rendered)

    def test_unreadable_artifacts_are_counted_not_swallowed(self):
        rendered = chk.render(_classify(), scanned=500, unreadable=7,
                              backrefs=4)
        self.assertIn("unreadable (reach lost)", rendered)
        self.assertIn("7", rendered)

    def test_an_agenda_entry_path_reduces_to_the_id(self):
        """`agenda_entry` names the FILE and `item` names the id; both must
        reduce to the same key or the join silently matches nothing."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "demo-output"
            (root / "sub").mkdir(parents=True)
            (root / "sub" / "report.json").write_text(json.dumps(
                {"agenda_entry": "demo-output/website/agenda/proposals/"
                                 "r2-closure.json"}), encoding="utf-8")
            (root / "sub" / "other.json").write_text(
                json.dumps({"item": "w3-qcr"}), encoding="utf-8")
            named, scanned, unreadable = chk.scan_artifacts(root)
        self.assertEqual(sorted(named), ["r2-closure", "w3-qcr"])
        self.assertEqual((scanned, unreadable), (2, 0))


class TestTheFrameIsPrintedEveryRun(unittest.TestCase):

    def test_every_frame_number_is_on_stdout(self):
        rendered = chk.render(_classify(), scanned=1, unreadable=0, backrefs=1)
        for line in ("inbox ids", "docket ids", "shared ids", "ONE-SIDED",
                     "CLASSIFICATION", "ARTIFACT BACK-REFERENCE", "VERDICT:"):
            self.assertIn(line, rendered)

    def test_the_legitimate_classes_are_printed_too_not_only_the_faults(self):
        """235 of the live 245 are legitimate. A frame that printed only the
        faults would make the population look like it was mostly broken."""
        rendered = chk.render(_classify(), scanned=1, unreadable=0, backrefs=1)
        self.assertIn("PENDING", rendered)
        self.assertIn("DRAFTED", rendered)


class TestItReachesTheLiveSurfaces(unittest.TestCase):
    """Reach measured on the real tree, not inferred from fixtures (L-84)."""

    def test_the_live_population_is_non_empty_and_three_valued(self):
        inbox = chk.load_inbox(chk.AGENDA / "proposals")
        docket = chk.load_docket(chk.AGENDA / "docket.json")
        result = chk.classify(inbox, docket, chk.refused_ids(chk.AGENDA), {})
        self.assertGreater(result["one_sided"], 0,
                           "the live population is empty: the instrument is "
                           "not reaching the surfaces")
        self.assertIn(result["verdict"], (chk.PASS, chk.FAIL))

    def test_the_script_runs_as_a_subprocess_under_the_exit_contract(self):
        proc = subprocess.run(
            [sys.executable, str(_SOURCE)], capture_output=True, text=True,
            cwd=str(REPO), timeout=600)
        self.assertIn(proc.returncode, (0, 1, 3), proc.stderr[-800:])
        self.assertIn("VERDICT:", proc.stdout)
        self.assertIn("FRAME", proc.stdout)


class TestMutations(unittest.TestCase):
    """Each guard proved by removing it and watching NAMED probes die.
    Judged by failure-count delta against a control asserted green, never by a
    returncode."""

    def _delta(self, mutant, expected_dead):
        dead = failures(mutant)
        self.assertEqual(failures(chk), [], "control went red mid-run")
        self.assertGreater(
            len(dead), 0,
            "SURVIVOR: the mutation changed the check and no probe noticed")
        names = {d.split(":")[0] for d in dead}
        self.assertTrue(
            expected_dead <= names,
            f"the mutation killed {sorted(names)} but the probes this guard "
            f"is supposed to own are {sorted(expected_dead)}")

    def test_M1_inverting_the_decided_test_swaps_LOST_and_PENDING(self):
        """The class-swap mutation, and the reason every probe names its id
        and its class: a probe asserting a fault COUNT survives this."""
        mutant = _mutant("decided_inverted",
                         "        elif status != UNDECIDED:",
                         "        elif status == UNDECIDED:")
        self._delta(mutant, {"probe_a_decided_inbox_only_id_is_LOST",
                             "probe_an_undecided_inbox_only_id_is_PENDING"})

    def test_M2_inverting_the_source_kind_test_swaps_ORPHANED_and_DRAFTED(self):
        """The negative control's own mutation, and the expensive one: on the
        live tree it turns all 189 legitimately drafted records into faults."""
        mutant = _mutant("kind_inverted", 'if kind == "inbox":',
                         'if kind != "inbox":')
        self._delta(mutant,
                    {"probe_an_inbox_sourced_docket_only_id_is_ORPHANED",
                     "probe_a_drafted_docket_only_id_is_not_a_fault"})

    def test_M3_defanging_the_refusal_test_hides_BLOCKED(self):
        mutant = _mutant("refusal_off", "        if item_id in refused:",
                         "        if item_id in ():")
        self._delta(mutant,
                    {"probe_a_refused_file_is_BLOCKED_even_while_proposed"})

    def test_M4_defanging_the_collision_test_hides_SHADOWED(self):
        mutant = _mutant("collision_off",
                         "        elif collided and collided != item_id:",
                         "        elif collided and collided == item_id:")
        self._delta(mutant, {"probe_an_objective_collision_is_SHADOWED"})

    def test_M5_dropping_the_closed_guard_fires_on_every_finished_item(self):
        """S8's mutation. Without it the artifact section reddens on every
        item that ever produced a report, which is every item worth having."""
        mutant = _mutant("closed_guard_off", "        if status in CLOSED:",
                         "        if status in ():")
        self._delta(mutant, {"probe_an_artifact_on_a_closed_item_does_not_fire"})

    def test_M6_dropping_the_trace_guard_ignores_the_repair(self):
        """The rule's repair is to move the record INTO the docket. Without
        this guard the check keeps firing after the repair is done, which
        makes the repair unrewarding and the check unread."""
        mutant = _mutant("trace_guard_off", "        if traces:\n",
                         "        if False:\n")
        self._delta(mutant,
                    {"probe_an_artifact_on_an_item_with_a_trace_does_not_fire"})

    def test_M7_removing_the_empty_set_guard_lets_nothing_PASS(self):
        """B1. Without it, zero classified ids falls through to the clean
        branch and reports coverage having classified nothing."""
        mutant = _mutant(
            "empty_pass",
            "    if not rows and not unabsorbed:\n        verdict = UNKNOWN",
            "    if False:\n        verdict = UNKNOWN")
        self.assertEqual(mutant.classify({}, {}, set(), {})["verdict"],
                         mutant.PASS,
                         "the mutation did not reintroduce the defect")
        self._delta(mutant, {"probe_empty_population_is_UNKNOWN",
                             "probe_a_fully_shared_population_is_UNKNOWN"})

    def test_M8_classifying_the_union_drags_in_every_shared_id(self):
        """S12. A population that reaches too far double-counts the tree and
        starts reporting the join's findings as coverage faults."""
        mutant = _mutant("union_population",
                         "    for item_id in sorted(set(inbox) - set(docket)):",
                         "    for item_id in sorted(set(inbox)):")
        self._delta(mutant, {"probe_a_shared_id_is_never_classified"})

    def test_M9_breaking_the_exit_contract_is_caught(self):
        mutant = _mutant("exit_contract_broken",
                         "EXIT = {PASS: 0, FAIL: 1, UNKNOWN: 3}",
                         "EXIT = {PASS: 0, FAIL: 0, UNKNOWN: 0}")
        self._delta(mutant, {"probe_exit_contract"})

    def test_M10_an_unreadable_surface_downgraded_to_PASS_is_caught(self):
        """S10. Outside `classify`, so it is proved against the cell that owns
        it rather than the pure probe battery."""
        mutant = _mutant("surface_error_passes",
                         "        return EXIT[UNKNOWN]\n",
                         "        return EXIT[PASS]\n")
        with tempfile.TemporaryDirectory() as tmp:
            agenda = Path(tmp) / "agenda"
            agenda.mkdir(parents=True)
            self.assertEqual(
                mutant.main(["--agenda", str(agenda), "--artifacts", tmp]), 0,
                "the mutation did not model the defect")
            self.assertEqual(
                chk.main(["--agenda", str(agenda), "--artifacts", tmp]), 3,
                "the control did not hold the line")


if __name__ == "__main__":
    unittest.main()
