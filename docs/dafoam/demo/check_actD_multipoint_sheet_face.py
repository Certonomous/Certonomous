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
    RULES as REFERENCE_RULES, STRUCK,
)
from demo_stages import (  # noqa: E402  the tense rule, keyed to the beat
    RESULTS, STATIC_REGION, Region, STAGE_NAMES, tense_sweep, coverage,
    check_coverage, check_plants as check_tense_plants,
)

# AMENDED 2026-09-01 (20:30Z DIRECTIVE, `cfcf766f`).  `PAST` and `_is_past` are
# no longer imported and no longer applied here.  Sanaa's shooting protocol
# restores *"Present and progressive tense while running; past tense for
# results"* and supersedes the flat 04:20Z "no past tense" this file
# implemented, so a global past-tense sweep over this sheet's face now flags
# COMPLIANT results prose.  Tense is swept by beat instead; the map is below and
# the regime table is in `demo_stages.py`, which is the only place a further
# revision of the rule has to touch.
#
# THE SHEET'S OWN MEASURED POSITION UNDER THE RESTORED RULE, so the change is
# not taken on trust: it carried 0 past-tense hits under the flat rule and
# carries 1 present-run-narration hit under this one.  The direction of failure
# inverted; the count did not collapse to zero either way.

#: WHICH BEAT EACH BLOCK IS.  Nothing here says what tense that implies.
STAGE_MAP = [
    Region(r"\\textbf\{Solver: DAFoam \\texttt\{DASimpleFoam\}", RESULTS,
           "the solved-case banner"),
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
    Region(r"\\textbf\{Figure 3\. Objective against major iteration\.\}",
           STATIC_REGION, "figure note"),
    Region(r"\\textbf\{Table 4\. The gradient, checked at the final shape\.\}",
           RESULTS, "gradient table"),
    Region(r"\\textbf\{Figure 4\. Gradient check at the final shape\.\}",
           STATIC_REGION, "figure note"),
    Region(r"\\textbf\{Table 5\. Instrument checks\.\}", RESULTS,
           "instrument checks"),
    Region(r"\\textbf\{Table 6\. Compute", RESULTS, "compute"),
    Region(r"\\textbf\{Uncertainty\}", RESULTS, "uncertainty channels"),
    Region(r"\\textbf\{Read this before you use the numbers\}", RESULTS,
           "limitations"),
    Region(r"\\textbf\{Assumed, not measured\}", STATIC_REGION,
           "assumptions: quantities with units"),
    Region(r"\\rolesig\{Lead Researcher\.\}", RESULTS,
           "the three roles, delivering findings"),
]

# WHAT THIS IMPORTS, AND WHAT IT DELIBERATELY DOES NOT.  The sibling module is
# under active repair, and its PLANT constants have already changed shape once
# (a single string per rule became a list of per-alternative plants).  Binding
# to those constants makes this script break, or worse silently skip an arm,
# every time that repair lands.  So only the RULE MATERIAL is shared -- the
# patterns, the past-tense verb set and the struck phrases, which are what must
# never drift between the two sheets -- and the plants below are this script's
# own.  A plant is a statement of what a rule must catch; writing it here rather
# than importing it means an edit to a shared pattern is checked against
# something that did not come from that pattern.
#
# THE SHAPE OF `RULES` IS ASSERTED RATHER THAN ASSUMED.  If the sibling changes
# it again, this REFUSES loudly instead of sweeping with rules it cannot plant.

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

OWN_RULES: list[tuple[str, re.Pattern, str]] = [
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
    #: EVERY ARM THAT ACTUALLY RUNS, REGISTERED AS IT RUNS. The ``+ 8`` this
    #: replaces was ARITHMETICALLY CORRECT here -- eight standalone arms, eight
    #: counted -- and it is replaced anyway, because the sibling compressible
    #: checker was written from this one, gained two arms, and went on
    #: publishing a constant: 61 arms where 59 existed. A hand-written count
    #: beside the thing it counts is right until somebody edits the thing, and
    #: nothing detects the moment it stops being right. Derived here too, so
    #: the count cannot disagree with reality: it IS reality.
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
    # THE TENSE ARMS RUN IN `demo_stages` AND ARE COUNTED HERE. They cannot run
    # through `sweep`, which reads a bare string with no beat, and a beat is now
    # the whole question. What they gained by moving is the second direction:
    # every alternative planted in a running beat where it must fire AND in a
    # results beat where it must stay quiet, plus the mirror pair for present
    # run narration. That arm is what a superseded rule left in place fails.
    t_ok, t_attempted, t_blind = check_tense_plants()
    for i in range(t_attempted - len(t_blind)):
        arm(f"tense arm {i} (demo_stages)", True)
    for name in t_blind:
        arm(name, False)
    arm("struck by name at 03:10Z",
        any(p.lower() in STRUCK_PLANT.lower() for p in STRUCK))
    # The conditional rule, driven in BOTH directions.  One-sided would let a
    # rule that never fires, or one that always fires, pass as if it worked.
    arm("converged with no terminal statement (must fire)",
        bool(sweep("the optimiser converged on its own tolerance")))
    arm("converged beside the terminal statement (must stay quiet)",
        not sweep("the optimiser converged. " + TERMINAL_STATEMENT))
    # The forbidden-reading rule, driven in both directions too.
    arm("drag reduction without the lift columns (must fire)",
        bool(sweep("drag falls 16.2 per cent")))
    arm("drag reduction beside the lift columns (must stay quiet)",
        not sweep("drag falls 16.2 per cent. CL start CL final "
                  + TERMINAL_STATEMENT))

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
