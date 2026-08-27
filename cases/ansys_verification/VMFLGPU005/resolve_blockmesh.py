#!/usr/bin/env python3
"""VMFLGPU005 frozen mesh generator -- fills blockMeshDict.template.

    resolve_blockmesh.py <template> <NX> <NY> <H1> <out>

Produces a double-graded cavity mesh: x is split into two halves of W/2, each
with NX/2 cells, geometrically graded so the FIRST CELL AT EACH VERTICAL WALL has
height H1 (integrate-to-wall). y is uniform with NY cells. It REFUSES (exit 1,
with a NAMED message -- L-357: a non-zero exit alone is not evidence a guard
fired) on any input it cannot honour, rather than emitting a silently-wrong mesh.

For a Roache r=2 triple, the launcher calls this with (NX,NY,H1) all scaled by 2
between levels, so every cell -- including the first -- refines by 2 and the three
meshes are geometrically similar (the condition an observed order requires).
"""
import sys

W = 0.0762  # cavity width (m), FROZEN geometry


def die(msg):
    sys.stderr.write("REFUSE (resolve_blockmesh VMFLGPU005): %s\n" % msg)
    sys.exit(1)


def solve_ratio(h1, L, n):
    """Cell-to-cell ratio r>0 for n geometric cells of total length L, first
    cell h1: h1*(r^n - 1)/(r - 1) = L. Bisection; returns r. Refuses if h1*n
    already overshoots L (no growing series can fit) unless h1*n ~ L (uniform)."""
    if n < 1:
        die("cells per half = %d < 1" % n)
    if h1 <= 0.0:
        die("first-cell height H1 = %g is not positive" % h1)
    if h1 * n >= L * (1.0 + 1e-12) and abs(h1 * n - L) > 1e-9 * L:
        die("H1 = %g over %d cells already exceeds the half-width %g; the first "
            "cell cannot be that large on this mesh" % (h1, n, L))
    if abs(h1 * n - L) <= 1e-9 * L:
        return 1.0  # uniform
    # f(r) = h1*(r^n - 1)/(r - 1) - L. f(1)=h1*n-L (<0 here). f grows with r.
    def f(r):
        if abs(r - 1.0) < 1e-15:
            return h1 * n - L
        return h1 * (r ** n - 1.0) / (r - 1.0) - L
    lo, hi = 1.0, 2.0
    it = 0
    while f(hi) < 0.0:
        hi *= 2.0
        it += 1
        if it > 200:
            die("could not bracket a grading ratio for h1=%g L=%g n=%d" % (h1, L, n))
    for _ in range(300):
        mid = 0.5 * (lo + hi)
        if f(mid) > 0.0:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def main(argv):
    if len(argv) != 6:
        die("usage: resolve_blockmesh.py <template> <NX> <NY> <H1> <out>")
    template, nxs, nys, h1s, out = argv[1:]
    try:
        NX, NY, H1 = int(nxs), int(nys), float(h1s)
    except ValueError:
        die("NX,NY must be ints and H1 a float; got %r %r %r" % (nxs, nys, h1s))
    if NX < 2 or NX % 2 != 0:
        die("NX = %d must be even and >= 2 (two graded halves)" % NX)
    if NY < 1:
        die("NY = %d < 1" % NY)
    n = NX // 2
    Lh = W / 2.0
    r = solve_ratio(H1, Lh, n)
    G = r ** (n - 1)          # blockMesh grading = last cell / first cell
    Ginv = 1.0 / G
    # first-half fine at x=0 (cells grow inward, ratio G>1); second-half fine at
    # x=W (cells shrink, ratio 1/G).
    xgrading = "( (0.5 0.5 %.10g) (0.5 0.5 %.10g) )" % (G, Ginv)
    try:
        txt = open(template).read()
    except OSError as e:
        die("cannot read template %s: %s" % (template, e))
    for k in ("__NX__", "__NY__", "__XGRADING__"):
        if k not in txt:
            die("template %s is missing placeholder %s" % (template, k))
    txt = txt.replace("__NX__", str(NX)).replace("__NY__", str(NY)).replace("__XGRADING__", xgrading)
    try:
        open(out, "w").write(txt)
    except OSError as e:
        die("cannot write %s: %s" % (out, e))
    sys.stderr.write("resolve_blockmesh VMFLGPU005: NX=%d NY=%d H1=%g -> r=%.6f "
                     "G=%.6f (cells %d)\n" % (NX, NY, H1, r, G, NX * NY))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
