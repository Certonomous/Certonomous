#!/usr/bin/env python3
"""W4 CBFS RE-ANCHOR -- the frozen comparator. It grades; it does not compose a
verdict by hand.

DERIVED, NOT WRITTEN FROM SCRATCH.  This file is
`cases/dafoam/ladder-b/S1_fd_plateau/analyse_s1_fd_plateau.py` (S1FDP's frozen
grading path, `5f55c742`, the closest kin -- it graded S1FDP to NOT A RESULT on
this same case family) DERIVED for Arm W4's 1e-8 re-anchor.  The DELTAS diff
beside it -- `analyse_w4_reanchor_DELTAS_from_analyse_s1_fd_plateau.diff` -- is
the derivation, shown.  This family's practice, and it is why the diffs are
readable.

FROZEN REGISTRATION
    cases/dafoam/ladder-b/W4_REANCHOR_PREREGISTRATION.md
    frozen at commit <F2 -- filled by the supervisor at the freeze commit>
    The registration is IN `FROZEN_PATHS`; `freeze_check` verifies disk == the
    committed blob at HEAD for it and for every instrument, so the freeze commit
    IS what this comparator is pinned to. There is no hardcoded blob md5 here:
    a disk-side hash would hash the wrong document (this family measured that on
    2026-09-04); the git-blob comparison in `freeze_check` cannot.

WHAT THIS FILE IS ENTITLED TO DECIDE, and nothing else:
    W1 (prereg 7.1)   |d(0.05) - d(0.025)| / |d(0.05)| <= 10 %, PER COMPONENT,
                      denominator |d(0.05)| (the graded larger step).  A miss is
                      NOT A RESULT -- explicitly NOT GATE FAIL, because a failed
                      plateau does not show the adjoint wrong, it shows the FD
                      estimate not to be a measurement of the derivative.
    W0 (prereg 7.2)   base consistency: OBJ varianceU from `anchor8w` (the
                      reference's own primal) == that from `base8w`, to 16 digits.
                      Not equal -> STOP, NOT A RESULT: no FD number is graded
                      against a gradient computed from a different state.
    F_W (prereg 7.3)  cell 5491 at h_F = 0.75.  REGISTERED PREDICTION: the
                      plateau statistic against d(0.05) is 19.1195 % > 10 %, so
                      F_W FAILS W1's 10 % bar -- the gate it NAMES.  This file
                      GRADES THE MEASUREMENT AGAINST THE REGISTERED PREDICTION;
                      it does NOT recompute 19.1195 from the O(h^2) model.
                      REGISTERED CONSEQUENCE: if the wrong step PASSES W1's bar,
                      W1's verdict is WITHDRAWN FOR EVERY COMPONENT (NOT A
                      RESULT).  F_W is a PRECONDITION for reading W1: if F_W is
                      UNRESOLVED, every W1 component reads UNRESOLVED.
    W2 (prereg 7.4)   ACCEPT_FLOOR_UNMOVED, imported from
                      `w4ra_accept_floor_control.py`: primalMinResTol == 1e-8,
                      primalMinResTolDiff == 100, product == 1e-6, read back out
                      of EVERY leg's OWN log.  primalMinResTolDiff IS 100 ON THE
                      S1 CBFS FAMILY, NOT 1000 (N-D43).  REFUSES (exit 2) on any
                      deviation, in EITHER direction.

IT REFUSES (exit 2) RATHER THAN DEGRADES:
    * the planted-zero control (prereg 7.5, CLAUDE.md rule 3) must be SEEN, and
      it plants into a COPY through THE LITERAL functions the FD gate calls;
    * W2 must read a tolerance back from EVERY leg's own log;
    * a rule-4 incomplete primal is not a result and cannot be graded around;
    * a staged instrument whose md5 != its registered source md5 is refused --
      a registration that hashes the source and grades the copy has checked
      nothing about what ran (prereg 4.3).

WHAT IT DOES NOT INFER (prereg 10.2):
    Whether the accept floor was MET is reported only where a banner states it.
    An absent banner is FLOOR_STATE_UNREADABLE, NEVER FLOOR_MET -- a zero from a
    reader not shown able to see a non-zero is not evidence, and on this run
    path NEITHER banner prints (N-D43 CORRECTION).

Usage:  python3 analyse_w4_reanchor.py [--run-root DIR] [--json OUT.json]
                                       [--skip-freeze]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *([os.pardir] * 4)))
sys.path.insert(0, HERE)
import w4ra_accept_floor_control as afc                          # noqa: E402

# ----------------------------------------------------------------- FROZEN CONSTANTS
# Every number in this block is REGISTERED and may not move (prereg 6, 7, 8).
S_HI = 0.05                   # the graded step -- d(0.05), the denominator of W1
S_LO = 0.025                  # fixed by N-D21's pair constraint s_hi >= 2*s_lo
H_F = 0.75                    # the falsifier step -- RESCALED from 0.5 (prereg 7.3)
W1_BAR = 0.10                 # 10 %, per component (N-D21 rule 7)
# The REGISTERED F_W prediction. NOT recomputed here: the O(h^2) fit that
# produced these lives in the frozen registration section 7.3 and is graded
# against, not re-derived (prereg 7.3, and the brief).
FALSIFIER_PRED_PCT_DHI = 19.1195   # statistic against |d(0.05)|  -> fails 10 %
FALSIFIER_PRED_PCT_DHF = 23.6392   # statistic against |d(h_F)|   -> fails 10 %
FALSIFIER_CELL = 5491
SIGNFLIP_MOVE = 0.50          # 50 % of own magnitude across one decade of step
PLANT = 1.234e-03            # planted-zero control, RELATIVE, into the + leg of 6740
PLANT_CELL = 6740
CELLS = (5491, 6740, 12486)   # the three section-5d cells; cell 6490 is OUT (prereg 2.3)
DECLARED_PRIMALS = 16         # legs 1-2, 3-4, 5, 6, 7-16
END_TIME = 2500               # system/controlDict endTime
CASE_SUBDIR = "cbfs_beta"     # W4's case state -- NOT S1's cbfs_inv (prereg 3)
CAP_CORE_MIN = 150.0          # REGISTERED HARD CAP -- an overrun STOPS the arm (prereg 8.1)
EST_CORE_MIN = 133.230        # declared total: 116.400 inherited + 16.830 F_W addendum

# The accept floor, PINNED TO THE INSTRUMENT'S so imported_symbol_identity can
# assert this file grades against the object the control drives.
PRIMAL_MIN_RES_TOL = afc.PRIMAL_MIN_RES_TOL          # 1e-08
PRIMAL_MIN_RES_TOL_DIFF = afc.PRIMAL_MIN_RES_TOL_DIFF  # 100 (NOT 1000)
ACCEPT_FLOOR = afc.ACCEPT_FLOOR                       # 1e-06 = product (N-D43)

# The reference gradient is the arm's OWN new anchor8w gradient at 1e-8 (leg 5).
# The 1e-6 gradient cbfs_beta_grad.npy is REFUSED as reference (prereg 2.2) and
# is NEVER read by this comparator.
ANCHOR_GRAD_NAME = "anchor8w_grad.npy"
REFUSED_1E6_GRAD_MD5 = "06fe8c5097872496e8d1354624d19f03"   # cited, NEVER read

# Rule 4's field list for THIS family. CLAUDE.md rule 4 names the THERMAL
# family's fields; the incompressible DASimpleFoam analogue is below. The
# substitution is stated, not silently made.
FIELDS = ("U", "p", "k", "omega", "nut", "phi")

# The staged instruments (prereg 4.1). The comparator asserts, at grading, that
# the md5 of the STAGED COPY in this directory equals the registered source md5.
# A registration that hashes the source and grades the copy has checked nothing
# about what ran (prereg 4.3).
STAGED_INSTRUMENTS = {
    "runScript.py":     "565307ddfd2affd7184011f60834edd8",
    "run_one.sh":       "1b269bb9b95cafe5ce3945b9e665c5c3",
    "run_plateau.sh":   "e82b5569510a3d1ce2370edaafd92f87",
    "fd_beta_ones.npy": "661e027867ffa48d5b64297a5e990238",
}

# EVERY FILE THIS GRADING PATH EXECUTES OR IMPORTS. `frozen_path_coverage`
# EXTRACTS that set FROM THIS FILE'S OWN BYTES and REFUSES if this tuple does
# not contain it -- so the tuple is checkable rather than remembered (prereg 4,
# DAFOAM_CHARTER section 18.3). SO2a-DRIVER-DEF-1 is the reason.
ITEM_DIR_REL = "cases/dafoam/ladder-b/W4_reanchor"
FROZEN_PATHS = tuple("%s/%s" % (ITEM_DIR_REL, n) for n in (
    "analyse_w4_reanchor.py",
    "w4ra_accept_floor_control.py",
    "runScript.py",
    "run_one.sh",
    "run_plateau.sh",
    "fd_beta_ones.npy",
)) + ("cases/dafoam/ladder-b/W4_REANCHOR_PREREGISTRATION.md",)

# ---- THE NULL-TOKEN TABLE, REGISTERED BEFORE COMPUTE (prereg 10.4) ----------
# A bar or statistic derived from the run DOES NOT EXIST when its producing leg
# does not run. UNRESOLVED naming its missing producer is honest; a bare null is
# silence. `null_reading_coverage` refuses at FREEZE if a RUN_DERIVED quantity
# has no row here, or a row here names a quantity this file does not grade.
RUN_DERIVED = (
    "W1_5491", "W1_6740", "W1_12486", "F_W", "W0",
    "relerr_vs_adjoint", "sign_match", "stopping_iteration",
    "W2_tolerance_readback", "planted_zero", "counts",
)
NULL_READINGS = {
    "W1_5491": {"run_derived_quantity": "W1_5491",
                "producing_leg": "p025_5491_+-, p050_5491_+-",
                "token": "UNRESOLVED", "bar_state": "STATISTIC_NOT_PRODUCED",
                "bar_artefact": "log.p025_5491_*/log.p050_5491_*"},
    "W1_6740": {"run_derived_quantity": "W1_6740",
                "producing_leg": "p025_6740_+-, p050_6740_+-",
                "token": "UNRESOLVED", "bar_state": "STATISTIC_NOT_PRODUCED",
                "bar_artefact": "log.p025_6740_*/log.p050_6740_*"},
    "W1_12486": {"run_derived_quantity": "W1_12486",
                 "producing_leg": "p025_12486_+-, p050_12486_+-",
                 "token": "UNRESOLVED", "bar_state": "STATISTIC_NOT_PRODUCED",
                 "bar_artefact": "log.p025_12486_*/log.p050_12486_*"},
    "F_W": {"run_derived_quantity": "F_W",
            "producing_leg": "fw750_5491_+- AND p050_5491_+-",
            "token": "UNRESOLVED", "bar_state": "FALSIFIER_NOT_PRODUCED",
            "bar_artefact": "log.fw750_5491_*/log.p050_5491_*"},
    "W0": {"run_derived_quantity": "W0",
           "producing_leg": "anchor8w AND base8w",
           "token": "UNRESOLVED", "bar_state": "CONTROL_NOT_PRODUCED",
           "bar_artefact": "log.anchor8w/log.base8w"},
    "relerr_vs_adjoint": {"run_derived_quantity": "relerr_vs_adjoint",
                          "producing_leg": "anchor8w",
                          "token": "UNRESOLVED",
                          "bar_state": "REFERENCE_NOT_PRODUCED",
                          "bar_artefact": ANCHOR_GRAD_NAME},
    "sign_match": {"run_derived_quantity": "sign_match",
                   "producing_leg": "that cell's FD legs",
                   "token": "UNRESOLVED", "bar_state": "STATISTIC_NOT_PRODUCED",
                   "bar_artefact": "log.p0*_<cell>_*"},
    "stopping_iteration": {"run_derived_quantity": "stopping_iteration",
                           "producing_leg": "that leg",
                           "token": "UNRESOLVED", "bar_state": "LEG_NOT_PRODUCED",
                           "bar_artefact": "log.<tag>"},
    "W2_tolerance_readback": {"run_derived_quantity": "W2_tolerance_readback",
                              "producing_leg": "any leg's own log",
                              "token": "REFUSE", "bar_state": "REFUSE_NOT_UNRESOLVED",
                              "bar_artefact": "log.<tag>"},
    "planted_zero": {"run_derived_quantity": "planted_zero",
                     "producing_leg": "the objective parse",
                     "token": "REFUSE", "bar_state": "REFUSE_NOT_UNRESOLVED",
                     "bar_artefact": "log.<tag> (copy)"},
    "counts": {"run_derived_quantity": "counts",
               "producing_leg": "the ledger",
               "token": "REFUSE", "bar_state": "ALWAYS_PRODUCED",
               "bar_artefact": "ledger.csv"},
}

OBJ_RE = re.compile(r"^OBJ varianceU:\s*(\S+)\s*$")
TIME_RE = re.compile(r"^Time = (\S+)\s*$")
TOTRES_RE = re.compile(r"^Total Residual Norm2:\s*(\S+)\s*$")
# The success banner and the refusal banner. On THIS run path NEITHER prints
# (N-D43 CORRECTION), so their absence is FLOOR_STATE_UNREADABLE, never FLOOR_MET.
SATISFIED_RE = re.compile(r"satisfied the prescribed tolerance")
FAILED_RE = re.compile(r"Primal solution failed!")


class Refusal(Exception):
    """Raised for every condition on which this comparator refuses rather than degrades."""


def refuse(msg: str) -> "Refusal":
    return Refusal(msg)


def md5_of(path) -> str:
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


# --------------------------------------------------------------------- LOG PARSING
def parse_obj(path: Path) -> tuple[int, float]:
    """Return (line index of the LAST 'OBJ varianceU:' line, its value).

    The line INDEX is returned because prereg 7.5 requires the plant be applied
    'by line index in the parsed objective list' -- so the index is a parsed
    product, not something the planter recomputes for itself.
    """
    lines = Path(path).read_text(errors="replace").splitlines()
    hit = None
    for i, ln in enumerate(lines):
        m = OBJ_RE.match(ln)
        if m:
            hit = (i, float(m.group(1)))
    if hit is None:
        raise refuse(f"no 'OBJ varianceU:' line in {path} -- the objective was never printed")
    return hit


def log_facts(path: Path) -> dict:
    lines = Path(path).read_text(errors="replace").splitlines()
    ends = sum(1 for ln in lines if ln.strip() == "End")
    times = [m.group(1) for ln in lines if (m := TIME_RE.match(ln))]
    totres = [m.group(1) for ln in lines if (m := TOTRES_RE.match(ln))]
    txt = "\n".join(lines)
    return {
        "end_lines": ends,
        "last_time": times[-1] if times else None,
        "n_time_lines": len(times),
        "total_residual_norm2": float(totres[-1]) if totres else None,
        "satisfied_banner": bool(SATISFIED_RE.search(txt)),
        "failed_banner": bool(FAILED_RE.search(txt)),
    }


def ledger_rows(root: Path) -> dict:
    out: dict[str, dict] = {}
    p = Path(root) / "ledger.csv"
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
def completion(root: Path, tag: str, led: dict, task: str = "run_model") -> dict:
    """CLAUDE.md rule 4, all-or-nothing. Every clause is reported, pass or fail.

    Distinguishes PRODUCER_CRASHED (no OBJ line at all, the leg died) from
    RAN-BUT-MISSED (an OBJ line present, some rule-4 clause unsatisfied) -- prereg
    10.1 B4: collapsing the two is the third-outcome failure that branch prevents.
    """
    root = Path(root)
    log = root / f"log.{tag}"
    c: dict = {"tag": tag, "task": task, "clauses": {}, "notes": []}

    c["clauses"]["log_exists"] = log.exists()
    if not log.exists():
        c["complete"] = False
        c["bar_state"] = "PRODUCER_CRASHED"
        c["reason"] = "no log file -- the primal did not run (PRODUCER_CRASHED)"
        return c

    row = led.get(tag)
    c["clauses"]["ledger_row"] = row is not None
    c["clauses"]["rc_zero"] = bool(row and row["rc"] == 0)
    c["rc"] = row["rc"] if row else None
    c["wall_s"] = row["wall_s"] if row else None
    c["core_min"] = row["core_min"] if row else None
    c["ranks"] = row["ranks"] if row else None

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

    # THE AGE GUARD. 0/ was touched LAST at staging, so it dates the run allowed
    # to produce this answer. Every field at endTime must be NEWER than it.
    zero = root / CASE_SUBDIR / "0"
    zt = max((q.stat().st_mtime for q in zero.iterdir() if q.is_file()),
             default=None) if zero.exists() else None
    c["zero_mtime"] = zt
    c["min_field_mtime"] = min(mtimes) if mtimes else None
    c["clauses"]["age_guard"] = bool(mtimes and zt is not None and min(mtimes) > zt)

    c["complete"] = all(c["clauses"].values())
    if not c["complete"]:
        # A log that exists but printed no objective is a crash; a log with an
        # objective that misses a clause RAN but MISSED.
        c["bar_state"] = ("PRODUCER_CRASHED" if not c["clauses"]["objective_printed"]
                          else "RAN-BUT-MISSED")
        c["reason"] = "FAILED rule 4 clauses: " + ", ".join(
            k for k, v in c["clauses"].items() if not v)
    else:
        c["bar_state"] = "COMPLETE"
    # FLOOR-STATE, reported but NEVER inferred as FLOOR_MET (prereg 10.2, N-D43).
    if f["satisfied_banner"]:
        c["floor_state"] = "FLOOR_MET_BANNER_PRESENT"
    elif f["failed_banner"]:
        c["floor_state"] = "FLOOR_MISSED_BANNER_PRESENT"
    else:
        c["floor_state"] = "FLOOR_STATE_UNREADABLE"   # neither banner -- never FLOOR_MET
    return c


# ------------------------------------------------------------------ FD ARITHMETIC
def central(jp: float, jm: float, h: float) -> float:
    return (jp - jm) / (2.0 * h)


def relerr(fd: float, adj: float) -> float:
    return abs(fd - adj) / abs(adj)


def plateau_stat(d_lo: float, d_hi: float) -> float:
    """W1's statistic: |d(hi) - d(lo)| / |d(hi)|, denominator the GRADED step
    d(0.05) (prereg 7.1). An unstated denominator is a 9 % ambiguity in a 10 %
    bar, so it is fixed here to |d_hi|."""
    return abs(d_hi - d_lo) / abs(d_hi)


# ------------------------------------------------- FREEZE / COVERAGE (prereg 4)
def frozen_path_coverage() -> dict:
    """DAFOAM_CHARTER section 18.3, APPLIED TO THIS FILE BY EXTRACTION.

    Reads THIS FILE'S OWN BYTES with `ast`, collects every LOCAL module it
    imports and every instrument filename literal it names, and REFUSES if any
    is absent from `FROZEN_PATHS` or absent on disk. EXISTENCE IS ASSERTED
    FIRST AND SEPARATELY. It is the extraction, not the diligence, that binds.
    """
    import ast as _ast
    me = os.path.abspath(__file__)
    tree = _ast.parse(open(me, errors="replace").read(), filename=me)
    imported, literals = set(), set()
    LOCAL = ("w4ra_", "analyse_w4_")
    INSTR = tuple(STAGED_INSTRUMENTS)
    for node in _ast.walk(tree):
        if isinstance(node, _ast.Import):
            for a in node.names:
                if a.name.startswith(LOCAL):
                    imported.add(a.name + ".py")
        elif isinstance(node, _ast.ImportFrom) and node.module:
            if node.module.startswith(LOCAL):
                imported.add(node.module + ".py")
        elif isinstance(node, _ast.Constant) and isinstance(node.value, str):
            v = node.value
            if v in INSTR or (v.startswith(LOCAL) and v.endswith((".py", ".sh"))):
                literals.add(v)
    referenced = sorted(imported | literals)
    frozen_names = {p.rsplit("/", 1)[-1] for p in FROZEN_PATHS}
    out = {"extracted_from": os.path.basename(me),
           "imported_local_modules": sorted(imported),
           "named_instruments": sorted(literals),
           "n_referenced": len(referenced)}
    if not referenced:
        raise refuse(json.dumps({"FROZEN_PATH_COVERAGE": "the extraction found "
                     "NOTHING -- a derivation that quietly finds nothing is "
                     "indistinguishable from one that found nothing wrong "
                     "(rule 3)"}))
    absent = [n for n in referenced if not os.path.isfile(os.path.join(HERE, n))]
    unfrozen = [n for n in referenced if n not in frozen_names]
    out["absent_on_disk"] = absent
    out["referenced_but_not_in_FROZEN_PATHS"] = unfrozen
    if absent or unfrozen:
        raise refuse(json.dumps({"FROZEN_PATH_COVERAGE": out,
                     "note": "section 18.3: a registered gate whose implementing "
                             "file is not in the instrument table is UNIMPLEMENTED"}))
    out["coverage_complete"] = True
    return out


def null_reading_coverage() -> dict:
    """prereg 10.4, ASSERTED AT FREEZE. Every RUN_DERIVED quantity has a
    NULL_READINGS row; every NULL_READINGS row names a RUN_DERIVED quantity. A
    table drifted from the code is not evidence about the code."""
    missing = [k for k in RUN_DERIVED if k not in NULL_READINGS]
    extra = [k for k in NULL_READINGS if k not in RUN_DERIVED]
    REQUIRED = ("run_derived_quantity", "producing_leg", "token",
                "bar_state", "bar_artefact")
    incomplete = {k: [f for f in REQUIRED if not NULL_READINGS[k].get(f)]
                  for k in NULL_READINGS
                  if [f for f in REQUIRED if not NULL_READINGS[k].get(f)]}
    if missing or extra or incomplete:
        raise refuse(json.dumps({"NULL_READINGS": {
            "run_derived_without_a_registered_null_reading": missing,
            "registered_but_not_graded_by_this_file": extra,
            "rows_missing_a_required_field": incomplete}}))
    return {"n_run_derived": len(RUN_DERIVED), "n_registered": len(NULL_READINGS),
            "coverage_complete": True}


def imported_symbol_identity() -> dict:
    """prereg 4/7.5, MADE EXECUTABLE ON THE SYMBOL. The planted controls plant
    into THE LITERAL FUNCTION THE GATE CALLS, not a re-implementation, and the
    accept floor this file grades against IS the instrument's object."""
    import w4ra_accept_floor_control as _afc_again
    checks = {
        "afc.read_accept_floor is the gate's accept-floor reader":
            afc.read_accept_floor is _afc_again.read_accept_floor,
        "afc.run_floor_control defaults to that same reader":
            afc.run_floor_control.__defaults__[-1] is afc.read_accept_floor,
        "the accept floor this file grades against IS the instrument's":
            ACCEPT_FLOOR is afc.ACCEPT_FLOOR,
        "primalMinResTolDiff this file uses IS the instrument's (100, not 1000)":
            PRIMAL_MIN_RES_TOL_DIFF is afc.PRIMAL_MIN_RES_TOL_DIFF,
        "the plant control calls THIS module's parse_obj":
            planted_pass.__globals__["parse_obj"] is parse_obj,
        "the plant control calls THIS module's central":
            planted_pass.__globals__["central"] is central,
    }
    bad = [k for k, v in checks.items() if not v]
    if bad:
        raise refuse(json.dumps({"IMPORTED_SYMBOL_IDENTITY": bad,
                     "note": "a control that plants into a COPY of the reader "
                             "the gate calls controls nothing"}))
    return {k: bool(v) for k, v in checks.items()}


def staged_instrument_md5s() -> dict:
    """prereg 4.3. The STAGED copy's md5 must equal the registered source md5.
    A registration that hashes the source and grades the copy has checked
    nothing about what ran."""
    out = {}
    for name, reg in STAGED_INSTRUMENTS.items():
        p = os.path.join(HERE, name)
        if not os.path.isfile(p):
            raise refuse(json.dumps({"STAGED_INSTRUMENT": {"absent": name}}))
        got = md5_of(p)
        out[name] = {"staged_md5": got, "registered_md5": reg, "match": got == reg}
        if got != reg:
            raise refuse(json.dumps({"STAGED_INSTRUMENT": {
                "name": name, "staged_md5": got, "registered_md5": reg,
                "note": "the staged instrument is not the registered source"}}))
    return out


def freeze_check(paths) -> dict:
    """The frozen file IS the file that ran: disk == git blob at HEAD (rule 2)."""
    out = {}
    for rel in paths:
        disk = os.path.join(REPO, rel)
        if not os.path.isfile(disk):
            raise refuse(json.dumps({"FREEZE": {"absent_on_disk": rel}}))
        on_disk = md5_of(disk)
        try:
            blob = subprocess.run(["git", "-C", REPO, "cat-file", "blob",
                                   "HEAD:%s" % rel], stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, check=True).stdout
        except Exception as e:                                    # noqa: BLE001
            raise refuse(json.dumps({"FREEZE": {"git_cat_file_failed": rel,
                                                "error": repr(e)[:200]}}))
        committed = hashlib.md5(blob).hexdigest()
        out[rel] = {"on_disk_md5": on_disk, "committed_blob_md5_HEAD": committed,
                    "disk_equals_committed_blob": on_disk == committed}
        if on_disk != committed:
            raise refuse(json.dumps({"FREEZE": {"path": rel,
                         "on_disk_md5": on_disk, "committed_blob_md5_HEAD": committed,
                         "note": "the grading path is fixed at the pre-registration commit"}}))
    return out


# ------------------------------------------------------- THE W2 TOLERANCE GATE
def w2_accept_floor(root: Path, all_tags: list, ctrl_dir: Path) -> dict:
    """W2 (prereg 7.4). Read primalMinResTol / primalMinResTolDiff back out of
    EVERY leg's own log through the imported control, and REFUSE (exit 2) on any
    deviation. A reader that found nothing has not found agreement."""
    out = {"registered": {"primalMinResTol": PRIMAL_MIN_RES_TOL,
                          "primalMinResTolDiff": PRIMAL_MIN_RES_TOL_DIFF,
                          "accept_floor": ACCEPT_FLOOR},
           "per_leg": {}}
    seen_any = False
    for tag in all_tags:
        log = Path(root) / f"log.{tag}"
        if not log.exists():
            out["per_leg"][tag] = {"state": afc.NOT_EXERCISED, "log_absent": True}
            continue
        seen_any = True
        try:
            r = afc.run_floor_control(str(Path(ctrl_dir) / f"w2_{tag}"), str(log))
        except afc.AcceptFloorRefusal as e:
            raise refuse(json.dumps({"W2_ACCEPT_FLOOR": {"tag": tag,
                         "detail": json.loads(str(e)) if str(e).startswith("{") else str(e)[:400]}}))
        out["per_leg"][tag] = {"state": r["state"], "read": r["read"],
                               "accept_floor_unmoved": r["accept_floor_unmoved"]}
    if not seen_any:
        raise refuse(json.dumps({"W2_ACCEPT_FLOOR": "no leg log exists -- the "
                     "tolerance was not read from any leg. UNMEASURED, never "
                     "UNMOVED (prereg 10.4: W2 is a REFUSE, not an UNRESOLVED)"}))
    out["all_legs_unmoved"] = all(
        v.get("accept_floor_unmoved") for v in out["per_leg"].values()
        if v.get("state") == afc.EXERCISED_PASS)
    return out


# ------------------------------------------------------- THE PLANTED-ZERO CONTROL
def planted_pass(root: Path, tags: dict, tmp: Path) -> dict:
    """prereg 7.5 / CLAUDE.md rule 3.

    A comparator that reports agreement must first be shown able to report
    disagreement. PLANT is added RELATIVE to the + leg of cell 6740 ONLY, BY
    LINE INDEX in the parsed objective list, applied to a COPY, and RE-READ FROM
    DISK. It uses THE LITERAL parse_obj/central the FD gate calls.
    """
    root = Path(root)
    target_tag = tags[PLANT_CELL]["plus"]
    out = {"plant": PLANT, "cell": PLANT_CELL, "target_tag": target_tag,
           "copies": [], "run_artefacts_modified": False}

    for cell in CELLS:
        for sgn in ("plus", "minus"):
            t = tags[cell][sgn]
            src = root / f"log.{t}"
            dst = Path(tmp) / f"log.{t}"
            shutil.copy2(src, dst)
            out["copies"].append(str(dst))

    dst = Path(tmp) / f"log.{target_tag}"
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

    src_idx, src_val = parse_obj(root / f"log.{target_tag}")
    out["run_artefacts_modified"] = (src_val != orig)
    if out["run_artefacts_modified"]:
        raise refuse("the plant reached the RUN ARTEFACT. It must be applied to a COPY.")
    return out


# -------------------------------------------------------------------------- MAIN
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-root", default="/home/ubuntu/certonomous-runs/W4-reanchor")
    ap.add_argument("--json", default=None)
    ap.add_argument("--skip-freeze", action="store_true",
                    help="skip the disk==HEAD git check (for the fixture drive only)")
    a = ap.parse_args()
    root = Path(a.run_root)

    import numpy as np

    R: dict = {"registration": {
        "path": "cases/dafoam/ladder-b/W4_REANCHOR_PREREGISTRATION.md",
        "cells": list(CELLS), "s_hi": S_HI, "s_lo": S_LO, "h_f": H_F,
        "w1_bar": W1_BAR, "falsifier_pred_pct_dhi": FALSIFIER_PRED_PCT_DHI,
        "primalMinResTol": PRIMAL_MIN_RES_TOL,
        "primalMinResTolDiff": PRIMAL_MIN_RES_TOL_DIFF,
        "accept_floor": ACCEPT_FLOOR,
        "cap_core_min": CAP_CORE_MIN, "estimate_core_min": EST_CORE_MIN}}

    print("=" * 78)
    print("W4 CBFS RE-ANCHOR -- FROZEN COMPARATOR (derived from S1FDP 5f55c742)")
    print("accept floor 1e-8 x 100 = 1e-6 (N-D43: the PRODUCT; diff is 100 NOT 1000)")
    print("=" * 78)

    # --------------------------- 0. FREEZE / COVERAGE / STAGED INSTRUMENTS
    print("\n[0] FREEZE + COVERAGE + STAGED-INSTRUMENT md5s")
    R["frozen_path_coverage"] = frozen_path_coverage()
    R["null_reading_coverage"] = null_reading_coverage()
    R["imported_symbol_identity"] = imported_symbol_identity()
    R["staged_instruments"] = staged_instrument_md5s()
    print(f"      frozen_path_coverage: {R['frozen_path_coverage']['n_referenced']} "
          f"referenced, all in FROZEN_PATHS and on disk")
    print(f"      null_reading_coverage: {R['null_reading_coverage']['n_run_derived']} "
          f"run-derived quantities, all have a registered null reading")
    print(f"      imported_symbol_identity: all {len(R['imported_symbol_identity'])} "
          f"identity checks hold (the plant plants into the gate's own functions)")
    for n, v in R["staged_instruments"].items():
        print(f"      staged {n:<20} md5 {v['staged_md5']} == registered  {'OK' if v['match'] else 'MISMATCH'}")
    if a.skip_freeze:
        print("      freeze_check: SKIPPED (--skip-freeze; fixture drive only)")
        R["freeze"] = {"skipped": True}
    else:
        R["freeze"] = freeze_check(FROZEN_PATHS)
        print(f"      freeze_check: disk == HEAD blob for all {len(FROZEN_PATHS)} frozen paths")

    # ----------------------------------------------------- tags & ledger
    tags = {c: {"plus": f"p025_{c}_plus", "minus": f"p025_{c}_minus"} for c in CELLS}
    hi_tags = {c: {"plus": f"p050_{c}_plus", "minus": f"p050_{c}_minus"} for c in CELLS}
    ftags = {"plus": "fw750_5491_plus", "minus": "fw750_5491_minus"}
    ANCHOR_TAG, BASE_TAG = "anchor8w", "base8w"
    fd_tags = [tags[c][s] for c in CELLS for s in ("plus", "minus")] + \
              [hi_tags[c][s] for c in CELLS for s in ("plus", "minus")]
    all_tags = [ftags["plus"], ftags["minus"], ANCHOR_TAG, BASE_TAG] + fd_tags
    led = ledger_rows(root)

    # ------------------------------------------ 1. W2, before grading anything
    print("\n[1] W2 -- TOLERANCE READBACK from EVERY leg's own log (imported control)")
    with tempfile.TemporaryDirectory(prefix="w4ra_w2_") as w2td:
        w2 = w2_accept_floor(root, all_tags, w2td)
    R["w2_accept_floor"] = w2
    exercised = [t for t, v in w2["per_leg"].items() if v.get("state") == afc.EXERCISED_PASS]
    print(f"      registered  tol={PRIMAL_MIN_RES_TOL:g}  diff={PRIMAL_MIN_RES_TOL_DIFF:g}  "
          f"floor={ACCEPT_FLOOR:g}   read back unmoved on {len(exercised)}/{len(all_tags)} legs")

    # -------------------------------- 2. the anchor gradient (arm's OWN, 1e-8)
    anchor_npy = root / ANCHOR_GRAD_NAME
    if not anchor_npy.exists():
        raise refuse(f"the arm's own 1e-8 reference gradient {anchor_npy} is absent -- "
                     f"the anchor8w leg did not produce it (REFERENCE_NOT_PRODUCED)")
    g = np.load(anchor_npy)
    adj = {c: float(g[c]) for c in CELLS}
    print(f"\n[2] anchor gradient (arm's OWN anchor8w at 1e-8)  {anchor_npy}  md5 {md5_of(anchor_npy)}")
    print(f"      NOT the refused 1e-6 gradient (md5 {REFUSED_1E6_GRAD_MD5}, prereg 2.2 -- NOT READ)")
    for c in CELLS:
        print(f"      J_adj[{c}] = {adj[c]:.12e}")
    R["anchor_gradient"] = {"path": str(anchor_npy), "md5": md5_of(anchor_npy),
                            "per_cell": {str(c): adj[c] for c in CELLS}}

    # --------------------------------------------------- 3. rule 4 completion
    comp = {t: completion(root, t, led,
                          task=("compute_totals" if t == ANCHOR_TAG else "run_model"))
            for t in all_tags}
    executed = [t for t in all_tags if comp[t]["complete"]]
    blocked = [t for t in all_tags if not comp[t]["complete"]]
    print(f"\n[3] RULE 4 STRICT COMPLETION -- declared {DECLARED_PRIMALS}, "
          f"executed {len(executed)}, blocked {len(blocked)}")
    print(f"      field list for this family: {' '.join(FIELDS)}  "
          f"(rule 4 names the THERMAL family's fields; this is the DASimpleFoam analogue)")
    for t in all_tags:
        c = comp[t]
        bad = [k for k, v in c["clauses"].items() if not v]
        print(f"      {t:<22} {'COMPLETE' if c['complete'] else c['bar_state']:<20}  "
              f"rc={c.get('rc')} last_time={c.get('last_time')} "
              f"core_min={c.get('core_min')} floor={c.get('floor_state')}"
              + (f"  FAILED: {','.join(bad)}" if bad else ""))
    R["completion"] = comp
    R["counts"] = {"declared": DECLARED_PRIMALS, "executed": len(executed),
                   "blocked": len(blocked)}
    if DECLARED_PRIMALS != len(executed) + len(blocked):
        raise refuse("declared != executed + blocked -- the program accounting is broken")

    # ------------------------------------------ 4. W0 base-consistency control
    print("\n[4] W0 -- base consistency: OBJ varianceU(anchor8w) == OBJ varianceU(base8w), 16 digits")
    w0 = {"run": False}
    if comp[ANCHOR_TAG]["complete"] and comp[BASE_TAG]["complete"]:
        oa = comp[ANCHOR_TAG]["obj"]
        ob = comp[BASE_TAG]["obj"]
        equal = (repr(oa) == repr(ob))
        w0 = {"run": True, "anchor_obj": oa, "base_obj": ob, "equal_16_digits": equal}
        print(f"      anchor8w OBJ {oa!r}   base8w OBJ {ob!r}   -> "
              f"{'EQUAL' if equal else 'NOT EQUAL'}")
        if not equal:
            R["w0"] = w0
            R["verdict"] = {"item_token": "NOT A RESULT",
                            "reason": "W0 base consistency failed: the reference "
                                      "gradient and the FD baseline are different states"}
            _emit(R, a.json)
            raise refuse("W0 FAILED: anchor8w and base8w disagree -- no FD number is "
                         "graded against a gradient computed from a different state")
    else:
        w0 = {"run": False, "reason": "anchor8w or base8w not rule-4 complete",
              "token": "UNRESOLVED", "bar_state": "CONTROL_NOT_PRODUCED"}
        print("      UNRESOLVED (CONTROL_NOT_PRODUCED): anchor8w or base8w did not complete")
    R["w0"] = w0

    # --------------------------------- 5. THE PLANTED-ZERO CONTROL (rule 3)
    print(f"\n[5] PLANTED-ZERO CONTROL -- PLANT = {PLANT:.6e} relative into the + leg of "
          f"cell {PLANT_CELL} ONLY, by line index, re-read from disk, on a COPY")
    fd_ok = all(comp[tags[c][s]]["complete"] and comp[hi_tags[c][s]]["complete"]
                for c in CELLS for s in ("plus", "minus"))
    if not fd_ok:
        print("      NOT RUN: not every FD leg is rule-4 complete, so there is nothing "
              "to grade and nothing for the control to protect.")
        R["plant"] = {"run": False, "reason": "FD legs incomplete"}
    else:
        with tempfile.TemporaryDirectory(prefix="w4ra_plant_") as td:
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
            print(f"      observed delta {observed:.12e}   implied by the plant {implied:.12e}")
            if observed == 0.0:
                raise refuse("THE PLANT WAS NOT SEEN: cell 6740 did not move. A zero from a "
                             "reader not shown able to see a non-zero is not evidence. NOTHING IS GRADED.")
            if abs(observed - implied) > 1e-9 * abs(implied):
                raise refuse(f"the plant moved cell {PLANT_CELL} by {observed:.12e}, not by the "
                             f"implied {implied:.12e}. NOTHING IS GRADED.")
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

    # --------------------------------------------------------- 6. F_W first
    print(f"\n[6] F_W -- the registered trivial baseline: cell {FALSIFIER_CELL} at h_F = {H_F}")
    print(f"      REGISTERED PREDICTION (not recomputed): plateau statistic vs |d(0.05)| "
          f"= {FALSIFIER_PRED_PCT_DHI} % > {W1_BAR*100:.0f} %  -> FAILS W1")
    armf_ok = (comp[ftags["plus"]]["complete"] and comp[ftags["minus"]]["complete"]
               and comp[hi_tags[FALSIFIER_CELL]["plus"]]["complete"]
               and comp[hi_tags[FALSIFIER_CELL]["minus"]]["complete"])
    fal: dict = {"complete": armf_ok, "named_gate": "W1",
                 "registered_prediction_pct_dhi": FALSIFIER_PRED_PCT_DHI,
                 "registered_prediction_pct_dhf": FALSIFIER_PRED_PCT_DHF}
    if armf_ok:
        jp = parse_obj(root / f"log.{ftags['plus']}")[1]
        jm = parse_obj(root / f"log.{ftags['minus']}")[1]
        d_f = central(jp, jm, H_F)
        # d(0.05) for the falsifier cell, from THIS arm's own p050_5491 legs
        hp = parse_obj(root / f"log.{hi_tags[FALSIFIER_CELL]['plus']}")[1]
        hm = parse_obj(root / f"log.{hi_tags[FALSIFIER_CELL]['minus']}")[1]
        d_hi_5491 = central(hp, hm, S_HI)
        stat_dhi = plateau_stat(d_f, d_hi_5491)          # |d(h_F) - d(0.05)| / |d(0.05)|
        stat_dhf = abs(d_hi_5491 - d_f) / abs(d_f)        # alternative denominator |d(h_F)|
        # THE WITHDRAWAL TEST: does the WRONG STEP PASS W1's 10 % bar?
        passes_w1 = stat_dhi <= W1_BAR
        fal.update({"d_hf": d_f, "d_hi_5491": d_hi_5491,
                    "measured_stat_pct_dhi": stat_dhi * 100.0,
                    "measured_stat_pct_dhf": stat_dhf * 100.0,
                    "falsifier_passes_w1": passes_w1,
                    "prediction_met": (not passes_w1),   # predicted to FAIL the bar
                    "sign_match": (d_f > 0) == (adj[FALSIFIER_CELL] > 0)})
        print(f"      MEASURED  d(h_F=0.75) = {d_f:.12e}   d(0.05) = {d_hi_5491:.12e}")
        print(f"      MEASURED  plateau statistic vs |d(0.05)| = {stat_dhi*100:.4f} %  "
              f"(registered prediction {FALSIFIER_PRED_PCT_DHI} %)  -> "
              f"{'FAILS W1 as predicted' if not passes_w1 else 'PASSES W1 -- DISCRIMINATION FAILURE'}")
        print(f"      MEASURED  alternative denominator |d(h_F)| = {stat_dhf*100:.4f} %  "
              f"(registered prediction {FALSIFIER_PRED_PCT_DHF} %)")
    else:
        fal["token"] = "UNRESOLVED"
        fal["bar_state"] = "FALSIFIER_NOT_PRODUCED"
        print("      UNRESOLVED (FALSIFIER_NOT_PRODUCED): the falsifier legs (fw750_5491 "
              "and p050_5491) did not all complete. W1 cannot be read (prereg 10.4 precondition).")
    R["f_w"] = fal

    # ------------------------------------------------------------- 7. GATE W1
    print(f"\n[7] W1 -- |d({S_HI}) - d({S_LO})| / |d({S_HI})| <= {W1_BAR*100:.0f} %, PER COMPONENT")
    w1: dict = {}
    for c in CELLS:
        tp, tm = tags[c]["plus"], tags[c]["minus"]
        hp, hm = hi_tags[c]["plus"], hi_tags[c]["minus"]
        legs_ok = all(comp[t]["complete"] for t in (tp, tm, hp, hm))
        if not armf_ok:
            # PRECONDITION: F_W unresolved -> every W1 component UNRESOLVED (prereg 10.4)
            w1[c] = {"token": "UNRESOLVED", "bar_state": "STATISTIC_NOT_PRODUCED",
                     "reason": "F_W is UNRESOLVED, so the withdrawal question is "
                               "unsettled and W1 cannot be read (precondition)"}
            print(f"      cell {c}: UNRESOLVED -- F_W is UNRESOLVED (precondition unmet)")
            continue
        if not legs_ok:
            w1[c] = {"token": "UNRESOLVED", "bar_state": "STATISTIC_NOT_PRODUCED",
                     "reason": "an FD leg for this cell is not rule-4 complete"}
            print(f"      cell {c}: UNRESOLVED (STATISTIC_NOT_PRODUCED) -- FD leg incomplete")
            continue
        jp = parse_obj(root / f"log.{tp}")[1]
        jm = parse_obj(root / f"log.{tm}")[1]
        d_lo = central(jp, jm, S_LO)
        Hp = parse_obj(root / f"log.{hp}")[1]
        Hm = parse_obj(root / f"log.{hm}")[1]
        d_hi = central(Hp, Hm, S_HI)
        move = plateau_stat(d_lo, d_hi)
        inside = move <= W1_BAR
        w1[c] = {
            "d_lo": d_lo, "d_hi": d_hi, "w1_move": move, "inside_bar": inside,
            "relerr_lo": relerr(d_lo, adj[c]), "relerr_hi": relerr(d_hi, adj[c]),
            "sign_match_lo": (d_lo > 0) == (adj[c] > 0),
            "sign_match_hi": (d_hi > 0) == (adj[c] > 0),
            "stopping_iteration_lo_plus": comp[tp]["last_time"],
            "stopping_iteration_hi_plus": comp[hp]["last_time"],
            "token": "PASS" if inside else "NOT A RESULT",
            "bar_state": "PRODUCED",
        }
        print(f"      cell {c}: d({S_LO}) = {d_lo:.12e}   d({S_HI}) = {d_hi:.12e}")
        print(f"               W1 move = {move*100:.4f} %  bar {W1_BAR*100:.0f} %  -> {w1[c]['token']}")
        print(f"               rel.err vs anchor8w: {w1[c]['relerr_lo']*100:.4f} % at {S_LO}, "
              f"{w1[c]['relerr_hi']*100:.4f} % at {S_HI}  (reported, no gate attached)")
    R["w1"] = w1

    # ---------------------- 8. the registered consequence, applied mechanically
    withdrawn = bool(fal.get("falsifier_passes_w1"))
    if armf_ok and withdrawn:
        print("\n[8] REGISTERED CONSEQUENCE (prereg 7.3): the deliberately wrong step PASSED "
              "W1's bar, so W1's VERDICT IS WITHDRAWN FOR EVERY COMPONENT.")
        for c in CELLS:
            if w1[c].get("token") in ("PASS", "NOT A RESULT"):
                w1[c]["token"] = "NOT A RESULT"
                w1[c]["withdrawn_by_falsifier"] = True
    elif armf_ok:
        print("\n[8] REGISTERED CONSEQUENCE: not triggered -- the wrong step does not pass "
              "W1's bar, so the gate discriminates step quality.")
    else:
        print("\n[8] REGISTERED CONSEQUENCE: UNRESOLVED -- F_W did not produce, so the "
              "withdrawal question is unsettled and every W1 reads UNRESOLVED.")
    R["falsifier_withdrawal"] = withdrawn

    # --------------------------------------- 9. sign-flip duty (separate)
    print("\n[9] SIGN-FLIP DUTY (VERIFICATION_CHARTER section 7 step 3, separate from W1)")
    for c in CELLS:
        if "d_lo" not in w1.get(c, {}) or "d_hi" not in w1.get(c, {}):
            continue
        move = abs(w1[c]["d_hi"] - w1[c]["d_lo"]) / abs(w1[c]["d_hi"])
        flag = (not w1[c]["sign_match_hi"]) or move > SIGNFLIP_MOVE
        w1[c]["signflip_flag"] = flag
        print(f"      cell {c}: move {move*100:.2f} % of own magnitude, sign "
              f"{'MATCHES' if w1[c]['sign_match_hi'] else 'FLIPS'} -> {'FLAGGED' if flag else 'not flagged'}")

    # -------------------------------------------------------------- 10. cost, rule 12
    spent = sum(v["core_min"] for v in led.values())
    over = spent > CAP_CORE_MIN
    print(f"\n[10] RULE 12 -- registered estimate {EST_CORE_MIN} core-min, HARD CAP "
          f"{CAP_CORE_MIN}, ACTUAL {spent:.3f} core-min "
          f"(ratio actual/predicted {spent/EST_CORE_MIN:.4f} if EST>0)")
    # billing convention: --cpus=2, wall_s x 2 / 60 (prereg 5.3, PROVISIONAL pending
    # Sanaa's rule-12 unit ruling F7). Assert --cpus == ranks used to bill (prereg 11.2).
    ranks_seen = sorted({v["ranks"] for v in led.values()}) if led else []
    print(f"      billing convention: --cpus=2 (wall_s x 2 / 60), PROVISIONAL pending "
          f"the rule-12 unit ruling (prereg F7); ranks-in-ledger seen: {ranks_seen}")
    if ranks_seen and ranks_seen != [2]:
        raise refuse(f"the ledger bills at ranks {ranks_seen}, not the registered [2]. "
                     f"prereg 11.2: --cpus must equal the billing multiplier or the cap "
                     f"is not the cap it says it is.")
    print(f"      derived $ at the owner-stated c7a.4xlarge rate $0.0513/core-h: "
          f"${spent/60*0.0513:.4f}  [DERIVED, NOT MEASURED -- the box cannot read its own billing]")
    stalls = [t for t, v in led.items() if v["wall_s"] > 3600]
    print(f"      rows over 3600 wall s (stalls): {stalls if stalls else 'none'}")
    print(f"      CAP {'EXCEEDED -- THE ARM STOPS' if over else 'respected'}")
    R["cost"] = {"estimate_core_min": EST_CORE_MIN, "cap_core_min": CAP_CORE_MIN,
                 "actual_core_min": spent, "ratio": (spent / EST_CORE_MIN) if EST_CORE_MIN else None,
                 "derived_usd": spent / 60 * 0.0513, "cap_exceeded": over,
                 "ranks_in_ledger": ranks_seen, "stalled_rows": stalls,
                 "cost_basis": "core-minutes MEASURED from this arm's own ledger.csv on the "
                               "--cpus=2 convention (prereg 5.3, PROVISIONAL/REFERRED); the "
                               "dollar figure is DERIVED at the owner-stated rate, NOT MEASURED"}

    # ------------------------------------------------------------- 11. THE VERDICT
    print("\n" + "=" * 78)
    print("VERDICT -- produced by this frozen path, not composed by hand")
    print("=" * 78)
    if blocked:
        item = "BLOCKED"
        why = (f"{len(blocked)} of {DECLARED_PRIMALS} declared primals are not rule-4 "
               f"complete ({', '.join(blocked)}). prereg 9.3: any blocked > 0 forces the "
               f"arm's token to NOT A RESULT or BLOCKED. No success-reading token over a "
               f"short program.")
    elif not armf_ok:
        item = "NOT A RESULT"
        why = ("F_W did not produce, so the withdrawal question is unsettled and every W1 "
               "reads UNRESOLVED (prereg 10.4 precondition).")
    elif withdrawn:
        item = "NOT A RESULT"
        why = ("the registered falsifier at h_F = 0.75 PASSED W1's 10 % bar, so W1's verdict "
               "is withdrawn for every component (prereg 7.3).")
    elif all(w1[c]["token"] == "PASS" for c in CELLS):
        item = "PASS"
        why = ("all three components sit inside the registered 10 % plateau bar, the "
               "falsifier failed the bar as predicted, W0 held, and the planted zero was seen.")
    else:
        outside = [c for c in CELLS if w1[c]["token"] != "PASS"]
        item = "NOT A RESULT"
        why = (f"component(s) {outside} miss the 10 % plateau bar. Registered label: NOT A "
               f"RESULT, not GATE FAIL -- a failed plateau does not show the adjoint wrong, "
               f"it shows the FD estimate not to be a measurement of the derivative.")
    print(f"\nITEM TOKEN: {item}")
    print(f"REASON:     {why}")
    for c in CELLS:
        print(f"  cell {c}: {w1[c].get('token')}")
    if armf_ok:
        print(f"  F_W (h_F={H_F}): measured {fal['measured_stat_pct_dhi']:.4f} % vs registered "
              f"prediction {FALSIFIER_PRED_PCT_DHI} % -> "
              f"{'MET (fails W1)' if fal['prediction_met'] else 'NOT MET (passes W1)'}")
    print(f"  cost: {spent:.3f} core-min actual vs {EST_CORE_MIN} registered, cap {CAP_CORE_MIN}")
    R["verdict"] = {"item_token": item, "reason": why,
                    "per_cell": {str(c): w1[c].get("token") for c in CELLS}}

    _emit(R, a.json)
    return 0


def _emit(R: dict, jpath) -> None:
    if jpath:
        Path(jpath).write_text(json.dumps(R, indent=2, default=str))
        print(f"\nmachine record: {jpath}")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Refusal as e:
        print("\n" + "!" * 78, file=sys.stderr)
        print("COMPARATOR REFUSES (exit 2). NOTHING IS GRADED.", file=sys.stderr)
        print(f"REASON: {e}", file=sys.stderr)
        print("!" * 78, file=sys.stderr)
        sys.exit(2)
