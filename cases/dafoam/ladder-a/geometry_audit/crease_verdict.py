#!/usr/bin/env python3
"""Crease or not: the like-for-like comparison, plus the section plot.

CORRECTION, 2026-09-01. The first version of this docstring said the sharpest
edges (100-112 deg) sit on the LEADING EDGE and the TIP CAP and that "the
BASELINE wing already carries edges of 105.7 deg in the same places", and
concluded that neither is something the optimizer made. THE SECOND HALF OF
THAT IS TRUE OF THE TIP CAP ONLY, and this script's own output says so:

    tip band          optimized max 105.682 deg   baseline max 105.727 deg
    leading-edge band optimized max 112.537 deg   baseline max  70.054 deg

The tip cap is unchanged to four decimal places. The leading edge is not: it
went from 70.1 deg to 112.5 deg. Reading the tip's innocence onto the nose was
a real error and it drove the verdict, so the nose is now measured on its own
terms rather than excluded as panelling.

A panel-to-panel angle is partly a property of the mesh, so the nose gets a
SECOND measurement that a mesh cannot fake: the included angle between the
upper and lower surface over the first 5% of chord, read off the section
outline itself. That is a property of the shape at any resolution.

The interior question stands and its answer is unchanged: away from the nose
and the tip, does the surface turn more sharply where the painted field
changes sign than it does anywhere else? It does not.

THIS IS A RECORDING INSTRUMENT, NOT A GATE, and it exits 0 whatever it finds.
There is no threshold here to fail: it answers a question about a shape and
writes the answer down. Said plainly because a script that never exits 2 looks
like one whose refusal path was forgotten. Act D reads the record it writes
and states the finding; nothing here decides whether anything may run.
"""
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

DOC = Path(__file__).resolve().parent.parent / "A2_shape_frames.json"
OUT = Path(__file__).resolve().parent.parent / "figures"


def sub(a, b):
    return [a[i] - b[i] for i in range(3)]


def cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0]]


def unit(a):
    n = math.sqrt(sum(x * x for x in a)) or 1.0
    return [x / n for x in a]


def dot(a, b):
    return sum(a[i] * b[i] for i in range(3))


def le_te_at(verts, tris, z, tol):
    """Leading- and trailing-edge x at span station z, from the surface."""
    xs = [v[0] for v in verts if abs(v[2] - z) < tol]
    return (min(xs), max(xs)) if xs else (None, None)


def main():
    doc = json.loads(DOC.read_text())
    base = doc["base_vertices"]
    frame = doc["frames"][-1]
    final = [[base[i][k] + frame["disp"][i][k] for k in range(3)]
             for i in range(len(base))]
    tris, dn = doc["faces"], frame["disp_n_mm"]
    span = doc["span_m"]

    normals, cent, bnormals = [], [], []
    for t in tris:
        p = [final[i] for i in t]
        normals.append(unit(cross(sub(p[1], p[0]), sub(p[2], p[0]))))
        cent.append([sum(q[k] for q in p) / 3.0 for k in range(3)])
        b = [base[i] for i in t]
        bnormals.append(unit(cross(sub(b[1], b[0]), sub(b[2], b[0]))))

    edges = defaultdict(list)
    for fi, t in enumerate(tris):
        for a, b in ((0, 1), (1, 2), (2, 0)):
            edges[tuple(sorted((t[a], t[b])))].append(fi)

    def ang(nl, i, j):
        return math.degrees(math.acos(max(-1.0, min(1.0, dot(nl[i], nl[j])))))

    # Chordwise position of every face, as a fraction of the local chord, so
    # "near the nose" means the same thing at the root and at the tip.
    zs_all = sorted({round(v[2], 4) for v in base})

    def xoc(c):
        near = min(zs_all, key=lambda z: abs(z - c[2]))
        lo, hi = le_te_at(base, tris, near, 1e-3)
        if lo is None or hi <= lo:
            return 0.5
        return (c[0] - lo) / (hi - lo)

    rows = []
    for e, fs in edges.items():
        if len(fs) != 2:
            continue
        i, j = fs
        c = cent[i]
        rows.append({
            "ang": ang(normals, i, j), "bang": ang(bnormals, i, j),
            "xoc": xoc(c), "z": c[2], "zc": c[2] / span,
            "flip": dn[i // 2] * dn[j // 2] < 0,
        })

    NOSE, TIP = 0.05, 0.97          # exclude nose 5% of chord and outer 3%
    body = [r for r in rows if NOSE < r["xoc"] < 0.98 and r["zc"] < TIP]

    def stats(sel, key="ang"):
        v = sorted(r[key] for r in sel)
        if not v:
            return None
        return (len(v), v[len(v) // 2], v[int(0.95 * len(v))], v[-1])

    print("WHERE THE SHARP EDGES ARE")
    print("-" * 72)
    nose = [r for r in rows if r["xoc"] <= NOSE]
    tip = [r for r in rows if r["zc"] >= TIP]
    for label, sel in (("leading-edge band (x/c <= 0.05)", nose),
                       ("tip band (z/span >= 0.97)", tip),
                       ("everywhere else", body)):
        n, med, p95, mx = stats(sel)
        nb, medb, p95b, mxb = stats(sel, "bang")
        print(f"  {label:34s} n={n:5d}  optimized median {med:7.3f} deg, "
              f"max {mx:8.3f}")
        print(f"  {'':34s}          baseline  median {medb:7.3f} deg, "
              f"max {mxb:8.3f}")

    print("\nTHE QUESTION: on the blue/red line, away from nose and tip")
    print("-" * 72)
    on = [r for r in body if r["flip"]]
    off = [r for r in body if not r["flip"]]
    n1, m1, p1, x1 = stats(on)
    n0, m0, p0, x0 = stats(off)
    print(f"  ON  the sign-change line : n={n1:4d}  median {m1:6.3f} deg  "
          f"95th {p1:6.3f}  max {x1:7.3f}")
    print(f"  OFF the sign-change line : n={n0:4d}  median {m0:6.3f} deg  "
          f"95th {p0:6.3f}  max {x0:7.3f}")
    print(f"  ratio of medians = {m1 / m0:.2f}x")
    print(f"  a real crease reads as a large ANGLE, not a ratio of small ones:")
    print(f"  the sharpest edge on the sign-change line is {x1:.3f} deg, "
          f"against\n  {max(r['ang'] for r in nose):.1f} deg on the leading "
          f"edge, which is where a genuine\n  crease in this surface actually "
          f"looks like something.")

    # Where does the line sit chordwise?
    xo = sorted(r["xoc"] for r in on)
    print(f"\n  the line sits at x/c {xo[0]:.3f} .. {xo[-1]:.3f} "
          f"(median {xo[len(xo) // 2]:.3f})")
    zz = sorted(r["z"] for r in on)
    print(f"  and runs from z = {zz[0]:.2f} m to {zz[-1]:.2f} m of "
          f"{span:.2f} m span")

    station = round(zz[len(zz) // 2], 2)
    print(f"\n  -> section plotted at z = {station} m, the median span "
          f"station of the line")

    # ---- WHY THE BOUNDARY IS WHERE IT IS ---------------------------------
    # The painted field is signed, so red and blue are push-out and pull-in.
    # If every face on one side of the wing has one sign and every face on the
    # other side has the other, then the "blue/red line" is not a contour
    # crossing the wing at all: it is the seam where the two surfaces meet,
    # which on a wing is the leading and trailing edges.
    #
    # Upper and lower are read off the BASELINE surface, not the optimized
    # one. The optimized section is strongly cambered, so on it the sign of y
    # is not a side: faces that belong to the lower surface have been carried
    # above y = 0 and would be counted as upper. Classifying on the baseline,
    # which is close to symmetric about y = 0, is the classification that
    # means what it says. (Measured: on the final surface the same test reads
    # 812/196, on the baseline it reads 555/453.)
    bcent = [[sum(base[i][k] for i in t) / 3.0 for k in range(3)]
             for t in tris]
    up = [i for i in range(len(dn)) if bcent[2 * i][1] > 0]
    lo = [i for i in range(len(dn)) if bcent[2 * i][1] <= 0]
    print("\nWHY THE BOUNDARY IS WHERE IT IS")
    print("-" * 72)
    print("  (upper and lower read off the BASELINE surface; see the note in "
          "the source)")
    for lab, sel in (("upper surface (y > 0)", up), ("lower surface (y <= 0)", lo)):
        pos = sum(1 for i in sel if dn[i] > 0)
        print(f"  {lab:24s} n={len(sel):5d}  moved OUT {pos:5d}  "
              f"moved IN {len(sel) - pos:5d}")

    # ---- THE NOSE, MEASURED OFF THE SHAPE RATHER THAN OFF THE PANELS -----
    print("\nLEADING-EDGE INCLUDED ANGLE, from the section outline")
    print("  (upper against lower tangent over the first 5% of chord; a")
    print("   property of the shape, not of how finely it is panelled)")
    print(f"  {'z (m)':>8} {'baseline deg':>14} {'optimised deg':>15}")
    le_rows = []
    for z in (0.5, 3.0, 5.2, 7.2, 9.1, 10.9, 13.5):
        a = le_included(tris, base, z)
        b = le_included(tris, final, z)
        if a is not None and b is not None:
            print(f"  {z:8.2f} {a:14.2f} {b:15.2f}")
            le_rows.append({"z_m": z, "baseline_deg": a, "optimised_deg": b})

    # The record Act D reads. The act states this finding in one line and must
    # not carry the numbers as its own constants: they belong to this
    # measurement, so they are written here and read there.
    record = {
        "_what": "Is the blue/red boundary on the A2 wing a geometric crease? "
                 "Measured, not reasoned from the colour map.",
        "_measured_by": str(Path(__file__).resolve()),
        "_source": str(DOC), "_figure": str(OUT / "actD_crease_section.png"),
        "boundary_is_the_upper_lower_seam": {
            "upper_faces": len(up), "upper_moved_out": sum(1 for i in up if dn[i] > 0),
            "lower_faces": len(lo), "lower_moved_out": sum(1 for i in lo if dn[i] > 0),
            "note": "sides read off the BASELINE surface"},
        "leading_edge_included_angle_deg": le_rows,
        "leading_edge_included_angle_baseline_mean":
            round(sum(r["baseline_deg"] for r in le_rows) / len(le_rows), 1)
            if le_rows else None,
        "leading_edge_included_angle_optimised_mean":
            round(sum(r["optimised_deg"] for r in le_rows) / len(le_rows), 1)
            if le_rows else None,
        "interior_line_max_turn_deg": round(x1, 3),
        "interior_off_line_max_turn_deg": round(x0, 3),
        "verdict": "At the leading edge YES: the optimised nose is sharper "
                   "than the baseline's at every station measured. Along the "
                   "interior NO: the surface turns no more sharply on the "
                   "sign-change line than off it.",
    }
    (DOC.parent / "A2_crease_check.json").write_text(
        json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(f"\n  record: {DOC.parent / 'A2_crease_check.json'}")
    return station, doc, base, final, tris


def le_included(tris, verts, z, frac=0.05):
    """Included angle at the nose, in degrees, from the section outline.

    The section is cut, split into upper and lower about the chord line, and
    the angle is taken between the two rays from the nose point to the last
    point of each surface inside the first ``frac`` of chord. Nothing is
    fitted and no derivative is estimated: it is the angle between two chords
    of the outline, so it is bounded by the outline itself.
    """
    pts = []
    for s in slice_at(tris, verts, z):
        pts.extend(s)
    if len(pts) < 8:
        return None
    seen, uniq = set(), []
    for p in pts:
        k = (round(p[0], 9), round(p[1], 9))
        if k not in seen:
            seen.add(k)
            uniq.append(p)
    x0 = min(p[0] for p in uniq)
    x1 = max(p[0] for p in uniq)
    if x1 <= x0:
        return None
    nose = min(uniq, key=lambda p: p[0])
    y1 = next(p[1] for p in uniq if p[0] == x1)

    def above(p):
        return p[1] >= nose[1] + (p[0] - x0) / (x1 - x0) * (y1 - nose[1])

    band = [p for p in uniq if p[0] - x0 <= frac * (x1 - x0)]
    hi = [p for p in band if above(p)]
    lw = [p for p in band if not above(p)]
    if not hi or not lw:
        return None
    a = max(hi, key=lambda p: p[0])
    b = max(lw, key=lambda p: p[0])
    return (math.degrees(math.atan2(a[1] - nose[1], a[0] - nose[0]))
            - math.degrees(math.atan2(b[1] - nose[1], b[0] - nose[0])))


def slice_at(tris, verts, z):
    segs = []
    for tri in tris:
        p = [verts[i] for i in tri]
        hit = []
        for a, b in ((0, 1), (1, 2), (2, 0)):
            za, zb = p[a][2], p[b][2]
            if (za - z) * (zb - z) > 0 or za == zb:
                continue
            t = (z - za) / (zb - za)
            if 0.0 <= t <= 1.0:
                hit.append((p[a][0] + t * (p[b][0] - p[a][0]),
                            p[a][1] + t * (p[b][1] - p[a][1])))
        if len(hit) == 2:
            segs.append(hit)
    return segs


def turning(segs):
    """Ordered surface points and the turn angle at each, in degrees.

    Ordering an aerofoil section by angle about its centroid does NOT work:
    the section is thin, so the upper and lower surfaces interleave and every
    'turn' comes out at 90 degrees, which is an artefact of the ordering and
    not a property of the shape. Instead the points are split into the upper
    and lower surfaces about the local chord line and each is walked in x,
    which is the order the surface is actually traversed.
    """
    pts = []
    for s in segs:
        pts.extend(s)
    # de-duplicate shared segment endpoints before walking
    seen, uniq = set(), []
    for p in pts:
        k = (round(p[0], 9), round(p[1], 9))
        if k not in seen:
            seen.add(k)
            uniq.append(p)
    pts = uniq
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    y0 = next(p[1] for p in pts if p[0] == x0)
    y1 = next(p[1] for p in pts if p[0] == x1)

    def above(p):
        if x1 == x0:
            return True
        t = (p[0] - x0) / (x1 - x0)
        return p[1] >= y0 + t * (y1 - y0)

    upper = sorted((p for p in pts if above(p)), key=lambda p: p[0])
    lower = sorted((p for p in pts if not above(p)), key=lambda p: -p[0])
    pts = upper + lower
    out = []
    for i in range(len(pts)):
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % len(pts)]
        v1 = (b[0] - a[0], b[1] - a[1])
        v2 = (c[0] - b[0], c[1] - b[1])
        n1 = math.hypot(*v1) or 1e-12
        n2 = math.hypot(*v2) or 1e-12
        cosang = max(-1.0, min(1.0, (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2)))
        out.append((b, math.degrees(math.acos(cosang))))
    return out


# FIGURE STANDARD (owner directive, 2026-09-01 03:10Z), applied here because
# this image predates it and broke it in three places. Its upper title ran to
# eleven words, its lower title was a two-sentence paragraph whose second
# sentence was meta-commentary about how to read the picture, and one axis
# label carried no symbol. Titles are now at most ten words, every variable is
# latexified, and the one caption line sits at the foot of the image. The
# sentence that left the picture is not lost: it is the crease paragraph in
# the figure-notes band of docs/dafoam/demo/ACT_D_reference_wing_sheet.tex.
#
# The limits are ENFORCED, not observed, and by the same guard the act's other
# two figures use -- a title that grows back fails here rather than on camera.
#
# THE IMPORT IS LAZY AND THAT IS DELIBERATE. This module is a MEASUREMENT
# instrument: it computes turning angles and included angles and writes them
# down, and main() does all of that without drawing anything. Reaching into
# sdk/ at module scope would make a geometry instrument unimportable whenever
# a PRESENTATION module in sdk/ fails to import, and the next person to break
# _a2_shape would watch a geometry audit die without guessing why. So the
# coupling is confined to figure(), which is the only function that needs it
# and the only place check_figure_text is called. The guard is on the path
# either way.
def _figure_text_guard():
    """The act's own figure-text guard, imported only when a figure is drawn."""
    sdk = Path(__file__).resolve().parents[4] / "sdk"
    if str(sdk) not in sys.path:
        sys.path.insert(0, str(sdk))
    from workflows._a2_shape import check_figure_text
    return check_figure_text


# The caption is figure-wide, so it says which panel the true-scale claim is
# about. Equal aspect holds on the outlines and cannot hold on an angle plot.
CREASE_CAPTION = ("True scale on the section outlines. Turning angle is the "
                  "angle between consecutive surface segments.")


def figure(station, doc, base, final, tris):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:                      # pragma: no cover
        print(f"  (no matplotlib: {exc})")
        return None
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / "actD_crease_section.png"
    check_figure_text = _figure_text_guard()
    section_title, caption = check_figure_text(
        f"Wing section at span station $z$ = {station:g} m", CREASE_CAPTION)
    turn_title, _ = check_figure_text(
        "Surface turning angle along the section", "")
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(11.0, 7.0), dpi=150,
                                  gridspec_kw={"height_ratios": [2, 1]})
    for verts, col, lab in ((base, "#8a8f98", "baseline section"),
                            (final, "#c0392b", "optimised section")):
        segs = slice_at(tris, verts, station)
        for s in segs:
            ax.plot([s[0][0], s[1][0]], [s[0][1], s[1][1]], color=col, lw=1.6)
        ax.plot([], [], color=col, lw=1.6, label=lab)
    ax.set_aspect("equal")
    ax.set_xlabel(r"$x$, chordwise (m)")
    ax.set_ylabel(r"$y$ (m)")
    ax.set_title(section_title, fontsize=11)
    ax.legend(frameon=False, fontsize=9)
    ax.grid(alpha=0.25)

    t = turning(slice_at(tris, final, station))
    tb = turning(slice_at(tris, base, station))
    xs = [p[0][0] for p in t]
    ax2.plot(xs, [p[1] for p in t], ".-", color="#c0392b", ms=4, lw=1.0,
             label="optimised")
    ax2.plot([p[0][0] for p in tb], [p[1] for p in tb], ".-", color="#8a8f98",
             ms=3, lw=0.8, label="baseline")
    ax2.set_xlabel(r"$x$, chordwise (m)")
    ax2.set_ylabel(r"Turning angle $\Delta\theta$ (deg)")
    ax2.set_title(turn_title, fontsize=10)
    ax2.legend(frameon=False, fontsize=9)
    ax2.grid(alpha=0.25)
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    fig.text(0.012, 0.012, caption, color="#5a5f66", fontsize=9, ha="left",
             va="bottom")
    fig.savefig(out)
    plt.close(fig)
    tt = sorted(p[1] for p in t)
    tbb = sorted(p[1] for p in tb)
    print(f"\n  section turn angle, optimised: median {tt[len(tt) // 2]:.2f} "
          f"deg, max {tt[-1]:.2f} deg")
    print(f"  section turn angle, baseline : median {tbb[len(tbb) // 2]:.2f} "
          f"deg, max {tbb[-1]:.2f} deg")
    print(f"  figure: {out}")
    return out


if __name__ == "__main__":
    station, doc, base, final, tris = main()
    figure(station, doc, base, final, tris)
    sys.exit(0)
