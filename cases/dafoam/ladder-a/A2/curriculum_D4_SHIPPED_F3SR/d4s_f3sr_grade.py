#!/usr/bin/env python
"""D4S-F3SR GRADER -- the two-row endpoint FD verdict under ONE stationarity
acceptance rule, with the AGE-CLAUSE and CAP-FRAME repairs.  Derived from
D4S-F3S's `d4s_f3s_grade.py` (md5 2ed0651c..., frozen at 8dfb4598): the FD
gate G5, the planted-zero control G6, the blind-reader control G6b, the count
refusals G7, the positional terminal statement, the kernel-rc clause,
G10/G11/G12 and the L-342 field classes are ported with their bands and
thresholds UNCHANGED (cited by value from curriculum_D4/PREREGISTRATION.md:82
-- band D 5 % per component and aggregate, zero sign flips, band E plateau
10 %).  NO BAND, THRESHOLD, CAP OR LABEL MOVES.

THE TWO REPAIRS, and they are the whole reason this file exists:

  D4S-F3S-AGE-DEF-1.  The predecessor's ARTEFACTS list (`:61`) age-checked
  `OptView.hst`, which is a STAGED INPUT of this item and never a product --
  copied with `cp -a` (`d4s_f3s_stage_arm.sh:61-63`, "mtime semantics = cp -a,
  PRESERVE") by an item that re-runs no optimiser.  A FILE THAT IS NEVER
  PRODUCED CAN NEVER POST-DATE THE LAUNCH, so the clause was UNSATISFIABLE BY
  CONSTRUCTION and D4S-F3S was recorded NOT A RESULT on that one limb with 19
  of 20 readings PASS.  Here: ARTEFACTS holds ONLY files this item's own run
  produces; the staged inputs are named in STAGED_INPUTS_EXCLUDED_FROM_AGE
  with their reason, are bound to the run's own staged-input manifest, and are
  checked by the INVERSE clause (a staged input must be NOT NEWER than the
  datum).  THE EXCLUSION IS REGISTERED AND CHECKED, NEVER SILENT.

  The predecessor's 26/26 selftest could not catch it: the fixture CREATED
  `OptView.hst` fresh (`d4s_f3s_grade.py:599-601`) against a datum pinned at
  epoch 1000000000, so real staging semantics were never exercised.  A PASSING
  SELFTEST IS WHAT MAKES THIS CLASS DANGEROUS.  Here the fixture STAGES with a
  real `cp -a` from a real source tree whose mtimes predate the datum, and the
  age clause is driven BOTH WAYS -- it must REFUSE on a genuinely stale
  product and PASS on a fresh one, with the staging semantics real.

  D4S-F3S-CAP-DEF-1 (the D6 shape one level up).  The cap was ENFORCED in the
  container (`timeout -k 60 1800`) and GRADED from a HOST bracket that
  strictly contains it, so an arm stopped exactly at its own deadline recorded
  a wall ABOVE the cap and tripped `within_cap` -- a GATE FAIL manufactured by
  the measurement frame.  Here the cap is UNCHANGED at 120.0 core-min, the
  enforced deadline is SHORTENED by a registered frame allowance, and G10
  BINDS the container's own kernel clock beside the host bracket instead of
  printing it as a diagnostic.

New relative to the predecessor, and only these:
  G-ACC  the stationarity acceptance of EVERY primal, re-evaluated HOST-SIDE
         from the per-primal captures with the SAME module the instrument used
         in-container (`d4s_f3s_accept.py`, md5 asserted), the capture count
         bound to the accept records, to the FD file's `n_primals` and to the
         arm log's `Running Primal Solver` count; the disarm record's read-back
         must equal the registered DISARM_TOL_DIFF.
  G1     the AGE CLAUSE, repaired: products age-checked, staged inputs
         excluded BY NAME and checked by the INVERSE clause against the run's
         own manifest.
  G10    the CAP FRAME: the container's own clock bound beside the host
         bracket; NOT_MEASURED falls back to the host bracket alone, which is
         the STRICTER reading, so the fallback can never turn a fail into a
         pass.
  P5/P6/P7  the new registered predictions.
  G9     per ROW: F-S's log must carry the SHIPPED `libidwarp.so` md5 and the
         SHIPPED digest, F-P the PATCHED pair; the two md5s must DIFFER.
  P1-P4  the registered predictions, scored HIT/MISS/UNSCORED in the output.
Every refusal is `raise`/`sys.exit(2)`; NO `assert` (L-332); identical under
`python3 -O`.  `--selftest` builds a sacrificial root from REAL artefacts
(curriculum_D4's F3 table and primal blocks) and drives every gate through
its planted mutant.
"""
import argparse
import hashlib
import importlib.util
import json
import math
import os
import re
import shutil
import sys
import tempfile

VOCAB = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")
ITEM = "D4S-F3SR"
ARMS = ["F-S", "F-P"]
ROW_OF = {"F-S": "SHIPPED", "F-P": "PATCHED"}
SO_MD5 = {"SHIPPED": "f0fcb488e0e98156575cd19548e91663",
          "PATCHED": "85f59e87253e0a71a813f64ca6e4c425"}
DIGEST = {"SHIPPED": "sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc",
          "PATCHED": "sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35"}
CAPS = {"F-S": 120.0, "F-P": 120.0}
ITEM_CEILING_CORE_MIN = 240.0
# ---- COST ANCHOR (PREREGISTRATION.md section 4).  The predecessor priced from
# an ARM-TOTAL anchor (D4's whole F3 arm, 709 s, carrying 32.2 s/primal of
# fixed overhead) and MISSED P4 at ratios 0.814 / 0.791.  The anchor was wrong,
# not the rate.  This item prices from the TWO-TERM decomposition MEASURED on
# the predecessor's own two arms:
#     wall_s = OVERHEAD_S + N_PRIMALS * RATE_S_PER_PRIMAL
#   F-S 577 s = 114.273 + 22 * 21.033      (sum of the instrument's own
#   F-P 561 s = 115.789 + 22 * 20.237       per-primal wall_s, both arms)
# pooled: OVERHEAD 115.0 s, RATE 20.635 s/primal, N 22
OVERHEAD_S_ANCHOR = 115.0
RATE_S_PER_PRIMAL_ANCHOR = 20.635
N_PRIMALS_ANCHOR = 22
PREDICTED = {"F-S": 37.931, "F-P": 37.931}
P4_BAND = (0.8, 1.5)          # INHERITED BY CITATION from D4S-F3S section 6, UNCHANGED
P5_BAND = (0.90, 1.15)        # NEW, TIGHTER; can only turn a HIT into a MISS
# ---- CAP FRAME (PREREGISTRATION.md section 4b).  The cap does not move; the
# enforced deadline is shortened by the allowance.  (TMO + ALLOWANCE)*4/60 = 120.0
TMO_REGISTERED_S = 1710
FRAME_ALLOWANCE_S = 90
KILL_GRACE_S = 60             # `timeout -k 60` TERM->KILL escalation
RANKS = 4
CPUSET_REGISTERED = [5, 6, 7, 9]
DELIVERED_FLOOR = 3.0
COMPONENTS_REGISTERED = [["shape", 46], ["shape", 18], ["shape", 0], ["twist", 0], ["patchV", 1]]
N_COMPONENTS_REGISTERED = 5
FD_BAND_PCT_PER_COMPONENT = 5.0
FD_BAND_PCT_AGGREGATE = 5.0
PLATEAU_TOL_PCT = 10.0
PLANT = 1.234e-03
TERMINAL_STATEMENT = "Finalising parallel run"
DISARM_TOL_DIFF = 1.0e12
P2_COMPONENT = "shape[18]"
P3_REL_TOL = 1.0e-12
D4_PATCHED_F3_TABLE = "/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/F3/d4_fd_endpoint.json"
D4S_F3S_REFERENCE_TABLE = {
    "F-S": "/home/ubuntu/certonomous-runs/CURRICULUM-D4S-F3S-a2-wing-cdmin/F-S/d4s_f3s_fd_endpoint.json",
    "F-P": "/home/ubuntu/certonomous-runs/CURRICULUM-D4S-F3S-a2-wing-cdmin/F-P/d4s_f3s_fd_endpoint.json"}
P6_REL_TOL = 1.0e-12
# ---- THE AGE-CHECKED SET: FILES THIS ITEM'S OWN RUN PRODUCES, AND ONLY THOSE.
# Every name here is absent from BOTH source arm-O trees (verified from disk
# 2026-08-27) and is written inside the container by `d4_endpoint_physical.py`
# or `d4s_f3s_fd_endpoint.py`.  `OptView.hst` is NOT here -- see below.
ARTEFACTS = ["d4_endpoint_dvs.json", "d4_endpoint_dvs_PHYSICAL.json",
             "d4_endpoint_dvs_DRIVERSCALED.json", "d4_major_history.json",
             "d4s_f3s_fd_endpoint.json", "d4s_f3s_fd_endpoint.jsonl", "d4s_f3s_accept.jsonl"]
# ---- THE REGISTERED EXCLUSIONS: STAGED INPUTS, NAMED, WITH THEIR REASON.
# These are carried into the arm by `d4s_f3sr_stage_arm.sh` with `cp -a`
# (mtime PRESERVED) and are never written by this item, which runs no
# optimiser.  They are NOT thereby unchecked: the INVERSE clause below
# requires each to be NOT NEWER than the datum, which is the positive proof
# that it is an input this item carried in rather than a product it made.
# The two clauses are complementary and jointly exhaustive over the registered
# files -- no file can satisfy both, and every registered file must satisfy
# exactly one.
STAGED_INPUTS_EXCLUDED_FROM_AGE = {
    "OptView.hst": ("staged input: the optimiser history the endpoint is READ FROM. "
                    "Copied by d4s_f3sr_stage_arm.sh with `cp -a` (mtime PRESERVE); this "
                    "item re-runs no optimiser and never writes it, so an age clause on it "
                    "is unsatisfiable by construction (D4S-F3S-AGE-DEF-1). Gated instead by "
                    "the INVERSE clause and by md5 equality with the source."),
    "opt_IPOPT.txt": ("staged input: the optimiser log beside OptView.hst, carried by the "
                      "same `cp -a`. Named here even though the predecessor never listed it, "
                      "because an unclassified file is the defect this repair exists to end; "
                      "d5_run_arm.sh:292-294 refuses on this pair together.")}
STAGED_INPUT_MANIFEST = ".d4s_f3sr_staged_inputs.json"
FIELDS_PHYSICS = ["ARM", "ROW", "DIGEST", "rc", "wall_s", "ranks", "core_min", "cap_core_min",
                  "enforced_core_min", "memory", "inspect_exit", "oomkilled", "cpuset", "log", "stamp"]
FIELDS_INFRASTRUCTURE = ["memavail_pre_GiB", "memavail_post_GiB", "delivered", "siblings_pre",
                         "siblings_post", "container_wall_s", "frame_allowance_s"]
HERE = os.path.dirname(os.path.abspath(__file__))


class Refuse(Exception):
    pass


def refuse(where, detail):
    raise Refuse("%s: %s" % (where, json.dumps(detail, sort_keys=True, default=str)))


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def read_json(path, where):
    if not os.path.isfile(path):
        refuse(where, {"absent": path})
    if os.path.getsize(path) == 0:
        refuse(where, {"empty_file": path})
    with open(path) as fh:
        try:
            return json.load(fh)
        except Exception as exc:                        # noqa: BLE001
            refuse(where, {"unparseable": path, "error": repr(exc)[:300]})


def read_jsonl(path, where):
    if not os.path.isfile(path):
        refuse(where, {"absent": path})
    out = []
    for k, line in enumerate(open(path)):
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except Exception as exc:                        # noqa: BLE001
            refuse(where, {"unparseable_line": k + 1, "path": path, "error": repr(exc)[:200]})
    return out


def load_accept_module(path):
    if not os.path.isfile(path):
        refuse("G-ACC", {"accept_module_absent": path})
    spec = importlib.util.spec_from_file_location("d4s_f3s_accept", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ------------------------------------------------------------------ ledger
PHYS_RE = {
    "ARM": r"ARM=(\S+)", "ROW": r"ROW=(\S+)", "DIGEST": r"DIGEST=(\S+)", "rc": r" rc=(\d+)",
    "wall_s": r"wall_s=(\d+)", "ranks": r"ranks=(\d+)", "core_min": r"core_min=([\d.]+)",
    "cap_core_min": r"cap_core_min=([\d.]+)", "enforced_core_min": r"enforced_core_min=([\d.]+)",
    "memory": r"memory=(\S+)", "inspect": r"inspect\(exit,oomkilled\)=\[(\S+) (\S+)\]",
    "cpuset": r"cpuset=(\S+)", "log": r"log=(\S+)", "stamp": r"stamp=(\S+)"}
INFRA_RE = {"memavail_pre_GiB": r"memavail_pre_GiB=(\S+)", "memavail_post_GiB": r"memavail_post_GiB=(\S+)",
            "delivered": r"delivered_cores_mean=\[([^\]]*)\]", "siblings_pre": r"siblings_pre=\[([^\]]*)\]",
            "siblings_post": r"siblings_post=\[([^\]]*)\]",
            "container_wall_s": r"container_wall_s=(\S+)", "frame_allowance_s": r"frame_allowance_s=(\S+)"}


def _infra_float(key, tok):
    """ABSENT -> None (NOT_MEASURED, disclosed); PRESENT-BUT-GARBAGE -> REFUSE (C1)."""
    if tok is None or tok == "NOT_MEASURED":
        return None
    try:
        return float(tok)
    except ValueError:
        refuse("ledger", {"present_but_unparseable_infrastructure_field": key, "value": tok})


def read_ledger(path):
    if not os.path.isfile(path):
        refuse("ledger", {"absent": path})
    rows, item_lines = [], []
    for line in open(path, errors="replace"):
        line = line.rstrip("\n")
        if line.startswith("ITEM="):
            item_lines.append(line)
            continue
        if not line.startswith("ARM="):
            continue
        row, missing = {}, []
        for k, rx in PHYS_RE.items():
            m = re.search(rx, line)
            if not m:
                missing.append(k)
                continue
            if k == "inspect":
                row["inspect_exit"], row["oomkilled"] = m.group(1), m.group(2)
            else:
                row[k] = m.group(1)
        if missing:
            refuse("ledger", {"physics_field_absent": missing, "line": line[:160]})
        for k in ("rc", "wall_s", "ranks"):
            row[k] = int(row[k])
        for k in ("core_min", "cap_core_min", "enforced_core_min"):
            row[k] = float(row[k])
        row["infra_not_measured"] = []
        for k, rx in INFRA_RE.items():
            m = re.search(rx, line)
            tok = m.group(1) if m else None
            if k in ("memavail_pre_GiB", "memavail_post_GiB"):
                row[k] = _infra_float(k, tok)
            elif k == "delivered":
                first = tok.split()[0] if tok else None
                row[k] = _infra_float(k, first)
            elif k in ("container_wall_s", "frame_allowance_s"):
                row[k] = _infra_float(k, tok)
            else:
                row[k] = tok
            if row[k] is None:
                row["infra_not_measured"].append(k)
        rows.append(row)
    if [l for l in item_lines if l != "ITEM=%s" % ITEM]:
        refuse("ledger", {"foreign_item_lines": item_lines})
    return rows


def last_row(rows, arm):
    hits = [r for r in rows if r["ARM"] == arm]
    return hits[-1] if hits else None


# ------------------------------------------------------------------- gates
def terminal_statement_ok(log_path):
    if not os.path.isfile(log_path):
        return False, {"log_absent": log_path}
    text = open(log_path, "rb").read().replace(b"\x00", b"").decode("utf-8", errors="replace")
    nonempty = [ln.rstrip() for ln in text.splitlines() if ln.strip()]
    if not nonempty:
        return False, {"log_empty": log_path}
    last = nonempty[-1]
    ok = TERMINAL_STATEMENT in last
    anywhere = any(TERMINAL_STATEMENT in ln for ln in nonempty)
    return ok, {"log": os.path.basename(log_path), "last_nonempty_line": last[:160],
                "terminal_ok_POSITIONAL": bool(ok), "substring_anywhere_NOT_THE_TEST": bool(anywhere)}


def g_completion_arm(base, work, row, arm):
    """G1 for one SOLVER arm: kernel rc == 0 and OOMKilled false; the positional
    terminal statement; THE REPAIRED AGE CLAUSE.

    D4S-F3S-AGE-DEF-1.  Two complementary clauses over two disjoint registered
    sets, and every registered file must satisfy exactly one:
      PRODUCTS (ARTEFACTS)                 mtime STRICTLY NEWER than the datum
      STAGED INPUTS (excluded BY NAME)     mtime NOT NEWER than the datum
    The second is the INVERSE clause: excluding a file from the age check does
    NOT leave it unchecked.  It is the positive proof that the file is an
    input this item carried in rather than a product it made -- which is
    exactly the fact the predecessor asserted in prose and never tested.
    The exclusions are also bound to the run's OWN staged-input manifest, so
    the grader reads what the stager recorded rather than trusting this list.
    """
    # ---- the two registered sets must be DISJOINT.  CHECKED FIRST, because a
    # ---- file classified as both produced and carried in makes every clause
    # ---- below meaningless.  This is the static shape of D4S-F3S-AGE-DEF-1.
    overlap = sorted(set(ARTEFACTS) & set(STAGED_INPUTS_EXCLUDED_FROM_AGE))
    if overlap:
        refuse("G1-age", {"arm": arm, "PRODUCT_AND_STAGED_INPUT_OVERLAP": overlap,
                          "note": "a file cannot be both produced by this item and carried into it"})
    out = {"arm": arm, "rc": row["rc"], "inspect_exit": row["inspect_exit"], "oomkilled": row["oomkilled"]}
    if str(row["inspect_exit"]) != str(row["rc"]):
        refuse("G1", {"arm": arm, "harness_rc_vs_kernel_rc_disagree": [row["rc"], row["inspect_exit"]]})
    out["rc_clause_pass"] = bool(row["rc"] == 0 and str(row["oomkilled"]).lower() == "false")
    ok, det = terminal_statement_ok(os.path.join(base, row["log"]))
    out["terminal_clause_pass"], out["terminal_detail"] = bool(ok), det
    ep = os.path.join(work, ".d4s_f3sr_stage_%s_copy_epoch" % arm)
    if not os.path.isfile(ep):
        refuse("G1-age", {"arm": arm, "copy_epoch_absent": ep})
    datum = int(open(ep).read().strip())
    # ---- the datum sentinel must exist and must BE the datum ----------
    ref = os.path.join(work, ".d4s_f3sr_age_ref")
    if not os.path.isfile(ref):
        refuse("G1-age", {"arm": arm, "age_reference_sentinel_absent": ref,
                          "note": "the datum was not taken from a file touched last at stage time"})
    if int(os.path.getmtime(ref)) != datum:
        refuse("G1-age", {"arm": arm, "age_reference_mtime_disagrees_with_frozen_datum":
                          [int(os.path.getmtime(ref)), datum]})
    # ---- CLAUSE A: every registered PRODUCT strictly newer than the datum
    arts, stale = [], []
    for a in ARTEFACTS:
        p = os.path.join(work, a)
        if not os.path.isfile(p):
            refuse("G1-age", {"arm": arm, "graded_artifact_absent": p})
        m = int(os.path.getmtime(p))
        arts.append({"artifact": a, "mtime": m, "newer_than_datum": bool(m > datum)})
        if m <= datum:
            stale.append(a)
    out["age_datum_epoch"], out["age_rows"], out["n_stale"] = datum, arts, len(stale)
    out["age_clause_pass"] = bool(not stale)
    # ---- CLAUSE B (INVERSE): every registered STAGED INPUT not newer -----
    man_path = os.path.join(work, STAGED_INPUT_MANIFEST)
    if not os.path.isfile(man_path):
        refuse("G1-age", {"arm": arm, "staged_input_manifest_absent": man_path,
                          "note": "the age exclusions were never registered by the run that claims them"})
    man = read_json(man_path, "G1-age")
    man_names = sorted(r["name"] for r in man.get("staged_inputs", []))
    if man_names != sorted(STAGED_INPUTS_EXCLUDED_FROM_AGE):
        refuse("G1-age", {"arm": arm, "COUNT_REFUSAL": "manifest names differ from the registered exclusions",
                          "manifest": man_names, "registered": sorted(STAGED_INPUTS_EXCLUDED_FROM_AGE)})
    if int(man.get("age_datum", -1)) != datum:
        refuse("G1-age", {"arm": arm, "manifest_datum_vs_frozen_datum": [man.get("age_datum"), datum]})
    excl = []
    for rec in sorted(man["staged_inputs"], key=lambda r: r["name"]):
        name = rec["name"]
        p = os.path.join(work, name)
        if not os.path.isfile(p):
            refuse("G1-age", {"arm": arm, "registered_staged_input_absent": p,
                              "reason_registered": STAGED_INPUTS_EXCLUDED_FROM_AGE[name][:80]})
        m = int(os.path.getmtime(p))
        d5 = md5_of(p)
        if m > datum:
            refuse("G1-age", {"arm": arm, "EXCLUSION_REFUSED": name, "mtime": m, "datum": datum,
                              "note": "a file excluded from the age clause as a STAGED INPUT is NEWER "
                                      "than the datum -- it is not a staged input and the exclusion is void"})
        if d5 != rec["src_md5"] or d5 != rec["dst_md5"]:
            refuse("G1-age", {"arm": arm, "EXCLUSION_REFUSED": name, "md5_on_disk": d5,
                              "src_md5_recorded": rec["src_md5"], "dst_md5_recorded": rec["dst_md5"],
                              "note": "the staged input on disk is not the bytes the stager copied"})
        excl.append({"staged_input": name, "mtime": m, "not_newer_than_datum": True,
                     "md5": d5, "src": man.get("src"), "reason": STAGED_INPUTS_EXCLUDED_FROM_AGE[name]})
    out["staged_inputs_excluded"] = excl
    out["n_staged_inputs_excluded"] = len(excl)
    out["inverse_clause_pass"] = bool(len(excl) == len(STAGED_INPUTS_EXCLUDED_FROM_AGE))
    out["pass"] = bool(out["rc_clause_pass"] and out["terminal_clause_pass"]
                       and out["age_clause_pass"] and out["inverse_clause_pass"])
    return out


def g_acceptance_arm(base, work, row, arm, acc):
    """G-ACC: every primal accepted by the stationarity rule, re-evaluated here."""
    out = {"arm": arm}
    fd = read_json(os.path.join(work, "d4s_f3s_fd_endpoint.json"), "G-ACC")
    recs = read_jsonl(os.path.join(work, "d4s_f3s_accept.jsonl"), "G-ACC")
    accepts = [r for r in recs if r.get("kind") == "accept"]
    prim = read_jsonl(os.path.join(work, "d4s_f3s_fd_endpoint.jsonl"), "G-ACC")
    disarm = [r for r in prim if r.get("kind") == "disarm"]
    if len(disarm) != 1:
        refuse("G-ACC", {"arm": arm, "disarm_records": len(disarm), "required": 1})
    out["disarm"] = disarm[0]
    out["disarm_effective_ok"] = bool(float(disarm[0].get("effective", -1)) == DISARM_TOL_DIFF)
    caps = sorted(f for f in os.listdir(work) if re.match(r"d4s_f3s_primal_\d{3}_.*\.log$", f))
    log_text = open(os.path.join(base, row["log"]), errors="replace").read()
    n_log = sum(1 for ln in log_text.splitlines() if ln.startswith("Running Primal Solver"))
    counts = {"captures": len(caps), "accept_records": len(accepts),
              "fd_n_primals": fd.get("n_primals"), "log_running_primal_solver": n_log}
    out["counts"] = counts
    if len(caps) == 0:
        refuse("G-ACC", {"arm": arm, "COUNT_REFUSAL": "zero primal captures", "counts": counts})
    if not (len(caps) == len(accepts) == fd.get("n_primals") == n_log):
        refuse("G-ACC", {"arm": arm, "COUNT_REFUSAL": "capture / record / log counts disagree", "counts": counts})
    per, n_acc = [], 0
    for k, f in enumerate(caps):
        try:
            ev = acc.evaluate(acc.parse_primal_text(open(os.path.join(work, f), errors="replace").read()))
        except acc.Refusal as exc:
            refuse("G-ACC", {"arm": arm, "capture": f, "reader_refused": str(exc)[:200]})
        rec = accepts[k] if k < len(accepts) else {}
        agree = bool(rec.get("accepted") is True and ev["accepted"])
        n_acc += 1 if ev["accepted"] else 0
        per.append({"capture": f, "tag": rec.get("tag"), "regraded_accepted": bool(ev["accepted"]),
                    "instrument_accepted": rec.get("accepted"), "agree": agree,
                    "failures": ev["failures"], "nuTilda_r_end": ev["per_equation"]["nuTilda"]["r_end"],
                    "max_rel_drift_nuTilda": ev["per_equation"]["nuTilda"]["max_rel_drift"],
                    "cont_local_end": ev["cont_local_end"]})
    out["per_primal"] = per
    out["n_primals"], out["n_accepted_regraded"] = len(caps), n_acc
    out["all_agree"] = bool(all(p["agree"] for p in per))
    out["accept_module_md5_instrument"] = fd.get("accept_module_md5")
    out["pass"] = bool(n_acc == len(caps) and out["all_agree"] and out["disarm_effective_ok"])
    return out


def g_fd(fd, where="G5"):
    rows = fd.get("rows")
    n_registered = N_COMPONENTS_REGISTERED
    if rows is None:
        refuse(where, {"rows_key_absent": True, "n_rows": 0, "n_registered": n_registered})
    if not isinstance(rows, list):
        refuse(where, {"rows_not_a_list": type(rows).__name__, "n_registered": n_registered})
    n_rows = len(rows)
    if n_rows == 0:
        refuse(where, {"COUNT_REFUSAL": "empty component set", "n_rows": 0, "n_registered": n_registered})
    if n_rows != n_registered:
        refuse(where, {"COUNT_REFUSAL": "short or long component set", "n_rows": n_rows, "n_registered": n_registered})
    got = [[r.get("dv"), r.get("idx")] for r in rows]
    if got != COMPONENTS_REGISTERED:
        refuse(where, {"COUNT_REFUSAL": "component set is not the registered set, in the registered order",
                       "n_rows": n_rows, "got": got, "registered": COMPONENTS_REGISTERED})
    eta = float(str(fd["eta_used"]).strip("'\""))
    graded, near_zero, ungradeable, n_plateau = [], [], [], 0
    for r in rows:
        tag = "%s[%d]" % (r["dv"], r["idx"])
        if r.get("status") != "PLANNED":
            (near_zero if r.get("status") == "NEAR_ZERO" else ungradeable).append(
                {"component": tag, "status": r.get("status"), "J_adj": r.get("J_adj"),
                 "max_clearance": r.get("max_clearance")})
            continue
        fdb = r.get("fd") or {}
        lo, hi = fdb.get("s_lo"), fdb.get("s_hi")
        if not (lo and hi and lo.get("ok") and hi.get("ok")):
            ungradeable.append({"component": tag, "status": "FD_STEP_FAILED", "s_lo": lo, "s_hi": hi})
            continue
        d_lo = float(str(lo["d"]).strip("'\""))
        d_hi = float(str(hi["d"]).strip("'\""))
        j = float(str(r["J_adj"]).strip("'\""))
        if d_hi == 0.0:
            ungradeable.append({"component": tag, "status": "FD_ZERO_AT_S_HI"})
            continue
        plateau = 100.0 * abs(d_hi - d_lo) / abs(d_hi)
        n_plateau += 1
        rel = 100.0 * abs(j - d_hi) / abs(d_hi)
        graded.append({"component": tag, "s_lo": lo["step"], "s_hi": hi["step"], "d_lo": d_lo, "d_hi": d_hi,
                       "J_adj": j, "plateau_pct": plateau, "plateau_ok": bool(plateau <= PLATEAU_TOL_PCT),
                       "rel_err_pct": rel, "in_band": bool(rel <= FD_BAND_PCT_PER_COMPONENT),
                       "sign_flip": bool(j * d_hi < 0.0)})
    if n_plateau != len(graded):
        refuse(where, {"plateau_comparisons": n_plateau, "graded_rows": len(graded)})
    if graded:
        num = math.sqrt(sum((g["J_adj"] - g["d_hi"]) ** 2 for g in graded))
        den = math.sqrt(sum(g["d_hi"] ** 2 for g in graded))
        agg = 100.0 * num / den if den else float("inf")
    else:
        agg = None
    return {"n_rows": n_rows, "n_registered": n_registered, "eta_used": eta, "eta_floored": fd.get("eta_floored"),
            "n_graded": len(graded), "n_near_zero": len(near_zero), "n_ungradeable": len(ungradeable),
            "graded": graded, "near_zero": near_zero, "ungradeable": ungradeable,
            "aggregate_rel_err_pct": agg, "aggregate_band_pct": FD_BAND_PCT_AGGREGATE,
            "n_sign_flips": sum(1 for g in graded if g["sign_flip"]),
            "n_without_plateau": sum(1 for g in graded if not g["plateau_ok"]),
            "coverage": "%d of %d" % (len(graded), n_registered)}


def fd_verdict(f):
    if f["n_graded"] == 0:
        return "NOT A RESULT"
    if (f["aggregate_rel_err_pct"] is not None and f["aggregate_rel_err_pct"] <= FD_BAND_PCT_AGGREGATE
            and f["n_sign_flips"] == 0 and f["n_without_plateau"] == 0 and all(g["in_band"] for g in f["graded"])):
        return "PASS"
    return "GATE FAIL"


def planted_zero_control(fd_path, workdir, reader=read_json):
    before = md5_of(fd_path)
    baseg = g_fd(reader(fd_path, "G6-base"), "G6-base")
    if baseg["n_graded"] == 0:
        return {"pass": False, "reason": "NO_GRADED_ROW_TO_PLANT_INTO", "n_graded": 0}
    os.makedirs(workdir, exist_ok=True)
    planted_path = os.path.join(workdir, "d4s_f3s_fd_endpoint.PLANTED.json")
    doc = reader(fd_path, "G6-copy")
    moved = None
    for r in doc["rows"]:
        if r.get("status") == "PLANNED" and (r.get("fd") or {}).get("s_hi", {}).get("ok"):
            old = float(str(r["fd"]["s_hi"]["d"]).strip("'\""))
            r["fd"]["s_hi"]["d"] = repr(old * (1.0 + PLANT))
            moved = {"component": "%s[%d]" % (r["dv"], r["idx"]), "from": old, "to": old * (1.0 + PLANT)}
            break
    if moved is None:
        return {"pass": False, "reason": "NO_PLANTABLE_ROW"}
    with open(planted_path, "w") as fh:
        json.dump(doc, fh)
    plantedg = g_fd(reader(planted_path, "G6-planted"), "G6-planted")
    seen = {"rel_err_pct": abs(plantedg["graded"][0]["rel_err_pct"] - baseg["graded"][0]["rel_err_pct"]) > 1e-9,
            "plateau_pct": abs(plantedg["graded"][0]["plateau_pct"] - baseg["graded"][0]["plateau_pct"]) > 1e-9,
            "aggregate": abs((plantedg["aggregate_rel_err_pct"] or 0.0) - (baseg["aggregate_rel_err_pct"] or 0.0)) > 1e-12}
    after = md5_of(fd_path)
    out = {"plant": PLANT, "moved": moved, "channel_seen": seen, "src_md5_before": before,
           "src_md5_after": after, "src_unchanged": bool(before == after),
           "pass": bool(all(seen.values()) and before == after)}
    os.remove(planted_path)
    if not out["pass"]:
        refuse("G6", out)
    return out


def negative_control(fd_path, workdir):
    def blind(_p, where=None, _real=fd_path):
        return read_json(_real, where or "blind")
    try:
        planted_zero_control(fd_path, workdir, reader=blind)
    except Refuse as exc:
        return {"pass": True, "refused_with": str(exc)[:300]}
    return {"pass": False, "refused_with": None, "note": "the blind reader was ACCEPTED -- G6 is not a control"}


def count_controls(fd_path, workdir):
    os.makedirs(workdir, exist_ok=True)
    results = {}
    for label, mutate in (("empty", lambda d: d.update({"rows": []})),
                          ("short", lambda d: d.update({"rows": d["rows"][:2]})),
                          ("reordered", lambda d: d.update({"rows": list(reversed(d["rows"]))})),
                          ("key_absent", lambda d: d.pop("rows", None))):
        doc = read_json(fd_path, "G7-src")
        mutate(doc)
        p = os.path.join(workdir, "d4s_f3s_fd_endpoint.G7_%s.json" % label)
        with open(p, "w") as fh:
            json.dump(doc, fh)
        try:
            g_fd(read_json(p, "G7-%s" % label), "G7-%s" % label)
            results[label] = {"pass": False, "refused_with": None, "note": "mutation was ACCEPTED"}
        except Refuse as exc:
            results[label] = {"pass": True, "refused_with": str(exc)[:300]}
        os.remove(p)
    results["pass"] = all(v["pass"] for k, v in results.items() if k != "pass")
    return results


def g_toolchain_arm(base, row, arm):
    """G9 per row: the .so md5 the container printed and the digest the ledger
    carries must be the REGISTERED pair for this arm's row."""
    want_row = ROW_OF[arm]
    so = None
    for line in open(os.path.join(base, row["log"]), errors="replace"):
        if "D4S_IDWARP_SO_MD5:" in line:
            so = line.split("D4S_IDWARP_SO_MD5:")[1].strip()
            break
    out = {"arm": arm, "row_in_ledger": row["ROW"], "row_registered": want_row,
           "so_md5_in_log": so, "so_md5_registered": SO_MD5[want_row],
           "digest_in_ledger": row["DIGEST"], "digest_registered": DIGEST[want_row]}
    out["pass"] = bool(row["ROW"] == want_row and so == SO_MD5[want_row] and row["DIGEST"] == DIGEST[want_row])
    return out


def g_caps(rows_by_arm):
    """G10 with the CAP FRAME repair (D4S-F3S-CAP-DEF-1).

    `within_cap` is UNCHANGED and UNWIDENED: the HOST bracket must not exceed
    the registered cap.  What changed is upstream -- the launcher shortens the
    in-container deadline by the registered frame allowance so the host
    bracket is SATISFIABLE at the deadline.  Two new limbs BIND the
    container's own kernel clock so the two frames are separated on the record
    rather than conflated; a discrepancy nobody grades is worse than one never
    computed.  If the container clock is NOT_MEASURED the gate falls back to
    the host bracket alone -- the STRICTER reading -- so the fallback can never
    turn a failing cap into a passing one.
    """
    rows, total = [], 0.0
    for arm in ARMS:
        r = rows_by_arm[arm]
        reg = CAPS[arm]
        cw = r.get("container_wall_s")
        fa = r.get("frame_allowance_s")
        row = {"arm": arm, "registered": reg, "ledger_cap": r["cap_core_min"], "enforced": r["enforced_core_min"],
               "actual": r["core_min"], "host_wall_s": r["wall_s"],
               "container_wall_s": cw if cw is not None else "NOT_MEASURED",
               "frame_allowance_s_in_ledger": fa if fa is not None else "NOT_MEASURED",
               "deadline_registered_s": TMO_REGISTERED_S,
               "cap_equals_registered": bool(abs(r["cap_core_min"] - reg) < 1e-9 and abs(r["enforced_core_min"] - reg) <= 0.02),
               "within_cap": bool(r["core_min"] <= reg + 1e-9)}
        if cw is None:
            row["deadline_frame_pass"] = "NOT_MEASURED"
            row["frame_gap_within_allowance"] = "NOT_MEASURED"
            row["frame_gap_s"] = "NOT_MEASURED"
            row["frame_limbs_binding"] = False
        else:
            gap = r["wall_s"] - cw
            row["frame_gap_s"] = gap
            row["deadline_frame_pass"] = bool(cw <= TMO_REGISTERED_S + KILL_GRACE_S)
            row["frame_gap_within_allowance"] = bool(gap <= FRAME_ALLOWANCE_S - KILL_GRACE_S)
            row["frame_limbs_binding"] = True
            if fa is not None and abs(fa - FRAME_ALLOWANCE_S) > 1e-9:
                row["frame_allowance_matches_registered"] = False
            else:
                row["frame_allowance_matches_registered"] = True
        rows.append(row)
        total += r["core_min"]

    def limbs_ok(x):
        base_ok = x["cap_equals_registered"] and x["within_cap"]
        if not x["frame_limbs_binding"]:
            return bool(base_ok)
        return bool(base_ok and x["deadline_frame_pass"] and x["frame_gap_within_allowance"]
                    and x["frame_allowance_matches_registered"])

    return {"rows": rows, "total_core_min": total, "item_ceiling": ITEM_CEILING_CORE_MIN,
            "frame_note": ("cap ENFORCED in the container at %d s; GRADED on the host bracket; "
                           "(deadline + allowance) * ranks / 60 = %.3f core-min = the registered cap"
                           % (TMO_REGISTERED_S, (TMO_REGISTERED_S + FRAME_ALLOWANCE_S) * RANKS / 60.0)),
            "pass": bool(all(limbs_ok(x) for x in rows) and total <= ITEM_CEILING_CORE_MIN)}


def g_placement_arm(work, row, arm):
    files = sorted(f for f in os.listdir(work) if re.match(r"d4_placement_rank\d+\.json$", f))
    if len(files) != RANKS:
        refuse("G12", {"arm": arm, "COUNT_REFUSAL": "placement files", "n": len(files), "expected": RANKS})
    affs = [read_json(os.path.join(work, f), "G12").get("affinity", []) for f in files]
    union = sorted(set(c for a in affs for c in a))
    inside = all(set(a) <= set(CPUSET_REGISTERED) for a in affs)
    distinct = (all(len(a) == 1 for a in affs) and len(set(a[0] for a in affs)) == RANKS)
    cps = sorted(int(x) for x in row["cpuset"].split(","))
    deliv = row.get("delivered")
    return {"arm": arm, "affinity_union": union, "affinity_inside_cpuset": bool(inside),
            "all_ranks_on_distinct_single_cores": bool(distinct), "cpuset_ledger": cps,
            "cpuset_as_registered": bool(cps == CPUSET_REGISTERED), "delivered_cores_mean": deliv,
            "delivered_floor": DELIVERED_FLOOR,
            "delivered_ok_or_not_measured": bool(deliv is None or deliv >= DELIVERED_FLOOR),
            "pass": bool(inside and distinct and cps == CPUSET_REGISTERED and (deliv is None or deliv >= DELIVERED_FLOOR))}


def score_predictions(report, verdicts):
    p = {}
    acc = report["G_ACC"]
    p["P1_both_rows_every_primal_accepted"] = ("HIT" if all(acc[a]["pass"] for a in ARMS) else "MISS")
    fs = report["G5"].get("F-S")
    if fs is None or fs["n_graded"] == 0:
        p["P2_shipped_shape18_outside_bandD"] = "UNSCORED"
    else:
        g = [x for x in fs["graded"] if x["component"] == P2_COMPONENT]
        p["P2_shipped_shape18_outside_bandD"] = ("HIT" if (g and (not g[0]["in_band"] or g[0]["sign_flip"])) else "MISS")
        p["P2_detail"] = g[0] if g else {"component_not_graded": P2_COMPONENT}
    fp = report["G5"].get("F-P")
    if fp is None or fp["n_graded"] == 0 or not os.path.isfile(D4_PATCHED_F3_TABLE):
        p["P3_patched_reproduces_D4_F3_to_printed_digits"] = "UNSCORED"
        p["P3_detail"] = {"reference": D4_PATCHED_F3_TABLE, "present": os.path.isfile(D4_PATCHED_F3_TABLE)}
    else:
        ref = g_fd(read_json(D4_PATCHED_F3_TABLE, "P3"), "P3")
        refby = {g["component"]: g for g in ref["graded"]}
        worst, rows = 0.0, []
        for g in fp["graded"]:
            r = refby.get(g["component"])
            if r is None:
                rows.append({"component": g["component"], "reference": "absent"})
                worst = float("inf")
                continue
            dj = abs(g["J_adj"] - r["J_adj"]) / abs(r["J_adj"]) if r["J_adj"] else float("inf")
            dd = abs(g["d_hi"] - r["d_hi"]) / abs(r["d_hi"]) if r["d_hi"] else float("inf")
            rows.append({"component": g["component"], "rel_diff_J_adj": dj, "rel_diff_d_hi": dd})
            worst = max(worst, dj, dd)
        p["P3_patched_reproduces_D4_F3_to_printed_digits"] = ("HIT" if worst <= P3_REL_TOL else "MISS")
        p["P3_detail"] = {"worst_rel_diff": worst, "tol": P3_REL_TOL, "rows": rows,
                          "reference_aggregate_pct": ref["aggregate_rel_err_pct"]}
    ratios = {a: report["G10"]["rows"][k]["actual"] / PREDICTED[a] for k, a in enumerate(ARMS)}
    p["P4_cost_ratio_per_arm_in_band"] = ("HIT" if all(P4_BAND[0] <= v <= P4_BAND[1] for v in ratios.values()) else "MISS")
    p["P4_detail"] = {"ratios": ratios, "band": list(P4_BAND), "predicted": PREDICTED,
                      "band_provenance": "INHERITED BY CITATION from D4S-F3S section 6, UNCHANGED"}
    # ---- P5: the TIGHTER band on the REPAIRED two-term anchor.  Registered as
    # NEW and STRICTLY TIGHTER than P4, so it can only turn a HIT into a MISS.
    p["P5_cost_ratio_per_arm_in_tight_band"] = ("HIT" if all(P5_BAND[0] <= v <= P5_BAND[1] for v in ratios.values()) else "MISS")
    p["P5_detail"] = {"ratios": ratios, "band": list(P5_BAND), "predicted": PREDICTED,
                      "anchor": {"overhead_s": OVERHEAD_S_ANCHOR, "rate_s_per_primal": RATE_S_PER_PRIMAL_ANCHOR,
                                 "n_primals": N_PRIMALS_ANCHOR, "ranks": RANKS,
                                 "formula": "core_min = (OVERHEAD_S + N_PRIMALS * RATE_S_PER_PRIMAL) * ranks / 60"},
                      "band_provenance": ("NEW at this freeze, derived from the predecessor's MEASURED "
                                          "two-term decomposition which this lane has read; TIGHTER than "
                                          "P4 and therefore incapable of turning a MISS into a HIT")}
    # ---- P6: the two-row reproduction of the PREDECESSOR's own tables.
    p6, p6rows, worst6 = "UNSCORED", {}, 0.0
    have = all(os.path.isfile(D4S_F3S_REFERENCE_TABLE[a]) for a in ARMS)
    graded_ok = all(report["G5"].get(a) and report["G5"][a]["n_graded"] > 0 for a in ARMS)
    if have and graded_ok:
        for a in ARMS:
            ref = g_fd(read_json(D4S_F3S_REFERENCE_TABLE[a], "P6"), "P6")
            refby = {g["component"]: g for g in ref["graded"]}
            rows6 = []
            for g in report["G5"][a]["graded"]:
                r = refby.get(g["component"])
                if r is None:
                    rows6.append({"component": g["component"], "reference": "absent"})
                    worst6 = float("inf")
                    continue
                dj = abs(g["J_adj"] - r["J_adj"]) / abs(r["J_adj"]) if r["J_adj"] else float("inf")
                dd = abs(g["d_hi"] - r["d_hi"]) / abs(r["d_hi"]) if r["d_hi"] else float("inf")
                rows6.append({"component": g["component"], "rel_diff_J_adj": dj, "rel_diff_d_hi": dd})
                worst6 = max(worst6, dj, dd)
            p6rows[a] = rows6
        p6 = "HIT" if worst6 <= P6_REL_TOL else "MISS"
    p["P6_both_rows_reproduce_D4S_F3S_to_printed_digits"] = p6
    p["P6_detail"] = {"worst_rel_diff": worst6, "tol": P6_REL_TOL, "rows": p6rows,
                      "references": D4S_F3S_REFERENCE_TABLE, "references_present": have}
    # ---- P7: THE REPAIR'S OWN FALSIFIER.  This is the prediction the item
    # exists to test and it is scored from the age clause itself.
    g1 = report.get("G1", {})
    if not all(a in g1 for a in ARMS):
        p["P7_age_clause_satisfiable_on_both_arms"] = "UNSCORED"
    else:
        okp = all(g1[a].get("age_clause_pass") and g1[a].get("n_stale") == 0
                  and g1[a].get("inverse_clause_pass")
                  and g1[a].get("n_staged_inputs_excluded") == len(STAGED_INPUTS_EXCLUDED_FROM_AGE)
                  for a in ARMS)
        p["P7_age_clause_satisfiable_on_both_arms"] = "HIT" if okp else "MISS"
    p["P7_detail"] = {a: {"n_stale": g1[a].get("n_stale"),
                          "n_staged_inputs_excluded": g1[a].get("n_staged_inputs_excluded"),
                          "age_clause_pass": g1[a].get("age_clause_pass"),
                          "inverse_clause_pass": g1[a].get("inverse_clause_pass")}
                      for a in ARMS if a in g1}
    return p


def grade(base, launcher=None, accept_path=None):
    verdicts, report = {}, {}
    accept_path = accept_path or os.path.join(HERE, "d4s_f3s_accept.py")
    acc = load_accept_module(accept_path)
    report["accept_module_md5_grader"] = md5_of(accept_path)
    ledger = read_ledger(os.path.join(base, "ledger.txt"))
    rows_by_arm = {}
    for arm in ARMS:
        r = last_row(ledger, arm)
        if r is None:
            refuse("G1", {"arm_absent_from_ledger": arm})
        rows_by_arm[arm] = r
    report["NOT_MEASURED"] = {a: rows_by_arm[a]["infra_not_measured"] for a in ARMS if rows_by_arm[a]["infra_not_measured"]}
    report["field_classes"] = {"physics": FIELDS_PHYSICS, "infrastructure": FIELDS_INFRASTRUCTURE}
    report["G1"], report["G_ACC"], report["G9"], report["G12"], report["G5"] = {}, {}, {}, {}, {}
    report["G6"], report["G6b"], report["G7"] = {}, {}, {}
    for arm in ARMS:
        work = os.path.join(base, arm)
        row = rows_by_arm[arm]
        report["G1"][arm] = g_completion_arm(base, work, row, arm)
        report["G9"][arm] = g_toolchain_arm(base, row, arm)
        report["G12"][arm] = g_placement_arm(work, row, arm)
        report["G_ACC"][arm] = g_acceptance_arm(base, work, row, arm, acc)
        if report["G_ACC"][arm]["accept_module_md5_instrument"] != report["accept_module_md5_grader"]:
            refuse("G-ACC", {"arm": arm, "accept_module_md5_instrument_vs_grader":
                             [report["G_ACC"][arm]["accept_module_md5_instrument"], report["accept_module_md5_grader"]]})
        fd_path = os.path.join(work, "d4s_f3s_fd_endpoint.json")
        ctrl = os.path.join(base, "grader_controls", arm)
        report["G7"][arm] = count_controls(fd_path, ctrl)
        report["G6b"][arm] = negative_control(fd_path, ctrl)
        report["G6"][arm] = planted_zero_control(fd_path, ctrl)
        report["G5"][arm] = g_fd(read_json(fd_path, "G5"))
        verdicts["G1_completion_and_age_%s" % arm] = "PASS" if report["G1"][arm]["pass"] else "NOT A RESULT"
        verdicts["G_ACC_stationarity_%s" % arm] = "PASS" if report["G_ACC"][arm]["pass"] else "NOT A RESULT"
        verdicts["G9_toolchain_identity_%s" % arm] = "PASS" if report["G9"][arm]["pass"] else "GATE FAIL"
        verdicts["G12_cpu_placement_%s" % arm] = "PASS" if report["G12"][arm]["pass"] else "GATE FAIL"
        verdicts["G7_count_refusal_control_%s" % arm] = "PASS" if report["G7"][arm]["pass"] else "GATE FAIL"
        verdicts["G6b_negative_control_%s" % arm] = "PASS" if report["G6b"][arm]["pass"] else "GATE FAIL"
        verdicts["G6_planted_zero_%s" % arm] = "PASS" if report["G6"][arm]["pass"] else "GATE FAIL"
        verdicts["G5_endpoint_fd_%s" % arm] = fd_verdict(report["G5"][arm])
    so_s, so_p = report["G9"]["F-S"]["so_md5_in_log"], report["G9"]["F-P"]["so_md5_in_log"]
    report["G9"]["two_rows_distinct"] = bool(so_s and so_p and so_s != so_p)
    verdicts["G9_two_rows_distinct"] = "PASS" if report["G9"]["two_rows_distinct"] else "GATE FAIL"
    report["G10"] = g_caps(rows_by_arm)
    verdicts["G10_cap_discipline"] = "PASS" if report["G10"]["pass"] else "GATE FAIL"
    oom = [a for a in ARMS if str(rows_by_arm[a]["oomkilled"]).lower() == "true"]
    report["G11"] = {"arms_oomkilled": oom, "pass": bool(not oom)}
    verdicts["G11_memory_envelope"] = "PASS" if not oom else "NOT A RESULT"
    # ---- item composition (PREREGISTRATION.md section 5)
    rows_ok = all(report["G1"][a]["pass"] and report["G_ACC"][a]["pass"] and report["G6"][a]["pass"]
                  and report["G6b"][a]["pass"] and report["G7"][a]["pass"] for a in ARMS)
    g5 = [verdicts["G5_endpoint_fd_%s" % a] for a in ARMS]
    if not rows_ok or "NOT A RESULT" in g5 or oom:
        item = "NOT A RESULT"
    elif all(v == "PASS" for v in g5):
        item = "PASS"
    else:
        item = "GATE FAIL"
    verdicts["ITEM_two_row_endpoint_fd"] = item
    report["predictions"] = score_predictions(report, verdicts)
    return verdicts, report


# --------------------------------------------------------------- selftest
def _count_asserts(path):
    import ast
    return sum(1 for n in ast.walk(ast.parse(open(path).read())) if isinstance(n, ast.Assert))


def build_fixture(root, acc_path, stale_product=None, staged_input_newer=None,
                  drop_manifest=False, corrupt_staged_bytes=False, drop_age_ref=False):
    """A sacrificial root built from REAL artefacts: curriculum_D4's F3 table
    and its 22 real primal blocks stand in for both arms.

    D4S-F3S-AGE-DEF-1 REPAIR OF THE FIXTURE ITSELF.  The predecessor's fixture
    CREATED `OptView.hst` fresh (`d4s_f3s_grade.py:599-601`) against a datum
    pinned at epoch 1000000000, so REAL STAGING SEMANTICS WERE NEVER
    EXERCISED and a 26/26 selftest passed over an unsatisfiable clause.  Here:

      * a real SOURCE tree is built under `<root>/_src/<arm>/` and its staged
        inputs are given mtimes that PREDATE the datum, as the real sources do
        (the real OptView.hst predates its arm's datum by ~30 hours);
      * the arm directory is staged from it by a REAL `cp -a` subprocess --
        not shutil, not a fresh write -- so the mtime-preserve semantics under
        test are the ones the stager actually uses;
      * the copy is VERIFIED to have preserved the source mtime, and that
        mtime is VERIFIED to predate the datum, before anything is graded;
      * the age reference sentinel is created and touched AFTER the copy and
        the datum is read FROM IT, as `d4s_f3sr_stage_arm.sh` step (g) does;
      * only THEN are the products written, and they are stamped strictly
        newer than the datum.

    The knobs drive the clause BOTH WAYS: `stale_product` back-dates one real
    product (the clause must REFUSE), `staged_input_newer` forward-dates one
    excluded input (the exclusion must REFUSE).
    """
    import subprocess
    ref_fd = D4_PATCHED_F3_TABLE
    ref_log = "/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/F3_20260825T220706Z_2733788.log"
    if not (os.path.isfile(ref_fd) and os.path.isfile(ref_log)):
        raise Refuse("selftest needs the real D4 F3 table and log: %s %s" % (ref_fd, ref_log))
    spec = importlib.util.spec_from_file_location("acc_fx", acc_path)
    acc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(acc)
    blocks = [b for b in acc.split_primal_blocks(open(ref_log, errors="replace").read())
              if acc.parse_primal_text(b)["n_samples"] > 0]
    os.makedirs(root, exist_ok=True)
    ledger = ["ITEM=%s" % ITEM]
    fixture_evidence = []
    for arm in ARMS:
        row = ROW_OF[arm]
        work = os.path.join(root, arm)
        # ---- (1) A REAL SOURCE TREE whose staged inputs PREDATE the datum ----
        srcdir = os.path.join(root, "_src", arm)
        os.makedirs(srcdir, exist_ok=True)
        old = int(__import__("time").time()) - 100000        # ~28 h old, as the real source is
        src_md5 = {}
        for si in sorted(STAGED_INPUTS_EXCLUDED_FROM_AGE):
            sp = os.path.join(srcdir, si)
            with open(sp, "w") as fh:
                fh.write("STAGED INPUT %s for %s -- never written by this item\n" % (si, arm))
            os.utime(sp, (old, old))
            src_md5[si] = md5_of(sp)
        # ---- (2) STAGE BY A REAL `cp -a`, exactly as the stager does --------
        shutil.rmtree(work, ignore_errors=True)
        subprocess.check_call(["cp", "-a", srcdir, work])
        # ---- (3) PROVE the staging semantics are real BEFORE grading -------
        for si in sorted(STAGED_INPUTS_EXCLUDED_FROM_AGE):
            sm = int(os.path.getmtime(os.path.join(srcdir, si)))
            dm = int(os.path.getmtime(os.path.join(work, si)))
            if sm != dm:
                raise Refuse("fixture: `cp -a` did not preserve the mtime of %s (%d -> %d)" % (si, sm, dm))
            fixture_evidence.append({"arm": arm, "staged_input": si, "src_mtime": sm, "dst_mtime": dm,
                                     "cp_a_preserved": True})
        # ---- (4) THE AGE REFERENCE, TOUCHED LAST (stager step (g)) ---------
        ref = os.path.join(work, ".d4s_f3sr_age_ref")
        open(ref, "w").close()
        os.utime(ref, None)
        datum = int(os.path.getmtime(ref))
        with open(os.path.join(work, ".d4s_f3sr_stage_%s_copy_epoch" % arm), "w") as fh:
            fh.write("%d\n" % datum)
        with open(os.path.join(work, ".d4s_f3sr_stage_%s_age_ref" % arm), "w") as fh:
            fh.write(".d4s_f3sr_age_ref\n")
        for si in sorted(STAGED_INPUTS_EXCLUDED_FROM_AGE):
            if int(os.path.getmtime(os.path.join(work, si))) > datum:
                raise Refuse("fixture: a staged input is newer than the datum before any mutation")
        if staged_input_newer:
            t = datum + 7
            os.utime(os.path.join(work, staged_input_newer), (t, t))
        if corrupt_staged_bytes:
            nm = sorted(STAGED_INPUTS_EXCLUDED_FROM_AGE)[0]
            p = os.path.join(work, nm)
            m = int(os.path.getmtime(p))
            open(p, "a").write("TAMPERED\n")
            os.utime(p, (m, m))
        if not drop_manifest:
            man = {"arm": arm, "src": srcdir, "age_datum": datum, "age_ref": ".d4s_f3sr_age_ref",
                   "staged_inputs": [{"name": si, "src_md5": src_md5[si], "dst_md5": src_md5[si],
                                      "src_mtime": old, "dst_mtime": old,
                                      "produced_by_this_item": False}
                                     for si in sorted(STAGED_INPUTS_EXCLUDED_FROM_AGE)]}
            with open(os.path.join(work, STAGED_INPUT_MANIFEST), "w") as fh:
                json.dump(man, fh)
        if drop_age_ref:
            os.remove(ref)
        fd = read_json(ref_fd, "fixture")
        fd["n_primals"] = len(blocks)
        fd["accept_module_md5"] = md5_of(acc_path)
        with open(os.path.join(work, "d4s_f3s_fd_endpoint.json"), "w") as fh:
            json.dump(fd, fh)
        with open(os.path.join(work, "d4s_f3s_fd_endpoint.jsonl"), "w") as fh:
            fh.write(json.dumps({"kind": "disarm", "key": "primalMinResTolDiff", "effective": DISARM_TOL_DIFF}) + "\n")
        with open(os.path.join(work, "d4s_f3s_accept.jsonl"), "w") as fh:
            for k, b in enumerate(blocks):
                cap = "d4s_f3s_primal_%03d_p%d.log" % (k + 1, k + 1)
                with open(os.path.join(work, cap), "w") as ch:
                    ch.write(b + "\n")
                fh.write(json.dumps({"kind": "accept", "n": k + 1, "tag": "p%d" % (k + 1), "capture": cap, "accepted": True}) + "\n")
        # ---- (5) THE PRODUCTS, written LAST and stamped STRICTLY NEWER -----
        for a in ARTEFACTS:
            p = os.path.join(work, a)
            if not os.path.exists(p):
                with open(p, "w") as fh:
                    fh.write("{}\n")
        for a in ARTEFACTS:
            p = os.path.join(work, a)
            t = datum + 5
            os.utime(p, (t, t))
        if stale_product:
            t = datum - 5
            os.utime(os.path.join(work, stale_product), (t, t))
        for r in range(RANKS):
            with open(os.path.join(work, "d4_placement_rank%d.json" % r), "w") as fh:
                json.dump({"rank": r, "affinity": [CPUSET_REGISTERED[r]], "n_cores": 1}, fh)
        log = "%s_20260826T000000Z_1.log" % arm
        with open(os.path.join(root, log), "w") as fh:
            fh.write("D4S_CONTAINER_UID: 0\nD4S_IDWARP_SO_MD5: %s\n" % SO_MD5[row])
            for b in blocks:
                fh.write("Running Primal Solver 001\n" + b + "\n")
            fh.write("D4S_F3S_FD_ENDPOINT_WRITTEN d4s_f3s_fd_endpoint.json n_rows=5 n_primals=%d\nFinalising parallel run\n" % len(blocks))
        ledger.append("ARM=%s ROW=%s IMG=x DIGEST=%s rc=0 wall_s=569 ranks=4 core_min=37.933 cap_core_min=120.0 enforced_wall_s=1710 enforced_core_min=120.000000 memory=12g inspect(exit,oomkilled)=[0 false] container_wall_s=560 frame_allowance_s=90 memavail_pre_GiB=26.39 memavail_post_GiB=26.42 cpuset=5,6,7,9 delivered_cores_mean=[3.9752 n=69 max_nr_throttled=2070] siblings_pre=[] siblings_post=[] log=%s stamp=1" % (arm, row, DIGEST[row], log))
    with open(os.path.join(root, "ledger.txt"), "w") as fh:
        fh.write("\n".join(ledger) + "\n")
    with open(os.path.join(root, "FIXTURE_STAGING_EVIDENCE.json"), "w") as fh:
        json.dump(fixture_evidence, fh, indent=1)
    return len(blocks)


def selftest(tmpdir):
    acc_path = os.path.join(HERE, "d4s_f3s_accept.py")
    res, fails = [], 0

    def check(name, cond, detail=""):
        nonlocal fails
        res.append("  [%s] %s %s" % ("OK " if cond else "BAD", name, str(detail)[:200]))
        if not cond:
            fails += 1

    def fresh(tag, **kw):
        root = os.path.join(tmpdir, "d4sf3sr_selftest_" + tag)
        shutil.rmtree(root, ignore_errors=True)
        n = build_fixture(root, acc_path, **kw)
        return root, n

    def run(root):
        try:
            v, r = grade(root, accept_path=acc_path)
            return {"verdicts": v, "report": r}
        except Refuse as exc:
            return {"REFUSED": str(exc)}

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
        fh.write("def f(x):\n    assert x\n")
        pp = fh.name
    check("0_ast_counter_sees_planted_assert", _count_asserts(pp) == 1)
    os.remove(pp)
    check("0_ast_Assert_zero_in_grader_and_accept", _count_asserts(os.path.abspath(__file__)) == 0 and _count_asserts(acc_path) == 0)
    root, n = fresh("clean")
    o = run(root)
    ok = "verdicts" in o and o["verdicts"]["ITEM_two_row_endpoint_fd"] == "PASS"
    check("1_clean_fixture_ITEM_PASS", ok, o.get("REFUSED") or {k: v for k, v in o["verdicts"].items() if k.startswith(("ITEM", "G5", "G_ACC", "G9_two"))})
    if ok:
        check("1_G_ACC_n_primals_%d_all_accepted" % n, o["report"]["G_ACC"]["F-S"]["n_accepted_regraded"] == n)
        check("1_G5_both_rows_PASS_aggregate_0.1634", abs(o["report"]["G5"]["F-P"]["aggregate_rel_err_pct"] - 0.1634451673004621) < 1e-9,
              o["report"]["G5"]["F-P"]["aggregate_rel_err_pct"])
        check("1_NOT_MEASURED_empty_on_full_rows", o["report"]["NOT_MEASURED"] == {})
        check("1_P3_HIT_on_the_reference_itself", o["report"]["predictions"]["P3_patched_reproduces_D4_F3_to_printed_digits"] == "HIT")
        check("1_P2_MISS_on_a_passing_fixture", o["report"]["predictions"]["P2_shipped_shape18_outside_bandD"] == "MISS")
        check("1_P4_HIT_at_ratio_1.0", o["report"]["predictions"]["P4_cost_ratio_per_arm_in_band"] == "HIT")
        check("1_P5_HIT_on_the_repaired_two_term_anchor", o["report"]["predictions"]["P5_cost_ratio_per_arm_in_tight_band"] == "HIT",
              o["report"]["predictions"]["P5_detail"]["ratios"])
        check("1_P7_HIT_age_clause_satisfiable_on_both_arms", o["report"]["predictions"]["P7_age_clause_satisfiable_on_both_arms"] == "HIT",
              o["report"]["predictions"]["P7_detail"])
        # ---- THE PREDECESSOR'S DEFECT, REPLAYED WITH REAL STAGING SEMANTICS.
        # The fixture staged OptView.hst by a real `cp -a` from a source whose
        # mtime PREDATES the datum -- the exact condition that made D4S-F3S
        # NOT A RESULT.  Under the repaired list it must now PASS, with the
        # exclusion REGISTERED and CHECKED rather than silent.
        ev = json.load(open(os.path.join(root, "FIXTURE_STAGING_EVIDENCE.json")))
        check("1b_fixture_staged_by_real_cp_a_mtime_PRESERVED",
              len(ev) == len(ARMS) * len(STAGED_INPUTS_EXCLUDED_FROM_AGE) and all(e["cp_a_preserved"] for e in ev), len(ev))
        datum_fs = o["report"]["G1"]["F-S"]["age_datum_epoch"]
        opt_mtime = int(os.path.getmtime(os.path.join(root, "F-S", "OptView.hst")))
        check("1b_staged_OptView_hst_PREDATES_the_datum_by_construction", opt_mtime < datum_fs,
              {"OptView.hst": opt_mtime, "datum": datum_fs, "delta_s": datum_fs - opt_mtime})
        check("1c_PREDECESSOR_DEFECT_REPLAYED_now_PASSES",
              all(o["report"]["G1"][a]["n_stale"] == 0 and o["report"]["G1"][a]["pass"] for a in ARMS),
              {a: o["report"]["G1"][a]["n_stale"] for a in ARMS})
        check("1c_exclusions_REGISTERED_and_CHECKED_not_silent",
              all(o["report"]["G1"][a]["n_staged_inputs_excluded"] == 2
                  and sorted(x["staged_input"] for x in o["report"]["G1"][a]["staged_inputs_excluded"]) == ["OptView.hst", "opt_IPOPT.txt"]
                  and all(x["not_newer_than_datum"] and x["reason"] for x in o["report"]["G1"][a]["staged_inputs_excluded"])
                  for a in ARMS))
        check("1d_G10_frame_limbs_BINDING_not_diagnostic",
              all(r["frame_limbs_binding"] and r["deadline_frame_pass"] and r["frame_gap_within_allowance"]
                  for r in o["report"]["G10"]["rows"]),
              [{k: r[k] for k in ("arm", "container_wall_s", "host_wall_s", "frame_gap_s")} for r in o["report"]["G10"]["rows"]])
    # 2 rc=1 -> G1 fails -> NOT A RESULT
    root, n = fresh("rc1")
    L = open(os.path.join(root, "ledger.txt")).read().replace("ARM=F-S ROW=SHIPPED IMG=x DIGEST=%s rc=0" % DIGEST["SHIPPED"], "ARM=F-S ROW=SHIPPED IMG=x DIGEST=%s rc=1" % DIGEST["SHIPPED"]).replace("inspect(exit,oomkilled)=[0 false] container_wall_s=560 frame_allowance_s=90 memavail_pre_GiB=26.39 memavail_post_GiB=26.42 cpuset=5,6,7,9 delivered_cores_mean=[3.9752 n=69 max_nr_throttled=2070] siblings_pre=[] siblings_post=[] log=F-S", "inspect(exit,oomkilled)=[1 false] container_wall_s=560 frame_allowance_s=90 memavail_pre_GiB=26.39 memavail_post_GiB=26.42 cpuset=5,6,7,9 delivered_cores_mean=[3.9752 n=69 max_nr_throttled=2070] siblings_pre=[] siblings_post=[] log=F-S")
    open(os.path.join(root, "ledger.txt"), "w").write(L)
    o = run(root)
    check("2_rc1_G1_NOT_A_RESULT_item_NOT_A_RESULT", "verdicts" in o and o["verdicts"]["G1_completion_and_age_F-S"] == "NOT A RESULT" and o["verdicts"]["ITEM_two_row_endpoint_fd"] == "NOT A RESULT", o.get("REFUSED"))
    # 2b harness/kernel disagreement -> REFUSE
    root, n = fresh("disagree")
    L = open(os.path.join(root, "ledger.txt")).read().replace("inspect(exit,oomkilled)=[0 false] container_wall_s=560 frame_allowance_s=90 memavail_pre_GiB=26.39 memavail_post_GiB=26.42 cpuset=5,6,7,9 delivered_cores_mean=[3.9752 n=69 max_nr_throttled=2070] siblings_pre=[] siblings_post=[] log=F-P", "inspect(exit,oomkilled)=[1 false] container_wall_s=560 frame_allowance_s=90 memavail_pre_GiB=26.39 memavail_post_GiB=26.42 cpuset=5,6,7,9 delivered_cores_mean=[3.9752 n=69 max_nr_throttled=2070] siblings_pre=[] siblings_post=[] log=F-P")
    open(os.path.join(root, "ledger.txt"), "w").write(L)
    o = run(root)
    check("2b_harness_vs_kernel_rc_disagree_REFUSES", "REFUSED" in o and "disagree" in o["REFUSED"], o.get("REFUSED", "")[:120])
    # 3 terminal statement not last -> G1 fails
    root, n = fresh("terminal")
    lg = [f for f in os.listdir(root) if f.startswith("F-P_") and f.endswith(".log")][0]
    with open(os.path.join(root, lg), "a") as fh:
        fh.write("mpirun detected that one or more processes exited with non-zero status\n")
    o = run(root)
    check("3_terminal_not_last_G1_NOT_A_RESULT", "verdicts" in o and o["verdicts"]["G1_completion_and_age_F-P"] == "NOT A RESULT" and o["report"]["G1"]["F-P"]["terminal_detail"]["substring_anywhere_NOT_THE_TEST"] is True, o.get("REFUSED"))
    # ---- 4 THE AGE CLAUSE DRIVEN THE OTHER WAY: a GENUINELY STALE PRODUCT.
    # Same fixture, same real `cp -a` staging; one real product back-dated
    # behind the datum.  The clause must REFUSE the arm -- and must name
    # exactly that one file, not the whole list.
    root, n = fresh("stale", stale_product="d4s_f3s_fd_endpoint.json")
    o = run(root)
    check("4_STALE_PRODUCT_age_clause_REFUSES_the_arm",
          "verdicts" in o and o["verdicts"]["G1_completion_and_age_F-S"] == "NOT A RESULT"
          and o["verdicts"]["ITEM_two_row_endpoint_fd"] == "NOT A RESULT"
          and o["report"]["G1"]["F-S"]["n_stale"] == 1, o.get("REFUSED"))
    if "report" in o:
        stale_named = [r["artifact"] for r in o["report"]["G1"]["F-S"]["age_rows"] if not r["newer_than_datum"]]
        check("4_the_stale_file_is_NAMED_and_it_is_the_planted_one", stale_named == ["d4s_f3s_fd_endpoint.json"], stale_named)
        check("4_the_STAGED_INPUTS_are_NOT_counted_stale",
              o["report"]["G1"]["F-S"]["n_staged_inputs_excluded"] == 2, o["report"]["G1"]["F-S"].get("n_staged_inputs_excluded"))
    # 4b artefact absent -> REFUSE at G1-age
    root, n = fresh("absent")
    os.remove(os.path.join(root, "F-S", "d4s_f3s_fd_endpoint.json"))
    o = run(root)
    check("4b_absent_graded_artefact_REFUSES", "REFUSED" in o and "graded_artifact_absent" in o["REFUSED"], o.get("REFUSED", "")[:100])
    # ---- 4c THE INVERSE CLAUSE: an excluded file that is NEWER than the datum
    # is NOT a staged input, and the exclusion must be REFUSED, never honoured.
    root, n = fresh("inverse", staged_input_newer="OptView.hst")
    o = run(root)
    check("4c_staged_input_NEWER_than_datum_EXCLUSION_REFUSED",
          "REFUSED" in o and "EXCLUSION_REFUSED" in o["REFUSED"] and "OptView.hst" in o["REFUSED"], o.get("REFUSED", "")[:160])
    # ---- 4d the manifest is the registration; without it there is no exclusion
    root, n = fresh("nomanifest", drop_manifest=True)
    o = run(root)
    check("4d_absent_staged_input_manifest_REFUSES",
          "REFUSED" in o and "staged_input_manifest_absent" in o["REFUSED"], o.get("REFUSED", "")[:120])
    # ---- 4e the staged bytes must be the bytes the stager copied
    root, n = fresh("tamper", corrupt_staged_bytes=True)
    o = run(root)
    check("4e_tampered_staged_input_bytes_REFUSE",
          "REFUSED" in o and "EXCLUSION_REFUSED" in o["REFUSED"] and "md5_on_disk" in o["REFUSED"], o.get("REFUSED", "")[:160])
    # ---- 4f the datum must come from a sentinel touched last
    root, n = fresh("noref", drop_age_ref=True)
    o = run(root)
    check("4f_absent_age_reference_sentinel_REFUSES",
          "REFUSED" in o and "age_reference_sentinel_absent" in o["REFUSED"], o.get("REFUSED", "")[:120])
    # ---- 4g A REGISTERED STAGED INPUT THAT IS ABSENT is a refusal, not an
    # excuse: excluding a name may never excuse its absence.
    root, n = fresh("siabsent")
    os.remove(os.path.join(root, "F-S", "opt_IPOPT.txt"))
    o = run(root)
    check("4g_absent_registered_staged_input_REFUSES",
          "REFUSED" in o and "registered_staged_input_absent" in o["REFUSED"], o.get("REFUSED", "")[:120])
    # ---- 4h THE MUTATION CONTROL, IN TWO PARTS.  A repair that cannot be
    # shown to be load-bearing proves nothing, and an INERT mutation is
    # reported as proving nothing rather than quietly counted as a pass.
    root, n = fresh("mutation")
    # (i) THE ARITHMETIC PROOF, computed from the fixture's own disk state:
    # under the PREDECESSOR's list this real-`cp -a`-staged OptView.hst IS
    # stale.  This is the defect reproduced, not asserted.
    work_fs = os.path.join(root, "F-S")
    datum_m = int(open(os.path.join(work_fs, ".d4s_f3sr_stage_F-S_copy_epoch")).read().strip())
    opt_m = int(os.path.getmtime(os.path.join(work_fs, "OptView.hst")))
    predecessor_list = ["OptView.hst", "d4_endpoint_dvs_PHYSICAL.json", "d4_major_history.json",
                        "d4s_f3s_fd_endpoint.json", "d4s_f3s_fd_endpoint.jsonl", "d4s_f3s_accept.jsonl"]
    pred_stale = [a for a in predecessor_list
                  if int(os.path.getmtime(os.path.join(work_fs, a))) <= datum_m]
    check("4h_i_PREDECESSOR_LIST_REPRODUCES_THE_DEFECT_n_stale_1_on_OptView_hst",
          pred_stale == ["OptView.hst"],
          {"predecessor_n_stale": len(pred_stale), "named": pred_stale, "datum": datum_m, "OptView.hst": opt_m})
    repaired_stale = [a for a in ARTEFACTS
                      if int(os.path.getmtime(os.path.join(work_fs, a))) <= datum_m]
    check("4h_i_REPAIRED_LIST_ON_THE_SAME_DISK_STATE_n_stale_0", repaired_stale == [], repaired_stale)
    # (ii) THE GUARD-FIRES PROOF: putting the name back into ARTEFACTS makes
    # the grader REFUSE BY NAME on the same fixture that otherwise PASSES.
    saved = list(ARTEFACTS)
    try:
        ARTEFACTS.insert(0, "OptView.hst")
        o_mut = run(root)
    finally:
        ARTEFACTS[:] = saved
    mut_fires = ("REFUSED" in o_mut and "PRODUCT_AND_STAGED_INPUT_OVERLAP" in o_mut["REFUSED"]
                 and "OptView.hst" in o_mut["REFUSED"])
    check("4h_ii_MUTATION_CONTROL_FIRES_predecessor_classification_REFUSED_by_name",
          mut_fires, "MUTATION INERT -- PROVES NOTHING" if not mut_fires else str(o_mut["REFUSED"])[:140])
    o = run(root)
    check("4h_ii_control_restored_the_SAME_fixture_PASSES_with_the_repaired_list",
          "verdicts" in o and o["verdicts"]["G1_completion_and_age_F-S"] == "PASS", o.get("REFUSED"))
    # ---- 4i THE DISJOINTNESS of the two registered sets, checked not assumed
    check("4i_products_and_staged_inputs_are_DISJOINT_and_OptView_is_not_a_product",
          not (set(ARTEFACTS) & set(STAGED_INPUTS_EXCLUDED_FROM_AGE)) and "OptView.hst" not in ARTEFACTS
          and "OptView.hst" in STAGED_INPUTS_EXCLUDED_FROM_AGE)
    # 5 a drifting capture -> G-ACC fails (instrument said accepted -> disagreement recorded)
    root, n = fresh("drift")
    cap = os.path.join(root, "F-P", "d4s_f3s_primal_003_p3.log")
    t = open(cap).read().splitlines()
    out_l, cur = [], 0
    for l in t:
        m = re.match(r"^Time = (\d+)", l)
        if m:
            cur = int(m.group(1))
        mm = re.match(r"^nuTilda initRes: (\S+) finalRes: (\S+) nIters: (\d+)", l)
        if mm and cur == 800:
            l = "nuTilda initRes: %r finalRes: %s nIters: %s" % (float(mm.group(1)) * 1.05, mm.group(2), mm.group(3))
        out_l.append(l)
    open(cap, "w").write("\n".join(out_l) + "\n")
    o = run(root)
    check("5_planted_5pct_drift_G_ACC_NOT_A_RESULT_item_NOT_A_RESULT", "verdicts" in o and o["verdicts"]["G_ACC_stationarity_F-P"] == "NOT A RESULT" and o["verdicts"]["ITEM_two_row_endpoint_fd"] == "NOT A RESULT" and o["report"]["G_ACC"]["F-P"]["per_primal"][2]["agree"] is False, o.get("REFUSED"))
    # 5b capture count mismatch -> REFUSE
    root, n = fresh("count")
    os.remove(os.path.join(root, "F-S", "d4s_f3s_primal_002_p2.log"))
    o = run(root)
    check("5b_capture_count_mismatch_REFUSES", "REFUSED" in o and "COUNT_REFUSAL" in o["REFUSED"], o.get("REFUSED", "")[:100])
    # 5c disarm not effective -> G-ACC fails
    root, n = fresh("disarm")
    open(os.path.join(root, "F-S", "d4s_f3s_fd_endpoint.jsonl"), "w").write(json.dumps({"kind": "disarm", "effective": 1000.0}) + "\n")
    o = run(root)
    check("5c_disarm_readback_1e3_G_ACC_NOT_A_RESULT", "verdicts" in o and o["verdicts"]["G_ACC_stationarity_F-S"] == "NOT A RESULT", o.get("REFUSED"))
    # 6 wrong .so md5 on F-S -> G9 fail
    root, n = fresh("so")
    lg = [f for f in os.listdir(root) if f.startswith("F-S_") and f.endswith(".log")][0]
    p = os.path.join(root, lg)
    txt = open(p).read().replace(SO_MD5["SHIPPED"], SO_MD5["PATCHED"])
    with open(p, "w") as fh:
        fh.write(txt)
    o = run(root)
    check("6_shipped_arm_with_patched_so_G9_GATE_FAIL_and_rows_not_distinct", "verdicts" in o and o["verdicts"]["G9_toolchain_identity_F-S"] == "GATE FAIL" and o["verdicts"]["G9_two_rows_distinct"] == "GATE FAIL", o.get("REFUSED"))
    # 7 planted FD perturbation -> G5 GATE FAIL on F-S; P2 HIT
    root, n = fresh("fd")
    p = os.path.join(root, "F-S", "d4s_f3s_fd_endpoint.json")
    d = read_json(p, "st")
    for r in d["rows"]:
        if r["dv"] == "shape" and r["idx"] == 18:
            r["J_adj"] = repr(-float(str(r["J_adj"]).strip("'\"")) * 3.6)
    json.dump(d, open(p, "w"))
    # the rewrite gives the file a fresh mtime; re-stamp it strictly newer than
    # the datum so THIS case tests G5 and not the age clause (a same-second
    # rewrite would otherwise read as stale and mask the gate under test)
    _dm = int(open(os.path.join(root, "F-S", ".d4s_f3sr_stage_F-S_copy_epoch")).read().strip()) + 5
    os.utime(p, (_dm, _dm))
    o = run(root)
    check("7_shape18_sign_flip_G5_GATE_FAIL_item_GATE_FAIL_P2_HIT", "verdicts" in o and o["verdicts"]["G5_endpoint_fd_F-S"] == "GATE FAIL" and o["verdicts"]["ITEM_two_row_endpoint_fd"] == "GATE FAIL" and o["report"]["predictions"]["P2_shipped_shape18_outside_bandD"] == "HIT", o.get("REFUSED"))
    # 8 infra absent -> NOT_MEASURED, grade proceeds; garbage -> REFUSE
    root, n = fresh("infra")
    L = open(os.path.join(root, "ledger.txt")).read().replace("memavail_post_GiB=26.42 cpuset=5,6,7,9 delivered_cores_mean=[3.9752 n=69 max_nr_throttled=2070] siblings_pre=[] siblings_post=[] log=F-S", "memavail_post_GiB=NOT_MEASURED cpuset=5,6,7,9 delivered_cores_mean=[NOT_MEASURED] siblings_pre=[] siblings_post=[] log=F-S")
    open(os.path.join(root, "ledger.txt"), "w").write(L)
    o = run(root)
    check("8_infra_absent_NOT_MEASURED_disclosed_grade_proceeds", "verdicts" in o and o["verdicts"]["ITEM_two_row_endpoint_fd"] == "PASS" and o["report"]["NOT_MEASURED"].get("F-S") == ["memavail_post_GiB", "delivered"], o.get("REFUSED") or o["report"]["NOT_MEASURED"])
    root, n = fresh("garbage")
    L = open(os.path.join(root, "ledger.txt")).read().replace("memavail_post_GiB=26.42 cpuset=5,6,7,9 delivered_cores_mean=[3.9752 n=69 max_nr_throttled=2070] siblings_pre=[] siblings_post=[] log=F-S", "memavail_post_GiB=abc cpuset=5,6,7,9 delivered_cores_mean=[3.9752 n=69 max_nr_throttled=2070] siblings_pre=[] siblings_post=[] log=F-S")
    open(os.path.join(root, "ledger.txt"), "w").write(L)
    o = run(root)
    check("8b_infra_garbage_REFUSES", "REFUSED" in o and "present_but_unparseable" in o["REFUSED"], o.get("REFUSED", "")[:100])
    # 9 physics field absent -> REFUSE
    root, n = fresh("phys")
    L = open(os.path.join(root, "ledger.txt")).read().replace(" cpuset=5,6,7,9 delivered_cores_mean=[3.9752 n=69 max_nr_throttled=2070] siblings_pre=[] siblings_post=[] log=F-P", " delivered_cores_mean=[3.9752 n=69 max_nr_throttled=2070] siblings_pre=[] siblings_post=[] log=F-P")
    open(os.path.join(root, "ledger.txt"), "w").write(L)
    o = run(root)
    check("9_physics_field_absent_REFUSES", "REFUSED" in o and "physics_field_absent" in o["REFUSED"], o.get("REFUSED", "")[:100])
    # 10 OOM row -> G11 NOT A RESULT
    root, n = fresh("oom")
    L = open(os.path.join(root, "ledger.txt")).read().replace("inspect(exit,oomkilled)=[0 false] container_wall_s=560 frame_allowance_s=90 memavail_pre_GiB=26.39 memavail_post_GiB=26.42 cpuset=5,6,7,9 delivered_cores_mean=[3.9752 n=69 max_nr_throttled=2070] siblings_pre=[] siblings_post=[] log=F-P", "inspect(exit,oomkilled)=[0 true] container_wall_s=560 frame_allowance_s=90 memavail_pre_GiB=26.39 memavail_post_GiB=26.42 cpuset=5,6,7,9 delivered_cores_mean=[3.9752 n=69 max_nr_throttled=2070] siblings_pre=[] siblings_post=[] log=F-P")
    open(os.path.join(root, "ledger.txt"), "w").write(L)
    o = run(root)
    check("10_oom_row_G11_NOT_A_RESULT", "verdicts" in o and o["verdicts"]["G11_memory_envelope"] == "NOT A RESULT" and o["verdicts"]["ITEM_two_row_endpoint_fd"] == "NOT A RESULT", o.get("REFUSED"))
    # 11 cap crossing -> G10 GATE FAIL, P4 MISS
    root, n = fresh("cap")
    L = open(os.path.join(root, "ledger.txt")).read().replace("core_min=37.933 cap_core_min=120.0 enforced_wall_s=1710 enforced_core_min=120.000000 memory=12g inspect(exit,oomkilled)=[0 false] container_wall_s=560 frame_allowance_s=90 memavail_pre_GiB=26.39 memavail_post_GiB=26.42 cpuset=5,6,7,9 delivered_cores_mean=[3.9752 n=69 max_nr_throttled=2070] siblings_pre=[] siblings_post=[] log=F-S", "core_min=130.0 cap_core_min=120.0 enforced_wall_s=1710 enforced_core_min=120.000000 memory=12g inspect(exit,oomkilled)=[0 false] container_wall_s=560 frame_allowance_s=90 memavail_pre_GiB=26.39 memavail_post_GiB=26.42 cpuset=5,6,7,9 delivered_cores_mean=[3.9752 n=69 max_nr_throttled=2070] siblings_pre=[] siblings_post=[] log=F-S")
    open(os.path.join(root, "ledger.txt"), "w").write(L)
    o = run(root)
    check("11_cap_crossing_G10_GATE_FAIL_P4_MISS_P5_MISS", "verdicts" in o and o["verdicts"]["G10_cap_discipline"] == "GATE FAIL" and o["report"]["predictions"]["P4_cost_ratio_per_arm_in_band"] == "MISS" and o["report"]["predictions"]["P5_cost_ratio_per_arm_in_tight_band"] == "MISS", o.get("REFUSED"))
    # 12 placement collision -> G12 GATE FAIL
    root, n = fresh("place")
    json.dump({"rank": 1, "affinity": [5], "n_cores": 1}, open(os.path.join(root, "F-P", "d4_placement_rank1.json"), "w"))
    o = run(root)
    check("12_two_ranks_on_one_core_G12_GATE_FAIL", "verdicts" in o and o["verdicts"]["G12_cpu_placement_F-P"] == "GATE FAIL", o.get("REFUSED"))
    # ---- 12b THE CAP FRAME (D4S-F3S-CAP-DEF-1).  Container clock absent ->
    # NOT_MEASURED, disclosed, and the gate falls back to the HOST bracket,
    # which is the STRICTER reading.
    root, n = fresh("noclock")
    L = open(os.path.join(root, "ledger.txt")).read().replace(" container_wall_s=560 frame_allowance_s=90", "")
    open(os.path.join(root, "ledger.txt"), "w").write(L)
    o = run(root)
    check("12b_container_clock_absent_NOT_MEASURED_and_G10_still_PASS",
          "verdicts" in o and o["verdicts"]["G10_cap_discipline"] == "PASS"
          and all(r["container_wall_s"] == "NOT_MEASURED" and r["frame_limbs_binding"] is False for r in o["report"]["G10"]["rows"])
          and all("container_wall_s" in v for v in o["report"]["NOT_MEASURED"].values()), o.get("REFUSED"))
    # ---- 12c the in-container deadline was NOT honoured -> G10 GATE FAIL
    root, n = fresh("overdeadline")
    L = open(os.path.join(root, "ledger.txt")).read().replace("container_wall_s=560", "container_wall_s=%d" % (TMO_REGISTERED_S + KILL_GRACE_S + 1))
    open(os.path.join(root, "ledger.txt"), "w").write(L)
    o = run(root)
    check("12c_container_wall_over_deadline_plus_grace_G10_GATE_FAIL",
          "verdicts" in o and o["verdicts"]["G10_cap_discipline"] == "GATE FAIL"
          and all(r["deadline_frame_pass"] is False for r in o["report"]["G10"]["rows"]), o.get("REFUSED"))
    # ---- 12d the host/container FRAME GAP exceeds what was registered
    root, n = fresh("framegap")
    L = open(os.path.join(root, "ledger.txt")).read().replace("wall_s=569 ranks=4", "wall_s=605 ranks=4")
    open(os.path.join(root, "ledger.txt"), "w").write(L)
    o = run(root)
    check("12d_frame_gap_over_registered_allowance_G10_GATE_FAIL",
          "verdicts" in o and o["verdicts"]["G10_cap_discipline"] == "GATE FAIL"
          and all(r["frame_gap_within_allowance"] is False for r in o["report"]["G10"]["rows"]), o.get("REFUSED"))
    # ---- 12e THE D6 SHAPE, DRIVEN BOTH WAYS.  An arm stopped EXACTLY at its
    # in-container deadline.  Under the REPAIRED deadline (1710 s) the host
    # bracket lands inside the cap; under the PREDECESSOR's deadline (1800 s)
    # the same arm would have recorded 121.667 core-min and tripped its own
    # `within_cap` limb -- a GATE FAIL manufactured by the measurement frame.
    hit_host_wall = TMO_REGISTERED_S + 25            # deadline + preamble + poll slop
    hit_core_min = round(hit_host_wall * RANKS / 60.0, 3)
    root, n = fresh("atdeadline")
    L = open(os.path.join(root, "ledger.txt")).read() \
        .replace("wall_s=569 ranks=4", "wall_s=%d ranks=4" % hit_host_wall) \
        .replace("core_min=37.933", "core_min=%.3f" % hit_core_min) \
        .replace("container_wall_s=560", "container_wall_s=%d" % TMO_REGISTERED_S)
    open(os.path.join(root, "ledger.txt"), "w").write(L)
    o = run(root)
    check("12e_at_the_REPAIRED_deadline_host_bracket_is_WITHIN_the_cap",
          "verdicts" in o and o["verdicts"]["G10_cap_discipline"] == "PASS"
          and all(r["within_cap"] for r in o["report"]["G10"]["rows"]),
          {"host_wall_s": hit_host_wall, "core_min": hit_core_min, "cap": CAPS["F-S"]})
    old_host_wall = 1800 + 25
    old_core_min = round(old_host_wall * RANKS / 60.0, 3)
    check("12e_under_the_PREDECESSOR_deadline_the_SAME_arm_would_have_TRIPPED_within_cap",
          old_core_min > CAPS["F-S"] and hit_core_min <= CAPS["F-S"],
          {"predecessor_core_min": old_core_min, "repaired_core_min": hit_core_min, "cap": CAPS["F-S"],
           "note": "the cap did not move; the enforced deadline did"})
    check("12e_the_cap_did_NOT_move", CAPS["F-S"] == 120.0 and CAPS["F-P"] == 120.0 and ITEM_CEILING_CORE_MIN == 240.0)
    check("12e_deadline_plus_allowance_INVERTS_to_the_registered_cap",
          abs((TMO_REGISTERED_S + FRAME_ALLOWANCE_S) * RANKS / 60.0 - CAPS["F-S"]) <= 0.02,
          (TMO_REGISTERED_S + FRAME_ALLOWANCE_S) * RANKS / 60.0)
    # ---- 12f THE BANDS DID NOT MOVE (inherited by citation)
    check("12f_FD_bands_inherited_UNCHANGED",
          FD_BAND_PCT_PER_COMPONENT == 5.0 and FD_BAND_PCT_AGGREGATE == 5.0 and PLATEAU_TOL_PCT == 10.0
          and N_COMPONENTS_REGISTERED == 5 and COMPONENTS_REGISTERED == [["shape", 46], ["shape", 18], ["shape", 0], ["twist", 0], ["patchV", 1]])
    check("12g_P4_band_inherited_UNCHANGED_and_P5_is_STRICTLY_TIGHTER",
          P4_BAND == (0.8, 1.5) and P5_BAND[0] > P4_BAND[0] and P5_BAND[1] < P4_BAND[1])
    # 13 vocabulary
    root, n = fresh("vocab")
    o = run(root)
    check("13_every_verdict_in_the_fixed_vocabulary", "verdicts" in o and all(v in VOCAB for v in o["verdicts"].values()))
    for d in os.listdir(tmpdir):
        if d.startswith("d4sf3sr_selftest_"):
            shutil.rmtree(os.path.join(tmpdir, d), ignore_errors=True)
    mode = "python3 -O" if not __debug__ else "python3"
    print("D4S_F3SR_GRADE SELFTEST mode=%s grader_md5=%s accept_md5=%s" % (mode, md5_of(os.path.abspath(__file__)), md5_of(acc_path)))
    print("\n".join(res))
    print("D4S_F3SR_GRADE SELFTEST pass=%d fail=%d" % (len(res) - fails, fails))
    return 0 if fails == 0 else 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="/home/ubuntu/certonomous-runs/CURRICULUM-D4S-F3SR-a2-wing-cdmin")
    ap.add_argument("--out", default=None)
    ap.add_argument("--accept", default=os.path.join(HERE, "d4s_f3s_accept.py"))
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--tmpdir", default=tempfile.gettempdir())
    a = ap.parse_args()
    if a.selftest:
        return selftest(a.tmpdir)
    if not a.out:
        sys.stderr.write("--out is required for a grade\n")
        return 64
    try:
        verdicts, report = grade(a.base, accept_path=a.accept)
    except Refuse as exc:
        out = {"REFUSED": str(exc)}
        with open(a.out, "w") as fh:
            json.dump(out, fh, indent=1, sort_keys=True, default=str)
        sys.stdout.write("D4S_F3SR_GRADER REFUSED %s\n" % str(exc)[:600])
        return 2
    bad = [v for v in verdicts.values() if v not in VOCAB]
    if bad:
        sys.stderr.write("vocabulary violation %r\n" % bad)
        return 2
    out = {"verdicts": verdicts, "report": report, "grader_md5": md5_of(os.path.abspath(__file__)),
           "registered": {"components": COMPONENTS_REGISTERED, "band_D_pct": FD_BAND_PCT_PER_COMPONENT,
                          "band_E_plateau_pct": PLATEAU_TOL_PCT, "caps": CAPS, "ceiling": ITEM_CEILING_CORE_MIN,
                          "predicted": PREDICTED, "disarm_tol_diff": DISARM_TOL_DIFF}}
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)
    sys.stdout.write("D4S_F3SR_GRADER ITEM=%s %s\n" % (verdicts["ITEM_two_row_endpoint_fd"],
                     json.dumps({k: v for k, v in verdicts.items() if k.startswith(("G5", "G_ACC", "G1_", "G9_two"))}, sort_keys=True)))
    sys.stdout.write("D4S_F3SR_PREDICTIONS %s\n" % json.dumps({k: v for k, v in report["predictions"].items() if not k.endswith("_detail")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
