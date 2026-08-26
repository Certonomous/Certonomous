#!/usr/bin/env python3
"""Curriculum AV2 COMPARATOR -- NACA0012 INCOMPRESSIBLE (DASimpleFoam) baseline gradient,
FORWARD-mode AD (ADF) against REVERSE-mode AD (ADR) at np = 1, TWO ROWS (SHIPPED + PATCHED):
the family's first dot-product / duality rung, at the total level per registered component
(ADJOINT_VERIFICATION_STANDARD.md section 2, v1.0a).  FROZEN by md5 in PREREGISTRATION.md
section 7 before any container starts.  Computes nothing about physics; renders verdicts
from the FIXED vocabulary only (PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED /
PENDING).  DERIVED from curriculum_AV1/av1_grade.py (0b3ebaa4, md5 87f15e05130cfdb3cbf195d1daba6154):
ledger regex, L-342 field classes, completion, inspect fallback, G9/G10/G12 and the selftest
shape are AV1's; G-NP is REPLACED by G-DP (av2_grade_DELTAS_from_av1.diff).

WHAT IT GRADES (PREREGISTRATION.md section 3):
  G1   completion, ARM-KIND AWARE (AV1's form): kernel rc == 0, OOMKilled false, age guard,
       terminal marker (AV2_X_WRITTEN / AV2_FAD_WRITTEN) and the instrument's planted-control
       line (AV2_PLANTED_CONTROL_SEEN) in every solver log; MESH needs `Mesh OK.`.
  G-M2 mesh identity: cells == 4,032.
  G-DP per ROW, the bright line: for each registered component k the forward total g_fwd,k
       (FAD artefact) and the reverse total g_rev,k (X artefact) satisfy
           eps_k = |g_fwd,k - g_rev,k| / max(|g_fwd,k|, |g_rev,k|) <= 1.0e-5
       on CD and on CL; max(|.|) < 1e-14 -> NEAR_ZERO -> the component is NOT A RESULT;
       fewer than 3 graded components -> the row is NOT A RESULT.  Band: 10 x the adjoint
       solve's gmresRelTol (1e-6, the producer's value, read from the artefact identity and
       REFUSED if it is not 1e-6), standard section 2.  THE FORWARD-CHANNEL CONTROLS (v1.0a)
       are re-checked HERE from the artefact: a forward value exactly 0.0, exactly 1.0, or
       within 1e-6 relative of the baseline function value -> REFUSE (NOT A RESULT).  A FAD
       row carrying `blocked` -> the ROW is BLOCKED (never PASS, never NOT A RESULT), and the
       item is BLOCKED if either row is.
  G9   toolchain per row (ledger DIGEST, D4S_IDWARP_SO_MD5: print, artefact .so md5).
  G10  caps: every arm core_min <= its cap and the sum <= the ceiling (75.0).
  G12  placement: cpuset == 0,1 on every arm; delivered cores NOT gated at one rank.
  DIVERGENCE shipped-vs-patched on the reverse CD gradient is REPORTED per component; the
       forward-vs-reverse divergence per row is the gate.

PLANTED CONTROLS (rule 3): (i) AV2_PLANTED_CONTROL_SEEN required in every solver log; (ii)
the grader writes a copy of the SHIPPED X artefact with PLANT added to every total and
refuses unless the reader sees it; (iii) a copy of the SHIPPED X artefact with every reverse
total SIGN-FLIPPED (the deliberately wrong transpose) is graded through G-DP against the
real FAD artefact and MUST read GATE FAIL on every graded component, else REFUSE; (iv) a
copy of the SHIPPED FAD artefact with every forward value set to exactly 0.0 (the silent
no-op the mphys hooks would produce) MUST be REFUSED by the control re-check, else REFUSE.

L-342: FIELDS_PHYSICS absent -> REFUSE; FIELDS_INFRASTRUCTURE absent -> NOT_MEASURED beside
the verdict.  L-332: NO `assert` anywhere; ast.Assert counted, refused on any.
"""
import ast
import glob
import json
import os
import re
import sys
import time

# ---- REGISTERED CONSTANTS (PREREGISTRATION.md; the document governs) ----------------
ITEM = "AV2"
BASE = "/home/ubuntu/certonomous-runs/CURRICULUM-AV2-a1-naca0012-duality"
ARMS_REQUIRED = ["MESH", "X-S", "FAD-S", "X-P", "FAD-P"]
ARM_KIND = {"MESH": "SCRIPT", "X-S": "SOLVER", "FAD-S": "SOLVER", "X-P": "SOLVER", "FAD-P": "SOLVER"}
ARM_ROW = {"MESH": "SHIPPED", "X-S": "SHIPPED", "FAD-S": "SHIPPED", "X-P": "PATCHED", "FAD-P": "PATCHED"}
ARM_RANKS = {a: 1 for a in ARMS_REQUIRED}
ARTEFACT = {"MESH": "checkMesh.log", "X-S": "av2_X.json", "FAD-S": "av2_FAD.json", "X-P": "av2_X.json", "FAD-P": "av2_FAD.json"}
TERMINAL = {"X-S": "AV2_X_WRITTEN", "FAD-S": "AV2_FAD_WRITTEN", "X-P": "AV2_X_WRITTEN", "FAD-P": "AV2_FAD_WRITTEN"}
CONTROL_LINE = "AV2_PLANTED_CONTROL_SEEN"
DATUM_REF = {a: ("0.orig/U" if a == "MESH" else "0/U") for a in ARMS_REQUIRED}
CAPS = {"MESH": 5.0, "X-S": 10.0, "FAD-S": 25.0, "X-P": 10.0, "FAD-P": 25.0}
ITEM_CEILING_CORE_MIN = 75.0
PREDICTED_CORE_MIN = {"MESH": 0.3, "X-S": 2.5, "FAD-S": 5.0, "X-P": 2.5, "FAD-P": 5.0}
CELLS_EXPECTED = 4032
COMPONENTS_REGISTERED = [["shape", 0], ["shape", 3], ["shape", 6], ["shape", 7], ["patchV", 1]]
DP_BAND = 1.0e-5             # 10 x gmresRelTol (standard sec.2)
GMRES_REL_TOL_REGISTERED = 1.0e-6
NEAR_ZERO_ABS = 1.0e-14
ECHO_TOL = 1.0e-6
MIN_GRADED = 3
PLANT = 1.234e-03
IMG_DIGEST = {"SHIPPED": "sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc",
              "PATCHED": "sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35"}
SO_MD5 = {"SHIPPED": "f0fcb488e0e98156575cd19548e91663", "PATCHED": "85f59e87253e0a71a813f64ca6e4c425"}
CPUSET_REGISTERED = "0,1"
PRED = {"P5_core_min_band": (8.0, 40.0), "P5_fad_over_x_band": (1.0, 4.0), "P6_mesh_wall_s_max": 120.0}
FIELDS_PHYSICS = ("rc", "inspect_exit", "oomkilled", "terminal_statement", "age_guard",
                  "core_min", "cap_core_min", "DIGEST", "cpuset")
FIELDS_INFRASTRUCTURE = ("memavail_pre_GiB", "memavail_post_GiB", "delivered", "siblings_pre",
                         "siblings_post", "log", "wall_s")
NOT_MEASURED = "NOT_MEASURED"
VOCAB = {"PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"}
EXPECTED_UNITS = 25


class Refusal(Exception):
    pass


def refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail}, sort_keys=True, default=str))


def count_asserts(path):
    return sum(1 for n in ast.walk(ast.parse(open(path).read())) if isinstance(n, ast.Assert))


# ================= LEDGER (physics vs infrastructure, L-342) -- D5/D15/AV1's regex ====
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
            refuse("ledger", {"row_unparseable": line.strip()[:300], "note": "PRESENT-BUT-GARBAGE row: refused, never skipped"})
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
               "inspect_exit": (parts[0] if parts else None), "oomkilled": (parts[1] if len(parts) > 1 else None),
               "memavail_pre_GiB": _infra_float(g["mempre"]), "memavail_post_GiB": _infra_float(g["mempost"]),
               "cpuset": g["cpuset"], "delivered": g["delivered"], "siblings_pre": g["sibpre"],
               "siblings_post": g["sibpost"], "log": g["log"], "source": "ledger_row",
               "field_sources": {"all": "ledger_row"}, "infra_not_measured": infra_nm}
        if row["ARM"] in rows:
            refuse("ledger", {"duplicate_arm_row": row["ARM"], "note": "two records for one run is the defect"})
        rows[row["ARM"]] = row
    return rows


def inspect_file_fallback(base, arm):
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
            "ranks": ARM_RANKS[arm], "core_min": None, "cap_core_min": CAPS[arm], "enforced_core_min": CAPS[arm],
            "memory": parts[5] if len(parts) > 5 else None, "inspect_exit": parts[0], "oomkilled": parts[1].lower(),
            "memavail_pre_GiB": None, "memavail_post_GiB": None, "cpuset": parts[4], "delivered": NOT_MEASURED,
            "siblings_pre": NOT_MEASURED, "siblings_post": NOT_MEASURED,
            "log": (os.path.basename(logs[-1]) if logs else None), "source": "inspect_record",
            "field_sources": {"rc": "inspect.txt .State.ExitCode", "oomkilled": "inspect.txt .State.OOMKilled",
                              "cpuset": "inspect.txt HostConfig.CpusetCpus", "DIGEST": "inspect.txt 7th field (launcher's GOT_DIGEST)"},
            "infra_not_measured": list(FIELDS_INFRASTRUCTURE) + ["core_min"]}


# ================= G1: COMPLETION, ARM-KIND AWARE =====================================
def arm_datum(base, arm):
    d = os.path.join(base, arm)
    p = os.path.join(d, ".av2_age_datum")
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
            refuse("G1", {"arm": arm, "kernel_rc": kernel_rc, "oomkilled": oom, "note": "a run that fails any clause is not done (rule 4)"})
        adir, datum = arm_datum(base, arm)
        art = os.path.join(adir, ARTEFACT[arm])
        if not os.path.isfile(art):
            refuse("G1", {"artefact_absent": art, "arm": arm})
        if os.path.getmtime(art) <= datum:
            refuse("G1", {"artefact_not_newer_than_datum": art, "arm": arm, "datum": datum, "artefact_mtime": os.path.getmtime(art), "note": "age guard, rule 4"})
        kind = ARM_KIND[arm]
        if kind == "SOLVER":
            logname = r.get("log")
            logpath = os.path.join(base, logname) if logname else None
            if not logpath or not os.path.isfile(logpath):
                refuse("G1", {"log_absent": logname, "arm": arm, "note": "a missing log is a FAILED clause"})
            text = open(logpath, errors="replace").read()
            if TERMINAL[arm] not in text:
                refuse("G1", {"terminal_marker_absent": TERMINAL[arm], "arm": arm, "log": logname})
            if CONTROL_LINE not in text:
                refuse("CONTROL", {"instrument_planted_control_line_absent": CONTROL_LINE, "arm": arm, "log": logname})
            r["log_text"] = text
        else:
            text = open(art, errors="replace").read()
            if not re.search(r"^Mesh OK\.$", text, re.M):
                refuse("G1", {"mesh_ok_absent": art, "arm": arm})
            r["log_text"] = open(os.path.join(base, r["log"]), errors="replace").read() if r.get("log") and os.path.isfile(os.path.join(base, r["log"])) else ""
        out["arms"][arm] = {"kind": kind, "kernel_rc": kernel_rc, "oomkilled": oom, "artefact": ARTEFACT[arm], "source": r["source"], "field_sources": r["field_sources"]}
        if r.get("infra_not_measured"):
            out["not_measured"][arm] = r["infra_not_measured"]
    return out


# ================= readers with planted controls ======================================
def read_X(path):
    j = json.load(open(path))
    adj = {}
    for of in ("CD", "CL"):
        adj[of] = {dv: [float(v) for v in j["adjoint"][of][dv]] for dv in ("shape", "patchV")}
    return {"CD": float(j["CD_baseline"]), "CL": float(j["CL_baseline"]), "adjoint": adj,
            "so_md5": (j.get("identity") or {}).get("libidwarp_so_md5"), "nprocs": j.get("nprocs"),
            "gmresRelTol": (j.get("identity") or {}).get("gmresRelTol")}


def read_F(path):
    j = json.load(open(path))
    if j.get("components_requested") != COMPONENTS_REGISTERED:
        refuse("G-DP", {"components_requested_not_registered": j.get("components_requested"), "registered": COMPONENTS_REGISTERED})
    table = {}
    for row in j["rows"]:
        key = (row["dv"], int(row["idx"]))
        st = row.get("status")
        table[key] = {"status": st, "blocked": bool(row.get("blocked")), "error": row.get("error"),
                      "fwd_CD": (float(row["fwd_CD"]) if st in ("MEASURED", "NOT_A_RESULT_CONTROL") else None),
                      "fwd_CL": (float(row["fwd_CL"]) if st in ("MEASURED", "NOT_A_RESULT_CONTROL") else None),
                      "n_add_dvgeo": row.get("n_add_dvgeo")}
    return {"table": table, "CD": float(j["CD_baseline"]), "CL": float(j["CL_baseline"]),
            "so_md5": (j.get("identity") or {}).get("libidwarp_so_md5"), "blocked_any": bool(j.get("blocked_any")), "raw": j}


def forward_channel_control(F, tag):
    """v1.0a: a forward value exactly 0.0 (silent no-op), exactly 1.0 (seed echo) or within
    ECHO_TOL relative of the baseline function value (function echo) is REFUSED."""
    bad = []
    for key, row in F["table"].items():
        if row["status"] not in ("MEASURED", "NOT_A_RESULT_CONTROL"):
            continue
        for of, f0 in (("CD", F["CD"]), ("CL", F["CL"])):
            v = row["fwd_%s" % of]
            if v == 0.0:
                bad.append({"component": key, "of": of, "reason": "exactly_zero_silent_noop"})
            elif v == 1.0:
                bad.append({"component": key, "of": of, "reason": "seed_echo"})
            elif abs(v - f0) <= ECHO_TOL * abs(f0):
                bad.append({"component": key, "of": of, "reason": "function_echo", "value": v, "function": f0})
        if row["status"] == "NOT_A_RESULT_CONTROL":
            bad.append({"component": key, "reason": "instrument_marked_NOT_A_RESULT_CONTROL"})
    if bad:
        refuse("CONTROL", {"forward_channel_control_failed": bad, "row": tag})
    return {"forward_channel_controls_pass": True, "row": tag}


def grader_plant_control(base, xpath, tag):
    j = json.load(open(xpath))
    for of in ("CD", "CL"):
        for dv in ("shape", "patchV"):
            j["adjoint"][of][dv] = [repr(float(v) + PLANT) for v in j["adjoint"][of][dv]]
    cdir = os.path.join(base, "grader_controls")
    os.makedirs(cdir, exist_ok=True)
    cp = os.path.join(cdir, "X_%s_planted.json" % tag)
    json.dump(j, open(cp, "w"), indent=1, sort_keys=True)
    a, b = read_X(xpath), read_X(cp)
    worst, n = 0.0, 0
    for of in ("CD", "CL"):
        for dv in ("shape", "patchV"):
            for x, y in zip(a["adjoint"][of][dv], b["adjoint"][of][dv]):
                worst = max(worst, abs((y - x) - PLANT)); n += 1
    if n == 0 or worst > 1e-12:
        refuse("CONTROL", {"grader_plant_not_seen": {"n_values": n, "worst_residual": worst, "plant": PLANT}})
    return {"grader_plant_seen": True, "n_values": n, "worst_residual": worst, "file": cp}


def sign_flipped_copy(X):
    Y = json.loads(json.dumps(X))
    for of in ("CD", "CL"):
        for dv in ("shape", "patchV"):
            Y["adjoint"][of][dv] = [-v for v in Y["adjoint"][of][dv]]
    return Y


def silent_zero_copy(F):
    Y = json.loads(json.dumps({"table": {"%s|%d" % k: v for k, v in F["table"].items()}, "CD": F["CD"], "CL": F["CL"]}))
    T = {}
    for k, v in Y["table"].items():
        dv, idx = k.split("|")
        if v["status"] == "MEASURED":
            v["fwd_CD"] = 0.0; v["fwd_CL"] = 0.0
        T[(dv, int(idx))] = v
    return {"table": T, "CD": Y["CD"], "CL": Y["CL"], "so_md5": F["so_md5"], "blocked_any": F["blocked_any"], "raw": None}


# ================= G-DP: the bright line, per row =====================================
def grade_dp(X, F, of):
    comps, n_graded, n_blocked = [], 0, 0
    for dv, idx in COMPONENTS_REGISTERED:
        rev = X["adjoint"][of][dv][idx] if idx < len(X["adjoint"][of][dv]) else None
        row = F["table"].get((dv, idx))
        c = {"dv": dv, "idx": idx, "g_rev": rev}
        if row is None or rev is None:
            c.update({"verdict": "NOT A RESULT", "reason": "ABSENT"}); comps.append(c); continue
        if row["blocked"] or row["status"] == "BLOCKED":
            c.update({"verdict": "BLOCKED", "reason": row.get("error")}); n_blocked += 1; comps.append(c); continue
        if row["status"] != "MEASURED":
            c.update({"verdict": "NOT A RESULT", "reason": row["status"]}); comps.append(c); continue
        fwd = row["fwd_%s" % of]
        c["g_fwd"] = fwd
        den = max(abs(fwd), abs(rev))
        if den < NEAR_ZERO_ABS:
            c.update({"verdict": "NOT A RESULT", "reason": "NEAR_ZERO"}); comps.append(c); continue
        eps = abs(fwd - rev) / den
        c.update({"eps": eps, "band": DP_BAND, "sign_agree": bool(fwd * rev > 0.0)})
        c["verdict"] = "PASS" if eps <= DP_BAND else "GATE FAIL"
        n_graded += 1
        comps.append(c)
    out = {"objective": of, "components": comps, "n_graded": n_graded, "n_blocked": n_blocked,
           "n_pass": sum(1 for c in comps if c.get("verdict") == "PASS"),
           "n_gate_fail": sum(1 for c in comps if c.get("verdict") == "GATE FAIL"),
           "worst_eps": max([c["eps"] for c in comps if "eps" in c] or [None]) if n_graded else None}
    if n_blocked > 0:
        out.update({"verdict": "BLOCKED", "reason": "%d component(s) blocked in forward mode" % n_blocked}); return out
    if n_graded < MIN_GRADED:
        out.update({"verdict": "NOT A RESULT", "reason": "fewer than %d graded components" % MIN_GRADED}); return out
    out["verdict"] = "GATE FAIL" if out["n_gate_fail"] else "PASS"
    return out


def compose_row(g_cd, g_cl):
    if "BLOCKED" in (g_cd["verdict"], g_cl["verdict"]):
        return "BLOCKED"
    if "NOT A RESULT" in (g_cd["verdict"], g_cl["verdict"]):
        return "NOT A RESULT"
    if "GATE FAIL" in (g_cd["verdict"], g_cl["verdict"]):
        return "GATE FAIL"
    return "PASS"


# ================= G9 / G10 / G12 ======================================================
def g_toolchain(rows):
    out = {"per_arm": {}, "verdict": "PASS"}
    for arm in ARMS_REQUIRED:
        r = rows[arm]; row = ARM_ROW[arm]
        m = re.search(r"D4S_IDWARP_SO_MD5:\s*([0-9a-f]{32})", r.get("log_text", ""))
        printed = m.group(1) if m else None
        ok = (r.get("DIGEST") == IMG_DIGEST[row]) and (printed == SO_MD5[row])
        art_md5 = r.get("artefact_so_md5")
        if arm != "MESH":
            ok = ok and (art_md5 == SO_MD5[row])
        out["per_arm"][arm] = {"row": row, "digest": r.get("DIGEST"), "printed_so_md5": printed, "artefact_so_md5": art_md5, "ok": bool(ok)}
        if not ok:
            out["verdict"] = "GATE FAIL"
    return out


def g_caps(rows):
    out = {"per_arm": {}, "verdict": "PASS", "total_core_min": 0.0, "ceiling": ITEM_CEILING_CORE_MIN, "not_measured": []}
    for arm in ARMS_REQUIRED:
        r = rows[arm]; cm = r.get("core_min")
        if cm is None:
            out["not_measured"].append(arm); out["per_arm"][arm] = {"core_min": NOT_MEASURED, "cap": CAPS[arm]}; continue
        out["total_core_min"] += cm
        crossed = cm > CAPS[arm]
        out["per_arm"][arm] = {"core_min": cm, "cap": CAPS[arm], "crossed": crossed, "ratio_actual_over_predicted": round(cm / PREDICTED_CORE_MIN[arm], 4)}
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
        d = r.get("delivered"); dl = None
        m = re.match(r"\s*([\d.]+)\s+n=(\d+)", d or "")
        if m:
            dl = float(m.group(1))
        if dl is None:
            out["not_measured"].append(arm)
        out["per_arm"][arm] = {"cpuset": r.get("cpuset"), "delivered_cores_mean": (dl if dl is not None else NOT_MEASURED)}
        if not cs_ok:
            out["verdict"] = "GATE FAIL"
    return out


# ================= the grade ==========================================================
def grade(root):
    rows = read_ledger(os.path.join(root, "ledger.txt"))
    g1 = g_completion(root, rows)
    cm_txt = open(os.path.join(root, "MESH", "checkMesh.log"), errors="replace").read()
    m = re.search(r"^\s*cells:\s+(\d+)", cm_txt, re.M)
    if not m:
        refuse("G-M2", {"cells_absent_in_checkMesh": True})
    cells = int(m.group(1))
    gm2 = "PASS" if cells == CELLS_EXPECTED else "GATE FAIL"
    X = {"S": read_X(os.path.join(root, "X-S", "av2_X.json")), "P": read_X(os.path.join(root, "X-P", "av2_X.json"))}
    F = {"S": read_F(os.path.join(root, "FAD-S", "av2_FAD.json")), "P": read_F(os.path.join(root, "FAD-P", "av2_FAD.json"))}
    rows["X-S"]["artefact_so_md5"] = X["S"]["so_md5"]; rows["X-P"]["artefact_so_md5"] = X["P"]["so_md5"]
    rows["FAD-S"]["artefact_so_md5"] = F["S"]["so_md5"]; rows["FAD-P"]["artefact_so_md5"] = F["P"]["so_md5"]
    for rk in ("S", "P"):
        if X[rk]["gmresRelTol"] != GMRES_REL_TOL_REGISTERED:
            refuse("G-DP", {"gmresRelTol_in_artefact": X[rk]["gmresRelTol"], "registered": GMRES_REL_TOL_REGISTERED, "row": rk,
                            "note": "the band is 10 x the adjoint solve tolerance; a different tolerance is a different band"})
    controls = {"forward_channel_S": forward_channel_control(F["S"], "S"), "forward_channel_P": forward_channel_control(F["P"], "P"),
                "grader_plant_XS": grader_plant_control(root, os.path.join(root, "X-S", "av2_X.json"), "XS")}
    # (iii) the deliberately wrong transpose: sign-flipped reverse totals against the real forward values
    if not F["S"]["blocked_any"]:
        wrong = grade_dp(sign_flipped_copy(X["S"]), F["S"], "CD")
        if wrong["verdict"] != "GATE FAIL" or wrong["n_gate_fail"] != wrong["n_graded"] or wrong["n_graded"] < MIN_GRADED:
            refuse("CONTROL", {"sign_flipped_transpose_not_read_as_wrong": {"verdict": wrong["verdict"], "n_gate_fail": wrong["n_gate_fail"], "n_graded": wrong["n_graded"]}})
        controls["sign_flipped_XS_read_as_GATE_FAIL"] = {"seen": True, "n_gate_fail": wrong["n_gate_fail"]}
        # (iv) the silent no-op: every forward value 0.0 must be REFUSED by the channel control
        try:
            forward_channel_control(silent_zero_copy(F["S"]), "S_silent_zero_plant")
            refuse("CONTROL", {"silent_zero_plant_not_refused": True})
        except Refusal as e:
            if "silent_zero_plant_not_refused" in str(e):
                raise
            controls["silent_zero_FADS_refused"] = {"seen": True}
    else:
        controls["sign_flipped_XS_read_as_GATE_FAIL"] = {"seen": False, "note": "FAD-S blocked; the transpose control has nothing to read"}
        controls["silent_zero_FADS_refused"] = {"seen": False, "note": "FAD-S blocked"}
    gdp = {}
    for rk in ("S", "P"):
        cd = grade_dp(X[rk], F[rk], "CD"); cl = grade_dp(X[rk], F[rk], "CL")
        gdp[rk] = {"G-DP_CD": cd, "G-DP_CL": cl, "row_verdict": compose_row(cd, cl), "CD_baseline": X[rk]["CD"], "CL_baseline": X[rk]["CL"]}
    div = []
    for dv, idx in COMPONENTS_REGISTERED:
        a, b = X["S"]["adjoint"]["CD"][dv], X["P"]["adjoint"]["CD"][dv]
        if idx < len(a) and idx < len(b):
            den = max(abs(a[idx]), abs(b[idx]), 1e-300)
            div.append({"dv": dv, "idx": idx, "J_rev_shipped": a[idx], "J_rev_patched": b[idx], "divergence_pct": abs(a[idx] - b[idx]) / den * 100.0})
    g9, g10, g12 = g_toolchain(rows), g_caps(rows), g_placement(rows)
    # ---- predictions, scored never adjusted
    preds = {"P1_patched_row_PASS": "HIT" if gdp["P"]["row_verdict"] == "PASS" else ("NOT_MEASURED" if gdp["P"]["row_verdict"] == "BLOCKED" else "MISS")}
    s6 = [c for c in gdp["S"]["G-DP_CD"]["components"] if c["dv"] == "shape" and c["idx"] == 6]
    s6v = s6[0].get("verdict") if s6 else None
    others_in = sum(1 for c in gdp["S"]["G-DP_CD"]["components"] if not (c["dv"] == "shape" and c["idx"] == 6) and c.get("verdict") == "PASS")
    preds["P2_shipped_shape6_GATE_FAIL_others_ge3_PASS"] = ("HIT" if (s6v == "GATE FAIL" and others_in >= 3) else ("NOT_MEASURED" if s6v in ("BLOCKED", "NOT A RESULT", None) else "MISS"))
    preds["P2_shipped_shape6_eps"] = (s6[0].get("eps") if s6 else None)
    wp = gdp["P"]["G-DP_CD"]["worst_eps"]
    preds["P3_patched_worst_eps_le_1e-6"] = "NOT_MEASURED" if wp is None else ("HIT" if wp <= 1.0e-6 else "MISS")
    preds["P3_patched_worst_eps"] = wp
    preds["P4_forward_channel_controls_pass_both_rows"] = "HIT"   # reaching here means neither refused
    cx, cf = rows["X-S"].get("core_min"), rows["FAD-S"].get("core_min")
    preds["P5_fad_over_x_cost_ratio_shipped"] = NOT_MEASURED if (cx is None or cf is None or cx <= 0) else ("HIT" if PRED["P5_fad_over_x_band"][0] <= cf / cx <= PRED["P5_fad_over_x_band"][1] else "MISS")
    tot = g10["total_core_min"]
    preds["P5_total_core_min_band"] = NOT_MEASURED if g10["not_measured"] else ("HIT" if PRED["P5_core_min_band"][0] <= tot <= PRED["P5_core_min_band"][1] else "MISS")
    mw = rows["MESH"].get("wall_s")
    preds["P6_mesh_wall_le_120s"] = NOT_MEASURED if mw is None else ("HIT" if mw <= PRED["P6_mesh_wall_s_max"] else "MISS")
    preds["P7_cells_4032"] = "HIT" if gm2 == "PASS" else "MISS"
    rv = (gdp["S"]["row_verdict"], gdp["P"]["row_verdict"])
    if "BLOCKED" in rv:
        verdict = "BLOCKED"
    elif "NOT A RESULT" in rv:
        verdict = "NOT A RESULT"
    elif "GATE FAIL" in rv + (gm2, g9["verdict"], g10["verdict"], g12["verdict"]):
        verdict = "GATE FAIL"
    else:
        verdict = "PASS"
    if verdict not in VOCAB:
        refuse("VOCAB", {"verdict": verdict})
    return {"item": "CURRICULUM-%s" % ITEM, "verdict": verdict,
            "rows": {"SHIPPED": gdp["S"]["row_verdict"], "PATCHED": gdp["P"]["row_verdict"]},
            "gates": {"G1_completion": "PASS", "G-M2_mesh_identity": gm2, "G-DP_SHIPPED": gdp["S"], "G-DP_PATCHED": gdp["P"],
                      "G9_toolchain": g9, "G10_caps": g10, "G12_placement": g12},
            "bands": {"eps_per_component": DP_BAND, "gmresRelTol_registered": GMRES_REL_TOL_REGISTERED, "near_zero": NEAR_ZERO_ABS,
                      "provenance": "ADJOINT_VERIFICATION_STANDARD.md sec.2 (10 x gmresRelTol); v1.0a forward-channel controls"},
            "mesh_cells": cells, "divergence_rev_shipped_vs_patched_CD": div, "predictions": preds, "controls": controls, "completion": g1,
            "not_measured": {"G1": g1["not_measured"], "G10": g10["not_measured"], "G12": g12["not_measured"]},
            "field_classes": {"physics": list(FIELDS_PHYSICS), "infrastructure": list(FIELDS_INFRASTRUCTURE),
                              "rule": "absent infrastructure -> NOT_MEASURED beside the verdict; absent physics -> REFUSE (L-342)"},
            "no_gci": "no grid family; standing rule 5 has no row; NO GCI IS QUOTED",
            "no_fd": "this rung carries no FD table; its reference is forward-mode AD (the exact tangent), standard sec.2",
            "capability_grid_cell": "2D . steady . incompressible -- dot-product/duality evidence for the gradient column's 'what was checked'; the census line's 'never performed' moves only on a graded row"}


# ================= selftest: planted fixtures, counted against a FROZEN unit count ======
ROWFMT = ("ARM={arm} ROW={row} IMG={img} DIGEST={dig} rc={rc} wall_s={wall} ranks=1 core_min={cm} "
          "cap_core_min={cap} enforced_wall_s=600 enforced_core_min={cap} memory=4g inspect(exit,oomkilled)=[{ke} {oom}] "
          "memavail_pre_GiB=20.00 memavail_post_GiB={mpost} cpuset={cs} delivered_cores_mean=[{dl}] "
          "siblings_pre=[] siblings_post=[] log={log} stamp=x\n")
J0 = {"shape": [-0.011, 0.02, -0.03, 0.041, 0.05, -0.06, 0.007, -0.008], "patchV": [0.0, 0.0123]}


def _fix(tmp, tweak=None):
    k = {"rc": {a: 0 for a in ARMS_REQUIRED}, "ke": {}, "oom": {a: "false" for a in ARMS_REQUIRED},
         "cm": dict(PREDICTED_CORE_MIN), "cs": {a: CPUSET_REGISTERED for a in ARMS_REQUIRED},
         "so": {a: SO_MD5[ARM_ROW[a]] for a in ARMS_REQUIRED}, "cells": CELLS_EXPECTED,
         "eps": {"S": {}, "P": {}}, "flip": {"S": set(), "P": set()}, "blocked": {"S": set(), "P": set()},
         "zero": {"S": set(), "P": set()}, "echo": {"S": set(), "P": set()}, "seed": {"S": set(), "P": set()},
         "terminal": {a: True for a in ARMS_REQUIRED}, "ctrl_line": {a: True for a in ARMS_REQUIRED}, "stale": set(),
         "mpost": "20.00", "drop_row": set(), "inspect_file": set(), "dl": "0.99 n=10 max_nr_throttled=0",
         "gmres": 1.0e-6, "wall": {a: 60 for a in ARMS_REQUIRED}, "CD": 0.02, "CL": 0.5}
    if tweak:
        tweak(k)
    root = os.path.join(tmp, "root_%d" % int(time.time() * 1e6))
    os.makedirs(root)
    led = ["ITEM=AV2\n", "STAGED stamp=x\n"]
    for arm in ARMS_REQUIRED:
        d = os.path.join(root, arm)
        os.makedirs(os.path.join(d, "0.orig" if arm == "MESH" else "0"))
        ref = os.path.join(d, DATUM_REF[arm]); open(ref, "w").write("U\n")
        t0 = int(os.path.getmtime(ref)); open(os.path.join(d, ".av2_age_datum"), "w").write("%d\n" % t0)
        log = "%s_x.log" % arm; so = k["so"][arm]
        text = "D4S_CONTAINER_UID: 0\nD4S_IDWARP_SO_MD5: %s\nD4S_DEADLINE_IN_CONTAINER_S: 600\n" % so
        if arm == "MESH":
            art = os.path.join(d, "checkMesh.log")
            open(art, "w").write("Mesh stats\n    cells:            %d\n\nMesh OK.\n" % k["cells"])
        else:
            rk = "S" if arm.endswith("-S") else "P"
            art = os.path.join(d, ARTEFACT[arm])
            ident = {"libidwarp_so_md5": so, "idwarp_file": "/x/idwarp/__init__.py", "gmresRelTol": k["gmres"]}
            if arm.startswith("X"):
                adj = {"CD": {dv: [repr(v) for v in J0[dv]] for dv in J0}, "CL": {dv: [repr(v * 10.0) for v in J0[dv]] for dv in J0}}
                json.dump({"item": "AV2", "mode": "X", "identity": ident, "nprocs": 1, "CD_baseline": repr(k["CD"]), "CL_baseline": repr(k["CL"]), "adjoint": adj, "plant": PLANT}, open(art, "w"))
            else:
                rows_ = []
                for dv, idx in COMPONENTS_REGISTERED:
                    rev = J0[dv][idx]
                    e = k["eps"][rk].get((dv, idx), 1.0e-7)
                    fcd = rev * (1.0 + e); fcl = rev * 10.0 * (1.0 + e)
                    if (dv, idx) in k["flip"][rk]:
                        fcd, fcl = -fcd, -fcl
                    if (dv, idx) in k["zero"][rk]:
                        fcd, fcl = 0.0, 0.0
                    if (dv, idx) in k["seed"][rk]:
                        fcd, fcl = 1.0, 1.0
                    if (dv, idx) in k["echo"][rk]:
                        fcd, fcl = k["CD"], k["CL"]
                    if (dv, idx) in k["blocked"][rk]:
                        rows_.append({"dv": dv, "idx": idx, "status": "BLOCKED", "blocked": True, "error": "RuntimeError('no add_dvgeo')"})
                    else:
                        rows_.append({"dv": dv, "idx": idx, "status": "MEASURED", "fwd_CD": repr(fcd), "fwd_CL": repr(fcl), "n_add_dvgeo": 1,
                                      "controls": {"nonzero": True, "not_seed_echo": True, "not_function_echo": True}})
                json.dump({"item": "AV2", "mode": "FAD", "identity": ident, "nprocs": 1, "components_requested": COMPONENTS_REGISTERED,
                           "CD_baseline": repr(k["CD"]), "CL_baseline": repr(k["CL"]), "rows": rows_, "blocked_any": bool(k["blocked"][rk]), "plant": PLANT}, open(art, "w"))
            if k["ctrl_line"][arm]:
                text += CONTROL_LINE + " n=10 worst_residual=0.0 plant=0.001234\n"
            if k["terminal"][arm]:
                text += TERMINAL[arm] + " ok\n"
        os.utime(art, (t0 - 5, t0 - 5) if arm in k["stale"] else (t0 + 5, t0 + 5))
        open(os.path.join(root, log), "w").write(text)
        ke = k["ke"].get(arm, k["rc"][arm])
        if arm in k["inspect_file"]:
            open(os.path.join(root, "%s_x.inspect.txt" % arm), "w").write("%d %s 2026-08-26T00:00:00Z 2026-08-26T00:01:00Z %s 4294967296 %s\n" % (ke, k["oom"][arm], k["cs"][arm], IMG_DIGEST[ARM_ROW[arm]]))
        if arm in k["drop_row"]:
            continue
        led.append(ROWFMT.format(arm=arm, row=ARM_ROW[arm], img="img", dig=IMG_DIGEST[ARM_ROW[arm]], rc=k["rc"][arm], wall=k["wall"][arm],
                                 cm=k["cm"][arm], cap=CAPS[arm], ke=ke, oom=k["oom"][arm], mpost=k["mpost"], cs=k["cs"][arm], dl=k["dl"], log=log))
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
    unit("U1 clean fixture (eps 1e-7) -> item PASS, both rows PASS, G-M2/G9/G10/G12 PASS",
         r["verdict"] == "PASS" and r["rows"] == {"SHIPPED": "PASS", "PATCHED": "PASS"} and r["gates"]["G-M2_mesh_identity"] == "PASS"
         and r["gates"]["G9_toolchain"]["verdict"] == "PASS" and r["gates"]["G10_caps"]["verdict"] == "PASS" and r["gates"]["G12_placement"]["verdict"] == "PASS")
    unit("U2 clean fixture -> P1, P3, P4, P5, P6, P7 HIT; P2 MISS (shipped shape[6] clean by construction)",
         all(r["predictions"][x] == "HIT" for x in ("P1_patched_row_PASS", "P3_patched_worst_eps_le_1e-6", "P4_forward_channel_controls_pass_both_rows",
                                                    "P5_fad_over_x_cost_ratio_shipped", "P5_total_core_min_band", "P6_mesh_wall_le_120s", "P7_cells_4032"))
         and r["predictions"]["P2_shipped_shape6_GATE_FAIL_others_ge3_PASS"] == "MISS")
    unit("U3 grader plant SEEN; sign-flipped X-S read as GATE FAIL on 5/5; silent-zero FAD-S plant REFUSED (rule 3 x3)",
         r["controls"]["grader_plant_XS"]["grader_plant_seen"] and r["controls"]["sign_flipped_XS_read_as_GATE_FAIL"]["n_gate_fail"] == 5
         and r["controls"]["silent_zero_FADS_refused"]["seen"])
    r = grade(_fix(tmp, tw(eps={"S": {("shape", 6): 0.8}})))
    unit("U4 PLANTED eps 0.8 on shipped shape[6] -> component GATE FAIL, SHIPPED row GATE FAIL, item GATE FAIL, P2 HIT",
         r["rows"]["SHIPPED"] == "GATE FAIL" and r["verdict"] == "GATE FAIL" and r["predictions"]["P2_shipped_shape6_GATE_FAIL_others_ge3_PASS"] == "HIT" and r["rows"]["PATCHED"] == "PASS")
    r = grade(_fix(tmp, tw(eps={"P": {("shape", 3): 2.0e-5}})))
    unit("U5 PLANTED eps 2e-5 on patched shape[3] (> 1e-5) -> PATCHED GATE FAIL, P1 MISS", r["rows"]["PATCHED"] == "GATE FAIL" and r["predictions"]["P1_patched_row_PASS"] == "MISS")
    r = grade(_fix(tmp, tw(eps={"P": {("shape", 3): 8.0e-6}})))
    unit("U6 eps 8e-6 (inside 1e-5, outside P3's 1e-6) -> PASS, P3 MISS", r["rows"]["PATCHED"] == "PASS" and r["predictions"]["P3_patched_worst_eps_le_1e-6"] == "MISS")
    r = grade(_fix(tmp, tw(flip={"P": {("patchV", 1)}})))
    unit("U7 PLANTED sign flip on patched patchV[1] -> eps 2 -> GATE FAIL", r["rows"]["PATCHED"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(blocked={"P": {("shape", 0), ("shape", 3), ("shape", 6), ("shape", 7)}})))
    unit("U8 four shape components BLOCKED in forward mode on PATCHED (no add_dvgeo) -> row BLOCKED, item BLOCKED, P1 NOT_MEASURED",
         r["rows"]["PATCHED"] == "BLOCKED" and r["verdict"] == "BLOCKED" and r["predictions"]["P1_patched_row_PASS"] == "NOT_MEASURED")
    r = grade(_fix(tmp, tw(blocked={"S": {("shape", 6)}})))
    unit("U9 one component BLOCKED on SHIPPED -> row BLOCKED, transpose/silent controls reported as not readable, item BLOCKED",
         r["rows"]["SHIPPED"] == "BLOCKED" and r["verdict"] == "BLOCKED" and not r["controls"]["sign_flipped_XS_read_as_GATE_FAIL"]["seen"])
    unit("U10 forward value exactly 0.0 on one shipped component (silent no-op) -> REFUSAL (v1.0a)", refused(_fix(tmp, tw(zero={"S": {("shape", 0)}}))))
    unit("U11 forward value exactly 1.0 (seed echo) -> REFUSAL", refused(_fix(tmp, tw(seed={"P": {("shape", 7)}}))))
    unit("U12 forward value equal to the function value (function echo) -> REFUSAL", refused(_fix(tmp, tw(echo={"S": {("patchV", 1)}}))))
    unit("U13 gmresRelTol 1e-5 in the artefact (band is 10 x tolerance) -> REFUSAL", refused(_fix(tmp, tw(gmres=1.0e-5))))
    unit("U14 rc=1 on FAD-P -> REFUSAL", refused(_fix(tmp, tw(rc={"FAD-P": 1}, ke={"FAD-P": 1}))))
    unit("U15 OOMKilled=true on X-S -> REFUSAL", refused(_fix(tmp, tw(oom={"X-S": "true"}))))
    unit("U16 terminal marker absent in FAD-S log -> REFUSAL", refused(_fix(tmp, tw(terminal={"FAD-S": False}))))
    unit("U17 planted-control line absent in X-P log -> REFUSAL", refused(_fix(tmp, tw(ctrl_line={"X-P": False}))))
    unit("U18 artefact OLDER than the age datum (X-S) -> REFUSAL (rule 4)", refused(_fix(tmp, tw(stale={"X-S"}))))
    r = grade(_fix(tmp, tw(so={"FAD-P": SO_MD5["SHIPPED"]})))
    unit("U19 FAD-P carrying the SHIPPED .so md5 -> G9 GATE FAIL, item GATE FAIL", r["gates"]["G9_toolchain"]["verdict"] == "GATE FAIL" and r["verdict"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(cm={"FAD-S": 26.0})))
    unit("U20 FAD-S core_min 26.0 > cap 25.0 -> G10 GATE FAIL", r["gates"]["G10_caps"]["verdict"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(cs={"X-P": "4,14"})))
    unit("U21 X-P on cpuset 4,14 -> G12 GATE FAIL", r["gates"]["G12_placement"]["verdict"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(cells=4033)))
    unit("U22 cells 4033 -> G-M2 GATE FAIL, P7 MISS", r["gates"]["G-M2_mesh_identity"] == "GATE FAIL" and r["predictions"]["P7_cells_4032"] == "MISS")
    r = grade(_fix(tmp, tw(mpost="NOT_MEASURED", dl="NOT_MEASURED")))
    unit("U23 absent infrastructure fields -> verdict unchanged PASS, NOT_MEASURED named beside it (L-342)", r["verdict"] == "PASS" and r["not_measured"]["G1"].get("X-S") and "X-S" in r["not_measured"]["G12"])
    r = grade(_fix(tmp, tw(drop_row={"FAD-P"}, inspect_file={"FAD-P"})))
    unit("U24 ledger row absent, ONE inspect record -> read from it, source named, core_min NOT_MEASURED, verdict PASS",
         r["verdict"] == "PASS" and r["completion"]["arms"]["FAD-P"]["source"] == "inspect_record" and "FAD-P" in r["not_measured"]["G10"])
    here = os.path.dirname(os.path.abspath(__file__))
    p = os.path.join(tmp, "planted_assert.py"); open(p, "w").write("x = 1\nassert x == 1\n")
    unit("U25 ast.Assert count = 0 in av2_grade.py and av2_xf.py, and the counter sees a planted assert (=1)",
         count_asserts(os.path.abspath(__file__)) == 0 and count_asserts(os.path.join(here, "av2_xf.py")) == 0 and count_asserts(p) == 1)
    print("AV2 GRADER SELFTEST units=%d expected=%d failures=%d python_O=%s" % (n, EXPECTED_UNITS, len(fails), not __debug__))
    if n != EXPECTED_UNITS or fails:
        print("SELFTEST FAIL: %s" % (fails or "unit count %d != %d" % (n, EXPECTED_UNITS)))
        return 2
    print("AV2 GRADER SELFTEST PASS %d/%d (counted against the frozen EXPECTED_UNITS)" % (n, EXPECTED_UNITS))
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
        d = os.path.join(a.tmpdir, "av2_selftest_%d" % os.getpid()); os.makedirs(d, exist_ok=True)
        return selftest(d)
    if not a.root:
        print("usage: av2_grade.py --root <run root> [--out FILE] | --selftest"); return 64
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
