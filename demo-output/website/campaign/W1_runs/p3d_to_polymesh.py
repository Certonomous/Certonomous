"""Direct structured PLOT3D (j,k) plane -> OpenFOAM polyMesh, one cell thick.

Uses NASA's node coordinates exactly as read: streamwise x = file x,
wall-normal y = file z, span z in {0,1} = -(file y). No transformPoints,
no shape-matching heuristics: faces, owner, neighbour built by index
arithmetic, orientation fixed numerically per face. Written because
plot3dToFoam v2606 duplicates the two bottom-corner inlet/outlet boundary
faces on the 177x81 and 353x161 bump grids (2 open cells, 2 spurious
89.5-degree faces); the coarse 89x41 conversion is healthy and serves as
the validation reference for this converter.
"""
import sys
import numpy as np

sys.path.insert(0, '/home/ubuntu/certonomous-runs/w1-bump-nasa-grids')
from read_p3d import read_p3dfmt

WALL_X0, WALL_X1 = 0.0, 1.5

def build(grid_path, case_dir):
    ni, nj, nk, X, Y, Z = read_p3dfmt(grid_path)
    assert ni == 2
    x2 = X[:, :, 0].T   # (j, k): streamwise
    y2 = Z[:, :, 0].T   # (j, k): wall-normal (file z)
    # span from file y in [-1, 0] -> z in {0, 1}; verify planes are exact
    zplanes = sorted(-v for v in np.unique(Y))
    assert zplanes == [0.0, 1.0], zplanes
    NJ, NK = nj, nk
    npl = NJ * NK
    def pid(j, k, l): return l * npl + k * NJ + j
    pts = np.empty((2 * npl, 3))
    for l, zv in enumerate(zplanes):
        pts[l*npl:(l+1)*npl, 0] = x2.T.ravel()   # k-major: index k*NJ+j
        pts[l*npl:(l+1)*npl, 1] = y2.T.ravel()
        pts[l*npl:(l+1)*npl, 2] = zv
    CJ, CK = NJ - 1, NK - 1
    ncell = CJ * CK
    def cid(j, k): return k * CJ + j
    ccent = np.empty((ncell, 3))
    for k in range(CK):
        for j in range(CJ):
            ccent[cid(j, k), 0] = 0.25*(x2[j,k]+x2[j+1,k]+x2[j,k+1]+x2[j+1,k+1])
            ccent[cid(j, k), 1] = 0.25*(y2[j,k]+y2[j+1,k]+y2[j,k+1]+y2[j+1,k+1])
            ccent[cid(j, k), 2] = 0.5
    faces, owner, neigh = [], [], []
    def area_center(quad):
        v = pts[quad]; c = v.mean(axis=0)
        a = np.zeros(3)
        for m in range(4):
            a += 0.5 * np.cross(v[m] - c, v[(m+1) % 4] - c)
        return a, c
    def add(quad, own, nei=None):
        a, c = area_center(quad)
        outward = (ccent[nei] - ccent[own]) if nei is not None else (c - ccent[own])
        if np.dot(a, outward) < 0.0:
            quad = quad[::-1]
        faces.append(quad); owner.append(own)
        if nei is not None: neigh.append(nei)
    # internal faces, upper-triangular order: per cell, j+1 neighbour then k+1
    for k in range(CK):
        for j in range(CJ):
            c = cid(j, k)
            if j + 1 < CJ:
                add([pid(j+1,k,0), pid(j+1,k+1,0), pid(j+1,k+1,1), pid(j+1,k,1)], c, c+1)
            if k + 1 < CK:
                add([pid(j,k+1,0), pid(j+1,k+1,0), pid(j+1,k+1,1), pid(j,k+1,1)], c, c+CJ)
    patches = []
    def patch(name, ptype, quads_owner):
        start = len(faces)
        for quad, own in quads_owner:
            add(quad, own)
        patches.append((name, ptype, start, len(faces) - start))
    patch('inlet', 'patch', [([pid(0,k,0), pid(0,k+1,0), pid(0,k+1,1), pid(0,k,1)], cid(0,k)) for k in range(CK)])
    patch('outlet', 'patch', [([pid(NJ-1,k,0), pid(NJ-1,k+1,0), pid(NJ-1,k+1,1), pid(NJ-1,k,1)], cid(CJ-1,k)) for k in range(CK)])
    patch('top', 'symmetry', [([pid(j,NK-1,0), pid(j+1,NK-1,0), pid(j+1,NK-1,1), pid(j,NK-1,1)], cid(j,CK-1)) for j in range(CJ)])
    # bottom row split by wall x-range measured on face centers
    wall_js, sym_js = [], []
    for j in range(CJ):
        xc = 0.5 * (x2[j, 0] + x2[j+1, 0])
        (wall_js if WALL_X0 < xc < WALL_X1 else sym_js).append(j)
    patch('bump', 'wall', [([pid(j,0,0), pid(j+1,0,0), pid(j+1,0,1), pid(j,0,1)], cid(j,0)) for j in wall_js])
    patch('bottomSym', 'symmetry', [([pid(j,0,0), pid(j+1,0,0), pid(j+1,0,1), pid(j,0,1)], cid(j,0)) for j in sym_js])
    fb = [([pid(j,k,0), pid(j+1,k,0), pid(j+1,k+1,0), pid(j,k+1,0)], cid(j,k)) for k in range(CK) for j in range(CJ)]
    fb += [([pid(j,k,1), pid(j+1,k,1), pid(j+1,k+1,1), pid(j,k+1,1)], cid(j,k)) for k in range(CK) for j in range(CJ)]
    patch('frontAndBack', 'empty', fb)

    from pathlib import Path
    pm = Path(case_dir) / 'constant' / 'polyMesh'
    pm.mkdir(parents=True, exist_ok=True)
    def hdr(cls, obj, note=''):
        return ('FoamFile\n{\n    version 2.0;\n    format ascii;\n'
                f'    class {cls};\n    location "constant/polyMesh";\n'
                f'    object {obj};\n}}\n' + note)
    with open(pm/'points', 'w') as fh:
        fh.write(hdr('vectorField', 'points'))
        fh.write(f'\n{len(pts)}\n(\n')
        for p in pts:
            fh.write(f'({p[0]:.17g} {p[1]:.17g} {p[2]:.17g})\n')
        fh.write(')\n')
    with open(pm/'faces', 'w') as fh:
        fh.write(hdr('faceList', 'faces'))
        fh.write(f'\n{len(faces)}\n(\n')
        for q in faces:
            fh.write(f'4({q[0]} {q[1]} {q[2]} {q[3]})\n')
        fh.write(')\n')
    for name, lst in (('owner', owner), ('neighbour', neigh)):
        with open(pm/name, 'w') as fh:
            fh.write(hdr('labelList', name))
            fh.write(f'\n{len(lst)}\n(\n')
            fh.write('\n'.join(str(v) for v in lst))
            fh.write('\n)\n')
    with open(pm/'boundary', 'w') as fh:
        fh.write(hdr('polyBoundaryMesh', 'boundary'))
        fh.write(f'\n{len(patches)}\n(\n')
        for name, ptype, start, n in patches:
            grp = ''
            if ptype == 'wall': grp = '        inGroups        1(wall);\n'
            fh.write(f'    {name}\n    {{\n        type            {ptype};\n{grp}'
                     f'        nFaces          {n};\n        startFace       {start};\n    }}\n')
        fh.write(')\n')
    print(case_dir, ':', ncell, 'cells,', len(faces), 'faces,',
          {name: n for name, _, _, n in patches})

if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2])
