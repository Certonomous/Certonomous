"""R7 GATE CONTROL -- rule 3 applied to a VERDICT rather than to a zero.

A NOT A RESULT emitted by a gate never shown able to emit a PASS is not
evidence: it is indistinguishable from a gate hard-wired to refuse.  This
control drives the PRODUCTION gate_order -- the function the comparator calls
at analyse_t23g2.py, not a copy of it (VERIFICATION_CHARTER.md section 2p.7
limb (d): "a test that exercises a redundant copy of the guarded logic tests
nothing") -- over four inputs and requires four different answers.

IT GRADES NOTHING.  It reads no field, opens no case, and writes no verdict
into any record.
"""
import os
import sys

sys.path.insert(0, "/home/ubuntu/Certonomous/docs/campaigns/T-family")
import analyse_t23g2 as A
import roache_triple as RT

BASE = dict(quantity="Q4",
            orders=[0.5980, 0.6111],
            states=["CONVERGING", "CONVERGING"],
            iterative_convergence={"T23G2_L1": "CONVERGED",
                                   "T23G2_L2": "NOT CONVERGED",
                                   "T23G2_L3": "CONVERGED"},
            plateau={"T23G2_L1": "PLATEAUED",
                     "T23G2_L2": "PLATEAUED",
                     "T23G2_L3": "PLATEAUED"})


def row(**over):
    r = {k: (dict(v) if isinstance(v, dict) else list(v))
         for k, v in BASE.items() if k != "quantity"}
    r["quantity"] = "Q4"
    r.update(over)
    return r


def drive(label, r, expect):
    print("-" * 74)
    print("CONTROL %s -- expect %s" % (label, expect))
    try:
        got = A.gate_order({"Q4": r})
    except RT.Refusal as e:
        got = "REFUSED: %s" % e
    ok = (got == expect) if expect != "REFUSAL" else got.startswith("REFUSED")
    print("  GOT: %s" % got)
    print("  %s" % ("CONTROL PASSED" if ok else "CONTROL FAILED"))
    return ok


ok = []
# (1) the T23G2 case as it actually stands: L2 not iteratively converged.
ok.append(drive("1  AS-MEASURED (T23G2_L2 NOT CONVERGED)", row(),
                "NOT A RESULT"))
# (2) THE PLANT.  Same order, same triple state, every level CONVERGED and
#     PLATEAUED.  The gate MUST emit PASS here or it is stuck, and a stuck
#     gate's NOT A RESULT proves nothing.
ok.append(drive("2  PLANT -- all levels CONVERGED/PLATEAUED",
                row(iterative_convergence={lv: "CONVERGED" for lv in
                                           ("T23G2_L1", "T23G2_L2",
                                            "T23G2_L3")}),
                "PASS"))
# (3) THE SECOND PLANT.  Band still registered, order moved OUTSIDE it.  The
#     gate MUST emit GATE FAIL -- it is not collapsed onto two answers.
ok.append(drive("3  PLANT -- converged, order 2.9000 OUTSIDE [0.5, 1.5]",
                row(orders=[0.5980, 2.9000],
                    iterative_convergence={lv: "CONVERGED" for lv in
                                           ("T23G2_L1", "T23G2_L2",
                                            "T23G2_L3")}),
                "GATE FAIL"))
# (4) plateau limb alone -- iterative all CONVERGED, one level not PLATEAUED.
ok.append(drive("4  plateau limb alone (L3 NOT PLATEAUED)",
                row(iterative_convergence={lv: "CONVERGED" for lv in
                                           ("T23G2_L1", "T23G2_L2",
                                            "T23G2_L3")},
                    plateau={"T23G2_L1": "PLATEAUED",
                             "T23G2_L2": "PLATEAUED",
                             "T23G2_L3": "NOT PLATEAUED"}),
                "NOT A RESULT"))
# (5) states never supplied -- step (a) unevaluable -> REFUSAL, mirroring
#     grade_ladder:609-612.
ok.append(drive("5  iterative states ABSENT", row(iterative_convergence=None),
                "REFUSAL"))
print("-" * 74)
print("R7 GATE CONTROL: %d/%d passed" % (sum(ok), len(ok)))
sys.exit(0 if all(ok) else 1)
