#!/usr/bin/env python3
"""T25R4 LADDER GATE -- the FIRST ACTION of every queued ladder entry.

⛔ DEFAULT-DENY.  This exists because a queue entry that says "run the ladder"
and relies on a person not releasing it on a FAIL is not a gate, it is an
intention.  The gate is INSIDE the job.

It (prereg A1.4, in this order and it may not reorder them):
  1. reads G-P's verdict VALUE from GP_VERDICT.json and REFUSES unless it is
     literally "PASS" -- a missing file, unparseable JSON, an absent field, or
     any other verdict all REFUSE;
  2. reads the probe's measured s_per_step;
  3. computes POINT / CAP / timeout from the FORMULA FROZEN AT A1.1;
  4. REFUSES if the total CAP exceeds the A1.3 ceiling of 20,000 core-min;
  5. prints the priced plan.
Exit 0 = cleared to launch.  Any non-zero = do not launch.

    python3 ladder_gate_t25R4.py --run S3
    python3 ladder_gate_t25R4.py --selftest
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
VERDICT = os.path.join(HERE, "GP_VERDICT.json")
EXIT_REFUSE = 3

# --- FROZEN AT PREREG A1.1.  Changing a number here without amending the
# --- pre-registration is a silent re-pricing and is forbidden.
M_MARGIN = 4.0
RANKS = 2
CEILING_CORE_MIN = 20000.0
N_STEPS = {"S1": 11800, "S2": 11800, "S3": 11800,
           "T2": 23600, "T4": 47200, "W30": 11800}
LEVEL = {"S1": "L1", "S2": "L2", "S3": "L3",
         "T2": "L2", "T4": "L2", "W30": "L2"}
SWEEP = {"S1": 1.0, "S2": 1.0, "S3": 1.0, "T2": 1.0, "T4": 1.0, "W30": 2.0}


def refuse(msg, code=EXIT_REFUSE):
    print("REFUSE: " + msg)
    sys.exit(code)


def read_verdict(path):
    if not os.path.isfile(path):
        refuse("G-P verdict artifact %s DOES NOT EXIST. Default-deny: the "
               "absence of a gate result is not a pass." % path)
    try:
        d = json.load(open(path))
    except Exception as e:
        refuse("G-P verdict artifact %s is UNPARSEABLE (%s). Default-deny."
               % (path, e))
    if not isinstance(d, dict) or "verdict" not in d:
        refuse("G-P verdict artifact %s carries no `verdict` field. "
               "Default-deny." % path)
    v = d["verdict"]
    if v != "PASS":
        refuse("G-P verdict is %r, not PASS. The ladder does not launch "
               "(prereg §2.2). ratio=%r threshold=%r notes=%r"
               % (v, d.get("ratio"), d.get("threshold"), d.get("notes")))
    for lv in ("L1", "L2", "L3"):
        if lv not in d.get("s_per_step", {}):
            refuse("G-P PASSED but s_per_step[%s] is absent, so the frozen "
                   "pricing formula has no input. Default-deny." % lv)
        if not (d["s_per_step"][lv] > 0):
            refuse("s_per_step[%s] = %r is not positive" % (lv, d["s_per_step"][lv]))
    return d


def price(d):
    out, total = {}, 0.0
    for run in sorted(N_STEPS):
        r = d["s_per_step"][LEVEL[run]]
        point = N_STEPS[run] * r * SWEEP[run] * RANKS / 60.0
        cap = M_MARGIN * point
        out[run] = dict(point_core_min=round(point, 3),
                        cap_core_min=round(cap, 1),
                        timeout_s=int(cap * 60 / RANKS))
        total += cap
    return out, total


def gate(run, path=None):
    path = VERDICT if path is None else path
    if run not in N_STEPS:
        refuse("%r is not one of the six registered ladder runs" % run)
    d = read_verdict(path)
    priced, total = price(d)
    if total > CEILING_CORE_MIN:
        refuse("total CAP %.0f core-min EXCEEDS the A1.3 ceiling of %.0f. The "
               "ladder REFUSES and escalates to the supervisor rather than "
               "auto-launching a spend this size." % (total, CEILING_CORE_MIN))
    p = priced[run]
    print("G-P PASS (ratio %.3f <= %.1f). %s CLEARED."
          % (d["ratio"], d["threshold"], run))
    print("  POINT %.3f core-min  CAP %.1f  timeout %d s  (total ladder CAP "
          "%.0f, ceiling %.0f)" % (p["point_core_min"], p["cap_core_min"],
                                   p["timeout_s"], total, CEILING_CORE_MIN))
    return 0


def selftest():
    import tempfile, shutil
    fails = [0]
    def chk(n, c):
        print("  %-4s %s" % ("ok" if c else "FAIL", n))
        if not c: fails[0] += 1
    def run_gate(p, run="S3"):
        try:
            return gate(run, p)
        except SystemExit as e:
            return e.code
    tmp = tempfile.mkdtemp(prefix="gate_")
    try:
        good = dict(gate="G-P", verdict="PASS", ratio=2.1, threshold=3.0,
                    s_per_step={"L1": 0.2, "L2": 0.45, "L3": 1.0})
        p = os.path.join(tmp, "pass.json"); json.dump(good, open(p, "w"))
        chk("PLANTED PASS -> the entry is CLEARED (exit 0)", run_gate(p) == 0)
        for v in ("GATE FAIL", "NOT A RESULT", "pass", "PASSED", "", None):
            q = os.path.join(tmp, "v.json")
            json.dump(dict(good, verdict=v), open(q, "w"))
            chk("PLANTED verdict %r -> REFUSES" % (v,), run_gate(q) == EXIT_REFUSE)
        chk("MISSING artifact -> REFUSES (absence is not a pass)",
            run_gate(os.path.join(tmp, "nope.json")) == EXIT_REFUSE)
        bad = os.path.join(tmp, "bad.json"); open(bad, "w").write("{not json")
        chk("UNPARSEABLE artifact -> REFUSES", run_gate(bad) == EXIT_REFUSE)
        nof = os.path.join(tmp, "nof.json"); json.dump({"gate": "G-P"}, open(nof, "w"))
        chk("artifact with NO `verdict` field -> REFUSES", run_gate(nof) == EXIT_REFUSE)
        nos = os.path.join(tmp, "nos.json")
        json.dump(dict(gate="G-P", verdict="PASS", ratio=1.0, threshold=3.0),
                  open(nos, "w"))
        chk("PASS but NO s_per_step -> REFUSES (formula has no input)",
            run_gate(nos) == EXIT_REFUSE)
        big = os.path.join(tmp, "big.json")
        json.dump(dict(good, s_per_step={"L1": 5.0, "L2": 12.0, "L3": 30.0}),
                  open(big, "w"))
        chk("PASS but the priced total BREACHES the 20,000 core-min ceiling "
            "-> REFUSES and escalates", run_gate(big) == EXIT_REFUSE)
        chk("an unregistered run id -> REFUSES", run_gate(p, "S9") == EXIT_REFUSE)
        pr, tot = price(good)
        chk("the frozen formula reproduces by hand for T4: "
            "47200 x 1.0 x 2 x 0.45/60 = %.3f" % (47200 * 0.45 * 2 / 60),
            abs(pr["T4"]["point_core_min"] - 47200 * 0.45 * 2 / 60) < 0.01)
        chk("W30 carries the registered SWEEP factor of 2.0",
            abs(pr["W30"]["point_core_min"]
                - 2.0 * 11800 * 0.45 * 2 / 60) < 0.01)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("\nSELFTEST %s (%d failed)" % ("PASS" if not fails[0] else "FAIL", fails[0]))
    return 0 if not fails[0] else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    i = sys.argv.index("--run")
    sys.exit(gate(sys.argv[i + 1]))
