#!/usr/bin/env python
"""
Coordinator-directed discriminating test for the dR/dW 285-337x gap found in
probeChainLinksA5.py. That gap dwarfs everything else measured in this entire
investigation (A1's worst ~150%, A5's own real check tops out at 208%) -- a
factor of ~300 is not a subtle linearization error, it is the signature of
comparing two quantities that differ by a SCALING. Two candidate explanations
that would make it a probe artifact, not a defect:
  (a) a single global units/normalization constant  -> ratio ~CONSTANT everywhere
  (b) per-cell volume weighting present in one code path, not the other
      -> ratio VARIES per component, correlating with local cell volume
A third possibility is that it is a genuine, patternless defect (285x is real).

This script tests DIAGONAL entries of dR/dW one at a time, which is the only
way to get two INDEPENDENTLY, DIRECTLY comparable scalars per component without
forward-mode AD (DAFoam does not support it -- confirmed, "we do not support
forward mode AD" in every compute_jacvec_product in mphys_dafoam.py):

  FD_i = (R(W0 + h*e_i)[i] - R(W0 - h*e_i)[i]) / (2h)       -- forward FD of
         the SAME diagonal entry, perturb state i, read residual i back
  AN_i = calcJacTVecProduct(stateName, W0, residualName, seed=e_i)[i]
         -- since product = J^T e_i, product[i] = (J^T)[i,i] = J[i,i],
         the SAME diagonal entry via reverse AD

Both are direct, real evaluations at the converged baseline -- FD_i via
DASolver.getResiduals() (a pure residual-assembly call, no solve), AN_i via
the same DASolver.solverAD.calcJacTVecProduct() the real adjoint chain calls
(DAFoamSolver.apply_linear, mphys_dafoam.py). No aggregation, no dot product
with an arbitrary direction -- ratio_i = AN_i / FD_i is a genuine per-component
number, comparable across components.

Run in SERIAL (nRanks=1) deliberately: this sidesteps every parallel
processor-boundary question entirely (no perturbation of duplicated points,
no partition ambiguity) -- the 4800-cell mesh is small enough that this is
still fast, and removing parallelism removes a whole axis of possible probe
error while this specific question is being isolated.

Deliberately does NOT attempt to decode which physical cell/variable each
global state index corresponds to (adjStateOrdering="cell" packs a
PER-CELL block of [U(3), volScalarStates, modelStates, phi(variable count per
cell, based on how many faces that cell owns)] -- the phi count is NOT
constant per cell, so index arithmetic to recover "which cell" would need the
exact same C++ offset table this test is trying to independently check, and
getting that decoding wrong would silently invalidate the result). Instead
this reports the DISTRIBUTION of ratio_i across a random sample of diagonal
indices spanning the whole state vector -- sufficient to discriminate
"constant" (global scaling) from "not constant" (volume weighting or a real
defect) without needing that decoding at all, per the coordinator's own
decision tree.
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
assert comm.size == 1, "this probe is deliberately serial -- run with plain `python`, no mpirun"

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
print("DIAGRATIO === running real primal (serial) ===", flush=True)
prob.run_model()
print("DIAGRATIO === primal done, t=%.1fs ===" % (time.time() - t0), flush=True)

DASolver = prob.model.dafoam_builder.DASolver
discipline = DASolver.getOption("discipline")
stateName = "%s_states" % discipline
residualName = "%s_residuals" % discipline

W0 = DASolver.getStates().copy()
nW = W0.size
print("DIAGRATIO nW=%d discipline=%s" % (nW, discipline), flush=True)

DASolver.setStates(W0)

np.random.seed(2026)
nSample = 60
idxs = np.sort(np.random.choice(nW, size=nSample, replace=False))

rows = []
for i in idxs:
    hi = 1e-4 * max(abs(W0[i]), 1e-8)

    Wp = W0.copy()
    Wp[i] += hi
    DASolver.setStates(Wp)
    Rp_i = float(DASolver.getResiduals()[i])

    Wm = W0.copy()
    Wm[i] -= hi
    DASolver.setStates(Wm)
    Rm_i = float(DASolver.getResiduals()[i])

    DASolver.setStates(W0)

    FD_i = (Rp_i - Rm_i) / (2.0 * hi)

    seed = np.zeros(nW)
    seed[i] = 1.0
    product = np.zeros(nW)
    DASolver.solverAD.calcJacTVecProduct(stateName, "stateVar", W0, residualName, "residual", seed, product)
    AN_i = float(product[i])

    if abs(FD_i) > 1e-300:
        ratio = AN_i / FD_i
    else:
        ratio = float("nan")

    rows.append((int(i), float(W0[i]), hi, FD_i, AN_i, ratio))
    print("DIAGRATIO_ROW idx=%d W0_i=%.6e h_i=%.3e FD_i=%.8e AN_i=%.8e ratio=%.6f" % (
        int(i), float(W0[i]), hi, FD_i, AN_i, ratio), flush=True)

ratios = np.array([r[5] for r in rows])
validRatios = ratios[np.isfinite(ratios)]
print("DIAGRATIO_SUMMARY n=%d nValid=%d mean=%.4f median=%.4f std=%.4f min=%.4f max=%.4f cv=%.4f" % (
    len(ratios), len(validRatios),
    float(np.mean(validRatios)), float(np.median(validRatios)), float(np.std(validRatios)),
    float(np.min(validRatios)), float(np.max(validRatios)),
    float(np.std(validRatios) / (abs(np.mean(validRatios)) + 1e-300)),
), flush=True)
print("DIAGRATIO_DONE t=%.1fs" % (time.time() - t0), flush=True)
