#!/usr/bin/env python3
"""control_assert_guards_under_O.py -- THE MEASUREMENT THAT MAKES L-470 CITABLE.

It is easy to *assert* that `python3 -O` deletes asserts. This runs the old and the
repaired `ugrid_to_foam.py` against the same malformed UGRID under both interpreter
modes and reports what each actually did.

THE EXHIBIT, and it is the whole point: under `python3 -O` the OLD converter does not
merely lose a warning — **it writes a complete OpenFOAM mesh from a file it has already
been given evidence is malformed**, and exits 0. Nothing downstream can tell.

WHY THIS SPECIMEN. The plant is a **raw C stream** (`.b8`) with 8 trailing bytes. That
class matters more than any other: of the old converter's eight guards, the byte-budget
check was **doubly** conditional — inside `if fortran:` *and* an `assert` — so a raw C
stream never reached it at all, and `assert nbnd == ndecl`, the **only** structural check
such a file did receive, was an assert too. **Under `-O` a `.b8` grid converted with no
validation whatsoever.**

A CONTROL THAT CANNOT FIRE IS WORSE THAN NO CONTROL (L-467), so this one is required to
DISCRIMINATE: the old form must pass under `python3` and fail to guard under `python3 -O`,
and the repaired form must guard under both. If the four cells do not come out that way
the control REFUSES rather than reporting a result.

USAGE
    control_assert_guards_under_O.py --old <path to the pre-repair converter>
                                     [--new <path>] [--json PATH]
The old converter is not stored here; it is recovered from git, e.g.
    git show ace20cb1:cases/committee-grids/ugrid_to_foam.py > /tmp/old_conv.py
Exit 0 = the control discriminated and the repair holds; 2 = REFUSED.
"""
from __future__ import annotations

import argparse
import json
import os
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

EXIT_REFUSE = 2
HERE = Path(__file__).resolve().parent


class Refusal(Exception):
    """Never an `assert` -- this file of all files (L-332, L-470)."""


def write_specimen(d: Path):
    """A MINIMAL, VALID big-endian raw-C-stream UGRID, then the same file with 8 trailing
    bytes. One tetrahedron, four nodes, four boundary triangles, one `.mapbc` group."""
    hdr = struct.pack(">7i", 4, 4, 0, 1, 0, 0, 0)
    body = (struct.pack(">12d", 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1)
            + struct.pack(">12i", 1, 2, 3, 1, 2, 4, 2, 3, 4, 1, 3, 4)
            + struct.pack(">4i", 1, 1, 1, 1)
            + struct.pack(">4i", 1, 2, 3, 4))
    clean = hdr + body
    (d / "tet_clean.b8.ugrid").write_bytes(clean)
    (d / "tet_trail.b8.ugrid").write_bytes(clean + b"\x00" * 8)
    (d / "tet.mapbc").write_text("1\n1 4000 wall\n")
    if (d / "tet_trail.b8.ugrid").stat().st_size != len(clean) + 8:
        raise Refusal("PLANT DID NOT PLANT: the trailing bytes were not written.")
    return len(clean)


def run(conv: Path, ugrid: Path, mapbc: Path, out: Path, opt: bool):
    flags = ["-O"] if opt else []
    p = subprocess.run([sys.executable] + flags + [str(conv), str(ugrid), str(mapbc), str(out)],
                       capture_output=True, text=True)
    return dict(rc=p.returncode,
                mesh_written=(out / "constant/polyMesh/owner").is_file(),
                stderr_tail=p.stderr.strip().splitlines()[-1][:160] if p.stderr.strip() else "")


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--old", required=True, help="the PRE-REPAIR converter, from git")
    ap.add_argument("--new", default=str(HERE / "ugrid_to_foam.py"))
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    scratch = Path(tempfile.mkdtemp(prefix="assert_guards_O_"))
    try:
        for p in (Path(a.old), Path(a.new)):
            if not p.is_file():
                raise Refusal(f"{p} is absent. ABSENT NEVER READS CLEAN.")
        clean_size = write_specimen(scratch)
        cells = {}
        for label, conv in (("old", Path(a.old)), ("new", Path(a.new))):
            for opt in (False, True):
                key = f"{label}_{'O' if opt else 'plain'}"
                cells[key] = run(conv, scratch / "tet_trail.b8.ugrid",
                                 scratch / "tet.mapbc", scratch / f"out_{key}", opt)
        discriminated = (cells["old_plain"]["rc"] != 0
                         and cells["old_O"]["rc"] == 0
                         and cells["old_O"]["mesh_written"]
                         and cells["new_plain"]["rc"] != 0
                         and cells["new_O"]["rc"] != 0
                         and not cells["new_O"]["mesh_written"])
    except Refusal as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return EXIT_REFUSE
    finally:
        for p in sorted(scratch.rglob("*"), reverse=True):
            (p.rmdir() if p.is_dir() else p.unlink())
        scratch.rmdir()

    print("=== `assert` GUARDS UNDER `python3 -O` -- BOTH WAYS ===")
    print(f"specimen: a valid {clean_size}-byte raw-C-stream (.b8) UGRID + 8 TRAILING BYTES")
    for key, want in (("old_plain", "guard fires"), ("old_O", "GUARD VANISHES"),
                      ("new_plain", "guard fires"), ("new_O", "guard still fires")):
        c = cells[key]
        state = ("GUARD FIRED, no mesh written" if c["rc"] != 0
                 else "*** GUARD ABSENT -- MESH WRITTEN FROM A MALFORMED FILE ***")
        print(f"  {key:10s} rc={c['rc']:<3} mesh_written={str(c['mesh_written']):5s} "
              f"{state}   (expected: {want})")
    print(f"\nCONTROL DISCRIMINATED: {discriminated}")
    if not discriminated:
        print("NOT A RESULT: the control did not separate the old form from the repaired "
              "one, so it certifies nothing (L-467). REFUSED at exit 2.")
        return EXIT_REFUSE
    print("THE REPAIR HOLDS: the old converter's guard is deleted by one interpreter flag "
          "and writes a mesh from a malformed file; the repaired converter refuses under "
          "both modes.")
    if a.json:
        Path(a.json).write_text(json.dumps(
            dict(THIS_IS_NOT_A_GRADED_RUN=True, specimen_bytes=clean_size,
                 cells=cells, discriminated=discriminated,
                 old_converter=a.old, new_converter=a.new),
            indent=2, sort_keys=True))
        print(f"written: {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
