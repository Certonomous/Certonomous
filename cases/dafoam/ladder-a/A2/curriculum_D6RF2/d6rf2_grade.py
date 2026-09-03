#!/usr/bin/env python3
"""Curriculum D6RF -- THE FROZEN GRADING PATH for `F_mp` and `REF_off`.

This file IS the grading path fixed at the pre-registration commit
(`CLAUDE.md` rule 2).  Its md5 is pinned in `PREREGISTRATION.md` section 7 and
in the queue row; it verifies at execution that its own bytes on disk equal the
committed blob at HEAD, and it REFUSES (exit 2) if they do not.

VOCABULARY.  `PASS` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING` and
no other word (`CLAUDE.md` rule 1).  `GATE REACHED` is DELIBERATELY ABSENT: it
labels an optimiser stopped by a wall clock, an iteration cap or a budget
(`DAFOAM_CHARTER.md` section 9), and THIS ITEM RUNS NO OPTIMISER.  A word that
can never fire is not registered.

REFUSES RATHER THAN DEGRADES (exit 2), as this family's comparators do.

THE PLANTED-ZERO CONTROLS (`CLAUDE.md` rule 3) are not optional decoration and
are not skippable: `G-FD` and `G-PRICE` each plant a known perturbation into a
COPY of the artefact they read, read it back FROM DISK through the SAME reader,
and REFUSE if the reader cannot see it.  Both also assert the unperturbed
original is byte-unchanged.  A zero -- or an agreement -- from a reader not
shown able to see a non-zero is not evidence.

L-342 FIELD CLASSES.  Absent INFRASTRUCTURE (a delivered-cores sample, a
container kernel clock) is reported `NOT_MEASURED` beside the verdict and voids
only the claim that depends on it.  Absent PHYSICS (a log, an rc, a registered
artefact whose producing arm ran) REFUSES.  Bookkeeping never voids physics.
"""
import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys

# ============================ REGISTERED CONSTANTS ==========================
# Every value in this block is frozen by PREREGISTRATION.md before compute.
ITEM = "D6RF2"
ARMS = ["F_mp", "REF_off"]
ARM_KIND = {"F_mp": "SOLVER", "REF_off": "SCRIPT"}
ARM_DIR = {"F_mp": "F_mp", "REF_off": "REF_off"}

RANKS = 4
CAPS = {"F_mp": 480.0, "REF_off": 190.0}
TMO = {"F_mp": 7110, "REF_off": 2760}
FRAME_ALLOWANCE_S = 90
KILL_GRACE_S = 60
FRAME_GAP_ALLOWANCE_S = FRAME_ALLOWANCE_S - KILL_GRACE_S      # 30
CAP_INVERSION_TOL_CORE_MIN = 0.02

CPUSET = "2,3,4,14"
DELIVERED_MIN = 3.0
MEMORY = "20g"

DIGEST_PATCHED = ("sha256:2927768a16acdea0330180fff95c8879"
                  "c1dda9efcf6028728523b7dee30f6d35")
DIGEST_SHIPPED = ("sha256:9d45679d55fd47f5ca7afd99cabb86c7"
                  "c2729cf2acf34c438eb33af5290f07fc")     # NAMED UNBOUGHT
IDWARP_SO_MD5 = "85f59e87253e0a71a813f64ca6e4c425"

# FD bright line -- band D, inherited BY CITATION from D6R PREREGISTRATION.md
# section 3e (VERIFICATION_CHARTER.md section 7 through D6 section 3 and
# DAFOAM_CHARTER.md section 2).  NOT re-derived here.
FD_BAND_PCT = 5.0
AGG_BAND_PCT = 5.0
PLATEAU_TOL_PCT = 10.0
SIGN_FLIP_PATHOLOGY = 2

# D4's PATCHED single-point optimum, re-read from ITS OWN artefact and refused
# if it has moved.
CD_F_D4_RECORDED = 2.1125978108239574e-02
D4_OPT_IPOPT = ("/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/"
                "O/opt_IPOPT.txt")
PRICE_BAND = (0.0, 1.0e-3)

# REPORTED, NOT GATED (Sanaa 2026-09-03 ~20:00Z): the composite reduction is a
# number about an optimisation that exited on a non-finite objective.
RED_BAND_PCT = (15.0, 40.0)

POINTS = ["cl04", "cl05", "cl06"]
CL_TARGETS = {"cl04": 0.4, "cl05": 0.5, "cl06": 0.6}

PLANT = 1.234e-03                    # the planted-zero perturbation, registered
PLANT_REL_TOL = 1.0e-9

REGISTERED_CHAIN_OUTCOMES = ("STOPPED_AT_FIRST_NONZERO", "STOPPED_H5",
                             "BLOCKED_H5", "BLOCKED_AGGREGATE",
                             "REFUSED_ALREADY_BOUGHT", "ABORT")

ARTEFACT_PRODUCER = {
    "d6rf2_endpoint_dvs_PHYSICAL.json": "F_mp",
    "d6r_endpoint_dvs_DRIVERSCALED.json": "F_mp",
    "d6r_endpoint_dvs.json": "F_mp",
    "d6r_major_history.json": "F_mp",
    "d6r_fd_endpoint.json": "F_mp",
    "d4_endpoint_dvs_PHYSICAL.json": "REF_off",
    "d4_endpoint_dvs.json": "REF_off",
    "d6r_ref_off.json": "REF_off",
}
REGISTERED_PRODUCTS = {
    "F_mp": ["d6rf2_endpoint_dvs_PHYSICAL.json", "d6r_endpoint_dvs_DRIVERSCALED.json",
             "d6r_endpoint_dvs.json", "d6r_major_history.json",
             "d6r_fd_endpoint.json"],
    "REF_off": ["d4_endpoint_dvs_PHYSICAL.json", "d4_endpoint_dvs.json",
                "d6r_ref_off.json"],
}
TERMINAL_STATEMENT = "Finalising parallel run"
# ===========================================================================

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir, os.pardir,
                                    os.pardir, os.pardir))


class Refusal(Exception):
    pass


def refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail},
                             sort_keys=True, default=str)[:4000])


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def _f(x):
    """A repr()'d float from an artefact, or a float, or REFUSE."""
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        try:
            return float(x)
        except ValueError:
            refuse("float_parse", {"value": x[:120]})
    refuse("float_parse", {"type": type(x).__name__})


# ------------------------------------------------------------ freeze check
def freeze_check(paths):
    """The frozen file IS the file that ran: disk == git blob at HEAD."""
    out = {}
    for rel in paths:
        disk = os.path.join(REPO, rel)
        if not os.path.isfile(disk):
            refuse("FREEZE", {"absent_on_disk": rel})
        on_disk = md5_of(disk)
        try:
            blob = subprocess.run(["git", "-C", REPO, "cat-file", "blob",
                                   "HEAD:%s" % rel],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  check=True).stdout
        except Exception as e:                                   # noqa: BLE001
            refuse("FREEZE", {"git_cat_file_failed": rel, "error": repr(e)[:300]})
        committed = hashlib.md5(blob).hexdigest()
        out[rel] = {"on_disk_md5": on_disk, "committed_blob_md5_HEAD": committed,
                    "disk_equals_committed_blob": on_disk == committed}
        if on_disk != committed:
            refuse("FREEZE", {"path": rel, "on_disk_md5": on_disk,
                              "committed_blob_md5_HEAD": committed,
                              "note": "the grading path is fixed at the "
                                      "pre-registration commit (rule 2)"})
    return out


# ------------------------------------------------------------ ledger reader
_TOK = re.compile(r'(?P<k>[A-Za-z_][\w(),]*)=(?P<v>\[[^\]]*\]|\S*)')


def parse_ledger(path):
    """Return {arm: row-dict} plus the raw extra lines.  REFUSES on a duplicate
    arm row -- D6's grader silently kept the last of two, and a strengthening
    can only turn a pass into a stop."""
    if not os.path.isfile(path):
        refuse("LEDGER", {"absent": path})
    rows, extra, seen = {}, [], []
    with open(path, errors="replace") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.startswith("ARM="):
                extra.append(line)
                continue
            rec = {m.group("k"): m.group("v") for m in _TOK.finditer(line)}
            arm = rec.get("ARM")
            seen.append(arm)
            if arm in rows:
                refuse("LEDGER", {"duplicate_arm_row": arm, "arms_seen": seen,
                                  "note": "refused, not last-wins"})
            rec["_raw"] = line
            rows[arm] = rec
    return rows, extra


def read_chain_status(path):
    """REFUSES on multiplicity: exactly one `chain=started`, at most one
    terminal outcome (D6R AMENDMENT 1)."""
    if not os.path.isfile(path):
        return None
    started, terminal, arm_rc = [], [], {}
    with open(path, errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if line.startswith("chain=started"):
                started.append(line)
            elif line.startswith("chain="):
                terminal.append(line)
            elif line.startswith("arm="):
                m = re.match(r'arm=(\S+)\s+rc=(-?\d+)', line)
                if m:
                    arm_rc[m.group(1)] = int(m.group(2))
    if len(started) != 1:
        refuse("CHAIN_STATUS", {"n_chain_started": len(started),
                               "note": "a second fire into an existing root "
                                       "makes the census unreadable"})
    if len(terminal) > 1:
        refuse("CHAIN_STATUS", {"n_terminal_outcomes": len(terminal),
                               "lines": terminal})
    out = {"started": started[0], "arm_rc": arm_rc, "terminal": None,
           "outcome": None, "stop_arm": None, "stop_rc": None, "not_run": []}
    if terminal:
        t = terminal[0]
        out["terminal"] = t
        m = re.match(r'chain=(\S+)', t)
        out["outcome"] = m.group(1) if m else None
        m = re.search(r'\barm=(\S+)', t)
        out["stop_arm"] = m.group(1) if m else None
        m = re.search(r'\brc=(-?\d+)', t)
        out["stop_rc"] = int(m.group(1)) if m else None
        m = re.search(r'not_run=\[([^\]]*)\]', t)
        out["not_run"] = m.group(1).split() if m else []
    return out


# ------------------------------------------------------------- arm census
def arm_census(root, ledger_rows, chain):
    """1 ledger row -> RAN.  2 no row, chain accounts for the absence ->
    NOT_RUN with its reason.  3 otherwise REFUSE."""
    census = {}
    for arm in ARMS:
        if arm in ledger_rows:
            census[arm] = {"state": "RAN", "source": "ledger_row"}
            continue
        if chain and chain["outcome"] in REGISTERED_CHAIN_OUTCOMES \
                and arm in chain["not_run"]:
            census[arm] = {"state": "NOT_RUN",
                           "reason": "REGISTERED_CHAIN_%s" % chain["outcome"],
                           "stop_arm": chain["stop_arm"],
                           "stop_rc": chain["stop_rc"],
                           "chain_record": os.path.join(root, "STATUS.chain"),
                           "note": "the registration names this outcome; the "
                                   "arm bought 0 core-min"}
            continue
        refuse("CENSUS", {"arm": arm, "arm_absent_from_ledger": True,
                          "chain_outcome": (chain or {}).get("outcome"),
                          "chain_not_run": (chain or {}).get("not_run"),
                          "note": "COMPLETE accounts for nothing -- after a "
                                  "complete chain no arm may be missing"})
    return census


# ------------------------------------------------------------------- G1
def gate_g1(root, ledger_rows, census):
    res = {"gate": "G1_completion", "arms": {}, "all_arms_ran": True,
           "ran_clean": True, "not_measured": []}
    for arm in ARMS:
        st = census[arm]
        if st["state"] != "RAN":
            res["all_arms_ran"] = False
            res["arms"][arm] = {"state": "NOT_RUN", "reason": st.get("reason"),
                                "core_min": 0.0}
            continue
        row = ledger_rows[arm]
        a = {"state": "RAN", "arm_kind": ARM_KIND[arm]}
        rc = int(row.get("rc", "999"))
        insp = row.get("inspect(exit,oomkilled)", "[]").strip("[]").split()
        if len(insp) != 2:
            refuse("G1", {"arm": arm, "inspect_field_unreadable": row.get(
                "inspect(exit,oomkilled)")})
        kernel_rc, oom = int(insp[0]), insp[1]
        if kernel_rc != rc:
            refuse("G1", {"arm": arm, "harness_rc": rc, "kernel_rc": kernel_rc,
                          "note": "harness and kernel disagree on rc"})
        a["rc"] = rc
        a["kernel_rc"] = kernel_rc
        a["oomkilled"] = oom
        a["rc_clause_pass"] = (rc == 0)
        a["oom_clause_pass"] = (oom == "false")

        log = os.path.join(root, row.get("log", ""))
        if not os.path.isfile(log):
            refuse("G1", {"arm": arm, "log_absent": log,
                          "note": "a log is PHYSICS, not infrastructure"})
        a["log"] = log
        if ARM_KIND[arm] == "SOLVER":
            last = None
            with open(log, errors="replace") as fh:
                for line in fh:
                    s = line.strip()
                    if s:
                        last = s
            a["terminal_last_line"] = last
            a["terminal_clause_pass"] = (last == TERMINAL_STATEMENT)
        else:
            ok = [f for f in os.listdir(root)
                  if f.startswith(os.path.basename(log) + ".ok.")]
            a["ok_markers"] = ok
            a["terminal_clause_pass"] = (len(ok) == 1)

        # ---- the AGE GUARD (rule 4) -------------------------------------
        wd = os.path.join(root, ARM_DIR[arm])
        datum_file = os.path.join(wd, ".d4_age_datum")
        if not os.path.isfile(datum_file):
            refuse("G1", {"arm": arm, "age_datum_absent": datum_file,
                          "note": "without the datum the age guard cannot run, "
                                  "and the age guard is PHYSICS"})
        with open(datum_file) as fh:
            datum = float(fh.read().strip())
        ages, age_pass = {}, True
        for prod in REGISTERED_PRODUCTS[arm]:
            p = os.path.join(wd, prod)
            if not os.path.isfile(p):
                refuse("G1", {"arm": arm, "registered_product_absent": p,
                              "note": "the producing arm RAN, so an absent "
                                      "product refuses (D6's behaviour, kept)"})
            mt = os.stat(p).st_mtime
            ages[prod] = {"mtime": mt, "newer_than_datum": mt > datum}
            age_pass = age_pass and mt > datum
        a["age_datum"] = datum
        a["age_detail"] = ages
        a["age_clause_pass"] = age_pass

        a["core_min"] = _f(row.get("core_min", "nan"))
        a["wall_s"] = _f(row.get("wall_s", "nan"))
        a["ranks"] = int(row.get("ranks", "0"))
        a["clauses_all_pass"] = all([a["rc_clause_pass"], a["oom_clause_pass"],
                                     a["terminal_clause_pass"],
                                     a["age_clause_pass"]])
        if not a["clauses_all_pass"]:
            res["ran_clean"] = False
        res["arms"][arm] = a
    return res


# ---------------------------------------------------- G-CAPS / G9 / G12
def gate_caps(ledger_rows, census):
    res = {"gate": "G-CAPS", "arms": {}, "verdict": "PASS", "not_measured": []}
    for arm in ARMS:
        if census[arm]["state"] != "RAN":
            res["arms"][arm] = {"state": "NOT_RUN", "core_min": 0.0}
            continue
        row = ledger_rows[arm]
        cm = _f(row.get("core_min", "nan"))
        cap = CAPS[arm]
        a = {"core_min": cm, "cap_core_min": cap, "within_cap": cm <= cap}
        inv = (TMO[arm] + FRAME_ALLOWANCE_S) * RANKS / 60.0
        a["deadline_in_container_s"] = TMO[arm]
        a["cap_inversion_core_min"] = inv
        a["inversion_matches_cap"] = abs(inv - cap) <= CAP_INVERSION_TOL_CORE_MIN
        cw = row.get("container_wall_s")
        if cw in (None, "", "NOT_MEASURED"):
            a["container_wall_s"] = "NOT_MEASURED"
            a["deadline_frame_pass"] = "NOT_MEASURED"
            a["frame_gap_within_allowance"] = "NOT_MEASURED"
            res["not_measured"].append("%s/container_wall_s" % arm)
        else:
            cwv = _f(cw)
            a["container_wall_s"] = cwv
            a["deadline_frame_pass"] = cwv <= TMO[arm] + KILL_GRACE_S
            gap = _f(row.get("wall_s", "nan")) - cwv
            a["host_minus_container_s"] = gap
            a["frame_gap_within_allowance"] = gap <= FRAME_GAP_ALLOWANCE_S
        fa = row.get("frame_allowance_s")
        a["frame_allowance_matches_registered"] = (
            fa is not None and int(_f(fa)) == FRAME_ALLOWANCE_S)
        limbs = [a["within_cap"], a["inversion_matches_cap"],
                 a["frame_allowance_matches_registered"]]
        for k in ("deadline_frame_pass", "frame_gap_within_allowance"):
            if a[k] is not True and a[k] != "NOT_MEASURED":
                limbs.append(False)
        a["verdict"] = "PASS" if all(limbs) else "GATE FAIL"
        if a["verdict"] == "GATE FAIL":
            res["verdict"] = "GATE FAIL"
        res["arms"][arm] = a
    return res


def gate_toolchain(root, ledger_rows, census):
    res = {"gate": "G9_toolchain", "arms": {}, "verdict": "PASS",
           "shipped_row": "NAMED UNBOUGHT: %s" % DIGEST_SHIPPED}
    for arm in ARMS:
        if census[arm]["state"] != "RAN":
            res["arms"][arm] = {"state": "NOT_RUN"}
            continue
        row = ledger_rows[arm]
        a = {"row": row.get("ROW"), "digest": row.get("DIGEST")}
        a["digest_is_patched"] = (row.get("DIGEST") == DIGEST_PATCHED)
        a["row_is_patched"] = (row.get("ROW") == "PATCHED")
        log = os.path.join(root, row.get("log", ""))
        seen = None
        if os.path.isfile(log):
            with open(log, errors="replace") as fh:
                for line in fh:
                    if "D4S_IDWARP_SO_MD5:" in line or "D4_IDWARP_SO_MD5:" in line:
                        seen = line.strip().split(":")[-1].strip()
                        break
        a["idwarp_so_md5_in_log"] = seen
        a["idwarp_so_md5_matches"] = (seen == IDWARP_SO_MD5)
        a["verdict"] = "PASS" if all([a["digest_is_patched"], a["row_is_patched"],
                                      a["idwarp_so_md5_matches"]]) else "GATE FAIL"
        if a["verdict"] == "GATE FAIL":
            res["verdict"] = "GATE FAIL"
        res["arms"][arm] = a
    return res


def gate_placement(ledger_rows, census):
    res = {"gate": "G12_placement", "arms": {}, "verdict": "PASS",
           "not_measured": []}
    for arm in ARMS:
        if census[arm]["state"] != "RAN":
            res["arms"][arm] = {"state": "NOT_RUN"}
            continue
        row = ledger_rows[arm]
        a = {"cpuset": row.get("cpuset"), "memory": row.get("memory")}
        a["cpuset_matches_registered"] = (row.get("cpuset") == CPUSET)
        a["memory_matches_registered"] = (row.get("memory") == MEMORY)
        dm = row.get("delivered_cores_mean", "[]").strip("[]").split()
        if not dm or dm[0] == "NOT_MEASURED":
            a["delivered_cores_mean"] = "NOT_MEASURED"
            a["delivered_pass"] = "NOT_MEASURED"
            res["not_measured"].append("%s/delivered_cores_mean" % arm)
        else:
            a["delivered_cores_mean"] = _f(dm[0])
            a["delivered_pass"] = a["delivered_cores_mean"] >= DELIVERED_MIN
        limbs = [a["cpuset_matches_registered"], a["memory_matches_registered"]]
        if a["delivered_pass"] is not True and a["delivered_pass"] != "NOT_MEASURED":
            limbs.append(False)
        a["verdict"] = "PASS" if all(limbs) else "GATE FAIL"
        if a["verdict"] == "GATE FAIL":
            res["verdict"] = "GATE FAIL"
        res["arms"][arm] = a
    return res


# -------------------------------------------------------------- G-DVL
def gate_dvl(root, census, runscript_d6r, runscript_d4):
    """Re-read BOTH published physical artefacts from disk and re-assert the two
    locus controls at GRADING time.  Never trusts the producer's say-so."""
    sys.path.insert(0, HERE)
    import d6rf2_endpoint_locus as locus
    res = {"gate": "G-DVL_endpoint_locus", "arms": {}}
    verdicts = []
    for arm, art, rs in (("F_mp", "d6rf2_endpoint_dvs_PHYSICAL.json", runscript_d6r),
                         ("REF_off", "d4_endpoint_dvs_PHYSICAL.json", runscript_d4)):
        if census[arm]["state"] != "RAN":
            res["arms"][arm] = {"verdict": "NOT A RESULT",
                                "reason": "ARM_DID_NOT_RUN",
                                "producing_arm": arm, "artefact": art}
            verdicts.append("NOT A RESULT")
            continue
        path = os.path.join(root, ARM_DIR[arm], art)
        try:
            r = locus.gate(path, rs)
            r["verdict"] = "PASS"
        except locus.LocusRefusal as e:
            r = {"verdict": "GATE FAIL", "artefact": path,
                 "registration_source": rs, "control_refusal": str(e)[:900]}
        res["arms"][arm] = r
        verdicts.append(r["verdict"])
    res["verdict"] = ("NOT A RESULT" if "NOT A RESULT" in verdicts else
                      ("GATE FAIL" if "GATE FAIL" in verdicts else "PASS"))
    return res


# -------------------------------------------- readers + planted-zero controls
def read_fd(path):
    """THE FD READER.  One function, used for the real artefact AND for the
    planted copy -- a control that exercises a different reader controls
    nothing."""
    with open(path) as fh:
        doc = json.load(fh)
    rows = []
    for r in doc.get("rows", []):
        rec = {"dv": r.get("dv"), "idx": r.get("idx"), "status": r.get("status")}
        if r.get("status") == "PLANNED":
            rec["J_adj"] = _f(r.get("J_adj"))
            fd = r.get("fd") or {}
            for lab in ("s_lo", "s_hi"):
                leg = fd.get(lab) or {}
                rec[lab] = {"ok": bool(leg.get("ok")),
                            "step": leg.get("step"),
                            "d": _f(leg["d"]) if leg.get("ok") else None}
        rows.append(rec)
    return {"rows": rows, "n_rows": doc.get("n_rows"),
            "eta_used": _f(doc.get("eta_used", "nan")),
            "eta_floored": doc.get("eta_floored"),
            "producer_md5": doc.get("producer_md5")}


def plant_into_fd(src, dst):
    """Plant PLANT into the FIRST PLANNED row's s_hi derivative, BY KEY, and
    write the perturbed copy.  Returns the row identity that was planted."""
    with open(src) as fh:
        doc = json.load(fh)
    for r in doc.get("rows", []):
        if r.get("status") != "PLANNED":
            continue
        leg = (r.get("fd") or {}).get("s_hi") or {}
        if not leg.get("ok"):
            continue
        leg["d"] = repr(float(leg["d"]) + PLANT)
        with open(dst, "w") as fh:
            json.dump(doc, fh, indent=1, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())
        return {"dv": r.get("dv"), "idx": r.get("idx")}
    return None


def read_d4_cd_f(path):
    """THE PRICE READER.  Takes the LAST field of the single `^Objective` line
    of D4's IPOPT summary.  Refuses on zero or more than one such line."""
    if not os.path.isfile(path):
        refuse("PRICE_READER", {"absent": path})
    hits = []
    with open(path, errors="replace") as fh:
        for i, line in enumerate(fh, 1):
            if line.startswith("Objective"):
                hits.append((i, line.rstrip("\n")))
    if len(hits) != 1:
        refuse("PRICE_READER", {"n_objective_lines": len(hits), "path": path})
    parts = hits[0][1].replace(":", " ").split()
    return _f(parts[-1]), {"line_no": hits[0][0], "line": hits[0][1]}


def plant_into_d4(src, dst):
    """Plant PLANT into the objective on a COPY, BY LINE INDEX."""
    with open(src, errors="replace") as fh:
        lines = fh.readlines()
    idx = [i for i, l in enumerate(lines) if l.startswith("Objective")]
    if len(idx) != 1:
        refuse("PRICE_PLANT", {"n_objective_lines": len(idx)})
    i = idx[0]
    parts = lines[i].replace(":", " ").split()
    val = float(parts[-1]) + PLANT
    lines[i] = "Objective...............:   %.16e    %.16e\n" % (val, val)
    with open(dst, "w") as fh:
        fh.writelines(lines)
        fh.flush()
        os.fsync(fh.fileno())
    return i + 1


def run_planted_controls(ctrl_dir, fd_path):
    """CLAUDE.md rule 3.  Both controls plant, read back FROM DISK through the
    SAME reader, and REFUSE if the reader is blind.  Both assert the
    unperturbed original is byte-unchanged."""
    os.makedirs(ctrl_dir, exist_ok=True)
    out = {"PLANT": PLANT, "rel_tol": PLANT_REL_TOL}

    # ---- control 1: the FD reader ----
    if fd_path is None or not os.path.isfile(fd_path):
        out["fd_control"] = {"skipped": "the FD artefact's producing arm did "
                                        "not run; there is nothing to read and "
                                        "no gate is computed from it"}
    else:
        m_before = md5_of(fd_path)
        base = read_fd(fd_path)
        planted_copy = os.path.join(ctrl_dir, "d6r_fd_endpoint.PLANTED.json")
        who = plant_into_fd(fd_path, planted_copy)
        if who is None:
            refuse("PLANT_FD", {"no_PLANNED_row_with_an_ok_s_hi_leg": True,
                                "note": "a control with nothing to plant into "
                                        "is not a control (L-302)"})
        got = read_fd(planted_copy)
        b = [r for r in base["rows"]
             if r["dv"] == who["dv"] and r["idx"] == who["idx"]][0]["s_hi"]["d"]
        g = [r for r in got["rows"]
             if r["dv"] == who["dv"] and r["idx"] == who["idx"]][0]["s_hi"]["d"]
        delta = g - b
        seen = abs(delta - PLANT) <= PLANT_REL_TOL * max(abs(PLANT), abs(b), 1.0)
        m_after = md5_of(fd_path)
        out["fd_control"] = {"planted_into": who, "unperturbed": b,
                             "planted_read_back": g, "delta": delta,
                             "reader_saw_the_plant": seen,
                             "original_md5_before": m_before,
                             "original_md5_after": m_after,
                             "original_unchanged": m_before == m_after,
                             "planted_copy": planted_copy}
        if not seen:
            refuse("PLANT_FD", out["fd_control"])
        if m_before != m_after:
            refuse("PLANT_FD", {"the_control_modified_the_artefact_it_grades":
                                True, **out["fd_control"]})

    # ---- control 2: the D4 price reader ----
    m_before = md5_of(D4_OPT_IPOPT)
    base_cd, where = read_d4_cd_f(D4_OPT_IPOPT)
    planted_copy = os.path.join(ctrl_dir, "d4_opt_IPOPT.PLANTED.txt")
    ln = plant_into_d4(D4_OPT_IPOPT, planted_copy)
    got_cd, _ = read_d4_cd_f(planted_copy)
    delta = got_cd - base_cd
    seen = abs(delta - PLANT) <= PLANT_REL_TOL * max(abs(PLANT), abs(base_cd), 1.0)
    m_after = md5_of(D4_OPT_IPOPT)
    out["price_control"] = {"planted_at_line": ln, "unperturbed": base_cd,
                            "planted_read_back": got_cd, "delta": delta,
                            "reader_saw_the_plant": seen,
                            "source_line": where,
                            "original_md5_before": m_before,
                            "original_md5_after": m_after,
                            "original_unchanged": m_before == m_after,
                            "planted_copy": planted_copy}
    if not seen:
        refuse("PLANT_PRICE", out["price_control"])
    if m_before != m_after:
        refuse("PLANT_PRICE", {"the_control_modified_D4s_preserved_artefact":
                               True, **out["price_control"]})
    with open(os.path.join(ctrl_dir, "planted_controls.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    return out


# ---------------------------------------------------------------- G-FD
def gate_fd(root, census):
    art = "d6r_fd_endpoint.json"
    producer = ARTEFACT_PRODUCER[art]
    base = {"gate": "G-FD_bright_line_on_J", "artefact": art,
            "producing_arm": producer, "band_pct": FD_BAND_PCT,
            "aggregate_band_pct": AGG_BAND_PCT,
            "plateau_tol_pct": PLATEAU_TOL_PCT,
            "sign_flip_pathology_at": SIGN_FLIP_PATHOLOGY,
            "band_provenance": "band D, inherited BY CITATION from D6R "
                               "PREREGISTRATION.md section 3e; NOT re-derived"}
    if census[producer]["state"] != "RAN":
        base.update({"verdict": "NOT A RESULT", "reason": "ARM_DID_NOT_RUN",
                     "arm_state": census[producer],
                     "note": "the arm that writes this artefact did not run, "
                             "so this gate has NO INPUT. That is NOT a GATE "
                             "FAIL -- nothing was measured that could fail."})
        return base
    path = os.path.join(root, ARM_DIR[producer], art)
    if not os.path.isfile(path):
        refuse("G-FD", {"artefact_absent_although_producer_ran": path})
    doc = read_fd(path)
    comps, flips, num, den = [], 0, 0.0, 0.0
    n_planned = 0
    for r in doc["rows"]:
        c = {"dv": r["dv"], "idx": r["idx"], "status": r["status"]}
        if r["status"] != "PLANNED":
            c["verdict"] = "NOT A RESULT"
            c["reason"] = "component status %s -- no FD was taken" % r["status"]
            comps.append(c)
            continue
        lo, hi = r.get("s_lo") or {}, r.get("s_hi") or {}
        if not (lo.get("ok") and hi.get("ok")):
            c["verdict"] = "NOT A RESULT"
            c["reason"] = "an FD step did not evaluate"
            c["s_lo_ok"], c["s_hi_ok"] = lo.get("ok"), hi.get("ok")
            comps.append(c)
            continue
        n_planned += 1
        d_hi, d_lo, jadj = hi["d"], lo["d"], r["J_adj"]
        c.update({"J_adj": jadj, "d_s_lo": d_lo, "d_s_hi": d_hi,
                  "step_lo": lo["step"], "step_hi": hi["step"]})
        c["rel_err_pct"] = (abs(d_hi - jadj) / abs(d_hi) * 100.0
                            if d_hi != 0.0 else float("inf"))
        c["plateau_pct"] = (abs(d_hi - d_lo) / abs(d_hi) * 100.0
                            if d_hi != 0.0 else float("inf"))
        c["sign_flip"] = (d_hi * jadj) < 0.0
        if c["sign_flip"]:
            flips += 1
        c["in_band"] = c["rel_err_pct"] <= FD_BAND_PCT
        c["plateau_pass"] = c["plateau_pct"] <= PLATEAU_TOL_PCT
        c["verdict"] = ("PASS" if (c["in_band"] and c["plateau_pass"]
                                   and not c["sign_flip"]) else "GATE FAIL")
        num += (d_hi - jadj) ** 2
        den += d_hi ** 2
        comps.append(c)
    base["components"] = comps
    base["n_planned"] = n_planned
    base["sign_flips"] = flips
    base["eta_used"] = doc["eta_used"]
    base["eta_floored"] = doc["eta_floored"]
    if n_planned == 0:
        base.update({"verdict": "NOT A RESULT",
                     "reason": "no component produced a usable FD pair"})
        return base
    base["aggregate_rel_err_pct"] = (math.sqrt(num) / math.sqrt(den) * 100.0
                                     if den > 0 else float("inf"))
    base["aggregate_pass"] = base["aggregate_rel_err_pct"] <= AGG_BAND_PCT
    if flips >= SIGN_FLIP_PATHOLOGY:
        base["pathology_NOT_A_RESULT"] = True
        base["verdict"] = "NOT A RESULT"
        base["reason"] = ("%d sign flips >= the registered pathology threshold "
                          "%d -- named in advance" % (flips, SIGN_FLIP_PATHOLOGY))
        return base
    base["pathology_NOT_A_RESULT"] = False
    per_ok = all(c.get("verdict") == "PASS" for c in comps
                 if c.get("status") == "PLANNED" and "verdict" in c
                 and c.get("rel_err_pct") is not None)
    any_nar = any(c.get("verdict") == "NOT A RESULT" for c in comps)
    if any_nar:
        base["verdict"] = "NOT A RESULT"
        base["reason"] = "at least one registered component produced no FD pair"
    else:
        base["verdict"] = "PASS" if (per_ok and base["aggregate_pass"]) else "GATE FAIL"
    return base


# ------------------------------------------------------- G-OFF / G-PRICE
def _major_history(root, census):
    art = "d6r_major_history.json"
    producer = ARTEFACT_PRODUCER[art]
    if census[producer]["state"] != "RAN":
        return None, producer, art
    path = os.path.join(root, ARM_DIR[producer], art)
    if not os.path.isfile(path):
        refuse("MAJOR_HISTORY", {"absent_although_producer_ran": path})
    with open(path) as fh:
        return json.load(fh), producer, art


def gate_off(root, census):
    res = {"gate": "G-OFF_per_point", "artefacts": ["d6r_major_history.json",
                                                    "d6r_ref_off.json"],
           "caveat": ("CD_i(mp) is the LAST ACCEPTED MAJOR of an optimisation "
                      "that exited `Invalid number in NLP function or "
                      "derivative detected.` (D6R O_mp/opt_IPOPT.txt:822, "
                      "G-D6R-OPT UNCLASSIFIED). It is a design point, not an "
                      "optimum, and this gate makes no optimality claim."),
           "per_point": {}}
    hist, hp, ha = _major_history(root, census)
    if hist is None:
        res.update({"verdict": "NOT A RESULT", "reason": "ARM_DID_NOT_RUN",
                    "producing_arm": hp, "artefact": ha,
                    "per_point": {p: {"verdict": "NOT A RESULT",
                                      "reason": "ARM_DID_NOT_RUN"} for p in POINTS}})
        return res
    if census["REF_off"]["state"] != "RAN":
        res.update({"verdict": "NOT A RESULT", "reason": "ARM_DID_NOT_RUN",
                    "producing_arm": "REF_off", "artefact": "d6r_ref_off.json",
                    "per_point": {p: {"verdict": "NOT A RESULT",
                                      "reason": "ARM_DID_NOT_RUN"} for p in POINTS}})
        return res
    rp = os.path.join(root, ARM_DIR["REF_off"], "d6r_ref_off.json")
    if not os.path.isfile(rp):
        refuse("G-OFF", {"artefact_absent_although_producer_ran": rp})
    with open(rp) as fh:
        ref = json.load(fh)
    verds = []
    for p in POINTS:
        key = "CD_%s" % p
        if key not in hist or not hist[key]:
            refuse("G-OFF", {"major_history_missing": key})
        cd_mp = _f(hist[key][-1])
        if p not in ref.get("points", {}):
            refuse("G-OFF", {"ref_off_missing_point": p})
        cd_ref = _f(ref["points"][p]["CD"])
        cl_ref = _f(ref["points"][p]["CL"])
        v = "PASS" if cd_mp <= cd_ref else "GATE FAIL"
        verds.append(v)
        res["per_point"][p] = {"CL_target": CL_TARGETS[p], "CD_mp": cd_mp,
                               "CD_REF_off": cd_ref, "CL_REF_off": cl_ref,
                               "gain_REF_minus_mp": cd_ref - cd_mp,
                               "verdict": v}
    res["verdict"] = "PASS" if all(v == "PASS" for v in verds) else "GATE FAIL"
    return res


def gate_price(root, census, controls):
    res = {"gate": "G-PRICE_single_point", "band": list(PRICE_BAND),
           "reference_recorded": CD_F_D4_RECORDED,
           "reference_source": D4_OPT_IPOPT}
    cd_f, where = read_d4_cd_f(D4_OPT_IPOPT)
    res["reference_reread"] = cd_f
    res["reference_line"] = where
    res["planted_control"] = controls.get("price_control", {}).get(
        "reader_saw_the_plant")
    if cd_f != CD_F_D4_RECORDED:
        refuse("G-PRICE", {"D4_reference_moved": {"recorded": CD_F_D4_RECORDED,
                                                  "reread": cd_f}})
    hist, hp, ha = _major_history(root, census)
    if hist is None:
        res.update({"verdict": "NOT A RESULT", "reason": "ARM_DID_NOT_RUN",
                    "producing_arm": hp, "artefact": ha})
        return res
    cd_mp = _f(hist["CD_cl05"][-1])
    price = cd_mp - cd_f
    res["CD_cl05_mp"] = cd_mp
    res["price"] = price
    if price < 0.0:
        res["verdict"] = "NOT A RESULT"
        res["reason"] = ("a negative price is a finding about D4, named in "
                         "advance as pending triage")
    elif price <= PRICE_BAND[1]:
        res["verdict"] = "PASS"
    else:
        res["verdict"] = "GATE FAIL"
    return res


def report_reduction(root, census):
    """REPORTED, NOT GATED (Sanaa 2026-09-03 ~20:00Z)."""
    res = {"row": "R-RED_composite_reduction", "gating": False,
           "band_pct_for_reference": list(RED_BAND_PCT),
           "why_not_gated": ("the producing optimisation exited on a "
                             "non-finite objective (G-D6R-OPT UNCLASSIFIED), "
                             "so a reduction along its trajectory is a number, "
                             "not a claim about a converged optimum")}
    hist, hp, ha = _major_history(root, census)
    if hist is None:
        res.update({"value_pct": None, "reason": "ARM_DID_NOT_RUN",
                    "producing_arm": hp})
        return res
    J = [_f(v) for v in hist["J"]]
    res["J0"], res["Jf"], res["n_major"] = J[0], J[-1], len(J)
    res["value_pct"] = (J[0] - J[-1]) / J[0] * 100.0 if J[0] != 0 else None
    res["inside_reference_band"] = (
        res["value_pct"] is not None
        and RED_BAND_PCT[0] <= res["value_pct"] <= RED_BAND_PCT[1])
    return res


# ------------------------------------------------------------- composition
def compose(g1, dvl, fd, off, price, caps, tool, place, census):
    """THE REGISTERED VERDICT LADDER, in order.  A NOT A RESULT can only turn a
    PASS or GATE FAIL INTO a NOT A RESULT, never the reverse."""
    reasons = []
    ran = [a for a in ARMS if census[a]["state"] == "RAN"]
    notrun = [a for a in ARMS if census[a]["state"] != "RAN"]

    dirty = [a for a in ran if not g1["arms"][a].get("clauses_all_pass")]
    if dirty:
        reasons.append("rung 1: completion clause failed on arm(s) %s" % dirty)
        return "NOT A RESULT", reasons
    if notrun:
        reasons.append("rung 2: registered arm(s) %s did not run; the item can "
                       "never be PASS with an arm unbought" % notrun)
        return "NOT A RESULT", reasons
    if dvl["verdict"] == "GATE FAIL":
        reasons.append("rung 3: G-DVL GATE FAIL -- the design point on disk is "
                       "not the one the registration names, so nothing "
                       "downstream of it measures what it says")
        return "NOT A RESULT", reasons
    if fd.get("pathology_NOT_A_RESULT"):
        reasons.append("rung 4: the registered FD sign-flip pathology fired")
        return "NOT A RESULT", reasons
    if price["verdict"] == "NOT A RESULT" and price.get("price", 0.0) < 0.0:
        reasons.append("rung 4: negative single-point price -- a finding about "
                       "D4, named in advance")
        return "NOT A RESULT", reasons
    nar = [g["gate"] for g in (dvl, fd, off, price)
           if g.get("verdict") == "NOT A RESULT"]
    if nar:
        reasons.append("rung 5: gate(s) %s NOT A RESULT for want of an input" % nar)
        return "NOT A RESULT", reasons
    gf = [g["gate"] for g in (dvl, fd, off, price, caps, tool, place)
          if g.get("verdict") == "GATE FAIL"]
    if gf:
        reasons.append("rung 6: gate(s) %s GATE FAIL" % gf)
        return "GATE FAIL", reasons
    reasons.append("rung 7: every gated row PASS")
    return "PASS", reasons


# ------------------------------------------------------------------- main
def grade(root, out_path, skip_freeze=False, runscript_d6r=None,
          runscript_d4=None, d4_ref=None):
    global D4_OPT_IPOPT
    if d4_ref:
        D4_OPT_IPOPT = d4_ref
    frozen = {}
    if not skip_freeze:
        frozen = freeze_check([
            "cases/dafoam/ladder-a/A2/curriculum_D6RF2/PREREGISTRATION.md",
            "cases/dafoam/ladder-a/A2/curriculum_D6RF2/d6rf2_grade.py",
            "cases/dafoam/ladder-a/A2/curriculum_D6RF2/d6rf2_endpoint_locus.py",
            "cases/dafoam/ladder-a/A2/curriculum_D6RF2/d6rf2_endpoint_physical.py",
            "cases/dafoam/ladder-a/A2/curriculum_D6RF2/d6rf2_anchor_gate.py",
            "cases/dafoam/ladder-a/A2/curriculum_D6RF2/d6rf2_opt_runScript.py",
        ])
    rs6 = runscript_d6r or os.path.join(
        HERE, os.pardir, "curriculum_D6R", "d6rf2_opt_runScript.py")
    rs4 = runscript_d4 or os.path.join(
        HERE, os.pardir, "curriculum_D4", "d4_opt_runScript.py")
    rs6, rs4 = os.path.abspath(rs6), os.path.abspath(rs4)

    ledger_rows, extra = parse_ledger(os.path.join(root, "ledger.txt"))
    chain = read_chain_status(os.path.join(root, "STATUS.chain"))
    census = arm_census(root, ledger_rows, chain)

    ctrl_dir = os.path.join(os.path.dirname(os.path.abspath(out_path)),
                            "grader_controls")
    fd_path = None
    if census[ARTEFACT_PRODUCER["d6r_fd_endpoint.json"]]["state"] == "RAN":
        fd_path = os.path.join(root, ARM_DIR["F_mp"], "d6r_fd_endpoint.json")
    controls = run_planted_controls(ctrl_dir, fd_path)

    g1 = gate_g1(root, ledger_rows, census)
    caps = gate_caps(ledger_rows, census)
    tool = gate_toolchain(root, ledger_rows, census)
    place = gate_placement(ledger_rows, census)
    dvl = gate_dvl(root, census, rs6, rs4)
    fd = gate_fd(root, census)
    off = gate_off(root, census)
    price = gate_price(root, census, controls)
    red = report_reduction(root, census)

    verdict, reasons = compose(g1, dvl, fd, off, price, caps, tool, place, census)
    spend = sum(g1["arms"][a].get("core_min", 0.0) for a in ARMS)
    doc = {
        "item": ITEM,
        "verdict": verdict,
        "verdict_reasons": reasons,
        "frozen": frozen,
        "census": census,
        "chain_status": chain,
        "planted_controls": controls,
        "grade": {"G1": g1, "G-DVL": dvl, "G-FD": fd, "G-OFF": off,
                  "G-PRICE": price, "G-CAPS": caps, "G9": tool, "G12": place},
        "reported_not_gated": {"R-RED": red},
        "spend_core_min": spend,
        "cost_basis": ("c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT "
                       "MEASURED (COMPUTE_BUDGET_CHARTER.md section 5). "
                       "Dollars DERIVED, never measured."),
        "spend_usd_derived": round(spend / 60.0 * 0.0513, 6),
        "ceiling_core_min": sum(CAPS.values()),
        "ledger_extra_lines": extra,
    }
    with open(out_path, "w") as fh:
        json.dump(doc, fh, indent=1, sort_keys=True)
        fh.flush()
        os.fsync(fh.fileno())
    print("D6RF2_VERDICT %s  spend %.3f core-min of a %.1f ceiling  -> %s"
          % (verdict, spend, sum(CAPS.values()), out_path))
    # G1 reports TWO SEPARATE FACTS and they are never the same verdict:
    # a chain stop makes `all_arms_ran` false and can leave `ran_clean` true.
    print("  %-26s ran_clean=%s all_arms_ran=%s"
          % (g1["gate"], g1["ran_clean"], g1["all_arms_ran"]))
    for g in (dvl, fd, off, price, caps, tool, place):
        print("  %-26s %s" % (g["gate"], g.get("verdict", "-")))
    print("  %-26s %s (REPORTED, NOT GATED)"
          % (red["row"], red.get("value_pct")))
    return doc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root")
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--skip-freeze", action="store_true",
                    help="selftest fixtures only; NEVER on a real grading run")
    ap.add_argument("--runscript-d6r")
    ap.add_argument("--runscript-d4")
    ap.add_argument("--d4-ref")
    a = ap.parse_args()
    if a.selftest:
        import d6rf2_grade_selftest as st
        return st.run()
    if not a.root or not a.out:
        sys.stderr.write("usage: d6rf2_grade.py --root <run root> --out <json>\n")
        return 64
    try:
        grade(a.root, a.out, a.skip_freeze, a.runscript_d6r, a.runscript_d4,
              a.d4_ref)
    except Refusal as e:
        sys.stderr.write("D6RF2_GRADE REFUSED %s\n" % e)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
