#!/usr/bin/env python3
"""T3d comparator — the triple (R_m, R_f, R_fx) graded through the FROZEN
analyse_t3.py, with the rule-3 planted-zero control REPAIRED per

IDENTICAL to analyse_t3c.py but for FIVE identity hunks, none of them logic:
LADDER level f R_ff -> R_fx, the output filename, the confound wording, the cost
key, and the rung label.  NO predicate, threshold, gate, band or verdict rule
differs.  `R_fx` is R_ff's SAME MESH continued from iteration 118 000, so this is
not a new level -- it is the same level iterated further, and the ladder's two
coarse members are byte-identical to T3c's.

Registered by T3d_PREREGISTRATION.md and frozen BEFORE R_fx has iterated: at the
freeze commit no R_fx time directory, STATUS or DONE marker exists.

The remainder of this docstring is analyse_t3c.py's and applies unchanged --
VERIFICATION_CHARTER.md §2d.11.1 (v1.45, commit ad9eda53).

WHAT IS REPAIRED, AND WHAT IS NOT.  analyse_t3.py:326-327 sets `seen` to the
reader's MAXIMUM CHANGE OVER ALL CELLS and tests `seen >= PLANT - 1e-15`.  That
predicate NEVER ASKS WHETHER THE MAXIMUM IS AT THE PLANTED CELL, so on a case in
a limit cycle it certifies the reader on a real change the plant did not produce.
Measured: on R_c it returned True on a 2.4684 K change while the planted cell was
never the argmax -- clearing a 1.234e-03 K plant by ~2000x WITHOUT SEEING IT.
Verification ruled that a rule-3 violation inside a rule-3 control and granted
the repair.  NOTHING ELSE CHANGES: no gate, no band, no threshold on any graded
quantity, no verdict logic.  PLANT stays 1.234e-03 K.

THE REGISTERED PREDICATE IS **P-2**, and it SUPERSEDES T3c_PREREGISTRATION.md
§5.1's P-1.  P-1 was drafted 2026-08-30, before the fail-open limb was found, and
was MEASURED (this lane, 2026-09-03) still to pass R_c vacuously: `got == rec` to
the last digit, the plant invisible.  P-1 repairs the fails-CLOSED limb only.

    LIMB A (LOCATION)   the reader's max_change must BE the planted cell's
                        difference -- the control can pass only by seeing ITS OWN
                        plant.  This is the repair.
    LIMB B (MAGNITUDE)  abs(got_max - PLANT) <= N_ULP * ulp(operand)

N_ULP = 32.  §2d.11.1 condition 4 forbids a hardcoded "equivalent" constant: the
tolerance is computed from math.ulp() OF THE ACTUAL OPERANDS at grade time, so it
is correct at any field magnitude.  The VALUE 32 is fixed by arms already frozen
in T3c_PREREGISTRATION.md §9 before this question arose -- S-2 requires drift
-7/0/+7/+21 ulp to PASS (lower bound 21) and +200 ulp to REFUSE (upper bound
200).  The admissible window is 21 <= N_ULP < 200; the admissible powers of two
are 32, 64 AND 128.  **32 is the SMALLEST ADMISSIBLE power of two**, i.e. the
most restrictive tolerance that still satisfies every frozen must-pass arm -- the
choice that cannot be accused of having been tuned to pass something.  (An
earlier draft of this reasoning claimed 32 was the UNIQUE admissible power of
two.  That was false and is corrected here rather than quietly dropped.)

WHAT THIS FILE'S FREEZE STATUS WILL BE, STATED SO IT IS NOT MISREAD.
scripts/check_comparator_freeze.py will scope this comparator to DONE.R_m and
DONE.R_f (2026-08-24) and report it UNFROZEN.  THAT IS A TRUE POSITIVE, not an
artifact: two of the three levels were complete and published in gate_t3.json
before this module existed.  It is dispositioned by the §2d.11.1 grant under
§2d.1, not argued away.  What was NOT known when this predicate was written is
every graded R_ff quantity: gate_t3_rff.json was never written and no St_peak,
x_peak/H, refinement ratio, observed order or GCI has been computed by anyone.

Output: gate_t3c.json beside this file.  gate_t3.json and gate_t3_rff.json are
never written.  Exit 0 ran, 1 selftest failed, 2 refusal.  Zero `assert` (L-332).
"""
import datetime, json, math, os, shutil, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyse_t3 as A          # FROZEN comparator, imported, never edited

LADDER = {"c": "R_m", "m": "R_f", "f": "R_fx"}
LEVELS = A.LEVELS
P_MIN = 0.5                     # the floor A.gci_unequal applies; T11 352aef0d
N_ULP = 32                      # smallest admissible power of two; see docstring
GATE_JSON = os.path.join(HERE, "gate_t3d.json")
CONFOUND = ("R_fx and R_ff ran decomposed (8 ranks, simple (8 1 1)); R_m and R_f ran serial. "
            "The triple carries ONE non-mesh difference, floating-point summation order "
            "(F15 RULING 2, T3_R_FF_PREREGISTRATION.md S5). Quoted on every row.")
EXIT_OK, EXIT_FAIL, EXIT_REFUSE = 0, 1, 2

# The production reader.  Named at module level so a control can substitute a
# BLIND reader and drive THIS function -- §2p.3(d), the production path, not a copy.
READER = A.T1C.iterative_convergence


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def _checkpoints(case_dir):
    import re
    return sorted((x for x in os.listdir(case_dir)
                   if re.fullmatch(r"\d+(\.\d+)?", x) and float(x) > 0), key=float)


def planted_zero_control_p2(case_dir):
    """THE REPAIRED RULE-3 CONTROL.  Returns a dict; `passed` is True only if the
    reader's maximum change IS the change at the cell this function planted.

    The run tree is never written: the last two checkpoints' T files are copied to
    a temp case and the plant goes into the copy (S-7)."""
    ts = _checkpoints(case_dir)
    if len(ts) < 2:
        return dict(passed=False, why="fewer than two checkpoints", limb_A=None, limb_B=None)
    tmp = tempfile.mkdtemp(prefix="t3c_plant_")
    try:
        work = os.path.join(tmp, os.path.basename(case_dir))
        if os.path.abspath(work).startswith(os.path.abspath(os.path.join(HERE, ""))
                                            ) and "runs" in os.path.abspath(work).split(os.sep):
            return dict(passed=False, why="S-7: scratch path resolves inside the run tree",
                        limb_A=None, limb_B=None)
        for t in ts[-2:]:
            os.makedirs(os.path.join(work, t))
            shutil.copy(os.path.join(case_dir, t, "T"), os.path.join(work, t, "T"))

        a_before = A.T1C.read_internal(os.path.join(work, ts[-2], "T"))
        b = A.T1C.read_internal(os.path.join(work, ts[-1], "T"))
        if not a_before or not b:                                  # S-8
            return dict(passed=False, why="S-8: empty internal field", limb_A=None, limb_B=None)
        if len(a_before) != len(b):                                # S-8
            return dict(passed=False, why="S-8: cell-count mismatch between checkpoints %d vs %d"
                        % (len(a_before), len(b)), limb_A=None, limb_B=None)

        rec = READER(work).get("max_change", 0.0)                  # UN-PLANTED baseline (S-6)

        # plant, in place in the COPY, and read it back from disk
        before, after = A.plant_into_T(os.path.join(work, ts[-2], "T"))
        a_after = A.T1C.read_internal(os.path.join(work, ts[-2], "T"))
        got_max = READER(work).get("max_change", 0.0)

        # the operands this control differences, and the ulp OF THOSE OPERANDS
        ulp = math.ulp(max(abs(a_after[0]), abs(b[0])))
        tol = N_ULP * ulp
        cell_diff = abs(a_after[0] - b[0])           # the planted cell's own change
        drift = a_before[0] - b[0]                   # the field's real change there

        # LIMB A is an IDENTITY, not a tolerance test: when the plant is the argmax,
        # got_max and cell_diff are the SAME subtraction and agree bit-for-bit
        # (measured: 0.00 ulp residual on R_m, R_f and R_ff).  A tolerance here
        # would let a DECOY cell whose change is merely NEAR the plant satisfy it,
        # which is the fail-open in a new dress -- see arm S-9.
        limb_A = (got_max == cell_diff)
        err_B = abs(got_max - A.PLANT)
        limb_B = err_B <= tol

        return dict(passed=bool(limb_A and limb_B), planted=A.PLANT,
                    read_back_delta=after - before, reader_max_change=got_max,
                    rec_unplanted=rec, planted_cell_change=cell_diff,
                    drift_at_planted_cell=drift, drift_ulp=(drift / ulp),
                    ulp_of_operands=ulp, N_ULP=N_ULP, tol_absolute=tol,
                    limb_A=bool(limb_A), limb_A_residual_ulp=(abs(got_max - cell_diff) / ulp),
                    limb_B=bool(limb_B), limb_B_error_ulp=(err_B / ulp),
                    reader_state=READER(work).get("state"), between=ts[-2:],
                    predicate="P-2 (VERIFICATION_CHARTER 2d.11.1); supersedes T3c 5.1 P-1")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def outlet_guard_from_record(root):
    """G4's extra NOT A RESULT input, from the graded record's own DO row."""
    p = os.path.join(root, "gate_t3.json")
    if not os.path.isfile(p):
        return None, "gate_t3.json absent: outlet-independence guard NOT MEASURED"
    try:
        g = json.load(open(p))
    except Exception as e:                                          # noqa: BLE001
        return None, "gate_t3.json does not parse (%s): outlet guard NOT MEASURED" % e
    for r in g.get("rows", []):
        if r.get("row") == "DO":
            return bool(r.get("criterion_met")), None
    return None, "gate_t3.json holds no DO row: outlet guard NOT MEASURED"


def grade(root, ladder=LADDER, out=print):
    missing = [c for c in ladder.values()
               if not os.path.isfile(os.path.join(root, "DONE.%s" % c))]
    if missing:
        refuse("no completion marker DONE.%s -- the triple is graded whole or not at all"
               % ", DONE.".join(missing))
    J_sec, SEC = A.load_secondary()
    PRIM = A.load_primary()

    pz = planted_zero_control_p2(os.path.join(root, ladder["m"]))
    out("rule-3 control (P-2) on %s:" % ladder["m"])
    for k in ("passed", "limb_A", "limb_A_residual_ulp", "limb_B", "limb_B_error_ulp",
              "drift_ulp", "N_ULP", "reader_max_change", "rec_unplanted", "read_back_delta"):
        out("    %-22s %r" % (k, pz.get(k)))
    if not pz.get("passed"):
        refuse("P-2 planted-zero control failed on %s (limb_A=%r limb_B=%r): the reader was "
               "not shown able to see ITS OWN plant; its zeros mean nothing"
               % (ladder["m"], pz.get("limb_A"), pz.get("limb_B")))
    # S-6 negative limb, on a REAL case only: a baseline that was never driven
    # establishes nothing, and must say so rather than pass.
    if pz.get("rec_unplanted") == 0.0:
        refuse("S-6: rec is exactly 0.0 on the real case %s -- the un-planted baseline was "
               "never driven, so the control has established nothing" % ladder["m"])

    M = {}
    for lv in LEVELS:
        out("measuring %s (level %s) ..." % (ladder[lv], lv))
        M[lv] = A.measure(os.path.join(root, ladder[lv]))
    conv = {lv: M[lv]["convergence_state"] for lv in LEVELS}
    r21, r32 = A.ratios_from_ncells(M)
    out("effective refinement ratios from nCells: r21 = %.4f, r32 = %.4f" % (r21, r32))
    if r21 <= 1.0 or r32 <= 1.0:
        refuse("the ladder does not refine: r21 = %.4f, r32 = %.4f" % (r21, r32))
    outlet_ok, outlet_note = outlet_guard_from_record(root)

    triples, rows = {}, []
    for key in ("St_peak", "x_peak_H", "St_10H", "St_20H", "x_R_H", "Cf_15H"):
        tr = A.triple_of(M, key)
        triples[key] = (dict(state="UNMEASURED", triple=list(tr)) if any(v is None for v in tr)
                        else dict(A.gci_unequal(*tr, r21, r32), triple=list(tr)))
    for rid, key in A.GRADED.items():
        extra = None
        if rid == "G4" and outlet_ok is False:
            extra = "outlet-independence test failed on the graded record (gate_t3.json row DO)"
        row = A.graded_verdict(rid, key, M["f"][key], A.triple_of(M, key), conv,
                               triples[key], PRIM, SEC[rid], extra)
        row.update(kind="GRADE", ladder=dict(ladder), decomposition_confound=CONFOUND,
                   P_MIN=P_MIN, outlet_guard_note=outlet_note)
        rows.append(row)
    rows.append(dict(row="M1", kind="REPORT", quantity="x_R_H", value=M["f"]["x_R_H"],
                     triple=list(A.triple_of(M, "x_R_H")), grid=triples["x_R_H"],
                     secondary=SEC["M1"], verdict="REPORTED", decomposition_confound=CONFOUND))

    st = {}
    p = os.path.join(root, "STATUS.%s" % ladder["f"])
    if os.path.isfile(p):
        for line in open(p):
            if "=" in line:
                k, v = line.strip().split("=", 1)
                st[k] = v
    cost = dict(R_fx_status=st, core_min_from_status=st.get("core_min"),
                cost_basis="wall x ranks / 60 from STATUS.R_fx; dollars derived, not measured")
    tally = {v: sum(1 for r in rows if r["kind"] == "GRADE" and r["verdict"] == v)
             for v in A.VERDICTS}
    result = dict(rung="T3d -- fourth level CONTINUED (R_fx), repaired rule-3 control", ladder=ladder,
                  comparator_of_record="analyse_t3.py blob d5e4a9eb (imported)",
                  this_file_sha256=A.sha256(os.path.abspath(__file__)),
                  Fs=A.FS, P_MIN=P_MIN, N_ULP=N_ULP,
                  refinement_ratios=dict(r21=r21, r32=r32), planted_zero_control=pz,
                  primary_present=PRIM is not None, decomposition_confound=CONFOUND,
                  measurements={ladder[lv]: {k: M[lv][k] for k in
                                ("nCells", "time", "convergence_state", "St_peak", "x_peak_H",
                                 "St_10H", "St_20H", "x_R_H", "Re_achieved", "yplus_min",
                                 "yplus_max", "delta99_floor_H")} for lv in LEVELS},
                  triples=triples, rows=rows, tally=tally, cost=cost,
                  generated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    out("\nladder (%s, %s, %s)  r21 = %.4f  r32 = %.4f  P_MIN = %.1f"
        % (ladder["c"], ladder["m"], ladder["f"], r21, r32, P_MIN))
    for r in rows:
        line = "  %-3s %-13s %-9s triple = %s  grid = %s" % (
            r["row"], r["verdict"], r["quantity"], [A.fmt(v) for v in r["triple"]],
            r["grid"].get("state"))
        if "order" in r["grid"]:
            line += "  p = %.3f" % r["grid"]["order"]
        if "GCI_pct" in r:
            line += "  GCI = %.3f %%" % r["GCI_pct"]
        if "why" in r:
            line += "  [" + r["why"] + "]"
        out(line)
    out("tally " + json.dumps(tally))
    out("CAVEAT " + CONFOUND)
    return result


# ---------------------------------------------------------------------------
# synthetic cases for the registered arms -- written by this file, read by the
# production reader.  A scratch case is NOT a substitute for the real path; the
# real path is exercised by the R_c / R_m / R_f arms in control_t3c_p2.py.
# ---------------------------------------------------------------------------
def write_case(root, base=300.0, drift_ulp=0.0, n=50,
               decoy_cell=None, decoy_change=0.0):
    """Two checkpoints; cell 0 of the EARLIER one sits `drift_ulp` ulp above the
    later one, every other cell identical.

    `decoy_cell` / `decoy_change` plant a change at a DIFFERENT cell, to build the
    S-9 case: a cell whose change is close enough to PLANT that LIMB B cannot tell
    them apart, but which is not the cell the control planted."""
    u = math.ulp(base)
    later = [base + 0.01 * i for i in range(n)]
    earlier = list(later)
    earlier[0] = later[0] + drift_ulp * u
    if decoy_cell is not None:
        earlier[decoy_cell] = later[decoy_cell] + decoy_change
    for t, vals in (("2000", earlier), ("4000", later)):
        d = os.path.join(root, t)
        os.makedirs(d)
        open(os.path.join(d, "T"), "w").write(
            "FoamFile\n{\n    version 2.0;\n    format ascii;\n    class volScalarField;\n"
            "    object T;\n}\ndimensions [0 0 0 1 0 0 0];\n"
            "internalField nonuniform List<scalar>\n%d\n(\n" % n
            + "\n".join(repr(v) for v in vals) + "\n)\n;\n")
    return root


def selftest():
    fails = []

    def check(name, ok, detail=""):
        print("  [%s] %s %s" % ("ok" if ok else "FAIL", name, detail))
        if not ok:
            fails.append(name)

    # ---- S-2: both signs of checkpoint drift, the arm the parent never drove ----
    for d in (-7.0, 0.0, 7.0, 21.0):
        tmp = tempfile.mkdtemp(prefix="t3c_s2p_")
        try:
            pz = planted_zero_control_p2(write_case(os.path.join(tmp, "c"), drift_ulp=d))
            check("S-2 POSITIVE drift %+5.0f ulp -> PASS" % d, pz["passed"] is True,
                  "got %r  err %.2f ulp" % (pz["reader_max_change"], pz["limb_B_error_ulp"]))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    tmp = tempfile.mkdtemp(prefix="t3c_s2n_")
    try:
        pz = planted_zero_control_p2(write_case(os.path.join(tmp, "c"), drift_ulp=200.0))
        check("S-2 NEGATIVE drift +200 ulp -> REFUSE", pz["passed"] is False,
              "err %.2f ulp against N_ULP %d" % (pz["limb_B_error_ulp"], N_ULP))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ---- S-5: binade independence -- the tolerance must follow the operands ----
    for base in (48.0, 96.0, 384.0, 768.0, 3072.0):
        tmp = tempfile.mkdtemp(prefix="t3c_s5_")
        try:
            pz = planted_zero_control_p2(write_case(os.path.join(tmp, "c"), base=base,
                                                    drift_ulp=7.0))
            check("S-5 binade base %7.1f -> PASS" % base, pz["passed"] is True,
                  "ulp %r  err %.2f ulp" % (pz["ulp_of_operands"], pz["limb_B_error_ulp"]))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    # ---- S-1: the plant is read back from disk ----
    tmp = tempfile.mkdtemp(prefix="t3c_s1_")
    try:
        pz = planted_zero_control_p2(write_case(os.path.join(tmp, "c")))
        check("S-1 plant read back from disk to within 1e-12",
              abs(pz["read_back_delta"] - A.PLANT) < 1e-12, "%r" % pz["read_back_delta"])
        check("S-1 rec is the UN-PLANTED reading and is not the planted one (S-6)",
              pz["rec_unplanted"] < A.PLANT / 2.0, "rec %r" % pz["rec_unplanted"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ---- S-9: A DECOY CELL WITHIN LIMB B's TOLERANCE MUST NOT BE CREDITED ----
    # This is the arm that makes LIMB A load-bearing.  R_c is refused by LIMB B
    # alone (its max is 2000x the plant), so R_c does NOT demonstrate LIMB A.
    # Here another cell changes by PLANT + 20 ulp: LIMB B cannot tell it from the
    # plant, and only the identity limb catches that the plant was not the argmax.
    tmp = tempfile.mkdtemp(prefix="t3c_s9_")
    try:
        c = write_case(os.path.join(tmp, "c"), decoy_cell=7,
                       decoy_change=A.PLANT + 20.0 * math.ulp(300.0))
        pz = planted_zero_control_p2(c)
        check("S-9 decoy cell within LIMB B tolerance -> REFUSE", pz["passed"] is False,
              "limb_A=%s limb_B=%s (err %.2f ulp, INSIDE N_ULP=%d)"
              % (pz["limb_A"], pz["limb_B"], pz["limb_B_error_ulp"], N_ULP))
        check("S-9 refuses on LIMB A, and LIMB B alone would have PASSED it",
              pz["limb_A"] is False and pz["limb_B"] is True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ---- S-8: schema integrity ----
    tmp = tempfile.mkdtemp(prefix="t3c_s8_")
    try:
        c = write_case(os.path.join(tmp, "c"))
        open(os.path.join(c, "2000", "T"), "w").write(
            "FoamFile\n{\n    class volScalarField;\n    object T;\n}\n"
            "internalField nonuniform List<scalar>\n0\n(\n)\n;\n")
        pz = planted_zero_control_p2(c)
        check("S-8 empty internal field -> REFUSE", pz["passed"] is False, pz.get("why", ""))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ---- the verdict logic is the frozen module's and is re-exercised ----
    conv_ok = {lv: "CONVERGED" for lv in LEVELS}
    r21, r32 = 1.5989, 1.6000
    sec = dict(value=6.2, increment=0.05)
    tr = (6.135162, 6.141197, 6.143560)
    g = A.gci_unequal(*tr, r21, r32)
    check("P1-shaped triple CONVERGING, p in [0.5, 3]",
          g["state"] == "CONVERGING" and 0.5 <= g["order"] <= 3.0,
          "p = %.3f" % g.get("order", float("nan")))
    row = A.graded_verdict("G2", "x_peak_H", tr[2], tr, dict(conv_ok, f="NOT_CONVERGED"),
                           g, None, sec)
    check("a level NOT_CONVERGED -> NOT A RESULT at gate (1)",
          row["verdict"] == "NOT A RESULT" and "level f" in row["why"], row.get("why", ""))
    check("verdict vocabulary closed",
          all(v in A.VERDICTS for v in ("PASS", "GATE FAIL", "NOT A RESULT", "BLOCKED",
                                        "REPORTED", "PENDING")))

    # ---- refusal on an absent DONE marker, driven through grade() ----
    tmp = tempfile.mkdtemp(prefix="t3c_done_")
    try:
        for c in ("R_m", "R_f"):
            open(os.path.join(tmp, "DONE.%s" % c), "w").write("forged\n")
        code = None
        try:
            grade(tmp, out=lambda *a, **k: None)
        except SystemExit as e:
            code = e.code
        check("absent DONE.R_ff -> refusal exit 2", code == EXIT_REFUSE, "exit %s" % code)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("SELFTEST %s (%d checks failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return EXIT_OK if not fails else EXIT_FAIL


def main(argv):
    if "--selftest" in argv:
        return selftest()
    root = os.path.abspath(argv[argv.index("--root") + 1]) if "--root" in argv else HERE
    res = grade(root)
    json.dump(res, open(GATE_JSON, "w"), indent=2)
    print("wrote %s" % GATE_JSON)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
