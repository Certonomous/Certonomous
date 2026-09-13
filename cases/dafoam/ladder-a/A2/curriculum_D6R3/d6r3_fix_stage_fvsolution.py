#!/usr/bin/env python3
"""D6R3 FIX ARMS -- the ONLY instrument allowed to edit fvSolution for arms FIX_RELTOL1 and
FIX_NONGAMG1.  Registered by D6R3_FIX_PREREGISTRATION.md before any compute (rule 2).

It edits INSIDE the "(p|p_rgh|G)" solvers block and nowhere else, and it ASSERTS that -- a bare
sed on `relTol 0.1` would also hit the "(U|T|e|h|nuTilda|k|omega|epsilon)" block, which must not
move.  It refuses (exit 2) rather than degrade.

usage: d6r3_fix_stage_fvsolution.py <fvSolution> <reltol|nongamg> <value>
"""
import re
import sys

RELTOL_NEW = "2.008e-03"   # frozen by D6R3_FIX_PREREGISTRATION.md section 3; 0.1/(R*S)

def fail(msg):
    sys.stderr.write("D6R3_FIX_STAGE REFUSE: %s\n" % msg)
    sys.exit(2)

def main():
    if len(sys.argv) != 4:
        fail("usage: <fvSolution> <reltol|nongamg> <value>")
    path, mode, value = sys.argv[1], sys.argv[2], sys.argv[3]
    src = open(path).read()
    lines = src.splitlines(True)

    # --- locate the p block, by header then brace depth.  Nothing outside it may be touched. ---
    hdr = None
    for i, ln in enumerate(lines):
        if ln.strip() == '"(p|p_rgh|G)"':
            if hdr is not None:
                fail("two p-block headers in %s" % path)
            hdr = i
    if hdr is None:
        fail("no \"(p|p_rgh|G)\" header in %s" % path)
    if lines[hdr + 1].strip() != "{":
        fail("p-block header is not followed by '{'")
    depth, end = 0, None
    for i in range(hdr + 1, len(lines)):
        depth += lines[i].count("{") - lines[i].count("}")
        if depth == 0:
            end = i
            break
    if end is None:
        fail("p block is not closed")
    lo, hi = hdr + 1, end          # [lo, hi] inclusive: the braces and their contents

    # --- the pre-edit state, asserted, so a file that is not the published one is refused -------
    before_reltol01 = [i for i, ln in enumerate(lines) if re.match(r"\s*relTol\s+0\.1;\s*$", ln)]
    if len(before_reltol01) != 2:
        fail("expected exactly 2 `relTol 0.1;` lines in the published fvSolution, found %d"
             % len(before_reltol01))
    in_p = [i for i in before_reltol01 if lo <= i <= hi]
    out_p = [i for i in before_reltol01 if not (lo <= i <= hi)]
    if len(in_p) != 1 or len(out_p) != 1:
        fail("the two `relTol 0.1;` lines are not one inside and one outside the p block")

    changed = []
    if mode == "reltol":
        if value != RELTOL_NEW:
            fail("value %s is not the frozen %s" % (value, RELTOL_NEW))
        i = in_p[0]
        old = lines[i]
        lines[i] = re.sub(r"(relTol\s+)0\.1;", r"\g<1>%s;" % value, old)
        changed.append((i, old, lines[i]))
        # DIRECTION ASSERT: the staged value must be STRICTLY TIGHTER than the published 0.1.
        if float(value) >= 0.1:
            fail("staged relTol %s is not tighter than the published 0.1 -- refusing to loosen"
                 % value)
    elif mode == "nongamg":
        got_solver = got_smoother = False
        for i in range(lo, hi + 1):
            if re.match(r"\s*solver\s+GAMG;\s*$", lines[i]):
                old = lines[i]
                lines[i] = re.sub(r"(solver\s+)GAMG;", r"\g<1>%s;" % value, old)
                changed.append((i, old, lines[i])); got_solver = True
            elif re.match(r"\s*smoother\s+GaussSeidel;\s*$", lines[i]):
                old = lines[i]
                lines[i] = re.sub(r"(\s*)smoother(\s+)GaussSeidel;",
                                  r"\g<1>preconditioner\g<2>diagonal;", old)
                changed.append((i, old, lines[i])); got_smoother = True
        if not (got_solver and got_smoother):
            fail("nongamg: solver=%s smoother=%s -- both required" % (got_solver, got_smoother))
        if value == "GAMG":
            fail("nongamg: the replacement solver is still GAMG")
    else:
        fail("unknown mode %s" % mode)

    # --- the post-edit state, asserted --------------------------------------------------------
    after = "".join(lines)
    after_lines = after.splitlines(True)
    still01 = [i for i, ln in enumerate(after_lines) if re.match(r"\s*relTol\s+0\.1;\s*$", ln)]
    if mode == "reltol":
        if len(still01) != 1:
            fail("after the edit there are %d `relTol 0.1;` lines, expected 1 (the U block)"
                 % len(still01))
        if lo <= still01[0] <= hi:
            fail("the surviving `relTol 0.1;` is INSIDE the p block -- the wrong line was edited")
        if ("relTol                         %s;" % RELTOL_NEW) not in after:
            fail("the tightened relTol is not readable back from the edited text")
    else:
        if len(still01) != 2:
            fail("nongamg must not move either `relTol 0.1;` line; found %d" % len(still01))
        if not any(lo <= i <= hi for i in still01):
            fail("nongamg moved the p block's relTol -- it must stay at the published 0.1")

    # nothing outside [lo,hi] may have changed
    for i, ln in enumerate(lines):
        if not (lo <= i <= hi) and ln != src.splitlines(True)[i]:
            fail("line %d, outside the p block, changed" % (i + 1))

    open(path, "w").write(after)
    for i, old, new in changed:
        print("D6R3_FIX_STAGE line %d: %s -> %s" % (i + 1, old.strip(), new.strip()))
    print("D6R3_FIX_STAGE OK mode=%s file=%s edits=%d p_block_lines=%d-%d"
          % (mode, path, len(changed), lo + 1, hi + 1))

if __name__ == "__main__":
    main()
