#!/usr/bin/env python3
"""M6H1 H-G0 / H-G2 instrument — measure the ONERA M6 trailing-edge BASE thickness
from a surface STL, in spanwise bands, and grade it against AGARD AR-138 Table B1-1.

REGISTERED REFERENCE (AGARD AR-138 Appendix B1, Table B1-1, PDF page B1-7, title-page
verified under rule 15):  z/l at x/l = 1.0 is 0.0007052, so the base is
2 x 0.0007052 = 0.0014104 of local chord = 0.1410 %.  It is NOT zero: the ONERA D
section closes on a finite base and a surface that closes it sharp is a departure
from the reference.

PLANTED CONTROL (rule 3).  The control plants into the INPUT -- it rewrites one
solid's z coordinates in a COPY OF THE STL ON DISK and re-runs the real reader on
that file.  It does NOT relabel a copy of the output, and it does NOT compare a copy
with its own source (a tautology that cannot fail -- L-555).

DISCRIMINATION CONTROL.  The plant touches only z; spanwise bands are assigned on y.
So the reported `chord` column must be UNCHANGED by the plant.  If chord moves, the
plant leaked into a path it was not meant to exercise and the control REFUSES.

ALL THREE OF §7's H-G0 CLAUSES ARE GRADED HERE, and until 2026-09-12 only the first was.
§7 registers: base thickness within +/-10 % of 0.1410 % of LOCAL chord at every one of >= 9
spanwise stations; **max t/c within +/-2 % of 9.79 %**; **semispan within +/-0.5 % of
1.1963 m**.  This instrument implemented the base clause alone and then printed
"H-G0 (surface fidelity ...): PASS", i.e. IT CLAIMED A GATE IT HAD NOT EVALUATED.  The
contrast that convicts it: `read_cell_count.py` announces its own missing clause on stdout,
so a reader knows H-G1 is not discharged by it; this one announced nothing.  Each added
clause carries its own plant, and each plant is the other's discrimination control.

Exit codes:  0 PASS   1 GATE FAIL (reported, never adjusted)   2 REFUSE (control failed)
"""
import sys, os, re, math, shutil, tempfile

# --- REGISTERED IN ADVANCE (M6H1_PREREGISTRATION.md §1.3, §7). Do not edit to fit. ---
REF_ZL_AT_TE   = 0.0007052       # AGARD AR-138 Table B1-1, final row
REF_T_TE_FRAC  = 2 * REF_ZL_AT_TE   # 0.0014104 of local chord
H_G0_TOL       = 0.10            # +/- 10 % of the reference base thickness
H_G2_MIN_CELLS = 8               # >= 8 cells across the base, every station
N_STATIONS     = 9
REF_TC_MAX     = 2 * 0.0489296   # §1.3: max z/l 0.0489296 -> t/c = 9.79 %
H_G0_TC_TOL    = 0.02            # §7 H-G0 clause 2: max t/c within +/- 2 % of 9.79 %
REF_SEMISPAN   = 1.1963          # §1.2 / AR-138 B1 §2.1.8, in metres
H_G0_SPAN_TOL  = 0.005           # §7 H-G0 clause 3: semispan within +/- 0.5 %
PLANT_TC       = 1.5             # the t/c plant factor, applied to the SURFACE solids' z
PLANT_SPAN     = 1.25            # the semispan plant factor, applied to y
MIN_PTS_PER_SLICE = 8            # a constant-y group with fewer points is not a section
MIN_SLICE_CHORD_FRAC = 0.2       # ... nor is one whose x extent is a fraction of the largest
PLANT_RTOL     = 1.0e-7          # the plants rewrite vertices with '%.9g', so an assertion
                                 # tighter than that round-trip cannot hold -- the same
                                 # class of defect as read_min_quality.py's PLANT A
# ------------------------------------------------------------------------------------

VRE = re.compile(r'^\s*vertex\s+(\S+)\s+(\S+)\s+(\S+)')


def load_stl(path):
    """Return {solid_name: [(x,y,z), ...]}. Reads ASCII STL from disk."""
    solids, cur = {}, None
    with open(path) as f:
        for line in f:
            s = line.strip()
            if s.startswith('solid'):
                parts = s.split(None, 1)
                cur = parts[1] if len(parts) > 1 else 'unnamed'
                solids.setdefault(cur, [])
            m = VRE.match(line)
            if m and cur is not None:
                solids[cur].append(tuple(float(g) for g in m.groups()))
    return solids


def measure(path, base_solid='wing_base', surf_solids=('wing_upper', 'wing_lower')):
    """Measure base thickness and local chord in N_STATIONS spanwise bands."""
    s = load_stl(path)
    if base_solid not in s or not s[base_solid]:
        return None, "REFUSE: no '%s' solid in %s -- this surface has no trailing-edge base. " \
                     "A sharp-closed surface is a DEPARTURE from AGARD Table B1-1, not a pass." \
                     % (base_solid, path)
    base = s[base_solid]
    surf = [v for n in surf_solids for v in s.get(n, [])]
    ys = [v[1] for v in base]
    y0, y1 = min(ys), max(ys)
    span = y1 - y0
    rows = []
    for i in range(N_STATIONS):
        a = y0 + span * i / N_STATIONS
        b = y0 + span * (i + 1) / N_STATIONS
        band = [v for v in base if a <= v[1] <= b]
        if len(band) < 2:
            continue
        zs = [v[2] for v in band]
        dz = max(zs) - min(zs)
        ymid = 0.5 * (a + b)
        cband = [v for v in surf if abs(v[1] - ymid) < span / (2.0 * N_STATIONS)]
        chord = (max(v[0] for v in cband) - min(v[0] for v in cband)) if len(cband) >= 2 else None
        rows.append({'y': ymid, 'n': len(band), 'dz': dz, 'chord': chord})
    return rows, None


def planted_control(src, factor=3.0, solid='wing_base'):
    """Plant into the INPUT: scale `solid`'s z by `factor` in a COPY OF THE STL ON DISK,
    then RE-RUN the real reader (measure()) on that file.

    Which code path does this exercise?  measure()'s band reduction max(z)-min(z),
    reached through load_stl()'s vertex parser and solid-name dispatch -- i.e. exactly
    the path that produces the graded number.

    Could the phenomenon arrive another way?  Yes: a reported change could also come
    from vertices migrating between spanwise bands.  That is EXCLUDED here, because the
    plant touches only z while bands are assigned on y -- so the `chord` column is a
    live discrimination control and must not move.
    """
    out = []
    clean, err = measure(src)
    if err:
        return False, [err]
    d = tempfile.mkdtemp(prefix='m6h1_plant_')
    dst = os.path.join(d, 'planted.stl')
    cur, touched = None, 0
    with open(src) as fi, open(dst, 'w') as fo:
        for line in fi:
            st = line.strip()
            if st.startswith('solid'):
                parts = st.split(None, 1)
                cur = parts[1] if len(parts) > 1 else 'unnamed'
            m = VRE.match(line.rstrip('\n'))
            if m and cur == solid:
                x, y, z = (float(m.group(i)) for i in (1, 2, 3))
                fo.write("    vertex %.9g %.9g %.9g\n" % (x, y, z * factor))
                touched += 1
                continue
            fo.write(line)
    out.append("plant: scaled z of %d '%s' vertices by %.1f in a COPY ON DISK -> %s"
               % (touched, solid, factor, dst))
    planted, err = measure(dst)
    shutil.rmtree(d, ignore_errors=True)
    if err:
        return False, out + [err]

    seen = chord_ok = True
    for c, p in zip(clean, planted):
        exp = c['dz'] * factor
        if abs(p['dz'] - exp) > 1e-9 * max(1.0, exp):
            seen = False
        if c['chord'] is not None and p['chord'] is not None and abs(c['chord'] - p['chord']) > 1e-12:
            chord_ok = False
    out.append("  station 0: clean dz = %.6e  ->  planted dz = %.6e  (expected %.6e)"
               % (clean[0]['dz'], planted[0]['dz'], clean[0]['dz'] * factor))
    out.append("  reader SAW the planted perturbation at every station: %s" % seen)
    out.append("  DISCRIMINATION: chord column unchanged by the plant: %s" % chord_ok)
    if not seen:
        out.append("  REFUSE: the reader did not see a known non-zero change in its input. "
                   "Its clean result is NOT evidence (rule 3).")
    if not chord_ok:
        out.append("  REFUSE: the plant moved the chord column, so it exercised a path it "
                   "was not meant to. The control does not discriminate.")
    return (seen and chord_ok), out


def measure_tc_and_span(path, surf_solids=('wing_upper', 'wing_lower'),
                        base_solid='wing_base'):
    """§7's H-G0 clauses 2 and 3, measured from the SAME STL the base clause is measured
    from.  Returns (tc_max, semispan, n_bands) or (None, None, None).

    THESE TWO CLAUSES WERE REGISTERED IN §7 AND HAD NO INSTRUMENT.  This reader printed
    "H-G0 (surface fidelity ...): PASS" while evaluating ONE of the three registered
    clauses -- i.e. it claimed a gate it had not evaluated.  `read_cell_count.py` announces
    its own gap on stdout; this one did not, which is worse, because a reader of the output
    had no way to know.
    """
    s = load_stl(path)
    pts = [v for n in surf_solids for v in s.get(n, [])] + list(s.get(base_solid, []))
    if len(pts) < 3:
        return None, None, None
    ys = [v[1] for v in pts]
    span = max(ys) - min(ys)
    if span <= 0:
        return None, None, None
    # 🔴 t/c IS MEASURED ON EXACT CONSTANT-y SLICES, NOT ON BANDS, AND THAT IS NOT
    # FUSSINESS.  A band of finite width on a wing swept 30 deg at the leading edge and
    # 15.8 deg at the trailing edge has max(x) - min(x) LARGER than the local chord, by
    # roughly the band width times tan(sweep).  That inflates the chord, so it deflates
    # t/c.  MEASURED with 9 bands on a surface whose true t/c is 9.784 %: the banded
    # estimate returned 9.3928 %, 4.02 % low -- i.e. TWICE the +/-2 % gate, so a
    # geometrically exact M6 surface would have been failed by the instrument rather than
    # by the geometry.
    # A surface built from a structured grid has exact repeated y values, so grouping
    # vertices by y recovers true sections and the bias is identically zero.
    groups = {}
    for v in pts:
        groups.setdefault(round(v[1], 9), []).append(v)
    usable = [g for g in groups.values() if len(g) >= MIN_PTS_PER_SLICE]
    # 🔴 DECLINE RATHER THAN DEGRADE.  If the surface does not present repeated constant-y
    # sections -- an unstructured or multiblock STL will not -- then a "slice" is three
    # scattered points, its chord is near zero, and t/c comes out enormous.  MEASURED on the
    # DAFoam tutorial's 9-block M6 surface: t/c 4,586,152.  A number like that is not a
    # failed gate, it is a reader outside its domain, and it must say so rather than emit it.
    if len(usable) < N_STATIONS:
        return None, span, len(usable)
    chords = [(max(v[0] for v in g) - min(v[0] for v in g), g) for g in usable]
    cmax = max(c for c, _ in chords) if chords else 0.0
    if cmax <= 0:
        return None, span, 0
    # A group of coplanar-in-y points whose x extent is a small fraction of the largest
    # section is a FRAGMENT, not a section -- a tip-cap block, a patch seam.  Dividing a
    # thickness by a fragment's x extent is what produced t/c = 4.6e8 % on the DAFoam
    # tutorial's 9-block surface.  Fragments are dropped, and if too few real sections
    # survive the reader DECLINES instead of emitting a number from the ones that did.
    real = [(c, g) for c, g in chords if c >= MIN_SLICE_CHORD_FRAC * cmax]
    if len(real) < N_STATIONS:
        return None, span, len(real)
    tc = max((max(v[2] for v in g) - min(v[2] for v in g)) / c for c, g in real)
    return tc, span, len(real)


def planted_control_tc_span(src):
    """Plant into the INPUT for the two clauses this reader used to leave ungraded.

    TWO PLANTS, EACH WITH THE OTHER AS ITS DISCRIMINATION CONTROL:
      * scale the SURFACE solids' z by PLANT_TC -> t/c must move by that factor and the
        SEMISPAN must not move at all;
      * scale every solid's y by PLANT_SPAN -> the semispan must move by that factor and
        t/c must not move (y is not in the t/c ratio).
    A plant that moved both would not discriminate between the two clauses, and a reader
    that responded to neither would have been reporting a gate it cannot see.
    """
    out = []
    tc0, sp0, nb0 = measure_tc_and_span(src)
    if tc0 is None or sp0 is None:
        return False, ["DECLINE: this surface does not present repeated constant-y sections "
                       "(%s usable slices of at least %d points, %d needed), so H-G0's "
                       "max-t/c clause cannot be measured on it without a sweep-biased "
                       "chord. Declined rather than degraded."
                       % (nb0, MIN_PTS_PER_SLICE, N_STATIONS)]
    d = tempfile.mkdtemp(prefix='m6h1_tcspan_')
    try:
        def rewrite(dst, zf, yf, solids):
            cur = None
            with open(src) as fi, open(dst, 'w') as fo:
                for line in fi:
                    st = line.strip()
                    if st.startswith('solid'):
                        parts = st.split(None, 1)
                        cur = parts[1] if len(parts) > 1 else 'unnamed'
                    m = VRE.match(line.rstrip('\n'))
                    if m and (solids is None or cur in solids):
                        x, y, z = (float(m.group(i)) for i in (1, 2, 3))
                        fo.write("    vertex %.9g %.9g %.9g\n" % (x, y * yf, z * zf))
                        continue
                    fo.write(line)

        a = os.path.join(d, 'plant_tc.stl')
        rewrite(a, PLANT_TC, 1.0, ('wing_upper', 'wing_lower'))
        tc1, sp1, _ = measure_tc_and_span(a)
        tc_seen = tc1 is not None and abs(tc1 - tc0 * PLANT_TC) <= PLANT_RTOL * tc0 * PLANT_TC
        tc_disc = sp1 is not None and abs(sp1 - sp0) <= PLANT_RTOL * sp0
        out.append("PLANT t/c : scaled the SURFACE solids' z by %.2f -> t/c %.6f became "
                   "%.6f (predicted %.6f) : %s ; DISCRIMINATION semispan unmoved: %s"
                   % (PLANT_TC, tc0, tc1 if tc1 is not None else float('nan'),
                      tc0 * PLANT_TC, 'ok' if tc_seen else 'REFUSE',
                      'ok' if tc_disc else 'REFUSE'))

        b = os.path.join(d, 'plant_span.stl')
        rewrite(b, 1.0, PLANT_SPAN, None)
        tc2, sp2, _ = measure_tc_and_span(b)
        sp_seen = sp2 is not None and abs(sp2 - sp0 * PLANT_SPAN) <= PLANT_RTOL * sp0 * PLANT_SPAN
        sp_disc = tc2 is not None and abs(tc2 - tc0) <= PLANT_RTOL * tc0
        out.append("PLANT span: scaled EVERY solid's y by %.2f -> semispan %.6f became "
                   "%.6f (predicted %.6f) : %s ; DISCRIMINATION t/c unmoved: %s"
                   % (PLANT_SPAN, sp0, sp2 if sp2 is not None else float('nan'),
                      sp0 * PLANT_SPAN, 'ok' if sp_seen else 'REFUSE',
                      'ok' if sp_disc else 'REFUSE'))
        return (tc_seen and tc_disc and sp_seen and sp_disc), out
    finally:
        shutil.rmtree(d, ignore_errors=True)


def measure_base_cells(path, base_solid='wing_base'):
    """H-G2's count, DERIVED FROM THE MESH.  Returns (min_cells, max_cells, n_stations)
    or (None, None, 0) if the surface does not present it.

    🔴 WHY THIS IS DERIVED AND NO LONGER TAKEN FROM argv.
    §7 registers H-G2 as ">= 8 CELLS ACROSS THE TE BASE at every spanwise station".  This
    reader used to take a single scalar "volume cell size" from the command line and divide
    the base thickness by it.  THAT WORKS ONLY FOR AN ISOTROPIC CELL.  The M6H1 route is a
    hyperbolic C/O mesh whose cell at the base is about 1.654e-6 m NORMAL TO THE WALL and
    about base/n ALONG the base, so "the volume cell size" is not one number:

        fed s0 = 1.654e-6      ->  1.1366e-3 / 1.654e-6  =  687 cells  ->  PASSES by 86x
        fed the base spacing   ->  1.1366e-3 / 5.68e-4   =    2 cells  ->  FAILS by 4x

    SAME MESH, SAME GATE, TWO ANSWERS THREE ORDERS APART, decided by an argument the
    registration cannot constrain.  **AN INSTRUMENT THAT TAKES ITS MEASURED QUANTITY FROM
    ITS CALLER HAS A FREE PARAMETER UNLESS THE REGISTRATION FIXES THE CALLER, AND A
    REGISTRATION CANNOT FIX A COMMAND LINE.**  Annotating the choice would have left it
    exactly where it was; the choice is removed instead.

    RULED (cfd-supervisor, 2026-09-12, pre-compute): the cell size is **the spacing ALONG
    the base in the WRAP direction**, so the count is **the number of cells laid across the
    blunt base**.  §1.3's argument for abandoning the octree is REPRESENTABILITY — "a snappy
    cell is isotropic and at the old route's level 4 the TE base was 0.04 cells wide, i.e.
    NOT REPRESENTABLE AT ALL" — and representability is about SPANNING the base, not about
    how thin the cells are normal to it.  A cell that spans the entire base in the wrap
    direction does not resolve the base; it resolves the boundary layer.

    HOW IT IS DERIVED.  The base solid is a strip of quads laid across the blunt base and
    swept along the span, so at each constant-y station its vertices form a line of n+1
    distinct thickness coordinates.  The count is n.  This is the SURFACE spacing, and a
    hyperbolic extrusion carries the surface distribution into the volume unchanged in that
    direction, so the surface count IS the volume count across the base.
    """
    s = load_stl(path)
    base = s.get(base_solid, [])
    if len(base) < 4:
        return None, None, 0
    groups = {}
    for v in base:
        groups.setdefault(round(v[1], 9), set()).add(round(v[2], 12))
    counts = [len(z) - 1 for z in groups.values() if len(z) >= 2]
    if len(counts) < N_STATIONS:
        return None, None, len(counts)
    return min(counts), max(counts), len(counts)


def _rebuild_base(src, dst, k, base_solid='wing_base'):
    """Write a copy of the STL whose base solid is laid with EXACTLY k cells across it,
    over the same span stations and the same thickness extent.  Everything else is copied
    byte for byte.  This is the plant for H-G2's derived count."""
    s = load_stl(src)
    base = s.get(base_solid, [])
    if len(base) < 4:
        raise ValueError("no base solid to rebuild in %s" % src)
    ys = sorted({round(v[1], 9) for v in base})
    ext = {}
    for v in base:
        y = round(v[1], 9)
        lo, hi = ext.get(y, (v[2], v[2]))
        ext[y] = (min(lo, v[2]), max(hi, v[2]))
    xs = {}
    for v in base:
        xs.setdefault(round(v[1], 9), []).append(v[0])
    out, skipping = [], False
    with open(src) as fi:
        for line in fi:
            st = line.strip()
            if st.startswith('solid'):
                nm = st.split(None, 1)[1] if len(st.split(None, 1)) > 1 else ''
                skipping = (nm == base_solid)
                if skipping:
                    continue
            if st.startswith('endsolid') and skipping:
                skipping = False
                continue
            if not skipping:
                out.append(line.rstrip('\n'))
    out.append("solid %s" % base_solid)
    for j in range(len(ys) - 1):
        y0, y1 = ys[j], ys[j + 1]
        x0 = sum(xs[y0]) / len(xs[y0])
        x1 = sum(xs[y1]) / len(xs[y1])
        (a0, b0), (a1, b1) = ext[y0], ext[y1]
        for i in range(k):
            z00 = a0 + (b0 - a0) * i / float(k); z01 = a0 + (b0 - a0) * (i + 1) / float(k)
            z10 = a1 + (b1 - a1) * i / float(k); z11 = a1 + (b1 - a1) * (i + 1) / float(k)
            for tri in (((x0, y0, z00), (x0, y0, z01), (x1, y1, z11)),
                        ((x0, y0, z00), (x1, y1, z11), (x1, y1, z10))):
                out.append("facet normal 0 0 0\n outer loop")
                for v in tri:
                    out.append("    vertex %.9g %.9g %.9g" % v)
                out.append(" endloop\nendfacet")
    out.append("endsolid %s" % base_solid)
    open(dst, 'w').write("\n".join(out) + "\n")


def planted_control_basecells(src):
    """Plant into the INPUT: rebuild the base at a KNOWN cell count in a copy on disk and
    re-run the real reader.  Two plants at different counts, so the arm cannot be satisfied
    by a reader that returns a constant.  DISCRIMINATION: a plant that changes only the
    base's CELL COUNT must NOT move the base THICKNESS the first clause grades."""
    out = []
    n0 = measure_base_cells(src)[0]
    t0, _ = measure(src)
    if n0 is None or t0 is None:
        return False, ["DECLINE: H-G2's count cannot be derived from %s -- the base solid "
                       "does not present constant-y stations. Declined, not defaulted." % src]
    d = tempfile.mkdtemp(prefix='m6h1_g2_')
    try:
        ok = True
        for k in (3, 11):
            q = os.path.join(d, 'plant_%d.stl' % k)
            _rebuild_base(src, q, k)
            got = measure_base_cells(q)[0]
            tk, _ = measure(q)
            seen = (got == k)
            disc = (tk is not None and len(tk) == len(t0)
                    and all(abs(a['dz'] - b['dz']) <= 1e-12 for a, b in zip(t0, tk)))
            ok = ok and seen and disc
            out.append("PLANT H-G2 count=%d : reader derived %s (predicted %d) : %s ; "
                       "DISCRIMINATION base thickness unmoved: %s"
                       % (k, got, k, 'ok' if seen else 'REFUSE',
                          'ok' if disc else 'REFUSE'))
        return ok, out
    finally:
        shutil.rmtree(d, ignore_errors=True)


def selftest():
    """Arm 2 is the one that matters: the control MUST be able to FAIL.
    A control that passes when the plant is withheld proves nothing."""
    d = tempfile.mkdtemp(prefix='m6h1_self_')
    p = os.path.join(d, 'synth.stl')
    with open(p, 'w') as f:
        for name, zlo, zhi in (('wing_upper', 0.0, 0.05), ('wing_lower', -0.05, 0.0),
                               ('wing_base', -0.0007, 0.0007)):
            f.write("solid %s\n" % name)
            for k in range(40):
                y = k * 0.03
                f.write(" facet normal 0 0 1\n  outer loop\n")
                f.write("    vertex 1.0 %.6f %.6f\n" % (y, zlo))
                f.write("    vertex 1.0 %.6f %.6f\n" % (y, zhi))
                f.write("    vertex %.6f %.6f %.6f\n" % (0.0 if name != 'wing_base' else 1.0, y, zhi))
                f.write("  endloop\n endfacet\n")
            f.write("endsolid %s\n" % name)

    print("SELFTEST 1 — plant APPLIED on a sound reader: control must PASS")
    ok1, msg = planted_control(p)
    for m in msg:
        print("   " + m)
    print("   -> %s  (expected PASS)" % ("PASS" if ok1 else "FAIL"))

    print("SELFTEST 2 — THE CONTROL MUST BE ABLE TO FAIL: blind the reader, re-run")
    g = globals()
    saved = g['measure']
    frozen, _ = saved(p)
    g['measure'] = lambda path, **kw: (frozen, None)      # a reader that ignores its input
    ok2, msg2 = planted_control(p)
    g['measure'] = saved
    for m in msg2:
        print("   " + m)
    print("   -> %s  (expected FAIL — this is the control refusing)" % ("PASS" if ok2 else "FAIL"))

    print("SELFTEST 3 — a SHARP-CLOSED surface (no wing_base) must REFUSE, not pass")
    p2 = os.path.join(d, 'sharp.stl')
    with open(p2, 'w') as f, open(p) as fi:
        skip = False
        for line in fi:
            if line.startswith('solid wing_base'):
                skip = True
            if not skip:
                f.write(line)
            if line.startswith('endsolid wing_base'):
                skip = False
    rows, err = measure(p2)
    print("   -> %s" % (err if err else "NO REFUSAL — DEFECT"))
    ok3 = err is not None
    shutil.rmtree(d, ignore_errors=True)
    good = ok1 and (not ok2) and ok3
    print("\nSELFTEST %s" % ("PASS — the control sees a real plant, REFUSES a blind reader, "
                             "and refuses a sharp-closed surface" if good else "FAIL"))
    return 0 if good else 1


def main(path):
    print("M6H1 H-G0 / H-G2 — trailing-edge base, graded against AGARD AR-138 Table B1-1")
    print("SURFACE: %s" % path)
    print("REFERENCE (registered in advance): base = %.4f %% of local chord\n"
          % (100 * REF_T_TE_FRAC))

    ok_ctrl, msg = planted_control(path)
    print("PLANTED CONTROL — planted into the INPUT, real reader re-run FROM DISK")
    for m in msg:
        print("  " + m)
    ok_ctrl2, msg2 = planted_control_tc_span(path)
    for m in msg2:
        print("  " + m)
    if not (ok_ctrl and ok_ctrl2):
        print("\nREFUSE (exit 2): the controls did not establish that this reader can see a "
              "known non-zero in EVERY clause it grades. No number below would be evidence.")
        return 2

    rows, err = measure(path)
    if err:
        print("\n" + err)
        return 2

    print("\n  %-9s %6s %6s %14s %11s %11s %9s" %
          ("y (m)", "y/b", "n", "base dz (m)", "chord (m)", "% chord", "vs ref"))
    g0 = True
    for r in rows:
        if r['chord']:
            pc = 100 * r['dz'] / r['chord']
            dev = abs(pc - 100 * REF_T_TE_FRAC) / (100 * REF_T_TE_FRAC)
            g0 &= dev <= H_G0_TOL
            print("  %-9.5f %6.3f %6d %14.6e %11.6f %11.4f %8.1f%%"
                  % (r['y'], r['y'] / 1.1963, r['n'], r['dz'], r['chord'], pc, 100 * dev))
        else:
            print("  %-9.5f %6.3f %6d %14.6e %11s %11s %9s"
                  % (r['y'], r['y'] / 1.1963, r['n'], r['dz'], "n/a", "n/a", "n/a"))

    # ---- §7 H-G0 clauses 2 and 3, which this instrument used to leave ungraded ----
    tc, span, nb = measure_tc_and_span(path)
    if tc is None or span is None:
        print("\nDECLINE (exit 2): H-G0's max-t/c and semispan clauses could not be measured "
              "on this surface, and a gate with three registered clauses is not discharged "
              "by grading one of them.")
        return 2
    dtc = abs(tc - REF_TC_MAX) / REF_TC_MAX
    dsp = abs(span - REF_SEMISPAN) / REF_SEMISPAN
    g0_tc = dtc <= H_G0_TC_TOL
    g0_sp = dsp <= H_G0_SPAN_TOL
    print("\n  clause 2  max t/c   %8.4f %%  against %8.4f %%   (%6.2f %% off, gate +/-%.0f %%)  %s"
          % (100 * tc, 100 * REF_TC_MAX, 100 * dtc, 100 * H_G0_TC_TOL,
             'PASS' if g0_tc else 'GATE FAIL'))
    print("  clause 3  semispan  %8.6f m  against %8.4f m  (%6.3f %% off, gate +/-%.1f %%)  %s"
          % (span, REF_SEMISPAN, 100 * dsp, 100 * H_G0_SPAN_TOL,
             'PASS' if g0_sp else 'GATE FAIL'))

    g0_all = g0 and g0_tc and g0_sp
    print("\nH-G0, ALL THREE REGISTERED CLAUSES (base +/-%.0f %%, max t/c +/-%.0f %%, semispan "
          "+/-%.1f %%): %s"
          % (100 * H_G0_TOL, 100 * H_G0_TC_TOL, 100 * H_G0_SPAN_TOL,
             "PASS" if g0_all else "GATE FAIL — reported, NOT adjusted"))
    if g0 and not g0_all:
        print("  (the base clause alone would have said PASS -- which is what this "
              "instrument used to print)")
    g0 = g0_all

    # ---- H-G2, DERIVED FROM THE MESH.  No argv, no default, no fallback. ----
    ok_g2c, msg_g2c = planted_control_basecells(path)
    print("\nPLANTED CONTROL for H-G2's derived count")
    for m in msg_g2c:
        print("  " + m)
    if not ok_g2c:
        print("\nDECLINE (exit 2): H-G2's count could not be established on this surface, or "
              "its controls did not hold. THE COUNT IS NOT TAKEN FROM THE COMMAND LINE and "
              "there is nothing to fall back to -- an instrument that accepts its measured "
              "quantity from its caller has a free parameter the registration cannot fix.")
        return 2
    nmin, nmax, nst = measure_base_cells(path)
    print("\nH-G2 (>= %d cells across the TE base at every spanwise station), count DERIVED "
          "from the surface's own base strip over %d stations:" % (H_G2_MIN_CELLS, nst))
    print("   cells across the base: min %d, max %d" % (nmin, nmax))
    g2 = nmin >= H_G2_MIN_CELLS
    print("H-G2: %s" % ("PASS" if g2 else "GATE FAIL — every M6H1 §5 claim FORBIDDEN"))
    print("  (H-G2's second clause, 'non-decreasing under refinement', is a statement about "
          "THREE levels and is NOT dischargeable from one surface. It is not claimed here.)")
    if len(sys.argv) > 2:
        print("\n  NOTE: argv[2] = %r was IGNORED. This instrument used to accept a volume "
              "cell size there and divide the base thickness by it, which gives answers "
              "three orders apart on an anisotropic cell depending on which size is fed. "
              "The argument is no longer read." % sys.argv[2])
    return 0 if (g0 and g2) else 1


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--selftest':
        sys.exit(selftest())
    if len(sys.argv) < 2:
        sys.exit("usage: measure_te_base.py <surface.stl> [volume_cell_size_m] | --selftest")
    sys.exit(main(sys.argv[1]))
