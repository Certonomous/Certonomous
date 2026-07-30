#!/usr/bin/env python
"""
Re-run of the dR/dXv link test from probeChainLinksA5.py, fixed.

That earlier attempt injected an independent random perturbation direction
into Xv PER MPI RANK (np=4). Processor-boundary mesh points are physically
duplicated across neighboring ranks and must receive an IDENTICAL
perturbation; independent per-rank randoms broke that, producing 1.23
million OpenFOAM face-area-mismatch warnings and an FD side that DIVERGED
(not converged) under step refinement -- the signature of an invalid
parallel mesh, not a real derivative.

Fix used here: run SERIAL (np=1). With a single rank there is no processor
boundary and therefore no possibility of the per-rank-inconsistent
perturbation bug -- any direction is trivially globally consistent. This is
simpler than constructing an actual FFD/warp-derived Xv direction (the
alternative fix named in the record) and is methodologically consistent
with how every other single-link isolation test in this session
(probeA5DiagRatio.py, probeA5HandComposition.py, probeA5TwoSidedFormula.py,
probeA5MatvecMaxCorrected.py) was run -- all serial, all valid, all
cross-checked against parallel results elsewhere in this investigation
(mesh.warpDeriv agreed in both serial and 4-rank parallel for A1, per
PROOF.md section 15).

Method unchanged otherwise: one real primal solve for baseline W0, Xv0;
perturb Xv DIRECTLY (relative-magnitude-scaled... actually flat random, Xv
has no cross-scale problem, matching every prior warpDeriv script in this
investigation), hold W fixed, FD the residual via getResiduals(); compare to
calcJacTVecProduct(volCoord -> residual), exactly as DAFoamSolver.apply_linear
calls it in the real adjoint chain.
"""
import os
import time
import numpy as np
import openmdao.api as om
from mphys.multipoint import Multipoint
from dafoam.mphys import DAFoamBuilder
from mphys.scenario_aerodynamic import ScenarioAerodynamic
from pygeo.mphys import OM_DVGEOCOMP
from pygeo import geo_utils
from mpi4py import MPI

comm = MPI.COMM_WORLD
assert comm.size == 1, "serial by design -- see docstring for why this is the chosen fix"

U0 = 8.4
daOptionsAero = {
    "solverName": "DASimpleFoam", "designSurfaces": ["ubend"], "useAD": {"mode": "reverse"},
    "primalMinResTol": 1e-8, "primalMinResTolDiff": 1e7, "writeMinorIterations": True,
    "wallDistanceMethod": "daCustom", "primalBC": {"useWallFunction": True},
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


class Top(Multipoint):
    def setup(self):
        b = DAFoamBuilder(daOptionsAero, meshOptions, scenario="aerodynamic")
        b.initialize(self.comm)
        self.dafoam_builder = b
        self.add_subsystem("dvs", om.IndepVarComp(), promotes=["*"])
        self.add_subsystem("mesh_aero", b.get_mesh_coordinate_subsystem())
        self.add_subsystem("geometry_aero", OM_DVGEOCOMP(file="FFD/UBendDuctFFDSym.xyz", type="ffd"))
        self.mphys_add_scenario("scenario", ScenarioAerodynamic(aero_builder=b))
        self.connect("mesh_aero.x_aero0", "geometry_aero.x_aero_in")
        self.connect("geometry_aero.x_aero0", "scenario.x_aero")
        self.add_subsystem("OBJ", om.ExecComp("val = TP1 - TP2"))

    def configure(self):
        super().configure()
        points_aero = self.mesh_aero.mphys_get_surface_mesh()
        self.geometry_aero.nom_add_discipline_coords("aero", points_aero)
        pts = self.geometry_aero.nom_getDVGeo().getLocalIndex(0)
        indexList = []
        indexList.extend(pts[7:16, 1, :].flatten())
        PS = geo_utils.PointSelect("list", indexList)
        n = self.geometry_aero.nom_addLocalDV(dvName="shapexUpper", pointSelect=PS, axis="x")
        self.dvs.add_output("shapexUpper", val=np.array([0.0] * n))
        self.connect("shapexUpper", "geometry_aero.shapexUpper")
        self.add_design_var("shapexUpper", lower=-0.04, upper=0.04, scaler=25.0)
        self.connect("scenario.aero_post.TP1", "OBJ.TP1")
        self.connect("scenario.aero_post.TP2", "OBJ.TP2")
        self.add_objective("OBJ.val", scaler=1.0)


t0 = time.time()
prob = om.Problem(reports=None)
prob.model = Top()
prob.setup(mode="rev")
prob.run_model()
print("FIXEDDRDXV === primal done t=%.1fs ===" % (time.time() - t0), flush=True)

DASolver = prob.model.dafoam_builder.DASolver
stateName = "%s_states" % DASolver.getOption("discipline")
residualName = "%s_residuals" % DASolver.getOption("discipline")
W0 = DASolver.getStates().copy()
Xv0 = DASolver.mesh.getSolverGrid().copy()
nW = W0.size
nXv = Xv0.size
print("FIXEDDRDXV nW=%d nXv=%d nRanks=1 (no processor boundary possible)" % (nW, nXv), flush=True)

DASolver.setStates(W0)
DASolver.setVolCoords(Xv0)


def restore():
    DASolver.setStates(W0)
    DASolver.setVolCoords(Xv0)


for seedNum in [2026, 42, 777]:
    np.random.seed(seedNum + 13)
    dXv = np.random.uniform(-1.0, 1.0, size=nXv)  # flat random, no cross-scale problem, single rank so no consistency issue

    np.random.seed(seedNum + 19)
    w_R = np.random.uniform(-1.0, 1.0, size=nW)

    for h in [1e-4, 1e-5]:
        restore()
        DASolver.setVolCoords(Xv0 + h * dXv)
        R_p = DASolver.getResiduals().copy()
        DASolver.setVolCoords(Xv0 - h * dXv)
        R_m = DASolver.getResiduals().copy()
        restore()

        FD_dR = (R_p - R_m) / (2.0 * h)
        FD_scalar = float(np.dot(w_R, FD_dR))

        product = np.zeros(nXv)
        DASolver.solverAD.calcJacTVecProduct("aero_vol_coords", "volCoord", Xv0, residualName, "residual", w_R, product)
        AN_scalar = float(np.dot(product, dXv))

        absdiff = FD_scalar - AN_scalar
        relerr = abs(absdiff) / (abs(FD_scalar) + 1e-300)
        sign = "agree" if (FD_scalar * AN_scalar) > 0 else "FLIPPED"
        print(
            "FIXEDDRDXV_RESULT seed=%d h=%.1e FD=%.8e AN=%.8e rel_err=%.6e sign=%s"
            % (seedNum, h, FD_scalar, AN_scalar, relerr, sign),
            flush=True,
        )

restore()
print("FIXEDDRDXV_DONE t=%.1fs" % (time.time() - t0), flush=True)
