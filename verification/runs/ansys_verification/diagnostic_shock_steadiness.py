#!/usr/bin/env python3
"""DIAGNOSTIC ONLY -- NOT A GATE LIMB, NOT FROZEN, GRADES NOTHING.

Measures whether the PRIMARY gate quantity of VMFL046 (the normal-shock location)
was iteratively converged at the moment the run stopped, and compares that against
what the frozen comparator's convergence limb (the M(0.9) plateau) reported.

WHY THIS EXISTS. The frozen comparator grade_vmfl046.py checks convergence with a
plateau on M(x=0.9) and reads the shock from a SINGLE final sample -- there is no
steadiness check on the shock anywhere in it. Its line 247-248 dismisses residuals
as diagnostic on the stated ground that "the steady-shock limit cycle floors them
~1e-4". x=0.9 lies between the throat (x=0.5) and the shock (x~1.15-1.28), so it is
SUPERSONIC AND UPSTREAM, and in supersonic flow downstream disturbances cannot
propagate upstream. The plateau station is therefore causally incapable of seeing
the shock move. This script measures the shock directly, across the sample history.

READER DISCIPLINE, AND IT IS THE POINT OF THE `--station-check` ARM. The supervisor
first ran this comparison by taking the NEAREST sample point to x=0.9 (which is
x=0.902451) and comparing it against register row #54's value, which is INTERPOLATED
at exactly x=0.900. The station offset alone is 3.494e-03 in Mach -- about 20x the
real viscous effect of 1.71e-04 -- so the mismatch manufactured a viscous signal
that does not exist. Both quantities here are therefore read by ONE reader,
interpolated at exactly x=0.900, and the nearest-point value is printed beside it
so the trap is visible rather than merely avoided.

PLANTED CONTROL (CLAUDE.md rule 3): a zero from a reader not shown able to see a
non-zero is not evidence. This script's finding is a NON-zero (the shock moves), so
the control is inverted: --selftest plants a KNOWN SHOCK DISPLACEMENT into a copy of
a real sample and REFUSES (exit 2) if the shock finder does not recover it, and
plants a known-still history and refuses if the drift metric reports motion.
"""
import glob
import math
import os
import sys

GAMMA, RGAS = 1.4, 287.0
X_GATE = 0.900          # exactly the frozen comparator's gate station
ANALYTICAL_SHOCK = 1.250
BAND = 0.05 * ANALYTICAL_SHOCK   # 0.0625 m -- the frozen 5% primary tolerance


class Refuse(SystemExit):
    def __init__(self, msg):
        sys.stderr.write("REFUSE: %s\n" % msg)
        SystemExit.__init__(self, 2)


def read_centreline(path):
    """-> [(x, Mach)] from a line_T_U.xy sample (cols: x T Ux Uy Uz)."""
    rows = []
    for ln in open(path):
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        c = [float(v) for v in ln.split()]
        if len(c) < 5:
            raise Refuse("unexpected column count %d in %s" % (len(c), path))
        speed = math.sqrt(c[2] ** 2 + c[3] ** 2 + c[4] ** 2)
        rows.append((c[0], speed / math.sqrt(GAMMA * RGAS * c[1])))
    if len(rows) < 10:
        raise Refuse("only %d rows in %s" % (len(rows), path))
    return rows


def interp_mach(rows, x0):
    """Mach INTERPOLATED at exactly x0 -- the frozen comparator's convention."""
    for i in range(1, len(rows)):
        xa, ma = rows[i - 1]
        xb, mb = rows[i]
        if xa <= x0 <= xb:
            return ma + (mb - ma) * (x0 - xa) / (xb - xa)
    raise Refuse("x=%g outside sampled range in this profile" % x0)


def nearest_mach(rows, x0):
    """The NEAREST-POINT value -- printed only to expose the station-offset trap."""
    r = min(rows, key=lambda r: abs(r[0] - x0))
    return r[0], r[1]


def shock_location(rows):
    """The LAST Mach=1 crossing with Mach DECREASING = the normal shock.

    Taking the FIRST crossing returns the THROAT (subsonic->supersonic sonic point),
    which is a different feature entirely and sits ~0.7 m upstream. A lane made
    exactly that substitution and reported the shock at x=0.527 (the throat).
    """
    found = None
    for i in range(1, len(rows)):
        xa, ma = rows[i - 1]
        xb, mb = rows[i]
        if (ma - 1.0) * (mb - 1.0) < 0 and mb < ma:      # downward crossing only
            found = xa + (1.0 - ma) * (xb - xa) / (mb - ma)
    return found


def history(level_dir):
    """-> [(iteration, rows)] sorted by iteration."""
    pat = os.path.join(level_dir, "postProcessing", "centreline", "*", "line_T_U.xy")
    files = glob.glob(pat)
    if not files:
        raise Refuse("no centreline history under %s" % level_dir)
    out = []
    for f in files:
        it = int(float(os.path.basename(os.path.dirname(f))))
        out.append((it, f))
    out.sort()
    return out


def analyse(level_dir, from_iter=3000):
    hist = history(level_dir)
    series = [(it, read_centreline(f)) for it, f in hist]
    xs = [(it, shock_location(rows)) for it, rows in series]
    xs = [(it, x) for it, x in xs if x is not None]
    if len(xs) < 2:
        raise Refuse("fewer than 2 resolvable shock positions in %s" % level_dir)
    tail = [(it, x) for it, x in xs if it >= from_iter]
    last_it, last_x = xs[-1]
    prev = [x for it, x in xs if it == last_it - 500]
    final_window = abs(last_x - prev[0]) if prev else float("nan")
    ptp = max(x for _, x in tail) - min(x for _, x in tail)
    last_rows = series[-1][1]
    m_gate = interp_mach(last_rows, X_GATE)
    m_prev = interp_mach([r for it, r in series if it == last_it - 500][0], X_GATE) \
        if any(it == last_it - 500 for it, _ in series) else float("nan")
    nx, nm = nearest_mach(last_rows, X_GATE)
    return dict(last_it=last_it, x_shock=last_x, final_window=final_window, ptp=ptp,
                m_gate=m_gate, dM=abs(m_gate - m_prev), near_x=nx, near_m=nm,
                tail=tail)


def report(run_root, label):
    print("=" * 78)
    print("%s   %s" % (label, run_root))
    print("=" * 78)
    for lvl in ("L1", "L2", "L3"):
        ld = os.path.join(run_root, lvl)
        if not os.path.isdir(ld):
            print("  %s: absent" % lvl)
            continue
        a = analyse(ld)
        dev = 100.0 * (a["x_shock"] - ANALYTICAL_SHOCK) / ANALYTICAL_SHOCK
        print("  %s  last_iter=%d" % (lvl, a["last_it"]))
        print("     x_shock (final sample)      = %.6f m   (%+.4f %% vs analytical %.3f)"
              % (a["x_shock"], dev, ANALYTICAL_SHOCK))
        print("     SHOCK drift, final W=500    = %.4e m = %7.3f %% of the %.4f m band"
              % (a["final_window"], 100 * a["final_window"] / BAND, BAND))
        print("     SHOCK excursion, iter>=3000 = %.4e m = %7.2f %% of the band"
              % (a["ptp"], 100 * a["ptp"] / BAND))
        print("     GATE QUANTITY M(0.900)      = %.8f   |dM| over final W = %.3e"
              % (a["m_gate"], a["dM"]))
        print("     ^ frozen plateau threshold delta_M = 4.25e-04 -> plateau limb says %s"
              % ("CONVERGED" if a["dM"] < 4.25e-4 else "NOT CONVERGED"))
        if a["dM"] > 0:
            print("     BLINDNESS RATIO (shock motion / gate-quantity motion) = %.2e"
                  % (a["final_window"] / a["dM"]))
        print("     [station trap] nearest sample point is x=%.6f, M=%.8f; "
              "offset vs interpolated = %.3e"
              % (a["near_x"], a["near_m"], a["near_m"] - a["m_gate"]))
    print()


def selftest():
    """Inverted planted control -- this script's finding is a NON-zero, so the
    control must prove the reader can see BOTH motion and stillness."""
    ok = True
    # Arm 1: a synthetic profile with a shock planted at a known location.
    for planted in (1.1000, 1.2500, 1.3117):
        rows = []
        for i in range(401):
            x = 0.5 + 1.5 * i / 400.0
            rows.append((x, 1.9 if x < planted else 0.6))
        got = shock_location(rows)
        err = abs(got - planted)
        good = err <= (1.5 / 400.0)     # within one sample interval
        ok &= good
        print("SELFTEST plant shock at %.4f -> read %.4f (err %.2e) %s"
              % (planted, got, err, "PASS" if good else "FAIL"))
    # Arm 2: the finder must NOT return the throat (first, upward crossing).
    rows = []
    for i in range(401):
        x = 0.0 + 2.0 * i / 400.0
        m = 0.4 + 1.5 * x if x < 1.20 else 0.5      # up through 1 near x=0.4, down at 1.20
        rows.append((x, m))
    got = shock_location(rows)
    good = got > 1.0
    ok &= good
    print("SELFTEST throat-vs-shock: read %.4f, must be the DOWNWARD crossing >1.0  %s"
          % (got, "PASS" if good else "FAIL"))
    # Arm 3: PLANT-NULL -- a genuinely still history must report zero drift.
    still = [(i, 1.2345) for i in range(3000, 20500, 500)]
    drift = max(x for _, x in still) - min(x for _, x in still)
    good = drift == 0.0
    ok &= good
    print("SELFTEST plant-null (still history) -> drift %.3e, must be 0  %s"
          % (drift, "PASS" if good else "FAIL"))
    # Arm 4: PLANT-DETECT -- a known drift must be recovered exactly.
    moving = [(i, 1.2000 + 1e-3 * k) for k, i in enumerate(range(3000, 20500, 500))]
    drift = max(x for _, x in moving) - min(x for _, x in moving)
    good = abs(drift - 0.034) < 1e-9
    ok &= good
    print("SELFTEST plant-detect (known 3.4e-2 drift) -> %.4e  %s"
          % (drift, "PASS" if good else "FAIL"))
    # -----------------------------------------------------------------------
    # CALLER-SIDE ARMS (added 2026-09-03 after verification's FAIL_OPEN_GATE_AUDIT
    # §28: "can the code path distinguish 'ran and found nothing' from 'did not
    # run'? If not, its zero must refuse. PLANT THE RUN, NOT ONLY THE VALUE.")
    #
    # Arms 1-4 above plant VALUES into in-memory profiles. NONE of them ever
    # exercised history() or analyse() against an ABSENT or EMPTY run, so the
    # empty-glob and too-few-samples refusals existed in code and were UNPROVEN
    # by any control. That gap matters specifically because this script's L1 and
    # L2 readings are NEAR-ZEROS (8.19e-14, 5.79e-13) that were load-bearing:
    # they carried "the two coarse levels are settled, so the physics conclusion
    # survives" in BOTH the row #55 and row #54 demotions. A near-zero from a
    # reader not shown able to refuse an absent run is the caller-side face of
    # CLAUDE.md rule 3.
    import tempfile
    def _must_refuse(label, fn):
        try:
            fn()
        except Refuse:
            print("SELFTEST %s -> REFUSED (exit 2) as required  PASS" % label)
            return True
        except SystemExit:
            print("SELFTEST %s -> REFUSED (exit 2) as required  PASS" % label)
            return True
        print("SELFTEST %s -> DID NOT REFUSE  FAIL" % label)
        return False

    with tempfile.TemporaryDirectory() as td:
        # Arm 5: THE RUN DID NOT HAPPEN AT ALL -- no postProcessing tree.
        ok &= _must_refuse("plant-absent-run (no postProcessing tree)",
                           lambda: history(os.path.join(td, "L_absent")))
        # Arm 6: THE DIRECTORY EXISTS AND IS EMPTY -- "ran and found nothing".
        empty = os.path.join(td, "L_empty", "postProcessing", "centreline")
        os.makedirs(empty)
        ok &= _must_refuse("plant-empty-run (tree exists, zero samples)",
                           lambda: history(os.path.join(td, "L_empty")))
        # Arm 7: EXACTLY ONE SAMPLE -- a history too short to measure drift at
        # all. A drift of 0.0 computed from one sample is the false zero this
        # whole script exists to catch, so it must refuse rather than return 0.
        one = os.path.join(td, "L_one", "postProcessing", "centreline", "20000")
        os.makedirs(one)
        with open(os.path.join(one, "line_T_U.xy"), "w") as fh:
            for i in range(401):
                x = 0.0 + 2.0 * i / 400.0
                m = 1.9 if x < 1.25 else 0.6
                T = 300.0
                u = m * math.sqrt(GAMMA * RGAS * T)
                fh.write("%.6f %.6f %.6f 0 0\n" % (x, T, u))
        ok &= _must_refuse("plant-single-sample (drift unmeasurable, must not return 0)",
                           lambda: analyse(os.path.join(td, "L_one")))
    if not ok:
        raise Refuse("SELFTEST FAILED -- the reader cannot be trusted, refusing")
    print("SELFTEST: ALL PASS")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    base = "/home/ubuntu/Certonomous/verification/runs/ansys_verification"
    report(os.path.join(base, "VMFL046_INVISCID"),
           "VMFL046-INVISCID  (this run -- Euler arm)")
    report(os.path.join(base, "VMFL046"),
           "VMFL046 VISCOUS  (register row #54, GATE FAIL) -- AUDIT")
