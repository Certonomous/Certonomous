#!/usr/bin/env python3
"""MRF R2 -- WINDOW-LENGTH SENSITIVITY OF THE PLATEAU STATISTIC.

WHAT THIS IS, AND WHAT IT IS NOT.
  It is a DIAGNOSTIC. It computes NO gate verdict, alters NO threshold, and cannot
  change the verdict of the frozen grader grade_triple_r2.py (blob
  b3758cc5427b12bec76f8c23b2188276401a1db8). Rule 2: after first compute the gates
  are closed. This is a caveat that TRAVELS WITH the triple, never one that moves it.

THE HAZARD IT MEASURES. MONITOR_STANDARD S12, as implemented at
cases/navier_class/MRF/measure_states_mrf.py:80-95, picks ONE window length:

    w = min(max(n // 4, 20), 2000)

and reports the drift across that one window's two halves. A drift read at ONE window
length is a single sample of a quantity that can depend strongly on the window. Measured
on a sibling case on 2026-09-11, the SAME series at the SAME instant read +0.787 %
over 10 iterations, +0.047 % over 20 and +7.039 % over 30 -- three window lengths
disagreeing by a factor of ~150. A two-point plateau test once called a
-10.02 %/100-iteration drift plateaued.

  => "PLATEAUED" from a single window length is not a plateau. It is one reading.

THE AXIS THIS ADDS. The frozen grader ALREADY varies the STOPPING POINT (41 points over
a 600-iteration span) and reports that spread. That is a different axis: it asks "where
did I stop?". This asks "how long was my ruler?". Both can be wrong independently, and
the grader measures only the first.

RULE 3. Its own planted control, on each level's OWN moment.dat, copied to a tempdir --
never writing into any case directory, and never into the LIVE fine run.
"""
import importlib.util, os, shutil, sys, tempfile

# BASE IS THE ET8000 FAMILY, NOT THE R2 ROOT. R2/coarse and R2/medium are the
# SUPERSEDED endTime=4000 runs; the GRADED triple is ET8000/{coarse,medium,fine}.
# This script pointed at the R2 root on its first run and diagnosed the wrong two
# levels. Taken from the frozen grader's own BASE/LEVELS (grade_triple_r2.py:44-46)
# rather than retyped, so the two cannot drift apart.
BASE = "/home/ubuntu/Certonomous/verification/runs/navier_class/MRF/R2/ET8000"
CASE = "/home/ubuntu/Certonomous/cases/navier_class/MRF"
LEVELS = [("coarse", "coarse"), ("medium", "medium"), ("fine", "fine")]
WINDOWS = [100, 200, 400, 800, 1600, 2000, 3200]


def load(nm, p):
    s = importlib.util.spec_from_file_location(nm, p)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


msm = load("msm", f"{CASE}/measure_states_mrf.py")


def drift_at(series, w):
    """S12's drift/monotone arithmetic, verbatim, but at an IMPOSED window length."""
    if len(series) < w or w < 4:
        return None
    win = series[-w:]
    half = w // 2
    m1 = sum(win[:half]) / half
    m2 = sum(win[half:]) / len(win[half:])
    mag = abs(sum(win) / len(win))
    drift = (m2 - m1) / mag if mag > 0 else float("inf")
    steps = [win[i + 1] - win[i] for i in range(len(win) - 1)]
    sign = 1.0 if drift >= 0 else -1.0
    mono = sum(1 for s in steps if s * sign > 0) / len(steps)
    return drift, mono, sum(win) / len(win), (abs(drift) >= 1e-3 and mono >= 0.90)


def plant_ok(mom):
    td = tempfile.mkdtemp(prefix="wsens_")
    try:
        pl = os.path.join(td, "m.dat"); shutil.copy(mom, pl)
        L = open(pl).read().splitlines()
        for i, ln in enumerate(L):
            if not ln.startswith("#"):
                tk = ln.replace("(", " ").replace(")", " ").split()
                L[i] = f"{tk[0]}\t({tk[1]} {tk[2]} {msm.PLANT:.12g})\t(0 0 0)\t(0 0 0)"
                break
        open(pl, "w").write("\n".join(L) + "\n")
        _, pv = msm.read_total_axial(pl)
        return abs(pv[0] - msm.PLANT) <= 1e-12
    finally:
        shutil.rmtree(td, True)


def main():
    print("MRF R2 -- WINDOW-LENGTH SENSITIVITY OF THE S12 PLATEAU DRIFT")
    print("DIAGNOSTIC ONLY. No gate. No threshold. Cannot move the frozen grader's verdict.")
    print(f"S12's own choice is w = min(max(n//4,20),2000); limb |drift| >= 1e-3 AND monotone >= 0.90\n")
    any_level = False
    for name, rel in LEVELS:
        mom = os.path.join(BASE, rel, "postProcessing/impellerForces/0/moment.dat")
        if not os.path.exists(mom):
            print(f"{name:7s}: moment.dat ABSENT -> PENDING: {mom}\n"); continue
        if not plant_ok(mom):
            print(f"{name:7s}: NOT A RESULT -- the reader failed its plant on this level's "
                  f"own moment.dat; a zero from it would not be evidence.\n"); continue
        t, mz = msm.read_total_axial(mom)
        ser = [msm.power_number(q) for q in mz]
        n = len(ser)
        w_s12 = min(max(n // 4, 20), 2000)
        d_s12 = drift_at(ser, w_s12)
        any_level = True
        print(f"{name:7s}  [rule 3] plant PASS   n={n}  last t={t[-1]:g}")
        print(f"         S12's OWN window w={w_s12}: drift {d_s12[0]:+.6e}  monotone {d_s12[1]:.4f}"
              f"  -> {'NOT_PLATEAUED' if d_s12[3] else 'PLATEAUED'}")
        print(f"         {'w':>6} {'drift':>15} {'monotone':>9} {'Np window mean':>16} {'limb':>14}")
        ds = []
        for w in WINDOWS:
            r = drift_at(ser, w)
            if r is None:
                print(f"         {w:6d} {'series too short':>15}"); continue
            ds.append(r[0])
            print(f"         {w:6d} {r[0]:+15.6e} {r[1]:9.4f} {r[2]:16.6f} "
                  f"{'NOT_PLATEAUED' if r[3] else 'PLATEAUED':>14}")
        if len(ds) >= 2:
            lo, hi = min(ds), max(ds)
            amin = min(abs(x) for x in ds); amax = max(abs(x) for x in ds)
            ratio = (amax / amin) if amin > 0 else float("inf")
            signs = len(set(x >= 0 for x in ds))
            print(f"         SPREAD ACROSS WINDOW LENGTHS: drift range {hi-lo:.6e}"
                  f"  |drift| min {amin:.6e} max {amax:.6e}  ratio {ratio:.1f}x"
                  f"  sign changes: {'YES' if signs > 1 else 'no'}")
            over = sum(1 for x in ds if abs(x) >= 1e-3)
            print(f"         windows over the 1e-3 drift limb: {over}/{len(ds)}")
        print()
    if not any_level:
        print("No level could be read. NOT A RESULT is not reportable from this script; "
              "it computes no verdict.")
        return 2
    print("READING: where the window-length ratio is large or the sign changes, "
          "'PLATEAUED' at S12's single window is ONE READING, not a plateau.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
