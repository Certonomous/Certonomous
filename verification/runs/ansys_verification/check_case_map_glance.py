#!/usr/bin/env python3
"""Refuse if CASE_MAP's glance table disagrees with the REGISTER.

WHY.  The glance table DUPLICATES facts derived elsewhere, and a hand-maintained
duplicate of a derived count drifts.  It did: it read "four cases run" while
listing five rows and OMITTING VMFL003 entirely -- under-reporting the campaign
and dropping a NOT A RESULT, which is the FLATTERING direction.
`check_aggregates_moved` protected the tally, the tier cell and the fraction; it
did NOT protect a prose table restating the same facts in a different shape.

WHAT IT CHECKS, AND WHY NOT MORE.  A first version tried to match case IDs across
the two tables.  That is BRITTLE and it FAILED HONESTLY on real data: the register
writes "VMFL001 -- Flow Between..." where the glance table writes "VMFL001 run 1",
and a checker that depends on two hand-written prose spellings agreeing will cry
wolf.  A guard that fires on correct data trains its reader to ignore it (L-315).
So this checks the three things that ACTUALLY DRIFT and that do not depend on id
spelling at all:

  1. ROW COUNT      -- glance rows == register rows.   (VMFL003 went missing)
  2. HEADER COUNT   -- the spelled-out number in the heading == register rows.
                       ("four cases run" while five were listed)
  3. VERDICT MULTISET -- the same verdicts in the same quantities.
                       (a dropped NOT A RESULT changes this even if counts were
                        patched by adding some other row)

THE REGISTER IS THE AUTHORITY; the glance table is a convenience, never a source.

usage: check_case_map_glance.py [--selftest]
"""
import re, subprocess, sys
from collections import Counter

REPO = "/home/ubuntu/Certonomous"
REG  = "verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md"
CMAP = "docs/ansys_verification/CASE_MAP.md"
EXIT_OK, EXIT_REFUSE = 0, 2
VERDICTS = ("NOT A RESULT", "GATE REACHED", "GATE FAIL", "BLOCKED", "PENDING", "PASS")
WORDS = {"ONE":1,"TWO":2,"THREE":3,"FOUR":4,"FIVE":5,"SIX":6,"SEVEN":7,
         "EIGHT":8,"NINE":9,"TEN":10,"ELEVEN":11,"TWELVE":12}
VPAT = re.compile(r"`(" + "|".join(VERDICTS) + r")`")   # longest-first: PASS last


def register_verdicts(text):
    out = []
    for line in text.split("\n"):
        if re.match(r"^\| \*\*\d+\*\* \| \*\*VMFL", line):
            f = line.split("|")
            # DATE-ANCHORED, never a fixed index: register row #7's description
            # contains the regex `"(h|e)"`, a LITERAL PIPE inside a Markdown cell,
            # which shifts every field after it and breaks naive pipe-splitting.
            # The ISO date cell moves with the shift, so anchoring on it survives.
            di = next((i for i, c in enumerate(f)
                       if re.fullmatch(r"\s*\d{4}-\d{2}-\d{2}\s*", c)), None)
            m = VPAT.search(f[di + 1]) if di is not None and di + 1 < len(f) else None
            out.append(m.group(1) if m else None)
    return out


def glance_verdicts(text):
    seg = re.search(r"^### The [A-Z]+ RUNS.*?(?=^### )", text, flags=re.M | re.S)
    if not seg:
        return None, None
    rows = [l for l in seg.group(0).split("\n") if l.startswith("| **VMFL")]
    vs = []
    for l in rows:
        f = l.split("|")
        m = VPAT.search(f[2] if len(f) > 2 else "")
        vs.append(m.group(1) if m else None)
    hdr = re.match(r"^### The ([A-Z]+) RUNS", seg.group(0))
    return vs, (WORDS.get(hdr.group(1)) if hdr else None)


def check(reg_text, cm_text):
    r = register_verdicts(reg_text)
    g, hdr_n = glance_verdicts(cm_text)
    if g is None:
        return ["glance-table heading not found (expected '### The <NUMBER> RUNS')"]
    p = []
    if len(g) != len(r):
        p.append(f"ROW COUNT: register {len(r)}, glance table {len(g)}")
    if hdr_n is not None and hdr_n != len(r):
        p.append(f"HEADER COUNT: heading says {hdr_n}, register has {len(r)}")
    if Counter(g) != Counter(r):
        p.append(f"VERDICT MULTISET: register {dict(Counter(r))} vs glance {dict(Counter(g))}")
    return p


def _selftest():
    reg = ("| **1** | **VMFL001** — x | 2026-08-24 | **`NOT A RESULT`** |\n"
           "| **2** | **VMFL005** — y after its `NOT A RESULT` | 2026-08-24 | **`PASS`** |\n")
    base = ("### The TWO RUNS across x\n\n"
            "| **VMFL001** run 1 | `NOT A RESULT` | t | w |\n"
            "| **VMFL005** | `PASS` | t | w |\n\n### next\n")
    res = []
    def arm(n, got, want, kind):
        res.append((got == want, n, kind, str(got)))
    arm("agree/GOOD", check(reg, base), [], "GOOD-input")
    arm("rowcount/BAD", any("ROW COUNT" in x for x in
        check(reg, base.replace("| **VMFL005** | `PASS` | t | w |\n", ""))), True, "BAD-input")
    arm("rowcount/GOOD", any("ROW COUNT" in x for x in check(reg, base)), False, "GOOD-input")
    arm("header/BAD", any("HEADER COUNT" in x for x in
        check(reg, base.replace("### The TWO RUNS", "### The FOUR RUNS"))), True, "BAD-input")
    arm("header/GOOD", any("HEADER COUNT" in x for x in check(reg, base)), False, "GOOD-input")
    arm("multiset/BAD", any("VERDICT MULTISET" in x for x in
        check(reg, base.replace("| **VMFL005** | `PASS` |", "| **VMFL005** | `GATE FAIL` |"))), True, "BAD-input")
    arm("multiset/GOOD", any("VERDICT MULTISET" in x for x in check(reg, base)), False, "GOOD-input")
    arm("heading/BAD-absent", check(reg, "no table here\n"),
        ["glance-table heading not found (expected '### The <NUMBER> RUNS')"], "BAD-input")
    w = max(len(n) for _, n, _, _ in res)
    for ok, n, k, note in res:
        print(f"  {'PASS' if ok else 'FAIL':4}  {n:<{w}}  {k:<10} {note[:60]}")
    fams = {}
    for _, n, k, _ in res: fams.setdefault(n.split("/")[0], set()).add(k)
    miss = [f for f, ks in fams.items() if {"GOOD-input", "BAD-input"} - ks]
    if miss:
        print(f"  NOTE: single-arm guard(s) {miss} -- heading/BAD-absent has no meaningful good arm")
    if any(not ok for ok, _, _, _ in res):
        print("  REFUSED: an arm failed"); return EXIT_REFUSE
    print("  ALL ARMS PASS"); return EXIT_OK


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    sh = lambda p: subprocess.check_output(["git", "-C", REPO, "show", f"HEAD:{p}"], text=True)
    probs = check(sh(REG), open(f"{REPO}/{CMAP}").read())
    if probs:
        for x in probs: print(f"  REFUSED: {x}")
        sys.exit(EXIT_REFUSE)
    print(f"  glance table AGREES with the register ({len(register_verdicts(sh(REG)))} rows)")
    sys.exit(EXIT_OK)
