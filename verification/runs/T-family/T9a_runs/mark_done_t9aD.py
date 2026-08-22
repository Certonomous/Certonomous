#!/usr/bin/env python3
"""
Turn T9a-D STATUS files into DONE markers under the STRICT RULE, which is
IMPORTED from the frozen mark_done_t9a.py rather than restated.

The frozen module hard-codes T9a's seven case names in a module-level CASES
list; its check() function does not read that list.  So this file imports the
frozen check() unchanged and drives it over the T9a-D case list.  Nothing in
the frozen file is edited and its six tests are the ones that apply:

  1. STATUS.<case> exists and reports rc=0
  2. log.solve ends with OpenFOAM's own "End" line
  3. the last written time directory equals the controlDict endTime
  4. that time directory carries every field the comparator reads (T, DT)
  5. the number of ExecutionTime lines equals endTime
  6. every field in that time directory is NEWER than the case's own 0/T

Anything short of that gets no marker, and analyse_t9aD.py refuses.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mark_done_t9a as M          # frozen, imported, never edited

CASES = list(json.load(open(os.path.join(HERE, "T9aD_registered.json")))["cases"])

def main():
    ok, bad = [], {}
    for c in CASES:
        f = M.check(c)             # THE FROZEN STRICT RULE, unmodified
        (ok.append(c) if not f else bad.setdefault(c, f))
    for c in ok:
        open(os.path.join(HERE, f"DONE.{c}"), "w").write("strict rule met\n")
    print(f"{len(ok)}/{len(CASES)} cases meet the strict completion rule: {' '.join(ok)}")
    for c in sorted(bad):
        print(f"  NOT DONE  {c}")
        for r in bad[c]:
            print(f"            - {r}")
    return 0 if not bad else 1

if __name__ == "__main__":
    sys.exit(main())
