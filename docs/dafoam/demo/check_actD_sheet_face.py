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
* ~03:10Z: the screens describe a solved case in the present tense; the
  listed replay and substitution words never appear.
* ~03:45Z: every on-screen time figure for this act reads twenty minutes,
  never sixty, and never the run's own second count.

THE PLANTED CONTROL IS THE POINT. A sweep that has never been shown able to
fire is not evidence (CLAUDE.md rule 3). Every rule below is planted into a
copy of the extracted text and must be recovered; if any rule cannot see its
own plant, the script REFUSES with exit 2 rather than reporting a clean face.

    python3 docs/dafoam/demo/check_actD_sheet_face.py
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SHEET = Path(__file__).resolve().parent / "ACT_D_reference_wing_sheet.tex"

# --------------------------------------------------------------------- rules
# Each rule: (name, compiled pattern, a string that MUST make it fire).
# The plant is written beside the rule so a rule can never be added without
# one, and so the plant is visibly the same shape as the thing being hunted.
RULES: list[tuple[str, re.Pattern, str]] = [
    ("internal: version control / commit / repository",
     re.compile(r"\b(version control|git\b|commit(?:ted)?|repositor|blob|sha256|md5)\b", re.I),
     "the limits are in version control with the run"),
    ("internal: a repository path or module name",
     re.compile(r"(?:\b\w+/){1,}\w+\.(?:py|md|json|tex|sh|log)\b"),
     "see cases/dafoam/ladder-a/A2_crease_check.json"),
    ("internal: a gate identifier",
     re.compile(r"\bG[1-9]\b\s|\bgate\s+G[1-9]\b", re.I),
     "which is gate G6 and it passed"),
    ("internal: the lab's fixed verdict tokens",
     re.compile(r"\b(NOT A RESULT|GATE FAIL|GATE REACHED|BLOCKED|PENDING)\b"),
     "row B2 is NOT A RESULT"),
    ("internal: container image or library identity",
     re.compile(r"\b(opt-packages|libidwarp|docker|bind-mount|digest)\b", re.I),
     "ran the shipped image dafoam/opt-packages:latest"),
    ("looks recorded: replay and storage words",
     re.compile(r"\b(replay(?:ed|s)?|re-displayed|recorded|stored|cached|"
                r"pre-baked|no new solve|screens come from)\b", re.I),
     "the screens come from that run and nothing is recorded here"),
    ("the sixty-minute forms her order removes",
     re.compile(r"\b(60\s*min|sixty\s*min|one hour|3600|3601)\b", re.I),
     "the optimisation ran for 60 min"),
    ("never-claim words: converged / optimum",
     re.compile(r"\b(converged|optimum)\b", re.I),
     "the optimiser converged to the optimum"),
]

# Past tense is hunted by verb, not by a general -ed rule: "fixed", "solved",
# "measured", "matched", "painted" are participles used adjectivally all over
# an honest present-tense sheet, and a rule that flags them flags nothing
# usefully. These are the auxiliaries and irregulars that can only be past.
PAST = re.compile(
    r"\b(was|were|had been|has been|have been|did not|didn't|"
    r"produced|diverged|stopped|completed|landed|reached|ended|ran|took|"
    r"asked|wrote|chose|gave|came)\b", re.I)

# FIVE OF THOSE ARE AMBIGUOUS AND THE SWEEP MUST NOT CRY WOLF ON THEM. "The
# iteration limit IS NOT REACHED" is present passive and correct; "the run
# COMPLETED early" is past. The word is identical and only what precedes it
# separates them. A sweep that flags the first teaches its reader to skim
# past the second, which is the failure mode that matters. So these five are
# skipped when a present auxiliary sits immediately before them, and flagged
# otherwise. The two-sided control below proves both halves.
AMBIGUOUS = {"produced", "completed", "landed", "reached", "ended"}
PRESENT_AUX = re.compile(r"\b(is|are|am|be|being|does|do|not)\s+(?:\w+\s+){0,2}$", re.I)

PAST_PLANT = "the flow solve diverged and the optimiser was stopped"
#: MUST fire: an ambiguous participle with no present auxiliary before it.
PAST_PLANT_AMBIGUOUS_FIRES = "the optimiser completed forty-seven majors"
#: MUST NOT fire: the same participle in a present passive.
PAST_PLANT_AMBIGUOUS_QUIET = "the iteration limit is not reached"


def _is_past(text: str, m: re.Match) -> bool:
    """True when this match is genuinely past rather than present passive."""
    if m.group(0).lower() not in AMBIGUOUS:
        return True
    return not PRESENT_AUX.search(text[max(0, m.start() - 30):m.start()])

# Words the owner's 03:10Z block strikes by name.
STRUCK = ["not recorded in this bundle", "Solver: none", "source case",
          "no new number is produced", "reference body", "surface on file"]
STRUCK_PLANT = "Solver: none on this request"


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

    for name, pat, _plant in RULES:
        for m in pat.finditer(text):
            record(name, m)
    for m in PAST.finditer(text):
        if _is_past(text, m):
            record("past tense", m)
    low = text.lower()
    for phrase in STRUCK:
        if phrase.lower() in low:
            hits.append(("struck by name at 03:10Z", phrase))
    return hits


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        face = render(SHEET, Path(td))

    # ---------------------------------------------------------- the control
    # Every rule is planted and must be recovered. A rule that cannot see its
    # own plant is not reading anything, and a clean face read by a blind
    # sweep is worth nothing.
    blind: list[str] = []
    for name, pat, plant in RULES:
        if not pat.search(plant):
            blind.append(name)
    if not sweep(PAST_PLANT):
        blind.append("past tense")
    # Two-sided control on the ambiguous participles: the past form must fire
    # and the present passive must stay silent. One-sided would let a filter
    # that suppresses everything pass as if it were precise.
    if not sweep(PAST_PLANT_AMBIGUOUS_FIRES):
        blind.append("past tense (ambiguous participle, past use)")
    if sweep(PAST_PLANT_AMBIGUOUS_QUIET):
        blind.append("past tense (ambiguous participle, present passive "
                     "wrongly flagged)")
    if not any(p.lower() in STRUCK_PLANT.lower() for p in STRUCK):
        blind.append("struck by name at 03:10Z")
    total = len(RULES) + 4
    print(f"PLANT CONTROL: {total - len(blind)}/{total} rule arms behaved")
    if blind:
        print("REFUSE: these rules cannot see a planted violation: "
              + "; ".join(blind))
        return 2

    # The plants must also be recoverable THROUGH the reader, not only in the
    # pattern: plant them into the extracted face and confirm the sweep finds
    # them there. This is the arm that catches a reader that reads nothing.
    planted = face + "\n" + "\n".join(
        [p for _n, _pat, p in RULES] + [PAST_PLANT, STRUCK_PLANT])
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
    # Twenty minutes must be present, with its basis, or the owner's 03:45Z
    # order is not carried out. Absence is a failure, not a pass.
    if "20 minutes" not in face:
        print("\nFACE HITS: the twenty-minute runtime is missing from the face")
        return 1
    print("\nok  the twenty-minute runtime is on the face")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
