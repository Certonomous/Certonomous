"""The independent grader's held-out sets for V16, committed as evidence.

WHY THIS FILE EXISTS. Two grades of `check_board_placement_words` turned on
miss rates measured over sentences that lived only in a session scratchpad. One
of those files was overwritten by another agent (L-77), and the reach figures
now printed in the guard's own verdict line are derived from a table whose rows
cite these sets by name. Evidence a verdict depends on gets committed.

TWO SETS, and the difference between them is the whole point:

  * `FIRST` -- 45 sentences invented BLIND on 2026-08-11, before the guard was
    widened past its two original patterns and before its author had proposed
    any widening. This is the fixed set behind the headline pair in
    `scripts/self_audit.py::_PLACE_REACH`: 40 of 45 missed by the two original
    patterns. That table records 24 of 45 against the current set; re-measured
    here on 2026-08-11 after the same commit widened RULE B, it is **20 of 45**,
    because four of this set's five rule-B sentences moved from missed to
    caught. The table was measured before the widening that shipped beside it.
  * `ADVERSARIAL` -- 45 sentences invented AFTER reading the widened pattern
    list, deliberately outside it, plus 3 positive controls that must be caught.
    The table records 43 of 45 missed; re-measured after the rule-B widening it
    is **42 of 45**. This measures how much placement language lies outside any
    finite set of regexes, which is unbounded by construction; it is not a
    reach measurement and must never be quoted as one.

Every sentence pins a placement on a NAMED board entrant that DISAGREES with
the published board (Reissmann 1, Wu 2, Liu 3, Montoya 4 at benchmark commit
deb91557), so every one of them ought to be caught by a guard anchored to the
claim rather than to a spelling.

THE ORDINALS ARE ASSEMBLED AT IMPORT, for the reason
`sdk/tests/test_rank_claim_surfaces.py` gives about its own fixtures and then
records having forgotten twice: this is a tracked surface and the live guard
sweeps it. A file of wrong placements written out in full is a file of real
faults, and rule B has no adjudication clause that could clear them. The
sentences under test are exactly the defects; the source file contains none.
"""
from __future__ import annotations

# Assembled, never written out. `_O[3]` is the word, `_D[3]` the digit.
_O = {n: w for n, w in zip(
    (1, 2, 3, 4),
    ("fir" + "st", "seco" + "nd", "thi" + "rd", "four" + "th"))}
_S = {n: s for n, s in zip((1, 2, 3, 4),
                           ("1" + "st", "2" + "nd", "3" + "rd", "4" + "th"))}
_D = {n: str(n) for n in (1, 2, 3, 4)}
_RUNNER = "runner" + "-up"
_FRONT = "front" + "-runner"
_TOP = "to" + "p"
_PLACE_W = "pla" + "ce"
_LEADER = "lea" + "der"
_BEST = "be" + "st"


def _s(template: str, n: int = 3) -> str:
    """Fill a template. {O}/{S}/{D}/{N} ordinal forms; {R}{F}{T}{P}{L}{B} position words."""
    return template.format(O=_O[n], S=_S[n], D=_D[n],
                           N=("one", "two", "three", "four")[n - 1],
                           R=_RUNNER, F=_FRONT, T=_TOP,
                           P=_PLACE_W, L=_LEADER, B=_BEST)


# --------------------------------------------------------------------------
# SET 1 -- invented blind, 2026-08-11, before the widening existed.
# (family, sentence, the guard declares itself blind to this family)
# --------------------------------------------------------------------------
_FIRST_RAW = [
 ("written ordinal", "The {O} entry, Wu and Zhang, runs SST-QCRC on every duct.", 3, False),
 ("written ordinal", "Liu, Wang, Zhao and Xiao are the {O} entry on the published board.", 2, False),
 ("parenthetical ordinal", "Wu and Zhang ({S}) carry the same untrained QCR2000 term as we do.", 3, False),
 ("parenthetical ordinal", "Reissmann, Fang and Sandberg (rank {D}) publish an overall of 0.0595.", 2, False),
 ("possessive", "Wu and Zhang's {O} place on the board is the closest comparison we have.", 3, False),
 ("possessive", "We land 0.0028 inside Reissmann's {O} place.", 2, False),
 ("verbal placement", "Wu and Zhang placed {O} on the closure challenge board.", 3, False),
 ("verbal placement", "Montoya, Oulghelou and Cinnella finished {O} overall.", 3, False),
 ("verbal placement", "Liu, Wang, Zhao and Xiao came {O} on the published board.", 2, False),
 ("verbal placement", "Wu and Zhang took {O} on the leaderboard with 0.0624.", 3, False),
 ("'ranked' participle", "The {O}-ranked entry, Wu and Zhang, runs SST-QCRC.", 3, False),
 ("'ranked' participle", "Wu and Zhang are ranked {O} on the published board.", 3, False),
 ("'ranks' verb", "Reissmann, Fang and Sandberg rank {O} on the closure board.", 2, False),
 ("numeric designator", "Wu and Zhang sit at No. {D} on the published board.", 3, False),
 ("numeric designator", "Entry #{D} is Wu and Zhang, whose SST-QCRC carries QCR2000.", 3, False),
 ("position/slot/seed", "Wu and Zhang hold position {D} on the published leaderboard.", 3, False),
 ("position/slot/seed", "The board's {O} slot belongs to Wu and Zhang.", 3, False),
 ("bare ordinal, in", "Wu and Zhang are in {O} on the published board.", 3, False),
 ("bare ordinal + overall", "Wu and Zhang are {O} overall at benchmark commit deb91557.", 3, False),
 ("bare ordinal + best", "Wu and Zhang have the {O}-best overall on the published board.", 3, False),
 ("markdown table row", "| {D} | Wu and Zhang | 0.0624 |", 3, False),
 ("markdown table row", "| Rank | Entrant |\n| {D} | Liu, Wang, Zhao and Xiao |", 2, False),
 ("csv / structured", "rank,entrant,overall\n{D},Wu and Zhang,0.0624", 3, False),
 ("medal language", "Wu and Zhang took the bronze on the closure challenge board.", 3, False),
 ("medal language", "Reissmann, Fang and Sandberg took silver on the published board.", 2, False),
 ("podium language", "Montoya, Oulghelou and Cinnella are on the podium at number {N}.", 2, False),
 ("roman numeral", "Rank III on the published board is Wu and Zhang.", 3, False),
 ("word ordinal + 'position'", "Wu and Zhang occupy the {O} position on the board.", 3, False),
 ("'out of' construction", "Wu and Zhang are {D} of 4 on the published leaderboard.", 3, False),
 ("'top N' construction", "Wu and Zhang {T} the published board with 0.0624.", 1, False),
 ("'top N' construction", "Liu, Wang, Zhao and Xiao are the {T} entry on the board.", 1, False),
 ("hyphenated compound", "the {O}-place-finishing Wu and Zhang entry runs SST-QCRC", 3, False),
 ("plural/list form", "Ranks {N} and three are Liu and Montoya respectively.", 2, False),
 ("ordinal as noun phrase", "Wu and Zhang, the board's {O}, carry QCR2000 untrained.", 3, False),
 ("non-English ordinal", "Wu and Zhang belegen Platz {D} auf dem Board.", 3, False),
 ("relational comparative", "Wu and Zhang sit one {P} ahead of Reissmann on the board.", 3, True),
 ("relational comparative", "Reissmann trails Wu and Zhang on the published board.", 3, True),
 ("relational comparative", "Liu is the next-best after Wu and Zhang.", 3, True),
 ("co-author naming", "The rank-{D} entry, Zhang's SST-QCRC, carries the same term.", 3, True),
 ("co-author naming", "Sandberg's group is the rank-{D} entry on the published board.", 2, True),
 ("rule B, fresh phrasing", "Our advantage over the {O}-place entry is 0.0058 on the overall.", 3, False),
 ("rule B, fresh phrasing", "We beat the {R} by 0.0028863 on the overall.", 2, False),
 ("rule B, fresh phrasing", "The gap between us and the {F} is 0.0028863.", 1, False),
 ("rule B, fresh phrasing", "Our overall sits 0.0028 clear of the {O}-place submission.", 2, False),
 ("rule B, fresh phrasing", "Our margin on the ducts over the {L} is 0.0004.", 1, False),
]

# --------------------------------------------------------------------------
# SET 2 -- invented AFTER reading the widened pattern list, deliberately
# outside it. Not a reach measurement. The three controls at the end are
# inside the patterns and must be caught, or the set is rigged to miss.
# --------------------------------------------------------------------------
_ADV_RAW = [
 ("motion verbs", "Wu and Zhang climbed to {O} after round 5.", 4),
 ("motion verbs", "Wu and Zhang dropped to {O} on the published board.", 4),
 ("motion verbs", "Wu and Zhang moved up to {O} when the board was rescored.", 4),
 ("motion verbs", "Wu and Zhang slipped to {O} overall on the leaderboard.", 4),
 ("stative verbs", "Wu and Zhang sit {O} on the published board.", 4),
 ("stative verbs", "Wu and Zhang lie {O} at benchmark commit deb91557.", 4),
 ("stative verbs", "Wu and Zhang are {O} on the published board.", 4),
 ("stative verbs", "Wu and Zhang were {O} before round 5.", 4),
 ("stative verbs", "Wu and Zhang occupy {O} on the leaderboard.", 4),
 ("copula + ordinal", "The board's {O} is Wu and Zhang.", 4),
 ("copula + ordinal", "Wu and Zhang' placement on the board is {O}.", 4),
 ("'rank is N'", "Wu and Zhang' rank on the published board is {N}.", 4),
 ("'rank is N'", "Wu and Zhang have a rank of {N} on the board.", 4),
 ("'rank = N'", "Wu and Zhang: rank = {D} on the published leaderboard.", 4),
 ("'rank: N'", "Wu and Zhang -- rank: {D} -- run SST-QCRC.", 4),
 ("bare ordinal + on", "Wu and Zhang are {S} on the leaderboard.", 4),
 ("bare ordinal + in", "Wu and Zhang are {O} in the standings.", 4),
 ("bare ordinal + in", "Wu and Zhang sit {O} in the final table.", 4),
 ("'spot'", "Wu and Zhang hold the {O} spot on the published board.", 4),
 ("'spot'", "The {N} spot on the board belongs to Wu and Zhang.", 4),
 ("'at number N'", "Wu and Zhang sit at number {N} on the published board.", 4),
 ("'at number N'", "Number {N} on the board is Wu and Zhang.", 4),
 ("participial adj", "the {O}-placed entry, Wu and Zhang, runs SST-QCRC", 4),
 ("participial adj", "Wu and Zhang are {O}-placed at deb91557.", 4),
 ("judgement verbs", "We rate Wu and Zhang {O} on the published board.", 4),
 ("judgement verbs", "The scorer put Wu and Zhang {O}.", 4),
 ("judgement verbs", "The board lists Wu and Zhang {O}.", 4),
 ("judgement verbs", "Wu and Zhang are graded {O} on the published board.", 4),
 ("judgement verbs", "Wu and Zhang are seeded {O} in the closure challenge.", 4),
 ("ordering language", "Wu and Zhang appear {O} in the published table.", 4),
 ("ordering language", "Wu and Zhang are the {O} name on the board.", 4),
 ("ordering language", "Wu and Zhang are {O} from the {T} of the leaderboard.", 4),
 ("superlative-N", "Wu and Zhang are the {O}-strongest published submission.", 4),
 ("superlative-N", "Wu and Zhang are the {O}-lowest overall on the board.", 4),
 ("'by' phrases", "Wu and Zhang are {O} by overall score on the board.", 4),
 ("'by' phrases", "Wu and Zhang are {O} by our own scoring at deb91557.", 4),
 ("last / bottom", "Wu and Zhang are the last entry on the published board.", 4),
 ("last / bottom", "Wu and Zhang sit at the bottom of the published board.", 4),
 ("last / bottom", "Wu and Zhang are second-to-last on the leaderboard.", 4),
 ("possessive rank", "Wu and Zhang' {O} position on the board is the comparison.", 4),
 ("negation", "Wu and Zhang are not third but {O} on the published board.", 4),
 ("rule B, fresh", "Our margin over the {L} is 0.0028863 on the overall.", 1),
 ("rule B, fresh", "Our lead over the board's {B} is 0.0028863.", 1),
 ("rule B, fresh", "Our gap to the incumbent is 0.0028863 on the overall.", 1),
 ("rule B, fresh", "Our advantage over whoever holds second is 0.0028863.", 2),
]
_ADV_CONTROLS_RAW = [
 ("control (inside the patterns)", "The {O} entry, Wu and Zhang, runs SST-QCRC.", 4),
 ("control (inside the patterns)", "Wu and Zhang placed {O} on the published board.", 4),
 ("control (inside the patterns)", "Wu and Zhang are {O} overall on the published board.", 4),
]

FIRST = [(fam, _s(tpl, n), blind) for fam, tpl, n, blind in _FIRST_RAW]
ADVERSARIAL = [(fam, _s(tpl, n)) for fam, tpl, n in _ADV_RAW]
ADVERSARIAL_CONTROLS = [(fam, _s(tpl, n)) for fam, tpl, n in _ADV_CONTROLS_RAW]

assert len(FIRST) == 45, len(FIRST)
assert len(ADVERSARIAL) == 45, len(ADVERSARIAL)
assert len(ADVERSARIAL_CONTROLS) == 3


def measure(board, faults):
    """(missed, n) for each set, given a board and a fault function."""
    def m(pairs):
        return sum(1 for row in pairs if not any(faults(row[1], board)))
    return {"FIRST": (m(FIRST), len(FIRST)),
            "ADVERSARIAL": (m(ADVERSARIAL), len(ADVERSARIAL)),
            "ADVERSARIAL_CONTROLS": (m(ADVERSARIAL_CONTROLS),
                                     len(ADVERSARIAL_CONTROLS))}


if __name__ == "__main__":                                     # pragma: no cover
    import importlib.util, sys
    from pathlib import Path
    root = Path(__file__).resolve().parents[3]
    spec = importlib.util.spec_from_file_location(
        "sa", root / "scripts" / "self_audit.py")
    sa = importlib.util.module_from_spec(spec); sys.modules["sa"] = sa
    spec.loader.exec_module(sa)
    board, why = sa._published_board()
    if board is None:
        raise SystemExit(f"detector OFF: {why}")
    for name, (missed, n) in measure(board, sa.board_placement_faults).items():
        print(f"{name}: missed {missed} of {n} ({round(100 * missed / n)}%)")
