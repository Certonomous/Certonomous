#!/usr/bin/env python3
"""A UNIFORM PLANT INTO A WEIGHTED STENCIL VERIFIES ONLY THAT THE WEIGHTS SUM TO ONE.

It never verifies what the individual weights ARE.  This file proves that claim in
exact arithmetic and then scans comparators for the shape that suffers from it.

THE ARITHMETIC (``--selftest`` proves every line of this in ``fractions.Fraction``)
----------------------------------------------------------------------------------
An axis extrapolation that recovers a field quadratic in ``r`` from the two
axis-adjacent columns at ``r1`` and ``r2 = k*r1`` has weights

    a = w1*f1 + w2*f2,      w1 = k**2/(k**2 - 1),      w2 = -1/(k**2 - 1)

so that, for EVERY k,

    w1 + w2 = (k**2 - 1)/(k**2 - 1) = 1     exactly.

Therefore a plant of P into BOTH columns -- the "uniform" arm -- shifts the
extrapolated value by ``P*(w1 + w2) = P`` **at any ratio whatsoever**.  The arm
returns the identical number on a correctly weighted stencil and on an arbitrarily
mis-weighted one.  It is BLIND in general, not merely insensitive.

A plant of P into a strict SUBSET of the inputs -- here the innermost column only --
shifts the extrapolate by ``P*w1``, which DOES depend on k.  It is DISCRIMINATING.

    k = 3      w1 = 9/8   = 1.125     uniform shift = P     subset shift = 1.125 P
    k = 7/3    w1 = 49/40 = 1.225     uniform shift = P     subset shift = 1.225 P
                                       ^ identical           ^ differ by P/10

HOW IT WAS FOUND, WHICH IS THE PART THAT MATTERS (L-326)
--------------------------------------------------------
T8's section 9 registered exactly ONE planted-zero arm, the both-column one, and the
comparator passed 69 selftest checks with two negative arms.  Its fixture
``make_synthetic_field_case`` placed cell centres at ``(j + 1/2)*dr``, which makes the
assumed ratio ``r2 = 3*r1`` TRUE BY CONSTRUCTION.  The fixture and the instrument
agreed because they shared one wrong assumption.

The real mesh gives ``r2/r1 = 7/3`` EXACTLY, because an OpenFOAM cell centre is the
volume centroid: for an annular sector, ``rbar = (2/3)(rb**3 - ra**3)/(rb**2 - ra**2)``,
giving ``(2/3)dr`` and ``(14/9)dr`` and a ratio of ``7/3``.  Not one of the 69 checks
could ever have caught it.  It surfaced only from running the frozen instrument against
a real mesh -- the one thing no selftest had done.

THE RULE THIS FILE ENFORCES
---------------------------
A planted-zero control on a weighted stencil MUST include at least one arm that plants
into a strict SUBSET of the stencil's inputs, and the selftest must show that arm
FIRING on a mis-weighted stencil where the uniform arm STAYS GREEN.

Scope: every interpolation, extrapolation and reconstruction comparator in this lab,
not only T8's centreline reader.

WHAT THE SCAN CAN AND CANNOT PROVE -- READ THIS BEFORE BELIEVING A CLEAN LINE
----------------------------------------------------------------------------
The scan is a STATIC, syntactic smell test over one file's AST.  Stating its reach
honestly is not politeness here: a checker that overstates its own reach is the exact
failure mode this lesson is about.

It CAN:
  * find call sites of plant-like callables, and arm rows that carry a plant-like
    callable by reference inside a tuple (the T8 ``arms = [(...), ...]`` shape);
  * count how many DISTINCT target-argument expressions those arms use;
  * find weighted-stencil expressions written as a numeric linear combination of two
    or more distinct operands, and functions named for extrapolation/interpolation.

It CANNOT:
  * prove that one arm's target set is a strict SUBSET of another's.  Two different
    expressions may denote the same cells; one may be a superset.  That needs the
    RUNTIME values, which a static scan does not have.  Where two or more distinct
    target expressions are found this file says so and says "inspect manually" -- it
    never reports a subset arm as proven;
  * see a stencil accumulated in a loop, built from a coefficient table, whose weights
    are VARIABLES rather than literals, or living in an imported module.  A file
    reported with no stencil is NOT proven to have none -- the variable-weight blind
    spot is carried as a declared case in ``--selftest`` so it stays on the record;
  * see a plant whose helper is not named for planting;
  * say anything about whether an existing subset arm is CORRECTLY registered.

A clean line from the scan is therefore evidence of absence of a smell, and nothing
stronger.  The proof in this file is the ``--selftest`` arithmetic, which is exact.

UNASSESSED IS NOT CLEAN -- why there is an exit code 3
------------------------------------------------------
The first independent test of this checker, by the heat-transfer supervisor on
2026-08-25, ran a case its author had not thought to construct: **a weighted stencil
with NO planted-zero control of any kind.**  It exited 0.  Severity was therefore
NON-MONOTONE in how well armed the instrument was -- the WORST case (no control at
all) scored the same as the BEST case (uniform arm plus subset arm), and only the
middle case fired:

    stencil + ZERO controls   ->  0     <- strictly the worst, and it read GREEN
    stencil + ONE uniform arm ->  2
    stencil + TWO arms        ->  0

The prose said "nothing this scan is competent to judge"; the EXIT CODE said "clean".
When those two disagree the exit code wins in practice, because exit codes are what get
automated into corpus sweeps and prose is what gets skimmed.  So a sweep by exit code
would have read an unarmed stencil as passing.

That is this very lesson's own shape, in the instrument written for it, found the same
way the lesson was found: by running it against something its author had not imagined.
The principle applied is already lab law -- CLAUDE.md rule 1 reserves ``PENDING`` as a
"not yet run" state and forbids using it to soften a ``GATE FAIL``.  The analogue here:
**NOT ASSESSED IS ITS OWN STATE AND IS NOT A PASS.**

Exit codes
----------
  0  ASSESSED AND CLEAN -- or genuinely nothing to assess (no weighted stencil found at
     all, so there is no control whose absence could mislead anyone)
  1  a note worth a look, no violation asserted
  2  ASSESSED AND VIOLATING: a plant-like control and a weighted stencil in one file
     with only ONE distinct plant target expression -- no subset arm found where the
     rule requires one.  Also 2 if ``--selftest`` fails.
  3  NOT ASSESSED: a weighted stencil IS present and NO plant-applying callable was
     found, so this scan has nothing it is competent to judge about its control.
     **THIS IS NOT A PASS.**  Treat it as an open question, never as a green.

PRECEDENCE when several files are scanned in one invocation: the process exit code is
the most serious severity seen, ordered 2 > 3 > 1 > 0 -- an assessed VIOLATION outranks
an unassessed file, even though 3 is the larger integer.  Do not use ``max()`` on these.

Usage
-----
    python3 scripts/check_stencil_plant_arms.py --selftest
    python3 scripts/check_stencil_plant_arms.py <file.py> [<file.py> ...]

Provenance: L-326, found 2026-08-25 on T8 by the heat-transfer team.  Cross-reference
L-321 (a fixture that shares the reader's route -- thesis confirmed here), and the two
same-day companions: ``scripts/check_k0d_mesh.py`` condition C planting into a modified
SPEC rather than a modified mesh, and ``scripts/check_grader_self_blindness.py`` going
RED ON CORRECT CODE.  Three instruments in one day passed green selftests while blind
to the defect they existed to catch; each was found only by running the instrument
against something real.  A selftest proves an instrument is SELF-CONSISTENT; only a
real artifact proves it is RIGHT.
"""
import argparse
import ast
import sys
from fractions import Fraction

# --------------------------------------------------------------------------
# the exact arithmetic
# --------------------------------------------------------------------------
# T8's registered perturbation and tolerance, used to state the discrepancy in the
# units the comparator actually gates on.  Read, never imported: analyse_t8.py is
# frozen and this file does not touch it.
T8_PLANT = Fraction(1234, 1000000)      # 1.234e-03 exactly
T8_TOL = Fraction(1, 10 ** 9)           # 1e-09


def axis_weights(k):
    """Exact (w1, w2) recovering a quadratic-in-r field at r = 0 from r1 and k*r1.

    f(r) = A + B r + C r^2 sampled at r1 and k*r1; the pair that annihilates both
    the linear and the quadratic term in the returned value of A is
    w1 = k^2/(k^2 - 1), w2 = -1/(k^2 - 1).
    """
    k = Fraction(k)
    if k == 1:
        raise ValueError("k = 1: the two columns coincide, no extrapolation exists")
    den = k * k - 1
    return k * k / den, Fraction(-1) / den


def uniform_shift(k, plant):
    """Shift of the extrapolate when EVERY input is planted with `plant`."""
    w1, w2 = axis_weights(k)
    return plant * (w1 + w2)


def subset_shift(k, plant):
    """Shift when ONLY the innermost input is planted -- a strict subset."""
    w1, _ = axis_weights(k)
    return plant * w1


def annular_centroid(ra, rb):
    """Volume centroid radius of an annular sector: (2/3)(rb^3-ra^3)/(rb^2-ra^2)."""
    ra, rb = Fraction(ra), Fraction(rb)
    return Fraction(2, 3) * (rb ** 3 - ra ** 3) / (rb ** 2 - ra ** 2)


# --------------------------------------------------------------------------
# the static scan
# --------------------------------------------------------------------------
PLANT_HINT = "plant"
# A callable whose name contains "plant" but ALSO one of these is the control's
# DRIVER, not a plant application.  ``check_planted_zero`` and
# ``planted_zero_control`` orchestrate arms; counting them as arms inflates the
# distinct-target count and would let a single-arm control read as clean.
DRIVER_HINTS = ("check_", "control", "_control", "verify")
STENCIL_NAME_HINTS = ("extrapol", "interp", "reconstruct", "stencil", "weight")

SEVERITY_MEANING = {
    0: "assessed and clean, or no weighted stencil to assess",
    1: "a note worth a look",
    2: "ASSESSED AND VIOLATING",
    3: "NOT ASSESSED -- a weighted stencil with no control found. NOT A PASS",
}


def _callee_name(node):
    f = node.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return None


def _is_plant_name(name):
    """True for a callable that APPLIES a plant, false for one that DRIVES arms."""
    if not name:
        return False
    low = name.lower()
    if PLANT_HINT not in low:
        return False
    return not any(h in low for h in DRIVER_HINTS)


def _plant_funcdefs(tree):
    return {n.name for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            and _is_plant_name(n.name)}


def _target_signature(exprs):
    """Render an arm's non-label arguments as a stable comparable string.

    String literals are dropped: they are the arm's human label, not its target.
    """
    parts = []
    for e in exprs:
        if isinstance(e, ast.Constant) and isinstance(e.value, str):
            continue
        try:
            parts.append(ast.unparse(e))
        except Exception:                                  # pragma: no cover
            parts.append("<unparseable>")
    return ", ".join(parts)


def find_plant_arms(tree):
    """Return [(lineno, signature)] for every plant call site and arm row.

    Two shapes are recognised:
      (1) a direct call ``plant_into_T(case, end_dir, tmp, targets, amount)``;
      (2) an arm ROW -- a tuple that carries a plant-like function BY REFERENCE,
          as in T8's ``arms = [("label", plant_into_T, inner2, PLANT, "dT", PLANT)]``.
          The row's remaining non-string elements are its target signature.
    """
    defs = _plant_funcdefs(tree)
    arms = []
    covered_tuples = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Tuple):
            # A Name is an arm's plant callable ONLY if it resolves to a plant
            # FUNCTION DEF in this file.  Matching bare names would count the
            # constants PLANT and PLANT_TOL as arms and inflate the distinct-target
            # count -- inflation is the dangerous direction: it suppresses a flag.
            names = [e for e in node.elts if isinstance(e, ast.Name) and e.id in defs]
            if names:
                rest = [e for e in node.elts if e not in names]
                arms.append((node.lineno, _target_signature(rest)))
                covered_tuples.add(id(node))

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and _is_plant_name(_callee_name(node)):
            arms.append((node.lineno, _target_signature(node.args)))

    return arms


def _flatten_additive(node, sign=1, terms=None):
    """Flatten a +/- tree into [(sign, operand_node)]."""
    if terms is None:
        terms = []
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub)):
        _flatten_additive(node.left, sign, terms)
        _flatten_additive(node.right, sign * (1 if isinstance(node.op, ast.Add) else -1),
                          terms)
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        _flatten_additive(node.operand, -sign, terms)
    else:
        terms.append((sign, node))
    return terms


def _numeric_coefficient(node):
    """(coeff_present, operand_source) for a single additive term."""
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Mult, ast.Div)):
        for a, b in ((node.left, node.right), (node.right, node.left)):
            if isinstance(a, ast.Constant) and isinstance(a.value, (int, float)):
                try:
                    return True, ast.unparse(b)
                except Exception:                          # pragma: no cover
                    return True, "<operand>"
    return False, None


def _parent_map(tree):
    parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[id(child)] = node
    return parents


def _has_string_constant(node):
    return any(isinstance(n, ast.Constant) and isinstance(n.value, str)
               for n in ast.walk(node))


def _is_plain_number(node):
    return isinstance(node, ast.Constant) and isinstance(node.value, (int, float))


def find_stencils(tree):
    """Return (strong, hints).

    ``strong`` -- [(lineno, source)] for expressions that are DIRECT evidence of a
    literally weighted stencil: an additive expression over two or more distinct
    NON-CONSTANT operands, carrying either two numeric coefficients
    (``1.125*f1 - 0.125*f2``) or one coefficient under a numeric divisor
    (``(9.0*T[i1] - T[i2]) / 8.0``).  String concatenation is excluded outright:
    ``'\\n' + '='*74`` is a banner, not a stencil.

    ``hints`` -- [(lineno, source)] for functions merely NAMED for extrapolation or
    interpolation.  A name is weak evidence and NEVER raises severity on its own;
    it is printed as context to look at.

    Loop-accumulated, table-driven and imported stencils are invisible to both.
    A file with no strong hit is NOT proven to have no stencil.
    """
    parents = _parent_map(tree)
    strong = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub))):
            continue
        par = parents.get(id(node))
        if isinstance(par, ast.BinOp) and isinstance(par.op, (ast.Add, ast.Sub)):
            continue                       # inner node of one additive expression
        if _has_string_constant(node):
            continue
        terms = _flatten_additive(node)
        if len(terms) < 2:
            continue
        operands, n_coeff = [], 0
        for _, t in terms:
            has, src = _numeric_coefficient(t)
            if has:
                n_coeff += 1
                operands.append(src)
            elif _is_plain_number(t):
                continue                   # a bare additive constant is an offset
            else:
                try:
                    operands.append(ast.unparse(t))
                except Exception:                          # pragma: no cover
                    operands.append("<term>")
        divided = (isinstance(par, ast.BinOp) and isinstance(par.op, ast.Div)
                   and _is_plain_number(par.right))
        if len(set(operands)) < 2:
            continue
        if not (n_coeff >= 2 or (n_coeff >= 1 and divided)):
            continue
        try:
            src = ast.unparse(par if divided else node)
        except Exception:                                  # pragma: no cover
            src = "<expr>"
        strong.append((node.lineno, src[:90]))

    hints = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            low = node.name.lower()
            if any(h in low for h in STENCIL_NAME_HINTS):
                hints.append((node.lineno, "def %s(...)" % node.name))
    return strong, hints


def scan(path):
    """Return (severity, [lines]).  severity in {0, 1, 2}."""
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        src = fh.read()
    tree = ast.parse(src, filename=path)
    arms = find_plant_arms(tree)
    strong, hints = find_stencils(tree)
    sigs = sorted({s for _, s in arms if s})
    out = []

    out.append("plant APPLICATION sites/arm rows (drivers excluded): %d" % len(arms))
    out.append("distinct plant TARGET expressions: %d" % len(sigs))
    out.append("literally weighted stencils (direct evidence): %d" % len(strong))
    for ln, s in strong[:6]:
        out.append("    stencil @L%d: %s" % (ln, s))
    out.append("functions merely NAMED for interpolation/extrapolation "
               "(weak, never raises severity): %d" % len(hints))
    for ln, s in hints[:4]:
        out.append("    name hint @L%d: %s" % (ln, s))

    if not arms:
        if strong:
            out.append("NOT ASSESSED (exit 3, NOT a pass): %d literally weighted "
                       "stencil(s) are present and NO plant-applying callable was found "
                       "in this file. A weighted stencil with no planted-zero control at "
                       "all is STRICTLY WORSE than one with a uniform-only arm, which "
                       "this scan exits 2 on -- so it must not share an exit code with "
                       "'assessed and clean'. This scan sees only callables whose name "
                       "contains 'plant', so a control may exist under another name or "
                       "in an imported module; that is precisely why this is NOT "
                       "ASSESSED rather than a violation. Go and look."
                       % len(strong))
            return 3, out
        out.append("NOTE: no plant-APPLYING callable found by NAME in this file, and no "
                   "literally weighted stencil either -- so there is genuinely nothing "
                   "here for this check to judge and no control whose absence could "
                   "mislead anyone. This scan sees only callables whose name contains "
                   "'plant'; it is NOT a proof that the file has no planted-zero "
                   "control.")
        return 0, out

    if not strong:
        out.append("NOTE: a plant-like control is present but this scan found no "
                   "LITERALLY WEIGHTED stencil. Loop-accumulated, table-driven and "
                   "imported stencils are INVISIBLE to a static scan, and a name hint "
                   "is not evidence of literal weights -- this is NOT a proof that no "
                   "stencil is planted into. Inspect manually.")
        return 0, out

    if len(sigs) < 2:
        out.append("VIOLATION (L-326): a literally weighted stencil and a plant-like "
                   "control in one file, with only %d distinct plant target "
                   "expression(s). A plant that goes uniformly into every input of a "
                   "weighted stencil verifies ONLY that the weights sum to one -- "
                   "w1+w2 = 1 for EVERY ratio -- so it cannot see a weight error at all. "
                   "The rule requires an arm planting into a strict SUBSET of the "
                   "stencil's inputs AND a demonstration that it FIRES where the uniform "
                   "arm stays green; ONE arm cannot supply both. This scan CANNOT tell "
                   "whether that one arm is uniform or subset, and cannot prove absence "
                   "-- only that it found no second arm. Inspect manually." % len(sigs))
        for ln, s in arms:
            out.append("    arm @L%d: %s" % (ln, s or "<no non-label args>"))
        return 2, out

    out.append("%d distinct plant target expressions found -- CONSISTENT with a subset "
               "arm being present, but THIS SCAN CANNOT PROVE one target set is a strict "
               "SUBSET of another: that needs the runtime values. It also cannot check "
               "that the subset arm is shown FIRING on a mis-weighted stencil. Inspect "
               "manually." % len(sigs))
    for s in sigs[:8]:
        out.append("    target: %s" % s[:100])
    return 0, out


# --------------------------------------------------------------------------
# selftest -- PROVES the claim in exact arithmetic
# --------------------------------------------------------------------------
# Severity precedence.  2 (assessed VIOLATION) outranks 3 (NOT ASSESSED) even though
# 3 is the larger integer, so ``max()`` is WRONG here and is never used on these.
_SEVERITY_RANK = {0: 0, 1: 1, 3: 2, 2: 3}


def worse(a, b):
    """Return the more serious of two severities under the documented precedence."""
    return a if _SEVERITY_RANK[a] >= _SEVERITY_RANK[b] else b


BAD_SRC = '''
PLANT = 1.234e-03

def plant_into_T(case, cells, amount):
    return case

def centreline(T, i1, i2):
    return (9.0 * T[i1] - T[i2]) / 8.0

def check_planted_zero(case, T, i1, i2):
    both = [i1, i2]
    c = plant_into_T(case, both, PLANT)
    return c
'''

GOOD_SRC = '''
PLANT = 1.234e-03

def plant_into_T(case, cells, amount):
    return case

def centreline(T, i1, i2):
    return (9.0 * T[i1] - T[i2]) / 8.0

def check_planted_zero(case, T, i1, i2):
    both = [i1, i2]
    inner_only = [i1]
    a = plant_into_T(case, both, PLANT)
    b = plant_into_T(case, inner_only, PLANT)
    return a, b
'''

NOSTENCIL_SRC = '''
PLANT = 1.234e-03

def plant_into_T(path, amount):
    return path

def read_max_change(path):
    return 0.0

def control(path):
    return plant_into_T(path, PLANT)
'''


DRIVER_SRC = '''
PLANT = 1.234e-03

def plant_into_T(case, cells, amount):
    return case

def centreline(T, i1, i2):
    return (9.0 * T[i1] - T[i2]) / 8.0

def check_planted_zero(case, T, i1, i2):
    """The DRIVER. Its own name contains "plant"; it applies nothing."""
    both = [i1, i2]
    return plant_into_T(case, both, PLANT)

def main(case, T, i1, i2):
    return check_planted_zero(case, T, i1, i2)
'''

NAMEHINT_ONLY_SRC = '''
PLANT = 1.234e-03

def plant_into_T(path, amount):
    return path

def interpolate(a, b, t):
    return a * (1.0 - t) + b * t

def control(path):
    return plant_into_T(path, PLANT)
'''


# The case the author did not think to construct, found by the heat-transfer
# supervisor's independent test: a weighted stencil with NO control of any kind.
# It must NOT share an exit code with "assessed and clean".
STENCIL_NO_CONTROL_SRC = '''
def centreline(T, i1, i2):
    return (9.0 * T[i1] - T[i2]) / 8.0

def grade(T, i1, i2):
    return centreline(T, i1, i2)
'''

# Its negative: no stencil and no control, where 0 is the RIGHT answer because there
# is no control whose absence could mislead anyone.
NOTHING_SRC = '''
def total(vals):
    out = 0.0
    for v in vals:
        out += v
    return out
'''


def _p(label, value, ok):
    print("  %-64s %s" % (label, "OK" if ok else "*** WRONG ***"))
    if value is not None:
        print("      %s" % value)
    return ok


def selftest():
    print("=" * 78)
    print("check_stencil_plant_arms.py -- SELFTEST")
    print("EXACT ARITHMETIC (fractions.Fraction). No floating point in part 1.")
    print("=" * 78)
    ok = True
    ks = [Fraction(3), Fraction(7, 3), Fraction(5, 2), Fraction(11, 7), Fraction(9, 4)]
    P = Fraction(1)

    print()
    print("(1) THE WEIGHTS SUM TO ONE AT EVERY RATIO -- exactly, not approximately")
    for k in ks:
        w1, w2 = axis_weights(k)
        good = (w1 + w2) == 1
        ok = _p("k = %-7s w1 = %-8s w2 = %-8s w1+w2" % (k, w1, w2),
                "w1 + w2 = %s   (exact Fraction equality to 1: %s)" % (w1 + w2, good),
                good) and ok

    print()
    print("(2) THE UNIFORM PLANT IS BLIND -- the SAME number at every ratio")
    shifts = []
    for k in ks:
        s = uniform_shift(k, P)
        shifts.append(s)
        ok = _p("k = %-7s uniform (both-column) shift" % k,
                "shift = %s * P   -- independent of k by construction" % s,
                s == P) and ok
    ok = _p("all %d ratios give the IDENTICAL uniform shift" % len(ks),
            "set of uniform shifts = {%s}  -> one element, so the arm cannot "
            "distinguish ANY two of these ratios"
            % ", ".join(str(s) for s in sorted(set(shifts))),
            len(set(shifts)) == 1) and ok
    d_uniform = uniform_shift(Fraction(3), P) - uniform_shift(Fraction(7, 3), P)
    ok = _p("k=3 vs k=7/3, uniform arm, difference",
            "%s * P  -- EXACTLY ZERO. The blindness, as a number." % d_uniform,
            d_uniform == 0) and ok

    print()
    print("(3) THE SUBSET PLANT DISCRIMINATES -- a DIFFERENT number at each ratio")
    subs = []
    for k in ks:
        s = subset_shift(k, P)
        subs.append(s)
        _p("k = %-7s subset (innermost-only) shift" % k,
           "shift = %s * P  = %.6f P" % (s, float(s)), True)
    ok = _p("the %d ratios give %d DISTINCT subset shifts" % (len(ks), len(set(subs))),
            "set = {%s}" % ", ".join(str(s) for s in sorted(set(subs))),
            len(set(subs)) == len(ks)) and ok
    d_subset = subset_shift(Fraction(7, 3), P) - subset_shift(Fraction(3), P)
    ok = _p("k=7/3 vs k=3, subset arm, difference",
            "49/40 P - 9/8 P = %s * P  = %.6f P  -- NON-ZERO. The discrimination."
            % (d_subset, float(d_subset)),
            d_subset == Fraction(1, 10)) and ok

    print()
    print("(4) THE OPERATIONAL CASE: an instrument shipping k=3 weights, run on a")
    print("    k=7/3 mesh, at T8's registered PLANT = 1.234e-03 and tol = 1e-09")
    shipped_w1, shipped_w2 = axis_weights(Fraction(3))
    true_w1, _ = axis_weights(Fraction(7, 3))
    seen_uniform = T8_PLANT * (shipped_w1 + shipped_w2)
    exp_uniform = T8_PLANT
    resid_u = abs(seen_uniform - exp_uniform)
    ok = _p("uniform arm on the MIS-WEIGHTED stencil",
            "expected %s, saw %s, residual %s -> %s vs tol 1e-09: STAYS GREEN"
            % (float(exp_uniform), float(seen_uniform), float(resid_u),
               "PASS" if resid_u <= T8_TOL else "FAIL"),
            resid_u <= T8_TOL) and ok
    seen_subset = T8_PLANT * shipped_w1
    exp_subset = T8_PLANT * true_w1
    resid_s = abs(seen_subset - exp_subset)
    ok = _p("subset arm on the SAME mis-weighted stencil",
            "expected %s, saw %s, residual %.6e = %d x tol -> FIRES"
            % (float(exp_subset), float(seen_subset), float(resid_s),
               int(resid_s / T8_TOL)),
            resid_s > T8_TOL) and ok
    print("      One stencil, one plant magnitude, two arms: the uniform arm's")
    print("      residual is exactly 0 and the subset arm's is %.6e." % float(resid_s))

    print()
    print("(5) WHY THE REAL MESH IS 7/3 AND THE FIXTURE WAS 3 -- exact geometry")
    c1 = annular_centroid(0, 1)
    c2 = annular_centroid(1, 2)
    ok = _p("OpenFOAM cell centre = volume centroid, rbar=(2/3)(rb^3-ra^3)/(rb^2-ra^2)",
            "cell 1 rbar = %s dr, cell 2 rbar = %s dr, ratio = %s"
            % (c1, c2, c2 / c1),
            c1 == Fraction(2, 3) and c2 == Fraction(14, 9)
            and c2 / c1 == Fraction(7, 3)) and ok
    f1, f2 = Fraction(1, 2), Fraction(3, 2)
    ok = _p("the fixture's (j+1/2)dr centres give ratio",
            "cell 1 = %s dr, cell 2 = %s dr, ratio = %s -- 3 BY CONSTRUCTION, which is "
            "why fixture and instrument agreed" % (f1, f2, f2 / f1),
            f2 / f1 == 3) and ok

    print()
    print("(6) THE STATIC SCAN, shown able to FIRE and able to STAY QUIET")
    import os
    import tempfile
    cases = [("uniform arm only, with a stencil   -> must FIRE", BAD_SRC, 2),
             ("a subset arm present              -> must stay quiet", GOOD_SRC, 0),
             ("plant, no literal stencil found   -> quiet, and says why",
              NOSTENCIL_SRC, 0),
             ("one arm + a 'plant'-NAMED DRIVER  -> must still FIRE (the driver "
              "must not count as an arm)", DRIVER_SRC, 2),
             ("KNOWN BLIND SPOT: one arm + a VARIABLE-weight interpolation "
              "-> quiet", NAMEHINT_ONLY_SRC, 0),
             ("stencil + ZERO controls -> must be 3, NOT ASSESSED, NOT a pass",
              STENCIL_NO_CONTROL_SRC, 3),
             ("no stencil and no control -> must be 0 (nothing to assess)",
              NOTHING_SRC, 0)]
    tmp = tempfile.mkdtemp(prefix="stencil_arms_")
    for i, (label, src, want) in enumerate(cases):
        p = os.path.join(tmp, "case%d.py" % i)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(src)
        sev, lines = scan(p)
        ok = _p(label, "severity = %d (wanted %d)" % (sev, want), sev == want) and ok
    print("      %d cases: %d must raise a severity, %d must stay at 0. A probe never"
          % (len(cases), sum(1 for c in cases if c[2]), sum(1 for c in cases if not c[2])))
    print("      shown able to fire is not evidence (standing rule 3); one never shown")
    print("      able to stay quiet flags everything.")
    print("      MONOTONICITY, which the first version of this file got WRONG: a stencil")
    print("      with ZERO controls (3) must not share an exit code with a stencil whose")
    print("      control carries a subset arm (0). The worst case scored the same as the")
    print("      best case until the supervisor's independent test ran the case this")
    print("      author had not constructed.")
    print("      The variable-weight case is a declared BLIND SPOT, not a success: a "
          "stencil whose")
    print("      weights are variables, not literals, is invisible to this scan even")
    print("      though the rule applies to it in full. It is in the selftest so the")
    print("      blindness is on the record instead of being discovered later.")

    print()
    print("(7) WHAT THIS SELFTEST DOES NOT PROVE -- stated, not buried")
    print("      Part 1-5 is a PROOF: exact rational arithmetic, no tolerance.")
    print("      Part 6 is NOT. It shows the scan separating assessed-clean, assessed-")
    print("      violating and NOT-ASSESSED on planted cases, one of which is a DECLARED")
    print("      BLIND SPOT rather than a success.")
    print("      It does NOT show the scan finds every such defect, and the scan CANNOT")
    print("      prove a subset relation between two target expressions. This lesson")
    print("      exists because a green selftest proved an instrument self-consistent")
    print("      while it was blind. Do not read part 6 as more than it is.")

    print()
    if ok:
        print("SELFTEST PASSED")
    else:
        print("SELFTEST FAILED")
    return 0 if ok else 2


def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        epilog=("EXIT CODES -- 0 assessed and clean (or no weighted stencil at all, so "
                "nothing to assess); 1 a note; 2 ASSESSED AND VIOLATING (a weighted "
                "stencil with only ONE distinct plant target); 3 NOT ASSESSED -- a "
                "weighted stencil is present and no plant-applying callable was found. "
                "3 IS NOT A PASS: unassessed is not clean, the same way PENDING is not "
                "a softened GATE FAIL (CLAUDE.md rule 1). Over several files the "
                "process exit code is the most serious severity under the precedence "
                "2 > 3 > 1 > 0, NOT the numeric max."),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("files", nargs="*")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.files:
        ap.error("give at least one .py file, or --selftest")
    worst = 0
    for p in a.files:
        print("=" * 78)
        print(p)
        try:
            sev, lines = scan(p)
        except SyntaxError as exc:
            print("  SKIPPED -- does not parse (%s)" % exc)
            continue
        for ln in lines:
            print("  " + ln)
        print("  severity: %d  (%s)" % (sev, SEVERITY_MEANING[sev]))
        worst = worse(worst, sev)
    if len(a.files) > 1:
        print("=" * 78)
        print("most serious severity, precedence 2 > 3 > 1 > 0: %d  (%s)"
              % (worst, SEVERITY_MEANING[worst]))
    return worst


if __name__ == "__main__":
    sys.exit(main())
