#!/usr/bin/env python3
r"""CASE PROTOCOL -- STAGE 4 MONITOR.  The five fixed stops and their one registered action.

AUTHORITY.  CASE_PROTOCOL_CHARTER v1.0 section 4, verbatim.  Monitor conventions, fixed:
    "residual targets per equation, absolute bounds on fields, stationarity of the graded
     quantity over its window, linear-solver saturation, cost per iteration against the
     estimate, wall time against the cap."
Monitor actions, fixed and pre-registered:
    S1 residual growth past the bound, or a field outside its bounds: stop.
    S2 plateau above target with a stalled linear solver: stop.
    S3 coherent oscillation with a fixed period in the graded quantity: stop, mark
       "physics voting unsteady."
    S4 cost per iteration beyond twice the estimate: stop, mark machine or case cause.
    S5 cap reached: stop, NOT A RESULT, never a raised cap.
And: "One change per run.  NEVER THE SAME ACTION TWICE ON THE SAME STATE.  Two stops on
the same cause: climb the ladder.  Ladder exhausted: park as NOT A RESULT."

THE LADDER IS SECTION 4's OWN, NOT SECTION 3's.  Section 4 names it explicitly --
"continuation from a converged neighbor, relaxation reduction, pseudo-transient, then
transient re-registration".  Section 3's "mesh, then numerics, then model" is the SMOKE
ladder and is a different ladder for a different stage; using it on a stage-4 monitor stop
would climb a rung against a case whose mesh is not what stopped.

TWO THINGS THIS MONITOR MEASURES THAT THE FIVE CLASSES DO NOT COVER, reported as
UNCLASSED rather than forced into a class that does not fit:
  * a residual STALLED ABOVE TARGET while the graded quantity is still MARCHING.  Section
    4 monitors "stationarity of the graded quantity over its window" but names no action
    for it: S2 requires a stalled LINEAR SOLVER, and a marching quantity is not a plateau.
  * levels of one triple drifting in OPPOSITE SIGNS.  No per-case monitor can see this:
    it exists only at triple scope, and the taxonomy is per-run.
Reported as UNCLASSED STOP with the measurement attached.  A class that does not fit is a
finding about the taxonomy, not a number to round into the nearest box.

STOPS ONLY.  This process sends SIGTERM to the registered solver pid and writes the stop
record.  It never edits a case, never relaunches, never raises a cap.  The one registered
action is APPLIED BY THE SUPERVISOR from the stop record.
"""
import argparse, glob, json, os, re, signal, sys, time
from datetime import datetime, timezone

def utc(): return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

LADDER = ["continuation from a converged neighbour", "relaxation reduction",
          "pseudo-transient", "transient re-registration"]

def read_iters(log, field):
    if not os.path.exists(log): return []
    txt = open(log, errors="replace").read()
    out = []
    for b in re.split(r"\nTime = ", txt)[1:]:
        m = re.match(r"(\d+)", b)
        h = re.findall(r"Solving for %s,\s*Initial residual\s*=\s*([-\d.eE+]+)" % field, b)
        n = re.findall(r"Solving for %s,.*No Iterations\s*(\d+)" % field, b)
        if m and h:
            out.append(dict(it=int(m.group(1)), res=float(h[0]),   # FIRST solve: the one
                            lin_iters=int(n[0]) if n else None))   # the SIMPLE loop tests
    return out

def read_series(case, pattern, col):
    d = sorted(glob.glob(os.path.join(case, pattern)))
    if not d: return None, []
    hdr, rows = None, []
    for l in open(d[-1], errors="replace"):
        if l.startswith("#"): hdr = l
        elif l.strip(): rows.append(l.split())
    if hdr is None: return d[-1], []
    cols = hdr.lstrip("#").split(); ci = cols.index(col) if col in cols else 1
    return d[-1], [(float(r[0]), float(r[ci])) for r in rows if len(r) > ci]

def block_means(vals, nb):
    n = max(len(vals) // nb, 1)
    return [sum(vals[i * n:(i + 1) * n]) / len(vals[i * n:(i + 1) * n])
            for i in range(nb) if vals[i * n:(i + 1) * n]]

def evaluate(prof, case, elapsed_s, ranks):
    m = prof["monitor"]
    log = os.path.join(case, m.get("log", "log.simpleFoam"))
    it = read_iters(log, m.get("residual_field", "p"))
    dat, ser = read_series(case, m["series_glob"], m["series_column"])
    stops = []
    if not it:
        return stops, dict(iterations_seen=0)

    res = [x["res"] for x in it]
    W = m["window_iterations"]
    n_it = len(it)

    # --- S1 residual growth past the bound -------------------------------------------
    if n_it >= 2 * W:
        b = block_means(res[-2 * W:], 2)
        if len(b) == 2 and b[1] > b[0] * (1.0 + m["residual_growth_rel"]):
            stops.append(dict(stop="S1", cause_class="residual growth",
                              measured=dict(prev_window_mean=b[0], last_window_mean=b[1],
                                            growth_rel=b[1] / b[0] - 1.0, window=W),
                              registered_action=LADDER[0]))
    # --- S1b field outside its bounds -------------------------------------------------
    if os.path.exists(log):
        nb = len(re.findall(r"[Bb]ounding ", open(log, errors="replace").read()))
        if nb > m.get("max_bounding_events", 0):
            stops.append(dict(stop="S1b", cause_class="field outside its bounds",
                              measured=dict(bounding_events=nb,
                                            allowed=m.get("max_bounding_events", 0)),
                              registered_action=LADDER[1]))
    # --- S2 plateau above target WITH a stalled linear solver --------------------------
    tail = it[-W:]
    if len(tail) == W:
        rs = [x["res"] for x in tail]
        flat = (max(rs) - min(rs)) <= m["residual_plateau_rel"] * max(abs(max(rs)), 1e-300)
        above = min(rs) > m["residual_target"]
        li = [x["lin_iters"] for x in tail if x["lin_iters"] is not None]
        sat = bool(li) and (sum(li) / len(li)) >= m["linear_saturation_iters"]
        if flat and above and sat:
            stops.append(dict(stop="S2", cause_class="plateau above target, linear solver stalled",
                              measured=dict(residual_spread_rel=(max(rs) - min(rs)) / max(rs),
                                            min_residual=min(rs), target=m["residual_target"],
                                            mean_linear_iters=sum(li) / len(li)),
                              registered_action=LADDER[1]))
    # --- S3 coherent oscillation with a fixed period in the graded quantity ------------
    if len(ser) >= W:
        v = [x[1] for x in ser[-W:]]
        d = [v[i + 1] - v[i] for i in range(len(v) - 1)]
        flips = sum(1 for i in range(len(d) - 1) if d[i] * d[i + 1] < 0)
        rate = flips / max(len(d) - 1, 1)
        if rate >= m["oscillation_sign_change_rate"]:
            stops.append(dict(stop="S3", cause_class="coherent oscillation",
                              mark="physics voting unsteady",
                              measured=dict(sign_change_rate=rate, window=W, flips=flips),
                              registered_action=LADDER[2]))
    # --- S4 cost per iteration beyond TWICE the estimate --------------------------------
    per_it = elapsed_s / n_it
    if per_it > 2.0 * m["estimated_s_per_iteration"]:
        stops.append(dict(stop="S4", cause_class="cost per iteration beyond twice the estimate",
                          measured=dict(measured_s_per_iteration=per_it,
                                        estimate_s_per_iteration=m["estimated_s_per_iteration"],
                                        ratio=per_it / m["estimated_s_per_iteration"]),
                          mark=("MACHINE cause if residual decay per iteration is unchanged and "
                                "only wall time moved; CASE cause if decay also degraded"),
                          registered_action="diagnose machine vs case from the per-iteration "
                                            "timing and residual decay before any ladder step"))
    # --- S5 cap ------------------------------------------------------------------------
    cap = m.get("cap_core_min")
    used = elapsed_s * ranks / 60.0
    if cap is not None and used >= cap:
        if m.get("cap_stops_run") is None:
            stops.append(dict(stop="S5?", cause_class="cap reached, DISPOSITION UNREGISTERED",
                              measured=dict(used_core_min=used, cap_core_min=cap),
                              registered_action=("REFUSE TO DECIDE: CASE_PROTOCOL section 9's "
                                                 "closing clause suspends budget gates for the 3D "
                                                 "cases that still need to run, and whether this "
                                                 "case is inside that scope is not registered. "
                                                 "cap_stops_run must be stated in the registration.")))
        elif m["cap_stops_run"]:
            stops.append(dict(stop="S5", cause_class="cap reached",
                              measured=dict(used_core_min=used, cap_core_min=cap),
                              verdict="NOT A RESULT",
                              registered_action="STOP. Never a raised cap. Answered by a "
                                                "re-registered successor."))
    # --- UNCLASSED: residual stalled above target while the graded quantity marches -----
    if len(ser) >= W and len(it) >= W:
        v = [x[1] for x in ser[-W:]]
        drift = abs(v[-1] - v[0]) / max(abs(v[-1]), 1e-300)
        rs = [x["res"] for x in it[-W:]]
        if min(rs) > m["residual_target"] and drift > m["graded_stationarity_rel"]:
            stops.append(dict(stop="U1", cause_class="UNCLASSED",
                              why=("residual is above target AND the graded quantity is still "
                                   "marching over its window. Section 4 monitors stationarity of "
                                   "the graded quantity but names NO action for it: S2 requires a "
                                   "stalled LINEAR SOLVER and a marching quantity is not a "
                                   "plateau. Reported unclassed rather than forced into S2."),
                              measured=dict(graded_drift_over_window_rel=drift,
                                            window=W, min_residual=min(rs),
                                            residual_target=m["residual_target"]),
                              registered_action="NONE REGISTERED -- this is a finding about the "
                                                "taxonomy and goes to the supervisor"))
    return stops, dict(iterations_seen=n_it, s_per_iteration=per_it,
                       used_core_min=used, graded_artifact=dat,
                       last_graded=(ser[-1][1] if ser else None))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", required=True); ap.add_argument("--case", required=True)
    ap.add_argument("--pid", type=int, required=True); ap.add_argument("--started", type=float, required=True)
    ap.add_argument("--record", required=True); ap.add_argument("--interval", type=float, default=60.0)
    ap.add_argument("--once", action="store_true")
    a = ap.parse_args()
    prof = json.load(open(a.profile)); ranks = prof.get("ranks", 1)
    history = []
    while True:
        alive = os.path.exists("/proc/%d" % a.pid)
        stops, meas = evaluate(prof, a.case, time.time() - a.started, ranks)
        rec = dict(utc=utc(), pid=a.pid, solver_alive=alive, measurements=meas, stops=stops,
                   monitor_ppid=os.getppid())
        # NEVER THE SAME ACTION TWICE ON THE SAME STATE
        for s in stops:
            prior = [h for h in history if h["cause_class"] == s["cause_class"]]
            s["prior_stops_on_this_cause"] = len(prior)
            if len(prior) >= 1:
                nxt = LADDER.index(s["registered_action"]) + 1 if s["registered_action"] in LADDER else None
                s["registered_action"] = (LADDER[nxt] if nxt is not None and nxt < len(LADDER)
                                          else "LADDER EXHAUSTED: park as NOT A RESULT with the "
                                               "full action history and the lesson")
            history.append(dict(cause_class=s["cause_class"], utc=rec["utc"]))
        with open(a.record, "a") as f:
            f.write(json.dumps(rec) + "\n")
        for s in stops:
            print("STAGE 4 | STOP %-4s | %-46s | action: %s"
                  % (s["stop"], s["cause_class"], s["registered_action"]))
        if stops and alive:
            try: os.kill(a.pid, signal.SIGTERM)
            except ProcessLookupError: pass
            print("STAGE 4 | EXIT | STOPPED | SIGTERM to pid %d; %d stop(s); record %s"
                  % (a.pid, len(stops), a.record))
            return 1
        if not alive:
            print("STAGE 4 | EXIT | SOLVER GONE | monitor stands down; record %s" % a.record)
            return 0
        if a.once:
            print("STAGE 4 | EXIT | NO STOP | %d iterations seen, %.3f s/iter, %.2f core-min"
                  % (meas.get("iterations_seen", 0), meas.get("s_per_iteration") or 0,
                     meas.get("used_core_min") or 0))
            return 0
        time.sleep(a.interval)

if __name__ == "__main__":
    sys.exit(main())
