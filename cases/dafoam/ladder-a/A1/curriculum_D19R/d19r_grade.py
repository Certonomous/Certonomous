#!/usr/bin/env python3
r"""Curriculum D19R PHASE 1 GRADER.

FROZEN BEFORE COMPUTE.  `CLAUDE.md` rule 2's third clause fixes the grading path
at the pre-registration commit and requires the frozen file to be hashed against
the committed blob at grading time.  This file is that path.

THE GATES (PREREGISTRATION.md section 5), and nothing outside them:

  G19R-1a  REPRODUCTION.  On the FIVE levels shared with D19, all five
           components, both functions: `S8` reproduces D19's `S2/d19_S.json` to
           <= 0.5 %; and `X2`'s adjoint reproduces D19's `X2/d19_X.json` to
           <= 0.1 %.  -> PASS / NOT A RESULT.

  G19R-1b  PLATEAU -- the gate the item turns on.  At `s*`, PASS iff EVERY one of
           the five components on BOTH functions has both DECADE-separated
           neighbour deviations <= 10.0 %.  `max`, NOT `min`.
           **THE RULE IS D19's, UNCHANGED.  `shape[7]` IS NOT EXCLUDED AND NO
           EXEMPTION EXISTS.**  Verified against D19's real data before freeze:
           this decade rule reproduces D19's own registered `score_pct=21.629866`
           at the level D19 graded, so it is provably not a relaxation.

  G19R-1c  PLANTED CONTROL, SIZED RELATIVE (rule 3).  Not a graded gate -- a
           refusal condition on every reader.  plant = K * (band/100) * |d_ref|,
           K = 5.0, plus the SUFFICIENCY RED LEG at K_shrunk = 0.5 which must NOT
           cross.  `SO-2M` was lost to a bare absolute plant that was 2.48 % of
           its own reference and could not cross its own 5 % band.

  G19R-1d  DECOMPOSITION.  At `s*`, `S1` (np=1) and `S8` (np=2) agree to <= 2.0 %
           on every component and both functions.  -> PASS / GATE FAIL.
           This is ALSO the live re-test of D19's `0/U` bound (section 3 of the
           pre-registration): D19 measured worst 0.041027 % on this exact pair.

  G19R-1e  FLAGGED-COMPONENT DISPOSITION (`DAFOAM_CHARTER.md` section 3).
           **EVIDENCE, NEVER A VERDICT, AND IT CANNOT LAUNCH PHASE 2.**

  G19R-1f  TOOLCHAIN.  Image digest AND `.so` md5, as printed by the run and as
           read from the artefact.  G19R-1g CAPS.  G19R-1h COMPLETION (rule 4, as
           repaired -- `d19r_age_guard`).  G19R-1i TRAVELLING PROVENANCE.

WHAT THIS GRADER WILL NOT DO
============================
It will not relax a threshold, exclude a component from `G19R-1b`, or convert a
`GATE FAIL` into anything softer.  `V-NOPLATEAU` is a REGISTERED RESULT LABEL
that travels BESIDE the `GATE FAIL` verdict; it never replaces it.  Gate design
is reserved to Sanaa (`CLAUDE.md` rule 9).

Usage: d19r_grade.py --root <run root> --out <json>
       d19r_grade.py --selftest
"""
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d19r_precondition as PROV                                      # noqa: E402
import d19r_age_guard as AGE                                          # noqa: E402

ITEM = "D19R"
BASE = "/home/ubuntu/certonomous-runs/CURRICULUM-D19R-a1-naca0012-subsonic-plateau"
D19_ROOT = "/home/ubuntu/certonomous-runs/CURRICULUM-D19-a1-naca0012-subsonic-opt"

ARMS_REQUIRED = ["MESH", "X2", "S8", "N2", "S1", "R1"]
ARM_KIND = {"MESH": "SCRIPT", "X2": "SOLVER", "S8": "SOLVER",
            "N2": "SOLVER", "S1": "SOLVER", "R1": "SOLVER"}
ARM_RANKS = {"MESH": 1, "X2": 2, "S8": 2, "N2": 2, "S1": 1, "R1": 1}
ARTEFACT = {"MESH": "checkMesh.log", "X2": "d19r_X.json", "S8": "d19r_S.json",
            "N2": "d19r_N.json", "S1": "d19r_S1.json", "R1": "d19r_R1.json"}
TERMINAL = {"X2": "D19R_X_WRITTEN", "S8": "D19R_S8_WRITTEN", "N2": "D19R_N2_WRITTEN",
            "S1": "D19R_S1_WRITTEN", "R1": "D19R_R1_WRITTEN"}
CAPS = {"MESH": 5.0, "X2": 20.0, "S8": 40.0, "N2": 10.0, "S1": 10.0, "R1": 8.0}
PREDICTED_CORE_MIN = {"MESH": 0.5, "X2": 3.4, "S8": 6.4, "N2": 1.7, "S1": 0.9, "R1": 0.7}
PHASE1_PREDICTED = 13.6
PHASE1_CAP = 93.0
ITEM_CEILING_CORE_MIN = 233.0

# Arms that MEASURE but GRADE NOTHING (PREREGISTRATION.md sections 4.2, 4.3).
NON_GRADING_ARMS = {"N2", "R1"}

STEPS_SWEEP = {
    "shape":  [3.0e-2, 1.0e-2, 3.0e-3, 1.0e-3, 3.0e-4, 1.0e-4, 3.0e-5, 1.0e-5],
    "patchV": [3.0e-1, 1.0e-1, 3.0e-2, 1.0e-2, 3.0e-3, 1.0e-3, 3.0e-4, 1.0e-4],
}
STEPS_D19 = {"shape":  [3.0e-2, 1.0e-2, 1.0e-3, 1.0e-4, 1.0e-5],
             "patchV": [3.0e-1, 1.0e-1, 1.0e-2, 1.0e-3, 1.0e-4]}
DECADE_STRIDE = 2
COMPONENTS = [["shape", 0], ["shape", 3], ["shape", 6], ["shape", 7], ["patchV", 1]]
FUNCTIONS = ["CD", "CL"]

REPRO_FD_PCT = 0.5            # G19R-1a
REPRO_ADJ_PCT = 0.1           # G19R-1a
PLATEAU_TOL_PCT = 10.0        # G19R-1b -- D19's band, UNCHANGED
DECOMP_TOL_PCT = 2.0          # G19R-1d
NEAR_ZERO_ABS = 1.0e-14

CTRL_STEP = 1.0e-3
PLANT_K = 5.0                 # G19R-1c
PLANT_K_SHRUNK = 0.5
GRADER_PLANT_K = 5.0          # this grader's OWN plant, same formula

IMG_DIGEST_PATCHED = "sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35"
SO_MD5_PATCHED = "85f59e87253e0a71a813f64ca6e4c425"
CPUSET_REGISTERED = "1,15"
VOCAB = {"PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"}
RESULT_LABELS = {"V-PLATEAU", "V-NOPLATEAU"}

INPUT_SUBDIRS = ["0.orig", "constant", "system", "d19r_runScript.py", "d19r_xf.py"]


class Refusal(Exception):
    pass


def refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail}, sort_keys=True, default=str))


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def read_json(path, what):
    if not os.path.isfile(path):
        refuse("ARTEFACT_ABSENT", {"path": path, "what": what})
    return json.load(open(path))


def fd_lookup(doc, dv, idx, step, of):
    for row in doc.get("rows", []):
        if row.get("dv") != dv or row.get("idx") != idx:
            continue
        for k, v in row.get("fd", {}).items():
            if abs(float(k) - step) < 1e-15:
                if not v.get("ok"):
                    return None
                return float(v["dCD" if of == "CD" else "dCL"])
    return None


# ================= ledger =====================================================
import re                                                              # noqa: E402

LEDGER_RE = re.compile(
    r"^ARM=(?P<arm>\S+) ROW=(?P<row>\S+) IMG=(?P<img>\S+) DIGEST=(?P<digest>\S+) "
    r"rc=(?P<rc>-?\d+) wall_s=(?P<wall_s>\d+) ranks=(?P<ranks>\d+) "
    r"core_min=(?P<core_min>[\d.]+) cap_core_min=(?P<cap>[\d.]+)")


def read_ledger(path):
    if not os.path.isfile(path):
        refuse("LEDGER_ABSENT", {"path": path})
    rows = {}
    for line in open(path):
        if not line.startswith("ARM="):
            continue
        m = LEDGER_RE.match(line)
        if not m:
            # PRESENT-BUT-GARBAGE is REFUSED, never skipped.  A skipped row is a
            # silently dropped arm, which is how a partial run reads as complete.
            refuse("LEDGER_ROW_GARBAGE", {"line": line.strip()[:300]})
        d = m.groupdict()
        rows[d["arm"]] = {"row": d["row"], "img": d["img"], "digest": d["digest"],
                          "rc": int(d["rc"]), "wall_s": int(d["wall_s"]),
                          "ranks": int(d["ranks"]), "core_min": float(d["core_min"]),
                          "cap": float(d["cap"]), "raw": line.strip()}
    return rows


# ================= G19R-1h COMPLETION, with the REPAIRED age datum ============
def g_completion(base, rows):
    """rule 4, as repaired by PREREGISTRATION.md section 2.2.

    The datum is the LAUNCH SENTINEL, stamped outside every bind-mount source --
    not the case's `0/`, which D19 measured to be inside the solver's write set
    (the `patchV` DV rewrites `0/U`'s inlet BC mid-run, and OpenFOAM writes the
    whole object under `writeCompression`).  The AGE ASSERTION ITSELF IS
    UNCHANGED: every artefact strictly newer than the datum.
    """
    out, mounts = {}, [base]
    for arm in ARMS_REQUIRED:
        r = rows.get(arm)
        if r is None:
            refuse("G19R-1h", {"ledger_row_absent": arm})
        if r["rc"] != 0:
            refuse("G19R-1h", {"arm": arm, "rc": r["rc"],
                               "note": "a non-zero rc is NOT A RESULT, not a warning"})
        arm_dir = os.path.join(base, arm)
        sentinel = AGE.sentinel_path(base, arm)
        man_path = os.path.join(arm_dir, ".d19r_manifest.json")
        if not os.path.isfile(man_path):
            refuse("G19R-1h", {"manifest_absent": man_path, "arm": arm})
        manifest = json.load(open(man_path))
        try:
            ev = AGE.check_arm(arm_dir, [ARTEFACT[arm]], sentinel, manifest, mounts)
        except AGE.Refusal as exc:
            refuse("G19R-1h", {"arm": arm, "age_guard": json.loads(str(exc))})
        if arm in TERMINAL:
            log = [f for f in os.listdir(base)
                   if f.startswith(arm + "_") and f.endswith(".log")]
            if not log:
                refuse("G19R-1h", {"log_absent": arm})
            text = open(os.path.join(base, sorted(log)[-1]), errors="replace").read()
            if TERMINAL[arm] not in text:
                refuse("G19R-1h", {"terminal_marker_absent": TERMINAL[arm], "arm": arm})
        out[arm] = {"rc": 0, "artefact": ARTEFACT[arm], "age_guard": ev,
                    "grades": arm not in NON_GRADING_ARMS}
    return {"verdict": "PASS", "arms": out,
            "age_datum": "LAUNCH SENTINEL outside every bind-mount source; the case's "
                         "0/ is a SOLVER WRITE TARGET and is excluded by name"}


# ================= G19R-1c the grader's OWN planted control ===================
def g_planted(S8doc, s8path):
    """rule 3, two halves, both refusing, and BOTH SIZED RELATIVE."""
    ctrl = [r for r in S8doc.get("rows", []) if r.get("dv") == "CTRL"]
    if not ctrl:
        refuse("G19R-1c", {"control_row_absent": s8path})
    ctrl = ctrl[0]
    d_ref = float(S8doc["CD_baseline"])
    want = AGE.plant_relative(d_ref, PLATEAU_TOL_PCT, PLANT_K) / (2.0 * CTRL_STEP)
    want_s = AGE.plant_relative(d_ref, PLATEAU_TOL_PCT, PLANT_K_SHRUNK) / (2.0 * CTRL_STEP)
    got_zero = float(ctrl["fd"][repr(CTRL_STEP)]["dCD"])
    got_plant = float(ctrl["planted"]["dCD"])
    got_shrunk = float(ctrl["planted_shrunk"]["dCD"])
    if (got_zero != 0.0 or abs(got_plant - want) > 1e-9 * abs(want)
            or abs(got_shrunk - want_s) > 1e-9 * abs(want_s)):
        refuse("G19R-1c", {"instrument_control_unreadable": True, "zero": got_zero,
                           "plant": got_plant, "want": want,
                           "shrunk": got_shrunk, "want_shrunk": want_s})
    if not bool(ctrl["planted"]["crosses_band"]):
        refuse("G19R-1c", {"plant_does_not_cross": True, "K": PLANT_K,
                           "note": "this is the SO-2M failure"})
    if bool(ctrl["planted_shrunk"]["crosses_band"]):
        refuse("G19R-1c", {"shrunk_plant_crosses": True, "K": PLANT_K_SHRUNK,
                           "note": "a control that crosses at every plant size is not "
                                   "measuring crossing"})
    # (b) THIS grader's own plant, into the on-disk table, relative by the same formula
    dv, idx = "shape", 7
    s = STEPS_SWEEP["shape"][3]
    base_v = fd_lookup(S8doc, dv, idx, s, "CD")
    if base_v is None:
        refuse("G19R-1c", {"grader_plant_target_absent": [dv, idx, s]})
    p = AGE.plant_relative(base_v, PLATEAU_TOL_PCT, GRADER_PLANT_K)
    moved = abs((base_v + p) - base_v) / abs(base_v) * 100.0
    predicted = GRADER_PLANT_K * PLATEAU_TOL_PCT
    if abs(moved - predicted) > 1e-9:
        refuse("G19R-1c", {"grader_reader_blind": True, "moved_pct": moved,
                           "predicted_pct": predicted})
    if moved <= PLATEAU_TOL_PCT:
        refuse("G19R-1c", {"grader_plant_not_sized_against_its_band": True,
                           "moved_pp": moved, "band": PLATEAU_TOL_PCT})
    return {"instrument_control": "SEEN", "zero": got_zero,
            "formula": "plant = K * (band/100) * |d_ref|",
            "K": PLANT_K, "K_shrunk": PLANT_K_SHRUNK, "band_pct": PLATEAU_TOL_PCT,
            "plant_derivative": got_plant, "shrunk_derivative": got_shrunk,
            "shrunk_crosses": False,
            "grader_plant_target": "%s[%d]/CD @ %g" % (dv, idx, s),
            "grader_reading_moved_pp": moved, "status": "EXERCISED"}


# ================= G19R-1a REPRODUCTION, against D19 =========================
def g_reproduction(S8doc, Xdoc):
    d19S = read_json(os.path.join(D19_ROOT, "S2", "d19_S.json"), "D19 S2")
    d19X = read_json(os.path.join(D19_ROOT, "X2", "d19_X.json"), "D19 X2")
    fd_rows, worst_fd = [], 0.0
    for dv, idx in COMPONENTS:
        for step in STEPS_D19[dv]:
            for of in FUNCTIONS:
                a = fd_lookup(S8doc, dv, idx, step, of)
                b = fd_lookup(d19S, dv, idx, step, of)
                if a is None or b is None:
                    refuse("G19R-1a", {"value_absent": [dv, idx, step, of],
                                       "d19r": a, "d19": b})
                if abs(b) < NEAR_ZERO_ABS:
                    refuse("G19R-1a", {"d19_reference_near_zero": [dv, idx, step, of]})
                rel = abs(a - b) / abs(b) * 100.0
                worst_fd = max(worst_fd, rel)
                fd_rows.append({"dv": dv, "idx": idx, "step": step, "of": of,
                                "d19r": a, "d19": b, "rel_pct": rel,
                                "ok": rel <= REPRO_FD_PCT})
    adj_rows, worst_adj = [], 0.0
    for of in FUNCTIONS:
        for dv, idx in COMPONENTS:
            a = float(Xdoc["adjoint"][of][dv][idx])
            b = float(d19X["adjoint"][of][dv][idx])
            if abs(b) < NEAR_ZERO_ABS:
                refuse("G19R-1a", {"d19_adjoint_near_zero": [dv, idx, of]})
            rel = abs(a - b) / abs(b) * 100.0
            worst_adj = max(worst_adj, rel)
            adj_rows.append({"dv": dv, "idx": idx, "of": of, "d19r": a, "d19": b,
                             "rel_pct": rel, "ok": rel <= REPRO_ADJ_PCT})
    ok = all(r["ok"] for r in fd_rows) and all(r["ok"] for r in adj_rows)
    return {"verdict": "PASS" if ok else "NOT A RESULT",
            "band_fd_pct": REPRO_FD_PCT, "band_adjoint_pct": REPRO_ADJ_PCT,
            "worst_fd_rel_pct": worst_fd, "worst_adjoint_rel_pct": worst_adj,
            "n_fd_compared": len(fd_rows), "n_adjoint_compared": len(adj_rows),
            "reference": "D19 phase 1 (grader REFUSED on an infrastructure clause; its "
                         "PHYSICS fields are read forward under Sanaa's 2026-08-26 rule "
                         "that bookkeeping never voids physics.  D19 carries NO verdict "
                         "and none is quoted here.)",
            "fd": fd_rows, "adjoint": adj_rows}


# ================= G19R-1b PLATEAU, DECADE neighbours, MAX not MIN ===========
def plateau_at(S8doc, lv):
    comps, worst, binding = [], 0.0, None
    lo, hi = lv - DECADE_STRIDE, lv + DECADE_STRIDE
    for dv, idx in COMPONENTS:
        for of in FUNCTIONS:
            vals = [fd_lookup(S8doc, dv, idx, s, of) for s in STEPS_SWEEP[dv]]
            if any(v is None for v in vals):
                refuse("G19R-1b", {"sweep_incomplete": [dv, idx, of]})
            if lo < 0 or hi >= len(vals):
                refuse("G19R-1b", {"candidate_lacks_decade_neighbour": lv})
            ref = vals[lv]
            if abs(ref) < NEAR_ZERO_ABS:
                refuse("G19R-1b", {"near_zero": [dv, idx, of]})
            nc = abs(vals[lo] - ref) / abs(ref) * 100.0
            nf = abs(vals[hi] - ref) / abs(ref) * 100.0
            mx = max(nc, nf)
            if mx > worst:
                worst, binding = mx, "%s[%d]/%s" % (dv, idx, of)
            comps.append({"dv": dv, "idx": idx, "of": of,
                          "neighbour_coarse_pct": nc, "neighbour_fine_pct": nf,
                          "max_pct": mx, "two_sided": bool(mx <= PLATEAU_TOL_PCT)})
    return comps, worst, binding


def g_plateau(S8doc, sel):
    lv = int(sel["s_star_level"])
    comps, worst, binding = plateau_at(S8doc, lv)
    ok = all(c["two_sided"] for c in comps)
    return {"verdict": "PASS" if ok else "GATE FAIL",
            "result_label": "V-PLATEAU" if ok else "V-NOPLATEAU",
            "s_star": sel["s_star"], "s_star_level": lv,
            "tol_pct": PLATEAU_TOL_PCT, "reading": "max, not min",
            "neighbour_rule": "DECADE-separated (stride %d on the half-decade grid); "
                              "half-decade points are candidate CENTRES only.  Verified "
                              "against D19's real data: this rule reproduces D19's own "
                              "registered score_pct=21.629866 at the level D19 graded, "
                              "so it is provably not a relaxation." % DECADE_STRIDE,
            "worst_pct": worst, "binding": binding,
            "n_two_sided": sum(1 for c in comps if c["two_sided"]),
            "n_components": len(comps), "components": comps}


# ================= G19R-1e FLAGGED-COMPONENT DISPOSITION -- EVIDENCE ONLY =====
def g_disposition(S8doc, Xdoc, plateau):
    """`DAFOAM_CHARTER.md` section 3: a component that does not stabilise ANYWHERE
    is flagged and excluded BY NAME from any aggregate quoted as agreement --
    never dropped silently, never rescued by a step at which it happens to cross.

    **THIS IS EVIDENCE FOR SANAA'S GATE-DESIGN DECISION.  IT IS NOT A VERDICT AND
    IT CANNOT LAUNCH PHASE 2.**  Letting a subordinate reading launch the
    optimiser IS relaxing the gate by another name (`CLAUDE.md` rule 9).
    """
    if plateau["verdict"] != "GATE FAIL":
        return {"status": "NOT EXERCISED",
                "why": "G19R-1e is computed only when G19R-1b GATE FAILs"}
    # a component is FLAGGED iff it stabilises at NO admissible level
    admissible = [lv for lv in range(DECADE_STRIDE,
                                     len(STEPS_SWEEP["shape"]) - DECADE_STRIDE)]
    never = {}
    for lv in admissible:
        comps, _w, _b = plateau_at(S8doc, lv)
        for c in comps:
            key = "%s[%d]/%s" % (c["dv"], c["idx"], c["of"])
            never.setdefault(key, True)
            if c["two_sided"]:
                never[key] = False
    flagged = sorted(k for k, v in never.items() if v)

    # each flagged component's share of the adjoint norm -- how much of the
    # optimiser's search direction it actually carries
    shares = {}
    for of in FUNCTIONS:
        vec = [abs(float(Xdoc["adjoint"][of][dv][idx])) for dv, idx in COMPONENTS]
        norm = sum(v * v for v in vec) ** 0.5
        for (dv, idx), v in zip(COMPONENTS, vec):
            shares["%s[%d]/%s" % (dv, idx, of)] = (v / norm * 100.0) if norm else None

    remaining = [c for c in plateau["components"]
                 if "%s[%d]/%s" % (c["dv"], c["idx"], c["of"]) not in flagged]
    worst_rem = max((c["max_pct"] for c in remaining), default=None)
    return {
        "status": "EXERCISED",
        "IS_A_VERDICT": False,
        "CAN_LAUNCH_PHASE_2": False,
        "flagged_components": flagged,
        "flagged_shares_of_adjoint_norm_pct": {k: shares.get(k) for k in flagged},
        "admissible_levels_searched": admissible,
        "worst_remaining_pct": worst_rem,
        "remaining_all_two_sided": bool(worst_rem is not None
                                        and worst_rem <= PLATEAU_TOL_PCT),
        "note": "DAFOAM_CHARTER.md section 3 requires a non-stabilising component to be "
                "FLAGGED AND NAMED, never dropped silently.  This block names them and "
                "reports what the plateau would read without them SO THAT SANAA CAN "
                "DECIDE.  It changes no gate, it is not a verdict, and the phase-2 "
                "branch is gated on G19R-1b PASS and on nothing else.",
    }


# ================= G19R-1d DECOMPOSITION =====================================
def g_decomposition(S8doc, S1doc, sel):
    star = sel["s_star"]
    rows, worst = [], 0.0
    for dv, idx in COMPONENTS:
        s = float(star[dv])
        for of in FUNCTIONS:
            a = fd_lookup(S1doc, dv, idx, s, of)
            b = fd_lookup(S8doc, dv, idx, s, of)
            if a is None or b is None:
                refuse("G19R-1d", {"value_absent": [dv, idx, s, of], "S1": a, "S8": b})
            if abs(b) < NEAR_ZERO_ABS:
                refuse("G19R-1d", {"near_zero": [dv, idx, s, of]})
            rel = abs(a - b) / abs(b) * 100.0
            worst = max(worst, rel)
            rows.append({"dv": dv, "idx": idx, "of": of, "step": s,
                         "np1": a, "np2": b, "rel_pct": rel,
                         "ok": rel <= DECOMP_TOL_PCT})
    ok = all(r["ok"] for r in rows)
    return {"verdict": "PASS" if ok else "GATE FAIL", "tol_pct": DECOMP_TOL_PCT,
            "worst_rel_pct": worst, "n_compared": len(rows), "rows": rows,
            "also_tests": "the live re-test of D19's 0/U warm-start bound "
                          "(PREREGISTRATION.md section 3); D19 measured worst "
                          "0.041027 % on this exact pair"}


# ================= toolchain / caps ==========================================
def g_toolchain(rows, base):
    out, ok = {}, True
    ledger_text = open(os.path.join(base, "ledger.txt"), errors="replace").read()
    for arm in ARMS_REQUIRED:
        r = rows[arm]
        printed_ok = ("D19R_G9_OK arm=%s libidwarp_so_md5=%s digest=%s"
                      % (arm, SO_MD5_PATCHED, IMG_DIGEST_PATCHED)) in ledger_text
        good = (r["digest"] == IMG_DIGEST_PATCHED and r["row"] == "PATCHED" and printed_ok)
        ok = ok and good
        out[arm] = {"digest": r["digest"], "row": r["row"],
                    "printed_marker_seen": printed_ok, "ok": good}
    return {"verdict": "PASS" if ok else "GATE FAIL",
            "expected_digest": IMG_DIGEST_PATCHED, "expected_so_md5": SO_MD5_PATCHED,
            "arms": out,
            "note": "toolchain identity is an image ID and a library hash, never a "
                    "version string"}


def g_caps(rows):
    per, total, ok = {}, 0.0, True
    for arm in ARMS_REQUIRED:
        r = rows[arm]
        within = r["core_min"] <= CAPS[arm]
        ok = ok and within
        total += r["core_min"]
        per[arm] = {"core_min": r["core_min"], "cap": CAPS[arm],
                    "predicted": PREDICTED_CORE_MIN[arm],
                    "ratio_actual_over_predicted": (r["core_min"] / PREDICTED_CORE_MIN[arm]
                                                    if PREDICTED_CORE_MIN[arm] else None),
                    "within_cap": within}
    within_phase = total <= PHASE1_CAP
    ok = ok and within_phase
    return {"verdict": "PASS" if ok else "GATE FAIL", "per_arm": per,
            "phase1_core_min": total, "phase1_cap": PHASE1_CAP,
            "phase1_predicted": PHASE1_PREDICTED,
            "phase1_ratio_actual_over_predicted": total / PHASE1_PREDICTED,
            "item_ceiling_core_min": ITEM_CEILING_CORE_MIN,
            "dollars_derived_not_measured": round(total / 60.0 * 0.0513, 6),
            "cost_basis": "Core-minutes are MEASURED, from the launcher's own per-arm "
                          "ledger rows (wall_s x ranks / 60).  Dollars are DERIVED from "
                          "those core-minutes at the c7a.4xlarge rate of $0.0513 per "
                          "core-hour.  THAT RATE IS REPORTED BY THE OWNER (Sanaa, "
                          "2026-08-21/22) AND IS NOT MEASURED BY THIS BOX -- the box "
                          "cannot read its own billing (COMPUTE_BUDGET_CHARTER.md "
                          "section 5), so no dollar figure here is a measurement.",
            "stop_rule": "an overrun STOPS the run; it does not get a new budget"}


# ================= compose ===================================================
def grade(root):
    prov = PROV.require_travelling_provenance({}, refuse=refuse)
    ledger = read_ledger(os.path.join(root, "ledger.txt"))
    comp = g_completion(root, ledger)

    S8 = read_json(os.path.join(root, "S8", "d19r_S.json"), "S8")
    X = read_json(os.path.join(root, "X2", "d19r_X.json"), "X2")
    S1 = read_json(os.path.join(root, "S1", "d19r_S1.json"), "S1")
    N2 = read_json(os.path.join(root, "N2", "d19r_N.json"), "N2")
    R1 = read_json(os.path.join(root, "R1", "d19r_R1.json"), "R1")
    sel = read_json(os.path.join(root, "d19r_selected_step.json"), "selector")

    if sel.get("selector_saw_adjoint") is not False:
        refuse("G19R-1b", {"selector_not_adjoint_blind": True})
    if N2.get("grades_nothing") is not True or R1.get("grades_nothing") is not True:
        refuse("G19R-1e", {"non_grading_arm_does_not_declare_itself": True})

    planted = g_planted(S8, os.path.join(root, "S8", "d19r_S.json"))
    repro = g_reproduction(S8, X)
    plateau = g_plateau(S8, sel)
    decomp = g_decomposition(S8, S1, sel)
    disp = g_disposition(S8, X, plateau)
    tool = g_toolchain(ledger, root)
    caps = g_caps(ledger)

    gates = {"G19R-1a": repro, "G19R-1b": plateau, "G19R-1c": planted,
             "G19R-1d": decomp, "G19R-1e": disp, "G19R-1f": tool,
             "G19R-1g": caps, "G19R-1h": comp, "G19R-1i": prov}

    # ---- composition.  A GATE FAIL is never softened. ------------------------
    if repro["verdict"] != "PASS":
        verdict, why = "NOT A RESULT", "G19R-1a: not the same instrument D19 ran"
    elif comp["verdict"] != "PASS" or tool["verdict"] != "PASS":
        verdict, why = "NOT A RESULT", "G19R-1h/G19R-1f"
    elif plateau["verdict"] != "PASS":
        verdict, why = "GATE FAIL", "G19R-1b: no two-sided decade-bracketed plateau at s*"
    elif decomp["verdict"] != "PASS":
        verdict, why = "GATE FAIL", "G19R-1d: np=1 and np=2 disagree at s*"
    elif caps["verdict"] != "PASS":
        verdict, why = "GATE FAIL", "G19R-1g: cap exceeded"
    else:
        verdict, why = "PASS", "all phase-1 gates PASS"
    if verdict not in VOCAB:
        refuse("VOCAB", {"verdict": verdict})

    phase2 = (verdict == "PASS")
    return {
        "item": ITEM, "phase": 1, "root": root,
        "rows": {"PATCHED": verdict},
        "row_note": "PHASE 1 IS PATCHED-ROW ONLY, registered before compute "
                    "(PREREGISTRATION.md section 9): the plateau is a property of the "
                    "PRIMAL and the STEP, which both images share, so a SHIPPED sweep "
                    "would reproduce this one by construction.  A DAFoam verdict is "
                    "normally TWO ROWS and phase 2, if ever reached, is two.",
        "verdict": verdict, "verdict_reason": why,
        "result_label": plateau.get("result_label"),
        "result_label_note": "V-NOPLATEAU is a REGISTERED RESULT that travels BESIDE the "
                             "verdict.  GATE FAIL is the verdict; V-NOPLATEAU is what was "
                             "learned; neither softens the other.  It reads 'no plateau of "
                             "half-decade width or greater', never 'no plateau'.",
        "phase2_eligible": phase2,
        "phase2_note": "PHASE 2 IS NOT AUTHORISED BY THIS GRADER.  Eligibility is gated on "
                       "G19R-1b PASS and on nothing else; G19R-1e cannot launch it.",
        "gates": gates,
        "measurement_arms_grading_nothing": {
            "N2": {"purpose": "the PERTURBED-MESH noise floor",
                   "rows": N2.get("n_rows"), "eta_raw": N2.get("eta_raw")},
            "R1": {"purpose": "sensitivity-equalised step DIAGNOSTIC",
                   "kappa": R1.get("kappa"), "ladder": R1.get("r1_ladder"),
                   "verdict": "DIAGNOSTIC"}},
        "verdict_suffix": "on the PATCHED toolchain; the SHIPPED toolchain FAILS the "
                          "gradient gate on this exact ground (D15 shipped worst 44.8738 % "
                          "on shape[6], aggregate 34.6807 %)",
    }


# ================= selftest ==================================================
def selftest():
    """Planted controls on the GRADING ARITHMETIC.  Every leg must fire."""
    ran, ok = 0, True

    def leg(name, cond, detail=""):
        nonlocal ran, ok
        ran += 1
        ok = ok and cond
        print("   %-44s %s %s" % (name, "OK" if cond else "**FAILED**", detail))

    print("D19R GRADER SELFTEST")
    print(" A. vocabulary")
    leg("every emitted verdict is in VOCAB",
        {"PASS", "GATE FAIL", "NOT A RESULT"} <= VOCAB)
    leg("V-NOPLATEAU is a RESULT LABEL, not a verdict",
        "V-NOPLATEAU" in RESULT_LABELS and "V-NOPLATEAU" not in VOCAB)

    print(" B. G19R-1b plateau arithmetic -- decade stride, max not min")
    # a synthetic doc whose level-3 decade neighbours are known
    def mkdoc(v7fine):
        rows = []
        for dv, idx in COMPONENTS:
            fd = {}
            for i, s in enumerate(STEPS_SWEEP[dv]):
                val = 1.0
                if (dv, idx) == ("shape", 7) and i == 3 + DECADE_STRIDE:
                    val = v7fine
                fd[repr(s)] = {"step": s, "dCD": repr(val), "dCL": repr(1.0), "ok": True}
            rows.append({"dv": dv, "idx": idx, "status": "MEASURED", "fd": fd})
        return {"rows": rows, "CD_baseline": "0.0146"}

    comps, worst, binding = plateau_at(mkdoc(1.0), 3)
    leg("flat table -> worst 0.0 %, all two-sided",
        abs(worst) < 1e-12 and all(c["two_sided"] for c in comps))
    comps, worst, binding = plateau_at(mkdoc(1.2163), 3)
    leg("PLANTED 21.63 % on shape[7] fine decade neighbour -> binding, GATE FAIL",
        abs(worst - 21.63) < 1e-9 and binding == "shape[7]/CD"
        and not all(c["two_sided"] for c in comps),
        "worst=%.4f %% binding=%s" % (worst, binding))
    # the plant is BELOW the band -> must NOT flip the gate.  A gate that fails on
    # everything is not a gate.
    comps, worst, _b = plateau_at(mkdoc(1.05), 3)
    leg("SUFFICIENCY RED LEG: 5 %% plant (half the band) does NOT flip the gate",
        abs(worst - 5.0) < 1e-9 and all(c["two_sided"] for c in comps),
        "worst=%.4f %%" % worst)

    print(" C. the stride really spans a decade")
    good = True
    for dv, steps in STEPS_SWEEP.items():
        for i in range(len(steps) - DECADE_STRIDE):
            good = good and abs(steps[i] / steps[i + DECADE_STRIDE] - 10.0) < 1e-9
    leg("DECADE_STRIDE=%d spans exactly one decade on both ladders" % DECADE_STRIDE, good)

    print(" D. G19R-1c relative plant, both legs")
    d_ref = -2.065253e-04
    m = abs(AGE.plant_relative(d_ref, PLATEAU_TOL_PCT, PLANT_K)) / abs(d_ref) * 100.0
    ms = abs(AGE.plant_relative(d_ref, PLATEAU_TOL_PCT, PLANT_K_SHRUNK)) / abs(d_ref) * 100.0
    leg("K=5.0 moves 50 pp and CROSSES the 10 pp band", abs(m - 50.0) < 1e-9 and m > PLATEAU_TOL_PCT)
    leg("K=0.5 moves 5 pp and DOES NOT cross -- red leg", abs(ms - 5.0) < 1e-9 and ms <= PLATEAU_TOL_PCT)

    print(" E. G19R-1e cannot launch phase 2")
    d = g_disposition(mkdoc(1.0), None, {"verdict": "PASS"})
    leg("not exercised while G19R-1b PASSes", d["status"] == "NOT EXERCISED")
    src = open(os.path.abspath(__file__)).read()
    leg("phase2_eligible is gated on the composed verdict alone",
        'phase2 = (verdict == "PASS")' in src and "G19R-1e" not in src.split("phase2 = ")[1][:200])

    print(" F. the age guard is the REPAIRED one and its legs still fire")
    leg("grader imports d19r_age_guard, not a local copy", AGE.ITEM == "D19R")
    leg("age guard selftest passes", AGE.selftest() == 0)

    print()
    if ran < 12:
        print("*** a selftest that ran %d checks is not this selftest ***" % ran)
        return 1
    print("D19R GRADER SELFTEST: %s (%d checks ran)" % ("OK" if ok else "FAILED", ran))
    return 0 if ok else 1


def main():
    argv = sys.argv[1:]
    if "--selftest" in argv:
        return selftest()
    root, out = BASE, None
    for i, a in enumerate(argv):
        if a == "--root" and i + 1 < len(argv):
            root = argv[i + 1]
        if a == "--out" and i + 1 < len(argv):
            out = argv[i + 1]
    try:
        res = grade(root)
    except (Refusal, PROV.Refusal) as exc:
        sys.stderr.write("D19R_GRADE REFUSED: %s\n" % exc)
        return 2
    txt = json.dumps(res, indent=1, sort_keys=True, default=str)
    if out:
        with open(out, "w") as fh:
            fh.write(txt)
            fh.flush()
            os.fsync(fh.fileno())
    print("D19R_GRADE verdict=%s label=%s reason=%s"
          % (res["verdict"], res.get("result_label"), res["verdict_reason"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
