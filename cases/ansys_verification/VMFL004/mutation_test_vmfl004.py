#!/usr/bin/env python3
"""mutation_test_vmfl004.py -- proves the VMFL004 comparator's controls are REAL and
are enforced IDENTICALLY under `python3` and `python3 -O`.

Why this exists (the brief, 2026-08-26): `python3 -O` strips `assert`, so any refusal,
guard, control or gate that rides on an `assert` silently vanishes under -O.  This test
drives grade_vmfl004.py as a subprocess under BOTH interpreters and checks:

  A. the unmutated comparator's --selftest exits 0 under python3 AND python3 -O;
  B. a comparator whose planted-zero REFUSAL is defanged (sys.exit(2) -> return None)
     FAILS --selftest (nonzero) under BOTH interpreters -- i.e. the control is what
     the selftest depends on, and -O does not strip it (it is not an assert).

Exit 0 iff every expectation holds under both interpreters.  No `assert` is used to
carry any check here either; failures are reported and drive the exit code.
"""
import os, sys, subprocess, tempfile, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
GRADER = os.path.join(HERE, 'grade_vmfl004.py')
INTERPS = [['python3'], ['python3', '-O']]

def run_selftest(grader_path):
    """Return (rc_plain, rc_O)."""
    rcs = []
    for interp in INTERPS:
        r = subprocess.run(interp + [grader_path, '--selftest'],
                           capture_output=True, text=True)
        rcs.append(r.returncode)
    return rcs

def main():
    fails = []
    def expect(name, cond):
        print(('  ok   ' if cond else '  FAIL ') + name)
        if not cond:
            fails.append(name)

    print('--- mutation_test_vmfl004.py')
    # A. unmutated selftest is green under both interpreters
    rc_plain, rc_O = run_selftest(GRADER)
    print('A. unmutated --selftest: python3 rc=%d ; python3 -O rc=%d' % (rc_plain, rc_O))
    expect('unmutated selftest exits 0 under python3', rc_plain == 0)
    expect('unmutated selftest exits 0 under python3 -O', rc_O == 0)
    expect('unmutated selftest identical across the two interpreters', rc_plain == rc_O)

    # B. defang the planted-zero refusal and confirm the selftest now FAILS under BOTH.
    src = open(GRADER).read()
    needle = "        sys.exit(2)\n        return {'artifact': artifact"
    # the refusal is `sys.exit(2)` inside planted_zero(); replace the exit with a pass
    # so the blind-reader path returns instead of refusing.
    old = "                'not evidence (CLAUDE.md rule 3).\\n' % (label, plant, artifact, delta))\n        sys.exit(2)"
    mutated = None
    if old in src:
        mutated = src.replace(old, old.replace('        sys.exit(2)', '        pass  # MUTATED: refusal defanged'))
    else:
        # fall back: neutralise the sole `sys.exit(2)` in planted_zero by a robust marker
        marker = "        sys.exit(2)"
        if src.count(marker) >= 1:
            # replace only the FIRST occurrence (the planted_zero refusal)
            idx = src.index(marker)
            mutated = src[:idx] + "        pass  # MUTATED: refusal defanged" + src[idx+len(marker):]
    if mutated is None or mutated == src:
        expect('could locate and defang the planted-zero refusal', False)
        print('%d failure(s)' % len(fails)); return 1 if fails else 0
    d = tempfile.mkdtemp(prefix='mut_')
    try:
        mp = os.path.join(d, 'grade_mutated.py')
        open(mp, 'w').write(mutated)
        mrc_plain, mrc_O = run_selftest(mp)
        print('B. defanged --selftest: python3 rc=%d ; python3 -O rc=%d' % (mrc_plain, mrc_O))
        expect('defanged comparator FAILS selftest under python3 (control is real)', mrc_plain != 0)
        expect('defanged comparator FAILS selftest under python3 -O (refusal is NOT an assert -O strips)', mrc_O != 0)
        expect('defanged failure identical across the two interpreters', (mrc_plain != 0) == (mrc_O != 0))
    finally:
        shutil.rmtree(d, ignore_errors=True)

    TOTAL = 6
    print('%d/%d expectations held' % (TOTAL - len(fails), TOTAL))
    if fails:
        print('MUTATION TEST FAILED: ' + '; '.join(fails)); return 1
    print('MUTATION TEST PASSED: controls real and interpreter-invariant.'); return 0

if __name__ == '__main__':
    sys.exit(main())
