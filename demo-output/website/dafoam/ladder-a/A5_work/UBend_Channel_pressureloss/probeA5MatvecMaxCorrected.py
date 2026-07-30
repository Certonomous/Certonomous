#!/usr/bin/env python
"""
Re-run the dR/dW matvec test under the MAX-of-the-two correction, confirmed
in probeA5TwoSidedFormula.py: corrected_entry = raw_AN[row,col] /
max(D_row, D_col), verified EXACT (1.000000, or 0.999935/0.999995 within FD
step noise) across 13 independently-measured (row,col) pairs spanning every
combination of U/p/nuTilda/T, versus the ratio formula's wild 0.001-70559x
scatter on the SAME pairs.

max(D_row, D_col) is NOT separable into a row-function times a column-
function (unlike a ratio or product), so it cannot be cancelled by simply
pre-scaling the seed vector w_R (row-space) the way the row-only correction
did for the diagonal. It CAN be cancelled exactly, in closed form, if BOTH
w_R and dW are restricted to be TYPE-HOMOGENEOUS (every nonzero component of
w_R is the same variable type, and likewise for dW) -- then max(D_row,D_col)
is the SAME CONSTANT for every (row,col) pair contributing to the sum, and
dividing the whole scalar by that one constant is exact, not approximate.

This sacrifices "one fully dense direction hits everything at once" for
"one direction per TYPE-PAIR, each still hitting MANY (row,col) entries
simultaneously (all cross terms between every known index of type A and
every known index of type B)" -- the necessary consequence of max() being
non-separable, not a weaker test in the entries-per-run sense.

Runs every type-pair combination available from the 43 diagonal-confirmed
indices (U, p, nuTilda, T -- 10 unordered pairs including self-pairs), 2
random sign/direction draws each.
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
print("MAXCORR === primal done t=%.1fs ===" % (time.time() - t0), flush=True)

DASolver = prob.model.dafoam_builder.DASolver
stateName = "%s_states" % DASolver.getOption("discipline")
residualName = "%s_residuals" % DASolver.getOption("discipline")
W0 = DASolver.getStates().copy()
nW = W0.size
DASolver.setStates(W0)

KNOWN_D = {
    560: 300.0, 1373: 35.28, 2490: 8.4, 3674: 0.001, 4045: 8.4, 4870: 0.001,
    5529: 35.28, 5818: 0.001, 9601: 8.4, 10568: 35.28, 10610: 8.4, 12651: 0.001,
    17020: 8.4, 17088: 8.4, 17492: 8.4, 17648: 8.4, 18441: 8.4, 19223: 8.4,
    19880: 35.28, 20436: 35.28, 20739: 0.001, 21543: 8.4, 23607: 8.4,
    23934: 8.4, 27697: 35.28, 28522: 8.4, 30600: 35.28, 30843: 8.4,
    32502: 8.4, 32659: 35.28, 34587: 8.4, 35193: 35.28, 36749: 300.0,
    37396: 8.4, 38303: 8.4, 39976: 8.4, 41018: 0.001, 41199: 0.001,
    41408: 300.0, 41590: 300.0, 42274: 8.4, 43974: 8.4, 44215: 8.4,
}
byType = {}
for idx, d in KNOWN_D.items():
    byType.setdefault(d, []).append(idx)
typeNames = {8.4: "U", 35.28: "p", 0.001: "nuTilda", 300.0: "T"}
types = sorted(byType.keys())

results = []
for ai in range(len(types)):
    for bi in range(ai, len(types)):
        typeA, typeB = types[ai], types[bi]
        rowsA = byType[typeA]
        colsB = byType[typeB]
        maxD = max(typeA, typeB)
        for seedNum in [2026, 42]:
            np.random.seed(seedNum + ai * 17 + bi * 31)
            w_R = np.zeros(nW)
            signs_row = np.random.choice([-1.0, 1.0], size=len(rowsA))
            for k, r in enumerate(rowsA):
                w_R[r] = signs_row[k]

            dW = np.zeros(nW)
            signs_col = np.random.choice([-1.0, 1.0], size=len(colsB))
            for k, c in enumerate(colsB):
                dW[c] = signs_col[k] * abs(W0[c])  # relative-magnitude, like other tests

            h = 1e-4
            Wp = W0 + h * dW
            Wm = W0 - h * dW
            DASolver.setStates(Wp)
            Rp = DASolver.getResiduals().copy()
            DASolver.setStates(Wm)
            Rm = DASolver.getResiduals().copy()
            DASolver.setStates(W0)
            FD_dR = (Rp - Rm) / (2.0 * h)
            FD_scalar = float(np.dot(w_R, FD_dR))

            product = np.zeros(nW)
            DASolver.solverAD.calcJacTVecProduct(stateName, "stateVar", W0, residualName, "residual", w_R, product)
            AN_scalar_raw = float(np.dot(dW, product))
            AN_scalar_corrected = AN_scalar_raw / maxD

            absdiff = FD_scalar - AN_scalar_corrected
            relerr = abs(absdiff) / (abs(FD_scalar) + 1e-300)
            sign = "agree" if (FD_scalar * AN_scalar_corrected) > 0 else "FLIPPED"
            print(
                "MAXCORR_RESULT typePair=%s-%s(maxD=%.3f) seed=%d nRows=%d nCols=%d "
                "FD=%.8e AN_corrected=%.8e rel_err=%.6e sign=%s"
                % (typeNames[typeA], typeNames[typeB], maxD, seedNum, len(rowsA), len(colsB),
                   FD_scalar, AN_scalar_corrected, relerr, sign),
                flush=True,
            )
            results.append((typeNames[typeA], typeNames[typeB], relerr, sign))

nAgree = sum(1 for r in results if r[3] == "agree")
print("MAXCORR_SUMMARY n=%d nAgreeSign=%d meanRelErr=%.6f medianRelErr=%.6f" % (
    len(results), nAgree, float(np.mean([r[2] for r in results])), float(np.median([r[2] for r in results]))), flush=True)
print("MAXCORR_DONE t=%.1fs" % (time.time() - t0), flush=True)
