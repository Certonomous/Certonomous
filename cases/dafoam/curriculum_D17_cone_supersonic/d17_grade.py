#!/usr/bin/env python3
"""Curriculum D17 COMPARATOR -- Cone_Supersonic 2D wedge (DAHisaFoam, M 1.96) baseline gradient,
TWO ROWS (SHIPPED + PATCHED), adjoint X against a central-FD table F.  FROZEN by md5 in
PREREGISTRATION.md section 7 before any container starts.  Computes nothing about
physics; renders verdicts from the FIXED vocabulary only (PASS / GATE REACHED / GATE FAIL /
NOT A RESULT / BLOCKED / PENDING).  Derived from curriculum_D16/d16_grade.py (d17_grade_DELTAS_from_d16.diff: item, caps, ceiling,
predictions, cpuset, the `shape`-only DV set, the registered components, G-M2 = 40,000 cells,
and G5c on CL REPLACED by a symmetry READING that is never composed -- see G5 below).  Shape: curriculum_D14/d14m_grade.py (built-in
--selftest counted against a FROZEN unit count); machinery: curriculum_D5/d5_grade.py
(ledger regex, L-342 field classes, arm-kind-aware completion).

WHAT IT GRADES (PREREGISTRATION.md section 3):
  G1   completion, ARM-KIND AWARE: every arm needs kernel rc == 0 (docker inspect, and
       the harness rc must agree), OOMKilled false, and the AGE GUARD on its registered
       artefact (strictly newer than the arm's own datum).  SOLVER arms (X-*, F-*) also
       need the instrument's TERMINAL MARKER in the arm log (D17_X_WRITTEN / D17_F_WRITTEN);
       the SCRIPT arm MESH needs `Mesh OK.` in checkMesh.log.  Any clause fails -> REFUSE
       (NOT A RESULT).  An arm with no ledger row is read from the launcher's surviving
       `<ARM>_<stamp>.inspect.txt` (the container itself is removed after inspect), with
       the source named per field and every infrastructure field NOT_MEASURED (L-342).
  G-M2 mesh identity: cells == 40,000 (blockMesh 2 blocks x 100x100x1 = 20,000, doubled by
       mirrorMesh across y = 0 -- DERIVED from system/blockMeshDict + mirrorMeshDict, not
       measured before this item) -> PASS else GATE FAIL (a different mesh is a different item).
  G5   per ROW, the bright line: per registered component, the FD reference is the
       MIDDLE step of the registered three; PLATEAU = the middle step agrees with at least
       one neighbour to 10 % (else the component is NOT A RESULT); band D = per-component
       |d_FD - J_adj| / |d_FD| <= 5.0 % AND the same sign (a SIGN FLIP is GATE FAIL whatever
       the magnitude); band E = aggregate vector-relative error over graded components
       <= 5.0 %.  Fewer than 3 graded components -> the row is NOT A RESULT.  G5 is graded
       on CD (the objective) ONLY.  CL is a SYMMETRY READING: the wedge is y-symmetric at
       0 deg and the shape functions move the j=0 / j=2 FFD rows in opposite y, so CL and
       dCL/dshape are zero by construction; the reading (max |J_adj CL|, max |d_FD CL|) is
       REPORTED beside the row and never composed (D16's G5c would have returned NEAR_ZERO
       -> NOT A RESULT on every component by construction).
  G6   dot-product / duality test: NOT MEASURED -- the tutorial exposes none; named.
  G9   toolchain per row: the ledger DIGEST, the container's `D4S_IDWARP_SO_MD5:` print
       and the artefact's in-process libidwarp.so md5 must all name the row's registered
       toolchain (shipped f0fcb488..., patched 85f59e87...).
  G10  caps: every row core_min <= its registered cap and the sum <= the ceiling;
       a crossing is GATE FAIL exactly as the frozen text says (report mode).
  G12  placement: cpuset == the registered 12,15 on every row; delivered cores >= 1.5
       of 2 where MEASURED, NOT_MEASURED disclosed otherwise.
  DIVERGENCE shipped-vs-patched per component on the adjoint is REPORTED with its number.

PLANTED CONTROLS (rule 3): (i) the instrument's CTRL component (derivative exactly 0.0)
and its PLANTED row (exactly PLANT/(2 s)) are re-read here and the grade REFUSES if the
reader cannot see them; (ii) this grader writes a copy of the F table with PLANT added to
every physical derivative into <root>/grader_controls/, re-reads it through the same
reader, and REFUSES unless every value moved by exactly PLANT.

L-342 (Sanaa, d4d0c29d): FIELDS_PHYSICS absent -> REFUSE; FIELDS_INFRASTRUCTURE absent
-> NOT_MEASURED, disclosed beside the verdict, never composed to PASS; present-but-garbage
-> REFUSE.  L-332: NO `assert` anywhere; the module counts ast.Assert nodes in its own
source and refuses on any.  No unconditional success print.
"""
import ast
import glob
import json
import math
import os
import re
import sys
import time

# ---- REGISTERED CONSTANTS (PREREGISTRATION.md; the document governs) ----------------
ITEM = "D17"
BASE = "/home/ubuntu/certonomous-runs/CURRICULUM-D17-cone-supersonic"
ARMS_REQUIRED = ["MESH", "X-S", "F-S", "X-P", "F-P"]
ARM_KIND = {"MESH": "SCRIPT", "X-S": "SOLVER", "F-S": "SOLVER", "X-P": "SOLVER", "F-P": "SOLVER"}
ARM_ROW = {"MESH": "SHIPPED", "X-S": "SHIPPED", "F-S": "SHIPPED", "X-P": "PATCHED", "F-P": "PATCHED"}
ARM_RANKS = {"MESH": 1, "X-S": 2, "F-S": 2, "X-P": 2, "F-P": 2}
ARTEFACT = {"MESH": "checkMesh.log", "X-S": "d17_X.json", "F-S": "d17_F.json", "X-P": "d17_X.json", "F-P": "d17_F.json"}
TERMINAL = {"X-S": "D17_X_WRITTEN", "F-S": "D17_F_WRITTEN", "X-P": "D17_X_WRITTEN", "F-P": "D17_F_WRITTEN"}
DATUM_REF = {"MESH": "0.orig/U", "X-S": "0/U", "F-S": "0/U", "X-P": "0/U", "F-P": "0/U"}
CAPS = {"MESH": 5.0, "X-S": 90.0, "F-S": 300.0, "X-P": 90.0, "F-P": 300.0}
ITEM_CEILING_CORE_MIN = 785.0
PREDICTED_CORE_MIN = {"MESH": 0.3, "X-S": 12.0, "F-S": 78.0, "X-P": 12.0, "F-P": 78.0}
CELLS_EXPECTED = 40000        # DERIVED: blockMesh 2 x (100 x 100 x 1) = 20,000, x2 by mirrorMesh (y = 0)
FD_BAND_PCT = 5.0            # band D, per component (D4 PREREGISTRATION.md:82; D7FR:228-229)
AGG_BAND_PCT = 5.0           # band E, aggregate vector-relative (same sources)
PLATEAU_TOL_PCT = 10.0
MIN_GRADED = 3
NEAR_ZERO_ABS = 1.0e-14
COMPONENTS_REGISTERED = [["shape", 0], ["shape", 1], ["shape", 3], ["shape", 4], ["shape", 5]]
STEPS_REGISTERED = {"shape": [1.0e-2, 1.0e-3, 1.0e-4]}
DVS = ("shape",)             # the tutorial's ONLY design variable group (6 shape functions; no patchV)
CTRL_STEP = 1.0e-3
PLANT = 1.234e-03
IMG_DIGEST = {"SHIPPED": "sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc",
              "PATCHED": "sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35"}
SO_MD5 = {"SHIPPED": "f0fcb488e0e98156575cd19548e91663", "PATCHED": "85f59e87253e0a71a813f64ca6e4c425"}
CPUSET_REGISTERED = "12,15"
DELIVERED_CORES_FLOOR = 1.5
PRED = {"P2_CL_abs_max": 1.0e-3, "P3_CD_band": (0.08, 0.45), "P4_patched_min_pass": 4,
        "P6_core_min_band": (60.0, 450.0), "P6_mesh_wall_s_max": 120.0}
FIELDS_PHYSICS = ("rc", "inspect_exit", "oomkilled", "terminal_statement", "age_guard",
                  "core_min", "cap_core_min", "DIGEST", "cpuset")
FIELDS_INFRASTRUCTURE = ("memavail_pre_GiB", "memavail_post_GiB", "delivered", "siblings_pre",
                         "siblings_post", "log", "wall_s")
NOT_MEASURED = "NOT_MEASURED"
VOCAB = {"PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"}
EXPECTED_UNITS = 22


class Refusal(Exception):
    pass


def refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail}, sort_keys=True, default=str))


def count_asserts(path):
    return sum(1 for n in ast.walk(ast.parse(open(path).read())) if isinstance(n, ast.Assert))


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


# ================= G1: COMPLETION, ARM-KIND AWARE =====================================
def arm_datum(base, arm):
    d = os.path.join(base, arm)
    p = os.path.join(d, ".d17_age_datum")
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
                          "note": "a run that fails any clause is not done (rule 4)"})
        adir, datum = arm_datum(base, arm)
        art = os.path.join(adir, ARTEFACT[arm])
        if not os.path.isfile(art):
            refuse("G1", {"artefact_absent": art, "arm": arm})
        if os.path.getmtime(art) <= datum:
            refuse("G1", {"artefact_not_newer_than_datum": art, "arm": arm, "datum": datum,
                          "artefact_mtime": os.path.getmtime(art), "note": "age guard, rule 4"})
        kind = ARM_KIND[arm]
        if kind == "SOLVER":
            logname = r.get("log")
            logpath = os.path.join(base, logname) if logname else None
            if not logpath or not os.path.isfile(logpath):
                refuse("G1", {"log_absent": logname, "arm": arm, "note": "a missing log is a FAILED clause"})
            text = open(logpath, errors="replace").read()
            if TERMINAL[arm] not in text:
                refuse("G1", {"terminal_marker_absent": TERMINAL[arm], "arm": arm, "log": logname})
            r["log_text"] = text
        else:
            text = open(art, errors="replace").read()
            if not re.search(r"^Mesh OK\.$", text, re.M):
                refuse("G1", {"mesh_ok_absent": art, "arm": arm})
            r["log_text"] = open(os.path.join(base, r["log"]), errors="replace").read() if r.get("log") and os.path.isfile(os.path.join(base, r["log"])) else ""
        out["arms"][arm] = {"kind": kind, "kernel_rc": kernel_rc, "oomkilled": oom, "artefact": ARTEFACT[arm],
                            "source": r["source"], "field_sources": r["field_sources"]}
        if r.get("infra_not_measured"):
            out["not_measured"][arm] = r["infra_not_measured"]
    return out


# ================= readers with planted controls ======================================
def read_X(path):
    j = json.load(open(path))
    adj = {}
    for of in ("CD", "CL"):
        adj[of] = {dv: [float(v) for v in j["adjoint"][of][dv]] for dv in DVS}
    return {"CD": float(j["CD_baseline"]), "CL": float(j["CL_baseline"]), "adjoint": adj,
            "so_md5": (j.get("identity") or {}).get("libidwarp_so_md5"), "nprocs": j.get("nprocs")}


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
            "so_md5": (j.get("identity") or {}).get("libidwarp_so_md5"), "raw": j}


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


def symmetry_reading(X, F):
    """CL for the y-symmetric wedge at 0 deg: zero by construction, REPORTED, never composed."""
    adj = [abs(v) for v in X["adjoint"]["CL"]["shape"]]
    fd = [abs(v["dCL"]) for row in F["table"].values() for v in row["fd"].values() if v["ok"] and v["dCL"] is not None]
    return {"objective": "CL", "kind": "SYMMETRY_READING_NOT_GRADED", "CL_baseline": X["CL"],
            "max_abs_J_adj_CL": (max(adj) if adj else None), "max_abs_dFD_CL": (max(fd) if fd else None),
            "note": "zero by construction for the symmetric wedge; a non-zero here is reported, it moves no verdict"}


def compose_row(g_cd):
    if g_cd["verdict"] == "NOT A RESULT":
        return "NOT A RESULT"
    if g_cd["verdict"] == "GATE FAIL":
        return "GATE FAIL"
    return "PASS"


# ================= G9 / G10 / G12 ======================================================
def g_toolchain(rows):
    out = {"per_arm": {}, "verdict": "PASS"}
    for arm in ARMS_REQUIRED:
        r = rows[arm]
        row = ARM_ROW[arm]
        m = re.search(r"D4S_IDWARP_SO_MD5:\s*([0-9a-f]{32})", r.get("log_text", ""))
        printed = m.group(1) if m else None
        ok = (r.get("DIGEST") == IMG_DIGEST[row]) and (printed == SO_MD5[row])
        art_md5 = r.get("artefact_so_md5")
        if arm != "MESH":
            ok = ok and (art_md5 == SO_MD5[row])
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
        dl_ok = True if (dl is None or ARM_RANKS[arm] == 1) else dl >= DELIVERED_CORES_FLOOR
        out["per_arm"][arm] = {"cpuset": r.get("cpuset"), "delivered_cores_mean": (dl if dl is not None else NOT_MEASURED)}
        if not (cs_ok and dl_ok):
            out["verdict"] = "GATE FAIL"
    return out


# ================= the grade ==========================================================
def grade(root):
    rows = read_ledger(os.path.join(root, "ledger.txt"))
    g1 = g_completion(root, rows)
    # ---- MESH identity
    cm_txt = open(os.path.join(root, "MESH", "checkMesh.log"), errors="replace").read()
    m = re.search(r"^\s*cells:\s+(\d+)", cm_txt, re.M)
    if not m:
        refuse("G-M2", {"cells_absent_in_checkMesh": True})
    cells = int(m.group(1))
    gm2 = "PASS" if cells == CELLS_EXPECTED else "GATE FAIL"
    # ---- rows
    X = {"S": read_X(os.path.join(root, "X-S", "d17_X.json")), "P": read_X(os.path.join(root, "X-P", "d17_X.json"))}
    F = {"S": read_F(os.path.join(root, "F-S", "d17_F.json")), "P": read_F(os.path.join(root, "F-P", "d17_F.json"))}
    rows["X-S"]["artefact_so_md5"] = X["S"]["so_md5"]; rows["X-P"]["artefact_so_md5"] = X["P"]["so_md5"]
    rows["F-S"]["artefact_so_md5"] = F["S"]["so_md5"]; rows["F-P"]["artefact_so_md5"] = F["P"]["so_md5"]
    controls = {"S": ctrl_control(F["S"]), "P": ctrl_control(F["P"]),
                "grader_plant_S": grader_plant_control(root, os.path.join(root, "F-S", "d17_F.json"), "S"),
                "grader_plant_P": grader_plant_control(root, os.path.join(root, "F-P", "d17_F.json"), "P")}
    g5 = {}
    for rk in ("S", "P"):
        cd = grade_components(X[rk], F[rk], "CD")
        cl = symmetry_reading(X[rk], F[rk])
        g5[rk] = {"G5_CD": cd, "CL_symmetry_reading": cl, "row_verdict": compose_row(cd),
                  "CD_baseline": X[rk]["CD"], "CL_baseline": X[rk]["CL"], "eta_F": F[rk]["eta"]}
    # ---- divergence shipped vs patched on the adjoint (reported with its number)
    div = []
    for dv, idx in COMPONENTS_REGISTERED:
        a, b = X["S"]["adjoint"]["CD"][dv], X["P"]["adjoint"]["CD"][dv]
        if idx < len(a) and idx < len(b):
            den = max(abs(a[idx]), abs(b[idx]), 1e-300)
            div.append({"dv": dv, "idx": idx, "J_shipped": a[idx], "J_patched": b[idx],
                        "divergence_pct": abs(a[idx] - b[idx]) / den * 100.0})
    g9, g10, g12 = g_toolchain(rows), g_caps(rows), g_placement(rows)
    # ---- predictions, scored never adjusted
    preds = {"P1_cells_40000": "HIT" if gm2 == "PASS" else "MISS",
             "P2_CL_baseline_abs_le_1e-3": "HIT" if abs(X["S"]["CL"]) <= PRED["P2_CL_abs_max"] else "MISS",
             "P3_CD_baseline_in_band": "HIT" if PRED["P3_CD_band"][0] <= X["S"]["CD"] <= PRED["P3_CD_band"][1] else "MISS",
             "P4_patched_row_CD_PASS_ge4": "HIT" if (g5["P"]["G5_CD"]["verdict"] == "PASS" and g5["P"]["G5_CD"]["n_pass"] >= PRED["P4_patched_min_pass"]) else "MISS"}
    s6 = [c for c in g5["S"]["G5_CD"]["components"] if c["dv"] == "shape" and c["idx"] == 0]
    preds["P5_shipped_shape0_outside_band_D_or_flipped"] = "HIT" if (s6 and s6[0].get("verdict") == "GATE FAIL") else ("NOT_MEASURED" if (s6 and s6[0].get("verdict") == "NOT A RESULT") else "MISS")
    tot = g10["total_core_min"]
    if g10["not_measured"]:
        preds["P6_total_core_min_band"] = NOT_MEASURED
    else:
        preds["P6_total_core_min_band"] = "HIT" if PRED["P6_core_min_band"][0] <= tot <= PRED["P6_core_min_band"][1] else "MISS"
    mw = rows["MESH"].get("wall_s")
    preds["P6b_mesh_wall_le_120s"] = NOT_MEASURED if mw is None else ("HIT" if mw <= PRED["P6_mesh_wall_s_max"] else "MISS")
    # ---- item verdict (composition registered here)
    if "NOT A RESULT" in (g5["S"]["row_verdict"], g5["P"]["row_verdict"]):
        verdict = "NOT A RESULT"
    elif "GATE FAIL" in (g5["S"]["row_verdict"], g5["P"]["row_verdict"], gm2, g9["verdict"], g10["verdict"], g12["verdict"]):
        verdict = "GATE FAIL"
    else:
        verdict = "PASS"
    if verdict not in VOCAB:
        refuse("VOCAB", {"verdict": verdict})
    return {"item": "CURRICULUM-%s" % ITEM, "verdict": verdict,
            "rows": {"SHIPPED": g5["S"]["row_verdict"], "PATCHED": g5["P"]["row_verdict"]},
            "gates": {"G1_completion": "PASS", "G-M2_mesh_identity": gm2, "G5_SHIPPED": g5["S"], "G5_PATCHED": g5["P"],
                      "G6_dot_product_duality": "NOT MEASURED -- the tutorial exposes no dot-product/duality test; named, never composed",
                      "G9_toolchain": g9, "G10_caps": g10, "G12_placement": g12},
            "mesh_cells": cells, "divergence_shipped_vs_patched_CD": div, "predictions": preds,
            "controls": controls, "completion": g1,
            "not_measured": {"G1": g1["not_measured"], "G10": g10["not_measured"], "G12": g12["not_measured"]},
            "field_classes": {"physics": list(FIELDS_PHYSICS), "infrastructure": list(FIELDS_INFRASTRUCTURE),
                              "rule": "absent infrastructure -> NOT_MEASURED beside the verdict; absent physics -> REFUSE (L-342)"},
            "no_gci": "no grid family; standing rule 5 has no row; NO GCI IS QUOTED",
            "capability_grid_cell": "2D . steady . supersonic -- gradients computed + FD-verified; this item moves ONLY that column"}


# ================= selftest: planted fixtures, counted against a FROZEN unit count ======
ROWFMT = ("ARM={arm} ROW={row} IMG={img} DIGEST={dig} rc={rc} wall_s={wall} ranks={ranks} core_min={cm} "
          "cap_core_min={cap} enforced_wall_s=600 enforced_core_min={cap} memory=4g inspect(exit,oomkilled)=[{ke} {oom}] "
          "memavail_pre_GiB=20.00 memavail_post_GiB={mpost} cpuset={cs} delivered_cores_mean=[{dl}] "
          "siblings_pre=[] siblings_post=[] log={log} stamp=x\n")


def _fix(tmp, tweak=None):
    """Build a clean fixture; `tweak` mutates the dict of knobs before writing."""
    k = {"rc": {a: 0 for a in ARMS_REQUIRED}, "ke": {}, "oom": {a: "false" for a in ARMS_REQUIRED},
         "cm": dict(PREDICTED_CORE_MIN), "cs": {a: CPUSET_REGISTERED for a in ARMS_REQUIRED},
         "so": {a: SO_MD5[ARM_ROW[a]] for a in ARMS_REQUIRED}, "cells": CELLS_EXPECTED,
         "err": {"S": {}, "P": {}}, "flip": {"S": set(), "P": set()}, "noplateau": {"S": set(), "P": set()},
         "terminal": {a: True for a in ARMS_REQUIRED}, "stale": set(), "ctrl_ok": True, "mpost": "20.00",
         "drop_row": set(), "inspect_file": set(), "dl": "1.99 n=10 max_nr_throttled=0", "CL": 0.0, "CD": 0.27}
    if tweak:
        tweak(k)
    root = os.path.join(tmp, "root_%d" % int(time.time() * 1e6))
    os.makedirs(root)
    led = ["ITEM=D17\n", "STAGED stamp=x\n"]
    for arm in ARMS_REQUIRED:
        d = os.path.join(root, arm)
        os.makedirs(os.path.join(d, "0.orig" if arm == "MESH" else "0"))
        ref = os.path.join(d, DATUM_REF[arm])
        open(ref, "w").write("U\n")
        t0 = int(os.path.getmtime(ref))
        open(os.path.join(d, ".d17_age_datum"), "w").write("%d\n" % t0)
        log = "%s_x.log" % arm
        so = k["so"][arm]
        text = "D4S_CONTAINER_UID: 0\nD4S_IDWARP_SO_MD5: %s\nD4S_DEADLINE_IN_CONTAINER_S: 600\n" % so
        if arm == "MESH":
            art = os.path.join(d, "checkMesh.log")
            open(art, "w").write("Mesh stats\n    cells:            %d\n\nMesh OK.\n" % k["cells"])
            text += "D17_CHECKMESH_RC 0\n"
        else:
            rk = "S" if arm.endswith("-S") else "P"
            art = os.path.join(d, ARTEFACT[arm])
            ident = {"libidwarp_so_md5": so, "idwarp_file": "/x/idwarp/__init__.py"}
            J = {"shape": [-0.011, 0.02, -0.03, 0.041, 0.05, -0.06]}
            if arm.startswith("X"):
                adj = {"CD": {dv: [repr(v) for v in J[dv]] for dv in J},
                       "CL": {dv: [repr(0.0) for v in J[dv]] for dv in J}}
                json.dump({"item": "D17", "mode": "X", "identity": ident, "nprocs": 2, "CD_baseline": repr(k["CD"]),
                           "CL_baseline": repr(k["CL"]), "adjoint": adj}, open(art, "w"))
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
                        fd[repr(s)] = {"step": s, "ok": True, "dCD": repr(dref * scale), "dCL": repr(0.0),
                                       "CD_plus": repr(0.0), "CD_minus": repr(0.0), "CL_plus": repr(0.0), "CL_minus": repr(0.0)}
                    rows_.append({"dv": dv, "idx": idx, "status": "MEASURED", "fd": fd})
                planted = PLANT / (2.0 * CTRL_STEP) if k["ctrl_ok"] else 0.0
                rows_.append({"dv": "CTRL", "idx": 0, "status": "CONTROL",
                              "fd": {repr(CTRL_STEP): {"step": CTRL_STEP, "ok": True, "dCD": repr(0.0), "dCL": repr(0.0)}},
                              "planted": {"step": CTRL_STEP, "plant": PLANT, "dCD": repr(planted), "ok": True}})
                json.dump({"item": "D17", "mode": "F", "identity": ident, "components_requested": COMPONENTS_REGISTERED,
                           "CD_baseline": repr(k["CD"]), "CL_baseline": repr(k["CL"]), "eta_used": repr(1e-9),
                           "rows": rows_}, open(art, "w"))
            if k["terminal"][arm]:
                text += TERMINAL[arm] + " ok\n"
        os.utime(art, (t0 - 5, t0 - 5) if arm in k["stale"] else (t0 + 5, t0 + 5))
        open(os.path.join(root, log), "w").write(text)
        ke = k["ke"].get(arm, k["rc"][arm])
        if arm in k["inspect_file"]:
            open(os.path.join(root, "%s_x.inspect.txt" % arm), "w").write("%d %s 2026-08-26T00:00:00Z 2026-08-26T00:01:00Z %s 4294967296 %s\n" % (ke, k["oom"][arm], k["cs"][arm], IMG_DIGEST[ARM_ROW[arm]]))
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
    r = grade(_fix(tmp))
    unit("U1 clean fixture -> item PASS, both rows PASS, G-M2/G9/G10/G12 PASS",
         r["verdict"] == "PASS" and r["rows"] == {"SHIPPED": "PASS", "PATCHED": "PASS"} and r["gates"]["G-M2_mesh_identity"] == "PASS"
         and r["gates"]["G9_toolchain"]["verdict"] == "PASS" and r["gates"]["G10_caps"]["verdict"] == "PASS" and r["gates"]["G12_placement"]["verdict"] == "PASS")
    unit("U2 clean fixture -> P1-P4, P6 HIT; P5 MISS (shape[0] clean by construction)",
         all(r["predictions"][k] == "HIT" for k in ("P1_cells_40000", "P2_CL_baseline_abs_le_1e-3", "P3_CD_baseline_in_band", "P4_patched_row_CD_PASS_ge4", "P6_total_core_min_band", "P6b_mesh_wall_le_120s")) and r["predictions"]["P5_shipped_shape0_outside_band_D_or_flipped"] == "MISS")
    unit("U19 grader-level plant SEEN on both F tables (rule 3)", r["controls"]["grader_plant_S"]["grader_plant_seen"] and r["controls"]["grader_plant_P"]["grader_plant_seen"] and r["controls"]["S"]["instrument_ctrl_zero"] == 0.0)
    r = grade(_fix(tmp, tw(err={"S": {("shape", 3): 7.0}})))
    unit("U3 PLANTED 7 % error on shipped shape[3] -> component GATE FAIL, SHIPPED row GATE FAIL, item GATE FAIL",
         r["rows"]["SHIPPED"] == "GATE FAIL" and r["verdict"] == "GATE FAIL" and r["gates"]["G5_SHIPPED"]["G5_CD"]["n_gate_fail"] == 1)
    r = grade(_fix(tmp, tw(flip={"S": {("shape", 0)}, "P": set()})))
    unit("U4 PLANTED sign flip on shipped shape[0] -> flip counted, SHIPPED GATE FAIL, P5 HIT, PATCHED PASS",
         r["gates"]["G5_SHIPPED"]["G5_CD"]["sign_flips"] == 1 and r["rows"]["SHIPPED"] == "GATE FAIL" and r["predictions"]["P5_shipped_shape0_outside_band_D_or_flipped"] == "HIT" and r["rows"]["PATCHED"] == "PASS")
    r = grade(_fix(tmp, tw(noplateau={"S": {("shape", 1)}, "P": set()})))
    c0 = [c for c in r["gates"]["G5_SHIPPED"]["G5_CD"]["components"] if c["idx"] == 1 and c["dv"] == "shape"][0]
    unit("U5 PLANTED no-plateau on one component -> that component NOT A RESULT, row still PASS on 4 graded",
         c0["verdict"] == "NOT A RESULT" and c0["reason"] == "NO_PLATEAU" and r["rows"]["SHIPPED"] == "PASS" and r["gates"]["G5_SHIPPED"]["G5_CD"]["n_graded"] == 4)
    r = grade(_fix(tmp, tw(noplateau={"P": {("shape", 0), ("shape", 3), ("shape", 5)}, "S": set()})))
    unit("U6 three no-plateau components on PATCHED -> 2 graded < 3 -> row NOT A RESULT, item NOT A RESULT",
         r["rows"]["PATCHED"] == "NOT A RESULT" and r["verdict"] == "NOT A RESULT")
    unit("U7 rc=1 on X-P -> REFUSAL", refused(_fix(tmp, tw(rc={"X-P": 1}, ke={"X-P": 1}))))
    unit("U8 OOMKilled=true on F-S -> REFUSAL", refused(_fix(tmp, tw(oom={"F-S": "true"}))))
    unit("U9 terminal marker absent in F-P log -> REFUSAL", refused(_fix(tmp, tw(terminal={"F-P": False}))))
    unit("U10 artefact OLDER than the age datum (X-S) -> REFUSAL (rule 4)", refused(_fix(tmp, tw(stale={"X-S"}))))
    unit("U11 instrument CTRL planted row broken -> REFUSAL (a reader not shown to see a non-zero)", refused(_fix(tmp, tw(ctrl_ok=False))))
    r = grade(_fix(tmp, tw(so={"X-P": SO_MD5["SHIPPED"]})))
    unit("U12 X-P carrying the SHIPPED .so md5 -> G9 GATE FAIL, item GATE FAIL", r["gates"]["G9_toolchain"]["verdict"] == "GATE FAIL" and r["verdict"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(cm={"F-S": 301.0})))
    unit("U13 F-S core_min 301.0 > cap 300.0 -> G10 GATE FAIL", r["gates"]["G10_caps"]["verdict"] == "GATE FAIL" and r["gates"]["G10_caps"]["per_arm"]["F-S"]["crossed"])
    r = grade(_fix(tmp, tw(cs={"X-S": "4,14"})))
    unit("U14 X-S on cpuset 4,14 (D16's) -> G12 GATE FAIL", r["gates"]["G12_placement"]["verdict"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(cells=40001)))
    unit("U15 cells 40001 -> G-M2 GATE FAIL, P1 MISS", r["gates"]["G-M2_mesh_identity"] == "GATE FAIL" and r["predictions"]["P1_cells_40000"] == "MISS")
    r = grade(_fix(tmp, tw(mpost="NOT_MEASURED", dl="NOT_MEASURED")))
    unit("U16 absent infrastructure fields -> verdict unchanged PASS, NOT_MEASURED named beside it (L-342)",
         r["verdict"] == "PASS" and r["not_measured"]["G1"].get("X-S") and "X-S" in r["not_measured"]["G12"])
    unit("U17 harness rc 0 vs kernel exit 1 disagreement -> REFUSAL", refused(_fix(tmp, tw(ke={"F-P": 1}))))
    unit("U18 ledger row absent, no inspect record -> REFUSAL", refused(_fix(tmp, tw(drop_row={"F-P"}))))
    r = grade(_fix(tmp, tw(drop_row={"F-P"}, inspect_file={"F-P"})))
    unit("U20 ledger row absent, ONE inspect record -> read from it, source named, core_min NOT_MEASURED, verdict PASS",
         r["verdict"] == "PASS" and r["completion"]["arms"]["F-P"]["source"] == "inspect_record" and "F-P" in r["not_measured"]["G10"])
    here = os.path.dirname(os.path.abspath(__file__))
    unit("U21 ast.Assert count = 0 in d17_grade.py and d17_xf.py", count_asserts(os.path.abspath(__file__)) == 0 and count_asserts(os.path.join(here, "d17_xf.py")) == 0)
    p = os.path.join(tmp, "planted_assert.py")
    open(p, "w").write("x = 1\nassert x == 1\n")
    unit("U22 the assert counter sees a planted assert (=1)", count_asserts(p) == 1)
    print("D17 GRADER SELFTEST units=%d expected=%d failures=%d python_O=%s" % (n, EXPECTED_UNITS, len(fails), not __debug__))
    if n != EXPECTED_UNITS or fails:
        print("SELFTEST FAIL: %s" % (fails or "unit count %d != %d" % (n, EXPECTED_UNITS)))
        return 2
    print("D17 GRADER SELFTEST PASS %d/%d (counted against the frozen EXPECTED_UNITS)" % (n, EXPECTED_UNITS))
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
        d = os.path.join(a.tmpdir, "d17_selftest_%d" % os.getpid()); os.makedirs(d, exist_ok=True)
        return selftest(d)
    if not a.root:
        print("usage: d17_grade.py --root <run root> [--out FILE] | --selftest"); return 64
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
