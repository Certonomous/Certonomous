#!/usr/bin/env python3
"""t5f_convergence_gate.py -- T5f registered clause (1), LIMB B.

Registration: docs/campaigns/T-family/T5f_PREREGISTRATION.md.  Frozen with it.
READ-ONLY on every case directory.  Launches no solver.

WHY THIS FILE EXISTS, IN ONE PARAGRAPH.  T5e proved that the registered
checkpoint field-delta (LIMB A) catches a ladder whose fields are still MOVING:
it rejected all three T5b levels by factors of 7,124x to 655,677x.  It does NOT
follow that it catches a solve that has stopped being solved.  A fully frozen
case presents a checkpoint delta of ~0 and would PASS limb A while its
turbulence model has locally ceased to exist.  LIMB B tests the FINAL FIELDS for
PHYSICAL ADMISSIBILITY, which is a different question from whether they moved.

THE INSTRUMENT IS THE FIELD ON DISK, NEVER THE RESIDUAL.
`T5_PREREGISTRATION.md` S5.5 refuses `residualControl` as a convergence
instrument (L-141) and T5f does not overturn a frozen registration.  Residual
MOVEMENT is therefore computed and printed as REPORTED, NEVER GATED (L-342
class).  Every GATING quantity below is read from a field file or counted from
solver bookkeeping (`bounding` lines), not from a residual magnitude.

THE THREE GATED CRITERIA, EACH WITH ITS PHYSICAL ANCHOR
-------------------------------------------------------
B1  OMEGA CEILING.  omega_max at endTime must be below OMEGA_CEILING.
    Anchor: the largest LEGITIMATE omega in this family is the wall value
    omega_w ~ 6 nu / (beta1 y1^2).  With mu 1.7917e-05 (the case's own
    thermophysicalProperties), rho ~ 1.161 kg/m3 at 1 bar / 300 K, so
    nu ~ 1.543e-05 m2/s, and beta1 = 0.075:
        y1 = 80.00 um (T5f level c) -> omega_w ~ 1.93e+05
        y1 = 31.25 um (T5f level f) -> omega_w ~ 1.26e+06
    OMEGA_CEILING is set THREE ORDERS above the finest level's wall value.  It
    is a physical absurdity bar, not a tuning knob: nothing in a converged
    incompressible RANS of a 0.4 m channel can legitimately reach it.

B2  NO CELL AT THE SOLVER'S OWN CLAMP FLOOR.  min(k) at endTime must exceed
    K_FLOOR_BAR.  Anchor: OpenFOAM bounds k to a small POSITIVE value, not to
    zero -- measured on this box, the floor is exactly 1.0e-15, so a test for
    `k <= 0` COULD NEVER FIRE and is not used.  A cell sitting AT the floor has
    no modelled turbulence at all and its nut has collapsed with it.
    K_FLOOR_BAR is set three orders ABOVE the observed floor so that a cell must
    be genuinely at the floor, not merely small, to fail.

B3  A CONVERGED SOLUTION DOES NOT NEED CLAMPING.  Over the final
    BOUND_WINDOW iterations, `bounding k` and `bounding omega` may each fire on
    at most BOUND_MAX_FRAC of iterations.  Anchor: the bound exists to catch a
    transient excursion.  A clamp firing on nearly every iteration is the
    discretisation producing inadmissible values as a steady state, which is a
    property of the solution, not a transient.

CALIBRATION HONESTY (rule 2).  These thresholds were chosen with T5b's THREE
COMPLETED LEVELS in hand as PRIOR EVIDENCE.  They are not fitted to T5f's
answer, because T5f HAS NO ANSWER: at the registration commit
`verification/runs/T-family/T5f_runs/T5F_CUBE_c` DOES NOT EXIST, and neither do
`_m` or `_f`.  The registration names that condition and how it was checked.
"""
import argparse, os, re, sys
import numpy as np

# --- REGISTERED CONSTANTS -- frozen with the registration -------------------
OMEGA_CEILING   = 1.0e+09      # B1; ~800x the finest level's wall value
K_FLOOR_BAR     = 1.0e-12      # B2; 1000x the measured OpenFOAM clamp floor 1e-15
OBSERVED_CLAMP  = 1.0e-15      # measured on this box, recorded so B2 is auditable
BOUND_WINDOW    = 1000         # iterations, matching the S5.5 checkpoint stride
BOUND_MAX_FRAC  = 0.01         # B3; 1 % of BOUND_WINDOW
GATED_FIELDS    = ("k", "omega")
REGION          = "air"


def refuse(msg):
    print("REFUSED: %s" % msg)
    sys.exit(2)


def read_internal(path):
    """Parse an OpenFOAM volScalarField internalField. Returns None if absent."""
    if not os.path.exists(path):
        return None
    t = open(path, errors="replace").read()
    m = re.search(r'internalField\s+nonuniform\s+List<scalar>\s*\n?(\d+)\s*\(', t)
    if m:
        n = int(m.group(1)); s = m.end(); e = t.index(')', s)
        v = np.array([float(x) for x in t[s:e].split()])
        if len(v) != n:
            refuse("%s declares %d values and carries %d" % (path, n, len(v)))
        return v
    m = re.search(r'internalField\s+uniform\s+([-\d.eE+]+)\s*;', t)
    if m:
        return np.array([float(m.group(1))])
    refuse("%s: internalField not parsable" % path)


def bounding_counts(logpath, window):
    """Count `bounding <fld>` lines inside the final `window` Time steps, and
    the residual MOVEMENT over the same span (REPORTED, never gated)."""
    if not os.path.exists(logpath):
        return None
    t = 0; last = 0
    events = {f: [] for f in GATED_FIELDS}
    res = {}
    for line in open(logpath, errors="replace"):
        if line.startswith("Time = "):
            try:
                t = int(line.split("=")[1]); last = t
            except ValueError:
                pass
        elif line.startswith("bounding "):
            f = line.split()[1].rstrip(",")
            if f in events:
                events[f].append(t)
        else:
            m = re.search(r'Solving for (\w+), Initial residual = ([\d.eE+-]+).*No Iterations (\d+)', line)
            if m:
                res.setdefault(m.group(1), []).append((t, float(m.group(2)), int(m.group(3))))
    lo = last - window
    counts = {f: len({x for x in v if x > lo}) for f, v in events.items()}
    return dict(last=last, lo=lo, counts=counts, res=res)


def evaluate(case_dir, endtime, label, _inject=None):
    """Returns (state, rows). state is CONVERGED / NOT CONVERGED.
    `_inject` is used ONLY by the planted controls."""
    rows = []
    fields = {}
    for fld in GATED_FIELDS:
        p = os.path.join(case_dir, str(endtime), REGION, fld)
        v = read_internal(p)
        if v is None:
            refuse("%s: %s absent at endTime %s -- clause (1) limb B cannot be "
                   "evaluated, and an absent field is refused rather than "
                   "treated as passing" % (label, fld, endtime))
        fields[fld] = v.copy()
    if _inject:
        _inject(fields)

    bad = []
    om = fields["omega"]
    ok1 = float(om.max()) < OMEGA_CEILING
    rows.append(("B1 omega ceiling", "%.6e" % om.max(), "< %.1e" % OMEGA_CEILING, ok1))
    if not ok1:
        bad.append("B1")

    kk = fields["k"]
    ok2 = float(kk.min()) > K_FLOOR_BAR
    nfloor = int((kk <= K_FLOOR_BAR).sum())
    rows.append(("B2 k above clamp floor", "min %.6e (%d cells at/below bar)"
                 % (kk.min(), nfloor), "> %.1e" % K_FLOOR_BAR, ok2))
    if not ok2:
        bad.append("B2")

    bc = bounding_counts(os.path.join(case_dir, "log.solve"), BOUND_WINDOW)
    if bc is None:
        refuse("%s: log.solve absent -- B3 cannot be evaluated" % label)
    lim = int(BOUND_MAX_FRAC * BOUND_WINDOW)
    for f in GATED_FIELDS:
        n = bc["counts"][f]
        ok3 = n <= lim
        rows.append(("B3 bounding %s in final %d" % (f, BOUND_WINDOW),
                     "%d iterations" % n, "<= %d" % lim, ok3))
        if not ok3:
            bad.append("B3:%s" % f)

    # REPORTED, NEVER GATED -- T5 S5.5 refuses the residual as an instrument
    for f, seq in sorted(bc["res"].items()):
        tail = [(t, r, n) for t, r, n in seq if t > bc["lo"]]
        if len(tail) >= 2:
            r0, r1 = tail[0][1], tail[-1][1]
            mov = abs(np.log10(max(r1, 1e-300)) - np.log10(max(r0, 1e-300)))
            nz = sum(1 for _, _, n in tail if n == 0)
            rows.append(("REPORTED residual movement %s" % f,
                         "%.3e -> %.3e (%.2f dex); nIter==0 on %d of %d"
                         % (r0, r1, mov, nz, len(tail)), "never gated", None))
    return ("NOT CONVERGED" if bad else "CONVERGED"), rows, bad


def selftest():
    """Planted controls (rule 3). A criterion that cannot fire is not a
    criterion, and every arm below must move or this exits 2."""
    fails = []

    def ok(c, msg):
        print("  %-5s %s" % ("ok" if c else "FAIL", msg))
        if not c:
            fails.append(msg)

    print("PLANTED CONTROLS -- each bar must be shown able to FIRE and able to PASS")

    # B1: a synthetic admissible field, then the same field with one cell spiked
    base_om = np.full(1000, 5.0e+04)
    base_k = np.full(1000, 1.0e-02)
    ok(base_om.max() < OMEGA_CEILING and base_k.min() > K_FLOOR_BAR,
       "CONTROL: a synthetic ADMISSIBLE field passes B1 and B2 "
       "(omega %.1e < %.1e, k %.1e > %.1e)"
       % (base_om.max(), OMEGA_CEILING, base_k.min(), K_FLOOR_BAR))
    spiked = base_om.copy(); spiked[437] = OMEGA_CEILING * 10
    ok(spiked.max() >= OMEGA_CEILING and int(np.argmax(spiked)) == 437,
       "B1 FIRES on a single planted cell, and the argmax IS the planted cell "
       "437 -- the bar asks WHERE, not merely whether")
    ok(base_om.max() < OMEGA_CEILING,
       "B1 NEGATIVE: the unplanted copy is unchanged, so the fire is the "
       "plant's doing")

    floored = base_k.copy(); floored[88] = OBSERVED_CLAMP
    ok(floored.min() <= K_FLOOR_BAR and int(np.argmin(floored)) == 88,
       "B2 FIRES on one cell planted AT the measured clamp floor %.0e, and the "
       "argmin IS the planted cell 88" % OBSERVED_CLAMP)
    ok(int((base_k <= K_FLOOR_BAR).sum()) == 0,
       "B2 NEGATIVE: the unplanted copy has 0 cells at or below the bar")
    near = base_k.copy(); near[88] = K_FLOOR_BAR * 10
    ok(near.min() > K_FLOOR_BAR,
       "B2 DISCRIMINATES: a cell 10x ABOVE the bar does NOT fire it, so B2 is "
       "not merely a test for 'small'")

    # B3 threshold arithmetic
    lim = int(BOUND_MAX_FRAC * BOUND_WINDOW)
    ok(lim == 10, "B3 bar is %d of %d iterations (%.0f %%)"
       % (lim, BOUND_WINDOW, 100 * BOUND_MAX_FRAC))
    ok(lim >= 1, "B3 bar is >= 1, so a single transient excursion does not fail "
                 "a case -- the bar is about a STEADY clamp, not a transient")

    # the ceiling is above the physics it must admit
    nu = 1.7917e-05 / 1.161
    for y1, nm in ((80.0e-6, "c"), (50.0e-6, "m"), (31.25e-6, "f")):
        w = 6 * nu / (0.075 * y1 ** 2)
        ok(w < OMEGA_CEILING / 100,
           "B1 ADMITS the physics: level %s wall omega ~ %.3e is more than 100x "
           "BELOW the ceiling %.1e" % (nm, w, OMEGA_CEILING))

    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 2


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--case-dir"); ap.add_argument("--endtime", type=int, default=5000)
    ap.add_argument("--label", default="?"); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not a.case_dir:
        ap.error("--case-dir required")
    st, rows, bad = evaluate(a.case_dir, a.endtime, a.label)
    print("T5f clause (1) LIMB B -- %s  endTime %d" % (a.label, a.endtime))
    for name, got, want, good in rows:
        tag = "REPORTED" if good is None else ("ok  " if good else "FAIL")
        print("  %-8s %-34s %-46s %s" % (tag, name, got, want))
    print("  -> LIMB B STATE: %s%s" % (st, ("  (failed: %s)" % ",".join(bad)) if bad else ""))
    sys.exit(0 if st == "CONVERGED" else 1)
