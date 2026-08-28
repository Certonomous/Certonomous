#!/usr/bin/env python3
"""Structural census of ORDERING-KEY sites: a multi-member set reduced to one
member by an ordering that is not the ordering the physics means.

NOT a regex sweep.  Walks the AST, so a call split over lines, or built from a
variable path, is seen exactly as one written on a single line.  The regex
failure this replaces is on record twice: ansys's own first two scan patterns
returned 0 on files proven to carry the shape, and so did mine.

A site is any subscript of an ordered/unordered sequence expression:
    sorted(<X>)[i]      glob.glob(<X>)[i]     os.listdir(<X>)[i]
Classification is by the SORT KEY, because the key is the whole question:
    NUMERIC  - sorted(..., key=float) / sorted(float(x) for x in ...) etc.
    LEXICAL  - sorted() with no key over strings, then indexed  -> HAZARD
    UNORDERED- glob/listdir indexed with no sort at all         -> HAZARD (worse)
Guard attribution is the second half: a `len(...) != 1` refuse is only a guard
on the set it MEASURES.  A cardinality guard over an INNER file glob does not
make an OUTER start-time-dir read safe.  They are different sets.
"""
import ast, os, sys, json

def _name(n):
    if isinstance(n, ast.Attribute):
        return _name(n.value) + '.' + n.attr
    if isinstance(n, ast.Name):
        return n.id
    return ''

def _is_numeric_key(call):
    """sorted(..., key=float|int) or sorted(<numeric comprehension>)"""
    for kw in call.keywords:
        if kw.arg == 'key' and _name(kw.value) in ('float', 'int'):
            return True
    if call.args:
        a = call.args[0]
        if isinstance(a, (ast.GeneratorExp, ast.ListComp)):
            e = a.elt
            if isinstance(e, ast.Call) and _name(e.func) in ('float', 'int'):
                return True
    return False

class V(ast.NodeVisitor):
    """Tracks NAME BINDINGS as well as direct subscripts.

    THE FIRST VERSION OF THIS FILE MISSED EVERY KNOWN POSITIVE.  Real code
    almost never writes sorted(...)[-1]; it writes
        f = sorted(glob.glob(...))
        ... open(f[-1])
    so the subscript is of a NAME, not of a Call.  ansys's first two regex
    patterns died on exactly this, and so did my first AST pass.  A detector
    that returns zero on ground truth is measuring itself.
    """
    def __init__(self, path):
        self.path, self.sites, self.binds, self.strbinds = path, [], {}, {}

    def _collect_strs(self, node):
        return [n.value for n in ast.walk(node)
                if isinstance(n, ast.Constant) and isinstance(n.value, str)]

    def _classify_call(self, v):
        fn = _name(v.func)
        if fn == 'sorted':
            inner = _name(v.args[0].func) if (v.args and isinstance(v.args[0], ast.Call)) else ''
            if _is_numeric_key(v):
                return ('NUMERIC', 'sorted(%s)' % (inner or '...'))
            if inner in ('glob.glob', 'os.listdir') and not _has_wildcard(v, self.strbinds):
                return ('BENIGN-LITERAL', 'sorted(%s <no wildcard>)' % inner)
            return ('LEXICAL', 'sorted(%s)' % (inner or '...'))
        if fn in ('glob.glob', 'os.listdir'):
            if not _has_wildcard(v, self.strbinds):
                return ('BENIGN-LITERAL', '%s(<no wildcard>)' % fn)
            return ('UNORDERED', '%s(...)' % fn)
        return (None, None)

    def visit_Assign(self, node):
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            strs = self._collect_strs(node.value)
            if strs:
                self.strbinds[node.targets[0].id] = strs
        if isinstance(node.value, ast.Call) and len(node.targets) == 1 \
           and isinstance(node.targets[0], ast.Name):
            kind, expr = self._classify_call(node.value)
            if kind:
                self.binds[node.targets[0].id] = (kind, expr, node.lineno)
        self.generic_visit(node)

    def visit_Subscript(self, node):
        idx = ast.unparse(node.slice) if hasattr(ast, 'unparse') else '?'
        v = node.value
        if isinstance(v, ast.Call):
            kind, expr = self._classify_call(v)
            if kind:
                self.sites.append((node.lineno, '%s[%s]' % (expr, idx), kind, 'direct'))
        elif isinstance(v, ast.Name) and v.id in self.binds:
            kind, expr, bln = self.binds[v.id]
            self.sites.append((node.lineno, '%s=%s[%s]' % (v.id, expr, idx), kind,
                               'bound@%d' % bln))
        self.generic_visit(node)

class LenGuards(ast.NodeVisitor):
    """Every name whose len() is COMPARED anywhere in the file.

    Guard attribution is the whole point.  A `len(hits) != 1: refuse` is a
    guard on `hits` AND ON NOTHING ELSE.  Where `hits` is an inner file glob
    and the hazardous read is over the OUTER start-time dirs, the site is
    UNGUARDED however prominent the guard looks when read by eye.
    """
    def __init__(self):
        self.guarded = set()
    def visit_Compare(self, node):
        for side in [node.left] + list(node.comparators):
            if isinstance(side, ast.Call) and _name(side.func) == 'len' \
               and side.args and isinstance(side.args[0], ast.Name):
                self.guarded.add(side.args[0].id)
        self.generic_visit(node)

def _has_wildcard(call, strbinds=None):
    """Resolves NAME-BOUND patterns as well as inline ones.

    THE FIRST VERSION OF THIS TEST RE-CREATED THE DEFECT IT AUDITS.  Real code
    writes
        pat  = os.path.join(d, "postProcessing", "inletMassFlow", "*", "x.dat")
        hits = sorted(glob.glob(pat))
    so the "*" is not inside the glob call at all.  Walking only the call saw
    no wildcard, called seven genuine hazard files BENIGN, and SHRANK an
    already-measured set.  That direction is the dangerous one: limbs that
    fail loudly give false zeros on ground truth, this one quietly deleted
    confirmed positives.  Same root cause as ansys's two dead regexes and my
    own two dead passes: A READER THAT ASSUMES THE INTERESTING EXPRESSION IS
    SYNTACTICALLY LOCAL.
    """
    """A glob pattern with NO wildcard has cardinality 0 or 1 BY CONSTRUCTION.
    glob.glob(join(d, "log.simpleFoam"))[0] after a not-empty guard is EXACT,
    not a hazard.  Found by reading four sites this instrument had flagged --
    the fourth false-positive limb in one audit."""
    lits = [n.value for n in ast.walk(call)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    for n in ast.walk(call):
        if isinstance(n, ast.Name) and strbinds and n.id in strbinds:
            lits.extend(strbinds[n.id])
    return any(ch in L for L in lits for ch in '*?[')

def _seq_is_strings(expr):
    """glob/listdir yield STRINGS; sorting them with no key is lexical.
    anything else (set(), comprehension, ...) may already be numeric -> UNKNOWN."""
    return ('glob.glob' in expr) or ('os.listdir' in expr)

def scan(path):
    try:
        tree = ast.parse(open(path, encoding='utf-8', errors='replace').read())
    except SyntaxError as e:
        return [(0, str(e), 'PARSE_FAIL', 'parse')]
    v = V(path); v.visit(tree)
    g = LenGuards(); g.visit(tree)
    out = []
    for ln, expr, kind, how in v.sites:
        nm = expr.split('=')[0] if '=' in expr and how.startswith('bound') else None
        guard = 'GUARDED(len %s)' % nm if (nm and nm in g.guarded) else 'unguarded'
        if kind in ('LEXICAL', 'UNORDERED') and not _seq_is_strings(expr):
            kind = 'UNKNOWN-TYPE'
        out.append((ln, expr, kind, how + ' ' + guard))
    return out

# ---------------------------------------------------------------------------
# PLANTED CONTROL (L-314 / standing rule 3).  Five limbs, driven with
#   python3 verification/credibility/ordering_key_census.py --selftest
# A zero from this census is worthless unless the census is shown able to see
# a non-zero, AND shown to stay silent on the two safe shapes.  Limb E was
# added AFTER the fact: pass 5 of this instrument declared seven confirmed
# hazard files benign while limbs A-D all passed, because no limb until E had
# its glob pattern bound on a PREVIOUS LINE.  See DEAD_LEVER_AUDIT.md 7.6.
# ---------------------------------------------------------------------------
_SELFTEST = [
    # (name, source, expect_hazard)
    ("A pos: bind-then-index over a wildcard glob", '''
import glob, os
def r(d):
    f = sorted(glob.glob(os.path.join(d, "postProcessing", "resid", "*", "s.dat")))
    if not f: raise SystemExit(1)
    return f[-1]
''', True),
    ("B pos: direct subscript", '''
import glob
def r(d):
    return sorted(glob.glob(d + "/pp/*/s.dat"))[-1]
''', True),
    ("C neg: wildcard-free literal, cardinality 1 by construction", '''
import glob, os
def r(d):
    log = glob.glob(os.path.join(d, "log.simpleFoam"))
    if not log: raise SystemExit(1)
    return log[0]
''', False),
    ("D neg: cardinality guard ON THE SAME SET", '''
import glob, os
def r(d):
    hits = sorted(glob.glob(os.path.join(d, "pp", "*", "g.xy")))
    if len(hits) != 1: raise SystemExit(1)
    return hits[0]
''', False),
    # THE LIMB THAT WAS MISSING WHEN THE INSTRUMENT WAS WRONG.
    ("E pos: PATTERN BOUND ON THE PREVIOUS LINE (killed 4 earlier passes)", '''
import glob, os
def r(d):
    pat  = os.path.join(d, "postProcessing", "inletMassFlow", "*", "s.dat")
    hits = sorted(glob.glob(pat))
    if not hits: raise SystemExit(1)
    return hits[-1]
''', True),
    ("F neg: numeric key over the same directories -- THE REPAIR SHAPE", '''
import os
def r(root):
    out = []
    for name in os.listdir(root):
        out.append((float(name), os.path.join(root, name)))
    out.sort()
    return out
''', False),
]


def selftest():
    import tempfile
    ok = True
    for nm, src, want in _SELFTEST:
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as fh:
            fh.write(src); path = fh.name
        sites = scan(path)
        got = any(k in ('LEXICAL', 'UNORDERED') and 'GUARDED' not in h
                  for _, _, k, h in sites)
        mark = 'ok ' if got == want else 'FAIL'
        if got != want:
            ok = False
        print('%s  %-62s want=%-5s got=%-5s' % (mark, nm, want, got))
        os.unlink(path)
    print('SELFTEST', 'PASS' if ok else 'FAIL')
    return 0 if ok else 2


if __name__ == '__main__':
    roots = sys.argv[1:]
    if roots and roots[0] == '--selftest':
        sys.exit(selftest())
    tot = {}
    for root in roots:
        for dp, dn, fn in os.walk(root):
            if '.git' in dp:
                continue
            for f in fn:
                if not f.endswith('.py'):
                    continue
                p = os.path.join(dp, f)
                s = scan(p)
                if s:
                    tot[p] = s
    haz = 0; num = 0; unord = 0
    for p, sites in sorted(tot.items()):
        for ln, expr, kind, how in sites:
            if 'GUARDED' in how:
                continue
            if kind == 'LEXICAL': haz += 1
            elif kind == 'NUMERIC': num += 1
            elif kind == 'UNORDERED': unord += 1
            print('%-9s %s:%s  %s  (%s)' % (kind, p, ln, expr, how))
    print('--- LEXICAL(hazard)=%d  UNORDERED(hazard)=%d  NUMERIC(safe)=%d  files=%d'
          % (haz, unord, num, len(tot)))


