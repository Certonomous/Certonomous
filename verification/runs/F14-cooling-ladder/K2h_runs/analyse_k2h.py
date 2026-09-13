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


#: OpenFOAM's own end-of-file banner.  A field file without it was truncated
#: mid-write, which is exactly what a killed solver leaves behind.
FOAM_EOF_BANNER = "// ******"


def _banner_closed(path):
    try:
        with open(path, "rb") as fh:
            fh.seek(max(0, os.path.getsize(path) - 400))
            return FOAM_EOF_BANNER.encode() in fh.read()
    except OSError:
        return False


def d_complete(case, segs):
    """AD7.3's SIX CLAUSES, each strict.  Failing any one is NOT A RESULT.

    AD7.3 replaced the original clause 3 -- "last WRITTEN time == endTime" --
    because it is WINNABLE BY NOTHING under endTime 112 with writeInterval 5:
    112 is not a multiple of 5, so no run, no rerun and no successor carrying
    that pair can ever satisfy it.  A clause with no passing input is not
    measuring the run; it is measuring a defect in the document.

    THE REPLACEMENT IS OpenFOAM'S OWN TEST, NOT ONE THIS LAB INVENTED, and that
    is the whole reason this is a reading rather than a relaxation:

        Time::run() is  value <  endTime - 0.5*deltaT
        Time::end() is  value >  endTime - 0.5*deltaT

    OpenFOAM HAS NEVER TESTED EXACT FLOAT EQUALITY against endTime.  The
    half-timestep tolerance IS the solver's definition of having finished, and it
    is why the `End` line gets written at all.  `deltaT` is read FROM THE RUN, not
    from a constant, and the three numbers -- value, tolerance, shortfall -- are
    printed beside the result so a reader can redo the comparison without the
    OpenFOAM source in front of them.

    WHICH DIRECTORY THE LAST WRITE LANDED IN IS AN INFRASTRUCTURE FACT, set
    entirely by writeInterval (this entry's own `_field_classes`, L-342).  It is
    REPORTED, and it does not by itself produce NOT A RESULT.
    """
    why, detail = [], {}
    final = segs[-1]

    # ---- clause 1: rc = 0, from the WRAPPER's own capture -------------------
    rc, rc_src = status_rc(case)
    detail["clause_1_rc"] = {"rc": rc, "source": rc_src}
    if rc is None:
        why.append("clause 1: rc could not be read (%s)" % rc_src)
    elif rc != 0:
        why.append("clause 1: rc = %d, not 0" % rc)

    # ---- clause 2: an End line in log.solve ---------------------------------
    detail["clause_2_End_lines_per_segment"] = [x["end"] for x in segs]
    if not final["end"]:
        why.append("clause 2: the final log segment carries no `End` line")

    # ---- clause 3: integrated to endTime, AS OPENFOAM TESTS IT --------------
    last_t = final["t_last"] if final["t"] else float("nan")
    dts = [x for x in final["dt"] if x == x]
    dt_last = dts[-1] if dts else float("nan")
    tol = 0.5 * dt_last
    shortfall = ENDTIME - last_t
    reached = last_t > (ENDTIME - tol)
    detail["clause_3_endTime"] = {
        "test": "Time::end(): last_time > endTime - 0.5*deltaT",
        "last_logged_time": last_t,
        "endTime": ENDTIME,
        "deltaT_read_from_the_run": dt_last,
        "half_deltaT_tolerance": tol,
        "shortfall": shortfall,
        "inside_the_solvers_own_tolerance": bool(reached),
        "note": ("Exact float equality is NOT the test and never was the "
                 "solver's. deltaT is read from the run, not from a constant."),
        "result": "REACHED endTime" if reached else "DID NOT REACH endTime"}
    if not reached:
        why.append("clause 3: last logged time %.8f is NOT inside OpenFOAM's own "
                   "tolerance of endTime %g -- shortfall %.8f against "
                   "0.5*deltaT = %.8f" % (last_t, ENDTIME, shortfall, tol))

    # ---- the last WRITE: reported as INFRASTRUCTURE, never a failure -------
    procs = sorted(glob.glob(os.path.join(case, "processor*")))
    if len(procs) != RANKS:
        why.append("found %d processor* dirs, expected %d" % (len(procs), RANKS))
    lasts = {}
    for p_ in procs:
        ts = _times_on_rank(p_)
        lasts[os.path.basename(p_)] = ts[-1] if ts else None
    vals = [v for v in lasts.values() if v is not None]
    last_written = max(vals) if vals else None
    detail["INFRASTRUCTURE_last_written_time"] = {
        "per_rank": lasts, "value": last_written, "endTime": ENDTIME,
        "why_it_differs": ("writeInterval 5 does not divide endTime 112, and "
                           "OpenFOAM writes only on writeInterval boundaries. "
                           "AD7.3: which directory the last write landed in is "
                           "an INFRASTRUCTURE fact and does NOT by itself "
                           "produce NOT A RESULT.")}
    if last_written is None:
        why.append("no written time on any rank")
    elif len(set(vals)) != 1:
        why.append("the four ranks disagree on their last written time: %s"
                   % lasts)

    # ---- clause 4: fields at the LAST WRITTEN time, banner-closed ----------
    tname = FR._tname(case, last_written) if last_written is not None else None
    missing, truncated = [], []
    if tname is not None:
        for p_ in procs:
            for f in FIELDS_REQUIRED + MEANS_REQUIRED:
                fp = os.path.join(p_, tname, f)
                if not os.path.exists(fp):
                    missing.append("%s/%s/%s" % (os.path.basename(p_), tname, f))
                elif not _banner_closed(fp):
                    truncated.append("%s/%s/%s" % (os.path.basename(p_), tname, f))
    detail["clause_4_fields"] = {
        "at_time": tname, "required": list(FIELDS_REQUIRED + MEANS_REQUIRED),
        "missing": missing, "not_banner_closed": truncated,
        "checked": "presence AND OpenFOAM's own end-of-file banner, all %d ranks"
                   % len(procs)}
    if missing:
        why.append("clause 4: %d field file(s) missing at the last written time "
                   "(%s%s)" % (len(missing), ", ".join(missing[:6]),
                               " ..." if len(missing) > 6 else ""))
    if truncated:
        why.append("clause 4: %d field file(s) are NOT closed by OpenFOAM's "
                   "end-of-file banner, i.e. truncated mid-write (%s%s)"
                   % (len(truncated), ", ".join(truncated[:6]),
                      " ..." if len(truncated) > 6 else ""))

    # ---- clause 5: THE AGE GUARD -------------------------------------------
    ref_paths = [os.path.join(case, "0", "T")]
    ref_paths += [os.path.join(p_, "0", "T") for p_ in procs]
    ref_paths = [x for x in ref_paths if os.path.exists(x)]
    if not ref_paths or tname is None:
        why.append("clause 5: the age guard has no reference `0/T` and cannot "
                   "be evaluated")
        detail["clause_5_age_guard"] = {"state": "NO REFERENCE"}
    else:
        ref = max(os.path.getmtime(x) for x in ref_paths)
        stale = []
        for p_ in procs:
            for f in FIELDS_REQUIRED + MEANS_REQUIRED:
                fp = os.path.join(p_, tname, f)
                if os.path.exists(fp) and os.path.getmtime(fp) <= ref:
                    stale.append("%s/%s/%s" % (os.path.basename(p_), tname, f))
        detail["clause_5_age_guard"] = {
            "state": "AGE GUARD SATISFIED" if not stale else "AGE GUARD VIOLATED",
            "reference_mtime": ref, "reference_files": ref_paths,
            "stale": stale}
        if stale:
            why.append("clause 5: AGE GUARD -- %d field(s) are NOT newer than "
                       "`0/T`" % len(stale))

    # ---- clause 6: the accumulator PRESENT AND AGREEING on all four ranks ---
    # STRICTER THAN ANYTHING THE ORIGINAL TEXT DEMANDED (AD7.3), and said so here
    # rather than buried: the original asked only that the means be present.
    acc_state, acc_detail = accumulator_agreement(
        case, last_written if last_written is not None else ENDTIME)
    detail["clause_6_accumulator"] = {
        "state": acc_state, "detail": acc_detail,
        "STRICTER_THAN_THE_ORIGINAL": (
            "AD7.3 clause 6 requires the fieldAverage accumulator PRESENT AND "
            "AGREEING across all four ranks on totalIter and totalTime. The "
            "original text asked only that the mean FIELDS be present. Four "
            "present-but-disagreeing accumulators would have satisfied that and "
            "still produced a wrong mean.")}
    if acc_state != "AGREE":
        why.append("clause 6: the fieldAverage accumulator is %s across the four "
                   "ranks; the time mean it produced is not one quantity"
                   % acc_state)

    # ---- the log-segment split, kept visible (the ERRATUM's trap) ----------
    detail["log_segments"] = [
        {"segment": i, "n_Time": x["n_time"], "n_ExecutionTime": x["n_exec"],
         "t_first": x["t_first"], "t_last": x["t_last"], "exec_s": x["exec_s"],
         "core_min": x["core_min"], "dt_mean": x["dt_mean"]}
        for i, x in enumerate(segs, 1)]
    detail["concatenated_n_exec_DO_NOT_USE"] = sum(x["n_exec"] for x in segs)

    bad = [b for x in segs for b in x["bad"]]
    detail["flagged_log_lines"] = bad
    if bad:
        why.append("%d log line(s) flagged as fault signatures" % len(bad))

    detail["AD7_4_DISCLOSURE"] = window_disclosure(last_written)
    # BOTH ENDS OF THE WINDOW, HONESTLY. AD7.4 discloses the 2 s shortfall at the
    # END. This discloses the 0.0083 s overshoot at the START. It is four orders
    # of magnitude smaller and it changes nothing -- but a window whose true
    # start is 41.9917 and whose record says 42 is a small false statement, and
    # small false statements are the ones that survive into papers.
    if last_written is not None:
        detail["MEASURED_COVERED_WINDOW"] = measured_covered_window(
            case, last_written)
    return ("COMPLETE" if not why else "INCOMPLETE"), why, detail


def measured_covered_window(case, last_written):
    """The window the average ACTUALLY covers, derived from the accumulator.

    NOT the registered `timeStart`, and not the first execution time either --
    the two differ by exactly one `deltaT` and only one of them is a WINDOW.

    `fieldAverage` adds the WHOLE `deltaT` of the step during which it fires, so
    a step executing at time t represents the interval (t - deltaT, t].  The
    covered interval therefore begins at `last_written - totalTime`, one full
    step before the first execution.  MEASURED HERE FROM `totalTime` ITSELF, so
    the number in the record is the accumulator's own arithmetic and not a
    restatement of what the registration asked for.

    `timeStart` 42 is not a step boundary, and the functionObject gate is
    `time >= timeStart - 0.5*deltaT` (timeControlFunctionObject.C:94), so the
    step that crossed 42 contributed its entire `deltaT` INCLUDING the part
    before 42.  That is ordinary OpenFOAM behaviour, not a defect, and the
    accumulator is not to be "corrected" -- the number it produces is the right
    one.  This is a REPORTING requirement.
    """
    try:
        st, det = accumulator_agreement(case, last_written)
        if st != "AGREE":
            return {"state": st, "note": "no agreeing accumulator to measure from"}
        rows = det["rows"]
        one = rows[sorted(rows)[0]]["fields"]
        tt = sorted({v["totalTime"] for v in one.values()})
        it = sorted({v["totalIter"] for v in one.values()})
        if len(tt) != 1:
            return {"state": "FIELDS DISAGREE", "totalTime_values": tt}
        total_time = tt[0]
        n = it[0] if len(it) == 1 else None
        start = float(last_written) - total_time
        early = WIN_LO - start
        # AD8.3: TWO numbers, both right, of DIFFERENT objects. Stating only one
        # would be a small false precision. They differ by exactly one deltaT.
        first_step = (float(last_written) - (n - 1) * (total_time / n)) \
            if n else None
        dt_eff = (total_time / n) if n else None
        # AD8.3's independent arithmetic: totalTime must be EXACTLY the sum of n
        # consecutive steps. Stronger than rank agreement, because four ranks can
        # agree on an identically wrong number.
        return {
            "AD8_4_PARAGRAPH_VERBATIM": (
                "Averaging's first included step was t = 41.99763593, not 42 -- "
                "0.00236407 s early, 0.400 of one timestep, by OpenFOAM's own "
                "`timeStart - 0.5*deltaT` gate. The accumulated interval "
                "therefore begins at 41.99172577. The direction is MORE "
                "coverage, not less: 0.003 % of the 70 s window, four orders of "
                "magnitude below the ~2 s shortfall at the other end that AD7.4 "
                "already discloses."),
            "first_step_INCLUDED_in_the_mean": first_step,
            "first_step_early_by_s": (WIN_LO - first_step) if first_step else None,
            "first_step_early_in_timesteps":
                ((WIN_LO - first_step) / dt_eff) if first_step else None,
            "the_two_numbers_differ_by_one_deltaT":
                (first_step - start) if first_step else None,
            "deltaT_implied_by_totalTime_over_totalIter": dt_eff,
            "covered_start_MEASURED": start,
            "covered_end": float(last_written),
            "registered_timeStart": WIN_LO,
            "earlier_than_registered_s": early,
            "totalTime": total_time, "totalIter": it[0] if len(it) == 1 else it,
            "as_fraction_of_registered_window_pct":
                100.0 * early / (WIN_HI - WIN_LO),
            "why": ("fieldAverage adds the WHOLE deltaT of the step during which "
                    "it activates, and timeStart 42 is not a step boundary, so "
                    "the step that crossed 42 contributed its entire deltaT "
                    "including the part before 42. Ordinary OpenFOAM behaviour, "
                    "not a defect; the accumulator is not corrected."),
            "direction": ("EARLIER, i.e. MORE coverage than the registered start "
                          "implies, and it moves the mean toward slightly "
                          "earlier data")}
    except Exception as e:                              # noqa: BLE001
        return {"state": "NOT MEASURABLE", "error": "%s: %s"
                % (type(e).__name__, e)}


def window_disclosure(last_written):
    """AD7.4's disclosure. THE PRICE OF THE RULING, AND IT IS NOT OPTIONAL.

    A permissive ruling that hides that it is permissive is worth less than no
    ruling, so this rides on EVERY emission of the graded value -- the grade
    record, the certificate, and burned into every figure caption.  A figure
    travels further than the record it came from.
    """
    if last_written is None:
        return "AD7.4 disclosure: no written time, so no window was covered."
    if float(last_written) <= WIN_LO:
        # Guard against a nonsense NEGATIVE window.  Before the last write
        # reaches S-WINDOW's start there is no covered interval at all, and
        # printing "-2 s, -2.9 %" would be arithmetic about nothing dressed as a
        # coverage figure.
        return ("AD7.4 disclosure: the last written time %g is at or BEFORE "
                "S-WINDOW's start %g, so NONE of the registered %g -> %g window "
                "is covered and no mean over it exists. This is not a small "
                "shortfall; it is zero coverage."
                % (float(last_written), WIN_LO, WIN_LO, WIN_HI))
    covered = float(last_written) - WIN_LO
    registered = WIN_HI - WIN_LO
    return (
        "The graded DPbar is the mean over simulated %g -> %g s, NOT %g -> %g s. "
        "That is %g s of the registered %g s window -- %.1f %%. The registered "
        "S-WINDOW is %g -> %g and it was NOT fully covered, because this solver "
        "writes only on writeInterval boundaries and %g is not one."
        % (WIN_LO, float(last_written), WIN_LO, WIN_HI, covered, registered,
           100.0 * covered / registered, WIN_LO, WIN_HI, WIN_HI))


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
def diagnostics_beside_a_refusal(case):
    """The physics numbers, computed and printed BESIDE a NOT A RESULT.

    CLAUDE.md rule 5's own spelling for a non-result is "`NOT A RESULT`, value,
    both triples and orders PRINTED BESIDE IT".  A comparator that returns a bare
    NOT A RESULT after a four-figure core-minute spend has thrown away everything
    the run computed.  So the value, the plant and the stationarity are evaluated
    at the latest time that actually exists and reported here.

    THIS BLOCK CANNOT CHANGE THE VERDICT, and that is enforced structurally: it is
    only ever called AFTER `out["verdict"]` has been set, it never writes to
    `out["verdict"]`, and every limb is individually wrapped so that a diagnostic
    that fails degrades to its own error string instead of propagating.

    It is NOT an annotation that softens the verdict.  The verdict stands exactly
    as the gate set it; these are the numbers a reader needs in order to act on
    it -- to see whether the run was physically healthy while failing a
    completion clause, which is a different situation from a run that diverged.
    """
    d = {"WHAT_THIS_IS": (
        "NOT THE GRADED VALUE. The verdict printed above stands unchanged and "
        "nothing in this block can alter it. These are the physics numbers at "
        "the latest time that EXISTS on disk, so that a NOT A RESULT is not "
        "also an empty record. Rule 5 requires the value to be printed beside a "
        "non-result rather than withheld.")}
    try:
        procs = sorted(glob.glob(os.path.join(case, "processor*")))
        common = None
        for p_ in procs:
            ts = set()
            for x in os.listdir(p_):
                try:
                    ts.add(float(x))
                except ValueError:
                    pass
            common = ts if common is None else (common & ts)
        if not common:
            d["error"] = "the four ranks share no written time"
            return d
        t = max(common)
        d["latest_common_written_time"] = t
        d["endTime_registered"] = ENDTIME
        d["shortfall_s"] = ENDTIME - t
    except Exception as e:                              # noqa: BLE001
        d["error"] = "%s: %s" % (type(e).__name__, e)
        return d

    for label, field in (("time_averaged", MEAN_FIELD), ("instantaneous", "p_rgh")):
        try:
            v, det = dpbar(case, field, t)
            d[label] = {"field": field, "DP_module": v, "detail": det}
        except Exception as e:                          # noqa: BLE001
            d[label] = {"field": field, "unavailable": "%s: %s"
                        % (type(e).__name__, e)}

    try:
        pc = planted_zero(case, PATCH_LO, MEAN_FIELD, t)
        d["planted_zero_%s" % PATCH_LO] = pc
    except Exception as e:                              # noqa: BLE001
        try:
            d["planted_zero_%s" % PATCH_LO] = planted_zero(case, PATCH_LO, "p_rgh", t)
            d["planted_zero_note"] = ("planted into p_rgh because %s is not "
                                      "present at t=%s (%s)"
                                      % (MEAN_FIELD, t, type(e).__name__))
        except Exception as e2:                         # noqa: BLE001
            d["planted_zero_%s" % PATCH_LO] = {"unavailable": str(e2)}

    try:
        st, sd = d_stationary(case)
        d["D_STATIONARY_from_the_dense_series"] = {"state": st, "detail": sd,
            "note": ("the dense dp_tile/dp_return series is written EVERY TIME "
                     "STEP and is independent of what was checkpointed, so this "
                     "limb survives a missing time directory")}
    except Exception as e:                              # noqa: BLE001
        d["D_STATIONARY_from_the_dense_series"] = {"unavailable": "%s: %s"
                                                   % (type(e).__name__, e)}
    d["WHAT_DP_IS"] = WHAT_DP_IS
    return d


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

        # The accumulator is AD7.3 CLAUSE 6 and is graded inside `d_complete`
        # at the LAST WRITTEN TIME.  It is deliberately NOT re-gated here: the
        # earlier version of this file checked it at ENDTIME 112, a directory
        # that never exists, and would have produced a second false NOT A RESULT
        # on a clause already graded correctly a few lines above.
        out["accumulator"] = out["D_COMPLETE"]["detail"].get("clause_6_accumulator")

        if comp != "COMPLETE":
            out["verdict"] = "NOT A RESULT"
            out["verdict_reason"] = ("D-COMPLETE failed: " + "; ".join(why))
            # Computed AFTER the verdict is set, and it cannot reach back into it.
            out["diagnostics_not_the_graded_value"] = \
                diagnostics_beside_a_refusal(CASE)
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
                        "AD7_4_DISCLOSURE": out["D_COMPLETE"]["detail"]
                            .get("AD7_4_DISCLOSURE"),
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
    disc = (out.get("D_COMPLETE", {}).get("detail", {}) or {}).get("AD7_4_DISCLOSURE")
    if disc:
        # AD7.4: THE PRICE OF THE RULING, AND IT IS NOT OPTIONAL.  A permissive
        # ruling that hides that it is permissive is worth less than no ruling.
        print("WINDOW : %s" % disc)
    print("COST   : %s" % out["cap_note"])
    print("=" * 78)
    return code


if __name__ == "__main__":
    sys.exit(main())
