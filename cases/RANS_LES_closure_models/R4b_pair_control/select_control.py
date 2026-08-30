#!/usr/bin/env python3
"""R4b instrument A1 - the control-value selector.

Implements `R4b_pair_control/PREREGISTRATION.md` sec. 3.4 EXACTLY:

    xi* = max { xi in G : for every training case c, for every cell in mask(c),
                b_total = b_lin + xi * b^Delta_model(c)
                is realisable at tol = 1e-6,
                and max_cell ||b_total||_F <= sqrt(2/3) }

with, all frozen there and re-stated here as module constants so a reader can
see them without opening the registration:

  * the grid G     - twelve values, fixed, NEVER refined afterwards;
  * the cell mask  - EXACTLY R4's fit mask, `fs3_select.py` lines 89-90,
                     re-used unmodified (172,106 of 172,171 cells);
  * realisability  - `_common/of_read.realisability_violation`, re-used
                     unmodified (Schumann barycentric, all three >= -tol);
  * b_lin          - the frozen dataset's own `b_lin` column, the same one
                     `score_apriori.py` reads;
  * b^Delta_model  - R4's discovered SpaRTA b^Delta, read from R4's committed
                     `MODEL.json`, evaluated as sum_j c_j * CT[name_j], the
                     same expression `score_apriori.py` uses.

REGISTERED REFUSALS (`INSTRUMENT_BUILD_PREREGISTRATION.md` sec. 2.2), each an
explicit `SystemExit(2)` and NEVER an `assert` -- L-332: `python3 -O` deletes
`assert`, so a refusal written as one is erased in exactly the configuration a
production run is most likely to use.  This module contains ZERO `ast.Assert`
nodes and `--selftest` proves it by parsing its own source.

  R1  exit 2 if no reader control passes (the birth requirement, sec. 5.0);
  R2  BLOCKED, and NEVER `xi* = 0`, if no grid value is feasible -- a zero
      control is the linear EVM and would propagate nothing.  BLOCKED exits 3,
      deliberately distinct from the refusal code 2, so the two outcomes can
      never be confused by a caller;
  R3  exit 2 if it is asked to select on anything but realisability.  Selecting
      `xi` on `b_rms` would be calibration on the quantity gate G1 grades, and
      selecting it on convergence is R4's departure D-7.

THE BIRTH REQUIREMENT (sec. 5.0), and it is two-sided.  Sanaa, 2026-08-28:
"A planted control must travel the real production path -- written by the real
producer's code, read through the real reader -- and prove the instrument sees
a non-zero the same way reality would deliver one.  A control that empties the
tuple it tests, or writes a schema the producer never emits, tests nothing and
certifies blindness."  So `--birth` plants into a SCRATCH COPY of a REAL
`bijDelta` written by the frozen extraction, never into a synthetic string and
never into an original, and both halves are graded:

  G0a positive - the plant is recovered through THIS module's reader;
  G0a negative - an unperturbed copy of the same real file, through the same
                 rewrite-and-read path, moves NOTHING;
  G0e positive - one cell of the real total-b array forced to a known
                 non-realisable state (a barycentric coordinate driven to
                 -1e-3); the violating count must rise by EXACTLY ONE, not
                 "by at least one", which a routine that flags everything also
                 satisfies;
  G0e negative - the unperturbed copy of the same array raises the count by
                 zero.
  G0f          - `NASA_2DWMH` inside a case list handed to the zero-shot guard.

THIS MODULE WRITES ONLY UNDER `/home/ubuntu/closure-data/r4b_instruments/`.
`/home/ubuntu/closure-data/r4b/` is R4b's SOLVE run root; its absence is R4b's
own pre-compute condition, and writing there would close R4b's amendment window
before Sanaa has ruled on the increment.  `guard_write_root()` refuses any
destination inside it.
"""
from __future__ import annotations

import argparse
import ast
import datetime
import hashlib
import json
import os
import re
import shutil
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CLOSURE = os.path.dirname(HERE)                      # .../RANS_LES_closure_models
sys.path.insert(0, os.path.join(CLOSURE, "R4_sparta_build"))
sys.path.insert(0, os.path.join(CLOSURE, "_common"))

import r4_lib as R                                                  # noqa: E402
from of_read import read_field, realisability_violation, barycentric  # noqa: E402

# ------------------------------------------------------------------ frozen
# PREREGISTRATION sec. 3.4.  Twelve values, fixed there, not refined here.
GRID = (0.01, 0.02, 0.03, 0.05, 0.07, 0.10, 0.15, 0.20, 0.30, 0.50, 0.70, 1.00)
TOL = 1e-6                                  # realisability tolerance, sec. 3.4
FROB_MAX = float(np.sqrt(2.0 / 3.0))        # 0.8164966, sec. 3.4
CRITERION = "realisability"                 # the ONLY legal selection criterion

DATASET = os.path.join(R.WORK, "dataset")   # /home/ubuntu/closure-data/r4/dataset
R4_MODEL = os.path.join(CLOSURE, "R4_sparta_build", "MODEL.json")

INSTRUMENT_ROOT = "/home/ubuntu/closure-data/r4b_instruments"
SOLVE_ROOT = "/home/ubuntu/closure-data/r4b"   # R4b's own; MUST stay absent

# The reader this module uses for every OpenFOAM field it reads.  Bound here,
# by name, so the birth demonstration provably exercises THE SAME object the
# production path uses -- not a look-alike passed in by a test.
READER = read_field

DEMO_PROVENANCE = (
    "DEMONSTRATION - NOT THE REGISTERED MODEL. Written by R4b-I's birth "
    "demonstration under INSTRUMENT_BUILD_PREREGISTRATION.md. R4b's registered "
    "MODEL.json is produced by a fresh run under R4b/PREREGISTRATION.md "
    "section 14 commit 2, after Sanaa has directed the increment.")


# ------------------------------------------------------------- refusals
def refuse(code, msg):
    """Every refusal in this module. NEVER an `assert` (L-332)."""
    sys.stderr.write(f"REFUSED [{code}] {msg}\n")
    raise SystemExit(2)


def require(cond, code, msg):
    if not cond:
        refuse(code, msg)


def blocked(msg, record=None, path=None):
    """sec. 3.4 R2: BLOCKED is a verdict, not a refusal, and is NEVER xi* = 0."""
    if record is not None and path is not None:
        write_json(path, record)
    sys.stderr.write(f"BLOCKED {msg}\n")
    raise SystemExit(3)


def guard_write_root(path):
    """Refuse any write inside R4b's SOLVE run root (sec. 3.3)."""
    p = os.path.abspath(path)
    require(p != os.path.abspath(SOLVE_ROOT)
            and not p.startswith(os.path.abspath(SOLVE_ROOT) + os.sep),
            "SOLVE-ROOT-GUARD",
            f"{p} is inside R4b's solve run root {SOLVE_ROOT}; writing there "
            f"would destroy R4b's pre-compute condition")
    return p


def write_json(path, obj):
    guard_write_root(path)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1)
        fh.write("\n")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")


# --------------------------------------------------------------- the mask
def fit_mask(z):
    """R4's fit mask, `fs3_select.py` lines 89-90, re-used UNMODIFIED.

    Copied term for term, not paraphrased: the LES anisotropy is undefined
    where the SHIPPED k_LES is non-positive, and b^Delta there is O(1e5)
    nonsense.  Selects 172,106 of 172,171 cells over the 12 training cases.
    """
    kraw, kDef, CR, bDel, CT = (z["k_les_raw"], z["kDef"], z["CR"],
                                z["bDel"], z["CT"])
    return ((kraw > 0) & np.isfinite(kDef) & np.isfinite(CR).all(axis=0)
            & np.isfinite(bDel).all(axis=(1, 2))
            & np.isfinite(CT).all(axis=(0, 2, 3)))


def load_case(dataset, case, cand_names, bdelta_names, bdelta_terms):
    """-> (b_lin[mask], b^Delta_model[mask], n_cells, n_used)."""
    z = np.load(os.path.join(dataset, case + ".npz"))
    ok = fit_mask(z)
    b_lin = z["b_lin"][ok]
    CT = z["CT"]
    b_mod = np.zeros_like(b_lin)
    for nm, term in zip(bdelta_names, bdelta_terms):
        coef = float(term[3])
        b_mod = b_mod + coef * CT[cand_names.index(nm)][ok]
    return b_lin, b_mod, int(ok.size), int(ok.sum())


# ------------------------------------------------------- the selection
def feasibility_at(b_lin, b_mod, xi):
    """sec. 3.4, one case at one grid value. Realisability AND the Frobenius cap."""
    b_tot = b_lin + xi * b_mod
    viol, mn = realisability_violation(b_tot, tol=TOL)
    frob = np.sqrt((b_tot ** 2).sum(axis=(1, 2)))
    n_viol = int(viol.sum())
    imax = int(np.argmax(frob))
    imin = int(np.argmin(mn))
    return dict(n_violating=n_viol,
                min_barycentric_coordinate=float(mn.min()),
                worst_cell_index=imin,
                max_frobenius_norm=float(frob.max()),
                max_frobenius_cell_index=imax,
                realisable=bool(n_viol == 0),
                within_frobenius_cap=bool(float(frob.max()) <= FROB_MAX),
                feasible=bool(n_viol == 0 and float(frob.max()) <= FROB_MAX))


def select(dataset, model_path, cases=None, criterion=CRITERION):
    """sec. 3.4.  Returns the full record: xi*, the grid, EVERY grid value's
    feasibility result, and the binding case and cell."""
    # R3 - the registered refusal.  xi is chosen on realisability ALONE.
    require(criterion == CRITERION, "CRITERION",
            f"sec. 3.4 registers selection on {CRITERION!r} alone; "
            f"{criterion!r} was asked for. Selecting xi on b_rms would be "
            f"calibration on the quantity gate G1 grades; selecting it on "
            f"convergence is R4's departure D-7.")

    man = json.load(open(os.path.join(dataset, "dataset_manifest.json")))
    cand_names = list(man["candidates"])
    if cases is None:
        cases = sorted(man["cases"])
    R.assert_no_test_case(cases)            # G0f, the zero-shot guard
    zero_shot = zero_shot_guard(cases)      # ... and the -O-proof re-assertion

    model = json.load(open(model_path))
    bnames = list(model["bDelta"]["names"])
    bterms = [list(t) for t in model["bDelta"]["terms"]]

    per_case, n_cells, n_used = {}, 0, 0
    loaded = {}
    for c in cases:
        b_lin, b_mod, nc, nu = load_case(dataset, c, cand_names, bnames, bterms)
        loaded[c] = (b_lin, b_mod)
        per_case[c] = dict(n_cells=nc, n_cells_fitted=nu)
        n_cells += nc
        n_used += nu

    # EVERY grid value is evaluated and reported.  A selector that short-
    # circuits at the first infeasible value cannot report twelve rows, so the
    # registration's "12 of 12 reported" requirement makes the shortcut visible.
    grid_results = []
    for xi in GRID:
        rows = {c: feasibility_at(loaded[c][0], loaded[c][1], xi) for c in cases}
        worst_case = min(rows, key=lambda c: rows[c]["min_barycentric_coordinate"])
        frob_case = max(rows, key=lambda c: rows[c]["max_frobenius_norm"])
        grid_results.append(dict(
            xi=xi,
            feasible=bool(all(r["feasible"] for r in rows.values())),
            n_violating_total=int(sum(r["n_violating"] for r in rows.values())),
            min_barycentric_coordinate=rows[worst_case]["min_barycentric_coordinate"],
            binding_case=worst_case,
            binding_cell_index=rows[worst_case]["worst_cell_index"],
            max_frobenius_norm=rows[frob_case]["max_frobenius_norm"],
            max_frobenius_case=frob_case,
            max_frobenius_cell_index=rows[frob_case]["max_frobenius_cell_index"],
            per_case=rows))

    feasible = [g for g in grid_results if g["feasible"]]
    record = dict(
        criterion=CRITERION,
        criterion_note="xi is chosen on realisability ALONE (sec. 3.4): not on "
                       "b_rms, not on any a-posteriori quantity, not on "
                       "convergence, and not on any test or validation case.",
        grid=list(GRID),
        realisability_tolerance=TOL,
        frobenius_cap=FROB_MAX,
        n_grid_values_evaluated=len(grid_results),
        grid_results=grid_results,
        training_cases=list(cases),
        n_cases=len(cases),
        n_cells_total=n_cells,
        n_cells_fitted=n_used,
        mask_source="R4 fit mask, fs3_select.py lines 89-90, re-used unmodified",
        realisability_instrument="_common/of_read.realisability_violation",
        b_lin_source="frozen dataset column `b_lin` (the one score_apriori.py reads)",
        source_model=dict(path=os.path.abspath(model_path),
                          sha256=sha256_file(model_path),
                          bDelta_names=bnames, bDelta_terms=bterms,
                          R_terms=[list(t) for t in model["R"]["terms"]]),
        zero_shot_guard=zero_shot,
        per_case=per_case)

    if not feasible:
        record["xi_star"] = None
        record["verdict"] = "BLOCKED"
        record["blocked_reason"] = (
            "No value on the frozen 12-value grid is feasible. sec. 3.4: "
            "xi* = 0 is NOT used -- a zero control is the linear EVM and would "
            "propagate nothing.")
        return record

    best = max(feasible, key=lambda g: g["xi"])
    record["xi_star"] = best["xi"]
    record["verdict"] = "GATE REACHED"
    record["binding"] = dict(
        xi_star=best["xi"],
        binding_case=best["binding_case"],
        binding_cell_index=best["binding_cell_index"],
        min_barycentric_coordinate=best["min_barycentric_coordinate"],
        max_frobenius_norm=best["max_frobenius_norm"],
        max_frobenius_case=best["max_frobenius_case"],
        max_frobenius_cell_index=best["max_frobenius_cell_index"],
        first_infeasible_xi=next((g["xi"] for g in grid_results
                                  if g["xi"] > best["xi"]), None))
    # The xi-scaled term sets the propagation cases are built from.
    # sec. 3.1, and it is explicit: "ONE scalar `xi` multiplying EVERY
    # coefficient of BOTH targets".  So R is scaled too -- xi is SELECTED on
    # the realisability of `b_lin + xi*b^Delta` (sec. 3.4) but APPLIED to the
    # pair, which is what "the PAIR" in this build's title means.  Scaling
    # b^Delta alone would silently register a different model from the one
    # sec. 3.1 writes down.
    scale = lambda ts: [[int(t[0]), int(t[1]), int(t[2]),
                         best["xi"] * float(t[3])] for t in ts]
    rterms = [list(t) for t in model["R"]["terms"]]
    record["bDelta_terms_scaled"] = scale(bterms)
    record["R_terms_scaled"] = scale(rterms)
    record["bDelta_terms_unscaled"] = [list(t) for t in bterms]
    record["R_terms_unscaled"] = rterms
    record["scaling_note"] = (
        "sec. 3.1: one scalar xi multiplies EVERY coefficient of BOTH targets. "
        "xi is selected on the realisability of b_lin + xi*b^Delta (sec. 3.4) "
        "and applied to the pair (R and b^Delta) when the cases are built.")
    return record


def zero_shot_guard(cases):
    """G0f, re-asserted at THIS call site so `-O` cannot erase it.

    `r4_lib.assert_no_test_case` is a bare `assert` in a FROZEN file this item
    may not edit (sec. 3.1).  Under `python3 -O` that assert is DELETED and the
    guard silently passes a test case.  Measured, not assumed.  The refusal
    below is an explicit SystemExit(2) and therefore survives `-O`.
    """
    bad = sorted(set(cases) & (R.TEST_CASES | R.VAL_CASES))
    require(not bad, "ZERO-SHOT",
            f"ZERO-SHOT VIOLATION: test/validation case in fit set: {bad}")
    return dict(n_cases=len(cases), test_or_validation_cases_found=0,
                frozen_guard="r4_lib.assert_no_test_case",
                frozen_guard_is_bare_assert=True,
                frozen_guard_erased_under_dash_O=True,
                reasserted_here_as_explicit_refusal=True)


# ---------------------------------------------------- THE BIRTH DEMONSTRATION
def _split_field(text):
    i = text.index("internalField")
    j = text.index("boundaryField")
    return text[:i], text[i:j], text[j:]


def _rewrite_body(body, delta):
    """The SAME rewrite `r4_lib.planted_zero_reader_check` performs, with the
    added amount as a parameter.  delta = PLANT is the positive half; delta =
    0.0 is the negative half -- an unperturbed copy of the same real file
    travelling the same path, which must move NOTHING."""
    if "(" in body.split("\n", 3)[3]:
        return re.sub(r"\(\s*(-?[\d.eE+-]+)",
                      lambda m: "(" + f"{float(m.group(1)) + delta:.17g}", body)
    return re.sub(r"^\s*(-?\d[\d.eE+-]*)\s*$",
                  lambda m: f"{float(m.group(1)) + delta:.17g}", body,
                  flags=re.M)


def birth_g0a(field_path, scratch_dir):
    """G0a, TWO-SIDED, on a real `bijDelta` written by the frozen extraction.

    Positive half: `r4_lib.planted_zero_reader_check`, re-used UNMODIFIED, with
    THIS module's READER.  Its bar is magnitude-aware -- max(1e-12, 8*eps*
    max|field|) AND the median recovery matching the plant to 1e-9 relative --
    for the reason R4 recorded as departure D-9.  It raises SystemExit(2) if
    the reader cannot see the plant, so R1 is discharged by the same call.

    Negative half: the same rewrite with delta = 0.0, read by the same reader.
    Nothing may move.  Without it a reader that flags everything passes the
    positive half.
    """
    require(os.path.exists(field_path), "G0A-ARTEFACT",
            f"PENDING: {field_path} - sec. 3.2's carve-out applies and this "
            f"control is NOT BORN")
    guard_write_root(scratch_dir)
    os.makedirs(scratch_dir, exist_ok=True)

    pos_scratch = os.path.join(scratch_dir, "bijDelta_planted")
    pos = R.planted_zero_reader_check(field_path, READER, pos_scratch)

    text = open(field_path).read()
    head, body, tail = _split_field(text)
    neg_scratch = os.path.join(scratch_dir, "bijDelta_unperturbed")
    with open(neg_scratch, "w") as fh:
        fh.write(head + _rewrite_body(body, 0.0) + tail)
    a = np.asarray(READER(field_path), dtype=float).reshape(-1)
    b = np.asarray(READER(neg_scratch), dtype=float).reshape(-1)
    require(a.size == b.size, "G0A-NEG",
            f"unperturbed copy changed the cell count: {a.size} -> {b.size}")
    d = b - a
    n_moved = int((np.abs(d) > 0).sum())
    max_moved = float(np.abs(d).max()) if d.size else 0.0

    copy_scratch = os.path.join(scratch_dir, "bijDelta_bytecopy")
    shutil.copy(field_path, copy_scratch)
    c = np.asarray(READER(copy_scratch), dtype=float).reshape(-1)
    n_moved_copy = int((np.abs(c - a) > 0).sum())

    require(n_moved == 0, "G0A-NEG",
            f"the reader flagged {n_moved} values on an UNPERTURBED copy of "
            f"{field_path} (max |delta| = {max_moved:.6g}); a reader that "
            f"moves on nothing cannot certify that it moved on something")
    return dict(control="G0a", instrument="select_control.py",
                reader="of_read.read_field", bar="r4_lib.planted_zero_reader_check",
                real_artefact=os.path.abspath(field_path),
                real_artefact_producer="the frozen extraction "
                                       "(kCorrectiveFrozenFoam)",
                real_artefact_bytes=os.path.getsize(field_path),
                positive=pos,
                negative=dict(scratch=os.path.abspath(neg_scratch),
                              path="same rewrite, delta = 0.0",
                              n_values_moved=n_moved,
                              max_abs_delta=max_moved, flagged=False),
                negative_bytecopy=dict(scratch=os.path.abspath(copy_scratch),
                                       n_values_moved=n_moved_copy,
                                       flagged=bool(n_moved_copy)),
                both_halves=True, verdict="PASS")


# A cell whose barycentric coordinates are (0, 1.001, -1e-3): traceless,
# symmetric, and non-realisable by EXACTLY the registered amount.  c3 = 3*l3+1
# so l3 = (-1e-3 - 1)/3; l1 = l2 = -l3/2 makes the trace zero and c1 = 0.
_L3 = (-1e-3 - 1.0) / 3.0
NONREALISABLE_CELL = np.diag([-_L3 / 2.0, -_L3 / 2.0, _L3])


def birth_g0e(b_total, scratch_dir, tag="select_control"):
    """G0e, TWO-SIDED, on the total-b array this module itself produced.

    The array is written to disk and re-read, so the plant travels a real
    round trip rather than living in memory.  The violating count must rise by
    EXACTLY ONE -- "at least one" is also satisfied by a routine that flags
    everything, which is the failure this control exists to exclude -- and must
    NOT rise on the unperturbed copy.
    """
    guard_write_root(scratch_dir)
    os.makedirs(scratch_dir, exist_ok=True)
    base_path = os.path.join(scratch_dir, f"{tag}_b_total.npy")
    np.save(base_path, b_total)

    base = np.load(base_path)
    v0, _ = realisability_violation(base, tol=TOL)
    n0 = int(v0.sum())

    clean = np.where(~v0)[0]
    require(clean.size > 0, "G0E-NOCELL",
            "every cell of the total-b array is already violating; there is no "
            "realisable cell to plant into")
    idx = int(clean[0])

    planted = base.copy()
    planted[idx] = NONREALISABLE_CELL
    pos_path = os.path.join(scratch_dir, f"{tag}_b_total_planted.npy")
    np.save(pos_path, planted)
    v1, mn1 = realisability_violation(np.load(pos_path), tol=TOL)
    n1 = int(v1.sum())

    neg_path = os.path.join(scratch_dir, f"{tag}_b_total_unperturbed.npy")
    np.save(neg_path, base.copy())
    v2, _ = realisability_violation(np.load(neg_path), tol=TOL)
    n2 = int(v2.sum())

    coords, _ = barycentric(NONREALISABLE_CELL[None, :, :])
    planted_min = float(coords.min())

    require(n1 - n0 == 1, "G0E-POS",
            f"the violating count rose by {n1 - n0}, not by EXACTLY one "
            f"({n0} -> {n1}); a routine that flags everything also satisfies "
            f"'at least one', which is why the bar is exactly one")
    require(v1[idx], "G0E-POS",
            f"the violating count moved but cell {idx} - the cell actually "
            f"planted into - is not the one flagged")
    require(n2 == n0, "G0E-NEG",
            f"the unperturbed copy raised the violating count from {n0} to "
            f"{n2}; a reader that flags an unplanted array certifies nothing")
    return dict(control="G0e", instrument="select_control.py",
                reader="of_read.realisability_violation",
                array_path=os.path.abspath(base_path),
                array_shape=list(base.shape), tolerance=TOL,
                planted_cell_index=idx,
                planted_min_barycentric_coordinate=planted_min,
                n_violating_baseline=n0, n_violating_planted=n1,
                n_violating_unperturbed=n2,
                rose_by=n1 - n0, required_rise=1,
                both_halves=True, verdict="PASS")


def birth_g0f():
    """G0f, TWO-SIDED, through the REAL frozen guard `assert_no_test_case`.

    Positive half: `NASA_2DWMH` inside a real training list -- the guard must
    raise.  Negative half: the same list without it -- the guard must NOT raise.

    MEASURED AND DISCLOSED: under `python3 -O` the frozen guard is a deleted
    `assert` and raises on NEITHER list.  That is a defect in a frozen re-used
    instrument this item may not edit, and it is recorded here rather than
    worked around.  `zero_shot_guard()` above re-asserts the same condition as
    an explicit refusal at this item's own call site, which does survive `-O`.
    """
    clean = ["PHLL10595", "CBFS13700", "AR_1_Ret_180"]
    dirty = clean + ["NASA_2DWMH"]

    raised_on_dirty = False
    try:
        R.assert_no_test_case(dirty)
    except AssertionError:
        raised_on_dirty = True

    raised_on_clean = False
    try:
        R.assert_no_test_case(clean)
    except AssertionError:
        raised_on_clean = True

    optimized = bool(sys.flags.optimize)
    refused_here = False
    try:
        zero_shot_guard(dirty)
    except SystemExit:
        refused_here = True
    passed_here = True
    try:
        zero_shot_guard(clean)
    except SystemExit:
        passed_here = False

    if not optimized:
        require(raised_on_dirty, "G0F-POS",
                "assert_no_test_case did NOT raise on a list containing "
                "NASA_2DWMH")
    require(not raised_on_clean, "G0F-NEG",
            "assert_no_test_case raised on a clean training list; a guard that "
            "refuses everything certifies nothing")
    require(refused_here, "G0F-POS-OWN",
            "this item's own zero-shot refusal did not fire on NASA_2DWMH")
    require(passed_here, "G0F-NEG-OWN",
            "this item's own zero-shot refusal fired on a clean training list")
    return dict(control="G0f", instrument="select_control.py",
                guard="r4_lib.assert_no_test_case",
                planted_case="NASA_2DWMH",
                interpreter_optimized=optimized,
                frozen_guard_raised_on_planted=raised_on_dirty,
                frozen_guard_raised_on_clean=raised_on_clean,
                frozen_guard_blind_under_dash_O=bool(optimized
                                                     and not raised_on_dirty),
                own_refusal_fired_on_planted=refused_here,
                own_refusal_silent_on_clean=passed_here,
                both_halves=True, verdict="PASS")


def default_bijDelta():
    """One real `bijDelta`, chosen by path, from the frozen extraction."""
    frozen = os.path.join(R.WORK, "frozen")
    if not os.path.isdir(frozen):
        return None
    for case in sorted(os.listdir(frozen)):
        d = os.path.join(frozen, case)
        if not os.path.isdir(d):
            continue
        t = R.latest_time(d)
        p = os.path.join(d, t, "bijDelta")
        if os.path.exists(p):
            return p
    return None


# --------------------------------------------------------------- MODEL.md
def model_markdown(rec):
    L = []
    L.append("# R4b MODEL - the uniform control value `xi*`\n")
    if rec.get("provenance"):
        L.append(f"**{rec['provenance']}**\n")
    L.append("Computed by `select_control.py` under "
             "`PREREGISTRATION.md` section 3.4. `xi*` is the LARGEST value on "
             "the frozen 12-value grid at which `b_total = b_lin + xi*b^Delta` "
             "is realisable at `tol = 1e-6` on EVERY fitted cell of ALL 12 "
             "training cases, with `max_cell ||b_total||_F <= sqrt(2/3)`.\n")
    L.append(f"* selection criterion: **{rec['criterion']}** and nothing else\n"
             f"* realisability tolerance: `{rec['realisability_tolerance']}`\n"
             f"* Frobenius cap: `{rec['frobenius_cap']:.7f}` = sqrt(2/3)\n"
             f"* mask: {rec['mask_source']}\n"
             f"* cells: **{rec['n_cells_fitted']:,} of {rec['n_cells_total']:,}** "
             f"over {rec['n_cases']} training cases\n"
             f"* source b^Delta model: `{rec['source_model']['path']}`\n"
             f"  sha256 `{rec['source_model']['sha256']}`\n")
    L.append(f"\n## Verdict: `{rec['verdict']}`\n")
    if rec.get("xi_star") is None:
        L.append(f"\n`xi*` is **not** defined. {rec.get('blocked_reason','')}\n")
    else:
        b = rec["binding"]
        L.append(f"\n**`xi* = {rec['xi_star']}`**, binding on case "
                 f"`{b['binding_case']}` cell `{b['binding_cell_index']}` "
                 f"(min barycentric coordinate "
                 f"`{b['min_barycentric_coordinate']:.6e}`); "
                 f"`max ||b_total||_F = {b['max_frobenius_norm']:.6f}` on "
                 f"`{b['max_frobenius_case']}`. The first infeasible grid value "
                 f"above it is `{b['first_infeasible_xi']}`.\n")
        L.append("\nThe value is **reported, not graded** by the instrument "
                 "build: R4b's prediction P1 belongs to R4b's own registration "
                 "and is graded there.\n")
    L.append("\n## Feasibility at EVERY grid value (all twelve, sec. 3.4)\n")
    L.append("\n| `xi` | feasible | violating cells | min barycentric | "
             "binding case | `max ||b||_F` |\n")
    L.append("|---|---|---|---|---|---|\n")
    for g in rec["grid_results"]:
        L.append(f"| `{g['xi']}` | {'YES' if g['feasible'] else 'no'} | "
                 f"{g['n_violating_total']} | "
                 f"`{g['min_barycentric_coordinate']:.6e}` | "
                 f"`{g['binding_case']}` | "
                 f"`{g['max_frobenius_norm']:.6f}` |\n")
    if rec.get("bDelta_terms_scaled"):
        L.append("\n## The xi-scaled term sets the propagation cases are built "
                 "from\n\n```\n")
        L.append(f"R       (x {rec['xi_star']}): {rec['R_terms_scaled']}\n")
        L.append(f"bDelta  (x {rec['xi_star']}): {rec['bDelta_terms_scaled']}\n")
        L.append("```\n")
    L.append(f"\n`frozen_at`: `{rec.get('frozen_at')}`\n")
    return "".join(L)


# --------------------------------------------------------------- selftest
def _selftest():
    """rc 0 under `python3` AND `python3 -O`. Cheap by design: no dataset."""
    ok = []

    def check(name, cond, detail=""):
        ok.append((name, bool(cond), detail))

    # (1) this module contains ZERO `ast.Assert` nodes (L-332).
    tree = ast.parse(open(os.path.abspath(__file__)).read())
    n_assert = sum(isinstance(n, ast.Assert) for n in ast.walk(tree))
    check("zero_ast_assert_nodes", n_assert == 0, f"count={n_assert}")

    # (2) the frozen grid is the registered one, in order.
    check("grid_is_frozen_12",
          GRID == (0.01, 0.02, 0.03, 0.05, 0.07, 0.10, 0.15, 0.20, 0.30,
                   0.50, 0.70, 1.00) and len(GRID) == 12, str(GRID))
    check("frobenius_cap", abs(FROB_MAX - 0.8164965809277260) < 1e-15,
          repr(FROB_MAX))
    check("tolerance", TOL == 1e-6, repr(TOL))

    # (3) refuse() exits 2, NOT AssertionError, under both interpreters.
    try:
        refuse("SELFTEST", "expected")
        check("refuse_exits", False, "did not raise")
    except SystemExit as e:
        check("refuse_exits", e.code == 2, f"code={e.code}")

    # (4) the criterion refusal fires on anything but realisability.
    try:
        select(DATASET, R4_MODEL, cases=["PHLL10595"], criterion="b_rms")
        check("criterion_refusal", False, "did not refuse")
    except SystemExit as e:
        check("criterion_refusal", e.code == 2, f"code={e.code}")

    # (5) the solve-root guard refuses, and permits the instrument root.
    try:
        guard_write_root(os.path.join(SOLVE_ROOT, "x", "MODEL.json"))
        check("solve_root_guard", False, "did not refuse")
    except SystemExit as e:
        check("solve_root_guard", e.code == 2, f"code={e.code}")
    try:
        guard_write_root(os.path.join(INSTRUMENT_ROOT, "MODEL.json"))
        check("instrument_root_allowed", True)
    except SystemExit:
        check("instrument_root_allowed", False, "refused its own root")

    # (6) the planted non-realisable cell really is non-realisable, by the real
    #     reader, and by EXACTLY the registered amount.
    coords, _ = barycentric(NONREALISABLE_CELL[None, :, :])
    mn = float(coords.min())
    check("planted_cell_min_coord", abs(mn - (-1e-3)) < 1e-12, f"{mn:.12e}")
    check("planted_cell_traceless",
          abs(float(np.trace(NONREALISABLE_CELL))) < 1e-14)
    v, _ = realisability_violation(NONREALISABLE_CELL[None, :, :], tol=TOL)
    check("planted_cell_flagged", bool(v[0]))

    # (7) two-sided on a tiny in-memory array through the REAL reader: an
    #     isotropic (b = 0) cell is realisable and must NOT be flagged.
    v0, _ = realisability_violation(np.zeros((3, 3, 3)), tol=TOL)
    check("isotropic_not_flagged", int(v0.sum()) == 0, f"{int(v0.sum())}")

    # (8) the rewrite round-trips exactly at delta = 0.0 and MOVES at delta =
    #     PLANT, on the parenthesised branch every real vector/symmTensor field
    #     takes.  Both halves of the negative control's own machinery.
    body = ("internalField   nonuniform List<vector>\n2\n(\n"
            "(1.5 2.5 3.5)\n(-2.25e-03 0 1)\n)\n;\n")
    first = lambda s: float(re.search(r"\(\s*(-?[\d.eE+-]+)", s.split("(\n", 1)[1]).group(1))
    check("rewrite_delta0_roundtrip", first(_rewrite_body(body, 0.0)) == 1.5,
          repr(first(_rewrite_body(body, 0.0))))
    check("rewrite_plant_moves",
          abs(first(_rewrite_body(body, R.PLANT)) - (1.5 + R.PLANT)) < 1e-15,
          repr(first(_rewrite_body(body, R.PLANT))))

    # (9) feasibility_at is monotone in the obvious direction on a synthetic
    #     pair: a bigger xi cannot reduce the Frobenius norm here.
    bl = np.zeros((2, 3, 3))
    bm = np.tile(np.diag([0.4, -0.2, -0.2]), (2, 1, 1))
    f1 = feasibility_at(bl, bm, 0.01)
    f2 = feasibility_at(bl, bm, 1.00)
    check("frobenius_grows_with_xi",
          f2["max_frobenius_norm"] > f1["max_frobenius_norm"])
    check("small_xi_realisable", f1["realisable"])

    bad = [n for n, c, _ in ok if not c]
    for n, c, d in ok:
        print(f"  [{'ok ' if c else 'FAIL'}] {n} {d}")
    print(f"select_control.py --selftest: {len(ok) - len(bad)}/{len(ok)} "
          f"(optimize={sys.flags.optimize})")
    if bad:
        sys.stderr.write(f"SELFTEST FAILED: {bad}\n")
        return 1
    return 0


# ------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dataset", default=DATASET)
    ap.add_argument("--model", default=R4_MODEL,
                    help="R4's committed MODEL.json - the source of b^Delta")
    ap.add_argument("--out-dir", default=INSTRUMENT_ROOT,
                    help="where MODEL.json / MODEL.md are written")
    ap.add_argument("--cases", default="",
                    help="comma list; default = all 12 training cases")
    ap.add_argument("--criterion", default=CRITERION)
    ap.add_argument("--demonstration", action="store_true",
                    help="stamp the output DEMONSTRATION - NOT THE REGISTERED "
                         "MODEL (sec. 4.3)")
    ap.add_argument("--birth", action="store_true",
                    help="run the two-sided birth demonstration (B3)")
    ap.add_argument("--birth-out", default="",
                    help="where the birth record fragment is written")
    ap.add_argument("--bijdelta", default="",
                    help="the real bijDelta G0a plants into")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    if a.selftest:
        return _selftest()

    out_dir = guard_write_root(a.out_dir)
    os.makedirs(out_dir, exist_ok=True)
    scratch = os.path.join(out_dir, "birth", "select_control")
    cases = [c for c in a.cases.split(",") if c] or None

    birth = None
    if a.birth:
        field = a.bijdelta or default_bijDelta()
        require(field, "G0A-ARTEFACT",
                "PENDING: no real bijDelta found under "
                f"{os.path.join(R.WORK, 'frozen')} - sec. 3.2's carve-out "
                "applies and G0a is NOT BORN")
        birth = dict(instrument="select_control.py",
                     gate="B3",
                     birth_requirement="INSTRUMENT_BUILD_PREREGISTRATION.md "
                                       "section 5.0, two-sided",
                     at=utcnow(),
                     interpreter_optimize=int(sys.flags.optimize),
                     G0a=birth_g0a(field, scratch),
                     G0f=birth_g0f())

    rec = select(a.dataset, a.model, cases=cases, criterion=a.criterion)
    rec["frozen_at"] = utcnow()
    rec["written_by"] = os.path.abspath(__file__)
    rec["written_by_sha256"] = sha256_file(os.path.abspath(__file__))

    if a.demonstration:
        rec = dict(provenance=DEMO_PROVENANCE, **rec)   # provenance FIRST

    if a.birth:
        # G0e plants into the total-b array THIS run produced, at xi* if there
        # is one and at the smallest grid value if the run is BLOCKED.
        man = json.load(open(os.path.join(a.dataset, "dataset_manifest.json")))
        cand = list(man["candidates"])
        model = json.load(open(a.model))
        xi = rec.get("xi_star") or GRID[0]
        c0 = (cases or sorted(man["cases"]))[0]
        b_lin, b_mod, _, _ = load_case(a.dataset, c0, cand,
                                       list(model["bDelta"]["names"]),
                                       [list(t) for t in model["bDelta"]["terms"]])
        birth["G0e"] = birth_g0e(b_lin + xi * b_mod, scratch)
        birth["G0e"]["xi_used"] = xi
        birth["G0e"]["case"] = c0
        birth["grid_values_evaluated"] = rec["n_grid_values_evaluated"]
        birth["grid_values_required"] = len(GRID)
        birth["xi_star_reported_not_graded"] = rec.get("xi_star")
        birth["verdict"] = ("PASS"
                            if (rec["n_grid_values_evaluated"] == len(GRID)
                                and birth["G0a"]["verdict"] == "PASS"
                                and birth["G0e"]["verdict"] == "PASS")
                            else "GATE FAIL")
        rec["birth"] = birth
        if a.birth_out:
            write_json(a.birth_out, birth)

    write_json(os.path.join(out_dir, "MODEL.json"), rec)
    mdp = guard_write_root(os.path.join(out_dir, "MODEL.md"))
    with open(mdp, "w") as fh:
        fh.write(model_markdown(rec))

    if rec["verdict"] == "BLOCKED":
        blocked(rec["blocked_reason"])
    print(f"xi* = {rec['xi_star']}  (verdict {rec['verdict']}, "
          f"{rec['n_grid_values_evaluated']}/{len(GRID)} grid values evaluated, "
          f"{rec['n_cells_fitted']:,}/{rec['n_cells_total']:,} cells)")
    print(f"  -> {os.path.join(out_dir, 'MODEL.json')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
