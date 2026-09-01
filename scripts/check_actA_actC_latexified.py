#!/usr/bin/env python3
"""Refuse unless every Act A and Act C figure really went through LaTeX.

Sanaa's 2026-09-01 04:20Z directive requires ALL PLOTS LATEXFIED.  Setting
``text.usetex`` is not evidence that it happened: matplotlib will happily draw
the glyphs itself if the rcParam is lost, overridden or never reached, and the
figure then looks latexified without being it.  That is the false-zero shape
this lab refuses, so this check reads the answer back off disk instead of
trusting the switch.

Method: ``pdffonts`` on each committed figure PDF.  Text set by LaTeX embeds
Latin Modern faces (``LMRoman10-Regular`` and friends).  Text drawn by
matplotlib embeds DejaVu.  The two are not confusable.

The check carries its own planted control: it renders one throwaway figure with
usetex OFF and refuses if that figure is NOT reported as un-latexified.  A
reader that cannot see the failure case is not evidence of the passing one.

Exit 0 = every figure latexified.  Exit 2 = at least one is not, or the
reader failed its own control.
"""

import os
import subprocess
import sys
import tempfile


REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMO = os.path.join(REPO, "docs", "campaigns", "T-family", "demo")
DIRS = [os.path.join(DEMO, "figures_actA"), os.path.join(DEMO, "figures")]

LATEX_STEM = "LM"          # Latin Modern, set by LaTeX
MPL_STEM = "DejaVu"        # matplotlib's own glyphs


def pdf_fonts(path):
    out = subprocess.run(["pdffonts", path], capture_output=True, text=True)
    if out.returncode != 0:
        return None
    names = []
    for line in out.stdout.splitlines()[2:]:
        if line.strip():
            names.append(line.split()[0].split("+", 1)[-1])
    return sorted(set(names))


def classify(fonts):
    if fonts is None:
        return "UNREADABLE"
    if not fonts:
        return "NO TEXT"
    if any(f.startswith(MPL_STEM) for f in fonts):
        return "NOT LATEXIFIED"
    if any(f.startswith(LATEX_STEM) for f in fonts):
        return "LATEXIFIED"
    return "UNKNOWN FAMILY"


def planted_control():
    """Prove the reader can see a NON-latexified figure before trusting a pass."""
    import matplotlib
    matplotlib.use("Agg")
    matplotlib.rcParams["text.usetex"] = False
    import matplotlib.pyplot as plt

    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "control.pdf")
        fig = plt.figure(figsize=(1.4, 1.0))
        fig.text(0.1, 0.5, "control 312 K")
        fig.savefig(p)
        plt.close(fig)
        verdict = classify(pdf_fonts(p))

    if verdict != "NOT LATEXIFIED":
        sys.stderr.write(
            "REFUSE: the planted control was read as %r, not 'NOT "
            "LATEXIFIED'. This reader cannot see the failure it is meant to "
            "detect, so its passes are worthless.\n" % verdict)
        raise SystemExit(2)
    return verdict


def main():
    planted_control()
    print("planted control: a non-latexified figure IS detected as such\n")

    bad = 0
    n = 0
    for d in DIRS:
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if not name.endswith(".pdf"):
                continue
            n += 1
            path = os.path.join(d, name)
            fonts = pdf_fonts(path)
            verdict = classify(fonts)
            if verdict != "LATEXIFIED":
                bad += 1
            print("%-14s %-36s %s" % (verdict, name,
                                      " ".join(fonts or ["-"])[:70]))

    print("\n%d figures, %d latexified, %d not" % (n, n - bad, bad))
    if n == 0:
        sys.stderr.write("REFUSE: no figures found; nothing was checked.\n")
        raise SystemExit(2)
    if bad:
        raise SystemExit(2)
    print("PASS -- every Act A and Act C figure was set by LaTeX")
    return 0


if __name__ == "__main__":
    sys.exit(main())
