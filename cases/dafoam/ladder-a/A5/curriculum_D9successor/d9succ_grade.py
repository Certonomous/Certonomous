#!/usr/bin/env python3
"""
CURRICULUM D9successor GRADER -- U-bend pressure-loss minimisation with a
meshQualityKS non-orthogonality constraint, ladder A5.  DRAFT INSTRUMENT -- NOT
FROZEN (awaiting the dafoam-supervisor's check-1 read and freeze).

DERIVED FROM cases/dafoam/ladder-a/A5/curriculum_D9/d9_grade_SUPPLEMENT.py
(md5 baf7d69b3f6c32f64d5a47bf9d88c717) -- the REPAIRED D9 grader (D9-DEF-1: the
reader plant is asserted to have FIRED, not silently skipped).  The supplement, not
the pre-repair d9_grade.py, is the correct base: D9successor inherits the fired-plant
assertion.  CHANGES FROM THE SUPPLEMENT, and nowhere else (each is a line in the
_DELTAS_from_d9.diff):

  D9SUCC-G1  FD_STEPS is RE-REGISTERED to the a-priori-derived 3-step usable set
        {5e-5, 1e-4, 2e-4} (PREREGISTRATION.md section 2.3).  D9's {1e-5,1e-4,1e-3,1e-2}
        collided with a noise floor from below (1e-5) and a mesh-inversion ceiling from
        above (1e-3,1e-2); the new set is chosen from D9's MEASURED noise floor and
        inversion ceiling, NOT from which D9 steps crashed.  A legitimate re-set only
        because this is a NEW pre-registration (D9/RESULTS.md section 10 point 1).
        PLATEAU_MIN_STEPS stays 3, so ALL THREE must produce a table AND lie in a common
        plateau -- a strictly harder bar than D9's 3-of-4.

  D9SUCC-G2  PROBE_STEP = 1e-3 is the F-CEIL falsifier (PREREG section 6), NOT a usable
        step; it is predicted to invert the mesh at the constrained endpoint and is never
        counted toward the plateau.  Its outcome is reported by the launcher, not graded
        here.

  D9SUCC-G3  NEW HEADLINE GATE G-MESH (PREREG section 3.1): the RAW checkMesh
        "Mesh non-orthogonality Max" at the unperturbed optimised endpoint must be
        <= MAXNONORTH_MAX (70.0, the case's own checkMeshThreshold).  Graded on the RAW
        checkMesh value, NEVER on the KS aggregate the optimiser saw (KS >= true max, so
        KS <= 70 forces raw <= 70; the raw is what D9's 80.93 failure was measured in).
        The KS value the driver reported (nonOrtho_KS, recorded by D9SUCC-3 in the run
        script) is printed beside the raw value with the gap, as a measurement of the KS
        slack.  RULE 3: the checkMesh reader is PROVEN ABLE to see a planted non-zero
        (checkmesh_reader_plant) before any G-MESH zero/pass is trusted; if the reader
        cannot see it, the grader REFUSES.

  D9SUCC-G4  The G9-4 endpoint-table-completeness gate is relabelled G-FDPERF (PREREG
        section 3.2) with the 3-of-3 language; its logic (fewer than PLATEAU_MIN_STEPS
        tables -> NOT A RESULT) is D9's, unchanged.

  D9SUCC-G5  reader_plant iterates the (usable) FD_STEPS for an endpoint record to plant
        into, instead of hardcoding fd_1p0em3 first -- 1e-3 is no longer a usable step.

L-302 IS A DESIGN CONSTRAINT HERE, NOT A HISTORY NOTE (carried verbatim):
  AN INSTRUMENT THAT CANNOT SAY "I MEASURED NOTHING" WILL REPORT A NUMBER IT DID NOT
  MEASURE.  Empty/short component set REFUSES BY COUNT; no exception swallowed into a
  constant; the plateau loop cannot select from a zero-iteration search; a set in which
  nothing is gradeable REFUSES.  rc=1 and rc=2 are different failures; a MISSING stage is
  NOT A RESULT, never BLOCKED.

THE PLANT (rule 3).  THREE plants now, each on a quantity that REACHES A VERDICT:
  * READER PLANT (FD): a known perturbation into a copy of the endpoint J_an, read back.
  * PHYSICAL PLANT: the optimiser must have MOVED the design point.
  * CHECKMESH READER PLANT (D9SUCC-G3): a known maxNonOrth planted into a synthetic
    checkMesh log and read back, so G-MESH's reader is shown able to see a non-zero.
"""
import argparse
import json
import math
import os
import re
import sys

# ===========================================================================
# FROZEN CONSTANTS -- these are the pre-registration's table, and nothing here
# may be changed after the pre-registration commit.
# ===========================================================================
N_COMPONENTS_REQUIRED = 27      # len(shapexUpper); refuse on EMPTY or SHORT, BY COUNT
NOISE_FACTOR = 10.0             # an FD signal must exceed this many measured noise floors
PLATEAU_TOL_REL = 5.0e-2        # max relative spread of FD estimates inside a plateau
PLATEAU_MIN_STEPS = 3           # a plateau is >= 3 CONSECUTIVE usable steps of one sign
FD_BAND_REL_AGG = 5.0e-2        # aggregate adjoint-vs-FD band on GRADEABLE components
MIN_GRADED_FRACTION = 0.70      # >= 19 of 27 gradeable, else NOT A RESULT
MAX_SIGN_FLIPS = 0              # sign flips permitted on gradeable components
OBJ_IMPROVE_FACTOR = 10.0       # improvement must exceed this many measured noise floors
FD_STEPS = [5.0e-5, 1.0e-4, 2.0e-4]   # D9SUCC-G1: the 3 a-priori usable steps
PROBE_STEP = 1.0e-3                    # D9SUCC-G2: F-CEIL falsifier probe, NOT usable
REGISTERED_CPUSET = None        # set from --cpuset; placement is READ BACK, never inferred
FLOOR_DERIV = 1.0e-12
PLANT = 1.234e-03               # the FD reader plant
MAXNONORTH_MAX = 70.0           # D9SUCC-G3: G-MESH threshold = case's own checkMeshThreshold
CHECKMESH_PLANT = 42.42         # D9SUCC-G3: planted non-zero for the checkMesh reader control

# Named IN ADVANCE as potentially FD-ungradeable (pre-registration section 5c).
IDX16_CLASS = [8, 16, 17]

ORDER = {"PASS": 0, "GATE REACHED": 0, "GATE FAIL": 1, "NOT A RESULT": 2, "BLOCKED": 3}
NAME = {0: "PASS", 1: "GATE FAIL", 2: "NOT A RESULT", 3: "BLOCKED"}


class Refuse(Exception):
    """exit 2.  The instrument declines to report a number it cannot defend."""


def load_stage(root, name):
    """Return (record, status).  status is one of PRESENT / MISSING / MALFORMED.

    A MISSING stage is NOT A RESULT (the stage was never reached).
    A MALFORMED record REFUSES -- it is not quietly replaced by a default.
    """
    p = os.path.join(root, name, "d9_out.json")
    if not os.path.isfile(p):
        return None, "MISSING"
    try:
        with open(p) as f:
            d = json.load(f)
    except Exception as e:
        raise Refuse("stage %s: record at %s is unreadable (%r). A malformed record is "
                     "REFUSED, never replaced by a default." % (name, p, e))
    if not isinstance(d, dict):
        raise Refuse("stage %s: record is not an object" % name)
    return d, "PRESENT"


def check_components(vec, where):
    """Refuse on an EMPTY or SHORT set, BY COUNT, WITH THE COUNT PRINTED."""
    if vec is None:
        raise Refuse("%s: no `shapexUpper` key at all; component count is UNKNOWN, not zero"
                     % where)
    n = len(vec)
    if n != N_COMPONENTS_REQUIRED:
        raise Refuse("%s: component count %d != registered %d. An empty or short set is "
                     "REFUSED BY COUNT; it does not average to 0.0000%%."
                     % (where, n, N_COMPONENTS_REQUIRED))
    return n


# ===========================================================================
# D9SUCC-G3  THE checkMesh READER and ITS PLANTED-ZERO CONTROL (rule 3).
# ===========================================================================
_CHECKMESH_RE = re.compile(r"Mesh non-orthogonality Max:\s*([-+0-9.eE]+)")


def read_checkmesh_maxnonorth(log_path):
    """Return (value, status).  status: PRESENT / MISSING / UNPARSEABLE.

    Parses checkMesh's 'Mesh non-orthogonality Max: <v> average: ...' line and returns
    the LAST such value in the log (checkMesh may print it more than once; the last is
    the mesh as finally checked).
    """
    if not os.path.isfile(log_path):
        return None, "MISSING"
    val = None
    with open(log_path, errors="replace") as f:
        for line in f:
            m = _CHECKMESH_RE.search(line)
            if m:
                try:
                    val = float(m.group(1))
                except ValueError:
                    return None, "UNPARSEABLE"
    if val is None:
        return None, "UNPARSEABLE"
    return val, "PRESENT"


def checkmesh_reader_plant(root):
    """RULE 3: prove the checkMesh reader can SEE a non-zero before its zero is trusted.

    Writes a synthetic checkMesh log carrying a KNOWN maxNonOrth, reads it back through
    the SAME reader G-MESH uses, and REFUSES if the reader cannot see it.  A reader not
    shown able to see a non-zero cannot be trusted to report a passing (small) value.
    """
    tmp = os.path.join(root, ".d9succ_checkmesh_plant.log")
    with open(tmp, "w") as f:
        f.write("Some checkMesh preamble\n")
        f.write("    Mesh non-orthogonality Max: %.4f average: 11.0\n" % CHECKMESH_PLANT)
        f.write("Mesh OK.\n")
    seen, st = read_checkmesh_maxnonorth(tmp)
    os.remove(tmp)
    if st != "PRESENT" or seen is None or abs(seen - CHECKMESH_PLANT) > 1e-9:
        raise Refuse("CHECKMESH READER PLANT NOT SEEN: planted maxNonOrth %.4f and read "
                     "back %r (status %s). A zero from a reader not shown able to see a "
                     "non-zero is not evidence (rule 3)." % (CHECKMESH_PLANT, seen, st))
    return seen


def reader_plant(root):
    """Plant a known perturbation, read it back FROM DISK, refuse if unseen."""
    src = None
    # D9SUCC-G5: iterate the USABLE FD_STEPS for an endpoint record to plant into
    # (1e-3 is the probe now, not a usable step, and may have no J_an).
    for h in FD_STEPS:
        cand = os.path.join(root, "fd_" + fmt_tag(h), "d9_out.json")
        if os.path.isfile(cand):
            src = cand
            break
    if src is None or not os.path.isfile(src):
        # REPAIR (D9-DEF-1): an EXPLICIT, TAGGED status.
        return ("NO_ENDPOINT", None)
    with open(src) as f:
        d = json.load(f)
    if "J_an" not in d:
        return ("NO_J_AN", None)
    planted = dict(d)
    planted["J_an"] = list(d["J_an"])
    if not planted["J_an"]:
        raise Refuse("reader plant: the endpoint record carries an EMPTY J_an")
    planted["J_an"][0] = float(planted["J_an"][0]) + PLANT
    tmp = os.path.join(root, ".d9_reader_plant.json")
    with open(tmp, "w") as f:
        json.dump(planted, f)
    with open(tmp) as f:
        back = json.load(f)
    seen = abs(float(back["J_an"][0]) - float(d["J_an"][0]))
    os.remove(tmp)
    if abs(seen - PLANT) > 1e-12:
        raise Refuse("READER PLANT NOT SEEN: planted %.6e into J_an[0] and read back a "
                     "difference of %.6e. A zero from a reader not shown able to see a "
                     "non-zero is not evidence." % (PLANT, seen))
    return ("PLANTED", seen)


def require_plant_fired(status, value):
    """REPAIR (D9-DEF-1).  The caller's ASSERTION, which the pre-repair grader lacked."""
    if status != "PLANTED" or value is None:
        raise Refuse("PLANT DID NOT FIRE (status=%r): the grader was about to report an "
                     "endpoint table without a reader shown able to see a planted "
                     "non-zero. A zero from such a reader is not evidence (rule 3)."
                     % (status,))
    return value


def fmt_tag(h):
    return ("%g" % h).replace(".", "p").replace("-", "m").replace("+", "p") if False else \
        ("%.1e" % h).replace(".", "p").replace("-", "m").replace("+", "p")


def plateau(steps, fds, floor):
    """Per-component plateau search.

    Returns (h_ref, fd_ref, window, usable_flags) or (None, None, [], usable_flags).
    A component with no window of PLATEAU_MIN_STEPS consecutive usable steps is
    UNGRADEABLE.  The loop CANNOT fall through to a default step -- that is precisely
    the zero-iteration-plateau defect L-302 names.
    """
    usable = []
    for h, fd in zip(steps, fds):
        signal = abs(fd) * 2.0 * h      # |OBJ(+h) - OBJ(-h)|, reconstructed
        usable.append(signal > NOISE_FACTOR * floor and abs(fd) > FLOOR_DERIV)
    best = []
    cur = []
    for i, u in enumerate(usable):
        if not u:
            cur = []
            continue
        if cur and (fds[i] > 0) != (fds[cur[0]] > 0):
            cur = []
        cur = cur + [i]
        ok = True
        vals = [fds[j] for j in cur]
        lo, hi = min(map(abs, vals)), max(map(abs, vals))
        if lo <= 0 or (hi - lo) / lo > PLATEAU_TOL_REL:
            ok = False
        if ok and len(cur) > len(best):
            best = list(cur)
        if not ok:
            # shrink from the left until the window is tight again
            while len(cur) > 1:
                cur = cur[1:]
                vals = [fds[j] for j in cur]
                lo, hi = min(map(abs, vals)), max(map(abs, vals))
                if lo > 0 and (hi - lo) / lo <= PLATEAU_TOL_REL:
                    break
            if len(cur) > len(best):
                vals = [fds[j] for j in cur]
                lo, hi = min(map(abs, vals)), max(map(abs, vals))
                if lo > 0 and (hi - lo) / lo <= PLATEAU_TOL_REL:
                    best = list(cur)
    if len(best) < PLATEAU_MIN_STEPS:
        return None, None, [], usable
    mid = best[len(best) // 2]
    return steps[mid], fds[mid], best, usable


def grade(root, cpuset, meshlog=None, quiet=False):
    lines = []
    worst = 0
    if meshlog is None:
        meshlog = os.path.join(root, "mesh", "checkMesh.log")

    def emit(gate, verdict, msg):
        nonlocal worst
        lines.append("  %-8s %-13s %s" % (gate, verdict, msg))
        if verdict in ORDER:
            worst = max(worst, ORDER[verdict])

    # ---------------- G9-0  records, counts, cold start ----------------
    cal, cal_st = load_stage(root, "cal")
    r1, r1_st = load_stage(root, "rep1")
    r2, r2_st = load_stage(root, "rep2")
    opt, opt_st = load_stage(root, "opt")

    missing = [n for n, s in (("cal", cal_st), ("rep1", r1_st), ("rep2", r2_st),
                              ("opt", opt_st)) if s == "MISSING"]
    if missing:
        emit("G9-0", "NOT A RESULT",
             "stage record(s) absent: %s. A stage that was never reached is NOT A RESULT; "
             "it is NOT BLOCKED, which would record a capability as absent that was never "
             "tested." % ", ".join(missing))
        return worst, lines, {}

    for nm, d in (("cal", cal), ("rep1", r1), ("rep2", r2), ("opt", opt)):
        if d.get("status") != "COMPLETE":
            emit("G9-0", "NOT A RESULT",
                 "stage %s did not reach status COMPLETE (status=%r)" % (nm, d.get("status")))
            return worst, lines, {}
    n = check_components(opt.get("shapexUpper"), "stage opt")
    emit("G9-0", "PASS",
         "four stage records present and COMPLETE; component set length %d == registered %d"
         % (n, N_COMPONENTS_REQUIRED))

    # ---------------- G9-1  delta_repeat, MEASURED BEFORE ANY STEP IS SIZED -------
    o1, o2 = float(r1["OBJ_val"]), float(r2["OBJ_val"])
    delta_repeat = abs(o1 - o2)
    obj_base = 0.5 * (o1 + o2)
    eps_floor = 2.220446049250313e-16 * abs(obj_base)
    floor = max(delta_repeat, eps_floor)
    disclosure = ""
    if delta_repeat == 0.0:
        disclosure = (" A zero repeat bounds REPRODUCIBILITY only; it does NOT bound "
                      "iterative-truncation jitter, which the step sweep does. The floor "
                      "therefore falls back to the representational epsilon, and this is "
                      "disclosed rather than absorbed.")
    emit("G9-1", "PASS",
         "delta_repeat MEASURED BEFORE ANY FD STEP WAS SIZED: |OBJ(rep1)-OBJ(rep2)| = "
         "%.6e (OBJ = %.15e, %.15e); representational eps*|OBJ| = %.6e -> noise floor "
         "%.6e.%s" % (delta_repeat, o1, o2, eps_floor, floor, disclosure))

    # ---------------- G9-2  the calibration major ----------------
    cal_iters = cal.get("driver_iter_count", -1)
    emit("G9-2", "PASS",
         "CALIBRATION MAJOR ran FIRST and completed: maxit=%s, driver_iter_count=%s, "
         "OBJ = %.15e. The buy's container timeout was projected from this stage by the "
         "frozen rule min(3600, ceil(t_cal*(1+MAXIT_OPT)))."
         % (cal.get("maxit"), cal_iters, float(cal["OBJ_val"])))

    # ---------------- G9-3  the optimisation ----------------
    obj_final = float(opt["OBJ_val"])
    improvement = obj_base - obj_final
    thresh = OBJ_IMPROVE_FACTOR * floor
    if opt.get("driver_failed"):
        emit("G9-3", "GATE FAIL",
             "the SLSQP driver reported failure; OBJ_baseline = %.15e, OBJ_final = %.15e"
             % (obj_base, obj_final))
    elif improvement > thresh:
        emit("G9-3", "GATE REACHED",
             "pressure loss DECREASED by %.6e (%.4f %%): OBJ_baseline = %.15e -> "
             "OBJ_final = %.15e, against a threshold of %.1f x the measured noise floor "
             "= %.6e; driver_iter_count = %s. NO REFERENCE VALUE EXISTS for a single-DV-"
             "group U-bend optimisation, so the MAGNITUDE is reported, not gated. A "
             "CONSTRAINED optimum is generally WORSE (higher OBJ) than the unconstrained "
             "one; that is expected and is not a failure (PREREG section 3.4)."
             % (improvement, 100.0 * improvement / abs(obj_base), obj_base, obj_final,
                OBJ_IMPROVE_FACTOR, thresh, opt.get("driver_iter_count")))
    else:
        emit("G9-3", "GATE FAIL",
             "pressure loss did not decrease beyond the measured noise floor: "
             "OBJ_baseline = %.15e, OBJ_final = %.15e, improvement %.6e <= threshold %.6e"
             % (obj_base, obj_final, improvement, thresh))

    # ---------------- THE PHYSICAL PLANT -----------------------------------
    dv = [float(v) for v in opt["shapexUpper"]]
    l2 = math.sqrt(sum(v * v for v in dv))
    if l2 == 0.0:
        raise Refuse("PHYSICAL PLANT NOT SEEN: the endpoint design point is bit-identical "
                     "to the all-zero baseline (l2 = 0). An FD table taken there is a table "
                     "about the BASELINE geometry wearing the endpoint's name.")

    # ---------------- D9SUCC-G3  G-MESH  THE HEADLINE ----------------------
    # RULE 3: the checkMesh reader is proven able to see a planted non-zero FIRST.
    checkmesh_reader_plant(root)
    mval, mstat = read_checkmesh_maxnonorth(meshlog)
    ks_ep = opt.get("nonOrtho_KS")
    ks_txt = ("%.4f" % ks_ep) if isinstance(ks_ep, (int, float)) else "unavailable"
    if mstat == "MISSING":
        emit("G-MESH", "NOT A RESULT",
             "endpoint checkMesh log absent at %s; the raw maxNonOrth cannot be read, so the "
             "headline is NOT A RESULT (the stage was never reached), never a silent pass."
             % meshlog)
    elif mstat == "UNPARSEABLE" or mval is None or not math.isfinite(mval):
        emit("G-MESH", "NOT A RESULT",
             "endpoint checkMesh log at %s carries no parseable finite 'Mesh non-orthogonality "
             "Max:' value (read %r)." % (meshlog, mval))
    elif mval <= MAXNONORTH_MAX:
        gap = (ks_ep - mval) if isinstance(ks_ep, (int, float)) else None
        gap_txt = ("%.4f" % gap) if gap is not None else "unavailable"
        emit("G-MESH", "PASS",
             "THE FIX WORKS: raw checkMesh maxNonOrth %.4f <= %.1f (the case's own "
             "checkMeshThreshold). D9's unconstrained endpoint was 80.93. KS value the driver "
             "saw = %s; KS-minus-raw slack = %s (KS is a smooth OVER-BOUND of the true max, so "
             "KS <= 70 forces raw <= 70)." % (mval, MAXNONORTH_MAX, ks_txt, gap_txt))
    else:
        emit("G-MESH", "GATE FAIL",
             "raw checkMesh maxNonOrth %.4f > %.1f: the constraint did NOT hold at convergence "
             "(the mechanism as configured does not bind). KS value the driver saw = %s. This "
             "is a reportable finding." % (mval, MAXNONORTH_MAX, ks_txt))

    # ---------------- G-FDPERF / G9-5 / G9-6  the endpoint FD table ---------
    plant_status, plant_seen = reader_plant(root)

    tables = {}
    for h in FD_STEPS:
        d, st = load_stage(root, "fd_" + fmt_tag(h))
        if st == "MISSING":
            continue
        if d.get("status") != "COMPLETE":
            continue
        if "check_totals_error" in d:
            emit("G-FDPERF", "BLOCKED",
                 "the endpoint check at h=%.1e COMPLETED but returned no derivative key: %s"
                 % (h, d["check_totals_error"]))
            return worst, lines, {}
        if "J_an" not in d or "J_fd" not in d:
            emit("G-FDPERF", "BLOCKED",
                 "the endpoint check at h=%.1e COMPLETED but carries no J_an/J_fd" % h)
            return worst, lines, {}
        check_components(d.get("J_an"), "endpoint h=%.1e (J_an)" % h)
        check_components(d.get("J_fd"), "endpoint h=%.1e (J_fd)" % h)
        # the endpoint must be AT the optimised design point, not the baseline
        dv_here = [float(v) for v in d["shapexUpper"]]
        if max(abs(a - b) for a, b in zip(dv_here, dv)) > 1e-12:
            raise Refuse("endpoint h=%.1e was evaluated at a DIFFERENT design point from "
                         "the driver's endpoint; the FD table does not describe the "
                         "geometry the verdict is about." % h)
        tables[h] = d

    if len(tables) < PLATEAU_MIN_STEPS:
        emit("G-FDPERF", "NOT A RESULT",
             "only %d of %d registered USABLE endpoint steps produced a table; a plateau "
             "needs at least %d consecutive usable steps and cannot be demonstrated from %d. "
             "PREREG section 3.2/3.3: if G-MESH PASSED but the endpoint admits fewer than 3 FD "
             "tables, the item is NOT A RESULT and that is a GOOD result -- it measures the "
             "mesh-quality constraint as necessary-but-not-sufficient and motivates the "
             "primal-tightening successor."
             % (len(tables), len(FD_STEPS), PLATEAU_MIN_STEPS, len(tables)))
        return worst, lines, {}

    steps = sorted(tables)
    J_an = [float(v) for v in tables[steps[0]]["J_an"]]
    # REPAIR (D9-DEF-1): assert the FD reader plant demonstrably FIRED before any endpoint PASS.
    require_plant_fired(plant_status, plant_seen)
    emit("G-FDPERF", "PASS",
         "endpoint FD table formed over %d of %d registered usable steps (%s) at the OPTIMISED "
         "design point (l2(shapexUpper) = %.10e, %d components); READER PLANT status "
         "%s, planted %.6e and read back %.6e from disk"
         % (len(steps), len(FD_STEPS), ", ".join("%.1e" % h for h in steps), l2, len(dv),
            plant_status, PLANT, plant_seen))

    gradeable, ungradeable, rows = [], [], []
    for i in range(N_COMPONENTS_REQUIRED):
        fds = [float(tables[h]["J_fd"][i]) for h in steps]
        h_ref, fd_ref, win, usable = plateau(steps, fds, floor)
        if h_ref is None:
            ungradeable.append(i)
            rows.append((i, None, None, J_an[i], None, usable))
            continue
        rel = abs(J_an[i] - fd_ref) / abs(fd_ref) if abs(fd_ref) > FLOOR_DERIV else float("inf")
        gradeable.append(i)
        rows.append((i, h_ref, fd_ref, J_an[i], rel, usable))

    m = N_COMPONENTS_REQUIRED
    ngr = len(gradeable)
    if ngr == 0:
        raise Refuse("NOT ONE of %d components has a demonstrated plateau. An aggregate "
                     "over an empty gradeable set is REFUSED, not reported as 0.0000%%." % m)

    named = sorted(set(ungradeable) & set(IDX16_CLASS))
    unnamed = sorted(set(ungradeable) - set(IDX16_CLASS))
    frac = ngr / float(m)
    if frac < MIN_GRADED_FRACTION:
        emit("G9-5", "NOT A RESULT",
             "only %d of %d components (%.1f %%) have a demonstrated plateau, below the "
             "registered floor of %.0f %%. Ungradeable: named-in-advance %s; NOT named in "
             "advance %s." % (ngr, m, 100 * frac, 100 * MIN_GRADED_FRACTION, named, unnamed))
    else:
        emit("G9-5", "PASS",
             "N-of-M ENDPOINT VERIFICATION BY CONSTRUCTION: %d of %d components (%.1f %%) "
             "have a plateau demonstrated over >= %d consecutive usable steps, above the "
             "registered floor of %.0f %%. FD-UNGRADEABLE: %d component(s) -- named in "
             "advance (idx16-class) %s; NOT named in advance %s. Ungradeable components are "
             "EXCLUDED from the aggregate WITH THE COUNT PRINTED, never averaged in as zeros."
             % (ngr, m, 100 * frac, PLATEAU_MIN_STEPS, 100 * MIN_GRADED_FRACTION,
                len(ungradeable), named, unnamed))

    num = sum(abs(J_an[i] - rows[i][2]) for i in gradeable)
    den = sum(abs(rows[i][2]) for i in gradeable)
    agg = num / den if den > 0 else float("inf")
    flips = [i for i in gradeable if (J_an[i] > 0) != (rows[i][2] > 0)]
    if len(flips) > MAX_SIGN_FLIPS:
        emit("G-GRAD", "GATE FAIL",
             "aggregate adjoint-vs-FD relative error %.6e over %d gradeable components, but "
             "%d SIGN FLIP(S) at %s (registered maximum %d)"
             % (agg, ngr, len(flips), flips, MAX_SIGN_FLIPS))
    elif agg <= FD_BAND_REL_AGG:
        emit("G-GRAD", "PASS",
             "aggregate adjoint-vs-FD relative error %.6e <= band %.3e over %d gradeable "
             "components, %d sign flips, each read at its OWN plateau step"
             % (agg, FD_BAND_REL_AGG, ngr, len(flips)))
    else:
        emit("G-GRAD", "GATE FAIL",
             "aggregate adjoint-vs-FD relative error %.6e > band %.3e over %d gradeable "
             "components, %d sign flips" % (agg, FD_BAND_REL_AGG, ngr, len(flips)))

    # ---------------- G9-7  placement, COST ROW ONLY ----------------
    affs = {}
    for nm, d in [("cal", cal), ("rep1", r1), ("rep2", r2), ("opt", opt)] + \
                 [("fd_%.1e" % h, tables[h]) for h in steps]:
        affs[nm] = d.get("sched_affinity")
    bad = {k: v for k, v in affs.items() if v != [cpuset]}
    if bad:
        emit("G9-7", "GATE FAIL",
             "COST-ATTRIBUTION ROW ONLY, and it does NOT touch the derivative verdict: "
             "stage(s) %s report measured affinity != registered cpuset [%d]"
             % (bad, cpuset))
    else:
        emit("G9-7", "PASS",
             "every stage reports measured CPU affinity [%d], equal to the registered "
             "cpuset; placement is READ FROM THE PROCESS, not inferred from the flag"
             % cpuset)

    facts = {"delta_repeat": delta_repeat, "floor": floor, "obj_base": obj_base,
             "obj_final": obj_final, "improvement": improvement, "agg": agg,
             "n_gradeable": ngr, "m": m, "ungradeable": ungradeable,
             "named_ungradeable": named, "unnamed_ungradeable": unnamed,
             "rows": rows, "steps": steps, "flips": flips, "l2_dv": l2,
             "cal_iters": cal_iters, "opt_iters": opt.get("driver_iter_count"),
             "maxnonorth": mval, "maxnonorth_status": mstat, "nonOrtho_KS": ks_ep}
    return worst, lines, facts


# ===========================================================================
# SELFTEST -- the grader is PROVEN ABLE TO REFUSE before it is allowed to pass
# anything.  Every case below is a failure mode this grader must catch.
# ===========================================================================
def _mk(root, name, **kw):
    os.makedirs(os.path.join(root, name), exist_ok=True)
    rec = {"status": "COMPLETE", "sched_affinity": [13]}
    rec.update(kw)
    with open(os.path.join(root, name, "d9_out.json"), "w") as f:
        json.dump(rec, f)


def _mk_meshlog(root, maxnonorth):
    d = os.path.join(root, "mesh")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "checkMesh.log"), "w") as f:
        f.write("Checking geometry...\n")
        f.write("    Mesh non-orthogonality Max: %.4f average: 11.0\n" % maxnonorth)
        f.write("Mesh OK.\n")


def _healthy(root, an=None, fd_scale=1.0, dv=None, obj_final=45.0, tables=None,
             maxnonorth=65.0):
    an = an or [(-1.0) ** i * (1.0 + 0.1 * i) for i in range(27)]
    dv = dv if dv is not None else [0.001 * (i + 1) for i in range(27)]
    _mk(root, "cal", OBJ_val=49.61, maxit=1, driver_iter_count=1, shapexUpper=[0.0] * 27)
    _mk(root, "rep1", OBJ_val=49.61, shapexUpper=[0.0] * 27)
    _mk(root, "rep2", OBJ_val=49.61, shapexUpper=[0.0] * 27)
    _mk(root, "opt", OBJ_val=obj_final, driver_failed=False, driver_iter_count=20,
        shapexUpper=dv, nonOrtho_KS=maxnonorth + 8.0)
    for h in FD_STEPS:
        fd = tables[h] if tables else [v * fd_scale for v in an]
        _mk(root, "fd_" + fmt_tag(h), J_an=an, J_fd=fd, fd_step=h, shapexUpper=dv)
    if maxnonorth is not None:
        _mk_meshlog(root, maxnonorth)


def selftest():
    global shutil, tempfile
    import shutil
    import tempfile
    results = []

    def case(label, build, want):
        d = tempfile.mkdtemp()
        try:
            build(d)
            try:
                worst, lines, facts = grade(d, 13)
                got = NAME[worst]
            except Refuse as e:
                got = "REFUSE"
            ok = (got == want)
            results.append((label, want, got, ok))
        finally:
            shutil.rmtree(d, ignore_errors=True)

    case("A healthy (G-MESH PASS at 65<=70)", lambda d: _healthy(d), "PASS")

    def b(d):
        _healthy(d)
        _mk(d, "opt", OBJ_val=45.0, driver_failed=False, driver_iter_count=20,
            shapexUpper=[])
    case("B empty component set refuses WITH COUNT", b, "REFUSE")

    def c(d):
        _healthy(d)
        _mk(d, "opt", OBJ_val=45.0, driver_failed=False, driver_iter_count=20,
            shapexUpper=[0.1] * 12)
    case("C short component set refuses WITH COUNT", c, "REFUSE")

    def e(d):
        _healthy(d, dv=[0.0] * 27)
    case("E physical plant: unmoved design point refuses", e, "REFUSE")

    def f(d):
        _healthy(d)
        for h in FD_STEPS:
            _mk(d, "fd_" + fmt_tag(h), J_an=[1.0] * 27, J_fd=[],
                fd_step=h, shapexUpper=[0.001 * (i + 1) for i in range(27)])
    case("F empty FD vector refuses WITH COUNT", f, "REFUSE")

    def g(d):
        an = [(-1.0) ** i * (1.0 + 0.1 * i) for i in range(27)]
        dv = [0.001 * (i + 1) for i in range(27)]
        t = {h: [v * (1.0 + 3.0 * k) for v in an] for k, h in enumerate(FD_STEPS)}
        _healthy(d, an=an, dv=dv, tables=t)
    case("G no plateau anywhere refuses (empty gradeable set)", g, "REFUSE")

    def hh(d):
        an = [(-1.0) ** i * (1.0 + 0.1 * i) for i in range(27)]
        _healthy(d, an=an, fd_scale=2.0)
    case("H disagreement -> GATE FAIL", hh, "GATE FAIL")

    def i_(d):
        an = [(-1.0) ** i * (1.0 + 0.1 * i) for i in range(27)]
        fd = [-v for v in an]
        _healthy(d, an=an, tables={h: fd for h in FD_STEPS})
    case("I sign flips -> GATE FAIL", i_, "GATE FAIL")

    def j(d):
        _healthy(d)
        os.remove(os.path.join(d, "opt", "d9_out.json"))
    case("J missing stage -> NOT A RESULT (never BLOCKED)", j, "NOT A RESULT")

    def k(d):
        _healthy(d)
        _mk(d, "fd_" + fmt_tag(1.0e-4), J_an=[1.0] * 27, fd_step=1.0e-4,
            check_totals_error="no key", shapexUpper=[0.001 * (i + 1) for i in range(27)])
    case("K completed-but-no-derivative-key -> BLOCKED", k, "BLOCKED")

    def l(d):
        _healthy(d)
        with open(os.path.join(d, "opt", "d9_out.json"), "w") as f:
            f.write("{not json")
    case("L malformed record refuses (no swallowed exception)", l, "REFUSE")

    def m(d):
        _healthy(d)
        for h in FD_STEPS:
            _mk(d, "fd_" + fmt_tag(h),
                J_an=[(-1.0) ** i * (1.0 + 0.1 * i) for i in range(27)],
                J_fd=[(-1.0) ** i * (1.0 + 0.1 * i) for i in range(27)],
                fd_step=h, shapexUpper=[0.0] * 27)
    case("M endpoint at a different design point refuses", m, "REFUSE")

    def nn(d):
        _healthy(d)
        _mk(d, "opt", OBJ_val=49.61, driver_failed=False, driver_iter_count=20,
            shapexUpper=[0.001 * (i + 1) for i in range(27)], nonOrtho_KS=73.0)
    case("N no improvement -> GATE FAIL", nn, "GATE FAIL")

    def o(d):
        _healthy(d)
        _mk(d, "cal", OBJ_val=49.61, maxit=1, driver_iter_count=1,
            shapexUpper=[0.0] * 27, status="STARTED")
    case("O incomplete stage -> NOT A RESULT", o, "NOT A RESULT")

    def p(d):
        _healthy(d)
        _mk(d, "rep1", OBJ_val=49.61, shapexUpper=[0.0] * 27, sched_affinity=[0])
    case("P misplacement caught WITHOUT touching the derivative verdict", p, "GATE FAIL")

    def q(d):
        an = [(-1.0) ** i * (1.0 + 0.1 * i) for i in range(27)]
        dv = [0.001 * (i + 1) for i in range(27)]
        t = {}
        for k, h in enumerate(FD_STEPS):
            col = []
            for i, v in enumerate(an):
                col.append(v * (1.0 + 3.0 * k) if i >= 7 else v)
            t[h] = col
        _healthy(d, an=an, dv=dv, tables=t)
    case("Q partial gradeable set below the N-of-M floor -> NOT A RESULT", q, "NOT A RESULT")

    # ---- D9SUCC-G3: G-MESH gate must be exercised in every direction ----
    def v_(d):
        _healthy(d, maxnonorth=80.93)   # F-MESH-NULL measured baseline: 80.93 > 70
    case("V G-MESH raw maxNonOrth 80.93 > 70 -> GATE FAIL (F-MESH-NULL)", v_, "GATE FAIL")

    def w_(d):
        _healthy(d)
        os.remove(os.path.join(d, "mesh", "checkMesh.log"))
    case("W G-MESH checkMesh log absent -> NOT A RESULT", w_, "NOT A RESULT")

    def x_(d):
        _healthy(d)
        # log present but no parseable non-ortho line
        with open(os.path.join(d, "mesh", "checkMesh.log"), "w") as f:
            f.write("Checking geometry...\nMesh OK.\n")
    case("X G-MESH checkMesh log unparseable -> NOT A RESULT", x_, "NOT A RESULT")

    def y_(d):
        _healthy(d)
        _mk(d, "fd_" + fmt_tag(FD_STEPS[0]), J_an=[1.0] * 27, J_fd=[1.0] * 27,
            fd_step=FD_STEPS[0], shapexUpper=[0.001 * (i + 1) for i in range(27)])
        os.remove(os.path.join(d, "fd_" + fmt_tag(FD_STEPS[1]), "d9_out.json"))
        os.remove(os.path.join(d, "fd_" + fmt_tag(FD_STEPS[2]), "d9_out.json"))
    case("Y G-FDPERF only 1 of 3 usable tables -> NOT A RESULT", y_, "NOT A RESULT")

    # --- D9-DEF-1 units: the FD reader plant must be PROVED TO FIRE ---
    def unit(label, fn, want):
        try:
            fn()
            got = "NO REFUSAL"
        except Refuse:
            got = "REFUSE"
        results.append((label, want, got, got == want))

    def r():
        d = tempfile.mkdtemp()
        try:
            st, val = reader_plant(d)          # empty root: no endpoint record at all
            assert st == "NO_ENDPOINT" and val is None, (st, val)
            require_plant_fired(st, val)        # MUST refuse
        finally:
            shutil.rmtree(d, ignore_errors=True)
    unit("R FD plant cannot run (no endpoint record) -> REFUSE, not a silent None", r, "REFUSE")

    def s_():
        d = tempfile.mkdtemp()
        try:
            _mk(d, "fd_" + fmt_tag(FD_STEPS[0]), J_fd=[1.0] * 27, fd_step=FD_STEPS[0],
                shapexUpper=[0.001] * 27)      # record present, J_an key ABSENT
            st, val = reader_plant(d)
            assert st == "NO_J_AN" and val is None, (st, val)
            require_plant_fired(st, val)        # MUST refuse
        finally:
            shutil.rmtree(d, ignore_errors=True)
    unit("S FD plant cannot run (J_an key ABSENT) -> REFUSE, not a silent None", s_, "REFUSE")

    # --- D9SUCC-G3 unit: the checkMesh reader plant must be PROVED TO SEE a non-zero ---
    def t_():
        d = tempfile.mkdtemp()
        try:
            seen = checkmesh_reader_plant(d)    # MUST see CHECKMESH_PLANT, else refuse
            assert abs(seen - CHECKMESH_PLANT) < 1e-9, seen
        finally:
            shutil.rmtree(d, ignore_errors=True)
    unit("T checkMesh reader plant SEES a planted non-zero (no silent zero)", t_, "NO REFUSAL")

    npass = sum(1 for _, _, _, ok in results if ok)
    print("D9successor GRADER SELFTEST: %d/%d %s" % (npass, len(results),
                                            "PASS" if npass == len(results) else "FAIL"))
    for label, want, got, ok in results:
        if not ok:
            print("   FAILED %s: wanted %s, got %s" % (label, want, got))
    return 0 if npass == len(results) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="")
    ap.add_argument("--cpuset", type=int, default=13)
    ap.add_argument("--meshlog", default="", help="endpoint checkMesh log for G-MESH")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not a.root:
        print("ABORT: --root is required")
        sys.exit(2)
    try:
        worst, lines, facts = grade(a.root, a.cpuset, meshlog=(a.meshlog or None))
    except Refuse as e:
        print("D9successor GRADER REFUSES (exit 2): %s" % e)
        sys.exit(2)
    for ln in lines:
        print(ln)
    print("D9successor VERDICT: %s" % NAME[worst])
    if facts.get("rows"):
        print("\nPER-COMPONENT ENDPOINT TABLE (adjoint vs FD at each component's OWN plateau step):")
        print("  %-5s %-11s %-16s %-16s %-12s %s" %
              ("idx", "h*", "FD(h*)", "adjoint", "rel", "usable-by-step"))
        for i, h, fd, an, rel, usable in facts["rows"]:
            if h is None:
                print("  %-5d %-11s %-16s %-16.9e %-12s %s   FD-UNGRADEABLE%s"
                      % (i, "-", "-", an, "-",
                         "".join("U" if u else "." for u in usable),
                         " (NAMED IN ADVANCE)" if i in IDX16_CLASS else ""))
            else:
                print("  %-5d %-11.1e %-16.9e %-16.9e %-12.6e %s"
                      % (i, h, fd, an, rel, "".join("U" if u else "." for u in usable)))
    sys.exit(0 if worst == 0 else 1)


if __name__ == "__main__":
    main()
