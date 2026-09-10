#!/usr/bin/env python3
"""t4e_rate_watch.py -- MEASURE the T4e per-leg solve rate against its REGISTERED
cost basis, and record the projection.  DIAGNOSTIC OF COST ONLY.

WHAT THIS IS AND IS NOT.  This script grades NOTHING.  It touches no gate, no
threshold, no band and no verdict; it does not write or move a DONE marker; it
cannot stop a solver.  It exists because T4e's registered cost basis is T4d's
measured core-min, and whether that basis holds on THIS rung is a rule-12
question that must be answered from a measurement, early, while the answer can
still change a decision.  Its output is a measured record, and it is BINDING as
evidence about cost -- it is not annotated away as "informational".

WHY THE RECENT-WINDOW RATE AND NOT THE CUMULATIVE RATE.  A solve's cumulative
average it/s is inflated by its own startup transient and therefore OVERSTATES
the remaining cost.  Measured on this rung's coarse leg: at 6,139 steps the
cumulative rate read 13.695 it/s while the recent-window rate read 23.060 it/s
against a T4d-implied 23.077 -- the cumulative figure was wrong by 1.68x and the
recent-window figure was right to 0.07 %.  A projection from the cumulative rate
would have reported a 5x cost blowout that does not exist.  So the rate is taken
over the most recent quarter of recorded steps, and the number of steps that
window rests on is PRINTED BESIDE IT, because the coarse leg needed ~1,500 steps
before its recent rate settled onto the basis.  A projection from a window of
tens of steps is reported WITH THAT FACT, never as a settled figure.

Exec/Clock is printed per leg: it separates descheduling (CPU starvation, which
this box's load can cause) from a genuine per-step rate difference.  A ratio near
1.0 means the process is getting its core and the rate difference is real.
Memory-bandwidth contention is NOT separable from the rate with these artifacts
and is therefore carried inside the rate rather than quoted as a number this box
cannot measure.
"""
import re, os, sys, json, time, datetime

RUNS = os.path.dirname(os.path.abspath(__file__))
# Registered figures, transcribed from docs/campaigns/T-family/T4e_PREREGISTRATION.md
# section 9 ("Cost -- rule 12, from T4d's OWN CLEAN MEASURED core-min").  POINT is
# that table's value; CEILING = 1.5 x POINT and CAP = 2 x POINT are that section's
# own stated rule.  NOTHING HERE MAY BE EDITED TO FIT A MEASUREMENT.
REG = {
    "T4e_IJ_c": dict(end=30000,  point=21.667,  t4d_cm_per_it=21.667/30000),
    "T4e_IJ_m": dict(end=60000,  point=206.100, t4d_cm_per_it=206.100/60000),
    "T4e_IJ_f": dict(end=160000, point=3000.6,  t4d_cm_per_it=1200.233/64000),
}
for v in REG.values():
    v["ceiling"] = 1.5 * v["point"]
    v["cap"]     = 2.0 * v["point"]

# Steps a recent-window rate needs before its projection is worth a verdict.
# MEASURED on this rung's own coarse leg (see project()): contamination is 2.51x
# at 1500 steps, 1.30x at 2500 and 1.00x by 9000.  2500 is where the calibrator
# first came within 30 % of its settled rate.
SETTLE_STEPS = 2500

# The calibrator's own measured startup contamination, (step, settled/recent),
# read back from T4e_IJ_c's log -- the leg that finished within 3 % of the
# registered basis.  Used ONLY to tell a reader what an early rate is worth; it
# never adjusts a reported measurement and never issues a verdict.
CALIBRATOR_CONTAMINATION = [(107, 3.86), (200, 4.16), (400, 4.95), (733, 3.42),
                            (1000, 2.96), (1500, 2.51), (2500, 1.30),
                            (5000, 1.08), (9000, 1.00)]

def calibrator_gap(steps):
    """How far below its settled rate the ON-BUDGET calibrator leg read at
    `steps`.  Nearest tabulated step; the table is measured, not modelled."""
    return min(CALIBRATOR_CONTAMINATION, key=lambda r: abs(r[0] - steps))[1]

STEP = re.compile(r'^Time = ([\d.]+).*?ExecutionTime = ([\d.]+) s\s+ClockTime = (\d+) s',
                  re.M | re.S)

def read_leg(case):
    """Return the per-step (Time, ExecutionTime, ClockTime) records for one leg.

    Reads ONE NAMED ARTIFACT, log.solve -- never a glob.  A glob has no defined
    last member: `grep ... log.* | tail -1` returns a different file per run on
    this box (ugrep emits per-file output in thread-completion order), and its
    failure signature is a healthy run reported as stalled.  Named file only.
    """
    p = os.path.join(RUNS, case, "log.solve")
    if not os.path.exists(p):
        return None
    with open(p, errors="replace") as fh:
        return [(float(a), float(b), float(c)) for a, b, c in STEP.findall(fh.read())]

def project(case, recs):
    r = REG[case]
    if not recs:
        return dict(case=case, state="NO STEP RECORD YET")
    t, ex, cl = recs[-1]
    k = max(2, len(recs) // 4)
    t0, e0, _ = recs[-k]
    win_steps = t - t0
    win_secs  = ex - e0
    if win_secs <= 0:
        return dict(case=case, state="WINDOW HAS ZERO ELAPSED TIME")
    inst = win_steps / win_secs
    cum  = t / ex if ex > 0 else 0.0
    basis_rate = 1.0 / (r["t4d_cm_per_it"] * 60.0)
    remaining_s = (r["end"] - t) / inst
    total_cm = (ex + remaining_s) / 60.0
    # ------------------------------------------------------------------------
    # REFUSE RATHER THAN DEGRADE.  A cost verdict is emitted ONLY from a settled
    # window.  This is not caution for its own sake -- it is a measured
    # correction to this script's first version, which DID emit a verdict from an
    # unsettled window and produced a false "CAP BREACHED" on two legs.
    #
    # THE MEASUREMENT THAT FORCED THIS CHANGE.  The coarse leg ends up matching
    # the registered T4d basis to 3 % (23.71 measured vs 23.077 implied).  Its
    # OWN recent-window rate, read back from its own log at low step counts, was
    # low by 3.86x at step 107, 4.95x at step 400, 3.42x at step 733, 2.96x at
    # step 1000, 2.51x at 1500, 1.30x at 2500 and 1.00x by 9000.  So a rate read
    # before ~2500 steps understates the settled rate by roughly 2.5-5x ON A LEG
    # THAT IS PERFECTLY ON BUDGET.  Projecting a cost from it manufactures a cap
    # breach out of nothing.  Measured against that envelope, the medium leg's
    # 2.95x gap at step 733 is BETTER than the coarse leg's own 3.42x at the same
    # step, and the fine leg's 4.22x at step 107 is the same order as the coarse
    # leg's 3.86x there -- i.e. both were INSIDE the startup envelope while being
    # reported as cap breaches.
    #
    # So: below SETTLE_STEPS this function reports the measurement and REFUSES
    # the verdict, and it prints the calibrator's contamination at the same step
    # count beside it so a reader can see what the number is worth.  It does not
    # annotate a misleading verdict as "diagnostic only" and leave it standing --
    # a printed verdict labelled non-binding is worse than one not computed.
    # ------------------------------------------------------------------------
    if win_steps < SETTLE_STEPS:
        verdict = ("NO COST VERDICT -- window not settled (%d steps < %d). The "
                   "calibrator leg was itself low by ~%.2fx at this step count "
                   "while finishing ON BUDGET, so a projection here is not "
                   "evidence of an overrun." % (win_steps, SETTLE_STEPS,
                                                calibrator_gap(win_steps)))
    elif total_cm <= r["ceiling"]: verdict = "WITHIN CEILING"
    elif total_cm <= r["cap"]:     verdict = "CEILING BREACHED, UNDER CAP"
    else:                          verdict = "CAP BREACHED -- projected to be SIGTERMed short of endTime"
    return dict(
        case=case, state="MEASURED",
        step=t, end=r["end"], frac_done=t / r["end"],
        execution_time_s=ex, exec_over_clock=(ex / cl if cl else None),
        rate_recent_it_s=inst, rate_window_steps=win_steps,
        rate_cumulative_it_s=cum,
        rate_t4d_basis_it_s=basis_rate,
        rate_ratio_basis_over_recent=(basis_rate / inst if inst else None),
        projected_total_core_min=total_cm,
        registered_point=r["point"], registered_ceiling=r["ceiling"], registered_cap=r["cap"],
        projected_over_point=total_cm / r["point"],
        projected_over_ceiling=total_cm / r["ceiling"],
        projected_over_cap=total_cm / r["cap"],
        cost_verdict=verdict,
        cost_verdict_issued=(win_steps >= SETTLE_STEPS),
        calibrator_contamination_at_this_step=calibrator_gap(win_steps),
        window_caveat=("SETTLED: the window rests on >=1500 steps, which is where "
                       "this rung's coarse leg converged onto its basis"
                       if win_steps >= 1500 else
                       "NOT SETTLED: the window rests on %d steps; the coarse leg "
                       "needed ~1500 before its recent rate matched the basis, so "
                       "this projection is expected to IMPROVE and must not be "
                       "quoted as final" % int(win_steps)),
    )

def main():
    interval = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    stop_after = int(sys.argv[2]) if len(sys.argv) > 2 else 24 * 3600
    out = os.path.join(RUNS, "T4E_RATE_PROJECTION.json")
    log = os.path.join(RUNS, "T4E_RATE_WATCH.log")
    t_start = time.time()
    while time.time() - t_start < stop_after:
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        rows = [project(c, read_leg(c)) for c in REG]
        rec = dict(measured_at_utc=stamp,
                   note=("MEASURED cost diagnostic, not a grade. Grades nothing, "
                         "moves no marker, stops no solver."),
                   legs=rows)
        with open(out, "w") as fh:
            json.dump(rec, fh, indent=2)
        with open(log, "a") as fh:
            fh.write("== %s\n" % stamp)
            for r in rows:
                if r.get("state") != "MEASURED":
                    fh.write("   %-10s %s\n" % (r["case"], r["state"])); continue
                settled = r["rate_window_steps"] >= SETTLE_STEPS
                fh.write("   %-10s step %7d/%7d (%5.1f%%)  recent %7.3f it/s over %5d steps  "
                         "basis %7.3f it/s (basis/recent %.2fx)  Exec/Clock %.4f\n"
                         % (r["case"], r["step"], r["end"], 100*r["frac_done"],
                            r["rate_recent_it_s"], r["rate_window_steps"],
                            r["rate_t4d_basis_it_s"], r["rate_ratio_basis_over_recent"],
                            r["exec_over_clock"]))
                if settled:
                    fh.write("              proj %9.1f core-min = %.2fx POINT %.2fx CEILING "
                             "%.3fx CAP  -> %s\n"
                             % (r["projected_total_core_min"], r["projected_over_point"],
                                r["projected_over_ceiling"], r["projected_over_cap"],
                                r["cost_verdict"]))
                else:
                    fh.write("              %s\n"
                             "              (unsettled projection, recorded but NOT a cost "
                             "verdict: %.1f core-min = %.3fx CAP)\n"
                             % (r["cost_verdict"], r["projected_total_core_min"],
                                r["projected_over_cap"]))
        # stop early once every live leg has settled AND been recorded
        time.sleep(interval)

if __name__ == "__main__":
    main()
