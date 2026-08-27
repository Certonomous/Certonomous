#!/usr/bin/env python3
"""T9a-R1c -- the FROZEN comparator.  A FLOOR DEMONSTRATION, and nothing else.

WHAT THIS RUNG CLAIMS, in one sentence, and it makes exactly this claim and no
more:

    THE DISCRETISATION ERROR IN T_i1 IS BELOW X = 1.0e-04 K AT 35 CELLS.

That is a STRICTLY WEAKER claim than grid convergence, and it is the claim the
evidence supports.  It is graded by ONE number at ONE level against ONE
pre-registered absolute threshold.

WHAT THE SENTENCE DELIBERATELY DOES NOT SAY, per VERIFICATION_CHARTER 2h.4
conditions (4) and (5).  It does not say "the solution is correct to X" -- a
floor demonstration WORDED as a continuum claim IS a continuum claim and 2f.3
would catch it.  And it does not say "so the answer does not depend on the
mesh": that phrase appeared in 2g.3's own drafting and was NARROWED by 2h.4(5)
against it, because a floor demonstration establishes the error AT THE MESHES
MEASURED and nothing about finer ones.  Establishing behaviour ACROSS meshes is
what a Roache triple is for, and this instrument deliberately has none.  The
claim is bounded by the meshes actually run and is extrapolated to none.

WHY THE INSTRUMENT CHANGED, and it is the whole reason this file exists.  The
predecessor T9a-R1b (`W1b`) registered a Roache triple on this case, measured
it EXACT (e21 -2.842e-13 K, e32 3.240e-12 K), and graded the row PASS on a
FLOOR EXCEPTION to standing rule 5 frozen before compute.  VERIFICATION_CHARTER
section 2g (v1.16, 2026-08-27) REFUSED that exception:

    "A pre-registration fixes the gate, threshold, cap and label FOR ITS CASE.
     It has no power to disapply a standing rule, and an exception to one is
     void however early it was frozen."

The decisive ground is that rule 5's gate is ONE-WAY -- "the gate can only turn
a PASS or GATE FAIL INTO NOT A RESULT, never the reverse" -- so an exception
yielding PASS where rule 5 yields NOT A RESULT runs the gate backwards.  The
same ruling's diagnosis, section 2g.3: THE WRONG INSTRUMENT WAS REGISTERED.
Where the discretisation error is below the registered floor at every level, a
Roache triple has nothing to measure; p = ln|e32/e21| / ln r on two round-off
differences is noise divided by noise.  Rule 5 refuses to compute an ORDER from
nothing.  It does not say the VALUE is worthless.

SO THIS FILE COMPUTES NO TRIPLE AT ALL.  There is nothing to gate and nothing
to bypass.  Two guards make that structural rather than stated:

  * C_CLASS -- every registered row carries a `claim_class`, and the only
    admissible classes are FLOOR_DEMONSTRATION (graded against the absolute
    floor) and REPORTED (no verdict).  A row registered with any other class --
    in particular any row claiming a grid-convergence property -- REFUSES,
    because this comparator has no triple gate to route it through.  Driven.

  * C_NOTRIPLE -- an AST scan of THIS FILE, which is blind to comments and
    docstrings, refusing if it contains any reference to `gci_equal`,
    `gci_unequal`, `refinement_ratio`, `richardson`, `observed_order`,
    `GCI_abs`, `GCI_pct`, `grade_triple` or `triple_of`, and requiring that the
    ONLY name imported from `scripts/roache_triple.py` is `PLANT`.  Driven with
    a planted call, so the scanner is shown able to see one.

THE RUNG IS DECOUPLED BY CONSTRUCTION, and that is a cost-model property as
much as a grading one.  F1 reads ONE level.  The other two are OPTIONAL
EVIDENCE feeding REPORTED rows: a level that is capped, crashed, mispriced or
simply not run is recorded as such and CANNOT touch F1's verdict.  The exposure
this avoids was measured on T16 on 2026-08-27 -- one flat per-cell-iteration
rate under-priced its medium level by 1.667x, and on an all-or-none comparator
a single capped level would have made the whole rung ungradeable.  The
decoupling is not a licence to drop an inconvenient level: see level_state().

RULE 5 IS UNREACHABLE HERE, NOT WAIVED (VERIFICATION_CHARTER section 2f.2), and
the half of it that still fires is the half that matters: LIMB (1) -- a level
not iteratively converged is NOT A RESULT -- applies IN FULL, on EVERY level
built, as gate (1).  Section 2f.7: a no-triple family has already given up limb
(2), so limb (1) is the only convergence gate it has left and it is not
optional.

THE REFERENT is `exact_t9aR1c.py`: two independent derivations, cross-checked
against FOUR numbers registered by rung T9a that this lab did not recompute
here.  A disagreement REFUSES.

THE PLANTED-ZERO CONTROL (standing rule 3) HAS FOUR ARMS, and the third is the
point.  A floor demonstration is a claim that a number is SMALL, which is the
most dangerous claim class in this lab, because a blind reader returns small.
A plant that carries the same form the reader is already looking for proves
only that the reader is not blind TO THAT FORM.  Arm P2 therefore plants a
PERMUTATION: it SWAPS the two values at the reader's own stencil, changing no
value in the file, only their ORDER.  Any reader that is value-based but
position-blind -- one that had drifted to a fixed index, that summed or averaged
a block, or that returned a cached constant -- reads exactly the same number
before and after and is REFUSED.  A value plant cannot detect that failure
class; this one can.

NO `assert` STATEMENT IN THIS FILE (L-332).  Every refusal is sys.exit(2).
apply_gate() is the ONLY function that writes a verdict.
Exit: 0 graded, 2 REFUSAL.
"""
import argparse
import ast
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "scripts"))
import exact_t9aR1c as EX                                       # noqa: E402
from roache_triple import PLANT                                 # noqa: E402

LEVELS = ("c", "m", "f")
CASES = {lv: "W1c_%s" % lv for lv in LEVELS}
ADMISSIBLE_CLAIM_CLASSES = ("FLOOR_DEMONSTRATION", "REPORTED")
ADMISSIBLE_CEILINGS = ("PASS", "GATE REACHED")
# names whose PRESENCE would mean this file computes an order or a GCI
FORBIDDEN_NAMES = ("gci", "gci_equal", "gci_unequal", "refinement_ratio", "richardson",
                   "observed_order", "GCI_abs", "GCI_pct", "grade_triple", "triple_of",
                   "p_observed", "roache_gate")
ROACHE_MODULE = "roache_triple"
ROACHE_ALLOWED_IMPORTS = {"PLANT"}
EXIT_OK, EXIT_REFUSE = 0, 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


# ==================================================== C_NOTRIPLE: the AST guard
def scan_for_triple(src, label):
    """Returns the sorted list of FORBIDDEN references found in `src`, and the
    set of names imported from roache_triple.  AST-based, so a name that appears
    only in a comment or a docstring is INVISIBLE to it -- which is what lets
    this file explain at length why it computes no triple without tripping its
    own guard."""
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        refuse("C_NOTRIPLE: %s is not parseable (%s)" % (label, e))
    hits, roache_imports = set(), None
    for n in ast.walk(tree):
        if isinstance(n, ast.Name) and n.id in FORBIDDEN_NAMES:
            hits.add(n.id)
        elif isinstance(n, ast.Attribute) and n.attr in FORBIDDEN_NAMES:
            hits.add(n.attr)
        elif isinstance(n, ast.FunctionDef) and n.name in FORBIDDEN_NAMES:
            hits.add(n.name)
        elif isinstance(n, ast.ImportFrom) and n.module == ROACHE_MODULE:
            roache_imports = set(a.name for a in n.names)
        elif isinstance(n, ast.Import):
            for a in n.names:
                if a.name == ROACHE_MODULE:
                    roache_imports = {"<whole module>"}
    return sorted(hits), roache_imports


def no_triple_guard():
    hits, roache_imports = scan_for_triple(open(__file__).read(), os.path.basename(__file__))
    if hits:
        refuse("C_NOTRIPLE: this comparator refers to %s -- it registered NO Roache triple, so a "
               "name that computes an order or a GCI has no business in it (charter 2f.2: rule 5 "
               "is UNREACHABLE here, not waived)" % ", ".join(hits))
    if roache_imports is not None and roache_imports != ROACHE_ALLOWED_IMPORTS:
        refuse("C_NOTRIPLE: the only name this comparator may take from %s.py is %s; it takes %s"
               % (ROACHE_MODULE, sorted(ROACHE_ALLOWED_IMPORTS), sorted(roache_imports)))
    return dict(status="PASS", forbidden_names_checked=len(FORBIDDEN_NAMES),
                roache_imports=sorted(roache_imports or []))


# ============================================== C_CLASS: what a row may claim
def check_claim_classes(reg):
    seen = {}
    for rid, row in sorted(reg["rows"].items()):
        cls = row.get("claim_class")
        if cls not in ADMISSIBLE_CLAIM_CLASSES:
            refuse("C_CLASS: row %s is registered claim_class %r; this comparator admits only %s. "
                   "A row that claims a grid-convergence property must be graded through an "
                   "UNCONDITIONAL rule 5 triple gate, and this comparator has none -- so it "
                   "refuses the row rather than grading it without one."
                   % (rid, cls, " or ".join(ADMISSIBLE_CLAIM_CLASSES)))
        seen[rid] = cls
    graded = [r for r, c in seen.items() if c == "FLOOR_DEMONSTRATION"]
    if len(graded) != 1:
        refuse("C_CLASS: exactly one FLOOR_DEMONSTRATION row is registered for this rung; found %d (%s)"
               % (len(graded), ", ".join(sorted(graded)) or "none"))
    return seen, graded[0]


def load_registered(root=None):
    p = os.path.join(root or HERE, "T9aR1c_registered.json")
    if not os.path.isfile(p):
        refuse("no T9aR1c_registered.json -- the gate is not registered")
    reg = json.load(open(p))
    for key in ("rows", "wall", "cases", "graded_level", "label_ceiling", "controls"):
        if key not in reg:
            refuse("T9aR1c_registered.json states no %r" % key)
    if reg["label_ceiling"] not in ADMISSIBLE_CEILINGS:
        refuse("registered label_ceiling %r is not one of %s" % (reg["label_ceiling"], ADMISSIBLE_CEILINGS))
    if reg["graded_level"] not in LEVELS:
        refuse("registered graded_level %r is not one of %s" % (reg["graded_level"], LEVELS))
    check_claim_classes(reg)
    fl = reg["rows"]["F1"].get("floor_K")
    if not isinstance(fl, float) or not (fl > 0.0):
        refuse("row F1 registers no positive absolute floor_K: %r" % fl)
    return reg


# ================================================================ THE READERS
def case_meta(root, case):
    p = os.path.join(root, case, "CASE.txt")
    if not os.path.isfile(p):
        refuse("no CASE.txt for %s" % case)
    return dict(re.findall(r"^([A-Za-z_0-9]+)=(.*)$", open(p).read(), re.M))


def latest_time(d):
    ts = [t for t in os.listdir(d) if re.fullmatch(r"[0-9]+(\.[0-9]+)?", t) and float(t) > 0]
    return max(ts, key=float) if ts else None


def read_internal(path):
    """THE PRODUCTION READER (T and DT)."""
    if not os.path.isfile(path):
        return None
    m = re.search(r"internalField\s+nonuniform[^(]*\(\s*(.*?)\n\)", open(path).read(), re.S)
    return [float(v) for v in m.group(1).split()] if m else None


def centres(wall, cells):
    Cx, x0 = [], 0.0
    for l, n in zip(wall["layers"], cells):
        Cx += [x0 + (i + 0.5) * l["L"] / n for i in range(n)]
        x0 += l["L"]
    return Cx


def layer_of(wall, x):
    x0 = 0.0
    for i, l in enumerate(wall["layers"]):
        x0 += l["L"]
        if x < x0:
            return i
    return len(wall["layers"]) - 1


def stencil(wall, Cx, iface_index):
    """The two cells straddling interface `iface_index`, and their conductance
    weights -- THE PARENT'S READER FORM (analyse_t9a.measure_wall.iface_T,
    inherited unchanged through analyse_t9aR1b.measure)."""
    ks = [l["k"] for l in wall["layers"]]
    xi = sum(l["L"] for l in wall["layers"][:iface_index + 1])
    left = [i for i in range(len(Cx)) if Cx[i] < xi]
    right = [i for i in range(len(Cx)) if Cx[i] > xi]
    if not left or not right:
        refuse("interface %d at x=%.6g has no cell on one side" % (iface_index + 1, xi))
    iL, iR = max(left), min(right)
    wL = ks[layer_of(wall, Cx[iL])] / (xi - Cx[iL])
    wR = ks[layer_of(wall, Cx[iR])] / (Cx[iR] - xi)
    return iL, iR, wL, wR


def iface_T(T, iL, iR, wL, wR):
    return (wL * T[iL] + wR * T[iR]) / (wL + wR)


def measure(root, case, wall, cells):
    """The frozen reader.  T_i1 (GRADED at the coarsest level), T_i2 and q_hot
    (REPORTED).  C_MAP checks the DT field cell by cell against the layer map."""
    d = os.path.join(root, case)
    t = latest_time(d)
    if t is None:
        refuse("%s has no time directory beyond 0" % case)
    T = read_internal(os.path.join(d, t, "T"))
    DT = read_internal(os.path.join(d, t, "DT"))
    if T is None or DT is None:
        refuse("%s: T or DT unreadable at time %s -- a missing number is not a zero" % (case, t))
    Cx = centres(wall, cells)
    if len(T) != len(Cx):
        refuse("%s: %d cells on disk, %d from the registered layer counts" % (case, len(T), len(Cx)))
    ks = [l["k"] for l in wall["layers"]]
    for i, x in enumerate(Cx):
        want = ks[layer_of(wall, x)]
        if abs(DT[i] - want) > 1e-9 * want:
            refuse("%s: cell %d at x=%.6g carries DT=%g, the registered layer map says %g (C_MAP)"
                   % (case, i, x, DT[i], want))
    i1L, i1R, w1L, w1R = stencil(wall, Cx, 0)
    i2L, i2R, w2L, w2R = stencil(wall, Cx, 1)
    return dict(time=t, n=len(T), T=T, Cx=Cx,
                T_i1=iface_T(T, i1L, i1R, w1L, w1R), i1L=i1L, i1R=i1R, w1L=w1L, w1R=w1R,
                T_i2=iface_T(T, i2L, i2R, w2L, w2R), i2L=i2L, i2R=i2R,
                q_hot=ks[0] * (wall["T_hot"] - T[0]) / Cx[0],
                far_cell=len(T) - 1)


def level_state(root, case):
    """WHAT STATE IS THIS LEVEL IN?  Returns one of DONE / RAN_NOT_COMPLETE /
    NOT RUN, and REFUSES the one state that must never be reported quietly.

    THIS RUNG IS DECOUPLED BY CONSTRUCTION.  The graded row F1 reads ONE level.
    A rung whose comparator refuses unless every level completed makes a
    mispriced, capped or crashed level able to destroy a verdict that never
    depended on it -- the exposure measured on T16 today, where a flat
    per-cell-iteration rate under-priced a level 1.667x and the whole rung
    would have become ungradeable on an all-or-none coupling.  So: the GRADED
    level must be DONE, and the other levels are OPTIONAL EVIDENCE whose
    absence is REPORTED, never fatal.

    The decoupling is not a licence to drop an inconvenient level, and the
    difference is enforced rather than promised:

      * every level whose DONE marker exists IS READ.  The comparator cannot be
        told to skip one.
      * a level with a STATUS file and no DONE marker is recorded
        RAN_NOT_COMPLETE with mark_done's own reasons -- it ran, it did not
        complete, and that appears in the record instead of vanishing.
      * a level holding a numeric time directory but NO STATUS file is a
        REFUSAL: a solver ran there and its exit status was never recorded, and
        an absent STATUS is never inferred from fields on disk (K0d L1).
    """
    d = os.path.join(root, case)
    has_done = os.path.isfile(os.path.join(root, "DONE.%s" % case))
    has_status = os.path.isfile(os.path.join(root, "STATUS.%s" % case))
    has_time = os.path.isdir(d) and any(
        re.fullmatch(r"[0-9]+(\.[0-9]+)?", t) and float(t) > 0 for t in os.listdir(d))
    if has_time and not has_status:
        refuse("%s holds a written time directory but NO STATUS.%s -- a solver ran there and its "
               "exit status was never recorded. An absent STATUS is refused, never inferred from "
               "fields on disk (K0d L1). A level cannot be dropped from this record by removing "
               "its markers." % (case, case))
    if has_done:
        return "DONE"
    if has_status:
        return "RAN_NOT_COMPLETE"
    return "NOT RUN"


def converged(root, case, floor):
    """GATE (1) -- standing rule 5's limb (1), which is UNAFFECTED by this
    rung's no-triple election (charter 2f.2, 2f.7).  End line present, and the
    last two written checkpoints agree in T to `floor` K (the parent's
    checkpoint form, L-140/L-141)."""
    d = os.path.join(root, case)
    log = os.path.join(d, "log.solve")
    if not os.path.isfile(log) or not re.search(r"^End\s*$", open(log, errors="replace").read(), re.M):
        return False, None, "no End line"
    ts = sorted((t for t in os.listdir(d) if re.fullmatch(r"[0-9]+(\.[0-9]+)?", t) and float(t) > 0),
                key=float)
    if len(ts) < 2:
        return False, None, "fewer than two written checkpoints, so the plateau test cannot be evaluated"
    a = read_internal(os.path.join(d, ts[-2], "T"))
    b = read_internal(os.path.join(d, ts[-1], "T"))
    if a is None or b is None:
        return False, None, "checkpoint T unreadable"
    mv = max(abs(x - y) for x, y in zip(a, b))
    return (mv <= floor), mv, ("" if mv <= floor else
                               "T moved %.3e K between the last two checkpoints, above the floor %.1e"
                               % (mv, floor))


# ================================ rule 3: THE FOUR-ARM PLANTED-ZERO CONTROL
def _plant_lines(p):
    lines = open(p).read().splitlines(True)
    start = None
    for i, ln in enumerate(lines):
        if "internalField" in ln and "nonuniform" in ln:
            for j in range(i, min(i + 5, len(lines))):
                if lines[j].strip() == "(":
                    start = j + 1
                    break
            break
    if start is None:
        refuse("planted-zero control: internalField could not be located STRUCTURALLY")
    return lines, start


def planted_zero_control(root, case, wall, cells, visibility_floor_K, far_cell_override=None):
    """FOUR ARMS.  Copies the case into scratch first and never writes into the
    run tree.

      N  negative   : identical bytes read twice -> must be bit-identical.
      P1 value      : the registered PLANT into the reader's own stencil cell,
                      on a measured ladder; the reader must SEE it, and (units
                      match, K into K) must move by at least 0.1 x the plant.
      P2 permutation: the two stencil values are SWAPPED.  No value in the file
                      changes -- only their order.  A reader that is value-based
                      but position-blind reads the same number and is REFUSED.
                      This is the form the reader was NOT written for.
      P3 specificity: the registered PLANT into a far cell in layer 3, outside
                      the reader's stencil.  T_i1 must move by EXACTLY zero; a
                      reader that has become a whole-field statistic is REFUSED.
    """
    tmp = tempfile.mkdtemp(prefix="t9ar1c_pz_")
    try:
        dst = os.path.join(tmp, case)
        shutil.copytree(os.path.join(root, case), dst, symlinks=True)
        if os.path.realpath(dst).startswith(os.path.realpath(os.path.join(root, case))):
            refuse("planted-zero control: the scratch copy resolved INSIDE the case tree")
        base = measure(tmp, case, wall, cells)
        again = measure(tmp, case, wall, cells)
        if base["T_i1"] != again["T_i1"]:
            refuse("planted-zero control ARM N FAILED: two reads of identical bytes differ by %.17g "
                   "-- the reader is NOISY" % abs(base["T_i1"] - again["T_i1"]))
        p = os.path.join(dst, base["time"], "T")
        orig = open(p).read()
        iL, iR = base["i1L"], base["i1R"]
        far = base["far_cell"] if far_cell_override is None else far_cell_override
        out = {}

        # ---- ARM P1: the registered value plant, on a measured ladder --------
        lines, start = _plant_lines(p)
        before = float(lines[start + iL].strip())
        seen, floor = {}, None
        for mag in (1.0, 1e-1, 1e-2, PLANT, 1e-4, 1e-5, 1e-6, 1e-7):
            lines[start + iL] = "%.17g\n" % (before + mag)
            open(p, "w").write("".join(lines))
            d = abs(measure(tmp, case, wall, cells)["T_i1"] - base["T_i1"])
            seen[mag] = d
            if d > 0.0:
                floor = mag
        open(p, "w").write(orig)
        if floor is None:
            refuse("planted-zero control ARM P1 FAILED: no plant magnitude down to 1e-7 K moved the "
                   "read -- the reader is BLIND")
        if seen[PLANT] < 0.1 * PLANT:
            refuse("planted-zero control ARM P1: the registered plant %.6g K moved T_i1 by only %.6g K "
                   "(< 0.1 x plant), while plant and read carry the SAME UNITS" % (PLANT, seen[PLANT]))
        out["P1_value"] = dict(status="PASS", arm="value plant at the reader's own stencil cell",
                               plant_K=PLANT, cell=iL, recovered_K=seen[PLANT],
                               demonstrated_detection_floor_K=floor,
                               ladder={"%g" % k: v for k, v in seen.items()})
        print("planted-zero P1 (value)       PASS: plant %.6g K in cell %d, T_i1 moved %.6g K, floor %.1g"
              % (PLANT, iL, seen[PLANT], floor))

        # ---- ARM P2: THE PERMUTATION PLANT -- order changes, values do not ---
        lines, start = _plant_lines(p)
        vL = float(lines[start + iL].strip())
        vR = float(lines[start + iR].strip())
        pred = ((base["w1L"] * vR + base["w1R"] * vL) / (base["w1L"] + base["w1R"])) - base["T_i1"]
        if abs(pred) < visibility_floor_K:
            refuse("planted-zero control ARM P2 COULD NOT BE ARMED: swapping the two stencil values "
                   "would move T_i1 by only %.3e K, below the registered visibility floor %.1e K. An "
                   "unarmable control is a REFUSAL, never a pass." % (abs(pred), visibility_floor_K))
        lines[start + iL], lines[start + iR] = lines[start + iR], lines[start + iL]
        open(p, "w").write("".join(lines))
        got = measure(tmp, case, wall, cells)["T_i1"]
        open(p, "w").write(orig)
        moved = got - base["T_i1"]
        if moved == 0.0:
            refuse("planted-zero control ARM P2 FAILED: the two stencil values were SWAPPED -- no "
                   "value in the file changed, only their ORDER -- and T_i1 did not move. The reader "
                   "is ORDER-BLIND, and a value plant cannot detect that.")
        out["P2_permutation"] = dict(
            status="PASS", arm="permutation plant: stencil values swapped, no value changed",
            cells_swapped=[iL, iR], moved_K=moved,
            predicted_from_the_readers_own_weights_K=pred,
            identity_agreement_K=abs(moved - pred),
            identity_note="the predicted/measured agreement is an IDENTITY (charter 2a): the "
                          "prediction uses the reader's own weights. It is REPORTED, never gated. "
                          "The GATE is that the move is non-zero.")
        print("planted-zero P2 (permutation) PASS: cells %d<->%d swapped, T_i1 moved %.6g K "
              "(identity check vs the reader's own weights: %.2e K)" % (iL, iR, moved, abs(moved - pred)))

        # ---- ARM P3: specificity -- a far plant must be INVISIBLE ------------
        lines, start = _plant_lines(p)
        bfar = float(lines[start + far].strip())
        lines[start + far] = "%.17g\n" % (bfar + PLANT)
        open(p, "w").write("".join(lines))
        gotf = measure(tmp, case, wall, cells)["T_i1"]
        open(p, "w").write(orig)
        dfar = abs(gotf - base["T_i1"])
        if dfar != 0.0:
            refuse("planted-zero control ARM P3 FAILED: a plant of %.6g K into cell %d, which is "
                   "OUTSIDE the reader's two-cell stencil (%d, %d), moved T_i1 by %.3e K. The reader "
                   "is not the local reader it is registered as." % (PLANT, far, iL, iR, dfar))
        out["P3_specificity"] = dict(status="PASS", arm="far plant outside the stencil must be invisible",
                                     plant_K=PLANT, cell=far, moved_K=dfar, stencil=[iL, iR])
        print("planted-zero P3 (specificity) PASS: plant %.6g K in cell %d (outside the stencil %d,%d), "
              "T_i1 moved %.1e K" % (PLANT, far, iL, iR, dfar))
        out["N_negative"] = dict(status="PASS", arm="two reads of identical bytes", delta_K=0.0)
        return out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ========================================================== THE GATE, one way
def apply_gate(dev_K, floor_K, gate1_ok, gate1_why, ceiling):
    """THE ONLY FUNCTION IN THIS FILE THAT WRITES A VERDICT.

    Order, and it is one-way:
      (1) rule 5's limb (1) -- any level not iteratively converged -> NOT A RESULT;
      (2) the FLOOR DEMONSTRATION -- |value - exact| <= floor_K -> PASS else GATE FAIL;
      (3) the registered LABEL CEILING is applied: where the registration caps
          the limb at GATE REACHED (charter 2f.3's CONTINUUM class), a band PASS
          is reported as GATE REACHED.  The ceiling can only WEAKEN a verdict.

    There is no branch (2) triple gate because there is no triple.  Nothing in
    this function can turn a NOT A RESULT into a PASS."""
    band_verdict = "PASS" if dev_K <= floor_K else "GATE FAIL"
    if not gate1_ok:
        return "NOT A RESULT", band_verdict, "gate (1), standing rule 5 limb (1): " + gate1_why
    if band_verdict == "PASS" and ceiling == "GATE REACHED":
        return "GATE REACHED", band_verdict, ("registered label ceiling GATE REACHED "
                                              "(VERIFICATION_CHARTER 2f.3): PASS is unavailable to this limb")
    return band_verdict, band_verdict, ""


# ================================================================== the grade
def grade(root, json_out, reg, quiet_ref=False):
    guard = no_triple_guard()
    classes, graded_row = check_claim_classes(reg)
    wall = reg["wall"]
    gl = reg["graded_level"]
    states = {lv: level_state(root, CASES[lv]) for lv in LEVELS}
    if states[gl] != "DONE":
        refuse("the GRADED level %s is %s -- F1 reads that level and no other, so without its DONE "
               "marker there is nothing to grade; mark_done_t9aR1c.py rules" % (CASES[gl], states[gl]))
    read = [lv for lv in LEVELS if states[lv] == "DONE"]
    for lv in LEVELS:
        if states[lv] != "DONE":
            print("  level %s (%s): %s -- REPORTED, and it does not touch F1 (this rung is decoupled "
                  "by construction; the graded row reads %s alone)" % (lv, CASES[lv], states[lv], CASES[gl]))
    ref = EX.solve(wall["layers"], wall["T_hot"], wall["T_cold"], quiet=quiet_ref)

    metas = {lv: case_meta(root, CASES[lv]) for lv in read}
    cells = {lv: [int(x) for x in metas[lv]["cells_per_layer"].split(",")] for lv in read}
    for lv in read:
        if cells[lv] != reg["cases"][CASES[lv]]["cells_per_layer"]:
            refuse("%s cells_per_layer %r != registered %r"
                   % (CASES[lv], cells[lv], reg["cases"][CASES[lv]]["cells_per_layer"]))
        if metas[lv].get("laplacianSchemes") != reg["controls"]["C_SCHEME"]["required_line"]:
            refuse("%s CASE.txt records laplacianSchemes=%r, the registration requires %r (C_SCHEME)"
                   % (CASES[lv], metas[lv].get("laplacianSchemes"),
                      reg["controls"]["C_SCHEME"]["required_line"]))
        sch = open(os.path.join(root, CASES[lv], "system", "fvSchemes")).read()
        if reg["controls"]["C_SCHEME"]["required_line"] not in sch:
            refuse("%s system/fvSchemes on disk does not carry the registered scheme %r (C_SCHEME)"
                   % (CASES[lv], reg["controls"]["C_SCHEME"]["required_line"]))

    # ---- gate (1): standing rule 5's limb (1) (charter 2f.2, 2f.7) --------
    # BINDING on the level F1 reads.  EVALUATED AND REPORTED on the others,
    # where it flags that level's REPORTED rows and touches no verdict -- a
    # level F1 does not read cannot decide F1.
    g1 = {}
    for lv in read:
        o, mv, w = converged(root, CASES[lv], reg["controls"]["C_CONV"]["floor"])
        g1[lv] = dict(ok=o, checkpoint_move_K=mv, why=w,
                      binding=(lv == gl), role=("gate (1) for F1" if lv == gl else "REPORTED only"))
        print("  level %s: checkpoint-converged %s (move %s K) [%s]"
              % (lv, o, ("%.3e" % mv) if mv is not None else "n/a", g1[lv]["role"]))
    gate1_ok = g1[gl]["ok"]
    why = ["%s: %s" % (CASES[gl], g1[gl]["why"])] if not gate1_ok else []

    ms = {lv: measure(root, CASES[lv], wall, cells[lv]) for lv in read}
    pz = planted_zero_control(root, CASES[gl], wall, cells[gl],
                              reg["controls"]["C_PZ"]["visibility_floor_K"])

    # ---- F1, THE ONE GRADED ROW: one number, one level, one threshold ----
    F = reg["rows"]["F1"]
    dev = abs(ms[gl]["T_i1"] - ref["T_i1"])
    verdict, band_verdict, note = apply_gate(dev, F["floor_K"], gate1_ok, "; ".join(why),
                                             reg["label_ceiling"])
    print("F1 [%s] FLOOR DEMONSTRATION at the COARSEST level %s: T_i1 = %.12f K, exact = %.12f K, "
          "|deviation| = %.3e K against the registered floor X = %.3e K -> %s%s"
          % (F["claim_class"], CASES[gl], ms[gl]["T_i1"], ref["T_i1"], dev, F["floor_K"], verdict,
             (" [" + note + "]") if note else ""))

    # ---- REPORTED rows: no verdict is written for any of these ------------
    # A level that is not DONE reads NOT MEASURED here.  L-342's rule applies:
    # NOT MEASURED is reported, never silently rendered as a zero.
    NM = "NOT MEASURED"

    def per_level(fn):
        return {lv: (fn(lv) if lv in read else NM) for lv in LEVELS}
    n1 = per_level(lambda lv: abs(ms[lv]["T_i1"] - ref["T_i1"]))
    n3 = per_level(lambda lv: (ms[lv]["q_hot"] - ref["q"]) / ref["q"])
    n4 = per_level(lambda lv: abs(ms[lv]["T_i2"] - ref["T_i2"]))
    vals = [ms[lv]["T_i1"] for lv in read]
    spread = (max(vals) - min(vals)) if len(read) > 1 else None

    def fmtrow(d, f):
        return ", ".join(("%s %s" % (lv, d[lv])) if d[lv] == NM else ("%s " + f) % (lv, d[lv])
                         for lv in LEVELS)
    print("N1 (REPORTED) |T_i1 - exact| per level: " + fmtrow(n1, "%.3e K"))
    print("N2 (REPORTED) mesh-family SPREAD max-min of T_i1 over the %d level(s) READ (%s): %s. "
          "This is a BOUND on observed variation over the meshes actually built "
          "(VERIFICATION_CHARTER 2f.6). It is NOT an error estimate, NOT extrapolated, and it is "
          "NOT a GCI and NOT an observed order."
          % (len(read), ",".join(CASES[lv] for lv in read),
             ("%.3e K" % spread) if spread is not None else
             "NOT MEASURED -- a spread needs at least two levels and %d was read" % len(read)))
    print("N3 (REPORTED) q_hot relative deviation: " + fmtrow(n3, "%+.3e"))
    print("N4 (REPORTED) |T_i2 - exact| per level (the interface F1 does NOT read): "
          + fmtrow(n4, "%.3e K"))

    out = dict(
        rung="T9a-R1c", parent="T9a-R1b (W1b)", predecessor_ruling="VERIFICATION_CHARTER 2g (v1.16); label ceiling ruled by 2h (v1.17)",
        claim="the discretisation error in T_i1 is below X at %d cells (%s), and below X at each "
              "further level run as reported in N1" % (ms[gl]["n"], CASES[gl]),
        claim_is_not="(a) NOT grid convergence: no observed order, no GCI, no Richardson "
                     "extrapolate and no Roache triple is computed anywhere in this comparator. "
                     "(b) NOT 'the solution is correct to X' -- that is a continuum claim and "
                     "charter 2f.3 would cap it. (c) NOT 'the answer does not depend on the mesh': "
                     "charter 2h.4(5) NARROWED 2g.3's own phrase, because this instrument "
                     "establishes the error at the meshes MEASURED and nothing about finer ones. "
                     "The claim is bounded by the meshes actually run and extrapolated to none.",
        charter_2h_conditions="PASS is available to this limb under VERIFICATION_CHARTER 2h "
                              "(v1.17) only where all five of 2h.4 hold; they are declared in "
                              "docs/campaigns/T-family/T9aR1c_PREREGISTRATION.md section 3a "
                              "BEFORE compute, and conditions (4) and (5) are wording conditions "
                              "that no machine check in this file can discharge -- the AST guard "
                              "proves the ABSENCE OF A TRIPLE, not the wording of the claim.",
        rule5_status="limb (2) UNREACHABLE, NOT WAIVED (charter 2f.2); limb (1) applies IN FULL as "
                     "gate (1), BINDING on the graded level (charter 2f.7, 2h.4(2))",
        label_ceiling=reg["label_ceiling"], graded_level=CASES[gl],
        decoupling=dict(
            levels_read=[CASES[lv] for lv in read], level_states={CASES[lv]: states[lv] for lv in LEVELS},
            rule="F1 reads the graded level ALONE. A level that is not DONE is REPORTED as such and "
                 "cannot touch F1's verdict; there is no all-or-none coupling for a capped, crashed "
                 "or mispriced level to destroy (the exposure measured on T16, 2026-08-27). A level "
                 "holding a written time directory with no STATUS file is still a REFUSAL, so a "
                 "level cannot be dropped from this record by removing its markers."),
        referent=dict(T_i1=ref["T_i1"], T_i2=ref["T_i2"], q=ref["q"],
                      route_agreement_rel=ref["route_agreement_rel"], cross_check=ref["cross_check"]),
        rows=[dict(row="F1", claim_class=F["claim_class"], quantity=F["quantity"], level=CASES[gl],
                   value_K=ms[gl]["T_i1"], reference_K=ref["T_i1"], deviation_K=dev,
                   floor_K=F["floor_K"], band_verdict=band_verdict, verdict=verdict, note=note)],
        reported_rows=dict(
            N1_deviation_per_level_K=n1,
            N2_mesh_family_spread_K=dict(value=spread, levels_read=[CASES[lv] for lv in read],
                                         kind="BOUND on observed variation over the meshes actually "
                                              "READ (charter 2f.6)",
                                         not_a="GCI or observed order; not extrapolated"),
            N3_q_hot_relative_deviation=n3,
            N4_T_i2_deviation_K=n4),
        cells={lv: ms[lv]["n"] for lv in read},
        gate1=dict(ok=gate1_ok, why="; ".join(why), per_level=g1,
                   rule="standing rule 5 limb (1), which is UNAFFECTED by the no-triple election "
                        "(charter 2f.2, 2f.7). BINDING on the graded level: F1 is NOT A RESULT if "
                        "%s fails it. EVALUATED AND REPORTED on the other levels, where it flags "
                        "their REPORTED rows and touches no verdict." % CASES[gl]),
        controls=dict(C_NOTRIPLE=guard, C_CLASS=classes, C_PZ=pz,
                      C_SCHEME=reg["controls"]["C_SCHEME"]["required_line"],
                      C_MAP="every cell's DT checked against the registered layer map inside measure()",
                      C_REF=ref["cross_check"]))
    json.dump(out, open(json_out, "w"), indent=2)
    print("wrote %s" % json_out)
    return EXIT_OK


# ================================================================== selftest
def _forge(root, lv, cells, wall, offset_K=0.0, move_K=0.0, scheme=None, dt_bad=False,
           equal_stencil=False, done=True, status=True):
    """A forged case carrying the ANALYTIC piecewise-linear T at cell centres,
    plus a constant offset.  `offset_K` may be a float (all levels) or a dict
    keyed by level."""
    case = CASES[lv]
    d = os.path.join(root, case)
    os.makedirs(os.path.join(d, "system"), exist_ok=True)
    os.makedirs(os.path.join(d, "0"), exist_ok=True)
    open(os.path.join(d, "0", "T"), "w").write("x")
    line = "Gauss harmonic corrected" if scheme is None else scheme
    open(os.path.join(d, "system", "fvSchemes"), "w").write(
        "laplacianSchemes { default %s; }\n" % line)
    open(os.path.join(d, "CASE.txt"), "w").write(
        "case=%s\ncells_per_layer=%s\nlaplacianSchemes=%s\n" % (case, ",".join(map(str, cells)), line))
    r = EX.solve(wall["layers"], wall["T_hot"], wall["T_cold"], quiet=True)
    q = r["q"]
    ks = [l["k"] for l in wall["layers"]]
    Cx = centres(wall, cells)
    off = offset_K[lv] if isinstance(offset_K, dict) else offset_K
    T, DT = [], []
    for x in Cx:
        li = layer_of(wall, x)
        x0 = sum(l["L"] for l in wall["layers"][:li])
        Tface = wall["T_hot"] - q * sum(l["L"] / l["k"] for l in wall["layers"][:li])
        T.append(Tface - q * (x - x0) / ks[li] + off)
        DT.append(ks[li])
    if dt_bad:
        DT[0] = DT[0] * 1.5
    if equal_stencil:
        iL, iR, _, _ = stencil(wall, Cx, 0)
        T[iR] = T[iL]

    def fld(name, vals):
        return ("FoamFile{version 2.0; format ascii; class volScalarField; object %s;}\n"
                "dimensions [0 0 0 1 0 0 0];\ninternalField   nonuniform List<scalar> \n%d\n(\n%s\n)\n;\n"
                "boundaryField{}\n" % (name, len(vals), "\n".join("%.17g" % v for v in vals)))
    for t, extra in (("900", move_K), ("1000", 0.0)):
        os.makedirs(os.path.join(d, t), exist_ok=True)
        open(os.path.join(d, t, "T"), "w").write(fld("T", [v + extra for v in T]))
        open(os.path.join(d, t, "DT"), "w").write(fld("DT", DT))
    open(os.path.join(d, "log.solve"), "w").write("ExecutionTime = 1 s\nEnd\n")
    # STATUS accompanies every real run (mark_done REFUSES without one and so
    # cannot write DONE), so the forge carries the same invariant.
    if status:
        open(os.path.join(root, "STATUS.%s" % case), "w").write("case=%s\nrc=0\n" % case)
    if done:
        open(os.path.join(root, "DONE.%s" % case), "w").write("done\n")


def selftest():
    fails = []
    reg = load_registered()
    wall = reg["wall"]
    X = reg["rows"]["F1"]["floor_K"]
    cells = {lv: reg["cases"][CASES[lv]]["cells_per_layer"] for lv in LEVELS}
    print("analyse_t9aR1c selftest (floor X = %.3e K, graded level %s, label ceiling %s):"
          % (X, CASES[reg["graded_level"]], reg["label_ceiling"]))

    def drive(label, fn):
        fired, code, res = False, None, None
        try:
            code, res = fn()
        except SystemExit as e:
            fired, code = True, e.code
        return fired, code, res

    def run_forged(**kw):
        tmp = tempfile.mkdtemp(prefix="t9ar1c_forge_")
        try:
            for lv in LEVELS:
                _forge(tmp, lv, cells[lv], wall, **kw)
            out = os.path.join(tmp, "gate.json")
            code = None
            try:
                code = grade(tmp, out, reg, quiet_ref=True)
            except SystemExit as e:
                code = e.code
            return code, (json.load(open(out)) if os.path.isfile(out) else None)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def check(label, ok):
        print("  [%s] %s" % ("ok " if ok else "FAIL", label))
        if not ok:
            fails.append(label)

    # ---- 1. the no-triple AST guard, with a PLANTED control ---------------
    hits, imports = scan_for_triple(open(__file__).read(), "self")
    planted = "def f(a, b, c, r, p):\n    return gci_unequal(a, b, c, r, p)\n"
    hits2, _ = scan_for_triple(planted, "planted")
    check("C_NOTRIPLE: this file refers to 0 forbidden order/GCI names; the PLANTED control "
          "`gci_unequal(...)` is seen (%d hit) -- the scanner is not blind" % len(hits2),
          hits == [] and hits2 == ["gci_unequal"])
    check("C_NOTRIPLE: the only name imported from roache_triple.py is ['PLANT'] (got %r)" % (imports,),
          imports == ROACHE_ALLOWED_IMPORTS)
    hits3, _ = scan_for_triple("# gci_unequal(1,2,3)\n'''richardson observed_order'''\nx = 1\n", "comment")
    check("C_NOTRIPLE: the scanner is AST-based -- the same names in a COMMENT and a DOCSTRING are "
          "invisible to it (0 hits)", hits3 == [])

    # ---- 2. C_CLASS: a convergence-claiming row is REFUSED ----------------
    for cls, want_refuse in (("ROACHE_TRIPLE", True), ("GRID_CONVERGENCE", True),
                             ("REPORTED", True), ("FLOOR_DEMONSTRATION", False)):
        bad = json.loads(json.dumps(reg))
        bad["rows"]["F1"]["claim_class"] = cls
        fired, code, _ = drive(cls, lambda: (check_claim_classes(bad), None))
        ok = (fired and code == EXIT_REFUSE) if want_refuse else (not fired)
        check("C_CLASS: row F1 registered claim_class %-20r -> %s"
              % (cls, "REFUSE" if want_refuse else "admitted"), ok)
    bad = json.loads(json.dumps(reg))
    bad["rows"]["F2_planted"] = dict(reg["rows"]["F1"])
    fired, code, _ = drive("two", lambda: (check_claim_classes(bad), None))
    check("C_CLASS: a SECOND FLOOR_DEMONSTRATION row planted -> REFUSE (exactly one graded row)",
          fired and code == EXIT_REFUSE)

    # ---- 3. the registration itself --------------------------------------
    tmpj = tempfile.mkdtemp(prefix="t9ar1c_reg_")
    try:
        bad = json.loads(json.dumps(reg))
        bad["label_ceiling"] = "VALIDATED"
        json.dump(bad, open(os.path.join(tmpj, "T9aR1c_registered.json"), "w"))
        fired, code, _ = drive("ceiling", lambda: (load_registered(tmpj), None))
        check("registered label_ceiling mutated to 'VALIDATED' -> REFUSE (the ceiling is one of "
              "PASS / GATE REACHED and nothing else)", fired and code == EXIT_REFUSE)
        bad = json.loads(json.dumps(reg))
        bad["rows"]["F1"].pop("floor_K")
        json.dump(bad, open(os.path.join(tmpj, "T9aR1c_registered.json"), "w"))
        fired, code, _ = drive("floor", lambda: (load_registered(tmpj), None))
        check("registered floor_K removed -> REFUSE (a floor demonstration with no floor is not a gate)",
              fired and code == EXIT_REFUSE)
    finally:
        shutil.rmtree(tmpj, ignore_errors=True)

    # ---- 4. the referent cross-check --------------------------------------
    fired, code, _ = drive("xcheck", lambda: (EX.solve(
        [dict(L=0.05, k=0.8 * 1.0001), dict(L=0.1, k=0.04), dict(L=0.02, k=16.0)],
        350.0, 300.0, quiet=True), None))
    check("C_REF: layer-1 k planted 1e-4 wrong -> the T9a cross-check REFUSES the referent",
          fired and code == EXIT_REFUSE)

    # ---- 5. THE FLOOR GATE, DRIVEN BOTH WAYS AND AT ITS EDGES -------------
    # apply_gate is driven directly on numbers, then end-to-end on real bytes.
    for label, dev, g1, ceiling, want in (
            ("dev 0            -> PASS", 0.0, True, "PASS", "PASS"),
            ("dev 0.99 X       -> PASS", 0.99 * X, True, "PASS", "PASS"),
            ("dev 1.00 X       -> PASS (the floor is inclusive, as registered)", X, True, "PASS", "PASS"),
            ("dev 1.01 X       -> GATE FAIL", 1.01 * X, True, "PASS", "GATE FAIL"),
            ("dev 2.00 X       -> GATE FAIL", 2.0 * X, True, "PASS", "GATE FAIL"),
            ("dev 5.43e-03 (the PARENT's linear scheme at this level) -> GATE FAIL",
             5.43e-03, True, "PASS", "GATE FAIL"),
            ("dev 0, gate (1) failed -> NOT A RESULT (rule 5 limb (1), one-way)",
             0.0, False, "PASS", "NOT A RESULT"),
            ("dev 2 X, gate (1) failed -> NOT A RESULT (never a GATE FAIL upgrade either)",
             2.0 * X, False, "PASS", "NOT A RESULT"),
            ("dev 0, ceiling GATE REACHED -> GATE REACHED (the ceiling only WEAKENS)",
             0.0, True, "GATE REACHED", "GATE REACHED"),
            ("dev 2 X, ceiling GATE REACHED -> GATE FAIL (a ceiling never rescues a fail)",
             2.0 * X, True, "GATE REACHED", "GATE FAIL")):
        v, bv, note = apply_gate(dev, X, g1, "forced", ceiling)
        check("FLOOR GATE: %-70s got %s" % (label, v), v == want)

    # ---- 6. end-to-end on forged bytes, PASSING and FAILING ---------------
    code, res = run_forged()
    row = res["rows"][0] if res else None
    ok = (code == 0 and row and row["verdict"] == reg["label_ceiling"] and row["deviation_K"] < X
          and all(v["status"] == "PASS" for v in res["controls"]["C_PZ"].values()))
    check("VALUE CONTROL end-to-end: the exact piecewise-linear field on all three levels grades F1 "
          "%s at |dev| = %s K; all four planted-zero arms PASS"
          % (reg["label_ceiling"], ("%.2e" % row["deviation_K"]) if row else "?"), ok)

    code, res = run_forged(offset_K={"c": 2.0 * X, "m": 0.0, "f": 0.0})
    row = res["rows"][0] if res else None
    ok = (code == 0 and row and row["verdict"] == "GATE FAIL")
    check("GATE-FAIL end-to-end on real bytes: a %.1e K offset planted at the COARSEST level only "
          "-> F1 GATE FAIL (a gate never shown to fail is not an instrument)" % (2.0 * X), ok)

    code, res = run_forged(offset_K={"c": 0.0, "m": 2.0 * X, "f": 0.0})
    row = res["rows"][0] if res else None
    ok = (code == 0 and row and row["verdict"] == reg["label_ceiling"]
          and res["reported_rows"]["N1_deviation_per_level_K"]["m"] > X)
    check("SCOPE: the same offset planted at the MEDIUM level leaves F1 %s and appears only in the "
          "REPORTED row N1 -- F1 grades the coarsest level and nothing else" % reg["label_ceiling"], ok)

    code, res = run_forged(move_K=1e-6)
    row = res["rows"][0] if res else None
    ok = (code == 0 and row and row["verdict"] == "NOT A RESULT" and not res["gate1"]["ok"])
    check("gate (1) end-to-end: checkpoints move 1e-6 K > the 1e-9 K floor -> F1 NOT A RESULT "
          "(rule 5 limb (1) fires on a no-triple registration, charter 2f.7)", ok)

    # ---- 6b. DECOUPLING, driven four ways --------------------------------
    def run_levels(spec):
        """spec: {level: kwargs or None (level not run at all)}"""
        tmp = tempfile.mkdtemp(prefix="t9ar1c_dec_")
        try:
            for lv, kw in spec.items():
                if kw is not None:
                    _forge(tmp, lv, cells[lv], wall, **kw)
            out = os.path.join(tmp, "gate.json")
            code = None
            try:
                code = grade(tmp, out, reg, quiet_ref=True)
            except SystemExit as e:
                code = e.code
            return code, (json.load(open(out)) if os.path.isfile(out) else None)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    code, res = run_levels({"c": {}, "m": None, "f": None})
    row = res["rows"][0] if res else None
    ok = (code == 0 and row and row["verdict"] == reg["label_ceiling"]
          and res["decoupling"]["level_states"]["W1c_m"] == "NOT RUN"
          and res["reported_rows"]["N1_deviation_per_level_K"]["m"] == "NOT MEASURED"
          and res["reported_rows"]["N2_mesh_family_spread_K"]["value"] is None)
    check("DECOUPLING: ONLY the coarsest level run -- m and f absent entirely -> F1 still grades %s; "
          "N1[m] reads NOT MEASURED and the spread N2 is NOT MEASURED (a mispriced, capped or "
          "crashed level cannot destroy this verdict: the T16 exposure is absent by construction)"
          % reg["label_ceiling"], ok)

    code, res = run_levels({"c": None, "m": {}, "f": {}})
    check("DECOUPLING: the GRADED level absent while m and f are DONE -> REFUSE (exit %s) -- the one "
          "level F1 reads is the one level that is mandatory" % code, code == EXIT_REFUSE)

    code, res = run_levels({"c": {}, "m": {}, "f": dict(done=False)})
    row = res["rows"][0] if res else None
    ok = (code == 0 and row and row["verdict"] == reg["label_ceiling"]
          and res["decoupling"]["level_states"]["W1c_f"] == "RAN_NOT_COMPLETE"
          and res["reported_rows"]["N1_deviation_per_level_K"]["f"] == "NOT MEASURED")
    check("DECOUPLING: level f has a STATUS file and NO DONE marker -> recorded RAN_NOT_COMPLETE and "
          "REPORTED; F1 still grades %s. It ran, it did not complete, and that appears in the record "
          "instead of vanishing" % reg["label_ceiling"], ok)

    code, res = run_levels({"c": {}, "m": {}, "f": dict(done=False, status=False)})
    check("ANTI-CHERRY-PICK: level f holds a written time directory and NO STATUS file -> REFUSE "
          "(exit %s). A level cannot be dropped from this record by removing its markers; an absent "
          "STATUS is refused, never inferred from fields on disk (K0d L1)" % code, code == EXIT_REFUSE)

    code, res = run_levels({"c": {}, "m": {}, "f": dict(move_K=1e-6)})
    row = res["rows"][0] if res else None
    ok = (code == 0 and row and row["verdict"] == reg["label_ceiling"]
          and res["gate1"]["ok"] and res["gate1"]["per_level"]["f"]["ok"] is False
          and res["gate1"]["per_level"]["f"]["binding"] is False)
    check("DECOUPLING: gate (1) BROKEN AT LEVEL f ONLY -> reported against f as non-binding, and F1 "
          "still grades %s on the level it actually reads. A level F1 does not read cannot decide F1"
          % reg["label_ceiling"], ok)

    code, res = run_forged(scheme="Gauss linear corrected")
    check("C_SCHEME: cases built with the PARENT's linear scheme -> REFUSE (exit %s)" % code,
          code == EXIT_REFUSE)

    code, res = run_forged(dt_bad=True)
    check("C_MAP: one cell's DT planted 1.5x the registered layer conductivity -> REFUSE (exit %s)" % code,
          code == EXIT_REFUSE)

    code, res = run_forged(equal_stencil=True)
    check("C_PZ ARM P2 UNARMABLE: the two stencil values forced EQUAL, so a swap cannot move the read "
          "-> REFUSE (an unarmable control is a refusal, never a pass) (exit %s)" % code,
          code == EXIT_REFUSE)

    # ---- 7. the planted-zero arms driven to REFUSE ------------------------
    tmp = tempfile.mkdtemp(prefix="t9ar1c_pz_drive_")
    try:
        gl = reg["graded_level"]
        _forge(tmp, gl, cells[gl], wall)
        m = measure(tmp, CASES[gl], wall, cells[gl])
        fired, code, _ = drive("P3", lambda: (planted_zero_control(
            tmp, CASES[gl], wall, cells[gl], reg["controls"]["C_PZ"]["visibility_floor_K"],
            far_cell_override=m["i1L"]), None))
        check("C_PZ ARM P3 driven to REFUSE: the 'far' cell overridden to the stencil cell %d, so the "
              "plant IS visible where the control registered it invisible -> REFUSE" % m["i1L"],
              fired and code == EXIT_REFUSE)
        pz = planted_zero_control(tmp, CASES[gl], wall, cells[gl],
                                  reg["controls"]["C_PZ"]["visibility_floor_K"])
        ok = (pz["P2_permutation"]["moved_K"] != 0.0
              and pz["P3_specificity"]["moved_K"] == 0.0
              and pz["P1_value"]["recovered_K"] >= 0.1 * PLANT)
        check("C_PZ four arms on real bytes: N bit-identical; P1 recovered %.3g K; P2 permutation moved "
              "%.3g K; P3 far plant moved %.1g K"
              % (pz["P1_value"]["recovered_K"], pz["P2_permutation"]["moved_K"],
                 pz["P3_specificity"]["moved_K"]), ok)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ---- 8. the live tree, and the AST assert counter ---------------------
    fired, code, _ = drive("live", lambda: (grade(
        HERE, os.path.join(tempfile.gettempdir(), "t9ar1c_never.json"), reg, quiet_ref=True), None))
    check("live tree, no DONE markers -> REFUSE (exit %s)" % code, fired and code == EXIT_REFUSE)

    src = open(__file__).read()
    n0 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src)))
    n1 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src + "\nassert 1\n")))
    check("AST assert count in this file = %d (planted control: the counter sees %d)" % (n0, n1),
          n0 == 0 and n1 == 1)

    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root", default=HERE)
    ap.add_argument("--json", default=os.path.join(HERE, "gate_t9aR1c.json"))
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    return grade(a.root, a.json, load_registered())


if __name__ == "__main__":
    sys.exit(main())
