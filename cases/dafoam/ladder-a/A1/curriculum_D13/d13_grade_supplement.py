#!/usr/bin/env python3
"""D13 grader, SUPPLEMENT under VERIFICATION_CHARTER section 2d.1.

THE FROZEN GRADER `d13_grade.py` (md5 f0b2ccfd0271d1301eec70df820d32e3) RAN
FIRST AND REFUSED (exit 2), and that refusal is published as the primary
grading outcome: run root `D13_GRADE_FROZEN_REFUSAL.txt`, RESULTS.md section 3.
This file differs from it in EXACTLY ONE HUNK -- the age-guard limb of
`completion()` -- and `d13_grade_supplement.diff` carries the proof.

NO GATE, THRESHOLD, CAP, BAND, LABEL OR START VECTOR IS ALTERED.  Not one
graded quantity moves: not a CD, not a shape component, not an FD number, not
an equivalence band edge.  The only thing that changes is whether G0's
completion clause can be EVALUATED AT ALL.

D13 grader.  Reads what the five starts wrote, runs every control, applies
the FROZEN gates, and prints the per-start verdicts and the cross-start basin
verdict from the FIXED vocabulary.

Frozen by the commit that carries
`cases/dafoam/ladder-a/A1/curriculum_D13/PREREGISTRATION.md`.
NOT EDITED AFTER THE FIRST LAUNCH.

REFUSES (exit 2) RATHER THAN DEGRADES.  Every band, tolerance and start vector
lives in `d13_basin.py` and none of them is re-stated here.
"""
import argparse
import glob
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d13_basin as B

# Instrument identity, frozen at the pre-registration commit.  The grader's own
# md5 is in PREREGISTRATION.md section 9; it cannot carry its own hash.
EXPECT_MD5 = {
    "d13_basin.py": "e96d77ff53e356d67f54a4cc46338c0e",
    "d13_opt_runScript.py": "bf6500c7ef89f7f5c8be02292e274181",
    "d1_fd_endpoint.py": "7e454d2f1830a40086465d9b5c57a941",
}
PATCHED_IDWARP_SO_MD5 = "85f59e87253e0a71a813f64ca6e4c425"
PATCHED_IMAGE_ID = ("sha256:2927768a16acdea0330180fff95c8879"
                    "c1dda9efcf6028728523b7dee30f6d35")

# Cost, frozen in PREREGISTRATION.md section 8.
COST_POINT_CORE_MIN = 40.0
COST_BAND_CORE_MIN = 80.0
COST_CEILING_CORE_MIN = 100.0          # an overrun STOPS the run
COST_PER_START_CEILING_CORE_MIN = 25.0
RATE_USD_PER_CORE_H = 0.0513           # REPORTED-BY-OWNER, NOT MEASURED

LEDGER = re.compile(
    r"ARM=(?P<arm>\S+)\s+IMG=(?P<img>\S+)\s+TASK=(?P<task>\S+)\s+"
    r"OPT=(?P<opt>\S+)\s+rc=(?P<rc>-?\d+)\s+wall_s=(?P<wall>\d+)\s+"
    r"ranks=(?P<ranks>\d+)\s+core_min=(?P<cm>[\d.]+)\s+"
    r"inspect\(exit,oomkilled\)=\[(?P<inspect>[^\]]*)\]\s+"
    r"maxrss_GiB=(?P<rss>\S+)\s+log=(?P<log>\S+)")


def md5_of(p):
    h = hashlib.md5()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def assert_instruments(where):
    """The frozen file must BE the file that ran (CLAUDE.md rule 2)."""
    out = {}
    for name, want in EXPECT_MD5.items():
        p = os.path.join(where, name)
        if not os.path.isfile(p):
            B._refuse("INSTRUMENT_MISSING", {"path": p})
        got = md5_of(p)
        if got != want:
            B._refuse("INSTRUMENT_MD5", {"path": p, "expected": want,
                                         "found": got})
        out[name] = got
    print("D13_INSTRUMENT_IDENTITY OK %s" % json.dumps(out, sort_keys=True))
    return out


def read_ledger(path):
    if not os.path.isfile(path):
        B._refuse("NO_LEDGER", {"path": path})
    rows = {}
    with open(path) as fh:
        for line in fh:
            m = LEDGER.search(line)
            if m:
                rows[m.group("arm")] = m.groupdict()
    if not rows:
        B._refuse("LEDGER_EMPTY", {"path": path})
    return rows


def completion(arm_dir, ep_path, led, log_path, ipopt):
    """CLAUDE.md rule 4, ALL of it, mapped onto an optimisation arm.  The
    mapping is registered in PREREGISTRATION.md section 7 and is stated here so
    no clause is silently dropped:

      rc == 0                       -> the launcher's rc
      container verdict             -> .State.ExitCode 0, .State.OOMKilled false
      an `End` line                 -> IPOPT's own `EXIT:` statement present
      last time == endTime          -> majors < the registered max_iter cap,
                                       i.e. the run stopped on ITS OWN
                                       criterion and not on the cap
      fields present                -> the endpoint JSON's full key set,
                                       asserted BY NAME by read_endpoint
      AGE GUARD: every field newer   -> the endpoint JSON is NEWER than this
      than the case's own 0/T           arm's own `0/U`, which the launcher
                                        restores at staging and which therefore
                                        dates the run allowed to produce it
    """
    f = {}
    f["rc_zero"] = (int(led["rc"]) == 0)
    insp = led["inspect"].split()
    f["container_exit_zero"] = (len(insp) == 2 and insp[0] == "0")
    f["not_oomkilled"] = (len(insp) == 2 and insp[1] == "false")
    f["ipopt_exit_present"] = bool(ipopt["exit"])
    f["terminated_not_capped"] = (ipopt["majors"] < B.MAX_ITER_CAP)
    f["endpoint_present"] = os.path.isfile(ep_path)
    f["log_sentinel"] = bool(glob.glob(log_path + ".ok.*"))
    # ---- AGE GUARD: NOT EXERCISED, and the reason is MEASURED --------------
    # CLAUDE.md rule 4's age guard presumes a field the run does NOT rewrite
    # ("0/T is touched last at launch and so dates the run allowed to produce
    # the answer").  A DAFoam optimisation rewrites 0/ IN PLACE: it gzips 0/U
    # to 0/U.gz during the solve.  MEASURED: 0/U is absent on all five D13 arms
    # AND on D1's own closed arm O; 0/U.gz carries an END-of-run mtime ONE
    # SECOND before the endpoint JSON, so handing it to the guard would
    # manufacture a meaningless green.  The clause is therefore recorded as NOT
    # EXERCISED rather than satisfied on a reference that does not date the
    # launch.
    #
    # Its EVIDENTIARY PURPOSE -- proving the answer was not produced by an
    # earlier run in a reused directory -- is discharged by a STRONGER,
    # PRE-LAUNCH assertion read here from the arm's own launch record: G8's
    # cold start rm -rf'd the arm directory, re-copied it from base/, and
    # asserted "no stale endpoint" BEFORE the container started.  That proves
    # the answer file did not exist AT ALL, and it was asserted in advance
    # rather than inferred afterwards.
    # Filed as PREREGISTRATION.md ADDENDUM 1 under VERIFICATION_CHARTER section
    # 2d.1, whose four conditions are enumerated with evidence there.
    ref = os.path.join(arm_dir, "0", "U")
    f["age_guard"] = "NOT EXERCISED"
    f["age_guard_reference_present"] = os.path.isfile(ref)
    f["age_guard_reason"] = ("0/U absent: DAFoam gzips it to 0/U.gz during the "
                             "solve; no launch-dated field artifact survives")
    if not f["endpoint_present"]:
        B._refuse("NO_ENDPOINT", {"path": ep_path})
    arm = os.path.basename(arm_dir)
    g8p = os.path.join(os.path.dirname(arm_dir), arm + "_launch.out")
    asserted = False
    if os.path.isfile(g8p):
        t = open(g8p).read()
        asserted = ("G8 OK (%s)" % arm) in t and "no stale endpoint" in t
    if not asserted:
        B._refuse("G8_COLD_START_NOT_ASSERTED", {"arm": arm, "path": g8p})
    f["g8_cold_start_asserted_prelaunch"] = True
    f["complete"] = all(f[k] for k in
                        ("rc_zero", "container_exit_zero", "not_oomkilled",
                         "ipopt_exit_present", "endpoint_present",
                         "log_sentinel", "g8_cold_start_asserted_prelaunch"))
    return f


def image_identity(log_path):
    with open(log_path, "rb") as fh:
        txt = fh.read().decode("utf-8", "replace")
    m = re.findall(r"IDWARP_SO_MD5:\s*([0-9a-f]{32})", txt)
    n = re.findall(r"nProcs\s*:\s*(\d+)", txt)
    if not m:
        B._refuse("NO_IDWARP_MD5", {"log": log_path})
    ok = (m[-1] == PATCHED_IDWARP_SO_MD5)
    if not ok:
        B._refuse("WRONG_IMAGE", {"log": log_path, "found": m[-1],
                                  "expected": PATCHED_IDWARP_SO_MD5})
    return {"idwarp_so_md5": m[-1], "patched": ok,
            "nProcs": (int(n[0]) if n else None)}


def grade_start(root, k, led_rows):
    arm = "s%d" % k
    arm_dir = os.path.join(root, arm)
    ep_path = os.path.join(arm_dir, "endpoint_d13.json")
    ip_path = os.path.join(arm_dir, "opt_IPOPT.txt")
    if arm not in led_rows:
        B._refuse("NO_LEDGER_ROW", {"arm": arm})
    led = led_rows[arm]
    log_path = os.path.join(root, led["log"])
    img = image_identity(log_path)
    ipopt = B.read_ipopt(ip_path, where=arm)
    ep = B.read_endpoint(ep_path, require_d13=True, where=arm)

    # the two independent termination channels must agree
    if ep["ipopt_exit"] != ipopt["exit"] or ep["ipopt_majors"] != ipopt["majors"]:
        B._refuse("TERMINATION_CHANNELS_DISAGREE",
                  {"arm": arm, "in_json": [ep["ipopt_exit"],
                                           ep["ipopt_majors"]],
                   "in_file": [ipopt["exit"], ipopt["majors"]]})
    if ep["start_id"] != k:
        B._refuse("START_ID_MISMATCH", {"arm": arm, "in_json": ep["start_id"]})
    want_sh, want_pv = B.start_vectors(k)
    dsh = max(abs(a - b) for a, b in zip(ep["start_shape"], want_sh))
    dpv = abs(ep["start_patchV"][1] - want_pv[1])
    if dsh > 0.0 or dpv > 0.0:
        B._refuse("START_VECTOR_MISMATCH",
                  {"arm": arm, "max_shape_dev": dsh, "aoa_dev": dpv})

    comp = completion(arm_dir, ep_path, led, log_path, ipopt)

    # ---- G1 termination -------------------------------------------------
    g1 = {"exit": ipopt["exit"], "majors": ipopt["majors"],
          "nlp_error": ipopt["nlp_error"], "cap": B.MAX_ITER_CAP}
    if ipopt["exit"] == B.IPOPT_OK and ipopt["majors"] < B.MAX_ITER_CAP:
        g1["verdict"] = "PASS"
    elif ipopt["majors"] >= B.MAX_ITER_CAP:
        g1["verdict"] = "GATE REACHED"      # a cap-stop is NEVER a PASS
    else:
        g1["verdict"] = "GATE FAIL"

    # ---- G2 feasibility --------------------------------------------------
    dcl = abs(ep["CL"] - B.CL_TARGET)
    cons = ep["cons"]
    rows = []
    bad = []
    for name, lo, hi in (("geometry.thickcon", B.THICKCON_LO, B.THICKCON_HI),
                         ("geometry.volcon", B.VOLCON_LO, None),
                         ("geometry.rcon", B.RCON_LO, None)):
        v = cons.get(name)
        if not isinstance(v, list) or len(v) == 0:
            B._refuse("CONSTRAINT_ROWS_EMPTY",
                      {"arm": arm, "family": name,
                       "n": (len(v) if isinstance(v, list) else -1)})
        for i, x in enumerate(v):
            inb = (x >= lo) and (hi is None or x <= hi)
            rows.append(inb)
            if not inb:
                bad.append({"family": name, "i": i, "value": x})
    g2 = {"abs_CL_err": dcl, "tol": B.CL_TOL, "n_constraint_rows": len(rows),
          "n_out_of_bound": len(bad), "out_of_bound": bad,
          "constr_viol": ipopt["constr_viol"]}
    g2["verdict"] = "PASS" if (dcl <= B.CL_TOL and not bad
                               and (ipopt["constr_viol"] is None
                                    or ipopt["constr_viol"]
                                    <= B.CONSTR_VIOL_TOL)) else "GATE FAIL"
    if len(rows) != 23:
        # D1 measured 20 thickcon + 1 volcon + 2 rcon = 23 geometric rows.
        # A different count is not graded silently.
        print("D13_NOTE arm=%s geometric_constraint_rows=%d (D1 measured 23)"
              % (arm, len(rows)))

    # ---- G3 the FD table, WITH THE COUNT REFUSAL -------------------------
    g3 = B.fd_table_gate(ep, where=arm)

    if not comp["complete"]:
        verdict = "NOT A RESULT"
    elif g1["verdict"] == "GATE REACHED":
        verdict = "GATE REACHED"
    elif "GATE FAIL" in (g1["verdict"], g2["verdict"], g3["verdict"]):
        verdict = "GATE FAIL"
    else:
        verdict = "PASS"

    return {"arm": arm, "start_id": k, "image": img, "ledger": led,
            "completion": comp, "G1": g1, "G2": g2,
            "G3": {k2: g3[k2] for k2 in
                   ("n_present", "n_graded", "worst_rel_err", "sign_flips",
                    "verdict")},
            "G3_rows": g3["rows"], "trivial": ep["trivial"],
            "CD": ep["CD"], "CL": ep["CL"], "shape": ep["shape"],
            "patchV": ep["patchV"], "feasible_CD": ep["feasible_CD"],
            "start_CD": None, "driver_wall_s": ep["driver_wall_s"],
            "core_min": float(led["cm"]), "verdict": verdict}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--instruments", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    inst = assert_instruments(a.instruments)
    led_rows = read_ledger(os.path.join(a.root, "ledger.txt"))

    starts = {}
    for k in B.START_IDS:
        starts[k] = grade_start(a.root, k, led_rows)
        s = starts[k]
        print("D13_START s%d verdict=%s exit=%r majors=%d CD=%.17g "
              "|CL-0.5|=%.6e n_graded=%d worst_fd=%.6e core_min=%.3f"
              % (k, s["verdict"], s["G1"]["exit"], s["G1"]["majors"],
                 s["CD"], s["G2"]["abs_CL_err"], s["G3"]["n_graded"],
                 s["G3"]["worst_rel_err"], s["core_min"]))

    # ---- controls, on REAL D13 evidence, not a fixture -------------------
    wd = os.path.join(a.root, "controls_grade")
    ctl_src = os.path.join(a.root, "s1", "endpoint_d13.json")
    ctl = {}
    ctl["planted_zero"] = B.planted_zero_control(ctl_src, wd,
                                                 src_md5=md5_of(ctl_src))
    ctl["negative"] = B.negative_control(ctl_src, wd)
    ctl["emptyset"] = B.emptyset_control(ctl_src)
    ctl["shortset"] = B.shortset_control(ctl_src)
    ctl["keyset"] = B.keyset_control(ctl_src, wd)
    ctl["planted_zero_D1"] = B.planted_zero_control(
        B.D1_ENDPOINT_JSON, wd, src_md5=B.D1_ENDPOINT_MD5, require_d13=False)
    if not all(v["pass"] for v in ctl.values()):
        B._refuse("CONTROLS_FAILED",
                  {k: v["pass"] for k, v in ctl.items()})
    print("D13_CONTROLS ALL PASS")

    # ---- the basin comparison against the FROZEN band --------------------
    d1 = B.read_endpoint(B.D1_ENDPOINT_JSON, require_d13=False, where="D1_armO")
    if md5_of(B.D1_ENDPOINT_JSON) != B.D1_ENDPOINT_MD5:
        B._refuse("D1_REFERENCE_MD5", {"path": B.D1_ENDPOINT_JSON})
    for key, want in (("CD", B.D1_REF["CD"]),):
        if d1[key] != want:
            B._refuse("D1_REFERENCE_DRIFT", {"key": key, "on_disk": d1[key],
                                             "registered": want})

    gradeable = [k for k in B.START_IDS
                 if starts[k]["verdict"] in ("PASS",)]
    members = [("D1", d1)] + [("S%d" % k, {"CD": starts[k]["CD"],
                                           "shape": starts[k]["shape"],
                                           "patchV": starts[k]["patchV"]})
                              for k in gradeable]
    if len(members) < 3:
        B._refuse("TOO_FEW_MEMBERS",
                  {"n_members": len(members), "gradeable_starts": gradeable,
                   "note": "a basin verdict needs at least two graded starts "
                           "beside the D1 reference"})
    basin = B.basin_verdict(members)
    for p in basin["pairs"]:
        print("D13_PAIR %s-%s cell=%s dCD=%.6e dSHAPE=%.6e dAOA=%.6e"
              % (p["a"], p["b"], p["cell"],
                 p["channels"]["CD"]["delta"],
                 p["channels"]["shape_Linf"]["delta"],
                 p["channels"]["aoa_deg"]["delta"]))
    print("D13_BASIN verdict=%s n_pairs=%d same=%d unresolved=%d different=%d"
          % (basin["verdict"], basin["n_pairs"], basin["n_same"],
             basin["n_unresolved"], basin["n_different"]))

    total_cm = sum(float(r["cm"]) for r in led_rows.values())
    cost = {"total_core_min_gross": round(total_cm, 3),
            "point_core_min": COST_POINT_CORE_MIN,
            "band_core_min": COST_BAND_CORE_MIN,
            "ceiling_core_min": COST_CEILING_CORE_MIN,
            "ratio_actual_over_point": round(total_cm / COST_POINT_CORE_MIN, 4),
            "usd_derived": round(total_cm / 60.0 * RATE_USD_PER_CORE_H, 6),
            "cost_basis": "c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, "
                          "NOT MEASURED; dollars DERIVED, not measured",
            "overrun": bool(total_cm > COST_CEILING_CORE_MIN)}
    print("D13_COST gross_core_min=%.3f ratio_vs_point=%.4f usd_DERIVED=%.6f "
          "overrun=%s" % (total_cm, cost["ratio_actual_over_point"],
                          cost["usd_derived"], cost["overrun"]))

    per_start = {("s%d" % k): starts[k]["verdict"] for k in B.START_IDS}
    if any(v == "NOT A RESULT" for v in per_start.values()):
        item = "NOT A RESULT"
    elif basin["verdict"] == "PASS" and all(v == "PASS"
                                            for v in per_start.values()):
        item = "PASS"
    else:
        item = basin["verdict"]
    print("D13_ITEM verdict=%s per_start=%s"
          % (item, json.dumps(per_start, sort_keys=True)))

    rep = {"instruments": inst, "image_id_registered": PATCHED_IMAGE_ID,
           "bands": {"EPS_CD": B.EPS_CD, "EPS_SHAPE": B.EPS_SHAPE,
                     "EPS_AOA": B.EPS_AOA, "DFD_REL": B.DFD_REL,
                     "DFD_CD": B.DFD_CD, "DFD_SHAPE": B.DFD_SHAPE,
                     "DFD_AOA": B.DFD_AOA},
           "starts": starts, "controls": ctl, "basin": basin, "cost": cost,
           "per_start_verdict": per_start, "item_verdict": item}
    with open(a.out, "w") as fh:
        json.dump(rep, fh, indent=1, default=str)
    print("D13_REPORT %s" % a.out)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except B.Refuse as exc:
        print("D13_GRADE REFUSED %s" % exc, flush=True)
        raise SystemExit(2)
