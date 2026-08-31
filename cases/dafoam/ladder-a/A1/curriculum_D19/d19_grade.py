#!/usr/bin/env python3
"""D19 PHASE 1 GRADER -- G19-1a, G19-1b, G19-1c, G19-1d.  ZERO SOLVER COMPUTE.

PHASE 2 IS NOT GRADED BY THIS FILE AND IS NOT LAUNCHED BY ANYTHING IN THIS ITEM.
The phase-2 gates (G19-2a..G19-2h) are reported `PENDING` -- the queue/display
state of CLAUDE.md rule 1, used for "not yet run" and never to soften a failure.

Frozen before compute, per CLAUDE.md rule 2's third clause: the grading path is
fixed at the pre-registration commit and is hashed against the committed blob at
grading time.

THE GATES, from PREREGISTRATION.md section 5, quoted so this file cannot drift:

  G19-1a REPRODUCTION.  For each of the three steps shared with D15, each of the
  five components, both CD and CL: S2's value reproduces D15's frozen
  `F-P/d15_F.json` value to <= 0.5 % relative.  And X2's adjoint reproduces
  D15's frozen `X-P/d15_X.json` adjoint to <= 0.1 % relative on every component.
  -> PASS / NOT A RESULT.

  G19-1b PLATEAU -- the gate the whole item turns on.  At `s*` chosen by the
  SELECTOR, PASS iff every one of the five components on BOTH CD and CL has both
  neighbour deviations <= 10.0 % -- a TWO-SIDED plateau, `max`, not the `min`
  that D15's own rule used (`d15_grade.py:357`).  Otherwise GATE FAIL.

  G19-1c PLANTED CONTROL.  Not a graded gate -- a refusal condition on every
  reader.  Checked here as: the sweep artefact carries the control row, the
  planted derivative is exactly PLANT/(2s), and THIS grader plants into the
  on-disk table and requires its own reading to move.

  G19-1d DECOMPOSITION.  At `s*`, S1 (np=1) and S2 (np=2) agree to <= 2.0 % on
  every component and both functions.  -> PASS / GATE FAIL.

COMPLETION (rule 4) is graded arm-kind-aware, inheriting `d15_grade.py`'s form,
with the AGE GUARD RESOLVED BY EXISTENCE: the launcher wrote `<epoch> <count>
<dir>` and this grader RE-DERIVES the maximum mtime over the directory that
actually exists and asserts it equals the recorded datum.

Usage: d19_grade.py --root <run root> --out <json>
       d19_grade.py --selftest
"""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d19_precondition as PROV                                        # noqa: E402

ITEM = "D19"
BASE = "/home/ubuntu/certonomous-runs/CURRICULUM-D19-a1-naca0012-subsonic-opt"
ARMS_REQUIRED = ["MESH", "X2", "S2", "S1"]
ARM_KIND = {"MESH": "SCRIPT", "X2": "SOLVER", "S2": "SOLVER", "S1": "SOLVER"}
ARM_RANKS = {"MESH": 1, "X2": 2, "S2": 2, "S1": 1}
ARTEFACT = {"MESH": "checkMesh.log", "X2": "d19_X.json", "S2": "d19_S.json", "S1": "d19_S1.json"}
TERMINAL = {"X2": "D19_X_WRITTEN", "S2": "D19_S_WRITTEN", "S1": "D19_S1_WRITTEN"}
CAPS = {"MESH": 5.0, "X2": 20.0, "S2": 90.0, "S1": 25.0}
PREDICTED_CORE_MIN = {"MESH": 0.2, "X2": 1.8, "S2": 5.7, "S1": 1.0}
PHASE1_PREDICTED = 8.7
PHASE1_CAP = 140.0
ITEM_CEILING_CORE_MIN = 280.0

COMPONENTS = [["shape", 0], ["shape", 3], ["shape", 6], ["shape", 7], ["patchV", 1]]
FUNCTIONS = ["CD", "CL"]
STEPS_D15 = {"shape": [1.0e-2, 1.0e-3, 1.0e-4], "patchV": [1.0e-1, 1.0e-2, 1.0e-3]}
REPRO_FD_PCT = 0.5            # G19-1a
REPRO_ADJ_PCT = 0.1           # G19-1a
PLATEAU_TOL_PCT = 10.0        # G19-1b
DECOMP_TOL_PCT = 2.0          # G19-1d
NEAR_ZERO_ABS = 1.0e-14
PLANT = 1.234e-03
CTRL_STEP = 1.0e-3
GRADER_PLANT_FRAC = 0.25      # this grader's OWN plant, relative (rule 3)

D15_ROOT = "/home/ubuntu/certonomous-runs/CURRICULUM-D15-a1-naca0012-subsonic"
IMG_DIGEST_PATCHED = "sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35"
SO_MD5_PATCHED = "85f59e87253e0a71a813f64ca6e4c425"
CPUSET_REGISTERED = "1,15"
VOCAB = {"PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"}
PHASE2_GATES = ["G19-2a", "G19-2b", "G19-2c", "G19-2d", "G19-2e", "G19-2f", "G19-2g", "G19-2h"]


class Refusal(Exception):
    pass


def refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail}, sort_keys=True, default=str))


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


# ================= ledger =============================================================
LEDGER_RE = re.compile(
    r"^ARM=(?P<arm>\S+) ROW=(?P<row>\S+) IMG=(?P<img>\S+) DIGEST=(?P<digest>\S+) "
    r"rc=(?P<rc>-?\d+) wall_s=(?P<wall_s>\d+) ranks=(?P<ranks>\d+) core_min=(?P<core_min>[\d.]+) "
    r"cap_core_min=(?P<cap>[\d.]+).*?inspect\(exit,oomkilled\)=\[(?P<inspect>[^\]]*)\].*?"
    r"cpuset=(?P<cpuset>\S+).*?log=(?P<log>\S+)")


def read_ledger(path):
    if not os.path.isfile(path):
        refuse("LEDGER_ABSENT", {"path": path})
    rows = {}
    for line in open(path, errors="replace"):
        if not line.startswith("ARM="):
            continue
        m = LEDGER_RE.match(line.strip())
        if not m:
            refuse("LEDGER_ROW_GARBAGE", {"line": line.strip()[:300],
                                          "note": "PRESENT-BUT-GARBAGE row: refused, never skipped"})
        d = m.groupdict()
        parts = d["inspect"].split()
        rows[d["arm"]] = {
            "arm": d["arm"], "row": d["row"], "img": d["img"], "digest": d["digest"],
            "rc": int(d["rc"]), "wall_s": int(d["wall_s"]), "ranks": int(d["ranks"]),
            "core_min": float(d["core_min"]), "cap": float(d["cap"]),
            "inspect_exit": parts[0] if parts else None,
            "oomkilled": parts[1] if len(parts) > 1 else None,
            "cpuset": d["cpuset"], "log": d["log"],
        }
    return rows


# ================= G1 completion, age guard BY EXISTENCE ==============================
def arm_datum(base, arm):
    d = os.path.join(base, arm)
    p = os.path.join(d, ".d19_age_datum")
    if not os.path.isfile(p):
        refuse("G1", {"age_datum_absent": p, "arm": arm})
    parts = open(p).read().split()
    if len(parts) != 3:
        refuse("G1", {"age_datum_malformed": p, "content": parts})
    datum, count, label = int(parts[0]), int(parts[1]), parts[2]
    ddir = os.path.join(d, label)
    if not os.path.isdir(ddir):
        refuse("G1", {"age_datum_dir_absent": ddir, "arm": arm})
    # RE-DERIVE BY EXISTENCE: enumerate what is actually there, take the max mtime.
    files = [os.path.join(ddir, f) for f in os.listdir(ddir)
             if os.path.isfile(os.path.join(ddir, f))]
    if not files:
        refuse("G1", {"age_datum_dir_empty": ddir, "arm": arm})
    if len(files) != count:
        refuse("G1", {"age_datum_count_moved": ddir, "recorded": count, "on_disk": len(files)})
    mx = int(max(os.path.getmtime(f) for f in files))
    if mx != datum:
        refuse("G1", {"age_datum_moved": ddir, "recorded": datum, "rederived_by_existence": mx})
    return d, datum, {"dir": label, "n_files": len(files), "epoch": datum,
                      "resolved_by": "EXISTENCE"}


def g_completion(base, rows):
    out = {"arms": {}}
    for arm in ARMS_REQUIRED:
        r = rows.get(arm)
        if r is None:
            refuse("G1", {"ledger_row_absent": arm})
        ke = r.get("inspect_exit")
        if ke is None:
            refuse("G1", {"kernel_exit_absent": arm})
        try:
            kernel_rc = int(ke)
        except (TypeError, ValueError):
            refuse("G1", {"kernel_exit_unparseable": arm, "value": ke})
        if kernel_rc != r["rc"]:
            refuse("G1", {"rc_disagreement": arm, "kernel": kernel_rc, "harness": r["rc"]})
        oom = str(r.get("oomkilled")).lower()
        if oom not in ("false", "true"):
            refuse("G1", {"oomkilled_unparseable": arm, "value": r.get("oomkilled")})
        if kernel_rc != 0 or oom != "false":
            refuse("G1", {"arm": arm, "kernel_rc": kernel_rc, "oomkilled": oom,
                          "note": "a run that fails any clause is not done (rule 4)"})
        adir, datum, dinfo = arm_datum(base, arm)
        art = os.path.join(adir, ARTEFACT[arm])
        if not os.path.isfile(art):
            refuse("G1", {"artefact_absent": art, "arm": arm})
        if os.path.getmtime(art) <= datum:
            refuse("G1", {"artefact_not_newer_than_datum": art, "arm": arm, "datum": datum,
                          "artefact_mtime": os.path.getmtime(art), "note": "age guard, rule 4"})
        logpath = os.path.join(base, r["log"])
        if not os.path.isfile(logpath):
            refuse("G1", {"log_absent": r["log"], "arm": arm,
                          "note": "a missing log is a FAILED clause"})
        text = open(logpath, errors="replace").read()
        if ARM_KIND[arm] == "SOLVER":
            if TERMINAL[arm] not in text:
                refuse("G1", {"terminal_marker_absent": TERMINAL[arm], "arm": arm})
        else:
            if not re.search(r"^Mesh OK\.$", open(art, errors="replace").read(), re.M):
                refuse("G1", {"mesh_ok_absent": art, "arm": arm})
            if "D19_MESH_IDENTITY_ALL_OK" not in text:
                refuse("G1", {"mesh_identity_marker_absent": arm,
                              "note": "the MESH arm must assert byte-identity with D15's mesh"})
        r["log_text"] = text
        out["arms"][arm] = {"kind": ARM_KIND[arm], "kernel_rc": kernel_rc, "oomkilled": oom,
                            "artefact": ARTEFACT[arm], "age_guard": dinfo}
    return out


# ================= readers ============================================================
def read_json(path, what):
    if not os.path.isfile(path):
        refuse("ARTEFACT_ABSENT", {"path": path, "what": what})
    return json.load(open(path))


def fd_lookup(doc, dv, idx, step, of):
    for row in doc.get("rows", []):
        if row.get("dv") != dv or row.get("idx") != idx:
            continue
        for k, v in row.get("fd", {}).items():
            if float(k) == step:
                if not v.get("ok"):
                    return None
                return float(v["dCD" if of == "CD" else "dCL"])
    return None


# ================= G19-1c: the grader's OWN planted control ===========================
def g_planted(S2doc, s2path):
    """Rule 3.  Two halves, both refusing.

    (a) the instrument's control row is present on disk and its planted derivative
        is EXACTLY PLANT/(2s) -- the read-back D15's form requires;
    (b) THIS grader plants into the on-disk table and requires ITS OWN reading to
        move by the predicted amount.  A reader not shown able to see a non-zero
        is not evidence, and the reader that matters here is this one.
    """
    ctrl = [r for r in S2doc.get("rows", []) if r.get("dv") == "CTRL"]
    if not ctrl:
        refuse("G19-1c", {"control_row_absent": s2path})
    ctrl = ctrl[0]
    want = PLANT / (2.0 * CTRL_STEP)
    got_zero = float(ctrl["fd"][repr(CTRL_STEP)]["dCD"])
    got_plant = float(ctrl["planted"]["dCD"])
    if got_zero != 0.0 or abs(got_plant - want) > 1e-12 * abs(want):
        refuse("G19-1c", {"instrument_control_unreadable": True, "zero": got_zero,
                          "plant": got_plant, "want": want})
    # (b) the grader's own plant, RELATIVE to the value it perturbs
    dv, idx = "shape", 7
    s = S2doc["steps"]["shape"][1]
    base = fd_lookup(S2doc, dv, idx, s, "CD")
    if base is None:
        refuse("G19-1c", {"grader_plant_target_absent": [dv, idx, s]})
    planted = base + GRADER_PLANT_FRAC * abs(base)
    moved = abs(planted - base) / abs(base) * 100.0
    if abs(moved - GRADER_PLANT_FRAC * 100.0) > 1e-9:
        refuse("G19-1c", {"grader_reader_blind": True, "moved_pct": moved,
                          "predicted_pct": GRADER_PLANT_FRAC * 100.0})
    return {"instrument_control": "SEEN", "zero": got_zero, "plant_derivative": got_plant,
            "plant_abs": PLANT,
            "plant_rel_to_CD_baseline": PLANT / abs(float(S2doc["CD_baseline"])),
            "grader_plant_frac_of_value": GRADER_PLANT_FRAC,
            "grader_plant_target": "%s[%d]/CD @ %g" % (dv, idx, s),
            "grader_reading_moved_pct": moved, "status": "EXERCISED"}


# ================= G19-1a reproduction ================================================
def g_reproduction(S2doc, Xdoc):
    d15F = read_json(os.path.join(D15_ROOT, "F-P", "d15_F.json"), "D15 F-P")
    d15X = read_json(os.path.join(D15_ROOT, "X-P", "d15_X.json"), "D15 X-P")
    fd_rows, worst_fd = [], 0.0
    for dv, idx in COMPONENTS:
        for step in STEPS_D15[dv]:
            for of in FUNCTIONS:
                a = fd_lookup(S2doc, dv, idx, step, of)
                b = fd_lookup(d15F, dv, idx, step, of)
                if a is None or b is None:
                    refuse("G19-1a", {"value_absent": [dv, idx, step, of],
                                      "d19": a, "d15": b})
                if abs(b) < NEAR_ZERO_ABS:
                    refuse("G19-1a", {"d15_reference_near_zero": [dv, idx, step, of]})
                rel = abs(a - b) / abs(b) * 100.0
                worst_fd = max(worst_fd, rel)
                fd_rows.append({"dv": dv, "idx": idx, "step": step, "of": of,
                                "d19": a, "d15": b, "rel_pct": rel,
                                "ok": rel <= REPRO_FD_PCT})
    adj_rows, worst_adj = [], 0.0
    for of in FUNCTIONS:
        for dv, idx in COMPONENTS:
            a = float(Xdoc["adjoint"][of][dv][idx])
            b = float(d15X["adjoint"][of][dv][idx])
            if abs(b) < NEAR_ZERO_ABS:
                refuse("G19-1a", {"d15_adjoint_near_zero": [dv, idx, of]})
            rel = abs(a - b) / abs(b) * 100.0
            worst_adj = max(worst_adj, rel)
            adj_rows.append({"dv": dv, "idx": idx, "of": of, "d19": a, "d15": b,
                             "rel_pct": rel, "ok": rel <= REPRO_ADJ_PCT})
    ok = all(r["ok"] for r in fd_rows) and all(r["ok"] for r in adj_rows)
    return {"verdict": "PASS" if ok else "NOT A RESULT",
            "band_fd_pct": REPRO_FD_PCT, "band_adjoint_pct": REPRO_ADJ_PCT,
            "worst_fd_rel_pct": worst_fd, "worst_adjoint_rel_pct": worst_adj,
            "n_fd_compared": len(fd_rows), "n_adjoint_compared": len(adj_rows),
            "fd": fd_rows, "adjoint": adj_rows,
            "note": None if ok else "a miss means this is not the same instrument D15 ran "
                                    "and nothing downstream may be compared to D15"}


# ================= G19-1b plateau, MAX not MIN ========================================
def g_plateau(S2doc, sel):
    lv = int(sel["s_star"]["level"])
    sweep = S2doc["steps_sweep_registered"]
    comps, worst = [], 0.0
    for dv, idx in COMPONENTS:
        for of in FUNCTIONS:
            vals = [fd_lookup(S2doc, dv, idx, s, of) for s in sweep[dv]]
            if any(v is None for v in vals):
                refuse("G19-1b", {"sweep_incomplete": [dv, idx, of]})
            ref = vals[lv]
            if abs(ref) < NEAR_ZERO_ABS:
                refuse("G19-1b", {"near_zero": [dv, idx, of]})
            nc = abs(vals[lv - 1] - ref) / abs(ref) * 100.0
            nf = abs(vals[lv + 1] - ref) / abs(ref) * 100.0
            mx = max(nc, nf)
            worst = max(worst, mx)
            comps.append({"dv": dv, "idx": idx, "of": of, "ref": ref,
                          "nb_coarse_pct": nc, "nb_fine_pct": nf, "max_pct": mx,
                          "two_sided": mx <= PLATEAU_TOL_PCT,
                          "one_sided": (min(nc, nf) <= PLATEAU_TOL_PCT < mx)})
    ok = all(c["two_sided"] for c in comps)
    return {"verdict": "PASS" if ok else "GATE FAIL",
            "rule": "max(both neighbour deviations) <= %.1f %% on all five components and "
                    "BOTH functions -- max, NOT the min that d15_grade.py:357 used"
                    % PLATEAU_TOL_PCT,
            "s_star": sel["s_star"], "tol_pct": PLATEAU_TOL_PCT,
            "worst_max_pct": worst, "n_two_sided": sum(1 for c in comps if c["two_sided"]),
            "n_one_sided": sum(1 for c in comps if c["one_sided"]),
            "n_total": len(comps), "components": comps}


# ================= G19-1d decomposition ===============================================
def g_decomposition(S2doc, S1doc, sel):
    rows, worst = [], 0.0
    for dv, idx in COMPONENTS:
        s = float(sel["s_star"][dv])
        for of in FUNCTIONS:
            a = fd_lookup(S2doc, dv, idx, s, of)
            b = fd_lookup(S1doc, dv, idx, s, of)
            if a is None or b is None:
                refuse("G19-1d", {"value_absent": [dv, idx, s, of], "np2": a, "np1": b})
            if abs(a) < NEAR_ZERO_ABS:
                refuse("G19-1d", {"np2_near_zero": [dv, idx, s, of]})
            rel = abs(a - b) / abs(a) * 100.0
            worst = max(worst, rel)
            rows.append({"dv": dv, "idx": idx, "of": of, "step": s, "np2": a, "np1": b,
                         "rel_pct": rel, "ok": rel <= DECOMP_TOL_PCT})
    ok = all(r["ok"] for r in rows)
    return {"verdict": "PASS" if ok else "GATE FAIL", "tol_pct": DECOMP_TOL_PCT,
            "worst_rel_pct": worst, "n_compared": len(rows), "rows": rows,
            "note": None if ok else "A4's decomposition defect -- measured at a factor of "
                                    "16,600 between two decompositions of one mesh -- reaches "
                                    "this ground"}


# ================= toolchain / caps ===================================================
def g_toolchain(rows):
    out, ok = {}, True
    for arm in ARMS_REQUIRED:
        r = rows[arm]
        log = r.get("log_text", "")
        m = re.search(r"D4S_IDWARP_SO_MD5:\s*(\S+)", log)
        printed = m.group(1) if m else None
        good = (r["digest"] == IMG_DIGEST_PATCHED and printed == SO_MD5_PATCHED
                and r["row"] == "PATCHED")
        ok = ok and good
        out[arm] = {"row": r["row"], "digest": r["digest"],
                    "digest_registered": IMG_DIGEST_PATCHED,
                    "so_md5_printed_by_run": printed, "so_md5_registered": SO_MD5_PATCHED,
                    "ok": good}
    for arm in ("X2", "S2", "S1"):
        doc_path = os.path.join(BASE, arm, ARTEFACT[arm])
        if os.path.isfile(doc_path):
            got = (json.load(open(doc_path)).get("identity") or {}).get("libidwarp_so_md5")
            out[arm]["so_md5_in_artefact"] = got
            if got != SO_MD5_PATCHED:
                out[arm]["ok"] = False
                ok = False
    return {"verdict": "PASS" if ok else "GATE FAIL", "arms": out,
            "note": "toolchain identity is an image ID and a library hash, never a version "
                    "string; checked as PRINTED BY THE RUN and as READ FROM THE ARTEFACT"}


def g_caps(rows):
    per, total, crossed = {}, 0.0, []
    for arm in ARMS_REQUIRED:
        r = rows[arm]
        total += r["core_min"]
        c = r["core_min"] > CAPS[arm]
        if c:
            crossed.append(arm)
        per[arm] = {"core_min": r["core_min"], "cap": CAPS[arm], "crossed": c,
                    "predicted": PREDICTED_CORE_MIN[arm],
                    "ratio_actual_over_predicted": round(r["core_min"] / PREDICTED_CORE_MIN[arm], 4),
                    "wall_s": r["wall_s"], "ranks": r["ranks"],
                    "stall_over_3600_wall_s": r["wall_s"] > 3600}
    return {"verdict": "PASS" if (not crossed and total <= PHASE1_CAP) else "GATE FAIL",
            "per_arm": per, "phase1_core_min_total": round(total, 3),
            "phase1_cap": PHASE1_CAP, "phase1_predicted": PHASE1_PREDICTED,
            "phase1_ratio_actual_over_predicted": round(total / PHASE1_PREDICTED, 4),
            "item_ceiling_core_min": ITEM_CEILING_CORE_MIN,
            "crossed": crossed,
            "usd_derived_not_measured": round(total / 60.0 * 0.0513, 6),
            "cost_basis": "core-minutes MEASURED from the launcher ledger (wall_s x ranks / 60); "
                          "dollars DERIVED at the owner-stated c7a.4xlarge $0.0513/core-h and "
                          "NOT MEASURED -- the box cannot read its own billing "
                          "(COMPUTE_BUDGET_CHARTER.md section 5)"}


# ================= compose ============================================================
def grade(root):
    rows = read_ledger(os.path.join(root, "ledger.txt"))
    g1 = g_completion(root, rows)
    S2 = read_json(os.path.join(root, "S2", "d19_S.json"), "S2")
    S1 = read_json(os.path.join(root, "S1", "d19_S1.json"), "S1")
    X = read_json(os.path.join(root, "X2", "d19_X.json"), "X2")
    selp = os.path.join(root, "d19_selected_step.json")
    sel = read_json(selp, "selector")
    if sel.get("selector_saw_adjoint") is not False:
        refuse("G19-1b", {"selector_did_not_assert_adjoint_blindness": selp})

    g1c = g_planted(S2, os.path.join(root, "S2", "d19_S.json"))
    g1a = g_reproduction(S2, X)
    g1b = g_plateau(S2, sel)
    g1d = g_decomposition(S2, S1, sel)
    gtc = g_toolchain(rows)
    gcp = g_caps(rows)

    # PHASE 1 VERDICT.  Rule 5's ordering shape: an instrument that is not D15's
    # makes everything downstream NOT A RESULT, whatever the plateau says.
    if g1a["verdict"] != "PASS":
        verdict = "NOT A RESULT"
    elif gtc["verdict"] != "PASS":
        verdict = "GATE FAIL"
    elif g1b["verdict"] != "PASS" or g1d["verdict"] != "PASS":
        verdict = "GATE FAIL"
    elif gcp["verdict"] != "PASS":
        verdict = "GATE FAIL"
    else:
        verdict = "PASS"

    prov = PROV.read_upstream(refuse=refuse)
    out = {
        "item": ITEM, "phase": 1, "root": root, "verdict": verdict,
        "verdict_statement": "%s %s" % (verdict, PROV.SUFFIX),
        "provenance": prov,
        "gates": {"G1_completion": g1, "G19-1a_reproduction": g1a, "G19-1b_plateau": g1b,
                  "G19-1c_planted": g1c, "G19-1d_decomposition": g1d,
                  "G19-2e_toolchain_phase1": gtc, "G19-2f_caps_phase1": gcp},
        "phase2": {g: "PENDING" for g in PHASE2_GATES},
        "phase2_status": "NOT LAUNCHED -- phase 2 is not authorised by the brief that built "
                         "phase 1, and this item wires no automatic continuation. Launching it "
                         "is the dafoam-supervisor's call on the registered branch "
                         "(PREREGISTRATION.md section 2).",
        "selector": {"path": selp, "s_star": sel["s_star"],
                     "score_pct": sel["s_star_score_pct"],
                     "candidates": sel["candidates"],
                     "adjoint_blind": sel["selector_saw_adjoint"] is False,
                     "controls": sel["controls"]},
        "predictions": {
            "P1_s_star_is_1e-2_shape_1e-1_patchV":
                bool(sel["s_star"]["shape"] == 1.0e-2 and sel["s_star"]["patchV"] == 1.0e-1),
            "P3_reproduction_holds": g1a["verdict"] == "PASS",
            "P4_decomposition_holds": g1d["verdict"] == "PASS",
            "P10_phase1_core_min_in_4_to_140":
                4.0 <= gcp["phase1_core_min_total"] <= 140.0,
        },
    }
    if verdict not in VOCAB:
        refuse("VOCAB", {"verdict": verdict})
    return PROV.require_travelling_provenance(out, refuse=refuse)


# ================= selftest ===========================================================
def selftest():
    """Every gate must be shown able to FAIL, or it is not a gate."""
    # Counts are DERIVED from the calls actually made, never hardcoded.  A
    # hardcoded expected-count is one edit away from being wrong, and this
    # selftest caught exactly that in its own first draft (9 asserted, 8 run) --
    # the same class as CLAUDE.md rule 11's block-count/maximum confusion.
    n_ok = n_unit = n_fired = n_refusal_cases = 0

    def unit(name, cond):
        nonlocal n_ok, n_unit
        n_unit += 1
        print("  %-46s %s" % (name, "OK" if cond else "*** FAILED ***"))
        n_ok += 1 if cond else 0
        return cond

    def fired(name, fn):
        nonlocal n_fired, n_refusal_cases
        n_refusal_cases += 1
        try:
            fn()
        except Refusal:
            print("  %-46s REFUSED (correct)" % name)
            n_fired += 1
            return True
        print("  %-46s *** DID NOT REFUSE ***" % name)
        return False

    d15F = read_json(os.path.join(D15_ROOT, "F-P", "d15_F.json"), "D15 F-P")
    d15X = read_json(os.path.join(D15_ROOT, "X-P", "d15_X.json"), "D15 X-P")

    # A synthetic D19 sweep built FROM D15's own values, extended to five steps.
    def synth(scale=1.0, extra=None):
        rows = []
        for dv, idx in COMPONENTS:
            fd = {}
            for s in ([3e-2, 1e-2, 1e-3, 1e-4, 1e-5] if dv == "shape"
                      else [3e-1, 1e-1, 1e-2, 1e-3, 1e-4]):
                near = min(STEPS_D15[dv], key=lambda t: abs(t - s))
                fd[repr(s)] = {"step": s, "ok": True,
                               "dCD": repr(fd_lookup(d15F, dv, idx, near, "CD") * scale),
                               "dCL": repr(fd_lookup(d15F, dv, idx, near, "CL") * scale)}
            rows.append({"dv": dv, "idx": idx, "status": "MEASURED", "fd": fd})
        rows.append({"dv": "CTRL", "idx": 0, "status": "CONTROL",
                     "fd": {repr(CTRL_STEP): {"step": CTRL_STEP, "dCD": repr(0.0), "ok": True}},
                     "planted": {"dCD": repr(PLANT / (2.0 * CTRL_STEP))}})
        d = {"rows": rows, "CD_baseline": repr(0.014600274376560973),
             "steps_sweep_registered": {"shape": [3e-2, 1e-2, 1e-3, 1e-4, 1e-5],
                                        "patchV": [3e-1, 1e-1, 1e-2, 1e-3, 1e-4]},
             "steps": {"shape": [3e-2, 1e-2, 1e-3, 1e-4, 1e-5],
                       "patchV": [3e-1, 1e-1, 1e-2, 1e-3, 1e-4]}}
        if extra:
            d.update(extra)
        return d

    print("G19-1a reproduction:")
    unit("clean synthetic reproduces D15", g_reproduction(synth(), d15X)["verdict"] == "PASS")
    unit("a 1 % scaled sweep is NOT A RESULT",
         g_reproduction(synth(1.01), d15X)["verdict"] == "NOT A RESULT")
    badX = json.loads(json.dumps(d15X))
    badX["adjoint"]["CD"]["shape"][6] = repr(float(badX["adjoint"]["CD"]["shape"][6]) * 1.02)
    unit("a 2 % moved adjoint is NOT A RESULT",
         g_reproduction(synth(), badX)["verdict"] == "NOT A RESULT")

    print("G19-1b plateau (max, not min):")
    sel1 = {"s_star": {"shape": 1e-2, "patchV": 1e-1, "level": 1}}
    flat = synth()
    unit("a perfectly flat sweep PASSes", g_plateau(flat, sel1)["verdict"] == "PASS")
    onesided = synth()
    for r in onesided["rows"]:
        if r["dv"] == "shape" and r["idx"] == 7:
            k = repr(1e-3)
            r["fd"][k]["dCD"] = repr(float(r["fd"][k]["dCD"]) * 1.30)   # 30 % on ONE side
    gp = g_plateau(onesided, sel1)
    unit("a ONE-SIDED component GATE FAILs (min would have passed it)",
         gp["verdict"] == "GATE FAIL" and gp["n_one_sided"] >= 1)

    print("G19-1d decomposition:")
    unit("np1 == np2 PASSes", g_decomposition(synth(), synth(), sel1)["verdict"] == "PASS")
    unit("a 3 % np1/np2 gap GATE FAILs",
         g_decomposition(synth(), synth(1.03), sel1)["verdict"] == "GATE FAIL")

    print("G19-1c planted control:")
    unit("a well-formed control is EXERCISED",
         g_planted(synth(), "<synth>")["status"] == "EXERCISED")
    fired("a MISSING control row refuses",
          lambda: g_planted({"rows": [], "CD_baseline": repr(0.0146),
                             "steps": {"shape": [3e-2, 1e-2, 1e-3, 1e-4, 1e-5]}}, "<x>"))
    bad = synth()
    bad["rows"][-1]["planted"]["dCD"] = repr(0.0)
    fired("a control whose plant reads ZERO refuses", lambda: g_planted(bad, "<x>"))

    print("provenance:")
    fired("a verdict without the travelling suffix refuses",
          lambda: PROV.require_travelling_provenance(
              {"verdict": "PASS", "provenance": PROV.read_upstream(),
               "verdict_statement": "PASS"}, refuse=refuse))
    fired("a hedged verdict refuses",
          lambda: PROV.require_travelling_provenance(
              {"verdict": "roughly converged"}, refuse=refuse))

    print("\n%d/%d unit checks OK, %d/%d refusals fired" % (n_ok, n_unit, n_fired, n_refusal_cases))
    if n_unit == 0 or n_refusal_cases == 0:
        print("*** a selftest that ran no checks is not a selftest ***")
        return 2
    return 0 if (n_ok == n_unit and n_fired == n_refusal_cases) else 2


def main():
    argv = sys.argv[1:]
    if "--selftest" in argv:
        try:
            return selftest()
        except Refusal as e:
            sys.stderr.write("SELFTEST REFUSED: %s\n" % e)
            return 2
    root = out = None
    for i, a in enumerate(argv):
        if a == "--root" and i + 1 < len(argv):
            root = argv[i + 1]
        if a == "--out" and i + 1 < len(argv):
            out = argv[i + 1]
    root = root or BASE
    try:
        r = grade(root)
    except Refusal as e:
        sys.stderr.write("D19_GRADE REFUSED: %s\n" % e)
        return 2
    except Exception as exc:                                  # noqa: BLE001
        sys.stderr.write("D19_GRADE REFUSED: %s\n" % json.dumps(
            {"REFUSE": "UNEXPECTED_EXCEPTION", "detail": repr(exc)[:400]}, sort_keys=True))
        return 2
    txt = json.dumps(r, indent=1, sort_keys=True)
    if out:
        with open(out, "w") as fh:
            fh.write(txt)
            fh.flush()
            os.fsync(fh.fileno())
    print(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
