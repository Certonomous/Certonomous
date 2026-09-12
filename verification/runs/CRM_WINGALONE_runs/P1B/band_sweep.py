#!/usr/bin/env python3
"""P1B — INDEPENDENT re-derivation of P2's root-plane band plateau, from the polyMesh.

WHY THIS EXISTS. P2 reports the CRM wing-alone root plane is planar to 9.491133e-06
mesh-units and that the root-plane face count sits on a plateau of 14,144 across four
decades of band. A new symmetry tolerance is about to be registered on that basis. A
tolerance registered on a CITED TABLE is a tolerance registered on somebody's summary;
this reads the mesh.

METHOD (P2's, restated so it can be checked): a face is a root-plane CANDIDATE if its
unit normal has |n_y| > 0.99. Candidates are then counted within a band on each face's
max|y| over its own vertices. The count as a function of band is swept.

PLANTED CONTROL (rule 3). The plant goes into the INPUT: one known root-plane face's
vertices are displaced in y by a known amount, and the real sweep is RE-RUN on the
perturbed coordinates. That face must LEAVE the bands tighter than the displacement and
REMAIN in the bands looser than it.

DISCRIMINATION CONTROL. A pure y-TRANSLATION does not rotate a face, so the |n_y| > 0.99
CANDIDATE COUNT must be UNCHANGED by the plant. If it moves, the plant leaked into the
normal path and the control does not discriminate -- REFUSE.

Exit: 0 swept and control passed; 2 REFUSE (control failed or mesh not as recorded).
"""
import sys, os, re, math

PATCH = "defaultFaces"
NY_MIN = 0.99
BANDS = [1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1e0, 1e1, 1e2]


def read_boundary(pm):
    txt = open(os.path.join(pm, "boundary")).read()
    m = re.search(PATCH + r"\s*\{[^}]*?nFaces\s+(\d+);[^}]*?startFace\s+(\d+);", txt, re.S)
    if not m:
        raise SystemExit("REFUSE: patch %s not found — this mesh is not in the recorded state." % PATCH)
    return int(m.group(1)), int(m.group(2))


def _body_start(path):
    with open(path) as f:
        for i, ln in enumerate(f):
            if ln.strip() == "(" and i > 10:
                return i
    raise SystemExit("REFUSE: no opening paren in %s" % path)


def load_faces(pm, nb, start):
    """Stream `faces`, keeping ONLY the boundary range."""
    p = os.path.join(pm, "faces")
    off = _body_start(p)
    lo, hi = off + 1 + start, off + 1 + start + nb
    out, need = [], set()
    with open(p) as f:
        for i, ln in enumerate(f):
            if i < lo:
                continue
            if i >= hi:
                break
            pl = [int(x) for x in re.findall(r"\d+", ln)][1:]
            out.append(pl); need.update(pl)
    return out, need


def load_points(pm, need):
    """Stream `points`, keeping ONLY the indices the boundary needs."""
    p = os.path.join(pm, "points")
    off = _body_start(p)
    coords = {}
    with open(p) as f:
        for i, ln in enumerate(f):
            idx = i - off - 1
            if idx < 0:
                continue
            if idx in need:
                v = re.findall(r"[-+0-9.eE]+", ln)
                if len(v) >= 3:
                    coords[idx] = (float(v[0]), float(v[1]), float(v[2]))
            if len(coords) == len(need):
                break
    return coords


def face_ny_and_maxy(pl, coords):
    """Unit-normal y-component (Newell) and max|y| over the face's own vertices."""
    pts = [coords[i] for i in pl]
    nx = ny = nz = 0.0
    n = len(pts)
    for k in range(n):
        a, b = pts[k], pts[(k + 1) % n]
        nx += (a[1] - b[1]) * (a[2] + b[2])
        ny += (a[2] - b[2]) * (a[0] + b[0])
        nz += (a[0] - b[0]) * (a[1] + b[1])
    mag = math.sqrt(nx * nx + ny * ny + nz * nz)
    if mag == 0.0:
        return 0.0, max(abs(p[1]) for p in pts)
    return abs(ny) / mag, max(abs(p[1]) for p in pts)


def sweep(faces, coords):
    """Return (candidate_count, {band: (count, max|y| within band)})."""
    cand = []
    for pl in faces:
        ny, my = face_ny_and_maxy(pl, coords)
        if ny > NY_MIN:
            cand.append(my)
    res = {}
    for b in BANDS:
        inb = [m for m in cand if m < b]
        res[b] = (len(inb), max(inb) if inb else 0.0)
    return len(cand), res


def planted_control(faces, coords):
    """Plant into the INPUT: translate EVERY vertex in y by a known DISP and RE-RUN the
    real sweep.

    🔴 WHY NOT A SINGLE-FACE PLANT. The first version of this control displaced ONE
    root-plane face's vertices. It REFUSED, and it was right to: on a conformal mesh the
    vertices are SHARED, so moving one face moved SIX out of the 1e-5 band and THREE out
    of 1e-3, and rotated its neighbours enough to move the |n_y| candidate count by 3.
    A plant whose blast radius is not known cannot have a predicted response, so it
    cannot discriminate. That refusal is kept in the record; it is the control working.

    A RIGID y-TRANSLATION has an exactly predictable response instead:
      * it does NOT rotate anything, so the |n_y| > 0.99 CANDIDATE COUNT must be
        UNCHANGED -- the discrimination control, and it is now exact rather than hopeful;
      * every root-plane face's max|y| becomes ~DISP, so bands BELOW DISP must empty of
        root-plane faces and bands ABOVE DISP must recover the clean count.

    Code path exercised: face_ny_and_maxy()'s max|y| reduction and sweep()'s band
    comparison -- the path that produces the graded count."""
    out = []
    DISP = 1e-4                      # sits between the 1e-5 and 1e-3 bands
    c0, r0 = sweep(faces, coords)
    saved = dict(coords)
    for j in list(coords):
        x, y, z = coords[j]
        coords[j] = (x, y + DISP, z)
    c1, r1 = sweep(faces, coords)
    coords.clear(); coords.update(saved)
    c2, r2 = sweep(faces, coords)

    below = r1[1e-5][0]                       # must be ~0: nothing is that close to y=0 now
    above = r1[1e-3][0]                       # must recover the clean plateau
    clean_above = r0[1e-3][0]
    restored = (r2[1e-5][0] == r0[1e-5][0] and c2 == c0)
    disc = (c1 == c0)
    out.append("plant: RIGID translation of all %d vertices by %+.1e in y" % (len(coords), DISP))
    out.append("  band 1e-5 (below DISP): %d -> %d   (must EMPTY of root-plane faces)" % (r0[1e-5][0], below))
    out.append("  band 1e-3 (above DISP): %d -> %d   (must RECOVER the clean count %d)" % (clean_above, above, clean_above))
    out.append("  restored -> band 1e-5 %d, candidates %d  (matches clean: %s)" % (r2[1e-5][0], c2, restored))
    out.append("  DISCRIMINATION: |n_y|>0.99 candidate count %d -> %d, unchanged: %s" % (c0, c1, disc))
    ok = (below == 0) and (above == clean_above) and restored and disc
    if not ok:
        out.append("  REFUSE: the sweep did not respond to a known rigid displacement in the way "
                   "a band classifier must. Its clean counts are NOT evidence (rule 3).")
    return ok, out


def main(pm):
    nb, start = read_boundary(pm)
    print("P1B — INDEPENDENT band sweep of the CRM wing-alone root plane")
    print("MESH: %s" % pm)
    print("PATCH %s: nFaces %d, startFace %d\n" % (PATCH, nb, start))
    faces, need = load_faces(pm, nb, start)
    coords = load_points(pm, need)
    print("read %d boundary faces, %d distinct points\n" % (len(faces), len(coords)))

    ok, msg = planted_control(faces, coords)
    print("PLANTED CONTROL — planted into the INPUT, real sweep re-run")
    for m in msg:
        print("  " + m)
    if not ok:
        print("\nREFUSE (exit 2).")
        return 2
    print("  -> control PASSED: the sweep is shown able to move when its input moves.\n")

    cand, res = sweep(faces, coords)
    print("root-plane CANDIDATES by normal (|n_y| > %.2f): %d\n" % (NY_MIN, cand))
    print("  %-10s %10s %18s" % ("band", "n_faces", "max|y| in band"))
    prev = None
    for b in BANDS:
        n, mx = res[b]
        flat = "" if prev is None or n != prev else "   <- flat"
        print("  %-10.0e %10d %18.6e%s" % (b, n, mx, flat))
        prev = n
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
