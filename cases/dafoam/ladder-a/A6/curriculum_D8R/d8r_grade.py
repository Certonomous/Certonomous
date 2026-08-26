#!/usr/bin/env python3
"""Curriculum D8R COMPARATOR -- A6 CRM wing-alone N=16, twist-only constrained drag
minimisation TO CONVERGENCE on TWO ROWS (PATCHED first, then SHIPPED), each followed by an
ENDPOINT central-FD table beside the endpoint adjoint.  FROZEN by md5 in PREREGISTRATION.md
section 7 before any container starts.  Computes nothing about physics; renders verdicts
from the FIXED vocabulary only (PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED /
PENDING).  Derived from curriculum_D16/d16_grade.py (d8r_grade_DELTAS_from_d16.diff): the
ledger regex, L-342 field classes, arm-kind-aware completion, the inspect-record fallback,
the FD machinery (plateau, band D with the sign-flip rule, band E, >= 3 graded), the
planted controls, G9/G10/G12 and the selftest shape are D16's; NEW here are the
optimisation gates G-O / G2 / G3 / G-BASE and the four-arm, no-MESH chain.

WHAT IT GRADES (PREREGISTRATION.md section 3):
  G1    completion, every arm SOLVER: kernel rc == 0 (docker inspect, harness rc must agree),
        OOMKilled false (G11, hard), the AGE GUARD on the registered artefact, the instrument's
        TERMINAL MARKER (D8R_O_WRITTEN / D8R_F_WRITTEN) in the arm log.  Any clause fails ->
        REFUSE (NOT A RESULT).  A missing ledger row is read from the surviving
        `<ARM>_<stamp>.inspect.txt` with the source named and every infrastructure field
        NOT_MEASURED (L-342).
  G-M2  mesh identity: md5(<arm>/constant/polyMesh/points.gz) == D8's frozen
        11b84f0de5fdf2d3e947fee8cea412a9 on every arm -> PASS else GATE FAIL.
  G-BASE per O arm: the cold CD lies within 10 eta of D8's five-times-reproduced
        0.03506349413916734 (np=1 gave 17-digit equality; np=4 decomposition is registered to
        move it by no more than the case's own noise floor) -> PASS else GATE FAIL.
  G-O   per O arm, the optimiser's OWN terminus (DAFOAM_CHARTER.md section 9):
        `EXIT: Optimal Solution Found.` -> PASS; `EXIT: Maximum Number of Iterations
        Exceeded.` with the registered intermediate threshold met (CD_start - CD_final >=
        10 eta, D8's G3) -> GATE REACHED; any other EXIT, or none -> NOT A RESULT.  A
        `Number of Iterations` above the registered MAX_ITER is an instrument defect ->
        REFUSE.
  G2    per O arm: |CL_final - 0.5| <= 5.0e-3 (D8 section 4) -> PASS else GATE FAIL.
  G3    per O arm: the drag reduction (CD_start - CD_final) / CD_start lies inside the
        REGISTERED band [0.29 %, 5.0 %] (P5; the lower edge is D8's measured 3-major drop,
        the upper the induced-drag bound of a twist-only reload) -> PASS else GATE FAIL --
        outside the band is a GATE FAIL, never a silent widening.
  G5    per row, the bright line at the ENDPOINT: per registered component the FD
        reference is the MIDDLE step of the registered three; PLATEAU = the middle step agrees
        with at least one neighbour to 10 % (else NOT A RESULT); band D = per-component
        |d_FD - J_adj| / |d_FD| <= 5.0 % AND the same sign (a SIGN FLIP is GATE FAIL whatever
        the magnitude); band E = aggregate vector-relative error <= 5.0 %.  Fewer than 3
        graded components -> the row is NOT A RESULT.  G5 on CD (the objective), G5c on CL
        (the constraint) with the same bands.  The F arm must have consumed the SAME ROW's
        endpoint (endpoint_source md5 == md5 of that row's d8r_O.json) or it REFUSES.
  G6    dot-product / duality test: NOT MEASURED -- the tutorial exposes none; named.
  G9    toolchain per row: ledger DIGEST, the container's `D4S_IDWARP_SO_MD5:` print and the
        artefact's in-process libidwarp.so md5 must all name the row's registered toolchain.
  G10   caps: every arm core_min <= its registered cap and the sum <= the ceiling; a crossing
        is GATE FAIL exactly as the frozen text says (report mode).
  G12   placement: cpuset == the registered 0,1,12,15 on every arm; delivered cores >= 3.0
        of 4 where MEASURED, NOT_MEASURED disclosed otherwise.
  ROW   = NOT A RESULT if any of G-O/G2/G3/G5/G5c is; else GATE FAIL if any is; else
        GATE REACHED if G-O is; else PASS.  ITEM = NOT A RESULT if any row is; else GATE FAIL
        if any row or G-M2/G-BASE/G9/G10/G12 is; else GATE REACHED if any row is; else PASS.
  DIVERGENCE shipped-vs-patched per component on the endpoint adjoint is REPORTED with its
        number (the two rows sit at DIFFERENT endpoints, so it is a reading, not a gate).

PLANTED CONTROLS (rule 3): (i) the instrument's CTRL component and its PLANTED row are
re-read here and the grade REFUSES if the reader cannot see them; (ii) this grader writes a
copy of each F table with PLANT added to every physical derivative into
<root>/grader_controls/, re-reads it through the same reader, and REFUSES unless every
value moved by exactly PLANT.

L-342 (Sanaa, d4d0c29d): FIELDS_PHYSICS absent -> REFUSE; FIELDS_INFRASTRUCTURE absent
-> NOT_MEASURED, disclosed beside the verdict, never composed to PASS; present-but-garbage
-> REFUSE.  L-332: NO `assert` anywhere; the module counts ast.Assert nodes in its own
source and refuses on any.  No unconditional success print.
"""
import ast
import glob
import hashlib
import json
import math
import os
import re
import sys
import time

# ---- REGISTERED CONSTANTS (PREREGISTRATION.md; the document governs) ----------------
ITEM = "D8R"
BASE = "/home/ubuntu/certonomous-runs/CURRICULUM-D8R-a6-twist-opt-conv"
ARMS_REQUIRED = ["O-P", "F-P", "O-S", "F-S"]
ARM_KIND = {"O-P": "SOLVER", "F-P": "SOLVER", "O-S": "SOLVER", "F-S": "SOLVER"}
ARM_ROW = {"O-P": "PATCHED", "F-P": "PATCHED", "O-S": "SHIPPED", "F-S": "SHIPPED"}
ARM_RANKS = {"O-P": 4, "F-P": 4, "O-S": 4, "F-S": 4}
ARTEFACT = {"O-P": "d8r_O.json", "F-P": "d8r_F.json", "O-S": "d8r_O.json", "F-S": "d8r_F.json"}
TERMINAL = {"O-P": "D8R_O_WRITTEN", "F-P": "D8R_F_WRITTEN", "O-S": "D8R_O_WRITTEN", "F-S": "D8R_F_WRITTEN"}
DATUM_REF = {"O-P": "0/U", "F-P": "0/U", "O-S": "0/U", "F-S": "0/U"}
CAPS = {"O-P": 1000.0, "F-P": 120.0, "O-S": 1000.0, "F-S": 120.0}
ITEM_CEILING_CORE_MIN = 2240.0
PREDICTED_CORE_MIN = {"O-P": 458.0, "F-P": 61.0, "O-S": 458.0, "F-S": 61.0}
POINTS_MD5 = "11b84f0de5fdf2d3e947fee8cea412a9"   # D8 PREREGISTRATION.md section 9, the fixed-reference tree's points.gz
NPROCS_REGISTERED = 4
MAX_ITER = 30
CL_TARGET = 0.5
G2_CL_TOL = 5.0e-3           # D8 PREREGISTRATION.md section 4, G2
ETA_D8 = 1.0910e-05          # N-D13; D8 section 2; endpoint reproduced at ratio 0.989 (D8 RESULTS section 4)
G3_MIN_DROP_ABS = 10.0 * ETA_D8   # D8's G3 threshold: the intermediate threshold for GATE REACHED
CD_COLD_REGISTERED = 0.03506349413916734
GBASE_TOL_ABS = 10.0 * ETA_D8
DROP_BAND_PCT = (0.29, 5.0)  # P5 / G3: registered band on (CD_start - CD_final) / CD_start
FD_BAND_PCT = 5.0            # band D, per component (D4 PREREGISTRATION.md:82; D7FR:228-229)
AGG_BAND_PCT = 5.0           # band E, aggregate vector-relative (same sources)
PLATEAU_TOL_PCT = 10.0
MIN_GRADED = 3
NEAR_ZERO_ABS = 1.0e-14
COMPONENTS_REGISTERED = [["twist", 0], ["twist", 1], ["twist", 3], ["twist", 4], ["twist", 5]]
STEPS_REGISTERED = {"twist": [3.0e-2, 1.0e-1, 3.0e-1]}
DVS = ("twist", "patchV")
CTRL_STEP = 1.0e-1
PLANT = 1.234e-03
IMG_DIGEST = {"SHIPPED": "sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc",
              "PATCHED": "sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35"}
SO_MD5 = {"SHIPPED": "f0fcb488e0e98156575cd19548e91663", "PATCHED": "85f59e87253e0a71a813f64ca6e4c425"}
CPUSET_REGISTERED = "0,1,12,15"
DELIVERED_CORES_FLOOR = 3.0
EXIT_OPTIMAL = "EXIT: Optimal Solution Found."
EXIT_MAXITER = "EXIT: Maximum Number of Iterations Exceeded."
PRED = {"P6_core_min_band": (500.0, 1800.0), "P7_majors_band": (8, 30)}
FIELDS_PHYSICS = ("rc", "inspect_exit", "oomkilled", "terminal_statement", "age_guard",
                  "core_min", "cap_core_min", "DIGEST", "cpuset")
FIELDS_INFRASTRUCTURE = ("memavail_pre_GiB", "memavail_post_GiB", "delivered", "siblings_pre",
                         "siblings_post", "log", "wall_s")
NOT_MEASURED = "NOT_MEASURED"
VOCAB = {"PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"}
EXPECTED_UNITS = 31


class Refusal(Exception):
    pass


def refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail}, sort_keys=True, default=str))


def count_asserts(path):
    return sum(1 for n in ast.walk(ast.parse(open(path).read())) if isinstance(n, ast.Assert))


def md5_of(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


# ================= LEDGER (physics vs infrastructure, L-342) -- D5's regex ============
LEDGER_RE = re.compile(
    r"ARM=(?P<ARM>\S+)\s+ROW=(?P<ROW>\S+)\s+IMG=(?P<IMG>\S+)\s+"
    r"DIGEST=(?P<DIGEST>\S+)\s+rc=(?P<rc>-?\d+)\s+wall_s=(?P<wall_s>\d+)\s+"
    r"ranks=(?P<ranks>\d+)\s+core_min=(?P<core_min>[\d.]+)\s+"
    r"cap_core_min=(?P<cap>[\d.]+)\s+enforced_wall_s=(?P<ewall>\d+)\s+"
    r"enforced_core_min=(?P<ecore>[\d.]+)\s+memory=(?P<mem>\S+)\s+"
    r"inspect\(exit,oomkilled\)=\[(?P<inspect>[^\]]*)\]"
    r"(?:\s+memavail_pre_GiB=(?P<mempre>[\d.]+|NOT_MEASURED))?"
    r"(?:\s+memavail_post_GiB=(?P<mempost>[\d.]+|NOT_MEASURED))?"
    r"\s+cpuset=(?P<cpuset>\S+)"
    r"(?:\s+delivered_cores_mean=\[(?P<delivered>[^\]]*)\])?"
    r"(?:\s+siblings_pre=\[(?P<sibpre>[^\]]*)\])?"
    r"(?:\s+siblings_post=\[(?P<sibpost>[^\]]*)\])?"
    r"(?:\s+log=(?P<log>\S+))?")


def _infra_float(v):
    if v is None or v == NOT_MEASURED:
        return None
    return float(v)


def read_ledger(path):
    if not os.path.isfile(path):
        refuse("ledger", {"absent": path})
    rows = {}
    for line in open(path, errors="replace"):
        if not line.startswith("ARM="):
            continue
        m = LEDGER_RE.search(line)
        if not m:
            refuse("ledger", {"row_unparseable": line.strip()[:300],
                              "note": "PRESENT-BUT-GARBAGE row: refused, never skipped"})
        g = m.groupdict()
        parts = g["inspect"].split()
        infra_nm = [k for k, v in (("memavail_pre_GiB", g["mempre"]), ("memavail_post_GiB", g["mempost"]),
                                   ("delivered", g["delivered"]), ("siblings_pre", g["sibpre"]),
                                   ("siblings_post", g["sibpost"]), ("log", g["log"]))
                    if v is None or NOT_MEASURED in str(v)]
        row = {"ARM": g["ARM"], "ROW": g["ROW"], "IMG": g["IMG"], "DIGEST": g["DIGEST"],
               "rc": int(g["rc"]), "wall_s": int(g["wall_s"]), "ranks": int(g["ranks"]),
               "core_min": float(g["core_min"]), "cap_core_min": float(g["cap"]),
               "enforced_core_min": float(g["ecore"]), "memory": g["mem"],
               "inspect_exit": (parts[0] if parts else None),
               "oomkilled": (parts[1] if len(parts) > 1 else None),
               "memavail_pre_GiB": _infra_float(g["mempre"]), "memavail_post_GiB": _infra_float(g["mempost"]),
               "cpuset": g["cpuset"], "delivered": g["delivered"], "siblings_pre": g["sibpre"],
               "siblings_post": g["sibpost"], "log": g["log"], "source": "ledger_row",
               "field_sources": {"all": "ledger_row"}, "infra_not_measured": infra_nm}
        if row["ARM"] in rows:
            refuse("ledger", {"duplicate_arm_row": row["ARM"], "note": "two records for one run is the defect"})
        rows[row["ARM"]] = row
    return rows


def inspect_file_fallback(base, arm):
    """L-342: an arm with no ledger row is read from the launcher's surviving inspect
    record `<ARM>_<stamp>.inspect.txt` (exit oom started finished cpuset memory); every
    infrastructure field NOT_MEASURED, the source named per field."""
    cands = sorted(glob.glob(os.path.join(base, "%s_*.inspect.txt" % arm)))
    if len(cands) != 1:
        refuse("G1", {"arm_absent_from_ledger": arm, "inspect_record_candidates": cands,
                      "note": "exactly one surviving inspect record may stand in for a missing row"})
    parts = open(cands[0]).read().split()
    if len(parts) < 5:
        refuse("G1", {"inspect_record_unparseable": cands[0], "content": parts})
    logs = sorted(glob.glob(os.path.join(base, "%s_*.log" % arm)))
    try:
        rc = int(parts[0])
    except ValueError:
        refuse("G1", {"inspect_record_exit_unparseable": parts[0]})
    return {"ARM": arm, "ROW": ARM_ROW[arm], "IMG": None, "DIGEST": (parts[6] if len(parts) > 6 else None), "rc": rc, "wall_s": None,
            "ranks": ARM_RANKS[arm], "core_min": None, "cap_core_min": CAPS[arm],
            "enforced_core_min": CAPS[arm], "memory": parts[5] if len(parts) > 5 else None,
            "inspect_exit": parts[0], "oomkilled": parts[1].lower(), "memavail_pre_GiB": None,
            "memavail_post_GiB": None, "cpuset": parts[4], "delivered": NOT_MEASURED,
            "siblings_pre": NOT_MEASURED, "siblings_post": NOT_MEASURED,
            "log": (os.path.basename(logs[-1]) if logs else None), "source": "inspect_record",
            "field_sources": {"rc": "inspect.txt .State.ExitCode", "oomkilled": "inspect.txt .State.OOMKilled",
                              "cpuset": "inspect.txt HostConfig.CpusetCpus", "DIGEST": "inspect.txt 7th field (launcher's GOT_DIGEST)"},
            "infra_not_measured": list(FIELDS_INFRASTRUCTURE) + ["core_min"]}


# ================= G1: COMPLETION =====================================================
def arm_datum(base, arm):
    d = os.path.join(base, arm)
    p = os.path.join(d, ".d8r_age_datum")
    if not os.path.isfile(p):
        refuse("G1", {"age_datum_absent": p, "arm": arm})
    datum = int(open(p).read().strip())
    ref = os.path.join(d, DATUM_REF[arm])
    if not os.path.isfile(ref):
        refuse("G1", {"age_reference_absent": ref})
    if int(os.path.getmtime(ref)) != datum:
        refuse("G1", {"age_reference_moved": ref, "recorded": datum, "on_disk": int(os.path.getmtime(ref))})
    return d, datum


def g_completion(base, rows):
    out = {"arms": {}, "not_measured": {}}
    for arm in ARMS_REQUIRED:
        r = rows.get(arm)
        if r is None:
            r = inspect_file_fallback(base, arm)
            rows[arm] = r
        ke = r.get("inspect_exit")
        if ke is None:
            refuse("G1", {"kernel_exit_absent": arm, "note": "inspect(exit,oomkilled) is a PHYSICS field"})
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
                          "note": "a run that fails any clause is not done (rule 4); OOMKilled is G11, hard"})
        adir, datum = arm_datum(base, arm)
        art = os.path.join(adir, ARTEFACT[arm])
        if not os.path.isfile(art):
            refuse("G1", {"artefact_absent": art, "arm": arm})
        if os.path.getmtime(art) <= datum:
            refuse("G1", {"artefact_not_newer_than_datum": art, "arm": arm, "datum": datum,
                          "artefact_mtime": os.path.getmtime(art), "note": "age guard, rule 4"})
        logname = r.get("log")
        logpath = os.path.join(base, logname) if logname else None
        if not logpath or not os.path.isfile(logpath):
            refuse("G1", {"log_absent": logname, "arm": arm, "note": "a missing log is a FAILED clause"})
        text = open(logpath, errors="replace").read()
        if TERMINAL[arm] not in text:
            refuse("G1", {"terminal_marker_absent": TERMINAL[arm], "arm": arm, "log": logname})
        r["log_text"] = text
        out["arms"][arm] = {"kind": ARM_KIND[arm], "kernel_rc": kernel_rc, "oomkilled": oom, "artefact": ARTEFACT[arm],
                            "source": r["source"], "field_sources": r["field_sources"]}
        if r.get("infra_not_measured"):
            out["not_measured"][arm] = r["infra_not_measured"]
    return out


# ================= readers with planted controls ======================================
def read_O(path):
    j = json.load(open(path))
    adj = {}
    for of in ("CD", "CL"):
        adj[of] = {dv: [float(v) for v in j["adjoint"][of][dv]] for dv in DVS}
    ip = j.get("ipopt") or {}
    return {"CD_cold": float(j["CD_cold"]), "CL_cold": float(j["CL_cold"]),
            "CD_start": float(j["CD_start"]), "CL_start": float(j["CL_start"]),
            "CD_final": float(j["CD_final"]), "CL_final": float(j["CL_final"]),
            "CD_endpoint": float(j["CD_endpoint"]), "adjoint": adj,
            "exit_line": ip.get("exit_line"), "n_iter": ip.get("n_iter"),
            "max_iter_registered": j.get("max_iter_registered"),
            "so_md5": (j.get("identity") or {}).get("libidwarp_so_md5"), "nprocs": j.get("nprocs"),
            "md5": md5_of(path)}


def read_F(path):
    j = json.load(open(path))
    if j.get("components_requested") != COMPONENTS_REGISTERED:
        refuse("G5", {"components_requested_not_registered": j.get("components_requested"),
                      "registered": COMPONENTS_REGISTERED})
    table, ctrl = {}, None
    for row in j["rows"]:
        if row.get("dv") == "CTRL":
            ctrl = row
            continue
        key = (row["dv"], int(row["idx"]))
        fd = {}
        for k, v in (row.get("fd") or {}).items():
            fd[float(v["step"])] = {"ok": bool(v.get("ok")),
                                    "dCD": (float(v["dCD"]) if v.get("ok") else None),
                                    "dCL": (float(v["dCL"]) if v.get("ok") else None)}
        table[key] = {"status": row.get("status"), "fd": fd}
    return {"table": table, "ctrl": ctrl, "CD": float(j["CD_baseline"]), "eta": float(j["eta_used"]),
            "endpoint_md5": (j.get("endpoint_source") or {}).get("md5"),
            "so_md5": (j.get("identity") or {}).get("libidwarp_so_md5"), "nprocs": j.get("nprocs"), "raw": j}


def ctrl_control(F):
    c = F["ctrl"]
    if c is None:
        refuse("CONTROL", {"ctrl_row_absent": True})
    zero = float(c["fd"][repr(CTRL_STEP)]["dCD"])
    plant = float(c["planted"]["dCD"])
    want = PLANT / (2.0 * CTRL_STEP)
    if zero != 0.0 or abs(plant - want) > 1e-12 * abs(want):
        refuse("CONTROL", {"instrument_ctrl_not_seen": {"zero": zero, "planted": plant, "want": want}})
    return {"instrument_ctrl_zero": zero, "instrument_ctrl_planted": plant, "want": want}


def grader_plant_control(base, fpath, tag):
    """Write a copy with PLANT added to every physical dCD, re-read it through read_F,
    refuse unless every value moved by exactly PLANT."""
    j = json.load(open(fpath))
    for row in j["rows"]:
        if row.get("dv") == "CTRL":
            continue
        for v in (row.get("fd") or {}).values():
            if v.get("ok"):
                v["dCD"] = repr(float(v["dCD"]) + PLANT)
    cdir = os.path.join(base, "grader_controls")
    os.makedirs(cdir, exist_ok=True)
    cp = os.path.join(cdir, "F_%s_planted.json" % tag)
    json.dump(j, open(cp, "w"), indent=1, sort_keys=True)
    orig, back = read_F(fpath)["table"], read_F(cp)["table"]
    worst = 0.0
    n = 0
    for key, row in orig.items():
        for s, v in row["fd"].items():
            if v["ok"]:
                worst = max(worst, abs((back[key]["fd"][s]["dCD"] - v["dCD"]) - PLANT))
                n += 1
    if n == 0 or worst > 1e-12:
        refuse("CONTROL", {"grader_plant_not_seen": {"n_values": n, "worst_residual": worst, "plant": PLANT}})
    return {"grader_plant_seen": True, "n_values": n, "worst_residual": worst, "file": cp}


# ================= G5: the bright line, per row, per objective =======================
def grade_components(X, F, of):
    key_d = "dCD" if of == "CD" else "dCL"
    comps, graded_fd, graded_adj = [], [], []
    for dv, idx in COMPONENTS_REGISTERED:
        j = X["adjoint"][of][dv][idx] if idx < len(X["adjoint"][of][dv]) else None
        row = F["table"].get((dv, idx))
        c = {"dv": dv, "idx": idx, "J_adj": j}
        if row is None or j is None:
            c.update({"verdict": "NOT A RESULT", "reason": "ABSENT"})
            comps.append(c)
            continue
        steps = sorted(STEPS_REGISTERED[dv], reverse=True)
        vals = [row["fd"].get(s) for s in steps]
        if any(v is None or not v["ok"] for v in vals):
            c.update({"verdict": "NOT A RESULT", "reason": "FD_STEP_FAILED_OR_ABSENT",
                      "steps_present": sorted(row["fd"])})
            comps.append(c)
            continue
        d = [v[key_d] for v in vals]
        ref = d[1]
        c.update({"steps": steps, "d_fd": d, "d_ref": ref})
        if abs(ref) < NEAR_ZERO_ABS:
            c.update({"verdict": "NOT A RESULT", "reason": "NEAR_ZERO"})
            comps.append(c)
            continue
        nb = [abs(d[0] - ref) / abs(ref) * 100.0, abs(d[2] - ref) / abs(ref) * 100.0]
        c["plateau_neighbour_pct"] = nb
        if min(nb) > PLATEAU_TOL_PCT:
            c.update({"verdict": "NOT A RESULT", "reason": "NO_PLATEAU"})
            comps.append(c)
            continue
        rel = abs(ref - j) / abs(ref) * 100.0
        flip = bool(ref * j < 0.0)
        c.update({"rel_err_pct": rel, "sign_flip": flip})
        c["verdict"] = "GATE FAIL" if (flip or rel > FD_BAND_PCT) else "PASS"
        graded_fd.append(ref)
        graded_adj.append(j)
        comps.append(c)
    n_graded = len(graded_fd)
    out = {"objective": of, "components": comps, "n_graded": n_graded,
           "n_pass": sum(1 for c in comps if c.get("verdict") == "PASS"),
           "n_gate_fail": sum(1 for c in comps if c.get("verdict") == "GATE FAIL"),
           "n_not_a_result": sum(1 for c in comps if c.get("verdict") == "NOT A RESULT"),
           "sign_flips": sum(1 for c in comps if c.get("sign_flip"))}
    if n_graded < MIN_GRADED:
        out.update({"verdict": "NOT A RESULT", "aggregate_rel_err_pct": None,
                    "reason": "fewer than %d graded components" % MIN_GRADED})
        return out
    num = math.sqrt(sum((a - b) ** 2 for a, b in zip(graded_fd, graded_adj)))
    den = math.sqrt(sum(a ** 2 for a in graded_fd))
    agg = num / den * 100.0
    out["aggregate_rel_err_pct"] = agg
    band_d_ok = out["n_gate_fail"] == 0
    band_e_ok = agg <= AGG_BAND_PCT
    out["band_D"] = "PASS" if band_d_ok else "GATE FAIL"
    out["band_E"] = "PASS" if band_e_ok else "GATE FAIL"
    out["verdict"] = "PASS" if (band_d_ok and band_e_ok) else "GATE FAIL"
    return out


# ================= the optimisation gates, per O arm ==================================
def g_optimiser(O):
    """G-O: the optimiser's OWN terminus (DAFOAM_CHARTER.md section 9)."""
    ex, n = O["exit_line"], O["n_iter"]
    if n is not None and n > MAX_ITER:
        refuse("G-O", {"n_iter_above_registered_max_iter": n, "max_iter": MAX_ITER,
                       "note": "the optimiser ran past the registered budget: an instrument defect, refused"})
    drop = O["CD_start"] - O["CD_final"]
    out = {"exit_line": ex, "n_iter": n, "max_iter": MAX_ITER, "CD_start": O["CD_start"], "CD_final": O["CD_final"],
           "drop_abs": drop, "intermediate_threshold_abs": G3_MIN_DROP_ABS}
    if ex == EXIT_OPTIMAL:
        out["verdict"] = "PASS"
    elif ex == EXIT_MAXITER:
        out["verdict"] = "GATE REACHED" if drop >= G3_MIN_DROP_ABS else "NOT A RESULT"
        out["reason"] = "registered budget reached; intermediate threshold %s" % ("met" if drop >= G3_MIN_DROP_ABS else "NOT met")
    else:
        out["verdict"] = "NOT A RESULT"
        out["reason"] = "no convergence statement, or an EXIT this registration did not map"
    return out


def g_cl(O):
    dev = abs(O["CL_final"] - CL_TARGET)
    return {"CL_final": O["CL_final"], "abs_dev": dev, "tol": G2_CL_TOL, "verdict": "PASS" if dev <= G2_CL_TOL else "GATE FAIL"}


def g_drop(O):
    rel = (O["CD_start"] - O["CD_final"]) / O["CD_start"] * 100.0
    ok = DROP_BAND_PCT[0] <= rel <= DROP_BAND_PCT[1]
    return {"CD_start": O["CD_start"], "CD_final": O["CD_final"], "reduction_pct": rel, "band_pct": DROP_BAND_PCT,
            "verdict": "PASS" if ok else "GATE FAIL"}


def g_base(O):
    dev = abs(O["CD_cold"] - CD_COLD_REGISTERED)
    return {"CD_cold": O["CD_cold"], "registered": CD_COLD_REGISTERED, "abs_dev": dev, "tol": GBASE_TOL_ABS,
            "verdict": "PASS" if dev <= GBASE_TOL_ABS else "GATE FAIL"}


def compose_row(g_o, g2, g3, g5cd, g5cl):
    vs = [g_o["verdict"], g2["verdict"], g3["verdict"], g5cd["verdict"], g5cl["verdict"]]
    if "NOT A RESULT" in vs:
        return "NOT A RESULT"
    if "GATE FAIL" in vs:
        return "GATE FAIL"
    if g_o["verdict"] == "GATE REACHED":
        return "GATE REACHED"
    return "PASS"


# ================= G9 / G10 / G12 ======================================================
def g_toolchain(rows):
    out = {"per_arm": {}, "verdict": "PASS"}
    for arm in ARMS_REQUIRED:
        r = rows[arm]
        row = ARM_ROW[arm]
        m = re.search(r"D4S_IDWARP_SO_MD5:\s*([0-9a-f]{32})", r.get("log_text", ""))
        printed = m.group(1) if m else None
        art_md5 = r.get("artefact_so_md5")
        ok = (r.get("DIGEST") == IMG_DIGEST[row]) and (printed == SO_MD5[row]) and (art_md5 == SO_MD5[row])
        out["per_arm"][arm] = {"row": row, "digest": r.get("DIGEST"), "printed_so_md5": printed,
                               "artefact_so_md5": art_md5, "ok": bool(ok)}
        if not ok:
            out["verdict"] = "GATE FAIL"
    return out


def g_caps(rows):
    out = {"per_arm": {}, "verdict": "PASS", "total_core_min": 0.0, "ceiling": ITEM_CEILING_CORE_MIN, "not_measured": []}
    for arm in ARMS_REQUIRED:
        r = rows[arm]
        cm = r.get("core_min")
        if cm is None:
            out["not_measured"].append(arm)
            out["per_arm"][arm] = {"core_min": NOT_MEASURED, "cap": CAPS[arm]}
            continue
        out["total_core_min"] += cm
        crossed = cm > CAPS[arm]
        out["per_arm"][arm] = {"core_min": cm, "cap": CAPS[arm], "crossed": crossed,
                               "ratio_actual_over_predicted": round(cm / PREDICTED_CORE_MIN[arm], 4)}
        if crossed:
            out["verdict"] = "GATE FAIL"
    if out["total_core_min"] > ITEM_CEILING_CORE_MIN:
        out["verdict"] = "GATE FAIL"
    return out


def g_placement(rows):
    out = {"per_arm": {}, "verdict": "PASS", "not_measured": []}
    for arm in ARMS_REQUIRED:
        r = rows[arm]
        cs_ok = r.get("cpuset") == CPUSET_REGISTERED
        d = r.get("delivered")
        dl = None
        m = re.match(r"\s*([\d.]+)\s+n=(\d+)", d or "")
        if m:
            dl = float(m.group(1))
        if dl is None:
            out["not_measured"].append(arm)
        dl_ok = True if dl is None else dl >= DELIVERED_CORES_FLOOR
        out["per_arm"][arm] = {"cpuset": r.get("cpuset"), "delivered_cores_mean": (dl if dl is not None else NOT_MEASURED)}
        if not (cs_ok and dl_ok):
            out["verdict"] = "GATE FAIL"
    return out


# ================= the grade ==========================================================
def grade(root):
    rows = read_ledger(os.path.join(root, "ledger.txt"))
    g1 = g_completion(root, rows)
    # ---- mesh identity by hash, every arm
    gm2, mesh = "PASS", {}
    for arm in ARMS_REQUIRED:
        p = os.path.join(root, arm, "constant", "polyMesh", "points.gz")
        if not os.path.isfile(p):
            refuse("G-M2", {"points_absent": p})
        h = md5_of(p)
        mesh[arm] = h
        if h != POINTS_MD5:
            gm2 = "GATE FAIL"
    # ---- rows
    O = {"S": read_O(os.path.join(root, "O-S", "d8r_O.json")), "P": read_O(os.path.join(root, "O-P", "d8r_O.json"))}
    F = {"S": read_F(os.path.join(root, "F-S", "d8r_F.json")), "P": read_F(os.path.join(root, "F-P", "d8r_F.json"))}
    for rk, oa, fa in (("S", "O-S", "F-S"), ("P", "O-P", "F-P")):
        rows[oa]["artefact_so_md5"] = O[rk]["so_md5"]
        rows[fa]["artefact_so_md5"] = F[rk]["so_md5"]
        if F[rk]["endpoint_md5"] != O[rk]["md5"]:
            refuse("G5", {"F_arm_endpoint_is_not_this_rows_O_artefact": fa, "endpoint_md5": F[rk]["endpoint_md5"], "O_md5": O[rk]["md5"]})
        for a, art in ((oa, O[rk]), (fa, F[rk])):
            if art.get("nprocs") != NPROCS_REGISTERED:
                refuse("G12", {"nprocs_not_registered": a, "nprocs": art.get("nprocs"), "registered": NPROCS_REGISTERED})
    controls = {"S": ctrl_control(F["S"]), "P": ctrl_control(F["P"]),
                "grader_plant_S": grader_plant_control(root, os.path.join(root, "F-S", "d8r_F.json"), "S"),
                "grader_plant_P": grader_plant_control(root, os.path.join(root, "F-P", "d8r_F.json"), "P")}
    g = {}
    for rk in ("S", "P"):
        go, g2, g3, gb = g_optimiser(O[rk]), g_cl(O[rk]), g_drop(O[rk]), g_base(O[rk])
        cd = grade_components(O[rk], F[rk], "CD")
        cl = grade_components(O[rk], F[rk], "CL")
        g[rk] = {"G-O_terminus": go, "G2_CL": g2, "G3_drop": g3, "G-BASE_cold_CD": gb, "G5_CD": cd, "G5c_CL": cl,
                 "row_verdict": compose_row(go, g2, g3, cd, cl), "eta_F": F[rk]["eta"], "CD_endpoint_F": F[rk]["CD"]}
    gbase = "GATE FAIL" if "GATE FAIL" in (g["S"]["G-BASE_cold_CD"]["verdict"], g["P"]["G-BASE_cold_CD"]["verdict"]) else "PASS"
    # ---- divergence shipped vs patched on the endpoint adjoint (reported; different endpoints)
    div = []
    for dv, idx in COMPONENTS_REGISTERED:
        a, b = O["S"]["adjoint"]["CD"][dv], O["P"]["adjoint"]["CD"][dv]
        if idx < len(a) and idx < len(b):
            den = max(abs(a[idx]), abs(b[idx]), 1e-300)
            div.append({"dv": dv, "idx": idx, "J_shipped": a[idx], "J_patched": b[idx],
                        "divergence_pct": abs(a[idx] - b[idx]) / den * 100.0, "note": "different endpoints; a reading"})
    g9, g10, g12 = g_toolchain(rows), g_caps(rows), g_placement(rows)
    # ---- predictions, scored never adjusted
    preds = {"P1_patched_exit_optimal_within_budget": "HIT" if g["P"]["G-O_terminus"]["verdict"] == "PASS" else "MISS",
             "P2_shipped_terminus_max_iter_exceeded": "HIT" if O["S"]["exit_line"] == EXIT_MAXITER else "MISS",
             "P3_patched_endpoint_FD_PASS_5of5": "HIT" if (g["P"]["G5_CD"]["verdict"] == "PASS" and g["P"]["G5_CD"]["n_pass"] == 5) else "MISS",
             "P5_patched_drag_reduction_in_band": "HIT" if g["P"]["G3_drop"]["verdict"] == "PASS" else "MISS"}
    s = g["S"]["G5_CD"]
    preds["P4_shipped_endpoint_FD_GATE_FAIL"] = "HIT" if s["verdict"] == "GATE FAIL" else ("NOT_MEASURED" if s["verdict"] == "NOT A RESULT" else "MISS")
    tot = g10["total_core_min"]
    preds["P6_total_core_min_band"] = NOT_MEASURED if g10["not_measured"] else ("HIT" if PRED["P6_core_min_band"][0] <= tot <= PRED["P6_core_min_band"][1] else "MISS")
    n = O["P"]["n_iter"]
    preds["P7_patched_majors_in_band"] = NOT_MEASURED if n is None else ("HIT" if PRED["P7_majors_band"][0] <= n <= PRED["P7_majors_band"][1] else "MISS")
    # ---- item verdict (composition registered here)
    rv = (g["S"]["row_verdict"], g["P"]["row_verdict"])
    if "NOT A RESULT" in rv:
        verdict = "NOT A RESULT"
    elif "GATE FAIL" in rv + (gm2, gbase, g9["verdict"], g10["verdict"], g12["verdict"]):
        verdict = "GATE FAIL"
    elif "GATE REACHED" in rv:
        verdict = "GATE REACHED"
    else:
        verdict = "PASS"
    if verdict not in VOCAB:
        refuse("VOCAB", {"verdict": verdict})
    return {"item": "CURRICULUM-%s" % ITEM, "verdict": verdict,
            "rows": {"SHIPPED": g["S"]["row_verdict"], "PATCHED": g["P"]["row_verdict"]},
            "gates": {"G1_completion": "PASS", "G-M2_mesh_identity": gm2, "G-BASE": gbase, "SHIPPED": g["S"], "PATCHED": g["P"],
                      "G6_dot_product_duality": "NOT MEASURED -- the tutorial exposes no dot-product/duality test; named, never composed",
                      "G9_toolchain": g9, "G10_caps": g10, "G12_placement": g12},
            "mesh_points_md5": mesh, "divergence_shipped_vs_patched_CD_endpoint": div, "predictions": preds,
            "controls": controls, "completion": g1,
            "not_measured": {"G1": g1["not_measured"], "G10": g10["not_measured"], "G12": g12["not_measured"]},
            "field_classes": {"physics": list(FIELDS_PHYSICS), "infrastructure": list(FIELDS_INFRASTRUCTURE),
                              "rule": "absent infrastructure -> NOT_MEASURED beside the verdict; absent physics -> REFUSE (L-342)"},
            "no_gci": "no grid family; standing rule 5 has no row; NO GCI IS QUOTED",
            "capability_grid_cell": "3D . steady . transonic -- optimization converged; the gradient column is re-evidenced at the endpoint"}


# ================= selftest: planted fixtures, counted against a FROZEN unit count ======
ROWFMT = ("ARM={arm} ROW={row} IMG={img} DIGEST={dig} rc={rc} wall_s={wall} ranks={ranks} core_min={cm} "
          "cap_core_min={cap} enforced_wall_s=600 enforced_core_min={cap} memory=14g inspect(exit,oomkilled)=[{ke} {oom}] "
          "memavail_pre_GiB=20.00 memavail_post_GiB={mpost} cpuset={cs} delivered_cores_mean=[{dl}] "
          "siblings_pre=[] siblings_post=[] log={log} stamp=x\n")


def _fix(tmp, tweak=None):
    """Build a clean fixture; `tweak` mutates the dict of knobs before writing."""
    k = {"rc": {a: 0 for a in ARMS_REQUIRED}, "ke": {}, "oom": {a: "false" for a in ARMS_REQUIRED},
         "cm": dict(PREDICTED_CORE_MIN), "cs": {a: CPUSET_REGISTERED for a in ARMS_REQUIRED},
         "so": {a: SO_MD5[ARM_ROW[a]] for a in ARMS_REQUIRED}, "points": {a: b"points-fixture-bytes" for a in ARMS_REQUIRED},
         "err": {"S": {}, "P": {}}, "flip": {"S": set(), "P": set()}, "noplateau": {"S": set(), "P": set()},
         "terminal": {a: True for a in ARMS_REQUIRED}, "stale": set(), "ctrl_ok": True, "mpost": "20.00",
         "drop_row": set(), "inspect_file": set(), "dl": "3.98 n=10 max_nr_throttled=0",
         "exit": {"S": EXIT_OPTIMAL, "P": EXIT_OPTIMAL}, "n_iter": {"S": 18, "P": 16},
         "CD_cold": CD_COLD_REGISTERED, "CD_start": 0.03877565, "drop_pct": {"S": 1.0, "P": 1.0},
         "CL_final": {"S": 0.49999, "P": 0.50001}, "nprocs": 4, "endpoint_ok": True}
    if tweak:
        tweak(k)
    root = os.path.join(tmp, "root_%d" % int(time.time() * 1e6))
    os.makedirs(root)
    led = ["ITEM=D8R\n", "STAGED stamp=x\n"]
    J = {"twist": [-0.0023, -0.0020, -0.0017, -0.0013, -0.00086, -0.00054, -0.00020], "patchV": [0.00087, 0.0106]}
    omd5 = {}
    for arm in ARMS_REQUIRED:
        d = os.path.join(root, arm)
        os.makedirs(os.path.join(d, "0"))
        os.makedirs(os.path.join(d, "constant", "polyMesh"))
        open(os.path.join(d, "constant", "polyMesh", "points.gz"), "wb").write(k["points"][arm])
        ref = os.path.join(d, DATUM_REF[arm])
        open(ref, "w").write("U\n")
        t0 = int(os.path.getmtime(ref))
        open(os.path.join(d, ".d8r_age_datum"), "w").write("%d\n" % t0)
        log = "%s_x.log" % arm
        so = k["so"][arm]
        text = "D4S_CONTAINER_UID: 0\nD4S_IDWARP_SO_MD5: %s\nD4S_DEADLINE_IN_CONTAINER_S: 600\n" % so
        rk = "S" if arm.endswith("-S") else "P"
        art = os.path.join(d, ARTEFACT[arm])
        ident = {"libidwarp_so_md5": so, "idwarp_file": "/x/idwarp/__init__.py"}
        if arm.startswith("O"):
            adj = {"CD": {dv: [repr(v) for v in J[dv]] for dv in J},
                   "CL": {dv: [repr(v * 10.0) for v in J[dv]] for dv in J}}
            cd_f = k["CD_start"] * (1.0 - k["drop_pct"][rk] / 100.0)
            json.dump({"item": "D8R", "mode": "O", "identity": ident, "nprocs": k["nprocs"], "max_iter_registered": MAX_ITER,
                       "CD_cold": repr(k["CD_cold"]), "CL_cold": repr(0.457), "CD_start": repr(k["CD_start"]), "CL_start": repr(0.4999),
                       "CD_final": repr(cd_f), "CL_final": repr(k["CL_final"][rk]), "CD_endpoint": repr(cd_f),
                       "ipopt": {"exit_line": k["exit"][rk], "n_iter": k["n_iter"][rk]}, "adjoint": adj}, open(art, "w"))
            omd5[rk] = md5_of(art)
        else:
            rows_ = []
            for dv, idx in COMPONENTS_REGISTERED:
                j = J[dv][idx]
                e = k["err"][rk].get((dv, idx), 0.5)          # default 0.5 % error
                dref = j * (1.0 + e / 100.0)
                if (dv, idx) in k["flip"][rk]:
                    dref = -dref
                fd = {}
                for s in STEPS_REGISTERED[dv]:
                    scale = 1.0 if s == sorted(STEPS_REGISTERED[dv])[1] else 1.01
                    if (dv, idx) in k["noplateau"][rk]:
                        scale = 1.0 if s == sorted(STEPS_REGISTERED[dv])[1] else 1.5
                    fd[repr(s)] = {"step": s, "ok": True, "dCD": repr(dref * scale), "dCL": repr(dref * 10.0 * scale),
                                   "CD_plus": repr(0.0), "CD_minus": repr(0.0), "CL_plus": repr(0.0), "CL_minus": repr(0.0)}
                rows_.append({"dv": dv, "idx": idx, "status": "MEASURED", "fd": fd})
            planted = PLANT / (2.0 * CTRL_STEP) if k["ctrl_ok"] else 0.0
            rows_.append({"dv": "CTRL", "idx": 0, "status": "CONTROL",
                          "fd": {repr(CTRL_STEP): {"step": CTRL_STEP, "ok": True, "dCD": repr(0.0), "dCL": repr(0.0)}},
                          "planted": {"step": CTRL_STEP, "plant": PLANT, "dCD": repr(planted), "ok": True}})
            json.dump({"item": "D8R", "mode": "F", "identity": ident, "nprocs": k["nprocs"], "components_requested": COMPONENTS_REGISTERED,
                       "endpoint_source": {"md5": (omd5.get(rk) if k["endpoint_ok"] else "0" * 32)},
                       "CD_baseline": repr(0.0386), "CL_baseline": repr(0.5), "eta_used": repr(1.08e-5),
                       "rows": rows_}, open(art, "w"))
        if k["terminal"][arm]:
            text += TERMINAL[arm] + " ok\n"
        os.utime(art, (t0 - 5, t0 - 5) if arm in k["stale"] else (t0 + 5, t0 + 5))
        open(os.path.join(root, log), "w").write(text)
        ke = k["ke"].get(arm, k["rc"][arm])
        if arm in k["inspect_file"]:
            open(os.path.join(root, "%s_x.inspect.txt" % arm), "w").write("%d %s 2026-08-26T00:00:00Z 2026-08-26T00:01:00Z %s 15032385536 %s\n" % (ke, k["oom"][arm], k["cs"][arm], IMG_DIGEST[ARM_ROW[arm]]))
        if arm in k["drop_row"]:
            continue
        led.append(ROWFMT.format(arm=arm, row=ARM_ROW[arm], img="img", dig=IMG_DIGEST[ARM_ROW[arm]], rc=k["rc"][arm],
                                 wall=60, ranks=ARM_RANKS[arm], cm=k["cm"][arm], cap=CAPS[arm], ke=ke, oom=k["oom"][arm],
                                 mpost=k["mpost"], cs=k["cs"][arm], dl=k["dl"], log=log))
    open(os.path.join(root, "ledger.txt"), "w").write("".join(led))
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

    def tw(**kw):
        def f(k):
            for key, val in kw.items():
                if isinstance(val, dict) and isinstance(k.get(key), dict):
                    k[key].update(val)
                else:
                    k[key] = val
        return f
    # the fixture's points.gz bytes must hash to the registered md5 for the clean case: patch the module constant
    global POINTS_MD5
    real_points_md5 = POINTS_MD5
    POINTS_MD5 = hashlib.md5(b"points-fixture-bytes").hexdigest()
    try:
        r = grade(_fix(tmp))
        unit("U1 clean fixture (both rows Optimal) -> item PASS, both rows PASS, G-M2/G-BASE/G9/G10/G12 PASS",
             r["verdict"] == "PASS" and r["rows"] == {"SHIPPED": "PASS", "PATCHED": "PASS"} and r["gates"]["G-M2_mesh_identity"] == "PASS"
             and r["gates"]["G-BASE"] == "PASS" and r["gates"]["G9_toolchain"]["verdict"] == "PASS" and r["gates"]["G10_caps"]["verdict"] == "PASS" and r["gates"]["G12_placement"]["verdict"] == "PASS")
        unit("U2 clean fixture -> P1, P3, P5, P6, P7 HIT; P2 and P4 MISS (shipped clean by construction)",
             all(r["predictions"][k] == "HIT" for k in ("P1_patched_exit_optimal_within_budget", "P3_patched_endpoint_FD_PASS_5of5", "P5_patched_drag_reduction_in_band", "P6_total_core_min_band", "P7_patched_majors_in_band"))
             and r["predictions"]["P2_shipped_terminus_max_iter_exceeded"] == "MISS" and r["predictions"]["P4_shipped_endpoint_FD_GATE_FAIL"] == "MISS")
        unit("U19 grader-level plant SEEN on both F tables (rule 3)", r["controls"]["grader_plant_S"]["grader_plant_seen"] and r["controls"]["grader_plant_P"]["grader_plant_seen"] and r["controls"]["S"]["instrument_ctrl_zero"] == 0.0)
        r = grade(_fix(tmp, tw(err={"S": {("twist", 3): 7.0}})))
        unit("U3 PLANTED 7 % error on shipped twist[3] -> component GATE FAIL, SHIPPED row GATE FAIL, item GATE FAIL, P4 HIT",
             r["rows"]["SHIPPED"] == "GATE FAIL" and r["verdict"] == "GATE FAIL" and r["gates"]["SHIPPED"]["G5_CD"]["n_gate_fail"] == 1 and r["predictions"]["P4_shipped_endpoint_FD_GATE_FAIL"] == "HIT")
        r = grade(_fix(tmp, tw(flip={"S": {("twist", 0)}, "P": set()})))
        unit("U4 PLANTED sign flip on shipped twist[0] -> flip counted, SHIPPED GATE FAIL, P4 HIT, PATCHED PASS",
             r["gates"]["SHIPPED"]["G5_CD"]["sign_flips"] == 1 and r["rows"]["SHIPPED"] == "GATE FAIL" and r["predictions"]["P4_shipped_endpoint_FD_GATE_FAIL"] == "HIT" and r["rows"]["PATCHED"] == "PASS")
        r = grade(_fix(tmp, tw(noplateau={"S": {("twist", 1)}, "P": set()})))
        c0 = [c for c in r["gates"]["SHIPPED"]["G5_CD"]["components"] if c["idx"] == 1 and c["dv"] == "twist"][0]
        unit("U5 PLANTED no-plateau on one component -> that component NOT A RESULT, row still PASS on 4 graded",
             c0["verdict"] == "NOT A RESULT" and c0["reason"] == "NO_PLATEAU" and r["rows"]["SHIPPED"] == "PASS" and r["gates"]["SHIPPED"]["G5_CD"]["n_graded"] == 4)
        r = grade(_fix(tmp, tw(noplateau={"P": {("twist", 0), ("twist", 3), ("twist", 5)}, "S": set()})))
        unit("U6 three no-plateau components on PATCHED -> 2 graded < 3 -> row NOT A RESULT, item NOT A RESULT",
             r["rows"]["PATCHED"] == "NOT A RESULT" and r["verdict"] == "NOT A RESULT")
        unit("U7 rc=1 on O-P -> REFUSAL", refused(_fix(tmp, tw(rc={"O-P": 1}, ke={"O-P": 1}))))
        unit("U8 OOMKilled=true on F-S -> REFUSAL (G11 hard)", refused(_fix(tmp, tw(oom={"F-S": "true"}))))
        unit("U9 terminal marker absent in F-P log -> REFUSAL", refused(_fix(tmp, tw(terminal={"F-P": False}))))
        unit("U10 artefact OLDER than the age datum (O-S) -> REFUSAL (rule 4)", refused(_fix(tmp, tw(stale={"O-S"}))))
        unit("U11 instrument CTRL planted row broken -> REFUSAL (a reader not shown to see a non-zero)", refused(_fix(tmp, tw(ctrl_ok=False))))
        r = grade(_fix(tmp, tw(so={"O-P": SO_MD5["SHIPPED"]})))
        unit("U12 O-P carrying the SHIPPED .so md5 -> G9 GATE FAIL, item GATE FAIL", r["gates"]["G9_toolchain"]["verdict"] == "GATE FAIL" and r["verdict"] == "GATE FAIL")
        r = grade(_fix(tmp, tw(cm={"O-P": 1001.0})))
        unit("U13 O-P core_min 1001.0 > cap 1000.0 -> G10 GATE FAIL", r["gates"]["G10_caps"]["verdict"] == "GATE FAIL" and r["gates"]["G10_caps"]["per_arm"]["O-P"]["crossed"])
        r = grade(_fix(tmp, tw(cs={"O-S": "8,10,11,13"})))
        unit("U14 O-S on cpuset 8,10,11,13 (D5's) -> G12 GATE FAIL", r["gates"]["G12_placement"]["verdict"] == "GATE FAIL")
        r = grade(_fix(tmp, tw(points={"F-S": b"other-mesh-bytes"})))
        unit("U15 F-S points.gz with another md5 -> G-M2 GATE FAIL, item GATE FAIL", r["gates"]["G-M2_mesh_identity"] == "GATE FAIL" and r["verdict"] == "GATE FAIL")
        r = grade(_fix(tmp, tw(mpost="NOT_MEASURED", dl="NOT_MEASURED")))
        unit("U16 absent infrastructure fields -> verdict unchanged PASS, NOT_MEASURED named beside it (L-342)",
             r["verdict"] == "PASS" and r["not_measured"]["G1"].get("O-S") and "O-S" in r["not_measured"]["G12"])
        unit("U17 harness rc 0 vs kernel exit 1 disagreement -> REFUSAL", refused(_fix(tmp, tw(ke={"F-P": 1}))))
        unit("U18 ledger row absent, no inspect record -> REFUSAL", refused(_fix(tmp, tw(drop_row={"F-P"}))))
        r = grade(_fix(tmp, tw(drop_row={"F-P"}, inspect_file={"F-P"})))
        unit("U20 ledger row absent, ONE inspect record -> read from it, source named, core_min NOT_MEASURED, verdict PASS",
             r["verdict"] == "PASS" and r["completion"]["arms"]["F-P"]["source"] == "inspect_record" and "F-P" in r["not_measured"]["G10"])
        here = os.path.dirname(os.path.abspath(__file__))
        unit("U21 ast.Assert count = 0 in d8r_grade.py and d8r_of.py", count_asserts(os.path.abspath(__file__)) == 0 and count_asserts(os.path.join(here, "d8r_of.py")) == 0)
        p = os.path.join(tmp, "planted_assert.py")
        open(p, "w").write("x = 1\nassert x == 1\n")
        unit("U22 the assert counter sees a planted assert (=1)", count_asserts(p) == 1)
        # ---- the optimisation gates
        r = grade(_fix(tmp, tw(exit={"S": EXIT_MAXITER}, n_iter={"S": 30})))
        unit("U23 SHIPPED exit = max_iter exceeded, drop 1 % >= 10 eta -> SHIPPED GATE REACHED, P2 HIT, item GATE REACHED (PATCHED PASS)",
             r["rows"]["SHIPPED"] == "GATE REACHED" and r["predictions"]["P2_shipped_terminus_max_iter_exceeded"] == "HIT" and r["verdict"] == "GATE REACHED" and r["rows"]["PATCHED"] == "PASS")
        r = grade(_fix(tmp, tw(exit={"S": EXIT_MAXITER}, n_iter={"S": 30}, drop_pct={"S": 0.0001})))
        unit("U24 SHIPPED exit = max_iter exceeded, drop 0.0001 % < 10 eta -> G-O NOT A RESULT, row NOT A RESULT, item NOT A RESULT",
             r["gates"]["SHIPPED"]["G-O_terminus"]["verdict"] == "NOT A RESULT" and r["rows"]["SHIPPED"] == "NOT A RESULT" and r["verdict"] == "NOT A RESULT")
        r = grade(_fix(tmp, tw(exit={"P": "EXIT: Restoration Failed!"})))
        unit("U25 PATCHED exit = Restoration Failed -> G-O NOT A RESULT, P1 MISS, item NOT A RESULT",
             r["gates"]["PATCHED"]["G-O_terminus"]["verdict"] == "NOT A RESULT" and r["predictions"]["P1_patched_exit_optimal_within_budget"] == "MISS" and r["verdict"] == "NOT A RESULT")
        r = grade(_fix(tmp, tw(CL_final={"P": 0.51})))
        unit("U26 PATCHED CL_final 0.51 (|dev| 1e-2 > 5e-3) -> G2 GATE FAIL, row GATE FAIL", r["gates"]["PATCHED"]["G2_CL"]["verdict"] == "GATE FAIL" and r["rows"]["PATCHED"] == "GATE FAIL")
        r = grade(_fix(tmp, tw(drop_pct={"P": 6.0})))
        unit("U27 PATCHED drag reduction 6 % outside [0.29, 5.0] -> G3 GATE FAIL, P5 MISS, row GATE FAIL (never a silent widen)",
             r["gates"]["PATCHED"]["G3_drop"]["verdict"] == "GATE FAIL" and r["predictions"]["P5_patched_drag_reduction_in_band"] == "MISS" and r["rows"]["PATCHED"] == "GATE FAIL")
        r = grade(_fix(tmp, tw(CD_cold=CD_COLD_REGISTERED + 2.0e-4)))
        unit("U28 cold CD 2e-4 off the registered value (> 10 eta) -> G-BASE GATE FAIL, item GATE FAIL", r["gates"]["G-BASE"] == "GATE FAIL" and r["verdict"] == "GATE FAIL")
        unit("U29 n_iter 31 > registered MAX_ITER 30 -> REFUSAL (instrument defect)", refused(_fix(tmp, tw(n_iter={"P": 31}))))
        unit("U30 F arm whose endpoint md5 is not this row's O artefact -> REFUSAL", refused(_fix(tmp, tw(endpoint_ok=False))))
        unit("U31 nprocs 1 in an artefact (registered 4) -> REFUSAL", refused(_fix(tmp, tw(nprocs=1))))
    finally:
        POINTS_MD5 = real_points_md5
    print("D8R GRADER SELFTEST units=%d expected=%d failures=%d python_O=%s" % (n, EXPECTED_UNITS, len(fails), not __debug__))
    if n != EXPECTED_UNITS or fails:
        print("SELFTEST FAIL: %s" % (fails or "unit count %d != %d" % (n, EXPECTED_UNITS)))
        return 2
    print("D8R GRADER SELFTEST PASS %d/%d (counted against the frozen EXPECTED_UNITS)" % (n, EXPECTED_UNITS))
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
        d = os.path.join(a.tmpdir, "d8r_selftest_%d" % os.getpid()); os.makedirs(d, exist_ok=True)
        return selftest(d)
    if not a.root:
        print("usage: d8r_grade.py --root <run root> [--out FILE] | --selftest"); return 64
    try:
        r = grade(a.root)
    except Refusal as e:
        print("REFUSAL: %s -> NOT A RESULT" % e)
        if a.out:
            json.dump({"item": "CURRICULUM-%s" % ITEM, "verdict": "NOT A RESULT", "refusal": str(e)}, open(a.out, "w"), indent=1)
        return 2
    print(json.dumps(r, indent=1, default=str))
    if a.out:
        json.dump(r, open(a.out, "w"), indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
