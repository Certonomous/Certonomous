#!/usr/bin/env python3
"""check_le_surface_resolution.py -- CURVATURE-BASED SURFACE-RESOLUTION ADMISSION CHECK.

A NEW 3-D mesh-admission mechanic for docs/standards/MESH_STANDARD.md (the single-mesh
admissibility standard).  The existing hard gates (max non-orthogonality 70 deg, max skewness
4.0, 0 negative-volume cells) grade cell SHAPE; none of them can see whether the wing SURFACE
tessellation is fine enough at the LEADING EDGE to resolve a suction peak.  The M6 own-family
mesh cleared every shape gate at 61 deg / 2.06 and still under-resolved the LE suction peak by
20-60x the +/-0.02 Cp band, because its 1,560-face parent surface has NO leading-edge
clustering (faceted nose).  This check closes exactly that hole:

  GIVEN a wing surface tessellation, for each spanwise section it computes
    * the local LEADING-EDGE RADIUS r_LE (least-squares circle fit to the nose points),
      hence the LE curvature kappa = 1/r_LE;
    * the local CHORDWISE SURFACE SPACING at the LE (nose Delta x/c);
    * how many surface cells span the LE-radius arc;
  and REFUSES (exit 2) a tessellation whose LE cannot resolve the peak, by EITHER criterion:
    (A) nose Delta x/c ABOVE the physics threshold (default 0.0016, the value DERIVED in
        verification/runs/M6_LE_RESOLVED_runs/size_from_physics.py: N_DESIGN=18 cells across
        the measured LE gradient width W_min=0.0288 x/c), OR
    (B) fewer than K cells (default 8) spanning the LE-radius arc (a geometry-only
        curvature-resolution floor: too few cells across the nose circle cannot represent the
        curvature that sets the suction peak).

RULE 3 (planted / positive control), EXERCISED BEFORE ANY CLEAN PASS IS TRUSTED.  A
deliberately COARSE synthetic section is driven through the SAME metric and MUST be REFUSED;
a FINE synthetic section MUST PASS.  A checker not shown able to REFUSE a coarse nose (and to
ADMIT a fine one) cannot have its admission of a real surface trusted -- a zero from a reader
not shown able to see a non-zero is not evidence.  --selftest runs only the controls; every
real run runs them first and refuses (exit 2) if either does not behave.

EXIT VOCABULARY:
    0   ADMISSIBLE -- every section resolves the LE by both criteria (controls fired).
    2   REFUSED    -- a section is inadmissible, OR a planted control did not behave, OR an
                     input is missing/unreadable.  REFUSE RATHER THAN DEGRADE.
    70  INTERNAL DEFECT of this checker (never a finding about a mesh).

Reads inputs only; writes at most one JSON report to a path the caller names.  Sends nothing,
commits nothing (rules 7, 16).
"""
import argparse
import json
import math
import os
import struct
import sys

# ---- default thresholds (the mesh-standard clause states these; a caller may tighten) -----
DEFAULT_NOSE_DXC_MAX = 0.0016      # physics threshold from size_from_physics.py (nose N_DESIGN=18)
DEFAULT_K_LE_ARC_MIN = 8           # min cells spanning the LE-radius arc (curvature floor)
DEFAULT_NPTS_CIRCLE_FIT = 7        # nose points used for the LE-radius circle fit
# Shock-band resolution (criterion C).  The M6 lambda-shock sweeps x/c ~0.20..0.58 across span
# (measured in size_from_physics.py, corroborated by the A3 primal's shock_location.json); the
# clustering band brackets it.  SHOCK_DXC_MAX is the physics shock target (tightest station
# ~0.0008; the admission gate is set a hair looser so a mesh built to target passes).
DEFAULT_SHOCK_XC_LO = 0.15
DEFAULT_SHOCK_XC_HI = 0.60
DEFAULT_SHOCK_DXC_MAX = 0.0012


class Refusal(Exception):
    """exit 2 -- inadmissible surface, control failure, or unreadable input."""


class InternalDefect(Exception):
    """exit 70 -- a defect in THIS checker."""


# --------------------------------------------------------------------------------------
# GEOMETRY.  A section is an ORDERED polyline of (x, y, z) surface points wrapping the
# airfoil.  We work in the (chord, thickness) plane of the section: the spanwise coordinate
# is (near) constant on a section, so we drop the axis of smallest variance and keep the two
# in-plane axes, then identify chord = larger-extent axis, thickness = the other.
# --------------------------------------------------------------------------------------
def _section_plane(points):
    """-> (chord_vals, thick_vals) arrays for the section, chord = larger-extent in-plane axis."""
    if len(points) < 5:
        raise Refusal(f"section has {len(points)} points; need >= 5 to fit an LE circle.")
    ext = []
    for a in range(3):
        vals = [p[a] for p in points]
        ext.append(max(vals) - min(vals))
    span_axis = min(range(3), key=lambda a: ext[a])     # smallest variation = spanwise
    rest = [a for a in range(3) if a != span_axis]
    chord_axis = max(rest, key=lambda a: ext[a])
    thick_axis = [a for a in rest if a != chord_axis][0]
    return ([p[chord_axis] for p in points], [p[thick_axis] for p in points],
            {"chord_axis": "xyz"[chord_axis], "thick_axis": "xyz"[thick_axis],
             "span_axis": "xyz"[span_axis], "chord_extent": ext[chord_axis]})


def _fit_circle(xs, ys):
    """Kasa algebraic least-squares circle fit, mean-centred for conditioning.  -> (xc, yc, r)."""
    n = len(xs)
    if n < 3:
        raise InternalDefect("circle fit needs >= 3 points")
    mx, my = sum(xs) / n, sum(ys) / n
    u = [x - mx for x in xs]
    v = [y - my for y in ys]
    Suu = sum(a * a for a in u); Svv = sum(b * b for b in v); Suv = sum(a * b for a, b in zip(u, v))
    Suuu = sum(a ** 3 for a in u); Svvv = sum(b ** 3 for b in v)
    Suvv = sum(a * b * b for a, b in zip(u, v)); Svuu = sum(b * a * a for a, b in zip(u, v))
    det = Suu * Svv - Suv * Suv
    if abs(det) < 1e-30:
        raise InternalDefect("degenerate circle fit (collinear nose points)")
    c1 = 0.5 * (Suuu + Suvv)
    c2 = 0.5 * (Svvv + Svuu)
    uc = (c1 * Svv - c2 * Suv) / det
    vc = (c2 * Suu - c1 * Suv) / det
    xc, yc = uc + mx, vc + my
    r = math.sqrt(uc * uc + vc * vc + (Suu + Svv) / n)
    return xc, yc, r


def section_le_metrics(points, npts_fit=DEFAULT_NPTS_CIRCLE_FIT):
    """-> per-section metrics: chord, LE radius, nose Delta x/c, cells across LE-radius arc."""
    ch, th, axes = _section_plane(points)
    n = len(ch)
    chord = max(ch) - min(ch)
    if chord <= 0.0:
        raise Refusal("section has zero chordwise extent.")
    # LE point = minimum chordwise coordinate
    le_i = min(range(n), key=lambda i: ch[i])
    le = (ch[le_i], th[le_i])
    # neighbours in polyline order (wrap): edges adjacent to the LE point
    prev_i = (le_i - 1) % n
    next_i = (le_i + 1) % n
    def _d(i, j):
        return math.hypot(ch[i] - ch[j], th[i] - th[j])
    ds_le = 0.5 * (_d(le_i, prev_i) + _d(le_i, next_i))     # mean adjacent surface-edge length
    # chordwise spacing at the nose (projection onto chord axis) -- the physics-relevant Delta x
    dx_le = 0.5 * (abs(ch[le_i] - ch[prev_i]) + abs(ch[le_i] - ch[next_i]))
    nose_dx_over_c = dx_le / chord
    nose_ds_over_c = ds_le / chord
    # LE radius: circle fit to the nose points within a small chordwise WINDOW of the LE (both
    # surfaces).  A fit to the absolute-nearest points is ill-conditioned under strong LE
    # clustering -- those points span a near-zero x-range and are collinear.  The window spans
    # the nose arc.  It is widened until the fit is well-conditioned and >= npts_fit points are
    # used, so the metric is deterministic and robust.
    x_le = ch[le_i]
    r_le = None
    fit_window = None
    n_fit = 0
    for win_xc in (0.01, 0.02, 0.03, 0.05, 0.08):
        idx = [i for i in range(n) if 0.0 <= (ch[i] - x_le) <= win_xc * chord]
        if len(idx) < max(5, npts_fit):
            continue
        try:
            _xc, _yc, r_cand = _fit_circle([ch[i] for i in idx], [th[i] for i in idx])
        except InternalDefect:
            continue
        if r_cand and 0.0 < r_cand < chord:    # a plausible nose radius
            r_le, fit_window, n_fit = r_cand, win_xc, len(idx)
            break
    # A nose too sparse/degenerate to fit an LE circle is NOT an unreadable input -- it is a
    # section that cannot be shown to resolve the LE, i.e. an inadmissible one.  r_LE=None
    # therefore FAILS criterion (B) in admit_section (cells across LE radius unknown -> < K),
    # rather than raising.  The distinction: Refusal is for a missing/malformed INPUT; a coarse
    # nose is a finding ABOUT the surface.
    r_le_over_c = (r_le / chord) if r_le else None
    # cells spanning the LE-radius arc: surface points within Euclidean distance r_le of the LE.
    # If the LE circle could not be fit (too coarse a nose), this is None -> fails (B).
    cells_across_le_radius = (sum(1 for i in range(n) if _d(i, le_i) <= r_le)
                              if r_le else None)
    # criterion (C): shock-band chordwise resolution.  Normalise chord to x/c, take the UPPER
    # surface, and find the max consecutive chordwise gap in the shock band.  Upper vs lower is
    # split at the MID-THICKNESS line (max+min)/2 -- robust for an O-section whose LE point
    # carries a small nonzero thickness (splitting at the LE-point thickness misclassifies).
    x_lo = min(ch)
    xoc = [(c - x_lo) / chord for c in ch]
    th_mid = 0.5 * (max(th) + min(th))
    upper_band_gaps = []
    upper_pts = sorted((xoc[i], th[i]) for i in range(n) if th[i] >= th_mid)
    for (xa, _ta), (xb, _tb) in zip(upper_pts, upper_pts[1:]):
        if xb >= DEFAULT_SHOCK_XC_LO and xa <= DEFAULT_SHOCK_XC_HI:
            upper_band_gaps.append(xb - xa)
    shock_band_max_dx_over_c = max(upper_band_gaps) if upper_band_gaps else None
    return {
        "n_points": n, "axes": axes, "chord": chord,
        "LE_point_chord_thick": le,
        "r_LE": r_le, "r_LE_over_c": r_le_over_c, "kappa_LE": (1.0 / r_le if r_le else None),
        "LE_fit_window_xc": fit_window, "LE_fit_n_points": n_fit,
        "nose_ds_surface": ds_le, "nose_dx_chordwise": dx_le,
        "nose_dx_over_c": nose_dx_over_c, "nose_ds_over_c": nose_ds_over_c,
        "cells_across_LE_radius": cells_across_le_radius,
        "shock_band_max_dx_over_c": shock_band_max_dx_over_c,
        "shock_band_xc": [DEFAULT_SHOCK_XC_LO, DEFAULT_SHOCK_XC_HI],
    }


def admit_section(points, nose_dxc_max, k_le_arc_min, shock_dxc_max=DEFAULT_SHOCK_DXC_MAX,
                  npts_fit=DEFAULT_NPTS_CIRCLE_FIT):
    """-> (ok, metrics, reasons).  ok False if ANY criterion (A) LE spacing, (B) LE curvature,
    or (C) shock-band spacing fails."""
    m = section_le_metrics(points, npts_fit=npts_fit)
    reasons = []
    if m["nose_dx_over_c"] > nose_dxc_max:
        reasons.append(f"(A) nose Delta x/c {m['nose_dx_over_c']:.5f} > threshold {nose_dxc_max} "
                       "-- LE chordwise spacing too coarse to resolve the suction-peak gradient")
    if m["cells_across_LE_radius"] is None:
        reasons.append("(B) LE circle could not be fit -- the nose is too sparse/degenerate to "
                       "establish its curvature, so LE resolution cannot be shown")
    elif m["cells_across_LE_radius"] < k_le_arc_min:
        reasons.append(f"(B) cells across LE radius {m['cells_across_LE_radius']} < K "
                       f"{k_le_arc_min} -- too few cells span the LE-radius arc to represent "
                       "the nose curvature")
    sb = m["shock_band_max_dx_over_c"]
    if sb is None:
        reasons.append(f"(C) no upper-surface points in the shock band {m['shock_band_xc']} "
                       "-- the shock region is unresolved")
    elif sb > shock_dxc_max:
        reasons.append(f"(C) shock-band max Delta x/c {sb:.5f} > threshold {shock_dxc_max} "
                       "-- chordwise spacing in the transonic-shock band too coarse to place "
                       "the shock within the Cp band")
    return (len(reasons) == 0), m, reasons


# --------------------------------------------------------------------------------------
# RULE-3 PLANTED / POSITIVE CONTROLS.  A COARSE nose MUST be refused; a FINE nose MUST pass.
# The synthetic sections are unit-chord NACA-0012-like noses: a parabolic LE (z ~ sqrt(x))
# gives a finite LE radius, and the point COUNT near the nose is what we vary.
# --------------------------------------------------------------------------------------
def _synthetic_section(n_per_surface, chord=1.0, thick=0.10, le_cluster=1.0, shock_cluster=False):
    """A closed airfoil-like section. le_cluster>1 clusters points toward the LE (cosine^p);
    shock_cluster adds extra points in the shock band [0.15,0.60] so a FINE control can also
    satisfy criterion (C)."""
    # base cosine distribution in [0,1], clustered near the LE if le_cluster>1.  The exponent
    # applies to the NORMALISED cosine value (which is in [0,1]) so x stays in [0,1].
    xs = [(0.5 * (1 - math.cos(math.pi * (i / (n_per_surface - 1))))) ** le_cluster
          for i in range(n_per_surface)]        # 0..1, clustered near 0 (LE) if le_cluster>1
    if shock_cluster:
        nb = 1400
        lo, hi = DEFAULT_SHOCK_XC_LO - 0.05, DEFAULT_SHOCK_XC_HI + 0.05   # cover the band edges
        band = [lo + (hi - lo) * j / nb for j in range(nb + 1)]
        xs = sorted(set(xs) | set(band))
    # parabolic-nose thickness (finite LE radius): z = thick * sqrt(x) * (1 - x) shape
    def zt(x):
        return thick * (1.834 * math.sqrt(max(x, 0.0)) - 0.630 * x - 1.204 * x * x
                        + 0.582 * x ** 3 - 0.582 * x ** 4)   # NACA-0012-like, sharp-ish TE
    upper = [(x * chord, zt(x) * chord, 0.0) for x in reversed(xs)]     # TE->LE
    lower = [(x * chord, -zt(x) * chord, 0.0) for x in xs[1:]]          # LE->TE
    return upper + lower


def run_controls(nose_dxc_max, k_le_arc_min, shock_dxc_max=DEFAULT_SHOCK_DXC_MAX,
                 npts_fit=DEFAULT_NPTS_CIRCLE_FIT):
    """Coarse MUST refuse; fine MUST pass.  -> dict; raises Refusal if either misbehaves."""
    # COARSE: few points, no LE clustering -> big nose Delta x/c, few cells across the arc,
    # coarse shock band.
    coarse = _synthetic_section(n_per_surface=12, le_cluster=1.0)
    ok_c, m_c, why_c = admit_section(coarse, nose_dxc_max, k_le_arc_min, shock_dxc_max, npts_fit)
    # FINE: many points, strong LE clustering AND shock-band clustering -> passes A, B and C.
    fine = _synthetic_section(n_per_surface=900, le_cluster=2.4, shock_cluster=True)
    ok_f, m_f, why_f = admit_section(fine, nose_dxc_max, k_le_arc_min, shock_dxc_max, npts_fit)
    report = {
        "coarse_control": {"MUST": "REFUSE", "refused": (not ok_c),
                           "nose_dx_over_c": m_c["nose_dx_over_c"],
                           "cells_across_LE_radius": m_c["cells_across_LE_radius"],
                           "shock_band_max_dx_over_c": m_c["shock_band_max_dx_over_c"],
                           "reasons": why_c},
        "fine_control": {"MUST": "PASS", "passed": ok_f,
                         "nose_dx_over_c": m_f["nose_dx_over_c"],
                         "cells_across_LE_radius": m_f["cells_across_LE_radius"],
                         "shock_band_max_dx_over_c": m_f["shock_band_max_dx_over_c"],
                         "reasons": why_f},
    }
    if ok_c:
        raise Refusal("PLANTED CONTROL DID NOT FIRE: the deliberately COARSE nose was ADMITTED "
                      f"(nose dx/c={m_c['nose_dx_over_c']:.5f}, cells={m_c['cells_across_LE_radius']}). "
                      "A checker that admits a coarse nose cannot be trusted to refuse one (rule 3).")
    if not ok_f:
        raise Refusal("POSITIVE CONTROL FAILED: the FINE nose was REFUSED "
                      f"({why_f}). A checker that refuses an adequately resolved nose would "
                      "refuse every real surface -- it is mis-calibrated (rule 3).")
    return report


# --------------------------------------------------------------------------------------
# INPUT READERS.  (a) a sections JSON {"sections": [[[x,y,z],...], ...]}; (b) an STL sliced
# at N spanwise stations into sections.  The mesh-gen dry-run emits (a) directly.
# --------------------------------------------------------------------------------------
def read_sections_json(path):
    with open(path) as fh:
        d = json.load(fh)
    secs = d["sections"] if isinstance(d, dict) else d
    return [[tuple(float(c) for c in p) for p in sec] for sec in secs]


def _read_stl_triangles(path):
    """-> list of (v0,v1,v2) triangles.  Handles ascii and binary STL."""
    with open(path, "rb") as fh:
        head = fh.read(84)
        fh.seek(0)
        raw = fh.read()
    if raw[:5].lower() == b"solid" and b"facet" in raw[:2048].lower():
        tris = []
        verts = []
        for ln in raw.decode("ascii", "replace").splitlines():
            s = ln.split()
            if len(s) == 4 and s[0] == "vertex":
                verts.append(tuple(float(x) for x in s[1:4]))
                if len(verts) == 3:
                    tris.append(tuple(verts)); verts = []
        return tris
    # binary
    ntri = struct.unpack("<I", raw[80:84])[0]
    tris = []
    off = 84
    for _ in range(ntri):
        vals = struct.unpack("<12fH", raw[off:off + 50])
        v0 = (vals[3], vals[4], vals[5]); v1 = (vals[6], vals[7], vals[8])
        v2 = (vals[9], vals[10], vals[11])
        tris.append((v0, v1, v2)); off += 50
    return tris


def slice_stl_to_sections(path, n_stations=7, span_axis=None):
    """Slice an STL at n_stations constant-span planes -> ordered section polylines."""
    tris = _read_stl_triangles(path)
    if not tris:
        raise Refusal(f"{path}: zero STL triangles parsed.")
    allpts = [v for t in tris for v in t]
    ext = [max(p[a] for p in allpts) - min(p[a] for p in allpts) for a in range(3)]
    if span_axis is None:
        # span axis = the axis whose extent is between chord and thickness is ambiguous; the
        # wing spans its LONGEST axis for M6 (semispan ~1.2 m > root chord ~0.8 m).
        span_axis = max(range(3), key=lambda a: ext[a])
    lo = min(p[span_axis] for p in allpts); hi = max(p[span_axis] for p in allpts)
    sections = []
    for k in range(n_stations):
        frac = (k + 0.5) / n_stations
        s = lo + frac * (hi - lo)
        seg = []
        for (a, b, c) in tris:
            for p, q in ((a, b), (b, c), (c, a)):
                if (p[span_axis] - s) * (q[span_axis] - s) < 0:
                    t = (s - p[span_axis]) / (q[span_axis] - p[span_axis])
                    seg.append(tuple(p[i] + t * (q[i] - p[i]) for i in range(3)))
        if len(seg) >= 5:
            sections.append(_order_polyline(seg))
    if not sections:
        raise Refusal(f"{path}: no section had >= 5 slice points.")
    return sections


def _order_polyline(seg):
    """Order scattered slice points into a polyline by nearest-neighbour walk (closed curve)."""
    pts = list(seg)
    ordered = [pts.pop(0)]
    while pts:
        last = ordered[-1]
        j = min(range(len(pts)), key=lambda i: sum((pts[i][a] - last[a]) ** 2 for a in range(3)))
        ordered.append(pts.pop(j))
    return ordered


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sections", help="sections JSON: {'sections': [[[x,y,z],...],...]}")
    ap.add_argument("--stl", help="STL surface to slice into sections")
    ap.add_argument("--n-stations", type=int, default=7)
    ap.add_argument("--nose-dxc-max", type=float, default=DEFAULT_NOSE_DXC_MAX)
    ap.add_argument("--k-le-arc-min", type=int, default=DEFAULT_K_LE_ARC_MIN)
    ap.add_argument("--shock-dxc-max", type=float, default=DEFAULT_SHOCK_DXC_MAX)
    ap.add_argument("--npts-fit", type=int, default=DEFAULT_NPTS_CIRCLE_FIT)
    ap.add_argument("--report", help="write the JSON report here")
    ap.add_argument("--selftest", action="store_true", help="run only the planted controls")
    args = ap.parse_args(argv[1:])

    # RULE 3: controls first, ALWAYS.  A run whose controls misbehave refuses before it grades.
    controls = run_controls(args.nose_dxc_max, args.k_le_arc_min, args.shock_dxc_max,
                            args.npts_fit)
    if args.selftest:
        print("CONTROLS: coarse REFUSED =", controls["coarse_control"]["refused"],
              "| fine PASSED =", controls["fine_control"]["passed"])
        print(json.dumps(controls, indent=2))
        return 0

    if not args.sections and not args.stl:
        raise Refusal("no surface given: pass --sections or --stl (or --selftest).")
    sections = (read_sections_json(args.sections) if args.sections
                else slice_stl_to_sections(args.stl, args.n_stations))

    per = []
    failed = []
    for i, sec in enumerate(sections):
        ok, m, why = admit_section(sec, args.nose_dxc_max, args.k_le_arc_min,
                                   args.shock_dxc_max, args.npts_fit)
        per.append({"section": i, "admissible": ok, "metrics": m, "reasons": why})
        if not ok:
            failed.append(i)

    report = {
        "WHAT": "curvature-based LE surface-resolution admission check",
        "thresholds": {"nose_dx_over_c_max": args.nose_dxc_max,
                       "K_cells_across_LE_radius_min": args.k_le_arc_min,
                       "shock_band_dx_over_c_max": args.shock_dxc_max,
                       "npts_circle_fit": args.npts_fit},
        "rule3_controls": controls,
        "n_sections": len(sections),
        "failed_sections": failed,
        "verdict": "REFUSED" if failed else "ADMISSIBLE",
        "per_section": per,
    }
    if args.report:
        with open(args.report, "w") as fh:
            fh.write(json.dumps(report, indent=2, default=str) + "\n")
        print(f"WROTE {args.report}")
    print(f"controls: coarse refused={controls['coarse_control']['refused']} "
          f"fine passed={controls['fine_control']['passed']}")
    print(f"sections={len(sections)} verdict={report['verdict']} "
          f"failed={failed}")
    for p in per:
        m = p["metrics"]
        sb = m["shock_band_max_dx_over_c"]
        rle = m["r_LE_over_c"]
        print(f"  sec {p['section']}: r_LE/c={rle if rle is None else round(rle,5)} "
              f"nose dx/c={m['nose_dx_over_c']:.5f} cells_LE_radius={m['cells_across_LE_radius']} "
              f"shock dx/c={sb if sb is None else round(sb,5)} "
              f"-> {'OK' if p['admissible'] else 'REFUSE ' + ';'.join(p['reasons'])}")
    return 2 if failed else 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Refusal as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        sys.exit(2)
    except InternalDefect as e:
        print(f"INTERNAL DEFECT: {e}", file=sys.stderr)
        sys.exit(70)
    except Exception as e:            # a crash is not a refusal -> 70
        import traceback
        traceback.print_exc()
        print(f"INTERNAL DEFECT (unhandled {type(e).__name__}): {e}", file=sys.stderr)
        sys.exit(70)
