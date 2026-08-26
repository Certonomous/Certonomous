#!/usr/bin/env python3
"""Curriculum D6 grader -- multipoint cruise (CL 0.4/0.5/0.6, w = 0.25/0.50/0.25)
on D4's case.  FROZEN by md5 in PREREGISTRATION.md section 8 before any
container starts.  DERIVED from curriculum_D5/d5_grade.py (the D4-SHIPPED
Addendum-2 field classes, kernel-record fallback, positional terminal clause and
Addendum-2b arm kinds) with D6's gates in place of D5's.

WHAT IT GRADES (PREREGISTRATION.md sections 3 and 5):
  G1      completion, ARM-KIND AWARE.  SOLVER arms (O_mp, F_mp): kernel rc == 0,
          OOMKilled false, POSITIONAL terminal statement, age guard on the
          registered artefacts.  SCRIPT arms (ACC_mp, REF_off): kernel rc == 0,
          the launcher's .ok marker, the registered artefact newer than the arm's
          own datum.  REF_off's staged input OptView.hst (D4's history) must carry
          the registered md5 -- a staged input, exempt from the age guard BY MD5
          (the D7FR H4 form), never by name alone.
  G-D6-1  per point: CD_i(mp) <= CD_i(REF_off) -> PASS for that point, else GATE
          FAIL for that point.  THREE verdicts, always all three reported.
  G-D6-2  composite: (J_0 - J_f)/J_0 in [15, 40] % -> PASS else GATE FAIL.
  G-D6-3  single-point price: CD_0.5(mp) - CD_f(D4) in [0, 1.0e-3] -> PASS;
          > 1.0e-3 -> GATE FAIL; NEGATIVE -> NOT A RESULT pending triage (a
          finding about D4, not about D6).  CD_f(D4) is RE-READ from D4's O/
          opt_IPOPT.txt (read-only) through a reader with a PLANTED control.
  G-D6-4  bright line on J: per-component and aggregate FD error <= 5 %, sign
          flips named per component; >= 2 flips -> NOT A RESULT (pathology).
  G9/G10/G12  toolchain (PATCHED digest + libidwarp md5), caps (report mode,
          GATE FAIL on a crossing as the frozen text says), placement (cpuset
          2,3,4,14; delivered >= 3.0 where measured).
L-342 field classes as D5; L-332: no assert anywhere, AST-counted.
"""
import ast
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import time

BASE = "/home/ubuntu/certonomous-runs/CURRICULUM-D6-a2-wing-multipoint"
D4_O_DIR = "/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/O"   # READ-ONLY
CD_F_D4_RECORDED = 2.1125978108239574e-02
MD5_D4_HST = "0d956d6ccbc010402915710f662d3b11"      # D4 O/OptView.hst, staged into REF_off/
ARMS_REQUIRED = ["O_mp", "ACC_mp", "F_mp", "REF_off"]
ARM_KIND = {"O_mp": "SOLVER", "F_mp": "SOLVER", "ACC_mp": "SCRIPT", "REF_off": "SCRIPT"}
ARM_DIR = {"O_mp": "O_mp", "ACC_mp": "ACC_mp", "F_mp": "O_mp", "REF_off": "REF_off"}
SOLVER_ARTEFACTS = {"O_mp": ["opt_IPOPT.txt", "OptView.hst"],
                    "F_mp": ["d6_fd_endpoint.json", "d6_endpoint_dvs.json", "d6_major_history.json"]}
SCRIPT_ARTEFACTS = {"ACC_mp": [], "REF_off": ["d6_ref_off.json"]}
CAPS = {"O_mp": 2000.0, "ACC_mp": 30.0, "F_mp": 180.0, "REF_off": 20.0}
ITEM_CEILING_CORE_MIN = 2230.0
PREDICTED_CORE_MIN = {"O_mp": 1533.4, "ACC_mp": 9.0, "F_mp": 141.8, "REF_off": 10.5}
POINTS = ["cl04", "cl05", "cl06"]
WEIGHTS = {"cl04": 0.25, "cl05": 0.50, "cl06": 0.25}
REDUCTION_BAND_PCT = (15.0, 40.0)     # G-D6-2
PRICE_BAND = (0.0, 1.0e-3)            # G-D6-3
SIGN_FLIP_PATHOLOGY_N = 2
FD_BAND_PCT = 5.0
PLATEAU_TOL_PCT = 10.0
COMPONENTS_REGISTERED = [["shape", 46], ["shape", 18], ["shape", 0], ["twist", 0], ["patchV_cl05", 1]]
IMG_PATCHED_DIGEST = "sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35"
IDWARP_SO_MD5_PATCHED = "85f59e87253e0a71a813f64ca6e4c425"
RANKS = 4
CPUSET_REGISTERED = "2,3,4,14"
DELIVERED_CORES_FLOOR = 3.0
TERMINAL_STATEMENT = "Finalising parallel run"
FIELDS_PHYSICS = ("rc", "inspect_exit", "oomkilled", "terminal_statement", "age_guard", "wall_s",
                  "core_min", "cap_core_min", "enforced_core_min", "DIGEST", "cpuset")
FIELDS_INFRASTRUCTURE = ("memavail_pre_GiB", "memavail_post_GiB", "delivered", "siblings_pre",
                         "siblings_post", "cpu_series", "log")
NOT_MEASURED = "NOT_MEASURED"
KERNEL_RECORD_NAME_PREFIX = "d6_%s_"
PLANT = 1.234e-03
PREDICTIONS_MAJORS = (60, 100)
P5_BAND = (1200.0, 2000.0)
VOCAB = {"PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"}


class Refuse(Exception):
    pass


def refuse(where, detail):
    msg = json.dumps({"REFUSE": where, "detail": detail}, sort_keys=True, default=str)
    sys.stderr.write("D6_GRADE REFUSE " + msg + "\n")
    raise Refuse(msg)


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def count_asserts(source_text):
    return sum(1 for n in ast.walk(ast.parse(source_text)) if isinstance(n, ast.Assert))


def self_assert_check():
    n = count_asserts(open(__file__).read())
    if n != 0:
        refuse("L-332", {"assert_nodes_in_own_source": n})
    planted = count_asserts("x = 1\nassert x == 1\n")
    if planted != 1:
        refuse("L-332", {"assert_counter_blind": planted})
    return {"assert_nodes": n, "counter_sees_planted": planted}


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
    rows = []
    for line in open(path, errors="replace"):
        if not line.startswith("ARM="):
            continue
        m = LEDGER_RE.search(line)
        if not m:
            refuse("ledger", {"row_unparseable": line.strip()[:300],
                              "note": "an ARM= line that does not parse is PRESENT-BUT-GARBAGE: "
                                      "refused, never skipped (absent != garbage)"})
        g = m.groupdict()
        parts = g["inspect"].split()
        infra_nm = [k for k, v in (("memavail_pre_GiB", g["mempre"]), ("memavail_post_GiB", g["mempost"]),
                                   ("delivered", g["delivered"]), ("siblings_pre", g["sibpre"]),
                                   ("siblings_post", g["sibpost"]), ("log", g["log"]))
                    if v is None or NOT_MEASURED in str(v)]
        rows.append({"ARM": g["ARM"], "ROW": g["ROW"], "IMG": g["IMG"], "DIGEST": g["DIGEST"],
                     "rc": int(g["rc"]), "wall_s": int(g["wall_s"]), "ranks": int(g["ranks"]),
                     "core_min": float(g["core_min"]), "cap_core_min": float(g["cap"]),
                     "enforced_core_min": float(g["ecore"]), "memory": g["mem"],
                     "inspect_exit": (parts[0] if parts else None),
                     "oomkilled": (parts[1] if len(parts) > 1 else None),
                     "memavail_pre_GiB": _infra_float(g["mempre"]),
                     "memavail_post_GiB": _infra_float(g["mempost"]),
                     "cpuset": g["cpuset"], "delivered": g["delivered"],
                     "siblings_pre": g["sibpre"], "siblings_post": g["sibpost"],
                     "log": g["log"], "source": "ledger_row", "field_sources": {"all": "ledger_row"},
                     "infra_not_measured": infra_nm})
    return rows


def docker_ps_a_names(prefix):
    r = subprocess.run(["sudo", "-n", "docker", "ps", "-a", "--format", "{{.Names}}"],
                       capture_output=True, text=True)
    return [n for n in r.stdout.split() if n.startswith(prefix)]


def docker_inspect(name):
    r = subprocess.run(["sudo", "-n", "docker", "inspect", name], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    return json.loads(r.stdout)[0]


def docker_logs(name):
    r = subprocess.run(["sudo", "-n", "docker", "logs", name], capture_output=True, text=True,
                       stderr=subprocess.STDOUT)
    return r.stdout


def parse_docker_ts(s):
    s = s.split(".")[0].rstrip("Z")
    return int(time.mktime(time.strptime(s, "%Y-%m-%dT%H:%M:%S"))) - time.timezone


def kernel_record_row(arm, name, insp, log_text, registered_cap):
    st = insp.get("State", {})
    if st.get("Running"):
        refuse("G1", {"kernel_record_container_running": name})
    started, finished = st.get("StartedAt"), st.get("FinishedAt")
    if not started or not finished or finished.startswith("0001"):
        refuse("G1", {"kernel_record_timestamps_absent": name})
    wall = parse_docker_ts(finished) - parse_docker_ts(started)
    if wall < 0:
        refuse("G1", {"kernel_record_negative_wall": name})
    hc = insp.get("HostConfig", {})
    m = re.search(r"(sha256:[0-9a-f]{64})", json.dumps(insp.get("Image", "")))
    return {"ARM": arm, "ROW": "PATCHED", "IMG": insp.get("Config", {}).get("Image"),
            "DIGEST": (m.group(1) if m else None), "rc": int(st.get("ExitCode", -1)),
            "inspect_exit": str(st.get("ExitCode")), "oomkilled": str(st.get("OOMKilled")).lower(),
            "wall_s": wall, "ranks": RANKS, "core_min": round(wall * RANKS / 60.0, 3),
            "cap_core_min": registered_cap, "enforced_core_min": registered_cap,
            "memory": str(hc.get("Memory")), "cpuset": hc.get("CpusetCpus"),
            "memavail_pre_GiB": None, "memavail_post_GiB": None, "delivered": NOT_MEASURED,
            "siblings_pre": NOT_MEASURED, "siblings_post": NOT_MEASURED, "log": None,
            "log_text": log_text, "container": name, "source": "kernel_record",
            "field_sources": {"rc": "docker inspect .State.ExitCode",
                              "oomkilled": "docker inspect .State.OOMKilled",
                              "wall_s": "docker inspect StartedAt/FinishedAt",
                              "cpuset": "docker inspect HostConfig.CpusetCpus",
                              "terminal_statement": "docker logs (stream order)"},
            "infra_not_measured": list(FIELDS_INFRASTRUCTURE)}


def kernel_record_fallback(arm):
    names = docker_ps_a_names(KERNEL_RECORD_NAME_PREFIX % arm)
    if len(names) != 1:
        refuse("G1", {"arm_absent_from_ledger": arm, "kernel_record_candidates": names,
                      "note": "exactly one surviving container may stand in; zero or several refuse"})
    insp = docker_inspect(names[0])
    if insp is None:
        refuse("G1", {"kernel_record_inspect_failed": names[0]})
    return kernel_record_row(arm, names[0], insp, docker_logs(names[0]), CAPS[arm])


def terminal_statement_ok_text(text, where):
    lines = [l.rstrip() for l in text.splitlines() if l.strip()]
    if not lines:
        return False, {"log": where, "empty": True}
    last = lines[-1]
    return (last.strip() == TERMINAL_STATEMENT,
            {"log": where, "last_line": last[:200], "n_occurrences_anywhere": text.count(TERMINAL_STATEMENT),
             "positional": True})


def terminal_statement_ok(path):
    if not os.path.isfile(path):
        return False, {"log": path, "absent": True, "note": "a missing log is a FAILED clause"}
    return terminal_statement_ok_text(open(path, errors="replace").read(), path)


def arm_datum(base, arm):
    d = os.path.join(base, ARM_DIR[arm])
    p = os.path.join(d, ".d4_age_datum")
    if not os.path.isfile(p):
        refuse("G1", {"age_datum_absent": p, "arm": arm})
    datum = int(open(p).read().strip())
    ref = os.path.join(d, "0", "U")
    if not os.path.isfile(ref):
        refuse("G1", {"age_reference_absent": ref})
    if int(os.path.getmtime(ref)) != datum:
        refuse("G1", {"age_reference_moved": ref, "recorded": datum, "on_disk": int(os.path.getmtime(ref))})
    return d, datum


def g_completion(base, rows_by_arm, arms_required):
    out = {"arms_required": arms_required, "arms": {}, "rc_failures": [], "terminal_failures": [],
           "age_failures": [], "not_measured": {}, "staged_inputs": {}}
    for arm in arms_required:
        r = rows_by_arm.get(arm)
        if r is None:
            r = kernel_record_fallback(arm)
            rows_by_arm[arm] = r
        kind = ARM_KIND.get(arm)
        if kind is None:
            refuse("G1", {"arm_kind_unregistered": arm, "registered": sorted(ARM_KIND)})
        ke = r.get("inspect_exit")
        if ke is None:
            refuse("G1", {"kernel_exit_absent": arm})
        try:
            kernel_rc = int(ke)
        except (TypeError, ValueError):
            refuse("G1", {"kernel_exit_unparseable": arm, "value": ke})
        if kernel_rc != r["rc"]:
            refuse("G1", {"rc_disagreement": arm, "kernel": kernel_rc, "harness": r["rc"]})
        oom = str(r.get("oomkilled")).lower()
        if oom not in ("false", "true"):
            refuse("G1", {"oomkilled_unparseable": arm, "value": r.get("oomkilled")})
        rc_ok = bool(kernel_rc == 0 and oom == "false")
        if not rc_ok:
            out["rc_failures"].append({"arm": arm, "kernel_rc": kernel_rc, "oomkilled": oom})
        adir, datum = arm_datum(base, arm)
        if arm == "REF_off":
            hst = os.path.join(adir, "OptView.hst")
            if not os.path.isfile(hst):
                refuse("G1", {"staged_input_absent": hst})
            got = md5_of(hst)
            if got != MD5_D4_HST:
                refuse("G1", {"staged_input_md5_moved": hst, "got": got, "registered": MD5_D4_HST,
                              "note": "REF_off's D4 history is a staged INPUT exempt from the age guard "
                                      "by md5 only; a moved md5 refuses"})
            out["staged_inputs"][arm] = {"OptView.hst": got, "age_exempt_by_md5": True}
        logname = r.get("log")
        if kind == "SCRIPT":
            oks = glob.glob(os.path.join(base, logname + ".ok.*")) if logname else []
            arts = SCRIPT_ARTEFACTS.get(arm, [])
            art_paths = [os.path.join(adir, f) for f in arts]
            if not arts and logname:
                art_paths = [os.path.join(base, logname)]
            art_rows = []
            for ap in art_paths:
                present = os.path.isfile(ap)
                mt = int(os.path.getmtime(ap)) if present else None
                art_rows.append({"artefact": os.path.relpath(ap, base), "present": present, "mtime": mt,
                                 "newer_than_arm_datum": bool(present and mt > datum)})
            info = (terminal_statement_ok(os.path.join(base, logname))[1] if logname else {"log_not_named": True})
            t_ok = bool(oks and art_rows and all(a["newer_than_arm_datum"] for a in art_rows))
            t_detail = {"arm_kind": "SCRIPT", "ok_markers": [os.path.basename(x) for x in oks],
                        "arm_datum": datum, "artefacts": art_rows,
                        "terminal_statement_INFORMATIONAL_not_composed": info}
            age_ok, age_detail = t_ok, {"same_as_script_clause": True}
        else:
            if r.get("log_text") is not None:
                t_ok, t_detail = terminal_statement_ok_text(r["log_text"], "docker logs " + str(r.get("container")))
                t_detail["source"] = "kernel_record"
            elif not logname:
                t_ok, t_detail = False, {"log_not_named_in_ledger": arm}
            else:
                t_ok, t_detail = terminal_statement_ok(os.path.join(base, logname))
            t_detail["arm_kind"] = "SOLVER"
            art_rows = []
            for f in SOLVER_ARTEFACTS[arm]:
                ap = os.path.join(adir, f)
                present = os.path.isfile(ap)
                mt = int(os.path.getmtime(ap)) if present else None
                art_rows.append({"artefact": os.path.relpath(ap, base), "present": present, "mtime": mt,
                                 "newer_than_datum": bool(present and mt > datum)})
            age_ok = bool(art_rows and all(a["newer_than_datum"] for a in art_rows))
            age_detail = {"datum": datum, "artefacts": art_rows}
        if not t_ok:
            out["terminal_failures"].append({"arm": arm, "detail": t_detail})
        if not age_ok:
            out["age_failures"].append({"arm": arm, "detail": age_detail})
        nm = r.get("infra_not_measured", [])
        if nm:
            out["not_measured"][arm] = nm
        out["arms"][arm] = {"rc": r["rc"], "kernel_rc": kernel_rc, "arm_kind": kind, "source": r.get("source"),
                            "field_sources": r.get("field_sources"), "core_min": r["core_min"],
                            "oomkilled": oom, "rc_clause_pass": rc_ok, "terminal_clause_pass": bool(t_ok),
                            "age_clause_pass": bool(age_ok), "terminal_detail": t_detail,
                            "age_detail": age_detail, "infrastructure_not_measured": nm}
    if len(out["arms"]) != len(arms_required):
        refuse("G1", {"arms_checked": len(out["arms"]), "arms_required": len(arms_required)})
    out["pass"] = bool(not out["rc_failures"] and not out["terminal_failures"] and not out["age_failures"])
    out["any_oom_killed"] = any(f["oomkilled"] == "true" for f in out["rc_failures"])
    return out


OBJ_RE = re.compile(r"^Objective\.+:\s+(?P<scaled>[-+0-9.eE]+)\s+(?P<unscaled>[-+0-9.eE]+)\s*$", re.M)
NIT_RE = re.compile(r"^Number of Iterations\.+:\s+(?P<n>\d+)\s*$", re.M)
EXIT_RE = re.compile(r"^(EXIT: .*)$", re.M)


def read_ipopt(path, where="read_ipopt"):
    if not os.path.isfile(path):
        refuse(where, {"absent": path})
    txt = open(path, errors="replace").read()
    objs, exits, nits = OBJ_RE.findall(txt), EXIT_RE.findall(txt), NIT_RE.findall(txt)
    if not objs or not exits:
        refuse(where, {"no_final_objective_or_exit": path, "n_obj": len(objs), "n_exit": len(exits)})
    return {"objective": float(objs[-1][1]), "objective_scaled": float(objs[-1][0]),
            "exit": exits[-1].strip(), "n_iter": (int(nits[-1]) if nits else None),
            "optimal": exits[-1].strip().startswith("EXIT: Optimal Solution Found"), "path": path}


def planted_zero_control(ref_path, ctrl_dir, reader=read_ipopt):
    os.makedirs(ctrl_dir, exist_ok=True)
    txt = open(ref_path, errors="replace").read()
    base_val = reader(ref_path, "control")["objective"]
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    plant_path = os.path.join(ctrl_dir, "plant_%s.txt" % stamp)
    m = list(OBJ_RE.finditer(txt))[-1]
    planted_line = "Objective...............:   %.16e    %.16e" % (base_val + PLANT, base_val + PLANT)
    open(plant_path, "w").write(txt[:m.start()] + planted_line + txt[m.end():])
    seen = reader(plant_path, "control")["objective"]
    neg_path = os.path.join(ctrl_dir, "unperturbed_%s.txt" % stamp)
    open(neg_path, "w").write(txt)
    neg = reader(neg_path, "control")["objective"]
    if abs((seen - base_val) - PLANT) >= 1.0e-12:
        refuse("PLANTED_ZERO", {"reader_blind": True, "expected_delta": PLANT, "seen_delta": seen - base_val})
    if abs(neg - base_val) > 0.0:
        refuse("PLANTED_ZERO", {"negative_control_moved": neg - base_val})
    return {"pass": True, "plant": PLANT, "seen_delta": seen - base_val,
            "negative_control_delta": neg - base_val, "files": [plant_path, neg_path]}


def _f(v):
    return float(v)


def read_history(base):
    p = os.path.join(base, "O_mp", "d6_major_history.json")
    if not os.path.isfile(p):
        refuse("G-D6", {"absent": p})
    h = json.load(open(p))
    for k in ["J"] + ["CD_" + pt for pt in POINTS] + ["CL_" + pt for pt in POINTS]:
        if k not in h or not h[k]:
            refuse("G-D6", {"history_key_absent_or_empty": k, "path": p})
    return h


def read_ref_off(base):
    p = os.path.join(base, "REF_off", "d6_ref_off.json")
    if not os.path.isfile(p):
        refuse("G-D6-1", {"absent": p})
    r = json.load(open(p))
    for pt in POINTS:
        if pt not in r.get("points", {}) or "CD" not in r["points"][pt]:
            refuse("G-D6-1", {"ref_off_point_absent": pt, "path": p})
    return r


def g_points(hist, ref):
    per = {}
    for pt in POINTS:
        cd_mp = _f(hist["CD_" + pt][-1])
        cd_ref = _f(ref["points"][pt]["CD"])
        per[pt] = {"CD_mp": cd_mp, "CD_ref_off": cd_ref, "gain": cd_ref - cd_mp,
                   "CL_mp_final": _f(hist["CL_" + pt][-1]), "CL_ref": _f(ref["points"][pt]["CL"]),
                   "verdict": "PASS" if cd_mp <= cd_ref else "GATE FAIL"}
    return {"per_point": per, "all_pass": all(p["verdict"] == "PASS" for p in per.values()),
            "verdicts": {pt: per[pt]["verdict"] for pt in POINTS}}


def g_composite(hist, band=REDUCTION_BAND_PCT):
    j0, jf = _f(hist["J"][0]), _f(hist["J"][-1])
    if j0 == 0.0:
        refuse("G-D6-2", {"J0_zero": True})
    red = (j0 - jf) / j0 * 100.0
    ok = band[0] <= red <= band[1]
    return {"J0": j0, "Jf": jf, "reduction_pct": red, "band_pct": list(band), "n_major": len(hist["J"]),
            "verdict": "PASS" if ok else "GATE FAIL"}


def g_price(base, hist, d4_o_dir, band=PRICE_BAND):
    ref = os.path.join(d4_o_dir, "opt_IPOPT.txt")
    ctrl = planted_zero_control(ref, os.path.join(base, "grader_controls"))
    r = read_ipopt(ref, "G-D6-3")
    if abs(r["objective"] - CD_F_D4_RECORDED) > 1.0e-15:
        refuse("G-D6-3", {"d4_reference_changed": r["objective"], "recorded": CD_F_D4_RECORDED, "path": ref})
    price = _f(hist["CD_cl05"][-1]) - r["objective"]
    if price < band[0]:
        v = "NOT A RESULT"
    elif price > band[1]:
        v = "GATE FAIL"
    else:
        v = "PASS"
    return {"planted_control": ctrl, "CD_f_D4": r["objective"], "CD_cl05_mp": _f(hist["CD_cl05"][-1]),
            "price": price, "band": list(band), "verdict": v,
            "note": ("negative price: a finding about D4, NOT A RESULT pending triage" if v == "NOT A RESULT" else "")}


def g_fd(base):
    path = os.path.join(base, "O_mp", "d6_fd_endpoint.json")
    if not os.path.isfile(path):
        refuse("G-D6-4", {"absent": path})
    fd = json.load(open(path))
    if fd.get("components_requested") != COMPONENTS_REGISTERED:
        refuse("G-D6-4", {"components_not_the_registered_five": fd.get("components_requested")})
    comps, flips, planned, num, den = [], 0, [], 0.0, 0.0
    for row in fd["rows"]:
        c = {"dv": row["dv"], "idx": row["idx"], "status": row["status"]}
        if row["status"] != "PLANNED":
            c["verdict"] = "NOT A RESULT"
            comps.append(c)
            continue
        lo, hi = row["fd"].get("s_lo", {}), row["fd"].get("s_hi", {})
        if not (lo.get("ok") and hi.get("ok")):
            c["verdict"], c["fd_failed"] = "NOT A RESULT", True
            comps.append(c)
            continue
        d_lo, d_hi, j = _f(lo["d"]), _f(hi["d"]), _f(row["J_adj"])
        plateau = (abs(d_hi - d_lo) / abs(d_hi) * 100.0) if d_hi != 0 else float("inf")
        rel = (abs(d_hi - j) / abs(d_hi) * 100.0) if d_hi != 0 else float("inf")
        flip = bool((d_hi > 0) != (j > 0))
        flips += int(flip)
        num += (d_hi - j) ** 2
        den += d_hi ** 2
        c.update({"d_lo": d_lo, "d_hi": d_hi, "J_adj": j, "plateau_pct": plateau, "rel_err_pct": rel,
                  "sign_flip": flip,
                  "verdict": ("NOT A RESULT" if plateau > PLATEAU_TOL_PCT else
                              ("PASS" if (rel <= FD_BAND_PCT and not flip) else "GATE FAIL"))})
        planned.append(c)
        comps.append(c)
    agg = ((num / den) ** 0.5 * 100.0) if den > 0 else None
    pathology = bool(flips >= SIGN_FLIP_PATHOLOGY_N)
    return {"components": comps, "n_planned": len(planned), "sign_flips": flips,
            "pathology_NOT_A_RESULT": pathology, "aggregate_rel_err_pct": agg,
            "aggregate_pass": bool(agg is not None and agg <= FD_BAND_PCT),
            "verdict": ("NOT A RESULT" if (pathology or not planned) else
                        ("PASS" if (agg is not None and agg <= FD_BAND_PCT and
                                    all(c["verdict"] == "PASS" for c in planned)) else "GATE FAIL"))}


def g_caps(rows_by_arm):
    per, total = {}, 0.0
    for arm, r in rows_by_arm.items():
        cap = CAPS.get(arm)
        if cap is None:
            refuse("G10", {"arm_without_registered_cap": arm})
        per[arm] = {"core_min": r["core_min"], "cap": cap, "within_cap": bool(r["core_min"] <= cap),
                    "predicted": PREDICTED_CORE_MIN.get(arm),
                    "ratio_actual_over_predicted": r["core_min"] / PREDICTED_CORE_MIN[arm]}
        total += r["core_min"]
    ok = all(p["within_cap"] for p in per.values()) and total <= ITEM_CEILING_CORE_MIN
    return {"per_arm": per, "total_core_min": round(total, 3), "ceiling": ITEM_CEILING_CORE_MIN,
            "verdict": "PASS" if ok else "GATE FAIL"}


def g_toolchain(base, rows_by_arm):
    per = {}
    for arm, r in rows_by_arm.items():
        if r.get("log_text") is not None:
            txt = r["log_text"]
        elif r.get("log") and os.path.isfile(os.path.join(base, r["log"])):
            txt = open(os.path.join(base, r["log"]), errors="replace").read()
        else:
            txt = ""
        m = re.search(r"D4S_IDWARP_SO_MD5:\s*([0-9a-f]{32})", txt)
        per[arm] = {"digest": r.get("DIGEST"), "digest_ok": r.get("DIGEST") == IMG_PATCHED_DIGEST,
                    "so_md5": (m.group(1) if m else None),
                    "so_md5_ok": bool(m and m.group(1) == IDWARP_SO_MD5_PATCHED)}
    ok = bool(per) and all(p["digest_ok"] and p["so_md5_ok"] for p in per.values())
    return {"per_arm": per, "verdict": "PASS" if ok else "GATE FAIL"}


def g_placement(rows_by_arm):
    per, nm = {}, []
    for arm, r in rows_by_arm.items():
        cs = str(r.get("cpuset"))
        dm = re.match(r"\s*([\d.]+)", str(r.get("delivered", "")))
        delivered = float(dm.group(1)) if dm else None
        if delivered is None:
            nm.append(arm)
        per[arm] = {"cpuset": cs, "cpuset_ok": cs == CPUSET_REGISTERED,
                    "delivered_mean": (delivered if delivered is not None else NOT_MEASURED),
                    "delivered_ok": (bool(delivered >= DELIVERED_CORES_FLOOR) if delivered is not None else None)}
    ok = bool(per) and all(p["cpuset_ok"] and p["delivered_ok"] is not False for p in per.values())
    return {"per_arm": per, "delivered_not_measured": nm, "verdict": "PASS" if ok else "GATE FAIL"}


def compose(g1, gp, gc, gpr, gfd, g10, g9, g12):
    gates = {"G1_completion": "PASS" if g1["pass"] else "NOT A RESULT",
             "G-D6-1_cl04": gp["verdicts"]["cl04"], "G-D6-1_cl05": gp["verdicts"]["cl05"],
             "G-D6-1_cl06": gp["verdicts"]["cl06"], "G-D6-2_composite": gc["verdict"],
             "G-D6-3_price": gpr["verdict"], "G-D6-4_fd": gfd["verdict"],
             "G9_toolchain": g9["verdict"], "G10_caps": g10["verdict"], "G12_placement": g12["verdict"]}
    if not g1["pass"] or gfd["pathology_NOT_A_RESULT"] or gpr["verdict"] == "NOT A RESULT":
        item = "NOT A RESULT"
    elif any(v == "GATE FAIL" for v in gates.values()):
        item = "GATE FAIL"
    else:
        item = "PASS"
    if item not in VOCAB:
        refuse("VOCAB", {"item": item})
    return {"gates": gates, "item": item, "not_measured_named": dict(g1.get("not_measured", {})),
            "per_point_verdicts_reported_as_three": gp["verdicts"]}


def score_predictions(base, gc, gp, gpr, g10, g1):
    ip = read_ipopt(os.path.join(base, "O_mp", "opt_IPOPT.txt"), "P1")
    n = ip["n_iter"]
    p = {"P1": {"pred": "EXIT: Optimal within max_iter 100, majors [60,100] point 80",
                "obs": [ip["exit"], n],
                "score": ("HIT" if (ip["optimal"] and n is not None and
                                    PREDICTIONS_MAJORS[0] <= n <= PREDICTIONS_MAJORS[1]) else "MISS")},
         "P2": {"pred": "composite reduction [15,40] %, point 22 %", "obs": gc["reduction_pct"],
                "score": "HIT" if gc["verdict"] == "PASS" else "MISS"},
         "P3": {"pred": "price CD_0.5(mp) - CD_f(D4) in [0, 1.0e-3], point +3.0e-4", "obs": gpr["price"],
                "score": ("NOT A RESULT" if gpr["verdict"] == "NOT A RESULT" else
                          ("HIT" if gpr["verdict"] == "PASS" else "MISS"))},
         "P4": {"pred": "off-design gains > 0 (0.6 point +8.0e-4; 0.4 point +2.0e-4)",
                "obs": {"cl06": gp["per_point"]["cl06"]["gain"], "cl04": gp["per_point"]["cl04"]["gain"]},
                "score": ("HIT" if (gp["per_point"]["cl06"]["gain"] > 0 and gp["per_point"]["cl04"]["gain"] > 0)
                          else "MISS")},
         "P5": {"pred": "O_mp cost [1200, 2000] core-min, point 1533.4",
                "obs": g10["per_arm"].get("O_mp", {}).get("core_min"),
                "score": ("HIT" if (g10["per_arm"].get("O_mp") and
                                    P5_BAND[0] <= g10["per_arm"]["O_mp"]["core_min"] <= P5_BAND[1]) else "MISS")},
         "P6": {"pred": "all three per-point verdicts PASS", "obs": gp["verdicts"],
                "score": "HIT" if gp["all_pass"] else "MISS"},
         "P7": {"pred": "no arm OOM-killed at the 20g cap (multipoint feasible at np=4 on this box)",
                "obs": g1["any_oom_killed"], "score": "MISS" if g1["any_oom_killed"] else "HIT"}}
    return p


def grade(base=BASE, d4_o_dir=D4_O_DIR, arms=None):
    arms = arms or list(ARMS_REQUIRED)
    rows = read_ledger(os.path.join(base, "ledger.txt"))
    rows_by_arm = {}
    for r in rows:
        rows_by_arm[r["ARM"]] = r
    rows_by_arm = {a: rows_by_arm[a] for a in arms if a in rows_by_arm}
    g1 = g_completion(base, rows_by_arm, arms)
    hist = read_history(base)
    ref = read_ref_off(base)
    gp = g_points(hist, ref)
    gc = g_composite(hist)
    gpr = g_price(base, hist, d4_o_dir)
    gfd = g_fd(base)
    g10 = g_caps(rows_by_arm)
    g9 = g_toolchain(base, rows_by_arm)
    g12 = g_placement(rows_by_arm)
    comp = compose(g1, gp, gc, gpr, gfd, g10, g9, g12)
    preds = score_predictions(base, gc, gp, gpr, g10, g1)
    return {"item": "D6", "grader_md5": md5_of(__file__), "base": base, "verdict": comp["item"],
            "gates": comp["gates"], "per_point_verdicts": comp["per_point_verdicts_reported_as_three"],
            "not_measured_named": comp["not_measured_named"], "G1": g1, "G-D6-1": gp, "G-D6-2": gc,
            "G-D6-3": gpr, "G-D6-4": gfd, "G10": g10, "G9": g9, "G12": g12, "predictions": preds,
            "ref_off_consistency_CD_cl05_minus_D4": ref.get("consistency_CD_cl05_minus_D4_CD_f"),
            "L332": self_assert_check()}


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=BASE)
    ap.add_argument("--d4-o-dir", default=D4_O_DIR)
    ap.add_argument("--arms", default=",".join(ARMS_REQUIRED))
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    self_assert_check()
    try:
        res = grade(a.base, a.d4_o_dir, [x for x in a.arms.split(",") if x])
    except Refuse as exc:
        sys.stdout.write("D6_GRADE REFUSED %s\n" % exc)
        return 2
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "d6_grade_verdict_%s.json" % time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))
    json.dump(res, open(out, "w"), indent=1, sort_keys=True, default=str)
    nm = "; ".join("%s:%s" % (k, ",".join(v)) for k, v in sorted(res["not_measured_named"].items())) or "none"
    sys.stdout.write("D6_VERDICT %s | per-point %s | gates %s | NOT_MEASURED[%s] | out=%s\n"
                     % (res["verdict"], json.dumps(res["per_point_verdicts"], sort_keys=True),
                        json.dumps(res["gates"], sort_keys=True), nm, out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
