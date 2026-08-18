"""The author's held-out set for V16, committed as evidence.

WHY THIS FILE EXISTS. `scripts/self_audit.py::_PLACE_REACH` publishes three
reach measurements in the guard's own verdict line, one row per held-out set.
The grader's two sets were committed at `V16_GRADE_HELDOUT_SETS.py` after a
third grade found the table STALE BY THE COMMIT THAT INSTALLED IT -- rule B was
widened and the table shipped in the same commit, so four rule-B sentences moved
from missed to caught and nothing re-measured. The figures were generated so
they could not drift between surfaces; they could still drift from the
sentences, because the sentences were not in the repository.

This is the third row: 46 sentences invented on 2026-08-11 by the guard's own
author, BEFORE proposing any widening and WITHOUT having seen the grader's set,
which is why the two agree that the two-pattern version missed roughly four
fifths and are the corroboration of each other rather than a repetition. With
this file every row of `_PLACE_REACH` recomputes from its own sentences, and
`sdk/tests/test_rank_claim_surfaces.py` fails if the table and the sentences
ever disagree again.

Every sentence pins a placement on a NAMED board entrant that DISAGREES with the
published board (Reissmann 1, Wu 2, Liu 3, Montoya 4 at benchmark commit
deb91557), so every one ought to be caught by a guard anchored to the claim
rather than to a spelling. Fourteen are not, and the verdict line says so.

THE ORDINALS AND POSITION WORDS ARE ASSEMBLED AT IMPORT, under the convention
`sdk/tests/test_rank_claim_surfaces.py` states and this lab has now had to
re-apply after the fact five times in one night, in three files, by three
agents: a tracked file of wrong placements written out in full is a file of real
faults, and rule B has no adjudication clause that could clear them. The
sentences under test are exactly the defects; this source file contains none.
"""
from __future__ import annotations

_O = {1: "fir" + "st", 2: "seco" + "nd", 3: "thi" + "rd", 4: "four" + "th"}
_S = {3: "3" + "rd", 4: "4" + "th"}
_D = {4: "4"}
_R = "runner" + "-up"
_F = "front" + "-runner"
_T = "to" + "p"
_L = "lead" + "er"
_MED = "sil" + "ver"
_RN = "I" + "V"
_DE = "vi" + "er"
_PLZ = "Pla" + "tz"
_C = {1: "o" + "ne", 3: "thr" + "ee", 4: "fo" + "ur"}
_D3, _D1 = "3", "1"


def _s(t: str) -> str:
    return t.format(O1=_O[1], O2=_O[2], O3=_O[3], O4=_O[4], S3=_S[3], S4=_S[4],
                    D4=_D[4], R=_R, F=_F, T=_T, L=_L, MED=_MED, RN=_RN,
                    DE=_DE, PLZ=_PLZ, C1=_C[1], C3=_C[3], C4=_C[4],
                    D3=_D3, D1=_D1)


_RAW = [
    ('rank token, digit', 'The rank-{D4} entry, Wu and Zhang, runs SST-QCRC.'),
    ('rank token, word', 'The rank {C4} entry, Wu and Zhang, runs SST-QCRC.'),
    ('ordinal-place compound', 'The {O4}-place entry, Wu and Zhang, carries the term.'),
    ('possessive ordinal', "Wu and Zhang's {O4} place on the board is unchanged."),
    ('parenthetical rank', 'Wu and Zhang (rank {D4}) publish an overall of 0.0624.'),
    ('participle: ranked', 'The published entry ranked {O4} is Wu and Zhang.'),
    ('participle: ranked-2', 'Wu and Zhang, ranked {O4} before round 5, run the same term.'),
    ('verb: ranks', 'Wu and Zhang ranks {O4} on the published board.'),
    ('compound: Nth-ranked', 'The {O4}-ranked entry, Wu and Zhang, runs SST-QCRC.'),
    ('verbal: placed', 'Wu and Zhang placed {O4} on the published board.'),
    ('verbal: finished', 'Wu and Zhang finished {O4} on the board.'),
    ('verbal: came', 'Wu and Zhang came {O4} in the published standings.'),
    ('verbal: took', 'Wu and Zhang took {O4} on the board.'),
    ('verbal: sits at', 'Wu and Zhang sits at {O4} on the published board.'),
    ('bare: Nth overall', 'Wu and Zhang are {O4} overall on the published board.'),
    ('bare: in Nth', 'Wu and Zhang are in {O4} on the board.'),
    ('bare: Nth-best', 'Wu and Zhang are the {O4}-best published entry.'),
    ('noun phrase', "Wu and Zhang, the board's {O4}, run SST-QCRC."),
    ('the Nth entry', 'The {O4} entry, Wu and Zhang, runs SST-QCRC.'),
    ('the Nth submission', 'The {O4} submission, Wu and Zhang, carries QCR2000.'),
    ('numeric: No. N', 'No. {D4} on the published board is Wu and Zhang.'),
    ('numeric: #N', '#{D4} is Wu and Zhang, who run SST-QCRC.'),
    ('numeric: rank #N', 'The board shows rank #{D4}, Wu and Zhang, at 0.0624.'),
    ('position/slot', 'Wu and Zhang hold position {D4} on the published board.'),
    ('slot', "The board's {O4} slot belongs to Wu and Zhang."),
    ('parenthetical bare', 'Wu and Zhang ({S4}) carry the same untrained term.'),
    ('board-topping', 'Wu and Zhang {T} the published board.'),
    ('tops of', 'Wu and Zhang sit at the {T} of the published board.'),
    ('leader', 'Wu and Zhang are the {L} on the published board.'),
    ('medal: silver', 'Wu and Zhang take {MED} on the published board.'),
    ('podium', 'Wu and Zhang are on the podium at number four.'),
    ('roman numeral', 'Rank {RN} on the published board is Wu and Zhang.'),
    ('markdown row', '| {D4} | Wu and Zhang | 0.0624 |'),
    ('csv row', '{D4},Wu and Zhang,0.0624'),
    ('list form', 'Ranks {C4} and five are Wu and Zhang and Montoya.'),
    ('non-English', 'Wu and Zhang liegen auf {PLZ} {DE} der Tabelle.'),
    ('reissmann: rank token', 'The rank-{D3} entry, Reissmann, Fang and Sandberg, tops nothing.'),
    ('reissmann: ranked', 'Reissmann, Fang and Sandberg ranked {O3} before round 5.'),
    ('reissmann: Nth overall', 'Reissmann and colleagues are {O3} overall on the board.'),
    ('reissmann: position word', 'Reissmann, Fang and Sandberg are the {R} on the board.'),
    ('reissmann: placed', 'Reissmann, Fang and Sandberg placed {O3} on the board.'),
    ('liu: rank token', 'The rank-{D1} entry, Liu, Wang, Zhao and Xiao, leads.'),
    ('liu: ordinal place', 'Liu, Wang, Zhao and Xiao hold {O1} place on the board.'),
    ('montoya: ranked', 'Montoya, Oulghelou and Cinnella ranked {O2} on the board.'),
    ('montoya: Nth entry', 'The {O2} entry, Montoya, Oulghelou and Cinnella, uses SpaRTA.'),
    ('RELATIONAL (declared)', 'Wu and Zhang are ahead of Reissmann on the published board.'),
]

#: (family, sentence) -- 46 sentences, every one a WRONG placement on a NAMED entrant.
AUTHOR = [(fam, _s(t)) for fam, t in _RAW]

assert len(AUTHOR) == 46, len(AUTHOR)


# --------------------------------------------------------------------------
# RULE B's five shapes, invented BLIND by the independent grader and
# transcribed here because they were the one published figure with no
# committed inputs.
#
# `_PLACE_REACH_B` carried "5 of 5 shapes caught" beside three rows that
# recompute from their sentences, interpolated into the same paragraph, with
# nothing distinguishing it -- under a comment reading "It cannot happen
# again, because the sentences are now IN THE REPOSITORY". That was true of
# three of the four published figures and false of the fourth, and the fourth
# is the exact figure whose contradiction made the previous table stale. So
# these live here now and the row recomputes like every other.
#
# Rule B has no adjudication clause -- there is no correct form of a position
# word to sit beside a wrong one -- so these are assembled like everything
# else in this file.
_RULE_B_RAW = [
    ("margin over a position word", "Our margin over the {R} is 0.0028863."),
    ("beat a position word", "We beat the {R} by 0.0029 on the overall."),
    ("clear of a position word",
     "We finished clear of the {O2}-place submission."),
    ("gap between us and a position word",
     "The gap between us and the {F} is 0.0029."),
    ("margin over the leader", "Our margin over the {L} is 0.0029."),
]

#: (family, sentence) -- five RULE-B shapes; five sentences is a smoke test,
#: not a reach measurement, and the guard's verdict line says so.
RULE_B = [(fam, _s(t)) for fam, t in _RULE_B_RAW]

assert len(RULE_B) == 5, len(RULE_B)


def measure(board, faults):
    """(missed, n) against a board and a fault function."""
    missed = sum(1 for _fam, s in AUTHOR if not any(faults(s, board)))
    caught_b = sum(1 for _fam, s in RULE_B if faults(s, board)[1])
    return {"AUTHOR": (missed, len(AUTHOR)),
            "RULE_B_CAUGHT": (caught_b, len(RULE_B))}


if __name__ == "__main__":                                     # pragma: no cover
    import importlib.util, sys
    from pathlib import Path
    # NOT `parents[3]`, and this is a defect class rather than a typo: a
    # repository root derived by COUNTING segments up from a path under a
    # MOVING tree points somewhere else the moment the tree moves.  MOVE_MAP
    # batch 7 made this file ONE SEGMENT SHALLOWER, so `parents[3]` went from
    # the repository root to `/home/ubuntu`.  There is no path literal in the
    # expression, so no prefix rewrite and no grep for `demo-output` reaches it
    # -- the same class cost `sdk/tests/test_a2_shape.py:28` a green comparison
    # over ten synthetic bodies at batch 6.  DERIVED BY SEARCHING for the
    # marker, so the answer no longer depends on this file's depth.
    root = next((_p for _p in Path(__file__).resolve().parents
                if (_p / "scripts" / "lab_paths.py").is_file()), None)
    if root is None:
        raise RuntimeError(
            "cannot locate scripts/lab_paths.py above %s; refusing to "
            "guess a repository root" % __file__)
    spec = importlib.util.spec_from_file_location(
        "sa", root / "scripts" / "self_audit.py")
    sa = importlib.util.module_from_spec(spec); sys.modules["sa"] = sa
    spec.loader.exec_module(sa)
    board, why = sa._published_board()
    if board is None:
        raise SystemExit(f"detector OFF: {why}")
    for name, (count, n) in measure(board, sa.board_placement_faults).items():
        verb = "caught" if name.endswith("_CAUGHT") else "missed"
        print(f"{name}: {verb} {count} of {n} ({round(100 * count / n)}%)")
