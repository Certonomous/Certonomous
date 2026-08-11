"""GRADE ROUND 5 (independent, worktree-isolated) -- the probes that broke E2
and E4, committed so the finding is executable rather than readable.

WHY THIS FILE EXISTS. R-ISOLATE part 3: a grader never reads the author's
summary of a claim, it executes the claim. This round executed the five
declared V16 items and two of them failed on sentences constructed here. A
finding stated in prose is a finding a later round has to re-derive, so the
sentences live in the repository with their expected and actual verdicts, and
`main` recomputes both against the live guard.

THE ORDINALS, POSITION WORDS AND THE `rank` TOKENS ARE ASSEMBLED AT IMPORT,
under the convention `sdk/tests/test_rank_claim_surfaces.py` states: a tracked
file that spells a wrong placement in full IS a file of real faults, and rule B
has no adjudication clause that could clear them. The sentences under test are
exactly the defects; this source file contains none. Verified at commit time by
running `check_board_placement_words` over the tree with this file in it -- the
count did not move.

FRAME. Board read from the benchmark README at deb91557 -- Reissmann 1, Wu 2,
Liu 3, Montoya 4. Guard at self_audit.py, repo HEAD 1393b8b4. Zero of these
shapes occur in the tracked corpus today (swept over `git ls-files`, files read
in Python, UTF-8, <= 4 MB): the defects are LATENT, not live, and no published
figure moves. What they falsify is a written claim about the guard.
"""
from __future__ import annotations

# Split so this source carries no placement the guard can match.
_RK = "ra" + "nk"
_D = {1: "1", 2: "2", 3: "3", 4: "4"}
_S = {2: "2" + "nd", 4: "4" + "th"}
_O = {4: "four" + "th"}
_OU = {4: "Four" + "th"}


def _s(t: str) -> str:
    return t.format(RK=_RK, D1=_D[1], D2=_D[2], D3=_D[3], D4=_D[4],
                    S2=_S[2], S4=_S[4], O4=_O[4], OU4=_OU[4])


# (label, template, what the guard SHOULD do, what it DOES at 1393b8b4)
#
# E2 -- the linear-algebra homonym discriminator is "nearest wins, left-hand
# only". Nearest-token proximity is a PROXY for the grammatical subject, and the
# ordinary genitive/prepositional construction inverts the proxy: put an
# entrant's genitive BETWEEN the linear-algebra noun and the ordinal, and the
# surname sits NEARER the ordinal than the noun does, so the guard votes
# ENTRANT on a sentence whose grammatical subject is a tensor. This lab's four
# entrants are turbulence authors, so that construction is the ordinary
# phrasing here, not the exotic one. The sentence itself is in `_E2_RAW` below,
# assembled -- writing it out HERE is the defect this file is about, and this
# comment carried it until the live guard was run over the file by hand.
_E2_RAW = [
    ("E2 FP genitive after the noun",
     "The Reynolds stress tensor in Liu's closure is {RK} {D2} at every cell.",
     "silent", "FAULT"),
    ("E2 FP agent phrase",
     "The velocity gradient used by Liu is {RK} {D2} pointwise across the duct.",
     "silent", "FAULT"),
    ("E2 FP relative clause",
     "The anisotropy tensor that Montoya fits is {RK} {D2} almost everywhere.",
     "silent", "FAULT"),
    ("E2 FP of-phrase",
     "In the integrity basis the strain-rate invariant of Wu is {RK} {D3} here.",
     "silent", "FAULT"),
    # The mirror. Declared by the rule, but it is the half the author's own
    # comment calls the silent one, and it mutes a real wrong placement.
    ("E2 FN noun nearer in a subordinate clause",
     "Liu and Montoya, whose Reynolds stress tensor closure won the duct case, "
     "are {RK} {D2} on the board.",
     "FAULT", "silent"),
    ("E2 FN apposition",
     "Montoya, who rebuilt the anisotropy tensor from the strain invariant, "
     "is {RK} {D2} overall.",
     "FAULT", "silent"),
    # Controls: the discriminator must still work on the plain cases, or the
    # findings above are just a wedged guard.
    ("E2 control plain placement",
     "Liu and Wu are {RK} {D1} on the board.", "FAULT", "FAULT"),
    ("E2 control plain linear algebra",
     "The Reynolds stress is a {RK} {D2} tensor in three dimensions.",
     "silent", "silent"),
    ("E2 control correct placement",
     "Liu is {RK} {D3} on the published board.", "silent", "silent"),
]

# E4 -- the sentence-boundary bind. The repair made the probe SYMMETRIC: each
# side appends one character of what follows the gap. That is true, and it is
# not the invariant that matters. `_PLACE_SENTENCE` closes a boundary only on
# `[.!?] .. \s .. [A-Z("'*`]`, so the appended character closes it only when it
# is an UPPERCASE letter -- and neither side's appended character is reliably
# one. LEFT appends the ORDINAL token's first character, which is a digit in
# every `Nth place` form and lowercase in a sentence-initial `rank N`. RIGHT
# appends the MATCHED NAME's first character, and surnames match
# case-insensitively, so a lowercase citation form defeats it. The failure axis
# is the character class, not the side.
_E4_RAW = [
    ("E4 FP left, digit-form ordinal opens the sentence",
     "Liu ran the duct case. {S4} place is still open.", "silent", "FAULT"),
    ("E4 FP left, digit-form ordinal (2nd)",
     "Montoya closed the hump case. {S2} place is still open.",
     "silent", "FAULT"),
    ("E4 FP left, acknowledgement then a result",
     "We thank Reissmann for the baseline. {S2} place was decided on the duct.",
     "silent", "FAULT"),
    ("E4 FP left, lowercase sentence-initial rank",
     "Liu ran the duct case. {RK} {D4} is still open.", "silent", "FAULT"),
    ("E4 FP right, lowercase citation form of the surname",
     "They are at {RK} {D4}. liu et al. ran SST-QCRC.", "silent", "FAULT"),
    # And the word form is not safe either, which is what makes the axis the
    # CHARACTER CLASS rather than the digit/word distinction: a lowercase
    # sentence-initial `fourth place` -- the form a markdown bullet, a log line
    # or a lowercased heading produces -- fails for the identical reason. This
    # entry was written as a control and the probe file's own regression check
    # reclassified it, which is the argument for committing probes rather than
    # prose.
    ("E4 FP left, lowercase word-form ordinal",
     "Liu ran the duct case. {O4} place is still open.", "silent", "FAULT"),
    # Controls: the cases the author tested, which do hold -- and the over-fix
    # controls, which show the guard has not simply stopped binding after a stop.
    ("E4 control left, capitalised word-form ordinal",
     "Liu ran the duct case. {OU4} place is still open.", "silent", "silent"),
    ("E4 control left, capitalised rank token",
     "Liu ran the duct case. Rank {D4} is still open.", "silent", "silent"),
    ("E4 control right, capitalised surname",
     "They are at {RK} {D4}. Liu et al. ran SST-QCRC.", "silent", "silent"),
    ("E4 control still binds with no boundary",
     "Liu is at {RK} {D4} in the standings.", "FAULT", "FAULT"),
    ("E4 control still binds in the sentence after a stop",
     "The duct case closed. Liu is at {RK} {D4} in the standings.",
     "FAULT", "FAULT"),
]

#: (label, sentence, expected, observed-at-1393b8b4)
E2 = [(lab, _s(t), exp, obs) for lab, t, exp, obs in _E2_RAW]
E4 = [(lab, _s(t), exp, obs) for lab, t, exp, obs in _E4_RAW]

assert len(E2) == 9, len(E2)
assert len(E4) == 11, len(E4)


def measure(board, faults):
    """{label: (expected, observed_now)} against a board and a fault function."""
    out = {}
    for lab, sentence, expected, _recorded in E2 + E4:
        out[lab] = (expected,
                    "FAULT" if faults(sentence, board)[0] else "silent")
    return out


def regressions(board, faults):
    """Labels whose CURRENT behaviour differs from what this round recorded."""
    drift = []
    for lab, sentence, _expected, recorded in E2 + E4:
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
        print(f"{'OK ' if ok else '!! '}{lab:<52} want={expected:<7} got={now}")
    print(f"\n{bad} of {len(E2) + len(E4)} probes disagree with what the guard "
          f"ought to do.")
    drift = regressions(board, sa.board_placement_faults)
    if drift:
        print("\nDRIFT from what grade round 5 recorded at 1393b8b4:")
        for lab, was, now in drift:
            print(f"  {lab}: recorded {was}, now {now}")
    else:
        print("No drift from what grade round 5 recorded at 1393b8b4.")
