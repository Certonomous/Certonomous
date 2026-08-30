#!/usr/bin/env python3
"""AV2RG EVIDENCE DUMP -- writes the FULL grade payload the frozen comparator's `main()`
drops for brevity (`av2rg_grade.py` pops the "grade" key before serialising).

ADOPTED VERBATIM IN SHAPE from `curriculum_AVWC/avwc_dump_full_grades.py` -- same cross-check
discipline, same refusal, only the module and file names differ.

It changes NOTHING about the grading: it calls the SAME frozen `regrade()` and writes what
that function returned.  It then CROSS-CHECKS every field the two artefacts share -- verdict,
names_rebound, repairs_applied, root_manifest_identical, refusal -- against
`AV2RG_regrade.json` and REFUSES if any of them differ, so this file cannot quietly become a
second, softer reading of the same run.  Read `AV2RG_regrade.json` as the verdict of record;
read this one for the gate detail behind it.  No `assert` (L-332).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import av2rg_grade as G                                                    # noqa: E402

SHARED = ("verdict", "names_rebound", "repairs_applied", "root_manifest_identical", "refusal")


def main():
    tmp = sys.argv[1] if len(sys.argv) > 1 else "/tmp"
    out = os.path.join(HERE, "AV2RG_full_grades.json")
    ref = json.load(open(os.path.join(HERE, "AV2RG_regrade.json")))
    d = os.path.join(tmp, "av2rg_dump_%d" % os.getpid())
    os.makedirs(d, exist_ok=True)
    res = {}
    for it in sorted(G.ITEMS):
        r = G.regrade(it, d, tag="real")
        for k in SHARED:
            if r.get(k) != ref[it].get(k):
                print("REFUSAL: %s field %r disagrees with AV2RG_regrade.json: %r vs %r"
                      % (it, k, r.get(k), ref[it].get(k)))
                return 2
        res[it] = r
        print("%-5s %-13s rebound=%s cross-checked on %d shared fields"
              % (it, r["verdict"], r["names_rebound"], len(SHARED)))
    json.dump(res, open(out, "w"), indent=1, default=str)
    print("WROTE %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
