#!/usr/bin/env python3
"""Curriculum D5 grader -- FFD density study on D4's problem.  FROZEN by md5 in
PREREGISTRATION.md section 8 before any container starts.

WHAT IT GRADES (PREREGISTRATION.md sections 3 and 5):
  G1   completion, ARM-KIND AWARE (the D4-SHIPPED Addendum 2b form, from birth):
       SOLVER arms (O48, O192, F48, F192): kernel rc == 0 (docker inspect, never
       the harness $?), OOMKilled false, the POSITIONAL terminal statement
       `Finalising parallel run` as the LAST non-empty line of the producer's own
       log, and the AGE GUARD on the arm's registered artefacts.
       SCRIPT arms (ACC48, ACC192): kernel rc == 0, the launcher's `.ok` marker,
       and the registered artefact (the log itself; compute_totals writes no
       file) strictly newer than the arm's own `.d4_age_datum`.
  G-D5-1  cross-density: DeltaCD(192) = CD_f(192) - CD_f(96), |.| <= 3.0e-4 ->
       PASS else GATE FAIL.  CD_f(96) is RE-READ from D4's PATCHED `O/opt_IPOPT.txt`
       on disk (read-only) and never imported from a document; the reader carries
       a PLANTED control (rule 3) and refuses if it cannot see the plant.
       DeltaCD(48) carries NO band: sign only (P2).
  G-D5-P  the "optimiser exploits the parametrisation" pathology: a density
       whose FD table has >= 2 sign flips among the five registered components is
       NOT A RESULT for that density; its CD_f is quoted only beside that label.
  G5d  per-density FD bright line (D4 band D by citation): per-component and
       aggregate vector-relative error <= 5 %, plateau 10 %.
  G9   toolchain: every ledger row carries the PATCHED digest, every log the
       PATCHED libidwarp.so md5 (D4S_IDWARP_SO_MD5:, the string the inherited
       launcher prints).
  G10  caps: every row core_min <= its registered cap and the sum <= 1860.0;
       a crossing is GATE FAIL exactly as the frozen text says (report mode).
  G12  placement: cpuset == the registered 8,10,11,13 on every row; delivered
       cores >= 3.0 where MEASURED, NOT_MEASURED disclosed otherwise.

L-342 (Sanaa, d4d0c29d): a bookkeeping failure invalidates the bookkeeping,
never the physics.  FIELDS_PHYSICS absent -> REFUSE.  FIELDS_INFRASTRUCTURE
absent -> NOT_MEASURED, disclosed in the verdict line, never composed to PASS.
A field PRESENT BUT UNPARSEABLE -> REFUSE (absent != garbage).  An arm with no
ledger row is read from the KERNEL RECORD of its container (launcher naming
`d5_<ARM>_<stamp>`, no --rm) with the source named per field.

L-332: NO `assert` carries anything here.  Every refusal is `raise`/`sys.exit(2)`.
The module counts `ast.Assert` nodes in its own source and refuses on any.
Never an unconditional success print: each verdict word is emitted from the
branch that verified it.
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

# ---- REGISTERED CONSTANTS (PREREGISTRATION.md; the document governs) ----
BASE = "/home/ubuntu/certonomous-runs/CURRICULUM-D5-a2-wing-ffd-density"
D4_O_DIR = "/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/O"   # READ-ONLY; density 96
CD_F_96_RECORDED = 2.1125978108239574e-02   # D4 PATCHED, cited for the consistency check ONLY
ARMS_REQUIRED = ["O48", "ACC48", "F48", "O192", "ACC192", "F192"]
ARM_KIND = {"O48": "SOLVER", "O192": "SOLVER", "F48": "SOLVER", "F192": "SOLVER",
            "ACC48": "SCRIPT", "ACC192": "SCRIPT"}
ARM_DIR = {"O48": "O48", "ACC48": "ACC48", "F48": "O48",
           "O192": "O192", "ACC192": "ACC192", "F192": "O192"}
SOLVER_ARTEFACTS = {"O48": ["opt_IPOPT.txt", "OptView.hst"],
                    "O192": ["opt_IPOPT.txt", "OptView.hst"],
                    "F48": ["d5_fd_endpoint.json", "d4_endpoint_dvs.json"],
                    "F192": ["d5_fd_endpoint.json", "d4_endpoint_dvs.json"]}
SCRIPT_ARTEFACTS = {"ACC48": [], "ACC192": []}   # compute_totals writes no file: the artefact is the log
CAPS = {"O48": 800.0, "O192": 800.0, "ACC48": 10.0, "ACC192": 10.0,
        "F48": 120.0, "F192": 120.0}
ITEM_CEILING_CORE_MIN = 1860.0
PREDICTED_CORE_MIN = {"O48": 638.9, "O192": 638.9, "ACC48": 3.0, "ACC192": 3.0,
                      "F48": 47.267, "F192": 47.267}
CROSS_BAND_192 = 3.0e-4               # G-D5-1
SIGN_FLIP_PATHOLOGY_N = 2             # G-D5-P
FD_BAND_PCT = 5.0                     # D4 band D by citation
PLATEAU_TOL_PCT = 10.0
DENSITIES = {"48": "O48", "192": "O192"}
COMPONENTS_REGISTERED = [["shape", 46], ["shape", 18], ["shape", 0], ["twist", 0], ["patchV", 1]]
IMG_PATCHED_DIGEST = "sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35"
IDWARP_SO_MD5_PATCHED = "85f59e87253e0a71a813f64ca6e4c425"
RANKS = 4
CPUSET_REGISTERED = "8,10,11,13"
DELIVERED_CORES_FLOOR = 3.0
TERMINAL_STATEMENT = "Finalising parallel run"
FIELDS_PHYSICS = ("rc", "inspect_exit", "oomkilled", "terminal_statement",
                  "age_guard", "wall_s", "core_min", "cap_core_min",
                  "enforced_core_min", "DIGEST", "cpuset")
FIELDS_INFRASTRUCTURE = ("memavail_pre_GiB", "memavail_post_GiB", "delivered",
                         "siblings_pre", "siblings_post", "cpu_series", "log")
NOT_MEASURED = "NOT_MEASURED"
KERNEL_RECORD_NAME_PREFIX = "d5_%s_"
PLANT = 1.234e-03                      # rule 3
PREDICTIONS_MAJORS = (60, 100)         # P1
P4_BANDS = {"O48": (450.0, 700.0), "O192": (550.0, 850.0)}
VOCAB = {"PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"}


class Refuse(Exception):
    pass


def refuse(where, detail):
    msg = json.dumps({"REFUSE": where, "detail": detail}, sort_keys=True, default=str)
    sys.stderr.write("D5_GRADE REFUSE " + msg + "\n")
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


# ================= LEDGER (physics vs infrastructure, L-342) ================
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
    """ABSENT -> None (NOT_MEASURED).  PRESENT-BUT-GARBAGE is impossible here
    because the regex only admits a number or NOT_MEASURED; a garbage value
    makes the whole ARM= line unparseable, which read_ledger REFUSES."""
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
                              "note": "an ARM= line that does not parse is a "
                                      "PRESENT-BUT-GARBAGE row: refused, never "
                                      "skipped (absent != garbage)"})
        g = m.groupdict()
        parts = g["inspect"].split()
        infra_nm = [k for k, v in (("memavail_pre_GiB", g["mempre"]),
                                   ("memavail_post_GiB", g["mempost"]),
                                   ("delivered", g["delivered"]),
                                   ("siblings_pre", g["sibpre"]),
                                   ("siblings_post", g["sibpost"]),
                                   ("log", g["log"]))
                    if v is None or NOT_MEASURED in str(v)]
        rows.append({"ARM": g["ARM"], "ROW": g["ROW"], "IMG": g["IMG"],
                     "DIGEST": g["DIGEST"], "rc": int(g["rc"]),
                     "wall_s": int(g["wall_s"]), "ranks": int(g["ranks"]),
                     "core_min": float(g["core_min"]),
                     "cap_core_min": float(g["cap"]),
                     "enforced_core_min": float(g["ecore"]), "memory": g["mem"],
                     "inspect_exit": (parts[0] if parts else None),
                     "oomkilled": (parts[1] if len(parts) > 1 else None),
                     "memavail_pre_GiB": _infra_float(g["mempre"]),
                     "memavail_post_GiB": _infra_float(g["mempost"]),
                     "cpuset": g["cpuset"], "delivered": g["delivered"],
                     "siblings_pre": g["sibpre"], "siblings_post": g["sibpost"],
                     "log": g["log"], "source": "ledger_row",
                     "field_sources": {"all": "ledger_row"},
                     "infra_not_measured": infra_nm})
    return rows


# ================= KERNEL RECORD (L-342 fallback for an absent row) ===========
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
    digest = None
    img = insp.get("Config", {}).get("Image")
    m = re.search(r"(sha256:[0-9a-f]{64})", json.dumps(insp.get("Image", "")))
    if m:
        digest = m.group(1)
    return {"ARM": arm, "ROW": "PATCHED", "IMG": img, "DIGEST": digest,
            "rc": int(st.get("ExitCode", -1)), "inspect_exit": str(st.get("ExitCode")),
            "oomkilled": str(st.get("OOMKilled")).lower(), "wall_s": wall,
            "ranks": RANKS, "core_min": round(wall * RANKS / 60.0, 3),
            "cap_core_min": registered_cap, "enforced_core_min": registered_cap,
            "memory": str(hc.get("Memory")), "cpuset": hc.get("CpusetCpus"),
            "memavail_pre_GiB": None, "memavail_post_GiB": None,
            "delivered": NOT_MEASURED, "siblings_pre": NOT_MEASURED,
            "siblings_post": NOT_MEASURED, "log": None, "log_text": log_text,
            "container": name, "source": "kernel_record",
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
                      "note": "exactly one surviving container may stand in for a "
                              "missing ledger row; zero or several refuse"})
    insp = docker_inspect(names[0])
    if insp is None:
        refuse("G1", {"kernel_record_inspect_failed": names[0]})
    return kernel_record_row(arm, names[0], insp, docker_logs(names[0]), CAPS[arm])


# ================= G1: COMPLETION, ARM-KIND AWARE ==========================
def terminal_statement_ok_text(text, where):
    lines = [l.rstrip() for l in text.splitlines() if l.strip()]
    if not lines:
        return False, {"log": where, "empty": True}
    last = lines[-1]
    return (last.strip() == TERMINAL_STATEMENT,
            {"log": where, "last_line": last[:200],
             "n_occurrences_anywhere": text.count(TERMINAL_STATEMENT),
             "positional": True})


def terminal_statement_ok(path):
    if not os.path.isfile(path):
        return False, {"log": path, "absent": True,
                       "note": "a missing log is a FAILED clause, never a passing one"}
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
        refuse("G1", {"age_reference_moved": ref, "recorded": datum,
                      "on_disk": int(os.path.getmtime(ref))})
    return d, datum


def g_completion(base, rows_by_arm, arms_required):
    out = {"arms_required": arms_required, "arms": {}, "rc_failures": [],
           "terminal_failures": [], "age_failures": [], "not_measured": {}}
    for arm in arms_required:
        r = rows_by_arm.get(arm)
        if r is None:
            r = kernel_record_fallback(arm)
            rows_by_arm[arm] = r
        kind = ARM_KIND.get(arm)
        if kind is None:
            refuse("G1", {"arm_kind_unregistered": arm, "registered": sorted(ARM_KIND)})
        # ---- clause 1: rc == 0 from the KERNEL'S record ----
        ke = r.get("inspect_exit")
        if ke is None:
            refuse("G1", {"kernel_exit_absent": arm,
                          "note": "inspect(exit,oomkilled) is a PHYSICS field"})
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
        # ---- clause 2 + 3: by ARM KIND ----
        adir, datum = arm_datum(base, arm)
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
                art_rows.append({"artefact": os.path.relpath(ap, base), "present": present,
                                 "mtime": mt, "newer_than_arm_datum": bool(present and mt > datum)})
            info = (terminal_statement_ok(os.path.join(base, logname))[1] if logname
                    else {"log_not_named": True})
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
                t_ok, t_detail = False, {"log_not_named_in_ledger": arm,
                                         "note": "reported as a FAILED clause, never a passing one"}
            else:
                t_ok, t_detail = terminal_statement_ok(os.path.join(base, logname))
            t_detail["arm_kind"] = "SOLVER"
            art_rows = []
            for f in SOLVER_ARTEFACTS[arm]:
                ap = os.path.join(adir, f)
                present = os.path.isfile(ap)
                mt = int(os.path.getmtime(ap)) if present else None
                art_rows.append({"artefact": os.path.relpath(ap, base), "present": present,
                                 "mtime": mt, "newer_than_datum": bool(present and mt > datum)})
            age_ok = bool(art_rows and all(a["newer_than_datum"] for a in art_rows))
            age_detail = {"datum": datum, "artefacts": art_rows}
        if not t_ok:
            out["terminal_failures"].append({"arm": arm, "detail": t_detail})
        if not age_ok:
            out["age_failures"].append({"arm": arm, "detail": age_detail})
        nm = r.get("infra_not_measured", [])
        if nm:
            out["not_measured"][arm] = nm
        out["arms"][arm] = {"rc": r["rc"], "kernel_rc": kernel_rc, "arm_kind": kind,
                            "source": r.get("source"), "field_sources": r.get("field_sources"),
                            "core_min": r["core_min"], "oomkilled": oom,
                            "rc_clause_pass": rc_ok, "terminal_clause_pass": bool(t_ok),
                            "age_clause_pass": bool(age_ok), "terminal_detail": t_detail,
                            "age_detail": age_detail, "infrastructure_not_measured": nm}
    if len(out["arms"]) != len(arms_required):
        refuse("G1", {"arms_checked": len(out["arms"]), "arms_required": len(arms_required)})
    out["pass"] = bool(not out["rc_failures"] and not out["terminal_failures"]
                       and not out["age_failures"])
    return out


# ================= IPOPT READER + PLANTED CONTROL ============================
OBJ_RE = re.compile(r"^Objective\.+:\s+(?P<scaled>[-+0-9.eE]+)\s+(?P<unscaled>[-+0-9.eE]+)\s*$", re.M)
NIT_RE = re.compile(r"^Number of Iterations\.+:\s+(?P<n>\d+)\s*$", re.M)
EXIT_RE = re.compile(r"^(EXIT: .*)$", re.M)


def read_ipopt(path, where="read_ipopt"):
    if not os.path.isfile(path):
        refuse(where, {"absent": path})
    txt = open(path, errors="replace").read()
    objs = OBJ_RE.findall(txt)
    exits = EXIT_RE.findall(txt)
    nits = NIT_RE.findall(txt)
    if not objs or not exits:
        refuse(where, {"no_final_objective_or_exit": path, "n_obj": len(objs), "n_exit": len(exits)})
    return {"objective": float(objs[-1][1]), "objective_scaled": float(objs[-1][0]),
            "exit": exits[-1].strip(), "n_iter": (int(nits[-1]) if nits else None),
            "optimal": exits[-1].strip().startswith("EXIT: Optimal Solution Found"),
            "path": path}


def planted_zero_control(ref_path, ctrl_dir, reader=read_ipopt):
    """rule 3: perturb a COPY of the reference by PLANT, read it back with the
    SAME reader, refuse unless the reader sees exactly the plant; and read an
    unperturbed copy back unchanged (negative control)."""
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
    ok = abs((seen - base_val) - PLANT) < 1.0e-12
    if not ok:
        refuse("PLANTED_ZERO", {"reader_blind": True, "expected_delta": PLANT,
                                "seen_delta": seen - base_val, "file": plant_path})
    if abs(neg - base_val) > 0.0:
        refuse("PLANTED_ZERO", {"negative_control_moved": neg - base_val})
    return {"pass": True, "plant": PLANT, "seen_delta": seen - base_val,
            "negative_control_delta": neg - base_val, "files": [plant_path, neg_path]}


def g_cross_density(base, d4_o_dir, band=CROSS_BAND_192):
    ref = os.path.join(d4_o_dir, "opt_IPOPT.txt")
    ctrl = planted_zero_control(ref, os.path.join(base, "grader_controls"))
    r96 = read_ipopt(ref, "G-D5-1")
    if abs(r96["objective"] - CD_F_96_RECORDED) > 1.0e-15:
        refuse("G-D5-1", {"d4_reference_changed": r96["objective"],
                          "recorded": CD_F_96_RECORDED, "path": ref})
    out = {"planted_control": ctrl, "CD_f": {"96": r96["objective"]},
           "exit": {"96": r96["exit"]}, "n_iter": {"96": r96["n_iter"]}, "band_192": band}
    for d, arm in DENSITIES.items():
        r = read_ipopt(os.path.join(base, arm, "opt_IPOPT.txt"), "G-D5-1")
        out["CD_f"][d] = r["objective"]
        out["exit"][d] = r["exit"]
        out["n_iter"][d] = r["n_iter"]
    out["delta_192"] = out["CD_f"]["192"] - out["CD_f"]["96"]
    out["delta_48"] = out["CD_f"]["48"] - out["CD_f"]["96"]
    out["in_band_192"] = bool(abs(out["delta_192"]) <= band)
    out["verdict"] = "PASS" if out["in_band_192"] else "GATE FAIL"
    out["P2_sign_48_positive"] = bool(out["delta_48"] > 0.0)
    return out


# ================= FD BRIGHT LINE PER DENSITY ================================
def _f(v):
    return float(v) if isinstance(v, str) else float(v)


def g_fd_density(base, arm):
    path = os.path.join(base, arm, "d5_fd_endpoint.json")
    if not os.path.isfile(path):
        refuse("G5d", {"absent": path})
    fd = json.load(open(path))
    if fd.get("components_requested") != COMPONENTS_REGISTERED:
        refuse("G5d", {"components_not_the_registered_five": fd.get("components_requested")})
    comps, flips, planned = [], 0, []
    num, den = 0.0, 0.0
    for row in fd["rows"]:
        c = {"dv": row["dv"], "idx": row["idx"], "status": row["status"]}
        if row["status"] != "PLANNED":
            c["verdict"] = "NOT A RESULT"
            comps.append(c)
            continue
        lo, hi = row["fd"].get("s_lo", {}), row["fd"].get("s_hi", {})
        if not (lo.get("ok") and hi.get("ok")):
            c["verdict"] = "NOT A RESULT"
            c["fd_failed"] = True
            comps.append(c)
            continue
        d_lo, d_hi, j = _f(lo["d"]), _f(hi["d"]), _f(row["J_adj"])
        plateau = (abs(d_hi - d_lo) / abs(d_hi) * 100.0) if d_hi != 0 else float("inf")
        rel = (abs(d_hi - j) / abs(d_hi) * 100.0) if d_hi != 0 else float("inf")
        flip = bool((d_hi > 0) != (j > 0))
        flips += int(flip)
        num += (d_hi - j) ** 2
        den += d_hi ** 2
        c.update({"d_lo": d_lo, "d_hi": d_hi, "J_adj": j, "plateau_pct": plateau,
                  "rel_err_pct": rel, "sign_flip": flip,
                  "verdict": ("NOT A RESULT" if plateau > PLATEAU_TOL_PCT else
                              ("PASS" if (rel <= FD_BAND_PCT and not flip) else "GATE FAIL"))})
        planned.append(c)
        comps.append(c)
    agg = ((num / den) ** 0.5 * 100.0) if den > 0 else None
    pathology = bool(flips >= SIGN_FLIP_PATHOLOGY_N)
    return {"arm": arm, "components": comps, "n_planned": len(planned), "sign_flips": flips,
            "pathology_NOT_A_RESULT": pathology, "aggregate_rel_err_pct": agg,
            "aggregate_pass": bool(agg is not None and agg <= FD_BAND_PCT),
            "verdict": ("NOT A RESULT" if (pathology or not planned) else
                        ("PASS" if (agg is not None and agg <= FD_BAND_PCT and
                                    all(c["verdict"] == "PASS" for c in planned)) else "GATE FAIL"))}


# ================= G9 / G10 / G12 ===========================================
def g_caps(rows_by_arm):
    per, total = {}, 0.0
    for arm, r in rows_by_arm.items():
        cap = CAPS.get(arm)
        if cap is None:
            refuse("G10", {"arm_without_registered_cap": arm})
        per[arm] = {"core_min": r["core_min"], "cap": cap, "within_cap": bool(r["core_min"] <= cap),
                    "predicted": PREDICTED_CORE_MIN.get(arm),
                    "ratio_actual_over_predicted": (r["core_min"] / PREDICTED_CORE_MIN[arm]
                                                    if PREDICTED_CORE_MIN.get(arm) else None)}
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
        d = str(r.get("delivered", ""))
        dm = re.match(r"\s*([\d.]+)", d)
        delivered = float(dm.group(1)) if dm else None
        if delivered is None:
            nm.append(arm)
        per[arm] = {"cpuset": cs, "cpuset_ok": cs == CPUSET_REGISTERED,
                    "delivered_mean": (delivered if delivered is not None else NOT_MEASURED),
                    "delivered_ok": (bool(delivered >= DELIVERED_CORES_FLOOR) if delivered is not None else None)}
    ok = bool(per) and all(p["cpuset_ok"] and p["delivered_ok"] is not False for p in per.values())
    return {"per_arm": per, "delivered_not_measured": nm, "verdict": "PASS" if ok else "GATE FAIL"}


# ================= COMPOSITION ==============================================
def compose(g1, gx, fd48, fd192, g10, g9, g12):
    gates = {"G1_completion": "PASS" if g1["pass"] else "NOT A RESULT",
             "G-D5-P_48": "NOT A RESULT" if fd48["pathology_NOT_A_RESULT"] else "PASS",
             "G-D5-P_192": "NOT A RESULT" if fd192["pathology_NOT_A_RESULT"] else "PASS",
             "G5d_48": fd48["verdict"], "G5d_192": fd192["verdict"],
             "G-D5-1": gx["verdict"], "G9_toolchain": g9["verdict"],
             "G10_caps": g10["verdict"], "G12_placement": g12["verdict"]}
    if fd192["pathology_NOT_A_RESULT"]:
        gates["G-D5-1"] = "NOT A RESULT"       # CD_f(192) quoted only beside the label
    if not g1["pass"]:
        item = "NOT A RESULT"
    elif fd192["pathology_NOT_A_RESULT"]:
        item = "NOT A RESULT"
    elif any(gates[k] == "GATE FAIL" for k in ("G-D5-1", "G9_toolchain", "G10_caps", "G12_placement")):
        item = "GATE FAIL"
    else:
        item = "PASS"
    if item not in VOCAB:
        refuse("VOCAB", {"item": item})
    nm = {}
    for arm, fields in g1.get("not_measured", {}).items():
        nm[arm] = fields
    return {"gates": gates, "item": item, "not_measured_named": nm}


def score_predictions(gx, g10, fd48, fd192):
    p = {}
    n48, n192 = gx["n_iter"].get("48"), gx["n_iter"].get("192")
    p["P1"] = {"pred": "both densities optimal within max_iter, majors in [60,100]",
               "obs": {"48": [gx["exit"]["48"], n48], "192": [gx["exit"]["192"], n192]},
               "score": ("HIT" if (gx["exit"]["48"].startswith("EXIT: Optimal") and
                                   gx["exit"]["192"].startswith("EXIT: Optimal") and
                                   n48 is not None and n192 is not None and
                                   PREDICTIONS_MAJORS[0] <= n48 <= PREDICTIONS_MAJORS[1] and
                                   PREDICTIONS_MAJORS[0] <= n192 <= PREDICTIONS_MAJORS[1]) else "MISS")}
    p["P2"] = {"pred": "DeltaCD(48) > 0", "obs": gx["delta_48"],
               "score": ("NOT A RESULT" if fd48["pathology_NOT_A_RESULT"] else
                         ("HIT" if gx["P2_sign_48_positive"] else "MISS"))}
    p["P3"] = {"pred": "DeltaCD(192) in [-3.0e-4, 0], point -1.0e-4", "obs": gx["delta_192"],
               "score": ("NOT A RESULT" if fd192["pathology_NOT_A_RESULT"] else
                         ("HIT" if (-CROSS_BAND_192 <= gx["delta_192"] <= 0.0) else "MISS"))}
    p4 = {}
    for arm, (lo, hi) in P4_BANDS.items():
        cm = g10["per_arm"].get(arm, {}).get("core_min")
        p4[arm] = {"obs": cm, "band": [lo, hi], "score": ("HIT" if (cm is not None and lo <= cm <= hi) else "MISS")}
    p["P4"] = p4
    p["P5"] = {"pred": "each density <= 1 sign flip and aggregate < 5 %",
               "obs": {"48": [fd48["sign_flips"], fd48["aggregate_rel_err_pct"]],
                       "192": [fd192["sign_flips"], fd192["aggregate_rel_err_pct"]]},
               "score": ("HIT" if (fd48["sign_flips"] <= 1 and fd192["sign_flips"] <= 1 and
                                   fd48["aggregate_pass"] and fd192["aggregate_pass"]) else "MISS")}
    return p


def grade(base=BASE, d4_o_dir=D4_O_DIR, arms=None):
    arms = arms or list(ARMS_REQUIRED)
    rows = read_ledger(os.path.join(base, "ledger.txt"))
    rows_by_arm = {}
    for r in rows:
        rows_by_arm[r["ARM"]] = r          # last row per arm wins; ALREADY_BOUGHT forbids a second rc=0
    rows_by_arm = {a: rows_by_arm[a] for a in arms if a in rows_by_arm}
    g1 = g_completion(base, rows_by_arm, arms)
    gx = g_cross_density(base, d4_o_dir)
    fd48 = g_fd_density(base, "O48")
    fd192 = g_fd_density(base, "O192")
    g10 = g_caps(rows_by_arm)
    g9 = g_toolchain(base, rows_by_arm)
    g12 = g_placement(rows_by_arm)
    comp = compose(g1, gx, fd48, fd192, g10, g9, g12)
    preds = score_predictions(gx, g10, fd48, fd192)
    return {"item": "D5", "grader_md5": md5_of(__file__), "base": base,
            "verdict": comp["item"], "gates": comp["gates"],
            "not_measured_named": comp["not_measured_named"],
            "G1": g1, "G-D5-1": gx, "G5d": {"48": fd48, "192": fd192},
            "G10": g10, "G9": g9, "G12": g12, "predictions": preds,
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
        sys.stdout.write("D5_GRADE REFUSED %s\n" % exc)
        return 2
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "d5_grade_verdict_%s.json" % time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))
    json.dump(res, open(out, "w"), indent=1, sort_keys=True, default=str)
    nm = "; ".join("%s:%s" % (k, ",".join(v)) for k, v in sorted(res["not_measured_named"].items())) or "none"
    sys.stdout.write("D5_VERDICT %s | gates %s | NOT_MEASURED[%s] | out=%s\n"
                     % (res["verdict"], json.dumps(res["gates"], sort_keys=True), nm, out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
