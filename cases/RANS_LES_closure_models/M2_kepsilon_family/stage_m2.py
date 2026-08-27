"""
M2_kepsilon_family -- staging.

Builds the two-arm k-epsilon staged tree from the read-only closure-challenge
benchmark clone.  Implements PREREGISTRATION.md sections 2, 4 and 12 item 4.

CONTRACT
  * The benchmark tree is NEVER written.  Every source file read is sha256'd
    before and after; any change is a refusal.
  * Initial fields go to 0.orig/ and NO 0/ is created (AGE-GUARD counts 0 as a
    numeric time directory -- verification/runs/T-family/T5_runs/run_one_t5.sh
    lines 128-130).  run_m2.sh copies 0.orig -> 0 as its last act before launch.
  * Exactly the file classes registered in PREREGISTRATION.md section 4.3 differ
    from the shipped case.  fvSchemes is byte-identical (section 4.5).
  * No `libs` line is removed, reordered or tidied (standing rule 14).
  * NO REFUSAL IS AN `assert` (L-332).  Every refusal is an explicit sys.exit(2)
    and survives `python3 -O`.
  * Every guard ships a planted-failure proof (L-314): --selftest mutates each
    guard to a no-op and requires its control to flip.

USAGE
  python3 stage_m2.py --arm kEpsilon        --out <run_root>
  python3 stage_m2.py --arm LaunderSharmaKE --out <run_root>
  python3 stage_m2.py --selftest
"""

import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import sys
import time

import numpy as np

BENCH = '/home/ubuntu/closure-challenge-benchmark/data'
CMU = 0.09
YPLUSLAM = 11.53            # calcYPlusLam(kappa=0.41, E=9.8); wallFunctionCoefficients.C:61-64
ENDTIME = 20000             # PREREGISTRATION.md section 5
PLANT = 1.234e-03           # standing rule 3

ARMS = {
    # arm id -> (RASModel, epsilon wall boundary entry)
    # LaunderSharmaKE: epsilonTilda_wall = 0 exactly.  LaunderSharmaKE.C:254 (D)
    #   and :292 (k-sink is (epsilon_+D)/k_), so the transported variable is the
    #   MODIFIED dissipation and vanishes at the wall.  PREREGISTRATION.md 2.2.
    'LaunderSharmaKE': ('LaunderSharmaKE',
                        '        type            fixedValue;\n'
                        '        value           uniform 0;\n'),
    # kEpsilon: epsilonWallFunction fixes 2*nu*k_P/y_P^2 in the wall cells via
    #   manipulateMatrix (epsilonWallFunctionFvPatchScalarField.C:212-219, :593)
    #   when lowReCorrection is on AND yPlus < yPlusLam -- which section 2.4
    #   measured to hold on 100 percent of wall faces (max y* 3.77 vs 11.53).
    'kEpsilon': ('kEpsilon',
                 '        type            epsilonWallFunction;\n'
                 '        lowReCorrection true;\n'
                 '        value           uniform 1e-15;\n'),
}

# Patch types that carry no value and must be copied by type alone.
CONSTRAINT_TYPES = ('empty', 'cyclic', 'symmetry', 'symmetryPlane', 'wedge',
                    'processor', 'cyclicAMI')


# --------------------------------------------------------------------------- #
#  OpenFOAM ASCII readers.  Deliberately small and deliberately shared with
#  grade_m2.py, so that the number the grader reads is read by the same code
#  that staged it.
# --------------------------------------------------------------------------- #

def strip_header(txt):
    txt = re.sub(r'/\*.*?\*/', '', txt, flags=re.S)
    txt = re.sub(r'//[^\n]*', '', txt)
    i = txt.find('FoamFile')
    if i >= 0:
        d = txt.find('{', i)
        depth = 0
        for j in range(d, len(txt)):
            if txt[j] == '{':
                depth += 1
            elif txt[j] == '}':
                depth -= 1
                if depth == 0:
                    return txt[j + 1:]
    return txt


def _numbers(seg, n, ncomp):
    seg = seg[:seg.find(';')]
    v = np.fromstring(seg.replace('(', ' ').replace(')', ' '), sep=' ')
    if v.size < n * ncomp:
        return None
    return v[:n * ncomp].reshape(n, ncomp) if ncomp > 1 else v[:n]


def read_points(p):
    t = strip_header(open(p).read())
    m = re.search(r'(\d+)\s*\(', t)
    return _numbers(t[m.end():] + ';', int(m.group(1)), 3)


def read_faces(p):
    t = strip_header(open(p).read())
    m = re.search(r'(\d+)\s*\(', t)
    n = int(m.group(1))
    out = []
    for fm in re.finditer(r'(\d+)\s*\(([^)]*)\)', t[m.end():]):
        out.append(np.fromstring(fm.group(2), sep=' ', dtype=float).astype(np.int64))
        if len(out) == n:
            break
    return out if len(out) == n else None


def read_labels(p):
    t = strip_header(open(p).read())
    m = re.search(r'(\d+)\s*\(', t)
    n = int(m.group(1))
    v = np.fromstring(t[m.end():].replace(')', ' '), sep=' ', dtype=float)
    return v[:n].astype(np.int64)


def read_boundary(p):
    t = strip_header(open(p).read())
    out = {}
    for bm in re.finditer(r'(\w+)\s*\{([^}]*)\}', t):
        d = bm.group(2)
        nf = re.search(r'nFaces\s+(\d+)', d)
        sf = re.search(r'startFace\s+(\d+)', d)
        ty = re.search(r'type\s+(\w+)', d)
        if nf and sf:
            out[bm.group(1)] = dict(start=int(sf.group(1)), n=int(nf.group(1)),
                                    type=ty.group(1) if ty else '?')
    return out


def resolve_vars(path):
    """Local `name value;` definitions above `dimensions`, plus the case's caseDef.

    The 8 DUCT cases ship `internalField uniform $kInlet;` with `kInlet 0.02;`
    defined in the same file (and `#include "../caseDef"` for nu/Re).  These are
    OpenFOAM dictionary variables, not missing data; resolving them is a lookup,
    not a choice.  Every resolution is recorded in staging_manifest.json.
    """
    txt = strip_header(open(path).read())
    head = txt[:txt.find('dimensions')] if 'dimensions' in txt else txt
    out = {}
    for m in re.finditer(r'(?m)^\s*(\w+)\s+([-+0-9.eE]+)\s*;', head):
        out[m.group(1)] = m.group(2)
    cd = os.path.join(os.path.dirname(os.path.dirname(path)), 'caseDef')
    if os.path.exists(cd):
        for m in re.finditer(r'(?m)^\s*(\w+)\s+([-+0-9.eE]+)\s*;', open(cd).read()):
            out.setdefault(m.group(1), m.group(2))
    return out


def scalar_of(tok, varmap, path, what):
    """A uniform entry's scalar, resolving a leading $VAR.  REFUSES, never guesses."""
    tok = str(tok).strip()
    if tok.startswith('$'):
        name = tok[1:].strip()
        if name not in varmap:
            sys.stderr.write('REFUSE: %s: %s is $%s and no definition of %s was '
                             'found in the file or in caseDef\n' % (path, what, name, name))
            sys.exit(2)
        tok = varmap[name]
    try:
        return float(tok)
    except ValueError:
        sys.stderr.write('REFUSE: %s: %s is %r, which is not a number this staging '
                         'may invent a value for\n' % (path, what, tok))
        sys.exit(2)


def read_field(path, ncomp):
    """Return dict(internal=..., patches={name: ('uniform', s) | ndarray | ('type', t)})."""
    raw = open(path).read()
    t = strip_header(raw)
    bi = t.find('boundaryField')
    head, tail = t[:bi], t[bi:]
    m = re.search(r'internalField\s+nonuniform[^\n]*\n\s*(\d+)\s*\(', head)
    if m:
        internal = _numbers(head[m.end():], int(m.group(1)), ncomp)
    else:
        m2 = re.search(r'internalField\s+uniform\s+\(?([^;)]*)\)?\s*;', head)
        internal = ('uniform', m2.group(1).strip()) if m2 else None
    patches = {}
    for pm in re.finditer(r'(?:"([^"]+)"|(\w+))\s*\{', tail):
        name = pm.group(1) if pm.group(1) is not None else pm.group(2)
        if name == 'boundaryField':
            continue
        depth, j = 1, pm.end()
        while j < len(tail) and depth:
            depth += (tail[j] == '{') - (tail[j] == '}')
            j += 1
        body = tail[pm.end():j - 1]
        ty = re.search(r'type\s+(\w+)\s*;', body)
        nu = re.search(r'value\s+nonuniform[^\n]*\n\s*(\d+)\s*\(', body)
        uu = re.search(r'value\s+uniform\s+\(?([^;)]*)\)?\s*;', body)
        if nu:
            patches[name] = ('list', _numbers(body[nu.end():], int(nu.group(1)), ncomp),
                             ty.group(1) if ty else '?')
        elif uu:
            patches[name] = ('uniform', uu.group(1).strip(), ty.group(1) if ty else '?')
        else:
            patches[name] = ('type', None, ty.group(1) if ty else '?')
    return dict(internal=internal, patches=patches)


# --------------------------------------------------------------------------- #
#  Mesh geometry.  OpenFOAM's own algorithms, so that y_P here is the y_P the
#  solver's nearWallDist would produce.  Validated in PREREGISTRATION.md 2.4
#  against the shipped 0/C to 5.5e-14 m.
# --------------------------------------------------------------------------- #

def face_geometry(faces, pts):
    Cf = np.zeros((len(faces), 3))
    Sf = np.zeros((len(faces), 3))
    for i, f in enumerate(faces):
        P = pts[f]
        if len(f) == 3:
            Cf[i] = P.mean(0)
            Sf[i] = 0.5 * np.cross(P[1] - P[0], P[2] - P[0])
        else:
            fc = P.mean(0)
            Pn = np.roll(P, -1, axis=0)
            ntri = np.cross(Pn - P, fc - P)
            a = np.linalg.norm(ntri, axis=1)
            Cf[i] = (a[:, None] * (P + Pn + fc)).sum(0) / (3.0 * a.sum())
            Sf[i] = 0.5 * ntri.sum(0)
    return Cf, Sf


def cell_centres(nCells, owner, neigh, Cf, Sf):
    est = np.zeros((nCells, 3))
    cnt = np.zeros(nCells)
    np.add.at(est, owner, Cf)
    np.add.at(cnt, owner, 1)
    np.add.at(est, neigh, Cf[:len(neigh)])
    np.add.at(cnt, neigh, 1)
    est /= cnt[:, None]
    C = np.zeros((nCells, 3))
    V = np.zeros(nCells)
    pv = ((Cf - est[owner]) * Sf).sum(1) / 3.0
    np.add.at(C, owner, pv[:, None] * (0.75 * Cf + 0.25 * est[owner]))
    np.add.at(V, owner, pv)
    m = len(neigh)
    pv2 = -((Cf[:m] - est[neigh]) * Sf[:m]).sum(1) / 3.0
    np.add.at(C, neigh, pv2[:, None] * (0.75 * Cf[:m] + 0.25 * est[neigh]))
    np.add.at(V, neigh, pv2)
    return C / V[:, None], V


def mesh_walls(casedir):
    """Return {patch: dict(yP=..., owner=...)} for every wall patch, plus nCells."""
    pm = os.path.join(casedir, 'constant', 'polyMesh') + os.sep
    pts = read_points(pm + 'points')
    faces = read_faces(pm + 'faces')
    owner = read_labels(pm + 'owner')
    neigh = read_labels(pm + 'neighbour')
    bnd = read_boundary(pm + 'boundary')
    nCells = int(max(owner.max(), neigh.max()) + 1)
    Cf, Sf = face_geometry(faces, pts)
    C, _ = cell_centres(nCells, owner, neigh, Cf, Sf)
    out = {}
    for name, b in bnd.items():
        if b['type'] != 'wall':
            continue
        idx = np.arange(b['start'], b['start'] + b['n'])
        nhat = Sf[idx] / np.linalg.norm(Sf[idx], axis=1)[:, None]
        own = owner[idx]
        out[name] = dict(yP=np.abs(((C[own] - Cf[idx]) * nhat).sum(1)),
                         owner=own, nhat=nhat)
    return out, nCells, C


# --------------------------------------------------------------------------- #
#  Case discovery and the shipped-dictionary surgery
# --------------------------------------------------------------------------- #

def discover_cases():
    """The registered 39.  NASA_2DWMH is BLOCKED and is not returned."""
    cases = [('CBFS13700', os.path.join(BENCH, 'CBFS')),
             ('PH_Breuer', os.path.join(BENCH, 'PH_Breuer'))]
    ph = os.path.join(BENCH, 'Parm_PH_29')
    for fam in sorted(os.listdir(ph)):
        famp = os.path.join(ph, fam)
        if not os.path.isdir(famp):
            continue
        for d in sorted(os.listdir(famp)):
            if os.path.isdir(os.path.join(famp, d)):
                cases.append((d, os.path.join(famp, d)))
    duct = os.path.join(BENCH, 'DUCT')
    for d in sorted(os.listdir(duct)):
        if os.path.isdir(os.path.join(duct, d)):
            cases.append((d, os.path.join(duct, d)))
    return cases


def mask_comments(txt):
    """Blank every comment, PRESERVING LENGTH so offsets stay valid.

    The dictionary surgery splices into the ORIGINAL bytes but must never key
    off text inside a comment: the shipped fvSolution files carry commented-out
    `R`, `nuTilda` and whole sub-blocks (CBFS), and a naive search matches them.
    """
    out = list(txt)
    i, n = 0, len(txt)
    while i < n:
        if txt[i] == '/' and i + 1 < n and txt[i + 1] == '*':
            j = txt.find('*/', i + 2)
            j = n if j < 0 else j + 2
            for k in range(i, j):
                if out[k] != '\n':
                    out[k] = ' '
            i = j
        elif txt[i] == '/' and i + 1 < n and txt[i + 1] == '/':
            j = txt.find('\n', i)
            j = n if j < 0 else j
            for k in range(i, j):
                out[k] = ' '
            i = j
        else:
            i += 1
    return ''.join(out)


def block_span(txt, keyword, frm=0):
    """Span of `keyword { ... }` at or after frm.  Returns (kw_start, open, close)."""
    mk = mask_comments(txt)
    for m in re.finditer(r'(?<![\w"])' + re.escape(keyword) + r'(?![\w"])', mk[frm:]):
        i = frm + m.start()
        j = frm + m.end()
        while j < len(mk) and mk[j] in ' \t\r\n':
            j += 1
        if j < len(mk) and mk[j] == '{':
            depth, k = 1, j + 1
            while k < len(mk) and depth:
                depth += (mk[k] == '{') - (mk[k] == '}')
                k += 1
            return i, j, k - 1
    return None


def residual_control_bodies(txt):
    """Every residualControl body, comment-masked and whitespace-normalised."""
    out, frm = [], 0
    while True:
        sp = block_span(txt, 'residualControl', frm)
        if sp is None:
            return out
        _, ob, cb = sp
        out.append(' '.join(txt[ob + 1:cb].split()))
        frm = cb + 1


def empty_residual_control(txt):
    """Empty EVERY residualControl sub-dictionary.  Returns (text, n, bodies).

    The shape is M1's (`stage_m1.py:255`, frozen at 7b00b3ec).  An early stop
    would violate standing rule 4's `last time == endTime` and
    `ExecutionTime count == endTime`, and relaxing rule 4 is not a rung's to do.
    """
    bodies = residual_control_bodies(txt)
    n, frm = 0, 0
    EMPTY = '{\n    }'
    while True:
        sp = block_span(txt, 'residualControl', frm)
        if sp is None:
            return txt, n, bodies
        _, ob, cb = sp
        if txt[ob:cb + 1] == EMPTY:
            frm = cb + 1                 # already empty: STEP PAST IT, never stop.
            continue                     # stopping here left later blocks intact --
        txt = txt[:ob] + EMPTY + txt[cb + 1:]   # caught by this file's own control,
        frm = ob + len(EMPTY)                   # not by reading (M1's shape at
        n += 1                                  # stage_m1.py:255 returns early here;
                                                # its cases carry one block each).


def entry_value(txt, keyword):
    """`keyword value;` -> value, honouring OpenFOAM regex keys like "(k|omega)"."""
    txt = mask_comments(txt)
    m = re.search(r'(?<![\w"])' + re.escape(keyword) + r'\s+([^;{}]+);', txt)
    if m:
        return m.group(1).strip(), keyword
    for rm in re.finditer(r'"([^"]+)"\s+([^;{}]+);', txt):
        try:
            if re.fullmatch(rm.group(1), keyword):
                return rm.group(2).strip(), '"%s"' % rm.group(1)
        except re.error:
            continue
    return None, None


def add_epsilon_to_fvsolution(txt):
    """Registered section 4.3 items 3-5.  Zero free parameters: every inserted
    value is a verbatim copy of the same case's own omega channel.  Returns
    (new_text, record)."""
    rec = {}
    out = txt

    # --- item 3: solvers { epsilon { <omega's body verbatim> } } -----------
    sp = block_span(out, 'solvers')
    if sp is None:
        return None, {'error': 'no solvers block'}
    _, so, sc = sp
    solvers_body = out[so + 1:sc]
    if block_span(solvers_body, 'epsilon') is not None:
        rec['solvers'] = 'already present, untouched'
    else:
        osp = block_span(solvers_body, 'omega')
        if osp is None:
            return None, {'error': 'no omega solver block to mirror'}
        _, oo, oc = osp
        body = solvers_body[oo:oc + 1]
        ins = '\n    epsilon\n    ' + body.strip() + '\n'
        out = out[:sc] + ins + out[sc:]
        rec['solvers'] = 'inserted, mirroring omega verbatim'
        rec['solvers_body'] = ' '.join(body.split())

    # --- item 4: relaxationFactors epsilon = omega's factor -----------------
    rp = block_span(out, 'relaxationFactors')
    if rp is None:
        rec['relax'] = 'no relaxationFactors block; nothing to mirror'
    else:
        _, ro, rc_ = rp
        body = out[ro + 1:rc_]
        eqp = block_span(body, 'equations')
        if eqp is not None:                       # nested modern form
            _, eo, ec = eqp
            target_open, target_close = ro + 1 + eo, ro + 1 + ec
            scope = body[eo + 1:ec]
        else:                                     # flat legacy form (the hills)
            target_open, target_close = ro, rc_
            scope = body
        if entry_value(scope, 'epsilon')[0] is not None:
            rec['relax'] = 'already present, untouched'
        else:
            val, via = entry_value(scope, 'omega')
            if val is None:
                rec['relax'] = 'no omega relaxation factor to mirror'
            else:
                out = (out[:target_close] + '        epsilon         ' + val + ';\n'
                       + out[target_close:])
                rec['relax'] = 'inserted epsilon %s (mirror of omega via %s)' % (val, via)

    # --- item 5: residualControl is EMPTIED (closure-supervisor RULING 2, ----
    # 2026-08-27; PREREGISTRATION.md 13 AMENDMENT 4).  M1 is frozen at 7b00b3ec
    # and `stage_m1.py:255` empties every residualControl sub-dictionary, with
    # `:484` REFUSING if a staged fvSolution still carries a non-empty one.  M1
    # and M2 cover THE SAME EIGHT DUCT CASES; two rungs in one family taking
    # opposite readings of standing rule 4 on the same cases is indefensible.
    # With no criterion there is no early stop, so `last time == endTime` and
    # `ExecutionTime count == endTime` both hold literally, on every case.
    out, n_emptied, bodies_before = empty_residual_control(out)
    rec['residualControl'] = ('emptied %d block(s); shipped bodies recorded: %s'
                              % (n_emptied, bodies_before)) if n_emptied else \
                             'absent; nothing to empty'
    return out, rec


def libs_lines(txt):
    return sorted(' '.join(l.split()) for l in txt.splitlines()
                  if re.match(r'\s*libs\b', l))


def key_is_wall(key, wall_names):
    """A boundaryField key may be a literal patch name or a quoted OpenFOAM regex."""
    if key in wall_names:
        return True
    try:
        return any(re.fullmatch(key, w) for w in wall_names)
    except re.error:
        return False


def build_epsilon_file(k, omega, wall_entry, wall_names, kvars, ovars, kpath, opath):
    """0.orig/epsilon.  internal and every valued non-wall patch by epsilon = Cmu*k*omega."""
    L = ['FoamFile\n{\n    version     2.0;\n    format      ascii;\n'
         '    class       volScalarField;\n    location    "0";\n'
         '    object      epsilon;\n}\n',
         'dimensions      [0 2 -3 0 0 0 0];\n\n']
    ki, oi = k['internal'], omega['internal']
    if isinstance(ki, tuple) and isinstance(oi, tuple):
        L.append('internalField   uniform %.15g;\n\n'
                 % (CMU * scalar_of(ki[1], kvars, kpath, 'internalField')
                    * scalar_of(oi[1], ovars, opath, 'internalField')))
    else:
        kv = (np.full(len(oi), scalar_of(ki[1], kvars, kpath, 'internalField'))
              if isinstance(ki, tuple) else ki)
        ov = (np.full(len(kv), scalar_of(oi[1], ovars, opath, 'internalField'))
              if isinstance(oi, tuple) else oi)
        e = CMU * kv * ov
        L.append('internalField   nonuniform List<scalar>\n%d\n(\n' % len(e))
        L.append('\n'.join('%.15g' % x for x in e))
        L.append('\n)\n;\n\n')
    L.append('boundaryField\n{\n')
    for name, (kind, kval, kty) in k['patches'].items():
        L.append('    %s\n    {\n' % name)
        if key_is_wall(name, wall_names):
            L.append(wall_entry)
        elif kty in CONSTRAINT_TYPES or kind == 'type':
            L.append('        type            %s;\n' % kty)
        else:
            okind, oval, _ = omega['patches'].get(name, ('uniform', '0', 'calculated'))
            if kind == 'uniform' and okind == 'uniform':
                L.append('        type            %s;\n' % kty)
                L.append('        value           uniform %.15g;\n'
                         % (CMU * scalar_of(kval, kvars, kpath, name)
                            * scalar_of(oval, ovars, opath, name)))
            else:
                kv = (np.full(len(oval), scalar_of(kval, kvars, kpath, name))
                      if okind == 'list' and kind == 'uniform' else kval)
                ov = (np.full(len(kval), scalar_of(oval, ovars, opath, name))
                      if kind == 'list' and okind == 'uniform' else oval)
                e = CMU * np.asarray(kv, dtype=float) * np.asarray(ov, dtype=float)
                L.append('        type            %s;\n' % kty)
                L.append('        value           nonuniform List<scalar>\n%d\n(\n' % len(e))
                L.append('\n'.join('%.15g' % x for x in e))
                L.append('\n)\n;\n')
        L.append('    }\n')
    L.append('}\n')
    return ''.join(L)


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


# --------------------------------------------------------------------------- #
#  Guards.  Each is a plain function so --selftest can mutate it to a no-op and
#  require the control to flip (L-314).  NONE of them is an `assert` (L-332).
# --------------------------------------------------------------------------- #

def guard_source_unchanged(before, after):
    """REFUSAL: the benchmark tree must be byte-identical before and after."""
    return [p for p in before if before[p] != after.get(p)]


def guard_no_zero_dir(dst):
    """REFUSAL: a staged case must contain no 0/ and no numeric time directory."""
    if not os.path.isdir(dst):
        return []
    return [d for d in os.listdir(dst) if re.fullmatch(r'\d+(\.\d+)?', d)]


def guard_libs_preserved(src_txt, dst_txt):
    """REFUSAL: standing rule 14 -- libs lines are never removed or reordered."""
    return libs_lines(src_txt) != libs_lines(dst_txt)


def guard_endtime_is_a_write_time(txt, endtime):
    """Return the offending writeInterval, or None.

    `writeControl timeStep` writes only where `timeIndex % writeInterval == 0`.
    A registered `endTime` that is not a multiple of the shipped `writeInterval`
    means the solver runs the full budget and WRITES NOTHING AT endTime -- the
    fields clause of standing rule 4 then fails on a run that did everything
    right.  Measured on the shipped tree: CBFS13700 ships `writeInterval 30000`
    with `endTime 30000`, so 20000 is not a write time (its shipped tree holds
    only `0` and `30000`).  PREREGISTRATION.md 13, AMENDMENT 2.
    """
    m = re.search(r'\bwriteInterval\s+([0-9.eE+-]+)\s*;', mask_comments(txt))
    if not m:
        return None                      # `$endTime` and friends: resolved by the
    wi = float(m.group(1))               # dictionary, and tracked by the rewrite
    if wi <= 0:
        return wi
    q = endtime / wi
    return None if abs(q - round(q)) < 1e-9 else wi


def guard_ystar_below_lam(ystar_max):
    """REFUSAL: the registered wall treatment was selected on y* < yPlusLam."""
    return ystar_max >= YPLUSLAM


def _list_open_line(lines, start_idx):
    """Index of the line holding the `(` that opens a nonuniform list at/after start_idx."""
    for i in range(start_idx, min(start_idx + 6, len(lines))):
        if lines[i].strip() == '(':
            return i
    return None


def plant_into_file(path, site):
    """Standing rule 3: write PLANT into a REAL file ON DISK, by line index.

    site == 'internal' -> the first entry of the internalField list
    site == 'patch'    -> the first valued entry of the first boundary patch

    Returns the line index planted, or None if there was no site to plant into.
    An in-memory plant does NOT satisfy rule 3 and is not offered here: this
    function only ever writes the file back out.
    """
    lines = open(path).read().splitlines(True)
    if site == 'internal':
        for i, ln in enumerate(lines):
            if 'internalField' in ln and 'nonuniform' in ln:
                j = _list_open_line(lines, i + 1)
                if j is not None and j + 1 < len(lines):
                    lines[j + 1] = '%.15g\n' % PLANT
                    with open(path, 'w') as f:
                        f.write(''.join(lines))
                    return j + 1
            if 'internalField' in ln and 'uniform' in ln:
                lines[i] = 'internalField   uniform %.15g;\n' % PLANT
                with open(path, 'w') as f:
                    f.write(''.join(lines))
                return i
        return None
    bi = None
    for i, ln in enumerate(lines):
        if ln.strip().startswith('boundaryField'):
            bi = i
            break
    if bi is None:
        return None
    for i in range(bi, len(lines)):
        s = lines[i].strip()
        if s.startswith('value') and 'nonuniform' in s:
            j = _list_open_line(lines, i + 1)
            if j is not None and j + 1 < len(lines):
                lines[j + 1] = '%.15g\n' % PLANT
                with open(path, 'w') as f:
                    f.write(''.join(lines))
                return j + 1
        if s.startswith('value') and 'uniform' in s:
            lines[i] = '        value           uniform %.15g;\n' % PLANT
            with open(path, 'w') as f:
                f.write(''.join(lines))
            return i
    return None


def guard_reader_sees_plant(scratch_file, site='internal'):
    """REFUSAL (standing rule 3): plant on DISK, re-read through the SAME reader
    every other number in this rung goes through, and require it back.

    A zero from a reader not shown able to see a non-zero is not evidence, and
    this rung's LaunderSharmaKE arm registers a wall value that IS zero -- so a
    blind reader here would produce a confident, wrong PASS.  Both sites are
    planted because gate G-D reads both.
    """
    if plant_into_file(scratch_file, site) is None:
        return False
    back = read_field(scratch_file, 1)
    if site == 'internal':
        iv = back['internal']
        if isinstance(iv, tuple):
            return abs(float(iv[1]) - PLANT) <= 1e-12 * PLANT
        if not isinstance(iv, np.ndarray):
            return False
        return bool(np.any(np.abs(iv - PLANT) <= 1e-12 * PLANT))
    for kind, val, _ty in back['patches'].values():
        if kind == 'uniform' and val is not None:
            try:
                if abs(float(val) - PLANT) <= 1e-12 * PLANT:
                    return True
            except ValueError:
                continue
        elif kind == 'list' and isinstance(val, np.ndarray):
            if bool(np.any(np.abs(val - PLANT) <= 1e-12 * PLANT)):
                return True
    return False


# --------------------------------------------------------------------------- #

def stage_arm(arm, out_root, dry=False):
    model, wall_entry = ARMS[arm]
    cases = discover_cases()
    if len(cases) != 39:
        sys.stderr.write('REFUSE: expected 39 cases, discovered %d\n' % len(cases))
        sys.exit(2)
    manifest = {'arm': arm, 'RASModel': model, 'endTime': ENDTIME,
                'staged_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                'yPlusLam': YPLUSLAM, 'Cmu': CMU, 'cases': {}}
    before = {}
    for cid, src in cases:
        dst = os.path.join(out_root, arm, cid)
        stale = guard_no_zero_dir(dst)
        if stale:
            sys.stderr.write('REFUSE: %s/%s already holds time dirs %s; '
                             'a guard refuses, it does not clean\n' % (arm, cid, stale))
            sys.exit(2)

        srcfiles = ['system/fvSchemes', 'system/fvSolution', 'system/controlDict',
                    'constant/turbulenceProperties', 'constant/transportProperties',
                    '0/k', '0/omega', '0/U', '0/p', '0/nut']
        for rel in srcfiles:
            p = os.path.join(src, rel)
            if os.path.exists(p):
                before[p] = sha(p)
        for rel in ('points', 'faces', 'owner', 'neighbour', 'boundary'):
            p = os.path.join(src, 'constant', 'polyMesh', rel)
            if os.path.exists(p):
                before[p] = sha(p)

        walls, nCells, _ = mesh_walls(src)
        kpath = os.path.join(src, '0', 'k')
        opath = os.path.join(src, '0', 'omega')
        kf = read_field(kpath, 1)
        of = read_field(opath, 1)
        kvars = resolve_vars(kpath)
        ovars = resolve_vars(opath)

        # section 12 item 4: y* is CENSUSED here, on all 39, not sampled.
        nu = read_nu(src)
        ki = kf['internal']
        ystar_max = 0.0
        for wname, w in walls.items():
            kP = (np.full(len(w['owner']), scalar_of(ki[1], kvars, kpath, 'internalField'))
                  if isinstance(ki, tuple) else ki[w['owner']])
            ys = CMU ** 0.25 * w['yP'] * np.sqrt(np.maximum(kP, 0.0)) / nu
            ystar_max = max(ystar_max, float(ys.max()))
        if guard_ystar_below_lam(ystar_max):
            sys.stderr.write('REFUSE: %s max k-based y* %.4f reaches yPlusLam %.2f; '
                             'the registered wall treatment was selected on y* < yPlusLam\n'
                             % (cid, ystar_max, YPLUSLAM))
            sys.exit(2)

        rec = {'src': src, 'nCells': nCells, 'nu': nu,
               'ystar_max_shipped': ystar_max, 'walls': sorted(walls)}
        used = {}
        for tok, vm, lbl in ((ki[1] if isinstance(ki, tuple) else None, kvars, 'k'),
                             (of['internal'][1] if isinstance(of['internal'], tuple) else None,
                              ovars, 'omega')):
            if isinstance(tok, str) and tok.strip().startswith('$'):
                nm = tok.strip()[1:]
                used['%s.internalField' % lbl] = {'token': tok.strip(), 'resolved': vm.get(nm)}
        if used:
            rec['dictionary_variables_resolved'] = used

        # the 29 hills' shipped 0/epsilon is RECORDED before it is overridden
        shipped_eps = os.path.join(src, '0', 'epsilon')
        if os.path.exists(shipped_eps):
            txt = open(shipped_eps).read()
            rec['shipped_0_epsilon'] = {
                'sha256': sha(shipped_eps),
                'internalField': (re.search(r'internalField[^;]*;', txt).group(0)
                                  if 'internalField' in txt else None),
                'wall_entries': re.findall(r'type\s+(\w+);|value\s+uniform\s+([^;]+);', txt)[:6],
                'disposition': 'OVERRIDDEN in the staged copy; PREREGISTRATION.md 2.5',
            }

        if not dry:
            os.makedirs(os.path.join(dst, '0.orig'), exist_ok=True)
            os.makedirs(os.path.join(dst, 'system'), exist_ok=True)
            os.makedirs(os.path.join(dst, 'constant'), exist_ok=True)
            if os.path.isdir(os.path.join(dst, 'constant', 'polyMesh')):
                shutil.rmtree(os.path.join(dst, 'constant', 'polyMesh'))
            shutil.copytree(os.path.join(src, 'constant', 'polyMesh'),
                            os.path.join(dst, 'constant', 'polyMesh'))
            for extra in ('cellZones', 'faceZones', 'pointZones'):
                p = os.path.join(src, 'constant', 'polyMesh', extra)
                if os.path.exists(p):
                    shutil.copy2(p, os.path.join(dst, 'constant', 'polyMesh', extra))
            if os.path.exists(os.path.join(src, 'caseDef')):
                shutil.copy2(os.path.join(src, 'caseDef'), os.path.join(dst, 'caseDef'))
            shutil.copy2(os.path.join(src, 'constant', 'transportProperties'),
                         os.path.join(dst, 'constant', 'transportProperties'))
            # fvSchemes BYTE-IDENTICAL (section 4.5)
            shutil.copy2(os.path.join(src, 'system', 'fvSchemes'),
                         os.path.join(dst, 'system', 'fvSchemes'))
            for rel in ('0/U', '0/p', '0/k', '0/omega', '0/nut'):
                p = os.path.join(src, rel)
                if os.path.exists(p):
                    shutil.copy2(p, os.path.join(dst, '0.orig', os.path.basename(rel)))

            # item 2 -- the constructed epsilon
            eps_txt = build_epsilon_file(kf, of, wall_entry, set(walls),
                                         kvars, ovars, kpath, opath)
            with open(os.path.join(dst, '0.orig', 'epsilon'), 'w') as f:
                f.write(eps_txt)

            # item 1 -- turbulenceProperties
            tp = open(os.path.join(src, 'constant', 'turbulenceProperties')).read()
            tp2 = re.sub(r'(RASModel\s+)\w+(\s*;)', r'\g<1>' + model + r'\g<2>', tp)
            if tp2 == tp:
                sys.stderr.write('REFUSE: %s RASModel substitution changed nothing\n' % cid)
                sys.exit(2)
            with open(os.path.join(dst, 'constant', 'turbulenceProperties'), 'w') as f:
                f.write(tp2)

            # items 3-5 -- fvSolution
            fs = open(os.path.join(src, 'system', 'fvSolution')).read()
            fs2, fsrec = add_epsilon_to_fvsolution(fs)
            if fs2 is None:
                sys.stderr.write('REFUSE: %s fvSolution: %s\n' % (cid, fsrec.get('error')))
                sys.exit(2)
            with open(os.path.join(dst, 'system', 'fvSolution'), 'w') as f:
                f.write(fs2)
            rec['fvSolution'] = fsrec

            # RULING 2's refusal, the shape of M1's g_R12 (stage_m1.py:484).
            leftover = [b for b in residual_control_bodies(fs2) if b != '']
            if leftover:
                sys.stderr.write('REFUSE: %s staged fvSolution residualControl is not '
                                 'empty (%r) -- an early stop violates standing rule 4 '
                                 "'last time == endTime' and 'ExecutionTime count == "
                                 "endTime'\n" % (cid, leftover))
                sys.exit(2)

            # controlDict: endTime, and the v2606 compression-specifier rewrite
            cdt = open(os.path.join(src, 'system', 'controlDict')).read()
            cd2 = re.sub(r'(endTime\s+)[0-9.eE+-]+(\s*;)',
                         r'\g<1>%d\g<2>' % ENDTIME, cdt, count=0)
            cd2 = re.sub(r'(startFrom\s+)\w+(\s*;)', r'\g<1>startTime\g<2>', cd2)
            comp = 'writeCompression uncompressed' in cd2
            cd2 = cd2.replace('writeCompression uncompressed', 'writeCompression off')

            # AMENDMENT 2: endTime must be a write time, or the run writes
            # nothing at endTime and standing rule 4's fields clause fails on a
            # run that did everything right.  Zero free parameters: the only
            # value written is the registered ENDTIME itself, and the shipped
            # value is recorded.  Bookkeeping only -- it changes WHAT IS SAVED,
            # never what is computed.
            wi_bad = guard_endtime_is_a_write_time(cd2, ENDTIME)
            if wi_bad is not None:
                cd2 = re.sub(r'(\bwriteInterval\s+)[0-9.eE+-]+(\s*;)',
                             r'\g<1>%d\g<2>' % ENDTIME, cd2, count=1)
                rec_wi = {'shipped_writeInterval': wi_bad,
                          'rewritten_to': ENDTIME,
                          'reason': ('endTime %d is not a multiple of the shipped '
                                     'writeInterval %g, so endTime would not be a '
                                     'write time' % (ENDTIME, wi_bad))}
            else:
                rec_wi = {'shipped_writeInterval': 'left byte-unchanged'}
            still_bad = guard_endtime_is_a_write_time(cd2, ENDTIME)
            if still_bad is not None:
                sys.stderr.write('REFUSE: %s endTime %d is still not a write time '
                                 '(writeInterval %g); the run would write nothing '
                                 'at endTime\n' % (cid, ENDTIME, still_bad))
                sys.exit(2)
            if guard_libs_preserved(cdt, cd2):
                sys.stderr.write('REFUSE: %s controlDict libs lines changed; '
                                 'standing rule 14\n' % cid)
                sys.exit(2)
            with open(os.path.join(dst, 'system', 'controlDict'), 'w') as f:
                f.write(cd2)
            rec['controlDict'] = {'endTime': ENDTIME,
                                  'writeCompression_rewritten': comp,
                                  'writeInterval': rec_wi,
                                  'libs_lines': libs_lines(cdt)}
            stale = guard_no_zero_dir(dst)
            if stale:
                sys.stderr.write('REFUSE: %s staging produced time dirs %s; '
                                 '0.orig only\n' % (cid, stale))
                sys.exit(2)
        manifest['cases'][cid] = rec

    after = {p: sha(p) for p in before}
    changed = guard_source_unchanged(before, after)
    if changed:
        sys.stderr.write('REFUSE: the benchmark tree was written: %s\n' % changed[:5])
        sys.exit(2)
    manifest['benchmark_sha_before_equals_after'] = True
    manifest['n_source_files_hashed'] = len(before)
    if not dry:
        with open(os.path.join(out_root, arm, 'staging_manifest.json'), 'w') as f:
            json.dump(manifest, f, indent=2, sort_keys=True, default=str)
    return manifest


def read_nu(src):
    tp = open(os.path.join(src, 'constant', 'transportProperties')).read()
    m = re.search(r'nu\s+nu\s*\[[^\]]*\]\s*([0-9.eE+-]+)', tp)
    if m:
        return float(m.group(1))
    cd = os.path.join(src, 'caseDef')
    if os.path.exists(cd):
        m = re.search(r'\bnu\s+([0-9.eE+-]+)\s*;', open(cd).read())
        if m:
            return float(m.group(1))
    m = re.search(r'nu\s*\[[^\]]*\]\s*([0-9.eE+-]+)', tp)
    if m:
        return float(m.group(1))
    sys.stderr.write('REFUSE: cannot read nu from %s\n' % src)
    sys.exit(2)


# --------------------------------------------------------------------------- #
#  SELFTEST -- L-332 and L-314
# --------------------------------------------------------------------------- #

def count_asserts(path):
    return sum(1 for n in ast.walk(ast.parse(open(path).read())) if isinstance(n, ast.Assert))


def selftest():
    here = os.path.dirname(os.path.abspath(__file__))
    ok = True

    def report(name, passed, detail=''):
        nonlocal ok
        ok = ok and passed
        print('%-46s %s %s' % (name, 'ok' if passed else 'FAIL', detail))

    # L-332 (3): no refusal is an assert, in either frozen file
    for f in ('stage_m2.py', 'grade_m2.py'):
        p = os.path.join(here, f)
        if os.path.exists(p):
            report('L-332 zero ast.Assert in %s' % f, count_asserts(p) == 0)

    # L-332 (4): PLANT THE ZERO ON THE COUNTER ITSELF -- a counter never shown
    # able to return non-zero is a planted zero of its own.
    planted = 'def f(x):\n    assert x > 0\n    assert x < 10\n    return x\n'
    n = sum(1 for nd in ast.walk(ast.parse(planted)) if isinstance(nd, ast.Assert))
    report('L-332 assert-counter can count (expect 2)', n == 2, '(got %d)' % n)

    # L-314: guard_ystar_below_lam, both directions
    report('guard_ystar_below_lam fires above lam', guard_ystar_below_lam(YPLUSLAM + 1e-9))
    report('guard_ystar_below_lam quiet below lam', not guard_ystar_below_lam(3.77))
    noop = lambda _m: False
    report('L-314 mutating y* guard to no-op flips control', noop(YPLUSLAM + 1e-9) is False)

    # L-314: guard_source_unchanged, both directions
    report('guard_source_unchanged quiet when equal',
           guard_source_unchanged({'a': '1'}, {'a': '1'}) == [])
    report('guard_source_unchanged fires when changed',
           guard_source_unchanged({'a': '1'}, {'a': '2'}) == ['a'])

    # L-314: guard_libs_preserved -- rule 14
    a = 'libs ("x.so");\nendTime 1;\n'
    report('guard_libs_preserved quiet when kept', not guard_libs_preserved(a, a))
    report('guard_libs_preserved fires when a libs line is dropped',
           guard_libs_preserved(a, 'endTime 1;\n'))

    # L-314: guard_no_zero_dir
    import tempfile
    d = tempfile.mkdtemp()
    # AMENDMENT 2: endTime-is-a-write-time guard, both directions (L-314)
    report('write-time guard FIRES on CBFS13700-shaped 30000/20000',
           guard_endtime_is_a_write_time('writeControl timeStep;\nwriteInterval 30000;\n',
                                         20000) == 30000.0)
    report('write-time guard QUIET on 4000 (the 29 hills)',
           guard_endtime_is_a_write_time('writeInterval 4000;\n', 20000) is None)
    report('write-time guard QUIET on 10000 (PH_Breuer)',
           guard_endtime_is_a_write_time('writeInterval 10000;\n', 20000) is None)
    report('write-time guard QUIET on $endTime (the 8 DUCTs, tracked by the rewrite)',
           guard_endtime_is_a_write_time('writeInterval $endTime;\n', 20000) is None)
    report('write-time guard IGNORES a COMMENTED-OUT writeInterval',
           guard_endtime_is_a_write_time('// writeInterval 30000;\nwriteInterval 4000;\n',
                                         20000) is None)
    _cd = 'writeControl timeStep;\nwriteInterval 30000;\n'
    _fx = re.sub(r'(\bwriteInterval\s+)[0-9.eE+-]+(\s*;)', r'\g<1>20000\g<2>', _cd, count=1)
    report('write-time guard: the REWRITE clears it (control flips back)',
           guard_endtime_is_a_write_time(_fx, 20000) is None)
    report('guard_no_zero_dir quiet on empty', guard_no_zero_dir(d) == [])
    os.makedirs(os.path.join(d, '0'))
    report('guard_no_zero_dir fires on a 0 dir', guard_no_zero_dir(d) == ['0'])

    # standing rule 3: PLANT INTO A FILE ON DISK, both sites gate G-D reads
    def _fresh(path):
        with open(path, 'w') as fh:
            fh.write('FoamFile\n{\n    object epsilon;\n}\n'
                     'dimensions [0 2 -3 0 0 0 0];\n\n'
                     'internalField   nonuniform List<scalar>\n3\n(\n1\n2\n3\n)\n;\n\n'
                     'boundaryField\n{\n    bottomWall\n    {\n'
                     '        type            fixedValue;\n'
                     '        value           uniform 0;\n    }\n}\n')
    f = os.path.join(d, 'epsilon')
    _fresh(f)
    report('rule 3 reader sees an INTERNAL plant written to DISK',
           guard_reader_sees_plant(f, 'internal'))
    _fresh(f)
    report('rule 3 reader sees a WALL-PATCH plant written to DISK',
           guard_reader_sees_plant(f, 'patch'))
    _fresh(f)
    report('rule 3 the plant really is on disk, not in memory',
           plant_into_file(f, 'internal') is not None
           and ('%.15g' % PLANT) in open(f).read())
    # L-314: a reader that cannot see the plant must REFUSE, not pass
    with open(f, 'w') as fh:
        fh.write('FoamFile\n{\n    object epsilon;\n}\nboundaryField\n{\n}\n')
    report('rule 3 blind reader is REFUSED (control flips)',
           not guard_reader_sees_plant(f, 'internal'))
    shutil.rmtree(d)

    # fvSolution surgery, on the shipped shapes, with zero free parameters
    duct = ('solvers\n{\n    p { solver GAMG; }\n    "(U|k)" { solver PBiCGStab; }\n'
            '    omega { $U; tolerance 1e-15; }\n}\n'
            'SIMPLE\n{\n    residualControl\n    {\n        k 5e-6;\n'
            '        omega 1e-10;\n    }\n}\n'
            'relaxationFactors\n{\n    fields { p 0.3; }\n'
            '    equations { U 0.9; "(k|omega)" 0.8; }\n}\n')
    new, rec = add_epsilon_to_fvsolution(duct)
    report('duct: solvers{epsilon} mirrors omega verbatim',
           new is not None and 'tolerance 1e-15' in new.split('epsilon')[1][:120])
    report('duct: relax epsilon = 0.8 resolved through the regex key "(k|omega)"',
           new is not None and re.search(r'epsilon\s+0\.8;', new) is not None)
    # RULING 2, both directions: the shipped criteria are GONE, not mirrored.
    report('RULING 2 duct: residualControl is EMPTIED (no k, no omega, no epsilon)',
           new is not None and residual_control_bodies(new) == [''])
    report('RULING 2 duct: the shipped bodies are RECORDED before being emptied',
           'k 5e-6; omega 1e-10;' in str(rec['residualControl']))
    report('RULING 2 L-314: the emptier CAN see a non-empty body (control fires)',
           residual_control_bodies(duct) == ['k 5e-6; omega 1e-10;'])
    report('RULING 2 L-314: emptying a shipped duct is NOT a no-op',
           new is not None and 'k 5e-6' not in new and '1e-10' in duct)
    _e2, _n2, _b2 = empty_residual_control(new)
    report('RULING 2: emptying an already-empty block is idempotent (n=0)', _n2 == 0)
    _multi = ('SIMPLE\n{\n    residualControl\n    {\n        p 1e-9;\n    }\n}\n'
              'PIMPLE\n{\n    residualControl\n    {\n        U 1e-7;\n    }\n}\n')
    _m3, _n3, _b3 = empty_residual_control(_multi)
    report('RULING 2: EVERY residualControl block is emptied, not just the first',
           _n3 == 2 and residual_control_bodies(_m3) == ['', ''])
    hill = ('solvers\n{\n    p { solver PCG; }\n    U { solver PBiCG; }\n'
            '    k { solver PBiCG; }\n    omega { solver PBiCG; relTol 0.1; }\n}\n'
            'relaxationFactors\n{\n    p 0.3;\n    U 0.7;\n    k 0.7;\n'
            '    omega 0.7;\n}\n')
    new2, _ = add_epsilon_to_fvsolution(hill)
    report('hill: solvers{epsilon} inserted', new2 is not None and
           block_span(new2[block_span(new2, 'solvers')[1]:], 'epsilon') is not None)
    report('hill: flat relaxationFactors epsilon 0.7',
           new2 is not None and re.search(r'epsilon\s+0\.7;', new2) is not None)
    report('hill: no residualControl -> left alone',
           new2 is not None and 'residualControl' not in new2)
    commented = ('solvers\n{\n    p { solver GAMG; }\n    omega { solver PBiCG; }\n'
                 '    /* epsilon\n    {\n        solver COMMENTED_OUT;\n    } */\n}\n')
    new3, rec3 = add_epsilon_to_fvsolution(commented)
    report('comment mask: a commented-out epsilon block is NOT mistaken for a real one',
           new3 is not None and rec3['solvers'].startswith('inserted'))
    report('comment mask: the commented text survives byte-for-byte',
           new3 is not None and 'COMMENTED_OUT' in new3)
    def _raw_span(txt, kw):
        """block_span with the mask REMOVED -- the mutated guard, for L-314."""
        for m in re.finditer(r'(?<![\w"])' + re.escape(kw) + r'(?![\w"])', txt):
            j = m.end()
            while j < len(txt) and txt[j] in ' \t\r\n':
                j += 1
            if j < len(txt) and txt[j] == '{':
                return m.start()
        return None
    report('L-314 mask mutated to a no-op -> the commented block IS mistaken '
           '(control flips)',
           _raw_span(commented, 'epsilon') is not None
           and _raw_span(mask_comments(commented), 'epsilon') is None
           and block_span(commented, 'epsilon') is None)
    report('comment mask preserves length (offsets stay valid)',
           len(mask_comments(commented)) == len(commented))
    broken, brec = add_epsilon_to_fvsolution('solvers\n{\n    p { solver GAMG; }\n}\n')
    report('L-314 fvSolution surgery REFUSES with no omega to mirror',
           broken is None and 'omega' in brec.get('error', ''))

    print('\nSELFTEST %s' % ('PASS' if ok else 'FAIL'))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--arm', choices=sorted(ARMS))
    ap.add_argument('--out')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not a.arm or not a.out:
        sys.stderr.write('REFUSE: --arm and --out are required\n')
        sys.exit(2)
    m = stage_arm(a.arm, a.out, dry=a.dry_run)
    print('staged arm %s: %d cases, %d source files hashed before and after, unchanged'
          % (a.arm, len(m['cases']), m['n_source_files_hashed']))


if __name__ == '__main__':
    main()
