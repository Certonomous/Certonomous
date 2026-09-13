#!/usr/bin/env bash
# ===========================================================================
# d6r2c_guard_deps.sh -- THE DEPENDENCY-CLOSURE GUARD, EXTRACTED SO THERE IS
# ONE DEFINITION AND EVERY LAUNCHER CALLS IT (L-221/L-222).
# ===========================================================================
#
# ORIGIN, NAMED RATHER THAN PARAPHRASED:
#   file       cases/dafoam/ladder-a/A2/curriculum_D6R2C/d6r2c_fm6_run_arm.sh
#   md5        cead1008eeb4d151c0ccddae2653d64b   (committed at HEAD)
#   lines      189..222
#   body md5   e4fe26ad6e29900ce4b67255c9ddc9c1
#
# THE FUNCTION BELOW IS THE ORIGIN'S BYTES, VERBATIM AND UNALTERED.  It is NOT
# re-spelled, NOT re-indented and NOT renamed, so the copy can be PROVED equal
# to its origin rather than asserted equal:
#
#   sed -n '189,222p' <origin> | md5sum   ==   e4fe26ad6e29900ce4b67255c9ddc9c1
#
# and any launcher sourcing this file re-runs that comparison as a guard.
#
# WHY EXTRACTED RATHER THAN SOURCED FROM THE ORIGIN: d6r2c_fm6_run_arm.sh is a
# FROZEN instrument that compute has already run against.  Sourcing it would
# execute its top-level code; editing it would touch a frozen file (rule 6).
# Extraction touches nothing frozen and leaves the origin exactly where it is.
#
# THE BANNER STILL READS `D6R2C_FM6_G_DEPS_PASS`.  That is deliberate: it is the
# origin's own byte and changing it would make this copy differ from the file it
# claims to be.  The banner names where the check came from.
#
# CONTRACT: the caller must have $SRC set to the directory holding the staged
# .py files, and passes the staged file list as arguments.
# ===========================================================================

guard_deps() {
  python3 - "$SRC" "$@" <<'DEPSPY'
import ast, os, sys
src, staged = sys.argv[1], sys.argv[2:]
stem = {os.path.splitext(f)[0] for f in staged}
missing, scanned = [], 0
for f in staged:
    if not f.endswith(".py"):
        continue
    p = os.path.join(src, f)
    if not os.path.isfile(p):
        print("ABORT G-DEPS staged file does not exist in SRC: %s" % f)
        sys.exit(1)
    scanned += 1
    tree = ast.parse(open(p).read(), p)
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            mods.add(node.module.split(".")[0])
    for m in sorted(mods):
        # LOCAL means "a file of that name sits in SRC" -- an image module is
        # not this launcher's to stage and is not its to vouch for.
        if os.path.isfile(os.path.join(src, m + ".py")) and m not in stem:
            missing.append("%s imports %s, which is NOT staged" % (f, m))
if missing:
    print("ABORT G-DEPS the staged set does not cover its own imports:")
    for x in missing:
        print("   " + x)
    sys.exit(1)
print("D6R2C_FM6_G_DEPS_PASS scanned=%d staged=%d" % (scanned, len(staged)))
DEPSPY
}
