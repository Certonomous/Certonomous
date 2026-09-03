"""R8 GATE POSITIVE CONTROL -- VERIFICATION_CHARTER.md section 2p.3(e).

RULED AT COMMIT c4007e42, v1.42 section 2p.8: "EVERY RESTRICTIVE REPAIR CARRIES A
POSITIVE CONTROL.  It is not enough to show the gate now refuses what it should
refuse; the same run must show it STILL PASSES WHAT IT SHOULD PASS, driven through
the PRODUCTION path over a planted input constructed to deserve a pass.  A repair
that refuses everything is 'restrictive' in the trivial sense and is
indistinguishable, from its verdicts alone, from a correct one."

THIS DRIVES THE PRODUCTION `g_ratio` BY IMPORT -- the function the comparator
itself calls at analyse_t23g2.py, never a copy and never a reimplementation
(section 2p.7 limb (d): "a test that exercises a redundant copy of the guarded
logic tests nothing").

IT GRADES NOTHING.  It opens no case, reads no field, writes no verdict into any
record, and launches no solver.

NEGATIVE PLANTS ARE MANDATORY HERE AND ARE CONTROLS 2 AND 3.  Control 2 must come
back PASS and control 3 must come back GATE FAIL, over the SAME numerator, so the
only thing separating them is RATIO_MIN.  That is what shows the registered band
is still live and still discriminating after R8 -- a gate that refuses everything
would fail both.
"""
import hashlib
import os
import sys

# THE PATH IS RESOLVED, PRINTED AND FINGERPRINTED, so a reader of this control's
# output never has to take limb (d) on trust.  PRODUCTION is the default and is
# what every recorded run of this control uses; the override exists ONLY so the
# mutation demonstration (r8_mutation_demo_t23g2.py) can point the SAME suite at
# a deliberately broken copy and require it to go RED.  A control that cannot be
# shown to fail is not a control.
PRODUCTION = "/home/ubuntu/Certonomous/docs/campaigns/T-family"
CMP_DIR = os.environ.get("T23G2_CMP_DIR", PRODUCTION)

sys.path.insert(0, CMP_DIR)
import analyse_t23g2 as A                                      # noqa: E402
import roache_triple as RT                                     # noqa: E402

_LOADED = os.path.realpath(A.__file__)
_SHA = hashlib.sha256(open(_LOADED, "rb").read()).hexdigest()
print("=" * 74)
print("R8 GATE POSITIVE CONTROL -- VERIFICATION_CHARTER.md section 2p.3(e)")
print("  driving g_ratio from : %s" % _LOADED)
print("  sha256 of that file  : %s" % _SHA)
print("  PRODUCTION PATH?     : %s"
      % ("YES" if os.path.dirname(_LOADED) == PRODUCTION
         else "NO -- MUTATION DEMONSTRATION, this run is EXPECTED to go red"))
print("=" * 74)

LV = ("T23G2_L1", "T23G2_L2", "T23G2_L3")
ALL_CONVERGED = {lv: "CONVERGED" for lv in LV}
ALL_PLATEAUED = {lv: "PLATEAUED" for lv in LV}
AS_MEASURED_IT = {"T23G2_L1": "CONVERGED", "T23G2_L2": "NOT CONVERGED",
                  "T23G2_L3": "CONVERGED"}

# A planted-zero control that PASSES, so R5's refusal is not what is being
# exercised except where a control deliberately withholds it (control 7).
GOOD_CONTROL = dict(reader="control-harness", artifact="none",
                    planted=RT.PLANT, reader_delta=RT.PLANT, passed=True)

# The T23G2 Q4 numerator, kept fixed across controls 2 and 3 so that RATIO_MIN is
# the ONLY thing that separates their verdicts.
DIFFS = [0.6664925, 0.7000000]          # smallest |difference| = 0.6664925
PASS_ITER = 1.0e-03                     # ratio 666.5  -> >= RATIO_MIN -> PASS
FAIL_ITER = 2.0e-01                     # ratio   3.3  ->  < RATIO_MIN -> GATE FAIL


def drive(label, expect, expect_limbs=None, expect_msg=None, **kw):
    """expect_limbs: the R8 limb numbers required to appear in `grounds`, or
    None to not check.  Checking it is what stops the two grounds collapsing
    into one indistinguishable refusal.

    expect_msg: a substring the REFUSAL text must contain.  Added after the
    mutation demonstration measured a blind spot in this very suite -- see
    control 9."""
    kw.setdefault("control", GOOD_CONTROL)
    kw.setdefault("iterative_states", ALL_CONVERGED)
    kw.setdefault("plateau_states", ALL_PLATEAUED)
    kw.setdefault("level_diffs", DIFFS)
    print("-" * 74)
    print("CONTROL %s" % label)
    print("  expect %s%s" % (expect, "" if expect_limbs is None
                             else "  limbs %s" % (expect_limbs,)))
    limbs = None
    try:
        got, ratio, smallest, grounds = A.g_ratio(
            kw.pop("name", "Q4"), kw.pop("iter_change"),
            kw.pop("level_diffs"), control=kw.pop("control"),
            iterative_states=kw.pop("iterative_states"),
            plateau_states=kw.pop("plateau_states"))
        limbs = sorted(n for n in (1, 2)
                       if any(("R8 LIMB %d" % n) in g for g in grounds))
        print("  GOT: %s   ratio %s   smallest %.7f   limbs %s"
              % (got, ratio, smallest, limbs))
    except RT.Refusal as e:
        msg = str(e)
        got = "REFUSED: %s" % msg[:60]
        print("  GOT: %s" % got)
        if expect_msg is not None:
            print("  refusal text contains %r : %s"
                  % (expect_msg, expect_msg in msg))
            if expect_msg not in msg:
                got = "REFUSED BY THE WRONG LINE"
    ok = got.startswith("REFUSED:") if expect == "REFUSAL" else (got == expect)
    if ok and expect_limbs is not None:
        ok = (limbs == expect_limbs)
    print("  %s" % ("CONTROL PASSED" if ok else "CONTROL FAILED"))
    return ok


ok = []

# (1) THE T23G2 CASE AS IT ACTUALLY STANDS.  L2 not iteratively converged AND the
#     iterative change exactly 0.0 -- BOTH ruled grounds hold, and BOTH must be
#     reported, because "either alone is sufficient" is only checkable if the
#     instrument does not collapse them.
ok.append(drive("1  AS-MEASURED (T23G2_L2 NOT CONVERGED, iter_change 0.0)",
                "NOT A RESULT", [1, 2],
                iter_change=0.0, iterative_states=AS_MEASURED_IT))

# (2) THE POSITIVE PLANT -- section 2p.3(e)'s requirement.  Everything converged
#     and plateaued, a REAL non-zero iterative change, ratio comfortably above
#     RATIO_MIN.  The gate MUST emit PASS here, or R8 disabled it rather than
#     restricting it and control 1's NOT A RESULT proves nothing.
ok.append(drive("2  POSITIVE PLANT -- all CONVERGED/PLATEAUED, ratio 666.5",
                "PASS", [], iter_change=PASS_ITER))

# (3) THE NEGATIVE PLANT -- SAME numerator, iterative change large enough that
#     the ratio falls BELOW RATIO_MIN.  The gate MUST emit GATE FAIL.  Together
#     with (2) this shows RATIO_MIN = 10.0 is still live and still
#     discriminating: R8 did not widen it, narrow it or retire it.
ok.append(drive("3  NEGATIVE PLANT -- all CONVERGED, ratio 3.3 BELOW RATIO_MIN",
                "GATE FAIL", [], iter_change=FAIL_ITER))

# (4) LIMB 2 ALONE.  Every level converged and plateaued -- limb 1 cannot fire --
#     but the iterative change is exactly 0.0.  This is the ground the petition
#     did not raise, isolated: the numerator is never consulted.
ok.append(drive("4  LIMB 2 ALONE -- all CONVERGED, iter_change EXACTLY 0.0",
                "NOT A RESULT", [2], iter_change=0.0))

# (5) LIMB 1 ALONE, ITERATIVE.  A non-zero iterative change that WOULD have
#     passed (same input as control 2), with one level not converged.
ok.append(drive("5  LIMB 1 ALONE -- L2 NOT CONVERGED, ratio 666.5",
                "NOT A RESULT", [1],
                iter_change=PASS_ITER, iterative_states=AS_MEASURED_IT))

# (6) LIMB 1 ALONE, PLATEAU.  The plateau half of step (a), which the T23G2 data
#     never reaches on its own.
ok.append(drive("6  LIMB 1 ALONE -- L3 NOT PLATEAUED, ratio 666.5",
                "NOT A RESULT", [1], iter_change=PASS_ITER,
                plateau_states={"T23G2_L1": "PLATEAUED",
                                "T23G2_L2": "PLATEAUED",
                                "T23G2_L3": "NOT PLATEAUED"}))

# (7) STEP (a) UNEVALUABLE -- iterative states never supplied.  Mirrors
#     roache_triple.grade_ladder:609-612, exactly as R7 did for gate_order.
ok.append(drive("7  iterative states ABSENT -> refusal", "REFUSAL",
                None, iter_change=PASS_ITER, iterative_states=None))

# (8) R5 IS NOT WEAKENED BY R8.  An exact zero with NO planted-zero control still
#     REFUSES (exit 2), and is not quietly downgraded to a NOT A RESULT by a
#     later limb that would have voided the cell anyway.
ok.append(drive("8  exact zero, NO planted-zero control -> R5 refusal STILL",
                "REFUSAL", None, iter_change=0.0, control=None))

# (9) A BLIND SPOT THIS SUITE MEASURED IN ITSELF, AND THEN CLOSED.  The FIRST
#     mutation demonstration removed g_ratio's own `control is None` refusal and
#     the suite SURVIVED it, 5 of 6, because roache_triple.assert_plant_control
#     refuses on the same input one line later.  Control 8 above cannot tell the
#     two refusals apart; it sees only that something refused.  R5's registered
#     feature is g_ratio's OWN explicit refusal -- the registered mutation set's
#     D4 exists precisely to ask whether the second line of defence is real --
#     so this control requires the refusal to come from THAT line, by its text.
#     Recorded here rather than quietly folded into control 8, because a suite
#     that was shown its own blind spot and closed it is better evidence than
#     one that never looked.
ok.append(drive("9  the SAME input, and the refusal must come from g_ratio's "
                "OWN line",
                "REFUSAL", None, iter_change=0.0, control=None,
                expect_msg="EXACT ZERO iterative change"))

print("-" * 74)
print("R8 GATE CONTROL: %d/%d passed" % (sum(ok), len(ok)))
print("  control 2 is the section 2p.3(e) POSITIVE control: the repaired gate "
      "still PASSES what it should pass.")
print("  control 3 is its NEGATIVE plant over the SAME numerator: RATIO_MIN = "
      "%.0f is still live and still discriminating." % A.RATIO_MIN)
sys.exit(0 if all(ok) else 1)
