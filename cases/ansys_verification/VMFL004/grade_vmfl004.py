#!/usr/bin/env python3
"""grade_vmfl004.py -- comparator for VMFL004, Plain Couette Flow with Pressure Gradient
(Ansys Fluid Dynamics Verification Manual, VM2026R1, p.21).

FROZEN GRADING PATH (CLAUDE.md rule 2).  The gate, the band and the tier ceiling
are fixed in cases/ansys_verification/VMFL004/PREREGISTRATION.md and are committed
BEFORE any solver starts.  This file changes nothing about them; it only reads.

CONTROLS CARRIED HERE, all non-droppable:
  rule 3  planted-zero: the gate channel is planted into ON DISK and read back, and
          the comparator REFUSES (exit 2) if the reader cannot see the plant.
  rule 4  strict completion, every clause, including the age guard.
  rule 5  Roache triple gating; the gate may only turn a result INTO NOT A RESULT.
"""
# ---------------------------------------------------------------- shared core
import os, sys, glob, json, math, shutil, tempfile, subprocess

def _times(d):
    ts = []
    for e in os.listdir(d):
        try:
            v = float(e)
        except ValueError:
            continue
        if os.path.isdir(os.path.join(d, e)):
            ts.append((v, e))
    return sorted(ts)

def strict_completion(level_dir, endtime, fields):
    """CLAUDE.md rule 4 -- ALL of it, or the level is NOT complete.
    Returns (ok, [reasons]).  Refuses rather than degrading."""
    bad = []
    rcf = os.path.join(level_dir, 'RUN_RC.txt')
    if not os.path.isfile(rcf):
        return False, ['no RUN_RC.txt -- rc could not be evaluated, and a rule you '
                       'cannot evaluate is a rule you are not applying']
    rc = None
    for ln in open(rcf):
        if ln.strip().startswith('rc'):
            rc = int(ln.split('=')[1].strip())
    if rc != 0:
        bad.append('rc = %s (rule 4 requires 0)' % rc)
    # (2) the End line -- log.simpleFoam BY EXACT NAME.  A `log*` glob matches
    # log.blockMesh FIRST alphabetically and would report the MESHER's End line.
    slog = os.path.join(level_dir, 'log.simpleFoam')
    if not os.path.isfile(slog):
        bad.append('no log.simpleFoam')
        return False, bad
    txt = open(slog, errors='replace').read()
    if '\nEnd\n' not in txt:
        bad.append('no End line in log.simpleFoam')
    # (3) last time == endTime
    ts = _times(level_dir)
    if not ts:
        bad.append('no time directories')
        return False, bad
    last_v, last_s = ts[-1]
    if abs(last_v - endtime) > 1e-9:
        bad.append('last time %s != endTime %s' % (last_s, endtime))
    # (4) fields present at endTime
    for f in fields:
        if not os.path.isfile(os.path.join(level_dir, last_s, f)):
            bad.append('field %s missing at %s' % (f, last_s))
    # (5) ExecutionTime count == endTime
    n_exec = txt.count('\nExecutionTime = ')
    if n_exec != int(endtime):
        bad.append('ExecutionTime count %d != endTime %d' % (n_exec, int(endtime)))
    # (6) AGE GUARD -- every field at endTime strictly newer than the case's own 0/
    zero = os.path.join(level_dir, '0')
    if not os.path.isdir(zero):
        bad.append('no 0/ directory -- the age guard cannot be evaluated')
    else:
        t0 = max(os.path.getmtime(os.path.join(zero, f))
                 for f in os.listdir(zero)
                 if os.path.isfile(os.path.join(zero, f)))
        for f in fields:
            fp = os.path.join(level_dir, last_s, f)
            if os.path.isfile(fp) and not os.path.getmtime(fp) > t0:
                bad.append('AGE GUARD: %s at %s is not newer than 0/' % (f, last_s))
    return (len(bad) == 0), bad

def iterative_convergence(level_dir, floor, chans):
    """rule 5 step 1: a level not iteratively converged is NOT A RESULT."""
    f = sorted(glob.glob(os.path.join(level_dir, 'postProcessing', 'resid', '*', 'solverInfo.dat')))
    if not f:
        return False, {}, 'no solverInfo.dat'
    hdr, rows = None, []
    for ln in open(f[-1]):
        if ln.startswith('#'):
            hdr = ln[1:].split()
        elif ln.strip():
            rows.append(ln.split())
    if not rows or hdr is None:
        return False, {}, 'solverInfo.dat empty'
    out, ok = {}, True
    for c in chans:
        col = hdr.index(c) if c in hdr else None
        if col is None:
            return False, {}, 'channel %s absent from solverInfo.dat' % c
        v = float(rows[-1][col])
        out[c] = v
        if not (v < floor):
            ok = False
    return ok, out, ('' if ok else 'final initial-residual above the frozen floor %g' % floor)

def roache(f1, f2, f3, r=2.0):
    """CLAUDE.md rule 5.  f1 coarse, f2 medium, f3 fine.  Fs = 1.25.
    Never quotes a GCI when the three values are not monotone."""
    e32, e21 = f3 - f2, f2 - f1
    out = {'f_coarse': f1, 'f_medium': f2, 'f_fine': f3, 'r': r,
           'e21': e21, 'e32': e32, 'p': None, 'gci_fine': None, 'f_extrapolated': None}
    if e21 == 0.0 and e32 == 0.0:
        out['state'] = 'EXACT'; return out
    if e21 == 0.0 or e32 == 0.0:
        out['state'] = 'STAGNANT'; return out
    ratio = e32 / e21
    out['ratio'] = ratio
    if ratio < 0:
        out['state'] = 'OSCILLATORY'; return out
    if ratio >= 1.0:
        out['state'] = 'DIVERGENT'; return out
    p = math.log(1.0 / ratio) / math.log(r)
    out['p'] = p
    fex = f3 + e32 / (r ** p - 1.0)
    out['f_extrapolated'] = fex
    if f3 != 0.0:
        out['gci_fine'] = 1.25 * abs(e32 / f3) / (r ** p - 1.0)
    out['state'] = 'CONVERGING'
    return out

def planted_zero(artifact, perturb_fn, read_fn, plant, label):
    """CLAUDE.md rule 3.  Copy the REAL artifact, plant a known perturbation into
    the copy ON DISK, read it back with the SAME reader, and REFUSE (exit 2) if the
    reader cannot see it.  A zero from a reader not shown able to see a non-zero is
    not evidence."""
    d = tempfile.mkdtemp(prefix='plant_')
    try:
        base = read_fn(artifact)
        cp = os.path.join(d, os.path.basename(artifact))
        shutil.copy2(artifact, cp)
        perturb_fn(cp, plant)
        seen = read_fn(cp)
        delta = abs(seen - base)
        if not (delta > 0.1 * abs(plant)):
            sys.stderr.write(
                'REFUSING (exit 2): planted-zero control FAILED for %s.\n'
                '  planted %g into %s, reader moved by only %g.\n'
                '  A reader not shown able to see a non-zero cannot certify a zero '
                '(CLAUDE.md rule 3).\n' % (label, plant, artifact, delta))
            sys.exit(2)
        return {'artifact': artifact, 'plant': plant, 'baseline': base,
                'perturbed': seen, 'delta_seen': delta, 'control': 'PASS'}
    finally:
        shutil.rmtree(d, ignore_errors=True)

def verify_frozen(path, sha):
    """The grading path is fixed at the pre-registration commit (rule 2)."""
    repo = subprocess.run(['git', '-C', os.path.dirname(os.path.abspath(path)),
                           'rev-parse', '--show-toplevel'],
                          capture_output=True, text=True).stdout.strip()
    rel = os.path.relpath(os.path.abspath(path), repo)
    head = subprocess.run(['git', '-C', repo, 'rev-parse', '%s:%s' % (sha, rel)],
                          capture_output=True, text=True).stdout.strip()
    disk = subprocess.run(['git', '-C', repo, 'hash-object', path],
                          capture_output=True, text=True).stdout.strip()
    print('committed(%s) = %s' % (sha, head)); print('on disk        = %s' % disk)
    if head and head == disk:
        print('FROZEN: the comparator on disk IS the committed blob.'); return 0
    print('NOT FROZEN: the comparator on disk differs from the committed blob.'); return 1


# ------------------------------------------------------------ VMFL004 specifics
U_WALL   = 3.0            # m/s,   manual p.21 (velocity of the moving wall)
GAP      = 1.0            # m,     manual p.21 (width of the domain)
DPDX     = -12.0          # Pa/m,  manual p.21 (pressure gradient across periodics)
MU       = 1.0            # kg/m-s, manual p.21
# CLOSED FORM (Munson, Okiishi & Huebsch, Fundamentals of Fluid Mechanics 5e -- the
# manual's own cited Reference), plane Couette flow with a pressure gradient:
#     u(y) = U*y/b + (1/(2*mu)) * (dp/dx) * (y^2 - b*y)
# With U=3, b=1, mu=1, dp/dx=-12 this is  u(y) = 9y - 6y^2, peak 3.375 m/s at y=0.75.
# VERIFIED against the manual's OWN analytical table carried in the case archive
# (VMFL004_WB.wbpz -> .../Fluent/VMFL004_couette_analytical.xy): that file gives
# u = 0.6122449 at y = 0.0714286 and u = 3.3673469 at y = 0.7142857, and the formula
# above reproduces BOTH to every printed digit.
def u_exact(y):
    return U_WALL * y / GAP + (DPDX / (2.0 * MU)) * (y * y - GAP * y)

U_PEAK_REF = 3.375        # m/s at y = 0.75, from the closed form above (context only)
# GATE QUANTITY (supervisor Ruling 2, 2026-08-26): the section/volume-average of the
# x-velocity.  For plane Couette-Poiseuille u(y)=9y-6y^2 the exact mean over the gap is
#   <u> = INT_0^1 (9y - 6y^2) dy = 4.5 - 2 = 2.5 m/s, EXACT.
# This is the closed form the lab evaluates ITSELF, so the ceiling is PASS/HOLDS
# (VMFL019 precedent: closed form, figure-only manual -> verdict PASS).
U_MEAN_REF = 2.5          # m/s, EXACT closed-form section mean (manual p.21 geometry)
BAND_REL   = 1.0e-3       # frozen; justified in PREREGISTRATION.md sec.5
RESID_FLOOR = 1.0e-7      # frozen; rule 5 step 1
ENDTIME  = 20000
FIELDS   = ['U', 'p']
LEVELS   = ['L1', 'L2', 'L3']
PLANT    = 1.234e-03

import re as _re

def _vfv(level_dir):
    """Path to the volFieldValue.dat holding volAverage(U) (function object volAvgU)."""
    f = sorted(glob.glob(os.path.join(level_dir, 'postProcessing', 'volAvgU', '*',
                                      'volFieldValue.dat')))
    if not f:
        raise RuntimeError('no volAvgU/volFieldValue.dat under %s' % level_dir)
    return f[-1]

def _data_line(path):
    """The LAST non-comment data line of a volFieldValue.dat."""
    last = None
    for ln in open(path):
        if ln.startswith('#') or not ln.strip():
            continue
        last = ln.rstrip('\n')
    if last is None:
        raise RuntimeError('no data rows in %s' % path)
    return last

def _read_ux(path):
    """volAverage(U) x-component from the last data row.  A vector volFieldValue row is
    written as  <time>  (Ux Uy Uz) ; the gate reads Ux against 2.5 m/s EXACT."""
    ln = _data_line(path)
    m = _re.search(r'\(([^)]*)\)', ln)
    if not m:
        raise RuntimeError('no parenthesised vector in volAvgU row: %r' % ln)
    return float(m.group(1).split()[0])

def _perturb(path, plant):
    """Plant `plant` into the Ux component of the last data row, ON DISK (rule 3)."""
    lines = open(path).read().rstrip('\n').split('\n')
    for i in range(len(lines) - 1, -1, -1):
        ln = lines[i]
        if ln.startswith('#') or not ln.strip():
            continue
        m = _re.search(r'\(([^)]*)\)', ln)
        comps = m.group(1).split()
        comps[0] = repr(float(comps[0]) + plant)
        lines[i] = ln[:m.start()] + '(' + ' '.join(comps) + ')' + ln[m.end():]
        break
    open(path, 'w').write('\n'.join(lines) + '\n')

def channels(level_dir):
    p = _vfv(level_dir)
    ux = _read_ux(p)
    return {'volavg_ux_ms': ux, 'ref_ms': U_MEAN_REF,
            'rel_dev': abs(ux - U_MEAN_REF) / abs(U_MEAN_REF)}

def controls(level_dir):
    return {'volavg_ux_ms': planted_zero(_vfv(level_dir), _perturb, _read_ux,
                                         PLANT, 'volavg_ux_ms (section-mean X-velocity)')}
# ------------------------------------------------------------------- the driver
def selftest():
    n = p = 0
    def chk(name, cond):
        nonlocal n, p
        n += 1
        p += 1 if cond else 0
        print(('  ok   ' if cond else '  FAIL ') + name)
    print('--- %s --selftest' % os.path.basename(__file__))
    t = roache(1.0, 0.5, 0.25, 2.0);  chk('roache CONVERGING on a halving family', t['state'] == 'CONVERGING')
    chk('roache p == 1 on that family', abs(t['p'] - 1.0) < 1e-12)
    t = roache(16.0, 4.0, 1.0, 2.0);  chk('roache p == 2 on a quartering family', abs(t['p'] - 2.0) < 1e-12)
    chk('roache extrapolates that family to 0', abs(t['f_extrapolated']) < 1e-12)
    chk('roache EXACT when all three equal', roache(1.0, 1.0, 1.0)['state'] == 'EXACT')
    chk('roache STAGNANT on one null step', roache(1.0, 1.0, 0.5)['state'] == 'STAGNANT')
    chk('roache OSCILLATORY on a sign flip', roache(1.0, 0.5, 0.9)['state'] == 'OSCILLATORY')
    chk('roache DIVERGENT when steps grow', roache(1.0, 0.5, -1.0)['state'] == 'DIVERGENT')
    chk('no GCI quoted when not CONVERGING', roache(1.0, 1.0, 1.0)['gci_fine'] is None)
    d = tempfile.mkdtemp(prefix='st_')
    try:
        lv = os.path.join(d, 'L9'); os.makedirs(os.path.join(lv, '0'))
        open(os.path.join(lv, '0', 'U'), 'w').write('x')
        chk('strict completion REFUSES with no RUN_RC.txt',
            not strict_completion(lv, 10, ['U'])[0])
        open(os.path.join(lv, 'RUN_RC.txt'), 'w').write('rc = 1\n')
        open(os.path.join(lv, 'log.simpleFoam'), 'w').write('\nEnd\n')
        ok, why = strict_completion(lv, 10, ['U'])
        chk('strict completion REFUSES rc != 0', (not ok) and any('rc = 1' in r for r in why))
        chk('strict completion REFUSES a missing time dir', not ok)
        # BEHAVIOURAL test that the End line is read from log.simpleFoam BY NAME.
        # A `log*` glob matches log.blockMesh FIRST alphabetically, so a mesher End
        # line would be mistaken for a solver End line -- measured on this box.
        lv2 = os.path.join(d, 'L8'); os.makedirs(os.path.join(lv2, '0'))
        open(os.path.join(lv2, '0', 'U'), 'w').write('x')
        open(os.path.join(lv2, 'RUN_RC.txt'), 'w').write('rc = 0\n')
        open(os.path.join(lv2, 'log.blockMesh'), 'w').write('mesher\nEnd\n')
        open(os.path.join(lv2, 'log.simpleFoam'), 'w').write('solver ran, no End line\n')
        ok2, why2 = strict_completion(lv2, 10, ['U'])
        chk('the mesher End line is NOT accepted as the solver End line',
            (not ok2) and any('no End line in log.simpleFoam' in r for r in why2))
    finally:
        shutil.rmtree(d, ignore_errors=True)
    # The planted-zero control must REFUSE a blind reader, and ACCEPT a seeing one.
    # Checked IN-PROCESS by catching SystemExit.  An earlier version of this test
    # ran the comparator in a subprocess and asserted rc == 2 -- but argparse ALSO
    # exits 2, so that test passed for the wrong reason on a file it never really
    # exercised.  A control that can pass without the mechanism working is not a
    # control (CLAUDE.md rule 3).
    d = tempfile.mkdtemp(prefix='st2_')
    try:
        f = os.path.join(d, 'a.dat')
        open(f, 'w').write('# h\n0 1.0\n')
        blind_ok = False
        try:
            planted_zero(f, lambda p, v: None, lambda p: 0.0, 1.0, 'blind reader')
        except SystemExit as ex:
            blind_ok = (ex.code == 2)
        chk('planted-zero REFUSES (exit 2) a reader that cannot see the plant', blind_ok)

        def _see(p):
            return float(open(p).read().strip().split('\n')[-1].split()[-1])

        def _bump(p, v):
            ln = open(p).read().rstrip('\n').split('\n')
            g = ln[-1].split(); g[-1] = repr(float(g[-1]) + v)
            ln[-1] = ' '.join(g); open(p, 'w').write('\n'.join(ln) + '\n')
        seen = planted_zero(f, _bump, _see, 1.0, 'seeing reader')
        chk('planted-zero ACCEPTS a reader that DOES see the plant',
            seen['control'] == 'PASS' and abs(seen['delta_seen'] - 1.0) < 1e-9)
        chk('planted-zero left the REAL artifact untouched', abs(_see(f) - 1.0) < 1e-12)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    # channel reader on THIS case's real volFieldValue format (rule 3 on the gate file).
    d = tempfile.mkdtemp(prefix='st3_')
    try:
        vf = os.path.join(d, 'volFieldValue.dat')
        open(vf, 'w').write('# Time  volAverage(U)\n20000\t(2.5012 -1e-19 0)\n')
        chk('volAvg reader parses Ux from the vector row', abs(_read_ux(vf) - 2.5012) < 1e-9)
        seen = planted_zero(vf, _perturb, _read_ux, PLANT, 'volavg_ux_ms selftest')
        chk('planted-zero sees a plant in the Ux component',
            seen['control'] == 'PASS' and abs(seen['delta_seen'] - PLANT) < 1e-9)
        chk('planted-zero left the real volAvg row untouched', abs(_read_ux(vf) - 2.5012) < 1e-9)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    print('%d/%d' % (p, n))
    return 0 if p == n else 1

# ------------------------------------------------------------------- the driver
def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--run-root'); ap.add_argument('--out')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--verify-frozen')
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.verify_frozen:
        return verify_frozen(os.path.abspath(__file__), a.verify_frozen)
    if not a.run_root:
        ap.error('--run-root is required')
    R = {'case': 'VMFL004', 'manual_page': 21, 'endTime': ENDTIME,
         'reference': {'kind': 'V (exact closed form, lab-evaluated)',
                       'formula': 'u(y) = 9y - 6y^2 m/s ; section mean <u> = 2.5 m/s EXACT',
                       'gate_quantity': 'volAverage(U)_x',
                       'ref_ms': U_MEAN_REF, 'u_peak_ms_context': U_PEAK_REF,
                       'source': 'Munson, Okiishi & Huebsch, Fundamentals of Fluid Mechanics 5e -- the manual p.21 Reference; the manual prints only a FIGURE (Figure .04.2) and NO discrete target table, so the reference is the closed-form section mean, evaluated by the lab itself as INT_0^1 (9y-6y^2) dy = 2.5 m/s'},
         'bands': {'rel_dev': BAND_REL},
         'tier_ceiling': 'HOLDS',
         'levels': {}, 'blocking': []}
    triple_vals = []
    for L in LEVELS:
        d = os.path.join(a.run_root, L)
        e = {'dir': d}
        if not os.path.isdir(d):
            e['state'] = 'ABSENT'; R['levels'][L] = e
            R['blocking'].append('%s: run directory absent' % L); continue
        ok, why = strict_completion(d, ENDTIME, FIELDS)
        e['strict_completion'] = {'ok': ok, 'reasons': why}
        if not ok:
            e['state'] = 'INCOMPLETE'; R['levels'][L] = e
            R['blocking'].append('%s: strict completion (rule 4) FAILED: %s' % (L, '; '.join(why)))
            continue
        ic, res, msg = iterative_convergence(d, RESID_FLOOR, ['Ux_initial', 'Uy_initial', 'p_initial'])
        e['iterative_convergence'] = {'ok': ic, 'final_initial_residuals': res,
                                      'floor': RESID_FLOOR, 'note': msg}
        e['controls'] = controls(d)          # rule 3 -- exits 2 if the reader is blind
        c = channels(d); e['channels'] = c
        e['state'] = 'COMPLETE'
        if not ic:
            R['blocking'].append('%s: NOT iteratively converged (rule 5 step 1): %s' % (L, msg))
        triple_vals.append(c['volavg_ux_ms'])
        R['levels'][L] = e
    if len(triple_vals) == 3:
        R['triple'] = roache(*triple_vals)
        R['triple_on'] = 'volavg_ux_ms'
    else:
        R['blocking'].append('the grid triple is INCOMPLETE -- %d of 3 levels graded' % len(triple_vals))
    if R['blocking']:
        R['verdict'] = 'NOT A RESULT'; R['tier'] = 'NOT HELD'
    elif R['triple']['state'] != 'CONVERGING':
        R['verdict'] = 'NOT A RESULT'; R['tier'] = 'NOT HELD'
        R['blocking'].append('grid triple not CONVERGING: %s' % R['triple']['state'])
    else:
        ch = R['levels'][LEVELS[-1]]['channels']
        v = ch['rel_dev']
        R['deviation'] = {'rel_dev': v, 'band': BAND_REL,
                          'volavg_ux_ms': ch['volavg_ux_ms'], 'ref_ms': U_MEAN_REF}
        if v <= BAND_REL:
            R['verdict'] = 'PASS'; R['tier'] = 'HOLDS'
        else:
            R['verdict'] = 'GATE FAIL'; R['tier'] = 'NOT HELD'
    R['ceiling_note'] = ('The reference is an EXACT closed form the lab evaluates ITSELF '
        '(section mean <u> = 2.5 m/s).  Per supervisor Ruling 2 (2026-08-26) and the '
        'VMFL019 precedent (closed form, figure-only manual -> verdict PASS), such a case '
        'carries a PASS/HOLDS ceiling; it is a category-V credential, not a GATE-REACHED '
        'cap.  The EXACT risk (central differencing is exact for the quadratic nodal field) '
        'is dodged by gating on the volAverage, whose midpoint-quadrature error is O(h^2) '
        'and non-zero -> CONVERGING; were that error below write precision the triple would '
        'read EXACT/STAGNANT -> NOT A RESULT, an honest predicted outcome.')
    out = a.out or os.path.join(a.run_root, 'GRADING_VMFL004.json')
    json.dump(R, open(out, 'w'), indent=2, sort_keys=True)
    print(json.dumps({k: R[k] for k in ('verdict', 'tier', 'blocking') if k in R}, indent=2))
    print('written: %s' % out)
    return 0

if __name__ == '__main__':
    sys.exit(main())
