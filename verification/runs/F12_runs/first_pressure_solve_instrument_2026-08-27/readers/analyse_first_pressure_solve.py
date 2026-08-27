#!/usr/bin/env python3
"""F12 ARM E -- THE FIRST PRESSURE SOLVE.  READER.

Scores the SIX registered predictions PE1-PE6 of
verification/campaign/F12_FIRST_PRESSURE_SOLVE_PREREGISTRATION.md
(frozen at commit 86af0a31, blob 2bb885c6c969f70e21551ec479a0742ae9f953eb,
frozen body = lines 1-176,
sha256 ac6a74e3259eac7e779f970315bc16411b0e8b0a981e372e822689dbfe806788)
and REGISTERS NO PREDICTION FOR PE7, exactly as frozen.

THIS ARM GRADES NOTHING.  It holds no gate, no threshold of its own and no
band.  Every constant below is QUOTED from the freeze; this file originates
none of them.  It therefore emits NO WORD OF THE FIXED VERDICT VOCABULARY --
not PASS, not GATE REACHED, not GATE FAIL, not NOT A RESULT, not BLOCKED, not
PENDING.  A registered prediction is reported HELD or NOT HELD; a control is
reported FIRED or DID NOT FIRE.  F12 rung 1 stands NOT A RESULT and rungs 2-5
stand BLOCKED by records this reader neither reads nor touches, and rung 2's
rate_calibration_gate() interlock is not invoked, not imported and not read
around here.

-----------------------------------------------------------------------------
THE 30-SECOND PER-ARM TIMEOUT IS A HANG DETECTOR, NOT A BUDGET TRACKER.
-----------------------------------------------------------------------------
Registered estimate 0.0795 core-min, registered cap 0.50 core-min, ratio 6.3x.
Section 6 of the freeze states openly WHY the ratio is not slack: ClockTime has
integer-second resolution, so quantisation alone is +/-0.0167 core-min per arm
= 42% of the whole estimate, and a 1.5x cap on a five-second arm would abort on
rounding.  Do not read the 6.3x as sloppy costing.  The cap is never raised.
-----------------------------------------------------------------------------

E2's CONFIGURATION IS A MEASUREMENT INSTRUMENT AND MAY NEVER BE CARRIED INTO
ANY GRADED RUN.  This reader refuses to score an E2 whose recorded case path
does not carry the token E2_INSTRUMENT_NEVER_GRADE, and refuses to score an E2
whose DO_NOT_GRADE marker is absent from the evidence.

CONTROLS (standing rule 3, and section 5 of the freeze).  Each is shown able to
REFUSE (exit 2), never to degrade:
  C1 PLANTED ZERO   a known value planted into a COPY of the written time-1 p
                    ON DISK, read back THROUGH THE REAL READER, required at the
                    EXACT planted cell index.  A zero from a reader not shown
                    able to see a non-zero is not evidence.
  C2 KNOWN NON-ZERO the reader independently derives the bounds from rung 1's
                    own 0/p and fvSolution factors and reproduces 10132.5 /
                    202650 and the 6,914 count.
  C3 LEVER EFFECT   E2's written p must DIFFER from E1's.  An arm whose output
                    equals its control did not exercise its lever.
  C4 MESH IDENTITY  both arms' polyMesh {points,faces,owner,neighbour} hash
                    identical to rung 1's.
  C5 DICT IDENTITY  E1 18/18 byte-identical; E2 17/18 with the ONE difference
                    being system/fvSolution, in exactly two deleted lines.
  C6 RUNG 1 UNTOUCHED  rung-1 fingerprint before == after; rungs 2-5 absent.
Plus the CLAUDE.md rule-4 STRICT COMPLETION RULE on each arm, INCLUDING THE AGE
GUARD, checked BEFORE any prediction is scored.

NO `assert` STATEMENT APPEARS IN THIS FILE.  Assertions vanish under
`python3 -O`, and a control that can be switched off by an interpreter flag is
not a control.  Under -O this module BAILS WITH rc 2 at module entry, below.

`--selftest` drives EVERY registered control and EVERY registered prediction to
BOTH a passing and a failing value through the real reader, on synthetic
fixtures written to disk.  A control that can only pass is not a control.

Exit codes:  0 every prediction held and every control fired
             1 the reader spoke, and at least one registered prediction DID NOT
               HOLD (a measurement outcome, not a refusal)
             2 REFUSED -- a control did not fire, an input was missing, the
               strict completion rule failed, or the interpreter was -O
"""
import sys

if not __debug__:
    sys.stderr.write(
        "REFUSED (rc 2): this reader was started under `python3 -O`.  Assertions\n"
        "vanish under -O, so this file uses none; it bails here at module entry\n"
        "rather than run with any check silently disabled.\n")
    raise SystemExit(2)

import json
import math
import os
import pathlib
import re
import shutil

NUM = r"[-+0-9.eE]+"

# ===========================================================================
# REGISTERED CONSTANTS -- every one QUOTED from the freeze.  None originates here.
# ===========================================================================
FROZEN_COMMIT = "86af0a31"
FROZEN_BLOB = "2bb885c6c969f70e21551ec479a0742ae9f953eb"
FROZEN_BODY_LINES = 176
FROZEN_BODY_SHA256 = "ac6a74e3259eac7e779f970315bc16411b0e8b0a981e372e822689dbfe806788"

# section 4, PE1 -- rung 1's iteration-1 log, digit for digit
PE1 = {
    "Ux_initial": "0.9999999533",
    "Uy_initial": "0.9999999583",
    "e_initial": "0.9999999059",
    "p1_initial": "1",
    "p1_final": "0.009729218448",
    "p1_iters": "47",
    "p2_initial": "0.00077669948",
    "p2_final": "6.945700699e-06",
    "p2_iters": "28",
    "cont_sum_local": "8.216163968e-05",
    "cont_global": "1.981380643e-05",
}
# section 4, PE2 / PE3 ; section 2, the case's own registered bounds
PE2_AT_BOUND = 6914
N_CELLS = 23040
P_REF = 101325.0
PMINFACTOR = 0.1
PMAXFACTOR = 2.0
FLOOR = P_REF * PMINFACTOR          # 10132.5 Pa
CEIL = P_REF * PMAXFACTOR           # 202650.0 Pa
# section 4, PE4 -- the iteration-1 pressureControl pre-clip print
PE4_MIN = -411376.774
PE4_MAX = 2974458.981
PE4_PRINT_DP = 3                    # "to its printed digits"
# section 4, PE6 -- the radius the frozen field-localisation probe measured
PE6_R_MAX = 0.836
QC = (0.25, 0.0)
CHORD = 1.0
# section 2 -- endTime, and the fields the freeze names as written at time 1
END_TIME = 1
REQUIRED_FIELDS = ("p", "U", "T", "rho", "phi")
# section 6 -- cost, in the lab's unit
REGISTERED_ESTIMATE_CORE_MIN = 0.0795
REGISTERED_CAP_CORE_MIN = 0.50
HANG_DETECTOR_WALL_S = 30
RATE_USD_PER_CORE_H = 0.0513       # reported-by-owner; DERIVED dollars only

# the plant.  The freeze requires the value to come back at THE EXACT planted
# cell index; it names no particular index, so this reader pins one and holds
# itself to exactness at it.
PLANT_VALUE = -7.654321e+09
PLANT_CELL = 12345
E2_TOKEN = "E2_INSTRUMENT_NEVER_GRADE"


class Refused(Exception):
    """Raised wherever this reader would otherwise have to degrade."""


def refuse(msg):
    raise Refused(msg)


def must_read(path):
    p = pathlib.Path(path)
    if not p.is_file():
        refuse(f"REFUSED: required input is missing: {p}")
    txt = p.read_text(errors="replace")
    if txt.strip() == "":
        refuse(f"REFUSED: required input is empty: {p}")
    return txt


# ===========================================================================
# OpenFOAM ascii field reading -- the ONE code path.  The plant is read back
# through exactly this, never through a shortcut.
# ===========================================================================
def _strip(txt):
    txt = re.sub(r"/\*.*?\*/", "", txt, flags=re.S)
    return re.sub(r"//[^\n]*", "", txt)


def _block(txt, start):
    i = txt.index("(", start)
    d, j = 0, i
    while True:
        if txt[j] == "(":
            d += 1
        elif txt[j] == ")":
            d -= 1
            if d == 0:
                return txt[i + 1:j], j + 1
        j += 1


def _vals(body, vector):
    if vector:
        return [tuple(float(x) for x in m)
                for m in re.findall(rf"\(\s*({NUM})\s+({NUM})\s+({NUM})\s*\)", body)]
    return [float(x) for x in re.findall(rf"(?<![\w.)])({NUM})(?![\w.])", body)]


def read_internal(path):
    """-> list of floats (scalar) or 3-tuples (vector), the internalField only."""
    txt = _strip(must_read(path))
    vector = "volVectorField" in txt
    m = re.search(rf"internalField\s+nonuniform[^;(]*?(\d+)\s*\(", txt)
    if not m:
        refuse(f"REFUSED: {path} has no nonuniform internalField list -- this "
               f"reader will not guess at a uniform field")
    body, _ = _block(txt, m.end() - 1)
    vals = _vals(body, vector)
    if not vals:
        refuse(f"REFUSED: {path} internalField list parsed to zero values")
    return vals


def plant_into_copy(src, dst, cell, value):
    """Write a copy of `src` at `dst` with cell index `cell` set to `value`.
    Positional replacement by token index -- NEVER by matching the old value."""
    txt = _strip(must_read(src))
    m = re.search(rf"internalField\s+nonuniform[^;(]*?(\d+)\s*\(", txt)
    if not m:
        refuse(f"REFUSED: cannot plant into {src}: internalField is not nonuniform")
    body, _ = _block(txt, m.end() - 1)
    count, new_body = 0, None
    for mt in re.finditer(rf"(?<![\w.)])({NUM})(?![\w.])", body):
        if count == cell:
            new_body = body[:mt.start()] + repr(value) + body[mt.end():]
            break
        count += 1
    if new_body is None:
        refuse(f"REFUSED: plant cell {cell} is out of range in {src}")
    pathlib.Path(dst).write_text(txt.replace(body, new_body, 1))


# ===========================================================================
# CLAUDE.md rule 4 -- THE STRICT COMPLETION RULE, all-or-nothing, INCLUDING
# THE AGE GUARD.  Checked BEFORE any prediction is scored.  Every limb must
# hold; a run that fails any clause is not done and this reader refuses.
# ===========================================================================
def strict_completion_rule(ev, arm):
    """-> dict of limbs.  Every value True, or the arm is not complete."""
    d = pathlib.Path(ev) / arm
    limbs, detail = {}, {}

    rc_txt = must_read(d / "RC.txt").strip()
    limbs["rc_zero"] = (rc_txt == "0")
    detail["rc"] = rc_txt

    log = must_read(d / "log.rhoSimpleFoam")
    limbs["end_line"] = bool(re.search(r"^End\s*$", log, re.M))

    times = [int(m.group(1)) for m in re.finditer(r"^Time = (\d+)\s*$", log, re.M)]
    limbs["last_time_is_endTime"] = bool(times) and times[-1] == END_TIME
    detail["last_time"] = times[-1] if times else None

    n_exec = len(re.findall(r"^ExecutionTime = ", log, re.M))
    limbs["executiontime_count_is_endTime"] = (n_exec == END_TIME)
    detail["executiontime_count"] = n_exec

    present = [f for f in REQUIRED_FIELDS if (d / "time1" / f).is_file()]
    limbs["fields_present"] = (len(present) == len(REQUIRED_FIELDS))
    detail["fields_present"] = present
    detail["fields_required"] = list(REQUIRED_FIELDS)

    # ---- THE AGE GUARD ----------------------------------------------------
    # 0/T is touched LAST at launch, so it dates the run allowed to produce the
    # answer.  EVERY field at endTime must be strictly NEWER than it.  A field
    # older than 0/T was not written by this run.
    t0 = int(must_read(d / "age_guard_0T_mtime_ns.txt").strip())
    mt = json.loads(must_read(d / "time1_mtime_ns.json"))
    older = [f for f in REQUIRED_FIELDS
             if mt.get(f) is None or mt[f] <= t0]
    limbs["age_guard"] = (len(older) == 0)
    detail["age_guard_0T_mtime_ns"] = t0
    detail["age_guard_fields_not_newer"] = older

    limbs_ok = all(limbs.values())
    return {"arm": arm, "limbs": limbs, "detail": detail, "complete": limbs_ok}


# ===========================================================================
# LOG PARSING -- iteration 1
# ===========================================================================
def iteration1_records(log_text):
    """-> dict of the iteration-1 solver lines, as PRINTED STRINGS (never
    re-formatted floats), plus the two p solves in order and the
    pressureControl pre-clip print."""
    lines = log_text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if re.match(r"^Time = 1\s*$", ln):
            start = i
            break
    if start is None:
        refuse("REFUSED: the log has no `Time = 1` block")
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if re.match(r"^Time = \d+\s*$", lines[i]):
            end = i
            break
    blk = lines[start:end]

    out = {"p_solves": [], "preclip": {}}
    for ln in blk:
        m = re.match(r"^\S+:\s+Solving for (\w+), Initial residual = "
                     rf"({NUM}), Final residual = ({NUM}), No Iterations (\d+)", ln)
        if m:
            var, i0, f0, it = m.group(1), m.group(2), m.group(3), m.group(4)
            if var == "p":
                out["p_solves"].append({"initial": i0, "final": f0, "iters": it})
            else:
                out.setdefault(var, {"initial": i0, "final": f0, "iters": it})
            continue
        m = re.match(rf"^time step continuity errors : sum local = ({NUM}), "
                     rf"global = ({NUM}), cumulative = ({NUM})", ln)
        if m:
            out["cont"] = {"sum_local": m.group(1), "global": m.group(2)}
            continue
        m = re.match(rf"^pressureControl: p (max|min) ({NUM})", ln)
        if m:
            out["preclip"][m.group(1)] = m.group(2)
    return out


def residual_signature(rec):
    """The comparable part of an iteration-1 record: every solver line, in
    order, as printed.  Used by PE5 for E1-vs-E2 identity."""
    sig = []
    for v in ("Ux", "Uy", "e", "omega", "k"):
        if v in rec:
            sig.append((v, rec[v]["initial"], rec[v]["final"], rec[v]["iters"]))
    for n, s in enumerate(rec["p_solves"]):
        sig.append((f"p#{n+1}", s["initial"], s["final"], s["iters"]))
    if "cont" in rec:
        sig.append(("cont", rec["cont"]["sum_local"], rec["cont"]["global"], ""))
    return sig


# ===========================================================================
# GEOMETRY
# ===========================================================================
def r_qc(centres, i):
    x, y = centres[i][0], centres[i][1]
    return math.hypot(x - QC[0], y - QC[1]) / CHORD


# ===========================================================================
# CONTROLS
# ===========================================================================
def control_c1_planted_zero(field_path, workdir):
    """C1.  Plant into a COPY on disk; read back THROUGH read_internal; require
    the planted value AT THE EXACT planted cell index.  REFUSE otherwise."""
    workdir = pathlib.Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    clean = read_internal(field_path)
    if any(abs(v - PLANT_VALUE) < 1e-3 for v in clean):
        refuse("REFUSED (C1): the CLEAN field already contains the plant value, "
               "so a positive arm could be a false positive")
    if PLANT_CELL >= len(clean):
        refuse(f"REFUSED (C1): plant cell {PLANT_CELL} out of range ({len(clean)})")
    dst = workdir / (pathlib.Path(field_path).name + ".PLANTED")
    plant_into_copy(field_path, dst, PLANT_CELL, PLANT_VALUE)
    back = read_internal(dst)
    if len(back) != len(clean):
        refuse(f"REFUSED (C1): planting changed the cell count {len(clean)} -> {len(back)}")
    if abs(back[PLANT_CELL] - PLANT_VALUE) >= 1e-3:
        refuse(f"REFUSED (C1): the reader CANNOT SEE the planted value at cell "
               f"{PLANT_CELL}: read {back[PLANT_CELL]!r}, planted {PLANT_VALUE!r}.  "
               f"A zero from this reader would not be evidence.")
    lo_i = min(range(len(back)), key=lambda i: back[i])
    if lo_i != PLANT_CELL:
        refuse(f"REFUSED (C1): the plant is reported at cell {lo_i}, not at the "
               f"exact planted cell {PLANT_CELL}")
    # NEGATIVE arm: re-reading the UNPLANTED original must NOT show the plant,
    # so "nothing here" is a reading and not a blind spot.
    again = read_internal(field_path)
    if any(abs(v - PLANT_VALUE) < 1e-3 for v in again):
        refuse("REFUSED (C1): the NEGATIVE arm found the plant in the unplanted "
               "original -- the reader is reading the wrong file")
    return {"fired": True, "cell": PLANT_CELL, "value": PLANT_VALUE,
            "n_cells": len(back)}


def control_c2_known_nonzero(rung1_p0, rung1_fvsolution, at_bound_count):
    """C2.  Derive the bounds from rung 1's OWN dictionaries and reproduce the
    registered bound values and the registered count."""
    t = must_read(rung1_p0)
    m = re.search(rf"internalField\s+uniform\s+({NUM})\s*;", _strip(t))
    if not m:
        refuse("REFUSED (C2): rung 1's 0/p is not a uniform internalField")
    p0 = float(m.group(1))
    fv = _strip(must_read(rung1_fvsolution))
    mn = re.search(rf"pMinFactor\s+({NUM})\s*;", fv)
    mx = re.search(rf"pMaxFactor\s+({NUM})\s*;", fv)
    if not (mn and mx):
        refuse("REFUSED (C2): rung 1's fvSolution has no pMinFactor/pMaxFactor")
    lo, hi = p0 * float(mn.group(1)), p0 * float(mx.group(1))
    ok_bounds = (lo == FLOOR and hi == CEIL)
    ok_count = (at_bound_count == PE2_AT_BOUND)
    if not ok_bounds:
        refuse(f"REFUSED (C2): bounds derived from rung 1's own dictionaries are "
               f"[{lo}, {hi}], not the registered [{FLOOR}, {CEIL}]")
    return {"fired": bool(ok_count), "p0": p0, "floor": lo, "ceil": hi,
            "at_bound_count": at_bound_count, "registered_count": PE2_AT_BOUND}


def control_c3_lever(e1_p, e2_p):
    """C3.  E2's written p must DIFFER from E1's."""
    a, b = read_internal(e1_p), read_internal(e2_p)
    if len(a) != len(b):
        refuse(f"REFUSED (C3): the two arms wrote different cell counts "
               f"{len(a)} vs {len(b)} -- they are not the same case")
    ndiff = sum(1 for i in range(len(a)) if a[i] != b[i])
    return {"fired": ndiff > 0, "n_cells": len(a), "n_cells_differing": ndiff}


def control_c4_mesh(mesh_identity_txt):
    """C4.  Every recorded polyMesh line must read IDENTICAL."""
    lines = [l for l in must_read(mesh_identity_txt).splitlines() if l.strip()]
    bad = [l for l in lines if not l.startswith("MESH IDENTICAL")]
    n_expected = 12   # geom + E1 + E2, four files each
    return {"fired": (len(bad) == 0 and len(lines) == n_expected),
            "n_lines": len(lines), "n_expected": n_expected, "non_identical": bad}


def control_c5_dicts(ev):
    """C5.  E1 18/18 identical; E2 17/18 with the ONE difference in
    system/fvSolution, in exactly two DELETED lines and nothing else."""
    e1 = must_read(pathlib.Path(ev) / "E1" / "case_identity_18.txt")
    n_id_1 = len(re.findall(r"^IDENTICAL ", e1, re.M))
    n_df_1 = len(re.findall(r"^DIFFERS   ", e1, re.M))
    e2 = must_read(pathlib.Path(ev) / "E2" / "case_identity_18.txt")
    n_id_2 = len(re.findall(r"^IDENTICAL ", e2, re.M))
    df2 = re.findall(r"^DIFFERS   (\S+)", e2, re.M)
    lever = must_read(pathlib.Path(ev) / "E2" / "lever_THE_ENTIRE_DELTA.diff")
    dels = [l for l in lever.splitlines() if l.startswith("< ")]
    adds = [l for l in lever.splitlines() if l.startswith("> ")]
    want = {"<     pMinFactor      0.1;", "<     pMaxFactor      2;"}
    fired = (n_id_1 == 18 and n_df_1 == 0 and
             n_id_2 == 17 and df2 == ["system/fvSolution"] and
             len(dels) == 2 and len(adds) == 0 and set(dels) == want)
    return {"fired": fired, "E1_identical": n_id_1, "E1_differing": n_df_1,
            "E2_identical": n_id_2, "E2_differing_files": df2,
            "lever_deletions": dels, "lever_additions": adds}


def control_c6_rung1(ev):
    """C6.  Rung 1's fingerprint before == after, for both arms."""
    before = must_read(pathlib.Path(ev) / "rung1_fingerprint_before.txt").strip()
    outs = {}
    ok = True
    for arm in ("E1", "E2"):
        after = must_read(pathlib.Path(ev) / arm / "rung1_fingerprint_after.txt").strip()
        outs[arm] = after
        if after != before:
            ok = False
    return {"fired": ok, "before": before, "after": outs}


def control_e2_never_grade(ev):
    """E2's structural never-grade interlock, re-checked at grading time."""
    d = pathlib.Path(ev) / "E2"
    case_path = must_read(d / "CASE_PATH.txt").strip()
    marker = (d / "DO_NOT_GRADE_INSTRUMENT_ONLY.txt").is_file()
    tok = E2_TOKEN in case_path
    if not (marker and tok):
        refuse(f"REFUSED: E2's never-grade interlock is not intact "
               f"(token in path: {tok}; marker present: {marker}).  E2's "
               f"configuration is a measurement instrument and may never be "
               f"carried into any graded run.")
    return {"fired": True, "case_path": case_path, "marker": marker}


# ===========================================================================
# CAP WATCH -- a HANG DETECTOR, not a budget tracker.  See the banner.
# ===========================================================================
def cap_watch(ev):
    total = 0.0
    per = {}
    for arm in ("E1", "E2"):
        p = pathlib.Path(ev) / arm / "CORE_MIN.txt"
        v = float(must_read(p).strip())
        per[arm] = v
        total += v
    over = total > REGISTERED_CAP_CORE_MIN
    return {
        "per_arm_core_min": per,
        "total_core_min": round(total, 6),
        "registered_estimate_core_min": REGISTERED_ESTIMATE_CORE_MIN,
        "registered_cap_core_min": REGISTERED_CAP_CORE_MIN,
        "ratio_actual_over_predicted": round(total / REGISTERED_ESTIMATE_CORE_MIN, 4),
        "hang_detector_wall_s_per_arm": HANG_DETECTOR_WALL_S,
        "what_the_cap_is": (
            "THE CAP IS A HANG DETECTOR, NOT A BUDGET TRACKER.  The 6.3x "
            "cap/estimate ratio is QUANTISATION, NOT SLACK: ClockTime has "
            "integer-second resolution, so quantisation alone is +/-0.0167 "
            "core-min per arm = 42% of the whole estimate, and a 1.5x cap on a "
            "five-second arm would abort on rounding (freeze section 6).  The "
            "cap is set from the wall-clock envelope, never from the estimate, "
            "and it is never raised."),
        "over_cap": over,
        "derived_usd": round(total / 60.0 * RATE_USD_PER_CORE_H, 8),
        "cost_basis": (
            "core-minutes = wall s x ranks / 60, measured from the launcher's "
            "own WALL_S.txt.  DOLLARS ARE DERIVED, NOT MEASURED "
            "($0.0513/core-h, c7a.4xlarge, reported-by-owner; the box cannot "
            "read its own billing, COMPUTE_BUDGET_CHARTER.md section 5)."),
    }


# ===========================================================================
# THE SIX REGISTERED PREDICTIONS, AND PE7's DELIBERATE ABSENCE
# ===========================================================================
def score(ev, rung1_case, centres_path, workdir):
    ev = pathlib.Path(ev)
    out = {
        "frozen_at_commit": FROZEN_COMMIT,
        "frozen_blob": FROZEN_BLOB,
        "frozen_body_lines": FROZEN_BODY_LINES,
        "frozen_body_sha256": FROZEN_BODY_SHA256,
        "this_arm_grades_nothing": True,
        "verdict_vocabulary_emitted": None,
        "note": ("F12 rung 1 stands NOT A RESULT and rungs 2-5 stand BLOCKED by "
                 "records this reader neither reads nor touches.  The rung-2 "
                 "rate_calibration_gate() interlock is not invoked, not "
                 "imported and not read around here."),
        "completion": {}, "controls": {}, "predictions": {}, "PE7": {},
    }

    # ---- E2's never-grade interlock, BEFORE anything else ----
    out["controls"]["E2_never_grade"] = control_e2_never_grade(ev)

    # ---- rule 4 FIRST: nothing is scored on an incomplete arm --------------
    for arm in ("E1", "E2"):
        out["completion"][arm] = strict_completion_rule(ev, arm)
    incomplete = [a for a in ("E1", "E2") if not out["completion"][a]["complete"]]
    if incomplete:
        refuse(f"REFUSED: the strict completion rule (CLAUDE.md rule 4) does not "
               f"hold for {incomplete}.  A run that fails any clause is not "
               f"done, and nothing is scored on it.  Limbs: "
               f"{json.dumps({a: out['completion'][a]['limbs'] for a in incomplete})}")

    e1p = ev / "E1" / "time1" / "p"
    e2p = ev / "E2" / "time1" / "p"

    # ---- C1 planted zero, on BOTH arms' own written field ------------------
    out["controls"]["C1_planted_zero_E1"] = control_c1_planted_zero(e1p, pathlib.Path(workdir) / "C1_E1")
    out["controls"]["C1_planted_zero_E2"] = control_c1_planted_zero(e2p, pathlib.Path(workdir) / "C1_E2")

    e1_vals = read_internal(e1p)
    e2_vals = read_internal(e2p)

    # ---- PE2 / PE3 --------------------------------------------------------
    at_bound = sum(1 for v in e1_vals if v == FLOOR or v == CEIL)
    outside = [i for i, v in enumerate(e1_vals) if v < FLOOR or v > CEIL]
    out["predictions"]["PE2"] = {
        "statement": "E1's time-1 p, post-clip, has exactly 6,914 of 23,040 cells at a bound",
        "registered": {"at_bound": PE2_AT_BOUND, "n_cells": N_CELLS},
        "measured": {"at_bound": at_bound, "n_cells": len(e1_vals),
                     "at_floor": sum(1 for v in e1_vals if v == FLOOR),
                     "at_ceil": sum(1 for v in e1_vals if v == CEIL)},
        "held": (at_bound == PE2_AT_BOUND and len(e1_vals) == N_CELLS),
    }
    out["predictions"]["PE3"] = {
        "statement": f"E1's time-1 p has no cell outside [{FLOOR}, {CEIL}]",
        "measured": {"n_outside": len(outside), "first_outside": outside[:10],
                     "min": min(e1_vals), "max": max(e1_vals)},
        "held": (len(outside) == 0),
    }

    # ---- C2 ----------------------------------------------------------------
    out["controls"]["C2_known_nonzero"] = control_c2_known_nonzero(
        pathlib.Path(rung1_case) / "0" / "p",
        pathlib.Path(rung1_case) / "system" / "fvSolution",
        at_bound)

    # ---- PE1 / PE5 --------------------------------------------------------
    r1 = iteration1_records(must_read(ev / "E1" / "log.rhoSimpleFoam"))
    r2 = iteration1_records(must_read(ev / "E2" / "log.rhoSimpleFoam"))
    if len(r1["p_solves"]) < 2:
        refuse(f"REFUSED: E1's iteration 1 shows {len(r1['p_solves'])} p solves, "
               f"not the 2 the registered nNonOrthogonalCorrectors 1 implies")
    got = {
        "Ux_initial": r1.get("Ux", {}).get("initial"),
        "Uy_initial": r1.get("Uy", {}).get("initial"),
        "e_initial": r1.get("e", {}).get("initial"),
        "p1_initial": r1["p_solves"][0]["initial"],
        "p1_final": r1["p_solves"][0]["final"],
        "p1_iters": r1["p_solves"][0]["iters"],
        "p2_initial": r1["p_solves"][1]["initial"],
        "p2_final": r1["p_solves"][1]["final"],
        "p2_iters": r1["p_solves"][1]["iters"],
        "cont_sum_local": r1.get("cont", {}).get("sum_local"),
        "cont_global": r1.get("cont", {}).get("global"),
    }
    mismatches = {k: {"registered": PE1[k], "measured": got[k]}
                  for k in PE1 if got[k] != PE1[k]}
    out["predictions"]["PE1"] = {
        "statement": "E1's iteration-1 log reproduces rung 1's exactly; 0 mismatches",
        "n_mismatches": len(mismatches), "mismatches": mismatches,
        "measured": got,
        "held": (len(mismatches) == 0),
    }
    s1, s2 = residual_signature(r1), residual_signature(r2)
    out["predictions"]["PE5"] = {
        "statement": ("E1 and E2 have identical iteration-1 solve residuals, "
                      "because pressureControl::limit() acts AFTER both p solves"),
        "identical": (s1 == s2),
        "E1_signature": s1, "E2_signature": s2,
        "if_it_fails": ("the limiter acts EARLIER than this registration "
                        "believes, and that is itself the finding"),
        "held": (s1 == s2),
    }

    # ---- PE4 --------------------------------------------------------------
    e2_min, e2_max = min(e2_vals), max(e2_vals)
    out["predictions"]["PE4"] = {
        "statement": ("E2's time-1 p reproduces the pre-clip print to its "
                      "printed digits: min -411376.774, max 2974458.981"),
        "registered": {"min": PE4_MIN, "max": PE4_MAX},
        "measured": {"min": e2_min, "max": e2_max,
                     "min_index": e2_vals.index(e2_min),
                     "max_index": e2_vals.index(e2_max)},
        "E2_own_preclip_print": r2.get("preclip", {}),
        "held": (round(e2_min, PE4_PRINT_DP) == round(PE4_MIN, PE4_PRINT_DP) and
                 round(e2_max, PE4_PRINT_DP) == round(PE4_MAX, PE4_PRINT_DP)),
    }

    # ---- C3 ----------------------------------------------------------------
    out["controls"]["C3_lever_effect"] = control_c3_lever(e1p, e2p)

    # ---- PE6 --------------------------------------------------------------
    centres = read_internal(centres_path)
    if len(centres) != len(e2_vals):
        refuse(f"REFUSED: the cell-centre field has {len(centres)} cells and the "
               f"p field has {len(e2_vals)} -- they are not the same mesh")
    imin, imax = e2_vals.index(e2_min), e2_vals.index(e2_max)
    rmin, rmax = r_qc(centres, imin), r_qc(centres, imax)
    out["predictions"]["PE6"] = {
        "statement": ("the pre-clip extreme cells lie within r <= 0.836 chords "
                      "of the quarter chord"),
        "registered_r_max": PE6_R_MAX,
        "measured": {
            "min_cell": imin, "min_xy": centres[imin][:2], "min_r_qc": round(rmin, 6),
            "max_cell": imax, "max_xy": centres[imax][:2], "max_r_qc": round(rmax, 6)},
        "held": (rmin <= PE6_R_MAX and rmax <= PE6_R_MAX),
    }

    # ---- C4, C5, C6 -------------------------------------------------------
    out["controls"]["C4_mesh_identity"] = control_c4_mesh(ev / "mesh_identity.txt")
    out["controls"]["C5_dictionary_identity"] = control_c5_dicts(ev)
    out["controls"]["C6_rung1_untouched"] = control_c6_rung1(ev)

    # ---- PE7: NO PREDICTION IS REGISTERED ---------------------------------
    # Section 4 of the freeze: "No evidence on disk bears on it, and registering
    # a guess would be outcome-fitting."  The arm reports the answer either way
    # and the record states it AS A MEASUREMENT.  This reader therefore emits no
    # `held` key for PE7 and no threshold for it.
    out["PE7"] = {
        "prediction_registered": False,
        "question": ("whether the extremes are present after the FIRST inner p "
                     "solve or only after the SECOND (the non-orthogonal "
                     "corrector)"),
        "measurement": {
            "E1_p_solves_iteration1": r1["p_solves"],
            "E2_p_solves_iteration1": r2["p_solves"],
            "E1_preclip_print": r1.get("preclip", {}),
            "E2_preclip_print": r2.get("preclip", {}),
        },
        "resolved_by_this_instrument": False,
        "why_not": (
            "The registered instrument writes fields at time 1 only, and "
            "pressureControl prints once per outer iteration, AFTER both inner "
            "p solves.  No field and no print exists BETWEEN the two inner "
            "solves, so this arm's disk output does not resolve the question "
            "either way.  Stated as a measurement, not narrowed, not guessed, "
            "and NOT converted into a prediction after the fact."),
    }

    # ---- the seven open mechanisms stay listed, unchanged and unnarrowed ---
    out["open_mechanisms"] = (
        "F12's triage names SEVEN mechanisms explicitly not distinguished. "
        "This arm distinguishes NONE of them, prunes none, merges none, and "
        "its existence implies none.  The list is unchanged and unnarrowed.")

    failed = [k for k, v in out["predictions"].items() if not v["held"]]
    unfired = [k for k, v in out["controls"].items() if not v.get("fired", False)]
    if unfired:
        refuse(f"REFUSED: control(s) {unfired} DID NOT FIRE.  Every number this "
               f"reader produced is withdrawn.")
    out["cap_watch"] = cap_watch(ev)
    out["predictions_not_held"] = failed
    return out


# ===========================================================================
# SELFTEST -- every control and every prediction driven BOTH ways, through the
# real reader, on synthetic fixtures written to disk.  A control that can only
# pass is not a control.
# ===========================================================================
def _write_scalar(path, vals, cls="volScalarField", loc="1", obj="p"):
    body = "\n".join(repr(v) for v in vals)
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(path).write_text(
        f"FoamFile\n{{\n version 2.0;\n format ascii;\n class {cls};\n"
        f" location \"{loc}\";\n object {obj};\n}}\n\n"
        f"dimensions [1 -1 -2 0 0 0 0];\n\n"
        f"internalField   nonuniform List<scalar> \n{len(vals)}\n(\n{body}\n)\n;\n\n"
        f"boundaryField\n{{\n}}\n")


def _write_vector(path, vals, obj="C"):
    body = "\n".join(f"({v[0]!r} {v[1]!r} {v[2]!r})" for v in vals)
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(path).write_text(
        f"FoamFile\n{{\n version 2.0;\n format ascii;\n class volVectorField;\n"
        f" object {obj};\n}}\n\ndimensions [0 1 0 0 0 0 0];\n\n"
        f"internalField   nonuniform List<vector> \n{len(vals)}\n(\n{body}\n)\n;\n\n"
        f"boundaryField\n{{\n}}\n")


_LOG_TMPL = """/*-- header --*/
Starting time loop

Time = {t}

DILUPBiCGStab:  Solving for Ux, Initial residual = {Ux}, Final residual = 1.667801535e-05, No Iterations 1
DILUPBiCGStab:  Solving for Uy, Initial residual = {Uy}, Final residual = 1.036800283e-05, No Iterations 1
DILUPBiCGStab:  Solving for e, Initial residual = {e}, Final residual = 0.0001841217762, No Iterations 1
GAMG:  Solving for p, Initial residual = {p1i}, Final residual = {p1f}, No Iterations {p1n}
GAMG:  Solving for p, Initial residual = {p2i}, Final residual = {p2f}, No Iterations {p2n}
time step continuity errors : sum local = {cl}, global = {cg}, cumulative = {cg}
pressureControl: p max {pmax}
pressureControl: p min {pmin}
DILUPBiCGStab:  Solving for omega, Initial residual = 0.0002266996962, Final residual = 7.329120709e-08, No Iterations 1
DILUPBiCGStab:  Solving for k, Initial residual = 1, Final residual = 0.00464266379, No Iterations 1
ExecutionTime = 0.25 s  ClockTime = 1 s

End
"""


def _log(**kw):
    d = dict(t=1, Ux=PE1["Ux_initial"], Uy=PE1["Uy_initial"], e=PE1["e_initial"],
             p1i=PE1["p1_initial"], p1f=PE1["p1_final"], p1n=PE1["p1_iters"],
             p2i=PE1["p2_initial"], p2f=PE1["p2_final"], p2n=PE1["p2_iters"],
             cl=PE1["cont_sum_local"], cg=PE1["cont_global"],
             pmax=repr(PE4_MAX), pmin=repr(PE4_MIN))
    d.update(kw)
    return _LOG_TMPL.format(**d)


def _build_fixture(root):
    """A complete synthetic Arm E evidence tree that SCORES CLEAN, plus a
    synthetic rung-1 case and cell-centre field.  N is small; the registered
    counts are honoured by construction so the fixture exercises the real
    comparisons rather than a relaxed copy of them."""
    root = pathlib.Path(root)
    if root.exists():
        shutil.rmtree(root)
    ev = root / "evidence"
    n = N_CELLS
    # E1: exactly PE2_AT_BOUND cells at a bound (split floor/ceil), rest inside.
    n_floor = 3628
    n_ceil = PE2_AT_BOUND - n_floor
    e1 = [FLOOR] * n_floor + [CEIL] * n_ceil + \
         [50000.0 + (i % 977) for i in range(n - PE2_AT_BOUND)]
    # E2: the pre-clip field.  Its min/max sit at cells whose centres are inside
    # r <= 0.836, and it differs from E1 everywhere the clip acted.
    e2 = list(e1)
    e2[0] = PE4_MIN
    e2[1] = PE4_MAX
    for i in range(2, PE2_AT_BOUND):
        e2[i] = e1[i] + (1.0 if e1[i] == CEIL else -1.0)
    # cell centres: cells 0 and 1 near the quarter chord; the rest far away.
    centres = [(0.25, 0.0, 0.0), (0.9956, 0.001, 0.0)] + \
              [(30.0 + i * 1e-3, 0.0, 0.0) for i in range(n - 2)]
    _write_vector(ev / "cellCentres_C", centres)

    for arm, vals in (("E1", e1), ("E2", e2)):
        d = ev / arm
        d.mkdir(parents=True, exist_ok=True)
        (d / "RC.txt").write_text("0\n")
        (d / "log.rhoSimpleFoam").write_text(_log())
        (d / "WALL_S.txt").write_text("2.384000\n")
        (d / "CORE_MIN.txt").write_text("0.039733\n")
        (d / "CASE_PATH.txt").write_text(
            str(root / ("E2_INSTRUMENT_NEVER_GRADE/case" if arm == "E2" else "E1/case")) + "\n")
        (d / "rung1_fingerprint_after.txt").write_text("FINGERPRINT_X\n")
        _write_scalar(d / "time1" / "p", vals)
        for f in ("U", "T", "rho", "phi"):
            (d / "time1" / f).write_text("placeholder\n")
        (d / "age_guard_0T_mtime_ns.txt").write_text("1000\n")
        (d / "time1_mtime_ns.json").write_text(
            json.dumps({f: 2000 for f in REQUIRED_FIELDS}))
        n_id = 18 if arm == "E1" else 17
        rows = [f"IDENTICAL f{i} 00" for i in range(n_id)]
        if arm == "E2":
            rows.append("DIFFERS   system/fvSolution src=a arm=b")
            (d / "lever_THE_ENTIRE_DELTA.diff").write_text(
                "6,7d5\n<     pMinFactor      0.1;\n<     pMaxFactor      2;\n")
            (d / "DO_NOT_GRADE_INSTRUMENT_ONLY.txt").write_text("INSTRUMENT ONLY\n")
        (d / "case_identity_18.txt").write_text("\n".join(rows) + "\n")
    (ev / "rung1_fingerprint_before.txt").write_text("FINGERPRINT_X\n")
    (ev / "mesh_identity.txt").write_text("\n".join(
        f"MESH IDENTICAL {a} constant/polyMesh/{f} 00"
        for a in ("geom", "E1", "E2")
        for f in ("points", "faces", "owner", "neighbour")) + "\n")
    # synthetic rung-1 case for C2
    r1 = root / "rung1"
    (r1 / "0").mkdir(parents=True, exist_ok=True)
    (r1 / "system").mkdir(parents=True, exist_ok=True)
    (r1 / "0" / "p").write_text(
        "FoamFile{class volScalarField; object p;}\ndimensions [1 -1 -2 0 0 0 0];\n"
        f"internalField   uniform {P_REF!r};\nboundaryField{{}}\n")
    (r1 / "system" / "fvSolution").write_text(
        "SIMPLE\n{\n    nNonOrthogonalCorrectors 1;\n"
        f"    pMinFactor      {PMINFACTOR};\n    pMaxFactor      {PMAXFACTOR};\n}}\n")
    return ev, r1, ev / "cellCentres_C"


def selftest(workroot):
    workroot = pathlib.Path(workroot)
    results = []

    def drive(name, mutate=None, expect_refuse=False, expect_not_held=None):
        """Build a clean fixture, optionally mutate it, run the REAL scorer."""
        root = workroot / re.sub(r"\W+", "_", name)
        ev, r1, cc = _build_fixture(root)
        if mutate is not None:
            mutate(ev, r1, cc)
        try:
            out = score(ev, r1, cc, root / "scratch")
        except Refused as exc:
            got_refuse, out, err = True, None, str(exc)
        else:
            got_refuse, err = False, ""
        if expect_refuse:
            ok = got_refuse
            detail = (err[:110] if got_refuse else "the reader DID NOT refuse")
        elif expect_not_held is not None:
            ok = (not got_refuse) and out["predictions"][expect_not_held]["held"] is False
            detail = (f"{expect_not_held} not held" if ok else
                      (f"refused: {err[:80]}" if got_refuse else
                       f"{expect_not_held} still held"))
        else:
            ok = (not got_refuse) and out["predictions_not_held"] == []
            detail = ("clean" if ok else
                      (f"refused: {err[:110]}" if got_refuse else
                       f"not held: {out['predictions_not_held']}"))
        results.append((name, ok, detail))
        print(("CONTROL-OK   " if ok else "CONTROL-BAD  ") + name + f"   [{detail}]")

    print("=== BASELINE: the clean fixture must score with every prediction "
          "HELD and every control FIRED ===")
    drive("BASELINE clean fixture scores clean")

    print("\n=== EVERY REGISTERED PREDICTION DRIVEN TO A FAILING VALUE ===")

    def m_pe1(ev, r1, cc):
        p = ev / "E1" / "log.rhoSimpleFoam"
        p.write_text(_log(Ux="0.9999999999"))
    drive("PE1 fails when one iteration-1 digit differs", m_pe1, expect_not_held="PE1")

    def m_pe2(ev, r1, cc):
        v = read_internal(ev / "E1" / "time1" / "p")
        v[0] = 99999.0
        _write_scalar(ev / "E1" / "time1" / "p", v)
    drive("PE2/C2: the at-bound count moving off 6,914 REFUSES (rc 2), because the\n      freeze makes the 6,914 count a CONTROL limb of C2 as well as prediction PE2",
          m_pe2, expect_refuse=True)

    def m_pe3(ev, r1, cc):
        v = read_internal(ev / "E1" / "time1" / "p")
        v[-1] = CEIL + 1.0
        _write_scalar(ev / "E1" / "time1" / "p", v)
    drive("PE3 fails when one E1 cell lies outside the registered bounds",
          m_pe3, expect_not_held="PE3")

    def m_pe4(ev, r1, cc):
        v = read_internal(ev / "E2" / "time1" / "p")
        v[0] = PE4_MIN - 1000.0
        _write_scalar(ev / "E2" / "time1" / "p", v)
    drive("PE4 fails when E2's pre-clip min departs the printed digits",
          m_pe4, expect_not_held="PE4")

    def m_pe5(ev, r1, cc):
        (ev / "E2" / "log.rhoSimpleFoam").write_text(_log(p1n="48"))
    drive("PE5 fails when E1 and E2 iteration-1 residuals differ",
          m_pe5, expect_not_held="PE5")

    def m_pe6(ev, r1, cc):
        c = read_internal(cc)
        c[0] = (0.25 + 5.0, 0.0, 0.0)
        _write_vector(cc, c)
    drive("PE6 fails when a pre-clip extreme cell lies beyond r = 0.836 chords",
          m_pe6, expect_not_held="PE6")

    print("\n=== EVERY REGISTERED CONTROL DRIVEN TO A REFUSAL ===")

    def m_c1(ev, r1, cc):
        # a reader that cannot see the plant: make the plant value already
        # present in the clean field, so the positive arm cannot distinguish it
        v = read_internal(ev / "E1" / "time1" / "p")
        v[5] = PLANT_VALUE
        _write_scalar(ev / "E1" / "time1" / "p", v)
    drive("C1 refuses when the clean field already carries the plant value",
          m_c1, expect_refuse=True)

    def m_c1b(ev, r1, cc):
        # truncate the field so the planted cell index is out of range: the
        # reader must REFUSE, not silently plant somewhere else
        v = read_internal(ev / "E1" / "time1" / "p")[:100]
        _write_scalar(ev / "E1" / "time1" / "p", v)
    drive("C1 refuses when the plant cell is out of range", m_c1b, expect_refuse=True)

    def m_c2(ev, r1, cc):
        (r1 / "system" / "fvSolution").write_text(
            "SIMPLE\n{\n    pMinFactor      0.2;\n    pMaxFactor      2;\n}\n")
    drive("C2 refuses when the bounds derived from rung 1 are not the registered ones",
          m_c2, expect_refuse=True)

    def m_c3(ev, r1, cc):
        shutil.copy(ev / "E1" / "time1" / "p", ev / "E2" / "time1" / "p")
    drive("C3 refuses when E2's field equals E1's -- the lever did not act",
          m_c3, expect_refuse=True)

    def m_c4(ev, r1, cc):
        t = (ev / "mesh_identity.txt").read_text()
        (ev / "mesh_identity.txt").write_text(
            t.replace("MESH IDENTICAL E2 constant/polyMesh/points",
                      "MESH DIFFERS   E2 constant/polyMesh/points", 1))
    drive("C4 refuses when one polyMesh file is not identical to rung 1's",
          m_c4, expect_refuse=True)

    def m_c5(ev, r1, cc):
        (ev / "E2" / "lever_THE_ENTIRE_DELTA.diff").write_text(
            "6,8d5\n<     pMinFactor      0.1;\n<     pMaxFactor      2;\n"
            "<     nNonOrthogonalCorrectors 1;\n")
    drive("C5 refuses when E2's fvSolution differs in more than the two registered lines",
          m_c5, expect_refuse=True)

    def m_c5b(ev, r1, cc):
        (ev / "E1" / "case_identity_18.txt").write_text(
            "\n".join([f"IDENTICAL f{i} 00" for i in range(17)]) +
            "\nDIFFERS   system/fvSchemes src=a arm=b\n")
    drive("C5 refuses when an E1 physics dictionary is not byte-identical to rung 1's",
          m_c5b, expect_refuse=True)

    def m_c6(ev, r1, cc):
        (ev / "E1" / "rung1_fingerprint_after.txt").write_text("FINGERPRINT_Y\n")
    drive("C6 refuses when rung 1's fingerprint changed across the arm",
          m_c6, expect_refuse=True)

    def m_e2tok(ev, r1, cc):
        (ev / "E2" / "CASE_PATH.txt").write_text("/tmp/some/graded/case\n")
    drive("E2 never-grade interlock refuses when the case path lacks the token",
          m_e2tok, expect_refuse=True)

    def m_e2mark(ev, r1, cc):
        (ev / "E2" / "DO_NOT_GRADE_INSTRUMENT_ONLY.txt").unlink()
    drive("E2 never-grade interlock refuses when the DO_NOT_GRADE marker is absent",
          m_e2mark, expect_refuse=True)

    print("\n=== EVERY STRICT-COMPLETION LIMB (rule 4) DRIVEN TO A REFUSAL ===")

    def m_rc(ev, r1, cc):
        (ev / "E1" / "RC.txt").write_text("1\n")
    drive("rule 4: refuses on rc != 0", m_rc, expect_refuse=True)

    def m_rc124(ev, r1, cc):
        (ev / "E1" / "RC.txt").write_text("124\n")
    drive("rule 4: refuses on rc 124 -- the hang detector fired", m_rc124, expect_refuse=True)

    def m_end(ev, r1, cc):
        p = ev / "E1" / "log.rhoSimpleFoam"
        p.write_text(p.read_text().replace("\nEnd\n", "\n"))
    drive("rule 4: refuses when the log has no End line", m_end, expect_refuse=True)

    def m_time(ev, r1, cc):
        (ev / "E1" / "log.rhoSimpleFoam").write_text(_log(t=2))
    drive("rule 4: refuses when the last time is not endTime", m_time, expect_refuse=True)

    def m_exec(ev, r1, cc):
        p = ev / "E1" / "log.rhoSimpleFoam"
        p.write_text(p.read_text() + "ExecutionTime = 0.5 s  ClockTime = 1 s\n")
    drive("rule 4: refuses when the ExecutionTime count != endTime", m_exec, expect_refuse=True)

    def m_field(ev, r1, cc):
        (ev / "E1" / "time1" / "rho").unlink()
    drive("rule 4: refuses when a registered field is absent at endTime",
          m_field, expect_refuse=True)

    def m_age(ev, r1, cc):
        (ev / "E1" / "time1_mtime_ns.json").write_text(
            json.dumps({f: (500 if f == "p" else 2000) for f in REQUIRED_FIELDS}))
    drive("rule 4 AGE GUARD: refuses when a field at endTime is OLDER than the "
          "case's own 0/T", m_age, expect_refuse=True)

    print("\n=== REFUSE-RATHER-THAN-DEGRADE ON MISSING INPUT ===")

    def m_missing(ev, r1, cc):
        (ev / "E2" / "log.rhoSimpleFoam").unlink()
    drive("refuses on a missing input rather than degrading", m_missing, expect_refuse=True)

    def m_empty(ev, r1, cc):
        (ev / "E1" / "WALL_S.txt").write_text("")
        (ev / "E1" / "CORE_MIN.txt").write_text("")
    drive("refuses on an empty input rather than degrading", m_empty, expect_refuse=True)

    print("\n=== CAP WATCH (a HANG DETECTOR, not a budget tracker) ===")

    def m_cap(ev, r1, cc):
        (ev / "E1" / "CORE_MIN.txt").write_text("0.400000\n")
        (ev / "E2" / "CORE_MIN.txt").write_text("0.300000\n")
    root = workroot / "capwatch"
    ev, r1, cc = _build_fixture(root)
    m_cap(ev, r1, cc)
    cw = score(ev, r1, cc, root / "scratch")["cap_watch"]
    ok = cw["over_cap"] is True and cw["total_core_min"] == 0.7
    results.append(("cap watch flags an over-cap total", ok, f"{cw['total_core_min']} core-min"))
    print(("CONTROL-OK   " if ok else "CONTROL-BAD  ") +
          "cap watch flags an over-cap total   [%s core-min]" % cw["total_core_min"])
    root = workroot / "capwatch_under"
    ev, r1, cc = _build_fixture(root)
    cw = score(ev, r1, cc, root / "scratch")["cap_watch"]
    ok = cw["over_cap"] is False
    results.append(("cap watch passes an under-cap total", ok, f"{cw['total_core_min']} core-min"))
    print(("CONTROL-OK   " if ok else "CONTROL-BAD  ") +
          "cap watch passes an under-cap total   [%s core-min]" % cw["total_core_min"])

    print("\n=== PE7 REGISTERS NO PREDICTION ===")
    root = workroot / "pe7"
    ev, r1, cc = _build_fixture(root)
    out = score(ev, r1, cc, root / "scratch")
    ok = (out["PE7"]["prediction_registered"] is False and
          "held" not in out["PE7"] and
          "PE7" not in out["predictions"] and
          out["PE7"]["resolved_by_this_instrument"] is False)
    results.append(("PE7 carries NO prediction and NO threshold", ok, ""))
    print(("CONTROL-OK   " if ok else "CONTROL-BAD  ") +
          "PE7 carries NO prediction and NO threshold")

    print("\n=== NO VERDICT-VOCABULARY WORD IS EMITTED ===")
    blob = json.dumps(out, default=str)
    banned = [w for w in ("GATE REACHED", "GATE FAIL", "BLOCKED", "PENDING")
              if w in blob and w not in out["note"]]
    ok = (banned == [])
    results.append(("no verdict-vocabulary word leaks into the result", ok, str(banned)))
    print(("CONTROL-OK   " if ok else "CONTROL-BAD  ") +
          "no verdict-vocabulary word leaks into the result")

    bad = [n for n, o, _ in results if not o]
    print(f"\n{len(results)-len(bad)}/{len(results)} controls driven BOTH WAYS through "
          f"the real reader" + (f"; FAILED {bad} -> READER REFUSED" if bad else
          "; every registered control and every registered prediction was shown "
          "able to FAIL as well as to hold"))
    return 2 if bad else 0


# ===========================================================================
def main(argv):
    if len(argv) >= 2 and argv[1] == "--selftest":
        wr = argv[2] if len(argv) >= 3 else "/tmp/f12_arm_e_selftest"
        return selftest(pathlib.Path(wr))
    if len(argv) < 5:
        sys.stderr.write(
            "usage: analyse_first_pressure_solve.py <evidence_dir> <rung1_case> "
            "<cellCentres_C> <workdir>\n"
            "       analyse_first_pressure_solve.py --selftest [workdir]\n")
        return 2
    try:
        out = score(argv[1], argv[2], argv[3], argv[4])
    except Refused as exc:
        sys.stderr.write(str(exc) + "\n")
        return 2
    print(json.dumps(out, indent=2, default=str))
    return 1 if out["predictions_not_held"] else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
