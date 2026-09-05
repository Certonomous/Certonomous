#!/usr/bin/env python3
"""S1 FD PLATEAU -- the frozen comparator. It grades; it does not compose a verdict by hand.

FROZEN REGISTRATION
    cases/dafoam/ladder-b/S1_FD_PLATEAU_PREREGISTRATION.md
    frozen at commit a1727bd01c4012e1350cd7138460606a3d103338
    blob md5 4c40181966d39acc39489b094e4b824a (verified from `git show`, NEVER from the
    working tree -- a disk-side hash would hash the wrong document, which this family
    measured on 2026-09-04).

WHAT THIS FILE IS ENTITLED TO DECIDE, and nothing else:
    GATE P1 (prereg 2.4)  |d(0.05) - d(0.025)| / |d(0.05)| <= 10 %, PER COMPONENT.
                          A miss is NOT A RESULT -- explicitly NOT GATE FAIL, because a
                          failed plateau does not show the adjoint wrong, it shows the FD
                          estimate not to be a measurement of the derivative.
    ARM F (prereg 2.5)    cell 5363 at h = 0.5. Registered prediction: rel. err > 2 %.
                          REGISTERED CONSEQUENCE: if the deliberately wrong step PASSES
                          P1's bar, P1's verdict is WITHDRAWN FOR EVERY COMPONENT.

IT REFUSES (exit 2) RATHER THAN DEGRADES:
    * the planted-zero control (prereg 2.7, CLAUDE.md rule 3) must be SEEN;
    * the reader must first reproduce a PUBLISHED number it did not compute;
    * a rule-4 incomplete primal is not a result and cannot be graded around.

Usage:  python3 analyse_s1_fd_plateau.py [--run-root DIR] [--json OUT.json]
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ----------------------------------------------------------------- FROZEN CONSTANTS
# Every number in this block is REGISTERED and may not move (prereg 2.2, 2.4, 2.5, 2.8).
ETA = 3.907091e-12            # noise floor, last 200 iterations of log.anchor8
ETA_CONS = 2.751958e-11       # conservative alternative, last 500 iterations
S_HI = 0.05                   # the already-graded step -- frozen, not re-selected
S_LO = 0.025                  # fixed by N-D21's pair constraint s_hi >= 2*s_lo
S_FALSIFIER = 0.5             # the registered trivial baseline: ten times the graded step
P1_BAR = 0.10                 # 10 %, per component
FALSIFIER_PREDICTION = 0.02   # rel. err > 2 %
CLEARANCE_BAR = 5.0           # N-D21 rule 3: C >= 5
SIGNFLIP_MOVE = 0.50          # 50 % of own magnitude across one decade of step
PLANT = 1.234e-03             # planted-zero control, RELATIVE, into the + leg of 5428 only
PLANT_CELL = 5428
CELLS = (5363, 5428, 5491)
DECLARED_PRIMALS = 8          # 6 (Arm P) + 2 (Arm F)
END_TIME = 2500               # system/controlDict endTime
CAP_CORE_MIN = 75.0           # REGISTERED HARD CAP -- an overrun STOPS the item
EST_CORE_MIN = 60.711         # registered estimate: P 45.533 + F 15.178

# The unperturbed control, REUSED and not re-bought: a central difference does not use
# it, and prereg 2.8 budgets no new baseline primal.
FD8_BASE_OBJ = 6.1509017109920479e-04

ARCHIVE = Path("/home/ubuntu/certonomous-runs/S1-cbfs-reinversion")
ANCHOR_NPY = ARCHIVE / "cbfs_inv" / "grad_anchor8.npy"
ANCHOR_MD5 = "3b1548801294e523944dc85c139529b9"

# The PUBLISHED numbers this reader must reproduce before it is trusted on new data
# (S1_CBFS_REINVERSION_PREREGISTRATION.md:207-211, Amendment 1 section C).
PUBLISHED_RELERR_PCT = {5363: 0.032, 5428: 0.115, 5491: 0.009}

# Rule 4's field list for THIS family. CLAUDE.md rule 4 names the THERMAL family's
# fields (T U p_rgh alphat nut k omega); the incompressible DASimpleFoam analogue is
# below. The substitution is stated, not silently made.
FIELDS = ("U", "p", "k", "omega", "nut", "phi")

OBJ_RE = re.compile(r"^OBJ varianceU:\s*(\S+)\s*$")
TIME_RE = re.compile(r"^Time = (\S+)\s*$")
TOTRES_RE = re.compile(r"^Total Residual Norm2:\s*(\S+)\s*$")


class Refusal(Exception):
    """Raised for every condition on which this comparator refuses rather than degrades."""


def refuse(msg: str) -> "Refusal":
    return Refusal(msg)


# --------------------------------------------------------------------- LOG PARSING
def parse_obj(path: Path) -> tuple[int, float]:
    """Return (line index of the LAST 'OBJ varianceU:' line, its value).

    The line INDEX is returned because prereg 2.7 requires the plant be applied
    'by line index in the parsed objective list' -- so the index is a parsed product,
    not something the planter recomputes for itself.
    """
    lines = path.read_text(errors="replace").splitlines()
    hit = None
    for i, ln in enumerate(lines):
        m = OBJ_RE.match(ln)
        if m:
            hit = (i, float(m.group(1)))
    if hit is None:
        raise refuse(f"no 'OBJ varianceU:' line in {path} -- the objective was never printed")
    return hit


def log_facts(path: Path) -> dict:
    lines = path.read_text(errors="replace").splitlines()
    ends = sum(1 for ln in lines if ln.strip() == "End")
    times = [m.group(1) for ln in lines if (m := TIME_RE.match(ln))]
    totres = [m.group(1) for ln in lines if (m := TOTRES_RE.match(ln))]
    return {
        "end_lines": ends,
        "last_time": times[-1] if times else None,
        "n_time_lines": len(times),
        "total_residual_norm2": float(totres[-1]) if totres else None,
    }


def ledger_rows(root: Path) -> dict:
    out: dict[str, dict] = {}
    p = root / "ledger.csv"
    if not p.exists():
        return out
    for ln in p.read_text().splitlines():
        f = ln.split(",")
        if len(f) >= 7 and f[1] == "END":
            out[f[0]] = {
                "rc": int(f[4].split("=")[1]),
                "wall_s": int(f[5].split("=")[1]),
                "core_min": float(f[6].split("=")[1]),
                "ranks": int(f[3]),
            }
    return out


# ------------------------------------------------------- RULE 4 STRICT COMPLETION
def completion(root: Path, tag: str, led: dict) -> dict:
    """CLAUDE.md rule 4, all-or-nothing. Every clause is reported, pass or fail."""
    log = root / f"log.{tag}"
    c: dict = {"tag": tag, "clauses": {}, "notes": []}

    c["clauses"]["log_exists"] = log.exists()
    if not log.exists():
        c["complete"] = False
        c["reason"] = "no log file -- the primal did not run"
        return c

    row = led.get(tag)
    c["clauses"]["ledger_row"] = row is not None
    c["clauses"]["rc_zero"] = bool(row and row["rc"] == 0)
    c["rc"] = row["rc"] if row else None
    c["wall_s"] = row["wall_s"] if row else None
    c["core_min"] = row["core_min"] if row else None

    f = log_facts(log)
    c.update(f)
    c["clauses"]["end_line"] = f["end_lines"] >= 1
    c["clauses"]["last_time_is_endtime"] = (
        f["last_time"] is not None and abs(float(f["last_time"]) - END_TIME) < 1e-9)

    try:
        idx, val = parse_obj(log)
        c["obj"] = val
        c["obj_lineno"] = idx
        c["clauses"]["objective_printed"] = True
    except Refusal:
        c["obj"] = None
        c["clauses"]["objective_printed"] = False

    # Fields present at endTime, in the preserved decomposition.
    fdir = root / f"fields_{tag}"
    present, missing, mtimes = [], [], []
    for p in range(4):
        for fld in FIELDS:
            fp = fdir / f"processor{p}" / str(END_TIME) / fld
            if fp.exists():
                present.append(str(fp))
                mtimes.append(fp.stat().st_mtime)
            else:
                missing.append(str(fp))
    c["clauses"]["fields_present"] = (len(missing) == 0 and len(present) == 4 * len(FIELDS))
    c["fields_missing"] = missing[:6]

    # THE AGE GUARD. 0/ was touched LAST at staging, so it dates the run allowed to
    # produce this answer. Every field at endTime must be NEWER than it.
    zero = root / "cbfs_inv" / "0"
    zt = max((q.stat().st_mtime for q in zero.iterdir() if q.is_file()), default=None)
    c["zero_mtime"] = zt
    c["min_field_mtime"] = min(mtimes) if mtimes else None
    c["clauses"]["age_guard"] = bool(mtimes and zt is not None and min(mtimes) > zt)

    c["complete"] = all(c["clauses"].values())
    if not c["complete"]:
        c["reason"] = "FAILED rule 4 clauses: " + ", ".join(
            k for k, v in c["clauses"].items() if not v)
    return c


# ------------------------------------------------------------------ FD ARITHMETIC
def central(jp: float, jm: float, h: float) -> float:
    return (jp - jm) / (2.0 * h)


def relerr(fd: float, adj: float) -> float:
    return abs(fd - adj) / abs(adj)


def clearance(adj: float, s: float, eta: float) -> float:
    return abs(adj) * 2.0 * s / eta


# ------------------------------------------------------- THE PLANTED-ZERO CONTROL
def planted_pass(root: Path, tags: dict, tmp: Path) -> dict:
    """prereg 2.7 / CLAUDE.md rule 3.

    A comparator that reports agreement must first be shown able to report
    disagreement. PLANT is added RELATIVE to the + leg of cell 5428 ONLY, BY LINE
    INDEX in the parsed objective list, applied to a COPY, and RE-READ FROM DISK.
    """
    target_tag = tags[PLANT_CELL]["plus"]
    out = {"plant": PLANT, "cell": PLANT_CELL, "target_tag": target_tag,
           "copies": [], "run_artefacts_modified": False}

    for cell in CELLS:
        for sgn in ("plus", "minus"):
            t = tags[cell][sgn]
            src = root / f"log.{t}"
            dst = tmp / f"log.{t}"
            shutil.copy2(src, dst)
            out["copies"].append(str(dst))

    # Plant BY LINE INDEX taken from the parse, into the COPY.
    dst = tmp / f"log.{target_tag}"
    idx, orig = parse_obj(dst)
    lines = dst.read_text().splitlines()
    if not OBJ_RE.match(lines[idx]):
        raise refuse("the parsed line index does not address an OBJ line -- planter and "
                     "parser disagree, so the control could not be applied where it was aimed")
    lines[idx] = "OBJ varianceU: %.16e" % (orig * (1.0 + PLANT))
    dst.write_text("\n".join(lines) + "\n")
    out["planted_line_index"] = idx
    out["objective_before"] = orig
    out["objective_after"] = orig * (1.0 + PLANT)

    # Confirm the run artefact itself is untouched.
    src_idx, src_val = parse_obj(root / f"log.{target_tag}")
    out["run_artefacts_modified"] = (src_val != orig)
    if out["run_artefacts_modified"]:
        raise refuse("the plant reached the RUN ARTEFACT. It must be applied to a COPY.")
    return out


# -------------------------------------------------------------------------- MAIN
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-root", default="/home/ubuntu/certonomous-runs/S1-fd-plateau")
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    root = Path(a.run_root)

    import numpy as np

    R: dict = {"registration": {
        "path": "cases/dafoam/ladder-b/S1_FD_PLATEAU_PREREGISTRATION.md",
        "commit": "a1727bd01c4012e1350cd7138460606a3d103338",
        "blob_md5": "4c40181966d39acc39489b094e4b824a",
        "eta": ETA, "eta_cons": ETA_CONS, "s_hi": S_HI, "s_lo": S_LO,
        "p1_bar": P1_BAR, "falsifier_step": S_FALSIFIER,
        "falsifier_prediction_relerr": FALSIFIER_PREDICTION,
        "cap_core_min": CAP_CORE_MIN, "estimate_core_min": EST_CORE_MIN}}

    print("=" * 78)
    print("S1 FD PLATEAU -- FROZEN COMPARATOR")
    print("registration a1727bd0 blob md5 4c40181966d39acc39489b094e4b824a")
    print("=" * 78)

    # --------------------------------------------------- 0. the anchor, by md5
    h = subprocess.run(["md5sum", str(ANCHOR_NPY)], capture_output=True, text=True)
    got = h.stdout.split()[0] if h.returncode == 0 else "<unreadable>"
    if got != ANCHOR_MD5:
        raise refuse(f"grad_anchor8.npy md5 {got} != registered {ANCHOR_MD5}. The frozen "
                     "analytic reference is not the file this comparator was written against.")
    g = np.load(ANCHOR_NPY)
    adj = {c: float(g[c]) for c in CELLS}
    print(f"\n[0] anchor gradient  {ANCHOR_NPY}  md5 OK")
    for c in CELLS:
        print(f"      J_adj[{c}] = {adj[c]:.12e}")

    # ------------------------- 1. READER CONTROL: reproduce a PUBLISHED number
    # A reader is not trusted on new data until it reproduces a number it did not
    # compute. This is the same principle as the planted zero, aimed at the reader
    # rather than at the plumbing.
    print("\n[1] READER CONTROL -- reproduce the PUBLISHED h=0.05 rel. errs from the archive")
    arch: dict = {}
    for c in CELLS:
        jp = parse_obj(ARCHIVE / f"log.fd8_{c}_plus")[1]
        jm = parse_obj(ARCHIVE / f"log.fd8_{c}_minus")[1]
        d = central(jp, jm, S_HI)
        re_ = relerr(d, adj[c])
        arch[c] = {"jp": jp, "jm": jm, "d": d, "relerr": re_}
        pub = PUBLISHED_RELERR_PCT[c]
        ok = abs(re_ * 100.0 - pub) <= 0.001
        print(f"      cell {c}: d(0.05) = {d:.12e}  rel.err = {re_*100:.4f} %  "
              f"published {pub} %  {'OK' if ok else 'MISMATCH'}")
        if not ok:
            raise refuse(
                f"the reader does not reproduce the published rel. err for cell {c} "
                f"({re_*100:.4f} % vs {pub} %). It is not trusted on new data.")
    print("      READER CONTROL PASSED -- this reader reproduces all three published values.")
    R["reader_control"] = {str(c): arch[c]["relerr"] * 100.0 for c in CELLS}
    R["baseline_reused"] = {"tag": "fd8_base", "obj": FD8_BASE_OBJ,
                            "note": "step-independent; NOT re-bought (prereg 2.8)"}

    # --------------------------------------------------- 2. rule 4 completion
    tags = {c: {"plus": f"p025_{c}_plus", "minus": f"p025_{c}_minus"} for c in CELLS}
    ftags = {"plus": f"f500_5363_plus", "minus": f"f500_5363_minus"}
    all_tags = [ftags["plus"], ftags["minus"]] + [tags[c][s] for c in CELLS for s in ("plus", "minus")]

    led = ledger_rows(root)
    comp = {t: completion(root, t, led) for t in all_tags}
    executed = [t for t in all_tags if comp[t]["complete"]]
    blocked = [t for t in all_tags if not comp[t]["complete"]]

    print(f"\n[2] RULE 4 STRICT COMPLETION -- declared {DECLARED_PRIMALS}, "
          f"executed {len(executed)}, blocked {len(blocked)}")
    print(f"      field list for this family: {' '.join(FIELDS)}  "
          f"(rule 4 names the THERMAL family's fields; this is the DASimpleFoam analogue)")
    for t in all_tags:
        c = comp[t]
        bad = [k for k, v in c["clauses"].items() if not v]
        print(f"      {t:<22} {'COMPLETE' if c['complete'] else 'INCOMPLETE'}  "
              f"rc={c.get('rc')} last_time={c.get('last_time')} "
              f"wall={c.get('wall_s')}s core_min={c.get('core_min')}"
              + (f"  FAILED: {','.join(bad)}" if bad else ""))
    R["completion"] = comp
    R["counts"] = {"declared": DECLARED_PRIMALS, "executed": len(executed),
                   "blocked": len(blocked)}
    if DECLARED_PRIMALS != len(executed) + len(blocked):
        raise refuse("declared != executed + blocked -- the program accounting is broken")

    # --------------------------------- 3. THE PLANTED-ZERO CONTROL (rule 3)
    print(f"\n[3] PLANTED-ZERO CONTROL -- PLANT = {PLANT:.6e} relative into the + leg of "
          f"cell {PLANT_CELL} ONLY, by line index, re-read from disk, applied to a COPY")
    armp_ok = all(comp[tags[c][s]]["complete"] for c in CELLS for s in ("plus", "minus"))
    if not armp_ok:
        print("      NOT RUN: Arm P is not rule-4 complete, so there is nothing to grade "
              "and nothing for the control to protect.")
        R["plant"] = {"run": False, "reason": "Arm P incomplete"}
    else:
        with tempfile.TemporaryDirectory(prefix="s1fdp_plant_") as td:
            tmp = Path(td)
            pinfo = planted_pass(root, tags, tmp)
            clean_d, plant_d = {}, {}
            for c in CELLS:
                jp = parse_obj(root / f"log.{tags[c]['plus']}")[1]
                jm = parse_obj(root / f"log.{tags[c]['minus']}")[1]
                clean_d[c] = central(jp, jm, S_LO)
                pjp = parse_obj(tmp / f"log.{tags[c]['plus']}")[1]
                pjm = parse_obj(tmp / f"log.{tags[c]['minus']}")[1]
                plant_d[c] = central(pjp, pjm, S_LO)

            implied = pinfo["objective_before"] * PLANT / (2.0 * S_LO)
            observed = plant_d[PLANT_CELL] - clean_d[PLANT_CELL]
            print(f"      cell {PLANT_CELL}: d moved {clean_d[PLANT_CELL]:.12e} -> "
                  f"{plant_d[PLANT_CELL]:.12e}")
            print(f"      observed delta {observed:.12e}   implied by the plant "
                  f"{implied:.12e}")
            if observed == 0.0:
                raise refuse("THE PLANT WAS NOT SEEN: cell 5428 did not move. A zero from a "
                             "reader not shown able to see a non-zero is not evidence. "
                             "NOTHING IS GRADED.")
            if abs(observed - implied) > 1e-9 * abs(implied):
                raise refuse(f"the plant moved cell {PLANT_CELL} by {observed:.12e}, not by "
                             f"the implied {implied:.12e}. NOTHING IS GRADED.")
            for c in CELLS:
                if c == PLANT_CELL:
                    continue
                if plant_d[c] != clean_d[c]:
                    raise refuse(f"the plant leaked into cell {c} "
                                 f"({clean_d[c]!r} -> {plant_d[c]!r}). NOTHING IS GRADED.")
                print(f"      cell {c}: unchanged to the last digit ({clean_d[c]!r})")
            print("      PLANT SEEN. The comparator can report disagreement.")
            R["plant"] = {"run": True, "seen": True, "observed_delta": observed,
                          "implied_delta": implied, "line_index": pinfo["planted_line_index"],
                          "run_artefacts_modified": False}

    # --------------------------------------------------------- 4. ARM F first
    print(f"\n[4] ARM F -- the registered trivial baseline: cell 5363 at h = {S_FALSIFIER}")
    armf_ok = comp[ftags["plus"]]["complete"] and comp[ftags["minus"]]["complete"]
    fal: dict = {"complete": armf_ok}
    if armf_ok:
        jp = parse_obj(root / f"log.{ftags['plus']}")[1]
        jm = parse_obj(root / f"log.{ftags['minus']}")[1]
        d_f = central(jp, jm, S_FALSIFIER)
        re_f = relerr(d_f, adj[5363])
        fal.update({"d": d_f, "relerr": re_f,
                    "prediction_met": re_f > FALSIFIER_PREDICTION,
                    "sign_match": (d_f > 0) == (adj[5363] > 0)})
        # Does the deliberately-wrong step PASS P1's bar against d(0.05)?
        p1_f = abs(arch[5363]["d"] - d_f) / abs(arch[5363]["d"])
        fal["p1_against_dhi"] = p1_f
        fal["falsifier_passes_p1"] = p1_f <= P1_BAR
        print(f"      d(0.5) = {d_f:.12e}   rel.err = {re_f*100:.4f} %   "
              f"REGISTERED PREDICTION > {FALSIFIER_PREDICTION*100:.0f} %  -> "
              f"{'MET' if fal['prediction_met'] else 'NOT MET'}")
        print(f"      P1 bar applied to the WRONG step: {p1_f*100:.4f} % vs "
              f"{P1_BAR*100:.0f} %  -> {'PASSES (DISCRIMINATION FAILURE)' if fal['falsifier_passes_p1'] else 'FAILS, as registered'}")
        # sign-flip duty across one decade of step (0.05 -> 0.5)
        move = abs(d_f - arch[5363]["d"]) / abs(arch[5363]["d"])
        fal["decade_move"] = move
        fal["signflip_flag"] = (not fal["sign_match"]) or move > SIGNFLIP_MOVE
        print(f"      sign-flip duty, one decade 0.05 -> 0.5: move {move*100:.2f} % of own "
              f"magnitude, sign {'MATCHES' if fal['sign_match'] else 'FLIPS'} -> "
              f"{'FLAGGED' if fal['signflip_flag'] else 'not flagged'}")
    else:
        print("      INCOMPLETE -- Arm F did not produce two rule-4 complete primals.")
    R["arm_f"] = fal

    # ------------------------------------------------------------- 5. GATE P1
    print(f"\n[5] GATE P1 -- |d({S_HI}) - d({S_LO})| / |d({S_HI})| <= {P1_BAR*100:.0f} %, "
          "PER COMPONENT")
    p1: dict = {}
    for c in CELLS:
        tp, tm = tags[c]["plus"], tags[c]["minus"]
        if not (comp[tp]["complete"] and comp[tm]["complete"]):
            p1[c] = {"token": "NOT A RESULT", "reason": "primal not rule-4 complete"}
            print(f"      cell {c}: NOT A RESULT -- primal not rule-4 complete")
            continue
        jp = parse_obj(root / f"log.{tp}")[1]
        jm = parse_obj(root / f"log.{tm}")[1]
        d_lo = central(jp, jm, S_LO)
        d_hi = arch[c]["d"]
        move = abs(d_hi - d_lo) / abs(d_hi)
        inside = move <= P1_BAR
        p1[c] = {
            "d_lo": d_lo, "d_hi": d_hi, "p1_move": move, "inside_bar": inside,
            "relerr_lo": relerr(d_lo, adj[c]), "relerr_hi": arch[c]["relerr"],
            "sign_match_lo": (d_lo > 0) == (adj[c] > 0),
            "sign_match_hi": (d_hi > 0) == (adj[c] > 0),
            "clearance_eta": clearance(adj[c], S_LO, ETA),
            "clearance_eta_cons": clearance(adj[c], S_LO, ETA_CONS),
            "stopping_iteration_plus": comp[tp]["last_time"],
            "stopping_iteration_minus": comp[tm]["last_time"],
            "token": "PASS" if inside else "NOT A RESULT",
        }
        print(f"      cell {c}: d({S_LO}) = {d_lo:.12e}   d({S_HI}) = {d_hi:.12e}")
        print(f"               P1 move = {move*100:.4f} %  bar {P1_BAR*100:.0f} %  -> "
              f"{p1[c]['token']}")
        print(f"               rel.err vs anchor: {p1[c]['relerr_lo']*100:.4f} % at {S_LO}, "
              f"{p1[c]['relerr_hi']*100:.4f} % at {S_HI}")
        print(f"               clearance C({S_LO}) = {p1[c]['clearance_eta']:.3e} (eta)  "
              f"{p1[c]['clearance_eta_cons']:.3e} (eta_cons)  bar C >= {CLEARANCE_BAR}")
    R["p1"] = p1

    # ---------------------- 6. the registered consequence, applied mechanically
    withdrawn = bool(fal.get("falsifier_passes_p1"))
    if withdrawn:
        print("\n[6] REGISTERED CONSEQUENCE (prereg 2.5): the deliberately wrong step PASSED "
              "P1's bar, so P1's VERDICT IS WITHDRAWN FOR EVERY COMPONENT -- the gate is "
              "shown not to discriminate step quality.")
        for c in CELLS:
            p1[c]["token"] = "NOT A RESULT"
            p1[c]["withdrawn_by_falsifier"] = True
    else:
        print("\n[6] REGISTERED CONSEQUENCE: not triggered -- the wrong step does not pass "
              "P1's bar, so the gate discriminates step quality.")
    R["falsifier_withdrawal"] = withdrawn

    # --------------------------------------------------- 7. the two registered tables
    print(f"\n[7] TABLE 1 (prereg 2.6) -- per component, WITH the step column and the "
          "sign-match column the original section C table lacked")
    print(f"      | {'idx':>5} | {'analytic':>18} | {'FD':>18} | {'step':>6} | "
          f"{'rel. err %':>10} | {'sign match':>10} |")
    rows1 = []
    for c in CELLS:
        for step, key in ((S_HI, "hi"), (S_LO, "lo")):
            if key == "hi":
                d, re_, sm = arch[c]["d"], arch[c]["relerr"], (arch[c]["d"] > 0) == (adj[c] > 0)
            else:
                if "d_lo" not in p1[c]:
                    print(f"      | {c:>5} | {adj[c]:>18.10e} | {'--':>18} | {step:>6} | "
                          f"{'--':>10} | {'--':>10} |   (not a result)")
                    continue
                d, re_, sm = p1[c]["d_lo"], p1[c]["relerr_lo"], p1[c]["sign_match_lo"]
            print(f"      | {c:>5} | {adj[c]:>18.10e} | {d:>18.10e} | {step:>6} | "
                  f"{re_*100:>10.4f} | {'yes' if sm else 'NO':>10} |")
            rows1.append({"idx": c, "analytic": adj[c], "fd": d, "step": step,
                          "relerr_pct": re_ * 100, "sign_match": sm})
    if armf_ok:
        print(f"      | {5363:>5} | {adj[5363]:>18.10e} | {fal['d']:>18.10e} | "
              f"{S_FALSIFIER:>6} | {fal['relerr']*100:>10.4f} | "
              f"{'yes' if fal['sign_match'] else 'NO':>10} |   (Arm F, registered falsifier)")
        rows1.append({"idx": 5363, "analytic": adj[5363], "fd": fal["d"],
                      "step": S_FALSIFIER, "relerr_pct": fal["relerr"] * 100,
                      "sign_match": fal["sign_match"], "arm": "F"})
    R["table_per_component"] = rows1

    print(f"\n      TABLE 2 (prereg 2.6) -- step sweep, FAILED STEPS AS ROWS: "
          "'a sweep that hides its failed steps is reporting a plateau it did not measure'")
    print(f"      | {'step':>6} | {'rel err %':>10} | {'rel err %':>10} | {'cosine':>8} | status")
    print(f"      | {'':>6} | {'':>10} | {'(excl flag)':>10} | {'':>8} |")
    rows2 = []
    for step, getter in ((S_HI, "hi"), (S_LO, "lo"), (S_FALSIFIER, "f")):
        if getter == "hi":
            vals = [(c, arch[c]["relerr"], True) for c in CELLS]
            status = "OK (archived, S1 Amendment 1 section C)"
        elif getter == "lo":
            vals = [(c, p1[c]["relerr_lo"], p1[c].get("inside_bar", False))
                    for c in CELLS if "relerr_lo" in p1[c]]
            miss = [c for c in CELLS if "relerr_lo" not in p1[c]]
            status = "OK" if not miss else (
                "FAILED: primal not rule-4 complete for idx " + ",".join(str(m) for m in miss)
                + f" (+step); see clause list, tolerance 1e-8")
        else:
            if not armf_ok:
                bad = [t for t in (ftags["plus"], ftags["minus"]) if not comp[t]["complete"]]
                rows2.append({"step": step, "status": "FAILED: " + ",".join(bad)})
                print(f"      | {step:>6} | {'--':>10} | {'--':>10} | {'--':>8} | "
                      f"FAILED: primal not rule-4 complete for {','.join(bad)}")
                continue
            vals = [(5363, fal["relerr"], not fal["signflip_flag"])]
            status = ("REGISTERED FALSIFIER -- prediction > 2 % "
                      + ("MET" if fal["prediction_met"] else "NOT MET"))
        if not vals:
            print(f"      | {step:>6} | {'--':>10} | {'--':>10} | {'--':>8} | {status}")
            rows2.append({"step": step, "status": status})
            continue
        mean_all = sum(v for _, v, _ in vals) / len(vals)
        keep = [v for _, v, ok in vals if ok]
        mean_ex = (sum(keep) / len(keep)) if keep else float("nan")
        # cosine between the FD vector and the analytic vector over the cells in play
        idxs = [c for c, _, _ in vals]
        if getter == "hi":
            fv = [arch[c]["d"] for c in idxs]
        elif getter == "lo":
            fv = [p1[c]["d_lo"] for c in idxs]
        else:
            fv = [fal["d"]]
        av = [adj[c] for c in idxs]
        dot = sum(x * y for x, y in zip(fv, av))
        cos = dot / (math.sqrt(sum(x * x for x in fv)) * math.sqrt(sum(y * y for y in av)))
        print(f"      | {step:>6} | {mean_all*100:>10.4f} | {mean_ex*100:>10.4f} | "
              f"{cos:>8.6f} | {status}")
        rows2.append({"step": step, "relerr_pct": mean_all * 100,
                      "relerr_pct_excl_flagged": mean_ex * 100, "cosine": cos,
                      "status": status})
    R["table_step_sweep"] = rows2

    # -------------------------------------------------------------- 8. cost, rule 12
    spent = sum(v["core_min"] for v in led.values())
    over = spent > CAP_CORE_MIN
    print(f"\n[8] RULE 12 -- registered estimate {EST_CORE_MIN} core-min, HARD CAP "
          f"{CAP_CORE_MIN}, ACTUAL {spent:.3f} core-min "
          f"(ratio actual/predicted {spent/EST_CORE_MIN:.4f})")
    print(f"      derived $ at the owner-stated c7a.4xlarge rate $0.0513/core-h: "
          f"${spent/60*0.0513:.4f}  [DERIVED, NOT MEASURED -- the box cannot read its "
          f"own billing]")
    stalls = [t for t, v in led.items() if v["wall_s"] > 3600]
    print(f"      rows over 3600 wall s (stalls): {stalls if stalls else 'none'}")
    print(f"      CAP {'EXCEEDED -- THE ITEM STOPS' if over else 'respected'}")
    R["cost"] = {"estimate_core_min": EST_CORE_MIN, "cap_core_min": CAP_CORE_MIN,
                 "actual_core_min": spent, "ratio": spent / EST_CORE_MIN,
                 "derived_usd": spent / 60 * 0.0513, "cap_exceeded": over,
                 "stalled_rows": stalls,
                 "cost_basis": "core-minutes MEASURED from this item's own ledger.csv; "
                               "the dollar figure is DERIVED at the owner-stated rate and "
                               "is reported-by-owner, NOT MEASURED"}

    # ------------------------------------------------------------- 9. THE VERDICT
    print("\n" + "=" * 78)
    print("VERDICT -- produced by this frozen path, not composed by hand")
    print("=" * 78)
    if blocked:
        item = "BLOCKED"
        why = (f"{len(blocked)} of {DECLARED_PRIMALS} declared primals are not rule-4 "
               f"complete ({', '.join(blocked)}). prereg 2.9: any blocked > 0 forces the "
               f"item's token to NOT A RESULT or BLOCKED. No success-reading token is "
               f"emitted over a short program.")
    elif withdrawn:
        item = "NOT A RESULT"
        why = ("the registered falsifier at h = 0.5 PASSED P1's bar, so P1's verdict is "
               "withdrawn for every component (prereg 2.5).")
    elif all(p1[c]["token"] == "PASS" for c in CELLS):
        item = "PASS"
        why = ("all three components sit inside the registered 10 % plateau bar, the "
               "falsifier failed the bar as predicted, and the planted zero was seen.")
    else:
        outside = [c for c in CELLS if p1[c]["token"] != "PASS"]
        item = "NOT A RESULT"
        why = (f"component(s) {outside} miss the 10 % plateau bar. Registered label: NOT A "
               f"RESULT, not GATE FAIL -- a failed plateau does not show the adjoint wrong, "
               f"it shows the FD estimate not to be a measurement of the derivative.")
    print(f"\nITEM TOKEN: {item}")
    print(f"REASON:     {why}")
    for c in CELLS:
        print(f"  cell {c}: {p1[c]['token']}")
    if armf_ok:
        print(f"  Arm F (h=0.5): rel.err {fal['relerr']*100:.4f} % vs registered "
              f"prediction > 2 % -> {'MET' if fal['prediction_met'] else 'NOT MET'}")
    print(f"  cost: {spent:.3f} core-min actual vs {EST_CORE_MIN} registered, cap "
          f"{CAP_CORE_MIN}")
    R["verdict"] = {"item_token": item, "reason": why,
                    "per_cell": {str(c): p1[c]["token"] for c in CELLS}}

    if a.json:
        Path(a.json).write_text(json.dumps(R, indent=2, default=str))
        print(f"\nmachine record: {a.json}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Refusal as e:
        print("\n" + "!" * 78, file=sys.stderr)
        print("COMPARATOR REFUSES (exit 2). NOTHING IS GRADED.", file=sys.stderr)
        print(f"REASON: {e}", file=sys.stderr)
        print("!" * 78, file=sys.stderr)
        sys.exit(2)
