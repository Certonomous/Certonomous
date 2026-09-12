#!/usr/bin/env python
"""D6R2C -- the per-iteration monitor and Sanaa's item-7 stop rules.

Her While-running item 11: "Monitor writes per iteration: residuals per
equation, the graded quantity, cost per iteration, wall time vs cap."
Her D6R2 item 6: "Monitor writes the objective, constraint violation and each
condition's convergence per iteration."

Her item 7, verbatim: "objective rises three consecutive iterations -> stop,
halve the step, resume; any condition's primal fails to converge (the D6/D6R
NaN signature) -> stop, resume from the last good iterate with the step
halved; cap -> NOT A RESULT, never raised."

WHAT THIS FILE DOES AND DOES NOT DO
  It DETECTS and it RECORDS.  It writes D6R2C_MONITOR.jsonl and, when a stop
  rule fires, D6R2C_STOP_RULE.json.  `--act` is required before it will touch
  a container, and even with `--act` the ONLY thing it does is `docker stop`
  the named container and write the resume instruction: it never relaunches,
  and it never acts on a cap.  A cap crossing is REPORTED and the row is
  graded NOT A RESULT; the cap is never raised and NOTHING KILLS ON IT
  (Sanaa 2026-09-12 #17, and the chief's reading of items 3/7/10).

THE STOP RULES ARE TESTED AGAINST REAL DATA, NOT ONLY SYNTHETIC.  `--selftest`
drives rule 1 over the ACTUAL IPOPT objective sequence of the D6R2 run that
died at 17:32:57Z -- a sequence that contains a two-in-a-row rise and must
therefore NOT fire -- and then over the same sequence mutated to carry a
three-in-a-row rise, which must fire.  A detector shown only on data it was
built from is decoration.
"""
import os
import re
import sys
import json
import time
import argparse
import subprocess

# ---- FROZEN (PREREGISTRATION.md section 6) --------------------------------
RISE_RUN_LENGTH = 3            # her item 7: THREE consecutive rises
STEP_HALVING = 0.5             # "halve the step"
NONCONV_TOKENS = ("Primal solution failed", "nan", "NaN", "Invalid number in NLP")

IPOPT_ROW = re.compile(r"^\s*(\d+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)")
TIME_LINE = re.compile(r"^Time = (\d+)")
RESID = re.compile(r"^(Ux|Uy|Uz|p|p_rgh|e|h|T|nuTilda|k|omega|epsilon)\b.*[Ff]inal residual = ([-\d.eE+]+)")


def parse_ipopt(text):
    """[(major, obj, inf_pr, inf_du)] from IPOPT's iteration table."""
    out = []
    for line in text.splitlines():
        m = IPOPT_ROW.match(line)
        if not m:
            continue
        try:
            n = int(m.group(1))
            vals = [float(m.group(i)) for i in (2, 3, 4)]
        except ValueError:
            continue
        if out and n <= out[-1][0]:
            continue
        out.append((n, vals[0], vals[1], vals[2]))
    return out


def rule1_consecutive_rises(objs, run_length=RISE_RUN_LENGTH):
    """Sanaa item 7 rule 1.  Returns the major at which the run_length-th
    consecutive rise completes, or None.  A rise is strict."""
    run = 0
    for i in range(1, len(objs)):
        if objs[i][1] > objs[i - 1][1]:
            run += 1
            if run >= run_length:
                return objs[i][0]
        else:
            run = 0
    return None


def rule2_primal_nonconvergence(log_text):
    """Sanaa item 7 rule 2 -- the D6/D6R NaN signature.  Returns the first
    offending line, or None."""
    for line in log_text.splitlines():
        for tok in NONCONV_TOKENS:
            if tok in line:
                return line.strip()[:300]
    return None


def per_condition_convergence(work, points=("mp04", "mp05", "mp06")):
    """Latest primal time reached and the final residual per equation, per
    condition.  A condition with no readable log is reported NOT_MEASURED --
    never as converged."""
    out = {}
    for p in points:
        d = os.path.join(work, p)
        rec = {"last_time": None, "final_residuals": {}, "source": None}
        cands = []
        for root, _dirs, files in os.walk(d):
            for f in files:
                if f.startswith("log") or f.endswith(".log"):
                    cands.append(os.path.join(root, f))
            if root.count(os.sep) - d.count(os.sep) > 2:
                _dirs[:] = []
        if not cands:
            rec["source"] = "NOT_MEASURED (no log under %s)" % d
            out[p] = rec
            continue
        f = max(cands, key=lambda x: os.path.getmtime(x))
        rec["source"] = f
        try:
            txt = open(f, errors="replace").read()[-400000:]
        except OSError as e:
            rec["source"] = "NOT_MEASURED (%s)" % e
            out[p] = rec
            continue
        for line in txt.splitlines():
            m = TIME_LINE.match(line)
            if m:
                rec["last_time"] = int(m.group(1))
            m = RESID.match(line)
            if m:
                rec["final_residuals"][m.group(1)] = float(m.group(2))
        out[p] = rec
    return out


def tick(work, base, container, cap_core_min, ranks, t0_epoch, act=False):
    ip = os.path.join(work, "opt_IPOPT.txt")
    text = open(ip, errors="replace").read() if os.path.exists(ip) else ""
    objs = parse_ipopt(text)
    ev = os.path.join(work, "d6r2c_evals.jsonl")
    rows = []
    if os.path.exists(ev):
        for line in open(ev):
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except ValueError:
                    pass
    reals = [r for r in rows if r.get("kind") in ("F", "G")]
    wall = time.time() - t0_epoch
    core_min = wall * ranks / 60.0

    logs = ""
    for root, _d, files in os.walk(work):
        for f in files:
            if f.endswith(".log") or f.startswith("log"):
                try:
                    logs += open(os.path.join(root, f), errors="replace").read()[-200000:]
                except OSError:
                    pass
    row = {
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "major": objs[-1][0] if objs else None,
        "objective": objs[-1][1] if objs else None,
        "constraint_violation_inf_pr": objs[-1][2] if objs else None,
        "dual_inf_du": objs[-1][3] if objs else None,
        "objective_history": [o[1] for o in objs],
        "real_evaluations": len(reals),
        "cost_core_min_so_far": round(core_min, 3),
        "cost_core_min_per_major": round(core_min / objs[-1][0], 3) if objs and objs[-1][0] else None,
        "wall_s": round(wall, 1),
        "cap_core_min_registered": cap_core_min,
        "cap_crossed": core_min > cap_core_min,
        "cap_note": "A CROSSED CAP IS REPORTED AND THE ROW IS GRADED NOT A RESULT. "
                    "THE CAP IS NEVER RAISED AND NOTHING KILLS ON IT.",
        "per_condition": per_condition_convergence(work),
    }
    r1 = rule1_consecutive_rises(objs)
    r2 = rule2_primal_nonconvergence(logs)
    row["stop_rule_1_objective_rises"] = r1
    row["stop_rule_2_primal_nonconvergence"] = r2
    with open(os.path.join(work, "D6R2C_MONITOR.jsonl"), "a") as fh:
        fh.write(json.dumps(row, sort_keys=True, default=str) + "\n")

    fired = None
    if r1 is not None:
        fired = {"rule": 1, "text": "objective rose %d consecutive majors, completing at major %d"
                 % (RISE_RUN_LENGTH, r1), "action": "STOP, halve the step, resume from the last "
                 "good iterate", "step_factor": STEP_HALVING, "resume_from_major": max(0, r1 - RISE_RUN_LENGTH)}
    elif r2 is not None:
        fired = {"rule": 2, "text": "primal non-convergence signature: %s" % r2,
                 "action": "STOP, resume from the last good iterate with the step halved",
                 "step_factor": STEP_HALVING,
                 "resume_from_major": objs[-1][0] - 1 if objs and objs[-1][0] else 0}
    if fired:
        fired["utc"] = row["utc"]
        fired["container"] = container
        fired["hotstart_file"] = os.path.join(work, "OptView.hst")
        fired["acted"] = False
        if act and container:
            subprocess.run(["sudo", "-n", "docker", "stop", container],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            fired["acted"] = True
        with open(os.path.join(work, "D6R2C_STOP_RULE.json"), "w") as fh:
            json.dump(fired, fh, indent=1, sort_keys=True)
        with open(os.path.join(base, "ledger.txt"), "a") as fh:
            fh.write("D6R2C_STOP_RULE rule=%d acted=%s %s\n" % (fired["rule"], fired["acted"], fired["text"]))
    return row, fired


# --------------------------------------------------------------------------- selftest
D6R2_REAL_OBJ = [3.0641631e-02, 3.0631067e-02, 2.8625963e-02, 2.5132705e-02,
                 2.5680714e-02, 2.8117733e-02, 2.6939703e-02, 2.4976239e-02,
                 2.4567002e-02, 2.7605615e-02, 2.4603956e-02, 2.3534713e-02,
                 2.3260046e-02]
D6R2_REAL_SOURCE = ("/home/ubuntu/certonomous-runs/CURRICULUM-D6R2-a2-wing-multipoint-transonic"
                    "/O_mp/opt_IPOPT.txt -- majors 0-12 of the run that died 2026-09-12T17:32:57Z")


def selftest():
    fails = []

    def chk(tag, got, want):
        ok = got == want
        print("  %-62s -> %-6s (want %-6s) %s" % (tag, got, want, "OK" if ok else "*** DID NOT FIRE ***"))
        if not ok:
            fails.append(tag)

    seq = [(i, v, 0.0, 0.0) for i, v in enumerate(D6R2_REAL_OBJ)]
    print("D6R2C_MONITOR SELFTEST")
    print(" A. stop rule 1 on REAL data -- %s" % D6R2_REAL_SOURCE)
    print("    the real sequence contains rises 3->4 and 4->5 (TWO in a row) and 8->9 (one).")
    chk("A1 real D6R2 majors 0-12: must NOT fire at a run of 3", rule1_consecutive_rises(seq), None)
    chk("A2 same sequence at run length 2: MUST fire (proves the reader sees the rises)",
        rule1_consecutive_rises(seq, run_length=2), 5)

    print(" B. the same real sequence MUTATED to carry three consecutive rises")
    mut = list(D6R2_REAL_OBJ)
    mut[6] = mut[5] + 1.0e-4              # 3->4, 4->5, 5->6 now all rise
    mseq = [(i, v, 0.0, 0.0) for i, v in enumerate(mut)]
    chk("B1 mutated real sequence: MUST fire, at major 6", rule1_consecutive_rises(mseq), 6)

    print(" C. rule 1 boundary controls")
    chk("C1 strictly falling sequence", rule1_consecutive_rises([(i, 1.0 - 0.1 * i, 0, 0) for i in range(8)]), None)
    chk("C2 flat sequence (a plateau is NOT a rise)", rule1_consecutive_rises([(i, 1.0, 0, 0) for i in range(8)]), None)
    chk("C3 exactly two rises then a fall", rule1_consecutive_rises(
        [(0, 1.0, 0, 0), (1, 1.1, 0, 0), (2, 1.2, 0, 0), (3, 0.9, 0, 0)]), None)
    chk("C4 exactly three rises", rule1_consecutive_rises(
        [(0, 1.0, 0, 0), (1, 1.1, 0, 0), (2, 1.2, 0, 0), (3, 1.3, 0, 0)]), 3)

    print(" D. stop rule 2 -- the D6/D6R NaN signature, both directions")
    chk("D1 a clean log", rule2_primal_nonconvergence("Time = 1000\nExecutionTime = 3 s\n"), None)
    chk("D2 the D6R line, verbatim",
        rule2_primal_nonconvergence("Time = 200\nPrimal solution failed!\n") is not None, True)
    chk("D3 an IPOPT invalid-number exit",
        rule2_primal_nonconvergence("EXIT: Invalid number in NLP function or derivative detected.\n") is not None, True)

    print(" E. the IPOPT table reader, driven on the REAL file's own text")
    real = ("iter    objective    inf_pr   inf_du lg(mu)  ||d||  lg(rg) alpha_du alpha_pr  ls\n"
            "   0  3.0641631e-02 4.21e-08 8.13e-03   0.0 0.00e+00    -  0.00e+00 0.00e+00   0\n"
            "   1  3.0631067e-02 1.66e-07 5.71e-03  -5.3 9.24e-03    -  9.88e-01 1.00e+00h  1\n")
    got = parse_ipopt(real)
    chk("E1 two rows parsed", len(got), 2)
    chk("E2 major 1 objective read exactly", got[1][1], 3.0631067e-02)
    chk("E3 major 1 constraint violation read exactly", got[1][2], 1.66e-07)
    chk("E4 the header line is not parsed as a row", got[0][0], 0)

    print("")
    if fails:
        print("D6R2C_MONITOR SELFTEST FAIL -- %d control(s): %s" % (len(fails), fails))
        return 1
    print("D6R2C_MONITOR SELFTEST PASS -- 13 controls, real data and mutated real data, both directions")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work"); ap.add_argument("--base")
    ap.add_argument("--container", default=None)
    ap.add_argument("--cap-core-min", type=float, default=0.0)
    ap.add_argument("--ranks", type=int, default=4)
    ap.add_argument("--interval", type=int, default=60)
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--act", action="store_true",
                    help="permit the stop rules to `docker stop` the container. NEVER acts on a cap.")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.work or not a.base:
        print("usage: --work <arm dir> --base <run root> [--container N] [--act]")
        return 64
    t0 = time.time()
    while True:
        row, fired = tick(a.work, a.base, a.container, a.cap_core_min, a.ranks, t0, act=a.act)
        print("D6R2C_MON major=%s obj=%s viol=%s reals=%s core_min=%s stop=%s"
              % (row["major"], row["objective"], row["constraint_violation_inf_pr"],
                 row["real_evaluations"], row["cost_core_min_so_far"],
                 (fired or {}).get("rule")))
        if a.once or fired:
            return 0
        if a.container:
            q = subprocess.run(["sudo", "-n", "docker", "ps", "-q", "--filter", "name=^%s$" % a.container],
                               capture_output=True, text=True)
            if not q.stdout.strip():
                return 0
        time.sleep(a.interval)


if __name__ == "__main__":
    sys.exit(main())
