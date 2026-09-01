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
BANNED = [
    ("verdict:PASS",            r"\bPASS\b"),
    ("verdict:GATE REACHED",    r"\bGATE\s+REACHED\b"),
    ("verdict:GATE FAIL",       r"\bGATE\s+FAIL\b"),
    ("verdict:NOT A RESULT",    r"\bNOT\s+A\s+RESULT\b"),
    ("verdict:BLOCKED",         r"\bBLOCKED\b"),
    ("verdict:PENDING",         r"\bPENDING\b"),
    ("process:pre-registration", r"pre-?registration"),
    ("process:preregistered",   r"pre-?registered"),
    ("process:docket",          r"\bdocket\b"),
    ("process:lesson id",       r"\bL-\d+\b"),
    ("process:docket id",       r"\bD-?\d{3,}\b"),
    ("process:rule id",         r"\brule\s+\d+\b"),
    ("process:section id",      r"\bsection[ \t]{1,2}\d+(\.\d+)*[a-z]?\b"),
    ("process:charter",         r"\bcharter\b"),
    ("process:tier",            r"\btier\s*[0-9A-Z]"),
    ("process:defect/patch",    r"\b(defect|upstream patch|toolchain|workaround)\b"),
    ("id:case id",              r"\bJF1[_A-Za-z0-9]*"),
    ("id:CMU tag",              r"\bCMU\d{3}\b"),
    ("id:rung id",              r"\b(L1|P1|A0)_[A-Z0-9]"),
    ("solver:polyMesh",         r"\bpolyMesh\b"),
    ("solver:jetSlot",          r"\bjetSlot\b"),
    ("solver:patch type",       r"\bboundary\s+(type|patch)\b|\btype\s+(wall|patch)\b"),
    ("solver:controlDict",      r"\bcontrolDict\b"),
    ("solver:simpleFoam",       r"\bsimpleFoam\b"),
    ("solver:checkMesh",        r"\bcheckMesh\b"),
    ("solver:kOmegaSST",        r"\bkOmegaSST\b"),
    ("solver:OpenFOAM",         r"\bOpenFOAM\b"),
    ("sanaa:unfamiliar body",   r"unfamiliar body"),
    # The false Act B claim, in every wording it has worn.
    ("false:differ only(unscoped)",
     r"five (calculations|curves|conditions)[^.]{0,80}differ only"),
    ("false:nothing else differs",
     r"nothing else about the calculation differs"),
    ("false:blowing alone(five)",
     r"[Aa]ll five[^.]{0,120}blowing alone"),
]

POISON = (
    "PASS GATE REACHED GATE FAIL NOT A RESULT BLOCKED PENDING pre-registration "
    "pre-registered docket L-186 D438 rule 10 section 5.2a charter tier 1 "
    "defect upstream patch toolchain workaround JF1_L1_BLOWN_CMU005_A0 CMU005 "
    "L1_B polyMesh jetSlot type wall controlDict simpleFoam checkMesh "
    "kOmegaSST OpenFOAM unfamiliar body "
    "All five calculations share one mesh and differ only in blowing, "
    "nothing else about the calculation differs. "
    "All five blowing strengths were computed on this one grid, so the "
    "differences between them come from the blowing alone."
)


def render(pdf, txt):
    subprocess.run(["pdftotext", "-layout", pdf, txt], check=True)


def scan(path):
    text = open(path, errors="replace").read()
    hits = []
    for label, pat in BANNED:
        m = re.findall(pat, text, re.I if label.startswith("false:") else 0)
        if m:
            hits.append((label, len(m)))
    return hits


def main():
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
