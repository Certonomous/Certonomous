#!/usr/bin/env python3
"""T25R6c-R2 GRADER / COMPARATOR -- G-R2-1 (PLATEAU) and G-R2-2 (DIRECTION).

FROZEN AT THE R2 PRE-REGISTRATION COMMIT, BEFORE ANY CASE DIRECTORY HOLDS
COMPUTE.  Registration: docs/campaigns/T-family/T25R6cR2_PREREGISTRATION.md.

THIS FILE IS A CHANGED MEASUREMENT SCRIPT.  It is the successor to the frozen
grade_t25R6c.py and it differs from it in ways that CHANGE WHAT IS MEASURED.
Under SUPERVISION_CHARTER section 3 check 1 that diff is the supervisor's
PERSONAL, NON-DELEGABLE read.  The lane that wrote this file has NOT graded with
it and there is nothing yet to grade.

WHAT IS MEASURED
----------------
    rho = r(leg B, POST-TRANSIENT) / r(leg A)

both per-step CPU rates from `ExecutionTime` deltas, taken WITHIN ONE RUN, so
arm, mesh, ranks, `0/` and solver are identical between numerator and
denominator by construction.  Leg A is 40 steps at deltaT 0.02 (the window every
C4/C5 wall factor was measured on).  Leg B is 1110 steps at deltaT 0.1 from
`latestTime`, t = 0.8 -> 111.8 s, of which the FIRST 40 ARE DISCARDED as the
restart transient and the remaining 1070 are graded.

`ExecutionTime` IS CPU TIME, NOT WALL TIME, AND THAT IS ESTABLISHED, NOT ASSUMED
-------------------------------------------------------------------------------
OpenFOAM-v2606, this box's build, at
  src/OpenFOAM/db/Time/Time.H:533          "the elapsed ExecutionTime (cpu-time)"
  src/OpenFOAM/db/Time/TimeIO.C:631        os << "ExecutionTime = " <<
                                              elapsedCpuTime() << " s"
  src/OSspecific/POSIX/cpuTime/cpuTimeFwd.H   typedef cpuTimePosix cpuTime
  src/OSspecific/POSIX/cpuTime/cpuTimePosix.C:40-47
        diff(a,b) = ((a.tms_utime + a.tms_stime) - (b.tms_utime + b.tms_stime))
                    / sysconf(_SC_CLK_TCK),  value_type::update() -> ::times()
`times(2)` fills tms_utime/tms_stime for the CALLING PROCESS ONLY -- children go
to tms_cutime/tms_cstime, which OpenFOAM never reads.  So ExecutionTime is
rank 0's own user+system CPU: NOT wall, and NOT a sum over ranks.

WHAT THAT CHANGES, AND WHAT IT DOES NOT.  T25R6c's A1.2(a) treated a contended
box as INFLATING the measured rate.  For the DESCHEDULING pathway that is
backwards: a process that loses the CPU accrues LESS cpu-time.  The confound
survives by two other pathways that cpu-time does NOT filter -- memory-bandwidth
and last-level-cache contention, which makes identical work cost more real
cycles; and MPI busy-wait, where rank 0 SPINS in a collective while a
descheduled peer catches up and the spin is charged to rank 0 as user cpu-time.
T25R6c measured ExecutionTime/ClockTime = 0.9573 (leg A) and 0.9921 (leg B),
which is that signature.  AND THE RESIDUAL CONFOUND IS MEASURED, NOT ASSUMED:
over T25R6c's 360 settled leg-B steps the linear-solver iteration count is
CONSTANT (92..94, a 2.15 % integer spread) while the 40-step window rate scatters
by 2.915 %.  Identical work, different cost: that is the machine.  R2 therefore
registers, IN ADVANCE, that a rho finer than about +/-3 % is NOT ACHIEVABLE on
this shared box, and G-R2-2 is only readable because the predicted effect
(rho - 1 = 7.5 %) is about 2.6 floor-widths.

THE THREE THINGS THIS GRADER CHANGES, AND WHY (the supervisor's diff)
---------------------------------------------------------------------
(1) THE PLATEAU WINDOW.  T25R6c's statistic was
        |r(last 40) - r(first 40)| / r(last 40)
    with `first 40` = leg-B steps 1..40 -- WHICH ARE THE RESTART TRANSIENT.
    T25R6c measured that window 10.43 % CHEAPER than the settled level, so the
    statistic asymptotes to 10.43 % and NO LEG-B LENGTH DRIVES IT TO 5 %.  It
    tests "has the rate stopped changing SINCE THE RESTART", not "has the rate
    plateaued".  R2 discards the first 40 steps and splits the remaining 1070
    into halves.  THE THRESHOLD NUMBER IS UNCHANGED AT 5 %.
(2) THE NORMALISER.  T25R6c divided by `last`.  With a RISING rate last > first,
    so dividing by `last` yields the SMALLER statistic: T25R6c's 13.939 % is
    16.197 % under the stricter normaliser.  ITS GATE FAILED UNDER THE LOOSER OF
    THE TWO AND WOULD ONLY HARDEN UNDER THE STRICTER, so that verdict is robust
    to the choice.  R2 removes the choice: it computes BOTH and grades the
    LARGER.  This is registered here so that nobody later "tightens" the
    normaliser and mistakes a harder gate for a moved verdict.
    THIS IS NOT AN INSTANCE OF THE OPEN D389 HAZARD.  D389 concerns normalising
    an ABSOLUTE TEMPERATURE by its mean, where the zero is arbitrary and the
    ratio is therefore not meaningful.  A rate in s/step has a meaningful zero,
    so endpoint normalisation is legitimate here.  D389 IS OPEN AND IS NOT
    SETTLED BY THIS FILE.
(3) rho's WINDOW.  T25R6c's rho averaged ALL 400 leg-B steps including the cheap
    transient.  R2 grades the post-transient rate, which RAISES rho from
    1.063997 to a predicted 1.075209 and so makes G-R2-2 HARDER.  The reason is
    physical and fixed before the run: the ladder runs 8,300 leg-B steps, so a
    40-step restart transient is 0.48 % of the mixture and the settled rate is
    the one that prices the ladder.  The all-steps rho is REPORTED beside it so
    R2 and R6c stay directly comparable.

DEFAULT-DENY, IN ORDER
----------------------
  1. PLANTED-ZERO control on the ExecutionTime reader, BOTH legs   (rule 3)
  2. rule 4 completion, all conjuncts, AGE GUARD vs `0/module/T`   (rule 4)
  3. C-R2-1  the run's OWN transient must end at or before step 40
  4. G-R2-1  PLATEAU -- evaluated BEFORE rho is consulted
  5. G-R2-2  DIRECTION
A failure at 1 is a REFUSAL (exit 2) and issues no verdict at all.  A failure at
2, 3 or 4 is NOT A RESULT (exit 4).  THE COMPARATOR REFUSES RATHER THAN DEGRADES.

NO ROACHE TRIPLE IS FORMED, AND THAT IS A REGISTERED DECISION.  This rung
measures WALL COST inside one transient at one mesh.  There is no grid family,
no solution functional at convergence, and therefore no triple: rule 5's
machinery does not apply and is not invoked.  No observed order and no GCI is
computed, quoted, or derivable from this rung.  A successor reading a
grid-convergence claim off these numbers gets NOT A RESULT.

    python3 grade_t25R6cR2.py --grade
    python3 grade_t25R6cR2.py --selftest
"""
import glob
import hashlib
import json
import math
import os
import re
import shutil
import statistics
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

EXIT_PASS = 0
EXIT_REFUSE = 2
EXIT_GATE_FAIL = 3
EXIT_NOT_A_RESULT = 4

# --- THE CASE.  Module-level literals ON PURPOSE: check_comparator_freeze.py
# --- derives a comparator's marker scope from string constants in its own
# --- source (D471.1).  A grader whose source names no marker in its tree is
# --- reported AMBIGUOUS-SCOPE and gets NO freeze verdict.
CASES = ["W1150_C4_L1"]
CASE = "W1150_C4_L1"

# --- FROZEN AT THE REGISTRATION.  Leg geometry.  N_B, D_EXCL and W_HALF are
# --- DERIVED, not chosen: derive_t25R6cR2.py -> DESIGN_DERIVATION.json, both in
# --- this directory and both committed with this file.
N_A = 40                 # leg A steps, deltaT 0.02, t 0 -> 0.8
N_B = 1110               # leg B steps, deltaT 0.1,  t 0.8 -> 111.8
ENDTIME_A = 0.8
ENDTIME_B = 111.8
DT_A = 0.02
DT_B = 0.1
RANKS = 2

D_EXCL = 40              # leg-B steps 1..40 DISCARDED as the restart transient
W_HALF = 535             # each graded half: steps 41..575 and 576..1110

# --- FROZEN AT THE REGISTRATION, section 3.
PLATEAU_TOL = 0.05                 # G-R2-1: 5 %, THE SAME NUMBER AS T25R6c
RHO_THRESHOLD = 1.0                # G-R2-2: the registered prediction is rho < 1
R6C_PLATEAU_WINDOW = 40            # only to REPRODUCE the R6c-form statistic

# B-R2 ceiling relief -- REPORTED, NEVER GATED, GRANTS NOTHING.
SIGMA_CAP_C4 = 24709.3             # core-min, C4's published Sigma CAP
A13_CEILING = 20000.0              # core-min, Sanaa's; NOT this team's to move
RHO_BLEND_RELIEF = A13_CEILING / SIGMA_CAP_C4     # 0.809412
LADDER_N_A = 3500
LADDER_N_B = 8300

# --- FROZEN AT THE REGISTRATION, section 6.  Cost.
POINT_CORE_MIN = 14.707            # DERIVED from T25R6c's own measured rates
CAP_PER_RUN_CORE_MIN = 45.0        # ~3x the point estimate; the team's cap
USD_PER_CORE_H = 0.0513

# --- THE REGISTERED PREDICTIONS.  All POINT values with stated bases, never
# --- inequalities (L-463).  Every one is scored on the certificate.
P_R2_1_R6C_FORM_STATISTIC = 0.10427     # will NOT fall below 5 % at any length
P_R2_2_GRADED_PLATEAU = 0.0180          # predicted graded plateau statistic
P_R2_3_RHO_POST = 1.075209              # -> predicted verdict GATE FAIL
P_R2_4_COST_CORE_MIN = 14.707
P_R2_5_SETTLED_ITERS = (92, 94)         # inclusive integer band
P_R2_6_FIELD_DIRS_AT_ENDTIME = 1
P_R2_7_PER_HALF_DRIFT_SD_PCT = 1.8016
PREDICTED_VERDICT = "GATE FAIL"

FIELDS = {"coolant": ["T", "U", "p_rgh", "alphat", "nut", "k", "omega"],
          "module": ["T"]}

TIME_RE = re.compile(r"^Time = ([\d.eE+-]+)")
EXEC_RE = re.compile(r"^ExecutionTime = ([\d.]+) s\s+ClockTime = (\d+) s")
IT_RE = re.compile(r"No Iterations (\d+)")

# ----------------------------------------------------------------------------
# THE PLANTED-ZERO CONTROL  (rule 3)
# ----------------------------------------------------------------------------
# PLANT_S is 1.23 s and is NOT arbitrary.  OpenFOAM prints ExecutionTime to TWO
# DECIMALS, so 0.01 s is the smallest perturbation this log can represent at
# all.  A 1.234e-03 plant -- the T3 constant -- would be ANNIHILATED by the print
# format and the control would "pass" by reading a zero it could never have read
# otherwise.  1.23 s is exactly representable at the log's own granularity.
PLANT_S = 1.23
# Planted at ONE step and read back AT THAT STEP.  Never a maximum, never a
# total: VERIFICATION_CHARTER 2d.11.1 found exactly that defect in the T3
# control, where a max-over-all-steps reader would report the plant even if it
# had landed somewhere else entirely.
PLANT_STEP = 7


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def git_blob(path):
    """The sha1 git would give this file's blob, computed locally.  No
    subprocess: a freeze check that shells out can be defeated by PATH."""
    data = open(path, "rb").read()
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(data))
    h.update(data)
    return h.hexdigest()


def sha256_of(path):
    """FULL sha256 of the disk bytes -- this rung's freeze witness (L-450)."""
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


# ----------------------------------------------------------------------------
# the ExecutionTime reader -- the instrument every number here comes from
# ----------------------------------------------------------------------------

def read_exec(path):
    """exec_at={step: cumulative ExecutionTime s}, clock_at={step: ClockTime s},
    iters={step: summed linear-solver iterations at that step}, times, end_lines.
    `step` is 1-based and counts `Time = ` lines.

    ExecutionTime is CUMULATIVE within one mpirun invocation and RESETS at each
    invocation, so leg A and leg B each start their own clock at ~0.  That is
    precisely why the legs are two independent samples and not one series cut in
    half."""
    if not os.path.isfile(path):
        return None
    exec_at, clock_at, iters, times = {}, {}, {}, []
    step, cur, ends = 0, 0, 0
    for ln in open(path, errors="replace"):
        m = TIME_RE.match(ln)
        if m:
            if step >= 1:
                iters[step] = cur
            step += 1
            cur = 0
            times.append(float(m.group(1)))
            continue
        if ln.startswith("End"):
            ends += 1
            continue
        m = IT_RE.search(ln)
        if m and step >= 1:
            cur += int(m.group(1))
            continue
        m = EXEC_RE.match(ln)
        if m and step >= 1:
            exec_at[step] = float(m.group(1))
            clock_at[step] = float(m.group(2))
    if step >= 1:
        iters[step] = cur
    return dict(exec_at=exec_at, clock_at=clock_at, iters=iters, times=times,
                end_lines=ends, n_steps=step)


def deltas(exec_at, n):
    """Per-step deltas d[i] = E[i] - E[i-1], with E[0] = 0."""
    out, prev = [], 0.0
    for i in range(1, n + 1):
        if i not in exec_at:
            return None
        out.append(exec_at[i] - prev)
        prev = exec_at[i]
    return out


def rate(ds):
    """Mean per-step CPU rate over a window of deltas, in cpu-seconds/step."""
    return sum(ds) / len(ds) if ds else None


def window_rate(exec_at, lo, hi):
    """Mean rate over 1-based steps [lo, hi] as a TELESCOPING difference.

    (E[hi] - E[lo-1]) / (hi - lo + 1) touches the log at exactly TWO points, so
    the 0.01 s ExecutionTime print quantum contributes at most 0.01/(hi-lo+1)
    s/step -- 0.0000187 s/step over a 535-step half, 0.005 % of the level.  The
    drift this grader measures is two orders larger and is NOT print noise."""
    e0 = exec_at[lo - 1] if lo - 1 >= 1 else 0.0
    return (exec_at[hi] - e0) / (hi - lo + 1)


def plant_into_log(src, dst):
    """Copy `src` to `dst`, adding PLANT_S to the cumulative ExecutionTime at
    PLANT_STEP AND AT EVERY STEP AFTER IT.

    Adding to the tail rather than to one line is what makes the plant land in
    EXACTLY ONE DELTA: d[PLANT_STEP] rises by PLANT_S and every other delta is
    untouched.  Adding to a single line would move TWO deltas in opposite
    directions and a reader could see the plant while pointing at the wrong
    step.  Returns the number of ExecutionTime lines rewritten."""
    step, n = 0, 0
    with open(src, errors="replace") as fh:
        lines = fh.readlines()
    for k, ln in enumerate(lines):
        if TIME_RE.match(ln):
            step += 1
            continue
        m = EXEC_RE.match(ln)
        if m and step >= PLANT_STEP:
            lines[k] = "ExecutionTime = %.2f s  ClockTime = %s s\n" % (
                float(m.group(1)) + PLANT_S, m.group(2))
            n += 1
    with open(dst, "w") as fh:
        fh.writelines(lines)
    return n


def planted_zero_control(log_path, n_steps, label):
    """RULE 3.  Plant PLANT_S into a COPY of a real log, READ IT BACK FROM DISK
    through the SAME reader that grades, and require:
      (i)  the delta at PLANT_STEP rose by exactly PLANT_S, and
      (ii) NO OTHER delta moved.
    Clause (ii) is what makes this a control on a STEP and not on a maximum.

    The tolerance is RELATIVE TO THE OPERANDS BEING DIFFERENCED -- never a bare
    absolute below the arithmetic noise floor.  ExecutionTime values here run to
    O(10^3) s; a fixed 1e-12 would be under float resolution at that magnitude
    and would fail for reasons that have nothing to do with the reader."""
    if n_steps <= PLANT_STEP:
        return dict(passed=False, label=label,
                    why="log has %d steps; PLANT_STEP %d is not inside it"
                        % (n_steps, PLANT_STEP))
    base = read_exec(log_path)
    if base is None:
        return dict(passed=False, why="no log at %s" % log_path, label=label)
    d0 = deltas(base["exec_at"], n_steps)
    if d0 is None:
        return dict(passed=False, label=label,
                    why="log is missing an ExecutionTime line inside 1..%d" % n_steps)
    tmpd = tempfile.mkdtemp(prefix="t25R6cR2_plant_")
    try:
        dst = os.path.join(tmpd, os.path.basename(log_path))
        nrw = plant_into_log(log_path, dst)
        got = read_exec(dst)                      # <-- READ BACK FROM DISK
        if got is None:
            return dict(passed=False, label=label,
                        why="the planted copy could not be read back")
        d1 = deltas(got["exec_at"], n_steps)
        if d1 is None:
            return dict(passed=False, label=label,
                        why="the planted copy lost an ExecutionTime line")

        def tol(i):
            return 1e-6 * max(abs(base["exec_at"].get(i, 0.0)),
                              abs(base["exec_at"].get(i - 1, 0.0)), PLANT_S)
        seen = d1[PLANT_STEP - 1] - d0[PLANT_STEP - 1]
        at_step_ok = abs(seen - PLANT_S) <= tol(PLANT_STEP)
        moved = [i + 1 for i in range(n_steps)
                 if i + 1 != PLANT_STEP and abs(d1[i] - d0[i]) > tol(i + 1)]
        return dict(passed=bool(at_step_ok and not moved), label=label,
                    plant_s=PLANT_S, plant_step=PLANT_STEP,
                    read_back_delta_change=seen, lines_rewritten=nrw,
                    other_deltas_that_moved=moved[:8],
                    tolerance_at_plant_step=tol(PLANT_STEP),
                    tolerance_basis="1e-6 x max(|E[i]|, |E[i-1]|, PLANT_S) -- "
                                    "relative to the operands differenced, never "
                                    "a bare absolute")
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)


# ----------------------------------------------------------------------------
# THE TRANSIENT.  Located by SOLVER WORK, so the box cannot choose the boundary.
# ----------------------------------------------------------------------------

def transient_end(iters, n):
    """First leg-B step from which the per-step linear-solver iteration count
    NEVER AGAIN leaves the settled band, band = median +/- max(1, 3 x MAD) over
    the LAST HALF of the leg.

    WHY WORK AND NOT COST.  The graded statistic is a COST statistic and cost on
    a shared box carries the box in it.  Iteration count does not: it is what
    the solver did, and it is identical whether the machine was busy or idle.
    Locating the boundary by work gives a boundary a contended re-run finds in
    the same place.  Locating it by cost would let the box choose it.

    WHY ROBUST AND NOT [min, max].  The tail's extremes let a SINGLE outlier
    inside the tail widen the band until it contains itself, and the locator
    then reports `settled` over a region the work plainly leaves.  The selftest
    plants exactly that excursion and requires the boundary to move.  The floor
    of 1 is not a tuning knob: iteration counts are INTEGERS, so a half-width
    below 1 would read an ordinary +/-1 fluctuation as a transient."""
    vals = [iters[k] for k in range(1, n + 1)]
    tail = vals[n // 2:]
    med = statistics.median(tail)
    mad = statistics.median([abs(x - med) for x in tail])
    hw = max(1.0, 3.0 * mad)
    lo, hi = med - hw, med + hw
    s = n
    while s > 1 and lo <= vals[s - 2] <= hi:
        s -= 1
    return s, (lo, hi)


# ----------------------------------------------------------------------------
# rule 4 -- ALL conjuncts, BOTH legs, AGE GUARD vs 0/module/T
# ----------------------------------------------------------------------------

def _num(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def rule4(case_dir, case, lga, lgb):
    """Returns (ok, [failures]).  The case name is an ARGUMENT, never hardcoded:
    grade_t25R5.py hardcoded '_L2' in an rc filename and compared two different
    meshes (T25R5 D3.3)."""
    bad = []

    for leg, log, n, et in (("legA", lga, N_A, ENDTIME_A),
                            ("legB", lgb, N_B, ENDTIME_B)):
        rcf = os.path.join(case_dir, ".rc.%s.%s" % (case, leg))
        if not os.path.isfile(rcf):
            bad.append("%s: rc file absent (%s)" % (leg, os.path.basename(rcf)))
        else:
            rc = open(rcf).read().strip()
            if rc != "0":
                bad.append("%s: rc != 0 (%s)%s"
                           % (leg, rc, "  [124 = CAP STOP]" if rc == "124" else ""))
        if log is None:
            bad.append("%s: no log" % leg)
            continue
        if log["end_lines"] < 1:
            bad.append("%s: no End line" % leg)
        # CLAUSE 5 IS A STEP-COUNT IDENTITY, NOT A TIME-VALUE IDENTITY.  At
        # deltaT 0.02, endTime 0.8 is 40 counts; reading CLAUDE.md rule 4's
        # shorthand "ExecutionTime count == endTime" LITERALLY would fail every
        # case with deltaT != 1 and is UNSATISFIABLE AS WRITTEN.  The step-count
        # reading is the correct one and is carried forward from
        # grade_t25R6c.py:335-337 UNCHANGED -- deliberately unchanged, because a
        # successor silently choosing a THIRD reading is the failure mode being
        # reported.  THE CLAUSE'S WORDING IS DOCKETED AS D588 (docs/DOCKET.md,
        # commit 4c6bc6aa), owner verification.  This grader does not amend
        # CLAUDE.md and no lane may (rule 9).
        if len(log["exec_at"]) != n:
            bad.append("%s: ExecutionTime count %d != registered step count %d"
                       % (leg, len(log["exec_at"]), n))
        if log["n_steps"] != n:
            bad.append("%s: Time lines %d != registered step count %d"
                       % (leg, log["n_steps"], n))
        # clause 3: LAST TIME == endTime
        if log["times"] and abs(log["times"][-1] - et) > 1e-6:
            bad.append("%s: last Time %g != endTime %g" % (leg, log["times"][-1], et))

    p0 = os.path.join(case_dir, "processor0")
    if not os.path.isdir(p0):
        bad.append("no processor0/")
        return (not bad), bad
    tdirs = [d for d in os.listdir(p0) if _num(d) and abs(float(d) - ENDTIME_B) <= 1e-6]
    if len(tdirs) != 1:
        # P-R2-6 SCORED HERE.  T25R6c died on exactly this conjunct: its
        # `writeControl timeStep` counted on the GLOBAL time index, which does
        # NOT reset across a `startFrom latestTime` restart, so writeInterval 400
        # fired at global index 400 = leg-B step 360 and nothing wrote at the
        # registered endTime.  R2 uses `writeControl runTime`, whose index is
        # relative to startTime_ and therefore independent of leg A entirely.
        bad.append("t=%g field dir: %d found  [P-R2-6 predicted exactly 1]"
                   % (ENDTIME_B, len(tdirs)))
        return (not bad), bad

    procs = sorted(glob.glob(os.path.join(case_dir, "processor*")))
    # clause 4: fields present, per region, in every processor dir
    for region, names in FIELDS.items():
        for nm in names:
            hits = [p for p in procs
                    if os.path.isfile(os.path.join(p, tdirs[0], region, nm))]
            if len(hits) != len(procs):
                bad.append("field %s/%s present in %d of %d processor dirs"
                           % (region, nm, len(hits), len(procs)))

    # clause 6: THE AGE GUARD.  THE REGION IS `module` AND THE DATING FILE IS
    # `0/module/T`, NOT `0/T`.  A comparator asserting `0/T` on this family would
    # assert A FILE THAT DOES NOT EXIST: the guard would never evaluate and would
    # never say so.  Its EXISTENCE is checked before it is used as a datum.
    ref = os.path.join(case_dir, "0", "module", "T")
    if not os.path.isfile(ref):
        bad.append("no 0/module/T to date the run against -- AGE GUARD UNEVALUABLE")
    else:
        t0 = os.path.getmtime(ref)
        old = [f for f in glob.glob(os.path.join(case_dir, "processor*",
                                                 tdirs[0], "*", "*"))
               if os.path.isfile(f) and os.path.getmtime(f) <= t0]
        if old:
            bad.append("AGE GUARD: %d field(s) NOT newer than 0/module/T" % len(old))

    return (not bad), bad


# ----------------------------------------------------------------------------
# grade
# ----------------------------------------------------------------------------

def grade(root=None):
    root = root or HERE
    case_dir = os.path.join(root, CASE)
    print("T25R6c-R2 -- G-R2-1 (PLATEAU) and G-R2-2 (DIRECTION)")
    print("=" * 74)

    me = os.path.abspath(__file__)
    out = dict(rung="T25R6c-R2", case=CASE,
               registration="docs/campaigns/T-family/T25R6cR2_PREREGISTRATION.md",
               grader_sha256=sha256_of(me), grader_git_blob=git_blob(me),
               predicted_verdict=PREDICTED_VERDICT,
               roache="NOT INVOKED -- no grid family, no functional at "
                      "convergence, no order and no GCI is computed or derivable "
                      "(rule 5 does not apply to a wall-cost measurement inside "
                      "one transient)",
               cost_basis=("REPORTED-BY-OWNER; dollars DERIVED at $%.4f/core-h, "
                           "NOT MEASURED -- this box cannot read its own billing "
                           "(COMPUTE_BUDGET_CHARTER section 5)" % USD_PER_CORE_H))

    if not os.path.isdir(case_dir):
        refuse("%s absent -- there is nothing to grade, and a verdict without a "
               "run is not a verdict." % case_dir)

    lga = read_exec(os.path.join(case_dir, "log.solve.legA"))
    lgb = read_exec(os.path.join(case_dir, "log.solve.legB"))
    if lga is None:
        refuse("no log.solve.legA in %s" % case_dir)
    if lgb is None:
        refuse("no log.solve.legB in %s" % case_dir)

    print("\n[1] PLANTED-ZERO CONTROL ON THE ExecutionTime READER, BOTH LEGS (rule 3)")
    pz = {}
    for label, path, n in (("legA", os.path.join(case_dir, "log.solve.legA"), N_A),
                           ("legB", os.path.join(case_dir, "log.solve.legB"), N_B)):
        r = planted_zero_control(path, n, label)
        pz[label] = r
        if not r.get("passed"):
            refuse("PLANTED-ZERO CONTROL FAILED on %s: %s.  The reader cannot be "
                   "shown to see a known %.2f s change at step %d, so any rate it "
                   "reports -- and any zero -- is not evidence."
                   % (label, r.get("why", "the plant was not read back at its step"),
                      PLANT_S, PLANT_STEP))
        print("  ok   %s: %.2f s planted at step %d, read back from disk as a "
              "%.6f s change IN THAT DELTA and in no other (%d other deltas moved)"
              % (label, PLANT_S, PLANT_STEP, r["read_back_delta_change"],
                 len(r["other_deltas_that_moved"])))
    out["planted_zero"] = pz

    print("\n[2] RULE 4 COMPLETION, ALL CONJUNCTS, AGE GUARD vs 0/module/T")
    ok, bad = rule4(case_dir, CASE, lga, lgb)
    out["rule4"] = bad
    print("  %-14s %s" % (CASE, "COMPLETE" if ok else "; ".join(bad)))
    if not ok:
        out["verdict"] = "NOT A RESULT"
        out["ground"] = "rule 4 incomplete: " + "; ".join(bad)
        return finish(out, EXIT_NOT_A_RESULT, root)

    dA = deltas(lga["exec_at"], N_A)
    dB = deltas(lgb["exec_at"], N_B)
    if dA is None or dB is None:
        refuse("an ExecutionTime line is missing inside the registered step "
               "range; the rate would be computed over a window that is not the "
               "registered window.")
    rA = rate(dA)

    print("\n[3] C-R2-1 TRANSIENT CONTROL -- THE RUN'S OWN TRANSIENT, BY SOLVER WORK")
    t_end, band = transient_end(lgb["iters"], N_B)
    tail_it = [lgb["iters"][k] for k in range(D_EXCL + 1, N_B + 1)]
    out["transient"] = dict(
        measured_first_settled_step=t_end, settled_band=list(band),
        registered_D_EXCL=D_EXCL,
        settled_iterations_min=min(tail_it), settled_iterations_max=max(tail_it),
        settled_iterations_mean=sum(tail_it) / len(tail_it),
        P_R2_5_predicted_band=list(P_R2_5_SETTLED_ITERS),
        P_R2_5_verdict=("WINS" if P_R2_5_SETTLED_ITERS[0] <= min(tail_it)
                        and max(tail_it) <= P_R2_5_SETTLED_ITERS[1] else "LOSES"),
        located_by="linear-solver iteration count, NOT cost -- so the box cannot "
                   "choose the boundary")
    print("     the run's own transient ends at leg-B step %d; registered "
          "exclusion is %d" % (t_end, D_EXCL))
    print("     settled work %d..%d iterations/step over the graded %d steps "
          "(P-R2-5 predicted %d..%d: %s)"
          % (min(tail_it), max(tail_it), len(tail_it), P_R2_5_SETTLED_ITERS[0],
             P_R2_5_SETTLED_ITERS[1], out["transient"]["P_R2_5_verdict"]))
    if t_end > D_EXCL:
        out["verdict"] = "NOT A RESULT"
        out["ground"] = ("C-R2-1: the run's own restart transient ends at leg-B "
                         "step %d, AFTER the registered exclusion of %d.  The "
                         "graded window would contain transient steps, and a "
                         "plateau statistic computed over a window that still "
                         "holds the transient is the T25R6c defect repeated."
                         % (t_end, D_EXCL))
        print("\n  C-R2-1: NOT A RESULT -- the graded window would contain transient.")
        return finish(out, EXIT_NOT_A_RESULT, root)

    print("\n[4] G-R2-1 PLATEAU -- EVALUATED FIRST, BEFORE rho IS CONSULTED")
    lo1, hi1 = D_EXCL + 1, D_EXCL + W_HALF
    lo2, hi2 = D_EXCL + W_HALF + 1, N_B
    r1 = window_rate(lgb["exec_at"], lo1, hi1)
    r2 = window_rate(lgb["exec_at"], lo2, hi2)
    # BOTH NORMALISERS ARE COMPUTED AND THE LARGER IS GRADED.  Registered in
    # advance so that nobody later "tightens" the normaliser and mistakes a
    # harder gate for a moved verdict.  NOT a D389 instance: D389 is about
    # normalising an ABSOLUTE TEMPERATURE by its mean, where the zero is
    # arbitrary; a rate in s/step has a meaningful zero.  D389 STAYS OPEN.
    s_by_second = abs(r2 - r1) / r2
    s_by_first = abs(r2 - r1) / r1
    plateau = max(s_by_second, s_by_first)
    out["plateau"] = dict(
        first_half=dict(steps=[lo1, hi1], r=r1),
        second_half=dict(steps=[lo2, hi2], r=r2),
        statistic_normalised_by_second_half=s_by_second,
        statistic_normalised_by_first_half=s_by_first,
        graded_statistic=plateau, graded_normaliser=("first_half"
                                                     if s_by_first >= s_by_second
                                                     else "second_half"),
        threshold=PLATEAU_TOL, passed=bool(plateau <= PLATEAU_TOL),
        P_R2_2_predicted=P_R2_2_GRADED_PLATEAU,
        both_normalisers_registered="T25R6c divided by `last` only.  With a rising "
            "rate that is the SMALLER statistic -- T25R6c's 13.939 % is 16.197 % "
            "under the other normaliser, so ITS GATE FAILED UNDER THE LOOSER OF "
            "THE TWO and would only harden under the stricter.  R2 removes the "
            "choice by grading the larger.",
        not_a_D389_instance="D389 concerns normalising an ABSOLUTE TEMPERATURE by "
            "its mean, where the zero is arbitrary.  A rate in s/step has a "
            "meaningful zero, so endpoint normalisation is legitimate here.  "
            "D389 IS OPEN AND IS NOT SETTLED BY THIS RUNG.")
    print("     r(steps %d..%d) = %.6f s/step" % (lo1, hi1, r1))
    print("     r(steps %d..%d) = %.6f s/step" % (lo2, hi2, r2))
    print("     |d|/second = %.4f %% ; |d|/first = %.4f %% ; GRADED %.4f %%   "
          "threshold %.1f %%" % (s_by_second * 100.0, s_by_first * 100.0,
                                 plateau * 100.0, PLATEAU_TOL * 100.0))

    # ---- R-R2-1: what the T25R6c-FORM statistic does here.  REPORTED. -------
    f40 = window_rate(lgb["exec_at"], 1, R6C_PLATEAU_WINDOW)
    l40 = window_rate(lgb["exec_at"], N_B - R6C_PLATEAU_WINDOW + 1, N_B)
    s_r6c = abs(l40 - f40) / l40
    out["R_R2_1_the_R6c_form_statistic_reported_gating_nothing"] = dict(
        first40=f40, last40=l40, statistic=s_r6c, threshold=PLATEAU_TOL,
        would_have_passed=bool(s_r6c <= PLATEAU_TOL),
        P_R2_1_predicted=P_R2_1_R6C_FORM_STATISTIC,
        P_R2_1_verdict=("WINS" if s_r6c > PLATEAU_TOL else "LOSES"),
        why="REGISTERED PREDICTION P-R2-1: this statistic will NOT fall below 5 % "
            "at ANY leg-B length, because its `first` window is anchored on the "
            "restart transient (measured 10.43 % cheaper than settled in T25R6c) "
            "while its `last` window is drawn from the settled distribution.  It "
            "asymptotes to ~10.4 %, not to zero.  REPORTED HERE, GATING NOTHING: "
            "it is the predecessor's instrument, scored.")
    print("     R-R2-1 (REPORTED): the T25R6c-FORM statistic here is %.4f %% "
          "(P-R2-1 predicted %.3f %%, > 5 %%: %s)"
          % (s_r6c * 100.0, P_R2_1_R6C_FORM_STATISTIC * 100.0,
             out["R_R2_1_the_R6c_form_statistic_reported_gating_nothing"]["P_R2_1_verdict"]))

    # ---- R-R2-2: the windowed trajectory.  REPORTED. ------------------------
    traj = []
    s = 1
    while s + R6C_PLATEAU_WINDOW - 1 <= N_B:
        e = s + R6C_PLATEAU_WINDOW - 1
        traj.append(dict(leg="B", steps=[s, e], r=window_rate(lgb["exec_at"], s, e),
                         rho_window=window_rate(lgb["exec_at"], s, e) / rA,
                         iters=sum(lgb["iters"][k] for k in range(s, e + 1))
                         / R6C_PLATEAU_WINDOW))
        s += R6C_PLATEAU_WINDOW
    out["R_R2_2_trajectory_reported_gating_nothing"] = (
        [dict(leg="A", steps=[1, N_A], r=rA, rho_window=1.0,
              iters=sum(lga["iters"][k] for k in range(1, N_A + 1)) / N_A)] + traj)
    print("     R-R2-2 (REPORTED): %d leg-B windows of %d steps, rho per window "
          "%.4f .. %.4f" % (len(traj), R6C_PLATEAU_WINDOW,
                            min(t["rho_window"] for t in traj),
                            max(t["rho_window"] for t in traj)))

    # ---- R-R2-3: THE DRIFT FLOOR, MEASURED.  Scores P-R2-7.  REPORTED. ------
    floor = []
    for W in (40, 90, 180, 267, W_HALF):
        rs, ss = [], D_EXCL + 1
        while ss + W - 1 <= N_B:
            rs.append(window_rate(lgb["exec_at"], ss, ss + W - 1))
            ss += W
        if len(rs) >= 3:
            m = statistics.mean(rs)
            floor.append(dict(W=W, n=len(rs), mean=m,
                              sd_pct=statistics.stdev(rs) / m * 100.0))
        else:
            floor.append(dict(W=W, n=len(rs), note="fewer than 3 windows; no sd"))
    it_tail_spread = (max(tail_it) - min(tail_it)) / (sum(tail_it) / len(tail_it)) * 100.0
    sd40 = next((f["sd_pct"] for f in floor if f["W"] == 40 and "sd_pct" in f), None)
    out["R_R2_3_drift_floor_reported_gating_nothing"] = dict(
        scaling=floor, P_R2_7_predicted_per_half_sd_pct=P_R2_7_PER_HALF_DRIFT_SD_PCT,
        settled_work_spread_pct=it_tail_spread,
        what_it_says="Over the graded steps the solver does CONSTANT WORK (%.3f %% "
                     "integer spread in iterations/step) while the cost scatters "
                     "by %s.  Identical work, different cost: THAT IS THE MACHINE, "
                     "and cpu-time accounting does not remove it.  It is the floor "
                     "under any rate this rung reports."
                     % (it_tail_spread,
                        ("%.3f %% on a 40-step window" % sd40) if sd40 is not None
                        else "the windows tabulated above"),
        registered_in_advance="The R2 registration states BEFORE the run that a rho "
                              "finer than about +/-3 % is not achievable on this "
                              "shared box.  This row measures whether that held.")
    print("     R-R2-3 (REPORTED): settled work spread %.3f %%; drift floor "
          "tabulated at W = 40, 90, 180, 267, %d" % (it_tail_spread, W_HALF))

    if plateau > PLATEAU_TOL:
        out["verdict"] = "NOT A RESULT"
        out["rho_measured_but_not_graded"] = window_rate(
            lgb["exec_at"], D_EXCL + 1, N_B) / rA
        out["ground"] = ("G-R2-1 PLATEAU FAILED: the post-transient leg-B rate "
                         "moved %.4f %% between its two %d-step halves, above the "
                         "registered %.1f %%.  A leg-B rate still moving cannot "
                         "bound the rate at step 11,800, and a bound quoted off a "
                         "moving rate is a false bound.  rho is printed beside "
                         "this verdict and IS NOT A RESULT."
                         % (plateau * 100.0, W_HALF, PLATEAU_TOL * 100.0))
        print("\n  G-R2: NOT A RESULT -- the plateau clause refused before rho "
              "was read.")
        return finish(out, EXIT_NOT_A_RESULT, root)

    print("\n[5] G-R2-2 DIRECTION")
    rB_post = window_rate(lgb["exec_at"], D_EXCL + 1, N_B)
    rB_all = rate(dB)
    rho = rB_post / rA
    it_A = sum(lga["iters"][k] for k in range(1, N_A + 1)) / N_A
    it_B = sum(tail_it) / len(tail_it)
    out["r_legA_s_per_step"] = rA
    out["r_legB_post_transient_s_per_step"] = rB_post
    out["r_legB_all_steps_s_per_step"] = rB_all
    out["rho"] = rho
    out["rho_all_steps_reported_for_comparability_with_T25R6c"] = rB_all / rA
    out["R_R2_4_work_vs_throughput_reported_gating_nothing"] = dict(
        rho_work=it_B / it_A, rho_throughput=rho / (it_B / it_A),
        iters_legA=it_A, iters_legB_settled=it_B,
        note="rho = rho_work x rho_throughput.  rho_work is CONTENTION-FREE -- "
             "iteration counts do not depend on how busy the box is -- and "
             "rho_throughput is what is left, which is the machine.  REPORTED, "
             "GATING NOTHING: a new instrument, and Sanaa's 2026-09-03 20:00Z "
             "default is reported-not-gated.  A raw iteration SUM mixes cheap "
             "DILUPBiCGStab sweeps with expensive GAMGPCG ones and the two legs "
             "need not share that mixture, so rho_work is NOT offered as a "
             "corrected rho and no verdict rests on it.")
    print("     r(leg A)              = %.6f s/step over %d steps at deltaT %.2f"
          % (rA, N_A, DT_A))
    print("     r(leg B post-transient) = %.6f s/step over %d steps at deltaT %.2f"
          % (rB_post, N_B - D_EXCL, DT_B))
    print("     rho = %.6f      registered prediction: rho < %.1f  (P-R2-3 "
          "predicted %.6f)" % (rho, RHO_THRESHOLD, P_R2_3_RHO_POST))
    print("     R-R2-4 (REPORTED): rho_work = %.6f, rho_throughput = %.6f"
          % (it_B / it_A, rho / (it_B / it_A)))
    print("     rho over ALL leg-B steps (comparable to T25R6c's 1.063997) = %.6f"
          % (rB_all / rA))

    print("\n[6] B-R2 CEILING RELIEF -- REPORTED, NEVER GATED")
    blend_ladder = (LADDER_N_A + LADDER_N_B * rho) / (LADDER_N_A + LADDER_N_B)
    blend_probe = (N_A + (N_B - D_EXCL) * rho) / (N_A + N_B - D_EXCL)
    out["B_R2_reported_never_gated"] = dict(
        rho_blend_ladder=blend_ladder, rho_blend_probe=blend_probe,
        relief_threshold=RHO_BLEND_RELIEF,
        sigma_cap_c4_x_blend_ladder=SIGMA_CAP_C4 * blend_ladder,
        a13_ceiling=A13_CEILING,
        ambiguity="THE THRESHOLD 0.809412 IS FIXED ON rho_blend AND rho_blend'S "
                  "MIXTURE IS NOT DEFINED BY THE REGISTRATION.  Both readings are "
                  "reported; neither gates; this lane resolves nothing.  The "
                  "ladder mixture (3500 leg-A + 8300 leg-B steps) is the one a "
                  "ceiling statement would need.",
        not_a_relief_grant="THIS ROW GRANTS NOTHING.  The A1.3 ceiling of 20,000 "
                           "core-min is not this team's to move, this rung "
                           "pre-registers no widening, and a rho >= 1 moves the "
                           "ceiling question in the UNSAFE direction, not the "
                           "safe one.")
    print("     rho_blend (ladder 3500A + 8300B) = %.6f -> Sigma CAP(C4) x blend "
          "= %.1f core-min vs ceiling %.0f"
          % (blend_ladder, SIGMA_CAP_C4 * blend_ladder, A13_CEILING))
    print("     relief threshold %.6f.  REPORTED, NEVER GATED, GRANTS NO WIDENING."
          % RHO_BLEND_RELIEF)

    print("\n[7] PREDICTED-VS-ACTUAL (rule 12) -- REPORTED, GATING NOTHING")
    total_cpu_s = lga["exec_at"][N_A] + lgb["exec_at"][N_B]
    total_core_min = total_cpu_s * RANKS / 60.0
    ratio = total_core_min / POINT_CORE_MIN
    out["predicted_vs_actual"] = dict(
        point_core_min=POINT_CORE_MIN, actual_core_min=total_core_min,
        ratio_actual_over_predicted=ratio,
        P_R2_4_verdict=("WINS" if abs(ratio - 1.0) <= 0.5 else "LOSES"),
        cap_core_min=CAP_PER_RUN_CORE_MIN,
        cap_breached=bool(total_core_min > CAP_PER_RUN_CORE_MIN),
        usd_derived_not_measured=round(total_core_min / 60.0 * USD_PER_CORE_H, 6),
        core_min_basis="ExecutionTime (CPU s, rank 0) x %d ranks / 60.  THE RANK "
                       "MULTIPLIER IS AN ASSUMPTION: ExecutionTime cannot see "
                       "rank 1.  T25R6c used the same basis and R2 keeps it "
                       "UNCHANGED so the two rungs stay comparable." % RANKS,
        attribution="The point estimate is derived from T25R6c's OWN measured "
                    "per-step rates on the SAME case, arm, mesh, ranks and box, "
                    "so a miss is contention or waste, NOT arm misprediction -- "
                    "which is what T25R6c's P-C1 was.  Contention and waste stay "
                    "separately named (COMPUTE_BUDGET_CHARTER section 6).",
        calibration_row_owed="docs/COST_CALIBRATION.md -- owed at completion "
                             "under rule 12; NOT discharged by this verdict.")
    print("     actual %.4f core-min vs point %.3f  ->  ratio %.4f  (P-R2-4 %s)"
          % (total_core_min, POINT_CORE_MIN, ratio,
             out["predicted_vs_actual"]["P_R2_4_verdict"]))

    if rho < RHO_THRESHOLD:
        out["verdict"] = "PASS"
        out["ground"] = ("G-R2-2: rho = %.6f < %.1f.  The registered direction "
                         "HOLDS: post-transient leg-B steps are cheaper, and the "
                         "C4/C5 wall factors measured on the ramp window are "
                         "conservative in the SAFE direction." % (rho, RHO_THRESHOLD))
        rc = EXIT_PASS
        print("\n  G-R2: PASS -- rho = %.6f < %.1f." % (rho, RHO_THRESHOLD))
    else:
        out["verdict"] = "GATE FAIL"
        out["ground"] = ("G-R2-2: rho = %.6f >= %.1f.  A1.2's REGISTERED "
                         "DIRECTION IS FALSIFIED: post-transient leg-B steps are "
                         "NOT cheaper, so every CAP in the C4/C5 line priced off "
                         "the 40-step ramp window is conservative in the UNSAFE "
                         "direction rather than the safe one." % (rho, RHO_THRESHOLD))
        rc = EXIT_GATE_FAIL
        print("\n  G-R2: GATE FAIL -- rho = %.6f >= %.1f.  A1.2's DIRECTION IS "
              "FALSIFIED." % (rho, RHO_THRESHOLD))
    out["P_R2_3_verdict"] = ("WINS" if (rho >= RHO_THRESHOLD) ==
                             (P_R2_3_RHO_POST >= RHO_THRESHOLD) else "LOSES")
    out["predicted_verdict_matched"] = bool(out["verdict"] == PREDICTED_VERDICT)

    print("\n  ROACHE (rule 5) -- NOT INVOKED, AND THAT IS A REGISTERED DECISION.")
    print("  There is no grid family here and no functional at convergence: this is")
    print("  a WALL-COST measurement inside one transient at one mesh.  NO observed")
    print("  order and NO GCI is computed, quoted or derivable.  A successor")
    print("  reading a grid-convergence claim off these numbers gets NOT A RESULT.")
    return finish(out, rc, root)


def finish(out, rc, root, name="T25R6cR2_VERDICT.json"):
    out["exit"] = rc
    out["ExecutionTime_is_cpu_time_not_wall_time"] = (
        "ESTABLISHED FROM THIS BUILD'S SOURCE, not assumed from convention: "
        "OpenFOAM-v2606 TimeIO.C:631 prints elapsedCpuTime(); cpuTimeFwd.H "
        "typedefs cpuTime = cpuTimePosix; cpuTimePosix.C:40-47 computes "
        "((tms_utime + tms_stime) difference) / sysconf(_SC_CLK_TCK) via "
        "::times().  times(2) reports the CALLING PROCESS ONLY, so this is "
        "rank 0's user+system CPU -- not wall, not a sum over ranks.")
    out["what_this_does_not_do"] = [
        "IT AUTHORISES NO LADDER LAUNCH.  T25R5 5.1 is carried IN FORCE: no "
        "ladder launches on this result, whatever it says.",
        "IT DOES NOT MEASURE THE SOAK RATE AT STEP 11,800.  It samples "
        "t <= 111.8 s of a soak that runs to t = 900 s -- 12.4 %, against "
        "T25R6c's 4.4 %.  The plateau clause is what licenses reading rho beyond "
        "the sampled steps, and that is a weaker claim, registered as the weaker "
        "claim.",
        "IT DOES NOT RE-OPEN, WIDEN OR RETIRE THE A1.3 CEILING OF 20,000 "
        "CORE-MIN, which is not this team's to move.",
        "IT CONSUMES NO OUTPUT OF T25R6a OR T25R6c.  It reads only ExecutionTime "
        "and iteration counts from logs it produced itself.  T25R6c's rho = "
        "1.063997 REMAINS A DIAGNOSTIC AND MAY NOT BE QUOTED AS A VERDICT -- "
        "that prohibition stands and this rung does not lift it.",
        "IT SETTLES NOTHING ABOUT D389, which is open, and nothing about the "
        "CLAUDE.md rule 4 clause wording, which is docketed and is not this "
        "team's to amend.",
    ]
    out["legs_are_independent_because"] = (
        "r(leg A) and r(leg B) are means over DISJOINT delta sets parsed from TWO "
        "SEPARATE log files written by TWO SEPARATE mpirun invocations.  Neither "
        "is computed from the other and no term appears in both but ranks and 60, "
        "which cancel.  WHAT WOULD BREAK IT: (a) a change in the shared box's "
        "per-core throughput between the two windows -- MEASURED for the first "
        "time in this rung as R-R2-3, at constant solver work, and registered in "
        "advance as an irreducible ~3 %% floor; (b) leg B's restart coupling to "
        "leg A's output, which C-R2-1 and G-R2-1 exist to catch and which R2 "
        "additionally EXCLUDES by discarding the first %d leg-B steps; (c) the "
        "single shared parser, whose defects cancel in the ratio only if "
        "multiplicative and identical across legs -- hence the planted-zero "
        "control in BOTH legs." % D_EXCL)
    p = os.path.join(root, name)
    json.dump(out, open(p, "w"), indent=2, sort_keys=True, default=str)
    print("\n  written %s" % p)
    print("  VERDICT: %s   (predicted %s)"
          % (out.get("verdict", "(none -- refused)"), PREDICTED_VERDICT))
    return rc


# ----------------------------------------------------------------------------
# selftest -- planted controls on this comparator's OWN arithmetic
# ----------------------------------------------------------------------------

def _synth_log(path, n, base_rate, first_extra=0.0, drift=0.0, dt=1.0,
               iters=93, transient_iters=None, transient_n=0):
    """A synthetic OpenFOAM-shaped log with a known per-step rate and a known
    per-step iteration count."""
    e = 0.0
    with open(path, "w") as fh:
        for i in range(1, n + 1):
            fh.write("Time = %g\n\n" % (i * dt))
            it = transient_iters if (transient_iters is not None
                                     and i <= transient_n) else iters
            fh.write("DILUPBiCGStab:  Solving for Ux, Initial residual = 1e-9, "
                     "Final residual = 1e-11, No Iterations %d\n" % it)
            d = base_rate + (first_extra if i == 1 else 0.0) + drift * (i - 1)
            e += d
            fh.write("ExecutionTime = %.2f s  ClockTime = %d s\n\n" % (e, int(e)))
        fh.write("End\n")


def selftest():
    fails = [0]

    def chk(what, ok):
        print("  %-70s %s" % (what[:70], "ok" if ok else "FAIL"))
        if not ok:
            fails[0] += 1

    print("T25R6c-R2 COMPARATOR SELFTEST")
    print("-" * 78)

    tmpd = tempfile.mkdtemp(prefix="t25R6cR2_selftest_")
    try:
        # ---- the reader reads what was written ------------------------------
        p = os.path.join(tmpd, "log.synth")
        _synth_log(p, 40, 0.50)
        r = read_exec(p)
        chk("the reader finds 40 ExecutionTime lines and 40 Time lines",
            len(r["exec_at"]) == 40 and r["n_steps"] == 40)
        chk("the reader attributes iterations to the step they belong to",
            all(r["iters"][k] == 93 for k in range(1, 41)))
        d = deltas(r["exec_at"], 40)
        chk("a 0.50 s/step synthetic log reads back at 0.50 s/step",
            abs(rate(d) - 0.50) < 1e-9)
        chk("window_rate is a telescoping difference and agrees with the mean",
            abs(window_rate(r["exec_at"], 11, 30) - 0.50) < 1e-9)

        # ---- THE PLANTED-ZERO CONTROL MUST FIRE, AND AT THE STEP ------------
        pz = planted_zero_control(p, 40, "synth")
        chk("the planted %.2f s is read back FROM DISK at step %d"
            % (PLANT_S, PLANT_STEP),
            pz["passed"] and abs(pz["read_back_delta_change"] - PLANT_S) < 1e-6)
        chk("...and NO OTHER delta moved (a control on a STEP, not a maximum)",
            pz["other_deltas_that_moved"] == [])

        # PLANTED VIOLATION 1: a reader returning a CONSTANT cannot see the plant.
        real_read = globals()["read_exec"]

        def blind_read(path):
            got = real_read(path)
            if got is None:
                return None
            got["exec_at"] = {k: 0.5 * k for k in got["exec_at"]}
            return got
        globals()["read_exec"] = blind_read
        pzb = planted_zero_control(p, 40, "blind")
        globals()["read_exec"] = real_read
        chk("A BLIND READER (constant rate) FAILS the planted-zero control",
            not pzb["passed"])

        # PLANTED VIOLATION 2: a SMEARED plant must not read back at the step.
        p2 = os.path.join(tmpd, "log.smear")
        _synth_log(p2, 40, 0.50)
        dst = os.path.join(tmpd, "log.smear.planted")
        with open(p2, errors="replace") as fh:
            lines = fh.readlines()
        acc = 0.0
        for k, ln in enumerate(lines):
            m = EXEC_RE.match(ln)
            if m:
                acc += PLANT_S / 40.0
                lines[k] = "ExecutionTime = %.4f s  ClockTime = %s s\n" % (
                    float(m.group(1)) + acc, m.group(2))
        open(dst, "w").writelines(lines)
        b = deltas(read_exec(p2)["exec_at"], 40)
        sm = deltas(read_exec(dst)["exec_at"], 40)
        chk("A SMEARED plant does NOT read back as PLANT_S at the planted step "
            "(a max-over-steps control would have passed it)",
            abs((sm[PLANT_STEP - 1] - b[PLANT_STEP - 1]) - PLANT_S) > 0.5)

        # ---- THE HALF-SPLIT PLATEAU CLAUSE ---------------------------------
        pflat = os.path.join(tmpd, "log.flat")
        _synth_log(pflat, 1110, 0.50)
        ef = read_exec(pflat)["exec_at"]
        f1 = window_rate(ef, D_EXCL + 1, D_EXCL + W_HALF)
        f2 = window_rate(ef, D_EXCL + W_HALF + 1, N_B)
        chk("a FLAT leg B passes the 5 % half-split plateau clause",
            max(abs(f2 - f1) / f2, abs(f2 - f1) / f1) <= PLATEAU_TOL)
        pdr = os.path.join(tmpd, "log.drift")
        _synth_log(pdr, 1110, 0.50, drift=0.0002)
        ed = read_exec(pdr)["exec_at"]
        g1 = window_rate(ed, D_EXCL + 1, D_EXCL + W_HALF)
        g2 = window_rate(ed, D_EXCL + W_HALF + 1, N_B)
        sd_ = max(abs(g2 - g1) / g2, abs(g2 - g1) / g1)
        chk("a DRIFTING leg B (+0.0002 s/step) FAILS the 5 % half-split clause",
            sd_ > PLATEAU_TOL)
        chk("A MUTATION FLIPS THE ANSWER: flat passes and drifting fails on the "
            "SAME threshold",
            max(abs(f2 - f1) / f2, abs(f2 - f1) / f1) <= PLATEAU_TOL < sd_)

        # ---- THE R6c FORM MUST BE UNREACHABLE ON A SETTLED SERIES WITH A
        # ---- CHEAP TRANSIENT.  This is prediction P-R2-1, demonstrated.
        pt = os.path.join(tmpd, "log.transient")
        _synth_log(pt, 1110, 0.386, transient_n=0)
        et = read_exec(pt)["exec_at"]
        # rewrite the first 40 steps 10.43 % cheaper, as T25R6c measured
        cheap = os.path.join(tmpd, "log.cheap")
        _synth_log(cheap, 40, 0.34575)
        e_cheap = read_exec(cheap)["exec_at"]
        merged = dict(e_cheap)
        base = e_cheap[40]
        for k in range(41, 1111):
            merged[k] = base + 0.386 * (k - 40)
        r6c_first = window_rate(merged, 1, 40)
        r6c_last = window_rate(merged, 1071, 1110)
        chk("P-R2-1 DEMONSTRATED: with a 10.43 % cheap first window and a settled "
            "tail, the R6c-FORM statistic sits at ~10.4 %, NOT below 5 %",
            0.10 < abs(r6c_last - r6c_first) / r6c_last < 0.11)
        h1 = window_rate(merged, 41, 575)
        h2 = window_rate(merged, 576, 1110)
        chk("...while the R2 HALF-SPLIT statistic on THE SAME series is ~0 -- the "
            "window was the defect, not the threshold",
            max(abs(h2 - h1) / h2, abs(h2 - h1) / h1) < 1e-9)

        # ---- THE STRICTER NORMALISER MUST BE THE ONE GRADED -----------------
        a, bq = 1.0, 1.2
        chk("with a RISING rate the graded (larger) statistic is the one "
            "normalised by the FIRST half, not the second",
            max(abs(bq - a) / bq, abs(bq - a) / a) == abs(bq - a) / a)
        chk("T25R6c's own numbers: 13.939 % by `last`, 16.197 % by `first` -- its "
            "gate failed under the LOOSER of the two",
            abs((0.401750 - 0.345750) / 0.401750 - 0.13939) < 5e-5
            and abs((0.401750 - 0.345750) / 0.345750 - 0.16197) < 5e-5)

        # ---- THE TRANSIENT LOCATOR -----------------------------------------
        it = {k: (50 if k <= 17 else 93) for k in range(1, N_B + 1)}
        s, band = transient_end(it, N_B)
        chk("the transient locator finds a PLANTED work boundary at step 18",
            s == 18 and band == (92.0, 94.0))
        it2 = {k: 93 for k in range(1, N_B + 1)}
        chk("...and returns step 1 when there is NO transient (none invented)",
            transient_end(it2, N_B)[0] == 1)
        it3 = {k: (93 if k != 700 else 400) for k in range(1, N_B + 1)}
        chk("A MUTATION FLIPS IT: one planted late excursion at step 700 moves "
            "the boundary to 701 (a [min,max] band would have hidden it)",
            transient_end(it3, N_B)[0] == 701)
        it4 = {k: (60 if k <= D_EXCL + 5 else 93) for k in range(1, N_B + 1)}
        chk("C-R2-1 FIRES: a transient running 5 steps past the registered "
            "exclusion is caught", transient_end(it4, N_B)[0] > D_EXCL)

        # ---- rho arithmetic -------------------------------------------------
        pa = os.path.join(tmpd, "log.A")
        pb = os.path.join(tmpd, "log.B")
        _synth_log(pa, N_A, 1.00)
        _synth_log(pb, N_B, 0.60)
        ra = rate(deltas(read_exec(pa)["exec_at"], N_A))
        rb = window_rate(read_exec(pb)["exec_at"], D_EXCL + 1, N_B)
        chk("rho recovers a planted 0.60 ratio to 3 dp", abs(rb / ra - 0.60) < 5e-4)
        chk("the direction gate fires the right way at rho = 0.60 and 1.40",
            (rb / ra) < RHO_THRESHOLD <= 1.40)

    finally:
        shutil.rmtree(tmpd, ignore_errors=True)

    # ---- the frozen constants ------------------------------------------------
    chk("N_A + N_B = 1150 steps", N_A + N_B == 1150)
    chk("the graded window is 1070 steps, split into two halves of %d" % W_HALF,
        N_B - D_EXCL == 2 * W_HALF and W_HALF == 535)
    chk("leg B ends at t = 0.8 + 1110 x 0.1 = 111.8",
        abs(ENDTIME_A + N_B * DT_B - ENDTIME_B) < 1e-9)
    chk("leg A ends at t = 40 x 0.02 = 0.8", abs(N_A * DT_A - ENDTIME_A) < 1e-9)
    chk("the plateau threshold is UNCHANGED from T25R6c at 5 %", PLATEAU_TOL == 0.05)
    chk("the per-run cap is ~3x the point estimate and is a POINT, not a bound",
        2.9 <= CAP_PER_RUN_CORE_MIN / POINT_CORE_MIN <= 3.2)
    chk("the cap derives $%.5f at $0.0513/core-h (DERIVED, NOT MEASURED)"
        % (CAP_PER_RUN_CORE_MIN / 60.0 * USD_PER_CORE_H),
        CAP_PER_RUN_CORE_MIN / 60.0 * USD_PER_CORE_H < 0.05)
    chk("the cap is far below the $150 single-run escalation trigger",
        CAP_PER_RUN_CORE_MIN / 60.0 * USD_PER_CORE_H < 150.0)
    chk("the whole run is 0.23 % of the 20,000 core-min T25 ceiling, which this "
        "rung does not touch", CAP_PER_RUN_CORE_MIN / A13_CEILING < 0.01)
    chk("the B-R2 relief threshold is 20000/24709.3 = 0.809412",
        abs(RHO_BLEND_RELIEF - 0.809412) < 5e-6)
    chk("the ladder mixture resolves to 11,800 steps (3500 + 8300)",
        LADDER_N_A + LADDER_N_B == 11800)
    chk("the registered exclusion of %d is 0.48 %% of the ladder's leg-B steps"
        % D_EXCL, abs(D_EXCL / LADDER_N_B - 0.00482) < 5e-5)
    chk("leg B samples 12.4 % of the 900 s soak, against T25R6c's 4.4 %",
        abs(ENDTIME_B / 900.0 - 0.1242) < 5e-4)
    chk("every prediction is a POINT with a stated basis, never an inequality "
        "(L-463)",
        all(isinstance(v, float) and v > 0 for v in
            (P_R2_1_R6C_FORM_STATISTIC, P_R2_2_GRADED_PLATEAU, P_R2_3_RHO_POST,
             P_R2_4_COST_CORE_MIN, P_R2_7_PER_HALF_DRIFT_SD_PCT)))
    chk("the predicted verdict is from the fixed vocabulary",
        PREDICTED_VERDICT in ("PASS", "GATE FAIL", "NOT A RESULT", "GATE REACHED",
                              "BLOCKED", "PENDING"))
    chk("PLANT_S is representable at the log's own 2-dp print granularity",
        abs(round(PLANT_S, 2) - PLANT_S) < 1e-12 and PLANT_S >= 0.01)
    src = open(os.path.abspath(__file__), errors="replace").read()
    chk("every case name appears as a literal string in this source",
        all(('"%s"' % c) in src for c in CASES))
    chk("no bare `assert` is used as a control (python3 -O strips them)",
        not re.search(r"^\s*assert\b", src, re.M))

    print("\nSELFTEST %s (%d failed)" % ("PASS" if not fails[0] else "FAIL", fails[0]))
    return 0 if not fails[0] else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    if "--grade" in sys.argv:
        root = HERE
        if "--root" in sys.argv:
            root = os.path.abspath(sys.argv[sys.argv.index("--root") + 1])
        sys.exit(grade(root))
    print(__doc__)
    sys.exit(EXIT_REFUSE)


# ===========================================================================
# AMENDMENT 1 -- 2026-09-03 -- RECORD-EMISSION REPAIR.  VERSION BUMP: the file
# as frozen at f67ade8d carried NO version constant, so the bump is recorded
# HERE and nowhere else -- v1.0 (frozen, blob eb363769bb18dd0550b551e6fa5ba457
# f002cfb9) -> v1.1 (this amendment).  Introducing a version CONSTANT would
# have been a second change to the body and is deliberately not made.
# ===========================================================================
#
# LINES WHOSE NUMBER CHANGED ABOVE THIS SECTION: 0.  VERIFIED BY DIFF, NOT
# RECITED: the diff of this file against blob eb363769bb18dd0550b551e6fa5ba457
# f002cfb9 is ONE 1-for-1 line replacement at :863 plus this appended block.
# Nothing is inserted or deleted above this section, so every record that
# cites this file by line still lands on the same statement -- including
# VERIFICATION_CHARTER.md 2ah.3's :117-120, :551, :583, :702, :719, :800,
# :808, :826, :829, :856, :863 and :870.
#
# HONEST QUALIFICATION, BECAUSE RULE 6'S CANONICAL AMENDMENT IS A PURE APPEND
# AND THIS ONE IS NOT.  One line's CONTENT changed in place.  Line NUMBERING is
# untouched -- the assertion above is about numbering and is true as written --
# but the frozen blob is NO LONGER A BYTE-EXACT PREFIX of this file, so a
# prefix-form freeze check (the form carried at cases/F23b_HP_WEDGE/
# grade_f23b.py, verify_freeze_prefix) would flag it and would be RIGHT to.
# TWO OF THE THREE STATES BELOW ARE MEASURED AND THE THIRD IS A READING, AND
# THEY ARE NOT ASSERTED AT THE SAME STRENGTH.
#   MEASURED, 2026-09-03, by running scripts/check_comparator_freeze.py against
#   this tree: it reported this comparator FROZEN before the repair
#   (worktree_differs_from_HEAD False), and MODIFIED_AFTER_COMMIT with the
#   repair on disk and uncommitted (worktree_differs_from_HEAD True).
#   NOT MEASURED, and named as what it is: a READING of
#   check_comparator_freeze.py:404-409 says that once this amendment is
#   committed the same check should report AMENDED_AFTER -- that checker's own
#   designed state for a rule-6 amendment to a published rung.  THAT THIRD
#   STATE HAD NOT BEEN OBSERVED WHEN THIS BLOCK WAS WRITTEN, and could not be:
#   it cannot exist until the commit does.  It is observable immediately after
#   that commit, and the observation is recorded WHERE IT IS TAKEN -- in the
#   rung's results record -- and is never retrofitted into this block.
#
# (i) WHAT CHANGED -- ONE CHARACTER, AT :863, INSIDE finish().
#     STRUCK -- the frozen text, quoted verbatim and NEVER rewritten:
#         "advance as an irreducible ~3 % floor; (b) leg B's restart coupling to "
#     REPLACED BY:
#         "advance as an irreducible ~3 %% floor; (b) leg B's restart coupling to "
#     The literal at :856-868 is an implicit concatenation closed by `% D_EXCL`
#     at :868.  In the frozen text the `% f` of "% floor" parses as a valid
#     conversion -- space flag, 'f' float -- and CONSUMES D_EXCL, leaving the
#     real `%d` at :865 with no argument: TypeError: not enough arguments for
#     format string.  Escaping to `%%` restores the literal per-cent sign, and
#     the emitted prose is byte-for-byte what the frozen file intended to emit.
#     NOTHING ELSE IS CHANGED: no refactor, no added field, no exit code, no
#     reformatting.
#
# (ii) WHEN -- 2026-09-03, AFTER the graded solve and AFTER the pre-repair
#     stdout, traceback intact and tidied away nowhere, was landed at 286276a1
#     as T25R6cR2_GRADE_STDOUT.txt.  That file is NOT edited by this amendment
#     and is not re-graded by it.
#
# (iii) WHAT WAS READABLE AT THAT MOMENT -- every gate line.  The crash is at
#     :863 inside finish(), called at :826, AFTER all grading.  All 43 printed
#     lines up to the traceback were already on stdout and are landed.  What
#     was NOT readable: the registered artifact T25R6cR2_VERDICT.json, which
#     json.dump at :870 never reached.
#
# (iv) WHICH FINDINGS REST ON THIS AND WHICH DO NOT.  NO gate finding rests on
#     it.  G-R2-1 PLATEAU 0.3546 % against the 5 % threshold, G-R2-2
#     rho = 1.103859, the verdict GATE FAIL, C-R2-1, the rule-3 planted-zero
#     control, the rule-4 completion line, R-R2-1, R-R2-2 and R-R2-4 are all
#     computed above :826 and print byte-identically before and after --
#     MEASURED by the 2ah.1 probe over all 43 lines, not asserted.  What rests
#     on the repair is exactly two things: the EXISTENCE of
#     T25R6cR2_VERDICT.json, and the process exit code.
#
# (v) FIFTH DISCLOSURE CONTENT, REQUIRED BY 2ah.3 -- THE REGISTERED CHANNELS
#     THAT MOVED, WITH THEIR PRE- AND POST-REPAIR VALUES:
#       * the process exit code: registered 3 (EXIT_GATE_FAIL, :117-120)
#         -> 1 ACTUAL, an unhandled TypeError leaving the interpreter through
#         the unguarded __main__ -> 3 AFTER THIS REPAIR.
#       * the verdict artifact registered at T25R6cR2_PREREGISTRATION.md:532:
#         ABSENT -> PRESENT.
#     No other registered channel moved.
#
# (vi) WHICH OFF-PATH CLAIM THIS AMENDMENT STANDS ON, per 2ah.3's closing
#     narrowing.  IT IS SPLIT, AND THAT IS SAID RATHER THAN AVERAGED:
#       * ON THE GATE VALUES -- the STRUCTURAL claim, "nothing downstream
#         COMPUTES it".  Every out["verdict"] assignment is at :551, :583,
#         :702, :800 and :808, all inside grade() and all above the finish()
#         call at :826; rho is computed at :719; finish() opens at :829 by
#         storing the rc it was handed.  Nothing at or after :829 computes a
#         gate value.  This claim does not expire.
#       * ON THE EXIT CODE -- a CONSUMER CENSUS ONLY, "nothing READS it".  It
#         is the strictly weaker claim and it EXPIRES the moment somebody
#         writes a consumer of this grader's rc.
#
# (vii) THE 2ah.2 CONDITION IS DISCHARGED BY RE-RUN, NOT BY THIS TEXT.  The
#     repaired grader was driven through the production path against the real
#     case directory; T25R6cR2_VERDICT.json exists on disk and parses; its gate
#     lines are byte-identical to the landed stdout; the process exited 3.  The
#     receipt is in the rung's record.
#
# (viii) RULE 2'S FREEZE VERIFICATION WAS SATISFIED BY HAND AND NOT BY THE
#     REGISTERED PATH.  T25R6cR2_PREREGISTRATION.md:532 registers that this
#     grader reports its own git blob sha1 and full disk sha256 INTO
#     T25R6cR2_VERDICT.json at grade time.  That artifact was UNREACHABLE
#     through the frozen path, so the verification was done BY HAND, ON THE
#     PRE-REPAIR BYTES, against blob eb363769bb18dd0550b551e6fa5ba457f002cfb9
#     -- identical on disk at that moment, at freeze commit f67ade8d, and at
#     HEAD -- with disk sha256
#     421b9cf4e7768b95cb9ca6d5eed1e2c093142a934100f90b0bf39de32d45d07b.  A
#     reader must not be left to assume the registered path produced it.
#     AND THE CONVERSE, SO NOBODY MISREADS THE ARTIFACT THAT NOW EXISTS: the
#     T25R6cR2_VERDICT.json emitted after this repair carries THIS FILE'S
#     POST-AMENDMENT hashes, which attest the AMENDED file and NOT the frozen
#     one.  Those two values are deliberately NOT written here -- writing a
#     file's own sha into itself changes the sha, which is the same reason the
#     registration at T25R6cR2_PREREGISTRATION.md:530-534 has the grader
#     recompute them at grade time rather than carry them as constants.  They
#     are recorded in the rung's results record instead.  The frozen blob
#     eb363769 is what graded the landed stdout; the two are reconciled only by
#     this amendment.
#
# (ix) AUTHORITY, AND ITS LIMITS.  VERIFICATION_CHARTER.md 2ah, 2ah.1, 2ah.2
#     and 2ah.3, landed v1.53: an off-grading-path post-compute change needs no
#     2d.1 exception, no petition and no ruling; CLAUDE.md rule 6 supplies this
#     FORM and 2d:1842-1845 supplies contents (i)-(iv).  NO EXIT-CODE CONTRACT
#     IS ADOPTED HERE: 2ak (v1.54) is FORWARD-ONLY, this comparator is outside
#     its scope, no EXIT_INSTRUMENT_ERROR is introduced, and the unguarded
#     __main__ -- Defect B -- is NOT repaired by this amendment.
# ===========================================================================
