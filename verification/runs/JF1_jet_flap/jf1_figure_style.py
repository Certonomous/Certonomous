#!/usr/bin/env python3
"""ONE typographic style for every jet-flap figure, and a refusal if it is not
actually available.

Sanaa's overnight order is "all plots latexfied". Real ``text.usetex`` is not
reachable on this box: it needs a ``cm-super`` install behind root, and root is
hers alone. The no-root route reaches the same visible result, because the
printed result sheet is already typeset by real pdflatex in Latin Modern --
registering the same Latin Modern faces with matplotlib makes every figure
typographically identical to the sheet, with mathematics staying Computer
Modern where it already is.

WHY THIS IS ONE FILE AND NOT THREE COPIES OF AN rcParams BLOCK. Three
generators draw the figures on this screen. This campaign has already paid for
the two-implementations lesson once, on the settle band, where two copies of
one arithmetic agreed right up until they did not. A style block is no
different: three copies drift, and the drift is invisible because a figure
that looks slightly wrong looks like a figure.

WHY IT RAISES RATHER THAN FALLS BACK, WHICH IS THE LOAD-BEARING PART. If the
faces are missing, matplotlib does not fail. It picks the next serif on the
list, draws a perfectly good figure in DejaVu, and prints a warning nobody
reads. The source would then say Latin Modern, the artifact would ship DejaVu,
and the only way to know would be to inspect the embedded fonts of a PDF
already signed off. That is the same shape as a hard-coded constant wearing a
measured caption: a claim in the source that the artifact does not carry. So
this checks the four faces are on disk, registers them, asserts the family is
in matplotlib's own list afterwards, and REFUSES if it is not.

ACCEPTANCE IS ``pdffonts``, NOT A READ OF THIS FILE. A source read says what
the code means; only the embedded fonts say what shipped.
"""

from __future__ import annotations

import os

#: Where the Latin Modern OpenType faces live on this box. VERIFIED by listing
#: the directory, not by recall: an earlier reading of this path gave
#: ``/usr/share/texlive/texmf-dist/fonts/opentype/public/lm/``, which does not
#: exist at all.
LM_DIR = "/usr/share/texmf/fonts/opentype/public/lm"

#: The four faces a serif family needs to render regular, bold, italic and
#: bold-italic without matplotlib synthesising any of them.
#: plus the monospace face, because one figure sets ``family="monospace"`` on a
#: three-number label and a serif-only registration leaves that ONE text object
#: in DejaVu Sans Mono. Measured, not reasoned: pdffonts on the rendered
#: resolution page reported exactly one DejaVu face while every other figure
#: reported none, which is the whole argument for testing the artifact.
LM_FACES = ("lmroman10-regular.otf", "lmroman10-bold.otf",
            "lmroman10-italic.otf", "lmroman10-bolditalic.otf",
            # Regular and italic only: this distribution ships no
            # ``lmmono10-bold.otf`` -- VERIFIED by the refusal, which fired on
            # exactly that name when it was listed here on the strength of a
            # naming pattern rather than a directory listing. Nothing in these
            # figures sets bold monospace.
            "lmmono10-regular.otf", "lmmono10-italic.otf")

#: The family names the faces register under, and the names the rcParams ask
#: for. Asserted present after registration rather than assumed.
LM_FAMILY = "Latin Modern Roman"
LM_MONO_FAMILY = "Latin Modern Mono"


class StyleRefused(RuntimeError):
    """The typographic style asked for is not the one that would be drawn."""


def latin_modern_rc(directory: str = LM_DIR) -> dict:
    """Register Latin Modern with matplotlib and return the rcParams for it.

    Raises :class:`StyleRefused` if any face is missing or if the family is
    absent from matplotlib's own font list after registration. It never falls
    back: a silent fallback is how a figure ships in a font its source denies.
    """
    from matplotlib import font_manager

    missing = [face for face in LM_FACES
               if not os.path.isfile(os.path.join(directory, face))]
    if missing:
        raise StyleRefused(
            "Latin Modern is not installed where this style expects it: "
            "%s missing from %s. Refusing rather than drawing in whatever "
            "serif matplotlib finds next, because that figure would look "
            "finished and be in the wrong font."
            % (", ".join(missing), directory))

    for face in LM_FACES:
        font_manager.fontManager.addfont(os.path.join(directory, face))

    names = {font.name for font in font_manager.fontManager.ttflist}
    for family in (LM_FAMILY, LM_MONO_FAMILY):
        if family not in names:
            raise StyleRefused(
                "the Latin Modern faces were registered and %r is still not "
                "in matplotlib's font list; the figures would be drawn in a "
                "fallback face while this file says otherwise" % family)

    return {
        "font.family": "serif",
        "font.serif": [LM_FAMILY],
        "font.monospace": [LM_MONO_FAMILY],
        "mathtext.fontset": "cm",
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
    }


# ---------------------------------------------------------------------------
# Where the text a figure no longer carries actually goes
# ---------------------------------------------------------------------------

#: One file per figure, beside the figures. Sanaa's standard moves every
#: explanation printed inside a figure out to the sheet text as one compact
#: paragraph per figure. The sheet's own source is held by another lane
#: tonight and must not be touched, so the paragraphs are STAGED here, named
#: by the figure they belong to, rather than deleted to satisfy a style rule.
NOTES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "artefacts", "figure_notes")


def sheet_note(stem: str, title: str, paragraph: str) -> str:
    """Write one figure's sheet paragraph, and return where it went.

    ONE FILE PER FIGURE, ON PURPOSE. Three generators draw these figures and
    each knows only its own; a single shared file would be clobbered by
    whichever generator ran last, and the disclosure would vanish exactly the
    way a caveat deleted by hand does. Each generator rewrites its own figure's
    note on every run, so a note cannot go stale against the figure it
    describes.

    The paragraph is not a caption and is not limited to twenty words: it is
    the place the long explanation is allowed to be long. What it must not do
    is live only here while the figure says something different -- a
    disclosure that exists only in a file nobody reads is worth nothing, which
    is the lesson this staging exists to answer rather than to repeat.
    """
    os.makedirs(NOTES_DIR, exist_ok=True)
    path = os.path.join(NOTES_DIR, "%s.md" % stem)
    body = "\n".join(line.rstrip() for line in paragraph.strip().splitlines())
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("# %s\n\n%s\n" % (title, body))
    return path


def main() -> int:
    """Report whether the style is available, for a check without a figure."""
    try:
        rc = latin_modern_rc()
    except StyleRefused as exc:
        print("STYLE REFUSED: %s" % exc)
        return 2
    print("Latin Modern registered from %s" % LM_DIR)
    for key, value in sorted(rc.items()):
        print("  %-16s %s" % (key, value))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
