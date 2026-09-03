#!/usr/bin/env python3
"""§2p.3(e) POSITIVE CONTROL AND MUTATION DEMONSTRATION for T3c's repaired
rule-3 predicate P-2.

VERIFICATION_CHARTER.md §2d.11.1 condition 3 requires BOTH limbs through the
PRODUCTION path (§2p.3(d)), not a copy: the repaired predicate must STILL REFUSE
something, and must STILL PASS a case constructed to deserve it.  §2p.3(e) adds
that a repair which refuses everything is indistinguishable, from its verdicts
alone, from a correct one.

EVERYTHING BELOW DRIVES `analyse_t3c.planted_zero_control_p2` BY IMPORT.  No
predicate is re-implemented here; if the shipped function changes, these results
change with it, which is the entire point.  Nothing is written into any run tree.

THE MUST-FAIL PLANT IS `R_c`, THE REAL CASE.  Under the frozen predicate it
PASSED VACUOUSLY -- a 2.4684 K change at a cell that never carried the plant,
clearing a 1.234e-03 K plant by ~2000x without seeing it.  Under P-2 it must now
REFUSE on LIMB A.  If it still passes, the repair did not land.

Clear __pycache__ before running: stale bytecode inverts mutation tests.
Exit 0 all controls behaved, 1 a control did not.
"""
import math, os, shutil, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyse_t3 as A          # noqa: E402
import analyse_t3c as T         # noqa: E402  -- the PRODUCTION module under test

FAILS = []


def check(label, ok, detail=""):
    print("  [%s] %s %s" % ("ok" if ok else "FAIL", label, detail))
    if not ok:
        FAILS.append(label)


def head(t):
    print("\n=== %s ===" % t)


def main():
    print("production module : %s" % T.__file__)
    print("predicate         : P-2, N_ULP = %d" % T.N_ULP)
    print("PLANT             : %r K (from the frozen analyse_t3.py)" % A.PLANT)

    # ---------------------------------------------------------------- limb 1
    head("LIMB 1 -- MUST PASS: real cases where the reader genuinely sees its plant")
    for case in ("R_m", "R_f", "R_ff"):
        d = os.path.join(HERE, case)
        if not os.path.isdir(d):
            check("%s present" % case, False, "case directory absent")
            continue
        pz = T.planted_zero_control_p2(d)
        check("%-4s PASSES" % case, pz["passed"] is True,
              "limb_A=%s (resid %.2f ulp)  limb_B=%s (err %.2f ulp)  drift %+.2f ulp"
              % (pz["limb_A"], pz["limb_A_residual_ulp"], pz["limb_B"],
                 pz["limb_B_error_ulp"], pz["drift_ulp"]))

    # ---------------------------------------------------------------- limb 2
    head("LIMB 2 -- MUST FAIL: R_c, the real case the frozen predicate passed vacuously")
    d = os.path.join(HERE, "R_c")
    pz = T.planted_zero_control_p2(d)
    check("R_c REFUSES under P-2", pz["passed"] is False,
          "limb_A=%s limb_B=%s  reader max %.6f K vs planted cell %.9f K"
          % (pz["limb_A"], pz["limb_B"], pz["reader_max_change"], pz["planted_cell_change"]))
    # STATED HONESTLY, BECAUSE THE MUTATION ARM BELOW MEASURED IT: R_c is refused
    # by BOTH limbs, and LIMB B ALONE WOULD SUFFICE -- its max is 2000x the plant,
    # far outside a 32 ulp window.  So R_c does NOT demonstrate that LIMB A does
    # any work.  The arm that does is S-9 / M1 below, with a decoy cell.
    check("R_c is refused by BOTH limbs (so it does not isolate LIMB A)",
          pz["limb_A"] is False and pz["limb_B"] is False,
          "the reader's max is %.0fx the plant" % (pz["reader_max_change"] / A.PLANT))
    frozen = A.planted_zero_control(d)
    check("and the FROZEN predicate passed this same case (the defect, reproduced)",
          frozen.get("passed") is True, "frozen passed=%r" % frozen.get("passed"))

    # ---------------------------------------------------------------- limb 3
    head("LIMB 3 -- MUST FAIL: a BLIND reader, driven through the production function")
    real = T.READER
    for case, baseline in (("R_f", 4.910338816443982e-06), ("R_m", 7.875202072682441e-07)):
        try:
            T.READER = lambda w, _b=baseline: dict(max_change=_b, state="CONVERGED")
            pz = T.planted_zero_control_p2(os.path.join(HERE, case))
            check("blind reader on %-4s REFUSES" % case, pz["passed"] is False,
                  "short by %.2fx" % (A.PLANT / baseline))
        finally:
            T.READER = real

    head("LIMB 4 -- MUST FAIL: an OVER-REPORTING reader (2*PLANT + rec)")
    try:
        T.READER = lambda w: dict(max_change=2 * A.PLANT + 4.910338816443982e-06,
                                  state="NOT_CONVERGED")
        pz = T.planted_zero_control_p2(os.path.join(HERE, "R_f"))
        check("over-reporting reader REFUSES", pz["passed"] is False,
              "err %.3e ulp" % pz["limb_B_error_ulp"])
    finally:
        T.READER = real

    # ---------------------------------------------------------------- mutation
    head("MUTATION -- the controls must DIE when the shipped predicate is broken")

    # M1: disable LIMB A (the identity limb).  The S-9 DECOY case must then wrongly
    # pass.  R_c is NOT used here: it is refused by LIMB B alone, so mutating LIMB A
    # would not change its verdict and the mutation would look survivable when it is
    # not.  This lane's first M1 used R_c and the control caught the error.
    src = open(T.__file__).read()
    mutated = src.replace("limb_A = (got_max == cell_diff)",
                          "limb_A = True  # MUTANT: identity limb disabled")
    check("M1 mutation is a real edit (the target line exists)", mutated != src)
    tmp = tempfile.mkdtemp(prefix="t3c_mut_")
    try:
        for f in ("analyse_t3.py", "analyse_t3_rff.py"):
            p = os.path.join(HERE, f)
            if os.path.isfile(p):
                shutil.copy(p, os.path.join(tmp, f))
        for extra in ("T3_secondary_digitisation.json", "gate_t3.json",
                      "T3_reference_primary.json"):
            p = os.path.join(HERE, extra)
            if os.path.isfile(p):
                shutil.copy(p, os.path.join(tmp, extra))
        mp = os.path.join(tmp, "analyse_t3c_mutant.py")
        open(mp, "w").write(mutated)
        for junk in ("__pycache__",):
            shutil.rmtree(os.path.join(tmp, junk), ignore_errors=True)
        sys.path.insert(0, tmp)
        import importlib.util
        spec = importlib.util.spec_from_file_location("analyse_t3c_mutant", mp)
        mut = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mut)
        decoy = mut.write_case(os.path.join(tmp, "decoy"), decoy_cell=7,
                               decoy_change=A.PLANT + 20.0 * math.ulp(300.0))
        pz_mut = mut.planted_zero_control_p2(decoy)
        pz_ship = T.planted_zero_control_p2(decoy)
        check("M1 SHIPPED module REFUSES the decoy case", pz_ship["passed"] is False,
              "limb_A=%s limb_B=%s" % (pz_ship["limb_A"], pz_ship["limb_B"]))
        check("M1 MUTANT (identity limb disabled) WRONGLY PASSES it -> mutation killed",
              pz_mut["passed"] is True,
              "mutant passed=%r while the shipped module refuses the identical case"
              % pz_mut["passed"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        if tmp in sys.path:
            sys.path.remove(tmp)

    # M2: widen N_ULP past the frozen S-2 ceiling.  +200 ulp must then wrongly pass.
    real_n = T.N_ULP
    try:
        T.N_ULP = 256                      # MUTANT: above the frozen +200 refusal arm
        t2 = tempfile.mkdtemp(prefix="t3c_mut2_")
        try:
            pz = T.planted_zero_control_p2(T.write_case(os.path.join(t2, "c"),
                                                        drift_ulp=200.0))
            check("M2 with N_ULP widened to 256, +200 ulp WRONGLY PASSES -> S-2 kills it",
                  pz["passed"] is True, "err %.2f ulp" % pz["limb_B_error_ulp"])
        finally:
            shutil.rmtree(t2, ignore_errors=True)
    finally:
        T.N_ULP = real_n
    t3 = tempfile.mkdtemp(prefix="t3c_mut3_")
    try:
        pz = T.planted_zero_control_p2(T.write_case(os.path.join(t3, "c"), drift_ulp=200.0))
        check("N_ULP restored to %d, +200 ulp REFUSES again" % T.N_ULP, pz["passed"] is False,
              "err %.2f ulp" % pz["limb_B_error_ulp"])
    finally:
        shutil.rmtree(t3, ignore_errors=True)

    print("\nCONTROL %s (%d did not behave)" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 0 if not FAILS else 1


if __name__ == "__main__":
    sys.exit(main())
