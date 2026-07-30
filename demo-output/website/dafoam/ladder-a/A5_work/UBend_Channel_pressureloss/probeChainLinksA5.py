#!/usr/bin/env python
"""
A5 root-cause hunt, coordinator-directed follow-up to the 2026-07-29 finding
that mesh.warpDeriv (A1's root cause) is NOT A5's defect (A5's idx8/idx17 are
single-station DVs and agree with the warp finite difference to 0.32-1.30%,
no sign flip -- see A5_ubend_internal.md's addendum and PROOF.md's cross-rung
note). A5's real check_totals still fails badly (46.6% aggregate, 5/27 within
band, idx8/idx17 sign-flipped) with the SAME immunities A1's warpDeriv defect
had (step-size sweep ruled out "just needs a bigger step"; tightening the
primal made it WORSE, 2 sign flips -> 3). So A5 is a genuine second, distinct
defect and nothing is known yet about which link of the chain carries it.

Chain links downstream of mesh.warpDeriv (already cleared):
  dXv/dXs  (mesh warp's own derivative)        -- CLEARED, this is warpDeriv
  dF/dW    (objective's dependence on state)   -- TESTED HERE
  dR/dXv   (residual's dependence on mesh)     -- TESTED HERE
  dR/dW    (residual's dependence on state)    -- TESTED HERE

Method: the same adjoint/dot-product identity used throughout this
investigation for warpDeriv, applied to each link directly, WITHOUT solving
the flow or the adjoint -- pure post-processing evaluations at a fixed
baseline (one real converged primal solve, needed once to get a physically
meaningful state to linearize about):

  dF/dW:   <seed, F(W0+h*dW) - F(W0-h*dW)> / (2h)   ==   <calcJacTVecProduct(W0; F; seed), dW>
  dR/dW:   <seed, R(W0+h*dW) - R(W0-h*dW)> / (2h)   ==   <calcJacTVecProduct(W0; R; seed), dW>
  dR/dXv:  <seed, R(Xv0+h*dXv,W0) - R(Xv0-h*dXv,W0)> / (2h)  ==  <calcJacTVecProduct(Xv0; R; seed), dXv>

F(.) is evaluated via DASolver.evalFunctions() (a pure patch-integral
post-processing call, no solve). R(.) is evaluated via DASolver.getResiduals()
(DASolver.solver.getResiduals(), a pure residual-assembly call at the CURRENT
OF field, no iteration -- confirmed by reading pyDAFoam.py: it is a single
call to self.solver.getResiduals(residuals), the same non-AD "solver" object
used for checkMesh/primal bookkeeping, not solvePrimal). Both let us hold one
side of a two-argument function fixed (W fixed while perturbing Xv, and vice
versa) exactly as check_totals never can (it always perturbs the DESIGN
VARIABLE and lets everything downstream re-equilibrate through a full re-solve)
-- this isolates ONE partial derivative at a time, cleanly, the same principle
that let warpDeriv be cleared/confirmed for A1.

dW is a RELATIVE-magnitude random direction (dW_i = W0_i * r_i, r_i ~
Uniform(-1,1)) rather than a flat random vector, because A5's state vector
mixes physically very different scales in one array (U~8.4, p~35, nuTilda~
1e-3, T~300) -- a flat random perturbation at a single step h would be a huge
relative perturbation on the small-magnitude channels (nuTilda) and a
negligible one on the large channels (T), contaminating the FD estimate with
spurious nonlinearity on whichever channel happens to be small. Scaling by
each state's own value makes the step h a genuine RELATIVE step on every
channel simultaneously. dXv uses a flat random direction (mesh coordinates in
this case are all O(0.01-1) m, no cross-scale problem), matching every prior
warpDeriv script in this investigation.

--cpus=4 --memory=6g (this session's budget). No idx-specific test here --
these are properties of the solver's own AD Jacobians, not of a specific shape
DV, so a couple of random-seed directions is the right granularity (same
genre as the section 15 warpDeriv test before it was known which DV mattered).
"""
import os
import sys
import time
import numpy as np
from mpi4py import MPI
import openmdao.api as om
from mphys.multipoint import Multipoint
from dafoam.mphys import DAFoamBuilder
from mphys.scenario_aerodynamic import ScenarioAerodynamic
from pygeo.mphys import OM_DVGEOCOMP
from pygeo import geo_utils

comm = MPI.COMM_WORLD
rank = comm.rank
nRanks = comm.size

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

meshOptions = {
    "gridFile": os.getcwd(),
    "fileType": "OpenFOAM",
    "symmetryPlanes": [],
}


class Top(Multipoint):
    def setup(self):
        dafoam_builder = DAFoamBuilder(daOptionsAero, meshOptions, scenario="aerodynamic")
        dafoam_builder.initialize(self.comm)
        self.dafoam_builder = dafoam_builder
        self.add_subsystem("dvs", om.IndepVarComp(), promotes=["*"])
        self.add_subsystem("mesh_aero", dafoam_builder.get_mesh_coordinate_subsystem())
        self.add_subsystem("geometry_aero", OM_DVGEOCOMP(file="FFD/UBendDuctFFDSym.xyz", type="ffd"))
        self.mphys_add_scenario("scenario", ScenarioAerodynamic(aero_builder=dafoam_builder))
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
        shapexUpper = self.geometry_aero.nom_addLocalDV(dvName="shapexUpper", pointSelect=PS, axis="x")

        self.dvs.add_output("shapexUpper", val=np.array([0.0] * shapexUpper))
        self.connect("shapexUpper", "geometry_aero.shapexUpper")
        self.add_design_var("shapexUpper", lower=-0.04, upper=0.04, scaler=25.0)

        self.connect("scenario.aero_post.TP1", "OBJ.TP1")
        self.connect("scenario.aero_post.TP2", "OBJ.TP2")
        self.add_objective("OBJ.val", scaler=1.0)


t0 = time.time()
prob = om.Problem(reports=None)
prob.model = Top()
prob.setup(mode="rev")

if rank == 0:
    print("CHAINLINKS === running real primal (run_model) to get a converged baseline W0, Xv0 ===", flush=True)
prob.run_model()
if rank == 0:
    print("CHAINLINKS === primal done, t=%.1fs ===" % (time.time() - t0), flush=True)
    print("CHAINLINKS baseline OBJ.val=%.10f TP1=%.10f TP2=%.10f" % (
        float(prob.get_val("OBJ.val")), float(prob.get_val("scenario.aero_post.TP1")),
        float(prob.get_val("scenario.aero_post.TP2"))), flush=True)

DASolver = prob.model.dafoam_builder.DASolver
discipline = DASolver.getOption("discipline")
stateName = "%s_states" % discipline
residualName = "%s_residuals" % discipline
if rank == 0:
    print("CHAINLINKS discipline=%s stateName=%s residualName=%s" % (discipline, stateName, residualName), flush=True)

W0 = DASolver.getStates().copy()
Xv0 = DASolver.mesh.getSolverGrid().copy()
nW = W0.size
nXv = Xv0.size
nWglobal = comm.allreduce(nW, op=MPI.SUM)
nXvGlobal = comm.allreduce(nXv, op=MPI.SUM)
if rank == 0:
    print("CHAINLINKS nWglobal=%d nXvGlobal=%d" % (nWglobal, nXvGlobal), flush=True)

# make sure the OF fields are set to the converged baseline before any test
DASolver.setStates(W0)
DASolver.setVolCoords(Xv0)


def restore_baseline():
    DASolver.setStates(W0)
    DASolver.setVolCoords(Xv0)


def evalF(funcName):
    funcs = {}
    DASolver.evalFunctions(funcs)
    return float(funcs[funcName])


def relerr_sign(FD, AN):
    absdiff = FD - AN
    rel = abs(absdiff) / (abs(FD) + 1e-300)
    sign = "agree" if (FD * AN) > 0 else "FLIPPED"
    return absdiff, rel, sign


results = []

# ---------------------------------------------------------------------------
# LINK 1: dF/dW -- objective's (TP1, TP2, and the real combined TP1-TP2 seed)
# dependence on the flow state.
# ---------------------------------------------------------------------------
for seedNum in [2026, 42]:
    np.random.seed(seedNum + rank * 100003)  # per-rank-reproducible, seed-labeled
    r = np.random.uniform(-1.0, 1.0, size=nW)
    dW = W0 * r  # relative-magnitude random direction

    for h in [1e-4, 1e-5]:
        restore_baseline()
        DASolver.setStates(W0 + h * dW)
        TP1_p = evalF("TP1")
        TP2_p = evalF("TP2")
        DASolver.setStates(W0 - h * dW)
        TP1_m = evalF("TP1")
        TP2_m = evalF("TP2")
        restore_baseline()

        FD_TP1_local = (TP1_p - TP1_m) / (2.0 * h)
        FD_TP2_local = (TP2_p - TP2_m) / (2.0 * h)
        # TP1/TP2 from evalFunctions are already GLOBAL scalars (patch integral,
        # reduced internally) -- identical on every rank. The FD "scalar" IS the
        # directional derivative already; to make this a fair per-rank dot-product
        # identity against calcJacTVecProduct (whose seed/product live in the
        # LOCAL state partition), we instead treat FD_TP1_local as already the
        # correct global scalar (same value on every rank) and do not allreduce it
        # (allreduce of an identical value across ranks would inflate it by nRanks).
        FD_TP1 = FD_TP1_local
        FD_TP2 = FD_TP2_local

        for funcName, FD_val in [("TP1", FD_TP1), ("TP2", FD_TP2)]:
            seed = np.array([1.0])
            product = np.zeros_like(W0)
            DASolver.solverAD.calcJacTVecProduct(stateName, "stateVar", W0, funcName, "function", seed, product)
            AN_local = float(np.dot(product, dW))
            AN_scalar = comm.allreduce(AN_local, op=MPI.SUM)
            absdiff, rel, sign = relerr_sign(FD_val, AN_scalar)
            if rank == 0:
                print("CHAINLINKS_RESULT link=dF/dW func=%s seed=%d h=%.1e FD=%.8e AN=%.8e rel_err=%.6e sign=%s" % (
                    funcName, seedNum, h, FD_val, AN_scalar, rel, sign), flush=True)
            results.append(("dF/dW", funcName, seedNum, h, FD_val, AN_scalar, rel, sign))

        # the REAL combined seed the actual OBJ.val=TP1-TP2 adjoint uses: sum the
        # two functions' contributions exactly as DAFoamFunctions.compute_jacvec_product
        # does when d_outputs has both TP1 (seed 1) and TP2 (seed -1) nonzero at once.
        FD_OBJ = FD_TP1 - FD_TP2
        product1 = np.zeros_like(W0)
        DASolver.solverAD.calcJacTVecProduct(stateName, "stateVar", W0, "TP1", "function", np.array([1.0]), product1)
        product2 = np.zeros_like(W0)
        DASolver.solverAD.calcJacTVecProduct(stateName, "stateVar", W0, "TP2", "function", np.array([-1.0]), product2)
        productOBJ = product1 + product2
        AN_OBJ_local = float(np.dot(productOBJ, dW))
        AN_OBJ = comm.allreduce(AN_OBJ_local, op=MPI.SUM)
        absdiff, rel, sign = relerr_sign(FD_OBJ, AN_OBJ)
        if rank == 0:
            print("CHAINLINKS_RESULT link=dF/dW func=OBJ(TP1-TP2,real-seed) seed=%d h=%.1e FD=%.8e AN=%.8e rel_err=%.6e sign=%s" % (
                seedNum, h, FD_OBJ, AN_OBJ, rel, sign), flush=True)
        results.append(("dF/dW", "OBJ", seedNum, h, FD_OBJ, AN_OBJ, rel, sign))

restore_baseline()

# ---------------------------------------------------------------------------
# LINK 2: dR/dW -- residual's dependence on the state (the core adjoint matrix)
# ---------------------------------------------------------------------------
for seedNum in [2026, 42]:
    np.random.seed(seedNum + rank * 100003)
    r = np.random.uniform(-1.0, 1.0, size=nW)
    dW = W0 * r

    np.random.seed(seedNum + 7 + rank * 100003)
    w_R = np.random.uniform(-1.0, 1.0, size=nW)  # arbitrary seed in residual space

    for h in [1e-4, 1e-5]:
        restore_baseline()
        DASolver.setStates(W0 + h * dW)
        R_p = DASolver.getResiduals().copy()
        DASolver.setStates(W0 - h * dW)
        R_m = DASolver.getResiduals().copy()
        restore_baseline()

        FD_dR = (R_p - R_m) / (2.0 * h)
        FD_scalar_local = float(np.dot(w_R, FD_dR))
        FD_scalar = comm.allreduce(FD_scalar_local, op=MPI.SUM)

        product = np.zeros_like(W0)
        DASolver.solverAD.calcJacTVecProduct(stateName, "stateVar", W0, residualName, "residual", w_R, product)
        AN_local = float(np.dot(product, dW))
        AN_scalar = comm.allreduce(AN_local, op=MPI.SUM)

        absdiff, rel, sign = relerr_sign(FD_scalar, AN_scalar)
        if rank == 0:
            print("CHAINLINKS_RESULT link=dR/dW seed=%d h=%.1e FD=%.8e AN=%.8e rel_err=%.6e sign=%s" % (
                seedNum, h, FD_scalar, AN_scalar, rel, sign), flush=True)
        results.append(("dR/dW", "-", seedNum, h, FD_scalar, AN_scalar, rel, sign))

restore_baseline()

# ---------------------------------------------------------------------------
# LINK 3: dR/dXv -- residual's dependence on mesh coordinates (state held fixed)
# ---------------------------------------------------------------------------
for seedNum in [2026, 42]:
    np.random.seed(seedNum + 13 + rank * 100003)
    dXv = np.random.uniform(-1.0, 1.0, size=nXv)  # flat random -- Xv has no cross-scale problem

    np.random.seed(seedNum + 19 + rank * 100003)
    w_R = np.random.uniform(-1.0, 1.0, size=nW)

    for h in [1e-4, 1e-5]:
        restore_baseline()
        DASolver.setStates(W0)
        DASolver.setVolCoords(Xv0 + h * dXv)
        R_p = DASolver.getResiduals().copy()
        DASolver.setVolCoords(Xv0 - h * dXv)
        R_m = DASolver.getResiduals().copy()
        restore_baseline()

        FD_dR = (R_p - R_m) / (2.0 * h)
        FD_scalar_local = float(np.dot(w_R, FD_dR))
        FD_scalar = comm.allreduce(FD_scalar_local, op=MPI.SUM)

        product = np.zeros_like(Xv0)
        DASolver.solverAD.calcJacTVecProduct("aero_vol_coords", "volCoord", Xv0, residualName, "residual", w_R, product)
        AN_local = float(np.dot(product, dXv))
        AN_scalar = comm.allreduce(AN_local, op=MPI.SUM)

        absdiff, rel, sign = relerr_sign(FD_scalar, AN_scalar)
        if rank == 0:
            print("CHAINLINKS_RESULT link=dR/dXv seed=%d h=%.1e FD=%.8e AN=%.8e rel_err=%.6e sign=%s" % (
                seedNum, h, FD_scalar, AN_scalar, rel, sign), flush=True)
        results.append(("dR/dXv", "-", seedNum, h, FD_scalar, AN_scalar, rel, sign))

restore_baseline()

if rank == 0:
    print("CHAINLINKS_DONE nRanks=%d t=%.1fs nResults=%d" % (nRanks, time.time() - t0, len(results)), flush=True)
