#!/usr/bin/env python3
"""BUILD ONLY -- T23G2Rn2: the dated §2ba NUMERICS successor to T23G2Rn.  LAUNCHES NOTHING.

======================================================================
DRAFT -- NOT FROZEN, NOTHING RUN
======================================================================
This script is a DRAFT authored by a heat-transfer lab-lane.  It is NOT
sha-frozen; the §3 diff-read and the freeze are the supervisor's.  Running
this script builds a case tree and drives blockMesh/splitMeshRegions/checkMesh
(meshing + inspection utilities, never a solver) -- but THIS drafting task does
not run it.

WHAT THIS SCRIPT IS.  A PARAMETRIC EDIT of build_t23g2r.py (the FROZEN base --
the SAME base build_t23g2rn.py edits; T23G2Rn was itself a numerics-only edit of
this base).  It IMPORTS build_t23g2r.py and reuses EVERY dictionary it generates
VERBATIM, overriding exactly ONE thing: the p_rgh solver block in
system/fluid/fvSolution.

THE ONLY BEHAVIOURAL DIFFERENCE vs build_t23g2r.py:
    system/fluid/fvSolution, p_rgh block, ALL THREE LEVELS identically:
        tolerance  1e-08  ->  1e-09     (ONE decade below the 1e-8 G-CONV gate)
        maxIter    (absent; GAMG default 1000)  ->  100   (INSERTED, explicit)
        relTol     0.01          UNCHANGED (small-but-nonzero; keeps GAMG's
                                 relative early-exit -- the property T23G2Rn's
                                 relTol 0 destroyed)
        solver     GAMG          UNCHANGED
        smoother   GaussSeidel   UNCHANGED
Every other dictionary -- controlDict, blockMeshDict, fvSchemes, the rho and
(U|h|k|omega) solver blocks, SIMPLE, relaxationFactors, thermo, fvOptions, the
solid regions, every 0.orig field -- is build_t23g2r.py's OWN output, byte for
byte, because this script does not regenerate them: it lets build_t23g2r.py
write them.

WHY (see T23G2Rn2_PREREGISTRATION.md §1-§2 and LESSONS L-514).
T23G2R graded NOT A RESULT: the p_rgh outer (initial) residual FLOOR-PINNED at
~1e-8 because the GAMG linear-solver `tolerance` (1e-8) EQUALLED the G-CONV gate
(1e-8) -- the linear solver stopped reducing p_rgh the instant it crossed the
gate ("No Iterations 0/1" in log.solve).  Its first successor T23G2Rn OVER-
CORRECTED with `relTol 0` (+ tolerance 1e-10): with no relative early-exit, GAMG
ran to its DEFAULT maxIter (1000 V-cycles) EVERY outer step, MEASURED at
13.79/13.11/14.53x the T23G2R per-iteration cost (T23G2Rn PENDING, §6 cost miss;
L-514).  T23G2Rn2 splits the difference exactly as L-514 prescribes: a
small-but-NONZERO relTol (kept at T23G2R's 0.01) so early outer steps still exit
cheaply on the relative criterion, an ABSOLUTE tolerance ONE decade below the
gate (1e-9) so only NEAR convergence does the sub-gate absolute floor bind and
drive p_rgh below 1e-8, and an EXPLICIT maxIter 100 so a mis-set relTol can never
silently run to 1000 V-cycles again (it bounds the worst case at ~2.2x, not 13x).
The GATE is NOT moved (that is rule 2 and not this lane's); only the linear-solver
stopping tolerance and the iteration cap are.

RELTOL 0.01 IS KEPT, NOT GUESSED.  The near-convergence p_rgh INITIAL linear
residual MEASURED from the frozen T23G2R logs (last 300 outer steps) is ~1e-8
typical, worst-case 1.966e-8 (L2).  relTol 0.01 x 1.966e-8 = 1.97e-10, which is
~5x BELOW the 1e-9 absolute floor, so near convergence the ABSOLUTE floor (1e-9)
binds and the linear solve is driven a full decade below the 1e-8 gate.  A tighter
relTol (e.g. the 1e-3 of L-514's example) is not needed -- that example assumed a
~1e-6 near-conv residual; the MEASURED value here is ~1e-8 -- and would only add
early-iteration cost.  0.01 is also T23G2R's own value, so early-iteration
behaviour is byte-anchored to the measured T23G2R baseline.

REFUSAL CONTRACT (T23G2Rn2_PREREGISTRATION.md §2.2, §5).  This script REFUSES
(exit non-zero) unless:
  * build_t23g2r.py's FLUID_SOLUTION contains EXACTLY ONE p_rgh block;
  * that block's solver is GAMG, its smoother is GaussSeidel and its relTol is
    0.01 (the parts held invariant), AND it carries NO `maxIter` entry (the base
    must NOT already set one, or the insertion is not a pure add);
  * its tolerance in the base is exactly 1e-08 (the value being changed);
  * the modified FLUID_SOLUTION differs from build_t23g2r's ONLY inside the
    p_rgh block, and inside it ONLY by the tolerance VALUE and by exactly one
    ADDED `maxIter 100;` line -- nothing else moves;
  * the new p_rgh block reads tolerance 1e-09, maxIter 100, relTol 0.01.
It PRINTS the p_rgh block it writes before delegating the build.

Usage (identical CLI to build_t23g2r.py): the phase is argv[1] (all|A|B|C) and
--level {L1|L2|L3} is REQUIRED and passed through to build_t23g2r.py's own
module-level level parse.
    python3 build_t23g2rn2.py all --level L2
"""
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE_PATH = os.path.join(HERE, "build_t23g2r.py")

# The p_rgh keys held INVARIANT (asserted from the base, never assumed).  relTol
# is now INVARIANT: T23G2Rn2 keeps T23G2R's 0.01, unlike T23G2Rn which set it 0.
P_RGH_INVARIANT = (("solver", "GAMG"), ("relTol", "0.01"),
                   ("smoother", "GaussSeidel"))
# The ONE value substituted, with its base (pre-edit) value asserted.
P_RGH_SUBST = (("tolerance", "1e-08", "1e-09"),)   # (key, old_expected, new)
# The ONE key INSERTED.  It must be ABSENT in the base (a pure add, not a
# silent overwrite of a maxIter the base already carried).
P_RGH_INSERT = (("maxIter", "100"),)


def _refuse(msg):
    raise SystemExit("REFUSE (build_t23g2rn2): " + msg)


def _load_base():
    """Import build_t23g2r.py as a module.  Its module-level code parses --level
    from sys.argv and raises SystemExit if it is absent; this script's own CLI
    passes --level through, so the base configures every derived constant for the
    SAME level.  Import happens HERE (inside a function), not at module scope, so
    `python3 -m py_compile` of this file never triggers the base's level parse."""
    if not os.path.isfile(BASE_PATH):
        _refuse("build_t23g2r.py is not on disk at %s; the parametric base is "
                "missing and nothing can be built parametrically from it" % BASE_PATH)
    spec = importlib.util.spec_from_file_location("build_t23g2r_base", BASE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _locate_p_rgh(fluid_solution):
    """Return the re.Match delimiting the SINGLE p_rgh solver block, or refuse.
    The match is whitespace-anchored on the block's own structure
    (`\\n    p_rgh\\n    {` ... first `\\n    }`) rather than on hand-counted
    spaces, so it does not break if the base reflows indentation."""
    anchors = re.findall(r"\n    p_rgh\n    \{", fluid_solution)
    if len(anchors) != 1:
        _refuse("build_t23g2r FLUID_SOLUTION contains %d p_rgh blocks, not exactly "
                "one; a surgical numerics edit needs exactly one target" % len(anchors))
    m = re.search(r"(\n    p_rgh\n    \{\n)(.*?)(\n    \})", fluid_solution, re.S)
    if not m:
        _refuse("could not delimit the p_rgh block body in build_t23g2r "
                "FLUID_SOLUTION; the base structure is not what this edit expects")
    return m


def _key_present(body, key):
    return re.search(r"\b%s\s+\S+?;" % re.escape(key), body) is not None


def _check_key(body, key, expected, where):
    m = re.search(r"\b%s\s+(\S+?);" % re.escape(key), body)
    if not m:
        _refuse("the p_rgh block %s has no `%s` entry; the base is not the "
                "T23G2R p_rgh block this edit was written against" % (where, key))
    if m.group(1) != expected:
        _refuse("the p_rgh block %s reads `%s %s;`, expected `%s %s;`; the base "
                "changed and the numerics diff cannot be applied on trust"
                % (where, key, m.group(1), key, expected))


def _tolerance_line_indent(body):
    """Return (leading_ws, value_col) for the tolerance line, so the inserted
    maxIter line can be aligned to the SAME value column the base uses.  The
    exact alignment is cosmetic -- the value-locality proof strips the maxIter
    line entirely -- but a tidy insertion is worth the few lines."""
    m = re.search(r"^([ \t]*)tolerance([ \t]+)\S+?;", body, re.M)
    if not m:
        _refuse("could not locate the `tolerance` line to size the maxIter "
                "insertion; the base structure is not what this edit expects")
    indent = m.group(1)
    value_col = len(indent) + len("tolerance") + len(m.group(2))
    return indent, value_col


def build_modified_fluid_solution(base_fluid_solution):
    """Return (modified, old_block, new_block).  Proves the edit is p_rgh-block-
    local AND, inside the block, limited to the tolerance VALUE and exactly one
    ADDED maxIter line -- nothing else moves."""
    m = _locate_p_rgh(base_fluid_solution)
    s, e = m.start(), m.end()
    head, body, tail = m.group(1), m.group(2), m.group(3)
    old_block = head + body + tail

    # 1. the parts held invariant must ALREADY be right in the base.
    for key, val in P_RGH_INVARIANT:
        _check_key(body, key, val, "(base)")
    # 2. the value we change must be exactly the T23G2R value in the base.
    for key, old, _new in P_RGH_SUBST:
        _check_key(body, key, old, "(base, pre-edit)")
    # 3. the key we INSERT must NOT already exist -- a pure add, never an
    #    overwrite of a base entry we did not know about.
    for key, _val in P_RGH_INSERT:
        if _key_present(body, key):
            _refuse("the base p_rgh block ALREADY carries a `%s` entry; this edit "
                    "INSERTS %s and must not silently overwrite one the base set. "
                    "The base changed; refusing." % (key, key))

    # 4. substitute the tolerance VALUE in place, one occurrence.
    new_body = body
    for key, _old, new in P_RGH_SUBST:
        new_body, n = re.subn(r"(\b%s\s+)\S+?;" % re.escape(key),
                              r"\g<1>%s;" % new, new_body, count=1)
        if n != 1:
            _refuse("expected exactly one `%s` substitution in the p_rgh body, "
                    "made %d" % (key, n))

    # 5. INSERT the maxIter line immediately AFTER the tolerance line, aligned to
    #    the base's own value column.  Exactly one insertion.
    indent, value_col = _tolerance_line_indent(new_body)
    for key, val in P_RGH_INSERT:
        pad = " " * max(1, value_col - len(indent) - len(key))
        ins_line = "%s%s%s%s;" % (indent, key, pad, val)
        new_body, n = re.subn(
            r"(^[ \t]*tolerance[ \t]+\S+?;)$",
            r"\g<1>\n" + ins_line.replace("\\", "\\\\"),
            new_body, count=1, flags=re.M)
        if n != 1:
            _refuse("expected exactly one `%s` insertion after the tolerance "
                    "line, made %d" % (key, n))
    new_block = head + new_body + tail
    modified = base_fluid_solution[:s] + new_block + base_fluid_solution[e:]

    # 6. PROVE the edit touched ONLY the p_rgh block: everything outside the
    #    original span is byte-identical.
    if modified[:s] != base_fluid_solution[:s] or \
       modified[s + len(new_block):] != base_fluid_solution[e:]:
        _refuse("the modified FLUID_SOLUTION differs OUTSIDE the p_rgh block; a "
                "numerics fix must not perturb any other solver dictionary")
    # 7. PROVE that inside the block, only the tolerance VALUE moved and only the
    #    maxIter line was ADDED: the invariant keys are unchanged, the new values
    #    read as required, and the block MINUS {tolerance value, the added maxIter
    #    line} is byte-identical old vs new.
    for key, val in P_RGH_INVARIANT:
        _check_key(new_body, key, val, "(new)")
    for key, _old, new in P_RGH_SUBST:
        _check_key(new_body, key, new, "(new)")
    for key, val in P_RGH_INSERT:
        _check_key(new_body, key, val, "(new)")

    def _normalize(block):
        b = block
        # blank the tolerance VALUE so a value change is invisible to the compare
        for key, _o, _n in P_RGH_SUBST:
            b = re.sub(r"(\b%s\s+)\S+?;" % re.escape(key), r"\g<1>VAL;", b)
        # remove the inserted key's whole line so an ADD is invisible to the
        # compare (it can only remove a line the old block never had)
        for key, _v in P_RGH_INSERT:
            b = re.sub(r"^[ \t]*%s[ \t]+\S+?;[ \t]*\n" % re.escape(key), "",
                       b, flags=re.M)
        return b
    if _normalize(old_block) != _normalize(new_block):
        _refuse("inside the p_rgh block, something OTHER than the tolerance VALUE "
                "and the single added maxIter line changed; the edit is not "
                "value-and-insertion-local")
    # 8. the add really is an ADD: the maxIter line must be absent from old_block
    #    and present exactly once in new_block.
    for key, _v in P_RGH_INSERT:
        if _key_present(old_block, key):
            _refuse("post-check: `%s` was present in the OLD block after all" % key)
        if len(re.findall(r"\b%s\s+\S+?;" % re.escape(key), new_block)) != 1:
            _refuse("post-check: `%s` is not present exactly once in the NEW "
                    "block" % key)
    return modified, old_block, new_block


def main():
    B = _load_base()

    modified, old_block, new_block = build_modified_fluid_solution(B.FLUID_SOLUTION)

    print("=" * 72)
    print("T23G2Rn2 -- dated §2ba NUMERICS EDIT of build_t23g2r.py (DRAFT, NOT FROZEN)")
    print("  level = %s   endTime = %d   (endTime UNCHANGED from T23G2R/T23G2Rn)"
          % (B.LEVEL, B.N_ITER))
    print("=" * 72)
    print("p_rgh block WRITTEN into system/fluid/fvSolution:")
    print(new_block.strip("\n"))
    print("-" * 72)
    print("change vs T23G2R:  tolerance 1e-08 -> 1e-09 ,  + maxIter 100 (INSERTED)")
    print("                   relTol 0.01, solver GAMG, smoother GaussSeidel UNCHANGED")
    print("change vs T23G2Rn: tolerance 1e-10 -> 1e-09 (one decade below gate, not two);")
    print("                   relTol 0 -> 0.01 (restore relative early-exit); + maxIter 100")
    print("every OTHER dictionary is build_t23g2r.py's own output, verbatim.")
    print("=" * 72)

    # Delegate the build to build_t23g2r.py with the ONE overridden constant.
    # B.main() reads FLUID_SOLUTION when it writes system/fluid/fvSolution.
    B.FLUID_SOLUTION = modified
    return B.main()


if __name__ == "__main__":
    sys.exit(main())
