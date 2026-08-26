#!/usr/bin/env python3
"""T8 -- STATIONARITY PROBE.  A DIAGNOSTIC.  IT GRADES NOTHING.

WHAT THIS IS, AND WHAT IT IS NOT
--------------------------------
This file is NOT in the section 11 freeze set of `T8_PREREGISTRATION.md` and is
NOT on the grading path.  It produces NO verdict, NO band, NO triple and NO
value that any verdict may rest on.  It exists to answer ONE case-selection
question, ruled by the heat-transfer supervisor on 2026-08-26 (ruling A3):

    `buoyantBoussinesqSimpleFoam` is a STEADY solver.  Is the registered T8
    configuration stationary at all?

It is added AFTER first compute.  `VERIFICATION_CHARTER.md` section 2d permits
instrumentation that is not on the grading path to be added later, and requires
a dated disclosure naming what was added, when, what was readable at that
moment, and which findings rest on it.  That disclosure is in
`docs/campaigns/T-family/T8_STEADINESS_MEASUREMENT_2026-08-26.md`.

`CLAUDE.md` rule 2 forbids these runs from supplying a graded value.  The
re-registration draft's RULING C draws the line this file stays on the right
side of: existing solves *"may tell us what to REGISTER.  They may never tell us
what the ANSWER is."*

THE PARAMETERS ARE REGISTERED HERE, IN SOURCE, BEFORE THE SCRIPT WAS FIRST RUN
------------------------------------------------------------------------------
Supervisor ruling A2 forbids choosing the window length after seeing the series
-- that is the same move as choosing the level that makes the test work.  The
five constants below were written and committed to this file before any window
statistic was computed, and are not tuned:

  SPAN      the comparison span is the SECOND HALF of the registered run.  The
            first half contains the documented start transient (the descent to
            2.87e-07 near iteration 900 and the first excursion peaking at
            iteration 1800), and a stationarity test run across a transient
            tests the transient.
  K = 4     supervisor ruling A2: at least FOUR disjoint equal-length windows.
            Two windows give ONE difference, which is a sample and not a spread.
  W         SPAN / K, i.e. the second half quartered.  Not chosen by inspection.
  SPREAD    sample standard deviation within a window.
  CRITERION section 4c part 1, as ruled: the window MEAN must not trend across
            CONSECUTIVE windows by more than the WITHIN-WINDOW SPREAD --
            |mean[i+1] - mean[i]| <= spread[i] for every consecutive pair.
  SIGMA_SELF supervisor ruling A2: the MAXIMUM PAIRWISE window-to-window mean
            difference across the K windows.  NOT the single difference of two
            windows.

THE SERIES, AND ITS ADMITTED LIMITATION
---------------------------------------
Section 4c part 1 as drafted applies the precondition to each GRADED QUANTITY.
The graded quantities are read from written checkpoints, and `f` wrote only
`18000` and `20000` -- TWO samples, which is exactly the two-point sample that
section 4b.1 identifies as the defect.  The T initial residual is therefore the
only DENSELY sampled series this run possesses, and it is what is measured here.

    STATED AS A LIMITATION AND NOT PAPERED OVER: a stationarity result on the
    residual is NOT a stationarity result on a graded quantity.  It can REFUSE
    the case (a non-stationary residual on a steady solver is decisive) but a
    stationary residual would NOT establish that the graded quantities are
    stationary.  This probe is therefore admissible as evidence AGAINST
    steadiness and is NOT admissible as evidence FOR it.

READER
------
`CLAUDE.md`/method note section 9 of the re-registration draft: a fixed-width
substring reader truncated the exponent off scientific notation and turned a
converged value into a residual of 3.8.  This reader matches the WHOLE token and
asserts nothing -- it REFUSES (sys.exit(2)) on a short or unparseable series, and
carries no `assert` statement anywhere (the `-O` rule).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
K = 4
FIELD = "T"
MIN_ITERS = 2000


def refuse(msg):
    print("REFUSED: " + msg)
    sys.exit(2)


def read_initial_residuals(log_path, field):
    """Whole-token reader.  Returns one value per outer iteration (the FIRST
    solve of `field` inside each `Time = n` block)."""
    if not os.path.isfile(log_path):
        refuse("no such log: %s" % log_path)
    pat_time = re.compile(r"^Time = (\d+)")
    pat_res = re.compile(
        r"Solving for " + re.escape(field) +
        r", Initial residual = ([0-9eE.+-]+)")
    out = []
    seen_this_time = False
    with open(log_path, "r", errors="replace") as fh:
        for line in fh:
            if pat_time.match(line):
                seen_this_time = False
                continue
            m = pat_res.search(line)
            if m and not seen_this_time:
                tok = m.group(1)
                try:
                    out.append(float(tok))
                except ValueError:
                    refuse("unparseable residual token %r in %s" % (tok, log_path))
                seen_this_time = True
    return out


def mean(xs):
    return sum(xs) / len(xs)


def sstdev(xs):
    if len(xs) < 2:
        refuse("stdev of fewer than two samples")
    m = mean(xs)
    return (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5


def probe(level):
    log = os.path.join(HERE, "T8_MTT_%s" % level, "log.solve")
    r = read_initial_residuals(log, FIELD)
    n = len(r)
    print("=" * 74)
    print("level %s -- %s" % (level, os.path.relpath(log, os.path.dirname(HERE))))
    print("  outer iterations with a %s initial residual: %d" % (FIELD, n))
    if n < MIN_ITERS:
        print("  SERIES TOO SHORT for the registered span/K -- NOT A RESULT for"
              " this probe on this level.")
        return
    half = n // 2
    span = r[half:]
    W = len(span) // K
    if W < 2:
        print("  span too short to form K=%d windows -- NOT A RESULT." % K)
        return
    wins = [span[i * W:(i + 1) * W] for i in range(K)]
    ms = [mean(w) for w in wins]
    ss = [sstdev(w) for w in wins]
    print("  registered span: iterations %d..%d (second half); K=%d, W=%d"
          % (half + 1, n, K, W))
    for i in range(K):
        print("    window %d  mean %.6e  within-window sd %.6e  min %.6e  max %.6e"
              % (i + 1, ms[i], ss[i], min(wins[i]), max(wins[i])))
    # section 4c part 1 criterion, as ruled
    ok = True
    for i in range(K - 1):
        d = abs(ms[i + 1] - ms[i])
        verdict = "within" if d <= ss[i] else "EXCEEDS"
        if d > ss[i]:
            ok = False
        print("    consecutive %d->%d  |dmean| %.6e  vs within-window sd %.6e  -> %s"
              % (i + 1, i + 2, d, ss[i], verdict))
    # ruling A2: sigma_self = MAX PAIRWISE window-to-window mean difference
    pair = [(abs(ms[i] - ms[j]), i + 1, j + 1)
            for i in range(K) for j in range(i + 1, K)]
    smax = max(pair)
    print("    sigma_self (ruling A2: MAX pairwise of %d pairs) = %.6e"
          "   (windows %d vs %d)" % (len(pair), smax[0], smax[1], smax[2]))
    print("    for contrast, the SUPERSEDED two-window form (windows 1 vs 2)"
          " would have given sigma_self = %.6e" % abs(ms[1] - ms[0]))
    print("  STATIONARITY PRECONDITION (section 4c part 1): %s"
          % ("HOLDS on this series" if ok else "FAILS"))
    # the registered 1e-6 criterion, over the WHOLE run
    below = [i for i, v in enumerate(r, 1) if v <= 1e-6]
    runs = []
    if below:
        s = p = below[0]
        for i in below[1:]:
            if i == p + 1:
                p = i
            else:
                runs.append((s, p)); s = p = i
        runs.append((s, p))
    print("  registered criterion 1e-6 over the WHOLE run: %d iterations at or"
          " below, in %d contiguous stretch(es)" % (len(below), len(runs)))
    for a, b in runs[:6]:
        print("    stretch iterations %d..%d (%d long)" % (a, b, b - a + 1))
    print("  value at the LAST iteration (%d): %.6e" % (n, r[-1]))
    print("  min over the whole run: %.6e at iteration %d"
          % (min(r), r.index(min(r)) + 1))
    print("  max over the registered span: %.6e" % max(span))


def main():
    for lv in ("c", "f"):
        probe(lv)
    print("=" * 74)
    print("DIAGNOSTIC ONLY.  No verdict, no band, no triple, no graded value.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
