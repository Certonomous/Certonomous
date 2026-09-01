#!/usr/bin/env python3
"""Refuse if a sheet's LAST substantive line never reached the compiled page.

THE FAILURE THIS GUARDS, AND WHY IT IS NOT A ONE-OFF.  A one-page LaTeX sheet
whose content just exceeds the page silently DROPS its final line.  pdflatex
returns rc=0, reports "Output written ... (1 page)", and raises no overfull
warning at the console.  Page count is therefore NOT evidence of completeness:
a sheet can lose its tail and still report exactly the page count you expect.

Measured instances, all on docs/campaigns/T-family/demo/ACT_A_thermal_map_sheet.tex:
  * the pre-2026-09-01 sheet lost "All figures are read from solution files
    retained on disk" -- present at source, absent from the PDF, unnoticed;
  * during a routine table edit the same day, at three separate
    \\enlargethispage settings, the sheet reported "1 page" while dropping
    "16 operating points solved on this geometry, 39,680 cells".

THE ASYMMETRY THAT MAKES THIS WORSE THAN A COSMETIC BUG.  On this lab's sheets
the honesty statements sit LAST -- the limitations line, the mesh-count
statement, the "no error bar is quoted" note, the closing statement of fact.
A failure mode that deletes the final line therefore PREFERENTIALLY DELETES THE
CAVEATS Sanaa requires on screen, while leaving every headline number intact.
It removes exactly the text that makes the numbers honest, and it does so
silently.  That is why this belongs in code and not in one lane's habit.

METHOD.  Take the last substantive line of the .tex source -- the final line
carrying real prose, ignoring comments, \\end{document} and bare markup -- and
require it to appear in the pdftotext output of the compiled PDF as a
CONTIGUOUS PHRASE.  A bag-of-words test is not enough and was measured failing
on BOTH sheets -- do not "simplify" this back to a set test:

  * Act A, tail "16 operating points solved on this geometry, 39,680 cells":
    when it was dropped, exactly ONE of its words ("geometry") was absent from
    the page.  A single word carried the entire detection.
  * Act C, tail "one mesh, one time step, and no numerical error bar on any
    module number": when it was dropped, ZERO of its words were absent --
    error, bar, any, module and number all appear elsewhere on that sheet.  A
    word-set check would have passed COMPLETELY on a silently deleted
    limitation statement.

So the set test is not merely weaker; on Act C it is BLIND, and blind on
exactly the honesty statement this guard exists to protect.  Only the ordered
phrase is unique to the tail.

CONTROL.  The control compiles an overlong copy of a real sheet and REFUSES
unless this checker reports that tail as missing.  It grows the prose group
ABOVE the tail, because that is what a routine edit does and it is what
reproduces the defect -- filler appended at the end does NOT reproduce it, the
tail simply reflows onto page 2 and survives.  Twelve pad x \\enlargethispage
combinations of that first, wrong control gave ZERO reproductions while looking
like a working control.  A CONTROL THAT REPRODUCES A SUPERFICIALLY SIMILAR
FAILURE INSTEAD OF THE REAL ONE IS WORSE THAN NO CONTROL, BECAUSE IT CERTIFIES
THE WRONG THING -- it would have reported this guard as proven against a
page-overflow it never actually suffers.  Measured on the Act A sheet: ONE
added sentence is enough to trigger the silent loss, at every \\enlargethispage
setting tried between 30 and 60 pt.  A guard never shown catching the defect is
ceremony.

Exit 0 = every sheet's tail is on the page.  Exit 2 = a tail was dropped, or
the control failed.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile


REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMO = os.path.join(REPO, "docs", "campaigns", "T-family", "demo")
SHEETS = [
    os.path.join(DEMO, "ACT_A_thermal_map_sheet.tex"),
    os.path.join(DEMO, "ACT_C_battery_module_sheet.tex"),
]

# Markup-only fragments that are not the sheet's last SUBSTANTIVE line.
_SKIP = re.compile(r"^\s*(%|\\end\{document\}|\\end\{|\\begin\{|\\vspace|"
                   r"\\newpage|\\clearpage|\\hfill|\\\\|\}*\s*$)")


def last_substantive_line(tex_path):
    """The final source line carrying prose the reader should see."""
    with open(tex_path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    for line in reversed(lines):
        if _SKIP.match(line):
            continue
        # Needs at least three real words once markup is stripped.
        if len(words(line)) >= 3:
            return line
    return None


def words(tex_line):
    """Plain words of a LaTeX line, in the form pdftotext would show them."""
    s = re.sub(r"(?<!\\)%.*", "", tex_line)
    s = re.sub(r"\$[^$]*\$", " ", s)              # maths renders differently
    s = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?", " ", s)
    s = re.sub(r"[{}&~^_\\]", " ", s)
    return [w for w in re.findall(r"[A-Za-z][A-Za-z'-]{2,}", s)]


def page_words(pdf_path):
    """The page's words as an ordered sequence, so a PHRASE can be matched."""
    out = subprocess.run(["pdftotext", "-q", pdf_path, "-"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        return None
    return [w.lower() for w in re.findall(r"[A-Za-z][A-Za-z'-]{2,}",
                                          out.stdout)]


def tail_present(tex_path, pdf_path):
    """(ok, tail_line, detail). ok is None when it cannot be judged.

    The tail is matched as a CONTIGUOUS PHRASE, not as a bag of words.  Its
    individual words -- "solved", "points", "cells" -- recur all over these
    sheets, so a set test can be satisfied entirely by other lines and would
    report a dropped tail as present.  The ordered phrase is unique to it.
    """
    tail = last_substantive_line(tex_path)
    if tail is None:
        return None, None, None
    pw = page_words(pdf_path)
    if pw is None:
        return None, tail, None
    need = [w.lower() for w in words(tail)]
    if not need:
        return None, tail, None
    joined_page = " " + " ".join(pw) + " "
    joined_need = " " + " ".join(need) + " "
    if joined_need in joined_page:
        return True, tail, ""
    absent = [w for w in need if w not in set(pw)]
    detail = ("phrase absent from the page; %s"
              % ("words never appearing anywhere: %s" % ", ".join(absent[:8])
                 if absent else "its words appear only in other lines"))
    return False, tail, detail


def compile_and_require_tail(tex_path):
    """Compile ``tex_path`` in place and REFUSE if its last line was dropped.

    The shared body behind every sheet's build path, so a sheet cannot be left
    looking finished with its final line silently deleted.  Raises
    ``SystemExit(2)`` on failure; returns the tail line on success.
    """
    sys.stdout.flush()          # so a refusal reads in order on a terminal
    workdir = os.path.dirname(os.path.abspath(tex_path))
    pdf, _ = compile_tex(tex_path, workdir)
    if pdf is None:
        sys.stderr.write("REFUSE: %s does not compile.\n"
                         % os.path.basename(tex_path))
        raise SystemExit(2)
    for ext in (".aux", ".log", ".out"):
        stale = tex_path[:-4] + ext
        if os.path.exists(stale):
            os.remove(stale)

    ok, tail, detail = tail_present(tex_path, pdf)
    if ok is None:
        sys.stderr.write("REFUSE: could not judge whether %s rendered its "
                         "tail.\n" % os.path.basename(tex_path))
        raise SystemExit(2)
    if not ok:
        sys.stderr.write(
            "\nREFUSE: THE SHEET'S LAST LINE DID NOT REACH THE PAGE.\n"
            "  sheet:        %s\n"
            "  missing line: %s\n"
            "  %s\n"
            "pdflatex reported success and the page count looks right, and "
            "the line is gone anyway. On these sheets the last line is a\n"
            "limitation or a statement of fact Sanaa requires on screen, so "
            "this silently deletes a caveat and keeps every number.\n"
            "Shorten the prose above the tail until it fits; do NOT raise "
            "\\enlargethispage, which hides the loss instead of fixing it.\n"
            % (os.path.basename(tex_path), tail.strip()[:96], detail))
        raise SystemExit(2)
    print("tail check: %s kept its last line on the page"
          % os.path.basename(tex_path))
    return tail


def compile_tex(tex_path, workdir):
    out = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
         os.path.basename(tex_path)],
        cwd=workdir, capture_output=True, text=True)
    pdf = os.path.join(workdir,
                       os.path.basename(tex_path)[:-4] + ".pdf")
    return (pdf if os.path.exists(pdf) else None), out.stdout


def selftest():
    """Compile an overlong copy whose tail cannot fit, and require detection."""
    src = SHEETS[0]
    if not os.path.exists(src):
        sys.stderr.write("REFUSE: cannot run the control; %s missing\n" % src)
        raise SystemExit(2)
    with tempfile.TemporaryDirectory() as d:
        dst = os.path.join(d, os.path.basename(src))
        shutil.copy(src, dst)
        text = open(dst, encoding="utf-8").read()
        # Grow the block ABOVE the tail, which is how a routine prose edit
        # does it. Appending filler at the very end does NOT reproduce the
        # bug -- the tail simply flows onto page 2 and survives. The defect
        # needs the page to stay at one page while the tail is squeezed out,
        # and that is what growing the preceding block causes. Measured: one
        # extra sentence is enough.
        tail = last_substantive_line(dst)
        i = text.index(tail)
        # Grow the text INSIDE the last prose group before the tail, not
        # between groups: filler in its own paragraph simply reflows onto
        # page 2 and the tail survives, which does not exercise the defect.
        j = text.rfind(".}", 0, i)
        if j < 0:
            sys.stderr.write("REFUSE: the control could not find a prose "
                             "group above the tail to grow.\n")
            raise SystemExit(2)
        filler = (" Additional sentence added by the control to grow the "
                  "block above the tail." * 4)
        text = text[:j] + filler + text[j:]
        open(dst, "w", encoding="utf-8").write(text)
        pdf, _ = compile_tex(dst, d)
        if pdf is None:
            sys.stderr.write("REFUSE: the control copy did not compile, so "
                             "the control proved nothing.\n")
            raise SystemExit(2)
        ok, tail, missing = tail_present(dst, pdf)
        if ok is not False:
            sys.stderr.write(
                "REFUSE: the overlong control page did NOT report a dropped "
                "tail (ok=%r). This checker cannot see the failure it exists "
                "for, so its passes are worthless.\n" % (ok,))
            raise SystemExit(2)
        print("control: an overlong sheet IS reported as losing its tail "
              "-- %s" % missing)


def main():
    selftest()
    bad = 0
    checked = 0
    for tex in SHEETS:
        pdf = tex[:-4] + ".pdf"
        name = os.path.basename(tex)
        if not os.path.exists(tex):
            print("SKIP (no source) %s" % name)
            continue
        if not os.path.exists(pdf):
            sys.stderr.write("REFUSE: %s is not compiled; a tail that was "
                             "never rendered cannot be checked.\n" % name)
            raise SystemExit(2)
        ok, tail, missing = tail_present(tex, pdf)
        checked += 1
        if ok is None:
            print("UNREADABLE   %s" % name)
            bad += 1
            continue
        if ok:
            print("tail on page %s\n     last line: %s"
                  % (name, tail.strip()[:96]))
        else:
            bad += 1
            print("*** TAIL DROPPED %s" % name)
            print("     last line: %s" % tail.strip()[:96])
            print("     %s" % missing)
            print("     the page count will NOT show this; the line is gone.")

    print("\n%d sheet(s) checked, %d losing their tail" % (checked, bad))
    if checked == 0:
        sys.stderr.write("REFUSE: no sheet was checked.\n")
        raise SystemExit(2)
    if bad:
        raise SystemExit(2)
    print("PASS -- every sheet's last substantive line reached its page")
    return 0


if __name__ == "__main__":
    sys.exit(main())
