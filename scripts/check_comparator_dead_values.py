#!/usr/bin/env python3
"""
check_comparator_dead_values.py -- FREEZE-TIME QUESTION 3.

  usage: check_comparator_dead_values.py <comparator.py> [<comparator.py> ...]
         check_comparator_dead_values.py --selftest

WHEN A REGISTRATION NAMES A COMPARATOR, THE LANE FREEZING IT RUNS THIS ON THAT COMPARATOR.
It costs a second, it runs where the reader who would be misled is actually reading, and a
dead prefix-variant can still be repaired BEFORE anything is pinned.

WHAT IT LOOKS FOR, and it is deliberately NARROW.  Not "assigned and never read" -- that is
348 occurrences across 55 % of this lab's graders and most are harmless.  The reportable
shape is the one that misleads:

    A NAME ASSIGNED AND NEVER READ WHOSE SPELLING IS A PREFIX-EXTENSION OF A NAME THAT *IS*
    READ IN THE SAME FUNCTION.

That is the `dloc_c` / `dloc` shape: two variants of one quantity, one live and one dead, so
a reader tracing which quantity a gate consumes can land on the wrong one.  It is not a
hypothesis -- it is what nearly happened while tracing this lab's own M6 shock assert.

EXIT CODES
  0  no strict-set occurrence in the named files
  1  at least one occurrence -- REPORTED, NOT REFUSED.  This check INFORMS a freeze; it does
     not block one.  A `dropped`-shaped duplicate is harmless and the lane says so in the
     registration; a genuine mis-wiring is repaired before the pin.
  2  usage error, or the SELFTEST FAILED

THE SELFTEST IS A PLANTED CONTROL (CLAUDE.md rule 3).  It requires this checker to FIND a
known-true instance and to NOT report three known-live names.  A checker not shown able to
see a non-zero is not evidence, and its clean report on your comparator would be worthless.
Provenance: docs/standards/MONITOR_STANDARD.md sections 2a and 2b.
"""
import ast
import sys
import pathlib

MIN_LEN = 4          # both names; below this, prefix relations are short-name coincidence
MAX_LEN_DIFF = 2     # 'dloc' -> 'dloc_c' is 2


def dead_prefix_variants(path):
    """[(function, dead_name, lineno, [live names it extends or is extended by])]"""
    try:
        tree = ast.parse(pathlib.Path(path).read_text(errors="replace"))
    except (OSError, SyntaxError) as e:
        return None, str(e)
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        stored, loaded, skip = {}, set(), set()
        for n in ast.walk(node):
            if isinstance(n, ast.Name):
                if isinstance(n.ctx, ast.Store):
                    stored.setdefault(n.id, n.lineno)
                else:
                    loaded.add(n.id)
            elif isinstance(n, ast.AugAssign) and isinstance(n.target, ast.Name):
                loaded.add(n.target.id)
            elif isinstance(n, (ast.Global, ast.Nonlocal)):
                loaded.update(n.names)
            elif isinstance(n, (ast.For, ast.AsyncFor)):
                skip.update(t.id for t in ast.walk(n.target) if isinstance(t, ast.Name))
            elif isinstance(n, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                for g in n.generators:
                    skip.update(t.id for t in ast.walk(g.target) if isinstance(t, ast.Name))
            elif isinstance(n, ast.ExceptHandler) and n.name:
                skip.add(n.name)
            elif isinstance(n, ast.withitem) and n.optional_vars is not None:
                skip.update(t.id for t in ast.walk(n.optional_vars) if isinstance(t, ast.Name))
        for name, ln in stored.items():
            if name in loaded or name in skip or name.startswith("_") or len(name) < MIN_LEN:
                continue
            near = sorted(
                lv for lv in loaded
                if lv != name and len(lv) >= MIN_LEN
                and (lv.startswith(name) or name.startswith(lv))
                and abs(len(lv) - len(name)) <= MAX_LEN_DIFF
            )
            if near:
                out.append((node.name, name, ln, near))
    return out, None


def selftest():
    """PLANTED CONTROL: the checker must SEE a known-true instance and must NOT invent one."""
    ok = True
    known = "scripts/grade_m6_agard_cp.py"
    if not pathlib.Path(known).is_file():
        print("SELFTEST INCONCLUSIVE: %s not present; the control has no referent." % known)
        return 2
    hits, err = dead_prefix_variants(known)
    if err:
        print("SELFTEST FAIL: could not parse %s: %s" % (known, err)); return 2
    names = {h[1] for h in hits}
    # POSITIVE limb -- both known-true instances, found by hand and by sweep respectively
    for want in ("dloc_c", "dropped"):
        good = want in names
        print("  POSITIVE  %-8s expected FOUND    -> %s" % (want, "FOUND" if good else "MISSING"))
        ok &= good
    # NEGATIVE limb -- names that ARE read must never be reported
    for live in ("dloc", "rise", "devs"):
        bad = live in names
        print("  NEGATIVE  %-8s expected ABSENT   -> %s" % (live, "REPORTED (WRONG)" if bad else "absent"))
        ok &= not bad
    print("SELFTEST %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 2


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip().split("\n\n")[1], file=sys.stderr); return 2
    if argv[1] == "--selftest":
        return selftest()
    found = 0
    for p in argv[1:]:
        hits, err = dead_prefix_variants(p)
        if err:
            print("%s: COULD NOT PARSE -- %s" % (p, err)); found += 1; continue
        if not hits:
            print("%s: clean (no assigned-and-never-read prefix-variant of a live name)" % p)
            continue
        for fn, name, ln, near in sorted(hits, key=lambda t: t[2]):
            print("%s:%d  in %s()  DEAD %r  <->  LIVE %s" % (p, ln, fn, name, ", ".join(near)))
            found += 1
    if found:
        print("\n%d occurrence(s). REPORTED, NOT REFUSED: this informs the freeze, it does not "
              "block it. Say in the registration which are harmless duplicates and repair any "
              "that are not, BEFORE the pin." % found)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
