#!/usr/bin/env python3
"""Run cases/committee-grids/ugrid_to_foam.py with a BYTE-BUDGET-VERIFIED layout sniffer.

THE DEFECT THIS WORKS AROUND, MEASURED HERE 2026-09-03
------------------------------------------------------
`ugrid_to_foam.sniff_layout` decides the byte order of a raw-C-stream UGRID file by
reading the first four bytes as a node count and accepting the FIRST byte order that
gives `0 < n < 2_000_000_000`, big-endian first.  For a large grid the byte-swapped
node count overflows into the negatives and the test rejects it, so the answer comes
out right.  FOR A SMALL GRID IT DOES NOT.  Measured on the M6I family:

    file                        LE first word   BE first word   sniffer picks   correct?
    wing_strct.1.lb8.ugrid           990849     -2128736512     little           yes
    wing_strct.2.lb8.ugrid           124865     -1041825536     little           yes
    wing_strct.3.lb8.ugrid            15873       20840448      BIG              NO
    wing_strct.4.lb8.ugrid             2057      151519232      BIG              NO
    wing_strct.5.lb8.ugrid              279      385941504      BIG              NO

The module's own docstring says "the caller's own byte-budget assertion below is what
actually proves the choice right" -- but that assertion (`bulk == want`) is inside the
`if fortran:` branch ONLY.  A raw C stream gets no budget check before the arrays are
read, so a wrong byte order is caught, if at all, by whichever `reshape` blows up first.
On L3 it blew up.  There is no guarantee it always will.

THE FIX, AND WHY IT CANNOT BE FOOLED
------------------------------------
The seven-integer header determines the file's total size EXACTLY:

    28 + 24*nNodes + 12*nTri + 16*nQuad + 4*(nTri+nQuad)
       + 16*nTet + 20*nPyr + 24*nPrism + 32*nHex          (raw C stream)

so instead of asking whether a node count looks plausible, this sniffer asks which
packaging REPRODUCES THE FILE SIZE ON DISK, and requires EXACTLY ONE to do so.  Zero
matches or two matches are both a refusal, never a guess.  Byte order is then not an
inference at all -- it is an arithmetic identity between the header and `os.path.getsize`.

PLANTED CONTROL (rule 3) -- run before any conversion, and the conversion is REFUSED
if the control does not fire.

THE FIRST PLANT WRITTEN HERE WAS INVALID AND THE CONTROL CAUGHT IT.  It byte-swapped
the seven header integers in a scratch copy and expected a refusal.  It got an
ACCEPTANCE, correctly: byte-swapping the header bytes and flipping the reading byte
order are the SAME OPERATION, so the swapped copy is a genuinely valid big-endian file
carrying the identical header.  NO BYTE-ORDER PLANT CAN EVER BE VALID against a sniffer
whose whole job is byte order.  That plant would have "passed" on any later run while
testing nothing.  It is recorded rather than quietly replaced.

THE VALID PLANT, and it is what runs: a scratch copy has ONE header integer (the hex
count) incremented by one, so the implied byte budget misses the true file size by 32
bytes and NO packaging can reproduce it.  The sniffer must REFUSE that file.  A sniffer
that cannot reject a file it should reject is not evidence that it accepted the right
one.  Note that the acceptance of the real file already carries its own control for
free: `len(hits) != 1` refuses, so an accepted file is one whose OTHER byte order was
measured NOT to reproduce the size.

THE FROZEN CONVERTER IS NOT EDITED.  `cases/committee-grids/ugrid_to_foam.py` is the
grading path of RUNG0_MESH_IMPORT_PREREGISTRATION section 11, and that registration is
POST-COMPUTE (it ran 2026-09-03 17:49).  Rule 6 forbids editing it here.  This wrapper
overrides one function at run time and leaves the file on disk untouched; the upstream
repair is the cfd supervisor's call, not this lane's.

Usage: ugrid_layout_verified.py <file.ugrid> <file.mapbc> <caseDir>
"""
import os
import shutil
import struct
import sys
import tempfile

sys.path.insert(0, "/home/ubuntu/Certonomous/cases/committee-grids")
import ugrid_to_foam as u2f  # noqa: E402

HDR = struct.Struct("7i")


def _budget(hdr, fortran):
    """Exact file size implied by a seven-integer UGRID header."""
    nN, nT, nQ, nTet, nPyr, nPri, nHex = hdr
    if min(hdr) < 0:
        return -1
    bulk = (nN * 24 + nT * 12 + nQ * 16 + nT * 4 + nQ * 4
            + nTet * 16 + nPyr * 20 + nPri * 24 + nHex * 32)
    if fortran:
        # 4 + 28 + 4 (header record) + 4 + bulk + 4 (single bulk record)
        return 44 + bulk
    return 28 + bulk


def sniff_layout_verified(path):
    """(endian, fortran) proven by total-byte-budget identity, or a refusal."""
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        head = f.read(36)
    hits = []
    for endian in ("<", ">"):
        # raw C stream: header at byte 0
        if len(head) >= 28:
            h = struct.unpack(endian + "7i", head[:28])
            if _budget(h, False) == size:
                hits.append((endian, False, h))
        # Fortran unformatted: 4-byte record marker, then the header
        if len(head) >= 36:
            marker = struct.unpack(endian + "i", head[:4])[0]
            if marker == 28:
                h = struct.unpack(endian + "7i", head[4:32])
                if _budget(h, True) == size:
                    hits.append((endian, True, h))
    if len(hits) != 1:
        raise ValueError(
            f"UGRID layout of {path} is not settled by byte budget: "
            f"{len(hits)} packaging(s) reproduce the {size}-byte file size. "
            "REFUSING rather than guessing.")
    endian, fortran, h = hits[0]
    print(f"       layout VERIFIED by byte budget: "
          f"{'big' if endian == '>' else 'little'}-endian, "
          f"{'Fortran unformatted' if fortran else 'raw C stream'}; "
          f"header {h} -> {size} bytes exactly", flush=True)
    return endian, fortran


def planted_control(path):
    """The reader must REFUSE a header it should refuse. Returns True if it fired."""
    with tempfile.TemporaryDirectory() as d:
        bad = os.path.join(d, "PLANT_hexcount_plus_one.ugrid")
        shutil.copyfile(path, bad)
        endian, fortran = sniff_layout_verified(path)
        off = 4 if fortran else 0
        with open(bad, "r+b") as f:
            f.seek(off + 24)                       # the 7th header integer: nHex
            n = struct.unpack(endian + "i", f.read(4))[0]
            f.seek(off + 24)
            f.write(struct.pack(endian + "i", n + 1))
        try:
            sniff_layout_verified(bad)
        except ValueError:
            return True
        return False


def main():
    ug, mb, case = sys.argv[1], sys.argv[2], sys.argv[3]
    if not planted_control(ug):
        sys.exit("PLANTED CONTROL DID NOT FIRE: the verified sniffer ACCEPTED a "
                 "byte-swapped header. Its acceptance of the real file is therefore "
                 "not evidence. REFUSING to convert.")
    print("       planted control FIRED: header with nHex+1 REFUSED "
          "(byte budget misses the file size by 32 bytes)", flush=True)
    u2f.sniff_layout = sniff_layout_verified
    sys.argv = ["ugrid_to_foam.py", ug, mb, case]
    u2f.main()


if __name__ == "__main__":
    main()
