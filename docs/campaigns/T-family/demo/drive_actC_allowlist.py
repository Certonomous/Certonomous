#!/usr/bin/env python3
"""Drive Amendment 1 END TO END, BOTH DIRECTIONS, on a really rendered sheet.

`check_actC_gate_screen.allowlist_control()` drives the match rule on strings.
This drives the WHOLE SWEEP -- LaTeX, `pdftotext`, the numeric rules, the
latexified reader -- on a real one-page PDF carrying real planted temperatures,
because the arithmetic being right is not the same evidence as the instrument
catching it on a rendered page.  The guard's own docstring records that
`pdflatex` will happily render a banned thermal result and return zero; that is
the failure this drive reproduces on purpose.

WHAT IT PLANTS.  Two temperatures, chosen so the pair separates the two
outcomes on ONE page:

    301.4409 K   -- treated as GRADED in direction 2
    301.5409 K   -- its neighbour, GRADED BY NOTHING, ever

DIRECTION 1, the empty graded set.  Both must be refused, and the sweep must
exit 2.  This is the state the lab is in until the corrected run grades, and it
is the arm that proves the amendment changed nothing while the set is empty.

DIRECTION 2, a planted graded set.  Exactly `301.4409` must be released and
`301.5409` must still be refused, on the same page, in the same run.  A
loosening that admits its own plant proves nothing about what it still refuses,
so the refusal is asserted in the same breath as the admission.

THE SEAM.  Direction 2 substitutes the derived set at
`actC_graded_admission.derive`, which is the one documented seam.  The
DERIVATION itself -- including its reader looking at HEAD rather than at the
working tree -- carries its own planted control against a real scratch git
repository (`actC_graded_admission.py --selftest`), so nothing here is asserted
on the derivation's own authority.

Nothing in the repository is written or modified: the mutated sheet is built in
a temporary directory and removed.

    python3 drive_actC_allowlist.py
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import actC_graded_admission as ADMIT                          # noqa: E402
import check_actC_gate_screen as SCREEN                        # noqa: E402

GRADED = 301.4409
NEIGHBOUR = 301.5409

PLANT_TEX = (r"{\footnotesize The module peak reads %.4f\,K and the "
             r"neighbouring probe reads %.4f\,K.}\\[1.0mm]"
             % (GRADED, NEIGHBOUR))


def build_mutated_sheet(workdir):
    """Compile a copy of the sheet carrying both planted temperatures."""
    src = os.path.join(HERE, "ACT_C_GATE_sheet.tex")
    tex = open(src).read()
    if r"\end{document}" not in tex:
        raise SystemExit("the sheet source has no document end to plant before")
    tex = tex.replace(r"\end{document}", PLANT_TEX + "\n\\end{document}")
    dst = os.path.join(workdir, "ACT_C_GATE_sheet.tex")
    open(dst, "w").write(tex)
    figdst = os.path.join(workdir, "figures_actC_gate")
    os.makedirs(figdst, exist_ok=True)
    for name in os.listdir(os.path.join(HERE, "figures_actC_gate")):
        if name.endswith(".pdf"):
            shutil.copy(os.path.join(HERE, "figures_actC_gate", name), figdst)
    for _ in range(2):
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode",
                            "-halt-on-error", "ACT_C_GATE_sheet.tex"],
                           cwd=workdir, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
    pdf = os.path.join(workdir, "ACT_C_GATE_sheet.pdf")
    if not os.path.isfile(pdf):
        raise SystemExit("REFUSE: the mutated sheet did not compile, so this "
                         "drive proves nothing:\n"
                         + r.stdout.decode("utf-8", "replace")[-2000:])
    return pdf


def sweep(pdf, admissible):
    """Run the guard's own rules over the rendered page, as the guard does."""
    import check_demo_language as LANG
    text = LANG.pdftotext(pdf)
    if text is None:
        raise SystemExit("REFUSE: the planted page is unreadable, so this "
                         "drive read nothing")
    refused, released = [], []
    for rule in SCREEN.NUMERIC_RULES:
        for phrase, _pos in rule["fn"](text):
            token = SCREEN.hit_token(phrase)
            if (rule["id"] in SCREEN.ALLOWLISTED_RULES
                    and ADMIT.token_admissible(token, admissible)):
                released.append((rule["id"], phrase))
            else:
                refused.append((rule["id"], phrase))
    return text, refused, released


def _has(pairs, value):
    return any(abs(float(SCREEN.hit_token(p).replace(",", "")) - value) < 1e-9
               for _rid, p in pairs if SCREEN.hit_token(p))


def main():
    work = tempfile.mkdtemp(prefix="actC_drive_")
    fails = []
    try:
        pdf = build_mutated_sheet(work)
        print("planted sheet compiled, and pdflatex returned success -- which "
              "is the point: the toolchain is happy to render a withheld "
              "temperature onto a filmed surface.\n")

        print("DIRECTION 1 -- EMPTY GRADED SET (the live state today)")
        text, refused, released = sweep(pdf, ())
        print("   refused %d token(s), released %d" % (len(refused),
                                                       len(released)))
        for rid, phrase in refused:
            print("      [%s] %r" % (rid, phrase))
        if not _has(refused, GRADED):
            fails.append("direction 1 did not refuse %.4f" % GRADED)
        if not _has(refused, NEIGHBOUR):
            fails.append("direction 1 did not refuse %.4f" % NEIGHBOUR)
        if released:
            fails.append("direction 1 released %d token(s) with nothing "
                         "graded" % len(released))

        print("\nDIRECTION 2 -- PLANTED GRADED SET {%.4f}" % GRADED)
        text, refused, released = sweep(pdf, (GRADED,))
        print("   refused %d token(s), released %d" % (len(refused),
                                                       len(released)))
        for rid, phrase in released:
            print("      RELEASED [%s] %r" % (rid, phrase))
        for rid, phrase in refused:
            print("      refused  [%s] %r" % (rid, phrase))
        if not _has(released, GRADED):
            fails.append("direction 2 did not release the graded %.4f"
                         % GRADED)
        if not _has(refused, NEIGHBOUR):
            fails.append("direction 2 released the NON-graded neighbour "
                         "%.4f" % NEIGHBOUR)

        print("\nDIRECTION 3 -- the committed sheet, unmutated, both settings")
        for label, admissible in (("empty", ()), ("graded", (GRADED,))):
            _t, ref, rel = sweep(os.path.join(HERE, "ACT_C_GATE_sheet.pdf"),
                                 admissible)
            print("   %-7s set: %d refused, %d released" % (label, len(ref),
                                                            len(rel)))
            if ref or rel:
                fails.append("the committed sheet is not clean under the "
                             "%s set" % label)
    finally:
        shutil.rmtree(work, ignore_errors=True)

    if fails:
        sys.stderr.write("\nDRIVE FAILED:\n")
        for f in fails:
            sys.stderr.write("  - %s\n" % f)
        return 2
    print("\nDRIVE PASS -- with nothing graded the guard refuses both planted "
          "temperatures; with one graded it releases exactly that one and "
          "still refuses its neighbour; and the committed sheet is clean "
          "under both.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
