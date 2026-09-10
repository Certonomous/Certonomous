#!/usr/bin/env python3
"""TOOL 3 (grid-b) -- RE-CLUSTERED 9-ZONE M6 SURFACE WITH BLOCK COINCIDENCE BY CONSTRUCTION.

WHY THIS EXISTS.  build_capped_surface.py --cluster redistributed the chord nodes ZONE BY ZONE,
in place.  Two zones sharing an edge each moved that edge independently, the shared curve
diverged, and pyHyp autoConnect refused the surface:

    ERROR: Unknown topology encountered
     0.67834532200252762 0.62427737159455356E-2 1.1700269049985450 (node has 5 edges and 4 faces)
     0.67622318423013117 0.18117164574948399E-6 1.1712519658957385 (node has 5 edges and 3 faces)
    (verification/runs/M6_LE_RESOLVED_runs/Lc/work/march_Lc.out)

Both coordinates are corners of master zone 5, the 17x17 tip leading-edge corner cap -- exactly
where the most zone edges meet.  That is a COINCIDENCE failure, not a failure of the master's
topology: the same 9 zones with their point positions untouched marched cleanly
(surfaceMesh_Lc_nocluster.cgns -> volumeMesh_Lc_yp35.cgns).

THE CONSTRUCTION.  Coincidence is not asserted with a tolerance; it is made impossible to break.
  1. the master's shared edges are DISCOVERED numerically (exact array equality, fwd or rev),
     never hard-coded -- 16 of them, and 40 shared corners;
  2. the refinement PARAMETER of every family is defined so that two zones meeting on an edge
     must use the SAME array on it (see PARAMETERS below);
  3. after each zone is refined independently, every shared edge is taken from ONE zone and
     COPIED into the other (with reversal where the master edges ran opposite), and every
     shared corner is set from ONE representative.  The displacement this copy introduces is
     MEASURED and printed: it is the evidence that step 2 was actually consistent, because a
     copy that has to move a point by more than roundoff means the two zones had disagreed;
  4. every shared edge and corner is then asserted BIT-IDENTICAL with numpy.array_equal.  No
     tolerance argument appears anywhere in this file.

PARAMETERS.  Family map, taken from the master's own dims:
     chord 257 -> N_CHORD (prereg Lf: 557)   clustered to the registered nose+shock density
     span  161 -> N_SPAN  (prereg Lf: 177)   INTERPOLATED in span (gen_m6_gridb.py:167 SNAPPED
                                             to the nearest master station, which is why 177
                                             requested sections held only 161 distinct ones)
     wrap   17 -> 17                         unchanged (the LE nose strip and the cap collars)
Master zone 2 -- the 161x17 LE NOSE STRIP that gen_m6_gridb.py:147 discarded -- is retained, so
this surface HAS a leading edge.
The chord parameter is PER SPAN STATION: a single root-referenced parameter was measured to
leave the shock band under-resolved outboard (band max Delta x/c 6.01e-3 at station 165 against
9.7e-4 at the root), because the master's index-to-x/c map is only nearly self-similar.  A
per-station parameter is still coincidence-safe: two zones sharing a CHORD edge share the span
station that edge sits at, and the tip-collar zones (1, 4, 8) all chain to the tip station, so
they all take the tip station's parameter.

OUTPUT.  Multiblock PLOT3D.  **USE --fmt ascii.**  The two candidate consumers were both
MEASURED on this box (image dafoam-idwarp-rot:v1), and only one of them can take this surface:

  (a) `cgns_utils plot3d2cgns` -> pyHyp CGNS.  **DEAD, and not for the reason expected.**
      * Its own --help says "unformatted fortran, big-endian".  MEASURED FALSE for this build:
        a big-endian file dies at cgns_utilities.F90:2616 "Fortran runtime error: End of file";
        a NATIVE LITTLE-ENDIAN file is read correctly.  convertPlot3d opens with
        `open(unit=50, form='unformatted', file=pFile)` and NO `convert=` specifier, so the byte
        order is whatever the compiler defaulted to -- here, little-endian.  The record layout in
        the source is exactly the one written below: read(nZones); read(all dims); then one
        record per zone holding x, then y, then z, as real(kind=8).
      * The real blocker: **it cannot write a k=1 (surface) zone at all.**  A 3-D test grid
        (nk=3) converts perfectly and reads back with its planted z=999.5 intact; the SAME grid
        at nk=1 fails with `Invalid input: VertexSize[0]=3 and CellSize[0]=1` and leaves a
        4,096-byte CGNS holding ZERO zones.  The nk=3 control is what makes that a finding
        rather than a guess -- the reader was shown able to say otherwise.
      * NOTE the silent-failure trap: the little-endian nk=1 runs exited rc 0 and produced a
        file.  Only opening it (0 blocks) showed the conversion had not happened.
  (b) pyHyp with `fileType: "PLOT3D"`.  **THIS IS THE PATH THAT WORKS.**  pyHyp's plot3d reader
      is FORMATTED, not unformatted: readPlot3d.F90:17 `open (unit=7, form='formatted', ...)`,
      then `read(7,*) nPatch`, `read(7,*) (patchSizes(1:3,i), i=1,nPatch)`, then one flat
      list-directed read of 3*ni*nj values per patch.  --fmt ascii writes exactly that.  Both
      binary variants die at setup3d.F90:1185 "Bad integer for item 1 in list input".
      CGNS is therefore DROPPABLE for the surface input.

Host-only: numpy + scipy, no container, no MPI, no solver.  Writes only --out and --report.
"""
import argparse
import json
import os
import sys

import numpy as np

RR = os.path.dirname(os.path.abspath(__file__))
FAM_CHORD, FAM_SPAN, FAM_WRAP = 257, 161, 17
Z_UPPER, Z_STRIP, Z_LOWER, Z_TE = 0, 2, 3, 6      # master zone ids, verified by dims + extent


# ---------------------------------------------------------------------------- master I/O ----
def read_p3d_ascii(path):
    tok = open(path).read().split()
    it = iter(tok)
    nb = int(next(it))
    dims = [(int(next(it)), int(next(it)), int(next(it))) for _ in range(nb)]
    blocks = []
    for (ni, nj, nk) in dims:
        if nk != 1:
            raise RuntimeError(f"REFUSED: master block is not a surface (nk={nk})")
        n = ni * nj
        v = np.array([float(next(it)) for _ in range(3 * n)])
        b = np.stack([v[0:n], v[n:2 * n], v[2 * n:3 * n]], axis=-1).reshape(nj, ni, 3)
        blocks.append(np.ascontiguousarray(b.transpose(1, 0, 2)))   # (ni,nj,3)
    if next(it, None) is not None:
        raise RuntimeError("REFUSED: trailing tokens after the last block")
    return blocks


def edge_slots(b):
    ni, nj, _ = b.shape
    return {"i0": b[0, :, :], "i1": b[ni - 1, :, :], "j0": b[:, 0, :], "j1": b[:, nj - 1, :]}


def corner_slots(b):
    return {"00": (0, 0), "0N": (0, -1), "N0": (-1, 0), "NN": (-1, -1)}


def discover_shared_edges(blocks):
    out = []
    for a in range(len(blocks)):
        for c in range(a + 1, len(blocks)):
            ea, ec = edge_slots(blocks[a]), edge_slots(blocks[c])
            for ka, va in ea.items():
                for kc, vc in ec.items():
                    if va.shape != vc.shape:
                        continue
                    if np.array_equal(va, vc):
                        out.append((a, ka, c, kc, False))
                    elif np.array_equal(va, vc[::-1]):
                        out.append((a, ka, c, kc, True))
    return out


def discover_shared_corners(blocks):
    """-> list of equivalence classes, each a list of (zone, cornerkey)."""
    items = [(z, k) for z in range(len(blocks)) for k in corner_slots(blocks[0])]
    parent = {it: it for it in items}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a in range(len(blocks)):
        for c in range(a + 1, len(blocks)):
            for ka, ia in corner_slots(blocks[a]).items():
                pa = blocks[a][ia[0], ia[1]]
                for kc, ic in corner_slots(blocks[c]).items():
                    if np.array_equal(pa, blocks[c][ic[0], ic[1]]):
                        ra, rc = find((a, ka)), find((c, kc))
                        if ra != rc:
                            parent[rc] = ra
    cls = {}
    for it in items:
        cls.setdefault(find(it), []).append(it)
    return [v for v in cls.values() if len(v) > 1]


# ------------------------------------------------------------------- refinement kernels -----
def spline1d(curve, u):
    """Cubic resample of an (n,3) curve at fractional indices u; endpoints taken VERBATIM.

    A cubic spline evaluated at its last knot returns y0+b+c+d, equal to the end value only to
    roundoff, so two curves meeting at a shared corner drifted in the last bits.  u[0] and u[-1]
    are exactly the master end indices by construction, so the endpoints ARE master points."""
    n = len(curve)
    if len(u) == n and np.array_equal(u, np.arange(n, dtype=float)):
        return curve.copy()
    from scipy.interpolate import CubicSpline
    s = np.arange(n, dtype=float)
    out = np.empty((len(u), 3))
    for a in range(3):
        out[:, a] = CubicSpline(s, curve[:, a], bc_type="not-a-knot")(u)
    if u[0] == 0.0:
        out[0, :] = curve[0, :]
    if u[-1] == float(n - 1):
        out[-1, :] = curve[-1, :]
    return out


def resample_axis(b, axis, u):
    """Refine ONE index direction of a surface block, line by line, with spline1d."""
    if axis == 1:
        return np.ascontiguousarray(resample_axis(b.transpose(1, 0, 2), 0, u).transpose(1, 0, 2))
    ni, nj, _ = b.shape
    out = np.empty((len(u), nj, 3))
    for j in range(nj):
        out[:, j, :] = spline1d(np.ascontiguousarray(b[:, j, :]), u)
    return np.ascontiguousarray(out)


def resample_axis_perline(b, axis, us):
    """Refine ONE index direction with a DIFFERENT parameter array per line (us[j] for line j)."""
    if axis == 1:
        return np.ascontiguousarray(
            resample_axis_perline(b.transpose(1, 0, 2), 0, us).transpose(1, 0, 2))
    ni, nj, _ = b.shape
    n_new = len(us[0])
    out = np.empty((n_new, nj, 3))
    for j in range(nj):
        out[:, j, :] = spline1d(np.ascontiguousarray(b[:, j, :]), us[j])
    return np.ascontiguousarray(out)


# ------------------------------------------------------------------ chord clustering --------
def registered_spacing(G, x):
    """gen_m6_gridb's registered chordwise spacing law, lifted from clustering_distribution."""
    nose, shock = G.GEN_NOSE_TARGET, G.SHOCK_DXC
    lo, hi = G.SHOCK_XC_LO, G.SHOCK_XC_HI
    te = 2.0 * shock
    LE_W, TE_W = G.GEN_LE_ZONE_W, 0.08
    s = 0.02
    if x < LE_W:
        s = min(s, nose + (0.02 - nose) * (x / LE_W))
    if lo <= x <= hi:
        s = min(s, shock)
    elif lo - 0.05 <= x < lo:
        s = min(s, shock + (0.02 - shock) * (lo - x) / 0.05)
    elif hi < x <= hi + 0.05:
        s = min(s, shock + (0.02 - shock) * (x - hi) / 0.05)
    if x > 1.0 - TE_W:
        s = min(s, te + (0.02 - te) * (1.0 - x) / TE_W)
    return max(s, 1e-5)


def registered_cdf():
    sys.path.insert(0, RR)
    import gen_m6_gridb as G
    G.load_sizing()
    xs = np.linspace(0.0, 1.0, 200001)
    dens = 1.0 / np.array([registered_spacing(G, x) for x in xs])
    cdf = np.concatenate([[0.0], np.cumsum(0.5 * (dens[:-1] + dens[1:]) * np.diff(xs))])
    return G, xs, cdf


def chord_param(xc, xs, cdf, n_chord):
    """-> fractional master-index array (length n_chord, [0, len(xc)-1]) realising the registered
    density on THIS station's own x/c map."""
    if not np.all(np.diff(xc) > 0):
        raise RuntimeError("REFUSED: station x/c map is not strictly increasing")
    c0, c1 = np.interp(xc[0], xs, cdf), np.interp(xc[-1], xs, cdf)
    t = np.interp(np.linspace(c0, c1, n_chord), cdf, xs)
    t[0], t[-1] = xc[0], xc[-1]
    u = np.interp(t, xc, np.arange(len(xc), dtype=float))
    u[0], u[-1] = 0.0, float(len(xc) - 1)
    if not np.all(np.diff(u) > 0):
        raise RuntimeError("REFUSED: chord parameter is not strictly increasing")
    return u


# ------------------------------------------------------------------------ PLOT3D writers ----
def write_p3d_fortran(path, blocks, real4=False, big=True):
    ie = ">i4" if big else "<i4"
    re = (">f4" if real4 else ">f8") if big else ("<f4" if real4 else "<f8")

    def rec(fh, arr):
        b = np.asarray(arr).tobytes()
        np.array([len(b)], dtype=ie).tofile(fh)
        fh.write(b)
        np.array([len(b)], dtype=ie).tofile(fh)

    with open(path, "wb") as fh:
        rec(fh, np.array([len(blocks)], dtype=ie))
        rec(fh, np.array([[b.shape[0], b.shape[1], 1] for b in blocks], dtype=ie).ravel())
        for b in blocks:
            rec(fh, np.concatenate([b[:, :, a].ravel(order="F")
                                    for a in range(3)]).astype(re))


def write_p3d_ascii(path, blocks):
    with open(path, "w") as fh:
        fh.write(f"{len(blocks)}\n")
        for b in blocks:
            fh.write(f"{b.shape[0]} {b.shape[1]} 1\n")
        for b in blocks:
            for a in range(3):
                fh.write("\n".join("%.17g" % v for v in b[:, :, a].ravel(order="F")) + "\n")


# ------------------------------------------------------------------------------- build ------
def build(master_p3d, n_chord, n_span, out, fmt, report, quiet=False):
    def say(*a):
        if not quiet:
            print(*a)

    B = read_p3d_ascii(master_p3d)
    dims = [b.shape[:2] for b in B]
    say(f"master: {len(B)} zones, dims {dims}")
    fam = {FAM_CHORD: "chord", FAM_SPAN: "span", FAM_WRAP: "wrap"}
    for (ni, nj) in dims:
        for d in (ni, nj):
            if d not in fam:
                raise RuntimeError(f"REFUSED: master dim {d} is not a known family {sorted(fam)}")

    u_span = np.linspace(0.0, float(FAM_SPAN - 1), n_span)
    u_wrap = np.arange(float(FAM_WRAP))

    # --- stage 1: refine the SPAN direction wherever a zone has one -------------------------
    S = []
    for b in B:
        ni, nj, _ = b.shape
        if ni == FAM_SPAN:
            S.append(resample_axis(b, 0, u_span))
        elif nj == FAM_SPAN:
            S.append(resample_axis(b, 1, u_span))
        else:
            S.append(b.copy())

    # --- the per-station chord parameter, from the SPAN-REFINED upper surface ---------------
    G, xs, cdf = registered_cdf()
    up, strip, te = S[Z_UPPER], S[Z_STRIP], S[Z_TE]          # (n_span,257) (n_span,17) (17,n_span)
    U = []
    for s in range(n_span):
        x_le = float(strip[s, :, 0].min())
        x_te = float(te[:, s, 0].max())
        xc = (up[s, :, 0] - x_le) / (x_te - x_le)
        U.append(chord_param(xc, xs, cdf, n_chord))
    u_tip = U[-1]     # the tip station's parameter; every tip-collar zone chains to it

    # --- stage 2: refine the CHORD direction ------------------------------------------------
    N = []
    for z, b in enumerate(S):
        ni, nj, _ = b.shape
        has_span = (B[z].shape[0] == FAM_SPAN) or (B[z].shape[1] == FAM_SPAN)
        if ni == FAM_CHORD:
            N.append(resample_axis_perline(b, 0, U) if has_span
                     else resample_axis(b, 0, u_tip))
        elif nj == FAM_CHORD:
            N.append(resample_axis_perline(b, 1, U) if has_span
                     else resample_axis(b, 1, u_tip))
        else:
            N.append(b.copy())

    # --- stage 3: ENFORCE coincidence, and MEASURE what enforcing it had to move ------------
    shared = discover_shared_edges(B)
    classes = discover_shared_corners(B)
    say(f"shared edges discovered by EXACT array equality: {len(shared)}; "
        f"shared corner classes: {len(classes)}")
    moved = 0.0
    for (a, ka, c, kc, rev) in shared:
        src = edge_slots(N[a])[ka]
        dst = edge_slots(N[c])[kc]
        newv = src[::-1] if rev else src
        moved = max(moved, float(np.abs(dst - newv).max()))
        dst[...] = newv
    for cl in classes:
        z0, k0 = cl[0]
        i0 = corner_slots(N[z0])[k0]
        pt = N[z0][i0[0], i0[1]].copy()
        for (z, k) in cl[1:]:
            i = corner_slots(N[z])[k]
            moved = max(moved, float(np.abs(N[z][i[0], i[1]] - pt).max()))
            N[z][i[0], i[1]] = pt
    say(f"  max coordinate displacement imposed by enforcing coincidence: {moved:.3e} m "
        f"(chord ~0.8 m).  A value at roundoff means the independent per-zone refinements had "
        f"ALREADY agreed; the copy is what makes it exact.")

    # --- stage 4: THE ASSERTION -------------------------------------------------------------
    fails = []
    for (a, ka, c, kc, rev) in shared:
        va, vc = edge_slots(N[a])[ka], edge_slots(N[c])[kc]
        ok = np.array_equal(va, vc[::-1]) if rev else np.array_equal(va, vc)
        say(f"  EDGE Z{a}.{ka} <-> Z{c}.{kc}  n={va.shape[0]:4d}  "
            f"{'REV' if rev else 'FWD'}  BIT-IDENTICAL: {ok}")
        if not ok:
            fails.append(f"edge Z{a}.{ka}/Z{c}.{kc}")
    ncorn = 0
    for cl in classes:
        z0, k0 = cl[0]
        i0 = corner_slots(N[z0])[k0]
        pt = N[z0][i0[0], i0[1]]
        for (z, k) in cl[1:]:
            ncorn += 1
            i = corner_slots(N[z])[k]
            if not np.array_equal(N[z][i[0], i[1]], pt):
                fails.append(f"corner Z{z}.{k}")
    say(f"  shared corners checked: {ncorn} in {len(classes)} classes, "
        f"all bit-identical: {not any('corner' in f for f in fails)}")
    if fails:
        print("ASSERTION FAILED:", fails, file=sys.stderr)
        return 2, None
    say("ASSERTION PASSED: every shared edge and every shared corner is BIT-IDENTICAL "
        "(numpy.array_equal; no tolerance is used anywhere in this file)")

    # --- stage 5: measured resolution and face counts ---------------------------------------
    faces = sum((b.shape[0] - 1) * (b.shape[1] - 1) for b in N)
    wing = ((N[Z_UPPER].shape[0] - 1) * (N[Z_UPPER].shape[1] - 1)
            + (N[Z_LOWER].shape[0] - 1) * (N[Z_LOWER].shape[1] - 1))
    meas = measure_resolution(N)
    say(f"new surface: dims {[list(b.shape[:2]) for b in N]}")
    say(f"  surface faces ALL 9 ZONES = {faces:,}   wing-loop only = {wing:,}"
        f"   (tip/collar = {faces - wing:,}, +{100.0 * (faces - wing) / wing:.1f}%)")
    say(f"  MEASURED nose  Delta x/c, worst over {meas['n_span_stations']} stations "
        f"= {meas['nose_dxc_max']:.4e}  (registered gate <= 0.0016)")
    say(f"  MEASURED shock-band [0.15,0.60] Delta x/c, worst = {meas['shock_dxc_max']:.4e}"
        f"  (registered gate <= 0.0012)")
    say(f"  distinct span stations = {meas['distinct_span_stations']} of {n_span} "
        f"(gen_m6_gridb SNAPPED and produced 161 distinct of 177)")
    say(f"  nose-strip -> wing first-cell spacing ratio, worst = "
        f"{meas['junction_ratio_max']:.2f}")

    if out:
        if fmt == "ascii":
            write_p3d_ascii(out, N)
        else:
            write_p3d_fortran(out, N, real4=fmt.endswith("r4"), big=fmt.startswith("big"))
        say(f"WROTE {out}  fmt={fmt}  {os.path.getsize(out):,} bytes")
    if report:
        json.dump({"WHAT": "re-clustered 9-zone M6 surface, coincidence by construction",
                   "master": master_p3d, "n_chord": n_chord, "n_span": n_span,
                   "dims": [list(b.shape[:2]) for b in N],
                   "surface_faces_all9": faces, "surface_faces_wing_loop": wing,
                   "shared_edges": len(shared), "shared_corner_classes": len(classes),
                   "shared_corner_pairs_checked": ncorn,
                   "edges_and_corners_bit_identical": True,
                   "coincidence_enforcement_displacement_m": moved,
                   "measured": meas}, open(report, "w"), indent=1)
        say(f"WROTE {report}")
    return 0, N


def measure_resolution(N):
    """Per span station, in that station's own x/c: nose spacing (from the LE nose strip) and
    the worst chordwise spacing inside the registered shock band."""
    up, strip, te = N[Z_UPPER], N[Z_STRIP], N[Z_TE]
    n_span = strip.shape[0]
    nose_max = shock_max = jr_max = 0.0
    for s in range(n_span):
        x_le = float(strip[s, :, 0].min())
        x_te = float(te[:, s, 0].max())
        c = x_te - x_le
        d_strip = np.abs(np.diff(strip[s, :, 0])) / c
        x = up[s, :, 0]
        d_up = np.abs(np.diff(x)) / c
        xc = (x[:-1] - x_le) / c
        band = (xc >= 0.15) & (xc <= 0.60)
        nose_max = max(nose_max, float(d_strip.max()))
        if band.any():
            shock_max = max(shock_max, float(d_up[band].max()))
        jr_max = max(jr_max, float(d_up[0] / d_strip.max()))
    zs = np.array([strip[s, 0, 2] for s in range(n_span)])
    return {"nose_dxc_max": nose_max, "shock_dxc_max": shock_max,
            "junction_ratio_max": jr_max, "n_span_stations": int(n_span),
            "distinct_span_stations": int(len(np.unique(np.round(zs, 12))))}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--master", default=os.path.join(RR, "master_surface", "m6_fine.xyz"))
    ap.add_argument("--n-chord", type=int, default=557)
    ap.add_argument("--n-span", type=int, default=177)
    ap.add_argument("--out", default=None)
    ap.add_argument("--fmt", default="big_r8",
                    choices=["big_r8", "big_r4", "little_r8", "little_r4", "ascii"])
    ap.add_argument("--report", default=None)
    a = ap.parse_args()
    rc, _ = build(a.master, a.n_chord, a.n_span, a.out, a.fmt, a.report)
    sys.exit(rc)
