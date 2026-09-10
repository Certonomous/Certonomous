#!/usr/bin/env python3
"""analyse_k2d.py -- K2d comparator.  F14 rack-row module, three-level ladder.

    python3 analyse_k2d.py                 # grade the rung
    python3 analyse_k2d.py --selftest      # mutation matrix

REGISTRATION
------------
`docs/campaigns/F14-cooling-ladder/K2d_PREREGISTRATION.md`.  Every gate, band,
threshold and label below is READ FROM that document's registered values; this
file implements them and invents none.

EXIT MAP -- registration section 6.4, T3's convention
    0 EXIT_OK       graded (whatever the verdicts say)
    1 EXIT_FAIL     a graded row is GATE FAIL
    2 EXIT_REFUSE   this comparator will not grade

THE EXIT CODE DOES NOT CARRY THE VERDICT.  T16c returned rc = 0 with every row
`NOT A RESULT`.  Read the verdicts from stdout and from gate_k2d.json.

WHAT IS CALLED RATHER THAN REIMPLEMENTED, AND WHY
-------------------------------------------------
Three things in this rung already have exactly one correct implementation in
this repository, and a second copy of any of them is a place for drift to live:

  * `mark_done_k2d.py`          -- standing rule 4 and clause 7
  * `scripts/roache_triple.py`  -- ratios from CELL COUNTS, GCI at Fs = 1.25,
                                   triple states, the planted-zero constant
  * `scripts/check_convergence.py::classify_monitor` -- S13, carrying the
                                   `range_spanned_over_run` normaliser (D393)
                                   and the null-variation refusal

This comparator CALLS all three.  In particular the S13 normaliser is NOT
re-derived here: registration section 3.3a.1 records that a mean-normalised
threshold in this rung would have reintroduced the defect D393 repaired.

THE ORDER OF EVALUATION IS PART OF THE REGISTRATION (section 4.2), one-way
------------------------------------------------------------------------
  1 admission   G-MESHSIM, G-CHECKMESH (provenance + verdict), G-MINCELL,
                G-3D, the planted-zero control, and rule 4 via mark_done
  2 G-CYCLE     on BOTH monitored quantities, per level
  3 triple      classification per row
  4 band        only a CONVERGING triple is graded

The gate may turn a PASS or GATE FAIL *into* NOT A RESULT and NEVER the
reverse.  No branch below promotes a row.
"""

import glob
import json
import math
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def _find_repo(start):
    """Walk up to the repo root by LOOKING FOR IT, not by counting dirnames.

    A hard-coded chain of os.path.dirname() calls is a silent breakage the day
    the tree is reorganised -- and it broke on this file's first run, three
    levels where four were needed.  Search for the marker instead, and REFUSE
    rather than importing whatever happens to be on sys.path.
    """
    d = start
    while True:
        if (os.path.isdir(os.path.join(d, "scripts"))
                and os.path.isfile(os.path.join(d, "CLAUDE.md"))):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            raise SystemExit("REFUSE (exit 2): cannot locate the repository root "
                             "above %s -- refusing to import a shared instrument "
                             "from an unverified path" % start)
        d = parent


REPO = _find_repo(HERE)
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, HERE)

import roache_triple as RT                                    # noqa: E402
import mark_done_k2d as MD                                    # noqa: E402

EXIT_OK, EXIT_FAIL, EXIT_REFUSE = 0, 1, 2

LEVELS = ("K2d_L1", "K2d_L2", "K2d_L3")
DIM = 3                                       # registration 1.1: 3D, r = 1.5
TARGETS = {"K2d_L1": 59259, "K2d_L2": 200000, "K2d_L3": 675000}

# --- registered gates -------------------------------------------------------
MESHSIM_LO, MESHSIM_HI = 3.2063, 3.5438       # 3.375 +- 5 %   (section 1.2)
ORDER_LO, ORDER_HI = 0.5, 3.5                 # widened band   (section 4.3)
SUBFIRST = 1.0                                # A-SUBFIRST      (section 4.3a)
MINCELL_FLOOR_M = 5.0e-3                      # G-MINCELL       (section 5.1)
CYCLE_TOL_PCT = 0.02                          # S13, of RANGE   (section 3.3a)
CYCLE_WINDOW, CYCLE_INTERVAL, CYCLE_MIN_SAMPLES = 400, 50, 9
SIGN_CHANGES_MIN = 3                          # section 3.3
TREND_FRAC_MAX = 0.25                         # section 3.3

# G-CHECKMESH tolerance registry.  EMPTY = ZERO TOLERANCE (section 5.1).  An
# entry may only be added BEFORE the freeze and must carry its justification.
MESHQ_TOLERANCE = {}

NAMED_FEATURES = ("rack front face", "rack rear face", "rack side faces",
                  "supply tile face", "return face",
                  "cold-aisle/rack interface band",
                  "hot-aisle/rack interface band",
                  "floor boundary layer", "ceiling boundary layer",
                  "row-end margin")

GRADED_ROWS = ("G1", "G2", "G3", "G4")


class Refuse(Exception):
    pass


def refuse(msg):
    raise Refuse(msg)


# ------------------------------------------------------- reader-side guards

def resolve_unique(pattern):
    """Refuse when a glob matches more than one file where one is expected.

    This should be unreachable once clause 7 refuses a dirty postProcessing/.
    It is here anyway because A GUARD AND A READER THAT BOTH CHECK is the
    pattern that saved K2bU3R3, whose launch guard was live and enforcing
    while the rest of its instrument could not execute at all.  One of the two
    being dead must not be enough to produce a number.
    """
    hits = sorted(glob.glob(pattern))
    if not hits:
        refuse("no file matches %s" % pattern)
    if len(hits) > 1:
        refuse("GLOB COLLISION: %d files match %s -- %s. OpenFOAM writes a "
               "SECOND function-object file on restart rather than overwriting "
               "the first, so reading either is a WRONG NUMBER, not a crash. "
               "This reader refuses rather than picking one."
               % (len(hits), pattern, ", ".join(os.path.basename(h) for h in hits)))
    return hits[0]


# ------------------------------------------------------------ checkMesh gates

_GEOM_RE = re.compile(r"Mesh has (\d+) geometric \(non-empty/wedge\) directions "
                      r"\(([\d ]+)\)")


def read_checkmesh(case_dir):
    """Return everything the three checkMesh-derived gates need, or REFUSE.

    NEVER reads blockMeshDict.  The gate reads what was BUILT, not what was
    asked for.
    """
    path = os.path.join(case_dir, "log.checkMesh")
    if not os.path.isfile(path):
        refuse("%s has no log.checkMesh -- mesh quality and dimensionality are "
               "UNMEASURED, and unmeasured is not passing" % case_dir)
    with open(path, errors="replace") as fh:
        text = fh.read()

    # --- provenance limb: was the FULL check set run? -----------------------
    # Bare `checkMesh` prints `Mesh OK.` on a mesh the full set fails; the
    # face-tet and cell-determinant checks run only under these two flags.
    prov_ok = ("-allGeometry" in text) and ("-allTopology" in text)

    # --- verdict limb: what did checkMesh ITSELF say? -----------------------
    n_failed, failed_lines = None, []
    for ln in text.splitlines():
        m = re.search(r"Failed (\d+) mesh check", ln)
        if m:
            n_failed = int(m.group(1))
        if ln.strip() == "Mesh OK." and n_failed is None:
            n_failed = 0
        if "***" in ln:
            failed_lines.append(ln.strip())

    # --- the dimensionality line, matched SPECIFICALLY ----------------------
    # The same log prints `Mesh has 3 solution (non-empty) directions (1 1 1)`
    # a few lines away, and FOR A WEDGE MESH IT SAYS 3 WHILE THE MESH IS 2D.
    gm = _GEOM_RE.search(text)
    geom_line = gm.group(0) if gm else None
    n_geom = int(gm.group(1)) if gm else None

    # --- minimum cell dimension --------------------------------------------
    mc = re.search(r"Min volume = ([0-9.eE+-]+)", text)
    min_vol = float(mc.group(1)) if mc else None

    return dict(path=path, provenance_full_set=prov_ok, n_failed=n_failed,
                failed_lines=failed_lines, geometric_line=geom_line,
                n_geometric=n_geom, min_volume=min_vol)


def gate_checkmesh(cm):
    """G-CHECKMESH -- provenance limb then verdict limb.  Registration 5.1."""
    if not cm["provenance_full_set"]:
        return False, ("G-CHECKMESH PROVENANCE: %s does not evidence BOTH "
                       "-allGeometry and -allTopology. A log missing half the "
                       "checks is not evidence of a sound mesh, and the D-3D "
                       "gate reads this same log." % cm["path"])
    if cm["n_failed"] is None:
        return False, ("G-CHECKMESH VERDICT: %s carries NO verdict line -- "
                       "neither `Mesh OK.` nor `Failed N mesh checks`. Mesh "
                       "quality is UNMEASURED, and unmeasured is not passing."
                       % cm["path"])
    if cm["n_failed"] > 0:
        untolerated = [ln for ln in cm["failed_lines"]
                       if not any(k.lower() in ln.lower() for k in MESHQ_TOLERANCE)]
        if untolerated:
            return False, ("G-CHECKMESH VERDICT: checkMesh -allGeometry "
                           "-allTopology FAILED %d check(s) with no registered "
                           "tolerance covering: %s. The mesh is REBUILT, or a "
                           "tolerance is registered with its justification "
                           "BEFORE the freeze -- the gate is never relaxed to "
                           "let a mesh through after the mesh has been seen."
                           % (cm["n_failed"], "; ".join(untolerated[:3])))
    return True, "G-CHECKMESH PASS (full check set run, %d failed checks)" % cm["n_failed"]


def read_patch_census(case_dir):
    """D-3D: patch types from constant/polyMesh/boundary -- the BUILT mesh."""
    p = os.path.join(case_dir, "constant", "polyMesh", "boundary")
    if not os.path.isfile(p):
        refuse("%s has no constant/polyMesh/boundary" % case_dir)
    with open(p, errors="replace") as fh:
        text = fh.read()
    return {t: len(re.findall(r"type\s+%s\s*;" % t, text))
            for t in ("empty", "wedge", "patch", "wall", "symmetry",
                      "cyclic", "mappedWall")}


def gate_3d(cm, census):
    """G-3D.  Registration 5.2.  T4e and the whole T23G2 line were 2D wedges."""
    if cm["n_geometric"] is None:
        return False, ("G-3D: no `Mesh has N geometric (non-empty/wedge) "
                       "directions` line in %s. Dimensionality UNMEASURED."
                       % cm["path"])
    if cm["n_geometric"] != 3:
        return False, ("G-3D: %r -- this mesh has %d geometric directions, not "
                       "3. It is NOT a 3D case."
                       % (cm["geometric_line"], cm["n_geometric"]))
    bad = {k: v for k, v in census.items() if k in ("empty", "wedge") and v}
    if bad:
        return False, ("G-3D: the BUILT boundary carries %s. A wedge mesh "
                       "reports 3 SOLUTION directions while being 2D; this gate "
                       "reads the GEOMETRIC line and the patch census, never "
                       "blockMeshDict."
                       % ", ".join("%d %s patch(es)" % (v, k) for k, v in bad.items()))
    return True, "G-3D CONFIRMED: %r, no empty/wedge patches" % cm["geometric_line"]


def gate_mincell(case_dir, features=NAMED_FEATURES):
    """G-MINCELL -- minimum cell dimension per NAMED feature against the floor.

    cfd's M6 finding: a cusped trailing edge passed BOTH check sets and still
    destroyed the rung.  A geometry limb independent of checkMesh is required.
    """
    p = os.path.join(case_dir, "MINCELL.json")
    if not os.path.isfile(p):
        refuse("%s has no MINCELL.json -- the per-feature minimum cell "
               "dimension is UNMEASURED, and unmeasured is not passing. "
               "build_k2d.py writes it at build time." % case_dir)
    with open(p) as fh:
        got = json.load(fh)
    missing = [f for f in features if f not in got]
    if missing:
        return False, ("G-MINCELL: no measurement for named feature(s): %s"
                       % ", ".join(missing)), got
    under = {f: got[f] for f in features if float(got[f]) < MINCELL_FLOOR_M}
    if under:
        return False, ("G-MINCELL: feature(s) below the registered %.1f mm "
                       "floor: %s" % (MINCELL_FLOOR_M * 1e3,
                                      ", ".join("%s = %.4g m" % (k, v)
                                                for k, v in under.items()))), got
    return True, ("G-MINCELL PASS: every named feature >= %.1f mm (worst %.4g m)"
                  % (MINCELL_FLOOR_M * 1e3, min(float(got[f]) for f in features))), got


# --------------------------------------------------------------- G-MESHSIM

def built_cell_count(case_dir):
    """Cell count read from the BUILT polyMesh.  Never from a target."""
    owner = os.path.join(case_dir, "constant", "polyMesh", "owner")
    if not os.path.isfile(owner):
        refuse("%s has no constant/polyMesh/owner" % case_dir)
    with open(owner, "rb") as fh:
        head = fh.read(4096).decode("utf-8", "replace")
    m = re.search(r"nCells:\s*(\d+)", head)
    if not m:
        refuse("%s/constant/polyMesh/owner carries no nCells in its header note"
               % case_dir)
    return int(m.group(1))


def gate_meshsim(counts):
    """A ladder that grades on intended counts is grading on an intention."""
    n1, n2, n3 = (counts[L] for L in LEVELS)
    r_a, r_b = n2 / n1, n3 / n2
    ok = all(MESHSIM_LO <= r <= MESHSIM_HI for r in (r_a, r_b))
    msg = ("G-MESHSIM %s: BUILT counts %d / %d / %d, actual steps %.4f / %.4f "
           "(window [%.4f, %.4f] = 3.375 +- 5 %%), implied r = %.4f / %.4f"
           % ("PASS" if ok else "FAIL", n1, n2, n3, r_a, r_b,
              MESHSIM_LO, MESHSIM_HI, r_a ** (1 / DIM), r_b ** (1 / DIM)))
    return ok, msg, dict(built=counts, targets=TARGETS,
                         step_21=r_a, step_32=r_b,
                         r_21=r_a ** (1 / DIM), r_32=r_b ** (1 / DIM))


# ----------------------------------------------------------------- G-CYCLE

def classify_cycle(series, tol_pct=CYCLE_TOL_PCT):
    """CONVERGED / CYCLING / DRIFTING on the registered 3-part rule (3.3, 3.3a).

    Normalised by the RANGE THE QUANTITY SPANNED OVER THE RUN -- D393's
    repair, `heat_monitor_normaliser: range_spanned_over_run`.  A
    mean-normalised form here would reintroduce the defect D393 fixed.
    """
    if len(series) < CYCLE_MIN_SAMPLES:
        refuse("G-CYCLE: %d samples < the registered minimum %d. A spread over "
               "too few points is not a spread."
               % (len(series), CYCLE_MIN_SAMPLES))
    win = series[-CYCLE_MIN_SAMPLES:]
    rng = max(series) - min(series)
    if rng <= 0.0:
        refuse("G-CYCLE: the quantity never moved over the whole run (range 0), "
               "so 'has it stopped moving?' cannot be answered. NULL-VARIATION "
               "REFUSAL -- a quantity that CANNOT move scores perfectly on a "
               "test of whether it HAS stopped moving.")
    spread = max(win) - min(win)
    spread_pct = 100.0 * spread / rng

    diffs = [b - a for a, b in zip(win, win[1:])]
    signs = [1 if d > 0 else (-1 if d < 0 else 0) for d in diffs if d != 0]
    sign_changes = sum(1 for a, b in zip(signs, signs[1:]) if a != b)

    n = len(win)
    xs = list(range(n))
    mx, my = sum(xs) / n, sum(win) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in win)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, win))
    trend_frac = 0.0 if syy <= 0 or sxx <= 0 else (sxy * sxy) / (sxx * syy)

    if spread_pct <= tol_pct:
        state = "CONVERGED"
    elif sign_changes >= SIGN_CHANGES_MIN and trend_frac < TREND_FRAC_MAX:
        state = "CYCLING"
    else:
        state = "DRIFTING"
    return dict(state=state, spread_pct=spread_pct, range_over_run=rng,
                sign_changes=sign_changes, trend_frac=trend_frac,
                n_samples=len(series), normaliser="range_spanned_over_run")


def planted_cycle_control(base_series, tol_pct=CYCLE_TOL_PCT):
    """Section 3.3b.  The detector must be SHOWN able to detect a cycle.

    A cycle detector never shown able to detect a cycle is worth exactly as
    much as a zero from a blind reader.  REFUSES rather than degrading.
    """
    rng = max(base_series) - min(base_series)
    if rng <= 0:
        refuse("planted-cycle control: the base series has zero range, so no "
               "amplitude can be expressed against it")
    n = max(len(base_series), CYCLE_MIN_SAMPLES)
    level = sum(base_series) / len(base_series)

    def synth(amp_frac):
        # period 200 iterations = 4 samples at the 50-iteration cadence
        amp = amp_frac * (tol_pct / 100.0) * rng
        return [level + amp * math.sin(2 * math.pi * i / 4.0) for i in range(n)]

    pos = classify_cycle(synth(2.0), tol_pct)
    if pos["state"] != "CYCLING":
        refuse("PLANTED-CYCLE CONTROL FAILED (positive arm): a planted sinusoid "
               "at 2x the registered spread threshold, period 200 iterations, "
               "was classified %r and not CYCLING. The detector cannot see the "
               "phenomenon P-K2d-2 predicts, so this comparator will not grade."
               % pos["state"])

    clean = [level + rng * 0.5 * math.exp(-3.0 * i / n) for i in range(n)]
    neg = classify_cycle(clean, tol_pct)
    if neg["state"] == "CYCLING":
        refuse("PLANTED-CYCLE CONTROL FAILED (negative arm): a clean monotone "
               "decaying series was classified CYCLING. A detector that calls "
               "everything a cycle is as useless as one that calls nothing.")

    floor = None
    for frac in (1.0, 0.5, 0.25, 0.125, 0.0625):
        if classify_cycle(synth(frac), tol_pct)["state"] == "CYCLING":
            floor = frac
    return dict(positive_arm=pos["state"], negative_arm=neg["state"],
                detection_floor_frac_of_threshold=floor,
                note=("the smallest planted amplitude still classified CYCLING, "
                      "as a fraction of the registered spread threshold; a "
                      "CONVERGED reading without this figure is an unqualified "
                      "negative"))


# ------------------------------------------------------- planted-zero control

def planted_zero_control(series_path, level):
    """Rule 3.  Plant, read back FROM DISK, and REFUSE if unseen."""
    ok, seen = RT.plant_into_series(series_path, level, plant=RT.PLANT)
    if not ok or abs(seen - RT.PLANT) > RT.PLANT_READBACK_TOL:
        refuse("PLANTED-ZERO CONTROL FAILED at %s: planted %.6e, reader saw "
               "%r. A zero from a reader not shown able to see a non-zero is "
               "not evidence, and this comparator refuses rather than grading."
               % (level, RT.PLANT, seen))
    return dict(planted=RT.PLANT, seen=seen, ok=True)


# --------------------------------------------------------------- band + rows

def grade_row(name, triple):
    """Section 4.2, in order, one-way.  Only a CONVERGING triple is graded."""
    ann = []
    if triple["state"] in RT.NOT_A_RESULT_STATES:
        return dict(row=name, verdict="NOT A RESULT", triple_state=triple["state"],
                    values=triple["values"], order=triple["order"],
                    gci_pct=None, annotations=ann,
                    why=("triple is %s; the value, the triple and the order are "
                         "printed and NO GCI is quoted" % triple["state"]))
    if not RT.monotone(triple):
        return dict(row=name, verdict="NOT A RESULT", triple_state=triple["state"],
                    values=triple["values"], order=triple["order"],
                    gci_pct=None, annotations=ann,
                    why="values are not monotone; a GCI may never be quoted here")
    p = triple["order"]
    inside = ORDER_LO < p < ORDER_HI
    if inside and p < SUBFIRST:
        ann.append("p = %.4f < 1.0 on a nominally second-order scheme. "
                   "Sub-first-order convergence indicates an unresolved or "
                   "structurally-dominant error source -- an unresolved feature, "
                   "a discontinuity, or mesh defects that do not dilute under "
                   "refinement -- and NOT merely slow convergence. This PASS is "
                   "inside the registered band and stands; it may not be cited "
                   "as evidence of asymptotic convergence." % p)
    return dict(row=name, verdict="PASS" if inside else "GATE FAIL",
                triple_state=triple["state"], values=triple["values"],
                order=p, gci_pct=triple["GCI_pct"], annotations=ann,
                why=("observed order %.4f %s the registered band (%.1f, %.1f)"
                     % (p, "inside" if inside else "OUTSIDE", ORDER_LO, ORDER_HI)))


# ------------------------------------------------------------------ selftest

def _series(n=12, base=300.0, span=10.0, mode="converged"):
    out = []
    for i in range(n):
        if mode == "converged":
            out.append(base + span * math.exp(-4.0 * i / n))
        elif mode == "cycling":
            out.append(base + span * (0.02 if i else 1.0) * math.sin(2 * math.pi * i / 4.0)
                       if i else base + span)
        else:
            out.append(base + span * (1.0 - i / n))
    return out


def selftest():
    ok_all = True

    def arm(label, got, want):
        nonlocal ok_all
        good = (got == want)
        ok_all = ok_all and good
        print("  [%s] %s" % ("ok " if good else "BAD", label))

    def arm_refuses(label, fn):
        nonlocal ok_all
        try:
            fn()
            ok_all = False
            print("  [BAD] %s -- did NOT refuse" % label)
        except Refuse:
            print("  [ok ] %s -- REFUSED" % label)

    print("-- G-MESHSIM, on BUILT counts --")
    arm("CONTROL: exact 3.375 ladder -> PASS",
        gate_meshsim({"K2d_L1": 59259, "K2d_L2": 200000, "K2d_L3": 675000})[0], True)
    arm("a 2D ladder (2.25 steps) -> FAIL",
        gate_meshsim({"K2d_L1": 59259, "K2d_L2": 133333, "K2d_L3": 300000})[0], False)
    arm("built counts 4 %% off the target ratio -> still PASS (within +-5 %%)",
        gate_meshsim({"K2d_L1": 59259, "K2d_L2": 192000, "K2d_L3": 648000})[0], True)

    print("-- G-CYCLE, normalised by RANGE SPANNED (D393) --")
    conv = _series(mode="converged")
    # A quantity that travelled 10 K and is now flat to 4e-4 K: 0.004 % of the
    # range it spanned, inside the registered 0.02 %.
    # NOTE the shape: the window is the LAST 9 samples, so the transient must
    # be OUT of it. An earlier fixture left 300.5 inside the window and scored
    # 5.0 % -- the arm caught my test, not the code.
    settled = ([310.0, 305.0, 302.0]
               + [300.0005, 300.0004, 300.0003, 300.0002, 300.0001,
                  300.0001, 300.0001, 300.0001, 300.0001])
    arm("CONTROL: travelled 10 K then settled to 4e-4 K -> CONVERGED",
        classify_cycle(settled)["state"], "CONVERGED")
    # THE D393 PROPERTY, LOCKED IN BY AN ARM RATHER THAN ASSERTED IN A COMMENT.
    # A series creeping by 1e-9 per sample is ABSOLUTELY tiny and has NOT
    # converged: it never stopped moving, and its window spread is ~73 % of the
    # whole distance it ever travelled.  Under the OLD mean-normalised form it
    # would have scored ~3e-10 % of 300 K and passed triumphantly.  This arm is
    # the difference between the two normalisers, made executable.
    arm("a series still creeping by 1e-9/sample -> DRIFTING, NOT converged "
        "(absolute smallness buys nothing once the normaliser is the RANGE)",
        classify_cycle([300.0 + 1e-9 * i for i in range(12)])["state"], "DRIFTING")
    arm("a linear ramp -> DRIFTING", classify_cycle(_series(mode="ramp"))["state"],
        "DRIFTING")
    cyc = [300.0 + 5.0 * math.sin(2 * math.pi * i / 4.0) for i in range(12)]
    arm("a clean oscillation -> CYCLING", classify_cycle(cyc)["state"], "CYCLING")
    arm_refuses("too few samples -> REFUSE", lambda: classify_cycle([1.0, 2.0]))
    arm_refuses("a quantity that NEVER MOVED -> NULL-VARIATION REFUSAL",
                lambda: classify_cycle([300.0] * 12))

    print("-- 3.3b PLANTED-CYCLE CONTROL, the detector on itself --")
    pc = planted_cycle_control(conv)
    arm("positive arm: planted sinusoid at 2x threshold -> CYCLING",
        pc["positive_arm"], "CYCLING")
    arm("negative arm: clean monotone decay -> NOT CYCLING",
        pc["negative_arm"] != "CYCLING", True)
    arm("detection floor is MEASURED and reported, not asserted",
        pc["detection_floor_frac_of_threshold"] is not None, True)
    arm_refuses("a base series with zero range -> REFUSE",
                lambda: planted_cycle_control([1.0] * 12))

    print("-- section 4.2 order: only a CONVERGING triple is graded --")
    good = RT.triple_from_cells(53.6, 52.9, 52.5, 59259, 200000, 675000, dim=DIM)
    r = grade_row("G1", good)
    arm("CONVERGING inside the band -> PASS", r["verdict"], "PASS")
    bad = dict(good, state="OSCILLATORY")
    arm("OSCILLATORY -> NOT A RESULT whatever the value",
        grade_row("G1", bad)["verdict"], "NOT A RESULT")
    arm("...and NO GCI is quoted on it", grade_row("G1", bad)["gci_pct"], None)
    arm("DIVERGENT -> NOT A RESULT",
        grade_row("G1", dict(good, state="DIVERGENT"))["verdict"], "NOT A RESULT")
    sub = dict(good, order=0.7)
    rr = grade_row("G1", sub)
    arm("A-SUBFIRST: PASS with p < 1.0 -> annotated", bool(rr["annotations"]), True)
    arm("...and it is still a PASS, the band did not move", rr["verdict"], "PASS")
    arm("p outside the band -> GATE FAIL",
        grade_row("G1", dict(good, order=4.2))["verdict"], "GATE FAIL")

    print("-- reader-side glob refusal --")
    d = tempfile.mkdtemp(prefix="k2d_glob_")
    try:
        open(os.path.join(d, "T_in.dat"), "w").close()
        arm("one match -> resolves", os.path.basename(resolve_unique(os.path.join(d, "T_in*.dat"))),
            "T_in.dat")
        open(os.path.join(d, "T_in_0.dat"), "w").close()
        arm_refuses("TWO matches (the restart collision) -> REFUSE",
                    lambda: resolve_unique(os.path.join(d, "T_in*.dat")))
        arm_refuses("no match -> REFUSE",
                    lambda: resolve_unique(os.path.join(d, "nope*.dat")))
    finally:
        shutil.rmtree(d, ignore_errors=True)

    print("-- G-CHECKMESH: provenance limb then verdict limb --")
    full = "Exec   : checkMesh -allGeometry -allTopology\nMesh OK.\n"
    bare = "Exec   : checkMesh\nMesh OK.\n"
    failed = ("Exec   : checkMesh -allGeometry -allTopology\n"
              " ***Cells with small determinant found, number of cells: 2320\n"
              "Failed 2 mesh checks.\n")
    noverdict = "Exec   : checkMesh -allGeometry -allTopology\n(nothing)\n"

    def cm_from(text):
        d2 = tempfile.mkdtemp(prefix="k2d_cm_")
        with open(os.path.join(d2, "log.checkMesh"), "w") as fh:
            fh.write(text)
        try:
            return read_checkmesh(d2)
        finally:
            shutil.rmtree(d2, ignore_errors=True)

    arm("CONTROL: full check set, Mesh OK -> PASS", gate_checkmesh(cm_from(full))[0], True)
    arm("BARE checkMesh with `Mesh OK.` -> REFUSED on provenance "
        "(`Mesh OK.` is exactly what bare prints on a mesh the full set fails)",
        gate_checkmesh(cm_from(bare))[0], False)
    arm("full set, `Failed 2 mesh checks` -> NOT A RESULT (zero tolerance)",
        gate_checkmesh(cm_from(failed))[0], False)
    arm("NEITHER verdict line -> NOT A RESULT (unmeasured is not passing)",
        gate_checkmesh(cm_from(noverdict))[0], False)

    print("-- G-3D: the geometric line, never blockMeshDict --")
    g3 = ("Exec   : checkMesh -allGeometry -allTopology\n"
          "Mesh has 3 geometric (non-empty/wedge) directions (1 1 1)\n"
          "Mesh has 3 solution (non-empty) directions (1 1 1)\nMesh OK.\n")
    wedge = ("Exec   : checkMesh -allGeometry -allTopology\n"
             "Mesh has 2 geometric (non-empty/wedge) directions (0 1 1)\n"
             "Mesh has 3 solution (non-empty) directions (1 1 1)\nMesh OK.\n")
    arm("CONTROL: 3 geometric directions, no empty/wedge -> CONFIRMED",
        gate_3d(cm_from(g3), {"empty": 0, "wedge": 0})[0], True)
    arm("THE WEDGE TRAP: 2 geometric but 3 SOLUTION directions -> REFUSED "
        "(T4e and the whole T23G2 line)",
        gate_3d(cm_from(wedge), {"empty": 0, "wedge": 2})[0], False)
    arm("3 geometric directions but a wedge patch present -> REFUSED",
        gate_3d(cm_from(g3), {"empty": 0, "wedge": 2})[0], False)
    arm("no geometric line at all -> REFUSED",
        gate_3d(cm_from(noverdict), {"empty": 0, "wedge": 0})[0], False)

    print("\nSELFTEST %s" % ("PASS -- every arm fired as registered" if ok_all
                             else "FAIL -- an arm did not behave as registered"))
    return EXIT_OK if ok_all else EXIT_FAIL


def main(argv):
    if argv and argv[0] == "--selftest":
        return selftest()
    print(__doc__)
    print("REFUSE: no K2d case directory exists yet. This comparator grades a "
          "run; there is nothing to grade. Run --selftest to exercise the gates.")
    return EXIT_REFUSE


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Refuse as e:
        print("REFUSED (exit 2): %s" % e)
        sys.exit(EXIT_REFUSE)
