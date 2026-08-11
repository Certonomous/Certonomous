"""GRADER'S INDEPENDENT PRECISION SET -- Ladder V, rung V16, grade round 7.

Built BLIND, against subject `64281b6b`, to answer the one thing the rung's
author named against itself:

    "The precision denominator is the thing to attack, because I built it with
     the pattern list in hand, and a set built by someone else will give a
     different number."

That is the L-74 defect exactly: a check built with the same knowledge as the
thing it checks measures transcription fidelity, not the world.  So this set
was written under a discipline the author's could not have:

  * `campaign/V16_PRECISION_SET.py` was NOT read before these sentences were
    written, and neither were the `_place*` pattern definitions in
    `scripts/self_audit.py`.  The only inputs were (a) the PROBLEM STATEMENT
    in `LADDER_V_TRIPLE_VERIFICATION.md` -- "sentences containing a rank-like
    expression that are not live board placements pinned on a named entrant"
    -- and (b) the entry-point signature `board_placement_faults(text, board)`.
  * The classes below are the grader's own taxonomy of "ways English puts an
    ordinal near a person's name without placing them on a board".  Four of
    them (LINALG, DATED, QUOTED, CROSS) are named in the ruling itself and so
    are NOT independent; the other seven were generated here.  The split is
    reported, because a number is only as external as the frame that made it.

WHY THERE ARE NO ENTRANT SURNAMES IN THIS FILE (D4).
D4 has caught five agents in five files, every grader so far, by writing a
rank-claim as a literal into a fixture -- where the live sweep then finds it.
Splitting a sentence into word tokens is NOT enough: the guard collapses
whitespace and `_PLACE_CLAUSE` does not cut on a comma, so
`"Liu", "is", "rank", "2"` can flatten back into the very claim it was meant
to hide.  Instead every sentence carries a POSITIONAL placeholder -- `{e3}` is
"whoever the published board puts at rank 3" -- and the surnames are
interpolated at runtime from the board itself.  This file therefore contains
no board surname at all, so `_placements` skips it as a surface that names
nobody.  The positive control in the round-7 grade proves the skip is real by
planting a fault and finding it.

Recomputed from these sentences by the suite, never transcribed (L-79).
"""

# --------------------------------------------------------------------------
# THE HELD-OUT NON-PLACEMENTS.
#
# Every one is a sentence in which a rank-like expression appears bound near a
# named entrant, and in which NO live board placement is pinned on that
# entrant.  Faulting any of them is a false FAULT.
#
# `{e1}`..`{e4}` = the entrant the published board puts at rank 1..4.  The
# ordinals written into the sentences are chosen to DISAGREE with the
# placeholder's board rank wherever a placement reading would be possible --
# an agreeing ordinal cannot produce a rule-A fault and would pad the
# denominator with sentences that are safe for an uninteresting reason.
# --------------------------------------------------------------------------

NON_PLACEMENTS = [

    # LINALG -- "rank N" in its linear-algebra sense: a property of a matrix,
    # tensor or operator, not of a person.  Named in the ruling.
    ("LINALG", "The anisotropy tensor {e3} fits is rank 2 throughout the "
                "boundary layer."),
    ("LINALG", "In {e1}'s formulation the constraint Jacobian drops to rank 2 "
                "near the shock."),
    ("LINALG", "{e4} reports that the reduced Hessian has numerical rank 1 "
                "after the third cycle."),
    ("LINALG", "The correction {e2} applies is a rank 1 update to the "
                "preconditioner."),
    ("LINALG", "{e3}'s discrete adjoint uses a rank 4 approximation of the "
                "inverse."),

    # REDUCED -- the object relative pronoun is deleted, so the entrant sits
    # directly beside a verb and the head noun is several words back.  This is
    # the shape round 6 broke on; it is on the ruling's list only implicitly.
    ("REDUCED", "The gradient operator {e4} assembles is rank 2 by "
                "construction."),
    ("REDUCED", "The residual basis {e2} keeps is rank 3 after truncation."),
    ("REDUCED", "The sensitivity block {e1} inverts is rank 4 in every case "
                "we ran."),
    ("REDUCED", "The deflation subspace {e3} builds is rank 1 at the first "
                "iteration."),

    # DATED -- a standing that WAS true of a superseded board.  Named in the
    # ruling.  The tense and the date are the whole discriminator.
    ("DATED", "In the 2024 round {e2} finished 4th, and the board has been "
              "rebuilt twice since."),
    ("DATED", "{e1} placed 3rd on the January board, before the rescoring."),
    ("DATED", "{e4} was ranked 2nd on the pilot leaderboard we retired in "
              "March."),
    ("DATED", "The archived standings from last year put {e3} at position 1."),

    # QUOTED -- somebody else's claim, reported and usually disowned in the
    # same sentence.  Named in the ruling.
    ("QUOTED", "The referee wrote, \"{e4} is clearly the second-place "
               "entrant,\" and we do not endorse it."),
    ("QUOTED", "A press summary claimed that {e2} holds rank 4; the summary "
               "was wrong."),
    ("QUOTED", "Their README still says {e3} is ranked 2nd, and ours does "
               "not."),
    ("QUOTED", "\"{e1} is fourth,\" the tipsheet said, which is not what the "
               "board says."),

    # CROSS -- the name is in one sentence and the ordinal in the next, so no
    # single sentence pins anything.  Named in the ruling.
    ("CROSS", "{e1} withdrew the late submission. Rank 3 was left vacant for "
              "a week."),
    ("CROSS", "We reviewed {e4}'s convergence history first. Position 2 "
              "belongs to a different family entirely."),
    ("CROSS", "{e2} asked about the tie-break rule. The 4th slot is decided "
              "by wall-clock time."),
    ("CROSS", "{e3} supplied the mesh. First place went to whoever could run "
              "it unmodified."),

    # IDIOM -- an ordinal word inside a fixed phrase that has no ordinal
    # meaning at all.  Grader's own class.
    ("IDIOM", "{e4}'s tooling is first rate, and we said so in the review."),
    ("IDIOM", "{e2}'s documentation is second to none in this field."),
    ("IDIOM", "{e1} treats the mesh generator as a third party component."),

    # ORDINAL_OTHER -- the ordinal counts something real, but not a board
    # position: attempts, authors, drafts, runs, submissions.  Grader's own.
    ("ORDINAL_OTHER", "{e3}'s third attempt converged where the first two "
                      "stalled."),
    ("ORDINAL_OTHER", "{e4} is the second author on the 2023 paper."),
    ("ORDINAL_OTHER", "{e2} shipped the first draft of the harness in April."),
    ("ORDINAL_OTHER", "{e1}'s fourth run is the only one with the fine mesh."),
    ("ORDINAL_OTHER", "We take {e3}'s second submission as the baseline for "
                      "this table."),

    # BIBLIO -- volume, number, page, edition, chapter.  A citation is dense
    # with small integers next to a surname and asserts nothing.  Grader's own.
    ("BIBLIO", "{e3}, R. and Chen, S., J. Comput. Phys., vol. 4, no. 2, "
               "p. 1."),
    ("BIBLIO", "See {e4} 2022, chapter 3, section 1, for the derivation."),
    ("BIBLIO", "{e2}, H., ed. 2, p. 4, is the edition our numbers came from."),

    # ABBREV -- an abbreviation-final period sits between the name and the
    # ordinal.  Whether that period ends the sentence is the whole question,
    # and this rung changed the answer.  Grader's own class.
    ("ABBREV", "We follow {e2} et al. Rank 4 entries were excluded from that "
               "study."),
    ("ABBREV", "The mesh is described in {e3} et al. Fig. 2 shows the rank 1 "
               "correction."),
    ("ABBREV", "Compare {e4} et al. No. 1 in that table is the coarse case."),

    # OTHERBOARD -- a genuine ordinal placement, on a DIFFERENT and explicitly
    # named ranking.  Grader's own class, and the one a reader is most likely
    # to meet in the wild.
    ("OTHERBOARD", "On the SU2 benchmark {e2} is 4th, which is a different "
                   "leaderboard entirely."),
    ("OTHERBOARD", "{e3} came 1st in the 2019 AIAA student competition."),
    ("OTHERBOARD", "{e1} sits at position 2 in the citation ranking, not the "
                   "closure board."),
    ("OTHERBOARD", "{e4} is 3rd by wall-clock on our internal timing table."),

    # NEGATED -- negation, interrogative and counterfactual.  The ordinal is
    # denied, questioned or hypothesised, never asserted.  Grader's own.
    ("NEGATED", "{e1} is not ranked 3rd, whatever the mirror says."),
    ("NEGATED", "Is {e2} really rank 1? The board says otherwise."),
    ("NEGATED", "If {e4} had converged, she would have been 2nd."),
    ("NEGATED", "Nobody has claimed {e3} is 4th, and nobody should."),
]

# The four classes the RULING itself names.  Sentences in these classes had a
# hint from the same document the author read, so they are not fully external;
# the round-7 grade reports the precision figure with and without them.
RULING_NAMED_CLASSES = frozenset({"LINALG", "DATED", "QUOTED", "CROSS"})

# --------------------------------------------------------------------------
# POSITIVE CONTROLS -- plain, live, wrong placements pinned on a named
# entrant.  Every one MUST fault.  Without these a precision figure of zero
# false FAULTs is indistinguishable from a detector that has been wedged shut,
# which is the failure mode this rung's own round 6 found in a repair.
# --------------------------------------------------------------------------

MUST_FAULT = [
    ("CTL-A", "{e1} holds rank 3 on the published board."),
    ("CTL-B", "{e2} is ranked 4th on the closure board."),
    ("CTL-C", "{e3} is in first place on the leaderboard."),
    ("CTL-D", "{e4} sits at position 2 in the published standings."),
    ("CTL-E", "The board puts {e2} at rank 1."),
    # An ordinal naming a position the board does not have is itself a fault.
    ("CTL-F", "{e3} finished 5th on the board."),
]

# NEGATIVE CONTROLS -- CORRECT live placements.  Every one must stay silent.
# These catch the opposite wedge: a guard that faults everything would score a
# perfect recall and a precision of zero, and MUST_FAULT alone cannot see it.
MUST_STAY_SILENT = [
    ("CTL-G", "{e1} holds rank 1 on the published board."),
    ("CTL-H", "{e4} sits at position 4 in the published standings."),
]


# --------------------------------------------------------------------------


def _entrants(board):
    """{1: 'Reissmann', ...} derived from the board, never typed in here."""
    return {rank: name.capitalize() for name, rank in board.items()}


def render(template, board):
    """One sentence, with the positional placeholders resolved."""
    who = _entrants(board)
    out = template
    for rank, name in who.items():
        out = out.replace("{e%d}" % rank, name)
    return out


def sentences(board):
    """[(label, class, sentence)] for the held-out non-placements."""
    return [("NP-%02d" % (i + 1), cls, render(tmpl, board))
            for i, (cls, tmpl) in enumerate(NON_PLACEMENTS)]


def measure(board, faults):
    """The precision figure, recomputed from the committed sentences.

    Keys are stable so the suite can assert on them without transcribing a
    number: FALSE_FAULTS / DENOMINATOR / BY_CLASS / CONTROLS_MISSED /
    SILENT_CONTROLS_FAULTED.
    """
    result = {"BY_CLASS": {}, "FALSE_FAULT_LABELS": []}
    false_faults = 0
    for lab, cls, text in sentences(board):
        hit = bool(faults(text, board)[0])
        seen, bad = result["BY_CLASS"].get(cls, (0, 0))
        result["BY_CLASS"][cls] = (seen + 1, bad + (1 if hit else 0))
        if hit:
            false_faults += 1
            result["FALSE_FAULT_LABELS"].append(lab)
    result["FALSE_FAULTS"] = false_faults
    result["DENOMINATOR"] = len(NON_PLACEMENTS)

    result["CONTROLS_MISSED"] = [
        lab for lab, tmpl in MUST_FAULT
        if not faults(render(tmpl, board), board)[0]]
    result["SILENT_CONTROLS_FAULTED"] = [
        lab for lab, tmpl in MUST_STAY_SILENT
        if faults(render(tmpl, board), board)[0]]
    return result


def admission(board, placements, names):
    """{label: n} -- how many rank-like expressions the guard actually FINDS.

    The author's set asserts at import that a rule-A pattern matches every
    sentence, so the denominator cannot be padded with sentences the guard
    never looks at.  This set applies the SAME admission rule rather than a
    friendlier one, because a precision figure flattered by unexamined
    sentences would not be comparable to 20 of 41.
    """
    pat = names(board)
    return {lab: len(placements(text, pat, board))
            for lab, _cls, text in sentences(board)}


def normalised(board):
    """Sentences reduced to a comparable key, for the disjointness assertion.

    R-ISOLATE part 2: author and grader samples are ASSERTED disjoint by a
    test, never trusted.  Overlap here would mean template reuse (L-66) and
    would make the two figures one figure counted twice.
    """
    import re
    keys = set()
    for _lab, _cls, text in sentences(board):
        keys.add(re.sub(r"[^a-z0-9 ]", "", text.lower()).strip())
    return keys
