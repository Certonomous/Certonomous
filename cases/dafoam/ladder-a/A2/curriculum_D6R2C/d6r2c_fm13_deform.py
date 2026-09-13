#!/usr/bin/env python
"""D6R2C arm FM13 -- THE GUARDED DEFORM PRODUCER.

WHY THIS FILE EXISTS, IN ONE PARAGRAPH.
`d6r2c_freshmesh.py` computes `rank0 = MPI.COMM_WORLD.rank == 0` at line 213 and
first USES it at line 301 -- 88 lines after `grid.writeToCGNS(surface_out)` at
line 268.  That write is therefore executed by ALL FOUR MPI RANKS ONTO ONE PATH.
In arm FM12 the four ranks collided: three `cgio_create_node:ADF 5` lines, rank 1
exited 1, and the output was 8,192 bytes against the 114,688 every prior arm
produced.  FM10 ran the BYTE-IDENTICAL command and won the race.  EVERY
FRESH-MESH ARM THIS FAMILY HAS EVER RUN WAS ROLLING THIS DICE, and a silent win
looks exactly like a correct run.

`d6r2c_freshmesh.py` IS FROZEN AND IS NOT EDITED (CLAUDE.md rule 6).  This file
imports it, asserts its md5 is the frozen one, and applies exactly ONE change:

    THE CGNS WRITE IS GUARDED TO RANK 0, WITH A COLLECTIVE BARRIER ON EITHER
    SIDE AND A POST-WRITE ASSERTION EXECUTED INDEPENDENTLY ON EVERY RANK.

The change is applied by rebinding `Grid.writeToCGNS`, NOT by copying
`phase_deform`'s body.  A copy would be a second 90-line producer free to drift
from the first; a rebind cannot drift, and the frozen module stays byte-for-byte
the file the family pins.

WHAT THE ASSERTION CHECKS, AND WHY IT IS A CONTENT CHECK AND NOT A SIZE CHECK.
MEASURED, 2026-09-13, in the pinned image, by driving the UNGUARDED path 12 times
at 4 ranks on measurably idle cores: 12 of 12 trials crashed, and the output size
ranged 12,288 -> 114,688 bytes.  FIVE OF TWELVE PRODUCED THE FULL, CORRECT
114,688 BYTES.  One such full-size output was captured and probed: it READ
SUCCESSFULLY, reported the correct 9 blocks and 1,215 points, and its coordinates
were IDENTICAL to the input to 0.0 exactly.

SO A SIZE-AND-READABILITY ASSERTION WOULD HAVE PASSED 5 OF 12 RACED WRITES.  It
is registered here as the limb that catches TRUNCATION -- which is what FM12
actually suffered -- and NOT as the instrument that detects the race.  The
instrument that removes the race is the rank-0 guard itself.  The assertion's
load-bearing limb is therefore limb 4: every rank re-reads the file from disk and
compares the coordinates against THE ARRAY IT ALREADY HOLDS IN MEMORY.  That is a
comparison against the answer, not against a proxy for the answer.

READING A CORRUPT CGNS CANNOT BE CAUGHT IN-PROCESS.  MEASURED on the preserved
8,192-byte FM12 artifact: `readGrid` does not raise a Python exception.  The ADF
C library prints `cgio_children_ids:ADF 11: Block/offset out of legal range.` and
TERMINATES THE PROCESS with rc 1.  A `try/except BaseException` around it never
runs.  Limbs 3 and 4 therefore execute in a SUBPROCESS, so a library abort
arrives as a non-zero return code that this file converts into its own registered
refusal instead of an opaque ADF line.

AND THE CORRUPT FILE IS NOT GARBAGE.  Its first 32 bytes are a perfectly valid
ADF signature, byte-identical in form to the good file's.  A header check would
pass it.  That is precisely why this failure is silent when it does not crash.

SUBMISSIONS PARKED (CLAUDE.md rule 7).  This is OUR defect in OUR script -- a FIX,
not a filing.  It is NOT an upstream DAFoam defect and no upstream report is
drafted or referenced.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys

# --------------------------------------------------------------------------
# THE FROZEN MODULE THIS FILE WRAPS, AND THE PIN THAT PROVES IT IS UNCHANGED
# --------------------------------------------------------------------------
FRESHMESH_MD5 = "1d15ce361673ca600d565280441b67e0"

# Registered from MEASUREMENT, not recall: the base surface read in the pinned
# image reports 9 blocks and 1,215 block-structured points
# (shapes [(3,21,1,3),(3,21,1,3),(21,21,1,3),(21,21,1,3),(3,3,1,3),(21,3,1,3),
#          (3,21,1,3),(21,3,1,3),(3,3,1,3)]).
CGNS_BLOCKS = 9
CGNS_BLOCK_STRUCTURED_POINTS = 1215

# DERIVED, and deliberately a LOWER BOUND that ignores every byte of ADF
# structure: a correct file must hold at least the raw coordinate payload,
# 1215 points x 3 components x 8 bytes/double.  It is NOT a number chosen to sit
# between the observed good and bad sizes.
MIN_CGNS_BYTES = CGNS_BLOCK_STRUCTURED_POINTS * 3 * 8          # = 29160

# The family's planted-perturbation constant (CLAUDE.md rule 3), reused by the
# content control so the plant is the family's and not a fresh invention.
PLANT = 1.234e-03

# The preserved FM12 evidence -- the KNOWN-BAD CONTROL, and it is NOT SYNTHETIC.
FM12_CORRUPT_CGNS = ("/home/ubuntu/certonomous-runs/"
                     "CURRICULUM-D6R2C-FM12-a2-wing-matched-lift-provenance/"
                     "FM12/Zo/surfaceMesh_final.cgns")
FM12_CORRUPT_BYTES = 8192


class GuardRefusal(Exception):
    pass


def _md5_file(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# --------------------------------------------------------------------------
# THE SUBPROCESS READER.  It is a separate process for one measured reason:
# a corrupt CGNS kills the reading process outright and cannot be caught.
# --------------------------------------------------------------------------
_READER = r'''
import sys, hashlib, numpy as np
from cgnsutilities.cgnsutilities import readGrid
g = readGrid(sys.argv[1])
h = hashlib.md5(); n = 0
for b in g.blocks:
    x = np.ascontiguousarray(np.asarray(b.coords, dtype=np.float64))
    n += x.shape[0] * x.shape[1] * x.shape[2]
    h.update(x.tobytes())
print("D6R2C_FM13_READ blocks=%d points=%d coord_md5=%s" % (len(g.blocks), n, h.hexdigest()))
'''


def read_cgns_in_subprocess(path):
    """Return (rc, blocks, points, coord_md5, raw). Never raises on a bad file."""
    p = subprocess.Popen([sys.executable, "-c", _READER, path],
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, _ = p.communicate()
    raw = out.decode("utf-8", "replace")
    blocks = points = None
    cmd5 = None
    for line in raw.splitlines():
        if line.startswith("D6R2C_FM13_READ "):
            for tok in line.split()[1:]:
                k, _, v = tok.partition("=")
                if k == "blocks":
                    blocks = int(v)
                elif k == "points":
                    points = int(v)
                elif k == "coord_md5":
                    cmd5 = v
    return p.returncode, blocks, points, cmd5, raw


def expected_coord_md5(blocks_coords):
    """md5 of the in-memory coordinates, in block order, exactly as the reader
    hashes them.  The parent holds this array already; nothing is read back from
    disk to build the expectation."""
    import hashlib as _h
    import numpy as np
    h = _h.md5()
    for x in blocks_coords:
        h.update(np.ascontiguousarray(np.asarray(x, dtype=np.float64)).tobytes())
    return h.hexdigest()


# --------------------------------------------------------------------------
# THE ASSERTION.  Four limbs.  It runs on EVERY RANK, independently.
# --------------------------------------------------------------------------
def assert_cgns_written(path, expect_md5=None, rank="?"):
    # limb 1 -- the file exists at all
    if not os.path.exists(path):
        raise GuardRefusal(
            "REFUSE_CGNS_ABSENT rank=%s path=%s -- the guarded write produced no "
            "file; the deform phase stops rather than hand an absent surface to "
            "the mesher" % (rank, path))

    # limb 2 -- TRUNCATION.  This is the limb that catches what FM12 suffered,
    # and it is registered as catching truncation and NOTHING MORE (see the
    # module docstring: 5 of 12 raced writes were FULL SIZE).
    size = os.path.getsize(path)
    if size < MIN_CGNS_BYTES:
        raise GuardRefusal(
            "REFUSE_CGNS_SHORT_WRITE rank=%s bytes=%d minimum=%d path=%s -- the "
            "minimum is DERIVED as %d block-structured points x 3 components x 8 "
            "bytes and ignores all ADF structure, so it is a true lower bound. "
            "FM12's raced write produced %d bytes here."
            % (rank, size, MIN_CGNS_BYTES, path,
               CGNS_BLOCK_STRUCTURED_POINTS, FM12_CORRUPT_BYTES))

    # limb 3 -- READABILITY AND STRUCTURE, in a subprocess because a corrupt
    # CGNS terminates the reading process and cannot be caught in-process.
    rc, blocks, points, cmd5, raw = read_cgns_in_subprocess(path)
    if rc != 0 or blocks is None:
        raise GuardRefusal(
            "REFUSE_CGNS_UNREADABLE rank=%s rc=%d bytes=%d path=%s -- the CGNS "
            "reader could not open the file the write produced.  Reader output:\n%s"
            % (rank, rc, size, path, raw.strip()[:600]))
    if blocks != CGNS_BLOCKS or points != CGNS_BLOCK_STRUCTURED_POINTS:
        raise GuardRefusal(
            "REFUSE_CGNS_STRUCTURE rank=%s blocks=%d/%d points=%d/%d path=%s -- "
            "the file reads but is not the surface this family registered"
            % (rank, blocks, CGNS_BLOCKS, points,
               CGNS_BLOCK_STRUCTURED_POINTS, path))

    # limb 4 -- CONTENT, AND THIS IS THE LOAD-BEARING LIMB.  The coordinates on
    # disk are compared against the array the caller ALREADY HOLDS IN MEMORY --
    # the answer itself, not a proxy for it.
    if expect_md5 is not None and cmd5 != expect_md5:
        raise GuardRefusal(
            "REFUSE_CGNS_CONTENT rank=%s coord_md5_on_disk=%s in_memory=%s "
            "bytes=%d path=%s -- the file is the right size and reads cleanly and "
            "its coordinates are NOT the ones this rank computed"
            % (rank, cmd5, expect_md5, size, path))

    return {"bytes": size, "blocks": blocks, "points": points,
            "coord_md5": cmd5, "content_checked": expect_md5 is not None}


# --------------------------------------------------------------------------
# THE ONE REGISTERED CHANGE, APPLIED BY REBINDING -- NOT BY COPYING
# --------------------------------------------------------------------------
def install_guarded_write():
    from mpi4py import MPI
    from cgnsutilities.cgnsutilities import Grid

    original = Grid.writeToCGNS
    comm = MPI.COMM_WORLD

    def guarded_writeToCGNS(self, path, *a, **kw):
        rank = comm.rank
        # the coordinates THIS rank believes it is writing, captured BEFORE the
        # write, from the object in memory
        expect = expected_coord_md5([b.coords for b in self.blocks])

        comm.Barrier()                       # no rank is still touching the path
        if rank == 0:
            original(self, path, *a, **kw)   # <-- ONE writer.  The race is gone.
        comm.Barrier()                       # every rank waits for the writer

        info = assert_cgns_written(path, expect_md5=expect, rank=rank)
        if rank == 0:
            try:
                with open(os.path.join(os.path.dirname(os.path.abspath(path)) or ".",
                                       "d6r2c_fm13_write_guard.json"), "w") as fh:
                    json.dump({"path": os.path.abspath(path),
                               "ranks": comm.size,
                               "writer_rank": 0,
                               "asserted_on_every_rank": True,
                               "min_cgns_bytes_derived": MIN_CGNS_BYTES,
                               "result": info}, fh, indent=2, sort_keys=True)
            except OSError:
                pass                          # a read-only dir never fails the run
        comm.Barrier()
        return None

    Grid.writeToCGNS = guarded_writeToCGNS
    return original


# --------------------------------------------------------------------------
def _freshmesh_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "d6r2c_freshmesh.py")


def guard_freshmesh_pin():
    p = _freshmesh_path()
    if not os.path.exists(p):
        raise GuardRefusal("REFUSE_FRESHMESH_ABSENT %s" % p)
    got = _md5_file(p)
    if got != FRESHMESH_MD5:
        raise GuardRefusal(
            "REFUSE_FRESHMESH_MD5 got %s want %s -- this file's ONE registered "
            "change is only provable against the frozen producer it wraps"
            % (got, FRESHMESH_MD5))
    return got


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="D6R2C FM13 guarded deform producer (wraps the frozen "
                    "d6r2c_freshmesh.py; rank-0 CGNS write + 4-limb assertion).")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check-known-bad", metavar="PATH", nargs="?",
                    const=FM12_CORRUPT_CGNS,
                    help="drive the assertion against the preserved corrupt "
                         "artifact; the guard MUST refuse it")
    ap.add_argument("--check-good", metavar="PATH",
                    help="drive the assertion against a file it must ACCEPT")
    ap.add_argument("--plant-control", metavar="PATH",
                    help="copy PATH, move one coordinate by PLANT, and require "
                         "limb 4 to see it")
    known, rest = ap.parse_known_args(argv)

    if known.selftest:
        return selftest()
    if known.check_known_bad is not None:
        return _drive_known_bad(known.check_known_bad)
    if known.check_good:
        return _drive_good(known.check_good)
    if known.plant_control:
        return _drive_plant(known.plant_control)

    # ---- the real run --------------------------------------------------
    guard_freshmesh_pin()
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import d6r2c_freshmesh as fm

    argv_real = list(sys.argv[1:] if argv is None else argv)
    if "--phase" in argv_real:
        ph = argv_real[argv_real.index("--phase") + 1]
        if ph != "deform":
            print("D6R2C_FM13 REFUSED\nREFUSE_PHASE this producer carries the "
                  "deform-write guard and is registered for --phase deform "
                  "only; got %r" % ph)
            return 2
    install_guarded_write()
    print("D6R2C_FM13_GUARD INSTALLED freshmesh_md5=%s min_cgns_bytes=%d "
          "limbs=exists,size,readable+structure,content" % (FRESHMESH_MD5, MIN_CGNS_BYTES))
    return fm.main(argv_real)


# --------------------------------------------------------------------------
# CONTROLS
# --------------------------------------------------------------------------
def _drive_known_bad(path):
    print("CONTROL C1 -- KNOWN-BAD, NOT SYNTHETIC: the preserved FM12 artifact")
    print("  path  %s" % path)
    if not os.path.exists(path):
        print("  CONTROL FAIL the preserved evidence is not on disk"); return 1
    print("  bytes %d" % os.path.getsize(path))
    try:
        assert_cgns_written(path, expect_md5=None, rank="control")
    except GuardRefusal as e:
        print("  GUARD REFUSED -- as required:\n    %s" % str(e).split("\n")[0])
        return 0
    print("  CONTROL FAIL the guard ACCEPTED the corrupt artifact. "
          "A guard that has never said no is not a guard.")
    return 1


def _drive_good(path):
    print("CONTROL C3 -- POSITIVE: a correct CGNS must be ACCEPTED")
    print("  path  %s  bytes %d" % (path, os.path.getsize(path)))
    try:
        info = assert_cgns_written(path, expect_md5=None, rank="control")
    except GuardRefusal as e:
        print("  CONTROL FAIL the guard refused a good file:\n    %s" % e); return 1
    print("  GUARD ACCEPTED blocks=%d points=%d bytes=%d coord_md5=%s"
          % (info["blocks"], info["points"], info["bytes"], info["coord_md5"]))
    return 0


def _drive_plant(path):
    """CONTROL C2 -- PLANTED CONTENT (CLAUDE.md rule 3).  Limb 4 compares against
    an in-memory expectation; the plant moves the DISK side, so a reader that
    cannot see the plant is refused."""
    import shutil
    import tempfile
    print("CONTROL C2 -- PLANTED CONTENT, plant = %.6e m" % PLANT)
    rc0, b0, p0, md5_clean, _ = read_cgns_in_subprocess(path)
    if rc0 != 0:
        print("  CONTROL FAIL the clean file could not be read"); return 1
    print("  clean coord_md5 %s  (blocks=%d points=%d)" % (md5_clean, b0, p0))

    d = tempfile.mkdtemp(prefix="fm13plant_")
    tgt = os.path.join(d, "planted.cgns")
    shutil.copy2(path, tgt)
    planter = (
        "import sys, numpy as np\n"
        "from cgnsutilities.cgnsutilities import readGrid\n"
        "g = readGrid(sys.argv[1])\n"
        "x = np.asarray(g.blocks[0].coords, dtype=np.float64).copy()\n"
        "x[0, 0, 0, 0] += %r\n"
        "g.blocks[0].coords = x\n"
        "g.writeToCGNS(sys.argv[1])\n"
        "print('PLANTED')\n" % PLANT)
    pr = subprocess.run([sys.executable, "-c", planter, tgt],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if pr.returncode != 0:
        print("  CONTROL FAIL could not plant: %s"
              % pr.stdout.decode("utf-8", "replace")[:300])
        return 1
    rc1, b1, p1, md5_planted, _ = read_cgns_in_subprocess(tgt)
    if rc1 != 0:
        print("  CONTROL FAIL the planted file could not be read"); return 1
    print("  planted coord_md5 %s" % md5_planted)
    if md5_planted == md5_clean:
        print("  CONTROL FAIL the reader CANNOT SEE a %.6e m plant. "
              "A zero from a blind reader is not evidence (rule 3)." % PLANT)
        return 1
    print("  the reader SEES the plant -- the md5 moved")
    # and the guard, given the CLEAN expectation, must refuse the planted file
    try:
        assert_cgns_written(tgt, expect_md5=md5_clean, rank="control")
    except GuardRefusal as e:
        print("  GUARD REFUSED the planted file -- as required:\n    %s"
              % str(e).split("\n")[0])
        # and it must ACCEPT it when handed the matching expectation, or the
        # limb is refusing everything rather than refusing a mismatch
        try:
            assert_cgns_written(tgt, expect_md5=md5_planted, rank="control")
            print("  GUARD ACCEPTED the same file against its OWN md5 -- limb 4 "
                  "refuses a MISMATCH, not merely any file it is shown")
            return 0
        except GuardRefusal as e2:
            print("  CONTROL FAIL limb 4 refuses even a matching expectation: %s" % e2)
            return 1
    print("  CONTROL FAIL limb 4 accepted content it was told not to expect")
    return 1


def selftest():
    rc = 0

    def check(name, got, want):
        nonlocal rc
        ok = got == want
        print("SELFTEST %s %s (got %r want %r)"
              % ("ok " if ok else "FAIL", name, got, want))
        if not ok:
            rc = 1

    check("MIN_CGNS_BYTES is DERIVED from the registered point count",
          MIN_CGNS_BYTES, CGNS_BLOCK_STRUCTURED_POINTS * 3 * 8)
    check("the derived minimum is 29160", MIN_CGNS_BYTES, 29160)
    check("FM12's 8192-byte artifact is BELOW the derived minimum",
          FM12_CORRUPT_BYTES < MIN_CGNS_BYTES, True)
    check("a correct 114688-byte file is ABOVE it", 114688 > MIN_CGNS_BYTES, True)
    # THE LIMB-2 HONESTY CLAUSE, asserted rather than merely written in prose:
    check("a FULL-SIZE raced write is NOT caught by limb 2 -- measured, 5 of 12",
          114688 < MIN_CGNS_BYTES, False)

    # limb 1 and limb 2 drive without the pinned image
    import tempfile
    d = tempfile.mkdtemp(prefix="fm13self_")
    absent = os.path.join(d, "nope.cgns")
    try:
        assert_cgns_written(absent, rank="selftest")
        check("an absent file is refused", "accepted", "refused")
    except GuardRefusal as e:
        check("an absent file is refused", str(e).split()[0], "REFUSE_CGNS_ABSENT")

    short = os.path.join(d, "short.cgns")
    with open(short, "wb") as fh:
        fh.write(b"\xc0\xa8\xa3\xa9ADF Database Version A02011>" + b" " * (FM12_CORRUPT_BYTES - 32))
    check("the short fixture is exactly FM12's size",
          os.path.getsize(short), FM12_CORRUPT_BYTES)
    try:
        assert_cgns_written(short, rank="selftest")
        check("a short file is refused", "accepted", "refused")
    except GuardRefusal as e:
        check("a short file is refused", str(e).split()[0],
              "REFUSE_CGNS_SHORT_WRITE")

    # AND THE SHORT FIXTURE CARRIES A VALID ADF HEADER -- so limb 2, not a
    # header check, is what refuses it.  Measured on the real artifact.
    with open(short, "rb") as fh:
        hdr = fh.read(32)
    if os.path.exists(FM12_CORRUPT_CGNS):
        with open(FM12_CORRUPT_CGNS, "rb") as fh:
            real_hdr = fh.read(32)
        check("the fixture's ADF signature is the REAL artifact's", hdr, real_hdr)
    else:
        print("SELFTEST note the preserved FM12 artifact is not on this box; "
              "the header identity clause is NOT exercised")

    check("the frozen producer's pin is the FM12 as-run md5",
          FRESHMESH_MD5, "1d15ce361673ca600d565280441b67e0")
    try:
        got = guard_freshmesh_pin()
        check("the frozen producer beside this file matches its pin",
              got, FRESHMESH_MD5)
    except GuardRefusal as e:
        check("the frozen producer beside this file matches its pin", str(e), "ok")

    print("SELFTEST %s" % ("PASS" if rc == 0 else "FAIL"))
    return rc


if __name__ == "__main__":
    try:
        sys.exit(main())
    except GuardRefusal as e:
        print("D6R2C_FM13 REFUSED\n%s" % e)
        sys.exit(2)
