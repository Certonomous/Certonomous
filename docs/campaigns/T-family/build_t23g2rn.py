#!/usr/bin/env python3
"""BUILD ONLY -- T23G2Rn: the §2ba NUMERICS successor to T23G2R.  LAUNCHES NOTHING.

======================================================================
DRAFT -- NOT FROZEN, NOTHING RUN
======================================================================
This script is a DRAFT authored by a heat-transfer lab-lane.  It is NOT
sha-frozen; the §3 diff-read and the freeze are the supervisor's.  Running
this script builds a case tree and drives blockMesh/splitMeshRegions/checkMesh
(meshing + inspection utilities, never a solver) -- but THIS drafting task does
not run it.

WHAT THIS SCRIPT IS.  A PARAMETRIC EDIT of build_t23g2r.py.  It IMPORTS
build_t23g2r.py and reuses EVERY dictionary it generates VERBATIM, overriding
exactly ONE thing: the p_rgh solver block in system/fluid/fvSolution.

THE ONLY BEHAVIOURAL DIFFERENCE vs build_t23g2r.py:
    system/fluid/fvSolution, p_rgh block, ALL THREE LEVELS identically:
        tolerance  1e-08  ->  1e-10     (two decades below the 1e-8 G-CONV gate)
        relTol     0.01   ->  0
        solver     GAMG          UNCHANGED
        smoother   GaussSeidel   UNCHANGED
Every other dictionary -- controlDict, blockMeshDict, fvSchemes, the rho and
(U|h|k|omega) solver blocks, SIMPLE, relaxationFactors, thermo, fvOptions, the
solid regions, every 0.orig field -- is build_t23g2r.py's OWN output, byte for
byte, because this script does not regenerate them: it lets build_t23g2r.py
write them.

WHY (T23G2R_PREREGISTRATION successor; see T23G2Rn_PREREGISTRATION.md §1).
T23G2R graded NOT A RESULT because G-CONV failed on L2/L3: the p_rgh outer
(initial) residual floor-pinned at ~1e-8 (1.208e-08 L2, 1.036e-08 L3) because
the GAMG linear-solver `tolerance` (1e-8) EQUALLED the G-CONV convergence gate
(1e-8) -- the linear solver stopped reducing p_rgh the instant it crossed the
gate ("No Iterations 0" in log.solve).  Dropping the linear floor two decades
below the gate lets the outer residual descend below 1e-8.  The gate is NOT
moved (that is rule 2 and not this lane's); only the linear-solver stopping
tolerance is.

REFUSAL CONTRACT (T23G2Rn_PREREGISTRATION.md §2.2, §5).  This script REFUSES
(exit non-zero) unless:
  * build_t23g2r.py's FLUID_SOLUTION contains EXACTLY ONE p_rgh block;
  * that block's solver is GAMG and its smoother is GaussSeidel (the parts held
    invariant);
  * the modified FLUID_SOLUTION differs from build_t23g2r's ONLY inside the
    p_rgh block, and inside it ONLY in the tolerance and relTol values;
  * the new p_rgh block reads tolerance 1e-10 and relTol 0.
It PRINTS the p_rgh block it writes before delegating the build.

Usage (identical CLI to build_t23g2r.py): the phase is argv[1] (all|A|B|C) and
--level {L1|L2|L3} is REQUIRED and passed through to build_t23g2r.py's own
module-level level parse.
    python3 build_t23g2rn.py all --level L2
"""
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE_PATH = os.path.join(HERE, "build_t23g2r.py")

# The p_rgh keys held INVARIANT (asserted from the base, never assumed) and the
# two that change.  Kept as data so the diff is one table, not scattered edits.
P_RGH_INVARIANT = (("solver", "GAMG"), ("smoother", "GaussSeidel"))
P_RGH_NEW = (("tolerance", "1e-10"), ("relTol", "0"))
P_RGH_OLD_EXPECTED = (("tolerance", "1e-08"), ("relTol", "0.01"))


def _refuse(msg):
    raise SystemExit("REFUSE (build_t23g2rn): " + msg)


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
    """Return (start, end, block_text) for the SINGLE p_rgh solver block, or
    refuse.  The match is whitespace-anchored on the block's own structure
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
    return m.start(), m.end(), m


def _check_key(body, key, expected, where):
    m = re.search(r"\b%s\s+(\S+?);" % re.escape(key), body)
    if not m:
        _refuse("the p_rgh block %s has no `%s` entry; the base is not the "
                "T23G2R p_rgh block this edit was written against" % (where, key))
    if m.group(1) != expected:
        _refuse("the p_rgh block %s reads `%s %s;`, expected `%s %s;`; the base "
                "changed and the numerics diff cannot be applied on trust"
                % (where, key, m.group(1), key, expected))


def build_modified_fluid_solution(base_fluid_solution):
    """Return the modified FLUID_SOLUTION and the (old, new) p_rgh block texts.
    Proves the edit is p_rgh-block-local AND, inside the block, value-local."""
    s, e, m = _locate_p_rgh(base_fluid_solution)
    head, body, tail = m.group(1), m.group(2), m.group(3)
    old_block = head + body + tail

    # 1. the parts held invariant must ALREADY be right in the base.
    for key, val in P_RGH_INVARIANT:
        _check_key(body, key, val, "(base)")
    # 2. the parts we change must be exactly the T23G2R values in the base.
    for key, val in P_RGH_OLD_EXPECTED:
        _check_key(body, key, val, "(base, pre-edit)")

    # 3. substitute ONLY the two target values, in place, one occurrence each.
    new_body = body
    for key, val in P_RGH_NEW:
        new_body, n = re.subn(r"(\b%s\s+)\S+?;" % re.escape(key),
                              r"\g<1>%s;" % val, new_body, count=1)
        if n != 1:
            _refuse("expected exactly one `%s` substitution in the p_rgh body, "
                    "made %d" % (key, n))
    new_block = head + new_body + tail
    modified = base_fluid_solution[:s] + new_block + base_fluid_solution[e:]

    # 4. PROVE the edit touched ONLY the p_rgh block: everything outside [s,e)
    #    is byte-identical.
    if modified[:s] != base_fluid_solution[:s] or \
       modified[s + len(new_block):] != base_fluid_solution[e:]:
        _refuse("the modified FLUID_SOLUTION differs OUTSIDE the p_rgh block; a "
                "numerics fix must not perturb any other solver dictionary")
    # 5. PROVE that inside the block, only tolerance/relTol values moved: the
    #    invariant keys and the block scaffolding are unchanged.
    for key, val in P_RGH_INVARIANT:
        _check_key(new_body, key, val, "(new)")
    for key, val in P_RGH_NEW:
        _check_key(new_body, key, val, "(new)")
    # the block minus its value tokens must be identical old vs new.
    def _strip_values(block):
        b = block
        for key, _ in P_RGH_NEW:
            b = re.sub(r"(\b%s\s+)\S+?;" % re.escape(key), r"\g<1>VAL;", b)
        return b
    if _strip_values(old_block) != _strip_values(new_block):
        _refuse("inside the p_rgh block, something other than the tolerance and "
                "relTol VALUES changed; the edit is not value-local")
    return modified, old_block, new_block


def main():
    B = _load_base()

    modified, old_block, new_block = build_modified_fluid_solution(B.FLUID_SOLUTION)

    print("=" * 72)
    print("T23G2Rn -- §2ba NUMERICS EDIT of build_t23g2r.py (DRAFT, NOT FROZEN)")
    print("  level = %s   endTime = %d   (endTime UNCHANGED from T23G2R)"
          % (B.LEVEL, B.N_ITER))
    print("=" * 72)
    print("p_rgh block WRITTEN into system/fluid/fvSolution:")
    print(new_block.strip("\n"))
    print("-" * 72)
    print("change vs T23G2R:  tolerance 1e-08 -> 1e-10 ,  relTol 0.01 -> 0")
    print("                   solver GAMG + smoother GaussSeidel UNCHANGED")
    print("every OTHER dictionary is build_t23g2r.py's own output, verbatim.")
    print("=" * 72)

    # Delegate the build to build_t23g2r.py with the ONE overridden constant.
    # B.main() reads FLUID_SOLUTION when it writes system/fluid/fvSolution.
    B.FLUID_SOLUTION = modified
    return B.main()


if __name__ == "__main__":
    sys.exit(main())
