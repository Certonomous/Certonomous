#!/usr/bin/env python3
"""analyse_k2bU3R3.py -- grade the K2b-U3-R3 successor run (the un-confounded
Test D at the nearest builder-feasible 59 mm uniform mesh, 80 s) against the SAME gate as its
frozen predecessor, plus the planted-zero control that predecessor lacks.

    python3 analyse_k2bU3R3.py            # grade the true run
    python3 analyse_k2bU3R3.py --selftest # prove the planted control fires

WHAT IS RE-USED, UNCHANGED, FROM THE FROZEN PREDECESSOR analyse_k2bU3.py
(git blob d1500a5f..., grading K2bU3R3_PREREGISTRATION.md, itself citing
K2b_3D_UNSTEADINESS_PREREGISTRATION.md sha256 91a26fc9...):
  * the disk reader   series()                 -- imported, NOT re-implemented
  * the grade + gate  grade()                  -- imported, NOT re-implemented
  * every constant    P_SURV,P_DAMP,R_SURV,R_DAMP = 0.30,0.10,0.8,0.5
                      MIN_STEPS_PER_PERIOD,MIN_SAMPLES_PER_PERIOD = 20,10
                      DISCARD,WIN = 40.0,20.0 ; PERIOD_2D = 6.000
                      -- imported, NOT redefined
  * the aliasing guard (>=20 steps AND >=10 samples per 6.000 s period -> else
    REFUSED -> P3) and the 60-80 vs 40-60 s windows -- inside the imported
    grade(), exercised unchanged.
  * the SURVIVES->P1 / DAMPS->P2 / (REFUSED|UNDECIDABLE)->P3 mapping.

WHAT IS ADDED (the only new thing): the planted-zero control that
K2bU3R3_PREREGISTRATION.md §5.1 requires and the frozen predecessor lacks
(CLAUDE.md rule 3; memory a-zero-needs-a-live-planted-control). Before the true
series is graded, a known non-zero peak-to-peak PLANT is planted into a COPY of
the run's on-disk monitor log and re-read back THROUGH THE SAME reader the grade
uses (the imported series()); if the reader cannot recover PLANT the script
REFUSES (exit 2). A DAMPS verdict is a near-zero p2p, and a near-zero from a
reader not shown able to see a non-zero is not evidence.

NO GATE, THRESHOLD, GUARD FLOOR, WINDOW OR OUTCOME MEANING IS ALTERED HERE. Only
the case directory is re-pointed (59 mm K2bU3R3_D59) and the planted control is
added. This file does not edit analyse_k2bU3.py.
"""
import math, os, re, shutil, statistics, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# ---- everything below the import is re-used UNCHANGED from the frozen predecessor
from analyse_k2bU3 import (                       # noqa: E402
    series, grade,                                # the disk reader and the gate
    P_SURV, P_DAMP, R_SURV, R_DAMP,               # 0.30, 0.10, 0.8, 0.5
    MIN_STEPS_PER_PERIOD, MIN_SAMPLES_PER_PERIOD, # 20, 10
    DISCARD, WIN, PERIOD_2D,                       # 40.0, 20.0, 6.000
    HERE as K_HERE,                                # the base series() joins to
)

# ---- the ONE new gate-independent constant: the planted-zero perturbation ----
PLANT = 1.234e-03          # K, planted peak-to-peak (as analyse_t3.py:81)
TOL   = 1.0e-9             # K, float round-trip tolerance for exact recovery
LOGNAME = "log.buoyantBoussinesqPimpleFoam"

# The successor's own 59 mm case (K2bU3R3_PREREGISTRATION.md §5.3), and the same
# four-rack graded quantity as the predecessor's Test D (§2, §3.3).
CASE = "K2bU3R3_D59"
RXS  = [rf'weightedAverage\(rack{r}_in\) of T = ([-0-9.eE+]+)' for r in range(4)]


# ---------------------------------------------------------------------------
# The p2p reader, EXPRESSED THROUGH THE IMPORTED series(). Its combine/window/
# p2p arithmetic mirrors analyse_k2bU3.grade() lines 51-52 and 66-69 verbatim;
# it exists only so the planted control can report a NUMBER. The true verdict
# below is produced by the imported grade() itself, unchanged.
# ---------------------------------------------------------------------------
def window_p2p_via_series(case_rel, rxs):
    """Read a log THROUGH the imported, unmodified series() (the same disk reader
    grade() uses) and return (final_window_p2p, n_window, window_mean).
    Returns (None, 0, None) when there is no gradeable final window."""
    times, per = series(case_rel, rxs)
    keys = [k for k in rxs if k in per]
    if not times or not keys:
        return None, 0, None
    n = min(len(per[k]) for k in keys)                          # grade():50
    ts = [(per[keys[0]][i][0],                                  # grade():51-52
           statistics.fmean(per[k][i][1] for k in keys)) for i in range(n)]
    fin = [b for a, b in ts if DISCARD + WIN < a <= DISCARD + 2 * WIN]  # grade():66
    if not fin:
        return None, 0, None
    return max(fin) - min(fin), len(fin), statistics.fmean(fin)  # grade():68


def blind_window_p2p(case_rel, rxs):
    """A reader that ignores the disk and always returns zero p2p -- the failure
    mode the planted control exists to catch. Used only by --selftest."""
    return 0.0, 999, 300.0


# ---------------------------------------------------------------------------
# Plant a KNOWN peak-to-peak PLANT into a copy of the on-disk monitor log, by
# overwriting the final-window monitor samples with a two-level square wave of
# amplitude PLANT centred on the run's true window mean. The window's mean-over-
# racks series then has peak-to-peak == PLANT exactly, whatever the true data.
# ---------------------------------------------------------------------------
def _plant_squarewave(src_log, dst_log, rxs, center):
    lines = open(src_log, errors="replace").read().split("\n")
    out, cur, msamp, level, lastt = [], None, -1, None, None
    for line in lines:
        m = re.match(r'^Time = ([0-9.eE+-]+)\s*$', line)
        if m:
            cur = float(m.group(1))
            out.append(line)
            continue
        in_win = cur is not None and DISCARD + WIN < cur <= DISCARD + 2 * WIN
        if in_win and any(re.search(rx, line) for rx in rxs):
            if cur != lastt:                     # alternate per MONITOR timestamp,
                msamp += 1                       # not per Time line (monitors are
                level = center + (PLANT / 2 if msamp % 2 == 0 else -PLANT / 2)
                lastt = cur                      # not written every step)
            out.append(re.sub(r'= [-0-9.eE+]+', f'= {level!r}', line, count=1))
        else:
            out.append(line)
    open(dst_log, "w").write("\n".join(out))


def planted_zero_control(src_log, rxs, reader=window_p2p_via_series):
    """Two arms on a COPY of the run's log:
      * negative arm  -- identical bytes, no plant -> the TRUE final-window p2p
                         (a near-zero is permitted; it proves the reader is not
                         hard-wired to PLANT).
      * positive arm  -- PLANT planted, re-read through `reader` -> must recover
                         PLANT within TOL, else the reader is blind and the
                         grade's near-zeros mean nothing.
    Planting is always constructed from the truth (window_p2p_via_series); only
    the RECOVERY uses `reader`, so a blind reader is caught."""
    if not os.path.isfile(src_log):
        return dict(passed=False, why=f"missing log {src_log}")
    tmp = tempfile.mkdtemp(prefix="k2bU3R3plant_")
    try:
        neg = os.path.join(tmp, "neg"); os.makedirs(neg)
        shutil.copy(src_log, os.path.join(neg, LOGNAME))
        neg_rel = os.path.relpath(neg, K_HERE)
        p_true, n_true, center = window_p2p_via_series(neg_rel, rxs)
        if center is None:
            return dict(passed=False, why="no gradeable final window in the log")
        pos = os.path.join(tmp, "pos"); os.makedirs(pos)
        _plant_squarewave(src_log, os.path.join(pos, LOGNAME), rxs, center)
        pos_rel = os.path.relpath(pos, K_HERE)
        p_plant, n_plant, _ = reader(pos_rel, rxs)
        # negative-arm p2p read with the SAME reader-under-test (for the blind proof)
        p_true_r, _, _ = reader(neg_rel, rxs)
        passed = (p_plant is not None and n_plant >= 2
                  and abs(p_plant - PLANT) <= TOL)
        return dict(passed=passed, planted=PLANT, recovered=p_plant,
                    true=p_true, true_reader=p_true_r, floor=PLANT, tol=TOL,
                    n_window=n_plant)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
def main():
    print("=" * 78)
    print("K2b-U3-R3  DOES THE 2D LIMIT CYCLE SURVIVE IN 3D AT THE 59 mm FEASIBLE MESH?")
    print("graded against K2bU3R3_PREREGISTRATION.md; gate re-used unchanged from")
    print("analyse_k2bU3.py (git blob d1500a5f...), K2b_3D_UNSTEADINESS_PRE... 91a26fc9...")
    print(f"thresholds: p2p >= {P_SURV} K and ratio >= {R_SURV} = SURVIVES;"
          f"  p2p <= {P_DAMP} K or ratio <= {R_DAMP} = DAMPS")
    print(f"aliasing floors: {MIN_STEPS_PER_PERIOD} steps and "
          f"{MIN_SAMPLES_PER_PERIOD} samples per {PERIOD_2D:.3f} s period")
    print("=" * 78)

    log = os.path.join(K_HERE, CASE, LOGNAME)
    if not os.path.isfile(log):
        print(f"\nREFUSED (exit 2): missing input -- no monitor log at {log}")
        return 2

    # ---- PLANTED-ZERO CONTROL (rule 3 / §5.1) -- BEFORE the true grade --------
    print("\nPLANTED-ZERO CONTROL (CLAUDE.md rule 3; §5.1) -- closing the gap the")
    print("frozen predecessor lacks. A DAMPS verdict is a near-zero p2p and must")
    print("not be believed from a reader not shown able to see a non-zero.")
    pz = planted_zero_control(log, RXS)
    if pz.get("why"):
        print(f"  REFUSED (exit 2): {pz['why']}")
        return 2
    print(f"  planted p2p PLANT           = {pz['planted']:.6e} K   (tol {pz['tol']:.1e} K)")
    print(f"  negative arm (no plant)     = {pz['true']:.6e} K   "
          f"(true final-window p2p; near-zero permitted)")
    print(f"  positive arm (PLANT, re-read through series()) = {pz['recovered']:.6e} K")
    print(f"  demonstrated detection floor = {pz['floor']:.6e} K   "
          f"({P_DAMP / pz['floor']:.0f}x below the {P_DAMP} K DAMPS floor)")
    if not pz["passed"]:
        print("  ==> REFUSED (exit 2): the reader did NOT recover the planted p2p; "
              "its near-zeros are not evidence.")
        return 2
    print("  ==> control PASSES: the grade's reader can see a p2p down to the "
          "floor above, so a DAMPS near-zero is a MEASURED value.")

    # ---- the true grade -- the IMPORTED grade(), gate unchanged --------------
    print("\nTEST D (R3) -- the full 3D module, N=4 racks, OPEN row ends, h=0.059 m.")
    d, dper = grade(CASE, "Test D R3 (3D, h=0.059)", RXS)
    if d is None:
        print(f"\nREFUSED (exit 2): missing/insufficient input -- the run did not")
        print("reach a gradeable state (no samples, or endTime window not reached).")
        return 2

    print("\n" + "=" * 78)
    if d == "SURVIVES":
        print("OUTCOME P1 -- IT SURVIVES IN 3D. The limit cycle is not an artefact of")
        print("two-dimensionality at the nearest builder-feasible 59 mm module. O1's consequence")
        print("carries: the module needs a transient formulation, the section 9 steady")
        print("estimate stays VOID, and K2a section 9 must be re-specified for")
        print("transient-with-averaging at this provisioning.")
    elif d == "DAMPS":
        print("OUTCOME P2 -- IT DAMPS IN 3D. Three-dimensionality damps the mode at the")
        print("nearest builder-feasible 59 mm module. The 2D finding STANDS as true of the 2D slice --")
        print("it is not retracted and it was not wrong. What changes is its")
        print("extrapolation: the section 9 estimate becomes REVIVABLE BUT NOT REVIVED --")
        print("it was built on iteration counts from an unsteady 2D case and must be")
        print("re-derived before it is quoted. (This near-zero is a measured value:")
        print("the planted-zero control above passed.)")
    elif d == "REFUSED":
        print("OUTCOME P3 -- UNDECIDABLE AT THIS PRICE. The aliasing guard fired: the")
        print("achieved sampling cannot distinguish decay from aliasing. Stated as the")
        print("answer, not resolved by preference.")
    else:  # UNDECIDABLE
        print("OUTCOME P3 -- Test D read UNDECIDABLE. Stated as the answer.")
    print("=" * 78)
    return 0


# ---------------------------------------------------------------------------
def _write_log(path, endtime=80.0, dt=0.1, mon_every=2, amp=0.0,
               period=6.0, base=300.0):
    """Write a synthetic monitor log in the run's on-disk shape. No solver."""
    lines, n = [], int(round(endtime / dt))
    for i in range(n + 1):
        t = i * dt
        lines.append(f"Time = {t:.4f}")
        lines.append("  smoothSolver:  Solving for Ux, ...")
        if i % mon_every == 0:
            val = base + amp * math.sin(2 * math.pi * t / period)
            for r in range(4):
                lines.append(f"weightedAverage(rack{r}_in) of T = {val!r}")
    lines.append("End")
    open(path, "w").write("\n".join(lines))


def _selftest():
    """Known inputs in, known outputs out. Proves (a) the planted control
    recovers PLANT, (b) a blinded reader is CAUGHT, (c) the negative arm reads
    the true near-zero, (d) the imported aliasing guard still fires, (e) the
    imported gate still maps SURVIVES/DAMPS. NO SOLVER IS RUN."""
    ok = True

    def check(name, cond, extra=""):
        nonlocal ok
        ok &= bool(cond)
        print(f"  [{'OK' if cond else 'FAIL'}] {name}" + (f"   {extra}" if extra else ""))

    # imported reader/gate still see a 6.000 s oscillation
    from analyse_k2bU import dominant_period
    ts = [(i * 0.2, 300 + 0.5 * math.sin(2 * math.pi * i * 0.2 / 6.0))
          for i in range(400)]
    per = dominant_period(ts)
    check("imported dominant_period recovers the 6.000 s period",
          per is not None and abs(per - 6.0) / 6.0 < 0.15, f"got {per}")

    tmp = tempfile.mkdtemp(prefix="k2bU3R3selftest_")
    try:
        # (i) a valid, well-sampled, FLAT log -- true p2p ~0 (a DAMPS shape)
        case = os.path.join(tmp, CASE); os.makedirs(case)
        _write_log(os.path.join(case, LOGNAME), amp=0.0)
        rel = os.path.relpath(case, K_HERE)
        p_true, n_true, _ = window_p2p_via_series(rel, RXS)
        check("negative arm on a flat log reads a true near-zero p2p",
              p_true is not None and abs(p_true) <= TOL, f"p2p={p_true}")

        # (ii) the planted control FIRES: real reader recovers PLANT exactly
        pz = planted_zero_control(os.path.join(case, LOGNAME), RXS)
        check("planted control recovers PLANT through series()",
              pz["passed"] and abs(pz["recovered"] - PLANT) <= TOL,
              f"recovered={pz['recovered']:.6e}")

        # (iii) planted-FAILURE proof: a blinded reader is CAUGHT (control fails)
        pzb = planted_zero_control(os.path.join(case, LOGNAME), RXS,
                                   reader=blind_window_p2p)
        check("a blinded reader (always 0) is CAUGHT -> control REFUSES",
              (not pzb["passed"]) and pzb["recovered"] == 0.0,
              f"blind recovered={pzb['recovered']:.6e} vs PLANT={PLANT:.6e}")

        # (iv) the imported ALIASING GUARD still fires on coarse sampling
        coarse = os.path.join(tmp, "coarse"); os.makedirs(coarse)
        _write_log(os.path.join(coarse, LOGNAME), dt=0.5, mon_every=2, amp=0.5)
        v_coarse, _ = grade(os.path.relpath(coarse, K_HERE), "coarse", RXS)
        check("imported aliasing guard REFUSES coarse sampling -> P3",
              v_coarse == "REFUSED", f"verdict={v_coarse}")

        # (v) the imported GATE still maps a strong oscillation to SURVIVES
        surv = os.path.join(tmp, "surv"); os.makedirs(surv)
        _write_log(os.path.join(surv, LOGNAME), amp=0.6)
        v_surv, _ = grade(os.path.relpath(surv, K_HERE), "survives", RXS)
        check("imported gate maps a strong sustained oscillation to SURVIVES",
              v_surv == "SURVIVES", f"verdict={v_surv}")

        # (vi) the imported GATE still maps a flat series to DAMPS
        v_damp, _ = grade(rel, "damps", RXS)
        check("imported gate maps a flat (near-zero) series to DAMPS",
              v_damp == "DAMPS", f"verdict={v_damp}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n" + ("SELFTEST PASSED" if ok else "SELFTEST FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(_selftest() if "--selftest" in sys.argv else main())
