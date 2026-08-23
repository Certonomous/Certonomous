#!/usr/bin/env python3
"""R0 diagnostic — back out the comparator's IMPLIED front definition.

NOT-NORMATIVE, and it takes no gate verdict.  The normative home of the F7a
measurement definition is `f7a_contract.py` / `F7a_REGATE_SPEC.md` §2, and the
GATE (a): FAIL at +11.03% is untouched by anything in this file.

Purpose.  `F7a_REGATE_PREREGISTRATION.md` §5 item R0 asks, at 0 core-min, for
the front-extraction method behind the Fig. 7 simulation curve of Leakey,
Glenis & Hewett (arXiv:2108.08769), and says that "if unstated, contact-free
bound it by re-deriving their curve's implied threshold from our own field
data".  The paper does not state it (see the R0 outcome section appended to
`verification/campaign/F7a_REGATE_SPEC.md`).  This script executes the
fallback.

Question, narrowly.  Spec §3.1 measured our `res16_papermodel` case -- the
comparator's own physics (inviscid, sigma = 0, cAlpha = 0), on the
comparator's own mesh (240 x 20, dx = dy = a/16), in the comparator's own
domain (15a x 1.25a, all walls) -- as sitting +23.3% ahead of the comparator's
own published curve.  If that offset were a front-DEFINITION artifact, then
there would exist ONE front definition which, applied to our field, lands on
their curve at EVERY graded station.  A definition is a single fixed rule; it
cannot be re-chosen per station.  So the test is not "does some definition fit
station k" -- at a/16 the readings span tens of points and something always
fits -- but "is the implied definition the SAME at all six stations".

Positive control (rule 3, planted-zero principle: a reader not shown able to
see the answer is not evidence).  Before any back-out, this script re-derives
the already-published §3.1 column of Z_sim for this case under the §2
definition and refuses to continue unless it reproduces them.  Those published
values are 7.104, 8.157, 9.388, 10.714, 12.029, 14.235 at T = 3.90 ... 7.72.
A reader that cannot reproduce a number the repo already holds is not trusted
to produce one it does not.

Column grouping is at 6 decimal places, not §2.1's 8.  Reason, on the record:
spec §6.4 measured that 8 dp does not close the a/16 family at all, and that
6 dp closes every tracked case while moving no verdict and no number.  This is
a diagnostic on an a/16 case, so 6 dp is the only setting under which it can
be computed.  Docket G1c carries the re-pin.

Zero compute: reads tracked, already-written fields only.  Launches nothing.

Usage:  r0_implied_front_definition.py [out.json]
"""
import gzip
import json
import os
import re
import sys
from collections import defaultdict

A = 0.05715          # metres, exactly 2 1/4 in x 0.0254, §2.1
G = 9.81             # m/s^2, exactly, §2.3
HERE = os.path.dirname(os.path.abspath(__file__))
CASE = os.path.join(HERE, "F7a_R1", "res16_papermodel")
DIGITISED = os.path.join(HERE, "fig7_digitised_R1.json")

# §2.4 frozen reference table, first six = the graded stations.
REF = [(3.90, 6.00), (4.49, 7.00), (5.17, 8.00),
       (5.91, 9.00), (6.70, 10.00), (7.72, 11.00)]

# Spec §3.1, published: our res16_papermodel front under the §2 definition.
PUBLISHED_Z = [7.104, 8.157, 9.388, 10.714, 12.029, 14.235]
CONTROL_TOL = 0.02   # in Z units; digit-level agreement with the published table


def _open(path):
    if os.path.exists(path):
        return open(path)
    if os.path.exists(path + ".gz"):
        return gzip.open(path + ".gz", "rt")
    raise FileNotFoundError(path)


def _read_list(path, kind):
    txt = _open(path).read()
    m = re.search(
        r"internalField\s+nonuniform\s+List<%s>\s*\n(\d+)\n\(\n(.*?)\n\)\s*;" % kind,
        txt, re.S)
    if m is None:
        m2 = re.search(r"internalField\s+uniform\s+([-\d.eE+]+)\s*;", txt)
        if m2 is not None:
            return None, float(m2.group(1))
        raise ValueError("cannot parse %s" % path)
    n = int(m.group(1))
    body = m.group(2).split("\n")
    assert len(body) == n, (len(body), n, path)
    return body, None


def read_scalar(path, ncells=None):
    body, uni = _read_list(path, "scalar")
    if body is None:
        return [uni] * ncells
    return [float(x) for x in body]


def read_vector(path):
    body, _ = _read_list(path, "vector")
    return [tuple(float(v) for v in ln.strip().strip("()").split()) for ln in body]


def find_centres(case_dir):
    for d in sorted(os.listdir(case_dir)):
        p = os.path.join(case_dir, d, "C")
        if os.path.exists(p) or os.path.exists(p + ".gz"):
            return p
    raise SystemExit("no C field in %s" % case_dir)


def written_times(case_dir):
    ts = []
    for d in os.listdir(case_dir):
        try:
            t = float(d)
        except ValueError:
            continue
        if t <= 0:
            continue
        if os.path.exists(os.path.join(case_dir, d, "alpha.water")) or \
           os.path.exists(os.path.join(case_dir, d, "alpha.water.gz")):
            ts.append((t, d))
    return sorted(ts)


def build_grid(C, ndp=6):
    """Structured (col, row) index.  FAIL LOUD if the grid does not close."""
    xs = sorted({round(c[0], ndp) for c in C})
    ys = sorted({round(c[1], ndp) for c in C})
    nx, ny = len(xs), len(ys)
    if nx * ny != len(C):
        raise SystemExit("grid does not close at %d dp: %d cols x %d rows != %d cells"
                         % (ndp, nx, ny, len(C)))
    xi = {x: i for i, x in enumerate(xs)}
    yi = {y: j for j, y in enumerate(ys)}
    colcount = defaultdict(int)
    rowcount = defaultdict(int)
    idx = []
    for c in C:
        i, j = xi[round(c[0], ndp)], yi[round(c[1], ndp)]
        idx.append((i, j))
        colcount[i] += 1
        rowcount[j] += 1
    if set(colcount.values()) != {ny} or set(rowcount.values()) != {nx}:
        raise SystemExit("ragged structured grid at %d dp" % ndp)
    # dy from the UNROUNDED centres: `ys` carries +-1e-6 of grouping round-off,
    # which would show as a spurious non-uniformity at this mesh.
    yrow = [0.0] * ny
    for k, (i, j) in enumerate(idx):
        yrow[j] = C[k][1]
    dys = [yrow[k + 1] - yrow[k] for k in range(ny - 1)]
    # Tolerance 1e-4 relative: the `C` field is written at 8 significant
    # figures, so a uniform mesh reads back with ~1e-6 relative scatter.  Any
    # genuinely graded mesh carries an expansion ratio of at least a percent,
    # so this still refuses one.
    if max(dys) - min(dys) > 1e-4 * max(dys):
        raise SystemExit("mesh not uniform in y: %r" % sorted(set(dys)))
    return xs, ys, idx, nx, ny, sum(dys) / len(dys)


def cross_down(xs, vals, level):
    """Furthest x at which vals(x) crosses DOWN through level; linear interp.

    Scans from the far wall toward x = 0 and returns the first crossing met,
    which is by construction the furthest downstream one (§2.2)."""
    for i in range(len(xs) - 1, 0, -1):
        if vals[i] < level <= vals[i - 1]:
            v0, v1 = vals[i - 1], vals[i]
            if v0 == v1:
                return xs[i - 1]
            f = (v0 - level) / (v0 - v1)
            return xs[i - 1] + f * (xs[i] - xs[i - 1])
    return None


def interp_series(series, t):
    """Linear interpolation of a (t, value) series at t; None if not bracketed."""
    for k in range(len(series) - 1):
        t0, v0 = series[k]
        t1, v1 = series[k + 1]
        if t0 <= t <= t1:
            if t1 == t0:
                return v0
            return v0 + (v1 - v0) * (t - t0) / (t1 - t0)
    return None


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else None
    if not os.path.isdir(CASE):
        raise SystemExit("case not on disk: %s" % CASE)

    C = read_vector(find_centres(CASE))
    xs, ys, idx, nx, ny, dy = build_grid(C, 6)
    ncells = len(C)

    times = written_times(CASE)
    if not times:
        raise SystemExit("no written alpha.water times in %s" % CASE)

    # ---- per-time fields -------------------------------------------------
    # h(x)  = depth integral, §2.1/§2.2 (our definition)
    # a0(x) = alpha in the floor-adjacent row (row 0), the OLD line-probe family
    # amax  = column-max alpha, used only for reporting the smear extent
    per_time = []
    for t, d in times:
        alpha = read_scalar(os.path.join(CASE, d, "alpha.water"), ncells)
        h = [0.0] * nx
        rows = [[0.0] * nx for _ in range(ny)]
        for k, (i, j) in enumerate(idx):
            h[i] += alpha[k] * dy
            rows[j][i] = alpha[k]
        T = t * (G / A) ** 0.5
        per_time.append({"t": t, "T": T, "h": h, "rows": rows})

    Zx = [x / A for x in xs]

    def z_of(level, kind, row=0):
        """(T, Z) series under one front definition."""
        ser = []
        for rec in per_time:
            if kind == "h":
                vals = rec["h"]
                lv = level * A
            elif kind == "alpha":
                vals = rec["rows"][row]
                lv = level
            else:
                raise ValueError(kind)
            xf = cross_down(xs, vals, lv)
            if xf is None:
                continue
            ser.append((rec["T"], xf / A))
        # §2.2 monotonicity guard: stop at the first retreat > 0.05 in Z
        guarded = []
        for T, Z in ser:
            if guarded and Z < guarded[-1][1] - 0.05:
                break
            guarded.append((T, Z))
        return guarded

    # ---- POSITIVE CONTROL ------------------------------------------------
    # Reproduce the published §3.1 Z_sim column before trusting any back-out.
    base = z_of(0.02, "h")
    control = []
    for (Tref, _), zpub in zip(REF, PUBLISHED_Z):
        zs = interp_series(base, Tref)
        control.append({"T": Tref, "published": zpub, "reproduced": zs,
                        "delta": None if zs is None else zs - zpub})
    bad = [c for c in control
           if c["reproduced"] is None or abs(c["delta"]) > CONTROL_TOL]
    control_ok = not bad
    if not control_ok:
        sys.stderr.write(
            "POSITIVE CONTROL FAILED -- this reader does not reproduce the "
            "published res16_papermodel front under the §2 definition. "
            "Refusing to report an implied threshold.\n"
            + json.dumps(control, indent=1) + "\n")
        if out_path:
            json.dump({"control_ok": False, "control": control},
                      open(out_path, "w"), indent=1)
        return 2

    # ---- the comparator's own curve, digitised ---------------------------
    green = sorted(json.load(open(DIGITISED))["green"])
    z_comp = [interp_series(green, Tref) for Tref, _ in REF]

    # ---- back-out 1: implied depth-integral level h*/a -------------------
    # Front position falls monotonically as h* rises, so scan h*/a upward and
    # take the first level whose Z(T) sits at or below the comparator's Z.
    levels = [0.0025 * k for k in range(1, 501)]      # 0.0025a .. 1.25a
    implied_h = []
    for (Tref, _), zc in zip(REF, z_comp):
        hit = None
        for lv in levels:
            zs = interp_series(z_of(lv, "h"), Tref)
            if zs is None:
                continue
            if zs <= zc:
                hit = lv
                break
        implied_h.append(hit)

    # ---- back-out 2: implied floor-row alpha threshold -------------------
    alphas = [0.005 * k for k in range(1, 200)]        # 0.005 .. 0.995
    implied_a = []
    for (Tref, _), zc in zip(REF, z_comp):
        hit = None
        for av in alphas:
            zs = interp_series(z_of(av, "alpha", 0), Tref)
            if zs is None:
                continue
            if zs <= zc:
                hit = av
                break
        implied_a.append(hit)

    # ---- back-out 3: implied row index at alpha = 0.5 --------------------
    implied_row = []
    for (Tref, _), zc in zip(REF, z_comp):
        hit = None
        for r in range(ny):
            zs = interp_series(z_of(0.5, "alpha", r), Tref)
            if zs is None:
                continue
            if zs <= zc:
                hit = r
                break
        implied_row.append(hit)

    # ---- the decisive test: can ONE fixed definition close the gap? ------
    # A definition is a single rule, not a per-station knob.  For each fixed
    # candidate definition, report the residual deviation of our front from
    # the comparator's curve at every graded station.  If some candidate
    # drives all six residuals to ~0, the offset IS a definition artifact.
    fixed = []
    cands = ([("h", lv, 0) for lv in (0.02, 0.03, 0.04, 0.05, 0.0625, 0.08, 0.10, 0.125)] +
             [("alpha", av, 0) for av in (0.5, 0.6, 0.65, 0.7, 0.785, 0.9, 0.95)] +
             [("alpha", 0.5, r) for r in range(1, min(4, ny))])
    for kind, lv, row in cands:
        ser = z_of(lv, kind, row)
        devs = []
        for (Tref, _), zc in zip(REF, z_comp):
            zs = interp_series(ser, Tref)
            devs.append(None if (zs is None or zc is None)
                        else 100.0 * (zs - zc) / zc)
        got = [d for d in devs if d is not None]
        fixed.append({
            "definition": ("h*=%.4fa" % lv) if kind == "h"
                          else ("alpha=%.3f on row %d" % (lv, row)),
            "kind": kind, "level": lv, "row": row,
            "dev_vs_comparator_pct": devs,
            "n_stations": len(got),
            "mean_pct": None if not got else sum(got) / len(got),
            "max_abs_pct": None if not got else max(abs(d) for d in got),
            "spread_pct": None if not got else max(got) - min(got),
        })

    # ---- how wide is the toe, in cells?  the physical bound on any -------
    # definition-induced offset at a given time.
    dx_a = (xs[1] - xs[0]) / A
    toe_width = []
    for Tref, _ in REF:
        # nearest written time to the reference T
        rec = min(per_time, key=lambda r: abs(r["T"] - Tref))
        x95 = cross_down(xs, rec["h"], 0.95 * max(rec["h"]))
        x005 = cross_down(xs, rec["h"], 0.005 * A)
        toe_width.append({
            "T": Tref, "t_used": rec["t"],
            "x_h995_over_a": None if x95 is None else x95 / A,
            "x_h0005a_over_a": None if x005 is None else x005 / A,
            "cells": None if (x95 is None or x005 is None)
                     else (x005 - x95) / (xs[1] - xs[0]),
        })

    res = {
        "case": os.path.relpath(CASE, HERE),
        "mesh": {"nx": nx, "ny": ny, "ncells": ncells,
                 "dy_m": dy, "dx_over_a": dx_a, "column_rounding_dp": 6},
        "control_ok": control_ok,
        "control": control,
        "stations": [
            {"T": Tref, "Z_expt": Zref,
             "Z_ours_spec2": interp_series(base, Tref),
             "Z_comparator": zc,
             "gap_Z": None if zc is None else interp_series(base, Tref) - zc,
             "gap_pct_of_comparator": None if zc is None else
                 100.0 * (interp_series(base, Tref) - zc) / zc,
             "gap_in_their_cells": None if zc is None else
                 (interp_series(base, Tref) - zc) / dx_a,
             "implied_hstar_over_a": ih,
             "implied_row0_alpha": ia,
             "implied_row_index_at_alpha0p5": ir}
            for (Tref, Zref), zc, ih, ia, ir
            in zip(REF, z_comp, implied_h, implied_a, implied_row)
        ],
        "toe_width": toe_width,
        "fixed_definition_sweep": fixed,
    }

    for s in res["stations"]:
        print("T=%.2f  Z_expt=%5.2f  Z_ours=%7.3f  Z_comp=%7.3f  gap=%6.3f "
              "(%+6.2f%%, %5.1f of their cells)  implied h*/a=%s  "
              "implied row0 alpha=%s  implied row=%s"
              % (s["T"], s["Z_expt"], s["Z_ours_spec2"], s["Z_comparator"],
                 s["gap_Z"], s["gap_pct_of_comparator"], s["gap_in_their_cells"],
                 s["implied_hstar_over_a"], s["implied_row0_alpha"],
                 s["implied_row_index_at_alpha0p5"]))
    print("\n-- ONE FIXED DEFINITION vs the comparator's curve, all 6 stations --")
    for f in res["fixed_definition_sweep"]:
        print("%-22s n=%d  mean=%s  max|d|=%s  spread=%s  per-station=%s"
              % (f["definition"], f["n_stations"],
                 "n/a" if f["mean_pct"] is None else "%+7.2f%%" % f["mean_pct"],
                 "n/a" if f["max_abs_pct"] is None else "%6.2f%%" % f["max_abs_pct"],
                 "n/a" if f["spread_pct"] is None else "%6.2f pts" % f["spread_pct"],
                 ["%+.1f" % d if d is not None else "--"
                  for d in f["dev_vs_comparator_pct"]]))
    print()
    for w in res["toe_width"]:
        print("T=%.2f toe from h=0.995*hmax to h=0.005a spans %s cells"
              % (w["T"], None if w["cells"] is None else "%.1f" % w["cells"]))

    if out_path:
        json.dump(res, open(out_path, "w"), indent=1)
        print("\nwrote %s" % out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
