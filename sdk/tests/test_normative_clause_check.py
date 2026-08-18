"""Tests for `scripts/check_normative_clauses.py` (docket D119).

Every assertion here is MUTATION-PROVEN: the mutation and its control were run
in ONE pytest invocation with `__pycache__` purged first, because stale bytecode
in this tree has INVERTED mutation results before (clean control failing, mutated
case passing) and `PYTHONDONTWRITEBYTECODE=1` does NOT fix it.

The mutations run, and what each proves:

  M1  `MANDATE`: `must\\b` -> `mustnot_a_word\\b`.  Kills
      test_controls_all_pass, test_fires_on_prerepair_clause_b,
      test_corpus_examines_a_nonzero_clause_count. Proves the mandate marker is
      load-bearing and not decorative.
  M2  `BIND` 18 -> 90.  Kills test_distance_alone_refuses_a_far_literal.
  M3  `_FILL` word-only -> `[^.]`.  Kills
      test_binding_refuses_the_four_measured_false_positives. M2 and M3 are
      separate on purpose: the first mutation round found M2 SURVIVING, because
      every corpus false positive happened to also cross punctuation and
      nothing pinned the distance on its own.
  M4  `decide`'s `if not examined` branch deleted.  Kills
      test_empty_set_is_unknown_not_pass. Proves defect class B1 is guarded.
  M5  `mask_exempt` replaced by identity.  Kills
      test_struck_clause_does_not_fire. Proves struck text really is exempt and
      the check is not passing that control by accident.
  M6  `_unit_ok` forced True.  Kills
      test_a_percentage_does_not_bind_to_an_absolute_quantity.
  M7  `THRESH_WORD` forced never to match.  Kills
      test_a_threshold_beside_the_quantity_name_is_not_a_claim. This mutant
      also survived its first round, against a threshold predicate anchored at
      `$`; the predicate is now unanchored and scanned on both sides of the
      literal, and the dead symbol forms were deleted rather than kept.
  M8  W1's designation pattern forced never to match.  Kills
      test_fires_on_prerepair_clause_b and test_controls_all_pass.

All eight are killed. Control ran clean immediately before and immediately
after the whole sequence, so no mutant left residue in the tree.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

import check_normative_clauses as N          # noqa: E402
from check_derived_figures import (          # noqa: E402
    mask_exempt, read_sources, build_registry,
)

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

GUIDELINES = str(lab_paths.web_file(
    "CLOSURE_FAMILY_SUPERVISION_GUIDELINES.md").relative_to(lab_paths.REPO))

#: The commit that struck clause (b). Its parent is the pre-repair state.
STRIKE_COMMIT = "5bec65f0"


def _in_commit(commit: str, path: str) -> str:
    """`path`'s spelling INSIDE `commit`, probed rather than assumed.

    MOVE_MAP batch 5, 2026-08-18.  `GUIDELINES` comes from
    `lab_paths.web_file()`, which answers *where the file is now* -- right for
    the live read at the bottom of this module and WRONG for a `git show` into
    an immutable commit, where the file is at whatever path that commit used.
    R16 moved this document to `research/closure/md/` and the positive control
    stopped being readable: `fatal: path ... exists on disk, but not in
    '5bec65f0^'`.  `lab_paths.unredirect()` is the inverse the history side
    needs; both directions are probed with `cat-file -e`, so a control commit
    written after a move is answered by the successor spelling instead.
    """
    for cand in (path, lab_paths.unredirect(path), lab_paths.redirect(path)):
        if not cand:
            continue
        p = subprocess.run(["git", "-C", str(REPO), "cat-file", "-e",
                            f"{commit}:{cand}"], capture_output=True, text=True)
        if p.returncode == 0:
            return cand
    return path


@pytest.fixture(scope="module")
def qs():
    quantities, problems, _ = build_registry(read_sources(REPO))
    assert not problems, f"source records unreadable: {problems}"
    return quantities


def _scan(text, qs, rel="<test>"):
    live, _ = mask_exempt(text)
    out = []
    N.scan(live, rel, qs, out)
    return out


# ---------------------------------------------------------------------------
# The controls the check runs on itself
# ---------------------------------------------------------------------------

def test_controls_all_pass(qs):
    """Both halves, L-84. A control list that never misfires is not a control."""
    bad, log = N.run_controls(qs)
    assert not bad, "\n".join(bad)
    assert len(log) == len(N.CONTROLS) >= 12
    assert sum(1 for _, want, *_ in N.CONTROLS if want) >= 5, "positives"
    assert sum(1 for _, want, *_ in N.CONTROLS if not want) >= 5, "negatives"


def test_control_misfire_forces_unknown_not_fail():
    v, why = N.decide(0, "", [], ["POS-1 did not fire"], 800, [])
    assert v == N.UNKNOWN
    assert "control misfired" in why[0]


# ---------------------------------------------------------------------------
# POSITIVE: it fires on the real defect, at its real pre-repair state
# ---------------------------------------------------------------------------

def test_fires_on_prerepair_clause_b(qs):
    """Clause (b) as it stood before `5bec65f0`, read from git, must fault.

    Not a paraphrase: the file content is fetched from the commit that struck
    it, so the test cannot drift away from the artifact it is about.
    """
    in_commit = _in_commit(STRIKE_COMMIT + "^", GUIDELINES)
    proc = subprocess.run(
        ["git", "-C", str(REPO), "show", f"{STRIKE_COMMIT}^:{in_commit}"],
        capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    found = _scan(proc.stdout, qs, GUIDELINES)
    w2 = [f for f in found if f.rule == "W2" and f.quantity == "live_margin"]
    assert w2, ("the pre-repair clause (b) must fault on the margin it pins; "
                f"got {[(f.rule, f.quantity, f.written) for f in found]}")
    assert any(f.written == "0.0029" and f.verdict == N.FAIL for f in w2)
    w1 = [f for f in found if f.rule == "W1"]
    assert w1, "'is the reference wording' must be reported as a mandated wording"


def test_check_derived_figures_cannot_see_that_same_clause():
    """The non-redundancy claim in the docstring, under test.

    Three of the four `live_margin` anchors in `check_derived_figures` require
    the word `Yang` and the fourth requires the possessive `our margin`. A
    clause pinning the SUPERSEDED margin can do neither -- Yang was not on the
    board it was computed against -- so `the 0.0029 rank-1 margin` is invisible
    to R1 by construction. If someone widens those anchors this test fails and
    this check's justification must be rewritten, which is the point of
    asserting it here rather than only claiming it in a docstring.
    """
    import check_derived_figures as C
    quantities, _, _ = C.build_registry(C.read_sources(REPO))
    margin = next(q for q in quantities if q.qid == "live_margin")
    assert all("Yang" in rx.pattern or "our margin" in rx.pattern
               for rx in margin.anchors)
    for probe in ("the 0.0029 rank-1 margin",
                  "comparable to the 0.0029 rank-1 margin, and the rank-1"):
        assert not any(rx.search(probe) for rx in margin.anchors), probe


def test_numberless_form_is_reachable(qs):
    """W3: the vector that survived five passes gets a verdict, not silence."""
    found = _scan(
        "- Rank 1 **may not** be stated without the seed-uncertainty bound,\n"
        "  which is comparable to its margin.\n", qs)
    w3 = [f for f in found if f.rule == "W3"]
    assert w3, "a mandated qualitative relation must be reported"
    assert w3[0].verdict == N.UNKNOWN, "it can only ever be UNDECIDABLE"
    assert "nothing to grade" in w3[0].why


# ---------------------------------------------------------------------------
# MUST-NOT-MATCH: the half that decides whether this is shippable
# ---------------------------------------------------------------------------

def test_repaired_clause_b_does_not_fire(qs):
    """The live guidelines file must be clean -- verified on the file itself."""
    found = _scan((REPO / GUIDELINES).read_text(encoding="utf-8"), qs,
                  GUIDELINES)
    bad = [f for f in found if f.verdict == N.FAIL]
    assert not bad, [(f.rule, f.line, f.written, f.why) for f in bad]


def test_procedural_mandate_does_not_fire(qs):
    """`must carry its board` is a good rule. It must never be a finding."""
    for text in (
        "- **No surface may state the figure without its BOARD** -- how many\n"
        "  entries, fetched when.\n",
        "- **A cap must state where it came from.**\n",
        "- No document in this package may quote the margin except as a\n"
        "  triple: the margin, the entrant it is over by name, and the board\n"
        "  by entrant count and retrieval date.\n",
        "- The gate **must** pass ratio <= 0.70 and r >= 0.85 before accept.\n",
    ):
        assert not _scan(text, qs), text


def test_struck_clause_does_not_fire(qs):
    """A struck clause is a historical record. Flagging it is worse than a miss."""
    pre = N.CLAUSE_B_PRE.replace("- ", "", 1).strip()
    assert _scan("- " + pre + "\n", qs), "control: unstruck, must fire"
    assert not _scan("- ~~" + pre + "~~\n", qs), "struck, must NOT fire"


def test_binding_refuses_the_four_measured_false_positives(qs):
    """The four corpus findings measured at a +-90 window, all four false.

    Each binds a literal to a quantity NAME across a punctuation boundary:
    Yang's overall to `our margin`, and a t-statistic to `the margin`. Held as
    a regression test because loosening the bind is the obvious "improvement"
    and it is the one that turns this into a 561-hit list.
    """
    for text in (
        "- The companion is **MANDATORY**: the board has six entries and a new\n"
        "  leader, Yang at 0.0580; our margin over Yang is elsewhere.\n",
        "- Every claim **must** carry it: Yang (t = -0.189, dispersion 15x the\n"
        "  margin, 4 of 8 cases won).\n",
        "- Every claim **must** carry it: Reissmann (t = -0.495, dispersion 5x\n"
        "  the margin, 4 of 8 won).\n",
        "- The row **must** stay: (Yang, 0.0580); our margin over Yang more\n"
        "  than halved.\n",
    ):
        found = [f for f in _scan(text, qs) if f.rule == "W2"]
        assert not found, (text, [(f.quantity, f.written) for f in found])


def test_distance_alone_refuses_a_far_literal(qs):
    """`BIND` is load-bearing independently of the punctuation restriction.

    Word-only filler, so `_FILL` admits it; too far, so `BIND` must not. This
    test exists because a first mutation round found `BIND` 18 -> 90 SURVIVED:
    every corpus false positive happened to also cross punctuation, so nothing
    pinned the distance on its own.
    """
    text = ("- The row **must** stay exactly as it is: 0.0024 was the figure "
            "recorded well before the margin ever moved at all.\n")
    found = [f for f in _scan(text, qs) if f.rule == "W2"]
    assert not found, [(f.quantity, f.written) for f in found]


def test_a_threshold_beside_the_quantity_name_is_not_a_claim(qs):
    """`the margin must be at least 0.0030` mandates a GATE, not a figure.

    Also from a surviving mutant: `THRESHOLD` never fired in any earlier test,
    because the only threshold fixture used quantities outside the registry.
    """
    for text in (
        "- Accept only if **must** holds: the margin at least 0.0030.\n",
        "- Every entry **must** ship: the seed bound under 0.0030.\n",
        "- Every entry **must** ship: 0.0030 caps the seed bound.\n",
    ):
        found = [f for f in _scan(text, qs) if f.rule == "W2"]
        assert not found, (text, [(f.quantity, f.written) for f in found])


def test_a_percentage_does_not_bind_to_an_absolute_quantity(qs):
    """A ratio stated as a percentage is not a mandated margin.

    The real sentence, from `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md:784`. It was
    this check's ONLY corpus finding at one point and it was false: `0.3%` was
    graded against an absolute margin of 0.001365. One false positive out of
    one finding is a 100% false-positive rate.
    """
    text = ("**A second pair that must not be smoothed together.** The two\n"
            "inputs differ by 9x10-6, about 0.3%\nof the margin.\n")
    found = [f for f in _scan(text, qs) if f.rule == "W2"]
    assert not found, [(f.quantity, f.written) for f in found]
    # ... and the converse: a percentage still binds to the percentage quantity
    assert [f for f in _scan(
        "- Every rank claim **must** state that the seed bound covers 84% of\n"
        "  the margin.\n", qs) if f.rule == "W2" and f.written == "84%"]


def test_a_correct_figure_with_its_full_triple_does_not_fire(qs):
    found = _scan(
        "- Every surface **must** state the seed bound as **0.002419**, i.e.\n"
        "  177% of the **0.001365** margin over **Yang** on the **six-entry**\n"
        "  board retrieved **2026-08-11T23:33Z**.\n", qs)
    assert not found, [(f.rule, f.quantity, f.written, f.verdict)
                       for f in found]


def test_a_commit_anchor_is_not_an_admissible_board(qs):
    """`deb91557` scores but does not rank, so it cannot satisfy the triple."""
    found = _scan(
        "- Every surface **must** state our margin as 0.001365 at the pinned\n"
        "  benchmark commit `deb91557`.\n", qs)
    assert found, "a commit anchor must not exempt a bare pinned margin"
    assert all(f.verdict == N.UNKNOWN for f in found)
    assert any("board triple" in f.why for f in found)


# ---------------------------------------------------------------------------
# The frame, and defect class B1
# ---------------------------------------------------------------------------

def test_empty_set_is_unknown_not_pass():
    """Zero clauses matched has never cleared anything (defect class B1)."""
    v, why = N.decide(0, "", [], [], 0, [])
    assert v == N.UNKNOWN
    assert "examined nothing" in why[0]
    assert "B1" in why[0]


# ---------------------------------------------------------------------------
# F1: the population LOOKED AT is not the population GRADED
# ---------------------------------------------------------------------------
#
# LADDER_V_V15_ROUND8 §2, reproduced at HEAD before the repair:
#
#     >>> N.decide(0, "", [], [], 887, [])
#     ('PASS', ['887 normative clause(s) examined; 0 pin a figure that agrees
#               with its record; 0 are UNDECIDABLE ...; none is graded false'])
#
# The B1 branch gated on `examined` -- the count of clauses a mandate marker was
# seen in -- and never on `findings`, the set that actually received a verdict.
# The shipped PASS rested on 0 of 887 decided. These tests gate on the decided
# set, and they name WHICH of the three empty arms each state is in, because
# "no clause matched" and "895 matched and none was gradeable" call for
# opposite repairs and an undifferentiated "empty" hides that.

def test_a_nonzero_examined_count_with_no_verdicts_is_unknown_not_pass():
    """THE F1 REGRESSION, verbatim. 887 examined, 0 decided, must not PASS."""
    v, why = N.decide(0, "", [], [], 887, [])
    assert v == N.UNKNOWN, f"F1 is back: {why}"
    assert why[0].startswith(N.EMPTY_NONE_GRADEABLE + ":"), why
    assert "887" in why[0] and "ZERO reached a verdict" in why[0]
    assert "B1" in why[0]


def test_a_compliant_clause_is_silent_in_the_report_but_counted_as_decided(qs):
    """The half of the repair that keeps this from becoming a useless alarm.

    NEG-6 pins that an obeyed mandate is NOT a finding -- reporting one trains
    readers to ignore the check. But it IS a decision, and if nothing counts it
    then a corpus in which every mandate is obeyed has an empty graded set and
    the B1 guard fires on a PERFECT corpus. `cleared` is that count.
    """
    text = ("- Every surface **must** state the seed bound as **0.002419**, "
            "i.e.\n  177% of the **0.001365** margin over **Yang** on the "
            "**six-entry**\n  board retrieved **2026-08-11T23:33Z**.\n")
    live, _ = mask_exempt(text)
    found, cleared = [], []
    examined = N.scan(live, "<t>", qs, found, cleared)
    assert examined == 1
    assert found == [], "an obeyed mandate was reported as a finding (NEG-6)"
    assert cleared, "an obeyed mandate was graded and then thrown away"
    assert all(c.verdict == N.PASS for c in cleared)
    assert N.empty_arm(examined, found, (), cleared) is None
    assert N.decide(0, "", [], [], examined, found, (), cleared)[0] == N.PASS


def test_a_perfect_corpus_passes_rather_than_going_unknown(tmp_path):
    """L-84's other half at the level of the whole instrument.

    A check that returns UNKNOWN once the corpus is clean has replaced false
    greens with an alarm nobody can switch off. Driven through `main`.
    """
    doc = tmp_path / "clean.md"
    doc.write_text(
        "- Every surface **must** state the seed bound as **0.002419**, i.e.\n"
        "  177% of the **0.001365** margin over **Yang** on the **six-entry**\n"
        "  board retrieved **2026-08-11T23:33Z**.\n", encoding="utf-8")
    code, out = _run_main([str(doc)])
    assert code == N.EXIT[N.PASS], out[-2500:]
    assert "1 decided" in out
    assert "of those, CLEARED 1" in out


def test_the_three_empty_arms_are_distinguished_by_name():
    """One UNKNOWN is three different states and the reason must say which."""
    assert N.empty_arm(0, []) == N.EMPTY_NO_CLAUSES
    assert N.empty_arm(887, []) == N.EMPTY_NONE_GRADEABLE
    assert N.empty_arm(887, [], ["x.md: [Errno 2]"]) == N.EMPTY_UNREADABLE
    assert N.empty_arm(0, [], ["x.md: [Errno 2]"]) == N.EMPTY_UNREADABLE
    arms = {N.decide(0, "", [], [], ex, [], un)[1][0].split(":")[0]
            for ex, un in ((0, ()), (887, ()), (887, ("x.md: boom",)))}
    assert arms == {N.EMPTY_NO_CLAUSES, N.EMPTY_NONE_GRADEABLE,
                    N.EMPTY_UNREADABLE}, arms


def test_an_unreadable_source_makes_an_empty_set_unattributable():
    v, why = N.decide(0, "", [], [], 0, [], ["a.md: [Errno 2] No such file"])
    assert v == N.UNKNOWN
    assert why[0].startswith(N.EMPTY_UNREADABLE + ":"), why
    assert "unattributable" in why[0]


def test_a_nonempty_decision_set_is_still_gradeable(qs):
    """MUST-NOT-MATCH, L-84's other half: this must not become an instrument
    that only ever returns UNKNOWN. One real finding is enough to decide."""
    found = _scan(
        "- Every surface **must** state our margin as 0.0029 on the live "
        "board.\n", qs)
    assert found, "fixture produced no finding; the control below is vacuous"
    assert N.decide(0, "", [], [], 895, found)[0] in (N.PASS, N.FAIL)
    assert N.empty_arm(895, found) is None


def test_a_false_clause_still_fails_over_a_nonempty_set(qs):
    fail = [f for f in _scan(N.CLAUSE_B_PRE, qs) if f.verdict == N.FAIL]
    assert fail, "fixture produced no FAIL finding"
    v, why = N.decide(0, "", [], [], 895, fail)
    assert v == N.FAIL, why


def test_an_undecidable_only_set_is_pass_and_the_frame_says_so(qs):
    """Recorded, not hidden: the live corpus decides 2 clauses and both are
    UNDECIDABLE, so today's PASS confirms nothing positively. That is inside
    the contract -- an UNDECIDABLE is a verdict, so the set is not empty -- but
    the count of TRUE findings is printed beside it precisely so a reader can
    see what the PASS rests on."""
    undec = [f for f in _scan(
        "- Every surface **must** state our margin as 0.001365 at the pinned\n"
        "  benchmark commit `deb91557`.\n", qs) if f.verdict == N.UNKNOWN]
    assert undec
    v, why = N.decide(0, "", [], [], 895, undec)
    assert v == N.PASS
    assert f"{len(undec)} decided" in why[0]
    assert "0 pin a figure that agrees" in why[0]


# ---------------------------------------------------------------------------
# The SHIPPED ENTRY POINT, driven -- not a re-derivation beside it
# ---------------------------------------------------------------------------
#
# `decide` being right is not the same claim as `main` calling it with the
# right arguments. The `unreadable` list is assembled in `main` and nowhere
# else, so an arm that is correct in `decide` and never reached from `main` is
# the M1 shape on this module. These call `N.main()`.

def _run_main(files, *, err="", rc=0, argv=()):
    """Run `N.main()` over an injected corpus. Patches only its SOURCES."""
    import contextlib
    import io
    from unittest import mock

    args = ["check_normative_clauses", "--root", str(REPO), *argv]
    buf = io.StringIO()
    with mock.patch.object(sys, "argv", args), \
         mock.patch.object(N, "tracked_prose",
                           lambda root: (list(files), err, rc)):
        with contextlib.redirect_stdout(buf):
            code = N.main()
    return code, buf.getvalue()


def _verdict_block(out):
    """Only the text BELOW `VERDICT:`.

    Asserting over the whole report is how a test goes vacuous here: the frame
    names the arm too, so `EMPTY-3 in out` stayed true under a mutant in which
    `main` stopped passing `unreadable` to `decide` and the verdict fell back to
    EMPTY-1. Measured -- that mutant SURVIVED the first cut of this test.
    """
    return out.split("VERDICT:", 1)[1]


def test_main_refuses_to_pass_over_a_corpus_of_no_files(tmp_path):
    code, out = _run_main([])
    assert code == N.EXIT[N.UNKNOWN], out[-2000:]
    assert "VERDICT: UNKNOWN" in out
    assert N.EMPTY_NO_CLAUSES in _verdict_block(out)


def test_main_refuses_to_pass_when_the_only_source_is_unreadable(tmp_path):
    """The `unreadable` wiring, which exists only inside `main`."""
    code, out = _run_main([str(tmp_path / "never-written.md")])
    assert code == N.EXIT[N.UNKNOWN], out[-2000:]
    tail = _verdict_block(out)
    assert N.EMPTY_UNREADABLE in tail, tail
    assert "1 source(s) could not be read" in tail
    assert "sources unread      1" in out


def test_main_prints_the_same_arm_in_the_frame_and_in_the_verdict(tmp_path):
    """One sentence, two places. A frame that names EMPTY-3 above a verdict
    that took EMPTY-1 is worse than printing neither."""
    code, out = _run_main([str(tmp_path / "never-written.md")])
    frame = out.split("empty-set arm", 1)[1].split("\n", 1)[0].strip()
    assert frame == N.empty_reason(N.EMPTY_UNREADABLE, 0,
                                   ["never-written.md: x"]), frame
    assert frame in _verdict_block(out)


def test_main_prints_the_decided_count_beside_the_examined_count(tmp_path):
    """The frame must carry both numbers. F1 was invisible because only the
    number that could not clear anything was printed."""
    doc = tmp_path / "fixture.md"
    doc.write_text(
        "- Every surface **must** state our margin as 0.001365 at the pinned\n"
        "  benchmark commit `deb91557`.\n", encoding="utf-8")
    code, out = _run_main([str(doc)])
    assert "clauses examined" in out and "clauses DECIDED" in out
    assert code in (N.EXIT[N.PASS], N.EXIT[N.FAIL]), out[-2000:]
    assert "empty-set arm       (none)" in out


def test_main_still_fails_on_a_genuine_violation(tmp_path):
    """MUST-NOT-MATCH control on the runner: FAIL is still reachable."""
    doc = tmp_path / "fixture.md"
    doc.write_text(N.CLAUSE_B_PRE, encoding="utf-8")
    code, out = _run_main([str(doc)])
    assert code == N.EXIT[N.FAIL], out[-2000:]
    assert "VERDICT: FAIL" in out


def test_main_reports_a_broken_frame_as_unknown(tmp_path):
    code, out = _run_main([], err="fatal: not a git repository", rc=128)
    assert code == N.EXIT[N.UNKNOWN], out[-2000:]
    assert "not a git repository" in out


def test_broken_frame_is_unknown_not_empty():
    v, why = N.decide(128, "fatal: not a git repository", [], [], 0, [])
    assert v == N.UNKNOWN
    assert "not a git repository" in why[0]


def test_unreadable_source_record_is_unknown():
    v, why = N.decide(0, "", ["seed json unreadable"], [], 800, [])
    assert v == N.UNKNOWN
    assert "source record problem" in why[0]


def test_corpus_examines_a_nonzero_clause_count(qs):
    """The real corpus, through the real frame. A zero here would be UNKNOWN."""
    files, err, rc = N.tracked_prose(REPO)
    assert rc == 0, err
    assert len(files) > 300
    total = 0
    for rel in files[:120]:
        if N.GENERATED_HTML.search(rel):
            continue
        try:
            raw = (REPO / rel).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        live, _ = mask_exempt(raw)
        total += N.scan(live, rel, qs, [])
    assert total > 50, total


# ---------------------------------------------------------------------------
# Guards found by ENUMERATION rather than by asking what the tests cover
# ---------------------------------------------------------------------------
#
# Every branch in this module that changes a finding, a count printed in the
# frame, or a verdict was enumerated and mutated, 2026-08-15. The ones below
# each SURVIVED and are pinned here. None of them was a false green -- they
# change a REASON or a printed FRAME COUNT, not a PASS -- which is exactly why
# nothing noticed: a check whose verdict is right and whose stated reason is
# wrong reads as working, and the reason is what an operator acts on.
#
# One recorded non-finding, so the census can be audited: mutating
# `unreadable.append(...)` to `opened.append(rel) or unreadable.append(...)`
# reported a SURVIVOR, and it is not one -- `list.append` returns None, so the
# `or` still evaluated the original call and the mutant was a no-op. Deleting
# the line outright kills two tests. A harness that asserts its site occurs
# once cannot tell a mutation from a no-op; only the KILLED result can.

def test_a_pointer_designation_and_an_inline_one_get_different_reasons(qs):
    """W1's discriminator. Both arms are UNDECIDABLE, so the verdict cannot
    tell them apart and only the reason can -- and the two call for opposite
    actions: chase the pointer, or read the sentence that is already here."""
    pointer = _scan(
        "- Every surface **must** copy it: `closure.html`'s stability note is\n"
        "  the reference wording.\n", qs)
    assert pointer and all(f.verdict == N.UNKNOWN for f in pointer)
    assert any("POINTER" in f.why for f in pointer if f.rule == "W1"), \
        [(f.rule, f.why[:60]) for f in pointer]
    inline = _scan(
        "- Every surface **must** use the wording to copy, and it is fixed "
        "right here.\n", qs)
    w1 = [f for f in inline if f.rule == "W1"]
    assert w1, "a designated wording with no pointer must still be reported"
    assert not any("POINTER" in f.why for f in w1), \
        "an inline designation was reported as a cross-document pointer"


def test_w3_does_not_double_report_a_clause_w2_already_graded(qs):
    """A qualitative relation that ALSO carries a literal is W2's, not W3's.

    Without the deferral the same clause is reported twice under two rules,
    which inflates the UNDECIDABLE count a reader acts on. The verdict does not
    move, so nothing else would notice.
    """
    both = ("- Every surface **must** state the seed bound as 0.0024, which is\n"
            "  comparable to the margin.\n")
    found = _scan(both, qs)
    assert found, "fixture produced no finding at all"
    assert not [f for f in found if f.rule == "W3"], \
        [(f.rule, f.quantity) for f in found]
    # Control: strip the literal and W3 is exactly what must fire.
    only_qual = ("- Every surface **must** state a seed bound comparable to "
                 "the margin.\n")
    assert [f for f in _scan(only_qual, qs) if f.rule == "W3"]


def test_generated_report_html_is_excluded_and_counted_not_silently_skipped(
        tmp_path):
    """53 of 57 tracked HTML files are DAFoam OpenMDAO reports carrying
    minified d3 and no prose. Reading them is not wrong so much as unbounded --
    but a skip that is not COUNTED is a silent skip, which is the defect class
    the frame block exists to close."""
    rep = tmp_path / "reports"
    rep.mkdir()
    doc = rep / "opt_report.html"
    doc.write_text("<p>the gate **must** hold at 0.0029 margin</p>\n",
                   encoding="utf-8")
    assert N.GENERATED_HTML.search(str(doc)), "fixture does not match the rule"
    code, out = _run_main([str(doc)])
    assert "files opened        0" in out, out[:1500]
    assert "1 generated OpenMDAO report HTML" in out
    assert code == N.EXIT[N.UNKNOWN], "an all-excluded corpus must not PASS"


def test_an_oversize_file_is_excluded_and_named_in_the_frame(tmp_path):
    doc = tmp_path / "huge.md"
    doc.write_text("x" * (N.MAX_BYTES + 1), encoding="utf-8")
    code, out = _run_main([str(doc)])
    assert "files opened        0" in out, out[:1500]
    assert "oversize        " in out, "an excluded file was not named"
    assert code == N.EXIT[N.UNKNOWN]
    # Control: the same file one byte under the cap IS opened.
    small = tmp_path / "small.md"
    small.write_text("x" * (N.MAX_BYTES - 1), encoding="utf-8")
    _, out2 = _run_main([str(small)])
    assert "files opened        1" in out2


def test_exit_contract_matches_the_runner():
    assert N.EXIT == {"PASS": 0, "FAIL": 1, "UNKNOWN": 3}


def test_it_writes_nothing(qs):
    """`lab_check` skips writers. Assert the source carries no write primitive."""
    src = (REPO / "scripts" / "check_normative_clauses.py").read_text()
    for bad in ("write_text(", "write_bytes(", ".mkdir(", "shutil.copy",
                "os.remove", "os.rename", "unlink("):
        assert bad not in src, bad
    assert not re.search(r"\bopen\([^)]*['\"][wax]", src)
