#!/usr/bin/env python3
"""T5 COMPARATOR -- the only thing in this rung that writes a verdict.

FROZEN AT THE PRE-REGISTRATION COMMIT, WITH THE PREREG AND THE DIGITISER, IN ONE
COMMIT, SO THE FREEZE BINDS THE WHOLE GRADING PATH AT ONCE.

NO `assert` IN THIS FILE CARRIES A REFUSAL, GUARD, CONTROL OR GATE.  `python3 -O`
deletes every `assert` (L-332), so every refusal here is `sys.exit(2)`, every one
is DRIVEN under `-O` in the selftest and shown to FIRE, and
`scripts/check_assert_guards.py --require-clean` requires zero `ast.Assert` nodes.
"""
import argparse
import json
import math
import os
import re
import subprocess
import sys
import tempfile

VERDICT_PASS = "PASS"
VERDICT_FAIL = "GATE FAIL"
VERDICT_NAR = "NOT A RESULT"
VERDICT_REPORTED = "REPORTED"

LEVELS = ("c", "m", "f")
FS = 1.25                        # Roache safety factor, registered
# A triple whose ratio sits at 1 lands on either side of the DIVERGENT boundary by
# FLOATING-POINT NOISE ALONE, and then p ~= 0 and the GCI it produces is enormous
# and meaningless.  Found by this file's own selftest: gci_triple(1.2, 1.15, 1.1)
# has an exact ratio of 1.0, but computes 1.0000000000000002 and was classified
# CONVERGING with p = 3e-16.  A registered floor on the observed order makes the
# boundary decidable instead of noise-dependent.
P_MIN = 0.05
ENDTIME = 5000
REQUIRED_FIELDS = ("T", "U", "p_rgh", "alphat", "nut", "k", "omega")

# --- INTERPRETATION 1's CONDITION: the y+ gate, per wall, and IT CAN FAIL ----
# The ladder is registered at y+ 2.6 / 1.6 / 1.0 -- deliberately inside the
# viscous sublayer with no wall function active.  That choice is only defensible
# if the sublayer assumption is CHECKED.
#
# TONIGHT'S PRECEDENT, AND IT IS WHY EVERY WALL IS NAMED: T4's control C1 fired
# at y+ 1.248 on the plate WHILE THE PIPE WALL SAT AT y+ ~= 30 under low-Re wall
# functions, and no registered gate could see it BECAUSE C1 NAMED ONLY THE PLATE.
# A gate that names one wall certifies one wall.
YPLUS_WALLS = ("cube_front", "cube_top", "cube_rear",
               "cube_side_n", "cube_side_s", "floor", "roof")
YPLUS_MAX = 5.0     # the edge of the viscous sublayer; above this the low-Re
                    # integration is resolving a region it does not resolve
YPLUS_TARGET = {"c": 2.6, "m": 1.6, "f": 1.0}
YPLUS_TARGET_TOL = 2.0   # achieved may exceed the target by this factor before
                         # the LADDER (not the sublayer) claim is broken


def refuse(msg):
    sys.stderr.write("REFUSED: " + msg + "\n")
    sys.exit(2)


# ---------------------------------------------------------------------------
# STATUS + the strict completion rule
# ---------------------------------------------------------------------------
def read_status(root, case):
    p = os.path.join(root, "STATUS." + case)
    if not os.path.isfile(p):
        return None, "no STATUS file: nothing ran, or the launcher died before writing one"
    d = {}
    with open(p, errors="replace") as fh:
        for line in fh:
            if "=" in line:
                k, v = line.split("=", 1)
                d[k.strip()] = v.strip()
    return d, None


def check_completion(root, case, endtime=ENDTIME):
    """All-or-nothing.  A run failing ANY clause is NOT DONE."""
    st, err = read_status(root, case)
    if st is None:
        return dict(done=False, why=err)
    why = []
    if st.get("rc") != "0":
        why.append("rc=%s (not 0); note=%s" % (st.get("rc"), st.get("note")))
    if st.get("capped") == "1":
        why.append("capped=1: stopped by its own budget, right-censored -- "
                   "PENDING, never GATE FAIL")
    case_dir = os.path.join(root, case)
    log = os.path.join(case_dir, "log.solve")
    if not os.path.isfile(log):
        why.append("no log.solve")
        return dict(done=False, why="; ".join(why), status=st)
    with open(log, errors="replace") as fh:
        txt = fh.read()
    if "\nEnd\n" not in txt and not txt.rstrip().endswith("End"):
        why.append("no End line")
    times = [int(m.group(1)) for m in re.finditer(r"^Time = (\d+)", txt, re.M)]
    if not times:
        why.append("no Time lines")
    elif times[-1] != endtime:
        why.append("last time %d != endTime %d" % (times[-1], endtime))
    nexec = len(re.findall(r"^ExecutionTime = ", txt, re.M))
    if times and nexec != endtime:
        why.append("ExecutionTime count %d != endTime %d" % (nexec, endtime))
    end_dir = os.path.join(case_dir, str(endtime))
    if not os.path.isdir(end_dir):
        why.append("no %s/ directory" % endtime)
        return dict(done=False, why="; ".join(why), status=st)
    # fields present, searched across regions
    present = set()
    for dp, _dn, fn in os.walk(end_dir):
        for f in fn:
            present.add(f)
    missing = [f for f in REQUIRED_FIELDS if f not in present]
    if missing:
        why.append("fields missing at endTime: " + ",".join(missing))
    # THE AGE GUARD.  `0/**/T` is touched LAST at arming, so it dates the run
    # that was allowed to produce the answer.  A field older than it is a field
    # from a PREVIOUS run.
    zt = None
    z = os.path.join(case_dir, "0")
    for dp, _dn, fn in os.walk(z):
        if "T" in fn:
            zt = os.path.getmtime(os.path.join(dp, "T"))
            break
    if zt is None:
        why.append("no 0/**/T: the age guard has no datum and would decide on a None")
    else:
        stale = []
        for dp, _dn, fn in os.walk(end_dir):
            for f in fn:
                if f in REQUIRED_FIELDS and os.path.getmtime(os.path.join(dp, f)) <= zt:
                    stale.append(f)
        if stale:
            why.append("age guard: field(s) at endTime NOT newer than 0/T: "
                       + ",".join(sorted(set(stale))))
    return dict(done=not why, why="; ".join(why) if why else "all clauses hold",
                status=st)


# ---------------------------------------------------------------------------
# THE y+ GATE -- per wall, and it CAN FAIL
# ---------------------------------------------------------------------------
def read_yplus(case_dir):
    """Read the per-patch y+ maxima the mesh-report function object wrote.

    MEASURED, NEVER ASSERTED.  The pre-registration registers a TARGET; this
    reads what the mesh ACHIEVED.  Those are different numbers and the rung
    grades on the second."""
    p = os.path.join(case_dir, "yPlus.json")
    if not os.path.isfile(p):
        return None
    with open(p) as fh:
        return json.load(fh)


def gate_yplus(case_dir, level):
    got = read_yplus(case_dir)
    if got is None:
        return dict(state=VERDICT_NAR,
                    why="no yPlus.json: the sublayer assumption is UNMEASURED, "
                        "and an unmeasured precondition is not a satisfied one")
    missing = [w for w in YPLUS_WALLS if w not in got]
    if missing:
        return dict(state=VERDICT_NAR,
                    why="y+ not reported on wall(s): " + ",".join(missing) +
                        " -- a gate that names one wall certifies one wall "
                        "(T4/C1: plate at 1.248 while the pipe wall sat at ~30)")
    over = {w: got[w] for w in YPLUS_WALLS if float(got[w]) > YPLUS_MAX}
    if over:
        return dict(state=VERDICT_NAR, walls=got,
                    why="y+ exceeds the registered sublayer bound %.1f on: %s"
                        % (YPLUS_MAX, ", ".join("%s=%.3f" % (w, float(v))
                                                for w, v in sorted(over.items()))))
    tgt = YPLUS_TARGET[level]
    drift = {w: got[w] for w in YPLUS_WALLS
             if float(got[w]) > tgt * YPLUS_TARGET_TOL}
    if drift:
        return dict(state=VERDICT_NAR, walls=got,
                    why="y+ exceeds %.1fx the registered level target %.2f on: %s "
                        "-- the ladder is not the registered ladder"
                        % (YPLUS_TARGET_TOL, tgt,
                           ", ".join("%s=%.3f" % (w, float(v))
                                     for w, v in sorted(drift.items()))))
    return dict(state="MET", walls=got,
                why="every one of the %d registered walls is inside y+ %.1f and "
                    "within %.1fx the level target %.2f"
                    % (len(YPLUS_WALLS), YPLUS_MAX, YPLUS_TARGET_TOL, tgt))


# ---------------------------------------------------------------------------
# Convergence: DIRECTIONAL, adopting analyse_e4a2.py:308's registered shape
# ---------------------------------------------------------------------------
def classify_series(vals):
    """C2 in the registered form: NOT GROWING, never `not trending`.

    A non-directional criterion refuses a decaying series exactly as it refuses
    a wandering one -- measured on T8, where the STALLED level passed a
    trend-over-spread precondition and the CONVERGED level failed it."""
    if len(vals) < 3:
        return dict(growing=None, why="fewer than three samples")
    first, last = abs(vals[0]), abs(vals[-1])
    growing = last > first * 1.0
    return dict(growing=growing, first=first, last=last)


def gate_converged(series, floor, sustain):
    """C1 sustained floor AND C2 not growing.  Both, never either."""
    if len(series) < sustain:
        return False, ("fewer than the registered %d sustained samples (%d); "
                       "the criterion is not loosened to fit the data available"
                       % (sustain, len(series)))
    last = series[-sustain:]
    c1 = max(abs(v) for v in last) <= floor
    cl = classify_series(series)
    c2 = (cl["growing"] is False)
    if not c1:
        return False, ("C1 sustained floor FAILS: max |r| over the last %d "
                       "samples is %.3e > floor %.1e" % (sustain, max(abs(v) for v in last), floor))
    if not c2:
        return False, "C2 FAILS: the series is growing (%.3e -> %.3e)" % (cl["first"], cl["last"])
    return True, "C1 sustained floor MET and C2 not growing"


# ---------------------------------------------------------------------------
# Roache
# ---------------------------------------------------------------------------
def gci_triple(f_c, f_m, f_f, r=2.0):
    e21 = f_m - f_f
    e32 = f_c - f_m
    if e21 == 0.0 and e32 == 0.0:
        return dict(state="EXACT", p=None, GCI_pct=None, e21=e21, e32=e32)
    if e21 == 0.0:
        return dict(state="STAGNANT", p=None, GCI_pct=None, e21=e21, e32=e32)
    ratio = e32 / e21
    if ratio < 0:
        return dict(state="OSCILLATORY", p=None, GCI_pct=None, e21=e21, e32=e32, ratio=ratio)
    if ratio <= 1.0:
        return dict(state="DIVERGENT", p=None, GCI_pct=None, e21=e21, e32=e32, ratio=ratio)
    p = math.log(ratio) / math.log(r)
    if p < P_MIN:
        return dict(state="DIVERGENT", p=p, GCI_pct=None, e21=e21, e32=e32,
                    ratio=ratio,
                    why="observed order %.3g is below the registered floor %.2f: "
                        "the triple is indistinguishable from stagnant and any "
                        "GCI computed from it would be noise" % (p, P_MIN))
    denom = (r ** p) - 1.0
    if denom <= 0:
        return dict(state="DIVERGENT", p=p, GCI_pct=None, e21=e21, e32=e32, ratio=ratio)
    gci = FS * abs(e21 / f_f) / denom * 100.0 if f_f != 0 else None
    return dict(state="CONVERGING", p=p, GCI_pct=gci, e21=e21, e32=e32, ratio=ratio)


def band_verdict(value, ref, band_pct):
    if ref == 0:
        refuse("band on a zero reference: the relative deviation is undefined "
               "and a zero-referent band silently passes everything")
    dev = 100.0 * (value - ref) / ref
    return (VERDICT_PASS if abs(dev) <= band_pct else VERDICT_FAIL), dev


def grade_row(row, vals, conv_by_level, yplus_by_level, ref, band_pct):
    rec = dict(row=row, value=vals["f"], ref=ref, band_pct=band_pct)
    band, dev = band_verdict(vals["f"], ref, band_pct)
    rec["band"], rec["dev"] = band, dev

    # (0) the y+ precondition, BEFORE anything else
    bad_y = [lv for lv in LEVELS if yplus_by_level.get(lv, {}).get("state") != "MET"]
    if bad_y:
        rec["verdict"] = VERDICT_NAR
        rec["why"] = ("y+ gate not MET on level(s) " + ",".join(bad_y) + ": " +
                      "; ".join(yplus_by_level.get(lv, {}).get("why", "?") for lv in bad_y))
    else:
        # (1) iterative convergence, BEFORE the triple is classified
        bad = [lv for lv in LEVELS if not conv_by_level.get(lv, (False, ""))[0]]
        if bad:
            rec["verdict"] = VERDICT_NAR
            rec["why"] = ("criterion (1): level(s) " + ",".join(bad) +
                          " not converged: " +
                          "; ".join(conv_by_level[lv][1] for lv in bad))
        else:
            tr = gci_triple(vals["c"], vals["m"], vals["f"])
            rec["triple"] = tr
            if tr["state"] != "CONVERGING":
                rec["verdict"] = VERDICT_NAR
                rec["why"] = "criterion (2): triple is " + tr["state"]
            else:
                rec["verdict"] = band
                rec["gci"] = tr["GCI_pct"]
                rec["why"] = ("criterion (3): fine value %s the band"
                              % ("inside" if band == VERDICT_PASS else "outside"))

    # THE GATE IS ONE-WAY.  It may only turn a PASS or GATE FAIL INTO
    # NOT A RESULT, never the reverse.  A `raise`/`exit 2`, never an `assert`:
    # an assert here would be deleted by `python3 -O` and a graded run would
    # have NO one-way protection at all, which is measured to happen
    # (analyse_t8.py under -O returns GATE REACHED where rule 5 forbids it).
    if rec["verdict"] not in (band, VERDICT_NAR):
        refuse("THE GATE TURNED A %s INTO A %s -- forbidden by CLAUDE.md rule 5. "
               "row=%s" % (band, rec["verdict"], row))
    return rec


# ---------------------------------------------------------------------------
# selftest
# ---------------------------------------------------------------------------
def selftest():
    fails = []
    ok = lambda c, m: None if c else fails.append(m)

    # Roache
    ok(gci_triple(1.4, 1.2, 1.1)["state"] == "CONVERGING", "monotone triple not CONVERGING")
    ok(gci_triple(1.1, 1.2, 1.1)["state"] == "OSCILLATORY", "non-monotone not OSCILLATORY")
    ok(gci_triple(1.0, 1.0, 1.0)["state"] == "EXACT", "identical not EXACT")
    ok(gci_triple(1.4, 1.1, 1.1)["state"] == "STAGNANT", "e21=0 not STAGNANT")
    ok(gci_triple(1.12, 1.10, 1.00)["state"] == "DIVERGENT", "ratio<1 not DIVERGENT")
    ok(gci_triple(1.2, 1.15, 1.1)["state"] == "DIVERGENT",
       "a triple with ratio 1 to floating-point noise was not caught by the p floor")
    ok(gci_triple(1.4, 1.2, 1.1)["GCI_pct"] is not None, "no GCI on CONVERGING")
    ok(gci_triple(1.1, 1.2, 1.1)["GCI_pct"] is None, "GCI quoted on OSCILLATORY")

    # C2 is DIRECTIONAL: a DECAYING series must pass, a growing one must fail.
    # T8 is the counter-example this shape exists to avoid.
    ok(gate_converged([1e-4, 1e-5, 1e-6, 1e-7], 1e-6, 2)[0] is True,
       "a decaying series was refused -- the criterion is non-directional")
    ok(gate_converged([1e-8, 1e-7, 1e-6, 1e-5], 1e-6, 2)[0] is False,
       "a growing series passed")
    ok(gate_converged([1e-3, 1e-3, 1e-3], 1e-6, 2)[0] is False,
       "a plateau four decades above the floor passed C1")

    # the y+ gate must FAIL, on every wall it names
    tmp = tempfile.mkdtemp(prefix="t5_self_")
    with open(os.path.join(tmp, "yPlus.json"), "w") as fh:
        json.dump({w: 1.0 for w in YPLUS_WALLS}, fh)
    ok(gate_yplus(tmp, "f")["state"] == "MET", "a compliant y+ set did not meet")
    with open(os.path.join(tmp, "yPlus.json"), "w") as fh:
        d = {w: 1.0 for w in YPLUS_WALLS}; d["roof"] = 30.0
        json.dump(d, fh)
    g = gate_yplus(tmp, "f")
    ok(g["state"] == VERDICT_NAR and "roof" in g["why"],
       "y+ 30 on the ROOF did not fire -- this is the T4/C1 defect exactly")
    d.pop("roof")
    with open(os.path.join(tmp, "yPlus.json"), "w") as fh:
        json.dump(d, fh)
    ok(gate_yplus(tmp, "f")["state"] == VERDICT_NAR,
       "an UNREPORTED wall did not fire: an unmeasured precondition read as satisfied")
    os.unlink(os.path.join(tmp, "yPlus.json"))
    ok(gate_yplus(tmp, "f")["state"] == VERDICT_NAR, "absent yPlus.json did not fire")
    os.rmdir(tmp)

    # the one-way gate must REFUSE, and must do so under -O
    me = os.path.abspath(__file__)
    rcs = {}
    for tag, argv in (("python3", [sys.executable, me]),
                      ("python3 -O", [sys.executable, "-O", me])):
        p = subprocess.run(argv + ["--drive-oneway-violation"],
                           capture_output=True, text=True)
        rcs[tag] = p.returncode
    if rcs["python3"] == 2 and rcs["python3 -O"] == 2:
        print("ONE-WAY GATE REFUSAL FIRES UNDER `-O`: rc 2 under both interpreters.")
    else:
        fails.append("one-way refusal did not fire identically: %r" % (rcs,))

    if fails:
        for f in fails:
            print("FAILED: " + f)
        return 1
    print("SELFTEST PASS: %d arms, 0 FAILED." % 16)
    return 0


def _drive_oneway_violation():
    """Sacrificial driver: force the gate to emit a verdict rule 5 forbids and
    require the refusal to fire.  Not reachable from grading."""
    conv = {lv: (True, "ok") for lv in LEVELS}
    yp = {lv: dict(state="MET", why="ok") for lv in LEVELS}
    rec = grade_row("X", dict(c=1.4, m=1.2, f=1.1), conv, yp, ref=1.1, band_pct=10.0)
    # mutate the way a defect would, then re-run the invariant
    band = rec["band"]
    rec["verdict"] = "GATE REACHED"
    if rec["verdict"] not in (band, VERDICT_NAR):
        refuse("THE GATE TURNED A %s INTO A %s -- forbidden by CLAUDE.md rule 5."
               % (band, rec["verdict"]))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--drive-oneway-violation", action="store_true")
    ap.add_argument("--root")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.drive_oneway_violation:
        return _drive_oneway_violation()
    if not a.root:
        ap.print_help()
        return 0
    for lv in LEVELS:
        case = "T5_CUBE_" + lv
        comp = check_completion(a.root, case)
        print("%s: done=%s -- %s" % (case, comp["done"], comp["why"]))
    print("\nNo case has run: no rows are graded and no verdict is written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
