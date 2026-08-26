#!/usr/bin/env python
"""D4S-F3S -- THE STATIONARITY ACCEPTANCE RULE FOR A PRIMAL, one implementation,
two call sites (the in-container instrument `d4s_f3s_fd_endpoint.py` and the
host-side grader `d4s_f3s_grade.py`).  Ancestor: curriculum_D4's acceptance
instrument `d4_accept_primal.py` (RESULTS.md section 11.2 at 1697ea49), which
accepted ONE primal by a CD band; this rule accepts EVERY primal of the endpoint
FD sweep by the SHAPE of its own residual history and by nothing else.

WHY A STATIONARITY RULE AND NOT A THRESHOLD (D4S-PREREG-DEF-1).  The frozen
producer `d4_opt_runScript.py:36-37` accepts a primal when its minimum residual
is <= primalMinResTol x primalMinResTolDiff = 1e-8 x 1e3 = 1e-5.  On this case
the converged primal's `nuTilda` initial residual FLOORS at ~1e-5 on both rows:
  PATCHED endpoint (curriculum_D4 F3, 2026-08-25):  9.780100659e-06  -> accepted by 2.2 %
  SHIPPED endpoint (D4-SHIPPED F3 r2, 2026-08-26): 1.115891818e-05  -> rejected by 11.6 %
Both series are stationary to < 1e-6 relative over their last 200 iterations.
A threshold sitting at the instrument's own floor decides the arm by which side
of the floor the endpoint lands.  THIS RULE NEVER COMPARES A RESIDUAL TO A LEVEL:
it asks whether the primal has STOPPED MOVING, whether continuity is bounded and
whether everything is finite -- and is therefore blind to which side of 1e-5 the
floor sits.  It is applied IDENTICALLY to both rows (one rule, not a SHIPPED-only
relaxation), and the two measured floors above are its selftest's positive
controls, with planted drifting / non-finite / unbounded mutants as negatives.

THE RULE (registered constants below, every one derived in PREREGISTRATION.md
section 3):
  R1  the capture carries the solver's `End` line and >= MIN_WINDOW_SAMPLES
      printed samples with Time >= endTime - WINDOW_ITERS (the producer prints
      every `printInterval` = 100 iterations, so the last-200 window holds the
      samples at 800, 900 and 1000 for endTime 1000);
  R2  for EVERY registered equation, max over the window of
      |r(t) - r(end)| / r(end)  <=  STATIONARITY_TOL, with r(end) finite and > 0;
  R3  `Time step continuity errors : sum local` at the last sample <=
      CONTINUITY_BOUND, and the global / cumulative values finite;
  R4  every parsed number finite.
An accepted primal is one that satisfies R1-R4.  A capture that yields ZERO
`Time =` lines is a READER FAILURE and is REFUSED, never accepted (rule 3: a
reader not shown able to see a residual has not measured stationarity).

NO `assert` anywhere: identical under `python -O` (L-332).
"""
import json
import math
import os
import re
import sys

EQUATIONS = ("U0", "U1", "U2", "he", "p", "nuTilda")
WINDOW_ITERS = 200
STATIONARITY_TOL = 1.0e-3
MIN_WINDOW_SAMPLES = 3
CONTINUITY_BOUND = 1.0e-6
END_TIME_REGISTERED = 1000

TIME_RE = re.compile(r"^Time = (\d+)\s*$")
RES_RE = re.compile(r"^(\S+) initRes: (\S+) finalRes: (\S+) nIters: (\d+)\s*$")
CONT_RE = re.compile(r"^Time step continuity errors : sum local = (\S+)")
GLOBAL_RE = re.compile(r"^\s*global = (\S+)")
CUM_RE = re.compile(r"^\s*cumulative = (\S+)")
CD_RE = re.compile(r"^CD: (\S+) final: (\S+)")
CL_RE = re.compile(r"^CL: (\S+) final: (\S+)")


class Refusal(Exception):
    """The reader could not measure; distinct from a primal that FAILED the rule."""


def _f(tok):
    try:
        return float(tok)
    except (TypeError, ValueError):
        return float("nan")


def parse_primal_text(text):
    """Parse ONE primal's solver output (from `Running Primal Solver` or the
    start of a capture, to its `End` line) into printed samples."""
    samples, cur, end_seen = [], None, False
    for raw in text.splitlines():
        line = raw.rstrip()
        m = TIME_RE.match(line)
        if m:
            cur = {"time": int(m.group(1)), "res": {}, "cont_local": None,
                   "cont_global": None, "cont_cumulative": None,
                   "CD": None, "CL": None}
            samples.append(cur)
            continue
        if cur is None:
            continue
        m = RES_RE.match(line)
        if m:
            cur["res"][m.group(1)] = _f(m.group(2))
            continue
        m = CONT_RE.match(line)
        if m:
            cur["cont_local"] = _f(m.group(1))
            continue
        m = GLOBAL_RE.match(line)
        if m and cur["cont_local"] is not None:
            cur["cont_global"] = _f(m.group(1))
            continue
        m = CUM_RE.match(line)
        if m and cur["cont_local"] is not None:
            cur["cont_cumulative"] = _f(m.group(1))
            continue
        m = CD_RE.match(line)
        if m:
            cur["CD"] = _f(m.group(2))
            continue
        m = CL_RE.match(line)
        if m:
            cur["CL"] = _f(m.group(2))
            continue
        if line.strip() == "End":
            end_seen = True
    return {"samples": samples, "n_samples": len(samples), "end_line": end_seen}


def evaluate(parsed, equations=EQUATIONS, window_iters=WINDOW_ITERS,
             tol=STATIONARITY_TOL, min_samples=MIN_WINDOW_SAMPLES,
             cont_bound=CONTINUITY_BOUND, end_time_registered=END_TIME_REGISTERED):
    """Apply R1-R4.  Returns a dict with `accepted` (bool) and every reading.
    Raises Refusal only when the reader saw nothing (zero samples)."""
    samples = parsed.get("samples") or []
    if not samples:
        raise Refusal("READER SAW ZERO `Time =` SAMPLES -- the capture is empty or "
                      "is not a primal; refusing rather than accepting a void")
    last = samples[-1]
    end_time = last["time"]
    window = [s for s in samples if s["time"] >= end_time - window_iters]
    out = {"end_time": end_time, "end_time_registered": end_time_registered,
           "end_time_matches_registered": bool(end_time == end_time_registered),
           "end_line": bool(parsed.get("end_line")),
           "n_samples": len(samples), "n_window": len(window),
           "window_times": [s["time"] for s in window],
           "window_iters": window_iters, "tol": tol,
           "min_window_samples": min_samples, "cont_bound": cont_bound,
           "per_equation": {}, "failures": []}
    # R1
    if not out["end_line"]:
        out["failures"].append("R1:no_End_line")
    if not out["end_time_matches_registered"]:
        out["failures"].append("R1:endTime_%s_!=_registered_%s" % (end_time, end_time_registered))
    if len(window) < min_samples:
        out["failures"].append("R1:window_samples_%d_<_%d" % (len(window), min_samples))
    # R2 + R4 on residuals
    for eq in equations:
        r_end = last["res"].get(eq, float("nan"))
        row = {"r_end": r_end, "max_rel_drift": None, "finite": bool(math.isfinite(r_end)),
               "positive": bool(math.isfinite(r_end) and r_end > 0.0), "stationary": False,
               "present_in_every_window_sample": all(eq in s["res"] for s in window)}
        if not row["present_in_every_window_sample"]:
            out["failures"].append("R2:%s_absent_in_window" % eq)
        elif not (row["finite"] and row["positive"]):
            out["failures"].append("R4:%s_r_end_not_finite_positive" % eq)
        else:
            drifts = [abs(s["res"][eq] - r_end) / r_end for s in window]
            if any(not math.isfinite(d) for d in drifts):
                out["failures"].append("R4:%s_non_finite_in_window" % eq)
            else:
                row["max_rel_drift"] = max(drifts)
                row["stationary"] = bool(row["max_rel_drift"] <= tol)
                if not row["stationary"]:
                    out["failures"].append("R2:%s_drift_%.3e_>_%.1e" % (eq, row["max_rel_drift"], tol))
        out["per_equation"][eq] = row
    # R3
    cl = last.get("cont_local")
    out["cont_local_end"] = cl
    out["cont_global_end"] = last.get("cont_global")
    out["cont_cumulative_end"] = last.get("cont_cumulative")
    if cl is None or not math.isfinite(cl):
        out["failures"].append("R3:continuity_sum_local_absent_or_non_finite")
    elif cl > cont_bound:
        out["failures"].append("R3:continuity_sum_local_%.3e_>_%.1e" % (cl, cont_bound))
    for k in ("cont_global_end", "cont_cumulative_end"):
        v = out[k]
        if v is None or not math.isfinite(v):
            out["failures"].append("R3:%s_absent_or_non_finite" % k)
    # R4 on CD/CL of the last sample
    for k in ("CD", "CL"):
        v = last.get(k)
        out["%s_end" % k] = v
        if v is None or not math.isfinite(v):
            out["failures"].append("R4:%s_end_absent_or_non_finite" % k)
    out["accepted"] = bool(not out["failures"])
    return out


def split_primal_blocks(log_text):
    """Split a whole arm log into its `Running Primal Solver NNN` blocks (each
    to its `End` line).  Used by the grader and the selftest on real logs."""
    blocks, cur = [], None
    for raw in log_text.splitlines():
        if raw.startswith("Running Primal Solver"):
            cur = []
            blocks.append(cur)
            continue
        if cur is not None:
            cur.append(raw)
            if raw.strip() == "End":
                cur = None
    return ["\n".join(b) for b in blocks]


# ------------------------------------------------------------------ selftest
def _count_asserts(path):
    import ast
    tree = ast.parse(open(path).read())
    return sum(1 for n in ast.walk(tree) if isinstance(n, ast.Assert))


def selftest():
    here = os.path.dirname(os.path.abspath(__file__))
    logs = {
        "PATCHED_D4_F3": "/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/F3_20260825T220706Z_2733788.log",
        "SHIPPED_D4S_F3r2": "/home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-a2-wing-cdmin/F3_20260826T205120Z_411184.log",
    }
    results, fails = [], 0

    def check(name, cond, detail=""):
        nonlocal fails
        results.append("  [%s] %s %s" % ("OK " if cond else "BAD", name, detail))
        if not cond:
            fails += 1

    # 0. the AST counter can count: a planted assert in a temp file
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
        fh.write("def f(x):\n    assert x\n")
        pp = fh.name
    check("0_ast_counter_sees_a_planted_assert", _count_asserts(pp) == 1)
    os.remove(pp)
    check("0_ast_Assert_zero_in_this_module", _count_asserts(os.path.abspath(__file__)) == 0)

    # 1. POSITIVE CONTROLS: the two measured floors, every primal block, ACCEPT
    worst = {}
    for label, path in logs.items():
        if not os.path.isfile(path):
            check("1_%s_log_present" % label, False, path)
            continue
        text = open(path, errors="replace").read()
        blocks = split_primal_blocks(text)
        check("1_%s_has_primal_blocks" % label, len(blocks) >= 1, "n=%d" % len(blocks))
        n_acc = 0
        for i, b in enumerate(blocks):
            p = parse_primal_text(b)
            if p["n_samples"] == 0:
                continue   # a block cut by the arm's abort carries no samples
            e = evaluate(p)
            n_acc += 1 if e["accepted"] else 0
            for eq, row in e["per_equation"].items():
                if row["max_rel_drift"] is not None:
                    worst[eq] = max(worst.get(eq, 0.0), row["max_rel_drift"])
            if i == 0:
                check("1_%s_primal001_accepted" % label, e["accepted"],
                      "nuTilda r_end=%.9e max_drift=%.3e cont=%.3e failures=%s"
                      % (e["per_equation"]["nuTilda"]["r_end"],
                         e["per_equation"]["nuTilda"]["max_rel_drift"] or -1,
                         e["cont_local_end"] or -1, e["failures"]))
        nb = sum(1 for b in blocks if parse_primal_text(b)["n_samples"] > 0)
        check("1_%s_all_%d_complete_primals_accepted" % (label, nb), n_acc == nb, "accepted=%d" % n_acc)
    if worst:
        margin = min(STATIONARITY_TOL / v for v in worst.values() if v > 0)
        check("1_measured_worst_drift_below_tol_by_>=100x", margin >= 100.0,
              "worst per eq %s ; tol %.0e ; margin %.0fx" % ({k: "%.2e" % v for k, v in worst.items()}, STATIONARITY_TOL, margin))
    # the SHIPPED floor is ABOVE 1e-5 and PATCHED below: the rule is blind to that
    sh = open(logs["SHIPPED_D4S_F3r2"], errors="replace").read() if os.path.isfile(logs["SHIPPED_D4S_F3r2"]) else ""
    pa = open(logs["PATCHED_D4_F3"], errors="replace").read() if os.path.isfile(logs["PATCHED_D4_F3"]) else ""
    if sh and pa:
        es = evaluate(parse_primal_text(split_primal_blocks(sh)[0]))
        ep = evaluate(parse_primal_text(split_primal_blocks(pa)[0]))
        rs, rp = es["per_equation"]["nuTilda"]["r_end"], ep["per_equation"]["nuTilda"]["r_end"]
        check("1_blind_to_the_1e-5_side", es["accepted"] and ep["accepted"] and rs > 1.0e-5 > rp,
              "SHIPPED nuTilda %.9e (> 1e-5) ACCEPTED; PATCHED %.9e (< 1e-5) ACCEPTED" % (rs, rp))
        base_block = split_primal_blocks(pa)[0]
    else:
        base_block = None

    # 2. NEGATIVE CONTROLS on planted mutants of the real PATCHED block
    if base_block:
        def mutate(text, fn):
            return "\n".join(fn(l) for l in text.splitlines())
        # 2a drift: scale nuTilda at Time 800 by 1.2 % (> 0.1 % tol)
        state = {"t": 0}
        def drift(l):
            m = TIME_RE.match(l)
            if m:
                state["t"] = int(m.group(1))
            mm = RES_RE.match(l)
            if mm and mm.group(1) == "nuTilda" and state["t"] == 800:
                return "nuTilda initRes: %r finalRes: %s nIters: %s" % (float(mm.group(2)) * 1.012, mm.group(3), mm.group(4))
            return l
        e = evaluate(parse_primal_text(mutate(base_block, drift)))
        check("2a_planted_1.2pct_drift_at_800_REJECTED", not e["accepted"] and any(f.startswith("R2:nuTilda") for f in e["failures"]), str(e["failures"]))
        # 2b a drift just UNDER the tol is accepted (the tol is a tol, not a zero)
        def drift_small(l):
            m = TIME_RE.match(l)
            if m:
                state["t"] = int(m.group(1))
            mm = RES_RE.match(l)
            if mm and mm.group(1) == "nuTilda" and state["t"] == 800:
                return "nuTilda initRes: %r finalRes: %s nIters: %s" % (float(mm.group(2)) * 1.0009, mm.group(3), mm.group(4))
            return l
        e = evaluate(parse_primal_text(mutate(base_block, drift_small)))
        check("2b_planted_0.09pct_drift_ACCEPTED", e["accepted"], str(e["failures"]))
        # 2c non-finite residual at the end
        def nanify(l):
            m = TIME_RE.match(l)
            if m:
                state["t"] = int(m.group(1))
            mm = RES_RE.match(l)
            if mm and mm.group(1) == "U0" and state["t"] == 1000:
                return "U0 initRes: nan finalRes: nan nIters: 1"
            return l
        e = evaluate(parse_primal_text(mutate(base_block, nanify)))
        check("2c_planted_nan_REJECTED", not e["accepted"] and any(f.startswith("R4:U0") for f in e["failures"]), str(e["failures"]))
        # 2d continuity unbounded
        def cont(l):
            m = TIME_RE.match(l)
            if m:
                state["t"] = int(m.group(1))
            if CONT_RE.match(l) and state["t"] == 1000:
                return "Time step continuity errors : sum local = 2.5e-05"
            return l
        e = evaluate(parse_primal_text(mutate(base_block, cont)))
        check("2d_planted_continuity_2.5e-5_REJECTED", not e["accepted"] and any(f.startswith("R3:continuity") for f in e["failures"]), str(e["failures"]))
        # 2e End line removed
        e = evaluate(parse_primal_text(mutate(base_block, lambda l: "" if l.strip() == "End" else l)))
        check("2e_missing_End_REJECTED", not e["accepted"] and "R1:no_End_line" in e["failures"], str(e["failures"]))
        # 2f truncated at Time 700 (endTime != registered, window short)
        cut = base_block.split("Time = 800")[0]
        e = evaluate(parse_primal_text(cut))
        check("2f_truncated_at_700_REJECTED", not e["accepted"] and any(f.startswith("R1:") for f in e["failures"]), str(e["failures"]))
        # 2g empty capture -> REFUSAL, never accepted
        try:
            evaluate(parse_primal_text("nothing here\n"))
            check("2g_empty_capture_REFUSES", False, "accepted a void")
        except Refusal as exc:
            check("2g_empty_capture_REFUSES", True, str(exc)[:80])
        # 2h a residual line for one equation missing in the window
        def drop(l):
            m = TIME_RE.match(l)
            if m:
                state["t"] = int(m.group(1))
            mm = RES_RE.match(l)
            if mm and mm.group(1) == "he" and state["t"] == 900:
                return ""
            return l
        e = evaluate(parse_primal_text(mutate(base_block, drop)))
        check("2h_equation_absent_in_window_REJECTED", not e["accepted"] and "R2:he_absent_in_window" in e["failures"], str(e["failures"]))
    print("D4S_F3S_ACCEPT SELFTEST %s constants EQUATIONS=%s WINDOW_ITERS=%d STATIONARITY_TOL=%g MIN_WINDOW_SAMPLES=%d CONTINUITY_BOUND=%g END_TIME=%d mode=%s"
          % (os.path.basename(__file__), ",".join(EQUATIONS), WINDOW_ITERS, STATIONARITY_TOL,
             MIN_WINDOW_SAMPLES, CONTINUITY_BOUND, END_TIME_REGISTERED,
             "python3 -O" if not __debug__ else "python3"))
    print("\n".join(results))
    print("D4S_F3S_ACCEPT SELFTEST pass=%d fail=%d" % (len(results) - fails, fails))
    return 0 if fails == 0 else 2


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--selftest":
        sys.exit(selftest())
    if len(sys.argv) >= 3 and sys.argv[1] == "--evaluate":
        # evaluate one capture file; prints JSON; rc 0 accepted, 1 rejected, 2 refused
        try:
            e = evaluate(parse_primal_text(open(sys.argv[2], errors="replace").read()))
        except Refusal as exc:
            print(json.dumps({"REFUSED": str(exc)}))
            sys.exit(2)
        print(json.dumps(e, sort_keys=True))
        sys.exit(0 if e["accepted"] else 1)
    sys.stderr.write("usage: d4s_f3s_accept.py --selftest | --evaluate <capture.log>\n")
    sys.exit(64)
