#!/usr/bin/env python3
"""D6RF11 comparator -- the gates frozen in PREREGISTRATION.md section 3.

This file is committed IN THE SAME COMMIT as the pre-registration, before any
container starts.  The rule-2 departure disclosed on D6R2 at bc3aa7ce2 -- a
grading path outside the freeze -- is not repeated.

It REFUSES (exit 2) rather than degrades.
"""
import argparse
import glob
import json
import os
import re
import sys

BASE_DEFAULT = "/home/ubuntu/certonomous-runs/CURRICULUM-D6RF11-a2-wing-fd-simplec-probe"

# ---- THE FROZEN THRESHOLDS (PREREGISTRATION.md section 3) -----------------
G1_MAX_PRIMAL_FAILURES = 0            # D6RF3 recorded 17
G2_ACCEPT_FLOOR = 1.0e-05             # primalMinResTol 1e-8 x primalMinResTolDiff 1e3 (N-D43: the PRODUCT)
G3_MIN_FD_SAMPLES = 1
FD_JSONL = "d6rf3_fd_endpoint.jsonl"  # the byte-identical instrument's own output name

RE_P_INITRES = re.compile(r"^p initRes:\s*([0-9eE+.\-]+)", re.M)
RE_FAILED = re.compile(r"Primal solution failed!")


def refuse(code, detail):
    print("REFUSE %s %s" % (code, json.dumps(detail)))
    sys.exit(2)


def planted_control(text):
    """Rule 3.  The reader is SHOWN able to see a different value before any
    zero, count or residual it reports is believed."""
    planted = text + "\np initRes: 1.234000e-03 finalRes: 1e-12 nIters: 1\nPrimal solution failed!\n"
    res = RE_P_INITRES.findall(planted)
    fails = len(RE_FAILED.findall(planted))
    base_fails = len(RE_FAILED.findall(text))
    saw_res = bool(res) and abs(float(res[-1]) - 1.234e-03) < 1e-15
    saw_fail = fails == base_fails + 1
    ctrl = {"planted_p_initRes": 1.234e-03,
            "read_back_last_p_initRes": float(res[-1]) if res else None,
            "reader_saw_planted_residual": bool(saw_res),
            "baseline_failure_count": base_fails,
            "planted_failure_count": fails,
            "reader_saw_planted_failure": bool(saw_fail),
            "state": "EXERCISED-PASS" if (saw_res and saw_fail) else "EXERCISED-FAIL"}
    if not (saw_res and saw_fail):
        refuse("PLANT", ctrl)
    return ctrl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=BASE_DEFAULT)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    B, W = a.base, os.path.join(a.base, "F_probe")
    R = {"item": "D6RF11", "base": B}

    if not os.path.isdir(W):
        refuse("NO_ARM_DIR", {"expected": W})
    dat = os.path.join(W, ".d6rf11_age_datum")
    if not os.path.exists(dat):
        refuse("NO_AGE_DATUM", {"expected": dat})
    age = int(open(dat).read().strip())
    R["age_datum_epoch"] = age

    rcf = os.path.join(B, "D6RF11_ARM_RC.txt")
    if not os.path.exists(rcf):
        refuse("NO_RC", {"expected": rcf, "note": "the arm has not finished, or the launcher died"})
    rc = int(open(rcf).read().strip())
    R["rc"] = rc

    logs = sorted(glob.glob(os.path.join(B, "F_probe_*.log")))
    if not logs:
        refuse("NO_LOG", {"glob": os.path.join(B, "F_probe_*.log")})
    text = open(logs[-1], errors="replace").read()
    R["log"] = logs[-1]
    R["controls"] = {"planted_reader": planted_control(text)}

    # ---- G1: the primal no longer fails -------------------------------
    nfail = len(RE_FAILED.findall(text))
    R["G1"] = {"primal_failures": nfail, "ceiling": G1_MAX_PRIMAL_FAILURES,
               "d6rf3_measured": 17,
               "verdict": "PASS" if nfail <= G1_MAX_PRIMAL_FAILURES else "FAIL"}

    # ---- G2: the binding field clears its floor ------------------------
    res = [float(x) for x in RE_P_INITRES.findall(text)]
    g2 = {"n_p_initRes_prints": len(res), "floor": G2_ACCEPT_FLOOR,
          "floor_provenance": "primalMinResTol 1e-8 x primalMinResTolDiff 1e3, UNCHANGED from D6RF3 "
                              "(d6rf3_opt_runScript.py:67-68). The tolerance is not touched.",
          "d6rf3_measured_plateau": 1.3162e-05,
          "d6rf10_R3_measured": 6.323e-06}
    if res:
        g2["last_p_initRes"] = res[-1]
        g2["ratio_to_floor"] = res[-1] / G2_ACCEPT_FLOOR
        g2["verdict"] = "PASS" if res[-1] < G2_ACCEPT_FLOOR else "FAIL"
    else:
        g2["verdict"] = "FAIL"
        g2["reason"] = "no p initRes line in the log"
    R["G2"] = g2

    # ---- G3: at least one FD sample exists -----------------------------
    p = os.path.join(W, FD_JSONL)
    g3 = {"file": p, "min_samples": G3_MIN_FD_SAMPLES}
    if os.path.exists(p):
        rows = [l for l in open(p, errors="replace") if l.strip()]
        g3.update({"present": True, "newer_than_datum": os.path.getmtime(p) > age,
                   "n_sample_rows": len(rows)})
        g3["verdict"] = "PASS" if (g3["newer_than_datum"] and len(rows) >= G3_MIN_FD_SAMPLES) else "FAIL"
    else:
        g3.update({"present": False, "newer_than_datum": False, "n_sample_rows": 0,
                   "verdict": "FAIL"})
    R["G3"] = g3

    # ---- G4: it is this run's ------------------------------------------
    g4 = {"rc_captured_inside_launcher": True, "rc": rc,
          "log_newer_than_datum": os.path.getmtime(logs[-1]) > age}
    g4["verdict"] = "PASS" if g4["log_newer_than_datum"] else "FAIL"
    R["G4"] = g4

    if g4["verdict"] != "PASS":
        verdict = "NOT A RESULT"
    elif all(R[g]["verdict"] == "PASS" for g in ("G1", "G2", "G3")):
        verdict = "PASS"
    else:
        verdict = "GATE FAIL"
    R["verdict"] = verdict

    led = os.path.join(B, "ledger.txt")
    if os.path.exists(led):
        for line in open(led, errors="replace"):
            if line.startswith("ARM=F_probe"):
                R["ledger_row"] = line.strip()
                m = re.search(r"core_min=([0-9.]+)", line)
                if m:
                    R["core_min_measured"] = float(m.group(1))
                    R["core_min_registered_prediction"] = 1236.0
                    R["actual_over_predicted"] = round(float(m.group(1)) / 1236.0, 3)

    out = a.json or os.path.join(B, "D6RF11_grade.json")
    json.dump(R, open(out, "w"), indent=1, sort_keys=True)
    print("VERDICT %s  G1=%s G2=%s G3=%s G4=%s  written=%s" % (
        verdict, R["G1"]["verdict"], g2["verdict"], g3["verdict"], g4["verdict"], out))
    print("  primal failures = %d (ceiling %d; D6RF3 measured 17)" % (nfail, G1_MAX_PRIMAL_FAILURES))
    if "last_p_initRes" in g2:
        print("  last p initRes = %.6e  (floor %.1e, ratio %.4f)" % (
            g2["last_p_initRes"], G2_ACCEPT_FLOOR, g2["ratio_to_floor"]))
    print("  FD sample rows  = %d (minimum %d)" % (g3["n_sample_rows"], G3_MIN_FD_SAMPLES))
    print("  BOUNDS: PATCHED ROW ONLY -- not a verdict about DAFoam (charter two-row rule).")
    print("  BOUNDS: one FD sample is a PROBE, not the FD table the charter's bright line requires.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
