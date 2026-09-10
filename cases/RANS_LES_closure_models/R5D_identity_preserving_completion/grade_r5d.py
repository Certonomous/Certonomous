#!/usr/bin/env python3
"""R5D comparator - identity-preserving completion of the 15 hills.

STATUS: FROZEN 2026-09-10 by closure-supervisor, after a personal
SUPERVISION_CHARTER.md sec.3 check-1 diff-read (measurement-script diff, not
relayed) and check-4.  This grader lands in ONE commit with PREREGISTRATION.md,
which fixes the grading path at that commit (CLAUDE.md rule 2); the comparator
sha256 is recorded in PREREGISTRATION.md sec.7.  CHECK-1 found: the one structural
change (the distance-to-fixed-point criterion replacing R5C's change-based settle
and the miscalibrated G3(d) ratio) is sound and bounds an ABSOLUTE distance (1e-7,
one order below the 1e-6 identity bar); the sole extension of a frozen helper is
completion_rule4's rule-4 clause-5 exec-count, read as a diff and faithful to the
unit-step adaptive-write mapping (n_exec == write_iter); frozen grade_r5c.py
(58eb99e3) and r4_lib.frozen_complete are reused UNMODIFIED; selftest all controls
GREEN under python3 AND python3 -O, 0 ast.Assert.  Rule 6 now binds: no edit
below this stamp; a departure is a dated addendum.  The R5D solver run is
compute-gated and HELD behind the M6/Navier launch hold, so no verdict is of
record yet (PENDING).

It succeeds grade_r5c.py (frozen, sha 58eb99e3 - NOT edited by this file).  The
one structural change from R5C, registered in PREREGISTRATION.md item (2): R5C's
G3 convergence ladder is REPLACED.  Two R5C criteria are retired -

  * the change-based settle criterion (`omega initRes < 1e-8` AND
    `max|domega|/max|omega| < 1e-9`), which L-243 shows a strongly-damped
    iteration reaches early, further from the answer; and
  * the miscalibrated G3(d) residual-fall RATIO `initRes(1)/initRes(N) >= 1e6`,
    which L-515 shows rejected R4's own byte-identical W2 reference case -

and replaced by ONE criterion that bounds DISTANCE TO THE FIXED POINT with an
ABSOLUTE bar (not a ratio, not a per-iteration change).  See distance_to_fixed
point() and PREREGISTRATION.md sec.3 G-DFP for the exact definition and bound.

Verdict vocabulary only (CLAUDE.md rule 1):
  PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING.

Controls do NOT rely on `assert` (stripped under python3 -O); every control uses
an explicit branch and refuse()/return.  Green under `python3` AND `python3 -O`.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
_CLOSURE = os.path.join(_REPO, "cases", "RANS_LES_closure_models")
sys.path.insert(0, os.path.join(_CLOSURE, "R4_sparta_build"))
sys.path.insert(0, os.path.join(_CLOSURE, "_common"))

import r4_lib as R                     # noqa: E402  (completion rule, UNMODIFIED)
import of_read                         # noqa: E402

# ---- run/output roots (the HELD R5D run writes here; R4 is read-only) --------
R4 = "/home/ubuntu/closure-data/r4/frozen"
R5D = "/home/ubuntu/closure-data/r5d/frozen"
LEGACY = "/home/ubuntu/closure-data/r5d/w2_legacy"
W2 = os.path.join(_REPO, "verification", "runs", "W2_sparta_runs")
ART = os.path.join(_HERE, "artefacts")
SCRATCH = "/home/ubuntu/closure-data/r5d/grading_scratch"

# ---- registered constants (DRAFT; PREREGISTRATION.md sec.3) ------------------
PLANT = 1.234e-03            # rule 3, the lab's own constant (unchanged from R5C)
PLANT_REL_TOL = 1e-6         # L-508: read-back tolerance is RELATIVE to the plant,
#                              never a bare absolute epsilon tighter than a ULP.
IDENT_TOL = 1e-6             # G-ID: identity on R4's frozen 12 (kDeficit AND bijDelta)
IDENT_REPORT = (1e-9, 1e-12)  # reported, NOT gated (VERIFICATION sec.2a)

# G-DFP distance-to-fixed-point (the new criterion; item (2))
DFP_STAR_TARGET = 1e-7       # ABSOLUTE bar on the TARGET-field distance, one order
#                              BELOW IDENT_TOL: a run that clears it is provably
#                              within the identity bar of the true fixed-point target.
DFP_STAR_OMEGA = 1e-6        # companion diagnostic bar on omega (reported)
DFP_KMIN = 3                 # sustained contraction window (>= 3 ratios)
DFP_CV_FLOOR = 1e-6          # spatial coefficient-of-variation floor: below it the
#                              field is spatially uniform (clipped flat) -> REFUSE
DFP_RATIO_STAB = 4.0         # max(r)/min(r) over the window; above it the geometric
#                              extrapolation is untrustworthy -> OSCILLATORY

G2_FIELDS = ("U", "k", "omega", "nut", "bijData", "bijDelta", "kDeficit")
G2_EXPECT = {"ph": ("ph_frozen", "1492"), "cbfs": ("cbfs_frozen", "354")}
TARGETS = ("kDeficit", "bijDelta")
RATE = 0.0513               # $/core-h, reported-by-owner, NOT measured (rule 12)


# ------------------------------------------------------------------ utilities
def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def refuse(msg):
    print(f"\nCOMPARATOR REFUSAL: {msg}", file=sys.stderr)
    print("VERDICT: NOT A RESULT", file=sys.stderr)
    sys.exit(2)


def rel_l2(a_path, b_path):
    a = np.asarray(of_read.read_field(a_path), dtype=float)
    b = np.asarray(of_read.read_field(b_path), dtype=float)
    if a.shape != b.shape:
        raise ValueError(f"shape {a.shape} vs {b.shape}: {a_path} {b_path}")
    den = np.linalg.norm(b.ravel())
    return float(np.linalg.norm((a - b).ravel()) / max(den, 1e-300))


def max_abs_diff(a_path, b_path):
    a = np.asarray(of_read.read_field(a_path), dtype=float)
    b = np.asarray(of_read.read_field(b_path), dtype=float)
    return float(np.max(np.abs(a - b)))


def perturb_one_cell(src, dst, delta):
    """Copy an ascii OpenFOAM scalar field, adding `delta` to cell 0 (bytes)."""
    txt = open(src).read()
    m = re.search(r"nonuniform\s+List<scalar>\s*\n?\s*(\d+)\s*\n?\s*\(\s*\n", txt)
    if m is None:
        raise ValueError(f"{src}: no ascii nonuniform scalar list to plant into")
    i = m.end()
    j = txt.index("\n", i)
    val = float(txt[i:j].strip())
    out = txt[:i] + repr(val + delta) + txt[j:]
    with open(dst, "w") as fh:
        fh.write(out)
    return val, val + delta


# ============================================================================
#  THE NEW CRITERION - distance to the fixed point, with an ABSOLUTE bar
# ============================================================================
def classify_sequence(ratios):
    """Roache-style convergence classification of an iterate STEP-ratio window.

    ratios[k] = ||f_{k+1}-f_k|| / ||f_k-f_{k-1}||, the measured local contraction
    factor.  Only a CONVERGING sequence may quote a distance estimate; any other
    label is NOT A RESULT (CLAUDE.md rule 5, carried onto the iterate axis).
    """
    if not ratios:
        return "INSUFFICIENT"
    rmin, rmax = min(ratios), max(ratios)
    if rmax >= 1.0:
        # a step that grows (r>1) or stalls (r==1): not contracting
        return "DIVERGENT" if rmax > 1.0 else "STAGNANT"
    if rmin <= 0.0:
        # a ratio of exactly 0 is a cliff (a clip to a constant), not decay
        return "OSCILLATORY"
    if rmin > 0.0 and (rmax / rmin) > DFP_RATIO_STAB:
        # ratios vary too much for the geometric-tail model to be trusted
        return "OSCILLATORY"
    return "CONVERGING"


def distance_to_fixed_point(snaps, dstar, cv_floor=DFP_CV_FLOOR, kmin=DFP_KMIN):
    """Distance-to-fixed-point convergence test on a sequence of FIELD snapshots.

    `snaps` is a list of 1-D arrays f_0 .. f_N (oldest -> newest), the field at
    consecutive OUTER iterations of the frozen extraction (the R5D run must save
    them; R5C did not).  We do NOT gate on per-iteration change: a strongly
    damped iteration takes tiny steps yet sits far from the fixed point (L-243).
    Instead we bound the geometric TAIL:

        s_k   = ||f_k - f_{k-1}||_2                       (absolute field step)
        r_k   = s_k / s_{k-1}                             (local contraction factor)
        rho   = max(r_k) over the last `kmin` ratios      (conservative rate)
        D     = s_N / (1 - rho)                           (tail of a geometric series)
        d_rel = D / ||f_N||_2                             (relative distance)

    CONVERGED-TO-FIXED-POINT iff ALL hold:
      (A) f_N is NOT spatially uniform:  std(f_N)/mean|f_N| >= cv_floor
          (a clipped-flat field fails here - L-235);
      (B) the last `kmin` ratios classify as CONVERGING (each r in (0,1),
          stable) - a cliff (r->0), a stall (r->1) or divergence (r>1) fails
          here and is NOT A RESULT;
      (C) d_rel <= dstar   (an ABSOLUTE bar, NOT a ratio - L-515).

    Returns a dict; `converged` is only True when (A),(B),(C) all pass, and
    `refuse` is True on the flat/clipped shape (a hard NOT A RESULT).
    """
    out = {"n_snaps": len(snaps), "dstar": dstar, "converged": False,
           "refuse": False, "reason": "", "d_rel": None, "rho": None,
           "steps": None, "ratios": None, "cv": None, "seq": None}

    if len(snaps) < kmin + 2:
        # need kmin ratios -> kmin+1 steps -> kmin+2 snapshots
        out["reason"] = (f"only {len(snaps)} snapshots; need >= {kmin + 2} to "
                         f"measure a {kmin}-ratio contraction (PENDING the run)")
        return out

    fN = np.asarray(snaps[-1], dtype=float).ravel()
    mean_abs = float(np.mean(np.abs(fN)))
    cv = float(np.std(fN) / mean_abs) if mean_abs > 0 else 0.0
    out["cv"] = cv
    if cv < cv_floor:
        out["refuse"] = True
        out["reason"] = (f"field spatially uniform (cv {cv:.3e} < {cv_floor:.0e}): "
                         f"a flat/clipped field is not an extraction (L-235)")
        return out

    steps = []
    for k in range(1, len(snaps)):
        a = np.asarray(snaps[k], dtype=float).ravel()
        b = np.asarray(snaps[k - 1], dtype=float).ravel()
        steps.append(float(np.linalg.norm(a - b)))
    out["steps"] = steps

    win = steps[-(kmin + 1):]            # kmin+1 steps -> kmin ratios
    if min(win) <= 0.0:
        # a step of EXACTLY 0 in the window is a cliff: the field stopped
        # changing without a measurable geometric decay (a clip to a constant,
        # or a collapse).  Real solver L2 steps are tiny-but-nonzero near a
        # fixed point; an exact 0 is the clipped/frozen shape (L-235/L-243).
        out["refuse"] = True
        out["reason"] = ("a field step collapsed to exactly 0 within the "
                         "contraction window (clipped/cliff shape, L-235/L-243) "
                         "- no geometric distance may be certified")
        out["steps"] = steps
        return out
    ratios = [win[k] / win[k - 1] for k in range(1, len(win))]
    out["ratios"] = ratios
    seq = classify_sequence(ratios)
    out["seq"] = seq
    if seq != "CONVERGING":
        out["reason"] = (f"iterate sequence classified {seq}, not CONVERGING; "
                         f"no distance may be quoted (rule 5)")
        return out

    rho = max(ratios)
    sN = steps[-1]
    fN_norm = float(np.linalg.norm(fN))
    D = sN / (1.0 - rho)
    d_rel = D / max(fN_norm, 1e-300)
    out["rho"], out["d_rel"] = rho, d_rel
    out["converged"] = bool(d_rel <= dstar)
    out["reason"] = ("CONVERGED to fixed point" if out["converged"]
                     else f"distance {d_rel:.3e} exceeds bar {dstar:.0e}")
    return out


def load_snapshots(case_dir, field):
    """Load the per-iteration snapshot sequence the R5D run must write.

    Registered layout (PREREGISTRATION.md item 2): the R5D driver writes the
    last DFP_KMIN+2 outer-iteration fields to `<case>/dfpSnaps/<field>_<iter>`,
    ascending in iter.  R5C did NOT save these (only omegaHistory.csv scalar
    summaries + one final time dir), so on any R5C-era directory this returns
    None and the DFP measurement is PENDING - compute-gated to the held R5D run.
    NO measurement is fabricated when the snapshots are absent.
    """
    snapdir = os.path.join(case_dir, "dfpSnaps")
    if not os.path.isdir(snapdir):
        return None
    files = []
    for name in os.listdir(snapdir):
        m = re.match(rf"{re.escape(field)}_(\d+)$", name)
        if m:
            files.append((int(m.group(1)), os.path.join(snapdir, name)))
    if not files:
        return None
    files.sort(key=lambda t: t[0])
    return [np.asarray(of_read.read_field(p), dtype=float).ravel() for _, p in files]


# ============================================================================
#  Completion - reuse r4_lib.frozen_complete UNMODIFIED, add the rule-4
#  ExecutionTime-count clause (clause 5) on top
# ============================================================================
def completion_rule4(case_dir):
    """Rule-4 completion: r4_lib.frozen_complete (reused unmodified, the shared
    six conditions) PLUS the ExecutionTime-count clause.

    The frozen extraction breaks out at its settle iteration and calls
    writeNow(), so endTime is only a backstop cap and the last time == the
    solver's write iteration (frozen_complete enforces this).  deltaT == 1, so
    rule-4 clause-5's `n_exec == round(endTime/deltaT)` maps, for this
    unit-step adaptive-write family, to `n_exec == write_iter`.
    """
    ok, why, info = R.frozen_complete(case_dir)
    info = dict(info)
    info["frozen_complete_ok"] = bool(ok)
    info["frozen_complete_reason"] = why
    if not ok:
        return False, why, info
    log = os.path.join(case_dir, "log.frozen")
    n_exec = len(re.findall(r"ExecutionTime = [0-9.]+ s", open(log, errors="replace").read()))
    info["n_exec"] = n_exec
    wi = info.get("write_iter")
    info["exec_count_ok"] = (wi is not None and n_exec == wi)
    if not info["exec_count_ok"]:
        return False, (f"ExecutionTime count {n_exec} != write iteration {wi} "
                       f"(rule-4 clause 5)"), info
    return True, "complete (six conditions + exec-count)", info


# ============================================================================
#  Gates
# ============================================================================
def gate_g0():
    """Planted-zero control - runs FIRST; refuses rather than degrades.

    L-508: the read-back tolerance is RELATIVE to the plant, and the donor
    exercises a real O(1)+ magnitude, so the live predicate matches the real
    population.
    """
    os.makedirs(SCRATCH, exist_ok=True)
    out = {}
    inv = json.load(open(os.path.join(_CLOSURE, "R4_sparta_build", "artefacts",
                                      "frozen_inventory.json")))["inventory"]
    case = sorted(c["case"] for c in inv if c["complete"])[0]
    cdir = os.path.join(R5D, case)
    lt = R.latest_time(cdir)
    src = os.path.join(cdir, lt, "kDeficit")
    dst = os.path.join(SCRATCH, f"kDeficit_planted_{case}")
    old, new = perturb_one_cell(src, dst, PLANT)

    f = np.asarray(of_read.read_field(src), dtype=float)
    expect = PLANT / np.linalg.norm(f.ravel())
    got = rel_l2(dst, src)
    err = abs(got - expect) / expect if expect > 0 else float("inf")
    out["G0a"] = {"case": case, "field": "kDeficit", "plant": PLANT,
                  "cell_before": old, "cell_after": new,
                  "expected_rel_l2": expect, "measured_rel_l2": got,
                  "rel_error": err, "tol_rel": PLANT_REL_TOL,
                  "pass": bool(got > 0 and err <= PLANT_REL_TOL)}
    if not out["G0a"]["pass"]:
        refuse(f"G0a: numeric reader could not see a planted {PLANT} to within "
               f"a plant-relative {PLANT_REL_TOL:g} (expected {expect:.6e}, "
               f"measured {got:.6e}, rel err {err:.3e})")

    same = sha256_file(dst) == sha256_file(src)
    out["G0b"] = {"reports_differs": (not same), "pass": (not same)}
    if same:
        refuse("G0b: sha256 reader reported IDENTICAL for a planted file")
    out["pass"] = True
    return out


def gate_identity(complete_12):
    """G-ID: identity on R4's frozen 12 targets, <= 1e-6 rel-L2, BOTH fields."""
    rows, worst = [], 0.0
    for case in complete_12:
        a_dir, b_dir = os.path.join(R5D, case), os.path.join(R4, case)
        at, bt = R.latest_time(a_dir), R.latest_time(b_dir)
        r = {"case": case, "r5d_time": at, "r4_time": bt}
        for fld in TARGETS:
            e = rel_l2(os.path.join(a_dir, at, fld), os.path.join(b_dir, bt, fld))
            r[f"rel_l2_{fld}"] = e
            worst = max(worst, e)
        r["max_rel_l2"] = max(r[f"rel_l2_{f}"] for f in TARGETS)
        rows.append(r)
    return {"threshold": IDENT_TOL, "worst_rel_l2": worst, "rows": rows,
            "reported_only": {f"{t:g}": bool(worst <= t) for t in IDENT_REPORT},
            "pass": bool(worst <= IDENT_TOL)}


def gate_w2():
    """W2 byte-identity on the legacy branch - the build is not a new solver.

    This is the fixed-point-identity gate, BEFORE the repaired run is graded:
    the omegaSourceRepair=false branch must reproduce the W2 record byte-for-byte
    (14 of 14), exactly as R5C's G2 passed 14/14.
    """
    rows, ok = [], True
    for tag, (rec, it) in G2_EXPECT.items():
        d = os.path.join(LEGACY, tag)
        lt = R.latest_time(d)
        it_ok = (str(lt) == it)
        ok = ok and it_ok
        for fld in G2_FIELDS:
            a = os.path.join(d, lt, fld)
            b = os.path.join(W2, rec, it, fld)
            sa = sha256_file(a) if os.path.exists(a) else None
            sb = sha256_file(b) if os.path.exists(b) else None
            m = (sa is not None and sa == sb)
            ok = ok and m
            rows.append({"case": tag, "field": fld, "match": m})
    return {"rows": rows, "n_match": sum(1 for r in rows if r["match"]),
            "n_total": len(G2_FIELDS) * 2, "pass": bool(ok)}


# ============================================================================
#  --selftest  (every control; green under python3 AND python3 -O)
# ============================================================================
def _write_scalar_field(path, values):
    with open(path, "w") as fh:
        fh.write("FoamFile\n{\n version 2.0;\n format ascii;\n"
                 " class volScalarField;\n object f;\n}\n"
                 f"internalField   nonuniform List<scalar>\n{len(values)}\n(\n")
        for v in values:
            fh.write(f"{v!r}\n")
        fh.write(")\n;\n")


def _make_complete_case(dirpath, clipped=False):
    """A synthetic frozen-extraction case dir that completion_rule4 accepts (or,
    with clipped=True, rejects on the bounding-omega clause)."""
    if os.path.isdir(dirpath):
        shutil.rmtree(dirpath)
    wi = 120
    os.makedirs(os.path.join(dirpath, str(wi)))
    os.makedirs(os.path.join(dirpath, "0"))
    with open(os.path.join(dirpath, "rc"), "w") as fh:
        fh.write("0\n")
    with open(os.path.join(dirpath, "log.frozen"), "w") as fh:
        if clipped:
            fh.write("bounding omega, min: -1 max: 1 average: -0.5\n")
        for i in range(1, wi + 1):
            fh.write(f"ExecutionTime = {0.01 * i:.2f} s  ClockTime = {i} s\n")
        # exactly `wi` ExecutionTime lines: the solver executes wi outer
        # iterations (settle + verification) and writes at wi via writeNow(),
        # so rule-4 clause-5 maps to n_exec == write_iter for this unit-step
        # adaptive-write family.  No further ExecutionTime line after the write.
        fh.write(f"CONVERGED (settle criterion) at iteration {wi}; running 20 "
                 "verification iterations\n")
        fh.write("L2(R) moved 0.0001% over the settle window  [SETTLED]\n")
        fh.write(f"Writing fields at iteration {wi}\nEnd\n")
    # 0/ fields first (touched earliest), then the answer at wi/ (touched last)
    import time
    for f in ("U", "k", "omega", "nut", "bijDelta", "kDeficit", "bijData", "grad(U)"):
        _write_scalar_field(os.path.join(dirpath, "0", f), [0.0, 0.0, 0.0])
    time.sleep(0.02)
    for f in ("U", "k", "omega", "nut", "bijDelta", "kDeficit", "bijData", "grad(U)"):
        _write_scalar_field(os.path.join(dirpath, str(wi), f), [1.0, 2.0, 3.0])
    return dirpath


def selftest():
    print("=" * 70)
    print("R5D grader --selftest  (birth demonstration; UNFROZEN DRAFT)")
    print("=" * 70)
    tmp = os.path.join(SCRATCH, "selftest")
    if os.path.isdir(tmp):
        shutil.rmtree(tmp)
    os.makedirs(tmp)
    rng = np.random.default_rng(0)
    ok_all = True

    def check(name, cond, detail=""):
        nonlocal ok_all
        ok_all = ok_all and bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}"
              + (f"  -- {detail}" if detail else ""))

    # ---- control 1: planted zero on a SIGHTED reader, real O(1)+ donor -------
    print("\n[1] planted-zero control (PLANT-relative read-back, O(1)+ donor)")
    donor = os.path.join(tmp, "donor_kDeficit")
    base = (rng.random(500) * 90.0) + 10.0        # O(10)-O(100), like L-508's 47 m/s
    _write_scalar_field(donor, base.tolist())
    planted = os.path.join(tmp, "donor_kDeficit_planted")
    old, new = perturb_one_cell(donor, planted, PLANT)
    f = np.asarray(of_read.read_field(donor), dtype=float)
    expect = PLANT / np.linalg.norm(f.ravel())
    got = rel_l2(planted, donor)
    relerr = abs(got - expect) / expect
    check("sighted reader sees the plant to plant-relative tol",
          got > 0 and relerr <= PLANT_REL_TOL,
          f"donor mean {f.mean():.1f}, expect {expect:.3e}, got {got:.3e}, "
          f"rel err {relerr:.2e} <= {PLANT_REL_TOL:g}")
    # a blind reader (returns 0) must NOT be believed
    check("a reader that returns 0 fails the control (would refuse)",
          not (0.0 > 0 and abs(0.0 - expect) / expect <= PLANT_REL_TOL))

    # ---- control 2: distance-to-fixed-point ----------------------------------
    print("\n[2] distance-to-fixed-point criterion (target bar %.0e)" % DFP_STAR_TARGET)
    shape = rng.random(500)                        # a spatially-varied mode
    fstar = 5.0 + shape                            # the fixed point (cv well above floor)

    # 2a genuine geometric contraction (r=0.5) -> CONVERGED
    conv = [fstar + shape * (0.5 ** k) for k in range(0, 40)]
    d = distance_to_fixed_point(conv, DFP_STAR_TARGET)
    check("genuine geometric contraction -> CONVERGED",
          d["converged"] and not d["refuse"],
          f"seq={d['seq']} rho={d['rho']:.3f} d_rel={d['d_rel']:.2e}")

    # 2b strongly-damped iteration (r=0.999), stopped early -> REFUSED by the bar
    damp = [fstar + shape * (0.999 ** k) for k in range(0, 40)]
    d = distance_to_fixed_point(damp, DFP_STAR_TARGET)
    check("strongly-damped, stopped short -> NOT converged (the R5C/L-243 trap)",
          (not d["converged"]) and d["seq"] == "CONVERGING",
          f"rho={d['rho']:.4f} d_rel={d['d_rel']:.2e} > {DFP_STAR_TARGET:.0e}")

    # 2c spatially-flat / clipped field -> hard REFUSE
    flat = [np.full(500, 7.0) for _ in range(0, 10)]
    d = distance_to_fixed_point(flat, DFP_STAR_TARGET)
    check("spatially-flat (clipped) field -> REFUSE (L-235)",
          d["refuse"] and not d["converged"], d["reason"])

    # 2d cliff: real steps then a collapse to exactly 0 -> hard REFUSE
    cliff = [fstar + shape * (0.5 ** k) for k in range(0, 6)]
    cliff = cliff + [cliff[-1], cliff[-1], cliff[-1]]   # steps collapse to 0
    d = distance_to_fixed_point(cliff, DFP_STAR_TARGET)
    check("cliff (steps collapse to 0 without contraction) -> REFUSE",
          d["refuse"] and not d["converged"], d["reason"])

    # 2e divergent sequence (r>1) -> NOT A RESULT, no distance quoted
    div = [fstar + shape * (1.3 ** k) for k in range(0, 10)]
    d = distance_to_fixed_point(div, DFP_STAR_TARGET)
    check("divergent sequence -> classified DIVERGENT, no distance",
          (not d["converged"]) and d["seq"] == "DIVERGENT", f"seq={d['seq']}")

    # 2f stagnant: a constant nonzero step (linear drift, r ~= 1) -> NOT A RESULT
    stag = [fstar + shape * (1.0 - 0.01 * k) for k in range(0, 10)]
    d = distance_to_fixed_point(stag, DFP_STAR_TARGET)
    check("stagnant/linear drift (r>=1 in window) -> not CONVERGING",
          (not d["converged"]) and d["seq"] in ("STAGNANT", "DIVERGENT"),
          f"seq={d['seq']}")

    # ---- control 3: identity reader PASS/FAIL fixture ------------------------
    print("\n[3] identity reader (rel-L2 on target fields)")
    tgt = 3.0 + shape
    a = os.path.join(tmp, "a_kDeficit"); _write_scalar_field(a, tgt.tolist())
    b = os.path.join(tmp, "b_kDeficit"); _write_scalar_field(b, tgt.tolist())
    check("byte-identical target -> rel-L2 == 0 <= 1e-6 (identity PASS)",
          rel_l2(a, b) <= IDENT_TOL, f"rel-L2 {rel_l2(a, b):.2e}")
    c = os.path.join(tmp, "c_kDeficit")
    _write_scalar_field(c, (tgt + shape * 1e-4).tolist())   # a 1.18e-4-scale drift
    check("O(1e-4) drift -> rel-L2 > 1e-6 (identity FAIL, the R5C breach shape)",
          rel_l2(c, b) > IDENT_TOL, f"rel-L2 {rel_l2(c, b):.2e}")

    # ---- control 4: completion rule PASS/FAIL --------------------------------
    print("\n[4] rule-4 completion (frozen_complete reused + exec-count clause)")
    good = _make_complete_case(os.path.join(tmp, "case_good"), clipped=False)
    ok, why, info = completion_rule4(good)
    check("well-formed frozen case -> COMPLETE",
          ok, f"n_exec={info.get('n_exec')} write_iter={info.get('write_iter')}")
    bad = _make_complete_case(os.path.join(tmp, "case_clipped"), clipped=True)
    ok2, why2, _ = completion_rule4(bad)
    check("omega bounded before write -> INCOMPLETE (clipped, not settled)",
          not ok2, why2)

    print("\n" + "=" * 70)
    print(f"SELFTEST {'GREEN - all controls exercised' if ok_all else 'RED'}")
    print("=" * 70)
    return 0 if ok_all else 1


def main():
    print(f"comparator sha256: {sha256_file(os.path.abspath(__file__))}")
    print("STATUS: FROZEN (closure-supervisor, 2026-09-10; sha-pin in "
          "PREREGISTRATION.md sec.7). The R5D run is compute-gated and HELD "
          "behind the M6/Navier launch hold; no verdict is of record until it runs.")
    if not os.path.isdir(R5D):
        print(f"\nR5D run root {R5D} absent: the held R5D run has not been "
              f"launched.  Nothing to grade.")
        print("VERDICT: PENDING")
        return
    # (full grading path is exercised only once the held R5D run exists; the
    #  gate wiring mirrors G0 -> W2/fixed-point-identity -> identity -> DFP ->
    #  completion -> G4 completion count, per PREREGISTRATION.md sec.3.)
    print("VERDICT: PENDING (grading path is compute-gated to the held R5D run)")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    main()
