#!/usr/bin/env python3
"""MUTATION CONTROLS for the F6a / C-15 frozen pre-registration.

THE STANDARD THIS MEETS, and why it is not a formality.

`docs/NUMERICS_KNOWLEDGE.md` N-T8 (read from HEAD -- the worktree copy of that file
does NOT contain N-T8) records that four independent implementations in this lab got
a Richardson sign wrong the same way, and that the defect survived every run because
the frozen selftests **checked that a key EXISTED** rather than what its VALUE was.
N-T8's standing rule is that a control must check the VALUE, by construction.

The same disease has a second form here, and `VMFL045` is its case: its comparator
passed **45/45 with real negative controls** and could never have caught its crash,
because nothing in it exercised the thing that broke. **A selftest that only ever
passes proves the grader, not the case.**

So every frozen clause below carries BOTH ARMS:
  * a PASS arm -- the clause admits what it should admit; and
  * a FAIL arm that MUST ACTUALLY FLIP -- the clause refuses what it should refuse.

A clause with no failing control is a clause that cannot bind, and this file fails
if any FAIL arm does not flip.

ZERO SOLVER COMPUTE. No mesh is built, no `checkMesh` is run, no solver is started,
and nothing is created under `verification/runs/`. The final control asserts that.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))

# Stale bytecode inverts mutation tests: a clean control fails and a mutated case
# passes. PYTHONDONTWRITEBYTECODE does NOT fix it -- the caches must be removed.
for _root, _dirs, _files in os.walk(HERE):
    for _d in list(_dirs):
        if _d == "__pycache__":
            shutil.rmtree(os.path.join(_root, _d), ignore_errors=True)
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)

import f6a_greenblatt_gate as G      # noqa: E402
import run_f6a_greenblatt as L       # noqa: E402

REPO = G.REPO
RESULTS = []

# Snapshot the registered run roots BEFORE any control runs, so the zero-compute
# control tests what THIS FILE did rather than what the world looks like.
_ROOTS_AT_IMPORT = {d: os.path.exists(d) for d in L.RUN_ROOTS}


def control(clause, arm, description):
    def deco(fn):
        RESULTS.append((clause, arm, description, fn))
        return fn
    return deco


# ==========================================================================
# ss3.1 (P-a) -- residualControl TRIPPED, not the iteration cap reached
# ==========================================================================
def _log(converged_at, resid=None, times=None, end=True, initial_scale=1.0):
    resid = resid or {"Ux": 1e-8, "Uy": 1e-8, "p": 1e-8, "k": 1e-8, "omega": 1e-11}
    times = times or [converged_at if converged_at is not None else 2000]
    key = converged_at if converged_at is not None else times[-1]
    blocks = {key: {f: {"initial": v * initial_scale, "final": v * 1e-3}
                    for f, v in resid.items()}}
    return {"converged_at": converged_at, "times": times, "last_time": times[-1],
            "exec_count": times[-1], "has_end": end, "blocks": blocks}


@control("ss3.1 (P-a)", "PASS", "residualControl tripped at 1772 < cap 2000 -> admitted")
def pa_pass():
    ok, d = G.clause_p_a(_log(1772))
    assert ok is True, d
    return "converged_at=1772 cap=2000 -> ok"


@control("ss3.1 (P-a)", "FAIL", "run REACHED the iteration cap instead of converging -> REFUSED")
def pa_fail():
    ok, d = G.clause_p_a(_log(None, times=[2000]))
    assert ok is False, "a run that reached its cap was admitted as converged"
    assert "cap" in d["why"].lower() or "converged" in d["why"].lower()
    ok2, _ = G.clause_p_a(_log(2000))
    assert ok2 is False, "converged_at == cap must not be admitted"
    return "no-converged-line -> refused; converged_at==cap -> refused"


# ==========================================================================
# ss3.1 (P-b) -- INITIAL residuals, never Final
# ==========================================================================
@control("ss3.1 (P-b)", "PASS", "Initial residuals under the shipped controls -> admitted")
def pb_pass():
    ok, d = G.clause_p_b(_log(1772))
    assert ok is True, d
    assert d["asserts_reading_initial_column"] is True
    assert all(v["column_read"] == "Initial" for v in d["fields"].values())
    return "all Initial residuals under U/p/k 5e-7, omega 1e-10"


@control("ss3.1 (P-b)", "FAIL",
         "reader pointed at FINAL rather than INITIAL -> the clause must REFUSE, and a "
         "mutated Final-reading comparator must PASS the same fixture (the confusion "
         "this exact case has already paid for once)")
def pb_fail():
    # Initial ABOVE the control, Final BELOW it: the F6a_epistemic_band 1.0722 shape.
    lg = _log(1772, resid={"Ux": 1e-4, "Uy": 1e-4, "p": 1e-4, "k": 1e-4, "omega": 1e-4})
    ok, d = G.clause_p_b(lg)
    assert ok is False, "a run failing on INITIAL residuals was admitted"

    # THE MUTATION: a comparator that reads the Final column instead.
    blk = lg["blocks"][1772]
    mutated_ok = all(blk[f]["final"] <= lim
                     for f, lim in (("Ux", 5e-7), ("Uy", 5e-7), ("p", 5e-7), ("k", 5e-7)))
    assert mutated_ok is True, ("the fixture does not separate the two readings, so this "
                                "control would not catch the Initial/Final confusion")
    return ("Initial-reading REFUSES (correct); the mutated Final-reading comparator "
            "PASSES the same log -- the distinction bites")


@control("ss3.1 (P-b)", "FAIL", "missing residual line -> REFUSAL (exit 2), never a pass")
def pb_unevaluable():
    lg = _log(1772)
    lg["blocks"][1772].pop("omega")
    try:
        G.clause_p_b(lg)
    except G.Refusal as e:
        assert "unevaluable" in str(e).lower()
        return "missing omega residual -> Refusal raised"
    raise AssertionError("a missing residual line was not refused")


# ==========================================================================
# ss3.1 (P-c) -- THE GATED FUNCTIONAL ITSELF MUST BE FLAT
# ==========================================================================
def _samples(sep, rea):
    return [{"separation": s, "reattachment": r} for s, r in zip(sep, rea)]


@control("ss3.1 (P-c)", "PASS", "flat functional inside ptp 0.0033 / 0.0055 -> plateaued")
def pc_pass():
    sep = [0.6544 + 1e-5 * ((-1) ** i) for i in range(10)]
    rea = [1.2531 + 2e-5 * ((-1) ** i) for i in range(10)]
    ok, d = G.clause_p_c(_samples(sep, rea))
    assert ok is True, d
    return "ptp sep %.2e, rea %.2e" % (d["quantities"]["separation"]["ptp"],
                                       d["quantities"]["reattachment"]["ptp"])


@control("ss3.1 (P-c)", "FAIL",
         "functional STILL DRIFTING by a tenth of the gate band -> NOT PLATEAUED, "
         "whatever the residuals say (the clause VMFL051 needed)")
def pc_fail():
    sep = [0.6544] * 10
    rea = [1.2531 + 0.0012 * i for i in range(10)]     # ptp 0.0108 > 0.0055
    ok, d = G.clause_p_c(_samples(sep, rea))
    assert ok is False, "a drifting reattachment was called plateaued"
    assert d["quantities"]["reattachment"]["ptp"] > G.PTP_MAX["reattachment"]
    sep2 = [0.6544 + 0.0005 * i for i in range(10)]    # ptp 0.0045 > 0.0033
    ok2, _ = G.clause_p_c(_samples(sep2, [1.2531] * 10))
    assert ok2 is False, "a drifting separation was called plateaued"
    return "reattachment ptp 1.08e-2 refused; separation ptp 4.5e-3 refused"


@control("ss3.1 (P-c)", "FAIL", "fewer than 10 samples -> REFUSAL, not a pass")
def pc_unevaluable():
    try:
        G.clause_p_c(_samples([0.6544] * 9, [1.2531] * 9))
    except G.Refusal as e:
        assert "refusal" in str(e).lower() or "requires" in str(e).lower()
        return "9 samples -> Refusal raised"
    raise AssertionError("9 samples were graded")


@control("ss3.1 (P-c)", "FAIL",
         "sample-time selection refuses a run that cannot supply 10 samples on the "
         "50-iteration grid")
def pc_sample_times():
    got = G.sample_times(1772, list(range(50, 2001, 50)))
    assert got == [1300, 1350, 1400, 1450, 1500, 1550, 1600, 1650, 1700, 1750], got
    try:
        G.sample_times(1772, [1700, 1750])
    except G.Refusal:
        return "10 sample times selected on real cadence; a 2-sample cadence REFUSED"
    raise AssertionError("a 2-sample cadence was accepted")


# ==========================================================================
# ss3.1 (P-d) -- NO OSCILLATION
# ==========================================================================
@control("ss3.1 (P-d)", "PASS", "monotone approach with one turn -> admitted")
def pd_pass():
    rea = [1.2600, 1.2580, 1.2560, 1.2545, 1.2535, 1.2531, 1.2530, 1.2530, 1.2531, 1.2531]
    ok, d = G.clause_p_d(_samples([0.6544 - 1e-6 * i for i in range(10)], rea))
    assert ok is True, d
    return "sign alternations <= %d" % G.MAX_SIGN_ALTERNATIONS


@control("ss3.1 (P-d)", "FAIL",
         "OSCILLATING series -> REFUSED. VMFL051's triple was OSCILLATORY at R = -1.3486 "
         "and its deviation still read like a PASS on a -0.2337 %% band")
def pd_fail():
    rea = [1.2531 + 0.0002 * ((-1) ** i) for i in range(10)]   # 8 alternations
    ok, d = G.clause_p_d(_samples([0.6544] * 10, rea))
    assert ok is False, "an oscillating functional was admitted"
    assert d["quantities"]["reattachment"]["sign_alternations"] > G.MAX_SIGN_ALTERNATIONS
    return "8 sign alternations refused against a limit of %d" % G.MAX_SIGN_ALTERNATIONS


# ==========================================================================
# ss3.2 -- PLATEAU FIRST AND BINDING; rule 5's ONE-WAY DOOR
# ==========================================================================
@control("ss3.2", "PASS", "plateaued run is graded on its band (here: GATE FAIL at 1.2531)")
def ordering_pass():
    r = G.grade({"separation": 0.6544, "reattachment": 1.2531, "crest_xc": 0.5147},
                _samples([0.6544] * 10, [1.2531] * 10), _log(1772), True, {"seen": True})
    assert r["VERDICT"] == "GATE FAIL", r["VERDICT"]
    assert r["gates"]["P1_separation"]["verdict"] == "PASS"
    assert r["gates"]["P2_reattachment"]["verdict"] == "GATE FAIL"
    assert abs(r["gates"]["P2_reattachment"]["deviation_pct"] - 13.9182) < 1e-3
    return "P1 PASS, P2 GATE FAIL (+13.918 %), row GATE FAIL -- the forecast's OUTCOME A"


@control("ss3.2", "FAIL",
         "A DEVIATION INSIDE THE BAND ON A NON-PLATEAUED RUN IS `NOT A RESULT`, NEVER "
         "`PASS` -- the single control this clause exists for")
def ordering_fail():
    inside = {"separation": 0.6650, "reattachment": 1.1000, "crest_xc": 0.5147}
    # Same values, plateaued: would be a PASS. Establish that first, or the control
    # proves nothing.
    good = G.grade(inside, _samples([0.6650] * 10, [1.1000] * 10),
                   _log(1772), True, {"seen": True})
    assert good["VERDICT"] == "PASS", good["VERDICT"]
    # Now break ONLY the plateau. The deviation is untouched and is dead centre.
    drifting = _samples([0.6650] * 10, [1.1000 + 0.0012 * i for i in range(10)])
    bad = G.grade(inside, drifting, _log(1772), True, {"seen": True})
    assert bad["VERDICT"] == "NOT A RESULT", bad["VERDICT"]
    assert bad["gates"]["P2_reattachment"]["verdict"] == "PASS", (
        "the band verdict must still be printed beside the refusal")
    return ("identical dead-centre deviation: plateaued -> PASS, non-plateaued -> "
            "NOT A RESULT. The gate turned a PASS INTO NOT A RESULT, never the reverse")


@control("ss3.2", "FAIL", "ss9.4 completion failure alone forces NOT A RESULT")
def ordering_completion():
    inside = {"separation": 0.6650, "reattachment": 1.1000, "crest_xc": 0.5147}
    r = G.grade(inside, _samples([0.6650] * 10, [1.1000] * 10),
                _log(1772), False, {"seen": True})
    assert r["VERDICT"] == "NOT A RESULT", r["VERDICT"]
    return "completion_ok=False on a dead-centre deviation -> NOT A RESULT"


@control("rule 1", "PASS", "every verdict emitted lies inside the fixed vocabulary")
def vocabulary():
    seen = set()
    for compl, samp in ((True, _samples([0.6650] * 10, [1.1000] * 10)),
                        (False, _samples([0.6650] * 10, [1.1000] * 10)),
                        (True, _samples([0.6650] * 10, [1.1 + 0.002 * i for i in range(10)]))):
        seen.add(G.grade({"separation": 0.6650, "reattachment": 1.1000},
                         samp, _log(1772), compl, {"seen": True})["VERDICT"])
    assert seen <= set(G.VERDICTS), seen
    return "verdicts emitted: %s -- all inside rule 1's vocabulary" % sorted(seen)


# ==========================================================================
# ss2.2 -- the crest selection, the ONE ambiguous clause, resolved from geometry
# ==========================================================================
@control("ss2.2", "PASS", "crest read from wall GEOMETRY excludes the two spurious "
                          "near-zero crossings and admits the physical pair")
def crest_pass():
    crossings = [[-0.01290312390649109, "sep(+->-)"],
                 [0.007171228846393563, "reattach(-->+)"],
                 [0.6544112103270481, "sep(+->-)"],
                 [1.2534332991635089, "reattach(-->+)"]]
    x_s, x_r = G.select_bubble_pair(crossings, 0.5146595238095238)
    assert abs(x_s - 0.6544112) < 1e-6 and abs(x_r - 1.2534333) < 1e-6
    return "crest x/c 0.51466 -> pair (0.65441, 1.25343)"


@control("ss2.2", "FAIL",
         "WITHOUT the crest exclusion the reader returns the SPURIOUS near-zero pair -- "
         "so the exclusion is load-bearing, not decorative")
def crest_fail():
    crossings = [[-0.01290312390649109, "sep(+->-)"],
                 [0.007171228846393563, "reattach(-->+)"],
                 [0.6544112103270481, "sep(+->-)"],
                 [1.2534332991635089, "reattach(-->+)"]]
    x_s, x_r = G.select_bubble_pair(crossings, -99.0)
    assert abs(x_s - (-0.0129031)) < 1e-6, x_s
    assert abs(x_r - 0.0071712) < 1e-6, x_r
    # and the real crest is measured from geometry, not asserted
    raw = os.path.join(REPO, "cases/dafoam/f6a_nasa_hump/case/postProcessing/"
                             "wallValues/1772/wallShearStress_wallValues.raw")
    crest, zmax = G.wall_crest_xc(raw)
    assert abs(crest - 0.51466) < 1e-4, crest
    return ("crest -99 -> spurious pair (-0.01290, 0.00717); the geometric crest "
            "measures x/c %.5f at z_max %.6f" % (crest, zmax))


@control("ss2.2", "FAIL", "a first-crossing that is not a separation is REFUSED, not reinterpreted")
def crest_type_refusal():
    try:
        G.select_bubble_pair([[0.7, "reattach(-->+)"], [0.9, "sep(+->-)"]], 0.5)
    except G.Refusal:
        return "reattach-before-sep -> Refusal raised"
    raise AssertionError("a mistyped crossing pair was graded")


# ==========================================================================
# ss3.3 -- THE PLANTED-ZERO CONTROL, planted BY LINE INDEX
# ==========================================================================
@control("ss3.3", "PASS",
         "a known perturbation planted BY LINE INDEX into a copy of the trace comes "
         "back through the PINNED extractor")
def plant_pass():
    tmp = tempfile.mkdtemp(prefix="f6a_plant_")
    try:
        src = os.path.join(REPO, "cases/dafoam/f6a_nasa_hump/case/postProcessing/"
                                 "wallValues/1772")
        case = os.path.join(tmp, "case")
        dst = os.path.join(case, "postProcessing", "wallValues", "1772")
        os.makedirs(dst)
        for n in os.listdir(src):
            shutil.copy2(os.path.join(src, n), os.path.join(dst, n))
        d = G.plant_and_reread(case, 1772, tmp)
        assert d["seen"] is True
        assert d["crossings_after"] > d["crossings_before"]
        assert d["new_crossings_in_planted_range"]
        return ("line-index band %s -> x/c [%.4f, %.4f]; crossings %d -> %d; plant "
                "recovered" % (d["line_index_band"], d["planted_xc_range"][0],
                               d["planted_xc_range"][1], d["crossings_before"],
                               d["crossings_after"]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@control("ss3.3", "FAIL",
         "A BLIND READER -- one that cannot see the plant -- must REFUSE. A zero from a "
         "reader not shown able to see a non-zero is not evidence")
def plant_fail():
    tmp = tempfile.mkdtemp(prefix="f6a_blind_")
    real = G.run_extractor
    try:
        src = os.path.join(REPO, "cases/dafoam/f6a_nasa_hump/case/postProcessing/"
                                 "wallValues/1772")
        case = os.path.join(tmp, "case")
        dst = os.path.join(case, "postProcessing", "wallValues", "1772")
        os.makedirs(dst)
        for n in os.listdir(src):
            shutil.copy2(os.path.join(src, n), os.path.join(dst, n))
        frozen = real(case, 1772)

        # THE MUTATION: a reader that returns the same answer whatever is on disk.
        G.run_extractor = lambda c, t, repo=REPO: frozen
        try:
            G.plant_and_reread(case, 1772, tmp)
        except G.Refusal as e:
            assert "plant did not come back" in str(e).lower()
            return "blind reader -> REFUSAL; no gate verdict is written"
        raise AssertionError("a blind reader was allowed to grade")
    finally:
        G.run_extractor = real
        shutil.rmtree(tmp, ignore_errors=True)


@control("rule 2 / ss9.3", "FAIL",
         "a MUTATED extraction script fails its hash pin -> the campaign STOPS; the "
         "clause is not relaxed to match the code")
def pin_fail():
    tmp = tempfile.mkdtemp(prefix="f6a_pin_")
    try:
        fake = os.path.join(tmp, "cases/dafoam/f6a_nasa_hump/case")
        os.makedirs(fake)
        shutil.copy2(os.path.join(REPO, G.EXTRACTOR), os.path.join(fake, "hump_gate_analysis.py"))
        with open(os.path.join(fake, "hump_gate_analysis.py"), "a") as fh:
            fh.write("\n# one byte of drift\n")
        try:
            G.assert_pinned(tmp)
        except G.Refusal as e:
            assert "hash mismatch" in str(e).lower()
            return "one appended comment -> HASH MISMATCH -> refusal"
        raise AssertionError("a mutated extractor passed the pin")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@control("rule 2 / ss9.3", "PASS", "the extraction script on disk matches the frozen sha256")
def pin_pass():
    got = G.assert_pinned(REPO)
    assert got == G.EXTRACTOR_SHA256
    return "sha256 %s" % got


# ==========================================================================
# ss9.4 -- completion (rule 4) and THE AGE GUARD
# ==========================================================================
def _mkcase(tmp, endtime=2000, age_ok=True):
    case = os.path.join(tmp, "case")
    os.makedirs(os.path.join(case, "0"))
    os.makedirs(os.path.join(case, str(endtime)))
    open(os.path.join(case, "0", "U"), "w").write("x")
    old = time.time() - 100
    os.utime(os.path.join(case, "0", "U"), (old, old))
    for f in G.REQUIRED_FIELDS:
        p = os.path.join(case, str(endtime), f)
        open(p, "w").write("x")
        if not age_ok:
            t = old - 50
            os.utime(p, (t, t))
    return case


@control("ss9.4", "PASS", "rc 0, End line, last time == endTime, fields present, all "
                          "newer than 0/U -> complete")
def completion_pass():
    tmp = tempfile.mkdtemp(prefix="f6a_comp_")
    try:
        ok, d = G.completion_check(_mkcase(tmp), _log(1772, times=[1772, 2000]), 2000, 0)
        assert ok is True, d
        assert d["age_guard_anchor"] == "0/U"
        return "all clauses hold; age guard anchored on 0/U (NOT 0/T -- no T in this case)"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@control("ss9.4", "FAIL", "THE AGE GUARD: a field OLDER than the case's own 0/U -> refused")
def completion_age():
    tmp = tempfile.mkdtemp(prefix="f6a_age_")
    try:
        ok, d = G.completion_check(_mkcase(tmp, age_ok=False), _log(1772, times=[1772, 2000]), 2000, 0)
        assert ok is False, "a stale field survived the age guard"
        assert any("AGE GUARD" in f for f in d["failures"]), d
        return "%d age-guard failures raised" % sum("AGE GUARD" in f for f in d["failures"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@control("ss9.4", "FAIL", "rc != 0, no End line, last time != endTime, missing field -> each refused")
def completion_clauses():
    tmp = tempfile.mkdtemp(prefix="f6a_comp2_")
    try:
        case = _mkcase(tmp)
        assert G.completion_check(case, _log(1772, times=[1772, 2000]), 2000, 1)[0] is False
        lg = _log(1772, times=[1772, 2000], end=False)
        assert G.completion_check(case, lg, 2000, 0)[0] is False
        assert G.completion_check(case, _log(1772, times=[1772, 1900]), 2000, 0)[0] is False
        os.remove(os.path.join(case, "2000", "nut"))
        assert G.completion_check(case, _log(1772, times=[1772, 2000]), 2000, 0)[0] is False
        return "rc!=0, no End, last!=endTime, missing nut -- all four refused"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ==========================================================================
# ss5.5 -- GATE M, and its ENFORCEMENT: the launcher starts NO solver
# ==========================================================================
GOOD_CHECKMESH = """
    Mesh non-orthogonality Max: 40.5495 average: 9.19635
    Max skewness = 0.743352 OK.
Mesh OK.
"""
F12_CHECKMESH = """
    Mesh non-orthogonality Max: 70.64625857 average: 11.2 
   *Number of severely non-orthogonal (> 70 degrees) faces: 892.
    Max skewness = 1.9 OK.
Failed 1 mesh checks.
"""


@control("ss5.5", "PASS", "the shipped 51,626-cell hump mesh clears both hard gates")
def gate_m_pass():
    ok, d = L.gate_m(GOOD_CHECKMESH)
    assert ok is True, d
    assert abs(d["max_non_orthogonality"] - 40.5495) < 1e-6
    assert abs(d["max_skewness"] - 0.743352) < 1e-6
    return ("non-ortho 40.5495 (29.45 deg of margin), skewness 0.743352 (factor 5.4) "
            "-> GATE M PASS")


@control("ss5.5", "FAIL", "F12's rung-1 mesh at 70.646 deg -> GATE M BLOCKED")
def gate_m_fail():
    ok, d = L.gate_m(F12_CHECKMESH)
    assert ok is False, "a 70.646 deg mesh cleared a <= 70 gate"
    assert d["GATE_M"] == "BLOCKED"
    return "70.64625857 > 70.0 -> BLOCKED (not GATE FAIL, not NOT A RESULT)"


@control("ss5.5", "FAIL", "checkMesh output with no gate lines -> UNEVALUABLE -> refusal")
def gate_m_unevaluable():
    try:
        L.gate_m("Mesh OK.\n")
    except G.Refusal:
        return "no non-orthogonality line -> Refusal; Gate M never assumes"
    raise AssertionError("Gate M graded an output carrying neither quantity")


def _fixture_case(root):
    """A minimal case standing in for the shipped one, so the launcher's enforcement
    can be exercised END TO END without copying a 51,626-cell mesh or running one."""
    case = os.path.join(root, "src_case")
    os.makedirs(os.path.join(case, "0"))
    os.makedirs(os.path.join(case, "constant"))
    os.makedirs(os.path.join(case, "system"))
    open(os.path.join(case, "0", "U"), "w").write("x")
    open(os.path.join(case, "caseDef"), "w").write("// caseDef\n")
    open(os.path.join(case, "fieldDef"), "w").write("wallValuesFields (wallShearStress p);\n")
    open(os.path.join(case, "system", "controlDict"), "w").write(
        "// libs ( \"libfrozen.so\" );\n"
        "endTime         2000;\n"
        "functions\n{\n    wallShearStress\n    {\n"
        "        executeControl  writeTime;\n        writeControl    writeTime;\n    }\n"
        "    wallValues\n    {\n        writeControl    writeTime;\n    }\n}\n")
    return case


@control("ss5.5 ENFORCEMENT", "FAIL",
         "GATE M FAILS -> THE LAUNCHER STARTS NO SOLVER PROCESS AND SPAWNS NO MPI RANK. "
         "This is the single change that would have saved F12's spend")
def gate_m_enforcement():
    tmp = tempfile.mkdtemp(prefix="f6a_launch_")
    saved = (L.RUN_ROOTS, L.RUN_CASE, L.SOURCE_CASE, subprocess.run)
    invoked = []

    def fake_run(cmd, *a, **k):
        invoked.append(list(cmd))
        class R:
            returncode = 0
            stdout = F12_CHECKMESH        # a mesh that FAILS Gate M
            stderr = ""
        return R()
    try:
        src = _fixture_case(tmp)
        L.RUN_ROOTS = (os.path.join(tmp, "runs"),)
        L.RUN_CASE = os.path.join(tmp, "runs", "baseline_Re936k")
        L.SOURCE_CASE = os.path.relpath(src, REPO)
        L.subprocess.run = fake_run
        rc = L.main(["--scratch", os.path.join(tmp, "scratch")])
        assert rc == 4, "Gate M failure did not return exit 4, got %s" % rc
        started = [c for c in invoked
                   if any(("simpleFoam" in str(x)) or ("mpirun" in str(x)) for x in c)]
        assert not started, ("A SOLVER WAS STARTED ON A MESH THAT FAILED GATE M: %s"
                             % started)
        assert any("checkMesh" in str(x) for c in invoked for x in c)
        return ("exit 4, BLOCKED; commands invoked: %d, of which checkMesh 1 and "
                "solver/mpirun 0" % len(invoked))
    finally:
        L.RUN_ROOTS, L.RUN_CASE, L.SOURCE_CASE, L.subprocess.run = saved
        shutil.rmtree(tmp, ignore_errors=True)


# ==========================================================================
# ss9.2 -- the existing-directory guard
# ==========================================================================
@control("ss9.2", "PASS", "with both registered roots absent the freeze condition holds")
def dirguard_pass():
    ok, present = L.freeze_condition(("/nonexistent/a", "/nonexistent/b"))
    assert ok is True and present == []
    ok2, present2 = L.freeze_condition()
    return ("registered roots %s -> existing %s"
            % ("ABSENT" if ok2 else "PRESENT", present2))


@control("ss9.2", "FAIL",
         "a registered run directory that ALREADY EXISTS -> exit 3, and no case is built "
         "and no command is run")
def dirguard_fail():
    tmp = tempfile.mkdtemp(prefix="f6a_guard_")
    saved = (L.RUN_ROOTS, L.RUN_CASE, subprocess.run)
    invoked = []
    try:
        existing = os.path.join(tmp, "runs")
        os.makedirs(existing)
        ok, present = L.freeze_condition((existing,))
        assert ok is False and present == [existing]
        L.RUN_ROOTS = (existing,)
        L.RUN_CASE = os.path.join(existing, "baseline_Re936k")
        L.subprocess.run = lambda cmd, *a, **k: invoked.append(list(cmd))
        rc = L.main(["--scratch", os.path.join(tmp, "scratch")])
        assert rc == 3, "existing run directory did not return exit 3, got %s" % rc
        assert invoked == [], "commands were run after the guard should have refused"
        assert not os.path.exists(L.RUN_CASE), "a case was built after the guard fired"
        return "exit 3; 0 commands invoked; no case directory created"
    finally:
        L.RUN_ROOTS, L.RUN_CASE, L.subprocess.run = saved
        shutil.rmtree(tmp, ignore_errors=True)


# ==========================================================================
# ss8.5 -- the cap, which must actually cap
# ==========================================================================
@control("ss8.5", "PASS", "cap 30 core-min at ranks 4 -> 450 s wall, 420 s to the solver")
def cap_pass():
    total, t = L.solver_timeout_s()
    assert total == 450.0 and t == 420.0, (total, t)
    return "30 * 60 / 4 = 450 s; less a 30 s mesh reserve = 420 s"


@control("ss8.5", "FAIL",
         "THE NAIVE `timeout 1800` WOULD PERMIT 4x THE REGISTERED BUDGET -- a cap that "
         "does not cap; and a degenerate configuration raises rather than launching")
def cap_fail():
    naive = L.CAP_CORE_MIN * 60
    total, _ = L.solver_timeout_s()
    assert naive == 1800 and total == 450.0
    assert naive / total == L.RANKS, "the divisor is not the rank count"
    for bad in ({"ranks": 0}, {"reserve": 10 ** 6}):
        try:
            L.solver_timeout_s(**bad)
        except ValueError:
            continue
        raise AssertionError("degenerate cap configuration %s was accepted" % bad)
    return ("naive 1800 s is %dx the correct 450 s; ranks=0 and an over-large reserve "
            "both raise" % L.RANKS)


# ==========================================================================
# rule 14 + ss3.1 (P-c) sampling install
# ==========================================================================
@control("rule 14", "PASS", "no active top-level libs entry -> stock kOmegaSST asserted")
def libs_pass():
    assert L.assert_libs_stock('// libs ( "libfrozen.so" );\nendTime 2000;\nfunctions\n{\n}\n')
    return "commented-out libs line is not an active entry"


@control("rule 14", "FAIL",
         "an ACTIVE top-level libs entry is a FINDING and is REFUSED -- never silently "
         "replaced (a lesson is not applied until every call site asserts it)")
def libs_fail():
    try:
        L.assert_libs_stock('libs ("libkOmegaSSTQCRTurbulenceModels.so");\nfunctions\n{\n}\n')
    except G.Refusal as e:
        assert "rule 14" in str(e)
        return "active libs entry -> Refusal; the W1 model-library boundary is caught"
    raise AssertionError("an active libs entry was accepted")


@control("ss3.1 (P-c) install", "PASS", "the sampling cadence is installed and ASSERTED")
def install_pass():
    txt = ("functions\n{\n    wallShearStress\n    {\n"
           "        executeControl  writeTime;\n        writeControl    writeTime;\n    }\n"
           "    wallValues\n    {\n        writeControl    writeTime;\n    }\n}\n")
    out = L.install_pc_sampling(txt)
    assert out.count("timeStep;") == 3, out
    assert out.count("Interval") == 3, out
    assert "writeTime" not in out
    return "3 writeTime controls -> timeStep with a 50-iteration interval"


@control("ss3.1 (P-c) install", "FAIL",
         "a controlDict the install cannot fully patch -> REFUSAL rather than launching a "
         "run that cannot produce 10 samples")
def install_fail():
    try:
        L.install_pc_sampling("functions\n{\n    wallValues\n    {\n"
                              "        writeControl    writeTime;\n    }\n}\n")
    except G.Refusal as e:
        assert "3 substitutions" in str(e)
        return "1 substitution where 3 are required -> Refusal"
    raise AssertionError("a partial sampling install was accepted")


# ==========================================================================
# ss4 -- no triple is ever emitted, and the REPORTED channels never grade
# ==========================================================================
@control("ss4", "PASS", "no GCI, no observed order, no Richardson value is ever emitted")
def no_triple():
    r = G.grade({"separation": 0.6544, "reattachment": 1.2531},
                _samples([0.6544] * 10, [1.2531] * 10), _log(1772), True, {"seen": True})
    gc = r["grid_convergence"]
    assert gc["triple"] is None and gc["gci"] is None and gc["observed_order"] is None
    assert _forbidden_words(r) == [], _forbidden_words(r)
    return "triple/gci/observed_order all null; G stays NO; single mesh level disclosed"


@control("ss2.3 / ss2.1", "PASS",
         "the REPORTED channels are printed, labelled, and CANNOT move a verdict")
def reported_never_grades():
    # A value inside the oil-film band but outside the gated band must still GATE FAIL.
    r = G.grade({"separation": 0.6650, "reattachment": 1.16},
                _samples([0.6650] * 10, [1.16] * 10), _log(1772), True, {"seen": True})
    assert r["gates"]["P2_reattachment"]["verdict"] == "GATE FAIL"
    assert r["VERDICT"] == "GATE FAIL"
    rep = r["reported_not_gated"]
    assert rep["LABEL"] == "REPORTED -- NOT A GATE"
    # and the oil-film limb is reported beside it, at 1.2531, robust to the limb
    r2 = G.grade({"separation": 0.6544, "reattachment": 1.2531},
                 _samples([0.6544] * 10, [1.2531] * 10), _log(1772), True, {"seen": True})
    oil = r2["reported_not_gated"]["oilfilm_limb"]
    assert abs(oil["deviation_pct"] - 12.8919) < 1e-3, oil
    assert oil["band_verdict_if_gated"] == "GATE FAIL"
    return ("oil-film limb reported at +12.892 % (GATE FAIL either way); the reported "
            "channels changed no verdict")


@control("ss8.5 decompose", "PASS", "the launcher calls decomposePar and reconstructPar "
                                    "-- the frozen ss8.5 reserve names decomposePar")
def decompose_present():
    src = open(os.path.join(HERE, "run_f6a_greenblatt.py")).read()
    assert "decomposePar" in src and "reconstructPar" in src
    i_dec, i_mpi = src.index('"decomposePar"'), src.index('"mpirun"')
    i_rec = src.index('"reconstructPar"')
    assert i_dec < i_mpi < i_rec, "decompose/solve/reconstruct are out of order"
    return "decomposePar precedes mpirun precedes reconstructPar"


@control("ss8.5 decompose", "FAIL",
         "a decomposition that does not yield `ranks` processor directories -> REFUSAL, "
         "never an undecomposed parallel launch")
def decompose_guard():
    src = open(os.path.join(HERE, "run_f6a_greenblatt.py")).read()
    assert "processor directories, ss6.1" in src, "no rank-count guard on decomposePar"
    assert "REFUSING rather than\n                            \"launching an undecomposed" in src \
        or "launching an undecomposed" in src
    return "rank-count guard and a non-zero-rc refusal both present"


@control("ss9.4 endTime", "PASS",
         "the (P-a)/ss9.4 clause conflict is SURFACED with BOTH readings, not silently "
         "resolved")
def endtime_reconcile():
    r = G.endtime_reconciliation(_log(1772, times=[1772]), 2000)
    assert r["declared_endtime_controlDict"] == 2000
    assert r["effective_endtime_used"] == 1772
    assert r["residual_control_terminated"] is True
    assert r["clause_would_fail_on_declared"] is True
    assert "RULING" in r["DISPOSITION"]
    return ("declared 2000, effective 1772, both printed; disposition = reported to the "
            "supervisor, not resolved by the lane")


@control("ss9.4 endTime", "FAIL",
         "a run that reached the cap is NOT relabelled -- effective endTime is the last "
         "time and (P-a) still refuses it")
def endtime_no_laundering():
    r = G.endtime_reconciliation(_log(None, times=[2000]), 2000)
    assert r["residual_control_terminated"] is False
    assert r["effective_endtime_used"] == 2000
    ok, _ = G.clause_p_a(_log(None, times=[2000]))
    assert ok is False, "the reconciliation laundered a cap-hit into a convergence"
    return "cap-hit run: effective endTime 2000, and (P-a) still REFUSES it"


@control("truncate-before-read", "PASS",
         "every controlDict rewrite goes through rewrite_file(), which reads FULLY first")
def rewrite_pass():
    import tempfile as _t
    d = _t.mkdtemp(); p = os.path.join(d, "cd")
    open(p, "w").write("endTime         2000;\n")
    try:
        out = L.rewrite_file(p, lambda t: t.replace("2000", "1"))
        assert out.strip() == "endTime         1;", repr(out)
        assert open(p).read().strip() == "endTime         1;"
        return "content preserved and transformed; file non-empty after rewrite"
    finally:
        shutil.rmtree(d, ignore_errors=True)


@control("truncate-before-read", "FAIL",
         "THE TRUNCATING FORM IS ABSENT FROM THE SOURCE, and the control is shown able "
         "to SEE it -- this defect emptied a controlDict to 0 bytes and produced a "
         "FOAM FATAL that looked exactly like a case defect")
def rewrite_fail():
    # An AST walk, not a regex: the first form of this control matched its OWN
    # DOCSTRING describing the bug. A scan that cannot tell code from prose about
    # code is not a scan.
    import ast as _ast

    def truncating_calls(src):
        hits = []
        for node in _ast.walk(_ast.parse(src)):
            if not (isinstance(node, _ast.Call)
                    and isinstance(node.func, _ast.Attribute)
                    and node.func.attr == "write"
                    and isinstance(node.func.value, _ast.Call)
                    and getattr(node.func.value.func, "id", None) == "open"):
                continue
            mode = [a for a in node.func.value.args[1:]
                    if isinstance(a, _ast.Constant) and a.value == "w"]
            if not mode:
                continue
            for arg in node.args:
                for sub in _ast.walk(arg):
                    if isinstance(sub, _ast.Call) and getattr(sub.func, "id", None) == "open":
                        hits.append(node.lineno)
        return hits

    for name in ("run_f6a_greenblatt.py", "f6a_greenblatt_gate.py"):
        src = open(os.path.join(HERE, name)).read()
        hits = truncating_calls(src)
        assert not hits, "%s still contains the truncating form at lines %s" % (name, hits)
    # the scan must be shown able to SEE a violation
    planted = 'open(cdp, "w").write(re.sub(r"x", "y", open(cdp).read()))'
    assert truncating_calls(planted), "the scan cannot see the defect it is meant to catch"
    assert not truncating_calls('open(p, "w").write(text)'), "the scan false-positives"
    # and rewrite_file refuses to write emptiness
    import tempfile as _t
    d = _t.mkdtemp(); p = os.path.join(d, "cd")
    open(p, "w").write("endTime 2000;\n")
    try:
        try:
            L.rewrite_file(p, lambda t: "")
        except G.Refusal:
            return "0 truncating call sites; the scan SEES a planted one; empty write REFUSED"
        raise AssertionError("rewrite_file wrote empty content")
    finally:
        shutil.rmtree(d, ignore_errors=True)


@control("ADDENDUM 2", "PASS",
         "attempt 1's preserved tree and its evidence are present -> attempt 2 may run")
def preserved_pass():
    d = L.assert_preserved()
    assert d
    return "%d preserved trees present with their evidence" % len(d)


@control("ADDENDUM 2", "FAIL",
         "A CLEARED OR STRIPPED ATTEMPT-1 TREE REFUSES ATTEMPT 2 -- 'do not delete the "
         "evidence' is a check the code performs, not a discipline the lane remembers")
def preserved_fail():
    import tempfile as _t
    d = _t.mkdtemp()
    try:
        try:
            L.assert_preserved({os.path.join(d, "gone"): ("result.json",)})
        except G.Refusal as e:
            assert "PRESERVED tree is missing" in str(e)
        else:
            raise AssertionError("a deleted tree was accepted")
        empty = os.path.join(d, "stripped"); os.makedirs(empty)
        try:
            L.assert_preserved({empty: ("result.json",)})
        except G.Refusal as e:
            assert "evidence has been removed" in str(e)
            return "deleted tree REFUSED; tree stripped of result.json REFUSED"
        raise AssertionError("a stripped tree was accepted")
    finally:
        shutil.rmtree(d, ignore_errors=True)


@control("ADDENDUM 2", "FAIL",
         "the ss9.1 registration is NOT repurposed: attempt 2 writes to a "
         "differently-named root and the attempt-1 case path is never a write target")
def roots_distinct():
    assert L.RUN_CASE not in L.PRESERVED_TREES, "this attempt would overwrite a preserved tree"
    assert L.RUN_CASE.endswith("attempt%d_Re936k" % L.ATTEMPT), L.RUN_CASE
    for t in L.PRESERVED_TREES:
        assert t not in L.RUN_ROOTS, (
            "a preserved tree is registered as must-not-exist -- it MUST exist")
    assert L.RUN_CASE in L.RUN_ROOTS
    return "attempt-%d root distinct from all %d preserved trees" % (L.ATTEMPT, len(L.PRESERVED_TREES))


@control("ADDENDUM 4 rc", "PASS",
         "the solver exit code is PERSISTED TO DISK IMMEDIATELY ON CAPTURE, before any "
         "reporting, formatting or f-string")
def rc_persist_pass():
    import tempfile as _t
    d = _t.mkdtemp()
    try:
        p = L.persist_rc(d, 0)
        assert open(p).read().strip() == "0"
        src = open(os.path.join(HERE, "run_f6a_greenblatt.py")).read()
        i_cap = src.index("rc = pr.returncode")
        i_persist = src.index("persist_rc(RUN_CASE, rc)")
        i_report = src.index('report["solver_rc"] = rc')
        assert i_cap < i_persist < i_report, (
            "rc is not persisted between capture and reporting")
        between = src[i_cap:i_persist]
        assert "%" not in between and "format(" not in between, (
            "formatting happens between capturing rc and persisting it: %r" % between)
        return "capture -> persist -> report, with no formatting in between"
    finally:
        shutil.rmtree(d, ignore_errors=True)


@control("ADDENDUM 4 rc", "FAIL",
         "AN UNPERSISTED rc IS REFUSED, NOT INFERRED. Attempt 2's rc was lost to a typo, "
         "the supervisor REFUSED the inference and the row became NOT A RESULT: an "
         "unmeasured limb in a conjunctive rule is a degradation")
def rc_missing_refused():
    import tempfile as _t
    d = _t.mkdtemp()
    try:
        out = os.path.join(d, "o.json")
        rc = G.main(["--case", d, "--log", os.path.join(HERE, "run_f6a_greenblatt.py"),
                     "--endtime", "1813", "--rc-file", os.path.join(d, "nope.txt"),
                     "--scratch", d, "--out", out])
        assert rc == 2, "a missing rc file did not refuse, got %s" % rc
        import json as _j
        assert _j.load(open(out))["VERDICT"] == "NOT A RESULT"
        # and a garbage exit code is refused rather than coerced
        bad = os.path.join(d, "bad.txt"); open(bad, "w").write("probably fine")
        rc2 = G.main(["--case", d, "--log", os.path.join(HERE, "run_f6a_greenblatt.py"),
                      "--endtime", "1813", "--rc-file", bad,
                      "--scratch", d, "--out", out])
        assert rc2 == 2, "a non-integer rc was accepted"
        return "missing rc file -> NOT A RESULT (exit 2); non-integer rc -> refused"
    finally:
        shutil.rmtree(d, ignore_errors=True)


@control("ADDENDUM 4", "FAIL",
         "EVERY prior attempt's tree is guarded, not just attempt 1 -- attempt 2's "
         "complete solve and grading must still be there")
def preserved_all_attempts():
    assert len(L.PRESERVED_TREES) >= 2, L.PRESERVED_TREES
    keys = sorted(L.PRESERVED_TREES)
    assert any("baseline_Re936k" in k for k in keys)
    assert any("attempt2_Re936k" in k for k in keys)
    import tempfile as _t
    d = _t.mkdtemp()
    try:
        try:
            L.assert_preserved({os.path.join(d, "gone"): ("result.json",)})
        except G.Refusal:
            return "%d trees guarded; a missing one REFUSES" % len(L.PRESERVED_TREES)
        raise AssertionError("a missing preserved tree was accepted")
    finally:
        shutil.rmtree(d, ignore_errors=True)


FORBIDDEN = ("richardson", "extrapolat", "gci_fine", "observed order of")


def _forbidden_words(result):
    """ss4/ss9.3: no Richardson value, GCI or observed order may be emitted, and this
    scan must be shown able to SEE one -- a checker never demonstrated against a
    violation is the planted-zero failure applied to a checker."""
    blob = json.dumps(result).lower().replace('"observed_order": null', "")
    return [w for w in FORBIDDEN if w in blob]


@control("ss4", "FAIL",
         "the no-triple scan is shown able to SEE a violation -- a checker never "
         "demonstrated against one proves nothing")
def no_triple_control():
    clean = G.grade({"separation": 0.6544, "reattachment": 1.2531},
                    _samples([0.6544] * 10, [1.2531] * 10), _log(1772), True, {"seen": True})
    assert _forbidden_words(clean) == []
    mutated = dict(clean)
    mutated["grid_convergence"] = {"gci_fine": 0.0005, "richardson": 1.2499,
                                   "observed_order": 1.93}
    hits = _forbidden_words(mutated)
    assert set(hits) >= {"richardson", "gci_fine"}, hits
    return "clean result 0 hits; a planted GCI/Richardson block -> %d hits" % len(hits)


@control("ss2.3 / ss2.1", "FAIL",
         "GRADING ON THE REPORTED LIMB WOULD FLIP THE VERDICT -- so the code demonstrably "
         "used the GATED band and the reported channel is genuinely non-binding")
def reported_is_not_the_gate():
    # 1.16 sits OUTSIDE the gated PIV band [1.045, 1.155] and INSIDE the reported
    # oil-film band [1.0545, 1.1655]. The two channels disagree by construction.
    r = G.grade({"separation": 0.6650, "reattachment": 1.16},
                _samples([0.6650] * 10, [1.16] * 10), _log(1772), True, {"seen": True})
    assert r["gates"]["P2_reattachment"]["verdict"] == "GATE FAIL"
    assert r["VERDICT"] == "GATE FAIL"
    mutated = r["reported_not_gated"]["oilfilm_limb"]["band_verdict_if_gated"]
    assert mutated == "PASS", mutated
    assert r["reported_not_gated"]["separation_2pct_reading"]["inside"] is True
    return ("gated band -> GATE FAIL while the reported limb would have said PASS; the "
            "reported channels did not move the verdict")


@control("rule 1", "FAIL",
         "a verdict outside the fixed vocabulary is REFUSED -- no synonym, no hedge, "
         "ever reaches a record")
def vocabulary_control():
    real = G.band_verdict
    try:
        G.band_verdict = lambda v, b: "roughly converged"
        try:
            G.grade({"separation": 0.6650, "reattachment": 1.1000},
                    _samples([0.6650] * 10, [1.1000] * 10), _log(1772), True, {"seen": True})
        except G.Refusal as e:
            assert "vocabulary" in str(e) or "one-way door" in str(e), str(e)
            return "a mutated comparator emitting 'roughly converged' -> Refusal"
        raise AssertionError("a hedging verdict was written to a record")
    finally:
        G.band_verdict = real


# ==========================================================================
def main():
    print(__doc__.strip())
    print("\n" + "=" * 78)
    passed = failed = 0
    per_clause = {}
    for clause, arm, desc, fn in RESULTS:
        try:
            note = fn()
            print("  [OK]   %-22s %-4s %s" % (clause, arm, desc.split(" -- ")[0][:60]))
            if note:
                print("         -> %s" % note)
            passed += 1
            per_clause.setdefault(clause, set()).add(arm)
        except Exception as e:                                   # noqa: BLE001
            print("  [FAIL] %-22s %-4s %s" % (clause, arm, desc))
            print("         !! %s: %s" % (type(e).__name__, e))
            failed += 1
    print("=" * 78)

    # EVERY frozen clause must carry BOTH arms. A clause with no failing control is
    # a clause that cannot bind.
    missing = [c for c, arms in per_clause.items() if "FAIL" not in arms]
    if missing:
        print("  [FAIL] clauses with NO failing control: %s" % missing)
        failed += len(missing)

    # ZERO COMPUTE, asserted rather than claimed. The test is that THIS SELFTEST
    # created nothing -- not that the roots never exist. Once a launch has legitimately
    # built the run tree, that tree is EVIDENCE and is preserved; a control that failed
    # on its presence would be pressure to delete it.
    after = {d: os.path.exists(d) for d in L.RUN_ROOTS}
    created = [d for d in L.RUN_ROOTS if after[d] and not _ROOTS_AT_IMPORT[d]]
    if created:
        print("  [FAIL] this selftest created a registered run directory: %s" % created)
        failed += 1
    else:
        state = ", ".join("%s=%s" % (os.path.basename(d), "PRESENT" if v else "ABSENT")
                          for d, v in after.items())
        print("  [OK]   zero-compute control: this selftest created no run directory "
              "(%s, unchanged)" % state)

    print("\n%d controls passed, %d failed, across %d frozen clauses."
          % (passed, failed, len(per_clause)))
    if failed:
        print("SELFTEST FAILED.")
        return 1
    print("SELFTEST PASSED -- every frozen clause carries a control that can FAIL.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
