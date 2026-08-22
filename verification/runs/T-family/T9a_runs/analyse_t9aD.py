#!/usr/bin/env python3
"""
T9a-D comparator -- the diagnosis arm for T9a's 2.41 mK interface miss.

WRITTEN AND HASHED BEFORE ANY D_* CASE EXISTED (Charter 2d, prediction-first).
The freeze condition -- no D_* directory anywhere in the run tree -- is checked
with a timestamped command whose output is pasted into T9aD_RESULTS.md, not
asserted.

WHAT THIS GRADES, AND WHAT IT MAY NOT.

  It grades SEVEN ROWS -- A1 A2 B0 B1 B2 C1 C2 -- each against a numeric
  threshold registered in T9aD_registered.json before any case existed.

  IT GRADES NOTHING AGAINST THE T9a BAND.  T9a's verdict (GATE FAIL on R1)
  stands as its frozen comparator returned it.  This arm re-solves no T9a
  case: the baseline levels are READ from gate_t9a.json.

  IT REPAIRS NOTHING FROZEN.  analyse_t9a.py is imported unmodified and its
  hash is verified at every run.  Its readers are reused.  Its gci() is NOT
  called on any T9a-D row.

WHY IT CARRIES ITS OWN GCI, and why that is not a repair.

  The frozen gci() returns richardson = f_f + (f_m - f_f)/(r^p - 1); Roache's
  extrapolate is f_f + (f_f - f_m)/(r^p - 1).  T9a_RESULTS.md 8.1 records the
  defect and declines to fix it, because a repair cannot change a number a
  verdict depends on; T10a_RESULTS.md 1.1 works around it with a separate
  richardson_corrected field.

  THIS IS A NEW INSTRUMENT, NOT A REPAIR.  It is written before any case of a
  new arm exists, sign-correct from the start.  Charter 2d.1's four-condition
  repair exception is NOT INVOKED: nothing frozen changes and no published
  number moves.  The GCI BAND is identical either way -- it uses |e21| -- so
  no T9a verdict would have changed under either implementation, and that is
  said here so this file cannot be read as quietly correcting a graded result.

THE H-C OVERRIDE, stated because it looks like an edit and is not.

  measure_wall() verifies every cell's DT against the REGISTERED layer map and
  would correctly refuse a 0.4 W/mK layer.  For the H-C cases only, the
  in-memory dict analyse_t9a.REG["wall"]["layers"][1]["k"] is set to 0.4 for
  the duration of the call and restored afterwards.  The file on disk is never
  written.  exact_t9a.WALL_LAYERS is overridden the same way so that BOTH of
  its independent derivations run on the 40x problem and must agree.

CARRIED FORWARD, because they were paid for once:
  * every geometric constant is READ FROM THE MESH (the frozen readers do it);
  * convergence is judged from the last two WRITTEN checkpoints (L-141), with
    a LIVE PLANTED ZERO, because every wall case here is expected to report a
    literal 0.0 and a broken reader would report the same 0.0;
  * the fvSchemes entry that defines each arm is READ BACK FROM THE CASE, so
    the arm's single change is verified on disk and not assumed from a builder.

Usage:
  analyse_t9aD.py --selftest     instrument self-test, no case needed
  analyse_t9aD.py                grade the arm, write gate_t9aD.json
"""
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyse_t9a as AN            # noqa: E402  frozen, imported, never edited
import exact_t9a as EXACT           # noqa: E402  frozen, imported, never edited

DREG = json.load(open(os.path.join(HERE, "T9aD_registered.json")))
R_REFINE = DREG["grid"]["r"]
FS = DREG["grid"]["Fs"]
FLOOR_mK = DREG["collapse_floor_mK"]

PASS, GATE_REACHED, GATE_FAIL = "PASS", "GATE REACHED", "GATE FAIL"
NOT_A_RESULT, BLOCKED, PENDING = "NOT A RESULT", "BLOCKED", "PENDING"
EXIT_OK, EXIT_FAIL, EXIT_REFUSE = 0, 1, 2

# sha256 of the frozen files, as published in T9a_RESULTS.md (prefix/suffix)
FROZEN_EXPECT = {"analyse_t9a.py": ("dd2d6bf0", "cac9da"),
                 "exact_t9a.py": ("d3f2558c", "d3d0b8"),
                 "T9a_registered.json": ("66b03c7d", "b40ed")}

A_CASES = {"c": "D_A_c", "m": "D_A_m", "f": "D_A_f"}
C_CASES = {"c": "D_C_c", "m": "D_C_m", "f": "D_C_f"}
B_CASE = "D_B_x"
R_CASE = "D_R_f"          # replica control: the frozen W_f, rebuilt, nothing changed
ALL_CASES = list(A_CASES.values()) + [B_CASE] + list(C_CASES.values()) + [R_CASE]


def refuse(msg):
    print(msg)
    sys.exit(EXIT_REFUSE)


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


# ---------------------------------------------------------------------------
# the arm's own GCI -- sign-correct per Roache
# ---------------------------------------------------------------------------
def gci(f_coarse, f_med, f_fine, r=R_REFINE, Fs=FS):
    """Observed order, Roache GCI on the finest level, and a SIGN-CORRECT
    Richardson extrapolate  f_f + (f_f - f_m)/(r^p - 1).

    Refuses to invent an order: OSCILLATORY, STAGNANT (p < 0.5) and DIVERGENT
    (p <= 0) triples arm no band, and any row that depends on such a triple is
    NOT A RESULT.  An EXACT triple (medium and fine identical) arms a band of
    literal zero."""
    e21 = f_med - f_fine
    e32 = f_coarse - f_med
    if e21 == 0.0:
        return dict(state="EXACT", GCI_pct=0.0, richardson=f_fine)
    if e32 / e21 < 0.0:
        return dict(state="OSCILLATORY")
    p = math.log(abs(e32 / e21)) / math.log(r)
    if p <= 0.0:
        return dict(state="DIVERGENT", order=p)
    if p < 0.5:
        return dict(state="STAGNANT", order=p)
    den = r ** p - 1.0
    return dict(state="CONVERGING", order=p,
                GCI_pct=100.0 * Fs * abs(e21 / f_fine) / den,
                richardson=f_fine + (f_fine - f_med) / den)


# ---------------------------------------------------------------------------
def exact_wall(layers):
    """Closed form + independent FV route, both from the FROZEN exact_t9a with
    WALL_LAYERS overridden IN MEMORY.  Refuses if the two disagree."""
    saved = EXACT.WALL_LAYERS
    try:
        EXACT.WALL_LAYERS = tuple((ly["L"], ly["k"]) for ly in layers)
        a = EXACT.wall_closed_form()
        b = EXACT.wall_numeric(n_per_layer=(400, 800, 160))
        for key in ("q", "T_i1", "T_i2"):
            rel = abs(a[key] - b[key]) / abs(a[key])
            if rel > 1e-9:
                refuse(f"REFUSE: the two exact routes disagree on {key} "
                       f"(rel {rel:.2e}); no reference can be trusted.")
        return a
    finally:
        EXACT.WALL_LAYERS = saved


def read_laplacian_scheme(case):
    """READ BACK from the case what this arm's single change was supposed to
    be.  Never taken from the builder."""
    p = os.path.join(HERE, case, "system", "fvSchemes")
    if not os.path.isfile(p):
        refuse(f"REFUSE: {case} has no system/fvSchemes")
    txt = open(p).read()
    m = re.search(r"laplacianSchemes\s*\{(.*?)\}", txt, re.S)
    if not m:
        refuse(f"REFUSE: {case} fvSchemes has no laplacianSchemes block")
    body = m.group(1)
    m2 = re.search(r"laplacian\(DT,T\)\s+([^;]+);", body)
    if m2:
        return " ".join(m2.group(1).split())
    m3 = re.search(r"default\s+([^;]+);", body)
    if not m3:
        refuse(f"REFUSE: {case} has neither laplacian(DT,T) nor a default "
               f"laplacian scheme")
    return " ".join(m3.group(1).split())


def measure(case, k2):
    """The FROZEN measure_wall, with the registered layer-2 conductivity
    overridden in memory for the H-C arm only.  The file is never edited."""
    saved = AN.REG["wall"]["layers"][1]["k"]
    try:
        AN.REG["wall"]["layers"][1]["k"] = k2
        return AN.measure_wall(os.path.join(HERE, case))
    finally:
        AN.REG["wall"]["layers"][1]["k"] = saved


def ratios(vals):
    return [abs(vals[i]) / abs(vals[i + 1]) for i in range(len(vals) - 1)]


def band_row(tag, claim, ok, detail, predicted=None):
    v = PASS if ok else GATE_FAIL
    print(f"    {tag}: {v}   {detail}")
    return dict(row=tag, claim=claim, verdict=v, detail=detail,
                registered_prediction=predicted)


# ---------------------------------------------------------------------------
def selftest():
    """The instrument against triples whose answers are known by construction."""
    bad = []

    def chk(name, got, want, tol=1e-9):
        good = (isinstance(want, str) and got == want) or \
               (not isinstance(want, str) and abs(got - want) <= tol)
        print(f"  {name:34s} {got!r:>22}  want {want!r:<22} "
              f"{'ok' if good else 'FAIL'}")
        if not good:
            bad.append(name)

    r = R_REFINE
    print("T9a-D comparator self-test: gci() against constructed triples")
    # exact first order about a known limit F = 10, C = 1
    F, C = 10.0, 1.0
    t1 = gci(F + C * r ** 2, F + C * r, F + C)
    chk("first order: state", t1["state"], "CONVERGING")
    chk("first order: p", t1["order"], 1.0)
    chk("first order: richardson -> F", t1["richardson"], F, 1e-9)
    # exact second order
    t2 = gci(F + C * r ** 4, F + C * r ** 2, F + C)
    chk("second order: state", t2["state"], "CONVERGING")
    chk("second order: p", t2["order"], 2.0)
    chk("second order: richardson -> F", t2["richardson"], F, 1e-9)
    # GCI formula on the first-order triple
    e21 = (F + C * r) - (F + C)
    want = 100.0 * FS * abs(e21 / (F + C)) / (r ** 1.0 - 1.0)
    chk("GCI = Fs|e21/f_f|/(r^p-1)", t1["GCI_pct"], want, 1e-12)
    # the three no-band states
    chk("oscillatory", gci(10.0, 11.0, 10.5)["state"], "OSCILLATORY")
    chk("stagnant  (ratio 1.2)", gci(10.0 + 1.2 ** 2, 10.0 + 1.2, 11.0)["state"],
        "STAGNANT")
    chk("divergent (ratio 0.8)", gci(10.0 + 0.8 ** 2, 10.0 + 0.8, 11.0)["state"],
        "DIVERGENT")
    chk("exact (medium == fine)", gci(10.5, 11.0, 11.0)["state"], "EXACT")

    # the sign, against the frozen instrument, on T9a's own published R0 triple
    fc, fm, ff = 20.425588, 20.069440, 19.854991
    mine = gci(fc, fm, ff)
    theirs = AN.gci(fc, fm, ff)
    print(f"\n  T9a R0 triple {fc} -> {fm} -> {ff} (monotone falling)")
    print(f"    frozen  richardson {theirs['richardson']:.6f}  "
          f"{'ABOVE' if theirs['richardson'] > ff else 'below'} the fine value")
    print(f"    this    richardson {mine['richardson']:.6f}  "
          f"{'above' if mine['richardson'] > ff else 'BELOW'} the fine value")
    chk("frozen sign defect reproduced", theirs["richardson"] > ff, True)
    chk("this instrument extrapolates below", mine["richardson"] < ff, True)
    chk("bands identical (both use |e21|)", mine["GCI_pct"],
        theirs["GCI_pct"], 1e-12)

    # the exact-reference override round-trips to the registered decimals
    print("\n  exact_t9a override round-trip")
    e400 = exact_wall(DREG["wall_frozen"]["layers"])
    chk("400x T_i1 -> registered", e400["T_i1"], 348.781082, 2e-6)
    chk("400x q''  -> registered", e400["q"], 19.502682, 2e-6)
    e40 = exact_wall(DREG["wall_H_C"]["layers"])
    chk("40x  T_i1 -> registered", e40["T_i1"], DREG["wall_H_C"]["T_i1"], 1e-9)
    chk("40x  q''  -> registered", e40["q"], DREG["wall_H_C"]["q"], 1e-6)
    chk("frozen WALL_LAYERS restored", EXACT.WALL_LAYERS[1][1], 0.04)
    chk("frozen REG k restored", AN.REG["wall"]["layers"][1]["k"], 0.04)

    print("\nSELFTEST PASSED" if not bad else f"\nSELFTEST FAILED: {bad}")
    return EXIT_OK if not bad else EXIT_REFUSE


# ---------------------------------------------------------------------------
def planted_zero(case):
    """L-141 live control: plant 1.234e-3 K into a SCRATCH COPY and recover it
    with the frozen reader.  The run tree is not touched."""
    src = os.path.join(HERE, case)
    tmp = tempfile.mkdtemp(prefix="t9aD_planted_")
    dst = os.path.join(tmp, case)
    shutil.copytree(src, dst)
    p = os.path.join(dst, "900", "T")
    txt = open(p).read()
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\n?(\d+)\s*\(\s*\n",
                  txt)
    if not m:
        shutil.rmtree(tmp)
        refuse(f"REFUSE: cannot plant into {p}")
    i = m.end()
    j = txt.index("\n", i)
    v0 = float(txt[i:j])
    planted = txt[:i] + repr(v0 + 1.234e-03) + txt[j:]
    open(p, "w").write(planted)
    conv = AN.iterative_convergence(dst)
    shutil.rmtree(tmp)
    return dict(case=case, scratch=dst, planted_K=1.234e-03,
                recovered_max_change=conv.get("max_change"),
                state=conv.get("state"),
                recovered=abs(conv.get("max_change", 0) - 1.234e-03) < 1e-9)


# ---------------------------------------------------------------------------
def main():
    out = {"arm": "T9a-D", "r": R_REFINE, "Fs": FS,
           "collapse_floor_mK": FLOOR_mK}

    # ---- provenance: the frozen files must be the frozen files -------------
    print("frozen-file hashes (verified, not asserted):")
    hashes = {}
    for name, (pre, suf) in FROZEN_EXPECT.items():
        h = sha256(os.path.join(HERE, name))
        hashes[name] = h
        ok = h.startswith(pre) and h.endswith(suf)
        print(f"  {name:22s} {h[:8]}...{h[-6:]}  "
              f"{'matches T9a_RESULTS' if ok else 'DOES NOT MATCH'}")
        if not ok:
            refuse(f"REFUSE: {name} is not the file T9a_RESULTS.md published.")
    hashes["analyse_t9aD.py"] = sha256(os.path.join(HERE, "analyse_t9aD.py"))
    hashes["T9aD_registered.json"] = sha256(
        os.path.join(HERE, "T9aD_registered.json"))
    out["hashes"] = hashes

    # ---- the reference must survive its own re-derivation ------------------
    print("\nre-deriving the references (frozen exact_t9a.py, both routes) ...")
    ex400 = exact_wall(DREG["wall_frozen"]["layers"])
    ex40 = exact_wall(DREG["wall_H_C"]["layers"])
    # The 400x pair is checked against T9a's PRINTED SIX-DECIMAL constants, so
    # the tolerance is half a unit in the last printed place (5e-7 ABSOLUTE),
    # not a relative one; the 40x pair is registered at full double precision
    # and is checked relatively at 1e-9.  See T9aD_RESULTS.md section 6: this
    # line refused on its first run at 18:02 Z because a single relative 1e-8
    # was applied to a constant printed to six decimals, and the tolerance was
    # repaired under Charter 2d's boundary clause 1.  It compares two
    # DERIVED/TRANSCRIBED constants and touches no measurement.
    for nm, got, want, kind, tol in (
            ("400x T_i1", ex400["T_i1"], 348.781082, "abs", 5e-7),
            ("400x q", ex400["q"], 19.502682, "abs", 5e-7),
            ("40x T_i1", ex40["T_i1"], DREG["wall_H_C"]["T_i1"], "rel", 1e-9),
            # T9aD_registered.json prints the 40x q'' to FIVE decimals
            # (159.36255) while T_i1 and T_i2 are at full double precision, so
            # this one gets the same half-a-unit-in-the-last-place treatment.
            ("40x q", ex40["q"], DREG["wall_H_C"]["q"], "abs", 5e-6)):
        err = abs(got - want) if kind == "abs" else abs(got - want) / abs(want)
        if err > tol:
            refuse(f"REFUSE: derived {nm} = {got} disagrees with the "
                   f"registered {want} ({kind} error {err:.3e} > {tol:.1e})")
    print(f"  400x: q'' {ex400['q']:.6f}  T_i1 {ex400['T_i1']:.6f}  "
          f"T_i2 {ex400['T_i2']:.6f}")
    print(f"   40x: q'' {ex40['q']:.6f}  T_i1 {ex40['T_i1']:.6f}  "
          f"T_i2 {ex40['T_i2']:.6f}")
    out["exact"] = {"contrast_400": ex400, "contrast_40": ex40}

    # ---- the T9a baseline is READ, never re-solved --------------------------
    gate = json.load(open(os.path.join(HERE, "gate_t9a.json")))
    base = {l: gate["cases"][c] for l, c in
            (("c", "W_c"), ("m", "W_m"), ("f", "W_f"))}
    base_e1 = [base[l]["T_i1"] - ex400["T_i1"] for l in ("c", "m", "f")]
    print("\nT9a baseline, READ from gate_t9a.json (no case re-solved):")
    for l, e in zip(("c", "m", "f"), base_e1):
        print(f"  W_{l}: T_i1 {base[l]['T_i1']:.9f}   e1 {1e3*e:+.4f} mK")
    print(f"  ratios {', '.join(f'{r:.3f}' for r in ratios(base_e1))}")
    out["baseline_read"] = {l: base[l] for l in base}
    out["baseline_e1_mK"] = [1e3 * e for e in base_e1]

    # ---- completion markers -------------------------------------------------
    missing = [c for c in ALL_CASES
               if not os.path.isfile(os.path.join(HERE, f"DONE.{c}"))]
    if missing:
        refuse("REFUSE: the arm is PENDING -- no completion marker for "
               + ", ".join(sorted(missing)))

    # ---- measure -------------------------------------------------------------
    print("\nmeasuring, with the fvSchemes entry READ BACK from each case:")
    meas, schemes = {}, {}
    for case in ALL_CASES:
        k2 = DREG["cases"][case]["k2"]
        schemes[case] = read_laplacian_scheme(case)
        want = DREG["cases"][case]["scheme"]
        if schemes[case] != want:
            refuse(f"REFUSE: {case} carries laplacian scheme "
                   f"'{schemes[case]}', registered as '{want}'")
        meas[case] = measure(case, k2)
        m = meas[case]
        ex = ex40 if k2 != 0.04 else ex400
        print(f"  {case:8s} {m['n_cells']:3d} cells  scheme '{schemes[case]}'  "
              f"k2 {k2}  q {m['q']:.6f} ({100*(m['q']-ex['q'])/ex['q']:+.5f} %)"
              f"  T_i1 {m['T_i1']:.9f} ({1e3*(m['T_i1']-ex['T_i1']):+.5f} mK)"
              f"  T_i2 ({1e3*(m['T_i2']-ex['T_i2']):+.5f} mK)"
              f"  closure {m['heat_balance_closure']:.2e}")
    out["cases"] = meas
    out["schemes_read_back"] = schemes

    # ---- replica control: the new builder must reproduce the frozen case ----
    # A near-IDENTITY (Charter 2a), so it is never one of the graded rows.  It
    # is a REFUSAL CONDITION: if the builder does not reproduce W_f with
    # nothing changed, the arm's single-change claim is false and every row
    # below is NOT A RESULT.
    rep = meas[R_CASE]
    wf = gate["cases"]["W_f"]
    dT1 = rep["T_i1"] - wf["T_i1"]
    dT2 = rep["T_i2"] - wf["T_i2"]
    dq = rep["q"] - wf["q"]
    print(f"\nreplica control {R_CASE} vs the frozen W_f "
          f"(near-identity; refusal condition, never a graded row):")
    print(f"  T_i1 d = {dT1:+.3e} K   T_i2 d = {dT2:+.3e} K   "
          f"q'' d = {dq:+.3e} W/m2")
    rep_ok = abs(dT1) < 1e-9 and abs(dT2) < 1e-9 and abs(dq) < 1e-7
    out["replica_control"] = dict(case=R_CASE, dT_i1=dT1, dT_i2=dT2, dq=dq,
                                  reproduces=rep_ok)
    if not rep_ok:
        refuse(f"REFUSE: {R_CASE} does not reproduce the frozen W_f "
               f"(dT_i1 {dT1:.3e} K, dT_i2 {dT2:.3e} K, dq {dq:.3e}). The new "
               f"builder is itself a variable, so no T9a-D row is a result.")
    print("  REPRODUCES -- the new builder is not a variable.")

    # ---- iterative convergence, with a live planted zero ---------------------
    print("\niterative convergence (last two written checkpoints, L-141):")
    conv = {}
    for case in ALL_CASES:
        conv[case] = AN.iterative_convergence(os.path.join(HERE, case))
        print(f"  {case:8s} {conv[case]['state']:14s} "
              f"max_change {conv[case].get('max_change', float('nan')):.3e} K  "
              f"range {conv[case].get('field_range', float('nan')):.4f} K")
    out["iterative_convergence"] = conv
    pz = planted_zero("D_C_f")
    print(f"  PLANTED ZERO on a scratch copy of {pz['case']}: planted "
          f"{pz['planted_K']:.3e} K, recovered "
          f"{pz['recovered_max_change']:.7e} K, state {pz['state']}  -> "
          f"{'RECOVERED' if pz['recovered'] else 'NOT RECOVERED'}")
    out["planted_zero"] = pz
    if not pz["recovered"]:
        refuse("REFUSE: the convergence reader cannot see a planted number; "
               "its zeros mean nothing.")

    # ---- emulator identity, reported and NEVER gated -------------------------
    pred_path = os.path.join(HERE, "T9aD_predictions.json")
    pred = json.load(open(pred_path)) if os.path.isfile(pred_path) else None
    out["emulator_identity"] = None
    if pred:
        print("\nemulator identity (Charter 2a: reported, NEVER gated) -- "
              "predict_t9aD.py vs the solver:")
        ident = {}
        for case in ALL_CASES:
            h = DREG["cases"][case]["hypothesis"]
            lv = case.split("_")[-1]
            key = {"H-A": "H_A", "H-B": "H_B", "H-C": "H_C",
                   "CONTROL-R": "H_B"}[h]
            src = pred[key]["levels"].get(lv)
            if not src:
                continue
            d = meas[case]["T_i1"] - src["T_i1"]
            ident[case] = dict(predicted_T_i1=src["T_i1"],
                               solved_T_i1=meas[case]["T_i1"], diff_K=d)
            print(f"  {case:8s} predicted {src['T_i1']:.9f}  solved "
                  f"{meas[case]['T_i1']:.9f}  d = {d:+.3e} K")
        out["emulator_identity"] = ident

    # ---- the rows ------------------------------------------------------------
    rows = []
    R = DREG["rows"]
    print("\n" + "=" * 78)
    print("H-A  interface scheme  (D_A_c / D_A_m / D_A_f)")
    print("=" * 78)
    a_e1 = [meas[A_CASES[l]]["T_i1"] - ex400["T_i1"] for l in ("c", "m", "f")]
    drop = [abs(b) / abs(a) if a != 0.0 else float("inf")
            for b, a in zip(base_e1, a_e1)]
    for l, e, d in zip(("c", "m", "f"), a_e1, drop):
        print(f"    {l}: e1 {1e3*e:+.6g} mK   drop vs frozen scheme x{d:.4g}")
    rows.append(band_row(
        "A1", R["A1"]["claim"], min(drop) > 3.0,
        f"drop factors {', '.join(f'{d:.4g}' for d in drop)}; threshold "
        f"min > 3.0", R["A1"].get("registered_disagreement")))
    a_mK = [abs(1e3 * e) for e in a_e1]
    if max(a_mK) < FLOOR_mK:
        print(f"    A2: {NOT_A_RESULT} -- all three |e1| "
              f"({', '.join(f'{v:.3g}' for v in a_mK)} mK) lie below the "
              f"registered collapse floor {FLOOR_mK} mK; the ratios would "
              f"measure round-off, not order. PREDICTED.")
        rows.append(dict(row="A2", claim=R["A2"]["claim"],
                         verdict=NOT_A_RESULT,
                         detail=f"collapse floor {FLOOR_mK} mK fired; "
                                f"|e1| = {a_mK}",
                         registered_prediction=R["A2"]
                         ["registered_disagreement"]))
    else:
        ar = ratios(a_e1)
        rows.append(band_row(
            "A2", R["A2"]["claim"],
            all(2.0 <= v <= 3.3 for v in ar),
            f"ratios {', '.join(f'{v:.3f}' for v in ar)}; threshold "
            f"[2.0, 3.3]", R["A2"].get("registered_disagreement")))
    out["H_A"] = dict(e1_mK=[1e3 * e for e in a_e1], drop_factor=drop)

    print("\n" + "=" * 78)
    print("H-B  mesh  (m / f read from gate_t9a.json, x = D_B_x)")
    print("=" * 78)
    Ti1_mfx = [base["m"]["T_i1"], base["f"]["T_i1"], meas[B_CASE]["T_i1"]]
    b_e1 = [v - ex400["T_i1"] for v in Ti1_mfx]
    for l, v, e in zip(("m", "f", "x"), Ti1_mfx, b_e1):
        print(f"    {l}: T_i1 {v:.9f}   e1 {1e3*e:+.5f} mK")
    trip = gci(*Ti1_mfx)
    print(f"    m/f/x triple: {trip}")
    out["H_B"] = dict(T_i1=Ti1_mfx, e1_mK=[1e3 * e for e in b_e1],
                      triple=trip, n_cells=meas[B_CASE]["n_cells"])
    if trip["state"] != "CONVERGING":
        print(f"    B0: {NOT_A_RESULT} -- the m/f/x triple is "
              f"{trip['state']}; no band may be armed. PREDICTED.")
        rows.append(dict(row="B0", claim=R["B0"]["claim"],
                         verdict=NOT_A_RESULT,
                         detail=f"triple is {trip['state']}"
                                + (f" (p = {trip['order']:.4f})"
                                   if "order" in trip else ""),
                         registered_prediction=R["B0"]
                         ["registered_disagreement"]))
    else:
        rows.append(band_row(
            "B0", R["B0"]["claim"], 0.7 <= trip["order"] <= 1.4,
            f"CONVERGING, p = {trip['order']:.4f}; threshold [0.7, 1.4]",
            R["B0"].get("registered_disagreement")))
    br = ratios(b_e1)
    rows.append(band_row(
        "B1", R["B1"]["claim"], all(1.25 <= v <= 2.05 for v in br),
        f"level-error ratios {', '.join(f'{v:.3f}' for v in br)}; threshold "
        f"[1.25, 2.05]"))
    out["H_B"]["e1_ratios"] = br
    if trip["state"] != "CONVERGING":
        would = None
        if "order" in trip and trip["order"] > 0:
            den = R_REFINE ** trip["order"] - 1.0
            would = 1e3 * FS * abs(Ti1_mfx[1] - Ti1_mfx[2]) / den
        print(f"    B2: {NOT_A_RESULT} -- no band may be armed on a "
              f"{trip['state']} triple. PREDICTED."
              + (f" A forbidden arming would have given {would:.4f} mK "
                 f"against a {abs(1e3*b_e1[2]):.4f} mK error." if would else ""))
        rows.append(dict(row="B2", claim=R["B2"]["claim"],
                         verdict=NOT_A_RESULT,
                         detail=f"triple is {trip['state']}; band forbidden",
                         forbidden_band_mK=would,
                         error_x_mK=1e3 * b_e1[2],
                         registered_prediction=R["B2"]
                         ["registered_disagreement"]))
        out["H_B"]["forbidden_band_mK"] = would
    else:
        band_mK = 1e3 * (trip["GCI_pct"] / 100.0) * abs(Ti1_mfx[2])
        rows.append(band_row(
            "B2", R["B2"]["claim"], band_mK < abs(1e3 * b_e1[2]),
            f"band {band_mK:.4f} mK vs |error| {abs(1e3*b_e1[2]):.4f} mK; "
            f"PASS means the band does NOT cover the error",
            R["B2"].get("registered_disagreement")))
        out["H_B"]["band_mK"] = band_mK

    print("\n" + "=" * 78)
    print("H-C  property jump 400x -> 40x  (D_C_c / D_C_m / D_C_f)")
    print("=" * 78)
    c_e1 = [meas[C_CASES[l]]["T_i1"] - ex40["T_i1"] for l in ("c", "m", "f")]
    shrink = [abs(b) / abs(c) for b, c in zip(base_e1, c_e1)]
    drop400 = DREG["wall_frozen"]["T_hot"] - DREG["wall_frozen"]["T_cold"]
    lay1_400 = ex400["q"] * 0.05 / 0.8
    lay1_40 = ex40["q"] * 0.05 / 0.8
    for l, e, s in zip(("c", "m", "f"), c_e1, shrink):
        print(f"    {l}: e1 {1e3*e:+.5f} mK  ({100*e/lay1_40:+.5f} % of the "
              f"{lay1_40:.6f} K layer-1 drop)   shrink vs 400x x{s:.4g}")
    print(f"    for reference, the 400x errors are "
          f"{', '.join(f'{1e3*e:+.4f}' for e in base_e1)} mK "
          f"({', '.join(f'{100*e/lay1_400:+.5f}' for e in base_e1)} % of its "
          f"{lay1_400:.6f} K layer-1 drop); the driving potential is "
          f"{drop400:.0f} K in BOTH arms")
    rows.append(band_row(
        "C1", R["C1"]["claim"], all(3.0 <= v <= 30.0 for v in shrink),
        f"shrink factors {', '.join(f'{v:.4g}' for v in shrink)}; threshold "
        f"all in [3, 30]" + ("  (the error GREW)" if max(shrink) < 1 else ""),
        R["C1"].get("registered_disagreement")))
    cr = ratios(c_e1)
    rows.append(band_row(
        "C2", R["C2"]["claim"], all(1.25 <= v <= 2.05 for v in cr),
        f"level-error ratios {', '.join(f'{v:.3f}' for v in cr)}; threshold "
        f"[1.25, 2.05]"))
    out["H_C"] = dict(e1_mK=[1e3 * e for e in c_e1], shrink_factor=shrink,
                      e1_ratios=cr, layer1_drop_40=lay1_40,
                      layer1_drop_400=lay1_400,
                      e1_pct_of_drop=[100 * e / lay1_40 for e in c_e1],
                      base_e1_pct_of_drop=[100 * e / lay1_400
                                           for e in base_e1])

    out["rows"] = rows
    print("\n" + "=" * 78)
    print("T9a-D ROW SUMMARY (each verdict is against a threshold registered "
          "in\nT9aD_registered.json before any D_* case existed; NONE is "
          "against the T9a band)")
    print("=" * 78)
    for r in rows:
        print(f"  {r['row']:3s} {r['verdict']:14s} {r['detail']}")
    n_fail = sum(1 for r in rows if r["verdict"] == GATE_FAIL)
    n_nar = sum(1 for r in rows if r["verdict"] == NOT_A_RESULT)
    n_pass = sum(1 for r in rows if r["verdict"] == PASS)
    print(f"\n  {n_pass} PASS, {n_fail} GATE FAIL, {n_nar} NOT A RESULT, "
          f"of {len(rows)} rows")
    out["tally"] = dict(PASS=n_pass, GATE_FAIL=n_fail, NOT_A_RESULT=n_nar)

    unconv = [c for c in ALL_CASES
              if conv[c]["state"] not in ("CONVERGED", "EXACT")]
    if unconv:
        print(f"  unconverged cases: {unconv}")
    out["unconverged"] = unconv

    with open(os.path.join(HERE, "gate_t9aD.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True, default=str)
    print("\nwritten: gate_t9aD.json")
    return EXIT_FAIL if n_fail else EXIT_OK


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(selftest())
    raise SystemExit(main())
