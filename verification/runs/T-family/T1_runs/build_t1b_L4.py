#!/usr/bin/env python3
"""
T1b fourth grid level ("x"): build ONLY the four wall-refined cases R_*_x.

Registered in docs/campaigns/T-family/T1b_L4_AMENDMENT.md (2026-08-21) before
any of these cases existed.  Approved by Sanaa on 2026-08-21: the T1b fourth
grid level (wall-refined) runs under the T1b design with the comparator
amended to gate on the triple state; the frozen originals are left untouched.

WHAT THIS FILE DOES NOT DO.  It does not copy build_t1b.py's grading, mesh,
dictionary or CASE.txt code.  It imports the frozen builder and calls its
build() with the new level, so the reciprocal radial grading that attempt 1
got wrong (L-142), every dictionary and the CASE.txt layout are identical in
form to the twelve R_* cases already solved.  The only levers are:

  * the level:   x = (205 radial, 1024 axial, first-cell-centre y+ 0.390625)
                 i.e. 1.6x the fine level's 128 x 640 in each direction
                 (205 = round(128 * 1.6); 1024 = 640 * 1.6), target y+ =
                 0.625 / 1.6.  Effective refinement ratio from the counts:
                 205/128 = 1.6016 radially, 1024/640 = 1.6000 axially,
                 sqrt(209920/81920) = 1.6008 on cell count.
  * endTime:     per case, from the amendment (20000 at Re 1e4; 80000 at
                 3e4, 1e5, 3e5), applied by setting the frozen builder's
                 END_TIME module global for the duration of the build() call,
                 exactly as build_d_ts.py sets B.RE.  writeInterval stays at
                 the builder's 2000 and purgeWrite at its 2.

It never touches an existing case: a case directory that already holds a
numeric time directory, a 0/ directory or a LAUNCH_LOCK is reported and left
alone, and the twelve R_*_{c,m,f} cases are not in its list at all.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_t1b as T1B                                # noqa: E402

LEVEL_X = (205, 1024, T1B.RESOLVED["f"][2] / 1.6)      # (nr, nx, y+ centre)
END_TIME_X = {"10k": 20000, "30k": 80000, "100k": 80000, "300k": 80000}
CASES_X = [f"R_{t}_x" for t in ("10k", "30k", "100k", "300k")]


def occupied(name):
    d = os.path.join(HERE, name)
    if not os.path.isdir(d):
        return None
    why = []
    for n in os.listdir(d):
        if n == "0" or n == "LAUNCH_LOCK":
            why.append(n)
        elif n.replace(".", "", 1).isdigit() and float(n) != 0.0:
            why.append(n)
    return why or None


def main():
    nr, nx, yp = LEVEL_X
    made = []
    for tag, Re in T1B.RE_SWEEP.items():
        name = f"R_{tag}_x"
        occ = occupied(name)
        if occ:
            print(f"  {name}: NOT rebuilt, holds {', '.join(sorted(occ))}")
            continue
        old = T1B.END_TIME
        T1B.END_TIME = END_TIME_X[tag]
        try:
            m = T1B.build(name, Re, nr, nx, yp, False, T1B.PRT_DEFAULT, False)
        finally:
            T1B.END_TIME = old
        with open(os.path.join(HERE, name, "CASE.txt"), "a") as fh:
            fh.write(
                "level             x (fourth level, wall-refined)\n"
                "ladder_for        R_%s_{m,f,x} under T1b_L4_AMENDMENT.md; "
                "R_%s_{c,m,f} as frozen\n"
                "refinement_ratio  radial %.4f, axial %.4f, cell-count sqrt "
                "%.4f (gci uses 1.6)\n"
                "built_by          build_t1b_L4.py calling build_t1b.build() "
                "with END_TIME set to %d for this call\n"
                % (tag, tag, nr / 128.0, nx / 640.0,
                   (nr * nx / 81920.0) ** 0.5, END_TIME_X[tag]))
        m["endTime"] = END_TIME_X[tag]
        made.append(m)

    print(f"T1b L4: {len(made)} x-level cases built in {HERE}")
    print(f"  {'case':10s} {'Re':>8s} {'cells':>7s} {'y+':>8s} "
          f"{'first cell':>12s} {'ratio':>9s} {'expansion':>10s} {'endTime':>8s}")
    for m in made:
        print(f"  {m['name']:10s} {m['Re']:8.0f} {m['cells']:7d} {m['yplus']:8.6f} "
              f"{m['first']:12.6e} {m['ratio']:9.6f} "
              f"{m['ratio'] ** (nr - 1):10.4f} {m['endTime']:8d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
