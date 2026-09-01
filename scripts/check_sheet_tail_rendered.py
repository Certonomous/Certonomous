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
import time


REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMO = os.path.join(REPO, "docs", "campaigns", "T-family", "demo")
SHEETS = [
    os.path.join(DEMO, "ACT_A_thermal_map_sheet.tex"),
    # ⚠ SUPERSEDED, AND KEPT ANYWAY. The Act C content specification's section
    # 0 records that this is NOT the Act C sheet that goes on camera. It stays
    # in the list because dropping a sheet from a guard is a reduction in
    # coverage, and it still has a tail worth protecting.
    os.path.join(DEMO, "ACT_C_battery_module_sheet.tex"),
    # ADDED 2026-09-01. THE SHEET THAT ACTUALLY GOES ON CAMERA WAS NOT IN THIS
    # LIST. It was compiled through `compile_and_require_tail` by its own
    # builder, so its tail was checked at BUILD time -- but nothing checked it
    # afterwards, and a sheet is filmed long after it is built. On this one
    # the tail is the honesty statement: "the run completes, the gate refuses
    # it, and no thermal result exists."
    os.path.join(DEMO, "ACT_C_GATE_sheet.tex"),
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
    """Compile, and return the PDF **THIS** compile produced -- or ``None``.

    ==================================================================
    AMENDMENT 1 -- 2026-09-01.  THIS FUNCTION CERTIFIED A STALE PDF AS A
    SUCCESSFUL COMPILE, AND IT WAS MEASURED DOING IT.
    ==================================================================

    THE BEHAVIOUR THIS REPLACES, QUOTED AND STRUCK RATHER THAN REWRITTEN::

        ~~out = subprocess.run([...], cwd=workdir, capture_output=True)~~
        ~~pdf = os.path.join(workdir, basename[:-4] + ".pdf")~~
        ~~return (pdf if os.path.exists(pdf) else None), out.stdout~~

    An EXISTENCE test, and ``out.returncode`` captured and never read.  So
    when ``pdflatex`` failed under ``-halt-on-error`` and wrote nothing, the
    PREVIOUS pdf was still sitting in the workdir, this returned it, the tail
    guard read THAT file, found the tail on it, and the build printed success.

    MEASURED, and this is the authority for the amendment: on 2026-09-01 an
    Act C caption edit broke the sheet source, ``pdflatex`` produced no output
    file at all, and the builder reported *"the sheet's last line is verified
    present on the page"* over a PDF **83 minutes old**.  It was caught only
    because a downstream token count failed to move.

    THE SHAPE, because it is the same one this file already exists to fight:
    A GREEN RESULT FROM AN INSTRUMENT THAT COULD NOT SEE WHAT IT WAS ASKED
    ABOUT.  This guard was written because ``pdflatex`` reports success over a
    silently deleted last line; it then reported success over a silently
    absent whole document.  On a filmed sheet that means shooting the previous
    version of a screen while believing the edit landed.

    IT WAS ALSO AN INCONSISTENCY INSIDE THIS FILE, not a house style:
    :func:`page_words` twelve lines up already refuses on a non-zero
    ``returncode``.  Only this function threw the signal away.

    THREE CLAUSES, because each alone can be fooled:

    1. the target PDF is REMOVED before the compile, so a failed run leaves
       nothing to mistake for output;
    2. ``returncode`` is ASSERTED zero -- the signal that was being discarded;
    3. the PDF's mtime is asserted to POSTDATE the compile invocation, so a
       file restored by any other means is caught too.

    Driven both ways by :func:`selftest`: a deliberately broken source must
    return ``None`` and leave no PDF behind, and a good source must still
    compile and pass.  The positive arm is not decoration -- a guard that
    refused every compile would sail through a refusal-only test while making
    every sheet in the lab impossible to build.
    """
    pdf = os.path.join(workdir, os.path.basename(tex_path)[:-4] + ".pdf")
    if os.path.exists(pdf):
        os.remove(pdf)
    started = time.time()
    out = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
         os.path.basename(tex_path)],
        cwd=workdir, capture_output=True, text=True)
    if out.returncode != 0:
        sys.stderr.write(
            "REFUSE: pdflatex exited %d on %s. No sheet is produced by a "
            "failed compile, and the previous one is not this one's output.\n"
            % (out.returncode, os.path.basename(tex_path)))
        return None, out.stdout
    if not os.path.exists(pdf):
        sys.stderr.write("REFUSE: pdflatex reported success on %s and wrote "
                         "no output file.\n" % os.path.basename(tex_path))
        return None, out.stdout
    if os.path.getmtime(pdf) < started - 1.0:
        sys.stderr.write(
            "REFUSE: %s is OLDER than the compile that claims to have "
            "produced it (%.0f s before it began). A previous build is being "
            "read as this one's output.\n"
            % (os.path.basename(pdf), started - os.path.getmtime(pdf)))
        return None, out.stdout
    return pdf, out.stdout


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

    # ------------------------------------------------------------------
    # AMENDMENT 1's OWN CONTROL, BOTH ARMS.  A compile guard shown only to
    # refuse could be refusing everything, which would make every sheet in
    # the lab impossible to build and would still pass a refusal-only test.
    # ------------------------------------------------------------------
    with tempfile.TemporaryDirectory() as d:
        # THE COPY IS RENAMED, and that is not cosmetic. The negative arm
        # below deliberately fails a compile, and `compile_tex` names the
        # sheet in its refusal. Under the real basename that refusal reads
        # exactly like the Act A sheet failing to build -- measured on the
        # first run of this control, where it sat above the PASS line and
        # looked like a live defect. A control whose success output is
        # indistinguishable from a real failure will be acted on as one.
        dst = os.path.join(d, "CONTROL_deliberately_broken_sheet.tex")
        shutil.copy(src, dst)
        pdf_path = dst[:-4] + ".pdf"

        # POSITIVE ARM FIRST: an unmodified sheet must still compile, and the
        # PDF must be one this compile produced.
        started = time.time()
        pdf, _ = compile_tex(dst, d)
        if pdf is None or not os.path.exists(pdf):
            sys.stderr.write(
                "REFUSE: a GOOD source did not compile through the hardened "
                "path. A guard that refuses every compile makes every sheet "
                "in the lab unbuildable and would pass a refusal-only "
                "test.\n")
            raise SystemExit(2)
        if os.path.getmtime(pdf) < started - 1.0:
            sys.stderr.write("REFUSE: the good arm returned a PDF older than "
                             "its own compile.\n")
            raise SystemExit(2)
        print("control: a GOOD source compiles and returns a PDF newer than "
              "the compile that made it")

        # NEGATIVE ARM: break the source, leaving the good PDF in place. The
        # struck behaviour returned that PDF and the tail guard certified it.
        text = open(dst, encoding="utf-8").read()
        text = text.replace(r"\end{document}",
                            "\\undefinedcontrolmacro\n" + r"\end{document}")
        open(dst, "w", encoding="utf-8").write(text)
        stale_before = os.path.getmtime(pdf_path)
        bad, _ = compile_tex(dst, d)
        if bad is not None:
            sys.stderr.write(
                "REFUSE: a BROKEN source was accepted as a successful "
                "compile. This is the exact defect Amendment 1 exists for: a "
                "green result from an instrument that could not see what it "
                "was asked about.\n")
            raise SystemExit(2)
        if os.path.exists(pdf_path):
            sys.stderr.write(
                "REFUSE: a failed compile LEFT A PDF BEHIND (mtime %r). The "
                "next reader would find it and call it current.\n"
                % stale_before)
            raise SystemExit(2)
        print("control: a BROKEN source is refused AND leaves no PDF behind, "
              "so nothing stale survives for the tail guard to certify")


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
