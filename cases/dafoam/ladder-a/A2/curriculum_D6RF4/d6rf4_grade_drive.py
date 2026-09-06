#!/usr/bin/env python3
"""Curriculum D6RF4 -- THE END-TO-END DRIVE OF `d6rf4_grade.py`, on a SYNTHETIC
run root, at ZERO SOLVER CORE-MINUTES.

WHAT THIS IS AND IS NOT.  It is a TOOL, not an instrument: `d6rf4_grade.py`
neither imports nor executes it, it is not in `FROZEN_PATHS`, and NO NUMBER IT
PRODUCES IS A RESULT ABOUT THE A2 WING.  Every value below is a fixture the
author chose, and the only thing the drive establishes is that the grading path
RUNS END TO END and that its gates move in the registered directions when the
fixture moves.  A drive on a fixture is not a verdict, and this file says so
rather than letting a reader infer otherwise.

WHY IT EXISTS ANYWAY.  `D6RF3` was frozen, launched and dead 31 s later.  Its
grader was never executed on anything shaped like its own output until after
the compute was spent, and `D6RF4-DEF-7` -- one token for two states -- is
exactly the class of defect a pre-compute drive over a fixture finds for free.
The drive costs 0.000 solver core-min and is run BEFORE the freeze.

THE SIX SCENARIOS, each one a registered behaviour of the frozen grader:

  S1  THE HAPPY PATH.  All three legs present, tightened fvSolution installed
      before L1/L2 and D6RF3's original before L3, every field under the
      1.0e-05 accept floor at the tight setting and `p` OVER it at the loose
      one.  EXPECT: `G-CONV` PASS, `G-SOLN` PASS, `F5` AS PREDICTED, and the
      item NOT A RESULT overall -- because `G-FD`, `G-OFF` and `G-PRICE` have
      NO INPUTS in a one-arm convergence probe and section 9 item 6 says so.
      A PASS on those gates here would be the finding that something is wrong.

  S2  `F5` FIRES.  The wrong setting ALSO passes `G-CONV`.  EXPECT: `F5`
      FALSIFIED, `withdraws=True`, and `compose` rung 3a withdrawing `G-CONV`'s
      verdict -- the gate F5 NAMES, and no other (DAFOAM_CHARTER.md 21.3).

  S3  `G-SOLN` FAILS.  The tightened baseline's `CD` has moved 5 % from
      `D6RF3`'s measured 0.0184758685.  EXPECT: `G-SOLN` GATE FAIL and rung 3b
      -- the repair moved the SOLUTION, so no `G-CONV` PASS may be quoted as
      `D6RF3`'s answer.

  S4  `D6RF4-DEF-7`, THE STATE THE PARENT HAD NO TOKEN FOR.  The arm RAN and
      the gated artefact was NOT WRITTEN.  EXPECT `X-CDLOG` to read
      `ARM_RAN_ARTEFACT_NOT_WRITTEN` with the arm's rc AND its core-min beside
      it -- never `ARM_DID_NOT_RUN`, which is what the parent would have said
      about an arm that consumed 2.067 core-min.

  S6  THE SHAPE THE REGISTERED ARM ACTUALLY WRITES: an FD product with no
      `rows`, because `--mode P_conv` takes no FD step.  EXPECT a CLEAN
      grading -- `G-FD` NOT A RESULT, the plateau bar `BAR_NOT_PRODUCED`, the
      FD planted control `NOT EXERCISED` and the CD and price controls
      `EXERCISED-PASS`.  This scenario found two real defects in the grader
      before any compute; both are recorded in its own output.

  S5  `ACCEPT_FLOOR_UNMOVED` REFUSES.  The arm log carries
      `primalMinResTolDiff 1e12`.  EXPECT the WHOLE GRADING to stop, exit 2,
      with no verdict written -- because every number in it would then be
      earned against a bar nobody registered.

NO `assert` STATEMENT APPEARS IN THIS FILE.  `python -O` deletes them.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import d6rf4_grade as G                                        # noqa: E402
import d6rf4_finiteness_mutation as FM                         # noqa: E402

# Fixture residuals.  TIGHT: every field two decades under the 1.0e-05 floor.
# LOOSE: D6RF3's OWN MEASURED values at Time = 1000, so the F5 leg's fixture is
# the real thing rather than an invented failure.
TIGHT = {"U0": "1.38e-09", "U1": "5.86e-09", "U2": "3.74e-10",
         "he": "7.03e-11", "p": "1.31e-07", "nuTilda": "1.05e-07"}
LOOSE = {k: repr(v) for k, v in G.CONV_MEASURED_D6RF3.items()}

DAOPT = ("    solverName      DARhoSimpleFoam;\n"
         "    primalMinResTol {tol};\n"
         "    printIntervalUnsteady 1;\n"
         "    primalMinResTolDiff {diff};\n")


def _leg(tag, mode, res, cd, cl, failed=False):
    out = ["", "Setting UMag = 100 AoA = 0.8829754496 degs",
           "%s %s mode=%s" % (G.LEG_BEGIN, tag, mode), "", "Time = 1000", ""]
    for f in ("U0", "U1", "U2", "he", "p", "nuTilda"):
        out.append("%s initRes: %s finalRes: 1.0e-11 nIters: 3" % (f, res[f]))
    out += ["CD: %s final: %s" % (cd, cd), "CL: %s final: %s" % (cl, cl),
            "ExecutionTime = 118.3 s  ClockTime = 119 s", "", "End"]
    if failed:
        out += ["********************************************",
                "Primal min residual %s" % res["p"],
                "did not satisfy the prescribed tolerance 1e-08",
                "Primal solution failed!",
                "********************************************"]
    out.append("%s %s mode=%s J=0.0222 wall_s=118.300 primal_raised=False"
               % (G.LEG_END, tag, mode))
    return out


def arm_log(path, loose_res=None, tight_cd=None, diff="1000", tol="1e-08",
            legs=("L1", "L2", "L3")):
    tight_cd = tight_cd or repr(G.G_SOLN_CD_D6RF3)
    cl = repr(G.G_SOLN_CL_D6RF3)
    loose_res = loose_res or LOOSE
    L = ["D4S_CONTAINER_UID: 0",
         "D4S_IDWARP_SO_MD5: %s" % G.IDWARP_SO_MD5,
         "D4S_DEADLINE_IN_CONTAINER_S: %d" % G.TMO["P_conv"]]
    tightmd5 = G.FVSOL_MD5["d6rf4_fvSolution_TIGHT"]
    origmd5 = G.FVSOL_MD5["d6rf4_fvSolution_D6RF3_ORIGINAL"]
    if "L1" in legs or "L2" in legs:
        L.append("%s leg=L1_L2 md5=%s sites=4 file=d6rf4_fvSolution_TIGHT"
                 % (G.FVSOL_INSTALL_MARKER, tightmd5))
    for leg in ("L1", "L2"):
        if leg in legs:
            L += DAOPT.format(tol=tol, diff=diff).split("\n")
            L += _leg("baseline" if leg == "L1" else "baseline_repeat",
                      "P_conv", TIGHT, tight_cd, cl)
    if "L3" in legs:
        L.append("%s leg=L3 md5=%s sites=4 "
                 "file=d6rf4_fvSolution_D6RF3_ORIGINAL"
                 % (G.FVSOL_INSTALL_MARKER, origmd5))
        L += DAOPT.format(tol=tol, diff=diff).split("\n")
        L += _leg("baseline", "F5_loose", loose_res, tight_cd, cl,
                  failed=(float(loose_res["p"]) >= G.CONV_BAR))
    L.append(G.TERMINAL_STATEMENT)
    with open(path, "w") as fh:
        fh.write("\n".join(L) + "\n")
    return path


def build_root(tmp, **kw):
    """A P_conv run root: FM's fixture artefacts, plus this item's arm log,
    ledger row and chain record."""
    root = os.path.join(tmp, "run")
    d4 = FM.build(root)
    G.D4_OPT_IPOPT = d4
    log = os.path.join(root, "P_conv_fix.log")
    arm_log(log, **kw)
    with open(os.path.join(root, "STATUS.chain"), "w") as fh:
        fh.write("chain=started utc=fixture\narm=P_conv rc=0\n"
                 "chain=COMPLETE arm=P_conv rc=0 not_run=[]\n")
    # the age guard: every product strictly newer than the datum
    now = time.time()
    for p in G.REGISTERED_PRODUCTS["P_conv"]:
        f = os.path.join(root, "P_conv", p)
        if not os.path.isfile(f):
            with open(f, "w") as fh:
                json.dump({"note": "fixture"}, fh)
        os.utime(f, (now, now))
    with open(os.path.join(root, "P_conv", ".d4_age_datum"), "w") as fh:
        fh.write("%.3f" % (now - 100.0))
    return root, d4


def run_grade(root, d4, out):
    r = subprocess.run(
        [sys.executable, os.path.join(HERE, "d6rf4_grade.py"),
         "--root", root, "--out", out, "--skip-freeze", "--d4-ref", d4,
         "--runscript-d6r", os.path.join(HERE, "d6rf4_opt_runScript.py"),
         "--runscript-d4", os.path.join(HERE, os.pardir, "curriculum_D4",
                                        "d4_opt_runScript.py")],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return r.returncode, r.stdout


def show(tag, rc, out, keys):
    print("  rc=%d" % rc)
    for line in out.splitlines():
        if any(k in line for k in keys):
            print("   |%s" % line)


def main():
    tmp = tempfile.mkdtemp(prefix="d6rf4_drive_")
    rc_all = 0
    print("D6RF4 GRADER DRIVE -- SYNTHETIC FIXTURES, 0.000 SOLVER CORE-MIN")
    print("  NOTHING HERE IS A RESULT ABOUT THE A2 WING. Every input is a "
          "fixture chosen by the author;")
    print("  the drive establishes only that the frozen grading path runs and "
          "moves in the registered directions.")
    print("  fixture tmp %s" % tmp)

    # ---------------- S1: the happy path -------------------------------
    print("\n--- S1  happy path: L1/L2 tight and under the floor, L3 loose and "
          "OVER it (D6RF3's own measured values)")
    root, d4 = build_root(tmp)
    out = os.path.join(tmp, "s1.json")
    rc, txt = run_grade(root, d4, out)
    show("S1", rc, txt, ("VERDICT", "G-CONV", "G-SOLN", "F5 falsifier",
                         "ACCEPT_FLOOR", "plateau bar", "null readings",
                         "X-CDLOG"))
    d = json.load(open(out))
    ok = (d["grade"]["G-CONV"]["verdict"] == "PASS"
          and d["grade"]["G-SOLN"]["verdict"] == "PASS"
          and d["falsifiers"]["F5"]["verdict"] == "AS PREDICTED"
          and d["accept_floor_unmoved"]["state"] == G.afc.EXERCISED_PASS
          and d["verdict"] == "NOT A RESULT")
    print("  S1 as registered: %s  (G-CONV PASS, G-SOLN PASS, F5 AS "
          "PREDICTED, item NOT A RESULT because G-FD/G-OFF/G-PRICE have no "
          "inputs)" % ok)
    rc_all = rc_all if ok else 1

    # ---------------- S2: F5 fires -------------------------------------
    print("\n--- S2  F5 FIRES: the WRONG setting also passes G-CONV")
    root, d4 = build_root(tmp, loose_res=TIGHT)
    out = os.path.join(tmp, "s2.json")
    rc, txt = run_grade(root, d4, out)
    show("S2", rc, txt, ("VERDICT", "F5 falsifier", "G-CONV "))
    d = json.load(open(out))
    ok = (d["falsifiers"]["F5"]["verdict"] == "FALSIFIED"
          and d["falsifiers"]["F5"]["withdraws"] is True
          and d["falsifiers"]["F5"]["withdraws_gate"] == "G-CONV"
          and any("rung 3a" in r for r in d["verdict_reasons"])
          and d["verdict"] == "NOT A RESULT")
    print("  S2 as registered: %s  (F5 FALSIFIED, withdraws G-CONV -- the gate "
          "it NAMES and no other)" % ok)
    rc_all = rc_all if ok else 1

    # ---------------- S3: G-SOLN fails ---------------------------------
    print("\n--- S3  G-SOLN GATE FAIL: the tightened baseline's CD moved 5 %")
    root, d4 = build_root(tmp, tight_cd=repr(G.G_SOLN_CD_D6RF3 * 1.05))
    out = os.path.join(tmp, "s3.json")
    rc, txt = run_grade(root, d4, out)
    show("S3", rc, txt, ("VERDICT", "G-SOLN"))
    d = json.load(open(out))
    ok = (d["grade"]["G-SOLN"]["verdict"] == "GATE FAIL"
          and any("rung 3b" in r for r in d["verdict_reasons"])
          and d["verdict"] == "NOT A RESULT")
    print("  S3 as registered: %s  (GATE FAIL -> rung 3b: the repair moved the "
          "SOLUTION, so no G-CONV PASS may be quoted as D6RF3's answer)" % ok)
    rc_all = rc_all if ok else 1

    # ---------------- S4: DEF-7's own state ----------------------------
    print("\n--- S4  D6RF4-DEF-7: the arm RAN and the gated artefact was NOT "
          "WRITTEN")
    root, d4 = build_root(tmp)
    os.remove(os.path.join(root, "P_conv", "d6rf4_fd_endpoint.json"))
    out = os.path.join(tmp, "s4.json")
    rc, txt = run_grade(root, d4, out)
    show("S4", rc, txt, ("REFUSED", "X-CDLOG"))
    ok = "registered_product_absent" in txt or "REFUSE" in txt
    print("  S4  G1's age guard REFUSES an absent registered product on an arm "
          "that ran -- the parent's behaviour, KEPT: %s" % ok)
    print("      so DEF-7's token is reached through `_no_input_reason`, which "
          "is driven directly below rather than through a run root G1 refuses.")
    census = {"P_conv": {"state": "RAN", "source": "drive"}}
    for label, cen, arm in (
            ("arm RAN, artefact NOT written", census, "P_conv"),
            ("arm NOT REGISTERED at this freeze",
             {"REF_off": {"state": G.NOT_REGISTERED_STATE}}, "REF_off"),
            ("registered arm DID NOT RUN",
             {"P_conv": {"state": "NOT_RUN", "reason": "REGISTERED_CHAIN_ABORT"}},
             "P_conv")):
        r, det = G._no_input_reason(cen, arm, "d6rf4_fd_endpoint.json", root)
        print("      %-38s -> %s" % (label, r))
    three = {G._no_input_reason(c, a, "x.json", root)[0]
             for c, a in ((census, "P_conv"),
                          ({"REF_off": {"state": G.NOT_REGISTERED_STATE}}, "REF_off"),
                          ({"P_conv": {"state": "NOT_RUN"}}, "P_conv"))}
    ok4 = (three == {G.ARM_RAN_ARTEFACT_NOT_WRITTEN, G.NOT_REGISTERED_REASON,
                     "ARM_DID_NOT_RUN"})
    print("  S4 as registered: %s  (THREE DISTINGUISHABLE TOKENS where the "
          "parent had ONE)" % ok4)
    rc_all = rc_all if ok4 else 1

    # ---------------- S5: the accept floor moved -----------------------
    print("\n--- S5  ACCEPT_FLOOR_UNMOVED: the arm log carries "
          "primalMinResTolDiff 1e12")
    root, d4 = build_root(tmp, diff="1e12")
    out = os.path.join(tmp, "s5.json")
    rc, txt = run_grade(root, d4, out)
    print("  rc=%d (2 == REFUSED, as registered)" % rc)
    for line in txt.splitlines():
        if "ACCEPT_FLOOR" in line:
            print("   |%s" % line[:400])
    ok5 = (rc == 2 and "ACCEPT_FLOOR_MOVED" in txt
           and not os.path.exists(out))
    print("  S5 as registered: %s  (grading STOPPED, exit 2, NO VERDICT "
          "WRITTEN -- every number would have been earned against a bar "
          "nobody registered)" % ok5)
    rc_all = rc_all if ok5 else 1

    # ---------------- S6: THE SHAPE THE REGISTERED ARM ACTUALLY WRITES --
    print("\n--- S6  THE REGISTERED P_conv SHAPE: an FD product with NO rows "
          "(P_conv takes no FD step at all)")
    root, d4 = build_root(tmp)
    p = os.path.join(root, "P_conv", "d6rf4_fd_endpoint.json")
    doc = json.load(open(p))
    doc["rows"], doc["n_rows"], doc["mode"] = [], 0, "P_conv"
    json.dump(doc, open(p, "w"), indent=1, sort_keys=True)
    out = os.path.join(tmp, "s6.json")
    rc, txt = run_grade(root, d4, out)
    show("S6", rc, txt, ("VERDICT", "plateau bar", "G-FD_", "planted controls",
                         "G-CONV_", "G-SOLN_"))
    d = json.load(open(out)) if os.path.exists(out) else {}
    cs = (d.get("planted_controls") or {}).get("control_states", {})
    ok6 = (rc == 0
           and d.get("grade", {}).get("G-FD", {}).get("verdict") == "NOT A RESULT"
           and d["grade"]["G-FD"]["plateau_bar_state"] == G.BAR_NOT_PRODUCED
           and d["grade"]["G-FD"]["plateau_bar_exercised"] is None
           and cs.get("fd_control") == G.cdc.NOT_EXERCISED
           and cs.get("cd_control") == G.cdc.EXERCISED_PASS
           and cs.get("price_control") == G.cdc.EXERCISED_PASS)
    print("  S6 as registered: %s" % ok6)
    print("      THIS SCENARIO FOUND TWO REAL DEFECTS IN THE GRADER BEFORE ANY")
    print("      COMPUTE, and both were in the NOT-EXERCISED direction:")
    print("      (a) the inherited FD planted control REFUSED the whole")
    print("          grading on an empty FD product -- correct for an FD arm,")
    print("          wrong for an arm registered to take no FD step;")
    print("      (b) the first repair for (a) nulled the shared artefact path")
    print("          and sent the CD reader to NOT EXERCISED too, skipping a")
    print("          control that CAN be exercised.  Skipping an exercisable")
    print("          control and counting an unexercisable one as a pass are")
    print("          the same failure in opposite directions.")
    rc_all = rc_all if ok6 else 1

    print("\n  RESULT %s" % ("ALL SIX SCENARIOS AS REGISTERED"
                            if rc_all == 0 else "NOT AS REGISTERED"))
    print("  solver core-minutes spent by this drive: 0.000")
    shutil.rmtree(tmp, ignore_errors=True)
    return rc_all


if __name__ == "__main__":
    sys.exit(main())
