#!/usr/bin/env python3
"""D18R-P7 SUCCESSOR COMPARATOR -- re-grades ONE prediction, P7, of curriculum item D18
from D18's PRESERVED grade JSON.  Zero solver compute.  It does not re-run physics, does
not re-mesh, does not re-read a solver log, and IT DOES NOT TOUCH THE ITEM VERDICT.

WHY IT EXISTS (the defect, verified against the frozen file at md5
e4ade11ed9e3db18d2c4988b30e929b4, disk == HEAD blob):

  d18_grade.py:581   worst_div   = max(d["divergence_pct"] for d in div)      <-- NO verdict filter
  d18_grade.py:582   pc          = [c for c in PATCHED components if isinstance(rel_err_pct, num)]
  d18_grade.py:583   worst_noise = max(c["rel_err_pct"] for c in pc)          <-- graded-only
  d18_grade.py:588   sn          = worst_div / worst_noise

  The two halves of one ratio are filtered ASYMMETRICALLY.  The numerator sweeps every
  registered component including those the SAME grader has already declared unreadable
  (NOT A RESULT), while the denominator sweeps only components it could read.  On D18 the
  entire P7 signal (64.3953 %) is shape[3] -- the component BOTH rows graded NOT A RESULT
  (NO_PLATEAU; neighbour disagreements 1572.6916 % / 195.6583 % against a 10 % plateau
  rule).  So P7 was scored on a number the item itself refuses to stand behind.

THE CORRECTED COMPOSITION RULE (registered in PREREGISTRATION.md section 4, frozen):
  GRADED(row)  = registered components whose row verdict is in {PASS, GATE FAIL} AND whose
                 rel_err_pct is a number.  NOT A RESULT is the exclusion criterion; a
                 GATE FAIL component is a MEASURED disagreement and stays in.
  SIGNAL_SET   = GRADED(SHIPPED) intersect GRADED(PATCHED) intersect COMPONENTS_REGISTERED
  worst_div    = max divergence_pct over SIGNAL_SET          (this is the repair)
  worst_noise  = max rel_err_pct over GRADED(PATCHED)        (unchanged -- already graded-only)
  sn           = worst_div / worst_noise
  P7           = HIT if sn <= P7_SN_MIN_TO_DISCRIMINATE (1.0) else MISS

WHAT THIS COMPARATOR MAY NOT CONCLUDE, stated so no reader can borrow more than it bought:
  * NOTHING about the physics.  No solver ran.  The cone, the shock, the Mach number and
    the perfect-gas caveat are exactly as D18 left them.
  * NOTHING about the mesh.  One mesh, 40,000 cells, no grid family, NO GCI IS QUOTED.
  * NOTHING about the SHIPPED-vs-PATCHED toolchain comparison as a physical finding.  A
    corrected S/N <= 1 says the two rows are NOT distinguishable ABOVE THE COMMON-MODE FD
    NOISE on the graded components; it does not say the two builds are identical, and it
    says nothing at all about shape[3], which remains unreadable in both rows.
  * NOTHING about D18's item verdict, its rows, or any gate.  It re-grades ONE registered
    prediction and reports the move.
  * It buys no new capability-grid cell and moves no census.

THE ITEM VERDICT CANNOT MOVE, AND THIS COMPARATOR PROVES IT RATHER THAN ASSERTING IT.
d18_grade.py:596-601 composes the item verdict from exactly six readings -- the two row
verdicts, G-M2, G9, G10, G12.  `preds` is NOT in that expression; it is serialised into the
output dict afterwards and never read back.  recompose_item_verdict() below re-evaluates
that expression from the preserved JSON's own gate fields and REFUSES if the result differs
from the JSON's recorded verdict.  Unit U6 drives the recomposer to a DIFFERENT answer on a
producer-built fixture, so a recomposer that merely echoes the input is caught.

BIRTH REQUIREMENT (Sanaa 2026-08-28; rule 3's question made a precondition), and the lane
sharpening that a ONE-DIRECTIONAL control certifies only half an instrument:
every planted control below is written by the REAL PRODUCER -- d18_grade.py's own _fix()
fixture builder and its own grade() -- and read back through THIS reader, in BOTH
directions on the same code path:
  MUST-FLAG    (U4): a divergence planted on a component GRADED in both rows.  The reader
                     must INCLUDE it and P7 must move to MISS.
  MUST-NOT-FLAG(U3): a divergence planted on a component NOT A RESULT in both rows.  The
                     reader must EXCLUDE it and stay HIT -- and the ORIGINAL formula is
                     evaluated on the SAME producer-emitted JSON and shown to say MISS, so
                     the defect is demonstrated live rather than argued.
A reader that always flags fails U3; a reader that never flags fails U4; a reader that
hard-codes D18's numbers fails U1.

L-332: NO `assert` anywhere; the module counts ast.Assert nodes in its own source and
refuses on any.  No unconditional success print.
"""
import ast
import json
import os
import sys

ITEM_EXPECTED = "CURRICULUM-D18"
COMPONENTS_REGISTERED = [["shape", 0], ["shape", 1], ["shape", 3], ["shape", 4], ["shape", 5]]
P7_SN_MIN_TO_DISCRIMINATE = 1.0          # D18 PREREGISTRATION.md; d18_grade.py:108, unchanged
GRADED_VERDICTS = ("PASS", "GATE FAIL")
VOCAB = {"PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"}
EXPECTED_UNITS = 13
D18_DIR = "/home/ubuntu/Certonomous/cases/dafoam/curriculum_D18_cone_hypersonic"
D18_GRADE_MD5_REGISTERED = "e4ade11ed9e3db18d2c4988b30e929b4"


class Refusal(Exception):
    pass


def refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail}, sort_keys=True, default=str))


def count_asserts(path):
    return sum(1 for n in ast.walk(ast.parse(open(path).read())) if isinstance(n, ast.Assert))


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def graded_keys(gate):
    """Components of one row that the ROW ITSELF could read: verdict graded AND rel_err numeric."""
    out = {}
    for c in gate["G5_CD"]["components"]:
        k = (c.get("dv"), c.get("idx"))
        if c.get("verdict") in GRADED_VERDICTS and _num(c.get("rel_err_pct")):
            out[k] = float(c["rel_err_pct"])
    return out


def recompose_item_verdict(r):
    """Re-evaluate d18_grade.py:596-601 from the preserved JSON's OWN gate fields.
    `preds` is absent from this expression -- that absence is the proof P7 cannot move it."""
    g = r["gates"]
    rows = (r["rows"]["SHIPPED"], r["rows"]["PATCHED"])
    six = (rows[0], rows[1], g["G-M2_mesh_identity"], g["G9_toolchain"]["verdict"],
           g["G10_caps"]["verdict"], g["G12_placement"]["verdict"])
    if "NOT A RESULT" in rows:
        v = "NOT A RESULT"
    elif "GATE FAIL" in six:
        v = "GATE FAIL"
    else:
        v = "PASS"
    if v not in VOCAB:
        refuse("VOCAB", {"verdict": v})
    return v, list(six)


def regrade_p7(r):
    if r.get("item") != ITEM_EXPECTED:
        refuse("WRONG_ITEM", {"item": r.get("item"), "expected": ITEM_EXPECTED})
    for k in ("gates", "rows", "predictions", "divergence_shipped_vs_patched_CD"):
        if k not in r:
            refuse("MISSING_KEY", {"key": k})
    div = r["divergence_shipped_vs_patched_CD"]
    if not div:
        refuse("NO_DIVERGENCE_ENTRIES", {"n": 0})
    gs, gp = graded_keys(r["gates"]["G5_SHIPPED"]), graded_keys(r["gates"]["G5_PATCHED"])
    reg = {(dv, idx) for dv, idx in COMPONENTS_REGISTERED}
    signal_set = sorted(set(gs) & set(gp) & reg)
    if not signal_set:
        refuse("EMPTY_SIGNAL_SET", {"graded_shipped": sorted(gs), "graded_patched": sorted(gp)})
    if not gp:
        refuse("NO_NOISE_TERM", {"graded_patched": []})
    dmap = {(d["dv"], d["idx"]): float(d["divergence_pct"]) for d in div}
    missing = [list(k) for k in signal_set if k not in dmap]
    if missing:
        refuse("SIGNAL_COMPONENT_HAS_NO_DIVERGENCE_ENTRY", {"missing": missing})
    worst_noise = max(gp.values())
    if worst_noise == 0.0:
        refuse("ZERO_NOISE_TERM", {"worst_noise": worst_noise})
    kd = max(signal_set, key=lambda k: dmap[k])
    worst_div = dmap[kd]
    sn = worst_div / worst_noise
    p7 = "HIT" if sn <= P7_SN_MIN_TO_DISCRIMINATE else "MISS"
    # ---- the ORIGINAL (defective) formula, evaluated on the SAME artefact, for the move
    o_worst_div = max(dmap.values())
    o_kd = max(dmap, key=lambda k: dmap[k])
    o_sn = o_worst_div / worst_noise
    o_p7 = "HIT" if o_sn <= P7_SN_MIN_TO_DISCRIMINATE else "MISS"
    excluded = sorted([k for k in dmap if k not in signal_set], key=lambda k: -dmap[k])
    recomposed, six = recompose_item_verdict(r)
    if recomposed != r["verdict"]:
        refuse("ITEM_VERDICT_RECOMPOSITION_DISAGREES",
               {"recomposed": recomposed, "recorded": r["verdict"], "six_inputs": six})
    return {"item": "%s-R-P7" % ITEM_EXPECTED,
            "subject": "ONE registered prediction (P7) of %s, re-graded from its preserved grade JSON" % ITEM_EXPECTED,
            "P7_original_recorded": r["predictions"].get("P7_two_rows_NOT_discriminating"),
            "P7_original_recomputed": o_p7,
            "P7_corrected": p7,
            "moved": o_p7 != p7,
            "sn_original": o_sn, "sn_corrected": sn,
            "signal_original_pct": o_worst_div, "signal_original_component": list(o_kd),
            "signal_corrected_pct": worst_div, "signal_corrected_component": list(kd),
            "noise_pct": worst_noise, "noise_component": list(max(gp, key=lambda k: gp[k])),
            "signal_set": [list(k) for k in signal_set],
            "excluded_components": [{"component": list(k), "divergence_pct": dmap[k],
                                     "shipped_verdict": _v(r, "G5_SHIPPED", k),
                                     "patched_verdict": _v(r, "G5_PATCHED", k)} for k in excluded],
            "threshold_P7_SN_min_to_discriminate": P7_SN_MIN_TO_DISCRIMINATE,
            "item_verdict_UNCHANGED": r["verdict"],
            "item_verdict_recomposed_from_the_six_registered_inputs": recomposed,
            "item_verdict_composition_inputs": six,
            "item_verdict_note": "d18_grade.py:596-601 reads two row verdicts, G-M2, G9, G10, G12 "
                                 "and NOTHING from `preds`; P7 is structurally incapable of moving it. "
                                 "Recomposed here from the preserved JSON and matched to the recorded verdict.",
            "buys_nothing_about": ["physics", "mesh", "grid convergence (no grid family; NO GCI)",
                                   "the shipped-vs-patched toolchain comparison as a physical finding",
                                   "the capability grid census"]}


def _v(r, gk, key):
    for c in r["gates"][gk]["G5_CD"]["components"]:
        if (c.get("dv"), c.get("idx")) == key:
            return c.get("verdict")
    return None


# ================= selftest: every fixture EMITTED BY THE REAL PRODUCER ==================
def _producer():
    """Import the REAL producer.  Bytecode writing is disabled first so that importing a
    FROZEN case's comparator cannot drop a __pycache__ into its directory (rule 6: a frozen
    file's directory is not a scratch area), and so no stale bytecode can invert a unit."""
    sys.dont_write_bytecode = True
    if D18_DIR not in sys.path:
        sys.path.insert(0, D18_DIR)
    import d18_grade
    return d18_grade


def _drive(D18, tmp, tweak=None, scale=None):
    """Build a fixture with the REAL producer's own _fix(), optionally scale one SHIPPED
    adjoint component IN THE ARTEFACT THE PRODUCER WROTE, then run the REAL grade()."""
    root = D18._fix(tmp, tweak)
    if scale:
        (dv, idx), f = scale
        p = os.path.join(root, "X-S", "d18_X.json")
        d = json.load(open(p))
        d["adjoint"]["CD"][dv][idx] = repr(float(d["adjoint"]["CD"][dv][idx]) * f)
        json.dump(d, open(p, "w"))
    return D18.grade(root)


def selftest(tmp):
    n = 0
    fails = []

    def unit(name, cond):
        nonlocal n
        n += 1
        if not cond:
            fails.append(name)
        print("  [%s] %s" % ("OK " if cond else "BAD", name))

    def refused(fn):
        try:
            fn()
            return False
        except Refusal:
            return True

    D18 = _producer()

    def tw(**kw):
        def f(k):
            for key, val in kw.items():
                if isinstance(val, dict) and isinstance(k.get(key), dict):
                    k[key].update(val)
                else:
                    k[key] = val
        return f

    # ---- U1 clean producer fixture: no divergence anywhere, nothing excluded
    r = _drive(D18, tmp)
    a = regrade_p7(r)
    unit("U1 CLEAN producer fixture -> P7 HIT under both formulas, S/N 0.0, NOTHING excluded "
         "(the exclusion machinery is not always-on, and this reader is not hard-coded to D18)",
         a["P7_corrected"] == "HIT" and a["P7_original_recomputed"] == "HIT"
         and a["sn_corrected"] == 0.0 and a["excluded_components"] == [] and a["moved"] is False)

    # ---- U2 THE REAL PRESERVED ARTEFACT
    land = json.load(open(LANDED))
    b = regrade_p7(land)
    unit("U2 THE PRESERVED D18 ARTEFACT -> P7 MOVES MISS(S/N 19.8691, signal shape[3]) -> "
         "HIT(S/N 0.1383, signal shape[1] 0.4482626682 %, noise shape[0] 3.2409827589 %)",
         b["P7_original_recorded"] == "MISS" and b["P7_original_recomputed"] == "MISS"
         and b["P7_corrected"] == "HIT" and b["moved"] is True
         and round(b["sn_original"], 4) == 19.8691 and round(b["sn_corrected"], 4) == 0.1383
         and b["signal_corrected_component"] == ["shape", 1]
         and b["signal_original_component"] == ["shape", 3]
         and len(b["excluded_components"]) == 1
         and b["excluded_components"][0]["component"] == ["shape", 3]
         and b["excluded_components"][0]["shipped_verdict"] == "NOT A RESULT"
         and b["excluded_components"][0]["patched_verdict"] == "NOT A RESULT")

    # ---- U3 BIRTH, MUST-NOT-FLAG direction: huge divergence on an UNGRADED component
    r = _drive(D18, tmp, tw(noplateau={"S": {("shape", 3)}, "P": {("shape", 3)}}),
               scale=(("shape", 3), 1000.0))
    c = regrade_p7(r)
    unit("U3 BIRTH must-NOT-flag, PRODUCER-DRIVEN: a %.4f %% divergence planted on shape[3], "
         "NOT A RESULT in BOTH rows -> this reader EXCLUDES it and STAYS HIT (S/N %.4f); the "
         "ORIGINAL formula on the SAME producer-emitted JSON says MISS (S/N %.4f) -- the defect "
         "reproduced live, not argued"
         % (c["signal_original_pct"], c["sn_corrected"], c["sn_original"]),
         c["P7_corrected"] == "HIT" and c["P7_original_recomputed"] == "MISS" and c["moved"] is True
         and c["signal_original_component"] == ["shape", 3] and c["signal_original_pct"] > 99.0
         and c["excluded_components"][0]["component"] == ["shape", 3]
         and c["excluded_components"][0]["shipped_verdict"] == "NOT A RESULT")

    # ---- U4 BIRTH, MUST-FLAG direction: divergence on a component GRADED in both rows
    r = _drive(D18, tmp, scale=(("shape", 1), 1.5))
    d = regrade_p7(r)
    unit("U4 BIRTH must-FLAG, PRODUCER-DRIVEN: a %.4f %% divergence planted on shape[1], GRADED "
         "in BOTH rows -> this reader INCLUDES it and P7 moves to MISS (S/N %.4f). A reader that "
         "always excluded, or that never saw a non-zero, dies here"
         % (d["signal_corrected_pct"], d["sn_corrected"]),
         d["P7_corrected"] == "MISS" and d["signal_corrected_component"] == ["shape", 1]
         and d["signal_corrected_pct"] > 30.0 and d["sn_corrected"] > 1.0
         and d["excluded_components"] == [])

    # ---- U5/U6 the item-verdict recomposer, and proof it is not a constant
    unit("U5 item verdict recomposed from the SIX registered inputs on the preserved artefact "
         "equals the recorded PASS -- and `preds` is absent from that expression",
         b["item_verdict_UNCHANGED"] == "PASS" and b["item_verdict_recomposed_from_the_six_registered_inputs"] == "PASS"
         and len(b["item_verdict_composition_inputs"]) == 6)
    r = _drive(D18, tmp, tw(err={"S": {("shape", 4): 7.0}}))
    e = regrade_p7(r)
    unit("U6 PLANTED 7 %% FD error on SHIPPED shape[4] -> the producer's item verdict is GATE FAIL "
         "and the recomposer TRACKS it to GATE FAIL (so U5 is not an echo)",
         e["item_verdict_UNCHANGED"] == "GATE FAIL"
         and e["item_verdict_recomposed_from_the_six_registered_inputs"] == "GATE FAIL")

    # ---- U7-U11 refusals
    unit("U7 REFUSE: divergence list empty",
         refused(lambda: regrade_p7(dict(land, divergence_shipped_vs_patched_CD=[]))))
    unit("U8 REFUSE: PATCHED row has no graded component -> no noise term and no signal set "
         "(driven: all five components no-plateau on PATCHED)",
         refused(lambda: regrade_p7(_drive(D18, tmp, tw(noplateau={"P": {("shape", i) for i in (0, 1, 3, 4, 5)}})))))
    unit("U9 REFUSE: wrong item id", refused(lambda: regrade_p7(dict(land, item="CURRICULUM-D17"))))
    unit("U10 REFUSE: a required key absent",
         refused(lambda: regrade_p7({k: v for k, v in land.items() if k != "rows"})))
    unit("U11 REFUSE: the recorded item verdict disagrees with the recomposition -- this reader "
         "never publishes a verdict it cannot re-derive",
         refused(lambda: regrade_p7(dict(land, verdict="GATE FAIL"))))

    # ---- U12/U13 L-332
    here = os.path.abspath(__file__)
    unit("U12 ast.Assert count = 0 in d18r_p7_grade.py", count_asserts(here) == 0)
    p = os.path.join(tmp, "planted_assert.py")
    open(p, "w").write("x = 1\nassert x == 1\n")
    unit("U13 the assert counter SEES a planted assert (=1)", count_asserts(p) == 1)

    print("D18R-P7 SELFTEST units=%d expected=%d failures=%d python_O=%s"
          % (n, EXPECTED_UNITS, len(fails), not __debug__))
    if n != EXPECTED_UNITS or fails:
        print("SELFTEST FAIL: %s" % (fails or "unit count %d != %d" % (n, EXPECTED_UNITS)))
        return 2
    print("D18R-P7 SELFTEST PASS %d/%d (counted against the frozen EXPECTED_UNITS)" % (n, EXPECTED_UNITS))
    return 0


LANDED = "/home/ubuntu/certonomous-runs/CURRICULUM-D18-cone-hypersonic/D18_grade_20260828T032852Z.json"


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--grade-json", default=LANDED)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--tmpdir", default="/tmp")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if count_asserts(os.path.abspath(__file__)) != 0:
        print("REFUSAL: this comparator carries an assert statement (L-332)")
        return 2
    if a.selftest:
        d = os.path.join(a.tmpdir, "d18r_p7_selftest_%d" % os.getpid())
        os.makedirs(d, exist_ok=True)
        return selftest(d)
    try:
        r = regrade_p7(json.load(open(a.grade_json)))
    except Refusal as ex:
        print("REFUSAL: %s -> NOT A RESULT" % ex)
        if a.out:
            json.dump({"item": "%s-R-P7" % ITEM_EXPECTED, "verdict": "NOT A RESULT", "refusal": str(ex)},
                      open(a.out, "w"), indent=1)
        return 2
    r["source_grade_json"] = os.path.abspath(a.grade_json)
    print(json.dumps(r, indent=1, default=str))
    if a.out:
        json.dump(r, open(a.out, "w"), indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
