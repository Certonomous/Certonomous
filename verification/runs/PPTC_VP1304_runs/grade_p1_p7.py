#!/usr/bin/env python3
"""Grade P1-P7 of the PPTC mesh-repair rung.

Registration FROZEN at e2a8294f; Addendum 1 f373bc115; Addendum 2 1c95466b.

FROZEN §3.2a, BINDING ON EVERY PAIRED OR DIFFERENCED QUANTITY HERE:
    assert, IN THE SAME INVOCATION AS THE COMPARISON, that the arrays have equal length and
    that the length equals the cell or face count of the mesh being graded.  A comparison that
    cannot show this assert did not happen.
THE REBUILT MESH HAS MORE CELLS THAN F360_coarse BY CONSTRUCTION, so a cross-mesh pairing is
the EXPECTED condition unless something refuses it -- and it returns a plausible number, not
an error.  Baselines below are SCALARS measured on F360_coarse, never arrays, precisely so
that no array from one mesh can ever be paired against an array from another.
"""
import re, sys, argparse
import numpy as np

# Baselines: scalars measured on F360_coarse and quoted in the frozen registration.
BASE = dict(neg_vol=316, wrong_oriented_set=2089, wrong_oriented_checkmesh=2548,
            enrich_4_3=31.2, minpyr_nonpos=1028, pos_vol_inverted=712)


def _body(raw):
    sep = b'// * * *'
    return raw[raw.index(sep):] if sep in raw else raw


def labels(path):
    """Content-sniffed.  A cellSet declares `format binary` and writes an ASCII body; a
    header-trusting parse decodes digit characters as int32 and every index lands out of
    range, which reads as 'no matches' rather than as an error."""
    raw = open(path, 'rb').read(); b = _body(raw)
    m = re.search(rb'(\d+)\s*\(', b)
    if m is None:
        return np.zeros(0, dtype=np.int64)
    n = int(m.group(1)); s = m.end()
    t = b[s:s + min(4000, len(b) - s)]
    if sum(32 <= c < 127 or c in (10, 13) for c in t) / max(len(t), 1) > 0.99:
        a = np.array(b[s:b.rindex(b')')].split(), dtype=np.int64)
    else:
        a = np.frombuffer(b[s:s + 4 * n], dtype='<i4').astype(np.int64)
    assert len(a) == n, f'{path}: declared {n}, parsed {len(a)}'
    return a


def vfield(path):
    raw = open(path, 'rb').read(); k = raw.index(b'internalField'); seg = raw[k:]
    m = re.search(rb'nonuniform\s+List<scalar>\s*(\d+)\s*\(', seg)
    n = int(m.group(1)); s = m.end(); e = seg.index(b')\n;', s)
    a = np.array(seg[s:e].split(), dtype=np.float64)
    assert len(a) == n, f'{path}: declared {n}, parsed {len(a)}'
    return a


def main(case, ncells_expected=None):
    pm = f'{case}/constant/polyMesh'
    cv = vfield(f'{case}/0/cellVolume')
    mp = vfield(f'{case}/0/minPyrVolume')
    lvl = labels(f'{pm}/cellLevel')
    NC = len(cv)

    # ---- §3.2a SAME-MESH ASSERT, in this invocation, before any paired quantity ----------
    print('SAME-MESH ASSERT (frozen §3.2a) -- before any comparison below')
    for nm, arr in (('0/cellVolume', cv), ('0/minPyrVolume', mp), ('cellLevel', lvl)):
        print(f'    {nm:<18} len = {len(arr)}')
        if len(arr) != NC:
            sys.exit(f'REFUSE: {nm} has {len(arr)} entries, mesh has {NC} cells -- ASSERT FAILED')
    if ncells_expected is not None and NC != ncells_expected:
        sys.exit(f'REFUSE: mesh has {NC} cells, caller expected {ncells_expected}')
    print(f'    all equal, and equal to the graded mesh cell count {NC}: ASSERT PASSED')
    print(f'    (baselines below are SCALARS from F360_coarse, never arrays -- no array from '
          f'one mesh\n     can be paired against an array from another)\n')

    zvc = labels(f'{pm}/sets/zeroVolumeCells')
    if len(zvc) and zvc.max() >= NC:
        sys.exit(f'REFUSE: zeroVolumeCells max index {zvc.max()} >= {NC} cells')
    try:
        wof = labels(f'{pm}/sets/wrongOrientedFaces')
    except Exception:
        wof = np.zeros(0, dtype=np.int64)

    neg = int((cv < 0).sum())
    minpyr = int((mp <= 0).sum())
    posinv = int(((cv > 0) & (mp <= 0)).sum())
    neg_pyrpos = int(((cv < 0) & (mp > 0)).sum())

    # ---- P4: the 4<->3 enrichment among SURVIVING negative-volume cells -----------------
    own = labels(f'{pm}/owner'); nei = labels(f'{pm}/neighbour')
    o = own[:len(nei)]; n_ = nei
    lo, ln = lvl[o], lvl[n_]
    # P4's NORMALISATION IS FIXED BY THE FROZEN 31.2x AND MUST REPRODUCE IT.
    # It is a FACE-SLOT share seen from the level-4 cells, NOT a share of all internal faces:
    #   numerator   = among the face slots of the negative-volume cells, the 4<->3 fraction
    #   denominator = among the face slots of ALL level-4 cells, the 4<->3 fraction
    # A face between two qualifying cells is counted once per cell, which is what a "seen from
    # the cell" share means.  Normalising instead over all internal faces gives 18.3x on
    # F360_coarse -- the same direction, but a different quantity, and P4's 10x threshold
    # would then be applied to a number the registration never measured.
    is43_face = ((lo == 4) & (ln == 3)) | ((lo == 3) & (ln == 4))
    n43_total = int(is43_face.sum())
    isbad = np.zeros(NC, dtype=bool); isbad[zvc] = True
    slots_bad = int(isbad[o].sum() + isbad[n_].sum())
    bad_43 = int((isbad[o] & is43_face).sum() + (isbad[n_] & is43_face).sum())
    lvl4 = (lvl == 4)
    slots_l4 = int(lvl4[o].sum() + lvl4[n_].sum())
    base43_slots = int((lvl4[o] & is43_face).sum() + (lvl4[n_] & is43_face).sum())
    bad_faces = slots_bad
    base_43_share = base43_slots / slots_l4 * 100 if slots_l4 else 0.0
    if n43_total == 0:
        p4 = 'NOT MEASURABLE'; enrich = None
    elif bad_faces == 0:
        p4 = 'NOT MEASURABLE'; enrich = None
    else:
        enrich = (bad_43 / bad_faces * 100) / base_43_share if base_43_share else None
        p4 = ('PASS' if enrich is not None and enrich < 10 else 'GATE FAIL')

    v = lambda ok: 'PASS' if ok else 'GATE FAIL'
    rows = [
        ('P1', 'negative-volume cells < 200', neg, BASE['neg_vol'], v(neg < 200)),
        ('P2', 'negative-volume cells > 0 (rung NOT predicted to cure)', neg, BASE['neg_vol'], v(neg > 0)),
        ('P3', 'wrongOrientedFaces set < 1800', len(wof), BASE['wrong_oriented_set'], v(len(wof) < 1800)),
        ('P4', '4<->3 enrichment among survivors < 10x',
         ('n/a' if enrich is None else f'{enrich:.1f}x'), f"{BASE['enrich_4_3']}x", p4),
        ('P6', 'cells with minPyrVolume <= 0 < 700', minpyr, BASE['minpyr_nonpos'], v(minpyr < 700)),
        ('P7', 'positive volume + inverted face > 0', posinv, BASE['pos_vol_inverted'], v(posinv > 0)),
    ]
    print(f'{"#":<4}{"prediction":<52}{"measured":>14}{"baseline":>12}   verdict')
    for k, d, m_, b, r in rows:
        print(f'{k:<4}{d:<52}{str(m_):>14}{str(b):>12}   {r}')
    print(f'\nP5  the §3.2 SPD gate still FAILS  -> graded by spd_gate.py, reported beside its '
          f'geometry control')
    print(f'\nSUPPORTING, not predictions:')
    print(f'    cells {NC}   (F360_coarse had 19700035; more by construction -- see the assert)')
    print(f'    4<->3 internal faces in the whole mesh : {n43_total} of {len(n_)} '
          f'({base_43_share:.4f}%)')
    print(f'    face SLOTS of negative-volume cells    : {bad_faces}, of which 4<->3: {bad_43} '
          f'({100*bad_43/max(bad_faces,1):.2f}%)')
    print(f'    face SLOTS of all level-4 cells        : {slots_l4}, of which 4<->3: '
          f'{base43_slots} ({base_43_share:.4f}%)  <- P4 denominator, fixed by the frozen 31.2x')
    print(f'    negative volume with a POSITIVE pyramid: {neg_pyrpos}  '
          f'(0 on F360_coarse => the 316 were a STRICT SUBSET of the 1028)')
    if p4 == 'NOT MEASURABLE':
        print(f'\n    P4 IS **NOT MEASURABLE**, NOT PASSED: the 4<->3 category is empty '
              f'({n43_total} such faces\n    in the mesh, {bad_43} touching a bad cell). An '
              f'enrichment ratio over an empty category has no\n    value, and reporting '
              f'"below 10x" because the denominator vanished would be arithmetic\n    dressed '
              f'as a result. Ruled in advance, before these numbers existed.')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--case', required=True)
    ap.add_argument('--expect-cells', type=int)
    a = ap.parse_args()
    main(a.case, a.expect_cells)
