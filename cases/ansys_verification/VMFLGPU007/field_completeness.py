#!/usr/bin/env python3
"""FIELD COMPLETENESS -- the consumer-side 0/ field guard, REPAIRED.

Usage:  field_completeness.py <case_dir>      -> exit 0 (OK) / 1 (ABORT)
        field_completeness.py --selftest      -> drives every clause, exit 0/1

WHAT IT CHECKS.  The fields the CONSUMER actually asks for must exist in the
case's 0/ directory.  The consumer is fvSolution's `solvers` block INTERSECTED
with the fields the closure named in constant/turbulenceProperties creates,
minus `phi`; every lookup accepts `X` or `X.gz`.  It is a CONSUMER-side check,
never a regex over a surface: a field nobody solves for is not required, and a
field the closure does not create is not required either.

WHY THIS FILE EXISTS AT ALL -- TWO BUGS, BOTH MEASURED, BOTH REPAIRED HERE.
The embedded ancestor of this guard (VMFLGPU001-R2 launcher blob
c75076be3aa1d83ea8e67145c25ad43141d926cb, function `field_completeness`) passes
VACUOUSLY.  On VMFLGPU001-R2's own frozen inputs it prints

    FIELD COMPLETENESS OK: closure=laminar required={} all present in 0/

-- an EMPTY required set.  It gates nothing, and it has printed OK on every case
this family has run.  A guard that prints OK on an empty set is decoration.

  BUG 1 -- THE PARSER CLEARS THE KEY AT THE NEWLINE BEFORE THE BRACE.
  The ancestor's key-collecting loop ended with

      if ch in ";\\n" and depth == 0:
          tok = ""

  which clears the accumulated key name at EVERY newline at depth 0 -- including
  the newline BETWEEN a solver key and its opening brace.  OpenFOAM's standard
  style is

      p_rgh
      {
          ...
      }

  so the key is always discarded before the `{` that would have captured it, and
  `keys` comes back EMPTY for every conventionally-formatted fvSolution.
  THE CAUSE IS NOT THE NESTED `petsc { options { ... } }` BLOCKS.  The depth
  tracking is correct and always was; the discriminating A/B is driven in
  --selftest (arm BUG1-A keeps the nesting and puts key and brace on ONE line ->
  the ancestor WORKS; arm BUG1-B removes the nesting entirely and leaves the key
  on its own line -> the ancestor STILL FAILS).  Repair: only `;` clears the
  token.  A `;` at depth 0 ends a `key value;` entry, which is not a block and
  must not be captured; a newline is ordinary whitespace and `.split()[-1]`
  already takes the last token.

  BUG 2 -- THE BASE REQUIREMENT SET CANNOT SEE A BUOYANT CASE.
  The ancestor hard-codes `{"p", "U"}`.  VMFLGPU007 is buoyant: its pressure
  variable is `p_rgh` and there is no `p` in its solvers block at all.  So even
  with BUG 1 repaired, a missing `0/p_rgh` sails straight through -- the guard
  would require only {U, k, epsilon} and report OK on a case that cannot start.
  Repair: BASE = {"p", "U", "p_rgh"}.

  WHY `h` AND `e` ARE DELIBERATELY *NOT* IN BASE, and this is a correctness
  point rather than an oversight: VMFLGPU007's fvSolution solves `"(U|h|k|
  epsilon)"`, so `h` IS in the consumer set -- but OpenFOAM does not read a
  `0/h`.  Sensible enthalpy is DERIVED from `0/T` by the thermophysical model at
  construction.  Requiring `h` would abort every correctly-built buoyant case.
  The energy PRIMITIVE that must exist is `0/T`, and it is required by
  ENERGY_PRIMITIVE below whenever the consumer solves for h or e -- so the
  energy field is checked, by the name that is actually on disk.

  Both repairs are STRICTLY MORE DISCRIMINATING than the ancestor.  Neither
  loosens a test: BUG 1's repair can only ADD keys to a set that was empty, and
  BUG 2's repair can only ADD names to the base set.  Nothing that aborted
  before passes now.

NO `assert` ANYWHERE.  `python3 -O` strips assert statements, so a guard built
on them evaporates under optimisation.  Every refusal below is an explicit
branch with an exit code, and --selftest is driven under both `python3` and
`python3 -O` in the committed drive record.
"""
import os
import re
import sys

# The base consumer set: pressure and velocity, in the names OpenFOAM actually
# uses.  `p_rgh` is the buoyant pressure variable (BUG 2).
BASE = {"p", "U", "p_rgh"}

# Energy: the consumer solves for `h`/`e`, but the field ON DISK is `0/T`.
ENERGY_SOLVED = {"h", "e"}
ENERGY_PRIMITIVE = "T"

# What each closure CREATES.  A closure not listed is refused rather than
# guessed at.
CLOSURE = {
    "laminar": set(),
    "kEpsilon": {"k", "epsilon", "nut"},
    "realizableKE": {"k", "epsilon", "nut"},
    "RNGkEpsilon": {"k", "epsilon", "nut"},
    "kOmegaSST": {"k", "omega", "nut"},
    "kOmega": {"k", "omega", "nut"},
    "SpalartAllmaras": {"nuTilda", "nut"},
}


def solver_keys(body, legacy_newline_clear=False):
    """Top-level keys of a `solvers { ... }` body.

    `legacy_newline_clear=True` reinstates BUG 1 verbatim.  It exists so
    --selftest can SHOW the defect and show the repair flipping it; it is never
    used on a live case.
    """
    keys, depth, tok = [], 0, ""
    for ch in body:
        if ch == "{":
            if depth == 0:
                k = tok.strip().strip('"').split()
                if k:
                    keys.append(k[-1])
            depth += 1
            tok = ""
        elif ch == "}":
            depth -= 1
            tok = ""
        elif depth == 0:
            tok += ch
        # REPAIRED (BUG 1): only `;` clears.  A newline is whitespace.
        clear_on = ";\n" if legacy_newline_clear else ";"
        if ch in clear_on and depth == 0:
            tok = ""
    return keys


def expand(keys):
    """`"(U|h|k|epsilon)"` -> {U, h, k, epsilon}; strip the `Final` suffix."""
    cand = set()
    for k in keys:
        mm = re.fullmatch(r"\(([^)]*)\)", k)
        if mm:
            for alt in mm.group(1).split("|"):
                alt = alt.strip()
                if alt:
                    cand.add(alt)
        else:
            cand.add(k)
    return {c[:-5] if c.endswith("Final") else c for c in cand}


def closure_of(tp_path, legacy_line_anchor=False):
    """The closure named in constant/turbulenceProperties.

    BUG 3 -- FOUND BY DRIVING THIS GUARD, not by reading it, and it is the
    reason a selftest is worth more than a review.  The ancestor anchored the
    model lookup to the START OF A LINE:

        re.search(r"^\\s*(?:RASModel|LESModel|model)\\s+(\\w+)\\s*;", txt, re.M)

    OpenFOAM's RAS sub-dictionary is very commonly written INLINE --
    VMFLGPU007's own inherited turbulenceProperties is literally

        RAS { RASModel kEpsilon; turbulence on; printCoeffs on; }

    -- so `RASModel` is not at the start of any line, the lookup misses, and
    `model` stays at the value of `simulationType`, namely the string "RAS".
    "RAS" is not a key of CLOSURE, so the ancestor does not fall back or guess:
    it ABORTS with "closure 'RAS' is not in this launcher's registered closure
    map".  On VMFLGPU007's real inputs the ancestor guard would therefore have
    REFUSED THE LAUNCH -- loudly, at zero compute, for a reason that is a defect
    in the guard rather than in the case.  Repair: match the key anywhere, on a
    word boundary, which cannot match `RASModel` when looking for `model`
    because the comparison is case-sensitive.

    `legacy_line_anchor=True` reinstates the defect for --selftest only.
    """
    model = "laminar"
    if os.path.isfile(tp_path):
        txt = open(tp_path).read()
        mm = re.search(r"\bsimulationType\s+(\w+)\s*;", txt)
        if mm:
            model = mm.group(1)
        pat = (r"^\s*(?:RASModel|LESModel|model)\s+(\w+)\s*;" if legacy_line_anchor
               else r"\b(?:RASModel|LESModel|model)\s+(\w+)\s*;")
        mm = re.search(pat, txt, re.M) if legacy_line_anchor else re.search(pat, txt)
        if mm and model != "laminar":
            model = mm.group(1)
    return model


def check(d, legacy_newline_clear=False, legacy_base=False,
          legacy_line_anchor=False):
    """Returns (rc, message)."""
    fvs = os.path.join(d, "system", "fvSolution")
    tp = os.path.join(d, "constant", "turbulenceProperties")
    if not os.path.isfile(fvs):
        return 1, "ABORT: no system/fvSolution in %s" % d
    txt = open(fvs).read()
    m = re.search(r"\bsolvers\b\s*\{", txt)
    if not m:
        return 1, "ABORT: no solvers block in %s" % fvs
    i = m.end()
    depth = 1
    start = i
    while i < len(txt) and depth:
        if txt[i] == "{":
            depth += 1
        elif txt[i] == "}":
            depth -= 1
        i += 1
    if depth:
        return 1, "ABORT: unbalanced solvers block in %s" % fvs
    cand = expand(solver_keys(txt[start:i - 1], legacy_newline_clear))

    model = closure_of(tp, legacy_line_anchor)
    if model not in CLOSURE:
        return 1, ("ABORT: closure %r is not in this guard's registered closure "
                   "map; the consumer-side field set cannot be derived and this "
                   "guard does not guess" % model)

    base = {"p", "U"} if legacy_base else BASE
    required = (cand & (base | CLOSURE[model])) - {"phi"}
    # The energy PRIMITIVE: if the consumer solves for h or e, `0/T` must exist.
    # `h`/`e` are never required by name -- OpenFOAM derives them from T.
    if cand & ENERGY_SOLVED:
        required = required | {ENERGY_PRIMITIVE}

    # THE VACUITY REFUSAL.  A guard that certifies an EMPTY set has measured
    # nothing.  fvSolution has a solvers block, so at least one field must have
    # been recognised; an empty set means the parser failed, not that the case
    # needs no fields.  This is the clause that would have caught BUG 1 on the
    # day it shipped.
    if not required:
        return 1, ("ABORT: the required field set is EMPTY. %s has a solvers "
                   "block, so a consumer-side set of at least one field was "
                   "expected; an empty set means this guard PARSED NOTHING and "
                   "would certify the case vacuously. It refuses instead of "
                   "printing OK (closure=%s, solver keys seen: %s)."
                   % (fvs, model, sorted(cand) or "NONE"))

    missing = [f for f in sorted(required)
               if not (os.path.isfile(os.path.join(d, "0", f))
                       or os.path.isfile(os.path.join(d, "0", f + ".gz")))]
    if missing:
        return 1, ("ABORT: field(s) %s required by the consumer (fvSolution "
                   "solver blocks INTERSECT closure %r) are ABSENT from %s/0/ "
                   "-- neither X nor X.gz" % (", ".join(missing), model, d))
    return 0, ("FIELD COMPLETENESS OK: closure=%s required={%s} all present in 0/"
               % (model, ", ".join(sorted(required))))


# --------------------------------------------------------------------------
# SELFTEST.  Every clause is DRIVEN: a planted failure that FLIPS it, beside a
# clean control.  Sanaa's section 1 rule -- a guard nobody drove is decoration.
# --------------------------------------------------------------------------
FVSOLUTION_007 = """FoamFile { version 2.0; format ascii; class dictionary; object fvSolution; }
solvers
{
    p_rgh
    {
        solver petsc;
        petsc
        {
            options { ksp_type cg; pc_type jacobi; }
            caching { matrix { update always; } }
        }
        tolerance 1e-9; relTol 0.01;
    }
    "(U|h|k|epsilon)"
    {
        solver petsc;
        petsc
        {
            options { ksp_type bcgs; pc_type jacobi; }
        }
        tolerance 1e-9; relTol 0.1;
    }
}
SIMPLE { nNonOrthogonalCorrectors 0; }
"""

# BUG1-A: nesting KEPT, key and brace on ONE line.
FVSOLUTION_ONELINE = FVSOLUTION_007.replace("p_rgh\n    {", "p_rgh {").replace(
    '"(U|h|k|epsilon)"\n    {', '"(U|h|k|epsilon)" {')
# BUG1-B: nesting REMOVED entirely, key still on its own line.
FVSOLUTION_FLAT = """FoamFile { version 2.0; format ascii; class dictionary; object fvSolution; }
solvers
{
    p_rgh
    {
        solver PCG; tolerance 1e-9; relTol 0.01;
    }
    "(U|h|k|epsilon)"
    {
        solver PBiCGStab; tolerance 1e-9; relTol 0.1;
    }
}
"""
TURB_KE = ("FoamFile { version 2.0; format ascii; class dictionary; object "
           "turbulenceProperties; }\nsimulationType RAS;\n"
           "RAS { RASModel kEpsilon; turbulence on; }\n")

FIELDS = ["T", "U", "alphat", "epsilon", "k", "nut", "p", "p_rgh"]


def _fixture(root, name, fvsolution=FVSOLUTION_007, turb=TURB_KE, drop=()):
    d = os.path.join(root, name)
    os.makedirs(os.path.join(d, "0"))
    os.makedirs(os.path.join(d, "system"))
    os.makedirs(os.path.join(d, "constant"))
    open(os.path.join(d, "system", "fvSolution"), "w").write(fvsolution)
    open(os.path.join(d, "constant", "turbulenceProperties"), "w").write(turb)
    for f in FIELDS:
        if f in drop:
            continue
        open(os.path.join(d, "0", f), "w").write("// fixture field %s\n" % f)
    return d


def selftest():
    import tempfile
    root = tempfile.mkdtemp(prefix="fieldcomp_selftest_")
    results = []

    def arm(label, ok_expected, rc, msg, must_contain=()):
        good = (rc == 0) if ok_expected else (rc != 0)
        for s in must_contain:
            if s not in msg:
                good = False
                msg = msg + "   [MISSING EXPECTED SUBSTRING %r]" % s
        results.append((good, label, rc, msg))

    # ---- CONTROL: the repaired guard on a clean buoyant case ----------------
    clean = _fixture(root, "clean")
    rc, msg = check(clean)
    arm("CONTROL clean VMFLGPU007-shaped case -> OK, NON-EMPTY set naming p_rgh",
        True, rc, msg,
        ("required={T, U, epsilon, k, p_rgh}",))

    # ---- BUG 1: the flip -----------------------------------------------------
    rc, msg = check(clean, legacy_newline_clear=True)
    arm("BUG1 REPRODUCED: ancestor parser on the SAME clean case -> refuses, "
        "empty set (it would have printed OK before the vacuity clause)",
        False, rc, msg, ("required field set is EMPTY",))

    nok = _fixture(root, "no_k", drop=("k",))
    rc, msg = check(nok, legacy_newline_clear=True)
    arm("BUG1 FLIP, ancestor arm: 0/k REMOVED, ancestor parser -> does NOT "
        "name k (it parsed nothing)", False, rc, msg,
        ("required field set is EMPTY",))
    rc, msg = check(nok)
    arm("BUG1 FLIP, repaired arm: 0/k REMOVED -> ABORT NAMING k",
        False, rc, msg, ("ABORT: field(s) k", "ABSENT"))

    # ---- BUG 1 A/B: the cause is NOT the nested petsc blocks -----------------
    ab_a = _fixture(root, "ab_a", fvsolution=FVSOLUTION_ONELINE)
    rc, msg = check(ab_a, legacy_newline_clear=True)
    arm("BUG1-A discriminator: nesting KEPT, key+brace on ONE line -> ancestor "
        "WORKS (so the nesting was never the cause)", True, rc, msg,
        ("p_rgh",))
    ab_b = _fixture(root, "ab_b", fvsolution=FVSOLUTION_FLAT)
    rc, msg = check(ab_b, legacy_newline_clear=True)
    arm("BUG1-B discriminator: nesting REMOVED, key on its own line -> ancestor "
        "STILL FAILS (so the newline was always the cause)", False, rc, msg,
        ("required field set is EMPTY",))
    rc, msg = check(ab_b)
    arm("BUG1-B, repaired -> OK", True, rc, msg, ("p_rgh",))

    # ---- BUG 2: the flip -----------------------------------------------------
    noprgh = _fixture(root, "no_p_rgh", drop=("p_rgh",))
    rc, msg = check(noprgh, legacy_base=True)
    arm("BUG2 FLIP, legacy-base arm: 0/p_rgh REMOVED, base={p,U} -> SAILS "
        "THROUGH (p_rgh never required)", True, rc, msg)
    rc, msg = check(noprgh)
    arm("BUG2 FLIP, repaired arm: 0/p_rgh REMOVED -> ABORT NAMING p_rgh",
        False, rc, msg, ("ABORT: field(s) p_rgh", "ABSENT"))

    # ---- the energy primitive ------------------------------------------------
    not_ = _fixture(root, "no_T", drop=("T",))
    rc, msg = check(not_)
    arm("ENERGY PRIMITIVE: 0/T REMOVED while the consumer solves h -> ABORT "
        "NAMING T", False, rc, msg, ("ABORT: field(s) T", "ABSENT"))
    rc, msg = check(clean)
    arm("ENERGY PRIMITIVE: `h` is NEVER required by name (0/h does not exist "
        "in the clean fixture and it still passes)", True, rc, msg)

    # ---- BUG 3: the flip, FOUND BY DRIVING ----------------------------------
    rc, msg = check(clean, legacy_line_anchor=True)
    arm("BUG3 FLIP, ancestor arm: RAS block written INLINE (as VMFLGPU007's own "
        "turbulenceProperties is) -> ancestor ABORTS on closure 'RAS'",
        False, rc, msg, ("closure 'RAS' is not in this guard's registered",))
    rc, msg = check(clean)
    arm("BUG3 FLIP, repaired arm: same inline RAS block -> closure read as "
        "kEpsilon and the case passes", True, rc, msg, ("closure=kEpsilon",))

    # ---- the surviving refusals ---------------------------------------------
    bad = _fixture(root, "bad_closure",
                   turb="simulationType RAS;\nRAS { RASModel qEpsilon; }\n")
    rc, msg = check(bad)
    arm("UNREGISTERED CLOSURE -> ABORT, no guess", False, rc, msg,
        ("not in this guard's registered closure map",))
    nos = _fixture(root, "no_solvers", fvsolution="FoamFile { }\nSIMPLE { }\n")
    rc, msg = check(nos)
    arm("NO solvers BLOCK -> ABORT", False, rc, msg, ("no solvers block",))
    unb = _fixture(root, "unbalanced",
                   fvsolution="solvers\n{\n    p_rgh\n    {\n        solver PCG;\n")
    rc, msg = check(unb)
    arm("UNBALANCED solvers BLOCK -> ABORT", False, rc, msg,
        ("unbalanced solvers block",))
    rc, msg = check(os.path.join(root, "does_not_exist"))
    arm("NO fvSolution AT ALL -> ABORT", False, rc, msg, ("no system/fvSolution",))

    ok = True
    for good, label, rc, msg in results:
        print("%s  %s" % ("PASS" if good else "**FAIL**", label))
        print("        rc=%d  %s" % (rc, msg.replace("\n", " ")))
        ok = ok and good
    print("")
    print("%d/%d arms behaved as registered%s"
          % (sum(1 for g, _, _, _ in results if g), len(results),
             "" if ok else "   -- SELFTEST FAILED"))
    print("optimisation: __debug__=%s (this guard contains no `assert`, so it "
          "is byte-identical in effect under python3 -O)" % __debug__)
    return 0 if ok else 1


def main(argv):
    if len(argv) == 2 and argv[1] == "--selftest":
        return selftest()
    if len(argv) != 2:
        print("usage: field_completeness.py <case_dir> | --selftest")
        return 2
    rc, msg = check(argv[1])
    print(msg)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
