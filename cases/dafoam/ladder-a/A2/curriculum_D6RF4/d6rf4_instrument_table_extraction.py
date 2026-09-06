#!/usr/bin/env python3
"""Curriculum D6RF4 -- THE INSTRUMENT TABLE, EXTRACTED FROM THE CODE.

`DAFOAM_CHARTER.md` section 18.3.  EXISTENCE IS ASSERTED FIRST AND SEPARATELY;
an md5-agreement figure over a subset is NOT evidence the set is complete, at
8 of 8 or at 800 of 800.  `SO2a-DRIVER-DEF-1` is the reason: a gate was frozen
without its implementation and every control the item held reported that all
was well, because the eight pins it compared did not include the file the
driver actually ran.

**IT IS THE EXTRACTION THAT IS BINDING, NOT THE DILIGENCE.**  A prose list names
what its author thought of; a list derived from the code cannot have that
failure mode.  This file writes `d6rf4_instrument_table_extraction.txt` and
NOTHING IN THAT FILE IS TYPED BY HAND.

IT IS A TOOL, NOT AN INSTRUMENT.  `d6rf4_grade.py` neither imports nor executes
it, and it is deliberately NOT in `FROZEN_PATHS`: freezing the thing that
derives the frozen set would make the derivation depend on itself.  The
grader's own `frozen_path_coverage()` is the executable half and runs at every
grading; this is the reader's half and runs at the freeze.

THE EXTRACTOR NOTES CARRIED FROM `D6RF3`, VERBATIM, because that extraction was
wrong three times and each miss is a pattern this one must not repeat:
  (1) v1 matched only quoted literals and `$HERE/x.py`, so it MISSED
      `AGGREGATE_READER="$D6R_CASE_DIR/d6r_aggregate_memory.py"`.
  (2) v2 reported the run-time-generated `d6rf3_cmd.sh` ABSENT; it is
      GENERATED, WITH ITS GENERATING LINE NAMED, rather than suppressed.
  (3) v3 STILL missed `CEILING_GUARD="$HERE/../../../_common/item_ceiling_guard.py"`,
      because the pattern allowed no path SEGMENTS between the variable and the
      file -- blind to the single most important dependency added that day.
      Caught only by asking the finished list whether it contained what had
      just been added, which is the one question a completeness check cannot
      ask itself.

AND ONE NOTE THIS ITEM ADDS:
  (4) NON-`.py` DEPENDENCIES COUNT.  `D6RF4`'s whole claim rests on two
      `fvSolution` files with no extension at all, and a pattern that only
      matched `*.py`/`*.sh` would have been blind to the two files the item is
      ABOUT.  The extractor therefore also collects module-level string
      constants that NAME A FILE PRESENT IN THE ITEM DIRECTORY, whatever its
      extension, and reports how many rows arrived by that route.

NO `assert` STATEMENT APPEARS IN THIS FILE.  `python -O` deletes them.
"""
import ast
import hashlib
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *([os.pardir] * 5)))
OUT = os.path.join(HERE, "d6rf4_instrument_table_extraction.txt")
D6RF3 = os.path.abspath(os.path.join(HERE, os.pardir, "curriculum_D6RF3"))

NAMEISH = re.compile(r'^[A-Za-z0-9_][A-Za-z0-9_.-]*$')
SH_REFS = (
    # $HERE/x.py, $BASE/x.sh, $WORK/a/b/c.py -- SEGMENTS ALLOWED (note 3)
    re.compile(r'\$(?:\{)?(?:HERE|BASE|WORK|D6R_CASE_DIR|LAUNCHER)(?:\})?'
               r'((?:/[A-Za-z0-9_.-]+)+)'),
    # "$SOMEVAR/…/file.py" assigned to a shell variable
    re.compile(r'=\s*"\$\{?[A-Za-z_][A-Za-z0-9_]*\}?((?:/[A-Za-z0-9_.-]+)+)"'),
)
GENERATED = {"d6rf4_cmd.sh": 'written at run time by d6rf4_run_arm.sh '
                            'CMDFILE="$WORK/d6rf4_cmd.sh"'}

# ---- THE LOCAL-DEPENDENCY FILTER, AND ITS OWN GUARD ------------------------
# A raw extraction over these sources collects `os.py`, `numpy.py` and the
# selftest FIXTURE names (`nou0.py`, `zeroscaler.py`, ...) alongside the real
# dependencies.  Section 18.3 is about the files THIS ITEM ships and executes;
# stdlib and site-packages are the image's identity, frozen by DIGEST
# elsewhere, and a fixture name is not a file at all.
#
# BUT A FILTER IS EXACTLY WHAT EXTRACTOR NOTE (3) WARNS ABOUT: it can be blind
# to the newest dependency.  So the filter is GUARDED in two ways, both
# printed: every EXCLUDED name is listed by name and counted, and the
# extraction REFUSES if any excluded name is a file actually present in the
# item directory -- which is the only way a real local dependency could be
# dropped by this rule.
LOCAL_PREFIXES = ("d6rf4_", "d6rf3_", "d6rf2_", "d6rf_", "d6r_", "d6_", "d4_",
                  "item_", "so2a_", "so3_")


def md5_of(p):
    with open(p, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def item_files():
    return {n for n in os.listdir(HERE) if os.path.isfile(os.path.join(HERE, n))}


def declared_in_py(path, present):
    """Module-level string constants that NAME A FILE.  `.py`/`.sh` always;
    any other name only when a file of that name is present in the item
    directory (note 4) -- so `fvSolution` files are caught and English prose is
    not."""
    try:
        tree = ast.parse(open(path, errors="replace").read(), filename=path)
    except SyntaxError:
        return None
    out = set()
    for node in ast.walk(tree):
        vals = []
        if isinstance(node, (ast.Import,)):
            vals = [a.name + ".py" for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            vals = [node.module + ".py"]
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            vals = [node.value]
        for v in vals:
            if not NAMEISH.match(v or ""):
                continue
            if v.endswith((".py", ".sh")) or v in present:
                out.add(v)
    return out


def referenced_in_sh(path, present):
    txt = open(path, errors="replace").read()
    out = set()
    for rx in SH_REFS:
        for m in rx.finditer(txt):
            leaf = m.group(1).rsplit("/", 1)[-1]
            if leaf.endswith((".py", ".sh")) or leaf in present:
                out.add(leaf)
    # bare `python <file>.py` / `bash <file>.sh` inside the container command
    for m in re.finditer(r'\b(?:python3?|bash)\s+([A-Za-z0-9_][\w.-]*\.(?:py|sh))',
                         txt):
        out.add(m.group(1))
    # `cp -a "$BASE/<name>"` where <name> has no extension (the fvSolution pair)
    for m in re.finditer(r'"\$(?:BASE|WORK)/([A-Za-z0-9_][\w.-]*)"', txt):
        if m.group(1) in present:
            out.add(m.group(1))
    return out


def main():
    present = item_files()
    sources = sorted(n for n in present if n.endswith((".py", ".sh")))
    if not sources:
        sys.stderr.write("REFUSE the extractor found ZERO source files in %s. "
                         "A derivation that quietly finds nothing is "
                         "indistinguishable from one that found nothing "
                         "wrong.\n" % HERE)
        return 2

    refs, by_source, unparseable = set(), {}, []
    for n in sources:
        p = os.path.join(HERE, n)
        got = (declared_in_py(p, present) if n.endswith(".py")
               else referenced_in_sh(p, present))
        if got is None:
            unparseable.append(n)
            continue
        by_source[n] = sorted(got)
        refs |= got
    refs |= set(sources)                      # a source is its own dependency

    # ---- the grader's OWN registered sets, read from the module -----------
    sys.path.insert(0, HERE)
    import d6rf4_grade as G                                    # noqa: E402
    cross = dict(G.CROSS_ITEM)
    frozen_rel = list(G.FROZEN_PATHS)
    frozen_names = {p.rsplit("/", 1)[-1] for p in frozen_rel}
    refs |= frozen_names

    def is_local(n):
        return (n in present or n in cross or n in GENERATED
                or n.startswith(LOCAL_PREFIXES))

    excluded = sorted(n for n in refs if not is_local(n))
    # THE FILTER'S OWN GUARD: an excluded name that is a real file here would
    # mean the rule dropped a genuine local dependency.
    dropped_but_present = [n for n in excluded if n in present]
    refs = {n for n in refs if is_local(n)}
    by_source = {k: [x for x in v if is_local(x)] for k, v in by_source.items()}

    def resolve(n):
        p = os.path.join(HERE, n)
        if os.path.isfile(p):
            return p, "item dir"
        if n in cross:
            q = os.path.join(REPO, cross[n])
            if os.path.isfile(q):
                return q, "cross-item: %s" % cross[n]
        if n in GENERATED:
            return None, "GENERATED"
        return None, "ABSENT"

    lines = []
    W = lines.append
    W("D6RF4 INSTRUMENT TABLE -- EXTRACTED, NOT WRITTEN FROM MEMORY")
    W("generated %s  dir %s"
      % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), HERE))
    W("extractor  d6rf4_instrument_table_extraction.py (a TOOL, not an "
      "instrument: the grader neither imports nor executes it, and it is")
    W("           deliberately NOT in FROZEN_PATHS -- freezing the thing that "
      "derives the frozen set would make the derivation")
    W("           depend on itself.  The executable half is "
      "d6rf4_grade.py:frozen_path_coverage(), run at EVERY grading.)")
    W("DAFOAM_CHARTER.md section 18.3: existence is asserted FIRST and "
      "SEPARATELY;")
    W("an md5-agreement figure over a subset is NOT evidence the set is "
      "complete.")
    W("")
    W("EXTRACTOR NOTES (1)-(3) are D6RF3's, carried verbatim; (4) is this "
      "item's own.  See the extractor's docstring.")
    W("  (4) NON-.py DEPENDENCIES COUNT.  This item's whole claim rests on two "
      "fvSolution files with no extension at all.")
    W("      A pattern matching only *.py/*.sh would have been blind to the two "
      "files the item is ABOUT.")
    W("")
    W("=== THE LOCAL-DEPENDENCY FILTER, SHOWN BEFORE IT IS APPLIED ===")
    W("  A raw extraction also collects stdlib/site-packages imports and the")
    W("  selftest FIXTURE names inside these files.  %d name(s) were EXCLUDED"
      % len(excluded))
    W("  as not-local, and they are listed so the filter is auditable rather")
    W("  than trusted (extractor note (3): a filter can be blind to the newest")
    W("  dependency):")
    for i in range(0, len(excluded), 6):
        W("    %s" % "  ".join("%-24s" % n for n in excluded[i:i + 6]))
    W("  EXCLUDED NAMES THAT ARE FILES PRESENT IN THIS DIRECTORY: %s"
      % (" ".join(dropped_but_present) if dropped_but_present
         else "NONE -- the filter dropped no real local dependency"))
    W("")
    W("=== EXISTENCE FIRST ===")
    absent, generated, rows = [], [], []
    for n in sorted(refs):
        p, how = resolve(n)
        if how == "ABSENT":
            absent.append(n)
            W("  ABSENT      %-38s" % n)
        elif how == "GENERATED":
            generated.append(n)
            W("  GENERATED   %-38s (%s)" % (n, GENERATED[n]))
        else:
            extra = ("" if how == "item dir"
                     else "(%s  md5 %s)" % (how, md5_of(p)))
            W("  EXISTS      %-38s %s" % (n, extra or "(item dir)"))
            rows.append((n, p))
    W("  -> %d dependencies referenced; EXISTS or accounted for: %d; ABSENT: %d"
      % (len(refs), len(refs) - len(absent), len(absent)))
    W("")
    if unparseable:
        W("  REFUSE-UNPARSEABLE %s -- what they open cannot be derived, so the "
          "set is UNMEASURED, not assumed empty" % " ".join(unparseable))
        W("")
    W("=== THEN, AND ONLY THEN, md5 ===")
    W("  file                                          bytes  md5"
      "                               ast.Assert")
    for n, p in rows:
        if not p.startswith(HERE):
            continue
        na = ""
        if n.endswith(".py"):
            try:
                na = str(sum(1 for x in ast.walk(ast.parse(
                    open(p, errors="replace").read())) if isinstance(x, ast.Assert)))
            except SyntaxError:
                na = "?"
        W("  %-42s %7d  %s  %s"
          % (n, os.path.getsize(p), md5_of(p), na))
    W("")
    W("=== THE FROZEN SET, AND THE GIT BLOB BESIDE THE DISK ===")
    W("  `d6rf4_grade.py:freeze_check` REFUSES (exit 2) unless disk == the "
      "committed blob at HEAD for every row below.")
    W("  A row reading `NOT IN HEAD` is a file this item EXECUTES that is not "
      "committed yet, which is what the freeze commit fixes.")
    not_in_head = 0
    for rel in frozen_rel:
        disk = os.path.join(REPO, rel)
        dm = md5_of(disk) if os.path.isfile(disk) else "ABSENT-ON-DISK"
        try:
            blob = subprocess.run(["git", "-C", REPO, "cat-file", "blob",
                                   "HEAD:%s" % rel], stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL, check=True).stdout
            bm = hashlib.md5(blob).hexdigest()
        except Exception:                                      # noqa: BLE001
            bm = "NOT IN HEAD"
            not_in_head += 1
        W("  %-62s disk %s  HEAD %s  %s"
          % (rel.rsplit("/", 1)[-1], dm, bm,
             "AGREE" if dm == bm else ("PENDING COMMIT" if bm == "NOT IN HEAD"
                                       else "DISAGREE")))
    W("  -> %d of %d frozen paths are not yet in HEAD" % (not_in_head,
                                                          len(frozen_rel)))
    W("")
    W("=== THE DERIVATION LEDGER: parent -> derived, and the diff beside it ===")
    W("  This family's practice: every instrument is written BY DERIVATION from")
    W("  its parent with a *_DELTAS_from_*.diff beside it.  A ZERO-LINE diff is")
    W("  a CLAIM -- `byte-identical carry` -- and it is asserted here against")
    W("  the two md5s, so an empty diff can never be a FAILED diff read as an")
    W("  identical one.  D6RF3's parent directory: %s" % D6RF3)
    bad_diff = []
    for dn in sorted(n for n in present if n.endswith(".diff")):
        dp = os.path.join(HERE, dn)
        nlines = sum(1 for _ in open(dp, errors="replace"))
        stem = dn.split("_DELTAS_from_")[0].split("_SUBSTANTIVE_after_")[0]
        cand = [x for x in present
                if x.startswith(stem) and not x.endswith(".diff")]
        child = os.path.join(HERE, sorted(cand, key=len)[0]) if cand else None
        if "_DELTAS_from_d6rf3" in dn:
            leaf = os.path.basename(child or "").replace("d6rf4_", "d6rf3_", 1)
            parent = os.path.join(D6RF3, leaf)
        elif dn.startswith("d6rf4_fvSolution_DELTAS"):
            parent = os.path.join(HERE, "d6rf4_fvSolution_D6RF3_ORIGINAL")
            child = os.path.join(HERE, "d6rf4_fvSolution_TIGHT")
        else:
            parent = None                       # the rename-stripped diffs
        pm = md5_of(parent) if parent and os.path.isfile(parent) else "-"
        cm = md5_of(child) if child and os.path.isfile(child) else "-"
        note = ""
        if parent is not None:
            if nlines == 0 and pm != cm:
                note = "  <-- REFUSE: EMPTY DIFF BUT THE md5s DIFFER"
                bad_diff.append(dn)
            elif nlines == 0:
                note = "  BYTE-IDENTICAL CARRY, asserted on both md5s"
            elif pm == cm:
                note = "  <-- REFUSE: NON-EMPTY DIFF BUT THE md5s AGREE"
                bad_diff.append(dn)
        else:
            note = "  (rename-stripped view; no parent file)"
        W("  %-52s %5d lines  parent %s  derived %s%s"
          % (dn, nlines, pm, cm, note))
    if bad_diff:
        W("  -> REFUSE: %d diff(s) disagree with their own md5s" % len(bad_diff))
    else:
        W("  -> every DELTAS diff agrees with the md5s of the pair it describes")
    W("")
    W("=== WHAT EACH SOURCE REFERENCES (the derivation itself, shown) ===")
    for n in sorted(by_source):
        W("  %-38s -> %s" % (n, " ".join(by_source[n]) or "(nothing)"))
    W("")
    if absent:
        W("=== REFUSE: %d REGISTERED DEPENDENCY(IES) ABSENT ===" % len(absent))
        W("  %s" % " ".join(absent))
        W("  Section 18.3: a registered gate whose implementing file is not in "
          "the instrument table is not frozen -- it is UNIMPLEMENTED.")
    else:
        W("=== NOTHING REFERENCED IS ABSENT ===")
    txt = "\n".join(lines) + "\n"
    with open(OUT, "w") as fh:
        fh.write(txt)
        fh.flush()
        os.fsync(fh.fileno())
    sys.stdout.write(txt)
    return 2 if (absent or unparseable or dropped_but_present or bad_diff) else 0


if __name__ == "__main__":
    sys.exit(main())
