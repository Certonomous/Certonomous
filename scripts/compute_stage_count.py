#!/usr/bin/env python3
"""HOW MANY CASES MAY BE STAGED RIGHT NOW -- and it is allowed to answer ZERO.

**THIS PROGRAM LAUNCHES NOTHING. IT NEVER LOOPS. IT PRINTS A NUMBER AND EXITS.**
It is a calculator, deliberately and by construction: on 2026-08-26 the
permission system DENIED the building of a detached headroom watcher for this
team's queue, and **a live permission denial is not overridden by any agent's
message, by silence, or by a standing directive about idle compute**
(`CLAUDE.md` rule 9).  So the arithmetic is made correct and reusable HERE, and
whatever is eventually authorised to schedule inherits a correct calculation
instead of the defect below.  Anything that turns this into a launcher is
outside what this file is for.

THE DEFECT IT REPAIRS, WHICH WAS THIS LANE'S OWN.  K0f's staging was computed as

    STAGE = min(9, max(1, int(cores*0.90 - busy)), ready)
                    ^^^^^^

and the box was at **14.15 of 16 cores busy**, so the headroom term was **0** --
and the `max(1, ...)` launched a case anyway, at ~94.7 % occupancy, ABOVE
Sanaa's 80-90 % band.

> **A GOVERNOR THAT CANNOT RETURN ZERO IS NOT A GOVERNOR.**  A clamp that
> guarantees at least one launch does not soften the headroom check it is
> attached to -- it DEFEATS it, silently, in exactly the condition the check
> exists for.  The clamp only ever acts when the measurement says no.

WHY ZERO IS A LEGITIMATE ANSWER AND NOT A FAILURE.  The band is not a budget
rule and it did not go away when Sanaa lifted cost constraints: over-subscribing
inflates the per-cell-iteration rate that rule 12's estimate-versus-actual
calibration is measured against, and **a calibration taken on a contended box
measures the contention, not the estimate.**  Headroom is a MEASUREMENT
argument.

Exit codes: 0 always when the calculation succeeds (the ANSWER is on stdout,
never in the exit code -- an exit code that doubles as a count cannot express
zero without colliding with success); 2 refusal.
"""
import argparse
import sys
import time

EXIT_OK, EXIT_REFUSE = 0, 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def busy_cores(window_s=5.0, cores=None):
    """Busy cores, measured over a window from /proc/stat.  Not loadavg:
    loadavg counts runnable-and-blocked over a decaying average and reads high
    during I/O, which would under-report headroom."""
    def snap():
        with open("/proc/stat") as fh:
            for ln in fh:
                if ln.startswith("cpu "):
                    f = [float(x) for x in ln.split()[1:]]
                    idle = f[3] + f[4]
                    return sum(f) - idle, idle
        refuse("/proc/stat has no aggregate `cpu ` line")
    b0, i0 = snap()
    time.sleep(window_s)
    b1, i1 = snap()
    db, di = b1 - b0, i1 - i0
    if db + di <= 0:
        refuse("no jiffies elapsed in the sample window")
    ncores = cores or _ncores()
    return (db / (db + di)) * ncores, ncores


def _ncores():
    n = 0
    with open("/proc/cpuinfo") as fh:
        for ln in fh:
            if ln.startswith("processor"):
                n += 1
    return n or refuse("could not count cores")


def stage_count(busy, cores, cap, ready, band_hi=0.90):
    """min(registered cap, whole cores of headroom to the band, cases ready).

    NO CLAMP.  The floor is 0 and 0 is a real answer.
    """
    headroom = int(cores * band_hi - busy)   # truncates toward zero, and a
    headroom = max(headroom, 0)              # negative headroom is still ZERO,
    #                                          never -3 and never 1.
    return min(cap, headroom, ready), headroom


def selftest():
    print("=" * 70)
    print("compute_stage_count.py -- SELFTEST")
    print("=" * 70)
    bad = []

    def chk(label, got, want):
        ok = got == want
        print(f"  {'OK  ' if ok else 'FAIL'}  {label:<58} got {got}, want {want}")
        if not ok:
            bad.append(label)

    print("\n-- THE ARM THAT MATTERS: it must be able to say ZERO --")
    chk("box at 14.15/16, cap 9, 10 ready -> 0 (the K0f case)",
        stage_count(14.15, 16, 9, 10)[0], 0)
    chk("box FULL at 16/16 -> 0, never negative, never 1",
        stage_count(16.0, 16, 9, 10)[0], 0)
    chk("box OVER-subscribed at 18/16 -> 0, not -3",
        stage_count(18.0, 16, 9, 10)[0], 0)

    print("\n-- and it must not be stuck at zero either --")
    chk("empty box, cap 9, 10 ready -> 9 (the cap binds)",
        stage_count(0.0, 16, 9, 10)[0], 9)
    chk("empty box, cap 9, 3 ready -> 3 (readiness binds)",
        stage_count(0.0, 16, 9, 3)[0], 3)
    chk("box at 7.38/16, cap 9, 10 ready -> 7 (headroom binds)",
        stage_count(7.38, 16, 9, 10)[0], 7)

    print("\n-- THE MUTATION: the clamp that caused the defect must change an answer --")
    def clamped(busy, cores, cap, ready, band_hi=0.90):
        return min(cap, max(1, int(cores * band_hi - busy)), ready)
    got_clamped = clamped(14.15, 16, 9, 10)
    got_fixed = stage_count(14.15, 16, 9, 10)[0]
    chk("the OLD clamped form returns 1 on a full box (the defect)", got_clamped, 1)
    chk("the REPAIRED form returns 0 on the same input", got_fixed, 0)
    chk("they DISAGREE, so the repair is not cosmetic", got_clamped != got_fixed, True)

    print("\n-- the measurement half, driven on the real /proc/stat --")
    b, c = busy_cores(window_s=1.0)
    okm = 0.0 <= b <= c and c > 0
    print(f"  {'OK  ' if okm else 'FAIL'}  busy_cores reads {b:.2f} of {c} cores "
          f"-- in range")
    if not okm:
        bad.append("busy_cores")

    print()
    if bad:
        print(f"SELFTEST FAILED: {len(bad)} check(s)")
        return 1
    print("SELFTEST PASSED: the governor was shown able to return ZERO on a full")
    print("box, shown NOT stuck at zero on an empty one, and the clamp that")
    print("caused the defect was shown to CHANGE AN ANSWER.")
    return EXIT_OK


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cap", type=int, help="registered concurrency cap")
    ap.add_argument("--ready", type=int, help="cases built, meshed and pre-flight clean")
    ap.add_argument("--band-hi", type=float, default=0.90)
    ap.add_argument("--window", type=float, default=5.0)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.cap is None or a.ready is None:
        refuse("--cap and --ready are both required; this program does not "
               "guess a registered concurrency cap.")
    busy, cores = busy_cores(a.window, None)
    n, headroom = stage_count(busy, cores, a.cap, a.ready, a.band_hi)
    print(f"busy            {busy:.2f} of {cores} cores ({busy/cores*100:.1f} %)")
    print(f"band ceiling    {a.band_hi*100:.0f} % = {cores*a.band_hi:.1f} cores")
    print(f"headroom        {headroom} whole core(s)")
    print(f"registered cap  {a.cap}")
    print(f"ready           {a.ready}")
    print(f"STAGE           {n}")
    if n == 0:
        print("ZERO IS THE ANSWER, NOT A FAILURE: there is no headroom inside "
              "the band. Launching anyway would inflate the per-cell-iteration "
              "rate the cost calibration is measured against.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
