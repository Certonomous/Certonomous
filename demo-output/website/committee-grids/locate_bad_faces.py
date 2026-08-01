#!/usr/bin/env python3
"""Where are checkMesh's wrongOrientedFaces?

The import is asserted against the file's own boundary list, all topology
checks pass, and three independent conversions of the same domain agree on
total volume to 1e-5 relative. But checkMesh still reports a handful of faces
whose decomposition pyramid has negative volume, and it matters whether those
are a converter defect or genuine degeneracy in the published grid. A converter
defect would be systematic -- a wrong node-ordering convention hits a whole
element class. Genuine degeneracy is localised to the worst cells. This reports
which it is, by locating each offending face and reporting the aspect ratio
neighbourhood it sits in.
"""
import re
import sys

import numpy as np

CASE = sys.argv[1]
PM = f"{CASE}/constant/polyMesh"


def read_list(path, parse):
    txt = open(path).read()
    body = txt[txt.index("(", txt.index("\n}")):]
    return parse(body)


def read_points():
    txt = open(f"{PM}/points").read()
    i = txt.index("(", txt.index("}"))
    vals = re.findall(r"\(([^()]*)\)", txt[i + 1:])
    return np.array([np.fromstring(v, sep=" ") for v in vals])


def read_faces():
    txt = open(f"{PM}/faces").read()
    i = txt.index("(", txt.index("}"))
    return [np.fromstring(m, dtype=int, sep=" ")
            for m in re.findall(r"\d+\(([^)]*)\)", txt[i:])]


def read_labels(path):
    txt = open(path).read()
    i = txt.index("(", txt.index("}"))
    j = txt.rindex(")")
    return np.fromstring(txt[i + 1:j], dtype=int, sep="\n")


def read_set(path):
    txt = open(path).read()
    i = txt.index("(", txt.index("}"))
    j = txt.rindex(")")
    return np.fromstring(txt[i + 1:j], dtype=int, sep="\n")


pts = read_points()
faces = read_faces()
own = read_labels(f"{PM}/owner")
nei = read_labels(f"{PM}/neighbour")
bad = read_set(f"{PM}/sets/wrongOrientedFaces")
print(f"{CASE}: {len(pts)} points, {len(faces)} faces, "
      f"{len(bad)} wrongOrientedFaces")

# cell centres, crudely, from the faces each cell owns/neighbours
nCells = int(max(own.max(), nei.max())) + 1
acc = np.zeros((nCells, 3))
cnt = np.zeros(nCells)
fc = np.array([pts[f].mean(axis=0) for f in faces])
np.add.at(acc, own, fc)
np.add.at(cnt, own, 1)
np.add.at(acc, nei, fc[:len(nei)])
np.add.at(cnt, nei, 1)
cc = acc / cnt[:, None]

R = np.linalg.norm(fc, axis=1)
print(f"domain radius from origin: faces span {R.min():.3g} .. {R.max():.3g}")
print(f"\nthe {len(bad)} offending faces:")
print(f"  radius from origin: min {R[bad].min():.4g}  median "
      f"{np.median(R[bad]):.4g}  max {R[bad].max():.4g}")
print(f"  fraction of all faces beyond the median offending radius: "
      f"{(R > np.median(R[bad])).mean():.4f}")
nb = len(faces) - len(nei)
print(f"  boundary faces among them: {int((bad >= len(nei)).sum())} of {len(bad)}"
      f"  (mesh has {nb} boundary faces)")
sz = np.array([len(faces[b]) for b in bad])
print(f"  face vertex counts: {dict(zip(*np.unique(sz, return_counts=True)))}")
# how far out are they, in units of the wall bounding box
print("\n  first 10 face centres (m):")
for b in bad[:10]:
    print(f"    face {b:>9d}  centre {np.round(fc[b], 2)}  |r|={R[b]:.4g}")
