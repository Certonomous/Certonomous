#!/usr/bin/env python
"""
Follow-up to probeA5MatvecDrDW.py: the corrected matvec did NOT cleanly agree
(150-1252% relative error, 2 of 3 seeds sign-flipped), unlike the clean
diagonal result. Two explanations are live: (a) a genuine off-diagonal
coupling defect, or (b) the row-only correction (AN_row = D_row * J_true_row,
verified only AT the diagonal) does not actually hold for OFF-diagonal
entries -- e.g. if the true convention also depends on the COLUMN's own
variable type, dividing by D_row alone would leave a residual scaling error
that looks like "disagreement" but isn't a coupling defect at all.

This tests that distinction directly and cheaply: pick ONE residual row
(idx=2490, a "U" row, D_row=8.4, confirmed diagonal-clean), get its FULL
analytic row via ONE calcJacTVecProduct(seed=e_2490) call, corrected by
dividing by 8.4. Then FD-check a handful of OFF-diagonal entries of that same
row DIRECTLY and individually (perturb ONE other state index j at a time,
read residual 2490 back) -- no aggregation, no ambiguity about which
component contributed what. Picks the largest-magnitude off-diagonal entries
in the corrected row first (so the test isn't swamped by near-zero noise).
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
print("OFFDIAG === primal done t=%.1fs ===" % (time.time() - t0), flush=True)

DASolver = prob.model.dafoam_builder.DASolver
stateName = "%s_states" % DASolver.getOption("discipline")
residualName = "%s_residuals" % DASolver.getOption("discipline")
W0 = DASolver.getStates().copy()
nW = W0.size
DASolver.setStates(W0)

ROW = 2490
D_ROW = 8.4
seed = np.zeros(nW)
seed[ROW] = 1.0
fullRow = np.zeros(nW)
DASolver.solverAD.calcJacTVecProduct(stateName, "stateVar", W0, residualName, "residual", seed, fullRow)
correctedRow = fullRow / D_ROW

# pick the largest-magnitude OFF-diagonal entries (excluding ROW itself)
absRow = np.abs(correctedRow).copy()
absRow[ROW] = 0.0
topJ = np.argsort(absRow)[::-1][:6]
print("OFFDIAG row=%d D_row=%.3f correctedRow[ROW]=%.6e top off-diag |value|: %s" % (
    ROW, D_ROW, correctedRow[ROW], np.array2string(correctedRow[topJ], precision=6)), flush=True)

for j in topJ:
    j = int(j)
    hj = 1e-4 * max(abs(W0[j]), 1e-8)
    Wp = W0.copy()
    Wp[j] += hj
    DASolver.setStates(Wp)
    Rp = float(DASolver.getResiduals()[ROW])
    Wm = W0.copy()
    Wm[j] -= hj
    DASolver.setStates(Wm)
    Rm = float(DASolver.getResiduals()[ROW])
    DASolver.setStates(W0)
    FD_j = (Rp - Rm) / (2.0 * hj)
    AN_j = float(correctedRow[j])
    absdiff = FD_j - AN_j
    relerr = abs(absdiff) / (abs(FD_j) + 1e-300)
    sign = "agree" if (FD_j * AN_j) > 0 else "FLIPPED"
    print("OFFDIAG_RESULT row=%d col=%d W0_j=%.6e FD=%.8e AN(corrected)=%.8e rel_err=%.6e sign=%s" % (
        ROW, j, W0[j], FD_j, AN_j, relerr, sign), flush=True)

print("OFFDIAG_DONE t=%.1fs" % (time.time() - t0), flush=True)
