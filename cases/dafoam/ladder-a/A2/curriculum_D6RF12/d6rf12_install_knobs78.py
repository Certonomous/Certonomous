#!/usr/bin/env python3
"""D6RF12 -- install knobs 7-8 (THE nuTilda REPAIR) into a staged fvSolution.

SIX VALUES, TWO NAMED BLOCKS, AND NOTHING ELSE (PREREGISTRATION.md section 3),
carried from cases/dafoam/ladder-a/A2/curriculum_D6RF7/d6rf7_fvSolution, whose
:80 names itself "THIS IS THE nuTilda REPAIR (D6RF4 section 1.5)".

  "(p|p_rgh|G)"  GAMG          relTol 0.1 -> 0.001 ; tolerance 0 -> 1e-12 ; + minIter 5
  "(U|T|...)"    smoothSolver  relTol 0.1 -> 0.001 ; tolerance 0 -> 1e-09 ; nSweeps 1 -> 3

THE `Phi` BLOCK IS NOT TOUCHED -- it carries relTol 0 / tolerance 1e-6 and is the
potential-flow initialiser, not the SIMPLE loop.

L-221/L-222: EVERY VALUE IS INSERTED WITH AN ASSERT, NEVER REPLACED BLINDLY, and the
assert reads the file BACK FROM DISK after writing.  A swap that swapped nothing is a
refusal, not a success.
"""
import re, sys

GAMG_BLOCK = '"(p|p_rgh|G)"'
SMOOTH_BLOCK = '"(U|T|e|h|nuTilda|k|omega|epsilon)"'
WANT = {GAMG_BLOCK:   {"relTol": "0.001", "tolerance": "1e-12", "minIter": "5"},
        SMOOTH_BLOCK: {"relTol": "0.001", "tolerance": "1e-09", "nSweeps": "3"}}


def block_span(text, header):
    i = text.find(header)
    if i < 0:
        return None
    o = text.find("{", i)
    if o < 0:
        return None
    depth, j = 0, o
    while j < len(text):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return (o + 1, j)
        j += 1
    return None


def patch_block(text, header, want):
    span = block_span(text, header)
    if span is None:
        print("D6RF12_KNOBS_ABORT block %s not found" % header); sys.exit(5)
    a, b = span
    body, changed = text[a:b], 0
    for key, val in want.items():
        rx = re.compile(r"^(\s*)%s(\s+)\S+;" % re.escape(key), re.M)
        if rx.search(body):
            body, n = rx.subn(lambda m: "%s%s%s%s;" % (m.group(1), key, m.group(2), val), body)
            changed += n
        else:
            body = body.rstrip() + "\n        %-30s %s;\n    " % (key, val)   # INSERTED, not replaced
            changed += 1
    return text[:a] + body + text[b:], changed


def main(path):
    src = open(path).read()
    total = 0
    for header, want in WANT.items():
        src, n = patch_block(src, header, want)
        total += n
    if total != 6:
        print("D6RF12_KNOBS_ABORT expected 6 edits, made %d" % total); sys.exit(5)
    open(path, "w").write(src)

    # ---- READ BACK FROM DISK.  The assert is on the file, never on the buffer.
    back = open(path).read()
    bad = []
    for header, want in WANT.items():
        a, b = block_span(back, header)
        body = back[a:b]
        for key, val in want.items():
            if not re.search(r"^\s*%s\s+%s;" % (re.escape(key), re.escape(val)), body, re.M):
                bad.append("%s/%s != %s" % (header, key, val))
    # the Phi block must be UNTOUCHED
    pa, pb = block_span(back, "\n    Phi")
    phi = back[pa:pb]
    if not (re.search(r"relTol\s+0;", phi) and re.search(r"tolerance\s+1e-6;", phi)):
        bad.append("Phi block was modified -- it must not be")
    if bad:
        print("D6RF12_KNOBS_ABORT read-back failed: %s" % "; ".join(bad)); sys.exit(5)
    print("D6RF12_KNOBS78_INSTALLED sites=6 file=%s  "
          "GAMG[relTol 0.001 tolerance 1e-12 minIter 5]  "
          "smoothSolver[relTol 0.001 tolerance 1e-09 nSweeps 3]  Phi untouched" % path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
