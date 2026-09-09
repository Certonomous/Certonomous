#!/usr/bin/env python3
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mk_ortho as M

mode = sys.argv[1]        # "normal" | "transfinite"
outdir = sys.argv[2]
nlayers = int(sys.argv[3]) if len(sys.argv) > 3 else 150
nofill = (sys.argv[4] == "nofill") if len(sys.argv) > 4 else True

M.N_NORM = nlayers
M.ORTHO_MODE = mode
t0 = time.time()
g = M.M6Geometry(verbose=False)
g.z_tip = g.z_tip_measured
mm = M.Mesh(1, g, verbose=False, nofill=nofill)
mm.cells()
mm.build()
mm.write(outdir)
dt = time.time() - t0
print(f"MODE={mode} nofill={nofill} NN={mm.NN} cells={mm.nC+mm.nF} "
      f"points={mm.n_points} faces={len(mm.faces)} prisms={mm.n_prism} "
      f"delta0_um={mm.delta0*1e6:.5f} min_face_area={mm.min_face_area:.3e} wall_s={dt:.1f}")
