#!/usr/bin/env python3
"""CRM WING-BODY (D8G) -- THE GRADING PATH FOR THE PSEUDO-TRANSIENT (LTS) RUNG.

This file is the comparator for the rung registered at
`verification/campaign/CRM_WINGBODY_DPW6_ACT_PREREGISTRATION.md` ADDENDUM 15 (v1.14),
and for the act's §5 force bands.  A grade produced by any other path is NOT A RESULT.
Before its output is believed, hash this file against its committed blob: the frozen
file must BE the file that ran.  `--freeze-check <sha>` does that hash here; the lab
instrument is `scripts/check_comparator_freeze.py`.

WHAT IT DOES
    1. ESTABLISHES LIVENESS FROM THE PROCESS TABLE AND FILE MTIMES -- never from the
       log's contents -- and refuses in BOTH directions: it will not grade a run that
       is still moving, and it will not report a rate or a progress figure from a log
       that has stopped.  (`--monitor` is the rate path; `--grade` is the verdict path.)
    2. Enforces standing rule 4, EVERY clause, on the decomposed case.
    3. Reads the A15.7 refutation channels L1..L5 out of the solver log and, for L5,
       out of the BINARY FIELD FILES themselves.
    4. Reads Cd/Cl/CmPitch from `postProcessing/forceCoeffs/*/coefficient.dat` BY
       COLUMN NAME, taken from the file's own header line, never by position, and
       carries the arithmetic identities Cd(f)+Cd(r) == Cd and Cl(f)+Cl(r) == Cl as
       controls that can REFUSE.
    5. Gates CL, CD, CM against the §5 bands when -- and only when -- the run is
       complete at its registered length and the reference row has been registered.
    6. Emits one verdict from the fixed vocabulary:
       PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING

THE D631 READING, ADOPTED AND NAMED.  Standing rule 4's ExecutionTime clause has a
resume-shaped hole and five graders in this lab read it two incompatible ways.  THIS
FILE ADOPTS THE STRONGEST READING IN THE LAB, the one implemented in
`cases/navier_class/SUBOFF_A1/grade_suboff_a1h.py:212-226` via `scripts/solver_log_set.py`:
the count is taken on the PHYSICS -- the set of DISTINCT `Time =` values reached,
UNIONED ACROSS EVERY LOG SEGMENT -- and the clause passes only when that set is
EXACTLY {1 .. endTime}.  A step re-run after a resume collapses to one step; a skipped
step is NAMED; a repeated step is not credited twice.  The launcher appends every
segment into one `log.<APP>` (`launch_crm_wb_v2.A15_PROPOSED.sh:179`, `>>`), which is
the appended layout that module's fixtures 7 and 8 exist for.

WHAT IT REFUSES TO DO (exit 2, never a degraded answer)
    - run before its plants have been read back FROM DISK (standing rule 3)
    - grade a run that is still live, or report a rate from a log that is dead
    - read a coefficient by column position
    - read a coefficient from a file whose own split columns do not sum to its total
    - write anything inside a case it grades

WHY THE PLANTS ARE NOT A FORMALITY.  Two failures this act has already paid for:
    (a) A rate table was published from logs that had been frozen for 37 minutes.  The
        reader had no way to know: it read the log's CONTENTS, which look identical
        whether the writer is alive or dead.  P-E is that control.
    (b) `Cd(f)` was read as `Cd` by `awk '{print $3}'` and drag was reported halved,
        with a mechanism invented for it.  P-A and P-B are that control: P-A shuffles
        the header columns and requires the SAME answer, P-B breaks the split sum and
        requires a REFUSAL.

    AND THE ONE THAT MATTERS MOST.  Nine planted controls in this lab passed while
    asking only whether the gate FIRED, never whether the NUMBER WAS REAL.  P-C and
    P-D are written the other way round: P-C drives a case that must FAIL completion
    and then, with one mtime corrected, must PASS it -- a guard that cannot fail is
    inert.  P-D drives a whole synthetic run end to end with an EXACTLY KNOWN Cd, once
    outside the band (must be GATE FAIL) and once inside (must be PASS), and checks
    the RETURNED NUMBER against the planted one to 1e-12.  A gate that cannot fail is
    not a gate, and a gate that fires on a number nobody checked is not evidence.

Author: cfd lab-lane, 2026-09-13.
"""

import argparse
import json
import math
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time

try:
    import numpy as _np              # decode/reduce only; see read_internal_field
except ImportError:                  # pragma: no cover -- the pure-python path is kept
    _np = None

if not __debug__:
    sys.stderr.write("REFUSED: must not run under python3 -O; the asserts are the point.\n")
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

# ------------------------------------------------------------ frozen constants --
PREREG = "verification/campaign/CRM_WINGBODY_DPW6_ACT_PREREGISTRATION.md"
PREREG_VERSION = "1.14 (ADDENDUM 15)"

# §4, computed there and written into the case dictionaries.  Quoted, not re-derived.
RHO_INF   = 0.04503298815        # kg m^-3
U_INF     = 300.0189024          # m s^-1
P_INF     = 4007.394649          # Pa
T_INF     = 310.0                # K  [registered by Sanaa; DPW-6 states 310.93]
C_REF     = 7.00532              # m
A_REF     = 191.8447776          # m^2, HALF MODEL
Q_INF     = 0.5 * RHO_INF * U_INF ** 2          # Pa, dynamic pressure

# §5 bands.  FULL/HALF width convention is settled in the pre-registration; these are
# the HALF widths it registers.  They are not re-derived and may not be changed here.
BAND_CD   = 0.0004               # §5.1, from Tinoco p.13's 8-count spread, full->half
BAND_CL   = 0.01                 # §5.2, LABELLED A LAB JUDGEMENT
BAND_CM   = 0.01                 # §5.2, LABELLED A LAB JUDGEMENT

# A15.7 refutation conditions.  Numeric, written before the run.
L1_RESIDUAL_CEIL   = 0.99        # h initial residual of the hFinal solve
L1_BY_STEP         = 20
L2_CLAMP_CEIL_PCT  = 1.0         # BOTH branches summed
L2_BY_STEP         = 50
L3_CD_RANGE        = (0.0, 0.2)
L3_CL_RANGE        = (0.0, 1.0)
L3_THROUGH_STEP    = 300
L4_MAX_CO          = 0.2         # registered maxCo
L5_P_ABS_MAX       = 12854.0     # 2 * p0, p0 = 6427.135 Pa (LAUNCH.log stage 0b)
L5_U_MAG_MAX       = 2.0 * U_INF # 600.0378048 m s^-1

# Liveness.  Seconds.  These are instrument settings, not gates.
LIVE_MTIME_S  = 90.0     # a log touched this recently, with no rc written, is LIVE
STALL_S       = 300.0    # a log untouched this long is DEAD; --monitor refuses on it

# rule-3 plant magnitudes.  House constant 1.234e-03 (T3_runs/analyse_t3.py).
PLANT_CD        = 1.234e-03
PLANT_CD_DECOY  = 5.678e-03
PLANT_P_FIELD   = 9.876e+03
PLANT_U_FIELD   = 4.321e+02

VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")


def refuse(msg, code=2):
    sys.stderr.write("REFUSED: " + msg + "\n")
    sys.exit(code)


# ============================================================ 1. LIVENESS =======
# Established from the PROCESS TABLE and FILE MTIMES.  Never from the log's contents:
# a log frozen 37 minutes ago and a log being written right now are byte-identical in
# their last 10,000 lines, and this lab has already published a rate table off the
# former.

def _procs_in(case):
    """PIDs whose cwd resolves into `case`, or whose argv names it.  No pgrep: a
    pattern match against a command line also matches the shell that invoked it, and
    fleet agents are invisible to it anyway (L-41).  /proc is read directly."""
    case = os.path.realpath(case)
    out = []
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            cwd = os.path.realpath(os.path.join("/proc", pid, "cwd"))
            with open(os.path.join("/proc", pid, "cmdline"), "rb") as f:
                argv = f.read().decode("utf-8", "replace").replace("\0", " ").strip()
        except (OSError, PermissionError):
            continue
        if cwd == case or cwd.startswith(case + os.sep) or case in argv:
            if "grade_crm_wb_lts" in argv:      # never count ourselves
                continue
            out.append({"pid": int(pid), "cwd": cwd, "argv": argv[:200]})
    return out


def _newest_artifact(case, app):
    """The newest thing the RUN itself writes.  Explicitly enumerated, because a glob
    over the case also catches files a grader or an editor touched."""
    cands = [os.path.join(case, "log." + app),
             os.path.join(case, "RC.txt"),
             os.path.join(case, "LAUNCH.log")]
    for sub in ("forceCoeffs", "forces"):
        d = os.path.join(case, "postProcessing", sub)
        if os.path.isdir(d):
            for t in os.listdir(d):
                td = os.path.join(d, t)
                if os.path.isdir(td):
                    cands += [os.path.join(td, f) for f in os.listdir(td)]
    best, best_m = None, -1.0
    for p in cands:
        try:
            m = os.path.getmtime(p)
        except OSError:
            continue
        if m > best_m:
            best, best_m = p, m
    return best, best_m


def liveness(case, app, now=None):
    now = time.time() if now is None else now
    procs = _procs_in(case)
    art, m = _newest_artifact(case, app)
    age = (now - m) if art else None
    rc_present = os.path.isfile(os.path.join(case, "RC.txt"))
    # LIVE if a process is in the case, OR the run's own artifacts are still moving
    # and no rc has been written.  The second clause is the conservative one and it is
    # there for L-41: an agent-owned solver need not appear in /proc under this user.
    live = bool(procs) or (age is not None and age < LIVE_MTIME_S and not rc_present)
    return {"live": live,
            "n_procs": len(procs),
            "procs": procs[:5],
            "newest_artifact": art,
            "newest_artifact_age_s": None if age is None else round(age, 1),
            "rc_file_present": rc_present,
            "stalled": (age is not None and age > STALL_S),
            "basis": "process table (/proc cwd + argv) and artifact mtime; "
                     "NEVER the log's contents"}


# ============================================================ 2. RULE 4 =========

def _read_rc(case):
    """`RC=<n>` in RC.txt.  NOT `launcher_rc` from the STATUS file, which that file
    itself labels `exit-status-of-the-launch-argv-NOT-the-solver-rc`."""
    p = os.path.join(case, "RC.txt")
    if not os.path.isfile(p):
        return None, "RC.txt absent"
    body = open(p).read().strip()
    m = re.search(r"^RC=(-?\d+)\s*$", body, re.M)
    if not m:
        return None, f"RC.txt does not carry an RC= line (contains {body!r})"
    return int(m.group(1)), None


def _controldict(case):
    p = os.path.join(case, "system", "controlDict")
    txt = open(p).read() if os.path.isfile(p) else ""
    def key(k, default=None):
        m = re.search(r"^\s*%s\s+([^;]+);" % re.escape(k), txt, re.M)
        return m.group(1).strip() if m else default
    return {"application": key("application"),
            "endTime": float(key("endTime", "nan")),
            "deltaT": float(key("deltaT", "nan")),
            "writeInterval": key("writeInterval"),
            "purgeWrite": key("purgeWrite")}


def required_fields(case):
    """Derived from the case's OWN closure dictionary, never hard-coded to one model.
    A14.3's lesson was a guard that names one model by literal and refuses the other;
    hard-coding `nuTilda` here would be that defect one field over."""
    p = os.path.join(case, "constant", "turbulenceProperties")
    txt = open(p).read() if os.path.isfile(p) else ""
    m = re.search(r"^\s*RASModel\s+(\w+)\s*;", txt, re.M)
    model = m.group(1) if m else None
    base = ["T", "U", "p", "rho", "alphat", "nut", "phi"]
    if model == "SpalartAllmaras":
        extra = ["nuTilda"]
    elif model in ("kOmegaSST", "kOmega", "kOmegaSSTLM"):
        extra = ["k", "omega"]
    elif model in ("kEpsilon", "realizableKE"):
        extra = ["k", "epsilon"]
    else:
        extra = None
    return model, (None if extra is None else tuple(base + extra))


def write_schedule(case):
    """🔴 CAN THIS CASE SATISFY RULE 4's FIELD CLAUSE AT ALL?

    OpenFOAM writes fields at multiples of `writeInterval` (writeControl timeStep).  If
    `endTime` is NOT one of them, NOTHING IS EVER WRITTEN AT endTime, the field clause
    and the age guard cannot pass, and the run grades NOT A RESULT on bookkeeping
    however sound its physics.  `purgeWrite N` then keeps only the most recent N of the
    writes that did happen, which is a SECOND, independent way to lose endTime.

    MEASURED ON THIS ACT'S OWN LTS RATE PROBE, 2026-09-13: endTime 20, writeInterval 6,
    purgeWrite 2.  It finished with rc=0, an `End` line, all 20 distinct steps and last
    time == endTime -- four of rule 4's six clauses -- and wrote fields at 6, 12 and 18,
    keeping 12 and 18.  There is no time-20 directory and there never could have been.

    This is a PRE-FLIGHT check: it reads only the dictionary, so it answers before the
    solver starts.  Sanaa's universal rule is that bookkeeping never voids physics, and
    the way to honour it is to not let bookkeeping break the run in the first place."""
    cd = _controldict(case)
    try:
        et = float(cd["endTime"])
        wi = float(cd["writeInterval"])
        pw = float(cd["purgeWrite"]) if cd["purgeWrite"] is not None else 0.0
    except (TypeError, ValueError):
        return {"readable": False,
                "note": "endTime/writeInterval not readable from system/controlDict"}
    if wi <= 0:
        return {"readable": False, "note": f"writeInterval {wi} is not positive"}
    n = et / wi
    lands = abs(n - round(n)) < 1e-9
    writes = [wi * (i + 1) for i in range(int(math.floor(et / wi + 1e-9)))]
    kept = writes[-int(pw):] if pw and pw > 0 else writes
    return {"readable": True, "endTime": et, "writeInterval": wi, "purgeWrite": pw,
            "endTime_is_a_write": lands,
            "writes_at": writes[:8] + (["..."] if len(writes) > 8 else []),
            "kept_after_purge": kept[-4:],
            "endTime_survives_purge": bool(kept) and abs(kept[-1] - et) < 1e-9,
            "note": ("endTime lands on a write and survives purgeWrite; rule 4's field "
                     "clause is reachable"
                     if lands and kept and abs(kept[-1] - et) < 1e-9 else
                     f"🔴 RULE 4's FIELD CLAUSE IS UNREACHABLE BY CONSTRUCTION: endTime "
                     f"{et:g} is {'not a multiple of' if not lands else 'purged by '
                     'purgeWrite from'} writeInterval {wi:g}"
                     f" (writes at {writes[-3:]}, kept {kept[-2:]}). No field is ever "
                     "written at endTime, so the field clause and the age guard cannot "
                     "pass however sound the physics.")}


def check_completion(case, end_time=None, delta_t=None, app=None):
    """Standing rule 4, EVERY clause, on the DECOMPOSED layout.  `ok` is the AND."""
    cd = _controldict(case)
    app = app or cd["application"] or "rhoPimpleFoam"
    end_time = cd["endTime"] if end_time is None else end_time
    delta_t = cd["deltaT"] if delta_t is None else delta_t
    r = {"case": case, "application": app, "endTime": end_time, "deltaT": delta_t,
         "write_schedule": write_schedule(case)}

    # -- clause 1: rc == 0
    rc, rc_err = _read_rc(case)
    r["rc"] = rc
    r["rc_error"] = rc_err
    r["clause_rc_zero"] = (rc == 0)

    # -- clauses 2,3,5: End line, last time == endTime, and the STEP SET.
    # The D631 reading: DISTINCT physics steps unioned across every log segment, and
    # the set must be exactly {1..endTime}.  Adopted from grade_suboff_a1h.py:212.
    sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))
    import solver_log_set as _sls
    sc = _sls.scan(case, app, end_time=end_time, delta_t=delta_t)
    r["clause_end_line"] = sc["end_line"]
    r["clause_last_eq_endTime"] = sc.get("clause_last_eq_endTime", False)
    r["clause_exec_count"] = sc.get("clause_exec_count", False)
    r["last_Time"] = sc["last_time"]
    r["n_steps_distinct"] = sc["n_steps"]
    r["n_exec_lines_raw_BOOKKEEPING"] = sc["n_exec_lines_raw"]
    r["n_log_segments"] = sc["n_segments"]
    r["resumed"] = sc["resumed"]
    r["missing_steps"] = sc.get("missing_steps", [])
    r["n_missing_steps"] = sc.get("n_missing_steps")
    r["unexpected_steps"] = sc.get("unexpected_steps", [])
    r["exec_count_reading"] = ("D631: DISTINCT physics steps unioned across log "
                               "segments, set == {1..endTime} exactly")

    # -- clause 4: fields present, at endTime, IN EVERY PROCESSOR TREE
    model, fields = required_fields(case)
    r["RASModel"] = model
    r["required_fields"] = fields
    procs = sorted(d for d in os.listdir(case)
                   if re.fullmatch(r"processor\d+", d)) if os.path.isdir(case) else []
    r["n_processor_trees"] = len(procs)
    if fields is None:
        r["clause_fields"] = False
        r["fields_error"] = (f"closure {model!r} is not in this comparator's registered "
                             "set; the required-field list cannot be derived and is not "
                             "guessed")
        r["fields_missing"] = None
    elif not procs:
        r["clause_fields"] = False
        r["fields_error"] = "no processorN trees: this comparator grades decomposed runs"
        r["fields_missing"] = None
    else:
        tname = _time_dirname(case, procs[0], end_time)
        r["endTime_dirname"] = tname
        missing = []
        for pd in procs:
            td = os.path.join(case, pd, tname) if tname else None
            present = set(os.listdir(td)) if td and os.path.isdir(td) else set()
            for f in fields:
                if f not in present:
                    missing.append(f"{pd}/{tname}/{f}")
        r["fields_missing"] = missing[:20]
        r["n_fields_missing"] = len(missing)
        r["clause_fields"] = (len(missing) == 0)

    # -- clause 6: THE AGE GUARD.
    # The case's own 0/ reference is written LAST at launch -- stage 0a writes U into
    # processor*/0 and stage 0b writes T, p and rho there (LAUNCH.log) -- so it dates
    # the run that was allowed to produce the answer.  The anchor taken is the NEWEST
    # file in processor*/0, which is the strictest available reading of rule 4.
    anchor, anchor_m = None, -1.0
    for pd in procs:
        z = os.path.join(case, pd, "0")
        if not os.path.isdir(z):
            continue
        for f in os.listdir(z):
            fp = os.path.join(z, f)
            try:
                m = os.path.getmtime(fp)
            except OSError:
                continue
            if m > anchor_m:
                anchor, anchor_m = fp, m
    r["age_anchor"] = anchor
    if anchor and r.get("clause_fields") and fields:
        tname = r["endTime_dirname"]
        margins = {}
        worst = None
        for pd in procs:
            for f in fields:
                fp = os.path.join(case, pd, tname, f)
                try:
                    d = os.path.getmtime(fp) - anchor_m
                except OSError:
                    d = None
                if d is None:
                    worst = -1.0
                    margins[f"{pd}/{f}"] = None
                    continue
                if worst is None or d < worst:
                    worst = d
                    margins["worst"] = {"file": f"{pd}/{tname}/{f}", "margin_s": round(d, 3)}
        r["age_margin_worst"] = margins.get("worst")
        r["clause_age_guard"] = (worst is not None and worst > 0.0)
    else:
        r["age_margin_worst"] = None
        r["clause_age_guard"] = False

    r["ok"] = all([r["clause_rc_zero"], r["clause_end_line"],
                   r["clause_last_eq_endTime"], r["clause_exec_count"],
                   r["clause_fields"], r["clause_age_guard"]])
    return r


def _time_dirname(case, proc, t):
    """OpenFOAM writes `96`, not `96.0`.  Find the directory that IS this time."""
    d = os.path.join(case, proc)
    if not os.path.isdir(d):
        return None
    for name in os.listdir(d):
        try:
            if abs(float(name) - float(t)) < 1e-9:
                return name
        except ValueError:
            continue
    return None


# ================================================= 3. THE BINARY FIELD READER ===
# L5 is registered as a FIELD reading, "never from a normalised residual", so it is
# read out of the field files themselves.  Format confirmed on this box:
#   format binary; arch "LSB;label=32;scalar=64"
#   internalField   nonuniform List<vector>\n<N>\n(<N*3 float64 LE>)

_IF_RE = re.compile(rb"internalField\s+(nonuniform|uniform)\s+(?:List<(scalar|vector)>)?")


def read_internal_field(path):
    """Return (kind, values).  kind is 'scalar' or 'vector'; values is a flat list of
    floats (vector: 3 per cell).  Handles binary and ascii, uniform and nonuniform."""
    with open(path, "rb") as f:
        blob = f.read()
    fmt = b"binary" if re.search(rb"format\s+binary\s*;", blob[:2000]) else b"ascii"
    m = _IF_RE.search(blob)
    if not m:
        raise ValueError(f"{path}: no internalField entry")
    kind = (m.group(2) or b"scalar").decode()
    if m.group(1) == b"uniform":
        tail = blob[m.end():m.end() + 200].decode("utf-8", "replace")
        nums = [float(x) for x in re.findall(r"-?\d+\.?\d*(?:[eE][+-]?\d+)?", tail)]
        n = 3 if kind == "vector" else 1
        return kind, nums[:n]
    rest = blob[m.end():]
    mn = re.match(rb"\s*(\d+)\s*\(", rest)
    if not mn:
        raise ValueError(f"{path}: nonuniform list without a count")
    n = int(mn.group(1))
    start = m.end() + mn.end()
    ncomp = 3 if kind == "vector" else 1
    if fmt == b"binary":
        need = n * ncomp * 8
        if len(blob) < start + need:
            raise ValueError(f"{path}: truncated binary payload "
                             f"(need {need} bytes, have {len(blob) - start})")
        raw = blob[start:start + need]
        if _np is not None:
            # 20.6 M cells over 32 trees is 500 MB of doubles; a Python-level loop over
            # it is minutes.  numpy is used ONLY to decode and reduce -- the byte layout
            # asserted above is the same one struct.unpack reads, and P-F proves the two
            # agree on a planted value.
            return kind, _np.frombuffer(raw, dtype="<f8")
        vals = struct.unpack("<%dd" % (n * ncomp), raw)
        return kind, list(vals)
    tail = blob[start:].decode("utf-8", "replace")
    toks = re.findall(r"-?\d+\.?\d*(?:[eE][+-]?\d+)?", tail)
    return kind, [float(x) for x in toks[:n * ncomp]]


def field_extrema(case, tname, field):
    """max/min of a scalar field, or max magnitude of a vector field, over EVERY
    processor tree.  Returns None if the field is not on disk."""
    procs = sorted(d for d in os.listdir(case) if re.fullmatch(r"processor\d+", d))
    lo, hi, mag, ncell, seen = math.inf, -math.inf, 0.0, 0, 0
    for pd in procs:
        p = os.path.join(case, pd, tname, field)
        if not os.path.isfile(p):
            continue
        kind, v = read_internal_field(p)
        seen += 1
        if _np is not None and not isinstance(v, list):
            if kind == "vector":
                a = v.reshape(-1, 3)
                m = float(_np.sqrt((a * a).sum(axis=1)).max()) if a.size else 0.0
                mag = max(mag, m)
                ncell += a.shape[0]
            else:
                if v.size:
                    lo = min(lo, float(v.min()))
                    hi = max(hi, float(v.max()))
                ncell += v.size
            continue
        if kind == "vector":
            for i in range(0, len(v), 3):
                m = math.sqrt(v[i] ** 2 + v[i + 1] ** 2 + v[i + 2] ** 2)
                if m > mag:
                    mag = m
            ncell += len(v) // 3
        else:
            for x in v:
                if x < lo:
                    lo = x
                if x > hi:
                    hi = x
            ncell += len(v)
    if seen == 0:
        return None
    return {"field": field, "time": tname, "trees_read": seen, "n_cells": ncell,
            "min": None if lo is math.inf else lo,
            "max": None if hi == -math.inf else hi,
            "max_magnitude": mag if mag else None}


# ============================================ 4. FORCE COEFFICIENTS, BY NAME ====
# THE TRAP THIS FUNCTION EXISTS FOR.  `awk '{print $3}'` on this file returns `Cd(f)`,
# not `Cd`, because column 1 is Time.  That reading halved a drag figure in this lab
# and a mechanism was invented to explain it.  Every column here is located BY NAME in
# the file's own header line, and the split identities are carried as controls.

SPLIT_TOL_REL = 1.0e-6


def read_coefficients(case, want_times=None):
    """Read `coefficient.dat` by column NAME.  Returns {time: {name: value}}.

    The file's LAST header comment line that starts with `# Time` carries the names,
    tab-separated.  A file with no such line is REFUSED -- an unnamed column is not a
    column this comparator will read."""
    root = os.path.join(case, "postProcessing", "forceCoeffs")
    if not os.path.isdir(root):
        return {}, {"error": "no postProcessing/forceCoeffs directory"}
    files = []
    for t in sorted(os.listdir(root), key=lambda s: (_fkey(s))):
        p = os.path.join(root, t, "coefficient.dat")
        if os.path.isfile(p):
            files.append(p)
    if not files:
        return {}, {"error": "no coefficient.dat under postProcessing/forceCoeffs"}
    out, meta = {}, {"files": files, "header_from": None, "columns": None}
    for p in files:
        names = None
        for line in open(p):
            if line.startswith("#"):
                if line.startswith("# Time"):
                    names = [c.strip() for c in line[1:].rstrip("\n").split("\t")
                             if c.strip()]
                    meta["header_from"] = p
                    meta["columns"] = names
                continue
            if names is None:
                refuse(f"{p}: data rows before any `# Time ...` header line. "
                       "This comparator will not read a column by position.")
            parts = line.rstrip("\n").split("\t")
            parts = [q.strip() for q in parts if q.strip() != ""]
            if len(parts) != len(names):
                # a torn last line while the solver is mid-write; skip it, and say so
                meta.setdefault("short_rows", 0)
                meta["short_rows"] += 1
                continue
            row = {}
            ok = True
            for nm, val in zip(names, parts):
                try:
                    row[nm] = float(val)
                except ValueError:
                    ok = False
            if not ok or "Time" not in row:
                continue
            t = row.pop("Time")
            if want_times is None or any(abs(t - w) < 1e-9 for w in want_times):
                out[t] = row               # a later segment overwrites an earlier one
    return out, meta


def _fkey(s):
    try:
        return (0, float(s))
    except ValueError:
        return (1, s)


def split_identity_control(row):
    """Cd(f)+Cd(r) == Cd and Cl(f)+Cl(r) == Cl, on the row actually being graded.

    This is an ARITHMETIC control on the numbers, not a check that the gate fired.  If
    it fails, the file is not being read the way the writer wrote it and NO coefficient
    from it may be quoted."""
    checks = {}
    for tot, fwd, aft in (("Cd", "Cd(f)", "Cd(r)"), ("Cl", "Cl(f)", "Cl(r)"),
                          ("Cs", "Cs(f)", "Cs(r)")):
        if tot in row and fwd in row and aft in row:
            s = row[fwd] + row[aft]
            scale = max(abs(row[tot]), abs(row[fwd]), abs(row[aft]), 1.0e-30)
            checks[tot] = {"total": row[tot], "sum_of_split": s,
                           "abs_err": abs(s - row[tot]),
                           "rel_err": abs(s - row[tot]) / scale,
                           "ok": abs(s - row[tot]) / scale <= SPLIT_TOL_REL}
    return checks


# ============================== 4a. IS A FORCE READABLE FROM THIS CASE AT ALL? ==
# A15.6(c), discharged 2026-09-13.  THIS IS A REFUSAL-ONLY GATE: standing rule 5 lets a
# gate turn a PASS or a GATE FAIL INTO `NOT A RESULT` and never the reverse, so coupling
# the force channel to the field state can only ever withhold a number, never produce or
# improve one.  That is why it may be added without touching a frozen threshold.
#
# 🔴 THE HAZARD, MEASURED ON `SOLVE_T_SST`'s OWN ARTIFACT, NOT HYPOTHESISED.
# That run died of SIGFPE at iteration 22 with the field at `p max 3.86761822375e+129`.
# Its `forceCoeffs` log blocks carry Total / Pressure / Viscous / Internal, and the
# PRESSURE column is quiet while the total is destroyed:
#
#     step  3  Total Cd -5.629357e+01    Pressure Cd +0.08000426
#     step  4  Total Cd -1.604469e+02    Pressure Cd +0.05376081
#     step  5  Total Cd -7.848507e+03    Pressure Cd +0.04040391
#     step  6  Total Cd -1.771947e+05    Pressure Cd +0.01696321
#     step  7  Total Cd +1.886737e+08    Pressure Cd +0.00037753
#     step 21  Total Cd -4.414128e+88    Pressure Cd +0.00912114
#
# SIX OF TWENTY-ONE STEPS CARRY A PRESSURE Cd INSIDE A15.7 L3's OWN ADMISSIBLE BAND
# [0, 0.2], on a run that crashed.  A reader that mines the pressure column finds a
# plausible, L3-passing drag coefficient in a destroyed solution.
#
# 🔴 AND AN HONEST LIMIT OF MY OWN P-B CONTROL, STATED RATHER THAN LEFT TO BE FOUND.
# The split identity Cd(f)+Cd(r) == Cd PASSES on SST's artifact -- measured, rel_err
# 8.64e-14.  An arithmetic identity is NECESSARY AND NOT SUFFICIENT: the file is
# perfectly self-consistent while being garbage.  Only the field coupling below
# separates the two, which is why P-B alone was never enough.

FORCE_COMPONENT_NAMES = ("Pressure", "Viscous", "Internal", "pressure", "viscous")


def force_is_readable(case, comp):
    """May ANY force number be quoted from this case?  Refusal-only (rule 5).

    Three independent clauses, ANY ONE of which withholds every force:

      F-1  THE FIELD IS NOT ADMISSIBLE.  A15.7 L5's own field gate, reused: if p or
           max|U| is outside its registered ceiling, or the field cannot be read at all,
           no force integrated over that field is evidence.  A15.3 measured a finite,
           ordinary-looking pressure-force integral on a field at 1e+129.
      F-2  THE CLAMP WAS HIDING AN EXCURSION.  If pressureControl reported a pre-clamp
           max over L5's ceiling, the written field understates what the pressure
           equation produced, and a force integrated over the written field is
           integrating a clamped surrogate.  DISCLOSURE-SOURCED, so it is reported and
           may refuse, but per the 2026-09-13 containment ruling it changes no L5
           verdict -- withholding a force is not an L5 verdict.
      F-3  THE PLANTED-FORCE CONTROL HAS NOT PASSED under this application (A15.6(c)).

    A case that fails none of the three is readable.  Nothing here can make a force
    BETTER; it can only decline to serve one."""
    r = {"refusals": [], "clauses": {}}
    l5 = comp.get("L5", {}) or {}
    r["clauses"]["F-1_field_admissible"] = (l5.get("verdict") == "PASS")
    if l5.get("verdict") != "PASS":
        r["refusals"].append(
            f"F-1: the field gate does not PASS (L5 {l5.get('verdict')!r}: "
            f"{l5.get('reason') or 'p or max|U| outside its registered ceiling'}). "
            "A force integrated over a field that is not admissible is not evidence, "
            "however ordinary the number looks -- SST's pressure Cd was +0.00912114 "
            "while its field stood at p max 3.87e+129.")
    pre = (l5.get("p_clause_reachability") or {}).get("preclamp") or {}
    over = bool(pre.get("exceeds_L5_ceiling"))
    r["clauses"]["F-2_no_hidden_clamp_excursion"] = not over
    if over:
        r["refusals"].append(
            f"F-2: pressureControl reported a pre-clamp max of "
            f"{pre.get('preclamp_p_max_Pa')} Pa on {pre.get('n_steps_over_clamp')} steps, "
            f"over L5's ceiling of {L5_P_ABS_MAX} Pa. The written field is a clamped "
            "surrogate for what the pressure equation produced, so a force integrated "
            "over it is integrating the clamp.")
    ok_plant = (comp.get("force_plant_control") == "PASS")
    r["clauses"]["F-3_planted_force_control_passed"] = ok_plant
    if not ok_plant:
        r["refusals"].append(
            f"F-3: A15.6(c)'s planted-force control is {comp.get('force_plant_control')!r} "
            "under this application; a force from a reader never shown able to be wrong "
            "is not evidence.")
    r["readable"] = not r["refusals"]
    r["basis"] = ("REFUSAL-ONLY gate (rule 5): it can turn a force reading into NOT A "
                  "RESULT and can never produce, improve or rescue one.")
    return r


def refuse_component_as_force(name):
    """A pressure or viscous COMPONENT IS NOT A FORCE, and this reader will not serve
    one under that name.  The hazard is not hypothetical: `Cd(f)` was once read as `Cd`
    in this lab and drag was reported halved, and SST's Pressure column is quiet on six
    of twenty-one steps of a crashed run."""
    if any(c in str(name) for c in FORCE_COMPONENT_NAMES):
        refuse(f"{name!r} is a force COMPONENT, not a force. This comparator serves only "
               "the Total, because a component can look ordinary while the total and the "
               "field it came from are destroyed (SST: Pressure Cd +0.00912114 at "
               "p max 3.87e+129).")
    return name


# ================================================== 5. THE A15.7 LOG CHANNELS ===

_TIME_RE   = re.compile(r"^Time = ([0-9.eE+-]+)\s*$", re.M)
_RESID_RE  = re.compile(r"Solving for (\w+),\s+Initial residual = ([0-9.eE+-]+)")
_LIMIT_RE  = re.compile(r"limitTemperature=(\w+), Type=(\w+), LimitedCells=(\d+), "
                        r"CellsPercent=([0-9.eE+-]+)")
_PCTRL_RE  = re.compile(r"pressureControl: p (max|min) ([0-9.eE+-]+)")
_COURANT_RE = re.compile(r"Courant Number mean: ([0-9.eE+-]+) max: ([0-9.eE+-]+)")
_EXEC_RE   = re.compile(r"^ExecutionTime = ([0-9.eE+-]+) s\s+ClockTime = ([0-9.eE+-]+)", re.M)


def read_log_channels(case, app):
    """Per-time-step channels, read from EVERY log segment and keyed by physics step.

    A later segment's reading of a step REPLACES an earlier one: after a resume the
    re-run step is the one that produced the fields on disk."""
    sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))
    import solver_log_set as _sls
    steps = {}
    for p in _sls.segments(case, app):
        body = p.read_text(errors="replace")
        cuts = [(m.start(), float(m.group(1))) for m in _TIME_RE.finditer(body)]
        for i, (pos, t) in enumerate(cuts):
            end = cuts[i + 1][0] if i + 1 < len(cuts) else len(body)
            blk = body[pos:end]
            d = {"segment": p.name}
            res = {}
            for m in _RESID_RE.finditer(blk):
                res.setdefault(m.group(1), []).append(float(m.group(2)))
            d["initial_residuals"] = res
            lim = {}
            for m in _LIMIT_RE.finditer(blk):
                lim.setdefault(m.group(2), []).append(float(m.group(4)))
            d["limitTemperature_pct"] = lim
            pc = {}
            for m in _PCTRL_RE.finditer(blk):
                pc[m.group(1)] = float(m.group(2))
            d["pressureControl"] = pc
            co = _COURANT_RE.findall(blk)
            d["courant_max"] = float(co[-1][1]) if co else None
            ex = _EXEC_RE.findall(blk)
            d["ExecutionTime_s"] = float(ex[-1][0]) if ex else None
            steps[t] = d
    return steps


def _h_residual(step):
    """L1's channel: the `h` initial residual of the FINAL energy solve of the step.

    Under PIMPLE at nOuterCorrectors 1 the solve is named `hFinal`; under SIMPLE it is
    `h`.  Both names are looked for BY NAME and the LAST occurrence in the step is
    taken, because L1 is registered on the final corrector."""
    res = step.get("initial_residuals", {})
    for nm in ("hFinal", "h", "eFinal", "e"):
        if nm in res and res[nm]:
            return nm, res[nm][-1]
    return None, None


def _clamp_total(step):
    """L2's channel: BOTH limitTemperature branches SUMMED at the single constrain
    call of the time step (A15.5 fixes nOuterCorrectors 1 so there is exactly one).

    A15.2's honesty flag: quoting the Upper branch alone as the total is what this act
    had to correct once already.  Both branches are summed here and both are reported."""
    lim = step.get("limitTemperature_pct", {})
    if not lim:
        return None, {}
    branches = {k: v[-1] for k, v in lim.items() if v}
    return sum(branches.values()), branches


def evaluate_L(case, app, steps, coeffs, comp):
    """A15.7 L1..L5.  Each returns PASS / GATE FAIL / NOT A RESULT with its number."""
    out = {}
    have = sorted(steps)

    # ---- L1
    if not have:
        out["L1"] = {"verdict": "NOT A RESULT", "reason": "no time steps in the log"}
    else:
        reached = [t for t in have if t <= L1_BY_STEP]
        if not reached or max(reached) < L1_BY_STEP:
            out["L1"] = {"verdict": "NOT A RESULT",
                         "reason": f"the run did not reach time step {L1_BY_STEP} "
                                   f"(last {max(have)}); the reading point registered "
                                   "for L1 was never reached and cannot be cleared"}
        else:
            nm, v = _h_residual(steps[max(reached)])
            best_nm, best = None, None
            for t in reached:
                n2, v2 = _h_residual(steps[t])
                if v2 is not None and (best is None or v2 < best):
                    best_nm, best = n2, v2
            out["L1"] = {"verdict": "PASS" if (best is not None and best < L1_RESIDUAL_CEIL)
                                    else "GATE FAIL",
                         "channel": best_nm, "min_initial_residual_to_step_20": best,
                         "at_step_20": v, "ceiling": L1_RESIDUAL_CEIL}

    # ---- L2
    reached = [t for t in have if t <= L2_BY_STEP]
    if not reached or max(reached) < L2_BY_STEP:
        # THE LAST MEASURED READING, NOT THE LAST STEP.  A run killed mid-step leaves a
        # final `Time =` block with no constrain call in it, and reporting that block's
        # empty reading as "the last total" prints `null` where the honest answer is
        # 60.87 % at step 21.  Search backwards for the last step that CARRIES one.
        last_t, last_tot, last_br = None, None, {}
        for t in reversed(have):
            tot, br = _clamp_total(steps[t])
            if tot is not None:
                last_t, last_tot, last_br = t, tot, br
                break
        out["L2"] = {"verdict": "NOT A RESULT",
                     "reason": f"time step {L2_BY_STEP} never reached "
                               f"(last {max(have) if have else None})",
                     "last_measured_at_step": last_t,
                     "last_total_pct": last_tot,
                     "last_branches": last_br}
    else:
        tot, br = _clamp_total(steps[L2_BY_STEP if L2_BY_STEP in steps else max(reached)])
        out["L2"] = {"verdict": ("NOT A RESULT" if tot is None else
                                 "PASS" if tot < L2_CLAMP_CEIL_PCT else "GATE FAIL"),
                     "total_pct_BOTH_BRANCHES": tot, "branches": br,
                     "ceiling_pct": L2_CLAMP_CEIL_PCT}

    # ---- L3.  Registered as readable ONLY after the planted-force control passes.
    fr = force_is_readable(case, comp)
    out["force_readability"] = fr
    if not fr["readable"]:
        out["L3"] = {"verdict": "NOT A RESULT",
                     "reason": "; ".join(fr["refusals"]),
                     "force_readability": fr}
    elif not coeffs:
        out["L3"] = {"verdict": "NOT A RESULT", "reason": "no coefficient rows read"}
    else:
        ts = [t for t in sorted(coeffs) if t <= L3_THROUGH_STEP]
        bad = []
        for t in ts:
            row = coeffs[t]
            cd, cl = row.get("Cd"), row.get("Cl")
            if cd is None or cl is None:
                bad.append((t, "Cd or Cl column absent by NAME"))
            elif not (L3_CD_RANGE[0] <= cd <= L3_CD_RANGE[1]):
                bad.append((t, f"Cd={cd:.6g} outside {L3_CD_RANGE}"))
            elif not (L3_CL_RANGE[0] <= cl <= L3_CL_RANGE[1]):
                bad.append((t, f"Cl={cl:.6g} outside {L3_CL_RANGE}"))
        if ts and max(ts) < L3_THROUGH_STEP:
            out["L3"] = {"verdict": "NOT A RESULT",
                         "reason": f"read only to step {max(ts)} of {L3_THROUGH_STEP}",
                         "first_excursion": bad[0] if bad else None,
                         "n_excursions": len(bad)}
        else:
            out["L3"] = {"verdict": "PASS" if not bad else "GATE FAIL",
                         "n_excursions": len(bad), "first_excursion": bad[0] if bad else None,
                         "steps_read": len(ts)}

    # ---- L4
    cos = [(t, steps[t]["courant_max"]) for t in have if steps[t].get("courant_max") is not None]
    if not cos:
        out["L4"] = {"verdict": "NOT A RESULT",
                     "reason": "no `Courant Number mean: .. max: ..` line in the log; "
                               "the LTS field's own channel was never written, so L4 "
                               "cannot be read and is not inferred from anything else"}
    else:
        worst = max(c for _, c in cos)
        finite = all(math.isfinite(c) for _, c in cos)
        out["L4"] = {"verdict": ("NOT A RESULT" if not finite else
                                 "PASS" if worst <= L4_MAX_CO else "GATE FAIL"),
                     "courant_max_over_run": worst, "registered_maxCo": L4_MAX_CO,
                     "all_finite": finite, "steps_with_courant": len(cos)}

    # ---- L5.  FROM THE FIELD.
    out["L5"] = comp.get("L5", {"verdict": "NOT A RESULT", "reason": "not evaluated"})
    return out


_PCTRL_LIMIT_RE = re.compile(r"^\s+p(Max|Min)\s+([0-9.eE+-]+)\s*$", re.M)


def preclamp_pressure(case, app):
    """🔴 WHAT THE PRESSURE EQUATION ACTUALLY PRODUCED, BEFORE THE CLAMP HID IT.

    `pressureControl::limit` (pressureControl.C:236-243 on this build) prints
    `pressureControl: p max <X>` with the OBSERVED max **and only when X exceeds the
    clamp**, then writes `p = min(p, pMax_)`.  So X is a pre-clamp field reading that
    never survives into any written field, and `field_extrema` on the written `p`
    CANNOT see it.

    This is not a nicety.  On the LTS rate probe, 2026-09-13, the solver's own
    construction banner printed `pMax 8014.789298` / `pMin 400.7394649`, and the
    pre-clamp max exceeded the clamp on ALL TWENTY steps, reaching 20176.5848879 Pa --
    which is 1.57x A15.7 L5's registered ceiling of 12854 Pa.  L5 read from the written
    field would have returned PASS on a field whose own pressure equation had gone over
    the gate on every step.  A gate that cannot fire is bad; a gate that cannot fire
    BECAUSE A CLAMP IS HIDING THE EXCURSION IT GATES ON is worse, and it is reported
    here beside L5 rather than left to be discovered after a verdict."""
    sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))
    import solver_log_set as _sls
    mx, mn, limits = [], [], {}
    for pth in _sls.segments(case, app):
        body = pth.read_text(errors="replace")
        for m in _PCTRL_LIMIT_RE.finditer(body):
            limits["p" + m.group(1)] = float(m.group(2))
        for m in _PCTRL_RE.finditer(body):
            (mx if m.group(1) == "max" else mn).append(float(m.group(2)))
    return {"solver_printed_clamp": limits or None,
            "n_steps_over_clamp": len(mx),
            "preclamp_p_max_Pa": max(mx) if mx else None,
            "preclamp_p_min_Pa": min(mn) if mn else None,
            "exceeds_L5_ceiling": (bool(mx) and max(mx) >= L5_P_ABS_MAX),
            "L5_registered_ceiling_Pa": L5_P_ABS_MAX,
            "basis": "pressureControl's own pre-clamp print; the WRITTEN field cannot "
                     "show this, because the clamp is applied before it is written"}


def p_clause_reachable(case):
    """CAN L5's p CLAUSE EVER FIRE UNDER THE DICTIONARY THAT WILL RUN?

    `pressureControl` clamps p to [pMinFactor, pMaxFactor] x p_ref.  If pMaxFactor x
    p_inf is BELOW L5's registered ceiling then p can never reach that ceiling and the
    clause is unfailable by construction -- a clause that cannot fail is not a clause,
    which is this act's own standard (A15.4, and `solver_log_set` fixture 8).

    MEASURED, not inferred: R1's field at t = 96 sits at p in
    [400.73946490000003, 8014.789298] Pa -- EXACTLY 0.1 x p_inf and EXACTLY 2.0 x p_inf
    -- while max|U| in the same field is 4.115107168072133e+22 m/s.  The clamp holds p
    inside the gate while the solution is destroyed, so the U half of L5 is the half
    that carries the clause and it may not be dropped."""
    txt = ""
    fp = os.path.join(case, "system", "fvSolution")
    if os.path.isfile(fp):
        txt = open(fp).read()
    m = re.search(r"^\s*pMaxFactor\s+([0-9.eE+-]+)\s*;", txt, re.M)
    if not m:
        return {"pMaxFactor": None,
                "note": "no pMaxFactor in system/fvSolution; reachability not established"}
    f = float(m.group(1))
    ceil_pa = f * P_INF
    return {"pMaxFactor": f, "p_ref_Pa": P_INF, "clamp_ceiling_Pa": ceil_pa,
            "L5_registered_ceiling_Pa": L5_P_ABS_MAX,
            "p_clause_can_fire": ceil_pa >= L5_P_ABS_MAX,
            "note": ("the p half of L5 CANNOT FIRE under this dictionary: pressureControl "
                     f"caps p at {ceil_pa:.6f} Pa, below the registered ceiling "
                     f"{L5_P_ABS_MAX} Pa. The U half is the half that carries L5."
                     if ceil_pa < L5_P_ABS_MAX else
                     "the p half of L5 can fire under this dictionary")}


def _l5_verdict_from_field(pe, ue):
    """L5's VERDICT, computed from the FIELD READINGS AND NOTHING ELSE.

    🔴 THE CONTAINMENT IS THE FUNCTION SIGNATURE.  `preclamp_pressure` is not in this
    function's scope and cannot be, so it cannot reach an L5 verdict without an edit
    that changes this signature -- and that edit is a named mutation site below.  See
    the ruling quoted in `evaluate_L5`."""
    if pe is None or ue is None:
        return "NOT A RESULT", None, None
    pmax = max(abs(pe["max"] or 0.0), abs(pe["min"] or 0.0))
    umax = ue["max_magnitude"]
    ok = (math.isfinite(pmax) and math.isfinite(umax)
          and pmax < L5_P_ABS_MAX and umax < L5_U_MAG_MAX)
    return ("PASS" if ok else "GATE FAIL"), pmax, umax


def evaluate_L5(case, comp, app="rhoPimpleFoam"):
    """p absolute max < 2 p0 and max|U| < 2 U_inf, READ FROM THE FIELD FILES.

    A15.7 says `read from the field, never from a normalised residual`.

    🔴 PROVENANCE AND CONTAINMENT OF THE `preclamp` CHANNEL -- RULING OF 2026-09-13,
    cfd-supervisor, on discharging check 1 against commit b0fbbb837, and BINDING:

        `preclamp_pressure` IS A DISCLOSURE CHANNEL, NEVER A GATE.

    It was written AFTER the LTS rate probe's log existed.  A15's gates and thresholds
    were frozen before compute and are untouched, so the freeze holds -- but a
    comparator channel added in response to data is exactly the shape pre-registration
    exists to prevent, and its provenance is disclosed here rather than left for a
    reader to reconstruct.  Therefore:

      * it may not change any L5 verdict, IN EITHER DIRECTION;
      * it is reported BESIDE L5 with its basis stated, never AS L5;
      * if a future rung wants the pre-clamp pressure to gate, that is a NEW
        REGISTRATION WRITTEN BEFORE THAT RUN, not this channel promoted.

    Enforced two ways, because a ruling nobody asserts is a ruling nobody keeps
    (standing rule 14): the verdict is computed by `_l5_verdict_from_field`, whose
    scope does not contain the channel; and P-M drives this function over the SAME case
    with and without a planted pre-clamp excursion and requires byte-identical output
    but for the disclosure itself."""
    reach = p_clause_reachable(case)          # set FIRST, so EVERY return path carries it
    reach["preclamp"] = preclamp_pressure(case, app)
    reach["preclamp"]["status"] = ("DISCLOSURE CHANNEL, NEVER A GATE -- added after the "
                                   "probe log existed; ruling of 2026-09-13. It changes "
                                   "no L5 verdict in either direction.")
    tname = comp.get("endTime_dirname")
    if not tname:
        return {"verdict": "NOT A RESULT", "p_clause_reachability": reach,
                "reason": "no endTime field directory on disk, so the field cannot be read"}
    pe = field_extrema(case, tname, "p")
    ue = field_extrema(case, tname, "U")
    verdict, pmax, umax = _l5_verdict_from_field(pe, ue)
    if pe is None or ue is None:
        return {"verdict": verdict, "p_clause_reachability": reach,
                "reason": f"p or U absent at time {tname}",
                "p": pe, "U": ue}
    return {"verdict": verdict,
            "p_clause_reachability": reach,
            "p_abs_max_Pa": pmax, "p_ceiling_Pa": L5_P_ABS_MAX,
            "U_mag_max_m_s": umax, "U_ceiling_m_s": L5_U_MAG_MAX,
            "p_min_Pa": pe["min"], "p_max_Pa": pe["max"],
            "cells_read": pe["n_cells"], "processor_trees_read": pe["trees_read"],
            "basis": "binary internalField of p and U in every processor tree"}


# ==================================================== 6. THE §5 BAND GATE =======

def gate_forces(row, ref):
    """§5.5.  PASS iff |Q_cfd - Q_NTF| <= band, for each of CL, CD, CM."""
    out = {"band_CL": BAND_CL, "band_CD": BAND_CD, "band_CM": BAND_CM,
           "band_widths_are": "HALF widths (§5, width convention stated and converted once)"}
    if ref is None:
        out["verdict"] = "BLOCKED"
        out["reason"] = ("no NTF reference row registered for this grade; §5 gates "
                         "against NTF Test 197 and the reference row selection rule is "
                         "not frozen in the pre-registration text this comparator reads")
        return out
    pairs = [("CL", row.get("Cl"), ref.get("CL"), BAND_CL),
             ("CD", row.get("Cd"), ref.get("CD"), BAND_CD),
             ("CM", row.get("CmPitch"), ref.get("CM"), BAND_CM)]
    worst = "PASS"
    for nm, cfd, exp, band in pairs:
        if cfd is None or exp is None:
            out[nm] = {"verdict": "NOT A RESULT", "cfd": cfd, "ntf": exp}
            worst = "NOT A RESULT"
            continue
        dev = cfd - exp
        v = "PASS" if abs(dev) <= band else "GATE FAIL"
        out[nm] = {"verdict": v, "cfd": cfd, "ntf": exp, "deviation": dev,
                   "band": band,
                   "counts": (dev * 1.0e4 if nm == "CD" else None)}
        if v == "GATE FAIL" and worst == "PASS":
            worst = "GATE FAIL"
    out["verdict"] = worst
    return out


# ================================================================ 7. DRIVER =====

def grade(case, mode="grade", ref=None, force_plant_control="NOT RUN", now=None):
    rep = {"comparator": os.path.relpath(os.path.abspath(__file__), REPO_ROOT),
           "prereg": PREREG, "prereg_version": PREREG_VERSION,
           "case": os.path.abspath(case), "mode": mode,
           "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))}
    cd = _controldict(case)
    app = cd["application"] or "rhoPimpleFoam"
    rep["controlDict"] = cd

    live = liveness(case, app, now=now)
    rep["liveness"] = live

    if mode == "monitor":
        # THE 37-MINUTE LESSON.  A rate or a progress figure from a log that has
        # stopped is not a rate.  Refuse; do not report.
        if live["stalled"] or not live["live"]:
            rep["verdict"] = "BLOCKED"
            rep["reason"] = (f"--monitor refuses: the run is NOT live. Newest artifact "
                             f"{live['newest_artifact']} was last written "
                             f"{live['newest_artifact_age_s']} s ago and "
                             f"{live['n_procs']} processes are in the case. A rate read "
                             "from a stopped log is not a rate; this lab published one "
                             "from logs frozen 37 minutes.")
            return rep
        steps = read_log_channels(case, app)
        have = sorted(steps)
        rep["steps_reached"] = len(have)
        rep["last_step"] = have[-1] if have else None
        exs = [(t, steps[t]["ExecutionTime_s"]) for t in have
               if steps[t].get("ExecutionTime_s") is not None]
        if len(exs) >= 2:
            rep["s_per_step_measured"] = ((exs[-1][1] - exs[0][1]) /
                                          max(1e-9, (exs[-1][0] - exs[0][0])))
            rep["rate_basis"] = ("the solver's own ExecutionTime across the steps read, "
                                 "on a log proven live above")
        rep["verdict"] = "PENDING"
        rep["reason"] = "run is live; no verdict is taken on a moving target"
        return rep

    # ---- grade mode
    if live["live"]:
        rep["verdict"] = "PENDING"
        rep["reason"] = (f"the run is LIVE ({live['n_procs']} processes in the case; "
                         f"newest artifact {live['newest_artifact_age_s']} s old). A "
                         "grade of a moving target is not a grade. PENDING is a queue "
                         "state, not a softened GATE FAIL.")
        return rep

    comp = check_completion(case, app=app)
    rep["completion"] = comp
    rep["force_plant_control"] = force_plant_control
    comp["force_plant_control"] = force_plant_control
    comp["L5"] = evaluate_L5(case, comp, app)

    steps = read_log_channels(case, app)
    coeffs, cmeta = read_coefficients(case)
    rep["coefficient_file"] = cmeta
    rep["L_channels"] = evaluate_L(case, app, steps, coeffs, comp)

    # the force row that would be graded, with its arithmetic controls
    et = comp["endTime"]
    row = coeffs.get(et) or (coeffs[max(coeffs)] if coeffs else None)
    if row is not None:
        rep["force_row_time"] = et if et in coeffs else (max(coeffs) if coeffs else None)
        rep["force_row"] = {k: row[k] for k in
                            ("Cd", "Cd(f)", "Cd(r)", "Cl", "Cl(f)", "Cl(r)", "CmPitch")
                            if k in row}
        ident = split_identity_control(row)
        rep["split_identity_control"] = ident
        if any(not c["ok"] for c in ident.values()):
            rep["verdict"] = "NOT A RESULT"
            rep["reason"] = ("the coefficient file's own split columns do not sum to its "
                             "totals, so the file is not being read the way it was "
                             "written and NO coefficient from it may be quoted: "
                             + json.dumps({k: v for k, v in ident.items() if not v["ok"]}))
            return rep

    # ---- the verdict.
    if not comp["ok"]:
        rep["verdict"] = "NOT A RESULT"
        failed = [k for k in ("clause_rc_zero", "clause_end_line", "clause_last_eq_endTime",
                              "clause_exec_count", "clause_fields", "clause_age_guard")
                  if not comp[k]]
        ws = comp.get("write_schedule", {})
        extra = ""
        if ws.get("readable") and not ws.get("endTime_survives_purge"):
            extra = (" -- AND THE FIELD CLAUSES WERE UNREACHABLE BY CONSTRUCTION: "
                     + ws["note"])
        rep["reason"] = ("standing rule 4 is not satisfied; clauses failing: "
                         + ", ".join(failed) + extra)
        # The L channels are still reported -- the rung's decision rests on them and
        # A15.7 registers them on a run that may legitimately not reach endTime.
        rep["rung_reading"] = _rung_reading(rep["L_channels"])
        return rep

    band = gate_forces(row or {}, ref)
    rep["band_gate"] = band
    rep["rung_reading"] = _rung_reading(rep["L_channels"])
    rep["verdict"] = band["verdict"]
    if band["verdict"] == "BLOCKED":
        rep["reason"] = band["reason"]
    return rep


def _rung_reading(L):
    """A15.7's consequence clause, stated as it is registered: if L1 AND L2 both fail,
    the NUMERICS rung is CLOSED at 2a and 2b and the act parks.  This function only
    READS the registered clause; it does not decide anything the addendum did not."""
    v1, v2 = L.get("L1", {}).get("verdict"), L.get("L2", {}).get("verdict")
    if v1 == "GATE FAIL" and v2 == "GATE FAIL":
        return ("A15.7 fires: L1 and L2 both GATE FAIL -> the NUMERICS rung is CLOSED "
                "for this act at 2a and 2b; no third numerics variant may be registered; "
                "the act parks and rung 1 (MESH) is handed to a mesh registration.")
    if "NOT A RESULT" in (v1, v2):
        return ("A15.7 does not fire: at least one of L1/L2 is NOT A RESULT, and a "
                "clause whose reading point was never reached cannot be cleared or failed.")
    return "A15.7 does not fire on L1/L2."


# ================================================================ 8. PLANTS =====
# Standing rule 3.  Every plant below is written to disk, read back THROUGH THE
# PRODUCTION READER, and the suite exits 2 if the reader cannot see it.

COEFF_NAMES = ["Time", "Cd", "Cd(f)", "Cd(r)", "Cl", "Cl(f)", "Cl(r)", "CmPitch",
               "CmRoll", "CmYaw", "Cs", "Cs(f)", "Cs(r)"]


def _write_coeff_file(path, rows, names=None):
    names = names or COEFF_NAMES
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("# Force and moment coefficients\n")
        f.write("# magUInf           : %.12e\n" % U_INF)
        f.write("#\n")
        f.write("# " + "\t".join("%-20s" % n for n in names) + "\n")
        for r in rows:
            f.write("\t".join("%.12e" % r[n] if n != "Time" else "%-20g" % r[n]
                              for n in names) + "\n")


def _coeff_row(t, cd, cl=0.5, cm=-0.06):
    """A row whose split columns SUM to its totals, so the identity control passes for
    the right reason.  The split is deliberately large and opposite-signed, exactly as
    the real file's is -- that is what made `Cd(f)` readable as `Cd`."""
    return {"Time": t,
            "Cd": cd, "Cd(f)": cd + 0.97, "Cd(r)": -0.97,
            "Cl": cl, "Cl(f)": cl + 0.31, "Cl(r)": -0.31,
            "CmPitch": cm, "CmRoll": 0.9, "CmYaw": 1.1,
            "Cs": -5.6, "Cs(f)": -1.6, "Cs(r)": -4.0}


def _write_log(path, times, end=False, app="rhoPimpleFoam", h_resid=None,
               clamp=None, courant=None, exec0=0.0, per_step=10.0):
    parts = ["Build  : v2606\nnProcs : 32\nExec   : %s -parallel\n" % app]
    for i, t in enumerate(times):
        parts.append("Time = %g\n\n" % t)
        if courant is not None:
            parts.append("Courant Number mean: %.6g max: %.6g\n" % (courant / 3.0, courant))
        parts.append("DILUPBiCGStab:  Solving for Ux, Initial residual = 0.1, "
                     "Final residual = 1e-5, No Iterations 1\n")
        hv = h_resid(t) if callable(h_resid) else (1.0 if h_resid is None else h_resid)
        parts.append("DILUPBiCGStab:  Solving for hFinal, Initial residual = %.10g, "
                     "Final residual = 1e-4, No Iterations 1\n" % hv)
        if clamp is not None:
            lo, hi = clamp(t) if callable(clamp) else clamp
            parts.append("limitTemperature=limitT, Type=Lower, LimitedCells=1, "
                         "CellsPercent=%.4g, Tmin=100, UnlimitedTmin=100\n" % lo)
            parts.append("limitTemperature=limitT, Type=Upper, LimitedCells=1, "
                         "CellsPercent=%.4g, Tmax=1000, UnlimitedTmax=1000\n" % hi)
        parts.append("pressureControl: p max 5000\npressureControl: p min 1000\n")
        parts.append("ExecutionTime = %.2f s  ClockTime = %d s\n\n"
                     % (exec0 + per_step * (i + 1), int(exec0 + per_step * (i + 1))))
    if end:
        parts.append("End\n")
    open(path, "w").write("".join(parts))


def _write_binary_field(path, kind, values, t="10"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    n = len(values) // (3 if kind == "vector" else 1)
    head = ("FoamFile\n{\n    version 2.0;\n    format binary;\n"
            "    arch \"LSB;label=32;scalar=64\";\n"
            "    class vol%sField;\n    location \"%s\";\n    object f;\n}\n\n"
            "dimensions      [0 1 -1 0 0 0 0];\n\n"
            "internalField   nonuniform List<%s> \n%d\n(" %
            ("Vector" if kind == "vector" else "Scalar", t, kind, n))
    with open(path, "wb") as f:
        f.write(head.encode())
        f.write(struct.pack("<%dd" % len(values), *values))
        f.write(b")\n;\n\nboundaryField\n{\n}\n")


def _fake_case(root, end_time=20, app="rhoPimpleFoam", closure="SpalartAllmaras",
               rc=0, nproc=2, complete=True, age_ok=True, drop_field=None,
               drop_step=None, cd=None, cl=0.5, cm=-0.06, **logkw):
    """A complete synthetic decomposed case that PASSES rule 4, unless asked to break
    exactly one clause.  The point of the `drop_*`/`age_ok` switches is that the suite
    can prove each clause FAILS when it should -- a guard that cannot fail is inert."""
    os.makedirs(os.path.join(root, "system"), exist_ok=True)
    os.makedirs(os.path.join(root, "constant"), exist_ok=True)
    open(os.path.join(root, "system", "controlDict"), "w").write(
        "application     %s;\nendTime         %g;\ndeltaT          1;\n"
        "writeInterval   1;\npurgeWrite      2;\n" % (app, end_time))
    open(os.path.join(root, "constant", "turbulenceProperties"), "w").write(
        "simulationType RAS;\nRAS\n{\n    RASModel %s;\n    turbulence on;\n}\n" % closure)
    open(os.path.join(root, "RC.txt"), "w").write("RC=%d\n" % rc)
    _model, fields = required_fields(root)
    if fields is None:                   # an unregistered closure: stage the base set
        fields = ("T", "U", "p", "rho", "alphat", "nut", "phi")
    t0 = time.time() - 10000.0
    for i in range(nproc):
        z = os.path.join(root, "processor%d" % i, "0")
        os.makedirs(z, exist_ok=True)
        for f in fields:
            open(os.path.join(z, f), "w").write("// 0\n")
            os.utime(os.path.join(z, f), (t0, t0))
        td = os.path.join(root, "processor%d" % i, "%g" % end_time)
        os.makedirs(td, exist_ok=True)
        for f in fields:
            if drop_field and f == drop_field and i == 0:
                continue
            fp = os.path.join(td, f)
            if f == "p":
                _write_binary_field(fp, "scalar", [4000.0, 4100.0, 3900.0], "%g" % end_time)
            elif f == "U":
                _write_binary_field(fp, "vector", [300.0, 0.0, 1.0, 299.0, 2.0, 0.0],
                                    "%g" % end_time)
            else:
                open(fp, "w").write("// t\n")
            m = (t0 + 500.0) if age_ok else (t0 - 500.0)
            os.utime(fp, (m, m))
    times = [t for t in range(1, int(end_time) + 1) if t != drop_step]
    if not complete:
        times = times[:max(1, len(times) // 2)]
    _write_log(os.path.join(root, "log." + app), times, end=complete, app=app, **logkw)
    if cd is not None:
        _write_coeff_file(os.path.join(root, "postProcessing", "forceCoeffs", "0",
                                       "coefficient.dat"),
                          [_coeff_row(t, cd if t == end_time else 0.05, cl, cm)
                           for t in times])
    return root


def selftest():
    fails = []

    def check(name, cond, detail=""):
        if not cond:
            fails.append(f"{name}: {detail}")
        return cond

    with tempfile.TemporaryDirectory() as td:
        # ---------------------------------------------------------------- P-A ---
        # THE COLUMN-NAME PLANT.  A decoy sits in the Cd(f) column at endTime and the
        # planted value in Cd.  An index reader returns the decoy.  Then the header is
        # SHUFFLED and the same answer is required: only a by-name reader survives.
        c = os.path.join(td, "PA")
        os.makedirs(c)
        rows = [_coeff_row(1, PLANT_CD_DECOY), _coeff_row(10, PLANT_CD)]
        rows[1]["Cd(f)"] = PLANT_CD_DECOY + 0.97     # the decoy, in the trap's column
        rows[1]["Cd(r)"] = rows[1]["Cd"] - rows[1]["Cd(f)"]
        _write_coeff_file(os.path.join(c, "postProcessing", "forceCoeffs", "0",
                                       "coefficient.dat"), rows)
        got, meta = read_coefficients(c)
        check("P-A reads Cd by name at endTime",
              abs(got[10.0]["Cd"] - PLANT_CD) < 1e-15,
              f"got {got.get(10.0, {}).get('Cd')!r}, planted {PLANT_CD}")
        check("P-A does NOT return the Cd(f) decoy",
              abs(got[10.0]["Cd"] - PLANT_CD_DECOY) > 1e-12,
              "the reader returned the column awk '{print $3}' returns")
        shuf = ["Time", "CmYaw", "Cl", "Cs", "Cd(r)", "CmPitch", "Cd", "Cl(f)",
                "Cs(f)", "Cd(f)", "CmRoll", "Cl(r)", "Cs(r)"]
        c2 = os.path.join(td, "PA2")
        os.makedirs(c2)
        _write_coeff_file(os.path.join(c2, "postProcessing", "forceCoeffs", "0",
                                       "coefficient.dat"), rows, names=shuf)
        got2, _ = read_coefficients(c2)
        check("P-A survives a shuffled header",
              abs(got2[10.0]["Cd"] - PLANT_CD) < 1e-15,
              f"shuffled-header read gave {got2.get(10.0, {}).get('Cd')!r}")
        if abs(got[10.0]["Cd"] - PLANT_CD) > 1e-15 or abs(got2[10.0]["Cd"] - PLANT_CD) > 1e-15:
            sys.stderr.write("REFUSED: the planted Cd was not read back by name.\n")
            return 2

        # ---------------------------------------------------------------- P-B ---
        # THE ARITHMETIC CONTROL, IN BOTH DIRECTIONS.  A clean row must PASS the
        # identity; a row whose split is broken by one part in 1e3 must FAIL it.  This
        # is a check on the NUMBERS, not on whether a gate fired.
        clean = _coeff_row(10, 0.0261)
        ident = split_identity_control(clean)
        check("P-B clean row passes the identity",
              all(v["ok"] for v in ident.values()),
              json.dumps(ident))
        broken = dict(clean)
        broken["Cd(f)"] = broken["Cd(f)"] * 1.001
        ident_b = split_identity_control(broken)
        check("P-B broken split is CAUGHT", not ident_b["Cd"]["ok"],
              f"rel_err {ident_b['Cd']['rel_err']:.3e} was accepted; an identity "
              "control that cannot fail is inert")

        # ---------------------------------------------------------------- P-C ---
        # THE COMPLETION CHECK MUST BE ABLE TO FAIL, CLAUSE BY CLAUSE.  Five fixtures,
        # each breaking exactly one clause, then the clean one.
        base = dict(end_time=8, nproc=2)
        cases = {
            "rc":      dict(base, rc=1),
            "age":     dict(base, age_ok=False),
            "field":   dict(base, drop_field="nuTilda"),
            "step":    dict(base, drop_step=5),
            "endline": dict(base, complete=False),
        }
        clause_of = {"rc": "clause_rc_zero", "age": "clause_age_guard",
                     "field": "clause_fields", "step": "clause_exec_count",
                     "endline": "clause_end_line"}
        for nm, kw in cases.items():
            cc = _fake_case(os.path.join(td, "PC_" + nm), **kw)
            comp = check_completion(cc)
            check(f"P-C {nm} breaks its clause", comp[clause_of[nm]] is False,
                  f"{clause_of[nm]} passed on a case built to break it")
            check(f"P-C {nm} is NOT complete", comp["ok"] is False, "")
        cc = _fake_case(os.path.join(td, "PC_clean"), **base)
        comp = check_completion(cc)
        check("P-C clean case IS complete", comp["ok"] is True,
              "the completion rule is now so strict it cannot pass a complete run: "
              + json.dumps({k: v for k, v in comp.items() if k.startswith("clause_")}))
        check("P-C names the planted missing step",
              check_completion(os.path.join(td, "PC_step"))["missing_steps"] == [5.0],
              str(check_completion(os.path.join(td, "PC_step"))["missing_steps"]))
        # the age guard, corrected in place, must flip to PASS -- the SUBOFF P-C shape
        ca = os.path.join(td, "PC_age")
        anchor_m = os.path.getmtime(check_completion(ca)["age_anchor"])
        for pd in sorted(d for d in os.listdir(ca) if d.startswith("processor")):
            tdp = os.path.join(ca, pd, "8")
            for f in os.listdir(tdp):
                os.utime(os.path.join(tdp, f), (anchor_m + 100, anchor_m + 100))
        check("P-C age guard flips to PASS when the mtime is corrected",
              check_completion(ca)["clause_age_guard"] is True,
              "a guard that cannot pass is as useless as one that cannot fail")

        # ---------------------------------------------------------------- P-D ---
        # THE GATE, AND THE NUMBER.  A whole synthetic run is driven end to end with an
        # EXACTLY KNOWN Cd: once outside the band (must be GATE FAIL), once inside
        # (must be PASS).  AND the returned number is checked against the planted one,
        # which is the clause nine controls in this lab omitted.
        ref = {"CL": 0.488653, "CD": 0.0240692, "CM": -0.0634127}   # a real NTF WB row
        for tag, cd_val, want in (("inside", ref["CD"] + 0.5 * BAND_CD, "PASS"),
                                  ("outside", ref["CD"] + 3.0 * BAND_CD, "GATE FAIL")):
            cc = _fake_case(os.path.join(td, "PD_" + tag), end_time=8, nproc=2,
                            cd=cd_val, cl=ref["CL"], cm=ref["CM"],
                            clamp=(0.2, 0.3), courant=0.15,
                            h_resid=lambda t: 1.0 if t < 3 else 0.5)
            rep = grade(cc, ref=ref, force_plant_control="PASS")
            check(f"P-D {tag} completion ok", rep["completion"]["ok"] is True,
                  json.dumps({k: v for k, v in rep["completion"].items()
                              if k.startswith("clause_")}))
            check(f"P-D {tag} verdict is {want}", rep.get("verdict") == want,
                  f"got {rep.get('verdict')!r} reason={rep.get('reason')!r}")
            got_cd = rep.get("band_gate", {}).get("CD", {}).get("cfd")
            check(f"P-D {tag} THE NUMBER is the planted one",
                  got_cd is not None and abs(got_cd - cd_val) < 1e-12,
                  f"gate fired on {got_cd!r}, planted {cd_val!r} -- a gate that fires "
                  "on a number nobody checked is not evidence")
            dev = rep.get("band_gate", {}).get("CD", {}).get("deviation")
            check(f"P-D {tag} the deviation is arithmetic",
                  dev is not None and abs(dev - (cd_val - ref["CD"])) < 1e-12,
                  f"deviation {dev!r}")

        # ---------------------------------------------------------------- P-E ---
        # LIVENESS, THE 37-MINUTE LESSON.  Contents identical; only mtime and the
        # process table differ.  A dead log must be refused by --monitor, and a live
        # case must be refused by --grade.
        cdead = _fake_case(os.path.join(td, "PE_dead"), end_time=8, nproc=1,
                           cd=0.024, clamp=(0.2, 0.3), courant=0.15)
        old = time.time() - 37 * 60
        for f in ("log.rhoPimpleFoam", "RC.txt", "LAUNCH.log"):
            p = os.path.join(cdead, f)
            if os.path.exists(p):
                os.utime(p, (old, old))
        for root_, _, fs in os.walk(os.path.join(cdead, "postProcessing")):
            for f in fs:
                os.utime(os.path.join(root_, f), (old, old))
        lv = liveness(cdead, "rhoPimpleFoam")
        check("P-E dead log is seen as dead", lv["live"] is False and lv["stalled"] is True,
              json.dumps(lv, default=str))
        check("P-E dead log age is ~37 min",
              2100 < lv["newest_artifact_age_s"] < 2300,
              str(lv["newest_artifact_age_s"]))
        mon = grade(cdead, mode="monitor")
        check("P-E --monitor REFUSES a dead log", mon["verdict"] == "BLOCKED",
              f"got {mon['verdict']!r} -- this is the exact shape of the rate table "
              "published from logs frozen 37 minutes")
        # and the control on the control: a LIVE case must not be graded
        clive = _fake_case(os.path.join(td, "PE_live"), end_time=8, nproc=1, cd=0.024)
        os.remove(os.path.join(clive, "RC.txt"))
        now = time.time()
        os.utime(os.path.join(clive, "log.rhoPimpleFoam"), (now, now))
        lv2 = liveness(clive, "rhoPimpleFoam")
        check("P-E fresh log with no rc is seen as LIVE", lv2["live"] is True,
              json.dumps(lv2, default=str))
        g2 = grade(clive, ref=ref)
        check("P-E --grade REFUSES a live run", g2["verdict"] == "PENDING",
              f"got {g2['verdict']!r}")
        # and the control on THAT: the same case, quiesced with an rc, IS gradeable
        os.utime(os.path.join(clive, "log.rhoPimpleFoam"), (old, old))
        open(os.path.join(clive, "RC.txt"), "w").write("RC=0\n")
        os.utime(os.path.join(clive, "RC.txt"), (old, old))
        g3 = grade(clive, ref=ref, force_plant_control="PASS")
        check("P-E a quiesced run IS gradeable", g3["verdict"] != "PENDING",
              "the liveness guard is now so strict nothing can ever be graded")

        # ---------------------------------------------------------------- P-F ---
        # THE FIELD READER.  A known max is planted into a binary field with a DECOY
        # first value, and the reader must return the planted one, not the first one.
        fp = os.path.join(td, "PF", "processor0", "10", "p")
        vals = [PLANT_P_FIELD * 0.1, 4000.0, PLANT_P_FIELD, -123.0]
        _write_binary_field(fp, "scalar", vals, "10")
        kind, back = read_internal_field(fp)
        check("P-F binary scalar round-trips", kind == "scalar" and len(back) == 4,
              f"{kind} {len(back)}")
        check("P-F reads the planted max, not the first value",
              abs(max(back) - PLANT_P_FIELD) < 1e-9,
              f"max {max(back)!r}, planted {PLANT_P_FIELD}")
        # THE TWO DECODERS MUST AGREE.  numpy is an optimisation, not a second opinion:
        # if it ever disagreed with struct.unpack the field readings would be silently
        # decided by whether numpy happened to be installed.
        with open(fp, "rb") as _f:
            _blob = _f.read()
        _m = _IF_RE.search(_blob)
        _mn = re.match(rb"\s*(\d+)\s*\(", _blob[_m.end():])
        _st = _m.end() + _mn.end()
        _ref = list(struct.unpack("<%dd" % int(_mn.group(1)),
                                  _blob[_st:_st + int(_mn.group(1)) * 8]))
        check("P-F numpy decode == struct decode",
              len(_ref) == len(back) and all(abs(x - y) < 1e-15 for x, y in zip(_ref, back)),
              f"struct {_ref} vs reader {list(back)}")
        uf = os.path.join(td, "PF", "processor0", "10", "U")
        _write_binary_field(uf, "vector",
                            [1.0, 2.0, 2.0, PLANT_U_FIELD, 0.0, 0.0, 3.0, 0.0, 4.0], "10")
        ue = field_extrema(os.path.join(td, "PF"), "10", "U")
        check("P-F vector magnitude sees the planted |U|",
              abs(ue["max_magnitude"] - PLANT_U_FIELD) < 1e-9,
              f"got {ue['max_magnitude']!r}")
        pe = field_extrema(os.path.join(td, "PF"), "10", "p")
        check("P-F field_extrema max", abs(pe["max"] - PLANT_P_FIELD) < 1e-9, str(pe))
        # and L5 must FAIL on a planted over-pressure and PASS on a clean one
        cbad = _fake_case(os.path.join(td, "PF_bad"), end_time=8, nproc=1, cd=0.024)
        _write_binary_field(os.path.join(cbad, "processor0", "8", "p"), "scalar",
                            [4000.0, L5_P_ABS_MAX * 1.5], "8")
        anchor = check_completion(cbad)["age_anchor"]
        am = os.path.getmtime(anchor)
        os.utime(os.path.join(cbad, "processor0", "8", "p"), (am + 100, am + 100))
        l5bad = evaluate_L5(cbad, check_completion(cbad))
        check("P-F L5 FAILS on a planted over-pressure", l5bad["verdict"] == "GATE FAIL",
              json.dumps(l5bad))
        l5ok = evaluate_L5(os.path.join(td, "PC_clean"), check_completion(
            os.path.join(td, "PC_clean")))
        check("P-F L5 PASSES on the clean field", l5ok["verdict"] == "PASS",
              json.dumps(l5ok))

        # ---------------------------------------------------------------- P-K ---
        # THE WRITE-SCHEDULE PRE-FLIGHT, ON THE REAL SHAPE AND ON A GOOD ONE.
        ck1 = os.path.join(td, "PK1")
        os.makedirs(os.path.join(ck1, "system"), exist_ok=True)
        open(os.path.join(ck1, "system", "controlDict"), "w").write(
            "application rhoPimpleFoam;\nendTime 20;\ndeltaT 1;\n"
            "writeInterval 6;\npurgeWrite 2;\n")
        w1 = write_schedule(ck1)
        check("P-K catches the probe's real shape (endTime 20, writeInterval 6)",
              w1["endTime_is_a_write"] is False
              and w1["endTime_survives_purge"] is False
              and w1["kept_after_purge"][-2:] == [12.0, 18.0],
              json.dumps(w1))
        open(os.path.join(ck1, "system", "controlDict"), "w").write(
            "application rhoPimpleFoam;\nendTime 6000;\ndeltaT 1;\n"
            "writeInterval 6;\npurgeWrite 2;\n")
        w2 = write_schedule(ck1)
        check("P-K stays QUIET on the production shape (endTime 6000, writeInterval 6)",
              w2["endTime_is_a_write"] is True and w2["endTime_survives_purge"] is True,
              json.dumps(w2))
        # and purgeWrite alone must be able to lose endTime even when it IS a write
        open(os.path.join(ck1, "system", "controlDict"), "w").write(
            "application rhoPimpleFoam;\nendTime 18;\ndeltaT 1;\n"
            "writeInterval 6;\npurgeWrite 2;\n")
        w3 = write_schedule(ck1)
        check("P-K accepts endTime 18 (a write, and kept)",
              w3["endTime_survives_purge"] is True, json.dumps(w3))

        # ---------------------------------------------------------------- P-L ---
        # THE PRE-CLAMP READER.  The excursion it reports never reaches a written field,
        # so nothing else in this comparator can corroborate it -- which is exactly why
        # it needs a plant of its own.
        cl1 = os.path.join(td, "PL")
        os.makedirs(cl1, exist_ok=True)
        open(os.path.join(cl1, "log.rhoPimpleFoam"), "w").write(
            "pressureControl\n    pMax 8014.789298\n    pMin 400.7394649\n\n"
            "Time = 1\n\npressureControl: p max 20176.5848879\n"
            "ExecutionTime = 1 s  ClockTime = 1 s\n\n"
            "Time = 2\n\npressureControl: p max 9000.5\n"
            "pressureControl: p min 12.25\n"
            "ExecutionTime = 2 s  ClockTime = 2 s\n\nEnd\n")
        pc = preclamp_pressure(cl1, "rhoPimpleFoam")
        check("P-L reads the solver's own printed clamp",
              pc["solver_printed_clamp"] == {"pMax": 8014.789298, "pMin": 400.7394649},
              json.dumps(pc["solver_printed_clamp"]))
        check("P-L sees the planted pre-clamp excursion, and takes the MAX not the first",
              abs(pc["preclamp_p_max_Pa"] - 20176.5848879) < 1e-9,
              f"got {pc['preclamp_p_max_Pa']!r}")
        check("P-L calls it over the L5 ceiling", pc["exceeds_L5_ceiling"] is True,
              json.dumps(pc))
        check("P-L counts every step that went over", pc["n_steps_over_clamp"] == 2,
              str(pc["n_steps_over_clamp"]))
        check("P-L reads the min channel too",
              abs(pc["preclamp_p_min_Pa"] - 12.25) < 1e-9, str(pc["preclamp_p_min_Pa"]))
        # the control on the control: a run that never exceeded the clamp must read clean
        open(os.path.join(cl1, "log.rhoPimpleFoam"), "w").write(
            "pressureControl\n    pMax 8014.789298\n    pMin 400.7394649\n\n"
            "Time = 1\n\nExecutionTime = 1 s  ClockTime = 1 s\n\nEnd\n")
        pc2 = preclamp_pressure(cl1, "rhoPimpleFoam")
        check("P-L stays QUIET when the clamp never fired",
              pc2["n_steps_over_clamp"] == 0 and pc2["preclamp_p_max_Pa"] is None
              and pc2["exceeds_L5_ceiling"] is False, json.dumps(pc2))

        # ---------------------------------------------------------------- P-N ---
        # A15.6(c)'s ADVERSARIAL CLAUSE.  The force channel must REFUSE on a diverged
        # field even when the number it would serve looks perfectly ordinary.  Driven on
        # SST's real SHAPE -- an ordinary Cd sitting on a field at 1e+129 -- and on a
        # clean case, because a gate that refuses everything is not a gate.
        cn_bad = _fake_case(os.path.join(td, "PN_bad"), end_time=8, nproc=1, cd=0.024,
                            clamp=(0.2, 0.3), courant=0.15)
        _write_binary_field(os.path.join(cn_bad, "processor0", "8", "U"), "vector",
                            [1.0, 0.0, 0.0, 3.86761822375e+129, 0.0, 0.0], "8")
        comp_bad = check_completion(cn_bad)
        am3 = os.path.getmtime(comp_bad["age_anchor"])
        for f in os.listdir(os.path.join(cn_bad, "processor0", "8")):
            os.utime(os.path.join(cn_bad, "processor0", "8", f), (am3 + 100, am3 + 100))
        comp_bad = check_completion(cn_bad)
        comp_bad["force_plant_control"] = "PASS"          # the plant PASSES; the field does not
        comp_bad["L5"] = evaluate_L5(cn_bad, comp_bad)
        fr_bad = force_is_readable(cn_bad, comp_bad)
        check("P-N the field gate SEES the diverged velocity",
              comp_bad["L5"]["verdict"] == "GATE FAIL",
              json.dumps({k: comp_bad["L5"].get(k) for k in ("verdict", "U_mag_max_m_s")}))
        check("P-N a force is REFUSED on a diverged field EVEN WITH THE PLANT PASSED",
              fr_bad["readable"] is False
              and any("F-1" in x for x in fr_bad["refusals"]),
              json.dumps(fr_bad))
        L_bad = evaluate_L(cn_bad, "rhoPimpleFoam",
                           read_log_channels(cn_bad, "rhoPimpleFoam"),
                           read_coefficients(cn_bad)[0], comp_bad)
        check("P-N and L3 is therefore NOT A RESULT, not a plausible pass",
              L_bad["L3"]["verdict"] == "NOT A RESULT", json.dumps(L_bad["L3"])[:200])
        # THE CONTROL ON THE CONTROL.  A clean field, plant passed -> READABLE.
        cn_ok = _fake_case(os.path.join(td, "PN_ok"), end_time=8, nproc=1, cd=0.024,
                           clamp=(0.2, 0.3), courant=0.15)
        comp_ok = check_completion(cn_ok)
        comp_ok["force_plant_control"] = "PASS"
        comp_ok["L5"] = evaluate_L5(cn_ok, comp_ok)
        fr_ok = force_is_readable(cn_ok, comp_ok)
        check("P-N a clean field with the plant passed IS readable",
              fr_ok["readable"] is True,
              "the refusal gate refuses everything, which is not a gate: "
              + json.dumps(fr_ok))
        # and each clause must be independently sufficient
        comp_np2 = dict(comp_ok)
        comp_np2["force_plant_control"] = "NOT RUN"
        check("P-N F-3 alone refuses",
              force_is_readable(cn_ok, comp_np2)["readable"] is False, "")
        # THE SPLIT IDENTITY IS NECESSARY AND NOT SUFFICIENT -- SST's REAL NUMBERS.
        sst_row = {"Cd": -4.41412776577e+88, "Cd(f)": 1.874164177613e+89,
                   "Cd(r)": -2.31557695419e+89}
        check("P-N the split identity PASSES on SST's destroyed artifact",
              split_identity_control(sst_row)["Cd"]["ok"] is True,
              "the fixture is wrong: SST's artifact is internally consistent and the "
              "point of this control is that arithmetic consistency does not detect "
              "divergence")
        # a COMPONENT may never be served as a force
        for nm in ("Pressure", "Viscous", "pressure_x"):
            try:
                refuse_component_as_force(nm)
                fails.append(f"P-N {nm!r} was served as a force")
            except SystemExit as e:
                check(f"P-N refuses to serve {nm!r} as a force", e.code == 2, str(e.code))

        # ---------------------------------------------------------------- P-M ---
        # THE CONTAINMENT RULING, ENFORCED.  The SAME case is graded twice: once with a
        # planted pre-clamp excursion far over the L5 ceiling in its log, once without.
        # The L5 verdict and EVERY numeric field must be identical; only the disclosure
        # may differ.  A disclosure channel that can move a verdict is a gate wearing a
        # different name, and this act's whole freeze argument would be worth nothing.
        cm1 = _fake_case(os.path.join(td, "PM"), end_time=8, nproc=1, cd=0.024)
        comp_m = check_completion(cm1)
        l5_clean = evaluate_L5(cm1, comp_m)
        logp = os.path.join(cm1, "log.rhoPimpleFoam")
        body = open(logp).read().replace(
            "Time = 1\n",
            "pressureControl\n    pMax 8014.789298\n    pMin 400.7394649\n\nTime = 1\n"
            "\npressureControl: p max 20176.5848879\n", 1)
        open(logp, "w").write(body)
        anchor_m2 = os.path.getmtime(comp_m["age_anchor"])
        for f in os.listdir(os.path.join(cm1, "processor0", "8")):
            os.utime(os.path.join(cm1, "processor0", "8", f),
                     (anchor_m2 + 100, anchor_m2 + 100))
        l5_dirty = evaluate_L5(cm1, check_completion(cm1))
        check("P-M the planted excursion IS disclosed",
              l5_dirty["p_clause_reachability"]["preclamp"]["exceeds_L5_ceiling"] is True
              and l5_clean["p_clause_reachability"]["preclamp"]["exceeds_L5_ceiling"] is False,
              "the fixture planted nothing the reader could see, so it proves nothing")
        check("P-M and it does NOT move the L5 verdict",
              l5_dirty["verdict"] == l5_clean["verdict"] == "PASS",
              f"clean {l5_clean['verdict']!r} vs planted {l5_dirty['verdict']!r} -- the "
              "disclosure channel moved a gate, in violation of the 2026-09-13 ruling")
        check("P-M nor any graded NUMBER",
              all(l5_dirty[k] == l5_clean[k] for k in
                  ("p_abs_max_Pa", "U_mag_max_m_s", "p_ceiling_Pa", "U_ceiling_m_s")),
              "a graded number changed when only the log's disclosure lines changed")
        check("P-M the channel labels itself a disclosure, not a gate",
              "NEVER A GATE" in l5_dirty["p_clause_reachability"]["preclamp"]["status"],
              "")

        # ---------------------------------------------------------------- P-J ---
        # THE REACHABILITY READER.  A clause that cannot fail is not a clause, so the
        # comparator must be able to SAY SO -- and must not say so when it is wrong.
        cj = os.path.join(td, "PJ")
        os.makedirs(os.path.join(cj, "system"), exist_ok=True)
        open(os.path.join(cj, "system", "fvSolution"), "w").write(
            "PIMPLE\n{\n    pMinFactor 0.1;\n    pMaxFactor 2.0;\n}\n")
        rj = p_clause_reachable(cj)
        check("P-J sees the registered clamp ceiling",
              abs(rj["clamp_ceiling_Pa"] - 2.0 * P_INF) < 1e-9
              and abs(rj["clamp_ceiling_Pa"] - 8014.789298) < 1e-6,
              json.dumps(rj))
        check("P-J calls the p clause UNFAILABLE at pMaxFactor 2.0",
              rj["p_clause_can_fire"] is False, json.dumps(rj))
        open(os.path.join(cj, "system", "fvSolution"), "w").write(
            "PIMPLE\n{\n    pMaxFactor 9.0;\n}\n")
        rj2 = p_clause_reachable(cj)
        check("P-J calls it REACHABLE at pMaxFactor 9.0 -- the reader is not stuck on one answer",
              rj2["p_clause_can_fire"] is True, json.dumps(rj2))

        # ---------------------------------------------------------------- P-G ---
        # THE L CHANNELS, EACH SHOWN ABLE TO FAIL AND TO PASS.
        good = _fake_case(os.path.join(td, "PG_good"), end_time=60, nproc=1, cd=0.024,
                          h_resid=lambda t: 1.0 if t < 10 else 0.4,
                          clamp=lambda t: (0.2, 0.3) if t > 30 else (20.0, 30.0),
                          courant=0.15)
        Lg = evaluate_L(good, "rhoPimpleFoam", read_log_channels(good, "rhoPimpleFoam"),
                        read_coefficients(good)[0], check_completion(good))
        check("P-G L1 PASS", Lg["L1"]["verdict"] == "PASS", json.dumps(Lg["L1"]))
        check("P-G L2 PASS", Lg["L2"]["verdict"] == "PASS", json.dumps(Lg["L2"]))
        check("P-G L4 PASS", Lg["L4"]["verdict"] == "PASS", json.dumps(Lg["L4"]))
        bad = _fake_case(os.path.join(td, "PG_bad"), end_time=60, nproc=1, cd=0.024,
                         h_resid=1.0, clamp=(45.31, 15.56), courant=3.0)
        Lb = evaluate_L(bad, "rhoPimpleFoam", read_log_channels(bad, "rhoPimpleFoam"),
                        read_coefficients(bad)[0], check_completion(bad))
        check("P-G L1 GATE FAIL on residual pinned at 1",
              Lb["L1"]["verdict"] == "GATE FAIL", json.dumps(Lb["L1"]))
        check("P-G L2 GATE FAIL and SUMS BOTH BRANCHES",
              Lb["L2"]["verdict"] == "GATE FAIL"
              and abs(Lb["L2"]["total_pct_BOTH_BRANCHES"] - 60.87) < 1e-6,
              f"total {Lb['L2'].get('total_pct_BOTH_BRANCHES')!r} -- A15.2's honesty "
              "flag: the Upper branch alone is 45.31 and is NOT the total")
        check("P-G L4 GATE FAIL above maxCo", Lb["L4"]["verdict"] == "GATE FAIL",
              json.dumps(Lb["L4"]))
        check("P-G A15.7 consequence fires on L1+L2 both failing",
              "CLOSED" in _rung_reading(Lb), _rung_reading(Lb))
        # L3 must REFUSE while the A15.6(c) plant has not passed
        comp_np = check_completion(good)
        comp_np["force_plant_control"] = "NOT RUN"
        L_np = evaluate_L(good, "rhoPimpleFoam", read_log_channels(good, "rhoPimpleFoam"),
                          read_coefficients(good)[0], comp_np)
        check("P-G L3 is NOT A RESULT until the force plant passes",
              L_np["L3"]["verdict"] == "NOT A RESULT", json.dumps(L_np["L3"]))
        # a short run: the reading point was never reached -> NOT A RESULT, not a pass
        short = _fake_case(os.path.join(td, "PG_short"), end_time=22, nproc=1, cd=0.024,
                           h_resid=1.0, clamp=(45.31, 15.56), courant=0.1)
        Ls = evaluate_L(short, "rhoPimpleFoam", read_log_channels(short, "rhoPimpleFoam"),
                        read_coefficients(short)[0], check_completion(short))
        check("P-G L2 unreached reading point is NOT A RESULT",
              Ls["L2"]["verdict"] == "NOT A RESULT", json.dumps(Ls["L2"]))
        check("P-G and it still reports the last measured total",
              abs(Ls["L2"]["last_total_pct"] - 60.87) < 1e-6,
              str(Ls["L2"].get("last_total_pct")))

        # ---------------------------------------------------------------- P-H ---
        # THE CLOSURE-DERIVED FIELD LIST.  A14.3's lesson, one field over.
        ck = _fake_case(os.path.join(td, "PH"), end_time=4, nproc=1, closure="kOmegaSST")
        mk, fk = required_fields(ck)
        check("P-H SST closure asks for k and omega, not nuTilda",
              mk == "kOmegaSST" and "k" in fk and "omega" in fk and "nuTilda" not in fk,
              f"{mk} {fk}")
        cu = _fake_case(os.path.join(td, "PH2"), end_time=4, nproc=1, closure="LaunderSharmaKE")
        mu, fu = required_fields(cu)
        check("P-H an unregistered closure REFUSES rather than guessing",
              fu is None and check_completion(cu)["clause_fields"] is False, f"{mu} {fu}")

        # ---------------------------------------------------------------- P-I ---
        # Q_INF, THE CONSTANT THE Cp EXTRACTION DEPENDS ON, checked against a literal
        # computed OUTSIDE this file from §4's own printed numbers.
        q_literal = 0.5 * 0.04503298815 * 300.0189024 * 300.0189024
        check("P-I q_inf matches an externally computed literal",
              abs(Q_INF - q_literal) < 1e-9 and abs(Q_INF - 2027.0355) < 1.0,
              f"Q_INF={Q_INF!r} literal={q_literal!r}")

    if fails:
        sys.stderr.write("SELFTEST RED:\n" + "\n".join("  " + f for f in fails) + "\n")
        return 1
    sys.stdout.write(
        "SELFTEST GREEN: 13 plant families. "
        "P-A column-name plant (Cd(f) decoy, and a shuffled header). "
        "P-B split identity accepted clean and caught at 1e-3. "
        "P-C five rule-4 clauses each shown able to FAIL, the clean case shown able to "
        "PASS, and the age guard flipped back by correcting one mtime. "
        "P-D the gate driven end to end inside and outside the band WITH THE RETURNED "
        "NUMBER CHECKED against the planted one. "
        "P-E a 37-minute-dead log refused by --monitor and a live case by --grade, the "
        "same case gradeable once quiesced. "
        "P-F the binary field reader with a decoy, numpy cross-decoded against struct. "
        "P-K the write-schedule pre-flight (fires on the probe shape, quiet on the "
        "production one). "
        "P-N A15.6(c)'s ADVERSARIAL CLAUSE: a force REFUSED on a diverged field even "
        "with the plant passed, a clean field still readable, and the split identity shown "
        "to PASS on SST's destroyed artifact (necessary, not sufficient). "
        "P-M THE 2026-09-13 CONTAINMENT RULING ENFORCED: a planted pre-clamp excursion "
        "is disclosed and moves no L5 verdict and no L5 number. "
        "P-L the pre-clamp reader seeing a planted excursion and quiet without one. "
        "P-J the L5 p-clause reachability reader in both directions. "
        "P-G L1/L2/L4 each PASS and FAIL, plus the unreached-reading-point case. "
        "P-H closure-derived fields. P-I q_inf against an external literal.\n")
    return 0


def mutation_control():
    """Neuter one load-bearing check in a COPY and require the suite to go RED.
    A control that cannot fail is not a control."""
    src = open(__file__).read()
    muts = {
        "by-name column reading":
            ("row[nm] = float(val)", "row[names[1]] = float(val)"),
        "the age guard":
            ('r["clause_age_guard"] = (worst is not None and worst > 0.0)',
             'r["clause_age_guard"] = True'),
        "the split identity control":
            ('"ok": abs(s - row[tot]) / scale <= SPLIT_TOL_REL',
             '"ok": True'),
        "the liveness guard":
            ('live = bool(procs) or (age is not None and age < LIVE_MTIME_S and not rc_present)',
             'live = False'),
        "the band gate":
            ('v = "PASS" if abs(dev) <= band else "GATE FAIL"', 'v = "PASS"'),
        # THE CONTAINMENT RULING OF 2026-09-13.  Promoting the disclosure channel to a
        # gate must go RED.  This is the mutation that matters most: it is the edit a
        # future lane would make in good faith, believing it an improvement.
        "the preclamp containment (promoting a disclosure channel to a gate)":
            ('    verdict, pmax, umax = _l5_verdict_from_field(pe, ue)',
             '    verdict, pmax, umax = _l5_verdict_from_field(pe, ue)\n'
             '    if reach["preclamp"]["exceeds_L5_ceiling"]:\n'
             '        verdict = "GATE FAIL"'),
    }
    rc_all = 0
    for name, (old, new) in muts.items():
        if old not in src:
            sys.stderr.write(f"MUTATION CONTROL BROKEN: site {name!r} not found; the "
                             "control cannot fail and is therefore not a control.\n")
            return 2
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "grade_crm_wb_lts.py")
            open(p, "w").write(src.replace(old, new, 1))
            env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
            r = subprocess.run([sys.executable, p, "--selftest"],
                               capture_output=True, text=True, env=env)
            if r.returncode == 0:
                sys.stderr.write(f"MUTATION CONTROL RED->GREEN on {name!r}: the neutered "
                                 "comparator PASSED its own suite.\n")
                rc_all = 1
            else:
                sys.stdout.write(f"MUTATION OK: neutering {name!r} -> suite rc={r.returncode}\n")
    return rc_all


def freeze_check(expected_sha):
    """Standing rule 2: the frozen file must BE the file that ran."""
    h = subprocess.run(["git", "hash-object", os.path.abspath(__file__)],
                       capture_output=True, text=True, cwd=REPO_ROOT)
    got = h.stdout.strip()
    print(json.dumps({"comparator": os.path.abspath(__file__),
                      "blob_sha_on_disk": got, "expected": expected_sha,
                      "state": "PINNED" if got == expected_sha else "DRIFTED"}, indent=2))
    return 0 if got == expected_sha else 2


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("case", nargs="?", help="run directory")
    ap.add_argument("--monitor", action="store_true",
                    help="report progress/rate on a LIVE run; refuses on a dead log")
    ap.add_argument("--ref-json", help="JSON file carrying the registered NTF reference "
                                       "row {CL,CD,CM}; without it the band gate is BLOCKED")
    ap.add_argument("--force-plant-control", default="NOT RUN",
                    choices=["PASS", "FAIL", "NOT RUN"],
                    help="state of the A15.6(c) planted-force control under this "
                         "application; L3 is NOT A RESULT unless it is PASS")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--mutation-control", action="store_true")
    ap.add_argument("--freeze-check", metavar="SHA")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if a.mutation_control:
        sys.exit(mutation_control())
    if a.freeze_check:
        sys.exit(freeze_check(a.freeze_check))
    if not a.case:
        ap.error("a case directory is required")
    ref = json.load(open(a.ref_json)) if a.ref_json else None
    rep = grade(a.case, mode="monitor" if a.monitor else "grade", ref=ref,
                force_plant_control=a.force_plant_control)
    print(json.dumps(rep, indent=2, default=str))
    v = rep.get("verdict")
    if v not in VERDICTS:
        refuse(f"verdict {v!r} is not in the fixed vocabulary {VERDICTS}")
    sys.exit(0 if v in ("PASS", "GATE REACHED") else 1)


if __name__ == "__main__":
    main()
