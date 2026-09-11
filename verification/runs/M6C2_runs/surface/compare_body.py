#!/usr/bin/env python3
"""Compare the BODY between two levels by section coordinates -- never by count.

WHY THIS EXISTS, from dafoam's measurements on its own artefacts:
  * A3's third coarsening COLLAPSES THE TRAILING EDGE to zero thickness;
  * A6's truncates the LEADING EDGE by 0.41 % of root chord;
  * and in BOTH cases the cell-count refinement ratio stayed a perfect 4.000/8.000.
**A refinement-ratio check cannot see a changed body.** Nor can a hash: re-coarsening
the same CGNS input twice gives a byte-different file at identical size (552,960
both ways), so md5 reports a provenance failure that does not exist.

So the body is compared geometrically: sections are taken at the SAME PHYSICAL span
stations, normalised by local chord and LE position, resampled to a common arclength
parametrisation, and compared coordinate by coordinate. Two figures are called out
by name because they are the two failure modes actually observed: TE thickness and
LE extent.

PLANT-CONTROLLED (rule 3): the reader is shown able to SEE a collapsed TE and a
truncated LE before any "bodies agree" it reports is believed. It REFUSES if a
planted change comes back undetected.
"""
import sys, numpy as np

def read_plot3d(path):
    t = open(path).read().split()
    nb = int(t[0]); p = 1; dims = []
    for _ in range(nb):
        dims.append((int(t[p]), int(t[p+1]), int(t[p+2]))); p += 3
    blocks = []
    for (a, b, c) in dims:
        n = a*b*c; arr = np.array(t[p:p+3*n], dtype=float); p += 3*n
        blocks.append(arr.reshape(3, b, a).transpose(1, 2, 0))   # (spanwise, around, 3)
    return blocks

def section_at(S, y):
    """Interpolate the section at physical span y. S is (nk+1, ni+1, 3)."""
    ys = S[:, 0, 1]
    k = int(np.clip(np.searchsorted(ys, y) - 1, 0, len(ys)-2))
    f = (y - ys[k])/(ys[k+1]-ys[k]) if ys[k+1] != ys[k] else 0.0
    return (1-f)*S[k] + f*S[k+1]

def normalise(sec):
    """(x/c, z/c) about the LE, plus the chord."""
    x, z = sec[:, 0], sec[:, 2]
    c = x.max() - x.min()
    return np.column_stack([(x - x.min())/c, (z - z.mean())/c]), c

def resample(pts, n):
    d = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
    if d[-1] == 0: return np.repeat(pts[:1], n, 0)
    d /= d[-1]; s = np.linspace(0, 1, n)
    return np.column_stack([np.interp(s, d, pts[:, k]) for k in range(2)])

def compare(SA, SB, nstat=20, nres=400):
    ymax = min(SA[:, 0, 1].max(), SB[:, 0, 1].max())
    out = []
    for y in np.linspace(0.05*ymax, 0.95*ymax, nstat):
        a, ca = normalise(section_at(SA, y)); b, cb = normalise(section_at(SB, y))
        ra, rb = resample(a, nres), resample(b, nres)
        dev = np.abs(ra - rb).max()
        te_a = a[:, 1].max() - a[:, 1].min() if False else None
        # TE thickness: spread in z among points at max x
        f = lambda p: (lambda m: p[m, 1].max() - p[m, 1].min())(p[:, 0] > p[:, 0].max() - 1e-9)
        out.append((y, dev, f(a), f(b), ca, cb))
    return out

def verdict(rows, tol=1e-4):
    dev = max(r[1] for r in rows)
    dte = max(abs(r[2]-r[3]) for r in rows)
    dch = max(abs(r[4]-r[5])/r[4] for r in rows)
    return dev, dte, dch, (dev <= tol and dte <= tol and dch <= tol)

if __name__ == "__main__":
    SA = read_plot3d(sys.argv[1])[0]
    SB = read_plot3d(sys.argv[2])[0] if len(sys.argv) > 2 else SA.copy()
    print("PLANTED CONTROLS -- the reader is shown able to SEE each failure mode first")
    ctl = []
    d0 = verdict(compare(SA, SA.copy()))
    ctl.append(("C1 identical body -> AGREE", d0[3], f"max dev {d0[0]:.2e}"))
    Bte = SA.copy(); xm = Bte[:, :, 0].max(axis=1, keepdims=True)
    m = Bte[:, :, 0] > xm - 1e-9
    for k in range(Bte.shape[0]):
        Bte[k, m[k], 2] = Bte[k, m[k], 2].mean()          # COLLAPSE the TE, as A3's does
    d1 = verdict(compare(SA, Bte))
    ctl.append(("C2 planted TE COLLAPSE -> REFUSE", not d1[3],
                f"max dev {d1[0]:.2e}, dTE {d1[1]:.2e}"))
    Ble = SA.copy()
    for k in range(Ble.shape[0]):
        x = Ble[k, :, 0]; c = x.max()-x.min()
        cut = x.min() + 0.0041*0.8059                      # A6's 0.41 % of ROOT chord
        Ble[k, x < cut, 0] = cut
    d2 = verdict(compare(SA, Ble))
    ctl.append(("C3 planted LE TRUNCATION 0.41% -> REFUSE", not d2[3],
                f"max dev {d2[0]:.2e}, dchord {d2[2]:.2e}"))
    for name, ok, det in ctl:
        print(f"  {'PASS' if ok else 'FAIL'}  {name:42s} {det}")
    if not all(ok for _, ok, _ in ctl):
        print("REFUSED: the reader was not shown able to see every planted change."); sys.exit(2)
    print()
    if len(sys.argv) > 2:
        rows = compare(SA, SB); dev, dte, dch, ok = verdict(rows)
        print(f"BODY COMPARISON  {sys.argv[1]}  vs  {sys.argv[2]}")
        print(f"  max normalised coordinate deviation : {dev:.3e}")
        print(f"  max TE-thickness difference (t/c)   : {dte:.3e}")
        print(f"  max relative chord difference       : {dch:.3e}")
        print(f"  VERDICT: {'SAME BODY' if ok else 'BODY DIFFERS -- REFUSE'}")
