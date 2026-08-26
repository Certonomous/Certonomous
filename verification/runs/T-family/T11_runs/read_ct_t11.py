#!/usr/bin/env python3
"""T11 control C-T reader (AMENDMENT 2). Prints G1 theta_mean for T11_PW_f and
T11_PW_f_CT through the FROZEN production reader analyse_t11.read_theta and
reports |dG1| against the registered band (1e-4 relative, prereg S6.1/S11 P3).
Writes NO verdict and NO json. Exit 2 = refuse."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyse_t11 as A          # frozen comparator, blob ca391ddf
import exact_t11 as EX

def g1(case):
    d = os.path.join(HERE, case)
    t = A.latest_time(d)
    if t is None:
        A.refuse("%s has no time directory beyond 0" % case)
    ok, worst, why = A.time_integration_ok(d)
    if not ok:
        A.refuse("%s: %s" % (case, why))
    pr = A.read_theta(d, t)
    if pr is None:
        A.refuse("could not read T for %s" % case)
    return t, len(pr[1]), worst, A.theta_mean_of(pr)

def main():
    if "--selftest" in sys.argv:          # planted arm: the band arithmetic sees a non-zero
        ref = 0.85
        if abs(((ref + 1.234e-3) - ref) / (ref * A.BAND_REL) - 1.234e-3 / (0.85e-4)) > 1e-9:
            print("SELFTEST FAIL"); return 1
        print("SELFTEST PASS"); return 0
    meta = A.level_meta("T11_PW_f")
    Fo = float(meta["Fo_end"]); ref = EX.theta_mean(Fo, A.BI)
    tf, nf, wf, gf = g1("T11_PW_f")
    tc, nc, wc, gc = g1("T11_PW_f_CT")
    d = gc - gf
    print("G1 T11_PW_f    t=%s n=%d worst_resid=%.3e theta_mean=%.12f" % (tf, nf, wf, gf))
    print("G1 T11_PW_f_CT t=%s n=%d worst_resid=%.3e theta_mean=%.12f" % (tc, nc, wc, gc))
    print("dG1 = %+.6e  |dG1|/ref = %.6e  band(rel) = %.1e  |dG1|/band = %.4f  (P3 registered: < 0.10)"
          % (d, abs(d) / ref, A.BAND_REL, abs(d) / (ref * A.BAND_REL)))
    print("exact theta_mean(Fo=%.3f, Bi=%g) = %.12f ; rel dev f=%+.3e f_CT=%+.3e"
          % (Fo, A.BI, ref, (gf - ref) / ref, (gc - ref) / ref))
    return 0

if __name__ == "__main__":
    sys.exit(main())
