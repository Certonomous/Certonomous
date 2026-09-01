#!/usr/bin/env python3
"""The tense rule, keyed to the STAGE a string is published in.

WHY THIS MODULE EXISTS.  Sanaa's language rule has now flipped once.  At ~03:40Z
on 2026-09-01 it read *"Progressive tense while running ... past tense for
results."*  At ~04:20Z it was restated flat: *"no past tense"*.  At 20:30Z
(`etc/sessions/2026-09-01T2030Z_sanaa_demo_shooting_protocol.md`, committed as
`cfcf766f`) it returned to the two-part form and that document says in its own
opening lines that it SUPERSEDES conflicting earlier presentation details:

    Present and progressive tense while running; past tense for results.

The three Act D face checkers implemented the FLAT 04:20Z form: one global
`PAST` pattern swept over the whole rendered face, firing wherever it matched.
Under the restored rule that instrument is not merely stale, it is INVERTED for
results text -- it flags compliant strings and pushes an author to write results
in the present tense, which is itself now a violation.  An instrument enforcing
a superseded rule is not neutral; it manufactures the wrong artefact.

THE FIX IS NOT A FLIPPED BOOLEAN, AND THAT IS THE WHOLE POINT OF THIS FILE.  A
global flag would have to be flipped again the next time the rule moves, and the
rule has already moved twice in seventeen hours.  What does not move is that
tense is a property of THE BEAT A STRING IS PUBLISHED IN.  So the regime lives
in one table, `STAGE_REGIME`, keyed by the protocol's own eight stages; the
patterns below say what past-tense narration and present-tense run narration
LOOK like, and never say where they are allowed.  A future revision edits the
table.  Nothing else moves.

THE THIRD REGIME IS LOAD-BEARING AND IS NOT AN ESCAPE HATCH.  Between the two
tense-carrying regimes sits STATIC: definitions, units, assumptions, figure
notes -- text where tense makes no claim about run state at all ("chord is
0.999416 m", "Degrees against span in metres").  Without it, a results-stage
present-tense rule would fire on every sentence on the sheet, and a rule that
fires on everything fires on nothing.  With it, the obvious abuse is to mark the
whole document STATIC and sweep clean, so `check_coverage` prints the word split
per regime and REFUSES below a floor on the tense-carrying share.

WHERE THE JUDGEMENT IS MADE, AND THE LIMIT OF IT.  The tense sweep reads the
SOURCE, not the rendered face, and that is a deliberate departure from the rest
of these checkers, which read the face on purpose.  The reason is mechanical:
`pdftotext -layout` interleaves a two-column page line by line, so a character
offset in the extracted face does not correspond to a position in the document's
reading order and CANNOT be resolved to a beat.  Staging a face offset would be
a fiction.  The source is in true reading order.  The cost is that a string could
in principle be in the source and not on the face, so every hit carries a
`on_face` flag set by looking the matched text up in the rendered face as a
normalised bigram; a hit that does not reach the face is reported as SOURCE-ONLY
rather than silently kept or silently dropped.  A bigram can straddle a column
break in the extraction and read as absent, so SOURCE-ONLY is evidence of doubt,
not proof of absence, and it is labelled that way.

    python3 docs/dafoam/demo/demo_stages.py     # runs the plant controls
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass

# ---------------------------------------------------------------- the stages --
# The protocol's own eight, named as it names them.  These are the vocabulary
# the per-document maps below speak in.
GEOMETRY = 1
PROGRESS = 2
ACKNOWLEDGEMENT = 3
EXPERT_DISCUSSION = 4
RUN = 5
RESULTS = 6
REPORT = 7
CONVERGENCE_STUDY = 8

STAGE_NAMES = {
    GEOMETRY: "1 GEOMETRY", PROGRESS: "2 PROGRESS",
    ACKNOWLEDGEMENT: "3 ACKNOWLEDGEMENT", EXPERT_DISCUSSION: "4 EXPERT",
    RUN: "5 RUN", RESULTS: "6 RESULTS", REPORT: "7 REPORT",
    CONVERGENCE_STUDY: "8 CONVERGENCE STUDY",
}

# --------------------------------------------------------------- the regimes --
RUNNING = "RUNNING"   # present/progressive required; past tense is a violation
RESULTS_R = "RESULTS"  # past tense required; present run narration is a violation
STATIC = "STATIC"     # tense carries no claim; neither rule fires

#: THE ONE TABLE THE RULE LIVES IN.  Sanaa's 20:30Z sentence, made executable.
#: Stages 1-5 are the platform working, so they are narrated as it works.  Stage
#: 6 is what it found, so it is narrated in the past.  Stage 8 is the one beat
#: that is GENUINELY still running at the moment it is shown -- the protocol's
#: own words are "the grid convergence study for this case is running" -- so it
#: is present progressive and a past-tense form there would be a lie about a
#: study that has not finished.  Stage 7 has no entry: the REPORT tab mixes
#: results content with figure notes and assumptions, so its regions declare
#: RESULTS or STATIC individually and a bare stage 7 is refused by `Region`.
STAGE_REGIME = {
    GEOMETRY: RUNNING,
    PROGRESS: RUNNING,
    ACKNOWLEDGEMENT: RUNNING,
    EXPERT_DISCUSSION: RUNNING,
    RUN: RUNNING,
    RESULTS: RESULTS_R,
    CONVERGENCE_STUDY: RUNNING,
}

# ------------------------------------------------------------ past narration --
# Unchanged in substance from `check_actD_sheet_face.PAST`, which is where it
# was born and from where the two sibling checkers still import it.  Past tense
# is hunted BY VERB, not by a general -ed rule: "fixed", "solved", "measured",
# "matched", "painted" are participles used adjectivally all over honest
# present-tense prose, and a rule that flags them flags nothing usefully.  These
# are the auxiliaries and irregulars that can only be past.
PAST = re.compile(
    r"\b(was|were|had been|has been|have been|did not|didn't|"
    r"produced|diverged|stopped|completed|landed|reached|ended|ran|took|"
    r"asked|wrote|chose|gave|came)\b", re.I)

#: An INDEPENDENT statement of what PAST must catch.  Generated from the pattern
#: it would carry the pattern's own typos and a broken alternative would plant
#: itself and pass; written by hand it checks the pattern against something that
#: did not come from the pattern.  (The trap is real: two alternatives in this
#: rule's sibling list were dead on arrival and only a per-alternative arm
#: found them.)
PAST_ALTERNATIVES = [
    "was", "were", "had been", "has been", "have been", "did not", "didn't",
    "produced", "diverged", "stopped", "completed", "landed", "reached",
    "ended", "ran", "took", "asked", "wrote", "chose", "gave", "came",
]

# Six of those are ambiguous and the sweep must not cry wolf on them.  "The
# iteration limit IS NOT REACHED" is present passive; "the run COMPLETED early"
# is past.  The word is identical and only what precedes it separates them.
#
# `stopped` IS THE SIXTH AND IT WAS NOT IN THIS SET BEFORE.  It was found by the
# two-sided arm added with this module, not by reading: "the run is not stopped"
# is present passive and correct in a running beat, and the flat rule flagged it.
# That is a pre-existing false positive in the shared pattern, and it is the
# same shape as the five already here -- it is fixed rather than worked around,
# because leaving it would mean the new arm passes by special-casing its own
# plant.
AMBIGUOUS = {"produced", "completed", "landed", "reached", "ended", "stopped"}
PRESENT_AUX = re.compile(r"\b(is|are|am|be|being|does|do|not)\s+(?:\w+\s+){0,2}$", re.I)


def is_past(text: str, m: re.Match) -> bool:
    """True when this match is genuinely past rather than present passive."""
    if m.group(0).lower() not in AMBIGUOUS:
        return True
    return not PRESENT_AUX.search(text[max(0, m.start() - 30):m.start()])


# --------------------------------------------------- present run narration ---
# THE NEW HALF, AND THE ONE THAT HAD TO BE WRITTEN NARROW.  The temptation is to
# make this the mirror of PAST -- flag present tense in a results region -- and
# that would be useless, because a results section is FULL of legitimate present
# tense: "drag is 0.02962051", "Table 3 lists every check", "the gradient is
# checked against finite differences".  Those are timeless statements about what
# the sheet holds and what the numbers are, and they stay present under any
# revision of the rule.
#
# What Sanaa's rule actually governs is the narration of RUN EVENTS: things that
# happened once, at a moment, during a solve that is over by the time a results
# screen exists.  "Its flow solve diverges" is a completed event told in the
# present, and under the restored rule it reads as though the run were still
# going.  So this pattern is a closed list of RUN-EVENT VERBS in present forms,
# not a general present-tense detector, and every alternative is planted.
PRESENT_RUN_NARRATION = re.compile(
    # progressive: the platform still working, told in a results beat
    r"\b(?:is|are)\s+(?:still\s+|now\s+)?"
    r"(running|solving|meshing|iterating|descending|diverging|converging|"
    r"optimising|optimizing)\b"
    # present passive of a run event: "the limit is not reached"
    r"|\b(?:is|are)\s+(?:not\s+)?"
    r"(reached|stopped|completed|terminated|aborted)\b"
    # negated present: "the optimisation does not reach convergence"
    r"|\b(?:does|do)\s+not\s+"
    r"(reach|converge|diverge|stop|complete|end|fire|run|yield)\b"
    # simple present of a run event.  `ends` CARRIES AN OBJECT REQUIREMENT and
    # `starts` is absent, and neither is an oversight.  "both of its ends sit on
    # the same lift line" is a plural NOUN and "every limit is fixed before the
    # solver starts" is a timeless statement of method; both sit on our own
    # sheets today and both would have been false hits.  A rule that cries wolf
    # on the masthead teaches its reader to skim the one line that matters.
    r"|\bends\s+(?=the\b|a\b|an\b|it\b|its\b|this\b|that\b|their\b|our\b)"
    r"|\b(diverges|converges|terminates|aborts|crashes|"
    r"stops|completes|reaches|fires|finishes|yields)\b",
    re.I)

#: One plant per alternative, written independently of the pattern above, for
#: exactly the reason `PAST_ALTERNATIVES` is written by hand.
PRESENT_ALTERNATIVES = [
    "the solve is running", "the optimiser is solving",
    "the platform is meshing", "the adjoint is iterating",
    "the objective is still descending", "the flow solve is diverging",
    "the optimiser is converging", "the shape is optimising",
    "the shape is optimizing",
    "the iteration limit is reached", "the run is not stopped",
    "the sweep is completed", "the job is terminated", "the row is aborted",
    "the optimisation does not reach convergence",
    "the residual does not converge", "the solve does not diverge",
    "the clock does not stop", "the row does not complete",
    "the descent does not end", "the check does not fire",
    "the case does not run", "the re-trim does not yield a value",
    "its flow solve diverges", "the residual converges",
    "the job terminates", "the row aborts", "the solver crashes",
    "a time limit stops it", "neither of those ends the run",
    "the optimiser completes the pass", "the limit reaches its value",
    "no test fires to confirm it", "the run finishes early",
    "the re-trim yields no value",
]

#: MUST STAY QUIET in a results region.  Timeless statements of fact, in the
#: present, which no revision of the tense rule makes wrong.  Without this arm a
#: pattern that flagged all present tense would score full marks above.
STATIC_FACT_PLANTS_QUIET = [
    "drag is 0.02962051 at a lift of 0.500000",
    "the chord is 0.999416 m and the span is 0.1 m",
    "Table 3 lists every check and its limit",
    "the gradient is checked against finite differences of the same solver",
    "lift is an equality constraint at CL = 0.5",
    # The two forms the object requirement and the dropped alternative exist
    # for.  Both are on our sheets today; both must stay quiet.
    "the reduction we report is the arrow in Figure 1, and both of its ends "
    "sit on the same lift line",
    "every threshold and limit on this sheet is fixed before the solver starts",
]

#: MUST STAY QUIET in a running region: past participles used adjectivally are
#: not past-tense narration.
ADJECTIVAL_PARTICIPLE_QUIET = [
    "the solved surface at true scale",
    "the measured share sits inside the band",
    "the iteration limit is not reached",
]


# ------------------------------------------------------------- the stage map --
@dataclass(frozen=True)
class Region:
    """One declared beat of one document: where it starts, and its stage."""
    anchor: str        # a regex that matches ONCE in the source body
    stage: int
    note: str = ""

    def __post_init__(self) -> None:
        if self.stage not in STAGE_REGIME and self.stage != REPORT:
            raise SystemExit(f"REFUSE: stage {self.stage} has no regime")
        if self.stage == REPORT:
            raise SystemExit(
                "REFUSE: a region may not be declared as bare stage 7 REPORT. "
                "The report tab mixes results content with figure notes and "
                "assumptions, and they carry different tense regimes, so each "
                "block declares RESULTS or STATIC_REGION for itself.")


#: A region whose tense carries no claim.  Declared with an explicit sentinel
#: rather than by omission, so that marking a block untested is a positive act
#: that shows up in the coverage print.
STATIC_REGION = -1
STAGE_NAMES[STATIC_REGION] = "- STATIC"
STAGE_REGIME[STATIC_REGION] = STATIC


def _regime(stage: int) -> str:
    return STAGE_REGIME[stage]


# ------------------------------------------------------------------- de-TeX ---
_TEX_COMMENT = re.compile(r"(?<!\\)%.*$", re.M)
_TEX_MATH = re.compile(r"\$[^$]*\$")
_TEX_TEXTCMD = re.compile(r"\\(?:textbf|textit|emph|rolesig|underline|texttt)"
                          r"\s*\{([^{}]*)\}")
_TEX_ENVCMD = re.compile(r"\\(?:begin|end)\s*\{[^{}]*\}(?:\[[^\]]*\])?"
                         r"(?:\{[^{}]*\})*")
_TEX_BARECMD = re.compile(r"\\[A-Za-z@]+\s*(?:\[[^\]]*\])?")
_TEX_BRACES = re.compile(r"[{}]")
_TEX_TABULAR = re.compile(r"[&\\]{1,2}")


def detex(src: str) -> str:
    """Source LaTeX to rough prose.

    Rough is enough and the roughness is bounded on purpose: this text is only
    ever searched for a closed list of English verbs, and LaTeX debris is not
    English.  What it must not do is JOIN two words that were apart or SPLIT a
    word that was together, because either would fabricate or hide a match, so
    every deletion leaves a space behind.
    """
    s = _TEX_COMMENT.sub(" ", src)
    s = _TEX_MATH.sub(" 0 ", s)
    for _ in range(3):                      # nested \textbf{... \textit{...}}
        s = _TEX_TEXTCMD.sub(r" \1 ", s)
    s = _TEX_ENVCMD.sub(" ", s)
    s = _TEX_BARECMD.sub(" ", s)
    s = _TEX_BRACES.sub(" ", s)
    s = _TEX_TABULAR.sub(" ", s)
    s = s.replace("~", " ").replace("``", '"').replace("''", '"')
    return re.sub(r"\s+", " ", s)


def body(src: str) -> str:
    """Everything between \\begin{document} and \\end{document}.

    The provenance header above it is deliberately full of paths, hashes and
    gate identifiers -- that is where they went when they left the face -- and
    it is also full of past tense, honestly, because it narrates what was done.
    Sweeping it would be sweeping the wrong document.
    """
    i = src.find(r"\begin{document}")
    j = src.rfind(r"\end{document}")
    if i < 0 or j < 0:
        raise SystemExit("REFUSE: no document body found in the source")
    return src[i:j]


def segment(src_body: str, regions: list[Region]) -> list[tuple[int, int, Region]]:
    """Resolve declared anchors to spans covering the whole body.

    Every anchor must match EXACTLY ONCE and the anchors must appear in the
    order declared.  Both are refusals, not warnings: an anchor that matches
    twice silently truncates a region, and an out-of-order anchor silently
    swaps two regimes, which is the failure this whole module exists to make
    impossible.
    """
    starts: list[int] = []
    for r in regions:
        found = [m.start() for m in re.finditer(r.anchor, src_body)]
        if len(found) != 1:
            raise SystemExit(
                f"REFUSE: stage anchor {r.anchor!r} matches {len(found)} times "
                f"in the body; it must match exactly once")
        starts.append(found[0])
    if starts != sorted(starts):
        raise SystemExit("REFUSE: stage anchors are not in document order; "
                         "the map does not describe this document")
    spans = []
    for k, r in enumerate(regions):
        end = starts[k + 1] if k + 1 < len(regions) else len(src_body)
        spans.append((starts[k], end, r))
    if spans and spans[0][0] != 0:
        spans.insert(0, (0, spans[0][0],
                         Region(anchor="<preamble>", stage=STATIC_REGION,
                                note="text before the first declared anchor")))
    return spans


# ------------------------------------------------------------------ the sweep --
@dataclass(frozen=True)
class TenseHit:
    rule: str
    stage: int
    matched: str
    context: str
    on_face: bool


def _bigram_on_face(prose: str, m: re.Match, face_norm: str) -> bool:
    """Did the matched text reach the rendered face?

    The token alone is worthless as evidence -- "was" occurs everywhere -- so
    this looks for the match plus one neighbouring word, whitespace normalised.
    A false NEGATIVE is possible where a column break in `pdftotext -layout`
    splits the pair, which is why a miss is reported as SOURCE-ONLY and read as
    doubt rather than as proof the string is invisible.
    """
    a = max(0, m.start() - 40)
    before = prose[a:m.start()].split()
    after = prose[m.end():m.end() + 40].split()
    cands = []
    if before:
        cands.append(f"{before[-1]} {m.group(0)}")
    if after:
        cands.append(f"{m.group(0)} {after[0]}")
    return any(c.lower() in face_norm for c in cands)


def tense_sweep(src: str, regions: list[Region], face: str = "") -> list[TenseHit]:
    """Every tense violation, each attributed to the beat it sits in.

    PAST fires only in RUNNING regions.  PRESENT_RUN_NARRATION fires only in
    RESULTS regions.  Neither fires in STATIC.  That sentence is the whole
    behavioural change, and it is one `if` because the rule lives in
    `STAGE_REGIME` rather than in this function.
    """
    face_norm = re.sub(r"\s+", " ", face).lower()
    hits: list[TenseHit] = []
    for start, end, region in segment(body(src), regions):
        prose = detex(body(src)[start:end])
        regime = _regime(region.stage)
        if regime == RUNNING:
            for m in PAST.finditer(prose):
                if is_past(prose, m):
                    hits.append(_hit("past tense in a running beat", region, prose,
                                     m, face_norm))
        elif regime == RESULTS_R:
            for m in PRESENT_RUN_NARRATION.finditer(prose):
                hits.append(_hit("present run narration in a results beat",
                                 region, prose, m, face_norm))
    return hits


def _hit(rule: str, region: Region, prose: str, m: re.Match,
         face_norm: str) -> TenseHit:
    a, b = max(0, m.start() - 45), min(len(prose), m.end() + 45)
    return TenseHit(rule=rule, stage=region.stage, matched=m.group(0),
                    context=" ".join(prose[a:b].split()),
                    on_face=_bigram_on_face(prose, m, face_norm) if face_norm
                    else True)


def coverage(src: str, regions: list[Region]) -> dict[str, int]:
    """Words of body prose per regime.  The abuse guard's raw material."""
    out = {RUNNING: 0, RESULTS_R: 0, STATIC: 0}
    b = body(src)
    for start, end, region in segment(b, regions):
        out[_regime(region.stage)] += len(detex(b[start:end]).split())
    return out


def check_coverage(src: str, regions: list[Region],
                   min_tense_share: float = 0.30) -> list[str]:
    """REFUSE if the tense-carrying regimes have been quietly emptied.

    The obvious way to sweep clean under this module is to declare the whole
    document STATIC.  This makes that visible and then makes it fail.  The share
    is a FLOOR, not a target: the reference-wing sheet measures well above it,
    and a sheet that legitimately drifts toward definitions and figure notes
    should be argued for in its map, not slipped past this.
    """
    cov = coverage(src, regions)
    total = sum(cov.values()) or 1
    share = (cov[RUNNING] + cov[RESULTS_R]) / total
    problems = []
    if share < min_tense_share:
        problems.append(
            f"only {share:.0%} of the body ({cov[RUNNING] + cov[RESULTS_R]} of "
            f"{total} words) sits in a tense-carrying regime, against a "
            f"{min_tense_share:.0%} floor; the map has emptied the rule")
    return problems


# ------------------------------------------------------------ plant controls --
def _in(stage: int, text: str) -> list[TenseHit]:
    """Sweep a bare string as though it were the whole of one region."""
    src = "\\begin{document}\nANCHOR " + text + "\n\\end{document}"
    return tense_sweep(src, [Region(anchor="ANCHOR", stage=stage)])


def check_plants() -> tuple[int, int, list[str]]:
    """Every alternative, in BOTH directions, in both regimes.

    A one-sided control cannot tell a precise rule from one that fires on
    everything, and under a rule that has already flipped once the two-sided
    arm is the only thing that would catch the flip being applied backwards.
    """
    blind: list[str] = []
    n = 0

    def arm(name: str, ok: bool) -> None:
        nonlocal n
        n += 1
        if not ok:
            blind.append(name)

    # 1. past tense in a RUNNING beat must fire, one arm per alternative.
    for w in PAST_ALTERNATIVES:
        arm(f"past {w!r} in a running beat must fire",
            bool(_in(RUN, f"the run {w} on the wing")))
    # 2. the same strings in a RESULTS beat must stay silent.  This is the arm
    #    that would have caught the 04:20Z instrument being left in place.
    for w in PAST_ALTERNATIVES:
        arm(f"past {w!r} in a results beat must stay quiet",
            not _in(RESULTS, f"the run {w} on the wing"))
    # 3. present run narration in a RESULTS beat must fire, per alternative.
    for p in PRESENT_ALTERNATIVES:
        arm(f"present run narration {p!r} in a results beat must fire",
            bool(_in(RESULTS, p)))
    # 4. the same strings in a RUNNING beat must stay silent -- that is the
    #    tense the platform is SUPPOSED to narrate its own work in.
    for p in PRESENT_ALTERNATIVES:
        arm(f"present run narration {p!r} in a running beat must stay quiet",
            not _in(RUN, p))
    # 5. timeless present-tense fact in a RESULTS beat must stay silent.  The
    #    "fires on everything fires on nothing" guard.
    for p in STATIC_FACT_PLANTS_QUIET:
        arm(f"static fact {p!r} must stay quiet in a results beat",
            not _in(RESULTS, p))
    # 6. adjectival participle in a RUNNING beat must stay silent.
    for p in ADJECTIVAL_PARTICIPLE_QUIET:
        arm(f"adjectival participle {p!r} must stay quiet in a running beat",
            not _in(RUN, p))
    # 7. stage 8 is running even though it appears beside results, and a
    #    past-tense form there is a lie about a study that has not finished.
    arm("stage 8 keeps the running regime",
        bool(_in(CONVERGENCE_STUDY, "the grid convergence study was run")))
    arm("stage 8 accepts its own protocol sentence",
        not _in(CONVERGENCE_STUDY,
                "the grid convergence study for this case is running; the band "
                "lands in your inbox with the certificate"))
    # 8. STATIC fires nothing at all, in either direction.
    arm("static region is silent on past tense",
        not _in(STATIC_REGION, "the run diverged on the wing"))
    arm("static region is silent on present run narration",
        not _in(STATIC_REGION, "its flow solve diverges"))
    return n - len(blind), n, blind


def main() -> int:
    ok, n, blind = check_plants()
    print(f"PLANT CONTROL: {ok}/{n} arms behaved "
          f"(both directions, both regimes, one arm per alternative)")
    if blind:
        print("REFUSE: these arms did not behave:")
        for b in blind:
            print(f"  {b}")
        return 2
    print("ok  the tense rule is stage-keyed and both directions are proven")
    return 0


if __name__ == "__main__":
    sys.exit(main())
