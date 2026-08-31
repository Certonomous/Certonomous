#!/usr/bin/env python3
"""F28 -- THE ABSOLUTE ARBITER: thrust stationarity over the last 2000 iterations.

Registration section 8 table: |dT_total| < 0.1 % over the last 2000 iterations.
Operationally, matching the precedent in the registration's own 2026-08-31
Addendum item 2 and frozen in the BC probe's PRECOMMITTED_READINGS.md section 3:

    ptp% = ( max(Fx) - min(Fx) ) / |mean(Fx)| * 100

over the FINAL 2000 iterations of postProcessing/forcesDuct/0/force.dat,
column `total_x`.  Invariant to the sign convention and to WEDGE_SCALE = 72,
both pure scalar multipliers.

THIS IS NOT A GRADER.  It reads a FEASIBILITY run and issues no verdict of the
fixed vocabulary.  It selects among the three readings that were committed
BEFORE any probe number existed, and it may not be given a fourth.

READER VALIDATION, standing rule 3, run with --validate: the reader is required
to REPRODUCE THE REGISTRATION'S OWN PUBLISHED FIGURE for the dp=1000 baseline
(min -0.356179, max -0.295725, mean -0.333725, ptp 18.1149 %) and to be shown
able to move -- a planted perturbation of one sample must change the answer.
A reader not shown able to read a different number is not a reader.

Usage:  read_ptp_f28.py <case_dir> [--window 2000]
        read_ptp_f28.py --validate <baseline_case_dir>
"""
import os
import sys

WINDOW = 2000
# The registration's own published dp=1000 baseline, quoted in
# PRECOMMITTED_READINGS.md section 3 and used here as the reader's control.
REF = {"min": -0.356179, "max": -0.295725, "mean": -0.333725, "ptp": 18.1149}

# The three readings, committed before any probe number existed.  NOT EDITABLE
# HERE: this table is a transcription of PRECOMMITTED_READINGS.md section 4.
BASELINE_PTP = 18.1149
THRESHOLD = 0.1
TENFOLD = 1.81  # = 18.1149 / 10, fixed in the frozen file


def read_total_x(case_dir):
    """Return [(time, total_x), ...] from forcesDuct/0/force.dat."""
    path = os.path.join(case_dir, "postProcessing", "forcesDuct", "0", "force.dat")
    if not os.path.isfile(path):
        raise SystemExit("REFUSE: no force.dat at %s" % path)
    rows = []
    for ln in open(path):
        if ln.startswith("#") or not ln.strip():
            continue
        f = ln.split()
        # Time  total_x total_y total_z  pressure_x ...
        rows.append((int(float(f[0])), float(f[1])))
    if not rows:
        raise SystemExit("REFUSE: force.dat at %s has no data rows" % path)
    return rows


def ptp_percent(rows, window=WINDOW):
    if len(rows) < window:
        raise SystemExit("REFUSE: only %d rows, need %d for the registered "
                         "window -- a short window is not the registered "
                         "criterion" % (len(rows), window))
    w = [v for _, v in rows[-window:]]
    lo, hi, mean = min(w), max(w), sum(w) / len(w)
    if mean == 0.0:
        raise SystemExit("REFUSE: mean Fx is exactly zero; the percentage "
                         "normalisation is undefined")
    return lo, hi, mean, (hi - lo) / abs(mean) * 100.0, rows[-window][0], rows[-1][0]


def select_reading(ptp):
    """The three pre-committed readings. No fourth may be added here."""
    if ptp < THRESHOLD:
        return ("A", "HYPOTHESIS CONFIRMED -- the registered absolute criterion "
                     "is MET; the free outer mass flux was the cause of the stall")
    if ptp < TENFOLD:
        return ("B", "HYPOTHESIS SUPPORTED, NOT SUFFICIENT -- a >=10x reduction; "
                     "the farfield is a major contributor but does not account "
                     "for the whole stall")
    return ("C", "HYPOTHESIS FALSIFIED -- less than a 10x reduction; the "
                 "farfield is EXONERATED as the leading cause, exactly as the "
                 "axis columns were")


def validate(baseline_dir):
    print("READER VALIDATION -- reproduce the registration's published figure, "
          "then be shown able to move.")
    rows = read_total_x(baseline_dir)
    lo, hi, mean, ptp, t0, t1 = ptp_percent(rows)
    ok = True
    for name, got, want, tol in (("min", lo, REF["min"], 5e-6),
                                 ("max", hi, REF["max"], 5e-6),
                                 ("mean", mean, REF["mean"], 5e-6),
                                 ("ptp%", ptp, REF["ptp"], 5e-4)):
        good = abs(got - want) <= tol
        ok = ok and good
        print("  %-5s published %-12s  reader %.6f   %s"
              % (name, want, got, "AGREES" if good else "*** DISAGREES ***"))
    print("  window iterations %d..%d (%d samples)" % (t0, t1, WINDOW))
    # PLANT: a reader that cannot see a change is not reading.
    planted = list(rows)
    planted[-1] = (planted[-1][0], planted[-1][1] * 2.0)
    _, _, _, pptp, _, _ = ptp_percent(planted)
    moved = abs(pptp - ptp) > 1e-6
    print("  PLANT (last sample doubled): ptp%% %.4f -> %.4f  %s"
          % (ptp, pptp, "READER MOVED as required" if moved else "*** BLIND ***"))
    ok = ok and moved
    print("VALIDATION %s" % ("rc 0" if ok else "FAILED"))
    return 0 if ok else 2


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--validate":
        sys.exit(validate(args[1]))
    if not args:
        raise SystemExit(__doc__)
    case = args[0]
    win = WINDOW
    if "--window" in args:
        win = int(args[args.index("--window") + 1])
    rows = read_total_x(case)
    lo, hi, mean, ptp, t0, t1 = ptp_percent(rows, win)
    tag, meaning = select_reading(ptp)
    print("case            %s" % case)
    print("window          iterations %d..%d (%d samples)" % (t0, t1, win))
    print("total_x  min    %.9f" % lo)
    print("total_x  max    %.9f" % hi)
    print("total_x  mean   %.9f" % mean)
    print("ptp%%            %.4f %%   (registered threshold %.1f %%)" % (ptp, THRESHOLD))
    print("baseline        %.4f %%   ratio probe/baseline = %.4f"
          % (BASELINE_PTP, ptp / BASELINE_PTP))
    print("PRE-COMMITTED READING %s: %s" % (tag, meaning))
    print("FEASIBILITY -- no verdict of the fixed vocabulary attaches to this.")
