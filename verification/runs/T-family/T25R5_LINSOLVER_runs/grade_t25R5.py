#!/usr/bin/env python3
"""T25R5 GRADER -- G-T5, Amendment A2's R, and Addendum D1.4's reproduction control.

⛔ DEFAULT-DENY, and it applies the checks in the REGISTERED ORDER (prereg section 6,
as amended): D1.4 reproduction first, then rule 4, then section 4.2 disqualification,
and ONLY THEN is an arm's iteration count eligible to be compared.

    python3 grade_t25R5.py            # grade every arm present
    python3 grade_t25R5.py --selftest
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXIT_REFUSE = 2

# --- FROZEN AT THE PRE-REGISTRATION.  section 3.2 / 3.2b / 5.1.
FEAS_L2   = 6.500e-07
DENOM     = 231.7636          # B0 baseline, steps 1-40, feasible solves
FACTOR    = 5.00
GATE      = 46.3527           # = DENOM / FACTOR
# --- FROZEN AT AMENDMENT A2.2.
R_NOTHING = 1.5               # R <= 1.5  -> coarse-grid correction contributes nothing
R_REAL    = 3.0               # R >= 3.0  -> it IS contributing
# --- FROZEN AT ADDENDUM D1.4, BEFORE THE RE-RUN.  Exact integers on purpose.
EXPECTED = {                  # arm -> (feasible solves, SUM of iterations)
    "C1": (901, 50281),
    "C2": (901, 40230),
    "C3": (901, 42293),
}
# --- The ladder arithmetic, section 3.3 / D1.6.  Quoted with EVERY measured factor.
LADDER_NEED = (20.9, 156.8)
# The ladder's requirement in the unit it is actually priced in: WALL TIME.
# 230,704 core-min priced from GP_VERDICT / 20,000 core-min A1.3 ceiling.
LADDER_WALL_NEED = 230704.0 / 20000.0

SOLVE = re.compile(r"^\S*(?:PCG|DIC|GAMG)\S*:\s+Solving for p_rgh, "
                   r"Initial residual = ([-\d.eE+]+), Final residual = ([-\d.eE+]+), "
                   r"No Iterations (\d+)")
TIME = re.compile(r"^Time = ([\d.eE+-]+)")
EXEC = re.compile(r"^ExecutionTime = ([\d.]+) s\s+ClockTime = (\d+) s")


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def read_log(path, max_steps=40):
    if not os.path.isfile(path):
        return None
    solves, step, ex, ck, ends = [], 0, None, None, 0
    for ln in open(path):
        if TIME.match(ln):
            step += 1
            continue
        if ln.startswith("End"):
            ends += 1
        if step > max_steps:
            continue
        m = EXEC.match(ln)
        if m:
            ex, ck = float(m.group(1)), float(m.group(2))
            continue
        m = SOLVE.match(ln)
        if m:
            solves.append((float(m.group(1)), float(m.group(2)), int(m.group(3))))
    return dict(solves=solves, steps=min(step, max_steps), exec_s=ex,
                clock_s=ck, end_lines=ends)


def feas_stats(solves):
    f = [s for s in solves if s[0] > FEAS_L2]
    return dict(n=len(f), total=sum(s[2] for s in f),
                mean=(sum(s[2] for s in f) / len(f)) if f else float("nan"),
                n_all=len(solves),
                mean_all=(sum(s[2] for s in solves) / len(solves)) if solves else float("nan"),
                pinned=sum(1 for s in solves if s[2] >= 1000))


def rule4(case, arm, log):
    """All six conjuncts. Returns (ok, [failures])."""
    bad = []
    rc = os.path.join(case, ".rc.%s_L2.legA" % arm)
    if not os.path.isfile(rc) or open(rc).read().strip() != "0":
        bad.append("rc != 0 (%s)" % (open(rc).read().strip() if os.path.isfile(rc) else "absent"))
    if log["end_lines"] < 1:
        bad.append("no End line")
    if log["steps"] != 40:
        bad.append("steps %d != 40" % log["steps"])
    tdirs = [d for d in os.listdir(os.path.join(case, "processor0"))
             if _num(d) and abs(float(d) - 0.8) <= 1e-6]
    if len(tdirs) != 1:
        bad.append("t=0.8 field dir: %d found" % len(tdirs))
    else:
        ref = os.path.join(case, "0", "module", "T")
        if os.path.isfile(ref):
            t0 = os.path.getmtime(ref)
            import glob
            old = [f for f in glob.glob(os.path.join(case, "processor*", tdirs[0], "*", "*"))
                   if os.path.isfile(f) and os.path.getmtime(f) <= t0]
            if old:
                bad.append("AGE GUARD: %d field(s) not newer than 0/module/T" % len(old))
        else:
            bad.append("no 0/module/T to date the run against (age guard unevaluable)")
    return (not bad), bad


def _num(s):
    try:
        float(s); return True
    except ValueError:
        return False


def main():
    print("=" * 92)
    print("T25R5 GRADER -- registered order: D1.4 reproduction, rule 4, section 4.2, THEN the gate")
    print("=" * 92)
    out, arms = {}, ["C1", "C2", "C3", "C4", "C5"]
    b0log = read_log(os.path.join(HERE, "B0_L2", "log.solve.legA"))
    B0_EXEC = b0log["exec_s"] if b0log else None

    # ---- 1. D1.4 REPRODUCTION CONTROL. Registered BEFORE the re-run; can lose.
    print("\n[1] ADDENDUM D1.4 REPRODUCTION CONTROL (registered before the re-run)")
    repro_fail = []
    for a in arms:
        log = read_log(os.path.join(HERE, "%s_L2" % a, "log.solve.legA"))
        if log is None:
            print("     %-3s no log yet" % a); continue
        st = feas_stats(log["solves"])
        if a in EXPECTED:
            en, et = EXPECTED[a]
            ok = (st["n"] == en and st["total"] == et)
            print("     %-3s feasible %d (expected %d)  SUM iters %d (expected %d)  -> %s"
                  % (a, st["n"], en, st["total"], et,
                     "REPRODUCES EXACTLY" if ok else "*** DEVIATES ***"))
            if not ok:
                repro_fail.append(a)
        else:
            print("     %-3s feasible %d  SUM iters %d  (no expectation registered -- "
                  "never run before; stated, not hidden)" % (a, st["n"], st["total"]))
    if repro_fail:
        refuse("D1.4: %s did not reproduce its registered iteration count. A "
               "deterministic quantity that changed is a DEFECT. The probe is "
               "NOT A RESULT and does not get quietly re-measured." % repro_fail)

    # ---- 2 & 3. rule 4, then section 4.2 equivalence -- BEFORE any gate comparison.
    print("\n[2] RULE 4 STRICT COMPLETION, then [3] SECTION 4.2 DISQUALIFICATION")
    for a in arms:
        case = os.path.join(HERE, "%s_L2" % a)
        log = read_log(os.path.join(case, "log.solve.legA"))
        if log is None:
            out[a] = dict(status="NOT RUN"); continue
        st = feas_stats(log["solves"])
        ok4, bad4 = rule4(case, a, log)
        rec = dict(mean_feasible=st["mean"], factor=DENOM / st["mean"],
                   feasible_n=st["n"], iter_sum=st["total"], mean_all=st["mean_all"],
                   pinned=st["pinned"], steps=log["steps"],
                   exec_s=log["exec_s"], clock_s=log["clock_s"], rule4=bad4)
        fired = []
        if not ok4:
            fired.append("E3/E4")
        else:
            r = subprocess.run([sys.executable, os.path.join(HERE, "compare_arms_t25R5.py"),
                                "--arm", a], capture_output=True, text=True)
            rec["equiv_raw"] = r.stdout
            if r.returncode != 0:
                fired.append("E5")
            for line in r.stdout.split("\n"):
                if "E1 FIRES" in line: fired.append("E1")
                if "E2 FIRES" in line: fired.append("E2")
                m = re.search(r"max\|dT\|.*?=\s*([\d.eE+-]+) K", line)
                if m: rec["max_dT_K"] = float(m.group(1))
                m = re.search(r"max\|dp_rgh\|\s*=\s*([\d.eE+-]+) Pa", line)
                if m: rec["max_dp_rgh_Pa"] = float(m.group(1))
        rec["wall_factor"] = (B0_EXEC / log["exec_s"]) if (B0_EXEC and log["exec_s"]) else None
        rec["fired"] = fired
        rec["eligible"] = not fired
        out[a] = rec
        print("     %-3s rule4 %-4s  fired %-12s  %s"
              % (a, "PASS" if ok4 else "FAIL", fired or "none",
                 "ELIGIBLE" if not fired else "DISQUALIFIED -- its iteration count "
                 "is NOT eligible for G-T5 whatever it is"))

    # ---- 4. THE GATE. Eligible arms only.
    print("\n[4] G-T5  (mean iterations per feasible solve <= %.4f, i.e. >= %.2fx)"
          % (GATE, FACTOR))
    elig = {a: r for a, r in out.items() if r.get("eligible")}
    for a, r in sorted(out.items()):
        if r.get("status") == "NOT RUN":
            continue
        tag = ("ELIGIBLE" if r["eligible"] else "not eligible")
        print("     %-3s %10.4f  = %5.2fx  [%s]%s"
              % (a, r["mean_feasible"], r["factor"], tag,
                 "  <-- MEETS THE BAR" if (r["eligible"] and r["mean_feasible"] <= GATE) else ""))
    winners = {a: r for a, r in elig.items() if r["mean_feasible"] <= GATE}
    verdict = "PASS" if winners else ("GATE FAIL" if elig else "NOT A RESULT")
    best = min(elig.items(), key=lambda kv: kv[1]["mean_feasible"]) if elig else None
    print("\n     G-T5 VERDICT: %s" % verdict)
    if best:
        print("     best ELIGIBLE factor: %s at %.2fx" % (best[0], best[1]["factor"]))
        # ⛔ D1.6. The gate metric is iterations per FEASIBLE solve. The ladder is
        # priced in WALL TIME. They are different quantities and comparing them
        # directly is the error this block exists to prevent -- an earlier version
        # of this very print did exactly that and called 60.11x "short" of 20.9x.
        b0 = out.get("B0_WALL")
        print("     ⛔ STANDING REPORTING CONDITION (D1.6) -- THE GATE METRIC IS NOT")
        print("        THE LADDER METRIC. G-T5 counts iterations per FEASIBLE solve;")
        print("        the ladder is priced in WALL TIME. The ladder needs a WALL")
        print("        factor of %.3fx (= 230,704 / 20,000 core-min)." % LADDER_WALL_NEED)
        for a, r in sorted(out.items()):
            if not isinstance(r, dict) or not r.get("eligible") or not r.get("wall_factor"):
                continue
            w = r["wall_factor"]
            verdict = ("MEETS the ladder requirement" if w >= LADDER_WALL_NEED
                       else "is %.1f%% SHORT of it" % (100 * (1 - w / LADDER_WALL_NEED)))
            print("        %-3s gate %6.2fx  ->  WALL %6.2fx  %s"
                  % (a, r["factor"], w, verdict))
        print("        Equivalent pressure-solve-factor framing (section 3.3): %.1fx-%.1fx"
              % LADDER_NEED)
        print("        ⚠ MEASURED OVER 40 RAMP STEPS. Extrapolation to the ladder's")
        print("          11,800-47,200 steps is NOT established by this probe.")

    # ---- 5. AMENDMENT A2's R.
    print("\n[5] AMENDMENT A2:  R = I(C5)/I(C4)")
    c4, c5 = out.get("C4", {}), out.get("C5", {})
    if not (c4.get("eligible") and c5.get("eligible")):
        R, band = None, ("UNAVAILABLE -- %s. A ratio between a valid arm and an "
                         "invalid one is not a measurement, and NO coarse-grid "
                         "conclusion may be drawn."
                         % ("C4 or C5 has not run" if not (c4 and c5)
                            else "C4 or C5 is disqualified"))
    else:
        R = c5["mean_feasible"] / c4["mean_feasible"]
        if R < 1.0:
            band = ("R < 1.0 -- the GAMG preconditioner is a NET COST, reported plainly")
        elif R <= R_NOTHING:
            band = ("R <= 1.5 -- the coarse-grid correction contributes NOTHING "
                    "measurable; section 1.2's reading is supported")
        elif R >= R_REAL:
            band = ("R >= 3.0 -- the coarse-grid correction IS contributing; this is "
                    "the OPPOSITE finding and section 1.2 is wrong about the mechanism")
        else:
            band = ("1.5 < R < 3.0 -- NOT SETTLED. Neither conclusion may be drawn.")
        print("     I(C4) = %.4f   I(C5) = %.4f   R = %.4f" % (c4["mean_feasible"], c5["mean_feasible"], R))
    print("     %s" % band)

    json.dump(dict(arms=out, gate=dict(verdict=verdict, threshold=GATE,
                                       denominator=DENOM, factor=FACTOR),
                   R=R, R_band=band, ladder_requirement=LADDER_NEED,
                   reproduction_control="PASS" if not repro_fail else "FAIL"),
              open(os.path.join(HERE, "GT5_VERDICT.json"), "w"), indent=2, sort_keys=True)
    print("\nwritten GT5_VERDICT.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
