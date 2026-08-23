#!/usr/bin/env python3
"""R5C comparator - grades gates G0..G4 of the frozen PREREGISTRATION.md.

Grading path fixed at the pre-registration commit (CLAUDE.md rule 2).  This
file's own sha256 is printed and recorded in RESULTS.md.

ORDER IS REGISTERED (PREREGISTRATION sec. 3.1):
  G0 planted-zero control FIRST.  A zero from a reader not shown able to see a
     non-zero is not evidence; this comparator REFUSES (exit 2) rather than
     degrade.
  G1 identity on the 12 R4-COMPLETE cases (<= 1e-6 rel L2) + G1c switch-active
  G2 W2 byte-identical reproduction, legacy branch (14 of 14 sha256)
  G3 converged-not-clipped, five criteria, on all 27
  G4 completion count on the 15 (PASS >= 13, GATE REACHED 1-12, GATE FAIL 0)

Verdict vocabulary only: PASS / GATE REACHED / GATE FAIL / NOT A RESULT /
BLOCKED / PENDING.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
_CLOSURE = os.path.join(_REPO, "cases", "RANS_LES_closure_models")
sys.path.insert(0, os.path.join(_CLOSURE, "R4_sparta_build"))
sys.path.insert(0, os.path.join(_CLOSURE, "_common"))

import r4_lib as R                     # noqa: E402  (completion rule, unmodified)
import of_read                         # noqa: E402

R4 = "/home/ubuntu/closure-data/r4/frozen"
R5C = "/home/ubuntu/closure-data/r5c/frozen"
LEGACY = "/home/ubuntu/closure-data/r5c/w2_legacy"
W2 = os.path.join(_REPO, "verification", "runs", "W2_sparta_runs")
ART = os.path.join(_HERE, "artefacts")
SCRATCH = "/home/ubuntu/closure-data/r5c/grading_scratch"

# ---- registered thresholds, PREREGISTRATION sec. 3 -----------------------
PLANT = 1.234e-03            # rule 3, the lab's own constant
G1_TOL = 1e-6                # sec. 3 G1
G1_REPORT = (1e-9, 1e-12)    # reported, NOT gated (VERIFICATION sec. 2a)
G2_FIELDS = ("U", "k", "omega", "nut", "bijData", "bijDelta", "kDeficit")
G2_EXPECT = {"ph": ("ph_frozen", "1492"), "cbfs": ("cbfs_frozen", "354")}
G3_MIN_CONVERGED_AT = 100    # sec. 3 G3 (c)
G3_RES_FALL = 1e6            # sec. 3 G3 (d)
G4_N = 13                    # sec. 3 G4
RATE = 0.0513                # $/core-h, reported-by-owner, NOT measured

TARGETS = ("kDeficit", "bijDelta")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def refuse(msg):
    print(f"\nCOMPARATOR REFUSAL: {msg}", file=sys.stderr)
    print("VERDICT: NOT A RESULT", file=sys.stderr)
    sys.exit(2)


# ------------------------------------------------------------------ readers
def rel_l2(a_path, b_path):
    """Relative L2 difference of two OpenFOAM internal fields."""
    a = np.asarray(of_read.read_field(a_path), dtype=float)
    b = np.asarray(of_read.read_field(b_path), dtype=float)
    if a.shape != b.shape:
        raise ValueError(f"shape {a.shape} vs {b.shape}: {a_path} {b_path}")
    den = np.linalg.norm(b.ravel())
    return float(np.linalg.norm((a - b).ravel()) / max(den, 1e-300))


def max_abs_diff(a_path, b_path):
    a = np.asarray(of_read.read_field(a_path), dtype=float)
    b = np.asarray(of_read.read_field(b_path), dtype=float)
    return float(np.max(np.abs(a - b)))


def perturb_one_cell(src, dst, delta):
    """Copy an ascii OpenFOAM scalar field, adding `delta` to cell 0.

    Deliberately edits the BYTES on disk, so the same file exercises both the
    numeric comparator (G0a) and the sha256 comparator (G0b).
    """
    txt = open(src).read()
    m = re.search(r"nonuniform\s+List<scalar>\s*\n?\s*(\d+)\s*\n?\s*\(\s*\n",
                  txt)
    if m is None:
        raise ValueError(f"{src}: no ascii nonuniform scalar list to plant into")
    i = m.end()
    j = txt.index("\n", i)
    val = float(txt[i:j].strip())
    new = repr(val + delta)
    out = txt[:i] + new + txt[j:]
    with open(dst, "w") as fh:
        fh.write(out)
    return val, val + delta


def parse_history(case_dir):
    p = os.path.join(case_dir, "omegaHistory.csv")
    if not os.path.exists(p):
        return None
    rows = []
    with open(p) as fh:
        next(fh)
        for line in fh:
            line = line.strip()
            if not line:
                continue
            f = line.split(",")
            if len(f) != 6:
                continue
            rows.append((int(f[0]), float(f[1]), float(f[2]), float(f[3]),
                         int(f[4]), int(f[5])))
    if not rows:
        return None
    a = np.array(rows, dtype=float)
    return {"iter": a[:, 0].astype(int), "initRes": a[:, 1],
            "maxRelDomega": a[:, 2], "minOmegaPreBound": a[:, 3],
            "nNegOmegaCells": a[:, 4].astype(int),
            "nNegSourceCells": a[:, 5].astype(int)}


def log_facts(case_dir):
    p = os.path.join(case_dir, "log.frozen")
    txt = open(p, errors="replace").read()
    pre = txt[:txt.index("Writing fields")] if "Writing fields" in txt else txt
    m = re.search(r"CONVERGED \(settle criterion\) at iteration (\d+)", txt)
    a = re.search(r"bound events before write = (\d+)", txt)
    r = re.search(r"omegaSourceRepair (true|false)", txt)
    return {
        "bounding_omega_msgs": pre.count("bounding omega"),
        "bound_events": int(a.group(1)) if a else None,
        "converged_at": int(m.group(1)) if m else None,
        "not_converged": "NOT CONVERGED" in txt,
        "repair_flag": (r.group(1) == "true") if r else None,
        "exec_seconds": float(re.findall(r"ExecutionTime = ([0-9.]+) s", txt)[-1])
        if re.findall(r"ExecutionTime = ([0-9.]+) s", txt) else None,
    }


def grade_g3(case_dir, hist=None, facts=None):
    """G3 (a)-(e).  Returns (converged: bool, detail: dict)."""
    facts = facts if facts is not None else log_facts(case_dir)
    hist = hist if hist is not None else parse_history(case_dir)
    d = {"a_bound_events": facts["bound_events"],
         "a_bounding_msgs": facts["bounding_omega_msgs"],
         "converged_at": facts["converged_at"]}

    a_ok = (facts["bound_events"] == 0) and (facts["bounding_omega_msgs"] == 0)

    # (b) min(omega) over the WRITTEN field, from disk
    lt = R.latest_time(case_dir)
    b_ok, minom = False, None
    op = os.path.join(case_dir, lt, "omega")
    if os.path.exists(op):
        minom = float(np.min(np.asarray(of_read.read_field(op), dtype=float)))
        b_ok = minom > 0.0
    d["b_min_omega_written"] = minom

    ca = facts["converged_at"]
    c_ok = (ca is not None) and (ca >= G3_MIN_CONVERGED_AT)

    d_ok, fall, e_ok, nzero = False, None, False, None
    if hist is not None and ca is not None:
        i1 = hist["initRes"][0] if len(hist["initRes"]) else None
        sel = hist["iter"] == ca
        ic = hist["initRes"][sel][0] if sel.any() else None
        if i1 is not None and ic is not None and ic > 0:
            fall = float(i1 / ic)
            d_ok = fall >= G3_RES_FALL
        win = hist["iter"] <= max(ca - 50, 0)
        nzero = int(np.sum(hist["maxRelDomega"][win] == 0.0))
        e_ok = (nzero == 0) and bool(win.any())
    d["d_res_fall"] = fall
    d["e_zero_domega_before_window"] = nzero
    d["pass"] = {"a": a_ok, "b": b_ok, "c": c_ok, "d": d_ok, "e": e_ok}
    return bool(a_ok and b_ok and c_ok and d_ok and e_ok), d


# ------------------------------------------------------------------ G0
def gate_g0():
    """Planted-zero control.  Runs FIRST.  Refuses rather than degrades."""
    os.makedirs(SCRATCH, exist_ok=True)
    out = {}

    # a deterministic choice: the alphabetically first R4-COMPLETE case
    inv = json.load(open(os.path.join(_CLOSURE, "R4_sparta_build", "artefacts",
                                      "frozen_inventory.json")))["inventory"]
    case = sorted(c["case"] for c in inv if c["complete"])[0]
    cdir = os.path.join(R5C, case)
    lt = R.latest_time(cdir)
    src = os.path.join(cdir, lt, "kDeficit")
    dst = os.path.join(SCRATCH, f"kDeficit_planted_{case}")
    old, new = perturb_one_cell(src, dst, PLANT)

    # G0a - numeric comparator must see the plant, within 1% of the analytic
    f = np.asarray(of_read.read_field(src), dtype=float)
    expect = PLANT / np.linalg.norm(f.ravel())
    got = rel_l2(dst, src)
    err = abs(got - expect) / expect if expect > 0 else float("inf")
    out["G0a"] = {"case": case, "field": "kDeficit", "cell": 0,
                  "plant": PLANT, "cell_before": old, "cell_after": new,
                  "expected_rel_l2": expect, "measured_rel_l2": got,
                  "rel_error": err, "pass": bool(got > 0 and err <= 0.01)}
    if not out["G0a"]["pass"]:
        refuse(f"G0a: the numeric comparator could not see a planted "
               f"{PLANT} (expected rel L2 {expect:.6e}, measured {got:.6e})")

    # G0b - byte comparator must report DIFFERS on the same file
    same = sha256_file(dst) == sha256_file(src)
    out["G0b"] = {"sha_planted": sha256_file(dst), "sha_original":
                  sha256_file(src), "reports_differs": (not same),
                  "pass": (not same)}
    if same:
        refuse("G0b: the sha256 comparator reported IDENTICAL for a file with "
               "a planted perturbation")

    # G0c - the G3 grader must refuse a clipped history and a bounded log,
    #       on each signature INDEPENDENTLY
    sub = {}
    for tag, mk in (("clipped_history", "e"), ("bounded_log", "a")):
        d = os.path.join(SCRATCH, f"g0c_{tag}")
        if os.path.isdir(d):
            shutil.rmtree(d)
        os.makedirs(os.path.join(d, "100"))
        # a synthetic run that is CONVERGED on every other criterion
        with open(os.path.join(d, "omegaHistory.csv"), "w") as fh:
            fh.write("iter,initRes,maxRelDomega,minOmegaPreBound,"
                     "nNegOmegaCells,nNegSourceCells\n")
            for i in range(1, 101):
                res = 1.0e-1 * (10.0 ** (-8.0 * i / 100.0))
                dom = 0.0 if (mk == "e" and i == 7) else 1.0e-3
                fh.write(f"{i},{res},{dom},1.0,0,5\n")
        nb = 3 if mk == "a" else 0
        bmsg = ("bounding omega, min: -1 max: 1 average: -0.5\n" * nb)
        with open(os.path.join(d, "log.frozen"), "w") as fh:
            fh.write(bmsg)
            fh.write("CONVERGED (settle criterion) at iteration 100; "
                     "running 20 verification iterations\n")
            fh.write(f"R5C omega clip audit: bound events before write = {nb}, "
                     "negative-source cells on the last iteration = 5, "
                     "omegaSourceRepair = true\n")
            fh.write("Writing fields at iteration 120\n")
            fh.write("ExecutionTime = 1.0 s  ClockTime = 1 s\nEnd\n")
        # a positive omega field so criterion (b) cannot be what fails
        with open(os.path.join(d, "100", "omega"), "w") as fh:
            fh.write("FoamFile\n{\n version 2.0;\n format ascii;\n"
                     " class volScalarField;\n object omega;\n}\n"
                     "internalField   nonuniform List<scalar>\n3\n(\n"
                     "1.0\n2.0\n3.0\n)\n;\n")
        ok, det = grade_g3(d)
        sub[tag] = {"graded_converged": ok, "detail": det,
                    "pass": (not ok)}
        if ok:
            refuse(f"G0c/{tag}: the G3 grader returned CONVERGED for a "
                   f"synthetically {tag.replace('_', ' ')} run")
    out["G0c"] = sub
    out["pass"] = True
    return out


# ------------------------------------------------------------------ G1
def gate_g1(inv_complete):
    rows, worst = [], 0.0
    for case in inv_complete:
        a_dir, b_dir = os.path.join(R5C, case), os.path.join(R4, case)
        at, bt = R.latest_time(a_dir), R.latest_time(b_dir)
        r = {"case": case, "r5c_time": at, "r4_time": bt}
        for f in TARGETS:
            e = rel_l2(os.path.join(a_dir, at, f), os.path.join(b_dir, bt, f))
            r[f"rel_l2_{f}"] = e
            r[f"max_abs_{f}"] = max_abs_diff(os.path.join(a_dir, at, f),
                                             os.path.join(b_dir, bt, f))
            worst = max(worst, e)
        r["max_rel_l2"] = max(r[f"rel_l2_{f}"] for f in TARGETS)
        rows.append(r)
    return {"threshold": G1_TOL, "worst_rel_l2": worst,
            "reported_only": {f"{t:g}": bool(worst <= t) for t in G1_REPORT},
            "rows": rows, "pass": bool(worst <= G1_TOL)}


def gate_g1c(all_cases):
    rows = []
    for case in all_cases:
        d = os.path.join(R5C, case)
        f, h = log_facts(d), parse_history(d)
        fired = int(h["nNegSourceCells"].max()) if h is not None else 0
        rows.append({"case": case, "repair_flag": f["repair_flag"],
                     "max_nNegSourceCells": fired,
                     "pass": bool(f["repair_flag"] and fired > 0)})
    return {"rows": rows, "pass": all(r["pass"] for r in rows)}


# ------------------------------------------------------------------ G2
def gate_g2():
    rows, ok = [], True
    for tag, (rec, it) in G2_EXPECT.items():
        d = os.path.join(LEGACY, tag)
        f = log_facts(d)
        lt = R.latest_time(d)
        it_ok = (str(lt) == it)
        ok = ok and it_ok
        for fld in G2_FIELDS:
            a = os.path.join(d, lt, fld)
            b = os.path.join(W2, rec, it, fld)
            sa = sha256_file(a) if os.path.exists(a) else None
            sb = sha256_file(b) if os.path.exists(b) else None
            m = (sa is not None and sa == sb)
            ok = ok and m
            rows.append({"case": tag, "field": fld, "record_time": it,
                         "run_time": lt, "sha_run": sa, "sha_record": sb,
                         "match": m})
        rows.append({"case": tag, "field": "__settle_iteration__",
                     "record_time": it, "run_time": lt,
                     "converged_at": f["converged_at"], "match": it_ok})
    return {"rows": rows, "n_match": sum(1 for r in rows
                                         if r["field"] != "__settle_iteration__"
                                         and r["match"]),
            "n_total": len(G2_FIELDS) * 2, "pass": bool(ok)}


# ------------------------------------------------------------------ main
def main():
    print(f"comparator sha256: {sha256_file(os.path.abspath(__file__))}")
    print(f"pre-registration sha256: "
          f"{sha256_file(os.path.join(_HERE, 'PREREGISTRATION.md'))}\n")

    inv = json.load(open(os.path.join(_CLOSURE, "R4_sparta_build", "artefacts",
                                      "frozen_inventory.json")))["inventory"]
    r4_complete = [c["case"] for c in inv if c["complete"]]
    r4_incomplete = [c["case"] for c in inv if not c["complete"]]
    fam = {c["case"]: c["family"] for c in inv}
    assert len(r4_complete) == 12 and len(r4_incomplete) == 15
    all_cases = [c["case"] for c in inv]

    print("=== G0  planted-zero control (runs FIRST; refuses rather than "
          "degrades) ===")
    g0 = gate_g0()
    print(f"  G0a numeric : expected {g0['G0a']['expected_rel_l2']:.6e}  "
          f"measured {g0['G0a']['measured_rel_l2']:.6e}  "
          f"rel err {g0['G0a']['rel_error']:.3e}  PASS")
    print(f"  G0b byte    : reports DIFFERS  PASS")
    print(f"  G0c history : clipped-history and bounded-log both graded "
          f"NOT CONVERGED  PASS\n")

    # per-case table
    table = []
    for case in all_cases:
        d = os.path.join(R5C, case)
        f = log_facts(d)
        h = parse_history(d)
        comp, why, info = R.frozen_complete(d)
        conv, det = grade_g3(d, hist=h, facts=f)
        ws = None
        wsp = os.path.join(d, "wall_seconds")
        if os.path.exists(wsp):
            ws = float(open(wsp).read().strip())
        table.append({
            "case": case, "family": fam[case],
            "r4_complete": case in r4_complete,
            "complete": bool(comp), "complete_reason": why,
            "converged_g3": bool(conv), "g3": det,
            "converged_at": f["converged_at"],
            "bound_events": f["bound_events"],
            "clipped": bool(f["bound_events"]),
            "exec_seconds": f["exec_seconds"], "wall_seconds": ws,
            "max_nNegSourceCells": int(h["nNegSourceCells"].max())
            if h is not None else None,
        })

    print("=== G1  identity gate on the 12 R4-COMPLETE cases ===")
    g1 = gate_g1(r4_complete)
    for r in g1["rows"]:
        print(f"  {r['case']:22s} kDeficit {r['rel_l2_kDeficit']:.4e}  "
              f"bijDelta {r['rel_l2_bijDelta']:.4e}")
    print(f"  worst {g1['worst_rel_l2']:.6e} against threshold {G1_TOL:g}  "
          f"-> {'PASS' if g1['pass'] else 'GATE FAIL'}")
    g1c = gate_g1c(all_cases)
    print(f"  G1c switch-active on all 27 -> "
          f"{'PASS' if g1c['pass'] else 'NOT A RESULT'}\n")

    print("=== G2  W2 byte-identical reproduction (legacy branch) ===")
    g2 = gate_g2()
    print(f"  {g2['n_match']} of {g2['n_total']} sha256 field matches; "
          f"settle iterations "
          + ", ".join(f"{r['case']}={r['run_time']}(record {r['record_time']})"
                      for r in g2["rows"]
                      if r["field"] == "__settle_iteration__")
          + f"  -> {'PASS' if g2['pass'] else 'GATE FAIL'}\n")

    print("=== G3  converged, not clipped (all 27) ===")
    n_conv = sum(1 for t in table if t["converged_g3"])
    print(f"  {n_conv} of 27 CONVERGED under (a)-(e)\n")

    print("=== G4  completion count on the 15 ===")
    m_rows = [t for t in table if not t["r4_complete"]]
    M = sum(1 for t in m_rows if t["complete"] and t["converged_g3"])
    if M >= G4_N:
        g4v = "PASS"
    elif M >= 1:
        g4v = "GATE REACHED"
    else:
        g4v = "GATE FAIL"
    print(f"  M = {M} of 15 (threshold PASS at >= {G4_N})  -> {g4v}\n")

    # the 12 must also stay COMPLETE and CONVERGED (part of G1)
    twelve_ok = all(t["complete"] and t["converged_g3"]
                    for t in table if t["r4_complete"])
    g1_full = g1["pass"] and g1c["pass"] and twelve_ok

    # cost actual
    exec_s = sum(t["exec_seconds"] or 0.0 for t in table)
    leg = {}
    for tag in G2_EXPECT:
        leg[tag] = log_facts(os.path.join(LEGACY, tag))["exec_seconds"]
    total_core_h = (exec_s + sum(leg.values())) / 3600.0
    cost = {"exec_seconds_27": exec_s,
            "exec_seconds_legacy": leg,
            "core_h_solver": total_core_h,
            "cost_usd_solver": total_core_h * RATE,
            "registered_estimate_core_h": 0.210,
            "registered_cap_core_h": 1.0,
            "rate_usd_per_core_h": RATE,
            "cost_basis": "reported-by-owner, NOT measured "
                          "(COMPUTE_BUDGET_CHARTER sec.5, CLAUDE.md rule 12); "
                          "core-hours are ExecutionTime x 1 rank / 3600"}

    # lane verdict, in the registered order
    if not g2["pass"] or not g1_full:
        verdict = "GATE FAIL"
    else:
        verdict = g4v
    print(f"LANE VERDICT: {verdict}")
    print(f"cost actual: {total_core_h:.4f} core-h = "
          f"${total_core_h * RATE:.4f} against a registered 0.210 core-h "
          f"($0.0108) and a 1.0 core-h cap")

    out = {"verdict": verdict, "G0": g0, "G1": g1, "G1c": g1c, "G2": g2,
           "G4": {"M": M, "threshold": G4_N, "verdict": g4v},
           "twelve_still_complete_and_converged": twelve_ok,
           "n_converged_of_27": n_conv, "table": table, "cost": cost,
           "comparator_sha256": sha256_file(os.path.abspath(__file__)),
           "prereg_sha256": sha256_file(os.path.join(_HERE,
                                                     "PREREGISTRATION.md"))}
    os.makedirs(ART, exist_ok=True)
    with open(os.path.join(ART, "r5c_grading.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=str)
    print(f"\nwrote {os.path.join(ART, 'r5c_grading.json')}")


if __name__ == "__main__":
    main()
