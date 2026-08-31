#!/usr/bin/env python3
"""D19 PHASE 1 -- THE STEP SELECTOR.  ADJOINT-BLIND BY ASSERTION, NOT BY INTENTION.

PREREGISTRATION.md section 5.1, frozen:

    THE SELECTOR RULE, FROZEN.  Among candidate steps, `s*` is the one minimising
    `max` over components and over both functions of the two neighbour deviations.
    Ties break to the LARGER step.  The selector reads only `rows[].fd`.  It is
    handed no adjoint.  `d19_select_step.py` asserts, at entry, that no adjoint
    array is present in its input, and refuses if one is -- so the prohibition is
    enforced by the code and not by the author's intention.

WHY THIS FILE IS NOT `d19_step_table.py`.  The companion reader
`cases/dafoam/ladder-a/A1/curriculum_D19/d19_step_table.py` computes
`rel_err_pct` against `X["adjoint"][of][dv][idx]` (its `analyse()`, line 112).
It READS THE ADJOINT.  It is a REPORTING table and it is NEVER to be reused as
the selector: choosing a step by its agreement with the answer is precisely what
`DAFOAM_CHARTER.md` section 3 forbids -- "Selecting the step after seeing which
one agrees."  What section 3 forbids is selection by agreement with the ADJOINT;
`VERIFICATION_CHARTER.md` section 7 step 1 REQUIRES selection by flatness of the
FD curve.  The two files exist so that the legal reading and the forbidden one
cannot be performed by the same code path.

THREE CONTROLS, ALL REFUSING (CLAUDE.md rule 3).  None of them is decoration:
each gates the emission of a selection, so a selector whose controls fail emits
nothing at all.

  CONTROL N -- NO-ADJOINT, WITH A KNOWN POSITIVE.  The entry assert is a
  WHITELIST on the top-level keys (a blacklist leaks; a whitelist does not) PLUS
  a recursive blacklist scan for adjoint-bearing names at any depth PLUS a
  refusal of the adjoint artefact's own `"mode": "X"` marker.  It is EXERCISED
  against three separately-shaped contaminated inputs and must refuse all three.
  An assert never shown to fire is ceremony.

  CONTROL P -- PLANTED, AND SIZED RELATIVE TO THE QUANTITY IT PERTURBS.  A known
  perturbation is injected into the neighbour value that BINDS the winning
  candidate's score, and the selector's reading must move by the predicted
  amount.  The plant is `PLANT_FRAC` x |ref| -- a FRACTION of the quantity whose
  deviation it moves -- and its sign is chosen AWAY from `ref`, so the induced
  change in the reading is exactly `PLANT_FRAC * 100` percentage points in closed
  form.  It is registered relative and NOT as a bare absolute because a bare
  absolute plant is not sized against any band: SO-2M died on a 1.234e-03
  absolute plant that was 2.48 % of a functional it had never been sized against
  and could not cross its own 5 % band.  Here the control additionally REFUSES
  unless the induced movement EXCEEDS `PLATEAU_TOL_PCT`, i.e. unless the plant is
  big enough to break the very plateau this selector is reading.

  CONTROL D -- DECISION.  A plant large enough to push the winner's score past
  the runner-up's must FLIP `s*`.  CONTROL P proves the reader sees a number
  move; CONTROL D proves the DECISION is driven by that number and is not a
  constant wearing a computation's clothes.

Usage:
    d19_select_step.py --selftest                 # fixture suite, exit 0/2
    d19_select_step.py --fd <d19_S.json> --out <d19_selected_step.json>
"""
import copy
import json
import math
import os
import sys

# ---- registered constants (PREREGISTRATION.md sections 3 and 5) ---------------
STEPS_SWEEP = {
    "shape":  [3.0e-2, 1.0e-2, 1.0e-3, 1.0e-4, 1.0e-5],
    "patchV": [3.0e-1, 1.0e-1, 1.0e-2, 1.0e-3, 1.0e-4],
}
# G19-1b: the candidates are those inside VERIFICATION_CHARTER.md section 7 step 5's
# sanctioned range AND possessing BOTH neighbours in the five-step sweep.  Frozen
# by the registration as an explicit list, so nothing here re-derives them:
#   shape {1e-2, 1e-3}  /  patchV {1e-1, 1e-2}
# They move as a PAIR -- P1 predicts "s* = 1e-2 (shape) / 1e-1 (patchV)" -- so a
# candidate is a LEVEL INDEX into the sweep, not a free per-dv choice.
CANDIDATE_LEVELS = [1, 2]
COMPONENTS = [("shape", 0), ("shape", 3), ("shape", 6), ("shape", 7), ("patchV", 1)]
FUNCTIONS = ["CD", "CL"]
PLATEAU_TOL_PCT = 10.0        # G19-1b, and d15_grade.py:75
NEAR_ZERO_ABS = 1.0e-14       # d15_grade.py:78

# ---- CONTROL P / D constants, RELATIVE by construction ------------------------
PLANT_FRAC = 0.50             # 50 % of |ref| -- 5x the 10.0 pp band it must cross
DECISION_MARGIN_PP = 100.0    # CONTROL D pushes this far past the runner-up

# The EXACT top-level key set `d19_xf.py` writes in modes S and S1.  Anything else
# refuses.  This is the half of CONTROL N that a novel contaminant cannot slip past.
ALLOWED_TOP_KEYS = {
    "item", "mode", "producer_md5", "header_md5", "nprocs", "identity",
    "components_requested", "n_components_requested", "steps",
    "steps_sweep_registered", "steps_shared_with_d15", "selected_step",
    "ctrl_step", "plant", "plant_rel_to_CD_baseline", "CD_baseline", "CL_baseline",
    "CD_baseline_repeat", "CL_baseline_repeat", "eta_raw", "eta_used",
    "eta_floored", "baseline_dvs", "rows", "n_rows", "contains_adjoint",
}
# Defence in depth: names that mean "the answer", at any depth.
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


# ================= CONTROL N: the entry assert ========================================
def assert_adjoint_free(obj, where="<input>"):
    """REFUSE (the caller exits 2) if anything adjoint-shaped is present."""
    if not isinstance(obj, dict):
        refuse("NOT_A_MAPPING", {"where": where, "type": type(obj).__name__})
    extra = sorted(set(obj) - ALLOWED_TOP_KEYS)
    if extra:
        refuse("ADJOINT_ASSERT_TOP_KEY_NOT_WHITELISTED", {
            "where": where, "unexpected_top_level_keys": extra,
            "note": "the selector accepts only the FD sweep artefact's own key set"})
    if obj.get("mode") not in ("S", "S1"):
        refuse("ADJOINT_ASSERT_MODE", {
            "where": where, "mode": obj.get("mode"),
            "note": "mode X is the ADJOINT artefact; the selector never opens it"})
    if obj.get("contains_adjoint") is not False:
        refuse("ADJOINT_ASSERT_SELF_DECLARATION", {
            "where": where, "contains_adjoint": obj.get("contains_adjoint")})

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
            "note": "selecting a step by agreement with the adjoint is DAFOAM_CHARTER section 3's "
                    "forbidden act; the selector refuses rather than reads"})
    return True


# ================= the FD-only reading ================================================
def fd_table(doc):
    """rows[].fd -> {(dv, idx, of): [v0..v4] in sweep order}.  READS NOTHING ELSE."""
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
                    refuse("SWEEP_STEP_FAILED", {"dv": dv, "idx": idx, "step": s,
                                                 "error": hit.get("error")})
                vals.append(float(hit["dCD" if of == "CD" else "dCL"]))
            table[(dv, idx, of)] = vals
    missing = sorted(want - seen)
    if missing:
        refuse("COMPONENT_ABSENT", {"missing": [list(m) for m in missing]})
    return table


def deviations(table, level):
    """Both neighbour deviations, per component and function, at a sweep level."""
    out = {}
    for (dv, idx, of), vals in table.items():
        ref = vals[level]
        if abs(ref) < NEAR_ZERO_ABS:
            refuse("NEAR_ZERO", {"dv": dv, "idx": idx, "of": of, "level": level, "ref": ref})
        out[(dv, idx, of)] = (abs(vals[level - 1] - ref) / abs(ref) * 100.0,
                              abs(vals[level + 1] - ref) / abs(ref) * 100.0)
    return out


def score(table, level):
    """max over components and over BOTH functions of the two neighbour deviations."""
    dev = deviations(table, level)
    worst, arg = -1.0, None
    for key in sorted(dev):
        for side, val in enumerate(dev[key]):
            if val > worst:
                worst, arg = val, (key, side)
    return worst, arg, dev


def select(table):
    """s* = argmin score over candidate LEVELS; ties break to the LARGER step."""
    for lv in CANDIDATE_LEVELS:
        if lv - 1 < 0 or lv + 1 >= len(STEPS_SWEEP["shape"]):
            refuse("CANDIDATE_LACKS_NEIGHBOUR", {"level": lv})
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


# ================= CONTROL P and CONTROL D ============================================
def _plant(table, key, level, side, amount_pct):
    """Move the binding neighbour AWAY from ref by amount_pct % of |ref|.

    Away-from-ref is what makes the induced change closed-form: with the sign
    chosen away, |v_nb + p - ref| == |v_nb - ref| + |p| exactly, so the deviation
    rises by exactly amount_pct percentage points.  A fixed-sign plant could
    cancel to zero movement and would be a control that proves nothing.
    """
    t = {k: list(v) for k, v in table.items()}
    vals = t[key]
    ref = vals[level]
    nb_i = level - 1 if side == 0 else level + 1
    diff = vals[nb_i] - ref
    sgn = 1.0 if diff >= 0 else -1.0
    p = sgn * (amount_pct / 100.0) * abs(ref)
    vals[nb_i] = vals[nb_i] + p
    return t, p, ref


def control_p(table, best):
    key, side = best["binding"]
    before = best["dev"][key][side]
    t2, p_abs, ref = _plant(table, key, best["level"], side, PLANT_FRAC * 100.0)
    after = deviations(t2, best["level"])[key][side]
    predicted = before + PLANT_FRAC * 100.0
    if abs(after - predicted) > 1e-9:
        refuse("CONTROL_P", {"predicted_pct": predicted, "observed_pct": after,
                             "before_pct": before})
    moved = after - before
    if moved <= PLATEAU_TOL_PCT:
        refuse("CONTROL_P_PLANT_NOT_SIZED_AGAINST_ITS_BAND", {
            "moved_pp": moved, "plateau_tol_pct": PLATEAU_TOL_PCT,
            "note": "a plant that cannot cross the band it is judged by is not a control"})
    return {"component": "%s[%d]" % (key[0], key[1]), "function": key[2],
            "side": "coarse" if side == 0 else "fine",
            "plant_frac_of_ref": PLANT_FRAC, "ref": ref, "plant_abs": p_abs,
            "before_pct": before, "after_pct": after, "predicted_pct": predicted,
            "moved_pp": moved, "plateau_tol_pct": PLATEAU_TOL_PCT}


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


def control_n(doc):
    """KNOWN POSITIVE: three separately-shaped contaminations must ALL refuse.

    ORDERING IS LOAD-BEARING.  This runs AFTER `assert_adjoint_free` has already
    accepted `doc`, never before it.  It was written the other way round first,
    and handing it D15's real adjoint artefact `X-P/d15_X.json` -- a document with
    no `rows` key -- raised KeyError and exited 1.  A CRASH IS NOT A REFUSAL: the
    registered refusal is exit 2, and a reader that dies on a contaminated input
    has not refused it, it has merely stopped.  The known positive caught that.
    """
    if "rows" not in doc or not doc["rows"]:
        refuse("CONTROL_N_NO_ROWS", {"note": "cannot build the nested-graft case"})
    cases = []

    a = copy.deepcopy(doc)
    a["adjoint"] = {"CD": {"shape": ["-0.007221766503489129"]}}
    cases.append(("top_level_adjoint_block", a))

    b = copy.deepcopy(doc)
    b["mode"] = "X"
    cases.append(("mode_X_adjoint_artefact", b))

    c = copy.deepcopy(doc)
    # nested BELOW the top level, under a name the whitelist can never see --
    # only the recursive scan catches this one.
    c["rows"][0]["J_adj"] = -0.00020994801762558475
    cases.append(("nested_J_adj_in_rows", c))

    results = []
    for name, bad in cases:
        try:
            assert_adjoint_free(bad, where="<control_n:%s>" % name)
        except Refusal as e:
            results.append({"case": name, "refused": True,
                            "where": json.loads(str(e))["REFUSE"]})
            continue
        refuse("CONTROL_N_ASSERT_DID_NOT_FIRE", {
            "case": name,
            "note": "an adjoint was placed in the selector's input and the entry assert "
                    "accepted it; the adjoint-blindness of this selector is UNPROVEN"})
    # and the clean document must still PASS, or the assert is merely refusing everything
    assert_adjoint_free(doc, where="<control_n:clean>")
    results.append({"case": "clean_document", "refused": False, "where": None})
    return results


# ================= fixture for --selftest =============================================
def fixture():
    """A synthetic FIVE-STEP sweep with the shape of the real artefact.

    Values are invented; this fixture tests the SELECTOR'S LOGIC AND CONTROLS and
    makes no claim about the physics.  Component `shape[7]` is given a real
    cancellation tail so the candidate levels genuinely differ.
    """
    curves = {
        ("shape", 0, "CD"): [-7.30e-3, -7.24e-3, -7.217e-3, -7.175e-3, -6.90e-3],
        ("shape", 0, "CL"): [1.081, 1.0742, 1.0735, 1.0725, 1.061],
        ("shape", 3, "CD"): [9.60e-3, 9.32e-3, 9.291e-3, 9.24e-3, 8.90e-3],
        ("shape", 3, "CL"): [-0.512, -0.5061, -0.5055, -0.5040, -0.494],
        ("shape", 6, "CD"): [-1.452e-2, -1.416e-2, -1.4134e-2, -1.4090e-2, -1.370e-2],
        ("shape", 6, "CL"): [2.121, 2.0912, 2.0901, 2.0880, 2.061],
        ("shape", 7, "CD"): [-2.130e-4, -2.0891e-4, -2.0653e-4, -1.6185e-4, -0.980e-4],
        ("shape", 7, "CL"): [0.4901, 0.48888, 0.48874, 0.48777, 0.4802],
        ("patchV", 1, "CD"): [2.030e-3, 1.9701e-3, 1.9595e-3, 1.9480e-3, 1.880e-3],
        ("patchV", 1, "CL"): [11.31, 11.212, 11.204, 11.191, 11.08],
    }
    rows = []
    for dv, idx in COMPONENTS:
        fd = {}
        for lv, s in enumerate(STEPS_SWEEP[dv]):
            fd[repr(s)] = {"step": s, "ok": True,
                           "dCD": repr(curves[(dv, idx, "CD")][lv]),
                           "dCL": repr(curves[(dv, idx, "CL")][lv]),
                           "CD_plus": repr(0.0), "CD_minus": repr(0.0),
                           "CL_plus": repr(0.0), "CL_minus": repr(0.0)}
        rows.append({"dv": dv, "idx": idx, "status": "MEASURED", "fd": fd})
    rows.append({"dv": "CTRL", "idx": 0, "status": "CONTROL", "fd": {}})
    return {"item": "D19", "mode": "S", "producer_md5": "0" * 32, "header_md5": "0" * 32,
            "nprocs": 2, "identity": {}, "components_requested": [[d, i] for d, i in COMPONENTS],
            "n_components_requested": 5, "steps": STEPS_SWEEP,
            "steps_sweep_registered": STEPS_SWEEP,
            "steps_shared_with_d15": {"shape": [1e-2, 1e-3, 1e-4],
                                      "patchV": [1e-1, 1e-2, 1e-3]},
            "selected_step": None, "ctrl_step": 1e-3, "plant": 1.234e-3,
            "plant_rel_to_CD_baseline": repr(0.0845), "CD_baseline": repr(0.0146),
            "CL_baseline": repr(0.4229), "CD_baseline_repeat": repr(0.0146),
            "CL_baseline_repeat": repr(0.4229), "eta_raw": repr(1.3e-10),
            "eta_used": repr(1.3e-10), "eta_floored": False,
            "baseline_dvs": {"shape": [], "patchV": []},
            "rows": rows, "n_rows": len(rows), "contains_adjoint": False}


# ================= driver =============================================================
def run(doc, where):
    # THE ENTRY ASSERT IS FIRST.  Nothing in this file touches the input before it.
    assert_adjoint_free(doc, where=where)
    # Only then the known positive, which grafts contamination onto a document
    # already known clean and requires the same assert to reject every graft.
    ctrl_n = control_n(doc)
    table = fd_table(doc)
    best, scored = select(table)
    ctrl_p = control_p(table, best)
    ctrl_d = control_d(table, best, scored)
    two_sided = {}
    for key, (nc, nf) in best["dev"].items():
        two_sided["%s[%d]/%s" % (key[0], key[1], key[2])] = {
            "nb_coarse_pct": nc, "nb_fine_pct": nf, "max_pct": max(nc, nf),
            "two_sided": bool(max(nc, nf) <= PLATEAU_TOL_PCT)}
    return {
        "item": "D19", "phase": 1, "selector": "d19_select_step.py",
        "rule": "argmin over candidate levels of max over components and both functions "
                "of the two neighbour deviations; ties to the larger step",
        "selector_saw_adjoint": False,
        "candidate_levels": CANDIDATE_LEVELS,
        "s_star": {"shape": best["s_shape"], "patchV": best["s_patchV"], "level": best["level"]},
        "s_star_score_pct": best["score_pct"],
        "s_star_binding": {"component": "%s[%d]" % (best["binding"][0][0], best["binding"][0][1]),
                           "function": best["binding"][0][2],
                           "side": "coarse" if best["binding"][1] == 0 else "fine"},
        "candidates": [{"level": c["level"], "s_shape": c["s_shape"], "s_patchV": c["s_patchV"],
                        "score_pct": c["score_pct"],
                        "binding": "%s[%d]/%s/%s" % (c["binding"][0][0], c["binding"][0][1],
                                                     c["binding"][0][2],
                                                     "coarse" if c["binding"][1] == 0 else "fine")}
                       for c in scored],
        "plateau_tol_pct": PLATEAU_TOL_PCT,
        "two_sided_at_s_star": two_sided,
        "all_two_sided_at_s_star": all(v["two_sided"] for v in two_sided.values()),
        "controls": {"N_no_adjoint_known_positive": ctrl_n, "P_planted": ctrl_p,
                     "D_decision": ctrl_d},
        "source": where,
    }


def main():
    argv = sys.argv[1:]
    selftest = "--selftest" in argv
    fd_path = out_path = None
    for i, a in enumerate(argv):
        if a == "--fd" and i + 1 < len(argv):
            fd_path = argv[i + 1]
        if a == "--out" and i + 1 < len(argv):
            out_path = argv[i + 1]

    try:
        if selftest:
            r = run(fixture(), "<fixture>")
            print("CONTROL N no-adjoint known positive:")
            for c in r["controls"]["N_no_adjoint_known_positive"]:
                print("   %-28s refused=%-5s %s" % (c["case"], c["refused"], c["where"] or ""))
            p = r["controls"]["P_planted"]
            print("CONTROL P planted (RELATIVE, %.0f %% of |ref| = %.6e):" %
                  (p["plant_frac_of_ref"] * 100, abs(p["plant_abs"])))
            print("   %s/%s %s-side  %.4f %% -> %.4f %% (predicted %.4f %%), moved %.4f pp "
                  "> band %.1f pp" % (p["component"], p["function"], p["side"], p["before_pct"],
                                      p["after_pct"], p["predicted_pct"], p["moved_pp"],
                                      p["plateau_tol_pct"]))
            d = r["controls"]["D_decision"]
            print("CONTROL D decision: plant %.4f pp flips s* level %d -> %d (shape %g -> %g)"
                  % (d["planted_pp"], d["level_before"], d["level_after"],
                     d["s_shape_before"], d["s_shape_after"]))
            print("FIXTURE s* = shape %g / patchV %g, score %.4f %%"
                  % (r["s_star"]["shape"], r["s_star"]["patchV"], r["s_star_score_pct"]))
            print("SELFTEST OK (fixture values are synthetic; this proves the LOGIC and the "
                  "CONTROLS, not the physics)")
            return 0

        if not fd_path or not out_path:
            sys.stderr.write("usage: d19_select_step.py --fd <d19_S.json> --out <sel.json>\n"
                             "       d19_select_step.py --selftest\n")
            return 64
        if not os.path.isfile(fd_path):
            refuse("FD_ARTEFACT_ABSENT", {"path": fd_path})
        doc = json.load(open(fd_path))
        r = run(doc, os.path.abspath(fd_path))
        with open(out_path, "w") as fh:
            json.dump(r, fh, indent=1, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())
        print("D19_SELECTOR_WRITTEN %s" % out_path)
        print("D19_S_STAR shape=%g patchV=%g level=%d score_pct=%.6f all_two_sided=%s"
              % (r["s_star"]["shape"], r["s_star"]["patchV"], r["s_star"]["level"],
                 r["s_star_score_pct"], r["all_two_sided_at_s_star"]))
        return 0
    except Refusal as e:
        sys.stderr.write("D19_SELECTOR REFUSED: %s\n" % e)
        return 2
    except Exception as exc:                                  # noqa: BLE001
        # A comparator REFUSES (exit 2) rather than degrade, and rather than die
        # with a traceback a caller cannot classify.  An unexpected exception on a
        # malformed or hostile input is a refusal, not an exit-1 crash.
        sys.stderr.write("D19_SELECTOR REFUSED: %s\n" % json.dumps(
            {"REFUSE": "UNEXPECTED_EXCEPTION", "detail": {"error": repr(exc)[:400]}},
            sort_keys=True))
        return 2


if __name__ == "__main__":
    sys.exit(main())
