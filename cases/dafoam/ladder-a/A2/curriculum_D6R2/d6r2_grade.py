#!/usr/bin/env python3
"""D6R2 comparator -- grades the gates frozen in PREREGISTRATION.md section 2.

FREEZE NOTE, stated plainly and not buried.  PREREGISTRATION.md -- which carries
the gates, their thresholds, the cap and the labels -- was committed at
17eb2a2605549548d153ae6958ccd59b4637ef60, 2026-09-12T03:33:00Z.  The arm's own
age datum is 2026-09-12T03:36:01Z, 181 s later, so the gates were frozen before
any container started (rule 2).  THIS FILE was written after that container
started and is committed in its own commit; it was written while the run had
produced ZERO objective values (the first `obj.J` print had not appeared), so no
threshold in it could have been chosen to fit an answer.  It reads the frozen
thresholds; it does not set them.  If this file and PREREGISTRATION.md ever
disagree, the PREREGISTRATION is the gate and this file is the defect.

It REFUSES (exit 2) rather than degrades: a reading it cannot take is never
scored as a pass.

Usage:  python3 d6r2_grade.py [--base <run root>] [--json <out>]
"""
import argparse
import glob
import json
import os
import re
import sys

BASE_DEFAULT = "/home/ubuntu/certonomous-runs/CURRICULUM-D6R2-a2-wing-multipoint-transonic"

# ---- THE FROZEN THRESHOLDS (PREREGISTRATION.md section 2) -----------------
G1_REQUIRED_ITERATIONS = 25
G1_REQUIRED_EXIT = "Maximum Number of Iterations Exceeded"
G2_RATIO_CEILING = 0.90          # Jf <= 0.90 * J0
G3_CL_MISS_CEILING = 1.0e-3      # max_i |CL_i - target_i|
CL_TARGETS = {"cl04": 0.4, "cl05": 0.5, "cl06": 0.6}
G4_REQUIRED_TIME_DIR = "1000"
POINTS = ["mp04", "mp05", "mp06"]


def refuse(code, detail):
    print("REFUSE %s %s" % (code, json.dumps(detail)))
    sys.exit(2)


# ---- readers --------------------------------------------------------------
RE_OBJ = re.compile(r"'obj\.J':\s*array\(\[\s*([0-9eE+.\-]+)")
RE_CL = re.compile(r"'(cl0[456])\.aero_post\.functionals\.CL':\s*array\(\[\s*([0-9eE+.\-]+)")
RE_ITERS = re.compile(r"^Number of Iterations\.*:\s*(\d+)\s*$", re.M)
RE_EXIT = re.compile(r"^EXIT:\s*(.+?)\s*$", re.M)


def read_objectives(text):
    """Every obj.J printed, in order."""
    return [float(m.group(1)) for m in RE_OBJ.finditer(text)]


def read_final_cls(text):
    """The LAST value printed for each of the three scenarios."""
    out = {}
    for m in RE_CL.finditer(text):
        out[m.group(1)] = float(m.group(2))
    return out


# ---- rule 3: the planted control ------------------------------------------
def planted_control(text):
    """The reader must be SHOWN able to see a different value before a zero, a
    miss or a pass from it is believed.  Plant an objective pair and an EXIT
    line into a COPY of the log text, read the copy back, and refuse if the
    reader does not see the plant."""
    plant_j0, plant_jf = 9.876543e-01, 1.234000e-03
    planted = text + (
        "\nObjectives\n{'obj.J': array([%.6e])}\n" % plant_j0 +
        "\nObjectives\n{'obj.J': array([%.6e])}\n" % plant_jf +
        "\nEXIT: PLANTED CONTROL EXIT LINE\n"
    )
    objs = read_objectives(planted)
    exits = [m.group(1) for m in RE_EXIT.finditer(planted)]
    saw_j = len(objs) >= 2 and abs(objs[-1] - plant_jf) < 1e-12 and abs(objs[-2] - plant_j0) < 1e-12
    saw_exit = "PLANTED CONTROL EXIT LINE" in exits
    ctrl = {
        "planted_objectives": [plant_j0, plant_jf],
        "read_back_last_two": objs[-2:] if len(objs) >= 2 else objs,
        "reader_saw_planted_objectives": bool(saw_j),
        "planted_exit_line": "PLANTED CONTROL EXIT LINE",
        "reader_saw_planted_exit": bool(saw_exit),
        "original_len_unchanged": len(text) == len(text),
        "state": "EXERCISED-PASS" if (saw_j and saw_exit) else "EXERCISED-FAIL",
    }
    if not (saw_j and saw_exit):
        refuse("PLANT", ctrl)
    return ctrl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=BASE_DEFAULT)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    B = a.base
    W = os.path.join(B, "O_mp")
    R = {"item": "D6R2", "base": B,
         "prereg_sha": "17eb2a2605549548d153ae6958ccd59b4637ef60"}

    if not os.path.isdir(W):
        refuse("NO_ARM_DIR", {"expected": W})

    # ---- age datum: every artifact must be strictly newer -----------------
    dat = os.path.join(W, ".d4_age_datum")
    if not os.path.exists(dat):
        refuse("NO_AGE_DATUM", {"expected": dat})
    age_datum = int(open(dat).read().strip())
    R["age_datum_epoch"] = age_datum

    # ---- rc, from the wrapper that captured it INSIDE ---------------------
    rcf = os.path.join(B, "D6R2_ARM_RC.txt")
    if not os.path.exists(rcf):
        refuse("NO_RC", {"expected": rcf, "note": "the arm has not finished, or the wrapper died"})
    rc = int(open(rcf).read().strip())
    R["rc"] = rc

    # ---- the arm log ------------------------------------------------------
    logs = sorted(glob.glob(os.path.join(B, "O_mp_*.log")))
    if not logs:
        refuse("NO_LOG", {"glob": os.path.join(B, "O_mp_*.log")})
    log = logs[-1]
    R["log"] = log
    text = open(log, errors="replace").read()
    R["controls"] = {"planted_reader": planted_control(text)}

    # ---- G1: the optimiser terminated ITSELF at its registered budget -----
    ipf = os.path.join(W, "opt_IPOPT.txt")
    g1 = {"rc": rc, "rc_ok": rc == 0}
    if os.path.exists(ipf):
        ip = open(ipf, errors="replace").read()
        g1["opt_IPOPT_present"] = True
        g1["opt_IPOPT_newer_than_datum"] = os.path.getmtime(ipf) > age_datum
        it = RE_ITERS.search(ip)
        ex = RE_EXIT.findall(ip)
        g1["iterations"] = int(it.group(1)) if it else None
        g1["exit_line"] = ex[-1] if ex else None
    else:
        g1.update({"opt_IPOPT_present": False, "opt_IPOPT_newer_than_datum": False,
                   "iterations": None, "exit_line": None})
    g1["iterations_as_registered"] = g1["iterations"] == G1_REQUIRED_ITERATIONS
    g1["exit_as_registered"] = bool(g1["exit_line"]) and G1_REQUIRED_EXIT in g1["exit_line"]
    g1["verdict"] = "PASS" if (g1["rc_ok"] and g1["opt_IPOPT_present"] and
                               g1["opt_IPOPT_newer_than_datum"] and
                               g1["iterations_as_registered"] and
                               g1["exit_as_registered"]) else "FAIL"
    R["G1"] = g1

    # ---- G2: the physics gate and its band --------------------------------
    objs = read_objectives(text)
    g2 = {"n_obj_prints": len(objs)}
    if len(objs) >= 2:
        j0, jf = objs[0], objs[-1]
        g2.update({"J0": j0, "Jf": jf,
                   "ratio_Jf_over_J0": (jf / j0) if j0 else None,
                   "reduction_percent": (100.0 * (1.0 - jf / j0)) if j0 else None,
                   "ceiling": G2_RATIO_CEILING})
        g2["verdict"] = "PASS" if (j0 > 0 and jf <= G2_RATIO_CEILING * j0) else "FAIL"
    else:
        g2["verdict"] = "FAIL"
        g2["reason"] = "fewer than two obj.J prints in the log"
    R["G2"] = g2

    # ---- G3: the lift constraints at the final design ---------------------
    cls = read_final_cls(text)
    g3 = {"final_CL": cls, "targets": CL_TARGETS, "ceiling": G3_CL_MISS_CEILING}
    if set(cls) == set(CL_TARGETS):
        misses = {k: abs(cls[k] - CL_TARGETS[k]) for k in CL_TARGETS}
        g3["misses"] = misses
        g3["max_miss"] = max(misses.values())
        g3["verdict"] = "PASS" if g3["max_miss"] <= G3_CL_MISS_CEILING else "FAIL"
    else:
        g3["verdict"] = "FAIL"
        g3["reason"] = "not all three scenarios printed a CL"
    R["G3"] = g3

    # ---- G4: the results are saved, and they are THIS run's ---------------
    g4 = {"required_time_dir": G4_REQUIRED_TIME_DIR, "artifacts": {}}
    ok = True
    for name in ("OptView.hst", "opt_IPOPT.txt"):
        p = os.path.join(W, name)
        ex = os.path.exists(p)
        newer = ex and os.path.getmtime(p) > age_datum
        g4["artifacts"][name] = {"present": ex, "newer_than_datum": newer,
                                 "bytes": os.path.getsize(p) if ex else 0}
        ok = ok and ex and newer
    for mp in POINTS:
        hits = sorted(glob.glob(os.path.join(W, mp, "processor*", G4_REQUIRED_TIME_DIR)))
        newest = max((os.path.getmtime(h) for h in hits), default=0)
        g4["artifacts"][mp] = {"processor_time_dirs": len(hits),
                               "newest_mtime": newest,
                               "newer_than_datum": bool(hits) and newest > age_datum}
        ok = ok and bool(hits) and newest > age_datum
    g4["verdict"] = "PASS" if ok else "FAIL"
    R["G4"] = g4

    # ---- THE LABEL, from the frozen table ---------------------------------
    if g1["verdict"] == "PASS" and g4["verdict"] == "PASS":
        verdict = "PASS" if (g2["verdict"] == "PASS" and g3["verdict"] == "PASS") else "GATE FAIL"
    else:
        verdict = "NOT A RESULT"
    R["verdict"] = verdict

    # ---- the ledger's cost row, reported beside the verdict ---------------
    led = os.path.join(B, "ledger.txt")
    row = None
    if os.path.exists(led):
        for line in open(led, errors="replace"):
            if line.startswith("ARM=O_mp"):
                row = line.strip()
    R["ledger_row"] = row
    if row:
        m = re.search(r"core_min=([0-9.]+)", row)
        R["core_min_measured"] = float(m.group(1)) if m else None
        R["core_min_registered_prediction"] = 786.0
        if R.get("core_min_measured"):
            R["actual_over_predicted"] = round(R["core_min_measured"] / 786.0, 3)

    out = a.json or os.path.join(B, "D6R2_grade.json")
    with open(out, "w") as f:
        json.dump(R, f, indent=1, sort_keys=True)
    print("VERDICT %s  G1=%s G2=%s G3=%s G4=%s  written=%s" % (
        verdict, g1["verdict"], g2["verdict"], g3["verdict"], g4["verdict"], out))
    if g2.get("J0") is not None:
        print("  J0=%.8g  Jf=%.8g  reduction=%.2f%%  band: Jf <= %.2f x J0" % (
            g2["J0"], g2["Jf"], g2["reduction_percent"], G2_RATIO_CEILING))
    if g3.get("max_miss") is not None:
        print("  max CL miss = %.3e  (ceiling %.1e)  CL=%s" % (
            g3["max_miss"], G3_CL_MISS_CEILING, g3["final_CL"]))
    print("  IPOPT: iterations=%s exit=%r" % (g1["iterations"], g1["exit_line"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
