#!/usr/bin/env python
"""D6R2C ADDENDUM 1 -- the x0 guard driven against a REAL pyoptsparse history.

WHY THIS FILE EXISTS. The original guard's controls were built on SYNTHETIC
dictionaries and never touched a real history. That is exactly why a unit
mismatch survived to launch and cost KR_RES (rc=73, 21 s). This driver reads
the actual artefacts on disk -- KR_KILL/OptView.hst, 1,077,248 bytes, and
KR_KILL/d6r2c_x0.json -- and drives the repaired comparison in BOTH directions.

It grades nothing and gates nothing. It is a control.

Run inside the registered image:
  python d6r2c_x0_guard_selftest.py --base /mnt
"""
import os
import sys
import json
import argparse
import numpy as np

PLANT = 1.234e-03
X0_MATCH_TOL = 1.0e-12
X0_INFORMATIVE_FLOOR = 6
# The registered scalers, used ONLY to reproduce the historical defect and to
# stand in for OpenMDAO's metadata in this offline driver. The guard itself
# reads them from prob.model.get_design_vars(), never from a copy like this.
SCALERS = {"twist": 0.1, "shape": 10.0,
           "patchV_cl04": 0.1, "patchV_cl05": 0.1, "patchV_cl06": 0.1}


def compare(ref, got, floor=X0_INFORMATIVE_FLOOR, tol=X0_MATCH_TOL, plant=None):
    """The repaired comparison, in the history's own (driver-scaled) space.
    Returns (verdict, worst_abs_diff, informative, total)."""
    worst = 0.0
    informative = 0
    total = 0
    for k, v in ref.items():
        cand = [n for n in got if n == k or n.endswith("." + k) or n.split(".")[-1] == k]
        if not cand:
            return "REFUSE_NO_MATCH", None, informative, total
        g = np.asarray(got[cand[0]], dtype=float).flatten().copy()
        r = np.asarray(v, dtype=float).flatten()
        if g.size != r.size:
            return "REFUSE_SIZE", None, informative, total
        if plant is not None and k == plant[0]:
            g[plant[1]] += PLANT
        informative += int(np.count_nonzero((g != 0.0) | (r != 0.0)))
        total += int(r.size)
        if r.size:
            worst = max(worst, float(np.max(np.abs(g - r))))
    if informative < floor:
        return "REFUSE_BLIND", worst, informative, total
    if worst > tol:
        return "REFUSE_MISMATCH", worst, informative, total
    return "PASS", worst, informative, total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="/mnt")
    ap.add_argument("--arm", default="KR_KILL")
    a = ap.parse_args()

    hst = os.path.join(a.base, a.arm, "OptView.hst")
    x0f = os.path.join(a.base, a.arm, "d6r2c_x0.json")
    for p in (hst, x0f):
        if not os.path.exists(p):
            print("D6R2C_X0_SELFTEST REFUSE: %s does not exist. This driver reads REAL artefacts "
                  "and will not fall back to synthetic ones -- that fallback is the defect it exists "
                  "to prevent." % p)
            return 2

    from pyoptsparse.pyOpt_history import History
    h = History(hst, temp=False, flag="r")
    got = h.getValues(names=h.getDVNames(), callCounters=[0], major=False, allowSens=True)
    h.close()
    blob = json.load(open(x0f))
    phys = blob["dv"]
    scaled = blob.get("dv_driver_scaled") or {
        k: [float(x) * SCALERS.get(k, 1.0) for x in np.asarray(v, dtype=float).flatten()]
        for k, v in phys.items()}

    print("D6R2C_X0_SELFTEST -- driven on REAL artefacts")
    print("  history : %s (%d bytes)" % (hst, os.path.getsize(hst)))
    print("  x0      : %s%s" % (x0f, "" if blob.get("dv_driver_scaled") else
                                "  [pre-ADDENDUM-1 file: physical only, converted here]"))
    print("  history DV names: %s" % sorted(got))
    print()
    fails = []

    def chk(tag, want, **kw):
        v, w, inf, tot = compare(**kw)
        ok = (v == want)
        print("  %-64s -> %-16s worst=%-11s inf=%s/%s %s"
              % (tag, v, ("%.3e" % w) if w is not None else "n/a", inf, tot,
                 "OK" if ok else "*** DID NOT FIRE ***"))
        if not ok:
            fails.append(tag)

    print(" A. the repaired comparison, correct space, must PASS on the real history")
    chk("A1 driver-scaled ref vs history call-0", "PASS", ref=scaled, got=got)

    print(" B. THE HISTORICAL DEFECT, reproduced exactly on the real artefacts")
    chk("B1 PHYSICAL ref vs history (the rc=73 bug) must REFUSE", "REFUSE_MISMATCH",
        ref=phys, got=got)
    v, w, _, _ = compare(ref=phys, got=got)
    exp = 90.0
    ok = abs(w - exp) < 1e-9
    print("     reproduces worst_abs_diff = %.6f (expected exactly %.1f = 100.0 - 100.0*0.1) %s"
          % (w, exp, "OK" if ok else "*** VALUE DID NOT REPRODUCE ***"))
    if not ok:
        fails.append("B1-value")

    print(" C. planted disagreements in the CORRECT space must REFUSE")
    for k, i in (("patchV_cl04", 1), ("patchV_cl05", 0), ("twist", 0), ("shape", 0)):
        chk("C/%s[%d] planted %.3e" % (k, i, PLANT), "REFUSE_MISMATCH",
            ref=scaled, got=got, plant=(k, i))

    print(" D. THE BLINDNESS CONTROL -- the repair this addendum exists for")
    zero_ref = {k: [0.0] * len(np.asarray(v).flatten()) for k, v in scaled.items()}
    zero_got = {k: np.zeros(len(np.asarray(v).flatten())) for k, v in got.items()}
    chk("D1 an all-zero design vector must REFUSE as BLIND, never PASS", "REFUSE_BLIND",
        ref=zero_ref, got=zero_got)
    only_shape = {k: v for k, v in scaled.items() if k in ("shape", "twist")}
    chk("D2 shape+twist only (103 zero components) must REFUSE as BLIND", "REFUSE_BLIND",
        ref=only_shape, got=got)
    print("     ^ these two are the whole point: under the ORIGINAL guard both would have PASSED,")
    print("       because zero times any scaler is zero and 103 of 109 components are zero at x0.")

    print(" E. floor boundary")
    chk("E1 floor of exactly 6 with 6 informative must PASS", "PASS",
        ref=scaled, got=got, floor=6)
    chk("E2 floor of 7 with 6 informative must REFUSE", "REFUSE_BLIND",
        ref=scaled, got=got, floor=7)

    print()
    if fails:
        print("D6R2C_X0_SELFTEST FAIL -- %d control(s): %s" % (len(fails), fails))
        return 1
    print("D6R2C_X0_SELFTEST PASS -- 11 controls on REAL artefacts, both directions, "
          "including the historical defect reproduced to the exact 90.0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
