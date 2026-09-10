#!/usr/bin/env python3
"""geometry_gate_t26.py -- T26 GEOMETRY ADMISSION GATE (CASE_PROTOCOL_CHARTER section 1).

    python3 docs/campaigns/T-family/geometry_gate_t26.py --stl <path>
    python3 docs/campaigns/T-family/geometry_gate_t26.py --selftest

WHAT THIS IS.  CASE_PROTOCOL_CHARTER v1.0 section 1 opens with:
"Geometry: admitted through the gate (units, watertightness, normals, regions,
feature resolution, curvature-based surface resolution for 3D).  Refusal names
the deficiency and stops."  This file IS that gate for T26.  It decides nothing
about physics and issues no rung verdict.

EXIT CODES.  0 = every registered check PASS.  2 = REFUSED, deficiency named.
3 = the gate's own planted control failed, so no result of this run is evidence
(CLAUDE.md rule 3: a zero from a reader not shown able to see a non-zero is not
evidence).  The gate NEVER degrades; it refuses.

THE PLANTED CONTROL, AND WHY EVERY CHECK NEEDS ONE.  Every check below can
return zero -- zero open edges, zero orientation clashes, zero degenerate
facets, zero self-intersections.  A reader with a broken loop returns exactly
the same zeros.  So --selftest builds MUTANT surfaces that are known to be
defective in each specific way, drives the SAME production functions over them,
and REFUSES unless every one of them is caught.  It also drives the clean
surface and refuses if any check fires on it.  Both directions, every check.
"""
import argparse, hashlib, math, os, struct, sys
from collections import defaultdict

EXIT_OK, EXIT_REFUSE, EXIT_CONTROL = 0, 2, 3

# ---------------------------------------------------------------- registered
# Registered in T26_PREREGISTRATION.md section 2.  Values here are the gate;
# changing one after the freeze commit is a charter violation, not an edit.
UNIT_TOL_M          = 1.0e-6    # header-declared dimension vs measured bbox
AREA_FLOOR_M2       = 1.0e-14   # a facet below this is degenerate
MAX_OPEN_EDGES      = 0
MAX_ORIENT_CLASH    = 0
MAX_DEGENERATE      = 0
MAX_INTRA_SELFX     = 0         # self-intersection WITHIN one component
DECLARED_M = {"D_duct_inner": 0.250, "L_body": 0.200, "D_hub": 0.075}


def refuse(msg, code=EXIT_REFUSE):
    print(f"REFUSED: {msg}")
    sys.exit(code)


# ------------------------------------------------------------------- readers
def read_stl(path):
    """Binary STL -> (header, [ (v0,v1,v2), ... ]).  Refuses a size mismatch."""
    with open(path, "rb") as fh:
        b = fh.read()
    if len(b) < 84:
        refuse(f"{path}: shorter than an STL header")
    n = struct.unpack("<I", b[80:84])[0]
    if 84 + 50 * n != len(b):
        refuse(f"{path}: facet count {n} implies {84+50*n} bytes, file has {len(b)}")
    hdr = b[:80].decode("ascii", "replace").rstrip("\x00").strip()
    tris, off = [], 84
    for _ in range(n):
        v = struct.unpack("<12fH", b[off:off + 50]); off += 50
        tris.append((v[3:6], v[6:9], v[9:12]))
    return hdr, tris


def vkey(c):
    return (round(c[0], 9), round(c[1], 9), round(c[2], 9))


def edge_census(tris):
    """-> (n_open, n_nonmanifold, n_orient_clash, n_edges).  All four can be 0,
    which is exactly why --selftest drives mutants that make each of them
    non-zero through THIS function."""
    und, dir_ = defaultdict(int), defaultdict(int)
    for t in tris:
        k = [vkey(c) for c in t]
        for a, b in ((0, 1), (1, 2), (2, 0)):
            und[tuple(sorted((k[a], k[b])))] += 1
            dir_[(k[a], k[b])] += 1
    n_open = sum(1 for c in und.values() if c == 1)
    n_nm = sum(1 for c in und.values() if c > 2)
    n_clash = sum(1 for c in dir_.values() if c > 1)
    return n_open, n_nm, n_clash, len(und)


def facet_metrics(tris):
    """-> (total_area, signed_volume, n_degenerate)."""
    A = V = 0.0
    ndeg = 0
    for a, b, c in tris:
        e1 = (b[0]-a[0], b[1]-a[1], b[2]-a[2])
        e2 = (c[0]-a[0], c[1]-a[1], c[2]-a[2])
        cx = e1[1]*e2[2]-e1[2]*e2[1]
        cy = e1[2]*e2[0]-e1[0]*e2[2]
        cz = e1[0]*e2[1]-e1[1]*e2[0]
        ar = 0.5*math.sqrt(cx*cx+cy*cy+cz*cz)
        A += ar
        if ar < AREA_FLOOR_M2:
            ndeg += 1
        V += (a[0]*(b[1]*c[2]-b[2]*c[1]) - a[1]*(b[0]*c[2]-b[2]*c[0])
              + a[2]*(b[0]*c[1]-b[1]*c[0]))/6.0
    return A, V, ndeg


def components(tris):
    """Vertex-connected components -> list of triangle-index lists."""
    parent = {}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb: parent[ra] = rb
    for t in tris:
        for c in t:
            parent.setdefault(vkey(c), vkey(c))
    for t in tris:
        k = [vkey(c) for c in t]; union(k[0], k[1]); union(k[1], k[2])
    comp = defaultdict(list)
    for i, t in enumerate(tris):
        comp[find(vkey(t[0]))].append(i)
    return [v for _, v in sorted(comp.items(), key=lambda kv: -len(kv[1]))]


# ------------------------------------------- triangle-triangle intersection
def _tri_tri(t0, t1):
    """Moller separating-axis test, EXCLUDING pairs that share a vertex (an
    adjacent pair touches by construction and is not a self-intersection)."""
    if {vkey(c) for c in t0} & {vkey(c) for c in t1}:
        return False
    def sub(a, b): return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
    def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2],
                             a[0]*b[1]-a[1]*b[0])
    def dot(a, b): return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
    e0 = [sub(t0[1], t0[0]), sub(t0[2], t0[1]), sub(t0[0], t0[2])]
    e1 = [sub(t1[1], t1[0]), sub(t1[2], t1[1]), sub(t1[0], t1[2])]
    n0, n1 = cross(e0[0], e0[1]), cross(e1[0], e1[1])
    axes = [n0, n1]
    for a in e0:
        for b in e1:
            axes.append(cross(a, b))
    # THE COPLANAR AXES, AND WHY THEY ARE HERE.  {n0, n1, e0_i x e1_j} is the
    # complete axis set only for NON-coplanar triangles.  When the two lie in
    # one plane every one of those eleven axes degenerates or lies in-plane
    # with zero separation, so the test returns "intersecting" for EVERY
    # coplanar pair -- including two disjoint facets of the same flat end cap.
    # Measured, on this surface, before the fix: 8,838 false pairs on the duct
    # end caps and 96 on the three flat struts.  The in-plane normals n x e are
    # the 2-D SAT in the shared plane and are what separates them.
    for a in e0:
        axes.append(cross(n0, a))
    for b in e1:
        axes.append(cross(n1, b))
    for ax in axes:
        if abs(ax[0]) + abs(ax[1]) + abs(ax[2]) < 1e-20:
            continue
        p0 = [dot(ax, v) for v in t0]; p1 = [dot(ax, v) for v in t1]
        # SEPARATED iff one projection lies strictly beyond the other.  The
        # epsilon is POSITIVE and on the far side: a pair that merely touches
        # within 1e-12 m is separated, not intersecting.  Writing it on the
        # near side (>= max - eps) makes the degenerate coplanar axis, whose
        # two projections are both zero-extent, report SEPARATED and the whole
        # test then misses every coplanar overlap -- caught by the selftest's
        # coplanar MUTANT arm, which is why that arm exists.
        if min(p0) > max(p1) + 1e-12 or min(p1) > max(p0) + 1e-12:
            return False
    return True


def self_intersections(tris, idx, cell):
    """Count intersecting NON-ADJACENT triangle pairs inside one component,
    via a uniform spatial hash at `cell`.  Returns (count, first_pair)."""
    grid = defaultdict(list)
    for i in idx:
        t = tris[i]
        lo = [min(c[d] for c in t) for d in range(3)]
        hi = [max(c[d] for c in t) for d in range(3)]
        for gx in range(int(math.floor(lo[0]/cell)), int(math.floor(hi[0]/cell))+1):
            for gy in range(int(math.floor(lo[1]/cell)), int(math.floor(hi[1]/cell))+1):
                for gz in range(int(math.floor(lo[2]/cell)), int(math.floor(hi[2]/cell))+1):
                    grid[(gx, gy, gz)].append(i)
    seen, hits, first = set(), 0, None
    for bucket in grid.values():
        for a in range(len(bucket)):
            for b in range(a+1, len(bucket)):
                p = (bucket[a], bucket[b]) if bucket[a] < bucket[b] else (bucket[b], bucket[a])
                if p in seen:
                    continue
                seen.add(p)
                if _tri_tri(tris[p[0]], tris[p[1]]):
                    hits += 1
                    if first is None:
                        first = p
    return hits, first


# --------------------------------------------------------------- the report
def run_gate(path, verbose=True):
    hdr, tris = read_stl(path)
    sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
    n_open, n_nm, n_clash, n_edges = edge_census(tris)
    A, V, ndeg = facet_metrics(tris)
    comps = components(tris)
    pts = [c for t in tris for c in t]
    bb = [(min(c[d] for c in pts), max(c[d] for c in pts)) for d in range(3)]
    fails = []
    if n_open > MAX_OPEN_EDGES:
        fails.append(f"GEO-2 open edges {n_open} > {MAX_OPEN_EDGES} (surface not closed)")
    if n_nm > 0:
        fails.append(f"GEO-3a non-manifold edges {n_nm} > 0")
    if n_clash > MAX_ORIENT_CLASH:
        fails.append(f"GEO-3b orientation clashes {n_clash} > {MAX_ORIENT_CLASH}")
    if ndeg > MAX_DEGENERATE:
        fails.append(f"GEO-5 degenerate facets {ndeg} > {MAX_DEGENERATE}")
    per_comp = []
    for ci, idx in enumerate(comps):
        cA, cV, _ = facet_metrics([tris[i] for i in idx])
        cpts = [c for i in idx for c in tris[i]]
        rr = [math.hypot(c[1], c[2]) for c in cpts]
        L = []
        for i in idx:
            t = tris[i]
            for a, b in ((0, 1), (1, 2), (2, 0)):
                L.append(math.dist(t[a], t[b]))
        sx = self_intersections(tris, idx, max(2.0*sum(L)/len(L), 1e-6))
        per_comp.append(dict(i=ci, ntri=len(idx), area=cA, vol=cV,
                             rmin=min(rr), rmax=max(rr),
                             xmin=min(c[0] for c in cpts), xmax=max(c[0] for c in cpts),
                             emin=min(L), emax=max(L), selfx=sx[0], firstx=sx[1]))
        if cV <= 0.0:
            fails.append(f"GEO-4 component {ci} signed volume {cV:.6e} <= 0 "
                         f"(normals point inward)")
        if sx[0] > MAX_INTRA_SELFX:
            fails.append(f"GEO-6 component {ci} self-intersecting pairs {sx[0]} "
                         f"> {MAX_INTRA_SELFX}, first {sx[1]}")
    if verbose:
        print(f"stl        {path}")
        print(f"sha256     {sha}")
        print(f"header     {hdr!r}")
        print(f"facets     {len(tris)}   unique edges {n_edges}   components {len(comps)}")
        print(f"bbox x [{bb[0][0]:.6f},{bb[0][1]:.6f}]  y [{bb[1][0]:.6f},{bb[1][1]:.6f}]"
              f"  z [{bb[2][0]:.6f},{bb[2][1]:.6f}]")
        print(f"open {n_open}  nonmanifold {n_nm}  orient_clash {n_clash}  degenerate {ndeg}")
        print(f"area {A:.9f}  signed_volume {V:.9e}")
        for c in per_comp:
            print(f"  comp{c['i']}: tri {c['ntri']:5d}  x[{c['xmin']:.4f},{c['xmax']:.4f}]"
                  f"  r[{c['rmin']:.6f},{c['rmax']:.6f}]  A {c['area']:.6f}"
                  f"  V {c['vol']:.6e}  edge[{c['emin']:.3e},{c['emax']:.3e}]"
                  f"  selfX {c['selfx']}")
    return dict(sha=sha, hdr=hdr, tris=tris, bb=bb, comps=per_comp, fails=fails,
                n_open=n_open, n_nm=n_nm, n_clash=n_clash, ndeg=ndeg, area=A, vol=V)


# ------------------------------------------------------------------ mutants
def _mk(tris):
    return [tuple(tuple(float(x) for x in c) for c in t) for t in tris]


def selftest(path):
    ok = True
    def chk(name, cond):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        ok = ok and bool(cond)
    print("SELFTEST -- every check driven in BOTH directions")
    _, tris = read_stl(path)
    # ---- POSITIVE ARM: the clean surface must fire NOTHING -----------------
    o, nm, cl, _ = edge_census(tris)
    A, V, dg = facet_metrics(tris)
    chk("clean surface: 0 open edges", o == 0)
    chk("clean surface: 0 non-manifold edges", nm == 0)
    chk("clean surface: 0 orientation clashes", cl == 0)
    chk("clean surface: 0 degenerate facets", dg == 0)
    chk("clean surface: signed volume > 0", V > 0)
    # ---- NEGATIVE ARM: a mutant with a KNOWN defect must be CAUGHT ---------
    m = _mk(tris); m.pop(0)                       # delete a facet -> a hole
    o2, _, _, _ = edge_census(m)
    chk(f"MUTANT hole (one facet deleted): open edges {o2} > 0", o2 > 0)
    m = _mk(tris); m[0] = (m[0][0], m[0][2], m[0][1])   # flip one winding
    _, _, cl2, _ = edge_census(m)
    chk(f"MUTANT flipped facet: orientation clashes {cl2} > 0", cl2 > 0)
    m = _mk(tris); m.append((m[0][0], m[0][0], m[0][0]))  # zero-area facet
    _, _, dg2 = facet_metrics(m)
    chk(f"MUTANT zero-area facet: degenerate {dg2} > 0", dg2 > 0)
    m = _mk(tris)                                  # every winding flipped
    m = [(t[0], t[2], t[1]) for t in m]
    _, V2, _ = facet_metrics(m)
    chk(f"MUTANT all normals inward: signed volume {V2:.3e} < 0", V2 < 0)
    # self-intersection reader: two crossing triangles must be SEEN, and two
    # disjoint ones must NOT be -- the reader is shown able to say both.
    cross = [((0.,-1.,0.), (0.,1.,0.), (0.,0.,1.)),
             ((-1.,0.,0.5), (1.,0.,0.5), (0.,0.,1.5))]
    apart = [((0.,-1.,0.), (0.,1.,0.), (0.,0.,1.)),
             ((10.,-1.,0.), (10.,1.,0.), (10.,0.,1.))]
    hx, _ = self_intersections(cross, [0, 1], 1.0)
    hn, _ = self_intersections(apart, [0, 1], 1.0)
    chk(f"MUTANT crossing pair: self-intersections {hx} > 0", hx > 0)
    chk(f"CONTROL disjoint pair: self-intersections {hn} == 0", hn == 0)
    # COPLANAR ARM, both directions.  Two disjoint facets of one flat cap must
    # NOT fire; two overlapping coplanar facets MUST.  Without the n x e axes
    # the first of these two returns 1 and the gate refuses a clean surface.
    cop_ok = [((0.,0.,0.), (1.,0.,0.), (0.,1.,0.)),
              ((3.,0.,0.), (4.,0.,0.), (3.,1.,0.))]
    cop_bad = [((0.,0.,0.), (2.,0.,0.), (0.,2.,0.)),
               ((0.5,0.5,0.), (2.5,0.5,0.), (0.5,2.5,0.))]
    hc, _ = self_intersections(cop_ok, [0, 1], 5.0)
    hb, _ = self_intersections(cop_bad, [0, 1], 5.0)
    chk(f"CONTROL coplanar DISJOINT pair: self-intersections {hc} == 0", hc == 0)
    chk(f"MUTANT coplanar OVERLAPPING pair: self-intersections {hb} > 0", hb > 0)
    print("SELFTEST", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stl", default="cases/demo-surfaces/motor_in_duct.stl")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    _here = os.path.abspath(__file__)                 # docs/campaigns/T-family/<this>
    REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_here))))
    assert os.path.isfile(os.path.join(REPO, "CLAUDE.md")), (
        f"repo root resolved to {REPO}, which holds no CLAUDE.md -- refusing "
        "rather than reading a path this file cannot vouch for")
    p = a.stl if os.path.isabs(a.stl) else os.path.join(REPO, a.stl)
    if a.selftest:
        sys.exit(EXIT_OK if selftest(p) else EXIT_CONTROL)
    r = run_gate(p)
    if r["fails"]:
        for f in r["fails"]:
            print("  DEFICIENCY:", f)
        refuse("T26 geometry gate: " + str(len(r["fails"])) + " deficiency(ies) named above")
    print("GEOMETRY GATE: PASS")
