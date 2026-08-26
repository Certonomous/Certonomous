#!/usr/bin/env python3
"""T11 -- the FROZEN comparator. 1-D transient conduction, plane wall, Bi = 1.

SOLID ONLY. This rung earns `V` for TRANSIENT CONDUCTION and NOT for conjugate
heat transfer: there is no fluid in it. Claiming conjugate would be a tier
overclaim into the coverage matrix, which is the one place an overclaim becomes
a credential.

NO `assert` STATEMENT APPEARS IN THIS FILE. Every gate and refusal is an
explicit sys.exit(2); `assert` is stripped by `python -O` and a gate a flag can
remove is not a gate.

THE GATE CAN ONLY MAKE THINGS WORSE. Rule 5's order is walked in apply_gate(),
which is the only function here that writes a verdict.

Exit: 0 graded, 2 REFUSAL.
"""
import argparse
import json
import math
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import exact_t11 as EX                                    # the derivation

LEVELS = ("c", "m", "f")
CASES = {lv: "T11_PW_%s" % lv for lv in LEVELS}
REFINEMENT = 2.0
FS = 1.25
BI = 1.0
BAND_REL = 1.0e-4          # +/- 0.01 % relative on the FINE level, registered.
                           # NOT fitted to an answer: this is the ACCURACY CLAIM
                           # the rung makes -- "this solver on this mesh family
                           # reproduces the analytic transient to better than
                           # 0.01 %". A first draft of +/-0.05 % was rejected
                           # before freeze because a scratch probe showed the
                           # COARSE level already clearing it by 100x, and a band
                           # the coarsest mesh clears by two orders of magnitude
                           # is not a gate. Disclosed in the prereg, and the
                           # prediction that it passes is registered as P1.
PLANT = 1.234e-03
RESID_FLOOR = 1.0e-10      # max FINAL residual over all timesteps

EXIT_OK, EXIT_REFUSE = 0, 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def level_meta(case):
    p = os.path.join(HERE, case, "LEVEL.txt")
    if not os.path.isfile(p):
        refuse("no LEVEL.txt for %s" % case)
    return dict(re.findall(r"^([A-Za-z_]+)=(.*)$", open(p).read(), re.M))


def latest_time(case_dir):
    ts = [t for t in os.listdir(case_dir)
          if re.fullmatch(r"[0-9]+(\.[0-9]+)?", t) and float(t) > 0]
    return max(ts, key=float) if ts else None


# ------------------------------------------------------------ THE READER
def read_theta(case_dir, time):
    """THE PRODUCTION READER. Returns (xstar[], theta[]) from disk.

    Every graded number and the planted-zero control go through this one
    function, so the control exercises the channel the verdict depends on.
    """
    p = os.path.join(case_dir, str(time), "T")
    if not os.path.isfile(p):
        return None
    txt = open(p).read()
    m = re.search(r"internalField\s+nonuniform[^(]*\(\s*(.*?)\n\)", txt, re.S)
    if not m:
        u = re.search(r"internalField\s+uniform\s+([0-9.eE+-]+)\s*;", txt)
        return None if not u else ([0.5], [float(u.group(1))])
    vals = [float(v) for v in m.group(1).split()]
    n = len(vals)
    if n < 2:
        return None
    xs = [(i + 0.5) / n for i in range(n)]        # cell centres in x* = x/L
    return xs, vals


def theta_mean_of(prof):
    """Volume average. Cells are uniform, so this is the arithmetic mean --
    MESH-INDEPENDENT by construction, which is why it is the primary row."""
    return sum(prof[1]) / len(prof[1])


def theta_at(prof, xstar):
    """Linear interpolation to a FIXED x*, so the graded quantity is the same
    quantity on every level (cell centres move with the mesh; the comparison
    point must not)."""
    xs, th = prof
    if xstar <= xs[0]:
        s = (xstar - xs[0]) / (xs[1] - xs[0])
        return th[0] + s * (th[1] - th[0])
    if xstar >= xs[-1]:
        s = (xstar - xs[-2]) / (xs[-1] - xs[-2])
        return th[-2] + s * (th[-1] - th[-2])
    for i in range(len(xs) - 1):
        if xs[i] <= xstar <= xs[i + 1]:
            s = (xstar - xs[i]) / (xs[i + 1] - xs[i])
            return th[i] + s * (th[i + 1] - th[i])
    refuse("interpolation failed at x*=%g" % xstar)


# ------------------------------------------- rule 3: planted-zero control
def planted_zero_control(case_dir, time):
    """BOTH ARMS, an AIMED plant, and a MEASURED detection floor.

    THE FLOOR IS MEASURED, NOT ASSUMED. A change gate has a detection floor,
    and on T8 a registered plant of 1.234e-03 was invisible against a dmax of
    1.012e-01 -- 82x the plant -- so the control passed while seeing nothing.
    Here a descending ladder is driven through the SAME production reader and
    the smallest magnitude it still resolves is recorded; if the registered
    PLANT sits at or below that floor, this REFUSES.

    THE PLANT IS AIMED at the cell nearest the graded station, located
    STRUCTURALLY by index, never by matching a value: a value-matching plant
    can silently fail to land and then report success having done nothing.

    Copies first; never writes into the case directory.
    """
    tmp = tempfile.mkdtemp(prefix="t11pz_")
    try:
        dst = os.path.join(tmp, os.path.basename(case_dir))
        shutil.copytree(case_dir, dst, symlinks=True)
        if os.path.realpath(dst).startswith(os.path.realpath(case_dir)):
            refuse("planted-zero control: scratch copy resolved INSIDE the case tree")
        base = read_theta(dst, time)
        if base is None:
            refuse("planted-zero control: the reader returned nothing on the "
                   "unplanted copy, so neither arm can be judged")
        again = read_theta(dst, time)
        dneg = max(abs(a - b) for a, b in zip(base[1], again[1]))
        if dneg != 0.0:
            refuse("planted-zero control NEGATIVE ARM FAILED: the reader returned "
                   "%.17g on identical bytes. The reader is NOISY and its zeros "
                   "are not zeros; every T11 number depending on it is withdrawn, "
                   "not re-graded." % dneg)

        p = os.path.join(dst, str(time), "T")
        lines = open(p).read().splitlines(True)
        start = None
        for i, ln in enumerate(lines):
            if "internalField" in ln and "nonuniform" in ln:
                for j in range(i, min(i + 5, len(lines))):
                    if lines[j].strip() == "(":
                        start = j + 1
                        break
                break
        if start is None:
            refuse("planted-zero control: could not locate internalField STRUCTURALLY")
        idx = start                       # cell 0 == the centreplane station
        before = float(lines[idx].strip())

        seen, floor = {}, None
        for mag in (1.0, 1e-1, 1e-2, PLANT, 1e-4, 1e-5, 1e-6, 1e-7):
            lines[idx] = "%.17g\n" % (before + mag)
            open(p, "w").write("".join(lines))
            got = read_theta(dst, time)
            if got is None:
                refuse("planted-zero control: reader returned nothing at plant %.3g" % mag)
            d = max(abs(a - b) for a, b in zip(base[1], got[1]))
            seen[mag] = d
            if d > 0.0:
                floor = mag
        if floor is None:
            refuse("planted-zero control POSITIVE ARM FAILED: no plant magnitude "
                   "was visible at %s line %d. The reader is BLIND and every zero "
                   "it has produced for this rung is worthless." % (p, idx + 1))
        dpos = seen[PLANT]
        if dpos == 0.0:
            refuse("planted-zero control POSITIVE ARM FAILED at the REGISTERED "
                   "plant: %.6g was invisible while %.6g WAS visible. The "
                   "registered plant sits BELOW this reader's demonstrated "
                   "detection floor." % (PLANT, floor))
        return dict(status="PASS", plant=PLANT, planted_line=idx + 1,
                    recovered=dpos, negative_arm=dneg,
                    demonstrated_detection_floor=floor,
                    ladder={("%g" % k): v for k, v in seen.items()})
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ------------------------------------------- rule 5: Roache triple gating
def classify(triple):
    f3, f2, f1 = triple
    e21, e32 = f1 - f2, f2 - f3
    if e21 == 0.0 and e32 == 0.0:
        return "EXACT", None
    if e21 == 0.0 or e32 == 0.0:
        return "STAGNANT", None
    ratio = e32 / e21
    if ratio <= 0.0:
        return "OSCILLATORY", None
    if abs(e21) >= abs(e32):
        return "DIVERGENT", None
    return "CONVERGING", math.log(abs(ratio)) / math.log(REFINEMENT)


def gci(triple, p):
    f3, f2, f1 = triple
    if p is None or f1 == 0.0:
        return None
    return FS * abs((f1 - f2) / f1) / (REFINEMENT ** p - 1.0)


def richardson(triple, p):
    """REPORTED, NEVER GATED ON. The correct form is f_fine - e21/den;
    analyse_t3.py:384 and analyse_t1c.py:337 carry the inverted
    f_fine + e21/den, established display-only lab-wide at 2f1d6cb7."""
    f3, f2, f1 = triple
    if p is None:
        return None
    return f1 - (f1 - f2) / (REFINEMENT ** p - 1.0)


def apply_gate(value, ref, triple, time_ok):
    """The ONLY function that writes a verdict. Rule 5's fixed order."""
    state, p = classify(triple)
    if not time_ok:
        return "NOT A RESULT", state, p, None, ("gate (1): a level did not reach "
                                                "endTime or a timestep did not converge")
    if state != "CONVERGING":
        return "NOT A RESULT", state, p, None, "gate (2): triple is %s" % state
    g = gci(triple, p)
    lo, hi = ref * (1 - BAND_REL), ref * (1 + BAND_REL)
    if lo <= value <= hi:
        return "PASS", state, p, g, ""
    return "GATE FAIL", state, p, g, ""


def time_integration_ok(case_dir):
    """Gate (1) for a TRANSIENT rung. There is no iterative convergence to a
    steady state here; the analogous conditions are that the integration
    reached endTime and that every timestep's linear solve converged."""
    log = os.path.join(case_dir, "log.solve")
    if not os.path.isfile(log):
        return False, None, "no log.solve"
    body = open(log, errors="replace").read()
    fin = [float(m) for m in re.findall(
        r"Solving for T,.*?Final residual = ([0-9.eE+-]+)", body)]
    if not fin:
        return False, None, "no T solves in log.solve"
    worst = max(fin)
    if not re.search(r"^End\s*$", body, re.M):
        return False, worst, "no End line"
    if worst > RESID_FLOOR:
        return False, worst, "worst final residual %.3e > %.1e" % (worst, RESID_FLOOR)
    return True, worst, ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=os.path.join(HERE, "gate_t11.json"))
    a = ap.parse_args()

    for lv, case in CASES.items():
        if not os.path.isfile(os.path.join(HERE, "DONE.%s" % case)):
            refuse("no DONE.%s -- the whole rung is graded or none of it is. Run "
                   "mark_done_t11.py; if it says NOT DONE, that is the answer and "
                   "this comparator does not overrule it." % case)

    # the reference cannot be trusted until it is verified to solve the problem
    print("verifying the analytic reference before any comparison:")
    meta = level_meta(CASES["f"])
    Fo = float(meta["Fo_end"])
    EX.verify(BI, Fo)
    EX.lumped_limit_selfcheck()

    dirs, times, tok = {}, {}, {}
    for lv, case in CASES.items():
        d = os.path.join(HERE, case)
        t = latest_time(d)
        if t is None:
            refuse("%s has no time directory beyond 0" % case)
        dirs[lv], times[lv] = d, t
        ok, worst, why = time_integration_ok(d)
        tok[lv] = dict(ok=ok, worst_final_residual=worst, why=why)
        print("  level %s: reached endTime and every step converged: %s%s"
              % (lv, ok, ("" if ok else "  [" + why + "]")))
    time_ok = all(tok[lv]["ok"] for lv in LEVELS)

    control = planted_zero_control(dirs["f"], times["f"])
    print("planted-zero control PASS: registered plant %.6g recovered %.6g; "
          "negative arm %.17g; DEMONSTRATED detection floor %.6g"
          % (control["plant"], control["recovered"], control["negative_arm"],
             control["demonstrated_detection_floor"]))

    profs = {}
    for lv in LEVELS:
        pr = read_theta(dirs[lv], times[lv])
        if pr is None:
            refuse("could not read T on level %s -- a missing number is not a zero" % lv)
        profs[lv] = pr

    rows = []
    ROWS = (("G1", "theta_mean (stored energy, mesh-independent)",
             lambda pr: theta_mean_of(pr), EX.theta_mean(Fo, BI)),
            ("G2", "theta at x*=0 (centreplane)",
             lambda pr: theta_at(pr, 0.0), EX.theta(0.0, Fo, BI)),
            ("G3", "theta at x*=1 (convective face)",
             lambda pr: theta_at(pr, 1.0), EX.theta(1.0, Fo, BI)))
    for rid, label, fn, ref in ROWS:
        vals = {lv: fn(profs[lv]) for lv in LEVELS}
        triple = (vals["c"], vals["m"], vals["f"])
        verdict, state, p, g, note = apply_gate(vals["f"], ref, triple, time_ok)
        rows.append(dict(row=rid, quantity=label, reference=ref,
                         band=[ref * (1 - BAND_REL), ref * (1 + BAND_REL)],
                         value_fine=vals["f"], triple=dict(zip(LEVELS, triple)),
                         triple_state=state, observed_order=p, gci=g,
                         richardson_REPORTED_ONLY=richardson(triple, p),
                         verdict=verdict, note=note,
                         rel_deviation=(vals["f"] - ref) / ref,
                         band_utilisation=abs(vals["f"] - ref) / (ref * BAND_REL)))
        print("%-3s fine=%.10f ref=%.10f rel dev=%+.3e  triple=%-11s p=%s "
              "GCI=%s -> %s%s"
              % (rid, vals["f"], ref, (vals["f"] - ref) / ref, state,
                 ("%.3f" % p) if p is not None else "n/a",
                 ("%.4f%%" % (100 * g)) if g is not None else "n/a",
                 verdict, ("  [" + note + "]") if note else ""))

    out = dict(rung="T11", scope="SOLID-ONLY transient conduction; NOT conjugate",
               Bi=BI, Fo_end=Fo, refinement_ratio=REFINEMENT,
               factor_of_safety=FS, band_rel=BAND_REL,
               planted_zero_control=control, time_integration=tok, rows=rows)
    json.dump(out, open(a.json, "w"), indent=2)
    print("wrote %s" % a.json)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
