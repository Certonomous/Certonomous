#!/usr/bin/env python3
"""T25RF -- READ one arm of the ungated numerics feasibility probe.

*** THIS IS NOT A COMPARATOR AND IT EMITS NO VERDICT. ***
T25RF is a feasibility rung (VERIFICATION_CHARTER 2m): no gate, no threshold,
no band, no label.  This script prints OBSERVATIONS against the three reading
criteria registered in docs/campaigns/T-family/T25RF_FEASIBILITY_NOTE.md
section 4, and it must never print PASS, GATE REACHED, GATE FAIL or NOT A
RESULT.  "held" / "not held" here are descriptions of the probe, not verdicts.

POSITIVE CONTROL: this same reader is run over arm A0, which is known to have
diverged.  A reader that cannot see A0's continuity blow-up (sum local 125.93)
and its negative Min T (-73.54) is not able to see a non-zero, and its readings
on the other arms would be worthless.  Run with --all to see both together.

Usage: read_arm_t25RF.py <ARM_DIR> [<ARM_DIR> ...]
"""
import re
import sys
import os

RE_TIME = re.compile(r"^Time = (\S+)$")
RE_SOLVE = re.compile(
    r"Solving for (\S+?), Initial residual = (\S+?), "
    r"Final residual = (\S+?), No Iterations (\d+)"
)
RE_SUMLOCAL = re.compile(r"sum local = (\S+?),")
RE_MINMAX = re.compile(r"Min/max T:(\S+) (\S+)")
RE_COURANT = re.compile(r"coolant Courant Number mean: (\S+) max: (\S+)")


def read(case):
    log = os.path.join(case, "log.solve")
    steps = []          # list of dicts, one per Time =
    cur = None
    sumlocal = []
    minT, maxT = None, None
    courant = []
    maxiter_hits = 0
    total_p = 0
    fatal = None
    ended = False
    exec_time = None

    with open(log, errors="replace") as fh:
        for line in fh:
            m = RE_TIME.match(line.strip())
            if m:
                cur = {"t": m.group(1), "sweeps": []}
                steps.append(cur)
                continue
            m = RE_COURANT.search(line)
            if m:
                courant.append((float(m.group(1)), float(m.group(2))))
                continue
            m = RE_SOLVE.search(line)
            if m and cur is not None:
                fld, ini, fin, nit = m.group(1), float(m.group(2)), \
                    float(m.group(3)), int(m.group(4))
                if fld.startswith("p_rgh"):
                    total_p += 1
                    if nit >= 1000:
                        maxiter_hits += 1
                # a new sweep starts at each Ux solve
                if fld == "Ux":
                    cur["sweeps"].append({})
                if cur["sweeps"]:
                    cur["sweeps"][-1].setdefault(fld, []).append((ini, fin, nit))
                continue
            m = RE_SUMLOCAL.search(line)
            if m:
                v = float(m.group(1))
                sumlocal.append(v)
                if cur is not None and cur["sweeps"]:
                    cur["sweeps"][-1].setdefault("_sumlocal", []).append(v)
                continue
            m = RE_MINMAX.search(line)
            if m:
                lo, hi = float(m.group(1)), float(m.group(2))
                minT = lo if minT is None else min(minT, lo)
                maxT = hi if maxT is None else max(maxT, hi)
                continue
            if "FOAM FATAL" in line:
                fatal = line.strip()
            if line.strip() == "End":
                ended = True
            if line.startswith("ExecutionTime"):
                exec_time = line.split("=")[1].split("s")[0].strip()

    return dict(steps=steps, sumlocal=sumlocal, minT=minT, maxT=maxT,
                courant=courant, maxiter_hits=maxiter_hits, total_p=total_p,
                fatal=fatal, ended=ended, exec_time=exec_time)


def report(case):
    arm = os.path.basename(os.path.abspath(case))
    r = read(case)
    print("=" * 74)
    print(f"ARM {arm}   ({case})")
    print("=" * 74)
    print(f"  timesteps executed        : {len(r['steps'])}")
    print(f"  last Time reached         : "
          f"{r['steps'][-1]['t'] if r['steps'] else 'NONE'}")
    print(f"  'End' line present        : {r['ended']}")
    print(f"  ExecutionTime (s)         : {r['exec_time']}")
    print(f"  fatal error               : {r['fatal'] or 'none'}")
    print()

    # --- criterion (a) -----------------------------------------------------
    print("  (a) Min T bounded above 273 K for the whole probe")
    print(f"      global min T = {r['minT']} K")
    print(f"      global max T = {r['maxT']} K")
    ok_a = (r["minT"] is not None and r["minT"] > 273.0
            and r["fatal"] is None and r["ended"])
    print(f"      -> observation: {'HELD' if ok_a else 'NOT HELD'}")
    print()

    # --- criterion (b) -----------------------------------------------------
    print("  (b) last-sweep initial residuals for p_rgh / Ux / h below 1e-6")
    ok_b = True
    if r["steps"] and r["steps"][-1]["sweeps"]:
        last = r["steps"][-1]["sweeps"][-1]
        for fld in ("Ux", "h", "p_rgh"):
            vals = last.get(fld) or last.get(fld + "Final")
            if not vals:
                print(f"      {fld:6s}: NOT PRESENT in the last sweep")
                ok_b = False
                continue
            ini = vals[0][0]
            mark = "below 1e-6" if ini < 1e-6 else "ABOVE 1e-6"
            print(f"      {fld:6s}: initial residual = {ini:.6e}   {mark}")
            if ini >= 1e-6:
                ok_b = False
    else:
        print("      no complete sweep to read")
        ok_b = False
    print(f"      -> observation: {'HELD' if ok_b else 'NOT HELD'}")
    print()

    # --- criterion (c) -----------------------------------------------------
    print("  (c) continuity 'sum local' does not grow monotonically")
    s = r["sumlocal"]
    if s:
        rises = sum(1 for i in range(1, len(s)) if s[i] > s[i - 1])
        print(f"      samples = {len(s)}   first = {s[0]:.6e}   "
              f"last = {s[-1]:.6e}")
        print(f"      max = {max(s):.6e}   "
              f"rises = {rises}/{len(s)-1} "
              f"({100.0*rises/max(1, len(s)-1):.0f}% of steps increase)")
        ok_c = (s[-1] <= s[0]) and rises < (len(s) - 1)
        print(f"      last/first ratio = {s[-1]/s[0]:.3e}")
    else:
        print("      no continuity samples")
        ok_c = False
    print(f"      -> observation: {'HELD' if ok_c else 'NOT HELD'}")
    print()

    # --- cost / efficiency notes ------------------------------------------
    print("  cost notes")
    print(f"      p_rgh solves            : {r['total_p']}")
    print(f"      of which at maxIter 1000: {r['maxiter_hits']} "
          f"({100.0*r['maxiter_hits']/max(1, r['total_p']):.0f}%)")
    if r["courant"]:
        print(f"      Courant first  mean/max : {r['courant'][0][0]:.1f} / "
              f"{r['courant'][0][1]:.1f}")
        print(f"      Courant last   mean/max : {r['courant'][-1][0]:.1f} / "
              f"{r['courant'][-1][1]:.1f}")
    print()
    print(f"  SUMMARY for {arm}: (a) {'HELD' if ok_a else 'NOT HELD'} | "
          f"(b) {'HELD' if ok_b else 'NOT HELD'} | "
          f"(c) {'HELD' if ok_c else 'NOT HELD'}")
    print("  NO VERDICT.  T25RF is an ungated feasibility rung "
          "(VERIFICATION_CHARTER 2m).")
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    for c in sys.argv[1:]:
        report(c)
