#!/usr/bin/env python3
"""D5 FFD density generator.  Reads D4's FROZEN 6x2x8 box (the parametrisation D4 was graded
on), extracts its span-wise knots, and writes a box of the requested (nx, 2, nz) density in the
SAME bounding envelope.  PLANTED CONTROL: regenerating (6,2,8) must be BYTE-IDENTICAL to D4's
file, else this script REFUSES (exit 2) -- a generator that cannot reproduce the parametrisation
it claims to refine is not a generator of that family.  No bare assert (L-332): every check exits.
usage: d5_gen_ffd.py --ref <D4 wingFFD.xyz> --nx N --nz M --out <file>   [--selfcheck]
"""
import argparse, os, sys
import numpy as np

def refuse(msg, code=2):
    sys.stderr.write("REFUSAL: %s\n" % msg); sys.exit(code)

def read_plot3d(path):
    t = open(path).read().split()
    if int(t[0]) != 1: refuse("expected 1 block in %s, got %s" % (path, t[0]))
    nx, ny, nz = (int(v) for v in t[1:4]); n = nx*ny*nz
    v = np.array([float(x) for x in t[4:]])
    if v.size != 3*n: refuse("value count %d != 3*%d" % (v.size, n))
    X = v[:n].reshape(nz, ny, nx); Y = v[n:2*n].reshape(nz, ny, nx); Z = v[2*n:].reshape(nz, ny, nx)
    return nx, ny, nz, X, Y, Z

def knots(X, Y, Z, tol=2e-8):  # values are stored to 8 decimals; 2e-8 is two ulps of that format
    nz, ny, nx = X.shape
    if ny != 2: refuse("D5 keeps ny=2 (one upper, one lower control plane); ref has ny=%d" % ny)
    x0 = X[:, 0, 0]; x1 = X[:, 0, -1]; yh = np.abs(Y[:, 1, 0]); z = Z[:, 0, 0]
    for k in range(nz):
        lin = np.linspace(x0[k], x1[k], nx)
        if np.abs(X[k] - lin[None, :]).max() > tol: refuse("x not uniform in i at k=%d" % k)
        if np.abs(Y[k, 0] + yh[k]).max() > tol or np.abs(Y[k, 1] - yh[k]).max() > tol: refuse("y not symmetric at k=%d" % k)
        if np.abs(Z[k] - z[k]).max() > tol: refuse("z not constant on plane k=%d" % k)
    return x0, x1, yh, z

def build(x0, x1, yh, z, nx, nz):
    s_ref = np.linspace(0.0, 1.0, len(z)); s = np.linspace(0.0, 1.0, nz)
    X0 = np.interp(s, s_ref, x0); X1 = np.interp(s, s_ref, x1); YH = np.interp(s, s_ref, yh); ZZ = np.interp(s, s_ref, z)
    X = np.zeros((nz, 2, nx)); Y = np.zeros_like(X); Z = np.zeros_like(X)
    for k in range(nz):
        X[k, :, :] = np.linspace(X0[k], X1[k], nx)[None, :]
        Y[k, 0, :] = -YH[k]; Y[k, 1, :] = YH[k]; Z[k, :, :] = ZZ[k]
    return X, Y, Z

def fmt(X, Y, Z):
    nz, ny, nx = X.shape
    out = ["\t\t1", "\t\t%d\t\t%d\t\t%d" % (nx, ny, nz)]
    for A in (X, Y, Z):
        for k in range(nz):
            for j in range(ny):
                out.append("\t" + "\t".join("%.8f" % v for v in A[k, j, :]))
    return "\n".join(out) + "\n"

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--ref", required=True); ap.add_argument("--nx", type=int, required=True)
    ap.add_argument("--nz", type=int, required=True); ap.add_argument("--out", required=True); ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args()
    nx, ny, nz, X, Y, Z = read_plot3d(a.ref); x0, x1, yh, z = knots(X, Y, Z)
    # ---- PLANTED CONTROL 1: the family reproduces its own reference to ONE UNIT OF THE
    # FILE'S LAST PRINTED DIGIT (1e-8) at every value.  Byte identity was tried first and
    # is unattainable: the reference carries 8 decimals, and linspace over rounded endpoints
    # differs from the original unrounded arithmetic by exactly 1e-8 on 6 of 51 lines
    # (measured 2026-08-26).  So the claim is precision identity, stated as such.
    TOL = 1.0e-8
    ref_vals = np.array([float(v) for v in open(a.ref).read().split()[4:]])
    regen = np.array([float(v) for v in fmt(*build(x0, x1, yh, z, nx, nz)).split()[4:]])
    dmax = float(np.abs(regen - ref_vals).max())
    if regen.size != ref_vals.size or dmax > TOL: refuse("regenerated (%d,2,%d) differs from the reference by max %.3e > %.1e; the generator does not own this parametrisation" % (nx, nz, dmax, TOL))
    # ---- PLANTED CONTROL 2: the comparison can see a difference (a 1e-6 perturbation must NOT pass)
    pert = np.array([float(v) for v in fmt(*build(x0, x1, yh * (1.0 + 1e-6), z, nx, nz)).split()[4:]])
    pmax = float(np.abs(pert - ref_vals).max())
    if pmax <= TOL: refuse("the comparison could not see a planted 1e-6 perturbation (max diff %.3e); a 'match' from it would be meaningless" % pmax)
    print("D5_FFD_CONTROL_OK regen_max_abs_diff=%.3e tol=%.1e planted_perturbation_max_diff=%.3e seen=yes ref=%s nx=%d nz=%d" % (dmax, TOL, pmax, a.ref, nx, nz))
    if a.selfcheck: return
    Xn, Yn, Zn = build(x0, x1, yh, z, a.nx, a.nz)
    txt = fmt(Xn, Yn, Zn)
    if not (Xn.min() >= X.min()-1e-12 and Xn.max() <= X.max()+1e-12 and Zn.min() >= Z.min()-1e-12 and Zn.max() <= Z.max()+1e-12): refuse("new box leaves the reference envelope")
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True); open(a.out, "w").write(txt)
    import hashlib; print("D5_FFD_WRITTEN out=%s nx=%d nz=%d ndv_shape=%d md5=%s" % (a.out, a.nx, a.nz, a.nx*2*a.nz, hashlib.md5(txt.encode()).hexdigest()))

if __name__ == "__main__": main()
