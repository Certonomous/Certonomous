#!/usr/bin/env python3
"""Curriculum D4 grader -- MACH wing constrained CD minimisation at fixed CL.

REFUSES (exit 2) rather than degrades.  CLAUDE.md rule 4.

The defect this grader is built against, verbatim from the supervisor's brief:
`A4/curriculum_D3/d3_grade.py`'s gate G3+G4 returned PASS at 0.0000 % with zero
sign flips OVER AN EMPTY COMPONENT SET -- a present-but-unparseable FD block
yielded an empty list WITH THE KEY PRESENT, the refusal tested key presence and
never non-emptiness, the plateau loop iterated zero times so a step was
"selected" without one comparison, and the discrimination control fired
correctly and certified a result it had not measured.

Therefore, here:
  * G5 refuses on an EMPTY **or SHORT** component set EXPLICITLY, BY COUNT,
    WITH THE COUNT PRINTED, against the count registered before compute.
  * Every loop that could iterate zero times asserts its own trip count and
    prints it.
  * G7 is a live negative control that DELIBERATELY empties and DELIBERATELY
    shortens the row list and requires a NAMED refusal from each.  A control
    that cannot make the gate refuse is not a control (L-302).
  * G6 plants a known perturbation into the artifact ON DISK, reads it back
    THROUGH THE SAME READER, and refuses if the reader cannot see it; and a
    blind reader -- one that ignores the path it is handed -- must be REFUSED.

Every graded number is read from a FILE.  MPI log splicing on this exact case
is MEASURED (A2 per_component_table §2.2, commit 79679a84): four ranks
interleave on one stdout and sever arrays mid-number.  Nothing here parses
stdout for a graded quantity; stdout is read only for provenance markers
(container uid, IDWarp .so md5) which are single short lines whose corruption
would make them fail to match rather than silently mis-read.

D4-DEF-1 SUPPLEMENT.  This file is NOT `d4_grade.py`.  `d4_grade.py` is
frozen at md5 f162ef69a7385e5d0586ef5f27657cbb by PREREGISTRATION.md 9a and is
NOT edited (CLAUDE.md rule 6).  This supplement carries that file's grading
body BYTE-FOR-BYTE and repairs exactly one defect: the frozen `--selftest`
flag is declared at argparse and never read, so it silently runs a FULL GRADE.
Here it is WIRED to a real selftest with a DISTINCT exit path.  See the
D4-DEF-1 REPAIR section and `d4_grade_D4DEF1_REPAIR.diff`.
"""
import argparse
import hashlib
import json
import math
import os
import re
import shutil
import sys

# ================= REGISTERED CONSTANTS (PREREGISTRATION.md) ===============
N_COMPONENTS_REGISTERED = 5           # §6 -- named in advance, by name
COMPONENTS_REGISTERED = [["shape", 46], ["shape", 18], ["shape", 0],
                         ["twist", 0], ["patchV", 1]]
CL_TARGET = 0.5
CL_TOL_PER_MAJOR = 5.0e-4             # §4 band A
CL_TOL_FINAL = 1.0e-5                 # §4 band B (IPOPT constr_viol_tol)
DRAG_BAND_PCT = (25.0, 45.0)          # §4 band C
FD_BAND_PCT_PER_COMPONENT = 5.0       # §4 band D
FD_BAND_PCT_AGGREGATE = 5.0           # §4 band D
PLATEAU_TOL_PCT = 10.0                # §7
CD_BASELINE_A2 = 2.9619634e-02        # A2's own opt_IPOPT.txt iteration 0
NCELLS = 38304
RANKS = 4
DECOMP_METHOD = "scotch"
CPUSET_REGISTERED = [5, 6, 7, 9]      # §5b -- pinned before compute
DELIVERED_CORES_FLOOR = 3.0           # §5b -- of a 4-core quota
CAPS = {"P1": 5.0, "P2": 55.0, "O": 620.0, "F": 120.0}
ITEM_CEILING_CORE_MIN = 800.0
MD5_RUNSCRIPT = "2906d52a5dbed2bacbaeaf85a37d3fe8"
PLANT = 1.234e-03                     # rule 3

VOCAB = {"PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED",
         "PENDING"}


class Refuse(Exception):
    pass


def refuse(where, detail):
    raise Refuse("%s: %s" % (where, json.dumps(detail, sort_keys=True,
                                               default=str)[:1200]))


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


# ------------------------------------------------------------------ readers
def read_json(path, where):
    if not os.path.isfile(path):
        refuse(where, {"absent": path})
    if os.path.getsize(path) == 0:
        refuse(where, {"empty_file": path})
    with open(path) as fh:
        try:
            return json.load(fh)
        except Exception as exc:                       # noqa: BLE001
            refuse(where, {"unparseable": path, "error": repr(exc)[:300]})


IPOPT_ROW = re.compile(
    r"^\s*(\d+)r?\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s")


def read_ipopt(path, where="read_ipopt"):
    """Parse IPOPT's OWN output file.  This is written by IPOPT to
    `opt_IPOPT.txt`, not to stdout, so the MPI interleave cannot reach it."""
    if not os.path.isfile(path):
        refuse(where, {"absent": path})
    txt = open(path, errors="replace").read()
    rows = []
    for line in txt.splitlines():
        m = IPOPT_ROW.match(line)
        if m:
            try:
                rows.append({"iter": int(m.group(1)),
                             "objective": float(m.group(2)),
                             "inf_pr": float(m.group(3)),
                             "inf_du": float(m.group(4))})
            except ValueError:
                continue
    exits = [l.strip() for l in txt.splitlines() if l.strip().startswith("EXIT")]
    if not rows:
        refuse(where, {"no_iteration_rows_parsed": path,
                       "bytes": len(txt),
                       "note": "an IPOPT file with zero parsed rows is a "
                               "parser failure, not a converged run"})
    return {"rows": rows, "n_rows": len(rows), "exit_lines": exits,
            "path": os.path.abspath(path), "md5": md5_of(path)}


# ------------------------------------------------------------------- gates
def g_completion(work, ledger_rows, arms_required):
    """G1.  Strict completion, DAFoam analogue of CLAUDE.md rule 4.

    Rule 4's field list (`T U p_rgh alphat nut k omega`) is the THERMAL
    family's and does not apply to a compressible DAFoam optimisation.  The
    clauses that DO apply are carried through unchanged: rc == 0, a terminal
    statement from the producer's own log FILE, and the AGE GUARD -- every
    graded artifact strictly NEWER than the case's own `0/` reference, which
    the launcher touches LAST at stage time and records in `.d4_age_datum`.
    """
    out = {"arms_required": arms_required, "arms": {}}
    datum_path = os.path.join(work, ".d4_age_datum")
    if not os.path.isfile(datum_path):
        refuse("G1", {"age_datum_absent": datum_path})
    datum = int(open(datum_path).read().strip())
    ref = os.path.join(work, "0", "U")
    if not os.path.isfile(ref):
        refuse("G1", {"age_reference_absent": ref})
    if int(os.path.getmtime(ref)) != datum:
        refuse("G1", {"age_reference_moved": ref,
                      "recorded": datum, "on_disk": int(os.path.getmtime(ref))})
    out["age_datum_epoch"] = datum
    n_checked = 0
    for arm in arms_required:
        hits = [r for r in ledger_rows if r.get("ARM") == arm]
        if not hits:
            refuse("G1", {"arm_absent_from_ledger": arm})
        r = hits[-1]
        out["arms"][arm] = {"rc": r["rc"], "core_min": r["core_min"],
                            "oomkilled": r["oomkilled"],
                            "inspect_exit": r["inspect_exit"]}
        n_checked += 1
    if n_checked != len(arms_required):
        refuse("G1", {"arms_checked": n_checked,
                      "arms_required": len(arms_required)})
    out["n_arms_checked"] = n_checked
    return out


def g_age(work, artifacts, datum):
    """The age guard, applied by name to every graded artifact."""
    rows, n = [], 0
    for a in artifacts:
        p = os.path.join(work, a)
        if not os.path.isfile(p):
            refuse("G1-age", {"graded_artifact_absent": p})
        m = int(os.path.getmtime(p))
        rows.append({"artifact": a, "mtime": m, "newer_than_datum": m > datum})
        n += 1
    if n == 0:
        refuse("G1-age", {"artifacts_checked": 0,
                          "note": "an age guard that checked nothing is not a "
                                  "guard"})
    stale = [r for r in rows if not r["newer_than_datum"]]
    return {"n_checked": n, "rows": rows, "n_stale": len(stale),
            "pass": bool(not stale)}


def g_decomposition(work):
    """G8.  Determinism DEMONSTRATED, not asserted: the same decomposition,
    re-run, must produce the same processorN cell counts.

    Registered method: `scotch`, numberOfSubdomains 4, from the case's own
    `system/decomposeParDict`.  OpenFOAM's `scotchDecomp` exposes NO seed
    parameter, so determinism here is an EMPIRICAL claim about this build and
    this mesh -- it is not determinism by construction, and this gate is the
    only evidence for it.  That limitation is registered, not discovered.
    """
    a = read_json(os.path.join(work, "d4_decomp_A.json"), "G8")
    b = read_json(os.path.join(work, "d4_decomp_B.json"), "G8")
    if not a or not b:
        refuse("G8", {"empty_decomposition_map": {"A": len(a), "B": len(b)}})
    if len(a) != RANKS or len(b) != RANKS:
        refuse("G8", {"n_processor_dirs": {"A": len(a), "B": len(b)},
                      "expected": RANKS})
    tot_a, tot_b = sum(a.values()), sum(b.values())
    if tot_a != NCELLS:
        refuse("G8", {"cell_total_A": tot_a, "expected": NCELLS})
    dp = os.path.join(work, "system", "decomposeParDict")
    dict_txt = open(dp).read() if os.path.isfile(dp) else ""
    method_ok = bool(re.search(r"^\s*method\s+%s\s*;" % DECOMP_METHOD,
                               dict_txt, re.M))
    nsub_ok = bool(re.search(r"^\s*numberOfSubdomains\s+%d\s*;" % RANKS,
                             dict_txt, re.M))
    return {"A": a, "B": b, "identical": bool(a == b),
            "cells_A": tot_a, "cells_B": tot_b, "cells_expected": NCELLS,
            "method_registered": DECOMP_METHOD, "method_in_dict": method_ok,
            "numberOfSubdomains_in_dict": nsub_ok,
            "pass": bool(a == b and tot_a == NCELLS and tot_b == NCELLS
                         and method_ok and nsub_ok)}


def g_termination(ip):
    """G3.  DAFOAM_CHARTER §9.  A cap-stop is GATE REACHED or NOT A RESULT,
    NEVER PASS -- and never described by the size of the improvement."""
    conv = [l for l in ip["exit_lines"] if "Optimal Solution Found" in l]
    other = [l for l in ip["exit_lines"] if l not in conv]
    last = ip["rows"][-1]
    return {"exit_lines": ip["exit_lines"], "converged": bool(conv),
            "other_exit_lines": other, "n_majors": last["iter"],
            "n_rows_parsed": ip["n_rows"], "final_inf_pr": last["inf_pr"],
            "final_inf_du": last["inf_du"], "final_objective": last["objective"]}


def g_cl(hist):
    """G2.  CL feasibility per major, from the pyOptSparse history FILE."""
    cl = hist.get("CL")
    if cl is None:
        refuse("G2", {"CL_key_absent": sorted(hist.keys())})
    if not isinstance(cl, list) or len(cl) == 0:
        refuse("G2", {"CL_empty_or_not_a_list": type(cl).__name__,
                      "len": (len(cl) if isinstance(cl, list) else None),
                      "note": "a present-but-empty key is exactly the D3 "
                              "defect; this gate refuses on it BY COUNT"})
    n = len(cl)
    devs = [abs(v - CL_TARGET) for v in cl]
    n_compared = len(devs)
    if n_compared != n:
        refuse("G2", {"comparisons": n_compared, "majors": n})
    worst = max(devs)
    bad = [i for i, d in enumerate(devs) if d > CL_TOL_PER_MAJOR]
    return {"n_majors": n, "n_comparisons": n_compared,
            "worst_abs_dev": worst, "final_abs_dev": devs[-1],
            "band_per_major": CL_TOL_PER_MAJOR, "band_final": CL_TOL_FINAL,
            "n_outside_per_major_band": len(bad), "outside_indices": bad[:20],
            "pass_per_major": bool(not bad),
            "pass_final": bool(devs[-1] <= CL_TOL_FINAL)}


def g_drag(hist, ip):
    """G4.  Drag reduction against the band frozen before compute."""
    cd = hist.get("CD")
    if not cd:
        refuse("G4", {"CD_empty_or_absent": True, "len": len(cd or [])})
    cd0, cdf = cd[0], cd[-1]
    red = 100.0 * (cd0 - cdf) / cd0
    ip0 = ip["rows"][0]["objective"]
    return {"CD_first_major": cd0, "CD_final": cdf,
            "reduction_pct": red, "band_pct": list(DRAG_BAND_PCT),
            "in_band": bool(DRAG_BAND_PCT[0] <= red <= DRAG_BAND_PCT[1]),
            "CD_baseline_A2_record": CD_BASELINE_A2,
            "ipopt_iter0_objective": ip0,
            "baseline_matches_A2": bool(abs(ip0 - CD_BASELINE_A2)
                                        <= 1e-6 * abs(CD_BASELINE_A2))}


# ------------------------------- G5: the FD table, and the COUNT refusal ---
def g_fd(fd, where="G5"):
    """G5.  The endpoint FD table.

    THE COUNT REFUSAL, first, before anything else is read.  A present-but-
    empty or present-but-short `rows` list is the D3 defect verbatim and it is
    REFUSED HERE BY COUNT, with the count PRINTED.
    """
    rows = fd.get("rows")
    n_registered = N_COMPONENTS_REGISTERED
    if rows is None:
        refuse(where, {"rows_key_absent": True, "n_rows": 0,
                       "n_registered": n_registered})
    if not isinstance(rows, list):
        refuse(where, {"rows_not_a_list": type(rows).__name__,
                       "n_registered": n_registered})
    n_rows = len(rows)
    if n_rows == 0:
        refuse(where, {"COUNT_REFUSAL": "empty component set",
                       "n_rows": 0, "n_registered": n_registered})
    if n_rows != n_registered:
        refuse(where, {"COUNT_REFUSAL": "short or long component set",
                       "n_rows": n_rows, "n_registered": n_registered})
    got = [[r.get("dv"), r.get("idx")] for r in rows]
    if got != COMPONENTS_REGISTERED:
        refuse(where, {"COUNT_REFUSAL": "component set is not the registered "
                                        "set, in the registered order",
                       "n_rows": n_rows, "got": got,
                       "registered": COMPONENTS_REGISTERED})

    eta = float(fd["eta_used"].strip("'\"") if isinstance(fd["eta_used"], str)
                else fd["eta_used"])
    graded, near_zero, ungradeable = [], [], []
    n_plateau_comparisons = 0
    for r in rows:
        tag = "%s[%d]" % (r["dv"], r["idx"])
        if r.get("status") != "PLANNED":
            (near_zero if r.get("status") == "NEAR_ZERO"
             else ungradeable).append({"component": tag,
                                       "status": r.get("status"),
                                       "J_adj": r.get("J_adj"),
                                       "max_clearance": r.get("max_clearance")})
            continue
        fdb = r.get("fd") or {}
        lo, hi = fdb.get("s_lo"), fdb.get("s_hi")
        if not (lo and hi and lo.get("ok") and hi.get("ok")):
            ungradeable.append({"component": tag, "status": "FD_STEP_FAILED",
                                "s_lo": lo, "s_hi": hi})
            continue
        d_lo = float(str(lo["d"]).strip("'\""))
        d_hi = float(str(hi["d"]).strip("'\""))
        j = float(str(r["J_adj"]).strip("'\""))
        if d_hi == 0.0:
            ungradeable.append({"component": tag, "status": "FD_ZERO_AT_S_HI"})
            continue
        plateau = 100.0 * abs(d_hi - d_lo) / abs(d_hi)
        n_plateau_comparisons += 1
        rel = 100.0 * abs(j - d_hi) / abs(d_hi)
        graded.append({"component": tag, "s_lo": lo["step"], "s_hi": hi["step"],
                       "d_lo": d_lo, "d_hi": d_hi, "J_adj": j,
                       "plateau_pct": plateau,
                       "plateau_ok": bool(plateau <= PLATEAU_TOL_PCT),
                       "rel_err_pct": rel,
                       "in_band": bool(rel <= FD_BAND_PCT_PER_COMPONENT),
                       "sign_flip": bool(j * d_hi < 0.0),
                       "C_lo": r.get("C_lo"), "C_hi": r.get("C_hi")})

    # a plateau loop that iterated zero times "selected" nothing -- D3's defect
    if n_plateau_comparisons != len(graded):
        refuse(where, {"plateau_comparisons": n_plateau_comparisons,
                       "graded_rows": len(graded)})
    if graded:
        num = math.sqrt(sum((g["J_adj"] - g["d_hi"]) ** 2 for g in graded))
        den = math.sqrt(sum(g["d_hi"] ** 2 for g in graded))
        agg = 100.0 * num / den if den else float("inf")
    else:
        agg = None
    n_flips = sum(1 for g in graded if g["sign_flip"])
    n_no_plateau = sum(1 for g in graded if not g["plateau_ok"])
    return {"n_rows": n_rows, "n_registered": n_registered,
            "eta_used": eta, "eta_floored": fd.get("eta_floored"),
            "n_graded": len(graded), "n_near_zero": len(near_zero),
            "n_ungradeable": len(ungradeable),
            "n_plateau_comparisons": n_plateau_comparisons,
            "graded": graded, "near_zero": near_zero,
            "ungradeable": ungradeable,
            "aggregate_rel_err_pct": agg,
            "aggregate_band_pct": FD_BAND_PCT_AGGREGATE,
            "n_sign_flips": n_flips, "n_without_plateau": n_no_plateau,
            "coverage": "%d of %d" % (len(graded), n_registered)}


# ------------------------------------------------- G6/G7: the live controls
def planted_zero_control(fd_path, workdir, reader=read_json):
    """G6.  Rule 3.  Plant a KNOWN perturbation into the artifact ON DISK,
    read it back THROUGH THE SAME READER, and refuse if the reader cannot see
    it.  A zero from a reader not shown able to see a non-zero is not evidence.
    """
    before = md5_of(fd_path)
    base = reader(fd_path, "G6-base")
    baseg = g_fd(base, "G6-base")
    if baseg["n_graded"] == 0:
        # the plant needs a graded row to move; if there is none, SAY SO
        return {"pass": False, "reason": "NO_GRADED_ROW_TO_PLANT_INTO",
                "n_graded": 0,
                "note": "the control could not be run; this is reported as "
                        "an unmeasured channel, never as a passing control"}
    if not os.path.isdir(workdir):
        os.makedirs(workdir)
    planted_path = os.path.join(workdir, "d4_fd_endpoint.PLANTED.json")
    doc = reader(fd_path, "G6-copy")
    moved = None
    for r in doc["rows"]:
        if r.get("status") == "PLANNED" and (r.get("fd") or {}).get("s_hi", {}).get("ok"):
            old = float(str(r["fd"]["s_hi"]["d"]).strip("'\""))
            r["fd"]["s_hi"]["d"] = repr(old * (1.0 + PLANT))
            moved = {"component": "%s[%d]" % (r["dv"], r["idx"]),
                     "from": old, "to": old * (1.0 + PLANT)}
            break
    if moved is None:
        return {"pass": False, "reason": "NO_PLANTABLE_ROW"}
    with open(planted_path, "w") as fh:
        json.dump(doc, fh)
    plantedg = g_fd(reader(planted_path, "G6-planted"), "G6-planted")
    seen_channels = {
        "rel_err_pct": abs(plantedg["graded"][0]["rel_err_pct"]
                           - baseg["graded"][0]["rel_err_pct"]) > 1e-9,
        "plateau_pct": abs(plantedg["graded"][0]["plateau_pct"]
                           - baseg["graded"][0]["plateau_pct"]) > 1e-9,
        "aggregate": abs((plantedg["aggregate_rel_err_pct"] or 0.0)
                         - (baseg["aggregate_rel_err_pct"] or 0.0)) > 1e-12,
    }
    after = md5_of(fd_path)
    out = {"plant": PLANT, "moved": moved, "channel_seen": seen_channels,
           "src_md5_before": before, "src_md5_after": after,
           "src_unchanged": bool(before == after),
           "pass": bool(all(seen_channels.values()) and before == after)}
    os.remove(planted_path)
    if not out["pass"]:
        refuse("G6", out)
    return out


def negative_control(fd_path, workdir):
    """G6b.  The control must be able to FAIL.  A deliberately BLIND reader --
    one that returns the unperturbed document whatever path it is handed --
    must be REFUSED.  A planted-zero control that cannot refuse is not a
    control."""
    def blind(_p, where=None, _real=fd_path):
        return read_json(_real, where or "blind")
    try:
        planted_zero_control(fd_path, workdir, reader=blind)
    except Refuse as exc:
        return {"pass": True, "refused_with": str(exc)[:300]}
    return {"pass": False, "refused_with": None,
            "note": "the blind reader was ACCEPTED -- G6 is not a control"}


def count_controls(fd_path, workdir):
    """G7.  THE control this grader exists for.  Hand the FD gate (a) an EMPTY
    row list and (b) a SHORT row list, and require a NAMED refusal from each,
    with the count printed.  L-302: an instrument that cannot say "I measured
    nothing" will report a number it did not measure."""
    if not os.path.isdir(workdir):
        os.makedirs(workdir)
    results = {}
    for label, mutate in (
        ("empty", lambda d: d.update({"rows": []})),
        ("short", lambda d: d.update({"rows": d["rows"][:2]})),
        ("reordered", lambda d: d.update({"rows": list(reversed(d["rows"]))})),
        ("key_absent", lambda d: d.pop("rows", None)),
    ):
        doc = read_json(fd_path, "G7-src")
        mutate(doc)
        p = os.path.join(workdir, "d4_fd_endpoint.G7_%s.json" % label)
        with open(p, "w") as fh:
            json.dump(doc, fh)
        try:
            g_fd(read_json(p, "G7-%s" % label), "G7-%s" % label)
            results[label] = {"pass": False, "refused_with": None,
                              "note": "mutation was ACCEPTED"}
        except Refuse as exc:
            results[label] = {"pass": True, "refused_with": str(exc)[:400]}
        os.remove(p)
    results["pass"] = all(v["pass"] for k, v in results.items() if k != "pass")
    return results


def g_placement(p1dir, ledger_rows):
    """G12.  CPU PLACEMENT -- MEASURED, never inferred from the quota flag.

    `mpirun` inside a `--cpus=N` container binds rank 0 to the FIRST CORE OF
    THE HOST TOPOLOGY; concurrent containers collide there and throughput
    collapses as 1/N while the box reports itself idle (MEASURED, D13 lane,
    2026-08-25: 0.250 cores delivered against a 1.0-core quota, host 61 % idle).
    `--cpus=4` does NOT hand out four distinct cores.

    This gate refuses BY COUNT on a short set of per-rank placement files, for
    the same reason G5 does: a placement gate that reads zero ranks and reports
    no collision has measured nothing.

    It also exists to stop a specific FALSE FINDING.  A slow adjoint at np=4
    reads exactly like GMRES stagnation, which is a REAL failure mode measured
    on this ladder at N=52.  No adjoint-conditioning finding may be recorded by
    this item until this gate has ruled out core contention.
    """
    import glob
    files = sorted(glob.glob(os.path.join(p1dir, "d4_placement_rank*.json")))
    n_files = len(files)
    if n_files == 0:
        refuse("G12", {"COUNT_REFUSAL": "no per-rank placement files",
                       "n_files": 0, "n_expected": RANKS, "dir": p1dir})
    if n_files != RANKS:
        refuse("G12", {"COUNT_REFUSAL": "short or long placement set",
                       "n_files": n_files, "n_expected": RANKS})
    ranks, n_read = {}, 0
    for f in files:
        d = read_json(f, "G12")
        if "rank" not in d or "affinity" not in d:
            refuse("G12", {"placement_file_malformed": f,
                           "keys": sorted(d.keys())})
        if not d["affinity"]:
            refuse("G12", {"empty_affinity_mask": f})
        ranks[int(d["rank"])] = sorted(int(c) for c in d["affinity"])
        n_read += 1
    if n_read != RANKS or sorted(ranks.keys()) != list(range(RANKS)):
        refuse("G12", {"ranks_read": sorted(ranks.keys()), "expected": RANKS})
    union = sorted(set(c for v in ranks.values() for c in v))
    inside = bool(set(union) <= set(CPUSET_REGISTERED))
    # the defect's signature: every rank pinned to ONE shared core
    singles = [v[0] for v in ranks.values() if len(v) == 1]
    collided = bool(len(singles) == RANKS and len(set(singles)) < RANKS)
    distinct = bool(len(singles) == RANKS and len(set(singles)) == RANKS)
    delivered_rows, n_delivered = [], 0
    for r in ledger_rows:
        dv = (r.get("delivered") or "").split()
        val = None
        if dv and dv[0] not in ("NOT_MEASURED", ""):
            try:
                val = float(dv[0])
            except ValueError:
                val = None
        delivered_rows.append({"arm": r["ARM"], "cpuset": r.get("cpuset"),
                               "delivered_cores_mean": val,
                               "raw": r.get("delivered"),
                               "siblings_pre": r.get("siblings_pre"),
                               "siblings_post": r.get("siblings_post"),
                               "cpuset_as_registered": bool(
                                   r.get("cpuset") ==
                                   ",".join(str(c) for c in CPUSET_REGISTERED))})
        if val is not None:
            n_delivered += 1
    mpi_arms = [d for d in delivered_rows
                if d["arm"] in ("P2", "O", "F")
                and d["delivered_cores_mean"] is not None]
    starved = [d for d in mpi_arms
               if d["delivered_cores_mean"] < DELIVERED_CORES_FLOOR]
    return {"n_placement_files": n_files, "n_ranks_read": n_read,
            "rank_affinity": ranks, "affinity_union": union,
            "cpuset_registered": CPUSET_REGISTERED,
            "affinity_inside_cpuset": inside,
            "all_ranks_on_distinct_single_cores": distinct,
            "COLLISION_all_ranks_share_a_core": collided,
            "delivered": delivered_rows,
            "n_arms_with_delivered_measurement": n_delivered,
            "delivered_floor": DELIVERED_CORES_FLOOR,
            "arms_below_floor": [d["arm"] for d in starved],
            "pass": bool(inside and not collided and distinct
                         and not starved and mpi_arms)}


# ------------------------------------------------------------------ ledger
LEDGER_RE = re.compile(
    r"ARM=(?P<ARM>\S+)\s+ROW=(?P<ROW>\S+)\s+IMG=(?P<IMG>\S+)\s+"
    r"DIGEST=(?P<DIGEST>\S+)\s+rc=(?P<rc>-?\d+)\s+wall_s=(?P<wall_s>\d+)\s+"
    r"ranks=(?P<ranks>\d+)\s+core_min=(?P<core_min>[\d.]+)\s+"
    r"cap_core_min=(?P<cap>[\d.]+)\s+enforced_wall_s=(?P<ewall>\d+)\s+"
    r"enforced_core_min=(?P<ecore>[\d.]+)\s+memory=(?P<mem>\S+)\s+"
    r"inspect\(exit,oomkilled\)=\[(?P<inspect>[^\]]*)\]\s+"
    r"memavail_pre_GiB=(?P<mempre>[\d.]+)\s+memavail_post_GiB=(?P<mempost>[\d.]+)\s+"
    r"cpuset=(?P<cpuset>\S+)\s+delivered_cores_mean=\[(?P<delivered>[^\]]*)\]\s+"
    r"siblings_pre=\[(?P<sibpre>[^\]]*)\]\s+siblings_post=\[(?P<sibpost>[^\]]*)\]")


def read_ledger(path):
    if not os.path.isfile(path):
        refuse("ledger", {"absent": path})
    rows = []
    for line in open(path, errors="replace"):
        m = LEDGER_RE.search(line)
        if not m:
            continue
        g = m.groupdict()
        parts = g["inspect"].split()
        rows.append({"ARM": g["ARM"], "ROW": g["ROW"], "IMG": g["IMG"],
                     "DIGEST": g["DIGEST"], "rc": int(g["rc"]),
                     "wall_s": int(g["wall_s"]), "ranks": int(g["ranks"]),
                     "core_min": float(g["core_min"]),
                     "cap_core_min": float(g["cap"]),
                     "enforced_core_min": float(g["ecore"]),
                     "memory": g["mem"],
                     "inspect_exit": (parts[0] if parts else None),
                     "oomkilled": (parts[1] if len(parts) > 1 else None),
                     "memavail_pre_GiB": float(g["mempre"]),
                     "memavail_post_GiB": float(g["mempost"]),
                     "cpuset": g["cpuset"], "delivered": g["delivered"],
                     "siblings_pre": g["sibpre"], "siblings_post": g["sibpost"]})
    if not rows:
        refuse("ledger", {"no_rows_parsed": path,
                          "note": "a ledger with zero parsed rows is a parser "
                                  "failure, not a costless run"})
    return rows


def g_caps(ledger_rows):
    """G10.  The enforced cap must EQUAL the registered cap, per arm, read back
    from the ledger the launcher wrote -- not from the launcher's own claim."""
    rows, n = [], 0
    for r in ledger_rows:
        reg = CAPS.get(r["ARM"])
        if reg is None:
            refuse("G10", {"unregistered_arm_in_ledger": r["ARM"]})
        rows.append({"arm": r["ARM"], "registered": reg,
                     "ledger_cap": r["cap_core_min"],
                     "enforced": r["enforced_core_min"],
                     "actual": r["core_min"],
                     "cap_equals_registered": bool(
                         abs(r["cap_core_min"] - reg) < 1e-9
                         and abs(r["enforced_core_min"] - reg) <= 0.02),
                     "within_cap": bool(r["core_min"] <= reg + 1e-9)})
        n += 1
    if n == 0:
        refuse("G10", {"arms_checked": 0})
    total = sum(r["actual"] for r in rows)
    return {"n_arms": n, "rows": rows, "total_core_min": total,
            "item_ceiling": ITEM_CEILING_CORE_MIN,
            "within_item_ceiling": bool(total <= ITEM_CEILING_CORE_MIN),
            "pass": bool(all(r["cap_equals_registered"] and r["within_cap"]
                             for r in rows)
                         and total <= ITEM_CEILING_CORE_MIN)}


def g_toolchain(ledger_rows, work, logs):
    """G9.  DAFOAM_CHARTER §11: the identity is the image hash, never a version
    string.  Also records the IDWarp .so md5 the run actually imported."""
    so = {}
    n_logs = 0
    for lp in logs:
        if not os.path.isfile(lp):
            continue
        n_logs += 1
        for line in open(lp, errors="replace"):
            if "D4_IDWARP_SO_MD5:" in line:
                so.setdefault(os.path.basename(lp),
                              line.split("D4_IDWARP_SO_MD5:")[1].strip())
    if n_logs == 0:
        refuse("G9", {"no_arm_logs_found": logs})
    digests = sorted({r["DIGEST"] for r in ledger_rows})
    rowlabels = sorted({r["ROW"] for r in ledger_rows})
    uniq_so = sorted(set(so.values()))
    return {"n_logs_read": n_logs, "digests": digests, "rows": rowlabels,
            "idwarp_so_md5_by_log": so, "idwarp_so_md5_distinct": uniq_so,
            "single_toolchain": bool(len(digests) == 1 and len(uniq_so) <= 1),
            "pass": bool(len(digests) >= 1 and len(uniq_so) == 1)}


# ======================= D4-DEF-1 REPAIR: A REAL SELFTEST ==================
# PREREGISTRATION.md §9a freezes `d4_grade.py` at md5
# f162ef69a7385e5d0586ef5f27657cbb.  THAT FILE IS NOT EDITED (CLAUDE.md rule
# 6).  This SUPPLEMENT carries its grading body BYTE-FOR-BYTE and repairs one
# defect, named D4-DEF-1 by the dafoam-supervisor:
#
#   in the frozen grader `--selftest` is DECLARED at argparse (line 646) and
#   NEVER READ AGAIN.  The token appears exactly once in the file.  Because
#   --base/--work/--out are required, `--selftest` ALONE fails loudly on
#   missing arguments -- but `--selftest` ALONGSIDE a full invocation parses
#   fine and SILENTLY RUNS A COMPLETE GRADE, exiting clean.  A reader could
#   record "grader selftest passed" when no selftest ever existed.  That is
#   L-302's shape: an instrument that cannot say "I measured nothing".
#
# THE REPAIR DEMONSTRATES, IT DOES NOT ASSERT.  Every unit below builds a
# synthetic case that VIOLATES exactly one gate, then runs THIS FILE'S OWN
# main() AS A SUBPROCESS and reads the verdict back out of the JSON main()
# writes.  The REAL mapping is therefore exercised -- a mirrored copy of the
# mapping would only test the mirror.
#
# Unit CLEAN is the DISCRIMINATION CONTROL: a fully consistent fixture must
# grade all-PASS.  Without it, a mutation unit that "failed" would not
# distinguish a working gate from a broken fixture.
#
# The exit path is DISTINCT AND CANNOT BE CONFUSED WITH A GRADED RUN: the
# selftest writes NO --out file, prints the banner D4_SELFTEST, and exits 0
# (all units did what was wanted) or 3 (one or more did not).  A grading run
# exits 0 with D4_GRADER OK or 2 with D4_GRADER REFUSED.  3 is used by nothing
# else in this file.

_ST_CD0 = 2.9619634e-02
_ST_COMPS = [("shape", 46), ("shape", 18), ("shape", 0),
             ("twist", 0), ("patchV", 1)]
_ST_CPUS = [5, 6, 7, 9]


def _st_w(path, text):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with open(path, "w") as fh:
        fh.write(text)
    return path


def _st_ipopt(o):
    """A synthetic IPOPT output FILE.  Rows are formatted exactly as IPOPT
    writes them so the frozen IPOPT_ROW regex is what parses them."""
    red = 0.05 if o.get("drag_out_of_band") else 0.30
    n = 12
    cdf = _ST_CD0 * (1.0 - red)
    cds = [_ST_CD0 + (cdf - _ST_CD0) * i / (n - 1) for i in range(n)]
    lines = ["List of user-set options:",
             "iter    objective    inf_pr   inf_du lg(mu)  ||d||  lg(rg) "
             "alpha_du alpha_pr  ls"]
    for i, c in enumerate(cds):
        lines.append("  %2d  %.7e 4.16e-08 8.10e-03  -5.1 2.83e-01    -  "
                     "9.99e-01 1.00e+00h  1" % (i, c))
    if o.get("converged"):
        lines += ["", "Number of Iterations....: %d" % (n - 1), "",
                  "EXIT: Optimal Solution Found."]
    return "\n".join(lines) + "\n", cds


def _st_hist(o, cds):
    n = len(cds)
    cls = [0.5 + 1.0e-6] * n
    if o.get("cl_bad"):
        cls[3] = 0.5 + 1.0e-3          # beyond band A (5.0e-4)
    if o.get("cl_final_bad"):
        cls[-1] = 0.5 + 1.0e-4         # inside A, beyond B (1.0e-5)
    if o.get("cl_empty"):
        cls = []                       # the D3 defect: present-but-empty
    return {"CD": list(cds), "CL": cls, "_n_major_rows": n,
            "_key_CD": "scenario1.aero_post.functionals.CD",
            "_key_CL": "scenario1.aero_post.functionals.CL"}


def _st_fd(o):
    """A synthetic endpoint FD table that GRADES CLEAN: per-component relative
    error 1.0 % (band D is 5.0 %), plateau 1.0 % (tolerance 10 %), no sign
    flips.  The five components are the registered set in registered order."""
    rows = []
    for dv, idx in _ST_COMPS:
        d_hi = 1.0e-4
        d_lo = 1.0e-4 * 1.01
        j = 1.0e-4 * 1.01
        rows.append({"dv": dv, "idx": idx, "status": "PLANNED",
                     "s_lo": 1.0e-3, "s_hi": 3.0e-3,
                     "J_adj": repr(j), "C_lo": 50.0, "C_hi": 150.0,
                     "fd": {"s_lo": {"step": 1.0e-3, "d": repr(d_lo),
                                     "ok": True},
                            "s_hi": {"step": 3.0e-3, "d": repr(d_hi),
                                     "ok": True}}})
    return {"eta_used": repr(1.0e-9), "eta_raw": repr(1.0e-9),
            "eta_floored": False, "rows": rows, "n_rows": len(rows),
            "components_requested": [[d, i] for (d, i) in _ST_COMPS],
            "n_components_requested": len(_ST_COMPS),
            "clearance_floor": 5.0, "ratio_min": 2.0,
            "plateau_tol_pct": 10.0, "adjoint": {}}


def _st_ledger(o):
    specs = [("P1", 5.0, 0.333, "4g", "NOT_MEASURED"),
             ("P2", 55.0, 36.4, "12g", "3.9867 n=36"),
             ("O", 620.0, 600.0, "12g", "3.9900 n=100"),
             ("F", 120.0, 50.0, "12g", "3.9800 n=20")]
    out = []
    for arm, cap, act, mem, deliv in specs:
        if o.get("arm_missing") == arm:
            continue
        enforced = cap
        if o.get("cap_mismatch") == arm:
            enforced = cap * 2.0
        if o.get("over_cap") == arm:
            act = cap + 10.0
        if o.get("delivered_low") == arm:
            deliv = "2.1000 n=20"
        oom = "true" if o.get("oom") == arm else "false"
        out.append(
            "ARM=%s ROW=PATCHED IMG=img:v1 DIGEST=sha256:aaa rc=0 wall_s=100 "
            "ranks=4 core_min=%.3f cap_core_min=%.1f enforced_wall_s=100 "
            "enforced_core_min=%.6f memory=%s "
            "inspect(exit,oomkilled)=[0 %s] memavail_pre_GiB=17.5 "
            "memavail_post_GiB=17.2 cpuset=5,6,7,9 "
            "delivered_cores_mean=[%s] siblings_pre=[] siblings_post=[]"
            % (arm, act, cap, enforced, mem, oom, deliv))
    return "\n".join(out) + "\n"


def _st_fixture(root, **o):
    """Build a complete synthetic D4 case.  With no options it is CONSISTENT
    and must grade all-PASS; each option violates exactly one gate."""
    import time
    base = os.path.join(root, "base")
    work = os.path.join(base, "O")
    p1 = os.path.join(base, "P1")
    for d in (base, work, p1, os.path.join(work, "0"),
              os.path.join(p1, "system")):
        if not os.path.isdir(d):
            os.makedirs(d)

    now = int(time.time())
    datum = now - 1000

    ref = _st_w(os.path.join(work, "0", "U"), "synthetic U\n")
    os.utime(ref, (datum, datum))
    if not o.get("datum_absent"):
        _st_w(os.path.join(work, ".d4_age_datum"), "%d\n" % datum)
    if o.get("age_ref_moved"):
        os.utime(ref, (datum + 5, datum + 5))

    ip_txt, cds = _st_ipopt(o)
    ip = _st_w(os.path.join(work, "opt_IPOPT.txt"), ip_txt)
    _st_w(os.path.join(work, "OptView.hst"), "synthetic history\n")
    _st_w(os.path.join(work, "d4_major_history.json"),
          json.dumps(_st_hist(o, cds)))
    _st_w(os.path.join(work, "d4_fd_endpoint.json"), json.dumps(_st_fd(o)))
    if o.get("age_stale"):
        os.utime(ip, (datum - 10, datum - 10))

    _st_w(os.path.join(base, "ledger.txt"), _st_ledger(o))

    _st_w(os.path.join(base, "arm.log"),
          "D4_IDWARP_SO_MD5: 85f59e87253e0a71a813f64ca6e4c425\n")
    if o.get("so_mismatch"):
        _st_w(os.path.join(base, "arm2.log"),
              "D4_IDWARP_SO_MD5: 0000000000000000000000000000dead\n")

    per = NCELLS // RANKS
    a = dict(("processor%d" % i, per) for i in range(RANKS))
    b = dict(a)
    if o.get("decomp_mismatch"):
        b["processor0"] += 1
        b["processor1"] -= 1
    if o.get("decomp_badcells"):
        a["processor0"] += 7
    _st_w(os.path.join(p1, "d4_decomp_A.json"), json.dumps(a))
    _st_w(os.path.join(p1, "d4_decomp_B.json"), json.dumps(b))
    _st_w(os.path.join(p1, "system", "decomposeParDict"),
          "numberOfSubdomains %d;\nmethod %s;\n" % (RANKS, DECOMP_METHOD))

    n_rank = RANKS - 1 if o.get("placement_short") else RANKS
    for r in range(n_rank):
        if o.get("placement_collide"):
            aff = [_ST_CPUS[0]]
        elif o.get("placement_outside"):
            aff = [1 + r]
        else:
            aff = [_ST_CPUS[r]]
        _st_w(os.path.join(p1, "d4_placement_rank%d.json" % r),
              json.dumps({"rank": r, "affinity": aff}))
    return base, work


def _st_run(root):
    """Run THIS FILE'S OWN main() as a subprocess against the fixture and read
    the verdicts back from the file main() writes.  The real mapping runs."""
    import subprocess
    base = os.path.join(root, "base")
    work = os.path.join(base, "O")
    out = os.path.join(root, "selftest_out.json")
    if os.path.isfile(out):
        os.remove(out)
    p = subprocess.run(
        [sys.executable, os.path.abspath(__file__), "--base", base,
         "--work", work, "--arms", "P1,P2,O,F", "--out", out],
        capture_output=True, text=True)
    doc = {}
    if os.path.isfile(out):
        try:
            doc = json.load(open(out))
        except Exception:                                  # noqa: BLE001
            doc = {}
    return p.returncode, doc


def _st_v(doc, gate):
    return (doc.get("verdicts") or {}).get(gate)


def selftest():
    """Return 0 if every unit did what was wanted, 3 otherwise."""
    import shutil as _sh
    import tempfile

    def all_pass(rc, doc):
        vs = (doc.get("verdicts") or {})
        bad = sorted(k for k, v in vs.items() if v != "PASS")
        return (rc == 0 and vs and not bad,
                {"rc": rc, "non_PASS": bad, "n_gates": len(vs)})

    def refused(rc, doc):
        return (rc == 2 and "REFUSED" in doc,
                {"rc": rc, "refused": str(doc.get("REFUSED"))[:200]})

    def gate_is(gate, want):
        def chk(rc, doc):
            got = _st_v(doc, gate)
            return got == want, {"rc": rc, "gate": gate, "want": want,
                                 "got": got}
        return chk

    def capstop_never_pass(want_g3, want_g4):
        def chk(rc, doc):
            g3, g4 = _st_v(doc, "G3_termination"), _st_v(doc,
                                                         "G4_drag_reduction")
            ok = (g3 == want_g3 and g4 == want_g4
                  and g3 != "PASS" and g4 != "PASS")
            return ok, {"rc": rc, "G3": g3, "G4": g4,
                        "want": [want_g3, want_g4],
                        "NEVER_PASS_holds": bool(g3 != "PASS"
                                                 and g4 != "PASS")}
        return chk

    UNITS = [
        # name                        fixture options                    check
        ("CLEAN-control", dict(converged=True), all_pass),

        ("G3-capstop-in-band", dict(converged=False),
         capstop_never_pass("GATE REACHED", "GATE REACHED")),
        ("G3-capstop-out-of-band",
         dict(converged=False, drag_out_of_band=True),
         capstop_never_pass("NOT A RESULT", "NOT A RESULT")),
        ("G3-capstop-infeasible-CL", dict(converged=False, cl_bad=True),
         capstop_never_pass("NOT A RESULT", "GATE REACHED")),

        ("G2-CL-beyond-band-A", dict(converged=True, cl_bad=True),
         gate_is("G2_cl_feasibility", "GATE FAIL")),
        ("G2-CL-final-beyond-band-B",
         dict(converged=True, cl_final_bad=True),
         gate_is("G2_cl_feasibility", "GATE FAIL")),
        ("G2-CL-present-but-EMPTY", dict(converged=True, cl_empty=True),
         refused),

        ("G1-age-datum-absent", dict(converged=True, datum_absent=True),
         refused),
        ("G1-age-reference-moved", dict(converged=True, age_ref_moved=True),
         refused),
        ("G1-arm-absent-from-ledger", dict(converged=True, arm_missing="F"),
         refused),
        ("G1-stale-artifact-age-guard", dict(converged=True, age_stale=True),
         gate_is("G1_completion_and_age", "NOT A RESULT")),

        ("G8-decomposition-not-identical",
         dict(converged=True, decomp_mismatch=True),
         gate_is("G8_decomposition_determinism", "GATE FAIL")),
        ("G8-cell-total-wrong", dict(converged=True, decomp_badcells=True),
         refused),

        ("G9-two-distinct-IDWarp-so",
         dict(converged=True, so_mismatch=True),
         gate_is("G9_toolchain_identity", "GATE FAIL")),

        ("G10-enforced-cap-not-registered",
         dict(converged=True, cap_mismatch="O"),
         gate_is("G10_cap_discipline", "GATE FAIL")),
        ("G10-actual-over-cap", dict(converged=True, over_cap="O"),
         gate_is("G10_cap_discipline", "GATE FAIL")),

        ("G11-OOMKilled", dict(converged=True, oom="O"),
         gate_is("G11_memory_envelope", "NOT A RESULT")),

        ("G12-short-rank-set", dict(converged=True, placement_short=True),
         refused),
        ("G12-all-ranks-share-a-core",
         dict(converged=True, placement_collide=True),
         gate_is("G12_cpu_placement", "GATE FAIL")),
        ("G12-affinity-outside-cpuset",
         dict(converged=True, placement_outside=True),
         gate_is("G12_cpu_placement", "GATE FAIL")),
        ("G12-delivered-cores-below-floor",
         dict(converged=True, delivered_low="O"),
         gate_is("G12_cpu_placement", "GATE FAIL")),
    ]

    sys.stdout.write("D4_SELFTEST start units=%d  (this is NOT a grade: no "
                     "--out file is written)\n" % len(UNITS))
    results, n_ok = [], 0
    for name, opts, check in UNITS:
        root = tempfile.mkdtemp(prefix="d4st_")
        try:
            _st_fixture(root, **opts)
            rc, doc = _st_run(root)
            ok, detail = check(rc, doc)
        except Exception as exc:                           # noqa: BLE001
            ok, detail = False, {"exception": repr(exc)[:300]}
        finally:
            _sh.rmtree(root, ignore_errors=True)
        n_ok += bool(ok)
        results.append((name, ok, detail))
        sys.stdout.write("  %-34s %s  %s\n"
                         % (name, "ok " if ok else "NOT",
                            json.dumps(detail, sort_keys=True,
                                       default=str)[:190]))

    n = len(UNITS)
    sys.stdout.write("D4_SELFTEST %d/%d PASS\n" % (n_ok, n))
    if n_ok != n:
        for name, ok, detail in results:
            if not ok:
                sys.stdout.write("D4_SELFTEST UNIT DID NOT DO WHAT WAS "
                                 "WANTED: %s %s\n"
                                 % (name, json.dumps(detail, sort_keys=True,
                                                     default=str)[:400]))
        return 3
    sys.stdout.write("D4_SELFTEST_IS_NOT_A_GRADE -- no verdict file written\n")
    return 0



# ------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=False)
    ap.add_argument("--work", required=False)
    ap.add_argument("--arms", default="P1,P2,O,F")
    ap.add_argument("--out", required=False)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    # ---- D4-DEF-1 REPAIR.  In the frozen grader this flag is declared
    # and NEVER READ: passing it beside a full invocation silently ran a
    # COMPLETE GRADE and exited clean.  Here it is WIRED, it returns a
    # DISTINCT exit code (3) that no grading path uses, and it writes NO
    # verdict file -- so a selftest can never be mistaken for a grade.
    if a.selftest:
        sys.exit(selftest())
    for _req in ("base", "work", "out"):
        if getattr(a, _req) is None:
            ap.error("--%s is required for a grading run" % _req)

    verdicts, report = {}, {}
    try:
        ledger_rows = read_ledger(os.path.join(a.base, "ledger.txt"))
        arms = [x for x in a.arms.split(",") if x]
        report["G1_completion"] = g_completion(a.work, ledger_rows, arms)
        datum = report["G1_completion"]["age_datum_epoch"]

        report["G10_caps"] = g_caps(ledger_rows)
        verdicts["G10_cap_discipline"] = ("PASS" if report["G10_caps"]["pass"]
                                          else "GATE FAIL")

        logs = [os.path.join(a.base, f) for f in sorted(os.listdir(a.base))
                if f.endswith(".log")]
        report["G9_toolchain"] = g_toolchain(ledger_rows, a.work, logs)
        verdicts["G9_toolchain_identity"] = (
            "PASS" if report["G9_toolchain"]["pass"] else "GATE FAIL")

        # ---- G12 CPU placement, measured
        report["G12_placement"] = g_placement(
            os.path.join(a.base, "P1"), ledger_rows)
        verdicts["G12_cpu_placement"] = (
            "PASS" if report["G12_placement"]["pass"] else "GATE FAIL")

        # ---- G8 decomposition determinism
        report["G8_decomposition"] = g_decomposition(
            os.path.join(a.base, "P1"))
        verdicts["G8_decomposition_determinism"] = (
            "PASS" if report["G8_decomposition"]["pass"] else "GATE FAIL")

        # ---- G11 memory envelope (DAFOAM_CHARTER §7)
        oom = [r["ARM"] for r in ledger_rows if str(r["oomkilled"]).lower() == "true"]
        report["G11_memory"] = {"arms_oomkilled": oom,
                                "n_arms": len(ledger_rows),
                                "pass": bool(not oom)}
        verdicts["G11_memory_envelope"] = (
            "PASS" if not oom else "NOT A RESULT")

        # ---- the optimisation arm
        ip = read_ipopt(os.path.join(a.work, "opt_IPOPT.txt"))
        report["G3_termination"] = g_termination(ip)
        hist = read_json(os.path.join(a.work, "d4_major_history.json"), "G2")
        report["G2_cl_feasibility"] = g_cl(hist)
        report["G4_drag"] = g_drag(hist, ip)
        report["G1_age"] = g_age(a.work,
                                 ["opt_IPOPT.txt", "OptView.hst",
                                  "d4_major_history.json",
                                  "d4_fd_endpoint.json"], datum)
        verdicts["G1_completion_and_age"] = (
            "PASS" if report["G1_age"]["pass"] else "NOT A RESULT")

        cap_stopped = not report["G3_termination"]["converged"]
        if report["G3_termination"]["converged"]:
            verdicts["G3_termination"] = "PASS"
        elif report["G4_drag"]["in_band"] and report["G2_cl_feasibility"]["pass_per_major"]:
            verdicts["G3_termination"] = "GATE REACHED"
        else:
            verdicts["G3_termination"] = "NOT A RESULT"
        verdicts["G2_cl_feasibility"] = (
            "PASS" if (report["G2_cl_feasibility"]["pass_per_major"]
                       and report["G2_cl_feasibility"]["pass_final"])
            else "GATE FAIL")
        if cap_stopped:
            verdicts["G4_drag_reduction"] = (
                "GATE REACHED" if report["G4_drag"]["in_band"]
                else "NOT A RESULT")
        else:
            verdicts["G4_drag_reduction"] = (
                "PASS" if report["G4_drag"]["in_band"] else "GATE FAIL")

        # ---- G5/G6/G7 the endpoint FD table and its controls
        fd_path = os.path.join(a.work, "d4_fd_endpoint.json")
        ctrl_dir = os.path.join(a.base, "grader_controls")
        report["G7_count_controls"] = count_controls(fd_path, ctrl_dir)
        verdicts["G7_count_refusal_control"] = (
            "PASS" if report["G7_count_controls"]["pass"] else "GATE FAIL")
        report["G6b_negative_control"] = negative_control(fd_path, ctrl_dir)
        verdicts["G6b_negative_control"] = (
            "PASS" if report["G6b_negative_control"]["pass"] else "GATE FAIL")
        report["G6_planted_zero"] = planted_zero_control(fd_path, ctrl_dir)
        verdicts["G6_planted_zero"] = (
            "PASS" if report["G6_planted_zero"]["pass"] else "GATE FAIL")
        fd = read_json(fd_path, "G5")
        report["G5_fd_table"] = g_fd(fd)
        f = report["G5_fd_table"]
        if f["n_graded"] == 0:
            verdicts["G5_endpoint_fd"] = "NOT A RESULT"
        elif (f["aggregate_rel_err_pct"] is not None
              and f["aggregate_rel_err_pct"] <= FD_BAND_PCT_AGGREGATE
              and f["n_sign_flips"] == 0 and f["n_without_plateau"] == 0
              and all(g["in_band"] for g in f["graded"])):
            verdicts["G5_endpoint_fd"] = "PASS"
        else:
            verdicts["G5_endpoint_fd"] = "GATE FAIL"

    except Refuse as exc:
        out = {"REFUSED": str(exc), "verdicts": verdicts, "report": report}
        with open(a.out, "w") as fh:
            json.dump(out, fh, indent=1, sort_keys=True, default=str)
        sys.stdout.write("D4_GRADER REFUSED %s\n" % str(exc)[:600])
        sys.exit(2)

    bad = [v for v in verdicts.values() if v not in VOCAB]
    if bad:
        sys.stderr.write("D4_GRADER vocabulary violation %r\n" % bad)
        sys.exit(2)
    out = {"verdicts": verdicts, "report": report,
           "n_gates": len(verdicts),
           "registered": {"components": COMPONENTS_REGISTERED,
                          "n_components": N_COMPONENTS_REGISTERED,
                          "cl_target": CL_TARGET,
                          "cl_tol_per_major": CL_TOL_PER_MAJOR,
                          "cl_tol_final": CL_TOL_FINAL,
                          "drag_band_pct": list(DRAG_BAND_PCT),
                          "fd_band_pct": FD_BAND_PCT_PER_COMPONENT,
                          "plateau_tol_pct": PLATEAU_TOL_PCT,
                          "caps": CAPS,
                          "item_ceiling_core_min": ITEM_CEILING_CORE_MIN,
                          "decomposition": {"method": DECOMP_METHOD,
                                            "numberOfSubdomains": RANKS},
                          "cpuset": CPUSET_REGISTERED,
                          "delivered_cores_floor": DELIVERED_CORES_FLOOR}}
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)
    sys.stdout.write("D4_GRADER OK gates=%d %s\n"
                     % (len(verdicts), json.dumps(verdicts, sort_keys=True)))


if __name__ == "__main__":
    main()
