#!/usr/bin/env python3
"""DRIVAER R2b probe C2 -- MECHANICAL evaluation of the exits registered in
verification/campaign/DRIVAER_R2B_LAYER_PROBE_C2_PREREGISTRATION.md
(frozen d4142f0ee, sha256 57443ab92b6fda30d2027ecfaf3023aa6ca15e3313e19a90c4aa10316bdacc07).

WHY A NEW FILE IS NOT A NEW GATE.  Rule 2 fixes the GRADING PATH at the
pre-registration commit.  §5 of that registration fixes the three MEASUREMENT
instruments by literal sha256 -- run_build.sh, stage_r2_measure.py, and the control
snappyHexMeshDict -- and this script re-computes all three and REFUSES on any
mismatch.  What this script adds is arithmetic with NO free parameter: the three
numbers it compares against (50.0 %, 30, 300) are literals of §0, and it RE-READS THE
FROZEN FILE AT RUN TIME AND ASSERTS THAT EACH LITERAL IS STILL THERE.  If the text on
disk does not carry the thresholds coded here, this script refuses rather than grade.
It therefore cannot express a gate the registration does not already state.

IT KILLS NOTHING and it signals nothing.  It writes no file matching any launcher's
rc globs, so it cannot fabricate a completion.

RULE 3.  The measurement's own planted controls are checked: if
`all_plants_passed` is not true, the reader was not shown able to see a non-zero and
every number below is inadmissible.  REFUSE, never degrade.

exit 0 = verdict produced.  exit 2 = REFUSED.  exit 70 = internal defect.
"""
import hashlib
import json
import os
import sys

REPO = "/home/ubuntu/Certonomous"
REG = os.path.join(REPO, "verification/campaign/DRIVAER_R2B_LAYER_PROBE_C2_PREREGISTRATION.md")
REG_SHA = "57443ab92b6fda30d2027ecfaf3023aa6ca15e3313e19a90c4aa10316bdacc07"

# ---- §5 grading path, LITERAL HASHES, re-computed before any verdict is believed ----
INSTRUMENTS = {
    "cases/navier_class/DRIVAER/mesh/run_build.sh":
        "7577f707d17e0718aacefadb95fb304f94e934578e2926ae2ca623ed72aecebd",
    "cases/navier_class/DRIVAER/mesh/stage_r2_measure.py":
        "c86a8ea4317f0dc21a00c9c739f8de7932bebf86345751632deddffd1640bb0e",
    "verification/runs/navier_class/DRIVAER/r2_coarse/system/snappyHexMeshDict":
        "d13bbac350e032546546c0f228e45978b296ca2ae3428cc4bf581c17cca32ec3",
}

# ---- §0 literals.  Each is asserted present in the frozen text before it is used. ----
COVERAGE_FLOOR_PCT = 50.0
YPLUS_LO = 30.0
YPLUS_HI = 300.0
REG_LITERALS = [
    "Coverage **< 50.0 %**",
    "layered median y⁺ **> 300**",
    "y⁺ ∈ [30, 300]",
]

# ---- predictions ON RECORD BEFORE THE RUN, scored against the actual, never rewritten
REG_PRED = {"coverage_pct": 53.7, "yplus_lo": 227.0, "yplus_hi": 380.0,
            "source": "registration §2 table, 5.00 mm row"}
LANE_PRED = {"t1_mm": 7.016, "yplus": 318.0, "coverage_pct": 56.9,
             "source": "predecessor lane's sharpened prediction, written before the run"}
PRED_CORE_MIN = 80.0          # registration §4
PRED_PEAK_GIB = 0.6           # registration §4


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def refuse(msg):
    print("REFUSED: " + msg)
    sys.exit(2)


def main():
    if len(sys.argv) != 2:
        refuse("usage: grade_c2_exits.py <RUN_DIR>")
    root = os.path.abspath(sys.argv[1])
    if not os.path.isdir(root):
        refuse("no such run root %s" % root)

    out = {"run_root": root, "registration": REG, "registration_sha256_expected": REG_SHA}

    # ---- 1. the frozen registration IS the file that governs ------------------------
    if not os.path.exists(REG):
        refuse("the frozen registration is absent from the worktree: %s" % REG)
    got = sha256_file(REG)
    out["registration_sha256_actual"] = got
    if got != REG_SHA:
        refuse("registration sha256 %s != frozen %s -- the governing document is not the "
               "document that was frozen, and no verdict off it is admissible" % (got, REG_SHA))
    text = open(REG, encoding="utf-8").read()
    missing = [s for s in REG_LITERALS if s not in text]
    if missing:
        refuse("the frozen registration does not contain the threshold literal(s) this "
               "script applies: %r. This script cannot express a gate the registration "
               "does not state." % missing)
    out["registration_literals_confirmed"] = REG_LITERALS

    # ---- 2. §5 grading path ---------------------------------------------------------
    inst = {}
    for rel, want in INSTRUMENTS.items():
        p = os.path.join(REPO, rel)
        if not os.path.exists(p):
            refuse("§5 instrument absent: %s" % rel)
        g = sha256_file(p)
        inst[rel] = {"expected": want, "actual": g, "match": g == want}
        if g != want:
            refuse("§5 instrument hash mismatch on %s: %s != %s. A mismatch is a REFUSAL."
                   % (rel, g, want))
    out["instruments"] = inst

    # ---- 3. completion: RUN_RC, written LAST, after the measurement (§6.2) -----------
    rc_p = os.path.join(root, "RUN_RC")
    if not os.path.exists(rc_p):
        refuse("no RUN_RC in %s. RUN_C2.sh writes it LAST, after the measurement, so its "
               "absence means the probe has not finished. A verdict is not produced on an "
               "unfinished run and the exit status is NOT invented." % root)
    try:
        run_rc = int(open(rc_p).read().strip())
    except ValueError:
        refuse("RUN_RC is not an integer; the probe's exit status is unreadable")
    out["RUN_RC"] = run_rc

    meta = {}
    mp = os.path.join(root, "RUN_META.txt")
    if os.path.exists(mp):
        for line in open(mp):
            if "=" in line:
                k, v = line.split("=", 1)
                meta[k.strip()] = v.strip()
    out["RUN_META"] = meta

    # ---- 4. the measurement, and rule 3 before any number is read -------------------
    mj = os.path.join(root, "C2_MEASURED.json")
    if not os.path.exists(mj):
        if run_rc != 0:
            out["verdict"] = "NOT A RESULT"
            out["reason"] = ("RUN_RC=%d and no C2_MEASURED.json. The probe did not "
                             "complete cleanly, so there is no admissible measurement. "
                             "An absent instrument result is not evidence for either "
                             "branch (§6.2) and no exit is declared fired." % run_rc)
            emit(root, out)
            return 0
        refuse("RUN_RC=0 but no C2_MEASURED.json. A clean rc with no measurement is the "
               "C1 defect §6 names; the instrument result is absent and this script "
               "REFUSES rather than choose a branch.")
    try:
        m = json.load(open(mj))
    except Exception as e:
        refuse("C2_MEASURED.json is unparseable: %s" % e)

    if m.get("all_plants_passed") is not True:
        refuse("PLANTED CONTROLS DID NOT PASS (all_plants_passed=%r). A zero from a "
               "reader not shown able to see a non-zero is not evidence (rule 3). Every "
               "number in this measurement is inadmissible."
               % m.get("all_plants_passed"))
    out["all_plants_passed"] = True
    out["planted_controls"] = [{"plant": p.get("plant"), "passed": p.get("passed")}
                               for p in m.get("planted_controls", [])]

    if run_rc != 0:
        out["verdict"] = "NOT A RESULT"
        out["reason"] = ("RUN_RC=%d. RUN_C2.sh folds a non-zero measure_rc into RUN_RC, so "
                         "a non-zero here means the build or the instrument did not "
                         "complete. Completion fails and no exit is declared fired."
                         % run_rc)
        emit(root, out)
        return 0

    # ---- 5. the two graded quantities, each from its named field --------------------
    lay = m.get("layers") or {}
    ef, ec = lay.get("extruded_faces"), lay.get("extrude_candidate_faces")
    if not isinstance(ef, int) or not isinstance(ec, int) or ec <= 0:
        refuse("layers.extruded_faces / layers.extrude_candidate_faces missing or "
               "unusable (%r / %r); face coverage is not computable" % (ef, ec))
    coverage = 100.0 * ef / ec

    yp = m.get("yplus") or {}
    grp = yp.get("layered_group") or {}
    ypm = grp.get("yplus_area_weighted_median")
    if not isinstance(ypm, (int, float)):
        refuse("yplus.layered_group.yplus_area_weighted_median missing (%r); the band "
               "limb is not evaluable" % ypm)
    if grp.get("n_faces", 0) <= 0:
        refuse("yplus.layered_group.n_faces=%r: there is no layered group, so a layered "
               "median y+ describes nothing" % grp.get("n_faces"))

    per_m = yp.get("yplus_per_metre")
    t1_mm = (2000.0 * ypm / per_m) if isinstance(per_m, (int, float)) and per_m else None

    out["measured"] = {
        "coverage_face_pct": coverage,
        "coverage_definition": ("extruded_faces / extrude_candidate_faces -- the F1 "
                                "metric; reproduces C1's 32.390 %% from 7568/23365"),
        "extruded_faces": ef, "extrude_candidate_faces": ec,
        "layered_yplus_area_weighted_median": ypm,
        "layered_group_n_patches": grp.get("n_patches"),
        "layered_group_n_faces": grp.get("n_faces"),
        "layered_group_area_m2": grp.get("area_m2"),
        "yplus_per_metre": per_m,
        "delivered_first_layer_mm": t1_mm,
        "delivered_over_requested": (t1_mm / 5.00) if t1_mm else None,
        "requested_first_layer_mm": 5.00,
        "cells_coverage_pct_NOT_THE_GATE": lay.get("coverage_pct"),
        "unlayered_group": yp.get("unlayered_group"),
        "gate_M3_from_instrument": m.get("gate_M3"),
        "gate_Y1_from_instrument": m.get("gate_Y1"),
    }

    # ---- 6. THE EXITS, applied literally -------------------------------------------
    cov_ok = coverage >= COVERAGE_FLOOR_PCT
    band_ok = YPLUS_LO <= ypm <= YPLUS_HI
    out["limbs"] = {
        "coverage_ge_50.0": cov_ok,
        "yplus_in_[30,300]": band_ok,
        "coverage_pct": coverage,
        "layered_yplus": ypm,
    }

    if not cov_ok:
        out["exit_fired"] = "E1"
        out["verdict"] = "GATE FAIL"
        out["route_status"] = "BLOCKED"
        out["reason"] = (
            "E1. Coverage %.3f %% < the 50.0 %% floor at this ~2.4x thickness. Absolute "
            "layer sizing does not work on this geometry at this resolution. Per §0 the "
            "consequence is registered in advance: DrivAer Cd is BLOCKED on "
            "snappyHexMesh layer addition and the lab stops. Two measured points at "
            "0.040 and 0.096 thickness ratio bracket the failure. THIS IS A REFUTATION "
            "OF THE ROUTE, NOT OF A VALUE, and no third thickness follows from it."
            % coverage)
    elif ypm > YPLUS_HI:
        out["exit_fired"] = "E2"
        out["verdict"] = "GATE FAIL"
        out["route_status"] = "COARSE LEVEL REFUTED; a finer level is neither refuted nor authorised here"
        out["reason"] = (
            "E2. Coverage %.3f %% >= 50.0 %% but layered area-weighted median y+ = %.3f "
            "> 300. Absolute sizing can cover this surface but cannot do so inside the "
            "wall-function band at coarse resolution. Per §0 the COARSE level is refuted; "
            "a finer level has smaller h_surf, is NOT refuted by this, and is NOT "
            "authorised by this registration." % (coverage, ypm))
    elif band_ok:
        out["exit_fired"] = "PASS"
        out["verdict"] = "PASS"
        out["route_status"] = "coverage floor and wall-function band both met at coarse"
        out["reason"] = ("Coverage %.3f %% >= 50.0 %% AND layered area-weighted median "
                         "y+ = %.3f in [30, 300]. Both limbs of the registered PASS hold."
                         % (coverage, ypm))
    else:
        # coverage passes, y+ BELOW 30.  §0 registers no exit for this branch.
        out["exit_fired"] = "NONE -- UNREGISTERED BRANCH"
        out["verdict"] = "GATE FAIL"
        out["route_status"] = "UNREGISTERED OUTCOME -- ESCALATE, DO NOT INTERPRET"
        out["reason"] = (
            "Coverage %.3f %% >= 50.0 %% but layered median y+ = %.3f is BELOW 30, so the "
            "registered PASS condition y+ in [30,300] is not met. NEITHER E1 NOR E2 "
            "COVERS THIS BRANCH: E1 needs coverage < 50 and E2 needs y+ > 300. The label "
            "is GATE FAIL because the PASS condition failed; what it MEANS is not "
            "registered and is not decided here." % (coverage, ypm))

    # ---- 7. predictions scored, never rewritten ------------------------------------
    out["predictions_scored"] = {
        "registration_§2": dict(REG_PRED,
            coverage_error_pts=coverage - REG_PRED["coverage_pct"],
            yplus_inside_registered_range=REG_PRED["yplus_lo"] <= ypm <= REG_PRED["yplus_hi"]),
        "predecessor_lane": dict(LANE_PRED,
            coverage_error_pts=coverage - LANE_PRED["coverage_pct"],
            yplus_error=ypm - LANE_PRED["yplus"],
            t1_error_mm=(t1_mm - LANE_PRED["t1_mm"]) if t1_mm else None),
    }

    # ---- 8. cost, rule 12 -----------------------------------------------------------
    cost = {"predicted_core_min": PRED_CORE_MIN, "predicted_peak_GiB": PRED_PEAK_GIB}
    cs = os.path.join(root, "CAP_SCORED.txt")
    if os.path.exists(cs):
        for line in open(cs):
            if "=" in line:
                k, v = line.split("=", 1)
                cost[k.strip()] = v.strip()
    cm = os.path.join(root, "CORE_MINUTES.txt")
    if os.path.exists(cm):
        try:
            a = float(open(cm).read().strip())
            cost["actual_core_min_from_file"] = a
            cost["actual_over_predicted"] = a / PRED_CORE_MIN
            cost["derived_usd"] = a / 60.0 * 0.0513
            cost["cost_basis"] = ("DERIVED, NOT MEASURED: core-min/60 x $0.0513/core-h, "
                                  "owner-stated rate. The box cannot read its own billing.")
        except ValueError:
            pass
    out["cost"] = cost

    emit(root, out)
    return 0


def emit(root, out):
    jp = os.path.join(root, "C2_EXIT_VERDICT.json")
    with open(jp, "w") as f:
        json.dump(out, f, indent=1)
    mp = os.path.join(root, "C2_EXIT_VERDICT.md")
    mez = out.get("measured", {})
    with open(mp, "w") as f:
        f.write("# DRIVAER R2b probe C2 -- EXIT VERDICT\n\n")
        f.write("Registered by `verification/campaign/DRIVAER_R2B_LAYER_PROBE_C2_"
                "PREREGISTRATION.md`, frozen `d4142f0ee`,\nsha256 re-computed at grade "
                "time and matched: `%s`.\n\n" % out.get("registration_sha256_actual"))
        f.write("- verdict: **%s**\n" % out.get("verdict"))
        f.write("- exit fired: **%s**\n" % out.get("exit_fired", "n/a"))
        f.write("- route status: %s\n" % out.get("route_status", "n/a"))
        if mez:
            f.write("- coverage (extruded/candidate faces): **%.3f %%** "
                    "(%s / %s), floor 50.0 %%\n"
                    % (mez["coverage_face_pct"], mez["extruded_faces"],
                       mez["extrude_candidate_faces"]))
            f.write("- layered area-weighted median y+: **%.3f**, band [30, 300]\n"
                    % mez["layered_yplus_area_weighted_median"])
            if mez.get("delivered_first_layer_mm"):
                f.write("- delivered first layer: **%.4f mm** against 5.00 mm requested "
                        "(factor %.4f)\n" % (mez["delivered_first_layer_mm"],
                                             mez["delivered_over_requested"]))
        f.write("\n%s\n\n" % out.get("reason", ""))
        f.write("Planted controls: `all_plants_passed=%s` -- rule 3 satisfied before any "
                "number above was read.\n\n" % out.get("all_plants_passed"))
        f.write("Machine record: `C2_EXIT_VERDICT.json` beside this file.\n")
    print("verdict=%s exit=%s" % (out.get("verdict"), out.get("exit_fired", "n/a")))
    print("wrote %s" % jp)
    print("wrote %s" % mp)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("INTERNAL DEFECT: %s" % e)
        sys.exit(70)
