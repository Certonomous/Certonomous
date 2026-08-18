"""The held-out NON-PLACEMENT set for V16, and the precision figure it feeds.

WHY THIS FILE EXISTS, AND WHY IT DID NOT EXIST FOR SIX ROUNDS.

`scripts/self_audit.py` publishes four reach figures -- three rows of
`_PLACE_REACH` and `_PLACE_REACH_B` -- and every one of them measures a MISS.
Nothing in the guard measured how often it binds an ordinal to an entrant in a
sentence that asserts no such thing. That asymmetry is not a gap in the
paperwork; it is why six grade rounds of false FAULTs arrived as surprises. The
instrument had no way to report its own worst failure mode, so the only thing
that could report it was a grader, one sentence at a time, and each round found
a sentence nobody had tried. The guard's own comment says the false positive is
the expensive direction -- a rule-A fault on a travelling surface is FAIL
severity -- and the expensive direction was the unmeasured one.

WHAT THE FIGURE IS, stated so it is not read as more than it is.

  FRAME. Every sentence below is one this lab could plausibly write, in which
  the rule-A pattern DOES match an expression -- asserted at import, so the set
  cannot be padded with sentences the guard never looks at -- and in which NO
  LIVE BOARD PLACEMENT IS PINNED ON A NAMED ENTRANT. A guard that is right
  about all of them is silent on all of them.

  AND THE FIGURE IS SCORED OVER FEWER THAN ALL OF THEM, WHICH IS NEW IN ROUND
  10 AND IS THE LESS FLATTERING CHOICE (docket D49). A rule-A pattern matching
  is not the same event as the guard FINDING a placement: `_placements` applies
  the homonym list, the probability form, the of-N form and the linear-algebra
  subject-head discriminator after the match, and `board_placement_faults` --
  whose output is this figure's NUMERATOR -- can only fault a sentence that
  survives all of it. Scoring the numerator with one predicate and the
  denominator with another is what this file did for three rounds, and it put
  13 sentences in the denominator that were structurally incapable of entering
  the numerator. The denominator is now `admitted_labels` below, the same
  predicate the numerator uses. All 41 sentences stay in the file, all 41 still
  assert a rule-A match at import, and 28 of them are scored. The cost of the
  correction falls on this file's own headline: 20 of 41 (49%) becomes 20 of 28
  (71%), the numerator unmoved because all 13 dropped sentences were true
  negatives.

  FILTER. Board read from the benchmark README pin: Reissmann 1, Wu 2, Liu 3,
  Montoya 4. A sentence "faults" if `board_placement_faults` returns a rule-A
  or a rule-B fault for it.

  THE SET IS ADVERSARIAL, NOT REPRESENTATIVE. It was built by the guard's own
  author WITH the pattern list in hand and with six rounds of grade findings in
  hand, and it is deliberately weighted toward the shapes that have already
  broken. It is therefore not a rate over the corpus -- the corpus rate is
  reported separately in the verdict line as the live sweep, and is much
  better. Reading this number as "the guard is wrong this often in practice"
  would overstate it in the pessimistic direction.

  AND IT IS NOT A CEILING EITHER, WHICH IS WHAT THIS PARAGRAPH USED TO SAY.
  The sentence that stood here read: "So the figure is a WORST CASE on hard
  sentences, not a rate over the corpus." That was a bound, and grade round 7
  falsified it -- a disjoint set built blind by an independent grader measures
  19 of 25 against this set's 20 of 28. The hedge was written to stop a reader
  overstating the number in the pessimistic direction and it understated it in
  the optimistic one, which is the direction this rung exists to stop being
  wrong in. It is quoted here rather than deleted, because a repair that erases
  the mistake it repaired destroys the record (L-76); it is not asserted
  anywhere.

  THE CLAUSE THAT WAS DELETED FROM THAT PARAGRAPH, AND WHY THE STRIKE SURVIVED
  IT ANYWAY. The sentence above read, until 2026-08-11, that the grader's set
  measured its 19 of 25 "UNDER THIS FILE'S OWN ADMISSION RULE UNCHANGED". That
  was false -- the grader's set admitted on `_placements` and this one admitted
  on a raw match -- and it is quoted here rather than deleted, for the same
  reason as the sentence it modified. It is not asserted anywhere. The strike
  above does NOT rest on it: 19 of 25 exceeds this set's rate under every
  common admission rule, including the one now in use, so "worst case" is
  falsified without reference to how either denominator was drawn.

  ONE ROW IS A SELF-REPORT. The guard therefore publishes this set's figure
  BESIDE the grader's, each naming who built it and whether they were blind,
  exactly as `_PLACE_REACH` has always done for the recall half. The two
  disagree, and the disagreement is the finding (L-82). The other set is
  `campaign/V16_GRADE_ROUND7_PRECISION_SET.py`; the two are asserted disjoint
  by the suite rather than assumed to be (L-66).

  IT IS RECOMPUTED, NOT RECORDED. `_PLACE_PRECISION` in the guard carries the
  figure and `sdk/tests/test_rank_claim_surfaces.py` recomputes it from the
  sentences here on every run, reddening on disagreement -- the same repair
  L-79 forced on the reach figures after they went stale in the commit that
  installed them. A number whose inputs are not in the repository can go stale
  silently; this one cannot go stale without
  `test_the_published_precision_figure_recomputes_from_its_sentences` reddening
  -- which is a claim about the suite being run, not about the number being
  eternally right.

  POSITIVE CONTROLS. A set of sentences that must all be SILENT is satisfied
  perfectly by a guard that has been switched off. `CONTROLS` below are wrong
  placements that must all FAULT, and the test asserts both directions.

THE ORDINALS, POSITION WORDS AND THE `ra`+`nk` TOKENS ARE ASSEMBLED AT IMPORT,
under the convention `sdk/tests/test_rank_claim_surfaces.py` states and docket
D4 names: a tracked file that spells a wrong placement in full IS a file of real
faults, and rule B has no adjudication clause that could clear them. The
sentences under test are exactly the defects; this source file contains none,
and neither does the prose about them. Verified at commit time by running the
live guard over this file, with a positive control showing the run can find a
planted fault.
"""
from __future__ import annotations

# Split so this source carries no placement the guard can match.
_RK = "ra" + "nk"
_RKD = "ra" + "nk-"
_D = {1: "1", 2: "2", 3: "3", 4: "4"}
_O = {1: "fir" + "st", 2: "seco" + "nd", 3: "thi" + "rd", 4: "four" + "th"}
_S = {2: "2" + "nd", 4: "4" + "th"}
_P = "pl" + "ace"
_R = "runner" + "-up"
# Split for the same reason as everything else here, and it was NOT split in
# the first draft of this file: the live guard was run over it before commit,
# under docket D4, and reported this source as carrying one real rule-A fault.
# The convention has now caught five agents in five rounds. The sentence below
# is a probe about a front-runner; written out it was a claim about one.
_F = "front" + "-runner"


def _s(t: str) -> str:
    return t.format(RK=_RK, RKD=_RKD, D1=_D[1], D2=_D[2], D3=_D[3], D4=_D[4],
                    O1=_O[1], O2=_O[2], O3=_O[3], O4=_O[4], S2=_S[2],
                    S4=_S[4], P=_P, R=_R, F=_F)


# (class, label, sentence template)
#
# The CLASS column is what the guard's blind-spot list is generated against, so
# a shape cannot be counted in the figure and left out of the enumeration, or
# the reverse. That pairing is the whole point: the ruling permits a shape to be
# KNOWINGLY ACCEPTED rather than fixed, provided it is counted here and named
# there.
_RAW = [
    # ---- linear algebra, subject head ON `_PLACE_LINALG_NEAR` -------------
    ("linalg-head-listed", "tensor with a relative clause",
     "The anisotropy tensor that Liu fits is {RK} {D2} almost everywhere."),
    ("linalg-head-listed", "tensor with a genitive",
     "The Reynolds stress tensor of Wu is {RK} {D2} in three dimensions."),
    ("linalg-head-listed", "basis with a relative clause",
     "The integrity basis that Montoya uses is {RK} {D3} at every cell."),
    ("linalg-head-listed", "operator with a relative clause",
     "The Koopman operator that Liu fits is {RK} {D2} pointwise."),
    ("linalg-head-listed", "gradient with a genitive",
     "The mean velocity gradient of Montoya is {RK} {D2} by construction."),
    ("linalg-head-listed", "attributive, right-hand test",
     "The Reynolds stress is a {RK} {D2} tensor in three dimensions, as Liu "
     "notes."),
    ("linalg-head-listed", "fronted modifier",
     "In the duct case the anisotropy tensor of Liu is {RK} {D2} everywhere."),
    ("linalg-head-listed", "hyphenated attributive",
     "Liu approximates the closure with a {RKD}{D2} pure-shear tensor."),

    # ---- linear algebra, subject head NOT on the word list ----------------
    ("linalg-head-unlisted", "covariance kernel",
     "The covariance kernel that Liu fits is {RK} {D2} pointwise."),
    ("linalg-head-unlisted", "Gramian",
     "The Gramian that Liu fits is {RK} {D2} pointwise."),
    ("linalg-head-unlisted", "graph Laplacian",
     "The graph Laplacian that Liu fits is {RK} {D2} pointwise."),
    ("linalg-head-unlisted", "coefficient array",
     "The coefficient array that Montoya assembles is {RK} {D3} in every "
     "case."),

    # ---- reduced relative: the relativizer English is free to drop --------
    ("reduced-relative", "present tense",
     "The anisotropy tensor Liu fits is {RK} {D2} almost everywhere."),
    ("reduced-relative", "past participle",
     "The Reynolds stress tensor Montoya published is {RK} {D2} at every "
     "cell."),
    ("reduced-relative", "reporting verb",
     "The velocity gradient Wu reports is {RK} {D3} pointwise."),
    ("reduced-relative", "with an auxiliary",
     "The strain-rate tensor Reissmann has published is {RK} {D2} in the log "
     "layer."),

    # ---- coordination -----------------------------------------------------
    ("coordination", "genitive determiner in the second conjunct",
     "The Reynolds stress tensor and Liu's closure are {RK} {D2} at every "
     "cell."),
    ("coordination", "basis in the second conjunct",
     "The strain invariant and Montoya's basis are {RK} {D3} in the duct."),

    # ---- homonyms of the WORD, which the exclusion list owns --------------
    ("homonym", "MPI rank",
     "MPI_ABORT was invoked on {RK} {D1} in MPI_COMM_WORLD while Liu's case "
     "ran."),
    ("homonym", "process rank",
     "The solver pinned Montoya's mesh partition to process {RK} {D2}."),
    ("homonym", "a probability",
     "P({RK} {D1}) = 68% against Wu and Zhang on eight cases."),
    ("homonym", "our own claim, owned by the sibling guard",
     "Our entry of record is {RK} {D1} of 5 scored locally, and Liu's is not."),

    # ---- bibliography and titles ------------------------------------------
    ("bibliography", "a title containing the linear-algebra sense",
     "Wu, X. and Zhang, J. (2022). A {RK} {D2} correction to the "
     "eddy-viscosity closure."),
    ("bibliography", "the Nth entry of a journal issue, not of the board",
     "Liu and Wang, JCP 2021, the {O4} entry in that special issue."),

    # ---- the idiom --------------------------------------------------------
    ("idiom", "in the Nth place, entrant within the bind",
     "Liu's team got there in the {O1} {P}, and we followed."),
    ("idiom", "in the Nth place, entrant beyond the bind",
     "Wu should not have run the coarse mesh in the {O1} {P}."),

    # ---- adjacency across a sentence boundary -----------------------------
    ("cross-sentence", "name in the previous sentence, copula subject",
     "Liu ran the duct case on the coarse mesh. The entrant we must beat "
     "overall is {RK} {D2} today."),
    ("cross-sentence", "name in the previous sentence, ordinal opens this one",
     "Montoya rebuilt the anisotropy tensor from the strain invariant. "
     "{RK} {D4} is a position we do not claim."),
    ("cross-sentence", "name after a semicolon",
     "Liu withdrew the coarse-mesh run; the {F} is unchanged since."),

    # ---- adjacency across a markdown structural boundary ------------------
    ("cross-structure", "heading",
     "## Liu wins the duct case study\n\nThe entrant we must beat overall is "
     "{RK} {D2} today."),
    ("cross-structure", "list item",
     "- Liu ran the duct case on a coarse mesh\n- The entrant to beat here is "
     "{RK} {D2}\n"),
    ("cross-structure", "table cell",
     "| Liu | duct case, coarse mesh | the entrant to beat is {RK} {D2} |"),
    ("cross-structure", "heading, then a relative-clause subject",
     "### Montoya's closure\n\nThe submission that leads is {RK} {D1} on the "
     "board today."),

    # ---- abbreviation-final periods ---------------------------------------
    ("abbreviation", "abbreviation then a REAL sentence break",
     "The mesh study is in Liu et al. {RK} {D2} belongs to somebody else."),
    ("abbreviation", "abbreviation inside a citation, the Nth entry of a table",
     "See Montoya et al. 2022, Table {D2}, for the {O2} entry of the basis."),

    # ---- dated history: a past board, not a live claim --------------------
    ("dated-history", "an explicitly dated round",
     "In round 3 Wu and Zhang were {RK} {D4} overall, before the rescore."),
    ("dated-history", "held ... in the round-3 standings",
     "Reissmann held {RK} {D3} in the round-3 standings and moved up after."),
    ("dated-history", "participial, dated by a following clause",
     "Liu, ranked {O2} before round 5, has since been overtaken."),

    # ---- quotation and mention --------------------------------------------
    ("quotation", "a defect quoted in order to correct it",
     "The defect read: the {RKD}{D3} entry, Wu and Zhang, runs SST-QCRC."),
    ("quotation", "a wrong ordinal reported as someone else's error",
     "Round 5's report said Montoya {P}d {O2}, which the board does not "
     "support."),
    ("quotation", "a rule-B phrase quoted as an example of the defect",
     "The guide warns against writing our margin over the {R} without naming "
     "who holds it, as Liu's draft did."),
]

#: (class, label, sentence) -- every one asserts NO live board placement.
NON_PLACEMENTS = [(cls, lab, _s(t)) for cls, lab, t in _RAW]

# POSITIVE CONTROLS. Wrong placements on named entrants, in the plainest
# grammar there is. A guard that has been wedged shut to make the set above
# come out clean fails every one of these, so the two directions cannot both be
# satisfied by breaking the guard.
_CONTROLS_RAW = [
    ("plain copula", "Liu and Wu are {RK} {D1} on the published board."),
    ("ordinal-place compound",
     "The {O4}-{P} entry, Liu, Wang, Zhao and Xiao, runs the closure."),
    ("verbal placement", "Montoya {P}d {O2} on the published board."),
    ("subject-NP fallback, apposition",
     "Montoya, who rebuilt the anisotropy tensor from the strain invariant, "
     "is {RK} {D2} overall."),
    ("abbreviation then a bare ordinal",
     "Wu et al. {RK} {D4} overall on the duct case."),
]

#: (label, sentence) -- five wrong placements that MUST fault.
CONTROLS = [(lab, _s(t)) for lab, t in _CONTROLS_RAW]

assert len(NON_PLACEMENTS) == 41, len(NON_PLACEMENTS)
assert len(CONTROLS) == 5, len(CONTROLS)


def matches_a_pattern(sa) -> list[str]:
    """Labels whose sentence NO rule-A pattern matches at all.

    A precision set can be made to look perfect by filling it with sentences
    the guard never examines. Asserted by
    `test_the_precision_set_cannot_be_padded_or_wedged`, which reddens if this
    returns anything at all.
    """
    upto = 4 + sa._PLACE_OVER
    return [lab for _cls, lab, sentence in NON_PLACEMENTS
            if not sa._place_pattern(upto).search(sa._place_flatten(sentence))]


def admitted_labels(board, placements, names):
    """Labels of the sentences the guard ACTUALLY EXAMINES.

    `len(placements(...)) > 0` -- the same predicate `board_placement_faults`
    is built on, so this figure's denominator and its numerator come from one
    function rather than two. See the FRAME note above and docket D49: for
    three rounds this set was scored over every sentence a rule-A pattern
    merely matched, which is a strictly looser event, while the grader's set
    was scored over this one. The comparison between the two rows was therefore
    partly an artefact of the pairing.

    Callables are injected rather than imported so this file stays importable
    without the guard, exactly as `matches_a_pattern` does.
    """
    pat = names(board)
    return {lab for _cls, lab, sentence in NON_PLACEMENTS
            if placements(sentence, pat, board)}


def measure(board, faults, admitted=None):
    """Falsely faulted counts, headline and per class.

    `admitted` -- the labels to score, normally `admitted_labels(...)`. Passing
    None scores all 41, which is the RAW-MATCH rule this file used until round
    10; it is kept reachable so the sensitivity published in the verdict can be
    recomputed rather than typed, and it is NOT what the published figure is
    over. `TOTAL` is always the full size of the set, because a reader is
    entitled to see how many sentences it holds as well as how many were
    scored.
    """
    rows = [(cls, lab, s) for cls, lab, s in NON_PLACEMENTS
            if admitted is None or lab in admitted]
    bad = [(cls, lab) for cls, lab, s in rows if any(faults(s, board))]
    by_class: dict[str, int] = {}
    for cls, _lab in bad:
        by_class[cls] = by_class.get(cls, 0) + 1
    missed_controls = sum(1 for _lab, s in CONTROLS if not any(faults(s, board)))
    return {"PRECISION": (len(bad), len(rows)),
            "TOTAL": len(NON_PLACEMENTS),
            "BY_CLASS": by_class,
            "FALSE_FAULT_LABELS": sorted(f"{c}: {l}" for c, l in bad),
            "CONTROLS_MISSED": (missed_controls, len(CONTROLS))}


if __name__ == "__main__":                                     # pragma: no cover
    import importlib.util
    import sys
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
    sa = importlib.util.module_from_spec(spec)
    sys.modules["sa"] = sa
    spec.loader.exec_module(sa)
    board, why = sa._published_board()
    if board is None:
        raise SystemExit(f"detector OFF, not a silent pass: {why}")
    unmatched = matches_a_pattern(sa)
    if unmatched:
        print(f"NOT MATCHED BY ANY RULE-A PATTERN ({len(unmatched)}): "
              f"{unmatched}")
    admitted = admitted_labels(board, sa._placements, sa._board_names)
    got = measure(board, sa.board_placement_faults, admitted)
    k, n = got["PRECISION"]
    print(f"falsely faulted {k} of {n} held-out non-placements "
          f"({round(100 * k / n)}%), those {n} being the sentences the guard "
          f"examines out of the {got['TOTAL']} this set holds")
    for cls, count in sorted(got["BY_CLASS"].items()):
        print(f"  {cls}: {count}")
    for lab in got["FALSE_FAULT_LABELS"]:
        print(f"    !! {lab}")
    print(f"controls missed: {got['CONTROLS_MISSED'][0]} of "
          f"{got['CONTROLS_MISSED'][1]}")
