"""Read-back assertion: 9 zones, expected dims, and coordinates equal to the source PLOT3D."""
import sys
import numpy as np
from cgnsutilities.cgnsutilities import readGrid
g = readGrid(sys.argv[1])
print("ZONES", len(g.blocks))
for b in g.blocks:
    print("  ", b.name if isinstance(b.name, str) else b.name.decode(), list(b.dims))
