# P2 PREDICTION, DERIVED FROM THE BLOCK STRUCTURE ALONE.
# It does NOT read P1's achieved counts (11,908 / 11,196 / 13,312) and must not.
# Inputs: the 26-block surface CGNS and the extrusion node count N.
import sys
from collections import Counter
import numpy as np
from cgnsutilities.cgnsutilities import readGrid

surf, N = sys.argv[1], int(sys.argv[2])
g = readGrid(surf)
nk_cells = N - 1                      # cell layers in the extrusion direction

wing = 0
edge_count = Counter()
for b in g.blocks:
    d = list(b.dims)
    ni, nj = [x for x in d if x > 1][:2]
    wing += (ni - 1) * (nj - 1)       # one face per surface cell at k=0
    c = b.coords.reshape(d[0], d[1], d[2], 3)[:, :, 0, :]
    # the four boundary runs of this block, as consecutive node pairs
    runs = [c[0, :, :], c[-1, :, :], c[:, 0, :], c[:, -1, :]]
    for r in runs:
        for t in range(r.shape[0] - 1):
            a = tuple(np.round(r[t], 9)); bb = tuple(np.round(r[t + 1], 9))
            edge_count[tuple(sorted([a, bb]))] += 1

hist = Counter(edge_count.values())
free_edges = sum(1 for v in edge_count.values() if v == 1)
farfield = wing                        # one face per surface cell at k = N
symmetry = free_edges * nk_cells

print("DERIVED FROM BLOCK STRUCTURE ONLY — no P1 output consulted")
print("  blocks                       : %d" % len(g.blocks))
print("  surface cells (= wing faces) : %d" % wing)
print("  extrusion cell layers (N-1)  : %d" % nk_cells)
print("  block-boundary edge sharing  : %s" % dict(sorted(hist.items())))
print("  FREE perimeter edges (shared once) : %d" % free_edges)
print()
print("  PREDICTED wing     = %d" % wing)
print("  PREDICTED farfield = %d" % farfield)
print("  PREDICTED symmetry = %d x %d = %d" % (free_edges, nk_cells, symmetry))
print("  PREDICTED TOTAL    = %d" % (wing + farfield + symmetry))
print("  mesh's actual boundary face count is 36416 -> %s"
      % ("CONSISTENT" if wing + farfield + symmetry == 36416 else "*** INCONSISTENT — the model is wrong ***"))
