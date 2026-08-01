"""Readers for NASA TMR PLOT3D bump grids (formatted, whole-format)."""
import gzip, numpy as np

def _tokens(path):
    op = gzip.open if str(path).endswith(".gz") else open
    with op(path, "rt") as fh:
        return fh.read().split()

def read_p3dfmt(path):
    """3D whole-format single-block: nblocks; ni nj nk; then x,y,z arrays
    each of size ni*nj*nk, i fastest."""
    tok = _tokens(path)
    nb = int(tok[0]); assert nb == 1, nb
    ni, nj, nk = (int(v) for v in tok[1:4])
    data = np.array([float(v) for v in tok[4:]])
    assert data.size == 3 * ni * nj * nk, (data.size, ni, nj, nk)
    x, y, z = data.reshape(3, nk, nj, ni)  # fortran i-fastest -> C order (k,j,i)
    return ni, nj, nk, x, y, z

def read_p2dfmt(path):
    tok = _tokens(path)
    nb = int(tok[0]); assert nb == 1, nb
    ni, nj = (int(v) for v in tok[1:3])
    data = np.array([float(v) for v in tok[3:]])
    assert data.size == 2 * ni * nj, (data.size, ni, nj)
    x, y = data.reshape(2, nj, ni)
    return ni, nj, x, y
