#!/usr/bin/env python
"""
A5 analog of the airfoil's decisive `probeHandComposition.py` Stage 2 test.

A1's original warpDeriv test (sections 15/16/18 of PROOF.md, and A5's own
prior-session `probeWarpDerivA5.py`, byte-identical method) never tested
mesh.warpDeriv ALONE: its FD side reached the mesh via DVGeo.update(shape),
composing DVGeo's shape-to-surface map WITH the physical warp, and its
analytic side dotted warpDeriv(w) against DVGeo's OWN forward Jacobian
(totalSensitivityProd) -- also a composition. A parallel session on A1 showed
this leaves an unclosed ambiguity: a persistent FD-vs-analytic gap could be
warpDeriv's own error, OR it could be DVGeo's FFD update itself being
NONLINEAR (a real re-evaluation of a B-spline volume, not just its own linear
Jacobian) -- the original test could not distinguish the two. The fix: perturb
surface coordinates (Xs) DIRECTLY along eta = dXs/dShape_idx (DVGeo's own
already-trusted Jacobian column, computed once), bypassing DVGeo.update()
entirely on the FD side. If this new FD matches the ORIGINAL (DVGeo.update()-
based) FD closely, DVGeo nonlinearity is ruled out and the persistent gap can
only be warpDeriv's own error. If it does NOT match, DVGeo nonlinearity was a
real confound the whole time.

A5's own warpDeriv clearance (idx8/idx17 "agree to 0.32-1.30%, no sign flip",
prior-session addendum) used the EXACT same composed structure -- untested for
this same ambiguity. A5's DV construction (`nom_addLocalDV`, ONE FFD point
moving along ONE axis per DV) is structurally about as simple/linear an FFD
operation as this framework offers, so DVGeo nonlinearity mattering here would
itself be a notable finding either way. This script runs the same two-stage
check on A5's controls (idx2, idx26) and flipped components (idx8, idx17),
same seeds (2026, 42) as the original A5 warpDeriv test, for direct
comparability. Pure geometry, no CFD.
"""
import os
import time
import numpy as np
from mpi4py import MPI
from dafoam.mphys import DAFoamBuilder
from pygeo import DVGeometry, geo_utils

comm = MPI.COMM_WORLD
if comm.size != 1:
    raise RuntimeError("serial only")

U0 = 8.4
daOptionsAero = {
    "solverName": "DASimpleFoam",
    "designSurfaces": ["ubend"],
    "useAD": {"mode": "reverse"},
    "primalMinResTol": 1e-8,
    "primalMinResTolDiff": 1e7,
    "writeMinorIterations": True,
    "wallDistanceMethod": "daCustom",
    "primalBC": {"useWallFunction": True},
    "function": {
        "TP1": {"type": "totalPressure", "source": "patchToFace", "patches": ["inlet"], "scale": 1.0, "addToAdjoint": True},
        "TP2": {"type": "totalPressure", "source": "patchToFace", "patches": ["outlet"], "scale": 1.0, "addToAdjoint": True},
        "HFX": {"type": "wallHeatFlux", "source": "patchToFace", "patches": ["ubend"], "scale": 1.0, "addToAdjoint": False},
    },
    "adjStateOrdering": "cell",
    "adjEqnOption": {"gmresRelTol": 1e-5, "gmresTolDiff": 1e4, "pcFillLevel": 2,
                      "jacMatReOrdering": "natural", "gmresMaxIters": 3000, "gmresRestart": 3000},
    "normalizeStates": {"U": U0, "p": (U0 * U0) / 2.0, "nuTilda": 1e-3, "phi": 1.0, "T": 300},
    "inputInfo": {"aero_vol_coords": {"type": "volCoord", "components": ["solver", "function"]}},
    "outputInfo": {"q_convect": {"type": "thermalCouplingOutput", "patches": ["ubend"], "components": ["thermalCoupling"]}},
}
meshOptions = {"gridFile": os.getcwd(), "fileType": "OpenFOAM", "symmetryPlanes": []}

t0 = time.time()
builder = DAFoamBuilder(daOptionsAero, meshOptions, scenario="aerodynamic")
builder.initialize(comm)
DASolver = builder.DASolver
mesh = DASolver.mesh
print("HANDCOMP_A5 === builder init done, t=%.1fs ===" % (time.time() - t0), flush=True)

xs0 = DASolver.getSurfaceCoordinates(DASolver.designSurfacesGroup).copy()
DVGeo = DVGeometry(os.path.join(os.getcwd(), "FFD", "UBendDuctFFDSym.xyz"))
ptSetName = "x_aero0"
DVGeo.addPointSet(xs0, ptSetName)
pts = DVGeo.getLocalIndex(0)
indexList = list(pts[7:16, 1, :].flatten())
PS = geo_utils.PointSelect("list", indexList)
nShape = DVGeo.addLocalDV("shapexUpper", axis="x", pointSelect=PS)
assert nShape == 27


def set_shape(vec):
    DVGeo.setDesignVars({"shapexUpper": np.array(vec)})


def warp_via_dvgeo(shapeVec):
    set_shape(shapeVec)
    xs = DVGeo.update(ptSetName)
    DASolver.setSurfaceCoordinates(xs, DASolver.designSurfacesGroup)
    mesh.warpMesh()
    return mesh.getSolverGrid().copy()


def warp_via_direct_xs(xs):
    DASolver.setSurfaceCoordinates(xs, DASolver.designSurfacesGroup)
    mesh.warpMesh()
    return mesh.getSolverGrid().copy()


for idx in [2, 8, 17, 26]:
    for seedNum in [2026, 42]:
        h = 1e-4
        np.random.seed(seedNum)
        Xv0 = warp_via_dvgeo(np.zeros(nShape))
        nXvLocal = Xv0.size
        w = np.random.random(nXvLocal).astype("d")

        # --- eta = dXs/dShape_idx, DVGeo's own trusted analytic Jacobian ---
        set_shape(np.zeros(nShape))
        DVGeo.update(ptSetName)
        seedDV = {"shapexUpper": np.zeros(nShape)}
        seedDV["shapexUpper"][idx] = 1.0
        eta = DVGeo.totalSensitivityProd(seedDV, ptSetName).reshape(xs0.shape)

        # --- ORIGINAL FD: perturb shape, let DVGeo.update() compute xs ---
        ePlus = np.zeros(nShape)
        ePlus[idx] = h
        eMinus = np.zeros(nShape)
        eMinus[idx] = -h
        Xv_p_orig = warp_via_dvgeo(ePlus)
        Xv_m_orig = warp_via_dvgeo(eMinus)
        FD_dXv_orig = (Xv_p_orig - Xv_m_orig) / (2.0 * h)
        FD_scalar_orig = float(np.dot(w, FD_dXv_orig))

        # --- AN: warpDeriv(w) dotted with DVGeo's own eta (unchanged method) ---
        set_shape(np.zeros(nShape))
        xs_base = DVGeo.update(ptSetName)
        DASolver.setSurfaceCoordinates(xs_base, DASolver.designSurfacesGroup)
        mesh.warpMesh()
        mesh.warpDeriv(w)
        dXs_seed = mesh.getdXs()
        dXs_seed = DASolver.mapVector(dXs_seed, DASolver.allWallsGroup, DASolver.designSurfacesGroup)
        AN_scalar = float(np.dot(dXs_seed.flatten(), eta.flatten()))

        # --- STAGE 2: perturb Xs DIRECTLY along eta, bypassing DVGeo.update() ---
        xs_plus = xs_base + h * eta
        xs_minus = xs_base - h * eta
        Xv_p_direct = warp_via_direct_xs(xs_plus)
        Xv_m_direct = warp_via_direct_xs(xs_minus)
        # restore
        DASolver.setSurfaceCoordinates(xs_base, DASolver.designSurfacesGroup)
        mesh.warpMesh()
        FD_dXv_direct = (Xv_p_direct - Xv_m_direct) / (2.0 * h)
        FD_scalar_direct = float(np.dot(w, FD_dXv_direct))

        dvgeo_nonlin_diff = FD_scalar_orig - FD_scalar_direct
        dvgeo_nonlin_relerr = abs(dvgeo_nonlin_diff) / (abs(FD_scalar_orig) + 1e-300)

        absdiff = AN_scalar - FD_scalar_direct
        relerr = abs(absdiff) / (abs(FD_scalar_direct) + 1e-300)
        sign = "agree" if (AN_scalar * FD_scalar_direct) > 0 else "FLIPPED"

        print(
            "HANDCOMP_A5_RESULT idx=%d seed=%d h=%.1e "
            "FD_orig=%.8e FD_direct=%.8e dvgeo_nonlin_relerr=%.6e "
            "AN=%.8e vs_FD_direct_relerr=%.6e sign=%s"
            % (idx, seedNum, h, FD_scalar_orig, FD_scalar_direct, dvgeo_nonlin_relerr,
               AN_scalar, relerr, sign),
            flush=True,
        )

print("HANDCOMP_A5_DONE t=%.1fs" % (time.time() - t0), flush=True)
