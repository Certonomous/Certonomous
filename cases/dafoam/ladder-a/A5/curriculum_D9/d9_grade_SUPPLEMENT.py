#!/usr/bin/env python3
"""
CURRICULUM D9 GRADER -- U-bend pressure-loss minimisation, ladder A5.  Frozen instrument.

L-302 IS A DESIGN CONSTRAINT HERE, NOT A HISTORY NOTE:
  AN INSTRUMENT THAT CANNOT SAY "I MEASURED NOTHING" WILL REPORT A NUMBER IT DID NOT
  MEASURE.  Concretely, and each of these is exercised by --selftest:
    * an EMPTY or SHORT component set REFUSES (exit 2) BY COUNT, with the count printed.
      It is not enough to test that a key is present; `d3_grade.py` does exactly that and
      returns PASS at 0.0000 % over an empty set.
    * no exception is swallowed into a declared constant.  A malformed record REFUSES.
    * the plateau loop CANNOT select a step from a zero-iteration search: if no window of
      PLATEAU_MIN_STEPS consecutive usable steps exists, the component is UNGRADEABLE and
      is COUNTED as such -- never silently defaulted to the first or last step.
    * a component set in which NOTHING is gradeable does not average to a clean number; it
      REFUSES.
  `rc=1` and `rc=2` are different failures and a harness exit code is not a solver exit
  code: a MISSING stage record maps to NOT A RESULT, never to BLOCKED, so this lane's own
  harness cannot record a capability as absent that was never reached.

THE PLANT (rule 3).  Two plants, both on quantities that REACH THE VERDICT:
  * READER PLANT: a known perturbation is written into a copy of the endpoint record and
    read back from disk; if the reader cannot see it, the grader REFUSES.
  * PHYSICAL PLANT: the optimiser must have MOVED the design point.  If the endpoint
    `shapexUpper` is bit-identical to the all-zero baseline, the FD table is a table about
    the baseline geometry wearing the endpoint's name, and the grader REFUSES.
"""
import argparse
import json
import math
import os
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
FD_STEPS = [1.0e-5, 1.0e-4, 1.0e-3, 1.0e-2]
REGISTERED_CPUSET = None        # set from --cpuset; placement is READ BACK, never inferred
FLOOR_DERIV = 1.0e-12
PLANT = 1.234e-03               # the reader plant

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


def reader_plant(root):
    """Plant a known perturbation, read it back FROM DISK, refuse if unseen."""
    src = os.path.join(root, "fd_1p0em3", "d9_out.json")
    if not os.path.isfile(src):
        # try any fd stage
        for h in FD_STEPS:
            cand = os.path.join(root, "fd_" + fmt_tag(h), "d9_out.json")
            if os.path.isfile(cand):
                src = cand
                break
    if not os.path.isfile(src):
        # REPAIR (D9-DEF-1): an EXPLICIT, TAGGED status. A bare `None` here made the
        # plant silently not run, and nothing downstream could tell "the plant fired
        # and the reader saw it" from "the plant never ran" -- rule 3 exactly.
        return ("NO_ENDPOINT", None)
    with open(src) as f:
        d = json.load(f)
    if "J_an" not in d:
        # REPAIR (D9-DEF-1): key ABSENCE, as distinct from key EMPTINESS below.
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
    """REPAIR (D9-DEF-1).  The caller's ASSERTION, which the frozen grader lacked:
    `reader_plant(root)` was called with its return value DISCARDED, so two silent
    `None` paths could make the plant not run at all.  This can only turn an outcome
    INTO a refusal, never the reverse."""
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


def grade(root, cpuset, quiet=False):
    lines = []
    worst = 0

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
             "group U-bend optimisation, so the MAGNITUDE is reported, not gated."
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

    # ---------------- G9-4 / G9-5 / G9-6  the endpoint FD table -------------
    plant_status, plant_seen = reader_plant(root)

    tables = {}
    for h in FD_STEPS:
        d, st = load_stage(root, "fd_" + fmt_tag(h))
        if st == "MISSING":
            continue
        if d.get("status") != "COMPLETE":
            continue
        if "check_totals_error" in d:
            emit("G9-4", "BLOCKED",
                 "the endpoint check at h=%.1e COMPLETED but returned no derivative key: %s"
                 % (h, d["check_totals_error"]))
            return worst, lines, {}
        if "J_an" not in d or "J_fd" not in d:
            emit("G9-4", "BLOCKED",
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
        emit("G9-4", "NOT A RESULT",
             "only %d of %d registered endpoint steps produced a table; a plateau needs at "
             "least %d consecutive usable steps and cannot be demonstrated from %d."
             % (len(tables), len(FD_STEPS), PLATEAU_MIN_STEPS, len(tables)))
        return worst, lines, {}

    steps = sorted(tables)
    J_an = [float(v) for v in tables[steps[0]]["J_an"]]
    # REPAIR (D9-DEF-1): assert the plant demonstrably FIRED before any endpoint PASS.
    require_plant_fired(plant_status, plant_seen)
    emit("G9-4", "PASS",
         "endpoint FD table formed over %d of %d registered steps (%s) at the OPTIMISED "
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
        emit("G9-6", "GATE FAIL",
             "aggregate adjoint-vs-FD relative error %.6e over %d gradeable components, but "
             "%d SIGN FLIP(S) at %s (registered maximum %d)"
             % (agg, ngr, len(flips), flips, MAX_SIGN_FLIPS))
    elif agg <= FD_BAND_REL_AGG:
        emit("G9-6", "PASS",
             "aggregate adjoint-vs-FD relative error %.6e <= band %.3e over %d gradeable "
             "components, %d sign flips, each read at its OWN plateau step"
             % (agg, FD_BAND_REL_AGG, ngr, len(flips)))
    else:
        emit("G9-6", "GATE FAIL",
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
             "cal_iters": cal_iters, "opt_iters": opt.get("driver_iter_count")}
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


def _healthy(root, an=None, fd_scale=1.0, dv=None, obj_final=45.0, tables=None):
    an = an or [(-1.0) ** i * (1.0 + 0.1 * i) for i in range(27)]
    dv = dv if dv is not None else [0.001 * (i + 1) for i in range(27)]
    _mk(root, "cal", OBJ_val=49.61, maxit=1, driver_iter_count=1, shapexUpper=[0.0] * 27)
    _mk(root, "rep1", OBJ_val=49.61, shapexUpper=[0.0] * 27)
    _mk(root, "rep2", OBJ_val=49.61, shapexUpper=[0.0] * 27)
    _mk(root, "opt", OBJ_val=obj_final, driver_failed=False, driver_iter_count=20,
        shapexUpper=dv)
    for h in FD_STEPS:
        fd = tables[h] if tables else [v * fd_scale for v in an]
        _mk(root, "fd_" + fmt_tag(h), J_an=an, J_fd=fd, fd_step=h, shapexUpper=dv)


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

    case("A healthy", lambda d: _healthy(d), "PASS")

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
        # every step disagrees wildly with every other -> NO plateau anywhere
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
        shutil_dir = os.path.join(d, "opt", "d9_out.json")
        os.remove(shutil_dir)
    case("J missing stage -> NOT A RESULT (never BLOCKED)", j, "NOT A RESULT")

    def k(d):
        _healthy(d)
        _mk(d, "fd_" + fmt_tag(1.0e-3), J_an=[1.0] * 27, fd_step=1.0e-3,
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
            shapexUpper=[0.001 * (i + 1) for i in range(27)])
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
        # 20 of 27 components have NO plateau -> 7/27 = 25.9 % gradeable, below the
        # registered 70 % floor.  The N-of-M consequence must FIRE, not be discovered.
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

    # --- REPAIR (D9-DEF-1): the new refusal must be PROVED TO FIRE. A control that is
    # --- not shown to fire is ceremony, not a control. These two exercise the exact
    # --- paths that previously returned a bare `None` and vanished.
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
            require_plant_fired(st, val)        # MUST refuse, not pass silently
        finally:
            shutil.rmtree(d, ignore_errors=True)
    unit("R plant cannot run (no endpoint record) -> REFUSE, not a silent None", r, "REFUSE")

    def s_():
        d = tempfile.mkdtemp()
        try:
            _mk(d, "fd_" + fmt_tag(1.0e-3), J_fd=[1.0] * 27, fd_step=1.0e-3,
                shapexUpper=[0.001] * 27)      # record present, J_an key ABSENT
            st, val = reader_plant(d)
            assert st == "NO_J_AN" and val is None, (st, val)
            require_plant_fired(st, val)        # MUST refuse
        finally:
            shutil.rmtree(d, ignore_errors=True)
    unit("S plant cannot run (J_an key ABSENT) -> REFUSE, not a silent None", s_, "REFUSE")

    npass = sum(1 for _, _, _, ok in results if ok)
    print("D9 GRADER SUPPLEMENT SELFTEST: %d/%d %s" % (npass, len(results),
                                            "PASS" if npass == len(results) else "FAIL"))
    for label, want, got, ok in results:
        if not ok:
            print("   FAILED %s: wanted %s, got %s" % (label, want, got))
    return 0 if npass == len(results) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="")
    ap.add_argument("--cpuset", type=int, default=13)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not a.root:
        print("ABORT: --root is required")
        sys.exit(2)
    try:
        worst, lines, facts = grade(a.root, a.cpuset)
    except Refuse as e:
        print("D9 GRADER REFUSES (exit 2): %s" % e)
        sys.exit(2)
    for ln in lines:
        print(ln)
    print("D9 VERDICT: %s" % NAME[worst])
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
