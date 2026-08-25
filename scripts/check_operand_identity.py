#!/usr/bin/env python3
"""STATE WHAT TWO THINGS YOU ARE COMPARING, AND SHOW THEY ARE COMPARABLE, BEFORE YOU
READ THE DIFFERENCE.

A comparison instrument can be internally flawless and still be wrong, because the two
things it subtracted were not the same kind of thing.  Every failure of this shape in
this lab has been a correct instrument applied to incommensurable operands:

  * two checkpoints believed to be 2 write-intervals apart that were 38,000 iterations
    apart, because purgeWrite and run extensions leave non-uniform gaps;
  * a reader at time 12000 compared against a solver sample at time 4000, because the
    loader derived ``times[-1]`` itself while the solver was still writing;
  * a whole-file md5 standing in for a gate that reads only ``internalField``, so a
    differing ``location`` header read as differing data;
  * a fixed 12-character substring that truncated ``3.7758...e-06`` to ``3.7758...``,
    making a converged value look like a residual of 3.8.

In every one the instrument was right and THE OPERANDS WERE NOT THE SAME THING, and in
every one A HUMAN READING ONE LINE OF OUTPUT WOULD HAVE CAUGHT IT -- because the two
identities were visibly different and nobody was shown them.

THE RULE: a comparison instrument PRINTS THE IDENTITY OF BOTH OPERANDS BEFORE it prints
their difference.  Not after; not on failure only.  BEFORE, ALWAYS.  Identity means
whatever makes the operand findable again: time directory, iteration number, file path,
field name, sample count, and the spacing between them where a spacing exists.

Relation to L-326 and L-321: L-326 says a CONTROL can be blind to what it was built to
catch; L-321 says a FIXTURE can share the reader's wrong assumption.  This says a
COMPARISON can be blind to whether its two sides are commensurable at all.  Same family,
different limb.

WHAT THIS SCAN CAN AND CANNOT DO -- read this before believing a clean line
--------------------------------------------------------------------------
It CAN, from one file's AST:
  * PROBE A -- find a ``zip()`` whose tuple unpacking DISCARDS a position into ``_``.
    Two independently built sequences paired BY POSITION, with the second operand's
    own key thrown away, is an alignment asserted nowhere and unprintable afterwards.
    Evidence that the operands were checked must be TIED TO THOSE OPERANDS -- the
    identity component of the same sequences, or an explicit alignment assertion.  A
    generic identity word elsewhere in the function is not evidence, and accepting it
    made this probe report CLEAN on the very file it was written from.
  * PROBE B -- find a function that takes the VALUE component out of the last element
    of two or more DISTINCT sequences OF PAIRS -- ``tin[-1][1]``, where ``[-1][0]``
    would have been the identity -- and never records an identity for them; and, where
    identities are recorded, whether the first appears BEFORE the comparison in SOURCE
    ORDER.  The pair form is the point: the sequence CARRIES its identity and the code
    reached past it.  A bare ``seq[-1]`` on a numeric array is NOT flagged -- an
    earlier draft did flag it and, swept over 113 files, returned Thomas solvers and
    mesh-spacing arrays whose operands come off one grid.

It CANNOT:
  * prove two operands ARE comparable, or that they are not.  It sees whether identity
    is REPORTED, never whether it is EQUAL.  That is the whole declared limit of a
    static reader here, and it is why probe B's finding is NOT ASSESSED, not VIOLATION.
  * follow values across functions, modules or files, or through a helper that does the
    printing.  A comparator that prints both identities from a shared helper will be
    flagged by probe B and is a FALSE POSITIVE this scan cannot resolve.
  * read SOURCE order as EXECUTION order.  Branches, loops and early returns break it.
    Where the "before" test is used, the output says it is a source-order test.
  * see a comparison written without ``-``, ``/`` or a ``[-1]`` read -- ``math.isclose``
    on two helper calls, a set difference, a ``!=`` on two parsed dicts;
  * see a comparison over sequences that do NOT carry their own identity.  There is
    nothing for the code to discard, so probe B has no signal, and such a comparison
    can still be between two incommensurable things.  This is the probe's largest
    declared blind spot and it is deliberate: the alternative was a probe that fires
    on every numerical routine in the repository.

Exit codes -- three-way, with an explicit precedence
----------------------------------------------------
  0  ASSESSED AND CLEAN, or nothing this scan is competent to judge (it says which)
  1  a note worth a look
  2  ASSESSED AND VIOLATING -- probe A: a positional zip that discards an operand's
     identity.  Also 2 if ``--selftest`` fails.
  3  NOT ASSESSED -- probe B: a multi-operand last-element comparison whose operands'
     identities are never recorded, or recorded only after the comparison.  NOT A PASS:
     unassessed is not clean, the same way PENDING is not a softened GATE FAIL
     (CLAUDE.md rule 1).

Across several files the process exit code is the MOST SERIOUS severity under the
precedence 2 > 3 > 1 > 0 -- NOT the numeric max(), which would let an unassessed file
mask a violation.

Usage
-----
    python3 scripts/check_operand_identity.py --selftest
    python3 scripts/check_operand_identity.py <file.py> [<file.py> ...]
"""
import argparse
import ast
import os
import sys
import tempfile

# Deliberately NOT loose. An earlier draft included "n_", which matches the substring
# inside "T_in_K" and scored a plain value keyword as an identity -- a probe that
# accepts anything as evidence proves nothing. Every token here must be a word a
# reader would recognise as naming WHICH sample, not WHAT value.
IDENTITY_TOKENS = ("iter", "time", "index", "idx", "step", "path", "sample",
                   "count", "at_", "when")
COMPARE_OPS = (ast.Sub, ast.Div)

SEVERITY_MEANING = {
    0: "assessed and clean, or nothing to assess",
    1: "a note worth a look",
    2: "ASSESSED AND VIOLATING",
    3: "NOT ASSESSED -- operand identity never reported. NOT A PASS",
}

_RANK = {0: 0, 1: 1, 3: 2, 2: 3}


def worse(a, b):
    """Most serious of two severities: 2 > 3 > 1 > 0.  max() would be wrong."""
    return a if _RANK[a] >= _RANK[b] else b


def _src(node):
    try:
        return ast.unparse(node)
    except Exception:                                      # pragma: no cover
        return "<expr>"


# --------------------------------------------------------------------------
# PROBE A -- a positional zip that DISCARDS an operand's identity
# --------------------------------------------------------------------------
def _discarded_names(target):
    """Names bound to a discard (``_`` or ``_x``) inside a tuple target."""
    out = []
    for n in ast.walk(target):
        if isinstance(n, ast.Name) and n.id == "_" or (
                isinstance(n, ast.Name) and n.id.startswith("_")):
            out.append(n.id)
    return out


def probe_a(tree):
    """zip(...) whose unpacking throws a position away into ``_``."""
    findings = []
    for node in ast.walk(tree):
        gens = []
        if isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp,
                             ast.DictComp)):
            gens = node.generators
        elif isinstance(node, ast.For):
            gens = [node]
        for g in gens:
            it, tgt = g.iter, g.target
            if not (isinstance(it, ast.Call) and isinstance(it.func, ast.Name)
                    and it.func.id == "zip"):
                continue
            if len(it.args) < 2:
                continue
            if not isinstance(tgt, ast.Tuple):
                continue
            if not _discarded_names(tgt):
                continue
            findings.append((getattr(node, "lineno", 0),
                             "positional zip(%s) unpacked as %s -- a position is "
                             "DISCARDED into `_`, so the two sequences are paired BY "
                             "POSITION with the second operand's own identity thrown "
                             "away. Nothing here asserts they are aligned, and after "
                             "the discard nothing CAN print it. If either sequence "
                             "ever has a gap the other does not, every later pair is "
                             "off by one and the difference is between two different "
                             "samples."
                             % (", ".join(_src(a) for a in it.args), _src(tgt))))
    return findings


# --------------------------------------------------------------------------
# PROBE B -- multi-operand last-element comparison with no identity recorded
# --------------------------------------------------------------------------
def _is_last_index(node):
    if not isinstance(node, ast.Subscript):
        return False
    sl = node.slice
    return (isinstance(sl, ast.UnaryOp) and isinstance(sl.op, ast.USub)
            and isinstance(sl.operand, ast.Constant) and sl.operand.value == 1)


def _last_indexed_sites(node):
    """[(name, lineno, node)] for every ``seq[-1]`` read beneath `node`."""
    sites = []
    for n in ast.walk(node):
        if not _is_last_index(n):
            continue
        base = n.value
        while isinstance(base, ast.Subscript):
            base = base.value
        if isinstance(base, ast.Name):
            sites.append((base.id, n.lineno, n))
    return sites


def _paired_value_reads(fn):
    """[(name, lineno)] for ``seq[-1][k]`` where k is a constant OTHER than 0.

    THIS, AND NOT A BARE ``seq[-1]``, IS THE PROBE'S SUBJECT, and the narrowing was
    forced by a real sweep. An earlier draft fired on any function reading the last
    element of two sequences, and over 113 files in three run trees it flagged Thomas
    tridiagonal solvers and mesh-spacing arrays -- ``2.0 * kc[-1] / dx[-1]`` -- where
    the two operands come off ONE grid and their comparability is structural. A probe
    never shown able to stay quiet flags everything, and 15 hits of which 14 were
    numerics is that probe.

    ``seq[-1][1]`` is different in kind: the element is a PAIR, so the sequence CARRIES
    ITS OWN IDENTITY, and the code has reached past the identity to take the value.
    That is the tell -- the identity was available and was discarded -- and it is what
    makes the finding actionable rather than a guess about somebody's array.

    Declared consequence: a comparison over sequences that do NOT carry their identity
    is INVISIBLE to this probe. There is nothing to discard, so there is no signal, and
    such a comparison can still be between two incommensurable things. The scan says so.
    """
    out = []
    for n in ast.walk(fn):
        if not (isinstance(n, ast.Subscript) and _is_last_index(n.value)):
            continue
        sl = n.slice
        if not (isinstance(sl, ast.Constant) and isinstance(sl.value, int)):
            continue
        if sl.value == 0:
            continue                      # that IS the identity component
        base = n.value.value
        while isinstance(base, ast.Subscript):
            base = base.value
        if isinstance(base, ast.Name):
            out.append((base.id, n.lineno))
    return out


def _last_indexed_names(node):
    """Names read at [-1]: ``tin[-1]`` -> {"tin"}."""
    return {nm for nm, _, _ in _last_indexed_sites(node)}


def _identity_component_sites(fn):
    """[(name, lineno)] for ``seq[-1][0]`` -- the IDENTITY component of a pair."""
    out = []
    for n in ast.walk(fn):
        if not (isinstance(n, ast.Subscript) and _is_last_index(n.value)):
            continue
        sl = n.slice
        if not (isinstance(sl, ast.Constant) and sl.value == 0):
            continue
        base = n.value.value
        while isinstance(base, ast.Subscript):
            base = base.value
        if isinstance(base, ast.Name):
            out.append((base.id, n.lineno))
    return out


def _identity_component_lines(fn):
    """Lines where the INDEX component of a last-element read is taken.

    ``tin[-1][0]`` takes the sample's identity; ``tin[-1][1]`` takes its value.
    Reading the identity component of two different sequences is exactly the
    evidence this probe is looking for, and it carries no identity-ish word.
    """
    lines = []
    for n in ast.walk(fn):
        if isinstance(n, ast.Subscript) and _is_last_index(n.value):
            sl = n.slice
            if isinstance(sl, ast.Constant) and sl.value == 0:
                lines.append(n.lineno)
    return lines


def _alignment_assertion_lines(fn):
    """Lines that assert the two operands line up.

    Two accepted forms, and no looser: a comparison where BOTH sides involve a
    last-element read, and an ``==``/``!=`` between two bare names in a function that
    has ALSO taken index components. Accepting any ``==`` anywhere would let an
    unrelated equality vouch for an alignment nobody checked -- evidence that cheap
    would suppress the true positives this probe exists to raise.
    """
    lines = []
    has_components = bool(_identity_component_lines(fn))
    for n in ast.walk(fn):
        if not isinstance(n, ast.Compare):
            continue
        parts = [n.left] + list(n.comparators)
        if sum(1 for pp in parts if _last_indexed_sites(pp)) >= 2:
            lines.append(n.lineno)
        elif (has_components and isinstance(n.ops[0], (ast.NotEq, ast.Eq))
              and all(isinstance(pp, ast.Name) for pp in parts)):
            lines.append(n.lineno)
    return lines


def _identity_lines(fn):
    """Line numbers where an identity-ish token is written or printed."""
    lines = []
    for n in ast.walk(fn):
        if isinstance(n, ast.keyword) and n.arg and any(
                t in n.arg.lower() for t in IDENTITY_TOKENS):
            lines.append(getattr(n.value, "lineno", 0))
        elif isinstance(n, ast.Constant) and isinstance(n.value, str) and any(
                t in n.value.lower() for t in IDENTITY_TOKENS):
            lines.append(getattr(n, "lineno", 0))
    return sorted(x for x in lines if x)


def probe_b(tree):
    findings = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        paired = _paired_value_reads(fn)
        allnames = sorted({nm for nm, _ in paired})
        if len(allnames) < 2:
            continue                      # not a MULTI-operand comparison over pairs
        # A comparison of VALUES: an arithmetic difference or ratio that consumes a
        # last-element read. The def line is NOT a comparison site -- an earlier draft
        # used it and reported correct code as defective, which is the exact failure
        # this checker exists to name.
        cmp_sites = []
        for n in ast.walk(fn):
            if isinstance(n, ast.BinOp) and isinstance(n.op, COMPARE_OPS):
                if _paired_value_reads(n):
                    cmp_sites.append((n.lineno, allnames, _src(n)[:80]))
        if not cmp_sites:
            first_site = min(ln for _, ln in paired)
            cmp_sites = [(first_site, allnames,
                          "%d distinct PAIRED sequences read at [-1][k] in %s()"
                          % (len(allnames), fn.name))]
        # EVIDENCE MUST BE TIED TO THESE OPERANDS.  A generic identity word anywhere
        # in the function is NOT evidence about the two things being subtracted: on a
        # real 100-line grader, `iterations=iters[-1]` sits near the top and would
        # vouch for every later comparison in the body.  That is how this probe first
        # returned CLEAN on the very file it was written from.  Accepted evidence is
        # the identity component of the OPERAND sequences themselves, or an explicit
        # alignment assertion between two last-element reads.
        comp = _identity_component_sites(fn)
        covered = {nm for nm, _ in comp}
        align = _alignment_assertion_lines(fn)
        tied = sorted([ln for nm, ln in comp if nm in allnames] + align)
        enough = len(covered & set(allnames)) >= 2 or bool(align)
        idl = tied if enough else []
        first_cmp = min(l for l, _, _ in cmp_sites)
        if not idl:
            findings.append((first_cmp,
                             "%s(): %s -- the last element of %d DISTINCT sequences "
                             "of PAIRS is read, the VALUE component taken and the "
                             "IDENTITY component discarded, and no identity (iteration, "
                             "time, index, path, sample count) is recorded anywhere in "
                             "this function. Each [-1] is that sequence's OWN last "
                             "sample; "
                             "if one series stops earlier the two are at different "
                             "positions and the difference spans them. Nothing here "
                             "shows they are comparable, and nothing prints what would."
                             % (fn.name, cmp_sites[0][2], len(cmp_sites[0][1]))))
        elif min(idl) > first_cmp:
            findings.append((first_cmp,
                             "%s(): %s -- identity IS recorded, but the first mention "
                             "is at line %d, AFTER the comparison at line %d. The rule "
                             "is identity BEFORE the difference, not after and not on "
                             "failure only. SOURCE ORDER IS NOT EXECUTION ORDER, so "
                             "this is NOT ASSESSED rather than a violation: go and look."
                             % (fn.name, cmp_sites[0][2], min(idl), first_cmp)))
    return findings


def scan(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        tree = ast.parse(fh.read(), filename=path)
    fa, fb = probe_a(tree), probe_b(tree)
    out = ["probe A (positional zip discarding an operand's identity): %d" % len(fa),
           "probe B (multi-operand [-1] comparison, identity not reported first): %d"
           % len(fb)]
    for ln, d in fa:
        out.append("  VIOLATION @L%d: %s" % (ln, d))
    for ln, d in fb:
        out.append("  NOT ASSESSED @L%d: %s" % (ln, d))
    if not fa and not fb:
        out.append("NOTHING FOUND (exit 0). Read this as 'no smell of these two shapes',"
                   " NOT as 'this file's comparisons are sound': this scan sees whether"
                   " identity is REPORTED, never whether it is EQUAL, and it cannot"
                   " follow a value across functions, modules or a shared printing"
                   " helper. A comparison written without -, / or a [-1] read is"
                   " invisible to it.")
        return 0, out
    sev = 2 if fa else 3
    return sev, out


# --------------------------------------------------------------------------
# selftest
# --------------------------------------------------------------------------
BAD_A = '''
def spans(tmax, tmin):
    return [(i, mx - mn) for (i, mx), (_, mn) in zip(tmax, tmin)]
'''

GOOD_A = '''
def spans(tmax, tmin):
    out = []
    for (i, mx), (j, mn) in zip(tmax, tmin):
        if i != j:
            raise RuntimeError("operands at different iterations: %s vs %s" % (i, j))
        out.append((i, mx - mn))
    return out
'''

BAD_B = '''
def recirculation(tin, tout, t_sup, dt):
    theta_in = (tin[-1][1] - t_sup) / dt
    theta_out = (tout[-1][1] - t_sup) / dt
    return dict(T_in_K=tin[-1][1], T_out_K=tout[-1][1],
                theta_in=theta_in, theta_out=theta_out)
'''

GOOD_B = '''
def recirculation(tin, tout, t_sup, dt):
    i_in, i_out = tin[-1][0], tout[-1][0]
    print("T_in from iteration %s, T_out from iteration %s" % (i_in, i_out))
    if i_in != i_out:
        raise RuntimeError("not comparable")
    theta_in = (tin[-1][1] - t_sup) / dt
    theta_out = (tout[-1][1] - t_sup) / dt
    return dict(at_iteration=i_in, theta_in=theta_in, theta_out=theta_out)
'''

NOTHING = '''
def total(vals):
    out = 0.0
    for v in vals:
        out += v
    return out
'''


def _p(label, value, ok):
    print("  %-62s %s" % (label, "OK" if ok else "*** WRONG ***"))
    if value:
        print("      %s" % value)
    return ok


def selftest():
    print("=" * 78)
    print("check_operand_identity.py -- SELFTEST (planted controls, both directions)")
    print("=" * 78)
    ok = True
    tmp = tempfile.mkdtemp(prefix="operand_identity_")
    cases = [
        ("PROBE A positive: zip pairing that discards `_` -> must FIRE", BAD_A, 2),
        ("PROBE A negative: zip binds BOTH keys and asserts i == j -> quiet",
         GOOD_A, 0),
        ("PROBE B positive: two [-1] reads, no identity recorded -> 3", BAD_B, 3),
        ("PROBE B negative: identities printed BEFORE the difference -> quiet",
         GOOD_B, 0),
        ("no comparison at all -> 0, and says what it did not look at", NOTHING, 0),
    ]
    for n, (label, src, want) in enumerate(cases):
        p = os.path.join(tmp, "c%d.py" % n)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(src)
        sev, _ = scan(p)
        ok = _p(label, "severity = %d (wanted %d)" % (sev, want), sev == want) and ok

    print()
    print("  PRECEDENCE: an unassessed file must never mask a violation")
    a = os.path.join(tmp, "c0.py")
    b = os.path.join(tmp, "c2.py")
    sa, _ = scan(a)
    sb, _ = scan(b)
    agg = worse(worse(0, sb), sa)
    ok = _p("a 2-file and a 3-file in one run aggregate to",
            "worse(%d, %d) = %d   (max() would have given %d and MASKED the violation)"
            % (sa, sb, agg, max(sa, sb)), agg == 2) and ok

    print()
    print("  WHAT THIS SELFTEST DOES NOT PROVE, stated rather than buried:")
    print("    it shows each probe able to FIRE on a planted defect and able to STAY")
    print("    QUIET on its clean counterpart -- nothing more. It does NOT show the")
    print("    probes find every instance of either shape, and NO static probe can")
    print("    show two operands are comparable: this file sees whether identity is")
    print("    REPORTED, never whether it is EQUAL. That is why probe B returns 3,")
    print("    NOT ASSESSED, and never 2.")
    print()
    print("SELFTEST PASSED" if ok else "SELFTEST FAILED")
    return 0 if ok else 2


def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        epilog=("EXIT CODES -- 0 clean or nothing to assess; 1 a note; 2 VIOLATING "
                "(probe A); 3 NOT ASSESSED (probe B) and NOT a pass. Across files the "
                "exit code is the most serious under 2 > 3 > 1 > 0, not numeric max."),
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
