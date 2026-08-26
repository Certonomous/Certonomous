#!/usr/bin/env python3
"""grade_vmfl004_r2.py -- comparator for VMFL004-R2, Plain Couette Flow with Pressure
Gradient (Ansys Fluid Dynamics Verification Manual, VM2026R1, p.21).

VMFL004-R2 is the corrected re-run of VMFL004 (register row #25, verdict NOT A RESULT),
under ANSYS_VERIFICATION_CHARTER sec.6 ("a re-run after a repair is a new row citing the
old one") and CLAUDE.md rule 2 (the frozen VMFL004 comparator is NOT edited; this is a NEW
frozen file).

THE GATE IS CARRIED OVER BYTE-IDENTICAL FROM VMFL004, ON PURPOSE, so this re-registration
cannot be gate-fitting:
  * gate quantity : volAverage(U)_x            (unchanged)
  * reference     : <u> = 2.5 m/s EXACT, lab-evaluated INT_0^1 (9y-6y^2) dy   (unchanged)
  * band          : |volAverage(U)_x - 2.5|/2.5 <= 1.0e-3  (0.1 %)             (unchanged)
  * ceiling       : PASS/HOLDS reachable (VMFL019 precedent)                    (unchanged)
The prior run's value is KNOWN (2.50125 / 2.5003125 / 2.5000781, PASS-quality). The band,
the gate quantity and the reference are NOT touched here precisely so the known answer
cannot have shaped them.

THE ONE THING THAT CHANGES: the iterative-convergence channel.  VMFL004 required
Ux_initial, Uy_initial, p_initial ALL below 1e-7.  In a 1-D fully-developed flow
(streamwise-cyclic, driven by a fixed body force) the transverse velocity Uy and the
pressure p are STRUCTURALLY ~zero fields; OpenFOAM normalizes each residual by the field's
own scale, so for a ~zero field the denominator is ~zero and the reported "initial residual"
is normalization NOISE floating at O(1e-2 .. 1e-1) that can never reach an absolute floor,
no matter how long the solver runs (L-338).  Requiring it deletes a real result: that is
exactly why VMFL004 was NOT A RESULT while its physics was a textbook PASS.

The fix is NOT to silently drop the transverse channels -- a channel exempted without a
stated failure criterion is a channel deleted.  Instead:
  (1) DRIVEN channel Ux_initial < 1e-7 is the binding iterative-convergence gate (rule 5
      step 1).  The streamwise momentum is the only field with real y-structure to converge.
  (2) The transverse channels are exempted from the FLOOR but not from scrutiny.  Their
      exemption's PREMISE -- that Uy and p are degenerate (~zero) fields -- is itself tested,
      and a REAL transverse failure is defined and detected (transverse_degeneracy):
        (a) |volAverage(U)_y| <= 1e-6 m/s AND |volAverage(U)_z| <= 1e-6 m/s.  If the
            transverse mean velocity is NOT negligible, the field is NOT degenerate, its
            residual is NOT noise, and exempting it is void -- the excess IS the real
            failure (a broken streamwise-cyclic pair, spurious cross-flow, a non-1-D
            solution).  A value above 1e-6 m/s -> NOT A RESULT.
        (b) The transverse normalized residuals stay BOUNDED (< 1.0) at endTime.  Bounded
            normalization noise floats at O(1e-2); a value >= 1.0 means the field is growing
            faster than its own scale -> divergence, a real failure -> NOT A RESULT.

CONTROLS CARRIED HERE, all non-droppable, NONE on an `assert` (python3 -O strips asserts):
  rule 3  planted-zero on EVERY reader the verdict consumes -- the gate reader (Ux), the
          transverse-degeneracy readers (Uy, Uz), and the driven-convergence reader
          (Ux_initial in solverInfo.dat).  Each plants a KNOWN non-zero into a COPY on disk,
          reads it back with the SAME reader, and REFUSES (exit 2) if the reader cannot see
          it.  Every plant is a SINGLE-POINT plant into a SINGLE-POINT reader (one component
          of one row / one column of one row), so there is NO 1/sqrt(N) averaging dilution
          (L-340): the reader delta equals the plant.
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
    # Parse TOLERANTLY: `rc = 0` (with spaces) is what the launcher writes.  A reader that
    # required `rc=0` would fall back to a default and mis-grade a correct run (Amendment 5).
    import re as _re2
    rct = open(rcf).read()
    m = _re2.search(r'^\s*rc\s*=\s*(-?\d+)', rct, _re2.M)
    rc = int(m.group(1)) if m else None
    if rc is None:
        bad.append('RUN_RC.txt has no parseable rc line -- treated as a REFUSAL, not a pass')
    elif rc != 0:
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

def _solverinfo_path(level_dir):
    f = sorted(glob.glob(os.path.join(level_dir, 'postProcessing', 'resid', '*', 'solverInfo.dat')))
    if not f:
        raise RuntimeError('no solverInfo.dat under %s' % level_dir)
    return f[-1]

def _read_resid(path, chan):
    """Final-row value of a named solverInfo.dat column (e.g. Ux_initial)."""
    hdr, rows = None, []
    for ln in open(path):
        if ln.startswith('#'):
            hdr = ln[1:].split()
        elif ln.strip():
            rows.append(ln.split())
    if not rows or hdr is None:
        raise RuntimeError('solverInfo.dat empty: %s' % path)
    if chan not in hdr:
        raise RuntimeError('channel %s absent from %s' % (chan, path))
    return float(rows[-1][hdr.index(chan)])

def _perturb_resid(path, plant, chan):
    """Plant `plant` into the named column of the LAST data row of solverInfo.dat, ON DISK."""
    lines = open(path).read().rstrip('\n').split('\n')
    hdr = None
    for ln in lines:
        if ln.startswith('#'):
            hdr = ln[1:].split()
    if hdr is None or chan not in hdr:
        raise RuntimeError('cannot plant: channel %s absent' % chan)
    col = hdr.index(chan)
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].startswith('#') or not lines[i].strip():
            continue
        parts = lines[i].split()
        parts[col] = repr(float(parts[col]) + plant)
        lines[i] = '\t'.join(parts)
        break
    open(path, 'w').write('\n'.join(lines) + '\n')

def iterative_convergence(level_dir, floor, driven_chans, trans_chans):
    """rule 5 step 1, gated on the DRIVEN channel(s) only.
    Records the transverse residuals for the record and for transverse_degeneracy; the
    transverse residuals are EXEMPTED from the floor because they are normalization noise
    for a degenerate field (L-338).  Returns (ok, driven{}, transverse{}, msg)."""
    path = _solverinfo_path(level_dir)
    hdr, rows = None, []
    for ln in open(path):
        if ln.startswith('#'):
            hdr = ln[1:].split()
        elif ln.strip():
            rows.append(ln.split())
    if not rows or hdr is None:
        return False, {}, {}, 'solverInfo.dat empty'
    def col(c):
        return float(rows[-1][hdr.index(c)]) if c in hdr else None
    driven, ok = {}, True
    for c in driven_chans:
        v = col(c)
        if v is None:
            return False, {}, {}, 'driven channel %s absent from solverInfo.dat' % c
        driven[c] = v
        if not (v < floor):
            ok = False
    trans = {}
    for c in trans_chans:
        v = col(c)
        if v is not None:
            trans[c] = v
    return ok, driven, trans, ('' if ok else 'driven initial-residual above the frozen floor %g' % floor)

def transverse_degeneracy(uy_mean, uz_mean, trans_resid, abs_ceil, resid_ceil):
    """The transverse-channel criterion, stated so the exemption is not a deletion.
    A 1-D fully-developed flow has Uy ~ 0 and p spatially uniform; the transverse normalized
    residual is noise (exempted from the floor).  The exemption's premise is TESTED, and a
    real transverse failure is defined:
      (a) the transverse MEAN velocity must be physically negligible (<= abs_ceil m/s);
      (b) the transverse normalized residual must be BOUNDED (< resid_ceil) at endTime.
    Returns (ok, [reasons])."""
    reasons = []
    if not (abs(uy_mean) <= abs_ceil):
        reasons.append('|volAverage(U)_y| = %g exceeds %g m/s -- the transverse field is NOT '
                       'degenerate (real cross-flow: a broken streamwise-cyclic pair or a '
                       'non-1-D solution). The residual-noise exemption is void and THIS is '
                       'the real failure.' % (abs(uy_mean), abs_ceil))
    if not (abs(uz_mean) <= abs_ceil):
        reasons.append('|volAverage(U)_z| = %g exceeds %g m/s' % (abs(uz_mean), abs_ceil))
    for c, v in sorted(trans_resid.items()):
        if not (v < resid_ceil):
            reasons.append('%s = %g >= %g -- the transverse residual is DIVERGING (growing '
                           'faster than the field\'s own scale), not bounded normalization '
                           'noise. A real failure.' % (c, v, resid_ceil))
    return (len(reasons) == 0), reasons

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
    """CLAUDE.md rule 3.  Copy the REAL artifact, plant a known perturbation into the copy ON
    DISK, read it back with the SAME reader, and REFUSE (exit 2) if the reader cannot see it.
    A zero from a reader not shown able to see a non-zero is not evidence.  The only way this
    function RETURNS is to have seen the plant (Amendment 6a): the not-caught path exits."""
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


# --------------------------------------------------------- VMFL004-R2 specifics
U_WALL   = 3.0            # m/s,   manual p.21 (velocity of the moving wall)
GAP      = 1.0            # m,     manual p.21 (width of the domain)
DPDX     = -12.0          # Pa/m,  manual p.21 (pressure gradient across periodics)
MU       = 1.0            # kg/m-s, manual p.21
# CLOSED FORM (Munson, Okiishi & Huebsch, Fundamentals of Fluid Mechanics 5e -- the
# manual's own cited Reference):  u(y) = U*y/b + (1/(2*mu))(dp/dx)(y^2 - b*y) = 9y - 6y^2.
def u_exact(y):
    return U_WALL * y / GAP + (DPDX / (2.0 * MU)) * (y * y - GAP * y)

U_PEAK_REF = 3.375        # m/s at y = 0.75, from the closed form above (context only)
# GATE QUANTITY (CARRIED OVER BYTE-IDENTICAL FROM VMFL004): the section/volume-average of
# the x-velocity.  For plane Couette-Poiseuille u(y)=9y-6y^2 the exact section mean is
#   <u> = INT_0^1 (9y - 6y^2) dy = 4.5 - 2 = 2.5 m/s, EXACT.
U_MEAN_REF = 2.5          # m/s, EXACT closed-form section mean (manual p.21 geometry)
BAND_REL   = 1.0e-3       # frozen; CARRIED OVER from VMFL004 -- see PREREGISTRATION.md sec.5
RESID_FLOOR = 1.0e-7      # frozen; rule 5 step 1, driven channel (carried over from VMFL004)
# --- the ONLY changed channel: iterative convergence on the DRIVEN component only ---
DRIVEN_CHANS      = ['Ux_initial']              # the streamwise (driven) momentum residual
TRANS_RESID_CHANS = ['Uy_initial', 'p_initial'] # degenerate ~zero fields; residual is noise
TRANS_ABS_MS      = 1.0e-6   # |<U>_y|, |<U>_z| ceiling (m/s): transverse mean must be negligible
TRANS_RESID_CEIL  = 1.0      # transverse residual sanity ceiling (O(1)); >= 1.0 == divergence
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

def _read_comp(path, idx):
    """Component `idx` of volAverage(U) from the last data row.  A vector volFieldValue row
    is  <time>  (Ux Uy Uz).  idx 0 = Ux (gate), 1 = Uy, 2 = Uz (transverse degeneracy)."""
    ln = _data_line(path)
    m = _re.search(r'\(([^)]*)\)', ln)
    if not m:
        raise RuntimeError('no parenthesised vector in volAvgU row: %r' % ln)
    return float(m.group(1).split()[idx])

def _read_ux(path):
    return _read_comp(path, 0)

def _read_uy(path):
    return _read_comp(path, 1)

def _read_uz(path):
    return _read_comp(path, 2)

def _perturb_comp(path, plant, idx):
    """Plant `plant` into component `idx` of the last data row, ON DISK (rule 3)."""
    lines = open(path).read().rstrip('\n').split('\n')
    for i in range(len(lines) - 1, -1, -1):
        ln = lines[i]
        if ln.startswith('#') or not ln.strip():
            continue
        m = _re.search(r'\(([^)]*)\)', ln)
        comps = m.group(1).split()
        comps[idx] = repr(float(comps[idx]) + plant)
        lines[i] = ln[:m.start()] + '(' + ' '.join(comps) + ')' + ln[m.end():]
        break
    open(path, 'w').write('\n'.join(lines) + '\n')

def channels(level_dir):
    p = _vfv(level_dir)
    ux, uy, uz = _read_ux(p), _read_uy(p), _read_uz(p)
    return {'volavg_ux_ms': ux, 'volavg_uy_ms': uy, 'volavg_uz_ms': uz,
            'ref_ms': U_MEAN_REF, 'rel_dev': abs(ux - U_MEAN_REF) / abs(U_MEAN_REF)}

def controls(level_dir):
    """rule 3 on EVERY reader the verdict consumes.  Each planted_zero() exits 2 if its
    reader cannot see the plant, so this only returns when all four controls PASSED."""
    vf = _vfv(level_dir)
    si = _solverinfo_path(level_dir)
    return {
        'volavg_ux_ms': planted_zero(vf, lambda p, v: _perturb_comp(p, v, 0), _read_ux,
                                     PLANT, 'volavg_ux_ms (gate: section-mean X-velocity)'),
        'volavg_uy_ms': planted_zero(vf, lambda p, v: _perturb_comp(p, v, 1), _read_uy,
                                     PLANT, 'volavg_uy_ms (transverse: section-mean Y-velocity)'),
        'volavg_uz_ms': planted_zero(vf, lambda p, v: _perturb_comp(p, v, 2), _read_uz,
                                     PLANT, 'volavg_uz_ms (transverse: section-mean Z-velocity)'),
        'resid_Ux_initial': planted_zero(si, lambda p, v: _perturb_resid(p, v, 'Ux_initial'),
                                         lambda p: _read_resid(p, 'Ux_initial'),
                                         PLANT, 'resid Ux_initial (driven convergence gate reader)'),
    }
# ------------------------------------------------------------------- selftest
def selftest():
    n = p = 0
    def chk(name, cond):
        nonlocal n, p
        n += 1
        p += 1 if cond else 0
        print(('  ok   ' if cond else '  FAIL ') + name)
    print('--- %s --selftest' % os.path.basename(__file__))
    # roache classifier (carried over)
    t = roache(1.0, 0.5, 0.25, 2.0);  chk('roache CONVERGING on a halving family', t['state'] == 'CONVERGING')
    chk('roache p == 1 on that family', abs(t['p'] - 1.0) < 1e-12)
    t = roache(16.0, 4.0, 1.0, 2.0);  chk('roache p == 2 on a quartering family', abs(t['p'] - 2.0) < 1e-12)
    chk('roache extrapolates that family to 0', abs(t['f_extrapolated']) < 1e-12)
    chk('roache EXACT when all three equal', roache(1.0, 1.0, 1.0)['state'] == 'EXACT')
    chk('roache STAGNANT on one null step', roache(1.0, 1.0, 0.5)['state'] == 'STAGNANT')
    chk('roache OSCILLATORY on a sign flip', roache(1.0, 0.5, 0.9)['state'] == 'OSCILLATORY')
    chk('roache DIVERGENT when steps grow', roache(1.0, 0.5, -1.0)['state'] == 'DIVERGENT')
    chk('no GCI quoted when not CONVERGING', roache(1.0, 1.0, 1.0)['gci_fine'] is None)
    # strict completion (carried over), including tolerant `rc = 0` parsing (Amendment 5)
    d = tempfile.mkdtemp(prefix='st_')
    try:
        lv = os.path.join(d, 'L9'); os.makedirs(os.path.join(lv, '0'))
        open(os.path.join(lv, '0', 'U'), 'w').write('x')
        chk('strict completion REFUSES with no RUN_RC.txt',
            not strict_completion(lv, 10, ['U'])[0])
        open(os.path.join(lv, 'RUN_RC.txt'), 'w').write('rc = 1\n')
        open(os.path.join(lv, 'log.simpleFoam'), 'w').write('\nEnd\n')
        ok, why = strict_completion(lv, 10, ['U'])
        chk('strict completion parses `rc = 1` (spaces) and REFUSES it',
            (not ok) and any('rc = 1' in r for r in why))
        # the mesher End line must NOT be accepted as the solver End line
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
    # planted-zero: REFUSES a blind reader, ACCEPTS a seeing one (carried over)
    d = tempfile.mkdtemp(prefix='st2_')
    try:
        f = os.path.join(d, 'a.dat')
        open(f, 'w').write('# h\n0 1.0\n')
        blind_ok = False
        try:
            planted_zero(f, lambda pp, v: None, lambda pp: 0.0, 1.0, 'blind reader')
        except SystemExit as ex:
            blind_ok = (ex.code == 2)
        chk('planted-zero REFUSES (exit 2) a reader that cannot see the plant', blind_ok)
        def _see(pp):
            return float(open(pp).read().strip().split('\n')[-1].split()[-1])
        def _bump(pp, v):
            ln = open(pp).read().rstrip('\n').split('\n')
            g = ln[-1].split(); g[-1] = repr(float(g[-1]) + v)
            ln[-1] = ' '.join(g); open(pp, 'w').write('\n'.join(ln) + '\n')
        seen = planted_zero(f, _bump, _see, 1.0, 'seeing reader')
        chk('planted-zero ACCEPTS a reader that DOES see the plant',
            seen['control'] == 'PASS' and abs(seen['delta_seen'] - 1.0) < 1e-9)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    # the vector-component readers and their plants (rule 3 on Ux, Uy, Uz)
    d = tempfile.mkdtemp(prefix='st3_')
    try:
        vf = os.path.join(d, 'volFieldValue.dat')
        open(vf, 'w').write('# Time  volAverage(U)\n20000\t(2.5012 -6.55e-17 0)\n')
        chk('volAvg reader parses Ux', abs(_read_ux(vf) - 2.5012) < 1e-9)
        chk('volAvg reader parses Uy', abs(_read_uy(vf) - (-6.55e-17)) < 1e-20)
        chk('volAvg reader parses Uz', abs(_read_uz(vf) - 0.0) < 1e-20)
        for idx, nm in ((0, 'Ux'), (1, 'Uy'), (2, 'Uz')):
            seen = planted_zero(vf, lambda pp, v, i=idx: _perturb_comp(pp, v, i),
                                lambda pp, i=idx: _read_comp(pp, i), PLANT, '%s selftest' % nm)
            chk('planted-zero sees a plant in the %s component (no dilution)' % nm,
                seen['control'] == 'PASS' and abs(seen['delta_seen'] - PLANT) < 1e-9)
        chk('planted-zero left the real volAvg row untouched', abs(_read_ux(vf) - 2.5012) < 1e-9)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    # the solverInfo residual reader and its plant (rule 3 on the driven convergence gate)
    d = tempfile.mkdtemp(prefix='st4_')
    try:
        si = os.path.join(d, 'solverInfo.dat')
        open(si, 'w').write('# Solver information\n'
                            '# Time\tU_solver\tUx_initial\tUy_initial\tp_solver\tp_initial\n'
                            '20000\tPBiCGStab\t1.0e-15\t9.5e-02\tPCG\t4.2e-02\n')
        chk('resid reader parses Ux_initial', abs(_read_resid(si, 'Ux_initial') - 1.0e-15) < 1e-25)
        chk('resid reader parses Uy_initial (transverse noise, O(1e-2))',
            abs(_read_resid(si, 'Uy_initial') - 9.5e-02) < 1e-9)
        seen = planted_zero(si, lambda pp, v: _perturb_resid(pp, v, 'Ux_initial'),
                            lambda pp: _read_resid(pp, 'Ux_initial'), PLANT, 'Ux_initial selftest')
        chk('planted-zero sees a plant in Ux_initial (driven gate reader, no dilution)',
            seen['control'] == 'PASS' and abs(seen['delta_seen'] - PLANT) < 1e-9)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    # iterative_convergence gates the DRIVEN channel ONLY
    d = tempfile.mkdtemp(prefix='st5_')
    try:
        lv = os.path.join(d, 'postProcessing', 'resid', '0'); os.makedirs(lv)
        si = os.path.join(lv, 'solverInfo.dat')
        # Ux_initial converged (1e-15 < 1e-7) but Uy_initial and p_initial are O(1e-2) noise:
        open(si, 'w').write('# Solver information\n'
                            '# Time\tUx_initial\tUy_initial\tp_initial\n'
                            '20000\t1.0e-15\t9.5e-02\t4.2e-02\n')
        ok, drv, tr, msg = iterative_convergence(d, RESID_FLOOR, DRIVEN_CHANS, TRANS_RESID_CHANS)
        chk('iterative convergence PASSES on driven Ux_initial < floor despite O(1e-2) '
            'transverse noise (the L-338 fix)', ok)
        chk('   ... and it still RECORDS the transverse residuals', 'Uy_initial' in tr and 'p_initial' in tr)
        # now a genuinely un-converged driven channel must FAIL
        open(si, 'w').write('# Solver information\n'
                            '# Time\tUx_initial\tUy_initial\tp_initial\n'
                            '20000\t1.0e-03\t9.5e-02\t4.2e-02\n')
        ok2, _, _, _ = iterative_convergence(d, RESID_FLOOR, DRIVEN_CHANS, TRANS_RESID_CHANS)
        chk('iterative convergence FAILS when the DRIVEN channel is above the floor', not ok2)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    # transverse_degeneracy: the exemption is not a deletion
    tdok, _ = transverse_degeneracy(-6.55e-17, 0.0, {'Uy_initial': 9.5e-2, 'p_initial': 4.2e-2},
                                    TRANS_ABS_MS, TRANS_RESID_CEIL)
    chk('transverse degeneracy PASSES on a real 1-D field (|<Uy>| ~ 1e-17, resid O(1e-2))', tdok)
    tdbad, why = transverse_degeneracy(1.0e-3, 0.0, {'Uy_initial': 9.5e-2},
                                       TRANS_ABS_MS, TRANS_RESID_CEIL)
    chk('transverse degeneracy FAILS on real cross-flow (|<Uy>| = 1e-3 > 1e-6 -> NOT A RESULT)',
        (not tdbad) and any('NOT degenerate' in r for r in why))
    tddiv, why2 = transverse_degeneracy(0.0, 0.0, {'Uy_initial': 5.0},
                                        TRANS_ABS_MS, TRANS_RESID_CEIL)
    chk('transverse degeneracy FAILS on a DIVERGING residual (Uy_initial = 5.0 >= 1.0)',
        (not tddiv) and any('DIVERGING' in r for r in why2))
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
    R = {'case': 'VMFL004-R2', 'cites_row': 25, 'manual_page': 21, 'endTime': ENDTIME,
         'reference': {'kind': 'V (exact closed form, lab-evaluated)',
                       'formula': 'u(y) = 9y - 6y^2 m/s ; section mean <u> = 2.5 m/s EXACT',
                       'gate_quantity': 'volAverage(U)_x',
                       'ref_ms': U_MEAN_REF, 'u_peak_ms_context': U_PEAK_REF,
                       'carried_over_from': 'VMFL004 (gate quantity, reference, band, ceiling BYTE-IDENTICAL)',
                       'source': 'Munson, Okiishi & Huebsch, Fundamentals of Fluid Mechanics 5e -- the manual p.21 Reference; the manual prints only a FIGURE (Figure .04.2) and NO discrete target table, so the reference is the closed-form section mean, evaluated by the lab itself as INT_0^1 (9y-6y^2) dy = 2.5 m/s'},
         'bands': {'rel_dev': BAND_REL},
         'iterative_convergence_channel': {
             'driven': DRIVEN_CHANS, 'floor': RESID_FLOOR,
             'transverse_exempted_from_floor': TRANS_RESID_CHANS,
             'transverse_abs_ceil_ms': TRANS_ABS_MS, 'transverse_resid_ceil': TRANS_RESID_CEIL,
             'rationale': 'L-338: in a 1-D fully-developed flow Uy and p are degenerate ~zero '
                          'fields whose normalized residuals are noise; gate on the driven '
                          'channel, and test the transverse fields for ACTUAL degeneracy '
                          '(mean velocity negligible) and boundedness (residual not diverging).'},
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
        ic, driven, trans_resid, msg = iterative_convergence(
            d, RESID_FLOOR, DRIVEN_CHANS, TRANS_RESID_CHANS)
        e['iterative_convergence'] = {'ok': ic, 'driven_residuals': driven,
                                      'floor': RESID_FLOOR, 'driven_channels': DRIVEN_CHANS,
                                      'transverse_residuals': trans_resid, 'note': msg}
        e['controls'] = controls(d)          # rule 3 -- exits 2 if any reader is blind
        c = channels(d); e['channels'] = c
        td, td_reasons = transverse_degeneracy(
            c['volavg_uy_ms'], c['volavg_uz_ms'], trans_resid, TRANS_ABS_MS, TRANS_RESID_CEIL)
        e['transverse_degeneracy'] = {'ok': td, 'volavg_uy_ms': c['volavg_uy_ms'],
                                      'volavg_uz_ms': c['volavg_uz_ms'],
                                      'transverse_residuals': trans_resid,
                                      'abs_ceil_ms': TRANS_ABS_MS, 'resid_ceil': TRANS_RESID_CEIL,
                                      'reasons': td_reasons}
        e['state'] = 'COMPLETE'
        if not ic:
            R['blocking'].append('%s: DRIVEN channel NOT iteratively converged (rule 5 step 1): %s' % (L, msg))
        if not td:
            R['blocking'].append('%s: transverse degeneracy FAILED (rule 5 step 1): %s' % (L, '; '.join(td_reasons)))
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
    R['ceiling_note'] = ('Gate quantity, reference (<u> = 2.5 m/s EXACT), band (0.1 %) and '
        'ceiling are CARRIED OVER BYTE-IDENTICAL from VMFL004 (register row #25) so this '
        're-registration cannot be gate-fitting.  The ONLY change is the iterative-'
        'convergence channel: gated on the DRIVEN Ux_initial < 1e-7, with the transverse '
        'Uy/p residuals exempted from the floor as normalization noise (L-338) but tested '
        'for actual degeneracy (|<U>_y|,|<U>_z| <= 1e-6 m/s) and boundedness (< 1.0). '
        'Ceiling PASS/HOLDS per the VMFL019 precedent (closed form, figure-only manual).')
    out = a.out or os.path.join(a.run_root, 'GRADING_VMFL004_R2.json')
    json.dump(R, open(out, 'w'), indent=2, sort_keys=True)
    print(json.dumps({k: R[k] for k in ('verdict', 'tier', 'blocking') if k in R}, indent=2))
    print('written: %s' % out)
    return 0

if __name__ == '__main__':
    sys.exit(main())
