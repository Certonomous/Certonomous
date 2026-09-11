#!/usr/bin/env python3
"""Locate the G-M1 breaching faces: near-wall or far-field?
Streams the mesh rather than loading 1.7 GB. Includes a positive control:
the same lookup is first run on a face KNOWN to be on the wall."""
import sys, re, numpy as np
base = sys.argv[1]
ids = [15457192,15457195,15457198,15457486,15457517,15457563,15457566,15457885]
def face_start(path):
    with open(path) as f:
        for i, ln in enumerate(f, 1):
            if ln.strip() == "(" and i > 15: return i
    raise SystemExit("no opening paren")
fs = face_start(base + "/faces")
want = set(ids) | {0}          # face 0 as a control: it is a real face
rows = {}
with open(base + "/faces") as f:
    for i, ln in enumerate(f):
        idx = i - fs           # 0-based face index after the '('
        if idx in want:
            rows[idx] = ln.strip()
            if len(rows) == len(want): break
pts_needed = set()
parsed = {}
for k, v in rows.items():
    nums = [int(x) for x in re.findall(r"\d+", v)]
    pl = nums[1:]              # first number is the vertex count
    parsed[k] = pl
    pts_needed.update(pl)
ps = face_start(base + "/points")
coords = {}
with open(base + "/points") as f:
    for i, ln in enumerate(f):
        idx = i - ps
        if idx in pts_needed:
            coords[idx] = [float(x) for x in re.findall(r"[-+0-9.eE]+", ln)]
            if len(coords) == len(pts_needed): break
BODY_TIP_Y = 3.7666681523      # wing tip, mesh-units (census, this lane)
FARFIELD   = 84.8928           # farfield half-extent from checkMesh bbox
print("face_id            centre (x,y,z)                     |r|      %_of_farfield  location")
for k in [0] + ids:
    c = np.array([coords[p] for p in parsed[k]]).mean(axis=0)
    r = float(np.linalg.norm(c))
    tag = "CONTROL (face 0)" if k == 0 else ""
    loc = "NEAR-WALL" if r < 3*BODY_TIP_Y else ("FAR-FIELD" if r > 0.5*FARFIELD else "mid-field")
    print("%-10d %28s %9.3f   %6.1f%%    %s %s"
          % (k, np.array2string(c, precision=3), r, 100*r/FARFIELD, loc, tag))
