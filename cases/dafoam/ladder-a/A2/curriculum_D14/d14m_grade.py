#!/usr/bin/env python3
"""D14-M COMPARATOR -- reads the regenerated mesh's checkMesh record off disk and grades
it against the registered gates and predictions.  Computes nothing about physics; renders
verdicts from the FIXED vocabulary only (PASS / GATE REACHED / GATE FAIL / NOT A RESULT /
BLOCKED / PENDING).  No `assert` anywhere (L-332): refusals are exit 2; the selftest
(--selftest) runs its planted controls under whatever interpreter runs it, and the
driving shell runs it under both python3 and python3 -O.

Field classes (L-342, d4d0c29d): PHYSICS-CRITICAL = the container's own rc from `docker
inspect`, OOMKilled, the checkMesh log's presence/`Mesh OK.`/numbers, the age guard.
INFRASTRUCTURE = wall/core-min, MemAvailable samples, container name, driver pid.  Only a
physics-critical defect produces NOT A RESULT; an infrastructure defect voids the cost
claim and is reported beside the verdict.
"""
import ast
import json
import os
import re
import sys
import time

# ---- REGISTERED (PREREGISTRATION.md section 4-6; the freeze is the document) ----------
REF = {  # D4's baseline mesh, /home/ubuntu/certonomous-runs/A2-mach-wing/checkMesh.log (2026-07-28)
    "cells": 38304, "points": 40209, "faces": 116756, "internal_faces": 113068,
    "max_aspect_ratio": 684.4022128, "max_non_orthogonality": 66.96543422,
    "avg_non_orthogonality": 11.48508811, "max_skewness": 1.339283343,
}
REPRO_REL_TOL = 1.0e-6          # G14-4: same generator, same inputs, same image -> reproduction
DRIFT_REL_WORSE = 0.10          # G14-4: > +10 % on max aspect ratio = the GENERATOR_FINDING class, named
NONORTHO_HARD = 70.0            # MESH_STANDARD 3.1 hard gate (warning band 65-70 reported)
NONORTHO_WARN = 65.0
SKEW_HARD = 4.0                 # MESH_STANDARD 3.2
ASPECT_ADVISORY = 1000.0        # MESH_STANDARD 3.3 (advisory; flag with non-ortho > 60 or skew > 2)
PRED = {"P5_pyhyp_cpu_s": (2.0, 10.0), "P6_wall_s_max": 120.0, "P6_core_min_band": (0.3, 2.0)}
COST_PREDICTED_CORE_MIN = 0.67
EXPECTED_UNITS = 14


class Refusal(Exception):
    pass


def count_asserts(path):
    return sum(1 for n in ast.walk(ast.parse(open(path).read())) if isinstance(n, ast.Assert))


def parse_checkmesh(txt):
    out = {}
    for key, rx in (("cells", r"^\s*cells:\s+(\d+)"), ("points", r"^\s*points:\s+(\d+)"),
                    ("faces", r"^\s*faces:\s+(\d+)"), ("internal_faces", r"^\s*internal faces:\s+(\d+)"),
                    ("max_aspect_ratio", r"Max aspect ratio = ([-+0-9.eE]+)"),
                    ("max_skewness", r"Max skewness = ([-+0-9.eE]+)")):
        m = re.search(rx, txt, re.M)
        if m:
            out[key] = float(m.group(1)) if "." in m.group(1) or "e" in m.group(1).lower() else int(m.group(1))
    m = re.search(r"Mesh non-orthogonality Max: ([-+0-9.eE]+) average: ([-+0-9.eE]+)", txt)
    if m:
        out["max_non_orthogonality"] = float(m.group(1)); out["avg_non_orthogonality"] = float(m.group(2))
    out["mesh_ok_line"] = bool(re.search(r"^Mesh OK\.$", txt, re.M))
    out["failed_checks"] = len(re.findall(r"Failed \d+ mesh checks", txt))
    return out


def parse_ledger_row(txt, arm="MESH"):
    rows = [l for l in txt.splitlines() if l.startswith("ARM=%s " % arm)]
    if len(rows) != 1:
        raise Refusal("ledger carries %d ARM=%s rows; exactly one is required" % (len(rows), arm))
    kv = dict(re.findall(r"(\w+)=([^\s]+)", rows[0]))
    return kv


def parse_pyhyp_cpu(txt):
    last = None
    for line in txt.splitlines():
        m = re.match(r"^\s*(\d+)\s+([0-9.]+)\s+\d+\s+\d+", line)
        if m:
            last = (int(m.group(1)), float(m.group(2)))
    return last


def rel(a, b):
    return abs(a - b) / max(abs(b), 1e-300)


def grade(root, now=None):
    mesh_dir = os.path.join(root, "MESH")
    ledger = os.path.join(root, "ledger.txt")
    for p in (ledger, os.path.join(mesh_dir, "checkMesh.log")):
        if not os.path.isfile(p):
            raise Refusal("required artifact absent: %s" % p)
    row = parse_ledger_row(open(ledger).read())
    cm = parse_checkmesh(open(os.path.join(mesh_dir, "checkMesh.log")).read())
    gates, infra = {}, {}
    # ---- G14-1 completion (physics-critical: inspect rc, oom, Mesh OK, age guard) ----
    if row.get("rc") != "0":
        raise Refusal("G14-1: container rc=%s from docker inspect is not 0" % row.get("rc"))
    if row.get("oom", "false") != "false":
        raise Refusal("G14-1: OOMKilled=%s" % row.get("oom"))
    if not cm.get("mesh_ok_line"):
        raise Refusal("G14-1: checkMesh.log carries no 'Mesh OK.' line (failed checks: %d)" % cm.get("failed_checks", -1))
    datum = os.path.join(mesh_dir, "AGE_DATUM")
    if not os.path.isfile(datum):
        raise Refusal("G14-1: age datum absent: %s" % datum)
    if os.stat(os.path.join(mesh_dir, "checkMesh.log")).st_mtime <= os.stat(datum).st_mtime:
        raise Refusal("G14-1: checkMesh.log is not newer than the age datum (rule 4)")
    for k in ("cells", "points", "max_aspect_ratio", "max_non_orthogonality", "max_skewness"):
        if k not in cm:
            raise Refusal("G14-1: checkMesh.log carries no %s" % k)
    gates["G14-1_completion_age"] = "PASS"
    # ---- G14-2 identity with D4's mesh --------------------------------------------------
    gates["G14-2_identity"] = "PASS" if (cm["cells"] == REF["cells"] and cm["points"] == REF["points"]) else "GATE FAIL"
    # ---- G14-3 MESH_STANDARD ----------------------------------------------------------
    no, sk, ar = cm["max_non_orthogonality"], cm["max_skewness"], cm["max_aspect_ratio"]
    gates["G14-3_nonortho_hard70"] = "PASS" if no < NONORTHO_HARD else "GATE FAIL"
    gates["G14-3_skew_hard4"] = "PASS" if sk < SKEW_HARD else "GATE FAIL"
    aspect_flag = bool(ar > ASPECT_ADVISORY and (no > 60.0 or sk > 2.0))
    # ---- G14-4 the contaminant comparison, per number ---------------------------------
    d_ar = rel(ar, REF["max_aspect_ratio"]); d_no = rel(no, REF["max_non_orthogonality"]); d_sk = rel(sk, REF["max_skewness"])
    if d_ar <= REPRO_REL_TOL and d_no <= REPRO_REL_TOL and d_sk <= REPRO_REL_TOL:
        gates["G14-4_reproduction"] = "PASS"
    else:
        gates["G14-4_reproduction"] = "GATE FAIL"
    drift_named = bool((ar - REF["max_aspect_ratio"]) / REF["max_aspect_ratio"] > DRIFT_REL_WORSE)
    # ---- predictions ------------------------------------------------------------------
    preds = {"P1_cells_points_exact": "HIT" if gates["G14-2_identity"] == "PASS" else "MISS",
             "P2_max_aspect_repro": "HIT" if d_ar <= REPRO_REL_TOL else "MISS",
             "P3_max_nonortho_repro": "HIT" if d_no <= REPRO_REL_TOL else "MISS",
             "P4_max_skew_repro": "HIT" if d_sk <= REPRO_REL_TOL else "MISS"}
    pyhyp = None
    lg = os.path.join(mesh_dir, "logMeshGeneration.txt")
    if os.path.isfile(lg):
        pyhyp = parse_pyhyp_cpu(open(lg).read())
    if pyhyp is None:
        preds["P5_pyhyp_cpu_s"] = "NOT_MEASURED"
    else:
        lo, hi = PRED["P5_pyhyp_cpu_s"]; preds["P5_pyhyp_cpu_s"] = "HIT" if lo <= pyhyp[1] <= hi else "MISS"
    # ---- infrastructure (L-342: reported, never a verdict) -------------------------------
    try:
        wall = float(row.get("wall_s", "nan")); cmin = float(row.get("core_min", "nan"))
        if not (wall == wall and cmin == cmin and wall >= 0.0 and cmin >= 0.0):   # NaN or negative = not a measurement
            raise ValueError("wall_s/core_min not a finite non-negative number")
        infra["wall_s"] = wall; infra["core_min"] = cmin
        preds["P6_wall_le_120s"] = "HIT" if wall <= PRED["P6_wall_s_max"] else "MISS"
        infra["cost_ratio_actual_over_predicted"] = round(cmin / COST_PREDICTED_CORE_MIN, 4)
    except ValueError:
        infra["wall_s"] = "NOT_MEASURED"; infra["core_min"] = "NOT_MEASURED"; preds["P6_wall_le_120s"] = "NOT_MEASURED"
        infra["bookkeeping_defect"] = "wall_s/core_min unparseable in the ledger row -- voids the cost claim only (L-342)"
    infra["container"] = row.get("container", "NOT_MEASURED"); infra["memavail_GiB"] = row.get("memavail_GiB", "NOT_MEASURED")
    verdict = "PASS" if all(v == "PASS" for v in gates.values()) else "GATE FAIL"
    return {"item": "CURRICULUM-D14M", "verdict": verdict, "gates": gates, "predictions": preds,
            "measured": {k: cm[k] for k in cm}, "reference_D4_baseline": REF,
            "relative_departure": {"max_aspect_ratio": d_ar, "max_non_orthogonality": d_no, "max_skewness": d_sk},
            "nonortho_warning_band_65_70": bool(NONORTHO_WARN <= no < NONORTHO_HARD),
            "aspect_advisory_flag": aspect_flag,
            "generator_finding_class_drift": drift_named,
            "pyhyp_last_level_cpu_s": pyhyp, "infrastructure": infra,
            "field_classes": {"physics_critical": ["rc (docker inspect)", "oom", "checkMesh.log Mesh OK. + numbers", "AGE_DATUM age guard"],
                              "infrastructure": ["wall_s", "core_min", "memavail_GiB", "container", "driver pid"]},
            "no_gci": "no grid family; standing rule 5 has no row; NO GCI IS QUOTED"}


# ---- selftest: planted controls, counted against a FROZEN unit count ----------------------
BASE_LOG = """Mesh stats
    points:           40209
    faces:            116756
    internal faces:   113068
    cells:            38304
Checking geometry...
    Max aspect ratio = 684.4022128 OK.
    Mesh non-orthogonality Max: 66.96543422 average: 11.48508811
    Non-orthogonality check OK.
    Max skewness = 1.339283343 OK.

Mesh OK.
"""


def _mk(tmp, log=BASE_LOG, rc="0", oom="false", wall="40", datum_after=False):
    root = os.path.join(tmp, "root_%d" % int(time.time() * 1e6)); md = os.path.join(root, "MESH")
    os.makedirs(md)
    with open(os.path.join(md, "AGE_DATUM"), "w") as f:
        f.write("datum\n")
    t0 = os.stat(os.path.join(md, "AGE_DATUM")).st_mtime
    with open(os.path.join(md, "checkMesh.log"), "w") as f:
        f.write(log)
    os.utime(os.path.join(md, "checkMesh.log"), (t0 + 5, t0 + 5) if not datum_after else (t0 - 5, t0 - 5))
    with open(os.path.join(root, "ledger.txt"), "w") as f:
        f.write("ITEM=CURRICULUM-D14M\nARM=MESH rc=%s oom=%s wall_s=%s core_min=%.4f container=d14m_MESH_selftest memavail_GiB=20.0\n" % (rc, oom, wall, float(wall) / 60.0))
    return root


def selftest(tmp):
    n = 0; fails = []

    def unit(name, cond):
        nonlocal n
        n += 1
        if not cond:
            fails.append(name)
        print("  [%s] %s" % ("OK " if cond else "BAD", name))

    def refused(root):
        try:
            grade(root); return False
        except Refusal:
            return True
    r = grade(_mk(tmp))
    unit("U1 baseline log -> PASS, all four gates PASS", r["verdict"] == "PASS" and all(v == "PASS" for v in r["gates"].values()))
    unit("U2 baseline -> P1-P4 HIT, P6 HIT", all(r["predictions"][k] == "HIT" for k in ("P1_cells_points_exact", "P2_max_aspect_repro", "P3_max_nonortho_repro", "P4_max_skew_repro", "P6_wall_le_120s")))
    r = grade(_mk(tmp, BASE_LOG.replace("684.4022128", "1500.0")))
    unit("U3 PLANTED max aspect ratio 1500 -> G14-4 GATE FAIL, drift named, P2 MISS", r["gates"]["G14-4_reproduction"] == "GATE FAIL" and r["generator_finding_class_drift"] and r["predictions"]["P2_max_aspect_repro"] == "MISS" and r["verdict"] == "GATE FAIL")
    r = grade(_mk(tmp, BASE_LOG.replace("66.96543422", "71.0")))
    unit("U4 PLANTED non-ortho 71 -> G14-3 hard gate GATE FAIL", r["gates"]["G14-3_nonortho_hard70"] == "GATE FAIL")
    r = grade(_mk(tmp, BASE_LOG.replace("1.339283343", "4.5")))
    unit("U5 PLANTED skew 4.5 -> G14-3 skew GATE FAIL", r["gates"]["G14-3_skew_hard4"] == "GATE FAIL")
    r = grade(_mk(tmp, BASE_LOG.replace("38304", "38305")))
    unit("U6 PLANTED cells 38305 -> G14-2 GATE FAIL, P1 MISS", r["gates"]["G14-2_identity"] == "GATE FAIL" and r["predictions"]["P1_cells_points_exact"] == "MISS")
    r = grade(_mk(tmp, BASE_LOG.replace("684.4022128", "684.4029")))
    unit("U7 PLANTED 1e-6-relative departure on aspect ratio -> G14-4 GATE FAIL without drift naming", r["gates"]["G14-4_reproduction"] == "GATE FAIL" and not r["generator_finding_class_drift"])
    unit("U8 rc=1 row -> REFUSAL", refused(_mk(tmp, rc="1")))
    unit("U9 OOMKilled=true -> REFUSAL", refused(_mk(tmp, oom="true")))
    unit("U10 no 'Mesh OK.' line -> REFUSAL", refused(_mk(tmp, BASE_LOG.replace("Mesh OK.", "Failed 1 mesh checks."))))
    unit("U11 checkMesh.log OLDER than the age datum -> REFUSAL (rule 4)", refused(_mk(tmp, datum_after=True)))
    r = grade(_mk(tmp, wall="nan"))
    unit("U12 unparseable wall -> verdict unchanged PASS, bookkeeping defect reported (L-342)", r["verdict"] == "PASS" and "bookkeeping_defect" in r["infrastructure"])
    unit("U13 ast.Assert count in this file = 0", count_asserts(os.path.abspath(__file__)) == 0)
    p = os.path.join(tmp, "planted_assert.py")
    with open(p, "w") as f:
        f.write("x = 1\nassert x == 1\n")
    unit("U14 the assert counter sees a planted assert (=1)", count_asserts(p) == 1)
    print("D14M GRADER SELFTEST units=%d expected=%d failures=%d python_O=%s" % (n, EXPECTED_UNITS, len(fails), not __debug__))
    if n != EXPECTED_UNITS or fails:
        print("SELFTEST FAIL: %s" % (fails or "unit count %d != %d" % (n, EXPECTED_UNITS)))
        return 2
    print("D14M GRADER SELFTEST PASS %d/%d (counted against the frozen EXPECTED_UNITS)" % (n, EXPECTED_UNITS))
    return 0


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--tmpdir", default="/tmp")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if count_asserts(os.path.abspath(__file__)) != 0:
        print("REFUSAL: this comparator carries an assert statement (L-332)"); return 2
    if a.selftest:
        d = os.path.join(a.tmpdir, "d14m_selftest_%d" % os.getpid()); os.makedirs(d, exist_ok=True)
        return selftest(d)
    if not a.root:
        print("usage: d14m_grade.py --root <run root> [--out FILE] | --selftest"); return 64
    try:
        r = grade(a.root)
    except Refusal as e:
        print("REFUSAL: %s -> NOT A RESULT" % e)
        if a.out:
            with open(a.out, "w") as f:
                json.dump({"item": "CURRICULUM-D14M", "verdict": "NOT A RESULT", "refusal": str(e)}, f, indent=1)
        return 2
    print(json.dumps(r, indent=1))
    if a.out:
        with open(a.out, "w") as f:
            json.dump(r, f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
