#!/usr/bin/env python3
"""mutation_test_vmfl064.py -- proves grade_vmfl064.py's controls are REAL and enforced
IDENTICALLY under `python3` and `python3 -O` (template Amendment 6/6a).

Break each control on a SACRIFICIAL COPY and confirm --selftest exits NON-ZERO (and prints
no all-checks-passed line) under BOTH interpreters. A selftest that cannot fail is not
evidence; only breaking each control proves the selftest depends on it.

Mutations:
  A. baseline -- unmutated --selftest exits 0 under both interpreters.
  B. planted-zero REFUSAL defanged (raise -> pass) -- rule-3 control.
  C. completion rc-refusal defanged (`if out["rc"] != 0` -> `if False`) -- rule-4 control.
"""
import os, sys, subprocess, tempfile, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
GRADER = os.path.join(HERE, 'grade_vmfl064.py')
INTERPS = [['python3'], ['python3', '-O']]

def run_selftest(path):
    out = []
    for interp in INTERPS:
        r = subprocess.run(interp + [path, '--selftest'], capture_output=True, text=True)
        out.append((r.returncode, ('all checks passed' in r.stdout)))
    return out

def run_mutant(src, old, new):
    if old not in src:
        return None
    mutated = src.replace(old, new, 1)
    if mutated == src:
        return None
    d = tempfile.mkdtemp(prefix='mut064_')
    try:
        mp = os.path.join(d, 'grade_mutated.py')
        open(mp, 'w').write(mutated)
        return run_selftest(mp)
    finally:
        shutil.rmtree(d, ignore_errors=True)

def main():
    fails = []
    def expect(name, cond):
        print(('  ok   ' if cond else '  FAIL ') + name)
        if not cond:
            fails.append(name)

    print('--- mutation_test_vmfl064.py')
    src = open(GRADER).read()
    base = run_selftest(GRADER)
    print('A. unmutated: python3 (rc=%d, green=%s) ; -O (rc=%d, green=%s)'
          % (base[0][0], base[0][1], base[1][0], base[1][1]))
    expect('unmutated selftest exits 0 under python3', base[0][0] == 0)
    expect('unmutated selftest exits 0 under python3 -O', base[1][0] == 0)
    expect('unmutated selftest identical across interpreters', base[0][0] == base[1][0])

    mutations = [
        ('B. planted-zero refusal defanged',
         '        if not ok:\n'
         '            raise SystemExit2("planted-zero control FAILED: planted %g into wallShearStress "\n'
         '                              "bottomWall face 0, the reader moved by %g -- a reader not shown "\n'
         '                              "able to see a non-zero cannot certify a zero (CLAUDE.md rule 3)"\n'
         '                              % (PLANT, delta))',
         '        if not ok:\n            pass  # MUTATED: refusal defanged'),
        ('C. completion rc-refusal defanged',
         '    if out["rc"] != 0:',
         '    if False:  # MUTATED: rc refusal defanged'),
    ]
    for name, old, new in mutations:
        res = run_mutant(src, old, new)
        if res is None:
            expect('%s -- needle located' % name, False)
            continue
        (rc_p, g_p), (rc_o, g_o) = res
        print('%s: python3 (rc=%d, green=%s) ; -O (rc=%d, green=%s)' % (name, rc_p, g_p, rc_o, g_o))
        expect('%s FAILS selftest under python3 (control is real)' % name, rc_p != 0)
        expect('%s FAILS selftest under python3 -O (not stripped by -O)' % name, rc_o != 0)
        expect('%s prints no all-checks-passed line under either interpreter' % name,
               (not g_p) and (not g_o))

    TOTAL = 3 + 3 * len(mutations)
    print('%d/%d expectations held' % (TOTAL - len(fails), TOTAL))
    if fails:
        print('MUTATION TEST FAILED: ' + '; '.join(fails)); return 1
    print('MUTATION TEST PASSED: every control real and interpreter-invariant.'); return 0

if __name__ == '__main__':
    sys.exit(main())
