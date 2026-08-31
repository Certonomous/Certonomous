#!/usr/bin/env python3
"""mutation_test_vmfl006_r2.py -- proves grade_vmfl006_r2.py's controls are REAL and
enforced IDENTICALLY under `python3` and `python3 -O` (PREREG_TEMPLATE Amendments
6 and 6a).

Break each control on a SACRIFICIAL COPY and confirm --selftest exits NON-ZERO and
prints no all-checks-passed line, under BOTH interpreters. A selftest that cannot
fail is not evidence; neither reading the source nor an exit-code parity check
finds this -- only breaking each control does.

Mutations:
  A. baseline -- the unmutated selftest exits 0 under both interpreters.
  B. planted-zero refusal defanged (rule 3).
  C. strict-completion rc refusal defanged (rule 4).
  D. observed-order floor defanged (FINDING_p_floor.md sec.4).
  E. conservation/orientation refusal defanged (the mixing-cup weight control).
  F. INFRASTRUCTURE made FATAL -- infra_warn() raises instead of warning. This is
     the mutation for Sanaa's universal rule (L-342): if a bookkeeping absence can
     void a run, the infrastructure-tolerance control must catch it.
  G. convergence FLOOR defanged (R2 redesign) -- the still-descending and stalled
     probes must then mis-grade CONVERGED and the satisfiability control must catch it.
  H. convergence DESCENT/LIVENESS defanged (R2 redesign) -- the never-descended dead
     channel below the floor must then mis-grade CONVERGED and be caught.
"""
import os, sys, subprocess, tempfile, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
GRADER = os.path.join(HERE, 'grade_vmfl006_r2.py')
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
    d = tempfile.mkdtemp(prefix='mut006_')
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

    print('--- mutation_test_vmfl006.py')
    src = open(GRADER).read()
    base = run_selftest(GRADER)
    print('A. unmutated: python3 (rc=%d, green=%s) ; -O (rc=%d, green=%s)'
          % (base[0][0], base[0][1], base[1][0], base[1][1]))
    expect('unmutated selftest exits 0 under python3', base[0][0] == 0)
    expect('unmutated selftest exits 0 under python3 -O', base[1][0] == 0)
    expect('unmutated selftest identical across interpreters', base[0][0] == base[1][0])

    mutations = [
        ('B. planted-zero refusal defanged',
         '        if abs(delta - PLANT) > 1e-12:',
         '        if False:  # MUTATED'),
        ('C. completion rc-refusal defanged',
         '        if out["rc"] != 0:',
         '        if False:  # MUTATED'),
        ('D. observed-order floor defanged',
         '    if p < P_MIN:',
         '    if False:  # MUTATED'),
        ('E. conservation/orientation refusal defanged',
         '    if rel > FLUX_REL_TOL:',
         '    if False:  # MUTATED'),
        ('F. INFRASTRUCTURE made fatal (L-342 inverted)',
         '    line = "WARNING [INFRA]: %s" % _norm(msg)',
         '    raise SystemExit2("MUTATED: an infrastructure absence treated as fatal")'),
        ('G. convergence FLOOR defanged (R2 redesign)',
         '    if worst > RES_FLOOR:',
         '    if False:  # MUTATED'),
        ('H. convergence DESCENT/LIVENESS defanged (R2 redesign)',
         '    if peak <= RES_FLOOR:',
         '    if False:  # MUTATED'),
    ]
    for name, old, new in mutations:
        res = run_mutant(src, old, new)
        if res is None:
            expect('%s -- needle located' % name, False)
            continue
        (rc_p, g_p), (rc_o, g_o) = res
        print('%s: python3 (rc=%d, green=%s) ; -O (rc=%d, green=%s)'
              % (name, rc_p, g_p, rc_o, g_o))
        expect('%s FAILS selftest under python3 (control is real)' % name, rc_p != 0)
        expect('%s FAILS selftest under python3 -O (not stripped by -O)' % name, rc_o != 0)
        expect('%s prints no all-checks-passed line under either interpreter' % name,
               (not g_p) and (not g_o))

    TOTAL = 3 + 3 * len(mutations)
    print('%d/%d expectations held' % (TOTAL - len(fails), TOTAL))
    if fails:
        print('MUTATION TEST FAILED: ' + '; '.join(fails))
        return 1
    print('MUTATION TEST PASSED: every control real and interpreter-invariant.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
