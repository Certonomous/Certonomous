#!/usr/bin/env python3
"""T25R5 P-3 SCORER -- mesh-independence across L1/L2/L3, prereg section 3.3.

P-3 (REGISTERED, SCORED, GATING NOTHING): with the stage-2 winner, the mean
iterations per FEASIBLE solve across L1/L2/L3 has max/min <= 3.0 -- T25R4's own
G-P threshold, quoted unchanged and NOT re-registered here.

Ground registered before the probe: a working multigrid has a mesh-INDEPENDENT
iteration count, and the measured T25R4 baseline spread was x10.67.

⛔ THE PER-LEVEL FEASIBILITY THRESHOLDS ARE FROZEN AT section 3.2 AND ARE NOT
EQUAL. Using L2's threshold on L1 or L3 would silently change the population the
ratio is computed over. They are 100x each level's measured stall floor.

    python3 score_p3_t25R5.py [--arm C4]
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
# --- FROZEN AT PRE-REGISTRATION section 3.2. Not equal across levels, on purpose.
FEAS = {"L1": 4.500e-07, "L2": 6.500e-07, "L3": 1.000e-06}
P3_THRESHOLD = 3.0                  # T25R4's G-P threshold, quoted not re-registered
BASELINE_SPREAD = 10.67             # measured T25R4 baseline, section 0.3

SOLVE = re.compile(r"^\S*:\s+Solving for p_rgh, Initial residual = ([-\d.eE+]+), "
                   r"Final residual = ([-\d.eE+]+), No Iterations (\d+)")
TIME = re.compile(r"^Time = ")
EXEC = re.compile(r"^ExecutionTime = ([\d.]+) s\s+ClockTime = (\d+) s")


def stats(path, level, max_steps=40):
    if not os.path.isfile(path):
        return None
    s, step, ex, ck, ends = [], 0, None, None, 0
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
            s.append((float(m.group(1)), float(m.group(2)), int(m.group(3))))
    f = [x for x in s if x[0] > FEAS[level]]
    if not f:
        return None
    return dict(steps=min(step, max_steps), n_all=len(s), n_feas=len(f),
                sum_feas=sum(x[2] for x in f), mean_feas=sum(x[2] for x in f) / len(f),
                tot_it=sum(x[2] for x in s), pinned=sum(1 for x in s if x[2] >= 1000),
                min_final=min(x[1] for x in s if x[1] > 0),
                max_it=max(x[2] for x in s), exec_s=ex, clock_s=ck, end_lines=ends)


def main():
    arm = sys.argv[sys.argv.index("--arm") + 1] if "--arm" in sys.argv else "C4"
    print("=" * 84)
    print("T25R5 P-3 -- mesh-independence of the G-T5 winner (%s), scored, GATING NOTHING" % arm)
    print("=" * 84)
    print("  frozen per-level feasibility thresholds (section 3.2, NOT equal): "
          + "  ".join("%s>%.3e" % (k, v) for k, v in sorted(FEAS.items())))
    rows, out = {}, {}
    for who in (arm, "B0"):
        print("\n  %s:" % who)
        for lv in ("L1", "L2", "L3"):
            d = stats(os.path.join(HERE, "%s_%s" % (who, lv), "log.solve.legA"), lv)
            if not d:
                print("     %s  (not run / no feasible solves)" % lv)
                continue
            rows[(who, lv)] = d
            print("     %s steps=%2d feas=%4d mean_feas=%9.4f tot_it=%7d pinned=%4d "
                  "max_it=%5d min_final=%.3e exec=%.2fs clock=%.0fs"
                  % (lv, d["steps"], d["n_feas"], d["mean_feas"], d["tot_it"],
                     d["pinned"], d["max_it"], d["min_final"], d["exec_s"], d["clock_s"]))
    for who in (arm, "B0"):
        got = [rows[(who, lv)]["mean_feas"] for lv in ("L1", "L2", "L3")
               if (who, lv) in rows]
        if len(got) < 3:
            print("\n  %s: P-3 NOT EVALUABLE -- only %d of 3 levels present" % (who, len(got)))
            out[who] = None
            continue
        spread = max(got) / min(got)
        out[who] = spread
        print("\n  %s spread max/min = %.4f" % (who, spread))
    print("\n" + "-" * 84)
    if out.get(arm) is not None:
        sp = out[arm]
        print("  P-3: %s spread = %.4f against the registered threshold %.1f  ->  %s"
              % (arm, sp, P3_THRESHOLD, "P-3 WINS" if sp <= P3_THRESHOLD else "P-3 LOSES"))
        print("  (baseline T25R4 spread was x%.2f; B0 re-measured here: %s)"
              % (BASELINE_SPREAD,
                 ("x%.4f" % out["B0"]) if out.get("B0") else "not evaluable"))
        print("  ⚠ P-3 is REPORTED AND SCORED. It GATES NOTHING, and section 5.1 still")
        print("    binds: NO LADDER LAUNCHES ON THIS RESULT.")
    else:
        print("  P-3 NOT EVALUABLE.")
    # wall factors per level, since section D2.1 replaced the reporting condition
    print("\n  WALL FACTORS (%s vs B0), per level -- the ladder is priced in WALL TIME:" % arm)
    for lv in ("L1", "L2", "L3"):
        if (arm, lv) in rows and ("B0", lv) in rows:
            w = rows[("B0", lv)]["exec_s"] / rows[(arm, lv)]["exec_s"]
            wc = rows[("B0", lv)]["clock_s"] / max(rows[(arm, lv)]["clock_s"], 1)
            print("     %s  ExecutionTime %6.2fx   ClockTime %6.2fx" % (lv, w, wc))
    print("\n  D2.1 REPORTING CONDITION: a wall factor measured over 40 RAMP steps does")
    print("  NOT establish that the ladder fits inside 20,000 core-min. The ladder runs")
    print("  11,800-47,200 steps and this is the ramp, not the soak. The pressure-share")
    print("  bracket [20.9, 156.8] is a PRESSURE-SOLVE factor and is not quoted here.")
    json.dump({"arm": arm, "spread": out.get(arm), "threshold": P3_THRESHOLD,
               "B0_spread": out.get("B0"),
               "verdict": (None if out.get(arm) is None else
                           ("P-3 WINS" if out[arm] <= P3_THRESHOLD else "P-3 LOSES")),
               "rows": {"%s_%s" % k: v for k, v in rows.items()}},
              open(os.path.join(HERE, "P3_SCORE.json"), "w"), indent=2, sort_keys=True)
    print("\n  written P3_SCORE.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
