#!/usr/bin/env python3
"""
Turn E4a2 STATUS files into DONE markers under the STRICT completion rule
(CLAUDE.md rule 4).

The rule itself is NOT re-implemented here: the frozen mark_done_e4a.check()
is IMPORTED and reused through the restoring `in_dir` redirect of its
module-level HERE (the with_ratio / T10aR in_tree precedent), so E4a2 is
certified by exactly the same six tests, byte-for-byte the same code:
  1. STATUS.<case> exists and reports rc=0
  2. log.solve ends with OpenFOAM's own "End" line
  3. the last written time directory equals the controlDict endTime (60000)
  4. that time directory carries p, U and phi
  5. the number of ExecutionTime lines equals endTime
  6. every field in that time directory is NEWER than the case's own 0/U
     (the age guard: run_one_e4a2.sh re-copies 0/ from 0.orig at the start of
     the run that is allowed to answer)
All five cases are required; there is no optional case.  The frozen file is
never edited (rule 6), and its HERE is asserted restored afterwards.
"""
import sys
sys.dont_write_bytecode = True          # no __pycache__ in any frozen tree

import hashlib                                                     # noqa: E402
import json                                                        # noqa: E402
import os                                                          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TFAM = os.path.dirname(HERE)
E4_DIR = os.path.join(TFAM, "E4_runs")
sys.path.insert(0, E4_DIR)
import mark_done_e4a as MD                            # noqa: E402  FROZEN

REG = json.load(open(os.path.join(HERE, "E4a2_registered.json")))
CASES = sorted(REG["cases"])
EXIT_REFUSE = 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


class in_dir:
    def __init__(self, mod, path):
        self.mod, self.path = mod, path

    def __enter__(self):
        self.old = self.mod.HERE
        self.mod.HERE = self.path
        return self

    def __exit__(self, *a):
        self.mod.HERE = self.old
        return False


def main():
    if HERE == MD.HERE:
        refuse("this marker resolves to E4a's own run tree")
    for rel, want in REG["frozen_instruments"].items():
        got = sha256_of(os.path.join(TFAM, rel))
        if got != want:
            refuse(f"frozen instrument {rel} hashes {got}, registered {want}")
    if sorted(MD.CASES) != CASES:
        refuse(f"frozen case list {sorted(MD.CASES)} != registered {CASES}")
    if tuple(MD.NEEDED) != ("p", "U", "phi"):
        refuse(f"frozen field set {MD.NEEDED} is not (p, U, phi)")
    ok, bad = [], {}
    with in_dir(MD, HERE):
        for c in CASES:
            f = MD.check(c)                                     # FROZEN
            (ok.append(c) if not f else bad.setdefault(c, f))
    if MD.HERE != E4_DIR:
        refuse("in_dir did not restore the frozen module's HERE")
    for c in ok:
        open(os.path.join(HERE, f"DONE.{c}"), "w").write("strict rule met\n")
    print(f"{len(ok)}/{len(CASES)} cases meet the strict completion rule "
          f"(frozen mark_done_e4a.check, endTime {REG['time']['endTime']}): "
          f"{' '.join(ok)}")
    for c in sorted(bad):
        print(f"  NOT DONE  {c}")
        for r in bad[c]:
            print(f"            - {r}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
