#!/usr/bin/env python3
"""Sweep the RENDERED FACE of the Act D multipoint-optimisation sheet.

Sibling of `check_actD_sheet_face.py`, which does the same job for the
reference-wing sheet.  THE SHARED RULES ARE IMPORTED FROM THAT MODULE RATHER
THAN COPIED, so the two sheets cannot drift apart on what counts as internal
information, a replay word, a struck phrase or past tense.

TWO OF THAT MODULE'S RULES DO NOT TRANSFER, AND THE REASON IS STATED HERE
RATHER THAN LEFT TO BE INFERRED.  Each is REPLACED, never merely dropped.

  1. `never-claim words: converged / optimum`.  That ban exists because the
     reference-wing optimiser printed NO convergence statement, so the word
     would have been a claim the run did not support.  THIS run's optimiser
     printed its own: `Optimal Solution Found.`, against its own registered
     tolerance.  The frozen grade file's `forbidden_readings` forbids exactly
     one thing here, and it is narrower than a ban: *"using the word
     `converged` of a run whose optimiser printed no convergence statement"*.
     So the rule below is CONDITIONAL: the word is admissible only while the
     optimiser's own terminal statement is on the same face.  Remove the
     statement and the word becomes a violation again.

  2. `the sixty-minute forms her order removes`.  The 20-minute display figure
     was ordered against a 3,601 s figure on the reference-wing act.  This act
     measures 851 wall s, which is 14.2 minutes, so its honest figure is
     already under twenty.  The rule below therefore hunts the OPPOSITE
     failure: a twenty-minute figure asserted as THIS run's elapsed time would
     be a number this run did not produce.  Whether the owner intends the
     20-minute display figure to extend to this act is referred upward and is
     not decided by this script; if it is extended, this rule is the one to
     change, and it is written so that the change is visible.

ONE RULE IS NEW AND BELONGS TO THIS ITEM ALONE.  Lift is UNCONSTRAINED here and
it moved a long way, so the grade file forbids *"quoting the weighted-drag
reduction without CL_baseline and CL_final beside it"*.  That forbidden reading
is enforced below as an executable check rather than left as prose: the drag
reduction figure may appear on the face only while both lift columns appear on
it too.

THE PLANTED CONTROL IS THE POINT (CLAUDE.md rule 3).  Every rule, imported or
new, is planted into a copy of the extracted text and must be recovered; a rule
that cannot see its own plant makes this script REFUSE with exit 2 rather than
report a clean face.

    python3 docs/dafoam/demo/check_actD_multipoint_sheet_face.py
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_actD_sheet_face import (  # noqa: E402  shared, never copied
    PAST, PAST_PLANT, PAST_PLANT_AMBIGUOUS_FIRES, PAST_PLANT_AMBIGUOUS_QUIET,
    RULES as REFERENCE_RULES, STRUCK, STRUCK_PLANT, _is_past,
)


def render(tex: Path, workdir: Path) -> str:
    """Compile the sheet and return the text a viewer sees.

    NOT the imported `render`.  That one copies the source into a scratch
    directory, which is right for a sheet whose figures are all native LaTeX
    drawings; THIS sheet also carries a grid figure read from the run's own
    mesh, and a copied source cannot resolve it.  So the compile happens in
    the sheet's own directory with the output diverted, which leaves the
    working tree clean and still finds the figure.
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

SHEET = Path(__file__).resolve().parent / "ACT_D_multipoint_optimisation_sheet.tex"

#: The two reference-wing rules replaced above, named so the drop is visible.
NOT_TRANSFERRED = {"never-claim words: converged / optimum",
                   "the sixty-minute forms her order removes"}

SHARED_RULES = [r for r in REFERENCE_RULES if r[0] not in NOT_TRANSFERRED]
if len(SHARED_RULES) != len(REFERENCE_RULES) - 2:
    raise SystemExit("REFUSE: the two replaced rules are not both present "
                     "upstream; this script's reasoning no longer matches it")

OWN_RULES: list[tuple[re.Pattern, str]] = [
    ("a twenty-minute figure this run did not produce",
     re.compile(r"\b(20|twenty)\s*min", re.I),
     "the whole run is 20 minutes on one core"),
]

#: The optimiser's own terminal statement.  While this is on the face the word
#: `converged` is earned; without it the word is a violation.
TERMINAL_STATEMENT = "Optimal Solution Found."
CONVERGED = re.compile(r"\b(converged|optimum)\b", re.I)

#: The drag reduction may not travel without both lift columns.
DRAG_REDUCTION = re.compile(r"\b16\.2\s*(?:per cent|%)", re.I)
LIFT_START = re.compile(r"C\s*L\s*start", re.I)
LIFT_FINAL = re.compile(r"C\s*L\s*final", re.I)


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

    # This item's own forbidden reading, made executable.
    if DRAG_REDUCTION.search(text) and not (LIFT_START.search(text)
                                            and LIFT_FINAL.search(text)):
        hits.append(("the drag reduction is quoted without the lift columns",
                     "16.2 per cent appears; a lift column does not"))
    return hits


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        face = render(SHEET, Path(td))

    # ------------------------------------------------------------- controls
    blind: list[str] = []
    for name, pat, plant in SHARED_RULES + OWN_RULES:
        if not pat.search(plant):
            blind.append(name)
    if not sweep(PAST_PLANT):
        blind.append("past tense")
    if not sweep(PAST_PLANT_AMBIGUOUS_FIRES):
        blind.append("past tense (ambiguous participle, past use)")
    if sweep(PAST_PLANT_AMBIGUOUS_QUIET):
        blind.append("past tense (ambiguous participle, present passive "
                     "wrongly flagged)")
    if not any(p.lower() in STRUCK_PLANT.lower() for p in STRUCK):
        blind.append("struck by name at 03:10Z")
    # The conditional rule, driven in BOTH directions.  One-sided would let a
    # rule that never fires, or one that always fires, pass as if it worked.
    if not sweep("the optimiser converged on its own tolerance"):
        blind.append("converged with no terminal statement (must fire)")
    if sweep("the optimiser converged. " + TERMINAL_STATEMENT):
        blind.append("converged beside the terminal statement (must stay quiet)")
    # The forbidden-reading rule, driven in both directions too.
    if not sweep("drag falls 16.2 per cent"):
        blind.append("drag reduction without the lift columns (must fire)")
    if sweep("drag falls 16.2 per cent. CL start CL final " + TERMINAL_STATEMENT):
        blind.append("drag reduction beside the lift columns (must stay quiet)")

    total = len(SHARED_RULES) + len(OWN_RULES) + 8
    print(f"PLANT CONTROL: {total - len(blind)}/{total} rule arms behaved")
    if blind:
        print("REFUSE: these rules cannot see a planted violation, or fire on "
              "a clean string: " + "; ".join(blind))
        return 2

    planted = face + "\n" + "\n".join(
        [p for _n, _pat, p in SHARED_RULES + OWN_RULES] + [PAST_PLANT, STRUCK_PLANT])
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

    # Presence checks.  Absence of the honesty material is a failure, not a
    # pass: a sheet that simply omits the lift columns would sweep clean.
    missing = []
    if TERMINAL_STATEMENT not in face:
        missing.append("the optimiser's own terminal statement")
    if not (LIFT_START.search(face) and LIFT_FINAL.search(face)):
        missing.append("both lift columns")
    if "14.2 minutes" not in face:
        missing.append("this run's own elapsed figure, 14.2 minutes")
    if missing:
        print("\nFACE HITS: missing from the face: " + "; ".join(missing))
        return 1
    print("\nok  terminal statement, both lift columns and this run's own "
          "elapsed figure are all on the face")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
