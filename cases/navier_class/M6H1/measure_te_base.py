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

Exit codes:  0 PASS   1 GATE FAIL (reported, never adjusted)   2 REFUSE (control failed)
"""
import sys, os, re, math, shutil, tempfile

# --- REGISTERED IN ADVANCE (M6H1_PREREGISTRATION.md §1.3, §7). Do not edit to fit. ---
REF_ZL_AT_TE   = 0.0007052       # AGARD AR-138 Table B1-1, final row
REF_T_TE_FRAC  = 2 * REF_ZL_AT_TE   # 0.0014104 of local chord
H_G0_TOL       = 0.10            # +/- 10 % of the reference base thickness
H_G2_MIN_CELLS = 8               # >= 8 cells across the base, every station
N_STATIONS     = 9
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
    if not ok_ctrl:
        print("\nREFUSE (exit 2): the control did not establish that this reader can see a "
              "non-zero. No number below would be evidence.")
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

    print("\nH-G0 (surface fidelity, +/- %.0f %% of the reference base): %s"
          % (100 * H_G0_TOL, "PASS" if g0 else "GATE FAIL — reported, NOT adjusted"))

    if len(sys.argv) > 2:
        cell = float(sys.argv[2])
        print("\nH-G2 (>= %d cells across the base) at a volume cell of %.4e m:"
              % (H_G2_MIN_CELLS, cell))
        g2 = True
        for r in rows:
            n = r['dz'] / cell
            g2 &= n >= H_G2_MIN_CELLS
            print("   y/b %5.3f : %7.2f cells %s"
                  % (r['y'] / 1.1963, n, "" if n >= H_G2_MIN_CELLS else "  *** BELOW GATE ***"))
        print("H-G2: %s" % ("PASS" if g2 else "GATE FAIL — every M6H1 §5 claim FORBIDDEN"))
        return 0 if (g0 and g2) else 1
    return 0 if g0 else 1


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--selftest':
        sys.exit(selftest())
    if len(sys.argv) < 2:
        sys.exit("usage: measure_te_base.py <surface.stl> [volume_cell_size_m] | --selftest")
    sys.exit(main(sys.argv[1]))
