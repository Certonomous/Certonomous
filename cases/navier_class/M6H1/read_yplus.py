#!/usr/bin/env python3
"""M6H1 H-G3 instrument -- read the ACHIEVED y+ on the wing patch from a solved
OpenFOAM field, and APPLY M6H1_PREREGISTRATION.md section 5's claim-licence table.

WHAT SECTION 7 REGISTERS (H-G3): "y+ admission, measured on the solved field";
threshold "section 5's table, applied to the achieved y+ max on the wing patch";
label if not met "the claims section 5 forbids are FORBIDDEN; the run is not thereby
NOT A RESULT".  This instrument therefore NEVER emits NOT A RESULT and never emits
GATE FAIL: it emits a LICENCE.  Exit codes below.

WHY THE PATCH NAME IS PRINTED BESIDE EVERY VALUE (section 10).  A max can arrive from
a patch that is not the wing.  Every number this instrument prints carries the patch
it came from, and the patch-selection path is exercised by its own planted control
(PLANT B) which a global-max reader CANNOT survive.

PLANTED CONTROLS (rule 3).  Both plant INTO THE INPUT -- they rewrite a field file in
a COPY OF THE CASE ON DISK and RE-RUN the real reader on that copy.  Neither relabels
a copy of the output; neither compares a copy with its own source (L-555).

  PLANT A -- SENSITIVITY.  Scale the WING patch's y+ list by a known factor in the
  copy on disk.  The reported wing max MUST move by exactly that factor.
  Code path exercised: read_field()'s boundaryField block walker and nonuniform
  List<scalar> value parser, then pick_patch()'s name dispatch -- i.e. exactly the
  path that produces the graded number.

  PLANT B -- DISCRIMINATION (patch selection).  Set a NON-wing patch to a value far
  ABOVE the wing's max in the copy on disk.  The reported wing max MUST NOT move.
  A reader that takes a global max over all patches reports the planted value and is
  REFUSED here.  This is the "could the phenomenon arrive another way?" column of
  section 10 made executable.

THE SAME-RUN ASSERTION -- WHY THIS READER CAN DECLINE RATHER THAN EMIT A NUMBER.
This reader combines TWO sources: the field file in <time>/ and the mesh's
constant/polyMesh/boundary.  A planted zero cannot catch a reader that returns a
confident FALSE NUMBER from two sources that describe different runs.  So, before any
number is emitted:
  (i)  every patch's nonuniform list length MUST equal that patch's nFaces in
       constant/polyMesh/boundary;
  (ii) the field's own FoamFile `location` MUST name the time directory it was read
       from;
  (iii) the wing patch MUST exist in BOTH sources.
Any failure -> DECLINE (exit 2).  A mismatched pair is not graded down, it is not
graded at all.

THE 30-300 BAND CARRIES A CONDITION AND THE CONDITION IS CHECKED, NOT ASSUMED.
Section 5 licenses Cp / shock / forces in 30 < y+ <= 300 only "(wall functions
consistently applied)".  This reader reads the wing's `nut` boundary type to decide
whether they were, and DECLINES (exit 2) in that band if it cannot tell.  Emitting a
licence whose condition was never checked is the confident-false-number failure, not
a false zero.

Exit codes:
  0  every section 5 claim LICENSED at the achieved y+
  1  at least one section 5 claim FORBIDDEN (H-G3 applied; this is NOT a GATE FAIL and
     NOT A RESULT is NOT implied -- section 7's H-G3 row says so in terms)
  2  REFUSE / DECLINE -- a control failed, or the two sources do not describe one run
"""
import sys, os, re, shutil, tempfile

# --- REGISTERED IN ADVANCE (M6H1_PREREGISTRATION.md sections 4, 5, 7). Do not edit to fit. ---
WING_PATCH_DEFAULT = 'wing'
S0_TARGET_YPLUS    = 1.0        # section 4: s0 = 1.6540e-06 m is the y+ = 1 first layer
BAND_RESOLVED      = 5.0        # section 5 row 1 upper edge
BAND_BUFFER_TOP    = 30.0       # section 5 row 2 upper edge
BAND_WF_TOP        = 300.0      # section 5 row 3 upper edge
CLAIMS             = ('Cp at the 7 sections', 'shock position', 'CL / CD / CM', 'Cf')
# Wall-function nut types that constitute "wall functions consistently applied".
# nutLowReWallFunction is NOT one of them: it sets nut = 0 at the wall, i.e. it is the
# WALL-RESOLVED treatment wearing a "WallFunction" suffix.  Classifying it as a wall
# function would LICENSE Cp / shock / forces in the 30-300 band on a mesh that is not
# using wall functions at all -- a confident false licence, not a false zero.
WF_NUT_TYPES       = ('nutkWallFunction', 'nutUWallFunction', 'nutUSpaldingWallFunction',
                      'nutkRoughWallFunction', 'nutUBlendedWallFunction',
                      'nutkAtmRoughWallFunction')
RESOLVED_NUT_TYPES = ('calculated', 'fixedValue', 'zeroGradient', 'nutLowReWallFunction')
# --------------------------------------------------------------------------------------------


# ------------------------------------------------------------------ OpenFOAM parsing
def _blocks(txt, open_idx):
    """Yield (name, body) for each `name { ... }` entry inside the block whose opening
    brace is at open_idx. Depth-counted, so nested braces in a body are safe."""
    i, n = open_idx + 1, len(txt)
    while i < n:
        while i < n and txt[i].isspace():
            i += 1
        if i < n and txt[i] == '}':
            return
        if i >= n:
            return
        j = txt.find('{', i)
        if j < 0:
            return
        name = txt[i:j].strip()
        depth, k = 1, j + 1
        while k < n and depth:
            if txt[k] == '{':
                depth += 1
            elif txt[k] == '}':
                depth -= 1
            k += 1
        yield name, txt[j + 1:k - 1]
        i = k


def read_field(path):
    """Read an OpenFOAM volScalarField from DISK. Returns (location, {patch: [values]}).
    A patch with `value uniform V` yields a single-element list -- a uniform patch has
    one value, and its length is NOT the patch face count, so the same-run assertion
    skips uniform patches explicitly rather than silently."""
    txt = open(path).read()
    loc = None
    mloc = re.search(r'\blocation\s+"([^"]*)"\s*;', txt)
    if mloc:
        loc = mloc.group(1)
    m = re.search(r'^\s*boundaryField\s*$', txt, re.M)
    if not m:
        m = re.search(r'\bboundaryField\b', txt)
        if not m:
            raise ValueError('no boundaryField in %s' % path)
    ob = txt.index('{', m.end())
    out = {}
    for name, body in _blocks(txt, ob):
        mn = re.search(r'\bvalue\s+nonuniform\s+List<scalar>\s*(\d+)\s*\(', body)
        if mn:
            cnt = int(mn.group(1))
            tail = body[mn.end():]
            cp = tail.index(')')
            vals = [float(t) for t in tail[:cp].split()]
            out[name] = ('nonuniform', cnt, vals)
            continue
        mu = re.search(r'\bvalue\s+uniform\s+(-?[\d.]+(?:[eE][-+]?\d+)?)\s*;', body)
        if mu:
            out[name] = ('uniform', None, [float(mu.group(1))])
            continue
        if re.search(r'\bvalue\s+nonuniform\s+0\s*\(\s*\)', body):
            out[name] = ('nonuniform', 0, [])
            continue
        out[name] = ('unparsed', None, [])
    return loc, out


def read_boundary_nfaces(polymesh_dir):
    """Read {patch: nFaces} from constant/polyMesh/boundary ON DISK."""
    p = os.path.join(polymesh_dir, 'boundary')
    txt = open(p).read()
    out = {}
    for m in re.finditer(r'(\S+)\s*\{[^{}]*?\bnFaces\s+(\d+)\s*;', txt):
        out[m.group(1)] = int(m.group(2))
    return out


def read_nut_type(case, time_dir, patch):
    """Read the wing's nut boundary CONDITION TYPE from disk. Returns the type string
    or None. Tried in the graded time directory first, then 0/."""
    for t in (time_dir, '0'):
        p = os.path.join(case, str(t), 'nut')
        if not os.path.isfile(p):
            continue
        txt = open(p).read()
        m = re.search(r'^\s*boundaryField\s*$', txt, re.M) or re.search(r'\bboundaryField\b', txt)
        if not m:
            continue
        for name, body in _blocks(txt, txt.index('{', m.end())):
            if name == patch:
                mt = re.search(r'\btype\s+(\w+)\s*;', body)
                if mt:
                    return mt.group(1)
    return None


# ------------------------------------------------------------------ the graded reading
def pick_patch(fields, patch):
    """Select ONE patch by name. Never a max over all patches -- PLANT B refuses that."""
    if patch not in fields:
        return None
    kind, cnt, vals = fields[patch]
    if not vals:
        return None
    return {'patch': patch, 'kind': kind, 'n': len(vals),
            'max': max(vals), 'min': min(vals), 'mean': sum(vals) / len(vals)}


def same_run(loc, fields, nfaces, time_dir, patch):
    """Assert the field and the mesh describe ONE run. Returns list of failures."""
    bad = []
    if loc is not None and str(loc).strip('"') != str(time_dir):
        bad.append("field's FoamFile location is %r but it was read from time %r -- the "
                   "field was written by a different time directory than the one graded"
                   % (loc, time_dir))
    if patch not in fields:
        bad.append("wing patch %r absent from the FIELD" % patch)
    if patch not in nfaces:
        bad.append("wing patch %r absent from constant/polyMesh/boundary" % patch)
    for name, (kind, cnt, vals) in sorted(fields.items()):
        if kind != 'nonuniform':
            continue
        if name not in nfaces:
            bad.append("patch %r is in the field but not in the mesh boundary" % name)
            continue
        if len(vals) != nfaces[name]:
            bad.append("patch %r: field carries %d values, mesh boundary says nFaces %d "
                       "-- the field and the mesh are NOT the same run"
                       % (name, len(vals), nfaces[name]))
        if cnt is not None and cnt != len(vals):
            bad.append("patch %r: list header says %d, %d values present -- truncated file"
                       % (name, cnt, len(vals)))
    return bad


def licence(ypmax, wf_applied):
    """Apply section 5's table EXACTLY. Returns (dict claim->LICENSED/FORBIDDEN, band, decline)."""
    if ypmax <= BAND_RESOLVED:
        return {c: 'LICENSED' for c in CLAIMS}, 'y+ max <= 5 (wall-resolved)', None
    if ypmax <= BAND_BUFFER_TOP:
        return {c: 'FORBIDDEN' for c in CLAIMS}, '5 < y+ max <= 30 (buffer layer)', None
    if ypmax <= BAND_WF_TOP:
        if wf_applied is None:
            return None, '30 < y+ max <= 300', (
                "section 5 licenses this band ONLY '(wall functions consistently applied)'. "
                "The wing's nut boundary type could not be read, so the CONDITION ON THE "
                "LICENCE WAS NEVER CHECKED. Emitting the licence anyway would be a confident "
                "false statement, which a planted zero cannot catch. DECLINE.")
        if not wf_applied:
            return {c: 'FORBIDDEN' for c in CLAIMS}, \
                   '30 < y+ max <= 300, WALL FUNCTIONS NOT APPLIED', None
        d = {c: 'LICENSED' for c in CLAIMS}
        d['Cf'] = 'FORBIDDEN'
        return d, '30 < y+ max <= 300 (wall functions applied)', None
    return {c: 'FORBIDDEN' for c in CLAIMS}, 'y+ max > 300', None


# ------------------------------------------------------------------ planted controls
def _copy_case_field(case, time_dir, field='yPlus'):
    d = tempfile.mkdtemp(prefix='m6h1_yp_')
    dst_case = os.path.join(d, 'case')
    os.makedirs(os.path.join(dst_case, str(time_dir)))
    os.makedirs(os.path.join(dst_case, 'constant'))
    shutil.copy2(os.path.join(case, str(time_dir), field),
                 os.path.join(dst_case, str(time_dir), field))
    shutil.copytree(os.path.join(case, 'constant', 'polyMesh'),
                    os.path.join(dst_case, 'constant', 'polyMesh'))
    for t in (str(time_dir), '0'):
        src = os.path.join(case, t, 'nut')
        if os.path.isfile(src):
            os.makedirs(os.path.join(dst_case, t), exist_ok=True)
            shutil.copy2(src, os.path.join(dst_case, t, 'nut'))
    return d, dst_case


def _rewrite_patch(path, patch, fn):
    """Rewrite `patch`'s numeric values in the file AT path, in place, on disk.
    fn(v) -> new value. Uniform values are rewritten too."""
    txt = open(path).read()
    m = re.search(r'^\s*boundaryField\s*$', txt, re.M) or re.search(r'\bboundaryField\b', txt)
    ob = txt.index('{', m.end())
    pieces, touched = [], 0
    i, n = ob + 1, len(txt)
    pieces.append(txt[:ob + 1])
    for name, body in _blocks(txt, ob):
        start = txt.index('{', txt.index(name, i)) + 1
        end = start + len(body)
        pieces.append(txt[i:start])
        if name == patch:
            nb, touched = _rewrite_body(body, fn)
            pieces.append(nb)
        else:
            pieces.append(body)
        pieces.append('}')
        i = end + 1
    pieces.append(txt[i:])
    open(path, 'w').write(''.join(pieces))
    return touched


def _rewrite_body(body, fn):
    mn = re.search(r'(\bvalue\s+nonuniform\s+List<scalar>\s*\d+\s*\()', body)
    if mn:
        tail = body[mn.end():]
        cp = tail.index(')')
        vals = [float(t) for t in tail[:cp].split()]
        new = '\n'.join('%.10g' % fn(v) for v in vals)
        return body[:mn.end()] + '\n' + new + '\n' + tail[cp:], len(vals)
    mu = re.search(r'(\bvalue\s+uniform\s+)(-?[\d.]+(?:[eE][-+]?\d+)?)', body)
    if mu:
        return body[:mu.start(2)] + ('%.10g' % fn(float(mu.group(2)))) + body[mu.end(2):], 1
    return body, 0


def planted_controls(case, time_dir, patch, factor=3.0, decoy=1.0e6, field='yPlus'):
    """PLANT A (sensitivity) and PLANT B (patch-selection discrimination), both into the
    INPUT on disk, both re-running the real reader FROM DISK. Returns (ok, lines)."""
    out = []
    loc, f0 = read_field(os.path.join(case, str(time_dir), field))
    nf = read_boundary_nfaces(os.path.join(case, 'constant', 'polyMesh'))
    base = pick_patch(f0, patch)
    if base is None:
        return False, ["REFUSE: wing patch %r carries no values in the clean field" % patch]
    others = [p for p, (k, c, v) in f0.items() if p != patch and v]
    out.append("clean: %s max = %.6e  (n = %d, %s)" % (patch, base['max'], base['n'], base['kind']))

    # ---- PLANT A ----
    d, cc = _copy_case_field(case, time_dir, field)
    t = _rewrite_patch(os.path.join(cc, str(time_dir), field), patch, lambda v: v * factor)
    _, fa = read_field(os.path.join(cc, str(time_dir), field))
    pa = pick_patch(fa, patch)
    shutil.rmtree(d, ignore_errors=True)
    exp = base['max'] * factor
    # DETECTION HAS TWO CLAUSES AND BOTH ARE REQUIRED.  (i) the re-read number must MOVE
    # off the clean number -- a control that only checks "equals the prediction" reports
    # DETECTED for a factor of 1.0, i.e. for no plant at all, which is the tautology
    # L-555 names.  (ii) it must move by the PREDICTED amount, not merely move.
    moved_a = pa is not None and abs(pa['max'] - base['max']) > 1e-12 * max(1.0, base['max'])
    exact_a = pa is not None and abs(pa['max'] - exp) <= 1e-9 * max(1.0, abs(exp))
    seen_a = bool(moved_a and exact_a and t > 0 and abs(factor - 1.0) > 1e-12)
    out.append("PLANT A (sensitivity): scaled %d values of patch '%s' by %.6g in a COPY ON DISK"
               % (t, patch, factor))
    out.append("   re-read from disk: %s max = %s   clean %.6e   expected %.6e"
               % (patch, ('%.6e' % pa['max']) if pa else 'ABSENT', base['max'], exp))
    out.append("   MOVED off clean: %s    moved by the PREDICTED amount: %s    SEEN: %s"
               % (moved_a, exact_a, seen_a))
    if abs(factor - 1.0) <= 1e-12:
        out.append("   NOT A PLANT: a factor of 1.0 changes nothing, so nothing was planted and "
                   "nothing can be detected. The control reports NOT DETECTED, as it must.")

    # ---- PLANT B ----
    seen_b, note_b = True, 'no other patch carries values -- discrimination NOT established'
    if others:
        victim = max(others, key=lambda p: max(f0[p][2]))
        d, cc = _copy_case_field(case, time_dir, field)
        tb = _rewrite_patch(os.path.join(cc, str(time_dir), field), victim, lambda v: decoy)
        _, fb = read_field(os.path.join(cc, str(time_dir), field))
        pb = pick_patch(fb, patch)
        shutil.rmtree(d, ignore_errors=True)
        moved = pb is None or abs(pb['max'] - base['max']) > 1e-12 * max(1.0, base['max'])
        # The decoy is only a decoy if it is ABOVE the wing max: a decoy below it could not
        # move a global max either, so a "pass" would prove nothing.
        real_decoy = decoy > base['max'] * (1.0 + 1e-12)
        seen_b = (not moved) and real_decoy
        note_b = ("set %d values of NON-wing patch '%s' to %.3e in a COPY ON DISK; "
                  "'%s' max re-read as %s (clean %.6e) -- wing max UNMOVED: %s; "
                  "decoy ABOVE the wing max (so a global-max reader would have to move): %s"
                  % (tb, victim, decoy, patch,
                     ('%.6e' % pb['max']) if pb else 'ABSENT', base['max'], moved is False,
                     real_decoy))
    out.append("PLANT B (patch selection): " + note_b)

    ok = seen_a and seen_b and bool(others)
    if not seen_a:
        out.append("   REFUSE: the reader did not see a known non-zero change in its own input. "
                   "Its clean number is NOT evidence (rule 3).")
    if others and not seen_b:
        out.append("   REFUSE: either planting a NON-wing patch moved the reported wing max -- so "
                   "this reader takes a global max and its patch name is decoration -- or the "
                   "decoy was not above the wing max, in which case it discriminated nothing.")
    if not others:
        out.append("   REFUSE: the field has no second patch, so patch selection cannot be "
                   "discriminated. An undiscriminated max is not evidence.")
    return ok, out


# ------------------------------------------------------------------ selftest
def _synth_case(root, wing_vals, other_vals, nut_type='nutkWallFunction',
                wing='wing', other='farfield', time_dir='500', loc=None):
    case = os.path.join(root, 'case')
    os.makedirs(os.path.join(case, time_dir), exist_ok=True)
    os.makedirs(os.path.join(case, 'constant', 'polyMesh'), exist_ok=True)

    def fld(path, obj, entries):
        with open(path, 'w') as f:
            f.write('FoamFile\n{\n    version 2.0;\n    format ascii;\n'
                    '    class volScalarField;\n    location "%s";\n    object %s;\n}\n'
                    % (loc if loc is not None else time_dir, obj))
            f.write('dimensions [0 0 0 0 0 0 0];\n\ninternalField uniform 0;\n\nboundaryField\n{\n')
            for nm, vals in entries:
                f.write('    %s\n    {\n        type            calculated;\n' % nm)
                f.write('        value           nonuniform List<scalar> \n%d\n(\n%s\n)\n;\n'
                        % (len(vals), '\n'.join('%.10g' % v for v in vals)))
                f.write('    }\n')
            f.write('}\n')

    fld(os.path.join(case, time_dir, 'yPlus'), 'yPlus',
        [(wing, wing_vals), (other, other_vals)])
    with open(os.path.join(case, time_dir, 'nut'), 'w') as f:
        f.write('FoamFile\n{\n    class volScalarField;\n    object nut;\n}\n\nboundaryField\n{\n')
        f.write('    %s\n    {\n        type            %s;\n        value uniform 0;\n    }\n'
                % (wing, nut_type))
        f.write('    %s\n    {\n        type            calculated;\n        value uniform 0;\n    }\n'
                % other)
        f.write('}\n')
    with open(os.path.join(case, 'constant', 'polyMesh', 'boundary'), 'w') as f:
        f.write('FoamFile\n{\n    class polyBoundaryMesh;\n    object boundary;\n}\n\n2\n(\n')
        f.write('    %s\n    {\n        type wall;\n        nFaces %d;\n        startFace 0;\n    }\n'
                % (wing, len(wing_vals)))
        f.write('    %s\n    {\n        type patch;\n        nFaces %d;\n        startFace %d;\n    }\n'
                % (other, len(other_vals), len(wing_vals)))
        f.write(')\n')
    return case


def selftest():
    rc = 0
    d = tempfile.mkdtemp(prefix='m6h1_yp_self_')

    print("ARM 1 -- PLANT APPLIED, sound reader: both controls must be SEEN")
    c1 = _synth_case(os.path.join(d, 'a1'), [0.8, 1.9, 3.4, 0.5], [10.0, 12.0, 11.0])
    ok1, msg = planted_controls(c1, '500', 'wing')
    for m in msg:
        print("   " + m)
    print("   -> %s (expected DETECTED)" % ('DETECTED' if ok1 else 'NOT DETECTED'))

    print("\nARM 2 -- PLANT WITHHELD (factor 1.0 = the input is rewritten but UNCHANGED):")
    print("         the control must report NOT DETECTED. A control that reports DETECTED")
    print("         when no plant was applied proves nothing (L-555).")
    ok2, msg = planted_controls(c1, '500', 'wing', factor=1.0)
    for m in msg:
        print("   " + m)
    print("   -> %s (expected NOT DETECTED)" % ('DETECTED' if ok2 else 'NOT DETECTED'))
    withheld_ok = not ok2

    print("\nARM 3 -- BLINDED READER, plant applied: the control must REFUSE")
    g = globals()
    saved = g['read_field']
    frozen = saved(os.path.join(c1, '500', 'yPlus'))
    g['read_field'] = lambda p: frozen
    ok3, msg = planted_controls(c1, '500', 'wing')
    g['read_field'] = saved
    for m in msg:
        print("   " + m)
    print("   -> %s (expected NOT DETECTED -- this is the control refusing)"
          % ('DETECTED' if ok3 else 'NOT DETECTED'))

    print("\nARM 4 -- GLOBAL-MAX READER (patch name is decoration): PLANT B must REFUSE it")
    saved_pick = g['pick_patch']
    def global_max(fields, patch):
        allv = [v for (k, c, vals) in fields.values() for v in vals]
        return {'patch': patch, 'kind': 'GLOBAL', 'n': len(allv),
                'max': max(allv), 'min': min(allv), 'mean': sum(allv) / len(allv)}
    g['pick_patch'] = global_max
    ok4, msg = planted_controls(c1, '500', 'wing')
    g['pick_patch'] = saved_pick
    for m in msg:
        print("   " + m)
    print("   -> %s (expected NOT DETECTED -- PLANT B catches the global max)"
          % ('DETECTED' if ok4 else 'NOT DETECTED'))

    print("\nARM 5 -- SAME-RUN ASSERTION: field list length != mesh nFaces must DECLINE")
    c5 = _synth_case(os.path.join(d, 'a5'), [0.8, 1.9, 3.4, 0.5], [10.0, 12.0, 11.0])
    b = os.path.join(c5, 'constant', 'polyMesh', 'boundary')
    # READ FIRST, THEN WRITE. `open(b,'w').write(open(b).read()...)` truncates the file
    # before the read runs, and would demonstrate an EMPTY boundary file rather than the
    # length mismatch this arm claims to demonstrate.
    _txt = open(b).read()
    assert 'nFaces 4;' in _txt, 'ARM 5 precondition: wing nFaces 4 must be present'
    open(b, 'w').write(_txt.replace('nFaces 4;', 'nFaces 7;'))
    loc, f = read_field(os.path.join(c5, '500', 'yPlus'))
    bad = same_run(loc, f, read_boundary_nfaces(os.path.join(c5, 'constant', 'polyMesh')),
                   '500', 'wing')
    for x in bad:
        print("   " + x)
    ok5 = any('NOT the same run' in x for x in bad)
    print("   -> %s (expected DECLINE, on the LENGTH MISMATCH specifically)"
          % ('DECLINE' if ok5 else 'NO DECLINE ON THE INTENDED CAUSE -- DEFECT'))

    print("\nARM 6 -- SAME-RUN ASSERTION: FoamFile location naming another time must DECLINE")
    c6 = _synth_case(os.path.join(d, 'a6'), [0.8, 1.9], [10.0], time_dir='500', loc='250')
    loc, f = read_field(os.path.join(c6, '500', 'yPlus'))
    bad6 = same_run(loc, f, read_boundary_nfaces(os.path.join(c6, 'constant', 'polyMesh')),
                    '500', 'wing')
    for x in bad6:
        print("   " + x)
    ok6 = any('location' in x for x in bad6)
    print("   -> %s (expected DECLINE)" % ('DECLINE' if ok6 else 'NO DECLINE -- DEFECT'))

    print("\nARM 7 -- the 30-300 band with an UNREADABLE wall treatment must DECLINE,")
    print("         because section 5 licenses that band only on a condition.")
    lic, band, dec = licence(120.0, None)
    print("   " + (dec or 'NO DECLINE -- DEFECT'))
    ok7 = dec is not None and lic is None
    lic2, band2, _ = licence(120.0, True)
    print("   with wall functions CONFIRMED: %s -> Cf %s, Cp %s"
          % (band2, lic2['Cf'], lic2['Cp at the 7 sections']))
    ok7 = ok7 and lic2['Cf'] == 'FORBIDDEN' and lic2['Cp at the 7 sections'] == 'LICENSED'
    lic3, band3, _ = licence(12.0, True)
    print("   at y+ max 12.0: %s -> every claim %s" % (band3, lic3['Cp at the 7 sections']))
    ok7 = ok7 and all(v == 'FORBIDDEN' for v in lic3.values())

    shutil.rmtree(d, ignore_errors=True)
    good = ok1 and (not ok3) and (not ok4) and ok5 and ok6 and ok7 and withheld_ok
    print("\nSELFTEST %s" % ('PASS -- the controls SEE a real plant, do NOT see a withheld one, '
                             'REFUSE a blinded reader, REFUSE a global-max reader, and the '
                             'same-run assertion DECLINES on both mismatch modes'
                             if good else 'FAIL'))
    return 0 if good else 1


# ------------------------------------------------------------------ main
def main(case, time_dir, patch):
    print("M6H1 H-G3 -- achieved y+ on the wing patch, section 5's claim licence APPLIED")
    print("CASE: %s    TIME: %s    WING PATCH: %s" % (case, time_dir, patch))
    print("REGISTERED (section 4): s0 = 1.6540e-06 m, a y+ = %.0f first layer\n" % S0_TARGET_YPLUS)

    fpath = os.path.join(case, str(time_dir), 'yPlus')
    if not os.path.isfile(fpath):
        print("REFUSE (exit 2): no y+ field at %s. A y+ this reader cannot see is not a y+ of 1."
              % fpath)
        return 2
    pm = os.path.join(case, 'constant', 'polyMesh')
    if not os.path.isdir(pm):
        print("REFUSE (exit 2): no %s -- the second source of the same-run assertion is absent."
              % pm)
        return 2

    ok, msg = planted_controls(case, time_dir, patch)
    print("PLANTED CONTROLS -- planted INTO THE INPUT, real reader re-run FROM DISK")
    for m in msg:
        print("  " + m)
    if not ok:
        print("\nREFUSE (exit 2): the controls did not establish that this reader sees a known "
              "non-zero AND selects the wing patch. No number below would be evidence.")
        return 2

    loc, fields = read_field(fpath)
    nf = read_boundary_nfaces(pm)
    bad = same_run(loc, fields, nf, str(time_dir), patch)
    print("\nSAME-RUN ASSERTION -- field in %s/ against constant/polyMesh/boundary" % time_dir)
    if bad:
        for b in bad:
            print("  " + b)
        print("\nDECLINE (exit 2): the two sources do not describe one run. A plausible y+ from "
              "a mismatched pair is a confident FALSE NUMBER, which a planted zero cannot catch.")
        return 2
    print("  every nonuniform patch length == its nFaces; location == %s; wing present in both."
          % time_dir)

    print("\n  %-24s %8s %14s %14s %14s" % ('patch (NAME BESIDE VALUE)', 'n', 'y+ max', 'y+ mean', 'y+ min'))
    for name in sorted(fields):
        r = pick_patch(fields, name)
        if r is None:
            print("  %-24s %8s %14s %14s %14s" % (name, '-', 'no values', '-', '-'))
            continue
        mark = '   <-- WING, the graded patch' if name == patch else ''
        print("  %-24s %8d %14.6e %14.6e %14.6e%s"
              % (name, r['n'], r['max'], r['mean'], r['min'], mark))

    w = pick_patch(fields, patch)
    nut = read_nut_type(case, time_dir, patch)
    # THREE-VALUED, NOT TWO.  True = wall functions; False = wall-resolved; None = the
    # type is in neither registered list, so the CONDITION on section 5's 30-300 row was
    # not established and licence() DECLINES rather than guessing either way.
    wf = None
    if nut in WF_NUT_TYPES:
        wf = True
    elif nut in RESOLVED_NUT_TYPES:
        wf = False
    print("\nACHIEVED y+ MAX = %.6e  ON PATCH '%s'  (never a global max -- PLANT B forbids it)"
          % (w['max'], w['patch']))
    print("wing nut boundary type read from disk: %s -> wall functions applied: %s"
          % (nut if nut else 'UNREADABLE', wf))

    lic, band, dec = licence(w['max'], wf)
    if dec:
        print("\nDECLINE (exit 2): " + dec)
        return 2
    print("\nH-G3 -- section 5's table APPLIED. BAND: %s" % band)
    for c in CLAIMS:
        print("   %-24s %s" % (c, lic[c]))
    forb = [c for c in CLAIMS if lic[c] == 'FORBIDDEN']
    if forb:
        print("\nH-G3 applied. %d of %d claims FORBIDDEN. Section 7's H-G3 row: the run is NOT "
              "thereby NOT A RESULT." % (len(forb), len(CLAIMS)))
        return 1
    print("\nH-G3: PASS -- every section 5 claim LICENSED at the achieved y+.")
    return 0


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--selftest':
        sys.exit(selftest())
    if len(sys.argv) < 3:
        sys.exit("usage: read_yplus.py <case_dir> <time_dir> [wing_patch] | --selftest")
    sys.exit(main(sys.argv[1], sys.argv[2],
                  sys.argv[3] if len(sys.argv) > 3 else WING_PATCH_DEFAULT))
