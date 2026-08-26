#!/usr/bin/env python
"""D4S-F3S GRADER -- the two-row endpoint FD verdict under ONE stationarity
acceptance rule.  Derived from D4-SHIPPED's `d4s_grade.py` (Addendum 2d, md5
f825c2cd...): the FD gate G5, the planted-zero control G6, the blind-reader
control G6b, the count refusals G7, the positional terminal statement, the
kernel-rc clause, the age guard, G10/G11/G12 and the L-342 field classes are
ported with their bands and thresholds UNCHANGED (cited by value from
curriculum_D4/PREREGISTRATION.md:82 -- band D 5 % per component and aggregate,
zero sign flips, band E plateau 10 %).  New, and only these:
  G-ACC  the stationarity acceptance of EVERY primal, re-evaluated HOST-SIDE
         from the per-primal captures with the SAME module the instrument used
         in-container (`d4s_f3s_accept.py`, md5 asserted), the capture count
         bound to the accept records, to the FD file's `n_primals` and to the
         arm log's `Running Primal Solver` count; the disarm record's read-back
         must equal the registered DISARM_TOL_DIFF.
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
ITEM = "D4S-F3S"
ARMS = ["F-S", "F-P"]
ROW_OF = {"F-S": "SHIPPED", "F-P": "PATCHED"}
SO_MD5 = {"SHIPPED": "f0fcb488e0e98156575cd19548e91663",
          "PATCHED": "85f59e87253e0a71a813f64ca6e4c425"}
DIGEST = {"SHIPPED": "sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc",
          "PATCHED": "sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35"}
CAPS = {"F-S": 120.0, "F-P": 120.0}
ITEM_CEILING_CORE_MIN = 240.0
PREDICTED = {"F-S": 47.267, "F-P": 47.267}
P4_BAND = (0.8, 1.5)
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
ARTEFACTS = ["OptView.hst", "d4_endpoint_dvs_PHYSICAL.json", "d4_major_history.json",
             "d4s_f3s_fd_endpoint.json", "d4s_f3s_fd_endpoint.jsonl", "d4s_f3s_accept.jsonl"]
FIELDS_PHYSICS = ["ARM", "ROW", "DIGEST", "rc", "wall_s", "ranks", "core_min", "cap_core_min",
                  "enforced_core_min", "memory", "inspect_exit", "oomkilled", "cpuset", "log", "stamp"]
FIELDS_INFRASTRUCTURE = ["memavail_pre_GiB", "memavail_post_GiB", "delivered", "siblings_pre", "siblings_post"]
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
            "siblings_post": r"siblings_post=\[([^\]]*)\]"}


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
    terminal statement; every registered artefact newer than the arm's copy epoch."""
    out = {"arm": arm, "rc": row["rc"], "inspect_exit": row["inspect_exit"], "oomkilled": row["oomkilled"]}
    if str(row["inspect_exit"]) != str(row["rc"]):
        refuse("G1", {"arm": arm, "harness_rc_vs_kernel_rc_disagree": [row["rc"], row["inspect_exit"]]})
    out["rc_clause_pass"] = bool(row["rc"] == 0 and str(row["oomkilled"]).lower() == "false")
    ok, det = terminal_statement_ok(os.path.join(base, row["log"]))
    out["terminal_clause_pass"], out["terminal_detail"] = bool(ok), det
    ep = os.path.join(work, ".d4s_f3s_stage_%s_copy_epoch" % arm)
    if not os.path.isfile(ep):
        refuse("G1-age", {"arm": arm, "copy_epoch_absent": ep})
    datum = int(open(ep).read().strip())
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
    out["pass"] = bool(out["rc_clause_pass"] and out["terminal_clause_pass"] and out["age_clause_pass"])
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
    rows, total = [], 0.0
    for arm in ARMS:
        r = rows_by_arm[arm]
        reg = CAPS[arm]
        rows.append({"arm": arm, "registered": reg, "ledger_cap": r["cap_core_min"], "enforced": r["enforced_core_min"],
                     "actual": r["core_min"],
                     "cap_equals_registered": bool(abs(r["cap_core_min"] - reg) < 1e-9 and abs(r["enforced_core_min"] - reg) <= 0.02),
                     "within_cap": bool(r["core_min"] <= reg + 1e-9)})
        total += r["core_min"]
    return {"rows": rows, "total_core_min": total, "item_ceiling": ITEM_CEILING_CORE_MIN,
            "pass": bool(all(x["cap_equals_registered"] and x["within_cap"] for x in rows) and total <= ITEM_CEILING_CORE_MIN)}


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
    p["P4_detail"] = {"ratios": ratios, "band": list(P4_BAND), "predicted": PREDICTED}
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


def build_fixture(root, acc_path):
    """A sacrificial root built from REAL artefacts: curriculum_D4's F3 table
    and its 22 real primal blocks stand in for both arms."""
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
    for arm in ARMS:
        row = ROW_OF[arm]
        work = os.path.join(root, arm)
        os.makedirs(work, exist_ok=True)
        with open(os.path.join(work, ".d4s_f3s_stage_%s_copy_epoch" % arm), "w") as fh:
            fh.write("1000000000\n")
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
        for a in ("OptView.hst", "d4_endpoint_dvs_PHYSICAL.json", "d4_major_history.json"):
            with open(os.path.join(work, a), "w") as fh:
                fh.write("{}\n")
        for r in range(RANKS):
            with open(os.path.join(work, "d4_placement_rank%d.json" % r), "w") as fh:
                json.dump({"rank": r, "affinity": [CPUSET_REGISTERED[r]], "n_cores": 1}, fh)
        log = "%s_20260826T000000Z_1.log" % arm
        with open(os.path.join(root, log), "w") as fh:
            fh.write("D4S_CONTAINER_UID: 0\nD4S_IDWARP_SO_MD5: %s\n" % SO_MD5[row])
            for b in blocks:
                fh.write("Running Primal Solver 001\n" + b + "\n")
            fh.write("D4S_F3S_FD_ENDPOINT_WRITTEN d4s_f3s_fd_endpoint.json n_rows=5 n_primals=%d\nFinalising parallel run\n" % len(blocks))
        ledger.append("ARM=%s ROW=%s IMG=x DIGEST=%s rc=0 wall_s=709 ranks=4 core_min=47.267 cap_core_min=120.0 enforced_wall_s=1800 enforced_core_min=120.000000 memory=12g inspect(exit,oomkilled)=[0 false] memavail_pre_GiB=26.39 memavail_post_GiB=26.42 cpuset=5,6,7,9 delivered_cores_mean=[3.9752 n=69 max_nr_throttled=2070] siblings_pre=[] siblings_post=[] log=%s stamp=1" % (arm, row, DIGEST[row], log))
    with open(os.path.join(root, "ledger.txt"), "w") as fh:
        fh.write("\n".join(ledger) + "\n")
    return len(blocks)


def selftest(tmpdir):
    acc_path = os.path.join(HERE, "d4s_f3s_accept.py")
    res, fails = [], 0

    def check(name, cond, detail=""):
        nonlocal fails
        res.append("  [%s] %s %s" % ("OK " if cond else "BAD", name, str(detail)[:200]))
        if not cond:
            fails += 1

    def fresh(tag):
        root = os.path.join(tmpdir, "d4sf3s_selftest_" + tag)
        shutil.rmtree(root, ignore_errors=True)
        n = build_fixture(root, acc_path)
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
    # 2 rc=1 -> G1 fails -> NOT A RESULT
    root, n = fresh("rc1")
    L = open(os.path.join(root, "ledger.txt")).read().replace("ARM=F-S ROW=SHIPPED IMG=x DIGEST=%s rc=0" % DIGEST["SHIPPED"], "ARM=F-S ROW=SHIPPED IMG=x DIGEST=%s rc=1" % DIGEST["SHIPPED"]).replace("inspect(exit,oomkilled)=[0 false] memavail_pre_GiB=26.39 memavail_post_GiB=26.42 cpuset=5,6,7,9 delivered_cores_mean=[3.9752 n=69 max_nr_throttled=2070] siblings_pre=[] siblings_post=[] log=F-S", "inspect(exit,oomkilled)=[1 false] memavail_pre_GiB=26.39 memavail_post_GiB=26.42 cpuset=5,6,7,9 delivered_cores_mean=[3.9752 n=69 max_nr_throttled=2070] siblings_pre=[] siblings_post=[] log=F-S")
    open(os.path.join(root, "ledger.txt"), "w").write(L)
    o = run(root)
    check("2_rc1_G1_NOT_A_RESULT_item_NOT_A_RESULT", "verdicts" in o and o["verdicts"]["G1_completion_and_age_F-S"] == "NOT A RESULT" and o["verdicts"]["ITEM_two_row_endpoint_fd"] == "NOT A RESULT", o.get("REFUSED"))
    # 2b harness/kernel disagreement -> REFUSE
    root, n = fresh("disagree")
    L = open(os.path.join(root, "ledger.txt")).read().replace("inspect(exit,oomkilled)=[0 false] memavail_pre_GiB=26.39 memavail_post_GiB=26.42 cpuset=5,6,7,9 delivered_cores_mean=[3.9752 n=69 max_nr_throttled=2070] siblings_pre=[] siblings_post=[] log=F-P", "inspect(exit,oomkilled)=[1 false] memavail_pre_GiB=26.39 memavail_post_GiB=26.42 cpuset=5,6,7,9 delivered_cores_mean=[3.9752 n=69 max_nr_throttled=2070] siblings_pre=[] siblings_post=[] log=F-P")
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
    # 4 stale artefact -> age fails
    root, n = fresh("stale")
    open(os.path.join(root, "F-S", ".d4s_f3s_stage_F-S_copy_epoch"), "w").write("%d\n" % (int(__import__("time").time()) + 100000))
    o = run(root)
    check("4_stale_artefacts_age_clause_fails", "verdicts" in o and o["verdicts"]["G1_completion_and_age_F-S"] == "NOT A RESULT" and o["report"]["G1"]["F-S"]["n_stale"] == len(ARTEFACTS), o.get("REFUSED"))
    # 4b artefact absent -> REFUSE at G1-age
    root, n = fresh("absent")
    os.remove(os.path.join(root, "F-S", "d4s_f3s_fd_endpoint.json"))
    o = run(root)
    check("4b_absent_graded_artefact_REFUSES", "REFUSED" in o and "graded_artifact_absent" in o["REFUSED"], o.get("REFUSED", "")[:100])
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
    L = open(os.path.join(root, "ledger.txt")).read().replace("inspect(exit,oomkilled)=[0 false] memavail_pre_GiB=26.39 memavail_post_GiB=26.42 cpuset=5,6,7,9 delivered_cores_mean=[3.9752 n=69 max_nr_throttled=2070] siblings_pre=[] siblings_post=[] log=F-P", "inspect(exit,oomkilled)=[0 true] memavail_pre_GiB=26.39 memavail_post_GiB=26.42 cpuset=5,6,7,9 delivered_cores_mean=[3.9752 n=69 max_nr_throttled=2070] siblings_pre=[] siblings_post=[] log=F-P")
    open(os.path.join(root, "ledger.txt"), "w").write(L)
    o = run(root)
    check("10_oom_row_G11_NOT_A_RESULT", "verdicts" in o and o["verdicts"]["G11_memory_envelope"] == "NOT A RESULT" and o["verdicts"]["ITEM_two_row_endpoint_fd"] == "NOT A RESULT", o.get("REFUSED"))
    # 11 cap crossing -> G10 GATE FAIL, P4 MISS
    root, n = fresh("cap")
    L = open(os.path.join(root, "ledger.txt")).read().replace("core_min=47.267 cap_core_min=120.0 enforced_wall_s=1800 enforced_core_min=120.000000 memory=12g inspect(exit,oomkilled)=[0 false] memavail_pre_GiB=26.39 memavail_post_GiB=26.42 cpuset=5,6,7,9 delivered_cores_mean=[3.9752 n=69 max_nr_throttled=2070] siblings_pre=[] siblings_post=[] log=F-S", "core_min=130.0 cap_core_min=120.0 enforced_wall_s=1800 enforced_core_min=120.000000 memory=12g inspect(exit,oomkilled)=[0 false] memavail_pre_GiB=26.39 memavail_post_GiB=26.42 cpuset=5,6,7,9 delivered_cores_mean=[3.9752 n=69 max_nr_throttled=2070] siblings_pre=[] siblings_post=[] log=F-S")
    open(os.path.join(root, "ledger.txt"), "w").write(L)
    o = run(root)
    check("11_cap_crossing_G10_GATE_FAIL_P4_MISS", "verdicts" in o and o["verdicts"]["G10_cap_discipline"] == "GATE FAIL" and o["report"]["predictions"]["P4_cost_ratio_per_arm_in_band"] == "MISS", o.get("REFUSED"))
    # 12 placement collision -> G12 GATE FAIL
    root, n = fresh("place")
    json.dump({"rank": 1, "affinity": [5], "n_cores": 1}, open(os.path.join(root, "F-P", "d4_placement_rank1.json"), "w"))
    o = run(root)
    check("12_two_ranks_on_one_core_G12_GATE_FAIL", "verdicts" in o and o["verdicts"]["G12_cpu_placement_F-P"] == "GATE FAIL", o.get("REFUSED"))
    # 13 vocabulary
    root, n = fresh("vocab")
    o = run(root)
    check("13_every_verdict_in_the_fixed_vocabulary", "verdicts" in o and all(v in VOCAB for v in o["verdicts"].values()))
    for d in os.listdir(tmpdir):
        if d.startswith("d4sf3s_selftest_"):
            shutil.rmtree(os.path.join(tmpdir, d), ignore_errors=True)
    mode = "python3 -O" if not __debug__ else "python3"
    print("D4S_F3S_GRADE SELFTEST mode=%s grader_md5=%s accept_md5=%s" % (mode, md5_of(os.path.abspath(__file__)), md5_of(acc_path)))
    print("\n".join(res))
    print("D4S_F3S_GRADE SELFTEST pass=%d fail=%d" % (len(res) - fails, fails))
    return 0 if fails == 0 else 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="/home/ubuntu/certonomous-runs/CURRICULUM-D4S-F3S-a2-wing-cdmin")
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
        sys.stdout.write("D4S_F3S_GRADER REFUSED %s\n" % str(exc)[:600])
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
    sys.stdout.write("D4S_F3S_GRADER ITEM=%s %s\n" % (verdicts["ITEM_two_row_endpoint_fd"],
                     json.dumps({k: v for k, v in verdicts.items() if k.startswith(("G5", "G_ACC", "G1_", "G9_two"))}, sort_keys=True)))
    sys.stdout.write("D4S_F3S_PREDICTIONS %s\n" % json.dumps({k: v for k, v in report["predictions"].items() if not k.endswith("_detail")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
