#!/usr/bin/env python3
"""grade_vmfl011_r2.py -- comparator for VMFL011-R2, Laminar Flow in a Triangular
Cavity (Ansys Fluid Dynamics Verification Manual, VM2026R1, p.41).

RE-REGISTRATION OF VMFL011 under ANSYS_VERIFICATION_CHARTER section 6 (a NEW
register row that cites row #26 and never overwrites it).  Parent comparator blob
e369496bf2e28ccb7145756e1c2442eb11e8e3f7.  Parent pre-registration blob
4bd8c4285e379e93e1ad4e6c2b9967604d042523.

WHAT THE PARENT'S REFUSAL NAMED, AND THE ONLY THING THIS FILE CHANGES ON THE
GRADING PATH.  L-340: the parent planted 1.234e-3 into ONE row of bisect_U.xy and
read it back through an RMS over N = 46 benchmark abscissae.  An averaging reader
dilutes a single-point plant, so the read moved by 3.67709e-07 against a threshold
of 0.1*plant = 1.234e-04 and the comparator REFUSED a WORKING reader.  This file
sizes the plant PER CHANNEL to the reader it drives:

  * u_min_norm  -- a POINT reader (a min over the profile).  Plant, perturbation
                   shape and threshold are BYTE-IDENTICAL to the parent: one row,
                   -abs(PLANT)*100, delta > 0.1*|plant|.  It passed; it is not
                   touched.
  * rms_vs_benchmark -- an AVERAGING reader.  The perturbation is applied to EVERY
                   data row (_perturb_all), and its magnitude is sized from the
                   reader's OWN baseline: P = RMS_PLANT_K * U_WALL * max(base,
                   RMS_PLANT_FLOOR).  The THRESHOLD RULE is unchanged
                   (delta > 0.1*|plant|); only the plant is sized.

THE SIZING IS A THEOREM, NOT A TUNING.  With e_i = u_i/U_WALL - b_i,
base = sqrt(mean(e^2)) and <e> = mean(e), a uniform raw plant P shifts every e_i by
exactly d = P/U_WALL (linear interpolation of a uniformly shifted sampled function
is uniformly shifted, and _interp's end-clamping preserves that).  Hence
    new^2 = base^2 + 2*d*<e> + d^2 ,  and  |<e>| <= base  (Cauchy-Schwarz).
With d = K*base the worst case <e> = -base gives new = (K-1)*base, so
    (K-2)*base <= delta <= K*base ,
while the threshold is 0.1*P = 0.1*K*U_WALL*base.  The control is GUARANTEED to
pass for any working reader iff K*(1 - 0.1*U_WALL) > 2, i.e. K > 2.5 at U_WALL = 2.
K = 4 is registered, giving a worst-case margin of (K-2)/(0.1*K*U_WALL) = 2.5x.
No measured value entered that choice.

CARRIED BYTE-IDENTICAL FROM THE PARENT AND RE-CHECKED BY frozen_constants_control():
the gate quantity (rms_vs_benchmark at the finest level), the reference
(reference/vmfl011_benchmark_xnorm.csv, blob 9f11191b8c823eb32edd3f2b74bd29da855aab55),
the band BAND_RMS = 0.030, the tier ceiling GATE REACHED, U_WALL = 2.0,
ENDTIME = 20000, RESID_FLOOR = 1.0e-7, PLANT = 1.234e-3, the Roache classifier and
the triple channel u_min_norm.

ALSO CHANGED, EACH DISCLOSED IN THE PRE-REGISTRATION, NEITHER ON THE GATE:
  * P_MIN = 0.05 observed-order floor (docs/ansys_verification/FINDING_p_floor.md
    section 4).  It can only turn a result INTO NOT A RESULT (rule 5's fixed
    direction); it can never turn a NOT A RESULT into a pass.
  * L-342 field classes.  Sanaa, verbatim: "a bookkeeping failure invalidates the
    bookkeeping, never the physics artifacts".  RUN_RC is INFRASTRUCTURE: absent ->
    rc is reported NOT MEASURED and the grade PROCEEDS on the physics artefacts;
    present and non-zero -> REFUSE.  Every physics-critical conjunct of rule 4 is
    unchanged and still gates.

CONTROLS, all non-droppable, NONE on an `assert` (L-332: python3 -O deletes every
assert, so a refusal written as one is a refusal offer).  ast.Assert count in this
file is measured by the file itself, and the counter is shown able to count a
planted assert.  Every refusal is a sys.exit(2).
"""
# ---------------------------------------------------------------- shared core
import os, sys, ast, glob, json, math, shutil, tempfile, subprocess

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

def refuse(msg):
    """The ONLY refusal primitive.  A raise/exit, never an assert (L-332)."""
    sys.stderr.write('REFUSING (exit 2): %s\n' % msg)
    sys.exit(2)

def expect_refusal(scratch, fn, *args, **kw):
    """Run a probe that MUST refuse, capturing its stderr so the selftest output is
    DETERMINISTIC (a temp path differs between two invocations, and the launcher
    compares the python3 and python3 -O outputs byte for byte).  Returns
    (exit_code_or_None, normalised_message).  The message is kept and printed --
    a refusal that is swallowed is a refusal nobody can audit."""
    import io
    buf, old = io.StringIO(), sys.stderr
    sys.stderr = buf
    code = None
    try:
        fn(*args, **kw)
    except SystemExit as ex:
        code = ex.code
    finally:
        sys.stderr = old
    txt = buf.getvalue().replace(scratch, '<scratch>').strip()
    return code, txt

# ------------------------------------------------- rule 4 with L-342 classes
PHYSICS_CRITICAL = ['End line in log.simpleFoam (by exact name)',
                    'last time == endTime',
                    'registered fields present at endTime',
                    'ExecutionTime count == endTime',
                    'age guard: every field at endTime newer than the case own 0/']
INFRASTRUCTURE = ['RUN_RC.<level> (rc, wall_s, core_min, timeout_s)', 'COST.txt']

def _read_rc(rc_path):
    """INFRASTRUCTURE reader (L-342).  Returns (rc, note).  rc is None when the
    record is absent or unparseable -- that is a BOOKKEEPING defect, reported and
    never a verdict."""
    if not os.path.isfile(rc_path):
        return None, 'RUN_RC absent at %s -- rc NOT MEASURED (L-342 infrastructure); the grade proceeds on the physics artefacts' % rc_path
    rc = None
    for ln in open(rc_path, errors='replace'):
        s = ln.strip()
        if s.startswith('rc') and '=' in s:
            try:
                rc = int(s.split('=', 1)[1].strip())
            except ValueError:
                rc = None
    if rc is None:
        return None, 'RUN_RC at %s carries no parseable `rc = <int>` line -- rc NOT MEASURED (L-342 infrastructure)' % rc_path
    return rc, ''

def strict_completion(level_dir, endtime, fields, rc_path):
    """CLAUDE.md rule 4 -- every PHYSICS-CRITICAL clause, or the level is NOT
    complete.  Returns (ok, [reasons], infra).  Refuses rather than degrading.
    L-342: an absent RUN_RC is a bookkeeping defect, not a physics failure."""
    bad = []
    rc, rc_note = _read_rc(rc_path)
    infra = {'rc': rc, 'rc_measured': rc is not None, 'rc_path': rc_path,
             'notes': [rc_note] if rc_note else []}
    if rc is not None and rc != 0:
        bad.append('rc = %s (rule 4 requires 0; the record is present and says the '
                   'solver did not exit clean -- absence is a disclosure, a bad '
                   'value is not)' % rc)
    # (2) the End line -- log.simpleFoam BY EXACT NAME.  A `log*` glob matches
    # log.blockMesh FIRST alphabetically and would report the MESHER's End line.
    slog = os.path.join(level_dir, 'log.simpleFoam')
    if not os.path.isfile(slog):
        bad.append('no log.simpleFoam')
        return False, bad, infra
    txt = open(slog, errors='replace').read()
    if '\nEnd\n' not in txt:
        bad.append('no End line in log.simpleFoam')
    # (3) last time == endTime
    ts = _times(level_dir)
    if not ts:
        bad.append('no time directories')
        return False, bad, infra
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
    return (len(bad) == 0), bad, infra

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

P_MIN = 0.05      # observed-order floor; docs/ansys_verification/FINDING_p_floor.md sec.4

def roache(f1, f2, f3, r=2.0):
    """CLAUDE.md rule 5.  f1 coarse, f2 medium, f3 fine.  Fs = 1.25.
    Never quotes a GCI when the three values are not monotone, and never quotes one
    on an observed order below P_MIN -- an order that small is not an order, and the
    Richardson extrapolation divides by r**p - 1, which goes to zero with it.
    DEGENERATE, like every other non-CONVERGING state, is NOT A RESULT: the floor can
    only turn a result INTO NOT A RESULT, never the reverse."""
    e32, e21 = f3 - f2, f2 - f1
    out = {'f_coarse': f1, 'f_medium': f2, 'f_fine': f3, 'r': r,
           'e21': e21, 'e32': e32, 'p': None, 'gci_fine': None,
           'f_extrapolated': None, 'p_min': P_MIN}
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
    if p < P_MIN:
        out['state'] = 'DEGENERATE'
        return out
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
    not evidence.

    THE THRESHOLD RULE IS THE PARENT'S, CHARACTER FOR CHARACTER: delta > 0.1*|plant|.
    L-340 is answered by SIZING THE PLANT per channel at the call site, never by
    loosening this test.  The only way out of this function is to have seen the
    plant."""
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
                'perturbed': seen, 'delta_seen': delta,
                'threshold': 0.1 * abs(plant), 'control': 'PASS'}
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


# ------------------------------------------------------------ VMFL011 specifics
# EVERY constant in this block is BYTE-IDENTICAL to the parent comparator except
# the two RMS_PLANT_* values, which exist only inside the rule-3 control and can
# reach no verdict.  frozen_constants_control() re-checks them and REFUSES on drift.
U_WALL   = 2.0            # m/s, manual p.41 (velocity of the top/base wall)
BAND_RMS = 0.030          # frozen; justified in the parent PREREGISTRATION.md sec.5
RESID_FLOOR = 1.0e-7      # frozen; rule 5 step 1
ENDTIME  = 20000
FIELDS   = ['U', 'p']
LEVELS   = ['L1', 'L2', 'L3']
PLANT    = 1.234e-03      # the POINT-reader plant, unchanged
TIER_CEILING = 'GATE REACHED'
# --- the L-340 repair, and the whole of it ----------------------------------
RMS_PLANT_K     = 4.0     # K > 2.5 is required at U_WALL = 2; 4 gives a 2.5x margin
RMS_PLANT_FLOOR = 1.0e-6  # so a run that matched the benchmark exactly still plants

def rms_plant_for(base):
    """Size the plant to the AVERAGING reader (L-340).  Derivation in the module
    docstring; driven by rms_sizing_control() on real bytes and on an adversarial
    profile a FIXED plant cannot move at all."""
    return RMS_PLANT_K * U_WALL * max(abs(base), RMS_PLANT_FLOOR)

def _ref_csv():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'reference', 'vmfl011_benchmark_xnorm.csv')

def _bench():
    ys, vs = [], []
    for ln in open(_ref_csv()):
        if ln.startswith('#') or not ln.strip():
            continue
        a, b = ln.strip().split(',')
        ys.append(float(a)); vs.append(float(b))
    z = sorted(zip(ys, vs))
    return [t[0] for t in z], [t[1] for t in z]

def _xy(level_dir):
    f = sorted(glob.glob(os.path.join(level_dir, 'postProcessing', 'bisector', '*',
                                      'bisect_U.xy')))
    if not f:
        refuse('no bisect_U.xy under %s -- the gate artifact is absent, and an '
               'absent gate artifact is a refusal, never a number' % level_dir)
    return f[-1]

def _rows(path):
    out = []
    for ln in open(path):
        if ln.startswith('#') or not ln.strip():
            continue
        f = [float(t) for t in ln.split()]
        out.append((f[0], f[1] / U_WALL))     # (y, u_x normalised by the wall speed)
    out.sort()
    return out

def _interp(xs, ys, x):
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    lo, hi = 0, len(xs) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if xs[mid] <= x:
            lo = mid
        else:
            hi = mid
    t = (x - xs[lo]) / (xs[hi] - xs[lo])
    return ys[lo] + t * (ys[hi] - ys[lo])

def _read_rms(path):
    r = _rows(path)
    xs = [t[0] for t in r]; ys = [t[1] for t in r]
    by, bv = _bench()
    s = sum((_interp(xs, ys, by[i]) - bv[i]) ** 2 for i in range(len(by)))
    return math.sqrt(s / len(by))

def _read_umin(path):
    """The most negative normalised X-velocity on the bisector -- a SOLUTION
    functional, not an error norm.  The Roache triple runs on THIS, because the
    benchmark curve is a plot digitisation and carries its own noise floor (it
    reports values between -2.7e-04 and +1.1e-02, changing sign, in the quiescent
    lower half where the physical velocity is essentially zero), so an
    error-versus-reference norm cannot converge to zero and would grade STAGNANT
    for a reason that has nothing to do with this lab's discretisation."""
    return min(u for _, u in _rows(path))

def _perturb(path, plant):
    """THE PARENT'S PERTURBATION, byte-identical: ONE row.  It is CORRECT for the
    point reader (u_min) and it is preserved here both for that channel and so the
    control can show, on real bytes, that it is what an averaging reader cannot see."""
    lines = open(path).read().rstrip('\n').split('\n')
    for i, ln in enumerate(lines):
        if ln.startswith('#') or not ln.strip():
            continue
        f = ln.split()
        f[1] = repr(float(f[1]) + plant)
        lines[i] = '\t'.join(f)
        break
    open(path, 'w').write('\n'.join(lines) + '\n')

def _perturb_all(path, plant):
    """THE L-340 REPAIR: plant into EVERY data row, so an averaging reader sees a
    move of order the plant instead of the plant divided by ~sqrt(N)."""
    lines = open(path).read().rstrip('\n').split('\n')
    n = 0
    for i, ln in enumerate(lines):
        if ln.startswith('#') or not ln.strip():
            continue
        f = ln.split()
        f[1] = repr(float(f[1]) + plant)
        lines[i] = '\t'.join(f)
        n += 1
    if n == 0:
        refuse('_perturb_all found NO data row to plant into in %s -- a plant that '
               'went nowhere cannot drive a control' % path)
    open(path, 'w').write('\n'.join(lines) + '\n')

def channels(level_dir):
    p = _xy(level_dir)
    r = _rows(p)
    umin = _read_umin(p)
    ymin = [y for y, u in r if u == umin][0]
    return {'rms_vs_benchmark': _read_rms(p), 'u_min_norm': umin, 'y_at_u_min_m': ymin}

def controls(level_dir):
    """The rule-3 controls, one per channel, each with the plant sized to ITS reader."""
    p = _xy(level_dir)
    base_rms = _read_rms(p)
    return {'rms_vs_benchmark': planted_zero(p, _perturb_all, _read_rms,
                                             rms_plant_for(base_rms),
                                             'rms_vs_benchmark'),
            'u_min_norm': planted_zero(p, _perturb, _read_umin,
                                       -abs(PLANT) * 100, 'u_min_norm')}

# ============================================================================
# THE REAL BYTES THAT MADE ATTEMPT 1 REFUSE.
# verification/runs/ansys_verification/VMFL011/L1/postProcessing/bisector/20000/
# bisect_U.xy, verbatim, 401 sampled points.  It is embedded so the control that
# DRIVES this repair runs on the ACTUAL artifact of the refusal recorded in
# cases/ansys_verification/VMFL011/RESULTS.md, not on a construction that resembles
# it.  It is read ONLY by rms_sizing_control(); no verdict reads it.
# ============================================================================
REAL_XY_L1_ATTEMPT1 = r'''
-4 	0 	0 	0
-3.99 	6.24899441265e-12 	-6.13305354073e-17 	-1.97803336483e-20
-3.98 	1.24979888253e-11 	-1.22661070815e-16 	-3.95606672965e-20
-3.97 	1.87469832379e-11 	-1.83991606222e-16 	-5.93410009448e-20
-3.96 	2.49959776506e-11 	-2.45322141629e-16 	-7.91213345931e-20
-3.95 	3.12449720632e-11 	-3.06652677037e-16 	-9.89016682414e-20
-3.94 	3.74939664759e-11 	-3.67983212444e-16 	-1.1868200189e-19
-3.93 	4.37429608885e-11 	-4.29313747851e-16 	-1.38462335538e-19
-3.92 	4.99919553012e-11 	-4.90644283259e-16 	-1.58242669186e-19
-3.91 	5.62409497138e-11 	-5.51974818666e-16 	-1.78023002834e-19
-3.9 	6.24899441265e-11 	-6.13305354073e-16 	-1.97803336483e-19
-3.89 	1.39848651793e-10 	-1.35312384311e-16 	-2.15595946167e-19
-3.88 	2.17207359459e-10 	3.42680585452e-16 	-2.3338855585e-19
-3.87 	2.94566067125e-10 	8.20673555215e-16 	-2.51181165534e-19
-3.86 	3.71924774792e-10 	1.29866652498e-15 	-2.68973775218e-19
-3.85 	4.49283482458e-10 	1.77665949474e-15 	-2.86766384902e-19
-3.84 	5.26642190125e-10 	2.2546524645e-15 	-3.04558994586e-19
-3.83 	6.04000897791e-10 	2.73264543426e-15 	-3.22351604269e-19
-3.82 	6.81359605457e-10 	3.21063840402e-15 	-3.40144213953e-19
-3.81 	7.58718313124e-10 	3.68863137379e-15 	-3.57936823637e-19
-3.8 	8.3607702079e-10 	4.16662434355e-15 	-3.75729433321e-19
-3.79 	1.00210134084e-09 	1.57481329551e-14 	-3.30710168733e-19
-3.78 	1.1681256609e-09 	2.73296415667e-14 	-2.85690904145e-19
-3.77 	1.33414998095e-09 	3.89111501782e-14 	-2.40671639557e-19
-3.76 	1.500174301e-09 	5.04926587898e-14 	-1.95652374969e-19
-3.75 	1.66619862106e-09 	6.20741674014e-14 	-1.50633110381e-19
-3.74 	1.83222294111e-09 	7.36556760129e-14 	-1.05613845793e-19
-3.73 	1.99824726117e-09 	8.52371846245e-14 	-6.05945812047e-20
-3.72 	2.16427158122e-09 	9.68186932361e-14 	-1.55753166166e-20
-3.71 	2.33029590127e-09 	1.08400201848e-13 	2.94439479714e-20
-3.7 	2.49632022133e-09 	1.19981710459e-13 	7.44632125594e-20
-3.69 	-1.72010749425e-10 	2.56633843833e-13 	1.40962443984e-19
-3.68 	-2.84034172018e-09 	3.93285977207e-13 	2.07461675409e-19
-3.67 	-5.50867269093e-09 	5.29938110581e-13 	2.73960906834e-19
-3.66 	-8.17700366168e-09 	6.66590243955e-13 	3.40460138259e-19
-3.65 	-1.08453346324e-08 	8.03242377329e-13 	4.06959369685e-19
-3.64 	-1.35136656032e-08 	9.39894510702e-13 	4.7345860111e-19
-3.63 	-1.61819965739e-08 	1.07654664408e-12 	5.39957832535e-19
-3.62 	-1.88503275447e-08 	1.21319877745e-12 	6.0645706396e-19
-3.61 	-2.15186585155e-08 	1.34985091082e-12 	6.72956295385e-19
-3.6 	-2.41869894862e-08 	1.4865030442e-12 	7.3945552681e-19
-3.59 	-4.96754763241e-08 	2.40994172767e-12 	7.5734171487e-19
-3.58 	-7.5163963162e-08 	3.33338041114e-12 	7.75227902931e-19
-3.57 	-1.0065245e-07 	4.25681909461e-12 	7.93114090992e-19
-3.56 	-1.26140936838e-07 	5.18025777808e-12 	8.11000279053e-19
-3.55 	-1.51629423676e-07 	6.10369646155e-12 	8.28886467114e-19
-3.54 	-1.77117910514e-07 	7.02713514502e-12 	8.46772655174e-19
-3.53 	-2.02606397351e-07 	7.95057382849e-12 	8.64658843235e-19
-3.52 	-2.28094884189e-07 	8.87401251197e-12 	8.82545031296e-19
-3.51 	-2.53583371027e-07 	9.79745119544e-12 	9.00431219357e-19
-3.5 	-2.79071857865e-07 	1.07208898789e-11 	9.18317407418e-19
-3.49 	-3.95461967141e-07 	1.34440531816e-11 	8.19415563615e-19
-3.48 	-5.11852076417e-07 	1.61672164842e-11 	7.20513719813e-19
-3.47 	-6.28242185694e-07 	1.88903797869e-11 	6.2161187601e-19
-3.46 	-7.4463229497e-07 	2.16135430895e-11 	5.22710032208e-19
-3.45 	-8.61022404246e-07 	2.43367063922e-11 	4.23808188405e-19
-3.44 	-9.77412513522e-07 	2.70598696948e-11 	3.24906344602e-19
-3.43 	-1.0938026228e-06 	2.97830329975e-11 	2.260045008e-19
-3.42 	-1.21019273207e-06 	3.25061963002e-11 	1.27102656997e-19
-3.41 	-1.32658284135e-06 	3.52293596028e-11 	2.82008131947e-20
-3.4 	-1.44297295063e-06 	3.79525229055e-11 	-7.07010306078e-20
-3.39 	-1.78244269497e-06 	2.57821172647e-11 	-5.67762728571e-20
-3.38 	-2.12191243932e-06 	1.36117116239e-11 	-4.28515151062e-20
-3.37 	-2.46138218367e-06 	1.44130598316e-12 	-2.89267573554e-20
-3.36 	-2.80085192801e-06 	-1.07290996576e-11 	-1.50019996045e-20
-3.35 	-3.14032167236e-06 	-2.28995052984e-11 	-1.07724185367e-21
-3.34 	-3.4797914167e-06 	-3.50699109392e-11 	1.28475158972e-20
-3.33 	-3.81926116105e-06 	-4.72403165799e-11 	2.6772273648e-20
-3.32 	-4.1587309054e-06 	-5.94107222207e-11 	4.06970313989e-20
-3.31 	-4.49820064974e-06 	-7.15811278615e-11 	5.46217891498e-20
-3.3 	-4.83767039409e-06 	-8.37515335023e-11 	6.85465469006e-20
-3.29 	-5.49224201938e-06 	-2.85526897894e-10 	1.30059599976e-19
-3.28 	-6.14681364468e-06 	-4.87302262285e-10 	1.91572653052e-19
-3.27 	-6.80138526998e-06 	-6.89077626677e-10 	2.53085706128e-19
-3.26 	-7.45595689527e-06 	-8.90852991069e-10 	3.14598759204e-19
-3.25 	-8.11052852057e-06 	-1.09262835546e-09 	3.7611181228e-19
-3.24 	-8.76510014587e-06 	-1.29440371985e-09 	4.37624865356e-19
-3.23 	-9.41967177116e-06 	-1.49617908424e-09 	4.99137918432e-19
-3.22 	-1.00742433965e-05 	-1.69795444864e-09 	5.60650971508e-19
-3.21 	-1.07288150218e-05 	-1.89972981303e-09 	6.22164024584e-19
-3.2 	-1.13833866471e-05 	-2.10150517742e-09 	6.83677077659e-19
-3.19 	-1.20245141141e-05 	-3.48024809184e-09 	5.32335625188e-19
-3.18 	-1.26656415811e-05 	-4.85899100627e-09 	3.80994172715e-19
-3.17 	-1.33067690481e-05 	-6.23773392069e-09 	2.29652720243e-19
-3.16 	-1.39478965151e-05 	-7.61647683511e-09 	7.83112677711e-20
-3.15 	-1.45890239821e-05 	-8.99521974954e-09 	-7.30301847011e-20
-3.14 	-1.52301514491e-05 	-1.0373962664e-08 	-2.24371637173e-19
-3.13 	-1.58712789161e-05 	-1.17527055784e-08 	-3.75713089645e-19
-3.12 	-1.65124063831e-05 	-1.31314484928e-08 	-5.27054542118e-19
-3.11 	-1.71535338501e-05 	-1.45101914072e-08 	-6.7839599459e-19
-3.1 	-1.77946613171e-05 	-1.58889343217e-08 	-8.29737447062e-19
-3.09 	-1.69077985371e-05 	-2.2395729293e-08 	-8.31418181473e-19
-3.08 	-1.60209357571e-05 	-2.89025242644e-08 	-8.33098915885e-19
-3.07 	-1.5134072977e-05 	-3.54093192358e-08 	-8.34779650296e-19
-3.06 	-1.4247210197e-05 	-4.19161142072e-08 	-8.36460384707e-19
-3.05 	-1.3360347417e-05 	-4.84229091786e-08 	-8.38141119118e-19
-3.04 	-1.2473484637e-05 	-5.492970415e-08 	-8.39821853529e-19
-3.03 	-1.15866218569e-05 	-6.14364991214e-08 	-8.4150258794e-19
-3.02 	-1.06997590769e-05 	-6.79432940928e-08 	-8.43183322352e-19
-3.01 	-9.81289629688e-06 	-7.44500890642e-08 	-8.44864056763e-19
-3 	-8.92603351685e-06 	-8.09568840356e-08 	-8.46544791174e-19
-2.99 	-2.71762664339e-06 	-1.04604081062e-07 	-7.61890312057e-19
-2.98 	3.49078023008e-06 	-1.28251278088e-07 	-6.77235832939e-19
-2.97 	9.69918710356e-06 	-1.51898475114e-07 	-5.92581353822e-19
-2.96 	1.5907593977e-05 	-1.7554567214e-07 	-5.07926874705e-19
-2.95 	2.21160008505e-05 	-1.99192869167e-07 	-4.23272395587e-19
-2.94 	2.8324407724e-05 	-2.22840066193e-07 	-3.3861791647e-19
-2.93 	3.45328145974e-05 	-2.46487263219e-07 	-2.53963437352e-19
-2.92 	4.07412214709e-05 	-2.70134460245e-07 	-1.69308958235e-19
-2.91 	4.69496283444e-05 	-2.93781657271e-07 	-8.46544791176e-20
-2.9 	5.31580352179e-05 	-3.17428854298e-07 	-1.99201953254e-31
-2.89 	7.18831803652e-05 	-3.8619130432e-07 	0
-2.88 	9.06083255125e-05 	-4.54953754343e-07 	0
-2.87 	0.00010933347066 	-5.23716204366e-07 	0
-2.86 	0.000128058615807 	-5.92478654389e-07 	0
-2.85 	0.000146783760955 	-6.61241104411e-07 	0
-2.84 	0.000165508906102 	-7.30003554434e-07 	0
-2.83 	0.000184234051249 	-7.98766004457e-07 	0
-2.82 	0.000202959196397 	-8.6752845448e-07 	0
-2.81 	0.000221684341544 	-9.36290904502e-07 	0
-2.8 	0.000240409486691 	-1.00505335453e-06 	0
-2.79 	0.000282862710256 	-1.16590209003e-06 	-1.12045126848e-19
-2.78 	0.000325315933821 	-1.32675082554e-06 	-2.24090253696e-19
-2.77 	0.000367769157386 	-1.48759956105e-06 	-3.36135380544e-19
-2.76 	0.000410222380951 	-1.64844829656e-06 	-4.48180507392e-19
-2.75 	0.000452675604516 	-1.80929703207e-06 	-5.60225634239e-19
-2.74 	0.00049512882808 	-1.97014576758e-06 	-6.72270761087e-19
-2.73 	0.000537582051645 	-2.13099450309e-06 	-7.84315887935e-19
-2.72 	0.00058003527521 	-2.2918432386e-06 	-8.96361014783e-19
-2.71 	0.000622488498775 	-2.45269197411e-06 	-1.00840614163e-18
-2.7 	0.00066494172234 	-2.61354070962e-06 	-1.12045126848e-18
-2.69 	0.000745748573174 	-2.907117037e-06 	-1.24074362929e-18
-2.68 	0.000826555424009 	-3.20069336439e-06 	-1.36103599011e-18
-2.67 	0.000907362274844 	-3.49426969177e-06 	-1.48132835092e-18
-2.66 	0.000988169125678 	-3.78784601916e-06 	-1.60162071173e-18
-2.65 	0.00106897597651 	-4.08142234654e-06 	-1.72191307255e-18
-2.64 	0.00114978282735 	-4.37499867393e-06 	-1.84220543336e-18
-2.63 	0.00123058967818 	-4.66857500131e-06 	-1.96249779417e-18
-2.62 	0.00131139652902 	-4.9621513287e-06 	-2.08279015499e-18
-2.61 	0.00139220337985 	-5.25572765609e-06 	-2.2030825158e-18
-2.6 	0.00147301023069 	-5.54930398347e-06 	-2.32337487661e-18
-2.59 	0.00160762685726 	-5.91873695576e-06 	-2.33601322981e-18
-2.58 	0.00174224348383 	-6.28816992805e-06 	-2.348651583e-18
-2.57 	0.00187686011041 	-6.65760290034e-06 	-2.3612899362e-18
-2.56 	0.00201147673698 	-7.02703587263e-06 	-2.37392828939e-18
-2.55 	0.00214609336355 	-7.39646884493e-06 	-2.38656664258e-18
-2.54 	0.00228070999013 	-7.76590181722e-06 	-2.39920499578e-18
-2.53 	0.0024153266167 	-8.13533478951e-06 	-2.41184334897e-18
-2.52 	0.00254994324328 	-8.5047677618e-06 	-2.42448170217e-18
-2.51 	0.00268455986985 	-8.87420073409e-06 	-2.43712005536e-18
-2.5 	0.00281917649642 	-9.24363370638e-06 	-2.44975840855e-18
-2.49 	0.00301863335861 	-9.36490388103e-06 	-2.46172586782e-18
-2.48 	0.0032180902208 	-9.48617405568e-06 	-2.47369332709e-18
-2.47 	0.003417547083 	-9.60744423034e-06 	-2.48566078635e-18
-2.46 	0.00361700394519 	-9.72871440499e-06 	-2.49762824562e-18
-2.45 	0.00381646080738 	-9.84998457964e-06 	-2.50959570489e-18
-2.44 	0.00401591766957 	-9.97125475429e-06 	-2.52156316415e-18
-2.43 	0.00421537453176 	-1.00925249289e-05 	-2.53353062342e-18
-2.42 	0.00441483139395 	-1.02137951036e-05 	-2.54549808269e-18
-2.41 	0.00461428825614 	-1.03350652782e-05 	-2.55746554195e-18
-2.4 	0.00481374511834 	-1.04563354529e-05 	-2.56943300122e-18
-2.39 	0.00507623268124 	-9.60367711518e-06 	-2.44480011138e-18
-2.38 	0.00533872024415 	-8.75101877746e-06 	-2.32016722154e-18
-2.37 	0.00560120780706 	-7.89836043974e-06 	-2.19553433171e-18
-2.36 	0.00586369536996 	-7.04570210202e-06 	-2.07090144187e-18
-2.35 	0.00612618293287 	-6.1930437643e-06 	-1.94626855203e-18
-2.34 	0.00638867049578 	-5.34038542658e-06 	-1.8216356622e-18
-2.33 	0.00665115805868 	-4.48772708886e-06 	-1.69700277236e-18
-2.32 	0.00691364562159 	-3.63506875114e-06 	-1.57236988252e-18
-2.31 	0.0071761331845 	-2.78241041342e-06 	-1.44773699269e-18
-2.3 	0.0074386207474 	-1.9297520757e-06 	-1.32310410285e-18
-2.29 	0.0077377758327 	7.44919102762e-07 	-1.33184819808e-18
-2.28 	0.00803693091799 	3.41959028123e-06 	-1.34059229332e-18
-2.27 	0.00833608600329 	6.09426145969e-06 	-1.34933638855e-18
-2.26 	0.00863524108858 	8.76893263816e-06 	-1.35808048379e-18
-2.25 	0.00893439617387 	1.14436038166e-05 	-1.36682457902e-18
-2.24 	0.00923355125917 	1.41182749951e-05 	-1.37556867425e-18
-2.23 	0.00953270634446 	1.67929461736e-05 	-1.38431276949e-18
-2.22 	0.00983186142976 	1.9467617352e-05 	-1.39305686472e-18
-2.21 	0.010131016515 	2.21422885305e-05 	-1.40180095996e-18
-2.2 	0.0104301716003 	2.48169597089e-05 	-1.41054505519e-18
-2.19 	0.0107004392326 	2.89057488575e-05 	-1.55829682775e-18
-2.18 	0.0109707068649 	3.29945380062e-05 	-1.70604860031e-18
-2.17 	0.0112409744971 	3.70833271548e-05 	-1.85380037287e-18
-2.16 	0.0115112421294 	4.11721163034e-05 	-2.00155214543e-18
-2.15 	0.0117815097616 	4.5260905452e-05 	-2.14930391799e-18
-2.14 	0.0120517773939 	4.93496946006e-05 	-2.29705569055e-18
-2.13 	0.0123220450262 	5.34384837492e-05 	-2.44480746311e-18
-2.12 	0.0125923126584 	5.75272728978e-05 	-2.59255923567e-18
-2.11 	0.0128625802907 	6.16160620464e-05 	-2.74031100823e-18
-2.1 	0.0131328479229 	6.5704851195e-05 	-2.88806278079e-18
-2.09 	0.0132529846943 	6.64079918868e-05 	-2.89735753662e-18
-2.08 	0.0133731214657 	6.71111325787e-05 	-2.90665229245e-18
-2.07 	0.0134932582371 	6.78142732705e-05 	-2.91594704827e-18
-2.06 	0.0136133950085 	6.85174139624e-05 	-2.9252418041e-18
-2.05 	0.0137335317799 	6.92205546542e-05 	-2.93453655992e-18
-2.04 	0.0138536685513 	6.99236953461e-05 	-2.94383131575e-18
-2.03 	0.0139738053227 	7.06268360379e-05 	-2.95312607157e-18
-2.02 	0.014093942094 	7.13299767298e-05 	-2.9624208274e-18
-2.01 	0.0142140788654 	7.20331174216e-05 	-2.97171558322e-18
-2 	0.0143342156368 	7.27362581135e-05 	-2.98101033905e-18
-1.99 	0.0141106231653 	5.63490933365e-05 	-2.83518028774e-18
-1.98 	0.0138870306939 	3.99619285594e-05 	-2.68935023643e-18
-1.97 	0.0136634382224 	2.35747637824e-05 	-2.54352018511e-18
-1.96 	0.0134398457509 	7.18759900532e-06 	-2.3976901338e-18
-1.95 	0.0132162532794 	-9.19956577174e-06 	-2.25186008249e-18
-1.94 	0.0129926608079 	-2.55867305488e-05 	-2.10603003118e-18
-1.93 	0.0127690683364 	-4.19738953258e-05 	-1.96019997986e-18
-1.92 	0.0125454758649 	-5.83610601029e-05 	-1.81436992855e-18
-1.91 	0.0123218833935 	-7.47482248799e-05 	-1.66853987724e-18
-1.9 	0.012098290922 	-9.1135389657e-05 	-1.52270982593e-18
-1.89 	0.0112498372281 	-0.000149947804052 	-1.37043884333e-18
-1.88 	0.0104013835343 	-0.000208760218448 	-1.21816786074e-18
-1.87 	0.00955292984047 	-0.000267572632843 	-1.06589687815e-18
-1.86 	0.00870447614663 	-0.000326385047239 	-9.13625895557e-19
-1.85 	0.0078560224528 	-0.000385197461634 	-7.61354912964e-19
-1.84 	0.00700756875896 	-0.00044400987603 	-6.09083930371e-19
-1.83 	0.00615911506512 	-0.000502822290425 	-4.56812947779e-19
-1.82 	0.00531066137129 	-0.000561634704821 	-3.04541965186e-19
-1.81 	0.00446220767745 	-0.000620447119216 	-1.52270982593e-19
-1.8 	0.00361375398361 	-0.000679259533612 	-6.49254770665e-31
-1.79 	0.00175940186993 	-0.000810603090812 	0
-1.78 	-9.49502437608e-05 	-0.000941946648013 	0
-1.77 	-0.00194930235745 	-0.00107329020521 	0
-1.76 	-0.00380365447114 	-0.00120463376242 	0
-1.75 	-0.00565800658483 	-0.00133597731962 	0
-1.74 	-0.00751235869852 	-0.00146732087682 	0
-1.73 	-0.00936671081221 	-0.00159866443402 	0
-1.72 	-0.0112210629259 	-0.00173000799122 	0
-1.71 	-0.0130754150396 	-0.00186135154842 	0
-1.7 	-0.0149297671533 	-0.00199269510562 	0
-1.69 	-0.0182741701497 	-0.00220291106025 	0
-1.68 	-0.0216185731461 	-0.00241312701487 	0
-1.67 	-0.0249629761425 	-0.0026233429695 	0
-1.66 	-0.0283073791389 	-0.00283355892413 	0
-1.65 	-0.0316517821353 	-0.00304377487875 	0
-1.64 	-0.0349961851317 	-0.00325399083338 	0
-1.63 	-0.0383405881281 	-0.00346420678801 	0
-1.62 	-0.0416849911245 	-0.00367442274263 	0
-1.61 	-0.0450293941209 	-0.00388463869726 	0
-1.6 	-0.0483737971173 	-0.00409485465189 	0
-1.59 	-0.0537568425223 	-0.0043034803951 	-1.67979986596e-19
-1.58 	-0.0591398879273 	-0.00451210613832 	-3.35959973193e-19
-1.57 	-0.0645229333323 	-0.00472073188153 	-5.03939959791e-19
-1.56 	-0.0699059787373 	-0.00492935762474 	-6.71919946388e-19
-1.55 	-0.0752890241423 	-0.00513798336796 	-8.39899932985e-19
-1.54 	-0.0806720695473 	-0.00534660911117 	-1.00787991958e-18
-1.53 	-0.0860551149523 	-0.00555523485439 	-1.17585990618e-18
-1.52 	-0.0914381603573 	-0.0057638605976 	-1.34383989278e-18
-1.51 	-0.0968212057623 	-0.00597248634081 	-1.51181987937e-18
-1.5 	-0.102204251167 	-0.00618111208403 	-1.67979986597e-18
-1.49 	-0.110063689191 	-0.00615510095708 	-1.68183777252e-18
-1.48 	-0.117923127214 	-0.00612908983014 	-1.68387567908e-18
-1.47 	-0.125782565237 	-0.00610307870319 	-1.68591358563e-18
-1.46 	-0.13364200326 	-0.00607706757624 	-1.68795149218e-18
-1.45 	-0.141501441284 	-0.0060510564493 	-1.68998939873e-18
-1.44 	-0.149360879307 	-0.00602504532235 	-1.69202730529e-18
-1.43 	-0.15722031733 	-0.0059990341954 	-1.69406521184e-18
-1.42 	-0.165079755354 	-0.00597302306846 	-1.69610311839e-18
-1.41 	-0.172939193377 	-0.00594701194151 	-1.69814102494e-18
-1.4 	-0.1807986314 	-0.00592100081457 	-1.70017893149e-18
-1.39 	-0.191037657049 	-0.00532431282889 	-1.53016103835e-18
-1.38 	-0.201276682697 	-0.00472762484321 	-1.3601431452e-18
-1.37 	-0.211515708346 	-0.00413093685753 	-1.19012525205e-18
-1.36 	-0.221754733994 	-0.00353424887186 	-1.0201073589e-18
-1.35 	-0.231993759643 	-0.00293756088618 	-8.50089465748e-19
-1.34 	-0.242232785291 	-0.0023408729005 	-6.80071572599e-19
-1.33 	-0.25247181094 	-0.00174418491482 	-5.10053679449e-19
-1.32 	-0.262710836588 	-0.00114749692914 	-3.400357863e-19
-1.31 	-0.272949862236 	-0.000550808943465 	-1.7001789315e-19
-1.3 	-0.283188887885 	4.58790422127e-05 	-7.09540493414e-31
-1.29 	-0.294518297677 	0.00160239166581 	1.30529603897e-19
-1.28 	-0.305847707468 	0.00315890428941 	2.61059207795e-19
-1.27 	-0.31717711726 	0.00471541691302 	3.91588811693e-19
-1.26 	-0.328506527052 	0.00627192953662 	5.22118415591e-19
-1.25 	-0.339835936843 	0.00782844216022 	6.52648019488e-19
-1.24 	-0.351165346635 	0.00938495478382 	7.83177623386e-19
-1.23 	-0.362494756427 	0.0109414674074 	9.13707227284e-19
-1.22 	-0.373824166219 	0.012497980031 	1.04423683118e-18
-1.21 	-0.38515357601 	0.0140544926546 	1.17476643508e-18
-1.2 	-0.396482985802 	0.0156110052782 	1.30529603898e-18
-1.19 	-0.405973151415 	0.0184080758729 	1.30684140212e-18
-1.18 	-0.415463317029 	0.0212051464675 	1.30838676527e-18
-1.17 	-0.424953482642 	0.0240022170622 	1.30993212841e-18
-1.16 	-0.434443648255 	0.0267992876568 	1.31147749155e-18
-1.15 	-0.443933813868 	0.0295963582515 	1.3130228547e-18
-1.14 	-0.453423979482 	0.0323934288461 	1.31456821784e-18
-1.13 	-0.462914145095 	0.0351904994408 	1.31611358099e-18
-1.12 	-0.472404310708 	0.0379875700354 	1.31765894413e-18
-1.11 	-0.481894476322 	0.0407846406301 	1.31920430728e-18
-1.1 	-0.491384641935 	0.0435817112247 	1.32074967042e-18
-1.09 	-0.495145069063 	0.047434636658 	1.18867470338e-18
-1.08 	-0.498905496191 	0.0512875620913 	1.05659973634e-18
-1.07 	-0.502665923319 	0.0551404875246 	9.24524769294e-19
-1.06 	-0.506426350447 	0.0589934129579 	7.92449802252e-19
-1.05 	-0.510186777575 	0.0628463383912 	6.6037483521e-19
-1.04 	-0.513947204703 	0.0666992638245 	5.28299868168e-19
-1.03 	-0.517707631831 	0.0705521892578 	3.96224901126e-19
-1.02 	-0.521468058959 	0.0744051146911 	2.64149934084e-19
-1.01 	-0.525228486087 	0.0782580401244 	1.32074967042e-19
-1 	-0.528988913215 	0.0821109655577 	5.51338836893e-31
-0.99 	-0.524482970048 	0.0862792493111 	0
-0.98 	-0.51997702688 	0.0904475330646 	0
-0.97 	-0.515471083713 	0.0946158168181 	0
-0.96 	-0.510965140546 	0.0987841005716 	0
-0.95 	-0.506459197378 	0.102952384325 	0
-0.94 	-0.501953254211 	0.107120668079 	0
-0.93 	-0.497447311044 	0.111288951832 	0
-0.92 	-0.492941367876 	0.115457235586 	0
-0.91 	-0.488435424709 	0.119625519339 	0
-0.9 	-0.483929481542 	0.123793803092 	0
-0.89 	-0.472190021573 	0.12733546823 	0
-0.88 	-0.460450561604 	0.130877133368 	0
-0.87 	-0.448711101635 	0.134418798506 	0
-0.86 	-0.436971641666 	0.137960463644 	0
-0.85 	-0.425232181696 	0.141502128782 	0
-0.84 	-0.413492721727 	0.14504379392 	0
-0.83 	-0.401753261758 	0.148585459058 	0
-0.82 	-0.390013801789 	0.152127124196 	0
-0.81 	-0.37827434182 	0.155668789334 	0
-0.8 	-0.366534881851 	0.159210454472 	0
-0.79 	-0.351098314562 	0.161545614183 	0
-0.78 	-0.335661747273 	0.163880773895 	0
-0.77 	-0.320225179984 	0.166215933606 	0
-0.76 	-0.304788612695 	0.168551093318 	0
-0.75 	-0.289352045406 	0.170886253029 	0
-0.74 	-0.273915478117 	0.173221412741 	0
-0.73 	-0.258478910828 	0.175556572452 	0
-0.72 	-0.243042343539 	0.177891732164 	0
-0.71 	-0.22760577625 	0.180226891875 	0
-0.7 	-0.212169208961 	0.182562051587 	0
-0.69 	-0.195807736886 	0.183697031006 	2.11224016614e-19
-0.68 	-0.179446264812 	0.184832010426 	4.22448033229e-19
-0.67 	-0.163084792738 	0.185966989845 	6.33672049844e-19
-0.66 	-0.146723320664 	0.187101969265 	8.4489606646e-19
-0.65 	-0.13036184859 	0.188236948684 	1.05612008307e-18
-0.64 	-0.114000376515 	0.189371928104 	1.26734409969e-18
-0.63 	-0.0976389044413 	0.190506907523 	1.4785681163e-18
-0.62 	-0.0812774323671 	0.191641886943 	1.68979213292e-18
-0.61 	-0.0649159602929 	0.192776866363 	1.90101614954e-18
-0.6 	-0.0485544882187 	0.193911845782 	2.11224016615e-18
-0.59 	-0.0323953327454 	0.194133895413 	2.11465770193e-18
-0.58 	-0.0162361772721 	0.194355945044 	2.11707523771e-18
-0.57 	-7.70217988602e-05 	0.194577994675 	2.1194927735e-18
-0.56 	0.0160821336744 	0.194800044306 	2.12191030928e-18
-0.55 	0.0322412891477 	0.195022093937 	2.12432784506e-18
-0.54 	0.048400444621 	0.195244143568 	2.12674538084e-18
-0.53 	0.0645596000943 	0.195466193199 	2.12916291662e-18
-0.52 	0.0807187555676 	0.19568824283 	2.13158045241e-18
-0.51 	0.0968779110409 	0.195910292461 	2.13399798819e-18
-0.5 	0.113037066514 	0.196132342091 	2.13641552397e-18
-0.49 	0.128364596417 	0.195465914884 	2.08795455815e-18
-0.48 	0.14369212632 	0.194799487677 	2.03949359233e-18
-0.47 	0.159019656222 	0.19413306047 	1.99103262651e-18
-0.46 	0.174347186125 	0.193466633262 	1.94257166069e-18
-0.45 	0.189674716028 	0.192800206055 	1.89411069487e-18
-0.44 	0.205002245931 	0.192133778848 	1.84564972905e-18
-0.43 	0.220329775834 	0.191467351641 	1.79718876323e-18
-0.42 	0.235657305736 	0.190800924433 	1.74872779741e-18
-0.41 	0.250984835639 	0.190134497226 	1.7002668316e-18
-0.4 	0.266312365542 	0.189468070019 	1.65180586578e-18
-0.39 	0.280273070979 	0.187449576202 	1.65367930934e-18
-0.38 	0.294233776416 	0.185431082386 	1.6555527529e-18
-0.37 	0.308194481853 	0.183412588569 	1.65742619646e-18
-0.36 	0.32215518729 	0.181394094753 	1.65929964002e-18
-0.35 	0.336115892727 	0.179375600936 	1.66117308359e-18
-0.34 	0.350076598164 	0.17735710712 	1.66304652715e-18
-0.33 	0.364037303601 	0.175338613303 	1.66491997071e-18
-0.32 	0.377998009038 	0.173320119487 	1.66679341427e-18
-0.31 	0.391958714475 	0.17130162567 	1.66866685783e-18
-0.3 	0.405919419912 	0.169283131854 	1.6705403014e-18
-0.29 	0.423521215812 	0.165066974428 	1.41088557888e-18
-0.28 	0.441123011713 	0.160850817002 	1.15123085636e-18
-0.27 	0.458724807614 	0.156634659575 	8.91576133842e-19
-0.26 	0.476326603515 	0.152418502149 	6.31921411323e-19
-0.25 	0.493928399415 	0.148202344723 	3.72266688804e-19
-0.24 	0.511530195316 	0.143986187297 	1.12611966285e-19
-0.23 	0.529131991217 	0.139770029871 	-1.47042756234e-19
-0.22 	0.546733787118 	0.135553872445 	-4.06697478752e-19
-0.21 	0.564335583018 	0.131337715019 	-6.66352201271e-19
-0.2 	0.581937378919 	0.127121557593 	-9.2600692379e-19
-0.19 	0.626170356921 	0.120368775767 	-9.27048150074e-19
-0.18 	0.670403334923 	0.113615993942 	-9.28089376357e-19
-0.17 	0.714636312924 	0.106863212117 	-9.29130602639e-19
-0.16 	0.758869290926 	0.100110430292 	-9.30171828922e-19
-0.15 	0.803102268928 	0.0933576484665 	-9.31213055205e-19
-0.14 	0.84733524693 	0.0866048666413 	-9.32254281488e-19
-0.13 	0.891568224931 	0.0798520848161 	-9.3329550777e-19
-0.12 	0.935801202933 	0.0730993029909 	-9.34336734053e-19
-0.11 	0.980034180935 	0.0663465211656 	-9.35377960336e-19
-0.1 	1.02426715894 	0.0595937393404 	-9.36419186619e-19
-0.09 	1.12184044304 	0.0536343654064 	-8.42777267957e-19
-0.08 	1.21941372715 	0.0476749914723 	-7.49135349295e-19
-0.07 	1.31698701126 	0.0417156175383 	-6.55493430633e-19
-0.06 	1.41456029536 	0.0357562436043 	-5.61851511972e-19
-0.05 	1.51213357947 	0.0297968696702 	-4.6820959331e-19
-0.04 	1.60970686357 	0.0238374957362 	-3.74567674648e-19
-0.03 	1.70728014768 	0.0178781218021 	-2.80925755986e-19
-0.02 	1.80485343179 	0.0119187478681 	-1.87283837324e-19
-0.01 	1.90242671589 	0.00595937393406 	-9.36419186622e-20
-4.09894340692e-14 	2 	2.44238283792e-14 	-3.83780943403e-31
'''

REF_CSV_BLOB = '9f11191b8c823eb32edd3f2b74bd29da855aab55'
N_BENCH      = 46          # rows in the reference CSV -- see the pre-registration
REAL_L1_RMS_ATTEMPT1        = 0.0402642150   # measured from the embedded bytes
REAL_L1_DELTA_ATTEMPT1_PAIR = 3.67709e-07    # the refusal quoted in VMFL011/RESULTS.md

def _blob_sha1(path):
    """git's own blob hash, computed here so the reference identity is a CHECK at
    grade time and not a claim in a document.  No git subprocess: this must work
    in a scratch tree with no repository."""
    import hashlib
    data = open(path, 'rb').read()
    h = hashlib.sha1()
    h.update(b'blob %d\0' % len(data))
    h.update(data)
    return h.hexdigest()

def _write_real_xy(path):
    open(path, 'w').write(REAL_XY_L1_ATTEMPT1.lstrip('\n'))

def _write_flat_xy(path, offset):
    """A profile whose error against the benchmark is EXACTLY `offset` at every
    benchmark abscissa: sample points placed ON the benchmark abscissae, so the
    comparator's own linear interpolation is exact there."""
    by, bv = _bench()
    with open(path, 'w') as fh:
        for i in range(len(by)):
            fh.write('%r\t%r\t0\t0\n' % (by[i], U_WALL * (bv[i] + offset)))

# ---------------------------------------------------------------- the controls
def frozen_constants_control():
    """Everything the pre-registration calls BYTE-IDENTICAL, re-checked here.  A
    constant that drifted would move a verdict silently, so it REFUSES."""
    bad = []
    for name, got, want in (('U_WALL', U_WALL, 2.0),
                            ('BAND_RMS', BAND_RMS, 0.030),
                            ('RESID_FLOOR', RESID_FLOOR, 1.0e-7),
                            ('ENDTIME', ENDTIME, 20000),
                            ('PLANT', PLANT, 1.234e-03),
                            ('TIER_CEILING', TIER_CEILING, 'GATE REACHED'),
                            ('LEVELS', LEVELS, ['L1', 'L2', 'L3']),
                            ('FIELDS', FIELDS, ['U', 'p']),
                            ('P_MIN', P_MIN, 0.05)):
        if got != want:
            bad.append('%s = %r, registered %r' % (name, got, want))
    got_blob = _blob_sha1(_ref_csv())
    if got_blob != REF_CSV_BLOB:
        bad.append('reference CSV blob %s, registered %s' % (got_blob, REF_CSV_BLOB))
    by, _ = _bench()
    if len(by) != N_BENCH:
        bad.append('reference carries %d abscissae, registered %d' % (len(by), N_BENCH))
    if bad:
        refuse('FROZEN CONSTANT DRIFT -- ' + '; '.join(bad))
    return {'checked': 11, 'reference_blob': got_blob, 'n_bench': len(by),
            'result': 'every frozen constant and the reference blob match the registration'}

def assert_census():
    """L-332.  This file may carry NO `assert`, because python3 -O deletes them and
    a refusal a flag can delete is not a refusal.  The counter is shown able to
    count a PLANTED assert, so its zero is a reading and not a blind spot."""
    src = open(os.path.abspath(__file__), errors='replace').read()
    mine = sum(1 for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Assert))
    planted = sum(1 for n in ast.walk(ast.parse('def f(x):\n    assert x\n'))
                  if isinstance(n, ast.Assert))
    if planted < 1:
        refuse('the ast.Assert counter cannot see a PLANTED assert -- its zero on '
               'this file would be a blind spot, not a reading (L-332, rule 3)')
    if mine != 0:
        refuse('this comparator carries %d `assert` statement(s); python3 -O deletes '
               'every one of them (L-332)' % mine)
    return {'ast_assert_in_this_file': mine, 'ast_assert_in_planted_source': planted,
            'result': 'no assert carries any guard, and the counter is shown able to count one'}

def rms_sizing_control(quiet=False):
    """THE CONTROL THAT DRIVES THIS RE-REGISTRATION (L-340).

    Four probes, on the REAL bytes of the refusal and on an adversarial profile.
    Each refuses (exit 2) on its own failing path.  A repair nobody drives is a
    repair nobody has, so probe (1) requires the PARENT's pair to still REFUSE:
    if it did not, nothing would justify this file existing."""
    d = tempfile.mkdtemp(prefix='rmsctl_')
    try:
        real = os.path.join(d, 'bisect_U.xy')
        _write_real_xy(real)
        base = _read_rms(real)
        if abs(base - REAL_L1_RMS_ATTEMPT1) > 1e-9:
            refuse('the embedded attempt-1 L1 bytes read RMS %.10f, registered %.10f '
                   '-- the control is not running on the artifact it claims'
                   % (base, REAL_L1_RMS_ATTEMPT1))

        # (1) THE PARENT'S PAIR MUST STILL REFUSE ON THESE BYTES.
        code1, msg1 = expect_refusal(d, planted_zero, real, _perturb, _read_rms,
                                     PLANT, 'parent pair (off-path probe)')
        parent_refused = (code1 == 2)
        cp = os.path.join(d, 'p1.xy'); shutil.copy2(real, cp)
        _perturb(cp, PLANT)
        d_parent = abs(_read_rms(cp) - base)
        if not parent_refused:
            refuse('probe (1): the PARENT single-row plant did NOT refuse on the real '
                   'attempt-1 bytes -- then nothing drives this re-registration')
        if abs(d_parent - REAL_L1_DELTA_ATTEMPT1_PAIR) > 1e-11:
            refuse('probe (1): the parent pair moved the reader by %g, and the refusal '
                   'recorded in VMFL011/RESULTS.md is %g -- the control is not '
                   'reproducing the recorded refusal'
                   % (d_parent, REAL_L1_DELTA_ATTEMPT1_PAIR))

        # (2) PLANTING INTO ALL ROWS IS NOT ENOUGH BY ITSELF.  With the PARENT's
        # plant MAGNITUDE and the repaired perturbation shape, the control STILL
        # refuses on these bytes -- so the SIZING, not the shape, is load-bearing.
        code2, msg2 = expect_refusal(d, planted_zero, real, _perturb_all, _read_rms,
                                     PLANT, 'all-row unsized (off-path probe)')
        allrow_unsized_refused = (code2 == 2)
        cp = os.path.join(d, 'p2.xy'); shutil.copy2(real, cp)
        _perturb_all(cp, PLANT)
        d_unsized = abs(_read_rms(cp) - base)
        if not allrow_unsized_refused:
            refuse('probe (2): an ALL-ROW plant at the parent MAGNITUDE passed, so this '
                   'control cannot show that the SIZING is what repairs the defect')

        # (3) THE REGISTERED PAIR MUST PASS, INSIDE THE DERIVED BOUNDS.
        plant = rms_plant_for(base)
        got = planted_zero(real, _perturb_all, _read_rms, plant, 'rms sizing (probe 3)')
        lo, hi = (RMS_PLANT_K - 2.0) * base, RMS_PLANT_K * base
        if not (lo <= got['delta_seen'] <= hi):
            refuse('probe (3): the sized plant moved the reader by %g, outside the '
                   'DERIVED bounds [%g, %g] = [(K-2)*base, K*base] -- the reader does '
                   'not respond the way the sizing theorem says it must'
                   % (got['delta_seen'], lo, hi))

        # (4) ADVERSARIAL: a profile a FIXED plant cannot move AT ALL.  Error offset
        # c = -d/2 makes new^2 = base^2 exactly, so delta = 0 for that fixed plant --
        # the failure mode "plant into all points with a fixed magnitude" still has.
        adv = os.path.join(d, 'adv.xy')
        p_fixed = 0.4
        _write_flat_xy(adv, -p_fixed / (2.0 * U_WALL))
        a_base = _read_rms(adv)
        code4, msg4 = expect_refusal(d, planted_zero, adv, _perturb_all, _read_rms,
                                     p_fixed, 'adversarial fixed plant')
        fixed_refused = (code4 == 2)
        if not fixed_refused:
            refuse('probe (4): the adversarial profile did not defeat a FIXED all-row '
                   'plant, so it does not test what it was built to test')
        adv_got = planted_zero(adv, _perturb_all, _read_rms, rms_plant_for(a_base),
                               'adversarial sized plant')
        if not (adv_got['delta_seen'] > adv_got['threshold']):
            refuse('probe (4): the SIZED plant failed on the adversarial profile')

        out = {'real_bytes_rms': base,
               'parent_pair_delta': d_parent, 'parent_pair_threshold': 0.1 * PLANT,
               'allrow_unsized_delta': d_unsized, 'allrow_unsized_threshold': 0.1 * PLANT,
               'sized_plant': plant, 'sized_delta': got['delta_seen'],
               'sized_threshold': got['threshold'],
               'derived_bounds': [lo, hi],
               'adversarial_base': a_base, 'adversarial_sized_delta': adv_got['delta_seen'],
               'refusal_parent_pair': msg1,
               'refusal_allrow_unsized': msg2,
               'refusal_adversarial_fixed': msg4,
               'result': 'the parent pair and an unsized all-row plant BOTH refuse these '
                         'real bytes; the sized pair passes inside its derived bounds'}
        if not quiet:
            print('  L-340 REPAIR DRIVEN on the real attempt-1 L1 bytes: parent pair '
                  'delta %.6e < %.6e (REFUSES); all-row at the parent magnitude '
                  'delta %.6e < %.6e (REFUSES); sized plant %.6f -> delta %.6e > %.6e '
                  '(PASSES), inside [%.6e, %.6e]'
                  % (d_parent, 0.1 * PLANT, d_unsized, 0.1 * PLANT, plant,
                     got['delta_seen'], got['threshold'], lo, hi))
            for tag, m in (('parent pair', msg1), ('all-row unsized', msg2),
                           ('adversarial fixed plant', msg4)):
                print('  OFF-PATH REFUSAL (%s), verbatim: %s'
                      % (tag, ' | '.join(x.strip() for x in m.split('\n'))))
        return out
    finally:
        shutil.rmtree(d, ignore_errors=True)

def p_floor_control():
    """P_MIN, driven both ways: it must catch a near-flat triple AND must not
    swallow a real one."""
    deg = roache(0.0, 1.0, 1.0 + 2.0 ** -0.01)          # p = 0.01, below the floor
    if deg['state'] != 'DEGENERATE' or deg['gci_fine'] is not None:
        refuse('P_MIN did not catch a genuinely computed p = 0.01 (state %s, gci %r)'
               % (deg['state'], deg['gci_fine']))
    real = roache(0.0, 1.0, 1.0 + 2.0 ** -0.5)          # p = 0.5, a real result
    if real['state'] != 'CONVERGING' or real['gci_fine'] is None:
        refuse('P_MIN swallowed a real p = 0.5 result (state %s) -- a floor that eats '
               'results is not a floor' % real['state'])
    return {'p_below_floor': deg['p'], 'state_below': deg['state'],
            'p_above_floor': real['p'], 'state_above': real['state'],
            'result': 'the observed-order floor catches p = 0.01 and passes p = 0.5'}

# ------------------------------------------------------------------- selftest
def selftest():
    n = p = 0
    def chk(name, cond):
        nonlocal n, p
        n += 1
        if cond:
            p += 1
            print('  [PASS] ' + name)
        else:
            print('  [FAIL] ' + name)
    print('--- grade_vmfl011_r2.py --selftest')

    # ---- L-332 and the frozen constants
    c = assert_census()
    chk('ast.Assert count in this file is 0 (L-332)', c['ast_assert_in_this_file'] == 0)
    chk('the ast.Assert counter DOES see a planted assert', c['ast_assert_in_planted_source'] >= 1)
    fc = frozen_constants_control()
    chk('every frozen constant matches the registration', fc['n_bench'] == N_BENCH)
    chk('the reference CSV blob is the registered one', fc['reference_blob'] == REF_CSV_BLOB)

    # ---- the Roache classifier, carried from the parent
    t = roache(1.0, 0.5, 0.25, 2.0);  chk('roache CONVERGING on a halving family', t['state'] == 'CONVERGING')
    chk('roache p == 1 on that family', abs(t['p'] - 1.0) < 1e-12)
    t = roache(16.0, 4.0, 1.0, 2.0);  chk('roache p == 2 on a quartering family', abs(t['p'] - 2.0) < 1e-12)
    chk('roache extrapolates that family to 0', abs(t['f_extrapolated']) < 1e-12)
    chk('roache EXACT when all three equal', roache(1.0, 1.0, 1.0)['state'] == 'EXACT')
    chk('roache STAGNANT on one null step', roache(1.0, 1.0, 0.5)['state'] == 'STAGNANT')
    chk('roache OSCILLATORY on a sign flip', roache(1.0, 0.5, 0.9)['state'] == 'OSCILLATORY')
    chk('roache DIVERGENT when steps grow', roache(1.0, 0.5, -1.0)['state'] == 'DIVERGENT')
    chk('no GCI quoted when not CONVERGING', roache(1.0, 1.0, 1.0)['gci_fine'] is None)
    pf = p_floor_control()
    chk('P_MIN turns a computed p = 0.01 into DEGENERATE, NOT A RESULT, no GCI',
        pf['state_below'] == 'DEGENERATE')
    chk('P_MIN does NOT swallow a real p = 0.5 result', pf['state_above'] == 'CONVERGING')

    # ---- rule 4 with the L-342 field classes
    d = tempfile.mkdtemp(prefix='st_')
    try:
        lv = os.path.join(d, 'L9'); os.makedirs(os.path.join(lv, '0'))
        open(os.path.join(lv, '0', 'U'), 'w').write('x')
        rcp = os.path.join(d, 'RUN_RC.L9')
        ok, why, infra = strict_completion(lv, 10, ['U'], rcp)
        chk('L-342: an ABSENT RUN_RC reports rc NOT MEASURED, it does not void the level',
            (infra['rc_measured'] is False) and not any('rc =' in r for r in why))
        chk('L-342: the absent-RUN_RC bookkeeping defect is DISCLOSED, never silent',
            len(infra['notes']) == 1 and 'NOT MEASURED' in infra['notes'][0])
        chk('a level with no log.simpleFoam is still REFUSED with RUN_RC absent',
            not ok and any('no log.simpleFoam' in r for r in why))
        open(rcp, 'w').write('rc = 1\n')
        open(os.path.join(lv, 'log.simpleFoam'), 'w').write('\nEnd\n')
        ok, why, infra = strict_completion(lv, 10, ['U'], rcp)
        chk('a PRESENT RUN_RC carrying rc != 0 still REFUSES (absence is a disclosure, '
            'a bad value is not a licence)', (not ok) and any('rc = 1' in r for r in why))
        chk('strict completion REFUSES a missing time dir', not ok)
        open(rcp, 'w').write('rc = not-a-number\n')
        _, _, infra = strict_completion(lv, 10, ['U'], rcp)
        chk('an UNPARSEABLE RUN_RC is a bookkeeping defect, reported NOT MEASURED',
            infra['rc_measured'] is False and len(infra['notes']) == 1)
        # BEHAVIOURAL test that the End line is read from log.simpleFoam BY NAME.
        # A `log*` glob matches log.blockMesh FIRST alphabetically, so a mesher End
        # line would be mistaken for a solver End line -- measured on this box.
        lv2 = os.path.join(d, 'L8'); os.makedirs(os.path.join(lv2, '0'))
        open(os.path.join(lv2, '0', 'U'), 'w').write('x')
        rcp2 = os.path.join(d, 'RUN_RC.L8'); open(rcp2, 'w').write('rc = 0\n')
        open(os.path.join(lv2, 'log.blockMesh'), 'w').write('mesher\nEnd\n')
        open(os.path.join(lv2, 'log.simpleFoam'), 'w').write('solver ran, no End line\n')
        ok2, why2, _ = strict_completion(lv2, 10, ['U'], rcp2)
        chk('the mesher End line is NOT accepted as the solver End line',
            (not ok2) and any('no End line in log.simpleFoam' in r for r in why2))
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # ---- rule 3, the generic control, carried from the parent
    d = tempfile.mkdtemp(prefix='st2_')
    try:
        f = os.path.join(d, 'a.dat')
        open(f, 'w').write('# h\n0 1.0\n')
        codeb, msgb = expect_refusal(d, planted_zero, f, lambda pth, v: None,
                                     lambda pth: 0.0, 1.0, 'blind reader')
        chk('planted-zero REFUSES (exit 2) a reader that cannot see the plant', codeb == 2)

        def _see(pth):
            return float(open(pth).read().strip().split('\n')[-1].split()[-1])

        def _bump(pth, v):
            ln = open(pth).read().rstrip('\n').split('\n')
            g = ln[-1].split(); g[-1] = repr(float(g[-1]) + v)
            ln[-1] = ' '.join(g); open(pth, 'w').write('\n'.join(ln) + '\n')
        seen = planted_zero(f, _bump, _see, 1.0, 'seeing reader')
        chk('planted-zero ACCEPTS a reader that DOES see the plant',
            seen['control'] == 'PASS' and abs(seen['delta_seen'] - 1.0) < 1e-9)
        chk('planted-zero left the REAL artifact untouched', abs(_see(f) - 1.0) < 1e-12)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # ---- THE L-340 REPAIR, driven on the real bytes of the recorded refusal
    r = rms_sizing_control()
    chk('the embedded bytes ARE the attempt-1 L1 gate artifact (RMS matches)',
        abs(r['real_bytes_rms'] - REAL_L1_RMS_ATTEMPT1) < 1e-9)
    chk('probe 1: the PARENT single-row pair REFUSES these real bytes',
        r['parent_pair_delta'] < r['parent_pair_threshold'])
    chk('probe 1: it reproduces the delta quoted in VMFL011/RESULTS.md',
        abs(r['parent_pair_delta'] - REAL_L1_DELTA_ATTEMPT1_PAIR) < 1e-11)
    chk('probe 2: an ALL-ROW plant at the PARENT magnitude STILL refuses -- the '
        'SIZING is the repair, not the shape',
        r['allrow_unsized_delta'] < r['allrow_unsized_threshold'])
    chk('probe 3: the SIZED pair passes on the same real bytes',
        r['sized_delta'] > r['sized_threshold'])
    chk('probe 3: the move sits inside the DERIVED bounds [(K-2)*base, K*base]',
        r['derived_bounds'][0] <= r['sized_delta'] <= r['derived_bounds'][1])
    chk('probe 4: a fixed all-row plant is defeated by an adversarial profile, and '
        'the SIZED plant is not',
        r['adversarial_sized_delta'] > 0.1 * rms_plant_for(r['adversarial_base']))

    # ---- the gate artifact is a refusal when absent, never a number
    d = tempfile.mkdtemp(prefix='st3_')
    try:
        codeg, msgg = expect_refusal(d, _xy, d)
        chk('an ABSENT gate artifact REFUSES (exit 2) rather than returning a number',
            codeg == 2 and 'no bisect_U.xy under <scratch>' in msgg)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    if p == n:
        print('%d/%d' % (p, n))
        print('SELFTEST: all checks passed')
        return 0
    print('%d/%d' % (p, n))
    print('SELFTEST: %d check(s) FAILED' % (n - p))
    return 1

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
    # EVERY control runs BEFORE a single level is read.  A comparator whose controls
    # have not fired has produced no number.
    pre = {'frozen_constants': frozen_constants_control(),
           'assert_census': assert_census(),
           'p_floor': p_floor_control(),
           'rms_sizing_L340': rms_sizing_control()}
    R = {'case': 'VMFL011-R2', 'manual_page': 41, 'endTime': ENDTIME,
         'supersedes': 'register row #26 (VMFL011, NOT A RESULT -- the frozen comparator '
                       'refused on its own planted-zero control). A NEW row; the old one '
                       'is never overwritten (ANSYS_VERIFICATION_CHARTER section 6).',
         'parent_comparator_blob': 'e369496bf2e28ccb7145756e1c2442eb11e8e3f7',
         'reference': {'kind': 'NUM (code-to-code)', 'source': 'Jyotsna & Vanka, J. Comp. Phys. 122, 107-117 (1995), via the manual p.41 Reference; the curve is Ansys own digitisation carried in VMFL011_WB.wbpz as VMFL011_xvel.xy ("Benchmark x-norm", 46 rows). The manual p.42 prints only a FIGURE and NO discrete target table.', 'benchmark_min_u_norm': -0.318062, 'benchmark_min_at_y_m': -0.987229},
         'bands': {'rms_vs_benchmark': BAND_RMS},
         'tier_ceiling': TIER_CEILING,
         'field_classes': {'physics_critical': PHYSICS_CRITICAL,
                           'infrastructure': INFRASTRUCTURE,
                           'rule': 'a bookkeeping failure invalidates the bookkeeping, '
                                   'never the physics artifacts (L-342)'},
         'pre_read_controls': pre,
         'levels': {}, 'blocking': [], 'bookkeeping_defects': []}
    triple_vals = []
    for L in LEVELS:
        d = os.path.join(a.run_root, L)
        e = {'dir': d}
        if not os.path.isdir(d):
            e['state'] = 'ABSENT'; R['levels'][L] = e
            R['blocking'].append('%s: run directory absent' % L); continue
        rc_path = os.path.join(a.run_root, 'RUN_RC.%s' % L)
        ok, why, infra = strict_completion(d, ENDTIME, FIELDS, rc_path)
        e['strict_completion'] = {'ok': ok, 'reasons': why}
        e['infrastructure'] = infra
        for note in infra['notes']:
            R['bookkeeping_defects'].append('%s: %s' % (L, note))
        if not ok:
            e['state'] = 'INCOMPLETE'; R['levels'][L] = e
            R['blocking'].append('%s: strict completion (rule 4) FAILED: %s' % (L, '; '.join(why)))
            continue
        ic, res, msg = iterative_convergence(d, RESID_FLOOR, ['Ux_initial', 'Uy_initial', 'p_initial'])
        e['iterative_convergence'] = {'ok': ic, 'final_initial_residuals': res,
                                      'floor': RESID_FLOOR, 'note': msg}
        e['controls'] = controls(d)          # rule 3 -- exits 2 if a reader is blind
        c = channels(d); e['channels'] = c
        e['state'] = 'COMPLETE'
        if not ic:
            R['blocking'].append('%s: NOT iteratively converged (rule 5 step 1): %s' % (L, msg))
        triple_vals.append(c['u_min_norm'])
        R['levels'][L] = e
    if len(triple_vals) == 3:
        R['triple'] = roache(*triple_vals)
        R['triple_on'] = 'u_min_norm'
    else:
        R['blocking'].append('the grid triple is INCOMPLETE -- %d of 3 levels graded' % len(triple_vals))
    if R['blocking']:
        R['verdict'] = 'NOT A RESULT'; R['tier'] = 'NOT HELD'
    elif R['triple']['state'] != 'CONVERGING':
        R['verdict'] = 'NOT A RESULT'; R['tier'] = 'NOT HELD'
        R['blocking'].append('grid triple not CONVERGING: %s' % R['triple']['state'])
    else:
        v = R['levels'][LEVELS[-1]]['channels']['rms_vs_benchmark']
        R['deviation'] = {'rms_vs_benchmark': v}
        if v <= BAND_RMS:
            R['verdict'] = TIER_CEILING; R['tier'] = TIER_CEILING
        else:
            R['verdict'] = 'GATE FAIL'; R['tier'] = 'NOT HELD'
    R['ceiling_note'] = ('The reference is ANOTHER CODE NUMERICAL SOLUTION.  Code-to-code buys NEITHER V NOR P, so this case CANNOT exceed GATE REACHED whatever the number.')
    out = a.out or os.path.join(a.run_root, 'GRADING_VMFL011_R2.json')
    json.dump(R, open(out, 'w'), indent=2, sort_keys=True)
    print(json.dumps({k: R[k] for k in ('verdict', 'tier', 'blocking', 'bookkeeping_defects') if k in R}, indent=2))
    print('written: %s' % out)
    return 0

if __name__ == '__main__':
    sys.exit(main())
