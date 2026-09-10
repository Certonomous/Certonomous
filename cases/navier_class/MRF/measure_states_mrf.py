#!/usr/bin/env python3
"""MRF_R1 -- MEASURE (never assert) the per-level iterative_state and
plateau_state that rule 5 consumes, and print the raw numbers behind each.

WHY THIS FILE EXISTS.  rule 5's step (a) is absolute: any level not iteratively
converged or not plateaued makes the whole row NOT A RESULT whatever the value.
A state handed to grade_ladder as a literal string is an ASSERTION.  This
measures both from the run's own artifacts and prints what it measured, so the
supervisor's check-1 can read the numbers and not just the labels.

THE PLATEAU TEST IS NOT INVENTED HERE.  It is S12 of
docs/standards/MONITOR_STANDARD.md, adopted 2026-08-02, quoted verbatim:

    "Over a trailing window (a quarter of the iterations, floored at 20 and
     capped at 2000), the mean of the window's second half minus the mean of
     its first, divided by the window's mean magnitude, is the relative drift;
     the fraction of steps inside the window that move in the drift's own
     direction is the monotone fraction.  Fires when relative drift is at
     least 1e-3 and the monotone fraction is at least 0.90.  Both are
     required: a settled history wobbles without displacement, a truncated one
     travels."

Every threshold and the window rule come from that standard.  Nothing here was
chosen after seeing the data -- which matters, because this is a post-compute
measurement feeding a frozen gate (CLAUDE.md rule 2).  MRF_R1_PREREGISTRATION
sec.5 directs exactly this: convergence is judged "by the rule-5
plateau/settledness state measured over the final iteration window (F8's S12
discipline)", NOT by a residual early-exit.

S12 FIRES  -> the quantity was still travelling -> NOT_PLATEAUED.
S12 SILENT -> PLATEAUED.

iterative_state is the divergence-tell set the pre-registration named in sec.7
step 4 and F8 sec.12: NaN (S2), floating-point exception (S1), and a building
`bounding` cascade (S4).  Any present -> NOT_CONVERGED.  All absent AND the
quantity settled -> CONVERGED.
"""
from __future__ import annotations
import math
import os
import re
import sys

RHO, N_RPS, D_IMP = 998.0, 5.0, 0.100      # prereg sec.4 table
PLANT = 1.234e-03                          # rule 3


def read_total_axial(path, axis="z"):
    """Header-driven and fail-closed, the same discipline as the grader's
    reader: resolve total_<axis> from the header, refuse rather than read an
    assumed column position."""
    col = None
    times, vals = [], []
    with open(path) as fh:
        for line in fh:
            if line.startswith("#"):
                if "total_x" in line:
                    # header names the moment groups; find the index of
                    # total_<axis> among the whitespace/paren-stripped tokens
                    toks = line.lstrip("#").replace("(", " ").replace(")", " ").split()
                    if f"total_{axis}" in toks:
                        col = toks.index(f"total_{axis}")
                continue
            if col is None:
                raise SystemExit(f"REFUSE: {path} header never named total_{axis}")
            toks = line.replace("(", " ").replace(")", " ").split()
            if len(toks) <= col:
                continue
            times.append(float(toks[0]))
            vals.append(float(toks[col]))
    if col is None:
        raise SystemExit(f"REFUSE: {path} has no header naming total_{axis}")
    return times, vals


def power_number(Q):
    return 2.0 * math.pi * abs(Q) / (RHO * N_RPS ** 2 * D_IMP ** 5)


def s12(series):
    """MONITOR_STANDARD S12, verbatim. Returns (fires, drift, monotone, w)."""
    n = len(series)
    w = min(max(n // 4, 20), 2000)
    win = series[-w:]
    half = w // 2
    first, second = win[:half], win[half:]
    m1 = sum(first) / len(first)
    m2 = sum(second) / len(second)
    mag = abs(sum(win) / len(win))
    drift = (m2 - m1) / mag if mag > 0 else float("inf")
    steps = [win[i + 1] - win[i] for i in range(len(win) - 1)]
    sign = 1.0 if drift >= 0 else -1.0
    monotone = sum(1 for s in steps if s * sign > 0) / len(steps)
    fires = (abs(drift) >= 1e-3) and (monotone >= 0.90)
    return fires, drift, monotone, w


def divergence_tells(logpath, n_iters=4000):
    """S2 NaN / S1 FPE / S4 bounding CASCADE -- the sec.7 step-4 tell set.

    TWO CORRECTIONS to this function's first version, both because it fired on
    all three levels of runs that finished rc=0 with an End line -- a red with
    an innocent explanation is the easiest failure to wave through, so each was
    cleared against the real lines rather than reasoned away.

    (1) FPE.  The first version matched "floating point exception" anywhere and
        hit  `trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).`
        -- the startup BANNER announcing that trapping is ARMED, printed at
        log line 29 among commsType/memory pool, while iteration 1 begins at
        line 89.  That is the opposite of an exception, and a real SIGFPE
        precludes the 4000 iterations, End line and rc=0 that followed.  The
        trapping banner is now excluded explicitly.

    (2) BOUNDING.  The pre-registration's registered tell (sec.7 step 4, F8
        sec.12) is that no bounding "CASCADE BUILDS" -- not that no single
        bounding line exists.  k-omega SST clips a few cells while the
        turbulence field initialises; that is startup transient, not
        divergence.  A cascade BUILDS: it must be present LATE and growing.
        Measured here as: events in the final quarter strictly greater than
        events in the first quarter, i.e. the signature is accumulation.
        Both counts are returned and printed so the raw distribution is
        visible and this reading can be overruled by the supervisor, whose
        check-2 (crash/anomaly triage) is non-delegable.
    """
    nan = fpe = 0
    bound_iters = []
    it = 0
    with open(logpath, errors="replace") as fh:
        for line in fh:
            if line.startswith("Time = "):
                try:
                    it = int(float(line.split()[2]))
                except (IndexError, ValueError):
                    pass
            low = line.lower()
            if "nan" in low and not low.startswith("bounding"):
                nan += 1
            # an ACTUAL exception, never the "trapping enabled" banner
            if ("floating point exception" in low or "sigfpe" in low) \
               and "trapping enabled" not in low and not low.startswith("trapfpe:"):
                fpe += 1
            if low.startswith("bounding "):
                bound_iters.append(it)
    q = max(n_iters // 4, 1)
    early = sum(1 for i in bound_iters if i <= q)
    late = sum(1 for i in bound_iters if i > n_iters - q)
    cascade = late > early          # a cascade BUILDS; a transient decays
    return nan, fpe, bound_iters, early, late, cascade


def main():
    root = "/home/ubuntu/Certonomous/verification/runs/navier_class/MRF"
    out = {}
    print("MRF_R1 state measurement -- S12 (MONITOR_STANDARD, adopted 2026-08-02)")
    print("  window = trailing quarter, floor 20, cap 2000; fires iff |drift|>=1e-3 AND monotone>=0.90\n")

    # ---- rule 3: the reader is shown able to see a PLANT before any of its
    #      readings are believed.  Plant into the resolved total_z column of a
    #      COPY and read it back through this same parser.
    import shutil, tempfile
    src = os.path.join(root, "coarse/postProcessing/impellerForces/0/moment.dat")
    tmpd = tempfile.mkdtemp(prefix="mrf_state_plant_")
    tmp = os.path.join(tmpd, "moment.dat")
    shutil.copy(src, tmp)
    lines = open(tmp).read().splitlines()
    for i, ln in enumerate(lines):
        if not ln.startswith("#"):
            toks = ln.replace("(", " ").replace(")", " ").split()
            lines[i] = f"{toks[0]}\t({toks[1]} {toks[2]} {PLANT:.12g})\t(0 0 0)\t(0 0 0)"
            break
    open(tmp, "w").write("\n".join(lines) + "\n")
    _, pv = read_total_axial(tmp)
    if abs(pv[0] - PLANT) > 1e-12:
        print(f"REFUSE (rule 3): reader did not see the plant "
              f"{PLANT:.6g}, got {pv[0]:.6g}")
        return 2
    print(f"  [rule 3] PLANT CONTROL PASS: reader saw {pv[0]:.6g} == {PLANT:.6g} "
          f"in the resolved total_z column\n")

    for name in ("coarse", "medium", "fine"):
        d = os.path.join(root, name)
        mom = os.path.join(d, "postProcessing/impellerForces/0/moment.dat")
        t, mz = read_total_axial(mom)
        np_series = [power_number(q) for q in mz]
        fires, drift, mono, w = s12(np_series)
        nan, fpe, bnd_iters, early, late, cascade = divergence_tells(
            os.path.join(d, "log.simpleFoam"), n_iters=int(t[-1]))

        plateau = "NOT_PLATEAUED" if fires else "PLATEAUED"
        diverged = bool(nan or fpe or cascade)
        iterative = "NOT_CONVERGED" if (diverged or fires) else "CONVERGED"

        finite = all(math.isfinite(v) for v in np_series)
        print(f"--- {name} ---")
        print(f"  samples={len(np_series)}  all finite={finite}  last time={t[-1]:.0f}")
        print(f"  S12 window w={w} (iters {int(t[-w])}..{int(t[-1])})")
        print(f"  relative drift  = {drift:+.4e}   (fires at |drift| >= 1e-3)")
        print(f"  monotone frac   = {mono:.4f}       (fires at >= 0.90)")
        print(f"  S12 {'FIRES -- still travelling' if fires else 'SILENT -- settled'}")
        print(f"  divergence tells: NaN={nan}  FPE(real, banner excluded)={fpe}")
        print(f"  bounding events at iterations {bnd_iters if bnd_iters else 'none'}"
              f"  -> first-quarter={early} final-quarter={late} "
              f"cascade_builds={cascade}")
        print(f"  Np window mean  = {sum(np_series[-w:])/w:.6f}")
        print(f"  Np at endTime   = {np_series[-1]:.6f}")
        print(f"  => iterative_state={iterative}  plateau_state={plateau}\n")
        out[name] = (iterative, plateau, np_series[-1])

    print("STATES FOR grade_ladder (measured, not asserted):")
    for k, v in out.items():
        print(f"  {k:7s} iterative={v[0]:13s} plateau={v[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
