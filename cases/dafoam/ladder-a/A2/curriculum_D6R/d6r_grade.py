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
  G-D6R-1  per point: CD_i(mp) <= CD_i(REF_off) -> PASS for that point, else GATE
          FAIL for that point.  THREE verdicts, always all three reported.
  G-D6R-2  composite: (J_0 - J_f)/J_0 in [15, 40] % -> PASS else GATE FAIL.
  G-D6R-3  single-point price: CD_0.5(mp) - CD_f(D4) in [0, 1.0e-3] -> PASS;
          > 1.0e-3 -> GATE FAIL; NEGATIVE -> NOT A RESULT pending triage (a
          finding about D4, not about D6).  CD_f(D4) is RE-READ from D4's O/
          opt_IPOPT.txt (read-only) through a reader with a PLANTED control.
  G-D6R-4  bright line on J: per-component and aggregate FD error <= 5 %, sign
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

BASE = "/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint"
D4_O_DIR = "/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/O"   # READ-ONLY
CD_F_D4_RECORDED = 2.1125978108239574e-02
MD5_D4_HST = "0d956d6ccbc010402915710f662d3b11"      # D4 O/OptView.hst, staged into REF_off/
ARMS_REQUIRED = ["O_mp", "ACC_mp", "F_mp", "REF_off"]
ARM_KIND = {"O_mp": "SOLVER", "F_mp": "SOLVER", "ACC_mp": "SCRIPT", "REF_off": "SCRIPT"}
# ---- ARM WORKING DIRECTORIES, STATED WITH THEIR REASON AND ASSERTED AGAINST
# ---- THE LAUNCHER'S OWN BYTES (PREREGISTRATION.md section 3b).
# F_mp -> O_mp is NOT an alias defect: F_mp is registered to run IN O_mp's
# directory, reading the optimiser's OptView.hst and writing its three products
# THERE (d6r_run_arm.sh sets WORK="$BASE/O_mp" for F_mp and stages nothing
# else).  A per-arm artefact is therefore sought where the arm that WRITES it
# puts it -- and ARTEFACT_PRODUCER below names that arm, so an absent product
# is attributed to the arm that would have produced it instead of read as a
# defect of the directory it is missing from.
ARM_DIR = {"O_mp": "O_mp", "ACC_mp": "ACC_mp", "F_mp": "O_mp", "REF_off": "REF_off"}
ARM_DIR_REASON = {"O_mp": "its own staged case", "ACC_mp": "its own staged case",
                  "F_mp": "REGISTERED to run inside O_mp/ -- it reads the optimiser endpoint",
                  "REF_off": "its own staged case"}
ARTEFACT_PRODUCER = {"opt_IPOPT.txt": "O_mp", "OptView.hst": "O_mp",
                     "d6r_fd_endpoint.json": "F_mp", "d6r_endpoint_dvs.json": "F_mp",
                     "d6r_major_history.json": "F_mp", "d6r_ref_off.json": "REF_off"}
LAUNCHER_NAME = "d6r_run_arm.sh"
LAUNCHER_F_MP_WORKDIR_LINE = 'WORK="$BASE/O_mp"'
SOLVER_ARTEFACTS = {"O_mp": ["opt_IPOPT.txt", "OptView.hst"],
                    "F_mp": ["d6r_fd_endpoint.json", "d6r_endpoint_dvs.json", "d6r_major_history.json"]}
SCRIPT_ARTEFACTS = {"ACC_mp": [], "REF_off": ["d6r_ref_off.json"]}
# ---- COST, RE-DERIVED FROM THE MEASURED ANCHOR (PREREGISTRATION.md section 4).
# C-188 (8262f123) measured 31.258 core-min/major on THIS case at np=4
# (2000.533 core-min / 64 majors) against 19.167 registered (6.389 x 3) =
# 1.6308x.  D6's registered 80-major point costs 2500.7 at that rate -- 25 %
# ABOVE its 2000.0 cap, so THAT CAP COULD NEVER HAVE BEEN MET.  Nothing here is
# inherited: every figure below is that measurement or that measurement's
# correction factor applied to an arm whose own anchor is the same x3 model.
RATE_CORE_MIN_PER_MAJOR_MEASURED = 31.258      # C-188, D6 O_mp, 64 majors
MULTIPOINT_CORRECTION_MEASURED = 1.6308        # C-188, 31.258 / 19.167
MAX_ITER_REGISTERED = 80                       # d6r_opt_runScript.py, the BINDING stop
CAPS = {"O_mp": 2900.0, "ACC_mp": 30.0, "F_mp": 300.0, "REF_off": 40.0}
ITEM_CEILING_CORE_MIN = 3270.0
PREDICTED_CORE_MIN = {"O_mp": 2500.6, "ACC_mp": 14.7, "F_mp": 231.2, "REF_off": 17.1}
POINTS = ["cl04", "cl05", "cl06"]
WEIGHTS = {"cl04": 0.25, "cl05": 0.50, "cl06": 0.25}
REDUCTION_BAND_PCT = (15.0, 40.0)     # G-D6R-2
PRICE_BAND = (0.0, 1.0e-3)            # G-D6R-3
SIGN_FLIP_PATHOLOGY_N = 2
FD_BAND_PCT = 5.0
PLATEAU_TOL_PCT = 10.0
COMPONENTS_REGISTERED = [["shape", 46], ["shape", 18], ["shape", 0], ["twist", 0], ["patchV_cl05", 1]]
IMG_PATCHED_DIGEST = "sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35"
IDWARP_SO_MD5_PATCHED = "85f59e87253e0a71a813f64ca6e4c425"
RANKS = 4
# ---- CAP FRAME.  The cap is ENFORCED in the container (`timeout`) and GRADED
# on the host bracket T0..T1, and D6 measured the gap at 8 s = 0.5333 core-min,
# recording 2000.533 against a 2000.0 cap -- IT EXCEEDED ITS OWN CAP BY OBEYING
# IT (D6-CAP-FRAME-1, L-371).  THE CAP IS NOT WIDENED: the enforced deadline
# moves DOWN by the allowance and the arithmetic INVERTS to the registered cap.
# Cross-pinned: these three names appear in d6r_run_arm.sh with the same values.
FRAME_ALLOWANCE_S = 90
KILL_GRACE_S = 60          # `timeout -k 60` TERM->KILL escalation
TMO_REGISTERED_S = {a: int(round(c * 60.0 / 4)) - FRAME_ALLOWANCE_S for a, c in CAPS.items()}
CPUSET_REGISTERED = "2,3,4,14"
DELIVERED_CORES_FLOOR = 3.0
TERMINAL_STATEMENT = "Finalising parallel run"
FIELDS_PHYSICS = ("rc", "inspect_exit", "oomkilled", "terminal_statement", "age_guard", "wall_s",
                  "core_min", "cap_core_min", "enforced_core_min", "DIGEST", "cpuset")
FIELDS_INFRASTRUCTURE = ("memavail_pre_GiB", "memavail_post_GiB", "delivered", "siblings_pre",
                         "siblings_post", "cpu_series", "log", "container_wall_s")
NOT_MEASURED = "NOT_MEASURED"
KERNEL_RECORD_NAME_PREFIX = "d6r_%s_"
PLANT = 1.234e-03
# ---- THE OPTIMISER OUTCOME LADDER (PREREGISTRATION.md section 3c).  A STALL
# ---- IS NOT A CAP HIT AND IS NEVER COLLAPSED INTO ONE.  D6 measured, at the
# ---- registered tol 1e-5: 548 `Cutting back alpha due to evaluation error`
# ---- over 64 majors (8.56/major), 7 restoration majors, and dual infeasibility
# ---- WORSENING from 5.78e-04 at major 58 to 1.14e-03 at major 64.
STALL_CUTBACKS_PER_MAJOR = 1.0    # a converging line search accepts alpha; >=1
                                  # sustained means it fails once per major on
                                  # average.  D6 measured 8.56.
STALL_TAIL_FRACTION = 0.90        # inf_du at the last major vs at 90 % of them
OPT_OUTCOMES = ("CONVERGED", "ITERATION_CAP", "STALLED", "DEADLINE", "UNCLASSIFIED")
PREDICTIONS_MAJORS = (60, 80)
P5_BAND = (1900.0, 2900.0)
VOCAB = {"PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"}


class Refuse(Exception):
    pass


def refuse(where, detail):
    msg = json.dumps({"REFUSE": where, "detail": detail}, sort_keys=True, default=str)
    sys.stderr.write("D6R_GRADE REFUSE " + msg + "\n")
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
    r"(?:\s+container_wall_s=(?P<cwall>\d+|NOT_MEASURED))?"
    r"(?:\s+frame_allowance_s=(?P<falw>[\d.]+|NOT_MEASURED))?"
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
        infra_nm = [k for k, v in (("container_wall_s", g["cwall"]),
                                   ("memavail_pre_GiB", g["mempre"]), ("memavail_post_GiB", g["mempost"]),
                                   ("delivered", g["delivered"]), ("siblings_pre", g["sibpre"]),
                                   ("siblings_post", g["sibpost"]), ("log", g["log"]))
                    if v is None or NOT_MEASURED in str(v)]
        rows.append({"ARM": g["ARM"], "ROW": g["ROW"], "IMG": g["IMG"], "DIGEST": g["DIGEST"],
                     "rc": int(g["rc"]), "wall_s": int(g["wall_s"]), "ranks": int(g["ranks"]),
                     "core_min": float(g["core_min"]), "cap_core_min": float(g["cap"]),
                     "enforced_core_min": float(g["ecore"]), "memory": g["mem"],
                     "container_wall_s": (int(g["cwall"]) if (g["cwall"] and g["cwall"] != NOT_MEASURED) else None),
                     "frame_allowance_s": (float(g["falw"]) if (g["falw"] and g["falw"] != NOT_MEASURED) else None),
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
    """D6-GRADER-DEF-2 REPAIRED, AND THE REPAIR IS DRIVEN (L-357).

    d6_grade.py:176-179 passed BOTH `capture_output=True` AND
    `stderr=subprocess.STDOUT`; that combination raises
    `ValueError: stdout and stderr arguments may not be used with
    capture_output`, so this function COULD NEVER RETURN from the day it was
    frozen.  Its only call site is reached when an arm is missing from the
    ledger AND exactly one container survives to stand in -- on D6's run
    `names` was empty and :219 refused first, so the defect never fired.  Had
    one leftover container existed the grader would have died with a traceback
    instead of refusing.  The repair asks for the merge explicitly, with no
    `capture_output`, and d6r_grade_selftest.py DRIVES this function and shows
    it returns under python3 AND python3 -O.
    """
    r = subprocess.run(["sudo", "-n", "docker", "logs", name],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
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
    """Stand in for a LOST LEDGER ROW of an arm that RAN.  Returns None when no
    container survives, so the caller can ask the chain record whether the arm
    ran at all.  SEVERAL candidates still REFUSE -- that guard is the one
    REFIRE_RUNBOOK.md section 1 forbids loosening, and it is not loosened here:
    the line below a relaxed count assertion reads rc from an EARLIER fire, and
    under R-RC the rc value is physics.  ONLY the zero case moves, because zero
    is not ambiguity, it is absence, and absence is what the chain record
    explains."""
    names = docker_ps_a_names(KERNEL_RECORD_NAME_PREFIX % arm)
    if len(names) == 0:
        return None
    if len(names) != 1:
        refuse("G1", {"arm_absent_from_ledger": arm, "kernel_record_candidates": names,
                      "note": "exactly one surviving container may stand in; several REFUSE"})
    insp = docker_inspect(names[0])
    if insp is None:
        refuse("G1", {"kernel_record_inspect_failed": names[0]})
    return kernel_record_row(arm, names[0], insp, docker_logs(names[0]), CAPS[arm])


# ===========================================================================
# D6-GRADER-DEF-1 REPAIR -- THE ARM CENSUS.
# D6's registration calls a chain stop at O_mp "a finding about multipoint
# feasibility at np=4 on this box, not a wasted run" (PREREGISTRATION.md
# :115-117) and lists STOPPED_AT_FIRST_NONZERO among its registered chain
# outcomes (:299) -- and its grader REFUSED on any arm without a ledger row
# (d6_grade.py:218-220).  THE ITEM COULD NOT GRADE ONE OF ITS OWN REGISTERED
# PATHS (L-322).  D6R reads the driver's own chain record, NAMES the arms that
# did not run and why, and grades the arms that did on their own limbs.
# THIS IS NOT A WIDENING.  An arm absent for a reason the registration does NOT
# name still REFUSES; and a gate whose input arm did not run is NOT A RESULT
# for that gate -- never PASS, never GATE FAIL.
# ===========================================================================
CHAIN_STOP_RE = re.compile(r"^chain=(?P<outcome>[A-Z_]+)(?:\s+arm=(?P<arm>\S+))?"
                           r"(?:\s+rc=(?P<rc>-?\d+))?", re.M)
CHAIN_STARTED_RE = re.compile(r"^chain=started\s+arms=\[(?P<arms>[^\]]*)\]", re.M)
# Every chain outcome the DRIVER can write, and whether it accounts for the
# arms downstream of it NOT having run.  Registered before compute.
CHAIN_OUTCOMES_ACCOUNTING = {
    "STOPPED_AT_FIRST_NONZERO": True,   # the stop arm ran; everything after did not
    "STOPPED_H5": True,                 # refused at the memory floor, zero compute
    "BLOCKED_H5": True,
    "BLOCKED_AGGREGATE": True,
    "REFUSED_ALREADY_BOUGHT": True,
    "ABORT": True,                      # launcher md5 drifted mid-chain
    "COMPLETE": False,                  # nothing may be missing after COMPLETE
    "started": False,
}


def read_chain_status(base):
    """The driver's own record of what it ran.  Absent -> NOT_MEASURED, and an
    unexplained absent arm then refuses exactly as before."""
    p = os.path.join(base, "STATUS.chain")
    if not os.path.isfile(p):
        return {"present": False, "path": p, "registered_order": None, "outcome": None,
                "stop_arm": None, "stop_rc": None}
    txt = open(p, errors="replace").read()
    m0 = CHAIN_STARTED_RE.search(txt)
    order = m0.group("arms").split() if m0 else None
    last = None
    for m in CHAIN_STOP_RE.finditer(txt):
        if m.group("outcome") != "started":
            last = m
    return {"present": True, "path": p, "registered_order": order,
            "outcome": (last.group("outcome") if last else None),
            "stop_arm": (last.group("arm") if last else None),
            "stop_rc": (int(last.group("rc")) if last and last.group("rc") else None),
            "text_tail": txt.strip().splitlines()[-3:]}


def arm_census(base, rows_by_arm, arms_required):
    """RAN / NOT_RUN(reason) / refuse.  Order: ledger row -> surviving container
    -> the chain record's own explanation -> REFUSE."""
    chain = read_chain_status(base)
    order = chain["registered_order"] or list(arms_required)
    if chain["registered_order"] is not None and chain["registered_order"] != list(arms_required):
        refuse("G1", {"chain_order_not_the_registered_order": chain["registered_order"],
                      "registered": list(arms_required),
                      "note": "the driver ran a different arm list than the one registered"})
    census = {}
    for arm in arms_required:
        if arm in rows_by_arm:
            census[arm] = {"state": "RAN", "source": rows_by_arm[arm].get("source")}
            continue
        row = kernel_record_fallback(arm)
        if row is not None:
            rows_by_arm[arm] = row
            census[arm] = {"state": "RAN", "source": "kernel_record",
                           "note": "ledger row lost; the kernel record stands in (L-342, bookkeeping never voids physics)"}
            continue
        stop_arm, outcome = chain["stop_arm"], chain["outcome"]
        accounted = bool(outcome in CHAIN_OUTCOMES_ACCOUNTING and CHAIN_OUTCOMES_ACCOUNTING[outcome])
        downstream = False
        if accounted and stop_arm in order and arm in order:
            downstream = order.index(arm) >= order.index(stop_arm)
        if accounted and downstream:
            census[arm] = {"state": "NOT_RUN", "reason": "REGISTERED_CHAIN_%s" % outcome,
                           "stop_arm": stop_arm, "stop_rc": chain["stop_rc"],
                           "chain_record": chain["path"],
                           "note": "the registration names this outcome; the arm bought 0 core-min"}
            continue
        refuse("G1", {"arm_absent_from_ledger": arm, "kernel_record_candidates": [],
                      "chain_outcome": outcome, "chain_stop_arm": stop_arm,
                      "chain_record_present": chain["present"],
                      "note": "absent from the ledger, no surviving container, and NOT accounted for "
                              "by a registered chain outcome -- this refusal is UNCHANGED from D6"})
    return {"chain": chain, "census": census,
            "arms_ran": [a for a in arms_required if census[a]["state"] == "RAN"],
            "arms_not_run": [a for a in arms_required if census[a]["state"] == "NOT_RUN"]}


def producer_ran(census, artefact):
    """Did the arm that WRITES this artefact run?  (None = artefact not in the
    registered producer table, which is itself a refusal at the call site.)"""
    arm = ARTEFACT_PRODUCER.get(os.path.basename(artefact))
    if arm is None:
        return None, None
    return arm, bool(census.get(arm, {}).get("state") == "RAN")


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


def g_completion(base, rows_by_arm, arms_required, cen):
    out = {"arms_required": arms_required, "arms": {}, "rc_failures": [], "terminal_failures": [],
           "age_failures": [], "not_measured": {}, "staged_inputs": {},
           "arms_ran": list(cen["arms_ran"]), "arms_not_run": {},
           "chain_record": {k: v for k, v in cen["chain"].items() if k != "text_tail"}}
    for arm in arms_required:
        if cen["census"][arm]["state"] == "NOT_RUN":
            # NAMED, in the artefact, with its reason.  NOT a refusal, and NOT a pass.
            out["arms_not_run"][arm] = dict(cen["census"][arm])
            out["arms"][arm] = {"state": "NOT_RUN", "reason": cen["census"][arm]["reason"],
                                "stop_arm": cen["census"][arm].get("stop_arm"),
                                "stop_rc": cen["census"][arm].get("stop_rc"),
                                "core_min": 0.0, "arm_kind": ARM_KIND.get(arm),
                                "workdir": ARM_DIR.get(arm), "workdir_reason": ARM_DIR_REASON.get(arm)}
            continue
        r = rows_by_arm.get(arm)
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
    # THE DISTINCTION THIS GRADER EXISTS TO MAKE.  `complete` means every
    # registered arm ran AND every clause held.  `ran_clean` means every arm
    # that RAN held every clause.  A chain stop makes the first False and can
    # leave the second True, and the two are NEVER the same verdict.
    out["ran_clean"] = bool(not out["rc_failures"] and not out["terminal_failures"]
                            and not out["age_failures"])
    out["all_arms_ran"] = bool(not out["arms_not_run"])
    out["pass"] = bool(out["ran_clean"] and out["all_arms_ran"])
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


NOT_RUN_SENTINEL = "ARM_DID_NOT_RUN"


def gate_no_input(gate, artefact, cen):
    """The registered NOT A RESULT for a gate whose input arm never ran."""
    arm, ran = producer_ran(cen["census"], artefact)
    if arm is None:
        refuse(gate, {"artefact_has_no_registered_producer": artefact,
                      "registered": sorted(ARTEFACT_PRODUCER)})
    return {"verdict": "NOT A RESULT", "reason": NOT_RUN_SENTINEL, "gate": gate,
            "artefact": os.path.basename(artefact), "producing_arm": arm,
            "arm_state": cen["census"].get(arm, {}),
            "note": "the arm that writes this artefact did not run, so this gate has NO INPUT. "
                    "That is NOT a GATE FAIL -- nothing was measured that could fail."}


def input_absent_because_arm_not_run(path, cen):
    arm, ran = producer_ran(cen["census"], path)
    return bool(arm is not None and ran is False)


def read_history(base, cen):
    p = os.path.join(base, "O_mp", "d6r_major_history.json")
    if not os.path.isfile(p):
        if input_absent_because_arm_not_run(p, cen):
            return None
        refuse("G-D6R", {"absent": p, "producing_arm": ARTEFACT_PRODUCER["d6r_major_history.json"],
                         "note": "the producing arm RAN; an absent product is a real failure"})
    h = json.load(open(p))
    for k in ["J"] + ["CD_" + pt for pt in POINTS] + ["CL_" + pt for pt in POINTS]:
        if k not in h or not h[k]:
            refuse("G-D6R", {"history_key_absent_or_empty": k, "path": p})
    return h


def read_ref_off(base, cen):
    p = os.path.join(base, "REF_off", "d6r_ref_off.json")
    if not os.path.isfile(p):
        if input_absent_because_arm_not_run(p, cen):
            return None
        refuse("G-D6R-1", {"absent": p, "producing_arm": ARTEFACT_PRODUCER["d6r_ref_off.json"],
                           "note": "the producing arm RAN; an absent product is a real failure"})
    r = json.load(open(p))
    for pt in POINTS:
        if pt not in r.get("points", {}) or "CD" not in r["points"][pt]:
            refuse("G-D6R-1", {"ref_off_point_absent": pt, "path": p})
    return r


def g_points(hist, ref, cen):
    if hist is None or ref is None:
        miss = os.path.join("O_mp", "d6r_major_history.json") if hist is None else os.path.join("REF_off", "d6r_ref_off.json")
        g = gate_no_input("G-D6R-1", miss, cen)
        g["verdicts"] = {pt: "NOT A RESULT" for pt in POINTS}
        g["per_point"] = {pt: {"verdict": "NOT A RESULT", "reason": NOT_RUN_SENTINEL} for pt in POINTS}
        g["all_pass"] = False
        return g
    per = {}
    for pt in POINTS:
        cd_mp = _f(hist["CD_" + pt][-1])
        cd_ref = _f(ref["points"][pt]["CD"])
        per[pt] = {"CD_mp": cd_mp, "CD_ref_off": cd_ref, "gain": cd_ref - cd_mp,
                   "CL_mp_final": _f(hist["CL_" + pt][-1]), "CL_ref": _f(ref["points"][pt]["CL"]),
                   "verdict": "PASS" if cd_mp <= cd_ref else "GATE FAIL"}
    return {"per_point": per, "all_pass": all(p["verdict"] == "PASS" for p in per.values()),
            "verdicts": {pt: per[pt]["verdict"] for pt in POINTS}}


def g_composite(hist, cen, band=REDUCTION_BAND_PCT):
    if hist is None:
        g = gate_no_input("G-D6R-2", os.path.join("O_mp", "d6r_major_history.json"), cen)
        g.update({"reduction_pct": None, "band_pct": list(band), "J0": None, "Jf": None, "n_major": None})
        return g
    j0, jf = _f(hist["J"][0]), _f(hist["J"][-1])
    if j0 == 0.0:
        refuse("G-D6R-2", {"J0_zero": True})
    red = (j0 - jf) / j0 * 100.0
    ok = band[0] <= red <= band[1]
    return {"J0": j0, "Jf": jf, "reduction_pct": red, "band_pct": list(band), "n_major": len(hist["J"]),
            "verdict": "PASS" if ok else "GATE FAIL"}


def g_price(base, hist, d4_o_dir, cen, band=PRICE_BAND):
    if hist is None:
        g = gate_no_input("G-D6R-3", os.path.join("O_mp", "d6r_major_history.json"), cen)
        g.update({"price": None, "band": list(band), "CD_f_D4": None, "CD_cl05_mp": None,
                  "planted_control": {"skipped": "no input to compare against; the control plants "
                                                 "into D4's reference and is driven whenever the gate is"}})
        return g
    ref = os.path.join(d4_o_dir, "opt_IPOPT.txt")
    ctrl = planted_zero_control(ref, os.path.join(base, "grader_controls"))
    r = read_ipopt(ref, "G-D6R-3")
    if abs(r["objective"] - CD_F_D4_RECORDED) > 1.0e-15:
        refuse("G-D6R-3", {"d4_reference_changed": r["objective"], "recorded": CD_F_D4_RECORDED, "path": ref})
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


def g_fd(base, cen):
    path = os.path.join(base, "O_mp", "d6r_fd_endpoint.json")
    if not os.path.isfile(path):
        if input_absent_because_arm_not_run(path, cen):
            g = gate_no_input("G-D6R-4", path, cen)
            g.update({"components": [], "n_planned": 0, "sign_flips": 0,
                      "pathology_NOT_A_RESULT": False, "aggregate_rel_err_pct": None,
                      "aggregate_pass": False})
            return g
        refuse("G-D6R-4", {"absent": path, "producing_arm": ARTEFACT_PRODUCER["d6r_fd_endpoint.json"],
                           "note": "the producing arm RAN; an absent product is a real failure"})
    fd = json.load(open(path))
    if fd.get("components_requested") != COMPONENTS_REGISTERED:
        refuse("G-D6R-4", {"components_not_the_registered_five": fd.get("components_requested")})
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


def g_caps(rows_by_arm, cen):
    """CAP DISCIPLINE ACROSS FRAMES (D6-CAP-FRAME-1, L-371).

    The cap is ENFORCED by `timeout` inside the container and GRADED on the
    host bracket T0..T1.  D6 graded one frame against the other and an arm that
    obeyed its deadline exactly recorded 2000.533 against a 2000.0 cap.  Here
    BOTH clocks are read and BOTH limbs bind:
      within_cap        host bracket core_min <= the registered cap
      deadline_frame    container kernel wall <= TMO + the TERM->KILL grace
      frame_gap         host - container <= FRAME_ALLOWANCE_S - KILL_GRACE_S
    An absent container clock is INFRASTRUCTURE (L-342): the frame limbs go
    NOT_MEASURED and the gate falls back to the host bracket alone, which is
    the STRICTER reading -- the fallback can never turn a failing cap into a
    pass.  Arms that did not run bought 0 core-min and are named, not graded."""
    per, total = {}, 0.0
    for arm, r in rows_by_arm.items():
        cap = CAPS.get(arm)
        if cap is None:
            refuse("G10", {"arm_without_registered_cap": arm})
        tmo = TMO_REGISTERED_S[arm]
        cw = r.get("container_wall_s")
        fa = r.get("frame_allowance_s")
        row = {"core_min": r["core_min"], "cap": cap, "host_wall_s": r["wall_s"],
               "within_cap": bool(r["core_min"] <= cap + 1e-9),
               "predicted": PREDICTED_CORE_MIN.get(arm),
               "ratio_actual_over_predicted": r["core_min"] / PREDICTED_CORE_MIN[arm],
               "deadline_registered_s": tmo, "frame_allowance_s_registered": FRAME_ALLOWANCE_S,
               "container_wall_s": (cw if cw is not None else NOT_MEASURED),
               "cap_equals_registered": bool(abs(r["cap_core_min"] - cap) < 1e-9
                                             and abs(r["enforced_core_min"] - cap) <= 0.02)}
        if cw is None:
            row.update({"frame_limbs_binding": False, "frame_gap_s": NOT_MEASURED,
                        "deadline_frame_pass": NOT_MEASURED,
                        "frame_gap_within_allowance": NOT_MEASURED,
                        "frame_allowance_matches_registered": NOT_MEASURED})
        else:
            gap = r["wall_s"] - cw
            row.update({"frame_limbs_binding": True, "frame_gap_s": gap,
                        "deadline_frame_pass": bool(cw <= tmo + KILL_GRACE_S),
                        "frame_gap_within_allowance": bool(gap <= FRAME_ALLOWANCE_S - KILL_GRACE_S),
                        "frame_allowance_matches_registered":
                            bool(fa is not None and abs(fa - FRAME_ALLOWANCE_S) <= 1e-9)})
        per[arm] = row
        total += r["core_min"]

    def limbs_ok(x):
        base_ok = x["within_cap"] and x["cap_equals_registered"]
        if not x["frame_limbs_binding"]:
            return bool(base_ok)
        return bool(base_ok and x["deadline_frame_pass"] and x["frame_gap_within_allowance"]
                    and x["frame_allowance_matches_registered"])

    ok = bool(per) and all(limbs_ok(v) for v in per.values()) and total <= ITEM_CEILING_CORE_MIN
    inv = {a: round((TMO_REGISTERED_S[a] + FRAME_ALLOWANCE_S) * RANKS / 60.0, 6) for a in CAPS}
    return {"per_arm": per, "total_core_min": round(total, 3), "ceiling": ITEM_CEILING_CORE_MIN,
            "arms_not_run_bought_zero": list(cen["arms_not_run"]),
            "frame_note": "cap ENFORCED in the container; GRADED on the host bracket; "
                          "(deadline + allowance) * ranks / 60 INVERTS to the registered cap",
            "deadline_plus_allowance_inverts_to_cap": inv,
            "inversion_ok": all(abs(inv[a] - CAPS[a]) <= 0.02 for a in CAPS),
            "verdict": "PASS" if ok else "GATE FAIL"}


# ===========================================================================
# G-D6R-OPT -- THE OPTIMISER'S OWN OUTCOME, AND A STALL IS NOT A CAP HIT.
# DAFOAM_CHARTER section 9: an optimiser stopped by a wall clock, an iteration
# cap or a budget is GATE REACHED where a registered intermediate threshold was
# met and NOT A RESULT otherwise -- NEVER PASS.  D6 did not merely run slow: at
# tol 1e-5 it printed 548 `Cutting back alpha due to evaluation error` over 64
# majors, took 7 restoration majors, and its dual infeasibility WORSENED from
# 5.78e-04 at major 58 to 1.14e-03 at major 64.  That is a STALL, and it is a
# different fact about the problem than "the clock ran out".
# THE LADDER IS ORDERED AND THE ORDER IS REGISTERED.  STALLED is tested BEFORE
# ITERATION_CAP, so a stalled run that also exhausts its iterations is reported
# as a STALL -- the more informative label, and the one that cannot flatter.
# ===========================================================================
MAJOR_ROW_RE = re.compile(r"^\s*(?P<n>\d+)(?P<rest>r?)\s+(?P<obj>[-+0-9.eE]+)\s+"
                          r"(?P<inf_pr>[-+0-9.eE]+)\s+(?P<inf_du>[-+0-9.eE]+)\s", re.M)
CUTBACK_TOKEN = "Cutting back alpha"


def g_opt_outcome(base, cen, rows_by_arm):
    art = os.path.join(base, "O_mp", "opt_IPOPT.txt")
    if cen["census"].get("O_mp", {}).get("state") != "RAN":
        g = gate_no_input("G-D6R-OPT", art, cen)
        g["outcome"] = None
        return g
    if not os.path.isfile(art):
        refuse("G-D6R-OPT", {"absent": art, "note": "O_mp ran; its optimiser log is a product"})
    txt = open(art, errors="replace").read()
    ip = read_ipopt(art, "G-D6R-OPT")
    majors = [(int(m.group("n")), bool(m.group("rest")), float(m.group("inf_du")))
              for m in MAJOR_ROW_RE.finditer(txt)]
    n_major = (majors[-1][0] if majors else 0)
    n_restoration = sum(1 for _, r, _ in majors if r)
    cutbacks = txt.count(CUTBACK_TOKEN)
    cpm = (cutbacks / float(n_major)) if n_major else None
    inf_du_last = (majors[-1][2] if majors else None)
    tail_idx = int(round(STALL_TAIL_FRACTION * n_major)) if n_major else None
    inf_du_tail = None
    if tail_idx is not None:
        for n, _, v in majors:
            if n >= tail_idx:
                inf_du_tail = v
                break
    s1 = bool(cpm is not None and cpm >= STALL_CUTBACKS_PER_MAJOR)
    s2 = bool(inf_du_last is not None and inf_du_tail is not None and inf_du_last >= inf_du_tail)
    # the DEADLINE limb reads the arm's own kernel record, not the log
    r = rows_by_arm.get("O_mp", {})
    tmo = TMO_REGISTERED_S["O_mp"]
    cw = r.get("container_wall_s")
    deadline_fired = bool(r.get("rc") == 124 or (cw is not None and cw >= tmo))
    if deadline_fired:
        outcome = "DEADLINE"
    elif (not ip["optimal"]) and s1 and s2:
        outcome = "STALLED"
    elif ip["exit"].startswith("EXIT: Maximum Number of Iterations Exceeded"):
        outcome = "ITERATION_CAP"
    elif ip["optimal"]:
        outcome = "CONVERGED"
    else:
        outcome = "UNCLASSIFIED"
    if outcome not in OPT_OUTCOMES:
        refuse("G-D6R-OPT", {"outcome_not_registered": outcome, "registered": list(OPT_OUTCOMES)})
    return {"outcome": outcome, "exit_line": ip["exit"], "n_major": n_major,
            "max_iter_registered": MAX_ITER_REGISTERED,
            "n_restoration_majors": n_restoration, "cutbacks": cutbacks,
            "cutbacks_per_major": cpm, "stall_threshold_cutbacks_per_major": STALL_CUTBACKS_PER_MAJOR,
            "inf_du_last": inf_du_last, "inf_du_at_tail_start": inf_du_tail,
            "tail_start_major": tail_idx, "S1_line_search_failing": s1,
            "S2_dual_infeasibility_not_decreasing": s2,
            "deadline_fired": deadline_fired, "deadline_registered_s": tmo,
            "container_wall_s": (cw if cw is not None else NOT_MEASURED),
            "ladder": "DEADLINE > STALLED > ITERATION_CAP > CONVERGED (registered order)"}


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
    return {"per_arm": per, "arms_graded": sorted(per),
            "arms_not_graded_because_they_did_not_run":
                sorted(set(ARMS_REQUIRED) - set(per)),
            "verdict": "PASS" if ok else "GATE FAIL"}


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
    return {"per_arm": per, "delivered_not_measured": nm, "arms_graded": sorted(per),
            "arms_not_graded_because_they_did_not_run":
                sorted(set(ARMS_REQUIRED) - set(per)),
            "verdict": "PASS" if ok else "GATE FAIL"}


def compose(g1, gp, gc, gpr, gfd, gopt, g10, g9, g12):
    """THE REGISTERED VERDICT LADDER (PREREGISTRATION.md section 3d), in order.
    A NOT A RESULT can only turn a PASS / GATE REACHED / GATE FAIL INTO a
    NOT A RESULT, never the reverse."""
    gates = {"G1_completion": ("PASS" if g1["pass"] else "NOT A RESULT"),
             "G-D6R-1_cl04": gp["verdicts"]["cl04"], "G-D6R-1_cl05": gp["verdicts"]["cl05"],
             "G-D6R-1_cl06": gp["verdicts"]["cl06"], "G-D6R-2_composite": gc["verdict"],
             "G-D6R-3_price": gpr["verdict"], "G-D6R-4_fd": gfd["verdict"],
             "G-D6R-OPT_optimiser": ("NOT A RESULT" if gopt.get("outcome") in (None, "DEADLINE", "STALLED",
                                                                              "UNCLASSIFIED")
                                     else ("GATE REACHED" if gopt["outcome"] == "ITERATION_CAP" else "PASS")),
             "G9_toolchain": g9["verdict"], "G10_caps": g10["verdict"], "G12_placement": g12["verdict"]}
    reasons = []
    # 1. an arm that RAN failed a completion clause
    if not g1["ran_clean"]:
        reasons.append("a completion clause failed on an arm that ran")
    # 2. a registered arm never ran -- NAMED, and the item cannot be PASS
    if not g1["all_arms_ran"]:
        reasons.append("registered arms did not run: %s" % ",".join(sorted(g1["arms_not_run"])))
    # 3. the optimiser stopped in a way that is not a design point
    if gopt.get("outcome") in (None, "DEADLINE", "STALLED", "UNCLASSIFIED"):
        reasons.append("optimiser outcome %s" % gopt.get("outcome"))
    # 4. the registered pathologies
    if gfd.get("pathology_NOT_A_RESULT"):
        reasons.append("G-D6R-4 sign-flip pathology")
    if gpr["verdict"] == "NOT A RESULT" and gpr.get("reason") != NOT_RUN_SENTINEL:
        reasons.append("G-D6R-3 negative price (a finding about D4)")
    # 5. any gate with no input
    for k, v in gates.items():
        if v == "NOT A RESULT" and k not in ("G1_completion", "G-D6R-OPT_optimiser"):
            reasons.append("%s NOT A RESULT" % k)
    if reasons:
        item = "NOT A RESULT"
    elif any(v == "GATE FAIL" for v in gates.values()):
        item = "GATE FAIL"
    elif gopt["outcome"] == "ITERATION_CAP":
        # DAFOAM_CHARTER section 9: stopped by its own iteration cap with the
        # registered intermediate threshold (G-D6R-2) met -- NEVER PASS.
        item = "GATE REACHED" if gc["verdict"] == "PASS" else "NOT A RESULT"
    else:
        item = "PASS"
    if item not in VOCAB:
        refuse("VOCAB", {"item": item})
    return {"gates": gates, "item": item, "not_a_result_reasons": reasons,
            "arms_not_run": dict(g1["arms_not_run"]),
            "optimiser_outcome": gopt.get("outcome"),
            "not_measured_named": dict(g1.get("not_measured", {})),
            "per_point_verdicts_reported_as_three": gp["verdicts"]}


def score_predictions(base, gc, gp, gpr, g10, g1, gopt, cen):
    """SCORED HIT/MISS/NOT A RESULT, never adjusted after the fact."""
    out = gopt.get("outcome")
    n = gopt.get("n_major")
    p = {"P1": {"pred": "the optimiser does NOT converge in max_iter 80; outcome in "
                        "{ITERATION_CAP, STALLED}, POINT = STALLED.  Registered honestly against "
                        "D6's own measurement: 548 alpha cutbacks over 64 majors, 7 restoration "
                        "majors, dual infeasibility WORSENING 5.78e-04 (major 58) -> 1.14e-03 "
                        "(major 64) against tol 1e-5.  A MISS here is GOOD NEWS.",
                "obs": {"outcome": out, "n_major": n, "exit": gopt.get("exit_line")},
                "score": ("NOT A RESULT" if out is None else
                          ("HIT" if out in ("ITERATION_CAP", "STALLED") else "MISS"))},
         "P2": {"pred": "composite reduction [15,40] %, point 22 %", "obs": gc.get("reduction_pct"),
                "score": ("NOT A RESULT" if gc["verdict"] == "NOT A RESULT" else
                          ("HIT" if gc["verdict"] == "PASS" else "MISS"))},
         "P3": {"pred": "price CD_0.5(mp) - 2.1125978e-02 in [0, 1.0e-3], point +3.0e-4",
                "obs": gpr.get("price"),
                "score": ("NOT A RESULT" if gpr["verdict"] == "NOT A RESULT" else
                          ("HIT" if gpr["verdict"] == "PASS" else "MISS"))},
         "P4": {"pred": "off-design gains > 0 (0.6 point +8.0e-4; 0.4 point +2.0e-4)",
                "obs": {k: gp["per_point"].get(k, {}).get("gain") for k in ("cl06", "cl04")},
                "score": ("NOT A RESULT" if gp["verdicts"]["cl04"] == "NOT A RESULT" else
                          ("HIT" if (gp["per_point"]["cl06"]["gain"] > 0 and
                                     gp["per_point"]["cl04"]["gain"] > 0) else "MISS"))},
         "P5": {"pred": "O_mp cost [1900, 2900] core-min, point 2500.6 (80 x 31.258 MEASURED, C-188)",
                "obs": g10["per_arm"].get("O_mp", {}).get("core_min"),
                "score": ("NOT A RESULT" if "O_mp" not in g10["per_arm"] else
                          ("HIT" if P5_BAND[0] <= g10["per_arm"]["O_mp"]["core_min"] <= P5_BAND[1]
                           else "MISS"))},
         "P6": {"pred": "all three per-point verdicts PASS", "obs": gp["verdicts"],
                "score": ("NOT A RESULT" if any(v == "NOT A RESULT" for v in gp["verdicts"].values())
                          else ("HIT" if gp["all_pass"] else "MISS"))},
         "P7": {"pred": "ALREADY ANSWERED BY D6 AND NOT RE-BOUGHT: OOMKilled=false after 8 h 20 m at "
                        "np=4 in a 20g cgroup, so multipoint IS memory-feasible on this box "
                        "(C-188; D6 ledger inspect(exit,oomkilled)=[124 false]).  D6R scores it "
                        "ONLY as a regression check on an answered question.",
                "obs": {"any_oom_killed": g1["any_oom_killed"], "answered_by": "D6 / C-188"},
                "score": "MISS" if g1["any_oom_killed"] else "HIT"},
         "P8": {"pred": "THE REPAIR'S OWN FALSIFIER: the chain COMPLETES -- all four arms run, "
                        "because the optimiser's own max_iter (80 x 31.258 = 2500.6 core-min) "
                        "binds BEFORE the container deadline (2894.0 core-min of compute window).  "
                        "D6's chain died at O_mp on rc=124 and bought nothing else.",
                "obs": {"chain_outcome": cen["chain"]["outcome"],
                        "arms_not_run": sorted(g1["arms_not_run"])},
                "score": ("HIT" if (cen["chain"]["outcome"] == "COMPLETE" and not g1["arms_not_run"])
                          else "MISS")}}
    return p


def launcher_mapping_check():
    """ARM_DIR IS ASSERTED AGAINST THE LAUNCHER'S OWN BYTES, not merely stated.
    F_mp is registered to run inside O_mp/; if the launcher ever stops setting
    that working directory the grader would be looking in the wrong place, and
    a mapping nobody checks is a mapping that drifts."""
    lp = os.path.join(os.path.dirname(os.path.abspath(__file__)), LAUNCHER_NAME)
    if not os.path.isfile(lp):
        return {"launcher_present": False, "path": lp, "checked": False,
                "note": "launcher not beside the grader; the mapping is STATED but UNCHECKED"}
    txt = open(lp, errors="replace").read()
    ok = LAUNCHER_F_MP_WORKDIR_LINE in txt
    if not ok:
        refuse("ARM_DIR", {"launcher_does_not_set_F_mp_workdir": LAUNCHER_F_MP_WORKDIR_LINE,
                           "launcher": lp,
                           "note": "ARM_DIR maps F_mp -> O_mp; the launcher must agree"})
    return {"launcher_present": True, "path": lp, "md5": md5_of(lp), "checked": True,
            "F_mp_workdir_line_found": LAUNCHER_F_MP_WORKDIR_LINE,
            "ARM_DIR": dict(ARM_DIR), "ARM_DIR_REASON": dict(ARM_DIR_REASON),
            "ARTEFACT_PRODUCER": dict(ARTEFACT_PRODUCER)}


def grade(base=BASE, d4_o_dir=D4_O_DIR, arms=None):
    arms = arms or list(ARMS_REQUIRED)
    lmap = launcher_mapping_check()
    rows = read_ledger(os.path.join(base, "ledger.txt"))
    rows_by_arm = {}
    for r in rows:
        # A SECOND ROW FOR ONE ARM IS TWO RECORDS FOR ONE RUN.  D6's grader
        # silently kept the LAST; the family's other graders refuse
        # (REFIRE_RUNBOOK.md section 1, duplicate_arm_row).  D6R refuses too.
        # This is a STRENGTHENING and can only turn a pass into a stop.
        if r["ARM"] in rows_by_arm:
            refuse("ledger", {"duplicate_arm_row": r["ARM"],
                              "note": "two ledger rows for one arm; the grader will not guess between them"})
        rows_by_arm[r["ARM"]] = r
    rows_by_arm = {a: rows_by_arm[a] for a in arms if a in rows_by_arm}
    cen = arm_census(base, rows_by_arm, arms)
    g1 = g_completion(base, rows_by_arm, arms, cen)
    hist = read_history(base, cen)
    ref = read_ref_off(base, cen)
    gp = g_points(hist, ref, cen)
    gc = g_composite(hist, cen)
    gpr = g_price(base, hist, d4_o_dir, cen)
    gfd = g_fd(base, cen)
    gopt = g_opt_outcome(base, cen, rows_by_arm)
    g10 = g_caps(rows_by_arm, cen)
    g9 = g_toolchain(base, rows_by_arm)
    g12 = g_placement(rows_by_arm)
    comp = compose(g1, gp, gc, gpr, gfd, gopt, g10, g9, g12)
    preds = score_predictions(base, gc, gp, gpr, g10, g1, gopt, cen)
    return {"item": "D6R", "grader_md5": md5_of(__file__), "base": base, "verdict": comp["item"],
            "gates": comp["gates"], "not_a_result_reasons": comp["not_a_result_reasons"],
            "arm_census": cen["census"], "arms_ran": cen["arms_ran"],
            "arms_not_run": cen["arms_not_run"], "chain_record": cen["chain"],
            "per_point_verdicts": comp["per_point_verdicts_reported_as_three"],
            "optimiser_outcome": comp["optimiser_outcome"],
            "not_measured_named": comp["not_measured_named"], "G1": g1, "G-D6R-1": gp,
            "G-D6R-2": gc, "G-D6R-3": gpr, "G-D6R-4": gfd, "G-D6R-OPT": gopt,
            "G10": g10, "G9": g9, "G12": g12, "predictions": preds,
            "arm_dir_mapping": lmap,
            "ref_off_consistency_CD_cl05_minus_D4": (ref.get("consistency_CD_cl05_minus_D4_CD_f")
                                                     if ref else NOT_MEASURED),
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
        sys.stdout.write("D6R_GRADE REFUSED %s\n" % exc)
        return 2
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "d6r_grade_verdict_%s.json" % time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))
    json.dump(res, open(out, "w"), indent=1, sort_keys=True, default=str)
    nm = "; ".join("%s:%s" % (k, ",".join(v)) for k, v in sorted(res["not_measured_named"].items())) or "none"
    sys.stdout.write("D6R_VERDICT %s | opt=%s | ran=%s | NOT_RUN=%s | per-point %s | gates %s "
                     "| NOT_MEASURED[%s] | out=%s\n"
                     % (res["verdict"], res["optimiser_outcome"], ",".join(res["arms_ran"]) or "none",
                        ",".join(res["arms_not_run"]) or "none",
                        json.dumps(res["per_point_verdicts"], sort_keys=True),
                        json.dumps(res["gates"], sort_keys=True), nm, out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
