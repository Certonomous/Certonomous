#!/usr/bin/env python3
"""A1WRT -- THE PATCH-IDENTITY INSTRUMENT.  `G-PATCH` clauses 1 and 2, host side.

The A1WR L3 mesh's two bounding planes are `type symmetry`, not `empty`, so
OpenFOAM assembles a z-momentum equation on a mesh ONE CELL THICK.  A1WRT repairs
that for its `empty` unit.  **`empty` is not a one-word edit** (PREREGISTRATION
section 2.2): the mesh `boundary` file AND every field in `0.orig/` must agree, or
the case either will not start or -- the class this lab has been bitten by twice
-- starts and silently does something else.

THREE THINGS THIS FILE REFUSES TO DO, EACH BECAUSE OF A SPECIFIC FAILURE:

1. **IT NEVER SEDS THE WHOLE FILE.**  The patches are NAMED `symmetry1` and
   `symmetry2`.  A global `s/symmetry/empty/` renames the patches themselves and
   produces a mesh whose boundary names no longer match the fields -- a corruption
   that looks like a repair.  Every rewrite here is scoped to a NAMED BLOCK and
   touches only that block's `type` and `inGroups` VALUES.

2. **IT NEVER REPORTS A ZERO IT CANNOT DEFEND** (CLAUDE.md rule 3).  Every check
   asserts its own trip count.  A regex that matches nothing yields "no wrong
   entries found", which reads exactly like "every entry is right" -- the same
   vacuous pass a loop that iterates zero times gives.  So each verification
   states how many sites it EXPECTED to inspect, how many it ACTUALLY inspected,
   and REFUSES when those differ.  A file it cannot read is UNMEASURED, never 0.

3. **IT NEVER CONVERTS WITHOUT READING BACK.**  A rewrite asserts the bytes
   changed, re-reads them from disk through the SAME reader the verifier uses,
   and asserts the new identity landed.  A no-op mutation followed by a passing
   check is a control that proves nothing.

THE SITE COUNT IS FIXED BY THE REGISTRATION AND IS NOT DISCOVERED AT RUN TIME:
2 patches x (1 mesh boundary entry + 7 field entries) = 16 sites.  Discovering
the expected count from the same data being checked is how a truncated file
passes: it would expect what it found.

Self-test: `python3 a1wrt_patch_assert.py --selftest` builds a synthetic case,
drives every refusal branch through PLANTED mutants, and asserts each verdict
FLIPPED.  Exit 0 only if every control both fires and stays silent where it must.

EXIT CODES:  0 verified  |  7 PATCH REFUSAL, distinct and never a default
             2 usage / unreadable input  |  9 selftest failure
"""
import re
import shutil
import sys
import tempfile
from pathlib import Path

RC_OK = 0
RC_PATCH_REFUSAL = 7
RC_USAGE = 2
RC_SELFTEST = 9

# ---------------------------------------------------------------------------
# REGISTERED, NOT DISCOVERED.  PREREGISTRATION section 2.2 clauses 1 and 2.
# ---------------------------------------------------------------------------
PATCHES = ("symmetry1", "symmetry2")
FIELDS = ("U", "p", "nut", "nuTilda", "k", "omega", "epsilon")
N_MESH_SITES = len(PATCHES)                    # 2
N_FIELD_SITES = len(PATCHES) * len(FIELDS)     # 14
N_SITES = N_MESH_SITES + N_FIELD_SITES         # 16
NFACES = 130304                                # MEASURED on the A1WR L3 mesh

VALID = ("symmetry", "empty")


class Refusal(Exception):
    """The honest answer is 'this instrument cannot tell', or 'it is wrong'."""


def _block(text: str, patch: str):
    """The NAMED patch block's body, or None.

    Anchored on a line that is the patch name ALONE, so `symmetry1` cannot be
    matched inside `symmetry10` and a stray mention in a comment cannot stand in
    for the block.
    """
    m = re.search(r"^[ \t]*" + re.escape(patch) + r"[ \t]*\r?\n[ \t]*\{(.*?)^[ \t]*\}",
                  text, re.M | re.S)
    return m if m else None


def read_type(text: str, patch: str) -> str:
    """The `type` VALUE inside the named block.  UNMEASURED is an exception."""
    m = _block(text, patch)
    if m is None:
        raise Refusal("no block for patch %r" % patch)
    t = re.search(r"\btype\s+(\w+)\s*;", m.group(1))
    if t is None:
        raise Refusal("block %r carries no `type` entry" % patch)
    return t.group(1)


def read_ingroups(text: str, patch: str):
    """The `inGroups` VALUE, or None where the entry is legitimately absent."""
    m = _block(text, patch)
    if m is None:
        raise Refusal("no block for patch %r" % patch)
    g = re.search(r"\binGroups\s+1\(\s*(\w+)\s*\)\s*;", m.group(1))
    return g.group(1) if g else None


def rewrite_block(text: str, patch: str, want: str) -> tuple[str, int]:
    """Rewrite ONLY this block's `type` and `inGroups` values.  Returns (text, n).

    The patch NAME is never touched -- see the file header, defect 1.
    """
    m = _block(text, patch)
    if m is None:
        raise Refusal("no block for patch %r" % patch)
    body = m.group(1)
    new, n = re.subn(r"(\btype\s+)\w+(\s*;)", r"\g<1>%s\g<2>" % want, body, count=1)
    if n != 1:
        raise Refusal("block %r: expected exactly 1 `type` entry to rewrite, hit %d"
                      % (patch, n))
    new2, n2 = re.subn(r"(\binGroups\s+1\(\s*)\w+(\s*\)\s*;)", r"\g<1>%s\g<2>" % want,
                       new, count=1)
    # inGroups is optional (the `inout` patch has none); rewriting 0 of them is
    # legal ONLY when the block genuinely has none, which is asserted here.
    if n2 == 0 and re.search(r"\binGroups\b", new):
        raise Refusal("block %r has an inGroups entry this rewrite did not match"
                      % patch)
    return text[:m.start(1)] + new2 + text[m.end(1):], 1 + n2


def _read(p: Path) -> str:
    """A file this instrument cannot read is UNMEASURED, never empty."""
    try:
        return p.read_text(errors="replace")
    except OSError as exc:
        raise Refusal("cannot read %s: %s" % (p, exc))


def boundary_path(case: Path) -> Path:
    p = case / "constant" / "polyMesh" / "boundary"
    if not p.is_file():
        raise Refusal("no mesh boundary file at %s -- UNMEASURED, not 'clean'" % p)
    return p


def verify(case: Path, want: str) -> list[str]:
    """Assert the identity ACTUALLY ON DISK, counting every site it inspects.

    Refuses on a wrong identity AND on an inspection count that is not exactly
    the registered 16 -- a truncated case that presents 3 sites, all correct, is
    not a case that passed.
    """
    if want not in VALID:
        raise Refusal("want=%r is not one of %s" % (want, VALID))
    notes, seen, wrong = [], 0, []

    btext = _read(boundary_path(case))
    for patch in PATCHES:
        t = read_type(btext, patch)
        g = read_ingroups(btext, patch)
        seen += 1
        if t != want:
            wrong.append("mesh boundary %s: type=%s, want %s" % (patch, t, want))
        if g is not None and g != want:
            wrong.append("mesh boundary %s: inGroups=1(%s), want 1(%s)" % (patch, g, want))
        nf = re.search(r"\bnFaces\s+(\d+)\s*;", _block(btext, patch).group(1))
        if nf is None:
            raise Refusal("mesh boundary %s carries no nFaces" % patch)
        if int(nf.group(1)) != NFACES:
            wrong.append("mesh boundary %s: nFaces=%s, registered %d -- THE MESH "
                         "IS NOT THE A1WR L3 MESH" % (patch, nf.group(1), NFACES))
        notes.append("  mesh boundary %-10s type=%-8s inGroups=%-8s nFaces=%s"
                     % (patch, t, "1(%s)" % g if g else "ABSENT", nf.group(1)))

    fdir = case / "0.orig"
    if not fdir.is_dir():
        raise Refusal("no 0.orig/ under %s -- UNMEASURED, not 'clean'" % case)
    for fname in FIELDS:
        fp = fdir / fname
        if not fp.is_file():
            raise Refusal("0.orig/%s is absent -- a field this instrument cannot "
                          "read is UNMEASURED, never counted as correct" % fname)
        ftext = _read(fp)
        for patch in PATCHES:
            t = read_type(ftext, patch)
            seen += 1
            if t != want:
                wrong.append("0.orig/%s %s: type=%s, want %s" % (fname, patch, t, want))
        notes.append("  0.orig/%-9s %s" % (fname, " ".join(
            "%s=%s" % (p, read_type(ftext, p)) for p in PATCHES)))

    # ---- THE TRIP COUNT.  This is the clause that makes the zero above mean
    # ---- something: `wrong == []` is evidence only if the inspection happened.
    if seen != N_SITES:
        raise Refusal(
            "inspected %d sites, REGISTERED %d (%d mesh + %d field). A check that "
            "finds nothing wrong having inspected fewer sites than it should is "
            "not a check that passed -- it is a check that did not run."
            % (seen, N_SITES, N_MESH_SITES, N_FIELD_SITES))
    if wrong:
        # FINDINGS and SITES are different counts and are never conflated: one
        # site can yield two findings (a `type` and an `inGroups`), so "18 of 16"
        # is not a paradox but it IS a sentence a reader would stumble on.
        raise Refusal("patch identity is NOT %r -- %d finding(s) across %d sites "
                      "inspected:\n    %s"
                      % (want, len(wrong), seen, "\n    ".join(wrong)))
    notes.append("  A1WRT_PATCH_VERIFIED want=%s sites_inspected=%d/%d wrong=0"
                 % (want, seen, N_SITES))
    return notes


def convert(case: Path, want: str) -> list[str]:
    """Rewrite to `want`, then READ BACK THROUGH `verify` and assert it landed."""
    if want not in VALID:
        raise Refusal("want=%r is not one of %s" % (want, VALID))
    notes, changed = [], 0

    bp = boundary_path(case)
    before = _read(bp)
    text = before
    for patch in PATCHES:
        text, n = rewrite_block(text, patch, want)
        changed += n
    if text == before:
        # NOT an error by itself -- the case may already be correct -- but it is
        # stated, because "0 bytes changed" and "the rewrite worked" are
        # different facts and a reader is entitled to which one happened.
        notes.append("  mesh boundary: already %s, 0 bytes changed" % want)
    else:
        bp.write_text(text)
        notes.append("  mesh boundary: rewritten to %s" % want)

    for fname in FIELDS:
        fp = case / "0.orig" / fname
        if not fp.is_file():
            raise Refusal("0.orig/%s absent -- cannot convert what is not there" % fname)
        b4 = _read(fp)
        t = b4
        for patch in PATCHES:
            t, n = rewrite_block(t, patch, want)
            changed += n
        if t != b4:
            fp.write_text(t)
    notes.append("  rewrite sites touched: %d (registered %d)" % (changed, N_SITES))
    if changed != N_SITES - _n_optional_ingroups(case, want):
        # inGroups is optional per block; the count is therefore bounded, not
        # exact, and the AUTHORITATIVE check is the read-back below.
        notes.append("  (inGroups entries are optional per block, so the touch "
                     "count is a bound; the READ-BACK below is the assertion)")
    notes.append("  --- READ BACK FROM DISK, through the same reader ---")
    notes.extend(verify(case, want))
    return notes


def _n_optional_ingroups(case: Path, want: str) -> int:
    try:
        b = _read(boundary_path(case))
        return sum(1 for p in PATCHES if read_ingroups(b, p) is None)
    except Refusal:
        return 0


# ---------------------------------------------------------------------------
# SELFTEST.  Every branch driven by a PLANTED mutant on real bytes, each read
# back and asserted to have LANDED before the verdict is taken.
# ---------------------------------------------------------------------------
_BOUNDARY = """FoamFile { version 2.0; format ascii; class polyBoundaryMesh;
    object boundary; }
4
(
    symmetry1
    {
        type            symmetry;
        inGroups        1(symmetry);
        nFaces          130304;
        startFace       260099;
    }
    symmetry2
    {
        type            symmetry;
        inGroups        1(symmetry);
        nFaces          130304;
        startFace       390403;
    }
    wing
    {
        type            wall;
        inGroups        1(wall);
        nFaces          509;
        startFace       520707;
    }
    inout
    {
        type            patch;
        nFaces          509;
        startFace       521216;
    }
)
"""

_FIELD = """FoamFile { version 2.0; format ascii; class volScalarField; object %s; }
internalField   uniform 0;
boundaryField
{
    symmetry1
    {
        type            symmetry;
    }
    symmetry2
    {
        type            symmetry;
    }
    wing
    {
        type            zeroGradient;
    }
    inout
    {
        type            zeroGradient;
    }
}
"""


def _mkcase(root: Path) -> Path:
    case = root / "case"
    (case / "constant" / "polyMesh").mkdir(parents=True)
    (case / "0.orig").mkdir(parents=True)
    (case / "constant" / "polyMesh" / "boundary").write_text(_BOUNDARY)
    for f in FIELDS:
        (case / "0.orig" / f).write_text(_FIELD % f)
    return case


def selftest() -> int:
    out, fails = [], []

    def chk(tag, ok, what, why=""):
        out.append("  %-3s %s %-62s %s" % (tag[0], tag[1], what, "PASS" if ok else "FAIL"))
        if why:
            out.append("        %s" % why)
        if not ok:
            fails.append(tag[0])

    def drives(case, want):
        """(verdict, message) from the REAL verifier."""
        try:
            verify(case, want)
            return "OK", ""
        except Refusal as exc:
            return "REFUSED", str(exc)

    with tempfile.TemporaryDirectory(prefix="a1wrt_patch_") as td:
        root = Path(td)

        # ---- P1/P2: the pristine case IS symmetry and is NOT empty ----------
        case = _mkcase(root)
        v, _ = drives(case, "symmetry")
        chk(("P1", "[+]"), v == "OK", "pristine A1WR-shaped case verifies as `symmetry`",
            "no false alarm on the configuration U1 actually runs")
        v, m = drives(case, "empty")
        chk(("P2", "[-]"), v == "REFUSED", "the SAME case REFUSES as `empty`",
            "the reader is shown able to return BOTH answers; a verifier that "
            "only ever says OK proves nothing")

        # ---- P3: convert, and the read-back is the assertion ----------------
        notes = convert(case, "empty")
        v, _ = drives(case, "empty")
        chk(("P3", "[+]"), v == "OK", "after convert -> verifies as `empty`",
            notes[-1].strip())
        v, _ = drives(case, "symmetry")
        chk(("P4", "[-]"), v == "REFUSED", "after convert -> REFUSES as `symmetry`",
            "the conversion is shown to have MOVED the answer, not merely to have run")

        # ---- P5: THE PATCH NAMES SURVIVED.  The defect a global sed causes. --
        btxt = (case / "constant" / "polyMesh" / "boundary").read_text()
        names_ok = all(_block(btxt, p) is not None for p in PATCHES)
        chk(("P5", "[!]"), names_ok,
            "the patch NAMES symmetry1/symmetry2 survived the conversion",
            "a global s/symmetry/empty/ renames the patches and corrupts the mesh")
        chk(("P6", "[!]"), read_type(btxt, "wing") == "wall"
            and read_type(btxt, "inout") == "patch",
            "the wing and inout patches were NOT touched",
            "the rewrite is scoped to the two named blocks and to nothing else")

        # ---- P7: ONE wrong field entry REFUSES (the silent-no-op class) -----
        case2 = _mkcase(root / "b")
        convert(case2, "empty")
        fp = case2 / "0.orig" / "nuTilda"
        b4 = fp.read_text()
        fp.write_text(b4.replace("type            empty;", "type            symmetry;", 1))
        if fp.read_text() == b4:
            return _emit(out + ["  CONTROL P7 DID NOT LAND"], ["P7"])
        v, m = drives(case2, "empty")
        chk(("P7", "[-]"), v == "REFUSED",
            "ONE field patch left `symmetry` on an `empty` mesh -> REFUSED",
            "a mesh patch typed empty beside a field patch typed symmetry is the "
            "silent-no-op class this lab has been bitten by twice")

        # ---- P8: A MISSING FIELD IS UNMEASURED, NEVER A PASS -----------------
        case3 = _mkcase(root / "c")
        convert(case3, "empty")
        (case3 / "0.orig" / "omega").unlink()
        v, m = drives(case3, "empty")
        chk(("P8", "[!]"), v == "REFUSED" and "UNMEASURED" in m,
            "a DELETED field -> REFUSED as UNMEASURED, not passed as 'nothing wrong'",
            "the planted-zero branch: 13 correct sites and one unreadable is not 16 correct sites")

        # ---- P9: THE TRIP COUNT ITSELF.  Truncate the boundary file. --------
        case4 = _mkcase(root / "d")
        bp = case4 / "constant" / "polyMesh" / "boundary"
        b4 = bp.read_text()
        bp.write_text(b4.replace("    symmetry2\n    {\n        type            symmetry;\n"
                                 "        inGroups        1(symmetry);\n"
                                 "        nFaces          130304;\n"
                                 "        startFace       390403;\n    }\n", "", 1))
        if bp.read_text() == b4:
            return _emit(out + ["  CONTROL P9 DID NOT LAND"], ["P9"])
        v, m = drives(case4, "symmetry")
        chk(("P9", "[!]"), v == "REFUSED",
            "a boundary file MISSING a registered patch -> REFUSED",
            "every remaining site is correct; the count is what catches it")

        # ---- P10: a WRONG MESH (nFaces) is refused, not silently graded -----
        case5 = _mkcase(root / "e")
        bp = case5 / "constant" / "polyMesh" / "boundary"
        b4 = bp.read_text()
        bp.write_text(b4.replace("nFaces          130304;", "nFaces          4032;", 1))
        if bp.read_text() == b4:
            return _emit(out + ["  CONTROL P10 DID NOT LAND"], ["P10"])
        v, m = drives(case5, "symmetry")
        chk(("P10", "[-]"), v == "REFUSED" and "L3" in m,
            "the COARSE 4,032-cell mesh presented as L3 -> REFUSED",
            "section 3.5: the coarse pair is a DIFFERENT ITEM and must not run here")

        # ---- P11: the reader refuses an unregistered target identity --------
        v, m = drives(case, "cyclic")
        chk(("P11", "[!]"), v == "REFUSED",
            "an identity outside the registered two -> REFUSED",
            "neither `symmetry` nor `empty` is not a third option to grade against")

    return _emit(out, fails)


def _emit(out, fails) -> int:
    sys.stdout.write("A1WRT PATCH-IDENTITY INSTRUMENT -- SELFTEST\n")
    sys.stdout.write("\n".join(out) + "\n")
    if fails:
        sys.stderr.write("SELFTEST FAILED: %s\n" % ", ".join(fails))
        return RC_SELFTEST
    sys.stdout.write("SELFTEST PASS: %d controls, both directions, every mutant "
                     "asserted to have landed before its verdict was taken.\n"
                     % len([l for l in out if l.strip().startswith(("P",))
                            and "PASS" in l]))
    return RC_OK


def main(argv) -> int:
    if "--selftest" in argv:
        return selftest()
    if len(argv) < 4 or argv[1] not in ("--verify", "--convert"):
        sys.stderr.write(
            "usage: a1wrt_patch_assert.py --verify  <case_dir> --want <symmetry|empty>\n"
            "       a1wrt_patch_assert.py --convert <case_dir> --want <symmetry|empty>\n"
            "       a1wrt_patch_assert.py --selftest\n")
        return RC_USAGE
    case = Path(argv[2])
    if "--want" not in argv:
        sys.stderr.write("A1WRT_PATCH REFUSE: --want is required and has no default. "
                         "An identity nobody stated is not an identity this "
                         "instrument will guess.\n")
        return RC_USAGE
    want = argv[argv.index("--want") + 1]
    if not case.is_dir():
        sys.stderr.write("A1WRT_PATCH REFUSE: %s is not a directory\n" % case)
        return RC_PATCH_REFUSAL
    try:
        notes = (convert if argv[1] == "--convert" else verify)(case, want)
    except Refusal as exc:
        sys.stderr.write("A1WRT_PATCH REFUSE (rc %d) case=%s want=%s\n  %s\n"
                         % (RC_PATCH_REFUSAL, case, want, exc))
        sys.stderr.write("  G-PATCH clauses 1 and 2 are host-side and PRE-PRIMAL: "
                         "no solver runs on an identity this instrument could not "
                         "confirm.\n")
        return RC_PATCH_REFUSAL
    sys.stdout.write("A1WRT_PATCH %s case=%s want=%s\n" % (argv[1][2:].upper(), case, want))
    sys.stdout.write("\n".join(notes) + "\n")
    return RC_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv))
