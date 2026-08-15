"""The inbox/docket status join, with both controls. (D218, D219, 2026-08-15.)

WHAT THE CHECK UNDER TEST PROMISES, AND WHERE EACH PROMISE COMES FROM
=====================================================================
Every expectation asserted here is derived from the specification -- docket rows
D218 and D219 and the check's own docstring -- and NOT from reading the current
state of `scripts/check_docket_surface_agreement.py`. That distinction is the
whole point today: a guard written on 2026-08-15 by reading an already-mutated
HEAD asserted the mutant, passed, and was mutation-proved. A mutation proof
shows a test detects *a* change; only a specification-derived expectation shows
it detects the *right* one.

    S1  A shared id whose two statuses differ is a fault.        (D218)
    S2  An id present on ONE surface only is NOT a fault: no rule exists
        saying which surface may hold an item alone, and D218 says so in
        terms.                                                    (D218 (2))
    S3  Zero shared ids is UNKNOWN with a reason, never PASS. An empty
        selection has examined nothing.               (defect class B1, D123)
    S4  A surface that cannot be read is UNKNOWN, never PASS and never FAIL:
        it is a statement about the instrument, not the lab.       (D101)
    S5  A status outside the closed vocabulary is a fault, because
        `agenda.read_inbox` silently coerces it to "proposed" and every
        consumer that goes through the module is therefore blind to it.
    S6  Exit contract 0 PASS / 1 FAIL / 3 UNKNOWN, so `scripts/lab_check.py`
        reads it without an adapter.                                  (D64)

BOTH CONTROLS, WHICH IS L-84
============================
A positive control proves the instrument can fire; it does not prove its reach,
and a check that only ever fires is a check nobody can trust to be silent. So
both directions are here:

    FIRES      a planted disagreement on a shared id turns the verdict FAIL
    DOES NOT   a legitimately one-sided id -- inbox-only and docket-only, with
    FIRE       statuses that WOULD disagree if the two were joined -- leaves
               the verdict PASS, and is still counted in the printed frame

MUTATION DISCIPLINE
===================
Mutants are built by writing a substituted COPY into a temporary directory
(`_mutant`, the pattern already in `test_empty_set_is_not_agreement.py`). The
tracked file is never edited: a harness that held `scripts/self_audit.py`
mutated in place for ten minutes on 2026-08-15 had two live mutants captured
into HEAD by a concurrent commit, where `git status` read clean the whole time.

And `killed = returncode != 0` is not used anywhere here. Once a control is red
every mutant "dies" and every survivor is scored a kill. The control is asserted
GREEN first (`test_control_is_green`, zero probe failures on the real module),
and each mutant is judged by the FAILURE-COUNT DELTA against that zero, with the
probes that died named in the assertion message.
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
_SOURCE = REPO / "scripts" / "check_docket_surface_agreement.py"
_SPEC = importlib.util.spec_from_file_location(
    "check_docket_surface_agreement_under_test", _SOURCE)
chk = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = chk
_SPEC.loader.exec_module(chk)


def _mutant(name: str, old: str, new: str):
    """The check with one substitution, loaded from a COPY in a temp tree.

    The copy sits at `<tmp>/scripts/check_docket_surface_agreement.py` so its
    own `parents[1]` lands in the temporary tree and no mutant can reach the
    live agenda by accident.
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
    target = root / "scripts" / "check_docket_surface_agreement.py"
    target.write_text(text.replace(old, new), encoding="utf-8")
    spec = importlib.util.spec_from_file_location(f"cdsa_{name}", target)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.__keepalive = tmp          # noqa: SLF001 - hold the tempdir open
    return module


# --------------------------------------------------------------------------
# Fixtures. Deliberately tiny, so a count in an assertion is readable by eye.
# --------------------------------------------------------------------------

def _rec(item_id, status, core_min=10):
    return {"id": item_id, "status": status, "est_core_min": core_min}


def _surfaces(pairs):
    """pairs: {id: (inbox_status_or_None, docket_status_or_None)}."""
    inbox, docket = {}, {}
    for item_id, (in_status, dk_status) in pairs.items():
        if in_status is not None:
            inbox[item_id] = _rec(item_id, in_status)
        if dk_status is not None:
            docket[item_id] = _rec(item_id, dk_status)
    return inbox, docket


AGREEING = {"a": ("done", "done"), "b": ("approved", "approved")}
DISAGREEING = {"a": ("done", "done"), "b": ("proposed", "done")}
#: S2's control: two one-sided ids whose statuses WOULD disagree if the two
#: surfaces were joined on them. Nothing here may fire.
ONE_SIDED_ONLY = {"a": ("done", "done"),
                  "inbox-only-item": ("proposed", None),
                  "docket-only-item": (None, "done")}


# --------------------------------------------------------------------------
# The probe set. Each probe is one specification clause, expressed against a
# module rather than against the import at the top, so a mutant can be put
# through exactly the same battery as the control.
# --------------------------------------------------------------------------

def probe_disagreement_fails(mod):
    """S1."""
    result = mod.compare(*_surfaces(DISAGREEING))
    assert result["verdict"] == mod.FAIL, result["verdict"]
    assert result["disagreeing"] == 1, result["disagreeing"]
    # NAME THE ID, do not just count. A count of one is satisfied by the
    # WRONG one: inverting `!=` to `==` in `compare` makes the agreeing id
    # the reported disagreement, keeps the count at one, keeps the verdict
    # FAIL, and this probe survived the mutation until the id went in.
    assert [r["id"] for r in result["disagreements"]] == ["b"], \
        result["disagreements"]
    assert (result["disagreements"][0]["inbox"],
            result["disagreements"][0]["docket"]) == ("proposed", "done")


def probe_agreement_passes(mod):
    """S1, the other way: agreement over a non-empty join is PASS."""
    result = mod.compare(*_surfaces(AGREEING))
    assert result["verdict"] == mod.PASS, result["verdict"]
    assert result["shared"] == 2, result["shared"]


def probe_one_sided_does_not_fire(mod):
    """S2, the NEGATIVE control: one-sided ids are counted, never judged."""
    result = mod.compare(*_surfaces(ONE_SIDED_ONLY))
    assert result["verdict"] == mod.PASS, result["verdict"]
    assert result["disagreeing"] == 0, result["disagreeing"]
    assert result["inbox_only"] == ["inbox-only-item"], result["inbox_only"]
    assert result["docket_only"] == ["docket-only-item"], result["docket_only"]


def probe_empty_join_is_unknown(mod):
    """S3, defect class B1. Both surfaces non-empty, overlap empty."""
    inbox, docket = _surfaces({"only-in-inbox": ("proposed", None),
                               "only-in-docket": (None, "done")})
    result = mod.compare(inbox, docket)
    assert result["verdict"] == mod.UNKNOWN, result["verdict"]
    assert result["verdict"] != mod.PASS
    assert "zero shared" in result["reason"], result["reason"]


def probe_both_surfaces_empty_is_unknown(mod):
    """S3 again, the degenerate case a sweep hits when it is pointed at the
    wrong directory: nothing on either side is still not agreement."""
    result = mod.compare({}, {})
    assert result["verdict"] == mod.UNKNOWN, result["verdict"]


def probe_bad_vocabulary_fails(mod):
    """S5."""
    inbox, docket = _surfaces({"a": ("queued", "queued")})
    result = mod.compare(inbox, docket)
    assert result["verdict"] == mod.FAIL, result["verdict"]
    assert result["disagreeing"] == 0, "the two agree; only the word is bad"
    assert [r["status"] for r in result["bad_vocab"]] == ["queued", "queued"]


def probe_exit_contract(mod):
    """S6."""
    assert mod.EXIT[mod.PASS] == 0, mod.EXIT
    assert mod.EXIT[mod.FAIL] == 1, mod.EXIT
    assert mod.EXIT[mod.UNKNOWN] == 3, mod.EXIT


PROBES = (probe_disagreement_fails, probe_agreement_passes,
          probe_one_sided_does_not_fire, probe_empty_join_is_unknown,
          probe_both_surfaces_empty_is_unknown, probe_bad_vocabulary_fails,
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
        """THE PRECONDITION FOR EVERY MUTATION BELOW.

        `killed = returncode != 0` is wrong once the control is red: both runs
        fail, so every mutant reports KILLED including the survivors. Nothing
        in this file may be read as a kill unless this cell is green.
        """
        self.assertEqual(failures(chk), [],
                         "the control is RED; no mutation result below means "
                         "anything until this is green")


class TestBothControls(unittest.TestCase):
    """L-84 in one class: the instrument fires, and it stays silent."""

    def test_positive_control_a_planted_disagreement_fires(self):
        result = chk.compare(*_surfaces(DISAGREEING))
        self.assertEqual(result["verdict"], chk.FAIL)
        self.assertEqual([r["id"] for r in result["disagreements"]], ["b"])
        self.assertEqual(result["disagreements"][0]["inbox"], "proposed")
        self.assertEqual(result["disagreements"][0]["docket"], "done")

    def test_negative_control_a_one_sided_id_does_not_fire(self):
        """The reach question. An id on one surface only is the THIRD CLASS
        and D218 (2) says explicitly it is not necessarily a fault."""
        result = chk.compare(*_surfaces(ONE_SIDED_ONLY))
        self.assertEqual(result["verdict"], chk.PASS)
        self.assertEqual(result["disagreements"], [])
        # ...and it is still visible. Not judged is not the same as not seen.
        rendered = chk.render(result)
        self.assertIn("present in one surface only", rendered)
        self.assertIn("inbox-only 1", rendered)
        self.assertIn("docket-only 1", rendered)

    def test_the_two_controls_differ_only_in_where_the_second_id_lives(self):
        """The controls are a matched pair: same statuses, same prices, and
        the ONLY difference is whether the disagreeing id is shared. If they
        differed in more than that, the negative control would prove nothing
        about the positive one."""
        fires = chk.compare(*_surfaces(DISAGREEING))
        silent = chk.compare(*_surfaces(ONE_SIDED_ONLY))
        self.assertEqual(fires["verdict"], chk.FAIL)
        self.assertEqual(silent["verdict"], chk.PASS)
        self.assertEqual(fires["shared"], 2)
        self.assertEqual(silent["shared"], 1)


class TestEmptySelectionIsNeverAPass(unittest.TestCase):
    """Defect class B1. Three separate checks in this tree were found passing
    on an empty selection on 2026-08-15 alone."""

    def test_no_shared_ids_is_unknown(self):
        inbox, docket = _surfaces({"x": ("proposed", None),
                                   "y": (None, "done")})
        result = chk.compare(inbox, docket)
        self.assertEqual(result["verdict"], chk.UNKNOWN)
        self.assertIn("empty selection is never a pass", result["reason"])

    def test_both_surfaces_empty_is_unknown(self):
        self.assertEqual(chk.compare({}, {})["verdict"], chk.UNKNOWN)

    def test_a_missing_docket_is_unknown_not_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            agenda = Path(tmp) / "agenda"
            (agenda / "proposals").mkdir(parents=True)
            code = chk.main(["--agenda", str(agenda)])
        self.assertEqual(code, 3)

    def test_a_missing_inbox_directory_is_unknown_not_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            agenda = Path(tmp) / "agenda"
            agenda.mkdir(parents=True)
            (agenda / "docket.json").write_text(
                json.dumps({"proposals": [_rec("a", "done")]}),
                encoding="utf-8")
            code = chk.main(["--agenda", str(agenda)])
        self.assertEqual(code, 3)

    def test_an_unparseable_proposal_file_is_unknown_for_the_whole_run(self):
        """Not a skipped row. A join that quietly dropped the file it could
        not read would report agreement over a smaller set than it claims."""
        with tempfile.TemporaryDirectory() as tmp:
            agenda = Path(tmp) / "agenda"
            (agenda / "proposals").mkdir(parents=True)
            (agenda / "proposals" / "a.json").write_text(
                json.dumps(_rec("a", "done")), encoding="utf-8")
            (agenda / "proposals" / "broken.json").write_text(
                "{not json", encoding="utf-8")
            (agenda / "docket.json").write_text(
                json.dumps({"proposals": [_rec("a", "done")]}),
                encoding="utf-8")
            code = chk.main(["--agenda", str(agenda)])
        self.assertEqual(code, 3)


class TestTheVocabulary(unittest.TestCase):

    def test_an_out_of_vocabulary_status_is_a_fault_even_when_both_agree(self):
        result = chk.compare(*_surfaces({"a": ("queued", "queued")}))
        self.assertEqual(result["verdict"], chk.FAIL)
        self.assertEqual(result["disagreeing"], 0)

    def test_the_vocabulary_matches_the_module_that_owns_it(self):
        """It is copied rather than imported so a widened `STATUSES` cannot
        turn this check green by itself -- but it must not silently DRIFT
        either, so the equality is asserted here where drift is visible."""
        sys.path.insert(0, str(REPO / "sdk"))
        try:
            from chief_engineer import agenda
        finally:
            sys.path.pop(0)
        self.assertEqual(tuple(chk.STATUSES), tuple(agenda.STATUSES))


class TestTheFrameIsPrintedEveryRun(unittest.TestCase):

    def test_every_frame_number_is_on_stdout(self):
        rendered = chk.render(chk.compare(*_surfaces(DISAGREEING)))
        for line in ("inbox ids", "docket ids", "shared ids", "agreeing",
                     "DISAGREEING", "present in one surface only",
                     "disagreement rate", "VERDICT:"):
            self.assertIn(line, rendered)

    def test_the_two_directions_are_never_summed(self):
        """Finished work advertised as available and authorised work shown as
        speculative cost different things; one number over both hides which is
        happening."""
        inbox, docket = _surfaces({"a": ("proposed", "done"),
                                   "b": ("proposed", "approved"),
                                   "c": ("done", "done")})
        rows = chk._direction_totals(chk.compare(inbox, docket)["disagreements"])
        self.assertEqual({r[0] for r in rows},
                         {"proposed -> done", "proposed -> approved"})


class TestItReachesTheLiveSurfaces(unittest.TestCase):
    """Reach, measured on the real tree rather than inferred from a planted
    control (L-84). A check whose join matches nothing on the live agenda is
    broken however green its fixtures are."""

    def test_the_live_join_is_non_empty_and_three_valued(self):
        inbox = chk.load_inbox(chk.AGENDA / "proposals")
        docket = chk.load_docket(chk.AGENDA / "docket.json")
        result = chk.compare(inbox, docket)
        self.assertGreater(result["shared"], 0,
                           "the live join matched nothing: UNKNOWN, and the "
                           "instrument is not reaching the surfaces")
        self.assertIn(result["verdict"], (chk.PASS, chk.FAIL))

    def test_the_script_runs_as_a_subprocess_under_the_exit_contract(self):
        proc = subprocess.run(
            [sys.executable, str(_SOURCE)], capture_output=True, text=True,
            cwd=str(REPO), timeout=120)
        self.assertIn(proc.returncode, (0, 1, 3), proc.stderr[-800:])
        self.assertIn("VERDICT:", proc.stdout)
        self.assertIn("FRAME", proc.stdout)


class TestMutations(unittest.TestCase):
    """Each guard proved by removing it and watching named probes die.

    Judged by failure-count delta against a control asserted green above, never
    by a returncode.
    """

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

    def test_removing_the_empty_set_guard_lets_an_empty_join_PASS(self):
        """B1. Without the guard, zero shared ids falls through to the clean
        branch and reports agreement having compared nothing."""
        mutant = _mutant("empty_set_pass",
                         "    if not shared:\n        verdict = UNKNOWN",
                         "    if False:\n        verdict = UNKNOWN")
        self.assertEqual(
            mutant.compare({}, {})["verdict"], mutant.PASS,
            "the mutation did not reintroduce the defect it exists to model")
        self._delta(mutant, {"probe_empty_join_is_unknown",
                             "probe_both_surfaces_empty_is_unknown"})

    def test_inverting_the_status_comparison_kills_the_positive_control(self):
        mutant = _mutant("compare_inverted",
                         "if inbox_status != docket_status:",
                         "if inbox_status == docket_status:")
        self._delta(mutant, {"probe_disagreement_fails",
                             "probe_agreement_passes"})

    def test_joining_on_the_union_makes_one_sided_ids_fire(self):
        """The NEGATIVE control's mutation. A join that reaches too far turns
        every one-sided id into a phantom disagreement -- 245 of them on the
        live tree -- which is how a checker manufactures work."""
        mutant = _mutant("union_join",
                         "shared = sorted(set(inbox) & set(docket))",
                         "shared = sorted(set(inbox) | set(docket))")
        self._delta(mutant, {"probe_one_sided_does_not_fire"})

    def test_defanging_the_vocabulary_check_lets_queued_through(self):
        mutant = _mutant("vocab_off",
                         "            if status not in STATUSES:",
                         "            if status in ():")
        self._delta(mutant, {"probe_bad_vocabulary_fails"})

    def test_breaking_the_exit_contract_is_caught(self):
        """D64's own lesson twice over: a check whose exit code does not track
        its verdict is a printer, and a contract asserted on only one side of
        the map lets 25 of 25 FAILs read as out-of-contract."""
        mutant = _mutant("exit_contract_broken",
                         'EXIT = {PASS: 0, FAIL: 1, UNKNOWN: 3}',
                         'EXIT = {PASS: 0, FAIL: 0, UNKNOWN: 0}')
        self._delta(mutant, {"probe_exit_contract"})

    def test_an_unreadable_surface_downgraded_to_PASS_is_caught_by_the_cells(self):
        """S4. This mutation is outside `compare`, so it is proved against the
        cell that owns it rather than against the probe battery: the probes are
        pure and this defect lives in the I/O path."""
        mutant = _mutant("surface_error_passes",
                         "        return EXIT[UNKNOWN]\n",
                         "        return EXIT[PASS]\n")
        with tempfile.TemporaryDirectory() as tmp:
            agenda = Path(tmp) / "agenda"
            agenda.mkdir(parents=True)
            self.assertEqual(mutant.main(["--agenda", str(agenda)]), 0,
                             "the mutation did not model the defect")
            self.assertEqual(chk.main(["--agenda", str(agenda)]), 3,
                             "the control did not hold the line")


if __name__ == "__main__":
    unittest.main()
