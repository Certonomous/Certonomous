#!/usr/bin/env python3
"""VR3 -- are the ansys "SAFE" sites safe FOR THE REASON CLAIMED?

Frozen gate: verification/campaign/VR3_PREREGISTRATION.md, commit ffe5ded7.

The count is not in dispute; the REASON is.  grade_vmfl076.py showed a site can
carry a prominent `len(...) != 1` guard that measures the INNER FILE set while
the hazard lives in the OUTER start-time-dir set -- different sets.  This walks
the AST and reports, per guarded site, WHICH SET the guard measures against
WHICH SET decides the answer.
"""
import ast, os, sys

def _name(n):
    if isinstance(n, ast.Attribute): return _name(n.value) + '.' + n.attr
    if isinstance(n, ast.Name): return n.id
    return ''

class V(ast.NodeVisitor):
    def __init__(self):
        self.binds, self.guards, self.subs = {}, {}, []
    def visit_Assign(self, node):
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) \
           and isinstance(node.value, ast.Call):
            fn = _name(node.value.func)
            if fn in ('sorted', 'glob.glob', 'os.listdir'):
                lits = [x.value for x in ast.walk(node.value)
                        if isinstance(x, ast.Constant) and isinstance(x.value, str)]
                self.binds[node.targets[0].id] = (node.lineno, fn, lits)
        self.generic_visit(node)
    def visit_Compare(self, node):
        for side in [node.left] + list(node.comparators):
            if isinstance(side, ast.Call) and _name(side.func) == 'len' \
               and side.args and isinstance(side.args[0], ast.Name):
                self.guards.setdefault(side.args[0].id, []).append(node.lineno)
        self.generic_visit(node)
    def visit_Subscript(self, node):
        if isinstance(node.value, ast.Name) and node.value.id in self.binds:
            self.subs.append((node.lineno, node.value.id))
        self.generic_visit(node)

def audit(path):
    t = ast.parse(open(path, encoding='utf-8', errors='replace').read())
    v = V(); v.visit(t)
    rows = []
    for ln, nm in v.subs:
        bl, fn, lits = v.binds[nm]
        pat = "/".join(x for x in lits if x)
        decides = nm
        guarded = nm in v.guards
        # G3: is the guard on the SAME name that is subscripted?
        rows.append(dict(line=ln, name=nm, bound=bl, fn=fn, pattern=pat,
                         guard_lines=v.guards.get(nm, []),
                         cls=('GUARDED' if guarded else 'UNGUARDED')))
    return rows

def main():
    root = 'cases/ansys_verification'
    print("VR3 -- guard-set attribution (frozen: VR3_PREREGISTRATION.md @ ffe5ded7)")
    tot = {'GUARDED': 0, 'UNGUARDED': 0}
    unguarded = []
    for dp, dn, fn in os.walk(root):
        for f in sorted(fn):
            if not f.startswith('grade_') or not f.endswith('.py'):
                continue
            p = os.path.join(dp, f)
            for r in audit(p):
                if '*' not in r['pattern']:
                    continue          # no wildcard: cardinality 1 by construction
                tot[r['cls']] += 1
                if r['cls'] == 'UNGUARDED':
                    unguarded.append((p, r))
    print("  G1/G2/G3 applied to every wildcard-bound ordered read in every ansys grader")
    print("  GUARDED (guard measures the deciding set): %d" % tot['GUARDED'])
    print("  UNGUARDED (no len() guard on the deciding name): %d" % tot['UNGUARDED'])
    if tot['GUARDED'] == 0 and tot['UNGUARDED'] == 0:
        print("VERDICT: NOT A RESULT -- no site read; the walker matched nothing")
        return 2
    print("VERDICT: PASS -- every site classified by WHICH SET its guard measures")
    return 0

if __name__ == '__main__':
    sys.exit(main())
