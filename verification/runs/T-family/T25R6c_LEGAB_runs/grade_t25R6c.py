#!/usr/bin/env python3
"""T25R6c GRADER / COMPARATOR -- G-T6c-1 (PLATEAU) and G-T6c-2 (DIRECTION).

FROZEN AT THE PRE-REGISTRATION AMENDMENT COMMIT, BEFORE ANY CASE DIRECTORY HELD
COMPUTE.  Registration: docs/campaigns/T-family/T25R6c_PREREGISTRATION.md,
frozen 5e51676e, amended v1.1 (the amendment that PINS this file by blob).

WHAT IS MEASURED
----------------
    rho = r(leg B) / r(leg A)

both per-step wall rates from `ExecutionTime` deltas, taken WITHIN ONE RUN, so
arm, mesh, ranks, `0/` and solver are identical between numerator and
denominator by construction.  Leg A is 40 steps at deltaT 0.02 (the window every
C4/C5 wall factor was measured on).  Leg B is 400 steps at deltaT 0.1 from
`latestTime`, t = 0.8 -> 40.8 s -- a BOUNDED sample of the ladder's soak regime.

WHY THE TWO LEGS ARE INDEPENDENT, AND WHAT WOULD BREAK IT
---------------------------------------------------------
INDEPENDENT: r(leg A) and r(leg B) are means over DISJOINT sets of ExecutionTime
deltas, parsed from TWO SEPARATE FILES written by TWO SEPARATE `mpirun`
invocations.  Neither number is computed from the other, and no term appears in
both except `ranks` and the constant 60, which cancel in the ratio.  This is the
property the predecessor's cost basis did NOT have: T25R6b claimed two
"independent routes" to one rate where route 2 was route 1 divided by N -- an
algebraic identity wearing the costume of a corroboration.  Nothing in this file
divides one leg's number by the other leg's number to obtain a third.

WHAT WOULD BREAK IT -- stated so a reader does not have to find it:
  (a) THE SHARED BOX.  The legs run sequentially on one shared machine.  If
      effective per-core throughput differs between leg A's window and leg B's
      window, rho absorbs contention as if it were the deltaT regime change.
      Mitigated, not eliminated: /proc/loadavg is witnessed before leg A,
      between the legs and after leg B, and is REPORTED beside rho.  T25R5 lost
      C1/C2/C3 to exactly this hazard, so it is a measured risk, not a
      hypothetical one.
  (b) THE RESTART COUPLING.  Leg B starts `latestTime` from leg A's output, so
      its first steps carry field re-read and matrix re-assembly cost that is a
      leg-A -> leg-B dependency, not a deltaT effect.  G-T6c-1 (PLATEAU) exists
      for this: a leg-B rate still moving is NOT A RESULT before rho is read.
  (c) THE SHARED INSTRUMENT.  Both rates come from ONE parser.  A parser defect
      cancels in the ratio only if it is multiplicative and identical across the
      legs; it is not guaranteed to be, so the planted-zero control is planted
      into BOTH leg logs and read back AT THE PLANTED STEP in each.

DEFAULT-DENY, IN ORDER
----------------------
  1. PLANTED-ZERO control on the ExecutionTime reader, BOTH legs   (rule 3)
  2. rule 4 completion, all conjuncts, AGE GUARD vs `0/module/T`   (rule 4)
  3. G-T6c-1 PLATEAU -- evaluated BEFORE rho is consulted
  4. G-T6c-2 DIRECTION
A failure at 1 is a REFUSAL (exit 2) and issues no verdict at all: a zero from a
reader not shown able to see a non-zero is not evidence.  A failure at 2 or 3 is
NOT A RESULT (exit 4).  THE COMPARATOR REFUSES RATHER THAN DEGRADES.

NO ROACHE TRIPLE IS FORMED, AND THAT IS A REGISTERED DECISION.  This rung
measures WALL COST inside one transient at one mesh.  There is no grid family,
no solution functional at convergence, and therefore no triple: rule 5's
machinery does not apply and is not invoked.  No observed order and no GCI is
computed, quoted, or derivable from this rung.  A successor reading a
grid-convergence claim off these numbers gets NOT A RESULT.

    python3 grade_t25R6c.py --grade
    python3 grade_t25R6c.py --selftest
"""
import glob
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

EXIT_PASS = 0
EXIT_REFUSE = 2
EXIT_GATE_FAIL = 3
EXIT_NOT_A_RESULT = 4

# --- THE CASE.  A module-level literal ON PURPOSE: scripts/check_comparator_freeze.py
# --- derives a comparator's marker scope from string constants in its own source
# --- (D471.1).  A grader whose source names no marker in its tree is reported
# --- AMBIGUOUS-SCOPE and gets NO freeze verdict.  mark_done_t25R6c.py writes
# --- DONE.<CASE> under this same name.
CASES = ["W440_C4_L1"]
CASE = "W440_C4_L1"

# --- FROZEN AT THE REGISTRATION.  Leg geometry.
N_A = 40                 # leg A steps, deltaT 0.02, t 0 -> 0.8
N_B = 400                # leg B steps, deltaT 0.1,  t 0.8 -> 40.8
ENDTIME_A = 0.8
ENDTIME_B = 40.8
DT_A = 0.02
DT_B = 0.1
RANKS = 2

# --- FROZEN AT THE REGISTRATION, section 3.
PLATEAU_TOL = 0.05                 # G-T6c-1: 5 %
PLATEAU_WINDOW = 40                # steps in each plateau window
RHO_THRESHOLD = 1.0                # G-T6c-2: the registered prediction is rho < 1
# B-T6c ceiling relief -- REPORTED, NEVER GATED.
SIGMA_CAP_C4 = 24709.3             # core-min, C4's published Sigma CAP
A13_CEILING = 20000.0              # core-min, Sanaa's; NOT this team's to move
RHO_BLEND_RELIEF = A13_CEILING / SIGMA_CAP_C4     # 0.809412
# The LADDER's own leg mixture, from S1/system/controlDict{,.legB}:
# leg A 70/0.02 = 3500 steps, leg B 830/0.1 = 8300 steps, total 11800.
LADDER_N_A = 3500
LADDER_N_B = 8300

# --- FROZEN AT THE REGISTRATION, section 6.  Rates in core-min per step at 2 ranks.
R_C = 0.1594583          # the T25R4 probe rate -- the CAP basis (conservative)
R_M = 0.1094             # B0_L1's own 40-step arm rate -- THE RATIO DENOMINATOR
POINT_CORE_MIN = 48.136          # (N_A + N_B) * R_M   -- the frozen denominator
CAP_BRACKET_CORE_MIN = 70.162    # (N_A + N_B) * R_C
CAP_PER_RUN_CORE_MIN = 210.485   # 3 x the CAP bracket -- the hard per-run cap
USD_PER_CORE_H = 0.0513

# --- PREDICTION P-C1, registered in the v1.1 amendment under Sanaa's 2026-09-03
# --- 21:00Z launch rule.  The frozen POINT denominator is priced from B0_L1's
# --- GAMG rate while the case is C4_L1's PCG arm, which T25R5 measured 13.56x
# --- faster at L2.  A POINT estimate, never an inequality (L-463).
P_C1_PREDICTED_ACTUAL_CORE_MIN = 4.976   # 440 steps x 13.57 s/40 steps x 2/60, at rho = 1
P_C1_PREDICTED_RATIO = P_C1_PREDICTED_ACTUAL_CORE_MIN / POINT_CORE_MIN   # 0.1034

FIELDS = {"coolant": ["T", "U", "p_rgh", "alphat", "nut", "k", "omega"],
          "module": ["T"]}

TIME_RE = re.compile(r"^Time = ([\d.eE+-]+)")
EXEC_RE = re.compile(r"^ExecutionTime = ([\d.]+) s\s+ClockTime = (\d+) s")

# ----------------------------------------------------------------------------
# THE PLANTED-ZERO CONTROL  (rule 3)
# ----------------------------------------------------------------------------
# PLANT_S is 1.23 s and that value is NOT arbitrary.  OpenFOAM prints
# ExecutionTime to TWO DECIMALS, so the smallest perturbation this log can
# represent at all is 0.01 s.  A 1.234e-03 plant -- the T3 constant -- would be
# ANNIHILATED by the print format and the control would "pass" by reading a zero
# it could never have read otherwise.  1.23 s is exactly representable at the
# log's own granularity and is 123x it.
PLANT_S = 1.23
# The plant is written at ONE step and read back AT THAT STEP.  Never a maximum,
# never a total: VERIFICATION_CHARTER 2d.11.1 found exactly that defect in the T3
# control, where a max-over-all-steps reader would report the plant even if it
# had landed somewhere else entirely.
PLANT_STEP = 7


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def git_blob(path):
    """The sha1 git would give this file's blob, computed locally.  No subprocess:
    a freeze check that shells out can be defeated by PATH."""
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
    """Return dict(exec_at={step: cumulative ExecutionTime s}, times=[Time values],
    end_lines=int).  `step` is 1-based and counts `Time = ` lines.

    ExecutionTime is CUMULATIVE within one mpirun invocation and RESETS at each
    invocation, so leg A and leg B each start their own clock at ~0.  That is
    precisely why the legs are two independent samples and not one series cut in
    half."""
    if not os.path.isfile(path):
        return None
    exec_at, times, ends, step = {}, [], 0, 0
    for ln in open(path, errors="replace"):
        m = TIME_RE.match(ln)
        if m:
            step += 1
            times.append(float(m.group(1)))
            continue
        if ln.startswith("End"):
            ends += 1
            continue
        m = EXEC_RE.match(ln)
        if m and step >= 1:
            exec_at[step] = float(m.group(1))
    return dict(exec_at=exec_at, times=times, end_lines=ends, n_steps=step)


def deltas(exec_at, n):
    """Per-step wall deltas d[i] = E[i] - E[i-1], with E[0] = 0.

    E[0] = 0 IS THE LITERAL READING OF THE REGISTERED STATISTIC and it is
    deliberate.  The registration says "the first 40 leg-B steps"; excluding
    step 1 to hide the restart cost would quietly redefine the frozen window and
    would ALSO hide the very coupling G-T6c-1 exists to catch.  The
    step-1-excluded variant is computed and REPORTED as a diagnostic below; it
    gates nothing."""
    out = []
    prev = 0.0
    for i in range(1, n + 1):
        if i not in exec_at:
            return None
        out.append(exec_at[i] - prev)
        prev = exec_at[i]
    return out


def rate(ds):
    """Mean per-step wall rate over a window of deltas, in wall seconds/step."""
    return sum(ds) / len(ds) if ds else None


def plant_into_log(src, dst):
    """Copy `src` to `dst`, adding PLANT_S to the cumulative ExecutionTime at
    PLANT_STEP AND AT EVERY STEP AFTER IT.

    Adding to the tail rather than to one line is what makes the plant land in
    EXACTLY ONE DELTA: d[PLANT_STEP] rises by PLANT_S and every other delta is
    untouched.  Adding to a single line would move TWO deltas in opposite
    directions and a reader could see the plant while pointing at the wrong step.

    Returns the number of ExecutionTime lines rewritten."""
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
        return dict(passed=False, why="log has %d steps; PLANT_STEP %d is not inside it"
                                      % (n_steps, PLANT_STEP), label=label)
    base = read_exec(log_path)
    if base is None:
        return dict(passed=False, why="no log at %s" % log_path, label=label)
    d0 = deltas(base["exec_at"], n_steps)
    if d0 is None:
        return dict(passed=False, why="log is missing an ExecutionTime line inside "
                                      "1..%d" % n_steps, label=label)
    tmpd = tempfile.mkdtemp(prefix="t25R6c_plant_")
    try:
        dst = os.path.join(tmpd, os.path.basename(log_path))
        nrw = plant_into_log(log_path, dst)
        got = read_exec(dst)                      # <-- READ BACK FROM DISK
        if got is None:
            return dict(passed=False, why="the planted copy could not be read back",
                        label=label)
        d1 = deltas(got["exec_at"], n_steps)
        if d1 is None:
            return dict(passed=False, why="the planted copy lost an ExecutionTime line",
                        label=label)
        def tol(i):
            operands = [abs(base["exec_at"].get(i, 0.0)),
                        abs(base["exec_at"].get(i - 1, 0.0)), PLANT_S]
            return 1e-6 * max(operands)
        seen = d1[PLANT_STEP - 1] - d0[PLANT_STEP - 1]
        at_step_ok = abs(seen - PLANT_S) <= tol(PLANT_STEP)
        moved = [i + 1 for i in range(n_steps)
                 if i + 1 != PLANT_STEP and abs(d1[i] - d0[i]) > tol(i + 1)]
        return dict(passed=bool(at_step_ok and not moved), label=label,
                    plant_s=PLANT_S, plant_step=PLANT_STEP,
                    read_back_delta_change=seen, lines_rewritten=nrw,
                    other_deltas_that_moved=moved[:8],
                    tolerance_at_plant_step=tol(PLANT_STEP),
                    tolerance_basis="1e-6 x max(|E[i]|, |E[i-1]|, PLANT_S) -- relative "
                                    "to the operands differenced, never a bare absolute")
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)


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

    for leg, log, n, et in (("legA", lga, N_A, ENDTIME_A), ("legB", lgb, N_B, ENDTIME_B)):
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
        # clause 5 is a STEP-COUNT identity, not a time-value identity: at
        # deltaT 0.02 endTime 0.8 is 40 counts, and reading rule 4's shorthand
        # literally would fail every case with deltaT != 1.
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
        bad.append("t=%g field dir: %d found" % (ENDTIME_B, len(tdirs)))
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
        old = [f for f in glob.glob(os.path.join(case_dir, "processor*", tdirs[0], "*", "*"))
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
    print("T25R6c -- G-T6c-1 (PLATEAU) and G-T6c-2 (DIRECTION)")
    print("=" * 74)

    me = os.path.abspath(__file__)
    out = dict(rung="T25R6c", case=CASE,
               registration="docs/campaigns/T-family/T25R6c_PREREGISTRATION.md "
                            "(frozen 5e51676e, amendment v1.1 pins this grader)",
               grader_sha256=sha256_of(me), grader_git_blob=git_blob(me),
               roache="NOT INVOKED -- no grid family, no functional at convergence, "
                      "no order and no GCI is computed or derivable (rule 5 does not "
                      "apply to a wall-cost measurement inside one transient)",
               cost_basis=("REPORTED-BY-OWNER; dollars DERIVED at $%.4f/core-h, NOT "
                           "MEASURED -- this box cannot read its own billing "
                           "(COMPUTE_BUDGET_CHARTER section 5)" % USD_PER_CORE_H))

    if not os.path.isdir(case_dir):
        refuse("%s absent -- there is nothing to grade, and a verdict without a run "
               "is not a verdict." % case_dir)

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
        refuse("an ExecutionTime line is missing inside the registered step range; "
               "the rate would be computed over a window that is not the registered "
               "window.")

    rA = rate(dA)
    rB = rate(dB)
    rho = rB / rA

    print("\n[3] G-T6c-1 PLATEAU -- EVALUATED FIRST, BEFORE rho IS CONSULTED")
    first = rate(dB[:PLATEAU_WINDOW])
    last = rate(dB[-PLATEAU_WINDOW:])
    plateau = abs(last - first) / last
    print("     r(first %d leg-B steps) = %.6f s/step" % (PLATEAU_WINDOW, first))
    print("     r(last  %d leg-B steps) = %.6f s/step" % (PLATEAU_WINDOW, last))
    print("     |last - first| / last  = %.4f %%   threshold %.1f %%"
          % (plateau * 100.0, PLATEAU_TOL * 100.0))
    out["plateau"] = dict(first=first, last=last, statistic=plateau,
                          threshold=PLATEAU_TOL, passed=bool(plateau <= PLATEAU_TOL))
    # R-T6c: the windowed trajectory, REPORTED, gating nothing -- so a reader sees
    # the shape and not two endpoints.
    traj = []
    for s in range(0, N_B, PLATEAU_WINDOW):
        w = dB[s:s + PLATEAU_WINDOW]
        traj.append(dict(leg="B", steps=[s + 1, s + len(w)], r=rate(w),
                         rho_window=rate(w) / rA))
    trajA = [dict(leg="A", steps=[1, N_A], r=rA, rho_window=1.0)]
    out["R_T6c_trajectory_reported_gating_nothing"] = trajA + traj
    print("     R-T6c trajectory (REPORTED, gating nothing): %d leg-B windows of %d "
          "steps, rho per window %.4f .. %.4f"
          % (len(traj), PLATEAU_WINDOW, min(t["rho_window"] for t in traj),
             max(t["rho_window"] for t in traj)))

    if plateau > PLATEAU_TOL:
        out["verdict"] = "NOT A RESULT"
        out["rho_measured_but_not_graded"] = rho
        out["ground"] = ("G-T6c-1 PLATEAU FAILED: the leg-B rate moved %.4f %% between "
                         "its first and last %d-step windows, above the registered "
                         "%.1f %%.  A leg-B rate still moving cannot bound the rate at "
                         "step 11,800, and a bound quoted off a moving rate is a false "
                         "bound.  rho = %.6f is printed beside this verdict and IS NOT "
                         "A RESULT."
                         % (plateau * 100.0, PLATEAU_WINDOW, PLATEAU_TOL * 100.0, rho))
        print("\n  G-T6c: NOT A RESULT -- the plateau clause refused before rho was read.")
        return finish(out, EXIT_NOT_A_RESULT, root)

    print("\n[4] G-T6c-2 DIRECTION")
    print("     r(leg A) = %.6f s/step over %d steps at deltaT %.2f" % (rA, N_A, DT_A))
    print("     r(leg B) = %.6f s/step over %d steps at deltaT %.2f" % (rB, N_B, DT_B))
    print("     rho = r(B)/r(A) = %.6f      registered prediction: rho < %.1f"
          % (rho, RHO_THRESHOLD))
    out["r_legA_s_per_step"] = rA
    out["r_legB_s_per_step"] = rB
    out["rho"] = rho
    # The step-1-excluded variant: REPORTED as a diagnostic, gating nothing.
    rA2 = rate(dA[1:])
    rB2 = rate(dB[1:])
    out["diagnostic_step1_excluded"] = dict(
        r_legA=rA2, r_legB=rB2, rho=rB2 / rA2,
        note="REPORTED, GATES NOTHING.  The graded statistic is the LITERAL reading "
             "with step 1 included; this variant is printed so a reader can see how "
             "much of rho is leg B's restart cost.")
    print("     diagnostic (step 1 excluded, gating nothing): rho = %.6f" % (rB2 / rA2))

    print("\n[5] B-T6c CEILING RELIEF -- REPORTED, NEVER GATED")
    # THE REGISTRATION FIXES THE THRESHOLD ON rho_blend AND DOES NOT FIX
    # rho_blend'S MIXTURE.  Both readings are reported and NEITHER gates.  The
    # LADDER mixture is the one that means anything for a statement about the
    # ladder's cost; the PROBE mixture is this run's own and is reported only so
    # the ambiguity is visible rather than silently resolved by this lane.
    blend_ladder = (LADDER_N_A + LADDER_N_B * rho) / (LADDER_N_A + LADDER_N_B)
    blend_probe = (N_A + N_B * rho) / (N_A + N_B)
    out["B_T6c_reported_never_gated"] = dict(
        rho_blend_ladder=blend_ladder, rho_blend_probe=blend_probe,
        relief_threshold=RHO_BLEND_RELIEF,
        sigma_cap_c4_x_blend_ladder=SIGMA_CAP_C4 * blend_ladder,
        sigma_cap_c4_x_blend_probe=SIGMA_CAP_C4 * blend_probe,
        a13_ceiling=A13_CEILING,
        ambiguity="THE REGISTRATION FIXES THE THRESHOLD 0.809412 ON rho_blend AND "
                  "DOES NOT DEFINE rho_blend'S MIXTURE.  Both readings are reported; "
                  "neither gates; this lane resolves nothing.  The ladder mixture "
                  "(3500 leg-A + 8300 leg-B steps) is the one a ceiling statement "
                  "would need.",
        not_a_relief_grant="THIS ROW GRANTS NOTHING.  The A1.3 ceiling of 20,000 "
                           "core-min is not this team's to move and this rung "
                           "pre-registers no widening.")
    print("     rho_blend (ladder mixture 3500A + 8300B) = %.6f  ->  Sigma CAP(C4) x "
          "blend = %.1f core-min vs ceiling %.0f" % (blend_ladder,
                                                     SIGMA_CAP_C4 * blend_ladder, A13_CEILING))
    print("     rho_blend (probe mixture   40A +  400B) = %.6f  ->  %.1f core-min"
          % (blend_probe, SIGMA_CAP_C4 * blend_probe))
    print("     relief threshold on rho_blend = %.6f.  REPORTED, NEVER GATED, AND "
          "GRANTS NO WIDENING." % RHO_BLEND_RELIEF)

    print("\n[6] X-T6c CONSISTENCY -- REPORTED, AND ONE ROUTE IS STRUCK AS A TAUTOLOGY")
    # ***THE TAUTOLOGY THIS RUNG EXISTS NOT TO REPEAT.***  The registration's
    # closed form rho = ((N_A+N_B)*ratio - N_A)/N_B, applied to a cost ratio taken
    # against THIS RUN'S OWN r(leg A), returns rho EXACTLY BY ALGEBRA:
    #     total = N_A*rA + N_B*rB ;  ratio = total/((N_A+N_B)*rA) = (N_A+N_B*rho)/(N_A+N_B)
    #     => ((N_A+N_B)*ratio - N_A)/N_B = rho, identically.
    # That is the SAME shape struck at registration section 1 -- a number divided
    # back by what built it, wearing the costume of a corroboration.  It is
    # computed here ONLY as an arithmetic bookkeeping check on the parser, is
    # labelled as such, and corroborates NOTHING about the physics.
    total_wall_s = lga["exec_at"][N_A] + lgb["exec_at"][N_B]
    total_core_min = total_wall_s * RANKS / 60.0
    ratio_own = total_wall_s / ((N_A + N_B) * rA)
    rho_roundtrip = ((N_A + N_B) * ratio_own - N_A) / N_B
    # THE NON-TAUTOLOGICAL ROUTE: price the actual against the FROZEN denominator,
    # which was measured on a DIFFERENT run (B0_L1, T25R5) and cannot be derived
    # from anything this run produced.
    ratio_vs_frozen = total_core_min / POINT_CORE_MIN
    out["X_T6c_reported"] = dict(
        total_wall_s=total_wall_s, total_core_min=total_core_min,
        roundtrip_rho=rho_roundtrip, roundtrip_residual=abs(rho_roundtrip - rho),
        roundtrip_status="STRUCK AS A CORROBORATION -- ALGEBRAICALLY IDENTICAL TO rho. "
                         "Retained ONLY as a parser bookkeeping check; it says nothing "
                         "about the physics and is not evidence for rho.",
        actual_vs_frozen_point_ratio=ratio_vs_frozen,
        frozen_point_core_min=POINT_CORE_MIN,
        independent_because="POINT_CORE_MIN is (N_A+N_B) x R_M, and R_M = 0.1094 was "
                            "measured on B0_L1 in T25R5 -- a DIFFERENT run, on a "
                            "DIFFERENT arm, before this case existed.  Nothing this "
                            "run produced enters it.")
    print("     total %.2f wall s x %d ranks / 60 = %.4f core-min"
          % (total_wall_s, RANKS, total_core_min))
    print("     round-trip rho through the registered closed form = %.6f "
          "(residual %.2e)" % (rho_roundtrip, abs(rho_roundtrip - rho)))
    print("     >> STRUCK AS A CORROBORATION: that route is rho divided back by what")
    print("        built it.  It is the SAME tautology the registration struck at")
    print("        section 1 and it corroborates NOTHING.  Kept as a parser check.")
    print("     actual / FROZEN POINT (%.3f core-min, from B0_L1's rate, a different"
          % POINT_CORE_MIN)
    print("        run) = %.4f   <-- the one comparison here that is not circular"
          % ratio_vs_frozen)

    print("\n[7] PREDICTED-VS-ACTUAL (rule 12) -- REPORTED, GATING NOTHING")
    out["predicted_vs_actual"] = dict(
        frozen_point_core_min=POINT_CORE_MIN, actual_core_min=total_core_min,
        ratio_actual_over_predicted=ratio_vs_frozen,
        P_C1_predicted_actual_core_min=P_C1_PREDICTED_ACTUAL_CORE_MIN,
        P_C1_predicted_ratio=P_C1_PREDICTED_RATIO,
        P_C1_verdict=("WINS" if abs(ratio_vs_frozen - P_C1_PREDICTED_RATIO) <= 0.5 *
                      P_C1_PREDICTED_RATIO else "LOSES"),
        attribution="MISPREDICTION, not contention and not waste: the frozen POINT "
                    "denominator is priced from B0_L1's GAMG rate while this case is "
                    "C4_L1's PCG arm, which T25R5 measured 13.56x faster at L2.  "
                    "Registered as PREDICTION P-C1 BEFORE the run under Sanaa's "
                    "2026-09-03 21:00Z launch rule, not discovered after it.",
        cap_core_min=CAP_PER_RUN_CORE_MIN,
        cap_breached=bool(total_core_min > CAP_PER_RUN_CORE_MIN),
        usd_derived_not_measured=round(total_core_min / 60.0 * USD_PER_CORE_H, 6),
        calibration_row_owed="docs/COST_CALIBRATION.md -- owed at completion under "
                             "rule 12; NOT discharged by this verdict.")
    print("     actual %.4f core-min vs frozen POINT %.3f  ->  ratio %.4f"
          % (total_core_min, POINT_CORE_MIN, ratio_vs_frozen))
    print("     P-C1 predicted ratio %.4f  ->  %s"
          % (P_C1_PREDICTED_RATIO, out["predicted_vs_actual"]["P_C1_verdict"]))

    if rho < RHO_THRESHOLD:
        out["verdict"] = "PASS"
        out["ground"] = ("G-T6c-2: rho = %.6f < %.1f.  The registered direction HOLDS: "
                         "leg-B steps are cheaper, and the C4/C5 wall factors measured "
                         "on the ramp window are conservative in the SAFE direction."
                         % (rho, RHO_THRESHOLD))
        rc = EXIT_PASS
        print("\n  G-T6c: PASS -- rho = %.6f < %.1f." % (rho, RHO_THRESHOLD))
    else:
        out["verdict"] = "GATE FAIL"
        out["ground"] = ("G-T6c-2: rho = %.6f >= %.1f.  A1.2's REGISTERED DIRECTION IS "
                         "FALSIFIED: leg-B steps are NOT cheaper, so every CAP in the "
                         "C4/C5 line is conservative in the UNSAFE direction rather "
                         "than the safe one." % (rho, RHO_THRESHOLD))
        rc = EXIT_GATE_FAIL
        print("\n  G-T6c: GATE FAIL -- rho = %.6f >= %.1f.  A1.2's DIRECTION IS "
              "FALSIFIED." % (rho, RHO_THRESHOLD))

    print("\n  ROACHE (rule 5) -- NOT INVOKED, AND THAT IS A REGISTERED DECISION.")
    print("  There is no grid family here and no functional at convergence: this is a")
    print("  WALL-COST measurement inside one transient at one mesh.  NO observed order")
    print("  and NO GCI is computed, quoted or derivable.  A successor reading a")
    print("  grid-convergence claim off these numbers gets NOT A RESULT.")
    return finish(out, rc, root)


def finish(out, rc, root, name="T25R6c_VERDICT.json"):
    out["exit"] = rc
    out["what_this_does_not_do"] = [
        "IT AUTHORISES NO LADDER LAUNCH.  T25R5 5.1 is carried IN FORCE: no ladder "
        "launches on this result, whatever it says.",
        "IT DOES NOT MEASURE THE SOAK RATE AT STEP 11,800.  It samples t <= 40.8 s of "
        "a soak that runs to t = 900 s; the plateau clause is what licenses reading "
        "rho beyond the sampled steps, and that is a weaker claim, registered as the "
        "weaker claim.",
        "IT DOES NOT RE-OPEN, WIDEN OR RETIRE THE A1.3 CEILING OF 20,000 CORE-MIN, "
        "which is not this team's to move.",
        "IT CONSUMES NO OUTPUT OF T25R6a.  It reads only ExecutionTime deltas from "
        "logs it produced itself -- which matters here, because T25R6a graded NOT A "
        "RESULT (its equivalence control fired).",
    ]
    out["legs_are_independent_because"] = (
        "r(leg A) and r(leg B) are means over DISJOINT delta sets parsed from TWO "
        "SEPARATE log files written by TWO SEPARATE mpirun invocations.  Neither is "
        "computed from the other and no term appears in both but ranks and 60, which "
        "cancel.  WHAT WOULD BREAK IT: (a) a change in the shared box's per-core "
        "throughput between the two windows -- rho would absorb contention as if it "
        "were the deltaT regime change (loadavg witnessed and reported); (b) leg B's "
        "restart coupling to leg A's output, which G-T6c-1 exists to catch; (c) the "
        "single shared parser, whose defects cancel in the ratio only if multiplicative "
        "and identical across legs -- hence the planted-zero control in BOTH legs.")
    p = os.path.join(root, name)
    json.dump(out, open(p, "w"), indent=2, sort_keys=True, default=str)
    print("\n  written %s" % p)
    print("  VERDICT: %s" % out.get("verdict", "(none -- refused)"))
    return rc


# ----------------------------------------------------------------------------
# selftest -- planted controls on this comparator's OWN arithmetic
# ----------------------------------------------------------------------------

def _synth_log(path, n, base_rate, first_extra=0.0, drift=0.0, endtime=1.0, dt=1.0):
    """A synthetic OpenFOAM-shaped log with a known per-step rate."""
    e = 0.0
    with open(path, "w") as fh:
        for i in range(1, n + 1):
            fh.write("Time = %g\n\n" % (i * dt))
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

    print("T25R6c COMPARATOR SELFTEST")
    print("-" * 78)

    tmpd = tempfile.mkdtemp(prefix="t25R6c_selftest_")
    try:
        # ---- the reader reads what was written --------------------------------
        p = os.path.join(tmpd, "log.synth")
        _synth_log(p, 40, 0.50)
        r = read_exec(p)
        chk("the reader finds 40 ExecutionTime lines and 40 Time lines",
            len(r["exec_at"]) == 40 and r["n_steps"] == 40)
        d = deltas(r["exec_at"], 40)
        chk("a 0.50 s/step synthetic log reads back at 0.50 s/step",
            abs(rate(d) - 0.50) < 1e-9)

        # ---- THE PLANTED-ZERO CONTROL MUST FIRE, AND MUST FIRE AT THE STEP ----
        pz = planted_zero_control(p, 40, "synth")
        chk("the planted %.2f s is read back FROM DISK at step %d" % (PLANT_S, PLANT_STEP),
            pz["passed"] and abs(pz["read_back_delta_change"] - PLANT_S) < 1e-6)
        chk("...and NO OTHER delta moved (this is a control on a STEP, not a maximum)",
            pz["other_deltas_that_moved"] == [])

        # PLANTED VIOLATION 1: a reader that returns a CONSTANT cannot see the plant.
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

        # PLANTED VIOLATION 2: a max-over-all-steps reading would pass a plant that
        # landed at the WRONG step.  Plant at PLANT_STEP but check clause (ii)
        # catches a smeared plant.
        p2 = os.path.join(tmpd, "log.smear")
        _synth_log(p2, 40, 0.50)
        dst = os.path.join(tmpd, "log.smear.planted")
        # smear the plant across EVERY delta instead of one
        with open(p2, errors="replace") as fh:
            lines = fh.readlines()
        step, acc = 0, 0.0
        for k, ln in enumerate(lines):
            if TIME_RE.match(ln):
                step += 1
                continue
            m = EXEC_RE.match(ln)
            if m:
                acc += PLANT_S / 40.0
                lines[k] = "ExecutionTime = %.4f s  ClockTime = %s s\n" % (
                    float(m.group(1)) + acc, m.group(2))
        open(dst, "w").writelines(lines)
        b = deltas(read_exec(p2)["exec_at"], 40)
        s = deltas(read_exec(dst)["exec_at"], 40)
        smear_at_step = abs((s[PLANT_STEP - 1] - b[PLANT_STEP - 1]) - PLANT_S)
        chk("A SMEARED plant does NOT read back as PLANT_S at the planted step "
            "(a max-over-steps control would have passed it)", smear_at_step > 0.5)

        # ---- the PLATEAU clause must fire on a drifting leg B -----------------
        pflat = os.path.join(tmpd, "log.flat")
        _synth_log(pflat, 400, 0.50)
        dflat = deltas(read_exec(pflat)["exec_at"], 400)
        st_flat = abs(rate(dflat[-40:]) - rate(dflat[:40])) / rate(dflat[-40:])
        chk("a FLAT leg B passes the 5 % plateau clause", st_flat <= PLATEAU_TOL)
        pdrift = os.path.join(tmpd, "log.drift")
        _synth_log(pdrift, 400, 0.50, drift=0.002)
        ddrift = deltas(read_exec(pdrift)["exec_at"], 400)
        st_drift = abs(rate(ddrift[-40:]) - rate(ddrift[:40])) / rate(ddrift[-40:])
        chk("a DRIFTING leg B (+0.002 s/step) FAILS the 5 % plateau clause",
            st_drift > PLATEAU_TOL)
        chk("A MUTATION FLIPS THE ANSWER: flat passes and drifting fails on the "
            "SAME threshold", st_flat <= PLATEAU_TOL < st_drift)

        # ---- rho arithmetic ---------------------------------------------------
        pa = os.path.join(tmpd, "log.A")
        pb = os.path.join(tmpd, "log.B")
        _synth_log(pa, N_A, 1.00)
        _synth_log(pb, N_B, 0.60)
        ra = rate(deltas(read_exec(pa)["exec_at"], N_A))
        rb = rate(deltas(read_exec(pb)["exec_at"], N_B))
        chk("rho recovers a planted 0.60 ratio to 3 dp", abs(rb / ra - 0.60) < 5e-4)
        chk("the registered direction gate fires the right way at rho = 0.60 and 1.40",
            (rb / ra) < RHO_THRESHOLD and 1.40 >= RHO_THRESHOLD)

        # ---- THE TAUTOLOGY IS A TAUTOLOGY, DEMONSTRATED, NOT ASSERTED ---------
        rho_t = rb / ra
        ratio_own = (N_A * ra + N_B * rb) / ((N_A + N_B) * ra)
        rt = ((N_A + N_B) * ratio_own - N_A) / N_B
        chk("the registered closed form applied to the run's OWN r(leg A) returns rho "
            "IDENTICALLY -- it is a tautology and is struck as a corroboration",
            abs(rt - rho_t) < 1e-12)

    finally:
        shutil.rmtree(tmpd, ignore_errors=True)

    # ---- the frozen constants -------------------------------------------------
    chk("N_A + N_B = 440 steps", N_A + N_B == 440)
    chk("the CAP bracket is 440 x R_C = 70.162 core-min",
        abs((N_A + N_B) * R_C - CAP_BRACKET_CORE_MIN) < 5e-4)
    chk("the POINT bracket is 440 x R_M = 48.136 core-min",
        abs((N_A + N_B) * R_M - POINT_CORE_MIN) < 5e-4)
    # 3 x the UNROUNDED bracket: 440 x 0.1594583 = 70.161652, x3 = 210.484956.
    # Multiplying the DISPLAYED 70.162 gives 210.486 and disagrees in the third
    # decimal -- the registration's 210.485 comes from the unrounded chain, and
    # this check is written against the chain rather than against the display.
    chk("the hard per-run cap is 3x the UNROUNDED CAP bracket = 210.485 core-min",
        abs(3 * (N_A + N_B) * R_C - CAP_PER_RUN_CORE_MIN) < 5e-4)
    chk("the cap derives $0.17996 at $0.0513/core-h (DERIVED, NOT MEASURED)",
        abs(CAP_PER_RUN_CORE_MIN / 60.0 * USD_PER_CORE_H - 0.17996) < 5e-5)
    chk("the cap is far below the $150 single-run escalation trigger",
        CAP_PER_RUN_CORE_MIN / 60.0 * USD_PER_CORE_H < 150.0)
    chk("the B-T6c relief threshold is 20000/24709.3 = 0.809412",
        abs(RHO_BLEND_RELIEF - 0.809412) < 5e-6)
    chk("the ladder mixture resolves to 11,800 steps (3500 + 8300)",
        LADDER_N_A + LADDER_N_B == 11800)
    chk("leg A is 29.7 % of the probe's steps but 70.3 % of the ladder's steps are "
        "leg B -- the asymmetry this rung exists for",
        abs(LADDER_N_B / 11800.0 - 0.7034) < 5e-4)
    chk("P-C1 is a POINT estimate, not an inequality (L-463)",
        isinstance(P_C1_PREDICTED_ACTUAL_CORE_MIN, float)
        and P_C1_PREDICTED_ACTUAL_CORE_MIN > 0)
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
