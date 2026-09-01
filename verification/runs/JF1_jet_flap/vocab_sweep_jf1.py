#!/usr/bin/env python3
"""
Banned-vocabulary sweep over the RENDERED text of the Act B assets.

Run:  python3 verification/runs/JF1_jet_flap/vocab_sweep_jf1.py
Exit: 0 clean, 1 hits found, 2 the reader REFUSED (poisoned control blind).

A zero from a reader not shown able to see a non-zero is not evidence
(CLAUDE.md rule 3).  So this script ALWAYS builds a POISONED POSITIVE CONTROL
first: a copy of one real rendered page with one line inserted carrying every
banned token.  If the sweep does not flag EVERY token in the poisoned file, the
sweep REFUSES and reports nothing about the real files.
"""
import os
import re
import subprocess
import sys

ART = "/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap/artefacts"
ACTB = "/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap/artefacts_actB"
import tempfile
WORK = tempfile.mkdtemp(prefix="jf1_vocab_")

# (label, regex).  Demo Standard v2 R5 + R9: verdict vocabulary, process
# language, internal identifiers, solver dictionary names, defect/repair talk,
# and the phrases Sanaa struck by name in the 2026-09-01 GUI feedback.
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#  L-425 REPAIR, 2026-09-01.  `\b(defect|...)\b` REPORTED CLEAN BECAUSE IT
#  COULD NOT SEE.  Against "defects" the engine matched `defect` and then
#  required a word boundary between `t` and `s` -- both word characters, so
#  there is none and the match failed.  "defects", "toolchains" and
#  "workarounds" passed a sweep whose entire job is keeping those words off a
#  filmed surface.  That is the false-zero shape, in a checker rather than a
#  reader.
#
#  THE WHOLE PATTERN TABLE WAS AUDITED FOR THE CLASS, not the three named
#  words.  Every entry below was decided by looking at it and asking what
#  form could actually reach a screen.  The entries judged IMMATERIAL are
#  named in IMMATERIAL_BY_DESIGN at the foot of this table WITH THEIR REASON,
#  rather than being silently left narrow -- an undocumented decision not to
#  fix is indistinguishable from not having looked.
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
BANNED = [
    ("verdict:PASS",            r"\bPASS(?:ES|ED)?\b"),
    ("verdict:GATE REACHED",    r"\bGATE\s+REACHED\b"),
    ("verdict:GATE FAIL",       r"\bGATE\s+FAIL(?:S|ED|URE|URES)?\b"),
    ("verdict:NOT A RESULT",    r"\bNOT\s+A\s+RESULTS?\b"),
    ("verdict:BLOCKED",         r"\bBLOCKED\b"),
    ("verdict:PENDING",         r"\bPENDING\b"),
    ("process:pre-registration", r"pre-?registrations?"),
    ("process:preregistered",   r"pre-?register(?:ed|ing|s)?"),
    ("process:docket",          r"\bdockets?\b"),
    ("process:lesson id",       r"\bL-\d+\b"),
    ("process:docket id",       r"\bD-?\d{3,}\b"),
    ("process:rule id",         r"\brules?\s+\d+\b"),
    ("process:section id",      r"\bsections?[ \t]{1,2}\d+(\.\d+)*[a-z]?\b"),
    ("process:charter",         r"\bcharters?\b"),
    ("process:tier",            r"\btiers?\s*[0-9A-Z]"),
    ("process:defect/patch",
     r"\b(?:defect(?:s|ive)?|upstream\s+patch(?:es)?|toolchains?|workarounds?)\b"),
    ("id:case id",              r"\bJF1[_A-Za-z0-9]*"),
    ("id:CMU tag",              r"\bCMU\d{3}\b"),
    ("id:rung id",              r"\b(?:L1|P1|A0)_[A-Z0-9]"),
    ("solver:polyMesh",         r"\bpolyMesh(?:es)?\b"),
    ("solver:jetSlot",          r"\bjetSlots?\b"),
    ("solver:patch type",
     r"\bboundary\s+(?:types?|patch(?:es)?)\b|\btype\s+(?:wall|patch)\b"),
    ("solver:controlDict",      r"\bcontrolDicts?\b"),
    ("solver:simpleFoam",       r"\bsimpleFoam\b"),
    ("solver:checkMesh",        r"\bcheckMesh\b"),
    ("solver:kOmegaSST",        r"\bkOmegaSST\b"),
    ("solver:OpenFOAM",         r"\bOpenFOAM\b"),
    ("sanaa:unfamiliar body",   r"unfamiliar\s+bod(?:y|ies)"),
    # The false Act B claim, in every wording it has worn.
    ("false:differ only(unscoped)",
     r"five (calculations|curves|conditions)[^.]{0,80}differ only"),
    ("false:nothing else differs",
     r"nothing else about the calculation differs"),
    ("false:blowing alone(five)",
     r"[Aa]ll five[^.]{0,120}blowing alone"),
]

#: Entries deliberately left without an inflected form, WITH THE REASON. Each
#: is a proper noun -- a solver, a dictionary or a model name -- where a
#: plural cannot reach a rendered page as English. Recorded so that "not
#: fixed" is visibly a DECISION and not an oversight.
IMMATERIAL_BY_DESIGN = {
    "solver:simpleFoam":  "solver executable name; 'simpleFoams' is not English",
    "solver:checkMesh":   "tool name; no plural form occurs in prose",
    "solver:kOmegaSST":   "turbulence model name; used as a mass noun",
    "solver:OpenFOAM":    "product name; never pluralised",
    "id:CMU tag":         "fixed-width tag CMU\\d{3}; a plural cannot follow the digits",
    "process:lesson id":  "identifier L-<n>; plural would be 'lessons L-1 and L-2', "
                          "each id still matching individually",
    "process:docket id":  "identifier D<n>; same reasoning as the lesson id",
    "id:case id":         "already ends in [_A-Za-z0-9]* so every suffix is caught",
    "id:rung id":         "matches a prefix before an underscore; no trailing boundary",
    "verdict:GATE REACHED": "past participle already; 'GATE REACHEDs' is not English",
    "verdict:BLOCKED":    "past participle already",
    "verdict:PENDING":    "present participle already",
}

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#  THE PLANTS -- AND THE INDEPENDENCE CLAUSE, WHICH IS THE WHOLE POINT.
#
#  THESE ARE WRITTEN OUT BY HAND, ONE PER ALTERNATIVE, AND ARE NOT DERIVED
#  FROM `BANNED` IN ANY WAY.  That is not stylistic. If the plants were
#  generated from the pattern list, then a pattern blind to plurals would
#  produce a plant blind to plurals, the control would pass, AND THE GUARD
#  WOULD BE CERTIFIED BY ITS OWN DEFECT.  That is exactly how the old single
#  POISON line passed while "defects" walked through: the line was hand-typed,
#  but hand-typed to mirror the regexes' singular forms.
#
#  So each entry below answers a different question -- not "what does the
#  regex match?" but "WHAT COULD ACTUALLY REACH A SCREEN?" -- and the plural
#  forms are here because English has plurals, not because a pattern mentions
#  them.  The control must be able to fail for a reason the pattern does not
#  already know about.
#
#  Every alternative of every alternation gets its own plant (L-425).
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
PLANTS = [
    ("verdict:PASS", "the rung is a PASS"),
    ("verdict:PASS", "both rungs are PASSES on the stated band"),
    ("verdict:PASS", "the case PASSED its band"),
    ("verdict:GATE REACHED", "GATE REACHED on admission"),
    ("verdict:GATE FAIL", "recorded GATE FAIL against the gate"),
    ("verdict:GATE FAIL", "two GATE FAILS stand on the record"),
    ("verdict:GATE FAIL", "the clause GATE FAILED as written"),
    ("verdict:GATE FAIL", "a GATE FAILURE is recorded"),
    ("verdict:GATE FAIL", "both GATE FAILURES are left standing"),
    ("verdict:NOT A RESULT", "the row is NOT A RESULT"),
    ("verdict:NOT A RESULT", "these rows are NOT A RESULTS by the triple rule"),
    ("verdict:BLOCKED", "the case is BLOCKED on admission"),
    ("verdict:PENDING", "the rung is PENDING"),
    ("process:pre-registration", "the pre-registration was frozen first"),
    ("process:pre-registration", "both pre-registrations were frozen first"),
    ("process:pre-registration", "the preregistration is committed"),
    ("process:preregistered", "a preregistered gate"),
    ("process:preregistered", "we pre-registered the threshold"),
    ("process:preregistered", "pre-registering the threshold first"),
    ("process:docket", "filed on the docket"),
    ("process:docket", "filed across two dockets"),
    ("process:lesson id", "see L-186 for the reasoning"),
    ("process:docket id", "raised as D438 at the time"),
    ("process:rule id", "under rule 10 of the constitution"),
    ("process:rule id", "under rules 10 and 11 together"),
    ("process:section id", "see section 5.2a of the charter"),
    ("process:section id", "see sections 5.2 and 6.1"),
    ("process:charter", "the charter fixes the vocabulary"),
    ("process:charter", "the charters fix the vocabulary"),
    ("process:tier", "graded tier 2 for provenance"),
    ("process:tier", "graded tiers 2 and 3 for provenance"),
    # --- the four alternatives of the L-425 pattern, singular AND plural ---
    ("process:defect/patch", "a defect in the reader"),
    ("process:defect/patch", "two defects in the reader"),
    ("process:defect/patch", "a defective reading of the log"),
    ("process:defect/patch", "an upstream patch is prepared"),
    ("process:defect/patch", "two upstream patches are prepared"),
    ("process:defect/patch", "a toolchain limitation"),
    ("process:defect/patch", "several toolchains are affected"),
    ("process:defect/patch", "a workaround is in place"),
    ("process:defect/patch", "two workarounds are in place"),
    ("id:case id", "JF1_L1_BLOWN_CMU005_A0 was solved"),
    ("id:CMU tag", "the CMU005 row"),
    ("id:rung id", "the L1_B grid"),
    ("solver:polyMesh", "written to polyMesh on disk"),
    ("solver:polyMesh", "two polyMeshes on disk"),
    ("solver:jetSlot", "the jetSlot patch"),
    ("solver:jetSlot", "both jetSlots are closed"),
    ("solver:patch type", "the boundary type is set"),
    ("solver:patch type", "the boundary types are set"),
    ("solver:patch type", "the boundary patch is a wall"),
    ("solver:patch type", "the boundary patches are walls"),
    ("solver:patch type", "declared type wall in the dictionary"),
    ("solver:patch type", "declared type patch in the dictionary"),
    ("solver:controlDict", "set in controlDict"),
    ("solver:controlDict", "set in both controlDicts"),
    ("solver:simpleFoam", "solved with simpleFoam"),
    ("solver:checkMesh", "checkMesh reports it"),
    ("solver:kOmegaSST", "closed with kOmegaSST"),
    ("solver:OpenFOAM", "built on OpenFOAM"),
    ("sanaa:unfamiliar body", "an unfamiliar body to the viewer"),
    ("sanaa:unfamiliar body", "two unfamiliar bodies to the viewer"),
    ("false:differ only(unscoped)",
     "five calculations on one mesh that differ only in blowing"),
    ("false:differ only(unscoped)",
     "five curves on one mesh that differ only in blowing"),
    ("false:differ only(unscoped)",
     "five conditions on one mesh that differ only in blowing"),
    ("false:nothing else differs",
     "nothing else about the calculation differs"),
    ("false:blowing alone(five)",
     "All five rows come from the blowing alone"),
]

#: The blended line kept as a SECOND control, run against a REAL rendered
#: page. The per-plant control proves each pattern sees its own token; this
#: one proves the reader still works on real pdftotext output rather than only
#: on synthetic strings.
POISON = " ".join(text for _, text in PLANTS)


def render(pdf, txt):
    subprocess.run(["pdftotext", "-layout", pdf, txt], check=True)


def scan_text(text, table=None):
    hits = []
    for label, pat in (table if table is not None else BANNED):
        m = re.findall(pat, text, re.I if label.startswith("false:") else 0)
        if m:
            hits.append((label, len(m)))
    return hits


def scan(path, table=None):
    return scan_text(open(path, errors="replace").read(), table)


def plant_control(table=None, verbose=True):
    """Every planted violation must be caught BY ITS OWN pattern.

    Scanning each plant IN ISOLATION is deliberate and is stronger than the
    old blended line: in a blend, one token caught by a DIFFERENT pattern
    makes the label set look complete while the pattern that should have
    caught it is blind. Here plant and label are checked as a pair.

    Returns (ok, missed) where `missed` is a list of (label, text).
    """
    missed = []
    for label, text in PLANTS:
        fired = {lab for lab, _ in scan_text(text, table)}
        if label not in fired:
            missed.append((label, text))
    if verbose:
        print("PER-PLANT CONTROL         : %d planted violations, one per "
              "alternative, declared INDEPENDENTLY of the patterns" % len(PLANTS))
        if missed:
            print("  MISSED %d -- the guard is blind to these forms:" % len(missed))
            for label, text in missed:
                print("    %-28s %r" % (label, text))
        else:
            print("  every plant caught by its OWN pattern.")
    return (not missed), missed


def prove_control_can_fail(label_to_neuter="process:defect/patch"):
    """Neuter one pattern and require ITS plants to be reported MISSED.

    A control never seen to fail is not known to work. This reproduces the
    L-425 defect on purpose -- the neutered pattern is the ORIGINAL narrow
    one -- and requires the control to catch it.
    """
    narrow = {
        "process:defect/patch":
            r"\b(defect|upstream patch|toolchain|workaround)\b",
        "process:charter": r"\bcharter\b",
        "process:docket": r"\bdocket\b",
    }[label_to_neuter]
    table = [(lab, narrow if lab == label_to_neuter else pat)
             for lab, pat in BANNED]
    ok, missed = plant_control(table, verbose=False)
    mine = [(lab, txt) for lab, txt in missed if lab == label_to_neuter]
    print("MUTATION: %r reverted to its pre-repair narrow form" % label_to_neuter)
    print("  %r" % narrow)
    print("  control verdict            : %s" % ("PASSED (BAD)" if ok else "REFUSED"))
    print("  plants it now misses       : %d" % len(mine))
    for lab, txt in mine:
        print("    %-28s %r" % (lab, txt))
    good = (not ok) and bool(mine)
    print("  -> the control CAN fail, and fails on the right plants: %s"
          % ("YES" if good else "NO -- the control is not known to work"))
    return 0 if good else 2


def main():
    if "--prove-control" in sys.argv:
        return prove_control_can_fail()

    # ---- CONTROL 1, run before anything is rendered or reported ------------
    ok, _ = plant_control()
    if not ok:
        print("  REFUSED -- a zero on the real files would mean nothing. "
              "No sweep run.")
        return 2
    print()

    os.makedirs(WORK, exist_ok=True)
    targets = sorted(
        [os.path.join(ART, f) for f in os.listdir(ART) if f.endswith(".pdf")] +
        [os.path.join(ACTB, "blown_trailing_edge_result_sheet.pdf")])

    rendered = []
    for p in targets:
        t = os.path.join(WORK, os.path.basename(p)[:-4] + ".txt")
        render(p, t)
        rendered.append(t)

    # ---------------- POISONED POSITIVE CONTROL, RUN FIRST -------------------
    donor = rendered[0]
    poisoned = os.path.join(WORK, "_POISONED_POSITIVE_CONTROL.txt")
    with open(poisoned, "w") as fh:
        fh.write(open(donor, errors="replace").read())
        fh.write("\n" + POISON + "\n")

    seen = {lab for lab, _ in scan(poisoned)}
    missed = [lab for lab, _ in BANNED if lab not in seen]
    print("POISONED POSITIVE CONTROL : %s" % poisoned)
    print("  tokens the reader CAUGHT : %d of %d" % (len(seen), len(BANNED)))
    if missed:
        print("  REFUSED -- the reader is blind to: %s" % ", ".join(missed))
        print("  A zero on the real files would mean nothing. No sweep run.")
        return 2
    print("  the reader is shown able to see a non-zero for EVERY token.\n")

    # ---------------- the real sweep ----------------------------------------
    total = 0
    for t in rendered:
        hits = scan(t)
        total += sum(n for _, n in hits)
        print("%-44s %s" % (os.path.basename(t),
                            "clean" if not hits
                            else "; ".join("%s x%d" % h for h in hits)))
    print("\nTOTAL BANNED-VOCABULARY HITS ACROSS %d RENDERED PAGES: %d"
          % (len(rendered), total))
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
