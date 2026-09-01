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
    PAST, RULES as REFERENCE_RULES, STRUCK, _is_past,
)

SHEET = (Path(__file__).resolve().parent
         / "ACT_D_compressible_multipoint_sheet.tex")

# ---------------------------------------------------------------------------
# Plants for the imported rules.  WRITTEN HERE RATHER THAN IMPORTED, for the
# reason the SO-3 checker gives: a plant is a statement of what a rule must
# catch, and importing it from the module that owns the pattern would check a
# pattern against something derived from that same pattern.
PAST_PLANT = "the flow solve diverged and the optimiser was stopped"
PAST_PLANT_AMBIGUOUS_FIRES = "the optimiser completed ten majors"
PAST_PLANT_AMBIGUOUS_QUIET = "the iteration cap is not in force"
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
    for m in PAST.finditer(text):
        if _is_past(text, m):
            record("past tense", m)
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
    for rule in SHARED_RULES + OWN_RULES:
        name, pat = rule[0], rule[1]
        for plant in _plants(rule):
            if not pat.search(plant):
                blind.append("%s [%s]" % (name, plant[:40]))
    if not sweep(PAST_PLANT):
        blind.append("past tense")
    if not sweep(PAST_PLANT_AMBIGUOUS_FIRES):
        blind.append("past tense (ambiguous participle, past use)")
    if sweep(PAST_PLANT_AMBIGUOUS_QUIET):
        blind.append("past tense (ambiguous participle, present passive "
                     "wrongly flagged)")
    if not any(p.lower() in STRUCK_PLANT.lower() for p in STRUCK):
        blind.append("struck by name at 03:10Z")
    # The conditional rule, driven in BOTH directions.
    if not sweep("the optimiser converged on its own tolerance"):
        blind.append("converged with no terminal statement (must fire)")
    if sweep("the optimiser converged. " + TERMINAL_STATEMENT):
        blind.append("converged beside the terminal statement (must stay quiet)")

    # --- rule A, all three arms, each in both directions --------------------
    # A1: the collapse value missing while the reduction is quoted.
    a1_red = "drag falls 25.985 per cent. CL start CL final, lift 0.072"
    if not any(n.endswith("without the lift collapse")
               for n, _ in cl_collapse_hits(a1_red)):
        blind.append("A1 lift collapse absent (must fire)")
    a1_green = a1_red + " and CL goes to -0.157 at the lowest angle"
    if any(n.endswith("without the lift collapse")
           for n, _ in cl_collapse_hits(a1_green)):
        blind.append("A1 lift collapse present (must stay quiet)")
    # A1 again against the OTHER minus glyph pdftotext may emit.
    if not CL_NEGATIVE.search("CL goes to −0.157 at the lowest angle"):
        blind.append("A1 does not see a U+2212 minus (must fire on both glyphs)")
    # A2: the reduction alone in its own frame.
    a2_red = _pad("the objective falls 25.985 per cent in ten majors")
    if not any(n.endswith("stands alone in its own frame")
               for n, _ in cl_collapse_hits(a2_red)):
        blind.append("A2 proximity (must fire)")
    a2_green = _pad("the objective falls 25.985 per cent and lift goes to "
                    "-0.157 with it")
    if any(n.endswith("stands alone in its own frame")
           for n, _ in cl_collapse_hits(a2_green)):
        blind.append("A2 proximity with lift in frame (must stay quiet)")
    # A3: the column headers.
    a3_red = "drag falls 25.985 per cent and CL goes to -0.157"
    if not any(n.endswith("without the lift columns")
               for n, _ in cl_collapse_hits(a3_red)):
        blind.append("A3 lift columns (must fire)")
    if any(n.endswith("without the lift columns") for n, _ in cl_collapse_hits(
            a3_red + " CL start CL final")):
        blind.append("A3 lift columns present (must stay quiet)")
    # A, quiet control: no reduction figure at all means no arm may fire.
    if cl_collapse_hits("a sheet that quotes no reduction figure at all"):
        blind.append("rule A fires with no reduction figure on the face")

    # --- rule B, by DELETION from the face, the only mutant a presence rule
    #     can have.  Each clause is cut in turn and must go missing.
    for name, pat in CEILING_CLAUSES:
        cut = pat.sub("", face)
        if ("the ceiling clause: " + name) not in missing_from(cut):
            blind.append("ceiling clause not recovered by deletion: " + name)
        if ("the ceiling clause: " + name) in missing_from(face):
            continue  # reported by the real sweep below, not a blind rule
    # --- rule C, by deletion too, one clause at a time.
    for name, pat in HARNESS_FLOOR_CLAUSES:
        if ("the harness floor clause: " + name) not in missing_from(
                pat.sub("", face)):
            blind.append("harness floor clause not recovered by deletion: "
                         + name)
    # --- the collapse presence check, by deletion.
    if "the negative final lift value, the collapse itself" not in missing_from(
            CL_NEGATIVE.sub("", face)):
        blind.append("lift collapse not recovered by deletion from the face")

    total = (sum(len(_plants(r)) for r in SHARED_RULES + OWN_RULES)
             + 8 + 8 + len(CEILING_CLAUSES) + len(HARNESS_FLOOR_CLAUSES) + 1)
    print(f"PLANT CONTROL: {total - len(blind)}/{total} rule arms behaved")
    if blind:
        print("REFUSE: these rules cannot see a planted violation, or fire on "
              "a clean string: " + "; ".join(blind))
        return 2

    every_plant = [p for rule in SHARED_RULES + OWN_RULES for p in _plants(rule)]
    planted = face + "\n" + "\n".join(every_plant + [PAST_PLANT, STRUCK_PLANT])
    if len(sweep(planted)) <= len(sweep(face)):
        print("REFUSE: planting violations into the face changed nothing; "
              "the reader is not reading the face")
        return 2
    print("PLANT CONTROL: planted violations are recovered from the face itself")

    hits = sweep(face)
    print(f"\nFACE: {len(face.split())} words read from the compiled sheet")
    print(f"FACE HITS: {len(hits)}")
    for name, ctx in hits:
        print(f"  [{name}] {ctx}")

    missing = missing_from(face)
    if missing:
        print("\nFACE HITS: missing from the face: " + "; ".join(missing))
        return 1
    print("\nok  the ceiling, the lift collapse beside every drag figure, the "
          "harness floor, the terminal statement and this run's own elapsed "
          "figure are all on the face")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
