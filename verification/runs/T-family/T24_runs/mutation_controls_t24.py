#!/usr/bin/env python3
"""MUTATION CONTROLS FOR `analyse_t24.py`.

WHAT THIS MEASURES, AND WHAT IT DOES NOT
----------------------------------------
A selftest that passes tells you nothing about what an instrument can catch.
This harness MEASURES that: it damages one registered decision at a time in a
COPY of the comparator, runs that copy's own selftest, and records whether the
damage turned the suite RED.  A mutation the suite does not notice is reported
as a MISS, by name, with its reason -- the misses are the measurement, not an
embarrassment to be hidden.

THE HARNESS ITSELF CARRIES A PLANTED CONTROL.  Arm 0 runs an UNMUTATED copy and
REQUIRES it green.  If the clean arm is red, every "caught" below is
meaningless, because a harness that reds on everything catches nothing -- and a
stale `__pycache__` can INVERT exactly this (the clean arm fails, the mutated
arm passes), which is why each mutant runs in a fresh sandbox with no inherited
cache.

EVERY MUTATION IS APPLIED BY EXACT STRING REPLACEMENT AND THE APPLICATION IS
VERIFIED.  A mutation whose pattern did not match would be a no-op, and a no-op
scored as a MISS would be a lie about the instrument.  An unapplied pattern
ABORTS the harness rather than being counted either way.

NO T24 CASE DATA IS READ ANYWHERE IN THIS FILE.  Every arm runs against forged
trees built by `analyse_t24.forge_case`, in a temporary sandbox.

Usage: python3 mutation_controls_t24.py [--verbose]
Exit: 0 the clean arm is green and every MUST-CATCH mutation was caught,
      1 otherwise, 2 REFUSAL (a mutation pattern did not apply).
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
TARGET = os.path.join(HERE, "analyse_t24.py")
COMPANION = os.path.join(HERE, "mark_done_t24.py")
ROACHE = os.path.join(REPO, "scripts", "roache_triple.py")

EXIT_OK, EXIT_BAD, EXIT_REFUSE = 0, 1, 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


# --------------------------------------------------------------------------
# THE MUTATIONS.  (id, what registered decision it damages, old, new, kind)
# kind is "MUST-CATCH" -- the suite is required to go red -- or "EXPECTED-MISS",
# a quantity the frozen document registers as REPORTED AND NEVER GATED, whose
# corruption CANNOT change a verdict by construction.  An expected miss is a
# statement about the registration, not a hole in the instrument, and it is
# listed here so nobody has to take that distinction on trust.
# --------------------------------------------------------------------------
MUTATIONS = [
    # ---- the three registered bands (section 1 line 4)
    ("B1-threshold", "section 1 line 4: the 200.0 degC engineering bound",
     "B1_BOUND_C = 200.0", "B1_BOUND_C = 150.0", "MUST-CATCH"),
    ("B2-threshold", "section 1 line 4: the 0.0 degC floor",
     "B2_FLOOR_C = 0.0", "B2_FLOOR_C = -100.0", "MUST-CATCH"),
    ("B3-anti-degeneracy-dropped",
     "section 1 line 3: Q1 and Q2 must DIFFER, or the two readers are reading "
     "the same object twice",
     "    b3 = (q1_C >= q2_C) and (q1_C != q2_C)",
     "    b3 = (q1_C >= q2_C)", "MUST-CATCH"),

    # ---- the branch that is easiest to get wrong (frozen line 228)
    ("B1-unmet-becomes-GATE-FAIL",
     "section 1 line 4: B1's not-met branch is a FLAGGED PASS, NOT a GATE FAIL",
     '        verdict, flag = "PASS", B1_FLAG',
     '        verdict, flag = "GATE FAIL", None', "MUST-CATCH"),

    # ---- the one-way criteria order (frozen line 266)
    ("criteria-order-B2-before-B3",
     "section 1 line 7: B3 is tested BEFORE B2/B1, and a gate may only turn a "
     "PASS into NOT A RESULT, never the reverse",
     '    elif not b3:\n        verdict, flag = "NOT A RESULT", None\n'
     '    elif not b2:\n        verdict, flag = "GATE FAIL", None',
     '    elif not b2:\n        verdict, flag = "GATE FAIL", None\n'
     '    elif not b3:\n        verdict, flag = "NOT A RESULT", None',
     "MUST-CATCH"),
    ("mesh-identity-cannot-demote",
     "section 3.7: a mesh mismatch makes the affected rows NOT A RESULT",
     "    if not mesh_ok:\n        verdict, flag = \"NOT A RESULT\", None",
     "    if False:\n        verdict, flag = \"NOT A RESULT\", None",
     "MUST-CATCH"),

    # ---- CLAUDE.md rule 3, the planted-zero control (section 3.6)
    ("plant-predicate-swapped-to-the-REJECTED-absolute-form",
     "section 3.6 clause 5 EXPRESSLY REJECTS analyse_t3.py:327's absolute "
     "`seen >= PLANT - 1e-15`; the registered predicate is RELATIVE",
     "        if not (at_plant >= PLANT * (1.0 - PLANT_REL_SLACK)):",
     "        if not (at_plant >= PLANT - 1e-15):", "MUST-CATCH"),
    ("negative-arm-given-a-tolerance",
     "section 3.6 clause 2: bitwise 0.0, and NO absolute tolerance anywhere in "
     "the negative arm",
     "        if (b - a) != 0.0:", "        if abs(b - a) > 1e-12:",
     "MUST-CATCH"),
    # MEASURED, AND THE REASON IS STRUCTURAL RATHER THAN A GAP IN THE SUITE:
    # `floor is None` holds only when EVERY ladder magnitude read zero, PLANT
    # among them, so `at_plant` is 0.0 and clause 5's sizing predicate refuses
    # the SAME reader on the next line.  No reader can trip clause 4 without
    # also tripping clause 5.  Clause 4's value is DIAGNOSTIC -- it names the
    # reader BLIND rather than merely undersized -- and it is defence in depth,
    # not an independent gate.  analyse_t24.py's selftest carries an arm that
    # MEASURES this shadowing instead of leaving it to be assumed.
    ("BLIND-refusal-removed",
     "section 3.6 clause 4: REFUSE if no ladder magnitude produced a non-zero "
     "read. SHADOWED BY CLAUSE 5: a blind reader reads 0.0 at PLANT and 0.0 >= "
     "PLANT*(1-1e-9) is false, so the sizing predicate refuses it anyway",
     "        if floor is None:", "        if floor is None and False:",
     "EXPECTED-MISS"),
    ("PLANT-redefined-locally",
     "section 3.6 clause 6: PLANT is IMPORTED from scripts/roache_triple.py "
     "and never redefined",
     "PLANT = RT.PLANT ", "PLANT = 1.0e-03  # ", "MUST-CATCH"),
    ("ladder-loses-PLANT",
     "section 3.6 clause 3: the registered magnitude ladder contains PLANT",
     "LADDER = (10.0, 1.0, 1e-1, 1e-2, PLANT, 1e-3, 1e-4, 1e-5, 1e-6)",
     "LADDER = (10.0, 1.0, 1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6)", "MUST-CATCH"),
    ("plant-located-by-value-not-structurally",
     "section 3.6 clause 7: the plant is located STRUCTURALLY, by line index "
     "from the field's own header -- Q2 plants EVERY face so its shift is "
     "PLANT and not PLANT/N",
     "    for i in range(n):\n        lines[first + i] = \"%.12g\" % "
     "(float(lines[first + i]) + mag)\n    open(p, \"w\").write("
     "\"\\n\".join(lines))\n    return n",
     "    lines[first] = \"%.12g\" % (float(lines[first]) + mag)\n"
     "    open(p, \"w\").write(\"\\n\".join(lines))\n    return 1",
     "MUST-CATCH"),

    # ---- section 7.1, the guard analyse_t23.py does not carry
    ("Ux-exclusion-refusal-REMOVED",
     "section 7.1: a ratio above 1e-12 REFUSES the exclusion for that case",
     "    excluded = ratio <= UX_UZ_RATIO_MAX", "    excluded = True",
     "MUST-CATCH"),
    ("Ux-exclusion-threshold-LOOSENED",
     "section 7.1: the registered threshold is 1e-12, measured per case",
     "UX_UZ_RATIO_MAX = 1e-12", "UX_UZ_RATIO_MAX = 1.0", "MUST-CATCH"),
    ("Ux-ratio-recited-instead-of-measured",
     "section 7.1: the ratio is measured on THIS case and NEVER recited from "
     "T23",
     "    ratio = (mx[0] / mx[2]) if mx[2] else float(\"inf\")",
     "    ratio = 1.561e-16  # recited from T23", "MUST-CATCH"),

    # ---- section 3.7, mesh identity
    ("mesh-identity-always-true",
     "section 3.7: the twelve cases' points are asserted byte-identical to "
     "T23_P305_U10's",
     "        ok[case] = all(digests[case][r] == ref[r] for r in MESH_REGIONS)",
     "        ok[case] = True", "MUST-CATCH"),

    # ---- section 7.2, the y+ false zero
    ("yplus-BLIND-sentinel-removed",
     "section 7.2: a log whose own text says y+ was not calculated is BLIND "
     "and its zeros are REFUSED, not read",
     "    if any(s in txt for s in YPLUS_BLIND):",
     "    if any(s in txt for s in YPLUS_BLIND) and False:", "MUST-CATCH"),

    # ---- section 1 line 7 criterion 1, completion, delegated
    ("completion-marker-not-required",
     "section 1 line 7: strict completion is FIRST and one-way; a row is not "
     "graded before its completion is marked",
     "    if not os.path.exists(marker):", "    if False:", "MUST-CATCH"),
    ("stale-completion-marker-accepted",
     "section 3.5: a marker whose case no longer completes is STALE",
     "    fails, notes = MD.check(root, case)\n    if fails:",
     "    fails, notes = MD.check(root, case)\n    if False:", "MUST-CATCH"),

    # ---- section 2.4, the predictor's transcription from the frozen table
    ("T23-rise-mistranscribed",
     "section 2.4: the predictor is built from T23's MEASURED rises, "
     "transcribed from the frozen document",
     "T23_RISE_K = {10: 88.758,", "T23_RISE_K = {10: 88.858,", "MUST-CATCH"),
    ("T23-map-row-mistranscribed",
     "section 6.5: the 16-point map's T23 rows are transcribed from the frozen "
     "B1 margins and cross-checked against T_inf + rise",
     "T23_TMAX_C = {(305, 10): 103.6078,", "T23_TMAX_C = {(305, 10): 113.6078,",
     "MUST-CATCH"),

    # ---- section 0.3, the CATEGORY ERROR guard
    ("no-ladder-statement-suppressed",
     "section 0.3: a single mesh level admits no triple, and the artifact must "
     "say so rather than leave a reader to infer it",
     "SINGLE MESH LEVEL ADMITS NO TRIPLE, so no Roache classification, ",
     "single mesh level; no comment offered, ", "MUST-CATCH"),
    ("Ri-reported-as-a-passing-check",
     "section 3.4: Ri is DECLARED VACUOUS and is NOT reported as passing -- "
     "printing 'Ri = 0 < 0.1, PASS' is evidence annotated as non-binding",
     "SECTION 3.4: the directive's Ri < 0.1 criterion is DECLARED VACUOUS ",
     "SECTION 3.4: the directive's Ri < 0.1 criterion PASSES: Ri = 0 < 0.1 ",
     "MUST-CATCH"),

    # ---- section 1 line 3, Q2's reader path
    ("Q2-falls-back-to-refValue",
     "section 1 line 3: Q2 reads the `value` entry, NEVER `refValue`, and does "
     "not fall back from one to the other",
     "        if opened and depth == 1 and re.match(r\"\\s+value\\s+nonuniform\\s+\"",
     "        if opened and depth == 1 and re.match(r\"\\s+refValue\\s+nonuniform\\s+\"",
     "MUST-CATCH"),

    # ---- quantities the frozen document registers as NEVER GATED.  Corrupting
    # one CANNOT move a verdict, by construction, so the suite is EXPECTED to
    # miss it.  Listed so the boundary is measured rather than asserted.
    ("linearity-tolerance-corrupted",
     "section 2.4: the 2 % departure is REPORTED and IS NOT A GATE -- 'the "
     "affected row still carries whatever B1/B2/B3 say' (frozen line 421)",
     "LINEARITY_TOL_FRAC = 0.02", "LINEARITY_TOL_FRAC = 1e-12",
     "EXPECTED-MISS"),
    # RECLASSIFIED BY THIS HARNESS, and the reclassification is the finding.
    # It was first entered as an EXPECTED-MISS on the reasoning that T24
    # registers no residual gate, so a corrupted tolerance could not move a
    # verdict.  The harness reported it CAUGHT, i.e. as a SURPRISE, and the
    # surprise was right and the classification wrong: section 3.1 registers
    # the assertion tolerance AT 1e-06 and section 6.5 requires the asserted
    # residuals in the report, so corrupting it corrupts a REGISTERED REPORT
    # even though it moves no gate.  "Moves no gate" and "is not registered"
    # are different claims and only the first one is true here.
    ("residual-tolerance-corrupted",
     "section 3.1 registers the convergence assertion AT 1e-06 and section 6.5 "
     "requires it in the report; it gates nothing, but it is registered, and a "
     "corrupted tolerance corrupts a registered report",
     "RESID_TOL = 1e-6", "RESID_TOL = 1e-30", "MUST-CATCH"),
    ("per-case-cost-cap-corrupted",
     "section 1 line 8: the cap is enacted as `timeout 2700s` in the LAUNCHER; "
     "the comparator only reports against it",
     "PER_CASE_CAP_CORE_MIN = 45.0", "PER_CASE_CAP_CORE_MIN = 0.001",
     "EXPECTED-MISS"),
]


def build_sandbox(src_text):
    """A tree deep enough that the comparator's own REPO derivation resolves
    inside the sandbox, so a mutant never imports the real repo's modules."""
    tmp = tempfile.mkdtemp(prefix="t24mut_")
    runs = os.path.join(tmp, "verification", "runs", "T-family", "T24_runs")
    os.makedirs(runs)
    os.makedirs(os.path.join(tmp, "scripts"))
    shutil.copy2(ROACHE, os.path.join(tmp, "scripts", "roache_triple.py"))
    shutil.copy2(COMPANION, os.path.join(runs, "mark_done_t24.py"))
    path = os.path.join(runs, "analyse_t24.py")
    with open(path, "w") as fh:
        fh.write(src_text)
    return tmp, path


def run_suite(path, verbose=False):
    """-> (green, tail).  The mutant's OWN selftest, single mode; the two-mode
    re-exec is the comparator's clause-9 control and is not re-driven here."""
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"        # belt; the sandbox is fresh too
    p = subprocess.run([sys.executable, path, "--selftest", "--no-reexec"],
                       capture_output=True, text=True, env=env, timeout=1800)
    out = (p.stdout or "") + (p.stderr or "")
    if verbose:
        print(out[-3000:])
    return p.returncode == 0, out


def red_lines(out):
    return [l.strip() for l in out.split("\n") if l.strip().startswith("[FAIL]")]


def main(argv):
    verbose = "--verbose" in argv
    for p in (TARGET, COMPANION, ROACHE):
        if not os.path.isfile(p):
            refuse("no %s" % p)
    src = open(TARGET).read()

    print("MUTATION CONTROLS FOR analyse_t24.py")
    print("Target: %s" % TARGET)
    print("Each arm runs in a FRESH sandbox with no inherited __pycache__: a "
          "stale cache inverts a mutation control, so the clean arm would fail "
          "and the mutated arm pass.\n")

    # ---- ARM 0: THE HARNESS'S OWN PLANTED CONTROL.
    tmp, path = build_sandbox(src)
    try:
        green, out = run_suite(path, verbose)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("  [%s] ARM 0, THE PLANTED CONTROL: an UNMUTATED copy is GREEN"
          % ("ok " if green else "FAIL"))
    if not green:
        print("     THE CLEAN ARM IS RED, SO NOTHING BELOW WOULD MEAN "
              "ANYTHING: a harness that reds on everything catches nothing.")
        for l in red_lines(out)[:10]:
            print("     " + l)
        return EXIT_BAD
    print("")

    caught, missed, expected_missed, surprises = [], [], [], []
    for mid, why, old, new, kind in MUTATIONS:
        if src.count(old) != 1:
            refuse("mutation %r matches its pattern %d times, not exactly 1 -- "
                   "an unapplied mutation scored either way would be a lie "
                   "about the instrument" % (mid, src.count(old)))
        mutant = src.replace(old, new, 1)
        if mutant == src:
            refuse("mutation %r changed nothing" % mid)
        tmp, path = build_sandbox(mutant)
        try:
            green, out = run_suite(path, verbose)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        red = not green
        firstred = (red_lines(out) or ["(the suite died before reporting)"])[0]
        if kind == "MUST-CATCH":
            (caught if red else missed).append((mid, why, firstred))
            print("  [%s] %-46s %s" % ("ok " if red else "MISS", mid,
                                       "CAUGHT" if red else "NOT CAUGHT"))
            if red and verbose:
                print("        first red arm: %s" % firstred)
        else:
            if red:
                surprises.append((mid, why, firstred))
                print("  [!! ] %-46s CAUGHT, though registered as never gated"
                      % mid)
            else:
                expected_missed.append((mid, why))
                print("  [ex ] %-46s NOT CAUGHT (expected: never gated)" % mid)

    print("\n=== WHAT THIS INSTRUMENT CAN FAIL ===")
    print("MUST-CATCH mutations caught: %d of %d"
          % (len(caught), len(caught) + len(missed)))
    if missed:
        print("\nMISSES -- REGISTERED DECISIONS THIS SUITE DOES NOT DEFEND. "
              "These are the measurement:")
        for mid, why, _ in missed:
            print("  - %s\n      %s" % (mid, why))
    else:
        print("  No MUST-CATCH mutation survived.")
    print("\nEXPECTED MISSES -- quantities the frozen document registers as "
          "REPORTED AND NEVER GATED, whose corruption CANNOT move a verdict by "
          "construction. Their survival is a property of the REGISTRATION, not "
          "a hole in the comparator:")
    for mid, why in expected_missed:
        print("  - %s\n      %s" % (mid, why))
    if surprises:
        print("\nSURPRISES -- a never-gated quantity whose corruption DID turn "
              "the suite red. Investigate: either the quantity is gated after "
              "all, or a control is coupled to it by accident:")
        for mid, why, first in surprises:
            print("  - %s: %s\n      %s" % (mid, first, why))

    ok = (not missed) and (not surprises)
    print("\nMUTATION CONTROLS %s" % ("PASS" if ok else "FAIL"))
    return EXIT_OK if ok else EXIT_BAD


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
