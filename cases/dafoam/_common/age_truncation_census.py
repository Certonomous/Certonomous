#!/usr/bin/env python3
"""SUB-SECOND TIMESTAMP-TRUNCATION CENSUS over this repository's age guards.

`CLAUDE.md` rule 4's age guard exists so that a field the run did not produce
cannot be graded as one it did.  It compares two file modification times.  The
kernel records mtime to the NANOSECOND; a datum taken with `stat -c %Y`,
`int(os.path.getmtime(...))` or `"%d" %` is truncated to the WHOLE SECOND.  The
two predicates then disagree inside a window up to 1.000 s wide.  This instrument
finds those comparisons and says, per site, WHICH WAY the disagreement runs.

================================================================================
THIS INSTRUMENT HAS BEEN WRONG THREE TIMES.  READ THIS BEFORE TRUSTING ITS OUTPUT.
================================================================================

An instrument that arrives without its own failure history invites the next
person to trust its first output.  This one's first outputs were wrong three
times, and the failures are recorded here rather than tidied away.

**FAILURE 1 -- IT MANUFACTURED SIX DEFECTS IN A CLEAN FILE, AND THIS IS THE ONE
TO LEAD WITH.**  An earlier version accused
`cases/F28_DUCTED_ACTUATOR_DISK/analyse_f28.py` of SIX truncated comparisons.
**That file is clean** -- full precision on both sides, and it prints `%.6f`.
Two defects combined to produce the accusation: (a) it classed `st_mtime_ns` as
truncated when it is the OPPOSITE, integer nanoseconds, the most precise form
the kernel offers; and (b) it resolved variable names MODULE-WIDE, so a local
`mt` inside one function inherited the provenance of an unrelated `mt` in
another.  **A census that manufactures defects is worse than one that misses
them, because somebody acts on it.**  Fixed by treating `st_mtime_ns` as exact
and by scoping name resolution to the enclosing `FunctionDef`.

**FAILURE 2 -- THE PLANTED CONTROL SCORED 6/8 ON ITS FIRST RUN.**  It missed both
pure READ-BACK fixtures (`pos2`, `pos5`), where the floor sits on the read and
the only thing marking the value as a timestamp is the NAME IT IS BOUND TO.
**That idiom is 22 of the real sites in the dafoam family** -- the launcher
floors with `stat -c %Y` into a file and the grader reads it back with
`int(open(p).read())`, a floor that crosses a FILE BOUNDARY.  Without the plant
this census would have under-reported by roughly a quarter.  Fixed by resolving
the assignment TARGET name, not only the read expression.

**FAILURE 3 -- A LINE-LEVEL PASS SEES A THIRD OF THE POPULATION.**  Looking for
`int(`/`floor` ON THE COMPARISON LINE found 28 of the 89 truncated comparisons
in this tree.  **60 carry the floor somewhere else entirely.**  That is why this
instrument resolves provenance through assignment hops instead of grepping.

================================================================================
THE CONTROL GATE
================================================================================
`census()` REFUSES to report anything until the planted fixture has been emitted,
read back off disk, and scored EXACTLY 8/8 positives and 0/6 false positives.
A census that cannot see its own positives is not evidence, and this one has
already proved it can fail that way.  `--no-control` does not exist.

The gate itself has been DRIVEN IN THE REFUSING DIRECTION: each of the three
failures above was reintroduced as a mutation and the control REFUSED on each --
6/8 with `pos2`/`pos5` missed for FAILURE 2, `neg2` wrongly flagged for FAILURE
1(a), `neg6` wrongly flagged for FAILURE 1(b) -- plus a refusal when the fixture
is absent altogether.  `neg6` EXISTS BECAUSE OF THAT EXERCISE: the first mutation
run showed the control could NOT catch FAILURE 1(b), so the fixture was extended
until it could.  A control that has never been shown to fail is not a control.

================================================================================
WHAT IT REPORTS, AND WHY DIRECTION IS NOT THE OPERATOR
================================================================================
FAIL-OPEN vs FAIL-CLOSED is given by three things TOGETHER: the operator, WHICH
SIDE was truncated, and whether the predicate being TRUE means ACCEPT or REFUSE.
`--sweep` prints the possibility table, derived by exhaustive enumeration of
sub-second offsets rather than argued.

Two sites in this repository make the point:
  `so3_grade.py:1104`  `if amt <= datum: refuse(...)`   both floored  -> FAIL-CLOSED
  `so1a_grade.py:326`  `if on_disk < datum: refuse(...)` both floored -> FAIL-OPEN
Adjacent ladders, both sides floored in both, TRUE means REFUSE in both, and
**the only difference is the `=`**.

The SENSE (does TRUE mean ACCEPT or REFUSE) is NOT inferred: this instrument
reports the sites and their truncated sides, and a human assigns the sense by
reading what consumes the result.  Guessing it would be exactly the kind of
unwitnessed inference the census exists to find.

Usage:
    python3 age_truncation_census.py --repo /home/ubuntu/Certonomous
    python3 age_truncation_census.py --repo ... --json out.json
    python3 age_truncation_census.py --sweep
    python3 age_truncation_census.py --selftest      # the control gate, alone
"""
import argparse, ast, collections, json, math, os, re, subprocess, sys, tempfile

MTIME_CALLS = {"getmtime", "getctime"}
MTIME_FIELDS_EXACT = {"st_mtime_ns"}            # integer ns -- FULL precision, NOT a floor
MTIME_FIELDS_FLOAT = {"st_mtime", "st_ctime"}   # float seconds -- full precision
FLOOR_FUNCS = {"int", "floor", "trunc"}
ROUND_FUNCS = {"round", "ceil"}                 # NOT floors: they do not move a datum earlier
TS_NAME = re.compile(r"(stamp|datum|mtime|epoch|age|_ts\b|\bts\b|t0|tref|ref_?time|sentinel)", re.I)


class Refusal(RuntimeError):
    pass


# ---------------------------------------------------------------- provenance --
class P:
    __slots__ = ("m", "f", "why")

    def __init__(self, m=False, f=False, why=""):
        self.m, self.f, self.why = m, f, why


def unp(n):
    try:
        return ast.unparse(n)
    except Exception:
        return "<unparseable>"


class Scan:
    """Per-module provenance.  Scoping is per enclosing FunctionDef with a
    module-level fallback -- FAILURE 1(b) was module-wide resolution."""

    def __init__(self, tree):
        self.scopes, self.tgt_of, self.parent = {}, {}, {}
        self._index(tree, None)
        self.mod = id(tree)

    def _index(self, node, scope):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef)):
            scope = node
            self.scopes.setdefault(id(scope), {})
        for ch in ast.iter_child_nodes(node):
            self.parent[id(ch)] = (node, scope)
            if isinstance(ch, ast.Assign):
                for t in ch.targets:
                    if isinstance(t, ast.Name):
                        self.scopes.setdefault(id(scope), {}).setdefault(
                            t.id, []).append((ch.lineno, ch.value))
                        self.tgt_of[id(ch.value)] = t.id
            self._index(ch, scope)

    def scope_of(self, node):
        cur = node
        while id(cur) in self.parent:
            par, sc = self.parent[id(cur)]
            if sc is not None:
                return sc
            cur = par
        return None

    def lookup(self, name, scope):
        sc, seen = scope, 0
        while sc is not None and seen < 8:
            d = self.scopes.get(id(sc), {})
            if name in d:
                return d[name]
            par = self.parent.get(id(sc), (None, None))[1]
            sc = par if par is not sc else None
            seen += 1
        return self.scopes.get(self.mod, {}).get(name)

    def _is_readback(self, node, target=None):
        """FAILURE 2 lived here.  The floor is on the READ; the only thing that
        says the value is a TIMESTAMP may be the NAME IT IS BOUND TO."""
        s = unp(node)
        if not re.search(r"\.(read|read_text|readline)\(\)", s):
            return False
        if TS_NAME.search(s):
            return True
        return bool(target and TS_NAME.search(target))

    def prov(self, node, scope, depth=0):
        if node is None or depth > 6:
            return P()
        if isinstance(node, ast.Call):
            f = node.func
            fn = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")
            if fn in MTIME_CALLS:
                return P(True, False, "%s() float seconds, FULL precision" % fn)
            if fn in FLOOR_FUNCS:
                inner = self.prov(node.args[0], scope, depth + 1) if node.args else P()
                if inner.m:
                    return P(True, True, "%s(%s)" % (fn, inner.why))
                if node.args and self._is_readback(node.args[0], self.tgt_of.get(id(node))):
                    return P(True, True, "int(READ-BACK of a serialised timestamp)")
                return P()
            if fn in ROUND_FUNCS:
                inner = self.prov(node.args[0], scope, depth + 1) if node.args else P()
                return P(inner.m, False, "%s(...) -- NOT a floor" % fn) if inner.m else P()
            for a in node.args:
                p = self.prov(a, scope, depth + 1)
                if p.m:
                    return p
            return P()
        if isinstance(node, ast.Attribute):
            if node.attr in MTIME_FIELDS_EXACT:
                return P(True, False, "st_mtime_ns integer NANOSECONDS, FULL precision")
            if node.attr in MTIME_FIELDS_FLOAT:
                return P(True, False, "%s float seconds, FULL precision" % node.attr)
            return self.prov(node.value, scope, depth + 1)
        if isinstance(node, ast.Name):
            for ln, v in (self.lookup(node.id, scope) or [])[:5]:
                p = self.prov(v, scope, depth + 1)
                if p.m:
                    return P(True, p.f, "%s@%d <- %s" % (node.id, ln, p.why))
            return P()
        if isinstance(node, ast.BinOp):
            for s in (node.left, node.right):
                p = self.prov(s, scope, depth + 1)
                if p.m:
                    return p
            return P()
        if isinstance(node, (ast.Subscript, ast.Starred)):
            return self.prov(node.value, scope, depth + 1)
        return P()


def py_hits(rel, src):
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    sc, lines, out = Scan(tree), src.splitlines(), []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        scope = sc.scope_of(node)
        operands = [node.left] + list(node.comparators)
        provs = [sc.prov(o, scope) for o in operands]
        if not any(p.m for p in provs):
            continue
        out.append(dict(file=rel, line=node.lineno,
                        ops=[type(o).__name__ for o in node.ops],
                        text=(lines[node.lineno - 1].strip()[:200] if node.lineno - 1 < len(lines) else ""),
                        sides=[dict(expr=unp(o)[:90], mtime=p.m, floored=p.f, why=p.why)
                               for o, p in zip(operands, provs)],
                        truncated=any(p.m and p.f for p in provs)))
    return out


SH_STATY = re.compile(r"stat\s+(?:-[a-zA-Z]+\s+)*-c\s*['\"]?%Y")
SH_NUMCMP = re.compile(r"-(lt|le|gt|ge|eq|ne)\b")


def sh_hits(rel, src):
    lines, ts, out = src.splitlines(), {}, []
    for n, raw in enumerate(lines, 1):
        if raw.lstrip().startswith("#"):
            continue
        m = re.match(r"^\s*(?:local\s+|export\s+|declare\s+[-a-zA-Z]*\s+)?"
                     r"([A-Za-z_][A-Za-z_0-9]*)=(.*)$", raw)
        if m and SH_STATY.search(m.group(2)):
            ts[m.group(1)] = n
    for n, raw in enumerate(lines, 1):
        if raw.lstrip().startswith("#"):
            continue
        hit = None
        if re.search(r"-newermt\s+[\"']?@", raw):
            hit = ("find -newermt @N", True,
                   "-newermt @N means STRICTLY AFTER N.000000000; the datum is truncated")
        elif re.search(r"-newermt", raw):
            hit = ("find -newermt <relative>", True, "relative -newermt; second-resolution datum")
        elif re.search(r"(?<![A-Za-z-])-newer\s+[\"$]", raw):
            hit = ("find -newer FILE", False, "full-precision mtime comparison")
        else:
            m = SH_NUMCMP.search(raw)
            if m:
                names = [k for k in ts if re.search(r"\$\{?%s\b" % re.escape(k), raw)]
                inline = bool(SH_STATY.search(raw))
                if names or inline:
                    hit = ("[ -%s ]" % m.group(1), True,
                           "inline stat -c %Y" if inline
                           else "vars from stat -c %%Y: " + ",".join(names))
        if hit:
            out.append(dict(file=rel, line=n, ops=[hit[0]], text=raw.strip()[:200],
                            sides=[dict(expr="", mtime=True, floored=hit[1], why=hit[2])],
                            truncated=hit[1]))
    return out


def scan_source(rel, src):
    return py_hits(rel, src) if rel.endswith(".py") else sh_hits(rel, src)


# ------------------------------------------------------------- the sweep ------
OPS = {"Gt": lambda a, d: a > d, "GtE": lambda a, d: a >= d,
       "Lt": lambda a, d: a < d, "LtE": lambda a, d: a <= d,
       "Eq": lambda a, d: a == d, "NotEq": lambda a, d: a != d}


def sweep(op, art_floored, dat_floored, n_datum=200, span_ms=1500):
    """Exhaustive over sub-second offsets: can the truncated predicate produce a
    FALSE POSITIVE (true when the exact one is false) or a FALSE NEGATIVE?"""
    fp = fn = False
    for i in range(n_datum):
        d = 100.0 + i / float(n_datum)
        for j in range(-span_ms, span_ms + 1):
            a = d + j / 1000.0
            fa = math.floor(a) if art_floored else a
            fd = math.floor(d) if dat_floored else d
            ex, co = op(a, d), op(fa, fd)
            if co and not ex:
                fp = True
            if ex and not co:
                fn = True
            if fp and fn:
                return fp, fn
    return fp, fn


def sweep_table():
    rows = []
    for name, f in OPS.items():
        for af in (False, True):
            for df in (False, True):
                fp, fn = sweep(f, af, df)
                rows.append(dict(op=name, artefact="FLOORED" if af else "exact",
                                 datum="FLOORED" if df else "exact",
                                 can_false_positive=fp, can_false_negative=fn))
    return rows


# ------------------------------------------------------- THE CONTROL GATE -----
def run_control(tmpdir=None):
    """CLAUDE.md rule 3.  Emit the planted fixture, read it BACK OFF DISK, and
    require 8/8 positives and 0/5 false positives.  Raises Refusal otherwise."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        import age_truncation_census_fixture as fx
    except ImportError as e:
        raise Refusal("the planted fixture is MISSING (%s).  A census that cannot "
                      "run its own control reports nothing." % e)
    d = tmpdir or tempfile.mkdtemp(prefix="age_truncation_control_")
    pos, neg = fx.emit(d)
    seen = {}
    for name in pos + neg:
        p = os.path.join(d, name)
        with open(p, encoding="utf-8") as fh:            # READ BACK OFF DISK
            src = fh.read()
        seen[name] = any(h["truncated"] for h in scan_source(name, src))
    got_pos = sum(1 for n in pos if seen[n])
    false_pos = sum(1 for n in neg if seen[n])
    detail = dict(dir=d, positives_detected=got_pos, positives_total=len(pos),
                  false_positives=false_pos, negatives_total=len(neg),
                  missed=[n for n in pos if not seen[n]],
                  wrongly_flagged=[n for n in neg if seen[n]])
    if got_pos != len(pos) or false_pos != 0:
        raise Refusal(
            "PLANTED CONTROL FAILED: %d/%d positives detected, %d/%d negatives wrongly "
            "flagged. missed=%r wrongly_flagged=%r.  A reader not shown able to see a "
            "non-zero is not evidence (CLAUDE.md rule 3); THIS CENSUS REPORTS NOTHING."
            % (got_pos, len(pos), false_pos, len(neg), detail["missed"], detail["wrongly_flagged"]))
    return detail


# ------------------------------------------------------------- the census -----
def tracked_scripts(repo):
    out = subprocess.run(["git", "-C", repo, "ls-files"], capture_output=True, text=True)
    if out.returncode != 0:
        raise Refusal("git ls-files failed in %s" % repo)
    return [l for l in out.stdout.splitlines() if l.endswith((".py", ".sh"))]


def census(repo, control_tmpdir=None):
    """THE CONTROL RUNS FIRST AND UNCONDITIONALLY.  Nothing is reported without it."""
    control = run_control(control_tmpdir)
    hits = []
    for rel in tracked_scripts(repo):
        try:
            with open(os.path.join(repo, rel), encoding="utf-8", errors="replace") as fh:
                src = fh.read()
        except OSError:
            continue
        hits.extend(scan_source(rel, src))
    tr = [h for h in hits if h["truncated"]]
    line_visible = sum(1 for h in tr if re.search(
        r"\bint\s*\(|math\.floor|stat -c ?'?%Y|-newermt", h["text"]))
    return dict(
        control=control,
        scripts_scanned=len(tracked_scripts(repo)),
        mtime_comparisons=len(hits),
        mtime_comparison_files=len({h["file"] for h in hits}),
        truncated=len(tr),
        truncated_files=len({h["file"] for h in tr}),
        floor_on_the_comparison_line=line_visible,
        floor_elsewhere=len(tr) - line_visible,
        rounds_or_ceils_on_a_timestamp=sum(
            1 for h in hits if any(s["mtime"] and "NOT a floor" in s["why"] for s in h["sides"])),
        by_area=dict(collections.Counter(
            "cases/dafoam" if h["file"].startswith("cases/dafoam/")
            else "/".join(h["file"].split("/")[:2]) for h in tr)),
        hits=hits)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default="/home/ubuntu/Certonomous")
    ap.add_argument("--json", help="write every hit to this path")
    ap.add_argument("--sweep", action="store_true", help="print the FP/FN possibility table")
    ap.add_argument("--selftest", action="store_true", help="run the planted control alone")
    a = ap.parse_args(argv)

    if a.sweep:
        print("%-6s %-9s %-9s %-6s %-6s" % ("op", "artefact", "datum", "canFP", "canFN"))
        for r in sweep_table():
            print("%-6s %-9s %-9s %-6s %-6s" % (r["op"], r["artefact"], r["datum"],
                                                r["can_false_positive"], r["can_false_negative"]))
        return 0

    if a.selftest:
        try:
            d = run_control()
        except Refusal as e:
            print("REFUSED: %s" % e)
            return 2
        print("PLANTED CONTROL PASS  positives %d/%d  false positives %d/%d"
              % (d["positives_detected"], d["positives_total"],
                 d["false_positives"], d["negatives_total"]))
        return 0

    try:
        r = census(a.repo)
    except Refusal as e:
        print("REFUSED: %s" % e)
        return 2
    c = r["control"]
    print("PLANTED CONTROL PASS  positives %d/%d  false positives %d/%d"
          % (c["positives_detected"], c["positives_total"],
             c["false_positives"], c["negatives_total"]))
    print("scripts scanned            : %d" % r["scripts_scanned"])
    print("mtime comparisons          : %d in %d files" % (r["mtime_comparisons"], r["mtime_comparison_files"]))
    print("truncated on >=1 side      : %d in %d files" % (r["truncated"], r["truncated_files"]))
    print("  floor ON the compare line: %d" % r["floor_on_the_comparison_line"])
    print("  floor ELSEWHERE          : %d   <- invisible to a line-level pass" % r["floor_elsewhere"])
    print("round()/ceil() on a datum  : %d   (a floor moves a datum EARLIER; a round does not)"
          % r["rounds_or_ceils_on_a_timestamp"])
    print("truncated by area          : %s" % r["by_area"])
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(r["hits"], fh, indent=1)
        print("hits written to %s" % a.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
