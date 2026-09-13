#!/usr/bin/env python3
"""D6R3 FIX GRADER -- the grading path fixed at the D6R3_FIX_PREREGISTRATION.md commit (rule 2).

It refuses (exit 2) rather than degrade.  It carries a planted control: --selftest mutates a real
log in memory and requires the reader to REPORT the mutation before any silence of this reader is
believed (rule 3).

usage: d6r3_fix_grade.py <arm> <log>            # FIX_RELTOL1 | FIX_NONGAMG1
       d6r3_fix_grade.py --selftest <log>
"""
import json
import re
import sys

TOL = 1.0e-8          # primalMinResTol, UNCHANGED
DIFF = 100.0          # primalMinResTolDiff, UNCHANGED
GATE = TOL * DIFF     # 1.0e-06

# IC-1, verbatim from P00_20260913T192711Z.log step 1
IC1 = {
    "U0": ("0.9999999999999968", "0.0944846591692384", 2),
    "U1": ("1", "0.01212907860710623", 2),
    "U2": ("1", "0.09448777862426254", 2),
    "he": ("0.999999999993853", "0.08587891623171072", 2),
}
IC1_P_INITRES = "0.9999999999942178"
PUB_P = {1: ("0.09743304254827717", 24), 2: ("0.09727830036032596", 21)}
CD_CL04 = 0.02090109066417552      # P0 position-1 converged CD
FIELDS = ("U0", "U1", "U2", "he", "p", "nuTilda")

RES = re.compile(r"^(\w+) initRes: (\S+) finalRes: (\S+) nIters: (\d+)\s*$")
CD = re.compile(r"^CD: (\S+) final: (\S+)\s*$")


def parse(text):
    """Split a run_model log into instances by the step counter restarting."""
    t, rows = None, []
    for ln in text.splitlines():
        if ln.startswith("Time = "):
            v = ln.split("=")[1].strip()
            if v == "0":
                continue
            t = int(v)
            continue
        m = RES.match(ln)
        if m and t is not None:
            rows.append((t, m.group(1), m.group(2), m.group(3), int(m.group(4))))
            continue
        m = CD.match(ln)
        if m and t is not None:
            rows.append((t, "CD", m.group(1), m.group(1), 0))
    inst, cur, last = [], [], 0
    for r in rows:
        if r[0] < last and cur:
            inst.append(cur)
            cur = []
        cur.append(r)
        last = r[0]
    if cur:
        inst.append(cur)
    return inst


def grade(arm, text, rc=None):
    out = {"arm": arm, "gate_abs": GATE, "instances": [], "checks": [], "verdict": None}

    def chk(name, ok, detail):
        out["checks"].append({"check": name, "ok": bool(ok), "detail": detail})
        return ok

    inst = parse(text)
    if not inst:
        out["verdict"] = "NOT A RESULT"
        chk("PARSE", False, "no instance found in log")
        return out

    ic_ok = True
    for i, rows in enumerate(inst, 1):
        s1 = {r[1]: r for r in rows if r[0] == 1}
        for f, (a, b, n) in IC1.items():
            r = s1.get(f)
            good = r is not None and r[2] == a and r[3] == b and r[4] == n
            ic_ok &= chk("IC-1 inst%d %s" % (i, f), good,
                         "printed %s, registered initRes=%s finalRes=%s nIters=%d"
                         % (None if r is None else "initRes=%s finalRes=%s nIters=%d" % r[2:5],
                            a, b, n))
        rp = s1.get("p")
        ic_ok &= chk("IC-1 inst%d p initRes" % i, rp is not None and rp[2] == IC1_P_INITRES,
                     "printed %s, registered %s" % (None if rp is None else rp[2], IC1_P_INITRES))
        if arm == "FIX_RELTOL1" and rp is not None and i in PUB_P:
            pf, pn = PUB_P[i]
            ic_ok &= chk("IC-2 inst%d nIters > %d" % (i, pn), rp[4] > pn,
                         "printed nIters=%d, published %d (equal means the staged fvSolution "
                         "never reached the solver)" % (rp[4], pn))
            ic_ok &= chk("IC-2 inst%d finalRes < %s" % (i, pf), float(rp[3]) < float(pf),
                         "printed finalRes=%s, published %s" % (rp[3], pf))

        last_t = max(r[0] for r in rows)
        at_end = {r[1]: r for r in rows if r[0] == last_t}
        res = {f: float(at_end[f][2]) for f in FIELDS if f in at_end}
        maxf = max(res, key=res.get) if res else None
        cd = at_end.get("CD")
        rec = {
            "position": i, "last_time": last_t,
            "residuals_at_last_time": {f: "%.16g" % v for f, v in res.items()},
            "max_field": maxf,
            "max_residual": None if maxf is None else "%.16g" % res[maxf],
            "multiple_of_primalMinResTol": None if maxf is None else round(res[maxf] / TOL, 4),
            "passes_gate": None if maxf is None else bool(res[maxf] < GATE),
            "step1_p": None if rp is None else {"initRes": rp[2], "finalRes": rp[3], "nIters": rp[4]},
            "CD": None if cd is None else cd[2],
        }
        out["instances"].append(rec)
        if i == 1 and cd is not None:
            ic_ok &= chk("IC-3 CD(cl04) 4 s.f.",
                         abs(float(cd[2]) - CD_CL04) / CD_CL04 < 5e-5,
                         "printed %s, P0 %.16g" % (cd[2], CD_CL04))

    if rc is not None:
        ic_ok &= chk("IC-4 rc == 0", rc == 0, "rc=%s" % rc)
    failed = "Primal solution failed!" in text
    out["primal_solution_failed_raised"] = failed

    if arm == "FIX_NONGAMG1":
        a = out["instances"][0]["step1_p"] if len(out["instances"]) > 0 else None
        b = out["instances"][1]["step1_p"] if len(out["instances"]) > 1 else None
        if a is None or b is None:
            out["ordinal_signature"] = "UNDECIDED (fewer than two instances reached step 1)"
            out["verdict"] = "NOT A RESULT"
            return out
        same = (a["finalRes"] == b["finalRes"]) and (a["nIters"] == b["nIters"])
        out["ordinal_signature"] = "VANISHED" if same else "PERSISTS"
        out["hypothesis"] = "H-REMOVE (mechanism confirmed by removal)" if same \
            else "H-REMOVE-DEAD (agglomeration attribution is WRONG)"
        out["verdict"] = "GATE REACHED" if ic_ok else "NOT A RESULT"
        return out

    if not ic_ok:
        out["verdict"] = "NOT A RESULT"
        return out
    n_done = sum(1 for r in out["instances"] if r["last_time"] == 2000)
    all_pass = (len(out["instances"]) == 3 and n_done == 3 and not failed
                and all(r["passes_gate"] for r in out["instances"]))
    out["verdict"] = "PASS" if all_pass else "GATE FAIL"
    return out


def selftest(path):
    text = open(path).read()
    base = grade("FIX_RELTOL1", text, rc=1)
    mutated = text.replace("p initRes: 0.9999999999942178", "p initRes: 0.9999999999942179", 1)
    if mutated == text:
        print("SELFTEST REFUSE: could not plant the mutation", file=sys.stderr)
        sys.exit(2)
    mut = grade("FIX_RELTOL1", mutated, rc=1)
    saw = [c for c in mut["checks"] if c["check"].endswith("p initRes") and not c["ok"]]
    print(json.dumps({"selftest_log": path,
                      "control_verdict": base["verdict"],
                      "planted": "p initRes ...78 -> ...79 (one digit, instance 1)",
                      "reader_reported_the_plant": bool(saw),
                      "plant_detail": saw[0]["detail"] if saw else None,
                      "mutated_verdict": mut["verdict"]}, indent=2))
    if not saw:
        print("SELFTEST REFUSE: the reader could not see a planted difference; "
              "no silence of this reader is evidence (rule 3)", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--selftest":
        selftest(sys.argv[2])
    elif len(sys.argv) in (3, 4):
        rc = int(sys.argv[3]) if len(sys.argv) == 4 else None
        print(json.dumps(grade(sys.argv[1], open(sys.argv[2]).read(), rc), indent=2))
    else:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
