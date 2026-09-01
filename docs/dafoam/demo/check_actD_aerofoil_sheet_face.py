#!/usr/bin/env python3
"""Sweep the RENDERED FACE of the Act D aerofoil-section sheet (the baseline).

WHY THIS FILE EXISTS, AND IT IS NOT "FOR COMPLETENESS".  This sheet sat in a
directory of three swept sheets and was itself never swept by anything.  That is
the most dangerous file in the directory, because its cleanliness is inferred
from its neighbours rather than measured, and the inference is worthless: it was
carrying a screen-8 violation ("No grid-refinement study was run", which shows
the study as ABSENT, against Sanaa's 20:30Z rule that it is shown done or
underway and never as absent) at the moment the other three were reported clean.

IT IS ALSO THE CLEANEST DEMONSTRATION OF WHY THE FLAT TENSE RULE HAD TO GO.  This
sheet is written almost entirely in the past -- "What was checked", "The check
was proved able to fail", "These three points were solved twice", "Lift
derivatives were checked the same way" -- because it is a results artefact end to
end.  Under the superseded 04:20Z "no past tense" it would have gone red on every
one of those, all of which are CORRECT under the restored rule.  Nothing swept
it, so nobody found out.  An instrument's absence is not an instrument's silence.

WHAT IS SHARED AND WHAT IS NOT.  The rule MATERIAL is imported from
`check_actD_sheet_face` so the four sheets cannot drift on what counts as
internal information, a replay word or a struck phrase; the tense rule comes from
`demo_stages`, keyed to the beat.  Two imported rules do not transfer and each is
REPLACED rather than dropped:

  1. `never-claim words: converged / optimum`.  The reference-wing ban exists
     because THAT optimiser printed no convergence statement, so the word would
     have been a claim its run did not support.  Here the word is used of the
     FLOW SOLVER's residual falling below a stated tolerance at all three angles
     -- a measured fact with its evidence on the same face.  So the rule is
     CONDITIONAL, as on the two multipoint sheets: `converged` is admissible only
     while the residual tolerance is on the face beside it.  Remove the tolerance
     and the word becomes a violation again.  `optimum` stays banned outright:
     no optimiser has run on this section at all.

  2. `the sixty-minute forms her order removes`.  That figure was ordered against
     the reference wing's 3,601 s.  This sheet is a verification sheet for a
     4,032-cell section and its own compute figures are far smaller, so the rule
     hunts the OPPOSITE failure here: a twenty- or sixty-minute figure asserted
     as this sheet's own elapsed time would be a number this work did not
     produce.

ONE RULE IS NEW AND BELONGS TO THIS SHEET ALONE.  This is the BASELINE sheet --
"Shape optimisation runs next" -- so a drag or lift number here may never be
presented as an optimised result.  The check is executable rather than prose: the
words that would make it one are hunted, and the honest disclaimer's presence is
required, because a sheet that simply deleted the disclaimer would sweep clean.

    python3 docs/dafoam/demo/check_actD_aerofoil_sheet_face.py
"""
from __future__ import annotations

import re
import shutil
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
    tense_sweep, coverage, check_coverage, check_plants as check_tense_plants,
)

SHEET = Path(__file__).resolve().parent / "ACT_D_aerofoil_section_sheet.tex"

#: The two replaced rules, named so the drop is visible rather than silent.
NOT_TRANSFERRED = {"never-claim words: converged / optimum",
                   "the sixty-minute forms her order removes"}
SHARED_RULES = [r for r in REFERENCE_RULES if r[0] not in NOT_TRANSFERRED]
if len(SHARED_RULES) != len(REFERENCE_RULES) - 2:
    raise SystemExit("REFUSE: the two replaced rules are not both present "
                     "upstream; this script's reasoning no longer matches it")

OWN_RULES: list[tuple[str, re.Pattern, list[str]]] = [
    ("a minute figure this sheet did not produce",
     re.compile(r"\b(20|twenty|60|sixty)\s*min(?:ute)?s?\b|\bone hour\b", re.I),
     ["the whole job is 20 minutes on one core",
      "the whole job is twenty minutes on one core",
      "the whole job is 60 min on one core",
      "the whole job is sixty minutes on one core",
      "it took one hour on this box"]),
    ("an optimised result claimed on the baseline sheet",
     re.compile(r"\b(optimum|optimised (?:shape|section|result)|"
                r"optimized (?:shape|section|result)|"
                r"after optimisation|after optimization)\b", re.I),
     ["the shape is the optimum",
      "the optimised shape carries this drag",
      "the optimised section carries this drag",
      "the optimised result is quoted here",
      "the optimized shape carries this drag",
      "the optimized section carries this drag",
      "the optimized result is quoted here",
      "drag after optimisation is lower",
      "drag after optimization is lower"]),
]

#: `converged` is earned only while the solver's own residual tolerance is on the
#: same face.  Note this is the FLOW solver, not an optimiser: no optimiser has
#: run on this section, which is why `optimum` stays banned above.
RESIDUAL_EVIDENCE = re.compile(
    r"residual fell\s+below its\s+10\s*[-\u2212\u2013]\s*8", re.I)
CONVERGED = re.compile(r"\bconverged\b", re.I)

#: The baseline disclaimer.  Its ABSENCE is a failure, not a clean sweep.
DISCLAIMER = "No optimiser has run on this section"

# ------------------------------------------------------------- the stage map --
# WHICH BEAT EACH BLOCK IS.  Nothing here says what tense that implies.
STAGE_MAP = [
    Region(r"\\textbf\{Shape optimisation runs next\.\} This sheet is the step",
           STATIC_REGION, "masthead: what this sheet is and what comes next"),
    Region(r"\\textbf\{One thing we changed in your request\}", STATIC_REGION,
           "the user-assumption correction beat"),
    Region(r"\\textbf\{The problem we set up\.\}", STATIC_REGION,
           "method: the problem statement, timeless"),
    Region(r"\\textbf\{Table 1 --- Operating condition\.\}", STATIC_REGION,
           "assumptions: quantities with units"),
    Region(r"\\textbf\{Figure 1 --- Which way the optimiser would move",
           STATIC_REGION, "figure note"),
    Region(r"\\textbf\{Table 3 --- The derivative check\.\}", RESULTS,
           "the derivative check"),
    Region(r"\\textbf\{Table 2 --- The three solved operating points\.\}",
           RESULTS, "the solved points"),
    Region(r"\\textbf\{Figure 2 --- Step-size check\.\}", STATIC_REGION,
           "figure note"),
    Region(r"\\textbf\{What was checked, and what was not\}", RESULTS,
           "what was checked"),
    # STAGE 8. Her screen-8 rule, in her second form, and it is true rather than
    # a device: A1WR is live and A2-GC L1 cap-stopped with L2 and L3 owed to a
    # successor. No band is claimed and no study is called finished. This block
    # is why the flat rule could never have worked -- it is present progressive
    # sitting between two past-tense results blocks on the same sheet.
    Region(r"\\textbf\{One mesh, \$4\\,032\$ cells\.\}", CONVERGENCE_STUDY,
           "the grid convergence study, underway"),
    Region(r"\\textbf\{Shape optimisation runs next\.\} No optimiser", RESULTS,
           "the baseline disclaimer"),
    Region(r"\\textbf\{Table 4 --- Compute", RESULTS, "compute"),
    Region(r"\\textbf\{Read this before you use the numbers\}", RESULTS,
           "limitations"),
    Region(r"\\textbf\{Figure 3 --- Polar\.\}", STATIC_REGION, "figure note"),
    Region(r"\\rolesig\{Lead Researcher\.\}", RESULTS,
           "the three roles, delivering findings"),
]


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
    hits: list[tuple[str, str]] = []

    def record(name: str, m: re.Match) -> None:
        a, b = max(0, m.start() - 40), min(len(text), m.end() + 40)
        hits.append((name, f"{m.group(0)!r} in ...{' '.join(text[a:b].split())}..."))

    for name, pat, _plants in SHARED_RULES + OWN_RULES:
        for m in pat.finditer(text):
            record(name, m)
    low = text.lower()
    for phrase in STRUCK:
        if phrase.lower() in low:
            hits.append(("struck by name at 03:10Z", phrase))
    if not RESIDUAL_EVIDENCE.search(text):
        for m in CONVERGED.finditer(text):
            record("converged claimed with no residual tolerance on the face", m)
    return hits


def _fires(name: str, plant: str) -> bool:
    return any(n == name for n, _c in sweep(plant))


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        face = render(SHEET, Path(td))

    # ------------------------------------------------------------- controls
    blind: list[str] = []
    arms: list[str] = []

    def arm(name: str, behaved: bool) -> None:
        arms.append(name)
        if not behaved:
            blind.append(name)

    for name, _pat, plants in SHARED_RULES + OWN_RULES:
        for plant in plants:
            arm(f"{name} [{plant[:40]}]", _fires(name, plant))
    for phrase in STRUCK:
        arm(f"struck [{phrase}]",
            _fires("struck by name at 03:10Z",
                   f"the sheet says {phrase} on its face"))
    # The conditional rule, driven in BOTH directions.  One-sided would let a
    # rule that never fires, or one that always fires, pass as if it worked.
    arm("converged with no residual tolerance (must fire)",
        bool(sweep("every operating point converged")))
    # THE PLANT IS WRITTEN IN THE FORM THE RULE READS, WHICH IS THE FACE.
    # It was first written in LaTeX source form and this arm went red, which is
    # the arm working: `pdftotext` renders $10^{-8}$ with a UNICODE MINUS, so a
    # plant in source form proves nothing about what the rule sees on a page.
    arm("converged beside the residual tolerance (must stay quiet)",
        not sweep("every operating point converged: the solver's residual fell "
                  "below its 10\u22128 tolerance"))
    # The tense arms, both directions, both regimes, counted here.
    t_ok, t_attempted, t_blind = check_tense_plants()
    for i in range(t_attempted - len(t_blind)):
        arm(f"tense arm {i} (demo_stages, both directions)", True)
    for name in t_blind:
        arm(name, False)

    print(f"PLANT CONTROL: {len(arms) - len(blind)}/{len(arms)} rule arms behaved")
    if blind:
        print("REFUSE: these arms did not behave: " + "; ".join(blind))
        return 2

    every_plant = [p for _n, _pt, ps in SHARED_RULES + OWN_RULES for p in ps]
    if len(sweep(face + "\n" + "\n".join(every_plant))) <= len(sweep(face)):
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
    # pass: a sheet that simply deleted the baseline disclaimer, or the
    # convergence-study line, would otherwise sweep clean.
    missing = []
    if DISCLAIMER not in face:
        missing.append("the baseline disclaimer, "
                       f"{DISCLAIMER!r}")
    if "grid convergence study for this case is running" not in face:
        missing.append("the screen-8 line; the study may never be shown as absent")
    if missing:
        print("\nFACE HITS: missing from the face: " + "; ".join(missing))
        return 1
    print("\nok  the baseline disclaimer and the screen-8 line are both on the "
          f"face; the sweep found {len(hits)} hit(s)")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
