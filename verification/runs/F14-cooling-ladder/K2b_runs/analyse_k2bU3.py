#!/usr/bin/env python3
"""analyse_k2bU3.py -- grade K2b-U3 against the thresholds fixed in
K2b_3D_UNSTEADINESS_PREREGISTRATION.md (sha256 91a26fc9...).

    python3 analyse_k2bU3.py

Nothing here is chosen after the fact. The gate, the aliasing floors, the
windows and the three outcomes all come from that file.
"""
import math, os, re, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PERIOD_2D = 6.000            # the 2D limit cycle this is testing for
DISCARD, WIN = 40.0, 20.0    # pre-registered: discard 40 s, grade 60-80 vs 40-60
P_SURV, P_DAMP, R_SURV, R_DAMP = 0.30, 0.10, 0.8, 0.5
MIN_STEPS_PER_PERIOD, MIN_SAMPLES_PER_PERIOD = 20, 10
sys.path.insert(0, HERE)
from analyse_k2bU import dominant_period            # validated by --selftest


def series(case, rxs):
    """(time, value) for the first matching monitor, plus per-rack series."""
    p = os.path.join(HERE, case, "log.buoyantBoussinesqPimpleFoam")
    txt = open(p, errors="replace").read()
    times = [float(x) for x in re.findall(r'^Time = ([0-9.eE+-]+)', txt, re.M)]
    per = {}
    cur = None
    for line in txt.split("\n"):
        m = re.match(r'^Time = ([0-9.eE+-]+)\s*$', line)
        if m:
            cur = float(m.group(1)); continue
        for rx in rxs:
            mm = re.search(rx, line)
            if mm and cur is not None:
                per.setdefault(rx, []).append((cur, float(mm.group(1))))
    return times, per


def grade(case, label, rxs):
    times, per = series(case, rxs)
    if not times:
        print(f"  {label}: no log"); return None, None
    tmax = times[-1]
    dt = tmax / len(times)
    steps_per = PERIOD_2D / dt
    # combine the per-rack series into the graded quantity (mean over racks)
    keys = [k for k in rxs if k in per]
    if not keys:
        print(f"  {label}: no monitor samples"); return None, None
    n = min(len(per[k]) for k in keys)
    ts = [(per[keys[0]][i][0],
           statistics.fmean(per[k][i][1] for k in keys)) for i in range(n)]
    samp_dt = (ts[-1][0] - ts[0][0]) / (len(ts) - 1) if len(ts) > 1 else float("inf")
    samples_per = PERIOD_2D / samp_dt
    print(f"  {label}: {len(times)} steps to t={tmax:.2f} s, mean dt {dt:.4f} s, "
          f"{len(keys)} monitored face(s)")
    print(f"    ALIASING GUARD  steps/period {steps_per:.1f} (floor {MIN_STEPS_PER_PERIOD})"
          f"   samples/period {samples_per:.1f} (floor {MIN_SAMPLES_PER_PERIOD})")
    if steps_per < MIN_STEPS_PER_PERIOD or samples_per < MIN_SAMPLES_PER_PERIOD:
        print(f"    ==> REFUSED: cannot distinguish decay from aliasing at this "
              f"sampling. Outcome P3.")
        return "REFUSED", None
    if tmax < DISCARD + 2 * WIN:
        print(f"    ==> UNGRADED: needs {DISCARD + 2*WIN:.0f} s, reached {tmax:.2f} s")
        return None, None
    fin = [(a, b) for a, b in ts if DISCARD + WIN < a <= DISCARD + 2 * WIN]
    pre = [(a, b) for a, b in ts if DISCARD < a <= DISCARD + WIN]
    Bv = max(b for _, b in fin) - min(b for _, b in fin)
    Pv = max(b for _, b in pre) - min(b for _, b in pre)
    ratio = Bv / Pv if Pv else float("inf")
    v = ("SURVIVES" if (Bv >= P_SURV and ratio >= R_SURV) else
         "DAMPS" if (Bv <= P_DAMP or ratio <= R_DAMP) else "UNDECIDABLE")
    print(f"    final {DISCARD+WIN:.0f}-{DISCARD+2*WIN:.0f} s: p2p {Bv:.4f} K "
          f"(mean {statistics.fmean([b for _,b in fin]):.4f} K)")
    print(f"    preceding {DISCARD:.0f}-{DISCARD+WIN:.0f} s: p2p {Pv:.4f} K   "
          f"ratio {ratio:.3f}")
    per_ = dominant_period([(a, b) for a, b in ts if a > DISCARD])
    print(f"    dominant period after the discard: "
          f"{'none extracted' if per_ is None else f'{per_:.3f} s'}"
          f"   (2D limit cycle was {PERIOD_2D:.3f} s)")
    print(f"    ==> {label} SAYS: {v}")
    return v, per_


def main():
    print("=" * 78)
    print("K2b-U3  DOES THE 2D LIMIT CYCLE SURVIVE IN 3D?")
    print("graded against K2b_3D_UNSTEADINESS_PREREGISTRATION.md sha256 91a26fc9...")
    print(f"thresholds: p2p >= {P_SURV} K and ratio >= {R_SURV} = SURVIVES;"
          f"  p2p <= {P_DAMP} K or ratio <= {R_DAMP} = DAMPS")
    print("=" * 78)
    print("\nGATE -- Control M: the 2D slice at the 3D test's own 100 mm cell.")
    print("  Does the 6.000 s limit cycle survive COARSENING ALONE?")
    m, mper = grade("K2bU3_M", "Control M (2D, h=0.1)",
                    [r'weightedAverage\(rack_in\) of T = ([-0-9.eE+]+)'])
    if m is None:
        print("\n  gate not yet gradeable"); return 0
    if m != "SURVIVES":
        print(f"\n{'='*78}\nOUTCOME P3 -- UNDECIDABLE AT THIS PRICE.")
        print("The gate FAILED: the limit cycle does not survive coarsening to 100 mm")
        print("in 2D, so a 3D run at 100 mm cannot separate three-dimensionality from")
        print("mesh resolution. Test D is NOT run and no 3D verdict is claimed.")
        print("The un-confounded experiment is a 3D transient at the spec's own 60 mm")
        print("coarse mesh, 80 s: ~42 core-minutes at the measured transient rate.")
        print("=" * 78)
        return 0
    print("\n  gate PASSES -- mesh resolution is excluded; Test D's answer is about")
    print("  dimensionality.\n")
    print("TEST D -- the full 3D module, N=4 racks, OPEN row ends.")
    d, dper = grade("K2bU3_D", "Test D (3D, h=0.1)",
                    [rf'weightedAverage\(rack{r}_in\) of T = ([-0-9.eE+]+)'
                     for r in range(4)])
    print("\n" + "=" * 78)
    if d == "SURVIVES":
        print("OUTCOME P1 -- IT SURVIVES IN 3D. O1's consequence carries: the module")
        print("needs a transient formulation and the section 9 estimate stays VOID.")
    elif d == "DAMPS":
        print("OUTCOME P2 -- IT DAMPS IN 3D. Three-dimensionality damps the mode.")
        print("The 2D finding STANDS as true of the 2D slice -- it is not retracted,")
        print("and the three failures it explained were all measured on 2D cases.")
        print("What changes is its extrapolation: the section 9 estimate becomes")
        print("REVIVABLE BUT NOT REVIVED -- it was built on iteration counts taken")
        print("from an unsteady 2D case and must be re-derived before it is quoted.")
    elif d == "REFUSED" or d is None:
        print("OUTCOME P3 -- UNDECIDABLE AT THIS PRICE. Stated as the answer.")
    else:
        print("OUTCOME P3 -- Test D read UNDECIDABLE. Stated as the answer.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
