#!/usr/bin/env python3
"""VMFLGPU005 field-completeness guard (frozen). REFUSES (exit 1, NAMED message)
if the staged case is missing a field the solver integrates or an fvSolution
solvers entry for it. buoyantBoussinesqSimpleFoam + standard k-omega integrates
T, U, p_rgh, k, omega (nut, alphat, p are derived, not solved).

    field_completeness.py <case_dir>

Ancestry note (L-342 lineage): the VMFLGPU007 ancestor hard-coded a {p,U} base
set that could not see p_rgh, cleared its required set at the newline before the
brace, and line-anchored its closure lookup so it missed an inline RAS{...} form.
This version hard-codes the ACTUAL k-omega thermal set, reads the RASModel from
either an inline or a multi-line RAS block, and REFUSES an empty required set
rather than certifying it.
"""
import os
import re
import sys

SOLVED_FIELDS = ("T", "U", "p_rgh", "k", "omega")  # buoyantBoussinesqSimpleFoam + kOmega


def die(msg):
    sys.stderr.write("REFUSE (field_completeness VMFLGPU005): %s\n" % msg)
    sys.exit(1)


def has_field(zerodir, f):
    return os.path.isfile(os.path.join(zerodir, f)) or os.path.isfile(os.path.join(zerodir, f + ".gz"))


def main(argv):
    if len(argv) != 2:
        die("usage: field_completeness.py <case_dir>")
    case = argv[1]
    zerod = os.path.join(case, "0")
    if not os.path.isdir(zerod):
        die("no 0/ directory under %s" % case)

    # Confirm the turbulence model is the frozen one (inline or multi-line RAS).
    tp = os.path.join(case, "constant", "turbulenceProperties")
    if not os.path.isfile(tp):
        die("no constant/turbulenceProperties under %s" % case)
    tptxt = open(tp).read()
    m = re.search(r"RASModel\s+(\w+)", tptxt)
    if not m:
        die("could not read RASModel from %s (neither inline nor multi-line RAS "
            "block matched)" % tp)
    if m.group(1) != "kOmega":
        die("RASModel is %r, not the frozen kOmega -- the field set this guard "
            "enforces is model-specific and does not certify a different model"
            % m.group(1))

    required = list(SOLVED_FIELDS)
    if not required:
        die("the required-field set is EMPTY; refusing rather than certifying "
            "nothing (the ancestor's exact failure)")

    missing = [f for f in required if not has_field(zerod, f)]
    if missing:
        die("field(s) %s absent from %s (neither X nor X.gz)"
            % (", ".join(missing), zerod))

    # Every solved field must have an fvSolution solvers entry (literal or regex).
    fvs = os.path.join(case, "system", "fvSolution")
    if not os.path.isfile(fvs):
        die("no system/fvSolution under %s (materialise it before this guard)" % case)
    solt = open(fvs).read()
    sm = re.search(r"solvers\s*\{(.*?)\n\}", solt, re.S)
    if not sm:
        die("no solvers{...} block in %s" % fvs)
    solvers_block = sm.group(1)
    uncovered = []
    for f in required:
        # literal key at line start, or inside a quoted regex group like "(U|T|k|omega)"
        lit = re.search(r'(^|\n)\s*%s\s*\n?\s*\{' % re.escape(f), solvers_block)
        rex = re.search(r'"\([^"]*\b%s\b[^"]*\)"' % re.escape(f), solvers_block)
        if not lit and not rex:
            uncovered.append(f)
    if uncovered:
        die("field(s) %s have no solvers entry in %s (neither a literal key nor a "
            "quoted-regex group covers them), so they would not be solved"
            % (", ".join(uncovered), fvs))

    sys.stderr.write("field_completeness VMFLGPU005: required={%s} all present and "
                     "solved (RASModel kOmega)\n" % ", ".join(required))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
