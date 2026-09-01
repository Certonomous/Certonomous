#!/usr/bin/env python3
"""T25R4 PROBE GRADER -- decides G-P and writes GP_VERDICT.json (prereg A2.1).

G-P PASSES iff max(mean GAMG iterations per p_rgh solve) / min(...) <= 3.0
across P1, P2, P3.  A probe level that did not complete its 100 registered steps,
or whose rc is non-zero, makes G-P `NOT A RESULT` -- a gate that can only say
PASS or FAIL cannot express "the probe itself did not run".

    python3 grade_probe_t25R4.py            # grade and write the artifact
    python3 grade_probe_t25R4.py --selftest
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
FROZEN_DOC = "docs/campaigns/T-family/T25R4_PREREGISTRATION.md"
LEVELS = {"P1": "L1", "P2": "L2", "P3": "L3"}
STEPS = 100
THRESHOLD = 3.0
OUT = os.path.join(HERE, "GP_VERDICT.json")


def _blob():
    r = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD:" + FROZEN_DOC],
                       capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def grade(root=None, out=None):
    root = HERE if root is None else root
    out = OUT if out is None else out
    mean, sps, steps, notes = {}, {}, {}, []
    verdict = "PASS"
    for run, lv in LEVELS.items():
        case = os.path.join(root, run)
        log = os.path.join(case, "log.solve.legA")
        rcf = os.path.join(case, ".rc.%s.legA" % run)
        if not os.path.isfile(log):
            notes.append("%s: no solver log" % run); verdict = "NOT A RESULT"; continue
        txt = open(log).read()
        if not os.path.isfile(rcf):
            notes.append("%s: rc NOT RECORDED" % run); verdict = "NOT A RESULT"
        else:
            rc = open(rcf).read().strip()
            if rc != "0":
                notes.append("%s: rc=%s" % (run, rc)); verdict = "NOT A RESULT"
        ex = re.findall(r"^ExecutionTime = ([0-9.eE+-]+) s", txt, re.M)
        steps[lv] = len(ex)
        if len(ex) != STEPS:
            notes.append("%s: %d/%d registered steps" % (run, len(ex), STEPS))
            verdict = "NOT A RESULT"
        if re.search(r"FOAM FATAL", txt):
            notes.append("%s: FOAM FATAL" % run); verdict = "NOT A RESULT"
        its = [int(m) for m in
               re.findall(r"Solving for p_rgh,.*?No Iterations (\d+)", txt)]
        if not its:
            notes.append("%s: no p_rgh solves" % run); verdict = "NOT A RESULT"; continue
        mean[lv] = sum(its) / len(its)
        if ex:
            sps[lv] = float(ex[-1]) / len(ex)
    ratio = None
    if verdict != "NOT A RESULT" and len(mean) == 3 and min(mean.values()) > 0:
        ratio = max(mean.values()) / min(mean.values())
        verdict = "PASS" if ratio <= THRESHOLD else "GATE FAIL"
    elif verdict != "NOT A RESULT":
        verdict = "NOT A RESULT"
        notes.append("a level reported a zero or missing mean; the ratio is undefined")
    doc = {"gate": "G-P", "verdict": verdict, "ratio": ratio,
           "threshold": THRESHOLD, "mean_iters": mean, "s_per_step": sps,
           "steps_counted": steps, "prereg_blob": _blob(), "notes": notes}
    with open(out, "w") as f:
        json.dump(doc, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps(doc, indent=2, sort_keys=True))
    return doc


def selftest():
    import tempfile, shutil
    fails = [0]
    def chk(n, c):
        print("  %-4s %s" % ("ok" if c else "FAIL", n))
        if not c: fails[0] += 1
    tmp = tempfile.mkdtemp(prefix="gp_")
    def forge(root, iters, steps=STEPS, rc="0", fatal=False):
        for run, lv in LEVELS.items():
            d = os.path.join(root, run); os.makedirs(d, exist_ok=True)
            L = ["Time = %g" % (i * 0.02) for i in range(1)]
            for i in range(steps):
                L.append("GAMG:  Solving for p_rgh, Initial residual = 1e-3, "
                         "Final residual = 1e-6, No Iterations %d" % iters[lv])
                L.append("ExecutionTime = %.2f s  ClockTime = 1 s" % (i + 1))
            if fatal: L.append("--> FOAM FATAL ERROR:")
            L.append("End")
            open(os.path.join(d, "log.solve.legA"), "w").write("\n".join(L))
            open(os.path.join(d, ".rc.%s.legA" % run), "w").write(rc + "\n")
        return root
    try:
        a = forge(os.path.join(tmp, "pass"), {"L1": 10, "L2": 20, "L3": 25})
        d = grade(a, os.path.join(a, "v.json"))
        chk("PASS when the spread is 2.5 (<= 3.0)", d["verdict"] == "PASS"
            and abs(d["ratio"] - 2.5) < 1e-9)
        b = forge(os.path.join(tmp, "fail"), {"L1": 10, "L2": 20, "L3": 40})
        d = grade(b, os.path.join(b, "v.json"))
        chk("GATE FAIL when the spread is 4.0 (> 3.0)", d["verdict"] == "GATE FAIL")
        c = forge(os.path.join(tmp, "short"), {"L1": 10, "L2": 12, "L3": 14}, steps=50)
        d = grade(c, os.path.join(c, "v.json"))
        chk("NOT A RESULT when a level is short of its 100 registered steps",
            d["verdict"] == "NOT A RESULT")
        e = forge(os.path.join(tmp, "rc"), {"L1": 10, "L2": 12, "L3": 14}, rc="124")
        d = grade(e, os.path.join(e, "v.json"))
        chk("NOT A RESULT on a cap stop (rc=124), even with a fine ratio",
            d["verdict"] == "NOT A RESULT")
        f = forge(os.path.join(tmp, "fat"), {"L1": 10, "L2": 12, "L3": 14}, fatal=True)
        d = grade(f, os.path.join(f, "v.json"))
        chk("NOT A RESULT on FOAM FATAL", d["verdict"] == "NOT A RESULT")
        g = os.path.join(tmp, "empty"); os.makedirs(g)
        d = grade(g, os.path.join(g, "v.json"))
        chk("NOT A RESULT when the probe never ran at all",
            d["verdict"] == "NOT A RESULT")
        chk("the boundary is INCLUSIVE at exactly 3.0",
            grade(forge(os.path.join(tmp, "edge"), {"L1": 10, "L2": 20, "L3": 30}),
                  os.path.join(tmp, "edge", "v.json"))["verdict"] == "PASS")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("\nSELFTEST %s (%d failed)" % ("PASS" if not fails[0] else "FAIL", fails[0]))
    return 0 if not fails[0] else 1


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else (grade() and 0))
