"""
M2_kepsilon_family -- comparator.

Implements the gates of PREREGISTRATION.md section 6, in the frozen order
G-A -> G-B -> G-C -> G-D -> G-E.  A gate can only turn a row into NOT A RESULT
or BLOCKED; it can never turn one into a PASS.

VERDICT VOCABULARY (standing rule 1, and only this vocabulary):
    PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING

STANDING RULE 5 DOES NOT APPLY TO THIS RUNG.  One mesh per case: there is no
grid triple, no refinement ratio, no observed order, and NO GCI is computed or
quoted anywhere in this file.  Its absence is by design (PREREGISTRATION.md 1.1).

    cap_core_min_registered = 2600.0

L-332: no refusal here is an `assert`; every one is an explicit sys.exit(2) and
survives `python3 -O`.  L-314: every guard ships its planted-failure proof.
Standing rule 3: the reader is shown a plant written to DISK before any zero it
reports is believed -- and this rung's LaunderSharmaKE arm registers a wall
value that IS zero, so a blind reader would produce a confident, wrong PASS.
"""

import argparse
import ast
import json
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stage_m2 as S                                            # noqa: E402

CAP_CORE_MIN = 2600.0
CAP_CORE_MIN_ARM = 1300.0
EST_CORE_MIN_ARM = 649.0
RATE = 3.30e-06
RATE_LO, RATE_HI = 2.39e-06, 4.01e-06
ENDTIME = 20000
RATE_PER_CORE_H = 0.0513          # owner-stated; DERIVED dollars, not measured
# PREREGISTRATION.md, AMENDMENT 5's cost table: 13.4 % of the rung estimate.
WASTE_DUCTS_CORE_MIN = 173.6

# PREREGISTRATION.md 6 G-D1 / G-D2
BAND_D1_TIGHT, BAND_D1_FRAC = 1e-6, 0.999
BAND_D1_LOOSE = 1e-3
BAND_D2_WALL_ZERO = 1e-12
BAND_D2_D_POSITIVE_FRAC = 0.99
REQUIRED_FIELDS = ('U', 'p', 'k', 'epsilon', 'nut', 'phi')

VERDICTS = ('PASS', 'GATE REACHED', 'GATE FAIL', 'NOT A RESULT', 'BLOCKED', 'PENDING')


# --------------------------------------------------------------------------- #
#  G-A  PLANTED-ZERO CONTROL (standing rule 3).  Refuses; does not warn.
# --------------------------------------------------------------------------- #

def gate_a_planted_zero(scratch_dir):
    """Plant on DISK at BOTH sites gate G-D reads, and require both back."""
    os.makedirs(scratch_dir, exist_ok=True)
    f = os.path.join(scratch_dir, 'ga_epsilon')
    seen = {}
    for site in ('internal', 'patch'):
        with open(f, 'w') as fh:
            fh.write('FoamFile\n{\n    object epsilon;\n}\n'
                     'dimensions [0 2 -3 0 0 0 0];\n\n'
                     'internalField   nonuniform List<scalar>\n3\n(\n1\n2\n3\n)\n;\n\n'
                     'boundaryField\n{\n    bottomWall\n    {\n'
                     '        type            fixedValue;\n'
                     '        value           uniform 0;\n    }\n}\n')
        seen[site] = S.guard_reader_sees_plant(f, site)
    return seen


# --------------------------------------------------------------------------- #
#  G-B  STAGING EQUIVALENCE
# --------------------------------------------------------------------------- #

REGISTERED_DIFFS = ('constant/turbulenceProperties', 'system/fvSolution',
                    'system/controlDict', '0.orig/epsilon')
REGISTERED_IDENTICAL = ('system/fvSchemes', 'constant/transportProperties',
                        '0.orig/U', '0.orig/p', '0.orig/k', '0.orig/omega', '0.orig/nut')


def gate_b_staging(src, dst):
    """Return (bad_identical, missing).  Empty and empty is the only pass."""
    bad, missing = [], []
    for rel in REGISTERED_IDENTICAL:
        s = os.path.join(src, rel.replace('0.orig/', '0/'))
        d = os.path.join(dst, rel)
        if not os.path.exists(s):
            continue
        if not os.path.exists(d):
            missing.append(rel)
        elif S.sha(s) != S.sha(d):
            bad.append(rel)
    for rel in REGISTERED_DIFFS:
        if not os.path.exists(os.path.join(dst, rel)):
            missing.append(rel)
    return bad, missing


# --------------------------------------------------------------------------- #
#  G-C  STRICT COMPLETION + AGE GUARD (standing rule 4), with the L-342 split
# --------------------------------------------------------------------------- #

def read_status(casedir):
    p = os.path.join(casedir, 'STATUS')
    if not os.path.exists(p):
        return None
    out = {}
    for ln in open(p):
        if '=' in ln:
            k, v = ln.split('=', 1)
            out[k.strip()] = v.strip()
    return out


def time_dirs(casedir):
    out = []
    for d in os.listdir(casedir):
        if re.fullmatch(r'\d+(\.\d+)?', d) and os.path.isdir(os.path.join(casedir, d)):
            out.append(d)
    return sorted(out, key=float)


def gate_c_completion(casedir):
    """All-or-nothing.  Physics and infrastructure are reported SEPARATELY
    (L-342, and Sanaa 2026-08-27 ruling R-RC): an absent rc RECORD makes clause 1
    NOT MEASURED and can never void intact physics fields."""
    phys, infra = {}, {}
    log = os.path.join(casedir, 'log.solve')
    logtxt = open(log, errors='replace').read() if os.path.exists(log) else ''

    st = read_status(casedir)
    if st is None or 'rc' not in st:
        infra['rc'] = 'NOT MEASURED'          # infrastructure, never voids physics
    else:
        infra['rc'] = 'ok' if st['rc'] == '0' else 'rc=%s' % st['rc']
    infra['End_line'] = 'ok' if re.search(r'^End\s*$', logtxt, re.M) else 'absent'
    nexec = len(re.findall(r'^ExecutionTime = ', logtxt, re.M))
    infra['ExecutionTime_lines'] = nexec

    # RULING 1 (closure-supervisor, 2026-08-27; PREREGISTRATION.md 13 AMENDMENT 5).
    # Standing rule 4 requires `ExecutionTime count == endTime`.  The draft graded
    # this in `phys` with a 0.5 tolerance -- a quietly weakened equality, and a band
    # chosen before this lab had ever seen the count.  It is now the equality the
    # rule states, in `phys`, gating, in the shape frozen at grade_g1.py:502-505.
    phys['P7_ExecutionTime'] = ('ok' if nexec == ENDTIME else
                                'P7 ExecutionTime lines: %d, registered endTime %d. '
                                '(This is the L-342 clause: if the cause is a solver '
                                'that prints extra lines, it is triaged by the '
                                'supervisor, never reclassified here.)' % (nexec, ENDTIME))

    tds = [t for t in time_dirs(casedir) if float(t) > 0]
    if not tds:
        phys['last_time'] = 'NONE'
        phys['fields'] = 'NONE'
        phys['age_guard'] = 'NONE'
        return phys, infra, None
    last = tds[-1]
    # RULING 2: residualControl is emptied at staging, so there is no criterion and
    # no early stop.  `last time == endTime` is therefore the literal rule-4 test,
    # with no converged-stop alternative.  A `SIMPLE solution converged` line would
    # now mean the emptying failed, so it is recorded as a FINDING, not an excuse.
    conv = re.search(r'SIMPLE solution converged in (\d+) iterations', logtxt)
    expect_ok = abs(float(last) - ENDTIME) < 1e-9
    phys['last_time'] = '%s (%s)' % (last, 'ok' if expect_ok else 'NOT endTime')
    if conv is not None:
        phys['early_stop_FINDING'] = ('the log carries "SIMPLE solution converged in %s '
                                      'iterations"; RULING 2 empties every residualControl '
                                      'at staging, so a criterion was satisfied that should '
                                      'not exist' % conv.group(1))
    missing = [f for f in REQUIRED_FIELDS if not os.path.exists(os.path.join(casedir, last, f))]
    phys['fields'] = 'ok' if not missing else 'missing %s' % missing

    # AGE GUARD: every field at `last` must be NEWER than the case's own 0/k
    ref = os.path.join(casedir, '0', 'k')
    if not os.path.exists(ref):
        phys['age_guard'] = 'NOT MEASURED (no 0/k to date the run against)'
    else:
        t0 = os.path.getmtime(ref)
        stale = [f for f in REQUIRED_FIELDS
                 if os.path.exists(os.path.join(casedir, last, f))
                 and os.path.getmtime(os.path.join(casedir, last, f)) <= t0]
        phys['age_guard'] = 'ok' if not stale else 'STALE: %s' % stale
    return phys, infra, last


def completion_ok(phys):
    """All-or-nothing, and P7 is one of the clauses (RULING 1)."""
    return (phys.get('fields') == 'ok'
            and phys.get('age_guard') == 'ok'
            and phys.get('P7_ExecutionTime') == 'ok'
            and 'early_stop_FINDING' not in phys
            and str(phys.get('last_time', '')).endswith('(ok)'))


# --------------------------------------------------------------------------- #
#  G-D  PRIMARY -- the wall treatment must come out where section 2 says
# --------------------------------------------------------------------------- #

def wall_arrays(casedir, last, nu):
    """yP, owner index, k at the owner cell, epsilon at the owner cell, and the
    epsilon wall patch values, for every wall patch."""
    walls, nCells, _ = S.mesh_walls(casedir)
    ef = S.read_field(os.path.join(casedir, last, 'epsilon'), 1)
    kf = S.read_field(os.path.join(casedir, last, 'k'), 1)
    ei, ki = ef['internal'], kf['internal']
    out = {}
    for name, w in walls.items():
        own = w['owner']
        kP = (np.full(len(own), float(ki[1])) if isinstance(ki, tuple) else ki[own])
        eP = (np.full(len(own), float(ei[1])) if isinstance(ei, tuple) else ei[own])
        ew = None
        for key, (kind, val, _ty) in ef['patches'].items():
            if not S.key_is_wall(key, {name}):
                continue
            if kind == 'uniform':
                ew = np.full(len(own), float(val))
            elif kind == 'list' and isinstance(val, np.ndarray) and len(val) == len(own):
                ew = val
        kw = None
        for key, (kind, val, _ty) in kf['patches'].items():
            if not S.key_is_wall(key, {name}):
                continue
            if kind == 'uniform':
                kw = np.full(len(own), float(val))
            elif kind == 'list' and isinstance(val, np.ndarray) and len(val) == len(own):
                kw = val
        out[name] = dict(yP=w['yP'], kP=kP, eP=eP, ew=ew, kw=kw, nu=nu, own=own)
    return out


def gate_d1_kepsilon(wa):
    """epsilon in the wall-adjacent cells must equal what epsilonWallFunction
    puts there, and that is NOT the bare per-face 2*nu*k_P/y_P^2.

    The source ACCUMULATES over every wall face a cell owns, weighted by
    cornerWeights = 1/(number of wall faces on that cell):

        epsilonWallFunctionFvPatchScalarField.C:110   ++weights[faceCell];
        epsilonWallFunctionFvPatchScalarField.C:120   cornerWeights_ = 1.0/wf.patchInternalField();
        epsilonWallFunctionFvPatchScalarField.C:240   epsilon0[faceCell] += cornerWeights[facei]*epsilonVis(facei);

    and then FIXES the accumulated cell value by matrix.setValues (:593).  For a
    cell owning one wall face the weighted sum IS 2*nu*k_P/y_P^2 and nothing
    changes.  For a cell owning two, the source stores the AVERAGE of the two
    faces' epsilonVis, and a per-face prediction is simply a wrong transcription
    of the source -- measured, on the 8 DUCT cases, every one of which has
    exactly one such corner cell (PREREGISTRATION.md 13, AMENDMENT 1).

    Still reference-free: this is an analytic expression from the OpenFOAM
    source, never a comparison with reference data.
    """
    yP = np.concatenate([a['yP'] for a in wa.values()])
    kP = np.concatenate([a['kP'] for a in wa.values()])
    eP = np.concatenate([a['eP'] for a in wa.values()])
    own = np.concatenate([np.asarray(a['own']) for a in wa.values()]).astype(np.int64)
    nu = float(next(iter(wa.values()))['nu'])

    eps_vis = 2.0 * nu * kP / np.maximum(yP ** 2, 1e-300)      # per WALL FACE
    n = int(own.max()) + 1
    cnt = np.bincount(own, minlength=n).astype(float)          # wall faces per cell
    acc = np.bincount(own, weights=eps_vis, minlength=n)       # sum of w*epsilonVis
    pred_cell = acc / np.maximum(cnt, 1.0)                     # cornerWeights = 1/cnt
    pred = pred_cell[own]                                      # what the CELL holds

    rel = np.abs(eP - pred) / np.maximum(np.abs(pred), 1e-300)
    ys = S.CMU ** 0.25 * yP * np.sqrt(np.maximum(kP, 0.0)) / nu
    n_corner_faces = int((cnt[own] > 1).sum())
    return dict(frac_tight=float((rel <= BAND_D1_TIGHT).mean()),
                frac_loose=float((rel <= BAND_D1_LOOSE).mean()),
                rel_max=float(rel.max()), rel_med=float(np.median(rel)),
                ystar_max_converged=float(ys.max()),
                branch_still_viscous=bool(ys.max() < S.YPLUSLAM),
                n_wall_faces_on_corner_cells=n_corner_faces,
                cornerWeights_applied=bool(n_corner_faces > 0),
                n=int(rel.size))


def gate_d2_laundersharma(wa):
    """Two conditions (PREREGISTRATION.md 6 G-D2):
      (i)  the transported epsilonTilda vanishes at the wall;
      (ii) the true dissipation is NOT also zero there -- D = 2 nu |grad sqrt k|^2
           must be strictly positive, or the row is a dead solve wearing a
           correct boundary condition.

    D is estimated one-sidedly from the wall-normal difference,
    d(sqrt k)/dn ~ (sqrt(k_P) - sqrt(k_w))/y_P.  THIS IS AN ESTIMATE, not
    fvc::grad, and it is labelled as one wherever it is printed.
    """
    zeros, Ds = [], []
    for name, a in wa.items():
        if a['ew'] is None:
            return None
        zeros.append(np.abs(a['ew']))
        kw = a['kw'] if a['kw'] is not None else np.zeros_like(a['kP'])
        dsk = (np.sqrt(np.maximum(a['kP'], 0.0)) - np.sqrt(np.maximum(kw, 0.0))) / np.maximum(a['yP'], 1e-300)
        Ds.append(2.0 * a['nu'] * dsk ** 2)
    z = np.concatenate(zeros)
    D = np.concatenate(Ds)
    return dict(wall_abs_max=float(z.max()),
                frac_wall_zero=float((z <= BAND_D2_WALL_ZERO).mean()),
                D_frac_positive=float((D > 0.0).mean()),
                D_med_ESTIMATE=float(np.median(D)), n=int(z.size))


# --------------------------------------------------------------------------- #
#  G-E  iterative convergence.  Reported, not gated.
# --------------------------------------------------------------------------- #

def gate_e_convergence(casedir):
    log = os.path.join(casedir, 'log.solve')
    if not os.path.exists(log):
        return dict(status='NOT MEASURED (no log.solve)')
    txt = open(log, errors='replace').read()
    conv = re.search(r'SIMPLE solution converged in (\d+) iterations', txt)
    nexec = len(re.findall(r'^ExecutionTime = ', txt, re.M))
    nbound = len(re.findall(r'^bounding epsilon', txt, re.M))
    res = {}
    for f in ('Ux', 'p', 'k', 'epsilon'):
        hits = re.findall(r'Solving for %s, Initial residual = ([0-9.eE+-]+)' % f, txt)
        if hits:
            res[f] = float(hits[-1])
    return dict(status='converged' if conv else ('CAP-REACHED' if nexec >= ENDTIME else 'stopped early'),
                iterations=int(conv.group(1)) if conv else nexec,
                final_initial_residuals=res,
                bounding_epsilon_lines=nbound,
                bounding_epsilon_frac=(nbound / nexec if nexec else None))


# --------------------------------------------------------------------------- #
#  Secondaries.  REPORTED, never gated (D534: REPORTED is a row class).
# --------------------------------------------------------------------------- #

def l2_separation(a_dir, b_dir, last_a, last_b, field, ncomp):
    pa = os.path.join(a_dir, last_a, field)
    pb = os.path.join(b_dir, last_b, field)
    if not (os.path.exists(pa) and os.path.exists(pb)):
        return None
    A = S.read_field(pa, ncomp)['internal']
    B = S.read_field(pb, ncomp)['internal']
    if not (isinstance(A, np.ndarray) and isinstance(B, np.ndarray) and A.shape == B.shape):
        return None
    den = np.linalg.norm(B)
    return float(np.linalg.norm(A - B) / den) if den > 0 else None


# --------------------------------------------------------------------------- #
#  Cost calibration (standing rule 12, Sanaa 2026-08-23)
# --------------------------------------------------------------------------- #

def cost_row(arm_root, ncells_by_case):
    actual, per = 0.0, {}
    for cid, ncells in ncells_by_case.items():
        st = read_status(os.path.join(arm_root, cid))
        if st is None or 'core_min' not in st:
            per[cid] = dict(actual='NOT MEASURED (no STATUS; INFRASTRUCTURE, L-342)')
            continue
        cm = float(st['core_min'])
        pred = ncells * ENDTIME * RATE / 60.0
        actual += cm
        per[cid] = dict(actual_core_min=cm, predicted_core_min=round(pred, 4),
                        ratio=round(cm / pred, 4) if pred > 0 else None)
    return dict(arm_actual_core_min=round(actual, 4),
                arm_predicted_core_min=round(EST_CORE_MIN_ARM, 4),
                arm_ratio_actual_over_predicted=(round(actual / EST_CORE_MIN_ARM, 4)
                                                 if EST_CORE_MIN_ARM else None),
                arm_cap_core_min=CAP_CORE_MIN_ARM,
                dollars_derived_not_measured=round(actual / 60.0 * RATE_PER_CORE_H, 4),
                dollars_basis=('DERIVED at the owner-stated $%.4f/core-h; the box '
                               'cannot read its own billing (COMPUTE_BUDGET_CHARTER '
                               'section 5), so this is reported-by-owner, NOT measured'
                               % RATE_PER_CORE_H),
                waste_core_min_named=WASTE_DUCTS_CORE_MIN,
                waste_basis=('the 8 DUCT cases run past the iteration at which the '
                             'shipped kOmegaSST solve met its own residualControl '
                             '(334/405/1109/1540/2428/3636/5125/7009), priced at the '
                             'registered %.2e s/cell-iteration across both arms. '
                             'RULING 2 empties residualControl so M2 runs to endTime: '
                             'this is what standing rule 4 costs when it is honoured. '
                             'The convergence counts are kOmegaSST\'s, so this is an '
                             'ESTIMATE, not a measurement (PREREGISTRATION.md 12.5).'
                             % RATE),
                waste_note='NAMED SEPARATELY, never absorbed into the ratio above '
                           '(COMPUTE_BUDGET_CHARTER section 6)',
                per_case=per)


# --------------------------------------------------------------------------- #

def grade(run_root, arms=('kEpsilon', 'LaunderSharmaKE'), scratch=None):
    scratch = scratch or os.path.join(run_root, '_grade_scratch')

    # ---- G-A first.  If the reader is blind, NOTHING below is evidence. -----
    ga = gate_a_planted_zero(scratch)
    if not all(ga.values()):
        sys.stderr.write('REFUSE (gate G-A, standing rule 3): the reader could not '
                         'see a plant written to disk at %s. Every row in this rung '
                         'is NOT A RESULT.\n'
                         % [k for k, v in ga.items() if not v])
        sys.exit(2)

    report = {'rung': 'M2_kepsilon_family', 'gate_A_planted_zero': ga,
              'rule_5_applies': False,
              'rule_5_note': 'One mesh per case. No grid triple, no observed order, '
                             'NO GCI is computed or quoted anywhere in this rung.',
              'arms': {}}
    cases = dict(S.discover_cases())

    for arm in arms:
        arm_root = os.path.join(run_root, arm)
        rows, ncells = {}, {}
        if not os.path.isdir(arm_root):
            report['arms'][arm] = {'verdict': 'PENDING: %s' % arm_root}
            continue
        for cid, src in cases.items():
            d = os.path.join(arm_root, cid)
            row = {'chips': []}
            if not os.path.isdir(d):
                row['verdict'] = 'PENDING: %s' % d
                rows[cid] = row
                continue
            nu = S.read_nu(src)
            bad, missing = gate_b_staging(src, d)
            row['gate_B'] = ('ok' if not bad and not missing
                             else {'unexpectedly_differing': bad, 'missing': missing})
            phys, infra, last = gate_c_completion(d)
            row['gate_C_physics'] = phys
            row['gate_C_infrastructure'] = infra
            row['gate_E'] = gate_e_convergence(d)

            ncells[cid] = S.mesh_walls(d)[1] if last else 0
            if cid == 'CBFS13700':
                row['chips'].append('NEAR-WALL-MARGINAL')
            if cid in ('CBFS13700', 'PH_Breuer'):
                row['chips'].append('SCHEME-FALLTHROUGH')
            if arm == 'kEpsilon':
                row['chips'].append('HIGH-RE-MODEL-ON-RESOLVED-MESH')
            if row['gate_E'].get('status') == 'CAP-REACHED':
                row['chips'].append('CAP-REACHED')
            bf = row['gate_E'].get('bounding_epsilon_frac')
            if bf is not None and bf > 0.01:
                row['chips'].append('BOUNDING-EPSILON')

            if row['gate_B'] != 'ok':
                row['verdict'] = 'NOT A RESULT'
                row['because'] = 'gate G-B: the staged tree differs outside the registered set'
            elif not completion_ok(phys):
                row['verdict'] = 'NOT A RESULT'
                row['because'] = 'gate G-C: strict completion / age guard not satisfied'
            else:
                wa = wall_arrays(d, last, nu)
                if arm == 'kEpsilon':
                    r = gate_d1_kepsilon(wa)
                    row['gate_D1'] = r
                    if not r['branch_still_viscous']:
                        row['verdict'] = 'NOT A RESULT'
                        row['because'] = ('gate G-D1: the converged field pushes y* to %.3f, '
                                          'at or above yPlusLam %.2f -- the registered wall '
                                          'treatment was chosen on a premise the answer violated'
                                          % (r['ystar_max_converged'], S.YPLUSLAM))
                    elif r['frac_tight'] >= BAND_D1_FRAC and r['frac_loose'] >= 1.0:
                        row['verdict'] = 'PASS'
                    else:
                        row['verdict'] = 'GATE FAIL'
                        row['because'] = ('gate G-D1: %.4f of wall cells within 1e-6 (need %.3f) '
                                          'and %.4f within 1e-3 (need 1.000). This is a finding '
                                          'about PREREGISTRATION.md 2.3, reported as such.'
                                          % (r['frac_tight'], BAND_D1_FRAC, r['frac_loose']))
                else:
                    r = gate_d2_laundersharma(wa)
                    row['gate_D2'] = r
                    if r is None:
                        row['verdict'] = 'NOT A RESULT'
                        row['because'] = 'gate G-D2: no epsilon wall patch value could be read'
                    elif (r['frac_wall_zero'] >= 1.0
                          and r['D_frac_positive'] >= BAND_D2_D_POSITIVE_FRAC):
                        row['verdict'] = 'PASS'
                    elif r['frac_wall_zero'] < 1.0:
                        row['verdict'] = 'GATE FAIL'
                        row['because'] = ('gate G-D2(i): |epsilon| at the wall reaches %.3e, '
                                          'above the registered %.0e'
                                          % (r['wall_abs_max'], BAND_D2_WALL_ZERO))
                    else:
                        row['verdict'] = 'GATE FAIL'
                        row['because'] = ('gate G-D2(ii): D > 0 on only %.4f of wall faces '
                                          '(need %.2f). A wall where the true dissipation is '
                                          'also zero is a dead solve wearing a correct boundary '
                                          'condition. D is an ESTIMATE (one-sided difference), '
                                          'not fvc::grad.' % (r['D_frac_positive'],
                                                              BAND_D2_D_POSITIVE_FRAC))
            rows[cid] = row
        report['arms'][arm] = {'rows': rows, 'cost': cost_row(arm_root, ncells)}

    # secondaries, REPORTED only
    a, b = os.path.join(run_root, 'kEpsilon'), os.path.join(run_root, 'LaunderSharmaKE')
    sec = {}
    if os.path.isdir(a) and os.path.isdir(b):
        for cid in cases:
            da, db = os.path.join(a, cid), os.path.join(b, cid)
            if not (os.path.isdir(da) and os.path.isdir(db)):
                continue
            ta, tb = time_dirs(da), time_dirs(db)
            if not ta or not tb:
                continue
            sec[cid] = {'U': l2_separation(da, db, ta[-1], tb[-1], 'U', 3),
                        'k': l2_separation(da, db, ta[-1], tb[-1], 'k', 1)}
    report['secondary_A_arm_separation'] = {
        'class': 'REPORTED', 'gated': False,
        'note': 'D534: REPORTED is a row class, not a verdict, and is excluded from '
                'every census. With no null arm in this rung the separation cannot be '
                'attributed between model form and staging (PREREGISTRATION.md 7.2).',
        'values': sec}
    report['secondary_B_vs_reference'] = {
        'class': 'REPORTED', 'gated': False,
        'note': "Not computed as a verdict. M2's absolute readings become defensible "
                "only if and when M1's kOmegaSST_null arm (its gate G2) has passed "
                '(PREREGISTRATION.md 7.3).'}
    report['headline_metrics_owed'] = ('CPU %, GPU % (0 by construction: M2 uses no GPU), '
                                       'closure queue depth, idle-minutes per resource '
                                       '(Sanaa 2026-08-27 section 2)')
    return report


# --------------------------------------------------------------------------- #
#  SELFTEST -- L-332 and L-314
# --------------------------------------------------------------------------- #

def selftest():
    here = os.path.dirname(os.path.abspath(__file__))
    ok = True

    def report(name, passed, detail=''):
        nonlocal ok
        ok = ok and passed
        print('%-58s %s %s' % (name, 'ok' if passed else 'FAIL', detail))

    n = sum(1 for nd in ast.walk(ast.parse(open(os.path.join(here, 'grade_m2.py')).read()))
            if isinstance(nd, ast.Assert))
    report('L-332 zero ast.Assert in grade_m2.py', n == 0, '(got %d)' % n)
    planted = 'def f(x):\n    assert x\n    assert not x\n    return x\n'
    m = sum(1 for nd in ast.walk(ast.parse(planted)) if isinstance(nd, ast.Assert))
    report('L-332 assert-counter can count a planted assert (expect 2)', m == 2, '(got %d)' % m)

    src = open(os.path.join(here, 'grade_m2.py')).read()

    def gci_machinery(source, drop_selftest=False):
        """Names that would exist if this file computed a GCI.  AST-based, so it
        cannot match its own detector's source text -- a regex here matched its
        own literal and reported a false FAIL.

        drop_selftest removes THIS function's scaffolding from the tree before
        scanning: the frozen grading path is every function except `selftest`,
        and the detector's own helpers are named for what they hunt.
        """
        tree = ast.parse(source)
        if drop_selftest:
            tree.body = [n for n in tree.body
                         if not (isinstance(n, ast.FunctionDef) and n.name == 'selftest')]
        names = []
        for nd in ast.walk(tree):
            if isinstance(nd, (ast.FunctionDef, ast.AsyncFunctionDef)):
                names.append(nd.name)
            elif isinstance(nd, ast.Name) and isinstance(nd.ctx, ast.Store):
                names.append(nd.id)
        hits = [n for n in names if 'gci' in n.lower()
                or n.lower() in ('fs', 'f_s', 'safety_factor')]
        return hits

    report('standing rule 5: the GRADING PATH computes NO GCI '
           '(AST over every function except selftest)',
           gci_machinery(src, drop_selftest=True) == [])
    planted_gci = ('def compute_gci(a, b, c):\n    Fs = 1.25\n'
                   '    gci_fine = Fs * abs(a - b)\n    return gci_fine\n')
    report('L-314: the GCI detector CAN fire (planted machinery is found)',
           sorted(gci_machinery(planted_gci)) == ['Fs', 'compute_gci', 'gci_fine'])
    report('standing rule 5 is disapplied in the emitted report',
           "'rule_5_applies': False" in src)
    report('verdict vocabulary is exactly the six of standing rule 1',
           set(re.findall(r"'(PASS|GATE REACHED|GATE FAIL|NOT A RESULT|BLOCKED|PENDING)", src))
           <= set(VERDICTS))
    # G-A both directions, on disk
    import tempfile
    d = tempfile.mkdtemp()
    seen = gate_a_planted_zero(d)
    report('G-A reader sees the INTERNAL plant on disk', seen['internal'])
    report('G-A reader sees the WALL-PATCH plant on disk', seen['patch'])
    f = os.path.join(d, 'ga_epsilon')
    with open(f, 'w') as fh:
        fh.write('FoamFile\n{\n    object epsilon;\n}\nboundaryField\n{\n}\n')
    report('G-A L-314: a blind reader is REFUSED, not passed',
           not S.guard_reader_sees_plant(f, 'internal'))

    # G-D1 both directions, against a synthetic field the source predicts exactly
    nu, yP = 1.5e-5, np.full(50, 5.7e-7)
    kP = np.full(50, 2.5e-6)
    pred = 2.0 * nu * kP / yP ** 2
    wa = {'w': dict(yP=yP, kP=kP, eP=pred.copy(), ew=np.zeros(50),
                    kw=np.zeros(50), nu=nu, own=np.arange(50))}
    r = gate_d1_kepsilon(wa)
    report('G-D1 PASSES on a field that IS 2*nu*k/y^2', r['frac_tight'] == 1.0)
    wa['w']['eP'] = pred * 1.05
    r2 = gate_d1_kepsilon(wa)
    report('G-D1 L-314: 5 percent off -> control flips to fail',
           r2['frac_tight'] == 0.0 and r2['frac_loose'] == 0.0)
    wa['w']['eP'] = pred.copy()
    wa['w']['kP'] = np.full(50, 1.0e6)          # drive y* above yPlusLam
    r3 = gate_d1_kepsilon(wa)
    report('G-D1 L-314: y* above yPlusLam is detected', not r3['branch_still_viscous'])

    # G-D1 cornerWeights (PREREGISTRATION.md 13 AMENDMENT 1), both directions.
    # A corner cell owning two wall faces of UNEQUAL yP: the source stores the
    # cornerWeights average, so a correct predictor must too.
    nuC = 1e-5
    yPc = np.array([5.734e-07, 5.878e-07, 8.0e-07, 9.0e-07])
    kPc = np.full(4, 1e-3)
    ownc = np.array([0, 0, 1, 2])               # cell 0 owns TWO wall faces
    evis = 2.0 * nuC * kPc / yPc ** 2
    truth = evis.copy()
    truth[0] = truth[1] = 0.5 * (evis[0] + evis[1])   # what setValues fixes there
    wc = {'w': dict(yP=yPc, kP=kPc, eP=truth, ew=np.zeros(4), kw=np.zeros(4),
                    nu=nuC, own=ownc)}
    rc1 = gate_d1_kepsilon(wc)
    report('G-D1 cornerWeights: the corner cell is PREDICTED, not failed',
           rc1['frac_tight'] == 1.0 and rc1['n_wall_faces_on_corner_cells'] == 2)
    wc['w']['eP'] = evis.copy()                 # naive per-face field: must FAIL
    rc2 = gate_d1_kepsilon(wc)
    report('G-D1 L-314: a per-face (uncorner-weighted) field flips the control',
           rc2['frac_tight'] == 0.5 and rc2['frac_loose'] == 0.5)
    wc['w']['own'] = np.array([0, 1, 2, 3])     # no corner cell at all
    wc['w']['eP'] = evis.copy()
    rc3 = gate_d1_kepsilon(wc)
    report('G-D1 cornerWeights is INERT where no cell owns two wall faces',
           rc3['frac_tight'] == 1.0 and rc3['cornerWeights_applied'] is False)

    # G-D2 both directions
    wa2 = {'w': dict(yP=np.full(20, 1e-3), kP=np.full(20, 1e-3), eP=np.full(20, 1.0),
                     ew=np.zeros(20), kw=np.zeros(20), nu=1e-5)}
    q = gate_d2_laundersharma(wa2)
    report('G-D2 PASSES on epsilonTilda_wall = 0 with D > 0',
           q['frac_wall_zero'] == 1.0 and q['D_frac_positive'] == 1.0)
    wa2['w']['ew'] = np.full(20, 1e-6)
    report('G-D2 L-314: a non-zero wall value flips the control',
           gate_d2_laundersharma(wa2)['frac_wall_zero'] == 0.0)
    wa2['w']['ew'] = np.zeros(20)
    wa2['w']['kP'] = np.zeros(20)               # dead solve: D also zero
    q3 = gate_d2_laundersharma(wa2)
    report('G-D2 L-314: a DEAD SOLVE (D also zero) is caught, not passed',
           q3['D_frac_positive'] == 0.0)

    # G-C: the L-342 split
    c = os.path.join(d, 'case')
    os.makedirs(os.path.join(c, '0'))
    open(os.path.join(c, '0', 'k'), 'w').write('x')
    phys, infra, last = gate_c_completion(c)
    report('G-C: absent rc RECORD is INFRASTRUCTURE / NOT MEASURED (L-342, R-RC)',
           infra['rc'] == 'NOT MEASURED')
    report('G-C: with no time dirs the PHYSICS clauses are NONE, not silently ok',
           phys['fields'] == 'NONE' and not completion_ok(phys))
    OKP = {'fields': 'ok', 'age_guard': 'ok', 'last_time': '20000 (ok)',
           'P7_ExecutionTime': 'ok'}
    report('G-C L-314: completion_ok cannot pass on missing fields',
           not completion_ok(dict(OKP, fields='missing [1]')))
    report('G-C L-314: completion_ok cannot pass a STALE age guard',
           not completion_ok(dict(OKP, age_guard='STALE: [1]')))
    report('G-C: an infrastructure gap alone does NOT void intact physics',
           completion_ok(OKP))
    # RULING 1, both directions: P7 is a GATING EQUALITY in phys, not a band.
    report('RULING 1 L-314: P7 one line short of endTime FAILS completion',
           not completion_ok(dict(OKP, P7_ExecutionTime='P7 ExecutionTime lines: 19999')))
    report('RULING 1 L-314: P7 one line OVER endTime also FAILS (equality, not >=)',
           not completion_ok(dict(OKP, P7_ExecutionTime='P7 ExecutionTime lines: 20001')))
    def grading_path_text(source):
        """`source` minus the selftest function.  A detector whose needle appears
        in its own source reports a false FAIL -- this file's GCI detector already
        paid for that lesson, and this check hunts literals too."""
        tree = ast.parse(source)
        lines = source.splitlines()
        keep = list(lines)
        for nd in tree.body:
            if isinstance(nd, ast.FunctionDef) and nd.name == 'selftest':
                for i in range(nd.lineno - 1, nd.end_lineno):
                    keep[i] = ''
        return '\n'.join(keep)
    gp = grading_path_text(src)
    report('RULING 1: the 0.5-tolerance band is GONE from the grading path',
           '* 0.5' not in gp and 'ExecutionTime_vs_last' not in gp)
    report('RULING 1 L-314: the band detector CAN fire on planted source',
           '* 0.5' in grading_path_text('def f():\n    x = y * 0.5\n'
                                        'def selftest():\n    pass\n'))
    report('RULING 1: P7 carries the supervisor-triage note (grade_g1.py:502-505 shape)',
           'triaged by the supervisor, never reclassified here' in src)
    _d2 = os.path.join(d, 'p7case'); os.makedirs(os.path.join(_d2, '0'))
    open(os.path.join(_d2, '0', 'k'), 'w').write('x')
    open(os.path.join(_d2, 'log.solve'), 'w').write('ExecutionTime = 1 s\n' * 3)
    _p7, _i7, _l7 = gate_c_completion(_d2)
    report('RULING 1: 3 ExecutionTime lines against endTime %d is NOT ok' % ENDTIME,
           _p7['P7_ExecutionTime'] != 'ok' and str(ENDTIME) in _p7['P7_ExecutionTime'])
    # RULING 2, both directions: an early stop is a FINDING, never an excuse.
    open(os.path.join(_d2, 'log.solve'), 'w').write(
        'ExecutionTime = 1 s\nSIMPLE solution converged in 405 iterations\n')
    os.makedirs(os.path.join(_d2, '405'))
    for _f in REQUIRED_FIELDS:
        open(os.path.join(_d2, '405', _f), 'w').write('x')
    _p8, _i8, _l8 = gate_c_completion(_d2)
    report('RULING 2 L-314: a converged EARLY STOP is a FINDING and fails completion',
           'early_stop_FINDING' in _p8 and not completion_ok(_p8))
    report('RULING 2: a converged stop no longer satisfies last_time',
           _p8['last_time'].endswith('(NOT endTime)'))

    # G-B both directions
    s1 = os.path.join(d, 'src'); d1 = os.path.join(d, 'dst')
    os.makedirs(os.path.join(s1, 'system')); os.makedirs(os.path.join(d1, 'system'))
    open(os.path.join(s1, 'system', 'fvSchemes'), 'w').write('same')
    open(os.path.join(d1, 'system', 'fvSchemes'), 'w').write('same')
    bad, miss = gate_b_staging(s1, d1)
    report('G-B: identical fvSchemes is quiet', bad == [])
    open(os.path.join(d1, 'system', 'fvSchemes'), 'w').write('MUTATED')
    bad2, _ = gate_b_staging(s1, d1)
    report('G-B L-314: one mutated byte in fvSchemes flips the control',
           bad2 == ['system/fvSchemes'])

    # cap agreement with the launcher
    rs = open(os.path.join(here, 'run_m2.sh')).read()
    report('cap agrees with run_m2.sh (%.1f)' % CAP_CORE_MIN,
           ('CAP_CORE_MIN=%.1f' % CAP_CORE_MIN) in rs)
    report('arm cap agrees with run_m2.sh (%.1f)' % CAP_CORE_MIN_ARM,
           ('CAP_CORE_MIN_ARM=%.1f' % CAP_CORE_MIN_ARM) in rs)

    import shutil
    shutil.rmtree(d)
    print('\nSELFTEST %s' % ('PASS' if ok else 'FAIL'))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run-root', default='/home/ubuntu/closure-data/m2_kepsilon_family')
    ap.add_argument('--out')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    rep = grade(a.run_root)
    txt = json.dumps(rep, indent=2, sort_keys=True, default=str)
    if a.out:
        with open(a.out, 'w') as f:
            f.write(txt)
    print(txt)


if __name__ == '__main__':
    main()
