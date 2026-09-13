#!/usr/bin/env python3
"""CRM WING-BODY (D8G) -- Cp AT THE NINE NTF PRESSURE ROWS.  THE EXTRACTION PATH.

Pairs with `cases/CRM_wingbody/grade_crm_wb_lts.py` and serves §5.3 of
`verification/campaign/CRM_WINGBODY_DPW6_ACT_PREREGISTRATION.md`.  It produces the
CFD-vs-experiment chordwise Cp comparison at the nine span stations and the shock
position on each, and it refuses rather than degrade.

THE NINE ROWS, from the CRM site's Model Description and confirmed at prereg §2.1:
    eta = 0.131 0.201 0.283 0.397 0.502 0.603 0.727 0.846 0.950
    labelled A..I in the NTF Test 197 data, in that order.

--------------------------------------------------------------------------------
TWO TRAPS THIS FILE EXISTS TO NOT REPEAT.  Both are stated as controls, not as prose.

(a) COLUMN INDEX.  In this lab `Cd(f)` was read as `Cd` with `awk '{print $3}'`, drag
    was reported halved, and a mechanism was invented for it.  The NTF CSV is worse
    than the coefficient file: its 567 columns include `XOCA1..XOCA40` (row A upper)
    AND `XOCAL1..XOCAL12` (row A LOWER), so a reader that matches `XOCA` by prefix,
    or counts columns, silently mixes the two surfaces of the same row.  EVERY column
    here is located by an ANCHORED regex against the file's own header line, the upper
    and lower sets are separated by that regex, and P-1 shuffles the header and
    requires the same numbers back.

(b) RESAMPLING INTERVALS.  An argmax over unevenly spaced samples picks the WIDEST
    INTERVAL, not the steepest feature.  THE NTF TAPS ARE NOT UNIFORM -- measured on
    row A of run t197R51t: the spacing ratio max/min is reported by this file on every
    run, and it is never assumed.  The shock locator therefore differentiates with the
    ACTUAL spacing (a three-point unequal-interval derivative), and P-2 proves the
    point with numbers: on the same planted data the naive per-index difference picks
    the wrong x/c and this file's locator picks the planted one.

--------------------------------------------------------------------------------
REFUSALS (exit 2, never a degraded answer)
  - no experimental row matches the registered condition within the registered
    tolerance (it does NOT fall back to "the nearest point")
  - a row's upper and lower tap sets cannot be separated by name
  - a planted control is not read back
  - fewer than MIN_TAPS usable taps on a row

WHAT IS NOT DECIDED HERE.  §5.3 registers the GATE BAND as "the DPW-6 participant
scatter on Cp at each row", with a stated fallback of +/-0.05 away from the shock and
shock position +/-0.03 c LABELLED A LAB JUDGEMENT.  This file computes the deviations
and the shock positions; it applies a band only when one is handed to it, and reports
`BLOCKED` otherwise.  It also does NOT choose the experimental reference row's alpha
rule: the NTF polar has no point at exactly alpha = 2.75 (nearest WB/trip-on/tail-off
point at M 0.85, Re 5e6 is alpha = 2.6754), and the selection or interpolation rule is
NOT in the frozen pre-registration text.  This file states that gap and refuses to
invent one.

Author: cfd lab-lane, 2026-09-13.
"""

import argparse
import csv
import glob
import json
import math
import os
import re
import sys
import tempfile

if not __debug__:
    sys.stderr.write("REFUSED: must not run under python3 -O; the asserts are the point.\n")
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

# ------------------------------------------------------------ frozen constants --
PREREG = "verification/campaign/CRM_WINGBODY_DPW6_ACT_PREREGISTRATION.md"

RHO_INF = 0.04503298815          # §4
U_INF   = 300.0189024            # §4
P_INF   = 4007.394649            # §4
Q_INF   = 0.5 * RHO_INF * U_INF ** 2

SEMISPAN = 29.38145              # m, §4: b/2 = 58.7629/2
ROWS = (("A", 0.131), ("B", 0.201), ("C", 0.283), ("D", 0.397), ("E", 0.502),
        ("F", 0.603), ("G", 0.727), ("H", 0.846), ("I", 0.950))

# The registered condition, §0/§1.1.  Tolerances are the reader's admission window,
# NOT a gate: a row outside them is a REFUSAL, not a wider comparison.
COND = {"MACH": (0.85, 0.005), "CREYN": (5.0, 0.35), "ALPHA": (2.75, 0.10)}
COND_EXACT = {"CONFIG": 1.0,     # 1 = Wing/Body.  2 = WBPN and 3 = WBT are NOT this case.
              "CONFT": 99.0,     # tail off
              "CONFTS": 1.0}     # transition strip ON (the model was tripped)

MIN_TAPS = 8                     # a row with fewer usable taps is refused
DATA_ERROR_BAR = 0.0026          # §5.3: the ESP module's own uncertainty. IT DOES NOT GATE.

PLANT_CP   = -1.234              # house constant, sign-flipped so a magnitude reader fails
PLANT_XOC  = 0.4321
PLANT_DECOY_CP = -5.678

VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")


def refuse(msg):
    sys.stderr.write("REFUSED: " + msg + "\n")
    sys.exit(2)


# ================================================= 1. THE EXPERIMENTAL READER ===
# Anchored regexes.  `XOCA1` and `XOCAL1` differ by one character and belong to
# DIFFERENT SURFACES of the same row; a prefix match merges them.

def _row_patterns(letter):
    return (re.compile(r"^XOC%s(\d+)$" % letter),      # upper x/c
            re.compile(r"^CP%s(\d+)$" % letter),       # upper Cp
            re.compile(r"^XOC%sL(\d+)$" % letter),     # lower x/c
            re.compile(r"^CP%sL(\d+)$" % letter))      # lower Cp


def read_experiment(csv_dir, cond=None, cond_exact=None, quiet=False):
    """Select the ONE row matching the registered condition and return its nine rows.

    Every column is found BY NAME in the file's own header.  No row within tolerance
    means a REFUSAL -- this reader does not fall back to the nearest point, because
    'the nearest point' is how a comparison at the wrong condition gets published."""
    cond = cond or COND
    cond_exact = cond_exact if cond_exact is not None else COND_EXACT
    files = sorted(glob.glob(os.path.join(csv_dir, "*.csv")))
    if not files:
        refuse(f"no CSV files under {csv_dir}")
    hits = []
    for f in files:
        with open(f, newline="") as fh:
            rdr = csv.DictReader(fh)
            if rdr.fieldnames is None:
                continue
            names = [n.strip() for n in rdr.fieldnames]
            for raw in rdr:
                rec = {k.strip(): v for k, v in raw.items() if k}
                try:
                    ok = all(abs(float(rec[k]) - v) <= tol for k, (v, tol) in cond.items())
                    ok = ok and all(abs(float(rec[k]) - v) < 1e-9
                                    for k, v in cond_exact.items())
                except (KeyError, TypeError, ValueError):
                    continue
                if ok:
                    hits.append((f, names, rec))
    if not hits:
        refuse(f"no experimental row in {csv_dir} matches the registered condition "
               f"{cond} with {cond_exact}. This reader does NOT fall back to the "
               f"nearest point: a comparison at the wrong condition is worse than none.")
    if len(hits) > 1 and not quiet:
        sys.stderr.write(f"NOTE: {len(hits)} experimental rows match; the one with the "
                         "smallest ALPHA residual is used and all are listed.\n")
    hits.sort(key=lambda h: abs(float(h[2]["ALPHA"]) - cond["ALPHA"][0]))
    path, names, rec = hits[0]
    out = {"source_file": path, "n_matching_rows": len(hits),
           "condition_registered": {k: v[0] for k, v in cond.items()},
           "condition_tolerance": {k: v[1] for k, v in cond.items()},
           "condition_exact": cond_exact,
           "selected": {k: _f(rec.get(k)) for k in
                        ("TEST", "RUN", "POINT", "ALPHA", "MACH", "CREYN", "CONFIG",
                         "CONFTS", "CONFT", "CL", "CD", "CM", "CMS")},
           "residuals": {k: _f(rec.get(k)) - v[0] for k, v in cond.items()
                         if _f(rec.get(k)) is not None},
           "rows": {}}
    for letter, eta in ROWS:
        xu_re, cu_re, xl_re, cl_re = _row_patterns(letter)
        surf = {}
        for tag, (xre, cre) in (("upper", (xu_re, cu_re)), ("lower", (xl_re, cl_re))):
            xs = {int(m.group(1)): n for n in names for m in [xre.fullmatch(n)] if m}
            cs = {int(m.group(1)): n for n in names for m in [cre.fullmatch(n)] if m}
            idx = sorted(set(xs) & set(cs))
            pts = []
            for i in idx:
                x, c = _f(rec.get(xs[i])), _f(rec.get(cs[i]))
                if x is None or c is None:
                    continue
                if not (math.isfinite(x) and math.isfinite(c)):
                    continue
                if x < -0.01 or x > 1.05 or abs(c) > 20.0:   # dead tap sentinels
                    continue
                pts.append({"tap": i, "x_over_c": x, "Cp": c,
                            "column_xoc": xs[i], "column_cp": cs[i]})
            pts.sort(key=lambda p: p["x_over_c"])
            surf[tag] = pts
        if surf["upper"] and surf["lower"]:
            shared = set(p["column_xoc"] for p in surf["upper"]) & \
                     set(p["column_xoc"] for p in surf["lower"])
            if shared:
                refuse(f"row {letter}: the upper and lower tap sets share the columns "
                       f"{sorted(shared)[:5]} -- they have not been separated by name "
                       "and the two surfaces of one row would be mixed")
        out["rows"][letter] = {"eta": eta,
                               "n_upper": len(surf["upper"]), "n_lower": len(surf["lower"]),
                               "upper": surf["upper"], "lower": surf["lower"],
                               "spacing_upper": spacing_report([p["x_over_c"]
                                                                for p in surf["upper"]]),
                               "spacing_lower": spacing_report([p["x_over_c"]
                                                                for p in surf["lower"]])}
    return out


def _f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


# ==================================================== 2. SPACING AND SHOCKS =====

def spacing_report(xs):
    """IS THE SAMPLING UNIFORM?  Stated, never assumed.  Trap (b) begins here."""
    if len(xs) < 3:
        return {"n": len(xs), "uniform": None,
                "note": "fewer than 3 samples; uniformity not established"}
    d = [xs[i + 1] - xs[i] for i in range(len(xs) - 1)]
    d = [x for x in d if x > 0]
    if not d:
        return {"n": len(xs), "uniform": None, "note": "no positive intervals"}
    lo, hi = min(d), max(d)
    ratio = hi / lo
    return {"n": len(xs), "min_interval": lo, "max_interval": hi,
            "max_over_min": ratio,
            "uniform": ratio <= 1.05,
            "note": ("UNIFORM within 5%" if ratio <= 1.05 else
                     f"NON-UNIFORM: the widest interval is {ratio:.2f}x the narrowest. "
                     "A per-index argmax on this abscissa returns the widest interval, "
                     "not the steepest feature.")}


SHOCK_WINDOW = (0.05, 0.98)      # UNREGISTERED instrument setting -- see below
SHOCK_TOL_C  = 0.03              # §5.3's fallback shock-position tolerance, +/-0.03 c


def shock_position(xs, cps, window=SHOCK_WINDOW, tol=SHOCK_TOL_C):
    """Steepest ADVERSE chordwise Cp gradient, differentiated on the ACTUAL abscissa,
    WITH A RESOLVABILITY GATE.

    The derivative is a three-point unequal-interval (Fornberg) formula, so the
    abscissa's real spacing is used and trap (b) cannot bite through the arithmetic.
    The SIGNED derivative is maximised, not its magnitude: |dCp/dx| returns the
    leading-edge suction peak on every row and calls it a shock.

    🔴 THE GATE, AND WHY IT IS HERE RATHER THAN IN A CAVEAT.  Measured on NTF Test 197
    run 51 point 563 (the WB / trip-on / tail-off row nearest the registered
    condition), this tool's own spacing report:

        row  eta     taps  widest interval   located peak (window 0.05-0.98)
        D    0.397    12      0.60 c          0.70   <- 0.60 c gap from x/c 0.10 to 0.70
        E    0.502    12      0.30 c          0.50
        F    0.603    11      0.20 c          0.70
        G    0.727    15      0.10 c          0.10   <- the LE recovery, not a shock
        H    0.846    15      0.10 c          0.10   <- the LE recovery, not a shock

    Excluding the leading edge does not repair it: at window (0.15, 0.98) rows D, G and
    H all relocate to x/c = 0.93, which is the TRAILING-EDGE pressure recovery.  NO
    CHOICE OF WINDOW MAKES A DERIVATIVE ARGMAX A SHOCK LOCATOR ON THIS ABSCISSA, and
    choosing the window that makes the answer look right is fitting the instrument to
    the answer.

    The honest reading is that the TAP LAYOUT CANNOT RESOLVE A SHOCK POSITION to the
    +/-0.03 c that §5.3's fallback would grade it against: row D's aft gap alone is
    0.60 c, twenty times that tolerance.  So a located peak whose own local interval
    exceeds 2*tol is returned as `NOT A RESULT` WITH THE NUMBER, never as a position.
    The Cp DEVIATION channel is unaffected -- it is evaluated tap by tap and needs no
    interpolation of the experiment.

    `window` is an INSTRUMENT SETTING AND IT IS NOT REGISTERED in the pre-registration.
    It is reported on every call so that a reader can see what it was, and no shock
    position may be graded until it is frozen by addendum."""
    pts = sorted(zip(xs, cps))
    pts = [(x, c) for x, c in pts if window[0] <= x <= window[1]]
    base = {"window_UNREGISTERED_INSTRUMENT_SETTING": list(window),
            "tolerance_c": tol,
            "method": "three-point unequal-interval (Fornberg) derivative on the "
                      "actual abscissa; SIGNED maximum, not |dCp/dx|"}
    if len(pts) < 3:
        base.update({"x_over_c": None, "dCp_dx": None, "verdict": "NOT A RESULT",
                     "reason": f"only {len(pts)} taps inside {window}"})
        return base
    peaks = []
    for i in range(1, len(pts) - 1):
        x0, y0 = pts[i - 1]
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        h0, h1 = x1 - x0, x2 - x1
        if h0 <= 0 or h1 <= 0:
            continue
        d = (-h1 / (h0 * (h0 + h1))) * y0 + ((h1 - h0) / (h0 * h1)) * y1 \
            + (h0 / (h1 * (h0 + h1))) * y2
        peaks.append({"x_over_c": x1, "dCp_dx": d, "local_interval_c": max(h0, h1)})
    if not peaks:
        base.update({"x_over_c": None, "dCp_dx": None, "verdict": "NOT A RESULT",
                     "reason": "no interior point with two positive intervals"})
        return base
    peaks.sort(key=lambda q: -q["dCp_dx"])
    top = peaks[0]
    base.update({"x_over_c": top["x_over_c"], "dCp_dx": top["dCp_dx"],
                 "local_interval_c": top["local_interval_c"],
                 "n_taps_in_window": len(pts),
                 "ranked_peaks": peaks[:3]})
    if top["local_interval_c"] > 2.0 * tol:
        base["verdict"] = "NOT A RESULT"
        base["reason"] = (f"the located peak sits on a tap interval of "
                          f"{top['local_interval_c']:.3f} c, which is "
                          f"{top['local_interval_c'] / tol:.1f}x the +/-{tol} c tolerance "
                          "this position would be graded against. The abscissa cannot "
                          "resolve a shock position here; an argmax over it returns the "
                          "widest interval, not the steepest feature.")
    else:
        base["verdict"] = "GATE REACHED"
        base["reason"] = ("the located peak's own tap interval is inside twice the "
                          "grading tolerance, so the position is resolvable")
    return base


def shock_position_NAIVE_INDEX(xs, cps, window=(0.05, 0.98)):
    """THE TRAP, KEPT AS A CONTROL AND NEVER USED FOR A RESULT.

    argmax over per-index differences Cp[i+1]-Cp[i].  On a non-uniform abscissa this
    is an argmax over `interval width x local slope` and it returns the widest
    interval.  P-2 drives both this and `shock_position` over the same planted data
    and requires them to DISAGREE -- if they ever agreed on the fixture, the control
    would prove nothing."""
    pts = sorted(zip(xs, cps))
    pts = [(x, c) for x, c in pts if window[0] <= x <= window[1]]
    if len(pts) < 2:
        return {"x_over_c": None}
    best_x, best_d = None, -math.inf
    for i in range(len(pts) - 1):
        d = pts[i + 1][1] - pts[i][1]
        if d > best_d:
            best_x, best_d = pts[i + 1][0], d
    return {"x_over_c": best_x, "dCp_per_index": best_d}


# ============================================== 3. THE CFD SURFACE Cp READER ====
# Input is the raw sampled-surface file OpenFOAM's `surfaces` functionObject writes:
#   `postProcessing/<name>/<time>/p_<patch>.raw`, a `# x  y  z  p` table.
# The dictionary that produces it is written by --emit-sample-dict below; nothing here
# launches anything.

def read_surface_raw(path):
    """Read `# x y z <field>` raw sample output, BY COLUMN NAME from its own header."""
    xs, ys, zs, vs = [], [], [], []
    names = None
    with open(path) as f:
        for line in f:
            if line.startswith("#"):
                toks = [t for t in re.split(r"[\s]+", line[1:].strip()) if t]
                if len(toks) >= 4 and toks[0].lower() in ("x", "x0"):
                    names = [t.lower() for t in toks]
                continue
            parts = [p for p in re.split(r"[\s]+", line.strip()) if p]
            if len(parts) < 4:
                continue
            try:
                vals = [float(p) for p in parts]
            except ValueError:
                continue
            if names is not None and len(names) == len(vals):
                d = dict(zip(names, vals))
                xs.append(d["x"]); ys.append(d["y"]); zs.append(d["z"])
                vs.append(d[[n for n in names if n not in ("x", "y", "z")][0]])
            else:
                xs.append(vals[0]); ys.append(vals[1]); zs.append(vals[2]); vs.append(vals[3])
    if not xs:
        refuse(f"{path}: no data rows")
    return {"x": xs, "y": ys, "z": zs, "v": vs, "header_names": names, "n": len(xs)}


def cfd_sections(raw, etas=None, band_eta=0.004, semispan=SEMISPAN):
    """Cut the sampled wing surface at the nine span stations and return chordwise Cp.

    Cp = (p - p_inf) / q_inf, with p ABSOLUTE in Pa -- rhoPimpleFoam's `p` is absolute
    pressure, not the kinematic p/rho of the incompressible solvers.  Q_INF is checked
    against an externally computed literal in P-4.

    The span coordinate is y (the model's span axis; §4's moment reference and the
    forces dict both put the pitch axis on y).  eta = y / semispan."""
    etas = etas or [e for _, e in ROWS]
    out = {}
    for (letter, eta) in ROWS:
        y_t = eta * semispan
        sel = [i for i in range(raw["n"]) if abs(raw["y"][i] - y_t) <= band_eta * semispan]
        if not sel:
            out[letter] = {"eta": eta, "n": 0,
                           "reason": f"no sampled face within {band_eta} eta of y={y_t:.4f}"}
            continue
        xs = [raw["x"][i] for i in sel]
        x0, x1 = min(xs), max(xs)
        chord = x1 - x0
        pts = []
        for i in sel:
            if chord <= 0:
                continue
            pts.append({"x_over_c": (raw["x"][i] - x0) / chord,
                        "Cp": (raw["v"][i] - P_INF) / Q_INF,
                        "z": raw["z"][i]})
        pts.sort(key=lambda p: p["x_over_c"])
        out[letter] = {"eta": eta, "n": len(pts), "y_target": y_t,
                       "x_le": x0, "x_te": x1, "chord": chord, "points": pts,
                       "spacing": spacing_report([p["x_over_c"] for p in pts])}
    return out


SAMPLE_DICT = """\
// CRM-WB D8G -- Cp at the nine NTF pressure rows.  Written by
// cases/CRM_wingbody/tools/extract_cp_rows.py --emit-sample-dict.
// Run AFTER the solve, never during it:
//     mpirun -np 32 postProcess -func wingSurface -latestTime -parallel
// It produces postProcessing/wingSurface/<time>/p_wing.raw, which this tool reads.
wingSurface
{
    type            surfaces;
    libs            (sampling);
    writeControl    onEnd;
    surfaceFormat   raw;
    fields          (p);
    surfaces
    {
        wing { type patch; patches (wing); interpolate false; }
        body { type patch; patches (body); interpolate false; }
    }
}
"""

# The one-line instrumentation gap this tool found in the staged case, emitted so the
# supervisor can register it rather than discover it after the run:
FIELD_MINMAX_DICT = """\
// CRM-WB D8G -- A15.7 L5 asks for max|U| READ FROM THE FIELD.  The staged controlDict
// writes no such channel, so L5's U clause is only readable by re-reading the written
// fields (which grade_crm_wb_lts.py does, at endTime only).  This object makes it
// readable PER TIME STEP, at negligible cost, so an L5 excursion is dated.
fieldMinMax
{
    type            fieldMinMax;
    libs            (fieldFunctionObjects);
    writeControl    timeStep;
    writeInterval   1;
    mode            magnitude;
    fields          (U p rho T);
}
"""


# ==================================================== 4. THE COMPARISON =========

def compare(exp, cfd, band=None):
    """Deviation CFD-minus-experiment at every experimental tap, by interpolating the
    CFD section onto the EXPERIMENTAL abscissa -- never the other way round, because
    the experimental taps are the measurement and resampling them invents data."""
    out = {"band": band, "rows": {},
           "data_error_bar_NOT_A_GATE": DATA_ERROR_BAR,
           "note": ("Cp deviations are quoted at the experimental tap locations. The "
                    "+/-0.0026 ESP uncertainty is drawn and reported; §5.3 says it does "
                    "NOT gate.")}
    for letter, eta in ROWS:
        e = exp["rows"].get(letter, {})
        c = cfd.get(letter, {})
        row = {"eta": eta, "n_exp_upper": e.get("n_upper", 0),
               "n_cfd": c.get("n", 0),
               "exp_spacing_upper": e.get("spacing_upper")}
        eu = e.get("upper") or []
        if len(eu) < MIN_TAPS:
            row["verdict"] = "NOT A RESULT"
            row["reason"] = f"only {len(eu)} usable upper taps, need {MIN_TAPS}"
            out["rows"][letter] = row
            continue
        ex = [p["x_over_c"] for p in eu]
        ec = [p["Cp"] for p in eu]
        row["exp_shock"] = shock_position(ex, ec)
        row["exp_shock_NAIVE_INDEX_for_contrast"] = shock_position_NAIVE_INDEX(ex, ec)
        if not c.get("points"):
            row["verdict"] = "PENDING"
            row["reason"] = ("no CFD section: the sampled wing surface has not been "
                             "produced yet (see --emit-sample-dict)")
            out["rows"][letter] = row
            continue
        cx = [p["x_over_c"] for p in c["points"]]
        cc = [p["Cp"] for p in c["points"]]
        row["cfd_spacing"] = c.get("spacing")
        row["cfd_shock"] = shock_position(cx, cc)
        devs = []
        for x, y in zip(ex, ec):
            yi = _interp(cx, cc, x)
            if yi is not None:
                devs.append({"x_over_c": x, "exp": y, "cfd": yi, "dev": yi - y})
        row["n_compared"] = len(devs)
        row["max_abs_dev"] = max((abs(d["dev"]) for d in devs), default=None)
        row["rms_dev"] = (math.sqrt(sum(d["dev"] ** 2 for d in devs) / len(devs))
                          if devs else None)
        row["deviations"] = devs
        if band is None:
            row["verdict"] = "BLOCKED"
            row["reason"] = ("§5.3's gate band is the DPW-6 participant scatter on Cp and "
                             "no such number has been registered for this act; the "
                             "+/-0.0026 ESP error bar is NOT the gate and is not used as "
                             "one here")
        else:
            bad = [d for d in devs if abs(d["dev"]) > band]
            row["n_outside_band"] = len(bad)
            row["verdict"] = "PASS" if not bad else "GATE FAIL"
        out["rows"][letter] = row
    return out


def _interp(xs, ys, x):
    """Linear interpolation, refusing to EXTRAPOLATE.  An extrapolated Cp beyond the
    sampled chord is a number this file will not produce."""
    if not xs or x < xs[0] or x > xs[-1]:
        return None
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            if xs[i + 1] == xs[i]:
                return ys[i]
            t = (x - xs[i]) / (xs[i + 1] - xs[i])
            return ys[i] + t * (ys[i + 1] - ys[i])
    return ys[-1]


# ================================================================ 5. PLANTS =====

def _synth_csv(path, extra=None, shuffle=False, plant=None):
    """A synthetic NTF-shaped CSV: the registered condition, an XOCA/CPA upper set on a
    DELIBERATELY NON-UNIFORM abscissa, and an XOCAL/CPAL lower set carrying a DECOY in
    every Cp.  A prefix reader picks up the decoys."""
    cols = {"TEST": 197.0, "RUN": 51.0, "POINT": 1.0, "ALPHA": 2.75, "MACH": 0.85,
            "CREYN": 5.0, "CONFIG": 1.0, "CONFTS": 1.0, "CONFT": 99.0,
            "CL": 0.4887, "CD": 0.02407, "CM": -0.06341}
    # non-uniform: fine near the LE, coarse aft -- the real tap layout's shape
    xs = [0.0, 0.005, 0.01, 0.02, 0.035, 0.05, 0.08, 0.12, 0.18, 0.25, 0.33,
          0.4321, 0.55, 0.70, 0.85, 0.95]
    for i, x in enumerate(xs, 1):
        cols["XOCA%d" % i] = x
        cols["CPA%d" % i] = plant(x) if plant else -0.3
    for i, x in enumerate([0.02, 0.2, 0.5, 0.8], 1):
        cols["XOCAL%d" % i] = x
        cols["CPAL%d" % i] = PLANT_DECOY_CP          # the decoy, lower surface
    if extra:
        cols.update(extra)
    names = list(cols)
    if shuffle:
        names = names[::-1]
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(names)
        w.writerow(["%.9g" % cols[n] for n in names])
    return path


def selftest():
    fails = []

    def check(name, cond, detail=""):
        if not cond:
            fails.append(f"{name}: {detail}")
        return cond

    with tempfile.TemporaryDirectory() as td:
        # ------------------------------------------------------------------ P-1 --
        # COLUMN NAME, NOT INDEX, AND UPPER vs LOWER.  The planted Cp sits at a known
        # x/c on the UPPER set; a decoy fills every LOWER Cp.  Then the header is
        # reversed and the SAME numbers are required back.
        def field(x):
            return PLANT_CP if abs(x - PLANT_XOC) < 1e-12 else -0.3
        d1 = os.path.join(td, "exp1")
        os.makedirs(d1)
        _synth_csv(os.path.join(d1, "a.csv"), plant=field)
        e = read_experiment(d1, quiet=True)
        up = e["rows"]["A"]["upper"]
        hit = [p for p in up if abs(p["x_over_c"] - PLANT_XOC) < 1e-12]
        check("P-1 the planted upper tap is found", len(hit) == 1, f"{len(hit)} hits")
        check("P-1 it carries the planted Cp, not the lower decoy",
              hit and abs(hit[0]["Cp"] - PLANT_CP) < 1e-12,
              f"got {hit[0]['Cp'] if hit else None!r}, planted {PLANT_CP}, "
              f"decoy {PLANT_DECOY_CP}")
        check("P-1 the upper set excludes every lower column",
              all(not re.fullmatch(r"CPAL\d+", p["column_cp"]) for p in up),
              str([p["column_cp"] for p in up][:6]))
        check("P-1 the lower set is separate and carries the decoy",
              e["rows"]["A"]["n_lower"] == 4
              and all(abs(p["Cp"] - PLANT_DECOY_CP) < 1e-12
                      for p in e["rows"]["A"]["lower"]),
              str(e["rows"]["A"]["lower"][:2]))
        d2 = os.path.join(td, "exp2")
        os.makedirs(d2)
        _synth_csv(os.path.join(d2, "a.csv"), plant=field, shuffle=True)
        e2 = read_experiment(d2, quiet=True)
        hit2 = [p for p in e2["rows"]["A"]["upper"] if abs(p["x_over_c"] - PLANT_XOC) < 1e-12]
        check("P-1 survives a reversed header",
              hit2 and abs(hit2[0]["Cp"] - PLANT_CP) < 1e-12,
              f"got {hit2[0]['Cp'] if hit2 else None!r}")
        if not hit or abs(hit[0]["Cp"] - PLANT_CP) > 1e-12:
            sys.stderr.write("REFUSED: the planted Cp was not read back by name.\n")
            return 2

        # ------------------------------------------------------------------ P-2 --
        # THE RESAMPLING TRAP, PROVEN WITH NUMBERS.  A shock of known height is planted
        # at a known x/c inside the FINE region; a WIDER interval further aft carries a
        # SMALLER slope but a LARGER per-index rise.  The unequal-interval locator must
        # return the planted x/c; the naive per-index argmax must return the wide one.
        x_shock = 0.35
        xs = [0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.33, 0.35, 0.37, 0.40,
              0.70, 1.00]
        cps = []
        for x in xs:
            if x <= 0.33:
                cps.append(-1.10)
            elif x <= 0.37:
                cps.append(-1.10 + 0.35 * (x - 0.33) / 0.04)    # slope 8.75 per c
            else:
                cps.append(-0.75)
        # the decoy: a gentle rise of 0.40 spread over the 0.30-wide interval 0.40->0.70
        for i, x in enumerate(xs):
            if x >= 0.70:
                cps[i] += 0.40
        sr = shock_position(xs, cps, tol=0.03)
        nv = shock_position_NAIVE_INDEX(xs, cps)
        check("P-2 a RESOLVED peak is reported as resolvable",
              sr["verdict"] == "GATE REACHED"
              and sr["local_interval_c"] <= 2 * 0.03,
              json.dumps({k: sr.get(k) for k in
                          ("verdict", "x_over_c", "local_interval_c", "reason")}))
        check("P-2 the unequal-interval locator finds the planted shock",
              sr["x_over_c"] is not None and abs(sr["x_over_c"] - x_shock) <= 0.021,
              f"got {sr['x_over_c']!r}, planted {x_shock}")
        check("P-2 the naive per-index argmax MISSES it",
              nv["x_over_c"] is not None and abs(nv["x_over_c"] - x_shock) > 0.05,
              f"naive got {nv['x_over_c']!r} -- it AGREED with the correct locator on "
              "this fixture, so the fixture proves nothing and must be rebuilt")
        check("P-2 and it returns the WIDEST interval, as the trap predicts",
              nv["x_over_c"] == 0.70, f"naive returned {nv['x_over_c']!r}")
        sp = spacing_report(xs)
        check("P-2 the spacing report SAYS the abscissa is non-uniform",
              sp["uniform"] is False and sp["max_over_min"] > 5.0, json.dumps(sp))
        # the control on the control: on a UNIFORM abscissa the two must AGREE, so the
        # fixture above is not passing merely because the naive reader is always wrong
        xu = [i / 40.0 for i in range(41)]
        cu = [(-1.10 if x <= 0.35 else -0.75) for x in xu]
        check("P-2 on a UNIFORM abscissa both locators agree",
              abs(shock_position(xu, cu)["x_over_c"]
                  - shock_position_NAIVE_INDEX(xu, cu)["x_over_c"]) <= 0.026,
              f"{shock_position(xu, cu)['x_over_c']} vs "
              f"{shock_position_NAIVE_INDEX(xu, cu)['x_over_c']}")
        check("P-2 and the spacing report SAYS that one is uniform",
              spacing_report(xu)["uniform"] is True, json.dumps(spacing_report(xu)))
        # a magnitude reader would return the LE suction peak; the signed one must not
        xs2 = [0.0, 0.02, 0.05, 0.10, 0.30, 0.33, 0.35, 0.37, 0.50, 1.0]
        cp2 = [0.9, -1.9, -1.5, -1.2, -1.1, -1.1, -0.925, -0.75, -0.7, -0.1]
        check("P-2 the locator does not return the LE suction peak",
              shock_position(xs2, cp2)["x_over_c"] > 0.2,
              f"got {shock_position(xs2, cp2)['x_over_c']!r} -- |dCp/dx| would return "
              "the leading edge on every row and call it a shock")
        # ---- THE RESOLVABILITY GATE, IN BOTH DIRECTIONS.  It must refuse a peak that
        # lands on a wide interval AND accept one that lands on a narrow one; a gate
        # that always refuses is as useless as one that never does.
        xw = [0.00, 0.10, 0.70, 0.80, 0.90, 1.00]         # a 0.60 c gap, row D's shape
        cw = [-1.00, -1.00, -0.30, -0.20, -0.10, 0.00]
        gw = shock_position(xw, cw, tol=0.03)
        check("P-2 an UNRESOLVABLE peak is NOT A RESULT, with the number",
              gw["verdict"] == "NOT A RESULT" and gw["local_interval_c"] > 0.5,
              json.dumps({k: gw.get(k) for k in
                          ("verdict", "x_over_c", "local_interval_c", "reason")}))
        check("P-2 and it still REPORTS the located x/c rather than hiding it",
              gw["x_over_c"] is not None, json.dumps(gw))
        xf = [i / 100.0 for i in range(101)]
        cf = [(-1.10 if x <= 0.45 else -0.75) for x in xf]
        gf = shock_position(xf, cf, tol=0.03)
        check("P-2 a well-sampled peak IS resolvable",
              gf["verdict"] == "GATE REACHED" and abs(gf["x_over_c"] - 0.46) < 0.02,
              json.dumps({k: gf.get(k) for k in ("verdict", "x_over_c", "local_interval_c")}))

        # ------------------------------------------------------------------ P-3 --
        # THE CONDITION GUARD MUST REFUSE, AND MUST ACCEPT.  A row at the WRONG
        # configuration (WBPN) must not be selected even though it matches M/alpha/Re.
        d3 = os.path.join(td, "exp3")
        os.makedirs(d3)
        _synth_csv(os.path.join(d3, "wbpn.csv"), extra={"CONFIG": 2.0}, plant=field)
        import subprocess
        r = subprocess.run([sys.executable, os.path.abspath(__file__),
                            "--exp-dir", d3, "--json"],
                           capture_output=True, text=True,
                           env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        check("P-3 a WBPN row is REFUSED at the WB condition", r.returncode == 2,
              f"rc={r.returncode}; a comparison at the wrong configuration was allowed")
        check("P-3 the refusal names the condition", "registered condition" in r.stderr,
              r.stderr[:200])
        _synth_csv(os.path.join(d3, "wb.csv"), plant=field)
        e3 = read_experiment(d3, quiet=True)
        check("P-3 and the WB row IS selected when present",
              abs(e3["selected"]["CONFIG"] - 1.0) < 1e-9, json.dumps(e3["selected"]))

        # ------------------------------------------------------------------ P-4 --
        # THE CFD SIDE: Cp, THE CONSTANT AND THE SIGN.  A synthetic wing surface is
        # written with p set so that Cp is EXACTLY a known function, and the reader must
        # return that function -- not |Cp|, not p/q, not (p-p_inf)/(rho U^2).
        raw = os.path.join(td, "p_wing.raw")
        want = {}
        with open(raw, "w") as f:
            f.write("# x  y  z  p\n")
            for letter, eta in ROWS:
                y = eta * SEMISPAN
                for j, xx in enumerate([0.0, 0.1, 0.35, 0.36, 0.6, 1.0]):
                    cp = -1.10 if xx <= 0.35 else -0.75
                    want.setdefault(letter, []).append((xx, cp))
                    p = P_INF + cp * Q_INF
                    f.write("%.10g %.10g %.10g %.10g\n" % (30.0 + xx * 5.0, y, 4.0, p))
        rr = read_surface_raw(raw)
        check("P-4 the raw reader names its columns", rr["header_names"] == ["x", "y", "z", "p"],
              str(rr["header_names"]))
        sec = cfd_sections(rr)
        check("P-4 all nine rows are cut", all(sec[l]["n"] == 6 for l, _ in ROWS),
              str({l: sec[l]["n"] for l, _ in ROWS}))
        gotA = sec["A"]["points"]
        check("P-4 Cp is (p - p_inf)/q_inf with the right SIGN",
              all(abs(g["Cp"] - w[1]) < 1e-9 for g, w in zip(gotA, want["A"])),
              str([(round(g["x_over_c"], 3), g["Cp"]) for g in gotA]))
        check("P-4 a negative Cp stays negative",
              all(g["Cp"] < 0 for g in gotA), "a magnitude crept into the reader")
        q_literal = 0.5 * 0.04503298815 * 300.0189024 * 300.0189024
        check("P-4 q_inf equals an externally computed literal",
              abs(Q_INF - q_literal) < 1e-9, f"{Q_INF} vs {q_literal}")
        # and the reader must MISS a planted point at the wrong span station
        with open(raw, "a") as f:
            f.write("%.10g %.10g %.10g %.10g\n"
                    % (31.0, 0.5 * SEMISPAN, 4.0, P_INF + PLANT_CP * Q_INF))
        sec2 = cfd_sections(read_surface_raw(raw))
        check("P-4 a point at eta=0.5 lands in row E and nowhere else",
              sec2["E"]["n"] == 7 and sec2["A"]["n"] == 6,
              str({l: sec2[l]["n"] for l, _ in ROWS}))

        # ------------------------------------------------------------------ P-5 --
        # THE COMPARISON ITSELF, IN BOTH DIRECTIONS, WITH THE NUMBER CHECKED.  A CFD
        # section offset from the experiment by an EXACTLY KNOWN amount must give that
        # deviation back, and must PASS a band above it and FAIL a band below it.
        OFFS = 0.037
        d5 = os.path.join(td, "exp5")
        os.makedirs(d5)
        _synth_csv(os.path.join(d5, "a.csv"), plant=lambda x: -0.3)
        e5 = read_experiment(d5, quiet=True)
        raw5 = os.path.join(td, "p5.raw")
        with open(raw5, "w") as f:
            f.write("# x  y  z  p\n")
            for letter, eta in ROWS:
                for xx in [i / 20.0 for i in range(21)]:
                    p = P_INF + (-0.3 + OFFS) * Q_INF
                    f.write("%.10g %.10g %.10g %.10g\n"
                            % (30.0 + xx * 5.0, eta * SEMISPAN, 4.0, p))
        sec5 = cfd_sections(read_surface_raw(raw5))
        cmp_loose = compare(e5, sec5, band=OFFS * 1.5)
        cmp_tight = compare(e5, sec5, band=OFFS * 0.5)
        ra = cmp_loose["rows"]["A"]
        check("P-5 the deviation IS the planted offset",
              ra["max_abs_dev"] is not None and abs(ra["max_abs_dev"] - OFFS) < 1e-9,
              f"got {ra['max_abs_dev']!r}, planted {OFFS}")
        check("P-5 a band above it PASSES", ra["verdict"] == "PASS", json.dumps(
            {k: ra[k] for k in ("verdict", "max_abs_dev", "n_outside_band")}))
        check("P-5 a band below it GATE FAILS",
              cmp_tight["rows"]["A"]["verdict"] == "GATE FAIL",
              json.dumps({k: cmp_tight["rows"]["A"][k]
                          for k in ("verdict", "max_abs_dev", "n_outside_band")}))
        check("P-5 with no band it is BLOCKED, not silently passed",
              compare(e5, sec5, band=None)["rows"]["A"]["verdict"] == "BLOCKED",
              json.dumps(compare(e5, sec5, band=None)["rows"]["A"].get("reason")))
        check("P-5 the ESP error bar is NOT used as the band",
              compare(e5, sec5, band=None)["data_error_bar_NOT_A_GATE"] == DATA_ERROR_BAR,
              "")
        # no CFD section at all -> PENDING, never PASS
        check("P-5 a missing CFD section is PENDING, never PASS",
              compare(e5, {}, band=OFFS)["rows"]["A"]["verdict"] == "PENDING", "")
        # and the interpolator must refuse to extrapolate
        check("P-5 the interpolator refuses to extrapolate",
              _interp([0.2, 0.8], [1.0, 2.0], 0.1) is None
              and _interp([0.2, 0.8], [1.0, 2.0], 0.9) is None, "")

    if fails:
        sys.stderr.write("SELFTEST RED:\n" + "\n".join("  " + f for f in fails) + "\n")
        return 1
    sys.stdout.write(
        "SELFTEST GREEN: P-1 planted Cp read by anchored column name with a lower-surface "
        "decoy and a reversed header, P-2 the resampling trap shown with numbers (the "
        "unequal-interval locator finds the planted shock, the per-index argmax returns "
        "the widest interval) AND both agreeing on a uniform abscissa, P-3 the condition "
        "guard refusing a WBPN row and accepting the WB row, P-4 Cp = (p-p_inf)/q_inf "
        "with the sign and q_inf against an external literal, P-5 the comparison giving "
        "back the planted offset and passing/failing bands either side of it.\n")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--exp-dir",
                    default="/home/ubuntu/crm-data/experimental/NTF197/TWICSCorr",
                    help="directory of NTF Test 197 CSVs")
    ap.add_argument("--surface-raw", help="postProcessing/<name>/<time>/p_wing.raw")
    ap.add_argument("--band", type=float,
                    help="Cp gate band (§5.3). Without it the comparison is BLOCKED.")
    ap.add_argument("--alpha", type=float, help="override the registered alpha")
    ap.add_argument("--alpha-tol", type=float, help="override the alpha admission window")
    ap.add_argument("--emit-sample-dict", action="store_true",
                    help="print the `surfaces` and `fieldMinMax` dictionaries and exit")
    ap.add_argument("--json", action="store_true", help="full JSON, not the summary")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if a.emit_sample_dict:
        print(SAMPLE_DICT)
        print(FIELD_MINMAX_DICT)
        sys.exit(0)
    cond = {k: v for k, v in COND.items()}
    if a.alpha is not None:
        cond["ALPHA"] = (a.alpha, cond["ALPHA"][1])
    if a.alpha_tol is not None:
        cond["ALPHA"] = (cond["ALPHA"][0], a.alpha_tol)
    exp = read_experiment(a.exp_dir, cond=cond)
    cfd = {}
    if a.surface_raw:
        cfd = cfd_sections(read_surface_raw(a.surface_raw))
    rep = {"tool": os.path.relpath(os.path.abspath(__file__), REPO_ROOT),
           "prereg": PREREG, "experiment": exp,
           "comparison": compare(exp, cfd, band=a.band)}
    if a.json:
        print(json.dumps(rep, indent=2, default=str))
    else:
        s = exp["selected"]
        print(json.dumps({
            "experimental_row": s,
            "residual_from_registered_condition": exp["residuals"],
            "source_file": exp["source_file"],
            "rows": {l: {"eta": exp["rows"][l]["eta"],
                         "n_upper": exp["rows"][l]["n_upper"],
                         "n_lower": exp["rows"][l]["n_lower"],
                         "spacing_upper": exp["rows"][l]["spacing_upper"],
                         "verdict": rep["comparison"]["rows"][l].get("verdict"),
                         "exp_shock_x_over_c":
                             rep["comparison"]["rows"][l].get("exp_shock", {}).get("x_over_c"),
                         "exp_shock_verdict":
                             rep["comparison"]["rows"][l].get("exp_shock", {}).get("verdict"),
                         "exp_shock_local_interval_c":
                             rep["comparison"]["rows"][l].get("exp_shock", {}).get("local_interval_c"),
                         "max_abs_dev": rep["comparison"]["rows"][l].get("max_abs_dev")}
                     for l, _ in ROWS}}, indent=2, default=str))
    sys.exit(0)


if __name__ == "__main__":
    main()
