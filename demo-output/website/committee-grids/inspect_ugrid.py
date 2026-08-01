#!/usr/bin/env python3
"""Header / bounding-box / boundary-tag report for a UGRID file, without
building a mesh. Used to settle units, axes and patch numbering before any
conversion is attempted."""
import sys

import numpy as np

sys.path.insert(0, "/home/ubuntu/certonomous-runs/dpw5-committee-probe")
from ugrid_to_foam import sniff_layout  # noqa: E402

path = sys.argv[1]
endian, fortran = sniff_layout(path)
i4, f8 = endian + "i4", endian + "f8"
with open(path, "rb") as f:
    if fortran:
        f.read(4)
    nN, nT, nQ, nTet, nPyr, nPri, nHex = (
        int(x) for x in np.frombuffer(f.read(28), dtype=i4))
    if fortran:
        f.read(8)
    pts = np.frombuffer(f.read(nN * 24), dtype=f8).reshape(nN, 3)
    f.read(nT * 12 + nQ * 16)
    ttag = np.frombuffer(f.read(nT * 4), dtype=i4)
    qtag = np.frombuffer(f.read(nQ * 4), dtype=i4)

print(f"file      {path}")
print(f"layout    {'big' if endian == '>' else 'little'}-endian, "
      f"{'Fortran unformatted' if fortran else 'raw C stream'}")
print(f"nodes     {nN}")
print(f"bnd tri   {nT}   bnd quad {nQ}")
print(f"tet {nTet}  pyr {nPyr}  prism {nPri}  hex {nHex}  CELLS {nTet+nPyr+nPri+nHex}")
lo, hi = pts.min(axis=0), pts.max(axis=0)
print(f"bbox lo   {lo}")
print(f"bbox hi   {hi}")
print(f"extent    {hi - lo}")
tags = np.concatenate([ttag, qtag]) if nT or nQ else np.array([], dtype=int)
print("boundary tag histogram (tag: nTri, nQuad):")
for t in sorted(set(tags.tolist())):
    print(f"   {t:4d}: tri {int((ttag == t).sum()):8d}  quad {int((qtag == t).sum()):8d}")
