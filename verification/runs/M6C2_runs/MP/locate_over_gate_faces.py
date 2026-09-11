#!/usr/bin/env python3
"""WHERE ARE THE OVER-GATE FACES? Reads checkMesh's own `nonOrthoFaces` set and reports
the face centroids by radius from the body. It grades nothing; it localises.

The reading it feeds is fixed in MP/L1_PREDICTION.md, committed before any checkMesh ran.

PLANTED CONTROL: the radius classifier is shown a synthetic face it MUST place inside
r<2 and one it MUST place outside, through the same code path. A classifier not shown
able to separate the two cannot be believed when it says 100 % fell on one side.
"""
import sys, re, numpy as np, pathlib

R_BODY = 2.0

def load(meshdir):
    M = pathlib.Path(meshdir)
    t = (M / "points").read_text()
    m = re.search(r"^\s*(\d+)\s*\n\(", t, re.M); n = int(m.group(1))
    pts = np.fromstring(t[m.end():t.rindex(")")].replace("(", " ").replace(")", " "),
                        sep=" ").reshape(n, 3)
    t = (M / "faces").read_text()
    m = re.search(r"^\s*(\d+)\s*\n\(", t, re.M); nf = int(m.group(1))
    faces = re.findall(r"\d+\((.*?)\)", t[m.end():t.rindex(")")])
    assert len(faces) == nf, f"parsed {len(faces)} faces, header says {nf}"
    return pts, faces

def centroids(pts, faces, idx):
    return np.array([pts[np.fromstring(faces[i], sep=" ", dtype=float).astype(int)].mean(0)
                     for i in idx])

if __name__ == "__main__":
    meshdir, setfile = sys.argv[1], sys.argv[2]
    # --- planted control, through the same classifier ---
    probe = np.array([[0.5, 0.0, 0.3], [4.0, 0.0, 0.1]])
    rr = np.linalg.norm(probe, axis=1)
    inside, outside = int((rr < R_BODY).sum()), int((rr >= R_BODY).sum())
    print(f"PLANT: one near face r={rr[0]:.3f} and one far face r={rr[1]:.3f} "
          f"-> classified {inside} inside, {outside} outside")
    if not (inside == 1 and outside == 1):
        print("REFUSED (2): the radius classifier could not separate a known near from a known far face.")
        sys.exit(2)

    pts, faces = load(meshdir)
    t = pathlib.Path(setfile).read_text()
    # OpenFOAM writes a set EITHER as "N\n(\n a b c \n)" OR compactly as "N(a b c)".
    # A reader that knows only one form crashes on the other; small sets use the compact
    # form, so the crash would land exactly on the near-clean meshes that matter most.
    m = re.search(r"(?<![\w.])(\d+)\s*\(", t[t.index("//", t.index("object")):])
    if m is None:
        print("REFUSED (4): could not find a set body in", setfile); sys.exit(4)
    base = t.index("//", t.index("object"))
    ns = int(m.group(1))
    body = t[base + m.end(): t.index(")", base + m.end())]
    idx = np.fromstring(body, sep=" ", dtype=float).astype(int)
    assert idx.size == ns, f"set header {ns}, parsed {idx.size}"
    print(f"\nnonOrthoFaces in set: {ns}")
    if ns == 0:
        print("NO OVER-GATE FACES."); sys.exit(0)
    c = centroids(pts, faces, idx)
    r = np.linalg.norm(c, axis=1)
    print(f"  r: min {r.min():.4f}  median {np.median(r):.4f}  max {r.max():.4f}")
    for k, nm in enumerate("xyz"):
        q = np.percentile(c[:, k], [0, 50, 100])
        print(f"  {nm}: min {q[0]:9.4f}  median {q[1]:9.4f}  max {q[2]:9.4f}")
    near = int((r < R_BODY).sum()); far = ns - near
    print(f"\n  within r < {R_BODY} m of the body : {near:7d}  ({100*near/ns:6.2f} %)")
    print(f"  beyond r >= {R_BODY} m (far field) : {far:7d}  ({100*far/ns:6.2f} %)")
    # L1_PREDICTION.md's rows are about NON-ORTHOGONALITY ONLY. Printing its reading for
    # any other set would attach a registered prediction to a quantity it never named --
    # this tool did exactly that once, on skewFaces, and the line had to be retracted.
    if pathlib.Path(setfile).name == "nonOrthoFaces":
        print(f"\nPREDICTION READING (MP/L1_PREDICTION.md): "
              f"{'HOLDS -- far-field march, cap vindicated' if far/ns >= 0.90 else 'FAILS -- a body- or cap-local defect of its own'}")
    else:
        print(f"\nNO PREDICTION READING: MP/L1_PREDICTION.md fixes outcomes for "
              f"nonOrthoFaces, not for '{pathlib.Path(setfile).name}'. Location only.")
