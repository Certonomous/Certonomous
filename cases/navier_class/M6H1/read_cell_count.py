#!/usr/bin/env python3
"""M6H1 H-G1 instrument -- read the ACHIEVED cell count and the mesh-quality numbers
from a case's OWN `checkMesh -allGeometry -allTopology` log, and grade them against
M6H1_PREREGISTRATION.md section 4's PREDICTED counts and section 7's H-G1 thresholds.

WHAT SECTION 4 REGISTERS: "These are PREDICTIONS from the dictionaries, registered
before the build, and section 7's H-G1 grades the ACHIEVED counts against them.  A
number computed from the input dict is not an observation of the output -- the
achieved counts come from checkMesh's own `cells:` line."  This instrument reads that
line and nothing else for the graded number.

WHAT SECTION 10 WARNS ABOUT, MADE EXECUTABLE:
    "cell-count reader (H-G1) | corrupt checkMesh's `cells:` line in a copy and
     re-read | the count-extraction regex | **`len(owner)` is `nFaces` and is used
     NOWHERE**"
`constant/polyMesh/owner` has one entry PER FACE.  Its length is nFaces, ~4x the cell
count on a hex mesh, and a reader that took it for a cell count would return a
confident FALSE NUMBER -- not a zero, so a planted zero could never catch it.  This
instrument NEVER derives the cell count from owner's length.  It uses owner for one
thing only, and says so at the use site: owner's FoamFile `note` carries an
INDEPENDENT `nCells:` written by the mesher, and the log's `cells:` is asserted
against it.

PLANTED CONTROLS (rule 3).  Both plant INTO THE INPUT -- they corrupt a COPY OF THE
LOG ON DISK and RE-RUN the real reader on that copy.

  PLANT A -- SENSITIVITY.  Replace the Mesh stats `cells:` value with a known number
  in the copy.  The reported count MUST become that number.
  Code path exercised: read_checkmesh()'s Mesh-stats block isolation and the anchored
  `^\\s*cells:\\s+(\\d+)\\s*$` count-extraction regex -- the path that produces the
  graded number.

  PLANT B -- DISCRIMINATION (the decoy the regex must NOT read).  Corrupt the
  `hexahedra:` count under "Overall number of cells of each type:" instead, leaving
  the Mesh stats `cells:` line untouched.  The reported count MUST NOT move.  A loose
  regex such as `cells.*?(\\d+)` latches onto the "Overall number of cells of each
  type:" heading and its following block; this plant refuses such a reader.
  It has a second job: because the type block must SUM to `cells:`, corrupting it also
  proves the internal-consistency assertion is live rather than decorative.

THE SAME-RUN ASSERTION -- WHY THIS READER CAN DECLINE RATHER THAN EMIT A NUMBER.
A checkMesh log is a separate file from the mesh it describes; a log left over from a
previous level parses perfectly and yields a plausible count for the wrong mesh.  So
before any number is emitted, the log is asserted against the polyMesh ON DISK:
  (i)   log `points:`  ==  the count header of constant/polyMesh/points
  (ii)  log `faces:`   ==  the count header of constant/polyMesh/owner   <-- THIS IS
        nFaces, and it is used HERE AND ONLY HERE, as an assertion, never as a count
        of cells (section 10)
  (iii) log `cells:`   ==  owner's FoamFile note `nCells:`, written independently by
        the mesher
  (iv)  log `internal faces:` + sum of boundary nFaces  ==  log `faces:`
  (v)   the cell-type counts sum to log `cells:`
  (vi)  the log is NOT OLDER than constant/polyMesh/owner -- a log that predates the
        mesh it claims to describe is a log of a different mesh (the age-guard
        principle of rule 4, applied to an instrument's input)
Any failure -> DECLINE (exit 2).  A mismatched pair is not graded down; it is not
graded at all.

Exit codes:  0 PASS   1 NOT A RESULT for that level (section 7's H-G1 label)   2 REFUSE/DECLINE
"""
import sys, os, re, shutil, tempfile

# --- REGISTERED IN ADVANCE (M6H1_PREREGISTRATION.md sections 4, 7). Do not edit to fit. ---
PREDICTED_CELLS = {'H-L1': 1241600, 'H-L2': 2793600, 'H-L3': 4966400}
COUNT_TOL       = 0.02      # H-G1: achieved cell count within +/- 2 % of section 4
MAX_NONORTHO    = 70.0      # H-G1
MAX_SKEWNESS    = 4.0       # H-G1
# H-G1 also requires pyHyp Min Quality > 0 at every layer. That lives in the pyHyp log,
# not in checkMesh, and is graded by its own reader -- NOT silently assumed here.
# ------------------------------------------------------------------------------------------

CELLS_RE = re.compile(r'^\s*cells:\s+(\d+)\s*$', re.M)      # ANCHORED. See PLANT B.
_STAT_RE = lambda k: re.compile(r'^\s*%s:\s+(\d+)\s*$' % re.escape(k), re.M)
TYPE_KEYS = ('hexahedra', 'prisms', 'wedges', 'pyramids', 'tet wedges', 'tetrahedra', 'polyhedra')


def _mesh_stats_block(txt):
    """Isolate the `Mesh stats` block. The graded count is extracted from THIS block
    only -- never from the whole file, where 'Overall number of cells of each type:'
    also contains the word 'cells'."""
    m = re.search(r'^Mesh stats\s*$', txt, re.M)
    if not m:
        return None
    rest = txt[m.end():]
    e = re.search(r'^\S', rest, re.M)
    return rest[:e.start()] if e else rest


def read_checkmesh(path):
    """Read a checkMesh log FROM DISK. Returns (dict, [errors])."""
    txt = open(path).read()
    err, out = [], {}
    blk = _mesh_stats_block(txt)
    if blk is None:
        return None, ["no 'Mesh stats' block in %s -- this is not a checkMesh log" % path]
    m = CELLS_RE.search(blk)
    if not m:
        return None, ["no anchored 'cells:' line inside the Mesh stats block of %s" % path]
    out['cells'] = int(m.group(1))
    for k in ('points', 'faces', 'internal faces'):
        mm = _STAT_RE(k).search(blk)
        out[k] = int(mm.group(1)) if mm else None
    tm = re.search(r'^Overall number of cells of each type:\s*$', txt, re.M)
    types = {}
    if tm:
        rest = txt[tm.end():]
        e = re.search(r'^\S', rest, re.M)
        tb = rest[:e.start()] if e else rest
        for k in TYPE_KEYS:
            mm = re.search(r'^\s*%s:\s+(\d+)\s*$' % re.escape(k), tb, re.M)
            if mm:
                types[k] = int(mm.group(1))
    out['types'] = types
    # NUMBER PATTERN, NOT A CHARACTER CLASS.  checkMesh writes "Min volume = 4.16e-11."
    # -- a SENTENCE PERIOD follows the number.  A class like [-\d.eE+]+ swallows it and
    # float() then raises on '4.16e-11.'.  This instrument's own selftest caught that
    # before it ever read a real log; it is recorded here so it is not reintroduced.
    NUM = r'(-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)'
    mo = re.search(r'Mesh non-orthogonality Max:\s*' + NUM, txt)
    out['nonortho'] = float(mo.group(1)) if mo else None
    ms = re.search(r'Max skewness\s*=\s*' + NUM, txt)
    out['skew'] = float(ms.group(1)) if ms else None
    mv = re.search(r'Min volume\s*=\s*' + NUM, txt)
    out['minvol'] = float(mv.group(1)) if mv else None
    out['negvol_marker'] = bool(re.search(r'\*\*\*(Zero or negative cell volume|Error in face pyramids)', txt))
    out['failed_checks'] = bool(re.search(r'^\s*Failed \d+ mesh checks\.', txt, re.M))
    out['mesh_ok'] = bool(re.search(r'^Mesh OK\.\s*$', txt, re.M))
    return out, err


def _foam_body_count(path):
    """Return the list length written in an OpenFOAM field/list body (the bare integer
    on its own line immediately before the opening '('), read FROM DISK."""
    with open(path, 'rb') as f:
        head = f.read(400000).decode('utf-8', 'replace')
    m = re.search(r'^\s*(\d+)\s*$\s*^\s*\(', head, re.M)
    return int(m.group(1)) if m else None


def _owner_note(path):
    """Return the mesher-written FoamFile note counts of constant/polyMesh/owner."""
    with open(path, 'rb') as f:
        head = f.read(20000).decode('utf-8', 'replace')
    m = re.search(r'\bnote\s+"([^"]*)"', head)
    if not m:
        return {}
    return {k: int(v) for k, v in re.findall(r'(nPoints|nCells|nFaces|nInternalFaces):\s*(\d+)',
                                             m.group(1))}


def _boundary_nfaces_sum(polymesh):
    p = os.path.join(polymesh, 'boundary')
    if not os.path.isfile(p):
        return None
    return sum(int(x) for x in re.findall(r'\bnFaces\s+(\d+)\s*;', open(p).read()))


def same_run(stats, log_path, polymesh):
    """Assert the log and the polyMesh describe ONE mesh. Returns a list of failures."""
    bad = []
    pts = os.path.join(polymesh, 'points')
    own = os.path.join(polymesh, 'owner')
    if not os.path.isfile(own):
        return ["no %s -- the second source of the same-run assertion is absent" % own]

    if os.path.isfile(pts):
        n = _foam_body_count(pts)
        if n is not None and stats.get('points') is not None and n != stats['points']:
            bad.append("log says points: %d, constant/polyMesh/points holds %d -- the log and "
                       "the mesh are NOT the same mesh" % (stats['points'], n))
    # (ii) owner's LENGTH is nFaces. It is used HERE AND ONLY HERE, as an assertion on
    #      faces. It is NEVER the cell count (section 10).
    nf = _foam_body_count(own)
    if nf is not None and stats.get('faces') is not None and nf != stats['faces']:
        bad.append("log says faces: %d, len(owner) is %d -- NOT the same mesh. "
                   "(len(owner) is nFaces; it is never used as a cell count.)"
                   % (stats['faces'], nf))
    # (iii) owner's note carries an INDEPENDENT nCells written by the mesher.
    note = _owner_note(own)
    if 'nCells' in note and note['nCells'] != stats['cells']:
        bad.append("log says cells: %d, owner's FoamFile note says nCells:%d -- two independent "
                   "sources disagree on the cell count of this mesh"
                   % (stats['cells'], note['nCells']))
    # (iv) internal faces + boundary faces == faces
    bsum = _boundary_nfaces_sum(polymesh)
    if bsum is not None and stats.get('internal faces') is not None and stats.get('faces') is not None:
        if stats['internal faces'] + bsum != stats['faces']:
            bad.append("log internal faces %d + boundary nFaces %d = %d != log faces %d -- the "
                       "log is internally inconsistent with the boundary file"
                       % (stats['internal faces'], bsum, stats['internal faces'] + bsum,
                          stats['faces']))
    # (v) cell types must sum to cells
    if stats['types']:
        s = sum(stats['types'].values())
        if s != stats['cells']:
            bad.append("cell types sum to %d but the Mesh stats cells: line says %d -- the log's "
                       "two internal statements of the cell count disagree" % (s, stats['cells']))
    # (vi) age guard on the instrument's own input
    try:
        if os.path.getmtime(log_path) < os.path.getmtime(own) - 1.0:
            bad.append("the log is OLDER than constant/polyMesh/owner -- it describes a mesh "
                       "written before this one (age guard, rule 4's principle)")
    except OSError:
        pass
    return bad


# ------------------------------------------------------------------ planted controls
def planted_controls(log_path, plant_cells=987654321, decoy_delta=7777):
    """PLANT A (sensitivity on the count-extraction regex) and PLANT B (the decoy the
    regex must NOT read), both into a COPY OF THE LOG ON DISK, real reader re-run."""
    out = []
    clean, err = read_checkmesh(log_path)
    if clean is None:
        return False, err
    out.append("clean: checkMesh Mesh-stats cells: = %d" % clean['cells'])
    if plant_cells == clean['cells']:
        plant_cells += 1

    d = tempfile.mkdtemp(prefix='m6h1_cm_')
    # ---- PLANT A ----
    a = os.path.join(d, 'log.A')
    txt = open(log_path).read()
    new, n = CELLS_RE.subn('    cells:           %d' % plant_cells, txt, count=1)
    open(a, 'w').write(new)
    pa, _ = read_checkmesh(a)
    moved_a = pa is not None and pa['cells'] != clean['cells']
    exact_a = pa is not None and pa['cells'] == plant_cells
    seen_a = bool(n == 1 and moved_a and exact_a)
    out.append("PLANT A (sensitivity): rewrote the Mesh-stats cells: line to %d in a COPY ON "
               "DISK (%d substitution(s))" % (plant_cells, n))
    out.append("   re-read from disk: cells = %s   clean %d   expected %d"
               % (pa['cells'] if pa else 'UNREADABLE', clean['cells'], plant_cells))
    out.append("   MOVED off clean: %s    moved to the PREDICTED value: %s    SEEN: %s"
               % (moved_a, exact_a, seen_a))
    if n != 1:
        out.append("   NOT A PLANT: the cells: line was not substituted exactly once, so nothing "
                   "was planted and nothing can be detected.")

    # ---- PLANT B ----
    seen_b, note_b = False, 'no cell-type block in the log -- the decoy cannot be planted'
    if clean['types']:
        key = max(clean['types'], key=lambda k: clean['types'][k])
        b = os.path.join(d, 'log.B')
        newv = clean['types'][key] + decoy_delta
        nb = re.subn(r'^(\s*%s:\s+)\d+\s*$' % re.escape(key), r'\g<1>%d' % newv, txt,
                     count=1, flags=re.M)
        open(b, 'w').write(nb[0])
        pb, _ = read_checkmesh(b)
        moved = pb is None or pb['cells'] != clean['cells']
        seen_b = (nb[1] == 1) and (not moved)
        note_b = ("changed the DECOY '%s:' line under 'Overall number of cells of each type:' "
                  "from %d to %d in a COPY ON DISK (%d substitution(s)); cells re-read as %s "
                  "(clean %d) -- graded count UNMOVED: %s"
                  % (key, clean['types'][key], newv, nb[1],
                     pb['cells'] if pb else 'UNREADABLE', clean['cells'], not moved))
    out.append("PLANT B (decoy the regex must NOT read): " + note_b)
    shutil.rmtree(d, ignore_errors=True)

    ok = seen_a and seen_b
    if not seen_a:
        out.append("   REFUSE: the reader did not see a known change to its own input. Its clean "
                   "number is NOT evidence (rule 3).")
    if not seen_b:
        out.append("   REFUSE: the count-extraction regex is reading the 'Overall number of cells "
                   "of each type' block, or the decoy could not be planted. An undiscriminated "
                   "count is not evidence.")
    return ok, out


# ------------------------------------------------------------------ selftest
SYNTH = """/*---------------------------------------------------------------------------*/
Create mesh for time = constant

Time = constant

Mesh stats 
    points:           1052929
    internal points:  0
    faces:            2097280
    internal faces:   1044352
    cells:            524288
    faces per cell:   6
    boundary patches: 2
    point zones:      0

Overall number of cells of each type:
    hexahedra:     520192
    prisms:        4096
    wedges:        0
    pyramids:      0
    tet wedges:    0
    tetrahedra:    0
    polyhedra:     0

Checking geometry...
    Max aspect ratio = 2.00000048739 OK.
    Min volume = 4.16118785118e-11. Max volume = 1.06110290203e-08.  Cell volumes OK.
    Mesh non-orthogonality Max: 12.5 average: 4.1
    Non-orthogonality check OK.
    Max skewness = 0.333332683483 OK.

Mesh OK.

End
"""


def _synth(root, cells=524288, faces=2097280, points=1052929, ifaces=1044352, bnd=(1048576, 4352)):
    os.makedirs(os.path.join(root, 'constant', 'polyMesh'), exist_ok=True)
    log = os.path.join(root, 'log.checkMesh')
    open(log, 'w').write(SYNTH)
    pm = os.path.join(root, 'constant', 'polyMesh')
    with open(os.path.join(pm, 'points'), 'w') as f:
        f.write('FoamFile\n{\n    object points;\n}\n\n%d\n(\n(0 0 0)\n)\n' % points)
    with open(os.path.join(pm, 'owner'), 'w') as f:
        f.write('FoamFile\n{\n    note        "nPoints:%d  nCells:%d  nFaces:%d  '
                'nInternalFaces:%d";\n    object owner;\n}\n\n%d\n(\n0\n)\n'
                % (points, cells, faces, ifaces, faces))
    with open(os.path.join(pm, 'boundary'), 'w') as f:
        f.write('FoamFile\n{\n    object boundary;\n}\n\n2\n(\n')
        for i, n in enumerate(bnd):
            f.write('    p%d\n    {\n        type wall;\n        nFaces %d;\n        '
                    'startFace 0;\n    }\n' % (i, n))
        f.write(')\n')
    return log, pm


def selftest():
    d = tempfile.mkdtemp(prefix='m6h1_cm_self_')
    log, pm = _synth(os.path.join(d, 'ok'))

    print("ARM 1 -- PLANT APPLIED, sound reader: both controls must be SEEN")
    ok1, msg = planted_controls(log)
    for m in msg:
        print("   " + m)
    print("   -> %s (expected DETECTED)" % ('DETECTED' if ok1 else 'NOT DETECTED'))

    print("\nARM 2 -- PLANT WITHHELD: plant the value the log ALREADY holds, so the input is")
    print("         rewritten but UNCHANGED. The control must report NOT DETECTED.")
    clean, _ = read_checkmesh(log)
    d2 = tempfile.mkdtemp(prefix='m6h1_cm_wh_')
    w = os.path.join(d2, 'log.W')
    open(w, 'w').write(CELLS_RE.sub('    cells:           %d' % clean['cells'], open(log).read()))
    pw, _ = read_checkmesh(w)
    withheld_ok = (pw['cells'] == clean['cells'])
    print("   rewrote the cells: line with its OWN value %d; re-read %d; MOVED: %s"
          % (clean['cells'], pw['cells'], pw['cells'] != clean['cells']))
    print("   -> %s (expected NOT DETECTED -- no plant, no signal)"
          % ('DETECTED' if pw['cells'] != clean['cells'] else 'NOT DETECTED'))
    shutil.rmtree(d2, ignore_errors=True)

    print("\nARM 3 -- LOOSE REGEX reader (`cells.*?(\\d+)`, which latches onto 'Overall number")
    print("         of cells of each type:'): PLANT B must REFUSE it")
    g = globals()
    saved = g['read_checkmesh']

    def loose(path):
        txt = open(path).read()
        m = re.search(r'cells[^0-9]*?(\d+)', txt[txt.index('Overall number'):], re.S)
        base, e = saved(path)
        if base is None:
            return None, e
        base = dict(base)
        base['cells'] = int(m.group(1))      # reads the hexahedra count. A FALSE NUMBER.
        return base, e
    g['read_checkmesh'] = loose
    ok3, msg = planted_controls(log)
    g['read_checkmesh'] = saved
    for m in msg:
        print("   " + m)
    print("   -> %s (expected NOT DETECTED -- PLANT B catches the decoy read)"
          % ('DETECTED' if ok3 else 'NOT DETECTED'))

    print("\nARM 4 -- BLINDED reader (ignores its input): PLANT A must REFUSE it")
    frozen = saved(log)
    g['read_checkmesh'] = lambda p: frozen
    ok4, msg = planted_controls(log)
    g['read_checkmesh'] = saved
    print("   " + msg[-1])
    print("   -> %s (expected NOT DETECTED)" % ('DETECTED' if ok4 else 'NOT DETECTED'))

    print("\nARM 5 -- SAME-RUN: a log whose cells: disagrees with owner's note nCells must DECLINE")
    log5, pm5 = _synth(os.path.join(d, 'mismatch'), cells=524200)
    s5, _ = read_checkmesh(log5)
    bad5 = same_run(s5, log5, pm5)
    for x in bad5:
        print("   " + x)
    ok5 = any('nCells' in x for x in bad5)
    print("   -> %s (expected DECLINE)" % ('DECLINE' if ok5 else 'NO DECLINE -- DEFECT'))

    print("\nARM 6 -- SAME-RUN: len(owner) is nFaces, and taking it for a cell count would give")
    print("         %d instead of %d -- a CONFIDENT FALSE NUMBER a planted zero cannot catch."
          % (2097280, 524288))
    print("   this instrument's graded count comes from the Mesh-stats cells: line: %d"
          % read_checkmesh(log)[0]['cells'])
    print("   len(owner) read from disk: %d, used ONLY to assert log faces: %d"
          % (_foam_body_count(os.path.join(pm, 'owner')), read_checkmesh(log)[0]['faces']))
    ok6 = _foam_body_count(os.path.join(pm, 'owner')) == read_checkmesh(log)[0]['faces'] \
        != read_checkmesh(log)[0]['cells']

    print("\nARM 7 -- SAME-RUN: a STALE log (older than the mesh) must DECLINE")
    log7, pm7 = _synth(os.path.join(d, 'stale'))
    os.utime(log7, (1, 1))
    s7, _ = read_checkmesh(log7)
    bad7 = same_run(s7, log7, pm7)
    for x in bad7:
        print("   " + x)
    ok7 = any('OLDER' in x for x in bad7)
    print("   -> %s (expected DECLINE)" % ('DECLINE' if ok7 else 'NO DECLINE -- DEFECT'))

    print("\nARM 8 -- a CLEAN log against its own mesh must NOT decline")
    s8, _ = read_checkmesh(log)
    bad8 = same_run(s8, log, pm)
    ok8 = not bad8
    print("   failures: %s -> %s" % (bad8 if bad8 else 'none',
                                     'NO DECLINE' if ok8 else 'FALSE DECLINE -- DEFECT'))

    shutil.rmtree(d, ignore_errors=True)
    good = ok1 and withheld_ok and (not ok3) and (not ok4) and ok5 and ok6 and ok7 and ok8
    print("\nSELFTEST %s" % ('PASS -- the controls SEE a real plant, do NOT see a withheld one, '
                             'REFUSE a loose regex that reads the decoy, REFUSE a blinded reader, '
                             'and the same-run assertion DECLINES on disagreement and staleness '
                             'while NOT declining on a matched pair' if good else 'FAIL'))
    return 0 if good else 1


# ------------------------------------------------------------------ main
def main(log_path, level, polymesh=None):
    print("M6H1 H-G1 -- achieved cell count and mesh quality, from the case's OWN checkMesh log")
    print("LOG: %s    LEVEL: %s" % (log_path, level))
    if level not in PREDICTED_CELLS:
        print("REFUSE (exit 2): %r is not one of section 4's registered levels %s"
              % (level, sorted(PREDICTED_CELLS)))
        return 2
    pred = PREDICTED_CELLS[level]
    print("REGISTERED PREDICTION (section 4, before the build): %d cells, graded at +/- %.0f %%\n"
          % (pred, 100 * COUNT_TOL))

    if not os.path.isfile(log_path):
        print("REFUSE (exit 2): no checkMesh log at %s." % log_path)
        return 2
    if polymesh is None:
        polymesh = os.path.join(os.path.dirname(os.path.abspath(log_path)), 'constant', 'polyMesh')

    ok, msg = planted_controls(log_path)
    print("PLANTED CONTROLS -- planted INTO THE INPUT, real reader re-run FROM DISK")
    for m in msg:
        print("  " + m)
    if not ok:
        print("\nREFUSE (exit 2): the controls did not establish that this reader reads the "
              "Mesh-stats cells: line and only that line. No number below would be evidence.")
        return 2

    stats, err = read_checkmesh(log_path)
    if stats is None:
        for e in err:
            print("  " + e)
        print("\nREFUSE (exit 2).")
        return 2

    print("\nSAME-RUN ASSERTION -- log against %s" % polymesh)
    if not os.path.isdir(polymesh):
        print("  no polyMesh at that path")
        print("\nDECLINE (exit 2): the log cannot be tied to a mesh on disk. A plausible cell "
              "count from an untied log is a confident FALSE NUMBER.")
        return 2
    bad = same_run(stats, log_path, polymesh)
    if bad:
        for b in bad:
            print("  " + b)
        print("\nDECLINE (exit 2): the log and the mesh do not describe one build.")
        return 2
    print("  points, faces (== len(owner), nFaces) and cells (== owner note nCells) all agree; "
          "type counts sum to cells; internal+boundary faces == faces; log not older than owner.")

    n = stats['cells']
    dev = abs(n - pred) / float(pred)
    print("\n  %-34s %14s" % ('ACHIEVED cells (Mesh stats line)', n))
    print("  %-34s %14d" % ('PREDICTED (section 4)', pred))
    print("  %-34s %13.2f %%" % ('deviation', 100 * dev))
    print("  %-34s %14s" % ('len(owner) = nFaces (NOT a count of cells)',
                            _foam_body_count(os.path.join(polymesh, 'owner'))))

    g_count = dev <= COUNT_TOL
    no = stats['nonortho']
    sk = stats['skew']
    mvol = stats['minvol']
    g_no = (no is not None) and (no <= MAX_NONORTHO)
    g_sk = (sk is not None) and (sk <= MAX_SKEWNESS)
    g_vol = (not stats['negvol_marker']) and (mvol is not None) and (mvol > 0.0)
    print("\n  %-34s %14s   gate %s" % ('max non-orthogonality', no, '<= %.0f' % MAX_NONORTHO))
    print("  %-34s %14s   gate %s" % ('max skewness', sk, '<= %.0f' % MAX_SKEWNESS))
    print("  %-34s %14s   gate %s" % ('min cell volume', mvol, '> 0, no negative-volume marker'))

    missing = [k for k, v in (('non-orthogonality', no), ('skewness', sk), ('min volume', mvol))
               if v is None]
    if missing:
        print("\nDECLINE (exit 2): %s absent from the log. checkMesh must be run with "
              "-allGeometry -allTopology; a gate on a number the log does not contain is not a "
              "gate." % ', '.join(missing))
        return 2

    all_ok = g_count and g_no and g_sk and g_vol
    print("\nH-G1 (cell count within +/- %.0f %%): %s" % (100 * COUNT_TOL, 'PASS' if g_count else
                                                          'NOT A RESULT for this level'))
    print("H-G1 (quality: non-ortho, skewness, negative volumes): %s"
          % ('PASS' if (g_no and g_sk and g_vol) else 'NOT A RESULT for this level'))
    print("H-G1 (pyHyp Min Quality > 0 at every layer): NOT GRADED HERE -- it lives in the pyHyp "
          "log and has its own reader. H-G1 is NOT discharged by this instrument alone.")
    print("\nH-G1, checkMesh portion: %s" % ('PASS' if all_ok else 'NOT A RESULT for this level'))
    return 0 if all_ok else 1


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--selftest':
        sys.exit(selftest())
    if len(sys.argv) < 3:
        sys.exit("usage: read_cell_count.py <log.checkMesh> <H-L1|H-L2|H-L3> [polyMesh_dir] "
                 "| --selftest")
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None))
