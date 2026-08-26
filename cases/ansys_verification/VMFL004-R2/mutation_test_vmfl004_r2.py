#!/usr/bin/env python3
"""mutation_test_vmfl004_r2.py -- proves the VMFL004-R2 comparator's controls are REAL and
enforced IDENTICALLY under `python3` and `python3 -O` (CLAUDE.md rule; template Amendment 6/6a).

For each control, break it on a SACRIFICIAL COPY of the grader and confirm --selftest exits
NON-ZERO (and prints no full-pass tally) under BOTH interpreters.  A selftest that cannot
fail is not evidence; only breaking each control proves the selftest depends on it.

Mutations:
  A. baseline -- unmutated --selftest exits 0 under both interpreters.
  B. planted-zero REFUSAL defanged (sys.exit(2) -> pass) -- rule-3 control.
  C. transverse_degeneracy neutralised (early return, always OK) -- the L-338 fix's
     real-failure detector; the selftest's cross-flow / divergence checks must then fail.
  D. iterative_convergence driven gate neutralised (ok never set False) -- the binding
     convergence gate; the selftest's above-floor check must then fail.

No `assert` carries any check here either; failures drive the exit code.
"""
import os, sys, subprocess, tempfile, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
GRADER = os.path.join(HERE, 'grade_vmfl004_r2.py')
INTERPS = [['python3'], ['python3', '-O']]

def run_selftest(grader_path):
    rcs = []
    for interp in INTERPS:
        r = subprocess.run(interp + [grader_path, '--selftest'],
                           capture_output=True, text=True)
        rcs.append((r.returncode, ('30/30' in r.stdout)))
    return rcs   # [(rc_plain, full_plain), (rc_O, full_O)]

def run_mutant(src, old, new):
    if old not in src:
        return None
    mutated = src.replace(old, new, 1)
    if mutated == src:
        return None
    d = tempfile.mkdtemp(prefix='mut_')
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

    print('--- mutation_test_vmfl004_r2.py')
    src = open(GRADER).read()

    # A. baseline green under both
    base = run_selftest(GRADER)
    print('A. unmutated: python3 (rc=%d, full=%s) ; -O (rc=%d, full=%s)'
          % (base[0][0], base[0][1], base[1][0], base[1][1]))
    expect('unmutated selftest exits 0 under python3', base[0][0] == 0)
    expect('unmutated selftest exits 0 under python3 -O', base[1][0] == 0)
    expect('unmutated selftest identical across interpreters', base[0][0] == base[1][0])

    mutations = [
        ('B. planted-zero refusal defanged',
         "delta))\n            sys.exit(2)",
         "delta))\n            pass  # MUTATED: refusal defanged"),
        ('C. transverse_degeneracy neutralised',
         "    reasons = []\n    if not (abs(uy_mean) <= abs_ceil):",
         "    reasons = []\n    return (len(reasons) == 0), reasons  # MUTATED: always OK\n    if not (abs(uy_mean) <= abs_ceil):"),
        ('D. driven convergence gate neutralised',
         "        if not (v < floor):\n            ok = False",
         "        if not (v < floor):\n            ok = ok  # MUTATED: gate never trips"),
    ]
    for name, old, new in mutations:
        res = run_mutant(src, old, new)
        if res is None:
            expect('%s -- needle located' % name, False)
            continue
        (rc_p, full_p), (rc_o, full_o) = res
        print('%s: python3 (rc=%d, full=%s) ; -O (rc=%d, full=%s)' % (name, rc_p, full_p, rc_o, full_o))
        expect('%s FAILS selftest under python3 (control is real)' % name, rc_p != 0)
        expect('%s FAILS selftest under python3 -O (not stripped by -O)' % name, rc_o != 0)
        expect('%s prints no full-pass tally under either interpreter' % name,
               (not full_p) and (not full_o))

    TOTAL = 3 + 3 * len(mutations)
    print('%d/%d expectations held' % (TOTAL - len(fails), TOTAL))
    if fails:
        print('MUTATION TEST FAILED: ' + '; '.join(fails)); return 1
    print('MUTATION TEST PASSED: every control real and interpreter-invariant.'); return 0

if __name__ == '__main__':
    sys.exit(main())
