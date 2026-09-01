"""Shared LaTeX text rendering for every demo-act figure.

Sanaa's 2026-09-01 04:20Z directive requires ALL PLOTS LATEXFIED.  Before this
module the four figure generators set only ``mathtext.fontset``, which is
matplotlib's *imitation* of LaTeX drawn with DejaVu glyphs; no LaTeX ran.  This
module switches every generator onto a real LaTeX text pipeline so that the
glyphs on screen are the ones ``latex`` itself sets.

Family: Latin Modern (``lmodern``), the Type-1 successor to Computer Modern.
Both acts import this one module, so Act A and Act C carry the same serif text
and the same serif maths.

Verification, not assertion
---------------------------
An rcParam that silently falls back to DejaVu looks exactly like success, which
is the false-zero shape this lab refuses.  ``selftest()`` therefore renders a
throwaway PDF and reads the font names back out of it, refusing unless the
embedded fonts really are Latin Modern.  ``scripts/check_thermal_latexified.py``
runs the same read-back over every committed figure.

Escaping
--------
Under ``text.usetex`` the string is LaTeX source, so ``%``, ``_``, ``&`` and
``#`` outside maths would end the line or crash the run.  ``tex_text()`` escapes
those in the text segments only and leaves ``$...$`` maths untouched.  The
corpus was measured, not guessed: all 484 distinct strings the four generators
render were captured and inspected, and every ``_`` in them already sits inside
maths.
"""

import subprocess

import matplotlib


# Latin Modern for text and for maths, plus the two packages matplotlib's own
# usetex support file expects to be able to load.
PREAMBLE = "\n".join([
    r"\usepackage[T1]{fontenc}",
    r"\usepackage{lmodern}",
    r"\usepackage{amsmath}",
    r"\usepackage{amssymb}",
])

# The font names `pdffonts` must report for the text to have gone through
# LaTeX.  Latin Modern subsets are emitted as `XXXXXX+LMRoman10-Regular` and
# friends; DejaVu here means matplotlib drew the glyphs itself and no LaTeX ran.
EXPECTED_FONT_STEM = "LM"
FORBIDDEN_FONT_STEM = "DejaVu"


def rcparams(base_font_size=9):
    """The rcParams every demo figure shares."""
    return {
        "text.usetex": True,
        "text.latex.preamble": PREAMBLE,
        "font.family": "serif",
        "font.size": base_font_size,
        "axes.titlesize": base_font_size,
        "axes.labelsize": base_font_size,
        # Tick labels carry U+2212 MINUS SIGN by default, which 8-bit LaTeX
        # cannot set.  matplotlib wraps numeric ticks in \mathdefault{} under
        # usetex, so the ASCII hyphen still renders as a true minus.
        "axes.unicode_minus": False,
        "pdf.fonttype": 42,
        # Under usetex the SVG backend emits glyph outlines, so this is inert;
        # it is kept so a generator run with usetex disabled still behaves.
        "svg.fonttype": "none",
    }


def apply(plt, base_font_size=9, extra=None):
    """Apply the shared LaTeX style to ``plt``, then prove LaTeX really ran."""
    params = rcparams(base_font_size)
    if extra:
        params.update(extra)
    plt.rcParams.update(params)
    selftest()


_TEX_ESCAPE = {
    "%": r"\%",
    "&": r"\&",
    "#": r"\#",
    "_": r"\_",
}

_TEX_REPLACE = {
    "—": "---",   # em dash
    "–": "--",    # en dash
    "−": "-",     # minus sign
}


def tex_text(s):
    """Make ``s`` safe as LaTeX source, leaving ``$...$`` maths untouched.

    Segments alternate text, maths, text, ... on the ``$`` delimiter, so only
    the even-indexed segments are escaped.
    """
    if s is None:
        return s
    parts = str(s).split("$")
    for i in range(0, len(parts), 2):
        seg = parts[i]
        for bad, good in _TEX_REPLACE.items():
            seg = seg.replace(bad, good)
        for bad, good in _TEX_ESCAPE.items():
            seg = seg.replace(bad, good)
        parts[i] = seg
    return "$".join(parts)


def bold(s):
    """Wrap already-LaTeX-safe ``s`` in ``\\textbf{}``.

    matplotlib's ``weight="bold"`` is silently ignored under ``text.usetex``:
    the weight never reaches LaTeX, so a header row styled that way comes out
    in the regular face and nothing warns.  Emphasis has to be asked for in
    the LaTeX source instead.  This does NOT escape -- pass it through
    ``tex_text`` first if the string can carry ``%`` or ``_``.
    Each line is wrapped separately.  matplotlib typesets a multi-line string
    as one LaTeX run per line, so a single ``\\textbf{}`` spanning a newline
    arrives at LaTeX as unbalanced braces and the run dies with "Too many }'s".
    """
    if s is None or not str(s).strip():
        return s
    out = []
    for line in str(s).split("\n"):
        if not line.strip() or line.startswith(r"\textbf{"):
            out.append(line)
        else:
            out.append(r"\textbf{%s}" % line)
    return "\n".join(out)


def bold_cells(table, predicate):
    """Set every ``table`` cell matching ``predicate((row, col))`` bold.

    Applied after ``Table`` construction, so it replaces the cell's text with
    bold LaTeX source rather than setting a weight LaTeX will never see.
    """
    for key, cell in table.get_celld().items():
        if predicate(key):
            t = cell.get_text()
            t.set_text(bold(t.get_text()))


def pdf_fonts(path):
    """Font names embedded in ``path``, subset prefixes stripped."""
    out = subprocess.run(["pdffonts", path], capture_output=True, text=True)
    names = []
    for line in out.stdout.splitlines()[2:]:
        if not line.strip():
            continue
        name = line.split()[0]
        names.append(name.split("+", 1)[-1])
    return sorted(set(names))


_SELFTEST_DONE = []


def selftest():
    """Render a throwaway PDF and read its fonts back off disk.

    Refuses unless LaTeX really set the glyphs.  This is the planted control
    for the whole latexification: a reader that cannot tell Latin Modern from
    DejaVu is not evidence of anything.
    """
    if _SELFTEST_DONE:
        return
    import os
    import tempfile
    import matplotlib.pyplot as plt

    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "selftest.pdf")
        fig = plt.figure(figsize=(1.4, 1.0))
        fig.text(0.1, 0.5, r"Peak $T_{\max}$ 312 K")
        fig.savefig(p)
        plt.close(fig)
        fonts = pdf_fonts(p)

    if any(f.startswith(FORBIDDEN_FONT_STEM) for f in fonts):
        raise SystemExit(
            "REFUSE: LaTeX text rendering fell back to matplotlib's own "
            "glyphs -- embedded fonts %s. The figures would look latexified "
            "and not be." % (fonts,))
    if not any(f.startswith(EXPECTED_FONT_STEM) for f in fonts):
        raise SystemExit(
            "REFUSE: no Latin Modern font embedded; got %s. Refusing rather "
            "than writing figures whose typography cannot be verified."
            % (fonts,))
    _SELFTEST_DONE.append(fonts)
    return fonts


if __name__ == "__main__":
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    apply(plt)
    print("latex_style selftest PASS -- embedded fonts:", _SELFTEST_DONE[0])
    print("tex_text('Change, %') ->", repr(tex_text("Change, %")))
    print("tex_text('$U_\\\\infty$ 40 %') ->",
          repr(tex_text(r"$U_\infty$ 40 %")))
