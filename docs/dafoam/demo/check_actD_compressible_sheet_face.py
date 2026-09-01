#!/usr/bin/env python3
"""Sweep the RENDERED FACE of the Act D COMPRESSIBLE multipoint sheet (D19M).

Third sibling of `check_actD_sheet_face.py` (reference wing) and
`check_actD_multipoint_sheet_face.py` (SO-3, incompressible).  THE SHARED RULE
MATERIAL IS IMPORTED FROM THE FIRST OF THOSE RATHER THAN COPIED, so the sheets
cannot drift apart on what counts as internal information, a replay word, a
struck phrase or past tense.

WHY THIS FILE EXISTS RATHER THAN A FLAG ON THE SO-3 CHECKER.  The two items
differ in the one place a checker cannot be parameterised over: what the face
must SAY.  SO-3's item verdict is PASS and its sheet claims a verified
gradient.  D19M's is GATE REACHED on both rows, capped by a ceiling REGISTERED
BEFORE THE RUN, and its sheet must therefore carry, ON THE RENDERED FACE, three
statements SO-3's sheet must not carry.  A shared checker with a mode flag
would let a mode be selected wrongly and would sweep the wrong sheet clean.

TWO IMPORTED RULES DO NOT TRANSFER, for exactly the reasons the SO-3 checker
gives, and each is REPLACED rather than dropped:

  1. `never-claim words: converged / optimum`.  THIS run's optimiser prints its
     own terminal statement, `Optimal Solution Found.`, against its own
     registered iteration cap of 40, which it does not reach.  So the rule
     below is CONDITIONAL: the word is admissible only while that statement is
     on the same face.  Remove the statement and the word is a violation again.

  2. `the sixty-minute forms her order removes`.  The 20-minute display figure
     was ordered against a 3,601 s figure on the reference-wing act.  This
     act's own PATCHED path measures 1,059 wall s, 17.7 minutes, already under
     twenty.  The rule below therefore hunts the OPPOSITE failure: a
     twenty-minute figure asserted as THIS run's elapsed time.

THREE RULES ARE NEW AND BELONG TO THIS ITEM.  Each is enforced on the RENDERED
FACE and each carries a planted control that makes it go red, in BOTH
directions.  A check that has never been shown able to fire is not a check.

  A. THE CL COLLAPSE TRAVELS WITH THE DRAG FIGURE, AND `TRAVELS` MEANS IN THE
     SAME FRAME, NOT MERELY ON THE SAME PAGE.  The frozen grade file states the
     rule itself at `gates.G-OPT9.<ROW>._cl_travels`: *"THE THREE-CL TRIPLE
     therefore travels with every weighted-drag number this item publishes.  A
     reduction at unstated lift is not a reportable number."*  This is checked
     THREE ways, because the weakest of the three is the one the SO-3 checker
     currently has on its own:
       A1  PRESENCE OF THE COLLAPSE ITSELF, not of a column header.  A sheet
           can print `CL start` and `CL final` over three positive numbers and
           satisfy a header check while hiding the collapse.  So the NEGATIVE
           final lift value must be on the face.
       A2  PROXIMITY.  Every occurrence of the drag figure must have lift
           within a character window of the extracted layout.  This is what
           makes "same frame" executable.
       A3  COLUMN HEADERS, the SO-3 rule, kept as the weakest of the three
           rather than replaced by them.
     A2 IS THE ONE WITH A HONEST LIMIT AND IT IS STATED HERE RATHER THAN LEFT
     TO BE DISCOVERED: `pdftotext -layout` interleaves adjacent columns line by
     line, so a window on the extracted text is a proxy for visual proximity
     and not a proof of it.  It is strictly stronger than no proximity check at
     all and strictly weaker than reading the page geometry.  The window is
     named as a constant so the strength of the claim is visible.

  B. THE CEILING IS ON THE FACE.  D19M cannot publish PASS on any row: the
     compressible gradient it spends has no graded verdict of its own, and one
     of its eight shape controls is a REGISTERED NON-RESULT excluded by name.
     Those are not footnote material and their ABSENCE is a failure, not a
     clean sweep.  Three clauses are required and each is planted by DELETION
     from a copy of the face, which is the only mutant that tests a presence
     rule.

  C. THE HARNESS-SOUND FLOOR IS SAID WHERE THE NUMBER IS.  Every agreement
     figure in Table 4 lies below the 2.5 to 5 % harness-sound floor, so the
     face must say the floor is REPORTED and never used as a limit.

WHAT THIS SCRIPT DELIBERATELY DOES NOT DO.  It does not check the numbers
against the grade file.  That is the sheet's provenance block's job and a
separate reader's; this script checks what a VIEWER can see.  Conflating the
two would let a face that is honest about a wrong number sweep clean.

    python3 docs/dafoam/demo/check_actD_compressible_sheet_face.py
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_actD_sheet_face import (  # noqa: E402  shared, never copied
    RULES as REFERENCE_RULES, STRUCK,
)
from demo_stages import (  # noqa: E402  the tense rule, keyed to the beat
    RESULTS, STATIC_REGION, CONVERGENCE_STUDY, Region, STAGE_NAMES,
    tense_sweep, coverage,
    check_coverage, check_plants as check_tense_plants,
)

# AMENDED 2026-09-01 (20:30Z DIRECTIVE, `cfcf766f`).  `PAST` and `_is_past` are
# no longer imported and no longer applied here.  The shooting protocol restores
# *"Present and progressive tense while running; past tense for results"* and
# supersedes the flat 04:20Z "no past tense" that this file implemented, so a
# global past-tense sweep over this sheet's face now flags COMPLIANT results
# prose and pushes an author toward the present tense, which is itself now the
# violation.  Tense is swept by beat instead; the regime table lives in
# `demo_stages.py` and is the only thing a further revision has to touch.
#
# THIS SHEET'S OWN MEASURED POSITION UNDER THE RESTORED RULE: 0 past-tense hits
# under the flat rule, 2 present-run-narration hits under this one.  The
# direction of failure inverted.

#: WHICH BEAT EACH BLOCK IS.  Nothing here says what tense that implies.
STAGE_MAP = [
    Region(r"\\textbf\{Solver: DAFoam \\texttt\{DARhoSimpleFoam\}", RESULTS,
           "the solved-case banner"),
    Region(r"\\textbf\{What this sheet does not claim", STATIC_REGION,
           "the pre-registered ceiling, fixed before the run"),
    Region(r"\\textbf\{What the optimiser does, and what it costs you\}",
           STATIC_REGION, "framing: what the method is, timeless"),
    Region(r"\\textbf\{What this run establishes\.\}", RESULTS,
           "what this run established"),
    Region(r"\\textbf\{Table 1\. Operating condition and grid\.\}",
           STATIC_REGION, "assumptions: quantities with units"),
    Region(r"\\textbf\{Figure 1\. The grid the section is solved on\.\}",
           STATIC_REGION, "figure note"),
    Region(r"\\textbf\{Table 2\. The result\.", RESULTS, "the result table"),
    Region(r"\\textbf\{Figure 2\. Drag and lift at three angles", STATIC_REGION,
           "figure note"),
    Region(r"\\textbf\{Table 3\. The optimiser\.\}", RESULTS, "optimiser table"),
    # THE ONE ARGUABLE HIT IN EIGHTEEN, LEFT FIRING ON PURPOSE. This block's
    # "where the estimate stops moving" describes a PLATEAU -- a property of the
    # step sweep -- rather than a run event, so whether the restored rule reaches
    # it is genuinely open. It is NOT reworded: an honestly-labelled borderline
    # is worth more than a confident call, and silencing it by edit would hide
    # the judgement instead of recording it.
    Region(r"\\textbf\{Table 4\. The gradient, checked at the final shape\.\}",
           RESULTS, "gradient table; carries the one arguable hit"),
    Region(r"\\textbf\{Table 5\. Instrument checks\.\}", RESULTS,
           "instrument checks"),
    Region(r"\\textbf\{Table 6\. Compute", RESULTS, "compute"),
    Region(r"\\textbf\{Uncertainty\}", RESULTS, "uncertainty channels"),
    Region(r"\\textbf\{Read this before you use the numbers\}", RESULTS,
           "limitations"),
    # STAGE 8, the one running beat on this sheet. Sanaa's screen-8 rule is that
    # the convergence study is shown done or underway and NEVER as absent, and
    # her second form is present progressive sitting inside a results list. It
    # is true rather than a device: A1WR is live and A2-GC L1 cap-stopped with
    # L2 and L3 owed to a successor. No band is claimed and no study is called
    # finished.
    Region(r"One grid, \$4\\,032\$ cells, one core\. The grid convergence",
           CONVERGENCE_STUDY, "the grid convergence study, underway"),
    Region(r"Three angles between \$2\.787\$", RESULTS, "limitations resume"),
    Region(r"\\textbf\{Assumed, not measured\}", STATIC_REGION,
           "assumptions: quantities with units"),
    Region(r"\\rolesig\{Lead Engineer\.\}", RESULTS,
           "the roles, delivering findings"),
]

SHEET = (Path(__file__).resolve().parent
         / "ACT_D_compressible_multipoint_sheet.tex")

# ---------------------------------------------------------------------------
# Plants for the imported rules.  WRITTEN HERE RATHER THAN IMPORTED, for the
# reason the SO-3 checker gives: a plant is a statement of what a rule must
# catch, and importing it from the module that owns the pattern would check a
# pattern against something derived from that same pattern.
STRUCK_PLANT = "Solver: none on this request"


def _plants(rule) -> list[str]:
    """Every plant a shared rule carries, whichever shape it is written in."""
    if len(rule) != 3:
        raise SystemExit("REFUSE: a shared rule is not a 3-tuple; this script "
                         "cannot plant it and will not sweep with it")
    name, pat, plant = rule
    if not isinstance(name, str) or not hasattr(pat, "finditer"):
        raise SystemExit("REFUSE: a shared rule is not (name, pattern, plant)")
    if isinstance(plant, str):
        return [plant]
    if isinstance(plant, (list, tuple)) and plant and all(
            isinstance(x, str) for x in plant):
        return list(plant)
    raise SystemExit("REFUSE: a shared rule's plant is neither a string nor a "
                     "non-empty list of strings")


def render(tex: Path, workdir: Path) -> str:
    """Compile the sheet and return the text a viewer sees.

    The compile happens in the sheet's own directory with the output diverted,
    which leaves the working tree clean and still resolves the grid figure.
    """
    r = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode",
         "-output-directory", str(workdir), tex.name],
        cwd=tex.parent, capture_output=True, text=True)
    pdf = workdir / (tex.stem + ".pdf")
    if r.returncode != 0 or not pdf.exists():
        raise SystemExit(f"REFUSE: pdflatex rc={r.returncode}, no face to read")
    out = workdir / "face.txt"
    subprocess.run(["pdftotext", "-layout", str(pdf), str(out)], check=True)
    return out.read_text(encoding="utf-8", errors="replace")


#: The two reference-wing rules replaced above, named so the drop is visible.
NOT_TRANSFERRED = {"never-claim words: converged / optimum",
                   "the sixty-minute forms her order removes"}

SHARED_RULES = [r for r in REFERENCE_RULES if r[0] not in NOT_TRANSFERRED]
if len(SHARED_RULES) != len(REFERENCE_RULES) - 2:
    raise SystemExit("REFUSE: the two replaced rules are not both present "
                     "upstream; this script's reasoning no longer matches it")

OWN_RULES: list[tuple[str, re.Pattern, str]] = [
    ("a twenty-minute figure this run did not produce",
     re.compile(r"\b(20|twenty)\s*min", re.I),
     "the whole run is 20 minutes on one core"),
]

#: The optimiser's own terminal statement.  While this is on the face the word
#: `converged` is earned; without it the word is a violation.
TERMINAL_STATEMENT = "Optimal Solution Found."
CONVERGED = re.compile(r"\b(converged|optimum)\b", re.I)

# ------------------------------------------------------------ rule A --------
#: This item's weighted-drag reduction, to the digits the sheet prints.
DRAG_REDUCTION = re.compile(r"\b25\.985\b")
#: THE COLLAPSE ITSELF.  `pdftotext` may render a LaTeX minus as ASCII `-` or
#: as U+2212, and may or may not put a space after it, so all four forms are
#: admitted.  This is the value at the LOWEST operating point, the one that
#: goes negative; a sheet that prints only the two positive final lifts does
#: not satisfy it.
CL_NEGATIVE = re.compile(r"[-−–]\s?0\.157")
#: Lift, in any form a viewer would recognise on this face.
LIFT_ANY = re.compile(r"\blift\b|\bC\s*L\b", re.I)
#: The SO-3 column-header rule, kept as the weakest of the three arms.
LIFT_START = re.compile(r"C\s*L\s*start", re.I)
LIFT_FINAL = re.compile(r"C\s*L\s*final", re.I)
#: HOW FAR APART "IN THE SAME FRAME" IS ALLOWED TO BE, in characters of the
#: `-layout` extraction.  Named rather than inlined because it IS the strength
#: of arm A2 and a reader is entitled to see it.
PROXIMITY_WINDOW = 300

# ------------------------------------------------------------ rule B --------
#: The ceiling, as three clauses that must each be on the face.  These are
#: matched loosely on their load-bearing words rather than on an exact
#: sentence, so that the sheet's prose can be edited without silently losing
#: the claim -- and tightly enough that deleting the claim is caught.
CEILING_CLAUSES: list[tuple[str, re.Pattern]] = [
    ("the gradient carries no separate check of its own",
     re.compile(r"no separate check of its own", re.I)),
    ("one control is set aside by name before the run",
     re.compile(r"set aside by name before (?:this|the) run", re.I)),
    ("the size of the improvement grades nothing",
     re.compile(r"grades nothing here|never what this run stands on", re.I)),
]

# ------------------------------------------------------------ rule C --------
#: TWO INDEPENDENT ANCHORS, NOT ONE PHRASE, AND THE REASON IS MEASURED.  A
#: single regex spanning "two and a half to five per cent ... never used as a
#: limit" fails on the real face even when the sentence IS there, because
#: `pdftotext -layout` interleaves the neighbouring column's lines between the
#: two halves of the sentence.  The honest check is therefore that both halves
#: are on the face, reported separately so a reader sees WHICH half is missing.
#: This is weaker than a same-sentence check and is labelled as such rather
#: than dressed up: it catches a face that drops either half, and it would not
#: catch a face that said both halves about different things.
HARNESS_FLOOR_CLAUSES: list[tuple[str, re.Pattern]] = [
    ("the harness floor range, two and a half to five per cent",
     re.compile(r"two and a half to five per cent", re.I)),
    ("that the floor is never used as a limit",
     re.compile(r"never used as a limit", re.I)),
]


def cl_collapse_hits(text: str) -> list[tuple[str, str]]:
    """Arms A1, A2 and A3, in one place so the SO-3 checker can adopt them.

    Returns a list of (rule name, context) pairs; empty means the face is
    clean on this item's own forbidden reading.
    """
    hits: list[tuple[str, str]] = []
    occurrences = list(DRAG_REDUCTION.finditer(text))
    if not occurrences:
        return hits
    # A1 -- the collapse, not a column header.
    if not CL_NEGATIVE.search(text):
        hits.append(("the drag reduction is quoted without the lift collapse",
                     "the reduction figure appears; the negative final lift "
                     "value does not"))
    # A3 -- the column headers, the weakest arm, kept.
    if not (LIFT_START.search(text) and LIFT_FINAL.search(text)):
        hits.append(("the drag reduction is quoted without the lift columns",
                     "the reduction figure appears; a lift column does not"))
    # A2 -- proximity, occurrence by occurrence.
    for m in occurrences:
        a = max(0, m.start() - PROXIMITY_WINDOW)
        b = min(len(text), m.end() + PROXIMITY_WINDOW)
        window = text[a:b]
        if not LIFT_ANY.search(window):
            ctx = " ".join(text[max(0, m.start() - 60):m.end() + 60].split())
            hits.append(("the drag reduction stands alone in its own frame",
                         f"...{ctx}..."))
    return hits


def sweep(text: str) -> list[tuple[str, str]]:
    hits: list[tuple[str, str]] = []

    def record(name: str, m: re.Match) -> None:
        a, b = max(0, m.start() - 40), min(len(text), m.end() + 40)
        hits.append((name, f"{m.group(0)!r} in ...{' '.join(text[a:b].split())}..."))

    for name, pat, _plant in SHARED_RULES:
        for m in pat.finditer(text):
            record(name, m)
    for name, pat, _plant in OWN_RULES:
        for m in pat.finditer(text):
            record(name, m)
    # No tense rule here any more: a face offset cannot be resolved to a beat.
    # See the amendment note at the top and `tense_sweep` in `main`.
    low = text.lower()
    for phrase in STRUCK:
        if phrase.lower() in low:
            hits.append(("struck by name at 03:10Z", phrase))

    # Conditional rule: `converged` is earned only beside the statement.
    if TERMINAL_STATEMENT not in text:
        for m in CONVERGED.finditer(text):
            record("converged claimed with no terminal statement on the face", m)

    hits.extend(cl_collapse_hits(text))
    return hits


def missing_from(text: str) -> list[str]:
    """Presence checks.  ABSENCE OF THE HONESTY MATERIAL IS A FAILURE.

    A sheet that simply omits the ceiling, the lift columns or the terminal
    statement would sweep clean under `sweep` alone, which is exactly how a
    face gets quietly emptied of the thing it exists to say.
    """
    missing: list[str] = []
    if TERMINAL_STATEMENT not in text:
        missing.append("the optimiser's own terminal statement")
    if not (LIFT_START.search(text) and LIFT_FINAL.search(text)):
        missing.append("both lift columns")
    if not CL_NEGATIVE.search(text):
        missing.append("the negative final lift value, the collapse itself")
    if "17.7 minutes" not in text:
        missing.append("this run's own elapsed figure, 17.7 minutes")
    for name, pat in CEILING_CLAUSES:
        if not pat.search(text):
            missing.append("the ceiling clause: " + name)
    for name, pat in HARNESS_FLOOR_CLAUSES:
        if not pat.search(text):
            missing.append("the harness floor clause: " + name)
    return missing


#: Neutral filler for the proximity control.  It must be long enough to push
#: lift out of the window and must itself trip no rule -- no past-tense verb,
#: no struck phrase, no path, no internal token, no number that reads as a
#: minute figure.
_FILLER = ("the section sits in the tunnel of the mind and the grid around it "
           "holds its shape while the solver turns over each cell in order ")


def _pad(core: str) -> str:
    """`core` with enough neutral text on both sides to clear the window."""
    n = (PROXIMITY_WINDOW // len(_FILLER)) + 2
    wing = _FILLER * n
    return wing + core + wing


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        face = render(SHEET, Path(td))

    # ------------------------------------------------------------- controls
    blind: list[str] = []
    #: EVERY ARM THAT ACTUALLY RUNS, REGISTERED AS IT RUNS. The published count
    #: used to be a hand-written constant sitting beside the thing it counted
    #: -- ``+ 8 + 8 + len(...) + len(...) + 1`` -- and it had already drifted:
    #: it published 61 arms where 59 exist, because the first ``8`` was 6.
    #: Standalone arms were 6 (past tense, two ambiguous-participle directions,
    #: struck-by-name, and the conditional rule in both directions), not 8; the
    #: three tense arms among them moved into `demo_stages` with the 20:30Z
    #: amendment and came back as one arm per alternative per REGIME, which is
    #: exactly why the total is derived and not written down.
    #: A number nobody measured has no place in a published control, and a
    #: constant beside its subject is free to drift again the moment anyone
    #: adds an arm, with nothing able to detect it. So the total is DERIVED:
    #: it is the length of this register, and it cannot disagree with reality
    #: because it IS reality.
    arms: list[str] = []

    def arm(name: str, behaved: bool) -> None:
        """Run one control arm: count it, and record it if it misbehaved."""
        arms.append(name)
        if not behaved:
            blind.append(name)

    for rule in SHARED_RULES + OWN_RULES:
        name, pat = rule[0], rule[1]
        for plant in _plants(rule):
            arm("%s [%s]" % (name, plant[:40]), bool(pat.search(plant)))
    # THE TENSE ARMS RUN IN `demo_stages` AND ARE COUNTED HERE, and the count
    # is DERIVED rather than written down -- this file is the one that published
    # 61 arms where 59 existed, and a hand-written constant beside the thing it
    # counts is right until somebody edits the thing.
    t_ok, t_attempted, t_blind = check_tense_plants()
    for i in range(t_attempted - len(t_blind)):
        arm(f"tense arm {i} (demo_stages, both directions)", True)
    for _name in t_blind:
        arm(_name, False)
    arm("struck by name at 03:10Z",
        any(p.lower() in STRUCK_PLANT.lower() for p in STRUCK))
    # The conditional rule, driven in BOTH directions.
    arm("converged with no terminal statement (must fire)",
        bool(sweep("the optimiser converged on its own tolerance")))
    arm("converged beside the terminal statement (must stay quiet)",
        not sweep("the optimiser converged. " + TERMINAL_STATEMENT))

    # --- rule A, all three arms, each in both directions --------------------
    # A1: the collapse value missing while the reduction is quoted.
    a1_red = "drag falls 25.985 per cent. CL start CL final, lift 0.072"
    arm("A1 lift collapse absent (must fire)",
        any(n.endswith("without the lift collapse")
            for n, _ in cl_collapse_hits(a1_red)))
    a1_green = a1_red + " and CL goes to -0.157 at the lowest angle"
    arm("A1 lift collapse present (must stay quiet)",
        not any(n.endswith("without the lift collapse")
                for n, _ in cl_collapse_hits(a1_green)))
    # A1 again against the OTHER minus glyph pdftotext may emit.
    arm("A1 does not see a U+2212 minus (must fire on both glyphs)",
        bool(CL_NEGATIVE.search("CL goes to −0.157 at the lowest angle")))
    # A2: the reduction alone in its own frame.
    a2_red = _pad("the objective falls 25.985 per cent in ten majors")
    arm("A2 proximity (must fire)",
        any(n.endswith("stands alone in its own frame")
            for n, _ in cl_collapse_hits(a2_red)))
    a2_green = _pad("the objective falls 25.985 per cent and lift goes to "
                    "-0.157 with it")
    arm("A2 proximity with lift in frame (must stay quiet)",
        not any(n.endswith("stands alone in its own frame")
                for n, _ in cl_collapse_hits(a2_green)))
    # A3: the column headers.
    a3_red = "drag falls 25.985 per cent and CL goes to -0.157"
    arm("A3 lift columns (must fire)",
        any(n.endswith("without the lift columns")
            for n, _ in cl_collapse_hits(a3_red)))
    arm("A3 lift columns present (must stay quiet)",
        not any(n.endswith("without the lift columns")
                for n, _ in cl_collapse_hits(a3_red + " CL start CL final")))
    # A, quiet control: no reduction figure at all means no arm may fire.
    arm("rule A fires with no reduction figure on the face",
        not cl_collapse_hits("a sheet that quotes no reduction figure at all"))

    # --- rule B, by DELETION from the face, the only mutant a presence rule
    #     can have.  Each clause is cut in turn and must go missing.
    # A DEAD LEVER REMOVED. This loop carried a second ``if`` whose body was a
    # bare ``continue`` as the last statement in the block: it read as a guard
    # and did nothing at all. Whether a clause is genuinely missing from the
    # unmutated face is the real sweep's business below, not a blind-rule
    # question, so the branch is gone rather than left looking load-bearing.
    for name, pat in CEILING_CLAUSES:
        arm("ceiling clause not recovered by deletion: " + name,
            ("the ceiling clause: " + name) in missing_from(pat.sub("", face)))
    # --- rule C, by deletion too, one clause at a time.
    for name, pat in HARNESS_FLOOR_CLAUSES:
        arm("harness floor clause not recovered by deletion: " + name,
            ("the harness floor clause: " + name) in missing_from(
                pat.sub("", face)))
    # --- the collapse presence check, by deletion.
    arm("lift collapse not recovered by deletion from the face",
        "the negative final lift value, the collapse itself" in missing_from(
            CL_NEGATIVE.sub("", face)))

    total = len(arms)
    print(f"PLANT CONTROL: {total - len(blind)}/{total} rule arms behaved")
    if blind:
        print("REFUSE: these rules cannot see a planted violation, or fire on "
              "a clean string: " + "; ".join(blind))
        return 2

    every_plant = [p for rule in SHARED_RULES + OWN_RULES for p in _plants(rule)]
    planted = face + "\n" + "\n".join(every_plant + [STRUCK_PLANT])
    if len(sweep(planted)) <= len(sweep(face)):
        print("REFUSE: planting violations into the face changed nothing; "
              "the reader is not reading the face")
        return 2
    print("PLANT CONTROL: planted violations are recovered from the face itself")

    # ------------------------------------------------ the tense rule, by beat
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

    missing = missing_from(face)
    if missing:
        print("\nFACE HITS: missing from the face: " + "; ".join(missing))
        return 1
    presence = ("the ceiling, the lift collapse beside every drag figure, the "
                "harness floor, the terminal statement and this run's own "
                "elapsed figure are all on the face")
    if hits:
        # THE LAST LINE OF A FAILING RUN MAY NOT BE A GREEN WORD. This printed
        # a bare "ok" and then exited 1: the sentence was true and scoped to
        # the presence checks, but a reader skimming the tail saw "ok" on a run
        # that had already listed its hits. The scope is now named in the line
        # itself and the exit is stated beside it.
        print(f"\nPRESENCE CHECKS ONLY, and this run still exits 1: {presence}. "
              f"The sweep found {len(hits)} hit(s), listed above.")
        return 1
    print("\nok  " + presence)
    return 0


if __name__ == "__main__":
    sys.exit(main())
