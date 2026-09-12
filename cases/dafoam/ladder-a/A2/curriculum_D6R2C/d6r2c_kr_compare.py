#!/usr/bin/env python
"""D6R2C -- the kill-and-resume comparator.  Sanaa 2026-09-12, Checkpoints
item 5: "one kill-and-resume test on one case per solver class, once, before
the fleet launches anything; the resumed result must match an unkilled
reference to the solver's tolerance."

THE SOLVER CLASS THIS PROVES: DAFoam optimisation (pyOptSparse/IPOPT driving
DARhoSimpleFoam primals and their adjoints under mphys/OpenMDAO).

WHAT IT READS, AND NOTHING ELSE
  <base>/KR_REF/   the unkilled reference, cold, max_iter 4
  <base>/KR_KILL/  a cold run SIGKILLed at IPOPT major 2
  <base>/KR_RES/   hot-started from KR_KILL's history, max_iter 4

THE GATES ARE FROZEN IN PREREGISTRATION.md SECTION 5 AND REPRODUCED HERE.
Any change to a threshold in this file without the matching dated addendum is
a rule-2 violation and `--print-gates` exists so a reader can diff them.

REFUSAL, NEVER DEGRADATION.  A missing artefact, an unreadable history or an
unfireable control exits 2.  No number is printed from a run that did not
finish, and no verdict is softened.

THE PLANTED CONTROL (CLAUDE.md rule 3).  `--plant <name>` perturbs the value
this comparator READ BACK FROM DISK for the resumed run by PLANT = 1.234e-03
and REQUIRES the verdict to leave PASS.  A comparator that cannot see a
planted disagreement cannot certify an agreement, and its zero is not
evidence.  `--selftest` drives every control in both directions on synthetic
inputs and touches no run directory at all.
"""
import os
import sys
import json
import math
import argparse

PLANT = 1.234e-03

# ---- FROZEN TOLERANCES (PREREGISTRATION.md section 5).  "The solver's
# ---- tolerance" is not a free choice: the primal is converged to
# ---- primalMinResTol = 1.0e-8 and IPOPT's own function precision on this
# ---- problem is tol = 1.0e-5.  A resumed run whose first REAL primal starts
# ---- from a different field state than the reference's cannot be bitwise
# ---- identical and is not claimed to be; it must agree to the precision the
# ---- solver itself delivers.  These are those numbers and they are registered
# ---- BEFORE the test runs.
TOL_J_REL = 1.0e-5      # weighted composite objective, relative
TOL_CD_REL = 1.0e-5     # each condition's CD, relative
TOL_CL_ABS = 1.0e-6     # each condition's CL, absolute (CL ~ 0.4-0.6)
TOL_DV_ABS = 1.0e-6     # design vector, absolute, on the scaled DVs
TOL_X0_ABS = 1.0e-12    # hot-start x0 identity (enforced again in the run script)

GATES = {
    "KR-G1 MECHANISM ENGAGED": (
        "KR_RES's X0 guard line is present with worst_abs_diff <= 1.0e-12, AND KR_RES "
        "performed STRICTLY FEWER real (non-replayed) evaluations than KR_REF. A resumed "
        "run that re-evaluated everything did not hot-start, whatever its numbers say."),
    "KR-G2 REPLAY EXACT": (
        "for every call counter in KR_KILL's history, KR_RES's history entry carries "
        "BITWISE IDENTICAL objective and constraint values. pyoptsparse dumps the cached "
        "dictionary back out, so anything else means the cache was not used."),
    "KR-G3 THE ANSWER MATCHES": (
        "at the final common IPOPT major: |dJ|/J <= 1.0e-5, |dCD_i|/CD_i <= 1.0e-5, "
        "|dCL_i| <= 1.0e-6, max|dx_j| <= 1.0e-6, KR_RES against KR_REF."),
    "KR-G4 BOTH RUNS COMPLETED, AS UBUNTU": (
        "rc=0 for KR_REF and KR_RES; both opt_IPOPT.txt carry "
        "'Number of Iterations....: 4' and 'EXIT: Maximum Number of Iterations Exceeded.'; "
        "every graded artefact strictly newer than its own arm's age datum; ZERO root-owned "
        "files written by either run (Sanaa Launch item 6)."),
}
LABELS = ("PASS", "GATE FAIL", "NOT A RESULT")


def refuse(msg, code=2):
    print("D6R2C_KR REFUSE: %s" % msg)
    sys.exit(code)


# --------------------------------------------------------------------------- readers
def read_hist(path):
    """Return {callCounter: {'funcs': {...}, 'xuser': {...}}} from a pyoptsparse History."""
    try:
        from pyoptsparse.pyOpt_history import History
    except Exception as e:
        refuse("pyoptsparse is not importable (%s); run this inside the registered image." % e)
    if not os.path.exists(path):
        refuse("history %s does not exist" % path)
    h = History(path, temp=False, flag="r")
    out = {}
    for c in h.getCallCounters():
        try:
            n = int(c)
        except (TypeError, ValueError):
            continue
        d = h.read(n)
        if not isinstance(d, dict):
            continue
        out[n] = {"funcs": d.get("funcs", {}), "xuser": d.get("xuser", {}),
                  "isMajor": bool(d.get("isMajor", False)), "fail": d.get("fail", None)}
    h.close()
    if not out:
        refuse("history %s holds no call counters" % path)
    return out


def read_jsonl(path):
    if not os.path.exists(path):
        refuse("evaluation log %s does not exist" % path)
    rows = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def read_ipopt(path):
    if not os.path.exists(path):
        refuse("%s does not exist" % path)
    return open(path, errors="replace").read()


def flat(d):
    """Flatten a funcs/xuser dict of scalars-or-lists to {key: [floats]}."""
    out = {}
    for k, v in (d or {}).items():
        if isinstance(v, (list, tuple)):
            out[str(k)] = [float(x) for x in v]
        elif hasattr(v, "flatten"):
            out[str(k)] = [float(x) for x in v.flatten()]
        else:
            try:
                out[str(k)] = [float(v)]
            except (TypeError, ValueError):
                pass
    return out


def pick(d, needle):
    """The one key whose last dotted segment is `needle`, or whose name ends in it."""
    for k in d:
        if k == needle or k.split(".")[-1] == needle:
            return k
    for k in d:
        if needle in k:
            return k
    return None


# --------------------------------------------------------------------------- gates
def evaluate(ref_hist, kill_hist, res_hist, ref_rows, res_rows,
             ref_ipopt, res_ipopt, ref_rc, res_rc, ref_root_owned, res_root_owned,
             plant=None):
    """Returns (label, findings, numbers).  Pure: it touches no disk."""
    F = []          # (gate, ok, text)
    N = {}

    # ---------------------------------------------------------------- KR-G4
    g4 = True
    for nm, rc in (("KR_REF", ref_rc), ("KR_RES", res_rc)):
        if rc != 0:
            F.append(("KR-G4", False, "%s rc=%s (want 0)" % (nm, rc))); g4 = False
    for nm, txt in (("KR_REF", ref_ipopt), ("KR_RES", res_ipopt)):
        if "Number of Iterations....: 4" not in txt:
            F.append(("KR-G4", False, "%s opt_IPOPT.txt lacks 'Number of Iterations....: 4'" % nm)); g4 = False
        if "EXIT: Maximum Number of Iterations Exceeded." not in txt:
            bad = [l for l in txt.splitlines() if l.startswith("EXIT:")]
            F.append(("KR-G4", False, "%s did not hit the iteration cap; EXIT lines: %s" % (nm, bad or "NONE"))); g4 = False
    for nm, n in (("KR_REF", ref_root_owned), ("KR_RES", res_root_owned)):
        if n != 0:
            F.append(("KR-G4", False, "%s wrote %d root-owned files (Sanaa Launch item 6)" % (nm, n))); g4 = False
    if g4:
        F.append(("KR-G4", True, "rc=0 both; both terminated at the iteration cap; 0 root-owned files"))

    # ---------------------------------------------------------------- KR-G1
    g1 = True
    x0rows = [r for r in res_rows if r.get("kind") == "X0_GUARD"]
    if not x0rows:
        F.append(("KR-G1", False, "KR_RES wrote no X0_GUARD row -- the resume never checked where it started")); g1 = False
    else:
        w = float(x0rows[-1]["worst_abs_diff"]); N["x0_worst_abs_diff"] = w
        if w > TOL_X0_ABS:
            F.append(("KR-G1", False, "X0 guard worst_abs_diff %.3e > %.1e" % (w, TOL_X0_ABS))); g1 = False
        else:
            F.append(("KR-G1", True, "X0 guard worst_abs_diff %.3e <= %.1e" % (w, TOL_X0_ABS)))
    n_ref_real = len([r for r in ref_rows if r.get("kind") in ("F", "G")])
    n_res_real = len([r for r in res_rows if r.get("kind") in ("F", "G")])
    N["real_evals_ref"] = n_ref_real
    N["real_evals_res"] = n_res_real
    N["replayed_available"] = len(kill_hist)
    if n_res_real >= n_ref_real:
        F.append(("KR-G1", False,
                  "KR_RES ran %d real evaluations against KR_REF's %d -- the hot start saved nothing, "
                  "so this is a cold restart wearing a resume's name" % (n_res_real, n_ref_real))); g1 = False
    else:
        F.append(("KR-G1", True, "KR_RES ran %d real evaluations against KR_REF's %d; %d were served "
                                 "from the killed run's history" % (n_res_real, n_ref_real, len(kill_hist))))

    # ---------------------------------------------------------------- KR-G2
    g2 = True
    common = sorted(set(kill_hist) & set(res_hist))
    N["replay_counters_checked"] = len(common)
    if not common:
        F.append(("KR-G2", False, "KR_RES's history shares no call counter with KR_KILL's")); g2 = False
    worst_replay = 0.0
    for c in common:
        a = flat(kill_hist[c]["funcs"]); b = flat(res_hist[c]["funcs"])
        if set(a) != set(b):
            F.append(("KR-G2", False, "call %d: key sets differ %s vs %s" % (c, sorted(a), sorted(b)))); g2 = False
            continue
        for k in a:
            if len(a[k]) != len(b[k]):
                F.append(("KR-G2", False, "call %d key %s length %d vs %d" % (c, k, len(a[k]), len(b[k])))); g2 = False
                continue
            for u, v in zip(a[k], b[k]):
                if u != v:            # BITWISE. a cached dump that changed was not a cached dump.
                    worst_replay = max(worst_replay, abs(u - v))
                    g2 = False
    N["replay_worst_abs_diff"] = worst_replay
    if g2:
        F.append(("KR-G2", True, "%d replayed call counters bitwise identical to KR_KILL's history" % len(common)))
    elif worst_replay:
        F.append(("KR-G2", False, "replayed values are NOT bitwise identical; worst |diff| %.3e" % worst_replay))

    # ---------------------------------------------------------------- KR-G3
    g3 = True
    ref_last = max(ref_hist); res_last = max(res_hist)
    rf = flat(ref_hist[ref_last]["funcs"]); sf = flat(res_hist[res_last]["funcs"])
    rx = flat(ref_hist[ref_last]["xuser"]); sx = flat(res_hist[res_last]["xuser"])
    N["final_call_ref"] = ref_last
    N["final_call_res"] = res_last

    def val(d, needle):
        k = pick(d, needle)
        return (k, d[k]) if k else (None, None)

    # objective J
    kJ, vJ = val(rf, "J"); _, wJ = val(sf, "J")
    if vJ is None or wJ is None:
        F.append(("KR-G3", False, "no objective key found in one of the histories (ref keys %s)" % sorted(rf))); g3 = False
    else:
        jr, js = vJ[0], wJ[0]
        if plant == "J":
            js = js + PLANT
        rel = abs(js - jr) / abs(jr) if jr else float("inf")
        N["J_ref"] = jr; N["J_res"] = js; N["J_rel_diff"] = rel
        ok = rel <= TOL_J_REL
        g3 &= ok
        F.append(("KR-G3", ok, "J ref %.12e res %.12e rel %.3e vs %.1e" % (jr, js, rel, TOL_J_REL)))

    for pt, tgt in (("cl04", 0.4), ("cl05", 0.5), ("cl06", 0.6)):
        for q, tol, mode in (("CD", TOL_CD_REL, "rel"), ("CL", TOL_CL_ABS, "abs")):
            kr = pick(rf, "%s.aero_post.%s" % (pt, q)) or pick(rf, "%s_%s" % (pt, q))
            ks = pick(sf, "%s.aero_post.%s" % (pt, q)) or pick(sf, "%s_%s" % (pt, q))
            if not kr or not ks:
                continue
            a, b = rf[kr][0], sf[ks][0]
            if plant == "%s_%s" % (pt, q):
                b = b + PLANT
            d = abs(b - a) / abs(a) if (mode == "rel" and a) else abs(b - a)
            N["%s_%s_ref" % (pt, q)] = a; N["%s_%s_res" % (pt, q)] = b
            N["%s_%s_diff" % (pt, q)] = d
            ok = d <= tol
            g3 &= ok
            F.append(("KR-G3", ok, "%s %s ref %.12e res %.12e %s %.3e vs %.1e" % (pt, q, a, b, mode, d, tol)))

    worst_dv = 0.0; worst_dv_key = None
    for k in sorted(rx):
        ks = pick(sx, k)
        if not ks or len(sx[ks]) != len(rx[k]):
            F.append(("KR-G3", False, "design variable %s missing or mis-sized in KR_RES" % k)); g3 = False
            continue
        for i, (a, b) in enumerate(zip(rx[k], sx[ks])):
            if plant == "dv" and k == sorted(rx)[0] and i == 0:
                b = b + PLANT
            if abs(b - a) > worst_dv:
                worst_dv = abs(b - a); worst_dv_key = "%s[%d]" % (k, i)
    N["dv_worst_abs_diff"] = worst_dv; N["dv_worst_key"] = worst_dv_key
    ok = worst_dv <= TOL_DV_ABS
    g3 &= ok
    F.append(("KR-G3", ok, "design vector worst |diff| %.3e at %s vs %.1e" % (worst_dv, worst_dv_key, TOL_DV_ABS)))

    # ---------------------------------------------------------------- label
    if not (g1 and g4):
        label = "NOT A RESULT"
    elif g2 and g3:
        label = "PASS"
    else:
        label = "GATE FAIL"
    return label, F, N


# --------------------------------------------------------------------------- selftest
def _synth():
    """Synthetic inputs with the shape the real readers produce.  No run directory
    is touched; nothing here reads disk."""
    def funcs(j, cd, cl):
        return {"obj.J": j,
                "cl04.aero_post.CD": cd, "cl04.aero_post.CL": cl,
                "cl05.aero_post.CD": cd * 1.1, "cl05.aero_post.CL": cl + 0.1,
                "cl06.aero_post.CD": cd * 1.2, "cl06.aero_post.CL": cl + 0.2}
    x = {"shape": [0.1, -0.2, 0.3], "twist": [1.0, 2.0]}
    kill = {n: {"funcs": funcs(3.0e-2 - n * 1e-4, 2.0e-2, 0.4), "xuser": x,
                "isMajor": True, "fail": 0} for n in range(0, 5)}
    ref = dict(kill)
    ref.update({n: {"funcs": funcs(3.0e-2 - n * 1e-4, 2.0e-2, 0.4), "xuser": x,
                    "isMajor": True, "fail": 0} for n in range(5, 10)})
    res = dict(kill)
    res.update({n: {"funcs": funcs(3.0e-2 - n * 1e-4, 2.0e-2, 0.4), "xuser": x,
                    "isMajor": False, "fail": 0} for n in range(5, 10)})
    ref_rows = [{"kind": "HEADER", "mode": "COLD"}] + [{"kind": "F"}] * 10 + [{"kind": "G"}] * 10
    res_rows = ([{"kind": "HEADER", "mode": "HOT"},
                 {"kind": "X0_GUARD", "worst_abs_diff": 0.0, "tol": TOL_X0_ABS}]
                + [{"kind": "F"}] * 5 + [{"kind": "G"}] * 5)
    ip = "Number of Iterations....: 4\nEXIT: Maximum Number of Iterations Exceeded.\n"
    return ref, kill, res, ref_rows, res_rows, ip


def selftest():
    import copy
    ref, kill, res, ref_rows, res_rows, ip = _synth()
    fails = []

    def run(tag, want, **kw):
        a = dict(ref_hist=ref, kill_hist=kill, res_hist=res, ref_rows=ref_rows,
                 res_rows=res_rows, ref_ipopt=ip, res_ipopt=ip, ref_rc=0, res_rc=0,
                 ref_root_owned=0, res_root_owned=0)
        a.update(kw)
        label, F, N = evaluate(**a)
        ok = (label == want)
        print("  %-58s -> %-12s (want %-12s) %s" % (tag, label, want, "OK" if ok else "*** CONTROL DID NOT FIRE ***"))
        if not ok:
            fails.append(tag)
            for g, o, t in F:
                if not o:
                    print("        %s %s" % (g, t))
        return label

    print("D6R2C_KR SELFTEST -- every control, both directions, synthetic inputs only")
    print(" A. the clean case must PASS (a comparator that never passes proves nothing)")
    run("A1 clean reference/kill/resume", "PASS")

    print(" B. PLANTED perturbations of %.3e READ INTO the resumed record must leave PASS" % PLANT)
    for nm in ("J", "cl04_CD", "cl05_CL", "cl06_CD", "dv"):
        run("B/%s planted %.3e into KR_RES" % (nm, PLANT), "GATE FAIL", plant=nm)

    print(" C. mechanism controls -- a resume that did not resume is NOT A RESULT, not a PASS")
    run("C1 KR_RES ran as many real evaluations as KR_REF",
        "NOT A RESULT", res_rows=[{"kind": "HEADER"}, {"kind": "X0_GUARD", "worst_abs_diff": 0.0}] + [{"kind": "F"}] * 10 + [{"kind": "G"}] * 10)
    run("C2 KR_RES wrote no X0_GUARD row", "NOT A RESULT",
        res_rows=[r for r in res_rows if r.get("kind") != "X0_GUARD"])
    run("C3 X0 guard above tolerance", "NOT A RESULT",
        res_rows=[({"kind": "X0_GUARD", "worst_abs_diff": 1e-6} if r.get("kind") == "X0_GUARD" else r) for r in res_rows])

    print(" D. replay-exactness control -- a NON-bitwise replay is GATE FAIL, never PASS")
    res_b = copy.deepcopy(res)
    res_b[2]["funcs"]["obj.J"] = res_b[2]["funcs"]["obj.J"] * (1 + 1e-14)
    run("D1 one replayed value off by 1 ulp-ish", "GATE FAIL", res_hist=res_b)

    print(" E. completion controls -- these can only make a verdict WORSE, never better")
    run("E1 KR_RES rc=137", "NOT A RESULT", res_rc=137)
    run("E2 KR_REF crashed instead of hitting the cap", "NOT A RESULT",
        ref_ipopt="Number of Iterations....: 3\nEXIT: Invalid number in NLP function or derivative detected.\n")
    run("E3 KR_RES wrote 12 root-owned files", "NOT A RESULT", res_root_owned=12)

    print("")
    if fails:
        print("D6R2C_KR SELFTEST FAIL -- %d control(s) did not fire: %s" % (len(fails), fails))
        return 1
    print("D6R2C_KR SELFTEST PASS -- 13 controls, both directions, plants asserted to flip the verdict")
    return 0


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="/mnt")
    ap.add_argument("--plant", default=None,
                    help="perturb this quantity of the RESUMED record by %g after reading it from disk; "
                         "the verdict MUST leave PASS or this comparator refuses" % PLANT)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--print-gates", action="store_true")
    ap.add_argument("--json-out", default=None)
    a = ap.parse_args()

    if a.print_gates:
        for k, v in GATES.items():
            print("%s\n    %s\n" % (k, v))
        print("TOL_J_REL=%.1e TOL_CD_REL=%.1e TOL_CL_ABS=%.1e TOL_DV_ABS=%.1e TOL_X0_ABS=%.1e PLANT=%.3e"
              % (TOL_J_REL, TOL_CD_REL, TOL_CL_ABS, TOL_DV_ABS, TOL_X0_ABS, PLANT))
        return 0
    if a.selftest:
        return selftest()

    B = a.base
    ref_hist = read_hist(os.path.join(B, "KR_REF", "OptView.hst"))
    kill_hist = read_hist(os.path.join(B, "KR_KILL", "OptView.hst"))
    res_hist = read_hist(os.path.join(B, "KR_RES", "OptView.hst"))
    ref_rows = read_jsonl(os.path.join(B, "KR_REF", "d6r2c_evals.jsonl"))
    res_rows = read_jsonl(os.path.join(B, "KR_RES", "d6r2c_evals.jsonl"))
    ref_ipopt = read_ipopt(os.path.join(B, "KR_REF", "opt_IPOPT.txt"))
    res_ipopt = read_ipopt(os.path.join(B, "KR_RES", "opt_IPOPT.txt"))

    def ledger_field(arm, key, cast, default):
        p = os.path.join(B, "ledger.txt")
        if not os.path.exists(p):
            refuse("no ledger at %s; rc and ownership cannot be read and will not be assumed" % p)
        got = default
        for line in open(p, errors="replace"):
            if line.startswith("ARM=%s " % arm):
                for tok in line.split():
                    if tok.startswith(key + "="):
                        got = cast(tok.split("=", 1)[1])
        if got is default:
            refuse("ledger has no %s for ARM=%s" % (key, arm))
        return got

    ref_rc = ledger_field("KR_REF", "rc", int, None)
    res_rc = ledger_field("KR_RES", "rc", int, None)
    ref_ro = ledger_field("KR_REF", "root_owned_new_files", int, None)
    res_ro = ledger_field("KR_RES", "root_owned_new_files", int, None)

    label, F, N = evaluate(ref_hist, kill_hist, res_hist, ref_rows, res_rows,
                           ref_ipopt, res_ipopt, ref_rc, res_rc, ref_ro, res_ro, plant=None)

    # --- THE LIVE PLANTED CONTROL, on THIS run's own numbers (rule 3). ------
    plants = {}
    for nm in ("J", "cl05_CD", "dv"):
        pl, _, _ = evaluate(ref_hist, kill_hist, res_hist, ref_rows, res_rows,
                            ref_ipopt, res_ipopt, ref_rc, res_rc, ref_ro, res_ro, plant=nm)
        plants[nm] = pl
        if pl == "PASS":
            refuse("LIVE PLANT %r of %.3e into THIS run's resumed record did NOT move the verdict off "
                   "PASS. This comparator cannot see a disagreement of that size in these artefacts, "
                   "so its agreement is not evidence." % (nm, PLANT))
    print("D6R2C_KR_LIVE_PLANT plant=%.3e results=%s -- every plant left PASS, so the reader can see "
          "a disagreement in THESE artefacts" % (PLANT, plants))

    for g, ok, t in F:
        print("  %-10s %-4s %s" % (g, "OK" if ok else "MISS", t))
    print("")
    print("D6R2C_KR_VERDICT %s" % label)
    print("D6R2C_KR_NUMBERS %s" % json.dumps(N, sort_keys=True, default=str))
    if a.json_out:
        with open(a.json_out, "w") as fh:
            json.dump({"verdict": label, "numbers": N,
                       "findings": [{"gate": g, "ok": ok, "text": t} for g, ok, t in F],
                       "live_plants": plants, "plant_magnitude": PLANT,
                       "tolerances": {"J_rel": TOL_J_REL, "CD_rel": TOL_CD_REL,
                                      "CL_abs": TOL_CL_ABS, "DV_abs": TOL_DV_ABS,
                                      "X0_abs": TOL_X0_ABS}}, fh, indent=1, sort_keys=True)
    return 0 if label == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
