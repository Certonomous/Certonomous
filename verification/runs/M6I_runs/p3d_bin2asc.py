#!/usr/bin/env python3
"""Convert the TMR generator's Fortran-unformatted multiblock PLOT3D grid to the
ASCII form OpenFOAM's plot3dToFoam reads. Verifies every record marker."""
import sys, struct

def rec(f):
    h = f.read(4)
    if len(h) < 4: return None
    n = struct.unpack('<i', h)[0]
    d = f.read(n)
    t = struct.unpack('<i', f.read(4))[0]
    assert t == n, 'record marker mismatch %d != %d' % (n, t)
    return d

src, dst = sys.argv[1], sys.argv[2]
with open(src, 'rb') as f:
    nb = struct.unpack('<i', rec(f))[0]
    assert nb == 1, 'expected 1 block, got %d' % nb
    ni, nj, nk = struct.unpack('<3i', rec(f))
    d = rec(f)
    n = ni*nj*nk
    assert len(d) == n*3*8, 'coord record %d != %d' % (len(d), n*3*8)
    v = struct.unpack('<%dd' % (n*3), d)
    assert rec(f) is None, 'unexpected trailing record'
print('blocks=%d  dims= %d %d %d  nodes=%d  cells=%d' % (nb, ni, nj, nk, n, (ni-1)*(nj-1)*(nk-1)))
with open(dst, 'w') as o:
    o.write('%d\n' % nb)
    o.write('%d %d %d\n' % (ni, nj, nk))
    for i in range(0, len(v), 6):
        o.write(' '.join('%.15g' % x for x in v[i:i+6]) + '\n')
xs = v[0:n]; ys = v[n:2*n]; zs = v[2*n:3*n]
print('bounds x[%.6f, %.6f] y[%.6f, %.6f] z[%.6f, %.6f]'
      % (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)))
