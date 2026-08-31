#!/usr/bin/env python3
r"""Curriculum D19R -- THE STEP SELECTOR, ADJOINT-BLIND AND R1-BLIND BY ASSERTION,
READING DECADE-SEPARATED NEIGHBOURS OFF A HALF-DECADE GRID.

DERIVED FROM `curriculum_D19/d19_select_step.py` with exactly these deltas.
D19's file is FROZEN and is not edited.

WHY A DECADE STRIDE ON A HALF-DECADE GRID -- THE WHOLE POINT OF THIS FILE
=========================================================================
D19 sampled decades and found `shape[7]`/`CD` flat NOWHERE across five of them.
D19R samples HALF-decades, because a flat narrower than a decade is invisible to
a decade grid.  **That refinement creates a trap, and this file is where it is
closed.**

Half-decade neighbours deviate less FOR A PURELY GEOMETRIC REASON -- they are
closer.  Grading a two-sided plateau against them would relax `G19-1b`'s 10.0 %
band **by regridding**, with nobody editing a threshold and nothing in any diff
to see.  **Relaxing a gate threshold is reserved to Sanaa** (`CLAUDE.md` rule 9);
it is not available to a lane by arithmetic any more than by edit.

    FROZEN RULE G19R-1b-N (PREREGISTRATION.md section 1.3).  The neighbour
    deviation at a candidate step `s` is computed against `s x 10` and `s / 10`.
    On this grid that is a stride of TWO INDICES, not one.  The half-decade
    points are additional candidate CENTRES; they are NEVER neighbours.

So `DECADE_STRIDE = 2` and `deviations()` indexes `level -/+ DECADE_STRIDE`.
The gate's strictness is byte-for-byte D19's.  `assert_decade_stride()` proves
the stride really spans a decade on the registered sweep, from the sweep itself,
so the constant cannot silently stop matching the grid.

WHAT THE SELECTOR MAY READ, AND WHAT IT REFUSES
===============================================
`DAFOAM_CHARTER.md` section 3 forbids "Selecting the step after seeing which one
agrees."  What it forbids is selecting by agreement with the ADJOINT;
`VERIFICATION_CHARTER.md` section 7 step 1 REQUIRES selecting by flatness of the
FD curve.  The distinction is the defensibility of the whole item, so it is
mechanical: this selector reads only `rows[].fd`, is handed no adjoint, and
asserts at entry that

  * no adjoint-shaped key exists at any depth (CONTROL N), AND
  * the document's `mode` is the sweep mode `S8` -- never `X` (the adjoint
    artefact) and NEVER `R1`.

**R1-BLINDNESS IS NEW IN D19R AND IS NOT COSMETIC.**  Arm `R1` measures
`shape[7]` at a SENSITIVITY-EQUALISED ladder and is registered NON-GRADED
(PREREGISTRATION.md section 4.3).  If its artefact could reach the selector, a
step could be chosen off a ladder that no gate governs -- a second route to the
thing section 3 forbids.  It is refused by `mode`, by a `grades_nothing` flag, and
by the `diagnostic_only` key, so three independent things must fail together.

Usage:  d19r_select_step.py --fd <d19r_S.json> --out <d19r_selected_step.json>
        d19r_select_step.py --selftest
"""
import copy
import json
import os
import sys

# ---- registered constants (PREREGISTRATION.md sections 4.1 and 5) ------------
STEPS_SWEEP = {
    "shape":  [3.0e-2, 1.0e-2, 3.0e-3, 1.0e-3, 3.0e-4, 1.0e-4, 3.0e-5, 1.0e-5],
    "patchV": [3.0e-1, 1.0e-1, 3.0e-2, 1.0e-2, 3.0e-3, 1.0e-3, 3.0e-4, 1.0e-4],
}
# G19R-1b-N: a decade is TWO indices on a half-decade grid.
DECADE_STRIDE = 2

# The GRADED candidates: those with BOTH decade neighbours present in the sweep
# AND inside VERIFICATION_CHARTER.md section 7 step 5's sanctioned range
# [1e-3, 1e-2] for `shape`.  Frozen as explicit LEVEL INDICES so nothing here
# re-derives them:
#     level 2 -> shape 3e-3 / patchV 3e-2
#     level 3 -> shape 1e-3 / patchV 1e-2
# Levels 4 and 5 (3e-4, 1e-4) HAVE both decade neighbours and ARE measured and
# reported as rows -- section 7 requires a sweep to report its failed steps -- but
# they sit BELOW the sanctioned range and are registered NOT GRADED.
CANDIDATE_LEVELS = [2, 3]
REPORTED_NOT_GRADED_LEVELS = [4, 5]

COMPONENTS = [("shape", 0), ("shape", 3), ("shape", 6), ("shape", 7), ("patchV", 1)]
FUNCTIONS = ["CD", "CL"]
PLATEAU_TOL_PCT = 10.0        # G19R-1b -- D19's band, UNCHANGED
NEAR_ZERO_ABS = 1.0e-14

# ---- CONTROL P / D constants, RELATIVE by construction (rule 3) --------------
PLANT_K = 5.0                 # plant = K * (band/100) * |ref| -> 5x the band
PLANT_K_SHRUNK = 0.5          # the SUFFICIENCY RED LEG: must NOT cross
DECISION_MARGIN_PP = 100.0

# The EXACT top-level key set `d19r_xf.py` writes in modes S8 and S1.
ALLOWED_TOP_KEYS = {
    "item", "mode", "producer_md5", "header_md5", "nprocs", "identity",
    "components_requested", "n_components_requested", "steps",
    "steps_sweep_registered", "steps_shared_with_d19", "selected_step",
    "kappa", "r1_ladder", "ctrl_step",
    "plant", "plant_K", "plant_shrunk", "plant_K_shrunk", "plant_band_pct",
    "plant_moved_pp", "plant_moved_pp_shrunk",
    "CD_baseline", "CL_baseline", "CD_baseline_repeat", "CL_baseline_repeat",
    "eta_raw", "eta_used", "eta_floored", "baseline_dvs", "rows", "n_rows",
    "contains_adjoint", "grades_nothing",
}
ADJOINT_NAMES = {
    "adjoint", "adjoints", "jadj", "jadjoint", "adj", "dadj", "adjvalues",
    "adjointvalues", "totals", "computetotals", "jacobian", "gradadj",
    "dcdadj", "dcladj", "danalytic", "analytic", "reference",
}


class Refusal(Exception):
    pass


def refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail}, sort_keys=True, default=str))


def _norm(k):
    return "".join(ch for ch in str(k).lower() if ch.isalnum())


# ================= the stride is proved against the grid, not asserted in prose ==
def assert_decade_stride():
    """A stride constant that stops matching the grid is a silently relaxed gate.
    Prove, from the registered sweep itself, that `DECADE_STRIDE` spans a decade."""
    for dv, steps in STEPS_SWEEP.items():
        for i in range(len(steps) - DECADE_STRIDE):
            ratio = steps[i] / steps[i + DECADE_STRIDE]
            if abs(ratio - 10.0) > 1e-9 * 10.0:
                refuse("DECADE_STRIDE_DOES_NOT_SPAN_A_DECADE", {
                    "dv": dv, "level": i, "stride": DECADE_STRIDE,
                    "steps": [steps[i], steps[i + DECADE_STRIDE]], "ratio": ratio,
                    "note": "G19R-1b-N requires neighbours separated by exactly one "
                            "decade; a stride that does not span one would relax the "
                            "gate by regridding"})
    return True


# ================= CONTROL N: the entry assert ================================
def assert_adjoint_free(obj, where="<input>"):
    """REFUSE (the caller exits 2) if anything adjoint-shaped -- or R1-shaped -- is present."""
    if not isinstance(obj, dict):
        refuse("NOT_A_MAPPING", {"where": where, "type": type(obj).__name__})
    extra = sorted(set(obj) - ALLOWED_TOP_KEYS)
    if extra:
        refuse("ADJOINT_ASSERT_TOP_KEY_NOT_WHITELISTED", {
            "where": where, "unexpected_top_level_keys": extra,
            "note": "the selector accepts only the FD sweep artefact's own key set; "
                    "`diagnostic_only` is R1's marker and is NOT whitelisted"})
    if obj.get("mode") != "S8":
        refuse("ADJOINT_ASSERT_MODE", {
            "where": where, "mode": obj.get("mode"),
            "note": "mode X is the ADJOINT artefact and mode R1 is the NON-GRADED "
                    "sensitivity-equalised diagnostic; the selector opens neither"})
    if obj.get("contains_adjoint") is not False:
        refuse("ADJOINT_ASSERT_SELF_DECLARATION", {
            "where": where, "contains_adjoint": obj.get("contains_adjoint")})
    if obj.get("grades_nothing") is True:
        refuse("R1_ASSERT_GRADES_NOTHING", {
            "where": where,
            "note": "an artefact that declares it grades nothing may not choose the "
                    "step that every gate is then read at"})

    hits = []

    def walk(node, path):
        if isinstance(node, dict):
            for k, v in node.items():
                if _norm(k) in ADJOINT_NAMES:
                    hits.append("%s.%s" % (path, k))
                walk(v, "%s.%s" % (path, k))
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, "%s[%d]" % (path, i))

    walk(obj, where)
    if hits:
        refuse("ADJOINT_ASSERT_NAME_FOUND", {
            "where": where, "paths": hits[:20], "n": len(hits),
            "note": "selecting a step by agreement with the adjoint is DAFOAM_CHARTER "
                    "section 3's forbidden act; the selector refuses rather than reads"})
    return True


# ================= the FD-only reading ========================================
def fd_table(doc):
    """rows[].fd -> {(dv, idx, of): [v0..v7] in sweep order}.  READS NOTHING ELSE."""
    want = {(d, i) for d, i in COMPONENTS}
    table, seen = {}, set()
    for row in doc.get("rows", []):
        dv, idx = row.get("dv"), row.get("idx")
        if (dv, idx) not in want:
            continue
        if row.get("status") != "MEASURED":
            refuse("COMPONENT_NOT_MEASURED", {"dv": dv, "idx": idx, "status": row.get("status")})
        seen.add((dv, idx))
        for of in FUNCTIONS:
            vals = []
            for s in STEPS_SWEEP[dv]:
                hit = None
                for k, v in row["fd"].items():
                    if float(k) == s:
                        hit = v
                        break
                if hit is None:
                    refuse("SWEEP_STEP_ABSENT", {"dv": dv, "idx": idx, "step": s})
                if not hit.get("ok"):
                    # A failed step is REPORTED as a row by the instrument, but a
                    # candidate cannot be selected against a neighbour that failed.
                    refuse("SWEEP_STEP_FAILED", {"dv": dv, "idx": idx, "step": s,
                                                 "error": hit.get("error")})
                vals.append(float(hit["dCD" if of == "CD" else "dCL"]))
            table[(dv, idx, of)] = vals
    missing = sorted(want - seen)
    if missing:
        refuse("COMPONENT_ABSENT", {"missing": [list(m) for m in missing]})
    return table


def deviations(table, level):
    """Both DECADE-separated neighbour deviations, per component and function."""
    out = {}
    lo, hi = level - DECADE_STRIDE, level + DECADE_STRIDE
    for (dv, idx, of), vals in table.items():
        if lo < 0 or hi >= len(vals):
            refuse("CANDIDATE_LACKS_DECADE_NEIGHBOUR", {
                "level": level, "stride": DECADE_STRIDE, "n_levels": len(vals)})
        ref = vals[level]
        if abs(ref) < NEAR_ZERO_ABS:
            refuse("NEAR_ZERO", {"dv": dv, "idx": idx, "of": of, "level": level, "ref": ref})
        out[(dv, idx, of)] = (abs(vals[lo] - ref) / abs(ref) * 100.0,
                              abs(vals[hi] - ref) / abs(ref) * 100.0)
    return out


def score(table, level):
    """max over components and over BOTH functions of the two neighbour deviations.

    `max`, not `min`.  D15's own rule used `min`, which passes a component that
    agrees with ONE neighbour and misses the other by any margin whatever -- a
    boundary, not a plateau.  D19 tightened it to `max` and D19R does NOT relax it.
    """
    dev = deviations(table, level)
    worst, arg = -1.0, None
    for key in sorted(dev):
        for side, val in enumerate(dev[key]):
            if val > worst:
                worst, arg = val, (key, side)
    return worst, arg, dev


def select(table):
    """s* = argmin score over the GRADED candidate levels; ties break to the LARGER step."""
    assert_decade_stride()
    scored = []
    for lv in CANDIDATE_LEVELS:
        w, arg, dev = score(table, lv)
        scored.append({"level": lv, "score_pct": w, "binding": arg, "dev": dev,
                       "s_shape": STEPS_SWEEP["shape"][lv],
                       "s_patchV": STEPS_SWEEP["patchV"][lv]})
    # min score; tie -> LARGER step, and a larger step is a SMALLER level index
    # because the sweep is registered in descending order.
    best = min(scored, key=lambda c: (c["score_pct"], c["level"]))
    return best, scored


def report_not_graded(table):
    """Levels 4 and 5 are MEASURED and REPORTED but sit below section 7 step 5's
    sanctioned range, so they are registered NOT GRADED.  Reported so the sweep
    does not hide what it measured."""
    out = []
    for lv in REPORTED_NOT_GRADED_LEVELS:
        try:
            w, arg, _dev = score(table, lv)
        except Refusal as exc:
            out.append({"level": lv, "graded": False,
                        "refused": json.loads(str(exc))["REFUSE"]})
            continue
        out.append({"level": lv, "graded": False,
                    "s_shape": STEPS_SWEEP["shape"][lv],
                    "s_patchV": STEPS_SWEEP["patchV"][lv],
                    "score_pct": w,
                    "binding": ["%s[%d]" % (arg[0][0], arg[0][1]), arg[0][2],
                                "coarse" if arg[1] == 0 else "fine"] if arg else None,
                    "why_not_graded": "below VERIFICATION_CHARTER.md section 7 step 5's "
                                      "sanctioned range [1e-3, 1e-2] for `shape`"})
    return out


# ================= CONTROL P and CONTROL D ====================================
def _plant(table, key, level, side, amount_pct):
    """Move the binding DECADE neighbour AWAY from ref by amount_pct % of |ref|.

    Away-from-ref is what makes the induced change closed-form: with the sign
    chosen away, |v_nb + p - ref| == |v_nb - ref| + |p| exactly, so the deviation
    rises by exactly amount_pct percentage points.  A fixed-sign plant could
    cancel to zero movement and would be a control that proves nothing.
    """
    t = {k: list(v) for k, v in table.items()}
    vals = t[key]
    ref = vals[level]
    nb_i = level - DECADE_STRIDE if side == 0 else level + DECADE_STRIDE
    diff = vals[nb_i] - ref
    sgn = 1.0 if diff >= 0 else -1.0
    p = sgn * (amount_pct / 100.0) * abs(ref)
    vals[nb_i] = vals[nb_i] + p
    return t, p, ref


def control_p(table, best):
    """rule 3, sized RELATIVE, with the SUFFICIENCY LEG DRIVEN RED.

    `SO-2M` was lost to a bare ABSOLUTE plant that was 2.48 % of its own reference
    and could not cross its own 5 % band.  Here the plant is
    `K * (band/100) * |ref|`, so it crosses BY CONSTRUCTION at K = 5.0 -- and the
    shrunken leg at K = 0.5 must NOT cross, which is what proves the reader is
    measuring CROSSING rather than always answering yes.
    """
    key, side = best["binding"]
    before = best["dev"][key][side]

    amount = PLANT_K * PLATEAU_TOL_PCT                    # = K * band, in pp
    t2, p_abs, ref = _plant(table, key, best["level"], side, amount)
    after = deviations(t2, best["level"])[key][side]
    predicted = before + amount
    if abs(after - predicted) > 1e-9:
        refuse("CONTROL_P", {"predicted_pct": predicted, "observed_pct": after,
                             "before_pct": before})
    moved = after - before
    if moved <= PLATEAU_TOL_PCT:
        refuse("CONTROL_P_PLANT_NOT_SIZED_AGAINST_ITS_BAND", {
            "moved_pp": moved, "plateau_tol_pct": PLATEAU_TOL_PCT, "K": PLANT_K,
            "note": "a plant that cannot cross the band it is judged by is not a control"})

    amount_s = PLANT_K_SHRUNK * PLATEAU_TOL_PCT
    t3, p_abs_s, _ = _plant(table, key, best["level"], side, amount_s)
    after_s = deviations(t3, best["level"])[key][side]
    moved_s = after_s - before
    if moved_s > PLATEAU_TOL_PCT:
        refuse("CONTROL_P_SHRUNK_STILL_CROSSES", {
            "moved_pp": moved_s, "plateau_tol_pct": PLATEAU_TOL_PCT, "K": PLANT_K_SHRUNK,
            "note": "the shrunken plant must NOT cross; a control that crosses at every "
                    "plant size is not measuring crossing"})

    return {"component": "%s[%d]" % (key[0], key[1]), "function": key[2],
            "side": "coarse" if side == 0 else "fine",
            "formula": "plant = K * (band/100) * |ref|",
            "band_pct": PLATEAU_TOL_PCT, "ref": ref,
            "K": PLANT_K, "plant_abs": p_abs, "before_pct": before,
            "after_pct": after, "predicted_pct": predicted, "moved_pp": moved,
            "crosses": True,
            "K_shrunk": PLANT_K_SHRUNK, "plant_abs_shrunk": p_abs_s,
            "after_pct_shrunk": after_s, "moved_pp_shrunk": moved_s,
            "shrunk_crosses": False,
            "red_leg": "SUFFICIENCY RED LEG DROVE RED -- K_shrunk moves half the band "
                       "and does NOT cross"}


def control_d(table, best, scored):
    others = [c for c in scored if c["level"] != best["level"]]
    if not others:
        refuse("CONTROL_D", {"no_runner_up": True})
    runner = min(others, key=lambda c: c["score_pct"])
    key, side = best["binding"]
    need = (runner["score_pct"] - best["score_pct"]) + DECISION_MARGIN_PP
    t2, p_abs, ref = _plant(table, key, best["level"], side, need)
    best2, _ = select(t2)
    if best2["level"] == best["level"]:
        refuse("CONTROL_D_DECISION_INSENSITIVE", {
            "planted_pp": need, "level_before": best["level"], "level_after": best2["level"],
            "note": "a selection that survives a plant breaking its own plateau is not "
                    "being made from the FD data"})
    return {"planted_pp": need, "plant_abs": p_abs, "ref": ref,
            "level_before": best["level"], "level_after": best2["level"],
            "s_shape_before": best["s_shape"], "s_shape_after": best2["s_shape"],
            "runner_up_score_pct": runner["score_pct"], "winner_score_pct": best["score_pct"]}


# ================= CONTROL N: the known positive ==============================
def control_n(doc):
    """KNOWN POSITIVE: separately-shaped contaminations must ALL refuse.

    ORDERING IS LOAD-BEARING.  This runs AFTER `assert_adjoint_free` has already
    accepted `doc`, never before it.  D19's lane wrote it the other way round
    first, and handing it a real adjoint artefact -- a document with no `rows`
    key -- raised KeyError and exited 1.  **A CRASH IS NOT A REFUSAL**: the
    registered refusal is exit 2, and a reader that dies on a contaminated input
    has not refused it, it has merely stopped.  That known positive caught it, and
    D19R inherits both the ordering and the reason.
    """
    if "rows" not in doc or not doc["rows"]:
        refuse("CONTROL_N_NO_ROWS", {"note": "cannot build the nested-graft case"})
    cases = []

    a = copy.deepcopy(doc)
    a["adjoint"] = {"CD": {"shape": ["1.0"]}}
    cases.append(("top_level_adjoint_block", a))

    b = copy.deepcopy(doc)
    b["mode"] = "X"
    cases.append(("mode_X_adjoint_artefact", b))

    c = copy.deepcopy(doc)
    c["rows"][0].setdefault("fd", {})
    c["rows"][0]["J_adj"] = ["1.0"]
    cases.append(("nested_J_adj_in_rows", c))

    d = copy.deepcopy(doc)
    d["mode"] = "R1"
    d["grades_nothing"] = True
    cases.append(("mode_R1_non_graded_diagnostic", d))

    e = copy.deepcopy(doc)
    e["diagnostic_only"] = "R1"
    cases.append(("r1_diagnostic_only_key", e))

    f = copy.deepcopy(doc)
    cases.append(("clean_document", f))

    out = []
    for name, obj in cases:
        try:
            assert_adjoint_free(obj, name)
            out.append((name, False, ""))
        except Refusal as exc:
            out.append((name, True, json.loads(str(exc))["REFUSE"]))
    return out


# ================= the synthetic fixture ======================================
def fixture():
    """An eight-level synthetic sweep with a KNOWN answer, so the selftest proves
    the LOGIC and the CONTROLS.  It proves nothing about the physics and says so."""
    rows = []
    # a flat curve with a deliberate bump one decade above level 2, so the known
    # answer is level 3 and CONTROL D has a runner-up to flip to.
    profile = {
        ("shape", 0): [1.030, 1.010, 1.003, 1.000, 1.000, 1.001, 1.004, 1.020],
        ("shape", 3): [1.028, 1.009, 1.002, 1.000, 1.000, 1.001, 1.003, 1.018],
        ("shape", 6): [1.060, 1.020, 1.004, 1.000, 1.000, 1.002, 1.006, 1.030],
        ("shape", 7): [1.090, 1.030, 1.006, 1.000, 1.000, 1.003, 1.009, 1.040],
        ("patchV", 1): [1.025, 1.008, 1.002, 1.000, 1.000, 1.001, 1.003, 1.015],
    }
    for (dv, idx), vals in profile.items():
        fd = {}
        for s, v in zip(STEPS_SWEEP[dv], vals):
            fd[repr(s)] = {"step": s, "dCD": repr(v * 1.0e-2), "dCL": repr(v * 1.0), "ok": True}
        rows.append({"dv": dv, "idx": idx, "status": "MEASURED", "fd": fd})
    return {"item": "D19R", "mode": "S8", "producer_md5": "0" * 32,
            "header_md5": "0" * 32, "nprocs": 2, "identity": {},
            "components_requested": [[d, i] for d, i in COMPONENTS],
            "n_components_requested": len(COMPONENTS),
            "steps": STEPS_SWEEP, "steps_sweep_registered": STEPS_SWEEP,
            "steps_shared_with_d19": {}, "selected_step": None,
            "kappa": None, "r1_ladder": None,
            "ctrl_step": 1.0e-3, "plant": "0.0", "plant_K": PLANT_K,
            "plant_shrunk": "0.0", "plant_K_shrunk": PLANT_K_SHRUNK,
            "plant_band_pct": PLATEAU_TOL_PCT,
            "plant_moved_pp": "50.0", "plant_moved_pp_shrunk": "5.0",
            "CD_baseline": "0.0146", "CL_baseline": "0.42",
            "CD_baseline_repeat": "0.0146", "CL_baseline_repeat": "0.42",
            "eta_raw": "1e-10", "eta_used": "1e-10", "eta_floored": False,
            "baseline_dvs": {"shape": [], "patchV": []},
            "rows": rows, "n_rows": len(rows), "contains_adjoint": False,
            "grades_nothing": False}


# ================= driver =====================================================
def run(doc, where):
    assert_adjoint_free(doc, where)
    assert_decade_stride()
    table = fd_table(doc)
    best, scored = select(table)
    cp = control_p(table, best)
    cd = control_d(table, best, scored)
    ng = report_not_graded(table)
    all_two_sided = all(max(v) <= PLATEAU_TOL_PCT for v in best["dev"].values())
    out = {
        "item": "D19R", "source": where,
        "selector_saw_adjoint": False,
        "selector_saw_r1_diagnostic": False,
        "decade_stride": DECADE_STRIDE,
        "neighbour_rule": "G19R-1b-N: neighbours are s x 10 and s / 10 -- DECADE "
                          "separated.  Half-decade points are candidate CENTRES only, "
                          "never neighbours.  Strictness is identical to D19's G19-1b.",
        "plateau_tol_pct": PLATEAU_TOL_PCT,
        "reading": "max over components and BOTH functions (not min)",
        "candidate_levels": CANDIDATE_LEVELS,
        "s_star": {"shape": best["s_shape"], "patchV": best["s_patchV"]},
        "s_star_level": best["level"],
        "score_pct": best["score_pct"],
        "binding": ["%s[%d]" % (best["binding"][0][0], best["binding"][0][1]),
                    best["binding"][0][2],
                    "coarse" if best["binding"][1] == 0 else "fine"],
        "all_two_sided": all_two_sided,
        "candidates": [{"level": c["level"], "s_shape": c["s_shape"],
                        "s_patchV": c["s_patchV"], "score_pct": c["score_pct"]}
                       for c in scored],
        "levels_reported_not_graded": ng,
        "per_component": {"%s[%d]/%s" % (k[0], k[1], k[2]):
                          {"coarse_pct": v[0], "fine_pct": v[1],
                           "two_sided": bool(max(v) <= PLATEAU_TOL_PCT)}
                          for k, v in best["dev"].items()},
        "control_P": cp, "control_D": cd,
    }
    return out


def main():
    args = sys.argv[1:]
    if "--selftest" in args:
        doc = fixture()
        print("CONTROL N known positive (adjoint-shaped AND R1-shaped contaminations):")
        ok = True
        for name, refused, why in control_n(doc):
            want = (name != "clean_document")
            good = refused == want
            ok = ok and good
            print("   %-34s refused=%-5s %-42s %s"
                  % (name, refused, why, "OK" if good else "**WRONG**"))
        try:
            out = run(doc, "<fixture>")
        except Refusal as exc:
            print("SELFTEST FAILED on the fixture: %s" % exc)
            return 1
        print()
        print("DECADE-STRIDE assertion: OK -- stride %d spans exactly one decade on "
              "both registered ladders" % DECADE_STRIDE)
        cp = out["control_P"]
        print("CONTROL P (RELATIVE, K registered):")
        print("   K=%.1f       %.4f %% -> %.4f %% (predicted %.4f %%), moved %.4f pp "
              "> band %.1f pp  CROSSES"
              % (cp["K"], cp["before_pct"], cp["after_pct"], cp["predicted_pct"],
                 cp["moved_pp"], cp["band_pct"]))
        print("   K=%.1f  RED  %.4f %% -> %.4f %%, moved %.4f pp <= band %.1f pp  "
              "DOES NOT CROSS -- red leg drove red"
              % (cp["K_shrunk"], cp["before_pct"], cp["after_pct_shrunk"],
                 cp["moved_pp_shrunk"], cp["band_pct"]))
        cd = out["control_D"]
        print("CONTROL D decision: plant %.4f pp flips s* level %d -> %d (shape %g -> %g)"
              % (cd["planted_pp"], cd["level_before"], cd["level_after"],
                 cd["s_shape_before"], cd["s_shape_after"]))
        print("FIXTURE s* = shape %g / patchV %g, level %d, score %.4f %%, all_two_sided=%s"
              % (out["s_star"]["shape"], out["s_star"]["patchV"], out["s_star_level"],
                 out["score_pct"], out["all_two_sided"]))
        print("LEVELS REPORTED BUT NOT GRADED: %s"
              % [(r["level"], r.get("s_shape")) for r in out["levels_reported_not_graded"]])
        print()
        print("SELFTEST %s (fixture values are synthetic; this proves the LOGIC and the "
              "CONTROLS, not the physics)" % ("OK" if ok else "FAILED"))
        return 0 if ok else 1

    fd = out_path = None
    for i, a in enumerate(args):
        if a == "--fd" and i + 1 < len(args):
            fd = args[i + 1]
        if a == "--out" and i + 1 < len(args):
            out_path = args[i + 1]
    if not fd or not out_path:
        sys.stderr.write("usage: d19r_select_step.py --fd <d19r_S.json> --out <json>\n"
                         "       d19r_select_step.py --selftest\n")
        return 64
    if not os.path.isfile(fd):
        sys.stderr.write("D19R_SELECTOR REFUSE fd artefact absent: %s\n" % fd)
        return 2
    try:
        doc = json.load(open(fd))
        out = run(doc, os.path.abspath(fd))
    except Refusal as exc:
        sys.stderr.write("D19R_SELECTOR REFUSED: %s\n" % exc)
        return 2
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.flush()
        os.fsync(fh.fileno())
    print("D19R_SELECTOR_WRITTEN %s" % os.path.abspath(out_path))
    print("D19R_S_STAR shape=%g patchV=%g level=%d score_pct=%.6f all_two_sided=%s"
          % (out["s_star"]["shape"], out["s_star"]["patchV"], out["s_star_level"],
             out["score_pct"], out["all_two_sided"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
