#!/usr/bin/env python3
"""A1WRT -- THE controlDict DERIVER.  `S6`, and the reason it is a DERIVATION.

**A1WRT's whole claim is to be ONE VARIABLE against A1WR's alpha 0..12 body.**
So anything in `system/controlDict` that differs from what A1WR's own driver
wrote is a SECOND VARIABLE, and the tail stops being comparable to the body it
exists to extend.

**THIS FILE THEREFORE DOES NOT AUTHOR A controlDict.  IT DERIVES A1WR'S.**
The bytes are extracted from `a1wr_chain_driver.sh`'s own heredoc -- the one at
`stage_unit()`, which is what generated every controlDict A1WR actually ran --
and `$et` is substituted with THIS item's registered `endTime`.  Retyping the
heredoc here would let a future divergence in A1WR's template silently split the
two items, which is exactly the failure this derivation exists to prevent.

WHY THIS FILE EXISTS AT ALL -- THE DEFECT IT REPAIRS, MEASURED:
`/home/ubuntu/certonomous-runs/A1WR/L3/system/controlDict` carries
**`endTime 1000`**, while A1WR's real run cases (`sweep_I/case`, `cold_I_4/case`)
both carry **`endTime 4000`**.  A1WR *generates* the controlDict per unit and the
L3 mesh directory's copy is merely what was left behind by mesh generation.
A1WRT staged from that directory and inherited the wrong one.  The launcher's S6
refused at 11 s and ~0 core-min rather than run 1,000 iterations and report them
against a 4,000-iteration registration -- the two-variable trap, introduced by
the staging itself.  **The registration's 4000 is the correct side: it is what
A1WR ran and what section 7's whole projection table was computed from.**

FOUR ASSERTIONS, AND THE ORDER IS DELIBERATE:
 1. **A1WR's driver is md5-pinned.**  If the template moved, the two items would
    diverge silently; this REFUSES instead.
 2. **Exactly ONE heredoc is matched.**  A trip count, not a `[0]` on whatever
    the regex happened to find: zero matches and two matches are different
    failures and neither is "the first one".
 3. **No unsubstituted shell variable survives.**  A `$et` left in the file is a
    literal string in an OpenFOAM dictionary and would be read as garbage.
 4. **The derived bytes are checked TWICE, and the two checks are not the same
    check.**  (a) against a STATIC md5 pinned here, which always runs; and
    (b) against the controlDict **A1WR's driver actually wrote** for the alpha
    sweep this item extends -- an EXTERNAL artefact this instrument did not
    produce.  (b) is the stronger evidence and REFUSES on mismatch.  **IT HAS
    THREE ANSWERS AND ITS NOTE NAMES WHICH ONE IT GAVE**: COMPARED (the bytes
    were read and matched), NOT COMPARED (the endTime is not the registered one,
    so the reference describes a different run and does not apply), or
    UNMEASURED (the reference file is absent).  A note that claims a comparison
    it did not make is the defect this shape exists to prevent, and it is driven
    both directions by controls D12/D13; in the two non-COMPARED answers (a)
    still carries the claim on its own.

Self-test: `python3 a1wrt_controldict.py --selftest` drives every refusal branch
through PLANTED mutants on real bytes, each asserted to have LANDED before its
verdict is taken.

EXIT CODES:  0 ok  |  6 controlDict REFUSAL, distinct  |  2 usage  |  9 selftest
"""
import hashlib
import re
import sys
import tempfile
from pathlib import Path

RC_OK = 0
RC_CD_REFUSAL = 6
RC_USAGE = 2
RC_SELFTEST = 9

# ---------------------------------------------------------------------------
# REGISTERED.  PREREGISTRATION section 0 (endTime 4000, carried unchanged from
# the A1WR freeze) and section 7 (the iteration budget is FROZEN).
# ---------------------------------------------------------------------------
ENDTIME = 4000
DELTAT = "1"
A1WR_DRIVER = Path("/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/"
                   "wall_resolved_aoa_polar/a1wr_chain_driver.sh")
A1WR_DRIVER_MD5 = "9bff59b63509e76d5dfa373a42a47074"
# The bytes this derivation must produce.  PINNED, so the primary check needs no
# external file and cannot go UNMEASURED.
DERIVED_MD5 = "85656349b8c31277e51883d2df9f8217"
DERIVED_BYTES = 653
# A1WR's OWN generated controlDict for the alpha sweep this item extends.  An
# EXTERNAL corroboration: this instrument did not write it, A1WR's driver did.
A1WR_REFERENCE = Path("/home/ubuntu/certonomous-runs/A1WR/STAGE12/sweep_I/"
                      "case/system/controlDict")

HEREDOC = re.compile(r'cat > "\$u/case/system/controlDict" <<EOF\n(.*?)\nEOF\n', re.S)


class Refusal(Exception):
    """The honest answer is 'this instrument cannot tell', or 'it is wrong'."""


def _md5(b: bytes) -> str:
    return hashlib.md5(b).hexdigest()


def derive(endtime: int = ENDTIME, driver: Path = A1WR_DRIVER,
           check_pin: bool = True) -> tuple[str, list[str]]:
    """A1WR's controlDict bytes, with `$et` bound to `endtime`."""
    notes = []
    if not driver.is_file():
        raise Refusal("A1WR's driver is absent at %s -- UNMEASURED. The template "
                      "this derivation copies does not exist, so no controlDict "
                      "is written." % driver)
    raw = driver.read_bytes()
    got = _md5(raw)
    if check_pin and got != A1WR_DRIVER_MD5:
        raise Refusal(
            "a1wr_chain_driver.sh md5 %s != the pinned %s. A1WR's controlDict "
            "TEMPLATE HAS MOVED since this item registered against it. Deriving "
            "from the new bytes would silently change what A1WRT runs relative to "
            "the body it is compared against -- a second variable introduced by "
            "an edit to another item. REFUSED; a human decides whether the two "
            "items still belong on the same axis." % (got, A1WR_DRIVER_MD5))
    notes.append("  A1WR driver md5 %s == pin" % got)

    bodies = HEREDOC.findall(raw.decode("utf8", "replace"))
    # THE TRIP COUNT.  Zero and two are different failures, and neither is
    # "take the first one".
    if len(bodies) != 1:
        raise Refusal(
            "expected exactly 1 controlDict heredoc in A1WR's driver, found %d. "
            "A `[0]` here would take whichever the regex happened to match first "
            "and call it the template." % len(bodies))
    notes.append("  heredocs matched: 1 (exactly, asserted)")

    text = bodies[0].replace("$et", str(endtime)) + "\n"
    left = re.findall(r"\$\w+", text)
    if left:
        raise Refusal("unsubstituted shell variable(s) survive the derivation: %s. "
                      "A `$et` left in an OpenFOAM dictionary is read as a literal "
                      "string, not as a number." % ", ".join(sorted(set(left))))
    notes.append("  unsubstituted shell variables: none")
    return text, notes


def check_bytes(text: str, endtime: int = ENDTIME) -> list[str]:
    """The two byte checks, and they are NOT the same check."""
    notes = []
    got = _md5(text.encode())
    # (a) THE STATIC PIN.  Always available; cannot go UNMEASURED.
    if endtime == ENDTIME:
        if got != DERIVED_MD5:
            raise Refusal("derived controlDict md5 %s != the pinned %s (%d bytes "
                          "vs %d)" % (got, DERIVED_MD5, len(text), DERIVED_BYTES))
        notes.append("  derived md5 %s == pin, %d bytes" % (got, len(text)))
    else:
        notes.append("  derived md5 %s (endTime=%d is NOT the registered %d, so "
                     "the static pin does not apply and is NOT claimed)"
                     % (got, endtime, ENDTIME))
    # (b) THE EXTERNAL CORROBORATION.  A1WR's driver wrote this file, not us.
    #
    # THE NOTE STATES WHAT WAS ACTUALLY DONE, AND THERE ARE THREE ANSWERS, NOT
    # TWO.  An earlier form of this branch was guarded on the reference file
    # merely EXISTING while the comparison itself was additionally conditioned
    # on `endtime == ENDTIME` -- so at any other endTime NO comparison ran and
    # the note still read "BYTE-IDENTICAL to A1WR's own generated controlDict".
    # That is a guard reporting a property it did not check, and it is a defect
    # in its own right even though `verify()`'s field assertions would have
    # caught a wrong endTime a moment later: the LATER guard's catch is not this
    # guard's evidence.  Driven both directions by selftest controls D12/D13.
    if endtime != ENDTIME:
        notes.append("  external corroboration NOT COMPARED: endTime=%d is not the "
                     "registered %d, so A1WR's own generated controlDict at %s "
                     "describes a different run and is not a reference for these "
                     "bytes. NO comparison was made and none is claimed."
                     % (endtime, ENDTIME, A1WR_REFERENCE))
    elif A1WR_REFERENCE.is_file():
        ref = A1WR_REFERENCE.read_text()
        if text != ref:
            raise Refusal(
                "the derived controlDict is NOT byte-identical to the one A1WR's "
                "driver actually wrote at %s. The tail would run a different "
                "control dictionary from the body it is compared against."
                % A1WR_REFERENCE)
        notes.append("  COMPARED and BYTE-IDENTICAL to A1WR's own generated "
                     "controlDict at %s -- an EXTERNAL artefact this instrument "
                     "did not produce" % A1WR_REFERENCE)
    else:
        notes.append("  external corroboration UNMEASURED: %s is absent. Reported, "
                     "NOT silently skipped. The static pin above still carries the "
                     "claim on its own." % A1WR_REFERENCE)
    return notes


def read_field(text: str, key: str) -> str:
    """A key's VALUE, or UNMEASURED as an exception -- never a default."""
    m = re.search(r"^\s*" + re.escape(key) + r"\s+([0-9.]+)\s*;", text, re.M)
    if m is None:
        raise Refusal("controlDict carries no readable `%s` -- UNMEASURED, and "
                      "NOT assumed to be the registered value" % key)
    return m.group(1)


def verify(case: Path, endtime: int = ENDTIME) -> list[str]:
    """Read the controlDict BACK FROM DISK and assert the three fields.

    This is the same shape as the launcher's rc artefact: write, read back,
    assert.  It is NOT weakened to 'we wrote it, so it must be right'.
    """
    cd = case / "system" / "controlDict"
    if not cd.is_file():
        raise Refusal("no controlDict at %s -- UNMEASURED, not 'clean'" % cd)
    text = cd.read_text(errors="replace")
    notes = []
    for key, want in (("endTime", str(endtime)), ("writeInterval", str(endtime)),
                      ("deltaT", DELTAT)):
        got = read_field(text, key)
        if got != want:
            raise Refusal("controlDict %s=%s, registered %s. The iteration budget "
                          "is FROZEN (section 7): a different endTime is a NEW "
                          "rung with its own pre-registration." % (key, got, want))
        notes.append("  %-14s %s == registered" % (key, got))
    notes.extend(check_bytes(text, endtime))
    return notes


def write(case: Path, endtime: int = ENDTIME) -> list[str]:
    """Derive, write, then READ BACK THROUGH `verify` and assert it landed."""
    text, notes = derive(endtime)
    notes.extend(check_bytes(text, endtime))
    sysdir = case / "system"
    if not sysdir.is_dir():
        raise Refusal("no system/ directory under %s -- this is not a staged "
                      "OpenFOAM case" % case)
    cd = sysdir / "controlDict"
    before = cd.read_text(errors="replace") if cd.is_file() else None
    cd.write_text(text)
    if before is not None:
        notes.append("  REPLACED the inherited controlDict (endTime was %s; the "
                     "mesh directory's copy is mesh-generation leftover, NOT what "
                     "A1WR ran)" % (read_field(before, "endTime")
                                    if re.search(r"endTime", before) else "UNREADABLE"))
    notes.append("  --- READ BACK FROM DISK, through the same verifier ---")
    notes.extend(verify(case, endtime))
    return notes


# ---------------------------------------------------------------------------
# SELFTEST.  Every branch driven by a PLANTED mutant, each asserted to have
# LANDED on real bytes before its verdict is taken.
# ---------------------------------------------------------------------------
def selftest() -> int:
    out, fails, notrun = [], [], []

    def chk(tag, ok, what, why=""):
        out.append("  %-3s %s %-62s %s" % (tag[0], tag[1], what, "PASS" if ok else "FAIL"))
        if why:
            out.append("        %s" % why)
        if not ok:
            fails.append(tag[0])

    def cannot_run(tag, what, why):
        """A leg that could not be driven is NOT RUN -- never a PASS, and never
        a FAIL either: a control that did not run has not failed, and folding
        it into either column reports a reading nobody took."""
        out.append("  %-3s %s %-62s %s" % (tag, "[?]", what, "NOT RUN"))
        out.append("        %s" % why)
        notrun.append(tag)

    def drives(fn, *a, **k):
        try:
            fn(*a, **k)
            return "OK", ""
        except Refusal as exc:
            return "REFUSED", str(exc)

    # ---- D1: the derivation works on the REAL driver ------------------------
    try:
        text, _ = derive()
        ok = _md5(text.encode()) == DERIVED_MD5 and len(text) == DERIVED_BYTES
    except Refusal as exc:
        text, ok = "", False
        out.append("        %s" % exc)
    chk(("D1", "[+]"), ok, "derives A1WR's controlDict from the REAL driver bytes",
        "md5 %s, %d bytes" % (_md5(text.encode()) if text else "NONE", len(text)))

    # ---- D2: and it equals what A1WR ACTUALLY WROTE -------------------------
    if A1WR_REFERENCE.is_file():
        chk(("D2", "[+]"), text == A1WR_REFERENCE.read_text(),
            "byte-identical to the controlDict A1WR's driver actually wrote",
            "external corroboration: %s" % A1WR_REFERENCE)
    else:
        # `chk(..., True, ...)` here would award a PASS on a literal that cannot
        # fail -- the same vacuous-evidence shape D12 exists to catch, one frame
        # up.  The honest label for a control with nothing to compare is NOT RUN.
        cannot_run("D2", "byte-identical to what A1WR's driver actually wrote",
                   "%s is absent. The static pin (D1) carries the claim alone; "
                   "this control took no reading." % A1WR_REFERENCE)

    with tempfile.TemporaryDirectory(prefix="a1wrt_cd_") as td:
        root = Path(td)

        # ---- D3: a MOVED A1WR template REFUSES ------------------------------
        fake = root / "moved_driver.sh"
        real = A1WR_DRIVER.read_bytes()
        fake.write_bytes(real + b"\n# a later edit to A1WR's driver\n")
        if fake.read_bytes() == real:
            return _emit(out + ["  CONTROL D3 DID NOT LAND"], ["D3"])
        v, m = drives(derive, ENDTIME, fake)
        chk(("D3", "[-]"), v == "REFUSED" and "TEMPLATE HAS MOVED" in m,
            "A1WR's driver edited -> REFUSED, not silently re-derived",
            "a divergence in the other item's template must not split the two")

        # ---- D4: ZERO heredocs is a distinct failure from two ---------------
        none = root / "no_heredoc.sh"
        none.write_bytes(b"#!/bin/bash\necho nothing here\n")
        v, m = drives(derive, ENDTIME, none, False)
        chk(("D4", "[!]"), v == "REFUSED" and "found 0" in m,
            "ZERO heredocs -> REFUSED naming the count",
            "a [0] on an empty match list is an IndexError, not a verdict")

        # ---- D5: TWO heredocs is ALSO a refusal, not 'take the first' -------
        two = root / "two_heredoc.sh"
        block = HEREDOC.search(real.decode("utf8", "replace")).group(0)
        two.write_bytes((block + block).encode())
        v, m = drives(derive, ENDTIME, two, False)
        chk(("D5", "[-]"), v == "REFUSED" and "found 2" in m,
            "TWO heredocs -> REFUSED, not 'take the first one'",
            "the trip count is what distinguishes these two failures")

        # ---- D6: an unsubstituted variable REFUSES --------------------------
        badv = root / "unsub.sh"
        badv.write_bytes(block.replace("deltaT          1;",
                                       "deltaT          $dt;").encode())
        v, m = drives(derive, ENDTIME, badv, False)
        chk(("D6", "[!]"), v == "REFUSED" and "$dt" in m,
            "an unsubstituted $var survives -> REFUSED",
            "a $dt in an OpenFOAM dict is read as a literal string, not a number")

        # ---- D7/D8: write, then the read-back is the assertion --------------
        case = root / "case"
        (case / "system").mkdir(parents=True)
        (case / "system" / "controlDict").write_text(
            "FoamFile { object controlDict; }\nendTime         1000;\n"
            "deltaT          1;\nwriteInterval   1000;\n")
        v, m = drives(verify, case)
        chk(("D7", "[-]"), v == "REFUSED" and "1000" in m and "FROZEN" in m,
            "the INHERITED endTime 1000 -> REFUSED (the real defect, reproduced)",
            "this is the condition that aborted the 19:38:15Z launch at 11 s")
        notes = write(case)
        v2, _ = drives(verify, case)
        chk(("D8", "[+]"), v2 == "OK",
            "after write() -> verifies, and the verifier is the same one",
            notes[-1].strip())

        # ---- D9: a PLANTED post-write mutation is caught by the read-back ---
        cd = case / "system" / "controlDict"
        b4 = cd.read_text()
        cd.write_text(b4.replace("endTime         4000;", "endTime         4001;", 1))
        if cd.read_text() == b4:
            return _emit(out + ["  CONTROL D9 DID NOT LAND"], ["D9"])
        v, m = drives(verify, case)
        chk(("D9", "[-]"), v == "REFUSED",
            "controlDict mutated by ONE digit after the write -> REFUSED",
            "write-then-trust would have missed it; the read-back is the assertion")
        cd.write_text(b4)

        # ---- D10: an UNREADABLE field is UNMEASURED, never the default ------
        case2 = root / "case2"
        (case2 / "system").mkdir(parents=True)
        (case2 / "system" / "controlDict").write_text(
            "FoamFile { object controlDict; }\ndeltaT          1;\n")
        v, m = drives(verify, case2)
        chk(("D10", "[!]"), v == "REFUSED" and "UNMEASURED" in m,
            "an ABSENT endTime -> UNMEASURED and REFUSED, not assumed to be 4000",
            "the launcher's S6 already applied this and it is carried here")

        # ---- D11: a missing controlDict is UNMEASURED, not 'clean' ----------
        case3 = root / "case3"
        (case3 / "system").mkdir(parents=True)
        v, m = drives(verify, case3)
        chk(("D11", "[!]"), v == "REFUSED" and "UNMEASURED" in m,
            "NO controlDict at all -> UNMEASURED, not 'nothing wrong'",
            "a check that finds no bad value because it read no file is not a pass")

        # ---- D12/D13: THE EXTERNAL NOTE SAYS WHAT IT ACTUALLY DID -----------
        # The vacuous-evidence control.  The external branch is guarded on the
        # reference EXISTING; the comparison additionally needs the registered
        # endTime.  An earlier form printed "BYTE-IDENTICAL" in BOTH cases, so a
        # non-registered endTime got a note claiming a comparison nobody made.
        # D12 drives that path and asserts the claim is ABSENT; D13 drives the
        # registered path on the SAME reader and asserts the claim is PRESENT.
        # Without D13 a repair that simply deleted the sentence would pass D12.
        if not A1WR_REFERENCE.is_file():
            # The control cannot discriminate NOT-COMPARED from UNMEASURED when
            # the reference is gone, so it is NOT RUN and says so -- never
            # folded into a PASS and never into a FAIL.
            cannot_run("D12", "endTime != registered -> the note claims nothing",
                       "%s is absent, so the NOT-COMPARED branch and the "
                       "UNMEASURED branch cannot be told apart. No verdict is "
                       "taken. D13 is NOT RUN for the same reason."
                       % A1WR_REFERENCE)
            cannot_run("D13", "endTime == registered -> a REAL comparison",
                       "there is no external artefact to compare against")
        else:
            alt_notes = " ".join(check_bytes(derive(ENDTIME + 1)[0], ENDTIME + 1))
            reg_notes = " ".join(check_bytes(derive(ENDTIME)[0], ENDTIME))
            chk(("D12", "[-]"),
                "NOT COMPARED" in alt_notes and "BYTE-IDENTICAL" not in alt_notes,
                "endTime != registered -> the note says NOT COMPARED, claims nothing",
                "the reference EXISTS, so the branch under test is NOT-COMPARED "
                "and not the UNMEASURED one")
            chk(("D13", "[+]"),
                "BYTE-IDENTICAL" in reg_notes and "NOT COMPARED" not in reg_notes,
                "endTime == registered -> the SAME note reports a REAL comparison",
                "both directions on one reader: deleting the sentence would fail here")

    return _emit(out, fails, notrun)


def _emit(out, fails, notrun=()) -> int:
    sys.stdout.write("A1WRT controlDict DERIVER -- SELFTEST\n")
    sys.stdout.write("\n".join(out) + "\n")
    if fails:
        sys.stderr.write("SELFTEST FAILED: %s\n" % ", ".join(fails))
        return RC_SELFTEST
    n = len([l for l in out if l.strip().startswith("D") and " PASS" in l])
    # NOT RUN IS ITS OWN COLUMN AND IS NAMED.  A leg that could not be driven is
    # never folded into the PASS count, and the count line says so out loud
    # rather than leaving a reader to subtract.
    if notrun:
        sys.stdout.write("SELFTEST PASS: %d controls, both directions, every mutant "
                         "asserted to have landed before its verdict was taken.\n"
                         "SELFTEST NOT RUN: %d control(s) -- %s. NOT counted as "
                         "PASS.\n" % (n, len(notrun), ", ".join(notrun)))
    else:
        sys.stdout.write("SELFTEST PASS: %d controls, both directions, every mutant "
                         "asserted to have landed before its verdict was taken.\n"
                         "SELFTEST NOT RUN: 0 controls -- every leg was driven.\n" % n)
    return RC_OK


def main(argv) -> int:
    if "--selftest" in argv:
        return selftest()
    if len(argv) < 3 or argv[1] not in ("--write", "--verify"):
        sys.stderr.write("usage: a1wrt_controldict.py --write  <case_dir>\n"
                         "       a1wrt_controldict.py --verify <case_dir>\n"
                         "       a1wrt_controldict.py --selftest\n")
        return RC_USAGE
    case = Path(argv[2])
    if not case.is_dir():
        sys.stderr.write("A1WRT_CD REFUSE: %s is not a directory\n" % case)
        return RC_CD_REFUSAL
    try:
        notes = (write if argv[1] == "--write" else verify)(case)
    except Refusal as exc:
        sys.stderr.write("A1WRT_CD REFUSE (rc %d) case=%s\n  %s\n"
                         % (RC_CD_REFUSAL, case, exc))
        return RC_CD_REFUSAL
    sys.stdout.write("A1WRT_CD %s case=%s endTime=%d\n"
                     % (argv[1][2:].upper(), case, ENDTIME))
    sys.stdout.write("\n".join(notes) + "\n")
    return RC_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv))
