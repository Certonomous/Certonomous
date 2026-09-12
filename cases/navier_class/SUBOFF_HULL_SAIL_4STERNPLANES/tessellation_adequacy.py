#!/usr/bin/env python3
"""
TESSELLATION ADEQUACY OF THE SUBOFF APPENDED / CONFIG 1 STL SURFACES.

THE QUESTION.  snappyHexMesh snaps cells onto the triangulated surface it is
given.  If an STL FACET is larger than the local CELL, the mesh is finer than the
geometry and the mesher is resolving a facet edge rather than the body.  On thin,
twisted, load-carrying surfaces -- which is exactly what the four stern
appendages are, and they carry the graded normal force -- that shows up as a
faceted pressure distribution on the very surface being banded.

=============================================================================
THE THRESHOLD IS FIXED HERE, IN THIS FILE, BEFORE IT WAS FIRST RUN, AND IT IS
NOT A NUMBER TUNED TO AN ANSWER.
=============================================================================
    GATE:  >= 99.0 % of each graded surface's AREA is carried by facets whose
           LONGEST EDGE is <= the local mesh cell size on that surface.

Rationale, written before the measurement: "one cell per facet" is the natural
criterion -- it is the point at which the mesher stops being able to see the
facet at all -- so the threshold is a property of the mesh/geometry relationship
and not of this body.  99.0 % rather than 100 % because a cosine-clustered
surface necessarily has its coarsest facets at mid-chord, away from the features
that matter, and a single facet must not fail a surface.

=============================================================================
AREA-WEIGHTED, NEVER COUNT-WEIGHTED -- AND BOTH ARE PRINTED SO THE DIFFERENCE
IS VISIBLE.
=============================================================================
A COUNT-weighted facet statistic FLATTERS a coarse surface: cosine clustering
puts most of the FACETS where the surface is finely resolved (the leading and
trailing edges) and most of the AREA where it is not (mid-chord and mid-span).
So the count statistic is dominated by the facets that were never the problem.
The lab has just paid for this once on a propeller: a count-weighted tessellation
statistic read ADEQUATE and the area-weighted one rejected the same surface at
every level.  BOTH numbers are printed here, side by side, precisely so a reader
can see the gap rather than take the favourable one.

TWO CELL SIZES PER SURFACE, BECAUSE ONE IS NOT ENOUGH.  A fin is meshed at its
surface refinement level over most of its area and at the much finer TRAILING-EDGE
BOX level in a thin slab near its base.  A facet that is adequate at 1.23 mm can
be hopeless at 0.15 mm.  Each surface is therefore measured TWICE: against its
surface cell, over the whole surface, and against the finest box cell, over the
facets that lie inside that box.

RULE-3 PLANT.  The dangerous answer is "0 % of the area fails", which is what an
adequate surface looks like AND what a comparator with an inverted test, wrong
units or an empty facet list looks like.  A synthetic surface of KNOWN failing
area is pushed through the SAME statistic on every invocation before any STL is
read, and the tool REFUSES unless it returns that known value -- and returns 0
for a surface that cannot fail.

ZERO `assert` (L-332).  Refusals are sys.exit(2).
"""
import sys
if not __debug__:
    sys.stderr.write("REFUSED: must not run under python3 -O.\n"); sys.exit(2)

import os, json, argparse
import numpy as np

_A1 = "/home/ubuntu/Certonomous/cases/navier_class/SUBOFF_A1"
if _A1 not in sys.path:
    sys.path.insert(0, _A1)
import build_suboff_a1_geometry as A1                  # noqa: E402
FT2M = A1.FT2M

GATE_AREA_FRACTION = 0.990          # fixed before first run; see the docstring
PLANT_FAIL_AREA_FRACTION = 0.75     # known, non-round


def read_facets(path):
    v = []
    with open(path) as f:
        for line in f:
            if line.lstrip().startswith("vertex "):
                v.append([float(q) for q in line.split()[1:4]])
    V = np.asarray(v)
    if V.size == 0 or len(V) % 3 != 0:
        sys.stderr.write(f"REFUSED: {path} parsed to {len(V)} vertices.\n")
        sys.exit(2)
    return V.reshape(-1, 3, 3)


def facet_stats(T):
    """Per-facet area and LONGEST EDGE.  Longest edge, not sqrt(area): it is the
    demanding choice, and a sliver with small area can still span many cells."""
    e0 = T[:, 1] - T[:, 0]; e1 = T[:, 2] - T[:, 1]; e2 = T[:, 0] - T[:, 2]
    area = 0.5 * np.linalg.norm(np.cross(e0, -e2), axis=1)
    lmax = np.maximum(np.maximum(np.linalg.norm(e0, axis=1),
                                 np.linalg.norm(e1, axis=1)),
                      np.linalg.norm(e2, axis=1))
    return area, lmax


def wetted_mask(name, C):
    """WHICH FACETS THE MESHER ACTUALLY SEES.

    MEASURED DEFECT IN THE FIRST RUN OF THIS FILE, recorded rather than quietly
    fixed.  The first version measured EVERY facet of every STL and reported
    100.0 % of the fin area failing, with a maximum facet edge of 51.35 mm.
    Diagnosed by locating the offenders: the worst 1 % of fin area sits at radius
    0.0316 m, which is the BURIED ROOT LID at y0 = 0.10 ft, and the worst sail
    area sits at radius 0.0111 m, which is that solid's BOTTOM LID buried at
    y = 0.  BOTH ARE INSIDE THE HULL AND ARE NEVER MESHED -- snappyHexMesh's
    castellation discards them.  The instrument was measuring geometry that does
    not exist in the mesh.  Restricting to wetted facets is a SCOPE CORRECTION to
    the instrument, not a softening of the gate: the gate value is unchanged and
    the corrected scope is strictly what the gate was always about.
    """
    if name == "hull":
        return np.ones(len(C), dtype=bool)
    r = np.hypot(C[:, 1], C[:, 2])
    rh = np.array([A1.hull_R_ft(x / FT2M) * FT2M for x in C[:, 0]])
    return r > rh + 1.0e-6


def chordal_deviation_hull(C, area):
    """THE FIDELITY STATISTIC, computed exactly on the hull because its analytic
    surface is in hand: how far the triangulation departs from the true surface,
    which is the error the mesher actually inherits."""
    r_facet = np.hypot(C[:, 1], C[:, 2])
    r_true = np.array([A1.hull_R_ft(x / FT2M) * FT2M for x in C[:, 0]])
    return np.abs(r_true - r_facet)


def shares(area, lmax, h):
    """THE statistic.  Returns (area share failing, count share failing)."""
    bad = lmax > h
    tot = float(area.sum())
    if tot <= 0.0:
        return None, None
    return float(area[bad].sum() / tot), float(bad.mean())


def plant_control():
    """Rule 3.  A synthetic surface whose FAILING facets carry a KNOWN area
    share, pushed through the same statistic.  Also the converse: a surface that
    cannot fail must return exactly 0."""
    # one big failing facet of area 3.0 and small passing facets totalling 1.0
    area = np.array([3.0, 0.5, 0.25, 0.25])
    lmax = np.array([10.0, 0.1, 0.1, 0.1])
    a_share, c_share = shares(area, lmax, 1.0)
    want_a = PLANT_FAIL_AREA_FRACTION            # 3.0 / 4.0
    want_c = 0.25                                 # 1 facet of 4
    if abs(a_share - want_a) > 1e-12 or abs(c_share - want_c) > 1e-12:
        sys.stderr.write(f"REFUSED (rule 3): planted an AREA share of {want_a} and "
                         f"a COUNT share of {want_c}; the statistic returned "
                         f"{a_share} and {c_share}.\n"); sys.exit(2)
    a0, c0 = shares(area, lmax, 100.0)
    if a0 != 0.0 or c0 != 0.0:
        sys.stderr.write(f"REFUSED (rule 3): a surface that CANNOT fail returned "
                         f"{a0}, {c0}, not 0.\n"); sys.exit(2)
    # and the plant demonstrates the very gap this tool exists to show:
    return {"planted_area_share": want_a, "returned_area_share": a_share,
            "planted_count_share": want_c, "returned_count_share": c_share,
            "cannot_fail_returns": [a0, c0],
            "note": "on the plant the COUNT share (0.25) understates the AREA "
                    "share (0.75) by a factor of three -- which is the whole "
                    "reason this tool is area-weighted",
            "verdict": "ARMED"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--geom", required=True)
    ap.add_argument("--manifest", required=True,
                    help="a BUILD_MANIFEST.json from build_appended_mesh.py, for "
                         "the MEASURED cell sizes -- never assumed")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    plant = plant_control()
    print(f"rule-3 plant: {plant['verdict']} -- {plant['note']}")

    man = json.load(open(a.manifest))
    cs = man["cell_sizes_m"]
    boxes = man["boxes_m"]
    surf_cell = {"hull": cs["hull_surface"], "sail": cs["sail_surface"]}
    for f in ("fin000_upper_rudder", "fin090_horizontal",
              "fin180_lower_rudder", "fin270_horizontal"):
        surf_cell[f] = cs["fin_surface"]
    box_cell = {"hull": None, "sail": cs["sail_TE_box"]}
    for f in surf_cell:
        if f.startswith("fin"):
            box_cell[f] = cs["fin_TE_box"]

    def in_any_box(C, names):
        m = np.zeros(len(C), dtype=bool)
        for n in names:
            lo, hi = boxes[n]
            m |= np.all((C >= np.array(lo)) & (C <= np.array(hi)), axis=1)
        return m

    rows = []
    fails = []
    for nm, h in sorted(surf_cell.items()):
        p = os.path.join(a.geom, nm + ".stl")
        if not os.path.isfile(p):
            continue
        T = read_facets(p)
        area, lmax = facet_stats(T)
        Cc = T.mean(axis=1)
        wet = wetted_mask(nm, Cc)
        T, area, lmax, Cc = T[wet], area[wet], lmax[wet], Cc[wet]
        a_share, c_share = shares(area, lmax, h)
        rows.append({"surface": nm, "scope": "wetted surface",
                     "n_facets_total": int(len(wet)),
                     "n_facets_buried_excluded": int((~wet).sum()),
                     "cell_m": h, "n_facets": int(len(T)),
                     "area_m2": float(area.sum()),
                     "max_facet_edge_mm": float(lmax.max() * 1000.0),
                     "area_weighted_fail": a_share,
                     "count_weighted_fail": c_share,
                     "area_pass": 1.0 - a_share,
                     "verdict": "PASS" if (1.0 - a_share) >= GATE_AREA_FRACTION
                                else "GATE FAIL"})
        if rows[-1]["verdict"] != "PASS":
            fails.append(rows[-1]["surface"] + " (surface cell)")
        hb = box_cell.get(nm)
        if hb:
            bn = (["sailTeBox"] if nm == "sail"
                  else [k for k in boxes if k.startswith("finTeBox")])
            C = T.mean(axis=1)
            m = in_any_box(C, bn)
            if m.sum() >= 10:
                a2, c2 = shares(area[m], lmax[m], hb)
                rows.append({"surface": nm, "scope": "inside the TE box",
                             "cell_m": hb, "n_facets": int(m.sum()),
                             "area_m2": float(area[m].sum()),
                             "max_facet_edge_mm": float(lmax[m].max() * 1000.0),
                             "area_weighted_fail": a2,
                             "count_weighted_fail": c2,
                             "area_pass": 1.0 - a2,
                             "verdict": "PASS" if (1.0 - a2) >= GATE_AREA_FRACTION
                                        else "GATE FAIL"})
                if rows[-1]["verdict"] != "PASS":
                    fails.append(rows[-1]["surface"] + " (TE box cell)")

    # THE FIDELITY STATISTIC, reported beside the gate because the two disagree.
    Th = read_facets(os.path.join(a.geom, "hull.stl"))
    ah, _ = facet_stats(Th); Ch = Th.mean(axis=1)
    dev = chordal_deviation_hull(Ch, ah)
    hc = surf_cell["hull"]
    dev_summary = {"max_m": float(dev.max()), "p50_m": float(np.percentile(dev, 50)),
                   "p99_m": float(np.percentile(dev, 99)),
                   "hull_cell_m": hc,
                   "max_as_percent_of_a_cell": float(100 * dev.max() / hc),
                   "p50_as_percent_of_a_cell": float(100 * np.percentile(dev, 50) / hc)}

    w = max(len(r["surface"]) for r in rows)
    print(f"\n{'surface'.ljust(w)}  {'scope':<18} {'cell mm':>9} {'facets':>8} "
          f"{'max edge mm':>12} {'AREA fail %':>12} {'count fail %':>13}  verdict")
    for r in rows:
        print(f"{r['surface'].ljust(w)}  {r['scope']:<18} {r['cell_m']*1000:9.4f} "
              f"{r['n_facets']:8d} {r['max_facet_edge_mm']:12.5f} "
              f"{100*r['area_weighted_fail']:12.4f} "
              f"{100*r['count_weighted_fail']:13.4f}  {r['verdict']}")

    out = {"GATE_area_fraction_passing": GATE_AREA_FRACTION,
           "gate_fixed_before_first_run": True,
           "statistic": "fraction of surface AREA carried by facets whose LONGEST "
                        "EDGE exceeds the local mesh cell size",
           "why_area_not_count":
               "cosine clustering puts most FACETS where the surface is finely "
               "resolved and most AREA where it is not, so a count-weighted "
               "statistic is dominated by the facets that were never the problem",
           "rule3_plant": plant, "rows": rows, "n_gate_fail": len(fails),
           "gate_fail_surfaces": fails}
    with open(a.out, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nFIDELITY (hull chordal deviation from the analytic surface): "
          f"max {dev.max()*1e6:.1f} um = {100*dev.max()/hc:.2f} % of a cell; "
          f"median {np.percentile(dev,50)*1e6:.1f} um = "
          f"{100*np.percentile(dev,50)/hc:.3f} % of a cell")
    if fails:
        print(f"\nGATE FAIL on {len(fails)}: {fails}")
    else:
        print(f"\nAll surfaces PASS: >= {100*GATE_AREA_FRACTION:.1f} % of area on "
              "facets no larger than the local cell.")


if __name__ == "__main__":
    main()
