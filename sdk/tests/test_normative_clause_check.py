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

GUIDELINES = "demo-output/website/CLOSURE_FAMILY_SUPERVISION_GUIDELINES.md"

#: The commit that struck clause (b). Its parent is the pre-repair state.
STRIKE_COMMIT = "5bec65f0"


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
    proc = subprocess.run(
        ["git", "-C", str(REPO), "show", f"{STRIKE_COMMIT}^:{GUIDELINES}"],
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


def test_exit_contract_matches_the_runner():
    assert N.EXIT == {"PASS": 0, "FAIL": 1, "UNKNOWN": 3}


def test_it_writes_nothing(qs):
    """`lab_check` skips writers. Assert the source carries no write primitive."""
    src = (REPO / "scripts" / "check_normative_clauses.py").read_text()
    for bad in ("write_text(", "write_bytes(", ".mkdir(", "shutil.copy",
                "os.remove", "os.rename", "unlink("):
        assert bad not in src, bad
    assert not re.search(r"\bopen\([^)]*['\"][wax]", src)
