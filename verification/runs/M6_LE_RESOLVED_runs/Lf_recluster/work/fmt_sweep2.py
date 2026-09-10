"""Isolate TWO unknowns in `cgns_utils plot3d2cgns`: byte order, and whether it can write a
DEGENERATE (nk=1) surface zone at all.  Layout is now KNOWN from the source (convertPlot3d,
cgns_utilities.F90:2570): read(nZones); read(all dims); per zone read(x,y,z) as real(kind=8).
Planted control: zone 2 carries z=999.5, so a conversion that 'succeeds' with wrong data fails."""
import numpy as np

def mk(nk):
    B = []
    for bi, (ni, nj) in enumerate([(3, 2), (2, 2)]):
        b = np.zeros((ni, nj, nk, 3))
        for i in range(ni):
            for j in range(nj):
                for k in range(nk):
                    b[i, j, k] = [i + 10 * bi, j * 2.0, 999.5 if bi else 7.25 + k]
        B.append(b)
    return B

def write(path, B, ie, re):
    def rec(fh, a):
        bb = np.asarray(a).tobytes()
        np.array([len(bb)], dtype=ie).tofile(fh); fh.write(bb); np.array([len(bb)], dtype=ie).tofile(fh)
    with open(path, "wb") as fh:
        rec(fh, np.array([len(B)], dtype=ie))
        rec(fh, np.array([[b.shape[0], b.shape[1], b.shape[2]] for b in B], dtype=ie).ravel())
        for b in B:
            rec(fh, np.concatenate([b[:, :, :, a].ravel(order="F") for a in range(3)]).astype(re))

for nk in (1, 3):
    for endian, ie, rp in [("big", ">i4", ">f8"), ("little", "<i4", "<f8")]:
        write(f"t_nk{nk}_{endian}.xyz", mk(nk), ie, rp)
print("ok")
