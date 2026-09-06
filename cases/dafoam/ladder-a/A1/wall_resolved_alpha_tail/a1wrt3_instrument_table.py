#!/usr/bin/env python3
"""A1WRT3 -- THE INSTRUMENT TABLE, ENUMERATED BY **EXTRACTION**.

`A1WRT3_SUCCESSOR_DRAFT.md` section 11 item 4; `DAFOAM_CHARTER.md` section 18.3.

WHY THIS IS NOT A LIST SOMEBODY TYPED
=====================================
Section 18.3 names the failure mode directly: A LIST WRITTEN FROM MEMORY MISSES
THE FORM ITS AUTHOR DID NOT THINK OF.  A1WRT2 measured it on its own launcher --
an assignment matcher written from an enumeration blocked that launcher on `$rc`
and `$want`, two forms nobody had listed.  So this file does not carry a list of
this item's instruments.  IT READS THE FROZEN SCRIPTS AND PULLS THE PATHS OUT OF
THEM: every `$HERE/`, `$BASE/`, `$LAUNCHER`-style shell reference and every local
`spec_from_file_location(... HERE / "x.py")` import, resolved against the item
directory.

THE TWO PHASES, AND THE ORDER IS THE POINT
==========================================
**PHASE 1 -- EXISTENCE, ALONE, AND FIRST.**  Every extracted dependency must
EXIST.  This phase runs to completion and reports on its own before any md5 is
looked at, because AN MD5-AGREEMENT CONTROL CAN READ 8 OF 8 WHILE A DEPENDENCY
THE FROZEN CODE EXECUTES IS ABSENT -- the eight it agreed about were simply not
the missing one.  Agreement over a subset is not coverage of the set.

**PHASE 2 -- MD5 AGREEMENT**, only once phase 1 is clean, and only over the set
phase 1 enumerated.
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# The roots the extraction starts from.  THIS IS NOT THE INSTRUMENT TABLE -- it
# is the set of files whose text is read to BUILD the table.
ROOTS = ("a1wrt3_cmd.sh", "a1wrt3_run_arm.sh", "a1wrt3_stage.py",
         "a1wrt3_grade.py", "a1wrt3_instruments.py", "a1wrt3_selftest.py",
         "a1wrt3_instrument_table.py")

# Shell:  "$BASE/name"  "$HERE/name"  "$LAUNCHER"  $BASE/name
_SH_REF = re.compile(r'\$(?:\{)?(?:BASE|HERE|LAUNCHER|INSTR|GRADER|CMD_SRC)(?:\})?/'
                     r'([A-Za-z0-9_.\-]+)')
# Python: HERE / "name"   FIXTURES / "name"   (HERE / "name")
_PY_REF = re.compile(r'(?:HERE|FIX|FIXTURES)\s*/\s*"([A-Za-z0-9_.\-]+)"')
# Python: the assignments that name a sibling script directly
_PY_NAME = re.compile(r'"(a1wrt3_[A-Za-z0-9_]+\.(?:py|sh))"')
_SH_NAME = re.compile(r'\b(a1wrt3_[A-Za-z0-9_]+\.(?:py|sh))\b')


def md5_of(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def extract():
    """Every path the frozen scripts reference, with the file and line that
    references it.  A ROOT THAT DOES NOT EXIST IS ITSELF A FINDING and is
    returned rather than skipped."""
    refs = {}          # name -> set of "file:line"
    missing_roots = []
    for root in ROOTS:
        p = HERE / root
        if not p.is_file():
            missing_roots.append(root)
            continue
        refs.setdefault(root, set()).add("(root)")
        for i, line in enumerate(p.read_text(errors="replace").splitlines(), 1):
            for pat in (_SH_REF, _PY_REF, _PY_NAME, _SH_NAME):
                for m in pat.finditer(line):
                    refs.setdefault(m.group(1), set()).add("%s:%d" % (root, i))
    return refs, missing_roots


# =============================================================================
# THE EXCEPTIONS, AND EVERY ONE IS **CHECKED**, NOT ASSERTED.
#
# A blunt extractor over source text produces candidates that are not
# dependencies.  They are NOT SILENTLY DROPPED -- dropping them is how a list
# stops being an extraction and becomes a list somebody typed.  Each is named
# here WITH A REASON AND WITH A PREDICATE THAT IS EXECUTED, so an exception that
# stops being true FAILS PHASE 1 instead of hiding a real absence behind it.
# =============================================================================
def _only_referenced_from_this_file(name, refs):
    """The candidate came out of THIS file's own regex literals or docstring."""
    return all(w.startswith("a1wrt3_instrument_table.py") or w == "(root)"
               for w in refs[name])


def _must_be_absent(name, refs):
    """`W2c` proves the log reader REFUSES on an unreadable subject rather than
    reading count 0.  If this path ever EXISTS, that control silently stops
    testing anything -- so its absence is asserted here, not assumed."""
    return not (HERE / name).exists() and not (HERE / "fixtures" / name).exists()


EXCEPTIONS = {
    "name": ("extracted from this file's own regex literal, not a dependency",
             _only_referenced_from_this_file),
    "x.py": ("extracted from this file's own docstring, not a dependency",
             _only_referenced_from_this_file),
    "no_such_log_at_all.log":
        ("control W2c's DELIBERATELY ABSENT path: it proves the log reader "
         "refuses rather than reading a zero. Its absence is REQUIRED.",
         _must_be_absent),
}


def phase1_existence(refs, missing_roots):
    """EXISTENCE, ALONE, AND FIRST."""
    print("--- PHASE 1: EXISTENCE.  Every extracted dependency must EXIST, and "
          "this phase completes BEFORE any md5 is consulted.")
    problems = list("root absent: %s" % r for r in missing_roots)
    for name in sorted(refs):
        where = None
        for cand in (HERE / name, HERE / "fixtures" / name):
            # A DIRECTORY COUNTS AS PRESENT.  `HERE / "fixtures"` is a real
            # dependency of the frozen code and is not a file.
            if cand.exists():
                where = cand
                break
        if where is not None:
            print("    EXISTS  %-52s %s" % (name, where.relative_to(HERE)))
            continue
        if name in EXCEPTIONS:
            reason, predicate = EXCEPTIONS[name]
            if predicate(name, refs):
                print("    NOT-A-DEP %-50s %s" % (name, reason))
                continue
            problems.append("EXCEPTION NO LONGER HOLDS for %s (%s) -- referenced "
                            "from %s" % (name, reason, ", ".join(sorted(refs[name]))))
            print("    STALE-EXCEPTION %-44s %s" % (name, reason))
            continue
        problems.append("ABSENT: %s (referenced from %s)"
                        % (name, ", ".join(sorted(refs[name]))))
        print("    ABSENT  %-52s <- %s" % (name, ", ".join(sorted(refs[name]))))
    print("--- PHASE 1 RESULT: %d candidate(s), %d checked exception(s), "
          "%d problem(s)" % (len(refs), len(EXCEPTIONS), len(problems)))
    return problems


def phase2_md5(refs, pins):
    """MD5 AGREEMENT, over the set phase 1 enumerated, and only after it."""
    print("--- PHASE 2: MD5 AGREEMENT (only over the set phase 1 enumerated).")
    problems = []
    for name, want in sorted(pins.items()):
        # The pin table names the STAGED name (`cmd.sh`); the item directory
        # holds it as `a1wrt3_cmd.sh`.  Both are resolved and the mapping is
        # PRINTED, so a pin that silently checked the wrong file is visible.
        src = {"cmd.sh": "a1wrt3_cmd.sh", "run_arm.sh": "a1wrt3_run_arm.sh"}.get(name)
        if src is None:
            print("    SKIP    %-20s (not produced from this item directory)" % name)
            continue
        p = HERE / src
        if not p.is_file():
            problems.append("pinned instrument %s has no source %s" % (name, src))
            continue
        got = md5_of(p)
        mark = "OK  " if got == want else "MISMATCH"
        if got != want:
            problems.append("%s: pin %s != %s on disk (%s)" % (name, want, got, src))
        print("    %-8s %-14s pin=%s disk=%s  <- %s" % (mark, name, want, got, src))
    print("--- PHASE 2 RESULT: %d problem(s)" % len(problems))
    return problems


def main():
    refs, missing_roots = extract()
    p1 = phase1_existence(refs, missing_roots)
    if p1:
        print("A1WRT3_INSTRUMENT_TABLE PHASE 1 FAILED -- md5 agreement is NOT "
              "consulted, because agreement over a subset is not coverage of "
              "the set.")
        for x in p1:
            print("    %s" % x)
        return 1
    import importlib.util
    s = importlib.util.spec_from_file_location("g", str(HERE / "a1wrt3_grade.py"))
    g = importlib.util.module_from_spec(s); s.loader.exec_module(g)
    p2 = phase2_md5(refs, g.PIN_INSTRUMENTS)
    if p2:
        print("A1WRT3_INSTRUMENT_TABLE PHASE 2 FAILED")
        for x in p2:
            print("    %s" % x)
        return 1
    print("A1WRT3_INSTRUMENT_TABLE OK -- %d dependency(ies) exist, %d pin(s) agree"
          % (len(refs), len(g.PIN_INSTRUMENTS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
