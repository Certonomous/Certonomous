#!/usr/bin/env python3
"""T3 fourth-level comparator: the triple (R_m, R_f, R_ff) on EXACTLY the frozen
analyse_t3.py's row definitions, refinement-ratio handling and Roache gating.

Registered by T3_R_FF_PREREGISTRATION.md AMENDMENT 1, frozen BEFORE R_ff has
iterated.  The frozen analyse_t3.py (HEAD blob d5e4a9eb) is IMPORTED, never
edited: its LADDER is hard-wired to (R_c, R_m, R_f) and it refuses without all
eight DONE markers, so it cannot grade this triple; everything it exposes is
reused here rather than re-implemented --
  A.measure               the per-case reader (St, x_peak, stations, y+, heat balance,
                          convergence state) -- THE reader every graded number passes through
  A.planted_zero_control  rule 3, PLANT = 1.234e-03 K, planted into the medium level
  A.gci_unequal           Celik unequal-ratio order + GCI, Fs = 1.25; its `p < 0.5 ->
                          STAGNANT` branch IS the observed-order floor P_MIN = 0.5 that
                          T11 adopted at 352aef0d -- stated here, not re-implemented
  A.graded_verdict        the ordered gate (1) level not CONVERGED (2) triple not
                          CONVERGING (2b) outlet test (3) no primary -> BLOCKED (4) band
  A.load_secondary / A.load_primary / A.GRADED / A.VERDICTS / A.fmt / A.rel
What is NOT reused, and why: main()'s ladder wiring (hard-coded to c/m/f) and its
eight-case loop; read_status (it parses the single-line T1b pool format, and
launch_t3_rff.sh writes key=value lines).  The G4 outlet-independence input
(O_m vs R_m) is a measurement of the graded record, read from gate_t3.json row
DO, not re-measured.
Output: gate_t3_rff.json beside this file (gate_t3.json is never written).
Exit 0 ran, 1 selftest failed, 2 refusal.  Zero `assert` statements (L-332).
"""
import datetime, json, math, os, shutil, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyse_t3 as A          # frozen comparator, HEAD blob d5e4a9eb -- imported, not edited

LADDER = {"c": "R_m", "m": "R_f", "f": "R_ff"}
LEVELS = A.LEVELS
P_MIN = 0.5                     # the floor A.gci_unequal applies (STAGNANT below it); T11 352aef0d
GATE_JSON = os.path.join(HERE, "gate_t3_rff.json")
CONFOUND = ("R_ff ran decomposed (8 ranks, simple (8 1 1)); R_m and R_f ran serial. "
            "The triple carries ONE non-mesh difference, floating-point summation order "
            "(F15 RULING 2, T3_R_FF_PREREGISTRATION.md S5). Quoted on every row.")
EXIT_OK, EXIT_FAIL, EXIT_REFUSE = 0, 1, 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def read_status_kv(root, case):
    p = os.path.join(root, "STATUS.%s" % case)
    if not os.path.isfile(p):
        return None
    d = {}
    for line in open(p):
        if "=" in line:
            k, v = line.strip().split("=", 1)
            d[k] = v
    return d


def outlet_guard_from_record(root):
    """G4's extra NOT A RESULT input, from the graded record's own DO row."""
    p = os.path.join(root, "gate_t3.json")
    if not os.path.isfile(p):
        return None, "gate_t3.json absent: outlet-independence guard NOT MEASURED for this triple"
    try:
        g = json.load(open(p))
    except Exception as e:                           # noqa: BLE001
        return None, "gate_t3.json does not parse (%s): outlet guard NOT MEASURED" % e
    for r in g.get("rows", []):
        if r.get("row") == "DO":
            return bool(r.get("criterion_met")), None
    return None, "gate_t3.json holds no DO row: outlet guard NOT MEASURED"


def grade(root, ladder=LADDER, out=print):
    missing = [c for c in ladder.values() if not os.path.isfile(os.path.join(root, "DONE.%s" % c))]
    if missing:
        refuse("no completion marker DONE.%s -- the triple is graded whole or not at all; "
               "mark_done_t3_rff.py (R_ff) / mark_done_t3_ext1.py (R_m, R_f) decide, "
               "and this reader does not overrule them" % ", DONE.".join(missing))
    J_sec, SEC = A.load_secondary()
    PRIM = A.load_primary()
    pz = A.planted_zero_control(os.path.join(root, ladder["m"]))
    out("planted-zero control on %s: %s" % (ladder["m"], pz))
    if not pz.get("passed"):
        refuse("planted-zero control failed: the convergence reader cannot see a %g K "
               "difference; its zeros mean nothing" % A.PLANT)
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
        if rid == "G4":
            if outlet_ok is False:
                extra = "outlet-independence test failed on the graded record (gate_t3.json row DO)"
        row = A.graded_verdict(rid, key, M["f"][key], A.triple_of(M, key), conv,
                               triples[key], PRIM, SEC[rid], extra)
        row.update(kind="GRADE", ladder=dict(ladder), decomposition_confound=CONFOUND,
                   P_MIN=P_MIN, outlet_guard_note=outlet_note)
        rows.append(row)
    rows.append(dict(row="M1", kind="REPORT", quantity="x_R_H", value=M["f"]["x_R_H"],
                     triple=list(A.triple_of(M, "x_R_H")), grid=triples["x_R_H"],
                     secondary=SEC["M1"], verdict="REPORTED", decomposition_confound=CONFOUND))
    st = read_status_kv(root, ladder["f"]) or {}
    cost = dict(R_ff_status=st, core_min_from_status=st.get("core_min"),
                cost_basis="wall x ranks / 60 from STATUS.R_ff; dollars derived, not measured")
    tally = {v: sum(1 for r in rows if r["kind"] == "GRADE" and r["verdict"] == v) for v in A.VERDICTS}
    result = dict(rung="T3 fourth level", ladder=ladder, comparator_of_record="analyse_t3.py blob d5e4a9eb (imported)",
                  this_file_sha256=A.sha256(os.path.abspath(__file__)), Fs=A.FS, P_MIN=P_MIN,
                  refinement_ratios=dict(r21=r21, r32=r32), planted_zero_control=pz,
                  primary_present=PRIM is not None, decomposition_confound=CONFOUND,
                  measurements={ladder[lv]: {k: M[lv][k] for k in ("nCells", "time", "convergence_state",
                                "St_peak", "x_peak_H", "St_10H", "St_20H", "x_R_H", "Re_achieved",
                                "yplus_min", "yplus_max", "delta99_floor_H")} for lv in LEVELS},
                  triples=triples, rows=rows, tally=tally, cost=cost,
                  generated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    out("\nladder (%s, %s, %s)  r21 = %.4f  r32 = %.4f  P_MIN = %.1f" % (ladder["c"], ladder["m"], ladder["f"], r21, r32, P_MIN))
    for r in rows:
        line = "  %-3s %-13s %-9s triple = %s  grid = %s" % (
            r["row"], r["verdict"], r["quantity"], [A.fmt(v) for v in r["triple"]], r["grid"].get("state"))
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


def selftest():
    fails = []
    def check(name, ok, detail=""):
        print("  [%s] %s %s" % ("ok" if ok else "FAIL", name, detail))
        if not ok:
            fails.append(name)
    conv_ok = {lv: "CONVERGED" for lv in LEVELS}
    r21, r32 = 1.5989, 1.6000
    sec = dict(value=6.2, increment=0.05)
    # (i) the registered P1 shape: x_peak/H (6.13516, 6.14120, 6.14356) -> CONVERGING p ~ 2 -> BLOCKED (no primary)
    tr = (6.135162, 6.141197, 6.143560)
    g = A.gci_unequal(*tr, r21, r32)
    row = A.graded_verdict("G2", "x_peak_H", tr[2], tr, conv_ok, g, None, sec)
    check("P1-shaped triple CONVERGING, p in [0.5, 3]", g["state"] == "CONVERGING" and 0.5 <= g["order"] <= 3.0,
          "p = %.3f" % g.get("order", float("nan")))
    check("no primary -> BLOCKED (V/G only)", row["verdict"] == "BLOCKED", row.get("why", ""))
    # (ii) the P2 shape: equal steps -> STAGNANT (p < P_MIN = 0.5) -> NOT A RESULT, no GCI
    tr = (0.00343791, 0.00350859, 0.00357927)
    g = A.gci_unequal(*tr, r21, r32)
    row = A.graded_verdict("G1", "St_peak", tr[2], tr, conv_ok, g, None, sec)
    # the frozen reader returns DIVERGENT at p = 0 for exactly equal steps and STAGNANT for 0 < p < P_MIN;
    # both are NOT A RESULT and neither carries a GCI -- the floor is checked separately in (iii)
    check("equal-step triple -> DIVERGENT/STAGNANT, p < P_MIN", g["state"] in ("DIVERGENT", "STAGNANT") and g["order"] < P_MIN,
          "state %s p = %.4f" % (g["state"], g["order"]))
    check("-> NOT A RESULT with no GCI", row["verdict"] == "NOT A RESULT" and "GCI_pct" not in row)
    # (iii) p just above the floor is CONVERGING; just below is STAGNANT (the floor is live)
    def triple_for_p(p):
        e21 = 1e-3; e32 = e21 * r21 ** p
        return (1.0 + e21 + e32, 1.0 + e21, 1.0)
    ga, gb = A.gci_unequal(*triple_for_p(0.6), r21, r32), A.gci_unequal(*triple_for_p(0.4), r21, r32)
    check("p = 0.6 -> CONVERGING, p = 0.4 -> STAGNANT", ga["state"] == "CONVERGING" and gb["state"] == "STAGNANT",
          "%s / %s" % (ga["state"], gb["state"]))
    # (iv) a level NOT_CONVERGED beats a CONVERGING triple
    row = A.graded_verdict("G2", "x_peak_H", 6.14356, (6.135162, 6.141197, 6.143560),
                           dict(conv_ok, f="NOT_CONVERGED"), ga, None, sec)
    check("R_ff NOT_CONVERGED -> NOT A RESULT at gate (1)", row["verdict"] == "NOT A RESULT" and "level f" in row["why"])
    # (v) DIVERGENT and OSCILLATORY -> NOT A RESULT
    for label, tr in (("DIVERGENT", (1.00, 1.02, 1.05)), ("OSCILLATORY", (1.00, 1.10, 1.05))):
        g = A.gci_unequal(*tr, r21, r32)
        row = A.graded_verdict("G1", "St_peak", tr[2], tr, conv_ok, g, None, sec)
        check("%s -> NOT A RESULT" % label, g["state"] == label and row["verdict"] == "NOT A RESULT")
    # (vi) G4 outlet guard from the record: False forces NOT A RESULT
    row = A.graded_verdict("G4", "St_20H", 1.0, triple_for_p(2.0), conv_ok, ga, None, sec,
                           extra_not_a_result="outlet-independence test failed")
    check("outlet guard failed -> NOT A RESULT", row["verdict"] == "NOT A RESULT")
    check("verdict vocabulary closed", all(v in A.VERDICTS for v in ("PASS", "GATE FAIL", "NOT A RESULT", "BLOCKED", "REPORTED", "PENDING")))
    # (vii) refusal on an absent DONE marker, driven in a scratch root (exit 2 through grade())
    tmp = tempfile.mkdtemp(prefix="t3rff_self_")
    try:
        for c in ("R_m", "R_f"):
            open(os.path.join(tmp, "DONE.%s" % c), "w").write("forged\n")
        code = None
        try:
            grade(tmp, out=lambda *a, **k: None)
        except SystemExit as e:
            code = e.code
        check("absent DONE.R_ff -> refusal exit 2", code == EXIT_REFUSE, "exit %s" % code)
        # (viii) planted-zero machinery: a plant is seen; the un-planted copy returns 0 (negative arm)
        case = os.path.join(tmp, "R_x")
        body = ("FoamFile\n{\n    version 2.0;\n    format ascii;\n    class volScalarField;\n"
                "    object T;\n}\ndimensions [0 0 0 1 0 0 0];\ninternalField nonuniform List<scalar>\n50\n(\n"
                + "\n".join(repr(300.0 + 0.01 * i) for i in range(50)) + "\n)\n;\n")
        for t in ("2000", "4000"):
            os.makedirs(os.path.join(case, t)); open(os.path.join(case, t, "T"), "w").write(body)
        pz = A.planted_zero_control(case)
        check("plant of %g K seen by the reader" % A.PLANT, pz.get("passed") is True and abs(pz["read_back_delta"] - A.PLANT) < 1e-12,
              "read back %s" % pz.get("read_back_delta"))
        c0 = A.T1C.iterative_convergence(case)
        check("negative arm: identical checkpoints read as change 0", c0.get("max_change", 1.0) == 0.0, str(c0.get("max_change")))
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
