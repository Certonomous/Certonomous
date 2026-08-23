#!/usr/bin/env python3
"""
T9aH instrument -- the composite wall and fin re-graded under Gauss harmonic.

*** THIS IS A NEW INSTRUMENT.  READ IT AS SOURCE AND AS A DIFF BEFORE ANY OF
*** ITS OUTPUT IS BELIEVED (SUPERVISION_CHARTER.md section 3 check 1, and
*** section 1 of docs/campaigns/T-family/T9aH_PREREGISTRATION.md, which says so
*** in a box at the top of the document).  It is NOT the frozen T9a comparator.

WHAT IS FROZEN AND WHAT IS NEW, so the split is never in doubt:

  FROZEN, BYTE-IDENTICAL, and it grades rows FR0-FR4 and controls C1-C3 with no
  help from this file:            analyse_t9a.py  (sha dd2d6bf0...4ecac9da,
  committed blob 239ed2b8), exact_t9a.py (d3f2558c...17d3d0b8),
  T9a_registered.json (66b03c7d...1edb40ed), check_t9a_mesh.py, mark_done_t9a.py,
  run_one_t9a.sh, run_chain_t9a.sh.  This file HASHES all seven and refuses on
  any mismatch.

  NEW, and this is it: rows H1-H6 and controls HC1-HC4, graded as ABSOLUTE
  distances from the full-precision closed form.  IT CARRIES NO GCI AND ARMS NO
  BAND, so it cannot repair, widen or replace any frozen band.  Every frozen
  reader it uses is IMPORTED UNMODIFIED (measure_wall, measure_fin,
  iterative_convergence, read_internal, read_points, cell_centres, latest_time,
  boundary_blocks, gci, refuse, foam), and every override of a frozen module
  constant is made IN MEMORY for the duration of one call and RESTORED, with the
  restoration asserted.

WHY A NEW INSTRUMENT IS NEEDED AT ALL: the frozen comparator's only band is a
Roache GCI on differences between levels.  Under Gauss harmonic those
differences are round-off (T9a-D measured |e1| = 0 / 3.2e-12 / 3.0e-12 K), so
the frozen rule cannot grade an exact scheme -- see section 4.1 of the
pre-registration, which registers, BEFORE the run, that no frozen wall row can
come back PASS and that the frozen verdict is published exactly as returned.

THIS IS NOT A REPAIR (Charter 2d.1).  It is written for a new rung before any
T9aH case exists; nothing frozen changes, no published number moves, and T9a's
gate_t9a.json is read and never written.  The four-condition repair exception is
NOT INVOKED AND NOT NEEDED.

EVERY THRESHOLD IS TRANSCRIBED TWICE: once into T9aH_registered.json and once
into REGH_CODE below, from section 4 of the pre-registration.  The two
transcriptions are compared at every run and at every selftest, and a
disagreement REFUSES rather than grades -- the pre-registration governs.

WHAT THIS FILE CANNOT SEE: any fluid, any turbulence or thermal closure, any
conjugate coupling, contact resistance, anisotropic or temperature-dependent k,
a non-orthogonal mesh, or an interface that does not lie on a mesh face.
"""
import copy
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyse_t9a as A            # noqa: E402  frozen, byte-identical
import exact_t9a as EX             # noqa: E402  frozen, byte-identical
import check_t9a_mesh as MESH      # noqa: E402  frozen, byte-identical
import mark_done_t9a as MARK       # noqa: E402  frozen, byte-identical

T9A_RUNS = os.path.join(os.path.dirname(HERE), "T9a_runs")

PASS, GATE_REACHED, GATE_FAIL = "PASS", "GATE REACHED", "GATE FAIL"
NOT_A_RESULT, BLOCKED, PENDING = "NOT A RESULT", "BLOCKED", "PENDING"
EXIT_OK, EXIT_FAIL, EXIT_REFUSE = 0, 1, 2

# ---------------------------------------------------------------------------
# The registered numbers, hard-coded here as the SECOND transcription of
# section 4 of docs/campaigns/T-family/T9aH_PREREGISTRATION.md.  The first is
# T9aH_registered.json.  They must agree or this instrument refuses.
# ---------------------------------------------------------------------------
REGH_CODE = dict(
    tol_abs_K=1.0e-08,          # H1, H3, H4, H5   (kelvin)
    tol_rel=1.0e-08,            # H2, H5           (relative)
    tol_fin=1.0e-09,            # H6               (absolute, dimensionless)
    min_drop=1.0e+06,           # H4
    baseline_e1_mK=-64.99408,   # H4, read from gate_t9aD.json (D_C_f)
    collapse_floor_K=1.0e-06,   # section 5.2
    collapse_floor_rel=1.0e-06,
    plant_K=1.234e-03,          # section 6.5, both plants
    plant_min_shift_K=1.0e-05,  # section 6.5, the measurement-path plant
    replica_tol_K=1.0e-09,      # section 6.3
    replica_tol_q=1.0e-07,
    scheme_harmonic="Gauss harmonic corrected",
    scheme_linear="Gauss linear corrected",
    cap_core_s=300.0,
)

FROZEN_SHA = {
    "analyse_t9a.py":
        "dd2d6bf0ac690fdcca90719cb6586168763d311ea3b5a7ad937fdf054ecac9da",
    "exact_t9a.py":
        "d3f2558c1471ab3debd6e2804f58552e27b5708e18b81d219a2fe6d017d3d0b8",
    "T9a_registered.json":
        "66b03c7de15ceeba500dded8c496346023053ed2d0746de8749c324e1edb40ed",
    "check_t9a_mesh.py":
        "cb7fa05ab05d4751f0254419a199931f1d7cd7334d94075418ecad41c86688bc",
    "mark_done_t9a.py":
        "0feff87e148e1f69436a39f505f8fa8f49273f4c4669b41ad5bd9f4c6a7da669",
    "run_one_t9a.sh":
        "163c4345199cc8f2cfa1eb9406fedb8c44d3ff9f4d037f6b0d07eb495f8f2761",
    "run_chain_t9a.sh":
        "cbf3b957f5cd7d7a18f799112ca7936b824c2e37532515447fca575634999e7d",
    # copied into this tree before any case existed, so that build_t9aH.py
    # OVERRIDES the frozen builder rather than re-deriving it (disclosed in the
    # 2026-08-23 addendum to the pre-registration; changes no gate, threshold,
    # cap, band, reference or label)
    "build_t9a.py":
        "516fee581ecfaa25ffddefbb286de6b78c13b7bb9e9b635581958e4e9a2659e9",
}
T9A_READONLY_SHA = {
    "gate_t9a.json":
        "7c4c6826283f98d31e0c313cd713412b969bb2a4486b78ea31617eb1b3a5f4f8",
    "gate_t9aD.json":
        "96e0dce0ea8b57c069aa0f48060ebc9605c0ee3314ba7abf228de6440dc19993",
}

WALL_LEVELS = {"c": "W_c", "m": "W_m", "f": "W_f"}
FIN_LEVELS = {"c": "F_c", "m": "F_m", "f": "F_f"}
HARMONIC_CASES = ["W_c", "W_m", "W_f", "W_C3", "F_c", "F_m", "F_f",
                  "H40_f", "H4000_f"]
LINEAR_CASES = ["RL_f"]
ALL_CASES = HARMONIC_CASES + LINEAR_CASES


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# PURE DECISION FUNCTIONS.  Every verdict this instrument reaches is reached
# here, so that --selftest can exercise all of them with forged inputs and no
# OpenFOAM, no mesh and no case.  Nothing below calls sys.exit.
# ---------------------------------------------------------------------------
def grade_abs(tag, label, per_level, ref, tol, kind="abs_K"):
    """One absolute-distance row.  kind: 'abs_K' | 'rel' | 'abs'."""
    errs, worst, worst_level = {}, 0.0, None
    for lev, value in per_level.items():
        d = abs(value - ref)
        if kind == "rel":
            d = d / abs(ref)
        errs[lev] = d
        if d > worst:
            worst, worst_level = d, lev
    verdict = PASS if worst <= tol else GATE_FAIL
    return dict(row=tag, quantity=label, reference=ref, kind=kind,
                threshold=tol, errors=errs, worst=worst,
                worst_level=worst_level, verdict=verdict,
                levels=dict(per_level))


def grade_drop(tag, label, value, ref, tol, baseline_err, min_drop):
    """H4: the absolute bar AND a drop factor against a measured baseline.

    Registered honestly: at the registered numbers the ABSOLUTE bar is the
    binding one (drop < 1e6 needs |e1| > 6.5e-08 K, which already fails the
    1e-08 K bar).  The drop clause therefore binds only if the baseline read
    from gate_t9aD.json is not the registered -64.99408 mK, and it is kept as a
    cross-check on that read.  Section 4.4 of the pre-registration fixes both.
    """
    err = abs(value - ref)
    drop = (abs(baseline_err) / err) if err > 0 else float("inf")
    ok_abs, ok_drop = err <= tol, drop > min_drop
    return dict(row=tag, quantity=label, reference=ref, value=value,
                error=err, threshold=tol, drop=drop, min_drop=min_drop,
                baseline_error=baseline_err, abs_ok=ok_abs, drop_ok=ok_drop,
                verdict=PASS if (ok_abs and ok_drop) else GATE_FAIL)


def scheme_ok(fvschemes_text, expected):
    """Read laplacian(DT,T) back off disk.  Returns (ok, found_or_reason)."""
    m = re.search(r"laplacian\(DT,T\)\s+([^;]+);", fvschemes_text)
    if not m:
        return False, "no explicit laplacian(DT,T) entry"
    found = " ".join(m.group(1).split())
    return (found == expected), found


def plant_visible(delta, floor):
    """The measurement-path plant.  A zero from a reader not shown able to see
    a non-zero is not evidence, and this rung's headline is a set of zeros."""
    return abs(delta) >= floor


def collapse_fired(errors, floor):
    """True when every level error is below the floor: the triple has collapsed
    to round-off and NO order, Richardson extrapolate or GCI may be quoted."""
    return all(abs(e) < floor for e in errors)


def discrimination(null_arm_errors, thresholds):
    """Charter 2c.  null_arm_errors/thresholds keyed by row tag.

    Returns (met, fired_rows).  HC4 is MET when the registered null arm MISSES
    every threshold the hypothesis is graded on.  If the null MEETS any of them
    the discrimination set is empty for that row: it is REPORTED and NOT
    COUNTED toward the hypothesis.  This can only remove rows from the
    hypothesis's tally, never add one.
    """
    fired = [t for t, e in null_arm_errors.items() if abs(e) <= thresholds[t]]
    return (not fired), fired


def replica_ok(measured, published, tol_K, tol_q):
    """RC3: the new builder reproduces the frozen W_f, or every row is voided."""
    d = dict(T_i1=abs(measured["T_i1"] - published["T_i1"]),
             T_i2=abs(measured["T_i2"] - published["T_i2"]),
             q=abs(measured["q"] - published["q"]))
    return (d["T_i1"] <= tol_K and d["T_i2"] <= tol_K and d["q"] <= tol_q), d


def transcriptions_agree(reg_json):
    """The two transcriptions of section 4.  Disagreement REFUSES: the
    pre-registration governs and this instrument does not choose between them."""
    r, bad = reg_json["rows"], []

    def cmp(name, a, b):
        if a != b:
            bad.append(f"{name}: json {a!r} != code {b!r}")

    cmp("H1.tol", r["H1"]["tol"], REGH_CODE["tol_abs_K"])
    cmp("H2.tol", r["H2"]["tol"], REGH_CODE["tol_rel"])
    cmp("H3.tol", r["H3"]["tol"], REGH_CODE["tol_abs_K"])
    cmp("H4.tol", r["H4"]["tol"], REGH_CODE["tol_abs_K"])
    cmp("H4.min_drop", r["H4"]["min_drop"], REGH_CODE["min_drop"])
    cmp("H4.baseline", r["H4"]["baseline_e1_mK"], REGH_CODE["baseline_e1_mK"])
    cmp("H5.tol", r["H5"]["tol"], REGH_CODE["tol_abs_K"])
    cmp("H5.tol_rel", r["H5"]["tol_rel"], REGH_CODE["tol_rel"])
    cmp("H6.tol", r["H6"]["tol"], REGH_CODE["tol_fin"])
    t = reg_json["triple_state_rule"]
    cmp("collapse_floor_K", t["collapse_floor_K"], REGH_CODE["collapse_floor_K"])
    cmp("collapse_floor_rel", t["collapse_floor_rel"],
        REGH_CODE["collapse_floor_rel"])
    f = reg_json["refusals"]
    cmp("plant_K", f["RC5_planted_convergence"]["plant_K"], REGH_CODE["plant_K"])
    cmp("plant_min_shift", f["RC6_planted_measurement"]["min_visible_shift_K"],
        REGH_CODE["plant_min_shift_K"])
    cmp("replica_tol_K", f["RC3_replica"]["tol_K"], REGH_CODE["replica_tol_K"])
    cmp("replica_tol_q", f["RC3_replica"]["tol_q"], REGH_CODE["replica_tol_q"])
    s = reg_json["scheme"]
    cmp("scheme.harmonic", s["harmonic"], REGH_CODE["scheme_harmonic"])
    cmp("scheme.linear", s["linear"], REGH_CODE["scheme_linear"])
    cmp("cap_core_s", reg_json["cost"]["cap_core_s"], REGH_CODE["cap_core_s"])
    return (not bad), bad


# ---------------------------------------------------------------------------
# Exact references, re-derived at every run.  The frozen exact_t9a is imported
# unmodified; for the 40x and 4000x arms its WALL_LAYERS is overridden IN
# MEMORY for the duration of the derivation and RESTORED, and the restoration
# is asserted.  The file on disk is never touched.
# ---------------------------------------------------------------------------
def exact_wall(k2):
    """Both frozen routes at conductivity k2, or (None, reason) on disagreement."""
    saved = EX.WALL_LAYERS
    try:
        EX.WALL_LAYERS = ((0.05, 0.8), (0.10, k2), (0.02, 16.0))
        a = EX.wall_closed_form()
        b = EX.wall_numeric()
    finally:
        EX.WALL_LAYERS = saved
    assert EX.WALL_LAYERS == ((0.05, 0.8), (0.10, 0.04), (0.02, 16.0)), \
        "frozen exact_t9a.WALL_LAYERS was NOT restored"
    for key, tol in (("q", 1e-9), ("T_i1", 1e-11), ("T_i2", 1e-11)):
        rel = abs(a[key] - b[key]) / max(abs(a[key]), 1e-300)
        if rel > tol:
            return None, (f"the two frozen routes disagree at k2={k2} on "
                          f"{key}: {a[key]!r} vs {b[key]!r} (rel {rel:.2e})")
    return a, None


def with_k2(k2, fn, *args, **kwargs):
    """Run fn with the FROZEN comparator's registered layer-k map overridden in
    memory (the frozen measure_wall verifies every cell's DT against that map
    and would otherwise correctly refuse a 0.4 or 0.004 field).  Restored and
    asserted; the file on disk is never edited."""
    saved = copy.deepcopy(A.REG["wall"]["layers"])
    try:
        A.REG["wall"]["layers"][1]["k"] = k2
        return fn(*args, **kwargs)
    finally:
        A.REG["wall"]["layers"] = saved
        assert A.REG["wall"]["layers"][1]["k"] == 0.04, \
            "frozen analyse_t9a.REG layer-k map was NOT restored"


# ---------------------------------------------------------------------------
# planting
# ---------------------------------------------------------------------------
def plant_into_T(path, index, amount):
    """Add `amount` to one entry of a nonuniform scalar internalField, on a
    SCRATCH COPY outside the run tree.  Returns the new value, or (None,
    reason)."""
    txt = open(path, errors="replace").read()
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\n\s*(\d+)\s*\n"
                  r"\(\n(.*?)\n\)\s*;", txt, re.S)
    if not m:
        return None, f"{path} has no nonuniform internalField to plant into"
    vals = m.group(2).split("\n")
    if not (0 <= index < len(vals)):
        return None, f"plant index {index} outside {len(vals)} cells"
    new = float(vals[index]) + amount
    vals[index] = repr(new)
    body = "\n".join(vals)
    txt = txt[:m.start(2)] + body + txt[m.end(2):]
    open(path, "w").write(txt)
    return new, None


def scratch_copy(case):
    d = tempfile.mkdtemp(prefix="t9aH_planted_")
    dst = os.path.join(d, os.path.basename(case))
    shutil.copytree(case, dst)
    return d, dst


# ---------------------------------------------------------------------------
# the run.  Needs the ten solved cases; it does nothing until they exist.
# ---------------------------------------------------------------------------
def main():
    out = {"instrument": "analyse_t9aH.py (NEW -- read as source and as diff)",
           "rows": [], "controls": [], "refusals": {}, "cases": {}}

    # ---- RC1: the frozen files, and T9a_runs read-only ---------------------
    for name, want in FROZEN_SHA.items():
        got = sha256(os.path.join(HERE, name))
        out["refusals"][name] = got
        if got != want:
            A.refuse(f"REFUSE: {name} hashes {got}, not the frozen {want}")
    for name, want in T9A_READONLY_SHA.items():
        p = os.path.join(T9A_RUNS, name)
        got = sha256(p)
        out["refusals"][f"T9a_runs/{name}"] = got
        if got != want:
            A.refuse(f"REFUSE: T9a_runs/{name} MOVED ({got} != {want}); "
                     f"T9a_runs is read-only for this rung and every T9aH row "
                     f"is NOT A RESULT until that is explained")

    # ---- the two transcriptions of section 4 -------------------------------
    reg = json.load(open(os.path.join(HERE, "T9aH_registered.json")))
    ok, bad = transcriptions_agree(reg)
    if not ok:
        A.refuse("REFUSE: the registered JSON and this instrument's hard-coded "
                 "copy of section 4 disagree; the pre-registration governs and "
                 "this instrument does not choose between them: " + "; ".join(bad))

    # ---- RC4: the strict completion rule, all ten cases --------------------
    for c in ALL_CASES:
        fails = MARK.check(c)          # frozen six tests, incl. the age guard
        if fails:
            A.refuse(f"REFUSE: rung is PENDING -- {c} fails the strict "
                     f"completion rule: {fails}")

    # ---- RC2: the scheme, read back off disk -------------------------------
    for c in ALL_CASES:
        want = (REGH_CODE["scheme_harmonic"] if c in HARMONIC_CASES
                else REGH_CODE["scheme_linear"])
        txt = open(os.path.join(HERE, c, "system", "fvSchemes"),
                   errors="replace").read()
        good, found = scheme_ok(txt, want)
        out["cases"].setdefault(c, {})["laplacian(DT,T)"] = found
        if not good:
            A.refuse(f"REFUSE: {c} carries laplacian(DT,T) = {found!r}, "
                     f"not the registered {want!r}")

    # ---- exact references, both frozen routes ------------------------------
    exa, err = {}, None
    for tag, k2 in (("400x", 0.04), ("40x", 0.4), ("4000x", 0.004)):
        exa[tag], err = exact_wall(k2)
        if err:
            A.refuse("REFUSE: " + err)
        for key in ("q", "T_i1", "T_i2"):
            want = reg["exact_references"][tag][key]
            if abs(exa[tag][key] - want) > 1e-9 * max(1.0, abs(want)):
                A.refuse(f"REFUSE: derived {tag} {key} = {exa[tag][key]!r} "
                         f"disagrees with the registered {want!r}")
    out["exact_references"] = {t: exa[t] for t in exa}

    # ---- measurements ------------------------------------------------------
    mw = {l: A.measure_wall(os.path.join(HERE, WALL_LEVELS[l]))
          for l in ("c", "m", "f")}
    mf = {l: A.measure_fin(os.path.join(HERE, FIN_LEVELS[l]))
          for l in ("c", "m", "f")}
    m_c3 = A.measure_wall(os.path.join(HERE, "W_C3"))
    m_rl = A.measure_wall(os.path.join(HERE, "RL_f"))
    m_40 = with_k2(0.4, A.measure_wall, os.path.join(HERE, "H40_f"))
    m_4000 = with_k2(0.004, A.measure_wall, os.path.join(HERE, "H4000_f"))
    for name, m in (("W_c", mw["c"]), ("W_m", mw["m"]), ("W_f", mw["f"]),
                    ("F_c", mf["c"]), ("F_m", mf["m"]), ("F_f", mf["f"]),
                    ("W_C3", m_c3), ("RL_f", m_rl),
                    ("H40_f", m_40), ("H4000_f", m_4000)):
        out["cases"].setdefault(name, {}).update(m)

    # ---- RC3: the replica, and the builder as a controlled variable --------
    pub = json.load(open(os.path.join(T9A_RUNS, "gate_t9a.json")))
    w_f = pub["cases"]["W_f"]
    ok, d = replica_ok(m_rl, w_f, REGH_CODE["replica_tol_K"],
                       REGH_CODE["replica_tol_q"])
    out["refusals"]["RC3_replica"] = d
    if not ok:
        A.refuse(f"REFUSE: RL_f does not reproduce the frozen W_f ({d}); the "
                 f"rung's single-change claim would be a statement about a new "
                 f"builder, so every T9aH row is NOT A RESULT")

    # ---- RC5/RC6: the two planted controls, on scratch copies --------------
    for case in ("W_f", "H40_f"):
        tmp, dst = scratch_copy(os.path.join(HERE, case))
        try:
            t_last = A.latest_time(dst)
            ts = sorted((x for x in os.listdir(dst)
                         if re.fullmatch(r"\d+(\.\d+)?", x)), key=float)
            prev = ts[-2]
            if prev == t_last:
                A.refuse(f"REFUSE: {case} has no two checkpoints to compare")
            _, e = plant_into_T(os.path.join(dst, prev, "T"), 0,
                                REGH_CODE["plant_K"])
            if e:
                A.refuse("REFUSE: " + e)
            s = A.iterative_convergence(dst)
            out["refusals"][f"RC5_planted_convergence_{case}"] = s
            if (abs(s.get("max_change", 0.0) - REGH_CODE["plant_K"]) > 1e-12
                    or s.get("state") != "NOT_CONVERGED"):
                A.refuse(f"REFUSE: the convergence reader could not see a "
                         f"{REGH_CODE['plant_K']} K plant in {case}: {s}. "
                         f"Every row depending on a convergence zero is NOT A "
                         f"RESULT.")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    tmp, dst = scratch_copy(os.path.join(HERE, "W_f"))
    try:
        t_last = A.latest_time(dst)
        Cx, _, _ = A.cell_centres(dst, t_last)
        order = sorted(range(len(Cx)), key=lambda i: Cx[i])
        x1 = A.REG["wall"]["interfaces_x"][0]
        idx = max((i for i in order if Cx[i] < x1), key=lambda i: Cx[i])
        before = A.measure_wall(dst)["T_i1"]
        _, e = plant_into_T(os.path.join(dst, t_last, "T"), idx,
                            REGH_CODE["plant_K"])
        if e:
            A.refuse("REFUSE: " + e)
        after = A.measure_wall(dst)["T_i1"]
        shift = after - before
        out["refusals"]["RC6_planted_measurement"] = dict(
            cell=idx, x=Cx[idx], before=before, after=after, shift=shift,
            floor=REGH_CODE["plant_min_shift_K"])
        if not plant_visible(shift, REGH_CODE["plant_min_shift_K"]):
            A.refuse(f"REFUSE: a {REGH_CODE['plant_K']} K plant in the cell at "
                     f"the interface moved T_i1 by {shift:.3e} K, below the "
                     f"registered {REGH_CODE['plant_min_shift_K']:.1e} K floor. "
                     f"The near-zero H1/H2/H3 errors are NOT evidence and every "
                     f"H row is NOT A RESULT.")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ---- rows H1-H6 --------------------------------------------------------
    e400 = exa["400x"]
    rows = [
        grade_abs("H1", "wall T interface 1 [K], 400x, every level",
                  {l: mw[l]["T_i1"] for l in mw}, e400["T_i1"],
                  REGH_CODE["tol_abs_K"], "abs_K"),
        grade_abs("H2", "wall q'' [W/m2], 400x, every level",
                  {l: mw[l]["q"] for l in mw}, e400["q"],
                  REGH_CODE["tol_rel"], "rel"),
        grade_abs("H3", "wall T interface 2 [K], 400x, every level",
                  {l: mw[l]["T_i2"] for l in mw}, e400["T_i2"],
                  REGH_CODE["tol_abs_K"], "abs_K"),
        grade_drop("H4", "wall T interface 1 [K], 40x contrast",
                   m_40["T_i1"], exa["40x"]["T_i1"], REGH_CODE["tol_abs_K"],
                   abs(REGH_CODE["baseline_e1_mK"]) * 1e-3,
                   REGH_CODE["min_drop"]),
    ]
    h5a = grade_abs("H5a", "wall T interface 1 [K], 4000x contrast",
                    {"f": m_4000["T_i1"]}, exa["4000x"]["T_i1"],
                    REGH_CODE["tol_abs_K"], "abs_K")
    h5b = grade_abs("H5b", "wall q'' [W/m2], 4000x contrast",
                    {"f": m_4000["q"]}, exa["4000x"]["q"],
                    REGH_CODE["tol_rel"], "rel")
    rows.append(dict(row="H5", quantity="4000x contrast: T_i1 and q''",
                     parts=[h5a, h5b], threshold=REGH_CODE["tol_abs_K"],
                     verdict=(PASS if h5a["verdict"] == PASS
                              and h5b["verdict"] == PASS else GATE_FAIL)))
    t9a_fin = {l: pub["cases"][FIN_LEVELS[l]] for l in ("c", "m", "f")}
    h6 = grade_abs("H6", "fin eta and tip ratio vs T9a published (SPECIFICITY, "
                         "close to an identity, counted toward nothing)",
                   {f"{l}_{k}": mf[l][k] for l in mf
                    for k in ("eta", "tip_ratio")},
                   0.0, REGH_CODE["tol_fin"], "abs")
    h6["errors"] = {f"{l}_{k}": abs(mf[l][k] - t9a_fin[l][k])
                    for l in mf for k in ("eta", "tip_ratio")}
    h6["worst"] = max(h6["errors"].values())
    h6["verdict"] = PASS if h6["worst"] <= REGH_CODE["tol_fin"] else GATE_FAIL
    h6["counted_toward_hypothesis"] = False
    rows.append(h6)
    out["rows"] = rows

    # ---- controls HC1-HC4 --------------------------------------------------
    ks = [ly["k"] for ly in A.REG["wall"]["layers"]]
    q_c1 = (sum(ks) / len(ks)) * (A.REG["wall"]["T_hot"]
                                  - A.REG["wall"]["T_cold"]) \
        / A.REG["wall"]["total_thickness"]
    hc1 = abs(mw["f"]["q"] - q_c1) / q_c1 > REGH_CODE["tol_rel"]
    hc2 = abs(mf["f"]["eta"] - 1.0) > REGH_CODE["tol_fin"]
    hc3 = (abs(m_c3["T_i1"] - e400["T_i1"]) > REGH_CODE["tol_abs_K"]
           and abs(m_c3["T_i2"] - e400["T_i2"]) > REGH_CODE["tol_abs_K"]
           and abs(m_c3["q"] - e400["q"]) / abs(e400["q"]) > REGH_CODE["tol_rel"])
    null_err = {"H1": m_rl["T_i1"] - e400["T_i1"],
                "H2": (m_rl["q"] - e400["q"]) / abs(e400["q"]),
                "H3": m_rl["T_i2"] - e400["T_i2"]}
    hc4_met, fired = discrimination(
        null_err, {"H1": REGH_CODE["tol_abs_K"], "H2": REGH_CODE["tol_rel"],
                   "H3": REGH_CODE["tol_abs_K"]})
    for r in out["rows"]:
        if r["row"] in fired:
            r["counted_toward_hypothesis"] = False
            r["why_not_counted"] = ("the registered null arm RL_f MEETS this "
                                    "row's threshold: the discrimination set "
                                    "is EMPTY (Charter 2c), so the row is "
                                    "REPORTED and NOT COUNTED")
    out["controls"] = [
        dict(control="HC1_arithmetic_mean_conductivity", must="FAIL H2's bar",
             met=hc1),
        dict(control="HC2_perfect_fin", must="FAIL H6's bar", met=hc2),
        dict(control="HC3_uniform_wall_solved_trivial_baseline",
             must="FAIL H1, H2 and H3", met=hc3),
        dict(control="HC4_null_arm_RL_f_Gauss_linear",
             must="FAIL H1, H2 and H3", met=hc4_met,
             null_errors=null_err, rows_not_counted=fired),
    ]

    # ---- the triple state, printed beside every wall row, graded by none ----
    for key, tag in (("q", "H2"), ("T_i1", "H1"), ("T_i2", "H3")):
        tri = A.gci(mw["c"][key], mw["m"][key], mw["f"][key])
        floor = (REGH_CODE["collapse_floor_rel"] if key == "q"
                 else REGH_CODE["collapse_floor_K"])
        errs = [abs(mw[l][key] - e400[key]) / (abs(e400[key]) if key == "q"
                                               else 1.0) for l in ("c", "m", "f")]
        for r in out["rows"]:
            if r["row"] == tag:
                r["grid_triple_reported_never_graded"] = tri.get("state")
                r["collapse_floor_fired"] = collapse_fired(errs, floor)
                r["order_quoted"] = not r["collapse_floor_fired"]

    with open(os.path.join(HERE, "gate_t9aH.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)

    counted = [r for r in out["rows"]
               if r.get("counted_toward_hypothesis", True)]
    fails = [r for r in out["rows"] if r["verdict"] == GATE_FAIL]
    unmet = [c for c in out["controls"] if not c["met"]]
    print(f"\n  {len(out['rows'])} registered rows, "
          f"{sum(1 for r in out['rows'] if r['verdict'] == PASS)} PASS, "
          f"{len(fails)} GATE FAIL; {len(counted)} counted toward the "
          f"hypothesis (H6 is a specificity row and counts toward nothing)")
    print(f"  {len(out['controls'])} controls, {len(unmet)} NOT MET"
          + ("" if not unmet else " -- "
             + ", ".join(c["control"] for c in unmet)))
    print("  THIS INSTRUMENT ARMS NO BAND AND QUOTES NO GCI.  The frozen "
          "comparator's own verdicts (FR0-FR4, C1-C3) are whatever it printed, "
          "and are NOT re-graded here.")
    return EXIT_FAIL if (fails or unmet) else EXIT_OK


# ---------------------------------------------------------------------------
# --selftest: forged inputs only.  No case, no mesh, no OpenFOAM, no solver.
# Every refusal is tested in BOTH directions: it must fire when it should and
# stay silent when it should not.
# ---------------------------------------------------------------------------
def selftest():
    n_ok = n_bad = 0

    def chk(name, cond):
        nonlocal n_ok, n_bad
        if cond:
            n_ok += 1
            print(f"  ok    {name}")
        else:
            n_bad += 1
            print(f"  FAIL  {name}")

    print("T9aH instrument selftest -- forged inputs, zero solver compute\n")

    # -- the frozen files are the frozen files -------------------------------
    for name, want in FROZEN_SHA.items():
        chk(f"frozen {name} hashes {want[:8]}...",
            sha256(os.path.join(HERE, name)) == want)

    # -- the two transcriptions of section 4 agree, and a mutation refuses ----
    reg = json.load(open(os.path.join(HERE, "T9aH_registered.json")))
    ok, bad = transcriptions_agree(reg)
    chk("registered JSON agrees with the hard-coded copy of section 4", ok)
    mutated = copy.deepcopy(reg)
    mutated["rows"]["H1"]["tol"] = 1.0e-06      # a WIDER bar, the classic drift
    ok2, bad2 = transcriptions_agree(mutated)
    chk("a widened H1 threshold in the JSON is REFUSED, not adopted",
        (not ok2) and any("H1.tol" in b for b in bad2))

    # -- exact references, both frozen routes, three contrasts ---------------
    want = {"400x": (0.04, 19.502681618722573, 348.7810823988298,
                     300.0243783520234),
            "40x": (0.4, 159.3625498007968, 340.0398406374502, 300.199203187251),
            "4000x": (0.004, 1.9949129719216, 349.8753179392549,
                      300.0024936412149)}
    for tag, (k2, q, t1, t2) in want.items():
        a, err = exact_wall(k2)
        chk(f"exact {tag}: both frozen routes agree and reproduce section 3",
            err is None and abs(a["q"] - q) < 1e-9 and abs(a["T_i1"] - t1) < 1e-9
            and abs(a["T_i2"] - t2) < 1e-9)
    chk("frozen exact_t9a.WALL_LAYERS restored after every override",
        EX.WALL_LAYERS == ((0.05, 0.8), (0.10, 0.04), (0.02, 16.0)))
    with_k2(0.4, lambda: None)
    chk("frozen analyse_t9a.REG layer-k map restored after every override",
        A.REG["wall"]["layers"][1]["k"] == 0.04)

    # -- H1: the T9a-D numbers pass; a residual above the bar fails -----------
    ref = 348.7810823988298
    good = {"c": ref, "m": ref - 3.2e-12, "f": ref - 3.0e-12}
    chk("H1 PASSES on T9a-D's measured harmonic residuals (0/3.2e-12/3.0e-12 K)",
        grade_abs("H1", "", good, ref, REGH_CODE["tol_abs_K"])["verdict"] == PASS)
    bad_lv = dict(good, c=ref - 1.0e-07)
    chk("H1 GATE FAILS when ONE level (the coarse one) sits at 1e-07 K",
        grade_abs("H1", "", bad_lv, ref, REGH_CODE["tol_abs_K"])["verdict"]
        == GATE_FAIL)
    chk("H1 GATE FAILS on the frozen Gauss linear residual (-2.41e-03 K)",
        grade_abs("H1", "", {"f": ref - 2.40918e-03}, ref,
                  REGH_CODE["tol_abs_K"])["verdict"] == GATE_FAIL)
    # The boundary is forged at a magnitude where the error is EXACTLY
    # representable.  Forging it as (348.78... + 1e-08) does not test the
    # comparison: the nearest double to that sum sits 1.0000008e-08 from the
    # reference, above the bar, so such a row GATE FAILS on float construction
    # rather than on its verdict rule.  Recorded because the first version of
    # this selftest made exactly that mistake and the selftest caught it.
    chk("H1 PASSES exactly AT the threshold and FAILS just above it "
        "(error forged exactly)",
        grade_abs("H1", "", {"f": 1.0e-08}, 0.0,
                  REGH_CODE["tol_abs_K"])["verdict"] == PASS
        and grade_abs("H1", "", {"f": 1.0e-08 * (1 + 1e-9)}, 0.0,
                      REGH_CODE["tol_abs_K"])["verdict"] == GATE_FAIL)
    chk("H1 GATE FAILS 10x above the bar on a 348 K field",
        grade_abs("H1", "", {"f": ref + 1.0e-07}, ref,
                  REGH_CODE["tol_abs_K"])["verdict"] == GATE_FAIL)

    # -- SUPERVISOR-REQUIRED 1: an invisible measurement plant REFUSES --------
    chk("FORGED: a plant that moves T_i1 by 0.0 K is INVISIBLE -> refusal fires",
        not plant_visible(0.0, REGH_CODE["plant_min_shift_K"]))
    chk("FORGED: a plant that moves T_i1 by 1e-09 K is still invisible",
        not plant_visible(1.0e-09, REGH_CODE["plant_min_shift_K"]))
    chk("a plant that moves T_i1 by the expected 1.18e-03 K is VISIBLE",
        plant_visible(1.18e-03, REGH_CODE["plant_min_shift_K"]))

    # -- SUPERVISOR-REQUIRED 2: a null arm that MEETS H1 empties the set ------
    thr = {"H1": REGH_CODE["tol_abs_K"], "H2": REGH_CODE["tol_rel"],
           "H3": REGH_CODE["tol_abs_K"]}
    met, fired = discrimination({"H1": -2.40918e-03, "H2": 1.8e-02,
                                 "H3": -5.07e-04}, thr)
    chk("the REAL null arm (Gauss linear) misses every bar -> HC4 MET, rows "
        "counted", met and fired == [])
    met2, fired2 = discrimination({"H1": 1.0e-12, "H2": 1.8e-02,
                                   "H3": -5.07e-04}, thr)
    chk("FORGED: a null arm that MEETS H1 -> HC4 NOT MET and H1 is not counted",
        (not met2) and fired2 == ["H1"])
    met3, fired3 = discrimination({"H1": 1e-12, "H2": 1e-12, "H3": 1e-12}, thr)
    chk("FORGED: a null arm meeting all three -> all three uncounted",
        (not met3) and sorted(fired3) == ["H1", "H2", "H3"])

    # -- SUPERVISOR-REQUIRED 3: an fvSchemes readback mismatch REFUSES --------
    good_txt = ("laplacianSchemes { default Gauss harmonic corrected; }\n"
                "laplacian(DT,T)  Gauss harmonic corrected;\n")
    ok_h, found = scheme_ok(good_txt, REGH_CODE["scheme_harmonic"])
    chk("a matching harmonic readback is accepted", ok_h and found ==
        REGH_CODE["scheme_harmonic"])
    forged = ("laplacianSchemes { default Gauss harmonic corrected; }\n"
              "laplacian(DT,T)  Gauss linear corrected;\n")
    ok_f, found_f = scheme_ok(forged, REGH_CODE["scheme_harmonic"])
    chk("FORGED: a case whose laplacian(DT,T) says Gauss linear -> refusal "
        "fires", (not ok_f) and found_f == REGH_CODE["scheme_linear"])
    ok_m, why = scheme_ok("laplacianSchemes { default Gauss linear corrected; }",
                          REGH_CODE["scheme_harmonic"])
    chk("FORGED: a case with NO explicit laplacian(DT,T) entry -> refusal fires",
        (not ok_m) and "no explicit" in why)
    chk("the null arm's own linear entry is accepted as linear",
        scheme_ok(forged, REGH_CODE["scheme_linear"])[0])

    # -- the frozen triple classifier, over constructed triples --------------
    chk("frozen gci: EXACT triple (medium == fine)",
        A.gci(2.0, 1.0, 1.0)["state"] == "EXACT")
    chk("frozen gci: OSCILLATORY triple",
        A.gci(1.0, 2.0, 1.0)["state"] == "OSCILLATORY")
    st = A.gci(10.0 + 1.6 ** 2, 10.0 + 1.6, 10.0 + 1.0)
    chk("frozen gci: CONVERGING first-order triple reads p = 1",
        st["state"] == "CONVERGING" and abs(st["order"] - 1.0) < 1e-12)
    st2 = A.gci(10.0 + 1.6 ** 4, 10.0 + 1.6 ** 2, 10.0 + 1.0)
    chk("frozen gci: CONVERGING second-order triple reads p = 2",
        st2["state"] == "CONVERGING" and abs(st2["order"] - 2.0) < 1e-12)
    # STAGNANT needs 1 < |e32/e21| < 1.6^0.5, DIVERGENT needs |e32/e21| <= 1
    # with the SAME sign (opposite signs are OSCILLATORY, one branch earlier).
    chk("frozen gci: STAGNANT triple (p < 0.5) arms NO band",
        A.gci(3.1, 2.0, 1.0)["state"] == "STAGNANT"
        and "GCI_pct" not in A.gci(3.1, 2.0, 1.0))
    chk("frozen gci: DIVERGENT triple (p <= 0) arms NO band",
        A.gci(11.5, 11.0, 10.0)["state"] == "DIVERGENT"
        and "GCI_pct" not in A.gci(11.5, 11.0, 10.0))
    chk("frozen gci: opposite-signed differences are OSCILLATORY, not "
        "DIVERGENT", A.gci(10.5, 11.0, 10.0)["state"] == "OSCILLATORY")
    chk("T9a-D's own m/f/x triple still reads STAGNANT here",
        A.gci(348.777747338, 348.778673215, 348.779544025)["state"] == "STAGNANT")

    # -- the collapse floor --------------------------------------------------
    chk("collapse floor FIRES on T9a-D's harmonic residuals -> no order quoted",
        collapse_fired([0.0, 3.2e-12, 3.0e-12], REGH_CODE["collapse_floor_K"]))
    chk("collapse floor does NOT fire on T9a's own linear errors",
        not collapse_fired([5.43e-03, 3.34e-03, 2.41e-03],
                           REGH_CODE["collapse_floor_K"]))

    # -- H4's two clauses ----------------------------------------------------
    t40 = 340.0398406374502
    base = abs(REGH_CODE["baseline_e1_mK"]) * 1e-3
    r = grade_drop("H4", "", t40 - 3.0e-12, t40, REGH_CODE["tol_abs_K"], base,
                   REGH_CODE["min_drop"])
    chk("H4 PASSES at the predicted residual (drop ~2e+10)",
        r["verdict"] == PASS and r["drop"] > 1e9)
    r2 = grade_drop("H4", "", t40 - 7.0e-08, t40, REGH_CODE["tol_abs_K"], base,
                    REGH_CODE["min_drop"])
    chk("FORGED: a residual of 7e-08 K at 40x GATE FAILS both clauses "
        "(the C1 contrast-growth falsifier)",
        r2["verdict"] == GATE_FAIL and not r2["abs_ok"] and not r2["drop_ok"])
    r3 = grade_drop("H4", "", t40 - 3.0e-12, t40, REGH_CODE["tol_abs_K"],
                    1.0e-09, REGH_CODE["min_drop"])
    chk("FORGED: a corrupted baseline read makes the DROP clause fire on its "
        "own", r3["verdict"] == GATE_FAIL and r3["abs_ok"] and not r3["drop_ok"])

    # -- the replica refusal -------------------------------------------------
    pubw = dict(T_i1=348.778673215, T_i2=300.023872, q=19.854990714)
    ok_r, d = replica_ok(dict(pubw), pubw, REGH_CODE["replica_tol_K"],
                         REGH_CODE["replica_tol_q"])
    chk("replica reproducing W_f exactly is accepted", ok_r)
    off = dict(pubw, T_i1=pubw["T_i1"] + 1.0e-06)
    chk("FORGED: a replica 1e-06 K off W_f -> refusal fires (every row NOT A "
        "RESULT)",
        not replica_ok(off, pubw, REGH_CODE["replica_tol_K"],
                       REGH_CODE["replica_tol_q"])[0])

    # -- the builder writes what this instrument reads back ------------------
    import build_t9aH as BH        # no case is written by importing it
    for scheme in (REGH_CODE["scheme_harmonic"], REGH_CODE["scheme_linear"]):
        txt = BH.fv_schemes(scheme)
        ok_rt, found_rt = scheme_ok(txt, scheme)
        chk(f"builder writes and instrument reads back {scheme!r} unchanged",
            ok_rt and found_rt == scheme)
    chk("the builder's single-change proof accepts only the registered change",
        "laplacian(DT,T)" in BH.fv_schemes(REGH_CODE["scheme_harmonic"])
        and "Gauss harmonic corrected" in
        BH.fv_schemes(REGH_CODE["scheme_harmonic"]))
    tmp_g = tempfile.mkdtemp(prefix="t9aH_guard_")
    try:
        os.makedirs(os.path.join(tmp_g, "case", "1000"))
        fired_guard = False
        try:
            BH.guard(os.path.join(tmp_g, "case"), "case")
        except SystemExit:
            fired_guard = True
        chk("FORGED: the builder REFUSES a case that already holds a time "
            "directory", fired_guard)
    finally:
        shutil.rmtree(tmp_g, ignore_errors=True)

    # -- the strict completion rule is really wired to the frozen tests ------
    chk("frozen mark_done_t9a.check refuses a case that does not exist",
        bool(MARK.check("NO_SUCH_CASE")))
    src = open(os.path.join(HERE, "mark_done_t9a.py")).read()
    chk("the frozen completion rule still carries the age guard (0/T test)",
        "OLDER than 0/T" in src and "getmtime" in src)

    # -- T9a is read-only ----------------------------------------------------
    for name, wanted in T9A_READONLY_SHA.items():
        p = os.path.join(T9A_RUNS, name)
        chk(f"T9a_runs/{name} unchanged ({wanted[:8]}...)",
            os.path.isfile(p) and sha256(p) == wanted)

    print(f"\n  selftest: {n_ok} checks passed, {n_bad} failed")
    if n_bad:
        print("  REFUSING: the instrument does not grade until its own "
              "selftest passes.")
    return EXIT_OK if n_bad == 0 else EXIT_REFUSE


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(main())
