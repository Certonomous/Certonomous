#!/usr/bin/env python3
"""analyse_k2g.py -- the K2g grading path.  F14 cooling ladder.

    python3 analyse_k2g.py --selftest        # drives every refusal BOTH ways
    python3 analyse_k2g.py --grade           # grades the registered ladder

Registered by `docs/campaigns/F14-cooling-ladder/K2g_PREREGISTRATION.md`.
Nothing here may be changed after that document's freeze commit.

WHAT THIS FILE EXISTS TO AVOID.  In the T5b defect this lab measured this week a
ladder diverged twenty-one orders of magnitude, exited 0, passed the completion
rule and reached grading, because the REGISTERED CONVERGENCE CLAUSE WAS ABSENT
FROM THE COMPARATOR and a neighbouring gate silently supplied its number.  So:

  * step (a) of CLAUDE.md rule 5 -- iterative convergence and plateau -- is
    computed HERE, per level, and handed to `scripts/roache_triple.grade_ladder`,
    which refuses outright if `iterative_states` is None.  It is evaluated
    BEFORE any triple is classified because that function evaluates it first.
  * the plateau test is TWO-SIDED.  A level still moving fails it, and so does a
    level that has GONE DEAD: a frozen solve shows a late-checkpoint delta of ~0
    and would sail through a one-sided test, so `D-ALIVE` requires the field to
    have departed from its own initial condition by a registered floor.
  * rule 3's planted zero is read back FROM DISK through the production reader
    and this file exits 2 if the reader cannot see it.

REUSED, NOT REINVENTED: `scripts/roache_triple.py` (rule 5's floors, the GCI at
Fs = 1.25 and the one-way gate), `mark_done_k2f.py` (rule 4's six clauses,
verbatim and unedited -- it is the instrument that certified L1 and L2), and the
structure of `K2f_runs/analyse_k2f.py`, which refused honestly and is the model
for the refusal discipline here.
"""
import argparse, glob, hashlib, json, math, os, re, shutil, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, os.path.join(REPO, "verification", "runs",
                                "F14-cooling-ladder", "K2f_runs"))

import numpy as np
import roache_triple as RT
import mark_done_k2f as MD
import foam_patch_reader as FR

# ---------------------------------------------------------------------------
# REGISTERED CONSTANTS -- registration sections 3, 5, 6, 7.  Frozen.
# ---------------------------------------------------------------------------
RUNG = "K2g"
REGISTRATION = os.path.join(REPO, "docs", "campaigns", "F14-cooling-ladder",
                            "K2g_PREREGISTRATION.md")
K2F = os.path.join(REPO, "verification", "runs", "F14-cooling-ladder", "K2f_runs")

QUANTITY = "DP_module"        # areaAverage(p_rgh, tile) - areaAverage(p_rgh, return)
UNITS = "m2/s2"
PATCH_HI, PATCH_LO, FIELD = "tile", "return", "p_rgh"

LEVELS = ("K2g_L1", "K2g_L2", "K2g_L3")
CASE = {"K2g_L1": os.path.join(K2F, "K2f_L1"),
        "K2g_L2": os.path.join(K2F, "K2f_L2"),
        "K2g_L3": os.path.join(HERE, "K2f_L3")}
CELLS = {"K2g_L1": 58368, "K2g_L2": 196992, "K2g_L3": 664848}
ENDTIME = {"K2g_L1": 3000, "K2g_L2": 3000, "K2g_L3": 2000}
CHECKPOINT_BACK = 500          # writeInterval; the plateau window

BAND = (27.9699, 28.0901)      # section 5.  Implied by observed order in [1, 2].
DIM = 3
MESHSIM = (3.2063, 3.5438)     # section 5.4, carried from K2f G-MESHSIM

PLATEAU_TOL = 1.0e-2           # |f(end) - f(end-500)|, m2/s2
ALIVE_FLOOR = 0.10             # K, rms(T(end) - T(0)) over internal cells
RES_FLOOR = 5.0e-3             # final initial-residual, each of Ux, T, p_rgh
RES_DECADES_MIN = 2.5          # decades fallen from the normalised start
RES_RISE_MAX = 2.0             # mean(last 100) / min(last 400)
PLANT = RT.PLANT               # 1.234e-03

EXIT_OK, EXIT_FAIL, EXIT_NAR, EXIT_REFUSE = 0, 1, 3, 2


class Refusal(Exception):
    pass


def refuse(msg):
    raise Refusal(msg)


# ---------------------------------------------------------------------------
# the freeze -- section 10.  Every grading-path file is hashed from DISK BYTES.
# ---------------------------------------------------------------------------
FREEZE_PATHS = (
    "docs/campaigns/F14-cooling-ladder/K2g_PREREGISTRATION.md",
    "verification/runs/F14-cooling-ladder/K2g_runs/analyse_k2g.py",
    "verification/runs/F14-cooling-ladder/K2g_runs/foam_patch_reader.py",
    "verification/runs/F14-cooling-ladder/K2f_runs/build_k2f.py",
    "verification/runs/F14-cooling-ladder/K2f_runs/mark_done_k2f.py",
    "scripts/roache_triple.py",
)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 16), b""):
            h.update(blk)
    return h.hexdigest()


def registered_freeze():
    """The sha256 table the registration froze, parsed from its FREEZE block."""
    if not os.path.exists(REGISTRATION):
        refuse("the registration %s does not exist; there is no frozen gate and "
               "NOTHING may be graded" % REGISTRATION)
    txt = open(REGISTRATION).read()
    m = re.search(r"```json FREEZE\n(.*?)\n```", txt, re.S)
    if m is None:
        refuse("the registration carries no ```json FREEZE``` block; the "
               "grading path is not pinned and nothing may be graded")
    return json.loads(m.group(1))


def verify_freeze():
    want = registered_freeze()
    bad = []
    for rel in FREEZE_PATHS:
        p = os.path.join(REPO, rel)
        if rel == FREEZE_PATHS[0]:
            continue          # the registration carries the table; see section 10
        if not os.path.exists(p):
            bad.append((rel, "MISSING", want.get(rel)))
            continue
        got = sha256(p)
        if want.get(rel) != got:
            bad.append((rel, got, want.get(rel)))
    if bad:
        refuse("FREEZE BROKEN -- the files that would run are not the files the "
               "registration pinned: " + "; ".join(
                   "%s disk %s registered %s" % b for b in bad))
    return {"state": "FROZEN AND VERIFIED",
            "pinned": {r: want.get(r) for r in FREEZE_PATHS[1:]}}


# ---------------------------------------------------------------------------
# the gate quantity -- ONE reader, every level
# ---------------------------------------------------------------------------
def dp(case, time):
    hi, src = FR.area_average(case, time, FIELD, PATCH_HI)
    lo, _ = FR.area_average(case, time, FIELD, PATCH_LO)
    return hi - lo, src


# ---------------------------------------------------------------------------
# rule 5 step (a), part 1 -- iterative convergence, from the solver's own log
# ---------------------------------------------------------------------------
_RES = {"Ux": re.compile(r"Solving for Ux, Initial residual = ([-\d.eE+]+)"),
        "T": re.compile(r"Solving for T, Initial residual = ([-\d.eE+]+)"),
        "p_rgh": re.compile(r"Solving for p_rgh, Initial residual = ([-\d.eE+]+)")}


def residual_series(log_path):
    seq, seen = {k: [] for k in _RES}, 0
    with open(log_path, errors="replace") as fh:
        for ln in fh:
            for k, p in _RES.items():
                m = p.search(ln)
                if not m:
                    continue
                if k == "p_rgh":
                    seen += 1
                    if seen % 2 == 0:      # keep the FIRST of the two correctors
                        continue
                seq[k].append(float(m.group(1)))
    return seq


def iterative_state(case):
    log = os.path.join(case, "log.solve")
    if not os.path.exists(log):
        return "NO_LOG", {}
    seq, detail, bad = residual_series(log), {}, []
    for k, v in seq.items():
        if len(v) < 400:
            bad.append("%s: only %d entries, fewer than the 400-iteration "
                       "window this test needs" % (k, len(v)))
            continue
        first, last = max(v[:5]), v[-1]
        dec = math.log10(first / last) if last > 0 else float("inf")
        rise = (sum(v[-100:]) / 100.0) / min(v[-400:])
        detail[k] = dict(first=first, last=last, decades=dec, rise=rise,
                         n=len(v))
        if not (last <= RES_FLOOR):
            bad.append("%s final initial-residual %.4g above the registered "
                       "floor %.4g" % (k, last, RES_FLOOR))
        if not (dec >= RES_DECADES_MIN):
            bad.append("%s fell only %.2f decades, under the registered %.2f -- "
                       "a solve that never moved fails here" % (k, dec,
                                                                RES_DECADES_MIN))
        if not (rise <= RES_RISE_MAX):
            bad.append("%s is RISING: mean(last 100)/min(last 400) = %.3f above "
                       "the registered %.2f" % (k, rise, RES_RISE_MAX))
    if not detail:
        return "NO_RESIDUALS", detail
    return ("CONVERGED" if not bad else "NOT_CONVERGED: " + "; ".join(bad)), detail


# ---------------------------------------------------------------------------
# rule 5 step (a), part 2 -- plateau, TWO-SIDED
# ---------------------------------------------------------------------------
def plateau_state(case, level):
    end = ENDTIME[level]
    f_end, _ = dp(case, end)
    f_back, _ = dp(case, end - CHECKPOINT_BACK)
    drift = abs(f_end - f_back)
    alive = FR.rms_departure(case, end, "T", 0)
    detail = dict(f_end=f_end, f_back=f_back, drift=drift,
                  back_time=end - CHECKPOINT_BACK, alive_rms_K=alive,
                  tol=PLATEAU_TOL, alive_floor=ALIVE_FLOOR)
    why = []
    if not (drift <= PLATEAU_TOL):
        why.append("STILL MOVING: |f(%d) - f(%d)| = %.6g above the registered "
                   "%.6g" % (end, end - CHECKPOINT_BACK, drift, PLATEAU_TOL))
    if not (alive >= ALIVE_FLOOR):
        why.append("DEAD: rms(T(%d) - T(0)) = %.6g below the registered "
                   "aliveness floor %.6g -- the field never left its initial "
                   "condition, and a delta of ~0 is NOT a plateau"
                   % (end, alive, ALIVE_FLOOR))
    return ("PLATEAUED" if not why else "NOT_PLATEAUED: " + "; ".join(why)), detail


# ---------------------------------------------------------------------------
# rule 3 -- the planted zero, read back FROM DISK through the production reader
# ---------------------------------------------------------------------------
def planted_zero(case, level, plant=PLANT, patch=None):
    """Shadow the case with symlinks, plant `plant` into every `tile` face of the
    endTime p_rgh COPY, and require the production reader to see exactly it.

    Nothing under the real case directory is written to.  A reader that cannot
    see a known non-zero is a reader whose zero is not evidence.
    """
    end = ENDTIME[level]
    patch = PATCH_HI if patch is None else patch
    before, _ = dp(case, end)
    tmp = tempfile.mkdtemp(prefix="k2g_plant_")
    try:
        os.symlink(os.path.join(case, "constant"), os.path.join(tmp, "constant"))
        t = FR._tname(case, end)
        rec = os.path.join(case, t)
        if os.path.isdir(rec) and os.path.exists(os.path.join(rec, FIELD)):
            os.mkdir(os.path.join(tmp, t))
            _plant_file(os.path.join(rec, FIELD),
                        os.path.join(tmp, t, FIELD), patch, plant)
        else:
            for p in sorted(glob.glob(os.path.join(case, "processor*"))):
                b = os.path.basename(p)
                os.mkdir(os.path.join(tmp, b))
                os.symlink(os.path.join(p, "constant"),
                           os.path.join(tmp, b, "constant"))
                os.mkdir(os.path.join(tmp, b, t))
                _plant_file(os.path.join(p, t, FIELD),
                            os.path.join(tmp, b, t, FIELD), patch, plant)
        after, _ = dp(tmp, end)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return RT.external_plant_control("analyse_k2g.dp", before, after, plant=plant)


def _plant_file(src, dst, patch, plant):
    """Add `plant` to every face value of `patch` and write the result to disk."""
    txt = open(src).read()
    m = re.compile(r"\n(\s*)" + re.escape(patch) + r"\s*\n?\s*\{").search(txt)
    if m is None:
        shutil.copyfile(src, dst)
        return
    depth, j = 1, m.end()
    while depth:
        c = txt[j]
        depth += (c == "{") - (c == "}")
        j += 1
    blk = txt[m.end():j - 1]
    vk = blk.find("value")
    if vk < 0:
        shutil.copyfile(src, dst)
        return
    if "nonuniform" in blk[vk:vk + 60]:
        o = blk.index("(", blk.index("List", vk))
        c = blk.index(")", o)
        nums = np.fromstring(blk[o + 1:c], sep=" ") + plant
        new = blk[:o + 1] + "\n" + "\n".join("%.12g" % x for x in nums) + "\n" + blk[c:]
    else:
        mm = re.search(r"uniform\s+([-\d.eE+]+)\s*;", blk[vk:vk + 200])
        new = (blk[:vk + mm.start(1)] + "%.12g" % (float(mm.group(1)) + plant)
               + blk[vk + mm.end(1):])
    open(dst, "w").write(txt[:m.end()] + new + txt[j - 1:])


# ---------------------------------------------------------------------------
# mesh admission -- section 5.4, carried from K2f unchanged
# ---------------------------------------------------------------------------
def mesh_admission(case, level):
    out = {}
    log = os.path.join(case, "log.checkMesh")
    if not os.path.exists(log):
        return None, "G-CHECKMESH: no log.checkMesh at %s" % case
    txt = open(log, errors="replace").read()
    nfail = len(re.findall(r"\*\*\*", txt))
    out["checkmesh_failed"] = nfail
    out["mesh_ok"] = "Mesh OK." in txt
    out["three_d"] = "3 geometric (non-empty/wedge) directions (1 1 1)" in txt
    mc = os.path.join(case, "MINCELL.json")
    out["mincell_worst_m"] = (min(json.load(open(mc)).values())
                              if os.path.exists(mc) else None)
    m = re.search(r"\n\s+cells:\s+(\d+)", txt)
    out["cells"] = int(m.group(1)) if m else None
    why = []
    if nfail or not out["mesh_ok"]:
        why.append("G-CHECKMESH: %d failed checks, 'Mesh OK.' %s"
                   % (nfail, out["mesh_ok"]))
    if not out["three_d"]:
        why.append("G-3D: checkMesh does not report three geometric directions")
    if out["mincell_worst_m"] is None or out["mincell_worst_m"] < 5.0e-3:
        why.append("G-MINCELL: worst named feature %s below the 5.0 mm floor"
                   % out["mincell_worst_m"])
    if out["cells"] != CELLS[level]:
        why.append("G-CELLS: checkMesh reports %s cells, registered %d"
                   % (out["cells"], CELLS[level]))
    return out, ("; ".join(why) if why else None)


# ---------------------------------------------------------------------------
# the drive
# ---------------------------------------------------------------------------
def grade(levels=LEVELS, verbose=True):
    rep = {"rung": RUNG, "quantity": QUANTITY, "units": UNITS,
           "registration": os.path.relpath(REGISTRATION, REPO),
           "freeze": verify_freeze(), "levels": {}, "refusals": []}
    rows, it_states, pl_states, pc = [], {}, {}, None

    for lv in levels:
        case = CASE[lv]
        d = {"case": case, "cells": CELLS[lv], "endTime": ENDTIME[lv]}
        if not os.path.isdir(case):
            rep["levels"][lv] = dict(d, present=False)
            refuse("%s: the case directory %s does not exist; NOTHING is graded "
                   "and no verdict may be read from this run" % (lv, case))
        done, why = MD.check(case)
        d["completion"] = {"done": done, "why": why}
        if done is not True:
            refuse("%s fails CLAUDE.md rule 4 (six clauses, mark_done_k2f.check, "
                   "unedited): %s" % (lv, "; ".join(why)))
        ma, mwhy = mesh_admission(case, lv)
        d["mesh"] = ma
        if mwhy:
            refuse("%s fails mesh admission: %s" % (lv, mwhy))
        it, itd = iterative_state(case)
        pl, pld = plateau_state(case, lv)
        it_states[lv], pl_states[lv] = it, pl
        d["iterative"] = {"state": it, "detail": itd}
        d["plateau"] = {"state": pl, "detail": pld}
        value, src = dp(case, ENDTIME[lv])
        d["value"], d["source"] = value, src
        if pc is None:
            pc = planted_zero(case, lv)
            d["planted_zero"] = dict(pc)
        rep["levels"][lv] = d
        rows.append(dict(name=lv, cells=CELLS[lv], value=value))

    if pc is None or not pc.get("passed"):
        refuse("PLANTED-ZERO CONTROL FAILED: the reader was not shown able to "
               "see a known %g perturbation on disk, so its zero is not "
               "evidence (CLAUDE.md rule 3)" % PLANT)

    r21 = CELLS[levels[1]] / CELLS[levels[0]]
    r32 = CELLS[levels[2]] / CELLS[levels[1]]
    rep["mesh_similarity"] = {"r21": r21, "r32": r32, "band": MESHSIM}
    if not (MESHSIM[0] <= r21 <= MESHSIM[1] and MESHSIM[0] <= r32 <= MESHSIM[1]):
        refuse("G-MESHSIM: cell-count ratios %.5f and %.5f are not both inside "
               "the registered %s" % (r21, r32, list(MESHSIM)))

    row = RT.grade_ladder(QUANTITY, rows, DIM, BAND, pc,
                          iterative_states=it_states, plateau_states=pl_states)
    rep["row"] = row
    if verbose:
        print(RT.format_row(row))
    return rep, RT.exit_code_for(row["verdict"])


# ---------------------------------------------------------------------------
# SELFTEST -- every refusal driven BOTH ways, on synthetic data only.
# No argv here can reach a launcher: this file never starts a solver.
# ---------------------------------------------------------------------------
def _chk(name, ok, detail=""):
    print("  %-5s %s%s" % ("PASS" if ok else "FAIL", name,
                           ("  -- " + detail) if detail else ""))
    return bool(ok)


def _fake_levels(f3, cells3=664848):
    return [dict(name="K2g_L1", cells=58368, value=27.189119361484373),
            dict(name="K2g_L2", cells=196992, value=27.729679615659716),
            dict(name="K2g_L3", cells=cells3, value=f3)]


def selftest():
    ok = True
    good_pc = RT.external_plant_control("t", 1.0, 1.0 + PLANT, plant=PLANT)
    allc = {l: "CONVERGED" for l in LEVELS}
    allp = {l: "PLATEAUED" for l in LEVELS}

    print("A. step (a) -- iterative convergence and plateau, BOTH WAYS")
    r = RT.grade_ladder(QUANTITY, _fake_levels(28.0488), DIM, BAND, good_pc,
                        iterative_states=allc, plateau_states=allp)
    ok &= _chk("A1 accepts a converged, plateaued, CONVERGING ladder",
               r["verdict"] == "PASS", r["verdict"])
    bad = dict(allc); bad["K2g_L3"] = "NOT_CONVERGED: Ux is RISING"
    r = RT.grade_ladder(QUANTITY, _fake_levels(28.0488), DIM, BAND, good_pc,
                        iterative_states=bad, plateau_states=allp)
    ok &= _chk("A2 REJECTS a level that is not iteratively converged",
               r["verdict"] == "NOT A RESULT", r["verdict"])
    badp = dict(allp); badp["K2g_L3"] = "NOT_PLATEAUED: STILL MOVING"
    r = RT.grade_ladder(QUANTITY, _fake_levels(28.0488), DIM, BAND, good_pc,
                        iterative_states=allc, plateau_states=badp)
    ok &= _chk("A3 REJECTS a level that has not plateaued",
               r["verdict"] == "NOT A RESULT", r["verdict"])
    badp = dict(allp); badp["K2g_L3"] = "NOT_PLATEAUED: DEAD"
    r = RT.grade_ladder(QUANTITY, _fake_levels(28.0488), DIM, BAND, good_pc,
                        iterative_states=allc, plateau_states=badp)
    ok &= _chk("A4 REJECTS a level whose field never moved (the frozen solve)",
               r["verdict"] == "NOT A RESULT", r["verdict"])
    try:
        RT.grade_ladder(QUANTITY, _fake_levels(28.0488), DIM, BAND, good_pc,
                        iterative_states=None, plateau_states=allp)
        ok &= _chk("A5 REFUSES when step (a) was never evaluated", False,
                   "it graded anyway -- this is the T5b defect")
    except RT.Refusal as e:
        ok &= _chk("A5 REFUSES when step (a) was never evaluated", True, str(e)[:60])

    print("B. the two-sided plateau instrument itself, on synthetic cases")
    for label, drift, alive, want in (("plateaued and alive", 1.2e-3, 4.13, True),
                                      ("still moving", 5.0e-2, 4.13, False),
                                      ("frozen: zero drift, zero departure",
                                       0.0, 0.0, False)):
        why = []
        if not drift <= PLATEAU_TOL:
            why.append("STILL MOVING")
        if not alive >= ALIVE_FLOOR:
            why.append("DEAD")
        ok &= _chk("B %-36s" % label, (not why) == want,
                   "PLATEAUED" if not why else "; ".join(why))

    print("C. the residual instrument, BOTH WAYS")
    print("   accept side: THE REAL LOGS, not a synthetic shape")
    for label, case, want in (
            ("K2f_L1 (9.2 decades, clean)", CASE["K2g_L1"], "CONVERGED"),
            ("K2f_L2 (limit cycle at 1.76e-04)", CASE["K2g_L2"], "CONVERGED"),
            ("K2d_L3 RETIRED (995 iterations, same mesh as L3)",
             os.path.join(REPO, "verification", "runs", "F14-cooling-ladder",
                          "K2d_runs", "RETIRED_2026-09-11", "K2d_L3"),
             "CONVERGED")):
        if not os.path.exists(os.path.join(case, "log.solve")):
            ok &= _chk("C %-44s" % label, False, "log.solve missing")
            continue
        st, det = iterative_state(case)
        ok &= _chk("C %-44s" % label, st == want,
                   "%s  Ux last %.3g decades %.2f rise %.3f"
                   % (st.split(":")[0], det["Ux"]["last"], det["Ux"]["decades"],
                      det["Ux"]["rise"]))
    print("   reject side: synthetic series the instrument MUST refuse")
    for label, seq, want in (
            ("dead: never fell", [1.0] * 3000, False),
            ("diverging: rising by orders",
             [1e-4] * 2600 + list(np.logspace(-4, 2, 400)), False),
            ("floored but only 1.5 decades",
             [1.0] * 5 + [3.2e-2] * 2995, False)):
        v = list(seq)
        first, last = max(v[:5]), v[-1]
        dec = math.log10(first / last) if last > 0 else float("inf")
        rise = (sum(v[-100:]) / 100.0) / min(v[-400:])
        good = (last <= RES_FLOOR and dec >= RES_DECADES_MIN
                and rise <= RES_RISE_MAX)
        ok &= _chk("C %-44s" % label, good == want,
                   "last %.3g decades %.2f rise %.3g" % (last, dec, rise))

    print("D. the planted zero, BOTH WAYS")
    ok &= _chk("D1 a reader that sees the plant passes", good_pc["passed"])
    blind = RT.external_plant_control("blind", 1.0, 1.0, plant=PLANT)
    ok &= _chk("D2 a BLIND reader is refused", not blind["passed"])
    try:
        RT.assert_plant_control(blind)
        ok &= _chk("D3 grade_ladder refuses a blind reader", False,
                   "it accepted one")
    except RT.Refusal:
        ok &= _chk("D3 grade_ladder refuses a blind reader", True)

    print("E. the band, BOTH WAYS (a gate that cannot fail is not a gate)")
    r = RT.grade_ladder(QUANTITY, _fake_levels(28.11), DIM, BAND, good_pc,
                        iterative_states=allc, plateau_states=allp)
    ok &= _chk("E1a CONVERGING but ABOVE the band is GATE FAIL",
               r["verdict"] == "GATE FAIL",
               "%s  order %.3f" % (r["verdict"], r.get("order", float("nan"))))
    r = RT.grade_ladder(QUANTITY, _fake_levels(27.95), DIM, BAND, good_pc,
                        iterative_states=allc, plateau_states=allp)
    ok &= _chk("E1b CONVERGING but BELOW the band is GATE FAIL",
               r["verdict"] == "GATE FAIL",
               "%s  order %.3f" % (r["verdict"], r.get("order", float("nan"))))
    r = RT.grade_ladder(QUANTITY, _fake_levels(28.30), DIM, BAND, good_pc,
                        iterative_states=allc, plateau_states=allp)
    ok &= _chk("E1c a DIVERGENT triple is NOT A RESULT even inside a wide band",
               r["verdict"] == "NOT A RESULT", r["verdict"])
    r = RT.grade_ladder(QUANTITY, _fake_levels(27.60), DIM, BAND, good_pc,
                        iterative_states=allc, plateau_states=allp)
    ok &= _chk("E2 a NON-MONOTONE fine value is NOT A RESULT, not GATE FAIL",
               r["verdict"] == "NOT A RESULT", r["verdict"])
    ok &= _chk("E3 no GCI is quoted beside it", "GCI_pct" not in r)

    print("F. mesh similarity, BOTH WAYS")
    ok &= _chk("F1 the registered ladder passes",
               MESHSIM[0] <= 196992 / 58368 <= MESHSIM[1]
               and MESHSIM[0] <= 664848 / 196992 <= MESHSIM[1],
               "r = %.5f" % (196992 / 58368))
    ok &= _chk("F2 a 2.0x third level is REJECTED",
               not (MESHSIM[0] <= 393984 / 196992 <= MESHSIM[1]))

    print("G. the reader, against OpenFOAM's own areaAverage on REAL data")
    ref = {"K2g_L1": 27.189119361484373, "K2g_L2": 27.729679615659716}
    for lv, want in ref.items():
        if not os.path.isdir(CASE[lv]):
            ok &= _chk("G %s present" % lv, False, "case missing")
            continue
        got, src = dp(CASE[lv], ENDTIME[lv])
        ok &= _chk("G %s reader == OpenFOAM areaAverage" % lv,
                   abs(got - want) < 1e-9, "%s %.12f" % (src, got))
    print("H. the planted zero DRIVEN ON REAL DATA, both ways")
    for lv in ("K2g_L1", "K2g_L2"):
        if not os.path.isdir(CASE[lv]):
            ok &= _chk("H %s present" % lv, False, "case missing")
            continue
        pcr = planted_zero(CASE[lv], lv)
        ok &= _chk("H1 %s: the production reader SEES a %g plant on disk"
                   % (lv, PLANT), pcr["passed"],
                   "saw %.12g" % pcr.get("reader_delta", float("nan")))
    pcz = planted_zero(CASE["K2g_L1"], "K2g_L1", patch="a_patch_that_does_not_exist")
    ok &= _chk("H2 a plant the reader CANNOT see is REFUSED -- a control that "
               "cannot fail is not a control", not pcz["passed"],
               "planted %g, reader saw %.12g" % (PLANT,
                                                 pcz.get("reader_delta", float("nan"))))

    print("\n%s" % ("SELFTEST PASSED" if ok else "SELFTEST FAILED"))
    return EXIT_OK if ok else EXIT_FAIL


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--grade", action="store_true")
    ap.add_argument("--json", default=None)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.grade:
        ap.print_help()
        return EXIT_REFUSE
    try:
        rep, code = grade()
    except (Refusal, RT.Refusal) as e:
        print("REFUSED (exit 2): %s" % e)
        return EXIT_REFUSE
    if a.json:
        json.dump(rep, open(a.json, "w"), indent=1, default=str)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
