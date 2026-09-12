#!/usr/bin/env python3
"""analyse_k2h.py -- the comparator for K2h_L3.  ONE LEVEL.  NO TRIPLE.

Graded against `docs/campaigns/F14-cooling-ladder/K2h_PREREGISTRATION.md`, frozen
at db523d06a, plus AMENDMENT 1, ADDENDUM 1, its ERRATUM and ADDENDUM 2.

WHAT THIS INSTRUMENT WILL NOT DO, because section 3 of the registration forbids it
outright and the forbidding is the point:

    K2h_L1 and K2h_L2 DO NOT EXIST.  A triple whose L1/L2 are STEADY DP_module
    and whose L3 is TIME-AVERAGED DP_module is not a Roache triple of one
    discretisation.  NO observed order and NO GCI is computed here, not with a
    caveat and not with a footnote.  `roache_triple` is imported for its PLANT
    constant and its planted-zero control ONLY; `grade_ladder` is never called.

Order of evaluation, fixed by section 6 and section 10:

    1. FREEZE          -- the two pinned grading-path files, hashed from disk
                          bytes against the registration's own FREEZE block.
                          Any disagreement REFUSES (exit 2).  Nothing is graded.
    2. D-COMPLETE      -- CLAUDE.md rule 4 in the transient form section 6
                          registers, INCLUDING the age guard.  The step-count
                          clause is evaluated PER LOG SEGMENT, because the
                          ERRATUM records that `log.solve` is appended to on
                          resume and a count over the concatenation is arithmetic
                          about nothing.  Failure -> NOT A RESULT (exit 3).
    3. PLANTED ZERO    -- CLAUDE.md rule 3.  The `return` patch reads EXACTLY
                          0.0 at every step (its p_rgh BC is `fixedValue uniform
                          0`), so the graded difference rests on a zero and the
                          reader must be shown able to see a non-zero THERE.
                          Failure REFUSES (exit 2).
    4. D-STATIONARY    -- section 6.  Failure -> NOT A RESULT (exit 3).
    5. G-DPBAR         -- section 6.  Inside the band -> PASS, outside -> GATE FAIL.

THE CAP IS NOT A GATE HERE.  Whether a cap crossing forces NOT A RESULT is an
ESCALATED AND UNRULED conflict (her item 7 against her 2026-08-26 universal rule
against this entry's own _field_classes).  This instrument therefore computes and
prints the cap crossing as a SEPARATE, NAMED INFRASTRUCTURE FACT beside the
physics verdict, and lets it move the physics verdict in NEITHER direction.

Exit map (section 10): 0 OK, 1 GATE FAIL, 2 REFUSE, 3 NOT A RESULT.
NO VERDICT MAY BE READ FROM AN EXIT CODE.  The verdict is the word printed.
"""

import glob
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile

import numpy as np

REPO = "/home/ubuntu/Certonomous"
K2G = os.path.join(REPO, "verification/runs/F14-cooling-ladder/K2g_runs")
sys.path.insert(0, K2G)
sys.path.insert(0, os.path.join(REPO, "scripts"))

import foam_patch_reader as FR          # noqa: E402  FROZEN, section 11
import roache_triple as RT              # noqa: E402  FROZEN, section 11 (PLANT only)

REGISTRATION = os.path.join(
    REPO, "docs/campaigns/F14-cooling-ladder/K2h_PREREGISTRATION.md")
CASE = os.path.join(REPO,
                    "verification/runs/F14-cooling-ladder/K2h_runs/K2h_L3")

# ---- everything below is READ OFF THE REGISTRATION, never chosen here --------
ENDTIME = 112.0                     # section 5 E-ENDTIME
WIN_LO, WIN_HI = 42.0, 112.0        # section 5 S-WINDOW
WIN_MID = 0.5 * (WIN_LO + WIN_HI)   # 77.0 -- the two halves of D-STATIONARY
BAND = (27.9699, 28.0901)           # section 6 G-DPBAR, m2/s2
STATIONARY_TOL = 5.0e-3             # section 6 D-STATIONARY, m2/s2
POINT_CORE_MIN = 420.0              # section 8
CAP_CORE_MIN = 1260.0               # section 8
RANKS = 4                           # AD1.3 -- the decomposition the checkpoint is in
PATCH_HI, PATCH_LO = "tile", "return"
MEAN_FIELD = "p_rghMean"            # the fieldAverage output section 6 grades
FIELDS_REQUIRED = ("T", "U", "p_rgh", "alphat", "nut", "k", "omega", "phi")
MEANS_REQUIRED = ("p_rghMean", "TMean", "UMean")
PLANT = RT.PLANT                    # 1.234e-03

#: WHAT `DP_module` ACTUALLY IS, stated beside every value this instrument
#: emits because the NAME OVERSTATES IT.  `DP_module` is called a pressure DROP
#: and a reader will assume it is the difference between two MEASURED numbers.
#: It is not.  The `return` patch's p_rgh boundary condition is
#:
#:     return { type fixedValue; value uniform 0; }
#:
#: so areaAvg(p_rgh, return) is STRUCTURALLY ZERO by boundary condition, at
#: every step of both log segments, measured.  DP_module is therefore the
#: TILE-SIDE AREA AVERAGE AND NOTHING ELSE, and the subtraction is a formality.
#: THIS CHANGES NO GATE -- K2g established this same quantity on this same
#: construction at 27.189 and 27.730 -- so it needs no addendum.  But a number
#: whose name overstates what it is must carry the correction next to it rather
#: than in someone's message.
WHAT_DP_IS = (
    "DP_module = areaAvg(p_rghMean, tile) - areaAvg(p_rghMean, return). The "
    "`return` term is STRUCTURALLY ZERO: that patch's p_rgh boundary condition "
    "is `return { type fixedValue; value uniform 0; }`, so it reads exactly "
    "0.0 at every step of both log segments. DP_module is the TILE-SIDE AREA "
    "AVERAGE AND NOTHING ELSE; the subtraction is a formality and the name "
    "'pressure drop' overstates it. This changes NO gate -- K2g established the "
    "same quantity on the same construction at 27.189 and 27.730 m2/s2.")

EXIT_OK, EXIT_FAIL, EXIT_REFUSE, EXIT_NAR = 0, 1, 2, 3


class Refusal(Exception):
    pass


def refuse(msg):
    raise Refusal(msg)


# ---------------------------------------------------------------------------
# 1. THE FREEZE -- section 11.  Hashed from DISK BYTES, never from a manifest.
# ---------------------------------------------------------------------------
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 16), b""):
            h.update(blk)
    return h.hexdigest()


def verify_freeze():
    if not os.path.exists(REGISTRATION):
        refuse("the registration %s does not exist; there is no frozen gate and "
               "NOTHING may be graded" % REGISTRATION)
    m = re.search(r"```json FREEZE\n(.*?)\n```", open(REGISTRATION).read(), re.S)
    if m is None:
        refuse("the registration carries no ```json FREEZE``` block; the grading "
               "path is not pinned and nothing may be graded")
    want = json.loads(m.group(1))
    if not want:
        refuse("the registration's FREEZE block is empty; an empty table pins "
               "nothing and would let any file grade this run")
    bad, pinned = [], {}
    for rel, wsha in sorted(want.items()):
        p = os.path.join(REPO, rel)
        if not os.path.exists(p):
            bad.append((rel, "MISSING", wsha))
            continue
        got = sha256(p)
        pinned[rel] = got
        if got != wsha:
            bad.append((rel, got, wsha))
    if bad:
        refuse("FREEZE BROKEN -- the files that would run are NOT the files the "
               "registration pinned: " + "; ".join(
                   "%s disk=%s registered=%s" % b for b in bad))
    return {"state": "FROZEN AND VERIFIED", "n_pinned": len(pinned),
            "pinned": pinned}


# ---------------------------------------------------------------------------
# 2. THE LOG, SPLIT -- the ERRATUM's trap, handled rather than met as a surprise
# ---------------------------------------------------------------------------
def log_segments(case):
    """Split `log.solve` at each `Build  :` banner and evaluate each on its own.

    The ERRATUM records that `resume_k2h.sh` redirects with `>>`, so the file
    holds BOTH runs concatenated while `ExecutionTime` restarts near zero in the
    second.  `grep -c '^ExecutionTime = '` over the whole file is a count over
    two different clocks and is arithmetic about nothing.  Under the entry's own
    `_field_classes` rule (L-342) this is an INFRASTRUCTURE field: unsplit it
    voids the COST claim's arithmetic, and it can NEVER void the physics.
    """
    path = os.path.join(case, "log.solve")
    if not os.path.exists(path):
        refuse("%s does not exist; there is no log to read and nothing to grade"
               % path)
    segs, cur = [], None
    with open(path, errors="replace") as fh:
        for line in fh:
            if line.startswith("Build  :"):
                cur = {"t": [], "dt": [], "exec": [], "end": 0, "bad": []}
                segs.append(cur)
            if cur is None:
                continue
            try:
                if line.startswith("Time = "):
                    cur["t"].append(float(line.split("=")[1]))
                elif line.startswith("deltaT = "):
                    cur["dt"].append(float(line.split("=")[1]))
                elif line.startswith("ExecutionTime = "):
                    cur["exec"].append(float(line.split("=")[1].split("s")[0]))
                elif line.startswith("End"):
                    cur["end"] += 1
            except (ValueError, IndexError):
                pass
            low = line.lower()
            if "trapfpe" in low or "sigfpe" in low or "kinf" in low \
               or "omegainf" in low:
                continue                       # benign banners, not faults
            if ("nan" in low or "floating point exception" in low
                    or "segmentation" in low or "fatal" in low
                    or "diverg" in low):
                if len(cur["bad"]) < 50:
                    cur["bad"].append(line.rstrip()[:200])
    if not segs:
        refuse("%s carries no `Build  :` banner; it is not an OpenFOAM solver "
               "log and this instrument will not guess at its structure" % path)
    for s in segs:
        s["n_time"] = len(s["t"])
        s["n_exec"] = len(s["exec"])
        s["exec_s"] = s["exec"][-1] if s["exec"] else 0.0
        s["t_first"] = s["t"][0] if s["t"] else float("nan")
        s["t_last"] = s["t"][-1] if s["t"] else float("nan")
        s["dt_mean"] = (sum(s["dt"]) / len(s["dt"])) if s["dt"] else float("nan")
        s["core_min"] = s["exec_s"] * RANKS / 60.0
    return segs


def status_rc(case):
    """rc as the DETACHED WRAPPER captured it -- never as `setsid` returned it.

    `setsid timeout cmd` exits 0 for every outcome; the rc that means anything is
    the one `.k2h_inner.sh` captured INSIDE the wrapper and wrote to STATUS.
    """
    cands = sorted(glob.glob(os.path.join(os.path.dirname(case),
                                          "STATUS.%s" % os.path.basename(case))))
    if not cands:
        return None, "no STATUS.%s beside the case" % os.path.basename(case)
    txt = open(cands[-1]).read()
    m = re.search(r"^rc=(-?\d+)\s*$", txt, re.M)
    if m is None:
        return None, "STATUS carries no rc= line"
    return int(m.group(1)), cands[-1]


# ---------------------------------------------------------------------------
# 2b. D-COMPLETE -- rule 4 in section 6's transient form, WITH the age guard
# ---------------------------------------------------------------------------
def _times_on_rank(pdir):
    out = []
    for d in os.listdir(pdir):
        try:
            out.append(float(d))
        except ValueError:
            pass
    return sorted(out)


def d_complete(case, segs):
    why, detail = [], {}

    # clause 1 -- rc = 0, from the wrapper's own capture
    rc, rc_src = status_rc(case)
    detail["rc"] = rc
    detail["rc_source"] = rc_src
    if rc is None:
        why.append("rc could not be read (%s)" % rc_src)
    elif rc != 0:
        why.append("rc = %d, not 0" % rc)

    # clause 2 -- an End line, in the FINAL segment
    ends = [s["end"] for s in segs]
    detail["End_lines_per_segment"] = ends
    if not segs[-1]["end"]:
        why.append("the final log segment carries no `End` line")

    # clause 3 -- last written time == endTime, on EVERY rank
    procs = sorted(glob.glob(os.path.join(case, "processor*")))
    if len(procs) != RANKS:
        why.append("found %d processor* dirs, expected %d" % (len(procs), RANKS))
    lasts = {}
    for p in procs:
        ts = _times_on_rank(p)
        lasts[os.path.basename(p)] = ts[-1] if ts else None
    detail["last_written_time_per_rank"] = lasts
    for k, v in lasts.items():
        if v is None or abs(v - ENDTIME) > 1e-9:
            why.append("%s last written time %s != endTime %g" % (k, v, ENDTIME))

    # clause 4 -- fields present at endTime on every rank, PLUS the means
    tname = FR._tname(case, ENDTIME)
    missing = []
    for p in procs:
        for f in FIELDS_REQUIRED + MEANS_REQUIRED:
            if not os.path.exists(os.path.join(p, tname, f)):
                missing.append("%s/%s/%s" % (os.path.basename(p), tname, f))
    detail["missing_fields_at_endTime"] = missing
    if missing:
        why.append("%d field files missing at endTime (%s%s)"
                   % (len(missing), ", ".join(missing[:6]),
                      " ..." if len(missing) > 6 else ""))

    # clause 5 -- the step count, PER SEGMENT.  The ERRATUM's trap.
    seg_rows = []
    for i, s in enumerate(segs, 1):
        ok = (s["n_exec"] == s["n_time"]) or (s["n_exec"] == s["n_time"] - 1)
        seg_rows.append({"segment": i, "n_Time": s["n_time"],
                         "n_ExecutionTime": s["n_exec"],
                         "t_first": s["t_first"], "t_last": s["t_last"],
                         "exec_s": s["exec_s"], "core_min": s["core_min"],
                         "dt_mean": s["dt_mean"], "agrees": ok})
    detail["segments"] = seg_rows
    detail["concatenated_n_exec_DO_NOT_USE"] = sum(s["n_exec"] for s in segs)
    # A non-final segment may carry exactly ONE more `Time =` than
    # `ExecutionTime =`: the in-flight step that died mid-write (ERRATUM).
    for r, s in zip(seg_rows, segs):
        if s is segs[-1]:
            if r["n_ExecutionTime"] != r["n_Time"]:
                why.append("final segment: %d ExecutionTime lines against %d "
                           "Time lines; a completed segment must agree"
                           % (r["n_ExecutionTime"], r["n_Time"]))
        elif not r["agrees"]:
            why.append("segment %d: %d ExecutionTime lines against %d Time "
                       "lines; a killed segment may differ by at most the one "
                       "in-flight step" % (r["segment"], r["n_ExecutionTime"],
                                           r["n_Time"]))

    # clause 6 -- THE AGE GUARD.  `0/T` is touched last at launch and so dates
    # the run that was allowed to produce the answer.
    ref_paths = [os.path.join(case, "0", "T")]
    ref_paths += [os.path.join(p, "0", "T") for p in procs]
    ref_paths = [p for p in ref_paths if os.path.exists(p)]
    if not ref_paths:
        why.append("no `0/T` anywhere in the case; the age guard has no "
                   "reference and cannot be evaluated")
        detail["age_guard"] = "NO REFERENCE"
    else:
        ref = max(os.path.getmtime(p) for p in ref_paths)
        detail["age_guard_reference_mtime"] = ref
        detail["age_guard_reference_files"] = ref_paths
        stale = []
        for p in procs:
            for f in FIELDS_REQUIRED + MEANS_REQUIRED:
                fp = os.path.join(p, tname, f)
                if os.path.exists(fp) and os.path.getmtime(fp) <= ref:
                    stale.append("%s/%s/%s" % (os.path.basename(p), tname, f))
        detail["age_guard_stale_files"] = stale
        # NOT "PASS"/"FAIL".  Bare `FAIL` is not in rule 1's fixed vocabulary at
        # all -- rule 1 records an OPEN, UNRULED conflict about ledger cells that
        # read exactly that -- and a bare `PASS` here is a CLAUSE state, not this
        # level's gate verdict, so a reader grepping this record for a verdict
        # word would find one that is not the verdict.  Both are spelled so they
        # cannot be mistaken for either.
        detail["age_guard"] = ("AGE GUARD SATISFIED" if not stale
                               else "AGE GUARD VIOLATED")
        if stale:
            why.append("AGE GUARD: %d field(s) at endTime are NOT newer than "
                       "`0/T` (%s%s)" % (len(stale), ", ".join(stale[:6]),
                                         " ..." if len(stale) > 6 else ""))

    # not a clause, but reported: anything the log flagged
    bad = [b for s in segs for b in s["bad"]]
    detail["flagged_log_lines"] = bad
    if bad:
        why.append("%d log line(s) flagged as fault signatures" % len(bad))

    return ("COMPLETE" if not why else "INCOMPLETE"), why, detail


# ---------------------------------------------------------------------------
# 3. THE GRADED QUANTITY -- one reader, the frozen one
# ---------------------------------------------------------------------------
def dpbar(case, field=MEAN_FIELD, time=ENDTIME):
    """DPbar = areaAvg(p_rghMean, tile) - areaAvg(p_rghMean, return) at endTime.

    Both terms go through the FROZEN `foam_patch_reader.area_average`, which is
    the same reader that produced K2g's f1 and f2 -- section 11's "one reader,
    every level" discipline surviving the change of solver.
    """
    hi, src_hi = FR.area_average(case, time, field, PATCH_HI)
    lo, src_lo = FR.area_average(case, time, field, PATCH_LO)
    return hi - lo, {"hi": hi, "lo": lo, "path_hi": src_hi, "path_lo": src_lo}


def dpbar_decomposed_crosscheck(case, field=MEAN_FIELD, time=ENDTIME):
    """C-RECON: if `reconstructPar` ran, read the DECOMPOSED path too and require
    the two to agree.  `area_average` prefers the reconstructed directory when it
    exists, so the only way to exercise the other limb is a shadow that carries
    `processor*` and no reconstructed time directory."""
    tname = FR._tname(case, time)
    if not os.path.isdir(os.path.join(case, tname)):
        return None, "no reconstructed %s; the decomposed path was the only one" % tname
    tmp = tempfile.mkdtemp(prefix="k2h_recon_")
    try:
        os.symlink(os.path.join(case, "constant"), os.path.join(tmp, "constant"))
        for p in sorted(glob.glob(os.path.join(case, "processor*"))):
            os.symlink(p, os.path.join(tmp, os.path.basename(p)))
        val, _ = dpbar(tmp, field, time)
        return val, "decomposed"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# 4. RULE 3 -- THE PLANTED ZERO, planted into the artifact the real read path uses
# ---------------------------------------------------------------------------
def planted_zero(case, patch, field=MEAN_FIELD, time=ENDTIME, plant=PLANT):
    """Shadow the case with symlinks, add `plant` to every face of `patch` in a
    COPY of the endTime field, and require the production reader to see exactly
    it.  NOTHING under the real case directory is written to.

    `return` is the patch this control exists for: its p_rgh boundary condition
    is `fixedValue uniform 0`, so it reads EXACTLY 0.0 at every step and the
    graded difference rests on that zero.  A zero from a reader not shown able to
    see a non-zero is not evidence (CLAUDE.md rule 3).
    """
    before, _ = FR.area_average(case, time, field, patch)
    tname = FR._tname(case, time)
    tmp = tempfile.mkdtemp(prefix="k2h_plant_")
    try:
        os.symlink(os.path.join(case, "constant"), os.path.join(tmp, "constant"))
        rec = os.path.join(case, tname)
        if os.path.isdir(rec) and os.path.exists(os.path.join(rec, field)):
            os.mkdir(os.path.join(tmp, tname))
            _plant_file(os.path.join(rec, field),
                        os.path.join(tmp, tname, field), patch, plant)
        else:
            for p in sorted(glob.glob(os.path.join(case, "processor*"))):
                b = os.path.basename(p)
                os.mkdir(os.path.join(tmp, b))
                os.symlink(os.path.join(p, "constant"),
                           os.path.join(tmp, b, "constant"))
                os.mkdir(os.path.join(tmp, b, tname))
                _plant_file(os.path.join(p, tname, field),
                            os.path.join(tmp, b, tname, field), patch, plant)
        after, _ = FR.area_average(tmp, time, field, patch)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    pc = RT.external_plant_control("analyse_k2h.area_average[%s]" % patch,
                                   before, after, plant=plant,
                                   artifact="%s/%s/%s" % (case, tname, field),
                                   level="K2h_L3")
    pc["before"], pc["after"] = before, after
    return pc


def _plant_file(src, dst, patch, plant):
    """Add `plant` to every face value of `patch` and write the result to disk.

    Carried from `K2g_runs/analyse_k2g.py:_plant_file`, which is the shape the
    frozen reader was shown able to read.  A patch block this cannot find is
    copied through UNCHANGED, which makes the control FAIL rather than silently
    pass -- the correct direction for a control.
    """
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
# 5. D-STATIONARY -- section 6.  The dense series is the primary instrument and
#    the running means are the corroboration, and this says so rather than
#    choosing quietly.
# ---------------------------------------------------------------------------
def dense_dp_series(case):
    """The per-time-step DP_module series from the `dp_tile`/`dp_return` function
    objects, merged across every restart directory.

    On a restart OpenFOAM opens a NEW directory named for the restart time, so
    overlapping times exist in two files.  The later start wins, which is the
    standard restart semantics and the only reading consistent with the fields
    actually on disk.
    """
    def read(fo):
        out = {}
        dirs = sorted(glob.glob(os.path.join(case, "postProcessing", fo, "*")),
                      key=lambda d: float(os.path.basename(d)))
        if not dirs:
            refuse("no postProcessing/%s output; the dense DP_module series "
                   "does not exist and D-STATIONARY cannot be evaluated from it"
                   % fo)
        for d in dirs:
            for f in sorted(glob.glob(os.path.join(d, "*.dat"))):
                for line in open(f, errors="replace"):
                    if line.startswith("#"):
                        continue
                    p = line.split()
                    if len(p) >= 2:
                        try:
                            out[round(float(p[0]), 9)] = float(p[1])
                        except ValueError:
                            pass
        return out
    hi, lo = read("dp_tile"), read("dp_return")
    ts = sorted(set(hi) & set(lo))
    if not ts:
        refuse("dp_tile and dp_return share no common times; the difference "
               "cannot be formed")
    t = np.array(ts)
    v = np.array([hi[x] - lo[x] for x in ts])
    return t, v


def _tmean(t, v, a, b):
    """Time-weighted mean of v over [a, b] by trapezoid, NOT a sample mean."""
    k = (t >= a) & (t <= b)
    tt, vv = t[k], v[k]
    if tt.size < 2:
        return float("nan"), int(tt.size), (float("nan"), float("nan"))
    span = tt[-1] - tt[0]
    if span <= 0:
        return float("nan"), int(tt.size), (float(tt[0]), float(tt[-1]))
    return (float(np.trapezoid(vv, tt) / span), int(tt.size),
            (float(tt[0]), float(tt[-1])))


def d_stationary(case):
    t, v = dense_dp_series(case)
    detail = {"series_n": int(t.size), "series_t_first": float(t[0]),
              "series_t_last": float(t[-1])}
    if t[-1] < ENDTIME - 1e-6:
        detail["note"] = ("the dense series stops at %.4f, short of endTime %g"
                          % (t[-1], ENDTIME))
    m1, n1, s1 = _tmean(t, v, WIN_LO, WIN_MID)
    m2, n2, s2 = _tmean(t, v, WIN_MID, WIN_HI)
    mw, nw, sw = _tmean(t, v, WIN_LO, WIN_HI)
    detail.update({"half1_mean": m1, "half1_n": n1, "half1_span": s1,
                   "half2_mean": m2, "half2_n": n2, "half2_span": s2,
                   "window_mean_dense": mw, "window_n": nw, "window_span": sw,
                   "window": (WIN_LO, WIN_MID, WIN_HI),
                   "tolerance": STATIONARY_TOL})
    if not (np.isfinite(m1) and np.isfinite(m2)):
        return "NOT EVALUABLE", detail
    d = abs(m2 - m1)
    detail["half_difference"] = d
    return ("STATIONARY" if d <= STATIONARY_TOL else "NOT STATIONARY"), detail


#: THE ACCUMULATOR'S REAL HOME, READ OUT OF OpenFOAM's OWN SOURCE RATHER THAN
#: ASSUMED.  The brief this lane was given named
#: `processor*/<t>/uniform/fieldAverageProperties`.  THAT FILE DOES NOT EXIST IN
#: OpenFOAM 2606 AND NEVER WILL.  `fieldAverage::writeAveragingProperties()`
#: calls `item.writeState(propsDict)` and then `setProperty(...)`, and
#: `functionObjectList::createPropertiesDict()` builds that object at
#:
#:     <time>/uniform/functionObjects/functionObjectProperties
#:
#: (`functionObjectList.C:98-100`).  `writeState` adds exactly the keys
#: `totalIter` and `totalTime` (`fieldAverageItem.C:208`).  VERIFIED ON DISK:
#: `processor0/15/uniform/functionObjects/functionObjectProperties` already
#: exists, and all four ranks are byte-identical at md5
#: 8f01b63599b6571c9a73e8e68099fd38.
#:
#: TWO CONSEQUENCES, AND THE SECOND IS THE DANGEROUS ONE.
#:   (1) A check on the old path would have reported ABSENT ON ALL RANKS at
#:       t = 45 and returned a FALSE `NOT A RESULT` after the whole spend.
#:   (2) A PRESENCE TEST ON THE FILE IS NOW WORTHLESS, because the file exists
#:       from the first write at t = 5 carrying the OTHER function objects'
#:       state.  What must be checked is the `dpAverage` SUB-DICTIONARY inside
#:       it, and the `totalIter`/`totalTime` VALUES under each averaged field.
FA_FO_NAME = "dpAverage"            # system/controlDict:39, the fieldAverage FO
FA_PATHS = (os.path.join("uniform", "functionObjects",
                         "functionObjectProperties"),   # v1706+ and 2606
            os.path.join("uniform", "fieldAverageProperties"))  # pre-2016


def _block(txt, key):
    """The brace-balanced body of `key { ... }`, or None."""
    m = re.search(r"(?m)^\s*" + re.escape(key) + r"\s*$\s*\{", txt)
    if m is None:
        m = re.search(re.escape(key) + r"\s*\{", txt)
        if m is None:
            return None
    depth, j = 1, m.end()
    while depth and j < len(txt):
        depth += (txt[j] == "{") - (txt[j] == "}")
        j += 1
    return txt[m.end():j - 1]


def accumulator_agreement(case, time=ENDTIME):
    """The four ranks must AGREE on the averaging state, not merely carry a file.

    Four present-but-DISAGREEING accumulators pass a presence test and still
    produce a wrong mean, so `totalIter` and `totalTime` are read back per
    averaged field and compared across ranks.  Where the instrument looked is
    always reported, so an ABSENT reading never stands without the evidence of
    where it was looked for.
    """
    tname = FR._tname(case, time)
    rows, looked = {}, []
    for pdir in sorted(glob.glob(os.path.join(case, "processor*"))):
        b = os.path.basename(pdir)
        found = None
        for rel in FA_PATHS:
            fp = os.path.join(pdir, tname, rel)
            looked.append(fp)
            if os.path.exists(fp):
                found = fp
                break
        if found is None:
            rows[b] = None
            continue
        blk = _block(open(found, errors="replace").read(), FA_FO_NAME)
        if blk is None:
            rows[b] = {"file": found, "dpAverage": "ABSENT FROM THE FILE"}
            continue
        fields = {}
        for fm in re.finditer(r"(\w+)\s*\{([^{}]*)\}", blk):
            name, body = fm.group(1), fm.group(2)
            it = re.search(r"totalIter\s+(\d+)\s*;", body)
            tt = re.search(r"totalTime\s+([-\d.eE+]+)\s*;", body)
            if it or tt:
                fields[name] = {"totalIter": int(it.group(1)) if it else None,
                                "totalTime": float(tt.group(1)) if tt else None}
        rows[b] = {"file": found, "fields": fields}

    detail = {"rows": rows, "looked_in": sorted(set(looked)),
              "fo_name": FA_FO_NAME}

    absent = [k for k, r in rows.items() if r is None]
    no_block = [k for k, r in rows.items()
                if r is not None and r.get("dpAverage") == "ABSENT FROM THE FILE"]
    good = {k: r for k, r in rows.items() if r is not None and "fields" in r}

    if not rows:
        return "NO RANKS", detail
    if absent and len(absent) != len(rows):
        detail["note"] = ("the properties FILE is present on some ranks and not "
                          "others -- a WRONG NUMBER, not a crash")
        return "SPLIT", detail
    if len(no_block) and len(no_block) != len(rows):
        detail["note"] = ("the %r accumulator is present on some ranks and not "
                          "others -- a WRONG NUMBER, not a crash" % FA_FO_NAME)
        return "SPLIT", detail
    if absent:
        return "PROPERTIES FILE ABSENT ON ALL RANKS", detail
    if no_block:
        detail["note"] = ("the file exists on every rank but carries no %r "
                          "block. Before S-WINDOW opens at t = %g this is the "
                          "CORRECT state; at or after it, it means averaging "
                          "never started." % (FA_FO_NAME, WIN_LO))
        return "ACCUMULATOR ABSENT ON ALL RANKS", detail

    sig = {k: tuple(sorted((f, v["totalIter"], v["totalTime"])
                           for f, v in r["fields"].items()))
           for k, r in good.items()}
    detail["signature"] = {k: list(v) for k, v in sig.items()}
    if len(set(sig.values())) != 1:
        detail["note"] = ("the four ranks carry DIFFERENT totalIter/totalTime; "
                          "four present-but-disagreeing accumulators pass a "
                          "presence test and still give a wrong mean")
        return "DISAGREE", detail
    return "AGREE", detail


# ---------------------------------------------------------------------------
# 6. COST -- an INFRASTRUCTURE fact, computed and printed BESIDE the verdict
# ---------------------------------------------------------------------------
def cost(segs):
    per = [{"segment": i, "exec_s": s["exec_s"], "core_min": s["core_min"],
            "steps": s["n_time"], "dt_mean": s["dt_mean"],
            "s_per_step": (s["exec_s"] / s["n_exec"]) if s["n_exec"] else float("nan")}
           for i, s in enumerate(segs, 1)]
    tot_exec = sum(s["exec_s"] for s in segs)
    tot_cm = tot_exec * RANKS / 60.0
    return {"per_segment": per, "total_exec_s": tot_exec,
            "total_core_min": tot_cm,
            "point_core_min": POINT_CORE_MIN, "cap_core_min": CAP_CORE_MIN,
            "ratio_vs_point": tot_cm / POINT_CORE_MIN,
            "ratio_vs_cap": tot_cm / CAP_CORE_MIN,
            "point_crossed": tot_cm > POINT_CORE_MIN,
            "cap_crossed": tot_cm > CAP_CORE_MIN,
            "dollars_DERIVED_NOT_MEASURED": tot_cm / 60.0 * 0.0513,
            "rate_basis": "$0.0513/core-h, owner-stated 2026-08-21/22, "
                          "REPORTED-BY-OWNER and NOT MEASURED "
                          "(COMPUTE_BUDGET_CHARTER section 5)"}


# ---------------------------------------------------------------------------
def main():
    out = {"level": "K2h_L3", "case": CASE, "registration": REGISTRATION,
           "triple": "NONE -- K2h_L1 and K2h_L2 DO NOT EXIST; section 3 forbids "
                     "an observed order or a GCI from a mixed steady/"
                     "time-averaged set, with no caveat and no footnote"}
    try:
        out["freeze"] = verify_freeze()
        segs = log_segments(CASE)
        out["cost"] = cost(segs)

        comp, why, cdet = d_complete(CASE, segs)
        out["D_COMPLETE"] = {"state": comp, "why_not": why, "detail": cdet}

        acc, adet = accumulator_agreement(CASE)
        out["accumulator"] = {"state": acc, "detail": adet}

        if comp != "COMPLETE":
            out["verdict"] = "NOT A RESULT"
            out["verdict_reason"] = ("D-COMPLETE failed: " + "; ".join(why))
            return _emit(out, EXIT_NAR)
        if acc != "AGREE":
            out["verdict"] = "NOT A RESULT"
            out["verdict_reason"] = (
                "the fieldAverage accumulator is %s across the four ranks; the "
                "time mean it produced is not one quantity" % acc)
            return _emit(out, EXIT_NAR)

        pc_lo = planted_zero(CASE, PATCH_LO)
        pc_hi = planted_zero(CASE, PATCH_HI)
        out["planted_zero"] = {PATCH_LO: pc_lo, PATCH_HI: pc_hi}
        for p, pc in ((PATCH_LO, pc_lo), (PATCH_HI, pc_hi)):
            if not pc["passed"]:
                refuse("PLANTED-ZERO CONTROL FAILED on patch %r: the reader was "
                       "not shown able to see a planted %g (it saw %.12g). Its "
                       "zeros are not evidence (CLAUDE.md rule 3)"
                       % (p, PLANT, pc["read_back_delta"]))

        val, vdet = dpbar(CASE)
        out["DPbar"] = {"value": val, "detail": vdet, "band": BAND,
                        "reader": "FROZEN foam_patch_reader.area_average",
                        "field": MEAN_FIELD,
                        "what_this_quantity_actually_is": WHAT_DP_IS,
                        "planted_zero_is_what_makes_the_zero_evidence": (
                            "Both patches were shown able to see a planted "
                            "%g: see the `planted_zero` block, where each "
                            "read_back_delta equals the plant to 1e-12. A zero "
                            "from a reader not shown able to see a non-zero is "
                            "not evidence (CLAUDE.md rule 3)." % PLANT)}
        xval, xsrc = dpbar_decomposed_crosscheck(CASE)
        out["DPbar"]["crosscheck_decomposed"] = xval
        out["DPbar"]["crosscheck_note"] = xsrc
        if xval is not None:
            out["DPbar"]["crosscheck_delta"] = val - xval

        stat, sdet = d_stationary(CASE)
        out["D_STATIONARY"] = {"state": stat, "detail": sdet,
                               "instrument": "PRIMARY: the dense per-time-step "
                               "dp_tile/dp_return series, trapezoid-weighted. "
                               "Section 6 does not pin an instrument for "
                               "D-STATIONARY and this instrument states which it "
                               "used rather than choosing quietly."}
        if stat != "STATIONARY":
            out["verdict"] = "NOT A RESULT"
            out["verdict_reason"] = (
                "D-STATIONARY: the two halves of S-WINDOW differ by %.6g m2/s2, "
                "above the registered %.1e; a run still drifting across its own "
                "averaging window has not reached a statistically stationary "
                "state" % (sdet.get("half_difference", float("nan")),
                           STATIONARY_TOL))
            return _emit(out, EXIT_NAR)

        lo, hi = BAND
        if lo <= val <= hi:
            out["verdict"] = "PASS"
            out["verdict_reason"] = ("DPbar = %.6f m2/s2 lies inside the "
                                     "pre-registered G-DPBAR band [%.4f, %.4f]"
                                     % (val, lo, hi))
            return _emit(out, EXIT_OK)
        out["verdict"] = "GATE FAIL"
        out["verdict_reason"] = ("DPbar = %.6f m2/s2 lies OUTSIDE the "
                                 "pre-registered G-DPBAR band [%.4f, %.4f]"
                                 % (val, lo, hi))
        return _emit(out, EXIT_FAIL)

    except Refusal as e:
        # A REFUSAL IS NOT A VERDICT.  `REFUSED` is not in CLAUDE.md rule 1's
        # fixed vocabulary, and a field named `verdict` holding a non-vocabulary
        # word invites a later reader to transcribe it into a ledger cell as one
        # -- which is the open conflict rule 1 already records about cells
        # reading a bare FAIL.  A refusal means the comparator DECLINED TO GRADE:
        # nothing was graded, so there is no verdict to carry.  The family's
        # precedent is `analyse_k2g.py:565`, which PRINTS "REFUSED (exit 2)" and
        # writes that word into no verdict field.  The printed spelling is kept
        # exactly, because other records read it; the field is emptied.
        out["verdict"] = None
        out["grading_refused"] = {"reason": str(e), "exit": EXIT_REFUSE}
        out["verdict_reason"] = None
        return _emit(out, EXIT_REFUSE)


def _emit(out, code):
    c = out.get("cost", {})
    if not c:
        # A refusal can fire BEFORE the log is read (a broken freeze refuses
        # first, by design).  Printing "nan core-min" there is worse than saying
        # nothing: nan reads as a measurement that went wrong rather than as a
        # measurement never taken.
        out["cap_note"] = (
            "COST NOT COMPUTED. The comparator refused before reading the log, "
            "so no core-minute figure was measured. This is an ABSENT figure, "
            "not a zero and not a nan; it is left out rather than approximated "
            "(COST_CALIBRATION.md append rule 2).")
        print(json.dumps(out, indent=2, default=str))
        print("\n" + "=" * 78)
        print("K2h_L3  --  ONE LEVEL, NO TRIPLE, NO OBSERVED ORDER, NO GCI")
        print("REFUSED (exit 2): %s" % out["grading_refused"]["reason"])
        print("NOTE   : A REFUSAL IS NOT A VERDICT.  Nothing was graded, so no")
        print("         verdict word from rule 1's fixed vocabulary applies and")
        print("         the `verdict` field is null.  Exit 2 is the channel that")
        print("         carries a refusal; do not transcribe the word 'REFUSED'")
        print("         into a verdict or ledger cell as though it were one.")
        print("COST   : %s" % out["cap_note"])
        print("=" * 78)
        return code
    out["cap_note"] = (
        "THE CAP IS REPORTED BESIDE THE PHYSICS VERDICT AND MOVES IT IN NEITHER "
        "DIRECTION. Whether a cap crossing forces NOT A RESULT is ESCALATED AND "
        "UNRULED (her item 7 'cap -> NOT A RESULT, never raised' against her "
        "2026-08-26 universal rule that bookkeeping never voids physics, against "
        "this entry's own _field_classes which places cost among the "
        "INFRASTRUCTURE fields). This instrument therefore neither suppresses the "
        "crossing nor lets it manufacture a NOT A RESULT. "
        "CAP %g core-min %s: actual %.1f core-min = %.2fx POINT %g, %.2fx cap."
        % (c.get("cap_core_min", CAP_CORE_MIN),
           "CROSSED" if c.get("cap_crossed") else "not crossed",
           c.get("total_core_min", float("nan")),
           c.get("ratio_vs_point", float("nan")),
           c.get("point_core_min", POINT_CORE_MIN),
           c.get("ratio_vs_cap", float("nan"))))
    print(json.dumps(out, indent=2, default=str))
    print("\n" + "=" * 78)
    print("K2h_L3  --  ONE LEVEL, NO TRIPLE, NO OBSERVED ORDER, NO GCI")
    if out.get("grading_refused"):
        print("REFUSED (exit 2): %s" % out["grading_refused"]["reason"])
        print("NOTE   : A REFUSAL IS NOT A VERDICT.  Nothing was graded, so no")
        print("         verdict word from rule 1's fixed vocabulary applies and")
        print("         the `verdict` field is null.  Exit 2 is the channel that")
        print("         carries a refusal; do not transcribe the word 'REFUSED'")
        print("         into a verdict or ledger cell as though it were one.")
    else:
        print("VERDICT: %s" % out["verdict"])
        print("REASON : %s" % out["verdict_reason"])
    print("COST   : %s" % out["cap_note"])
    print("=" * 78)
    return code


if __name__ == "__main__":
    sys.exit(main())
