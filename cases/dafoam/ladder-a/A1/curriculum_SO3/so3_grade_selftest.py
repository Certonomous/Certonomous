#!/usr/bin/env python3
"""SO-3 COMPARATOR SELFTEST -- THE GATES SO-3 ADDS, EVERY ONE DRIVEN RED AND GREEN.

WHAT THIS FILE IS AND IS NOT.  `so3_grade.py --selftest` carries 97 inherited
units covering the gates SO-3 shares with SO-3aR2 (completion, G5J/G5C, the
plateau, the planted controls, the row-label sweep, G-STAGES, the caps).  They
run green and are NOT re-run here.  This file drives the FOUR THINGS SO-3 ADDS,
because a gate this item invented and never drove is a gate this item is
asserting:

  (g1) SECTION 9 -- the optimisation verdict, over EVERY registered branch.
       `PASS` only where the OPTIMISER printed a convergence statement against
       its OWN tolerance.  Never from the size of the improvement.
  (g2) THE COMPOSITION DIRECTION -- an endpoint FD `PASS` can never lift a
       `GATE REACHED` optimiser to `PASS`.  That is the laundering section 9
       forbids and it is driven, not promised.
  (g3) G-DESIGNPOINT -- an endpoint arm that evaluated at the BASELINE, or read
       the OTHER ROW's optimum, is refused.  Without this gate an XE/FE arm
       launched without `-xopt` is SO-3aR2's baseline number wearing SO-3's arm
       name, with every other gate green.
  (g4) THE HARNESS FLOOR and THE PROVENANCE CHAIN -- the two numbers that stop a
       reader overclaiming what the patched row supports.

EVERY LEG USES THE COMPARATOR'S OWN FIXTURE BUILDER, so the artefacts these
gates read are built by the same code the inherited suite uses and, for the X
and F records, by `so3_xf`'s own writers.  Sanaa's birth requirement,
2026-08-28, verbatim: *"A planted control must travel the real production path
-- written by the real producer's code, read through the real reader."*
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import so3_grade as G                                          # noqa: E402
import so3_stall as STALL                                      # noqa: E402

PASS = [0]
FAIL = []


def unit(name, cond):
    if cond:
        PASS[0] += 1
        print("  [OK ] %s" % name)
    else:
        FAIL.append(name)
        print("  [FAIL] %s" % name)
    return bool(cond)


def tw(**kw):
    def f(k):
        for key, val in kw.items():
            if isinstance(val, dict) and isinstance(k.get(key), dict):
                k[key].update(val)
            else:
                k[key] = val
    return f


def main():
    print("SO-3 COMPARATOR SELFTEST -- THE GATES SO-3 ADDS")
    tmp = tempfile.mkdtemp(prefix="so3_grade_selftest_")
    try:
        # =====================================================================
        print("\n(g0) THE CLEAN FIXTURE.  A converging optimiser on both rows and")
        print("     both endpoint arms at design_point=FINAL is the ONLY shape")
        print("     that can reach PASS, and it does.")
        r = G.grade(G._fix(tmp))
        unit("(g0) item PASS on a converged optimiser + endpoint FD PASS",
             r["verdict"] == "PASS")
        unit("(g0) both rows PASS", set(r["rows"].values()) == {"PASS"})
        o = r["gates"]["G-OPT9_optimisation_per_row"]
        unit("(g0) section 9 reads PASS on both rows, and says WHY",
             o["SHIPPED"]["verdict"] == "PASS" and o["PATCHED"]["verdict"] == "PASS"
             and "convergence statement" in o["PATCHED"]["why"])
        unit("(g0) and the reason is the OPTIMISER's own statement, quoted",
             o["PATCHED"]["optimiser_exit_statement"] == "Optimal Solution Found."
             and o["PATCHED"]["converged_to_optimizer_tolerance"] is True)

        # =====================================================================
        print("\n(g1) SECTION 9, BRANCH BY BRANCH.  Each is a REGISTERED state and")
        print("     each is driven.  `never PASS, and never described by the size")
        print("     of the improvement it reached`.")

        # --- the A2 shape: a real improvement, no EXIT line anywhere.
        rA2 = G.grade(G._fix(tmp, tw(opt_exit={"O-P": None, "O-S": None},
                                     opt_reduction_pct={"O-P": 28.275488,
                                                        "O-S": 28.275488},
                                     opt_majors={"O-P": 47, "O-S": 47})))
        oA2 = rA2["gates"]["G-OPT9_optimisation_per_row"]["PATCHED"]
        unit("(g1) A2's SHAPE -- 47 majors, 28.275488 %% reduction, NO EXIT line -> "
             "GATE REACHED, not PASS",
             oA2["verdict"] == "GATE REACHED"
             and oA2["convergence_statement_in_log"] is False)
        unit("(g1) and the ITEM is GATE REACHED, so the improvement cannot read as a pass",
             rA2["verdict"] == "GATE REACHED")
        unit("(g1) the 28.275488 %% is REPORTED beside the verdict, never instead of it",
             abs(oA2["weighted_drag_reduction_pct"] - 28.275488) < 1e-9)

        # --- the same shape with NO improvement: NOT A RESULT, not GATE REACHED.
        rA2b = G.grade(G._fix(tmp, tw(opt_exit={"O-P": None, "O-S": None},
                                      opt_reduction_pct={"O-P": 0.4, "O-S": 0.4},
                                      opt_majors={"O-P": 47, "O-S": 47})))
        oA2b = rA2b["gates"]["G-OPT9_optimisation_per_row"]["PATCHED"]
        unit("(g1) the SAME shape below the registered intermediate threshold "
             "(%.1f %%) -> NOT A RESULT" % G.OPT_INTERMEDIATE_THRESHOLD_PCT,
             oA2b["verdict"] == "NOT A RESULT"
             and oA2b["intermediate_threshold_met"] is False)
        unit("(g1) so GATE REACHED and NOT A RESULT are separated by a REGISTERED "
             "number, not by a judgement", rA2b["verdict"] == "NOT A RESULT")

        # --- a CAP is not a stall and is not a convergence.
        rCAP = G.grade(G._fix(tmp, tw(
            opt_exit={"O-P": "Maximum Number of Iterations Exceeded.",
                      "O-S": "Maximum Number of Iterations Exceeded."},
            opt_majors={"O-P": 50, "O-S": 50})))
        oCAP = rCAP["gates"]["G-OPT9_optimisation_per_row"]["PATCHED"]
        unit("(g1) `Maximum Number of Iterations Exceeded.` -> GATE REACHED, NOT PASS "
             "-- VERIFICATION section 4: an iteration cap is a budget, not a settle "
             "criterion", oCAP["verdict"] == "GATE REACHED")
        unit("(g1) and it is NOT read as a stall (a cap and a stall are different "
             "findings)", oCAP["stall"]["stall"] == "NO_STALL")
        unit("(g1) an EXIT line exists, so `convergence_statement_in_log` is TRUE and "
             "the verdict is still not PASS -- the string is matched against the "
             "REGISTERED converged set, not tested for truthiness",
             oCAP["convergence_statement_in_log"] is True
             and oCAP["converged_to_optimizer_tolerance"] is False)

        # --- the STALL, on C-188's own shape.
        rST = G.grade(G._fix(tmp, tw(opt_stall={"O-P": "STALL", "O-S": "STALL"},
                                     opt_marker={"O-P": True, "O-S": True},
                                     opt_exit={"O-P": None, "O-S": None},
                                     opt_majors={"O-P": 34, "O-S": 34},
                                     opt_reduction_pct={"O-P": 9.0, "O-S": 9.0})))
        oST = rST["gates"]["G-OPT9_optimisation_per_row"]["PATCHED"]
        unit("(g1) the registered STALL abort fires -> GATE REACHED (threshold met), "
             "never PASS", oST["verdict"] == "GATE REACHED")
        unit("(g1) and the stall's own evidence travels: stop_at_major, both "
             "conditions, the restoration count and the cutback count",
             oST["stall"]["stop_at_major"] == 34
             and oST["stall"]["n_restoration_majors"] == 7
             and oST["stall"]["cumulative_line_search_cutbacks"] == 547
             and oST["stall_abort_marker_present"] is True)
        rST2 = G.grade(G._fix(tmp, tw(opt_stall={"O-P": "STALL", "O-S": "STALL"},
                                      opt_marker={"O-P": True, "O-S": True},
                                      opt_exit={"O-P": None, "O-S": None},
                                      opt_majors={"O-P": 34, "O-S": 34},
                                      opt_reduction_pct={"O-P": 1.0, "O-S": 1.0})))
        unit("(g1) a stall that bought nothing -> item NOT A RESULT",
             rST2["verdict"] == "NOT A RESULT")

        # --- an unclassified EXIT line.
        rUNK = G.grade(G._fix(tmp, tw(
            opt_exit={"O-P": "Restoration Failed.", "O-S": "Restoration Failed."})))
        oUNK = rUNK["gates"]["G-OPT9_optimisation_per_row"]["PATCHED"]
        unit("(g1) an EXIT line in NEITHER registered set -> NOT A RESULT; the run is "
             "unclassified and is not a result", oUNK["verdict"] == "NOT A RESULT")

        # --- the driver's own failure flag.
        rF = G.grade(G._fix(tmp, tw(opt_fail_flag={"O-P": True, "O-S": True},
                                    opt_exit={"O-P": None, "O-S": None},
                                    opt_reduction_pct={"O-P": 8.0, "O-S": 8.0})))
        unit("(g1) pyOptSparse's own fail flag -> GATE REACHED at best",
             rF["gates"]["G-OPT9_optimisation_per_row"]["PATCHED"]["verdict"]
             == "GATE REACHED")

        # --- and the SHIPPED row alone, which is the two-row point.
        rSPLIT = G.grade(G._fix(tmp, tw(opt_exit={"O-S": None},
                                        opt_reduction_pct={"O-S": 20.0},
                                        opt_majors={"O-S": 47})))
        unit("(g1) SHIPPED GATE REACHED while PATCHED PASSES -- and the ITEM takes the "
             "WORSE of the two rows, which is what makes a two-row verdict a verdict",
             rSPLIT["rows"]["SHIPPED"] == "GATE REACHED"
             and rSPLIT["rows"]["PATCHED"] == "PASS"
             and rSPLIT["verdict"] == "GATE REACHED")

        # =====================================================================
        print("\n(g2) THE COMPOSITION DIRECTION -- THE LAUNDERING SECTION 9 FORBIDS.")
        print("     An endpoint FD PASS validates the DESIGN.  It says NOTHING about")
        print("     whether the optimiser converged, and it must never lift a")
        print("     GATE REACHED row to PASS.")
        oP = rA2["gates"]["G5J"]["PATCHED"]
        unit("(g2) the endpoint FD row PASSED on this very fixture",
             oP["endpoint_fd_verdict"] == "PASS")
        unit("(g2) the optimiser is GATE REACHED on the SAME row",
             oP["section9_optimisation"] == "GATE REACHED")
        unit("(g2) and the ROW is GATE REACHED, NOT PASS -- the endpoint PASS did not "
             "lift it", oP["row_verdict"] == "GATE REACHED")
        unit("(g2) the design change IS recorded as validated, which is the separate "
             "true statement",
             rA2["gates"]["G-OPT9_optimisation_per_row"]["PATCHED"]
                ["design_change_validated"] is True)
        unit("(g2) and the forbidden readings are enumerated in the record itself",
             any("upgrading GATE REACHED to PASS" in f for f in
                 rA2["gates"]["G-OPT9_optimisation_per_row"]["PATCHED"]
                    ["forbidden_readings"]))

        # --- THE OTHER DIRECTION: a FAILING endpoint FD under a CONVERGED optimiser.
        rEF = G.grade(G._fix(tmp, tw(err={"PATCHED": {0: 40.0, 3: 40.0}})))
        oEF = rEF["gates"]["G5J"]["PATCHED"]
        unit("(g2) a CONVERGED optimiser whose endpoint FD GATE FAILs -> the row is "
             "GATE FAIL, so a converged run cannot carry an unverified design",
             oEF["section9_optimisation"] == "PASS"
             and oEF["endpoint_fd_verdict"] == "GATE FAIL"
             and oEF["row_verdict"] == "GATE FAIL")
        unit("(g2) and the record says IN TERMS that the design change is NOT validated, "
             "with the IDWarp reason",
             rEF["gates"]["G-OPT9_optimisation_per_row"]["PATCHED"]
                ["design_change_validated"] is False
             and "iteration 0 is not verified at the optimum"
                 in rEF["gates"]["G-OPT9_optimisation_per_row"]["PATCHED"]
                       ["design_change_note"])

        # =====================================================================
        print("\n(g3) G-DESIGNPOINT.  An XE/FE arm launched without -xopt produces a")
        print("     VALID artefact that is SO-3aR2's BASELINE number wearing SO-3's")
        print("     arm name.  Every other gate would stay green.")
        rBL = G.grade(G._fix(tmp, tw(design_point={"XE-P": "BASELINE"})))
        unit("(g3) RED: an endpoint arm at design_point=BASELINE -> G-DESIGNPOINT "
             "GATE FAIL",
             rBL["gates"]["G-DESIGNPOINT_endpoint_arms_evaluated_at_the_optimum"]
                ["verdict"] == "GATE FAIL")
        unit("(g3) the failing artefact is NAMED",
             "X:PATCHED" in rBL["gates"]
                ["G-DESIGNPOINT_endpoint_arms_evaluated_at_the_optimum"]["failing"])
        unit("(g3) and the ITEM is GATE FAIL -- section 9's requirement is unmet and "
             "the item says so", rBL["verdict"] == "GATE FAIL")

        rUN = G.grade(G._fix(tmp, tw(design_point={"FE-S": None})))
        unit("(g3) RED: the producer's FAIL-CLOSED default `UNSPECIFIED` also refuses "
             "-- a builder that defaulted to BASELINE would have let this through",
             rUN["gates"]["G-DESIGNPOINT_endpoint_arms_evaluated_at_the_optimum"]
                ["verdict"] == "GATE FAIL"
             and rUN["gates"]["G-DESIGNPOINT_endpoint_arms_evaluated_at_the_optimum"]
                    ["per_artefact"]["F:SHIPPED"]["design_point"] == "UNSPECIFIED")

        rXR = G.grade(G._fix(tmp, tw(xopt_row={"XE-P": "SHIPPED"})))
        unit("(g3) RED: an endpoint arm on the PATCHED row that read the SHIPPED "
             "optimum -> GATE FAIL.  A patched gradient at a shipped design is a "
             "number about neither toolchain",
             rXR["gates"]["G-DESIGNPOINT_endpoint_arms_evaluated_at_the_optimum"]
                ["verdict"] == "GATE FAIL")
        unit("(g3) GREEN: with every endpoint arm at FINAL and on its own row, the "
             "gate PASSES -- so the three reds above are readings of the artefacts "
             "and not of a gate that always fails",
             r["gates"]["G-DESIGNPOINT_endpoint_arms_evaluated_at_the_optimum"]
              ["verdict"] == "PASS")

        # =====================================================================
        print("\n(g4) THE HARNESS FLOOR AND THE PROVENANCE CHAIN -- the two numbers")
        print("     that stop a reader overclaiming what the PATCHED row supports.")
        fm = r["gates"]["G5J"]["PATCHED"]["G5J_harness_floor"]
        unit("(g4) every aggregate publishes its margin to the harness floor",
             "margin_to_floor_lower_edge_pct_points" in fm
             and fm["provenance"] == "VERIFICATION_CHARTER.md section 7 step 4")
        unit("(g4) and it is REPORTED, NEVER GATED -- turning a caveat into a GATE "
             "FAIL is a threshold the charter does not authorise",
             fm["gated"] is False)
        # SO-3aR2's OWN NUMBER, driven through this function.
        so3ar2 = G.floor_margin(2.6779490823450605)
        unit("(g4) SO-3aR2's PATCHED aggregate 2.678 %% is labelled "
             "INSIDE_HARNESS_FLOOR_INTERVAL -- it passes essentially ON the floor",
             so3ar2["status"].startswith("INSIDE_HARNESS_FLOOR_INTERVAL")
             and abs(so3ar2["margin_to_floor_lower_edge_pct_points"] - 0.177949) < 1e-6)
        unit("(g4) a reading BELOW 2.5 %% is labelled a claim about the HARNESS",
             G.floor_margin(0.1)["status"].startswith("BELOW_HARNESS_FLOOR"))
        unit("(g4) and a reading above 5 %% is labelled resolvable",
             G.floor_margin(7.0)["status"].startswith("ABOVE_HARNESS_FLOOR"))

        prov = r["upstream_provenance"]
        unit("(g4) the provenance is a CHAIN of at least two links",
             len(prov["upstream"]["chain"]) >= 2)
        unit("(g4) EVERY link is GATE FAIL at item level and GATE FAIL on SHIPPED",
             all(l["item_verdict"] == "GATE FAIL"
                 and l["rows"]["SHIPPED"] == "GATE FAIL"
                 for l in prov["upstream"]["chain"]))
        unit("(g4) the chain names SO-3aR2 first (DIRECT) and SO-1a second "
             "(INHERITED)",
             prov["upstream"]["chain"][0]["item"] == "CURRICULUM-SO3aR2"
             and prov["upstream"]["chain"][1]["item"] == "CURRICULUM-SO1a")
        unit("(g4) and the composed line forbids the unqualified sentence in so many "
             "words",
             "NEVER `DAFoam reduces weighted drag by X`"
             in prov["upstream"]["verdict_line"])
        unit("(g4) SO-3aR2's own endpoint gap is carried, not quietly inherited",
             "iteration 0 is NOT verified at iteration"
             in prov["upstream"]["chain"][0]["patched_detail"]["endpoint_gap"])

        # --- RED: drop a link, and the gate must refuse.
        saved = list(G.UPSTREAM_CHAIN)
        try:
            G.UPSTREAM["chain"] = saved[:1]
            refused = False
            try:
                G.require_travelling_provenance()
            except G.Refusal as exc:
                refused = "upstream_chain_absent_or_shorter_than_two_links" in str(exc)
            unit("(g4) RED: dropping SO-1a from the chain REFUSES -- a rename that "
                 "repointed the head would have lost a GATE FAIL while every other "
                 "clause stayed green", refused)
            G.UPSTREAM["chain"] = [dict(saved[0], item_verdict="PASS"), saved[1]]
            refused2 = False
            try:
                G.require_travelling_provenance()
            except G.Refusal as exc:
                refused2 = "chain_link_item_verdict_not_GATE_FAIL" in str(exc)
            unit("(g4) RED: a link whose item verdict is upgraded to PASS REFUSES -- "
                 "this is the laundering direction and it is checked per link",
                 refused2)
        finally:
            G.UPSTREAM["chain"] = saved
        unit("(g4) GREEN again once the chain is restored",
             G.require_travelling_provenance()["verdict"] == "SATISFIED")

        # =====================================================================
        print("\n(g5) THE CAPS AND THE STALL BRANCH -- rule 12's estimate-versus-actual")
        print("     needs the PREDICTION, and a cap is not a prediction.")
        unit("(g5) the registered ceiling IS the sum of the registered caps",
             abs(G.ITEM_CEILING_CORE_MIN - sum(G.CAPS.values())) < 1e-9)
        unit("(g5) MESH's cap (%.1f) and prediction (%.2f) are DIFFERENT numbers"
             % (G.CAPS["MESH"], G.PREDICTED_CORE_MIN["MESH"]),
             G.CAPS["MESH"] != G.PREDICTED_CORE_MIN["MESH"])
        unit("(g5) the O-arm prediction is C-24 x 3 x C-188's 1.6308 correction over "
             "50 majors = 103.0 core-min",
             abs(G.PREDICTED_CORE_MIN["O-S"] - 103.0) < 1e-9)
        unit("(g5) and a STALL branch is registered, as C-188 demands of its "
             "successors", "O-S" in G.PREDICTED_STALL_CORE_MIN
             and G.PREDICTED_STALL_CORE_MIN["O-S"] < G.PREDICTED_CORE_MIN["O-S"])
        unit("(g5) every arm's cap can carry the C-188 margin (a cap that cannot is "
             "unrunnable and the launcher refuses it)",
             all(c * 60.0 / G.ARM_RANKS[a] - 180 >= 60 for a, c in G.CAPS.items()))

        # =====================================================================
        print("\n(g6) THE STALL DETECTOR THE GRADER GATES ON IS THE ONE THE WATCHDOG")
        print("     RAN.  One number, one file.")
        unit("(g6) the comparator imports the shared detector rather than "
             "reimplementing it", G.STALL is STALL)
        unit("(g6) and publishes its registered constants beside the verdict",
             ("%d consecutive majors" % STALL.N_STALL)
             in r["gates"]["G-OPT9_optimisation_per_row"]
                 ["stall_conditions_registered"]["A"])
        unit("(g6) condition B's calibration is published as NOT EXERCISED on real "
             "evidence, never as a passing control",
             "NEVER fired on real evidence"
             in r["gates"]["G-OPT9_optimisation_per_row"]
                 ["stall_conditions_registered"]["calibration"])

        # =====================================================================
        print("\n(g7) THE VOCABULARY.  Every verdict this comparator can emit is one")
        print("     of rule 1's six tokens, on every branch driven above.")
        allr = [r, rA2, rA2b, rCAP, rST, rST2, rUNK, rF, rSPLIT, rBL, rUN, rXR, rEF]
        unit("(g7) %d graded fixtures, every item verdict in the frozen vocabulary"
             % len(allr), all(x["verdict"] in G.VOCAB for x in allr))
        unit("(g7) every ROW verdict too",
             all(v in G.VOCAB for x in allr for v in x["rows"].values()))
        unit("(g7) every section 9 verdict too",
             all(x["gates"]["G-OPT9_optimisation_per_row"][w]["verdict"] in G.VOCAB
                 for x in allr for w in G.ROWS))
        seen = sorted({x["verdict"] for x in allr})
        unit("(g7) and the suite REACHED more than one item verdict (%r) -- a suite "
             "that only ever sees PASS has not driven a gate" % (seen,),
             len(seen) >= 3)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\nDRIVE %d checks, %d fail" % (PASS[0] + len(FAIL), len(FAIL)))
    for f in FAIL:
        print("  FAIL: %s" % f)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
