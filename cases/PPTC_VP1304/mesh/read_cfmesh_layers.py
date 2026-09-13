#!/usr/bin/env python3
"""LAYER-ACHIEVEMENT READER FOR A cfMesh (`cartesianMesh`) MESH -- PPTC VP1304 rung CFM-1.

WHY THIS EXISTS AND WHY IT IS NOT `read_layer_achievement.py`.
`snappyHexMesh` prints an achievement table ("Extruding N out of M faces (P%)") and
`cases/PPTC_VP1304/mesh/read_layer_achievement.py` reads that table.  **cfMesh prints no such
table.**  Inspected in the published source: every per-face layer report in
`meshLibrary/utilities/boundaryLayers/refineBoundaryLayers/refineBoundaryLayersFunctions.C`
(`:302-304`, `:333-337`) sits inside `# ifdef DEBUGLayer`, and the library's own per-face layer
count `nLayersAtBndFace_` (`:308-340`) is never written to any artifact.  Layer achievement on
a cfMesh mesh is therefore obtainable ONLY by post-processing the produced mesh, and THIS
SCRIPT IS THE REGISTERED INSTRUMENT that does it.

WHAT IT MEASURES, AND WHY A TOPOLOGICAL COUNT ALONE WOULD BE A FALSE INSTRUMENT.
A cartesian mesh with NO layers is already hexes stacked off the wall, so "how deep is the hex
column above this wall face" returns a large number on a layerless mesh and proves nothing.
The discriminator must be METRIC.  A boundary face f on wall patch P is LAYERED TO DEPTH m iff

    t_1 <= FIRST_FRAC * s_P                       (the near-wall cell is thin vs the local cell)
    RLO <= t_{j+1}/t_j <= RHI   for j = 1 .. m-1  (successive cells grow at the requested ratio)

with t_k the wall-normal extent of the k-th cell in the opposite-face column above f, s_P the
REGISTERED local surface cell size for patch P, and FIRST_FRAC/RLO/RHI frozen below.
Separation at the registered sizes: a layerless cartesian cell gives t_1/s_P = 1.00 and ratios
1.00; cfMesh at nLayers 6 / ratio 1.2 is predicted to give t_1/s_P = 0.1007 and ratios 1.20.
FIRST_FRAC = 0.5 sits between them by 2x on one side and 5x on the other.

GEOMETRY is OpenFOAM's own (`primitiveMeshFaceCentresAndAreas`,
`primitiveMeshCellCentresAndVols`), COPIED from the frozen instrument
`verification/runs/PPTC_VP1304_runs/spd_gate.py`, blob `c68c4ddb`, rather than rewritten --
including its content-sniffing binary/ASCII readers and its points/faces consistency REFUSAL,
which was paid for by the stale-points defect on `F360_coarse`.

ARMING (CLAUDE.md rule 3).  Three controls, and the reader REFUSES (exit 2) rather than
degrading if any of them fails:
  * `--selftest`      : a synthetic LAYERED mesh (must read 100% at depth nLayers) and a
                        synthetic LAYERLESS one (must read 0%).  Both directions.
  * `--control-none`  : a real mesh known to carry NO layers.
  * `--plant`         : PLANT = 1.234e-03 m displacement written TO DISK and read back.
"""
import sys, os, re, shutil, argparse
import numpy as np

EXIT_PASS, EXIT_FAIL, EXIT_REFUSE = 0, 3, 2

# ----------------------------------------------------------------- FROZEN CONSTANTS
FIRST_FRAC = 0.5      # a layered near-wall cell is at most this fraction of the local cell
RLO, RHI   = 1.10, 1.35   # admissible band on t_{j+1}/t_j about the requested ratio 1.2
MAXWALK    = 16       # columns are never walked deeper than this
PLANT      = 1.234e-03    # m -- the planted perturbation (same value as T3_runs/analyse_t3.py)
PLANT_N    = 5000     # number of blade faces planted
PLANT_SMEAR_MAX = 40  # a plant may contaminate at most this many faces per planted face


# ----------------------------------------------------------------- polyMesh readers
# COPIED from spd_gate.py (blob c68c4ddb).  Sniff by CONTENT, never by the header.
def _body(raw):
    sep = b'// * * *'
    return raw[raw.index(sep):] if sep in raw else raw


def read_labels(path):
    raw = open(path, 'rb').read(); b = _body(raw)
    m = re.search(rb'(\d+)\s*\(', b)
    if m is None:
        return np.zeros(0, dtype=np.int64)
    n = int(m.group(1)); s = m.end()
    tail = b[s:s + min(4000, len(b) - s)]
    ascii_frac = sum(32 <= c < 127 or c in (10, 13) for c in tail) / max(len(tail), 1)
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
    return a.reshape(n, 3).copy()


def read_faces(path):
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


def read_boundary(path):
    """-> ordered list of (name, nFaces, startFace).  Tolerates the OpenFOAM dict layout."""
    txt = open(path, 'rb').read().decode('utf8', 'replace')
    txt = _body(txt.encode()).decode('utf8', 'replace')
    out = []
    for m in re.finditer(r'(\w+)\s*\{([^{}]*)\}', txt):
        blk = m.group(2)
        nf = re.search(r'\bnFaces\s+(\d+)\s*;', blk)
        sf = re.search(r'\bstartFace\s+(\d+)\s*;', blk)
        if nf and sf:
            out.append((m.group(1), int(nf.group(1)), int(sf.group(1))))
    if not out:
        raise SystemExit(f'REFUSE: {path}: no patch block with nFaces and startFace')
    return out


# ------------------------------------------------------- OpenFOAM face/cell geometry
def face_geometry(pts, verts, off):
    """OpenFOAM primitiveMeshFaceCentresAndAreas: triangle fan from the vertex average."""
    nf = len(off) - 1
    Cf = np.zeros((nf, 3)); Sf = np.zeros((nf, 3))
    nv = np.diff(off)
    for k in np.unique(nv):
        sel = np.nonzero(nv == k)[0]
        idx = (off[sel][:, None] + np.arange(k)[None, :])
        P = pts[verts[idx]]
        if k == 3:
            Cf[sel] = P.mean(axis=1)
            Sf[sel] = 0.5 * np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
            continue
        pAvg = P.mean(axis=1)
        Pn = np.roll(P, -1, axis=1)
        nTri = np.cross(Pn - P, pAvg[:, None, :] - P)
        a = np.linalg.norm(nTri, axis=2)
        cTri = (P + Pn + pAvg[:, None, :]) / 3.0
        sumA = a.sum(axis=1)
        Sf[sel] = 0.5 * nTri.sum(axis=1)
        good = sumA > 1e-300
        Cf[sel] = np.where(good[:, None],
                           (a[:, :, None] * cTri).sum(axis=1) / np.where(good, sumA, 1)[:, None],
                           pAvg)
    return Cf, Sf


# ---------------------------------------------------------------- the column walk
class Mesh:
    def __init__(self, case, points_path=None, pts_override=None):
        pm = os.path.join(case, 'constant', 'polyMesh')
        self.pm = pm
        self.points_path = points_path or os.path.join(pm, 'points')
        self.verts, self.off = read_faces(os.path.join(pm, 'faces'))
        self.own = read_labels(os.path.join(pm, 'owner'))
        self.nei = read_labels(os.path.join(pm, 'neighbour'))
        self.bnd = read_boundary(os.path.join(pm, 'boundary'))
        self.pts = read_points(self.points_path) if pts_override is None else pts_override
        self.nfaces = len(self.off) - 1
        self.nInt = len(self.nei)
        if len(self.own) != self.nfaces:
            raise SystemExit(f'REFUSE: owner has {len(self.own)} entries, faces has {self.nfaces}')
        nUsed = int(self.verts.max()) + 1
        if len(self.pts) != nUsed:
            raise SystemExit(
                f'REFUSE: points/faces inconsistent: {self.points_path} has {len(self.pts)} '
                f'entries but the face list references {nUsed}.  This is the stale-points '
                'defect. The reader does NOT measure an inconsistent mesh.')
        self.ncells = int(max(self.own.max(), self.nei.max() if self.nInt else 0)) + 1
        self._geom()
        self._addr()

    def _geom(self):
        self.Cf, self.Sf = face_geometry(self.pts, self.verts, self.off)

    def _addr(self):
        """CSR cell -> faces."""
        cells = np.concatenate([self.own, self.nei])
        faces = np.concatenate([np.arange(self.nfaces), np.arange(self.nInt)])
        order = np.argsort(cells, kind='stable')
        self.cf_faces = faces[order]
        cnt = np.bincount(cells, minlength=self.ncells)
        self.cf_off = np.zeros(self.ncells + 1, dtype=np.int64)
        np.cumsum(cnt, out=self.cf_off[1:])

    def face_pts(self, f):
        return self.verts[self.off[f]:self.off[f + 1]]

    def opposite(self, c, f):
        """The unique face of cell c sharing NO point with f; None if not unique."""
        fp = set(self.face_pts(f).tolist())
        hit = None
        for g in self.cf_faces[self.cf_off[c]:self.cf_off[c + 1]]:
            if g == f:
                continue
            if fp.isdisjoint(self.face_pts(g).tolist()):
                if hit is not None:
                    return None
                hit = int(g)
        return hit

    def column(self, bf, maxwalk=MAXWALK):
        """Wall-normal extents t_1..t_K of the opposite-face column above boundary face bf."""
        S = self.Sf[bf]; m = np.linalg.norm(S)
        if m <= 0.0:
            return []
        nhat = S / m
        t = []
        c = int(self.own[bf]); f = int(bf)
        for _ in range(maxwalk):
            g = self.opposite(c, f)
            if g is None:
                break
            t.append(abs(float(np.dot(self.Cf[g] - self.Cf[f], nhat))))
            if g >= self.nInt:
                break
            c = int(self.nei[g]) if int(self.own[g]) == c else int(self.own[g])
            f = g
        return t


def depth(t, s_P, nlayers):
    """Registered metric depth of a layer column.  0 if the near-wall cell is not thin."""
    if not t or t[0] > FIRST_FRAC * s_P:
        return 0
    m = 1
    while m < min(len(t), nlayers):
        r = t[m] / t[m - 1] if t[m - 1] > 0 else 0.0
        if not (RLO <= r <= RHI):
            break
        m += 1
    return m


def measure(mesh, patches, sizes, nlayers, stride=1, verbose=True, label=''):
    res = {}
    byname = {n: (nf, sf) for n, nf, sf in mesh.bnd}
    for p in patches:
        if p not in byname:
            raise SystemExit(f'REFUSE: patch "{p}" is not in {mesh.pm}/boundary')
        nf, sf = byname[p]
        idx = np.arange(sf, sf + nf, stride)
        s_P = sizes[p]
        d = np.zeros(len(idx), dtype=np.int32)
        t1 = np.full(len(idx), np.nan)
        for i, bf in enumerate(idx):
            t = mesh.column(int(bf))
            if t:
                t1[i] = t[0]
            d[i] = depth(t, s_P, nlayers)
        res[p] = dict(n=len(idx), nFacesTotal=nf, startFace=sf, stride=stride, s_P=s_P,
                      idx=idx, t1=t1, depth=d,
                      Cfull=float((d >= nlayers).mean()),
                      C2=float((d >= 2).mean()),
                      t1_med=float(np.nanmedian(t1)) if len(t1) else float('nan'))
    if verbose:
        print(f'--- cfMesh LAYER ACHIEVEMENT :: {label}')
        print(f'    cells {mesh.ncells}  faces {mesh.nfaces}  internal {mesh.nInt}')
        print(f'    registered nLayers {nlayers}; FIRST_FRAC {FIRST_FRAC}; '
              f'ratio band [{RLO}, {RHI}]')
        for p in patches:
            r = res[p]
            print(f'    {p:>16}  faces {r["nFacesTotal"]} (sampled {r["n"]}, stride {r["stride"]})'
                  f'  s_P {r["s_P"]:.4e} m')
            print(f'    {"":>16}  C_full(depth>={nlayers}) = {100*r["Cfull"]:.3f}%   '
                  f'C_2(depth>=2) = {100*r["C2"]:.3f}%   median t1 = {r["t1_med"]:.6e} m '
                  f'({r["t1_med"]/r["s_P"]:.4f} local cells)')
    return res


# ------------------------------------------------------------------------- arming
HDR = ("FoamFile\n{{\n    version 2.0;\n    format ascii;\n    class {cls};\n"
       "    location \"constant/polyMesh\";\n    object {obj};\n}}\n"
       "// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n")


def write_column_mesh(case, s, nlayers, ratio, layered):
    """One wall face with a column of cells above it.
    layered=True : nlayers graded sub-cells filling ONE local cell s, then plain cells of s.
    layered=False: plain cells of height s all the way (a layerless cartesian column)."""
    pm = os.path.join(case, 'constant', 'polyMesh'); os.makedirs(pm, exist_ok=True)
    if layered:
        t1 = s / sum(ratio ** i for i in range(nlayers))
        h = [t1 * ratio ** i for i in range(nlayers)] + [s] * 3
    else:
        h = [s] * (nlayers + 3)
    z = [0.0]
    for hi in h:
        z.append(z[-1] + hi)
    nz = len(z)
    pts = [(x, y, zz) for zz in z for y in (0., s) for x in (0., s)]
    L = lambda i, j, k: k * 4 + j * 2 + i
    faces, owner, nb = [], [], []
    for k in range(nz - 1):                                   # z-normal faces
        q = [L(0, 0, k), L(1, 0, k), L(1, 1, k), L(0, 1, k)]
        if k == 0:
            continue
        # winding gives +z, i.e. owner (cell k-1) -> neighbour (cell k), as OpenFOAM requires
        faces.append(q); owner.append(k - 1); nb.append(k)
    nInt = len(faces)
    wall = [L(0, 0, 0), L(0, 1, 0), L(1, 1, 0), L(1, 0, 0)]   # outward = -z
    faces.append(wall); owner.append(0); nb.append(-1)
    top = [L(0, 0, nz - 1), L(1, 0, nz - 1), L(1, 1, nz - 1), L(0, 1, nz - 1)]
    faces.append(top); owner.append(nz - 2); nb.append(-1)
    sides = []
    for k in range(nz - 1):
        sides += [([L(0,0,k), L(0,0,k+1), L(1,0,k+1), L(1,0,k)], k),
                  ([L(1,1,k), L(1,1,k+1), L(0,1,k+1), L(0,1,k)], k),
                  ([L(0,1,k), L(0,1,k+1), L(0,0,k+1), L(0,0,k)], k),
                  ([L(1,0,k), L(1,0,k+1), L(1,1,k+1), L(1,1,k)], k)]
    for q, c in sides:
        faces.append(q); owner.append(c); nb.append(-1)
    with open(os.path.join(pm, 'points'), 'w') as f:
        f.write(HDR.format(cls='vectorField', obj='points') + f'{len(pts)}\n(\n')
        f.writelines(f'({p[0]:.12g} {p[1]:.12g} {p[2]:.12g})\n' for p in pts); f.write(')\n')
    with open(os.path.join(pm, 'faces'), 'w') as f:
        f.write(HDR.format(cls='faceList', obj='faces') + f'{len(faces)}\n(\n')
        f.writelines(f'{len(v)}({" ".join(map(str,v))})\n' for v in faces); f.write(')\n')
    with open(os.path.join(pm, 'owner'), 'w') as f:
        f.write(HDR.format(cls='labelList', obj='owner') + f'{len(owner)}\n(\n')
        f.writelines(f'{o}\n' for o in owner); f.write(')\n')
    with open(os.path.join(pm, 'neighbour'), 'w') as f:
        f.write(HDR.format(cls='labelList', obj='neighbour') + f'{nInt}\n(\n')
        f.writelines(f'{o}\n' for o in nb[:nInt]); f.write(')\n')
    with open(os.path.join(pm, 'boundary'), 'w') as f:
        f.write(HDR.format(cls='polyBoundaryMesh', obj='boundary'))
        f.write('1\n(\n    blades\n    {\n        type wall;\n'
                f'        nFaces 1;\n        startFace {nInt};\n    }}\n)\n')


def selftest(tmp, s=6.25e-4, nlayers=6, ratio=1.2):
    print('=== ARMING (CLAUDE.md rule 3): the reader is fired in BOTH directions ===')
    yes, no = os.path.join(tmp, 'ctl_layered'), os.path.join(tmp, 'ctl_layerless')
    for d in (yes, no):
        shutil.rmtree(d, ignore_errors=True)
    write_column_mesh(yes, s, nlayers, ratio, layered=True)
    write_column_mesh(no, s, nlayers, ratio, layered=False)
    ry = measure(Mesh(yes), ['blades'], {'blades': s}, nlayers,
                 label='POSITIVE CONTROL -- a SYNTHETIC LAYERED column, must read 100%')
    rn = measure(Mesh(no), ['blades'], {'blades': s}, nlayers,
                 label='NEGATIVE CONTROL -- a SYNTHETIC LAYERLESS column, must read 0%')
    print()
    if ry['blades']['Cfull'] != 1.0:
        print(f'  ARMING FAILED: the reader sees {100*ry["blades"]["Cfull"]:.3f}% on a mesh built '
              f'with exactly {nlayers} layers at ratio {ratio}. IT CANNOT SEE A NON-ZERO.')
        return EXIT_REFUSE
    if rn['blades']['Cfull'] != 0.0 or rn['blades']['C2'] != 0.0:
        print('  ARMING FAILED: the reader reports LAYERS on a LAYERLESS cartesian column.')
        print('  Its zero on any other mesh would be meaningless and its non-zero would be noise.')
        return EXIT_REFUSE
    print(f'  ARMED: layered column reads 100.000% at depth {nlayers}; layerless column reads '
          '0.000% at depth >= 2.  Both directions fired.')
    return EXIT_PASS


def plant_check(case, patch, s_P, nlayers, plant_dir, stride=1):
    """Rule 3: displace PLANT metres along the INWARD normal at PLANT_N faces of `patch`,
    WRITE THE PERTURBED POINTS TO DISK, read them back, and require the reader to see it."""
    print(f'=== PLANTED-ZERO CONTROL: PLANT = {PLANT:.6e} m at {PLANT_N} `{patch}` faces ===')
    base = Mesh(case)
    r0 = measure(base, [patch], {patch: s_P}, nlayers, stride=stride, verbose=False)
    byname = {n: (nf, sf) for n, nf, sf in base.bnd}
    nf, sf = byname[patch]
    step = max(1, nf // PLANT_N)
    targets = list(range(sf, sf + nf, step))[:PLANT_N]
    pts = base.pts.copy()
    moved = set()
    for bf in targets:
        S = base.Sf[bf]; m = np.linalg.norm(S)
        if m <= 0:
            continue
        nhat = S / m                       # outward; the fluid is at -nhat
        g = base.opposite(int(base.own[bf]), int(bf))
        if g is None:
            continue
        for v in base.face_pts(g):
            if v not in moved:
                pts[v] -= PLANT * nhat
                moved.add(int(v))
    os.makedirs(os.path.join(plant_dir, 'constant', 'polyMesh'), exist_ok=True)
    pp = os.path.join(plant_dir, 'constant', 'polyMesh', 'points')
    with open(pp, 'w') as f:
        f.write(HDR.format(cls='vectorField', obj='points') + f'{len(pts)}\n(\n')
        np.savetxt(f, pts, fmt='(%.17g %.17g %.17g)')
        f.write(')\n')
    for nm in ('faces', 'owner', 'neighbour', 'boundary'):
        dst = os.path.join(plant_dir, 'constant', 'polyMesh', nm)
        if not os.path.exists(dst):
            os.link(os.path.join(case, 'constant', 'polyMesh', nm), dst)
    # READ IT BACK FROM DISK -- not from the array in memory.
    planted = Mesh(plant_dir)
    r1 = measure(planted, [patch], {patch: s_P}, nlayers, stride=stride, verbose=False)
    idx = r0[patch]['idx']
    pos = {int(b): i for i, b in enumerate(idx)}
    dt = np.abs(np.nan_to_num(r1[patch]['t1']) - np.nan_to_num(r0[patch]['t1']))
    seen = [dt[pos[b]] for b in targets if b in pos]
    nmoved = int((dt > 1e-9).sum())
    print(f'    planted faces sampled by the reader : {len(seen)}')
    print(f'    max |delta t1| over planted faces   : {max(seen) if seen else 0.0:.9e} m '
          f'(PLANT = {PLANT:.9e})')
    print(f'    faces with |delta t1| > 1e-9        : {nmoved}')
    print(f'    C_full before / after               : {100*r0[patch]["Cfull"]:.3f}% / '
          f'{100*r1[patch]["Cfull"]:.3f}%')
    if not seen or abs(max(seen) - PLANT) > 1e-9:
        print('    PLANT NOT SEEN. The reader cannot see a known non-zero; its zero is not '
              'evidence. REFUSE.')
        return EXIT_REFUSE
    if nmoved > PLANT_SMEAR_MAX * len(seen):
        print(f'    PLANT SMEARED over {nmoved} faces, above the registered bound '
              f'{PLANT_SMEAR_MAX} x {len(seen)}. REFUSE.')
        return EXIT_REFUSE
    print('    PLANT SEEN at exactly the planted magnitude, and bounded. Reader armed on the '
          'real mesh.')
    return EXIT_PASS


def parse_sizes(spec):
    out = {}
    for kv in spec.split(','):
        k, v = kv.split('=')
        out[k.strip()] = float(v)
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--case')
    ap.add_argument('--points', help='override constant/polyMesh/points (stale-points defect)')
    ap.add_argument('--patches', default='blades,hub,cap,shaft')
    ap.add_argument('--sizes', default='blades=6.25e-4,hub=1.25e-3,cap=1.25e-3,shaft=2.5e-3',
                    help='REGISTERED local surface cell size per patch, metres')
    ap.add_argument('--nlayers', type=int, default=6)
    ap.add_argument('--stride', type=int, default=1)
    ap.add_argument('--label', default='')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--control-none', help='case known to carry NO layers; must read 0.000%%')
    ap.add_argument('--control-none-points', help='points override for the control')
    ap.add_argument('--plant-dir', help='where the planted points file is written')
    ap.add_argument('--tmp', default='/tmp/cfmesh_layer_ctl')
    a = ap.parse_args()

    rc = selftest(a.tmp, nlayers=a.nlayers)
    if rc != EXIT_PASS:
        sys.exit(rc)
    print()
    patches = [p for p in a.patches.split(',') if p]
    sizes = parse_sizes(a.sizes)

    if a.control_none:
        m = Mesh(a.control_none, points_path=a.control_none_points)
        r = measure(m, ['blades'], sizes, a.nlayers, stride=a.stride,
                    label=f'GEOMETRY CONTROL -- KNOWN-NO-LAYERS mesh {a.control_none}')
        if r['blades']['Cfull'] != 0.0 or r['blades']['C2'] != 0.0:
            print('\n  GEOMETRY CONTROL FAILED: the reader reports layers on a mesh whose own '
                  'log says 0 faces were extruded. NOTHING IT SAYS IS EVIDENCE. REFUSE.')
            sys.exit(EXIT_REFUSE)
        print('  GEOMETRY CONTROL PASSED: 0.000% on the known-no-layers mesh.')
        print()

    if not a.case:
        sys.exit(EXIT_PASS)

    if a.plant_dir:
        rc = plant_check(a.case, 'blades', sizes['blades'], a.nlayers, a.plant_dir,
                         stride=a.stride)
        if rc != EXIT_PASS:
            sys.exit(rc)
        print()

    measure(Mesh(a.case, points_path=a.points), patches, sizes, a.nlayers, stride=a.stride,
            label=a.label or a.case)
    sys.exit(EXIT_PASS)
