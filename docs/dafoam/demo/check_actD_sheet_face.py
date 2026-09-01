#!/usr/bin/env python3
"""Sweep the RENDERED FACE of the Act D reference-wing sheet, not its source.

WHY THE RENDERED FACE AND NOT THE .tex. The source carries a long provenance
header that is deliberately full of the things this check hunts for -- image
digests, gate identifiers, repository paths -- because that header is where
they went when they left the face. Grepping the source would fail on exactly
the material the standard says belongs there. So this compiles the sheet and
reads the text a viewer sees.

WHAT IT ENFORCES, from the owner's directives of 2026-09-01:

* ~04:20Z, verbatim: "no internal information, no past tense, no long
  sentences, all results in table, NOTHIGN that makes it look recorded".
  THE TENSE HALF OF THIS ORDER IS SUPERSEDED -- see the 2026-09-01 20:30Z
  amendment at the foot of this docstring.  Everything else in it stands.
* ~03:10Z: the screens describe a solved case in the present tense; the
  listed replay and substitution words never appear.
* ~03:45Z: every on-screen time figure for this act reads twenty minutes,
  never sixty, and never the run's own second count.

THE PLANTED CONTROL IS THE POINT. A sweep that has never been shown able to
fire is not evidence (CLAUDE.md rule 3).

AMENDED 2026-09-01 AFTER THE SUPERVISOR ATTACKED THIS FILE WITH MUTANTS. Two
arms survived a mutation they should have caught, and both holes are closed
here. They are written down because the shape of each is more useful than the
patch.

  MUTANT A -- a reader that reads ALMOST nothing passed every arm. Truncating
  the extracted face to its first 300 characters gave "12/12 rule arms
  behaved", "planted violations are recovered from the face itself" and
  "FACE HITS: 0" on a face of 44 words instead of 1,827. The old
  through-the-reader arm compared HIT COUNTS between the face and the face
  with plants appended, and the plants are recovered from the appendix no
  matter how little real face sits in front of them. A count comparison can
  never see that. Closed two ways: per-rule RECOVERY SETS, so each rule must
  individually recover its own plant, and a FLOOR on what the pipeline
  extracted -- a word count and a set of structural anchors that any version
  of this sheet must contain. A two-page sheet that reads 44 words is a broken
  pipeline whatever the rules say, and the instrument now says so in those
  words rather than failing closed by luck on a different arm.

  MUTANT B -- a broken alternative inside a multi-alternative pattern was
  invisible. Changing "ran" to "zzran" inside PAST left "12/12 rule arms
  behaved" and a clean rc=0, because the single past-tense plant exercised
  three of about twenty alternatives. THIS IS THE SAME SHAPE AS THE GUARD
  THAT SAT ON TWO OF THREE CALL SITES in the crease figure: one plant per
  RULE is not one plant per ALTERNATIVE, exactly as one assert per module is
  not one assert per call site. Every rule now declares one plant per
  alternative and every one of them must fire on its own.

AMENDED 2026-09-01 (20:30Z DIRECTIVE, `cfcf766f`): THE TENSE RULE IS NO LONGER
GLOBAL AND NO LONGER LIVES HERE.  Sanaa's shooting protocol restores the
two-part rule -- *"Present and progressive tense while running; past tense for
results"* -- and says in its opening lines that it supersedes conflicting
earlier presentation details.  The flat 04:20Z form this file implemented is
therefore INVERTED for results text: a global `PAST` sweep flags compliant
strings and pushes an author to write results in the present, which is itself
now a violation.

The repair is not a flipped flag.  This rule has moved twice in seventeen hours
and a boolean would have to move with it.  What does not move is that tense is a
property of THE BEAT A STRING IS PUBLISHED IN, so the regime now lives in one
table keyed by the protocol's own eight stages, in `demo_stages.py`, and this
file declares only WHICH BEAT EACH BLOCK OF THIS SHEET IS.  The next revision
edits that table; nothing here moves.

`PAST` and `_is_past` are still exported from this module because the two
sibling checkers import them from here, but they are now re-exports of the
shared definitions and the sweep below no longer applies them: tense is swept by
`tense_sweep`, over the source in reading order, because `pdftotext -layout`
interleaves two columns and a face offset cannot be resolved to a beat.  The
limit of that departure is stated in `demo_stages.py` and every tense hit
carries an on-face flag.

    python3 docs/dafoam/demo/check_actD_sheet_face.py
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from demo_stages import (  # noqa: E402  the tense rule, keyed to the beat
    PAST, PAST_ALTERNATIVES, AMBIGUOUS, PRESENT_AUX, RESULTS, STATIC_REGION,
    CONVERGENCE_STUDY, Region, STAGE_NAMES, is_past as _is_past, tense_sweep,
    coverage,
    check_coverage, check_plants as check_tense_plants,
)

SHEET = Path(__file__).resolve().parent / "ACT_D_reference_wing_sheet.tex"

# ------------------------------------------------------------- the stage map --
# WHICH BEAT EACH BLOCK OF THIS SHEET IS, and nothing about what tense that
# implies -- that is `demo_stages.STAGE_REGIME`'s job, so a revision of the rule
# never touches this list.
#
# THE ONE JUDGEMENT WORTH ARGUING WITH IS THE LAST ROW.  On the demo face the
# three role lines are stage 4, EXPERT DISCUSSION, which is a running beat.  On
# this REPORT-tab sheet the same three roles speak after the fact and deliver
# findings, so the beat their strings are PUBLISHED IN is stage 6.  That is the
# reading taken here and it is written down rather than assumed, because if it
# is wrong the fix is one word on this line.
STAGE_MAP = [
    Region(r"\\textbf\{Solver: DAFoam DARhoSimpleFoam", RESULTS,
           "the solved-case banner"),
    Region(r"Every threshold and limit on this sheet is fixed", STATIC_REGION,
           "method: what is fixed before the solver starts"),
    Region(r"\\textbf\{The question, and the trap inside it\}", STATIC_REGION,
           "framing: the failure mode in general, timeless"),
    Region(r"\\textbf\{Table 1\. The decomposition", RESULTS, "table 1"),
    Region(r"\\textbf\{Table 2\. The trap", RESULTS, "table 2"),
    Region(r"\\textbf\{Figure 1\. Drag against lift, all six", STATIC_REGION,
           "figure note"),
    Region(r"\\textbf\{Table 3\. Every check", RESULTS, "table 3"),
    Region(r"Read this before you use the numbers", RESULTS, "limitations"),
    # STAGE 8, AND THE ONLY RUNNING BEAT ON THIS SHEET. Sanaa's screen-8 rule is
    # that the convergence study is shown done or underway and NEVER as absent,
    # and her second form -- "the grid convergence study for this case is
    # running" -- is present progressive sitting between two results bullets.
    # It is true rather than a device: A1WR is live and A2-GC L1 cap-stopped
    # with L2 and L3 owed to a successor item. A global tense flag could not
    # have held this bullet and the beat next to it at the same time; that is
    # the whole argument for the stage map, standing on one line of one sheet.
    Region(r"cell mesh, chosen for speed", CONVERGENCE_STUDY,
           "the grid convergence study, underway"),
    Region(r"\\textbf\{The optimisation did not reach convergence", RESULTS,
           "limitations resume"),
    Region(r"\\textbf\{Table 4\. Compute", RESULTS, "compute"),
    Region(r"\\textbf\{Where these numbers come from\.\}", STATIC_REGION,
           "method: where the numbers come from"),
    Region(r"Figure notes", STATIC_REGION, "figure notes"),
    Region(r"\\rolesig\{Lead Researcher\.\}", RESULTS,
           "the three roles, delivering findings"),
    Region(r"\\textbf\{Table 5\. Why the optimisation stopped", RESULTS, "table 5"),
]

# --------------------------------------------------------------- the floor --
# MUTANT A's fix. These are properties of the PIPELINE, not of the prose: if
# they fail, pdflatex or pdftotext produced something other than this sheet
# and no verdict about its wording means anything. The word floor sits far
# below the 1,827 words the sheet carries and far above anything a broken
# read produces; the anchors are structural and survive any rewording of the
# body, so an honest edit cannot trip them.
FACE_MIN_WORDS = 800
FACE_ANCHORS = ("Where the drag reduction comes from", "Table 1", "Table 3",
                "Table 4", "Table 5", "Figure notes", "Lead Numericist")

# --------------------------------------------------------------------- rules
# Each rule: (name, compiled pattern, [one plant per alternative]).
#
# ONE PLANT PER ALTERNATIVE, NOT ONE PER RULE. That is MUTANT B's fix and it
# is the whole reason this list is verbose. A single plant proves the rule is
# wired up; it proves nothing about the fifteen alternatives it never touches,
# and a typo in any of them ships silently.
RULES: list[tuple[str, re.Pattern, list[str]]] = [
    # TWO ALTERNATIVES IN THIS FILE WERE DEAD ON ARRIVAL AND THE PER-ALTERNATIVE
    # ARM FOUND THEM ON ITS FIRST RUN. `repositor` sat inside a group closed by
    # a trailing \b, so it could only ever match a word ENDING in "repositor" --
    # never "repository", the only word anyone writes. Same trap below on the
    # sixty-minute rule. The lesson is the trailing \b, not the typo: an
    # alternation wrapped in \b(...)\b silently requires EVERY alternative to
    # end on a word boundary, and a prefix alternative therefore matches
    # nothing at all. `commit` had the milder form of it -- "commits" was
    # missed -- and is widened here too.
    ("internal: version control / commit / repository",
     re.compile(r"\b(version control|git\b|commit(?:s|ted|ting)?|"
                r"repositor(?:y|ies)|blob|sha256|md5)\b", re.I),
     ["the limits are in version control with the run",
      "run git log to see it",
      "the change was committed last night",
      "a commit landed at four",
      "two commits landed at four",
      "the repository holds the record",
      "both repositories hold the record",
      "the blob is unchanged",
      "image digest sha256 is stable",
      "stock library md5 matches"]),
    ("internal: a repository path or module name",
     re.compile(r"(?:\b\w+/){1,}\w+\.(?:py|md|json|tex|sh|log)\b"),
     ["see cases/dafoam/ladder-a/A2_crease_check.json",
      "see docs/dafoam/demo/sheet.tex",
      "see sdk/workflows/adjoint_act.py",
      "see docs/LOCATIONS.md",
      "see cases/dafoam/run_a2.sh",
      "see runs/opt_run_driver.log"]),
    ("internal: a gate identifier",
     re.compile(r"\bG[1-9]\b\s|\bgate\s+G[1-9]\b", re.I),
     ["G6 holds at both endpoints",
      "which is gate G5 and it is ungraded"]),
    ("internal: the lab's fixed verdict tokens",
     re.compile(r"\b(NOT A RESULT|GATE FAIL|GATE REACHED|BLOCKED|PENDING)\b"),
     ["row B2 is NOT A RESULT",
      "the row is a GATE FAIL",
      "the rung is GATE REACHED",
      "the arm is BLOCKED on the mesh",
      "the row is PENDING tonight"]),
    ("internal: container image or library identity",
     re.compile(r"\b(opt-packages|libidwarp|docker|bind-mount|digest)\b", re.I),
     ["it ran the shipped image opt-packages latest",
      "stock libidwarp was loaded",
      "the docker container started",
      "the launcher carries no bind-mount",
      "the image digest is pinned"]),
    ("looks recorded: replay and storage words",
     re.compile(r"\b(replay(?:ed|s)?|re-displayed|recorded|stored|cached|"
                r"pre-baked|no new solve|screens come from)\b", re.I),
     ["the monitor replay runs at pace",
      "the stage replayed the logs",
      "the stage replays the logs",
      "this request re-displayed that run",
      "nothing is recorded here",
      "the results are stored on disk",
      "the solve is cached from before",
      "a pre-baked mesh is shown",
      "no new solve is booked",
      "the screens come from that run"]),
    # THE SAME TRAILING-\b TRAP, AND HERE IT MATTERED. "60 min" matched and
    # "60 minutes" did NOT, because \b after "min" fails against the "u" that
    # follows. The single form the owner's order is most likely to be broken
    # by -- a sentence reading "sixty minutes" -- was the one form this rule
    # could not see. Widened to take the whole word.
    ("the sixty-minute forms her order removes",
     re.compile(r"\b((?:60|sixty)\s*min(?:ute)?s?|one hour|3600|3601)\b", re.I),
     ["the optimisation ran for 60 min",
      "the optimisation ran for 60 minutes",
      "the optimisation ran for sixty min",
      "the optimisation ran for sixty minutes",
      "it took one hour on this box",
      "the wall time is 3600 s",
      "the wall time is 3601 s"]),
    ("never-claim words: converged / optimum",
     re.compile(r"\b(converged|optimum)\b", re.I),
     ["the optimiser converged cleanly",
      "the shape is the optimum"]),
]

# PAST, PAST_ALTERNATIVES, AMBIGUOUS and PRESENT_AUX MOVED TO `demo_stages.py`
# with the 20:30Z amendment and are imported above. They are re-exported from
# here unchanged in substance, because the two sibling checkers import them from
# this module by name and a rename would be churn with no reader on the other
# end. One substantive change went with the move and is recorded there: `stopped`
# joined AMBIGUOUS, because "the run is not stopped" is present passive and the
# flat rule flagged it. That was a pre-existing false positive and the
# two-directional arm added with the move is what found it.
#
# The two ambiguous-participle plants that used to sit here moved with them, and
# so did their arms: they now run in BOTH regimes rather than once, which is the
# arm that would have caught the superseded rule being left in place.
#
# Words the owner's 03:10Z block strikes by name. Already one phrase per
# alternative, so the per-alternative plant is the phrase in a sentence.
STRUCK = ["not recorded in this bundle", "Solver: none", "source case",
          "no new number is produced", "reference body", "surface on file"]


def _past_plant(word: str) -> str:
    """A sentence that must make PAST fire on this one alternative.

    The carrier is deliberately bland and, for the ambiguous participles,
    deliberately carries NO present auxiliary in front of the word, since a
    present passive is the case that must stay silent.
    """
    return f"the run {word} on the wing"


def _struck_plant(phrase: str) -> str:
    return f"the sheet says {phrase} on its face"


PAST_RULE = "past tense"
STRUCK_RULE = "struck by name at 03:10Z"


def render(tex: Path, workdir: Path) -> str:
    """Compile the sheet and return the text a viewer sees."""
    shutil.copy(tex, workdir / tex.name)
    r = subprocess.run(["pdflatex", "-interaction=nonstopmode", tex.name],
                       cwd=workdir, capture_output=True, text=True)
    pdf = workdir / (tex.stem + ".pdf")
    if r.returncode != 0 or not pdf.exists():
        raise SystemExit(f"REFUSE: pdflatex rc={r.returncode}, no face to read")
    out = workdir / "face.txt"
    subprocess.run(["pdftotext", "-layout", str(pdf), str(out)], check=True)
    return out.read_text(encoding="utf-8", errors="replace")


def sweep(text: str) -> list[tuple[str, str]]:
    """Every hit, as (rule name, the matched text with a little context)."""
    hits: list[tuple[str, str]] = []

    def record(name: str, m: re.Match) -> None:
        # The MATCHED TOKEN is quoted first. A context window alone sends the
        # reader hunting for which word fired, and across a two-column layout
        # the window straddles both columns and the guess is usually wrong.
        a, b = max(0, m.start() - 40), min(len(text), m.end() + 40)
        hits.append((name, f"{m.group(0)!r} in ...{' '.join(text[a:b].split())}..."))

    for name, pat, _plants in RULES:
        for m in pat.finditer(text):
            record(name, m)
    # NO TENSE RULE HERE ANY MORE, and its absence is the 20:30Z amendment. A
    # global sweep over the extracted face cannot tell which beat a string sits
    # in, and under the restored rule the beat is the whole question. Tense is
    # swept by `tense_sweep` over the source in reading order; see `main`.
    low = text.lower()
    for phrase in STRUCK:
        if phrase.lower() in low:
            hits.append((STRUCK_RULE, phrase))
    return hits


def _fires(name: str, plant: str) -> bool:
    """Does sweeping this plant produce a hit attributed to THIS rule?

    Attribution matters. Checking only that SOMETHING fired would let one
    rule's plant be caught by a different rule and count as coverage, which
    is how a dead rule hides behind a live one.
    """
    return any(n == name for n, _ctx in sweep(plant))


def check_plants() -> tuple[int, int, list[str]]:
    """Every alternative of every rule must fire on its own plant.

    Returns (arms that behaved, arms attempted, the names that misbehaved).
    """
    blind: list[str] = []
    attempted = 0

    for name, _pat, plants in RULES:
        for plant in plants:
            attempted += 1
            if not _fires(name, plant):
                blind.append(f"{name} :: {plant!r}")

    for phrase in STRUCK:
        attempted += 1
        if not _fires(STRUCK_RULE, _struck_plant(phrase)):
            blind.append(f"{STRUCK_RULE} :: alternative {phrase!r} never fires")

    # THE TENSE ARMS RUN IN `demo_stages` AND ARE COUNTED HERE. They cannot run
    # through `_fires`, because `_fires` sweeps a bare string with no beat and a
    # beat is now the whole question. What they gained by moving is the SECOND
    # DIRECTION: each alternative is planted in a running beat, where it must
    # fire, AND in a results beat, where it must stay silent -- plus the mirror
    # pair for present run narration. One-sided arms are what let the superseded
    # rule sit here scoring full marks while it flagged compliant text.
    t_ok, t_attempted, t_blind = check_tense_plants()
    attempted += t_attempted
    blind.extend(t_blind)

    return attempted - len(blind), attempted, blind


def check_reader(face: str) -> list[str]:
    """Can the sweep recover EACH rule's plant from the face it just read?

    MUTANT A's fix, and the reason it is a per-rule SET rather than a count.
    The old arm asked whether the planted text produced more hits than the
    clean face. It always does, because the plants are appended to whatever
    the face holds -- including a face truncated to nothing. Recovering each
    rule individually is the question that was meant to be asked.
    """
    missing: list[str] = []
    for name, _pat, plants in RULES:
        planted = face + "\n" + plants[0]
        before = sum(1 for n, _c in sweep(face) if n == name)
        after = sum(1 for n, _c in sweep(planted) if n == name)
        if after <= before:
            missing.append(name)
    # PAST is no longer recovered from the face and cannot be: it is not swept
    # over the face at all. The equivalent arm for tense is the on-face flag
    # carried by every tense hit in `main`, which asks the same question the
    # other way round -- does the text I judged reach a viewer.
    rule, plant = STRUCK_RULE, _struck_plant(STRUCK[0])
    planted = face + "\n" + plant
    before = sum(1 for n, _c in sweep(face) if n == rule)
    after = sum(1 for n, _c in sweep(planted) if n == rule)
    if after <= before:
        missing.append(rule)
    return missing


def check_floor(face: str) -> list[str]:
    """Did the pipeline actually hand us this sheet? MUTANT A's other half."""
    problems: list[str] = []
    words = len(face.split())
    if words < FACE_MIN_WORDS:
        problems.append(f"the extracted face is {words} words against a "
                        f"{FACE_MIN_WORDS}-word floor; the pipeline is broken, "
                        f"not the prose")
    for anchor in FACE_ANCHORS:
        if anchor not in face:
            problems.append(f"structural anchor missing from the face: {anchor!r}")
    return problems


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        face = render(SHEET, Path(td))

    # --------------------------------------------------- the pipeline floor
    # FIRST, because every verdict below is worthless if what came back is not
    # this sheet. A clean sweep of 44 words is not a clean sheet.
    floor = check_floor(face)
    print(f"PIPELINE FLOOR: {len(face.split())} words, "
          f"{len(FACE_ANCHORS) - sum(1 for a in FACE_ANCHORS if a not in face)}"
          f"/{len(FACE_ANCHORS)} structural anchors present")
    if floor:
        for p in floor:
            print(f"REFUSE: {p}")
        return 2

    # ----------------------------------------------------- the plant control
    ok, attempted, blind = check_plants()
    print(f"PLANT CONTROL: {ok}/{attempted} arms behaved "
          f"(one per ALTERNATIVE, not one per rule)")
    if blind:
        print("REFUSE: these arms did not behave:")
        for b in blind:
            print(f"  {b}")
        return 2

    missing = check_reader(face)
    print(f"PLANT CONTROL: {len(RULES) + 1 - len(missing)}/{len(RULES) + 1} "
          f"rules recover their own plant from the face itself")
    if missing:
        print("REFUSE: these rules cannot recover a plant placed in the face: "
              + "; ".join(missing))
        return 2

    # ------------------------------------------------ the tense rule, by beat
    # The coverage line is printed BEFORE the hits and is not decoration. The
    # only way to sweep clean under a stage-keyed rule is to declare every block
    # STATIC, and this is where that would be visible; `check_coverage` then
    # refuses below a floor on the tense-carrying share.
    src = SHEET.read_text(encoding="utf-8")
    cov = coverage(src, STAGE_MAP)
    print(f"\nBEAT COVERAGE: {cov['RUNNING']} words in running beats, "
          f"{cov['RESULTS']} in results beats, {cov['STATIC']} static")
    emptied = check_coverage(src, STAGE_MAP)
    if emptied:
        for p in emptied:
            print(f"REFUSE: {p}")
        return 2

    tense = tense_sweep(src, STAGE_MAP, face)
    hits = sweep(face)
    print(f"\nFACE: {len(face.split())} words read from the compiled sheet")
    print(f"FACE HITS: {len(hits)}")
    for name, ctx in hits:
        print(f"  [{name}] {ctx}")
    print(f"TENSE HITS: {len(tense)} "
          f"({sum(1 for h in tense if h.on_face)} reach the face, "
          f"{sum(1 for h in tense if not h.on_face)} source-only)")
    for h in tense:
        mark = "" if h.on_face else "  [SOURCE-ONLY: doubt, not proof of absence]"
        print(f"  [{STAGE_NAMES[h.stage]}] {h.rule}: {h.matched!r}{mark}"
              f"\n      ...{h.context}...")
    hits = hits + [(h.rule, h.matched) for h in tense]
    # Twenty minutes must be present, with its basis, or the owner's 03:45Z
    # order is not carried out. Absence is a failure, not a pass.
    if "20 minutes" not in face:
        print("\nFACE HITS: the twenty-minute runtime is missing from the face")
        return 1
    print("\nok  the twenty-minute runtime is on the face")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
