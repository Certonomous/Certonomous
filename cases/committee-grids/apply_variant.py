#!/usr/bin/env python3
"""Copy the numerics of an already-run DPW5 variant onto another case.

The point is that the HLPW6 grid must be retried under *exactly* the numerics
that were measured on DPW5 -- not under a re-typed approximation of them. So
rather than re-derive the dictionaries, this lifts `system/fvSchemes` and
`system/fvSolution` verbatim from the DPW5 run directory that produced the
measured result, and reports the md5 of each so the two runs can be shown to
have used the same bytes.

Usage: apply_variant.py <sourceRunDir> <targetCaseDir>
"""
import hashlib
import os
import shutil
import sys

SRC, DST = sys.argv[1], sys.argv[2]
for f in ("fvSchemes", "fvSolution"):
    s = os.path.join(SRC, "system", f)
    d = os.path.join(DST, "system", f)
    shutil.copyfile(s, d)
    h = hashlib.md5(open(s, "rb").read()).hexdigest()
    print(f"{f}: {h}  {s} -> {d}")
