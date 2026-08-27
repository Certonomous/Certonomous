"""
M1 multi-model sweep -- THE COMPARATOR.

Grades 2 arms x 39 cases = 78 runs against the gates frozen in
PREREGISTRATION.md section 7.  Every threshold below is REGISTERED and may not
be changed after the first compute except by a dated addendum that cannot alter
a gate, threshold, cap or label (standing rule 2, rule 6).

STANDING RULES CARRIED HERE, EACH BY AN INSTRUMENT AND NOT BY A COMMENT:
  rule 3  a plant is written to a field ON DISK, re-read by re-opening the file,
          and the comparator REFUSES (sys.exit 2) if the reader cannot see it.
          An in-memory plant does not satisfy this.
  rule 4  strict completion + the age guard.  A row that fails any clause is
          INCOMPLETE and its numbers are NOT COMPUTED -- refuse, never degrade.
  rule 5  DOES NOT APPLY.  One mesh per case, no triple, no GCI, no observed
          order.  The comparator PRINTS that sentence rather than leaving a
          reader to infer it.
  L-342   physics-critical vs infrastructure fields.  A missing STATUS is
          INFRASTRUCTURE: NOT MEASURED, and it can never void intact physics.
  L-332   no `assert` carries a refusal.  --selftest runs under `python3 -O`
          with every refusal still firing.
  L-314   every guard ships its planted-failure proof.

Usage
  python3 grade_m1.py --root /home/ubuntu/closure-data/multimodel_sweep
  python3 -O grade_m1.py --selftest
"""

import argparse
import datetime
import json
import math
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

# --------------------------------------------------------------------------
# REGISTERED CONSTANTS -- frozen by PREREGISTRATION.md
# --------------------------------------------------------------------------
BENCH_ROOT_DEFAULT = "/home/ubuntu/closure-challenge-benchmark/data"
RUN_ROOT_DEFAULT = "/home/ubuntu/closure-data/multimodel_sweep"

ARMS = {"kOmegaSST_null": "kOmegaSST", "kOmega": "kOmega"}
NULL_ARM = "kOmegaSST_null"
TEST_ARM = "kOmega"
EXCLUDED_CASES = ("NASA_2DWMH",)

CAP_ITER = 20000                     # section 3
PHYSICS_FIELDS = ("U", "p", "k", "omega", "nut")
AGE_DATUM = "U"                      # 0/U, section 6 C4

CONV_K_TOL = 5.0e-6                  # section 4.1, sustained to CAP_ITER
CONV_OMEGA_TOL = 5.0e-6

G2_BAND = 1.0e-3                     # section 7 G2
G2_MIN_IN_BAND = 37
# SUPERVISOR'S RULING, 2026-08-27, before staging: G2's "37 of 39" was a LOTTERY
# over which two cases may miss the band.  It is replaced by a STRUCTURAL
# partition fixed here, which is strictly stronger at the same headline count.
# The 29 Parm_PH_29 hills are ITERATION-MATCHED -- their shipped reference was
# written at endTime 20000, exactly this sweep's cap -- so on those there is no
# excuse and ALL 29 must meet the band.  The 10 unmatched cases (8 ducts at
# 334-7009 under a criterion we do not use, CBFS at 30000, PH_Breuer at 10000)
# may contribute at most G2_UNMATCHED_MAX_OUT outliers, still under the ceiling.
# Net effect: the two permitted outliers can no longer hide among the hills.
G2_MATCHED_PREFIX = "alpha_"         # the 29 Parm_PH_29 hills
G2_UNMATCHED_MAX_OUT = 2
G2_CEILING = 1.0e-2
G2_REFUSE_ABOVE = 1.0e-1

G3_SEPARATION = 1.0e-2               # section 7 G3
G3_MIN_CASES = 30

G4_MAX_CAPBOUND = 8                  # section 7 G4

N_CASES = 39
N_RUNS = 78

PLANT = 1.234e-03                    # standing rule 3

VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")

RULE5_STATEMENT = (
    "STANDING RULE 5 DOES NOT APPLY TO THIS RUNG: one mesh per case is shipped, "
    "no grid triple exists, and therefore no GCI, no observed order and no "
    "Roache triple state is computed or quoted anywhere in this output.")

TIME_DIR_RE = re.compile(r"^[0-9]+(\.[0-9]+)?$")


class Refusal(Exception):
    def __init__(self, code, msg):
        super().__init__(f"REFUSE [{code}]: {msg}")
        self.code = code


def refuse(code, msg):
    raise Refusal(code, msg)


# --------------------------------------------------------------------------
# OpenFOAM ascii field reader.  Deliberately a SECOND, independent copy of the
# reader in stage_m1.py: each instrument carries its own reader and its own
# planted-zero control, so a divergence between the two is detectable rather
# than shared.
# --------------------------------------------------------------------------
def read_internal_field(path):
    if not os.path.isfile(path):
        refuse("FIELD-MISSING", f"no field file at {path}")
    txt = open(path, "r", errors="replace").read()
    m = re.search(r"^\s*internalField\s+(uniform|nonuniform)", txt, re.M)
    if not m:
        refuse("FIELD-PARSE", f"no internalField entry in {path}")
    if m.group(1) == "uniform":
        tail = txt[m.end():]
        stop = tail.find(";")
        if stop < 0:
            refuse("FIELD-PARSE", f"unterminated uniform internalField in {path}")
        body = tail[:stop].strip()
        if body.startswith("("):
            comps = [float(x) for x in body.strip("()").split()]
            return dict(kind="uniform", rank=len(comps), n=1, values=comps)
        try:
            return dict(kind="uniform", rank=1, n=1, values=[float(body)])
        except ValueError:
            refuse("FIELD-PARSE",
                   f"uniform internalField is not numeric in {path}: {body!r} "
                   f"(an unexpanded dictionary variable is not a value)")
    m2 = re.search(r"List<(\w+)>\s*\n?\s*(\d+)\s*\n?\s*\(", txt[m.start():])
    if not m2:
        refuse("FIELD-PARSE", f"cannot locate nonuniform List header in {path}")
    rank = {"scalar": 1, "vector": 3, "symmTensor": 6, "tensor": 9}.get(m2.group(1))
    if rank is None:
        refuse("FIELD-PARSE", f"unsupported List type {m2.group(1)} in {path}")
    n = int(m2.group(2))
    start = m.start() + m2.end()
    depth, i = 1, start
    while i < len(txt) and depth > 0:
        if txt[i] == "(":
            depth += 1
        elif txt[i] == ")":
            depth -= 1
            if depth == 0:
                break
        i += 1
    if depth != 0:
        refuse("FIELD-PARSE", f"unbalanced parentheses in {path}")
    vals = [float(x) for x in txt[start:i].replace("(", " ").replace(")", " ").split()]
    if len(vals) != n * rank:
        refuse("FIELD-PARSE", f"{path}: header says {n}x{rank}={n * rank} numbers, "
                              f"found {len(vals)}")
    return dict(kind="nonuniform", rank=rank, n=n, values=vals)


def as_flat(field, ncells):
    """Expand a uniform field to ncells; refuse on a length mismatch."""
    if field["kind"] == "uniform":
        return list(field["values"]) * ncells
    if field["n"] != ncells:
        refuse("FIELD-SIZE", f"field holds {field['n']} cells, expected {ncells}")
    return field["values"]


def rel_l2(a, b):
    """|| a - b ||_2 / || b ||_2 .  b is the reference."""
    if len(a) != len(b):
        refuse("FIELD-SIZE", f"length mismatch {len(a)} vs {len(b)}")
    num = math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))
    den = math.sqrt(sum(y * y for y in b))
    if den == 0.0:
        refuse("FIELD-ZERO", "the reference field has zero norm; a relative "
                             "difference against it is undefined")
    return num / den


def plant_into_field(path, plant=PLANT):
    txt = open(path, "r", errors="replace").read()
    m = re.search(r"^\s*internalField\s+(uniform|nonuniform)", txt, re.M)
    if not m:
        refuse("C1-PLANT", f"no internalField in {path}")
    if m.group(1) == "uniform":
        anchor = m.end()
    else:
        m2 = re.search(r"List<\w+>\s*\n?\s*\d+\s*\n?\s*\(", txt[m.start():])
        if not m2:
            refuse("C1-PLANT", f"cannot locate nonuniform data in {path}")
        anchor = m.start() + m2.end()
    numre = re.compile(r"[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?")
    mnum = numre.search(txt, anchor)
    if not mnum:
        refuse("C1-PLANT", f"no numeric token after the internalField header in {path}")
    before = float(mnum.group(0))
    open(path, "w").write(txt[:mnum.start()] + repr(before + plant) + txt[mnum.end():])
    back = numre.search(open(path, "r", errors="replace").read(), anchor)   # RE-OPEN
    if back is None or abs((float(back.group(0)) - before) - plant) > 1e-12:
        refuse("C1-PLANT", f"the plant did not land in {path}")
    return before, float(back.group(0))


def planted_zero_control(field_path, workdir):
    a = os.path.join(workdir, "c1_clean")
    b = os.path.join(workdir, "c1_planted")
    shutil.copyfile(field_path, a)
    shutil.copyfile(field_path, b)
    before, after = plant_into_field(b, PLANT)
    fa, fb = read_internal_field(a), read_internal_field(b)
    if len(fa["values"]) != len(fb["values"]):
        refuse("C1-PLANT", "planted and clean copies parsed to different lengths")
    seen = max(abs(x - y) for x, y in zip(fb["values"], fa["values"]))
    return dict(source=field_path, planted=PLANT, read_back_delta=after - before,
                reader_max_change=seen, passed=seen >= PLANT - 1e-15)


# --------------------------------------------------------------------------
# log and STATUS readers
# --------------------------------------------------------------------------
SOLVE_RE = re.compile(
    r"Solving for (\w+),\s*Initial residual = ([0-9.eE+-]+)")
TIME_RE = re.compile(r"^Time = (\S+)\s*$")
MODEL_RE = re.compile(r"Selecting\s+(?:RAS\s+)?turbulence model\s+(\w+)")
MODEL_RE2 = re.compile(r"^\s*(?:RAS\s+)?[Mm]odel\s+(\w+)\s*$")


def parse_log(path):
    """Physics-critical: the End line, the ExecutionTime count, the last time,
    the residual history and the model the SOLVER ITSELF says it selected."""
    if not os.path.isfile(path):
        refuse("LOG-MISSING", f"no log.run at {path}")
    end_line = False
    exec_count = 0
    last_time = None
    model = None
    res = {}          # field -> {iteration: first initial residual}
    cur = None
    seen_at_time = set()
    with open(path, "r", errors="replace") as fh:
        for line in fh:
            mt = TIME_RE.match(line)
            if mt:
                try:
                    cur = int(float(mt.group(1)))
                except ValueError:
                    cur = None
                last_time = mt.group(1)
                seen_at_time = set()
                continue
            if line.startswith("ExecutionTime"):
                exec_count += 1
                continue
            if line.strip() == "End":
                end_line = True
                continue
            if model is None:
                mm = MODEL_RE.search(line)
                if mm:
                    model = mm.group(1)
                    continue
            ms = SOLVE_RE.search(line)
            if ms and cur is not None:
                fld, val = ms.group(1), float(ms.group(2))
                if fld in seen_at_time:
                    continue
                seen_at_time.add(fld)
                res.setdefault(fld, {})[cur] = val
    return dict(end_line=end_line, exec_count=exec_count, last_time=last_time,
                model_from_log=model, residuals=res)


def read_status(path):
    """INFRASTRUCTURE (L-342).  Absent -> NOT MEASURED, never a failure."""
    if not os.path.isfile(path):
        return None
    out = {}
    for line in open(path, "r", errors="replace"):
        if "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def numeric_time_dirs(root):
    if not os.path.isdir(root):
        return []
    return sorted((d for d in os.listdir(root)
                   if TIME_DIR_RE.match(d) and os.path.isdir(os.path.join(root, d))),
                  key=float)


def read_ras_model_from_dict(case_dir):
    p = os.path.join(case_dir, "constant", "turbulenceProperties")
    if not os.path.isfile(p):
        refuse("TP-MISSING", f"no constant/turbulenceProperties in {case_dir}")
    m = re.search(r"(?m)^[ \t]*RASModel[ \t]+([^;]*);",
                  open(p, errors="replace").read())
    return m.group(1).strip() if m else None


# --------------------------------------------------------------------------
# completion and convergence
# --------------------------------------------------------------------------
def completion(case_dir, log):
    """Standing rule 4, split physics-critical / infrastructure per L-342."""
    end_dir = os.path.join(case_dir, str(CAP_ITER))
    zero_datum = os.path.join(case_dir, "0", AGE_DATUM)
    clauses = {}
    clauses["end_line"] = bool(log["end_line"])
    clauses["last_time_eq_endTime"] = (
        log["last_time"] is not None and
        abs(float(log["last_time"]) - CAP_ITER) < 1e-9)
    clauses["fields_present"] = all(
        os.path.isfile(os.path.join(end_dir, f)) for f in PHYSICS_FIELDS)
    clauses["exec_count_eq_endTime"] = (log["exec_count"] == CAP_ITER)
    if os.path.isfile(zero_datum) and clauses["fields_present"]:
        t0 = os.path.getmtime(zero_datum)
        clauses["age_guard"] = all(
            os.path.getmtime(os.path.join(end_dir, f)) > t0 for f in PHYSICS_FIELDS)
    else:
        clauses["age_guard"] = False
    st = read_status(os.path.join(case_dir, "STATUS"))
    if st is None:
        rc = None
        rc_class = "NOT MEASURED (infrastructure: no STATUS record; L-342, "\
                   "Sanaa desk ruling R-RC)"
        clauses["rc_zero"] = None
    else:
        try:
            rc = int(st.get("rc", "999"))
        except ValueError:
            rc = 999
        rc_class = "measured"
        clauses["rc_zero"] = (rc == 0)
    physics_ok = all(clauses[k] for k in ("end_line", "last_time_eq_endTime",
                                          "fields_present", "exec_count_eq_endTime",
                                          "age_guard"))
    # R-RC: the rc VALUE is physics; the rc RECORD is infrastructure.  An absent
    # record is NOT MEASURED only when the other four rule-4 conditions hold.
    complete = physics_ok and (clauses["rc_zero"] is not False)
    return dict(clauses=clauses, complete=complete, physics_ok=physics_ok,
                rc=rc, rc_class=rc_class, status=st)


def convergence_class(log):
    """Section 4.1.  CONVERGED@n if k<=CONV_K_TOL and omega<=CONV_OMEGA_TOL for
    EVERY outer iteration from n to CAP_ITER; otherwise CAP-BOUND."""
    rk = log["residuals"].get("k", {})
    ro = log["residuals"].get("omega", {})
    if not rk or not ro:
        return dict(state="CAP-BOUND", n=None,
                    reason="no k and/or omega residual history in log.run",
                    min_k=None, min_omega=None, min_k_at=None, min_omega_at=None)
    its = sorted(set(rk) & set(ro))
    last_bad = None
    for i in its:
        if rk[i] > CONV_K_TOL or ro[i] > CONV_OMEGA_TOL:
            last_bad = i
    mk = min(rk.items(), key=lambda kv: kv[1])
    mo = min(ro.items(), key=lambda kv: kv[1])
    common = dict(min_k=mk[1], min_k_at=mk[0], min_omega=mo[1], min_omega_at=mo[0])
    if last_bad is None:
        return dict(state="CONVERGED", n=its[0], reason="", **common)
    nxt = [i for i in its if i > last_bad]
    if not nxt:
        return dict(state="CAP-BOUND", n=None,
                    reason=f"criterion still unmet at the cap (last violation at "
                           f"iteration {last_bad})", **common)
    return dict(state="CONVERGED", n=nxt[0], reason="", **common)


# --------------------------------------------------------------------------
# case inventory, re-derived from the benchmark tree rather than hard-coded
# --------------------------------------------------------------------------
def bench_inventory(bench_root):
    out = {}
    for dirpath, _d, _f in os.walk(bench_root):
        if os.path.basename(dirpath) != "polyMesh":
            continue
        root = os.path.dirname(os.path.dirname(dirpath))
        if not (os.path.isdir(os.path.join(root, "0"))
                and os.path.isdir(os.path.join(root, "system"))):
            continue
        cid = os.path.basename(root)
        if cid in EXCLUDED_CASES:
            continue
        tds = numeric_time_dirs(root)
        tds = [t for t in tds if float(t) > 0]
        head = open(os.path.join(root, "constant", "polyMesh", "owner"),
                    errors="replace").read(4000)
        mc = re.search(r"nCells:\s*(\d+)", head)
        out[cid] = dict(path=root, ref_time=(tds[-1] if tds else None),
                        ncells=int(mc.group(1)) if mc else None)
    return out


# --------------------------------------------------------------------------
# grading
# --------------------------------------------------------------------------
def grade_row(run_root, arm, cid, inv):
    case_dir = os.path.join(run_root, arm, cid)
    row = dict(arm=arm, case_id=cid, case_dir=case_dir)
    if not os.path.isdir(case_dir):
        row.update(state="PENDING", note="run directory absent")
        return row
    log = parse_log(os.path.join(case_dir, "log.run"))
    comp = completion(case_dir, log)
    conv = convergence_class(log)
    row.update(completion=comp, convergence=conv,
               model_from_dict=read_ras_model_from_dict(case_dir),
               model_from_log=log["model_from_log"],
               exec_count=log["exec_count"], last_time=log["last_time"])
    if comp["status"] is None:
        row["core_min"] = None
        row["core_min_class"] = "NOT MEASURED (infrastructure)"
    else:
        try:
            row["core_min"] = float(comp["status"].get("core_min"))
        except (TypeError, ValueError):
            row["core_min"] = None
        row["core_min_class"] = "measured from STATUS"
    if not comp["complete"]:
        row["state"] = "INCOMPLETE"
        row["note"] = ("strict completion rule failed: " +
                       ", ".join(k for k, v in comp["clauses"].items() if v is False))
        # REFUSE TO DEGRADE: no field number is computed for an incomplete row.
        return row
    row["state"] = "COMPLETE"
    ncells = inv[cid]["ncells"]
    row["U_end"] = as_flat(read_internal_field(
        os.path.join(case_dir, str(CAP_ITER), "U")), ncells)
    row["k_end"] = as_flat(read_internal_field(
        os.path.join(case_dir, str(CAP_ITER), "k")), ncells)
    row["nut_end"] = as_flat(read_internal_field(
        os.path.join(case_dir, str(CAP_ITER), "nut")), ncells)
    return row


def main(argv):
    ap = argparse.ArgumentParser(description="M1 comparator")
    ap.add_argument("--root", default=RUN_ROOT_DEFAULT)
    ap.add_argument("--bench-root", default=BENCH_ROOT_DEFAULT)
    ap.add_argument("--out", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--planted-failure", metavar="GUARD")
    args = ap.parse_args(argv[1:])
    if args.selftest:
        return selftest()
    if args.planted_failure:
        return planted_failure_proof(args.planted_failure)
    return grade(args.root, args.bench_root, args.out)


def grade(run_root, bench_root, out_path=None):
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    print("M1 MULTI-MODEL SWEEP -- COMPARATOR")
    print(RULE5_STATEMENT)
    print()

    inv = bench_inventory(bench_root)
    if len(inv) != N_CASES:
        refuse("INVENTORY", f"the benchmark tree yields {len(inv)} includable cases, "
                            f"the registration names {N_CASES}")

    rows = {}
    for arm in ARMS:
        for cid in sorted(inv):
            rows[(arm, cid)] = grade_row(run_root, arm, cid, inv)

    pending = [k for k, r in rows.items() if r["state"] == "PENDING"]
    if pending:
        for arm, cid in sorted(pending):
            print(f"PENDING: {os.path.join(run_root, arm, cid)}")
        refuse("PENDING", f"{len(pending)} of {N_RUNS} runs have no run directory; a "
                          f"partial sweep receives no verdict")

    # ---- C1 PLANTED ZERO, ON DISK, BEFORE ANY NUMBER ---------------------
    donor = None
    for k in sorted(rows):
        if rows[k]["state"] == "COMPLETE":
            donor = os.path.join(rows[k]["case_dir"], str(CAP_ITER), "U")
            break
    if donor is None:
        refuse("C1-PLANT", "no complete run to plant into; the reader could not be "
                           "shown able to see a non-zero, so its zeros mean nothing")
    with tempfile.TemporaryDirectory(prefix="m1grade_") as tmp:
        pz = planted_zero_control(donor, tmp)
    print(f"C1 planted-zero control on {donor}: {pz}")
    if not pz["passed"]:
        refuse("C1-PLANT", f"planted-zero control FAILED: the reader cannot see a "
                           f"{PLANT} difference planted on disk; its zeros mean nothing")

    # ---- G1 ARM APPLICATION ---------------------------------------------
    g1_bad = []
    for (arm, cid), r in sorted(rows.items()):
        want = ARMS[arm]
        if r.get("model_from_dict") != want:
            g1_bad.append((arm, cid, "dict", r.get("model_from_dict")))
        elif r.get("model_from_log") not in (None, want):
            g1_bad.append((arm, cid, "log", r.get("model_from_log")))
    g1 = dict(gate="G1", name="arm application",
              verdict=("PASS" if not g1_bad else "NOT A RESULT"),
              n_bad=len(g1_bad), bad=g1_bad[:20])

    # ---- G0 COMPLETION ---------------------------------------------------
    incomplete = [(a, c) for (a, c), r in sorted(rows.items())
                  if r["state"] != "COMPLETE"]
    g0 = dict(gate="G0", name="completion / harness",
              verdict=("PASS" if not incomplete else "GATE FAIL"),
              n_complete=N_RUNS - len(incomplete), n_total=N_RUNS,
              incomplete=[f"{a}/{c}" for a, c in incomplete])

    capbound = {k for k, r in rows.items()
                if r["state"] == "COMPLETE" and r["convergence"]["state"] == "CAP-BOUND"}

    # ---- G2 NULL-ARM IDENTITY -------------------------------------------
    g2_vals, g2_missing = {}, []
    for cid in sorted(inv):
        r = rows[(NULL_ARM, cid)]
        if r["state"] != "COMPLETE":
            g2_missing.append(cid)
            continue
        ref_t = inv[cid]["ref_time"]
        if ref_t is None:
            g2_missing.append(cid)
            continue
        ref = as_flat(read_internal_field(
            os.path.join(inv[cid]["path"], ref_t, "U")), inv[cid]["ncells"])
        g2_vals[cid] = rel_l2(r["U_end"], ref)
    g2 = _g2_verdict(g2_vals, g2_missing, capbound, NULL_ARM)

    # ---- G3 ARM SEPARATION (a spread, and only a spread) ------------------
    g3_vals, g3_missing = {}, []
    for cid in sorted(inv):
        a, b = rows[(TEST_ARM, cid)], rows[(NULL_ARM, cid)]
        if a["state"] != "COMPLETE" or b["state"] != "COMPLETE":
            g3_missing.append(cid)
            continue
        g3_vals[cid] = rel_l2(a["U_end"], b["U_end"])
    g3 = _g3_verdict(g3_vals, g3_missing, capbound)

    # ---- G4 CAP-BOUND CENSUS --------------------------------------------
    g4 = dict(gate="G4", name="cap-bound census (a ROW CLASS, not a verdict)",
              verdict=("GATE REACHED" if len(capbound) <= G4_MAX_CAPBOUND
                       else "GATE FAIL"),
              n_capbound=len(capbound), threshold=G4_MAX_CAPBOUND,
              capbound=[f"{a}/{c}" for a, c in sorted(capbound)])

    # ---- report -----------------------------------------------------------
    print()
    print("PER-ROW TABLE.  Every row carries its convergence class beside its number.")
    print(f"{'arm':<16}{'case':<24}{'state':<11}{'convergence':<18}"
          f"{'rel-L2 U vs ref':>17}{'rel-L2 U arms':>15}{'core-min':>11}")
    for cid in sorted(inv):
        for arm in (NULL_ARM, TEST_ARM):
            r = rows[(arm, cid)]
            conv = (r["convergence"]["state"] +
                    (f"@{r['convergence']['n']}" if r.get("convergence", {}).get("n")
                     else "")) if r["state"] == "COMPLETE" else "-"
            v2 = f"{g2_vals[cid]:.3e}" if (arm == NULL_ARM and cid in g2_vals) else ""
            v3 = f"{g3_vals[cid]:.3e}" if (arm == TEST_ARM and cid in g3_vals) else ""
            cm = ("NOT MEASURED" if r.get("core_min") is None
                  else f"{r['core_min']:.2f}")
            print(f"{arm:<16}{cid:<24}{r['state']:<11}{conv:<18}{v2:>17}{v3:>15}{cm:>11}")

    print()
    for g in (g0, g1, g2, g3, g4):
        print(f"{g['gate']}  {g['name']}: {g['verdict']}")
        for kk, vv in g.items():
            if kk not in ("gate", "name", "verdict"):
                print(f"      {kk}: {vv}")
    print()
    print(RULE5_STATEMENT)

    total_measured = sum(r["core_min"] for r in rows.values()
                         if r.get("core_min") is not None)
    n_unmeasured = sum(1 for r in rows.values() if r.get("core_min") is None)
    print(f"\nCOST: {total_measured:.1f} core-min measured from STATUS across "
          f"{N_RUNS - n_unmeasured} rows; {n_unmeasured} rows NOT MEASURED "
          f"(infrastructure, L-342).  Registered estimate 1298.1 core-min, "
          f"registered cap 1900.0 core-min.  Any dollar figure is DERIVED at the "
          f"owner-stated $0.0513/core-h, NOT MEASURED "
          f"(COMPUTE_BUDGET_CHARTER section 5).")

    out = dict(
        tool="grade_m1.py", started_utc=started,
        finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        run_root=run_root, bench_root=bench_root,
        rule5=RULE5_STATEMENT, planted_zero=pz,
        registered=dict(cap_iterations=CAP_ITER, conv_k=CONV_K_TOL,
                        conv_omega=CONV_OMEGA_TOL, g2_band=G2_BAND,
                        g2_min_in_band=G2_MIN_IN_BAND, g2_ceiling=G2_CEILING,
                        g2_refuse_above=G2_REFUSE_ABOVE,
                        g3_separation=G3_SEPARATION, g3_min_cases=G3_MIN_CASES,
                        g4_max_capbound=G4_MAX_CAPBOUND),
        gates=[g0, g1, g2, g3, g4],
        rel_l2_null_vs_reference=g2_vals,
        rel_l2_arm_to_arm=g3_vals,
        rows={f"{a}/{c}": {k: v for k, v in r.items()
                           if k not in ("U_end", "k_end", "nut_end")}
              for (a, c), r in rows.items()},
        total_core_min_measured=total_measured,
        rows_cost_not_measured=n_unmeasured,
    )
    out_path = out_path or os.path.join(run_root, "gate_m1.json")
    json.dump(out, open(out_path, "w"), indent=2, sort_keys=True, default=str)
    print(f"\nwrote {out_path}")
    bad = any(g["verdict"] in ("GATE FAIL", "NOT A RESULT") for g in (g0, g1, g2, g3, g4))
    return 1 if bad else 0


def _aggregate_twice(vals, capbound_cids, label, predicate):
    """Section 4.3 rule 2: NO aggregate is reported once.  Converged-only and
    all-rows are printed side by side and are never merged."""
    all_rows = {c: v for c, v in vals.items()}
    conv_rows = {c: v for c, v in vals.items() if c not in capbound_cids}
    return dict(
        all_rows_n=len(all_rows),
        all_rows_meeting=sum(1 for v in all_rows.values() if predicate(v)),
        all_rows_max=(max(all_rows.values()) if all_rows else None),
        converged_rows_n=len(conv_rows),
        converged_rows_meeting=sum(1 for v in conv_rows.values() if predicate(v)),
        converged_rows_max=(max(conv_rows.values()) if conv_rows else None),
        capbound_excluded=sorted(set(vals) & set(capbound_cids)),
        aggregate_label=label,
    )


def _g2_partition_ok(vals):
    """The supervisor's structural G2 rule.  Iteration-matched cases (the 29
    hills, reference written at exactly this sweep's cap) must ALL meet the
    band; unmatched cases may contribute at most G2_UNMATCHED_MAX_OUT outliers.

    With no matched case present -- as in the synthetic selftest fixtures --
    this degenerates exactly to the old flat "at most 2 out of band" rule, which
    is why it does not disturb the fixtures that predate it.
    """
    matched_out = [c for c, v in vals.items()
                   if c.startswith(G2_MATCHED_PREFIX) and v > G2_BAND]
    unmatched_out = [c for c, v in vals.items()
                     if not c.startswith(G2_MATCHED_PREFIX) and v > G2_BAND]
    return not matched_out and len(unmatched_out) <= G2_UNMATCHED_MAX_OUT


def _g2_verdict(vals, missing, capbound, arm):
    cb = {c for (a, c) in capbound if a == arm}
    agg = _aggregate_twice(vals, cb, "rel-L2(U) null vs shipped reference",
                           lambda v: v <= G2_BAND)
    over = {c: v for c, v in vals.items() if v > G2_REFUSE_ABOVE}
    if over:
        verdict = "NOT A RESULT"
    elif missing:
        verdict = "GATE FAIL"
    else:
        ok_all = (_g2_partition_ok(vals)
                  and agg["all_rows_meeting"] >= G2_MIN_IN_BAND
                  and (agg["all_rows_max"] or 0.0) <= G2_CEILING)
        conv_vals = {c: v for c, v in vals.items() if c not in cb}
        ok_conv = (_g2_partition_ok(conv_vals)
                   and agg["converged_rows_meeting"] >= G2_MIN_IN_BAND
                   and (agg["converged_rows_max"] or 0.0) <= G2_CEILING)
        # section 4.3 rule 4: where the two disagree, the CONSERVATIVE verdict
        # is the one reported, and both are shown.
        verdict = "PASS" if (ok_all and ok_conv) else "GATE FAIL"
    return dict(gate="G2", name="null-arm identity (the sweep's planted control)",
                verdict=verdict, band=G2_BAND, min_in_band=G2_MIN_IN_BAND,
                ceiling=G2_CEILING, refuse_above=G2_REFUSE_ABOVE,
                partition_rule=("iteration-matched cases (prefix %r) must ALL "
                                "meet the band; at most %d unmatched outliers"
                                % (G2_MATCHED_PREFIX, G2_UNMATCHED_MAX_OUT)),
                matched_out_of_band=sorted(
                    c for c, v in vals.items()
                    if c.startswith(G2_MATCHED_PREFIX) and v > G2_BAND),
                aggregates=agg, over_refusal_threshold=over, missing=missing,
                label="a harness check, NOT a precision claim: the null re-solves "
                      "under a changed controlDict and against references of "
                      "unknown provenance")


def _g3_verdict(vals, missing, capbound):
    cb = {c for (_a, c) in capbound}
    agg = _aggregate_twice(vals, cb, "rel-L2(U) kOmega vs kOmegaSST",
                           lambda v: v > G3_SEPARATION)
    if missing:
        verdict = "GATE FAIL"
    else:
        ok_all = agg["all_rows_meeting"] >= G3_MIN_CASES
        ok_conv = agg["converged_rows_meeting"] >= G3_MIN_CASES
        verdict = "GATE REACHED" if (ok_all and ok_conv) else "GATE FAIL"
    return dict(gate="G3", name="arm separation", verdict=verdict,
                threshold=G3_SEPARATION, min_cases=G3_MIN_CASES,
                aggregates=agg, missing=missing,
                label="THIS IS A SPREAD AND ONLY A SPREAD. It measures how "
                      "sensitive the solution is to the choice of closure. It is "
                      "NOT a model-form uncertainty and NO interval is calibrated "
                      "from it: both arms are linear eddy-viscosity models sharing "
                      "the Boussinesq assumption, so their errors are CORRELATED, "
                      "NOT INDEPENDENT, and this spread SYSTEMATICALLY UNDERSTATES "
                      "true model-form uncertainty.")


# --------------------------------------------------------------------------
# SELFTEST
# --------------------------------------------------------------------------
def _w(path, txt):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(txt)


def _vec_field(vals):
    body = "\n".join(f"({a} {b} {c})" for a, b, c in vals)
    return ("FoamFile\n{\n    version 2.0;\n    format ascii;\n"
            "    class volVectorField;\n    object U;\n}\n"
            f"\ninternalField   nonuniform List<vector>\n{len(vals)}\n(\n{body}\n)\n;\n"
            "\nboundaryField\n{\n}\n")


def _sca_field(vals, name="k"):
    body = "\n".join(str(v) for v in vals)
    return ("FoamFile\n{\n    version 2.0;\n    format ascii;\n"
            f"    class volScalarField;\n    object {name};\n}}\n"
            f"\ninternalField   nonuniform List<scalar>\n{len(vals)}\n(\n{body}\n)\n;\n"
            "\nboundaryField\n{\n}\n")


def _fake_log(n_iter, k_res, om_res, model="kOmegaSST", end=True, exec_lines=None):
    out = [f"Selecting RAS turbulence model {model}"]
    for i in range(1, n_iter + 1):
        out.append(f"Time = {i}\n")
        out.append(f"DILUPBiCG:  Solving for Ux, Initial residual = 1e-9, "
                   f"Final residual = 1e-12, No Iterations 1")
        out.append(f"DILUPBiCG:  Solving for k, Initial residual = {k_res(i)}, "
                   f"Final residual = 1e-12, No Iterations 1")
        out.append(f"DILUPBiCG:  Solving for omega, Initial residual = {om_res(i)}, "
                   f"Final residual = 1e-12, No Iterations 1")
    for _ in range(exec_lines if exec_lines is not None else n_iter):
        out.append("ExecutionTime = 1 s  ClockTime = 1 s")
    if end:
        out.append("End")
    return "\n".join(out) + "\n"


def _fake_case(root, arm, cid, ncells, u_scale, n_iter, converge_at,
              model=None, with_status=True, end=True, exec_lines=None):
    d = os.path.join(root, arm, cid)
    model = model or ARMS[arm]
    _w(os.path.join(d, "constant", "turbulenceProperties"),
       f"simulationType RAS;\nRAS\n{{\n    RASModel        {model};\n}}\n")
    _w(os.path.join(d, "0", "U"), _vec_field([(1.0, 0, 0)] * ncells))
    import time as _t
    _t.sleep(0.01)
    vals = [(u_scale * (1 + 0.001 * i), 0.0, 0.0) for i in range(ncells)]
    _w(os.path.join(d, str(CAP_ITER), "U"), _vec_field(vals))
    for f in ("p", "k", "omega", "nut"):
        _w(os.path.join(d, str(CAP_ITER), f), _sca_field([0.1] * ncells, f))
    _w(os.path.join(d, "log.run"),
       _fake_log(n_iter,
                 lambda i: 1e-3 if i < converge_at else 1e-9,
                 lambda i: 1e-3 if i < converge_at else 1e-11,
                 model=model, end=end, exec_lines=exec_lines))
    if with_status:
        _w(os.path.join(d, "STATUS"),
           f"case={cid}\narm={arm}\nrc=0\nwall_s=600\nranks=1\ncore_min=10.0\n"
           f"cap_core_min=25.0\ncapped=0\nnote=clean\n")
    # the endTime fields must be NEWER than 0/U -- the age guard
    now = _t.time()
    for f in PHYSICS_FIELDS:
        os.utime(os.path.join(d, str(CAP_ITER), f), (now + 10, now + 10))
    os.utime(os.path.join(d, "0", "U"), (now, now))
    return d


def _check(label, ok, detail=""):
    print(f"  [{'ok  ' if ok else 'FAIL'}] {label}" + (f"  {detail}" if detail else ""))
    return bool(ok)


def _refuses(fn):
    try:
        fn()
    except Refusal:
        return True
    except Exception:
        return True
    return False


def selftest():
    print("grade_m1.py --selftest")
    print(f"  running under python3 "
          f"{'-O (assertions DELETED)' if not __debug__ else '(assertions live)'}")
    ok = True
    body = "\n".join(l for l in open(os.path.abspath(__file__), errors="replace")
                     .read().split("\n") if not l.strip().startswith("#"))
    ok &= _check("no `assert` statement anywhere in this file (L-332)",
                 not re.search(r"(?m)^\s*assert\b", body))
    ok &= _check("the verdict vocabulary is exactly the six words",
                 set(VERDICTS) == {"PASS", "GATE REACHED", "GATE FAIL",
                                   "NOT A RESULT", "BLOCKED", "PENDING"})

    with tempfile.TemporaryDirectory(prefix="m1g_") as tmp:
        d = _fake_case(tmp, "kOmega", "T1", 4, 1.0, CAP_ITER, 5000)
        log = parse_log(os.path.join(d, "log.run"))
        comp = completion(d, log)
        ok &= _check("a well-formed run is COMPLETE under rule 4",
                     comp["complete"], str(comp["clauses"]))
        conv = convergence_class(log)
        ok &= _check("convergence classified CONVERGED at the right iteration",
                     conv["state"] == "CONVERGED" and conv["n"] == 5000, str(conv))

        # rule 4 clauses, one planted failure each
        for clause, mutate in (
            ("end_line", lambda: _w(os.path.join(d, "log.run"),
                                    open(os.path.join(d, "log.run")).read()
                                    .replace("\nEnd\n", "\n"))),
            ("exec_count_eq_endTime", lambda: _w(
                os.path.join(d, "log.run"),
                open(os.path.join(d, "log.run")).read()
                .replace("ExecutionTime = 1 s  ClockTime = 1 s\n", "", 1))),
            ("fields_present", lambda: os.remove(
                os.path.join(d, str(CAP_ITER), "nut"))),
        ):
            src = open(os.path.join(d, "log.run"), errors="replace").read()
            keep = None
            if clause == "fields_present":
                keep = open(os.path.join(d, str(CAP_ITER), "nut")).read()
            mutate()
            c2 = completion(d, parse_log(os.path.join(d, "log.run")))
            ok &= _check(f"rule-4 clause `{clause}` refuses its planted failure",
                         c2["clauses"][clause] is False and not c2["complete"],
                         str(c2["clauses"]))
            _w(os.path.join(d, "log.run"), src)
            if keep is not None:
                _w(os.path.join(d, str(CAP_ITER), "nut"), keep)
                now = os.path.getmtime(os.path.join(d, "0", "U")) + 10
                os.utime(os.path.join(d, str(CAP_ITER), "nut"), (now, now))

        # age guard
        now = os.path.getmtime(os.path.join(d, str(CAP_ITER), "U")) + 100
        os.utime(os.path.join(d, "0", "U"), (now, now))
        c3 = completion(d, parse_log(os.path.join(d, "log.run")))
        ok &= _check("AGE GUARD refuses fields older than 0/U",
                     c3["clauses"]["age_guard"] is False and not c3["complete"])
        old = os.path.getmtime(os.path.join(d, str(CAP_ITER), "U")) - 100
        os.utime(os.path.join(d, "0", "U"), (old, old))

        # L-342 / R-RC: STATUS absent -> NOT MEASURED, physics STANDS
        os.remove(os.path.join(d, "STATUS"))
        c4 = completion(d, parse_log(os.path.join(d, "log.run")))
        ok &= _check("L-342/R-RC: absent STATUS is NOT MEASURED and does NOT void "
                     "intact physics", c4["complete"] and c4["rc"] is None and
                     "NOT MEASURED" in c4["rc_class"], c4["rc_class"])
        _w(os.path.join(d, "STATUS"), "rc=1\nwall_s=5\ncore_min=0.1\n")
        c5 = completion(d, parse_log(os.path.join(d, "log.run")))
        ok &= _check("R-RC: an rc VALUE of 1 is PHYSICS and refuses the row",
                     not c5["complete"] and c5["rc"] == 1)

        # C1 planted zero
        with tempfile.TemporaryDirectory(prefix="m1pz_") as t2:
            pz = planted_zero_control(os.path.join(d, str(CAP_ITER), "U"), t2)
        ok &= _check("C1: the reader SEES a plant made on disk",
                     pz["passed"] and abs(pz["reader_max_change"] - PLANT) < 1e-12,
                     str(pz))
        # L-314 planted failure of C1 itself: a BLIND reader must be caught
        global read_internal_field
        real = read_internal_field
        try:
            read_internal_field = lambda p: dict(kind="uniform", rank=1, n=1,
                                                 values=[0.0])
            with tempfile.TemporaryDirectory(prefix="m1pz2_") as t3:
                blind = planted_zero_control(os.path.join(d, str(CAP_ITER), "U"), t3)
            ok &= _check("C1 planted failure: a BLIND reader reports passed=False",
                         blind["passed"] is False, str(blind))
        finally:
            read_internal_field = real

    # convergence classification: CAP-BOUND, and the "sustained" requirement
    log_cap = parse_log_from_text(_fake_log(100, lambda i: 1e-3, lambda i: 1e-3))
    ok &= _check("never meeting the criterion is CAP-BOUND",
                 convergence_class(log_cap)["state"] == "CAP-BOUND")
    log_blip = parse_log_from_text(_fake_log(
        100, lambda i: 1e-9 if i != 90 else 1e-3, lambda i: 1e-11))
    cc = convergence_class(log_blip)
    ok &= _check("a LATE excursion moves the converged iteration, not the class",
                 cc["state"] == "CONVERGED" and cc["n"] == 91, str(cc))

    # rel_l2 and its refusals
    ok &= _check("rel_l2 of a field against itself is 0",
                 rel_l2([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]) == 0.0)
    ok &= _check("rel_l2 refuses a length mismatch",
                 _refuses(lambda: rel_l2([1.0], [1.0, 2.0])))
    ok &= _check("rel_l2 refuses a zero-norm reference",
                 _refuses(lambda: rel_l2([1.0], [0.0])))
    ok &= _check("rel_l2 of a 1e-2 perturbation reads ~1e-2",
                 abs(rel_l2([1.01, 1.01], [1.0, 1.0]) - 0.01) < 1e-9)

    # G2 / G3 verdicts on synthetic value sets
    good = {f"c{i}": 1e-5 for i in range(N_CASES)}
    ok &= _check("G2 PASSes when every case is inside the band",
                 _g2_verdict(good, [], set(), NULL_ARM)["verdict"] == "PASS")
    edge = dict(good); edge["c0"] = 5e-3; edge["c1"] = 5e-3; edge["c2"] = 5e-3
    ok &= _check("G2 GATE FAILs at 36 of 39 in band",
                 _g2_verdict(edge, [], set(), NULL_ARM)["verdict"] == "GATE FAIL")
    catastrophe = dict(good); catastrophe["c0"] = 0.5
    ok &= _check("G2 says NOT A RESULT above the refusal threshold",
                 _g2_verdict(catastrophe, [], set(), NULL_ARM)["verdict"] == "NOT A RESULT")
    # --- the supervisor's structural G2 partition, with its planted-failure
    # proof (L-314): the SAME two-outlier count PASSES when the outliers are
    # unmatched cases and GATE FAILS when one of them is an iteration-matched
    # hill.  Without this pair the partition could be a no-op and read as one.
    n_hill = 29
    part_ok = {f"alpha_h{i}": 1e-5 for i in range(n_hill)}
    part_ok.update({f"c{i}": 1e-5 for i in range(N_CASES - n_hill)})
    part_ok["c0"] = 5e-3; part_ok["c1"] = 5e-3          # 2 UNMATCHED outliers
    ok &= _check("G2 PASSes with 2 outliers when BOTH are unmatched cases",
                 _g2_verdict(part_ok, [], set(), NULL_ARM)["verdict"] == "PASS")
    part_bad = dict(part_ok)
    part_bad["c1"] = 1e-5                                # give the budget back
    part_bad["alpha_h0"] = 5e-3                          # spend it on a HILL
    r_bad = _g2_verdict(part_bad, [], set(), NULL_ARM)
    ok &= _check("G2 GATE FAILs when one outlier is an iteration-matched hill, "
                 "at the SAME 37-of-39 count the flat rule would have passed",
                 r_bad["verdict"] == "GATE FAIL"
                 and r_bad["aggregates"]["all_rows_meeting"] >= G2_MIN_IN_BAND
                 and r_bad["matched_out_of_band"] == ["alpha_h0"])
    ok &= _check("the partition rule is a no-op on fixtures with no hill "
                 "(so it cannot silently change the pre-existing controls)",
                 _g2_partition_ok({f"c{i}": 1e-5 for i in range(N_CASES)}))

    sep = {f"c{i}": 5e-2 for i in range(N_CASES)}
    ok &= _check("G3 GATE REACHED when the arms separate",
                 _g3_verdict(sep, [], set())["verdict"] == "GATE REACHED")
    nosep = {f"c{i}": 1e-9 for i in range(N_CASES)}
    ok &= _check("G3 GATE FAILs when the arms do not separate",
                 _g3_verdict(nosep, [], set())["verdict"] == "GATE FAIL")
    ok &= _check("G3 carries its non-uncertainty label",
                 "NOT a model-form uncertainty" in _g3_verdict(sep, [], set())["label"])

    # section 4.3: no aggregate is reported once, and CAP-BOUND rows are excluded
    mixed = dict(good); mixed["c0"] = 5e-3
    agg = _g2_verdict(mixed, [], {(NULL_ARM, "c0")}, NULL_ARM)["aggregates"]
    ok &= _check("aggregates are reported TWICE (all rows and converged only)",
                 agg["all_rows_n"] == N_CASES and
                 agg["converged_rows_n"] == N_CASES - 1 and
                 agg["capbound_excluded"] == ["c0"], str(agg))

    # rule 5 statement is emitted
    ok &= _check("the output states that standing rule 5 DOES NOT APPLY",
                 "RULE 5 DOES NOT APPLY" in RULE5_STATEMENT.upper()
                 and "GCI" in RULE5_STATEMENT)

    print("SELFTEST", "PASS" if ok else "FAIL")
    return 0 if ok else 2


def parse_log_from_text(txt):
    with tempfile.NamedTemporaryFile("w", suffix=".log", delete=False) as fh:
        fh.write(txt)
        p = fh.name
    try:
        return parse_log(p)
    finally:
        os.unlink(p)


PROOFS = {
    "C1": "a blind reader must make planted_zero_control report passed=False",
    "C4": "removing the End line must make completion() report incomplete",
    "C5": "an absent STATUS must be NOT MEASURED, never a failure",
    "G3-LABEL": "the spread label must say it is NOT an uncertainty",
}


def planted_failure_proof(code):
    if code not in PROOFS:
        print(f"unknown proof {code}; known: {sorted(PROOFS)}", file=sys.stderr)
        return 2
    print(f"planted-failure proof {code}: {PROOFS[code]}")
    return selftest()


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Refusal as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)
