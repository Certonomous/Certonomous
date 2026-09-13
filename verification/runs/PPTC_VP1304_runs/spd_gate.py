#!/usr/bin/env python3
"""§3.2 SPD GATE for the PPTC VP1304 mesh-repair rung.

Registered at `cases/PPTC_VP1304/HUB_ROOT_MESH_RUNG_PREREGISTRATION.md`, FROZEN at commit
e2a8294fafba043991197211a887dc2550c2b892, blob 7b875397a51d97cb9902c64fcfb3a666dd99f852.

THE GATE, quoted from the frozen §3.2:
    For every internal face compute w_f = |S_f|^2 / (S_f . d_f), with S_f the outward
    face-area vector of the OWNER and d_f = C_N - C_P.  Form the zero-row-sum symmetric
    operator A with off-diagonals -w_f and A_PP = sum_f w_f.
    GATE FAIL if any w_f <= 0, or if any cell diagonal A_PP <= 0.  PASS if every w_f > 0.
    The gate must report the witness cell index and the value of A_PP, or it has not fired.

WHY A WITNESS AND NOT AN INFERENCE.  x^T A x = sum_f w_f (x_P - x_N)^2.  If some cell has
A_PP <= 0 then x = e_P gives x^T A x = A_PP <= 0 -- a CONSTRUCTED counterexample to positive
definiteness.  The CG-residual test this replaces was an inference: CG minimises the error in
the A-norm, not ||r||, so residual growth does not prove non-SPD.

READS ONLY constant/polyMesh/{points,faces,owner,neighbour} -- solver-free by registration.

ARMING (CLAUDE.md rule 3).  `--selftest` builds a VALID two-cell mesh and a DELIBERATELY
INVERTED one and requires PASS then FAIL.  A gate only ever exercised on meshes we hope are
good is untested in the only direction that matters.  It REFUSES (exit 2) rather than
degrading.
"""
import sys, os, re, argparse
import numpy as np

EXIT_PASS, EXIT_FAIL, EXIT_REFUSE = 0, 3, 2


# ----------------------------------------------------------------- polyMesh readers
def _body(raw):
    sep = b'// * * *'
    return raw[raw.index(sep):] if sep in raw else raw


def read_labels(path):
    raw = open(path, 'rb').read(); b = _body(raw)
    m = re.search(rb'(\d+)\s*\(', b)
    if m is None:                      # possible "0()" empty list
        return np.zeros(0, dtype=np.int64)
    n = int(m.group(1)); s = m.end()
    tail = b[s:s + min(4000, len(b) - s)]
    ascii_frac = sum(32 <= c < 127 or c in (10, 13) for c in tail) / max(len(tail), 1)
    # SNIFF BY CONTENT, NEVER BY THE HEADER: a cellSet declares `format binary` and writes an
    # ASCII body; trusting the header decodes digit characters as int32 and every index lands
    # out of range, which reads as "no matches" rather than as an error.
    if ascii_frac > 0.99:
        a = np.array(b[s:b.rindex(b')')].split(), dtype=np.int64)
    else:
        a = np.frombuffer(b[s:s + 4 * n], dtype='<i4').astype(np.int64)
    if len(a) != n:
        raise SystemExit(f'REFUSE: {path}: declared {n} entries, parsed {len(a)}')
    return a


def read_points(path):
    raw = open(path, 'rb').read(); b = _body(raw)
    m = re.search(rb'(\d+)\s*\(', b); n = int(m.group(1)); s = m.end()
    tail = b[s:s + min(4000, len(b) - s)]
    if sum(32 <= c < 127 or c in (10, 13) for c in tail) / max(len(tail), 1) > 0.99:
        seg = b[s:b.rindex(b')')].replace(b'(', b' ').replace(b')', b' ')
        a = np.array(seg.split(), dtype=np.float64)
    else:
        a = np.frombuffer(b[s:s + 24 * n], dtype='<f8')
    if a.size != 3 * n:
        raise SystemExit(f'REFUSE: {path}: declared {n} points, parsed {a.size/3}')
    return a.reshape(n, 3)


def read_faces(path):
    """Returns (flat vertex stream, offsets[nFaces+1])."""
    raw = open(path, 'rb').read(); b = _body(raw)
    m = re.search(rb'(\d+)\s*\(', b); n = int(m.group(1)); s = m.end()
    region = b[s:b.rindex(b')')]
    counts = np.array(re.findall(rb'(\d+)\(', region), dtype=np.int64)
    if len(counts) != n:
        raise SystemExit(f'REFUSE: {path}: declared {n} faces, found {len(counts)} "N(" heads')
    stream = re.sub(rb'\d+\(', b' ', region).replace(b')', b' ')
    verts = np.array(stream.split(), dtype=np.int64)
    if verts.size != counts.sum():
        raise SystemExit(f'REFUSE: {path}: vertex stream {verts.size} != sum(counts) {counts.sum()}')
    off = np.zeros(n + 1, dtype=np.int64); np.cumsum(counts, out=off[1:])
    return verts, off


# ----------------------------------------------------------- OpenFOAM face/cell geometry
def face_geometry(pts, verts, off):
    """OpenFOAM primitiveMeshFaceCentresAndAreas: triangle fan from the vertex average."""
    nf = len(off) - 1
    Cf = np.zeros((nf, 3)); Sf = np.zeros((nf, 3))
    nv = np.diff(off)
    for k in np.unique(nv):                       # group by vertex count: all-quad is one pass
        sel = np.nonzero(nv == k)[0]
        idx = (off[sel][:, None] + np.arange(k)[None, :])
        P = pts[verts[idx]]                        # (m, k, 3)
        if k == 3:
            Cf[sel] = P.mean(axis=1)
            Sf[sel] = 0.5 * np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
            continue
        pAvg = P.mean(axis=1)                      # (m,3)
        Pn = np.roll(P, -1, axis=1)
        nTri = np.cross(Pn - P, pAvg[:, None, :] - P)          # (m,k,3)
        a = np.linalg.norm(nTri, axis=2)                        # (m,k)
        cTri = (P + Pn + pAvg[:, None, :]) / 3.0
        sumA = a.sum(axis=1)
        Sf[sel] = 0.5 * nTri.sum(axis=1)
        good = sumA > 1e-300
        Cf[sel] = np.where(good[:, None],
                           (a[:, :, None] * cTri).sum(axis=1) / np.where(good, sumA, 1)[:, None],
                           pAvg)
    return Cf, Sf


def cell_geometry(Cf, Sf, own, nei, ncells):
    """OpenFOAM primitiveMeshCellCentresAndVols: pyramid decomposition about an estimate."""
    nInt = len(nei)
    # np.bincount, never np.add.at: the latter is unbuffered and takes minutes on 6e7 indices.
    bc = lambda idx, w: np.bincount(idx, weights=w, minlength=ncells)
    def vsum(idx, V):
        return np.stack([bc(idx, V[:, j]) for j in range(3)], axis=1)
    cnt = bc(own, None) + bc(nei, None)
    acc = vsum(own, Cf) + vsum(nei, Cf[:nInt])
    cEst = acc / cnt[:, None]
    vol = np.zeros(ncells); volCtr = np.zeros((ncells, 3))
    for cells, Cfl, Sfl in ((own, Cf, Sf), (nei, Cf[:nInt], -Sf[:nInt])):
        d = Cfl - cEst[cells]
        pv = (Sfl * d).sum(axis=1) / 3.0
        ctr = 0.75 * Cfl + 0.25 * cEst[cells]
        vol += bc(cells, pv)
        volCtr += vsum(cells, pv[:, None] * ctr)
    Cc = np.where(np.abs(vol)[:, None] > 1e-300, volCtr / np.where(np.abs(vol) > 1e-300, vol, 1)[:, None], cEst)
    return Cc, vol


# ------------------------------------------------------------------------- the gate
def run_gate(case, label, verbose=True):
    pm = os.path.join(case, 'constant', 'polyMesh')
    pts = read_points(os.path.join(pm, 'points'))
    verts, off = read_faces(os.path.join(pm, 'faces'))
    own = read_labels(os.path.join(pm, 'owner'))
    nei = read_labels(os.path.join(pm, 'neighbour'))
    nfaces, nInt = len(off) - 1, len(nei)
    ncells = int(max(own.max(), nei.max() if nInt else 0)) + 1
    # SAME-MESH ASSERT (frozen §3.2a), IN THIS INVOCATION, before any paired quantity
    if len(own) != nfaces:
        raise SystemExit(f'REFUSE: owner has {len(own)} entries, faces has {nfaces}')
    if nInt > nfaces:
        raise SystemExit('REFUSE: more internal faces than faces')
    # ---------------------------------------------------------------------------------
    # POINTS/FACES CONSISTENCY -- REFUSE, NEVER GRADE.  Added 2026-09-13 after this gate
    # returned GATE FAIL on F360_coarse for the WRONG REASON: snappyHexMesh left
    # constant/polyMesh/points at the SNAPPED array (20,518,324, mtime 11:17) while
    # faces/owner in the same directory are the LAYER-PHASE arrays referencing 20,507,704.
    # Every index past the first merged point then addresses the wrong coordinate.  No index
    # is out of range, so nothing errors -- the geometry is simply garbage, and the gate
    # produced the EXPECTED verdict from it.  An expected answer is the one nobody checks.
    nUsed = int(verts.max()) + 1
    if len(pts) != nUsed:
        raise SystemExit(
            f'REFUSE: points/faces inconsistent in {pm}: points file has {len(pts)} entries '
            f'but the face list references {nUsed}. {len(pts)-nUsed} orphan points. '
            'This is the stale-points defect: the final positions are in 0/polyMesh/points. '
            'The gate does NOT grade an inconsistent mesh.')
    Cf, Sf = face_geometry(pts, verts, off)
    Cc, vol = cell_geometry(Cf, Sf, own, nei, ncells)

    P, N = own[:nInt], nei
    d = Cc[N] - Cc[P]
    Sd = (Sf[:nInt] * d).sum(axis=1)
    S2 = (Sf[:nInt] ** 2).sum(axis=1)
    with np.errstate(divide='ignore', invalid='ignore'):
        w = np.where(Sd != 0.0, S2 / Sd, -np.inf)     # Sd == 0 is degenerate -> fail
    App = (np.bincount(P, weights=w, minlength=ncells)
           + np.bincount(N, weights=w, minlength=ncells))

    bad_w = np.nonzero(~(w > 0))[0]
    bad_d = np.nonzero(~(App > 0))[0]
    fail = len(bad_w) > 0 or len(bad_d) > 0
    if verbose:
        print(f'--- SPD GATE :: {label}')
        print(f'    cells {ncells}  faces {nfaces}  internal {nInt}')
        print(f'    faces with w_f <= 0 (or S_f.d_f == 0) : {len(bad_w)}')
        print(f'    cells with A_PP  <= 0                 : {len(bad_d)}')
        if fail:
            if len(bad_d):
                k = bad_d[int(np.argmin(App[bad_d]))]
                print(f'    WITNESS cell index {k}   A_PP = {App[k]:.9e}')
                print(f'      x = e_{k} gives x^T A x = {App[k]:.9e} <= 0  -- constructed counterexample')
                print(f'      witness cell centre (x,y,z) = ({Cc[k,0]:.6f}, {Cc[k,1]:.6f}, {Cc[k,2]:.6f}) m')
            else:
                f0 = bad_w[int(np.argmin(w[bad_w]))]
                print(f'    NO cell diagonal is non-positive, but face {f0} has w_f = {w[f0]:.6e}')
                print(f'      owner {P[f0]}  neighbour {N[f0]}  S_f.d_f = {Sd[f0]:.6e}')
            print('    VERDICT: GATE FAIL')
        else:
            print('    VERDICT: PASS  (necessary, NOT sufficient -- frozen §3.2)')
    return (not fail), dict(ncells=ncells, nInt=nInt, bad_w=len(bad_w), bad_App=len(bad_d),
                            witness=(int(bad_d[int(np.argmin(App[bad_d]))]) if len(bad_d) else None),
                            App=(float(App[bad_d[int(np.argmin(App[bad_d]))]]) if len(bad_d) else None),
                            vol=vol)


# --------------------------------------------------------------------------- arming
HDR = ("FoamFile\n{{\n    version 2.0;\n    format ascii;\n    class {cls};\n"
       "    location \"constant/polyMesh\";\n    object {obj};\n}}\n"
       "// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n")


def write_two_cell(case, invert):
    """Two stacked hexes sharing one internal face.  invert=True reverses the shared face's
    winding, which flips S_f against d_f and must make w_f negative."""
    pm = os.path.join(case, 'constant', 'polyMesh'); os.makedirs(pm, exist_ok=True)
    pts = [(x, y, z) for z in (0., 1., 2.) for y in (0., 1.) for x in (0., 1.)]
    L = lambda i, j, k: k * 4 + j * 2 + i
    shared = [L(0,0,1), L(1,0,1), L(1,1,1), L(0,1,1)]
    if invert:
        shared = shared[::-1]
    faces = [shared]                                                     # face 0: internal
    for k0, k1 in ((0, 1), (1, 2)):                                      # boundary faces
        faces += [[L(0,0,k0), L(0,1,k0), L(1,1,k0), L(1,0,k0)],
                  [L(0,0,k1), L(1,0,k1), L(1,1,k1), L(0,1,k1)],
                  [L(0,0,k0), L(1,0,k0), L(1,0,k1), L(0,0,k1)],
                  [L(0,1,k0), L(0,1,k1), L(1,1,k1), L(1,1,k0)],
                  [L(0,0,k0), L(0,0,k1), L(0,1,k1), L(0,1,k0)],
                  [L(1,0,k0), L(1,1,k0), L(1,1,k1), L(1,0,k1)]]
    owner = [0] + [0]*6 + [1]*6
    with open(os.path.join(pm, 'points'), 'w') as f:
        f.write(HDR.format(cls='vectorField', obj='points') + f'{len(pts)}\n(\n')
        f.writelines(f'({p[0]} {p[1]} {p[2]})\n' for p in pts); f.write(')\n')
    with open(os.path.join(pm, 'faces'), 'w') as f:
        f.write(HDR.format(cls='faceList', obj='faces') + f'{len(faces)}\n(\n')
        f.writelines(f'{len(v)}({" ".join(map(str,v))})\n' for v in faces); f.write(')\n')
    with open(os.path.join(pm, 'owner'), 'w') as f:
        f.write(HDR.format(cls='labelList', obj='owner') + f'{len(owner)}\n(\n')
        f.writelines(f'{o}\n' for o in owner); f.write(')\n')
    with open(os.path.join(pm, 'neighbour'), 'w') as f:
        f.write(HDR.format(cls='labelList', obj='neighbour') + '1\n(\n1\n)\n')


def selftest(tmp):
    print('=== ARMING (CLAUDE.md rule 3): the gate is fired at a mesh that MUST trip it ===')
    good, bad = os.path.join(tmp, 'ctl_valid'), os.path.join(tmp, 'ctl_inverted')
    write_two_cell(good, invert=False); write_two_cell(bad, invert=True)
    ok_g, _ = run_gate(good, 'NEGATIVE CONTROL -- a VALID two-cell mesh, must PASS')
    ok_b, ib = run_gate(bad, 'POSITIVE CONTROL -- one face DELIBERATELY INVERTED, must FAIL')
    print()
    if not ok_g:
        print('  ARMING FAILED: the gate rejects a VALID mesh. It is not an instrument.'); return EXIT_REFUSE
    if ok_b:
        print('  ARMING FAILED: the gate PASSED a mesh with a deliberately inverted face.')
        print('  NOTHING IT SAYS ABOUT ANY OTHER MESH IS EVIDENCE.'); return EXIT_REFUSE
    if ib['witness'] is None:
        print('  ARMING FAILED: it failed the inverted mesh but produced NO WITNESS CELL.')
        print('  The frozen gate requires a witness index and an A_PP value, or it has not fired.')
        return EXIT_REFUSE
    print(f'  ARMED: valid mesh PASS, inverted mesh FAIL with witness cell {ib["witness"]} '
          f'A_PP = {ib["App"]:.6e}')
    return EXIT_PASS


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--case'); ap.add_argument('--label', default='')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--tmp', default='/tmp/spd_gate_ctl')
    ap.add_argument('--check-volumes', help='OpenFOAM 0/cellVolume to validate the geometry against')
    a = ap.parse_args()
    if a.selftest and not a.case:
        sys.exit(selftest(a.tmp))
    rc = selftest(a.tmp)                 # ALWAYS armed before it is pointed at anything
    if rc != EXIT_PASS:
        sys.exit(rc)
    print()
    ok, info = run_gate(a.case, a.label or a.case)
    if a.check_volumes:
        raw = open(a.check_volumes, 'rb').read(); k = raw.index(b'internalField'); seg = raw[k:]
        m = re.search(rb'nonuniform\s+List<scalar>\s*(\d+)\s*\(', seg)
        n = int(m.group(1)); s = m.end(); e = seg.index(b')\n;', s)
        V = np.array(seg[s:e].split(), dtype=np.float64)
        if len(V) != info['ncells']:
            raise SystemExit(f'REFUSE: cellVolume has {len(V)} cells, mesh has {info["ncells"]} '
                             '-- SAME-MESH ASSERT (frozen §3.2a) FAILED')
        rel = np.abs(info['vol'] - V) / np.maximum(np.abs(V), 1e-30)
        print(f'\n    GEOMETRY CONTROL vs OpenFOAM 0/cellVolume ({len(V)} cells, same-mesh assert PASSED):')
        print(f'      max relative difference in cell volume: {rel.max():.3e}')
        print(f'      negative volumes  mine {int((info["vol"]<0).sum())}  OpenFOAM {int((V<0).sum())}')
        # BLOCKING.  A gate whose own geometry disagrees with OpenFOAM's has not measured the
        # mesh it was pointed at, and its verdict -- in EITHER direction -- is void.
        if rel.max() > 1e-6 or int((info['vol'] < 0).sum()) != int((V < 0).sum()):
            print('      GEOMETRY CONTROL FAILED -- the verdict above is VOID, not a result.')
            sys.exit(EXIT_REFUSE)
        print('      geometry control PASSED -- the verdict above stands on measured geometry')
    sys.exit(EXIT_PASS if ok else EXIT_FAIL)
