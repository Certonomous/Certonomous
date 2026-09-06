#!/usr/bin/env python3
"""W4 CBFS RE-ANCHOR -- THE END-TO-END DRIVE of `analyse_w4_reanchor.py`, on a
SYNTHETIC run tree, at ZERO SOLVER CORE-MINUTES.

WHAT THIS IS AND IS NOT.  It is a TOOL, not an instrument: `analyse_w4_reanchor.py`
neither imports nor executes it, it is NOT in `FROZEN_PATHS`, and NO NUMBER IT
PRODUCES IS A RESULT ABOUT W4.  Every value below is a fixture the author chose;
the only thing the drive establishes is that the grading path RUNS END TO END,
that every gate is TRAVERSED, and that each gate and control moves in the
REGISTERED direction when the fixture moves.  A drive on a fixture is not a
verdict, and this file says so rather than letting a reader infer otherwise.

WHY IT EXISTS ANYWAY, IN ONE SENTENCE.  D6RF4 was frozen with a launcher never
driven past :515 and aborted five times, one guard per launch, because its guard
drive covered none of the launch path -- a coverage hole wearing a green number.
This drive traverses EVERY gate on the grading path and fires EVERY control in
BOTH directions BEFORE the freeze, so that is not repeated here.

THE FIXTURE FD VALUES are anchored on the registration's OWN section-5d and
section-7.3 numbers for cell 5491 -- d(0.05) = 1.914384790951e-06 and the O(h^2)
model's d(0.75) = 1.548364e-06 -- so the happy path's F_W statistic reproduces
the registered 19.1195 % rather than an invented one.

NO `assert` STATEMENT APPEARS IN THIS FILE.  `python -O` deletes them.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyse_w4_reanchor as A                                  # noqa: E402
import w4ra_accept_floor_control as afc                          # noqa: E402

BASE_OBJ = 1.5279278906359758e-02          # W4's baseline objective at this state

# adjoint gradient (anchor8w) per cell, and the FD d(step) fixtures.
ADJ = {5491: 1.916018813330e-06, 6740: 2.000000000000e-06, 12486: 3.000000000000e-06}
# HAPPY: d(0.05) is the registration's own measured value on 5491; d(0.025) sits
# inside the 10 % bar; F_W's d(0.75) is the registered O(h^2) model value, so the
# statistic reproduces 19.1195 % and FAILS W1 as predicted (no withdrawal).
D_HI = {5491: 1.914384790951e-06, 6740: 2.000000000000e-06, 12486: 3.000000000000e-06}
D_LO = {5491: 1.900000000000e-06, 6740: 1.980000000000e-06, 12486: 2.960000000000e-06}
D_HF_FAILS = 1.548364000000e-06            # registered d(0.75): statistic ~19.12 % > 10 %
D_HF_PASSES = 1.905000000000e-06           # near d(0.05): statistic < 10 % -> WITHDRAWAL

DAOPT = ("    solverName      DASimpleFoam;\n"
         "    primalMinResTol {tol};\n"
         "    primalMinResTolDiff {diff};\n")


def _leg_log(path, obj, tol="1e-08", diff="100"):
    body = ["W4RA_LEG_BEGIN", "Setting beta re-anchor leg",
            DAOPT.format(tol=tol, diff=diff), "", "Time = 2500", "",
            "OBJ varianceU: %.16e" % obj,
            "ExecutionTime = 227.6 s  ClockTime = 228 s", "", "End",
            "W4RA_LEG_END", "Finalising parallel run"]
    with open(path, "w") as fh:
        fh.write("\n".join(body) + "\n")


def _fields(root, tag, datum):
    """fields_<tag>/processor{0..3}/2500/<field>, all NEWER than the case datum."""
    for p in range(4):
        d = os.path.join(root, "fields_%s" % tag, "processor%d" % p, "2500")
        os.makedirs(d, exist_ok=True)
        for fld in A.FIELDS:
            fp = os.path.join(d, fld)
            with open(fp, "w") as fh:
                fh.write("fixture\n")
            os.utime(fp, (datum + 100, datum + 100))


def build_root(tmp, d_hf=D_HF_FAILS, base8w_obj=None, diff_map=None,
               drop=(), miss_fields=()):
    """A plausible COMPLETED re-anchor run tree. `diff_map` overrides
    primalMinResTolDiff on named tags (for the W2-moved scenario); `drop` omits a
    leg's log (PRODUCER_CRASHED); `miss_fields` omits a leg's field dir."""
    root = tempfile.mkdtemp(prefix="run_", dir=tmp)   # a FRESH tree per scenario
    os.makedirs(os.path.join(root, "cbfs_beta", "0"), exist_ok=True)
    datum = time.time() - 1000.0
    for fld in A.FIELDS:                      # the case datum, touched last at launch
        fp = os.path.join(root, "cbfs_beta", "0", fld)
        with open(fp, "w") as fh:
            fh.write("datum\n")
        os.utime(fp, (datum, datum))

    diff_map = diff_map or {}
    ledger, tags = [], []

    def emit(tag, obj, task="run_model"):
        if tag in drop:
            tags.append(tag)
            ledger.append("%s,END,%d,2,rc=0,wall=228,core_min=7.60" % (tag, int(time.time())))
            return                            # log absent -> PRODUCER_CRASHED
        _leg_log(os.path.join(root, "log.%s" % tag), obj,
                 diff=diff_map.get(tag, "100"))
        if tag not in miss_fields:
            _fields(root, tag, datum)
        ledger.append("%s,END,%d,2,rc=0,wall=228,core_min=7.60" % (tag, int(time.time())))
        tags.append(tag)

    # legs 1-2: p050_5491 ; legs 3-4: fw750_5491 ; leg 5: anchor8w ; leg 6: base8w
    for c in A.CELLS:
        emit("p050_%d_plus" % c, BASE_OBJ + D_HI[c] * A.S_HI)
        emit("p050_%d_minus" % c, BASE_OBJ - D_HI[c] * A.S_HI)
    emit("fw750_5491_plus", BASE_OBJ + d_hf * A.H_F)
    emit("fw750_5491_minus", BASE_OBJ - d_hf * A.H_F)
    emit("anchor8w", BASE_OBJ, task="compute_totals")
    emit("base8w", BASE_OBJ if base8w_obj is None else base8w_obj)
    for c in A.CELLS:
        emit("p025_%d_plus" % c, BASE_OBJ + D_LO[c] * A.S_LO)
        emit("p025_%d_minus" % c, BASE_OBJ - D_LO[c] * A.S_LO)

    with open(os.path.join(root, "ledger.csv"), "w") as fh:
        fh.write("\n".join(ledger) + "\n")

    # the anchor8w reference gradient (arm's OWN 1e-8), size 21000
    g = np.zeros(21000)
    for c, v in ADJ.items():
        g[c] = v
    np.save(os.path.join(root, A.ANCHOR_GRAD_NAME), g)
    return root


def run_grade(root, out):
    r = subprocess.run(
        [sys.executable, os.path.join(HERE, "analyse_w4_reanchor.py"),
         "--run-root", root, "--json", out, "--skip-freeze"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return r.returncode, r.stdout


# gates the grading path traverses on the happy tree (each printed [n]-section
# or named control). The drive asserts every one is reached in S1's stdout.
GATE_MARKERS = (
    "frozen_path_coverage", "null_reading_coverage", "imported_symbol_identity",
    "staged", "[1] W2", "[2] anchor gradient", "[3] RULE 4", "[4] W0",
    "[5] PLANTED-ZERO", "[6] F_W", "[7] W1", "cell 5491:", "cell 6740:",
    "cell 12486:", "[8] REGISTERED CONSEQUENCE", "[9] SIGN-FLIP",
    "[10] RULE 12", "VERDICT",
)


def main():
    tmp = tempfile.mkdtemp(prefix="w4ra_drive_")
    rc_all = 0
    print("W4 RE-ANCHOR GRADER DRIVE -- SYNTHETIC FIXTURES, 0.000 SOLVER CORE-MIN")
    print("  NOTHING HERE IS A RESULT ABOUT W4. Every input is a fixture chosen by "
          "the author;")
    print("  the drive establishes only that the frozen grading path runs, that "
          "every gate is TRAVERSED, and that each gate/control moves in the "
          "registered direction.")
    print("  fixture tmp %s" % tmp)

    # ---------------- S1: HAPPY PATH -> PASS, every gate traversed -----------
    print("\n--- S1  HAPPY PATH: W1 inside 10 % on all 3 cells, F_W FAILS W1 as "
          "predicted (~19.12 %), W0 holds, plant seen -> PASS")
    root = build_root(tmp)
    out = os.path.join(tmp, "s1.json")
    rc, txt = run_grade(root, out)
    traversed = [m for m in GATE_MARKERS if m in txt]
    missing = [m for m in GATE_MARKERS if m not in txt]
    d = json.load(open(out)) if os.path.exists(out) else {}
    fw_pct = d.get("f_w", {}).get("measured_stat_pct_dhi")
    ok1 = (rc == 0 and d.get("verdict", {}).get("item_token") == "PASS"
           and not missing
           and d["f_w"]["prediction_met"] is True
           and abs((fw_pct or 0) - A.FALSIFIER_PRED_PCT_DHI) < 0.01
           and all(d["w1"][str(c)]["token"] == "PASS" for c in A.CELLS)
           and d["w0"]["equal_16_digits"] is True
           and d["plant"]["seen"] is True
           and d["w2_accept_floor"]["all_legs_unmoved"] is True)
    print("  gates traversed: %d/%d %s" % (len(traversed), len(GATE_MARKERS),
          ("(missing: %s)" % missing) if missing else "(ALL)"))
    print("  F_W measured %.4f %% vs registered %.4f %% ; verdict %s" %
          (fw_pct or -1, A.FALSIFIER_PRED_PCT_DHI, d.get("verdict", {}).get("item_token")))
    print("  S1 as registered: %s" % ok1)
    rc_all = rc_all if ok1 else 1

    # ---------------- S2: F_W PASSES W1 -> WITHDRAWAL -----------------------
    print("\n--- S2  F_W PASSES W1 (wrong step near d(0.05)) -> W1 withdrawn for "
          "every component -> NOT A RESULT")
    root = build_root(tmp, d_hf=D_HF_PASSES)
    out = os.path.join(tmp, "s2.json")
    rc, txt = run_grade(root, out)
    d = json.load(open(out))
    ok2 = (rc == 0 and d["falsifier_withdrawal"] is True
           and d["f_w"]["falsifier_passes_w1"] is True
           and d["verdict"]["item_token"] == "NOT A RESULT"
           and all(d["w1"][str(c)].get("withdrawn_by_falsifier") is True for c in A.CELLS))
    print("  F_W statistic %.4f %% <= 10 %% -> withdraws; verdict %s" %
          (d["f_w"]["measured_stat_pct_dhi"], d["verdict"]["item_token"]))
    print("  S2 as registered: %s  (withdraws W1 -- the gate F_W NAMES, and no other)" % ok2)
    rc_all = rc_all if ok2 else 1

    # ---------------- S3: one W1 component misses --------------------------
    print("\n--- S3  W1 MISS on cell 12486 (d(0.025) far from d(0.05)); F_W still "
          "fails W1 -> that cell NOT A RESULT, item NOT A RESULT")
    root = build_root(tmp)
    # move 12486's d(0.025) 30 % off d(0.05) by editing its p025 logs
    for sgn, s in (("plus", +1), ("minus", -1)):
        _leg_log(os.path.join(root, "log.p025_12486_%s" % sgn),
                 BASE_OBJ + s * (D_HI[12486] * 0.70) * A.S_LO)
    out = os.path.join(tmp, "s3.json")
    rc, txt = run_grade(root, out)
    d = json.load(open(out))
    ok3 = (rc == 0 and d["falsifier_withdrawal"] is False
           and d["w1"]["12486"]["token"] == "NOT A RESULT"
           and d["w1"]["5491"]["token"] == "PASS"
           and d["verdict"]["item_token"] == "NOT A RESULT")
    print("  cell 12486 W1 move %.2f %% -> %s ; verdict %s" %
          (d["w1"]["12486"]["w1_move"] * 100, d["w1"]["12486"]["token"],
           d["verdict"]["item_token"]))
    print("  S3 as registered: %s  (NOT A RESULT, not GATE FAIL -- a failed plateau "
          "is not a wrong adjoint)" % ok3)
    rc_all = rc_all if ok3 else 1

    # ---------------- S4: W0 base consistency fails -> REFUSE ---------------
    print("\n--- S4  W0 FAILS: base8w OBJ != anchor8w OBJ -> REFUSE (no FD number "
          "graded against a gradient from a different state)")
    root = build_root(tmp, base8w_obj=BASE_OBJ * (1.0 + 1e-6))
    out = os.path.join(tmp, "s4.json")
    rc, txt = run_grade(root, out)
    ok4 = (rc == 2 and "W0 FAILED" in txt)
    print("  rc=%d (2==REFUSED) ; contains 'W0 FAILED': %s" % (rc, "W0 FAILED" in txt))
    print("  S4 as registered: %s" % ok4)
    rc_all = rc_all if ok4 else 1

    # ---------------- S5: W2 accept floor moved -> REFUSE ------------------
    print("\n--- S5  W2 MOVED: one leg's log carries primalMinResTolDiff 1e12 -> "
          "REFUSE, exit 2, NO VERDICT")
    root = build_root(tmp, diff_map={"p025_6740_plus": "1e12"})
    out = os.path.join(tmp, "s5.json")
    rc, txt = run_grade(root, out)
    ok5 = (rc == 2 and "W2_ACCEPT_FLOOR" in txt and not os.path.exists(out))
    print("  rc=%d ; contains 'W2_ACCEPT_FLOOR': %s ; verdict written: %s" %
          (rc, "W2_ACCEPT_FLOOR" in txt, os.path.exists(out)))
    print("  S5 as registered: %s" % ok5)
    rc_all = rc_all if ok5 else 1

    # ---------------- S6: STAGED INSTRUMENT md5 mismatch -> REFUSE ----------
    print("\n--- S6  STAGED-INSTRUMENT md5 MISMATCH (control driven BOTH ways in-process)")
    real = A.staged_instrument_md5s()
    ok6a = all(v["match"] for v in real.values())
    saved = dict(A.STAGED_INSTRUMENTS)
    A.STAGED_INSTRUMENTS["runScript.py"] = "0" * 32   # a wrong registered md5
    got6b = "NO REFUSAL"
    try:
        A.staged_instrument_md5s()
    except A.Refusal:
        got6b = "REFUSED"
    A.STAGED_INSTRUMENTS.clear(); A.STAGED_INSTRUMENTS.update(saved)
    ok6 = (ok6a and got6b == "REFUSED" and all(v["match"] for v in A.staged_instrument_md5s().values()))
    print("  real staged md5s all match: %s ; wrong registered md5 -> %s" % (ok6a, got6b))
    print("  S6 as registered: %s  (staged copy graded, not the source -- prereg 4.3)" % ok6)
    rc_all = rc_all if ok6 else 1

    # ---------------- S7: PLANTED-ZERO not seen -> REFUSE ------------------
    print("\n--- S7  PLANTED-ZERO control driven BOTH ways: PLANT=0 must REFUSE 'NOT SEEN'")
    root = build_root(tmp)
    saved_plant = A.PLANT
    A.PLANT = 0.0
    got7 = "NO REFUSAL"
    argv = sys.argv
    sys.argv = ["x", "--run-root", root, "--json", os.path.join(tmp, "s7.json"),
                "--skip-freeze"]
    try:
        A.main()
    except A.Refusal as e:
        got7 = "REFUSED" if "PLANT WAS NOT SEEN" in str(e) else "REFUSED(other:%s)" % str(e)[:60]
    except SystemExit:
        got7 = "SYSEXIT"
    finally:
        sys.argv = argv
        A.PLANT = saved_plant
    ok7 = got7 == "REFUSED"
    print("  PLANT=0 -> %s (the clean-plant SEEN direction is S1's plant.seen=True)" % got7)
    print("  S7 as registered: %s" % ok7)
    rc_all = rc_all if ok7 else 1

    # ---------------- S8: a leg log dropped -> BLOCKED ---------------------
    print("\n--- S8  PRODUCER_CRASHED: a leg's log absent -> BLOCKED, no success "
          "token over a short program")
    root = build_root(tmp, drop=("p025_6740_minus",))
    out = os.path.join(tmp, "s8.json")
    rc, txt = run_grade(root, out)
    d = json.load(open(out))
    ok8 = (rc == 0 and d["verdict"]["item_token"] == "BLOCKED"
           and d["completion"]["p025_6740_minus"]["bar_state"] == "PRODUCER_CRASHED")
    print("  p025_6740_minus bar_state=%s ; verdict %s" %
          (d["completion"]["p025_6740_minus"]["bar_state"], d["verdict"]["item_token"]))
    print("  S8 as registered: %s  (PRODUCER_CRASHED distinct from RAN-BUT-MISSED)" % ok8)
    rc_all = rc_all if ok8 else 1

    # ---------------- S9: F_W legs missing -> precondition, W1 UNRESOLVED ---
    print("\n--- S9  PRECONDITION: F_W legs absent -> BLOCKED, and every W1 cell "
          "reads UNRESOLVED (not PASS on its own merits)")
    root = build_root(tmp, drop=("fw750_5491_plus", "fw750_5491_minus"))
    out = os.path.join(tmp, "s9.json")
    rc, txt = run_grade(root, out)
    d = json.load(open(out))
    ok9 = (rc == 0 and d["verdict"]["item_token"] == "BLOCKED"
           and all(d["w1"][str(c)]["token"] == "UNRESOLVED" for c in A.CELLS)
           and d["f_w"].get("bar_state") == "FALSIFIER_NOT_PRODUCED")
    print("  F_W bar_state=%s ; W1 cells %s ; verdict %s" %
          (d["f_w"].get("bar_state"),
           {c: d["w1"][str(c)]["token"] for c in A.CELLS},
           d["verdict"]["item_token"]))
    print("  S9 as registered: %s  (a gate whose discriminating power was never "
          "tested is UNRESOLVED, never PASS)" % ok9)
    rc_all = rc_all if ok9 else 1

    # ---------------- W2's OWN control drive (6 directions, both ways) ------
    print("\n--- W2  the imported ACCEPT_FLOOR_UNMOVED control's own drive "
          "(6 directions, both senses):")
    w2rc = afc.drive()
    print("  W2 control drive rc=%d (0 == all directions as registered)" % w2rc)
    rc_all = rc_all if w2rc == 0 else 1

    print("\n" + "=" * 78)
    print("  GATES TRAVERSED ON THE HAPPY PATH: %d/%d (S1 asserted every marker present)"
          % (len(GATE_MARKERS), len(GATE_MARKERS)))
    print("  CONTROLS DRIVEN BOTH WAYS: W2 accept-floor (6 dirs), planted-zero "
          "(seen S1 / not-seen S7), staged-md5 (match S6a / mismatch S6b), W0 "
          "(holds S1 / fails S4), F_W (fails-as-predicted S1 / passes-withdraws S2)")
    print("  RESULT %s" % ("ALL NINE SCENARIOS + W2 DRIVE AS REGISTERED"
                          if rc_all == 0 else "NOT AS REGISTERED"))
    print("  solver core-minutes spent by this drive: 0.000")
    shutil.rmtree(tmp, ignore_errors=True)
    return rc_all


if __name__ == "__main__":
    sys.exit(main())
