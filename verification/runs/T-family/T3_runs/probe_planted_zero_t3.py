#!/usr/bin/env python3
"""EVIDENCE — the T3 planted-zero control's arithmetic, measured on all four cases.

Written 2026-09-03 by a heat-transfer `lab-lane` while triaging the refusal at
`verification/runs/T-family/T3_runs/T3_R_FF_GRADE_OUTPUT_20260830T224307Z.txt`.

THIS SCRIPT GRADES NOTHING.  It imports the frozen `analyse_t3.py` read-only and
calls that module's OWN `planted_zero_control`, then decomposes the arithmetic
the control performs.  It writes nothing into any case tree: the control copies
the last two checkpoints to a temp directory and plants there, and this probe's
own decomposition reads from a second temp copy.  No file under `R_c/`, `R_m/`,
`R_f/` or `R_ff/` is opened for writing.

WHAT IT ESTABLISHES, and the numbers it returned on 2026-09-03:

  The refusing predicate is `analyse_t3.py:327`

      return dict(passed=(seen >= PLANT - 1e-15), planted=PLANT,

  with `PLANT = 1.234e-03` K (`analyse_t3.py:81`) applied to a field of ~300 K,
  where one ULP of 300.0 is 6.661e-14 K.  The predicate therefore demands the
  reader recover the plant to 1e-15 ABSOLUTE -- about 1/66th of one ULP of its
  own operands -- and cannot be met by construction whenever the true field is
  still drifting at the planted cell in the subtracting direction.

    case   drift at planted cell   reader saw      shortfall    passed
    R_c    -2.27e-13              2.4684 K        --           True  (VACUOUS)
    R_m     exactly 0.0           1.2340000000e-3 -1.1e-14     True
    R_f    -3.98e-13              1.2339999996e-3 +3.87e-13    False
    R_ff   -3.41e-13              1.2339999997e-3 +3.30e-13    False

  TWO DEFECTS, AND THE SECOND IS THE DANGEROUS ONE:

  (1) FAILS CLOSED.  A sub-ULP absolute tolerance always refuses eventually.
      R_m passed by the accident of an exactly-zero drift, not by design.

  (2) FAILS OPEN -- R_c.  There `seen` is a real 2.47 K change at a DIFFERENT
      cell, so the predicate returned True while the plant was never the argmax.
      A control that can pass without seeing its own plant certifies nothing.

  THE READER IS NOT BLIND, and that must be said first because a refusing
  planted-zero control normally means the instrument is broken.  On R_f the
  reader saw the plant at 251x the un-planted signal (4.910e-06 K) and flipped
  CONVERGED -> NOT_CONVERGED.  The instrument passed its own test and the
  arithmetic of the test threw the result away.

PRIOR OBSERVATION, CREDITED: commit 93bf8c24 already recorded this ("that
control is decided by the sign of a seven-ULP wiggle and convergence cannot win
it").  This lane re-derived it independently from the artifacts; the numbers
reproduce.  It is not presented as a novel discovery.

Run from this directory:  python3 probe_planted_zero_t3.py
"""
import os, re, shutil, sys, tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import analyse_t3 as A  # frozen comparator -- imported read-only, never edited


def main():
    print("PLANT = %r K   (analyse_t3.py:81)" % A.PLANT)
    print("pass criterion, analyse_t3.py:327 -> seen >= PLANT - 1e-15")
    print("ULP(300.0 K) = %r\n" % (300.0 * 2.0 ** -52))

    for case in ("R_c", "R_m", "R_f", "R_ff"):
        d = os.path.join(ROOT, case)
        if not os.path.isdir(d):
            print("%-5s ABSENT" % case)
            continue

        # the frozen module's OWN control, unmodified
        pz = A.planted_zero_control(d)
        seen = pz.get("reader_max_change")
        deficit = None if seen is None else A.PLANT - seen
        print("%-5s passed=%s state=%s" % (case, pz.get("passed"), pz.get("reader_state")))
        print("      reader_max_change = %r" % seen)
        print("      shortfall vs PLANT = %r" % deficit)

        # decomposition: what the control's arithmetic is actually made of
        ts = sorted((x for x in os.listdir(d)
                     if re.fullmatch(r"\d+(\.\d+)?", x) and float(x) > 0), key=float)
        if len(ts) < 2:
            print()
            continue
        tmp = tempfile.mkdtemp(prefix="probe_pz_")
        try:
            work = os.path.join(tmp, case)
            for t in ts[-2:]:
                os.makedirs(os.path.join(work, t))
                shutil.copy(os.path.join(d, t, "T"), os.path.join(work, t, "T"))
            a = A.T1C.read_internal(os.path.join(work, ts[-2], "T"))
            b = A.T1C.read_internal(os.path.join(work, ts[-1], "T"))
            c0 = A.T1C.iterative_convergence(work)      # un-planted baseline
            print("      checkpoints %s -> %s   nCells(T) = %d" % (ts[-2], ts[-1], len(a)))
            print("      UNPLANTED baseline: state=%s max_change=%r"
                  % (c0.get("state"), c0.get("max_change")))
            print("      drift at planted cell (cell 0): %r" % (a[0] - b[0]))
            print("      plant + drift = %r" % ((a[0] + A.PLANT) - b[0]))
            unplanted = c0.get("max_change") or 0.0
            if unplanted > 0 and seen:
                print("      plant/unplanted signal ratio = %.2fx" % (seen / unplanted))
            if seen and abs(seen - A.PLANT) > 1e-9:
                print("      NOTE: the plant was NOT the argmax -- a pass here is VACUOUS")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        print()


if __name__ == "__main__":
    main()
