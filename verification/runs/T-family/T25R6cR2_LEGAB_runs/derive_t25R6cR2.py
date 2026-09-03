#!/usr/bin/env python3
"""T25R6c-R2 DESIGN DERIVATION -- every registered number, derived from measurement.

WHAT THIS IS, AND WHAT IT IS NOT
--------------------------------
THIS IS NOT A GRADER.  It computes NO verdict, applies NO gate and writes NO
DONE marker.  It runs ONCE, BEFORE the R2 registration is frozen, and its whole
job is to turn T25R6c's measured trajectory into the numbers the R2
registration then freezes: the transient exclusion D_EXCL, the leg-B step count
N_B, the plateau window, the cost point estimate and the registered predictions.

It exists because the supervisor's instruction was explicit: leg B's length must
be PREDICTED FROM THE MEASURED TRAJECTORY, not guessed.  A round number chosen
by a lane is not a prediction and cannot be scored.

INPUT -- and it is a single, named, on-disk artifact pair:
    T25R6c_LEGAB_runs/W440_C4_L1/log.solve.legA   (40 steps, deltaT 0.02)
    T25R6c_LEGAB_runs/W440_C4_L1/log.solve.legB   (400 steps, deltaT 0.1)
Both are sha256'd into the output, because they are ~9 MB of solver log and are
NOT carried in git.  DESIGN_DERIVATION.json IS carried in git and holds every
number and the full per-window table, so the derivation survives the log.

THE READER IS THE SAME ONE THE T25R6c GRADER USED, RETYPED HERE ON PURPOSE.
This file must not import grade_t25R6c.py: importing a frozen grader into a
design script makes the design script part of the grader's freeze scope, and a
later edit here would then read as an edit to a frozen comparator.  The retyped
reader is CONTROLLED against the frozen grader's own published output instead --
see check C-1 below, which requires this reader to reproduce the T25R6c verdict's
published planted-zero line counts and the 13.939 % plateau statistic EXACTLY.
A retyped reader that cannot reproduce the frozen one's numbers is a different
instrument and this script refuses.

    python3 derive_t25R6cR2.py            # write DESIGN_DERIVATION.json
    python3 derive_t25R6cR2.py --selftest
"""
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
TFAM = os.path.dirname(HERE)
SRC = os.path.join(TFAM, "T25R6c_LEGAB_runs", "W440_C4_L1")
LOG_A = os.path.join(SRC, "log.solve.legA")
LOG_B = os.path.join(SRC, "log.solve.legB")

EXIT_REFUSE = 2

# --- T25R6c's own frozen geometry, transcribed so the controls below can be
# --- stated against it.  NOT re-derived here.
R6C_N_A = 40
R6C_N_B = 400
R6C_PLATEAU_WINDOW = 40
RANKS = 2
USD_PER_CORE_H = 0.0513

# --- C-1 CONTROL TARGETS: values PUBLISHED by the frozen grade_t25R6c.py, taken
# --- from T25R6c_VERDICT.json and from the supervisor's own read of the grader.
# --- This retyped reader must reproduce them or refuse.
C1_PLATEAU_STATISTIC = 0.13939        # |last40 - first40| / last40, to 5 dp
C1_RHO_ALL_STEPS = 1.063997           # rho over ALL 400 leg-B steps
C1_PLANT_LINES_A = 34                 # planted_zero.legA.lines_rewritten
C1_PLANT_LINES_B = 394                # planted_zero.legB.lines_rewritten

# --- THE GATE THIS DESIGN MUST BE ABLE TO RESOLVE.  Unchanged from T25R6c: the
# --- threshold NUMBER is not moved by R2.  What R2 changes is the WINDOW the
# --- statistic is computed over, and this script derives how long that window
# --- must be for a 5 % threshold to sit outside the box's measured drift.
PLATEAU_TOL = 0.05
Z_TARGET = 1.96      # the threshold must sit at >= this many sd of the drift

TIME_RE = re.compile(r"^Time = ([\d.eE+-]+)")
EXEC_RE = re.compile(r"^ExecutionTime = ([\d.]+) s\s+ClockTime = (\d+) s")
IT_RE = re.compile(r"No Iterations (\d+)")
PLANT_S = 1.23
PLANT_STEP = 7


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_log(path):
    """exec_at{step->cumulative ExecutionTime s}, clock_at{step->ClockTime s},
    iters{step->summed 'No Iterations' over that step}, n_steps, end_lines."""
    if not os.path.isfile(path):
        return None
    exec_at, clock_at, iters = {}, {}, {}
    step, cur, ends = 0, 0, 0
    for ln in open(path, errors="replace"):
        if TIME_RE.match(ln):
            if step >= 1:
                iters[step] = cur
            step += 1
            cur = 0
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
    return dict(exec_at=exec_at, clock_at=clock_at, iters=iters,
                n_steps=step, end_lines=ends)


def deltas(exec_at, n):
    out, prev = [], 0.0
    for i in range(1, n + 1):
        if i not in exec_at:
            return None
        out.append(exec_at[i] - prev)
        prev = exec_at[i]
    return out


def rate(ds):
    return sum(ds) / len(ds) if ds else None


def plant_into_log(src, dst):
    """The frozen grader's plant, retyped: add PLANT_S to the cumulative
    ExecutionTime at PLANT_STEP and every step after, so it lands in exactly one
    delta.  Returns lines rewritten -- the C-1 control quantity."""
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


def planted_zero(path, n_steps):
    """RULE 3, on THIS script's reader.  A design derivation that reads a zero --
    or any number -- from a reader not shown able to see a known perturbation is
    not evidence either.  The same control the grader runs, run here, because
    this script's output is what the registration freezes."""
    base = read_log(path)
    d0 = deltas(base["exec_at"], n_steps)
    if d0 is None:
        return dict(passed=False, why="missing ExecutionTime inside 1..%d" % n_steps)
    tmpd = tempfile.mkdtemp(prefix="t25R6cR2_plant_")
    try:
        dst = os.path.join(tmpd, os.path.basename(path))
        nrw = plant_into_log(path, dst)
        d1 = deltas(read_log(dst)["exec_at"], n_steps)
        if d1 is None:
            return dict(passed=False, why="planted copy lost an ExecutionTime line")

        def tol(i):
            return 1e-6 * max(abs(base["exec_at"].get(i, 0.0)),
                              abs(base["exec_at"].get(i - 1, 0.0)), PLANT_S)
        seen = d1[PLANT_STEP - 1] - d0[PLANT_STEP - 1]
        moved = [i + 1 for i in range(n_steps)
                 if i + 1 != PLANT_STEP and abs(d1[i] - d0[i]) > tol(i + 1)]
        return dict(passed=bool(abs(seen - PLANT_S) <= tol(PLANT_STEP) and not moved),
                    lines_rewritten=nrw, read_back_delta_change=seen,
                    other_deltas_that_moved=moved[:8], plant_s=PLANT_S,
                    plant_step=PLANT_STEP)
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)


# ----------------------------------------------------------------------------
# THE TRANSIENT.  Located by SOLVER WORK, not by cost.
# ----------------------------------------------------------------------------

def find_transient_end(iters, n):
    """First leg-B step s such that the per-step linear-solver iteration count
    NEVER AGAIN LEAVES the settled band, where the band is [min, max] of the
    counts over the LAST HALF of the leg -- the leg's own settled behaviour,
    not a tolerance this lane picked.

    WHY WORK AND NOT COST.  The registered plateau statistic is about cost, and
    cost on a shared box carries the box in it.  Iteration count does not: it is
    what the solver did, and it is identical whether the machine was busy or
    idle.  Locating the restart transient by iteration count therefore gives a
    boundary that a contended re-run would find in the SAME place.  Locating it
    by cost would let the box choose the boundary.

    WHY A BAND AND NOT AN EQUALITY.  The settled region is not literally
    constant -- it carries a small integer spread -- so a strict-equality walk
    back from the end stops at the first ordinary fluctuation and reports a
    boundary hundreds of steps too late.  The band is derived from the data
    rather than asserted.

    WHY A ROBUST BAND AND NOT THE TAIL'S EXTREMES.  Taking [min, max] of the
    tail lets a SINGLE outlier inside the tail widen the band until it contains
    itself -- the excursion then hides in the band it created, and the locator
    reports `settled` over a region the work plainly leaves.  That failure is
    demonstrated in the selftest, not reasoned about.  The band here is
    median +/- max(1, 3 x MAD) of the tail.  The floor of 1 is not a tuning
    knob: iteration counts are INTEGERS, so any half-width below 1 would read an
    ordinary +/-1 fluctuation as a transient."""
    vals = [iters[k] for k in range(1, n + 1)]
    tail = vals[n // 2:]
    med = statistics.median(tail)
    mad = statistics.median([abs(x - med) for x in tail])
    hw = max(1.0, 3.0 * mad)
    lo, hi = med - hw, med + hw
    s = n
    while s > 1 and lo <= vals[s - 2] <= hi:
        s -= 1
    return s, (lo, hi), vals


def window_rates(exec_at, lo, hi, W, overlap_step=None):
    """Non-overlapping (default) or sliding window mean rates over leg-B steps
    [lo, hi] inclusive, 1-based.  Each window rate is a TELESCOPING difference
    (E[end] - E[start])/W, so the ExecutionTime print quantum of 0.01 s enters
    only at the two endpoints: the quantisation error in a window rate is
    <= 0.01/W s/step, which at W = 40 is 0.00025 s/step = 0.065 % of the level.
    The window-to-window scatter measured below is therefore NOT print noise."""
    step = overlap_step or W
    out = []
    s = lo
    while s + W - 1 <= hi:
        e0 = exec_at[s - 1] if s - 1 >= 1 else 0.0
        out.append((exec_at[s + W - 1] - e0) / W)
        s += step
    return out


def derive():
    for p in (LOG_A, LOG_B):
        if not os.path.isfile(p):
            refuse("the T25R6c log this derivation is built on is absent: %s.  A "
                   "design derived from a log that is gone is not a derivation." % p)

    A = read_log(LOG_A)
    B = read_log(LOG_B)
    out = dict(
        what="T25R6c-R2 DESIGN DERIVATION -- inputs to the R2 registration, "
             "derived from T25R6c's measured trajectory.  NO VERDICT IS ISSUED "
             "HERE and no gate is applied.",
        source_logs={
            "log.solve.legA": dict(path=os.path.relpath(LOG_A, os.path.dirname(TFAM)),
                                   sha256=sha256_of(LOG_A),
                                   bytes=os.path.getsize(LOG_A)),
            "log.solve.legB": dict(path=os.path.relpath(LOG_B, os.path.dirname(TFAM)),
                                   sha256=sha256_of(LOG_B),
                                   bytes=os.path.getsize(LOG_B)),
        },
        source_logs_not_in_git="These two logs total ~9.5 MB and are NOT carried "
                               "in git.  Every number this derivation rests on, "
                               "and the FULL per-window table, is written into "
                               "this file, which IS carried in git -- so the "
                               "derivation survives the log.  The sha256s above "
                               "let a reader who still has the logs confirm they "
                               "are the same bytes.")

    # ---- rule 3 on THIS reader ------------------------------------------
    pzA = planted_zero(LOG_A, R6C_N_A)
    pzB = planted_zero(LOG_B, R6C_N_B)
    out["planted_zero_on_this_readers_own_instrument"] = dict(legA=pzA, legB=pzB)
    if not (pzA.get("passed") and pzB.get("passed")):
        refuse("PLANTED-ZERO CONTROL FAILED on this derivation's own reader.  "
               "Every number below would be read by an instrument not shown able "
               "to see a known %.2f s change." % PLANT_S)

    dA = deltas(A["exec_at"], R6C_N_A)
    dB = deltas(B["exec_at"], R6C_N_B)
    if dA is None or dB is None:
        refuse("an ExecutionTime line is missing inside the T25R6c step range")
    rA = rate(dA)
    rB_all = rate(dB)

    # ---- C-1: this retyped reader must reproduce the FROZEN grader's numbers --
    first40 = rate(dB[:R6C_PLATEAU_WINDOW])
    last40 = rate(dB[-R6C_PLATEAU_WINDOW:])
    stat_r6c = abs(last40 - first40) / last40
    c1 = dict(
        plateau_statistic=dict(got=stat_r6c, target=C1_PLATEAU_STATISTIC,
                               ok=abs(stat_r6c - C1_PLATEAU_STATISTIC) <= 5e-5),
        rho_all_steps=dict(got=rB_all / rA, target=C1_RHO_ALL_STEPS,
                           ok=abs(rB_all / rA - C1_RHO_ALL_STEPS) <= 5e-6),
        plant_lines_legA=dict(got=pzA["lines_rewritten"], target=C1_PLANT_LINES_A,
                              ok=pzA["lines_rewritten"] == C1_PLANT_LINES_A),
        plant_lines_legB=dict(got=pzB["lines_rewritten"], target=C1_PLANT_LINES_B,
                              ok=pzB["lines_rewritten"] == C1_PLANT_LINES_B),
        why="This script retypes the T25R6c reader rather than importing the "
            "frozen grader, so that editing this design script can never read as "
            "editing a frozen comparator.  A RETYPED READER IS A DIFFERENT "
            "INSTRUMENT UNTIL IT IS SHOWN TO AGREE.  These four quantities were "
            "PUBLISHED by the frozen grader (T25R6c_VERDICT.json and the "
            "supervisor's read of it) and this reader must reproduce all four.")
    out["C1_control_against_the_frozen_grader"] = c1
    if not all(v["ok"] for k, v in c1.items() if isinstance(v, dict)):
        refuse("C-1 FAILED: this derivation's retyped reader does not reproduce "
               "the frozen T25R6c grader's published numbers, so it is a "
               "different instrument and its design outputs are not evidence.")

    # ---- WHERE THE RESTART TRANSIENT ENDS, BY SOLVER WORK -----------------
    d_end, band, itvals = find_transient_end(B["iters"], R6C_N_B)
    d_measured = d_end - 1                   # steps 1..d_measured are transient
    # THE REGISTERED EXCLUSION IS 40, NOT THE MEASURED %d.  Two reasons, both
    # stated before the run: (1) a 1.5x margin, because R2's own transient is a
    # fresh draw and may run longer than R6c's; (2) 40 steps is EXACTLY the
    # T25R6c plateau window, so R2's excluded region and R6c's `first` window are
    # the same length and the two rungs' statistics stay directly comparable.
    D_EXCL_REG = 40
    tail = itvals[D_EXCL_REG:]
    it_A_mean = sum(A["iters"][k] for k in range(1, R6C_N_A + 1)) / R6C_N_A
    out["transient"] = dict(
        located_by="linear-solver iteration count per leg-B step, NOT by cost",
        settled_band=list(band),
        first_settled_step_measured=d_end,
        D_EXCL_measured=d_measured,
        D_EXCL_REGISTERED_FOR_R2=D_EXCL_REG,
        why_40_not_the_measured_value="A 1.5x margin over the measured %d, and 40 "
            "steps is exactly the T25R6c plateau window -- so R2's excluded "
            "region and R6c's `first` window have the SAME length and the two "
            "rungs stay comparable.  R2's grader MEASURES its own transient end "
            "and returns NOT A RESULT if it exceeds 40, so the margin is a "
            "control and not an assumption." % d_measured,
        iterations_in_the_measured_transient=itvals[:d_measured],
        tail_iterations_min=min(tail), tail_iterations_max=max(tail),
        tail_iterations_mean=sum(tail) / len(tail),
        tail_iterations_spread_pct=(max(tail) - min(tail)) / (sum(tail) / len(tail)) * 100.0,
        legA_iterations_per_step=it_A_mean,
        finding="From leg-B step %d onward the solver does the SAME WORK every "
                "step: %d..%d iterations, a %.3f %% spread across %d steps.  "
                "EVERYTHING THE COST DOES AFTER THAT POINT IS THE MACHINE, NOT "
                "THE PROBLEM -- and the cost varies by %s over the same steps."
                % (d_end, min(tail), max(tail),
                   (max(tail) - min(tail)) / (sum(tail) / len(tail)) * 100.0,
                   len(tail), "several percent, quantified below"))
    settled_iters = sum(tail) / len(tail)

    # ---- THE DRIFT FLOOR: how window-rate scatter falls with window length --
    lo, hi = D_EXCL_REG + 1, R6C_N_B          # 360 post-transient steps
    n_post = hi - lo + 1
    scaling = []
    for W in (10, 20, 30, 40, 45, 60, 72, 90, 120, 180):
        nono = window_rates(B["exec_at"], lo, hi, W)
        slid = window_rates(B["exec_at"], lo, hi, W, overlap_step=max(1, W // 4))
        row = dict(W=W, n_nonoverlapping=len(nono), n_sliding=len(slid))
        if len(nono) >= 3:
            m = statistics.mean(nono)
            row.update(mean=m, sd=statistics.stdev(nono), sd_pct=statistics.stdev(nono) / m * 100.0)
        if len(slid) >= 4:
            ms = statistics.mean(slid)
            row.update(sd_pct_sliding=statistics.stdev(slid) / ms * 100.0)
        scaling.append(row)
    fit_rows = [r for r in scaling if "sd_pct" in r and r["n_nonoverlapping"] >= 3]
    xs = [math.log(r["W"]) for r in fit_rows]
    ys = [math.log(r["sd_pct"]) for r in fit_rows]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    inter = my - slope * mx
    p_exp = -slope
    resid = [y - (inter + slope * x) for x, y in zip(xs, ys)]
    out["drift_floor"] = dict(
        post_transient_steps=n_post, window_range=[lo, hi],
        scaling=scaling,
        power_law=dict(form="sd_pct(W) = exp(%.6f) * W**(-%.6f)" % (inter, p_exp),
                       intercept_ln=inter, exponent_p=p_exp,
                       log_residual_rms=(sum(r * r for r in resid) / n) ** 0.5),
        white_noise_exponent=0.5,
        finding="p = %.3f, NOT 0.5.  The scatter does NOT average away like "
                "independent noise: the box's throughput drifts on timescales "
                "comparable to the run, so tripling the window buys about %.2fx "
                "instead of 1.73x.  THIS IS THE FLOOR UNDER ANY RATE THIS RUNG "
                "CAN MEASURE." % (p_exp, 3.0 ** p_exp),
        quantisation_note="A window rate is a telescoping difference "
                          "(E[end]-E[start])/W, so the 0.01 s ExecutionTime print "
                          "quantum enters only at two endpoints: <= 0.01/W s/step, "
                          "0.065 %% of the level at W = 40.  The scatter above is "
                          "two orders larger and is NOT print noise.")

    # ---- HOW LONG LEG B MUST BE ------------------------------------------
    # The half-split statistic |r(2nd half) - r(1st half)| / r(2nd half) is a
    # difference of two window rates.  Conservatively treating the halves as
    # INDEPENDENT (positive autocorrelation would only shrink the difference's
    # sd, so this errs toward a LONGER leg B):
    #     sd_diff_pct(W) = sqrt(2) * sd_pct(W)
    # and the threshold must sit at Z_TARGET sd:
    #     sqrt(2) * sd_pct(W_half) <= 100*PLATEAU_TOL / Z_TARGET
    need_sd_pct = 100.0 * PLATEAU_TOL / Z_TARGET / math.sqrt(2.0)
    w_half_req = math.exp((inter - math.log(need_sd_pct)) / p_exp)
    W_HALF = int(math.ceil(w_half_req / 5.0) * 5)          # round UP to a multiple of 5
    N_B = D_EXCL_REG + 2 * W_HALF
    N_B = int(math.ceil(N_B / 10.0) * 10)                  # round UP to a multiple of 10
    W_HALF_FINAL = (N_B - D_EXCL_REG) // 2
    sd_at_final = math.exp(inter) * W_HALF_FINAL ** (-p_exp)
    z_at_final = (100.0 * PLATEAU_TOL) / (math.sqrt(2.0) * sd_at_final)
    out["leg_B_length"] = dict(
        required_sd_pct_per_half=need_sd_pct,
        W_half_required_raw=w_half_req,
        D_EXCL=D_EXCL_REG, W_half=W_HALF_FINAL, N_B=N_B,
        endTime_B=0.8 + N_B * 0.1,
        z_of_the_5pct_threshold_at_this_length=z_at_final,
        predicted_sd_pct_per_half=sd_at_final,
        extrapolation_warning="W_half = %d is a %.1fx EXTRAPOLATION beyond the "
                              "longest window the R6c log can form (%d steps). "
                              "The predicted per-half sd of %.3f %% is therefore "
                              "REGISTERED AS PREDICTION P-R2-7 and the R2 grader "
                              "MEASURES it.  If the drift floor is worse than the "
                              "power law says, the 5 %% threshold sits at fewer "
                              "than %.2f sd and the R2 registration will have said "
                              "so in advance."
                              % (W_HALF_FINAL, W_HALF_FINAL / 180.0, 180,
                                 sd_at_final, Z_TARGET),
        why_not_longer="Doubling leg B again buys only %.3f %% off the per-half sd "
                       "at p = %.3f, for double the compute.  The return is "
                       "flattening and the ladder ceiling is not this team's to "
                       "spend against."
                       % (sd_at_final * (1 - 2 ** -p_exp), p_exp))

    # ---- WHAT THE R6c-FORM STATISTIC DOES AT ANY LENGTH -------------------
    post = window_rates(B["exec_at"], lo, hi, R6C_PLATEAU_WINDOW)
    post_mean, post_sd = statistics.mean(post), statistics.stdev(post)
    asymptote = abs(post_mean - first40) / post_mean
    max_last40_that_passes = first40 / (1.0 - PLATEAU_TOL)
    z_pass = (max_last40_that_passes - post_mean) / post_sd
    out["R6c_form_statistic_is_unreachable"] = dict(
        first40_anchored_on_the_transient=first40,
        post_transient_40step_mean=post_mean, post_transient_40step_sd=post_sd,
        asymptote_pct=asymptote * 100.0, threshold_pct=PLATEAU_TOL * 100.0,
        max_r_last40_that_would_pass=max_last40_that_passes,
        observed_post_transient_40step_min=min(post),
        every_post_transient_window_exceeds_it=bool(min(post) > max_last40_that_passes),
        probability_any_given_last40_passes=0.5 * (1.0 + math.erf(z_pass / math.sqrt(2.0))),
        finding="THE T25R6c PLATEAU STATISTIC CANNOT BE SATISFIED BY LENGTHENING "
                "LEG B, AT ANY LENGTH.  Its `first` window is FROZEN on leg-B "
                "steps 1-%d, which are the restart transient and are %.2f %% "
                "CHEAPER than the settled level; extending leg B moves only the "
                "`last` window, which is drawn from the settled distribution.  "
                "The statistic therefore asymptotes to %.3f %%, not to zero, and "
                "the 5 %% gate would need r(last 40) <= %.6f when every one of "
                "the %d observed post-transient windows lies above it."
                % (R6C_PLATEAU_WINDOW, (post_mean - first40) / post_mean * 100.0,
                   asymptote * 100.0, max_last40_that_passes, len(post)),
        this_is_the_answer_to_the_supervisors_question="The supervisor asked for "
            "the leg-B step count at which the R6c statistic falls to 5 %.  "
            "DERIVED ANSWER: NO FINITE COUNT.  That is not a refusal to compute "
            "it; it is what the computation returns.")

    # ---- WHAT rho WILL BE ------------------------------------------------
    r_post = (B["exec_at"][R6C_N_B] - B["exec_at"][D_EXCL_REG]) / (R6C_N_B - D_EXCL_REG)
    r_trans = B["exec_at"][D_EXCL_REG] / D_EXCL_REG
    rho_post = r_post / rA
    it_A_local = sum(A["iters"][k] for k in range(1, R6C_N_A + 1)) / R6C_N_A
    out["rho"] = dict(
        r_legA_s_per_step=rA, r_legB_all_steps=rB_all,
        r_legB_transient=r_trans, r_legB_post_transient=r_post,
        rho_all_steps=rB_all / rA, rho_post_transient=rho_post,
        drift_floor_pct_on_a_40step_window=post_sd / post_mean * 100.0,
        rho_post_transient_1sd_band=[rho_post * (1 - post_sd / post_mean),
                                     rho_post * (1 + post_sd / post_mean)],
        effect_over_floor=(rho_post - 1.0) / (post_sd / post_mean),
        rho_work=settled_iters / it_A_local,
        rho_throughput=rho_post / (settled_iters / it_A_local),
        which_is_graded_in_R2="THE POST-TRANSIENT ONE, and that is the STRICTER "
            "choice: excluding the %d cheap transient steps RAISES rho from "
            "%.6f to %.6f and so makes G-R2-2 (rho < 1) HARDER, not easier.  It "
            "is chosen on a physical argument fixed BEFORE the run, not from the "
            "answer: the ladder runs 8,300 leg-B steps, so a %d-step restart "
            "transient is %.2f %% of the mixture and the settled rate is the one "
            "that prices the ladder."
            % (D_EXCL_REG, rB_all / rA, rho_post, D_EXCL_REG, D_EXCL_REG / 8300.0 * 100.0),
        rho_work_note="rho_work = (settled leg-B iterations/step) / (leg-A "
            "iterations/step) is CONTENTION-FREE -- iteration counts do not "
            "depend on how busy the box is.  rho_throughput is what is left, and "
            "it is the machine.  Both are REPORTED in R2, GATING NOTHING: they "
            "are a new instrument and Sanaa's 2026-09-03 20:00Z default is "
            "reported-not-gated.  A raw iteration SUM mixes cheap DILUPBiCGStab "
            "sweeps with expensive GAMGPCG ones and the two legs need not share "
            "that mixture, so rho_work is NOT offered as a corrected rho.")

    # ---- COST, FROM THIS RUN'S OWN MEASURED PER-STEP RATES ----------------
    cpu_a = rA * R6C_N_A
    cpu_b_trans = r_trans * D_EXCL_REG
    cpu_b_post = r_post * (N_B - D_EXCL_REG)
    total_cpu = cpu_a + cpu_b_trans + cpu_b_post
    point = total_cpu * RANKS / 60.0
    r6c_actual = (A["exec_at"][R6C_N_A] + B["exec_at"][R6C_N_B]) * RANKS / 60.0
    out["cost"] = dict(
        point_core_min=point,
        point_is_a_point_not_an_inequality="L-463: a POINT estimate with a stated "
            "basis.  No inequality is offered as a cost.",
        basis="MEASURED, on T25R6c's own logs: leg A %d steps x %.6f s/step; leg "
              "B transient %d steps x %.6f s/step; leg B settled %d steps x "
              "%.6f s/step; x %d ranks / 60.  SAME case, SAME arm dictionary, "
              "SAME mesh, SAME rank count, SAME box.  Not scaled from another "
              "rung and not a rule of thumb."
              % (R6C_N_A, rA, D_EXCL_REG, r_trans, N_B - D_EXCL_REG, r_post, RANKS),
        breakdown_core_min=dict(legA=cpu_a * RANKS / 60.0,
                                legB_transient=cpu_b_trans * RANKS / 60.0,
                                legB_settled=cpu_b_post * RANKS / 60.0),
        t25R6c_actual_core_min=r6c_actual,
        ratio_R2_over_R6c=point / r6c_actual,
        usd_derived_not_measured=point / 60.0 * USD_PER_CORE_H,
        cost_basis="REPORTED-BY-OWNER; dollars DERIVED at $%.4f/core-h, NOT "
                   "MEASURED -- this box cannot read its own billing "
                   "(COMPUTE_BUDGET_CHARTER section 5)" % USD_PER_CORE_H,
        contention_caveat="These per-step rates were measured under the drift "
                          "quantified above (%.3f %% on a 40-step window).  The "
                          "point estimate carries that width and the cap is set "
                          "at ~3x, not at the width."
                          % (post_sd / post_mean * 100.0))

    # ---- CPU-vs-WALL: WHAT ExecutionTime ACTUALLY IS ----------------------
    out["ExecutionTime_is_cpu_time"] = dict(
        verdict="CPU TIME (user + system) OF THE CALLING PROCESS -- rank 0 only. "
                "NOT wall time and NOT a sum over ranks.",
        source_chain=[
            "OpenFOAM-v2606 src/OpenFOAM/db/Time/Time.H:533 -- '//- Print the "
            "elapsed ExecutionTime (cpu-time), ClockTime'",
            "src/OpenFOAM/db/Time/TimeIO.C:631 -- os << \"ExecutionTime = \" << "
            "elapsedCpuTime() << \" s\" << \"  ClockTime = \" << "
            "elapsedClockTime() << \" s\"",
            "src/OSspecific/POSIX/cpuTime/cpuTimeFwd.H -- typedef cpuTimePosix "
            "cpuTime  (this build selects the POSIX implementation)",
            "src/OSspecific/POSIX/cpuTime/cpuTimePosix.C:40-47 -- diff(a,b) = "
            "((a.tms_utime + a.tms_stime) - (b.tms_utime + b.tms_stime)) / "
            "sysconf(_SC_CLK_TCK), with value_type::update() calling ::times(this)",
        ],
        measured_ratio_legA=A["exec_at"][R6C_N_A] / A["clock_at"][R6C_N_A],
        measured_ratio_legB=B["exec_at"][R6C_N_B] / B["clock_at"][R6C_N_B],
        why_it_matters="A1.2(a) assumed a contended box INFLATES the measured "
            "rate.  For the DESCHEDULING pathway that is BACKWARDS: a process "
            "that loses the CPU accrues LESS cpu-time, not more.  The confound "
            "survives by two OTHER pathways, neither of which cpu-time filters: "
            "(i) memory-bandwidth and last-level-cache contention, which makes "
            "the same work cost more real cycles; (ii) MPI busy-wait -- rank 0 "
            "SPINS in a collective while a descheduled peer catches up, and the "
            "spin is charged to rank 0 as user cpu-time.  The measured "
            "ExecutionTime/ClockTime ratios above (%.4f leg A, %.4f leg B) are "
            "the spin-wait signature: a 2-rank job accruing cpu at ~99 %% of wall "
            "is either never descheduled or spinning when it is.",
        loadavg_did_not_establish_oversubscription="The A1.2(a) breaking condition "
            "fired on /proc/loadavg 51.80 -> 52.96 -> 58.34 on 16 cores.  Field 4 "
            "of the SAME witnesses read 9/625, 9/625 and 11/625 RUNNABLE tasks. "
            "Linux loadavg is a 1-minute EWMA that counts uninterruptible-sleep "
            "tasks as well as runnable ones, so it does not establish CPU "
            "oversubscription and 9-11 runnable against 16 cores does not either. "
            "THE WITNESS THAT FIRED THE CONDITION DOES NOT SUPPORT THE MECHANISM "
            "IT WAS READ AS EVIDENCE FOR.",
        what_is_still_confounded="The %.3f %% window-rate scatter measured above, "
            "at CONSTANT solver work (%d iterations/step to %.3f %%).  That is "
            "the machine, it is real, and cpu-time accounting does not remove it. "
            "A rho measurement finer than about +/-%.1f %% IS NOT ACHIEVABLE ON "
            "THIS SHARED BOX at these window lengths, and R2 registers that "
            "rather than hoping otherwise."
            % (post_sd / post_mean * 100.0, settled_iters,
               (max(tail) - min(tail)) / (sum(tail) / len(tail)) * 100.0,
               post_sd / post_mean * 100.0),
        ranks_multiplier_is_an_assumption="core-min = ExecutionTime x 2 / 60 "
            "assumes rank 1 burns the same cpu as rank 0.  ExecutionTime cannot "
            "see rank 1.  This is the lab's established basis for this rung and "
            "R2 keeps it UNCHANGED so R2 and R6c stay comparable -- but it is an "
            "ASSUMPTION and is named here as one.")

    # ---- THE WRITE CONTROL, VERIFIED FROM SOURCE AND SIMULATED ------------
    out["write_control"] = write_control_check(N_B)

    p = os.path.join(HERE, "DESIGN_DERIVATION.json")
    json.dump(out, open(p, "w"), indent=2, sort_keys=True, default=str)
    print(json.dumps({k: v for k, v in out.items()
                      if k not in ("source_logs", "planted_zero_on_this_readers_own_instrument")},
                     indent=2, sort_keys=True, default=str))
    print("\nwritten %s" % p)
    return 0


# ----------------------------------------------------------------------------
# THE WRITE CONTROL -- the T25R6c defect, and the fix, CHECKED not assumed
# ----------------------------------------------------------------------------

def write_control_check(N_B, dt=0.1, t0=0.8, interval=None):
    """Step the EXACT arithmetic of OpenFOAM-v2606 Time.C:1117-1131 over the
    registered leg-B schedule and report which steps write.

    THE T25R6c DEFECT: `writeControl timeStep` tests
        writeTime_ = !(timeIndex_ % label(writeInterval_))
    and timeIndex_ is the GLOBAL time index, which does NOT reset across a
    `startFrom latestTime` restart.  Leg A had already advanced it to 40, so
    writeInterval 400 fired at global index 400 = leg-B step 360, t = 36.8 -- and
    NOTHING wrote at the registered endTime 40.8.  The run directory carries
    36.8/ and no 40.8/, and the frozen grader's rule 4 returned
    "t=40.8 field dir: 0 found".

    THE FIX: `writeControl runTime`.  Its index is computed RELATIVE TO
    startTime_, which `startFrom latestTime` sets to the restart time
    (Time.C:180-183), so it is INDEPENDENT OF LEG A'S STEP COUNT ENTIRELY.
    The rejected alternative -- keeping timeStep and setting writeInterval to
    N_A + N_B -- would leave exactly the same fragility in place: change leg A's
    length and the write silently moves again.  A fix that still depends on the
    quantity that broke it is not a fix."""
    interval = interval if interval is not None else N_B * dt
    writes, write_time_index, t = [], 0, t0
    for step in range(1, N_B + 1):
        t = t0 + step * dt                     # value() after the increment
        idx = int(((t - t0) + 0.5 * dt) / interval)     # label() truncates
        if idx > write_time_index:
            write_time_index = idx
            writes.append(dict(step=step, t=round(t, 10)))
    end_t = t0 + N_B * dt
    # the timeStep control that broke T25R6c, simulated on the SAME schedule
    ts_writes = [s for s in range(1, N_B + 1) if (40 + s) % (N_B) == 0]
    return dict(
        chosen="writeControl runTime; writeInterval %g;" % interval,
        endTime_B=end_t,
        simulated_writes=writes,
        n_writes=len(writes),
        writes_exactly_once_at_endTime=bool(len(writes) == 1
                                            and abs(writes[0]["t"] - end_t) < 1e-9),
        arithmetic_transcribed_from="OpenFOAM-v2606 src/OpenFOAM/db/Time/Time.C:"
            "1117-1131, wcRunTime branch: writeIndex = label(((value() - "
            "startTime_) + 0.5*deltaT_) / writeInterval_); write iff writeIndex > "
            "writeTimeIndex_.  writeTimeIndex_ is initialised to 0 at "
            "src/OpenFOAM/db/Time/TimeState.C:38.  startTime_ is set to the "
            "restart time by `startFrom latestTime` at Time.C:180-183.",
        half_step_tolerance_note="The + 0.5*deltaT_ term is why runTime is robust "
            "to accumulated floating-point drift in value(): the index still "
            "crosses even if the final time lands at %g - epsilon.  `timeStep` "
            "has no such tolerance and no such independence from leg A." % end_t,
        rejected_alternative=dict(
            what="writeControl timeStep; writeInterval %d;" % (40 + N_B),
            simulated_writes_at_leg_B_step=ts_writes,
            why_rejected="It works only by arithmetic coincidence with leg A's "
                         "step count, which is the exact quantity that caused the "
                         "T25R6c defect.  Change leg A and the write moves again, "
                         "silently.  runTime does not depend on leg A at all."),
        still_a_prediction="This is a SOURCE-VERIFIED SIMULATION of the branch, "
            "not a run of the solver.  It is registered as PREDICTION P-R2-6 and "
            "the R2 grader's rule 4 MEASURES it: exactly one field directory at "
            "t = %g, or NOT A RESULT." % end_t)


def selftest():
    fails = [0]

    def chk(what, ok):
        print("  %-72s %s" % (what[:72], "ok" if ok else "FAIL"))
        if not ok:
            fails[0] += 1

    print("T25R6c-R2 DESIGN DERIVATION SELFTEST")
    print("-" * 80)

    # --- the write-control simulation must reproduce the T25R6c DEFECT -------
    bad = write_control_check(400, interval=None)
    chk("runTime at the R6c geometry writes exactly once, at t = 40.8",
        bad["writes_exactly_once_at_endTime"] and abs(bad["endTime_B"] - 40.8) < 1e-9)
    # the timeStep control as T25R6c actually set it: writeInterval 400, global
    # index offset 40.  It must reproduce the OBSERVED failure: a write at leg-B
    # step 360 (t = 36.8) and NONE at 40.8.
    ts = [s for s in range(1, 401) if (40 + s) % 400 == 0]
    chk("the timeStep control T25R6c used fires at leg-B step 360, t = 36.8",
        ts == [360] and abs(0.8 + 360 * 0.1 - 36.8) < 1e-9)
    chk("...and NEVER at the registered endTime 40.8 -- the observed defect, "
        "reproduced", 400 not in ts)

    # --- a MUTATION must flip it --------------------------------------------
    m = write_control_check(400, interval=13.0)
    chk("A MUTATION FLIPS THE ANSWER: writeInterval 13 writes %d times, not once"
        % m["n_writes"], m["n_writes"] > 1 and not m["writes_exactly_once_at_endTime"])

    # --- float drift must not defeat the half-step tolerance ----------------
    drift = write_control_check(900, dt=0.1, t0=0.8, interval=90.0)
    chk("the R2 geometry (900 steps, interval 90) writes exactly once at 90.8",
        drift["writes_exactly_once_at_endTime"])

    # --- the transient locator must find a planted boundary -----------------
    it = {k: (50 if k <= 17 else 93) for k in range(1, 401)}
    s, band, _ = find_transient_end(it, 400)
    chk("the transient locator finds a PLANTED work boundary at step 18",
        s == 18 and band == (92.0, 94.0))
    it2 = {k: 93 for k in range(1, 401)}
    s2, _, _ = find_transient_end(it2, 400)
    chk("...and returns step 1 when there is NO transient (no boundary invented)",
        s2 == 1)
    # A PLANTED LATE EXCURSION must push the boundary out -- the locator must not
    # report 'settled' over a region the work later leaves.
    it3 = {k: (93 if k != 250 else 400) for k in range(1, 401)}
    s3, _, _ = find_transient_end(it3, 400)
    chk("A MUTATION FLIPS IT: one planted late excursion at step 250 moves the "
        "boundary to 251", s3 == 251)

    # --- the window rate must be a telescoping difference -------------------
    ea = {k: 0.5 * k for k in range(1, 101)}
    ws = window_rates(ea, 1, 100, 20)
    chk("a 0.50 s/step synthetic reads back at 0.50 in every 20-step window",
        len(ws) == 5 and all(abs(w - 0.5) < 1e-12 for w in ws))
    ws2 = window_rates(ea, 41, 100, 20)
    chk("windows starting mid-log subtract the correct predecessor",
        len(ws2) == 3 and all(abs(w - 0.5) < 1e-12 for w in ws2))

    # --- the power-law solve must invert itself -----------------------------
    inter, p = math.log(3.6), 0.18
    need = 100.0 * PLATEAU_TOL / Z_TARGET / math.sqrt(2.0)
    w = math.exp((inter - math.log(need)) / p)
    chk("the W_half solve inverts its own power law to 1e-9",
        abs(math.exp(inter) * w ** (-p) - need) < 1e-9)

    chk("no bare `assert` is used as a control (python3 -O strips them)",
        not re.search(r"^\s*assert\b", open(os.path.abspath(__file__),
                                            errors="replace").read(), re.M))
    print("\nSELFTEST %s (%d failed)" % ("PASS" if not fails[0] else "FAIL", fails[0]))
    return 0 if not fails[0] else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(derive())
