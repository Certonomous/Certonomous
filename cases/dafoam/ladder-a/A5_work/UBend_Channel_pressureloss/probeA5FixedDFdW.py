#!/usr/bin/env python
"""
Re-run of the dF/dW link test from probeChainLinksA5.py, fixed.

That earlier attempt got FD=0.0 exactly in all 12 measurements because
DASolver.evalFunctions() calls self.solver.getTimeOpFuncVal(functionName),
which reads a value from functionTimeSteps_ -- an array recorded DURING the
primal solve's own time loop (confirmed in DASolver.C:
`DASolver::getTimeOpFuncVal`, reading `daTimeOpPtrList_[idxI].compute(...)`
over the STORED trajectory) -- not a live recomputation from the state
DASolver.setStates() had just perturbed.

Fix: DASolver.solver.calcFunction(functionName), confirmed in the same
source (DASolver.C: `DASolver::calcFunction`, calling `daFunction.calcFunction()`
directly, no stored history involved) -- a genuine live, single-evaluation
function value from the CURRENT OF field.

Method unchanged from probeChainLinksA5.py: one real primal solve for a
converged baseline W0, then perturb W0 directly (relative-magnitude random
direction dW, no mesh/DVGeo involved -- direct injection into the link's own
input space) and compare a live central FD of TP1/TP2 against
calcJacTVecProduct(stateVar -> function), exactly as
DAFoamFunctions.compute_jacvec_product calls it in the real adjoint chain.
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
assert comm.size == 1

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
print("FIXEDDFDW === primal done t=%.1fs ===" % (time.time() - t0), flush=True)

DASolver = prob.model.dafoam_builder.DASolver
stateName = "%s_states" % DASolver.getOption("discipline")
W0 = DASolver.getStates().copy()
nW = W0.size
DASolver.setStates(W0)


def evalF_live(funcName):
    # THE FIX: calcFunction (live, single evaluation), not evalFunctions()
    # (which is getTimeOpFuncVal, a stored-time-history getter).
    return float(DASolver.solver.calcFunction(funcName))


# sanity: does calcFunction reproduce the known converged baseline TP1/TP2?
tp1_base = evalF_live("TP1")
tp2_base = evalF_live("TP2")
tp1_om = float(prob.get_val("scenario.aero_post.TP1"))
tp2_om = float(prob.get_val("scenario.aero_post.TP2"))
print("FIXEDDFDW sanity: calcFunction TP1=%.10f (OM=%.10f, diff=%.3e)  TP2=%.10f (OM=%.10f, diff=%.3e)" % (
    tp1_base, tp1_om, tp1_base - tp1_om, tp2_base, tp2_om, tp2_base - tp2_om), flush=True)

for seedNum in [2026, 42]:
    np.random.seed(seedNum)
    r = np.random.uniform(-1.0, 1.0, size=nW)
    dW = W0 * r

    for h in [1e-4, 1e-5]:
        DASolver.setStates(W0 + h * dW)
        TP1_p = evalF_live("TP1")
        TP2_p = evalF_live("TP2")
        DASolver.setStates(W0 - h * dW)
        TP1_m = evalF_live("TP1")
        TP2_m = evalF_live("TP2")
        DASolver.setStates(W0)

        FD_TP1 = (TP1_p - TP1_m) / (2.0 * h)
        FD_TP2 = (TP2_p - TP2_m) / (2.0 * h)

        for funcName, FD_val in [("TP1", FD_TP1), ("TP2", FD_TP2)]:
            seed = np.array([1.0])
            product = np.zeros_like(W0)
            DASolver.solverAD.calcJacTVecProduct(stateName, "stateVar", W0, funcName, "function", seed, product)
            AN_scalar = float(np.dot(product, dW))
            absdiff = FD_val - AN_scalar
            relerr = abs(absdiff) / (abs(FD_val) + 1e-300)
            sign = "agree" if (FD_val * AN_scalar) > 0 else "FLIPPED"
            print(
                "FIXEDDFDW_RESULT func=%s seed=%d h=%.1e FD=%.8e AN=%.8e rel_err=%.6e sign=%s"
                % (funcName, seedNum, h, FD_val, AN_scalar, relerr, sign),
                flush=True,
            )

        FD_OBJ = FD_TP1 - FD_TP2
        product1 = np.zeros_like(W0)
        DASolver.solverAD.calcJacTVecProduct(stateName, "stateVar", W0, "TP1", "function", np.array([1.0]), product1)
        product2 = np.zeros_like(W0)
        DASolver.solverAD.calcJacTVecProduct(stateName, "stateVar", W0, "TP2", "function", np.array([-1.0]), product2)
        AN_OBJ = float(np.dot(product1 + product2, dW))
        absdiff = FD_OBJ - AN_OBJ
        relerr = abs(absdiff) / (abs(FD_OBJ) + 1e-300)
        sign = "agree" if (FD_OBJ * AN_OBJ) > 0 else "FLIPPED"
        print(
            "FIXEDDFDW_RESULT func=OBJ(TP1-TP2,real-seed) seed=%d h=%.1e FD=%.8e AN=%.8e rel_err=%.6e sign=%s"
            % (seedNum, h, FD_OBJ, AN_OBJ, relerr, sign),
            flush=True,
        )

print("FIXEDDFDW_DONE t=%.1fs" % (time.time() - t0), flush=True)
