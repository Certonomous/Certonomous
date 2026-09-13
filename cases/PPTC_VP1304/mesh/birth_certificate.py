#!/usr/bin/env python3
"""PPTC VP1304 -- mesh birth certificate, pre-registration section 6.5.

Reports, for one built level, EVERY quantity section 6.5 makes mandatory, each beside the
gate it is measured against (Sanaa's section 5, transcribed in pre-registration 6.4):

    cells                                     -- family target, context not a gate
    max non-orthogonality   gate < 70 deg
    max skewness            gate < 4
    max adjacent-cell volume ratio  gate <= 1.25   -- Sanaa's "cell-volume growth capped at
                                                     1.25".  checkMesh does NOT report this,
                                                     so it is computed here directly from
                                                     polyMesh owner/neighbour against the
                                                     cell volumes checkMesh itself wrote.
    max aspect ratio        advisory 1000
    negative volumes        gate 0
    prism layers            gate 6 layers at growth ratio 1.2 on blades, hub, cap, shaft
    cells across LE radius  gate >= 8   (literal parse, registered to govern -- addendum E.5)
    cells across tip chord  gate >= 6
    mesh hash

IT REFUSES RATHER THAN DEGRADES.  Exit 2 if any input it needs is absent: a gate reported
from a file that was not there is worse than a gate not reported.  Exit 3 if a gate FAILS --
a distinct code, because "I could not measure it" and "I measured it and it is out" are
different findings and a caller that cannot tell them apart will treat one as the other.

A ZERO NEEDS A LIVE PLANTED CONTROL (standing rule 3).  --selftest plants a known bad value
into each numeric gate's input and requires the gate to flip to FAIL; a gate never shown able
to fail is not known to work.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import struct
import sys

# --- REGISTERED GATES (pre-registration 6.3, 6.4; Sanaa sections 5 and 6) ---------------
GATE_NONORTHO = 70.0          # deg, strict <
GATE_SKEWNESS = 4.0           # strict <
GATE_VOLGROWTH = 1.25         # adjacent-cell volume ratio, <=
ADVISORY_ASPECT = 1000.0
GATE_LAYERS = 6
GATE_EXPANSION = 1.2
LAYER_PATCHES = ('blades', 'hub', 'cap', 'shaft')
GATE_LE_CELLS = 8.0           # literal parse: cells across the LE RADIUS (addendum E.5)
GATE_TIP_CELLS = 6.0          # cells across the tip chord
GATE_CYCLIC_MATCH = 1.0e-6    # m, average coupled point location match on the periodics

# MEASURED geometry, mesh pipeline record CORRECTION 1 ADDENDUM F.3.  The three stations that
# the clamp guard ACCEPTED; r/R = 0.70 and outboard were REFUSED and are not extrapolated.
# The smallest accepted radius is used, because it is the hardest to resolve.
R_LE_MM = 1.4380              # mm, at r/R = 0.60; 1.7322 at 0.50 and 1.8233 at 0.40
R_LE_STATION = 'r/R = 0.60 (smallest of the three ACCEPTED stations; 0.70 and outboard '\
               'were REFUSED by the clamp guard and are NOT extrapolated)'
# Tip chord: the expanded-area section sweep's outermost band, compare_sections.py.
C_TIP_MM = 39.0
C_TIP_BASIS = 'outermost band of the twelve-radius section sweep (compare_sections.py); '\
              'DECLARED, and it clears its gate by a wide margin at every level'

# SECTOR PHASE -- A RECORDED MESH PROPERTY, because it was free to choose and is now fixed.
# It is imported from the generator rather than retyped, so the certificate cannot drift from
# the dictionary it describes. The clearance beside it is a MEASUREMENT over every blade
# vertex, not a bin count, and it is stated with its basis so a reader can re-derive it.
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from make_blockmesh import SECTOR_PHASE_DEG as _PHASE
except Exception:
    _PHASE = None
PHASE_CLEARANCE_DEG = 4.5084
PHASE_CLEARANCE_BASIS = ('minimum angular distance from either periodic plane to the nearest '
                         'of 17,843,469 blade vertices, folded onto one 72 deg passage')
BLADE_ANGULAR_WIDTH_DEG = 62.98
INTERBLADE_GAP_DEG = 9.0169


class Refusal(Exception):
    pass


def _read_ints(path):
    """Read an OpenFOAM labelList (ascii or binary) -- owner/neighbour."""
    with open(path, 'rb') as fh:
        raw = fh.read()
    m = re.search(rb'\n(\d+)\s*\(', raw)
    if m is None:
        raise Refusal(f'cannot find the list header in {path}')
    n = int(m.group(1))
    start = m.end()
    # binary lists are written as <n>(<raw bytes>)
    tail = raw[start:]
    if len(tail) >= 4 * n and not tail[:64].lstrip().startswith(b'0') or b'\n' not in tail[:64]:
        pass
    # decide by whether the next 4*n bytes are followed by ')'
    for width, fmt in ((4, '<%di'), (8, '<%dq')):
        if len(tail) > width * n and tail[width * n:width * n + 1] == b')':
            return list(struct.unpack(fmt % n, tail[:width * n]))
    # ascii
    txt = tail.decode('ascii', 'replace')
    end = txt.index(')')
    return [int(v) for v in txt[:end].split()]


def _read_scalars_volfield(path):
    """Read internalField of a volScalarField written by checkMesh -writeAllFields."""
    with open(path, 'rb') as fh:
        raw = fh.read()
    m = re.search(rb'internalField\s+nonuniform\s+List<scalar>\s*\n?(\d+)\s*\(', raw)
    if m is None:
        m2 = re.search(rb'internalField\s+uniform\s+([-\deE.+]+)\s*;', raw)
        if m2:
            raise Refusal(f'{path} holds a UNIFORM internalField; checkMesh did not write '
                          'per-cell values, so the volume-growth gate cannot be measured')
        raise Refusal(f'cannot parse internalField in {path}')
    n = int(m.group(1))
    tail = raw[m.end():]
    if len(tail) > 8 * n and tail[8 * n:8 * n + 1] == b')':
        return list(struct.unpack('<%dd' % n, tail[:8 * n]))
    txt = tail.decode('ascii', 'replace')
    return [float(v) for v in txt[:txt.index(')')].split()]


def parse_checkmesh(path):
    """Pull the geometry maxima out of checkMesh's own output. REFUSES on a missing line
    rather than defaulting: an absent metric reported as 0.0 would PASS every gate."""
    if not os.path.exists(path):
        raise Refusal(f'no checkMesh log at {path}')
    txt = open(path, errors='replace').read()
    out = {}
    # EACH METRIC HAS TWO PRINTED FORMS AND THE INSTRUMENT MUST READ BOTH.  checkMesh prints
    # "Max skewness = 0.27 OK." when a check passes and "***Max skewness = 305.39, 94 highly
    # skew faces detected" when it FAILS -- a different sentence.  An instrument that matches
    # only the passing form REFUSES on exactly the meshes it exists to judge, which is what
    # this one did on its first real broken mesh.  The refusal was correct behaviour; being
    # unable to read a failure is not.
    pats = {
        'cells': [r'\n\s*cells:\s+(\d+)'],
        'nonortho': [r'Mesh non-orthogonality Max:\s*([-\d.eE+]+)'],
        'skewness': [r'Max skewness = ([-\d.eE+]+)\s+OK',
                     r'\*\*\*Max skewness = ([-\d.eE+]+)'],
        'aspect': [r'Max aspect ratio = ([-\d.eE+]+)\s+OK',
                   r'Max aspect ratio:\s*([-\d.eE+]+)'],
        'minvol': [r'Min volume = ([-\d.eE+]+)',
                   r'Minimum negative volume:\s*([-\d.eE+]+)'],
        # THE ONE THING A 72 deg SECTOR MESH CAN GET WRONG SILENTLY.  A mismatched cyclic
        # pair runs, converges and returns a confidently wrong KT with NO residual
        # signature to warn anyone (MESH_PIPELINE_RECORD.md section 3).  It is a
        # CORRECTNESS check, not a quality disclosure, and is kept separate for that reason.
        'cyclic_match': [r'Coupled point location match \(average ([-\d.eE+]+)\)'],
    }
    for k, forms in pats.items():
        val = None
        for p in forms:
            m = re.search(p, txt)
            if m is not None:
                # 🔴 A TRAILING SENTENCE PERIOD IS PART OF THE MATCH.  checkMesh writes
                # "Min volume = 1.6837015e-12." -- with a full stop -- and the character
                # class [-\d.eE+] swallows it, so float() raised ValueError and this
                # instrument died with a TRACEBACK instead of refusing. An instrument that
                # CRASHES is worse than one that refuses: it neither reports nor abstains,
                # and the caller sees rc=1 with no verdict at all. Strip, then convert, and
                # convert inside a guard so a malformed number REFUSES like everything else.
                raw = m.group(1).strip().rstrip('.')
                try:
                    val = float(raw)
                except ValueError:
                    raise Refusal(f'checkMesh log {path}: {k!r} matched {m.group(1)!r} which '
                                  f'is not a number after stripping to {raw!r} -- refusing')
                break
        if val is None:
            raise Refusal(f'checkMesh log {path} carries no line matching {k!r} in any of its '
                          f'{len(forms)} known printed forms -- refusing rather than '
                          'reporting a metric that was never measured')
        out[k] = val
    out['cells'] = int(out['cells'])
    m = re.search(r'\*\*\*Error.*?negative volume', txt, re.S)
    out['neg_vol_flagged'] = bool(m)
    return out


def parse_layers(path):
    """What snappyHexMesh ACTUALLY EXTRUDED -- never what it was asked for.

    🔴 THE TABLE IN THE LOG IS THE REQUEST, NOT THE ACHIEVEMENT, AND THIS INSTRUMENT READ THE
    WRONG ONE.  Measured on this act's own coarse level: the log printed

        patch  faces    layers avg thickness[m]
        blades 76465    6      1.79e-06  1.07e-05

    and the run exited rc = 0 -- while the very same log said

        Extruding 0 out of 76465 faces (0%). Removed extrusion at 0 faces.
        Added 0 out of 458790 cells (0%).

    and the cell count was IDENTICAL before and after layer addition, 3,939,801 -> 3,939,801.
    ZERO LAYERS EXISTED ON THAT MESH.  An earlier version of this function read the table and
    would have certified "blades 6.00 of 6 nominal, coverage 100.0 %, SPECIFICATION MET".
    That is a certificate asserting six prism layers on a mesh with none, from a clean rc and
    a truthful-looking table -- the believable wrong answer in its purest form.

    THE ACHIEVEMENT IS THEREFORE TAKEN FROM THREE INDEPENDENT PLACES AND THEY MUST AGREE:
      (1) the LAST `Extruding N out of M faces (P%)` line,
      (2) the LAST `Added X out of Y cells (Q%)` line,
      (3) the CELL DELTA between `Snapped mesh : cells:` and `Layer mesh : cells:`.
    A delta of zero means no layers, whatever any table says.  If the log carries none of
    these lines this REFUSES rather than falling back to the table.
    """
    if not os.path.exists(path):
        raise Refusal(f'no snappyHexMesh log at {path}')
    txt = open(path, errors='replace').read()

    ex = re.findall(r'Extruding (\d+) out of (\d+) faces \(([\d.]+)%\)', txt)
    ad = re.findall(r'Added (\d+) out of (\d+) cells \(([\d.]+)%\)', txt)
    snap = re.findall(r'Snapped mesh : cells:(\d+)', txt)
    lay = re.findall(r'Layer mesh : cells:(\d+)', txt)
    # A LAYER PHASE THAT DIED BEFORE ITS COUNTERS IS "UNKNOWN", NOT "ZERO" AND NOT A REASON
    # TO SUPPRESS THE QUALITY VERDICT.  Refusing the whole certificate here was measured to
    # hide Sanaa's three gates on a mesh whose gates were the entire point of reading it:
    # the medium level's layer phase aborted before printing any extrusion counter, and the
    # instrument returned nothing at all rather than "non-orthogonality 86.38, skewness
    # 4.89, min volume positive".  The LAYER NUMBER is still refused -- the per-patch table
    # is the REQUEST and is never read as an achievement -- but the gates are reported.
    unknown = (not ex and not ad)

    achieved = {'unknown': unknown}
    achieved['faces_extruded'] = int(ex[-1][0]) if ex else None
    achieved['faces_total'] = int(ex[-1][1]) if ex else None
    achieved['faces_pct'] = float(ex[-1][2]) if ex else None
    achieved['cells_added'] = int(ad[-1][0]) if ad else None
    achieved['cells_wanted'] = int(ad[-1][1]) if ad else None
    achieved['cells_pct'] = float(ad[-1][2]) if ad else None
    achieved['cell_delta'] = ((int(lay[-1]) - int(snap[-1]))
                              if (snap and lay) else None)

    requested = {}
    for line in txt.splitlines():
        t = line.strip()
        for p in LAYER_PATCHES:
            if t.startswith(p + ' '):
                f = t.split()
                if len(f) >= 4:
                    try:
                        requested[p] = dict(faces=int(f[1]), layers=float(f[2]),
                                            thickness=float(f[3]),
                                            thickness_pct=(float(f[4]) if len(f) >= 5
                                                           else None))
                    except ValueError:
                        pass
    return dict(_achieved=achieved, _requested=requested)


def volume_growth(case):
    """Max ratio of adjacent cell volumes, both directions, from polyMesh + cellVolume.
    Sanaa's cap is 1.25 and checkMesh reports no such quantity, so it is computed here."""
    pm = os.path.join(case, 'constant', 'polyMesh')
    own = _read_ints(os.path.join(pm, 'owner'))
    nei = _read_ints(os.path.join(pm, 'neighbour'))
    vol = None
    for t in ('0', 'constant'):
        p = os.path.join(case, t, 'cellVolume')
        if os.path.exists(p):
            vol = _read_scalars_volfield(p)
            break
    if vol is None:
        raise Refusal('no cellVolume field -- run checkMesh with -writeAllFields first. '
                      'REFUSING: the volume-growth gate cannot be inferred from anything '
                      'else checkMesh prints.')
    worst, wf = 1.0, -1
    for f, n in enumerate(nei):
        a, b = vol[own[f]], vol[n]
        if a <= 0 or b <= 0:
            continue
        r = a / b if a > b else b / a
        if r > worst:
            worst, wf = r, f
    n_over = 0
    for f, n in enumerate(nei):
        a, b = vol[own[f]], vol[n]
        if a <= 0 or b <= 0:
            continue
        r = a / b if a > b else b / a
        if r > GATE_VOLGROWTH:
            n_over += 1
    return worst, wf, n_over, len(nei)


def mesh_hash(case):
    pm = os.path.join(case, 'constant', 'polyMesh')
    h = hashlib.sha256()
    for fn in ('points', 'faces', 'owner', 'neighbour', 'boundary'):
        p = os.path.join(pm, fn)
        if not os.path.exists(p):
            raise Refusal(f'polyMesh incomplete: {p} missing')
        with open(p, 'rb') as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b''):
                h.update(chunk)
    return h.hexdigest()


def report(level, ratio, cm, layers, growth, mhash, surface_cell_mm,
           layers_disclosure=False):
    """Print every item with its measured value beside it, IN THREE CLASSES, and return the
    BLOCKING failures only.

    THE CLASSES ARE NOT COSMETIC.  Sanaa's section 5 contains a sentence that begins
    "Quality gates:" and enumerates EXACTLY THREE: non-orthogonality below 70 deg, skewness
    below 4, cell-volume growth capped at 1.25.  The prism-layer clause sits in the PRECEDING
    sentence, a list of instructions to the generator, and that clause also contains the y+
    target -- which cannot be an achieved gate, because section 6.5 routes y+ to the
    certificate AFTER the design-point solve.  She drew the line herself, with punctuation.
    (cfd-supervisor ruling, 2026-09-13, made from her byte-exact text.)

      (A) HER THREE NAMED QUALITY GATES         -- BLOCK
      (B) LAB CORRECTNESS CHECKS                -- BLOCK, and they are NOT hers; they are
          named as the lab's own, because a mesh with negative volumes cannot be solved and
          a mismatched cyclic pair returns a confidently wrong KT with no residual signature
      (C) DISCLOSURES                           -- NEVER BLOCK, always a NUMBER

    A DISCLOSURE IS A NUMBER, NEVER AN ADJECTIVE, and it is printed so it cannot be read as
    a pass: the certificate says which KIND of item it is holding.
    """
    fails = []

    def g(name, val, gate, ok, unit='', note=''):
        verdict = 'PASS' if ok else 'GATE FAIL'
        if not ok:
            fails.append(f'{name}: {val} against {gate}')
        print(f'  {name:<34} {val:>14}   gate {gate:<14} {verdict}  {note}')

    print(f'\nBIRTH CERTIFICATE -- level {level} (family ratio {ratio})')
    print(f'  {"cells":<34} {cm["cells"]:>14}   (family target, context, not a gate)')
    print(f'  {"mesh sha256":<34} {mhash}')

    # RECORDED MESH PROPERTIES -- not gates, not disclosures of a shortfall. Things that were
    # FREE TO CHOOSE and are now FIXED, which a reader comparing this passage against another
    # implementation -- or against the full-360 check of section 5 -- must be able to see
    # without reading the mesh.
    print('\n  RECORDED MESH PROPERTIES -- free to choose, now fixed, stated as numbers')
    if _PHASE is None:
        print('    wedge phase                   NOT READABLE from make_blockmesh.py -- '
              'REFUSING to assert a value')
    else:
        print(f'    wedge phase                   {_PHASE:.4f} deg about x; periodic planes '
              f'at {_PHASE-36.0:+.4f} and {_PHASE+36.0:+.4f} deg')
        print(f'    minimum clearance, plane to blade   {PHASE_CLEARANCE_DEG:.4f} deg')
        print(f'      basis: {PHASE_CLEARANCE_BASIS}')
        print(f'      one blade occupies {BLADE_ANGULAR_WIDTH_DEG:.2f} deg of the 72 deg '
              f'passage; inter-blade gap {INTERBLADE_GAP_DEG:.4f} deg')
        print(f'      WHY IT IS NOT ZERO: built symmetric about theta = 0 the planes sat at')
        print(f'      -36.0000 and +36.0000 deg with clearance 0.0000 deg -- IN the blade -- '
              f'and')
        print(f'      snappyHexMesh died in layer addition at a face whose four corners were')
        print(f'      all at theta = -36.0000 deg, r = 110.6 mm. Reproduced on TWO independent')
        print(f'      tessellations. A periodic plane cutting a blade is not physically wrong;')
        print(f'      snappy simply cannot extrude layers through a wall ending on a cyclic.')

    print('\n  (A) SANAA SECTION 5 QUALITY GATES -- these BLOCK')
    g('max non-orthogonality (deg)', f'{cm["nonortho"]:.4f}', '< 70',
      cm['nonortho'] < GATE_NONORTHO)
    g('max skewness', f'{cm["skewness"]:.4f}', '< 4', cm['skewness'] < GATE_SKEWNESS)
    worst, wf, n_over, nfaces = growth
    g('max adj. cell volume ratio', f'{worst:.4f}', '<= 1.25', worst <= GATE_VOLGROWTH,
      note=f'{n_over} of {nfaces} internal faces over the cap')
    print('\n  (B) LAB CORRECTNESS CHECKS -- these BLOCK, and they are the LAB\'S, not hers')
    g('min cell volume (m3)', f'{cm["minvol"]:.6g}', '> 0', cm['minvol'] > 0)
    g('CORRECTNESS: cyclic point match', f'{cm["cyclic_match"]:.6g}', '< 1e-6',
      cm['cyclic_match'] < GATE_CYCLIC_MATCH,
      note='NOT a quality metric -- a mismatched periodic pair returns a confidently '
           'wrong KT with no residual signature')

    # TIP-CHORD RESOLUTION -- class (B), BLOCKING, and THE LAB'S OWN not hers.
    # cfd-supervisor ruling 2026-09-13: a layer shortfall at a sharp trailing edge degrades
    # gracefully and is ordinary; a FEATURE-RESOLUTION shortfall says the geometry the
    # physics turns on is not resolved, and a propeller's tip vortex is exactly that physics.
    # It is held strict WHILE IT COSTS NOTHING -- it clears by 10.4x at coarse -- because
    # loosening a clause while nothing turns on it is how a standard is lost.
    tip_cells_b = C_TIP_MM / surface_cell_mm
    g('cells across tip chord', f'{tip_cells_b:.1f}', '>= 6', tip_cells_b >= GATE_TIP_CELLS,
      note=f'c_tip = {C_TIP_MM} mm; {C_TIP_BASIS}')

    print('\n  (C) DISCLOSURES -- these NEVER block, and each is a NUMBER')
    print(f'  {"max aspect ratio":<34} {cm["aspect"]:>14.4f}   advisory '
          f'{ADVISORY_ASPECT:g}        DISCLOSED (never a lone rejection)')
    mode = 'DISCLOSED, not gating' if layers_disclosure else 'GATE'
    ach = layers.get('_achieved', {}) if isinstance(layers, dict) else {}
    req = layers.get('_requested', {}) if isinstance(layers, dict) else {}
    print(f'  prism layers -- dictionary asks {GATE_LAYERS} at ratio {GATE_EXPANSION} '
          f'[{mode}]:')
    if layers_disclosure:
        print('    Reading A (SPECIFICATION) governs by supervisor ruling: the registered')
        print('    requirement is on the DICTIONARY. ACHIEVED coverage is reported below and')
        print('    a shortfall CAPS THE FIDELITY CHIP; it does not move a band.')
    print('    ACHIEVED -- from the extrusion counters and the cell delta, NEVER from the')
    print('    per-patch table, which is the REQUEST. A table reading "6 layers" has been')
    print('    measured on a mesh with ZERO layers and an rc of 0.')
    fx, ft = ach.get('faces_extruded'), ach.get('faces_total')
    ca, cw = ach.get('cells_added'), ach.get('cells_wanted')
    dl = ach.get('cell_delta')
    if fx is not None:
        print(f'      faces extruded                {fx:>12,} of {ft:,}  '
              f'({ach.get("faces_pct"):.1f} %)')
    if ca is not None:
        print(f'      layer cells added             {ca:>12,} of {cw:,}  '
              f'({ach.get("cells_pct"):.1f} %)')
    if dl is not None:
        print(f'      cell count delta, snapped -> layered   {dl:>+12,}')
    # THE THREE MUST AGREE. They are independent readings of one fact.
    if ach.get('unknown'):
        print('      *** LAYER OUTCOME UNKNOWN. The layer phase ended before printing any')
        print('          extrusion counter, so there is NO EVIDENCE either way. The')
        print('          per-patch table below is the REQUEST and is NOT read as an')
        print('          achievement. This is "unknown", not "zero" and not "achieved".')
    zero = [n for n, v in (('faces extruded', fx), ('cells added', ca),
                           ('cell delta', dl)) if v == 0]
    nonzero = [n for n, v in (('faces extruded', fx), ('cells added', ca),
                              ('cell delta', dl)) if v not in (0, None)]
    if zero and nonzero:
        fails.append(f'layer counters DISAGREE: {zero} say zero while {nonzero} do not')
        print(f'      *** THE COUNTERS DISAGREE: {zero} zero, {nonzero} non-zero. '
              f'REFUSING to report a coverage.')
    elif zero:
        print(f'      -> NO PRISM LAYER EXISTS ON THIS MESH. Coverage 0.0 % on every patch.')
        print(f'         The per-patch table below is what was ASKED FOR and was NOT achieved.')
    for p in LAYER_PATCHES:
        d = req.get(p)
        if d is None:
            print(f'    {p:<32} {"not in the request table":>26}')
        elif ach.get('unknown'):
            print(f'    {p:<32} {"UNKNOWN":>26}   (requested {d["layers"]:.0f} on '
                  f'{d["faces"]} faces; no extrusion counter in the log)')
            continue
        else:
            got = 0.0 if zero else d['layers']
            cov = 100.0 * got / GATE_LAYERS
            ok = got >= GATE_LAYERS - 1e-9
            if ok:
                verdict = 'SPECIFICATION MET'
            elif layers_disclosure:
                verdict = 'SPEC SHORT -- DISCLOSED, NOT A GATE'
            else:
                verdict = 'GATE FAIL'
                fails.append(f'layers[{p}]: {got}')
            print(f'    {p:<32} {got:>8.2f} of {GATE_LAYERS} nominal, '
                  f'coverage {cov:5.1f} %   {verdict}')
            print(f'      {"":<30} (requested on {d["faces"]} faces)')

    le_cells = R_LE_MM / surface_cell_mm
    tip_cells = C_TIP_MM / surface_cell_mm
    le_ok = le_cells >= GATE_LE_CELLS
    print(f'  {"cells across LE radius":<34} {le_cells:>14.3f}   asks >= 8        '
          f'{"SPECIFICATION MET" if le_ok else "SPEC SHORT -- DISCLOSED, NOT A GATE"}')
    if not le_ok:
        # The LITERAL parse asks for 8 cells across the RADIUS; the conventional reading for
        # a rounded nose asks 8 across the DIAMETER, i.e. 4 across the radius. Both printed.
        print(f'      shortfall {GATE_LE_CELLS/le_cells:.2f}x on the LITERAL parse '
              f'(needs cell <= {R_LE_MM/GATE_LE_CELLS:.4f} mm, has '
              f'{surface_cell_mm:.4f} mm); '
              f'{"MET" if le_cells >= GATE_LE_CELLS/2 else f"{GATE_LE_CELLS/2/le_cells:.2f}x"}'
              f' on the conventional one (cell <= R/4)')
    print(f'      R_LE = {R_LE_MM} mm at {R_LE_STATION}')
    print(f'      surface cell {surface_cell_mm:.4f} mm. ADDENDUM E.5 registered the LITERAL '
          f'parse as GOVERNING and')
    print(f'      E.6 accepted route 2 -- build as registered, DISCLOSE the limitation. This '
          f'ruling does')
    print(f'      NOT extend from the prism-layer clause by analogy; it predates it.')
    # MOVED OUT OF (C) -- it is printed in class (B) above. Left here only as a pointer so
    # a reader scanning the disclosures does not conclude it was dropped.
    print('  cells across tip chord            -- see class (B): the lab holds this one '
          'STRICT and BLOCKING')
    return fails


def selftest() -> int:
    """PLANTED CONTROL. Each numeric gate is fed a value known to be out, and must FAIL.
    A gate never shown able to fail is not known to work (standing rule 3)."""
    ok = True
    base_cm = dict(cells=1, nonortho=10.0, skewness=1.0, aspect=10.0, minvol=1e-9,
                   cyclic_match=1e-9, neg_vol_flagged=False)
    def L(layers_got, extruded=1, total=1, added=1, wanted=1, delta=1):
        return dict(_requested={p: dict(faces=1, layers=layers_got, thickness=1.0)
                                for p in LAYER_PATCHES},
                    _achieved=dict(faces_extruded=extruded, faces_total=total,
                                   faces_pct=100.0 * extruded / max(total, 1),
                                   cells_added=added, cells_wanted=wanted,
                                   cells_pct=100.0 * added / max(wanted, 1),
                                   cell_delta=delta))
    base_layers = L(6.0)
    base_growth = (1.10, -1, 0, 1)
    clean = report('SELFTEST-CLEAN', 1.0, base_cm, base_layers, base_growth, 'x' * 64, 0.10)
    if clean:
        print(f'SELFTEST FAIL: the clean control produced failures {clean}')
        return 2
    print('  -> clean control produced ZERO failures, as required')

    plants = [
        ('non-orthogonality', dict(base_cm, nonortho=70.0), base_layers, base_growth, 0.10),
        ('skewness', dict(base_cm, skewness=4.0), base_layers, base_growth, 0.10),
        ('volume growth', base_cm, base_layers, (1.2500001, -1, 1, 1), 0.10),
        ('negative volume', dict(base_cm, minvol=-1e-20), base_layers, base_growth, 0.10),
        ('layers', base_cm, L(5.99), base_growth, 0.10),
        # 🔴 THE DECOY THAT CAUGHT THE REAL DEFECT: a request table saying SIX layers while
        # every achievement counter says ZERO. Under the old parser this read
        # "coverage 100.0 %, SPECIFICATION MET". It must now read zero.
        ('table says 6 but nothing was extruded', base_cm,
         L(6.0, extruded=0, total=76465, added=0, wanted=458790, delta=0),
         base_growth, 0.10),
        ('cyclic mismatch', dict(base_cm, cyclic_match=1.0e-6), base_layers, base_growth,
         0.10),
        # tip-chord resolution is class (B) and BLOCKS: a cell just over c_tip/6 must fire it
        ('tip-chord resolution', base_cm, base_layers, base_growth,
         C_TIP_MM / GATE_TIP_CELLS * 1.001),
    ]
    # The LE and prism-layer plants are DELIBERATELY ABSENT from the blocking list: after the
    # cfd-supervisor's 2026-09-13 ruling those are DISCLOSURES and must NOT append to the
    # blocking set. Their plant is the opposite assertion -- a planted shortfall must NOT
    # block -- and it is exercised below, because a disclosure that quietly blocks is as much
    # a defect as a gate that quietly passes.
    for name, cm, ly, gr, sc in plants:
        f = report(f'SELFTEST-PLANT[{name}]', 1.0, cm, ly, gr, 'x' * 64, sc)
        if not f:
            print(f'SELFTEST FAIL: the planted {name} defect did NOT fire the gate')
            ok = False
        else:
            print(f'  -> planted {name} defect FIRED: {f}')
    for name, sc, ly in (('LE resolution', R_LE_MM / 7.999, base_layers),
                         ('prism layers',  0.10, L(4.70))):
        f = report(f'SELFTEST-DISCLOSURE[{name}]', 1.0, base_cm, ly, base_growth,
                   'x' * 64, sc, layers_disclosure=True)
        if f:
            print(f'SELFTEST FAIL: a planted {name} shortfall BLOCKED, and it must only '
                  f'be disclosed: {f}')
            ok = False
        else:
            print(f'  -> planted {name} shortfall correctly DISCLOSED and did NOT block')
    print('\nSELFTEST ' + ('PASS' if ok else 'FAIL'))
    return 0 if ok else 2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--case')
    ap.add_argument('--level', default='coarse')
    ap.add_argument('--ratio', type=float, default=1.0)
    ap.add_argument('--checkmesh-log', default=None)
    ap.add_argument('--snappy-log', default=None)
    ap.add_argument('--background-mm', type=float, default=20.0)
    ap.add_argument('--blade-level', type=int, default=5)
    ap.add_argument('--layers-disclosure', action='store_true',
                    help='report achieved prism-layer coverage as a DISCLOSURE rather than '
                         'as a blocking gate. THE DEFAULT IS THE STRICTER READING and this '
                         'flag exists only to carry an explicit supervisor ruling on which '
                         'parse of section 6.3 governs -- it is never a lane\'s choice, for '
                         'the same reason ADDENDUM E.5 registered the LITERAL parse of the '
                         'leading-edge clause as governing: adopting the gentler reading '
                         'merely because it is gentler is the error that record exists to '
                         'prevent.')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if not a.case:
        print('REFUSE: --case is required unless --selftest is given')
        return 2

    try:
        cm = parse_checkmesh(a.checkmesh_log or os.path.join(a.case, 'log.checkMesh'))
        layers = parse_layers(a.snappy_log or os.path.join(a.case, 'log.snappyHexMesh'))
        growth = volume_growth(a.case)
        mhash = mesh_hash(a.case)
    except Refusal as exc:
        print(f'REFUSE: {exc}')
        return 2

    sc = (a.background_mm / a.ratio) / 2 ** a.blade_level
    fails = report(a.level, a.ratio, cm, layers, growth, mhash, sc,
                   layers_disclosure=a.layers_disclosure)
    if fails:
        print(f'\nMESH ADMISSIBILITY: NOT ADMISSIBLE -- {len(fails)} gate(s) failed:')
        for f in fails:
            print(f'    {f}')
        return 3
    print('\nMESH ADMISSIBILITY: ADMISSIBLE -- every registered gate passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
