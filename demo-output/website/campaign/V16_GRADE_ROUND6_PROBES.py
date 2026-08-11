"""GRADE ROUND 6 -- the probes that keep E2 open and the ones the round-6
repairs broke, committed so the finding is executable rather than readable.

WHY THIS FILE EXISTS. Round 5 committed its probes and the round-6 author then
wired them into `sdk/tests/test_rank_claim_surfaces.py`, where they now recompute
on every run. That worked: this round reproduced all twenty of them mechanically
before touching anything. Prose would have had to be re-derived. So the round-6
findings ship the same way.

THE ORDINALS, POSITION WORDS AND THE `ra`+`nk` TOKENS ARE ASSEMBLED AT IMPORT,
under the convention `sdk/tests/test_rank_claim_surfaces.py` states and docket D4
names: a tracked file that spells a wrong placement in full IS a file of real
faults, and rule B has no adjudication clause that could clear them. The
sentences under test are exactly the defects; this source file contains none,
and neither does the prose about them -- no shape below is written out in a
comment. Verified at commit time by running the live guard over this file, with
a positive control showing the run can find a fault when one is present.

FRAME. Board read from the benchmark README pin -- Reissmann 1, Wu 2, Liu 3,
Montoya 4. Guard at `scripts/self_audit.py`, repo HEAD 72609a04 (the graded
subject; `git merge-base --is-ancestor` OK and the three-path content diff
against HEAD empty). `old` below means 1393b8b4, the build round 5 graded.
"""
from __future__ import annotations

# Split so this source carries no placement the guard can match.
_RK = "ra" + "nk"
_D = {1: "1", 2: "2", 3: "3", 4: "4"}
_S = {2: "2" + "nd", 4: "4" + "th"}
_P = "pl" + "ace"


def _s(t: str) -> str:
    return t.format(RK=_RK, D1=_D[1], D2=_D[2], D3=_D[3], D4=_D[4],
                    S2=_S[2], S4=_S[4], P=_P)


# (label, template, what the guard SHOULD do, what it DOES at 72609a04)
#
# E2 -- the subject-head discriminator. The rule the guard states is THE HEAD OF
# THE GRAMMATICAL SUBJECT; the implementation finds that head by cutting the
# clause at the first `_PLACE_POSTMOD` marker with a candidate noun in front of
# it, and by taking the LATER of the two candidate nouns when no cut is made.
# Both halves have edges, and every shape below crosses one in the FALSE FAULT
# direction -- the expensive one, since a rule-A fault on a travelling surface
# is FAIL severity.
#
#   (a) the marker list is a word list, and English drops the relativizer in an
#       object relative clause. Remove that one word from a shape the round-6
#       repair fixed and no cut is made at all; the later-noun tie-break then
#       resolves to the entrant, who follows the head.
#   (b) `_PLACE_LINALG_NEAR` is also a word list. A subject headed by a linear-
#       algebra object whose noun is not ON that list cuts correctly and then
#       finds no object at all, so the discriminator declines to mute.
#   (c) coordination. The author's comment declares (b) and (c) as two of three
#       known blind spots and states that NONE of them produces a false FAULT.
#       Executed, (b) and (c) both do.
_E2_RAW = [
    ("E2 reduced relative, relativizer dropped",
     "The anisotropy tensor Liu fits is {RK} {D2} almost everywhere.",
     "silent", "FAULT"),
    ("E2 reduced relative, past participle",
     "The Reynolds stress tensor Montoya published is {RK} {D2} at every cell.",
     "silent", "FAULT"),
    ("E2 reduced relative, present tense",
     "The velocity gradient Wu reports is {RK} {D3} pointwise.",
     "silent", "FAULT"),
    ("E2 head noun off the word list (kernel)",
     "The covariance kernel that Liu fits is {RK} {D2} pointwise.",
     "silent", "FAULT"),
    ("E2 head noun off the word list (Gramian)",
     "The Gramian that Liu fits is {RK} {D2} pointwise.",
     "silent", "FAULT"),
    ("E2 head noun off the word list (Laplacian)",
     "The graph Laplacian that Liu fits is {RK} {D2} pointwise.",
     "silent", "FAULT"),
    ("E2 coordinated subject, both conjuncts objects",
     "The Reynolds stress tensor and Liu's closure are {RK} {D2} at every cell.",
     "silent", "FAULT"),
    # Controls. The discriminator must still do the job it was repaired to do,
    # or the shapes above are just a wedged guard.
    ("E2 control relativizer present (round-6 repair holds)",
     "The anisotropy tensor that Liu fits is {RK} {D2} almost everywhere.",
     "silent", "silent"),
    ("E2 control head noun ON the word list",
     "The Koopman operator that Liu fits is {RK} {D2} pointwise.",
     "silent", "silent"),
    ("E2 control fronted modifier still skipped",
     "In the duct case the anisotropy tensor of Liu is {RK} {D2} everywhere.",
     "silent", "silent"),
    ("E2 control plain wrong placement",
     "Liu and Wu are {RK} {D1} on the board.", "FAULT", "FAULT"),
    ("E2 control plain linear algebra",
     "The Reynolds stress is a {RK} {D2} tensor in three dimensions.",
     "silent", "silent"),
    ("E2 control correct placement",
     "Liu is {RK} {D3} on the published board.", "silent", "silent"),
]

# THE SUBJECT-NP FALLBACK, added this round so that an ordinal predicated by a
# copula still binds when the subject sits beyond `_PLACE_BIND`. Its comment
# states that it CANNOT reach across a sentence, because the phrase is cut at
# `_PLACE_CLAUSE` first. `_PLACE_CLAUSE` is `[.!?;:]`, and the whitespace of the
# surface is collapsed before any of this runs -- so what the fallback cannot
# cross is a PUNCTUATION MARK, not a sentence. A markdown heading, a list item
# and a table cell all end without one, and this corpus is markdown. Each shape
# below binds an ordinal to an entrant named in the PREVIOUS structural unit.
# These are regressions: `old` is silent on all three, because `old` has no
# fallback. Gaps are 65, 69 and 54 characters against a `_PLACE_BIND` of 40, so
# the ordinary bind cannot be what fires.
_FB_RAW = [
    ("FB across a markdown heading",
     "## Liu wins the duct case study\n\nThe entrant we must beat overall is "
     "{RK} {D2} today.", "silent", "FAULT"),
    ("FB across a list-item boundary",
     "- Liu ran the duct case on a coarse mesh\n- The entrant to beat here is "
     "{RK} {D2}\n", "silent", "FAULT"),
    ("FB across a table cell boundary",
     "| Liu | duct case, coarse mesh | the entrant to beat is {RK} {D2} |",
     "silent", "FAULT"),
    # Controls. The author's stated boundary does hold where the punctuation is
    # present, and the fallback must still catch the two shapes it was added for
    # -- otherwise the finding is just a demand to delete it.
    ("FB control same gap, full stop present",
     "Liu wins the duct case study.\n\nThe entrant we must beat overall is "
     "{RK} {D2} today.", "silent", "silent"),
    ("FB control same gap, semicolon present",
     "Liu ran the duct case on the coarse mesh; the front-runner is {RK} {D2}.",
     "silent", "silent"),
    ("FB control round-5 FN, apposition",
     "Montoya, who rebuilt the anisotropy tensor from the strain invariant, "
     "is {RK} {D2} overall.", "FAULT", "FAULT"),
    ("FB control round-5 FN, subordinate clause",
     "Liu and Montoya, whose Reynolds stress tensor closure won the duct case, "
     "are {RK} {D2} on the board.", "FAULT", "FAULT"),
]

# E4 -- the boundary probe now appends a CONSTANT standing for "a new token
# starts here" instead of the real next character. The six shapes round 5 found
# are fixed and both over-fix controls hold; those twenty probes live in
# `V16_GRADE_ROUND5_PROBES.py` and are wired into the suite. What the constant
# also does, because it is unconditionally uppercase, is close the boundary
# after EVERY full stop plus space -- including the one that ends an
# abbreviation rather than a sentence. `old` bound both shapes below and
# faulted them; the subject is silent on both. The direction is the cheap one
# (a missed fault, not a false one), and the trade is not named in the comment
# that makes it: it says the character's identity "was never doing any work",
# and on this class it was.
_E4_RAW = [
    ("E4 over-fix, abbreviation then a bare ordinal",
     "Wu et al. {RK} {D4} overall on the duct case.", "FAULT", "silent"),
    ("E4 over-fix, abbreviation then an ordinal-plus-noun",
     "Wu et al. {S4} {P} overall on the duct.", "FAULT", "silent"),
    ("E4 control still binds with no boundary",
     "Liu is at {RK} {D4} in the standings.", "FAULT", "FAULT"),
    ("E4 control still binds in the sentence after a stop",
     "The duct case closed. Liu is at {RK} {D4} in the standings.",
     "FAULT", "FAULT"),
]

#: (label, sentence, expected, observed-at-72609a04)
E2 = [(lab, _s(t), exp, obs) for lab, t, exp, obs in _E2_RAW]
FB = [(lab, _s(t), exp, obs) for lab, t, exp, obs in _FB_RAW]
E4 = [(lab, _s(t), exp, obs) for lab, t, exp, obs in _E4_RAW]
ALL = E2 + FB + E4

assert len(E2) == 13, len(E2)
assert len(FB) == 7, len(FB)
assert len(E4) == 4, len(E4)


def measure(board, faults):
    """{label: (expected, observed_now)} against a board and a fault function."""
    return {lab: (expected, "FAULT" if faults(sentence, board)[0] else "silent")
            for lab, sentence, expected, _recorded in ALL}


def regressions(board, faults):
    """Labels whose CURRENT behaviour differs from what this round recorded."""
    drift = []
    for lab, sentence, _expected, recorded in ALL:
        now = "FAULT" if faults(sentence, board)[0] else "silent"
        if now != recorded:
            drift.append((lab, recorded, now))
    return drift


if __name__ == "__main__":                                     # pragma: no cover
    import importlib.util
    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parents[3]
    spec = importlib.util.spec_from_file_location(
        "sa", root / "scripts" / "self_audit.py")
    sa = importlib.util.module_from_spec(spec)
    sys.modules["sa"] = sa
    spec.loader.exec_module(sa)
    board, why = sa._published_board()
    if board is None:
        raise SystemExit(f"detector OFF, not a silent pass: {why}")
    bad = 0
    for lab, (expected, now) in measure(board, sa.board_placement_faults).items():
        ok = expected == now
        bad += not ok
        print(f"{'OK ' if ok else '!! '}{lab:<56} want={expected:<7} got={now}")
    print(f"\n{bad} of {len(ALL)} probes disagree with what the guard ought to do.")
    drift = regressions(board, sa.board_placement_faults)
    if drift:
        print("\nDRIFT from what grade round 6 recorded at 72609a04:")
        for lab, was, now in drift:
            print(f"  {lab}: recorded {was}, now {now}")
    else:
        print("No drift from what grade round 6 recorded at 72609a04.")
