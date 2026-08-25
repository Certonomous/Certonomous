#!/usr/bin/env python3
"""F12 ENERGY-BOUND DISCRIMINATOR -- reader.

Answers D1/D2/D3 and grades P0-P5, L1 and L2 of
verification/campaign/F12_ENERGY_BOUND_DISCRIMINATOR_PREREGISTRATION.md
(commit 54acad46, blob e976f90a55ef077d623af5d609fbe32d245641d5).

GRADES NO F12 GATE. Reports no verdict from the fixed vocabulary.

Every number below rests on the planted-zero control in section L2, which plants
known perturbations into a T field WRITTEN BY THIS PROBE'S OWN RUN, reads them
back THROUGH THIS READER, and REFUSES (exit non-zero) if the reader cannot see
them.  The control exercises BOTH extremes because the primary reading is T_max.
"""
from __future__ import annotations
import json, os, re, shutil, sys, tempfile, pathlib

REPO = pathlib.Path("/home/ubuntu/Certonomous")
ROOT = pathlib.Path("/home/ubuntu/certonomous-runs/f12_energy_bound_discriminator_2026-08-25")
REC = REPO / "verification/runs/F12_runs/energy_bound_discriminator_2026-08-25"
RUNG1_LOG = REPO / "verification/runs/F12_runs/attempt2_coarse_workshop_M0.734_a2.79/log.rhoSimpleFoam"

# ---- FROZEN CONSTANTS.  Fixed in the pre-registration BEFORE any arm ran. ---
CP = 1004.5
DYN = 32.3309915963           # |U_inf|^2 / (2 Cp)
T0_CEIL = 332.3309915963      # D3 -- near-degenerate, disclosed, never used alone
GEN_CEIL = 342.3309915963     # D1 -- primary timing discriminator
S20_CONTROL = 3.282372        # D2 control value
I_GEN_CONTROL = 19
MITIGATED_IGEN = 38           # 2x control
MITIGATED_S20 = 1.641186      # half control
REMOVED_S20 = 1.5
P3_BAND = (2.625898, 3.938846)
CONTROL_TABLE = {             # frozen in freeze section 2.3, at SIX DECIMAL PLACES
    1:  (302.835189, 279.879433),
    4:  (332.985381, 276.161434),
    8:  (329.624836, 270.272989),
    11: (335.446862, 264.218612),
    19: (342.519742, 233.939444),
    20: (342.626798, 236.504460),
}
# ADDENDUM 1 (2026-08-25) REPAIR.  The table above is a SIX-DECIMAL transcription
# of an artifact that stores ten significant digits.  Testing exact float
# equality against it is a check with ONE UNREACHABLE BRANCH -- the same defect
# class as the terminal-departure probe's P4 and VMFL059.  It failed on arm 0,
# which is what a control is for.  P0's registered criterion is "reproduced to
# every printed digit", and the printed digits are these six decimals; the
# repaired check tests that, AND adds a STRICTLY STRONGER check against the
# committed control artifact at full precision over the WHOLE 147-row track.
# NO THRESHOLD, GATE, CAP OR LABEL IS ALTERED.
CONTROL_ARTIFACT = (REPO / "verification/runs/F12_runs/terminal_departure_2026-08-25"
                    / "evidence" / "terminal_departure.json")
PLANT_NEG = -7.654321e+09
PLANT_POS = +9.876543e+09


def refuse(msg):
    print("CONTROL REFUSED: " + msg)
    sys.exit(1)


def read_scalar(path):
    txt = pathlib.Path(path).read_text()
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\n(\d+)\s*\n\(", txt)
    if m:
        n = int(m.group(1)); start = m.end(); end = txt.index(")", start)
        vals = [float(x) for x in txt[start:end].split()]
        if len(vals) != n:
            refuse(f"{path}: declared {n} values, parsed {len(vals)}")
        return vals
    if re.search(r"internalField\s+uniform\s+([-\deE.+]+)\s*;", txt):
        return None
    refuse(f"{path}: no readable internalField")


# --------------------------------------------------------------------------
# L2 -- THE PLANTED-ZERO CONTROL (standing rule 3), SIX ARMS, BOTH EXTREMES
# --------------------------------------------------------------------------
def planted_control(case, time_dir="147", field="T"):
    src = pathlib.Path(case) / time_dir / field
    if not src.exists():
        refuse(f"no field to plant into at {src}")
    base = read_scalar(src)
    if base is None:
        refuse(f"{src} is uniform; a plant into it proves nothing about a "
               "nonuniform read path")
    arms = {"planted_into": str(src), "n_cells_clean": len(base),
            "clean_min": min(base), "clean_max": max(base)}
    tmp = tempfile.mkdtemp(prefix="f12_ebd_plant_")
    try:
        work = pathlib.Path(tmp) / field
        shutil.copy(src, work)
        # ARM 1 -- NEGATIVE: the unplanted original holds neither plant value
        arms["A1_negative_clean_has_no_plant"] = (
            PLANT_NEG not in base and PLANT_POS not in base)
        txt = work.read_text()
        m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\n(\d+)\s*\n\(", txt)
        start = m.end(); end = txt.index(")", start)
        vals = txt[start:end].split()
        i_neg = 12345 if len(base) > 12345 else len(base) // 3
        i_pos = 4321 if len(base) > 4321 else len(base) // 2
        if i_neg == i_pos:
            refuse("plant indices collided")
        vals[i_neg] = repr(PLANT_NEG)
        vals[i_pos] = repr(PLANT_POS)
        work.write_text(txt[:start] + "\n" + "\n".join(vals) + "\n" + txt[end:])
        back = read_scalar(work)
        arms["plant_cell_index_negative"] = i_neg
        arms["plant_cell_index_positive"] = i_pos
        # ARM 2 -- POSITIVE, MIN SIDE
        arms["A2_negative_plant_returned"] = PLANT_NEG in back
        # ARM 3 -- POSITIVE, MAX SIDE (this probe's primary reading is T_max)
        arms["A3_positive_plant_returned"] = PLANT_POS in back
        # ARM 4 -- LOCALISATION at the exact cell indices
        arms["A4_localisation_exact_cells"] = (
            (back.index(PLANT_NEG) == i_neg if PLANT_NEG in back else False) and
            (back.index(PLANT_POS) == i_pos if PLANT_POS in back else False))
        # ARM 5 -- CELL COUNT PRESERVED
        arms["A5_cell_count_preserved"] = (len(back) == len(base))
        # ARM 6 -- BOTH EXTREMA RELOCATE
        arms["A6_min_moved_to_negative_plant"] = (min(back) == PLANT_NEG)
        arms["A6_max_moved_to_positive_plant"] = (max(back) == PLANT_POS)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    ok = all(v for k, v in arms.items() if k.startswith(("A1", "A2", "A3", "A4", "A5", "A6")))
    arms["PASSED"] = bool(ok)
    if not ok:
        refuse(f"planted-zero control FAILED: {arms}")
    return arms


# --------------------------------------------------------------------------
FIRST = re.compile(r"Solving for (\w+), Initial residual = ([-\d.eE+]+)")


def first_solve_series(log_path):
    out, cur, seen = [], None, set()
    for line in pathlib.Path(log_path).read_text(errors="replace").splitlines():
        m = re.match(r"^Time = (\d+)$", line.strip())
        if m:
            if cur is not None:
                out.append(cur)
            cur, seen = {"iteration": int(m.group(1))}, set()
            continue
        if cur is None:
            continue
        f = FIRST.search(line)
        if f and f.group(1) not in seen:
            seen.add(f.group(1))
            cur[f.group(1)] = float(f.group(2))
    if cur is not None:
        out.append(cur)
    return out


def compare_residuals(a_series, b_series):
    n = min(len(a_series), len(b_series))
    mism, compared = [], 0
    for i in range(n):
        a, b = a_series[i], b_series[i]
        if a["iteration"] != b["iteration"]:
            mism.append(("iteration", i, a["iteration"], b["iteration"]))
            continue
        for k in ("Ux", "Uy", "e", "p", "k", "omega"):
            if k in a and k in b:
                compared += 1
                if a[k] != b[k]:
                    mism.append((k, a["iteration"], a[k], b[k]))
    return compared, mism


def times_of(case):
    return sorted(int(x.name) for x in pathlib.Path(case).iterdir()
                  if x.is_dir() and x.name.isdigit())


def T_track(case):
    out = []
    for t in times_of(case):
        if t == 0:
            continue
        Tv = read_scalar(pathlib.Path(case) / str(t) / "T")
        if Tv is None:
            continue
        out.append({"iteration": t, "T_max": max(Tv), "T_min": min(Tv),
                    "span": max(Tv) - min(Tv), "span_over_dyn": (max(Tv) - min(Tv)) / DYN})
    return out


def first_exceed(track, ceil):
    for r in track:
        if r["T_max"] > ceil:
            return r["iteration"]
    return None


def completion(case, ev):
    """REPORTED, never claimed. Standing rule 4's limbs, one by one."""
    log = (pathlib.Path(case) / "log.rhoSimpleFoam").read_text(errors="replace")
    rc = int((pathlib.Path(ev) / "RC.txt").read_text().strip())
    ts = times_of(case)
    last = max(ts)
    fields = sorted(p.name for p in (pathlib.Path(case) / str(last)).iterdir()
                    if p.is_file()) if last else []
    nexec = len(re.findall(r"^ExecutionTime = ", log, re.M))
    ab = re.search(r"Negative initial temperature T0: ([-\d.eE+]+)", log)
    iters = [int(m.group(1)) for m in re.finditer(r"^Time = (\d+)$", log, re.M)]
    return {"rc": rc,
            "End_line_present": bool(re.search(r"^End\s*$", log, re.M)),
            "endTime_registered": 148,
            "last_written_time": last,
            "last_time_equals_endTime": last == 148,
            "fields_at_last_time": fields,
            "ExecutionTime_count": nexec,
            "ExecutionTime_count_equals_endTime": nexec == 148,
            "last_iteration_started": max(iters) if iters else None,
            "abort_message_present": bool(ab),
            "abort_T0": float(ab.group(1)) if ab else None,
            "ALL_LIMBS_HOLD": (rc == 0 and bool(re.search(r"^End\s*$", log, re.M))
                               and last == 148 and nexec == 148),
            "NOTE": "Reported, NOT claimed. This probe grades nothing and no "
                    "completed run is claimed from any arm."}


def classify(i_gen, s20):
    if i_gen is None and s20 is not None and s20 <= REMOVED_S20:
        return "REMOVED"
    if s20 is None:
        return ("MITIGATED" if (i_gen is None or i_gen >= MITIGATED_IGEN)
                else "EXONERATED (on D1 alone; S20 ABSENT)")
    if (i_gen is None or i_gen >= MITIGATED_IGEN) or s20 <= MITIGATED_S20:
        return "MITIGATED"
    return "EXONERATED"


def main():
    arms = [a for a in ("arm0", "arm1", "arm2") if (ROOT / a / "case").exists()]
    R = {"grades_no_F12_gate": True,
         "issues_no_verdict_from_the_fixed_vocabulary": True,
         "prereg": "verification/campaign/F12_ENERGY_BOUND_DISCRIMINATOR_PREREGISTRATION.md",
         "prereg_commit": "54acad46f8b038310cfd4c52218a102d2a83e580",
         "prereg_blob": "e976f90a55ef077d623af5d609fbe32d245641d5",
         "arms_present": arms,
         "frozen_constants": {"dynamic_temperature_K": DYN, "T0_K": T0_CEIL,
                              "generous_ceiling_K": GEN_CEIL,
                              "S20_control": S20_CONTROL,
                              "i_gen_control": I_GEN_CONTROL}}

    print("L2. PLANTED-ZERO CONTROL (six arms, BOTH extrema)")
    R["L2_planted_zero"] = planted_control(ROOT / "arm0" / "case")
    print(f"   PASSED: {R['L2_planted_zero']['PASSED']} | "
          f"min plant at cell {R['L2_planted_zero']['plant_cell_index_negative']}, "
          f"max plant at cell {R['L2_planted_zero']['plant_cell_index_positive']}")

    series = {}
    for a in arms:
        series[a] = first_solve_series(ROOT / a / "case" / "log.rhoSimpleFoam")

    # ---------------- P0 : HARNESS FAITHFULNESS (arm 0) -------------------
    print("P0. HARNESS FAITHFULNESS (arm 0)")
    ref = first_solve_series(RUNG1_LOG)
    compared, mism = compare_residuals(series["arm0"], ref)
    tr0 = T_track(ROOT / "arm0" / "case")
    d0 = {r["iteration"]: r for r in tr0}

    # The control artifact must BE the committed one, verified by blob hash.
    import subprocess
    rel = CONTROL_ARTIFACT.relative_to(REPO).as_posix()
    blob_head = subprocess.check_output(["git", "-C", str(REPO), "rev-parse",
                                         f"HEAD:{rel}"]).decode().strip()
    blob_disk = subprocess.check_output(["git", "-C", str(REPO), "hash-object",
                                         rel]).decode().strip()
    if blob_head != blob_disk:
        refuse(f"control artifact on disk != HEAD ({blob_disk} vs {blob_head})")
    ctrl_track = {r["iteration"]: r for r in
                  json.loads(CONTROL_ARTIFACT.read_text())["Q2_T_min_track"]}

    # (a) THE REGISTERED CRITERION: every PRINTED digit of the six-decimal table.
    tbl, tbl_ok = {}, True
    for it, (tmx, tmn) in CONTROL_TABLE.items():
        got = d0.get(it)
        ok = (got is not None and round(got["T_max"], 6) == round(tmx, 6)
              and round(got["T_min"], 6) == round(tmn, 6))
        exact_vs_artifact = (got is not None and it in ctrl_track
                             and got["T_max"] == ctrl_track[it]["T_max"]
                             and got["T_min"] == ctrl_track[it]["T_min"])
        tbl[str(it)] = {"registered_6dp": [tmx, tmn],
                        "committed_artifact_full": [ctrl_track[it]["T_max"],
                                                    ctrl_track[it]["T_min"]]
                                                   if it in ctrl_track else None,
                        "arm0_measured": [got["T_max"], got["T_min"]] if got else None,
                        "meets_registered_printed_digits": bool(ok),
                        "exact_vs_committed_artifact": bool(exact_vs_artifact)}
        tbl_ok = tbl_ok and ok
    # (b) STRICTLY STRONGER, added by ADDENDUM 1: the WHOLE track, exact floats.
    full_bad, full_n = [], 0
    for it, r in ctrl_track.items():
        g = d0.get(it)
        for nm, a, b in (("T_max", g["T_max"] if g else None, r["T_max"]),
                         ("T_min", g["T_min"] if g else None, r["T_min"])):
            full_n += 1
            if a != b:
                full_bad.append([it, nm, a, b])
    full_ok = (len(full_bad) == 0 and full_n == 2 * len(ctrl_track) and full_n > 0)
    comp0 = completion(ROOT / "arm0" / "case", REC / "evidence" / "arm0")
    R["P0"] = {"residuals_compared": compared, "mismatches": len(mism),
               "first_mismatches": mism[:5],
               "rc": comp0["rc"], "abort_iteration": comp0["last_iteration_started"],
               "abort_T0": comp0["abort_T0"],
               "registered_criterion_printed_digits_MET": tbl_ok,
               "control_table": tbl,
               "ADDENDUM1_stronger_full_track": {
                   "rows": len(ctrl_track), "values_compared": full_n,
                   "mismatches": len(full_bad), "first_mismatches": full_bad[:5],
                   "PASS": full_ok,
                   "why": "strictly stronger than the registered criterion: exact "
                          "float equality against the committed control artifact "
                          "over EVERY written iteration, not the six registered ones"},
               "control_artifact_blob": blob_head,
               "PASS": (len(mism) == 0 and compared >= 885 and comp0["rc"] == 134
                        and comp0["last_iteration_started"] == 148
                        and comp0["abort_T0"] == -2.384321367 and tbl_ok and full_ok)}
    print(f"   {compared} first-solve residuals, {len(mism)} mismatches; "
          f"rc={comp0['rc']}, abort it {comp0['last_iteration_started']}, "
          f"T0={comp0['abort_T0']}")
    print(f"   registered printed-digit criterion MET: {tbl_ok} | ADDENDUM 1 "
          f"stronger full-track exact: {full_ok} "
          f"({full_n - len(full_bad)}/{full_n} values) -> "
          f"{'PASS' if R['P0']['PASS'] else 'FAIL'}")
    if not R["P0"]["PASS"]:
        R["P0_FAILED_ARMS_1_AND_2_ARE_VOID"] = True
        (REC / "evidence" / "discriminator.json").write_text(json.dumps(R, indent=1))
        print("   P0 FAILED -- the harness is the variable. No discrimination reported.")
        return 1

    # ---------------- per-arm readings -----------------------------------
    R["arms"] = {}
    for a in arms:
        tr = T_track(ROOT / a / "case")
        d = {r["iteration"]: r for r in tr}
        i_gen = first_exceed(tr, GEN_CEIL)
        i_t0 = first_exceed(tr, T0_CEIL)
        s20 = d[20]["span_over_dyn"] if 20 in d else None
        comp = completion(ROOT / a / "case", REC / "evidence" / a)
        entry = {"D1_i_gen_first_iteration_T_max_gt_342.331": i_gen,
                 "D2_S20": s20,
                 "D3_i_T0_first_iteration_T_max_gt_332.331": i_t0,
                 "D3_DEGENERACY_DISCLOSED":
                     "T0 is a bound a HEALTHY converged adiabatic solve touches "
                     "from below at its stagnation cell; a sub-Kelvin crossing is "
                     "expected of any run. Reported, never used to classify alone.",
                 "reported_iterations": {str(i): {"T_max": d[i]["T_max"],
                                                  "T_min": d[i]["T_min"],
                                                  "span_over_dyn": d[i]["span_over_dyn"]}
                                         for i in (1, 4, 8, 11, 19, 20) if i in d},
                 "T_max_over_run": max(r["T_max"] for r in tr),
                 "T_min_over_run": min(r["T_min"] for r in tr),
                 "n_written_iterations": len(tr),
                 "completion_REPORTED_not_claimed": comp,
                 "wall_s": float((REC / "evidence" / a / "WALL_S.txt").read_text().strip())}
        if a != "arm0":
            c, m = compare_residuals(series[a], series["arm0"])
            entry["L1_lever_effect"] = {
                "residuals_compared_vs_arm0": c, "mismatches_vs_arm0": len(m),
                "first_divergent_iteration": m[0][1] if m else None,
                "PASS": len(m) > 0,
                "why": "an arm whose residuals are IDENTICAL to arm 0's did not "
                       "reach the solver and is VOID"}
            if not entry["L1_lever_effect"]["PASS"]:
                entry["ARM_VOID"] = True
                entry["classification"] = None
            else:
                entry["classification"] = classify(i_gen, s20)
        else:
            # The classification rule of freeze section 4 is defined for arms 1
            # and 2 only. Arm 0 IS the control it is measured against; labelling
            # it would invite a misreading.
            entry["classification"] = "N/A -- arm 0 is the control"
        R["arms"][a] = entry
        print(f"   {a}: i_gen={i_gen}  S20={s20}  i_T0={i_t0}  "
              f"rc={comp['rc']}  last it {comp['last_iteration_started']}  "
              f"-> {entry['classification']}")

    # ---------------- P1..P5 ---------------------------------------------
    if "arm1" in arms and "arm2" in arms:
        a1, a2 = R["arms"]["arm1"], R["arms"]["arm2"]
        if a1.get("ARM_VOID") or a2.get("ARM_VOID"):
            R["PREDICTIONS"] = {"NOT GRADED": "an arm is VOID on L1"}
        else:
            s1, s2 = a1["D2_S20"], a2["D2_S20"]
            R["PREDICTIONS"] = {
              "P1_arm1_EXONERATED": {"measured": a1["classification"],
                                     "PASS": a1["classification"] == "EXONERATED"},
              "P2_arm2_EXONERATED": {"measured": a2["classification"],
                                     "PASS": a2["classification"] == "EXONERATED"},
              "P3_arm1_S20_within_20pc_of_3.282372": {
                  "band": list(P3_BAND), "measured": s1,
                  "rel_change": (s1 - S20_CONTROL) / S20_CONTROL if s1 is not None else None,
                  "PASS": (s1 is not None and P3_BAND[0] <= s1 <= P3_BAND[1])},
              "P4_arm2_S20_moves_by_at_least_20pc": {
                  "measured": s2,
                  "rel_change": (s2 - S20_CONTROL) / S20_CONTROL if s2 is not None else None,
                  "direction_NOT_predicted": True,
                  "PASS": (s2 is not None
                           and abs(s2 - S20_CONTROL) / S20_CONTROL >= 0.20)},
              "P5_at_least_one_arm_dies_differently": {
                  "arm1": [a1["completion_REPORTED_not_claimed"]["rc"],
                           a1["completion_REPORTED_not_claimed"]["last_iteration_started"]],
                  "arm2": [a2["completion_REPORTED_not_claimed"]["rc"],
                           a2["completion_REPORTED_not_claimed"]["last_iteration_started"]],
                  "PASS": not all(
                      (x["completion_REPORTED_not_claimed"]["rc"] == 134 and
                       x["completion_REPORTED_not_claimed"]["last_iteration_started"] == 148)
                      for x in (a1, a2))}}
            both_ex = (a1["classification"] == "EXONERATED"
                       and a2["classification"] == "EXONERATED")
            R["JOINT_OUTCOME"] = (
                "BOTH ARMS ARE EXONERATED -- AND THAT IS A RESULT, NOT A NULL. "
                "Neither the implicit energy-convection scheme order nor the rho "
                "under-relaxation factor removes or materially delays the early "
                "excursion above the flow's own stagnation-enthalpy ceiling. The "
                "search moves to the boundary conditions. Exonerating two "
                "candidates NAMES NO THIRD; no mechanism follows and none is "
                "asserted." if both_ex else
                f"NOT the both-exonerated outcome: arm1 {a1['classification']}, "
                f"arm2 {a2['classification']}.")
            for k, v in R["PREDICTIONS"].items():
                print(f"   {k}: {'PASS' if v['PASS'] else 'FAIL'}")
            print("   " + R["JOINT_OUTCOME"])

    (REC / "evidence" / "discriminator.json").write_text(json.dumps(R, indent=1))
    print(f"\nwritten {REC / 'evidence' / 'discriminator.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
