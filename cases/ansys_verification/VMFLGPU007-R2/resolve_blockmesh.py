#!/usr/bin/env python3
"""VMFLGPU007 -- resolve blockMeshDict.template's placeholders for one level.

usage: resolve_blockmesh.py <template> <NXI> <NXD> <NYU> <NYL> <H1> <out>

THE POINT OF THIS FILE.  The wall-normal first-cell height H1 is a REGISTERED
CONSTANT held IDENTICAL at every level (PREREGISTRATION: mesh-sensitivity
family, not a Roache triple), so the grading ratios cannot be constants -- they
must be SOLVED per level so that d1 == H1 exactly whatever the cell count.
Hand-tuned grading numbers would make H1 approximately fixed, and "approximately
fixed" is precisely the thing that would smuggle a model change into what is
supposed to be a mesh change.

MATH.  simpleGrading's expansion ratio G = (last cell)/(first cell) over a
segment of length L with n cells gives a geometric progression of common ratio
r = G**(1/(n-1)) and

    L = d1 * (r**n - 1)/(r - 1)     =>     d1 = L * (r - 1)/(r**n - 1)

d1 is monotone decreasing in G, so G is found by bisection.  Blocks A and B
carry the two-sided form ((0.5 0.5 GU) (0.5 0.5 1/GU)) over y = 1..5: each half
is length 2 with NYU/2 cells, fine at BOTH walls.  Block C is one-sided over
y = 0..1 with NYL cells, fine at the heated wall.

REFUSALS, each an explicit branch -- never `assert`, because python3 -O strips
assert statements and a guard that evaporates under optimisation is not a guard:
  * H1 >= L/n for any block  -> REFUSE.  The wall cell would have to be the
    LARGEST, which no expansion ratio >= 1 can produce.  This is the
    arithmetic limit that makes L3 the last admissible level of this family
    (see MESH_PREFREEZE_RECORD.md).
  * NYU odd                  -> REFUSE (the two-sided form halves it).
  * achieved d1 != H1        -> REFUSE.
  * any __PLACEHOLDER__ left -> REFUSE, naming it.
"""
import re
import sys

import sys

def d1_of_G(L, n, G):
    if abs(G - 1.0) < 1e-14:
        return L / n
    r = G ** (1.0 / (n - 1))
    return L * (r - 1.0) / (r ** n - 1.0)

def solve_G(L, n, target_d1):
    if target_d1 >= L / n:          # would need the wall cell to be the largest
        raise SystemExit("REFUSE: target first cell %.6g >= uniform spacing %.6g "
                         "for L=%g n=%d -- grading cannot be >1 and this level is "
                         "not admissible" % (target_d1, L / n, L, n))
    lo, hi = 1.0, 1e6
    for _ in range(300):
        mid = (lo + hi) / 2
        if d1_of_G(L, n, mid) > target_d1:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2

TEMPLATE = open(sys.argv[1]).read()
NXI, NXD, NYU, NYL, H1 = (int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]),
                          int(sys.argv[5]), float(sys.argv[6]))
if NYU % 2:
    raise SystemExit("REFUSE: NYU must be even (two-sided grading splits it in half)")

# blocks A/B: y from 1 to 5, L=4, two-sided -> each half L/2=2 with NYU/2 cells
GU = solve_G(2.0, NYU // 2, H1)
# block C: y from 0 to 1, L=1, one-sided from the heated wall
GC = solve_G(1.0, NYL, H1)

got_u = d1_of_G(2.0, NYU // 2, GU)
got_c = d1_of_G(1.0, NYL, GC)
# ASSERTION, as an explicit branch (never `assert` -- python3 -O strips those)
for nm, got in (("upper", got_u), ("stepblock", got_c)):
    if abs(got - H1) > 1e-9 * max(1.0, H1):
        raise SystemExit("REFUSE: %s first cell solved to %.12g, target %.12g" % (nm, got, H1))

out = (TEMPLATE.replace("__NXI__", str(NXI)).replace("__NXD__", str(NXD))
       .replace("__NYU__", str(NYU)).replace("__NYL__", str(NYL))
       .replace("__GUINV__", "%.10g" % (1.0 / GU))
       .replace("__GU__", "%.10g" % GU).replace("__GC__", "%.10g" % GC)
       .replace("__H1__", "%.10g" % H1))
# The placeholder class MUST include the underscore.  DRIVEN, and it caught a
# real defect: with r"__[A-Z0-9]+__" a typo like `__GC_TYPO__` does NOT match --
# the guard passed and an unresolved placeholder reached the blockMeshDict.
left = sorted(set(re.findall(r"__[A-Z0-9_]+__", out)))
if left:
    raise SystemExit("REFUSE: unresolved placeholder(s) remain in the generated "
                     "blockMeshDict: %s -- refusing to write a dict OpenFOAM would "
                     "either fail to parse or, worse, parse with a literal token in "
                     "it" % left)
open(sys.argv[7], "w").write(out)
cells = NXI * NYU + NXD * NYU + NXD * NYL
print("  GU=%.6f  GUINV=%.6f  GC=%.6f   d1_upper=%.9f  d1_step=%.9f (target %.9f)"
      % (GU, 1.0 / GU, GC, got_u, got_c, H1))
print("  PREDICTED cell count = NXI*NYU + NXD*NYU + NXD*NYL = %d*%d + %d*%d + %d*%d = %d"
      % (NXI, NYU, NXD, NYU, NXD, NYL, cells))
