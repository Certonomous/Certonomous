#!/usr/bin/env python3
"""monitor_k2g.py -- K2g L3 per-iteration monitor and registered stop rules.

    python3 monitor_k2g.py <case_dir> <ranks> <point_core_min> <cap_core_min>

WHAT IT WRITES, PER ITERATION (Sanaa's 2026-09-12 directive item 11)
-------------------------------------------------------------------
One row per solver iteration into `<case>/MONITOR.K2f_L3.tsv`:

    iter  wall_s  s_per_iter  core_min  core_min_per_iter  pct_of_POINT
    pct_of_CAP  res_Ux  res_Uy  res_Uz  res_T  res_p_rgh  res_k  res_omega
    dp_module  dp_tile  dp_return

  * residuals per equation -- the FIRST initial residual of each equation in
    the iteration (for p_rgh that is the first pressure corrector, which is
    what analyse_k2g.py's D-CONV grades);
  * the GRADED QUANTITY, DP_module = areaAvg(p_rgh, tile) - areaAvg(p_rgh,
    return), from the dp_tile/dp_return function objects.  THIS IS A MONITOR
    CHANNEL AND IS NEVER A GRADING INPUT -- the graded value is read from the
    field files by the frozen `foam_patch_reader.area_average`;
  * cost per iteration in core-minutes, the lab's unit (wall s x ranks / 60);
  * wall time against the REGISTERED estimate, as a percentage of POINT 598
    and of the registered CAP 1200 core-min.

IT IS PARENTED TO INIT, NOT TO AN AGENT
---------------------------------------
`resume_k2g.sh` starts it under `setsid`.  A watcher armed inside an agent dies
with the agent -- the lab paid for that lesson, and a report that says "waiting
on my monitor" is the dead-agent tell.  This process outlives the fleet, a
supervisor ending and an ssh close.  It polls the log; it holds no pipe to the
solver, so nothing it does can stall a rank.

HOW IT STOPS A RUN -- AND WHY IT NEVER KILLS ONE
------------------------------------------------
A stop is signalled by TOUCHING `<case>/ABORT`.  The `stop_on_rule` function
object (type `abort`, action `writeNow`) then makes the solver WRITE ITS FIELDS
and end itself cleanly at the end of the current iteration.  No signal is sent
to any rank.  That matters here specifically: the pre-reboot run died because
its wrapper took SIGKILL and left four orphaned ranks running for 12.9 hours.

THE REGISTERED STOP RULES (directive item 12)
---------------------------------------------
  R1  RESIDUAL GROWTH -- mean(last 100)/min(last 400) > 2.0 on any of Ux, T or
      p_rgh.  The threshold is analyse_k2g.py's own RES_RISE_MAX, so the monitor
      stops on exactly the condition the comparator would later refuse on.
  R2  FIELD OUT OF BOUNDS -- any residual nan/inf, or |DP_module| > 1000 m2/s2
      (36x the two measured levels).
  R3  PLATEAU WITH A STALLED LINEAR SOLVER -- DP_module drift over the last 500
      iterations below 1e-5 WHILE the p_rgh solver is at its iteration cap.
      Stop and CLIMB THE LADDER: mesh -> numerics -> model.
  R4  COHERENT OSCILLATION in DP_module -- >= 6 sign changes of the increment
      over the last 300 iterations with peak-to-peak above 1e-2 m2/s2.  Mark
      "physics voting unsteady"; the steady SIMPLE solve is the wrong instrument.

ONE REGISTERED CHANGE PER RUN, NEVER THE SAME ACTION TWICE ON THE SAME STATE
(item 13): every fired rule is appended to `ACTION_HISTORY.K2f_L3.tsv`, and a
rule that has already fired in this run NEVER fires again.

THE CAP IS A FLAG, NOT A STOP
-----------------------------
Crossing the registered 1200 core-min writes `CAP_FLAG.txt` with the evidence
and CHANGES NOTHING ELSE.  Sanaa's 2026-09-12 04:20Z directive #17: no run is
stopped by a time or budget cap.  The consequence of a crossed cap is a VERDICT
consequence at grade time, not a killed process, and raising a cap is Sanaa's
alone.
"""

import math
import os
import re
import sys
import time

POLL_S = 10.0
RES_RISE_MAX = 2.0          # analyse_k2g.py's own registered value
DP_ABS_MAX = 1000.0         # m2/s2; the two measured levels are ~27.2 and ~27.7
R3_WINDOW = 500
R3_DRIFT = 1.0e-5
R4_WINDOW = 300
R4_SIGN_CHANGES = 6
R4_AMPLITUDE = 1.0e-2

EQ = ("Ux", "Uy", "Uz", "T", "p_rgh", "k", "omega")

_TIME = re.compile(r"^Time = (\d+)")
_RES = re.compile(r"Solving for (\w+),\s+Initial residual = ([0-9.eE+-]+),"
                  r"\s+Final residual = ([0-9.eE+-]+),\s+No Iterations (\d+)")
_END = re.compile(r"^End\b")


def _dp_series(case):
    """(time -> value) for the dp_tile and dp_return function objects.

    Read from the function-object output.  Returns ({}, {}) before the first
    write, which is normal and is not an error.
    """
    out = {}
    for name in ("dp_tile", "dp_return"):
        vals = {}
        root = os.path.join(case, "postProcessing", name)
        if os.path.isdir(root):
            for sub in sorted(os.listdir(root)):
                f = os.path.join(root, sub, "surfaceFieldValue.dat")
                if not os.path.exists(f):
                    continue
                for line in open(f, errors="replace"):
                    if line.startswith("#"):
                        continue
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            vals[int(float(parts[0]))] = float(parts[1])
                        except ValueError:
                            pass
        out[name] = vals
    return out["dp_tile"], out["dp_return"]


def _fire(case, rule, detail):
    """Signal a CLEAN stop. Touch ABORT; the solver writes and ends itself."""
    hist = os.path.join(case, "ACTION_HISTORY.K2f_L3.tsv")
    new = not os.path.exists(hist)
    with open(hist, "a") as fh:
        if new:
            fh.write("utc\trule\taction\tdetail\n")
        fh.write("%s\t%s\tABORT_writeNow\t%s\n"
                 % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), rule, detail))
    with open(os.path.join(case, "STOP_RULE_FIRED.%s.txt" % rule), "w") as fh:
        fh.write("%s\nRULE %s FIRED\n%s\n\nThe solver was NOT killed. `ABORT` was "
                 "touched and the `stop_on_rule` function object (action writeNow) "
                 "makes the solver write its fields and end itself at the end of the "
                 "current iteration.\n"
                 % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), rule, detail))
    open(os.path.join(case, "ABORT"), "w").write("action=writeNow\n")


def main(argv):
    # The optional 5th argument is a comma-separated list of rule ids to SUSPEND.
    # It is ADDITIVE and defaults to suspending NOTHING, so every existing call
    # site -- resume_k2g.sh's included -- keeps every rule with no change, and
    # nothing about the K2g run this instrument already stopped is altered: its
    # ACTION_HISTORY, STOP_RULE_FIRED.R4.txt and MONITOR tsv are on disk and are
    # untouched. A suspension must be REGISTERED in a pre-registration before the
    # solver starts; it is not an operator convenience, and the monitor records
    # the suspension beside the run so a reader sees which rules were NOT armed.
    if len(argv) not in (4, 5):
        print(__doc__)
        return 2
    case, ranks = os.path.abspath(argv[0]), int(argv[1])
    point, cap = float(argv[2]), float(argv[3])
    suspended = set()
    if len(argv) == 5:
        suspended = {a.strip().upper() for a in argv[4].split(",") if a.strip()}
    if suspended:
        with open(os.path.join(case, "RULES_SUSPENDED.txt"), "w") as fh:
            fh.write("%s\nRULES NOT ARMED FOR THIS RUN: %s\n\nA suspended rule "
                     "cannot fire and cannot stop this run. This file exists so a "
                     "reader of the run sees the absence, rather than inferring "
                     "from silence that every rule was armed and none fired.\n"
                     % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        ", ".join(sorted(suspended))))
    log = os.path.join(case, "log.solve")
    tsv = os.path.join(case, "MONITOR.K2f_L3.tsv")

    t0 = None
    for _ in range(60):
        p = os.path.join(case, ".resume_t0")
        if os.path.exists(p):
            try:
                t0 = float(open(p).read().strip())
                break
            except ValueError:
                pass
        time.sleep(1.0)
    if t0 is None:
        t0 = time.time()

    with open(tsv, "w") as fh:
        fh.write("iter\twall_s\ts_per_iter\tcore_min\tcore_min_per_iter\t"
                 "pct_of_POINT\tpct_of_CAP\t"
                 + "\t".join("res_" + e for e in EQ)
                 + "\tdp_module\tdp_tile\tdp_return\tp_rgh_linear_iters\n")

    series = {e: [] for e in EQ}
    dp_hist = []            # (iter, dp)
    prgh_iters = []
    fired = set()
    capped = False
    pos, cur, seen_res, prgh_it, last_iter, finished = 0, None, {}, None, 0, False

    while True:
        try:
            size = os.path.getsize(log)
        except OSError:
            time.sleep(POLL_S)
            continue
        if size > pos:
            with open(log, errors="replace") as fh:
                fh.seek(pos)
                chunk = fh.read()
                pos = fh.tell()
            dpt, dpr = _dp_series(case)
            rows = []
            for line in chunk.splitlines():
                m = _TIME.match(line)
                if m:
                    if cur is not None and seen_res:
                        rows.append((cur, dict(seen_res), prgh_it))
                    cur, seen_res, prgh_it = int(m.group(1)), {}, None
                    continue
                if _END.match(line):
                    finished = True
                    continue
                r = _RES.search(line)
                if r and cur is not None:
                    name, ini, nit = r.group(1), r.group(2), int(r.group(4))
                    if name not in seen_res:      # FIRST corrector only
                        try:
                            seen_res[name] = float(ini)
                        except ValueError:
                            seen_res[name] = float("nan")
                        if name == "p_rgh":
                            prgh_it = nit
            if cur is not None and seen_res and finished:
                rows.append((cur, dict(seen_res), prgh_it))

            now = time.time()
            with open(tsv, "a") as fh:
                for it, res, nit in rows:
                    if it <= last_iter:
                        continue
                    last_iter = it
                    wall = now - t0
                    spi = wall / max(1, it - 500)
                    cm = wall * ranks / 60.0
                    cmpi = cm / max(1, it - 500)
                    dp_t, dp_r = dpt.get(it), dpr.get(it)
                    dp = (dp_t - dp_r) if (dp_t is not None and dp_r is not None) else None
                    if dp is not None:
                        dp_hist.append((it, dp))
                    if nit is not None:
                        prgh_iters.append(nit)
                    for e in EQ:
                        if e in res:
                            series[e].append(res[e])
                    fh.write("%d\t%.1f\t%.3f\t%.3f\t%.5f\t%.2f\t%.2f\t%s\t%s\t%s\t%s\t%s\n"
                             % (it, wall, spi, cm, cmpi, 100.0 * cm / point,
                                100.0 * cm / cap,
                                "\t".join("%.6g" % res[e] if e in res else "-" for e in EQ),
                                "%.9g" % dp if dp is not None else "-",
                                "%.9g" % dp_t if dp_t is not None else "-",
                                "%.9g" % dp_r if dp_r is not None else "-",
                                nit if nit is not None else "-"))
            fh_cm = (time.time() - t0) * ranks / 60.0

            # ---- the cap is a FLAG, not a stop (directive #17) -------------
            if fh_cm > cap and not capped:
                capped = True
                with open(os.path.join(case, "CAP_FLAG.txt"), "w") as f2:
                    f2.write("%s\nREGISTERED CAP %g core-min CROSSED at iteration %d "
                             "(%.1f core-min charged).\nTHE RUN IS NOT STOPPED: Sanaa's "
                             "2026-09-12 04:20Z directive #17 -- no run is stopped by a "
                             "time or budget cap. The consequence is a VERDICT "
                             "consequence at grade time (K2g section 7: cap -> NOT A "
                             "RESULT, never raised), and raising a cap is Sanaa's alone.\n"
                             % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                cap, last_iter, fh_cm))

            # ---- the registered stop rules -------------------------------
            # R2 first: an out-of-bounds field is the cheapest thing to be sure of.
            if "R2" not in fired:
                bad = [e for e in ("Ux", "T", "p_rgh")
                       if series[e] and not math.isfinite(series[e][-1])]
                if bad:
                    fired.add("R2")
                    _fire(case, "R2", "non-finite residual on %s at iteration %d"
                          % (", ".join(bad), last_iter))
                elif dp_hist and abs(dp_hist[-1][1]) > DP_ABS_MAX:
                    fired.add("R2")
                    _fire(case, "R2", "DP_module = %.6g at iteration %d is outside the "
                          "registered bound %g m2/s2 (the two measured levels are 27.189 "
                          "and 27.730)" % (dp_hist[-1][1], last_iter, DP_ABS_MAX))

            if "R1" not in fired:
                for e in ("Ux", "T", "p_rgh"):
                    v = series[e]
                    if len(v) >= 400:
                        mn = min(v[-400:])
                        if mn > 0:
                            rise = (sum(v[-100:]) / 100.0) / mn
                            if rise > RES_RISE_MAX:
                                fired.add("R1")
                                _fire(case, "R1", "%s is RISING: mean(last 100)/min(last "
                                      "400) = %.3f above the registered %.2f at iteration "
                                      "%d -- this is exactly the condition analyse_k2g.py "
                                      "D-CONV would refuse on" % (e, rise, RES_RISE_MAX,
                                                                  last_iter))
                                break

            if "R3" not in fired and len(dp_hist) >= R3_WINDOW and len(prgh_iters) >= 100:
                win = [d for _i, d in dp_hist[-R3_WINDOW:]]
                drift = max(win) - min(win)
                stalled = sum(1 for n in prgh_iters[-100:] if n >= 1000)
                if drift < R3_DRIFT and stalled >= 90:
                    fired.add("R3")
                    _fire(case, "R3", "PLATEAU WITH A STALLED LINEAR SOLVER: DP_module "
                          "moved %.3g over the last %d iterations while the p_rgh solver "
                          "hit its iteration cap in %d of the last 100. CLIMB THE LADDER: "
                          "mesh -> numerics -> model. Do not relax the solver."
                          % (drift, R3_WINDOW, stalled))

            if "R4" not in fired and "R4" not in suspended and len(dp_hist) >= R4_WINDOW:
                win = [d for _i, d in dp_hist[-R4_WINDOW:]]
                inc = [b - a for a, b in zip(win, win[1:])]
                flips = sum(1 for a, b in zip(inc, inc[1:]) if a * b < 0)
                amp = max(win) - min(win)
                if flips >= R4_SIGN_CHANGES and amp > R4_AMPLITUDE:
                    fired.add("R4")
                    _fire(case, "R4", "COHERENT OSCILLATION in the graded quantity: %d "
                          "sign changes over %d iterations, peak-to-peak %.4g m2/s2. "
                          "PHYSICS VOTING UNSTEADY -- a steady SIMPLE solve is the wrong "
                          "instrument for this state." % (flips, R4_WINDOW, amp))

        if finished:
            with open(os.path.join(case, "MONITOR_DONE.txt"), "w") as fh:
                fh.write("%s\nlast iteration %d; `End` seen in log.solve; "
                         "%.3f core-min charged (%.1f%% of POINT %g, %.1f%% of CAP %g)\n"
                         % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), last_iter,
                            (time.time() - t0) * ranks / 60.0,
                            100.0 * (time.time() - t0) * ranks / 60.0 / point, point,
                            100.0 * (time.time() - t0) * ranks / 60.0 / cap, cap))
            return 0
        time.sleep(POLL_S)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
