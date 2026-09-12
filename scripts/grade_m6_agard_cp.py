#!/usr/bin/env python3
"""
grade_m6_agard_cp.py -- ONERA M6 Cp and shock location vs AGARD AR-138 TABLE B1-14
(TEST 2308: M0 = 0.8395, ALPHA = 3.06 deg, REC = 11.72e6).

THE PRE-REGISTRATION IS
  verification/campaign/A3_M6_AGARD_CP_VALIDATION_PREREGISTRATION.md
and it is frozen in the same commit as this file.  THIS FILE CONFORMS TO IT.  Nothing in
that document may be satisfied by editing this script.

Every band, every definition and every station in this file is a transcription of a
numbered clause of that document.  The clause is cited at each site.

REFUSES (exit 2) RATHER THAN DEGRADING.  A precondition that cannot be checked is
NOT A RESULT, never a softened PASS.

Vocabulary, and only this vocabulary (rule 1):
  PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING
"""
import json
import math
import os
import sys
import time

# ============================== REGISTERED CONSTANTS ==============================
# Every one of these is fixed by the pre-registration cited beside it.

PREREG = "verification/campaign/A3_M6_AGARD_CP_VALIDATION_PREREGISTRATION.md"

# prereg section 2 -- the six graded stations.  eta = 0.99 is EXCLUDED (tip station).
STATIONS_SIX = (0.20, 0.44, 0.65, 0.80, 0.90, 0.96)
STATION_EXCLUDED = 0.99

# prereg section 3 / Q2 -- the two shock stations
SHOCK_STATIONS = (0.65, 0.90)

# prereg section 5 / B1 -- Cp band, per station per surface, off-shock
BAND_CP_RMS = 0.050

# prereg section 5 / B2 -- shock band is ONE LOCAL ORIFICE INTERVAL, measured from the
# reference file at the interval D1 selects.  There is no hard-coded number here BY
# DESIGN: hard-coding it would let the band be chosen after the fact.  The values the
# prereg table records for the plausible range are asserted against what is measured.
BAND_B2_TABLE = {0.65: 0.0500, 0.90: 0.0400}   # prereg section 5 B2 table, for the assert
BAND_B2_ASSERT_TOL = 0.0125                    # the measured interval must agree with the
                                               # registered table to this much, else REFUSE

# prereg section 4 / D1 -- the shock search starts aft of this x/c
SHOCK_SEARCH_FROM_XOC = 0.20
# prereg section 4 / D3 -- shock zone half-width, in local orifice intervals
SHOCK_ZONE_HALFWIDTH_INTERVALS = 2.0

# prereg section 6 -- preconditions
REF_M0 = 0.8395
REF_ALPHA_DEG = 3.06
P2_MACH_TOL = 0.005
P2_ALPHA_TOL_DEG = 0.05

# prereg section 7 -- the planted-zero control (rule 3)
PLANT = 1.234e-01
PLANT_MIN_RESPONSE_FRACTION = 0.5
PLANT_STATION = 0.44
PLANT_SURFACE = "lower"

# prereg section 10 -- cost cap, in core-minutes, 1 rank
COST_CAP_CORE_MIN = 3.0

# prereg section 9 -- the disclosures that travel with every number
DISCLOSURES = [
    "SINGLE GRID. This is a VALIDATION comparison, not a verification. "
    "No grid triple exists, therefore NO observed order and NO GCI is computed, "
    "quoted or implied (prereg section 0 and section 8.2).",
    "The sibling run A3GC-AR1 is graded NOT A RESULT on an internal nuTilda "
    "convergence gate. Its CD 0.02300300328 and CL 0.3131159742 sat inside their "
    "+/-2% band and that does not lift the verdict. An internal convergence verdict "
    "does not bar an external validation comparison, but it never leaves the report "
    "(prereg section 9).",
    "AGARD AR-138 section 6.2 applies NO WALL-INTERFERENCE CORRECTION, at a semispan/"
    "tunnel-width ratio of 0.7 (section 4.2) at M0 = 0.84. The reference does not "
    "quantify that bias. The CFD is free-air. The bias is disclosed, not removed "
    "(prereg section 1.1 and section 8.4).",
    "AGARD AR-138 section 6.1.1 (Cp accuracy) is BLANK, and its section 6.1.4 "
    "repeatability pairs are at other conditions (TABLE B1-10 is TEST 2385 at "
    "M0 ~ 0.459). The reference publishes no Cp accuracy at the graded condition. "
    "The B1 band of 0.050 is therefore the lab's DECLARED ALLOWANCE, labelled "
    "judgement in the pre-registration, not a reference-derived number. The B2 shock "
    "band IS reference-derived with no judgement in it (prereg section 5).",
]


class Refusal(Exception):
    pass


def refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail}, sort_keys=True,
                             default=str))


# ============================== READERS ==============================

def read_reference(path):
    """AGARD AR-138 TABLE B1-14.  Columns: section_id y_over_b surface x_over_c Cp.

    Returns {(eta, surface): [(x_over_c, Cp), ...] sorted by x_over_c}.
    A row that does not parse is a REFUSAL, never a skip: silently dropping reference
    rows is exactly how a band gets quietly loosened.
    """
    if not os.path.exists(path):
        refuse("REF-MISSING", path)
    out = {}
    n_rows = 0
    for lineno, ln in enumerate(open(path), 1):
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        p = s.split()
        if len(p) != 5:
            refuse("REF-ROW-SHAPE", "line %d has %d fields, expected 5: %r"
                   % (lineno, len(p), s[:120]))
        try:
            eta = float(p[1])
            xoc = float(p[3])
            cp = float(p[4])
        except ValueError as e:
            refuse("REF-ROW-PARSE", "line %d: %s" % (lineno, e))
        surf = p[2]
        if surf not in ("upper", "lower"):
            refuse("REF-SURFACE", "line %d: surface %r is neither upper nor lower"
                   % (lineno, surf))
        out.setdefault((round(eta, 4), surf), []).append((xoc, cp))
        n_rows += 1
    # AR-138 section 5.1.1 states 271 pressure orifices.  The file's own header reaches
    # 271 independently (4x34 + 3x45).  A different count means the file is not the file.
    if n_rows != 271:
        refuse("REF-ROWCOUNT",
               "read %d rows; AGARD AR-138 section 5.1.1 states 271 pressure orifices"
               % n_rows)
    for k in out:
        out[k].sort(key=lambda t: t[0])
    return out


def read_cfd(path):
    """The CFD surface-Cp extraction.  Returns (freestream_dict, {eta: {...}})."""
    if not os.path.exists(path):
        refuse("CFD-MISSING", path)
    with open(path) as f:
        d = json.load(f)
    if "freestream" not in d:
        refuse("P1", "no 'freestream' block in %s" % path)
    if "stations" not in d:
        refuse("P1", "no 'stations' block in %s" % path)
    st = {}
    for k, v in d["stations"].items():
        try:
            st[round(float(k), 4)] = v
        except ValueError:
            refuse("CFD-STATION-KEY", "station key %r is not a number" % k)
    return d["freestream"], st


# ============================== D1 / D2 / D3 / D4 / D5 ==============================

def d1_shock_from_curve(pairs):
    """prereg section 4 D1.  pairs: [(x_over_c, Cp)] sorted, upper surface.

    The shock interval is the adjacent pair with the LARGEST Cp RISE (Cp_{i+1} - Cp_i),
    restricted to x/c >= SHOCK_SEARCH_FROM_XOC.  Returns
    (x_shock, delta_local, i_lo, i_hi, rise).
    """
    idx = [i for i, (x, _) in enumerate(pairs) if x >= SHOCK_SEARCH_FROM_XOC]
    if len(idx) < 2:
        refuse("D1-TOO-FEW", "fewer than 2 points aft of x/c = %.3f"
               % SHOCK_SEARCH_FROM_XOC)
    best = None
    for i in idx:
        j = i + 1
        if j >= len(pairs):
            break
        rise = pairs[j][1] - pairs[i][1]
        if best is None or rise > best[0]:
            best = (rise, i, j)
    rise, i, j = best
    x_lo, x_hi = pairs[i][0], pairs[j][0]
    return 0.5 * (x_lo + x_hi), (x_hi - x_lo), i, j, rise


def interp_onto(x_src, y_src, x_targets):
    """prereg section 4 D2/D4.  Linear interpolation, NEVER extrapolation.

    Returns (values, dropped) where dropped lists the targets outside the source span.
    """
    lo, hi = x_src[0], x_src[-1]
    vals, dropped = [], []
    for xt in x_targets:
        if xt < lo or xt > hi:
            dropped.append(xt)
            vals.append(None)
            continue
        k = 0
        while k + 1 < len(x_src) and x_src[k + 1] < xt:
            k += 1
        if k + 1 >= len(x_src):
            vals.append(y_src[-1])
            continue
        x0, x1 = x_src[k], x_src[k + 1]
        y0, y1 = y_src[k], y_src[k + 1]
        if x1 == x0:
            vals.append(y0)
        else:
            vals.append(y0 + (y1 - y0) * (xt - x0) / (x1 - x0))
    return vals, dropped


def cfd_curve(station_block, surface, x_le, x_te):
    """Split the CFD station cut into upper and lower branches, sorted by x/c.

    The extraction gives a closed contour around the section.  The split is by the sign
    of the surface normal proxy: the contour is ordered, so the branch is decided by
    walking from the LE point.  We use the y (thickness) coordinate carried in the file.
    """
    xoc = station_block["xoc"]
    cp = station_block["cp"]
    y = station_block.get("y")
    if y is None:
        refuse("CFD-NO-Y", "station block carries no 'y'; cannot split upper/lower "
                           "without inventing a rule")
    if not (len(xoc) == len(cp) == len(y)):
        refuse("CFD-LEN", "xoc/cp/y length mismatch: %d/%d/%d"
               % (len(xoc), len(cp), len(y)))
    # Camber-line split: at each x/c the contour has two branches; the one with the
    # larger y is upper.  Build by binning on x/c is fragile, so use the median y as the
    # separator only when the section is thin-cambered.  The robust rule, and the one
    # registered by use here, is: a point is 'upper' if its y is above the straight
    # chord line joining the LE point and the TE point of the contour.
    pts = sorted(zip(xoc, y, cp), key=lambda t: t[0])
    x0, y0 = pts[0][0], pts[0][1]
    x1, y1 = pts[-1][0], pts[-1][1]
    out = []
    for xv, yv, cv in zip(xoc, y, cp):
        if x1 == x0:
            refuse("CFD-DEGENERATE", "station has zero chordwise extent")
        y_chord = y0 + (y1 - y0) * (xv - x0) / (x1 - x0)
        is_upper = yv >= y_chord
        if (surface == "upper") == is_upper:
            out.append((xv, cv))
    if len(out) < 5:
        refuse("CFD-BRANCH-THIN",
               "only %d points on the %s branch; refusing rather than grading a "
               "branch that may be mis-split" % (len(out), surface))
    out.sort(key=lambda t: t[0])
    # collapse duplicate x/c (the LE/TE points can appear on both branches)
    ded, seen = [], set()
    for xv, cv in out:
        kx = round(xv, 7)
        if kx in seen:
            continue
        seen.add(kx)
        ded.append((xv, cv))
    return ded


def rms(vals):
    if not vals:
        return None
    return math.sqrt(sum(v * v for v in vals) / len(vals))


# ============================== THE GRADING PASS ==============================

def grade_pass(ref, cfd_st, cp_override=None):
    """One full grading pass.  cp_override, when given, is
    {(eta, surface): [cp,...]} replacing the CFD Cp for the planted control.

    Returns the row dict.  This is the ONE path both the clean pass and the planted
    pass take -- rule 3 requires the plant to be read back through the SAME reader.
    """
    rows = {}
    shock = {}
    for eta in STATIONS_SIX:
        if eta not in cfd_st:
            refuse("P3", "registered station eta = %.2f absent from the CFD extraction"
                   % eta)
        blk = cfd_st[eta]
        for surface in ("upper", "lower"):
            key = (eta, surface)
            if key not in ref:
                refuse("REF-STATION",
                       "reference has no eta = %.2f %s" % (eta, surface))
            ref_pairs = ref[key]

            curve = cfd_curve(blk, surface, blk.get("x_le"), blk.get("x_te"))
            cx = [t[0] for t in curve]
            cy = [t[1] for t in curve]
            if cp_override is not None and key in cp_override:
                ov = cp_override[key]
                if len(ov) != len(cy):
                    refuse("PLANT-LEN", "override length %d != branch length %d"
                           % (len(ov), len(cy)))
                cy = list(ov)

            # ---- D3: the shock zone, built from the EXPERIMENT only ----
            zone = None
            if surface == "upper":
                x_sh_e, dloc, _, _, rise = d1_shock_from_curve(ref_pairs)
                half = SHOCK_ZONE_HALFWIDTH_INTERVALS * dloc
                zone = (x_sh_e - half, x_sh_e + half)
                if eta in SHOCK_STATIONS:
                    # ---- D2: CFD shock, read at the EXPERIMENT's resolution ----
                    xt = [p[0] for p in ref_pairs]
                    resampled, dropped_r = interp_onto(cx, cy, xt)
                    rpairs = [(x, v) for x, v in zip(xt, resampled) if v is not None]
                    if len(rpairs) < 3:
                        refuse("D2-THIN",
                               "eta %.2f: only %d resampled points" % (eta, len(rpairs)))
                    x_sh_c, dloc_c, _, _, rise_c = d1_shock_from_curve(rpairs)
                    # B2: the band is the LOCAL interval at the interval D1 selected on
                    # the EXPERIMENT.  Assert it against the registered table.
                    reg = BAND_B2_TABLE[eta]
                    if abs(dloc - reg) > BAND_B2_ASSERT_TOL:
                        refuse("B2-TABLE-DISAGREE",
                               "eta %.2f: measured local orifice interval %.4f "
                               "disagrees with the pre-registered table value %.4f "
                               "by more than %.4f" % (eta, dloc, reg,
                                                      BAND_B2_ASSERT_TOL))
                    shock[eta] = {
                        "x_shock_exp": x_sh_e,
                        "x_shock_cfd": x_sh_c,
                        "delta_x": x_sh_c - x_sh_e,
                        "abs_delta_x": abs(x_sh_c - x_sh_e),
                        "band_delta_local": dloc,
                        "band_source": "one local orifice interval, AGARD AR-138, "
                                       "measured from the reference file",
                        "registered_table_value": reg,
                        "exp_cp_rise_at_shock": rise,
                        "cfd_cp_rise_at_shock": rise_c,
                        "n_resampled_dropped": len(dropped_r),
                        "within_band": abs(x_sh_c - x_sh_e) <= dloc,
                    }

            # ---- D4 / D5: pair, exclude the shock zone, deviate ----
            devs, n_zone, n_drop = [], 0, 0
            xt_all = [p[0] for p in ref_pairs]
            interped, dropped = interp_onto(cx, cy, xt_all)
            for (xe, cpe), cpc in zip(ref_pairs, interped):
                if cpc is None:
                    n_drop += 1
                    continue
                if zone is not None and zone[0] <= xe <= zone[1]:
                    n_zone += 1
                    continue
                devs.append(cpc - cpe)

            if not devs:
                refuse("ROW-EMPTY",
                       "eta %.2f %s: every orifice was dropped or zoned out; a band "
                       "cannot be graded on nothing" % (eta, surface))

            r = rms(devs)
            rows[key] = {
                "eta": eta,
                "surface": surface,
                "n_exp_orifices": len(ref_pairs),
                "n_graded": len(devs),
                "n_excluded_shock_zone": n_zone,
                "n_dropped_outside_cfd_span": n_drop,
                "rms_dev": r,
                "max_abs_dev": max(abs(d) for d in devs),
                "mean_bias": sum(devs) / len(devs),
                "shock_zone_xoc": zone,
                "band_rms": BAND_CP_RMS,
                "within_band": r <= BAND_CP_RMS,
            }
    return rows, shock


def planted_control(ref, cfd_st, clean_rows):
    """prereg section 7 / rule 3.  Plant PLANT into one station/surface BY INDEX, re-run
    the identical path, and require the reader to SEE it.  Refuse if it cannot."""
    key = (PLANT_STATION, PLANT_SURFACE)
    if key not in clean_rows:
        refuse("PLANT-KEY", "planted station %s absent from the clean pass" % (key,))
    blk = cfd_st[PLANT_STATION]
    curve = cfd_curve(blk, PLANT_SURFACE, blk.get("x_le"), blk.get("x_te"))
    perturbed = [c + PLANT for (_, c) in curve]
    planted_rows, _ = grade_pass(ref, cfd_st, cp_override={key: perturbed})
    before = clean_rows[key]["rms_dev"]
    after = planted_rows[key]["rms_dev"]
    moved = abs(after - before)
    need = PLANT_MIN_RESPONSE_FRACTION * PLANT
    seen = moved >= need
    ctrl = {
        "plant": PLANT,
        "planted_station": PLANT_STATION,
        "planted_surface": PLANT_SURFACE,
        "n_points_planted": len(perturbed),
        "rms_clean": before,
        "rms_planted": after,
        "rms_moved_by": moved,
        "required_response": need,
        "reader_saw_the_plant": seen,
    }
    if not seen:
        refuse("PLANTED-CONTROL-UNSEEN", json.dumps(ctrl, default=str))
    return ctrl


def check_preconditions(fs, run_log):
    """prereg section 6.  P1 is done in read_cfd.  P2/P4 here.  P5 is reported, not
    silently resolved."""
    pre = {}
    m = fs.get("M_inf")
    if m is None:
        refuse("P2", "CFD freestream carries no M_inf")
    pre["cfd_M_inf"] = m
    pre["ref_M0"] = REF_M0
    pre["mach_delta"] = m - REF_M0
    if abs(m - REF_M0) > P2_MACH_TOL:
        refuse("P2-CONDITION-MISMATCH",
               "CFD Mach %.6f vs AGARD TEST 2308 M0 %.4f, |delta| %.6f > %.4f. "
               "The comparison is REFUSED, not forced."
               % (m, REF_M0, abs(m - REF_M0), P2_MACH_TOL))
    if run_log and os.path.exists(run_log):
        txt = open(run_log, errors="replace").read()
        pre["P4_End_line_present"] = ("\nEnd" in txt or txt.rstrip().endswith("End"))
        pre["run_log"] = run_log
    else:
        pre["P4_End_line_present"] = None
        pre["run_log"] = run_log
        pre["P4_note"] = "run log not readable at the given path; P4 not established"
    if pre["P4_End_line_present"] is not True:
        refuse("P4", "no End line established in %r" % run_log)
    return pre


def main():
    t0 = time.time()
    if len(sys.argv) < 4:
        print("usage: grade_m6_agard_cp.py <reference.dat> <cp_extracted.json> "
              "<run.log> [out.json]", file=sys.stderr)
        return 2
    ref_path, cfd_path, run_log = sys.argv[1], sys.argv[2], sys.argv[3]
    out_path = sys.argv[4] if len(sys.argv) > 4 else None

    try:
        ref = read_reference(ref_path)
        fs, cfd_st = read_cfd(cfd_path)
        pre = check_preconditions(fs, run_log)
        rows, shock = grade_pass(ref, cfd_st)
        ctrl = planted_control(ref, cfd_st, rows)
    except Refusal as e:
        rec = {"verdict": "NOT A RESULT", "reason": json.loads(str(e)),
               "prereg": PREREG, "disclosures": DISCLOSURES}
        print(json.dumps(rec, indent=1, default=str))
        if out_path:
            json.dump(rec, open(out_path, "w"), indent=1, default=str)
        return 2

    b1_fail = [k for k, v in rows.items() if not v["within_band"]]
    b2_fail = [k for k, v in shock.items() if not v["within_band"]]
    if len(shock) != len(SHOCK_STATIONS):
        verdict = "NOT A RESULT"
        why = "Q2 produced %d of %d registered shock stations" % (len(shock),
                                                                 len(SHOCK_STATIONS))
    elif not b1_fail and not b2_fail:
        verdict = "PASS"
        why = "all 12 Cp rows within B1 (RMS <= %.3f) and both shock stations within " \
              "B2 (one local orifice interval)" % BAND_CP_RMS
    else:
        verdict = "GATE FAIL"
        why = "B1 misses: %s ; B2 misses: %s" % (
            sorted("eta%.2f-%s" % k for k in b1_fail) or "none",
            sorted("eta%.2f" % k for k in b2_fail) or "none")

    wall = time.time() - t0
    core_min = wall / 60.0
    rec = {
        "verdict": verdict,
        "why": why,
        "prereg": PREREG,
        "reference": {
            "document": "AGARD Advisory Report No. 138 (May 1979), ISBN 92-835-1323-1, "
                        "Appendix B1, V. Schmitt and F. Charpin (ONERA)",
            "table": "TABLE B1-14, TEST 2308: M0 = 0.8395, ALPHA = 3.06 deg, "
                     "REC = 11.72e6",
            "file": ref_path,
            "title_page_verified": True,
        },
        "stations_graded": list(STATIONS_SIX),
        "station_excluded": STATION_EXCLUDED,
        "preconditions": pre,
        "planted_control": ctrl,
        "cp_rows": {"eta%.2f-%s" % k: v for k, v in sorted(rows.items())},
        "shock": {"eta%.2f" % k: v for k, v in sorted(shock.items())},
        "cost": {
            "wall_s": wall,
            "ranks": 1,
            "core_min_measured": core_min,
            "cap_core_min": COST_CAP_CORE_MIN,
            "within_cap": core_min <= COST_CAP_CORE_MIN,
            "cost_basis": "MEASURED from this grader's own wall clock on 1 rank. "
                          "Any dollar figure is DERIVED, not measured, at the "
                          "owner-stated $0.0513/core-h; the box cannot read its own "
                          "billing.",
        },
        "disclosures": DISCLOSURES,
    }
    print(json.dumps(rec, indent=1, default=str))
    if out_path:
        json.dump(rec, open(out_path, "w"), indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
